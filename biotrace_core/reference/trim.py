"""R-CUR-05: deterministic in-silico trimming with explicitly versioned primers."""

from biotrace_core.config import RulesConfig


def reverse_complement(sequence: str) -> str:
    return sequence.translate(str.maketrans("ACGTRYSWKMBDHVN", "TGCAYRSWMKVHDBN"))[::-1]


def trim_mifish(sequence: str, cfg: RulesConfig) -> str | None:
    """R-CUR-05. Return the insert without primer sites; no guessed partial match."""
    forward = str(cfg.curation["forward_primer"])
    reverse = reverse_complement(str(cfg.curation["reverse_primer"]))
    limit = int(cfg.curation["primer_max_mismatches"])
    choices = []
    for strand in (sequence.upper(), reverse_complement(sequence.upper())):
        positions = []
        for primer in (forward, reverse):
            positions.append(
                [
                    (
                        i,
                        sum(
                            a != b
                            for a, b in zip(strand[i : i + len(primer)], primer, strict=False)
                        ),
                    )
                    for i in range(len(strand) - len(primer) + 1)
                    if sum(
                        a != b for a, b in zip(strand[i : i + len(primer)], primer, strict=False)
                    )
                    <= limit
                ]
            )
        for start, f_mismatches in positions[0]:
            for end, r_mismatches in positions[1]:
                if end > start + len(forward):
                    insert = strand[start + len(forward) : end]
                    choices.append((f_mismatches + r_mismatches, start, end, insert))
    return min(choices)[3] if choices else None
