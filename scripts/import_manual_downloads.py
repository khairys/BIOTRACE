"""Impor unduhan manual pengguna 25 Okt 2026 ke data/curation/ (docs/16 §4, M2–M6) [P1].

Sumber (di raw/, SHA-256 di raw/DOWNLOAD_LOG.md):
- raw/dryad_tb2rbp00g_rasborinae/  Mitogenomics dataset for the Rasborinae of Sundaland (CC0;
  paper doi:10.1111/jbi.14141). 79 mitogenom + barcode COI dalam alignment NEXUS.
- raw/dryad_tk5rj_jawabali/        Data from: Revisiting the ichthyodiversity of Java and Bali
  through DNA barcodes (Dahruddin dkk. 2017; CC0). 1.046 sekuens COI berlabel BOLD|voucher|spesies.
- raw/dryad_sqv9s4n6f_rajaampat/   Juhel dkk. 2022, eDNA Raja Ampat/Lengguru (CC0): checklist ikan
  laut Raja Ampat (S4), pustaka 12S teleo Lengguru (S3), daftar UVC (S5) dan eDNA (S6).

Tidak ada nilai yang ditebak (A1). Asal spesimen Rasborinae tidak tercantum per spesimen di sumber,
jadi `specimen_country` dikosongkan dan kode voucher BIF dicatat apa adanya. Pustaka Lengguru
memakai primer teleo (Appendix S1), bukan MiFish, jadi tidak masuk kandidat kamus MiFish.

Jalankan:
    uv run --no-project --with openpyxl --with pydantic --with pyyaml --with numpy \
        python scripts/import_manual_downloads.py
"""

from __future__ import annotations

import csv
import io
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biotrace_core.config import load_rules  # noqa: E402
from scripts.analyze_tropis import trim_mifish_fast  # noqa: E402

OUT = ROOT / "data/curation"
RASBO = ROOT / "raw/dryad_tb2rbp00g_rasborinae/doi_10_5061_dryad_tb2rbp00g__v20220327.zip"
JAWA = ROOT / "raw/dryad_tk5rj_jawabali/doi_10_5061_dryad_tk5rj__v20160321.zip"
RAJA = ROOT / "raw/dryad_sqv9s4n6f_rajaampat/doi_10_5061_dryad_sqv9s4n6f__v20220706.zip"
ACCESSION = re.compile(r"^(?:[A-Z]{2}_?\d{6}(?:_\d)?|[A-Z]{1,2}\d{5,6})$")


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"  {path.relative_to(ROOT)}: {len(rows)} baris")


def nexus_matrix(text: str) -> dict[str, str]:
    block = re.search(r"matrix(.*?);", text, re.S | re.I).group(1)
    seqs: dict[str, str] = {}
    for line in block.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            seqs[parts[0]] = seqs.get(parts[0], "") + "".join(parts[1:])
    return seqs


def parse_label(label: str) -> dict[str, str]:
    """`MTG_Genus_species_ACC` atau `Genus_species_kodeLokal_VOUCHER/ACC` sesuai sumber."""
    parts = label.split("_")
    mito = parts[0] == "MTG"
    if mito:
        parts = parts[1:]
    genus, epithet = parts[0], parts[1] if len(parts) > 1 else ""
    tail = parts[2:]
    token = (
        "_".join(tail[-2:]) if len(tail) >= 2 and tail[-1].isdigit() else (tail[-1] if tail else "")
    )
    voucher = token if token.startswith("BIF") else ""
    accession = "" if voucher else token
    return {
        "species_verbatim": f"{genus} {epithet}".strip(),
        "voucher_bif": voucher,
        "accession_in_label": accession
        if accession and ACCESSION.match(accession.replace("_1", ""))
        else accession,
        "is_mitogenome_label": str(mito).lower(),
    }


def rasborinae(cfg) -> None:  # noqa: ANN001
    z = zipfile.ZipFile(RASBO)
    rows, fasta, seen = [], [], set()
    for name in sorted(n for n in z.namelist() if n.endswith(".nexus")):
        for label, aligned in nexus_matrix(z.read(name).decode("utf-8", "replace")).items():
            if label in seen:
                continue
            seen.add(label)
            seq = re.sub(r"[-?]", "", aligned).upper()
            insert = trim_mifish_fast(seq, cfg) if seq else None
            if not insert:
                continue
            info = parse_label(label)
            rows.append(
                {
                    "label_verbatim": label,
                    **info,
                    "alignment_file": name,
                    "ungapped_length": len(seq),
                    "mifish_length": len(insert),
                    "specimen_country": "",
                    "notes": "asal spesimen tidak dicantumkan per spesimen (lokasi dataset: Sundaland); "
                    "verifikasi lewat tabel suplemen doi:10.1111/jbi.14141",
                }
            )
            fasta.append(f">{label}\n{insert}\n")
    rows.sort(key=lambda r: r["label_verbatim"])
    write(OUT / "rasborinae_sundaland_tb2rbp00g/mifish_candidates.csv", rows)
    (OUT / "rasborinae_sundaland_tb2rbp00g/mifish_candidates.fasta").write_text(
        "".join(sorted(fasta)), "utf-8"
    )


def jawabali() -> None:
    z = zipfile.ZipFile(JAWA)
    text = z.read("Sequence+alignment.fas").decode("utf-8", "replace")
    rows = []
    for line in text.splitlines():
        if line.startswith(">"):
            parts = line[1:].split("|")
            rows.append(
                {
                    "bold_processid": parts[0],
                    "voucher_bif": parts[1] if len(parts) > 1 else "",
                    "species_verbatim": parts[2] if len(parts) > 2 else "",
                    "marker": parts[3] if len(parts) > 3 else "",
                }
            )
    rows.sort(key=lambda r: (r["species_verbatim"], r["bold_processid"]))
    write(OUT / "jawabali_dahruddin2017_tk5rj/coi_specimens.csv", rows)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["species_verbatim"]] = counts.get(r["species_verbatim"], 0) + 1
    write(
        OUT / "jawabali_dahruddin2017_tk5rj/species_summary.csv",
        [{"species_verbatim": k, "coi_specimens": v} for k, v in sorted(counts.items())],
    )


def rajaampat() -> None:
    import openpyxl

    z = zipfile.ZipFile(RAJA)
    base = OUT / "rajaampat_juhel2022_sqv9s4n6f"
    wb = openpyxl.load_workbook(
        io.BytesIO(
            z.read(
                "Appendix_S4_Updated_marine_fish_checklist_of_the_Raja_Ampat_Birds_Head_Peninsula_region.xlsx"
            )
        ),
        read_only=True,
    )
    sheet = list(wb.worksheets[0].iter_rows(values_only=True))
    head = [str(h) for h in sheet[0]]
    write(
        base / "checklist_raja_ampat_S4.csv",
        [
            dict(zip(head, ["" if v is None else str(v) for v in r], strict=False))
            for r in sheet[1:]
            if any(r)
        ],
    )
    for member, out_name in [
        (
            "Appendix_S3_Custom_reference_database_12S_Lengguru.csv",
            "reference_12s_teleo_lengguru_S3.csv",
        ),
        ("Appendix_S5_List_of_species_detected_by_UVC.csv", "species_uvc_S5.csv"),
        ("Appendix_S6_list_of_species_detected_by_eDNA.csv", "species_edna_S6.csv"),
    ]:
        reader = csv.DictReader(
            io.StringIO(z.read(member).decode("utf-8", "replace")), delimiter=";"
        )
        write(
            base / out_name,
            [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in reader],
        )


def main() -> None:
    cfg = load_rules()
    print("Rasborinae Sundaland (MiFish dari mitogenom):")
    rasborinae(cfg)
    print("Jawa-Bali (COI):")
    jawabali()
    print("Raja Ampat / Lengguru:")
    rajaampat()


if __name__ == "__main__":
    main()
