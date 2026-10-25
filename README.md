# BioTrace Indonesia

Prototipe hackathon `[MVP]` untuk memeriksa klaim nama ikan pada hasil eDNA yang sudah diproses lab. Mesin berbasis aturan (tanpa ML, tanpa internet) menentukan tingkat nama yang didukung bukti, nilai A–D, penyebab ketidakpastian, dan keputusan: Aman dilaporkan, Dengan catatan, Wajib verifikasi, atau Jangan dipakai.

BioTrace menghasilkan **laporan verifikasi pendukung**, bukan dokumen AMDAL resmi. Deteksi DNA bukan bukti pasti ikan hidup di lokasi.

Dokumen acuan ada di [`docs/`](docs/README.md). Sumber kebenaran tertinggi: [01_KONSEP_INDUK](docs/01_KONSEP_INDUK.md), lalu [09_LOG_KEPUTUSAN](docs/09_LOG_KEPUTUSAN.md). Aturan kerja agent: [AGENTS.md](AGENTS.md).

## Status saat ini

| Area | Status |
|---|---|
| Mesin inti, API, dashboard, PDF/CSV, jejak audit | Berjalan; tes `not slow` dan T-PERF lulus di perangkat tim |
| Aturan | `r0.4` aktif (D-030, D-033); semua ambang **usulan tim, belum dikalibrasi ahli** |
| Kamus Indonesia aktif `data/reference/v0.5` (D-037/D-038, Disetujui) | 999 sekuens 12S MiFish dari 630 spesies; 133 sekuens dari spesimen Indonesia. Tambahan 33 sekuens Rasborinae dari 28 spesies + checklist air tawar nasional. v0.1–v0.4 tetap utuh |
| Demo | **Data eDNA asli** Marwayana dkk. 2022 (MiFish-U, terumbu Indonesia, CC0) lewat tombol "Muat data eDNA asli Indonesia" (D-036), dan demo **SIMULASI** Matano berlabel |
| Fitur P1/P2 (D-031) | Verifikasi kode laporan, catatan ahli, usulan sekuens, peta lokasi tersamar, tampilan ponsel, CI, cocok ulang, agregasi celah, templat lab (`templates/`) |
| Validasi | LOSO r0.4 di `validation/results/`: Malili v0.3 (n 65) M3 0,092 vs baseline BLAST-97% 0,462, M2 0,908; Lake St. Pierre `CA-QC` (mode validasi, n 234) M3 0,197 vs 0,419, M2 0,803. M1 = 0 bersifat struktural (tidak ada spesimen `ID`, D-034). Juga LOSO pustaka 12S Guyana (Teleo1/12S-V5). Bukan bukti akurasi MiFish Indonesia |

Untuk pemeriksaan: **[Paket juri](docs/17_KESIAPAN_JURI.md)**. Persetujuan implementasi D-034–D-037 tercatat di D-038; tidak menggantikan tinjauan ahli. Celah endemik Malili tetap 0/19 spesies berreferensi. Snapshot sumber parsial dan bahan COI/teleo tidak otomatis masuk kamus MiFish.

LOSO lengkap v0.5: 630 spesies/999 query; M2 92,49%, M3 7,51% vs baseline 32,53%. Pada uji tanpa sekuens dirinya sendiri (589 query), M4 20,37% dan M5 77,76% menunjukkan biaya kehati-hatian; ini eksperimen pustaka internal, bukan akurasi lapangan. Seluruh metrik, penyebut, dan batas dijelaskan di [paket juri](docs/17_KESIAPAN_JURI.md).

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

Demo asli memakai kamus v0.5 dan hasil pra-hitung terverifikasi di `precomputed/edna_asli_marwayana2022_r0.4_v0.5/`. Sumber dan asumsi dataset masuk fingerprint serta tampil di UI/PDF. Untuk membangun ulang: `uv run python scripts/prepare_jury.py precompute`; untuk memeriksa aset: `uv run python scripts/prepare_jury.py check`.

BLAST memiliki anggaran eksekusi 600 detik, dapat diatur lewat `BIOTRACE_BLAST_TIMEOUT_SECONDS` (1–3600). Dataset nyata tidak dijanjikan selalu selesai kurang dari dua menit; lihat durasi dalam manifest/ringkasan. Hasil parsial tidak diterbitkan saat timeout. Pengaturan ini tidak mengubah ambang biologis r0.4.

## Sebelum vs selama hackathon

> Bagian ini wajib diisi oleh manusia (tim), bukan agent, sesuai [01 §10](docs/01_KONSEP_INDUK.md).

**Sudah ada sebelum hackathon:**

- _(diisi tim)_

**Dibuat selama hackathon:**

- _(diisi tim)_

## Tim

Tim Exastra: Bramantyo Kunni Nurrisqi (produk & validasi), Bagus Athallah (backend & data), Agathan Khairy Bowo Laksono (frontend & laporan).
