# v0.3

Dari v0.2 (D-032) + data repo BagusAth/BIOTRACE commit 5a407e4 (docs/13, D-034). Aturan r0.4 (D-033). Semua ambang usulan tim, belum dikalibrasi ahli.

## Sekuens (896 aksesi kandidat Malili dari mitohelper 12S Juli 2026)
- Diterima: 65 sekuens unik dari 38 spesies (V2 23, V3 42); 39 aksesi digabung sebagai duplikat (R-CUR-07); 12 bertanda konflik lintas spesies (R-CUR-08).
- Asal spesimen yang diterima: {'Australia': 1, 'Bangladesh': 2, 'Brazil': 1, 'Canada': 1, 'China': 3, 'Colombia': 3, 'Czech Republic': 1, 'Guinea-Bissau': 1, 'Japan': 5, 'Namibia': 1, 'Tanzania': 6, 'Thailand': 1, 'USA': 1, 'United Kingdom': 1, 'kosong': 37}. Spesimen luar Indonesia/asal kosong bertanda specimen_outside_indonesia; klaim yang hanya bertumpu padanya tidak pernah safe (R-DEC-09).
- Ditolak/ditandai menurut alasan:
  - accepted identical_cross_species: 12
  - flagged no_mifish_region: 277
  - flagged unknown_name: 53
  - rejected no_voucher: 244
  - rejected origin_not_verified_ID: 218
- no_voucher: tanpa /specimen_voucher dan semua REFERENCE berupa Unpublished/Direct Submission/tesis. Dicatat di curation_report.csv, tidak di sequences.csv, karena enum voucher_level tidak punya nilai yang benar untuk kasus ini.

## Checklist, status, alias
- Semua baris v0.2 tetap (source_quality primer). Baris tabel tim masuk sebagai source_quality sekunder (sumber ilmiah, file belum di raw/) atau berita (Mongabay, Bisnis.com). Baris tingkat Kompleks Malili diterapkan ke Matano, Mahalona, Towuti. Duplikat terhadap baris primer dicatat di notes baris primer.
- Spesies endemik di checklist: 19; spesies endemik dengan sekuens diterima: 0.
- Nama tidak dinormalisasi: Pterygoplichthys pardalis (tabel tim/GenBank) terpisah dari Pterygoplichthys cf. pardalis dan Lyposarcus pardalis (v0.2); perlu tinjauan ahli.
- Status: kategori IUCN lewat GBIF; invasive_flag hanya bila kolom sumber tabel tim menyebut sumber. Permen KP 19/2020 belum dicek.
- Alias louhan: hanya nama spesies induk dari tabel tim (reviewed_by_expert=false); baris tingkat genus tidak dipakai karena mesin mencocokkan alias per spesies.
- jalur_masuk.csv tabel tim tidak diimpor (tanpa tingkat danau; ringkasan, bukan transkripsi); introductions.csv tetap dari v0.2.
