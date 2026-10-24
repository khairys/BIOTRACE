# Sumber mentah lsp12s_mitohelper — metadata GenBank kamus 12S Kanada (validasi)

Untuk modul validasi Lake St. Pierre (`CA-QC`, docs/13 §7). **Hanya mode validasi** (A4); tidak
pernah mendukung nama ikan Indonesia.

- `accessions.txt`: 1.158 aksesi mitohelper 12S (arsip di `raw/malili12s_mitohelper/mitohelper/`,
  commit `f3d92c7`) untuk spesies binomial di
  `data/external/lake_st_pierre/v20250924/fish_codes.csv` (Astorg dkk. 2025, Dryad
  10.5061/dryad.3bk3j9kzf). Tidak termasuk kerabat dari luar wilayah.
- `genbank/esummary_000.json` … `esummary_011.json`: NCBI E-utilities esummary (db nuccore),
  100 aksesi per permintaan, diunduh 2026-10-25 lewat `scripts/fetch_data.py lsp12s_genbank`.
- `genbank_flat/headers_000.gb` … `headers_015.gb`: header flat file GenBank (`seq_start=1`,
  `seq_stop=1`, tanpa sekuens) untuk 780 aksesi yang esummary-nya tanpa `/specimen_voucher` atau
  `/country` (daftar di `genbank_flat/accessions.txt`).

Jumlah record setiap batch diverifikasi saat unduh. Lisensi: kebijakan NCBI
(https://www.ncbi.nlm.nih.gov/home/about/policies/). Sekuens diambil dari arsip mitohelper,
bukan diunduh ulang.
