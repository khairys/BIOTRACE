"""Pure R-PRE-02..05 [MVP] preparation of site × ASV claims."""

from collections import defaultdict
from dataclasses import dataclass

from biotrace_core.config import RulesConfig
from biotrace_core.models import ReadRow, Sample


@dataclass(frozen=True)
class Signal:
    asv_id: str
    site_id: str
    waterbody_id: str
    n_rep: int
    n_pos: int
    total_reads: int
    in_negative_control: bool


def preprocess(
    reads: list[ReadRow], samples: list[Sample], cfg: RulesConfig
) -> tuple[list[Signal], int]:
    """R-PRE-02..05: tag jump, extraction-batch blanks and stable claim formation."""
    sample_map = {s.sample_id: s for s in samples}
    totals: dict[str, int] = defaultdict(int)
    for row in reads:
        totals[row.asv_id] += row.reads
    positive = []
    removed = 0
    for row in reads:
        if 0 < row.reads < cfg.preprocess["tag_jump_fraction"] * totals[row.asv_id]:
            removed += 1
        elif row.reads > 0:
            positive.append(row)
    negatives = {
        (row.asv_id, sample_map[row.sample_id].extraction_batch)
        for row in positive
        if sample_map[row.sample_id].sample_type.startswith("kontrol_negatif")
    }
    sites: dict[str, list[Sample]] = defaultdict(list)
    groups: dict[tuple[str, str], list[ReadRow]] = defaultdict(list)
    for sample in samples:
        if sample.sample_type == "sampel":
            sites[sample.site_id].append(sample)
    for row in positive:
        sample = sample_map[row.sample_id]
        if sample.sample_type == "sampel":
            groups[(sample.site_id, row.asv_id)].append(row)
    claims = []
    for (site, asv), rows in sorted(groups.items()):
        batches = {sample_map[r.sample_id].extraction_batch for r in rows}
        claims.append(
            Signal(
                asv,
                site,
                sites[site][0].waterbody_id,
                len(sites[site]),
                len(rows),
                sum(r.reads for r in rows),
                any((asv, b) in negatives for b in batches),
            )
        )
    return claims, removed
