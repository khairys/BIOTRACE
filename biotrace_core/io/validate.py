"""V-01..V-10 [MVP]; no guessing of missing biological metadata."""

from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

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
    report: ValidationReport = field(default_factory=ValidationReport)
    is_simulated: bool = False


def issue(
    report: ValidationReport, code: str, message: str, level: str = "error", field: str = ""
) -> None:
    report.issues.append(ValidationIssue(code=code, level=level, message=message, field=field))


def safe_identifier(value: str) -> bool:
    return bool(value) and len(value) <= 128 and not any(c in value for c in "\n\r\t\x00")


def load_inputs(
    reads_path: Path,
    metadata_path: Path,
    fasta_path: Path | None,
    taxonomy_path: Path | None,
    site_context_path: Path | None,
    waterbodies: set[str],
    mode: Mode,
) -> InputData:
    """V-01..10, R-PRE-01 and R-PRE-05. Input errors return structured evidence."""
    data = InputData()
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
    try:
        data.samples = [
            Sample.model_validate({**row, "replicate": row.get("replicate") or None})
            for row in tables["metadata"]
        ]
        raw_reads = tables["reads"]
        long_rows = []
        for row in raw_reads:
            simulated = row.get("is_simulated", "false")
            if "reads" in row and "sample_id" in row:
                long_rows.append(row)
            else:
                for sample_id, reads in row.items():
                    if sample_id not in {"asv_id", "is_simulated"}:
                        long_rows.append(
                            {
                                "asv_id": row["asv_id"],
                                "sample_id": sample_id,
                                "reads": reads,
                                "is_simulated": simulated,
                            }
                        )
        for row in long_rows:
            number = row["reads"]
            if not number.isascii() or not number.isdigit():
                raise ValueError("Bacaan wajib integer tidak negatif.")
            data.reads.append(ReadRow.model_validate({**row, "reads": int(number)}))
        for row in tables.get("taxonomy", []):
            lab = LabTaxonomy.model_validate(
                {**row, "runner_up_pct_identity": row.get("runner_up_pct_identity") or None}
            )
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
        for row in tables.get("site_context", []):
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
    missing_dates = sum(
        s.collection_date is None for s in data.samples if s.sample_type == "sampel"
    )
    if missing_dates:
        issue(
            data.report,
            "V-06",
            f"Tanggal pengambilan tidak tersedia pada {missing_dates} sampel lapangan; tidak ditebak.",
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
    if not fasta_path and asvs - data.taxonomy.keys():
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
