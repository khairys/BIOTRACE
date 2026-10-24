"""Pure R-SCORE-01..07 [MVP]."""

from dataclasses import dataclass

from biotrace_core.config import RulesConfig
from biotrace_core.models import NamingResult
from biotrace_core.preprocess import Signal
from biotrace_core.reference.store import ReferenceIndex, truth


@dataclass(frozen=True)
class Score:
    l1: int
    l2: int
    l4: int
    total: int
    grade: str
    cap_reason: str
    labels: list[str]
    p_missing: float | None
    genus: str


def genus_for(name: NamingResult, ref: ReferenceIndex) -> str:
    if name.reported_rank == "genus":
        return name.reported_name
    if name.reported_rank in {"family", "order"}:
        return ""
    taxon = ref.taxa.get(name.best_match)
    return taxon.genus if taxon else ""


def score_claim(name: NamingResult, signal: Signal, ref: ReferenceIndex, cfg: RulesConfig) -> Score:
    """R-SCORE-01..07. Aggregated labels require agreement, not invented statuses."""
    genus = genus_for(name, ref)
    p_missing = ref.p_missing(genus, signal.waterbody_id) if genus else None
    score = cfg.scoring
    fraction = signal.n_pos / signal.n_rep
    l4 = (
        score.l4_single_replicate_score
        if signal.n_rep == 1
        else 2
        if fraction >= score.l4_full
        else 1
        if fraction >= score.l4_partial
        else 0
    )
    gap = name.gap_pct if name.gap_pct is not None else float("inf")
    pct = name.best_pct or 0
    l1 = (
        2
        if pct >= score.l1_high_pct and gap >= score.l1_high_gap
        else 1
        if pct >= score.l1_mid_pct and gap >= score.l1_mid_gap
        else 0
    )
    if p_missing is not None and 1 - p_missing < score.l1_penalty_ref_fraction_below:
        l1 = max(0, l1 - 1)
    if name.reported_rank == "unknown":
        l1 = 0
    checklist = ref.checklist(signal.waterbody_id)
    by_species = {r["species_valid"]: r for r in checklist}
    if name.reported_rank == "hybrid_alias":
        l2 = int(f"alias:{name.alias_key}" in by_species or name.alias_key in by_species)
    elif name.reported_rank == "species":
        l2 = int(name.reported_name in by_species)
    elif name.reported_rank in {"genus", "family", "order"}:
        l2 = int(
            any(
                getattr(ref.taxa[r["species_valid"]], name.reported_rank) == name.reported_name
                for r in checklist
                if r["species_valid"] in ref.taxa
            )
        )
    elif name.reported_rank == "complex":
        members = {
            r["member_species"]
            for r in ref.tables["complexes"]
            if r["complex_id"] == name.complex_id
        }
        l2 = int(bool(members & by_species.keys()))
    else:
        l2 = 0
    labels = []
    candidates = [c.species for c in name.candidates]
    statuses = {r["species_valid"]: r for r in ref.tables["status"]}
    if name.reported_rank != "unknown" and candidates:
        if all(by_species.get(n, {}).get("origin_status") == "endemik" for n in candidates):
            labels.append("endemic")
        if all(statuses.get(n, {}).get("iucn_category") in {"CR", "EN", "VU"} for n in candidates):
            labels.append("threatened")
        if all(truth(statuses.get(n, {}).get("invasive_flag", False)) for n in candidates):
            labels.append("invasive")
    if name.reported_rank == "hybrid_alias":
        labels.extend(["hybrid_alias", "invasive"])
    if name.reported_rank not in {"species", "hybrid_alias"} and genus:
        missing = ref.congeners(genus, signal.waterbody_id) - ref.available_species
        if any(by_species.get(n, {}).get("origin_status") == "endemik" for n in missing):
            labels.append("possible_unreferenced_endemic")
    cap = []
    if signal.in_negative_control:
        cap.append("negative_control")
    if signal.total_reads < score.min_total_reads:
        cap.append("low_reads")
    total = l1 + l2 + l4
    grade = "D" if cap else score.grade_map[total]
    return Score(l1, l2, l4, total, grade, ";".join(cap), sorted(set(labels)), p_missing, genus)
