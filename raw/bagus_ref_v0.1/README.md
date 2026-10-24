# Sumber mentah bagus_ref_v0.1 — tabel kurasi tim (sumber sekunder)

Asal: repo `BagusAth/BIOTRACE` (https://github.com/BagusAth/BIOTRACE), commit
`5a407e427ff3fe717b2c871209df02a28966b914`, folder `data/ref/v0.1/`. Disalin byte per byte pada
2026-10-25 (WIB) lewat cara manual `scripts/fetch_instructions.md` §6. SHA-256 setiap berkas cocok
dengan `manifest_sha256_rekan.txt` (salinan `data/ref/v0.1/manifest_sha256.txt` repo lama).

Ini **tabel kurasi tim, bukan file publikasi**. Perlakukan sebagai sumber sekunder (D-033).

| Berkas | Isi | Asal isi |
|---|---|---|
| `checklist_malili.csv` | spesies per danau (Matano, Mahalona, Towuti) atau tingkat kompleks, status endemik/introduksi/asli, sumber, tahun | Disusun agen (Claude) di repo lama sambil mengutip Kottelat 1990, 1991; Herder dkk. 2006; FEOW 750; Hedianto & Sentosa 2019; Mongabay 2018; Bisnis.com 2025; FishBase. **PDF/halaman sumber tidak diperiksa langsung**; pembagian spesies per danau perlu tinjauan ahli |
| `status.csv` | kategori IUCN, status invasif | Kategori IUCN dari GBIF species API (`species/{key}/iucnRedListCategory`, respons mentah di `raw/malili12s_mitohelper/gbif/gbif_species_indonesia.json`). Kolom invasif dari `sumber/invasif.csv`. Permen KP 19/2020 belum dicek |
| `alias.csv` | spesies/genus induk louhan → "louhan hibrida" | Disusun agen dari Audit Dataset tim; satu baris sinonim (*Vieja melanura*) perlu tinjauan ahli |
| `jalur_masuk.csv` | jalur introduksi dan kemungkinan sumber DNA lain | Disusun agen sambil mengutip Mongabay 2018 dan Hedianto & Sentosa 2019; ringkasan, bukan transkripsi |
| `sumber/invasif.csv` | daftar invasif bersumber | Disusun agen; penilaian "invasif" untuk ikan introduksi mengikuti kutipan di kolom `sumber`, belum dicek ke teks sumber |

Belum ada file sumber primer untuk baris-baris di atas di `raw/`. Baris yang dipakai di kamus
wajib bertanda `source_quality = sekunder` (sumber ilmiah) atau `berita` (Mongabay, Bisnis.com).
