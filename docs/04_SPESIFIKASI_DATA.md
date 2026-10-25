# 04 — Spesifikasi Data

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Tunduk pada | `01_KONSEP_INDUK.md`, `03_ATURAN_MESIN.md` |
| Cakupan | Skema input, kamus referensi, tabel acuan, output, parameter aturan, protokol kurasi, registri sumber, aturan data demo |

Konvensi umum:
- Semua CSV: UTF-8, pemisah koma, baris pertama header, akhir baris LF. TSV diterima untuk input.
- Tanggal: `YYYY-MM-DD`. Koordinat: desimal WGS84.
- Nama ilmiah selalu dalam bentuk `Genus species` tanpa author. Author disimpan di kolom terpisah.
- Kolom `is_simulated` (boolean) wajib ada di setiap tabel data demo.

---

## 1. Input pengguna `[MVP]`

*D-038 (Diusulkan):* nama kolom di bawah adalah kontrak internal. Ekspor lab dengan nama lain (mis. `otu_id`, `site_name`, `waterbody`, `pident`) dikenali lewat sinonim atau isinya (`biotrace_core/io/columns.py`), kolom tambahan diabaikan, dan semua pemetaan dilaporkan sebagai peringatan `V-COL`. Perairan dan marker yang kosong dipilih pengguna di formulir unggah; koordinat dan tanggal yang kosong tidak ditebak.

### 1.1 `reads.csv` (wajib)

Format panjang:

| Kolom | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `asv_id` | string | ya | Cocok dengan header FASTA |
| `sample_id` | string | ya | Cocok dengan `metadata.csv` |
| `reads` | integer ≥ 0 | ya | Jumlah bacaan |

Format lebar juga diterima: kolom pertama `asv_id`, kolom lain = `sample_id`, isi = bacaan. Format dideteksi otomatis (R-PRE-01).

```csv
asv_id,sample_id,reads
ASV_0001,MAT_S1_R1,523
ASV_0001,MAT_S1_R2,611
```

### 1.2 `metadata.csv` (wajib)

| Kolom | Tipe | Wajib | Nilai yang diterima / keterangan |
|---|---|---|---|
| `sample_id` | string | ya | Unik |
| `site_id` | string | ya | Lokasi pengambilan |
| `waterbody_id` | string | ya | Harus ada di `waterbodies.csv` kamus aktif (mis. `MATANO`) |
| `latitude`, `longitude` | float | ya | WGS84 |
| `collection_date` | date | ya | |
| `sample_type` | enum | ya | `sampel`, `kontrol_negatif_lapangan`, `kontrol_negatif_ekstraksi`, `kontrol_negatif_pcr`, `kontrol_positif` |
| `replicate` | integer | ya untuk `sampel` | Nomor replikat di lokasi |
| `extraction_batch` | string | ya | Dipakai untuk mencocokkan kontrol negatif |
| `marker` | enum | ya | `12S_MiFish_U`, `16S`, `COI` |
| `pcr_batch` | string | tidak | Disimpan, belum dipakai di r0.1 |
| `notes` | string | tidak | |

Untuk kontrol, `site_id` dan `waterbody_id` boleh diisi `CONTROL`.

Nama kolom dipetakan ke istilah FAIRe di roadmap `[P1]`.

### 1.3 `asv.fasta` (dianjurkan)

```
>ASV_0001
CACCGCGGTTATACGAGAGGCCCAAGTTGATAGACAACGGCGTAAAGAGTGGTT...
```

Header hanya `asv_id` (teks setelah spasi diabaikan). Basa yang diizinkan: A, C, G, T, N (huruf besar/kecil).

### 1.4 `taxonomy.csv` (wajib bila tanpa FASTA)

| Kolom | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `asv_id` | string | ya | |
| `taxon` | string | ya | Nama dari lab |
| `rank` | enum | ya | `species`, `genus`, `family`, `order` |
| `pct_identity` | float | ya | 0–100 |
| `runner_up_taxon` | string | tidak | Spesies terbaik kedua |
| `runner_up_pct_identity` | float | tidak | |
| `reference_db` | string | tidak | Mis. "MitoFish 2024-xx", "NCBI nt" |

### 1.5 `site_context.csv` (opsional)

| Kolom | Keterangan |
|---|---|
| `site_id` | |
| `context_type` | `keramba`, `pasar_ikan`, `inlet_sungai`, `permukiman`, `lainnya` |
| `description` | Teks bebas |

Dipakai untuk R-ORIG-01 (kemungkinan sumber DNA lain).

### 1.6 Aturan validasi input

| Kode | Kondisi | Tingkat |
|---|---|---|
| V-01 | Kolom wajib tidak ada | Galat (proses berhenti) |
| V-02 | `sample_id` di reads tidak ada di metadata | Peringatan; baris diabaikan |
| V-03 | `waterbody_id` tidak dikenal kamus | Galat |
| V-04 | Satu `site_id` dengan >1 `waterbody_id` | Galat |
| V-05 | Batch tanpa kontrol negatif | Peringatan |
| V-06 | Koordinat di luar rentang | Peringatan |
| V-07 | FASTA tanpa ASV yang ada di reads, atau sebaliknya | Peringatan |
| V-08 | Tanpa FASTA dan tanpa taxonomy | Galat |
| V-09 | Marker di metadata tidak sama untuk semua sampel | Galat (r0.1 hanya satu marker per run) |
| V-10 | Ukuran file > 200 MB atau ekstensi tidak diizinkan | Galat |

---

## 2. Kamus referensi (aset inti)

### 2.1 Struktur folder

```
data/
  reference/
    v0.1/                      # modul Indonesia, versi kamus
      manifest.json
      sequences.fasta
      sequences.csv
      taxa.csv
      waterbodies.csv
      checklist.csv
      status.csv
      aliases.csv
      complexes.csv
      introductions.csv
      sources.csv
      coverage.csv             # turunan (R-COV-01)
      curation_report.csv      # turunan (protokol §5)
      CHANGELOG.md
  external/                    # HANYA mode validasi (aturan A4)
    lake_st_pierre/
    french_guiana_12s/
  demo/                        # data SIMULASI untuk pitch
    matano_sim_v1/
```

Versi kamus tidak pernah ditimpa. Perubahan = folder versi baru (aturan A12).

### 2.2 `sequences.csv`

| Kolom | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `seq_id` | string | ya | ID internal unik, mis. `BT000123` |
| `accession` | string | ya bila publik | Nomor GenBank/BOLD/ENA |
| `source_db` | enum | ya | `genbank`, `bold`, `mitofish`, `paper_supplement`, `partner_lab`, `simulated` |
| `source_id` | string | ya | Merujuk `sources.csv` |
| `species_original` | string | ya | Nama seperti di sumber |
| `species_valid` | string | ya | Nama valid setelah normalisasi (Catalog of Fishes) |
| `marker` | enum | ya | `12S_MiFish_U`, `12S_other`, `16S`, `COI`, `mitogenome` |
| `region_trimmed` | boolean | ya | true bila sudah dipotong ke daerah amplikon MiFish-U |
| `length` | integer | ya | Panjang setelah dipotong |
| `n_ambiguous` | integer | ya | Jumlah basa non-ACGT |
| `voucher_level` | enum | ya | `V1`, `V2`, `V3`, `V4` (lihat §2.3) |
| `voucher_catalog` | string | tidak | Nomor katalog museum |
| `voucher_institution` | string | tidak | Mis. MZB, ZSM, MNHN |
| `specimen_country` | string | tidak | ISO 3166 alpha-2, mis. `ID` |
| `specimen_locality` | string | tidak | |
| `curation_status` | enum | ya | `accepted`, `flagged`, `rejected` |
| `flags` | string | tidak | Dipisah `;`: `similar_to=<sp>`, `conflict`, `short`, `ambiguous`, `outlier` |
| `license` | string | ya | Mis. `GenBank-public`, `CC-BY-4.0` |
| `date_added` | date | ya | |
| `curator` | string | ya | Nama orang atau `agent:<nama>` |
| `is_simulated` | boolean | ya | |

### 2.3 Level voucher

| Level | Definisi | Boleh mendukung klaim? |
|---|---|---|
| **V1** | Spesimen di museum dengan nomor katalog dan identifikasi oleh ahli taksonomi terdokumentasi | Ya |
| **V2** | Ada voucher/nomor spesimen, tetapi dokumentasi identifikasi tidak lengkap | Ya |
| **V3** | Tanpa voucher, tetapi dari spesimen teridentifikasi di paper peer-reviewed | Ya, dengan catatan di kartu |
| **V4** | Sekuens eDNA/lingkungan, atau sumber tanpa spesimen | **Tidak pernah** (aturan A5) |

### 2.4 `taxa.csv`

| Kolom | Keterangan |
|---|---|
| `species_valid` | Kunci |
| `genus`, `family`, `order` | Hierarki |
| `authority` | Author dan tahun |
| `synonyms` | Dipisah `;` |
| `in_indonesia` | boolean: tercatat di perairan Indonesia (asli atau introduksi) |
| `cof_checked_date` | Tanggal cek di Catalog of Fishes |
| `source_id` | |

### 2.5 `waterbodies.csv`

| Kolom | Contoh |
|---|---|
| `waterbody_id` | `MATANO` |
| `name` | Danau Matano |
| `type` | `danau` / `sungai` / `waduk` |
| `complex_id` | `MALILI` |
| `province` | Sulawesi Selatan |
| `country` | `ID` |
| `latitude`, `longitude` | Titik tengah |

Nilai awal v0.1: `MATANO`, `MAHALONA`, `TOWUTI`, `LONTOA`, `MASAPI` (kompleks `MALILI`).

### 2.6 `checklist.csv`

| Kolom | Keterangan |
|---|---|
| `waterbody_id` | |
| `species_valid` | Atau kunci alias, mis. `alias:louhan_hybrid` |
| `origin_status` | `asli`, `endemik`, `introduksi` |
| `endemic_scope` | `danau`, `kompleks_malili`, `sulawesi`, `indonesia`, kosong |
| `source_id` | |
| `year_recorded` | Tahun catatan |
| `notes` | |
| `source_quality` | r0.4 (D-033): `primer` (file sumber ada di `raw/`, bawaan bila kosong), `sekunder` (dikutip, file belum ada), `berita` (media massa). Selain `primer` → R-DEC-09 |

Checklist mencatat "tercatat", bukan "tidak mungkin". Spesies yang tidak ada di checklist berarti **tidak tercatat**.

### 2.7 `status.csv`

| Kolom | Keterangan |
|---|---|
| `species_valid` | |
| `iucn_category` | `CR`, `EN`, `VU`, `NT`, `LC`, `DD`, `NE` |
| `iucn_assessed_year` | |
| `invasive_flag` | boolean |
| `invasive_source_id` | Mis. sumber Permen KP 19/2020 (teks perlu diverifikasi) |
| `version_date` | |

### 2.8 `aliases.csv`

| Kolom | Contoh |
|---|---|
| `alias_key` | `louhan_hybrid` |
| `alias_label_id` | kemungkinan louhan hibrida |
| `alias_label_en` | likely flowerhorn hybrid |
| `member_name` | `Amphilophus citrinellus` (satu baris per nama) |
| `category` | `hybrid_invasive` |
| `source_id` | |
| `reviewed_by_expert` | boolean |

Isi awal dari PRD v2: nama spesies induk dari genus *Cichlasoma*, *Amphilophus*, dan *Paraneetroplus*. **Daftar nama spesies tepatnya wajib ditinjau ahli** (`reviewed_by_expert = false` sampai itu terjadi).

### 2.9 `complexes.csv`

| Kolom | Contoh |
|---|---|
| `complex_id` | `KX_TELMATHERINA_MATANO` |
| `label_id` | kompleks *Telmatherina* Matano |
| `label_en` | *Telmatherina* Matano complex |
| `member_species` | Satu baris per anggota |
| `waterbody_scope` | `MATANO` (dipisah `;` bila lebih dari satu) |
| `reason` | `introgresi`, `radiasi_muda`, `resolusi_marker` |
| `source_id` | Mis. Stelbrink dkk. 2014; revisi *Oryzias* 2026 |
| `reviewed_by_expert` | boolean |

Isi v0.1 adalah **draf** berdasarkan literatur (introgresi *Telmatherina* "sharpfin" Matano, Stelbrink 2014; introgresi *Oryzias* Malili, revisi 2026). Keanggotaan final butuh ahli dan uji in silico resolusi MiFish (`06_VALIDASI_DAN_UJI.md` T-DATA-02).

### 2.10 `introductions.csv`

| Kolom | Keterangan |
|---|---|
| `species_valid` / alias | |
| `waterbody_id` | |
| `pathway` | `budidaya`, `ikan_hias`, `tebar_benih`, `lepas_tidak_sengaja`, `tidak_diketahui` |
| `first_record_year` | |
| `source_id` | |

### 2.11 `sources.csv`

| Kolom | Keterangan |
|---|---|
| `source_id` | Mis. `SRC_STELBRINK2014` |
| `citation` | Sitasi lengkap |
| `doi_or_url` | |
| `type` | `peer_reviewed`, `preprint`, `book`, `database`, `regulation`, `news`, `simulated` |
| `license` | |
| `accessed_date` | |

### 2.12 `manifest.json`

```json
{
  "reference_version": "v0.1",
  "module": "ID",
  "created": "2026-10-24",
  "marker": "12S_MiFish_U",
  "files": {"sequences.fasta": "<sha256>", "sequences.csv": "<sha256>", "...": "<sha256>"},
  "counts": {"sequences_accepted": 0, "species_with_reference": 0, "waterbodies": 5},
  "contains_simulated": false,
  "changelog": "CHANGELOG.md"
}
```

---

## 3. Modul referensi luar (mode validasi) `[MVP]`

- Disimpan di `data/external/<nama>/` dengan struktur file yang sama, ditambah `README.md` berisi sumber, lisensi, dan cara unduh.
- Field `module` di manifest diisi kode wilayah (mis. `CA-QC`, `GF`).
- Mesin hanya memuat modul luar bila dipanggil dengan `--mode validation --module <nama>`.
- Tes wajib: run mode normal tidak pernah membaca `data/external/` (aturan A4).

Dataset yang direncanakan:

| Modul | Sumber | Isi | Catatan |
|---|---|---|---|
| `lake_st_pierre` | Astorg dkk. 2025, Dryad https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kzf | `raw_seq.zip` (2,94 GB FASTQ), `edna_lg_clean.csv`, `elec_long.csv`, `fish_codes.csv`, dll. | Ada pembanding electrofishing; tanpa field blank. Kamus 12S untuk spesies Québec harus disusun terpisah (lihat 06) |
| `french_guiana_12s` | Scientific Data 2026, Figshare https://doi.org/10.6084/m9.figshare.29168144; GenBank PX415477–PX417033 | 1.557 sekuens 12S, 369 spesies | Marker Teleo1/12S-V5, **bukan MiFish**. Cocok untuk uji leave-one-species-out |

---

## 4. Output `[MVP]`

Semua output sebuah run disimpan di `runs/<run_id>/` (`run_id` = 12 karakter pertama `run_fingerprint`).

### 4.1 `claims.csv`

| Kolom | Tipe | Keterangan |
|---|---|---|
| `run_id` | string | |
| `claim_id` | string | `{site_id}__{asv_id}` |
| `site_id`, `waterbody_id`, `asv_id` | string | |
| `taxon_lab` | string | Nama dari lab (bila ada) |
| `best_match` | string | Spesies dengan hit terbaik |
| `best_pct` | float | |
| `gap_pct` | float/null | `null` = ∞ |
| `candidates` | string | `species:pct` dipisah `;` |
| `reported_name` | string | Nama aman |
| `reported_rank` | enum | `species`, `complex`, `genus`, `family`, `order`, `unknown`, `hybrid_alias` |
| `complex_id` | string | Bila kompleks |
| `l1`, `l2`, `l4`, `total` | int | |
| `grade` | enum | `A`, `B`, `C`, `D` |
| `cap_reason` | string | `negative_control`, `low_reads`, kosong |
| `labels` | string | Label L3 dipisah `;` |
| `p_missing` | float/null | |
| `causes` | string | `reference;marker;sample;location` |
| `decision` | enum | `safe`, `with_note`, `must_verify`, `do_not_use` |
| `follow_up` | string | Teks Indonesia |
| `reasons_id`, `reasons_en` | string | Alasan per lapisan |
| `voucher_support` | enum/null | Level voucher terbaik di antara sekuens pendukung |
| `supporting_seq_ids` | string | Dipisah `;` |
| `n_rep`, `n_pos`, `total_reads` | int | |
| `in_negative_control` | bool | |
| `assessed_with_lab_database` | bool | |
| `origin_status`, `origin_pathway`, `origin_other_sources` | string | R-ORIG-01 |
| `is_simulated` | bool | |

### 4.2 File output lainnya

| File | Isi |
|---|---|
| `summary.json` | Jumlah klaim dan taksa unik per keputusan, tindak lanjut baku, peringatan validasi, flag SIMULASI |
| `coverage.csv` | `waterbody_id`, `genus`, `n`, `r`, `p_missing` untuk perairan dalam run |
| `barcode_priority.csv` | `type` (`species`/`asv`), `name_or_asv`, `waterbody_id`, `score`, `reasons`, `sites`, `total_reads`, `nearest_hint` |
| `validation_report.json` | Hasil V-01 s.d. V-10 |
| `run_manifest.json` | Hash input, versi kamus + hash manifest, versi aturan + hash YAML, versi engine, versi BLAST+, parameter efektif, `run_fingerprint`, `report_fingerprint`, waktu mulai/selesai (tidak ikut fingerprint) |
| `blast_hits.tsv` | Hit mentah setelah filter cakupan (untuk audit) |
| `report.pdf` | Laporan Bahasa Indonesia |

---

## 5. Protokol kurasi kamus `[MVP]` (alat `biotrace ref import` dan `biotrace ref build`)

| ID | Langkah | Aturan | Hasil |
|---|---|---|---|
| R-CUR-01 | Validasi skema | Semua kolom wajib §2.2 ada | Tolak baris yang tidak valid |
| R-CUR-02 | Tolak eDNA | `voucher_level = V4` atau `source_db` lingkungan | `rejected` |
| R-CUR-03 | Normalisasi nama | Cocokkan `species_original` ke `taxa.csv` (nama valid + sinonim). Simpan nama asli dan nama valid. Sinonim dipetakan, tidak dihapus | Nama tidak dikenal → `flagged` |
| R-CUR-04 | Okurensi | Spesies harus `in_indonesia = true` untuk modul `ID` | Bila tidak → pindah ke modul luar atau `rejected` |
| R-CUR-05 | Potong daerah MiFish-U | Potong in silico memakai primer MiFish-U (F: `GTCGGTAAAACTCGTGCCAGC`, R: `CATAGTGGGGTATCTAATCCCAGTTTG`; **verifikasi urutan primer terhadap Miya dkk. 2015 sebelum dipakai**). Izinkan ≤3 mismatch per primer | Tidak ada daerah MiFish → `flagged:no_mifish_region` (tidak dipakai untuk marker MiFish) |
| R-CUR-06 | Panjang & ambiguitas | Tolak bila panjang hasil potong < 90% panjang amplikon median atau basa N > 1% | `rejected:short` / `rejected:ambiguous` |
| R-CUR-07 | Duplikat | Sekuens identik dengan spesies sama digabung; semua aksesi disimpan | Satu `seq_id`, banyak aksesi |
| R-CUR-08 | Konflik | Sekuens identik dengan spesies berbeda → keduanya `flagged:conflict`, tetap dipakai, dan mesin akan menurunkannya ke LCA secara alami | Dicatat di laporan kurasi |
| R-CUR-09 | Outlier filogenetik | `[P1]` PhyloRef atau uji monofili per genus; tandai `similar_to=` | `flagged:outlier` |
| R-CUR-10 | Lisensi | `license` wajib terisi; sumber tanpa izin pakai → `rejected` | |
| R-CUR-11 | Versi | Hasil = folder versi baru + `manifest.json` + `CHANGELOG.md` + `curation_report.csv` | |
| R-CUR-12 | Hitung ulang | Jalankan R-COV-01 untuk semua perairan | `coverage.csv` |

`curation_report.csv`: `seq_id`, `accession`, `step`, `result` (`accepted`/`flagged`/`rejected`), `reason`.

---

## 6. Rencana isi kamus Malili v0.1 `[MVP]`

| Komponen | Sumber | Status | Tindakan |
|---|---|---|---|
| Sekuens Telmatherinidae 12S–16S | Stelbrink dkk. 2014, GenBank KJ667771–KJ667865 | Aksesi terverifikasi di PMC | **Manusia** mengunduh FASTA lewat NCBI Batch Entrez; cek apakah fragmennya mencakup daerah MiFish (R-CUR-05) |
| Sekuens ND2 Telmatherinidae | KJ667866–KJ667963 | Terverifikasi | Bukan 12S; simpan untuk referensi `[P1]` |
| Sekuens dari Herder dkk. 2006 | ESM paper | Aksesi belum dibuka | Daftar manual |
| *Oryzias* Malili | Revisi 2026 (BMC Ecol Evol) | Data SNP; aksesi 12S belum dicek | Daftar manual |
| Sekuens 12S publik lain untuk spesies Malili | GenBank/MitoFish/BOLD | Belum dicari | Pencarian manual per spesies checklist |
| Checklist Telmatherinidae Malili | Herder dkk. 2006, Verh. Ges. Ichthyol. 5:139–163 | Sumber teridentifikasi | Ekstrak ke `checklist.csv` |
| Ikan introduksi Malili | Herder dkk. 2012, Aquatic Invasions 7(4):521–535; Tantu & Nilawati 2007 | **Diekstrak ke v0.2** (D-032) | `data/reference/v0.2/checklist.csv` + `introductions.csv`; transkripsi di `data/curation/` |
| Nama valid | Catalog of Fishes | Online | Cek per spesies |
| Status IUCN | IUCN Red List | Online | Cek per spesies |
| Daftar invasif nasional | Permen KP No. 19/2020 | Teks belum diverifikasi | Daftar manual (JDIH KKP) |

**Jalur cadangan untuk demo:** bila sekuens publik belum siap, buat `data/demo/matano_sim_v1/` berisi kamus sintetis dengan `is_simulated = true`, `source_db = simulated`, dan label SIMULASI di dashboard. Jangan mencampur sekuens sintetis ke `data/reference/`.

---

## 7. File aturan `rules_r0.1.yaml`

```yaml
rules_version: r0.1
status: "usulan tim, belum dikalibrasi ahli"
marker_default: 12S_MiFish_U
naming:
  min_query_coverage: 0.90
  hit_window_pct: 0.5
  unknown_below_pct: 95.0
  species_min_pct: 98.0
  congener_gap_policy: strict      # strict | threshold
scoring:
  l1_high_pct: 99.0
  l1_high_gap: 1.0
  l1_mid_pct: 98.0
  l1_mid_gap: 0.5
  l1_penalty_ref_fraction_below: 0.5
  l4_full: 1.0
  l4_partial: 0.66
  l4_single_replicate_score: 1
  min_total_reads: 10
  grade_map: {5: A, 4: B, 3: C, 2: C, 1: D, 0: D}
causes:
  reference_cause_p_missing: 0.5
preprocess:
  tag_jump_fraction: 0.001
reference:
  allowed_voucher_levels: [V1, V2, V3]
validation:
  baseline_species_pct: 97.0
```

---

## 8. Data demo SIMULASI `[MVP]`

Folder `data/demo/matano_sim_v1/` berisi:
- `reads.csv`, `metadata.csv`, `asv.fasta` (atau `taxonomy.csv`), `README.md`.
- Skenario: 16 nama dari lab untuk 5 lokasi di Danau Matano, 3 replikat per lokasi, 2 batch ekstraksi dengan kontrol negatif.
- Harus memuat minimal satu contoh untuk setiap keputusan (`safe`, `with_note`, `must_verify`, `do_not_use`), satu kompleks, satu alias louhan, satu "tidak dikenal", satu kontaminasi kontrol negatif, satu klaim endemik lemah.
- Semua baris `is_simulated = true`. Nama folder dan README menyebut SIMULASI.
- Nama spesies boleh nama asli Malili, tetapi angka bacaan dan kemiripan **dibuat tim** dan wajib disebut demikian.

---

## 9. Registri sumber data (ringkas)

Daftar lengkap dataset, tautan, dan status ada di `07_REGISTRI_BUKTI_RINGKAS.md` §3 dan dokumen lengkap di Project GENOHACK. Setiap dataset yang masuk repo wajib punya entri di `sources.csv` dan `README.md` di foldernya.
