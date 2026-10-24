# Log Unduhan Data

| Dataset | File | URL | Tanggal | SHA-256 | Lisensi (isi manual) | Catatan |
|---|---|---|---|---|---|---|
| stelbrink2014 | stelbrink2014\stelbrink2014_12s16s.fasta | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi (KJ667771–KJ667865, fasta) | 2026-10-24 | 6895181a114e68a9… | ? | 95 aksesi |
| stelbrink2014 | stelbrink2014\stelbrink2014_12s16s.gb | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi (KJ667771–KJ667865, gb) | 2026-10-24 | d6f4a852be5c4df4… | ? | 95 aksesi |
| guyana12s | french_guiana_12s\Data_12S Ref library_Fish Guiana.csv | https://ndownloader.figshare.com/files/58389280 | 2026-10-24 | 7924d2370891443a… | ? | CC0 |

## Catatan audit 24 Oktober 2026 (WIB)

Baris otomatis di atas dipertahankan. Hash lengkap hasil pemeriksaan:

| File | SHA-256 | Lisensi/kebijakan akses |
|---|---|---|
| stelbrink2014/stelbrink2014_12s16s.fasta | 6895181a114e68a9a32b44851a03e311541dcc2cfe3d68aeb6ca2689fc8f4ebf | GenBank-public; lihat kebijakan NCBI dan sources.csv; belum penetapan hak pihak ketiga |
| stelbrink2014/stelbrink2014_12s16s.gb | d6f4a852be5c4df427cd27431f0cec1b506996bd3c6fe0d8393f78863a9410b7 | GenBank-public; lihat kebijakan NCBI dan sources.csv; belum penetapan hak pihak ketiga |
| french_guiana_12s/Data_12S Ref library_Fish Guiana.csv | 7924d2370891443a496a78f21fddae71c6a37c93bf04758077968927a0c6476f | CC0 (dataset; metadata penyedia dicatat terpisah) |
| french_guiana_12s/figshare_metadata.json | 8bb2b4bdc795886424eeafce88a0d74d60b55ef35424fbc02ef77e28a6727a0e | Metadata API Figshare; bukti lisensi CC0 dataset |

Metadata Figshare diambil oleh skrip dari https://api.figshare.com/v2/articles/29168144. Dataset CSV dari https://ndownloader.figshare.com/files/58389280; CC0 terkonfirmasi pada halaman dan metadata penyedia. Kebijakan NCBI: https://www.ncbi.nlm.nih.gov/home/about/policies/.

Unduhan Lake St. Pierre gagal pada https://datadryad.org/api/v2/files/4370610/download dengan HTTP 401; tidak ada file data yang tersimpan. Pemeriksaan HEAD ulang juga 401. FASTQ besar tidak diminta. Rincian pemeriksaan di AUDIT_2026-10-24.json. Tidak ada sumber yang diimpor ke kamus.

## Impor ZIP manual Lake St. Pierre

Sumber disediakan pengguna; DOI https://doi.org/10.5061/dryad.3bk3j9kzf; CC0 menurut kebijakan Dryad. Arsip dipindahkan ke `raw/lake_st_pierre/downloads/doi_10_5061_dryad_3bk3j9kzf__v20250924.zip`; SHA-256 `a741c2252a532c55cb3260bbba6134336a835ab36375117f0771b33917e31dd8`. Waktu impor 2026-10-24T22:38:19.209278+07:00.

- `raw/lake_st_pierre/v20250924/README.md`: `e0a69b28f373645d88e18556aac25689914488a7caae89332ff37eaa11765d1d`; CRC ZIP lulus saat ekstraksi.
- `raw/lake_st_pierre/v20250924/edna_env.csv`: `05dffe56d37190e4c55663d6cb89f7c34413274efa06e212156d296a7eee9aaa`; CRC ZIP lulus saat ekstraksi.
- `raw/lake_st_pierre/v20250924/edna_lg_clean.csv`: `7240a384ea566859216455a40adcb28ed1f2aea0abeddbd2f4b2d886e520af91`; CRC ZIP lulus saat ekstraksi.
- `raw/lake_st_pierre/v20250924/elec_env.csv`: `8fdc20daa36330398f5df0059291494aada7070103f4732699351e1331aa56b3`; CRC ZIP lulus saat ekstraksi.
- `raw/lake_st_pierre/v20250924/elec_long.csv`: `1bccfef945fc3a890a0c8d4aa159e1dab777e0ca3ed138fce1e97f8f47a62c96`; CRC ZIP lulus saat ekstraksi.
- `raw/lake_st_pierre/v20250924/fish_codes.csv`: `78ba86ceeea76f1b5a038d633b92237da81a15c8d9c1f0130060ff984db73c4b`; CRC ZIP lulus saat ekstraksi.
- `raw/lake_st_pierre/v20250924/raw_seq.zip`: `045dda292931b8fdc28a75b13f4990184b73fc6f76d75810fa090a631b3b5527`; CRC ZIP lulus saat ekstraksi.

## Unduhan manual pengguna 25 Oktober 2026 (WIB)

Diunduh manual oleh pengguna (Agathan) lalu dipindahkan agent dari akar repo ke `raw/checklists/`. PDF tidak dikomit ke Git (hak cipta pihak ketiga; `.gitignore`), hanya hash berikut. Byte file tidak diubah.

| File | Sumber | SHA-256 | Lisensi/kebijakan |
|---|---|---|---|
| raw/checklists/herder2012_aquatic_invasions.pdf | Herder dkk. 2012, Aquatic Invasions 7(4):521–535 (corrected proof) | 3d31e7fce2fdd52bd0c9ae991469d95168b4679675a7583d00622e12dc27e2b9 | Open Access; © 2012 The Author(s) |
| raw/checklists/tantu_nilawati2007_exotic_fish_matano.pdf | Tantu & Nilawati 2007, Vol. 4 No. 7, ISSN 1829-7374 (PDF hasil pindai) | 12892c9a2c4fb0da020004b02a67c15bd1e4570c3a966261582f295f0725e226 | tidak diketahui |

`Data_12S Ref library_Fish Guiana.csv` yang juga diunduh ulang ke akar repo identik (MD5 5b34a6eaeed4a8a1220be8f72321f208) dengan `raw/french_guiana_12s/`; salinan duplikat di akar dihapus. Herder dkk. 2006 (checklist Telmatherinidae) tidak berhasil diunduh dan belum tersedia.

Tabel hasil ekstraksi: `data/curation/malili_introduced_v0.2/transcription.csv` (Herder 2012 Appendix 1 + teks; Tantu 2007 Tabel 1 hlm. 33, dibaca dari gambar halaman karena OCR rusak). Setiap baris perlu dicek manusia terhadap PDF.
