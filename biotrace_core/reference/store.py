"""R-NAME-01, R-COV-01/02: versioned reference boundary, offline only."""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from biotrace_core.config import RulesConfig
from biotrace_core.io.loaders import read_fasta, read_table
from biotrace_core.models import CoverageRow, Mode, ReferenceSequence, Taxon

TABLES = [
    "sequences",
    "taxa",
    "waterbodies",
    "checklist",
    "status",
    "aliases",
    "complexes",
    "introductions",
    "sources",
]


def truth(value: object) -> bool:
    return str(value).lower() in {"true", "1"}


@dataclass
class ReferenceIndex:
    manifest: dict
    taxa: dict[str, Taxon]
    sequences: list[ReferenceSequence]
    fasta: dict[str, str]
    tables: dict[str, list[dict[str, str]]]
    eligible: list[ReferenceSequence] = field(default_factory=list)

    @property
    def available_species(self) -> set[str]:
        return {r.species_valid for r in self.eligible}

    def checklist(self, waterbody: str) -> list[dict[str, str]]:
        return [r for r in self.tables["checklist"] if r["waterbody_id"] == waterbody]

    def congeners(self, genus: str, waterbody: str) -> set[str]:
        return {
            r["species_valid"]
            for r in self.checklist(waterbody)
            if r["species_valid"] in self.taxa and self.taxa[r["species_valid"]].genus == genus
        }

    def p_missing(self, genus: str, waterbody: str) -> float | None:
        species = self.congeners(genus, waterbody)
        return len(species - self.available_species) / len(species) if species else None

    def complex_for(self, species: set[str], waterbody: str) -> tuple[str, str] | None:
        groups: dict[str, set[str]] = {}
        labels = {}
        for row in self.tables["complexes"]:
            if waterbody in row["waterbody_scope"].split(";"):
                groups.setdefault(row["complex_id"], set()).add(row["member_species"])
                labels[row["complex_id"]] = row["label_id"]
        for key in sorted(groups):
            if species and species <= groups[key]:
                return key, labels[key]
        return None

    def select(self, cfg: RulesConfig, mode: Mode, marker: str) -> "ReferenceIndex":
        """R-NAME-01: reject V4, mismatched markers and cross-region/simulation data."""
        simulated = bool(self.manifest.get("contains_simulated"))
        if (mode == "simulation") != simulated:
            raise ValueError("Kamus SIMULASI hanya boleh dipakai pada mode simulasi.")
        if mode == "normal" and self.manifest.get("module") != "ID":
            raise ValueError("Kamus luar Indonesia hanya boleh dipakai pada mode validasi.")
        selected = []
        for row in self.sequences:
            if (
                row.curation_status != "accepted"
                or row.voucher_level not in cfg.reference["allowed_voucher_levels"]
            ):
                continue
            if row.marker != marker or not row.region_trimmed:
                continue
            if row.species_valid not in self.taxa or not row.license:
                continue
            if mode == "normal" and (
                not self.taxa[row.species_valid].in_indonesia or row.specimen_country != "ID"
            ):
                continue
            if row.is_simulated != simulated:
                continue
            selected.append(row)
        return ReferenceIndex(
            self.manifest,
            self.taxa,
            self.sequences,
            self.fasta,
            self.tables,
            sorted(selected, key=lambda r: r.seq_id),
        )


def load_reference(path: Path, mode: Mode = "normal") -> ReferenceIndex:
    """Validate manifest and complete file hashes before consuming reference tables."""
    path = path.resolve()
    if mode == "normal" and "external" in path.parts:
        raise ValueError("Mode normal dilarang membaca data/external/.")
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    if mode == "normal" and manifest.get("module") != "ID":
        raise ValueError("Modul luar hanya boleh dimuat pada mode validasi.")
    expected = {f"{name}.csv" for name in TABLES} | {"sequences.fasta"}
    if expected - manifest.get("files", {}).keys():
        raise ValueError("Manifest tidak mencakup seluruh file kamus wajib.")
    for name, digest in manifest["files"].items():
        if Path(name).name != name or "\\" in name:
            raise ValueError("Path manifest tidak sah.")
        if hashlib.sha256((path / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Sidik jari file kamus tidak cocok: {name}.")
    tables = {name: read_table(path / f"{name}.csv") for name in TABLES}
    taxa = {r["species_valid"]: Taxon.model_validate(r) for r in tables["taxa"]}
    seqs = [ReferenceSequence.model_validate(r) for r in tables["sequences"]]
    fasta = read_fasta(path / "sequences.fasta", "ACGTNRYSWKMBDHV") if seqs else {}
    if len(taxa) != len(tables["taxa"]) or len({r.seq_id for r in seqs}) != len(seqs):
        raise ValueError("ID takson atau sekuens kamus duplikat.")
    for row in seqs:
        if row.seq_id not in fasta or len(fasta[row.seq_id]) != row.length:
            raise ValueError("FASTA kamus tidak cocok dengan metadata.")
        if row.source_id not in {r["source_id"] for r in tables["sources"]}:
            raise ValueError("Sumber sekuens tidak ditemukan.")
    if mode == "simulation" and not manifest.get("contains_simulated"):
        raise ValueError("Mode simulasi memerlukan kamus SIMULASI.")
    return ReferenceIndex(manifest, taxa, seqs, fasta, tables)


def coverage(ref: ReferenceIndex) -> list[CoverageRow]:
    """R-COV-01. Explicit checklist denominators, never inferred absences."""
    groups = {
        (row["waterbody_id"], ref.taxa[row["species_valid"]].genus)
        for row in ref.tables["checklist"]
        if row["species_valid"] in ref.taxa
    }
    result = []
    for waterbody, genus in sorted(groups):
        species = ref.congeners(genus, waterbody)
        missing = species - ref.available_species
        result.append(
            CoverageRow(
                waterbody_id=waterbody,
                genus=genus,
                n=len(species),
                r=len(species) - len(missing),
                p_missing=len(missing) / len(species),
                missing_species=sorted(missing),
                is_simulated=bool(ref.manifest.get("contains_simulated")),
            )
        )
    return result


def reference_stats(ref: ReferenceIndex) -> dict:
    """R-COV-02. Counts describe local files, not claims of validated accuracy."""
    from collections import Counter

    rows = coverage(ref)
    return {
        "reference_version": ref.manifest["reference_version"],
        "module": ref.manifest["module"],
        "marker": ref.manifest["marker"],
        "contains_simulated": bool(ref.manifest.get("contains_simulated")),
        "sequence_count": len(ref.sequences),
        "eligible_sequences": len(ref.eligible),
        "species_with_reference": len(ref.available_species),
        "by_voucher": dict(sorted(Counter(r.voucher_level for r in ref.sequences).items())),
        "by_curation": dict(sorted(Counter(r.curation_status for r in ref.sequences).items())),
        "coverage": [r.model_dump() for r in rows],
        "sources": ref.tables["sources"],
    }
