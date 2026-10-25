"""D-038 [MVP]: reproducible real-demo build and offline evidence inventory."""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from biotrace_core import __version__
from biotrace_core.audit import read_run, sha256, verify_run
from biotrace_core.config import DEFAULT_REFERENCE, ROOT, load_rules
from biotrace_core.demo import REAL_DEMO, REAL_PRECOMPUTED_NAME, REAL_PROVENANCE, REAL_REF
from biotrace_core.pipeline import run_analysis
from biotrace_core.records import compare_runs
from biotrace_core.reference.store import load_reference


def precompute() -> Path:
    """Preserve old snapshots; publish only an actually computed, verified complete run."""
    target = ROOT / "precomputed" / REAL_PRECOMPUTED_NAME
    if target.exists():
        if not verify_run(target)["valid"]:
            raise ValueError("Pra-hitung tujuan sudah ada tetapi berubah; jangan ditimpa.")
        result = read_run(target)
        if result.manifest.engine_version != __version__:
            raise ValueError("Pra-hitung dibuat engine lain; gunakan nama rilis baru.")
        return target
    print(f"Analisis data asli lengkap dengan {REAL_REF.name} dimulai.", flush=True)
    result = run_analysis(
        REAL_DEMO / "reads.csv",
        REAL_DEMO / "metadata.csv",
        REAL_DEMO / "asv.fasta",
        REAL_DEMO / "taxonomy.csv",
        None,
        REAL_REF,
        out_root=ROOT / "output/jury-runs",
        provenance=REAL_PROVENANCE,
    )
    source = ROOT / "output/jury-runs" / result.run_id
    if not verify_run(source)["valid"]:
        raise ValueError("Run lengkap tidak lolos verifikasi.")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("blastdb"))
    if not verify_run(target)["valid"]:
        raise ValueError("Salinan pra-hitung tidak lolos verifikasi.")
    return target


def audit(destination: Path) -> dict:
    """Measure local files only; this inventory never certifies biological correctness."""
    cfg = load_rules()
    references = []
    for path in sorted((ROOT / "data/reference").iterdir()):
        if not path.is_dir():
            continue
        ref = load_reference(path).select(cfg, "normal", "12S_MiFish_U")
        endemic = {
            row["species_valid"]
            for row in ref.tables["checklist"]
            if row["origin_status"] == "endemik"
            and row["waterbody_id"] in {"MATANO", "MAHALONA", "TOWUTI", "MASAPI"}
        }
        references.append(
            {
                "version": path.name,
                "manifest_sha256": sha256((path / "manifest.json").read_bytes()),
                "integrity": True,
                "eligible_sequences": len(ref.eligible),
                "species_with_reference": len(ref.available_species),
                "indonesian_specimen_sequences": sum(
                    r.specimen_country == "ID" for r in ref.eligible
                ),
                "malili_endemic_species": len(endemic),
                "malili_endemic_with_reference": len(endemic & ref.available_species),
            }
        )
    snapshots = []
    for path in sorted((ROOT / "precomputed").iterdir()):
        if path.is_dir():
            snapshots.append({"folder": path.name, **verify_run(path)})
    new = read_run(ROOT / "precomputed" / REAL_PRECOMPUTED_NAME)
    old = read_run(ROOT / "precomputed/edna_asli_marwayana2022_r0.4_v0.4")
    comparison = compare_runs(old, new)
    harvest = []
    for path in sorted((ROOT / "raw/tropis").glob("**/manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        harvest.append(
            {
                "manifest": path.relative_to(ROOT).as_posix(),
                "manifest_sha256": sha256(path.read_bytes()),
                "finished": manifest.get("finished"),
                "summary": manifest.get("summary"),
                "files_listed": len(manifest.get("files", {})),
                "usage": "Bahan mentah/kurasi; bukan bukti semua rekaman masuk kamus rilis.",
            }
        )
    report = {
        "release": "jury-v0.5",
        "engine_version": __version__,
        "rules_version": cfg.rules_version,
        "default_reference": DEFAULT_REFERENCE.name,
        "scientific_status": cfg.status,
        "references": references,
        "precomputed": snapshots,
        "real_demo": {
            "folder": REAL_PRECOMPUTED_NAME,
            "run_id": new.run_id,
            "claims": len(new.claims),
            "taxa": new.summary.total_taxa,
            "decisions": {d.decision: d.claims for d in new.summary.decisions},
            "duration_seconds": new.summary.duration_seconds,
            "report_fingerprint": new.manifest.report_fingerprint,
            "comparison_to_v04": comparison.model_dump(mode="json"),
            "provenance": new.manifest.parameters.get("data_provenance"),
        },
        "harvest": harvest,
        "limitations": [
            "Integritas file bukan verifikasi taksonomi, status konservasi, atau akurasi lapangan.",
            "Panen parsial tidak dipakai untuk mengklaim cakupan nasional lengkap.",
            "Lihat docs/17_KESIAPAN_JURI.md untuk gerbang ahli, data, dan rencana tindak lanjut.",
        ],
    }
    if not all(item["valid"] for item in snapshots):
        raise ValueError("Ada snapshot pra-hitung yang tidak valid.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    value = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != value:
        raise ValueError("Inventaris rilis sudah ada dan berbeda; pilih nama rilis baru.")
    destination.write_text(value, encoding="utf-8", newline="\n")
    return report


def check_assets() -> dict:
    """Fresh clones use curated assets without rebuilding or downloading raw data."""
    cfg = load_rules()
    ref = load_reference(DEFAULT_REFERENCE).select(cfg, "normal", cfg.marker_default)
    target = ROOT / "precomputed" / REAL_PRECOMPUTED_NAME
    if not verify_run(target)["valid"]:
        raise ValueError("Hasil demo rilis tidak valid.")
    return {
        "reference": ref.manifest["reference_version"],
        "eligible": len(ref.eligible),
        "demo_valid": True,
    }


def data_quality() -> dict:
    """Inspect provenance links and known limitations; do not infer biological truth."""
    cfg = load_rules()
    ref = load_reference(DEFAULT_REFERENCE).select(cfg, "normal", cfg.marker_default)
    source_ids = {row["source_id"] for row in ref.tables["sources"]}
    missing = []
    for table, rows in ref.tables.items():
        for index, row in enumerate(rows):
            for field in ("source_id", "iucn_source_id", "invasive_source_id"):
                for source in row.get(field, "").split(";"):
                    if source and source not in source_ids:
                        missing.append({"table": table, "row": index + 2, "source_id": source})
    return {
        "reference_version": ref.manifest["reference_version"],
        "missing_source_links": missing,
        "source_types": dict(sorted(Counter(r["type"] for r in ref.tables["sources"]).items())),
        "checklist_source_quality": dict(
            sorted(Counter(r.get("source_quality", "") for r in ref.tables["checklist"]).items())
        ),
        "voucher_levels": dict(sorted(Counter(r.voucher_level for r in ref.eligible).items())),
        "sequence_flags": dict(
            sorted(Counter(f for r in ref.eligible for f in r.flags.split(";") if f).items())
        ),
        "alias_members": len(ref.tables["aliases"]),
        "complex_members": len(ref.tables["complexes"]),
        "interpretation": [
            "Semua hitungan berasal dari file snapshot; tautan sumber yang lengkap bukan verifikasi isi sumber.",
            "V2 tidak sama dengan identifikasi ahli terdokumentasi V1; V3 tanpa katalog voucher tetap berlabel.",
            "Flag conflict mempertahankan ambiguitas lintas spesies; bukan pembenaran memilih satu nama.",
            "Kamus nyata belum memiliki anggota kompleks terkurasi. Contoh kompleks di demo SIMULASI hanya uji perangkat lunak.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=["precompute", "audit", "check", "quality"])
    parser.add_argument(
        "--out", type=Path, default=ROOT / "validation/jury/v0.5/release_checks.json"
    )
    args = parser.parse_args()
    if args.task == "precompute":
        print(precompute(), flush=True)
    elif args.task == "audit":
        report = audit(args.out)
        print(
            json.dumps({"report": str(args.out), "demo": report["real_demo"]["run_id"]}), flush=True
        )
    elif args.task == "quality":
        report = data_quality()
        if report["missing_source_links"]:
            raise ValueError("Ada tautan sumber yang tidak terdaftar.")
        target = ROOT / "validation/jury/v0.5/data_quality.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        value = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if target.exists() and target.read_text(encoding="utf-8") != value:
            raise ValueError("Inventaris kualitas berbeda; gunakan versi baru.")
        target.write_text(value, encoding="utf-8", newline="\n")
        print(target, flush=True)
    else:
        print(json.dumps(check_assets()), flush=True)


if __name__ == "__main__":
    main()
