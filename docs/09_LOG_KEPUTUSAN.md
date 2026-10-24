# 09 — Log Keputusan

Aturan pakai:
- Satu entri per keputusan. Entri lama **tidak dihapus**. Bila berubah, buat entri baru yang merujuk entri lama (`Menggantikan: D-xxx`).
- Status: `Diusulkan` → `Disetujui` / `Ditolak`. Hanya manusia (Ketua atau pemilik area) yang mengubah status ke `Disetujui`.
- AI agent boleh menambah entri berstatus `Diusulkan`, tetapi tidak boleh menyetujuinya.
- Keputusan `Disetujui` di sini menimpa dokumen lain bila bertentangan (kecuali 01; dalam kasus itu 01 diperbarui).

Templat:

```
### D-xxx — Judul singkat
- Tanggal:
- Status: Diusulkan | Disetujui | Ditolak
- Diusulkan oleh:
- Disetujui oleh:
- Konteks:
- Keputusan:
- Alasan:
- Dampak ke dokumen/kode:
- Menggantikan:
```

---

## Keputusan yang berlaku

### D-001 — Identitas produk
- Tanggal: 2026-10-24 · Status: **Disetujui** · Disetujui oleh: tim (sesi perencanaan 24 Okt)
- Keputusan: BioTrace adalah kamus DNA ikan air tawar tropis Indonesia + pemeriksa fakta eDNA yang hasilnya bisa diaudit.
- Alasan: Rumus penilaian bisa ditiru dan sudah ada versi publiknya; data spesimen lokal tidak bisa ditiru dan tidak bisa dibuat AI.
- Dampak: 01 §1–3, 02 §1.

### D-002 — Aset inti = kamus, bukan rumus
- Tanggal: 2026-10-24 · Status: **Disetujui**
- Keputusan: Metode publik (Polanco dkk. 2025, PhyloRef 2026) dipakai dan disitasi. Tidak mengklaim rumus skor sebagai inovasi.
- Dampak: 01 §3, 03 §13, halaman Metode.

### D-003 — Pengguna dan pembeli utama
- Tanggal: 2026-10-24 · Status: **Disetujui**
- Keputusan: Perusahaan korporat yang membutuhkan dokumen pendukung untuk perizinan dan pemantauan lingkungan (AMDAL, RKL-RPL), beserta konsultan penyusunnya. Lab = kanal. LSM = kolaborator/pendana.
- Batas: BioTrace menghasilkan laporan verifikasi pendukung, bukan dokumen AMDAL resmi. Keberterimaan data eDNA dalam AMDAL belum terverifikasi.
- Menggantikan: pembayar "LSM konservasi" di Pitch Deck v2.

### D-004 — Beachhead
- Status: **Disetujui**
- Keputusan: Kompleks Danau Malili / Sorowako, didekati sebagai kolaborasi riset (mis. tawaran analisis ulang), bukan penjualan langsung.

### D-005 — Kebijakan klaim
- Status: **Disetujui**
- Keputusan: Hanya angka terverifikasi. Daftar boleh/tunda/label/dilarang di 01 §8 dan 07 §2.

### D-006 — Batas legal spesimen
- Status: **Disetujui**
- Keputusan: Tim tidak memegang atau mengekspor spesimen ikan. Hanya mengolah data sekuens. Spesimen baru lewat mitra berizin.

### D-007 — Model bisnis bertahap
- Status: **Disetujui**
- Keputusan: Kolaborasi riset → verifikasi berbayar → lisensi kamus + hibah pengisian celah. Semua harga hipotesis sampai ≥5 wawancara.

### D-008 — Penasihat ahli
- Status: **Disetujui**
- Keputusan: Cari penasihat ahli taksonomi ikan sebelum klaim tingkat spesies dipakai di luar demo.

### D-009 — Stack
- Status: **Disetujui**
- Keputusan: Python `biotrace_core` + BLAST+ + FastAPI + React/Vite/TypeScript/Tailwind + penyimpanan berbasis file. Cadangan: Streamlit memanggil core yang sama.

### D-010 — Penyimpanan dokumen
- Status: **Disetujui**
- Keputusan: `docs/` di repo BIOTRACE untuk 01–06, 07 ringkas, dan 09. Project GENOHACK untuk 07 lengkap dan 08. Repo tidak memuat materi pitch.

### D-011 — Tahapan kamus dan isolasi data luar
- Status: **Disetujui**
- Keputusan: Kamus v0.1 (Malili) `[MVP]` → v0.2 (peta celah nasional) → v0.3 (12S publik Sulawesi) → v1.0 (spesimen bervoucher) → v2.0 (Asia Tenggara). Data luar Indonesia disimpan per wilayah dan hanya untuk mode validasi.

### D-012 — Tingkat "kompleks"
- Status: **Disetujui**
- Keputusan: "Kompleks" adalah tingkat nama yang sah dan dianggap jawaban benar, untuk kelompok yang tidak bisa dibedakan marker (mis. *Telmatherina* Matano, *Oryzias* Malili).

### D-013 — Level voucher
- Status: **Disetujui**
- Keputusan: V1–V4 (04 §2.3). V4 (eDNA/lingkungan) tidak pernah menjadi referensi.

### D-014 — Tanpa ML di MVP
- Status: **Disetujui** (dari PRD v2)

### D-015 — Deterministik dan jejak audit
- Status: **Disetujui** (dari PRD v2)

### D-016 — Label SIMULASI
- Status: **Disetujui** (dari PRD v2)

### D-017 — Marker
- Status: **Disetujui** (dari PRD v2)
- Keputusan: 12S MiFish-U utama; 16S dan COI opsional. r0.1 hanya satu marker per run.

---

## Keputusan yang diusulkan (aktif sebagai default r0.1 sampai disetujui/ditolak)

### D-018 — Kebijakan celah kerabat "strict"
- Tanggal: 2026-10-24 · Status: **Diusulkan** · Diusulkan oleh: Claude (dari rekomendasi deep research)
- Konteks: PRD v2 hanya mengurangi skor L1 bila >50% kerabat tanpa referensi. Riset menyarankan: jangan beri nama spesies bila genus itu punya spesies Indonesia di perairan tersebut yang belum berreferensi.
- Keputusan usulan: `congener_gap_policy = strict` (R-NAME-08). Alternatif `threshold` tersedia sebagai parameter.
- Dampak: lebih banyak klaim Malili turun ke kompleks/genus; nama keliru lebih sedikit.
- Perlu: persetujuan Ketua + Backend.

### D-019 — Kompleks dipertahankan hanya bila celah ada di dalam kompleks
- Status: **Diusulkan**
- Keputusan usulan: Klaim tetap di tingkat kompleks hanya bila semua kerabat tanpa referensi adalah anggota kompleks itu; jika tidak, turun ke genus (R-NAME-05, R-NAME-08).

### D-020 — Catatan baru untuk perairan tidak boleh "aman"
- Status: **Diusulkan**
- Konteks: Di PRD v2, nilai A–B selalu "aman" walau spesies tidak tercatat di perairan (L2 = 0).
- Keputusan usulan: R-DEC-08: tingkat spesies, nilai A–B, dan L2 = 0 → `with_note` (atau `must_verify` bila ada label L3).

### D-021 — Kolom wajib `waterbody_id`
- Status: **Diusulkan**
- Keputusan usulan: Metadata wajib memuat `waterbody_id` agar checklist dan modul wilayah ditentukan tanpa menebak dari koordinat. Penentuan dari koordinat `[P2]`.

### D-022 — Target metrik baru
- Status: **Diusulkan**
- Keputusan usulan: Target "nama keliru lolos < 16%" (PRD v2) diganti "lebih rendah dari baseline BLAST-97% pada data yang sama", karena 16% adalah hasil simulasi itu sendiri.

### D-023 — Parameter pra-proses
- Status: **Diusulkan**
- Keputusan usulan: `tag_jump_fraction = 0.001` (relatif terhadap total bacaan ASV dalam run); lokasi dengan 1 replikat mendapat L4 = 1 disertai peringatan.

### D-024 — LSM sebagai kolaborator, bukan pembeli utama
- Status: **Diusulkan** (konsekuensi D-003)
- Keputusan usulan: Persona LSM dipindah dari pengguna utama ke kolaborator/pendana di PRD v3 dan deck.

### D-025 — Dashboard hasil satu halaman
- Tanggal: 2026-10-24 · Status: **Disetujui** · Disetujui oleh: Agathan (frontend)
- Keputusan: Halaman P2–P6 digabung menjadi satu halaman Hasil: ringkasan, perhatian utama, keputusan per lokasi, daftar klaim + Evidence Card panel samping, kamus & celah, prioritas barcode, audit. Rincian di 10 §4.
- Menggantikan: pembagian halaman P2–P6 di 02 §7.

### D-026 — Unggah dengan drag & drop dan deteksi peran file
- Status: **Disetujui** · Disetujui oleh: Agathan
- Keputusan: Halaman Unggah satu kartu bersih, drag & drop banyak file, peran file dideteksi dari isi. Rincian di 10 §3.

### D-027 — Sistem desain
- Status: **Diusulkan** · Diusulkan oleh: Claude
- Keputusan usulan: Token warna, Inter + JetBrains Mono, radius dan jarak sesuai 10 §2; tanpa aset dari CDN.

### D-028 — Unduhan data lewat skrip
- Status: **Diusulkan** · Diusulkan oleh: Claude
- Keputusan usulan: Dataset publik diunduh dengan `scripts/fetch_data.py` ke `raw/` beserta log; agent boleh menjalankannya bila diminta manusia. Mesin inti tetap tanpa jaringan (A8, A13). Nama spesies asli hanya dari file sumber (A14).

---

## Konflik terbuka

### K-001 — Angka "4 → 34" Roussel dkk. 2026
- Tanggal: 2026-10-24
- Isi: Pembacaan halaman bioRxiv v2 pada sesi perencanaan menemukan kalimat "only four species were detected by all four eDNA companies" dan peningkatan ke 34 setelah analisis ulang. Laporan deep research menyatakan angka itu tidak ditemukan.
- Status: Ditunda. Jangan dipakai di pitch sampai dicek di teks penuh/suplemen.
- Pemilik: Ketua.

### K-002 — "Sekitar 630 endemik"
- Isi: Angka dari PRD v2 dan deck belum ditemukan di teks primer Hubert dkk. 2015.
- Status: Ditunda. Pakai "1.172 spesies asli" saja.
