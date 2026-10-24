"""Pure R-DEC-01..08 [MVP]; priority is part of the public rule contract."""

from biotrace_core.models import Decision, NamingResult
from biotrace_core.scoring import Score

DECISIONS: dict[str, tuple[str, str]] = {
    "safe": ("Aman dilaporkan", "Boleh dimasukkan ke dokumen pada tingkat nama yang tertera."),
    "with_note": (
        "Dengan catatan",
        "Tulis pada tingkat nama yang aman; sertakan catatan penyebab dan cek kemungkinan sumber DNA lain.",
    ),
    "must_verify": (
        "Wajib verifikasi",
        "Jangan dijadikan kesimpulan sebelum dicek: marker kedua (COI/16S), survei tangkap, atau barcode spesimen voucher.",
    ),
    "do_not_use": (
        "Jangan dipakai",
        "Tinjau batch ekstraksi dan kontrol; ulang PCR; abaikan data nyasar.",
    ),
}


def decide(name: NamingResult, score: Score, causes: list[str]) -> tuple[Decision, str, str]:
    """R-DEC-01..08: first matching decision wins; additional cautions are retained."""
    sensitive = bool(set(score.labels) & {"endemic", "threatened", "invasive", "hybrid_alias"})
    if name.reported_rank == "unknown":
        decision, rule = (
            ("do_not_use", "R-DEC-05") if "sample" in causes else ("with_note", "R-DEC-06")
        )
    elif (
        score.grade in {"A", "B"}
        and name.reported_rank in {"species", "hybrid_alias"}
        and score.l2 == 0
    ):
        decision, rule = ("must_verify" if sensitive else "with_note"), "R-DEC-08"
    elif score.grade in {"A", "B"}:
        decision, rule = "safe", "R-DEC-01"
    elif sensitive:
        decision, rule = "must_verify", "R-DEC-03"
    elif score.grade == "C":
        decision, rule = "with_note", "R-DEC-02"
    else:
        decision, rule = "do_not_use", "R-DEC-04"
    text = DECISIONS[decision][1]
    if rule == "R-DEC-06":
        text = "Ikan tidak dikenal, kemungkinan belum ada di kamus. " + text
    if "invasive" in score.labels and score.grade in {"C", "D"}:
        text += " Jangan dijadikan dasar pemberantasan sebelum dicek."
    if "endemic" in score.labels and score.grade == "D":
        text += " Klaim tidak dibuang agar tidak berujung kesimpulan 'tidak ada' yang keliru."
    if "possible_unreferenced_endemic" in score.labels:
        text += " Kemungkinan ikan endemik yang belum ada di kamus."
    return decision, rule, text
