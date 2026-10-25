"""V-01..V-10 [MVP]; no guessing of missing biological metadata."""

from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from biotrace_core.io.columns import (
    map_table,
    parse_count,
    prepare_metadata,
    prepare_taxonomy,
    table_marker,
)
from biotrace_core.io.loaders import read_fasta, read_table
from biotrace_core.models import (
    LabTaxonomy,
    Mode,
    ReadRow,
    Sample,
    ValidationIssue,
    ValidationReport,
)

ALLOWED_EXTENSIONS = {".csv", ".tsv", ".fa", ".fasta", ".fna"}
MAX_UPLOAD_BYTES = 200 * 1024 * 1024
LABELS = {
    "reads": "Tabel bacaan",
    "metadata": "Metadata sampel",
    "taxonomy": "Taksonomi lab",
    "site_context": "Konteks lokasi",
}
REQUIRED = {
    "reads": ("asv_id", "sample_id", "reads"),
    "metadata": ("sample_id",),
    "taxonomy": ("asv_id", "taxon", "pct_identity"),
    "site_context": ("site_id", "description"),
}
RowModel = TypeVar("RowModel", bound=BaseModel)


class InputError(ValueError):
    def __init__(self, report: ValidationReport):
        self.report = report
        super().__init__("; ".join(i.message for i in report.issues if i.level == "error"))


@dataclass
class InputData:
    reads: list[ReadRow] = field(default_factory=list)
    samples: list[Sample] = field(default_factory=list)
    fasta: dict[str, str] = field(default_factory=dict)
    taxonomy: dict[str, LabTaxonomy] = field(default_factory=dict)
    site_context: dict[str, list[str]] = field(default_factory=dict)
    # D-038: ASVs the lab table explicitly reports without a match; assessed as unknown.
    no_hit: set[str] = field(default_factory=set)
    report: ValidationReport = field(default_factory=ValidationReport)
    is_simulated: bool = False


def issue(
    report: ValidationReport, code: str, message: str, level: str = "error", field: str = ""
) -> None:
    report.issues.append(ValidationIssue(code=code, level=level, message=message, field=field))


def safe_identifier(value: str) -> bool:
    return bool(value) and len(value) <= 128 and not any(c in value for c in "\n\r\t\x00")


def validate_rows(model: type[RowModel], rows: list[dict], key: str, role: str) -> list[RowModel]:
    """Row-level pydantic errors as short messages naming the row and column."""
    out, problems = [], []
    for row in rows:
        try:
            out.append(model.model_validate(row))
        except ValidationError as exc:
            problems.extend(
                f"{row.get(key) or '?'} kolom {'.'.join(str(p) for p in e['loc'])}: {e['msg']}"
                for e in exc.errors()
            )
    if problems:
        more = f" (+{len(problems) - 5} lainnya)" if len(problems) > 5 else ""
        raise ValueError(f"{LABELS[role]}: {'; '.join(problems[:5])}{more}")
    return out


def load_inputs(
    reads_path: Path,
    metadata_path: Path,
    fasta_path: Path | None,
    taxonomy_path: Path | None,
    site_context_path: Path | None,
    waterbodies: Collection[str] | Mapping[str, str],
    mode: Mode,
    defaults: Mapping[str, str] | None = None,
) -> InputData:
    """V-01..10, R-PRE-01 and R-PRE-05. Input errors return structured evidence.

    D-038: columns are recognised by name or content; `defaults` (waterbody_id, marker) fill
    only blank metadata cells and come from the user, never from guessing.
    """
    data = InputData()
    names = (
        dict(waterbodies) if isinstance(waterbodies, Mapping) else dict.fromkeys(waterbodies, "")
    )
    defaults = {key: value for key, value in (defaults or {}).items() if value}
    paths = {
        "reads": reads_path,
        "metadata": metadata_path,
        "fasta": fasta_path,
        "taxonomy": taxonomy_path,
        "site_context": site_context_path,
    }
    for role, path in paths.items():
        if path and (not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS):
            issue(
                data.report,
                "V-10",
                "File tidak ditemukan atau ekstensi tidak diizinkan.",
                field=role,
            )
        elif path and path.stat().st_size > MAX_UPLOAD_BYTES:
            issue(data.report, "V-10", "Ukuran file melebihi 200 MB.", field=role)
    if not fasta_path and not taxonomy_path:
        issue(data.report, "V-08", "Sertakan FASTA atau tabel taksonomi lab.")
    if not data.report.valid:
        raise InputError(data.report)
    tables: dict[str, list[dict[str, str]]] = {}
    for role in ("reads", "metadata", "taxonomy", "site_context"):
        path = paths[role]
        if path:
            try:
                tables[role] = read_table(path)
                if not tables[role]:
                    raise ValueError("Tabel tidak boleh kosong.")
            except (ValueError, UnicodeError) as exc:
                issue(data.report, "V-01", str(exc), field=role)
    if not data.report.valid:
        raise InputError(data.report)
    mapped: dict[str, list[dict[str, str]]] = {}
    notes: dict[str, list[str]] = {}
    mapped["metadata"], mapping = map_table(tables["metadata"], "metadata")
    notes["metadata"] = mapping.changes()
    sample_set = {row.get("sample_id", "") for row in mapped["metadata"]}
    for role in ("reads", "taxonomy", "site_context"):
        if role in tables:
            mapped[role], mapping = map_table(tables[role], role, sample_set)
            notes[role] = mapping.changes()
    for role, rows in mapped.items():
        missing = [c for c in REQUIRED[role] if rows and c not in rows[0]]
        if missing:
            issue(
                data.report,
                "V-01",
                f"{LABELS[role]}: kolom wajib tidak dikenali: {', '.join(missing)}. "
                f"Kolom di file: {', '.join(tables[role][0])}.",
                field=role,
            )
    if not data.report.valid:
        raise InputError(data.report)
    if "marker" not in defaults and (marker := table_marker(tables.get("taxonomy", []))):
        defaults["marker"] = marker
    mapped["metadata"], extra = prepare_metadata(mapped["metadata"], names, defaults)
    notes["metadata"] += extra
    if "taxonomy" in mapped:
        mapped["taxonomy"], data.no_hit, extra = prepare_taxonomy(mapped["taxonomy"])
        notes["taxonomy"] += extra
    for role, messages in notes.items():
        if messages:
            issue(data.report, "V-COL", f"{LABELS[role]}: {'; '.join(messages)}.", "warning", role)
    blank_waterbody = sorted(
        r["sample_id"]
        for r in mapped["metadata"]
        if r["sample_type"] == "sampel" and not r["waterbody_id"]
    )
    if blank_waterbody:
        issue(
            data.report,
            "V-03",
            f"Perairan kosong pada {len(blank_waterbody)} sampel lapangan "
            f"(mis. {', '.join(blank_waterbody[:3])}). Pilih perairan di formulir unggah atau "
            f"isi kolom waterbody_id dengan salah satu: {', '.join(sorted(names))}.",
            field="waterbody_id",
        )
    if any(not r["marker"] for r in mapped["metadata"]):
        issue(
            data.report,
            "V-09",
            "Marker kosong di metadata. Pilih marker di formulir unggah atau isi kolom marker "
            "(mis. 12S_MiFish_U).",
            field="marker",
        )
    if not data.report.valid:
        raise InputError(data.report)
    try:
        data.samples = validate_rows(
            Sample,
            [{**row, "replicate": row.get("replicate") or None} for row in mapped["metadata"]],
            "sample_id",
            "metadata",
        )
        reads_rows = []
        for row in mapped["reads"]:
            number = parse_count(row["reads"])
            if number is None:
                raise ValueError(
                    f"Tabel bacaan: bacaan wajib integer tidak negatif ({row['asv_id']}, "
                    f"{row['sample_id']}: '{row['reads']}')."
                )
            reads_rows.append({**row, "reads": number})
        data.reads = validate_rows(ReadRow, reads_rows, "asv_id", "reads")
        for row in mapped.get("taxonomy", []):
            lab = validate_rows(
                LabTaxonomy,
                [{**row, "runner_up_pct_identity": row.get("runner_up_pct_identity") or None}],
                "asv_id",
                "taxonomy",
            )[0]
            if lab.asv_id in data.taxonomy:
                raise ValueError("ASV duplikat pada tabel taksonomi.")
            if bool(lab.runner_up_taxon) != (lab.runner_up_pct_identity is not None):
                raise ValueError("Nama dan identitas runner-up harus diisi berpasangan.")
            if (
                lab.runner_up_pct_identity is not None
                and lab.runner_up_pct_identity > lab.pct_identity
            ):
                raise ValueError("Identitas runner-up tidak boleh melebihi kecocokan terbaik.")
            data.taxonomy[lab.asv_id] = lab
        if fasta_path:
            data.fasta = read_fasta(fasta_path)
        for row in mapped.get("site_context", []):
            data.site_context.setdefault(row["site_id"], []).append(row["description"])
    except (ValidationError, ValueError, KeyError) as exc:
        issue(data.report, "V-01", f"Isi/kolom tidak valid: {exc}")
        raise InputError(data.report) from exc
    sample_ids = [sample.sample_id for sample in data.samples]
    if len(sample_ids) != len(set(sample_ids)):
        issue(data.report, "V-01", "sample_id metadata wajib unik.")
    read_keys = [(r.asv_id, r.sample_id) for r in data.reads]
    if len(read_keys) != len(set(read_keys)):
        issue(data.report, "V-01", "Pasangan ASV dan sampel pada bacaan wajib unik.")
    identifiers = sample_ids + [r.asv_id for r in data.reads] + [s.site_id for s in data.samples]
    if not all(safe_identifier(v) for v in identifiers):
        issue(data.report, "V-01", "ID kosong, terlalu panjang, atau memiliki karakter kontrol.")
    if any("__" in s.site_id for s in data.samples):
        issue(data.report, "V-01", "site_id tidak boleh memuat pemisah klaim __.")
    missing_samples = sorted({r.sample_id for r in data.reads} - set(sample_ids))
    if missing_samples:
        issue(
            data.report,
            "V-02",
            f"{len(missing_samples)} sample_id tidak ada di metadata; baris diabaikan.",
            "warning",
        )
        data.reads = [r for r in data.reads if r.sample_id in set(sample_ids)]
    sites: dict[str, set[str]] = {}
    replicate_keys = []
    negative_batches = {
        s.extraction_batch for s in data.samples if s.sample_type.startswith("kontrol_negatif")
    }
    no_coordinates: list[str] = []
    for sample in data.samples:
        if sample.sample_type == "sampel":
            if sample.waterbody_id not in waterbodies:
                issue(data.report, "V-03", f"Perairan tidak dikenal: {sample.waterbody_id}.")
            sites.setdefault(sample.site_id, set()).add(sample.waterbody_id)
            if sample.replicate is None:
                issue(data.report, "V-01", "Replikat wajib untuk sampel lapangan.")
            replicate_keys.append((sample.site_id, sample.replicate))
        if sample.latitude is None or sample.longitude is None:
            if sample.sample_type == "sampel":
                no_coordinates.append(sample.sample_id)
        elif not (-90 <= sample.latitude <= 90 and -180 <= sample.longitude <= 180):
            issue(
                data.report,
                "V-06",
                f"Koordinat di luar rentang pada {sample.sample_id}.",
                "warning",
            )
    if no_coordinates:
        issue(
            data.report,
            "V-06",
            f"Koordinat tidak tersedia pada {len(no_coordinates)} sampel lapangan "
            f"(mis. {', '.join(sorted(no_coordinates)[:3])}); tidak ditebak.",
            "warning",
        )
    if any(len(values) > 1 for values in sites.values()):
        issue(data.report, "V-04", "Satu site_id memetakan lebih dari satu perairan.")
    if len(replicate_keys) != len(set(replicate_keys)):
        issue(data.report, "V-01", "Nomor replikat harus unik per lokasi.")
    for batch in sorted(
        {s.extraction_batch for s in data.samples if s.sample_type == "sampel"} - negative_batches
    ):
        issue(data.report, "V-05", f"Batch {batch} tanpa kontrol negatif.", "warning")
    if len({s.marker for s in data.samples}) != 1:
        issue(data.report, "V-09", "Satu run hanya menerima satu marker.")
    if mode != "validation" and any(
        s.marker not in {"12S_MiFish_U", "16S", "COI"} for s in data.samples
    ):
        issue(data.report, "V-09", "Marker ini hanya tersedia dalam mode validasi.")
    asvs = {r.asv_id for r in data.reads}
    if fasta_path and asvs != set(data.fasta):
        issue(
            data.report,
            "V-07",
            "ID ASV pada FASTA dan bacaan berbeda; ASV tanpa sekuens tidak dikenal.",
            "warning",
        )
    if not fasta_path and asvs - data.taxonomy.keys() - data.no_hit:
        issue(data.report, "V-01", "Taksonomi tidak mencakup seluruh ASV pada bacaan.")
    flags = (
        [r.is_simulated for r in data.reads]
        + [s.is_simulated for s in data.samples]
        + [t.is_simulated for t in data.taxonomy.values()]
    )
    data.is_simulated = any(flags)
    if data.is_simulated and not all(flags):
        issue(data.report, "V-SIM", "Semua baris run simulasi wajib is_simulated=true.")
    if data.is_simulated and mode != "simulation":
        issue(data.report, "V-SIM", "Data SIMULASI wajib memakai mode simulasi terpisah.")
    if mode == "simulation" and not (flags and all(flags)):
        issue(data.report, "V-SIM", "Mode simulasi hanya menerima baris berlabel SIMULASI.")
    if data.is_simulated and any(path and "SIMULASI" not in path.name for path in paths.values()):
        issue(data.report, "V-SIM", "Nama setiap berkas simulasi wajib memuat SIMULASI.")
    if not data.report.valid:
        raise InputError(data.report)
    data.reads = sorted(data.reads, key=lambda r: (r.asv_id, r.sample_id))
    data.samples.sort(key=lambda s: s.sample_id)
    return data
