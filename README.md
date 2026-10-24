# BioTrace Indonesia

Prototipe hackathon `[MVP]` untuk memeriksa klaim nama ikan pada hasil eDNA yang sudah diproses lab. Mesin berbasis aturan (tanpa ML, tanpa internet) menentukan tingkat nama yang didukung bukti, nilai A–D, penyebab ketidakpastian, dan keputusan: Aman dilaporkan, Dengan catatan, Wajib verifikasi, atau Jangan dipakai.

BioTrace menghasilkan **laporan verifikasi pendukung**, bukan dokumen AMDAL resmi. Deteksi DNA bukan bukti pasti ikan hidup di lokasi.

Dokumen acuan ada di [`docs/`](docs/README.md). Sumber kebenaran tertinggi: [01_KONSEP_INDUK](docs/01_KONSEP_INDUK.md), lalu [09_LOG_KEPUTUSAN](docs/09_LOG_KEPUTUSAN.md). Aturan kerja agent: [AGENTS.md](AGENTS.md).

## Status saat ini

| Area | Status |
|---|---|
| Mesin inti, API, dashboard, PDF/CSV, jejak audit | Berjalan; tes `not slow` dan T-PERF lulus di perangkat tim |
| Aturan | `r0.4` aktif (D-030, D-033); semua ambang **usulan tim, belum dikalibrasi ahli** |
| Kamus Indonesia `data/reference/v0.3` (D-034, **diusulkan**) | Kamus bawaan. 65 sekuens 12S MiFish GenBank (V2/V3) dari 38 spesies, semua dari spesimen luar Indonesia atau asal kosong, sehingga klaim yang bertumpu padanya tidak pernah "Aman" (R-DEC-09). Checklist 62 baris: 24 primer (v0.2, D-032), 27 sekunder, 11 berita. Spesies berreferensi: Matano 10/32, Mahalona 5/10, Towuti 6/19, Masapi 1/1. **Cakupan endemik 0/19**. v0.1/v0.2 tetap utuh |
| Demo | Data dan kamus **SIMULASI** di `data/demo/matano_SIMULASI_v3/`; hasil cadangan di `precomputed/` |
| Fitur P1/P2 (D-031) | Verifikasi kode laporan, catatan ahli, usulan sekuens, peta lokasi tersamar, tampilan ponsel, CI, cocok ulang, agregasi celah, templat lab (`templates/`) |
| Validasi | LOSO r0.4 di `validation/results/`: Malili v0.3 (n 65) M3 0,092 vs baseline BLAST-97% 0,462, M2 0,908; Lake St. Pierre `CA-QC` (mode validasi, n 234) M3 0,197 vs 0,419, M2 0,803. M1 = 0 bersifat struktural (tidak ada spesimen `ID`, D-034). Juga LOSO pustaka 12S Guyana (Teleo1/12S-V5). Bukan bukti akurasi MiFish Indonesia |

## Persiapan

Butuh: [uv](https://docs.astral.sh/uv/) (memasang Python 3.11), Node.js 22 + npm, dan NCBI BLAST+ 2.14+ (di Windows dipasang otomatis ke `.tools/` oleh `setup`).

```bash
uv run python scripts/project.py setup
```

Setiap perintah `make <tugas>` di [Makefile](Makefile) setara dengan `uv run python scripts/project.py <tugas>`:

| Tugas | Isi |
|---|---|
| `setup` | Pasang dependensi Python/npm, BLAST (Windows), siapkan data |
| `test` | `ruff format --check`, `ruff check`, `pytest -m "not slow"` |
| `test-slow` | Uji kinerja T-PERF (200 sampel × 2.000 ASV) |
| `build` | Ekspor skema pydantic → TypeScript, lalu bangun `web/dist` |
| `demo` | Bangun web dan jalankan API di http://127.0.0.1:8000 |
| `dev` | API `--reload` + Vite dev server |
| `precompute` | Simpan run demo terverifikasi ke `precomputed/` |
| `ref-build` | Bangun blastdb kamus demo |

## Menjalankan demo

```bash
uv run python scripts/project.py demo
```

Buka http://127.0.0.1:8000, klik **Muat data demo (SIMULASI)**. Bila `blastn` tidak ditemukan, API memuat hasil dari `precomputed/matano_SIMULASI_v3_<versi aturan>/` dan dashboard menampilkan keterangan "Hasil pra-hitung". Cadangan ini hanya untuk data demo, bukan untuk unggahan pengguna.

CLI tersedia sebagai `uv run biotrace {run,verify,ref,validate}`; lihat [05 §7](docs/05_ARSITEKTUR.md).

## Sebelum vs selama hackathon

> Bagian ini wajib diisi oleh manusia (tim), bukan agent, sesuai [01 §10](docs/01_KONSEP_INDUK.md).

**Sudah ada sebelum hackathon:**

- _(diisi tim)_

**Dibuat selama hackathon:**

- _(diisi tim)_

## Tim

Tim Exastra: Bramantyo Kunni Nurrisqi (produk & validasi), Bagus Athallah (backend & data), Agathan Khairy Bowo Laksono (frontend & laporan).
