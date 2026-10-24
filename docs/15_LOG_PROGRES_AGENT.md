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

## Langkah berikutnya

- [x] Sisa langkah Bagus: D-034 (Diusulkan), README, LOSO v0.3
- [ ] Build web di branch gabungan
- [ ] Harvester otomatis lewat `scripts/fetch_data.py` (A13): FishBase country/countrysub/species/synonyms, GBIF daftar spesies per negara, GenBank 12S+mitogenom (negara tropis + spesies daftar Indonesia), BOLD v5 COI Indonesia, OAI-PMH 4 jurnal Indonesia
- [ ] Jalankan panen, catat SHA-256 di `raw/DOWNLOAD_LOG.md`; berkas besar tidak dikomit (gitignore), cukup manifest + skrip
- [ ] Analisis celah per tingkat asal (ID / Sundaland / lain / tidak ada) × status (endemik/asli/introduksi) × habitat
- [ ] Daftar sumber manual siap unduh dengan tautan langsung
- [ ] Dokumentasi metode lengkap + catatan akhir; push branch; buka PR bila memungkinkan
