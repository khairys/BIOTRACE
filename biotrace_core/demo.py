"""D-036/D-038: explicit local demo sources; no network or synthetic observations."""

from biotrace_core.config import DEFAULT_REFERENCE, ROOT, load_rules
from biotrace_core.models import DataProvenance

REAL_DEMO = ROOT / "data/edna_asli/marwayana2022_mifishu"
REAL_REF = DEFAULT_REFERENCE
REAL_PRECOMPUTED_NAME = f"edna_asli_marwayana2022_{load_rules().rules_version}_{REAL_REF.name}"
REAL_PROVENANCE = DataProvenance(
    dataset_id="marwayana2022_mifishu",
    label="Data eDNA asli terumbu karang Indonesia",
    citation="Marwayana dkk. 2022, Environmental DNA, doi:10.1002/edn3.257",
    doi="10.5068/D12T1B",
    license="CC0",
    limitations=[
        "Dataset terumbu karang menguji alur pada data Indonesia; bukan validasi lapangan Malili.",
        "Koordinat dan tanggal belum ditranskripsi dari Tabel S1; nilai kosong tidak ditebak.",
        "Batch ekstraksi dan jenis blank tidak dinyatakan sumber; semua blank diperlakukan "
        "sebagai kontrol satu batch. Ini asumsi analisis, bukan metadata terkonfirmasi.",
        "Checklist LAUT_INDONESIA berskala negara; tidak membuktikan keberadaan di tiap lokasi.",
        "Identitas lab dipakai untuk perbandingan, bukan kebenaran acuan untuk menghitung akurasi.",
    ],
)
