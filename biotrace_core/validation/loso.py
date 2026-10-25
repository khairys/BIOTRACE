"""R-VAL-02 [MVP]: actual leave-one-species-out using isolated local BLAST DBs."""

import json
import tempfile
import time
from pathlib import Path

from biotrace_core import __version__
from biotrace_core.assessment import assess
from biotrace_core.audit import fingerprint, sha256
from biotrace_core.config import DEFAULT_RULES, load_reasons, load_rules
from biotrace_core.naming.blast import blast_version, match_sequences
from biotrace_core.preprocess import Signal
from biotrace_core.reference.store import ReferenceIndex, load_reference, manifest_path
from biotrace_core.validation.baseline import baseline_name


def contains_truth(
    rank: str, reported: str, complex_id: str, truth: str, ref: ReferenceIndex
) -> bool:
    if rank == "unknown":
        return True
    if rank == "complex":
        return any(
            r["complex_id"] == complex_id and r["member_species"] == truth
            for r in ref.tables["complexes"]
        )
    return reported == (truth if rank == "species" else getattr(ref.taxa[truth], rank, None))


def run_loso(
    reference_dir: Path,
    output: Path,
    rules_path: Path = DEFAULT_RULES,
    max_species: int | None = None,
) -> dict:
    """R-VAL-02: remove ALL records of X before each database build; preserve checklist X."""
    cfg, reasons = load_rules(rules_path), load_reasons()
    raw = load_reference(
        reference_dir, "simulation" if "demo" in reference_dir.parts else "validation"
    )
    mode = "simulation" if raw.manifest.get("contains_simulated") else "validation"
    ref = raw.select(cfg, mode, raw.manifest["marker"])
    species = sorted(ref.available_species)
    if max_species is not None:
        species = species[:max_species]
    if not species or blast_version() == "unavailable":
        raise ValueError("LOSO memerlukan referensi layak dan BLAST+.")
    counts = {
        "n": 0,
        "wrong_safe": 0,
        "correct_abstention": 0,
        "wrong_any": 0,
        "baseline_wrong": 0,
        "complete_n": 0,
        "correct_species": 0,
        "unnecessary_lower": 0,
    }
    if output.exists():
        raise ValueError("Hasil LOSO sudah ada; pilih nama output baru.")
    identity = {
        "reference_manifest_hash": sha256(manifest_path(reference_dir).read_bytes()),
        "rules_hash": sha256(rules_path.read_bytes()),
        "engine_version": __version__,
        "blast_version": blast_version(),
        "species": species,
    }
    checkpoint = output.with_suffix(".checkpoint")
    completed: list[str] = []
    previous_duration = 0.0
    if checkpoint.exists():
        state = json.loads(checkpoint.read_text(encoding="utf-8"))
        digest = state.pop("payload_hash", "")
        if fingerprint(state) != digest or state.get("identity") != identity:
            raise ValueError("Checkpoint LOSO berubah atau versinya berbeda; pilih output baru.")
        completed = state["completed_species"]
        saved_counts = state["counts"]
        if (
            completed != species[: len(completed)]
            or saved_counts.keys() != counts.keys()
            or any(not isinstance(v, int) or v < 0 for v in saved_counts.values())
        ):
            raise ValueError("Isi checkpoint LOSO tidak sah.")
        counts = saved_counts
        previous_duration = float(state.get("duration_seconds", 0))
        print(f"Melanjutkan LOSO setelah {len(completed)}/{len(species)} spesies.", flush=True)
    started = time.perf_counter()
    for index, name in enumerate(species):
        if index < len(completed):
            continue
        queries = {r.seq_id: ref.fasta[r.seq_id] for r in ref.eligible if r.species_valid == name}
        remaining = [r for r in ref.eligible if r.species_valid != name]
        hidden = ReferenceIndex(
            ref.manifest, ref.taxa, ref.sequences, ref.fasta, ref.tables, remaining
        )
        with tempfile.TemporaryDirectory(prefix="biotrace-loso-") as temp:
            hits, _ = match_sequences(queries, hidden, cfg, Path(temp) / "hidden")
            for asv in sorted(queries):
                # Methodological L4 maximum per 06 §3.1; not observed lab read counts.
                waters = sorted(
                    r["waterbody_id"] for r in ref.tables["checklist"] if r["species_valid"] == name
                )
                water = waters[0] if waters else ref.tables["waterbodies"][0]["waterbody_id"]
                signal = Signal(asv, "VALIDATION", water, 3, 3, cfg.scoring.min_total_reads, False)
                claim = assess(signal, hits.get(asv, []), hidden, cfg, reasons, validation=True)
                correct = contains_truth(
                    claim.reported_rank, claim.reported_name, claim.complex_id, name, ref
                )
                counts["n"] += 1
                counts["wrong_safe"] += int(not correct and claim.decision == "safe")
                counts["wrong_any"] += int(not correct)
                counts["correct_abstention"] += int(correct and claim.reported_rank != "species")
                baseline = baseline_name(hits.get(asv, []), cfg.validation["baseline_species_pct"])
                counts["baseline_wrong"] += int(baseline is not None and baseline != name)
            # Leave-one-sequence-out for M4/M5 only where another reference of X exists.
            if len(queries) > 1:
                full_hits, _ = match_sequences(queries, ref, cfg, Path(temp) / "complete")
                for asv in sorted(queries):
                    without_self = [h for h in full_hits.get(asv, []) if h.seq_id != asv]
                    claim = assess(
                        Signal(asv, "VALIDATION", water, 3, 3, cfg.scoring.min_total_reads, False),
                        without_self,
                        ref,
                        cfg,
                        reasons,
                        validation=True,
                    )
                    counts["complete_n"] += 1
                    counts["correct_species"] += int(
                        claim.reported_rank == "species" and claim.reported_name == name
                    )
                    counts["unnecessary_lower"] += int(
                        claim.reported_rank != "species"
                        and contains_truth(
                            claim.reported_rank, claim.reported_name, claim.complex_id, name, ref
                        )
                    )
        # Only complete species are checkpointed; partial work never becomes published metrics.
        state = {
            "identity": identity,
            "completed_species": species[: index + 1],
            "counts": counts,
            "duration_seconds": previous_duration + time.perf_counter() - started,
        }
        state["payload_hash"] = fingerprint(state)
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        temporary = checkpoint.with_suffix(".checkpoint.tmp")
        temporary.write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(checkpoint)
        if index % 20 == 0 or index == len(species) - 1:
            print(f"LOSO {index + 1}/{len(species)} spesies; {counts['n']} query", flush=True)
    n, m = counts["n"], counts["complete_n"]
    result = {
        "dataset": ref.manifest["module"],
        "reference_version": ref.manifest["reference_version"],
        "rules_version": cfg.rules_version,
        "marker": ref.manifest["marker"],
        "n_species": len(species),
        "n_queries": n,
        "is_simulated": bool(ref.manifest.get("contains_simulated")),
        "partial": max_species is not None and len(species) < len(ref.available_species),
        "metrics": {
            "M1": counts["wrong_safe"] / n,
            "M2": counts["correct_abstention"] / n,
            "M3": counts["wrong_any"] / n,
            "M4": counts["correct_species"] / m if m else None,
            "M5": counts["unnecessary_lower"] / m if m else None,
        },
        "baseline_blast97": {
            "M1": counts["baseline_wrong"] / n,
            "M3": counts["baseline_wrong"] / n,
        },
        "counts": counts,
        "reference_manifest_hash": sha256(manifest_path(reference_dir).read_bytes()),
        "rules_hash": sha256(rules_path.read_bytes()),
        "blast_version": blast_version(),
        "duration_seconds": round(previous_duration + time.perf_counter() - started, 3),
        "notes": [
            "L4 diset maksimum untuk mengisolasi logika penamaan; bukan hasil sampel lapangan.",
            "Parameter belum dikalibrasi untuk marker ini; hasil tidak membuktikan akurasi MiFish Indonesia.",
            "M4/M5 hanya query spesies dengan lebih dari satu sekuens; bukan komplemen matematis.",
            "LOSO menghapus semua referensi X sebelum BLAST; checklist tetap memuat X.",
            "Checkpoint hanya menyimpan spesies selesai. Durasi kumulatif segmen berhasil; jeda/interupsi tidak dihitung sebagai bukti kinerja.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
    checkpoint.unlink(missing_ok=True)
    return result
