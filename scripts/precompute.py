"""Save a VERIFIED actual demo run for offline fallback [MVP]."""

import shutil
import tempfile
from pathlib import Path

from biotrace_core.audit import verify_run
from biotrace_core.config import ROOT, load_rules
from biotrace_core.pipeline import run_analysis
from scripts.make_demo_data import DEMO


def precompute() -> Path:
    target = ROOT / "precomputed" / f"matano_SIMULASI_v3_{load_rules().rules_version}"
    if target.exists():
        raise ValueError(
            "Hasil pra-hitung sudah ada; buat versi demo baru agar jejak audit tetap utuh."
        )
    with tempfile.TemporaryDirectory(prefix="biotrace-precompute-") as temp:
        out = Path(temp)
        result = run_analysis(
            DEMO / "reads_SIMULASI.csv",
            DEMO / "metadata_SIMULASI.csv",
            DEMO / "asv_SIMULASI.fasta",
            DEMO / "taxonomy_SIMULASI.csv",
            None,
            DEMO / "reference_SIMULASI",
            out_root=out,
            mode="simulation",
        )
        source = out / result.run_id
        if not verify_run(source)["valid"]:
            raise ValueError("Verifikasi hasil demo gagal.")
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("blastdb"))
        if not verify_run(target)["valid"]:
            raise ValueError("Salinan pra-hitung gagal verifikasi.")
    print(target)
    return target


if __name__ == "__main__":
    precompute()
