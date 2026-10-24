"""Pure R-CAUSE-01..05 [MVP]."""

from biotrace_core.config import RulesConfig
from biotrace_core.models import NamingResult
from biotrace_core.preprocess import Signal
from biotrace_core.scoring import Score


def identify_causes(
    name: NamingResult, signal: Signal, score: Score, cfg: RulesConfig
) -> list[str]:
    """R-CAUSE-01..05, including the mandatory non-species/weak-grade explanation."""
    result = set(name.causes)
    if score.p_missing is not None and score.p_missing >= cfg.causes["reference_cause_p_missing"]:
        result.add("reference")
    if (
        signal.in_negative_control
        or score.l4 == 0
        or signal.total_reads < cfg.scoring.min_total_reads
    ):
        result.add("sample")
    if score.l2 == 0 and name.reported_rank != "unknown":
        result.add("location")
    if not result and (score.grade != "A" or name.reported_rank != "species"):
        if score.l4 < 2:
            result.add("sample")
        elif score.l1 < 2:
            result.add("reference" if (name.best_pct or 0) < cfg.scoring.l1_high_pct else "marker")
        elif score.l2 < 1:
            result.add("location")
        else:
            result.add("marker")
    return sorted(result)
