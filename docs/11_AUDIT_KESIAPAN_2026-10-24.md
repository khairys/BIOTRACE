# 11 — Audit Kesiapan Implementasi BioTrace `[MVP]`

Tanggal: 24 Oktober 2026 (WIB). Pemeriksa: Codex. Status: hasil audit, bukan persetujuan aturan ilmiah atau perubahan skema.

## 1. Kesimpulan

**Konteks produk cukup jelas untuk dipahami dan direncanakan implementasinya. Repo belum siap dinyatakan sebagai MVP lengkap atau aplikasi yang bisa diinstal.** Fondasi prototipe dapat dikerjakan setelah penugasan implementasi. Aturan yang berkonflik memerlukan keputusan pemilik; jalur demo SIMULASI sudah diizinkan secara konsep tetapi kontrak teknisnya perlu dirapikan.

Penghambat utama ialah kamus MiFish Indonesia, konsistensi aturan, dan belum adanya kode aplikasi. Dataset kandidat utama Malili berhasil diunduh, tetapi pemeriksaan awal tidak menemukan cakupan primer MiFish yang diperlukan.

| Area | Status berdasarkan bukti |
|---|---|
| Identitas, pengguna, batas produk | Jelas dalam 01 dan keputusan utama 09 |
| PRD, alur UI, laporan | Cukup rinci sebagai dasar pengerjaan; aplikasi belum ada |
| Aturan dan skema | Sebagian masih usulan; ada konflik operasional |
| Kamus Indonesia MiFish | Belum ada versi yang dikurasi dan lolos syarat |
| Dataset luar | Guyana berhasil diunduh; unduhan skrip Lake St. Pierre gagal |
| Lingkungan instalasi | Node/npm/uv tersedia; Python 3.11 dan BLAST belum terdeteksi |
| Tes, reproduksibilitas, kinerja | Baru spesifikasi; belum ada suite atau hasil run |
| Penggunaan laporan nyata | Belum siap; perlu data layak, validasi, penasihat ahli sesuai D-008 |

## 2. Pemahaman produk

BioTrace memeriksa klaim nama ikan pada hasil eDNA yang sudah diproses lab. Operator mengunggah bacaan, metadata, dan FASTA atau taksonomi lab. Mesin berbasis aturan menentukan tingkat nama yang didukung bukti, skor A–D, penyebab ketidakpastian, dan keputusan `safe`, `with_note`, `must_verify`, atau `do_not_use`.

Hasil berupa dashboard satu halaman, Evidence Card, peta celah kamus, prioritas barcode, dan laporan verifikasi pendukung dengan jejak audit. Aset inti ialah referensi lokal yang terdokumentasi. Batas MVP jelas: tanpa ML, tanpa pemrosesan FASTQ, tanpa internet di core, tanpa estimasi kelimpahan/populasi, dan tanpa menerbitkan AMDAL resmi. Deteksi DNA bukan bukti pasti ikan hidup di lokasi.

## 3. Repo dan instalasi

Snapshot awal: HEAD `550e9b2`; working tree bersih. Yang tersedia ialah dokumen, skrip fetch, petunjuk fetch, dan satu bytecode Python yang ikut dilacak Git.

Belum tersedia: `biotrace_core/`, `api/`, `web/`, `tests/`, `data/`, rules YAML aktual, `pyproject.toml`, lockfile, `package.json`, Makefile, README akar, `.gitignore`, maupun `precomputed/`. Struktur pada 05 adalah rancangan. `raw/` belum ada pada awal audit; sekarang berisi hasil uji unduhan.

| Komponen mesin lokal | Hasil pemeriksaan |
|---|---|
| Python default | 3.13.0 |
| Python lain terdaftar oleh uv | 3.14.6; 3.11 tidak ditemukan dalam inventaris ini |
| Node / npm | v22.21.1 / 10.9.4 |
| uv | Tersedia |
| `blastn`, `makeblastdb`, `make`, `ruff` | Tidak ditemukan di PATH |
| Biopython / ReportLab | Tidak terdeteksi pada Python default yang diperiksa |
| pytest | Tersedia; suite proyek belum ada |

Instalasi aplikasi belum bisa diuji tanpa manifest dan kode. Implementasi memerlukan lingkungan terisolasi Python 3.11 sesuai AGENTS, dependensi dikunci, BLAST+, serta perintah Windows yang sesuai. Jangan mengganti target Python diam-diam. `make test` belum dapat dijalankan; tidak ada klaim bahwa tes aplikasi lulus.

## 4. Dataset yang benar-benar diperiksa

Unduhan dilakukan sekali melalui jalur yang diizinkan A13:

```powershell
python -X utf8 -B scripts/fetch_data.py stelbrink2014 guyana12s lsp_small
```

Folder tujuan belum ada sebelum perintah; tidak ada sumber lama yang ditimpa. FASTQ 2,94 GB tidak diunduh. File hasil unduhan tidak dieksekusi atau diimpor ke kamus; byte FASTA/GenBank/CSV sumber dipertahankan.

### 4.1 Stelbrink 2014 / kandidat Malili

- FASTA dan GenBank berhasil diunduh: masing-masing **95 record**, sesuai KJ667771–KJ667865. Semua accession `.1` hadir dan sekuens FASTA cocok dengan ORIGIN GenBank.
- Panjang sekuens keseluruhan **1.045–1.284 basa**, bukan panjang daerah MiFish.
- **93 record** memiliki anotasi 12S, hanya sepanjang **96–110 basa**; dua lainnya tidak memiliki anotasi 12S.
- Screening primer dari 04 R-CUR-05 pada kedua orientasi, tanpa gap dan maksimal tiga mismatch per primer: **0/95 record** memiliki pasangan primer berurutan. Forward maupun reverse juga tidak ditemukan pada batas itu.
- Semua record memiliki `specimen_voucher`; tidak ada qualifier `country`/`geo_loc_name`. Ini belum membuktikan V1, asal Indonesia, atau cakupan Malili. Rentang aksesi mencakup pembanding di luar kelompok target; seluruh rentang tidak boleh otomatis dianggap ikan Malili.

**Implikasi:** tersedia untuk diunduh, tetapi belum layak menjadi kamus 12S MiFish MVP. Ini screening teknis awal, bukan hasil alat kurasi BioTrace yang sudah jadi atau penetapan ahli. Perlu sumber Indonesia lain yang mencakup marker atau kamus demo SIMULASI terpisah. Jangan mengganti marker menjadi 16S tanpa keputusan.

Metode MiFish menyebut daerah target 163–185 basa; kesimpulan awal menggabungkan anotasi dan screening primer, bukan hanya panjang keseluruhan record. [Miya dkk. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4632578/). Bukti lokal: [GenBank hasil unduhan](../raw/stelbrink2014/stelbrink2014_12s16s.gb); konteks: [Stelbrink dkk. 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4029975/).

NCBI tidak mengenakan pembatasan sendiri pada penggunaan data molekuler, tetapi tidak memberikan jaminan hak pihak ketiga. `GenBank-public` tidak boleh dianggap sertifikasi seluruh hak penggunaan. [Kebijakan NCBI](https://www.ncbi.nlm.nih.gov/home/about/policies/).

### 4.2 Guyana Prancis

- Figshare 29168144 v1 menyediakan **satu CSV, 1.143.446 byte**, bukan paket FASTA dan metadata terpisah seperti gambaran petunjuk.
- Unduhan berhasil; **MD5 cocok** dengan checksum penyedia.
- Pemisah **titik koma**; **1.557 baris**, **369 pasangan label genus/spesies**, **1.557 accession unik**. Seluruh baris memiliki sekuens dan institusi voucher terisi. Ini pemeriksaan struktur, bukan verifikasi taksonomi/V1.
- Panjang sekuens **382–679 basa**. Ada **48 baris** dengan karakter di luar ACGT, termasuk **31 baris** dengan kode di luar ACGTN. Kebijakan IUPAC harus eksplisit; jangan menghapus atau mengganti basa diam-diam.
- Lisensi **CC0** terkonfirmasi di halaman dan metadata. [Dataset Figshare](https://doi.org/10.6084/m9.figshare.29168144).

Sumber menyatakan cakupan Teleo1/12S-V5. Data perlu adapter CSV, pemilihan daerah marker, kurasi, dan kontrak validasi. Tidak boleh mendukung nama ikan Indonesia; hasil marker ini juga tidak membuktikan akurasi MiFish Malili. [Artikel dataset](https://www.nature.com/articles/s41597-026-06811-5).

### 4.3 Lake St. Pierre

Halaman publik dan API daftar versi/file dapat diakses; skrip memperoleh tujuh entri file. Unduhan pertama melalui `/api/v2/files/4370610/download` gagal **HTTP 401 Unauthorized**. HEAD ulang pada endpoint sama juga 401. Proses keluar dengan kode 1; enam file kecil yang direncanakan belum tersimpan.

Dokumentasi penyedia menjelaskan CSV olahan per kode spesies/lokasi, metadata lingkungan, tangkapan pembanding, dan FASTQ. Ini belum merupakan input ASV+identity+batch BioTrace yang siap unggah. Perlu adapter dan pemeriksaan field; dilarang mengarang kontrol, replikat, atau identitas kecocokan. [Dataset Dryad](https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kzf).

Dryad menyatakan dataset dipublikasikan dengan CC0. Jalur fetch perlu mekanisme resmi yang berfungsi atau petunjuk manual yang sudah diizinkan; audit belum membuktikan unduhan manual berhasil. [Ketentuan Dryad](https://datadryad.org/terms).

### 4.4 Checklist dan data Indonesia lainnya

Belum ada tabel berversi `checklist.csv`, `taxa.csv`, status, alias, kompleks, dan sumbernya. Halaman Herder 2012 serta Tantu/Nilawati dapat dibuka; tautan Semantic Scholar Herder 2006 tidak berhasil diakses melalui alat web audit. PDF belum diunduh atau diekstrak menjadi checklist.

Data Matano, Balantak, dan tambahan Indonesia masih perlu akses/pencarian menurut registri repo. Audit tidak mendapatkan data tersebut atau menghubungi pemiliknya. Tidak ada dasar untuk menyebut seluruh inventaris siap. Nama, status, dan kompleks harus berasal dari sumber yang dapat ditelusuri serta tinjauan sesuai A14/D-008.

## 5. Konflik dan kekosongan kontrak

Dicatat tanpa mengubah aturan di [09, K-003–K-011](09_LOG_KEPUTUSAN.md):

| ID | Masalah |
|---|---|
| K-003 | Usulan dianggap default aktif, tetapi aturan kerja meminta persetujuan manusia |
| K-004 | `flagged:conflict` tetap diperlukan untuk LCA, matcher hanya menerima `accepted` |
| K-005 | Mode validasi/SIMULASI, marker Guyana, dan asal geografis referensi belum lengkap |
| K-006 | Hash memuat parameter efektif, tes meminta fingerprint sama saat thread berubah |
| K-007 | Penamaan SIMULASI, flag pada reads lebar/FASTA, sumber alias fixture |
| K-008 | Ambang kurasi dan definisi median belum lengkap dalam YAML |
| K-009 | Uji dataset luar P1 pada 01 tetapi wajib MVP pada PRD |
| K-010 | Lokasi dokumen bisnis/registri lengkap berbeda dari D-010 |
| K-011 | Cakupan/label untuk hasil famili/ordo belum sepenuhnya ditentukan |

Kontrak juga perlu melengkapi penanganan ID duplikat, reads negatif/noninteger, runner-up tidak lengkap, ASV hilang di taxonomy, kontrol `CONTROL` versus validasi waterbody, referensi kosong, serta batch/replikat tidak konsisten. Fallback biologis tidak boleh ditebak.

Untuk tinjauan ilmiah: `(n-r)/n` mengukur fraksi celah checklist; menyebutnya probabilitas identitas ASV tertentu belum ada di kamus memerlukan asumsi tambahan. R-NAME-12 menetapkan runner-up kosong sebagai gap tak hingga, sehingga informasi pembanding yang hilang dapat memperoleh L1 tinggi. Ini kebijakan yang perlu ditinjau, bukan bug kode yang telah terjadi; audit tidak mengubahnya.

## 6. Keandalan skrip dan keamanan operasional

Sintaks dan `--list` lulus. Skrip fetch menggunakan HTTPS dan tidak menjalankan isi dataset. Keberhasilan unduhan bukan sertifikasi keamanan maupun kelayakan ilmiah.

Temuan yang perlu ditangani sebelum penggunaan rutin:

1. `open(dest, 'wb')` / `write_bytes` menimpa path lama ketika diulang, berlawanan dengan pelestarian raw/versi A12.
2. Log menyimpan hanya 16 karakter awal SHA-256; metadata Figshare tidak dilog sendiri dan query efetch lengkap tidak dicatat.
3. Kolom lisensi selalu `?`, meskipun CC0 Guyana terbaca.
4. Tidak ada validasi format/jumlah record/kelengkapan file/checksum penyedia sebelum menyatakan selesai. Jumlah aksesi pada log adalah jumlah permintaan.
5. Tidak ada file sementara dan rename atomik; kegagalan dapat meninggalkan file parsial.
6. Nama file dari metadata remote langsung digabung ke path; perlu pemeriksaan nama dan batas direktori. Nama aktual Guyana pada audit aman.
7. Pemilihan versi Dryad memakai `items[-1]`, belum menangani pagination/hasil kosong/file wajib hilang; unduhan aktual 401.
8. `.gitignore` belum ada walaupun petunjuk menganggap raw diabaikan. File audit/data sekarang untracked; jangan otomatis memasukkan seluruh raw ke commit.

Keamanan aplikasi belum dapat diuji. Implementasi perlu menegakkan batas unggah, nama file baku, validasi server, pembatasan path run/ekspor, dan penanganan teks ekspor CSV. Auth/multi-pengguna masih P1. Kesiapan demo lokal tidak berarti kesiapan layanan publik.

## 7. Gerbang implementasi yang dapat dibuktikan

Rekomendasi audit, bukan perubahan status keputusan:

1. **Bekukan baseline:** pemilik menyelesaikan konflik kritis aturan/skema dan batas MVP. Ambang tetap berlabel belum dikalibrasi ahli.
2. **Fondasi:** Python 3.11 terisolasi, manifest/lockfile, BLAST, perintah Windows, models/config dan fixture yang patuh SIMULASI.
3. **Buktikan core:** tes aturan dan E1–E12 yang sudah konsisten, kasus batas, validasi input, determinisme, isolasi data luar dan simulasi.
4. **Selesaikan demo:** unggah → dashboard → Evidence Card → CSV/PDF → audit, tanpa internet. Hasil pra-hitung khusus demo; keempat keputusan berasal dari run nyata atas data SIMULASI.
5. **Gerbang data nyata:** sumber Indonesia dengan cakupan MiFish, checklist dan metadata; kurasi versi baru dengan sumber/lisensi/voucher/asal/marker. Guyana tidak menggantikan kamus Indonesia.
6. **Validasi:** LOSO/baseline sesuai lingkup disetujui, hanya menampilkan hasil run. Kinerja 200 sampel × 2.000 ASV <120 detik masih target.
7. **Penggunaan di luar demo:** tinjauan ahli D-008 dan validasi relevan. README "Sebelum vs selama hackathon" tetap diisi manusia sesuai 01 §10.

Validasi pasar, harga, penerimaan eDNA dalam dokumen lingkungan, mitra, dan kalibrasi ahli belum boleh dianggap selesai dari keberadaan rencananya. Angka target pada PRD bukan hasil uji.

## 8. Bukti dan batas audit

Audit membaca dokumen repo, memeriksa fetch/toolchain, mengakses sumber terkait dataset MVP, menguji dua unduhan berhasil dan satu gagal, serta memeriksa integritas/struktur sumber lokal. Audit tidak memverifikasi ulang seluruh klaim pemasaran 07, memasang aplikasi, mengubah core/ambang, melakukan LOSO, atau mengesahkan hasil biologis.

- [Hasil pemeriksaan dan hash lengkap](../raw/AUDIT_2026-10-24.json)
- [Log unduhan](../raw/DOWNLOAD_LOG.md)
- [Sumber Stelbrink](../raw/stelbrink2014/README.md)
- [Sumber Guyana](../raw/french_guiana_12s/README.md)

Keputusan kesiapan: pemahaman konteks memadai; fondasi/demo dapat dimulai secara bersyarat; seluruh MVP berbasis data nyata belum siap sebelum gerbang aturan dan data selesai.
