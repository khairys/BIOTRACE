# BioTrace Indonesia

**Pemeriksa fakta untuk hasil eDNA ikan Indonesia.** BioTrace memeriksa setiap nama ikan dari hasil lab eDNA (metabarcoding 12S MiFish) terhadap kamus DNA berversi dan aturan tertulis. Hasilnya tingkat nama yang aman, nilai bukti A–D, penyebab ketidakpastian, dan satu dari empat keputusan: **Aman dilaporkan**, **Dengan catatan**, **Wajib verifikasi**, atau **Jangan dipakai**. Setiap laporan memiliki jejak audit SHA-256.

> BioTrace menghasilkan **laporan verifikasi pendukung**, bukan dokumen AMDAL resmi. Deteksi DNA bukan bukti pasti ikan hidup di lokasi. Semua ambang adalah usulan tim dan belum dikalibrasi ahli.

GENOHACK 2026 · Track 2: Genomics for Food Security & Biodiversity · Tim Exastra

---

## Mulai cepat (juri)

```bash
uv run python scripts/project.py setup     # dependensi Python + npm, BLAST+ (Windows otomatis ke .tools/)
uv run python scripts/project.py demo      # build web + API di http://127.0.0.1:8000
```

1. Buka http://127.0.0.1:8000 → klik **Muat data eDNA asli Indonesia** (hasil pra-hitung terverifikasi, tanpa menunggu BLAST).
2. Gulir ke **Evidence Card** atau klik **Lihat bukti** di Daftar klaim untuk melihat alasan setiap keputusan.
3. Unduh **Ringkasan PDF** / ZIP, salin sidik jari laporan, dan periksa di halaman **Verifikasi**.
4. Demo **SIMULASI** Matano memperlihatkan keempat keputusan, kompleks spesies, dan alias louhan.

Tanpa menjalankan aplikasi: baca [`validation/jury/v0.5/ringkasan_juri.pdf`](validation/jury/v0.5/ringkasan_juri.pdf). Panduan pemeriksaan lengkap: [`docs/17_KESIAPAN_JURI.md`](docs/17_KESIAPAN_JURI.md).

---

## Masalah yang diselesaikan

Penamaan spesies dari eDNA hanya seandal kamus referensinya. Untuk ikan Indonesia, kamus itu masih bolong: bila spesies yang benar belum ada di kamus, pencocokan biasa (BLAST ≥97%) tetap memberi nama spesies lain dengan yakin. Nama keliru itu bisa masuk dokumen lingkungan perusahaan. BioTrace menurunkan nama ke tingkat yang didukung bukti (spesies → kompleks → genus → "tidak dikenal") dan menuliskan alasannya, alih-alih menebak.

## Cara kerja (alur satu run)

```
upload CSV/TSV/FASTA ─► pengenalan kolom otomatis + validasi (V-01..V-10)
                          │
                          ▼
   Tahap 0  Pra-proses     tabel panjang, filter tag-jumping, kontrol negatif, klaim = ASV × lokasi
   Tahap 1  Penamaan       BLAST+ lokal ke kamus berversi (atau taksonomi lab) → tingkat nama aman
   Tahap 2  Penilaian      L1 kamus (0–2) + L2 lokasi (0–1) + L4 sinyal lab (0–2) → nilai A–D; L3 = label
   Tahap 3  Penyebab       reference / marker / sample / location
   Tahap 4  Keputusan      safe / with_note / must_verify / do_not_use + tindak lanjut (R-DEC-01..09)
   Tahap 5  Asal-usul      kemungkinan sumber DNA lain
   Tahap 6  Celah          peta kelengkapan kamus + daftar prioritas barcode
   Tahap 7  Audit          SHA-256 input, versi kamus/aturan/engine, sidik jari laporan
                          │
                          ▼
   runs/<run_id>/  claims.csv · summary.json · report.pdf · run_manifest.json · validation_report.json
```

Ringkas aturan penilaian (`biotrace_core/rules/rules_r0.4.yaml`):

| Lapis | Dasar | Aturan utama |
|---|---|---|
| L1 Kamus (0–2) | Kemiripan terbaik dan selisih ke kandidat di luar jendela 0,5% | 2 bila ≥99% dan selisih ≥1,0%; 1 bila ≥98% dan ≥0,5%; −1 bila <50% spesies segenus di perairan punya referensi |
| L2 Lokasi (0–1) | Checklist perairan di kamus | 1 bila takson tercatat di perairan klaim |
| L3 Label | Checklist + status IUCN/invasif + alias | endemik, terancam, invasif, hibrida; tidak menambah skor, mengetatkan keputusan |
| L4 Sinyal lab (0–2) | Replikat positif per lokasi | 2 bila muncul di semua replikat; 1 bila ≥66% atau satu replikat |
| Batas D | Kontrol negatif / bacaan | Nilai D bila DNA ada di kontrol negatif batch yang sama atau total bacaan <10 |

Total L1+L2+L4: 5 = A, 4 = B, 2–3 = C, 0–1 = D. Klaim yang hanya didukung spesimen luar Indonesia atau checklist sekunder tidak pernah "Aman" (R-DEC-09). Rincian: [`docs/03_ATURAN_MESIN.md`](docs/03_ATURAN_MESIN.md).

## Arsitektur dan teknologi

```
Browser ── React dashboard (web/) ──► FastAPI (api/main.py) ──► biotrace_core (mesin murni, offline)
                                                                   ├─ data/reference/vX   kamus DNA berversi + manifest SHA-256
                                                                   ├─ biotrace_core/rules  aturan r0.4 (YAML)
                                                                   ├─ BLAST+ (blastn, makeblastdb) lokal
                                                                   └─ runs/<run_id>/       hasil + jejak audit
```

| Lapisan | Teknologi |
|---|---|
| Mesin inti | Python 3.11, pydantic v2, PyYAML, pandas, Biopython; fungsi murni deterministik, **tanpa ML, tanpa internet saat analisis** |
| Pencocokan sekuens | NCBI BLAST+ 2.14+ (`blastn`, `makeblastdb`), dijalankan lokal dengan anggaran waktu 600 dtk (`BIOTRACE_BLAST_TIMEOUT_SECONDS`) |
| API | FastAPI + Uvicorn, `python-multipart`; menyajikan API sekaligus build web |
| Laporan | ReportLab (PDF lengkap dan ringkasan), CSV/ZIP, sidik jari SHA-256 |
| Dashboard | React 18, Vite 6, TypeScript 5 (strict), Tailwind CSS 4, Recharts 3, TanStack Table 8, React Router 7, react-dropzone, lucide-react |
| Kontrak data | Skema pydantic diekspor ke TypeScript (`scripts/export_schemas.py` → `web/src/api/generated.ts`) |
| Penyimpanan | Berbasis file berversi (tanpa basis data): kamus, aturan, dan hasil run adalah folder |
| Kualitas | pytest (+ uji kinerja T-PERF), ruff format/check, Playwright (`scripts/test_browser.py`), GitHub Actions (`.github/workflows`) |
| Paket | uv (Python), npm (web), Node.js 22 |

## Data

| Komponen | Isi | Lokasi |
|---|---|---|
| Kamus aktif | **v0.5**: 999 sekuens 12S MiFish, 630 spesies, 133 sekuens dari spesimen Indonesia; checklist Malili, laut, dan air tawar Indonesia; status IUCN/invasif; alias | `data/reference/v0.5` |
| Kamus lama | v0.1–v0.4 tetap utuh untuk reproduksi | `data/reference/` |
| Data eDNA asli | Marwayana dkk. 2022, MiFish-U terumbu Indonesia (Dryad 10.5068/D12T1B, CC0); 4.354 klaim, 152 taksa | `data/edna_asli/`, `precomputed/edna_asli_marwayana2022_r0.4_v0.5/` |
| Demo SIMULASI | Danau Matano fiktif, 16 skenario, berlabel SIMULASI | `data/demo/matano_SIMULASI_v3/` |
| Modul validasi luar | Lake St. Pierre (Kanada), Guyana Prancis; hanya mode validasi | `data/external/` |
| Data mentah | Unduhan bersumber dengan SHA-256 dan log | `raw/`, `raw/DOWNLOAD_LOG.md`, `scripts/fetch_data.py` |

Celah yang diakui: **0 dari 19 spesies endemik Malili** di checklist sudah punya referensi MiFish yang layak. Celah ini ditampilkan sebagai peta celah dan prioritas barcode.

## Format input

| File | Wajib | Kolom utama |
|---|---|---|
| Tabel bacaan (CSV/TSV) | Ya | `asv_id`, `sample_id`, `reads` (format panjang atau lebar) |
| Metadata sampel | Ya | `sample_id`, `site_id`, `waterbody_id`, `sample_type`, `replicate`, `extraction_batch`, `marker` |
| FASTA ASV | Salah satu | `>asv_id` + urutan; dicocokkan ulang ke kamus BioTrace |
| Taksonomi lab | Salah satu | `asv_id`, `taxon`, `rank`, `pct_identity`, `runner_up_*` |

Nama kolom lain dikenali otomatis (mis. `otu_id`, `site_name`, `waterbody`, `pident`); kolom tambahan diabaikan dan dilaporkan. Perairan dan marker yang kosong dipilih di formulir unggah; koordinat dan tanggal yang kosong tidak ditebak. Templat lab: `templates/`. Spesifikasi: [`docs/04_SPESIFIKASI_DATA.md`](docs/04_SPESIFIKASI_DATA.md).

## Validasi

Uji *leave-one-species-out* (LOSO): semua sekuens spesies X dihapus dari kamus, lalu X dicocokkan ke kamus sisanya. Jawaban benar hanyalah takson yang memuat X atau "tidak dikenal".

| Kamus v0.5, r0.4 (630 spesies, 999 query) | BioTrace | BLAST ≥97% saja |
|---|---:|---:|
| Nama keliru di tingkat apa pun (M3) | **7,51%** | 32,53% |
| Menahan diri dengan benar (M2) | 92,49% | — |
| Nama spesies benar saat referensi lain tersedia (M4) | 20,37% | — |

M4 yang rendah adalah biaya kehati-hatian dan keterbatasan nyata. Ini eksperimen pustaka internal dengan sinyal lab ideal, **bukan akurasi lapangan**. Hasil: `validation/results/`, bukti rilis: `validation/jury/v0.5/`.

## Perintah

| Perintah (`uv run python scripts/project.py <tugas>` = `make <tugas>`) | Isi |
|---|---|
| `setup` | Pasang dependensi Python/npm, BLAST (Windows), siapkan data |
| `test` | `ruff format --check`, `ruff check`, `pytest -m "not slow"` |
| `test-slow` | Uji kinerja T-PERF (200 sampel × 2.000 ASV) |
| `build` | Ekspor skema → TypeScript, build `web/dist` |
| `demo` | Build web dan jalankan API di http://127.0.0.1:8000 |
| `dev` | API `--reload` + Vite dev server |
| `precompute` / `ref-build` | Simpan run demo terverifikasi / bangun blastdb kamus demo |

Pemeriksaan rilis juri: `uv run python scripts/prepare_jury.py check|audit|quality` dan `uv run biotrace verify --run precomputed/edna_asli_marwayana2022_r0.4_v0.5`.

CLI: `uv run biotrace {run,verify,rematch,compare,gaps,ref,validate}`. Contoh:

```bash
uv run biotrace run --reads reads.csv --meta metadata.csv --taxonomy taxonomy.csv --out runs
uv run biotrace validate loso --ref data/reference/v0.5 --out validation/results/loso.json
```

API utama (FastAPI, dokumentasi otomatis di `/docs`): `POST /api/runs`, `POST /api/inputs/inspect`, `POST /api/runs/demo/{id}`, `GET /api/runs/{id}` (+ `/claims`, `/coverage`, `/barcode-priority`, `/report.pdf`, `/export.zip`, `/sites`), `POST /api/runs/{id}/rematch`, `POST /api/verify`, `GET /api/reference`, `GET /api/methods`, `GET /api/validation/latest`.

## Struktur repo

```
api/              FastAPI: endpoint, unggah, demo
biotrace_core/    mesin: io (validasi, pengenalan kolom), naming, scoring, causes, decision,
                  reference (kurasi, kamus), report (PDF/CSV), audit, validation (LOSO), rules/
web/              dashboard React + Vite (Unggah, Hasil, Evidence Card, Metode, Validasi, Verifikasi)
data/             kamus berversi, data demo SIMULASI, data eDNA asli, modul validasi luar, kurasi
precomputed/      run demo terverifikasi (cadangan tanpa BLAST)
raw/              data mentah bersumber + DOWNLOAD_LOG.md
validation/       hasil LOSO dan bukti rilis juri
scripts/          setup/demo/build, unduh data, builder kamus, pemeriksaan rilis
templates/        templat lapangan dan permintaan lab
tests/            pytest per aturan (R-*), API, rilis
docs/             konsep, aturan mesin, spesifikasi data, arsitektur, validasi, registri bukti, paket juri
```

## Batas

- Bekerja setelah lab selesai: tidak mengambil sampel, tidak memproses FASTQ, tidak memegang spesimen.
- Barcode 12S mengenali spesies, bukan populasi; jumlah bacaan bukan kelimpahan.
- Nilai A bukan kepastian. Status taksonomi, endemik, invasif, dan regulasi dalam kamus belum ditinjau ahli.
- Tidak menyatakan kepatuhan AMDAL/RKL-RPL dan tidak menyebut mitra yang belum setuju tertulis.

## Sebelum vs selama hackathon

> Bagian ini wajib diisi oleh manusia (tim), bukan agent, sesuai [01 §10](docs/01_KONSEP_INDUK.md).

**Sudah ada sebelum hackathon:**

- _(diisi tim)_

**Dibuat selama hackathon:**

- _(diisi tim)_

## Tim

Tim Exastra: Bramantyo Kunni Nurrisqi (produk & validasi), Bagus Athallah (backend & data), Agathan Khairy Bowo Laksono (frontend & laporan).

Dokumentasi lengkap: [`docs/`](docs/README.md). Aturan kontributor dan agent: [`AGENTS.md`](AGENTS.md). Keputusan: [`docs/09_LOG_KEPUTUSAN.md`](docs/09_LOG_KEPUTUSAN.md).
