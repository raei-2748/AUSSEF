"""Pandera schemas for the stable-key portion of the canonical model.

The schemas deliberately validate identifiers and lineage columns without
coercing the underlying data. Missing values therefore remain distinct from
zero, unavailable, and not-applicable values.
"""

from __future__ import annotations

import pandera.pandas as pa


def _matches(pattern: str) -> pa.Check:
    return pa.Check(
        lambda series: series.astype("string").str.fullmatch(pattern, na=False),
        error=f"values must match {pattern}",
    )


def _key(
    pattern: str,
    *,
    unique: bool = False,
    nullable: bool = False,
) -> pa.Column:
    return pa.Column(
        str,
        checks=_matches(pattern),
        nullable=nullable,
        unique=unique,
    )


_COUNCIL_ID = r"^council_[0-9a-f]{32}$"
_DISASTER_ID = r"^disaster_[0-9a-f]{32}$"
_PROJECT_ID = r"^project_[0-9a-f]{32}$"
_EVIDENCE_ID = r"^evidence_[0-9a-f]{32}$"
_EXPOSURE_ID = r"^exposure_[0-9a-f]{32}$"
_FACT_ID = r"^[a-z_]+[0-9a-f]{32}$"
_SOURCE_KEY = r"^(input_[0-9a-f]{64}|document_[0-9a-f]{32})$"


TABLE_SCHEMAS: dict[str, pa.DataFrameSchema] = {
    "councils": pa.DataFrameSchema(
        {
            "council_id": _key(_COUNCIL_ID, unique=True),
            "council_name": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
    "disasters": pa.DataFrameSchema(
        {
            "disaster_id": _key(_DISASTER_ID, unique=True),
            "event_name": pa.Column(str, nullable=True),
        },
        strict=False,
    ),
    "projects": pa.DataFrameSchema(
        {
            "project_id": _key(_PROJECT_ID, unique=True),
            "council_id": _key(_COUNCIL_ID),
            "source_key": _key(_SOURCE_KEY),
            "source_record_key": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
    "evidence_records": pa.DataFrameSchema(
        {
            # Evidence rows preserve source-native identifiers where those
            # identifiers are stronger than an analyst-generated hash.
            "evidence_id": pa.Column(str, nullable=False, unique=True),
            "council_id": _key(_COUNCIL_ID, nullable=True),
            "project_id": _key(_PROJECT_ID, nullable=True),
            "source_key": _key(_SOURCE_KEY),
            "source_record_key": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
    "exposure_observations": pa.DataFrameSchema(
        {
            "exposure_id": _key(_EXPOSURE_ID, unique=True),
            "council_id": _key(_COUNCIL_ID),
            "source_key": _key(_SOURCE_KEY),
            "source_record_key": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
    "fiscal_annual": pa.DataFrameSchema(
        {
            "fiscal_record_id": _key(_FACT_ID, unique=True),
            "council_id": _key(_COUNCIL_ID),
            "source_key": _key(_SOURCE_KEY),
            "source_record_key": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
    "project_evidence": pa.DataFrameSchema(
        {
            "project_evidence_key": _key(_FACT_ID, unique=True),
            "project_id": _key(_PROJECT_ID),
            "council_id": _key(_COUNCIL_ID),
            "evidence_id": pa.Column(str, nullable=True),
            "source_key": _key(_SOURCE_KEY),
            "source_record_key": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
    "sources": pa.DataFrameSchema(
        {
            "source_key": _key(_SOURCE_KEY, unique=True),
            "source_type": pa.Column(str, nullable=False),
        },
        strict=False,
    ),
}
