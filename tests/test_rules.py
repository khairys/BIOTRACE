"""Rule boundaries, candidate ambiguity and deterministic tie handling [MVP]."""

import pytest

from biotrace_core.assessment import assess
from biotrace_core.config import DEFAULT_RULES, load_rules
from biotrace_core.models import LabTaxonomy, NamingResult, ReadRow, Sample, SpeciesHit
from biotrace_core.naming.candidates import candidate_set, species_hits
from biotrace_core.naming.rules import assign_rank
from biotrace_core.preprocess import Signal, preprocess
from biotrace_core.scoring import score_claim


@pytest.mark.parametrize(
    "pct,rank", [(94.999, "unknown"), (95, "genus"), (97.999, "genus"), (98, "species")]
)
def test_R_NAME_03_07_09_identity_boundaries(pct, rank, ref, cfg, hit):
    assert assign_rank([hit("Gobio epsilon", pct)], "MATANO", ref, cfg).reported_rank == rank


def test_R_NAME_02_one_hit_per_species_stable_tie(cfg):
    rows = [SpeciesHit(species="SIM alpha", pct=99, bitscore=100, seq_id=s) for s in ["Z", "A"]]
    assert species_hits(rows, cfg)[0].seq_id == "A"
    assert species_hits(list(reversed(rows)), cfg) == species_hits(rows, cfg)


def test_R_NAME_02_min_coverage(cfg, hit):
    assert species_hits([hit("Gobio delta", 100, coverage=0.8999)], cfg) == []
    assert len(species_hits([hit("Gobio delta", 100, coverage=0.9)], cfg)) == 1


def test_R_NAME_04_window_and_gap(cfg, hit):
    candidates, gap = candidate_set(
        [hit("Gobio delta", 100), hit("Gobio epsilon", 99.5), hit("Gobio lambda", 99.49)], cfg
    )
    assert len(candidates) == 2
    assert gap == pytest.approx(0.51)


def test_R_NAME_05_08_complex_missing_member(ref, cfg, hit):
    name = assign_rank([hit("Piscis alpha", 100)], "MATANO", ref, cfg)
    assert name.reported_rank == "complex"
    assert "reference" in name.causes


def test_R_NAME_08_strict_vs_threshold(ref, cfg, hit):
    strict = assign_rank([hit("Rasbo zeta", 100)], "MATANO", ref, cfg)
    assert strict.reported_rank == "genus"
    threshold = cfg.model_copy(deep=True)
    threshold.naming.congener_gap_policy = "threshold"
    threshold.causes["reference_cause_p_missing"] = 0.6
    assert (
        assign_rank([hit("Rasbo zeta", 100)], "MATANO", ref, threshold).reported_rank == "species"
    )


def test_R_NAME_06_lca_and_no_shared_order(ref, cfg, hit):
    result = assign_rank([hit("Gobio delta", 100), hit("Tilapa omega", 100)], "MATANO", ref, cfg)
    assert result.reported_rank == "order"
    ref.taxa["Tilapa omega"].order = "Ordo_berbeda_SIMULASI"
    assert (
        assign_rank(
            [hit("Gobio delta", 100), hit("Tilapa omega", 100)], "MATANO", ref, cfg
        ).reported_rank
        == "unknown"
    )


def test_R_NAME_12_lab_rank_never_promoted(ref, cfg):
    lab = LabTaxonomy(
        asv_id="SIM", taxon="Gobio", rank="genus", pct_identity=100, is_simulated=True
    )
    assert assign_rank([], "MATANO", ref, cfg, lab).reported_rank == "genus"


def test_R_SCORE_01_single_replicate(ref, cfg):
    name = NamingResult(
        reported_name="Gobio delta", reported_rank="species", best_match="Gobio delta", best_pct=100
    )
    score = score_claim(name, Signal("A", "S", "MATANO", 1, 1, 10, False), ref, cfg)
    assert score.l4 == 1


@pytest.mark.parametrize(
    "rules,labels,decision",
    [
        ("rules_r0.2.yaml", [], "do_not_use"),
        ("rules_r0.3.yaml", ["possible_endemic"], "must_verify"),
    ],
)
def test_R_SCORE_04_R_DEC_03_possible_endemic_mixed_candidates(
    rules, labels, decision, ref, reasons, hit
):
    """D-030: Gobio delta (endemik) + Gobio epsilon (asli) share a genus claim."""
    cfg = load_rules(DEFAULT_RULES.parent / rules)
    claim = assess(
        Signal("A", "S", "MATANO", 3, 3, 5, False),  # low reads → D (R-SCORE-06)
        [hit("Gobio delta", 100), hit("Gobio epsilon", 100)],
        ref,
        cfg,
        reasons,
    )
    assert claim.reported_rank == "genus"
    assert claim.grade == "D"
    assert [x for x in claim.labels if x == "possible_endemic"] == labels
    assert claim.decision == decision


def test_R_SCORE_04_possible_endemic_not_added_when_all_agree(ref, cfg, hit):
    """D-030: a full endemic label never gets the weaker mixed label as well."""
    name = NamingResult(
        reported_name="Gobio delta",
        reported_rank="species",
        best_match="Gobio delta",
        best_pct=100,
        candidates=[hit("Gobio delta", 100)],
    )
    labels = score_claim(name, Signal("A", "S", "MATANO", 3, 3, 100, False), ref, cfg).labels
    assert "endemic" in labels and "possible_endemic" not in labels


@pytest.mark.parametrize(
    "reads,negative,grade", [(9, False, "D"), (10, False, "A"), (100, True, "D")]
)
def test_R_SCORE_06_cap_boundaries(reads, negative, grade, ref, cfg):
    name = NamingResult(
        reported_name="Gobio delta", reported_rank="species", best_match="Gobio delta", best_pct=100
    )
    assert (
        score_claim(name, Signal("A", "S", "MATANO", 3, 3, reads, negative), ref, cfg).grade
        == grade
    )


def test_R_SCORE_07_null_without_denominator(ref, cfg):
    name = NamingResult(best_match="Gobio delta")
    assert (
        score_claim(name, Signal("A", "S", "NO_CHECKLIST", 3, 3, 10, False), ref, cfg).p_missing
        is None
    )


def test_R_CAUSE_05_fallback_single_replicate(ref, cfg, reasons, hit):
    claim = assess(
        Signal("A", "S", "MATANO", 1, 1, 100, False), [hit("Gobio epsilon", 100)], ref, cfg, reasons
    )
    assert claim.causes == ["sample"]
    assert "single_replicate" in claim.warnings


def test_R_PRE_02_03_04_batch_isolation(cfg):
    base = Sample(
        sample_id="S1",
        site_id="SITE1",
        waterbody_id="MATANO",
        latitude=0,
        longitude=0,
        collection_date="2026-10-24",
        sample_type="sampel",
        replicate=1,
        extraction_batch="B1",
        marker="12S_MiFish_U",
        is_simulated=True,
    )
    samples = [
        base,
        base.model_copy(update={"sample_id": "S2", "site_id": "SITE2", "extraction_batch": "B2"}),
        base.model_copy(update={"sample_id": "N", "sample_type": "kontrol_negatif_pcr"}),
    ]
    rows = [
        ReadRow(asv_id="A", sample_id=s, reads=n, is_simulated=True)
        for s, n in [("S1", 1000), ("S2", 1000), ("N", 10)]
    ]
    signals, removed = preprocess(rows, samples, cfg)
    assert [s.in_negative_control for s in signals] == [True, False]
    assert removed == 0
    rows[-1] = rows[-1].model_copy(update={"reads": 1})
    signals, removed = preprocess(rows, samples, cfg)
    assert not any(s.in_negative_control for s in signals)
    assert removed == 1


def test_R_ORIG_01_context_is_qualified(ref, cfg, reasons, hit):
    claim = assess(
        Signal("A", "S", "MATANO", 3, 3, 100, False),
        [hit("Tilapa omega", 100)],
        ref,
        cfg,
        reasons,
        context=["keramba - SIMULASI"],
    )
    assert "Kemungkinan" in claim.origin_status
    assert "budidaya" in claim.origin_pathway
    assert "keramba" in claim.origin_other_sources
