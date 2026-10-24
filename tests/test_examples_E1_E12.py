"""T-EX: E1–E12 [MVP]. E9 uses fictional Hybridus instead of unsourced real names."""

import pytest

from biotrace_core.assessment import assess
from biotrace_core.models import LabTaxonomy
from biotrace_core.preprocess import Signal

CASES = [
    (
        "E1",
        [("Gobio delta", 99.6), ("Gobio epsilon", 97.9)],
        3,
        1200,
        False,
        "species",
        (2, 1, 2),
        "A",
        [],
        ["endemic"],
        "safe",
    ),
    (
        "E2",
        [("Piscis alpha", 99.6), ("Piscis beta", 99.4), ("Tilapa omega", 85)],
        3,
        800,
        False,
        "complex",
        (2, 1, 2),
        "A",
        ["marker"],
        ["endemic", "possible_unreferenced_endemic"],
        "safe",
    ),
    (
        "E3",
        [("Piscis alpha", 99.8), ("Piscis beta", 98.9)],
        2,
        500,
        False,
        "complex",
        (1, 1, 1),
        "C",
        ["reference"],
        ["endemic", "possible_unreferenced_endemic"],
        "must_verify",
    ),
    (
        "E4",
        [("Rasbo zeta", 99.5), ("Rasbo iota", 97)],
        3,
        900,
        False,
        "genus",
        (2, 1, 2),
        "A",
        ["reference"],
        [],
        "safe",
    ),
    (
        "E5",
        [("Rasbo iota", 91.2)],
        3,
        300,
        False,
        "unknown",
        (0, 0, 2),
        "C",
        ["reference"],
        [],
        "with_note",
    ),
    (
        "E6",
        [("Rasbo iota", 91.2)],
        3,
        300,
        True,
        "unknown",
        (0, 0, 2),
        "D",
        ["reference", "sample"],
        [],
        "do_not_use",
    ),
    (
        "E7",
        [("Gobio epsilon", 96.5)],
        3,
        400,
        False,
        "genus",
        (0, 1, 2),
        "C",
        ["reference"],
        [],
        "with_note",
    ),
    (
        "E8",
        [("Tilapa omega", 99.9), ("Gobio epsilon", 96.9)],
        3,
        2000,
        True,
        "species",
        (2, 1, 2),
        "D",
        ["sample"],
        ["invasive"],
        "must_verify",
    ),
    (
        "E9",
        [],
        3,
        600,
        False,
        "hybrid_alias",
        (0, 1, 2),
        "C",
        ["marker"],
        ["hybrid_alias", "invasive"],
        "must_verify",
    ),
    (
        "E10",
        [],
        3,
        700,
        False,
        "genus",
        (2, 1, 2),
        "A",
        ["location"],
        ["possible_unreferenced_endemic"],
        "safe",
    ),
    (
        "E11",
        [("Gobio delta", 99.6), ("Gobio epsilon", 97.9)],
        1,
        7,
        False,
        "species",
        (2, 1, 0),
        "D",
        ["sample"],
        ["endemic"],
        "must_verify",
    ),
    (
        "E12",
        [("Gobio lambda", 99.7), ("Gobio epsilon", 97.7)],
        3,
        1000,
        False,
        "species",
        (2, 0, 2),
        "B",
        ["location"],
        [],
        "with_note",
    ),
]


@pytest.mark.parametrize(
    "case,values,npos,reads,negative,rank,scores,grade,causes,labels,decision",
    CASES,
    ids=[r[0] for r in CASES],
)
def test_R_NAME_SCORE_CAUSE_DEC_E1_E12(
    case,
    values,
    npos,
    reads,
    negative,
    rank,
    scores,
    grade,
    causes,
    labels,
    decision,
    ref,
    cfg,
    reasons,
    hit,
):
    lab = None
    if case == "E9":
        lab = LabTaxonomy(
            asv_id="SIM",
            taxon="Hybridus alpha",
            rank="species",
            pct_identity=99,
            runner_up_taxon="Hybridus beta",
            runner_up_pct_identity=98.8,
            is_simulated=True,
        )
    if case == "E10":
        lab = LabTaxonomy(
            asv_id="SIM",
            taxon="Piscis externus",
            rank="species",
            pct_identity=99.5,
            is_simulated=True,
        )
    result = assess(
        Signal("SIM", "S1", "MATANO", 3, npos, reads, negative),
        [hit(n, p) for n, p in values],
        ref,
        cfg,
        reasons,
        lab,
    )
    assert result.reported_rank == rank
    assert (result.l1, result.l2, result.l4) == scores
    assert result.grade == grade
    assert result.causes == causes
    assert result.labels == labels
    assert result.decision == decision
    assert result.is_simulated
    assert result.interpretation_limit in result.reasons_id
    if case in {"E8", "E9"}:
        assert "pemberantasan" in result.follow_up
    if case == "E11":
        assert "tidak ada" in result.follow_up
