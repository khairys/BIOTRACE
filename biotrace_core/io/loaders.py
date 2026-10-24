"""UTF-8 CSV/TSV/FASTA boundaries for F1/F2/F11 [MVP]."""

import csv
from pathlib import Path


def read_table(path: Path, delimiter: str | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if delimiter is None:
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        reader = csv.DictReader(stream, delimiter=delimiter)
        headers = reader.fieldnames
        if not headers or len(headers) != len(set(headers)):
            raise ValueError("Header kosong atau nama kolom duplikat.")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Jumlah kolom tidak konsisten.")
            if any(value.strip() for value in row.values()):
                rows.append({key: value.strip() for key, value in row.items()})
        return rows


def read_fasta(path: Path, alphabet: str = "ACGTN") -> dict[str, str]:
    sequences: dict[str, str] = {}
    current = ""
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            parts = line[1:].split()
            if not parts or parts[0] in sequences:
                raise ValueError("Header FASTA kosong atau duplikat.")
            current = parts[0]
            sequences[current] = ""
        elif current:
            if set(line.upper()) - set(alphabet):
                raise ValueError(f"Basa FASTA tidak diizinkan pada {current}.")
            sequences[current] += line.upper()
        else:
            raise ValueError("FASTA harus dimulai dengan header >asv_id.")
    if not sequences or any(not sequence for sequence in sequences.values()):
        raise ValueError("FASTA kosong atau ada sekuens tanpa basa.")
    return sequences


def write_fasta(path: Path, sequences: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for identifier, sequence in sorted(sequences.items()):
            stream.write(f">{identifier}\n{sequence}\n")


def write_table(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
