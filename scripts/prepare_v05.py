"""Kamus Indonesia v0.5 = v0.4 + MiFish Rasborinae Sundaland bervoucher (D-037, Diusulkan).

Tambahan terhadap v0.4 (yang diwarisi apa adanya lalu dikurasi ulang bersama, R-CUR-07/08):
1. Sekuens daerah MiFish dari mitogenom dataset Dryad 10.5061/dryad.tb2rbp00g (Rasborinae of
   Sundaland, CC0; data/curation/rasborinae_sundaland_tb2rbp00g/). Hanya baris berkode voucher
   BIF yang ada di unduhan BOLD global (raw/tropis/bold): asal spesimen dan institusi diambil dari
   kolom BOLD `country/ocean` dan `inst` rekaman itu, bukan ditebak (A1). Voucher level V2.
   Nama spesies harus cocok ke FishBase Indonesia (nama/sinonim); "sp." dilewati.
2. Perairan nasional AIR_TAWAR_INDONESIA: checklist FishBase tingkat negara untuk spesies air
   tawar (pola sama dengan LAUT_INDONESIA di v0.4; source_quality primer karena file sumber di raw/).

Jalankan:
    uv run --no-project --with pyarrow --with pydantic --with pyyaml --with numpy \
        python scripts/prepare_v05.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biotrace_core.config import load_rules  # noqa: E402
from biotrace_core.io.loaders import read_fasta, read_table  # noqa: E402
from biotrace_core.models import Taxon  # noqa: E402
from biotrace_core.reference.curate import curate_records, write_reference  # noqa: E402
from biotrace_core.reference.store import ReferenceIndex, coverage  # noqa: E402
from scripts.analyze_tropis import binomial, latest, load_fishbase  # noqa: E402

V04 = ROOT / "data/reference/v0.4"
V05 = ROOT / "data/reference/v0.5"
CAND = ROOT / "data/curation/rasborinae_sundaland_tb2rbp00g"
DATE = "2026-10-25"
CURATOR = "agent:Claude Code (instruksi Agathan)"
ORIGIN = {"native": "asli", "endemic": "endemik", "introduced": "introduksi"}
TABLES = (
    "sequences",
    "taxa",
    "waterbodies",
    "checklist",
    "status",
    "aliases",
    "complexes",
    "introductions",
    "sources",
)
NEW_SOURCES = [
    {
        "source_id": "SRC_RASBORINAE_TB2RBP00G",
        "citation": "Mitogenomics dataset for the Rasborinae of Sundaland, Dryad doi:10.5061/dryad.tb2rbp00g (CC0); paper doi:10.1111/jbi.14141",
        "doi_or_url": "https://doi.org/10.5061/dryad.tb2rbp00g",
        "type": "database",
        "license": "CC0 1.0",
        "accessed_date": DATE,
    },
    {
        "source_id": "SRC_BOLD_V5_2026",
        "citation": "BOLD Systems v5, unduhan global Teleostei 25 Okt 2026 (raw/tropis/bold), dipakai untuk asal spesimen voucher BIF",
        "doi_or_url": "https://portal.boldsystems.org/",
        "type": "database",
        "license": "rekaman publik BOLD",
        "accessed_date": DATE,
    },
]
WATERBODY = {
    "waterbody_id": "AIR_TAWAR_INDONESIA",
    "name": "Perairan tawar Indonesia (checklist tingkat negara)",
    "type": "sungai",
    "complex_id": "",
    "country": "ID",
}


def bold_vouchers(wanted: set[str]) -> dict[str, dict]:
    """sampleid/museumid/fieldid BOLD -> rekaman (negara, provinsi, institusi, processid)."""
    csv.field_size_limit(10**9)
    folder = latest("bold")
    found: dict[str, dict] = {}
    with open(folder / "teleostei_global.tsv", encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            for key in (row.get("sampleid", ""), row.get("museumid", ""), row.get("fieldid", "")):
                if key in wanted and key not in found:
                    found[key] = row
    return found


def main() -> None:
    if V05.exists():
        raise SystemExit(f"{V05} sudah ada; buat versi baru (A12).")
    cfg = load_rules()
    marker = "12S_MiFish_U"
    universe, names = load_fishbase()
    v04 = {n: read_table(V04 / f"{n}.csv") for n in TABLES}
    fasta = read_fasta(V04 / "sequences.fasta", "ACGTNRYSWKMBDHV")
    rows = list(v04["sequences"])
    taxa = {r["species_valid"]: dict(r) for r in v04["taxa"]}

    cand = list(csv.DictReader(open(CAND / "mifish_candidates.csv", encoding="utf-8")))
    inserts = read_fasta(CAND / "mifish_candidates.fasta", "ACGTNRYSWKMBDHV")
    bold = bold_vouchers({r["voucher_bif"] for r in cand if r["voucher_bif"]})
    skipped: Counter = Counter()
    for r in sorted(cand, key=lambda r: r["label_verbatim"]):
        voucher = r["voucher_bif"]
        if not voucher:
            skipped["tanpa_voucher_bif"] += 1
            continue
        b = bold.get(voucher)
        if b is None:
            skipped["voucher_tidak_ada_di_bold"] += 1
            continue
        code = names.get(binomial(r["species_verbatim"]))
        if code is None:
            skipped["nama_tidak_cocok_fishbase_indonesia"] += 1
            continue
        name = universe[code]["species"]
        if name not in taxa:
            taxa[name] = {
                "species_valid": name,
                "genus": name.split()[0],
                "family": universe[code]["family"],
                "order": universe[code]["order"],
                "authority": "",
                "synonyms": "",
                "in_indonesia": True,
                "cof_checked_date": "",
                "source_id": "SRC_FISHBASE_V2504",
            }
        seq_id = f"RASB_{voucher}"
        country = b.get("country/ocean", "")
        rows.append(
            {
                "seq_id": seq_id,
                "accession": "",
                "source_db": "paper_supplement",
                "source_id": "SRC_RASBORINAE_TB2RBP00G",
                "species_original": r["species_verbatim"],
                "species_valid": name,
                "marker": marker,
                "region_trimmed": True,
                "length": len(inserts[r["label_verbatim"]]),
                "n_ambiguous": sum(c not in "ACGT" for c in inserts[r["label_verbatim"]]),
                "voucher_level": "V2",
                "voucher_catalog": voucher,
                "voucher_institution": b.get("inst", ""),
                "specimen_country": "ID" if country == "Indonesia" else country,
                "specimen_locality": b.get("province/state", ""),
                "curation_status": "accepted",
                "flags": "",
                "license": "CC0 1.0",
                "date_added": DATE,
                "curator": CURATOR,
                "is_simulated": False,
            }
        )
        fasta[seq_id] = inserts[r["label_verbatim"]]

    checklist = [dict(r) for r in v04["checklist"]]
    for _code, sp in sorted(universe.items(), key=lambda kv: kv[1]["species"]):
        if not sp["freshwater"] or sp["status_id"] not in ORIGIN:
            continue
        checklist.append(
            {
                "waterbody_id": "AIR_TAWAR_INDONESIA",
                "species_valid": sp["species"],
                "origin_status": ORIGIN[sp["status_id"]],
                "endemic_scope": "indonesia" if sp["status_id"] == "endemic" else "",
                "source_id": "SRC_FISHBASE_V2504",
                "year_recorded": "",
                "notes": "FishBase v25.04 tabel country (C_Code 360), Freshwater=1, tingkat negara",
                "source_quality": "primer",
            }
        )
        if sp["species"] not in taxa:
            taxa[sp["species"]] = {
                "species_valid": sp["species"],
                "genus": sp["species"].split()[0],
                "family": sp["family"],
                "order": sp["order"],
                "authority": "",
                "synonyms": "",
                "in_indonesia": True,
                "cof_checked_date": "",
                "source_id": "SRC_FISHBASE_V2504",
            }
    checklist.sort(key=lambda r: (r["waterbody_id"], r["species_valid"]))

    sources = v04["sources"] + NEW_SOURCES
    manifest = {"reference_version": "v0.5", "module": "ID", "marker": marker}
    staging = ReferenceIndex(
        manifest,
        {n: Taxon.model_validate(t) for n, t in taxa.items()},
        [],
        {},
        {"sources": sources},
    )
    curated, seqs, report = curate_records(rows, fasta, staging, cfg, marker)
    used = (
        {r.species_valid for r in curated}
        | {r["species_valid"] for r in checklist if not r["species_valid"].startswith("alias:")}
        | {r["species_valid"] for r in v04["taxa"]}
    )
    taxa_out = [taxa[n] for n in sorted(used) if n in taxa]
    tables = {
        "sequences": [r.model_dump() for r in curated],
        "taxa": taxa_out,
        "waterbodies": v04["waterbodies"] + [WATERBODY],
        "checklist": checklist,
        "status": v04["status"],
        "aliases": v04["aliases"],
        "complexes": v04["complexes"],
        "introductions": v04["introductions"],
        "sources": sorted(sources, key=lambda r: r["source_id"]),
    }
    index = ReferenceIndex(
        manifest,
        {t["species_valid"]: Taxon.model_validate(t) for t in taxa_out},
        curated,
        seqs,
        tables,
    )
    tables["coverage"] = [r.model_dump() for r in coverage(index.select(cfg, "normal", marker))]
    tables["curation_report"] = sorted(report, key=lambda r: (r["seq_id"], r["step"]))
    new = [r for r in curated if r.source_id == "SRC_RASBORINAE_TB2RBP00G"]
    n_id = sum(r.specimen_country == "ID" for r in curated)
    notes = (
        "Dari v0.4 (D-035) + MiFish Rasborinae Sundaland bervoucher BIF (Dryad tb2rbp00g, asal spesimen "
        f"dari rekaman BOLD) + checklist AIR_TAWAR_INDONESIA (FishBase tingkat negara). D-037 Diusulkan. "
        f"Sekuens diterima {len(curated)} dari {len({r.species_valid for r in curated})} spesies; "
        f"spesimen bertanda Indonesia {n_id}; tambahan Rasborinae diterima {len(new)} dari "
        f"{len({r.species_valid for r in new})} spesies. Kandidat dilewati: "
        + "; ".join(f"{k} {v}" for k, v in sorted(skipped.items()))
        + ". Usulan tim, belum dikalibrasi ahli."
    )
    write_reference(V05, "v0.5", "ID", marker, tables, seqs, notes=notes, created=DATE)
    print(notes)


if __name__ == "__main__":
    main()
