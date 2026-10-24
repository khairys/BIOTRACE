"""Pure R-NAME-02/04 deterministic hit ordering."""

from biotrace_core.config import RulesConfig
from biotrace_core.models import SpeciesHit


def species_hits(hits: list[SpeciesHit], cfg: RulesConfig) -> list[SpeciesHit]:
    """R-NAME-02: one best hit per species, stable ties on seq_id."""
    result = {}
    for hit in sorted(hits, key=lambda h: (-h.pct, -h.bitscore, h.seq_id, h.species)):
        if hit.query_coverage >= cfg.naming.min_query_coverage:
            result.setdefault(hit.species, hit)
    return list(result.values())


def candidate_set(
    hits: list[SpeciesHit], cfg: RulesConfig
) -> tuple[list[SpeciesHit], float | None]:
    """R-NAME-04: gap is measured to the best species OUTSIDE the window."""
    if not hits:
        return [], None
    best = hits[0].pct
    candidates = [h for h in hits if h.pct >= best - cfg.naming.hit_window_pct]
    outside = [h for h in hits if h.pct < best - cfg.naming.hit_window_pct]
    return candidates, best - outside[0].pct if outside else None
