# Cara Mengunduh Data

**Cara cepat (otomatis):**

```
python scripts/fetch_data.py --list
python scripts/fetch_data.py all        # Stelbrink 2014 + Guyana 12S + Lake St. Pierre (CSV)
```

Skrip menyimpan file di `raw/` dan mencatat URL, tanggal, serta SHA-256 di `raw/DOWNLOAD_LOG.md`. Kolom lisensi diisi manual. Skrip belum diuji langsung terhadap API; bila gagal, pakai cara manual di bawah.

PDF checklist (§4) selalu diunduh manual.

**Cara manual:** ikuti langkah di bawah, taruh file di `raw/` (di-.gitignore), lalu minta agent mengkurasi.

## 1. Sekuens Telmatherinidae Malili (Stelbrink dkk. 2014) — T-DATA-01

1. Buka https://www.ncbi.nlm.nih.gov/sites/batchentrez
2. Database: **Nucleotide**.
3. Buat file teks berisi aksesi KJ667771 sampai KJ667865 (satu per baris). Rentang bisa juga dicari di https://www.ncbi.nlm.nih.gov/nuccore dengan kueri `KJ667771:KJ667865[accn]`.
4. Unduh dua format: **FASTA** dan **GenBank (full)**. Simpan sebagai `raw/stelbrink2014/stelbrink2014_12s16s.fasta` dan `raw/stelbrink2014/stelbrink2014_12s16s.gb`.
5. Opsional: ND2 `KJ667866:KJ667963[accn]` → `raw/stelbrink2014/stelbrink2014_nd2.fasta`.

## 2. Pustaka 12S Guyana Prancis — T-DATA-06

1. Buka https://doi.org/10.6084/m9.figshare.29168144
2. Unduh semua file (FASTA dan tabel metadata).
3. Simpan di `raw/french_guiana_12s/`. Catat lisensi yang tertera di halaman Figshare ke `README.md`.

## 3. Lake St. Pierre (Astorg dkk. 2025) — T-DATA-05

1. Buka https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kzf
2. Unduh dulu yang kecil: `edna_lg_clean.csv`, `edna_env.csv`, `elec_long.csv`, `elec_env.csv`, `fish_codes.csv`, `README.md`.
3. `raw_seq.zip` (2,94 GB) hanya bila diperlukan untuk `[P1]`.
4. Simpan di `raw/lake_st_pierre/`.

## 4. Checklist Malili — T-DATA-03

Unduh PDF:
- Herder dkk. 2006, checklist Telmatherinidae: https://www.semanticscholar.org/paper/46d68554f8667959ba28fc47f111b97c1e36c628
- Herder dkk. 2012, ikan introduksi Malili: https://www.researchgate.net/publication/232708663
- Tantu & Nilawati 2007: https://www.researchgate.net/publication/370417162

Simpan di `raw/checklists/`. Agent akan membantu mengetik tabelnya ke `checklist.csv` dan `introductions.csv`; setiap baris tetap dicek manusia terhadap PDF.

## 5. Setelah mengunduh

- Jangan ubah isi file mentah.
- Tulis di `raw/DOWNLOAD_LOG.md`: nama file, URL, tanggal unduh, lisensi.
- Minta agent: "kurasi `raw/...` ke kamus versi baru sesuai 04 §5".

## 6. Impor data mentah lokal rekan tim (tanpa unduh ulang)

Bila rekan tim sudah mengunduh sumber publik dan mencatat SHA-256-nya (mis. `data/ref/v0.1/manifest.csv` di repo BagusAth/BIOTRACE), file mentah boleh disalin dari laptopnya alih-alih diunduh ulang:

1. Salin file **mentah** (bukan hasil turunan seperti `ref12S.fasta`) ke `raw/<dataset>/` tanpa mengubah byte.
2. Hitung SHA-256 setiap file dan cocokkan dengan manifest rekan. File yang tidak cocok atau hilang **tidak dipakai**; unduh ulang lewat `scripts/fetch_data.py`.
3. Catat di `raw/DOWNLOAD_LOG.md`: nama file, URL/sumber asli dan versi/commit dari manifest rekan, tanggal unduh asli, siapa yang mengunduh, SHA-256, hasil pencocokan, dan lisensi.
4. Simpan salinan manifest rekan di `raw/<dataset>/manifest_rekan.csv` sebagai bukti.
