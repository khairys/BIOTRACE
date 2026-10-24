# 02 — PRD BioTrace Indonesia v3

| Atribut | Isi |
|---|---|
| Versi | 3.0 · 24 Oktober 2026 |
| Menggantikan | PRD BioTrace Indonesia v2 (24 Oktober 2026) |
| Tunduk pada | `01_KONSEP_INDUK.md`, `09_LOG_KEPUTUSAN.md` |
| Rincian aturan | `03_ATURAN_MESIN.md` · Rincian data: `04_SPESIFIKASI_DATA.md` · Rincian teknis: `05_ARSITEKTUR.md` |

---

## 1. Perubahan dari v2

| Area | v2 | v3 |
|---|---|---|
| Identitas | Penjaga data + mesin cek, skor sebagai sorotan | **Kamus referensi sebagai aset inti**; mesin cek sebagai produk di atasnya |
| Pengguna utama | Konsultan lingkungan dan LSM konservasi | **Perusahaan korporat yang butuh dokumen pendukung perizinan/pemantauan lingkungan (AMDAL, RKL-RPL)** dan konsultannya |
| Tingkat nama | Spesies, genus, famili, tidak dikenal | Ditambah **kompleks** (mis. "kompleks *Telmatherina* Matano") |
| Referensi | Sekuens tervalidasi | Ditambah **level voucher V1–V4** yang ditampilkan di setiap kartu |
| Metadata input | Tanpa identitas perairan | Kolom wajib baru **`waterbody_id`** |
| Halaman | Ringkasan, tabel klaim, kartu | Ditambah halaman **Kamus & Celah** sebagai halaman utama cerita aset |
| Data luar | Lake St. Pierre untuk uji | Semua data luar Indonesia disimpan per wilayah, hanya untuk mode validasi |
| Kurasi | Tidak dirinci | **Alat impor dan kurasi kamus** `[MVP]` |
| LSM | Pengguna utama | Menjadi kolaborator/pendana, bukan pembeli utama |

---

## 2. Tujuan MVP

MVP berhasil bila:
1. Pengguna bisa mengunggah data eDNA dan mendapat ringkasan keputusan dalam satu halaman, dalam waktu di bawah 2 menit.
2. Setiap nama ikan didukung referensi Indonesia yang tervalidasi, atau diturunkan ke tingkat aman, atau dinyatakan "tidak dikenal".
3. Setiap keputusan bisa ditelusuri ke data, kamus, dan aturan yang menghasilkannya.
4. Kamus awal Malili v0.1 dan peta celahnya terlihat di dashboard.
5. Semua data demo sintetis berlabel SIMULASI.

## 3. Non-tujuan

- Mengambil sampel, mengekstraksi DNA, atau menyekuensing.
- Mengolah FASTQ di MVP (`[P2]` lewat pipeline terbuka).
- Menerbitkan dokumen AMDAL resmi.
- Melacak asal populasi atau memperkirakan kelimpahan.
- Machine learning di MVP.
- Menamai ikan Indonesia dengan referensi spesies yang tidak tercatat di Indonesia.
- Akun pengguna, login, dan multi-tenant di MVP (`[P1]`).

---

## 4. User stories dan kriteria penerimaan

| ID | Sebagai | Saya ingin | Supaya | Kriteria penerimaan | Tag |
|---|---|---|---|---|---|
| US1 | Konsultan penyusun dokumen | Mengunggah 2–3 CSV dan FASTA, lalu langsung mendapat daftar klaim berisiko | Saya bisa memeriksa data sebelum masuk dokumen klien | Proyek 200 sampel × 2.000 ASV selesai < 2 menit di laptop; kolom yang hilang dicatat sebagai peringatan tanpa menghentikan proses kecuali kolom wajib | `[MVP]` |
| US2 | Konsultan | Urutan yang tidak cocok dengan referensi mana pun dilaporkan "tidak dikenal" | Dokumen tidak memuat nama ikan yang salah | Kemiripan terbaik < `unknown_below_pct` tidak pernah diberi nama; masuk daftar prioritas barcode | `[MVP]` |
| US3 | Manajer lingkungan perusahaan | Membaca satu halaman ringkasan keputusan | Saya bisa memutuskan tindak lanjut tanpa membaca semua kartu | Halaman memuat jumlah klaim per keputusan, jumlah taksa unik, dan satu tindak lanjut per kategori | `[MVP]` |
| US4 | Konsultan | Tahu kenapa sebuah klaim tidak pasti | Saya bisa memilih langkah cek yang tepat | Setiap klaim bernilai B–D atau tingkat di atas spesies menyebut ≥1 penyebab: referensi, marker, sampel, lokasi | `[MVP]` |
| US5 | Manajer lingkungan | Ikan invasif hibrida tertangkap walau lab menulis nama spesies induknya | Peringatan invasif tidak terlewat | Nama di tabel alias diberi label "kemungkinan louhan hibrida" dan label invasif | `[MVP]` |
| US6 | Manajer lingkungan | Ikan endemik berbukti lemah tidak dibuang dan tidak dipastikan | Ikan endemik tidak dinyatakan tidak ada atau ada tanpa bukti | Klaim berlabel endemik bernilai C–D selalu berkeputusan `must_verify` | `[MVP]` |
| US7 | Penilai/auditor | Memastikan laporan tidak diubah dan tahu versi kamus yang dipakai | Saya bisa menelusuri setiap klaim | Laporan memuat SHA-256 tiap file input, versi kamus, versi aturan; input yang sama menghasilkan sidik jari identik | `[MVP]` |
| US8 | Kolaborator kampus | Melihat sumber, aksesi, dan level voucher setiap sekuens referensi | Saya bisa membantu memperbaiki kamus | Setiap sekuens punya sumber, aksesi, level voucher, status kurasi; klaim spesies hanya didukung V1–V3 berstatus `accepted` | `[MVP]` |
| US9 | Manajer lingkungan | Melihat seberapa lengkap kamus untuk danau saya | Saya paham kenapa banyak hasil berhenti di genus | Halaman Kamus & Celah menampilkan cakupan per genus untuk `waterbody_id` proyek | `[MVP]` |
| US10 | Konsultan | Kelompok spesies yang memang tidak bisa dibedakan dilaporkan sebagai kompleks | Saya tidak salah menulis spesies, dan laporan tetap informatif | Kecocokan yang seluruhnya anggota satu kompleks dilaporkan sebagai kompleks dengan penyebab `marker` | `[MVP]` |
| US11 | Kurator data (tim) | Mengimpor FASTA + metadata sekuens baru ke kamus dengan validasi otomatis | Kamus tumbuh tanpa merusak versi lama | Impor menghasilkan versi kamus baru, laporan kurasi (diterima/ditandai/ditolak + alasan), dan manifest SHA-256 | `[MVP]` |
| US12 | Penilai/auditor | Memverifikasi keaslian laporan dari kode di PDF | Saya yakin laporan tidak dipalsukan | Halaman verifikasi menerima kode dan menampilkan sidik jari | `[P1]` |
| US13 | Ahli ikan | Menambah catatan dan menandai kartu "sudah diverifikasi" | Hasil tinjauan tercatat | Catatan tersimpan dengan nama dan tanggal | `[P1]` |

---

## 5. Alur pengguna

```
Lab selesai → Konsultan/perusahaan unggah file → Validasi input → Mesin cek
   → Ringkasan keputusan → Tabel klaim → Evidence Card → Laporan PDF/CSV
   → (klaim "tidak dikenal" & celah) → Daftar prioritas barcode → Kolaborator
```

1. **Unggah**: pengguna memilih file atau menekan "Muat data demo".
2. **Validasi**: sistem mengecek kolom wajib, konsistensi ID, dan kontrol negatif, lalu menampilkan peringatan.
3. **Proses**: penamaan ulang (bila ada FASTA), penilaian, keputusan.
4. **Ringkasan**: empat kotak keputusan + tindak lanjut.
5. **Telusuri**: tabel klaim, filter, buka Evidence Card.
6. **Kamus & Celah**: cakupan per genus untuk danau proyek + daftar prioritas barcode.
7. **Laporan**: unduh PDF (Bahasa Indonesia) dan CSV, lengkap dengan jejak audit.

---

## 6. Kebutuhan fungsional

ID dipertahankan dari v2 bila fungsinya sama. ID baru mulai dari F37.

### 6.1 Input dan validasi

| ID | Kebutuhan | Tag |
|---|---|---|
| F1 | Unggah tabel bacaan (format panjang atau lebar) dan metadata sampel | `[MVP]` |
| F2 | Unggah FASTA ASV; bila ada, memicu pencocokan ulang ke kamus BioTrace | `[MVP]` |
| F11 | Tanpa FASTA, pakai tabel taksonomi lab dengan catatan "dinilai dengan database lab" | `[MVP]` |
| F3 | Cek kolom wajib, konsistensi `sample_id`, koordinat, kontrol negatif per batch; kekurangan dicatat sebagai peringatan | `[MVP]` |
| F42 | Kolom metadata wajib `waterbody_id` untuk menentukan checklist dan modul wilayah | `[MVP]` |
| F4 | Simpan SHA-256 tiap file input, versi kamus, dan versi aturan | `[MVP]` |
| F33 | Terima FASTQ lewat pipeline terbuka (Illumina, Nanopore) | `[P2]` |
| F36 | Templat formulir lapangan dan daftar permintaan standar ke lab | `[P2]` |

### 6.2 Kamus referensi

| ID | Kebutuhan | Tag |
|---|---|---|
| F5 | Kamus referensi Indonesia v0.1 (Malili): tiap sekuens berlabel sumber, aksesi, level voucher, status kurasi | `[MVP]` |
| F6 | Checklist perairan Malili termasuk ikan introduksi; daftar status endemik/terancam/invasif; tabel alias hibrida | `[MVP]` |
| F37 | Tabel kompleks spesies (mis. *Telmatherina* Matano, *Oryzias* Malili) | `[MVP]` |
| F7 | Peta kelengkapan per genus per perairan, dihitung ulang setiap versi kamus berubah | `[MVP]` |
| F39 | Alat impor dan kurasi: validasi skema, normalisasi nama, cek panjang daerah MiFish, deteksi konflik, laporan kurasi, versi baru + manifest | `[MVP]` |
| F31 | Antarmuka kolaborator untuk mengusulkan dan memvalidasi sekuens | `[P1]` |
| F35 | Perluasan wilayah: danau Sulawesi lain, Danau Toba, lalu Asia Tenggara | `[P2]` |
| F43 | Peta celah 12S seluruh ikan air tawar Indonesia (dasar Paper 1) | `[P1]` |

### 6.3 Penamaan, penilaian, keputusan

| ID | Kebutuhan | Tag |
|---|---|---|
| F8 | BLAST ke kamus aktif wilayah; simpan semua kecocokan dalam jendela 0,5% dari yang terbaik | `[MVP]` |
| F9 | Tentukan tingkat nama: spesies, kompleks, genus, famili, ordo, atau tidak dikenal | `[MVP]` |
| F10 | Kecocokan ke spesies yang tidak tercatat di Indonesia tidak dilaporkan sebagai spesies itu | `[MVP]` |
| F12 | Audit L4: replikat positif, kontrol negatif per batch, ambang data nyasar | `[MVP]` |
| F13 | Audit L1: kemiripan, selisih dengan spesies lain, kelengkapan kamus | `[MVP]` |
| F14 | Audit L2: cek checklist perairan, termasuk lewat tabel alias | `[MVP]` |
| F15 | Audit L3: label endemik, terancam, invasif, alias hibrida | `[MVP]` |
| F16 | Skor 0–5 → nilai A–D, dengan batas maksimal D | `[MVP]` |
| F17 | Penyebab ketidakpastian per klaim | `[MVP]` |
| F18 | Peluang spesies asli belum di kamus per klaim | `[MVP]` |
| F20 | Petakan setiap klaim ke satu dari empat keputusan + tindak lanjut | `[MVP]` |
| F21 | Kemungkinan asal-usul (status di lokasi, jalur masuk, sumber DNA lain) dengan bahasa "kemungkinan" | `[MVP]` (teks dari tabel; minimal untuk spesies Malili di demo) |
| F19 | Tingkat galat terkalibrasi per nilai A–D | `[P1]` |
| F34 | Kalibrasi ambang dari kasus yang diverifikasi ahli (ML) | `[P2]` |
| F32 | Cocokkan ulang laporan lama saat kamus diperbarui, tampilkan klaim yang berubah | `[P2]` |

### 6.4 Output

| ID | Kebutuhan | Tag |
|---|---|---|
| F22 | Ringkasan keputusan satu halaman | `[MVP]` |
| F23 | Evidence Card per klaim: nama lab vs nama aman, nilai, penyebab, voucher pendukung, label, keputusan, tindak lanjut, batas interpretasi; alasan dalam Bahasa Indonesia dan Inggris | `[MVP]` |
| F38 | Level voucher pendukung ditampilkan di setiap kartu | `[MVP]` |
| F24 | Ekspor laporan PDF Bahasa Indonesia dan CSV | `[MVP]` |
| F25 | Daftar prioritas barcode dari klaim "tidak dikenal" dan celah kamus | `[MVP]` |
| F40 | Halaman Kamus & Celah: statistik kamus, cakupan per genus, daftar prioritas | `[MVP]` |
| F28 | Kode verifikasi laporan untuk penilai/auditor/bank | `[P1]` |
| F29 | Catatan ahli dan tombol "tandai sudah diverifikasi" per kartu | `[P1]` |
| F30 | Akumulasi peta celah lintas laporan (agregat, dengan persetujuan pemilik data) | `[P1]` |
| F44 | Format lampiran laporan yang selaras dengan struktur dokumen lingkungan (rona awal, pemantauan) | `[P1]` (setelah struktur regulasi terverifikasi) |

### 6.5 Uji mesin

| ID | Kebutuhan | Tag |
|---|---|---|
| F26 | Modul uji "tanpa satu spesies" (leave-one-species-out) pada kamus aktif | `[MVP]` |
| F27 | Mode validasi dengan kamus luar per wilayah (Lake St. Pierre, Guyana) yang terpisah dari kamus Indonesia | `[MVP]` (minimal satu dataset) |
| F41 | Pembanding baseline "BLAST-97% langsung" pada data yang sama | `[MVP]` |

---

## 7. Halaman dashboard

> **Diperbarui oleh D-025:** P2–P6 digabung menjadi satu halaman **Hasil** (dashboard satu halaman). Tata letak, token desain, dan Evidence Card dirinci di `10_DESAIN_UI_LAPORAN_DEMO.md`. Tabel di bawah tetap berlaku sebagai daftar isi yang harus ada.

| # | Halaman | Isi | Fitur | Tag |
|---|---|---|---|---|
| P1 | **Unggah** | Area unggah 4 file, tombol "Muat data demo (SIMULASI)", hasil validasi input (peringatan/galat), tombol "Jalankan" | F1–F4, F11, F42 | `[MVP]` |
| P2 | **Ringkasan** | 4 kotak keputusan (jumlah klaim + jumlah taksa), tindak lanjut per kotak, info run (versi kamus, versi aturan, waktu proses), banner SIMULASI bila relevan, kalimat batas interpretasi | F22 | `[MVP]` |
| P3 | **Klaim** | Tabel: lokasi, ASV, nama lab, nama aman, tingkat, nilai, keputusan, label; filter per keputusan/label/lokasi; pencarian; klik baris → Evidence Card (drawer) | F9–F20, F23 | `[MVP]` |
| P4 | **Evidence Card** | Nama lab → nama aman; nilai + skor L1/L2/L4; penyebab; kecocokan dalam 0,5%; voucher pendukung; label L3; peluang belum di kamus; asal-usul; keputusan + tindak lanjut; batas interpretasi; alasan ID/EN | F23, F38, F21 | `[MVP]` |
| P5 | **Kamus & Celah** | Versi kamus, jumlah sekuens/spesies/level voucher; grafik cakupan per genus untuk `waterbody_id`; tabel genus (tercatat, punya referensi, peluang belum di kamus); daftar prioritas barcode | F7, F25, F40 | `[MVP]` |
| P6 | **Laporan** | Unduh PDF dan CSV; tampilkan jejak audit (SHA-256, versi) | F4, F24 | `[MVP]` |
| P7 | **Metode** | Penjelasan aturan dalam bahasa awam, versi aturan, tabel parameter, sitasi metode (Polanco 2025, dll.) | — | `[MVP]` |
| P8 | **Validasi** | Hasil uji leave-one-species-out dan dataset luar vs baseline BLAST-97% | F26, F27, F41 | `[MVP]` (boleh statis dari hasil pra-hitung) |
| P9 | Verifikasi laporan | Masukkan kode → tampilkan sidik jari | F28 | `[P1]` |

### Tindak lanjut baku per keputusan (dipakai di P2 dan PDF)

| Keputusan | Label UI | Tindak lanjut |
|---|---|---|
| `safe` | Aman dilaporkan | Boleh dimasukkan ke dokumen pada tingkat nama yang tertera |
| `with_note` | Dengan catatan | Tulis pada tingkat nama yang aman; sertakan catatan penyebab; cek kemungkinan sumber DNA lain |
| `must_verify` | Wajib verifikasi | Jangan dijadikan kesimpulan sebelum dicek: marker kedua (COI/16S), survei tangkap, atau barcode spesimen voucher |
| `do_not_use` | Jangan dipakai | Tinjau batch ekstraksi dan kontrol; ulang PCR; abaikan data nyasar |

---

## 8. Kebutuhan non-fungsional

| Aspek | Kebutuhan | Tag |
|---|---|---|
| Jejak audit | Setiap run menyimpan SHA-256 input, versi kamus, versi tabel acuan, versi aturan, parameter | `[MVP]` |
| Reproduksibilitas | Tanpa unsur acak; sortir stabil; sidik jari laporan identik untuk input dan versi yang sama | `[MVP]` |
| Keterjelasan | Setiap nilai punya alasan per lapisan dalam bahasa awam; tanpa model kotak hitam | `[MVP]` |
| Kinerja | 200 sampel × 2.000 ASV < 2 menit termasuk BLAST di laptop 4 core | `[MVP]` |
| Offline | Seluruh demo berjalan tanpa internet | `[MVP]` |
| Bahasa | UI dan PDF Bahasa Indonesia; alasan di kartu juga Bahasa Inggris; nama ilmiah miring | `[MVP]` |
| Batas interpretasi | Setiap kartu dan laporan memuat kalimat batas interpretasi | `[MVP]` |
| Kejujuran data demo | Label SIMULASI di file, baris, layar, dan PDF | `[MVP]` |
| Kerahasiaan | Data pengguna tidak dibagikan; tidak dikirim ke layanan luar | `[MVP]` |
| Lokasi spesies sensitif | Koordinat deteksi spesies terancam bisa disamarkan di laporan | `[P1]` |
| Lisensi | Lisensi setiap sumber referensi dicatat dan sitasinya dicantumkan di laporan | `[MVP]` |
| Keamanan | Batas ukuran unggah 200 MB; hanya ekstensi .csv, .tsv, .fasta, .fa, .fna | `[MVP]` |

---

## 9. Metrik keberhasilan

| Metrik | Target | Cara ukur | Kapan |
|---|---|---|---|
| Nama keliru yang lolos sebagai "aman" | Lebih rendah dari baseline BLAST-97% pada data yang sama | Uji leave-one-species-out | Setiap versi kamus/aturan |
| Spesies terhapus yang tidak diberi nama lain | ≥ 90% dilaporkan kompleks/genus/tidak dikenal | Uji leave-one-species-out + dataset luar | MVP |
| Presisi klaim A–B | ≥ 90% cocok dengan hasil tangkapan | Lake St. Pierre | `[P1]` |
| Klaim dengan alasan dan penyebab tertulis | 100% | Uji otomatis | MVP |
| Reproduksibilitas | Sidik jari identik | Uji otomatis | MVP |
| Waktu unggah sampai ringkasan | < 2 menit | Log aplikasi | MVP |
| Validasi masalah | ≥ 5 dari 8 perusahaan/konsultan menyatakan masalah nyata | Wawancara | Bulan 1–2 |
| Kesepakatan dengan ahli | ≥ 80% keputusan disetujui pada 50 klaim | Tinjauan buta | Bulan 7–9 |
| Kemauan membayar | ≥ 1 pilot berbayar atau LOI | Kontrak/LOI | Bulan 10–12 |

Catatan: target "di bawah 16%" dari v2 dihapus karena sama dengan hasil simulasi internal, sehingga bukan target.

---

## 10. Data demo untuk pitch `[MVP]`

| Komponen | Sumber | Label |
|---|---|---|
| Kamus Malili v0.1 | Sekuens publik GenBank (mis. Telmatherinidae KJ667771–KJ667865, setelah dicek overlap daerah MiFish) | Data publik |
| Checklist Malili | Herder dkk. 2006, Herder dkk. 2012, sumber lain di 04 | Data publik |
| Hasil eDNA "Danau Matano" 16 nama | Dibuat tim untuk demo | **SIMULASI** |
| Validasi | Lake St. Pierre (Dryad) dan/atau pustaka 12S Guyana | Data publik, mode validasi |

Bila sekuens publik belum terunduh saat demo, kamus v0.1 boleh berisi sekuens sintetis **berlabel SIMULASI** dan disebut demikian secara lisan.
