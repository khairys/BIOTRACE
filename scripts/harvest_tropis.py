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
}
ZENODO = {
    "mifish_rcrux_2025": "17664847",  # 12S MiFish V5-V6, rCRUX nt + MitoFish (Nov 2025)
    "mitohelper_2025": "17602902",  # Mitohelper reference datasets (Nov 2025, +-2,2 GB)
}


# ---------------------------------------------------------------- utilitas


def _request(url: str, data: dict | None = None, timeout: int = 300) -> bytes:
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    last: Exception | None = None
    for attempt in range(5):  # server publik kadang membalas 429/5xx sementara
        try:
            req = urllib.request.Request(url, data=body, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except OSError as exc:
            last = exc
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"gagal setelah 5 percobaan: {url}") from last


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
            ISO2[country],
            f'Actinopterygii[Organism] AND "{country}"[country] AND {MARKER_TERM}',
        )
    run.finish(f"{total} rekaman 12S/mitogenom dari {len(COUNTRIES)} negara")


def _genbank_species(dataset: str, names: list[str], description: str) -> None:
    run = Run(
        dataset,
        "NCBI GenBank nuccore (E-utilities); daftar nama dari FishBase raw/tropis/fishbase",
        "Kebijakan NCBI: tanpa batasan pemakaian, tanpa jaminan hak pihak ketiga",
        f"{description}. Nama dibagi per 60 lalu digabung OR sebagai [Organism] AND " + MARKER_TERM,
    )
    run.manifest["target_species"] = len(names)
    total = 0
    for i in range(0, len(names), 60):
        chunk = names[i : i + 60]
        organisms = " OR ".join(f'"{n}"[Organism]' for n in chunk)
        total += _genbank_query(run, f"batch{i // 60:03d}", f"({organisms}) AND {MARKER_TERM}")
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


# ---------------------------------------------------------------- BOLD v5


def bold() -> None:
    """BOLD v5 portal: rekaman Teleostei per negara (COI, voucher museum, koordinat)."""
    run = Run(
        "bold",
        "BOLD Systems v5 portal API",
        "Rekaman publik BOLD; lisensi per rekaman (lihat kolom BOLD)",
        "api/query?query=tax:class:Teleostei;geo:country/region:<negara>&extent=full lalu "
        "api/documents/<query_id>/download?format=tsv",
    )
    for country in ["Indonesia", *SUNDALAND, *WALLACEA_SAHUL]:
        name = f"{ISO2[country]}.tsv"
        if run.has(name):
            continue
        query = f"tax:class:Teleostei;geo:country/region:{country}"
        qid = _json(
            "https://portal.boldsystems.org/api/query?"
            + urllib.parse.urlencode({"query": query, "extent": "full"})
        )["query_id"]
        url = f"https://portal.boldsystems.org/api/documents/{urllib.parse.quote(qid)}/download?format=tsv"
        _download(url, run.folder / name)
        rows = max(0, (run.folder / name).read_bytes().count(b"\n") - 1)
        run.manifest["queries"][country] = {"query": query, "records": rows}
        run.add(name, url, rows)
        time.sleep(1)
    run.finish("TSV BOLD per negara")


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

    for journal, endpoint in OAI_JOURNALS.items():
        if run.manifest["queries"].get(journal, {}).get("complete"):
            continue
        token, page, records = None, 0, 0
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
        run.manifest["queries"][journal] = {
            "endpoint": endpoint,
            "records": records,
            "pages": page + 1,
            "complete": True,
        }
        run.save()
    run.finish("metadata OAI 4 jurnal")


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
    "tropis_bold": (bold, "BOLD v5 COI Teleostei Indonesia + tetangga"),
    "tropis_gbif": (gbif, "GBIF jumlah okurensi/spesimen museum per spesies ikan"),
    "tropis_oai": (oai, "Metadata OAI-PMH 4 jurnal Indonesia"),
    "tropis_zenodo_mifish": (zenodo_mifish, "Pustaka 12S MiFish rCRUX+MitoFish (Zenodo, ±27,5 MB)"),
    "tropis_zenodo_mitohelper": (
        zenodo_mitohelper,
        "Mitohelper reference datasets (Zenodo, ±2,2 GB, opsional)",
    ),
}
