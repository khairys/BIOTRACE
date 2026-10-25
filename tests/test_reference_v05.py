"""D-037 (v0.5): Rasborinae MiFish bervoucher dengan asal dari BOLD; A1, A12 guards."""

import hashlib
import json

from biotrace_core.assessment import assess
from biotrace_core.config import ROOT, load_reasons, load_rules
from biotrace_core.models import SpeciesHit
from biotrace_core.preprocess import Signal
from biotrace_core.reference.store import load_reference

V05 = ROOT / "data/reference/v0.5"


def test_D037_rasborinae_rows_have_bif_voucher_and_source():
    ref = load_reference(V05, "normal")
    rows = [r for r in ref.sequences if r.source_id == "SRC_RASBORINAE_TB2RBP00G"]
    assert rows
    for r in rows:
        assert r.voucher_catalog.startswith("BIF") and r.voucher_level == "V2"
        assert r.voucher_institution  # dari rekaman BOLD, bukan ditebak
        assert r.region_trimmed and r.marker == "12S_MiFish_U"


def test_D037_indonesian_voucher_reaches_safe_at_a_cautious_rank():
    cfg = load_rules()
    ref = load_reference(V05, "normal").select(cfg, "normal", "12S_MiFish_U")
    seq = next(
        r
        for r in ref.eligible
        if r.source_id == "SRC_RASBORINAE_TB2RBP00G" and r.specimen_country == "ID"
    )
    hit = SpeciesHit(species=seq.species_valid, pct=100, bitscore=300, seq_id=seq.seq_id)
    claim = assess(
        Signal("A", "S", "AIR_TAWAR_INDONESIA", 3, 3, 500, False), [hit], ref, cfg, load_reasons()
    )
    assert claim.decision == "safe"
    assert "specimen_outside_indonesia" not in claim.warnings


def test_A12_v04_untouched():
    manifest = json.loads((ROOT / "data/reference/v0.4/manifest.json").read_text("utf-8"))
    for name, digest in manifest["files"].items():
        path = ROOT / "data/reference/v0.4" / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
