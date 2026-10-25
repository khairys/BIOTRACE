"""Adapter data eDNA ASLI Marwayana dkk. 2022 (Dryad 10.5068/D12T1B, CC0) ke format BioTrace (D-036).

Sumber: raw/edna_indonesia_dryad_D12T1B/anacapa_output.zip, tabel
miu_bio_12S_taxonomy_tables/miu_12S_ASV_taxonomy_detailed.txt (primer MiFish-U).
Paper: Marwayana O, Gold Z, Meyer C, Barber P (2022) Environmental DNA in a global
biodiversity hotspot: lessons from coral reef fish diversity across the Indonesian archipelago.
Environmental DNA, doi:10.1002/edn3.257.

Prinsip (A1): hanya isi file yang dipakai. Yang tidak ada di file tidak ditebak:
- koordinat dan tanggal dikosongkan (peringatan V-06);
- semua lokasi diberi perairan LAUT_INDONESIA (paper: seluruh lokasi di kepulauan Indonesia);
- batch ekstraksi tidak tercantum: semua sampel dan blank diberi satu batch, sehingga setiap
  ASV yang muncul di blank mana pun ditandai untuk semua lokasi (paling konservatif);
- sampel bertanda ".star" (makna tidak dijelaskan di file) tidak dipakai;
- hanya ASV dengan sekuens gabungan, klasifikasi lab class:Actinopteri, dan total bacaan
  sampel lapangan >= scoring.min_total_reads (rules YAML; di bawahnya klaim pasti bernilai D).
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "raw/edna_indonesia_dryad_D12T1B/anacapa_output.zip"
MEMBER = "miu_bio_12S_taxonomy_tables/miu_12S_ASV_taxonomy_detailed.txt"
OUT = ROOT / "data/edna_asli/marwayana2022_mifishu"
SAMPLE_RE = re.compile(r"^bio_12S_(?P<name>.+)\.S\d+\.L001$")
RANKS = ["species", "genus", "family", "order"]


def lab_taxon(taxonomy: str) -> tuple[str, str]:
    parts = dict(p.split(":", 1) for p in taxonomy.split(";") if ":" in p)
    for rank in RANKS:
        value = parts.get(rank, "")
        if value and value != "NA":
            return value, rank
    return "", ""


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"{OUT} sudah ada; buat versi baru (A12).")
    import sys

    sys.path.insert(0, str(ROOT))
    from biotrace_core.config import load_rules

    min_reads = load_rules().scoring.min_total_reads
    text = zipfile.ZipFile(SOURCE).read(MEMBER).decode("utf-8", errors="replace")
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    columns = rows[0].keys()
    samples = {}
    for col in columns:
        m = SAMPLE_RE.match(col)
        if not m:
            continue
        name = m.group("name")
        if ".star" in name:
            continue
        if name.startswith("BLANK."):
            samples[col] = {
                "sample_id": name,
                "site_id": "CONTROL",
                "replicate": "",
                "type": "kontrol_negatif_ekstraksi",
            }
        else:
            site, _, rep = name.rpartition(".")
            if not rep.isdigit():
                continue
            samples[col] = {"sample_id": name, "site_id": site, "replicate": rep, "type": "sampel"}
    reads, fasta, taxonomy = [], {}, []
    for row in rows:
        seq = (row.get("sequence") or "").strip().upper()
        if not seq or "class:Actinopteri" not in (row.get("taxonomy") or ""):
            continue
        asv = row["12S_seq_number"]  # ID asli Anacapa (forward_/merged_ dipertahankan, unik)
        counts = {s["sample_id"]: int(float(row[c] or 0)) for c, s in samples.items()}
        field = sum(counts[s["sample_id"]] for s in samples.values() if s["type"] == "sampel")
        if field < min_reads:  # ambang mesin R-SCORE-06 (rules YAML); di bawahnya pasti nilai D
            continue
        fasta[asv] = seq
        reads += [{"asv_id": asv, "sample_id": k, "reads": v} for k, v in counts.items() if v > 0]
        taxon, rank = lab_taxon(row.get("taxonomy") or "")
        if taxon:
            taxonomy.append(
                {
                    "asv_id": asv,
                    "taxon": taxon,
                    "rank": rank,
                    "pct_identity": round(float(row.get("max_percent_id") or 0) * 100, 2),
                    "runner_up_taxon": "",
                    "runner_up_pct_identity": "",
                    "reference_db": "Anacapa CRUX 12S + Mo'orea BIOCODE (Marwayana dkk. 2022)",
                }
            )
    OUT.mkdir(parents=True)
    with open(OUT / "reads.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["asv_id", "sample_id", "reads"], lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(reads, key=lambda r: (r["asv_id"], r["sample_id"])))
    with open(OUT / "metadata.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(
            [
                "sample_id",
                "site_id",
                "waterbody_id",
                "latitude",
                "longitude",
                "collection_date",
                "sample_type",
                "replicate",
                "extraction_batch",
                "marker",
                "pcr_batch",
                "notes",
            ]
        )
        for s in sorted(samples.values(), key=lambda s: s["sample_id"]):
            note = (
                "jenis blank tidak dinyatakan di file sumber"
                if s["type"] != "sampel"
                else "koordinat/tanggal ada di Tabel S1 paper; belum ditranskripsi"
            )
            w.writerow(
                [
                    s["sample_id"],
                    s["site_id"],
                    "LAUT_INDONESIA",
                    "",
                    "",
                    "",
                    s["type"],
                    s["replicate"],
                    "TIDAK_DINYATAKAN",
                    "12S_MiFish_U",
                    "",
                    note,
                ]
            )
    with open(OUT / "asv.fasta", "w", encoding="utf-8", newline="\n") as f:
        for asv in sorted(fasta):
            f.write(f">{asv}\n{fasta[asv]}\n")
    with open(OUT / "taxonomy.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, list(taxonomy[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(taxonomy, key=lambda r: r["asv_id"]))
    sites = sorted({s["site_id"] for s in samples.values() if s["type"] == "sampel"})
    (OUT / "README.md").write_text(
        f"""# Data eDNA ASLI: Marwayana dkk. 2022 (MiFish-U, kepulauan Indonesia)

**Bukan SIMULASI.** Sumber: Dryad doi:10.5068/D12T1B (CC0), berkas `{MEMBER}` di
`raw/edna_indonesia_dryad_D12T1B/anacapa_output.zip`. Paper: Marwayana O, Gold Z, Meyer C,
Barber P (2022) *Environmental DNA*, doi:10.1002/edn3.257.

Dibangun oleh `scripts/import_marwayana2022.py`:
- {len(fasta)} ASV ikan (class:Actinopteri menurut lab, ber-sekuens gabungan, total bacaan lapangan >= {min_reads} = ambang mesin `min_total_reads`);
- {len(sites)} kode lokasi, {sum(s["type"] == "sampel" for s in samples.values())} sampel lapangan, {sum(s["type"] != "sampel" for s in samples.values())} blank;
- `taxonomy.csv` = penamaan lab asli (Anacapa), untuk dibandingkan dengan BioTrace.

Keterbatasan (tidak ditebak, A1): koordinat dan tanggal kosong (ada di Tabel S1 paper,
belum ditranskripsi); batch ekstraksi tidak tercantum sehingga semua sampel dan blank satu
batch (paling konservatif); jenis blank tidak dinyatakan; sampel `.star` tidak dipakai;
perairan diberi LAUT_INDONESIA (checklist FishBase tingkat negara).
""",
        encoding="utf-8",
    )
    print(
        f"{len(fasta)} ASV, {len(reads)} baris bacaan, {len(samples)} sampel, {len(taxonomy)} taksonomi lab"
    )


if __name__ == "__main__":
    main()
