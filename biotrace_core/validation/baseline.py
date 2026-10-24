"""Pure R-VAL-01 [MVP] naive best-hit BLAST-97 comparator."""

from biotrace_core.models import SpeciesHit


def baseline_name(hits: list[SpeciesHit], species_threshold: float) -> str | None:
    ordered = sorted(hits, key=lambda h: (-h.pct, -h.bitscore, h.seq_id, h.species))
    return ordered[0].species if ordered and ordered[0].pct >= species_threshold else None
