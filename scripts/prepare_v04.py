"""Kamus Indonesia v0.4 (nasional, air laut + air tawar) dari panen raw/tropis/ (D-035, Diusulkan).

v0.3 diwarisi apa adanya; ditambah sekuens GenBank hasil panen (docs/16) untuk spesies yang
tercatat di Indonesia menurut FishBase (raw/tropis/fishbase), perairan nasional
LAUT_INDONESIA dengan checklist FishBase tingkat negara, dan status invasif dari transkripsi
Permen KP 19/2020. Semua sekuens lewat curate_records (R-CUR). Pemotongan MiFish dilakukan
lebih dulu dengan trim_mifish_fast (diverifikasi identik dengan trim_mifish pada sampel),
lalu diteruskan sebagai region_trimmed=True; sisa aturan R-CUR tetap dijalankan mesin.

Jalankan:
    uv run --no-project --with pyarrow --with pydantic --with pyyaml --with pymupdf \
        --with numpy python scripts/prepare_v04.py
"""

from __future__ import annotations

import csv
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biotrace_core.config import load_rules  # noqa: E402
from biotrace_core.io.loaders import read_fasta, read_table  # noqa: E402
from biotrace_core.models import Taxon  # noqa: E402
from biotrace_core.reference.curate import curate_records, write_reference  # noqa: E402
from biotrace_core.reference.store import ReferenceIndex, coverage  # noqa: E402
from scripts.analyze_tropis import (  # noqa: E402
    binomial,
    latest,
    load_fishbase,
    load_genbank,
    trim_mifish_fast,
    verify_fast_trim,
)

V03 = ROOT / "data/reference/v0.3"
V04 = ROOT / "data/reference/v0.4"
DATE = "2026-10-25"
CURATOR = "agent:Claude Code (instruksi Agathan)"
GENBANK_LICENSE = "GenBank-public; kebijakan NCBI"
NEW_SOURCES = [
    {
        "source_id": "SRC_GENBANK_TROPIS2026",
        "citation": "NCBI GenBank, panen 12S/mitogenom tropis 25 Okt 2026 (raw/tropis/genbank_*; docs/16)",
        "doi_or_url": "https://www.ncbi.nlm.nih.gov/nuccore",
        "type": "database",
        "license": GENBANK_LICENSE,
        "accessed_date": DATE,
    },
    {
        "source_id": "SRC_FISHBASE_V2504",
        "citation": "Froese R, Pauly D (eds) FishBase v25.04, tabel country/species/families (raw/tropis/fishbase)",
        "doi_or_url": "https://huggingface.co/datasets/cboettig/fishbase",
        "type": "database",
        "license": "CC BY-NC 4.0",
        "accessed_date": DATE,
    },
    {
        "source_id": "SRC_PERMEN_KP_19_2020",
        "citation": "Permen KP No. 19/PERMEN-KP/2020, Lampiran jenis ikan membahayakan/merugikan (BN 2020 No. 829); transkripsi data/curation/regulasi_kkp, belum dicek manusia",
        "doi_or_url": "https://www.peraturan.go.id/files/bn829-2020.pdf",
        "type": "regulation",
        "license": "peraturan perundang-undangan (UU 28/2014 Ps. 42)",
        "accessed_date": DATE,
    },
]
WATERBODY = {
    "waterbody_id": "LAUT_INDONESIA",
    "name": "Perairan laut Indonesia (checklist tingkat negara)",
    "type": "laut",
    "complex_id": "",
    "country": "ID",
}
ORIGIN = {"native": "asli", "endemic": "endemik", "introduced": "introduksi"}


_CFG = None


def _trim(seq: str) -> str:
    global _CFG
    if _CFG is None:
        _CFG = load_rules()
    return trim_mifish_fast(seq, _CFG) or ""


def main() -> None:
    if V04.exists():
        raise SystemExit(f"{V04} sudah ada; buat versi baru (A12).")
    cfg = load_rules()
    marker = "12S_MiFish_U"
    universe, names = load_fishbase()
    records = load_genbank()
    verify_fast_trim(records)
    v03 = {
        n: read_table(V03 / f"{n}.csv")
        for n in (
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
    }
    v03_fasta = read_fasta(V03 / "sequences.fasta", "ACGTNRYSWKMBDHV")
    known = {r["seq_id"] for r in v03["sequences"]}

    import pyarrow.parquet as pq

    fb = latest("fishbase")
    families = {r["FamCode"]: r for r in pq.read_table(fb / "families.parquet").to_pylist()}
    species = {r["SpecCode"]: r for r in pq.read_table(fb / "species.parquet").to_pylist()}

    taxa = {r["species_valid"]: dict(r) for r in v03["taxa"]}
    report: list[dict] = []
    rows, fasta, pending = [], {}, []
    for acc, rec in sorted(records.items()):
        if acc in known or not rec["seq"]:
            continue
        code = names.get(binomial(rec["organism"]))
        if code is None:
            continue  # tidak tercatat di Indonesia menurut FishBase atau nama tak cocok
        if not rec["voucher"]:
            report.append(
                {
                    "seq_id": acc,
                    "accession": acc,
                    "step": "R-CUR-01",
                    "result": "rejected",
                    "reason": "no_voucher",
                }
            )
            continue
        pending.append((acc, rec, code))
    with ProcessPoolExecutor() as pool:
        trimmed = list(pool.map(_trim, [p[1]["seq"] for p in pending], chunksize=50))
    for (acc, rec, code), insert in zip(pending, trimmed, strict=True):
        if not insert:
            report.append(
                {
                    "seq_id": acc,
                    "accession": acc,
                    "step": "R-CUR-05",
                    "result": "flagged",
                    "reason": "no_mifish_region",
                }
            )
            continue
        name = universe[code]["species"]
        if name not in taxa:
            sp = species.get(code, {})
            fam = families.get(sp.get("FamCode"), {})
            taxa[name] = {
                "species_valid": name,
                "genus": name.split()[0],
                "family": fam.get("Family", ""),
                "order": fam.get("Order", ""),
                "authority": sp.get("Author") or "",
                "synonyms": "",
                "in_indonesia": True,
                "cof_checked_date": "",
                "source_id": "SRC_FISHBASE_V2504",
            }
        country = rec["country"]
        rows.append(
            {
                "seq_id": acc,
                "accession": acc,
                "source_db": "genbank",
                "source_id": "SRC_GENBANK_TROPIS2026",
                "species_original": name,
                "species_valid": name,
                "marker": marker,
                "region_trimmed": True,
                "length": len(insert),
                "n_ambiguous": sum(c not in "ACGT" for c in insert),
                "voucher_level": "V2",
                "voucher_catalog": rec["voucher"],
                "voucher_institution": "",
                "specimen_country": "ID" if country == "Indonesia" else country,
                "specimen_locality": "",
                "curation_status": "accepted",
                "flags": "",
                "license": GENBANK_LICENSE,
                "date_added": DATE,
                "curator": CURATOR,
                "is_simulated": False,
            }
        )
        fasta[acc] = insert
    # v0.3 ikut dikurasi ulang bersama agar duplikat/konflik lintas versi terdeteksi (R-CUR-07/08).
    for r in v03["sequences"]:
        rows.append(r)
        fasta[r["seq_id"]] = v03_fasta[r["seq_id"]]

    # checklist nasional laut dari FishBase (file sumber ada di raw/ → primer, D-033)
    checklist = [dict(r) for r in v03["checklist"]]
    for code, sp in sorted(universe.items(), key=lambda kv: kv[1]["species"]):
        if not (sp["marine"] or sp["brackish"]) or sp["status_id"] not in ORIGIN:
            continue
        checklist.append(
            {
                "waterbody_id": "LAUT_INDONESIA",
                "species_valid": sp["species"],
                "origin_status": ORIGIN[sp["status_id"]],
                "endemic_scope": "indonesia" if sp["status_id"] == "endemic" else "",
                "source_id": "SRC_FISHBASE_V2504",
                "year_recorded": "",
                "notes": "FishBase v25.04 tabel country (C_Code 360), tingkat negara, bukan per lokasi",
                "source_quality": "primer",
            }
        )
        if sp["species"] not in taxa:
            fam = families.get(species.get(code, {}).get("FamCode"), {})
            taxa[sp["species"]] = {
                "species_valid": sp["species"],
                "genus": sp["species"].split()[0],
                "family": fam.get("Family", ""),
                "order": fam.get("Order", ""),
                "authority": species.get(code, {}).get("Author") or "",
                "synonyms": "",
                "in_indonesia": True,
                "cof_checked_date": "",
                "source_id": "SRC_FISHBASE_V2504",
            }
    checklist.sort(key=lambda r: (r["waterbody_id"], r["species_valid"]))

    # status invasif dari transkripsi Permen KP 19/2020 (spp. = seluruh genus)
    status = {r["species_valid"]: dict(r) for r in v03["status"]}
    permen = list(
        csv.DictReader(
            open(
                ROOT / "data/curation/regulasi_kkp/permen_kp_19_2020_lampiran.csv", encoding="utf-8"
            )
        )
    )
    genera = {
        r["scientific_name_verbatim"].split()[0]
        for r in permen
        if r["scientific_name_verbatim"].endswith(" spp.")
    }
    exact = {
        binomial(r["scientific_name_verbatim"][0] + r["scientific_name_verbatim"][1:].lower())
        for r in permen
    }
    for name in sorted(taxa):
        if name in exact or name.split()[0] in genera:
            row = status.setdefault(
                name,
                {
                    "species_valid": name,
                    "iucn_category": "",
                    "iucn_assessed_year": "",
                    "iucn_source_id": "",
                    "invasive_flag": True,
                    "invasive_source_id": "",
                    "version_date": DATE,
                },
            )
            row["invasive_flag"] = True
            row["invasive_source_id"] = ";".join(
                sorted(
                    {
                        *filter(None, row.get("invasive_source_id", "").split(";")),
                        "SRC_PERMEN_KP_19_2020",
                    }
                )
            )

    sources = v03["sources"] + NEW_SOURCES
    taxa_models = {n: Taxon.model_validate(t) for n, t in taxa.items()}
    manifest = {"reference_version": "v0.4", "module": "ID", "marker": marker}
    staging = ReferenceIndex(manifest, taxa_models, [], {}, {"sources": sources})
    curated, seqs, cur_report = curate_records(rows, fasta, staging, cfg, marker)
    report = sorted(report + cur_report, key=lambda r: (r["seq_id"], r["step"]))
    used = (
        {r.species_valid for r in curated}
        | {r["species_valid"] for r in checklist if not r["species_valid"].startswith("alias:")}
        | {r["species_valid"] for r in v03["taxa"]}
    )
    taxa_out = [taxa[n] for n in sorted(used) if n in taxa]
    tables = {
        "sequences": [r.model_dump() for r in curated],
        "taxa": taxa_out,
        "waterbodies": v03["waterbodies"] + [WATERBODY],
        "checklist": checklist,
        "status": [status[k] for k in sorted(status)],
        "aliases": v03["aliases"],
        "complexes": v03["complexes"],
        "introductions": v03["introductions"],
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
    tables["curation_report"] = report
    n_id = sum(r.specimen_country == "ID" for r in curated)
    from collections import Counter

    reasons = Counter(f"{r['result']} {r['reason']}" for r in report)
    notes = (
        "Dari v0.3 (D-034) + panen GenBank tropis (docs/16), D-035 Diusulkan. Panen per spesies "
        "air tawar/laut dan aksesi dari paper BELUM lengkap saat versi ini dibangun (gangguan NCBI); "
        "versi berikutnya menambah sisanya. "
        f"Sekuens diterima {len(curated)} dari {len({r.species_valid for r in curated})} spesies; "
        f"spesimen bertanda Indonesia {n_id}. Ditolak/ditandai: "
        + "; ".join(f"{k}: {v}" for k, v in sorted(reasons.items()))
        + ". Voucher: V2 hanya bila /specimen_voucher ada (tanpa header REFERENCE, rekaman tanpa voucher ditolak). "
        "Pemotongan MiFish lewat trim_mifish_fast (setara trim_mifish). LAUT_INDONESIA = checklist FishBase "
        "tingkat negara (spesies laut/payau). Status invasif dari transkripsi Permen KP 19/2020 yang belum dicek manusia. "
        "Usulan tim, belum dikalibrasi ahli."
    )
    write_reference(V04, "v0.4", "ID", marker, tables, seqs, notes=notes, created=DATE)
    print(notes)


if __name__ == "__main__":
    main()
