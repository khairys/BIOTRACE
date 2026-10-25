# 07 — Registri Bukti dan Dataset (Ringkas untuk Repo)

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Versi lengkap | `07_REGISTRI_BUKTI.md` di Project GENOHACK (memuat daftar pencarian manual, tautan induk, dan referensi lengkap) |
| Aturan | Teks UI, laporan, dan README hanya boleh memakai klaim berstatus **Terverifikasi** di §2.1, dengan sumbernya (AGENTS.md A9) |

Status: **Terverifikasi** (sumber primer dibuka) · **Ditunda** (jangan dipakai) · **Internal** (data tim, wajib berlabel).

## 2. Registri klaim

### 2.1 Klaim yang boleh dipakai

| # | Klaim | Angka | Sumber | Jenis | Status | Kalimat yang disarankan |
|---|---|---|---|---|---|---|
| C01 | Kekayaan ikan air tawar asli Indonesia | 1.172 spesies | Hubert N. dkk. 2015, *DNA Barcodes* 3:144–169, https://doi.org/10.1515/dna-2015-0018 | Peer-reviewed | Terverifikasi | "Indonesia punya 1.172 spesies ikan air tawar asli." |
| C02 | Cakupan pustaka barcode Jawa–Bali | 1.046 barcode COI, 159 spesies; 36% spesies Jawa, 60% spesies Bali | Dahruddin H. dkk. 2017, *Mol Ecol Resour* 17(2):288–299, https://doi.org/10.1111/1755-0998.12528 | Peer-reviewed | Terverifikasi | "Pustaka DNA ikan Jawa baru mencakup sekitar sepertiga spesies, dan itu pun marker COI, bukan 12S yang dipakai eDNA." |
| C03 | Kondisi riset eDNA air tawar Indonesia | 28 dari 106 studi memenuhi syarat; 86% di Jawa dan Sumatra Barat; COI 39%, 12S 36%; MiFish-U 14%; referensi buruk, minim cek ahli | Dwipayana I.D.A.P., Febryanti N.L.P.K., Ramona Y. 2026, *BIOTROPIA* 33(3):403–412, https://doi.org/10.11598/btb.2026.33.3.2639 | Review peer-reviewed | Terverifikasi (abstrak) | "86% studi eDNA air tawar Indonesia ada di Jawa dan Sumatra Barat; kamus referensinya disebut buruk." |
| C04 | Kinerja penyedia eDNA komersial di sungai tropis | 4 perusahaan; false negative 32–92%; false positive 20–59% (sebelum analisis ulang); 33–40% setelah analisis ulang | Roussel J.-M. dkk. 2026, bioRxiv, https://doi.org/10.64898/2026.03.15.711554 | **Preprint** | Terverifikasi (teks v2) | "Studi 2026 (preprint) di sungai tropis Guyana Prancis: hingga lebih dari separuh nama dari penyedia komersial tidak ada di lokasi." |
| C05 | Rekomendasi Roussel | Pengguna harus menuntut jaminan mutu minimum; inventaris komersial butuh pengawasan spesialis; database referensi tersertifikasi | Roussel 2026 | Preprint | Terverifikasi | "Penulisnya merekomendasikan jaminan mutu minimum dan pengawasan ahli." |
| C06 | Label referensi salah mengubah kesimpulan | 2 dari 5 spesies "bukti invasi lintas samudra" di Terusan Panama ternyata salah identifikasi karena label BOLD keliru | Schreiber L. dkk. 2023, koreksi di *Ecology and Evolution*, https://doi.org/10.1002/ece3.10697 | Koreksi jurnal | Terverifikasi | "Di Terusan Panama, dua dari lima 'bukti invasi' ternyata salah nama karena kamus yang salah label." |
| C07 | Skor keyakinan sudah ada sebagai metode publik | Skor 0–5, ambang < 2,5 = rendah; data ikan laut global, marker teleo | Polanco F. A. dkk. 2025, *Environmental DNA* 7(2):e70077, https://doi.org/10.1002/edn3.70077 | Peer-reviewed | Terverifikasi | Dipakai sebagai dasar metode, bukan klaim inovasi |
| C08 | AI tidak menutup celah kamus | Model zero-shot ≈24% benar di tingkat spesies untuk spesies yang tidak ada di referensi (dari >31.000 kemungkinan); penulis menduga lebih buruk pada radiasi in situ | Stalder S. dkk. 2025, *PLOS Comp Biol* 21(12):e1013776, https://doi.org/10.1371/journal.pcbi.1013776 | Peer-reviewed | Terverifikasi | "Model AI terbaik hanya menebak benar sekitar seperempat spesies yang tidak ada di kamus." |
| C09 | Kamus lokal bisa dibangun | Guyana Prancis: 1.557 sekuens 12S, 369 spesies (88,92%), 51 famili, dari 1.439 spesimen (>25 ekspedisi) + 118 spesimen museum | *Scientific Data* 13:408 (2026), https://doi.org/10.1038/s41597-026-06811-5 | Peer-reviewed | Terverifikasi | "Guyana Prancis membuktikan kamus hampir lengkap bisa dibangun, tetapi butuh lebih dari 25 ekspedisi." |
| C10 | Celah referensi makin besar ke arah tropis | Kualitatif; Eropa: 64% dari 627 spesies tanpa 12S | Marques V. dkk. 2021 (GAPeDNA), *Divers Distrib* 27:1880–1892, https://doi.org/10.1111/ddi.13142 | Peer-reviewed | Terverifikasi (Eropa via Marques) | "Celah kamus DNA ikan membesar ke arah tropis." |
| C11 | Kurasi referensi publik dibutuhkan | PhyloRef menandai 597 sekuens Actinopterygii dan 9 Chondrichthyes | Mai dkk. 2026, *Ecol Evol* 16(3):e73159, https://doi.org/10.1002/ece3.73159 | Peer-reviewed | Terverifikasi | — |
| C12 | Sekuens Malili tersedia (Telmatherinidae) | 12S–16S KJ667771–KJ667865; ND2 KJ667866–KJ667963 | Stelbrink B. dkk. 2014, *BMC Evol Biol* 14:94, https://doi.org/10.1186/1471-2148-14-94 | Peer-reviewed | Terverifikasi (PMC) | — |
| C13 | Flowerhorn di Danau Matano | Survei 134 titik (2010) + 9 titik ulang (2012) | Herder F. dkk. 2012, *Aquatic Invasions* 7(4):521–535 | Peer-reviewed | Terverifikasi (rincian dominasi di Mahalona/Towuti masih sekunder) | "Louhan hibrida invasif sudah tercatat di Danau Matano." |
| C14 | Danau Matano sudah disampel eDNA | 14 titik, 1–6 Juni 2026; USU, UNHAS, PT Vale, Tohoku; protokol ANEMONE; data belum publik | USU News, 17 Juni 2026, https://www.usu.ac.id/en/news/usu-unhas-and-pt-vale-collaboration-advances-biodiversity-monitoring-in-lake-matano | Rilis institusi | Terverifikasi | "Danau Matano sudah mulai dipantau dengan eDNA pada 2026." **Jangan** menyiratkan kerja sama dengan pihak-pihak ini |
| C15 | Audit IRMA Sorowako | Komitmen 17 Des 2024; on-site oleh ERM CVS 1–5 Des 2025; >400 persyaratan; laporan publik akan terbit | IRMA, https://responsiblemining.net/2025/11/05/erm-cvs-to-conduct-on-site-irma-assessment-of-pt-vale-indonesia-tbks-sorowako-mine/ | Rilis | Terverifikasi | — |
| C16 | KPI pinjaman PT Vale belum memuat biodiversitas | SLL USD 750 juta (+USD 250 juta greenshoe), 14 bank; KPI: intensitas karbon dan energi terbarukan | Jakarta Post, 7 Mei 2026, https://www.thejakartapost.com/business/2026/05/07/pt-vale-secures-750-million-esg-linked-syndicated-loan-facility.html | Berita | Terverifikasi | Dipakai internal sebagai bukti "belum wajib" |
| C17 | Kredit biodiversitas Indonesia | Feb 2026 kemitraan Indonesia–Inggris; Apr 2026 tiga skema (wajib, offset, sukarela); 15 Sep 2026 workshop dengan prinsip integritas ilmiah; 26 Sep 2026 draf Permen LH | KLH/BPLH dan Ecobiz (lihat §7) | Pemerintah/berita | Terverifikasi (isi draf tidak publik) | "Pemerintah sedang menyiapkan aturan kredit biodiversitas berprinsip integritas ilmiah." |
| C18 | Nature disclosure tumbuh | 836 organisasi berkomitmen TNFD; aset kelolaan > USD 26 triliun; ISO menyetujui standar berbasis LEAP | ESG Today, 16 Okt 2026, https://www.esgtoday.com/over-800-companies-commit-to-tnfd-aligned-nature-reporting-ahead-of-new-issb-iso-standards/ | Berita | Terverifikasi | — |
| C19 | Pembeli kredit diminta memeriksa galat | BCA menyarankan memeriksa "documented error rates" dan "how uncertainty is handled"; waspada model kotak hitam | Biodiversity Credit Alliance, Feb 2026, https://www.biodiversitycreditalliance.org/wp-content/uploads/2026/02/BC-Metrics_20240226_v5.pdf | Laporan | Terverifikasi | "Pasar kredit biodiversitas mulai menuntut tingkat galat yang terdokumentasi." |
| C20 | Pemain global eDNA | NatureMetrics: Series B USD 25 juta (Jan 2025); >600 klien di >110 negara; posisi untuk pelaporan TNFD/CSRD/SBTN | ESG Today, https://www.esgtoday.com/biodiversity-data-provider-naturemetrics-raises-25-million/ | Berita | Terverifikasi | — |
| C21 | Kasus biaya keputusan berbasis eDNA | Ikan mas Asia, Chicago 2009–2012: peracunan kanal ±100.000 pon ikan tanpa ikan target; gugatan sampai Mahkamah Agung AS (ditolak); >USD 100 juta untuk upaya pengendalian; perdebatan inti soal keandalan bukti eDNA | Notre Dame Environmental Change Initiative (2012), https://environmentalchange.nd.edu/news-events/news/fish-barrier-vs-carp-dna-what-to-believe/ | Berita institusi | Terverifikasi | "Hasil eDNA pernah menggerakkan ratusan juta dolar dan sampai ke pengadilan, dengan pertanyaan inti: seberapa bisa dipercaya?" |
| C22 | Pasar eDNA global | USD 1,51 miliar (2026) → 3,04 miliar (2031), CAGR 14,9% | MarketsandMarkets, https://www.marketsandmarkets.com/PressReleases/environmental-dna.asp | Laporan komersial | Terverifikasi (pakai sebagai batas atas) | "Pasar eDNA global sekitar USD 1,5 miliar (2026)." |
| C23 | Skala validasi eDNA | 5 level; meta-analisis 546 assay dari 327 paper | Thalinger B. dkk. 2021, *Environmental DNA*, https://doi.org/10.1002/edn3.189 | Peer-reviewed | Terverifikasi | — |
| C24 | Isi snapshot kamus aktif | v0.5: 999 sekuens layak teknis, 630 nama spesies berreferensi, 133 sekuens dari spesimen Indonesia; endemik Malili 0/19 | `data/reference/v0.5/manifest.json`, `validation/jury/v0.5/release_checks.json`, `data_quality.json` | Inventaris internal dari file sumber lokal | Terverifikasi (komputasional, D-038) | "Snapshot v0.5 memuat 999 sekuens; identitas/status belum mendapat tinjauan ahli." Bukan klaim cakupan nasional lengkap |
| C25 | Alur pada data eDNA asli Indonesia | 4.354 klaim, 152 taksa, 39 lokasi; aman 0, catatan 1.685, verifikasi 1, jangan dipakai 2.668; run v0.5 277,507 detik | `precomputed/edna_asli_marwayana2022_r0.4_v0.5/`; Dryad 10.5068/D12T1B (Marwayana 2022), CC0 | Pemrosesan internal data publik asli | Terverifikasi (run dan hash, D-038) | "Alur berjalan pada data asli; hasil ini belum menjadi pengukuran akurasi lapangan Malili." |
| C26 | LOSO pustaka MiFish r0.4 lama | M3 v0.3 Malili 6/65 vs baseline 30/65; CA-QC 46/234 vs baseline 98/234 | `validation/results/2026-10-25_MALILI_r0.4.json`, `2026-10-25_LSP_r0.4.json` | Eksperimen internal pada data pustaka nyata | Terverifikasi (file hasil run) | Sebutkan marker/kamus/aturan. M1 nol struktural pada pustaka tanpa spesimen Indonesia bukan bukti keamanan; bukan akurasi lapangan |
| C27 | LOSO lengkap kamus v0.5 | 630 spesies, 999 query: M1 0/999, M2 924/999, M3 75/999 vs baseline 325/999; M4 120/589, M5 458/589 | `validation/results/2026-10-25_ID_v0.5_r0.4.json` | Eksperimen pustaka internal, MiFish, r0.4 | Terverifikasi (run lengkap dan hash) | "Pada uji pustaka internal v0.5, M3 7,51% vs baseline 32,53%; M2 92,49%." Sertakan M4/M5 dan penyebut; bukan akurasi lapangan atau nol risiko |

Hasil lokal C24–C27 harus selalu disebut sebagai inventaris atau pengujian internal, disertai versi dan keterbatasan. "Terverifikasi komputasional" berarti file/run dapat diperiksa, bukan pengesahan taksonomi atau validasi ahli.

### 2.2 Ditunda (jangan dipakai)

| # | Klaim | Alasan |
|---|---|---|
| X01 | "Sekitar 630 spesies endemik" | Belum ditemukan di teks primer Hubert 2015 (K-002) |
| X02 | "4 → 34 spesies disepakati semua penyedia" | Sumber berbeda pendapat (K-001) |
| X03 | Pasar eDNA "USD 5,61 miliar, CAGR 10,2%" | Tidak konsisten secara matematis |
| X04 | Angka pasar Indonesia (SAM/SOM di deck v2) | Belum ada data harga lokal; tunggu ≥5 wawancara |
| X05 | eDNA diterima/diwajibkan AMDAL, RKL-RPL, PROPER | Belum diverifikasi |
| X06 | Harga jasa eDNA lab Indonesia | Belum ditemukan |
| X07 | Status regulasi ABS/Nagoya untuk database spesimen | Belum diverifikasi |
| X08 | *Pterygoplichthys* dan halfbeak di Malili | Belum diverifikasi |

### 2.3 Wajib dengan label

| # | Klaim | Label wajib |
|---|---|---|
| L01 | 41% spesies tersembunyi tetap diberi nama lain pada ≥97%; 83% kerabat satu genus | "Simulasi internal tim, kamus ikan laut I-MarFish, belum terbit" |
| L02 | Ambang 97% meloloskan 52% nama keliru; aturan BioTrace 16% | Sama dengan L01 |
| L03 | 5 dari 17 OTU data Nanopore UNDIP tidak bisa dibedakan sampai spesies | "Analisis ulang tim atas data pipeline DBP UNDIP" |
| L04 | 40 dari 41 kontrol negatif di 14 danau berisi bacaan ikan | Li dkk. 2019 (sumber primer perlu dicek ulang sebelum dipakai) |

---

## 3. Inventaris dataset

Prioritas: **1** = Malili/Sulawesi, **2** = Indonesia, **3** = Asia Tenggara, **4** = validasi luar.

| # | Dataset | Grup | Wilayah | Marker | Isi | Akses / aksesi | Voucher | Peran untuk BioTrace | Prioritas |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stelbrink dkk. 2014 | Barcode spesimen | Malili | 12S–16S, ND2 | Sekuens Telmatherinidae | GenBank KJ667771–KJ667865 (12S–16S), KJ667866–KJ667963 (ND2); https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4029975/ | Cek (ZSM/LIPI) | **Kandidat referensi Malili #1** (cek overlap MiFish) | 1 |
| 2 | Herder dkk. 2006 (Proc R Soc B) | Barcode spesimen | Malili | mtDNA + AFLP | Haplotipe | Aksesi di ESM (belum dibuka); https://pmc.ncbi.nlm.nih.gov/articles/PMC1635519/ | Cek | Referensi + bukti hibridisasi | 1 |
| 3 | Revisi taksonomi *Oryzias* Malili 2026 | Genomik | Malili | SNP | Taksonomi baru, introgresi | https://doi.org/10.1186/s12862-026-02529-5 | Cek | Nama valid + anggota kompleks | 1 |
| 4 | Checklist Telmatherinidae (Herder 2006) & ikan introduksi (Herder 2012) | Checklist | Malili | — | Daftar spesies asli dan asing | https://www.semanticscholar.org/paper/46d68554f8667959ba28fc47f111b97c1e36c628 ; https://www.researchgate.net/publication/232708663 | NA | `checklist.csv`, `introductions.csv` | 1 |
| 5 | Tantu & Nilawati 2007 | Checklist | Matano | — | Ikan eksotik | https://www.researchgate.net/publication/370417162 | NA | `introductions.csv` | 1 |
| 6 | Data eDNA Matano (ANEMONE, Juni 2026) | eDNA | Matano | belum diketahui | 14 titik | Belum publik | Tidak | Uji strategis beachhead | 1 (manual) |
| 7 | Balantak, Sulawesi Tengah (Rev Biol Trop 74(1):e20263754, 2026) | eDNA | Sulteng | 12S MiFish | ASV; MitoFish 97/99% | https://doi.org/10.15517/hp29s516 ; https://revistas.ucr.ac.cr/index.php/rrbt/article/view/3754 ; aksesi tidak ditemukan | Tidak | Data uji Sulawesi (minta FASTA/ASV ke penulis) | 1 |
| 8 | Barcode dua endemik karst Maros | Barcode | Sulsel | cek | Sekuens | https://zenodo.org/records/16955951 | Cek | Referensi | 2 |
| 9 | Hubert dkk. 2015 | Checklist | Indonesia | — | Checklist nasional 1.172 spesies | https://doi.org/10.1515/dna-2015-0018 | NA | Penyebut Paper 1 | 2 |
| 10 | Dahruddin dkk. 2017 | Barcode | Jawa–Bali | COI | 1.046 barcode + Tabel S1 (xlsx checklist) | https://doi.org/10.1111/1755-0998.12528 ; proyek BOLD BIFB, BIFC, BIFGA, BIFHB (dari pernyataan data, halaman BOLD belum dibuka) | MZB? | Daftar voucher untuk sekuensing 12S ulang; lapis celah "hanya COI" | 2 |
| 11 | Kurniawan dkk. 2025 (KMAE 426:17) | eDNA | 8 sungai Jawa | MiFish-U | Checklist + jumlah reads; FASTQ dijanjikan di BRIN | https://doi.org/10.1051/kmae/2025009 ; https://data.brin.go.id/dataverse/RestorasiEkosistemPerairan | Tidak | Data uji Jawa | 2 |
| 12 | Rawa Pening (Asian Fisheries Science 39:111–122, 2026) | eDNA | Jateng | eDNA | 34 taksa + survei visual | https://www.asianfisheriessociety.org/publication/downloadfile.php?id=1489&file=Y0dSbUx6QTJNVEUzT0RVd01ERTNPREkzT1RBek56RXVjR1Jt | Tidak | Uji danau | 2 |
| 13 | Dwipayana dkk. 2026 | Review | Indonesia | — | Daftar 28 studi | https://journal.biotrop.org/index.php/biotropia/article/view/2639 | NA | Daftar benih dataset | 2 |
| 14 | Porong (2024); spons eDNA (Kuncoro 2026); Ciliwung (PJOES) | eDNA | Jawa | eDNA | Variasi | https://www.sciencedirect.com/science/article/pii/S2666765724000528 ; https://scholar.its.ac.id/en/publications/freshwater-sponges-as-natural-edna-samplers-for-biodiversity-asse/ ; https://www.pjoes.com/Environmental-DNA-Biomonitoring-in-Urban-nRiver-Ecosystem-A-Ciliwung-River-Case-Study,184633,0,2.html | Tidak | Rendah | 3 |
| 15 | Rainbowfish (Kadarusman 2012); *Hemirhamphodon*; Rasborinae Sundaland | Barcode | Papua/Sundaland | COI | Barcode | https://doi.org/10.1371/journal.pone.0040627 ; https://doi.org/10.1371/journal.pone.0163596 ; https://doi.org/10.1038/s41598-020-59544-9 | Cek | Ekspansi | 3 |
| 16 | Lake St. Pierre (Astorg dkk. 2025) | Validasi | Kanada | 12S | FASTQ 2,94 GB + CSV deteksi + electrofishing | https://datadryad.org/dataset/doi:10.5061/dryad.3bk3j9kzf | NA | Uji presisi vs tangkapan | 4 |
| 17 | Pustaka 12S Guyana Prancis | Validasi | Guyana Pr. | 12S (Teleo1/12S-V5) | 1.557 sekuens, 369 spesies | Figshare https://doi.org/10.6084/m9.figshare.29168144 ; GenBank PX415477–PX417033 ; PRJNA1399107 | Ya | LOSO tropis | 4 |
| 18 | Roussel dkk. 2026 | Validasi | Guyana Pr. | 12S | Inventaris lengkap 50 spesies + data 4 perusahaan | https://doi.org/10.64898/2026.03.15.711554 ; data & kode: https://zenodo.org/records/19880312 | Tangkapan | Validasi komersial | 4 |
| 19 | Trawl metaprobe | Validasi | Laut | 12S Tele02/Elas02 | FASTQ + kontrol | https://doi.org/10.5061/dryad.s7h44j1g3 | NA | Uji penanganan kontrol | 4 |

---

## 4. Catatan untuk agent

- Unduh dataset dengan `python scripts/fetch_data.py all` (atau manual: `scripts/fetch_instructions.md`). Agent mengkurasi hasilnya (04 §5).
- Setiap dataset yang masuk repo wajib punya entri `sources.csv` dan `README.md` di foldernya, berisi sumber, lisensi, tanggal unduh.
- Dataset prioritas 4 hanya boleh ditaruh di `data/external/` (aturan A4).
