#!/usr/bin/env python3
"""Export canonical DuckDB tables to Parquet and the spatial source to GeoParquet.

This script is additive: it reads the canonical database and the existing
spatial source, and writes only the new ``data/parquet`` derivative tree.
Neither the database nor any source/result file is modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb
import geopandas as gpd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "aussef.duckdb"
DEFAULT_OUTPUT = ROOT / "data" / "parquet"
SPATIAL_SOURCE = (
    ROOT
    / "Experiment 2"
    / "data"
    / "disaster_exposure_v2"
    / "continuing_councils_2023.geojson"
)


def _identifier(value: str) -> str:
    """Quote an identifier after it has been read from DuckDB metadata."""

    return '"' + value.replace('"', '""') + '"'


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _base_tables(con: duckdb.DuckDBPyConnection, schema: str) -> list[str]:
    rows = con.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = ? AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
        [schema],
    ).fetchall()
    return [row[0] for row in rows]


def _export_table(
    con: duckdb.DuckDBPyConnection,
    schema: str,
    table: str,
    output_root: Path,
) -> dict[str, Any]:
    destination = output_root / schema / f"{table}.parquet"
    destination.parent.mkdir(parents=True, exist_ok=True)
    qualified = f"{_identifier(schema)}.{_identifier(table)}"
    destination_sql = _literal(destination.as_posix())

    con.execute(
        f"COPY {qualified} TO {destination_sql} "
        "(FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    row_count = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
    parquet_rows = pq.ParquetFile(destination).metadata.num_rows
    if parquet_rows != row_count:
        raise RuntimeError(
            f"row-count mismatch for {schema}.{table}: "
            f"DuckDB={row_count}, Parquet={parquet_rows}"
        )

    return {
        "kind": "table",
        "schema": schema,
        "table": table,
        "path": destination.relative_to(ROOT).as_posix(),
        "format": "parquet",
        "rows": row_count,
        "sha256": _sha256(destination),
    }


def _export_geoparquet(source: Path, output_root: Path) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(f"spatial source not found: {source}")

    source_key = f"input_{_sha256(source)}"
    frame = gpd.read_file(source)
    if frame.crs is None:
        raise ValueError("spatial source has no CRS; refusing to create an ambiguous GeoParquet")
    if frame.geometry.name not in frame.columns:
        raise ValueError("spatial source has no active geometry column")
    if frame.geometry.isna().any():
        raise ValueError("spatial source contains null geometries")
    if not frame.geometry.is_valid.all():
        raise ValueError("spatial source contains invalid geometries")

    frame = frame.copy()
    frame["source_key"] = source_key
    frame["source_record_key"] = [
        f"{source_key}:feature:{position:04d}"
        for position in range(len(frame))
    ]
    frame["source_dataset"] = "continuing_councils_2023"

    destination = output_root / "geo" / "continuing_councils_2023.parquet"
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(destination, index=False, compression="zstd")

    metadata = pq.ParquetFile(destination).metadata
    return {
        "kind": "spatial_source",
        "source_path": source.relative_to(ROOT).as_posix(),
        "source_sha256": _sha256(source),
        "path": destination.relative_to(ROOT).as_posix(),
        "format": "geoparquet",
        "rows": metadata.num_rows,
        "sha256": _sha256(destination),
        "crs": frame.crs.to_string(),
        "geometry_column": frame.geometry.name,
        "columns": [str(column) for column in frame.columns],
    }


def export(db_path: Path, output_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        files: list[dict[str, Any]] = []
        for schema in ("master", "provenance"):
            for table in _base_tables(con, schema):
                files.append(_export_table(con, schema, table, output_root))
    finally:
        con.close()

    files.append(_export_geoparquet(SPATIAL_SOURCE, output_root))
    files.sort(key=lambda item: item["path"])

    manifest = {
        "manifest_version": 1,
        "database": DEFAULT_DB.relative_to(ROOT).as_posix()
        if db_path == DEFAULT_DB
        else db_path.relative_to(ROOT).as_posix(),
        "policy": {
            "tables": "all canonical master and provenance base tables",
            "views": "not exported; experiment views remain derived in DuckDB",
            "spatial": "existing cleaned GeoJSON copied to GeoParquet without reprojection",
            "source_data": "read-only; no source or result file is modified",
        },
        "files": files,
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    db_path = args.database.resolve()
    output_root = args.output.resolve()
    manifest = export(db_path, output_root)
    print(
        f"Exported {len(manifest['files'])} Parquet/GeoParquet files "
        f"to {output_root.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
