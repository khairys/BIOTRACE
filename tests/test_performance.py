"""T-PERF [MVP]: 200 samples × 2,000 ASVs, real local BLAST, no fake timings."""

import json
import random
import time
from pathlib import Path

import pytest

from biotrace_core.io.loaders import write_fasta, write_table
from biotrace_core.naming.blast import executable
from biotrace_core.pipeline import run_analysis
from biotrace_core.reference.curate import write_reference
from scripts.make_demo_data import demo_tables


@pytest.mark.slow
@pytest.mark.blast
def test_T_PERF_200_samples_2000_ASVs(tmp_path):
    if not executable("blastn"):
        pytest.skip("BLAST+ diperlukan.")
    tables, _, _ = demo_tables()
    seed = tables["sequences"][0]
    rng = random.Random(20261024)
    sequences = {f"PERF_{i:04}": "".join(rng.choices("ACGT", k=170)) for i in range(2000)}
    tables.update(
        sequences=[], taxa=[], checklist=[], status=[], aliases=[], complexes=[], introductions=[]
    )
    for identifier in sequences:
        species = f"Perfsim{identifier.split('_')[1]} alpha"
        genus = species.split()[0]
        tables["sequences"].append(
            {
                **seed,
                "seq_id": identifier,
                "species_original": species,
                "species_valid": species,
                "length": 170,
            }
        )
        tables["taxa"].append(
            {
                "species_valid": species,
                "genus": genus,
                "family": "Perfsimidae",
                "order": "Perfsimiformes",
                "in_indonesia": True,
                "source_id": "SRC_SIMULASI",
                "is_simulated": True,
            }
        )
        tables["checklist"].append(
            {
                "waterbody_id": "MATANO",
                "species_valid": species,
                "origin_status": "asli",
                "endemic_scope": "",
                "source_id": "SRC_SIMULASI",
                "is_simulated": True,
            }
        )
    reference = tmp_path / "reference_SIMULASI"
    write_reference(
        reference,
        "PERF-SIMULASI",
        "SIMULASI-ID",
        "12S_MiFish_U",
        tables,
        sequences,
        True,
        "Data uji kinerja SIMULASI; bukan data biologi.",
    )
    samples = [
        {
            "sample_id": f"PERF_S{i:03}",
            "site_id": "PERF_SITE",
            "waterbody_id": "MATANO",
            "latitude": 0,
            "longitude": 0,
            "collection_date": "2026-10-24",
            "sample_type": "sampel",
            "replicate": i + 1,
            "extraction_batch": "PERF",
            "marker": "12S_MiFish_U",
            "is_simulated": True,
        }
        for i in range(200)
    ]
    write_table(tmp_path / "metadata_SIMULASI.csv", samples)
    write_table(
        tmp_path / "reads_SIMULASI.csv",
        [
            {"asv_id": identifier, "sample_id": s["sample_id"], "reads": 500, "is_simulated": True}
            for identifier in sequences
            for s in samples
        ],
    )
    write_fasta(tmp_path / "asv_SIMULASI.fasta", sequences)
    start = time.perf_counter()
    result = run_analysis(
        tmp_path / "reads_SIMULASI.csv",
        tmp_path / "metadata_SIMULASI.csv",
        tmp_path / "asv_SIMULASI.fasta",
        None,
        None,
        reference,
        out_root=tmp_path / "runs",
        mode="simulation",
        threads=4,
    )
    elapsed = time.perf_counter() - start
    assert len(result.claims) == 2000
    assert all(c.n_rep == 200 for c in result.claims)
    assert elapsed < 120, f"{elapsed:.2f} detik"
    output = Path("output/validation")
    output.mkdir(parents=True, exist_ok=True)
    (output / "performance_SIMULASI.json").write_text(
        json.dumps(
            {
                "samples": 200,
                "asvs": 2000,
                "reads_rows": 400000,
                "reference_sequences": 2000,
                "blast_threads": 4,
                "seconds": elapsed,
                "includes_pdf": True,
                "is_simulated": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
