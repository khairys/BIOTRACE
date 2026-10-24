# 07 — Registri Bukti, Dataset, dan Sumber (Lengkap)

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Lokasi | Project GENOHACK (lengkap). Versi ringkas untuk repo: `docs/07_REGISTRI_BUKTI_RINGKAS.md` |
| Dasar | Riset web dan literatur sesi 24 Oktober 2026 (Scite, web) + laporan deep research "deep research final" |
| Aturan | Hanya klaim berstatus **Terverifikasi** yang boleh dipakai di pitch, UI, dan paper (01 §8) |

---

## 1. Cara memakai dokumen ini

- **Tim pitch**: ambil angka hanya dari §2.1, pakai kalimat yang disarankan, dan sebut sumbernya.
- **Tim data**: ambil dataset dari §3 sesuai prioritas di §6.
- **Siapa pun yang menemukan bukti baru**: tambahkan baris dengan status, sumber, dan tanggal cek. Jangan mengubah status menjadi "Terverifikasi" tanpa membuka sumber primernya.

Status: **Terverifikasi** (sumber primer dibuka) · **Sekunder** (dari sumber yang mengutip) · **Ditunda** (sumber tidak sepakat / belum ditemukan) · **Internal** (data tim, belum terbit).

---

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

## 4. Taksonomi, checklist, dan basis data acuan

| Sumber | Kegunaan | Tautan |
|---|---|---|
| Catalog of Fishes (California Academy of Sciences) | Nama valid, sinonim | https://researcharchive.calacademy.org/research/ichthyology/catalog/fishcatmain.asp |
| FishBase | Sebaran, status | https://www.fishbase.se |
| GBIF | Okurensi, catatan spesimen museum | https://www.gbif.org |
| IUCN Red List | Status ancaman | https://www.iucnredlist.org |
| NCBI GenBank / Batch Entrez | Unduh sekuens | https://www.ncbi.nlm.nih.gov/nuccore ; https://www.ncbi.nlm.nih.gov/sites/batchentrez |
| NCBI SRA | Data mentah | https://www.ncbi.nlm.nih.gov/sra |
| BOLD Systems | Barcode COI, proyek | https://www.boldsystems.org |
| MitoFish / MiFish pipeline | Referensi 12S ikan | Zhu T. dkk. 2023, https://doi.org/10.1093/molbev/msad035 |
| BRIN Dataverse | Data riset Indonesia | https://data.brin.go.id |

---

## 5. Daftar pencarian manual

| # | Apa | Mengapa | Prioritas | Cara | Tautan |
|---|---|---|---|---|---|
| M01 | Data eDNA Matano 2026 (ANEMONE) | Uji beachhead, cerita paling kuat | Tinggi | Email LPPM UNHAS / LPPM USU, tawarkan analisis ulang gratis dengan NDA | Lihat C14 |
| M02 | Laporan audit IRMA Sorowako | Bukti kebutuhan; cek bab biodiversitas | Tinggi | Pantau halaman IRMA dan Vale; tanya IRMA (Director of Assurance) atau ERM CVS | https://responsiblemining.net/2024/12/17/pt-vale-indonesia-commits-sorowako-to-irma-audit/ ; https://vale.com/indonesia/irma-audit |
| M03 | FASTA/ASV studi Balantak | Uji Sulawesi | Tinggi | Email penulis korespondensi (UNHAS) | https://revistas.ucr.ac.cr/index.php/rrbt/article/view/3754 |
| M04 | FASTQ Kurniawan 2025 | Uji Jawa | Tinggi | Cek BRIN Dataverse; email penulis | https://data.brin.go.id/dataverse/RestorasiEkosistemPerairan |
| M05 | Aturan AMDAL/RKL-RPL soal data biota air dan eDNA | **Inti positioning D-003** | Tinggi | JDIH KLH; PP 22/2021 dan turunannya; wawancara konsultan penyusun AMDAL | — |
| M06 | Aturan akses sumber daya genetik / ABS / Nagoya | Legalitas kamus spesimen | Tinggi | JDIH; LPPM kampus mitra; BRIN | — |
| M07 | Voucher MZB/BRIN untuk ikan Malili | Level V1 | Tinggi | Surat ke pengelola koleksi BRIN Cibinong; cek GBIF | — |
| M08 | Aksesi Herder 2006 & *Oryzias* 2026 | Referensi Malili | Tinggi | Buka ESM / data availability | Lihat §3 #2–3 |
| M09 | Draf Permen LH kredit biodiversitas | Pendorong regulasi | Tinggi | Pantau konsultasi publik KLH | https://kemenlh.go.id/news/detail/klhbplh-matangkan-instrumen-kredit-keanekaragaman-hayati-berstandar-global |
| M10 | Harga jasa eDNA lokal | Benchmark harga | Tinggi | Minta penawaran ke 3–5 lab | — |
| M11 | Teks Permen KP 19/2020 | Daftar invasif | Sedang | JDIH KKP | — |
| M12 | Kottelat dkk. 1993 (buku) | Identifikasi ikan Indonesia barat & Sulawesi | Sedang | Perpustakaan BRIN/IPB/UNHAS | — |
| M13 | Daftar 28 studi Dwipayana | Benih pencarian dataset | Sedang | Unduh PDF | https://journal.biotrop.org/index.php/biotropia/article/view/2639 |
| M14 | Teks penuh Roussel (cek "4 → 34") | Pitch | Sedang | Teks penuh/suplemen bioRxiv | https://www.biorxiv.org/content/10.64898/2026.03.15.711554v2 |
| M15 | Kode proyek BOLD Dahruddin | Referensi COI | Sedang | Cari BIFB/BIFC/BIFGA/BIFHB di BOLD | https://www.boldsystems.org |
| M16 | Sumber primer "630 endemik" | Pitch | Sedang | Teks penuh Hubert 2015 | https://doi.org/10.1515/dna-2015-0018 |
| M17 | Dokumen resmi TNFD, IFC PS6, Equator Principles, EU Battery Regulation | Pendorong pasar | Sedang | Situs resmi | https://www.ifc.org/content/dam/ifc/doc/2010/20190627-ifc-ps-guidance-note-6-en.pdf |
| M18 | Fitur pesaing (NatureMetrics, Wilderlab, Jonah Ventures, SPYGEN, eDNAtec, EnviroDNA) | Positioning | Sedang | Situs + wawancara | — |
| M19 | Pembanding alat: FishCARD, RESCRIPt, BOLDigger, IDTAXA | Paper | Sedang | Literatur | — |
| M20 | Pendana barcoding (iBOL/BIOSCAN, GEF, BIOFIN, Darwin Initiative, KEHATI, BPDLH) | Flywheel | Sedang | Situs pendana | — |
| M21 | Halfbeak, gobi, *Pterygoplichthys* di Malili | Checklist | Sedang | Literatur Herder / von Rintelen | — |
| M22 | Sumber primer Li dkk. 2019 (40/41 kontrol negatif) | Pitch | Rendah | Cari paper | — |

---

## 6. Checklist unduhan berurutan

| Urutan | Unduh | Dari | Format | Untuk |
|---|---|---|---|---|
| 1 | KJ667771–KJ667865 | NCBI Batch Entrez | FASTA + GenBank flat file | T-DATA-01 |
| 2 | PDF Herder 2006 (checklist), Herder 2012, Tantu & Nilawati 2007 | Semantic Scholar / ResearchGate | PDF | T-DATA-03 |
| 3 | Pustaka 12S Guyana | Figshare 29168144 | FASTA + tabel | T-DATA-06 |
| 4 | Lake St. Pierre: `edna_lg_clean.csv`, `elec_long.csv`, `fish_codes.csv`, `README.md` | Dryad | CSV | T-DATA-05 |
| 5 | PDF Balantak; Zenodo Maros | UCR; Zenodo | PDF; file | Prioritas 1 |
| 6 | Tabel S1 Dahruddin; checklist Hubert 2015; lampiran Kurniawan; PDF Dwipayana | Wiley; De Gruyter; KMAE; BIOTROPIA | XLSX/PDF | Paper 1 |
| 7 | `raw_seq.zip` Lake St. Pierre (2,94 GB) | Dryad | FASTQ | `[P1]` |

---

## 7. Tautan induk

**Regulasi dan kebijakan Indonesia**
- KLH Feb 2026: https://kemenlh.go.id/news/detail/indonesia-siapkan-kebijakan-dan-implementasi-instrumen-high-integrity-biodiversity-credits-untuk-perkuat-pembiayaan-keanekaragaman-hayati
- KLH Apr 2026: https://kemenlh.go.id/news/detail/indonesia-percepat-implementasi-biodiversity-credit-untuk-perkuat-pembiayaan-konservasi-nasional
- KLH Sep 2026: https://kemenlh.go.id/news/detail/klhbplh-matangkan-instrumen-kredit-keanekaragaman-hayati-berstandar-global
- Draf Permen LH (Ecobiz): https://ecobiz.asia/klh-sudah-siapkan-draft-permen-lh-biodiversity-credit-cegah-praktik-makelar/
- Nikel.co.id 16 Sep 2026: https://nikel.co.id/2026/09/16/klh-matangkan-kredit-biodiversitas-sektor-tambang-berpotensi-terlibat/
- FGD Danau Matano (Sep 2026): https://www.inspirasitimur.com/2026/09/wujudkan-pengelolaan-danau-matano.html

**Pasar dan bisnis**
- IRMA (komitmen): https://responsiblemining.net/2024/12/17/pt-vale-indonesia-commits-sorowako-to-irma-audit/
- IRMA (on-site): https://responsiblemining.net/2025/11/05/erm-cvs-to-conduct-on-site-irma-assessment-of-pt-vale-indonesia-tbks-sorowako-mine/
- Pinjaman PT Vale: https://www.thejakartapost.com/business/2026/05/07/pt-vale-secures-750-million-esg-linked-syndicated-loan-facility.html
- TNFD adopsi: https://www.esgtoday.com/over-800-companies-commit-to-tnfd-aligned-nature-reporting-ahead-of-new-issb-iso-standards/
- BCA metrics: https://www.biodiversitycreditalliance.org/wp-content/uploads/2026/02/BC-Metrics_20240226_v5.pdf
- NatureMetrics: https://www.esgtoday.com/biodiversity-data-provider-naturemetrics-raises-25-million/
- MarketsandMarkets: https://www.marketsandmarkets.com/PressReleases/environmental-dna.asp
- IFC Guidance Note 6: https://www.ifc.org/content/dam/ifc/doc/2010/20190627-ifc-ps-guidance-note-6-en.pdf
- Kartzinel Lab (kredit biodiversitas & pustaka DNA): https://www.kartzinellab.com/news/biodiversity-credits-and-dna-reference-libraries
- Asian carp: https://environmentalchange.nd.edu/news-events/news/fish-barrier-vs-carp-dna-what-to-believe/

---

## 8. Daftar referensi ilmiah

1. Astorg L. dkk. (2025). eDNA metabarcoding to monitor fish communities in a large river floodplain. *Environmental DNA* 7(5):e70182. https://doi.org/10.1002/edn3.70182
2. Bajaffer dkk. Addressing false negatives and positives in eDNA studies. *Methods Ecol Evol*. https://doi.org/10.1111/2041-210x.70328
3. Brosse S. … Murienne J. (2026). Near complete 12S DNA reference library for the freshwater fish of French Guiana. *Scientific Data* 13:408. https://doi.org/10.1038/s41597-026-06811-5
4. Dahruddin H. dkk. (2017). Revisiting the ichthyodiversity of Java and Bali through DNA barcodes. *Mol Ecol Resour* 17(2):288–299. https://doi.org/10.1111/1755-0998.12528
5. Dwipayana I.D.A.P., Febryanti N.L.P.K., Ramona Y. (2026). Optimizing eDNA metabarcoding in Indonesian freshwaters: a scoping review of best practices. *BIOTROPIA* 33(3):403–412. https://doi.org/10.11598/btb.2026.33.3.2639
6. Herder F. dkk. (2006). Adaptive radiation and hybridization in Wallace's Dreamponds. *Proc R Soc B*. https://pmc.ncbi.nlm.nih.gov/articles/PMC1635519/
7. Herder F. dkk. (2006). Preliminary checklist of sailfin silversides in the Malili Lakes. *Verh Ges Ichthyol* 5:139–163.
8. Herder F. dkk. (2012). Alien invasion in Wallace's Dreamponds. *Aquatic Invasions* 7(4):521–535.
9. Hubert N. dkk. (2015). DNA barcoding Indonesian freshwater fishes: challenges and prospects. *DNA Barcodes* 3:144–169. https://doi.org/10.1515/dna-2015-0018
10. Kadarusman dkk. (2012). Cryptic diversity in Indo-Australian rainbowfishes. *PLoS ONE* 7:e40627. https://doi.org/10.1371/journal.pone.0040627
11. Kurniawan K. dkk. (2025). eDNA metabarcoding and local ecological knowledge… rivers of Java. *KMAE* 426:17. https://doi.org/10.1051/kmae/2025009
12. Mai Y. … Li C. (2026). PhyloRef. *Ecol Evol* 16(3):e73159. https://doi.org/10.1002/ece3.73159
13. Marques V. dkk. (2021). GAPeDNA. *Divers Distrib* 27:1880–1892. https://doi.org/10.1111/ddi.13142
14. (Penulis perlu dicek) (2026). eDNA exploration of fish diversity in the Balantak River. *Rev Biol Trop* 74(1):e20263754. https://doi.org/10.15517/hp29s516
15. Polanco F. A. dkk. (2025). A confidence scoring procedure for eDNA metabarcoding records. *Environmental DNA* 7(2):e70077. https://doi.org/10.1002/edn3.70077
16. Roussel J.-M. dkk. (2026). Variable performances of commercial eDNA inventories challenge their use for surveying stream fish communities. *bioRxiv*. https://doi.org/10.64898/2026.03.15.711554 **[preprint]**
17. Ruiz dkk. (2026). Benchmarking taxonomic resolution of fish eDNA metabarcodes against COI. *Mol Ecol Resour*. https://doi.org/10.1111/1755-0998.70069
18. Schreiber L. dkk. (2023). Correction to "eDNA reveals potential for interoceanic fish invasions across the Panama Canal". *Ecol Evol*. https://doi.org/10.1002/ece3.10697
19. Sioud dkk. (2026). ANEMONE Global's first eDNA-based assessment. *Environmental DNA* 8. https://doi.org/10.1002/edn3.70252
20. Stalder S. dkk. (2025). Zero-shot deep learning for the annotation of unknown eDNA sequences. *PLoS Comput Biol* 21(12):e1013776. https://doi.org/10.1371/journal.pcbi.1013776
21. Stelbrink B. dkk. (2014). Age estimates for an adaptive lake fish radiation… Malili Lakes. *BMC Evol Biol* 14:94. https://doi.org/10.1186/1471-2148-14-94
22. Thalinger B. dkk. (2021). A validation scale to determine the readiness of eDNA assays for routine species monitoring. *Environmental DNA*. https://doi.org/10.1002/edn3.189
23. Zhu T. dkk. (2023). MitoFish, MitoAnnotator, and MiFish pipeline: updates in 10 years. *Mol Biol Evol* 40(3). https://doi.org/10.1093/molbev/msad035
24. Revised taxonomy… ancient lake ricefishes (2026). *BMC Ecol Evol*. https://doi.org/10.1186/s12862-026-02529-5
25. Introgresi sungai–danau sailfin silversides (2025). *bioRxiv*. https://doi.org/10.1101/2025.04.16.648611 **[preprint]**
