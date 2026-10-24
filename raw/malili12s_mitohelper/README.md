# Sumber mentah malili12s_mitohelper — kandidat 12S Malili, metadata GenBank dan GBIF

Asal: folder `data/raw/` repo `BagusAth/BIOTRACE` (commit
`5a407e427ff3fe717b2c871209df02a28966b914`). Berkas diunduh di laptop Bagus pada 2026-10-24 (WIB)
oleh skrip repo lama (`scripts/fetch_raw.py`, `fetch_voucher.py`, `fetch_gbif.py`), lalu disalin
byte per byte ke sini pada 2026-10-25 lewat `scripts/fetch_instructions.md` §6. SHA-256 setiap
berkas cocok dengan `manifest_rekan.csv` (salinan `data/ref/v0.1/manifest.csv` repo lama). Tidak ada
berkas yang diunduh ulang.

| Berkas | Sumber asli | Versi |
|---|---|---|
| `mitohelper/QIIME-compatible/12S-seqs-derep-uniq.qza`, `12S-tax-derep-uniq.qza`, `README.MD`; `mitohelper/MitoFish_download_links.MD` | https://github.com/aomlomics/mitohelper (Lim & Thompson 2021; data dari GenBank dan MitoFish) | commit `f3d92c7` (12S Juli 2026) |
| `biotrace_ref_malili_v0.1.zip` dan isinya di `biotrace_ref_malili_v0.1/` | Ekstraksi kandidat Malili dari mitohelper oleh tim (Audit Dataset): 896 aksesi, 226 nama | v0.1 |
| `genbank/esummary_000.json` … `esummary_008.json` | NCBI E-utilities `esummary` (db nucleotide), 100 aksesi per permintaan; memuat `organism`, `subtype/subname` (specimen_voucher, country, isolate) | diambil 2026-10-24 |
| `gbif/gbif_species_indonesia.json` | GBIF species API: `species/match`, `occurrence/search?country=ID`, `species/{key}/iucnRedListCategory` untuk 180 nama | diambil 2026-10-24 |
| `gbif/gbif_telmatherinidae.json` | GBIF species API: spesies Telmatherinidae yang diterima | diambil 2026-10-24 |

`.qza` dan `.zip` adalah arsip ZIP. Ekstrak ke folder kerja saat membangun kamus; jangan menimpa
isi folder ini (A12). Berkas turunan repo lama (`ref12S.fasta`, `ref12S_taksonomi.csv`,
`kelengkapan*.csv`, `voucher.csv`, `gbif_indonesia.csv`) sengaja **tidak** disalin.

Lisensi: mitohelper tidak mencantumkan lisensi (data dari GenBank dan MitoFish; sitasi Lim &
Thompson 2021). GenBank: kebijakan NCBI (https://www.ncbi.nlm.nih.gov/home/about/policies/).
GBIF: lisensi per dataset GBIF.
