"""Pure explainable R-NAME-03..12 [MVP]."""

from biotrace_core.config import RulesConfig
from biotrace_core.models import LabTaxonomy, NamingResult, SpeciesHit
from biotrace_core.naming.candidates import candidate_set, species_hits
from biotrace_core.reference.store import ReferenceIndex


def assign_rank(
    hits: list[SpeciesHit],
    waterbody_id: str,
    ref: ReferenceIndex,
    cfg: RulesConfig,
    lab: LabTaxonomy | None = None,
    validation: bool = False,
) -> NamingResult:
    """R-NAME-03..12. No I/O, no taxonomic knowledge beyond the supplied index."""
    ordered = species_hits(hits, cfg)
    candidates, gap = candidate_set(ordered, cfg)
    result = NamingResult()
    if ordered:
        result.best_match = ordered[0].species
        result.best_pct = ordered[0].pct
        result.gap_pct = gap
    if lab:
        result.best_match, result.best_pct = lab.taxon, lab.pct_identity
        candidates = [SpeciesHit(species=lab.taxon, pct=lab.pct_identity)]
        result.gap_pct = None
        if lab.runner_up_taxon and lab.runner_up_pct_identity is not None:
            delta = lab.pct_identity - lab.runner_up_pct_identity
            if delta <= cfg.naming.hit_window_pct:
                candidates.append(
                    SpeciesHit(species=lab.runner_up_taxon, pct=lab.runner_up_pct_identity)
                )
                result.gap_pct = 0
            else:
                result.gap_pct = delta
        result.rule_ids.append("R-NAME-12")
    if result.best_pct is None or result.best_pct < cfg.naming.unknown_below_pct:
        result.causes = ["reference"]
        result.rule_ids.append("R-NAME-03")
        return result
    result.candidates = candidates
    if len(candidates) > 1:
        result.causes.append("marker")
    aliases = {r["member_name"]: r for r in ref.tables["aliases"]}
    alias_rows = [aliases[c.species] for c in candidates if c.species in aliases]
    if (
        alias_rows
        and len(alias_rows) == len(candidates)
        and len({a["alias_key"] for a in alias_rows}) == 1
    ):
        result.reported_rank = "hybrid_alias"
        result.reported_name = alias_rows[0]["alias_label_id"]
        result.alias_key = alias_rows[0]["alias_key"]
        result.rule_ids.append("R-NAME-11")
        return result
    taxon = ref.taxa.get(result.best_match)
    if lab and lab.rank != "species":
        result.reported_rank, result.reported_name = lab.rank, lab.taxon
        result.causes.append("reference")
        return result
    if lab and not validation and (taxon is None or not taxon.in_indonesia):
        result.reported_rank = "genus"
        result.reported_name = taxon.genus if taxon else lab.taxon.split()[0]
        result.causes.append("location")
        result.rule_ids.append("R-NAME-10")
        return result
    names = {h.species for h in candidates}
    if any(name not in ref.taxa for name in names):
        result.causes.append("reference")
        result.warnings.append("candidate_taxonomy_unavailable")
        result.rule_ids.append("R-NAME-03")
        return result
    complex_match = ref.complex_for(names, waterbody_id)
    if len(names) > 1:
        if complex_match:
            result.complex_id, result.reported_name = complex_match
            result.reported_rank = "complex"
            result.rule_ids.append("R-NAME-05")
        else:
            for rank in ("genus", "family", "order"):
                shared = {getattr(ref.taxa[name], rank) for name in names}
                if len(shared) == 1 and next(iter(shared)):
                    result.reported_rank, result.reported_name = rank, next(iter(shared))
                    break
            result.rule_ids.append("R-NAME-06")
            if result.reported_rank == "unknown":
                result.causes.append("reference")
    elif result.best_pct >= cfg.naming.species_min_pct:
        result.reported_rank, result.reported_name = "species", result.best_match
        result.rule_ids.append("R-NAME-07")
    else:
        result.reported_rank, result.reported_name = "genus", taxon.genus
        result.causes.append("reference")
        result.rule_ids.append("R-NAME-09")
    if result.reported_rank in {"species", "complex"}:
        genus = taxon.genus
        missing = ref.congeners(genus, waterbody_id) - ref.available_species
        p = ref.p_missing(genus, waterbody_id)
        should_lower = bool(missing) and (
            cfg.naming.congener_gap_policy == "strict"
            or (p is not None and p >= cfg.causes["reference_cause_p_missing"])
        )
        if should_lower:
            expanded = ref.complex_for(names | missing, waterbody_id)
            if expanded and cfg.naming.congener_gap_policy == "strict":
                if result.reported_rank != "complex":
                    result.causes.append("reference")
                result.reported_rank = "complex"
                result.complex_id, result.reported_name = expanded
            else:
                result.reported_rank, result.reported_name = "genus", genus
                result.complex_id = ""
                result.causes.append("reference")
            result.rule_ids.append("R-NAME-08")
    result.causes = sorted(set(result.causes))
    return result
