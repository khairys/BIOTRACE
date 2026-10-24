"""Import the user's manually downloaded Dryad ZIP without inventing ASV metadata.

Usage: uv run python scripts/import_lake_st_pierre.py --archive <download.zip>
The source ZIP is preserved in raw/lake_st_pierre/downloads/. FASTQ stays archived
because raw-read processing is outside the MVP. No network access is performed.
"""

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "edna_env.csv",
    "elec_env.csv",
    "edna_lg_clean.csv",
    "elec_long.csv",
    "fish_codes.csv",
    "raw_seq.zip",
    "README.md",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def import_archive(archive_path: Path) -> dict:
    source = archive_path.resolve(strict=True)
    target = (ROOT / "raw/lake_st_pierre").resolve()
    external = (ROOT / "data/external/lake_st_pierre/v20250924").resolve()
    for path in (target, external):
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError("Lokasi tujuan di luar workspace.")
    if external.exists():
        raise ValueError("Versi dataset sudah ada; tidak ditimpa.")
    with ZipFile(source) as archive:
        entries = archive.infolist()
        if len(entries) != len(EXPECTED) or {i.filename for i in entries} != EXPECTED:
            raise ValueError("Daftar isi ZIP tidak sesuai dataset Dryad yang diharapkan.")
        if any(i.flag_bits & 1 or i.file_size > 4 * 1024**3 for i in entries):
            raise ValueError("ZIP terenkripsi atau melebihi batas ukuran dataset.")
        extracted = target / "v20250924"
        extracted.mkdir(parents=True, exist_ok=False)
        hashes = {}
        for entry in entries:
            dest = (extracted / entry.filename).resolve()
            if dest.parent != extracted.resolve():
                raise ValueError("Nama file ZIP keluar dari direktori.")
            # ZipExtFile validates CRC on EOF; exclusive write preserves existing raw files.
            with archive.open(entry) as src, dest.open("xb") as dst:
                shutil.copyfileobj(src, dst, 1024 * 1024)
            hashes[entry.filename] = digest(dest)
    original_hash = digest(source)
    downloads = target / "downloads"
    downloads.mkdir(exist_ok=True)
    preserved = (downloads / source.name).resolve()
    if not preserved.is_relative_to(target) or preserved.exists():
        raise ValueError("Arsip sumber tidak boleh ditimpa.")
    # The user explicitly requested moving the newly supplied root archive.
    shutil.move(str(source), str(preserved))
    external.mkdir(parents=True, exist_ok=False)
    for name in sorted(EXPECTED - {"raw_seq.zip"}):
        shutil.copy2(extracted / name, external / name)
    profiles = {}
    for path in sorted(external.glob("*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            sample = stream.read(4096)
            stream.seek(0)
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
            reader = csv.DictReader(stream, delimiter=delimiter)
            rows = list(reader)
            profiles[path.name] = {
                "rows": len(rows),
                "columns": reader.fieldnames,
                "delimiter": delimiter,
            }
    with ZipFile(extracted / "raw_seq.zip") as inner:
        sequence_files = [
            {"name": i.filename, "bytes": i.file_size, "crc32": f"{i.CRC:08x}"}
            for i in inner.infolist()
            if not i.is_dir()
        ]
    manifest = {
        "dataset": "lake_st_pierre",
        "module": "CA-QC",
        "version": "v20250924",
        "source": "https://doi.org/10.5061/dryad.3bk3j9kzf",
        "license": "CC0",
        "imported_at": datetime.now(ZoneInfo("Asia/Jakarta")).isoformat(),
        "archive_path": preserved.relative_to(ROOT).as_posix(),
        "archive_sha256": original_hash,
        "raw_files_sha256": hashes,
        "tables": profiles,
        "sequence_files": sequence_files,
        "usage": "validation_only",
        "asv_pipeline_ready": False,
        "notes": [
            "CSV olahan per kode ikan, bukan tabel ASV.",
            "Jangan mengarang identity, kontrol, atau batch yang tidak tersedia.",
            "FASTQ dipertahankan dalam raw_seq.zip; pemrosesan FASTQ di luar MVP.",
        ],
    }
    (external / "dataset_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (external / "README_BIOTRACE.md").write_text(
        "# Lake St. Pierre - modul data validasi\n\nSumber: https://doi.org/10.5061/dryad.3bk3j9kzf (CC0).\n\n"
        "Diimpor dari ZIP unduhan manual pengguna. CSV/README sumber disalin tanpa perubahan. Hash, kolom dan inventaris FASTQ: dataset_manifest.json.\n\n"
        "Bukan kamus referensi dan tidak boleh mendukung nama ikan Indonesia. CSV agregat tidak diberi ASV/identity/batch buatan. FASTQ disimpan terarsip di raw/lake_st_pierre/v20250924/raw_seq.zip.\n",
        encoding="utf-8",
    )
    (external / "sources.csv").write_text(
        "source_id,citation,doi_or_url,type,license,accessed_date\n"
        'SRC_ASTORG2025,"Astorg L. dkk. (2025). eDNA metabarcoding to monitor fish communities in a large river floodplain. Dryad dataset.",https://doi.org/10.5061/dryad.3bk3j9kzf,database,CC0,2026-10-24\n',
        encoding="utf-8",
    )
    with (ROOT / "raw/DOWNLOAD_LOG.md").open("a", encoding="utf-8") as log:
        log.write(
            f"\n## Impor ZIP manual Lake St. Pierre\n\nSumber disediakan pengguna; DOI https://doi.org/10.5061/dryad.3bk3j9kzf; CC0 menurut kebijakan Dryad. Arsip dipindahkan ke `{preserved.relative_to(ROOT).as_posix()}`; SHA-256 `{original_hash}`. Waktu impor {manifest['imported_at']}.\n\n"
        )
        for name, sha in sorted(hashes.items()):
            log.write(
                f"- `{(extracted / name).relative_to(ROOT).as_posix()}`: `{sha}`; CRC ZIP lulus saat ekstraksi.\n"
            )
    print(
        json.dumps(
            {
                "imported": external.relative_to(ROOT).as_posix(),
                "tables": profiles,
                "sequence_files": len(sequence_files),
                "archive_sha256": original_hash,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    import_archive(args.archive)
