"""SIMULASI-only FX-1 equivalents from 03 §11; no biological data invented."""

import pytest

from biotrace_core.config import load_reasons, load_rules
from biotrace_core.models import ReferenceSequence, SpeciesHit, Taxon
from biotrace_core.reference.store import ReferenceIndex
from scripts.make_demo_data import DEMO, demo_tables


@pytest.fixture
def cfg():
    return load_rules()


@pytest.fixture
def reasons():
    return load_reasons()


@pytest.fixture
def ref(cfg):
    tables, fasta, _ = demo_tables()
    records = [ReferenceSequence.model_validate(r) for r in tables["sequences"]]
    index = ReferenceIndex(
        {
            "reference_version": "FX1-SIMULASI",
            "module": "SIMULASI-ID",
            "marker": "12S_MiFish_U",
            "contains_simulated": True,
        },
        {r["species_valid"]: Taxon.model_validate(r) for r in tables["taxa"]},
        records,
        fasta,
        tables,
    )
    return index.select(cfg, "simulation", "12S_MiFish_U")


@pytest.fixture
def hit(ref):
    seqs = {r.species_valid: r.seq_id for r in ref.eligible}

    def make(species, pct, seq_id=None, bitscore=100, coverage=1):
        return SpeciesHit(
            species=species,
            pct=pct,
            seq_id=seq_id or seqs.get(species, ""),
            bitscore=bitscore,
            query_coverage=coverage,
        )

    return make


@pytest.fixture
def demo_dir():
    return DEMO
