"""D-033 (r0.4): foreign-specimen and secondary-source evidence is usable but never safe."""

import pytest

from biotrace_core.assessment import assess
from biotrace_core.config import DEFAULT_RULES, load_reasons, load_rules
from biotrace_core.decision import cap_secondary, weak_evidence
from biotrace_core.models import ReferenceSequence, SpeciesHit, Taxon
from biotrace_core.preprocess import Signal
from biotrace_core.reference.store import ReferenceIndex
from scripts.make_demo_data import demo_tables

R03 = DEFAULT_RULES.parent / "rules_r0.3.yaml"
R04 = DEFAULT_RULES.parent / "rules_r0.4.yaml"


def normal_ref(country: str, quality: str = "primer") -> ReferenceIndex:
    """FX-1 tables re-labelled as a normal-mode module; only the D-033 fields vary."""
    tables, fasta, _ = demo_tables()
    rows = []
    for r in tables["sequences"]:
        rows.append({**r, "is_simulated": False, "specimen_country": country})
    for row in tables["checklist"]:
        row["source_quality"] = quality
    taxa = {
        r["species_valid"]: Taxon.model_validate({**r, "is_simulated": False})
        for r in tables["taxa"]
    }
    return ReferenceIndex(
        {"reference_version": "FX1-uji", "module": "ID", "marker": "12S_MiFish_U"},
        taxa,
        [ReferenceSequence.model_validate(r) for r in rows],
        fasta,
        tables,
    )


def species_claim(ref: ReferenceIndex, cfg):
    selected = ref.select(cfg, "normal", "12S_MiFish_U")
    seq = {r.species_valid: r.seq_id for r in selected.eligible}
    hit = SpeciesHit(species="Gobio delta", pct=100, bitscore=300, seq_id=seq["Gobio delta"])
    return assess(
        Signal("A", "S", "MATANO", 3, 3, 500, False), [hit], selected, cfg, load_reasons()
    )


def test_R_NAME_01_foreign_specimens_excluded_r03_flagged_r04():
    ref = normal_ref("JP")
    assert ref.select(load_rules(R03), "normal", "12S_MiFish_U").eligible == []
    assert ref.select(load_rules(R04), "normal", "12S_MiFish_U").eligible


def test_R_DEC_09_indonesian_specimen_stays_safe():
    claim = species_claim(normal_ref("ID"), load_rules(R04))
    assert claim.reported_rank == "species" and claim.grade in {"A", "B"}
    assert claim.decision == "safe"
    assert "specimen_outside_indonesia" not in claim.warnings


@pytest.mark.parametrize(
    "country,quality,warning",
    [
        ("JP", "primer", "specimen_outside_indonesia"),
        ("", "primer", "specimen_outside_indonesia"),
        ("ID", "sekunder", "checklist_secondary_source"),
        ("ID", "berita", "checklist_secondary_source"),
    ],
)
def test_R_DEC_09_weak_evidence_never_safe(country, quality, warning):
    claim = species_claim(normal_ref(country, quality), load_rules(R04))
    assert claim.decision == "with_note" and claim.decision_rule == "R-DEC-09"
    assert warning in claim.warnings and "reference" in claim.causes
    assert claim.grade in {"A", "B"}  # grade is unchanged; only the decision is capped


def test_D033_pure_helpers():
    assert weak_evidence([], ["primer"]) == []
    assert weak_evidence(["ID", "JP"], []) == []  # one Indonesian specimen is enough
    assert cap_secondary("must_verify", "R-DEC-03", "x", ["checklist_secondary_source"]) == (
        "must_verify",
        "R-DEC-03",
        "x",
    )
