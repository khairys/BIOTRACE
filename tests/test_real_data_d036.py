"""D-035/D-036: kamus nasional v0.4 dan data eDNA asli Marwayana 2022 [MVP]."""

import csv

from biotrace_core.config import ROOT, load_rules
from biotrace_core.io.loaders import read_table
from biotrace_core.models import Sample
from biotrace_core.reference.store import load_reference

REAL = ROOT / "data/edna_asli/marwayana2022_mifishu"
V04 = ROOT / "data/reference/v0.4"


def test_D036_blank_coordinates_are_missing_not_guessed():
    rows = read_table(REAL / "metadata.csv")
    samples = [
        Sample.model_validate({k: v for k, v in r.items() if v != "" or k != "replicate"})
        for r in rows
    ]
    assert samples and all(s.latitude is None and s.longitude is None for s in samples)
    assert all(not s.is_simulated for s in samples)
    assert {s.sample_type for s in samples} == {"sampel", "kontrol_negatif_ekstraksi"}
    assert "SIMULASI" not in " ".join(p.name for p in REAL.iterdir())


def test_D036_reads_unique_and_above_engine_threshold():
    reads = list(csv.DictReader(open(REAL / "reads.csv", encoding="utf-8")))
    pairs = [(r["asv_id"], r["sample_id"]) for r in reads]
    assert len(pairs) == len(set(pairs))
    field = {
        r["sample_id"] for r in read_table(REAL / "metadata.csv") if r["sample_type"] == "sampel"
    }
    totals: dict[str, int] = {}
    for r in reads:
        if r["sample_id"] in field:
            totals[r["asv_id"]] = totals.get(r["asv_id"], 0) + int(r["reads"])
    assert min(totals.values()) >= load_rules().scoring.min_total_reads


def test_D035_v04_normal_mode_indonesian_species_only():
    cfg = load_rules()
    ref = load_reference(V04, "normal").select(cfg, "normal", "12S_MiFish_U")
    assert ref.manifest["module"] == "ID" and not ref.manifest.get("contains_simulated")
    assert len(ref.eligible) >= 900
    assert all(ref.taxa[r.species_valid].in_indonesia for r in ref.eligible)
    assert all(r.region_trimmed and r.voucher_level != "V4" for r in ref.eligible)
    assert any(r.specimen_country == "ID" for r in ref.eligible)
