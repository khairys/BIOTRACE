"""D-039 (Disetujui untuk integrasi): kolom input dikenali otomatis, tanpa menebak metadata biologis [MVP]."""

import csv

import pytest

from biotrace_core.config import DEFAULT_RULES, ROOT
from biotrace_core.io.columns import (
    canonical,
    detect_role,
    map_table,
    normalize_marker,
    normalize_sample_type,
    resolve_waterbody,
)
from biotrace_core.io.loaders import write_table
from biotrace_core.io.validate import InputError, load_inputs
from biotrace_core.pipeline import run_analysis
from biotrace_core.records import rematch, site_points

WATERBODIES = {"MATANO": "Danau Matano", "LAUT_INDONESIA": "Perairan laut Indonesia"}
# Shapes of a real Nanopore lab export (otu_id, extra QC columns, blank site metadata).
READS = [
    {"otu_id": "OTU_01", "sample_id": "Sample_1", "reads": "11", "otu_asli": "S1_11"},
    {"otu_id": "OTU_02", "sample_id": "Sample_1", "reads": "16", "otu_asli": "S1_145"},
    {"otu_id": "OTU_01", "sample_id": "Sample_2", "reads": "7", "otu_asli": "S1_11"},
]
META_HEADERS = "sample_id,sample_type,nanopore_barcode,site_name,waterbody,latitude,longitude"
META_HEADERS += ",collection_date,replicate,extraction_batch,marker,lolos_cutadapt"
META = [
    dict(zip(META_HEADERS.split(","), values, strict=True))
    for values in (
        ["Sample_1", "sampel", "barcode41", "", "", "", "", "", "", "", "12S MiFish", "283"],
        ["Sample_2", "sampel", "barcode39", "", "", "", "", "", "", "", "12S MiFish", "254"],
    )
]


def taxonomy_rows(species: str, other: str) -> list[dict[str, str]]:
    return [
        {
            "otu_id": "OTU_01",
            "taxon": species,
            "rank": "species",
            "pct_identity": "100.0",
            "runner_up_taxon": other,
            "runner_up_pct_identity": "98.5",
            "reference_db": "lab",
            "catatan": "",
        },
        {
            "otu_id": "OTU_02",
            "taxon": "",
            "rank": "tidak_ada_hit",
            "pct_identity": "",
            "runner_up_taxon": "",
            "runner_up_pct_identity": "",
            "reference_db": "lab",
            "catatan": "tidak ada hit",
        },
    ]


def write(tmp_path, species="Genus alpha", other="Genus beta"):
    paths = {name: tmp_path / f"{name}.csv" for name in ("reads", "metadata", "taxonomy")}
    write_table(paths["reads"], READS)
    write_table(paths["metadata"], META)
    write_table(paths["taxonomy"], taxonomy_rows(species, other))
    return paths


def load(paths, defaults=None):
    return load_inputs(
        paths["reads"],
        paths["metadata"],
        None,
        paths["taxonomy"],
        None,
        WATERBODIES,
        "normal",
        defaults,
    )


def test_D038_lab_export_loads_with_user_chosen_waterbody(tmp_path):
    data = load(write(tmp_path), {"waterbody_id": "LAUT_INDONESIA"})
    sample = data.samples[0]
    assert (sample.site_id, sample.waterbody_id, sample.replicate) == (
        "Sample_1",
        "LAUT_INDONESIA",
        1,
    )
    assert sample.marker == "12S_MiFish_U" and sample.latitude is None
    assert sample.collection_date is None and sample.extraction_batch == "TIDAK_DICATAT"
    assert {r.asv_id for r in data.reads} == {"OTU_01", "OTU_02"}
    assert data.no_hit == {"OTU_02"} and set(data.taxonomy) == {"OTU_01"}
    notes = " ".join(i.message for i in data.report.issues if i.code == "V-COL")
    assert "otu_id → asv_id" in notes and "nanopore_barcode" in notes


def test_D038_blank_waterbody_is_asked_not_guessed(tmp_path):
    with pytest.raises(InputError) as error:
        load(write(tmp_path))
    issue = next(i for i in error.value.report.issues if i.level == "error")
    assert issue.code == "V-03" and issue.field == "waterbody_id"
    assert "LAUT_INDONESIA" in issue.message and "Extra inputs" not in issue.message


def test_D038_missing_required_column_is_named(tmp_path):
    paths = write(tmp_path)
    write_table(paths["reads"], [{"otu_id": "OTU_01", "sample_id": "Sample_1"}])
    with pytest.raises(InputError, match="kolom wajib tidak dikenali: reads"):
        load(paths, {"waterbody_id": "MATANO"})


def test_D038_wide_reads_with_otu_header(tmp_path):
    paths = write(tmp_path)
    write_table(paths["reads"], [{"#OTU ID": "OTU_01", "Sample_1": "5", "Sample_2": "0"}])
    data = load(paths, {"waterbody_id": "MATANO"})
    assert {(r.asv_id, r.sample_id, r.reads) for r in data.reads} == {
        ("OTU_01", "Sample_1", 5),
        ("OTU_01", "Sample_2", 0),
    }


def test_D038_columns_found_by_content_when_names_unknown():
    rows = [
        {"kode": "A1", "spl": "S1", "n": "12"},
        {"kode": "A2", "spl": "S2", "n": "3"},
    ]
    renamed, mapping = map_table(rows, "reads", {"S1", "S2"})
    assert mapping.columns == {"reads": "n", "sample_id": "spl", "asv_id": "kode"}
    assert renamed[0] == {"reads": "12", "sample_id": "S1", "asv_id": "A1"}


def test_D038_roles_from_headers():
    assert detect_role(list(READS[0]), READS) == "reads"
    assert detect_role(list(META[0]), META) == "metadata"
    rows = taxonomy_rows("Genus alpha", "Genus beta")
    assert detect_role(list(rows[0]), rows) == "taxonomy"


@pytest.mark.parametrize(
    "value,expected",
    [
        ("12S MiFish", "12S_MiFish_U"),
        ("MiFish-U", "12S_MiFish_U"),
        ("MiFish-E", "MiFish-E"),
        ("CO1", "COI"),
        ("16S rRNA", "16S"),
        ("Teleo", "12S_Teleo1_V5"),
    ],
)
def test_D038_marker_normalized_only_when_unambiguous(value, expected):
    assert normalize_marker(value) == expected


def test_D038_sample_type_and_waterbody_names():
    assert normalize_sample_type("Sample") == "sampel"
    assert normalize_sample_type("PCR blank") == "kontrol_negatif_pcr"
    assert normalize_sample_type("field blank") == "kontrol_negatif_lapangan"
    assert resolve_waterbody("Danau Matano", WATERBODIES) == "MATANO"
    assert resolve_waterbody("matano", WATERBODIES) == "MATANO"
    assert resolve_waterbody("Danau Poso", WATERBODIES) == "Danau Poso"
    assert canonical("% Identity ") == "identity"


def test_D038_no_hit_claim_is_unknown_and_defaults_fingerprinted(tmp_path):
    v04 = ROOT / "data/reference/v0.4"
    rows = list(csv.DictReader(open(v04 / "sequences.csv", encoding="utf-8")))
    checklist = {
        r["species_valid"]
        for r in csv.DictReader(open(v04 / "checklist.csv", encoding="utf-8"))
        if r["waterbody_id"] == "LAUT_INDONESIA"
    }
    names = sorted({r["species_valid"] for r in rows} & checklist)[:2]
    (tmp_path / "in").mkdir()
    paths = write(tmp_path / "in", *names)
    result = run_analysis(
        paths["reads"],
        paths["metadata"],
        None,
        paths["taxonomy"],
        None,
        v04,
        out_root=tmp_path / "runs",
        defaults={"waterbody_id": "LAUT_INDONESIA"},
    )
    ranks = {c.asv_id: c.reported_rank for c in result.claims}
    assert ranks["OTU_02"] == "unknown" and ranks["OTU_01"] != "unknown"
    assert result.manifest.parameters["input_defaults"] == {"waterbody_id": "LAUT_INDONESIA"}
    # Readers of stored inputs (map points, F32 rematch) apply the same mapping and defaults.
    folder = tmp_path / "runs" / result.run_id
    assert site_points(folder) == []
    again, _ = rematch(folder, v04, DEFAULT_RULES, tmp_path / "runs")
    assert again.run_id == result.run_id
