"""BioTrace command-line interfaces for F1/F24/F26/F39/F41 [MVP]."""

import argparse
import json
import sys
from pathlib import Path

from biotrace_core.audit import verify_run
from biotrace_core.config import DEFAULT_RULES, ROOT, load_rules
from biotrace_core.io.loaders import write_table
from biotrace_core.pipeline import run_analysis
from biotrace_core.reference.curate import import_reference
from biotrace_core.reference.store import coverage, load_reference, reference_stats
from biotrace_core.validation.loso import run_loso


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="BioTrace Indonesia - verifikasi pendukung data eDNA")
    commands = cli.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Jalankan analisis lokal")
    run.add_argument("--reads", type=Path, required=True)
    run.add_argument("--meta", type=Path, required=True)
    run.add_argument("--fasta", type=Path)
    run.add_argument("--taxonomy", type=Path)
    run.add_argument("--site-context", type=Path)
    run.add_argument("--ref", type=Path, default=ROOT / "data/reference/v0.1")
    run.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    run.add_argument("--out", type=Path, default=ROOT / "runs")
    run.add_argument("--mode", choices=["normal", "simulation", "validation"], default="normal")
    run.add_argument("--threads", type=int, default=4)
    verify = commands.add_parser("verify", help="Periksa hash input dan hasil run")
    verify.add_argument("--run", type=Path, required=True)
    ref = commands.add_parser("ref", help="Kurasi dan inspeksi kamus berversi")
    ref_commands = ref.add_subparsers(dest="ref_command", required=True)
    for name in ["stats", "coverage", "build"]:
        sub = ref_commands.add_parser(name)
        sub.add_argument("--ref", type=Path, required=True)
        sub.add_argument("--mode", choices=["normal", "simulation", "validation"], default="normal")
        if name == "coverage":
            sub.add_argument("--out", type=Path)
    imp = ref_commands.add_parser("import")
    imp.add_argument("--fasta", type=Path, required=True)
    imp.add_argument("--meta", type=Path, required=True)
    imp.add_argument("--from", dest="source", type=Path, required=True)
    imp.add_argument("--to", dest="destination", type=Path, required=True)
    imp.add_argument("--mode", choices=["normal", "simulation", "validation"], default="normal")
    validate = commands.add_parser("validate")
    validation = validate.add_subparsers(dest="validation_command", required=True)
    loso = validation.add_parser("loso")
    loso.add_argument("--ref", type=Path, required=True)
    loso.add_argument(
        "--module", help="Identitas modul untuk catatan pemanggil; manifest tetap sumber kebenaran"
    )
    loso.add_argument("--out", type=Path, required=True)
    loso.add_argument("--max-species", type=int)
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "run":
            result = run_analysis(
                args.reads,
                args.meta,
                args.fasta,
                args.taxonomy,
                args.site_context,
                args.ref,
                args.rules,
                args.out,
                args.mode,
                args.threads,
            )
            output = {
                "run_id": result.run_id,
                "report_fingerprint": result.manifest.report_fingerprint,
                "summary": result.summary.model_dump(mode="json"),
            }
        elif args.command == "verify":
            output = verify_run(args.run)
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0 if output["valid"] else 1
        elif args.command == "validate":
            output = run_loso(args.ref, args.out, max_species=args.max_species)
        else:
            cfg = load_rules()
            source = load_reference(
                args.source if args.ref_command == "import" else args.ref, args.mode
            )
            ref = source.select(cfg, args.mode, source.manifest["marker"])
            if args.ref_command == "stats":
                output = reference_stats(ref)
            elif args.ref_command == "coverage":
                rows = coverage(ref)
                if args.out:
                    if args.out.exists() or args.out.resolve().is_relative_to(args.ref.resolve()):
                        raise ValueError("Ekspor cakupan memerlukan file baru di luar versi kamus.")
                    write_table(args.out, [r.model_dump() for r in rows])
                output = {"coverage": [r.model_dump() for r in rows]}
            elif args.ref_command == "build":
                from biotrace_core.naming.blast import build_database

                output = {"database": str(build_database(ref, args.ref / "blastdb"))}
            else:
                output = import_reference(args.fasta, args.meta, source, args.destination, cfg)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"Galat: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
