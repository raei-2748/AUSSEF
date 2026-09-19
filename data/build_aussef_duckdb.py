#!/usr/bin/env python3
"""Build the canonical AUSSEF DuckDB database.

The builder reads only cleaned, structured CSV inputs declared in ``INPUTS``.
It never edits or copies raw source files.  The database is rebuilt atomically
at ``data/aussef.duckdb`` and contains normalized master tables plus
experiment views.  Stable entity identifiers are deterministic hashes of the
exact source labels/identifiers that were observed; no fuzzy council,
disaster, or project merge is inferred here.

The standalone DuckDB CLI is used instead of the Python duckdb package so the
build can run in the current macOS workspace.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parent.parent
DEFAULT_DATABASE = SCRIPT_PATH.parent / "aussef.duckdb"
DEFAULT_CHECKS_DIR = SCRIPT_PATH.parent / "checks"


@dataclass(frozen=True)
class InputSpec:
    stage_name: str
    relative_path: str
    role: str
    description: str


# These are cleaned/structured inputs.  ``sources/`` and ``raw/`` paths are
# intentionally excluded.  The small legacy bundle contains cleaned tables
# that are not duplicated by the Experiment 4 tables.
INPUTS: tuple[InputSpec, ...] = (
    InputSpec("e4_councils", "Experiment 4/data/councils.csv", "dimension", "Experiment 4 council universe"),
    InputSpec("e4_sources", "Experiment 4/data/sources.csv", "provenance", "Experiment 4 document/source register"),
    InputSpec("e4_fiscal_annual", "Experiment 4/data/fiscal_annual.csv", "master", "cleaned council x financial-year fiscal panel"),
    InputSpec("e4_disasters", "Experiment 4/data/disasters.csv", "master", "Experiment 4 disaster identity register"),
    InputSpec("e4_disaster_observations", "Experiment 4/data/disaster_observations.csv", "master", "Experiment 4 event timing observations"),
    InputSpec("e4_projects", "Experiment 4/data/projects.csv", "master", "Experiment 4 project ledger"),
    InputSpec("e4_budgets", "Experiment 4/data/budget_snapshots.csv", "master", "project budget snapshots"),
    InputSpec("e4_project_evidence", "Experiment 4/data/project_evidence.csv", "master", "project-level funding/evidence observations"),
    InputSpec("e4_project_linkage", "Experiment 4/data/project_linkage_audit.csv", "audit", "project linkage audit"),
    InputSpec("e4_project_milestones", "Experiment 4/data/project_milestones.csv", "master", "project milestone observations"),
    InputSpec("e4_project_revisions", "Experiment 4/data/project_revisions.csv", "master", "project budget revision observations"),
    InputSpec("e4_damage_status", "Experiment 4/data/damage_status.csv", "master", "project damage/access status register"),
    InputSpec("e4_capacity", "Experiment 4/data/capacity_candidates.csv", "master", "council capacity candidate observations"),
    InputSpec("e4_fiscal_availability", "Experiment 4/data/fiscal_availability_evidence.csv", "audit", "fiscal availability evidence"),
    InputSpec("e4_fiscal_value_audit", "Experiment 4/data/fiscal_value_audit.csv", "audit", "fiscal value reconciliation"),
    InputSpec("e4_review_decisions", "Experiment 4/data/review_decisions.csv", "audit", "review decision register"),
    InputSpec("e4_field_gaps", "Experiment 4/data/field_gaps.csv", "audit", "field gap register"),
    InputSpec("e4_source_conflicts", "Experiment 4/data/source_conflicts.csv", "audit", "source conflict register"),
    InputSpec("e4_search_followup", "Experiment 4/data/search_followup.csv", "audit", "search follow-up register"),
    InputSpec("e4_evidence_master_expanded", "Experiment 4/data/evidence_master_expanded.csv", "master", "expanded evidence register"),
    InputSpec("e2_fiscal_panel", "Experiment 2/data/fiscal_panel_v2/NSW_Fiscal_Panel_V2_candidate.csv", "master", "Experiment 2 extended fiscal panel"),
    InputSpec("e2_exposure_panel", "Experiment 2/data/disaster_exposure_v2/NSW_Disaster_Exposure_V2_candidate.csv", "master", "Experiment 2 council-year disaster exposure panel"),
    InputSpec("e2_declaration_events", "Experiment 2/data/disaster_exposure_v2/declaration_event_ledger.csv", "master", "declaration event ledger"),
    InputSpec("e2_declaration_links", "Experiment 2/data/disaster_exposure_v2/declaration_council_links.csv", "master", "declaration council links"),
    InputSpec("e2_name_crosswalk", "Experiment 2/data/disaster_exposure_v2/declaration_name_crosswalk.csv", "crosswalk", "declaration council-name crosswalk"),
    InputSpec("e2_historical_fire", "Experiment 2/data/disaster_exposure_v2/historical_fire_zonal_statistics.csv", "master", "historical fire zonal statistics"),
    InputSpec("e2_fesm_reconciliation", "Experiment 2/data/disaster_exposure_v2/fesm_2016_workbook_reconciliation.csv", "audit", "FESM workbook/raster reconciliation"),
    InputSpec("e2_fiscal_crosswalk", "Experiment 2/data/fiscal_panel_v2/council_crosswalk.csv", "crosswalk", "fiscal source council crosswalk"),
    InputSpec("legacy_nsw_panel", "NSW Data Panel.csv", "legacy_master", "existing legacy fiscal panel; preserved without re-interpretation"),
    InputSpec("legacy_annual_fiscal", "aussef_duckdb/source_tables/annual_fiscal_data.csv", "legacy_master", "cleaned annual fiscal measurements"),
    InputSpec("legacy_disasters", "aussef_duckdb/source_tables/disasters.csv", "legacy_master", "cleaned disaster-event inventory"),
    InputSpec("legacy_disaster_links", "aussef_duckdb/source_tables/disaster_council_links.csv", "legacy_master", "cleaned disaster-council bridge"),
    InputSpec("legacy_projects", "aussef_duckdb/source_tables/projects.csv", "legacy_master", "cleaned legacy project/program ledger"),
    InputSpec("legacy_accounting", "aussef_duckdb/source_tables/annual_accounting_snapshots.csv", "legacy_master", "annual accounting snapshots"),
    InputSpec("legacy_financing", "aussef_duckdb/source_tables/financing_components.csv", "legacy_master", "financing component observations"),
    InputSpec("legacy_payment_timing", "aussef_duckdb/source_tables/payment_timing_evidence.csv", "legacy_master", "payment timing evidence"),
    InputSpec("legacy_treatment", "aussef_duckdb/source_tables/treatment_roster.csv", "legacy_master", "provisional treatment roster"),
)

MASTER_TABLES = (
    "councils",
    "council_aliases",
    "sources",
    "disasters",
    "disaster_sources",
    "disaster_declarations",
    "disaster_council_links",
    "disaster_observations",
    "fiscal_annual",
    "fiscal_panel_extended",
    "fiscal_panel_legacy",
    "legacy_fiscal_measurements",
    "exposure_observations",
    "fire_zonal_statistics",
    "fesm_reconciliation",
    "projects",
    "project_financials",
    "project_evidence",
    "project_linkage_audit",
    "project_milestones",
    "project_revisions",
    "damage_status",
    "capacity_observations",
    "evidence_records",
    "accounting_snapshots",
    "financing_observations",
    "payment_timing_evidence",
    "treatment_roster",
    "fiscal_availability_evidence",
    "fiscal_value_audit",
    "review_decisions",
    "field_gaps",
    "source_conflicts",
    "search_followups",
    "declaration_name_crosswalk",
    "fiscal_council_crosswalk",
)

VIEW_SPECS = (
    ("experiment_1_fiscal_forecast", "council-year fiscal panel with next-year outcome and exposure fields", "master.fiscal_annual + master.exposure_observations"),
    ("experiment_2_disaster_exposure", "council-year exposure panel with stable entity keys", "master.exposure_observations + master.disasters"),
    ("experiment_3_project_evidence", "project-level evidence and status panel", "master.projects + master.project_evidence + master.damage_status"),
    ("experiment_4_budget_revisions", "project financial snapshots with annual revision summaries", "master.project_financials + master.project_revisions"),
    ("experiment_4_evidence_register", "expanded evidence register with exact-only council/project resolution", "master.evidence_records + master.sources"),
    ("experiment_4_council_year_screen", "council-year fiscal/exposure screening view", "master.fiscal_annual + master.exposure_observations"),
)


def sql_string(value: object) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_profile(path: Path, root: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if not header:
            raise ValueError(f"CSV is empty: {path}")
        rows = sum(1 for _ in reader)
    if any(not column for column in header) or len(header) != len(set(header)):
        raise ValueError(f"CSV has empty or duplicate columns: {path}")
    return {
        "relative_path": str(path.relative_to(root)),
        "sha256": sha256_file(path),
        "rows": rows,
        "columns": header,
    }


def find_duckdb(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    found = shutil.which("duckdb")
    if found:
        candidates.append(Path(found))
    candidates.extend((Path.home() / ".duckdb" / "cli" / "latest" / "duckdb", Path("/Users/ray/.local/bin/duckdb")))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise FileNotFoundError("DuckDB CLI not found")


def run_duckdb(duckdb_bin: Path, database: Path, sql: str) -> str:
    result = subprocess.run(
        [str(duckdb_bin), str(database), "-c", sql],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"DuckDB build failed:\n{detail}")
    return result.stdout


def run_csv_query(duckdb_bin: Path, database: Path, sql: str) -> list[dict[str, str]]:
    result = subprocess.run(
        [str(duckdb_bin), "-csv", "-header", str(database), "-c", sql],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"DuckDB verification failed:\n{detail}")
    return list(csv.DictReader(result.stdout.splitlines()))


def values_sql(rows: Iterable[Iterable[object]]) -> str:
    return ",\n".join("(" + ", ".join(sql_string(value) for value in row) + ")" for row in rows)


def input_manifest_sql(profiles: dict[str, dict[str, object]]) -> str:
    rows = []
    for spec in INPUTS:
        profile = profiles[spec.stage_name]
        input_key = "input_" + str(profile["sha256"])
        rows.append(
            (
                input_key,
                spec.stage_name,
                profile["relative_path"],
                profile["sha256"],
                profile["rows"],
                len(profile["columns"]),
                spec.role,
                spec.description,
            )
        )
    return (
        "CREATE OR REPLACE TABLE provenance.input_files AS SELECT * FROM (VALUES\n"
        + values_sql(rows)
        + ") AS x(input_key, input_name, relative_path, sha256, row_count, column_count, role, description);"
    )


def input_key(profiles: dict[str, dict[str, object]], stage_name: str) -> str:
    return "input_" + str(profiles[stage_name]["sha256"])


def source_row_key_sql(key: str, alias: str = "s") -> str:
    return f"{sql_string(key)} || ':row:' || CAST({alias}.source_row_number AS VARCHAR)"


def build_sql(profiles: dict[str, dict[str, object]]) -> str:
    e4_councils = input_key(profiles, "e4_councils")
    e4_sources = input_key(profiles, "e4_sources")
    e4_fiscal = input_key(profiles, "e4_fiscal_annual")
    e4_disasters = input_key(profiles, "e4_disasters")
    e4_disaster_obs = input_key(profiles, "e4_disaster_observations")
    e4_projects = input_key(profiles, "e4_projects")
    e4_budgets = input_key(profiles, "e4_budgets")
    e4_project_evidence = input_key(profiles, "e4_project_evidence")
    e4_project_linkage = input_key(profiles, "e4_project_linkage")
    e4_project_milestones = input_key(profiles, "e4_project_milestones")
    e4_project_revisions = input_key(profiles, "e4_project_revisions")
    e4_damage = input_key(profiles, "e4_damage_status")
    e4_capacity = input_key(profiles, "e4_capacity")
    e4_fiscal_availability = input_key(profiles, "e4_fiscal_availability")
    e4_fiscal_value_audit = input_key(profiles, "e4_fiscal_value_audit")
    e4_review = input_key(profiles, "e4_review_decisions")
    e4_field_gaps = input_key(profiles, "e4_field_gaps")
    e4_conflicts = input_key(profiles, "e4_source_conflicts")
    e4_search = input_key(profiles, "e4_search_followup")
    e4_evidence = input_key(profiles, "e4_evidence_master_expanded")
    e2_fiscal = input_key(profiles, "e2_fiscal_panel")
    e2_exposure = input_key(profiles, "e2_exposure_panel")
    e2_events = input_key(profiles, "e2_declaration_events")
    e2_links = input_key(profiles, "e2_declaration_links")
    e2_crosswalk = input_key(profiles, "e2_name_crosswalk")
    e2_fire = input_key(profiles, "e2_historical_fire")
    e2_fesm = input_key(profiles, "e2_fesm_reconciliation")
    e2_fiscal_crosswalk = input_key(profiles, "e2_fiscal_crosswalk")
    legacy_panel = input_key(profiles, "legacy_nsw_panel")
    legacy_annual = input_key(profiles, "legacy_annual_fiscal")
    legacy_disasters = input_key(profiles, "legacy_disasters")
    legacy_links = input_key(profiles, "legacy_disaster_links")
    legacy_projects = input_key(profiles, "legacy_projects")
    legacy_accounting = input_key(profiles, "legacy_accounting")
    legacy_financing = input_key(profiles, "legacy_financing")
    legacy_payment = input_key(profiles, "legacy_payment_timing")
    legacy_treatment = input_key(profiles, "legacy_treatment")

    statements: list[str] = [
        "PRAGMA threads=1;",
        "SET preserve_insertion_order=true;",
        "DROP SCHEMA IF EXISTS master CASCADE;",
        "DROP SCHEMA IF EXISTS provenance CASCADE;",
        "DROP SCHEMA IF EXISTS experiments CASCADE;",
        "DROP SCHEMA IF EXISTS metadata CASCADE;",
        "DROP SCHEMA IF EXISTS stage CASCADE;",
        "CREATE SCHEMA master;",
        "CREATE SCHEMA provenance;",
        "CREATE SCHEMA experiments;",
        "CREATE SCHEMA metadata;",
        "CREATE SCHEMA stage;",
        "CREATE OR REPLACE MACRO norm_name(v) AS regexp_replace(lower(trim(coalesce(CAST(v AS VARCHAR), ''))), '[^a-z0-9]+', '_', 'g');",
        "CREATE OR REPLACE MACRO council_id_for(v) AS CASE WHEN nullif(norm_name(v), '') IS NULL THEN NULL ELSE 'council_' || md5(norm_name(v)) END;",
        "CREATE OR REPLACE MACRO disaster_token(v) AS CASE WHEN regexp_matches(trim(coalesce(CAST(v AS VARCHAR), '')), '^(event:)?[0-9]+$') THEN 'agrn:' || regexp_replace(trim(CAST(v AS VARCHAR)), '^event:', '') ELSE 'label:' || lower(trim(coalesce(CAST(v AS VARCHAR), ''))) END;",
        input_manifest_sql(profiles),
    ]

    for spec in INPUTS:
        path = PROJECT_ROOT / spec.relative_path
        statements.append(
            "CREATE OR REPLACE TABLE stage."
            + sql_identifier(spec.stage_name)
            + " AS SELECT *, row_number() OVER ()::BIGINT AS source_row_number FROM read_csv_auto("
            + sql_string(path)
            + ", header=true, sample_size=-1, ignore_errors=false);"
        )

    # Every input file receives a stable source key. Document sources from the
    # Experiment 4 register receive their own stable key and are not confused
    # with the CSV container that carried the row.
    statements.append(
        f"""
        CREATE OR REPLACE TABLE provenance.source_catalog AS
        SELECT
            input_key AS source_key,
            input_name AS source_id,
            'cleaned_input_csv' AS source_type,
            relative_path AS local_file,
            CAST(NULL AS VARCHAR) AS source_url,
            sha256,
            CAST(NULL AS DATE) AS publication_date,
            description AS provenance_note
        FROM provenance.input_files
        UNION ALL
        SELECT
            'document_' || md5(concat_ws('|', CAST(source_id AS VARCHAR), CAST(url AS VARCHAR), CAST(local_file AS VARCHAR), CAST(sha256 AS VARCHAR))) AS source_key,
            CAST(source_id AS VARCHAR) AS source_id,
            'document_source' AS source_type,
            CAST(local_file AS VARCHAR) AS local_file,
            CAST(url AS VARCHAR) AS source_url,
            CAST(sha256 AS VARCHAR) AS sha256,
            try_cast(publication_date AS DATE) AS publication_date,
            CAST(evidence_status AS VARCHAR) AS provenance_note
        FROM stage.e4_sources;
        """.strip()
    )
    statements.append(
        "CREATE OR REPLACE TABLE master.sources AS SELECT * FROM provenance.source_catalog ORDER BY source_type, source_id;"
    )

    # Council labels remain exact labels.  A normalized name is used only to
    # make a deterministic internal ID; it is not an official ABS identifier.
    statements.append(
        f"""
        CREATE OR REPLACE TABLE master.councils AS
        WITH labels AS (
            SELECT trim(CAST(council_name AS VARCHAR)) AS council_name, CAST(council_key AS VARCHAR) AS source_council_key, CAST(jurisdiction AS VARCHAR) AS jurisdiction, 'e4_councils' AS source_dataset FROM stage.e4_councils WHERE nullif(trim(CAST(council_name AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council_name AS VARCHAR)), CAST(council_key AS VARCHAR), 'NSW', 'e2_fiscal_panel' FROM stage.e2_fiscal_panel WHERE nullif(trim(CAST(council_name AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), CAST(council_key AS VARCHAR), 'NSW', 'legacy_nsw_panel' FROM stage.legacy_nsw_panel WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'legacy_annual_fiscal' FROM stage.legacy_annual_fiscal WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'legacy_projects' FROM stage.legacy_projects WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'legacy_accounting' FROM stage.legacy_accounting WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'legacy_financing' FROM stage.legacy_financing WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'legacy_payment_timing' FROM stage.legacy_payment_timing WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'legacy_treatment' FROM stage.legacy_treatment WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT trim(CAST(council AS VARCHAR)), NULL, 'NSW', 'e4_evidence_master_expanded' FROM stage.e4_evidence_master_expanded WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
        )
        SELECT
            council_id_for(council_name) AS council_id,
            min(council_name) AS council_name,
            norm_name(council_name) AS normalized_name,
            coalesce(min(jurisdiction), 'NSW') AS jurisdiction,
            'NSW local council label' AS entity_class,
            'exact_label_hash' AS identity_basis,
            count(*)::BIGINT AS observed_source_rows
        FROM labels
        GROUP BY norm_name(council_name), council_id_for(council_name)
        ORDER BY council_name;
        """.strip()
    )
    statements.append(
        f"""
        CREATE OR REPLACE TABLE master.council_aliases AS
        WITH aliases AS (
            SELECT {sql_string(e4_councils)} AS source_key, {sql_string('e4_councils')} AS source_dataset, CAST(source_row_number AS VARCHAR) AS source_record_key, CAST(council_key AS VARCHAR) AS source_council_key, trim(CAST(council_name AS VARCHAR)) AS source_council_name, 'declared_dimension_label' AS match_status FROM stage.e4_councils
            UNION ALL SELECT {sql_string(e2_fiscal)} , {sql_string('e2_fiscal_panel')}, CAST(source_row_number AS VARCHAR), CAST(council_key AS VARCHAR), trim(CAST(council_name AS VARCHAR)), 'source_panel_label' FROM stage.e2_fiscal_panel WHERE nullif(trim(CAST(council_name AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_panel)} , {sql_string('legacy_nsw_panel')}, CAST(source_row_number AS VARCHAR), CAST(council_key AS VARCHAR), trim(CAST(council AS VARCHAR)), 'legacy_panel_label' FROM stage.legacy_nsw_panel WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_annual)} , {sql_string('legacy_annual_fiscal')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'legacy_source_label' FROM stage.legacy_annual_fiscal WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_projects)} , {sql_string('legacy_projects')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'legacy_source_label' FROM stage.legacy_projects WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_accounting)} , {sql_string('legacy_accounting')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'legacy_source_label' FROM stage.legacy_accounting WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_financing)} , {sql_string('legacy_financing')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'legacy_source_label' FROM stage.legacy_financing WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_payment)} , {sql_string('legacy_payment_timing')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'legacy_source_label' FROM stage.legacy_payment_timing WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(legacy_treatment)} , {sql_string('legacy_treatment')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'legacy_source_label' FROM stage.legacy_treatment WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
            UNION ALL SELECT {sql_string(e4_evidence)} , {sql_string('e4_evidence_master_expanded')}, CAST(source_row_number AS VARCHAR), NULL, trim(CAST(council AS VARCHAR)), 'evidence_register_label' FROM stage.e4_evidence_master_expanded WHERE nullif(trim(CAST(council AS VARCHAR)), '') IS NOT NULL
        )
        SELECT DISTINCT
            'alias_' || md5(concat_ws('|', source_key, source_record_key, source_council_name)) AS council_alias_id,
            council_id_for(source_council_name) AS council_id,
            source_council_key,
            source_council_name,
            norm_name(source_council_name) AS normalized_name,
            source_key,
            source_dataset,
            source_record_key,
            match_status
        FROM aliases
        WHERE nullif(trim(source_council_name), '') IS NOT NULL;
        """.strip()
    )

    # Stable disaster identity is based on AGRN where present, otherwise on
    # the exact reported label.  Source variants remain in disaster_sources.
    statements.append(
        f"""
        CREATE OR REPLACE TABLE stage.disaster_source_rows AS
        SELECT
            'legacy_disasters' AS source_dataset,
            {sql_string(legacy_disasters)} AS source_key,
            {source_row_key_sql(legacy_disasters)} AS source_record_key,
            disaster_token(CAST(agrn AS VARCHAR)) AS disaster_token,
            CAST(agrn AS VARCHAR) AS source_event_id,
            CAST(agrn AS VARCHAR) AS reported_event_id,
            CAST(agrn AS VARCHAR) AS agrn,
            CAST(event_name AS VARCHAR) AS event_name,
            CAST(hazard_raw AS VARCHAR) AS hazard,
            CAST(source_fy AS VARCHAR) AS source_fy,
            try_cast(event_start AS DATE) AS event_start_lower,
            try_cast(event_start AS DATE) AS event_start_upper,
            CAST(date_parse_status AS VARCHAR) AS identity_status,
            CAST(source_url AS VARCHAR) AS source_url
        FROM stage.legacy_disasters s
        WHERE nullif(trim(CAST(agrn AS VARCHAR)), '') IS NOT NULL
        UNION ALL
        SELECT
            'e4_disasters', {sql_string(e4_disasters)}, {source_row_key_sql(e4_disasters, 'd')},
            disaster_token(CAST(reported_event_id AS VARCHAR)),
            CAST(reported_event_id AS VARCHAR), CAST(reported_event_id AS VARCHAR), NULL,
            NULL, NULL, NULL, NULL, NULL, CAST(identity_status AS VARCHAR), NULL
        FROM stage.e4_disasters d
        UNION ALL
        SELECT
            'e2_declaration_events', {sql_string(e2_events)}, {source_row_key_sql(e2_events, 'e')},
            disaster_token(coalesce(NULLIF(trim(CAST(agrn AS VARCHAR)), ''), CAST(event_id AS VARCHAR))),
            CAST(event_id AS VARCHAR), CAST(agrn AS VARCHAR), CAST(agrn AS VARCHAR),
            CAST(event_id AS VARCHAR), CAST(reported_hazard AS VARCHAR), CAST(financial_year AS VARCHAR),
            onset_date_lower_bound, onset_date_upper_bound, CAST(publication_date_status AS VARCHAR), CAST(source_url AS VARCHAR)
        FROM stage.e2_declaration_events e;

        CREATE OR REPLACE TABLE master.disaster_sources AS
        SELECT
            'disaster_' || md5(disaster_token) AS disaster_id,
            source_dataset, source_key, source_record_key, source_event_id,
            reported_event_id, agrn, event_name, hazard, source_fy,
            event_start_lower, event_start_upper, identity_status, source_url
        FROM stage.disaster_source_rows;

        CREATE OR REPLACE TABLE master.disasters AS
        SELECT
            'disaster_' || md5(disaster_token) AS disaster_id,
            min(NULLIF(reported_event_id, '')) AS reported_event_id,
            min(NULLIF(agrn, '')) AS agrn,
            min(NULLIF(event_name, '')) AS event_name,
            min(NULLIF(hazard, '')) AS hazard,
            min(NULLIF(source_fy, '')) AS source_fy,
            min(event_start_lower) AS event_start_lower,
            max(event_start_upper) AS event_start_upper,
            min(NULLIF(identity_status, '')) AS identity_status,
            count(*)::BIGINT AS source_record_count
        FROM stage.disaster_source_rows
        GROUP BY disaster_token
        ORDER BY disaster_id;
        """.strip()
    )

    statements.append(
        f"""
        CREATE OR REPLACE TABLE master.disaster_declarations AS
        SELECT
            'declaration_' || md5(concat_ws('|', {sql_string(e2_events)}, CAST(e.source_row_number AS VARCHAR))) AS declaration_id,
            'disaster_' || md5(disaster_token(coalesce(NULLIF(trim(CAST(e.agrn AS VARCHAR)), ''), CAST(e.event_id AS VARCHAR)))) AS disaster_id,
            CAST(e.record_id AS VARCHAR) AS source_record_id,
            CAST(e.event_id AS VARCHAR) AS source_event_id,
            CAST(e.source_id AS VARCHAR) AS source_document_id,
            CAST(e.source_file AS VARCHAR) AS source_file,
            CAST(e.source_url AS VARCHAR) AS source_url,
            e.pdf_page,
            CAST(e.reported_event_date AS VARCHAR) AS reported_event_date,
            CAST(e.reported_hazard AS VARCHAR) AS reported_hazard,
            CAST(e.reported_area AS VARCHAR) AS reported_area,
            e.agricultural_only,
            CAST(e.agrn AS VARCHAR) AS agrn,
            CAST(e.declaration_announcement_date AS VARCHAR) AS declaration_announcement_date,
            CAST(e.source_first_publication_date AS VARCHAR) AS source_first_publication_date,
            CAST(e.publication_date_status AS VARCHAR) AS publication_date_status,
            e.onset_date_lower_bound,
            e.onset_date_upper_bound,
            e.reported_end_date,
            e.date_precision,
            e.year_start,
            e.financial_year,
            e.hazard_group,
            e.include_in_historical_panel,
            e.exclusion_reason,
            {sql_string(e2_events)} AS source_key,
            {source_row_key_sql(e2_events, 'e')} AS source_record_key
        FROM stage.e2_declaration_events e;

        CREATE OR REPLACE TABLE master.disaster_council_links AS
        SELECT
            'disaster_council_link_' || md5(concat_ws('|', {sql_string(legacy_links)}, CAST(l.source_row_number AS VARCHAR))) AS link_id,
            'disaster_' || md5(disaster_token(CAST(l.agrn AS VARCHAR))) AS disaster_id,
            council_id_for(l.council) AS council_id,
            NULLIF(trim(CAST(l.council AS VARCHAR)), '') AS source_council_name,
            CAST(l.lga_raw AS VARCHAR) AS source_lga_name,
            CAST(l.source_fy AS VARCHAR) AS source_fy,
            try_cast(regexp_extract(CAST(l.source_fy AS VARCHAR), '^[0-9]{{4}}') AS INTEGER) AS year_start,
            CAST(l.source_url AS VARCHAR) AS source_url,
            CAST(l.repair_note AS VARCHAR) AS repair_note,
            l.out_of_scope,
            CAST(l.extension_note AS VARCHAR) AS extension_note,
            {sql_string(legacy_links)} AS source_key,
            {source_row_key_sql(legacy_links, 'l')} AS source_record_key,
            'legacy_disaster_link' AS source_dataset
        FROM stage.legacy_disaster_links l
        UNION ALL
        SELECT
            'disaster_council_link_' || md5(concat_ws('|', {sql_string(e2_links)}, CAST(l.source_row_number AS VARCHAR))) AS link_id,
            'disaster_' || md5(disaster_token(CAST(l.event_id AS VARCHAR))) AS disaster_id,
            council_id_for(c.council_name) AS council_id,
            CAST(c.council_name AS VARCHAR),
            CAST(l.council_name_source AS VARCHAR),
            NULL,
            l.year_start,
            NULL,
            NULL,
            NULL,
            NULL,
            {sql_string(e2_links)},
            {source_row_key_sql(e2_links, 'l')},
            'e2_declaration_link'
        FROM stage.e2_declaration_links l
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(l.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.disaster_observations AS
        SELECT
            'disaster_observation_' || md5(concat_ws('|', {sql_string(e4_disaster_obs)}, CAST(o.source_row_number AS VARCHAR))) AS observation_key,
            CAST(o.observation_id AS VARCHAR) AS source_observation_id,
            'disaster_' || md5(disaster_token(CAST(o.disaster_id AS VARCHAR))) AS disaster_id,
            council_id_for(c.council_name) AS council_id,
            CAST(o.council_key AS VARCHAR) AS source_council_key,
            o.date,
            CAST(o.date_type AS VARCHAR) AS date_type,
            CAST(o.limitation AS VARCHAR) AS limitation,
            CAST(o.source_id AS VARCHAR) AS source_document_id,
            CAST(o.underlying_source_url AS VARCHAR) AS underlying_source_url,
            {sql_string(e4_disaster_obs)} AS source_key,
            {source_row_key_sql(e4_disaster_obs, 'o')} AS source_record_key
        FROM stage.e4_disaster_observations o
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(o.council_key AS VARCHAR);
        """.strip()
    )

    # Stable project IDs use the source's explicit project ID when available.
    # Legacy program rows are kept distinct because there is no certified
    # cross-document identifier for them.
    statements.append(
        f"""
        CREATE OR REPLACE TABLE stage.e4_project_map AS
        SELECT
            CAST(project_id AS VARCHAR) AS source_project_id,
            'project_' || md5(concat_ws('|', 'e4', coalesce(NULLIF(trim(CAST(project_id AS VARCHAR)), ''), CAST(source_row_number AS VARCHAR)))) AS project_id,
            CAST(official_project_id AS VARCHAR) AS official_project_id,
            CAST(analyst_record_id AS VARCHAR) AS analyst_record_id,
            CAST(council_key AS VARCHAR) AS source_council_key
        FROM stage.e4_projects;

        CREATE OR REPLACE TABLE stage.e4_project_ref_map AS
        SELECT source_project_id AS project_ref, project_id FROM stage.e4_project_map WHERE nullif(trim(source_project_id), '') IS NOT NULL
        UNION ALL SELECT official_project_id, project_id FROM stage.e4_project_map WHERE nullif(trim(official_project_id), '') IS NOT NULL
        UNION ALL SELECT analyst_record_id, project_id FROM stage.e4_project_map WHERE nullif(trim(analyst_record_id), '') IS NOT NULL;

        CREATE OR REPLACE TABLE master.projects AS
        SELECT
            m.project_id,
            council_id_for(c.council_name) AS council_id,
            CAST(p.council_key AS VARCHAR) AS source_council_key,
            CAST(p.project_id AS VARCHAR) AS source_project_id,
            CAST(p.official_project_id AS VARCHAR) AS official_project_id,
            CAST(p.analyst_record_id AS VARCHAR) AS analyst_record_id,
            CAST(p.project_label AS VARCHAR) AS project_name,
            CAST(NULL AS VARCHAR) AS program,
            CAST(p.unit_status AS VARCHAR) AS unit_status,
            CAST(p.identifier_status AS VARCHAR) AS identifier_status,
            CAST(p.spending_class AS VARCHAR) AS spending_class,
            CAST(p.cross_document_link_status AS VARCHAR) AS cross_document_link_status,
            CAST(NULL AS VARCHAR) AS classification,
            try_cast(p.original_completion_date AS DATE) AS original_completion_date,
            try_cast(p.actual_completion_date AS DATE) AS actual_completion_date,
            p.deferral_decision_date,
            CAST(p.rephased_to_fy AS VARCHAR) AS rephased_to_fy,
            CAST(p.completion_status AS VARCHAR) AS completion_status,
            CAST(p.fixed_pre_event_portfolio_verified AS BOOLEAN) AS fixed_pre_event_portfolio_verified,
            CAST(NULL AS DOUBLE) AS share_deferred_pct,
            CAST(NULL AS VARCHAR) AS earlier_program,
            CAST(NULL AS VARCHAR) AS later_program,
            CAST(NULL AS DOUBLE) AS budget_aud,
            CAST(NULL AS DOUBLE) AS spent_aud,
            CAST(NULL AS BOOLEAN) AS valid_clean_outcome,
            CAST(NULL AS VARCHAR) AS missing_evidence,
            CAST(p.source_id AS VARCHAR) AS source_document_id,
            CAST(p.source_page AS VARCHAR) AS source_page,
            {sql_string(e4_projects)} AS source_key,
            {source_row_key_sql(e4_projects, 'p')} AS source_record_key,
            'e4_project_ledger' AS source_dataset
        FROM stage.e4_projects p
        JOIN stage.e4_project_map m ON m.source_project_id = CAST(p.project_id AS VARCHAR)
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(p.council_key AS VARCHAR)
        UNION ALL
        SELECT
            'project_' || md5(concat_ws('|', 'legacy', coalesce(CAST(p.council AS VARCHAR), ''), coalesce(CAST(p.program AS VARCHAR), ''), coalesce(CAST(p.source_url AS VARCHAR), ''), coalesce(CAST(p.page AS VARCHAR), ''))) AS project_id,
            council_id_for(p.council) AS council_id,
            NULL,
            NULL,
            NULL,
            NULL,
            CAST(p.program AS VARCHAR),
            CAST(p.program AS VARCHAR),
            NULL,
            NULL,
            NULL,
            NULL,
            CAST(p.classification AS VARCHAR),
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            CAST(p.share_deferred_pct AS DOUBLE),
            CAST(p.earlier_program AS VARCHAR),
            CAST(p.later_program AS VARCHAR),
            CAST(p.budget_aud AS DOUBLE),
            CAST(p.spent_aud AS DOUBLE),
            p.valid_clean_outcome,
            CAST(p.missing_evidence AS VARCHAR),
            NULL,
            CAST(p.page AS VARCHAR),
            {sql_string(legacy_projects)},
            {source_row_key_sql(legacy_projects, 'p')},
            'legacy_project_ledger'
        FROM stage.legacy_projects p;
        """.strip()
    )

    statements.append(
        f"""
        CREATE OR REPLACE TABLE master.project_financials AS
        SELECT
            'project_financial_' || md5(concat_ws('|', {sql_string(e4_budgets)}, CAST(b.source_row_number AS VARCHAR))) AS financial_record_id,
            m.project_id,
            council_id_for(c.council_name) AS council_id,
            CAST(b.project_id AS VARCHAR) AS source_project_id,
            b.year_start,
            CAST(b.stage AS VARCHAR) AS stage,
            b.amount_aud,
            CAST(b.value_status AS VARCHAR) AS value_status,
            CAST(b.amount_basis AS VARCHAR) AS amount_basis,
            b.reference_period_end,
            b.decision_date,
            CAST(b.decision_status AS VARCHAR) AS decision_status,
            CAST(b.source_id AS VARCHAR) AS source_document_id,
            CAST(b.source_page AS VARCHAR) AS source_page,
            CAST(b.decision_source_id AS VARCHAR) AS decision_source_id,
            CAST(b.evidence_limit AS VARCHAR) AS evidence_limit,
            CAST(b.model_eligible AS BOOLEAN) AS model_eligible,
            CAST(NULL AS DOUBLE) AS budget_aud,
            CAST(NULL AS DOUBLE) AS spent_aud,
            CAST(NULL AS DOUBLE) AS unspent_budget_aud,
            {sql_string(e4_budgets)} AS source_key,
            {source_row_key_sql(e4_budgets, 'b')} AS source_record_key,
            'e4_budget_snapshot' AS source_dataset
        FROM stage.e4_budgets b
        LEFT JOIN stage.e4_project_map m ON m.source_project_id = CAST(b.project_id AS VARCHAR)
        LEFT JOIN stage.e4_projects p ON CAST(p.project_id AS VARCHAR) = CAST(b.project_id AS VARCHAR)
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(p.council_key AS VARCHAR)
        UNION ALL
        SELECT
            'project_financial_' || md5(concat_ws('|', {sql_string(legacy_projects)}, CAST(p.source_row_number AS VARCHAR))) AS financial_record_id,
            'project_' || md5(concat_ws('|', 'legacy', coalesce(CAST(p.council AS VARCHAR), ''), coalesce(CAST(p.program AS VARCHAR), ''), coalesce(CAST(p.source_url AS VARCHAR), ''), coalesce(CAST(p.page AS VARCHAR), ''))) AS project_id,
            council_id_for(p.council),
            NULL,
            NULL,
            'legacy_program_ledger',
            CAST(coalesce(p.budget_aud, p.spent_aud) AS DOUBLE),
            CASE WHEN p.budget_aud IS NULL AND p.spent_aud IS NULL THEN 'unavailable' ELSE 'source_row' END,
            'legacy project/program ledger',
            NULL,
            NULL,
            NULL,
            NULL,
            CAST(p.page AS VARCHAR),
            NULL,
            CAST(p.missing_evidence AS VARCHAR),
            p.valid_clean_outcome,
            CAST(p.budget_aud AS DOUBLE),
            CAST(p.spent_aud AS DOUBLE),
            CASE WHEN p.budget_aud IS NOT NULL AND p.spent_aud IS NOT NULL THEN p.budget_aud - p.spent_aud ELSE NULL END,
            {sql_string(legacy_projects)},
            {source_row_key_sql(legacy_projects, 'p')},
            'legacy_project_ledger'
        FROM stage.legacy_projects p;

        CREATE OR REPLACE TABLE master.project_evidence AS
        SELECT
            'project_evidence_' || md5(concat_ws('|', {sql_string(e4_project_evidence)}, CAST(e.source_row_number AS VARCHAR))) AS project_evidence_key,
            CAST(e.evidence_id AS VARCHAR) AS source_evidence_id,
            m.project_id,
            CASE WHEN m.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            council_id_for(c.council_name) AS council_id,
            e.* EXCLUDE (project_id, source_row_number),
            {sql_string(e4_project_evidence)} AS source_key,
            {source_row_key_sql(e4_project_evidence, 'e')} AS source_record_key
        FROM stage.e4_project_evidence e
        LEFT JOIN stage.e4_project_map m ON m.source_project_id = CAST(e.project_id AS VARCHAR)
        LEFT JOIN stage.e4_projects p ON CAST(p.project_id AS VARCHAR) = CAST(e.project_id AS VARCHAR)
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(p.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.project_linkage_audit AS
        SELECT
            'project_linkage_' || md5(concat_ws('|', {sql_string(e4_project_linkage)}, CAST(a.source_row_number AS VARCHAR))) AS linkage_audit_key,
            m.project_id,
            CASE WHEN m.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            a.* EXCLUDE (project_id, source_row_number),
            {sql_string(e4_project_linkage)} AS source_key,
            {source_row_key_sql(e4_project_linkage, 'a')} AS source_record_key
        FROM stage.e4_project_linkage a
        LEFT JOIN stage.e4_project_map m ON m.source_project_id = CAST(a.project_id AS VARCHAR);

        CREATE OR REPLACE TABLE master.project_milestones AS
        SELECT
            'project_milestone_' || md5(concat_ws('|', {sql_string(e4_project_milestones)}, CAST(mil.source_row_number AS VARCHAR))) AS milestone_key,
            pm.project_id,
            CASE WHEN pm.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            mil.* EXCLUDE (project_id, source_row_number),
            {sql_string(e4_project_milestones)} AS source_key,
            {source_row_key_sql(e4_project_milestones, 'mil')} AS source_record_key
        FROM stage.e4_project_milestones mil
        LEFT JOIN stage.e4_project_map pm ON pm.source_project_id = CAST(mil.project_id AS VARCHAR);

        CREATE OR REPLACE TABLE master.project_revisions AS
        SELECT
            'project_revision_' || md5(concat_ws('|', {sql_string(e4_project_revisions)}, CAST(r.source_row_number AS VARCHAR))) AS revision_key,
            pm.project_id,
            CASE WHEN pm.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            r.* EXCLUDE (project_id, source_row_number),
            {sql_string(e4_project_revisions)} AS source_key,
            {source_row_key_sql(e4_project_revisions, 'r')} AS source_record_key
        FROM stage.e4_project_revisions r
        LEFT JOIN stage.e4_project_map pm ON pm.source_project_id = CAST(r.project_id AS VARCHAR);

        CREATE OR REPLACE TABLE master.damage_status AS
        SELECT
            'damage_status_' || md5(concat_ws('|', {sql_string(e4_damage)}, CAST(d.source_row_number AS VARCHAR))) AS damage_status_key,
            pm.project_id,
            CASE WHEN pm.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            'disaster_' || md5(disaster_token(CAST(d.disaster_id AS VARCHAR))) AS disaster_id,
            d.* EXCLUDE (project_id, disaster_id, source_row_number),
            {sql_string(e4_damage)} AS source_key,
            {source_row_key_sql(e4_damage, 'd')} AS source_record_key
        FROM stage.e4_damage_status d
        LEFT JOIN stage.e4_project_map pm ON pm.source_project_id = CAST(d.project_id AS VARCHAR);
        """.strip()
    )

    statements.append(
        f"""
        CREATE OR REPLACE TABLE master.fiscal_annual AS
        SELECT
            'fiscal_record_' || md5(concat_ws('|', {sql_string(e4_fiscal)}, CAST(f.source_row_number AS VARCHAR))) AS fiscal_record_id,
            council_id_for(c.council_name) AS council_id,
            CASE WHEN c.council_key IS NULL THEN 'unresolved_source_council_key' ELSE 'exact_source_council_key' END AS council_resolution_status,
            f.* EXCLUDE (source_row_number),
            {sql_string(e4_fiscal)} AS source_key,
            {source_row_key_sql(e4_fiscal, 'f')} AS source_record_key
        FROM stage.e4_fiscal_annual f
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(f.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.fiscal_panel_extended AS
        SELECT
            'fiscal_extended_' || md5(concat_ws('|', {sql_string(e2_fiscal)}, CAST(f.source_row_number AS VARCHAR))) AS fiscal_panel_record_id,
            council_id_for(f.council_name) AS council_id,
            CASE WHEN c.council_key IS NULL THEN 'unresolved_source_council_key' ELSE 'exact_source_council_name' END AS council_resolution_status,
            f.* EXCLUDE (source_row_number),
            {sql_string(e2_fiscal)} AS source_key,
            {source_row_key_sql(e2_fiscal, 'f')} AS source_record_key
        FROM stage.e2_fiscal_panel f
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(f.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.fiscal_panel_legacy AS
        SELECT
            'fiscal_legacy_' || md5(concat_ws('|', {sql_string(legacy_panel)}, CAST(p.source_row_number AS VARCHAR))) AS fiscal_panel_record_id,
            council_id_for(p.council) AS council_id,
            'legacy_source_label' AS council_resolution_status,
            p.* EXCLUDE (source_row_number),
            {sql_string(legacy_panel)} AS source_key,
            {source_row_key_sql(legacy_panel, 'p')} AS source_record_key
        FROM stage.legacy_nsw_panel p;

        CREATE OR REPLACE TABLE master.legacy_fiscal_measurements AS
        SELECT
            'legacy_fiscal_measurement_' || md5(concat_ws('|', {sql_string(legacy_annual)}, CAST(a.source_row_number AS VARCHAR))) AS fiscal_measurement_id,
            council_id_for(a.council) AS council_id,
            'legacy_source_label' AS council_resolution_status,
            a.* EXCLUDE (source_row_number),
            {sql_string(legacy_annual)} AS source_key,
            {source_row_key_sql(legacy_annual, 'a')} AS source_record_key
        FROM stage.legacy_annual_fiscal a;

        CREATE OR REPLACE TABLE master.exposure_observations AS
        SELECT
            'exposure_' || md5(concat_ws('|', {sql_string(e2_exposure)}, CAST(e.source_row_number AS VARCHAR))) AS exposure_id,
            council_id_for(e.council_name) AS council_id,
            CASE WHEN c.council_key IS NULL THEN 'unresolved_source_council_key' ELSE 'exact_source_council_name' END AS council_resolution_status,
            e.* EXCLUDE (source_row_number),
            {sql_string(e2_exposure)} AS source_key,
            {source_row_key_sql(e2_exposure, 'e')} AS source_record_key
        FROM stage.e2_exposure_panel e
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(e.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.fire_zonal_statistics AS
        SELECT
            'fire_zonal_' || md5(concat_ws('|', {sql_string(e2_fire)}, CAST(f.source_row_number AS VARCHAR))) AS fire_observation_id,
            council_id_for(c.council_name) AS council_id,
            CASE WHEN c.council_key IS NULL THEN 'unresolved_source_council_key' ELSE 'exact_source_council_key' END AS council_resolution_status,
            f.* EXCLUDE (source_row_number),
            {sql_string(e2_fire)} AS source_key,
            {source_row_key_sql(e2_fire, 'f')} AS source_record_key
        FROM stage.e2_historical_fire f
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(f.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.fesm_reconciliation AS
        SELECT
            'fesm_reconciliation_' || md5(concat_ws('|', {sql_string(e2_fesm)}, CAST(f.source_row_number AS VARCHAR))) AS reconciliation_id,
            council_id_for(c.council_name) AS council_id,
            CASE WHEN c.council_key IS NULL THEN 'unresolved_source_council_key' ELSE 'exact_source_council_key' END AS council_resolution_status,
            f.* EXCLUDE (source_row_number),
            {sql_string(e2_fesm)} AS source_key,
            {source_row_key_sql(e2_fesm, 'f')} AS source_record_key
        FROM stage.e2_fesm_reconciliation f
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(f.council_key AS VARCHAR);
        """.strip()
    )

    statements.append(
        f"""
        CREATE OR REPLACE TABLE master.capacity_observations AS
        SELECT
            'capacity_' || md5(concat_ws('|', {sql_string(e4_capacity)}, CAST(o.source_row_number AS VARCHAR))) AS capacity_observation_id,
            council_id_for(c.council_name) AS council_id,
            CASE WHEN c.council_key IS NULL THEN 'unresolved_source_council_key' ELSE 'exact_source_council_key' END AS council_resolution_status,
            o.* EXCLUDE (source_row_number),
            {sql_string(e4_capacity)} AS source_key,
            {source_row_key_sql(e4_capacity, 'o')} AS source_record_key
        FROM stage.e4_capacity o
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(o.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.evidence_records AS
        SELECT
            'evidence_' || md5(concat_ws('|', {sql_string(e4_evidence)}, CAST(e.record_id AS VARCHAR))) AS evidence_id,
            council_id_for(e.council) AS council_id,
            CASE WHEN council_id_for(e.council) IS NULL THEN 'missing_council_label' ELSE 'exact_source_label_hash' END AS council_resolution_status,
            pm.project_id,
            CASE WHEN pm.project_id IS NULL AND nullif(trim(CAST(e.project_ref AS VARCHAR)), '') IS NULL THEN 'no_project_reference' WHEN pm.project_id IS NULL THEN 'unresolved_project_reference' ELSE 'exact_project_reference' END AS project_resolution_status,
            CAST(e.record_id AS VARCHAR) AS source_record_id,
            e.* EXCLUDE (record_id, source_row_number),
            {sql_string(e4_evidence)} AS source_key,
            {source_row_key_sql(e4_evidence, 'e')} AS source_record_key
        FROM stage.e4_evidence_master_expanded e
        LEFT JOIN stage.e4_project_ref_map pm ON trim(CAST(e.project_ref AS VARCHAR)) = trim(CAST(pm.project_ref AS VARCHAR));

        CREATE OR REPLACE TABLE master.accounting_snapshots AS
        SELECT
            'accounting_snapshot_' || md5(concat_ws('|', {sql_string(legacy_accounting)}, CAST(a.source_row_number AS VARCHAR))) AS accounting_snapshot_id,
            council_id_for(a.council) AS council_id,
            a.* EXCLUDE (source_row_number),
            {sql_string(legacy_accounting)} AS source_key,
            {source_row_key_sql(legacy_accounting, 'a')} AS source_record_key
        FROM stage.legacy_accounting a;

        CREATE OR REPLACE TABLE master.financing_observations AS
        SELECT
            'financing_' || md5(concat_ws('|', {sql_string(legacy_financing)}, CAST(f.source_row_number AS VARCHAR))) AS financing_observation_id,
            council_id_for(f.council) AS council_id,
            f.* EXCLUDE (source_row_number),
            {sql_string(legacy_financing)} AS source_key,
            {source_row_key_sql(legacy_financing, 'f')} AS source_record_key
        FROM stage.legacy_financing f;

        CREATE OR REPLACE TABLE master.payment_timing_evidence AS
        SELECT
            'payment_timing_' || md5(concat_ws('|', {sql_string(legacy_payment)}, CAST(p.source_row_number AS VARCHAR))) AS payment_timing_id,
            council_id_for(p.council) AS council_id,
            CASE WHEN nullif(trim(CAST(p.agrn AS VARCHAR)), '') IS NULL THEN NULL ELSE 'disaster_' || md5(disaster_token(CAST(p.agrn AS VARCHAR))) END AS disaster_id,
            p.* EXCLUDE (source_row_number),
            {sql_string(legacy_payment)} AS source_key,
            {source_row_key_sql(legacy_payment, 'p')} AS source_record_key
        FROM stage.legacy_payment_timing p;

        CREATE OR REPLACE TABLE master.treatment_roster AS
        SELECT
            'treatment_' || md5(concat_ws('|', {sql_string(legacy_treatment)}, CAST(t.source_row_number AS VARCHAR))) AS treatment_record_id,
            council_id_for(t.council) AS council_id,
            t.* EXCLUDE (source_row_number),
            {sql_string(legacy_treatment)} AS source_key,
            {source_row_key_sql(legacy_treatment, 't')} AS source_record_key
        FROM stage.legacy_treatment t;

        CREATE OR REPLACE TABLE master.fiscal_availability_evidence AS
        SELECT
            'fiscal_availability_' || md5(concat_ws('|', {sql_string(e4_fiscal_availability)}, CAST(a.source_row_number AS VARCHAR))) AS availability_record_id,
            council_id_for(c.council_name) AS council_id,
            a.* EXCLUDE (source_row_number),
            {sql_string(e4_fiscal_availability)} AS source_key,
            {source_row_key_sql(e4_fiscal_availability, 'a')} AS source_record_key
        FROM stage.e4_fiscal_availability a
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(a.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.fiscal_value_audit AS
        SELECT
            'fiscal_value_audit_' || md5(concat_ws('|', {sql_string(e4_fiscal_value_audit)}, CAST(a.source_row_number AS VARCHAR))) AS audit_record_id,
            council_id_for(c.council_name) AS council_id,
            a.* EXCLUDE (source_row_number),
            {sql_string(e4_fiscal_value_audit)} AS source_key,
            {source_row_key_sql(e4_fiscal_value_audit, 'a')} AS source_record_key
        FROM stage.e4_fiscal_value_audit a
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(a.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.review_decisions AS
        SELECT
            'review_decision_' || md5(concat_ws('|', {sql_string(e4_review)}, CAST(r.source_row_number AS VARCHAR))) AS review_decision_key,
            council_id_for(c.council_name) AS council_id,
            r.* EXCLUDE (source_row_number),
            {sql_string(e4_review)} AS source_key,
            {source_row_key_sql(e4_review, 'r')} AS source_record_key
        FROM stage.e4_review_decisions r
        LEFT JOIN stage.e4_councils c ON CAST(c.council_key AS VARCHAR) = CAST(r.council_key AS VARCHAR);

        CREATE OR REPLACE TABLE master.field_gaps AS
        SELECT
            'field_gap_' || md5(concat_ws('|', {sql_string(e4_field_gaps)}, CAST(g.source_row_number AS VARCHAR))) AS field_gap_key,
            pm.project_id,
            CASE WHEN pm.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            g.* EXCLUDE (project_id, source_row_number),
            {sql_string(e4_field_gaps)} AS source_key,
            {source_row_key_sql(e4_field_gaps, 'g')} AS source_record_key
        FROM stage.e4_field_gaps g
        LEFT JOIN stage.e4_project_map pm ON pm.source_project_id = CAST(g.project_id AS VARCHAR);

        CREATE OR REPLACE TABLE master.source_conflicts AS
        SELECT
            'source_conflict_' || md5(concat_ws('|', {sql_string(e4_conflicts)}, CAST(s.source_row_number AS VARCHAR))) AS source_conflict_key,
            pm.project_id,
            CASE WHEN pm.project_id IS NULL THEN 'unresolved_source_project_id' ELSE 'exact_source_project_id' END AS project_resolution_status,
            s.* EXCLUDE (project_id, source_row_number),
            {sql_string(e4_conflicts)} AS source_key,
            {source_row_key_sql(e4_conflicts, 's')} AS source_record_key
        FROM stage.e4_source_conflicts s
        LEFT JOIN stage.e4_project_map pm ON pm.source_project_id = CAST(s.project_id AS VARCHAR);

        CREATE OR REPLACE TABLE master.search_followups AS
        SELECT
            'search_followup_' || md5(concat_ws('|', {sql_string(e4_search)}, CAST(s.source_row_number AS VARCHAR))) AS search_followup_key,
            s.* EXCLUDE (source_row_number),
            {sql_string(e4_search)} AS source_key,
            {source_row_key_sql(e4_search, 's')} AS source_record_key
        FROM stage.e4_search_followup s;

        CREATE OR REPLACE TABLE master.declaration_name_crosswalk AS
        SELECT
            'declaration_name_crosswalk_' || md5(concat_ws('|', {sql_string(e2_crosswalk)}, CAST(c.source_row_number AS VARCHAR))) AS crosswalk_key,
            council_id_for(c.source_name) AS council_id,
            c.* EXCLUDE (source_row_number),
            {sql_string(e2_crosswalk)} AS source_key,
            {source_row_key_sql(e2_crosswalk, 'c')} AS source_record_key
        FROM stage.e2_name_crosswalk c;

        CREATE OR REPLACE TABLE master.fiscal_council_crosswalk AS
        SELECT
            'fiscal_council_crosswalk_' || md5(concat_ws('|', {sql_string(e2_fiscal_crosswalk)}, CAST(c.source_row_number AS VARCHAR))) AS crosswalk_key,
            council_id_for(c.source_name) AS council_id,
            c.* EXCLUDE (source_row_number),
            {sql_string(e2_fiscal_crosswalk)} AS source_key,
            {source_row_key_sql(e2_fiscal_crosswalk, 'c')} AS source_record_key
        FROM stage.e2_fiscal_crosswalk c;
        """.strip()
    )

    # Experiment products are views.  They contain no duplicated physical
    # experiment tables and are built only from the master schema.
    statements.append(
        """
        CREATE OR REPLACE VIEW experiments.experiment_1_fiscal_forecast AS
        WITH exposure AS (
            SELECT council_id, year_start, fesm_burned_ha, fesm_burned_pct_raw, bushfire_declared_event_count, flood_declared_event_count, exposure_provenance
            FROM master.exposure_observations
        )
        SELECT
            f.fiscal_record_id,
            f.council_id,
            c.council_name,
            f.year_start,
            f.financial_year,
            f.operating_ratio_pct,
            f.cash_cover_months,
            f.current_ratio,
            f.own_source_pct,
            f.grants_pct,
            f.debt_service_cover,
            f.population,
            f.strict_pre_event_available,
            lead(f.operating_ratio_pct) OVER (PARTITION BY f.council_id ORDER BY f.year_start) AS next_operating_ratio_pct,
            e.fesm_burned_ha,
            e.fesm_burned_pct_raw,
            e.bushfire_declared_event_count,
            e.flood_declared_event_count,
            e.exposure_provenance,
            f.source_key,
            f.source_record_key
        FROM master.fiscal_annual f
        LEFT JOIN master.councils c USING (council_id)
        LEFT JOIN exposure e USING (council_id, year_start);

        CREATE OR REPLACE VIEW experiments.experiment_2_disaster_exposure AS
        SELECT
            e.exposure_id,
            e.council_id,
            c.council_name,
            e.year_start,
            e.financial_year,
            e.fesm_burned_ha,
            e.fesm_burned_pct_raw,
            e.fesm_extent_only_ha,
            e.fesm_status,
            e.bushfire_declared_event_count,
            e.flood_declared_event_count,
            e.all_declared_event_count,
            e.exposure_provenance,
            e.source_key,
            e.source_record_key
        FROM master.exposure_observations e
        LEFT JOIN master.councils c USING (council_id);

        CREATE OR REPLACE VIEW experiments.experiment_3_project_evidence AS
        WITH evidence AS (
            SELECT project_id, count(*)::BIGINT AS evidence_record_count, count(*) FILTER (WHERE verification IS NOT NULL)::BIGINT AS verified_evidence_count
            FROM master.project_evidence
            GROUP BY project_id
        ), damage AS (
            SELECT project_id, count(*)::BIGINT AS damage_status_record_count, min(damage_status) AS damage_status
            FROM master.damage_status
            GROUP BY project_id
        )
        SELECT
            p.project_id,
            p.council_id,
            c.council_name,
            p.project_name,
            p.official_project_id,
            p.analyst_record_id,
            p.spending_class,
            p.identifier_status,
            p.valid_clean_outcome,
            p.missing_evidence,
            coalesce(e.evidence_record_count, 0) AS evidence_record_count,
            coalesce(e.verified_evidence_count, 0) AS verified_evidence_count,
            coalesce(d.damage_status_record_count, 0) AS damage_status_record_count,
            d.damage_status,
            p.source_key,
            p.source_record_key
        FROM master.projects p
        LEFT JOIN master.councils c USING (council_id)
        LEFT JOIN evidence e USING (project_id)
        LEFT JOIN damage d USING (project_id);

        CREATE OR REPLACE VIEW experiments.experiment_4_budget_revisions AS
        WITH revisions AS (
            SELECT project_id, year_start, count(*)::BIGINT AS revision_count, sum(revision_aud) AS total_revision_aud, min(reason) AS first_revision_reason
            FROM master.project_revisions
            GROUP BY project_id, year_start
        )
        SELECT
            f.financial_record_id,
            f.project_id,
            p.council_id,
            c.council_name,
            f.year_start,
            f.stage,
            f.amount_aud,
            f.budget_aud,
            f.spent_aud,
            f.unspent_budget_aud,
            f.value_status,
            f.model_eligible,
            coalesce(r.revision_count, 0) AS revision_count,
            r.total_revision_aud,
            r.first_revision_reason,
            f.source_key,
            f.source_record_key
        FROM master.project_financials f
        LEFT JOIN master.projects p ON p.project_id = f.project_id
        LEFT JOIN master.councils c ON c.council_id = p.council_id
        LEFT JOIN revisions r ON r.project_id = f.project_id AND r.year_start = f.year_start;

        CREATE OR REPLACE VIEW experiments.experiment_4_evidence_register AS
        SELECT
            e.evidence_id,
            e.council_id,
            c.council_name,
            e.project_id,
            e.project_ref,
            e.project_name,
            e.record_type,
            e.field_group,
            e.field_name,
            e.scope,
            e.value_text,
            e.certification_effect,
            e.model_ready,
            e.council_resolution_status,
            e.project_resolution_status,
            e.source_title,
            e.source_url,
            e.source_locator,
            e.source_key,
            e.source_record_key
        FROM master.evidence_records e
        LEFT JOIN master.councils c USING (council_id);

        CREATE OR REPLACE VIEW experiments.experiment_4_council_year_screen AS
        SELECT
            f.council_id,
            c.council_name,
            f.year_start,
            f.financial_year,
            f.operating_ratio_pct,
            f.cash_cover_months,
            f.current_ratio,
            e.fesm_burned_ha,
            e.fesm_burned_pct_raw,
            e.fesm_status,
            e.physical_flood_status,
            e.bushfire_declared_event_count,
            e.flood_declared_event_count,
            e.exposure_provenance,
            f.source_key AS fiscal_source_key,
            e.source_key AS exposure_source_key
        FROM master.fiscal_annual f
        LEFT JOIN master.councils c USING (council_id)
        LEFT JOIN master.exposure_observations e USING (council_id, year_start);
        """.strip()
    )

    view_rows = [(name, description, grain) for name, description, grain in VIEW_SPECS]
    statements.append(
        "CREATE OR REPLACE TABLE metadata.view_manifest AS SELECT * FROM (VALUES\n"
        + values_sql(view_rows)
        + ") AS v(view_name, grain, base_objects);"
    )
    manifest_selects = []
    for name in MASTER_TABLES:
        manifest_selects.append(
            "SELECT "
            + sql_string(name)
            + " AS object_name, 'master' AS schema_name, 'normalized_master' AS object_kind, "
            + "(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'master' AND table_name = "
            + sql_string(name)
            + ")::BIGINT AS column_count, (SELECT COUNT(*) FROM master."
            + sql_identifier(name)
            + ")::BIGINT AS row_count"
        )
    for name, _, _ in VIEW_SPECS:
        manifest_selects.append(
            "SELECT "
            + sql_string(name)
            + " AS object_name, 'experiments' AS schema_name, 'view' AS object_kind, "
            + "(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'experiments' AND table_name = "
            + sql_string(name)
            + ")::BIGINT AS column_count, (SELECT COUNT(*) FROM experiments."
            + sql_identifier(name)
            + ")::BIGINT AS row_count"
        )
    statements.append(
        "CREATE OR REPLACE TABLE metadata.object_manifest AS\n"
        + "\nUNION ALL\n".join(manifest_selects)
        + ";"
    )
    statements.append(
        """
        CREATE OR REPLACE TABLE metadata.build_info AS
        SELECT
            'canonical AUSSEF master database' AS database_role,
            'data/aussef.duckdb' AS database_path,
            'Stable IDs are deterministic hashes of exact observed source labels/identifiers; no fuzzy entity merge is performed.' AS identity_policy,
            'Raw source files are not build inputs and are not modified.' AS raw_file_policy,
            'Experiment outputs are views over master tables.' AS experiment_policy;
        DROP SCHEMA stage CASCADE;
        """.strip()
    )
    return "\n\n".join(statements) + "\n"


def verify(duckdb_bin: Path, database: Path, profiles: dict[str, dict[str, object]]) -> dict[str, object]:
    table_counts = {}
    for table_name in MASTER_TABLES:
        rows = run_csv_query(duckdb_bin, database, f"SELECT COUNT(*)::BIGINT AS row_count FROM master.{sql_identifier(table_name)};")
        table_counts[table_name] = int(rows[0]["row_count"])
    view_counts = {}
    for view_name, _, _ in VIEW_SPECS:
        rows = run_csv_query(duckdb_bin, database, f"SELECT COUNT(*)::BIGINT AS row_count FROM experiments.{sql_identifier(view_name)};")
        view_counts[view_name] = int(rows[0]["row_count"])

    uniqueness_rows = run_csv_query(
        duckdb_bin,
        database,
        """
        SELECT
            (SELECT COUNT(*) - COUNT(DISTINCT council_id) FROM master.councils) AS duplicate_council_ids,
            (SELECT COUNT(*) - COUNT(DISTINCT disaster_id) FROM master.disasters) AS duplicate_disaster_ids,
            (SELECT COUNT(*) - COUNT(DISTINCT project_id) FROM master.projects) AS duplicate_project_ids,
            (SELECT COUNT(*) - COUNT(DISTINCT evidence_id) FROM master.evidence_records) AS duplicate_evidence_ids,
            (SELECT COUNT(*) - COUNT(DISTINCT source_key) FROM master.sources) AS duplicate_source_keys;
        """.strip(),
    )[0]
    resolution_rows = run_csv_query(
        duckdb_bin,
        database,
        """
        SELECT
            (SELECT COUNT(*) FROM master.fiscal_annual WHERE council_id IS NULL) AS fiscal_unresolved_councils,
            (SELECT COUNT(*) FROM master.exposure_observations WHERE council_id IS NULL) AS exposure_unresolved_councils,
            (SELECT COUNT(*) FROM master.projects WHERE project_id IS NULL) AS projects_unresolved_ids,
            (SELECT COUNT(*) FROM master.evidence_records WHERE evidence_id IS NULL) AS evidence_unresolved_ids,
            (SELECT COUNT(*) FROM master.evidence_records WHERE project_resolution_status = 'unresolved_project_reference') AS evidence_unresolved_project_refs;
        """.strip(),
    )[0]
    stage_check = run_csv_query(
        duckdb_bin,
        database,
        "SELECT COUNT(*)::BIGINT AS n FROM information_schema.schemata WHERE schema_name = 'stage';",
    )[0]
    source_input_paths = [spec.relative_path for spec in INPUTS if "/raw/" in f"/{spec.relative_path}" or "/sources/" in f"/{spec.relative_path}"]
    input_counts = {spec.stage_name: int(profiles[spec.stage_name]["rows"]) for spec in INPUTS}
    all_unique = all(int(value) == 0 for value in uniqueness_rows.values())
    no_unresolved_keys = all(int(resolution_rows[key]) == 0 for key in ("fiscal_unresolved_councils", "exposure_unresolved_councils", "projects_unresolved_ids", "evidence_unresolved_ids"))
    views_present = all(count >= 0 for count in view_counts.values())
    status = "PASS" if all_unique and no_unresolved_keys and not source_input_paths and int(stage_check["n"]) == 0 and views_present else "FAIL"
    return {
        "status": status,
        "database": str(database),
        "duckdb_version": run_csv_query(duckdb_bin, database, "SELECT version() AS version;")[0]["version"],
        "input_profiles": profiles,
        "input_row_counts": input_counts,
        "master_table_row_counts": table_counts,
        "experiment_view_row_counts": view_counts,
        "integrity_checks": {
            "stable_entity_keys_unique": all_unique,
            "stable_key_duplicates": {key: int(value) for key, value in uniqueness_rows.items()},
            "required_master_keys_resolved": no_unresolved_keys,
            "resolution_counts": {key: int(value) for key, value in resolution_rows.items()},
            "stage_schema_removed": int(stage_check["n"]) == 0,
            "no_raw_or_download_source_inputs": not source_input_paths,
            "disallowed_input_paths": source_input_paths,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duckdb", default=None, help="DuckDB CLI path")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--checks-dir", type=Path, default=DEFAULT_CHECKS_DIR)
    args = parser.parse_args()

    project_root = args.project_root.expanduser().resolve()
    database = args.database.expanduser().resolve()
    checks_dir = args.checks_dir.expanduser().resolve()
    duckdb_bin = find_duckdb(args.duckdb)

    profiles: dict[str, dict[str, object]] = {}
    for spec in INPUTS:
        path = project_root / spec.relative_path
        if not path.is_file():
            raise FileNotFoundError(f"Required cleaned input is missing: {path}")
        if "/raw/" in f"/{spec.relative_path}" or "/sources/" in f"/{spec.relative_path}":
            raise ValueError(f"Raw/download source path is not an allowed input: {spec.relative_path}")
        profiles[spec.stage_name] = csv_profile(path, project_root)

    database.parent.mkdir(parents=True, exist_ok=True)
    checks_dir.mkdir(parents=True, exist_ok=True)
    temporary_database = database.with_name("." + database.name + ".building")
    if temporary_database.exists():
        temporary_database.unlink()
    run_duckdb(duckdb_bin, temporary_database, build_sql(profiles))
    verification = verify(duckdb_bin, temporary_database, profiles)
    if verification["status"] != "PASS":
        temporary_database.unlink(missing_ok=True)
        raise RuntimeError("Canonical DuckDB verification failed: " + json.dumps(verification["integrity_checks"], sort_keys=True))

    os.replace(temporary_database, database)
    verification["database"] = str(database)
    manifest_path = checks_dir / "aussef_build_manifest.json"
    manifest_path.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "database": str(database), "manifest": str(manifest_path)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
