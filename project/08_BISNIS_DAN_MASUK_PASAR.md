# 08 — Bisnis, Masuk Pasar, dan Narasi

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Lokasi | Project GENOHACK (bukan repo produk) |
| Tunduk pada | `01_KONSEP_INDUK.md` (D-003, D-004, D-005, D-007), `09_LOG_KEPUTUSAN.md` |
| Sumber angka | `07_REGISTRI_BUKTI.md`. Angka tanpa status Terverifikasi ditandai **hipotesis** |

---

## 1. Ringkasan

BioTrace menjual **kepastian yang bisa dipertanggungjawabkan** atas nama-nama ikan dalam data eDNA, kepada perusahaan yang memakai data itu untuk dokumen perizinan dan pemantauan lingkungan. Pembelinya adalah pihak yang menanggung risiko bila nama salah, bukan pihak yang membuat daftar nama. Aset jangka panjangnya adalah kamus DNA ikan air tawar tropis Indonesia yang tumbuh dari setiap laporan.

## 2. Masalah dari sisi pembeli

**Situasi.** Perusahaan tambang, PLTA, perkebunan, dan infrastruktur di dekat sungai dan danau harus menjelaskan kondisi biodiversitas perairan untuk dokumen lingkungan (rona awal AMDAL, laporan pemantauan RKL-RPL), dan semakin sering juga untuk auditor, standar industri (mis. IRMA), dan pemberi pinjaman. eDNA makin dipakai karena lebih murah dan tidak perlu menangkap ikan.

**Rasa sakit.**
1. Daftar spesies dari lab tidak memberi tahu nama mana yang rapuh. Studi 2026 (preprint) di sungai tropis menemukan 20–59% nama dari penyedia komersial tidak ada di lokasi (C04).
2. Kesalahan pada ikan endemik atau invasif mahal: dokumen dipersoalkan, rekomendasi pengelolaan keliru, reputasi rusak.
3. Tidak ada jejak audit yang menjelaskan asal sebuah nama.

**Yang belum terverifikasi (wajib dicek, M05):** apakah aturan AMDAL/RKL-RPL di Indonesia menerima atau mewajibkan data eDNA, dan bagian dokumen mana yang memakainya. Sampai itu terverifikasi, pitch memakai bahasa "data biodiversitas untuk dokumen lingkungan dan audit", bukan "syarat AMDAL".

## 3. Unit pengambil keputusan (DMU)

| Peran | Siapa | Apa yang mereka pedulikan | Pesan untuk mereka |
|---|---|---|---|
| Pengguna (operator) | Konsultan penyusun dokumen lingkungan; analis lab | Cepat, tidak salah, mudah dijelaskan ke klien | "Daftar klaim berisiko beserta alasan tertulis dalam < 2 menit." |
| Champion | Manajer lingkungan / HSE / biodiversitas perusahaan | Dokumen tidak dipersoalkan; ikan endemik tidak terlewat | "Satu halaman: mana yang aman masuk dokumen, mana yang harus dicek." |
| Pembeli (economic buyer) | Kepala departemen lingkungan / direksi operasi | Biaya kecil dibanding risiko | "Biaya verifikasi kecil dibanding biaya dokumen yang dipersoalkan." |
| Pemegang veto | Penilai dokumen, auditor (mis. IRMA/ERM CVS), pemberi pinjaman | Bisa ditelusuri | "Setiap nama tertaut ke voucher, versi kamus, dan sidik jari file." |
| Kanal | Lab jasa eDNA | Pembeda layanan, tidak tergeser | "BioTrace adalah QA untuk hasil Anda, bukan pesaing." |
| Kolaborator | Kampus, BRIN/MZB, museum | Publikasi, data lebih lengkap | "Peta celah dan daftar prioritas barcode untuk riset Anda." |
| Pendana | Program kredit biodiversitas, hibah konservasi | Integritas ilmiah | "Data dengan tingkat galat terdokumentasi." (C19) |

## 4. Kenapa sekarang

| Sinyal | Bukti | Status |
|---|---|---|
| Danau Matano mulai dipantau dengan eDNA | Survei 14 titik, Juni 2026 (C14) | Terverifikasi |
| Tambang Sorowako diaudit standar internasional | IRMA on-site Des 2025 (C15) | Terverifikasi |
| Indonesia menyiapkan kredit biodiversitas berprinsip integritas ilmiah | Draf Permen LH Sep 2026 (C17) | Terverifikasi (isi draf belum publik) |
| Pelaporan alam global tumbuh | 836 organisasi TNFD, ISO LEAP (C18) | Terverifikasi |
| Pasar kredit meminta tingkat galat terdokumentasi | BCA Feb 2026 (C19) | Terverifikasi |
| **Belum wajib** | KPI pinjaman PT Vale masih karbon dan energi (C16) | Terverifikasi — jujur di pitch |

## 5. Persaingan dan alternatif

| Alternatif | Menilai keandalan tiap nama? | Data dan konteks Indonesia? | Bisa diaudit, untuk non-ahli? |
|---|---|---|---|
| Tidak melakukan apa-apa (pakai daftar lab apa adanya) | Tidak | Tidak | Tidak |
| Penyedia eDNA internasional (NatureMetrics, dll.) | Jarang; "usually with little information about the reliability" (Roussel 2026) | Kamus global/privat | Laporan spesies |
| Pipeline terbuka (QIIME2, DADA2, MiFish pipeline) | Ambang identitas saja | Bergantung kamus | Tidak |
| Metode riset (Polanco 2025, GAPeDNA, PhyloRef) | Ya / peta celah / kurasi | Global, ikan laut | Metode riset, bukan layanan |
| Cek manual oleh ahli | Ya | Ya | Ya, tetapi lambat, mahal, langka |
| **BioTrace** | **Ya, per nama, dengan penyebab** | **Ya, kamus Indonesia + checklist + kompleks lokal** | **Ya, < 2 menit, jejak audit** |

**Matriks 2×2 untuk slide:** sumbu X = "Konteks dan data lokal Indonesia" (rendah → tinggi); sumbu Y = "Akuntabilitas per nama" (daftar spesies → keputusan yang bisa diaudit). BioTrace di kanan atas; cek manual ahli di kanan atas tetapi lambat (ukuran titik kecil); penyedia internasional di kiri bawah; metode riset di kiri atas.

**Pesaing yang mungkin muncul:** penyedia besar menambah fitur skor keyakinan. Pertahanan kita bukan fitur, tetapi kamus lokal bervoucher, jaringan ahli lokal, dan data dari setiap laporan.

## 6. Keunggulan di era AI

| Yang mudah ditiru | Yang sulit ditiru |
|---|---|
| Rumus skor (sudah publik) | Sekuens dari spesimen ikan Indonesia bervoucher (C09: Guyana butuh >25 ekspedisi) |
| Pipeline BLAST | Checklist danau, alias louhan, kompleks spesies danau purba |
| Dashboard | Akuntabilitas: nama tertaut ke voucher, versi, dan penanggung jawab |
| Model AI | AI paling lemah tepat di sini: ≈24% untuk spesies tanpa referensi (C08) |

Kalimat inti: **"AI bisa memberi jawaban. Ia tidak bisa menangkap ikan, dan tidak bisa bertanggung jawab di depan auditor."**

## 7. Model bisnis

Semua harga adalah **hipotesis** dari PRD v2 dan saran mentor; diuji di wawancara dan pilot.

| Lini | Pembeli | Bentuk harga (hipotesis) | Mulai |
|---|---|---|---|
| Verifikasi per proyek | Perusahaan, lewat konsultan atau lab | Rp250–400 rb per sampel; proyek tipikal 60 sampel ≈ Rp15–24 juta | Pilot bulan 10–12 |
| Lisensi lab | Lab jasa eDNA | Rp20–30 juta per tahun | Tahun 2 |
| Program pengisian celah | Pendana hibah, program kredit biodiversitas | Per program (perlu skema hibah nyata) | Tahun 2+ |
| Akses akademik | Kampus, BRIN | Gratis, ditukar kontribusi data dan validasi | Sejak MVP |

**Biaya per laporan (hipotesis PRD v2):** komputasi Rp10–50 rb; tinjauan ahli ±3 jam (±Rp750 rb); dukungan ±Rp500 rb; total ±Rp1,3 juta per proyek 60 sampel. Margin kotor hipotesis ±90% pada harga Rp18 juta.

**Patokan harga tes eDNA internasional:** USD 95–430 per sampel (PRD v2, mengutip Jonah Ventures, Wilderlab, NatureMetrics). **Belum diverifikasi ulang di sesi ini**; cek sebelum dipakai di slide.

## 8. Ukuran pasar

**Top-down (batas atas):** pasar eDNA global USD 1,51 miliar (2026) → 3,04 miliar (2031), CAGR 14,9% (C22). Segmen software/verifikasi hanya irisan kecil.

**Bottom-up Indonesia (kerangka, belum diisi):**

```
Pendapatan verifikasi/tahun = (jumlah proyek dokumen lingkungan di dekat perairan yang memakai eDNA per tahun)
                              × (sampel per proyek) × (harga per sampel)
```

Data yang dibutuhkan: jumlah dokumen lingkungan per sektor per tahun (M05), porsi yang memakai eDNA (wawancara), sampel per proyek (wawancara/konsultan), harga (M10). **Angka SAM/SOM di Pitch Deck v2 tidak dipakai** sampai ada ≥5 wawancara (X04).

**Jalur pertumbuhan:** Malili → danau prioritas nasional lain → DAS dengan proyek industri → Asia Tenggara (Mekong) → taksa lain.

## 9. Masuk pasar

**Beachhead:** kompleks Danau Malili / Sorowako. Alasan: tingkat endemik tinggi, ikan invasif sudah ada (C13), aktivitas tambang dengan audit internasional (C15), dan eDNA sudah dipakai (C14).

**Pendekatan:** kolaborasi riset dulu, bukan penjualan. Tawaran pertama: **analisis ulang gratis** atas data eDNA yang sudah ada, dengan NDA, lalu laporan peta celah untuk danau itu.

**Alur pembelian:**
1. Kenal lewat publikasi, forum, atau kampus mitra.
2. Analisis ulang gratis satu proyek lama.
3. Pilot berbayar pada proyek baru.
4. Masuk templat laporan rutin perusahaan/konsultan.

**Tempat bertemu (dari PRD v2):** sosialisasi PROPER KLH, Pertemuan Ilmiah Masyarakat Limnologi Indonesia, forum LSM konservasi, forum pengelolaan Danau Matano (FGD BBKSDA, Sep 2026; tautan di 07 §7).

**10 target pertama (belum dihubungi):**

| # | Organisasi | Peran |
|---|---|---|
| 1 | Tim biodiversitas PT Vale Indonesia | Champion potensial |
| 2 | LPPM Universitas Hasanuddin | Kolaborator; terlibat survei Matano |
| 3 | LPPM / PUI Mangrove Universitas Sumatera Utara | Kolaborator; mitra ANEMONE |
| 4 | Tohoku University / ANEMONE Global | Pemegang data Matano |
| 5 | BBKSDA Sulawesi Selatan | Pengelola kawasan |
| 6 | ERM CVS | Auditor |
| 7 | IRMA (bagian assurance) | Standar |
| 8 | BRIN (restorasi ekosistem perairan; koleksi MZB) | Kolaborator data dan voucher |
| 9 | Deputi terkait KLH/BPLH | Regulator kredit biodiversitas |
| 10 | Tim Universitas Udayana (penulis review 2026) | Mitra paper |

Kontak orang diambil dari laporan deep research; **verifikasi sebelum menghubungi**. Jangan menyebut target ini sebagai mitra di pitch.

## 10. Roadmap 12 bulan dan gerbang

| Bulan | Kegiatan | Gerbang |
|---|---|---|
| 0 (hackathon) | Prototipe MVP, kamus Malili v0.1, demo SIMULASI | — |
| 1–2 | Wawancara 5–8 perusahaan/konsultan/lab; verifikasi M05 (AMDAL) dan M10 (harga); unduh dataset prioritas 1–4 | **Gerbang 1:** ≥5 menyatakan masalah nyata |
| 1–4 | Paper 1: analisis celah 12S Indonesia; uji LOSO pada pustaka Guyana | GO bila pipeline cakupan mereproduksi angka Guyana (≈88,9%) |
| 3–4 | Uji Lake St. Pierre | GO bila nama keliru lolos aman < baseline BLAST-97% |
| 5–6 | Minta data Balantak, Kurniawan, Matano | NO-GO jalur data Indonesia bila 0 dataset; fokus ke kamus |
| 7–9 | Tinjauan buta 50 klaim oleh ahli; analisis ulang Matano bila ada NDA | **Gerbang 2:** ≥80% keputusan disetujui ahli |
| 10–12 | Pilot berbayar; proposal hibah pengisian celah; submit paper | GO venture bila ≥1 LOI/pilot berbayar |

## 11. Permintaan (ask) untuk pitch

Struktur sesuai panduan GENOHACK §10. Angka diisi Ketua; **jangan mengarang angka**.

| Jenis | Isi |
|---|---|
| Dana | [diisi Ketua], dibagi per milestone: kurasi kamus dan Paper 1; validasi (akses data, honor ahli peninjau); pilot |
| Non-dana | Perkenalan ke ahli iktiologi (penasihat), akses data eDNA air tawar Indonesia untuk validasi, perkenalan ke perusahaan/konsultan yang menyusun dokumen lingkungan |

## 12. Risiko

| # | Risiko | Dampak | Mitigasi |
|---|---|---|---|
| 1 | Tim tanpa ahli taksonomi | Klaim spesies tidak dipercaya | Penasihat dari kampus/BRIN sebelum klaim spesies di luar demo |
| 2 | MiFish tidak bisa membedakan kelompok Malili | Banyak hasil "kompleks" | Jadikan fitur; uji in silico (T-DATA-02) |
| 3 | Data eDNA Indonesia tidak publik | Sulit validasi lokal | Kontak penulis; validasi dulu dengan data luar |
| 4 | Izin sumber daya genetik | Masalah hukum | Tidak memegang spesimen; lewat mitra berizin |
| 5 | Data Matano milik pihak lain | Tidak bisa dipakai | Tawarkan analisis ulang dengan NDA |
| 6 | Regulasi belum mewajibkan | Adopsi lambat | Masuk lewat riset dan audit sukarela; jangan bergantung satu peraturan |
| 7 | Lab merasa terancam | Kanal tertutup | Posisikan sebagai QA untuk lab |
| 8 | Pemain besar menambah fitur skor | Diferensiasi melemah | Moat = kamus lokal bervoucher |
| 9 | Mesin salah | Kepercayaan hilang | Validasi publik, versi aturan, tinjauan ahli |
| 10 | Klaim berlebihan di pitch | Kredibilitas, diskualifikasi | Kebijakan klaim 01 §8 |

## 13. Narasi pitch

### 13.1 Dua audiens

**Untuk ahli biologi.** Nama spesies dari metabarcoding 12S hanya seandal database referensinya. Di Indonesia, sebagian besar spesies hanya punya COI atau tidak punya sekuens sama sekali, sementara kelompok di Danau Malili seperti *Telmatherina* dan *Oryzias* mengalami introgresi mitokondria. Akibatnya kecocokan ≥97% bisa menghasilkan nama yang meyakinkan tetapi salah. BioTrace mengukur celah per genus, menolak nama spesies bila ada kerabat lokal yang belum berreferensi, melaporkan "kompleks" bila marker tidak bisa membedakan, dan menautkan setiap nama ke voucher serta versi kamus.

**Untuk juri bisnis.** eDNA bisa berhalusinasi seperti AI: kalau jawaban yang benar tidak ada di kamusnya, mesin tetap memberi nama yang paling mirip, dengan yakin. Di Terusan Panama, dua dari lima "bukti invasi" ternyata salah nama. Di sungai tropis, sebuah studi 2026 menemukan hingga lebih dari separuh nama dari penyedia komersial tidak ada di lokasi. Perusahaan memakai nama-nama ini untuk dokumen lingkungan mereka. BioTrace adalah pemeriksa faktanya: nama mana yang aman, mana yang harus dicek, dan mana yang harus ditulis "tidak dikenal", dengan bukti yang bisa diaudit.

### 13.2 Tiga hal untuk diingat (rule of three)

1. Nama ikan dari eDNA bisa keliru tanpa ada yang tahu, dan Indonesia punya celah kamus terbesar justru di ikan endemiknya.
2. BioTrace memeriksa setiap nama dengan kamus Indonesia dan berani bilang "tidak tahu", dengan jejak audit.
3. Aset kami adalah kamus DNA ikan tropis Indonesia yang tumbuh dari setiap laporan, sesuatu yang tidak bisa dibuat AI.

### 13.3 Alur slide yang disarankan (9–10 slide, 6 menit termasuk demo)

| # | Slide | Isi utama | Bukti |
|---|---|---|---|
| 1 | Judul + hook | "eDNA juga bisa berhalusinasi" | — |
| 2 | Cerita persona | Manajer lingkungan tambang di Matano menerima 16 nama ikan | Data demo SIMULASI |
| 3 | Masalah | Nama keliru, contoh Panama, Roussel (preprint) | C04, C06 |
| 4 | Kenapa data, bukan algoritma | Celah kamus Indonesia; Malili sebagai kasus terberat; AI ≈24% | C02, C03, C08 |
| 5 | Solusi + demo | Ringkasan → kartu kompleks → kartu endemik wajib verifikasi → peta celah | Demo |
| 6 | Bukti awal | Uji LOSO vs BLAST-97% (hanya angka yang sudah dijalankan); simulasi internal berlabel | 06 §3 |
| 7 | Pembeda dan moat | Matriks 2×2; tabel "mudah ditiru vs sulit ditiru" | §5–6 |
| 8 | Bisnis dan masuk pasar | DMU, harga hipotesis, beachhead Malili, kenapa sekarang | §3, §4, §7, §9 |
| 9 | Roadmap dan tim | 12 bulan + gerbang; kebutuhan penasihat ahli | §10 |
| 10 | Ringkasan dan ask | Rule of three + ask | §11, §13.2 |

### 13.4 Perubahan dari Pitch Deck v2

| Deck v2 | Ganti menjadi |
|---|---|
| "LSM konservasi" sebagai pembayar | Perusahaan + konsultan dokumen lingkungan; LSM sebagai kolaborator |
| SAM ±Rp709 juta, SOM ±Rp167 juta | Kerangka bottom-up tanpa angka sampai ada wawancara |
| "630 endemik" | Hapus; pakai 1.172 spesies asli |
| Kamus v1 "Danau Matano dan Poso" | Kompleks Malili |
| Target lab kampus sebagai pembeli lisensi | Kampus sebagai kolaborator; lisensi untuk lab jasa swasta |
| "4 → 34" | Tunda (K-001) |
| Harga "±5% dari harga tes" | Rentang harga hipotesis dengan patokan yang sudah diverifikasi |

## 14. Rencana paper

**Paper 1:** analisis celah referensi 12S (MiFish) untuk ikan air tawar Indonesia (metode di 06 §5). Kebaruan: belum ditemukan paper serupa khusus Indonesia; wajib cek ulang.

**Calon jurnal (APC belum diverifikasi):** *Environmental DNA*; *Molecular Ecology Resources*; *Scientific Data* (bila menjadi data descriptor kamus); *Metabarcoding and Metagenomics*; *Biodiversitas* atau *BIOTROPIA* (jurnal Indonesia).

**Paper 2 (opsional):** kamus 12S bervoucher untuk ikan Malili dan uji resolusinya, bersama mitra berizin.

## 15. Tim dan kebutuhan kapabilitas

| Nama | Peran | Fokus |
|---|---|---|
| Bramantyo Kunni Nurrisqi | Ketua · Produk & validasi | Arah produk, wawancara, model bisnis |
| Bagus Athallah | Backend & data | Mesin, kamus, simulasi, jejak audit |
| Agathan Khairy Bowo Laksono | Frontend & laporan | Dashboard, Evidence Card, PDF |

**Kebutuhan 6–12 bulan:** penasihat ahli iktiologi (prioritas 1), ahli bioinformatika eDNA, mitra lab dengan data air tawar Indonesia, penasihat regulasi lingkungan (AMDAL).
