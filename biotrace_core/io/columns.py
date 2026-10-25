"""F1/F2 [MVP], D-039 (Disetujui untuk integrasi): kolom input dikenali dari nama dan isinya.

Nama kolom dicocokkan ke kontrak 04 §1 lewat sinonim; kolom wajib yang namanya tidak dikenal
dicari dari isinya. Nilai hanya dinormalisasi bila maknanya tidak ambigu (mis. "12S MiFish" →
`12S_MiFish_U`). Metadata biologis yang kosong tidak ditebak (A1): koordinat dan tanggal tetap
kosong, dan perairan wajib dipilih pengguna bila tidak ada di file.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

ASV = ("asv_id", "asv", "otu_id", "otu", "zotu_id", "zotu", "feature_id", "feature", "asv_name")
SAMPLE = ("sample_id", "sample", "sampel", "id_sampel", "kode_sampel", "sample_name", "sampleid")
ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "reads": {
        "asv_id": ASV,
        "sample_id": SAMPLE,
        "reads": (
            "reads",
            "read",
            "read_count",
            "reads_count",
            "n_reads",
            "count",
            "counts",
            "abundance",
            "jumlah_bacaan",
            "bacaan",
            "jumlah_read",
        ),
        "is_simulated": ("is_simulated",),
    },
    "taxonomy": {
        "asv_id": ASV,
        "taxon": (
            "taxon",
            "taxa",
            "species",
            "spesies",
            "scientific_name",
            "nama_ilmiah",
            "assigned_taxon",
            "best_hit",
            "best_match",
            "taxonomy",
        ),
        "rank": ("rank", "taxon_rank", "taxonomic_rank", "level", "tingkat", "tingkat_takson"),
        "pct_identity": (
            "pct_identity",
            "identity",
            "pident",
            "percent_identity",
            "pct_id",
            "perc_identity",
            "similarity",
            "identitas",
            "persen_identitas",
        ),
        "runner_up_taxon": ("runner_up_taxon", "runner_up", "second_taxon", "second_best"),
        "runner_up_pct_identity": (
            "runner_up_pct_identity",
            "runner_up_identity",
            "runner_up_pident",
            "second_pct_identity",
            "second_identity",
        ),
        "reference_db": ("reference_db", "database", "db", "ref_db", "reference"),
        "is_simulated": ("is_simulated",),
    },
    "metadata": {
        "sample_id": SAMPLE,
        "site_id": (
            "site_id",
            "site",
            "lokasi",
            "location",
            "location_id",
            "station",
            "stasiun",
            "site_code",
            "kode_lokasi",
            "site_name",
            "nama_lokasi",
        ),
        "waterbody_id": (
            "waterbody_id",
            "waterbody",
            "water_body",
            "perairan",
            "badan_air",
            "lake",
            "danau",
        ),
        "latitude": ("latitude", "lat", "lintang", "decimal_latitude", "decimallatitude"),
        "longitude": (
            "longitude",
            "lon",
            "long",
            "lng",
            "bujur",
            "decimal_longitude",
            "decimallongitude",
        ),
        "collection_date": (
            "collection_date",
            "date",
            "tanggal",
            "sampling_date",
            "tanggal_sampling",
            "event_date",
            "eventdate",
        ),
        "sample_type": ("sample_type", "type", "jenis_sampel", "tipe_sampel", "sample_category"),
        "replicate": ("replicate", "rep", "replikat", "ulangan", "replicate_no"),
        "extraction_batch": ("extraction_batch", "batch", "batch_ekstraksi", "extraction"),
        "marker": ("marker", "primer", "target_gene", "gene", "locus", "lokus"),
        "pcr_batch": ("pcr_batch", "batch_pcr"),
        "notes": ("notes", "note", "catatan", "keterangan", "remarks", "comment"),
        "is_simulated": ("is_simulated",),
    },
    "site_context": {
        "site_id": ("site_id", "site", "lokasi", "location", "station", "stasiun"),
        "context_type": ("context_type", "jenis_konteks", "type"),
        "description": ("description", "deskripsi", "keterangan", "catatan", "notes"),
    },
}
METADATA_FIELDS = {"site_id", "waterbody_id", "latitude", "longitude", "collection_date"} | {
    "sample_type",
    "replicate",
    "extraction_batch",
    "marker",
}
NO_HIT = {"", "tidak_ada_hit", "no_hit", "nohit", "unassigned", "unknown", "tidak_dikenal"} | {
    "na",
    "none",
    "null",
}
RANKS = {
    "species": "species",
    "spesies": "species",
    "sp": "species",
    "genus": "genus",
    "family": "family",
    "famili": "family",
    "familia": "family",
    "order": "order",
    "ordo": "order",
}
NO_BATCH = "TIDAK_DICATAT"
CONTROL = "CONTROL"
CONTROL_PATTERN = re.compile(r"blank|ntc|neg|kontrol|control")


@dataclass
class TableMapping:
    """Which source column fills which contract column, for the validation report."""

    role: str
    columns: dict[str, str] = field(default_factory=dict)
    ignored: list[str] = field(default_factory=list)
    wide: bool = False

    def changes(self) -> list[str]:
        renamed = [f"{src} → {dst}" for dst, src in sorted(self.columns.items()) if src != dst]
        notes = [f"kolom dibaca sebagai: {', '.join(renamed)}"] if renamed else []
        if self.wide:
            notes.append("format lebar (satu kolom per sampel)")
        if self.ignored:
            notes.append(f"kolom tambahan diabaikan: {', '.join(self.ignored)}")
        return notes


def canonical(text: str) -> str:
    """Header/value key: lowercase, non-alphanumerics folded to single underscores."""
    return re.sub(r"[^0-9a-z]+", "_", text.replace("﻿", "").strip().lower()).strip("_")


def parse_count(value: str) -> int | None:
    text = value.strip().replace("_", "")
    if re.fullmatch(r"\d+", text):
        return int(text)
    if re.fullmatch(r"\d+\.0+", text):
        return int(float(text))
    return None


def parse_number(value: str) -> float | None:
    text = value.strip().rstrip("%").strip().replace(",", ".")
    try:
        return float(text) if text else None
    except ValueError:
        return None


def parse_date(value: str) -> str:
    """ISO date/datetime or Indonesian day-first dd/mm/yyyy → ISO date; blank stays blank."""
    text = value.strip()
    if not text:
        return ""
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    for pattern in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    return text


def normalize_marker(value: str) -> str:
    key = canonical(value).replace("_", "")
    if not key:
        return ""
    if "mifish" in key:
        # MiFish-E (elasmobranch) is a different primer set and has no reference here.
        return value if re.search(r"mifish_?e\b", canonical(value)) else "12S_MiFish_U"
    if "teleo" in key:
        return "12S_Teleo1_V5"
    if key in {"coi", "co1", "cox1", "coxi"}:
        return "COI"
    if key.startswith("16s"):
        return "16S"
    if key.startswith("mitogenom"):
        return "mitogenome"
    if key in {"12s", "12srrna", "12sother"}:
        return "12S_other"
    return value


def normalize_sample_type(value: str) -> str:
    key = canonical(value)
    if key in {"sampel", "sample", "field", "field_sample", "lapangan", "sampel_lapangan"}:
        return "sampel"
    if key.startswith("kontrol_negatif") or key == "kontrol_positif":
        return key
    if "posit" in key:
        return "kontrol_positif"
    if CONTROL_PATTERN.search(key):
        if "pcr" in key or "ntc" in key:
            return "kontrol_negatif_pcr"
        if "field" in key or "lapangan" in key:
            return "kontrol_negatif_lapangan"
        return "kontrol_negatif_ekstraksi"
    return value


def rank_from_taxon(taxon: str) -> str:
    words = taxon.split()
    if len(words) >= 2 and words[1][:1].islower():
        return "species"
    if taxon.endswith("idae"):
        return "family"
    if taxon.endswith("iformes"):
        return "order"
    return "genus"


def _match_headers(headers: list[str], role: str) -> dict[str, str]:
    keys = {canonical(h): h for h in headers}
    columns: dict[str, str] = {}
    for target, aliases in ALIASES[role].items():
        for alias in aliases:
            source = keys.get(alias)
            if source and source not in columns.values():
                columns[target] = source
                break
    return columns


def detect_role(headers: list[str], rows: list[dict[str, str]]) -> str:
    """Role of an uploaded table from its headers, then its contents (wide read tables)."""
    keys = {canonical(h) for h in headers}
    taxonomy = {t for t, aliases in ALIASES["taxonomy"].items() if keys & set(aliases)}
    if "pct_identity" in taxonomy or {"taxon", "rank"} <= taxonomy:
        return "taxonomy"
    meta = {t for t, aliases in ALIASES["metadata"].items() if keys & set(aliases)}
    if "sample_id" in meta and len(meta & METADATA_FIELDS) >= 2:
        return "metadata"
    if keys & {"context_type", "description", "deskripsi"} and keys & {"site_id", "site"}:
        return "site_context"
    reads = _match_headers(headers, "reads")
    if {"sample_id", "reads"} <= reads.keys():
        return "reads"
    if len(headers) >= 2 and rows and _wide_counts(headers[1:], rows):
        return "reads"
    return "unknown"


def _wide_counts(columns: list[str], rows: list[dict[str, str]]) -> bool:
    values = [row[c] for row in rows[:200] for c in columns if canonical(c) != "is_simulated"]
    return bool(values) and all(parse_count(v) is not None for v in values if v)


def _content_column(
    rows: list[dict[str, str]], candidates: list[str], test, share: float = 1.0
) -> str | None:
    for column in candidates:
        values = [row[column] for row in rows[:500] if row[column]]
        if values and sum(bool(test(v)) for v in values) >= share * len(values):
            return column
    return None


def map_table(
    rows: list[dict[str, str]], role: str, sample_ids: set[str] | None = None
) -> tuple[list[dict[str, str]], TableMapping]:
    """Rename columns to the 04 §1 contract; wide read tables become long rows (R-PRE-01)."""
    headers = list(rows[0]) if rows else []
    columns = _match_headers(headers, role)
    mapping = TableMapping(role=role, columns=columns)
    free = [h for h in headers if h not in columns.values()]
    if role == "reads" and not ({"sample_id", "reads"} <= columns.keys()):
        samples = sample_ids or set()
        asv = columns.get("asv_id") or headers[0]
        counts = [h for h in headers if h != asv and canonical(h) != "is_simulated"]
        if "sample_id" not in columns and (
            set(counts) & samples or (counts and _wide_counts(counts, rows))
        ):
            mapping.columns = {"asv_id": asv, "sample_id": "(header)", "reads": "(isi)"}
            mapping.wide = True
            simulated = columns.get("is_simulated")
            long_rows = [
                {
                    "asv_id": row[asv],
                    "sample_id": column,
                    "reads": row[column],
                    "is_simulated": row[simulated] if simulated else "false",
                }
                for row in rows
                for column in counts
            ]
            return long_rows, mapping
        if "reads" not in columns:
            found = _content_column(rows, free, lambda v: parse_count(v) is not None)
            if found:
                columns["reads"], free = found, [h for h in free if h != found]
        if "sample_id" not in columns and samples:
            found = _content_column(rows, free, lambda v: v in samples, 0.8)
            if found:
                columns["sample_id"], free = found, [h for h in free if h != found]
    if role == "taxonomy":
        if "pct_identity" not in columns:
            found = _content_column(
                rows, free, lambda v: (n := parse_number(v)) is not None and 0 <= n <= 100
            )
            if found:
                columns["pct_identity"], free = found, [h for h in free if h != found]
        if "rank" not in columns:
            found = _content_column(rows, free, lambda v: canonical(v) in RANKS)
            if found:
                columns["rank"], free = found, [h for h in free if h != found]
        if "taxon" not in columns:
            found = _content_column(
                rows, free, lambda v: re.fullmatch(r"[A-Z][a-z]+( [a-z]+\.?)*", v), 0.5
            )
            if found:
                columns["taxon"], free = found, [h for h in free if h != found]
    if "asv_id" in ALIASES[role] and "asv_id" not in columns and free:
        columns["asv_id"], free = free[0], free[1:]
    mapping.columns = columns
    mapping.ignored = [h for h in headers if h not in columns.values()]
    renamed = [{target: row[source] for target, source in columns.items()} for row in rows]
    return renamed, mapping


def table_marker(rows: list[dict[str, str]]) -> str:
    """Single marker named in a table (e.g. lab taxonomy), used only when metadata is blank."""
    columns = _match_headers(list(rows[0]) if rows else [], "metadata")
    source = columns.get("marker")
    values = {normalize_marker(row[source]) for row in rows if source and row[source]}
    return values.pop() if len(values) == 1 else ""


def resolve_waterbody(value: str, waterbodies: Mapping[str, str]) -> str:
    """Waterbody given as id or name (e.g. "Danau Matano", "matano") → reference id."""
    key = canonical(value)
    for identifier, name in waterbodies.items():
        names = {canonical(identifier), canonical(name)}
        names |= {n.removeprefix(p) for n in names for p in ("danau_", "lake_", "perairan_")}
        if key in names:
            return identifier
    return value


def prepare_metadata(
    rows: list[dict[str, str]],
    waterbodies: Mapping[str, str],
    defaults: Mapping[str, str],
) -> tuple[list[dict[str, str]], list[str]]:
    """Fill structural gaps conservatively; never invent coordinates, dates or waterbodies."""
    notes: list[str] = []
    out = [dict(row) for row in rows]
    for row in out:
        for key in ("latitude", "longitude"):
            number = parse_number(row.get(key, ""))
            if number is not None:
                row[key] = str(number)
        if "collection_date" in row:
            row["collection_date"] = parse_date(row["collection_date"])
        given = row.get("sample_type", "")
        row["sample_type"] = (
            normalize_sample_type(given)
            if given
            else normalize_sample_type(row["sample_id"])
            if CONTROL_PATTERN.search(canonical(row["sample_id"]))
            else "sampel"
        )
        if not given:
            notes.append(
                "jenis sampel kosong: diisi dari sample_id (blank/NTC/kontrol) atau 'sampel'"
            )
        marker = row.get("marker", "")
        row["marker"] = normalize_marker(marker) or defaults.get("marker", "")
        if marker and row["marker"] != marker:
            notes.append(f"marker '{marker}' dibaca sebagai {row['marker']}")
        control = row["sample_type"] != "sampel"
        if row.get("waterbody_id"):
            resolved = resolve_waterbody(row["waterbody_id"], waterbodies)
            if resolved != row["waterbody_id"]:
                notes.append(f"perairan '{row['waterbody_id']}' dibaca sebagai {resolved}")
            row["waterbody_id"] = resolved
        else:
            row["waterbody_id"] = CONTROL if control else defaults.get("waterbody_id", "")
            if not control and row["waterbody_id"]:
                notes.append(f"perairan kosong: diisi {row['waterbody_id']} dari formulir unggah")
        if not row.get("extraction_batch"):
            row["extraction_batch"] = NO_BATCH
            notes.append(
                "extraction_batch kosong: semua sampel dan kontrol dianggap satu batch "
                f"({NO_BATCH})"
            )
        if row.get("replicate"):
            digits = re.sub(r"\D", "", row["replicate"])
            row["replicate"] = digits or row["replicate"]
    sites = [row.get("site_id", "") for row in out]
    if not any(sites):
        for row in out:
            control = row["sample_type"] != "sampel"
            row["site_id"] = CONTROL if control else row["sample_id"]
            if not control and not row.get("replicate"):
                row["replicate"] = "1"
        notes.append("lokasi kosong: setiap sampel dianggap lokasi sendiri dengan replikat 1")
    else:
        by_site: dict[str, list[dict[str, str]]] = {}
        for row in out:
            if not row.get("site_id"):
                row["site_id"] = CONTROL if row["sample_type"] != "sampel" else row["sample_id"]
            by_site.setdefault(row["site_id"], []).append(row)
        for site, members in sorted(by_site.items()):
            field_rows = [r for r in members if r["sample_type"] == "sampel"]
            if field_rows and not any(r.get("replicate") for r in field_rows):
                for number, row in enumerate(sorted(field_rows, key=lambda r: r["sample_id"]), 1):
                    row["replicate"] = str(number)
                notes.append(f"replikat kosong di {site}: dinomori urut menurut sample_id")
    return out, sorted(set(notes))


def prepare_taxonomy(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], set[str], list[str]]:
    """Lab 'no hit' rows become unknown claims (no candidates), not invented names."""
    out, no_hit, notes = [], set(), []
    for row in rows:
        taxon = row.get("taxon", "").strip()
        rank = canonical(row.get("rank", ""))
        if not taxon or (rank and rank in NO_HIT):
            no_hit.add(row["asv_id"])
            continue
        prepared = dict(row)
        prepared["rank"] = RANKS.get(rank) or rank_from_taxon(taxon)
        if not rank:
            notes.append("tingkat takson kosong: dibaca dari bentuk nama (binomial → species)")
        for key in ("pct_identity", "runner_up_pct_identity"):
            if prepared.get(key):
                number = parse_number(prepared[key])
                prepared[key] = str(number) if number is not None else prepared[key]
        out.append(prepared)
    if no_hit:
        notes.append(
            f"{len(no_hit)} ASV tanpa kecocokan lab (mis. {', '.join(sorted(no_hit)[:3])}) "
            "dinilai sebagai tidak dikenal"
        )
    return out, no_hit, sorted(set(notes))
