# 05 — Arsitektur dan Spesifikasi Teknis

| Atribut | Isi |
|---|---|
| Versi | 1.0 · 24 Oktober 2026 |
| Tunduk pada | `01_KONSEP_INDUK.md` (D-009, D-015), `03_ATURAN_MESIN.md`, `04_SPESIFIKASI_DATA.md` |
| Repo | `github.com/khairys/BIOTRACE` (khusus produk dan teknis; tanpa materi pitch) |

---

## 1. Prinsip arsitektur

1. **Mesin terpisah dari UI.** `biotrace_core` adalah library Python murni dengan CLI. API dan dashboard hanya membungkusnya.
2. **Deterministik dan bisa diaudit** (aturan A6, R-AUD-*).
3. **Offline.** Tidak ada panggilan internet saat run (aturan A8).
4. **Berbasis file dan berversi.** Kamus dan aturan adalah file di repo; hasil run adalah folder.
5. **Satu perintah untuk demo.** FastAPI menyajikan API sekaligus build React.
6. **Bisa diuji per aturan.** Setiap aturan di 03 adalah fungsi kecil dengan tes.

## 2. Stack

| Lapisan | Pilihan | Versi minimum | Tag |
|---|---|---|---|
| Bahasa mesin | Python | 3.11 | `[MVP]` |
| Data | pandas, pydantic v2, PyYAML, Biopython | terbaru stabil | `[MVP]` |
| Pencocokan | NCBI BLAST+ (`blastn`, `makeblastdb`) | 2.14+ | `[MVP]` |
| API | FastAPI + Uvicorn, `python-multipart` | terbaru stabil | `[MVP]` |
| PDF | ReportLab | 4.x | `[MVP]` |
| Tes | pytest, pytest-cov | | `[MVP]` |
| Lint | ruff | | `[MVP]` |
| Frontend | React 18, Vite, TypeScript (strict), Tailwind CSS, Recharts, TanStack Table, React Router, `react-dropzone`, `lucide-react`, `@fontsource/inter`, `@fontsource/jetbrains-mono` | | `[MVP]` |
| Paket Python | `uv` (disarankan) atau `pip` + `requirements.txt` | | `[MVP]` |
| Basis data | Tidak ada (berbasis file) | | `[MVP]` |
| Basis data | PostgreSQL | | `[P1]` |
| Kontainer | Docker (image dengan BLAST+) | | `[P1]` |
| Auth, multi-pengguna | — | | `[P1]` |
| FASTQ → ASV | Pipeline terbuka (mis. MiFish pipeline/DADA2) | | `[P2]` |

**Rencana cadangan (hanya bila waktu habis sebelum demo):** UI Streamlit `app_streamlit.py` yang memanggil `biotrace_core` yang sama. Tidak boleh ada logika mesin di UI cadangan.

## 3. Struktur repo

```
BIOTRACE/
├─ AGENTS.md
├─ CLAUDE.md
├─ README.md                    # wajib memuat bagian "Sebelum vs selama hackathon"
├─ Makefile
├─ pyproject.toml
├─ docs/                        # 01–06, 07 ringkas, 09
├─ biotrace_core/
│  ├─ __init__.py               # __version__
│  ├─ cli.py                    # entry point `biotrace`
│  ├─ models.py                 # pydantic: Claim, RunManifest, dll.
│  ├─ config.py                 # memuat rules YAML → RulesConfig
│  ├─ rules/
│  │  ├─ rules_r0.1.yaml
│  │  └─ reasons_r0.1.yaml
│  ├─ io/
│  │  ├─ loaders.py             # baca CSV/TSV/FASTA, deteksi format lebar/panjang
│  │  └─ validate.py            # V-01..V-10
│  ├─ reference/
│  │  ├─ store.py               # muat kamus per versi & modul
│  │  ├─ curate.py              # R-CUR-01..12
│  │  ├─ trim.py                # potong daerah MiFish-U
│  │  └─ coverage.py            # R-COV-01..02
│  ├─ preprocess.py             # R-PRE-01..05
│  ├─ naming/
│  │  ├─ blast.py               # makeblastdb, blastn, parse hasil
│  │  ├─ candidates.py          # R-NAME-02, 04
│  │  └─ rules.py               # R-NAME-03, 05..12
│  ├─ scoring.py                # R-SCORE-01..07
│  ├─ causes.py                 # R-CAUSE-01..05
│  ├─ decision.py               # R-DEC-01..08
│  ├─ origin.py                 # R-ORIG-01..02
│  ├─ gaps.py                   # R-GAP-01..02
│  ├─ audit.py                  # R-AUD-01..04
│  ├─ pipeline.py               # orkestrasi run
│  ├─ report/
│  │  ├─ csv_export.py
│  │  └─ pdf.py                 # ReportLab
│  └─ validation/
│     ├─ loso.py                # R-VAL-02
│     └─ baseline.py            # R-VAL-01
├─ api/
│  ├─ main.py                   # FastAPI app + sajikan web/dist
│  └─ routes.py
├─ web/                         # React + Vite + TS
│  ├─ src/
│  │  ├─ api/                   # client + tipe hasil generate
│  │  ├─ pages/                 # Upload, Summary, Claims, Reference, Report, Methods, Validation
│  │  ├─ components/            # DecisionTiles, ClaimsTable, EvidenceCard, CoverageChart, ...
│  │  └─ i18n/id.ts             # semua teks UI
│  └─ ...
├─ data/
│  ├─ reference/v0.1/
│  ├─ external/
│  └─ demo/matano_sim_v1/
├─ runs/                        # .gitignore
├─ precomputed/                 # hasil run demo cadangan (dikomit)
├─ scripts/
│  ├─ export_schemas.py         # pydantic → JSON Schema → TS types
│  ├─ make_demo_data.py         # membangkitkan data SIMULASI (seed tetap)
│  ├─ fetch_data.py             # unduh dataset publik ke raw/ + log (A13)
│  └─ fetch_instructions.md     # cara manual bila skrip gagal
└─ tests/
   ├─ fixtures/fx1/             # Fixture FX-1 dari 03 §11
   ├─ test_rules_naming.py
   ├─ test_rules_scoring.py
   ├─ test_rules_decision.py
   ├─ test_examples_E1_E12.py
   ├─ test_audit_reproducible.py
   ├─ test_external_isolation.py
   └─ test_performance.py
```

## 4. Alur data satu run

```
upload → io.loaders → io.validate ──(galat)──► stop + validation_report.json
             │
             ▼
     preprocess (R-PRE)
             │
     ┌───────┴────────┐
     │ FASTA ada?      │
     ├─ ya → naming.blast (kamus aktif) → candidates
     └─ tidak → taxonomy lab → candidates (R-NAME-12)
             │
     naming.rules → scoring → causes → decision → origin
             │
     gaps (coverage + barcode_priority)
             │
     audit (fingerprints) → report (csv, pdf) → runs/<run_id>/
```

## 5. Kontrak modul (Python)

```python
# biotrace_core/pipeline.py
def run_analysis(
    reads_path: Path,
    metadata_path: Path,
    fasta_path: Path | None,
    taxonomy_path: Path | None,
    site_context_path: Path | None,
    reference_dir: Path,            # data/reference/v0.1
    rules_path: Path,               # biotrace_core/rules/rules_r0.1.yaml
    out_root: Path,                 # runs/
    mode: Literal["normal", "validation"] = "normal",
) -> RunResult: ...

class RunResult(BaseModel):
    run_id: str
    claims: list[Claim]
    summary: RunSummary
    coverage: list[CoverageRow]
    barcode_priority: list[BarcodePriorityRow]
    manifest: RunManifest
    validation: ValidationReport
```

```python
# naming/rules.py — contoh tanda tangan fungsi murni
def assign_rank(
    hits: list[SpeciesHit],          # satu hit terbaik per spesies, tersortir
    waterbody_id: str,
    ref: ReferenceIndex,             # checklist, taxa, complexes, aliases, coverage
    cfg: RulesConfig,
) -> NamingResult:
    """R-NAME-03..11. Tidak melakukan I/O."""
```

Model `Claim` harus memuat semua kolom `claims.csv` (04 §4.1). Nama field Python sama persis dengan nama kolom.

## 6. BLAST

**Pembuatan database (sekali per versi kamus):**
```
makeblastdb -in data/reference/v0.1/sequences.fasta -dbtype nucl \
  -out data/reference/v0.1/blastdb/ref -parse_seqids
```
Hanya sekuens yang memenuhi R-NAME-01 yang ditulis ke `sequences.fasta` khusus BLAST (`blast_input.fasta`).

**Pencocokan:**
```
blastn -query asv.fasta -db .../blastdb/ref -task blastn \
  -max_target_seqs 500 -evalue 1e-5 -perc_identity 80 -dust no \
  -num_threads 4 \
  -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen qcovs"
```
- Setelah dibaca, hasil **disortir** (`qseqid`, `-pident`, `-bitscore`, `sseqid`) agar deterministik walaupun multi-thread.
- Parameter BLAST dicatat di `run_manifest.json`.
- Versi BLAST+ dibaca dari `blastn -version` dan dicatat.

**Cadangan demo:** bila `blastn` tidak tersedia, API memuat `precomputed/<demo_id>/` dan dashboard menampilkan "hasil pra-hitung". Ini hanya untuk data demo, bukan untuk unggahan pengguna.

## 7. CLI

| Perintah | Fungsi | Tag |
|---|---|---|
| `biotrace run --reads R --meta M [--fasta F] [--taxonomy T] [--ref data/reference/v0.1] [--rules ...] [--out runs/]` | Jalankan analisis | `[MVP]` |
| `biotrace ref import --fasta F --meta S.csv --from v0.1 --to v0.2` | Kurasi dan bangun versi kamus baru (R-CUR) | `[MVP]` |
| `biotrace ref coverage --ref data/reference/v0.1` | Hitung ulang `coverage.csv` | `[MVP]` |
| `biotrace ref stats --ref ...` | Ringkasan kamus (R-COV-02) | `[MVP]` |
| `biotrace validate loso --ref <dir> [--module <ext>]` | Uji leave-one-species-out vs baseline | `[MVP]` |
| `biotrace verify --run runs/<id>` | Hitung ulang fingerprint dan bandingkan | `[MVP]` |

## 8. API (FastAPI)

Basis: `/api`. Semua respons JSON memakai model pydantic. Proses sinkron di MVP (< 2 menit).

| Metode | Path | Input | Output | Tag |
|---|---|---|---|---|
| GET | `/api/health` | — | versi engine, versi kamus aktif, versi aturan, `blast_available` | `[MVP]` |
| POST | `/api/runs` | multipart: `reads`, `metadata`, `fasta?`, `taxonomy?`, `site_context?` | `{run_id, status, validation}` | `[MVP]` |
| POST | `/api/runs/demo/{demo_id}` | — | `{run_id, is_simulated: true}` | `[MVP]` |
| GET | `/api/runs/{run_id}` | — | `RunSummary` + manifest | `[MVP]` |
| GET | `/api/runs/{run_id}/claims` | query: `decision`, `site_id`, `label`, `q` | `list[Claim]` | `[MVP]` |
| GET | `/api/runs/{run_id}/claims/{claim_id}` | — | `Claim` lengkap (Evidence Card) | `[MVP]` |
| GET | `/api/runs/{run_id}/coverage` | — | `list[CoverageRow]` | `[MVP]` |
| GET | `/api/runs/{run_id}/barcode-priority` | — | `list[BarcodePriorityRow]` | `[MVP]` |
| GET | `/api/runs/{run_id}/report.pdf` | — | PDF | `[MVP]` |
| GET | `/api/runs/{run_id}/export.zip` | — | `claims.csv`, `summary.json`, `coverage.csv`, `barcode_priority.csv`, `run_manifest.json` | `[MVP]` |
| GET | `/api/reference` | — | statistik kamus aktif (R-COV-02) | `[MVP]` |
| GET | `/api/reference/coverage?waterbody_id=` | — | cakupan per genus | `[MVP]` |
| GET | `/api/validation/latest` | — | hasil LOSO pra-hitung | `[MVP]` |
| POST | `/api/verify` | `{report_fingerprint}` | cocok/tidak | `[P1]` |

Galat: `422` untuk validasi input, dengan isi `ValidationReport`. `500` dicatat di log tanpa membocorkan isi data.

## 9. Frontend

### 9.1 Rute

| Rute | Halaman (02 §7) |
|---|---|
| `/` | P1 Unggah |
| `/runs/:id` | **Hasil** (dashboard satu halaman: P2–P6 digabung, D-025); Evidence Card sebagai panel samping `?claim=` |
| `/methods` | P7 Metode |
| `/validation` | P8 Validasi |

### 9.2 Komponen utama

| Komponen | Isi |
|---|---|
| `SimulationBanner` | Pita kuning "SIMULASI: data dibuat tim untuk demo" bila `is_simulated` |
| `LimitNotice` | Kalimat batas interpretasi (aturan A11), tampil di P2, P4, P6 |
| `DecisionTiles` | 4 kotak: jumlah klaim, jumlah taksa, tindak lanjut |
| `ClaimsTable` | TanStack Table; kolom: lokasi, ASV, nama lab, nama aman (miring bila spesies), tingkat, nilai (badge A–D), keputusan (badge warna), label |
| `EvidenceCard` | Bagian: Nama (lab → aman); Nilai & skor L1/L2/L4; Penyebab; Kecocokan dalam 0,5%; Voucher pendukung; Label; Peluang belum di kamus; Asal-usul; Keputusan & tindak lanjut; Alasan ID/EN (tab); Batas interpretasi |
| `CoverageChart` | Bar horizontal per genus: r vs n, diurutkan dari P_missing terbesar |
| `GapTable` | Daftar prioritas barcode |
| `AuditPanel` | SHA-256 input, versi kamus, versi aturan, fingerprint, tombol salin |

### 9.3 Warna keputusan (token)

| Keputusan | Token | Makna visual |
|---|---|---|
| `safe` | `--decision-safe` (hijau) | Aman |
| `with_note` | `--decision-note` (biru) | Perlu catatan |
| `must_verify` | `--decision-verify` (oranye) | Perlu cek |
| `do_not_use` | `--decision-stop` (merah) | Jangan |

Warna tidak boleh menjadi satu-satunya pembeda: selalu sertakan label teks.

## 10. Laporan PDF `[MVP]`

Struktur (Bahasa Indonesia):
1. Sampul: judul "Laporan Verifikasi Data eDNA (Pendukung)", nama proyek, perairan, tanggal, `report_fingerprint`, banner SIMULASI bila relevan.
2. Ringkasan keputusan (tabel 4 kategori + tindak lanjut).
3. Tabel klaim (ringkas).
4. Lampiran Evidence Card untuk klaim `must_verify` dan `do_not_use`.
5. Kamus & celah: cakupan per genus, daftar prioritas barcode.
6. Metode singkat dan parameter aturan r0.1 ("usulan tim, belum dikalibrasi ahli").
7. Jejak audit dan daftar sumber kamus beserta lisensinya.
8. Batas interpretasi dan pernyataan: "Laporan ini adalah verifikasi pendukung, bukan dokumen AMDAL resmi."

## 11. Lingkungan dan menjalankan

### 11.1 Persiapan

| OS | BLAST+ |
|---|---|
| Windows | Unduh installer `ncbi-blast-*-win64.exe` dari situs FTP NCBI BLAST+, lalu tambahkan ke PATH |
| macOS | `brew install blast` |
| Linux | `sudo apt install ncbi-blast+` atau `conda install -c bioconda blast` |

```
make setup        # uv sync / pip install -e .[dev]; npm ci di web/
make test         # ruff + pytest
make demo         # bangun web, jalankan API di http://localhost:8000, muat demo
make dev          # API --reload + Vite dev server
make ref-build    # bangun blastdb kamus aktif
make precompute   # simpan hasil run demo ke precomputed/
```

### 11.2 Konfigurasi

Variabel lingkungan (`.env`, opsional):

| Nama | Default |
|---|---|
| `BIOTRACE_REF_DIR` | `data/reference/v0.1` |
| `BIOTRACE_RULES` | `biotrace_core/rules/rules_r0.1.yaml` |
| `BIOTRACE_RUNS_DIR` | `runs` |
| `BIOTRACE_BLAST_THREADS` | `4` |
| `BIOTRACE_MAX_UPLOAD_MB` | `200` |

## 12. Kualitas

| Aspek | Cara |
|---|---|
| Tes aturan | Setiap R-* punya ≥1 tes; contoh E1–E12 wajib lulus |
| Reproduksibilitas | Dua run identik menghasilkan `report_fingerprint` sama |
| Isolasi data luar | Tes memastikan mode normal tidak membaca `data/external/` |
| Kinerja | Tes sintetis 200 sampel × 2.000 ASV < 120 detik (ditandai `slow`) |
| Cakupan tes | ≥ 80% untuk `biotrace_core` `[P1]`; MVP: semua modul aturan |
| CI | GitHub Actions: ruff + pytest (tanpa tes `slow`) `[P1]` |

## 13. Keamanan dan privasi

- File unggahan disimpan hanya di `runs/<run_id>/input/` di mesin lokal.
- Tidak ada pengiriman data ke layanan luar.
- Validasi ekstensi dan ukuran sebelum diproses.
- Nama file pengguna tidak dipakai sebagai path (simpan dengan nama baku).

## 14. Rencana kerja malam hackathon `[MVP]`

Urutan disusun agar selalu ada demo yang jalan bila waktu habis.

| # | Pekerjaan | Pemilik | Selesai bila |
|---|---|---|---|
| 1 | Kerangka repo, `models.py`, `config.py`, rules YAML, fixture FX-1 | Backend | `make test` jalan |
| 2 | `preprocess`, `naming/rules`, `scoring`, `causes`, `decision` + tes E1–E12 (mode taksonomi lab dulu, tanpa BLAST) | Backend | E1–E12 lulus |
| 3 | `make_demo_data.py` → `data/demo/matano_sim_v1/` (SIMULASI) sesuai 10 §6 | Backend | 16 skenario menghasilkan keputusan target |
| 4 | API minimal: `/api/runs/demo`, `/claims`, `/coverage` | Backend | JSON keluar |
| 5 | Halaman Unggah (drag & drop) dan Hasil bagian ①–④ sesuai 10 §3–4 | Frontend | Alur demo berjalan dari unggah sampai Evidence Card |
| 6 | Modul BLAST + kamus v0.1 (publik bila sudah terunduh; bila belum, sintetis SIMULASI) | Backend | Mode FASTA jalan |
| 7 | Hasil bagian ⑤–⑦ | Frontend | Grafik cakupan dan audit tampil |
| 8 | Audit + PDF | Backend/Frontend | PDF terunduh dengan fingerprint |
| 9 | `make precompute` + P7 Metode + P8 Validasi (statis) | Semua | Demo bisa jalan offline tanpa BLAST |
| 10 | README "Sebelum vs selama hackathon" | Manusia | Terisi |

Titik aman: setelah langkah 5, demo sudah layak. Langkah 6–9 menambah kekuatan.
