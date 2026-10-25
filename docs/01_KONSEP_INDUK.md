# 01 — Konsep Induk BioTrace Indonesia (Single Source of Truth)

| Atribut | Isi |
|---|---|
| Versi | 1.0 |
| Tanggal | 24 Oktober 2026 |
| Status | Berlaku. Mengikat semua anggota tim dan AI agent |
| Menggantikan | Arah produk di PRD BioTrace Indonesia v2 dan Pitch Deck v2, sejauh bertentangan |
| Konteks | GENOHACK 2026, Track 2: Genomics for Food Security & Biodiversity |
| Dasar | PRD v2, Pitch Deck v2, tiga sesi mentoring, riset web dan literatur 24 Oktober 2026, laporan deep research "deep research final" (Project GENOHACK) |
| Perubahan | Hanya lewat entri baru di `09_LOG_KEPUTUSAN.md` yang disetujui Ketua |

---

## 1. Satu kalimat

**BioTrace Indonesia membangun kamus DNA ikan air tawar tropis Indonesia yang tervalidasi, lalu memakainya untuk memeriksa setiap nama ikan dalam laporan eDNA sebelum laporan itu dipakai perusahaan untuk perizinan dan pemantauan lingkungan.** Bila datanya tidak cukup, BioTrace menurunkan nama ke tingkat yang aman atau menyatakan "tidak dikenal", bukan menebak.

**Tagline:** *Biodiversitas Indonesia, dibaca dengan data Indonesia.*

**Hook untuk orang awam:** *eDNA juga bisa berhalusinasi, seperti AI. BioTrace adalah pemeriksa faktanya.*

---

## 2. Masalah

### 2.1 Untuk orang awam

Perusahaan yang membangun tambang, PLTA, atau perkebunan di dekat sungai dan danau wajib menjelaskan ikan apa saja yang hidup di sana. Cara modern adalah eDNA: ambil air, baca jejak DNA ikan di dalamnya, lalu cocokkan dengan "kamus DNA".

Masalahnya, kamus DNA untuk ikan Indonesia masih sangat bolong. Saat jawaban yang benar tidak ada di kamus, mesin tetap memberi nama ikan lain yang paling mirip, dengan yakin. Sama seperti AI yang berhalusinasi. Nama keliru itu masuk ke dokumen lingkungan perusahaan tanpa peringatan apa pun.

Akibatnya:
- ikan endemik bisa dinyatakan tidak ada, padahal masih ada;
- ikan invasif bisa terlewat atau memicu alarm palsu;
- dokumen perusahaan bisa dipersoalkan reviewer, auditor, atau pemberi pinjaman.

### 2.2 Untuk ilmuwan

Penetapan nama spesies dari metabarcoding 12S hanya seandal database referensinya. Untuk ikan air tawar Indonesia, celahnya berlapis:
1. spesies tanpa sekuens sama sekali;
2. spesies yang hanya punya COI tetapi tidak punya 12S, sehingga tidak berguna untuk data MiFish;
3. spesies yang punya 12S tetapi tanpa voucher atau berlabel salah.

Pada kelompok yang berevolusi cepat di satu danau, seperti *Telmatherina* dan *Oryzias* di Danau Malili, sudah dilaporkan introgresi mitokondria. Akibatnya marker 12S yang pendek kemungkinan tidak bisa membedakan spesies di dalamnya. Pencocokan dengan ambang ≥97% bisa menghasilkan nama yang meyakinkan tetapi salah.

### 2.3 Bukti utama (hanya yang terverifikasi; rincian di `07_REGISTRI_BUKTI_RINGKAS.md`)

| Bukti | Angka | Sumber | Jenis |
|---|---|---|---|
| Kekayaan ikan air tawar asli Indonesia | 1.172 spesies | Hubert dkk. 2015 | Peer-reviewed |
| Cakupan pustaka barcode ikan Jawa | 36% spesies Jawa (marker COI) | Dahruddin dkk. 2017 | Peer-reviewed |
| Studi eDNA air tawar Indonesia | 28 studi; 86% di Jawa dan Sumatra Barat; MiFish-U hanya 14% | Dwipayana dkk. 2026, BIOTROPIA | Review |
| Penyedia eDNA komersial di sungai tropis | False negative 32–92%; false positive 20–59% | Roussel dkk. 2026 | **Preprint** |
| Label referensi salah mengubah kesimpulan | 2 dari 5 "bukti invasi" di Terusan Panama salah identifikasi | Koreksi Schreiber dkk. 2023 | Koreksi jurnal |
| AI tidak menutup celah | Model zero-shot terbaik ≈24% benar untuk spesies yang tidak ada di referensi | Stalder dkk. 2025, PLOS Comp Biol | Peer-reviewed |
| Kamus lokal bisa dibangun | Guyana Prancis: 1.557 sekuens 12S, 369 spesies (88,92%) dari >25 ekspedisi | Scientific Data 2026 | Peer-reviewed |

---

## 3. Posisi produk

BioTrace punya tiga lapis yang saling memperkuat. Urutan pentingnya adalah aset dulu, baru produk.

| Lapis | Isi | Peran |
|---|---|---|
| **1. Kamus referensi (aset inti)** | Sekuens DNA ikan air tawar tropis tervalidasi, level voucher, checklist perairan, status endemik/invasif, tabel alias hibrida, flag kompleks, peta kelengkapan | Sulit ditiru, butuh spesimen fisik dan ahli lokal |
| **2. Mesin cek** | Penamaan ulang ke kamus, tingkat nama yang aman (spesies, kompleks, genus, tidak dikenal), nilai bukti A–D, penyebab ketidakpastian, empat keputusan, jejak audit | Produk yang dipakai pengguna |
| **3. Program pengisian celah** | Setiap "tidak dikenal" dan celah kamus menjadi daftar prioritas barcode bersama kolaborator | Flywheel: laporan → celah → hibah → kamus lebih lengkap |

**Yang BUKAN keunggulan kita:** rumus skor. Metode serupa sudah terbit (Polanco dkk. 2025, skor 0–5; PhyloRef 2026). Kita memakai dan menyitasi metode publik itu, bukan mengklaim menemukannya.

**Yang menjadi keunggulan kita:**
1. **Data fisik**: sekuens dari spesimen ikan Indonesia bervoucher. AI tidak bisa membuatnya.
2. **Pengetahuan lokal**: checklist per danau, alias louhan hibrida, kompleks spesies danau purba.
3. **Akuntabilitas**: setiap nama tertaut ke voucher, versi kamus, versi aturan, dan sidik jari file.
4. **Efek jaringan data**: setiap laporan memperlihatkan celah berikutnya.

---

## 4. Pengguna, pembeli, dan pihak lain

**Keputusan D-003:** pengguna dan pembeli utama adalah **perusahaan korporat yang membutuhkan dokumen pendukung untuk perizinan dan pemantauan lingkungan (AMDAL, RKL-RPL)**, beserta konsultan lingkungan yang menyusun dokumennya.

| Peran | Siapa | Kebutuhan | Yang dipakai |
|---|---|---|---|
| **Pembeli (economic buyer)** | Perusahaan tambang, PLTA, perkebunan, infrastruktur di dekat perairan | Dokumen lingkungan yang tidak dipersoalkan, tidak ada klaim endemik keliru | Laporan verifikasi PDF, ringkasan keputusan |
| **Champion** | Manajer lingkungan/HSE/biodiversitas perusahaan | Bukti yang bisa dipertanggungjawabkan ke direksi, auditor, bank | Ringkasan keputusan, peta celah |
| **Pengguna operator** | Konsultan lingkungan / tim penyusun AMDAL | Memeriksa data eDNA sebelum dimasukkan ke dokumen | Unggah data, tabel klaim, Evidence Card |
| **Kanal & pengunggah** | Lab jasa eDNA | Hasil yang lolos audit; pembeda layanan | Unggah data, lisensi lab `[P1]` |
| **Pemegang veto** | Penilai dokumen lingkungan, auditor (mis. IRMA/ERM CVS), pemberi pinjaman | Menelusuri asal setiap klaim | Jejak audit, kode verifikasi `[P1]` |
| **Kolaborator data** | Kampus (UNHAS, USU, IPB, UGM, ITB), BRIN/MZB, museum | Referensi lebih lengkap | Peta celah, daftar prioritas barcode |
| **Pendana** | Pemberi hibah konservasi, program kredit biodiversitas | Dana tepat sasaran | Peta celah, program pengisian celah |

**Batas penting (aturan A10):** BioTrace **tidak** menerbitkan dokumen AMDAL resmi. Dokumen AMDAL disusun penyusun yang berwenang. BioTrace menghasilkan **laporan verifikasi pendukung** untuk bagian data biodiversitas perairan (rona awal dan pemantauan), yang dilampirkan perusahaan atau konsultannya.

**Belum terverifikasi:** apakah regulasi AMDAL/RKL-RPL menerima atau mewajibkan data eDNA. Ini masuk daftar pencarian manual (item M05 di `07_REGISTRI_BUKTI.md` lengkap, Project GENOHACK). Sampai terverifikasi, jangan klaim bahwa BioTrace "memenuhi persyaratan AMDAL".

### Persona utama

**Manajer lingkungan perusahaan tambang di sekitar Danau Matano.** Menyiapkan data biodiversitas untuk dokumen lingkungan dan laporan pemantauan. Menerima daftar 16 spesies dari lab, tetapi tidak bisa menilai mana yang rapuh. Takut dokumennya dipersoalkan penilai atau auditor, dan takut ikan endemik terlewat. **Berhasil bila** dalam satu halaman tahu klaim mana aman dimasukkan ke dokumen, mana yang harus dicek, dan apa langkah ceknya.

**Konsultan penyusun dokumen lingkungan.** Mengolah hasil eDNA dari lab untuk beberapa klien. Tidak punya waktu dan referensi untuk memeriksa nama satu per satu. **Berhasil bila** mendapat daftar klaim berisiko beserta alasan tertulis dalam waktu di bawah 2 menit per proyek.

---

## 5. Batas produk

- BioTrace bekerja **setelah lab selesai**: tidak mengambil sampel, tidak mengekstraksi DNA, tidak menyekuensing.
- MVP tidak mengolah FASTQ. Jalur FASTQ masuk roadmap lewat pipeline terbuka yang sudah ada.
- Barcode 12S mengenali spesies, **bukan populasi**. BioTrace tidak melacak asal populasi.
- BioTrace tidak memperkirakan kelimpahan dari jumlah bacaan.
- Deteksi eDNA **bukan bukti pasti** ikan hidup di lokasi.
- **Tim tidak memegang atau mengekspor spesimen ikan.** Pengambilan spesimen hanya lewat mitra berizin.

---

## 6. Keputusan yang mengikat (ringkasan; detail di 09)

| ID | Keputusan |
|---|---|
| D-001 | Identitas: kamus DNA ikan air tawar tropis Indonesia + pemeriksa fakta eDNA yang bisa diaudit |
| D-002 | Aset inti adalah kamus referensi, bukan rumus skor. Metode publik (Polanco 2025, PhyloRef 2026) dipakai dan disitasi |
| D-003 | Pengguna/pembeli utama: perusahaan korporat yang butuh dokumen pendukung perizinan dan pemantauan lingkungan (AMDAL, RKL-RPL), beserta konsultannya. Lab = kanal |
| D-004 | Beachhead: kompleks Danau Malili / Sorowako, didekati sebagai kolaborasi riset |
| D-005 | Kebijakan klaim: hanya angka terverifikasi (§8) |
| D-006 | Batas legal: tim tidak memegang/mengekspor spesimen; hanya mengolah data sekuens |
| D-007 | Model bisnis bertahap: kolaborasi riset → verifikasi berbayar → lisensi kamus + hibah pengisian celah |
| D-008 | Cari penasihat ahli taksonomi ikan sebelum klaim tingkat spesies dipakai di luar demo |
| D-009 | Stack: Python `biotrace_core` + BLAST+ + FastAPI + React/Vite/TS + penyimpanan berbasis file |
| D-010 | Penyimpanan dokumen: repo `docs/` untuk 01–06 dan 09; Project GENOHACK untuk 07 lengkap dan 08 |
| D-011 | Kamus dibangun bertahap; modul luar per wilayah hanya untuk validasi. D-033/D-038: sekuens spesimen luar/asal kosong dari spesies tercatat Indonesia boleh masuk modul ID dengan label; bukti yang hanya bertumpu padanya tidak pernah `safe` |
| D-012 | "Kompleks" adalah tingkat nama yang sah dan dianggap jawaban benar |
| D-013 | Level voucher V1–V4; V4 (eDNA) tidak pernah menjadi referensi |
| D-014 | Tanpa machine learning di MVP |
| D-015 | Penilaian deterministik dengan jejak audit |
| D-016 | Data demo sintetis wajib berlabel SIMULASI |
| D-017 | Marker utama 12S MiFish-U; 16S dan COI opsional |

---

## 7. Peta tahapan

| Tahap | Waktu | Isi | Tag |
|---|---|---|---|
| **Prototipe hackathon** | s.d. 25 Okt 2026, 10:00 WIB | Mesin cek + dashboard + snapshot kamus v0.5 (checklist Malili dan nasional) + demo SIMULASI dan alur eDNA asli terumbu Indonesia + uji mesin dan LOSO pustaka berversi (D-038) | `[MVP]` |
| Validasi masalah | Bulan 1–2 | Wawancara 5–8 perusahaan/konsultan lingkungan. Gerbang 1: ≥5 menyatakan masalah nyata | `[P1]` |
| Paper 1 + snapshot kurasi berikutnya | Bulan 1–4 | Analisis celah 12S ikan air tawar Indonesia per pulau/famili/genus; bukan klaim snapshot awal sudah lengkap | `[P1]` |
| Validasi mesin | Bulan 3–4 | Uji presisi di Lake St. Pierre (LOSO Guyana sudah masuk MVP, K-009) | `[P1]` |
| Tinjauan ahli | Bulan 7–9 | 50 klaim diperiksa ahli ikan. Gerbang 2: ≥80% disetujui | `[P1]` |
| Pilot | Bulan 10–12 | Analisis ulang data proyek nyata bersama mitra; ≥1 pilot berbayar atau LOI | `[P1]` |
| Kamus v1.0 | Tahun 2 | Sekuens baru dari spesimen bervoucher lewat mitra berizin | `[P2]` |
| Ekspansi | Tahun 2+ | Danau lain di Indonesia, lalu Asia Tenggara (Mekong) | `[P2]` |

---

## 8. Kebijakan klaim (wajib untuk pitch, UI, paper, dan dokumen)

### 8.1 Boleh dipakai
Angka di tabel §2.3 dan di `07_REGISTRI_BUKTI_RINGKAS.md` §2 dengan status **Terverifikasi**, selalu dengan sumbernya. Roussel 2026 wajib disebut sebagai preprint.

### 8.2 Ditunda (jangan dipakai sampai dicek)
- "Sekitar 630 spesies endemik": tidak dipakai (K-002). Pakai "1.172 spesies ikan air tawar asli" (Hubert 2015).
- "4 → 34 spesies yang disepakati semua penyedia" (Roussel 2026): sumber berbeda pendapat; perlu dicek di teks penuh.
- Angka pasar eDNA Indonesia: belum ada data. Jangan ditampilkan sebelum ada ≥5 wawancara harga.
- Kewajiban eDNA dalam AMDAL/RKL-RPL/PROPER: belum terverifikasi.

### 8.3 Wajib dengan label
- Simulasi tim (41% spesies tersembunyi tetap diberi nama lain pada ≥97%; ambang 97% meloloskan 52% nama keliru vs aturan 16%) **wajib** disebut "simulasi internal tim, kamus ikan laut, belum terbit".
- Pasar eDNA global: USD 1,51 miliar (2026) → 3,04 miliar (2031), CAGR 14,9% (MarketsandMarkets). Hanya sebagai batas atas. Jangan pakai versi "5,61 miliar / 10,2%" karena tidak konsisten secara matematis.

### 8.4 Dilarang
- Menyebut nama mitra, pelanggan, atau pendukung yang belum setuju secara tertulis (PT Vale, UNHAS, BRIN, dll. **belum** menjadi mitra).
- Menyebut BioTrace "memenuhi persyaratan AMDAL" atau "dokumen resmi".
- Menyatakan nilai A sebagai kepastian.

---

## 9. Risiko utama (detail di 08)

1. Tim tanpa ahli taksonomi ikan.
2. Marker MiFish tidak bisa membedakan kelompok *Telmatherina*/*Oryzias* di Malili. Mitigasi: "kompleks" dijadikan fitur.
3. Data eDNA Malili belum tersedia di repo. Mitigasi: konfirmasi sumber/penulis; gunakan dataset luar untuk validasi pustaka dan data terumbu Indonesia untuk demo alur, tanpa mengklaim validasi lapangan Malili.
4. Izin akses sumber daya genetik. Mitigasi: tidak memegang spesimen.
5. Belum ada kewajiban regulasi. Mitigasi: masuk lewat kolaborasi riset.
6. Kamus Malili sangat bolong, sehingga banyak hasil berupa genus atau "tidak dikenal". Mitigasi: tampilkan sebagai peta celah yang bisa ditindaklanjuti, bukan kegagalan.

Pembaruan implementasi D-038 (25 Oktober 2026, atas instruksi Agathan): snapshot aktif v0.5 dan persetujuan usulan bukan pengesahan ahli. Isi snapshot, asumsi dataset, status validasi, dan solusi untuk bahan belum selesai dirinci di [17 — Kesiapan Juri](17_KESIAPAN_JURI.md). Semua ambang tetap usulan tim, belum dikalibrasi ahli; endemik Malili berreferensi tetap 0/19 pada snapshot ini.

---

## 10. Pengakuan kerja hackathon

Sesuai aturan GENOHACK, tim wajib memisahkan yang sudah ada sebelum hackathon dan yang dibuat selama hackathon. README repo wajib punya bagian "Sebelum vs selama hackathon". Yang diketahui ada sebelum kode MVP: PRD v1/v2, simulasi kamus ikan laut (`simulasi_kamus.py`), analisis ulang data Nanopore UNDIP, dan Pitch Deck v2. Isi bagian ini harus diisi manusia, bukan agent.

---

## 11. Glosarium (istilah baku)

| Istilah | Arti sederhana | Kode/enum |
|---|---|---|
| eDNA | DNA yang dilepas makhluk hidup ke air (lendir, sisik, kotoran) | — |
| Metabarcoding | Membaca DNA banyak spesies sekaligus dengan satu potongan gen | — |
| Marker 12S / MiFish-U | Potongan gen mitokondria (~170 basa) untuk mengenali ikan; MiFish-U adalah primernya | `12S_MiFish_U` |
| COI / 16S | Marker lain. COI adalah standar barcode hewan | `COI`, `16S` |
| ASV | Satu varian urutan DNA unik dalam hasil lab | `asv_id` |
| FASTA / FASTQ | File urutan DNA / file mentah mesin sekuensing beserta mutunya | — |
| Kamus referensi | Kumpulan sekuens dari ikan yang sudah diidentifikasi ahli | `reference` |
| Voucher | Spesimen ikan fisik di museum dengan nomor katalog | `voucher_level` V1–V4 |
| Checklist perairan | Daftar ikan yang pernah tercatat di suatu danau/sungai | `checklist` |
| Endemik | Hanya hidup di wilayah tertentu | `endemic` |
| Invasif / introduksi | Ikan asing yang masuk dan merugikan / ikan yang didatangkan manusia | `invasive`, `introduced` |
| Louhan / flowerhorn | Cichlid hibrida buatan, invasif di Danau Matano | alias `louhan_hybrid` |
| Kompleks | Kelompok spesies kerabat yang tidak bisa dibedakan dengan marker ini | `complex` |
| LCA | Tingkat takson terendah yang benar untuk semua kecocokan (mis. genus) | — |
| Klaim | Satu pasangan ASV × lokasi yang akan diberi nama | `claim_id` |
| Tingkat nama aman | Spesies, kompleks, genus, famili, ordo, atau tidak dikenal | `reported_rank` |
| Nilai bukti | A, B, C, D | `grade` |
| Penyebab ketidakpastian | Referensi, marker, sampel, lokasi | `reference`, `marker`, `sample`, `location` |
| Keputusan | Aman dilaporkan, dengan catatan, wajib verifikasi, jangan dipakai | `safe`, `with_note`, `must_verify`, `do_not_use` |
| Peta celah / kelengkapan | Per genus per wilayah: berapa spesies tercatat vs punya referensi | `coverage` |
| Daftar prioritas barcode | Daftar ikan yang perlu disekuens berikutnya | `barcode_priority` |
| Kontrol negatif | Sampel air bersih yang seharusnya tanpa DNA ikan | `negative_control` |
| Replikat | Ulangan sampel dari lokasi yang sama | `replicate` |
| Data nyasar (tag-jumping) | Sebagian kecil bacaan yang pindah ke sampel lain saat dibaca bersamaan | `tag_jump` |
| Jejak audit | Sidik jari file (SHA-256), versi kamus, versi aturan | `audit` |
| AMDAL / RKL-RPL | Dokumen kajian dampak lingkungan / rencana pengelolaan dan pemantauan lingkungan | — |
| Rona awal | Kondisi lingkungan sebelum proyek, bagian dari dokumen AMDAL | — |
