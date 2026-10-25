# 16 — Panen data ikan tropis Indonesia: sumber, cara, dan hasil `[P1]`

Tanggal: 25 Oktober 2026 (WIB). Dikerjakan otomatis oleh Claude Code atas instruksi Agathan (P3 di docs/15). Branch: `integrasi/main-bagus`.

> Status: **eksplorasi dan pengumpulan bahan mentah**, bukan kamus berversi. Tidak ada sekuens baru yang masuk `data/reference/`. Kamus berikutnya (v0.4) harus dibangun dari bahan ini lewat jalur kurasi R-CUR, dicatat di 09 sebagai Diusulkan, dan ditinjau manusia/ahli.

## 1. Gambaran besar

```
                 ┌──────────── PENYEBUT (spesies apa yang seharusnya ada) ────────────┐
                 │ FishBase country/countrysub · GBIF okurensi & spesimen museum       │
                 │ Regulasi KKP (dilindungi, invasif) · checklist literatur (manual)    │
                 └───────────────────────────────┬─────────────────────────────────────┘
                                                 │ daftar spesies target (nama dari file sumber, A14)
   ┌────────────── SEKUENS (bukti referensi) ────▼──────────────────────────────────────┐
   │ GenBank 12S + mitogenom: per negara tropis & per spesies target                     │
   │ GenBank untuk aksesi yang dikutip paper ikan Indonesia (Europe PMC)                 │
   │ BOLD v5 COI (lapis "hanya COI" + voucher museum) · Pustaka MiFish rCRUX (Zenodo)    │
   └───────────────────────────────┬─────────────────────────────────────────────────────┘
                                   │ uji daerah MiFish (trim_mifish) + tingkat asal spesimen
   ┌──────────── PENEMUAN (sumber lanjutan) ▼───────────────────────────────────────────┐
   │ OAI-PMH 10 jurnal Indonesia · Europe PMC · BRIN RIN · Zenodo/Dryad/Figshare · SRA   │
   └───────────────────────────────┬─────────────────────────────────────────────────────┘
                                   ▼
          data/curation/tropis_gap_v1/: cakupan per spesies, prioritas barcode,
          daftar artikel, daftar dataset, kandidat spesimen Indonesia dari paper,
          tautan FASTQ eDNA Indonesia
```

Tingkat asal spesimen dipakai untuk menilai kekuatan referensi (selaras D-033 / R-DEC-09):

| Tingkat | Negara (kualifier GenBank `country`/`geo_loc_name`) |
|---|---|
| 1_ID | Indonesia |
| 2_Sundaland | Malaysia, Singapura, Brunei |
| 3_Wallacea_Sahul | Timor-Leste, Papua Nugini, Filipina |
| 4_Asia_Tenggara_daratan | Thailand, Vietnam, Kamboja, Laos, Myanmar |
| 5_lain | negara lain |
| 6_asal_tidak_diketahui | kualifier kosong (sering spesimen Indonesia tanpa label, mis. *Telmatherina*) |

## 2. Cara menjalankan ulang

```bash
uv run --no-project --with pyarrow python scripts/fetch_data.py --list
uv run --no-project --with pyarrow python scripts/fetch_data.py tropis_fishbase tropis_genbank_country tropis_genbank_freshwater tropis_genbank_marine
uv run --no-project python scripts/fetch_data.py tropis_bold tropis_gbif tropis_oai tropis_sra tropis_regulasi tropis_europepmc tropis_brin tropis_brin_files tropis_repositori tropis_obis tropis_zenodo_mifish tropis_literatur
uv run --no-project python scripts/fetch_data.py tropis_genbank_cited
uv run --no-project --with pyarrow --with pydantic --with pyyaml --with pymupdf --with numpy python scripts/analyze_tropis.py
```

- Semua unduhan lewat `scripts/fetch_data.py` (A13); kode panen di `scripts/harvest_tropis.py`.
- Setiap dataset ditulis ke folder baru `raw/tropis/<dataset>/<tanggal>/` (A12). Unduhan bisa dilanjutkan: file yang sudah tercatat di manifest dilewati.
- `manifest.json` per folder mencatat kueri persis, URL, lisensi yang dilaporkan sumber, waktu, jumlah record, dan SHA-256 lengkap tiap file. **Hanya manifest yang dikomit**; berkas besar di-gitignore dan diunduh ulang dengan perintah di atas.
- Jumlah record setiap batch GenBank diverifikasi terhadap jumlah dari server; batch tidak lengkap dianggap galat. FishBase diverifikasi ke hash LFS HuggingFace; Zenodo ke MD5 Zenodo.
- NCBI: jeda 0,4 detik (< 3 permintaan/detik tanpa API key), percobaan ulang hingga ±7 menit.

## 3. Sumber OTOMATIS dan hasil panen

| Dataset (`fetch_data.py`) | Sumber dan cara | Lisensi dilaporkan | Hasil 25 Okt 2026 |
|---|---|---|---|
| `tropis_fishbase` | FishBase v25.04 parquet (HuggingFace `cboettig/fishbase`): country, countrysub, countref, species, synonyms, families, genera, orders, ecosystemcountry | **CC BY-NC 4.0** | 9 tabel (30 MB); Indonesia 5.099 baris negara |
| `tropis_genbank_country` | E-utilities: `Actinopterygii[Organism] AND "<negara>"[country] AND (12S … OR mitogenom 14–20 kb)` untuk 12 negara | Kebijakan NCBI | lihat manifest (ID 2.647; PH 1.317; VN 602; MY 561; SG 515 …) |
| `tropis_genbank_freshwater` | Sama, per spesies air tawar/payau Indonesia versi FishBase (60 nama per kueri) | Kebijakan NCBI | lihat manifest |
| `tropis_genbank_marine` | Sama, spesies laut Indonesia versi FishBase | Kebijakan NCBI | lihat manifest |
| `tropis_genbank_cited` | GenBank untuk aksesi yang disebut di artikel ikan Indonesia (dari `tropis_europepmc`), disaring Actinopterygii | Kebijakan NCBI | lihat manifest |
| `tropis_bold` | BOLD v5 portal: satu unduhan global `tax:class:Teleostei` (TSV), negara disaring lokal | Per rekaman BOLD | 423.278 rekaman global |
| `tropis_gbif` | GBIF occurrence facet per spesies (semua record + PRESERVED_SPECIMEN) untuk 7 negara + nama dari species API | Per dataset penerbit | 7 negara (ID, MY, SG, BN, TL, PG, PH); 8.350 nama spesies |
| `tropis_oai` | OAI-PMH `ListRecords` oai_dc: Jurnal Iktiologi Indonesia, Biodiversitas, Treubia, BIOTROPIA, Limnotek, Zoo Indonesia, Berita Biologi, Marine Research in Indonesia, OLDI, JITKT IPB | Metadata terbuka; PDF per lisensi jurnal | 10/11 jurnal (Ilmu Kelautan Undip gagal `ListRecords`) |
| `tropis_europepmc` | Europe PMC search (artikel OA ikan Indonesia + GenBank/BOLD) + Annotations API (`Accession Numbers`) | Metadata terbuka | 3.206 artikel OA, 3.183 PMCID, 53.240 aksesi nukleotida unik disebut |
| `tropis_sra` | BioProject eDNA ikan Indonesia + ENA filereport (URL FASTQ, MD5) | Data INSDC publik | 7 BioProject, 135 run, 147 FASTQ (9,7 GB) |
| `tropis_brin` | BRIN Repositori Ilmiah Nasional (Dataverse search + datasets API) | Per dataset | 64 dataset DNA ikan (metadata + daftar file terbuka/terkunci) |
| `tropis_brin_files` | File **terbuka** (PDF/tabel/sekuens/dokumen, ≤ 50 MB) dari dataset BRIN lewat Dataverse access API | Per dataset | 50 file (282 file terbuka total, sisanya gambar/terlalu besar) |
| `tropis_obis` | OBIS API v3 checklist Actinopteri area Indonesia (115) dan Indonesian Sea LME (40038) | Per dataset penerbit | 4.411 takson unik area Indonesia (OBIS melaporkan total 4.522) |
| `tropis_iucn` | IUCN Red List API v4 `/countries/ID` (butuh env `BIOTRACE_IUCN_TOKEN`) | Ketentuan IUCN (non-komersial) | siap dijalankan setelah token ada (M10) |
| `tropis_repositori` | Zenodo (AND, type=dataset), Dryad v2 search, Figshare search (9 kueri wilayah) | Per dataset | Zenodo 14, Dryad 31 unik, Figshare per kueri |
| `tropis_regulasi` | Kepmen KP 1/2021 (dilindungi), Permen KP 19/2020 (Berita Negara 829, membahayakan/invasif), Kepmen KP 83/2024 (belida jawa) | Peraturan, bukan ciptaan dilindungi (UU 28/2014 Ps. 42) | 3 PDF |
| `tropis_zenodo_mifish` | Zenodo 17664847: pustaka 12S MiFish rCRUX nt + MitoFish (Nov 2025) | CC BY 4.0 | 5 file |
| `tropis_zenodo_mitohelper` | Zenodo 17602902 Mitohelper (±2,2 GB) | lihat Zenodo | opsional, belum dijalankan |
| `tropis_literatur` | Literatur yang dihosting terbuka penerbit | Hak cipta penulis | Herder 2006: hanya 2 halaman pratinjau |

## 4. Sumber yang PERLU TINDAKAN MANUAL (siap unduh/ajukan)

| # | Sumber | Kenapa manual | Tautan langsung | Simpan ke |
|---|---|---|---|---|
| M1 | Kottelat 2013, *The Fishes of the Inland Waters of Southeast Asia: a catalogue* (Raffles Bull. Zool. Suppl. 27: 1–663) — checklist air tawar SE Asia termasuk Indonesia barat | Situs LKCNHM memakai proteksi anti-bot (Incapsula) | https://lkcnhm.nus.edu.sg/volumes/supplement-no-27-2013/ | `raw/checklists/` |
| M2 | Herder dkk. 2006, checklist Telmatherinidae Malili (Verh. Ges. Ichthyol. 5: 139–163) — **teks lengkap** | Situs GfI hanya pratinjau 2 halaman | https://www.ichthyologie.de/wp-content/uploads/2019/11/Preliminary_checklist_of_sailfin_silversides.pdf (pratinjau); teks lengkap lewat perpustakaan/penulis; arsip lama zfmk.de di Wayback Machine | `raw/checklists/` |
| M3 | Hubert dkk. 2015, *DNA Barcodes* 3: 144–169 (checklist nasional 1.172 spesies) | De Gruyter memblokir unduhan otomatis | https://doi.org/10.1515/dna-2015-0018 | `raw/checklists/` |
| M4 | Kottelat dkk. 1993, *Freshwater Fishes of Western Indonesia and Sulawesi* (buku) | Buku cetak; tidak ada PDF terbuka | perpustakaan/LIPI–BRIN | catatan halaman |
| M5 | Lampiran **Permen KP 19/2020** (daftar jenis ikan membahayakan/invasif) | PDF berupa gambar pindaian; perlu transkripsi | sudah terunduh: `raw/tropis/regulasi/2026-10-25/permen_kp_19_2020_jenis_ikan_membahayakan_bn829.pdf` | transkripsi ke `data/curation/` |
| M6 | Dataset Dryad: **Mitogenom Rasborinae Sundaland** (10.5061/dryad.tb2rbp00g), **Barcode Jawa–Bali** (10.5061/dryad.tk5rj), **Hibridisasi kuno danau Sulawesi** (10.5061/dryad.8cz8w9gr2), **Biota akuatik Sundaland** (10.5061/dryad.3xsj3txrf), **Fluktuasi Pleistosen SE Asia** (10.5061/dryad.rn8pk0p7s), **eDNA terumbu Indonesia** (10.5068/D12T1B), **eDNA Coral Triangle** (10.5061/dryad.t1g1jwt05), **eDNA hyper-diverse** (10.5061/dryad.sqv9s4n6f) | API unduhan Dryad membalas 401 (diuji pada Lake St. Pierre) | `https://doi.org/<DOI>` → tombol Download | `raw/<dataset>/` + log |
| M7 | Daftar lengkap dataset repositori | — | `data/curation/tropis_gap_v1/repository_datasets.csv` | pilih yang relevan |
| M8 | FASTQ eDNA Indonesia (7 BioProject, 9,7 GB) | Besar; pengolahan FASTQ → ASV adalah F33 [P2] | `data/curation/tropis_gap_v1/edna_fastq_indonesia.tsv` (URL ENA + MD5) | `raw/sra/` |
| M9 | Dataset BRIN yang **terkunci** | Perlu permintaan akses ke pemilik | `data/curation/tropis_gap_v1/brin_rin_datasets.csv` (kolom `files_restricted`) | — |
| M10 | Token **IUCN Red List API v4** (status terancam) | Perlu akun | https://api.iucnredlist.org/ | env `BIOTRACE_IUCN_TOKEN` |
| M11 | **NCBI API key** (panen 10 req/detik) | Perlu akun NCBI | https://account.ncbi.nlm.nih.gov/settings/ | env, opsional |
| M12 | Akun **GBIF** untuk unduhan asinkron besar | Perlu akun | https://www.gbif.org/user/profile | opsional |
| M13 | Izin **I-MarFish** (8.370 sekuens MiFish laut Indonesia, repo tanpa lisensi) | Hak cipta pemilik | https://github.com/mdaniealmalik/Curated-Metabarcoding-Database-for-Marine-Fish-in-Indonesia | izin tertulis |
| M14 | Lisensi komersial **FishBase** | Data CC BY-NC | https://www.fishbase.se/ (kontak) | — |
| M15 | Ilmu Kelautan Undip (OAI `ListRecords` gagal) | Server menolak/terlalu lambat | https://ejournal.undip.ac.id/index.php/ijms/oai?verb=Identify | jalankan ulang `tropis_oai` |
| M16 | Catalog of Fishes (validasi nama) | Tanpa API; ketentuan melarang scraping | https://researcharchive.calacademy.org/research/ichthyology/catalog/fishcatmain.asp | cek manual spesies prioritas |
| M17 | Data penulis: Kurniawan dkk. 2025 (eDNA Jawa), Balantak 2026, eDNA Matano (ANEMONE) | Belum publik | email penulis/institusi | — |

## 5. Hasil analisis celah

Diisi dari `data/curation/tropis_gap_v1/summary.json` setelah panen selesai (lihat §5 versi terbaru di bawah atau file itu langsung).

## 6. Bagaimana sumber-sumber ini ditemukan (jejak kerja agent)

1. **Mulai dari kebutuhan mesin.** BioTrace butuh (a) penyebut: daftar spesies per perairan dengan status; (b) referensi 12S MiFish dengan asal spesimen. Setiap sumber dinilai terhadap dua kebutuhan ini.
2. **Ukur dulu sebelum mengunduh.** Hitungan langsung lewat API (esearch GenBank per negara, statistik BOLD, facet GBIF, FishBase parquet) untuk melihat skala dan celah (docs/14).
3. **Kejar penyebab celah.** Temuan *Telmatherina* 46 rekaman tetapi 0 berlabel Indonesia → asal spesimen harus dibuktikan dari paper → Europe PMC Annotations API (aksesi yang disebut di teks artikel OA) dan OAI-PMH jurnal Indonesia.
4. **Telusuri penerbit Indonesia secara sistematis.** Daftar jurnal BRIN diambil dari indeks `ejournal.brin.go.id`, lalu setiap endpoint OAI diuji dengan `verb=Identify` sebelum dipanen.
5. **Repositori data.** BRIN RIN (Dataverse API), Zenodo/Dryad/Figshare (API pencarian) untuk dataset yang tidak masuk GenBank. Dataset terkunci tetap berguna: nama file sering memuat aksesi publik.
6. **Data lapangan nyata.** BioProject/SRA dengan kata kunci Indonesia + eDNA + ikan → ENA filereport untuk URL FASTQ dan MD5.
7. **Status hukum.** Pencarian web untuk regulasi KKP; PDF diunduh dari situs pemerintah (bukan salinan pihak ketiga).
8. **Verifikasi setiap tautan.** Setiap URL diuji (kode HTTP, tipe isi, tanda tangan `%PDF`); situs berproteksi anti-bot tidak diakali dan dipindah ke daftar manual.
9. **Bug yang ditemukan dan diperbaiki:** BOLD v5 mengabaikan filter geo pada `extent=full` (unduhan per negara identik) → satu unduhan global + saring lokal; NCBI efetch 5xx sementara → percobaan ulang diperpanjang; Zenodo membatasi `size` → 25 per halaman; satu jurnal OAI gagal tidak lagi menghentikan yang lain.

Alat yang dipakai: NCBI E-utilities, OBIS API, IUCN API v4 (dicek tanpa token), BOLD v5 portal API, GBIF API, HuggingFace API, Zenodo/Dryad/Figshare API, Europe PMC REST + Annotations API, ENA portal API, BRIN Dataverse API, OAI-PMH, pencarian web, pymupdf, pyarrow, numpy.

## 7. Batas dan risiko

- **Lisensi FishBase CC BY-NC**: aman untuk riset/prototipe; produk komersial perlu izin (M14).
- **Nama**: FishBase dan GenBank memakai taksonomi berbeda; pencocokan memakai nama + sinonim FishBase, tanpa tinjauan ahli. Sisa yang tidak cocok dicatat di `genbank_unmatched_organisms.csv`.
- **Asal spesimen**: kualifier negara GenBank sering kosong. Aksesi yang dikutip paper ikan Indonesia hanya **kandidat** spesimen Indonesia, karena paper juga mengutip pembanding dari negara lain.
- **"12S"** di kueri GenBank juga menangkap fragmen 12S–16S dan teks "small subunit ribosomal RNA"; setiap rekaman diuji daerah MiFish sebelum dihitung.
- **Kandidat regulasi** diekstrak otomatis dari teks PDF dan dicocokkan ke nama FishBase; wajib dicek terhadap lampiran (kolom `checked_by_human`).
- Ini bukan validasi ilmiah; angka cakupan menggambarkan ketersediaan data publik, bukan keberadaan ikan.

## 8. Unduhan manual yang sudah masuk (25 Okt 2026, ±07:10–07:30)

| Sumber (docs/16 §4) | Disimpan | Dipakai untuk | Hasil |
|---|---|---|---|
| M6 Rasborinae Sundaland (Dryad tb2rbp00g) | `raw/dryad_tb2rbp00g_rasborinae/` | **Kamus v0.5** (D-037) | 143 sekuens MiFish dari mitogenom; asal spesimen dicocokkan ke BOLD lewat kode voucher BIF (38/47 voucher = Indonesia, LIPI); 33 sekuens diterima; klaim *Rasbora* kini bisa `safe` pada tingkat genus |
| M6 Barcode Jawa–Bali (Dryad tk5rj) | `raw/dryad_tk5rj_jawabali/` | Lapis COI dan voucher | 1.046 spesimen COI dari 159 spesies, semuanya Indonesia (MZB/LIPI) menurut BOLD → `data/curation/jawabali_dahruddin2017_tk5rj/` |
| M6 Raja Ampat/Lengguru (Dryad sqv9s4n6f) | `raw/dryad_sqv9s4n6f_rajaampat/` (zip tidak dikomit, 324 MB) | Bahan checklist dan validasi | Checklist ikan laut Raja Ampat 2.534 baris; pustaka 12S **teleo** Lengguru 1.419 sekuens (bukan MiFish, tidak masuk kamus); daftar spesies UVC 402 dan eDNA 475 → `data/curation/rajaampat_juhel2022_sqv9s4n6f/` |
| M1 Kottelat 2013 | `raw/checklists/kottelat2013_raffles_suppl27.pdf` | Penyebut checklist (belum diekstrak) | 667 halaman, teks terbaca |
| M10 Token IUCN | — | Status terancam | Ditolak server (401); perlu aktivasi akun IUCN, lalu jalankan `tropis_iucn` |

Skrip: `scripts/import_manual_downloads.py` (ekstraksi ke `data/curation/`), `scripts/prepare_v05.py` (kamus v0.5).
