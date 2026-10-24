"""Analisis celah referensi ikan Indonesia dari panen raw/tropis/ (docs/16) [P1].

Eksplorasi, BUKAN kamus berversi: tidak ada sekuens yang masuk data/reference/. Hasil ke
data/curation/tropis_gap_v1/. Nama spesies hanya dari file sumber di raw/ (A14): FishBase
sebagai penyebut, GenBank/BOLD/GBIF sebagai bukti ketersediaan.

Jalankan (pyarrow hanya untuk membaca FishBase):
    uv run --no-project --with pyarrow --with pydantic --with pyyaml \
        python scripts/analyze_tropis.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biotrace_core.config import load_rules  # noqa: E402
from biotrace_core.reference.trim import trim_mifish  # noqa: E402

TROPIS = ROOT / "raw/tropis"
OUT = ROOT / "data/curation/tropis_gap_v1"
TIERS = {
    "Indonesia": "1_ID",
    **{c: "2_Sundaland" for c in ("Malaysia", "Singapore", "Brunei")},
    **{c: "3_Wallacea_Sahul" for c in ("Timor-Leste", "Papua New Guinea", "Philippines")},
    **{
        c: "4_Asia_Tenggara_daratan"
        for c in ("Thailand", "Viet Nam", "Vietnam", "Cambodia", "Laos", "Myanmar")
    },
}
TIER_ORDER = [
    "1_ID",
    "2_Sundaland",
    "3_Wallacea_Sahul",
    "4_Asia_Tenggara_daratan",
    "5_lain",
    "6_asal_tidak_diketahui",
]
# Kode provinsi ISO 3166-2:ID (FishBase countrysub) dikelompokkan per pulau besar.
ISLANDS = {
    "Sumatra": {"AC", "SU", "SB", "RI", "KR", "JA", "SS", "BE", "LA", "BB"},
    "Jawa": {"JK", "JB", "JT", "YO", "JI", "BT"},
    "Bali_Nusa_Tenggara": {"BA", "NB", "NT"},
    "Kalimantan": {"KB", "KT", "KS", "KI", "KU"},
    "Sulawesi": {"SA", "ST", "SN", "SG", "SR", "GO"},
    "Maluku": {"MA", "MU"},
    "Papua": {"PA", "PB", "PS", "PT", "PE", "PD"},
}
SKIP_STATUS = {"misidentification", "error", "questionable"}


def latest(dataset: str) -> Path | None:
    folders = sorted((TROPIS / dataset).glob("*/manifest.json"))
    return folders[-1].parent if folders else None


def binomial(name: str) -> str:
    parts = name.replace("cf. ", "").replace("aff. ", "").split()
    return f"{parts[0]} {parts[1]}" if len(parts) >= 2 and parts[1].islower() else ""


# ---------------------------------------------------------------- penyebut FishBase


def load_fishbase() -> tuple[dict[int, dict], dict[str, int]]:
    import pyarrow.parquet as pq

    folder = latest("fishbase")
    table = lambda n: pq.read_table(folder / f"{n}.parquet").to_pylist()  # noqa: E731
    species = {r["SpecCode"]: r for r in table("species")}
    families = {r["FamCode"]: r for r in table("families")}
    universe: dict[int, dict] = {}
    for row in table("country"):
        if str(row["C_Code"]).strip() != "360" or row.get("Status") in SKIP_STATUS:
            continue
        sp = species.get(row["SpecCode"])
        if not sp or not sp.get("Genus") or not sp.get("Species"):
            continue
        fam = families.get(sp.get("FamCode"), {})
        universe[row["SpecCode"]] = {
            "spec_code": row["SpecCode"],
            "species": f"{sp['Genus']} {sp['Species']}",
            "family": fam.get("Family", ""),
            "order": fam.get("Order", ""),
            "status_id": row.get("Status") or "",
            "freshwater": int(row.get("Freshwater") == 1),
            "brackish": int(row.get("Brackish") == 1),
            "marine": int(row.get("Saltwater") == 1),
            "islands": set(),
        }
    for row in table("countrysub"):
        code = str(row.get("CSub_Code") or "")
        if row["SpecCode"] in universe and code.startswith("ID-"):
            for island, provinces in ISLANDS.items():
                if code[3:] in provinces:
                    universe[row["SpecCode"]]["islands"].add(island)
    names = {v["species"]: k for k, v in universe.items()}
    for row in table("synonyms"):  # nama lama/salah eja di GenBank tetap terhubung ke SpecCode
        key = f"{row.get('SynGenus') or ''} {row.get('SynSpecies') or ''}".strip()
        if row.get("SpecCode") in universe and len(key.split()) == 2:
            names.setdefault(key, row["SpecCode"])
    return universe, names


# ---------------------------------------------------------------- GenBank


def _qualifiers(doc: dict) -> dict[str, str]:
    return dict(
        zip(
            (doc.get("subtype") or "").split("|"),
            (doc.get("subname") or "").split("|"),
            strict=False,
        )
    )


def _read_fasta(path: Path) -> dict[str, str]:
    seqs, key, buf = {}, None, []
    for line in path.read_text("utf-8", errors="replace").splitlines():
        if line.startswith(">"):
            if key:
                seqs[key] = "".join(buf)
            key, buf = line[1:].split()[0].split(".")[0], []
        else:
            buf.append(line.strip())
    if key:
        seqs[key] = "".join(buf)
    return seqs


def load_genbank() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for dataset in (
        "genbank_country",
        "genbank_species_freshwater",
        "genbank_species_marine",
        "genbank_cited",
    ):
        folder = latest(dataset)
        if not folder:
            continue
        for summary in sorted(folder.glob("*.esummary.json")):
            result = json.loads(summary.read_text("utf-8"))["result"]
            fasta = summary.with_name(summary.name.replace(".esummary.json", ".fasta"))
            seqs = _read_fasta(fasta) if fasta.is_file() else {}
            for uid in result["uids"]:
                doc = result[uid]
                acc = doc["caption"]
                if acc in records:
                    continue
                q = _qualifiers(doc)
                place = q.get("geo_loc_name") or q.get("country") or ""
                records[acc] = {
                    "accession": acc,
                    "organism": doc.get("organism", ""),
                    "country": place.split(":")[0].strip(),
                    "voucher": q.get("specimen_voucher", ""),
                    "slen": int(doc.get("slen") or 0),
                    "title": doc.get("title", ""),
                    "seq": seqs.get(acc, ""),
                    "dataset": dataset,
                }
    return records


_CFG = None


def _primer_hits(strand: bytes, primer: bytes, limit: int) -> list[tuple[int, int]]:
    """(posisi, mismatch) setiap jendela penuh dengan mismatch <= limit (vektor numpy)."""
    import numpy as np

    if len(strand) < len(primer):
        return []
    windows = np.lib.stride_tricks.sliding_window_view(np.frombuffer(strand, np.uint8), len(primer))
    mismatches = (windows != np.frombuffer(primer, np.uint8)).sum(axis=1)
    return [(int(i), int(mismatches[i])) for i in np.flatnonzero(mismatches <= limit)]


def trim_mifish_fast(sequence: str, cfg) -> str | None:  # noqa: ANN001
    """Setara trim_mifish (R-CUR-05) dengan pencarian primer tervektor.

    Kesetaraan diuji terhadap fungsi resmi pada sampel setiap kali skrip dijalankan
    (lihat verify_fast_trim); bila berbeda, skrip berhenti.
    """
    from biotrace_core.reference.trim import reverse_complement

    forward = str(cfg.curation["forward_primer"]).encode()
    reverse = reverse_complement(str(cfg.curation["reverse_primer"])).encode()
    limit = int(cfg.curation["primer_max_mismatches"])
    choices = []
    for strand in (sequence.upper(), reverse_complement(sequence.upper())):
        raw = strand.encode("ascii", "replace")
        f_hits, r_hits = _primer_hits(raw, forward, limit), _primer_hits(raw, reverse, limit)
        for start, f_mm in f_hits:
            for end, r_mm in r_hits:
                if end > start + len(forward):
                    choices.append((f_mm + r_mm, start, end, strand[start + len(forward) : end]))
    return min(choices)[3] if choices else None


def _mifish(seq: str) -> int:
    """Panjang insert MiFish (0 bila tidak ada)."""
    global _CFG
    if _CFG is None:
        _CFG = load_rules()
    found = trim_mifish_fast(seq, _CFG)
    return len(found) if found else 0


def verify_fast_trim(records: dict[str, dict], n: int = 120) -> None:
    """Bandingkan trim_mifish_fast dengan trim_mifish resmi pada sampel deterministik."""
    cfg = load_rules()
    sample = sorted(a for a, r in records.items() if r["seq"])[:: max(1, len(records) // n)][:n]
    for acc in sample:
        seq = records[acc]["seq"]
        if trim_mifish_fast(seq, cfg) != trim_mifish(seq.upper(), cfg):
            raise SystemExit(f"trim_mifish_fast berbeda dari trim_mifish untuk {acc}")
    print(f"trim_mifish_fast identik dengan trim_mifish pada {len(sample)} sampel")


def mifish_lengths(records: dict[str, dict]) -> dict[str, int]:
    cache_path = OUT / "cache_mifish.json"
    cache = json.loads(cache_path.read_text("utf-8")) if cache_path.is_file() else {}
    todo = [a for a, r in records.items() if a not in cache and r["seq"]]
    OUT.mkdir(parents=True, exist_ok=True)
    if todo:
        verify_fast_trim(records)
        with ProcessPoolExecutor() as pool:
            for i in range(0, len(todo), 2000):  # simpan bertahap; bisa dilanjutkan
                chunk = todo[i : i + 2000]
                seqs = [records[a]["seq"] for a in chunk]
                for acc, n in zip(chunk, pool.map(_mifish, seqs, chunksize=50), strict=True):
                    cache[acc] = n
                cache_path.write_text(json.dumps(cache), "utf-8")
                print(f"  MiFish: {min(i + 2000, len(todo))}/{len(todo)}")
    return cache


# ---------------------------------------------------------------- BOLD, GBIF, regulasi, OAI


def load_bold(names: dict[str, int]) -> dict[int, Counter]:
    folder = latest("bold")
    out: dict[int, Counter] = defaultdict(Counter)
    if not folder:
        return out
    csv.field_size_limit(10**9)
    with open(folder / "teleostei_global.tsv", encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            code = names.get(binomial(row.get("species") or ""))
            if code is None:
                continue
            country = row.get("country/ocean") or ""
            c = out[code]
            c["coi_total"] += 1
            c["coi_ID"] += country == "Indonesia"
            c["coi_ID_museum"] += country == "Indonesia" and bool(row.get("museumid"))
            c["coi_tetangga"] += TIERS.get(country, "") in {"2_Sundaland", "3_Wallacea_Sahul"}
            if country == "Indonesia" and row.get("inst"):
                c["inst:" + row["inst"]] += 1
    return out


def load_gbif(names: dict[str, int]) -> dict[int, dict]:
    folder = latest("gbif")
    out: dict[int, dict] = {}
    if (
        not folder
        or not (folder / "ID_species_counts.json").is_file()
        or not (folder / "species_names.json").is_file()
    ):
        return out
    counts = json.loads((folder / "ID_species_counts.json").read_text("utf-8"))["counts"]
    meta = json.loads((folder / "species_names.json").read_text("utf-8"))
    for key, n in counts["all"].items():
        code = names.get(binomial((meta.get(key) or {}).get("canonicalName") or ""))
        if code is not None:
            cur = out.setdefault(code, {"gbif_ID": 0, "gbif_ID_specimen": 0})
            cur["gbif_ID"] += n
            cur["gbif_ID_specimen"] += counts["preserved_specimen"].get(key, 0)
    return out


def regulation_species(names: dict[str, int]) -> list[dict]:
    """Kandidat spesies dari teks PDF regulasi; WAJIB dicek manusia terhadap lampiran."""
    import pymupdf

    folder = latest("regulasi")
    rows = []
    if not folder:
        return rows
    for pdf in sorted(folder.glob("*.pdf")):
        doc = pymupdf.open(pdf)
        for page_no, page in enumerate(doc, 1):
            for m in sorted(set(re.findall(r"\b([A-Z][a-z]+ [a-z]{3,})\b", page.get_text()))):
                if m in names:
                    rows.append(
                        {
                            "regulation": pdf.stem,
                            "page": page_no,
                            "name_in_pdf": m,
                            "spec_code": names[m],
                            "checked_by_human": "tidak",
                        }
                    )
    return rows


FISH_WORDS = re.compile(
    r"\b(ikan|fish|fishes|ichthy|pisces|teleost|cyprinid|gobi|rasbora|betta|oryzias|telmatherin|ikhtio)",
    re.I,
)
DNA_WORDS = re.compile(
    r"\b(DNA|barcod|COI|12S|16S|cytochrome|mitokondria|mitochondri|eDNA|metabarcod|filogen|phylogen|sekuens|sequence)",
    re.I,
)
ACCESSION = re.compile(r"\b([A-Z]{1,2}\d{5,6}|[A-Z]{2}_?\d{6,8})\b")


def journal_articles() -> list[dict]:
    folder = latest("oai_jurnal")
    out = []
    if not folder:
        return out
    ns = {
        "oai": "http://www.openarchives.org/OAI/2.0/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    }
    import xml.etree.ElementTree as ET

    for path in sorted(folder.glob("*.xml")):
        journal = path.stem.rsplit("_", 1)[0]
        try:
            root = ET.fromstring(path.read_bytes())
        except ET.ParseError:
            continue
        for rec in root.iter("{http://www.openarchives.org/OAI/2.0/}record"):
            md = rec.find("oai:metadata/oai_dc:dc", ns)
            if md is None:
                continue
            get = lambda tag, md=md: [e.text or "" for e in md.findall(f"dc:{tag}", ns)]  # noqa: E731
            text = " ".join(get("title") + get("subject") + get("description"))
            if not (FISH_WORDS.search(text) and DNA_WORDS.search(text)):
                continue
            urls = [u for u in get("identifier") if u.startswith("http")]
            out.append(
                {
                    "journal": journal,
                    "title": (get("title") or [""])[0].strip(),
                    "date": (get("date") or [""])[0][:10],
                    "url": urls[0] if urls else "",
                    "rights": "; ".join(r.strip() for r in get("rights"))[:200],
                    "accession_like_in_abstract": ";".join(sorted(set(ACCESSION.findall(text))))[
                        :200
                    ],
                }
            )
    return sorted(out, key=lambda r: (r["journal"], r["date"], r["title"]))


# ---------------------------------------------------------------- penemuan sumber


def cited_accessions() -> dict[str, list[str]]:
    """Aksesi -> PMCID artikel ikan Indonesia yang menyebutnya (Europe PMC)."""
    folder = latest("europepmc")
    out: dict[str, list[str]] = defaultdict(list)
    if not folder or not (folder / "accession_annotations.json").is_file():
        return out
    for pmcid, accs in json.loads(
        (folder / "accession_annotations.json").read_text("utf-8")
    ).items():
        for a in accs:
            out[a.split(".")[0]].append(pmcid)
    return out


def brin_datasets() -> list[dict]:
    folder = latest("brin_rin")
    rows = []
    if not folder:
        return rows
    for path in sorted(folder.glob("dataset_*.json")):
        data = json.loads(path.read_text("utf-8")).get("data", {})
        version = data.get("latestVersion", {})
        fields = {
            f["typeName"]: f["value"]
            for f in version.get("metadataBlocks", {}).get("citation", {}).get("fields", [])
            if isinstance(f.get("value"), str)
        }
        files = version.get("files", [])
        names = [f["dataFile"]["filename"] for f in files]
        rows.append(
            {
                "persistent_id": data.get("protocol", "")
                + ":"
                + data.get("authority", "")
                + "/"
                + data.get("identifier", ""),
                "title": fields.get("title", ""),
                "published": (data.get("publicationDate") or "")[:10],
                "files": len(files),
                "files_open": sum(not f.get("restricted") for f in files),
                "files_restricted": sum(bool(f.get("restricted")) for f in files),
                "accessions_in_filenames": ";".join(
                    sorted(set(ACCESSION.findall(" ".join(names))))
                )[:300],
                "url": "https://data.brin.go.id/dataset.xhtml?persistentId="
                + data.get("protocol", "")
                + ":"
                + data.get("authority", "")
                + "/"
                + data.get("identifier", ""),
            }
        )
    return sorted(rows, key=lambda r: (r["files_open"] == 0, r["title"]))


def repository_datasets() -> list[dict]:
    folder = latest("repositori")
    rows: dict[str, dict] = {}
    if not folder:
        return []
    if (folder / "zenodo.json").is_file():
        for h in json.loads((folder / "zenodo.json").read_text("utf-8")):
            md = h.get("metadata", {})
            rows[h.get("doi") or str(h.get("id"))] = {
                "repository": "zenodo",
                "title": md.get("title", ""),
                "doi": h.get("doi", ""),
                "date": md.get("publication_date", ""),
                "license": (md.get("license") or {}).get("id", ""),
                "url": h.get("links", {}).get("self_html", ""),
            }
    for path in sorted(folder.glob("dryad_*.json")):
        for d in json.loads(path.read_text("utf-8")).get("_embedded", {}).get("stash:datasets", []):
            doi = (d.get("identifier") or "").replace("doi:", "")
            rows.setdefault(
                doi,
                {
                    "repository": "dryad",
                    "title": d.get("title", ""),
                    "doi": doi,
                    "date": d.get("publicationDate", ""),
                    "license": d.get("license", ""),
                    "url": "https://doi.org/" + doi,
                },
            )
    for path in sorted(folder.glob("figshare_*.json")):
        for d in json.loads(path.read_text("utf-8")):
            text = d.get("title", "")
            if not FISH_WORDS.search(text):
                continue
            rows.setdefault(
                d.get("doi") or str(d.get("id")),
                {
                    "repository": "figshare",
                    "title": text,
                    "doi": d.get("doi", ""),
                    "date": (d.get("published_date") or "")[:10],
                    "license": "",
                    "url": d.get("url_public_html", ""),
                },
            )
    return sorted(rows.values(), key=lambda r: (r["repository"], r["title"]))


# ---------------------------------------------------------------- utama


def tier(country: str) -> str:
    if not country:
        return "6_asal_tidak_diketahui"
    return TIERS.get(country, "5_lain")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = load_rules()
    weights = cfg.priorities  # bobot R-GAP-01 (YAML), dipakai ulang untuk prioritas panen
    universe, names = load_fishbase()
    print(f"FishBase Indonesia: {len(universe)} spesies; {len(names)} nama termasuk sinonim")
    records = load_genbank()
    print(f"GenBank: {len(records)} rekaman unik")
    lengths = mifish_lengths(records)
    per: dict[int, dict] = defaultdict(
        lambda: {
            "gb": 0,
            "gb_mifish": 0,
            "tiers": Counter(),
            "voucher_mifish": 0,
            "best": "7_tidak_ada",
        }
    )
    unmatched = Counter()
    for acc, r in records.items():
        code = names.get(binomial(r["organism"]))
        if code is None:
            unmatched[r["organism"]] += 1
            continue
        p = per[code]
        p["gb"] += 1
        if lengths.get(acc, 0) > 0:
            t = tier(r["country"])
            p["gb_mifish"] += 1
            p["tiers"][t] += 1
            p["voucher_mifish"] += bool(r["voucher"])
            p["best"] = min(p["best"], t)
    bold = load_bold(names)
    gbif = load_gbif(names)
    regs = regulation_species(names)
    protected = {
        r["spec_code"]
        for r in regs
        if "dilindungi" in r["regulation"] or "belida" in r["regulation"]
    }
    rows = []
    for code, sp in sorted(universe.items(), key=lambda kv: kv[1]["species"]):
        p, b, g = per.get(code, {}), bold.get(code, Counter()), gbif.get(code, {})
        best = p.get("best", "7_tidak_ada")
        endemic = sp["status_id"] == "endemic"
        no_id_ref = best != "1_ID"
        score = (
            weights.get("endemic", 0) * endemic
            + weights.get("threatened", 0) * (code in protected)
            + weights.get("observed_reference_gap", 0) * no_id_ref
        )
        insts = sorted((k[5:] for k in b if k.startswith("inst:")), key=lambda k: -b["inst:" + k])
        rows.append(
            {
                "spec_code": code,
                "species": sp["species"],
                "family": sp["family"],
                "order": sp["order"],
                "status_id": sp["status_id"],
                "freshwater": sp["freshwater"],
                "brackish": sp["brackish"],
                "marine": sp["marine"],
                "islands": ";".join(sorted(sp["islands"])),
                "kepmen_dilindungi_kandidat": int(code in protected),
                "genbank_12s_mito": p.get("gb", 0),
                "genbank_mifish": p.get("gb_mifish", 0),
                "mifish_best_tier": best,
                "mifish_tiers": ";".join(
                    f"{k}:{v}" for k, v in sorted(p.get("tiers", Counter()).items())
                ),
                "mifish_with_voucher": p.get("voucher_mifish", 0),
                "bold_coi_total": b["coi_total"],
                "bold_coi_ID": b["coi_ID"],
                "bold_coi_ID_museum": b["coi_ID_museum"],
                "bold_coi_tetangga": b["coi_tetangga"],
                "bold_ID_institutions": ";".join(insts[:3]),
                "gbif_ID": g.get("gbif_ID", 0),
                "gbif_ID_specimen": g.get("gbif_ID_specimen", 0),
                "priority_score": score,
            }
        )
    fields = list(rows[0])
    with open(OUT / "species_coverage.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    targets = sorted(
        (
            r
            for r in rows
            if r["mifish_best_tier"] != "1_ID"
            and (r["status_id"] == "endemic" or r["kepmen_dilindungi_kandidat"])
        ),
        key=lambda r: (-r["priority_score"], -r["bold_coi_ID_museum"], r["species"]),
    )
    with open(OUT / "priority_targets.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        w.writerows(targets)
    with open(OUT / "regulation_species_candidates.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            ["regulation", "page", "name_in_pdf", "spec_code", "checked_by_human"],
            lineterminator="\n",
        )
        w.writeheader()
        w.writerows(regs)
    articles = journal_articles()
    with open(OUT / "journal_articles_fish_dna.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            ["journal", "title", "date", "url", "rights", "accession_like_in_abstract"],
            lineterminator="\n",
        )
        w.writeheader()
        w.writerows(articles)
    for name, rows_out in (
        ("brin_rin_datasets.csv", brin_datasets()),
        ("repository_datasets.csv", repository_datasets()),
    ):
        if rows_out:
            with open(OUT / name, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, list(rows_out[0]), lineterminator="\n")
                w.writeheader()
                w.writerows(rows_out)
    cited = cited_accessions()
    candidates = []
    for acc, r in sorted(records.items()):
        if acc in cited and not r["country"]:
            code = names.get(binomial(r["organism"]))
            candidates.append(
                {
                    "accession": acc,
                    "organism": r["organism"],
                    "spec_code": code if code is not None else "",
                    "mifish": int(lengths.get(acc, 0) > 0),
                    "voucher": r["voucher"],
                    "cited_in_pmcid": ";".join(sorted(set(cited[acc]))),
                    "title": r["title"][:150],
                }
            )
    if candidates:
        with open(
            OUT / "indonesian_specimen_candidates_from_papers.csv",
            "w",
            encoding="utf-8",
            newline="",
        ) as f:
            w = csv.DictWriter(f, list(candidates[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(candidates)
    sra = latest("sra_edna")
    if sra and (sra / "fastq_urls.tsv").is_file():
        (OUT / "edna_fastq_indonesia.tsv").write_bytes((sra / "fastq_urls.tsv").read_bytes())
    with open(OUT / "genbank_unmatched_organisms.csv", "w", encoding="utf-8", newline="") as f:
        f.write(
            "organism,records\n"
            + "".join(
                f'"{k}",{v}\n' for k, v in sorted(unmatched.items(), key=lambda kv: (-kv[1], kv[0]))
            )
        )

    def table(subset: list[dict]) -> dict:
        return {
            t: sum(r["mifish_best_tier"] == t for r in subset) for t in [*TIER_ORDER, "7_tidak_ada"]
        }

    groups = {
        "semua": rows,
        "air_tawar_payau": [r for r in rows if r["freshwater"] or r["brackish"]],
        "air_tawar_endemik": [r for r in rows if r["freshwater"] and r["status_id"] == "endemic"],
        "laut_saja": [r for r in rows if r["marine"] and not (r["freshwater"] or r["brackish"])],
        "introduksi": [r for r in rows if r["status_id"] == "introduced"],
        "kepmen_dilindungi_kandidat": [r for r in rows if r["kepmen_dilindungi_kandidat"]],
    }
    islands = {
        island: table([r for r in rows if island in r["islands"].split(";") and r["freshwater"]])
        for island in ISLANDS
    }
    summary = {
        "generated_from": {
            d: str(latest(d).relative_to(ROOT)) if latest(d) else None
            for d in (
                "fishbase",
                "genbank_country",
                "genbank_species_freshwater",
                "genbank_species_marine",
                "bold",
                "gbif",
                "oai_jurnal",
                "sra_edna",
                "regulasi",
            )
        },
        "fishbase_species_ID": len(universe),
        "genbank_records": len(records),
        "genbank_records_with_mifish": sum(1 for a in records if lengths.get(a, 0) > 0),
        "genbank_records_unmatched_to_fishbase_ID": sum(unmatched.values()),
        "coverage_by_group": {k: {"n": len(v), **table(v)} for k, v in groups.items()},
        "freshwater_by_island_fishbase_countrysub": islands,
        "bold_species_with_coi_from_ID": sum(1 for r in rows if r["bold_coi_ID"]),
        "priority_targets": len(targets),
        "journal_articles_fish_dna": len(articles),
        "articles_by_journal": dict(Counter(a["journal"] for a in articles)),
        "regulation_candidates": len(regs),
        "cited_accessions_europepmc": len(cited),
        "indonesian_specimen_candidates_from_papers": len(candidates),
        "notes": [
            "Eksplorasi otomatis; nama FishBase (CC BY-NC) tanpa tinjauan ahli. Bukan kamus berversi.",
            "MiFish = trim_mifish_fast, setara trim_mifish (R-CUR-05; primer dan mismatch dari rules YAML), diverifikasi identik pada sampel setiap run.",
            "Tingkat asal dari kualifier GenBank country/geo_loc_name; kosong = asal tidak diketahui (sering spesimen Indonesia tanpa label, mis. Telmatherina).",
            "Prioritas memakai bobot priorities rules YAML (endemic, threatened untuk kandidat Kepmen dilindungi, observed_reference_gap untuk tanpa referensi MiFish Indonesia).",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), "utf-8")
    print(json.dumps(summary["coverage_by_group"], indent=1))


if __name__ == "__main__":
    main()
