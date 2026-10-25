# Data eDNA ASLI: Marwayana dkk. 2022 (MiFish-U, kepulauan Indonesia)

**Bukan SIMULASI.** Sumber: Dryad doi:10.5068/D12T1B (CC0), berkas `miu_bio_12S_taxonomy_tables/miu_12S_ASV_taxonomy_detailed.txt` di
`raw/edna_indonesia_dryad_D12T1B/anacapa_output.zip`. Paper: Marwayana O, Gold Z, Meyer C,
Barber P (2022) *Environmental DNA*, doi:10.1002/edn3.257.

Dibangun oleh `scripts/import_marwayana2022.py`:
- 1935 ASV ikan (class:Actinopteri menurut lab, ber-sekuens gabungan, total bacaan lapangan >= 10 = ambang mesin `min_total_reads`);
- 39 kode lokasi, 116 sampel lapangan, 4 blank;
- `taxonomy.csv` = penamaan lab asli (Anacapa), untuk dibandingkan dengan BioTrace.

Keterbatasan (tidak ditebak, A1): koordinat dan tanggal kosong (ada di Tabel S1 paper,
belum ditranskripsi); batch ekstraksi tidak tercantum sehingga semua sampel dan blank satu
batch (paling konservatif); jenis blank tidak dinyatakan; sampel `.star` tidak dipakai;
perairan diberi LAUT_INDONESIA (checklist FishBase tingkat negara).
