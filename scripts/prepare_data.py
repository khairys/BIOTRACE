"""Local source adapters [MVP]. No downloads, no taxonomy inferred from memory."""

import argparse
from pathlib import Path
from statistics import median

from biotrace_core.config import ROOT, load_rules
from biotrace_core.io.loaders import read_table
from biotrace_core.reference.curate import write_reference


def initialize_indonesia() -> Path:
    path = ROOT / "data/reference/v0.1"
    if path.exists():
        return path
    tables = {
        key: []
        for key in [
            "sequences",
            "taxa",
            "waterbodies",
            "checklist",
            "status",
            "aliases",
            "complexes",
            "introductions",
            "sources",
        ]
    }
    tables["waterbodies"] = [
        {
            "waterbody_id": key,
            "name": f"Danau {name}",
            "type": "danau",
            "complex_id": "MALILI",
            "country": "ID",
        }
        for key, name in [
            ("MATANO", "Matano"),
            ("MAHALONA", "Mahalona"),
            ("TOWUTI", "Towuti"),
            ("LONTOA", "Lontoa"),
            ("MASAPI", "Masapi"),
        ]
    ]
    write_reference(
        path,
        "v0.1",
        "ID",
        "12S_MiFish_U",
        tables,
        {},
        notes="Snapshot kosong. Kamus nyata belum siap; kandidat Stelbrink tidak lolos screening MiFish. Tidak ada nama spesies atau checklist yang dikarang. Gunakan kamus SIMULASI terpisah untuk demo.",
    )
    return path


def prepare_guyana() -> Path:
    cfg = load_rules()
    source = ROOT / "raw/french_guiana_12s/Data_12S Ref library_Fish Guiana.csv"
    path = ROOT / "data/external/french_guiana_12s/v1"
    if path.exists():
        raise ValueError("Modul sudah ada; versi tidak ditimpa.")
    rows = read_table(source, ";")
    middle = median(len(r["12S sequence"]) for r in rows)
    taxa, fasta, records, checklist, report = {}, {}, [], {}, []
    for row in rows:
        genus = row["Genus"]
        species = (
            row["Species"]
            if row["Species"].startswith(genus + " ")
            else genus + " " + row["Species"]
        )
        accession = row["NCBI GenBank accession number"]
        sequence = row["12S sequence"].upper()
        taxa[species] = {
            "species_valid": species,
            "genus": genus,
            "family": row["Family"],
            "order": row["Order"],
            "source_id": "SRC_GUYANA2026",
            "in_indonesia": False,
            "is_simulated": False,
        }
        reasons = []
        if len(sequence) < float(cfg.curation["min_length_fraction"]) * middle:
            reasons.append("short")
        if sequence.count("N") / len(sequence) > float(cfg.curation["max_n_fraction"]):
            reasons.append("ambiguous")
        record = {
            "seq_id": accession,
            "accession": accession,
            "source_db": "paper_supplement",
            "source_id": "SRC_GUYANA2026",
            "species_original": species,
            "species_valid": species,
            "marker": "12S_Teleo1_V5",
            "region_trimmed": True,
            "length": len(sequence),
            "n_ambiguous": sum(c not in "ACGT" for c in sequence),
            "voucher_level": "V2",
            "voucher_catalog": row["Specimen identification code"],
            "voucher_institution": row["Institution storing the voucher"],
            "specimen_country": "GF",
            "specimen_locality": row["River basin"],
            "curation_status": "rejected" if reasons else "accepted",
            "flags": ";".join(reasons),
            "license": "CC0",
            "date_added": "2026-10-24",
            "curator": "agent:Codex",
            "is_simulated": False,
        }
        records.append(record)
        fasta[accession] = sequence
        checklist[species] = {
            "waterbody_id": "GF_LIBRARY",
            "species_valid": species,
            "origin_status": "tercatat_di_pustaka",
            "endemic_scope": "",
            "source_id": "SRC_GUYANA2026",
            "year_recorded": "",
            "notes": "Agregasi pustaka untuk LOSO; bukan checklist lengkap 415 spesies.",
            "is_simulated": False,
        }
        report.append(
            {
                "seq_id": accession,
                "accession": accession,
                "step": "R-CUR-06",
                "result": record["curation_status"],
                "reason": ";".join(reasons) or "passed_published_fragment_checks",
            }
        )
    tables = {
        "sequences": records,
        "taxa": list(taxa.values()),
        "waterbodies": [
            {
                "waterbody_id": "GF_LIBRARY",
                "name": "Pustaka uji Guyana (agregasi validasi)",
                "type": "validation_scope",
                "country": "GF",
            }
        ],
        "checklist": list(checklist.values()),
        "status": [],
        "aliases": [],
        "complexes": [],
        "introductions": [],
        "sources": read_table(ROOT / "raw/french_guiana_12s/sources.csv"),
        "curation_report": report,
    }
    write_reference(
        path,
        "external:GF-v1",
        "GF",
        "12S_Teleo1_V5",
        tables,
        fasta,
        notes="Sumber CSV Figshare v1/CC0. Label takson dipertahankan dari sumber, bukan validasi nama oleh ahli. V2 dari kode spesimen/institusi, bukan V1. Fragmen 12S publik mencakup Teleo1/12S-V5; tidak dipotong/diklaim sebagai MiFish. Checklist uji hanya spesies yang ada di pustaka, bukan penyebut 415 spesies regional. Hanya mode validasi; parameter r0.2 belum dikalibrasi untuk marker ini.",
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=["indonesia", "guyana"])
    args = parser.parse_args()
    print(initialize_indonesia() if args.dataset == "indonesia" else prepare_guyana())
