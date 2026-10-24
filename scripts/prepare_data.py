"""Local source adapters [MVP]. No downloads, no taxonomy inferred from memory."""

import argparse
import csv
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from statistics import median

from biotrace_core.config import ROOT, load_rules
from biotrace_core.io.loaders import read_table
from biotrace_core.models import ReferenceSequence, Taxon
from biotrace_core.reference.curate import curate_records, write_reference
from biotrace_core.reference.store import ReferenceIndex, coverage


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


# ------------------------------------------------------------------ v0.3 (docs/13, D-034)

MALILI_RAW = ROOT / "raw/malili12s_mitohelper"
TEAM_RAW = ROOT / "raw/bagus_ref_v0.1"
V03_DATE = "2026-10-25"
V03_CURATOR = "agent:Claude (Bagus Athallah)"
GENBANK_LICENSE = "GenBank-public; kebijakan NCBI"
LAKE_IDS = {"Matano": "MATANO", "Mahalona": "MAHALONA", "Towuti": "TOWUTI"}
# Baris tabel tim tingkat "Kompleks Malili" mencakup tiga danau yang dicakup tabel itu.
COMPLEX_LAKES = ["MATANO", "MAHALONA", "TOWUTI"]
NEWS_SOURCES = {"SRC_MONGABAY2018", "SRC_BISNIS2025"}
# Kutipan di kolom sumber tabel tim -> source_id. Teks kutipan apa adanya; rincian bibliografi
# yang tidak tercantum di tabel tim atau dokumen tim tidak ditambahkan dari ingatan (A1).
SOURCE_PATTERNS = [
    ("Kottelat 1990", "SRC_KOTTELAT1990"),
    ("Kottelat 1991", "SRC_KOTTELAT1991"),
    ("Herder dkk. 2006", "SRC_HERDER2006"),
    ("FEOW 750", "SRC_FEOW750"),
    ("Weber & de Beaufort 1922", "SRC_WEBER1922"),
    ("Boulenger 1897", "SRC_BOULENGER1897"),
    ("ensiklopedia Danau Matano", "SRC_ENSIKLOPEDIA_MATANO"),
    ("Hedianto & Sentosa 2019", "SRC_HEDIANTO2019"),
    ("Mongabay 2018", "SRC_MONGABAY2018"),
    ("Bisnis.com 2025", "SRC_BISNIS2025"),
    ("FishBase", "SRC_FISHBASE"),
]
UNVERIFIED = "dikutip di tabel kurasi tim (raw/bagus_ref_v0.1); file sumber belum ada di raw/"


def _source(source_id: str, citation: str, url: str, kind: str, license_: str = "") -> dict:
    return {
        "source_id": source_id,
        "citation": citation,
        "doi_or_url": url,
        "type": kind,
        "license": license_ or "tidak diketahui; file sumber tidak didistribusikan",
        "accessed_date": V03_DATE,
    }


SOURCES_V03 = [
    _source(
        "SRC_MITOHELPER2026",
        "Lim SJ, Thompson LR (2021) Mitohelper, Environmental DNA; data 12S Juli 2026, "
        "repo aomlomics/mitohelper commit f3d92c7 (raw/malili12s_mitohelper)",
        "https://github.com/aomlomics/mitohelper; https://doi.org/10.5281/zenodo.21326269",
        "database",
        "tidak tercantum di repo; data dari GenBank dan MitoFish",
    ),
    _source(
        "SRC_GENBANK",
        "NCBI GenBank nucleotide: esummary (2026-10-24) dan header flat file (2026-10-25) untuk "
        "aksesi kandidat Malili (raw/malili12s_mitohelper/genbank, genbank_flat)",
        "https://www.ncbi.nlm.nih.gov/nuccore",
        "database",
        GENBANK_LICENSE,
    ),
    _source(
        "SRC_GBIF",
        "GBIF species API dan occurrence search country=ID, diambil 2026-10-24 "
        "(raw/malili12s_mitohelper/gbif/gbif_species_indonesia.json)",
        "https://api.gbif.org/v1/",
        "database",
        "lisensi per dataset GBIF",
    ),
    _source(
        "SRC_GBIF_IUCN",
        "IUCN Red List via GBIF species API (species/{key}/iucnRedListCategory), diambil "
        "2026-10-24 (raw/malili12s_mitohelper/gbif/gbif_species_indonesia.json)",
        "https://api.gbif.org/v1/",
        "database",
        "lisensi per dataset GBIF/IUCN",
    ),
    _source(
        "SRC_BAGUS_REF_V01",
        "Tabel kurasi tim BagusAth/BIOTRACE commit 5a407e4 (raw/bagus_ref_v0.1): alias louhan "
        "dan daftar invasif disusun agent; perlu tinjauan ahli",
        "https://github.com/BagusAth/BIOTRACE",
        "team_curation",
        "tabel tim",
    ),
    _source(
        "SRC_HERDER2006",
        "Herder dkk. 2006, checklist Telmatherinidae Malili, Verh. Ges. Ichthyol. 5:139-163 "
        f"(sitasi mengikuti docs/04 §6); {UNVERIFIED}",
        "",
        "peer_reviewed",
    ),
    _source("SRC_KOTTELAT1990", f"Kottelat 1990; {UNVERIFIED}", "", "journal_unverified"),
    _source("SRC_KOTTELAT1991", f"Kottelat 1991; {UNVERIFIED}", "", "journal_unverified"),
    _source("SRC_WEBER1922", f"Weber & de Beaufort 1922; {UNVERIFIED}", "", "book"),
    _source("SRC_BOULENGER1897", f"Boulenger 1897; {UNVERIFIED}", "", "journal_unverified"),
    _source("SRC_FEOW750", f"FEOW, ekoregion 750 Malili Lakes; {UNVERIFIED}", "", "database"),
    _source(
        "SRC_ENSIKLOPEDIA_MATANO",
        f"Ringkasan ensiklopedia Danau Matano; {UNVERIFIED}",
        "",
        "database",
    ),
    _source(
        "SRC_HEDIANTO2019",
        "Hedianto & Sentosa 2019, Jurnal Penelitian Perikanan Indonesia: komunitas ikan dan "
        f"louhan di Danau Matano (survei 2015-2016); {UNVERIFIED}",
        "",
        "peer_reviewed",
    ),
    _source("SRC_FISHBASE", f"FishBase, sebaran Sulawesi; {UNVERIFIED}", "", "database"),
    _source(
        "SRC_MONGABAY2018",
        f"Mongabay 2018, nasib danau-danau Malili (mengutip studi 2013); {UNVERIFIED}",
        "",
        "news",
    ),
    _source(
        "SRC_BISNIS2025",
        f"Bisnis.com 2025, kolaborasi ekologis di lingkar nikel Sorowako; {UNVERIFIED}",
        "",
        "news",
    ),
]


def _zip_text(path: Path, suffix: str) -> str:
    """Isi satu anggota arsip ZIP (.qza/.zip) tanpa mengekstrak ke raw/ (A12)."""
    with zipfile.ZipFile(path) as archive:
        name = next(n for n in sorted(archive.namelist()) if n.endswith(suffix))
        return archive.read(name).decode("utf-8")


def _parse_fasta(text: str) -> dict[str, str]:
    seqs: dict[str, str] = {}
    key = ""
    for line in text.splitlines():
        if line.startswith(">"):
            key = line[1:].split()[0]
            seqs[key] = ""
        elif key:
            seqs[key] += line.strip().upper()
    return seqs


def _binomial(name: str) -> bool:
    parts = name.split()
    return (
        len(parts) == 2
        and parts[0][:1].isupper()
        and parts[0].isalpha()
        and parts[1].isalpha()
        and parts[1].islower()
        and parts[1] not in {"sp", "spp", "cf", "aff"}
    )


def _qualifiers(text: str) -> dict[str, str]:
    return {
        key: value.replace("\n", " ").strip()
        for key, value in re.findall(r'/(\w+)="([^"]*)"', text)
        if key in {"specimen_voucher", "country", "geo_loc_name", "organism", "isolate"}
    }


def _malili_metadata() -> dict[str, dict]:
    """esummary (semua aksesi) + header flat file (aksesi yang esummary-nya kurang)."""
    meta: dict[str, dict] = {}
    for path in sorted((MALILI_RAW / "genbank").glob("esummary_*.json")):
        result = json.loads(path.read_text(encoding="utf-8"))["result"]
        for uid in result["uids"]:
            doc = result[uid]
            names = (doc.get("subtype") or "").split("|")
            values = (doc.get("subname") or "").split("|")
            q = dict(zip(names, values, strict=False))
            meta[doc["caption"]] = {
                "organism": doc.get("organism", ""),
                "voucher": q.get("specimen_voucher", ""),
                "country": q.get("country") or q.get("geo_loc_name") or "",
                "journals": [],
            }
    for path in sorted((MALILI_RAW / "genbank_flat").glob("headers_*.gb")):
        for record in path.read_text(encoding="utf-8").split("\n//"):
            found = re.search(r"^ACCESSION\s+(\S+)", record, re.M)
            if not found:
                continue
            q = _qualifiers(record)
            row = meta.setdefault(found.group(1), {"organism": "", "voucher": "", "country": ""})
            row["voucher"] = row["voucher"] or q.get("specimen_voucher", "")
            row["country"] = row["country"] or q.get("country") or q.get("geo_loc_name") or ""
            row["organism"] = row["organism"] or q.get("organism", "")
            row["journals"] = [
                re.sub(r"\s+", " ", j).strip()
                for j in re.findall(r"^\s+JOURNAL\s+(.+?)(?=^\S|^\s{2}\w)", record, re.M | re.S)
            ]
    return meta


def _published(journals: list[str]) -> bool:
    """V3: REFERENCE terbit di jurnal (bukan Unpublished/Direct Submission/tesis/paten)."""
    skip = ("Unpublished", "Submitted", "Thesis", "Patent", "In press")
    return any(j and not j.startswith(skip) for j in journals)


def _source_ids(text: str) -> list[str]:
    return sorted({sid for pattern, sid in SOURCE_PATTERNS if pattern in text})


def prepare_indonesia_v03() -> Path:
    """v0.2 + data repo Bagus (docs/13 langkah 4, D-034) [MVP].

    Sekuens dari arsip mitohelper untuk 896 aksesi kandidat Malili; voucher dan negara dari
    esummary/header GenBank; in_indonesia dari checklist v0.2, tabel tim, atau GBIF country=ID.
    Semua sekuens lewat curate_records (R-CUR, termasuk pemotongan MiFish dan R-CUR-08).
    Baris checklist tabel tim masuk sebagai sumber sekunder/berita; baris primer v0.2 tetap.
    """
    path = ROOT / "data/reference/v0.3"
    if path.exists():
        return path
    cfg = load_rules()
    marker = "12S_MiFish_U"
    v02 = {name: read_table(ROOT / f"data/reference/v0.2/{name}.csv") for name in TABLES_V02}
    team_checklist = read_table(TEAM_RAW / "checklist_malili.csv")
    team_status = read_table(TEAM_RAW / "status.csv")
    team_alias = read_table(TEAM_RAW / "alias.csv")
    gbif = json.loads((MALILI_RAW / "gbif/gbif_species_indonesia.json").read_text(encoding="utf-8"))

    # kandidat dan sekuens (arsip mitohelper; daftar aksesi dari arsip kandidat Audit Dataset)
    candidates_zip = MALILI_RAW / "biotrace_ref_malili_v0.1.zip"
    candidate_rows = list(
        csv.DictReader(io.StringIO(_zip_text(candidates_zip, "_kandidat_taksonomi.csv")))
    )
    qza = MALILI_RAW / "mitohelper/QIIME-compatible"
    mito_seqs = _parse_fasta(_zip_text(qza / "12S-seqs-derep-uniq.qza", "dna-sequences.fasta"))
    mito_tax = {}
    for line in _zip_text(qza / "12S-tax-derep-uniq.qza", "taxonomy.tsv").splitlines()[1:]:
        acc, lineage = line.split("\t")[:2]
        ranks = dict(p.split("__", 1) for p in lineage.split(";") if "__" in p)
        mito_tax[acc] = ranks
    meta = _malili_metadata()

    # taxa: hanya nama binomial; in_indonesia dari sumber yang tercatat
    team_names = {r["spesies"]: r for r in team_checklist if _binomial(r["spesies"])}
    # semua takson v0.2 diwarisi apa adanya (sumber primer), termasuk nama "cf."
    taxa: dict[str, dict] = {r["species_valid"]: dict(r) for r in v02["taxa"]}

    def add_taxon(name: str, family: str = "", order: str = "") -> None:
        if name in taxa or not _binomial(name):
            return
        if name in team_names:
            ids = _source_ids(team_names[name]["sumber"])
            taxa[name] = {
                "species_valid": name,
                "genus": name.split()[0],
                "family": family or team_names[name]["famili"],
                "order": order,
                "authority": "",
                "synonyms": "",
                "in_indonesia": True,
                "cof_checked_date": "",
                "source_id": ";".join(ids) or "SRC_BAGUS_REF_V01",
            }
            return
        count = (gbif.get(name) or {}).get("jumlah_kemunculan_id")
        taxa[name] = {
            "species_valid": name,
            "genus": name.split()[0],
            "family": family,
            "order": order,
            "authority": "",
            "synonyms": "",
            "in_indonesia": bool(count),
            "cof_checked_date": "",
            "source_id": "SRC_GBIF" if count else "SRC_GENBANK",
        }

    rows, fasta, report = [], {}, []
    for cand in sorted(candidate_rows, key=lambda r: r["aksesi"]):
        acc = cand["aksesi"]
        info = meta.get(acc, {})
        sequence = mito_seqs.get(acc, "")
        organism = info.get("organism") or cand["spesies"]
        ranks = mito_tax.get(acc, {})
        same_genus = ranks.get("g") == organism.split()[0]
        add_taxon(organism, ranks.get("f", "") if same_genus else "", ranks.get("o", ""))
        if info.get("voucher"):
            level = "V2"
        elif _published(info.get("journals", [])):
            level = "V3"
        else:
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
        country = info.get("country", "")
        head, _, tail = country.partition(":")
        rows.append(
            {
                "seq_id": acc,
                "accession": acc,
                "source_db": "genbank",
                "source_id": "SRC_MITOHELPER2026",
                "species_original": organism,
                "species_valid": organism,
                "marker": "mitogenome" if len(sequence) > 10000 else "12S_other",
                "region_trimmed": False,
                "length": len(sequence) or 1,
                "n_ambiguous": sum(c not in "ACGT" for c in sequence),
                "voucher_level": level,
                "voucher_catalog": info.get("voucher", ""),
                "voucher_institution": "",
                "specimen_country": "ID" if head.strip() == "Indonesia" else head.strip(),
                "specimen_locality": tail.strip(),
                "curation_status": "accepted",
                "flags": "",
                "license": GENBANK_LICENSE,
                "date_added": V03_DATE,
                "curator": V03_CURATOR,
                "is_simulated": False,
            }
        )
        fasta[acc] = sequence
    for name in team_names:
        add_taxon(name)

    # checklist: baris primer v0.2 tetap; baris tabel tim sebagai sekunder/berita
    checklist = [{**r, "source_quality": "primer"} for r in v02["checklist"]]
    primary = {(r["waterbody_id"], r["species_valid"]): r for r in checklist}
    added: dict[tuple[str, str], dict] = {}
    for r in team_checklist:
        name = "alias:louhan_hybrid" if r["spesies"] == "louhan hibrida" else r["spesies"]
        lakes = COMPLEX_LAKES if r["danau"] == "Kompleks Malili" else [LAKE_IDS[r["danau"]]]
        ids = _source_ids(r["sumber"])
        quality = "berita" if ids and set(ids) <= NEWS_SOURCES else "sekunder"
        note = f"tabel kurasi tim ({r['danau']}): {r['catatan']}; sumber: {r['sumber']}"
        if r["danau"] == "Kompleks Malili":
            note += "; baris tingkat kompleks diterapkan ke Matano, Mahalona, Towuti"
        for lake in lakes:
            key = (lake, name)
            if key in primary:
                row = primary[key]
                if row["origin_status"] != r["status"]:
                    note += f"; KONFLIK status: tabel tim {r['status']}, dipakai primer"
                row["notes"] = f"{row['notes']} | juga di {note}"
            elif key in added:
                added[key]["notes"] += f" | {note}"
                merged = set(added[key]["source_id"].split(";")) | set(ids)
                added[key]["source_id"] = ";".join(sorted(merged))
                if quality == "sekunder":
                    added[key]["source_quality"] = "sekunder"
            else:
                added[key] = {
                    "waterbody_id": lake,
                    "species_valid": name,
                    "origin_status": r["status"],
                    "endemic_scope": "",
                    "source_id": ";".join(ids),
                    "year_recorded": r["tahun"],
                    "notes": note,
                    "source_quality": quality,
                }
    checklist += [added[k] for k in sorted(added)]
    checklist.sort(key=lambda r: (r["waterbody_id"], r["species_valid"]))

    # status: IUCN lewat GBIF; invasif hanya bila kolom sumber menyebut sumber
    in_taxa = {n for n, t in taxa.items() if str(t["in_indonesia"]).lower() in {"true", "1"}}
    status = []
    for r in team_status:
        name = "alias:louhan_hybrid" if r["spesies"] == "louhan hibrida" else r["spesies"]
        if name not in in_taxa and not name.startswith("alias:"):
            continue
        inv_ids = _source_ids(r["sumber_invasif"])
        status.append(
            {
                "species_valid": name,
                "iucn_category": r["kategori_iucn"],
                "iucn_assessed_year": "",
                "iucn_source_id": "SRC_GBIF_IUCN" if r["kategori_iucn"] else "",
                "invasive_flag": r["invasif"] == "ya" and bool(inv_ids),
                "invasive_source_id": ";".join(inv_ids) if r["invasif"] == "ya" else "",
                "version_date": "2026-10-24",
            }
        )
    aliases = [
        {
            "alias_key": "louhan_hybrid",
            "alias_label_id": "kemungkinan louhan hibrida",
            "alias_label_en": "likely flowerhorn hybrid",
            "member_name": r["nama_induk"],
            "category": "hybrid_invasive",
            "source_id": "SRC_BAGUS_REF_V01",
            "reviewed_by_expert": False,
            "notes": r["catatan"],
        }
        for r in team_alias
        if r["tingkat"] == "spesies"
    ]

    # kurasi R-CUR (indeks memuat semua nama agar alasan penolakan tepat)
    taxa_models = {n: Taxon.model_validate(t) for n, t in taxa.items()}
    sources = v02["sources"] + SOURCES_V03
    manifest = {"reference_version": "v0.3", "module": "ID", "marker": marker}
    staging = ReferenceIndex(manifest, taxa_models, [], {}, {"sources": sources})
    records, seqs, curated = curate_records(rows, fasta, staging, cfg, marker)
    report = sorted(report + curated, key=lambda r: (r["seq_id"], r["step"]))

    taxa_out = [taxa[n] for n in sorted(in_taxa)]
    tables = {
        "sequences": [r.model_dump() for r in records],
        "taxa": taxa_out,
        "waterbodies": v02["waterbodies"],
        "checklist": checklist,
        "status": sorted(status, key=lambda r: r["species_valid"]),
        "aliases": sorted(aliases, key=lambda r: r["member_name"]),
        "complexes": v02["complexes"],
        "introductions": v02["introductions"],
        "sources": sorted(sources, key=lambda r: r["source_id"]),
    }
    index = ReferenceIndex(
        manifest,
        {n: Taxon.model_validate(t) for n, t in ((t["species_valid"], t) for t in taxa_out)},
        [ReferenceSequence.model_validate(r) for r in tables["sequences"]],
        seqs,
        tables,
    )
    tables["coverage"] = [r.model_dump() for r in coverage(index.select(cfg, "normal", marker))]
    tables["curation_report"] = report
    write_reference(
        path, "v0.3", "ID", marker, tables, seqs, notes=_changelog_v03(tables), created=V03_DATE
    )
    return path


TABLES_V02 = ["taxa", "waterbodies", "checklist", "introductions", "complexes", "sources"]


def _changelog_v03(tables: dict[str, list[dict]]) -> str:
    report = tables["curation_report"]
    outcome = Counter((r["result"], r["reason"]) for r in report if r["step"] != "R-CUR-07")
    accepted = [r for r in tables["sequences"] if r["curation_status"] == "accepted"]
    species = sorted({r["species_valid"] for r in accepted})
    countries = Counter(r["specimen_country"] or "kosong" for r in accepted)
    levels = Counter(r["voucher_level"] for r in accepted)
    merged = sum(r["step"] == "R-CUR-07" for r in report)
    conflict = sum("conflict" in r["flags"] for r in accepted)
    endemic = sorted(
        {r["species_valid"] for r in tables["checklist"] if r["origin_status"] == "endemik"}
    )
    lines = [
        "Dari v0.2 (D-032) + data repo BagusAth/BIOTRACE commit 5a407e4 (docs/13, D-034). "
        "Aturan r0.4 (D-033). Semua ambang usulan tim, belum dikalibrasi ahli.",
        "",
        "## Sekuens (896 aksesi kandidat Malili dari mitohelper 12S Juli 2026)",
        f"- Diterima: {len(accepted)} sekuens unik dari {len(species)} spesies "
        f"(V2 {levels.get('V2', 0)}, V3 {levels.get('V3', 0)}); {merged} aksesi digabung "
        f"sebagai duplikat (R-CUR-07); {conflict} bertanda konflik lintas spesies (R-CUR-08).",
        f"- Asal spesimen yang diterima: {dict(sorted(countries.items()))}. Spesimen luar "
        "Indonesia/asal kosong bertanda specimen_outside_indonesia; klaim yang hanya bertumpu "
        "padanya tidak pernah safe (R-DEC-09).",
        "- Ditolak/ditandai menurut alasan:",
    ]
    lines += [
        f"  - {result} {reason}: {n}"
        for (result, reason), n in sorted(outcome.items())
        if result != "accepted" or reason != "passed"
    ]
    lines += [
        "- no_voucher: tanpa /specimen_voucher dan semua REFERENCE berupa Unpublished/Direct "
        "Submission/tesis. Dicatat di curation_report.csv, tidak di sequences.csv, karena enum "
        "voucher_level tidak punya nilai yang benar untuk kasus ini.",
        "",
        "## Checklist, status, alias",
        "- Semua baris v0.2 tetap (source_quality primer). Baris tabel tim masuk sebagai "
        "source_quality sekunder (sumber ilmiah, file belum di raw/) atau berita (Mongabay, "
        "Bisnis.com). Baris tingkat Kompleks Malili diterapkan ke Matano, Mahalona, Towuti. "
        "Duplikat terhadap baris primer dicatat di notes baris primer.",
        f"- Spesies endemik di checklist: {len(endemic)}; spesies endemik dengan sekuens "
        f"diterima: {len(set(endemic) & set(species))}.",
        "- Nama tidak dinormalisasi: Pterygoplichthys pardalis (tabel tim/GenBank) terpisah dari "
        "Pterygoplichthys cf. pardalis dan Lyposarcus pardalis (v0.2); perlu tinjauan ahli.",
        "- Status: kategori IUCN lewat GBIF; invasive_flag hanya bila kolom sumber tabel tim "
        "menyebut sumber. Permen KP 19/2020 belum dicek.",
        "- Alias louhan: hanya nama spesies induk dari tabel tim (reviewed_by_expert=false); baris "
        "tingkat genus tidak dipakai karena mesin mencocokkan alias per spesies.",
        "- jalur_masuk.csv tabel tim tidak diimpor (tanpa tingkat danau; ringkasan, bukan "
        "transkripsi); introductions.csv tetap dari v0.2.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dataset", choices=["indonesia", "indonesia_v02", "indonesia_v03", "guyana"]
    )
    args = parser.parse_args()
    print(
        {
            "indonesia": initialize_indonesia,
            "indonesia_v02": prepare_indonesia_v02,
            "indonesia_v03": prepare_indonesia_v03,
            "guyana": prepare_guyana,
        }[args.dataset]()
    )
