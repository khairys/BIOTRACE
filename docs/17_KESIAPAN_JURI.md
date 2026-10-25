# 17 — Paket pemeriksaan juri BioTrace `[MVP]`

Keputusan rilis: D-038, 25 Oktober 2026. Persetujuan implementasi D-034–D-037 diberikan Agathan dalam chat. Status ilmiah tetap **usulan tim, belum dikalibrasi ahli**. Dokumen ini memisahkan hasil yang dapat diperiksa dari pekerjaan yang memerlukan bukti tambahan.

## 1. Yang dinilai

BioTrace memeriksa klaim hasil eDNA yang sudah diproses lab. Input berupa bacaan, metadata, FASTA ASV atau taksonomi lab. Output berupa tingkat nama, nilai A–D, alasan ketidakpastian, empat keputusan, prioritas barcode, serta laporan verifikasi pendukung dengan jejak audit. Ini bukan dokumen AMDAL resmi. Deteksi DNA bukan bukti pasti ikan hidup di lokasi.

- Changelog di dalam snapshot mempertahankan status ketika snapshot dibuat. Persetujuan terbaru D-034–D-037 ada di log D-038; hash snapshot tidak diubah untuk mengganti tulisan historis.
- Kamus aktif: `data/reference/v0.5`, 999 sekuens MiFish, 630 spesies berreferensi, 133 sekuens dari spesimen Indonesia. Angka ini jumlah isi file, bukan ukuran akurasi.
- Fokus produk tetap ikan air tawar/Malili. Dataset eDNA terumbu Indonesia dipakai untuk membuktikan alur data nyata; tidak disebut sebagai validasi lapangan Malili.
- Sumber dataset: Marwayana dkk. 2022, *Environmental DNA*, doi:10.1002/edn3.257; Dryad doi:10.5068/D12T1B, CC0. Adapter dan batasnya ada di `data/edna_asli/marwayana2022_mifishu/README.md`.
- Demo Matano **SIMULASI** membuktikan skenario perangkat lunak, termasuk kompleks/alias, dan tidak menjadi bukti resolusi biologis spesies Malili.
- Tidak ada ML, jaringan saat analisis, penaksiran kelimpahan dari reads, atau klaim penelusuran populasi.

## 2. Jalur pemeriksaan cepat

1. Persiapan dependensi: `uv run python scripts/project.py setup`. Snapshot kurasi dan pra-hitung sudah disertakan; tidak perlu mengunduh ulang seluruh `raw/`.
2. Jalankan: `uv run python scripts/project.py demo`, buka `http://127.0.0.1:8000`.
3. Pilih **Muat data eDNA asli Indonesia**. Baca sumber, asumsi blank/batch, skala checklist, versi kamus, serta ringkasan keputusan.
4. Buka sebuah Evidence Card. Telusuri nama lab, kandidat, dukungan voucher/aksesi, skor, penyebab, tindak lanjut, dan batas interpretasi.
5. Pilih **Ringkasan PDF** (10 halaman untuk run rilis ini) untuk salinan baca singkat (maksimal 20 contoh klaim, 6 kartu, 20 genus; angka ringkasan memakai seluruh data). **Unduh PDF** memuat laporan lengkap, yang pada dataset asli ini mencapai 1.580 halaman. ZIP memuat seluruh klaim dan jejak audit. Salin sidik jari dan periksa di halaman Verifikasi (pencarian pada run lokal perangkat ini).
6. Buka Validasi: bedakan kamus, marker, dan versi aturan masing-masing eksperimen. M3 dibanding baseline; M1 nol dapat bersifat struktural pada pustaka tanpa spesimen Indonesia.
7. Jalankan demo SIMULASI bila ingin memeriksa seluruh empat kategori serta contoh kompleks/alias. Label SIMULASI wajib tetap terlihat.

## 3. Bukti yang bisa dihitung ulang

```powershell
uv run python scripts/project.py test
uv run python scripts/project.py test-slow
uv run python scripts/project.py build
uv run python scripts/prepare_jury.py check
uv run python scripts/prepare_jury.py audit
uv run python scripts/prepare_jury.py quality
uv run biotrace verify --run precomputed/edna_asli_marwayana2022_r0.4_v0.5
uv run python scripts/test_browser.py
```

- `validation/jury/v0.5/release_checks.json`: hash manifest, jumlah isi kamus, integritas seluruh pra-hitung, hasil demo asli v0.5, perbandingan dengan v0.4, dan inventaris manifest panen.
- `validation/jury/v0.5/reproducibility.json`: analisis ulang lengkap pada 1 thread menghasilkan fingerprint run/laporan yang sama dengan 4 thread. Run satu thread terkena Modern Standby, sehingga durasinya tidak dipakai sebagai benchmark.
- `validation/jury/v0.5/ringkasan_juri.pdf`: salinan baca untuk juri yang bisa dibuka tanpa menjalankan aplikasi; fingerprint sama dengan seluruh klaim rilis.
- `validation/jury/v0.5/data_quality.json`: pemeriksaan hubungan sumber, level voucher, kualitas checklist, flag konflik, dan ketersediaan alias/kompleks. Snapshot v0.5 mempunyai 957 V2 dan 42 V3, 75 sekuens berflag konflik, serta belum mempunyai anggota kompleks terkurasi pada data nyata; contoh kompleks SIMULASI tetap terpisah.
- `validation/results/`: eksperimen LOSO aktual; hanya file hasil run lengkap yang dipublikasikan. LOSO v0.5 menggunakan semua spesies, tanpa mengisi metrik dari ingatan.
- `precomputed/edna_asli_marwayana2022_r0.4_v0.5/`: input asli yang dipakai, klaim, ringkasan, PDF, manifest, dan hasil run. Sumber serta asumsi terikat pada fingerprint.
- `output/browser/` dan `output/validation/`: bukti pengujian lokal (diabaikan Git); bukan sumber klaim angka biologis.

Untuk analisis penuh baru, BLAST memiliki anggaran 600 detik. `BIOTRACE_BLAST_TIMEOUT_SECONDS` menerima integer 1–3600; perubahan anggaran tidak mengubah ambang biologis. Waktu nyata selalu dibaca dari hasil run. Target kinerja sintetis 200 sampel × 2.000 ASV dibedakan dari dataset asli yang lebih sulit. Jangan menyatakan semua dataset selalu selesai kurang dari dua menit. Uji sintetis memakai 200 sampel pada satu lokasi (2.000 klaim) dengan query acak SIMULASI; data asli menghasilkan 4.354 klaim di 39 lokasi. Keduanya bukan beban komputasi atau bukti biologis yang setara.

Laptop harus tetap aktif selama komputasi. Pada pengujian rilis, Windows Modern Standby menginterupsi satu upaya LOSO; upaya tersebut tidak menghasilkan metrik publik. LOSO kini menyimpan checkpoint per spesies (ekstensi `.checkpoint`, diabaikan Git/API) dengan hash isi, kamus, aturan, dan versi engine. Mengulang perintah yang sama melanjutkan spesies selesai tanpa mencampur versi; JSON metrik baru ditulis setelah seluruh spesies target selesai.

Hasil rilis data asli v0.5: 4.354 klaim, 152 taksa; `safe` 0, `with_note` 1.685, `must_verify` 1, `do_not_use` 2.668. Seluruh 4.354 keputusan/nama/nilai/label sama dengan pra-hitung v0.4 pada dataset ini. Waktu run rilis 277,507 detik; hasil tidak ditafsirkan sebagai akurasi 100%. Bukti terikat pada fingerprint `fa3006dabe4e026631bfaeba5536619dc9ab78986bbba5ba264ed12fbde24fa0`.

LOSO lengkap v0.5 (`validation/results/2026-10-25_ID_v0.5_r0.4.json`): 630 spesies, 999 query, marker MiFish, r0.4. Target menahan diri dengan benar ≥90% tercapai pada pustaka ini. Tetap ada 75 nama keliru pada tingkat apa pun, dan sikap hati-hati mempunyai biaya resolusi nama:

| Metrik | BioTrace | Baseline BLAST-97% | Penyebut dan batas |
|---|---:|---:|---|
| M1 nama keliru berkeputusan aman | 0/999 (0%) | 325/999 (32,53%) | Dipengaruhi pembatasan kualitas referensi; bukan bukti nol risiko lapangan |
| M2 menahan diri dengan benar | 924/999 (92,49%) | — | Pengujian pustaka internal dengan L4 metodologis maksimum |
| M3 nama keliru di tingkat apa pun | 75/999 (7,51%) | 325/999 (32,53%) | Bukan pengukuran akurasi/keberadaan ikan di lokasi |
| M4 nama spesies benar pada uji tanpa dirinya | 120/589 (20,37%) | — | Hanya query dari spesies dengan lebih dari satu referensi |
| M5 turun tingkat dengan takson benar | 458/589 (77,76%) | — | Proxy kehati-hatian; belum membuktikan penurunan tidak diperlukan |

M4 yang rendah dan M5 tinggi merupakan keterbatasan yang nyata. Solusinya adalah memperkuat referensi bervoucher, checklist lokal, dan evaluasi resolusi marker/ahli sebelum mempertimbangkan aturan baru. Angka tidak diperbaiki dengan melonggarkan ambang untuk kebutuhan pitch.

## 4. Penyelesaian keputusan dan bahan yang belum lengkap

| Item | Keputusan untuk rilis juri | Solusi lanjutan dan gerbang bukti | Pemilik |
|---|---|---|---|
| D-034–D-037 | Disetujui manusia; implementasi masuk rilis. Tidak ada persetujuan ahli yang dikarang | Tinjauan taksonomi dan status tetap dicatat terpisah | Agathan; Bagus untuk tindak lanjut data |
| v0.5 dan hasil lama | v0.5 menjadi bawaan bersama; v0.1–v0.4 dan semua pra-hitung lama dipertahankan | Pembaruan data berikutnya memakai folder versi baru | Backend & data |
| Timeout BLAST | Anggaran eksekusi eksplisit dan galat terstruktur; hasil parsial tidak diterbitkan | Ukur tiap run; optimasi hanya dengan pembandingan hasil dan fingerprint | Backend |
| CRLF/LF | YAML analitis dikunci byte LF; snapshot lama tidak diubah | Tes mencegah CRLF masuk aturan/alasan | Backend; CI |
| Endemik Malili | 0 dari 19 spesies endemik checklist mempunyai referensi layak pada snapshot rilis; tampil sebagai celah | Sekuens MiFish spesimen beridentitas/voucher dan asal yang dapat ditelusuri; kurasi R-CUR, lalu versi baru | Bagus + penasihat ahli |
| Checklist danau dari sumber sekunder/berita | Tetap berlabel; R-DEC-09 membatasi klaim yang bergantung padanya | Cocokkan setiap baris ke teks/halaman sumber asli dan lingkup danau sebelum menaikkan kualitas sumber | Kurator + ahli |
| GBIF sebagai bukti tercatat Indonesia | Tidak dianggap bukti spesies asli/liar di danau tertentu | Bedakan budidaya/impor/okurensi liar dari sumber primer dan pemeriksaan spesimen | Kurator + ahli |
| Sinonimi dan konflik sekuens lintas spesies | Nama/flag sumber dipertahankan; mesin tidak memilih nama hanya karena seri | Cek Catalog of Fishes secara manual dan sumber voucher; koreksi masuk versi baru | Ahli taksonomi |
| Status invasif/IUCN/regulasi | Transkripsi dan status sumber belum dianggap tinjauan ahli atau kepatuhan hukum | Verifikasi baris/halaman sumber, catat pemeriksa/tanggal; periksa status mutakhir sebelum penggunaan operasional | Kurator + penasihat terkait |
| Koordinat/tanggal kosong | Nilai kosong dan peringatan ditampilkan; tidak ada koordinat buatan | Transkripsi Tabel S1 dengan identitas sampel yang cocok dan sumber halaman; buat input versi baru | Kurator |
| Batch/jenis blank tidak dinyatakan | Pengelompokan satu batch adalah asumsi konservatif yang ditampilkan | Konfirmasi metadata penulis; jangan mengklaim konfirmasi sudah diperoleh | Tim validasi |
| Panen GenBank belum selesai | Bekukan isi snapshot rilis; manifest parsial tetap bahan kurasi | Lanjutkan melalui `fetch_data.py`, verifikasi selesai/hash, analisis ulang, lalu kurasi versi baru | Bagus |
| COI Jawa–Bali | Bahan voucher/lapis celah; tidak dimasukkan sebagai MiFish | Sekuensing ulang 12S atau sumber mitogenom yang sah | Kurator + mitra berizin |
| Lengguru teleo | Tetap terpisah dari MiFish | Modul validasi marker teleo terpisah; tidak dicampur ke laporan MiFish | Backend & data |
| Checklist Raja Ampat/Kottelat | Bahan sumber, tidak otomatis menjadi checklist lokal | Transkripsi asal-usul/kategori dan lingkup lokasi dari sumber, pemeriksaan ahli, versi baru | Kurator |
| M1 nol struktural | Tidak dijadikan klaim keamanan; UI menonjolkan M3 | Validasi pustaka yang memiliki dukungan Indonesia dan tinjauan ahli/lapangan | Tim validasi |
| Akurasi A–D dan F19/F34 | Tidak ada probabilitas/akurasi terkalibrasi yang diiklankan | VAL-E1: 50 klaim tinjauan buta; VAL-F1: pembanding lapangan; aturan baru hanya setelah persetujuan | Ketua + ahli |
| K-001 angka “4 → 34” | Dikeluarkan dari klaim rilis; kebutuhan angka tersebut ditutup oleh D-038 | Baru boleh dipakai bila teks primer cocok dan registri bukti diperbarui | Ketua |
| FishBase dan sumber lain | Lisensi sumber dicantumkan; persetujuan demo tidak menjadi lisensi komersial | Izin penggunaan sesuai lisensi sebelum komersialisasi | Ketua |
| Catatan ahli/login | Fitur pencatatan lokal tersedia; nama peninjau belum diautentikasi | Penyedia identitas dan otorisasi diperlukan sebelum layanan banyak pengguna | Produk + backend |
| FAIRe/PhyloRef/FASTQ/format regulasi | Roadmap dengan kebutuhan sumber/parameter; tidak disebut fitur selesai | Spesifikasi resmi, parameter yang disetujui, tes pembanding, dan keputusan terpisah | Pemilik area |
| Wawancara/mitra/pilot | Tidak ada pelanggan, harga tervalidasi, atau mitra yang dikarang | Bukti wawancara/izin nama/LOI sebelum klaim komersial | Ketua |
| Pengakuan sebelum/selama hackathon | Mengikuti konfirmasi manusia; riwayat Git tersedia untuk pemeriksaan | Manusia mengesahkan atribusi; agent tidak menebak kontribusi | Tim |

Setiap baris di atas mempunyai keputusan rilis dan gerbang berikutnya. Item yang membutuhkan ahli, izin, penulis dataset, atau spesimen fisik tetap jujur berstatus menunggu bukti; menerima usulan implementasi tidak membuat bukti tersebut ada.

## 5. Batas penggunaan dan jawaban untuk juri

**Apa yang sudah terbukti?** Kode menjalankan aturan yang dapat ditelusuri; input dan hasil tersimpan; run dapat diverifikasi; data asli dapat diproses; LOSO mengukur perilaku pada pustaka yang disebutkan.

**Apa yang belum terbukti?** Akurasi lapangan Malili, kalibrasi nilai A–D, kepastian deteksi ikan hidup, dan keberterimaan laporan sebagai pemenuhan regulasi.

**Mengapa hasil aman bisa sedikit atau nol?** Keputusan bergantung pada kekuatan referensi, kelengkapan kerabat, replikat, kontrol, dan skala checklist. Banyak nama dapat diturunkan atau dibatasi R-DEC-09. Ini bukan ukuran sensitivitas lapangan, dan jumlah “aman” tidak dioptimalkan untuk pitch.

**Mengapa demo laut sedangkan fokus air tawar?** Sumber eDNA Indonesia terbuka memungkinkan pemeriksaan alur pada data nyata; keterbatasan penerapan ke Malili disebut eksplisit. Cerita Malili tetap ditopang inventaris celah dan skenario SIMULASI yang berlabel.

**Bagaimana kamus menjadi lebih kuat?** Setiap celah menghasilkan prioritas barcode; sekuens baru harus mempunyai sumber, marker yang cocok, voucher, dan jejak asal. Kurasi menghasilkan versi baru, kemudian laporan lama dapat dicocokkan ulang dan dibandingkan tanpa ditimpa.
