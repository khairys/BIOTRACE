"""BioTrace command-line interfaces for F1/F24/F26/F39/F41 [MVP], F28/F30/F31/F32 [P1/P2]."""

import argparse
import json
import sys
from pathlib import Path

from biotrace_core.audit import read_run, verify_run
from biotrace_core.config import DEFAULT_RULES, ROOT, load_rules
from biotrace_core.io.loaders import write_table
from biotrace_core.pipeline import run_analysis
from biotrace_core.records import (
    aggregate_gaps,
    compare_runs,
    find_by_fingerprint,
    propose_sequences,
    rematch,
)
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
    run.add_argument("--ref", type=Path, default=ROOT / "data/reference/v0.3")
    run.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    run.add_argument("--out", type=Path, default=ROOT / "runs")
    run.add_argument("--mode", choices=["normal", "simulation", "validation"], default="normal")
    run.add_argument("--threads", type=int, default=4)
    verify = commands.add_parser("verify", help="Periksa hash input dan hasil run")
    target = verify.add_mutually_exclusive_group(required=True)
    target.add_argument("--run", type=Path)
    target.add_argument("--code", help="Kode/sidik jari laporan (12 atau 64 karakter) [P1]")
    verify.add_argument("--runs", type=Path, default=ROOT / "runs")
    again = commands.add_parser("rematch", help="Cocokkan ulang run dengan kamus/aturan lain [P2]")
    again.add_argument("--run", type=Path, required=True)
    again.add_argument("--ref", type=Path, required=True)
    again.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    again.add_argument("--out", type=Path, default=ROOT / "runs")
    compare = commands.add_parser("compare", help="Bandingkan klaim dua run [P2]")
    compare.add_argument("--base", type=Path, required=True)
    compare.add_argument("--other", type=Path, required=True)
    gaps = commands.add_parser("gaps", help="Gabungkan prioritas barcode lintas run [P1]")
    gaps.add_argument("--runs", type=Path, nargs="+", required=True)
    gaps.add_argument("--out", type=Path)
    gaps.add_argument(
        "--consent",
        action="store_true",
        help="Wajib: pemilik data setiap run telah menyetujui agregasi celah",
    )
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
    propose = ref_commands.add_parser("propose")
    propose.add_argument("--fasta", type=Path, required=True)
    propose.add_argument("--meta", type=Path, required=True)
    propose.add_argument("--ref", type=Path, required=True)
    propose.add_argument("--out", type=Path, default=ROOT / "proposals")
    propose.add_argument("--mode", choices=["normal", "simulation", "validation"], default="normal")
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
            output = verify_run(args.run) if args.run else find_by_fingerprint(args.runs, args.code)
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0 if output["valid"] else 1
        elif args.command == "rematch":
            result, diff = rematch(args.run, args.ref, args.rules, args.out)
            output = {"run_id": result.run_id, **diff.model_dump(mode="json")}
        elif args.command == "compare":
            output = compare_runs(read_run(args.base), read_run(args.other)).model_dump(mode="json")
        elif args.command == "gaps":
            if not args.consent:
                raise ValueError("Agregasi celah memerlukan --consent dari pemilik data.")
            rows = aggregate_gaps(args.runs)
            if args.out:
                if args.out.exists():
                    raise ValueError("File keluaran sudah ada.")
                write_table(args.out, rows)
            output = {"rows": rows}
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
            elif args.ref_command == "propose":
                output = propose_sequences(args.fasta, args.meta, ref, cfg, args.out)
            else:
                output = import_reference(args.fasta, args.meta, source, args.destination, cfg)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(f"Galat: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
