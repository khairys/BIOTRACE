"""Reference v0.3 (v0.2 + data repo Bagus, docs/13, D-034) [MVP]: A1, A4/R-CUR-04, A5, A12, A14."""

import hashlib
import json

import pytest

from biotrace_core.config import ROOT, load_rules
from biotrace_core.io.loaders import read_table
from biotrace_core.reference.store import load_reference, truth

V03 = ROOT / "data/reference/v0.3"
TEAM_CHECKLIST = ROOT / "raw/bagus_ref_v0.1/checklist_malili.csv"
PRIMARY_SOURCES = {"SRC_HERDER2012", "SRC_TANTU2007"}


@pytest.fixture(scope="module")
def ref():
    return load_reference(V03, "normal")


def test_v03_loads_in_normal_mode_with_sequences(ref):
    assert ref.manifest["module"] == "ID" and not ref.manifest["contains_simulated"]
    eligible = ref.select(load_rules(), "normal", "12S_MiFish_U").eligible
    assert eligible and len(eligible) == ref.manifest["counts"]["sequences_accepted"]


def test_A5_no_environmental_sequences(ref):
    assert all(r.voucher_level in {"V1", "V2", "V3"} for r in ref.sequences)


def test_R_CUR_05_accepted_sequences_are_trimmed_to_mifish(ref):
    accepted = [r for r in ref.sequences if r.curation_status == "accepted"]
    assert accepted and all(r.region_trimmed and r.marker == "12S_MiFish_U" for r in accepted)


def test_R_CUR_04_only_species_recorded_in_indonesia(ref):
    for r in ref.sequences:
        assert ref.taxa[r.species_valid].in_indonesia
        if r.specimen_country != "ID":
            assert "specimen_outside_indonesia" in r.flags.split(";")
    assert all(truth(t["in_indonesia"]) for t in read_table(V03 / "taxa.csv"))


def test_A1_every_checklist_row_cites_a_recorded_source(ref):
    sources = {r["source_id"] for r in ref.tables["sources"]}
    for row in ref.tables["checklist"]:
        ids = set(row["source_id"].split(";")) - {""}
        assert ids and ids <= sources, row


def test_D033_non_primary_rows_are_labelled(ref):
    for row in ref.tables["checklist"]:
        ids = set(row["source_id"].split(";"))
        assert row["source_quality"] in {"primer", "sekunder", "berita"}
        if row["source_quality"] == "primer":
            assert ids <= PRIMARY_SOURCES
        else:
            assert not ids & PRIMARY_SOURCES


def test_A14_checklist_names_come_from_v02_or_team_table(ref):
    v02 = {r["species_valid"] for r in read_table(ROOT / "data/reference/v0.2/checklist.csv")}
    team = {r["spesies"] for r in read_table(TEAM_CHECKLIST)} - {"louhan hibrida"}
    for row in ref.tables["checklist"]:
        assert row["species_valid"] in v02 | team | {"alias:louhan_hybrid"}


def test_v02_rows_and_taxa_carried_over(ref):
    v3 = {(r["waterbody_id"], r["species_valid"]): r for r in ref.tables["checklist"]}
    for row in read_table(ROOT / "data/reference/v0.2/checklist.csv"):
        kept = v3[(row["waterbody_id"], row["species_valid"])]
        assert kept["source_quality"] == "primer" and kept["source_id"] == row["source_id"]
    v2_taxa = {r["species_valid"] for r in read_table(ROOT / "data/reference/v0.2/taxa.csv")}
    assert v2_taxa <= set(ref.taxa)


@pytest.mark.parametrize("version", ["v0.1", "v0.2"])
def test_A12_previous_snapshots_untouched(version):
    folder = ROOT / "data/reference" / version
    manifest = json.loads((folder / "manifest.json").read_text("utf-8"))
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
