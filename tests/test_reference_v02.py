"""Reference v0.2 (Herder 2012 / Tantu 2007 checklist) [MVP]: A2, A12, A14 guards."""

import hashlib
import json

from biotrace_core.config import ROOT, load_rules
from biotrace_core.io.loaders import read_table
from biotrace_core.reference.store import coverage, load_reference

V02 = ROOT / "data/reference/v0.2"
TRANSCRIPTION = ROOT / "data/curation/malili_introduced_v0.2/transcription.csv"


def test_v02_loads_in_normal_mode_without_simulation():
    ref = load_reference(V02, "normal")
    assert ref.manifest["module"] == "ID" and not ref.manifest["contains_simulated"]
    assert ref.sequences == []  # no MiFish source yet; nothing invented
    rows = coverage(ref.select(load_rules(), "normal", "12S_MiFish_U"))
    assert rows and all(r.r == 0 and not r.is_simulated for r in rows)


def test_A14_every_name_comes_from_the_transcribed_sources():
    transcribed = {r["species_valid"] for r in read_table(TRANSCRIPTION) if r["include"] == "ya"}
    sources = {r["source_id"] for r in read_table(V02 / "sources.csv")}
    taxa = {r["species_valid"] for r in read_table(V02 / "taxa.csv")}
    for row in read_table(V02 / "checklist.csv"):
        assert row["species_valid"] in transcribed
        assert row["species_valid"] in taxa or row["species_valid"].startswith("alias:")
        assert set(row["source_id"].split(";")) <= sources
        assert row["origin_status"] == "introduksi"
    assert taxa <= transcribed


def test_A12_v01_snapshot_untouched():
    manifest = json.loads((ROOT / "data/reference/v0.1/manifest.json").read_text("utf-8"))
    for name, digest in manifest["files"].items():
        path = ROOT / "data/reference/v0.1" / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
