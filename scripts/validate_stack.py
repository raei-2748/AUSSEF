#!/usr/bin/env python3
"""Validate the integrated AUSSEF research stack and canonical derivatives."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import duckdb
import geopandas as gpd
import pandas as pd
import pandera
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from schemas.canonical import TABLE_SCHEMAS  # noqa: E402


DB_PATH = ROOT / "data" / "aussef.duckdb"
PARQUET_ROOT = ROOT / "data" / "parquet"
MANIFEST_PATH = PARQUET_ROOT / "manifest.json"
REPORT_PATH = ROOT / "data" / "checks" / "stack_validation.json"
SPATIAL_SOURCE = (
    ROOT
    / "Experiment 2"
    / "data"
    / "disaster_exposure_v2"
    / "continuing_councils_2023.geojson"
)


def _run_version(command: str, args: list[str]) -> str:
    candidates = [ROOT / ".venv" / "bin" / command]
    located = shutil.which(command)
    if located:
        candidates.append(Path(located))
    for candidate in candidates:
        if candidate.exists():
            completed = subprocess.run(
                [str(candidate), *args],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            return (completed.stdout or completed.stderr).strip().splitlines()[0]
    raise FileNotFoundError(command)


def _tables(con: duckdb.DuckDBPyConnection, schema: str, table_type: str) -> list[str]:
    return [
        row[0]
        for row in con.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = ? AND table_type = ?
            ORDER BY table_name
            """,
            [schema, table_type],
        ).fetchall()
    ]


def _count(con: duckdb.DuckDBPyConnection, schema: str, table: str) -> int:
    return int(
        con.execute(
            f'SELECT COUNT(*) FROM "{schema}"."{table}"'
        ).fetchone()[0]
    )


def _check_views(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    expected = {
        "experiment_1_fiscal_forecast",
        "experiment_2_disaster_exposure",
        "experiment_3_project_evidence",
        "experiment_4_budget_revisions",
        "experiment_4_council_year_screen",
        "experiment_4_evidence_register",
    }
    actual = set(_tables(con, "experiments", "VIEW"))
    if actual != expected:
        raise AssertionError(f"experiment objects differ: expected {expected}, got {actual}")
    if _tables(con, "experiments", "BASE TABLE"):
        raise AssertionError("experiments schema contains a base table")
    return {"views": sorted(actual)}


def _check_referential_integrity(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    checks = {
        "projects_to_councils": """
            SELECT COUNT(*) FROM master.projects p
            LEFT JOIN master.councils c USING (council_id)
            WHERE p.council_id IS NOT NULL AND c.council_id IS NULL
        """,
        "exposure_to_councils": """
            SELECT COUNT(*) FROM master.exposure_observations e
            LEFT JOIN master.councils c USING (council_id)
            WHERE e.council_id IS NOT NULL AND c.council_id IS NULL
        """,
        "fiscal_to_councils": """
            SELECT COUNT(*) FROM master.fiscal_annual f
            LEFT JOIN master.councils c USING (council_id)
            WHERE f.council_id IS NOT NULL AND c.council_id IS NULL
        """,
        "evidence_to_councils": """
            SELECT COUNT(*) FROM master.evidence_records e
            LEFT JOIN master.councils c USING (council_id)
            WHERE e.council_id IS NOT NULL AND c.council_id IS NULL
        """,
        "evidence_to_projects": """
            SELECT COUNT(*) FROM master.evidence_records e
            LEFT JOIN master.projects p USING (project_id)
            WHERE e.project_id IS NOT NULL AND p.project_id IS NULL
        """,
    }
    failures = {
        name: int(con.execute(sql).fetchone()[0]) for name, sql in checks.items()
    }
    if any(failures.values()):
        raise AssertionError(f"referential integrity failures: {failures}")
    return failures


def _check_spatial_extension() -> dict[str, Any]:
    con = duckdb.connect(":memory:")
    try:
        try:
            con.execute("LOAD spatial")
        except duckdb.Error:
            con.execute("INSTALL spatial")
            con.execute("LOAD spatial")
        spatial_row = con.execute(
            """
            SELECT extension_name, loaded
            FROM duckdb_extensions()
            WHERE extension_name = 'spatial'
            """
        ).fetchone()
        version = con.execute("PRAGMA version").fetchone()[0]
        valid_point = con.execute(
            "SELECT ST_IsValid(ST_GeomFromText('POINT (0 0)'))"
        ).fetchone()[0]
    finally:
        con.close()
    if not valid_point:
        raise AssertionError("DuckDB Spatial point validity probe failed")
    if spatial_row is None or not spatial_row[1]:
        raise AssertionError("DuckDB Spatial is not reported as loaded")
    return {
        "duckdb_version": str(version),
        "spatial_loaded": bool(spatial_row[1]),
        "point_probe": bool(valid_point),
    }


def _check_pandera(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    validated: dict[str, int] = {}
    for table_name, schema in TABLE_SCHEMAS.items():
        frame = con.execute(f'SELECT * FROM master."{table_name}"').df()
        schema.validate(frame, lazy=True)
        validated[table_name] = len(frame)
    return {"pandera_version": pandera.__version__, "tables": validated}


def _check_parquet(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(MANIFEST_PATH)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    if not files:
        raise AssertionError("Parquet manifest is empty")

    table_files = [item for item in files if item["kind"] == "table"]
    expected_tables = [
        (schema, table)
        for schema in ("master", "provenance")
        for table in _tables(con, schema, "BASE TABLE")
    ]
    actual_tables = [(item["schema"], item["table"]) for item in table_files]
    if sorted(actual_tables) != sorted(expected_tables):
        raise AssertionError("Parquet manifest does not cover exactly the canonical base tables")

    for item in table_files:
        path = ROOT / item["path"]
        if not path.exists():
            raise FileNotFoundError(path)
        parquet_rows = pq.ParquetFile(path).metadata.num_rows
        duckdb_rows = _count(con, item["schema"], item["table"])
        if parquet_rows != duckdb_rows or parquet_rows != item["rows"]:
            raise AssertionError(
                f"row-count mismatch for {item['schema']}.{item['table']}: "
                f"DuckDB={duckdb_rows}, Parquet={parquet_rows}, manifest={item['rows']}"
            )

    spatial_items = [item for item in files if item["kind"] == "spatial_source"]
    if len(spatial_items) != 1:
        raise AssertionError("manifest must contain exactly one spatial source export")
    spatial_item = spatial_items[0]
    spatial_path = ROOT / spatial_item["path"]
    frame = gpd.read_parquet(spatial_path)
    if frame.crs is None:
        raise AssertionError("GeoParquet has no CRS")
    if frame.geometry.isna().any() or not frame.geometry.is_valid.all():
        raise AssertionError("GeoParquet contains null or invalid geometry")
    if len(frame) != spatial_item["rows"]:
        raise AssertionError("GeoParquet row count does not match manifest")
    if len(frame) != len(gpd.read_file(SPATIAL_SOURCE)):
        raise AssertionError("GeoParquet row count does not match the source GeoJSON")

    return {
        "base_tables": len(table_files),
        "geo_rows": len(frame),
        "geo_crs": frame.crs.to_string(),
        "geo_geometry_column": frame.geometry.name,
    }


def _report_detail(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _report_detail(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_report_detail(item) for item in value]
    if isinstance(value, (pd.Timestamp, Path)):
        return str(value)
    return value


def validate(write_report: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def run(name: str, function: Callable[[], Any]) -> None:
        try:
            detail = function()
            checks.append({"name": name, "status": "pass", "detail": _report_detail(detail)})
        except Exception as error:  # noqa: BLE001 - preserve all check failures in the receipt
            message = f"{name}: {error}"
            errors.append(message)
            checks.append({"name": name, "status": "fail", "detail": str(error)})

    run("spatial_extension", _check_spatial_extension)
    run(
        "command_line_tools",
        lambda: {
            "duckdb": _run_version("duckdb", ["--version"]),
            "dvc": _run_version("dvc", ["--version"]),
            "quarto": _run_version("quarto", ["--version"]),
            "jupyter": _run_version("jupyter", ["--version"]),
            "dbeaver_app": Path("/Applications/DBeaver.app").exists(),
        },
    )

    if not DB_PATH.exists():
        errors.append(f"canonical database not found: {DB_PATH}")
    else:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        try:
            run("experiment_views", lambda: _check_views(con))
            run("referential_integrity", lambda: _check_referential_integrity(con))
            run("pandera_schemas", lambda: _check_pandera(con))
            run("parquet_derivatives", lambda: _check_parquet(con))
        finally:
            con.close()

    report = {
        "status": "pass" if not errors else "fail",
        "database": DB_PATH.relative_to(ROOT).as_posix(),
        "checks": checks,
        "errors": errors,
    }
    if write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if errors:
        raise SystemExit("\n".join(errors))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = validate(write_report=args.write_report)
    print(f"Stack validation passed ({len(report['checks'])} checks)")


if __name__ == "__main__":
    main()
