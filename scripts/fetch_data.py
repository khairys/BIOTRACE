#!/usr/bin/env python3
"""Unduh dataset publik BioTrace ke folder raw/ dan catat asal-usulnya.

Dijalankan di laptop tim (butuh internet). Mesin inti BioTrace tidak pernah
mengunduh apa pun (AGENTS.md A8); skrip ini terpisah dan hanya mengisi raw/.

Pemakaian:
    python scripts/fetch_data.py --list
    python scripts/fetch_data.py stelbrink2014 guyana12s lsp_small
    python scripts/fetch_data.py all            # semua kecuali file besar
    python scripts/fetch_data.py lsp_raw        # FASTQ 2,94 GB (opsional)

Setiap unduhan dicatat di raw/DOWNLOAD_LOG.md (URL, tanggal, SHA-256).
Lisensi wajib dicek manual di halaman sumber lalu ditulis di log.

STATUS: skrip belum diuji terhadap API langsung (ditulis tanpa akses internet).
Bila sebuah langkah gagal, ikuti cara manual di scripts/fetch_instructions.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "raw"
LOG = RAW / "DOWNLOAD_LOG.md"
UA = {"User-Agent": "BioTrace-fetch/1.0 (research; contact via repo)"}

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _get_json(url: str) -> dict | list:
    return json.loads(_get(url).decode("utf-8"))


def _download(url: str, dest: Path, chunk: int = 1 << 20) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while True:
            b = r.read(chunk)
            if not b:
                break
            f.write(b)
    return dest


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _log(name: str, url: str, path: Path, note: str = "") -> None:
    RAW.mkdir(exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Log Unduhan Data\n\n| Dataset | File | URL | Tanggal | SHA-256 | Lisensi (isi manual) | Catatan |\n"
            "|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(
            f"| {name} | {path.relative_to(RAW)} | {url} | {dt.date.today()} | "
            f"{_sha256(path)[:16]}… | ? | {note} |\n"
        )
    print(f"  ✓ {path.relative_to(RAW.parent)}")


def _accession_range(prefix: str, start: int, end: int) -> list[str]:
    return [f"{prefix}{n}" for n in range(start, end + 1)]


def _efetch(ids: list[str], rettype: str) -> bytes:
    params = urllib.parse.urlencode(
        {"db": "nuccore", "id": ",".join(ids), "rettype": rettype, "retmode": "text"}
    )
    return _get(f"{EUTILS}?{params}")


# ---------------------------------------------------------------- datasets


def stelbrink2014() -> None:
    """Telmatherinidae Malili, 12S–16S KJ667771–KJ667865 (Stelbrink dkk. 2014)."""
    ids = _accession_range("KJ", 667771, 667865)
    out = RAW / "stelbrink2014"
    out.mkdir(parents=True, exist_ok=True)
    for rettype, ext in (("fasta", "fasta"), ("gb", "gb")):
        data = _efetch(ids, rettype)
        p = out / f"stelbrink2014_12s16s.{ext}"
        p.write_bytes(data)
        _log("stelbrink2014", f"{EUTILS} (KJ667771–KJ667865, {rettype})", p, f"{len(ids)} aksesi")
        time.sleep(0.5)  # sopan terhadap NCBI (maks 3 permintaan/detik tanpa API key)


def stelbrink2014_nd2() -> None:
    """ND2 KJ667866–KJ667963 (bukan 12S; untuk referensi lanjutan)."""
    ids = _accession_range("KJ", 667866, 667963)
    p = RAW / "stelbrink2014" / "stelbrink2014_nd2.fasta"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(_efetch(ids, "fasta"))
    _log("stelbrink2014_nd2", f"{EUTILS} (KJ667866–KJ667963)", p, f"{len(ids)} aksesi")


def guyana12s() -> None:
    """Pustaka 12S Guyana Prancis (Scientific Data 2026), Figshare 29168144."""
    meta = _get_json("https://api.figshare.com/v2/articles/29168144")
    out = RAW / "french_guiana_12s"
    out.mkdir(parents=True, exist_ok=True)
    (out / "figshare_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"  lisensi menurut Figshare: {meta.get('license', {}).get('name', '?')}")
    for f in meta.get("files", []):
        p = _download(f["download_url"], out / f["name"])
        _log("guyana12s", f["download_url"], p, meta.get("license", {}).get("name", ""))


DRYAD_DOI = "doi:10.5061/dryad.3bk3j9kzf"
LSP_SMALL = {
    "edna_lg_clean.csv",
    "edna_env.csv",
    "elec_long.csv",
    "elec_env.csv",
    "fish_codes.csv",
    "README.md",
}


def _dryad_files() -> list[dict]:
    base = "https://datadryad.org/api/v2"
    doi = urllib.parse.quote(DRYAD_DOI, safe="")
    versions = _get_json(f"{base}/datasets/{doi}/versions")
    items = versions["_embedded"]["stash:versions"]
    latest = items[-1]
    files_href = latest["_links"]["stash:files"]["href"]
    files = _get_json(f"https://datadryad.org{files_href}")
    out = []
    for f in files["_embedded"]["stash:files"]:
        out.append(
            {
                "name": f["path"],
                "href": "https://datadryad.org" + f["_links"]["stash:download"]["href"],
            }
        )
    return out


def lsp_small() -> None:
    """Lake St. Pierre (Astorg dkk. 2025): file CSV kecil + README."""
    out = RAW / "lake_st_pierre"
    for f in _dryad_files():
        if f["name"] in LSP_SMALL:
            p = _download(f["href"], out / f["name"])
            _log("lake_st_pierre", f["href"], p)


def lsp_raw() -> None:
    """Lake St. Pierre raw_seq.zip (±2,94 GB)."""
    out = RAW / "lake_st_pierre"
    for f in _dryad_files():
        if f["name"] == "raw_seq.zip":
            print("  mengunduh ±2,94 GB, bisa lama…")
            p = _download(f["href"], out / f["name"])
            _log("lake_st_pierre_raw", f["href"], p)


MALILI = RAW / "malili12s_mitohelper"


def _missing_voucher_or_country() -> list[str]:
    """Aksesi kandidat yang esummary-nya tanpa /specimen_voucher atau /country (docs/13 §3)."""
    missing = []
    for path in sorted((MALILI / "genbank").glob("esummary_*.json")):
        result = json.loads(path.read_text(encoding="utf-8"))["result"]
        for uid in result["uids"]:
            doc = result[uid]
            names = (doc.get("subtype") or "").split("|")
            values = (doc.get("subname") or "").split("|")
            q = dict(zip(names, values, strict=False))
            if not q.get("specimen_voucher") or not (q.get("country") or q.get("geo_loc_name")):
                missing.append(doc["caption"])
    return sorted(set(missing))


def malili12s_genbank_headers() -> None:
    """Header GenBank (REFERENCE, kualifier source) untuk aksesi Malili yang esummary-nya kurang.

    efetch rettype=gb dengan seq_start=1 dan seq_stop=1: flat file lengkap kecuali sekuens
    (sekuens sudah ada di arsip mitohelper). Jumlah record diverifikasi per batch.
    """
    ids = _missing_voucher_or_country()
    out = MALILI / "genbank_flat"
    out.mkdir(parents=True, exist_ok=True)
    (out / "accessions.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    for i in range(0, len(ids), 50):
        chunk = ids[i : i + 50]
        p = out / f"headers_{i // 50:03d}.gb"
        if p.exists():  # lanjutkan unduhan yang terputus; batch lama sudah tercatat di log
            continue
        params = urllib.parse.urlencode(
            {
                "db": "nuccore",
                "id": ",".join(chunk),
                "rettype": "gb",
                "retmode": "text",
                "seq_start": 1,
                "seq_stop": 1,
                "tool": "biotrace",
            }
        )
        for attempt in range(4):  # NCBI kadang membalas 5xx sementara
            try:
                data = _get(f"{EUTILS}?{params}")
                break
            except OSError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
        text = data.decode("utf-8")
        found = text.count("\nACCESSION ") + text.startswith("ACCESSION ")
        if found != len(chunk):
            raise RuntimeError(
                f"batch {i // 50}: {found} dari {len(chunk)} record; unduhan sebagian"
            )
        p.write_bytes(data)
        _log(
            "malili12s_genbank_headers",
            f"{EUTILS} (rettype=gb, seq_start=1, seq_stop=1)",
            p,
            f"{len(chunk)} aksesi tanpa voucher/negara di esummary",
        )
        time.sleep(0.5)


DATASETS = {
    "malili12s_genbank_headers": (
        malili12s_genbank_headers,
        "Header GenBank aksesi Malili tanpa voucher/negara di esummary (docs/13 §3)",
    ),
    "stelbrink2014": (stelbrink2014, "Sekuens 12S–16S Telmatherinidae Malili (prioritas 1)"),
    "stelbrink2014_nd2": (stelbrink2014_nd2, "Sekuens ND2 Telmatherinidae (opsional)"),
    "guyana12s": (guyana12s, "Pustaka 12S Guyana Prancis untuk uji LOSO (prioritas 4)"),
    "lsp_small": (lsp_small, "Lake St. Pierre CSV + README (prioritas 4)"),
    "lsp_raw": (lsp_raw, "Lake St. Pierre FASTQ 2,94 GB (opsional, P1)"),
}
DEFAULT_ALL = ["stelbrink2014", "guyana12s", "lsp_small"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("names", nargs="*", help="nama dataset atau 'all'")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.names:
        for k, (_, d) in DATASETS.items():
            print(f"{k:20s} {d}")
        print(
            "\nPDF checklist (Herder 2006/2012, Tantu & Nilawati 2007) diunduh manual: "
            "lihat scripts/fetch_instructions.md §4"
        )
        return 0
    names = DEFAULT_ALL if a.names == ["all"] else a.names
    failed = []
    for n in names:
        if n not in DATASETS:
            print(f"✗ tidak dikenal: {n}")
            failed.append(n)
            continue
        print(f"→ {n}")
        try:
            DATASETS[n][0]()
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ gagal: {e}\n    Pakai cara manual di scripts/fetch_instructions.md")
            failed.append(n)
    print("\nSelesai." + (f" Gagal: {', '.join(failed)}" if failed else ""))
    print(f"Isi kolom lisensi di {LOG.relative_to(RAW.parent)} secara manual.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
