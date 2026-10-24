"""Typed non-run API responses [MVP], exported with the same pydantic schemas."""

from biotrace_core.config import RulesConfig
from biotrace_core.models import CoverageRow, Model, ValidationReport


class HealthResponse(Model):
    engine_version: str
    rules_version: str
    rules_status: str
    reference_version: str | None
    reference_ready: bool
    blast_available: bool
    demo_available: bool


class ReferenceStats(Model):
    reference_version: str
    module: str
    marker: str
    contains_simulated: bool
    sequence_count: int
    eligible_sequences: int
    species_with_reference: int
    by_voucher: dict[str, int]
    by_curation: dict[str, int]
    coverage: list[CoverageRow]
    sources: list[dict[str, str]]


class Citation(Model):
    label: str
    url: str


class MethodsResponse(Model):
    rules: RulesConfig
    citations: list[Citation]


class ValidationExperiment(Model):
    dataset: str
    reference_version: str
    rules_version: str
    marker: str
    n_species: int
    n_queries: int
    is_simulated: bool
    partial: bool
    metrics: dict[str, float | None]
    baseline_blast97: dict[str, float | None]
    counts: dict[str, int]
    reference_manifest_hash: str
    rules_hash: str
    blast_version: str
    duration_seconds: float
    notes: list[str]


class ValidationResults(Model):
    available: bool
    results: list[ValidationExperiment]


class DatasetTable(Model):
    rows: int
    columns: list[str]
    delimiter: str


class SequenceFile(Model):
    name: str
    bytes: int
    crc32: str


class ArchivedDataset(Model):
    dataset: str
    module: str
    version: str
    source: str
    license: str
    imported_at: str
    archive_path: str
    archive_sha256: str
    raw_files_sha256: dict[str, str]
    tables: dict[str, DatasetTable]
    sequence_files: list[SequenceFile]
    usage: str
    asv_pipeline_ready: bool
    notes: list[str]


class DatasetsResponse(Model):
    lake_st_pierre: ArchivedDataset | None
    guyana_available: bool


class APIError(Model):
    code: str
    message: str
    validation: ValidationReport | None = None


class ErrorResponse(Model):
    error: APIError
