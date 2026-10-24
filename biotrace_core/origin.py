"""Pure R-ORIG-01/02 [MVP]: source-qualified possibilities only."""

from biotrace_core.models import NamingResult
from biotrace_core.reference.store import ReferenceIndex


def origin_text(
    name: NamingResult, waterbody: str, ref: ReferenceIndex, context: list[str]
) -> tuple[str, str, str]:
    """R-ORIG-01/02. Never assigns a population or river of origin."""
    keys = {c.species for c in name.candidates} | {name.reported_name, f"alias:{name.alias_key}"}
    statuses = sorted(
        {r["origin_status"] for r in ref.checklist(waterbody) if r["species_valid"] in keys}
    )
    pathways = sorted(
        {
            r["pathway"]
            for r in ref.tables["introductions"]
            if r["waterbody_id"] == waterbody and r["species_valid"] in keys
        }
    )
    return (
        "Kemungkinan status menurut checklist: " + (", ".join(statuses) or "tidak tercatat"),
        "Kemungkinan jalur tercatat: " + (", ".join(pathways) or "tidak tersedia dalam sumber"),
        "Kemungkinan sumber DNA lain: "
        + (
            "; ".join(sorted(context))
            if context
            else "aliran dari hulu, keramba, atau limbah pasar; belum diverifikasi di lokasi."
        ),
    )
