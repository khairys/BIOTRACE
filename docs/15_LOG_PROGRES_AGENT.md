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

## Riwayat progres

| Waktu (WIB) | Langkah | Hasil |
|---|---|---|
| 25 Okt 02:28 | Riset sumber data (docs/14) | GenBank, BOLD v5, GBIF, FishBase, Mitohelper, rCRUX, OAI jurnal Indonesia; angka celah awal; dikomit di `main` (c1933b2) |
| 25 Okt 02:29 | Rapikan git | Folder utama kembali ke `main`; commit docs/14 dibuang dari branch lokal Bagus (sudah ada di main) |
| 25 Okt 02:30 | Analisis branch Bagus | Langkah 1–6 docs/13 selesai: impor raw dengan SHA-256, header GenBank 592 aksesi, builder v0.3, kamus v0.3 = 65 sekuens 12S dari 38 spesies (V2 23, V3 42), 19 endemik di checklist tetapi 0 bersekuens. Belum: D-034 di 09, README, LOSO, PR |
| 25 Okt 02:31 | Branch gabungan `integrasi/main-bagus` | Merge `main` + `origin/data/merge-bagus` tanpa konflik (3c66fb8); 101 tes lulus |

## Langkah berikutnya

- [ ] Selesaikan sisa langkah Bagus di branch gabungan: D-034 (Diusulkan) di 09, README, uji LOSO v0.3, build web
- [ ] Harvester otomatis lewat `scripts/fetch_data.py` (A13): FishBase country/countrysub/species/synonyms, GBIF daftar spesies per negara, GenBank 12S+mitogenom (negara tropis + spesies daftar Indonesia), BOLD v5 COI Indonesia, OAI-PMH 4 jurnal Indonesia
- [ ] Jalankan panen, catat SHA-256 di `raw/DOWNLOAD_LOG.md`; berkas besar tidak dikomit (gitignore), cukup manifest + skrip
- [ ] Analisis celah per tingkat asal (ID / Sundaland / lain / tidak ada) × status (endemik/asli/introduksi) × habitat
- [ ] Daftar sumber manual siap unduh dengan tautan langsung
- [ ] Dokumentasi metode lengkap + catatan akhir; push branch; buka PR bila memungkinkan
