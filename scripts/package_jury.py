"""D-038 [MVP]: deterministic jury bundle; exclude environments, secrets and bulk raw data."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from biotrace_core.config import ROOT
from scripts.prepare_jury import check_assets

FOLDERS = [
    "api",
    "biotrace_core",
    "scripts",
    "tests",
    "templates",
    "docs",
    ".github",
    "data",
    "precomputed",
    "validation/results",
    "validation/jury/v0.5",
    "web/src",
    "web/dist",
    "raw/bagus_ref_v0.1",
]
FILES = [
    "README.md",
    "AGENTS.md",
    "Makefile",
    "pyproject.toml",
    "uv.lock",
    ".gitattributes",
    ".gitignore",
    "web/package.json",
    "web/package-lock.json",
    "web/tsconfig.json",
    "web/vite.config.ts",
    "web/index.html",
    "web/postcss.config.js",
    "web/tailwind.config.js",
]
SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".css",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".csv",
    ".tsv",
    ".fasta",
    ".fa",
    ".fna",
    ".html",
    ".js",
    ".txt",
    ".woff",
    ".woff2",
    ".pdf",
}


def package(destination: Path) -> dict:
    """Package curated data and verified evidence; no network or raw-data downloads."""
    check_assets()
    if not (ROOT / "web/dist/index.html").is_file():
        raise ValueError("Bangun frontend sebelum membuat paket juri.")
    if not (ROOT / "validation/results/2026-10-25_ID_v0.5_r0.4.json").is_file():
        raise ValueError("LOSO lengkap v0.5 belum tersedia; paket final belum diterbitkan.")
    paths = {ROOT / name for name in FILES}
    for folder in FOLDERS:
        paths.update(
            path
            for path in (ROOT / folder).rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUFFIXES
            and not {"__pycache__", "blastdb", "node_modules", ".cache"} & set(path.parts)
        )
    paths = {path for path in paths if path.is_file()}
    manifest = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix())
    }
    readme = """# Paket juri BioTrace v0.5

Mulai dari validation/jury/v0.5/ringkasan_juri.pdf dan docs/17_KESIAPAN_JURI.md.
Semua klaim lengkap ada di precomputed/edna_asli_marwayana2022_r0.4_v0.5/.
FILE_MANIFEST.json mencatat SHA-256 setiap berkas paket (kecuali indeks ini dan petunjuk ini).

## Menjalankan demo

Ekstrak seluruh ZIP ke satu folder. Setelah uv/Python dan dependensi terpasang:

    uv sync --frozen --no-dev
    uv run --no-dev uvicorn api.main:app --host 127.0.0.1 --port 8000

Buka http://127.0.0.1:8000 dan pilih Muat data eDNA asli Indonesia.
Build web sudah disertakan; Node/npm tidak diperlukan untuk menyajikan demo ini.
Demo memakai pra-hitung terverifikasi sehingga BLAST tidak wajib untuk membuka demo.
Analisis FASTA baru dan LOSO memerlukan BLAST+. Dependensi perlu dipasang sebelum
demo luring. Paket mengecualikan .venv, node_modules, token, dan unduhan raw berukuran besar.
Pengumpulan ulang raw/panen memakai fetch_data.py pada repo lengkap; jangan menyamakan
ketiadaan bulk raw dalam paket dengan kelengkapan data biologis.

Semua ambang belum dikalibrasi ahli. Deteksi DNA bukan bukti pasti ikan hidup di lokasi.
BioTrace menghasilkan laporan verifikasi pendukung, bukan dokumen AMDAL resmi.
Lisensi dan sumber data tercantum di tabel sources.csv dan laporan.
"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError("Paket tujuan sudah ada; pilih nama baru untuk menjaga salinan rilis.")
    with zipfile.ZipFile(
        destination, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        entries = [(name, (ROOT / name).read_bytes()) for name in manifest]
        entries.extend(
            [
                (
                    "FILE_MANIFEST.json",
                    (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode(),
                ),
                ("BACA_DULU_JURI.md", readme.encode()),
            ]
        )
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError("Paket gagal pemeriksaan ZIP.")
        for name, digest in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f"Hash isi paket tidak cocok: {name}.")
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(".sha256").write_text(
        f"{digest}  {destination.name}\n", encoding="utf-8"
    )
    return {
        "path": str(destination),
        "files": len(manifest),
        "bytes": destination.stat().st_size,
        "sha256": digest,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "output/BIOTRACE_JURI_v0.5.zip")
    args = parser.parse_args()
    print(json.dumps(package(args.out)), flush=True)


if __name__ == "__main__":
    main()
