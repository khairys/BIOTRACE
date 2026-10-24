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


SOURCES_V02 = [
    {
        "source_id": "SRC_HERDER2012",
        "citation": "Herder F, Schliewen UK, Geiger MF, Hadiaty RK, Gray SM, McKinnon JS, Walter RP, Pfaender J (2012) Alien invasion in Wallace's Dreamponds: records of the hybridogenic 'flowerhorn' cichlid in Lake Matano, with an annotated checklist of fish species introduced to the Malili Lakes system in Sulawesi. Aquatic Invasions 7(4): 521-535",
        "doi_or_url": "https://www.researchgate.net/publication/232708663",
        "type": "peer_reviewed",
        "license": "Open Access; (c) 2012 The Author(s); journal compilation (c) 2012 REABIC",
        "accessed_date": "2026-10-25",
    },
    {
        "source_id": "SRC_TANTU2007",
        "citation": "Tantu FY, Nilawati J (2007) The exotic fish and fisheries in Lake Matano South Sulawesi. Vol. 4 No. 7, Desember 2007, ISSN 1829-7374, Himpunan Mahasiswa Pascasarjana Sulawesi Tengah-Bogor; Tabel 1 hlm. 33",
        "doi_or_url": "https://www.researchgate.net/publication/370417162",
        "type": "journal_unverified",
        "license": "tidak diketahui; PDF tidak didistribusikan ulang",
        "accessed_date": "2026-10-25",
    },
]


def prepare_indonesia_v02() -> Path:
    """Checklist + introductions from transcribed Herder 2012 / Tantu 2007 tables [MVP].

    Names are kept as printed in the sources (no Catalog of Fishes normalisation, A14);
    rows the sources give only at genus level or as common names stay out of the checklist.
    No sequences: neither source contains MiFish references.
    """
    path = ROOT / "data/reference/v0.2"
    if path.exists():
        return path
    rows = read_table(ROOT / "data/curation/malili_introduced_v0.2/transcription.csv")
    kept = [r for r in rows if r["include"] == "ya"]
    taxa: dict[str, dict] = {}
    for r in sorted(kept, key=lambda r: (r["source_id"] != "SRC_HERDER2012", r["species_valid"])):
        name = r["species_valid"]
        if name.startswith("alias:") or name in taxa:
            continue
        verbatim = r["name_verbatim"]
        authority = (
            verbatim[verbatim.find("(") :]
            if "(" in verbatim and r["source_id"] == "SRC_HERDER2012"
            else ""
        )
        synonyms = "Trichogaster " + name.split()[1] if name.startswith("Trichopodus ") else ""
        taxa[name] = {
            "species_valid": name,
            "genus": name.split()[0],
            "family": r["family_verbatim"],
            "order": "",
            "authority": authority.strip("()")
            if not authority.startswith("(Trichogaster)")
            else "",
            "synonyms": synonyms,
            "in_indonesia": True,
            "cof_checked_date": "",
            "source_id": r["source_id"],
        }
    grouped: dict[tuple[str, str], list[dict]] = {}
    for r in kept:
        grouped.setdefault((r["waterbody_id"], r["species_valid"]), []).append(r)
    checklist, introductions = [], []
    for (waterbody, name), group in sorted(grouped.items()):
        sources = ";".join(sorted({g["source_id"] for g in group}))
        years = sorted({g["first_record_year"] for g in group if g["first_record_year"]})
        notes = " | ".join(f"{g['source_id']} {g['location']}: {g['notes']}" for g in group)
        checklist.append(
            {
                "waterbody_id": waterbody,
                "species_valid": name,
                "origin_status": "introduksi",
                "endemic_scope": "",
                "source_id": sources,
                "year_recorded": years[0] if years else "",
                "notes": notes,
            }
        )
        pathways = sorted({g["pathway"] for g in group} - {"tidak_diketahui"})
        introductions.append(
            {
                "species_valid": name,
                "waterbody_id": waterbody,
                "pathway": ";".join(pathways) or "tidak_diketahui",
                "first_record_year": years[0] if years else "",
                "source_id": sources,
            }
        )
    previous = read_table(ROOT / "data/reference/v0.1/waterbodies.csv")
    tables = {
        "sequences": [],
        "taxa": [taxa[k] for k in sorted(taxa)],
        "waterbodies": previous,
        "checklist": checklist,
        "status": [],
        "aliases": [],
        "complexes": [],
        "introductions": introductions,
        "sources": SOURCES_V02,
    }
    write_reference(
        path,
        "v0.2",
        "ID",
        "12S_MiFish_U",
        tables,
        {},
        notes=(
            "Dari v0.1. Menambah checklist ikan introduksi Malili dari Herder dkk. 2012 "
            "(Appendix 1 dan teks) dan Tantu & Nilawati 2007 (Tabel 1), ditranskripsi di "
            "data/curation/malili_introduced_v0.2/transcription.csv. Nama sesuai sumber; "
            "sinonimi dan normalisasi Catalog of Fishes belum ditinjau ahli. Spesies endemik "
            "belum dimasukkan karena checklist Herder 2006 belum tersedia. Belum ada sekuens "
            "MiFish; alias louhan tanpa nama spesies induk; status IUCN/invasif belum diisi."
        ),
        created="2026-10-25",
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", choices=["indonesia", "indonesia_v02", "guyana"])
    args = parser.parse_args()
    print(
        {
            "indonesia": initialize_indonesia,
            "indonesia_v02": prepare_indonesia_v02,
            "guyana": prepare_guyana,
        }[args.dataset]()
    )
