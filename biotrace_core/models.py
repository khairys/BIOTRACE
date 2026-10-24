"""Public contracts for F1–F42 [MVP], generated into TypeScript from these models."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Decision = Literal["safe", "with_note", "must_verify", "do_not_use"]
Rank = Literal["species", "complex", "genus", "family", "order", "unknown", "hybrid_alias"]
Mode = Literal["normal", "validation", "simulation"]
Marker = Literal["12S_MiFish_U", "16S", "COI", "12S_Teleo1_V5", "12S_other", "mitogenome"]
Voucher = Literal["V1", "V2", "V3", "V4"]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ValidationIssue(Model):
    code: str
    level: Literal["error", "warning"]
    message: str
    field: str = ""


class ValidationReport(Model):
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.level == "error" for i in self.issues)


class ReadRow(Model):
    asv_id: str = Field(min_length=1)
    sample_id: str = Field(min_length=1)
    reads: int = Field(ge=0, strict=True)
    is_simulated: bool = False


class Sample(Model):
    sample_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    waterbody_id: str = Field(min_length=1)
    latitude: float
    longitude: float
    collection_date: date
    sample_type: Literal[
        "sampel",
        "kontrol_negatif_lapangan",
        "kontrol_negatif_ekstraksi",
        "kontrol_negatif_pcr",
        "kontrol_positif",
    ]
    replicate: int | None = Field(default=None, ge=1)
    extraction_batch: str = Field(min_length=1)
    marker: Marker
    pcr_batch: str = ""
    notes: str = ""
    is_simulated: bool = False


class LabTaxonomy(Model):
    asv_id: str
    taxon: str = Field(min_length=1)
    rank: Literal["species", "genus", "family", "order"]
    pct_identity: float = Field(ge=0, le=100)
    runner_up_taxon: str = ""
    runner_up_pct_identity: float | None = Field(default=None, ge=0, le=100)
    reference_db: str = ""
    is_simulated: bool = False


class Taxon(Model):
    species_valid: str
    genus: str
    family: str
    order: str
    authority: str = ""
    synonyms: str = ""
    in_indonesia: bool = False
    cof_checked_date: str = ""
    source_id: str
    is_simulated: bool = False


class ReferenceSequence(Model):
    seq_id: str
    accession: str = ""
    source_db: Literal[
        "genbank", "bold", "mitofish", "paper_supplement", "partner_lab", "simulated"
    ]
    source_id: str
    species_original: str
    species_valid: str
    marker: Marker
    region_trimmed: bool
    length: int = Field(gt=0)
    n_ambiguous: int = Field(ge=0)
    voucher_level: Voucher
    voucher_catalog: str = ""
    voucher_institution: str = ""
    specimen_country: str = ""
    specimen_locality: str = ""
    curation_status: Literal["accepted", "flagged", "rejected"]
    flags: str = ""
    license: str
    date_added: str
    curator: str
    is_simulated: bool = False


class SpeciesHit(Model):
    species: str
    pct: float = Field(ge=0, le=100)
    bitscore: float = 0
    seq_id: str = ""
    query_coverage: float = Field(default=1, ge=0, le=1)


class NamingResult(Model):
    reported_name: str = "tidak dikenal"
    reported_rank: Rank = "unknown"
    best_match: str = ""
    best_pct: float | None = None
    gap_pct: float | None = None
    candidates: list[SpeciesHit] = Field(default_factory=list)
    complex_id: str = ""
    alias_key: str = ""
    causes: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class Claim(Model):
    run_id: str = ""
    claim_id: str
    site_id: str
    waterbody_id: str
    asv_id: str
    taxon_lab: str = ""
    best_match: str = ""
    best_pct: float | None = None
    gap_pct: float | None = None
    candidates: list[SpeciesHit] = Field(default_factory=list)
    reported_name: str
    reported_rank: Rank
    complex_id: str = ""
    l1: int
    l2: int
    l4: int
    total: int
    grade: Literal["A", "B", "C", "D"]
    cap_reason: str = ""
    labels: list[str] = Field(default_factory=list)
    p_missing: float | None = None
    causes: list[str] = Field(default_factory=list)
    decision: Decision
    decision_rule: str
    follow_up: str
    reasons_id: list[str]
    reasons_en: list[str]
    voucher_support: Voucher | None = None
    supporting_seq_ids: list[str] = Field(default_factory=list)
    supporting_accessions: list[str] = Field(default_factory=list)
    n_rep: int
    n_pos: int
    total_reads: int
    in_negative_control: bool
    assessed_with_lab_database: bool
    origin_status: str = ""
    origin_pathway: str = ""
    origin_other_sources: str = ""
    is_simulated: bool
    warnings: list[str] = Field(default_factory=list)
    rule_ids: list[str] = Field(default_factory=list)
    interpretation_limit: str = "Deteksi DNA bukan bukti pasti ikan hidup di lokasi."


class CoverageRow(Model):
    waterbody_id: str
    genus: str
    n: int
    r: int
    p_missing: float
    missing_species: list[str] = Field(default_factory=list)
    is_simulated: bool = False


class BarcodePriorityRow(Model):
    type: Literal["species", "asv"]
    name_or_asv: str
    waterbody_id: str
    score: int = 0
    reasons: list[str] = Field(default_factory=list)
    sites: list[str] = Field(default_factory=list)
    total_reads: int = 0
    nearest_hint: str = ""
    is_simulated: bool = False


class DecisionCount(Model):
    decision: Decision
    label: str
    claims: int
    taxa: int
    follow_up: str


class RunSummary(Model):
    total_claims: int
    total_taxa: int
    safe_percent: float
    must_verify_count: int
    reference_coverage: float | None
    decisions: list[DecisionCount]
    sites: list[str]
    waterbodies: list[str]
    is_simulated: bool
    tag_jump_removed: int
    duration_seconds: float = 0
    warnings: list[str] = Field(default_factory=list)
    precomputed: bool = False
    reference_sequences: int = 0
    reference_species: int = 0
    reference_by_voucher: dict[str, int] = Field(default_factory=dict)


class RunManifest(Model):
    run_fingerprint: str
    report_fingerprint: str
    input_hashes: dict[str, str]
    reference_version: str
    reference_manifest_hash: str
    rules_version: str
    rules_hash: str
    reasons_hash: str
    engine_version: str
    blast_version: str
    parameters: dict
    execution: dict
    mode: Mode
    is_simulated: bool
    started_at: str
    finished_at: str
    result_payload_hash: str = ""
    output_hashes: dict[str, str] = Field(default_factory=dict)


class RunResult(Model):
    run_id: str
    claims: list[Claim]
    summary: RunSummary
    coverage: list[CoverageRow]
    barcode_priority: list[BarcodePriorityRow]
    manifest: RunManifest
    validation: ValidationReport


class RunCreated(Model):
    run_id: str
    status: Literal["completed"] = "completed"
    validation: ValidationReport
    is_simulated: bool
    precomputed: bool = False
