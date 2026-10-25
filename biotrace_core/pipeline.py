"""F1–F27 [MVP] local file orchestration around pure domain rules."""

import json
import os
import shutil
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from biotrace_core import __version__
from biotrace_core.assessment import assess
from biotrace_core.audit import fingerprint, read_run, report_fingerprint, sha256, verify_run
from biotrace_core.config import DEFAULT_RULES, blast_timeout, load_reasons, load_rules
from biotrace_core.decision import DECISIONS
from biotrace_core.gaps import barcode_priorities
from biotrace_core.io.validate import InputError, issue, load_inputs
from biotrace_core.models import (
    BarcodePriorityRow,
    Claim,
    CoverageRow,
    DataProvenance,
    DecisionCount,
    Mode,
    RunManifest,
    RunResult,
    RunSummary,
)
from biotrace_core.naming.blast import blast_version, match_sequences
from biotrace_core.preprocess import preprocess
from biotrace_core.reference.store import coverage, load_reference, manifest_path, reference_stats
from biotrace_core.report.csv_export import artifact_name, canonical_csv


def run_analysis(
    reads_path: Path,
    metadata_path: Path,
    fasta_path: Path | None,
    taxonomy_path: Path | None,
    site_context_path: Path | None,
    reference_dir: Path,
    rules_path: Path = DEFAULT_RULES,
    out_root: Path = Path("runs"),
    mode: Mode = "normal",
    threads: int = 4,
    provenance: DataProvenance | None = None,
) -> RunResult:
    """Load → validate → R-PRE/NAME/SCORE/CAUSE/DEC/ORIG/GAP/AUD → persist atomically."""
    started = datetime.now(UTC).isoformat()
    clock = time.perf_counter()
    cfg = load_rules(rules_path)
    ref = load_reference(reference_dir, mode)
    if mode == "normal" and not ref.taxa:
        raise ValueError(
            "Kamus Indonesia belum siap. Gunakan demo SIMULASI atau impor kamus lokal tervalidasi."
        )
    data = load_inputs(
        reads_path,
        metadata_path,
        fasta_path,
        taxonomy_path,
        site_context_path,
        {r["waterbody_id"] for r in ref.tables["waterbodies"]},
        mode,
    )
    marker = data.samples[0].marker
    ref = ref.select(cfg, mode, marker)
    if marker != ref.manifest["marker"]:
        issue(data.report, "V-09", "Marker input berbeda dari marker kamus aktif.")
        raise InputError(data.report)
    reasons = load_reasons()
    paths = {
        "reads": reads_path,
        "metadata": metadata_path,
        "fasta": fasta_path,
        "taxonomy": taxonomy_path,
        "site_context": site_context_path,
    }
    effective = {
        "rules": cfg.model_dump(mode="json"),
        "marker": marker,
        "uses_fasta": bool(fasta_path),
    }
    if provenance is not None:
        effective["data_provenance"] = provenance.model_dump(mode="json")
    # Original input bytes are preserved under canonical, role-based filenames.
    input_names = {
        role: artifact_name(
            role, "fasta" if role == "fasta" else path.suffix.lstrip("."), data.is_simulated
        )
        for role, path in paths.items()
        if path
    }
    input_hashes = {
        input_names[role]: sha256(path.read_bytes()) for role, path in paths.items() if path
    }
    version = blast_version() if fasta_path else "not_used_lab_taxonomy"
    identity = {
        "input_hashes": input_hashes,
        "reference_version": ref.manifest["reference_version"],
        "reference_manifest_hash": sha256(manifest_path(reference_dir).read_bytes()),
        "rules_version": cfg.rules_version,
        "rules_hash": sha256(rules_path.read_bytes()),
        "reasons_hash": sha256((DEFAULT_RULES.parent / "reasons_r0.1.yaml").read_bytes()),
        "engine_version": __version__,
        "blast_version": version,
        "parameters": effective,
        "mode": mode,
    }
    run_hash = fingerprint(identity)
    run_id = run_hash[:12]
    out_root.mkdir(parents=True, exist_ok=True)
    destination = out_root / run_id
    if destination.exists():
        if not verify_run(destination)["valid"]:
            raise ValueError(
                "Run tersimpan berubah; hasil tidak ditimpa. Pilih direktori output baru."
            )
        return read_run(destination)
    lock = out_root / f".{run_id}.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(descriptor)
    except FileExistsError as exc:
        raise ValueError(
            "Analisis input yang sama sedang berjalan; coba lagi setelah selesai."
        ) from exc
    try:
        with tempfile.TemporaryDirectory(prefix=f".{run_id}-", dir=out_root) as temp:
            folder = Path(temp)
            (folder / "input").mkdir()
            for role, path in paths.items():
                if path:
                    shutil.copyfile(path, folder / "input" / input_names[role])
            hits, raw_hits = (
                match_sequences(data.fasta, ref, cfg, folder / "blastdb", threads)
                if fasta_path
                else ({}, "")
            )
            signals, removed = preprocess(data.reads, data.samples, cfg)
            claims = [
                assess(
                    signal,
                    hits.get(signal.asv_id, []),
                    ref,
                    cfg,
                    reasons,
                    None if fasta_path else data.taxonomy[signal.asv_id],
                    data.site_context.get(signal.site_id, []),
                    mode == "validation",
                )
                for signal in signals
            ]
            # FASTA may be accompanied by lab names purely for comparison, not score inputs.
            if fasta_path:
                for claim in claims:
                    if claim.asv_id in data.taxonomy:
                        claim.taxon_lab = data.taxonomy[claim.asv_id].taxon
            for claim in claims:
                claim.run_id = run_id
            cov = [r for r in coverage(ref) if r.waterbody_id in {c.waterbody_id for c in claims}]
            priorities = barcode_priorities(claims, ref, cfg)
            counts = [
                DecisionCount(
                    decision=decision,
                    label=text[0],
                    claims=sum(c.decision == decision for c in claims),
                    taxa=len(
                        {
                            (c.reported_rank, c.reported_name)
                            for c in claims
                            if c.decision == decision
                        }
                    ),
                    follow_up=text[1],
                )
                for decision, text in DECISIONS.items()
            ]
            summary = RunSummary(
                total_claims=len(claims),
                total_taxa=len({(c.reported_rank, c.reported_name) for c in claims}),
                safe_percent=100 * sum(c.decision == "safe" for c in claims) / len(claims)
                if claims
                else 0,
                must_verify_count=sum(c.decision == "must_verify" for c in claims),
                reference_coverage=sum(r.r for r in cov) / sum(r.n for r in cov) if cov else None,
                decisions=counts,
                sites=sorted({c.site_id for c in claims}),
                waterbodies=sorted({c.waterbody_id for c in claims}),
                is_simulated=data.is_simulated,
                tag_jump_removed=removed,
                reference_sequences=len(ref.eligible),
                reference_species=len(ref.available_species),
                reference_by_voucher=reference_stats(ref)["by_voucher"],
                duration_seconds=round(time.perf_counter() - clock, 3),
                warnings=[i.message for i in data.report.issues if i.level == "warning"],
            )
            csv_data = canonical_csv(claims, sorted(Claim.model_fields))
            manifest = RunManifest(
                **identity,
                run_fingerprint=run_hash,
                report_fingerprint=report_fingerprint(csv_data, run_hash),
                execution={"blast_threads": threads, "blast_timeout_seconds": blast_timeout()},
                is_simulated=data.is_simulated,
                started_at=started,
                finished_at=datetime.now(UTC).isoformat(),
            )
            result = RunResult(
                run_id=run_id,
                claims=claims,
                summary=summary,
                coverage=cov,
                barcode_priority=priorities,
                manifest=manifest,
                validation=data.report,
            )

            def save_json(stem: str, value: dict) -> None:
                (folder / artifact_name(stem, "json", data.is_simulated)).write_text(
                    json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                )

            (folder / artifact_name("claims", "csv", data.is_simulated)).write_bytes(csv_data)
            for stem, rows, fields in [
                (
                    "coverage",
                    cov,
                    sorted(CoverageRow.model_fields),
                ),
                (
                    "barcode_priority",
                    priorities,
                    sorted(BarcodePriorityRow.model_fields),
                ),
            ]:
                (folder / artifact_name(stem, "csv", data.is_simulated)).write_bytes(
                    canonical_csv(rows, fields)
                )
            (folder / artifact_name("blast_hits", "tsv", data.is_simulated)).write_text(
                raw_hits, encoding="utf-8", newline="\n"
            )
            save_json("summary", summary.model_dump(mode="json"))
            save_json("validation_report", data.report.model_dump(mode="json"))
            from biotrace_core.report.pdf import render_report

            render_report(
                result,
                ref.tables["sources"],
                folder / artifact_name("report", "pdf", data.is_simulated),
            )
            manifest.result_payload_hash = fingerprint(
                result.model_dump(mode="json", exclude={"manifest"})
            )
            manifest.output_hashes = {
                p.name: sha256(p.read_bytes()) for p in sorted(folder.iterdir()) if p.is_file()
            }
            save_json("run_manifest", manifest.model_dump(mode="json"))
            save_json("run_result", result.model_dump(mode="json"))
            # Publish complete output atomically on the same volume.
            folder.rename(destination)
            return result
    finally:
        lock.unlink(missing_ok=True)
