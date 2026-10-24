"""Pure orchestration of R-NAME/R-SCORE/R-CAUSE/R-DEC/R-ORIG [MVP]."""

from biotrace_core.causes import identify_causes
from biotrace_core.config import RulesConfig
from biotrace_core.decision import cap_secondary, decide, weak_evidence
from biotrace_core.models import Claim, LabTaxonomy, SpeciesHit
from biotrace_core.naming.rules import assign_rank
from biotrace_core.origin import origin_text
from biotrace_core.preprocess import Signal
from biotrace_core.reference.store import ReferenceIndex
from biotrace_core.scoring import score_claim


def assess(
    signal: Signal,
    hits: list[SpeciesHit],
    ref: ReferenceIndex,
    cfg: RulesConfig,
    templates: dict[str, dict[str, str]],
    lab: LabTaxonomy | None = None,
    context: list[str] | None = None,
    validation: bool = False,
) -> Claim:
    """F8–F23: all rule calculations stay in pure functions, explanations included."""
    name = assign_rank(hits, signal.waterbody_id, ref, cfg, lab, validation)
    score = score_claim(name, signal, ref, cfg)
    causes = identify_causes(name, signal, score, cfg)
    decision, rule, follow_up = decide(name, score, causes)
    keys = ["l1", "l2", "l4"]
    rule_explanations = {
        "R-NAME-03": "unknown",
        "R-NAME-05": "complex",
        "R-NAME-06": "lca",
        "R-NAME-08": "congener_gap",
        "R-NAME-09": "mid_identity",
        "R-NAME-10": "not_in_indonesia",
        "R-NAME-11": "alias",
        "R-NAME-12": "lab_db",
    }
    keys.extend(rule_explanations[r] for r in name.rule_ids if r in rule_explanations)
    if "negative_control" in score.cap_reason:
        keys.append("neg_control")
    if "low_reads" in score.cap_reason:
        keys.append("low_reads")
    keys.append("limit")
    params = {
        "l1": score.l1,
        "l2": score.l2,
        "l4": score.l4,
        "best_pct": f"{name.best_pct:.2f}" if name.best_pct is not None else "tidak ada",
        "gap": f"{name.gap_pct:.2f}%"
        if name.gap_pct is not None
        else "tidak ada kandidat di luar jendela",
        "waterbody": signal.waterbody_id,
        "n_pos": signal.n_pos,
        "n_rep": signal.n_rep,
        "reads": signal.total_reads,
        "unknown_below_pct": cfg.naming.unknown_below_pct,
        "species_min_pct": cfg.naming.species_min_pct,
        "min_total_reads": cfg.scoring.min_total_reads,
        "name": name.reported_name,
        "rank": name.reported_rank,
    }
    names = {h.species for h in name.candidates}
    support = (
        []
        if lab
        else [r for r in ref.eligible if r.seq_id in {h.seq_id for h in hits if h.species in names}]
    )
    levels = sorted(r.voucher_level for r in support)
    origin = origin_text(name, signal.waterbody_id, ref, context or [])
    warnings = list(name.warnings)
    if signal.n_rep == 1:
        warnings.append("single_replicate")
    if score.p_missing is None:
        warnings.append("genus_not_in_checklist" if score.genus else "no_single_genus_for_coverage")
    if support and any(r.voucher_level == "V3" for r in support):
        warnings.append("voucher_V3_without_physical_catalog")
    if cfg.evidence.get("secondary_source_cap", False):
        taxa_used = names | {name.reported_name}
        qualities = [
            row.get("source_quality") or "primer"
            for row in ref.checklist(signal.waterbody_id)
            if row["species_valid"] in taxa_used
        ]
        weak = weak_evidence([r.specimen_country for r in support], qualities)
        warnings.extend(weak)
        decision, rule, follow_up = cap_secondary(decision, rule, follow_up, weak)
        if weak and "reference" not in causes:
            causes = sorted([*causes, "reference"])
    return Claim(
        claim_id=f"{signal.site_id}__{signal.asv_id}",
        site_id=signal.site_id,
        waterbody_id=signal.waterbody_id,
        asv_id=signal.asv_id,
        taxon_lab=lab.taxon if lab else "",
        best_match=name.best_match,
        best_pct=name.best_pct,
        gap_pct=name.gap_pct,
        candidates=name.candidates,
        reported_name=name.reported_name,
        reported_rank=name.reported_rank,
        complex_id=name.complex_id,
        l1=score.l1,
        l2=score.l2,
        l4=score.l4,
        total=score.total,
        grade=score.grade,
        cap_reason=score.cap_reason,
        labels=score.labels,
        p_missing=score.p_missing,
        causes=causes,
        decision=decision,
        decision_rule=rule,
        follow_up=follow_up,
        reasons_id=[templates[k]["id"].format(**params) for k in keys],
        reasons_en=[templates[k]["en"].format(**params) for k in keys],
        voucher_support=levels[0] if levels else None,
        supporting_seq_ids=sorted(r.seq_id for r in support),
        supporting_accessions=sorted({a for r in support for a in r.accession.split(";") if a}),
        n_rep=signal.n_rep,
        n_pos=signal.n_pos,
        total_reads=signal.total_reads,
        in_negative_control=signal.in_negative_control,
        assessed_with_lab_database=lab is not None,
        origin_status=origin[0],
        origin_pathway=origin[1],
        origin_other_sources=origin[2],
        is_simulated=bool(ref.manifest.get("contains_simulated")),
        warnings=sorted(set(warnings)),
        rule_ids=name.rule_ids + [rule],
        interpretation_limit=cfg.interpretation_limit,
    )
