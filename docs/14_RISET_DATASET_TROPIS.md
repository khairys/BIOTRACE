# 14 — Riset sumber data ikan tropis dan Indonesia

Tanggal: 25 Oktober 2026 (WIB). Pemeriksa: Claude Code. Status: **riset eksplorasi**, bukan data kamus. Angka di bawah dihitung langsung dari API sumber pada tanggal ini dan belum dikurasi (nama belum dinormalisasi, "12S" bisa mencakup fragmen 12S–16S yang tidak mencakup daerah MiFish). Jangan dipakai di pitch sebelum dijalankan ulang lewat jalur kurasi dan dicatat di 07.

## 1. Angka celah yang diukur

| Ukuran | Hasil | Sumber/cara |
|---|---|---|
| Spesies ikan air tawar tercatat di Indonesia | 1.302 (1.152 asli, 109 endemik, 20 introduksi) | FishBase v25.04 tabel `country`, `Freshwater = 1` |
| …yang punya 12S/mitogenom dari spesimen bertanda Indonesia | 134 | GenBank `[country]` + nama FishBase |
| …yang hanya punya dari spesimen Malaysia/Singapura | 27 | idem |
| Endemik air tawar (109) dengan 12S/mitogenom dari negara mana pun | 31 | GenBank per spesies |
| …dari spesimen bertanda Indonesia | 11 | idem |
| …dengan COI | 40 | idem |
| Spesies air tawar Malaysia yang juga tercatat di Indonesia | 459 dari 654 (70%) | FishBase |
| Spesies air tawar Singapura yang juga tercatat di Indonesia | 119 dari 163 | FishBase |
| *Telmatherina*: rekaman 12S/mitogenom | 46, **0 bertanda negara Indonesia** | GenBank: kolom negara sering kosong; asal harus dibuktikan dari paper |

Contoh endemik tanpa 12S sama sekali: *Adrianichthys kruyti*, *A. poptae*, *A. roseni*, *Glossogobius matanensis*, *G. mahalonensis*, *Chilatherina sentaniensis*, *Glossamia timika*.

## 2. Sumber yang bisa diambil OTOMATIS

| Sumber | Isi relevan | Ukuran (diukur) | Jalur akses | Lisensi | Peran di BioTrace |
|---|---|---|---|---|---|
| **NCBI GenBank** | 12S, mitogenom, voucher, negara | ID: 879 rekaman 12S/mito, 404 spesies; MY: 498/140; SG: 207/101 | E-utilities (esearch/efetch), tanpa akun; API key opsional | Kebijakan NCBI (tanpa batasan, tanpa jaminan hak pihak ketiga) | Sumber sekuens utama |
| **BOLD v5 portal** | COI + voucher museum, koordinat | ID: 11.083 rekaman, 1.635 spesies, 1.742 BIN; MY: 4.056/581; SG: 182/101 | `portal.boldsystems.org/api/query` → `api/documents/<id>/download` (TSV). API data v4 sudah offline | Per rekaman; umumnya publik | Lapis celah "hanya COI", daftar voucher untuk sekuensing ulang 12S |
| **GBIF** | Okurensi, spesimen museum, checklist | ID: 279.087 okurensi ikan, 119.626 spesimen museum, 6.083 spesies; MY: 57.031; SG: 27.262 | API search tanpa akun (catatan: backbone GBIF baru tidak memberi kelas pada ikan; hitung lewat ordo) | Per dataset (CC0/CC BY/CC BY-NC) | Bukti keberadaan per wilayah (`sekunder`), voucher |
| **FishBase v25.04** | Daftar spesies per negara dan provinsi, status endemik/introduksi, habitat, sinonim | 216 tabel parquet | HuggingFace `cboettig/fishbase` | **CC BY-NC 4.0** (non-komersial) | Penyebut checklist dan status (`sekunder`). Pemakaian komersial perlu izin |
| **Mitohelper** (Lim & Thompson) | 12S dan multi-gen dari MitoFish/GenBank | ±2,2 GB (rilis Nov 2025) | [Zenodo 17602902](https://zenodo.org/records/17602902), GitHub | Cek di rekaman Zenodo | Kandidat sekuens global; disaring ke spesies tercatat di Indonesia |
| **Pustaka 12S MiFish rCRUX + MitoFish** | 12S V5–V6 MiFish | ±27,5 MB (Nov 2025) | [Zenodo 17664847](https://zenodo.org/records/17664847) | Cek di rekaman Zenodo | Pembanding dan pelengkap daerah MiFish |
| **rCRUX MiFish + FishCARD** (Gold dkk. 2023) | 12S MiFish global | — | [doi:10.5281/zenodo.8409239](https://doi.org/10.5281/zenodo.8409239) | Cek di rekaman Zenodo | Idem |
| **Jurnal Indonesia via OAI-PMH** | Metadata artikel, tautan PDF | Endpoint aktif: Jurnal Iktiologi Indonesia, Biodiversitas, Treubia, BIOTROPIA | `…/oai?verb=ListRecords` (diuji: `Identify` 200) | Metadata terbuka; PDF per lisensi jurnal | Daftar paper ikan → aksesi GenBank, checklist, voucher |
| **Aksesi dari dataset terkunci** | Nomor aksesi publik pada nama file | BRIN RIN/H6VXUK (ikan sungai Kalimantan): PQ661148–PQ661153, PV034314–PV034316, mitogenom *Bagroides melapterus* voucher BR002 | File dataset dibatasi, tetapi aksesinya diunduh dari GenBank | GenBank | Sekuens Kalimantan dengan voucher |
| **MitoFish** | Mitogenom ikan + MiFish pipeline | — | [mitofish.aori.u-tokyo.ac.jp](https://mitofish.aori.u-tokyo.ac.jp/) (unduhan batch) | Cek ketentuan situs | Sumber mitogenom |

## 3. Sumber yang PERLU TINDAKAN MANUAL

| Sumber | Kenapa manual | Tindakan Anda |
|---|---|---|
| **I-MarFish** (DB MiFish ikan laut Indonesia, 8.370 sekuens, [GitHub](https://github.com/mdaniealmalik/Curated-Metabarcoding-Database-for-Marine-Fish-in-Indonesia)) | Repo publik **tanpa lisensi** = hak cipta penuh | Minta izin tertulis pemilik. Sementara itu sekuensnya bisa dibangun ulang dari GenBank memakai daftar aksesinya, dengan sitasi |
| **Herder dkk. 2006, Kottelat 1990/1991** (checklist endemik Malili) | PDF di balik login/penerbit | Unduh PDF ke `raw/checklists/`; agent mengekstrak, manusia mengecek |
| **Kurniawan dkk. 2025** (eDNA MiFish 8 sungai Jawa, [KMAE](https://www.kmae-journal.org/articles/kmae/full_html/2025/01/kmae240134/kmae240134.html)) | FASTQ dijanjikan di BRIN; pencarian BRIN tidak menemukannya | Email penulis |
| **Balantak, Sulteng** (Rev Biol Trop 2026) | Aksesi tidak ditemukan | Minta FASTA/ASV ke penulis |
| **eDNA Danau Matano (ANEMONE, Juni 2026)** | Belum publik | Kerja sama institusi (USU/UNHAS/PT Vale); jangan klaim kemitraan sebelum ada |
| **Perak River, Malaysia** (Ali dkk. 2026, [GECCO](https://researchportal.hw.ac.uk/en/publications/fish-diversity-and-invasive-species-detection-in-the-perak-river-/)) | Pernyataan ketersediaan data belum terbaca | Buka artikel penuh; minta data bila tidak publik |
| **BRIN RIN/H6VXUK** (file lengkap, termasuk dataset spesies dan COI) | Akses terbatas | Ajukan permintaan akses di data.brin.go.id |
| **IUCN Red List API** | Perlu token | Daftar akun IUCN dan buat token |
| **Unduhan GBIF besar** (asinkron) | Perlu akun GBIF | Buat akun; search API kecil tetap otomatis |
| **Catalog of Fishes** | Tanpa API, ketentuan melarang scraping | Cek nama valid manual untuk spesies prioritas |
| **Lisensi komersial FishBase** | Data CC BY-NC | Hubungi FishBase bila produk komersial memakai tabelnya |
| **Spesimen bervoucher baru** (LIPI/BRIN–MZB) | Data fisik belum ada | Kemitraan museum (aset inti jangka panjang) |

## 4. Urutan kerja yang disarankan

1. **Penyebut dulu.** Bangun daftar target per pulau/perairan dari FishBase (`country`, `countrysub`) dan GBIF, diberi `source_quality = sekunder`. Tanpa penyebut, celah tidak bisa diukur.
2. **Panen sekuens untuk daftar target.** GenBank (12S + mitogenom, dengan voucher/negara), Mitohelper dan pustaka MiFish rCRUX. Semua melewati R-CUR (potong MiFish, level voucher, asal spesimen).
3. **Lapis COI dan voucher.** BOLD v5 untuk spesies target: memberi lapis "hanya COI" dan daftar spesimen museum untuk diprioritaskan sekuensing 12S.
4. **Jurnal Indonesia.** Panen metadata OAI-PMH, saring artikel ikan, ekstrak aksesi/checklist/voucher (semi-otomatis, wajib cek manusia). Sumber ini menutup kolom negara GenBank yang kosong.
5. **Tetangga Sundaland.** Sudah ikut di langkah 2 dengan negara spesimen; usulan r0.5: tingkat asal ID > Sundaland (MY/SG/BN) > lainnya.
6. **Manual paralel.** Izin I-MarFish, PDF checklist, data penulis, token IUCN.

Implementasi langkah 1–4 perlu dataset baru di `scripts/fetch_data.py` (A13). Kerjakan setelah PR penggabungan data Bagus masuk, karena file itu sedang diubah di branch `data/merge-bagus`.

## 5. Catatan metode eksplorasi

- GenBank: `Actinopterygii[Organism] AND "<negara>"[country] AND (12S … OR mitochondrion[filter] AND 15000:20000[SLEN])`; nama spesies dari `esummary.organism`, tanpa "sp."/"cf.".
- FishBase: `country.parquet` `C_Code` 360 (ID), 458 (MY), 702 (SG), `Freshwater = 1`; nama dari `species.parquet` (Genus + Species), tanpa normalisasi sinonim.
- Pencocokan nama FishBase–GenBank bersifat literal, sehingga cakupan bisa sedikit terlalu rendah karena perbedaan sinonim.
