# 10 — Desain UI, Laporan PDF, dan Data Demo

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Tunduk pada | `01_KONSEP_INDUK.md`, `02_PRD_v3.md`, `05_ARSITEKTUR.md`, `09_LOG_KEPUTUSAN.md` (D-025 s.d. D-028) |
| Mengubah | 02 §7: halaman P2–P6 digabung menjadi **satu halaman Hasil** (D-025) |

---

## 1. Prinsip visual

1. **Tenang dan ilmiah.** Banyak ruang kosong, sedikit warna. Warna kuat hanya untuk keputusan dan peringatan.
2. **Satu layar, satu cerita.** Pengguna memahami hasil tanpa berpindah halaman.
3. **Teks dulu, warna kedua.** Setiap warna keputusan selalu disertai label teks.
4. **Offline.** Tidak ada font, peta, atau ikon dari CDN. Semua aset dibundel.

## 2. Token desain `[MVP]`

### 2.1 Warna

| Token | Nilai | Pakai untuk |
|---|---|---|
| `--bg` | `#F7F9FA` | Latar halaman |
| `--surface` | `#FFFFFF` | Kartu, tabel |
| `--border` | `#E3E8EC` | Garis kartu, pemisah |
| `--text` | `#14212B` | Teks utama |
| `--text-muted` | `#5B6B78` | Teks sekunder, label |
| `--accent` | `#0F766E` | Tombol utama, tautan, elemen merek (teal = air) |
| `--accent-soft` | `#E6F4F2` | Latar zona drag & drop aktif, sorotan |
| `--decision-safe` | `#15803D` (latar `#EAF6EE`) | Aman dilaporkan |
| `--decision-note` | `#1D4ED8` (latar `#EAF0FD`) | Dengan catatan |
| `--decision-verify` | `#C2410C` (latar `#FDF0E8`) | Wajib verifikasi |
| `--decision-stop` | `#B91C1C` (latar `#FDECEC`) | Jangan dipakai |
| `--sim` | `#A16207` (latar `#FEF7E0`) | Banner dan badge SIMULASI |

Grade badge A–D memakai skala abu-teal: A `#0F766E`, B `#3B8C84`, C `#8A9AA5`, D `#5B6B78` (teks putih), selalu dengan huruf.

### 2.2 Tipografi

| Peran | Font | Ukuran |
|---|---|---|
| UI | **Inter** (dibundel lewat `@fontsource/inter`) | 14 px dasar; judul bagian 18 px semibold; angka KPI 28 px semibold |
| ID, hash, sekuens | **JetBrains Mono** (`@fontsource/jetbrains-mono`) | 12–13 px |
| Nama ilmiah | Inter *italic* | Ikut konteks |

### 2.3 Bentuk dan jarak

- Radius kartu 10 px, tombol 8 px, badge 999 px (pil).
- Bayangan sangat halus: `0 1px 2px rgba(20,33,43,.06)`.
- Grid 12 kolom, lebar konten maks 1280 px, gutter 24 px; padding kartu 20 px.
- Ikon: `lucide-react` (dibundel), garis 1,75 px.
- Lebar minimum yang didukung: 1280 px (laptop demo). Tampilan ponsel `[P1]`.

## 3. Halaman Unggah (P1) `[MVP]`

Tujuan: bersih, satu kartu di tengah, selesai dalam tiga gerakan (tarik file → periksa → jalankan).

```
┌────────────────────────────────────────────────────────────┐
│  BioTrace Indonesia                         Metode  Validasi│
├────────────────────────────────────────────────────────────┤
│                                                            │
│      Periksa nama ikan dalam data eDNA Anda                 │
│      Tarik semua file sekaligus. Kami kenali jenisnya.      │
│                                                            │
│   ┌──────────────────────────────────────────────────┐     │
│   │             ⇪                                     │     │
│   │   Tarik & lepas file di sini                      │     │
│   │   atau  [Pilih file]                              │     │
│   │   .csv .tsv .fasta .fa .fna · maks 200 MB         │     │
│   └──────────────────────────────────────────────────┘     │
│                                                            │
│   File terdeteksi                                          │
│   ✓ Tabel bacaan      reads.csv        2.000 ASV × 15 sampel│
│   ✓ Metadata sampel   metadata.csv     5 lokasi · MATANO    │
│   ✓ Urutan ASV        asv.fasta        2.000 urutan         │
│   ○ Taksonomi lab     (opsional bila ada FASTA)             │
│   ○ Konteks lokasi    (opsional)                            │
│                                                            │
│   ⚠ 1 peringatan: batch B2 tanpa kontrol negatif   [Lihat]  │
│                                                            │
│   [ Jalankan analisis ]        Coba data demo (SIMULASI)    │
└────────────────────────────────────────────────────────────┘
```

Perilaku:
- **Drag & drop banyak file sekaligus** (`react-dropzone`). Zona berubah warna `--accent-soft` saat file di atasnya.
- **Deteksi peran file otomatis** dari isi, bukan hanya nama:
  - FASTA → baris pertama diawali `>`.
  - Metadata → punya kolom `sample_type` dan `waterbody_id`.
  - Taksonomi → punya kolom `pct_identity`.
  - Bacaan → kolom `asv_id` + (`reads` atau banyak kolom angka).
  - Ambigu → pengguna memilih peran dari dropdown pada baris file.
- Setiap baris file punya tombol hapus dan ganti.
- Validasi ringan dilakukan di browser (header, jumlah baris). Validasi penuh V-01..V-10 di server setelah tombol ditekan, ditampilkan di bawah daftar file.
- Tombol **Jalankan** aktif hanya bila bacaan + metadata + (FASTA atau taksonomi) ada.
- Saat berjalan: indikator langkah `Validasi → Penamaan → Penilaian → Laporan`, lalu otomatis pindah ke halaman Hasil.
- "Coba data demo (SIMULASI)" adalah tombol sekunder (garis), bukan tombol utama.

## 4. Halaman Hasil — dashboard satu halaman `[MVP]`

Semua yang dibutuhkan pengguna ada di satu halaman yang di-scroll. Navigasi bagian memakai daftar isi lengket (sticky) di kiri atau tab jangkar di atas.

```
┌──────────────────────────────────────────────────────────────────────┐
│ ◀ Unggah baru   Danau Matano · 5 lokasi · 24 Okt 2026   [SIMULASI]    │
│                                       [Unduh PDF] [Unduh CSV] [Audit] │
├──────────────────────────────────────────────────────────────────────┤
│ ① RINGKASAN                                                          │
│ ┌────────┐┌────────┐┌────────┐┌────────┐┌──────────────────┐         │
│ │ 42     ││ 16     ││ 38%    ││ 5      ││ Kamus MATANO 41% │         │
│ │ klaim  ││ taksa  ││ aman   ││ wajib  ││ spesies punya    │         │
│ │        ││ unik   ││        ││ verif. ││ referensi        │         │
│ └────────┘└────────┘└────────┘└────────┘└──────────────────┘         │
│ ┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐          │
│ │ AMAN        ││ DGN CATATAN ││ WAJIB VERIF ││ JANGAN PAKAI│ ← klik = │
│ │ 16 klaim    ││ 12 klaim    ││ 10 klaim    ││ 4 klaim     │   filter │
│ │ 6 taksa     ││ 4 taksa     ││ 5 taksa     ││ 1 taksa     │   tabel  │
│ │ tindak lanjut ││ ...       ││ ...         ││ ...         │          │
│ └─────────────┘└─────────────┘└─────────────┘└─────────────┘          │
├──────────────────────────────────────────────────────────────────────┤
│ ② PERHATIAN UTAMA                    │ ③ KEPUTUSAN PER LOKASI          │
│ • Telmatherina … endemik, nilai D →  │  S1 ████████░░░                  │
│   wajib verifikasi            [kartu]│  S2 ██████░░░░░                  │
│ • kemungkinan louhan hibrida (invasif)│  S3 ...   (stacked bar 4 warna) │
│ • DNA di kontrol negatif batch B1    │                                  │
│ (maks 5 butir, urut: endemik, invasif, kontaminasi, lainnya)           │
├──────────────────────────────────────────────────────────────────────┤
│ ④ DAFTAR KLAIM   [Cari…] [Keputusan ▾] [Lokasi ▾] [Label ▾]           │
│ Lokasi │ Nama dari lab │ Nama aman │ Tingkat │ Nilai │ Keputusan │ Label│
│ ... (klik baris → Evidence Card di panel samping kanan)               │
├──────────────────────────────────────────────────────────────────────┤
│ ⑤ KAMUS & CELAH (MATANO)             │ ⑥ PRIORITAS BARCODE (top 10)    │
│  Telmatherina ██████░░░  6/17        │ 1. … endemik, belum ada referensi│
│  Oryzias      ███░░░     1/2 …       │ 2. …                             │
├──────────────────────────────────────────────────────────────────────┤
│ ⑦ JEJAK AUDIT & BATAS INTERPRETASI                                    │
│ Sidik jari laporan  a1b2c3…  [salin]  · Kamus v0.1 · Aturan r0.1      │
│ Deteksi DNA bukan bukti pasti ikan hidup di lokasi. Laporan ini adalah │
│ verifikasi pendukung, bukan dokumen AMDAL resmi.                       │
└──────────────────────────────────────────────────────────────────────┘
```

Catatan: angka pada sketsa hanya contoh tata letak, bukan data.

Rincian bagian:

| # | Bagian | Isi | Fitur |
|---|---|---|---|
| Header | Konteks run | Perairan, jumlah lokasi, tanggal, badge SIMULASI, tombol Unduh PDF / CSV (zip) / Audit (menggulir ke ⑦) | F22, F24 |
| ① | Ringkasan | 5 KPI: total klaim, taksa unik, % klaim aman, jumlah klaim wajib verifikasi, cakupan kamus perairan (Σr/Σn). Lalu 4 kotak keputusan: jumlah klaim, jumlah taksa, satu kalimat tindak lanjut baku (02 §7). Klik kotak = filter tabel ④ dan gulir ke sana | F22 |
| ② | Perhatian utama | Maks 5 butir: klaim endemik `must_verify`, alias/invasif, kontaminasi kontrol negatif, "tidak dikenal" dengan bacaan tertinggi. Tiap butir membuka kartu | F15, F20 |
| ③ | Keputusan per lokasi | Stacked bar horizontal per `site_id` (Recharts), 4 warna keputusan + label jumlah. Tanpa peta (offline). Peta `[P1]` | F22 |
| ④ | Daftar klaim | TanStack Table: cari, filter, sortir; nama ilmiah miring; badge nilai dan keputusan. Klik baris → **Evidence Card** di panel samping kanan (lebar 480 px), tabel tetap terlihat | F23, F38 |
| ⑤ | Kamus & celah | Bar per genus (r dari n), diurutkan dari P_missing terbesar; tooltip daftar spesies tanpa referensi; info versi kamus dan jumlah sekuens per level voucher | F7, F40 |
| ⑥ | Prioritas barcode | 10 teratas dari `barcode_priority.csv` + tautan "lihat semua" (modal) | F25 |
| ⑦ | Audit & batas | Fingerprint (salin), SHA-256 file input (expand), versi kamus/aturan/engine/BLAST, kalimat batas interpretasi, pernyataan "bukan dokumen AMDAL resmi" | F4, A10, A11 |

**Evidence Card (panel samping):**
1. Judul: *nama aman* + badge tingkat; di bawahnya "Dari lab: *nama lab*" dicoret tipis bila berbeda.
2. Baris badge: Nilai, Keputusan, label L3.
3. "Kenapa?" — daftar penyebab dengan ikon, lalu alasan per lapisan (tab ID / EN).
4. "Bukti": skor L1/L2/L4 (mini bar 0–2), kecocokan dalam 0,5% (tabel kecil spesies + %), voucher pendukung (level + aksesi), peluang belum di kamus.
5. "Asal-usul (kemungkinan)".
6. "Tindak lanjut" (kotak berwarna keputusan).
7. Kalimat batas interpretasi.

Halaman lain tetap terpisah lewat navigasi atas: **Metode** (P7) dan **Validasi** (P8).

## 5. Laporan PDF `[MVP]`

- **A4 tegak**, margin 18 mm, ReportLab. Font: DejaVu Sans (dibundel, mendukung karakter Indonesia) atau Helvetica bawaan.
- **Header setiap halaman:** "BioTrace Indonesia · Laporan Verifikasi Data eDNA (Pendukung)". **Footer:** nomor halaman, 12 karakter pertama `report_fingerprint`, "Bukan dokumen AMDAL resmi".
- **Watermark diagonal "SIMULASI"** abu-abu muda di setiap halaman bila run memakai data demo.
- Warna keputusan sama dengan token UI (versi cetak tetap terbaca hitam-putih karena ada label teks).

| Halaman | Isi |
|---|---|
| 1 | **Ringkasan eksekutif**: identitas proyek dan perairan; 5 KPI; tabel 4 keputusan (jumlah klaim, taksa, tindak lanjut); 5 butir perhatian utama; fingerprint lengkap |
| 2–n | **Tabel klaim** (lokasi, nama lab, nama aman, tingkat, nilai, keputusan, penyebab), diurutkan per keputusan lalu lokasi |
| Lampiran A | **Evidence Card** untuk setiap klaim `must_verify` dan `do_not_use` (2 kartu per halaman) |
| Lampiran B | **Kamus & celah**: tabel cakupan per genus, 20 prioritas barcode teratas |
| Lampiran C | **Metode singkat** + tabel parameter r0.1 ("usulan tim, belum dikalibrasi ahli") + sitasi metode (03 §13) |
| Lampiran D | **Jejak audit**: SHA-256 input, versi, parameter BLAST; daftar sumber kamus + lisensi |
| Penutup | Batas interpretasi dan pernyataan laporan pendukung |

## 6. Spesifikasi data demo `data/demo/matano_sim_v1/` `[MVP]`

### 6.1 Aturan nama

- **Nama spesies asli hanya boleh diambil dari file yang diunduh manusia di `raw/`** (mis. record GenBank Stelbrink 2014). Model AI tidak boleh mengisi nama spesies dari ingatannya.
- Bila `raw/` belum ada, pakai nama fiktif bergaya ilmiah (mis. *Telmasim alpha*) dan nama perairan tetap `MATANO`.
- Semua file dan baris `is_simulated = true`; README menyebut SIMULASI.

### 6.2 Desain run

| Elemen | Nilai |
|---|---|
| Perairan | `MATANO` |
| Lokasi | `MAT-S1` … `MAT-S5`, koordinat di sekitar Danau Matano (±-2,47; 121,33), dibuat tim |
| Replikat | 3 per lokasi → 15 sampel lapangan |
| Batch ekstraksi | `B1` (S1–S3), `B2` (S4–S5), masing-masing 1 `kontrol_negatif_ekstraksi`; ditambah 1 `kontrol_negatif_pcr` |
| Marker | `12S_MiFish_U` |
| Panjang ASV | 170 bp |
| Identitas | Dikendalikan lewat jumlah mismatch: `identitas = (170 − k)/170` (k=1 → 99,41%; k=2 → 98,82%; k=3 → 98,24%; k=5 → 97,06%; k=8 → 95,29%; k=15 → 91,18%) |
| Kamus demo | Sekuens referensi sintetis 170 bp per spesies, dengan jarak antarspesies yang dirancang; `source_db = simulated` |
| Seed acak | Tetap (mis. 20261025) agar data bisa dibangkitkan ulang identik |

### 6.3 Skenario 16 nama dari lab

Setiap skenario harus menghasilkan keputusan yang tercantum. Ini sekaligus tes integrasi (T-SIM-SCN).

| # | Skenario | Aturan yang diuji | Keputusan target |
|---|---|---|---|
| 1 | Spesies endemik, referensi lengkap, 3/3 replikat | R-NAME-07, R-DEC-01 | `safe` (A) |
| 2 | Spesies asli non-endemik, kuat | R-DEC-01 | `safe` (A) |
| 3 | Ikan introduksi (mis. nila) kuat | R-DEC-01, label invasif | `safe` (A) — menunjukkan bahwa label invasif tidak otomatis menurunkan keputusan bila bukti kuat |
| 4 | Dua spesies dalam 0,5%, anggota satu kompleks | R-NAME-05 | `safe` di tingkat kompleks |
| 5 | Kandidat spesies, tetapi kerabat di danau tanpa referensi (non-kompleks) | R-NAME-08 | `safe` (A) di tingkat genus, penyebab referensi |
| 6 | Endemik, kandidat spesies, kerabat dalam kompleks tanpa referensi, 2/3 replikat | R-NAME-08 → kompleks, C | `must_verify` |
| 7 | Endemik, bacaan total < 10 | R-SCORE-06 | `must_verify` (D) |
| 8 | Nama induk louhan | R-NAME-11 | `must_verify` |
| 9 | Ikan invasif, DNA juga di kontrol negatif B1 | R-SCORE-06, R-DEC-07 | `must_verify` (D) + teks "jangan dasar pemberantasan" |
| 10 | Spesies non-L3 di kontrol negatif B2 | R-SCORE-06, R-DEC-04 | `do_not_use` |
| 11 | Spesies non-L3, 1/3 replikat, bacaan rendah | R-DEC-04 | `do_not_use` |
| 12 | Identitas 91% | R-NAME-03 | `with_note` (tidak dikenal) |
| 13 | Identitas 92%, beda lokasi | R-NAME-03 | `with_note` (tidak dikenal) |
| 14 | Identitas 97% satu spesies | R-NAME-09 | `with_note` (genus, C) |
| 15 | Spesies tercatat di Indonesia tetapi tidak di checklist Matano | R-DEC-08 | `with_note` |
| 16 | Dua spesies dalam 0,5%, bukan kompleks | R-NAME-06 | `safe` (A) di tingkat genus, penyebab marker |

Satu ASV boleh muncul di beberapa lokasi, jadi jumlah klaim > 16. Target sebaran klaim: keempat keputusan masing-masing ≥ 2 klaim.

Varian tambahan `matano_sim_v1_labtax/` (tanpa FASTA, memakai `taxonomy.csv`) untuk menguji R-NAME-10 dan R-NAME-12: minimal satu nama dari lab yang tidak tercatat di Indonesia.

## 7. Kriteria penerimaan desain

| ID | Kriteria |
|---|---|
| UI-01 | Unggah 3 file sekaligus lewat drag & drop; peran file terdeteksi otomatis |
| UI-02 | Dari klik "Jalankan" sampai halaman Hasil tanpa interaksi tambahan |
| UI-03 | Halaman Hasil memuat bagian ①–⑦ dalam satu halaman; klik kotak keputusan memfilter tabel |
| UI-04 | Evidence Card terbuka di panel samping tanpa meninggalkan halaman |
| UI-05 | Banner/badge SIMULASI terlihat di header Hasil, di halaman Unggah saat demo, dan watermark PDF |
| UI-06 | Tidak ada permintaan jaringan ke domain luar saat aplikasi berjalan (cek tab Network) |
| UI-07 | Semua teks Bahasa Indonesia; nama ilmiah miring |
| UI-08 | PDF halaman 1 bisa dibaca berdiri sendiri sebagai ringkasan eksekutif |
