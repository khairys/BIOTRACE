"""Pure R-GAP-01/02 [MVP]."""

from biotrace_core.config import RulesConfig
from biotrace_core.models import BarcodePriorityRow, Claim
from biotrace_core.reference.store import ReferenceIndex, truth


def barcode_priorities(
    claims: list[Claim], ref: ReferenceIndex, cfg: RulesConfig
) -> list[BarcodePriorityRow]:
    """R-GAP-01/02: weighted local species gaps and unknown ASVs, stable ordering."""
    result = []
    waters = {c.waterbody_id for c in claims}
    status = {r["species_valid"]: r for r in ref.tables["status"]}
    observed = {
        (c.waterbody_id, ref.taxa[c.best_match].genus)
        for c in claims
        if "reference" in c.causes and c.best_match in ref.taxa
    }
    simulated = bool(ref.manifest.get("contains_simulated"))
    seen = set()
    for row in sorted(
        ref.tables["checklist"], key=lambda r: (r["waterbody_id"], r["species_valid"])
    ):
        species, water = row["species_valid"], row["waterbody_id"]
        if (
            water not in waters
            or species not in ref.taxa
            or species in ref.available_species
            or (water, species) in seen
        ):
            continue
        seen.add((water, species))
        reasons = []
        if row["origin_status"] == "endemik":
            reasons.append("endemic")
        if status.get(species, {}).get("iucn_category") in {"CR", "EN", "VU"}:
            reasons.append("threatened")
        if (water, ref.taxa[species].genus) in observed:
            reasons.append("observed_reference_gap")
        if truth(status.get(species, {}).get("invasive_flag", False)):
            reasons.append("invasive")
        result.append(
            BarcodePriorityRow(
                type="species",
                name_or_asv=species,
                waterbody_id=water,
                score=sum(cfg.priorities[r] for r in reasons),
                reasons=reasons,
                is_simulated=simulated,
            )
        )
    unknowns: dict[tuple[str, str], list[Claim]] = {}
    for claim in claims:
        if claim.reported_rank == "unknown":
            unknowns.setdefault((claim.waterbody_id, claim.asv_id), []).append(claim)
    for (water, asv), rows in sorted(unknowns.items()):
        result.append(
            BarcodePriorityRow(
                type="asv",
                name_or_asv=asv,
                waterbody_id=water,
                reasons=["unknown"],
                sites=sorted(c.site_id for c in rows),
                total_reads=sum(c.total_reads for c in rows),
                nearest_hint=rows[0].best_match,
                is_simulated=simulated,
            )
        )
    return sorted(result, key=lambda r: (-r.score, r.name_or_asv, r.waterbody_id))
