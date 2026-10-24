"""F5/F6/F37 and T-SIM-SCN [MVP]: wholly fictional, seeded SIMULASI data."""

import random
from pathlib import Path

from biotrace_core.config import ROOT
from biotrace_core.io.loaders import write_fasta, write_table
from biotrace_core.reference.curate import write_reference

DEMO = ROOT / "data/demo/matano_SIMULASI_v3"
SOURCE = "SRC_SIMULASI"


def mutate(seq: str, positions: list[int], offset: int = 1) -> str:
    result = list(seq)
    for i in positions:
        options = [c for c in "ACGT" if c != seq[i]]
        result[i] = options[(offset - 1) % len(options)]
    return "".join(result)


def demo_tables() -> tuple[dict[str, list[dict]], dict[str, str], dict[str, str]]:
    rng = random.Random(20261025)  # Generator only; the core has no randomness.
    bases = {
        g: "".join(rng.choices("ACGT", k=170))
        for g in ("Piscis", "Gobio", "Rasbo", "Tilapa", "Hybridus")
    }
    seqs = {
        "Piscis alpha": bases["Piscis"],
        "Piscis beta": mutate(bases["Piscis"], [10]),
        "Gobio delta": bases["Gobio"],
        "Gobio epsilon": mutate(bases["Gobio"], [20, 80]),
        "Gobio lambda": mutate(bases["Gobio"], [5, 35, 65, 95, 125, 155]),
        "Rasbo zeta": bases["Rasbo"],
        "Rasbo iota": mutate(bases["Rasbo"], [5, 35, 65, 95, 125, 155]),
        "Tilapa omega": bases["Tilapa"],
        "Hybridus alpha": bases["Hybridus"],
        "Hybridus beta": mutate(bases["Hybridus"], [10]),
    }
    names = list(seqs) + ["Piscis gamma", "Rasbo eta", "Rasbo theta", "Piscis externus"]
    taxa = [
        {
            "species_valid": n,
            "genus": n.split()[0],
            "family": f"{n.split()[0]}idae_SIMULASI",
            "order": "Ordo_SIMULASI",
            "in_indonesia": n != "Piscis externus",
            "source_id": SOURCE,
            "is_simulated": True,
        }
        for n in sorted(names)
    ]
    sequences = []
    fasta = {}
    for i, (name, seq) in enumerate(sorted(seqs.items()), 1):
        key = f"SIM_REF_{i:03}"
        fasta[key] = seq
        sequences.append(
            {
                "seq_id": key,
                "accession": "",
                "source_db": "simulated",
                "source_id": SOURCE,
                "species_original": name,
                "species_valid": name,
                "marker": "12S_MiFish_U",
                "region_trimmed": True,
                "length": len(seq),
                "n_ambiguous": 0,
                "voucher_level": "V2",
                "voucher_catalog": f"SIMULASI-{i}",
                "voucher_institution": "SIMULASI",
                "specimen_country": "ID",
                "specimen_locality": "SIMULASI",
                "curation_status": "accepted",
                "flags": "SIMULASI",
                "license": "SIMULASI internal tim",
                "date_added": "2026-10-24",
                "curator": "agent:Codex",
                "is_simulated": True,
            }
        )
    endemic = {"Piscis alpha", "Piscis beta", "Piscis gamma", "Gobio delta"}
    checklist = [
        {
            "waterbody_id": "MATANO",
            "species_valid": n,
            "origin_status": "endemik"
            if n in endemic
            else "introduksi"
            if n == "Tilapa omega"
            else "asli",
            "endemic_scope": "danau" if n in endemic else "",
            "source_id": SOURCE,
            "year_recorded": "",
            "notes": "SIMULASI: bukan catatan keberadaan nyata",
            "is_simulated": True,
        }
        for n in sorted(
            set(names) - {"Gobio lambda", "Piscis externus", "Hybridus alpha", "Hybridus beta"}
        )
    ]
    checklist.append(
        {
            "waterbody_id": "MATANO",
            "species_valid": "alias:louhan_hybrid_SIMULASI",
            "origin_status": "introduksi",
            "endemic_scope": "",
            "source_id": SOURCE,
            "year_recorded": "",
            "notes": "SIMULASI",
            "is_simulated": True,
        }
    )
    tables = {
        "sequences": sequences,
        "taxa": taxa,
        "waterbodies": [
            {
                "waterbody_id": "MATANO",
                "name": "Danau Matano (SIMULASI)",
                "type": "danau",
                "complex_id": "MALILI",
                "country": "ID",
                "is_simulated": True,
            }
        ],
        "checklist": checklist,
        "status": [
            {
                "species_valid": n,
                "iucn_category": "NE",
                "invasive_flag": n == "Tilapa omega",
                "invasive_source_id": SOURCE,
                "version_date": "2026-10-24",
                "is_simulated": True,
            }
            for n in sorted(names)
        ],
        "aliases": [
            {
                "alias_key": "louhan_hybrid_SIMULASI",
                "alias_label_id": "kemungkinan louhan hibrida (SIMULASI)",
                "alias_label_en": "likely hybrid (SIMULATION)",
                "member_name": n,
                "category": "hybrid_invasive",
                "source_id": SOURCE,
                "reviewed_by_expert": False,
                "is_simulated": True,
            }
            for n in ["Hybridus alpha", "Hybridus beta"]
        ],
        "complexes": [
            {
                "complex_id": "KX_PISCIS_SIMULASI",
                "label_id": "kompleks Piscis Matano (SIMULASI)",
                "label_en": "Piscis SIMULATION complex",
                "member_species": n,
                "waterbody_scope": "MATANO",
                "reason": "resolusi_marker_SIMULASI",
                "source_id": SOURCE,
                "reviewed_by_expert": False,
                "is_simulated": True,
            }
            for n in ["Piscis alpha", "Piscis beta", "Piscis gamma"]
        ],
        "introductions": [
            {
                "species_valid": "Tilapa omega",
                "waterbody_id": "MATANO",
                "pathway": "budidaya",
                "first_record_year": "",
                "source_id": SOURCE,
                "is_simulated": True,
            }
        ],
        "sources": [
            {
                "source_id": SOURCE,
                "citation": "Data fiktif SIMULASI internal tim untuk pengujian perangkat lunak; bukan data ilmiah.",
                "doi_or_url": "",
                "type": "simulated",
                "license": "SIMULASI internal tim",
                "accessed_date": "2026-10-24",
                "is_simulated": True,
            }
        ],
    }
    return tables, fasta, seqs


def create_demo(destination: Path = DEMO) -> Path:
    if destination.exists():
        raise ValueError("Versi demo sudah ada; gunakan folder versi baru.")
    destination.mkdir(parents=True)
    tables, fasta, species = demo_tables()
    write_reference(
        destination / "reference_SIMULASI",
        "SIMULASI-v3",
        "SIMULASI-ID",
        "12S_MiFish_U",
        tables,
        fasta,
        True,
        "Kamus fiktif SIMULASI; bukan referensi Malili nyata. Semua voucher/status/sekuens adalah data uji.",
    )
    queries = [
        species["Gobio delta"],
        species["Gobio epsilon"],
        species["Tilapa omega"],
        mutate(species["Piscis alpha"], [10], 2),
        species["Rasbo zeta"],
        mutate(species["Piscis alpha"], [100]),
        species["Gobio delta"],
        mutate(species["Hybridus alpha"], [10], 2),
        species["Tilapa omega"],
        species["Gobio epsilon"],
        species["Gobio epsilon"],
        mutate(species["Rasbo iota"], list(range(12, 162, 10))),
        mutate(species["Rasbo iota"], list(range(13, 153, 10))),
        mutate(species["Gobio epsilon"], [13, 43, 73, 103, 133]),
        species["Gobio lambda"],
        mutate(species["Gobio delta"], [20]),
    ]
    metadata = []
    for site in range(1, 6):
        for rep in range(1, 4):
            metadata.append(
                {
                    "sample_id": f"MAT_S{site}_R{rep}",
                    "site_id": f"MAT-S{site}",
                    "waterbody_id": "MATANO",
                    "latitude": -2.47 + site * 0.001,
                    "longitude": 121.33 + site * 0.001,
                    "collection_date": "2026-10-24",
                    "sample_type": "sampel",
                    "replicate": rep,
                    "extraction_batch": "B1" if site <= 3 else "B2",
                    "marker": "12S_MiFish_U",
                    "is_simulated": True,
                }
            )
    for key, batch, kind in [
        ("NEG_B1", "B1", "kontrol_negatif_ekstraksi"),
        ("NEG_B2", "B2", "kontrol_negatif_ekstraksi"),
        ("PCR_B2", "B2", "kontrol_negatif_pcr"),
    ]:
        metadata.append(
            {
                "sample_id": key,
                "site_id": "CONTROL",
                "waterbody_id": "CONTROL",
                "latitude": 0,
                "longitude": 0,
                "collection_date": "2026-10-24",
                "sample_type": kind,
                "replicate": "",
                "extraction_batch": batch,
                "marker": "12S_MiFish_U",
                "is_simulated": True,
            }
        )
    rows, taxonomy = [], []
    for index in range(1, 17):
        asv = f"SIM_ASV_{index:03}"
        sites = (
            [1, 2] if index == 9 else [4, 5] if index == 10 else [1 + (index % 3), 4 + (index % 2)]
        )
        n_pos = 2 if index == 6 else 1 if index in {8, 11} else 3
        total = 7 if index in {7, 11} else 900
        for site in sites:
            for rep in range(1, n_pos + 1):
                rows.append(
                    {
                        "asv_id": asv,
                        "sample_id": f"MAT_S{site}_R{rep}",
                        "reads": total // n_pos + (1 if rep <= total % n_pos else 0),
                        "is_simulated": True,
                    }
                )
        if index in {9, 10}:
            rows.append(
                {
                    "asv_id": asv,
                    "sample_id": "NEG_B1" if index == 9 else "NEG_B2",
                    "reads": 20,
                    "is_simulated": True,
                }
            )
        nearest = [
            "Gobio delta",
            "Gobio epsilon",
            "Tilapa omega",
            "Piscis alpha",
            "Rasbo zeta",
            "Piscis alpha",
            "Gobio delta",
            "Hybridus alpha",
            "Tilapa omega",
            "Gobio epsilon",
            "Gobio epsilon",
            "Rasbo iota",
            "Rasbo iota",
            "Gobio epsilon",
            "Gobio lambda",
            "Gobio delta",
        ][index - 1]
        identity = (
            sum(a == b for a, b in zip(queries[index - 1], species[nearest], strict=False))
            / 170
            * 100
        )
        taxonomy.append(
            {
                "asv_id": asv,
                "taxon": nearest,
                "rank": "species",
                "pct_identity": identity,
                "runner_up_taxon": "Hybridus beta"
                if index == 8
                else "Piscis beta"
                if index == 4
                else "",
                "runner_up_pct_identity": identity if index in {4, 8} else "",
                "reference_db": "SIMULASI",
                "is_simulated": True,
            }
        )
    write_table(destination / "reads_SIMULASI.csv", rows)
    write_table(destination / "metadata_SIMULASI.csv", metadata)
    write_table(destination / "taxonomy_SIMULASI.csv", taxonomy)
    write_fasta(
        destination / "asv_SIMULASI.fasta",
        {f"SIM_ASV_{i:03}": seq for i, seq in enumerate(queries, 1)},
    )
    expected = [
        "safe",
        "safe",
        "safe",
        "safe",
        "safe",
        "must_verify",
        "must_verify",
        "must_verify",
        "must_verify",
        "do_not_use",
        "do_not_use",
        "with_note",
        "with_note",
        "with_note",
        "with_note",
        "safe",
    ]
    write_table(
        destination / "scenarios_SIMULASI.csv",
        [
            {"asv_id": f"SIM_ASV_{i:03}", "expected_decision": decision, "is_simulated": True}
            for i, decision in enumerate(expected, 1)
        ],
    )
    (destination / "README_SIMULASI.md").write_text(
        "# SIMULASI\n\nSeluruh nama, sekuens, bacaan, voucher, status dan koordinat dibuat untuk tes perangkat lunak. Bukan bukti ilmiah atau catatan ikan Matano. Seed 20261025. FASTA mewarisi is_simulated=true dari run/metadata.\n\n16 skenario, 5 lokasi, 15 sampel lapangan dan 3 kontrol. Alias memakai Hybridus fiktif agar tidak mengarang nama spesies nyata. Varian taksonomi lab memiliki aturan gap konservatif sehingga dapat berbeda nilai dari hasil FASTA.\n",
        encoding="utf-8",
    )
    return destination


if __name__ == "__main__":
    print(create_demo())
