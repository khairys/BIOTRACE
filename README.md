# BioTrace Indonesia

**Pemeriksa fakta untuk hasil eDNA ikan Indonesia.**

BioTrace memeriksa setiap nama ikan dari hasil lab eDNA (metabarcoding 12S MiFish) terhadap kamus DNA berversi dan aturan yang tertulis. Untuk setiap nama, BioTrace menentukan tingkat nama yang didukung bukti, nilai bukti A–D, penyebab ketidakpastian, dan satu dari empat keputusan: **Aman dilaporkan**, **Dengan catatan**, **Wajib verifikasi**, atau **Jangan dipakai**. Setiap laporan memiliki jejak audit yang bisa diverifikasi ulang.

> BioTrace menghasilkan **laporan verifikasi pendukung**, bukan dokumen AMDAL resmi. Deteksi DNA bukan bukti pasti ikan hidup di lokasi. Semua ambang adalah usulan tim dan belum dikalibrasi ahli taksonomi.

---

## Mengapa BioTrace

eDNA memungkinkan survei ikan hanya dari sampel air: lab menyaring DNA, memperbanyak potongan gen 12S dengan primer MiFish, membacanya, lalu mencocokkannya ke kamus DNA. Masalahnya, penamaan spesies hanya seandal kamus itu. Kamus DNA ikan Indonesia masih banyak celahnya. Bila spesies yang benar belum ada di kamus, pencocokan biasa (misalnya BLAST dengan ambang ≥97%) tetap memberi nama spesies lain yang paling mirip, dengan yakin. Nama keliru itu bisa masuk ke laporan pemantauan dan dokumen lingkungan.

BioTrace tidak menebak. Bila bukti tidak cukup, nama diturunkan ke tingkat yang aman (spesies → kompleks → genus → "tidak dikenal") dan alasannya dituliskan. Setiap "tidak dikenal" menjadi masukan untuk daftar prioritas barcode, yaitu ikan yang perlu dibaca DNA-nya berikutnya.

## Fitur utama

- **Penamaan yang jujur**: tingkat nama aman, nilai A–D, empat keputusan, dan tindak lanjut tertulis untuk setiap klaim (pasangan ASV × lokasi).
- **Evidence Card**: kartu bukti per klaim berisi nama dari lab dan nama aman, kandidat, skor L1/L2/L4, penyebab, voucher pendukung, asal-usul, dan alasan dalam Bahasa Indonesia dan Inggris.
- **Unggah fleksibel**: kolom CSV/TSV dikenali otomatis (mis. `otu_id`, `site_name`, `waterbody`, `pident`); perairan dan marker yang kosong dipilih pengguna, bukan ditebak.
- **Kamus berversi**: sekuens 12S MiFish dengan level voucher, checklist ikan per perairan, status IUCN/invasif, dan alias hibrida; setiap versi dikunci dengan SHA-256.
- **Peta celah dan prioritas barcode**: per genus per perairan, berapa spesies tercatat dibanding yang sudah punya referensi.
- **Jejak audit**: sidik jari SHA-256 dari input, versi kamus, aturan, dan engine; laporan bisa diverifikasi lewat kode sidik jari.
- **Laporan**: PDF lengkap, ringkasan PDF, CSV/ZIP, catatan peninjau ahli, pencocokan ulang ke versi kamus lain, dan perbandingan antar-run.
- **Lokal dan offline**: tidak ada machine learning dan tidak ada panggilan internet saat analisis; hasil deterministik.

## Cara kerja

```
CSV/TSV/FASTA ─► pengenalan kolom + validasi input
                    │
                    ▼
  Tahap 0  Pra-proses     format panjang, filter data nyasar (tag-jumping), kontrol negatif, klaim ASV × lokasi
  Tahap 1  Penamaan       BLAST+ lokal ke kamus berversi (atau taksonomi dari lab) → tingkat nama aman
  Tahap 2  Penilaian      L1 kamus (0–2) + L2 lokasi (0–1) + L4 sinyal lab (0–2) → nilai A–D; L3 = label status
  Tahap 3  Penyebab       reference · marker · sample · location
  Tahap 4  Keputusan      safe · with_note · must_verify · do_not_use, beserta tindak lanjut
  Tahap 5  Asal-usul      kemungkinan sumber DNA lain (hulu, keramba, pasar)
  Tahap 6  Celah          peta kelengkapan kamus + daftar prioritas barcode
  Tahap 7  Audit          SHA-256 input dan versi, sidik jari laporan
                    │
                    ▼
  runs/<run_id>/   claims.csv · summary.json · report.pdf · run_manifest.json · validation_report.json
```

| Lapis | Dasar penilaian | Aturan (r0.4) |
|---|---|---|
| L1 Kamus (0–2) | Kemiripan terbaik dan selisih ke kandidat di luar jendela 0,5% | 2 bila ≥99% dan selisih ≥1,0%; 1 bila ≥98% dan selisih ≥0,5%; dikurangi 1 bila <50% spesies segenus di perairan itu sudah punya referensi |
| L2 Lokasi (0–1) | Checklist ikan perairan | 1 bila takson tercatat di perairan klaim |
| L3 Label | Checklist, status IUCN/invasif, alias | Endemik, terancam, invasif, hibrida; tidak menambah skor tetapi mengetatkan keputusan |
| L4 Sinyal lab (0–2) | Replikat positif per lokasi | 2 bila muncul di semua replikat; 1 bila ≥66% atau hanya satu replikat |
| Batas D | Kontrol negatif dan jumlah bacaan | Nilai D bila DNA juga ada di kontrol negatif batch yang sama atau total bacaan <10 |

Total L1+L2+L4: 5 = A, 4 = B, 2–3 = C, 0–1 = D. Klaim yang hanya didukung spesimen dari luar Indonesia atau checklist bersumber sekunder tidak pernah diberi keputusan "Aman". Rincian aturan: [`docs/03_ATURAN_MESIN.md`](docs/03_ATURAN_MESIN.md).

## Mulai cepat

**Prasyarat:** [uv](https://docs.astral.sh/uv/) (memasang Python 3.11 otomatis), Node.js 22 + npm, dan NCBI BLAST+ 2.14+. Di Windows, BLAST+ dipasang otomatis ke `.tools/` oleh perintah `setup`.

```bash
git clone https://github.com/khairys/BIOTRACE.git
cd BIOTRACE
uv run python scripts/project.py setup
uv run python scripts/project.py demo
```

Buka http://127.0.0.1:8000, lalu pilih:

- **Muat data eDNA asli Indonesia**: data MiFish-U terumbu karang Indonesia (Marwayana dkk. 2022), memakai hasil pra-hitung terverifikasi sehingga langsung tampil.
- **Muat data demo (SIMULASI)**: skenario Danau Matano fiktif yang memperlihatkan keempat keputusan, kompleks spesies, dan alias hibrida.

> Di Windows, jalankan perintah `uv` dari PowerShell. Biarkan laptop tetap aktif selama analisis BLAST berjalan.

## Menggunakan BioTrace

### Lewat dashboard

1. **Unggah** tabel bacaan, metadata sampel, dan FASTA ASV atau taksonomi lab. Peran tiap file dan nama kolomnya dikenali otomatis.
2. Bila metadata tidak mencantumkan perairan atau marker, **pilih** di kotak "Lengkapi metadata". Pilihan ini tercatat di jejak audit.
3. Baca **ringkasan keputusan**, lalu buka **Evidence Card** lewat tombol **Lihat bukti** di daftar klaim.
4. Unduh **PDF** (lengkap atau ringkasan) atau **CSV/ZIP**, lalu salin sidik jari laporan untuk diperiksa di halaman **Verifikasi**.

### Format data input

| File | Wajib | Kolom utama |
|---|---|---|
| Tabel bacaan (CSV/TSV) | Ya | `asv_id`, `sample_id`, `reads` (format panjang), atau format lebar: kolom pertama ASV, kolom lain sampel |
| Metadata sampel | Ya | `sample_id`, `site_id`, `waterbody_id`, `sample_type`, `replicate`, `extraction_batch`, `marker`; opsional `latitude`, `longitude`, `collection_date` |
| FASTA ASV | Salah satu | `>asv_id` diikuti urutan; dicocokkan ulang ke kamus BioTrace dengan BLAST+ |
| Taksonomi lab | Salah satu | `asv_id`, `taxon`, `rank`, `pct_identity`, opsional `runner_up_taxon`, `runner_up_pct_identity` |

Nama kolom lain dikenali lewat sinonim atau isinya, kolom tambahan diabaikan, dan semua pemetaan dilaporkan sebagai peringatan. Templat tersedia di [`templates/`](templates/). Spesifikasi lengkap: [`docs/04_SPESIFIKASI_DATA.md`](docs/04_SPESIFIKASI_DATA.md).

### Lewat baris perintah

```bash
uv run biotrace run --reads reads.csv --meta metadata.csv --taxonomy taxonomy.csv --out runs
uv run biotrace run --reads reads.csv --meta metadata.csv --fasta asv.fasta --ref data/reference/v0.5 --out runs
uv run biotrace verify --run runs/<run_id>
uv run biotrace validate loso --ref data/reference/v0.5 --out loso.json
```

Subperintah lain: `rematch` (cocokkan ulang ke kamus/aturan lain), `compare` (bandingkan dua run), `gaps` (gabungkan celah lintas run), `ref` (kelola kamus).

### Lewat API

API FastAPI berjalan bersama dashboard; dokumentasi interaktif tersedia di http://127.0.0.1:8000/docs.

| Endpoint | Fungsi |
|---|---|
| `POST /api/inputs/inspect` | Kenali peran file dan pemetaan kolom |
| `POST /api/runs` | Jalankan analisis (opsional `waterbody_id`, `marker` untuk sel kosong) |
| `GET /api/runs/{id}` | Hasil lengkap; turunan `/claims`, `/coverage`, `/barcode-priority`, `/sites` |
| `GET /api/runs/{id}/report.pdf`, `/summary.pdf`, `/export.zip` | Laporan dan ekspor |
| `POST /api/runs/{id}/rematch`, `GET /api/runs/{id}/compare/{other}` | Cocok ulang dan banding run |
| `POST /api/verify` | Periksa laporan dari sidik jari |
| `GET /api/reference`, `/api/methods`, `/api/validation/latest` | Isi kamus, metode, hasil validasi |

## Kamus referensi dan data

| Komponen | Isi | Lokasi |
|---|---|---|
| Kamus aktif v0.5 | 999 sekuens 12S MiFish dari 630 spesies (133 dari spesimen Indonesia); checklist Danau Malili, laut, dan air tawar Indonesia; status IUCN/invasif; alias | [`data/reference/v0.5`](data/reference/v0.5) |
| Kamus sebelumnya | v0.1–v0.4, dipertahankan agar hasil lama bisa direproduksi | [`data/reference/`](data/reference/) |
| Data eDNA asli | Marwayana dkk. 2022, MiFish-U, 39 lokasi terumbu Indonesia (Dryad 10.5068/D12T1B, CC0) | [`data/edna_asli/`](data/edna_asli/) |
| Data demo | Skenario Danau Matano, berlabel SIMULASI di nama file dan setiap baris | [`data/demo/`](data/demo/) |
| Modul validasi luar | Lake St. Pierre (Kanada), Guyana Prancis; hanya untuk uji mesin | [`data/external/`](data/external/) |
| Data mentah | Unduhan bersumber, hash SHA-256, dan log unduhan | [`raw/`](raw/), [`raw/DOWNLOAD_LOG.md`](raw/DOWNLOAD_LOG.md) |

Celah yang masih terbuka: belum ada satu pun dari 19 spesies endemik Danau Malili dalam checklist yang punya referensi MiFish layak. BioTrace menampilkan celah ini sebagai peta celah dan prioritas barcode, bukan menyembunyikannya.

## Validasi

Uji *leave-one-species-out*: semua sekuens spesies X dihapus dari kamus, lalu DNA X dicocokkan ke kamus yang tersisa. Karena X sudah tidak ada, jawaban yang benar hanyalah takson yang memuat X (misalnya genusnya) atau "tidak dikenal"; nama spesies apa pun adalah nama keliru.

| Kamus v0.5, aturan r0.4 (630 spesies, 999 uji) | BioTrace | BLAST ≥97% saja |
|---|---:|---:|
| Nama keliru di tingkat apa pun | **7,51%** | 32,53% |
| Menahan diri dengan benar | 92,49% | — |
| Nama spesies benar saat referensi lain tersedia | 20,37% | — |

Angka terakhir menunjukkan biaya kehati-hatian: BioTrace sering berhenti di tingkat genus. Ini uji pustaka internal dengan sinyal lab ideal, **bukan akurasi lapangan**. Hasil lengkap: [`validation/results/`](validation/results/); bukti reproduksibilitas rilis v0.5: [`validation/jury/v0.5/`](validation/jury/v0.5/).

## Arsitektur dan teknologi

```
Browser ── dashboard React (web/) ──► FastAPI (api/) ──► biotrace_core (mesin aturan, offline)
                                                            ├─ data/reference/vX    kamus berversi + manifest SHA-256
                                                            ├─ biotrace_core/rules   aturan r0.4 (YAML)
                                                            ├─ BLAST+ lokal          blastn, makeblastdb
                                                            └─ runs/<run_id>/        hasil + jejak audit
```

| Lapisan | Teknologi |
|---|---|
| Mesin inti | Python 3.11, pydantic v2, PyYAML, pandas, Biopython; fungsi murni dan deterministik |
| Pencocokan sekuens | NCBI BLAST+ 2.14+, lokal; batas waktu 600 detik (`BIOTRACE_BLAST_TIMEOUT_SECONDS`, 1–3600) |
| API | FastAPI, Uvicorn, python-multipart |
| Laporan | ReportLab (PDF), CSV/ZIP, SHA-256 |
| Dashboard | React 18, Vite 6, TypeScript 5 (strict), Tailwind CSS 4, Recharts 3, TanStack Table 8, React Router 7, react-dropzone, lucide-react |
| Kontrak data | Skema pydantic diekspor ke TypeScript (`scripts/export_schemas.py`) |
| Penyimpanan | Berbasis file berversi, tanpa basis data |
| Kualitas | pytest, ruff, Playwright, GitHub Actions |

## Struktur repo

```
api/              API FastAPI: unggah, analisis, laporan, verifikasi
biotrace_core/    mesin: io (validasi, pengenalan kolom), naming, scoring, causes, decision,
                  reference (kurasi, kamus), report (PDF/CSV), audit, validation (LOSO), rules/
web/              dashboard React + Vite
data/             kamus berversi, data demo, data eDNA asli, modul validasi luar, kurasi
precomputed/      hasil run demo terverifikasi
raw/              data mentah bersumber dan log unduhan
validation/       hasil uji validasi dan bukti reproduksibilitas
scripts/          setup, demo, build, unduh data, builder kamus, pemeriksaan rilis
templates/        templat data lapangan dan lab
tests/            pengujian per aturan, API, dan rilis
docs/             konsep, aturan mesin, spesifikasi data, arsitektur, validasi, registri bukti
```

## Pengembangan

| Perintah (`uv run python scripts/project.py <tugas>`, atau `make <tugas>`) | Isi |
|---|---|
| `setup` | Pasang dependensi Python/npm, BLAST+ (Windows), siapkan data |
| `test` | `ruff format --check`, `ruff check`, `pytest -m "not slow"` |
| `test-slow` | Uji kinerja (200 sampel × 2.000 ASV) |
| `build` | Ekspor skema ke TypeScript, build `web/dist` |
| `demo` | Build dashboard dan jalankan di http://127.0.0.1:8000 |
| `dev` | API dengan reload + Vite dev server |
| `precompute` / `ref-build` | Simpan run demo terverifikasi / bangun database BLAST kamus demo |

Pemeriksaan rilis: `uv run python scripts/prepare_jury.py check|audit|quality`. Aturan kontribusi (termasuk untuk AI agent) ada di [`AGENTS.md`](AGENTS.md); setiap perubahan aturan, skema, atau kamus dicatat di [`docs/09_LOG_KEPUTUSAN.md`](docs/09_LOG_KEPUTUSAN.md). Indeks dokumentasi: [`docs/README.md`](docs/README.md).

## Batasan dan penggunaan yang bertanggung jawab

- BioTrace bekerja setelah lab selesai: tidak mengambil sampel, tidak mengolah FASTQ mentah, dan tidak memegang spesimen.
- Barcode 12S mengenali spesies, bukan populasi; jumlah bacaan bukan ukuran kelimpahan.
- Nilai A bukan kepastian. Status taksonomi, endemik, invasif, dan regulasi dalam kamus belum ditinjau ahli.
- Laporan BioTrace adalah verifikasi pendukung, tidak menyatakan kepatuhan AMDAL/RKL-RPL.
- Data pihak ketiga mengikuti lisensi sumbernya (antara lain GenBank/NCBI, FishBase, Dryad CC0); rincian per dataset ada di `raw/DOWNLOAD_LOG.md` dan `sources.csv` setiap kamus. Lisensi kode belum ditetapkan.

## Rujukan utama

- Miya M. dkk. 2015. MiFish, universal PCR primers for metabarcoding environmental DNA from fishes. *Royal Society Open Science* 2:150088. https://doi.org/10.1098/rsos.150088
- Altschul S. F. dkk. 1990. Basic local alignment search tool. *Journal of Molecular Biology* 215:403–410.
- Polanco F. A. dkk. 2025. *Environmental DNA* 7(2):e70077 (konsep skor keyakinan berlapis). https://doi.org/10.1002/edn3.70077
- Marwayana O. dkk. 2022. *Environmental DNA*. https://doi.org/10.1002/edn3.257; data Dryad https://doi.org/10.5068/D12T1B
- Daftar lengkap rujukan dan klaim yang boleh dipakai: [`docs/07_REGISTRI_BUKTI_RINGKAS.md`](docs/07_REGISTRI_BUKTI_RINGKAS.md).

## Tim

Tim Exastra: Bramantyo Kunni Nurrisqi (produk & validasi), Bagus Athallah (backend & data), Agathan Khairy Bowo Laksono (frontend & laporan).

## Sebelum vs selama hackathon

> Bagian ini wajib diisi oleh manusia (tim), bukan agent, sesuai [01 §10](docs/01_KONSEP_INDUK.md).

**Sudah ada sebelum hackathon:**

- _(diisi tim)_

**Dibuat selama hackathon:**

- _(diisi tim)_
