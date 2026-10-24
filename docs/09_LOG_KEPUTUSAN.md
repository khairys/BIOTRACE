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

### K-003 — Usulan aktif sebagai default vs persetujuan manusia `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex, audit kesiapan.
- Isi: Judul bagian usulan menyatakan "aktif sebagai default r0.1", sedangkan AGENTS.md §4 mewajibkan menunggu persetujuan untuk aturan, skema, dan keputusan. D-018–D-023 sudah dipakai dalam spesifikasi tetapi masih Diusulkan; D-027 juga belum disetujui.
- Pertanyaan keputusan: Apakah usulan tersebut boleh diterapkan sebagai baseline prototipe berlabel "usulan tim, belum dikalibrasi ahli", atau menunggu keputusan masing-masing pemilik?
- Status: Terbuka; tidak ada status D-* yang diubah oleh audit. Pembaruan implementasi: r0.2 dipakai sebagai baseline prototipe berlabel "usulan tim, belum dikalibrasi ahli" (D-029, 12); persetujuan formal tetap menunggu pemilik.
- Pemilik: Ketua, Backend & data; Frontend untuk D-027.

### K-004 — Referensi berkonflik dipakai atau dikeluarkan `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: 03 R-NAME-01 hanya menerima `curation_status = accepted`. 04 R-CUR-08 menyatakan sekuens identik dari spesies berbeda berstatus `flagged:conflict` dan tetap dipakai agar turun ke LCA. Keduanya tidak bisa diterapkan sekaligus dengan skema status sekarang.
- Pertanyaan keputusan: Bagaimana memisahkan status kelayakan dan flag konflik, serta apakah entri konflik boleh mendukung kandidat/LCA?
- Status: Terbuka; perlu usulan aturan/skema dan tes sebelum implementasi. Pembaruan implementasi: pilihan accepted + flag conflict dan wajib turun tingkat dikonfirmasi manusia di chat dan diterapkan di r0.2 beserta tes (D-029, 12); tinjauan ahli belum ada.
- Pemilik: Backend & data bersama penasihat ahli.

### K-005 — Kontrak mode, marker, dan asal referensi `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: 03 R-NAME-01 mensyaratkan direktori referensi Indonesia dan `in_indonesia = true`; belum ada ketentuan ekuivalen untuk validasi luar atau kamus sintetis terpisah. 04 §3 mewajibkan modul luar, tetapi enum marker input §1.2 tidak memuat Teleo1/12S-V5 dataset Guyana. 05 §5 hanya mendefinisikan mode normal/validation, sedangkan 04 §6 melarang kamus sintetis masuk `data/reference/`.
- Tambahan geografis: A4 melarang referensi luar Indonesia mendukung laporan Indonesia; R-NAME-01 mengecek keberadaan spesies di Indonesia, belum secara eksplisit asal spesimen. `specimen_country` di 04 opsional. Seluruh 95 record GenBank yang diperiksa audit tidak memuat country/geo_loc_name; asal tidak boleh diasumsikan dari judul paper.
- Pertanyaan keputusan: Tetapkan kelayakan per mode, marker validasi, propagasi SIMULASI, dan perlakuan asal spesimen yang belum diketahui tanpa melonggarkan A4/A5 diam-diam.
- Status: Terbuka; tidak ada data yang dimasukkan ke kamus aktif. Pembaruan implementasi: mode normal/simulation/validation dipisahkan sementara sesuai 12; marker Teleo1/12S-V5 hanya dipakai di mode validation; kamus `data/reference/v0.1` tetap 0 sekuens diterima.
- Pemilik: Ketua, Backend & data; penasihat ahli untuk cakupan ilmiah.

### K-006 — Sidik jari lintas jumlah thread `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: 03 R-AUD-02 memasukkan parameter efektif ke run fingerprint. 05 §6 mencatat `num_threads` sebagai parameter BLAST. 06 T-REPRO mengharuskan report fingerprint sama walau jumlah thread berbeda, sementara report fingerprint juga memasukkan run fingerprint.
- Pertanyaan keputusan: Apakah parameter eksekusi seperti jumlah thread dicatat di manifest tetapi dikecualikan dari fingerprint analitis, atau target tes dibedakan antara kesamaan hasil dan kesamaan fingerprint?
- Status: Terbuka. Pembaruan implementasi: thread, lokasi executable dan durasi dicatat di `execution`, di luar fingerprint analitis (dikonfirmasi manusia di chat; D-029, 12); T-REPRO lulus.
- Pemilik: Backend & data.

### K-007 — Kontrak berkas SIMULASI dan fixture `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: A2 mewajibkan SIMULASI di nama file, tetapi contoh 04 §8 dan 10 §6 memakai `reads.csv`, `metadata.csv`, dan folder `matano_sim_v1`. Format reads lebar menyebut seluruh kolom setelah `asv_id` sebagai sample_id, sementara tabel simulasi wajib memiliki `is_simulated`. FASTA tidak memiliki kolom boolean. FX-1 disebut fiktif, tetapi alias E9 menggunakan nama asli yang belum tersedia dalam sumber raw yang diunduh audit ini (A14).
- Pertanyaan keputusan: Tetapkan penamaan berkas, pengecualian kolom metadata pada reads lebar, propagasi flag untuk FASTA/run, dan sumber atau pengganti fiktif alias fixture.
- Status: Terbuka. Pembaruan implementasi: data demo `data/demo/matano_SIMULASI_v3/` dan `precomputed/matano_SIMULASI_v3/` memakai nama berkas SIMULASI, `is_simulated=true` per baris, FASTA mewarisi flag run (12).
- Pemilik: Backend & data, Frontend & laporan.

### K-008 — Parameter kurasi belum tercakup YAML `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: A3 mengharuskan semua ambang dibaca dari rules YAML. Contoh 04 §7 belum memuat batas mismatch primer, panjang relatif, dan ambiguitas R-CUR-05/06. Populasi untuk median panjang amplikon belum ditetapkan. Bobot prioritas R-GAP-01 juga belum tercantum dalam konfigurasi berversi.
- Pertanyaan keputusan: Lengkapi usulan konfigurasi kurasi/prioritas dan definisi median sebelum membekukan aturan pertama; nilai ilmiah tidak diubah tanpa persetujuan.
- Status: Terbuka. Pembaruan implementasi: angka kurasi dari 04 dan bobot prioritas dari 03 dipindah ke rules r0.2 tanpa mengubah nilai; definisi median sementara sesuai 12.
- Pemilik: Backend & data; penasihat ahli untuk parameter ilmiah.

### K-009 — Validasi luar sebagai MVP atau P1 `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: 01 §7 menjadwalkan uji Lake St. Pierre dan pustaka Guyana pada P1. 02 F27 mewajibkan minimal satu dataset luar pada MVP; 04 §3 dan 06 juga menandai bagian validasi Guyana sebagai MVP.
- Pertanyaan keputusan: Apakah LOSO dataset luar harus selesai sebelum demo, atau menjadi gerbang lanjutan setelah prototipe SIMULASI? Jika tetap MVP, 01 perlu diselaraskan melalui keputusan manusia.
- Status: Terbuka; tidak ada hasil validasi yang diklaim lulus. Pembaruan implementasi: LOSO pustaka Guyana (mode validation, r0.2) selesai dijalankan 2026-10-24, hasil di `validation/results/2026-10-24_GF_r0.2.json`; marker berbeda dari MiFish, jadi bukan validasi biologis Indonesia.
- Pemilik: Ketua dan Backend & data.

### K-010 — Lokasi dokumen lengkap dan materi bisnis `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: D-010 dan docs/README menyebut registri lengkap serta dokumen bisnis berada di Project GENOHACK, bukan repo produk. Keduanya saat audit dilacak Git di `project/07_REGISTRI_BUKTI.md` dan `project/08_BISNIS_DAN_MASUK_PASAR.md`.
- Pertanyaan keputusan: Apakah salinan repo memang diinginkan dan perlu diakui sebagai lokasi resmi/salinan?
- Status: Terbuka; file tidak dipindah/dihapus. Bukan penghambat mesin inti.
- Pemilik: Ketua.

### K-011 — Agregasi untuk nama famili/ordo belum lengkap `[MVP]`
- Tanggal: 2026-10-24 · Dicatat oleh: Codex.
- Isi: R-NAME-06 mengizinkan hasil famili/ordo dari kandidat lintas genus. R-SCORE-07 meminta "genus dari takson yang dilaporkan", yang tidak tunggal pada kasus tersebut; penalti L1 juga memakai fraksi referensi per genus. Belum ada fallback eksplisit jika kandidat tidak berbagi ordo. Label threatened/invasive pada takson agregat belum menetapkan penggunaan satu, semua, atau sebagian anggota kandidat.
- Pertanyaan keputusan: Tentukan agregasi cakupan/label dan fallback taksonomi sebelum implementasi; jangan memilih genus/status dari ingatan model.
- Status: Terbuka; perlu fixture tambahan setelah keputusan. Pembaruan implementasi: penanganan konservatif sementara sesuai 12 (P_missing null lintas genus, label agregat butuh dukungan semua kandidat, unknown bila tak berbagi ordo).
- Pemilik: Backend & data bersama penasihat ahli.

Rincian bukti dan gerbang implementasi: [11 — Audit Kesiapan](11_AUDIT_KESIAPAN_2026-10-24.md). Pencatatan konflik tidak menyetujui perubahan aturan/skema.

### D-029 — Baseline pengerjaan MVP setelah audit `[MVP]`
- Tanggal: 2026-10-24 · Status pencatatan: **Diusulkan** (status formal dokumen tetap milik manusia).
- Diusulkan oleh: Codex berdasarkan instruksi implementasi keseluruhan dari pengguna setelah audit.
- Konfirmasi manusia dalam chat: K-004 accepted + flag conflict, wajib turun tingkat; K-006 thread dipisah dari fingerprint analitis. Konfirmasi ini adalah otorisasi implementasi pilihan tersebut, bukan persetujuan ilmiah ambang.
- Keputusan implementasi: simpan rules r0.1, buat r0.2 tanpa mengubah angka ambang; dokumentasikan kontrak mode/berkas/agregasi dan penanganan dataset tertunda dalam [12 — Baseline implementasi](12_BASELINE_IMPLEMENTASI.md).
- Dampak: F1–F27, F37–F42; R-CUR-08, R-NAME-01, R-AUD-02; tes konflik dan reproduksibilitas. Semua ambang tetap belum dikalibrasi ahli.
- Menggantikan: perilaku konflik dan parameter eksekusi yang belum konsisten pada r0.1, khusus prototipe yang diotorisasi pengguna.
