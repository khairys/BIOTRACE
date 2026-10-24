# 15 — Log progres agent (kerja otomatis malam 25 Okt 2026)

> Dibaca PERTAMA oleh agent yang melanjutkan. Diperbarui setiap satu langkah selesai, lalu dikomit dan di-push ke branch `integrasi/main-bagus`. Waktu = waktu lokal laptop (WIB).

## Cara melanjutkan

1. Kerja di worktree `D:/Gathan/My Project/BIOTRACE/.worktrees/integrasi` (branch `integrasi/main-bagus`). Folder utama `D:/Gathan/My Project/BIOTRACE` sengaja dibiarkan di `main` untuk demo di port 8000.
2. Python: `D:/Gathan/My Project/BIOTRACE/.venv/Scripts/python.exe` dengan cwd worktree (impor otomatis memakai kode worktree). BLAST: set `BIOTRACE_BLAST_BIN="D:/Gathan/My Project/BIOTRACE/.tools/ncbi-blast-2.17.0+/bin"`.
3. Baca bagian "Langkah berikutnya" di bawah, lanjutkan dari baris pertama yang belum dicentang.
4. Jangan menyentuh branch `data/merge-bagus` (milik Bagus) dan jangan merge ke `main` tanpa persetujuan pengguna.

## Tujuan dari pengguna

Pengguna (Agathan) tidur dan meminta agent bekerja otomatis sampai selesai:
- Pengumpulan data besar spesies ikan tropis, terutama Indonesia: otomatisasi semua yang bisa; untuk yang tidak bisa, cari sumber dan tautan siap unduh manual.
- Semua cara memperoleh data didokumentasikan.
- Gabungkan branch pengguna (`main`) dengan branch Bagus (`data/merge-bagus`) di branch baru, setelah dianalisis.
- Di akhir: catatan dokumentasi "sampai mana".

## Daftar perintah pengguna (urut, sejak riset dataset)

| # | Perintah Agathan (ringkas) | Status |
|---|---|---|
| P1 | Fokus pada database ikan **tropis**, khususnya Indonesia; saran mentor: ambil data dari jurnal Indonesia dan dataset ikan Indonesia; pertimbangkan data negara tetangga tropis (Malaysia, Singapura); prioritaskan spesies penting | Arah kerja tetap |
| P2 | Jelaskan urutan yang disarankan; riset mendalam semua dataset relevan tropis/Indonesia yang bisa otomatis; beri tahu mana otomatis dan mana manual | Selesai: docs/14 (main c1933b2) |
| P3 | Lanjutkan otomatis apa pun sampai selesai tanpa dipantau; buat gambaran besar pengumpulan data besar spesies tropis Indonesia; otomatisasi yang bisa; untuk yang tidak bisa, cari sumbernya dan siapkan tautan siap unduh; dokumentasikan semua cara memperoleh data; beri catatan dokumentasi terakhir sebelum limit habis | **Sedang dikerjakan** |
| P4 | Analisis hasil implementasi rekan (Bagus) dan situasinya; bila beres, buat branch baru gabungan branch saya + branch rekan | Selesai: analisis di riwayat; branch `integrasi/main-bagus`; sisa langkah Bagus (D-034, README, LOSO) dikerjakan di sana |
| P5 | Ingat semua histori, dokumentasikan, ketahui kapan progres terakhir; setelah reset pengguna akan meminta "lanjutkan" | Berjalan: log ini + memori persisten, diperbarui tiap langkah |
| P6 | Pastikan semua perintah tertangkap dan dikerjakan berurutan | Berjalan: tabel ini |

Batasan yang tetap berlaku dari percakapan: tanpa Docker; hemat token tetapi standar tinggi; jangan ubah branch Bagus; jangan merge ke `main` tanpa izin; patuhi AGENTS (A1 tanpa fabrikasi, A13 unduhan lewat `fetch_data.py`, A14 nama dari sumber).

## Riwayat progres

| Waktu (WIB) | Langkah | Hasil |
|---|---|---|
| 25 Okt 02:28 | Riset sumber data (docs/14) | GenBank, BOLD v5, GBIF, FishBase, Mitohelper, rCRUX, OAI jurnal Indonesia; angka celah awal; dikomit di `main` (c1933b2) |
| 25 Okt 02:29 | Rapikan git | Folder utama kembali ke `main`; commit docs/14 dibuang dari branch lokal Bagus (sudah ada di main) |
| 25 Okt 02:30 | Analisis branch Bagus | Langkah 1–6 docs/13 selesai: impor raw dengan SHA-256, header GenBank 592 aksesi, builder v0.3, kamus v0.3 = 65 sekuens 12S dari 38 spesies (V2 23, V3 42), 19 endemik di checklist tetapi 0 bersekuens. Belum: D-034 di 09, README, LOSO, PR |
| 25 Okt 02:31 | Branch gabungan `integrasi/main-bagus` | Merge `main` + `origin/data/merge-bagus` tanpa konflik (3c66fb8); 101 tes lulus |
| 25 Okt 02:40 | LOSO kamus v0.3 + D-034 + README | MiFish, 38 spesies, 65 query: M1 0% vs BLAST-97% 46,2%; M2 90,8%; M5 51,3% (78a4b25) |
| 25 Okt 02:45 | Build web branch gabungan | Lulus (node_modules via junction ke folder utama) |
| 25 Okt 02:50 | Harvester `scripts/harvest_tropis.py` | 11 dataset via `fetch_data.py`: FishBase, GenBank per negara & per spesies, BOLD, GBIF, OAI 11 jurnal, SRA/ENA, regulasi, Zenodo (c627133 + lanjutan) |
| 25 Okt 02:55 | Panen selesai sebagian | FishBase 9 tabel (30 MB); SRA 7 BioProject/135 run/147 FASTQ (9,7 GB, URL ENA); regulasi 3 PDF; BOLD 423.278 rekaman Teleostei global |
| 25 Okt 03:00 | Bug BOLD diperbaiki | API v5 mengabaikan filter geo; ID.tsv = MY.tsv. Kini satu unduhan global + saring lokal; duplikat dihapus, dicatat di manifest |
| 25 Okt 03:05 | Sumber baru ditemukan & ditambahkan ke harvester | 7 jurnal OAI tambahan (Limnotek, Zoo Indonesia, Berita Biologi, MRI, OLDI, Ilmu Kelautan Undip, JITKT IPB); SRA/ENA eDNA; regulasi KKP; Europe PMC (aksesi di paper OA); literatur terbuka |
| 25 Okt 03:10 | OAI | 10/11 jurnal (Undip gagal ListRecords) |
| 25 Okt 03:12 | Zenodo MiFish rCRUX | 5 file, CC BY 4.0 |
| 25 Okt 03:15 | GenBank gagal sementara (efetch 5xx) | Retry diperpanjang (9x, ±7 menit); antrean NCBI dijalankan ulang (lanjut dari batch terakhir) |
| 25 Okt 03:20 | Herder 2006 | PDF di ichthyologie.de hanya 2 halaman pratinjau; teks lengkap = manual |
| 25 Okt 03:25 | Analisis celah `scripts/analyze_tropis.py` | Pemotongan MiFish tervektor (setara trim_mifish, diverifikasi pada sampel tiap run), cache bertahap |
| 25 Okt 03:35 | Europe PMC | 3.206 artikel OA, 53.240 aksesi nukleotida unik disebut di teks |
| 25 Okt 03:40 | BRIN RIN + repositori | 64 dataset BRIN; Zenodo 14, Dryad 31 (mis. mitogenom Rasborinae Sundaland, barcode Jawa-Bali, hibridisasi danau Sulawesi) |
| 25 Okt 03:45 | docs/16 ditulis | Gambaran besar, cara menjalankan, tabel sumber otomatis, 17 sumber manual + tautan, jejak cara menemukan sumber |
| 25 Okt 03:50 | Perbaikan NCBI | Kueri per spesies dibatasi <= 20 kb (rakitan genom bikin efetch timeout); manifest tahan PermissionError; antrean NCBI (country → freshwater → marine → cited) dijalankan ulang (c8ffc4b) |

## Langkah berikutnya

- [x] Sisa langkah Bagus: D-034 (Diusulkan), README, LOSO v0.3
- [x] Build web di branch gabungan
- [x] Harvester otomatis lewat `scripts/fetch_data.py` (14 dataset `tropis_*`)
- [ ] Tunggu antrean NCBI selesai (cek `raw/tropis/genbank_*/2026-10-25/manifest.json` kolom `summary`; bila gagal, jalankan ulang perintah docs/16 §2 — lanjut otomatis dari batch terakhir)
- [ ] Tunggu `tropis_gbif` selesai (resolusi nama spesies)
- [ ] Jalankan `scripts/analyze_tropis.py` (perintah di docs/16 §2) setelah semua panen selesai — JANGAN edit skrip saat berjalan (Windows spawn mengimpor ulang)
- [ ] Isi docs/16 §5 dari `data/curation/tropis_gap_v1/summary.json`; komit `data/curation/tropis_gap_v1/*.csv` (kecuali cache)
- [ ] (opsional) Transkripsi lampiran Permen KP 19/2020 (PDF pindaian) dan cek kandidat Kepmen 1/2021
- [ ] Catatan akhir untuk pengguna di bagian "Ringkasan akhir" dokumen ini; push; buka PR `integrasi/main-bagus` → `main` (jangan merge)
