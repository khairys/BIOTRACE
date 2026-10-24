"""Panen data ikan tropis/Indonesia ke raw/tropis/ (docs/14, docs/16) [P1].

Dipanggil lewat scripts/fetch_data.py (aturan A13), bukan langsung. Mesin inti tidak
pernah memanggil modul ini (A8).

Prinsip:
- Setiap dataset ditulis ke folder baru raw/tropis/<dataset>/<tanggal>/ (A12: tidak menimpa).
- Unduhan bisa dilanjutkan: file yang sudah lengkap dilewati.
- Jumlah record per batch diverifikasi terhadap jumlah dari server; batch tidak lengkap = galat.
- manifest.json menyimpan kueri persis, URL, tanggal, lisensi yang dilaporkan sumber, dan
  SHA-256 lengkap setiap file. Berkas besar tidak dikomit; manifest dikomit.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "raw"
ROOT = RAW / "tropis"
LOG = RAW / "DOWNLOAD_LOG.md"
UA = {"User-Agent": "BioTrace-harvest/1.0 (research; github.com/khairys/BIOTRACE)"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
NCBI_PAUSE = 0.4  # < 3 permintaan/detik tanpa API key (kebijakan NCBI)

# Negara tropis yang relevan dengan biogeografi Indonesia (nama sesuai daftar negara INSDC).
SUNDALAND = ["Malaysia", "Singapore", "Brunei"]
WALLACEA_SAHUL = ["Timor-Leste", "Papua New Guinea", "Philippines"]
MAINLAND_SEA = ["Thailand", "Viet Nam", "Cambodia", "Laos", "Myanmar"]
COUNTRIES = ["Indonesia", *SUNDALAND, *WALLACEA_SAHUL, *MAINLAND_SEA]
ISO2 = {
    "Indonesia": "ID",
    "Malaysia": "MY",
    "Singapore": "SG",
    "Brunei": "BN",
    "Timor-Leste": "TL",
    "Papua New Guinea": "PG",
    "Philippines": "PH",
    "Thailand": "TH",
    "Viet Nam": "VN",
    "Cambodia": "KH",
    "Laos": "LA",
    "Myanmar": "MM",
}
MARKER_TERM = (
    '((12S[All Fields] OR "12S ribosomal RNA"[All Fields] OR "small subunit ribosomal RNA"'
    "[All Fields]) OR (mitochondrion[filter] AND 14000:20000[SLEN]))"
)
# Kueri per spesies/aksesi juga menangkap rakitan genom utuh (scaffold > 20 kb) yang anotasinya
# menyebut 12S; unduhan FASTA-nya membengkak dan habis waktu. MiFish ada di mitogenom, jadi
# panjang dibatasi <= 20 kb (diuji 25 Okt 2026: "Betta splendens" 15 rekaman, 1 di atas 20 kb).
MARKER_TERM_CAPPED = f"({MARKER_TERM}) AND 50:20000[SLEN]"
FISHBASE_VERSION = "v25.04"
FISHBASE_TABLES = [
    "country",
    "countrysub",
    "countref",
    "species",
    "synonyms",
    "families",
    "genera",
    "orders",
    "ecosystemcountry",
]
OAI_JOURNALS = {
    "jurnal_iktiologi_indonesia": "https://www.jurnal-iktiologi.org/index.php/jii/oai",
    "biodiversitas": "https://smujo.id/biodiv/oai",
    "treubia": "https://ejournal.brin.go.id/treubia/oai",
    "biotropia": "https://journal.biotrop.org/index.php/biotropia/oai",
    # Ditambahkan setelah uji Identify 25 Okt 2026 (docs/16 §2).
    "limnotek": "https://ejournal.brin.go.id/limnotek/oai",
    "zoo_indonesia": "https://ejournal.brin.go.id/zoo_indonesia/oai",
    "berita_biologi": "https://ejournal.brin.go.id/berita_biologi/oai",
    "marine_research_indonesia": "https://ejournal.brin.go.id/mri/oai",
    "oldi": "https://ejournal.brin.go.id/oldi/oai",
    "ilmu_kelautan_undip": "https://ejournal.undip.ac.id/index.php/ijms/oai",
    "jitkt_ipb": "https://journal.ipb.ac.id/index.php/jurnalikt/oai",
}
SRA_TERM = (
    '(Indonesia[All Fields]) AND (eDNA[All Fields] OR "environmental DNA"[All Fields] OR '
    "metabarcoding[All Fields]) AND (fish[All Fields] OR 12S[All Fields] OR MiFish[All Fields] "
    "OR teleost*[All Fields])"
)
ENA_FIELDS = (
    "run_accession,sample_accession,experiment_title,library_strategy,instrument_platform,"
    "fastq_ftp,fastq_bytes,fastq_md5,sample_title,collection_date,country,location,lat,lon"
)
ZENODO = {
    "mifish_rcrux_2025": "17664847",  # 12S MiFish V5-V6, rCRUX nt + MitoFish (Nov 2025)
    "mitohelper_2025": "17602902",  # Mitohelper reference datasets (Nov 2025, +-2,2 GB)
}


# ---------------------------------------------------------------- utilitas


def _request(url: str, data: dict | None = None, timeout: int = 300) -> bytes:
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    last: Exception | None = None
    for attempt in range(9):  # server publik kadang membalas 429/5xx; jeda total +-7 menit
        try:
            req = urllib.request.Request(url, data=body, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except OSError as exc:
            last = exc
            time.sleep(min(60, 2 ** (attempt + 1)))
    raise RuntimeError(f"gagal setelah 9 percobaan: {url}") from last


def _json(url: str, data: dict | None = None) -> dict:
    return json.loads(_request(url, data).decode("utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".partial")
    temp.write_bytes(data)
    for attempt in range(20):  # Windows: file tujuan bisa sedang dibuka proses lain
        try:
            temp.replace(path)
            return
        except PermissionError:
            time.sleep(0.5 * (attempt + 1))
    temp.replace(path)


def _download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".partial")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=900) as r, open(temp, "wb") as f:
        for block in iter(lambda: r.read(1 << 20), b""):
            f.write(block)
    temp.replace(path)


class Run:
    """One dated harvest folder plus its manifest (A12: a new folder per day)."""

    def __init__(self, dataset: str, source: str, license_note: str, method: str) -> None:
        self.dataset = dataset
        self.folder = ROOT / dataset / dt.date.today().isoformat()
        self.folder.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.folder / "manifest.json"
        old = (
            json.loads(self.manifest_path.read_text("utf-8"))
            if self.manifest_path.is_file()
            else {}
        )
        self.manifest = {
            "dataset": dataset,
            "source": source,
            "license_reported_by_source": license_note,
            "method": method,
            "started": old.get("started", dt.datetime.now().isoformat(timespec="seconds")),
            "queries": old.get("queries", {}),
            "files": old.get("files", {}),
            "notes": old.get("notes", []),
        }

    def has(self, name: str) -> bool:
        return name in self.manifest["files"] and (self.folder / name).is_file()

    def add(self, name: str, url: str, records: int | None = None, **extra: object) -> None:
        path = self.folder / name
        self.manifest["files"][name] = {
            "url": url,
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
            "records": records,
            **extra,
        }
        self.save()

    def save(self) -> None:
        self.manifest["updated"] = dt.datetime.now().isoformat(timespec="seconds")
        _write(self.manifest_path, json.dumps(self.manifest, ensure_ascii=False, indent=1).encode())

    def finish(self, summary: str) -> None:
        self.manifest["finished"] = dt.datetime.now().isoformat(timespec="seconds")
        self.manifest["summary"] = summary
        self.save()
        rel = self.manifest_path.relative_to(RAW)
        line = (
            f"| {self.dataset} | {rel} | {self.manifest['source']} | {dt.date.today()} | "
            f"manifest {_sha256(self.manifest_path)} | {self.manifest['license_reported_by_source']}"
            f" | {summary} |\n"
        )
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line)
        print(f"  ✓ {rel}: {summary}")


# ---------------------------------------------------------------- FishBase


def fishbase() -> None:
    """FishBase v25.04 (parquet, HuggingFace cboettig/fishbase); hash diverifikasi ke LFS oid."""
    base = f"https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/fb/{FISHBASE_VERSION}/parquet"
    api = f"https://huggingface.co/api/datasets/cboettig/fishbase/tree/main/data/fb/{FISHBASE_VERSION}/parquet"
    run = Run(
        "fishbase",
        f"FishBase {FISHBASE_VERSION} via HuggingFace cboettig/fishbase",
        "CC BY-NC 4.0 (kartu dataset); pemakaian komersial perlu izin FishBase",
        "Unduh tabel parquet apa adanya; SHA-256 dibandingkan dengan LFS oid HuggingFace.",
    )
    oids = {
        x["path"].split("/")[-1]: x.get("lfs", {}).get("oid")
        for x in json.loads(_request(api).decode())
    }
    for table in FISHBASE_TABLES:
        name = f"{table}.parquet"
        if run.has(name):
            continue
        _download(f"{base}/{name}", run.folder / name)
        digest = _sha256(run.folder / name)
        if oids.get(name) and oids[name] != digest:
            raise RuntimeError(f"{name}: SHA-256 tidak cocok dengan LFS oid")
        run.add(name, f"{base}/{name}", lfs_oid_match=bool(oids.get(name)))
    run.finish(f"{len(FISHBASE_TABLES)} tabel parquet FishBase {FISHBASE_VERSION}")


def fishbase_species(
    country_code: str = "360", habitats: tuple[str, ...] = ("Freshwater", "Brackish")
) -> list[str]:
    """Nama spesies FishBase untuk sebuah negara (kode FishBase), dari file raw terbaru.

    Dipakai sebagai daftar target GenBank (A14: nama berasal dari file sumber di raw/).
    Memerlukan pyarrow (grup dependensi `harvest`).
    """
    import pyarrow.parquet as pq

    folder = sorted((ROOT / "fishbase").glob("*/country.parquet"))[-1].parent
    country = pq.read_table(folder / "country.parquet").to_pylist()
    species = {r["SpecCode"]: r for r in pq.read_table(folder / "species.parquet").to_pylist()}
    names = set()
    for row in country:
        if str(row["C_Code"]).strip() != country_code:
            continue
        if row.get("Status") in {"misidentification", "error", "questionable"}:
            continue
        if habitats and not any(row.get(h) == 1 for h in habitats):
            continue
        sp = species.get(row["SpecCode"])
        if sp and sp.get("Genus") and sp.get("Species"):
            names.add(f"{sp['Genus']} {sp['Species']}")
    return sorted(names)


# ---------------------------------------------------------------- GenBank


def _esearch(term: str) -> tuple[int, str, str]:
    r = _json(
        EUTILS + "esearch.fcgi",
        {
            "db": "nuccore",
            "term": term,
            "usehistory": "y",
            "retmax": 0,
            "retmode": "json",
            "tool": "biotrace_harvest",
        },
    )["esearchresult"]
    return int(r["count"]), r["webenv"], r["querykey"]


def _genbank_query(run: Run, label: str, term: str, page: int = 250) -> int:
    """esummary (JSON) + FASTA for every record of `term`; counts verified per page."""
    count, webenv, key = _esearch(term)
    run.manifest["queries"][label] = {"term": term, "count": count}
    run.save()
    time.sleep(NCBI_PAUSE)
    for start in range(0, count, page):
        expected = min(page, count - start)
        stem = f"{label}_{start // page:04d}"
        common = {
            "db": "nuccore",
            "query_key": key,
            "WebEnv": webenv,
            "retstart": start,
            "retmax": page,
            "tool": "biotrace_harvest",
        }
        if not run.has(f"{stem}.esummary.json"):
            data = _request(EUTILS + "esummary.fcgi", {**common, "retmode": "json"})
            got = len(json.loads(data)["result"].get("uids", []))
            if got != expected:
                raise RuntimeError(f"{stem}: esummary {got} dari {expected}")
            _write(run.folder / f"{stem}.esummary.json", data)
            run.add(f"{stem}.esummary.json", EUTILS + "esummary.fcgi", got, query=label)
            time.sleep(NCBI_PAUSE)
        if not run.has(f"{stem}.fasta"):
            data = _request(
                EUTILS + "efetch.fcgi", {**common, "rettype": "fasta", "retmode": "text"}
            )
            got = data.count(b">")
            if got != expected:
                raise RuntimeError(f"{stem}: FASTA {got} dari {expected}")
            _write(run.folder / f"{stem}.fasta", data)
            run.add(f"{stem}.fasta", EUTILS + "efetch.fcgi", got, query=label)
            time.sleep(NCBI_PAUSE)
    return count


def genbank_country() -> None:
    """12S + mitogenom ikan bersirip-jari per negara tropis (asal spesimen = kualifier country)."""
    run = Run(
        "genbank_country",
        "NCBI GenBank nuccore (E-utilities)",
        "Kebijakan NCBI: tanpa batasan pemakaian, tanpa jaminan hak pihak ketiga",
        'esearch per negara: Actinopterygii[Organism] AND "<negara>"[country] AND '
        + MARKER_TERM
        + "; esummary JSON + FASTA per 250 record.",
    )
    total = 0
    for country in COUNTRIES:
        total += _genbank_query(
            run,
            ISO2[country] + "_s20k",
            f'Actinopterygii[Organism] AND "{country}"[country] AND {MARKER_TERM_CAPPED}',
        )
    run.finish(f"{total} rekaman 12S/mitogenom dari {len(COUNTRIES)} negara")


def _genbank_species(dataset: str, names: list[str], description: str) -> None:
    run = Run(
        dataset,
        "NCBI GenBank nuccore (E-utilities); daftar nama dari FishBase raw/tropis/fishbase",
        "Kebijakan NCBI: tanpa batasan pemakaian, tanpa jaminan hak pihak ketiga",
        f"{description}. Nama dibagi per 60 lalu digabung OR sebagai [Organism] AND "
        + MARKER_TERM_CAPPED
        + " (label *_s20k; label batchNNN lama tanpa batas panjang, gagal)",
    )
    run.manifest["target_species"] = len(names)
    total = 0
    for i in range(0, len(names), 60):
        chunk = names[i : i + 60]
        organisms = " OR ".join(f'"{n}"[Organism]' for n in chunk)
        total += _genbank_query(
            run, f"b{i // 60:03d}_s20k", f"({organisms}) AND {MARKER_TERM_CAPPED}"
        )
    run.finish(f"{total} rekaman untuk {len(names)} spesies target")


def genbank_species_freshwater() -> None:
    """12S + mitogenom (negara mana pun) untuk spesies air tawar/payau Indonesia versi FishBase."""
    _genbank_species(
        "genbank_species_freshwater",
        fishbase_species("360", ("Freshwater", "Brackish")),
        "Spesies FishBase C_Code 360 (Indonesia) dengan Freshwater atau Brackish = 1, "
        "tanpa status misidentification/error/questionable",
    )


def genbank_species_marine() -> None:
    """12S + mitogenom untuk spesies laut Indonesia versi FishBase (lebih besar; opsional)."""
    fresh = set(fishbase_species("360", ("Freshwater", "Brackish")))
    names = [n for n in fishbase_species("360", ("Saltwater",)) if n not in fresh]
    _genbank_species(
        "genbank_species_marine",
        names,
        "Spesies FishBase C_Code 360 dengan Saltwater = 1 dan bukan air tawar/payau",
    )


# ---------------------------------------------------------------- Europe PMC (aksesi dari paper)

EPMC = "https://www.ebi.ac.uk/europepmc/"
EPMC_QUERY = (
    "(Indonesia OR Sulawesi OR Sumatra OR Kalimantan OR Borneo OR Java OR Papua OR Maluku) "
    'AND (fish OR fishes) AND (GenBank OR "accession number" OR "accession numbers" OR BOLD) '
    "AND OPEN_ACCESS:y"
)
ACCESSION_RE = r"^(?:[A-Z]\d{5}|[A-Z]{2}\d{6}|[A-Z]{2}\d{8})(?:\.\d+)?$"  # format INSDC nukleotida


def europepmc() -> None:
    """Artikel open access ikan Indonesia + nomor aksesi yang disebut di teksnya.

    Anotasi Europe PMC (type=Accession Numbers) menandai aksesi di teks lengkap. Rentang
    seperti "KJ667771–KJ667865" hanya tercatat ujung-ujungnya; tidak diperluas di sini.
    """
    run = Run(
        "europepmc",
        "Europe PMC REST search + Annotations API",
        "Metadata Europe PMC terbuka; teks artikel mengikuti lisensi artikel (CC/OA)",
        "search query="
        + EPMC_QUERY
        + "; annotationsByArticleIds type=Accession Numbers per 8 PMCID",
    )
    if not run.has("articles.json"):
        cursor, articles = "*", []
        while True:
            page = _json(
                EPMC
                + "webservices/rest/search?"
                + urllib.parse.urlencode(
                    {
                        "query": EPMC_QUERY,
                        "format": "json",
                        "pageSize": 1000,
                        "resultType": "lite",
                        "cursorMark": cursor,
                    }
                )
            )
            articles += page["resultList"]["result"]
            nxt = page.get("nextCursorMark")
            if not nxt or nxt == cursor or not page["resultList"]["result"]:
                break
            cursor = nxt
            time.sleep(0.5)
        _write(run.folder / "articles.json", json.dumps(articles, ensure_ascii=False).encode())
        run.add("articles.json", EPMC + "webservices/rest/search", len(articles))
        run.manifest["queries"]["search"] = {"query": EPMC_QUERY, "hits": len(articles)}
    articles = json.loads((run.folder / "articles.json").read_text("utf-8"))
    pmcids = sorted({a["pmcid"] for a in articles if a.get("pmcid")})
    ann_path = run.folder / "accession_annotations.json"
    annotations = json.loads(ann_path.read_text("utf-8")) if ann_path.is_file() else {}
    todo = [p for p in pmcids if p not in annotations]
    for i in range(0, len(todo), 8):
        batch = todo[i : i + 8]
        url = (
            EPMC
            + "annotations_api/annotationsByArticleIds?"
            + urllib.parse.urlencode(
                {
                    "articleIds": ",".join(f"PMC:{p}" for p in batch),
                    "type": "Accession Numbers",
                    "format": "JSON",
                }
            )
        )
        for item in json.loads(_request(url).decode("utf-8")):
            annotations[item.get("pmcid") or item.get("extId")] = sorted(
                {(x.get("exact") or "").strip() for x in item.get("annotations", [])}
            )
        for p in batch:
            annotations.setdefault(p, [])
        if i % 80 == 0:
            _write(ann_path, json.dumps(annotations).encode())
        time.sleep(0.3)
    _write(ann_path, json.dumps(annotations).encode())
    run.add(
        "accession_annotations.json",
        EPMC + "annotations_api/annotationsByArticleIds",
        len(annotations),
    )
    import re

    accs = sorted(
        {a.split(".")[0] for v in annotations.values() for a in v if re.match(ACCESSION_RE, a)}
    )
    _write(run.folder / "cited_accessions.txt", ("\n".join(accs) + "\n").encode())
    run.add("cited_accessions.txt", "turunan accession_annotations.json", len(accs))
    run.finish(
        f"{len(articles)} artikel OA, {len(pmcids)} PMCID, {len(accs)} aksesi nukleotida unik"
    )


def genbank_cited() -> None:
    """Rekaman GenBank untuk aksesi yang disebut di artikel ikan Indonesia (butuh europepmc)."""
    source = sorted((ROOT / "europepmc").glob("*/cited_accessions.txt"))[-1]
    accs = [a for a in source.read_text("utf-8").split() if a]
    run = Run(
        "genbank_cited",
        "NCBI GenBank nuccore; daftar aksesi dari " + str(source.relative_to(RAW)),
        "Kebijakan NCBI: tanpa batasan pemakaian, tanpa jaminan hak pihak ketiga",
        "esearch per 200 aksesi: (A[accn] OR B[accn] ...) AND Actinopterygii[Organism]",
    )
    total = 0
    for i in range(0, len(accs), 200):
        term = (
            "("
            + " OR ".join(f"{a}[accn]" for a in accs[i : i + 200])
            + ") AND Actinopterygii[Organism] AND 50:20000[SLEN]"
        )
        total += _genbank_query(run, f"cited{i // 200:03d}", term)
    run.finish(f"{total} rekaman ikan dari {len(accs)} aksesi yang dikutip")


# ---------------------------------------------------------------- BOLD v5


def bold() -> None:
    """BOLD v5 portal: semua rekaman publik Teleostei (COI, voucher museum, koordinat).

    API v5 mengabaikan filter geo pada query extent=full (diuji 25 Okt 2026: TSV Indonesia
    dan Malaysia identik), jadi diunduh sekali secara global dan negara disaring lokal dari
    kolom `country/ocean`.
    """
    run = Run(
        "bold",
        "BOLD Systems v5 portal API",
        "Rekaman publik BOLD; lisensi per rekaman (lihat kolom BOLD)",
        "Satu unduhan global tax:class:Teleostei (extent=full, TSV); negara disaring lokal "
        "dari kolom country/ocean.",
    )
    name = "teleostei_global.tsv"
    if not run.has(name):
        query = "tax:class:Teleostei"
        qid = _json(
            "https://portal.boldsystems.org/api/query?"
            + urllib.parse.urlencode({"query": query, "extent": "full"})
        )["query_id"]
        url = (
            f"https://portal.boldsystems.org/api/documents/{urllib.parse.quote(qid)}"
            "/download?format=tsv"
        )
        _download(url, run.folder / name)
        with open(run.folder / name, "rb") as f:
            rows = max(0, sum(1 for _ in f) - 1)
        run.manifest["queries"]["global"] = {"query": query, "records": rows}
        run.add(name, url, rows)
    run.finish(f"{run.manifest['files'][name]['records']} rekaman Teleostei global")


# ---------------------------------------------------------------- GBIF


def _gbif(path: str) -> dict:
    return _json("https://api.gbif.org/v1/" + path)


def gbif() -> None:
    """GBIF: jumlah okurensi dan spesimen museum per spesies ikan per negara + nama spesies.

    Backbone GBIF saat ini tidak memberi kelas pada ikan bersirip-jari; ordo ikan dipilih
    dinamis sebagai ordo Chordata tanpa classKey (dicatat di manifest).
    """
    run = Run(
        "gbif",
        "GBIF occurrence search API (facet) + species API",
        "Per dataset penerbit (CC0/CC BY/CC BY-NC); data agregat jumlah per spesies",
        "occurrence/search facet=speciesKey untuk ordo ikan, semua record dan "
        "basisOfRecord=PRESERVED_SPECIMEN; nama dari species/{key}",
    )
    names: dict[str, dict] = {}
    names_file = run.folder / "species_names.json"
    if names_file.is_file():
        names = json.loads(names_file.read_text("utf-8"))
    for country in ["Indonesia", *SUNDALAND, *WALLACEA_SAHUL]:
        code = ISO2[country]
        name = f"{code}_species_counts.json"
        if not run.has(name):
            orders = _gbif(
                f"occurrence/search?country={code}&phylumKey=44&limit=0&facet=orderKey&facetLimit=500"
            )
            fish = []
            for o in orders["facets"][0]["counts"]:
                s = _gbif(f"species/{o['name']}")
                if s.get("classKey") is None:
                    fish.append(
                        {
                            "orderKey": o["name"],
                            "order": s.get("scientificName"),
                            "count": o["count"],
                        }
                    )
            keys = "&".join(f"orderKey={o['orderKey']}" for o in fish)
            counts = {}
            for label, extra in [
                ("all", ""),
                ("preserved_specimen", "&basisOfRecord=PRESERVED_SPECIMEN"),
            ]:
                facet = _gbif(
                    f"occurrence/search?country={code}&{keys}{extra}&limit=0&facet=speciesKey&facetLimit=200000"
                )
                counts[label] = {c["name"]: c["count"] for c in facet["facets"][0]["counts"]}
            _write(
                run.folder / name,
                json.dumps({"country": code, "fish_orders": fish, "counts": counts}).encode(),
            )
            run.add(name, "https://api.gbif.org/v1/occurrence/search", len(counts["all"]))
        data = json.loads((run.folder / name).read_text("utf-8"))
        todo = [k for k in data["counts"]["all"] if k not in names]
        for i, key in enumerate(todo):
            s = _gbif(f"species/{key}")
            names[key] = {
                k: s.get(k)
                for k in (
                    "canonicalName",
                    "family",
                    "order",
                    "genus",
                    "taxonomicStatus",
                    "acceptedKey",
                )
            }
            if i % 200 == 199:
                _write(names_file, json.dumps(names).encode())
            time.sleep(0.05)
        _write(names_file, json.dumps(names).encode())
    run.add("species_names.json", "https://api.gbif.org/v1/species/{key}", len(names))
    run.finish(f"jumlah per spesies untuk 7 negara; {len(names)} nama spesies")


# ---------------------------------------------------------------- OAI-PMH jurnal Indonesia


def oai() -> None:
    """Metadata artikel (oai_dc) dari jurnal Indonesia lewat OAI-PMH ListRecords."""
    run = Run(
        "oai_jurnal",
        "OAI-PMH jurnal OJS Indonesia: " + ", ".join(OAI_JOURNALS),
        "Metadata OAI-PMH terbuka; isi/PDF mengikuti lisensi tiap jurnal (dc:rights)",
        "verb=ListRecords&metadataPrefix=oai_dc lalu resumptionToken sampai habis",
    )
    import re

    failed = []
    for journal, endpoint in OAI_JOURNALS.items():
        if run.manifest["queries"].get(journal, {}).get("complete"):
            continue
        token, page, records = None, 0, 0
        try:
            while True:
                name = f"{journal}_{page:04d}.xml"
                params = {
                    "verb": "ListRecords",
                    **({"resumptionToken": token} if token else {"metadataPrefix": "oai_dc"}),
                }
                url = endpoint + "?" + urllib.parse.urlencode(params)
                data = _request(url, timeout=180)
                _write(run.folder / name, data)
                n = data.count(b"<record>") + data.count(b"<record ")
                records += n
                run.add(name, url, n, journal=journal)
                m = re.search(rb"<resumptionToken[^>]*>([^<]+)</resumptionToken>", data)
                if not m:
                    break
                token, page = m.group(1).decode().strip(), page + 1
                time.sleep(1)
        except RuntimeError as exc:  # satu jurnal gagal tidak menghentikan jurnal lain
            failed.append(journal)
            run.manifest["queries"][journal] = {
                "endpoint": endpoint,
                "records": records,
                "error": str(exc),
            }
            run.save()
            continue
        run.manifest["queries"][journal] = {
            "endpoint": endpoint,
            "records": records,
            "pages": page + 1,
            "complete": True,
        }
        run.save()
    done = len(OAI_JOURNALS) - len(failed)
    run.finish(
        f"metadata OAI {done}/{len(OAI_JOURNALS)} jurnal"
        + (f"; gagal: {', '.join(failed)}" if failed else "")
    )


# ---------------------------------------------------------------- Regulasi Indonesia

# Peraturan perundang-undangan bukan ciptaan yang dilindungi (UU 28/2014 Pasal 42).
REGULATIONS = {
    "kepmen_kp_1_2021_jenis_ikan_dilindungi.pdf": (
        "https://emancing.kkp.go.id/assets/aturan/"
        "KEPMEN%20NO%201%20TAHUN%202021%20TENTANG%20JENIS%20IKAN%20YG%20DILINDUNGI.pdf"
    ),
    "permen_kp_19_2020_jenis_ikan_membahayakan_bn829.pdf": (
        "https://www.peraturan.go.id/files/bn829-2020.pdf"
    ),
    "kepmen_kp_83_2024_perlindungan_terbatas_belida_jawa.pdf": (
        "https://ppid.kkp.go.id/media/uploads/document_information_public/"
        "-2024kepmenkp083_1733794317.pdf"
    ),
}


def regulasi() -> None:
    """PDF regulasi status ikan Indonesia (dilindungi, membahayakan/invasif)."""
    run = Run(
        "regulasi",
        "KKP eMancing, peraturan.go.id (Berita Negara), PPID KKP",
        "Peraturan perundang-undangan; tidak dilindungi hak cipta (UU 28/2014 Ps. 42)",
        "Unduh PDF apa adanya; lampiran daftar spesies diekstrak terpisah dan wajib dicek manusia",
    )
    for name, url in REGULATIONS.items():
        if not run.has(name):
            _download(url, run.folder / name)
            if not (run.folder / name).read_bytes().startswith(b"%PDF"):
                raise RuntimeError(f"{name}: bukan PDF")
            run.add(name, url)
    run.finish(f"{len(REGULATIONS)} PDF regulasi")


# Literatur primer yang dihosting terbuka oleh penerbit/lembaga (tidak dikomit; hak cipta penulis).
OPEN_LITERATURE = {
    "herder2006_checklist_telmatherinidae_malili.pdf": (
        "https://www.ichthyologie.de/wp-content/uploads/2019/11/"
        "Preliminary_checklist_of_sailfin_silversides.pdf",
        "Herder F, Schwarzer J, Pfaender J, Hadiaty RK, Schliewen UK (2006) Preliminary checklist "
        "of sailfin silversides (Teleostei: Telmatherinidae) in the Malili Lakes of Sulawesi "
        "(Indonesia). Verh. Ges. Ichthyol. 5: 139-163",
    ),
}


def literatur() -> None:
    """PDF literatur primer yang disediakan terbuka oleh penerbitnya (checklist, deskripsi)."""
    run = Run(
        "literatur",
        "Situs penerbit/lembaga (lihat url per file)",
        "Hak cipta penulis/penerbit; disimpan lokal untuk ekstraksi fakta, tidak didistribusikan",
        "Unduh PDF apa adanya; ekstraksi tabel ke data/curation/ dengan rujukan halaman",
    )
    for name, (url, citation) in OPEN_LITERATURE.items():
        if not run.has(name):
            _download(url, run.folder / name)
            if not (run.folder / name).read_bytes().startswith(b"%PDF"):
                raise RuntimeError(f"{name}: bukan PDF")
            run.add(name, url, citation=citation)
    run.finish(f"{len(OPEN_LITERATURE)} PDF literatur")


# ---------------------------------------------------------------- BRIN RIN (Dataverse)

RIN = "https://data.brin.go.id/api/"
RIN_QUERY = (
    "(ikan OR fish OR pisces OR teleostei) AND (DNA OR COI OR 12S OR 16S OR barcode OR "
    "barcoding OR mitokondria OR mitochondrial OR eDNA OR metabarcoding OR sekuens)"
)


def brin_rin() -> None:
    """Repositori Ilmiah Nasional BRIN: metadata dataset DNA ikan + daftar file (terbuka/terkunci).

    Hanya metadata. File terbuka bisa diunduh lewat URL di manifest; file terkunci perlu
    permintaan akses ke pemilik. Nama file kerap memuat nomor aksesi GenBank publik.
    """
    run = Run(
        "brin_rin",
        "BRIN Repositori Ilmiah Nasional (Dataverse search + datasets API)",
        "Per dataset (lihat license/termsOfAccess di metadata)",
        "search q=" + RIN_QUERY + " type=dataset; datasets/:persistentId untuk tiap hasil",
    )
    if not run.has("search.json"):
        items, start = [], 0
        while True:
            page = _json(
                RIN
                + "search?"
                + urllib.parse.urlencode(
                    {"q": RIN_QUERY, "type": "dataset", "per_page": 100, "start": start}
                )
            )["data"]
            items += page["items"]
            start += 100
            if start >= page["total_count"]:
                break
            time.sleep(0.5)
        _write(run.folder / "search.json", json.dumps(items, ensure_ascii=False).encode())
        run.add("search.json", RIN + "search", len(items))
    items = json.loads((run.folder / "search.json").read_text("utf-8"))
    for item in items:
        pid = item.get("global_id")
        if not pid:
            continue
        name = "dataset_" + pid.split("/")[-1] + ".json"
        if run.has(name):
            continue
        url = RIN + "datasets/:persistentId/?" + urllib.parse.urlencode({"persistentId": pid})
        _write(run.folder / name, _request(url))
        run.add(name, url, 1, persistent_id=pid)
        time.sleep(0.3)
    run.finish(f"{len(items)} dataset BRIN terkait DNA ikan")


BRIN_FILE_TYPES = (
    ".pdf",
    ".csv",
    ".tsv",
    ".txt",
    ".xlsx",
    ".xls",
    ".gb",
    ".gbk",
    ".fasta",
    ".fas",
    ".fa",
    ".docx",
    ".doc",
)
BRIN_MAX_BYTES = 50_000_000


def brin_files() -> None:
    """Unduh file TERBUKA (bukan terkunci) dari dataset BRIN hasil `tropis_brin`.

    Hanya tipe berguna untuk ekstraksi (PDF, tabel, sekuens, dokumen), maksimal 50 MB per
    file. Gambar dilewati. Isi tetap mengikuti lisensi dataset di metadata.
    """
    meta = sorted((ROOT / "brin_rin").glob("*/manifest.json"))[-1].parent
    run = Run(
        "brin_rin_files",
        "BRIN Repositori Ilmiah Nasional (Dataverse access API); daftar dari "
        + str(meta.relative_to(RAW)),
        "Per dataset (license/termsOfAccess di metadata); disimpan lokal, tidak didistribusikan",
        "api/access/datafile/<id> untuk file restricted=false dengan ekstensi "
        + ", ".join(BRIN_FILE_TYPES)
        + f", <= {BRIN_MAX_BYTES} byte",
    )
    count = 0
    for path in sorted(meta.glob("dataset_*.json")):
        data = json.loads(path.read_text("utf-8")).get("data", {})
        for f in data.get("latestVersion", {}).get("files", []):
            df = f.get("dataFile", {})
            name = df.get("filename", "")
            if f.get("restricted") or not name.lower().endswith(BRIN_FILE_TYPES):
                continue
            if int(df.get("filesize") or 0) > BRIN_MAX_BYTES:
                continue
            safe = (
                f"{df['id']}_"
                + "".join(c if c.isalnum() or c in "._-" else "_" for c in name)[:120]
            )
            if run.has(safe):
                continue
            url = f"{RIN}access/datafile/{df['id']}"
            _download(url, run.folder / safe)
            run.add(safe, url, dataset=data.get("identifier"), original_name=name)
            count += 1
            time.sleep(0.3)
    run.finish(f"{len(run.manifest['files'])} file terbuka dari dataset BRIN")


OBIS_AREAS = {"115": "Indonesia", "40038": "Indonesian Sea (LME)"}
OBIS_TAXON = "10194"  # WoRMS AphiaID Actinopteri


def obis() -> None:
    """OBIS checklist ikan bersirip-jari per area Indonesia (laut/payau; pelengkap GBIF)."""
    run = Run(
        "obis",
        "OBIS API v3 checklist",
        "Per dataset penerbit OBIS (umumnya CC0/CC BY); data agregat jumlah per takson",
        f"checklist?areaid=<area>&taxonid={OBIS_TAXON}&size=10000; area: "
        + ", ".join(f"{k} {v}" for k, v in OBIS_AREAS.items()),
    )
    for area, label in OBIS_AREAS.items():
        name = f"checklist_area{area}.json"
        if run.has(name):
            continue
        # Satu permintaan: paginasi skip tidak menambah takson (diuji 25 Okt 2026); "total" OBIS
        # (4.522) lebih besar dari takson unik yang dikembalikan (4.411), dicatat sebagai catatan.
        page = _json(
            "https://api.obis.org/v3/checklist?"
            + urllib.parse.urlencode({"areaid": area, "taxonid": OBIS_TAXON, "size": 10000})
        )
        results = list({r["taxonID"]: r for r in page["results"]}.values())
        if len(results) != page["total"]:
            run.manifest["notes"].append(
                f"area {area}: OBIS total {page['total']}, takson unik diterima {len(results)}"
            )
        _write(run.folder / name, json.dumps(results, ensure_ascii=False).encode())
        run.add(name, "https://api.obis.org/v3/checklist", len(results), area=label)
    run.finish("checklist OBIS " + ", ".join(OBIS_AREAS.values()))


# ---------------------------------------------------------------- Repositori data internasional

ZENODO_QUERY = (
    "+Indonesia +(fish OR fishes OR ikan) +(DNA OR COI OR 12S OR barcode OR barcoding OR "
    "mitochondrial OR mitogenome OR eDNA OR phylogeny)"
)
REPO_QUERIES = [
    "Indonesia fish DNA",
    "Indonesia eDNA fish",
    "Sulawesi fish",
    "Sumatra fish",
    "Borneo freshwater fish",
    "Java fish barcode",
    "Papua fish",
    "Sundaland freshwater fish",
    "Wallacea fish",
]


def repositori() -> None:
    """Penemuan dataset di Zenodo, Dryad, Figshare (metadata saja; unduhan per dataset manual)."""
    run = Run(
        "repositori",
        "Zenodo records API, Dryad API v2 search, Figshare articles search",
        "Metadata terbuka; lisensi per dataset tercantum di metadata",
        "Zenodo q=" + ZENODO_QUERY + " type=dataset (semua halaman); Dryad dan Figshare per "
        "kueri: " + "; ".join(REPO_QUERIES),
    )
    if not run.has("zenodo.json"):
        hits, page = [], 1
        while True:
            data = _json(
                "https://zenodo.org/api/records?"
                + urllib.parse.urlencode(
                    {"q": ZENODO_QUERY, "type": "dataset", "size": 25, "page": page}
                )
            )
            hits += data["hits"]["hits"]
            if len(hits) >= data["hits"]["total"] or not data["hits"]["hits"]:
                break
            page += 1
            time.sleep(1)
        _write(run.folder / "zenodo.json", json.dumps(hits, ensure_ascii=False).encode())
        run.add("zenodo.json", "https://zenodo.org/api/records", len(hits))
    for i, query in enumerate(REPO_QUERIES):
        name = f"dryad_{i:02d}.json"
        if not run.has(name):
            url = "https://datadryad.org/api/v2/search?" + urllib.parse.urlencode(
                {"q": query, "per_page": 100}
            )
            _write(run.folder / name, _request(url))
            run.add(
                name,
                url,
                json.loads((run.folder / name).read_text("utf-8")).get("count"),
                query=query,
            )
            time.sleep(1)
        name = f"figshare_{i:02d}.json"
        if not run.has(name):
            body = json.dumps({"search_for": query, "page_size": 200}).encode()
            req = urllib.request.Request(
                "https://api.figshare.com/v2/articles/search",
                data=body,
                headers={**UA, "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                _write(run.folder / name, r.read())
            run.add(
                name,
                "https://api.figshare.com/v2/articles/search",
                len(json.loads((run.folder / name).read_text("utf-8"))),
                query=query,
            )
            time.sleep(1)
    run.finish("penemuan dataset Zenodo, Dryad, Figshare")


# ---------------------------------------------------------------- SRA/ENA (eDNA lapangan)


def sra() -> None:
    """BioProject eDNA ikan Indonesia: metadata + daftar URL FASTQ (ENA), tanpa FASTQ-nya.

    FASTQ besar tidak diunduh di sini; `fastq_urls.tsv` siap dipakai untuk unduhan manual
    atau dataset lanjutan. Mengolah FASTQ menjadi ASV adalah F33 [P2].
    """
    run = Run(
        "sra_edna",
        "NCBI BioProject (E-utilities) + ENA portal API filereport",
        "Data INSDC publik (NCBI/ENA); sitasi BioProject wajib",
        "esearch db=bioproject: "
        + SRA_TERM
        + "; ENA filereport result=read_run fields="
        + ENA_FIELDS,
    )
    ids = _json(
        EUTILS + "esearch.fcgi",
        {
            "db": "bioproject",
            "term": SRA_TERM,
            "retmax": 500,
            "retmode": "json",
            "tool": "biotrace_harvest",
        },
    )["esearchresult"]["idlist"]
    time.sleep(NCBI_PAUSE)
    summary = _request(
        EUTILS + "esummary.fcgi",
        {"db": "bioproject", "id": ",".join(ids), "retmode": "json", "tool": "biotrace_harvest"},
    )
    _write(run.folder / "bioprojects.esummary.json", summary)
    run.add("bioprojects.esummary.json", EUTILS + "esummary.fcgi", len(ids))
    projects = json.loads(summary)["result"]
    lines, total_bytes, runs = [], 0, 0
    for uid in projects["uids"]:
        acc = projects[uid]["project_acc"]
        name = f"{acc}.ena_read_run.tsv"
        url = "https://www.ebi.ac.uk/ena/portal/api/filereport?" + urllib.parse.urlencode(
            {"accession": acc, "result": "read_run", "fields": ENA_FIELDS, "format": "tsv"}
        )
        if not run.has(name):
            _write(run.folder / name, _request(url))
            rows = max(0, (run.folder / name).read_bytes().count(b"\n") - 1)
            run.add(name, url, rows, bioproject=acc, title=projects[uid].get("project_title"))
            time.sleep(0.5)
        table = (run.folder / name).read_text("utf-8").splitlines()
        if not table:
            continue
        head = table[0].split("\t")
        for row in table[1:]:
            rec = dict(zip(head, row.split("\t"), strict=False))
            for ftp, size, md5 in zip(
                rec.get("fastq_ftp", "").split(";"),
                rec.get("fastq_bytes", "").split(";"),
                rec.get("fastq_md5", "").split(";"),
                strict=False,
            ):
                if ftp:
                    lines.append(f"{acc}\t{rec['run_accession']}\thttps://{ftp}\t{size}\t{md5}")
                    total_bytes += int(size or 0)
            runs += 1
    _write(
        run.folder / "fastq_urls.tsv",
        ("bioproject\trun\turl\tbytes\tmd5\n" + "\n".join(sorted(lines)) + "\n").encode(),
    )
    run.add("fastq_urls.tsv", "ENA filereport fastq_ftp", len(lines), total_bytes=total_bytes)
    run.finish(
        f"{len(ids)} BioProject, {runs} run, {len(lines)} FASTQ ({total_bytes / 1e9:.1f} GB)"
    )


# ---------------------------------------------------------------- Zenodo


def _zenodo(dataset: str, record: str) -> None:
    meta = _json(f"https://zenodo.org/api/records/{record}")
    license_id = (meta.get("metadata", {}).get("license") or {}).get("id", "?")
    run = Run(
        dataset,
        f"Zenodo record {record}: {meta['metadata']['title']}",
        f"Lisensi Zenodo: {license_id}",
        "Unduh semua file record; MD5 dibandingkan dengan checksum Zenodo.",
    )
    for f in meta["files"]:
        name = f["key"]
        if run.has(name):
            continue
        url = f["links"]["self"]
        _download(url, run.folder / name)
        md5 = hashlib.md5((run.folder / name).read_bytes()).hexdigest()
        if f.get("checksum", "").replace("md5:", "") not in ("", md5):
            raise RuntimeError(f"{name}: MD5 tidak cocok dengan Zenodo")
        run.add(name, url, md5=md5)
    run.finish(f"{len(meta['files'])} file, lisensi {license_id}")


def zenodo_mifish() -> None:
    _zenodo("zenodo_mifish_rcrux", ZENODO["mifish_rcrux_2025"])


def zenodo_mitohelper() -> None:
    _zenodo("zenodo_mitohelper", ZENODO["mitohelper_2025"])


DATASETS: dict[str, tuple[Callable[[], None], str]] = {
    "tropis_fishbase": (fishbase, "FishBase v25.04 tabel negara/spesies/sinonim (CC BY-NC)"),
    "tropis_genbank_country": (
        genbank_country,
        "GenBank 12S+mitogenom ikan per negara tropis Asia Tenggara",
    ),
    "tropis_genbank_freshwater": (
        genbank_species_freshwater,
        "GenBank 12S+mitogenom spesies air tawar/payau Indonesia (butuh tropis_fishbase)",
    ),
    "tropis_genbank_marine": (
        genbank_species_marine,
        "GenBank 12S+mitogenom spesies laut Indonesia (besar, butuh tropis_fishbase)",
    ),
    "tropis_europepmc": (europepmc, "Artikel OA ikan Indonesia + aksesi yang disebut (Europe PMC)"),
    "tropis_genbank_cited": (
        genbank_cited,
        "GenBank untuk aksesi yang dikutip paper ikan Indonesia (butuh tropis_europepmc)",
    ),
    "tropis_bold": (bold, "BOLD v5 COI Teleostei global (disaring lokal per negara)"),
    "tropis_gbif": (gbif, "GBIF jumlah okurensi/spesimen museum per spesies ikan"),
    "tropis_oai": (oai, "Metadata OAI-PMH 11 jurnal Indonesia (biologi, ikan, perairan, laut)"),
    "tropis_regulasi": (regulasi, "PDF Kepmen KP 1/2021, Permen KP 19/2020, Kepmen KP 83/2024"),
    "tropis_literatur": (
        literatur,
        "PDF literatur primer terbuka (Herder 2006 checklist Telmatherinidae)",
    ),
    "tropis_brin": (brin_rin, "Metadata dataset DNA ikan di Repositori Ilmiah Nasional BRIN"),
    "tropis_repositori": (repositori, "Penemuan dataset ikan Indonesia di Zenodo, Dryad, Figshare"),
    "tropis_brin_files": (
        brin_files,
        "File terbuka (PDF/tabel/sekuens) dari dataset BRIN (butuh tropis_brin)",
    ),
    "tropis_obis": (obis, "OBIS checklist ikan laut area Indonesia"),
    "tropis_sra": (sra, "BioProject eDNA ikan Indonesia + daftar URL FASTQ ENA (tanpa FASTQ)"),
    "tropis_zenodo_mifish": (zenodo_mifish, "Pustaka 12S MiFish rCRUX+MitoFish (Zenodo, ±27,5 MB)"),
    "tropis_zenodo_mitohelper": (
        zenodo_mitohelper,
        "Mitohelper reference datasets (Zenodo, ±2,2 GB, opsional)",
    ),
}
