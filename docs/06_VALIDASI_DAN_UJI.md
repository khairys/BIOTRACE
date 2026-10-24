# 06 — Rencana Validasi dan Uji

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Tunduk pada | `03_ATURAN_MESIN.md`, `04_SPESIFIKASI_DATA.md`, `05_ARSITEKTUR.md` |
| Tujuan | Membuktikan (1) kode sesuai aturan, (2) aturan lebih baik dari praktik umum, (3) hasil jujur dan bisa diulang |

Validasi BioTrace punya tiga lapis:
1. **Uji perangkat lunak**: apakah kode menjalankan aturan dengan benar?
2. **Uji logika mesin**: apakah aturan menekan nama keliru dibanding BLAST-97%?
3. **Validasi lapangan dan ahli**: apakah hasil cocok dengan tangkapan nyata dan penilaian ahli? `[P1]`

---

## 1. Uji perangkat lunak `[MVP]`

| ID | Jenis | Isi | Lulus bila |
|---|---|---|---|
| T-UNIT-NAME | Unit | Setiap R-NAME-* dengan kasus batas (tepat di ambang, di atas, di bawah) | Semua lulus |
| T-UNIT-SCORE | Unit | R-SCORE-01..07, termasuk 1 replikat, `n_genus = 0`, batas D | Semua lulus |
| T-UNIT-CAUSE | Unit | R-CAUSE-01..05 | Semua lulus |
| T-UNIT-DEC | Unit | Urutan evaluasi R-DEC dan teks tambahan R-DEC-07 | Semua lulus |
| T-EX | Contoh kerja | E1–E12 dari 03 §11 memakai fixture FX-1 | Semua keluaran (nama, tingkat, L1/L2/L4, nilai, penyebab, label, keputusan) sama persis |
| T-INV-01 | Invarian | Setiap klaim B–D atau di atas tingkat spesies punya ≥1 penyebab | 0 pelanggaran pada semua data uji |
| T-INV-02 | Invarian | Tidak ada klaim `reported_rank = species` bila `best_pct < species_min_pct` | 0 pelanggaran |
| T-INV-03 | Invarian | Klaim endemik bernilai C–D selalu `must_verify` | 0 pelanggaran |
| T-INV-04 | Invarian | Setiap klaim memuat teks batas interpretasi di laporan | 0 pelanggaran |
| T-INV-05 | Invarian | Tidak ada sekuens V4 di `blast_input.fasta` | 0 pelanggaran |
| T-REPRO | Reproduksibilitas | Jalankan run yang sama dua kali (juga dengan `num_threads` berbeda) | `report_fingerprint` identik |
| T-ISO | Isolasi | Mode normal tidak membuka file di `data/external/` (patch `open` / cek path) | Lulus |
| T-VALID | Validasi input | V-01..V-10 dengan file rusak | Galat/peringatan sesuai 04 §1.6 |
| T-PERF | Kinerja (`slow`) | 200 sampel × 2.000 ASV sintetis, BLAST ke kamus 2.000 sekuens | < 120 detik di laptop 4 core |
| T-API | Integrasi | Unggah demo → claims → coverage → PDF | Semua endpoint 200; PDF terbuka |
| T-SIM | Kejujuran demo | Run demo menghasilkan `is_simulated = true` di semua baris, summary, dan PDF | Lulus |

## 2. Tugas data (dikerjakan manusia + agent)

Agent **tidak** mengunduh dari NCBI/BOLD/Dryad. Manusia mengunduh, agent mengkurasi.

| ID | Tugas | Pelaku | Hasil | Tag |
|---|---|---|---|---|
| T-DATA-01 | Unduh FASTA KJ667771–KJ667865 (Stelbrink 2014) lewat NCBI Batch Entrez | Manusia | `raw/stelbrink2014_12s16s.fasta` | `[MVP]` |
| T-DATA-02 | Cek apakah fragmen itu mencakup daerah MiFish-U (R-CUR-05). Bila ya, ukur jarak antarspesies *Telmatherina* di daerah MiFish | Agent | Laporan: berapa spesies bisa dibedakan, pasangan yang identik → masukan untuk `complexes.csv` | `[MVP]` |
| T-DATA-03 | Ekstrak checklist Malili dari Herder 2006/2012 dan Tantu & Nilawati 2007 | Manusia (PDF) + agent (ketik ke CSV) | `checklist.csv`, `introductions.csv` v0.1 | `[MVP]` |
| T-DATA-04 | Cari sekuens 12S/mitogenom publik untuk setiap spesies checklist Malili | Manusia (cari di GenBank/MitoFish/BOLD) + agent (kurasi) | Kamus v0.1 lebih lengkap | `[P1]` |
| T-DATA-05 | Unduh Dryad Lake St. Pierre (`edna_lg_clean.csv`, `elec_long.csv`, `fish_codes.csv`; `raw_seq.zip` bila perlu) | Manusia | `data/external/lake_st_pierre/` | `[MVP]` (CSV), `[P1]` (FASTQ) |
| T-DATA-06 | Unduh pustaka 12S Guyana (Figshare 29168144) | Manusia | `data/external/french_guiana_12s/` | `[MVP]` |
| T-DATA-07 | Bangkitkan data demo SIMULASI dengan seed tetap | Agent | `data/demo/matano_sim_v1/` | `[MVP]` |

## 3. Uji logika mesin

### 3.1 Leave-one-species-out (R-VAL-02)

**Pertanyaan:** bila spesies asli tidak ada di kamus, seberapa sering mesin tetap memberi nama spesies lain yang diberi keputusan aman?

**Prosedur:**
1. Pilih kamus uji K (mis. pustaka Guyana, atau kamus Malili v0.1 bila cukup besar).
2. Untuk setiap spesies X dengan ≥1 sekuens: buat K' = K tanpa X. Jadikan semua sekuens X sebagai "ASV query" dengan checklist perairan uji yang **memuat X** (X tercatat tetapi tidak berreferensi, persis kondisi celah nyata).
3. Jalankan BioTrace (L4 diset maksimal agar yang diuji hanya logika penamaan) dan baseline BLAST-97%.
4. Ulangi untuk semua X.

**Metrik:**

| ID | Metrik | Definisi | Target MVP |
|---|---|---|---|
| M1 | Nama keliru lolos aman | Query yang dilaporkan sebagai **spesies lain** (atau kompleks yang tidak memuat X) dengan keputusan `safe` / total query | Lebih rendah dari baseline |
| M2 | Menahan diri dengan benar | Query yang dilaporkan kompleks (memuat X), genus X, tingkat lebih tinggi yang benar, atau `unknown` / total query | ≥ 90% |
| M3 | Nama keliru di tingkat apa pun | Takson yang dilaporkan tidak memuat X / total | Dilaporkan, dibanding baseline |

### 3.2 Uji tanpa penyembunyian (mengukur sikap terlalu hati-hati)

Dengan kamus lengkap, cocokkan setiap sekuens ke K tanpa dirinya sendiri (spesies lain dari X tetap ada).

| ID | Metrik | Definisi |
|---|---|---|
| M4 | Spesies benar dilaporkan | Query yang dilaporkan sebagai spesies X dengan benar |
| M5 | Turun tingkat tanpa perlu | Query yang turun ke kompleks/genus padahal X bisa dibedakan |

M4 dan M5 menjaga agar BioTrace tidak "aman karena tidak pernah menjawab".

### 3.3 Dataset uji

| Dataset | Kegunaan | Keterbatasan | Tag |
|---|---|---|---|
| Fixture FX-1 | Uji perangkat lunak | Fiktif | `[MVP]` |
| Pustaka 12S Guyana (369 spesies, 88,92%) | LOSO pada pustaka tropis hampir lengkap | Marker Teleo1/12S-V5, bukan MiFish. Parameter ambang perlu dicatat terpisah | `[MVP]` |
| Kamus Malili v0.1 | LOSO lokal, uji resolusi kompleks | Kecil; belum tentu mencakup daerah MiFish | `[MVP]` bila T-DATA-02 berhasil |
| Lake St. Pierre | Presisi klaim A–B vs electrofishing; deteksi yang hilang | Perlu kamus 12S spesies Québec (susun dari GenBank untuk spesies di `fish_codes.csv`); tanpa field blank | `[P1]` |
| Simulasi kamus ikan laut tim (I-MarFish) | Pembanding historis (52% vs 16%) | Laut, internal, belum terbit | Arsip |

### 3.4 Format hasil

`validation/results/<tanggal>_<dataset>_<rules_version>.json`:

```json
{
  "dataset": "french_guiana_12s",
  "reference_version": "external:GF-2026",
  "rules_version": "r0.1",
  "n_species": 369,
  "metrics": {"M1": null, "M2": null, "M3": null, "M4": null, "M5": null},
  "baseline_blast97": {"M1": null, "M3": null, "M4": null},
  "notes": "marker Teleo1/12S-V5"
}
```

Angka hanya diisi dari hasil run nyata. Halaman P8 Validasi membaca file ini. **Jangan menampilkan angka validasi yang belum dijalankan.**

## 4. Validasi lapangan dan ahli `[P1]`

| ID | Kegiatan | Gerbang |
|---|---|---|
| VAL-F1 | Lake St. Pierre: presisi klaim A–B terhadap electrofishing | Target presisi ≥ 90% |
| VAL-F2 | Analisis ulang data eDNA Indonesia bila didapat dari penulis (Balantak, Kurniawan, Matano) | Minimal 1 dataset Indonesia berhasil dianalisis |
| VAL-E1 | Tinjauan buta: 50 klaim dinilai ahli ikan tanpa melihat keputusan BioTrace | ≥ 80% sepakat (Gerbang 2) |
| VAL-E2 | Kalibrasi ambang r0.2 dari VAL-E1 dan VAL-F1 | Ambang baru dicatat di 09 |

## 5. Jalur riset Paper 1 (memakai alat yang sama) `[P1]`

**Judul kerja:** Analisis celah referensi 12S (MiFish) untuk ikan air tawar Indonesia.

| Langkah | Isi |
|---|---|
| Penyebut | Checklist nasional Hubert dkk. 2015 + Catalog of Fishes + checklist danau |
| Pembilang | Sekuens dari GenBank, MitoFish, BOLD, MIDORI (diunduh manusia), dikurasi dengan R-CUR |
| Ekstraksi | Potong in silico daerah MiFish-U (R-CUR-05) |
| Analisis | Cakupan per pulau/famili/genus/status endemik; tiga lapis celah (tanpa sekuens, hanya COI, 12S tanpa voucher/berlabel salah) |
| Studi kasus | Malili: resolusi MiFish untuk *Telmatherina*/*Oryzias* |
| Pembanding | GAPeDNA (Marques dkk. 2021) |
| Status kebaruan | Belum ditemukan paper serupa khusus Indonesia (cek ulang di Scopus/Google Scholar/SINTA sebelum submit) |

Rencana jurnal ada di dokumen 08 / registri lengkap di Project.

## 6. Skrip demo (uji manual sebelum pitch) `[MVP]`

1. `make demo` di laptop tanpa internet.
2. Buka `http://localhost:8000`, klik "Muat data demo (SIMULASI)". Banner SIMULASI terlihat.
3. Ringkasan: keempat kotak keputusan terisi.
4. Klik "Wajib verifikasi" → buka kartu klaim endemik lemah: penyebab dan tindak lanjut terbaca.
5. Buka kartu kompleks *Telmatherina* → tingkat "kompleks", penyebab marker.
6. Buka kartu alias louhan → label invasif.
7. Halaman Kamus & Celah → grafik cakupan per genus untuk MATANO.
8. Unduh PDF → fingerprint ada, banner SIMULASI ada, kalimat "bukan dokumen AMDAL resmi" ada.
9. Matikan BLAST (ubah PATH) → demo tetap jalan dari hasil pra-hitung.
10. Waktu total demo ≤ 2 menit.
