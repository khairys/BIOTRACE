"""R-CUR-01..12 [MVP]: local imports produce new, immutable reference versions."""

import hashlib
import json
from pathlib import Path
from statistics import median

from pydantic import ValidationError

from biotrace_core.config import RulesConfig
from biotrace_core.io.loaders import read_fasta, read_table, write_fasta, write_table
from biotrace_core.models import ReferenceSequence
from biotrace_core.reference.store import ReferenceIndex, coverage
from biotrace_core.reference.trim import trim_mifish


def write_reference(
    path: Path,
    version: str,
    module: str,
    marker: str,
    tables: dict[str, list[dict]],
    sequences: dict[str, str],
    simulated: bool = False,
    notes: str = "",
    created: str = "2026-10-24",
) -> None:
    """R-CUR-11: exclusive directory; never replaces an existing version."""
    path.mkdir(parents=True, exist_ok=False)
    suffix = "_SIMULASI" if simulated else ""
    for name, rows in sorted(tables.items()):
        fields = list(rows[0]) if rows else ["seq_id"] if name == "sequences" else ["source_id"]
        write_table(path / f"{name}{suffix}.csv", rows, fields)
    write_fasta(path / f"sequences{suffix}.fasta", sequences)
    (path / f"CHANGELOG{suffix}.md").write_text(f"# {version}\n\n{notes}\n", encoding="utf-8")
    manifest = {
        "reference_version": version,
        "module": module,
        "marker": marker,
        "created": created,
        "contains_simulated": simulated,
        "files": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.iterdir())
            if p.is_file()
        },
        "counts": {
            "sequences_accepted": sum(
                r.get("curation_status") == "accepted" for r in tables["sequences"]
            ),
            "species_with_reference": len(
                {
                    r["species_valid"]
                    for r in tables["sequences"]
                    if r.get("curation_status") == "accepted"
                }
            ),
            "waterbodies": len(tables["waterbodies"]),
        },
        "changelog": f"CHANGELOG{suffix}.md",
        "table_files": {name: f"{name}{suffix}.csv" for name in tables},
    }
    (path / f"manifest{suffix}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def curate_records(
    rows: list[dict], fasta: dict[str, str], ref: ReferenceIndex, cfg: RulesConfig, marker: str
) -> tuple[list[ReferenceSequence], dict[str, str], list[dict]]:
    """R-CUR-01..10 pure curation; V4 is rejected before any duplicate/conflict logic."""
    candidates: list[tuple[ReferenceSequence, str]] = []
    report = []
    names = {name: name for name in ref.taxa}
    for name, taxon in ref.taxa.items():
        names.update({s: name for s in taxon.synonyms.split(";") if s})
    sources = {r["source_id"] for r in ref.tables["sources"]}
    for raw in sorted(rows, key=lambda r: r.get("seq_id", "")):
        try:
            record = ReferenceSequence.model_validate(raw)
        except ValidationError:
            report.append(
                {
                    "seq_id": raw.get("seq_id", ""),
                    "accession": raw.get("accession", ""),
                    "step": "R-CUR-01",
                    "result": "rejected",
                    "reason": "invalid_schema",
                }
            )
            continue
        sequence = fasta.get(record.seq_id, "")
        reason, step, status = "", "R-CUR-01", "accepted"
        extra_flags: list[str] = []
        if record.voucher_level == "V4":
            reason, step, status = "environmental_sequence", "R-CUR-02", "rejected"
        elif record.species_original not in names:
            reason, step, status = "unknown_name", "R-CUR-03", "flagged"
        elif (
            not sequence
            or record.source_id not in sources
            or not record.license
            or record.license == "?"
        ):
            reason, step, status = "missing_sequence_source_or_license", "R-CUR-10", "rejected"
        else:
            record = record.model_copy(update={"species_valid": names[record.species_original]})
            # D-033 (r0.4): same policy as R-NAME-01 selection; the species must still be
            # recorded in Indonesia, only the specimen may be foreign or of unknown origin.
            foreign_ok = cfg.evidence.get("foreign_specimen_policy") == "flag"
            outside = record.specimen_country != "ID"
            if ref.manifest["module"] == "ID" and (
                not ref.taxa[record.species_valid].in_indonesia or (outside and not foreign_ok)
            ):
                reason, step, status = "origin_not_verified_ID", "R-CUR-04", "rejected"
            elif record.marker != marker and record.marker not in {"mitogenome", "12S_other"}:
                reason, step, status = "marker_mismatch", "R-CUR-05", "rejected"
            elif marker == "12S_MiFish_U" and not record.region_trimmed:
                trimmed = trim_mifish(sequence, cfg)
                if trimmed is None:
                    reason, step, status = "no_mifish_region", "R-CUR-05", "flagged"
                else:
                    sequence = trimmed
                    record = record.model_copy(update={"marker": marker, "region_trimmed": True})
            if status == "accepted" and ref.manifest["module"] == "ID" and outside:
                extra_flags.append("specimen_outside_indonesia")
        record = record.model_copy(
            update={
                "curation_status": status,
                "flags": ";".join(f for f in [reason, *extra_flags] if f),
                "length": len(sequence) or record.length,
                "n_ambiguous": sum(c not in "ACGT" for c in sequence),
            }
        )
        if status == "accepted":
            candidates.append((record, sequence))
        else:
            report.append(
                {
                    "seq_id": record.seq_id,
                    "accession": record.accession,
                    "step": step,
                    "result": status,
                    "reason": reason,
                }
            )
    middle = median(len(s) for _, s in candidates) if candidates else 0
    accepted: list[tuple[ReferenceSequence, str]] = []
    for record, seq in candidates:
        reason = (
            "short"
            if len(seq) < float(cfg.curation["min_length_fraction"]) * middle
            else "ambiguous"
            if seq.count("N") / len(seq) > float(cfg.curation["max_n_fraction"])
            else ""
        )
        if reason:
            report.append(
                {
                    "seq_id": record.seq_id,
                    "accession": record.accession,
                    "step": "R-CUR-06",
                    "result": "rejected",
                    "reason": reason,
                }
            )
        else:
            accepted.append((record, seq))
    dedup: dict[tuple[str, str, str], tuple[ReferenceSequence, str]] = {}
    for record, seq in accepted:
        key = (record.species_valid, record.specimen_country, seq)
        if key in dedup:
            first, _ = dedup[key]
            accessions = sorted(
                set(first.accession.split(";") + record.accession.split(";")) - {""}
            )
            dedup[key] = (first.model_copy(update={"accession": ";".join(accessions)}), seq)
            report.append(
                {
                    "seq_id": record.seq_id,
                    "accession": record.accession,
                    "step": "R-CUR-07",
                    "result": "accepted",
                    "reason": f"merged_into={first.seq_id}",
                }
            )
        else:
            dedup[key] = record, seq
    conflicts: dict[str, set[str]] = {}
    for record, seq in dedup.values():
        conflicts.setdefault(seq, set()).add(record.species_valid)
    records, seqs = [], {}
    for record, seq in sorted(dedup.values(), key=lambda p: p[0].seq_id):
        conflict = len(conflicts[seq]) > 1
        if conflict:
            record = record.model_copy(
                update={
                    "flags": ";".join(sorted(set(record.flags.split(";")) - {""} | {"conflict"})),
                    "curation_status": "accepted"
                    if cfg.curation.get("conflict_policy") == "accepted_with_flag"
                    else "flagged",
                }
            )
        records.append(record)
        seqs[record.seq_id] = seq
        report.append(
            {
                "seq_id": record.seq_id,
                "accession": record.accession,
                "step": "R-CUR-08" if conflict else "R-CUR-01",
                "result": record.curation_status,
                "reason": "identical_cross_species" if conflict else "passed",
            }
        )
    return records, seqs, sorted(report, key=lambda r: (r["seq_id"], r["step"]))


def import_reference(
    fasta_path: Path,
    metadata_path: Path,
    source: ReferenceIndex,
    destination: Path,
    cfg: RulesConfig,
) -> dict:
    """R-CUR-11/12; create a new version, keep the previous version intact."""
    if destination.exists():
        raise ValueError("Versi tujuan sudah ada dan tidak boleh ditimpa.")
    records, seqs, report = curate_records(
        read_table(metadata_path),
        read_fasta(fasta_path, "ACGTNRYSWKMBDHV"),
        source,
        cfg,
        source.manifest["marker"],
    )
    tables = {key: list(value) for key, value in source.tables.items()}
    # Import is a new snapshot combining the previous version with incoming records.
    combined = {r.seq_id: r for r in source.sequences}
    if set(combined) & {r.seq_id for r in records}:
        raise ValueError("ID sekuens impor sudah ada pada versi sumber; gunakan ID baru.")
    combined.update({r.seq_id: r for r in records})
    merged_fasta = {**source.fasta, **seqs}
    # Detect new conflicts against the PREVIOUS snapshot as well as incoming rows.
    # Existing flagged/rejected records are never silently promoted.
    sequence_species: dict[str, set[str]] = {}
    for record in combined.values():
        if record.curation_status == "accepted":
            sequence_species.setdefault(merged_fasta[record.seq_id], set()).add(
                record.species_valid
            )
    for key, record in list(combined.items()):
        if (
            record.curation_status == "accepted"
            and len(sequence_species.get(merged_fasta[key], set())) > 1
        ):
            flags = ";".join(sorted(set(record.flags.split(";")) | {"conflict"} - {""}))
            combined[key] = record.model_copy(update={"flags": flags})
            report.append(
                {
                    "seq_id": key,
                    "accession": record.accession,
                    "step": "R-CUR-08",
                    "result": "accepted",
                    "reason": "conflict_with_snapshot",
                }
            )
    tables["sequences"] = [
        r.model_dump() for r in sorted(combined.values(), key=lambda r: r.seq_id)
    ]
    index = ReferenceIndex(
        source.manifest, source.taxa, list(combined.values()), merged_fasta, tables
    )
    mode = (
        "simulation"
        if source.manifest.get("contains_simulated")
        else "normal"
        if source.manifest["module"] == "ID"
        else "validation"
    )
    index = index.select(cfg, mode, source.manifest["marker"])
    tables["coverage"] = [r.model_dump() for r in coverage(index)]
    tables["curation_report"] = report
    write_reference(
        destination,
        destination.name,
        source.manifest["module"],
        source.manifest["marker"],
        tables,
        merged_fasta,
        bool(source.manifest.get("contains_simulated")),
        f"Impor dari {source.manifest['reference_version']}; aturan {cfg.rules_version}.",
    )
    return {"reference_version": destination.name, "imported": len(records), "report": report}
