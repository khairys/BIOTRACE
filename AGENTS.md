# AGENTS.md — Aturan Wajib untuk Semua AI Agent di Repo BioTrace

> Berlaku untuk setiap AI agent (Claude Code, Cursor, Copilot, Codex, dll.) dan manusia yang bekerja di repo ini.
> Versi aturan: 1.0 · 24 Oktober 2026 · Pemilik: Tim Exastra

## 1. Baca dulu sebelum bekerja

Urutan baca minimum sebelum menulis kode atau dokumen:

1. `docs/01_KONSEP_INDUK.md`: identitas produk, keputusan, kebijakan klaim, glosarium. **Sumber kebenaran tertinggi.**
2. `docs/09_LOG_KEPUTUSAN.md`: keputusan terbaru, yang menimpa isi dokumen lain bila bertentangan.
3. Dokumen sesuai tugas:
   - Logika mesin (penamaan, skor, keputusan) → `docs/03_ATURAN_MESIN.md`
   - Skema file, kamus referensi, kurasi → `docs/04_SPESIFIKASI_DATA.md`
   - Fitur, halaman, kriteria penerimaan → `docs/02_PRD_v3.md`
   - Struktur repo, API, stack, cara menjalankan → `docs/05_ARSITEKTUR.md`
   - Tampilan dashboard, PDF, data demo → `docs/10_DESAIN_UI_LAPORAN_DEMO.md`
   - Tes dan validasi → `docs/06_VALIDASI_DAN_UJI.md`
   - Klaim angka dan dataset → `docs/07_REGISTRI_BUKTI_RINGKAS.md`

**Urutan prioritas jika ada konflik:** 01 > 09 > 03 = 04 > 10 > 02 > 05 > 06 > 07.
Jika menemukan konflik, jangan memilih sendiri. Catat di `docs/09_LOG_KEPUTUSAN.md` bagian "Konflik terbuka" lalu tanyakan ke manusia.

## 2. Aturan yang tidak boleh dilanggar

| ID | Aturan |
|---|---|
| A1 | **Jangan pernah mengarang data.** Ini mencakup sekuens, nomor aksesi, DOI, angka, kutipan, hasil uji, nama mitra, dan data wawancara. Fabrikasi = diskualifikasi lomba dan merusak kredibilitas produk. |
| A2 | **Data sintetis wajib berlabel `SIMULASI`** di nama file, di kolom `is_simulated=true` pada setiap baris, dan di layar dashboard. |
| A3 | **Jangan mengubah aturan mesin atau ambang secara diam-diam.** Semua ambang ada di `biotrace_core/rules/rules_r0.1.yaml`. Perubahan wajib: (1) naikkan versi aturan, (2) catat entri baru di 09, (3) perbarui tes. |
| A4 | **Referensi luar Indonesia tidak boleh mendukung nama spesies di laporan Indonesia.** Data Guyana Prancis, Lake St. Pierre, dll. hanya disimpan di `data/external/` dan hanya dipakai di mode validasi. *Sejak r0.4 (D-033):* sekuens dari spesimen luar Indonesia atau asal tidak diketahui **boleh** masuk kamus Indonesia hanya bila spesiesnya tercatat di Indonesia (`in_indonesia = true`); klaim yang hanya didukung sekuens seperti itu tidak pernah `safe` (R-DEC-09). Spesies yang tidak tercatat di Indonesia tetap tidak boleh. |
| A5 | **Sekuens eDNA (voucher level V4) tidak boleh masuk kamus referensi**, berapa pun kualitasnya. |
| A6 | **Mesin inti harus deterministik.** Tanpa unsur acak, urutan baris selalu disortir, dan input yang sama dengan versi yang sama harus menghasilkan sidik jari laporan yang identik. |
| A7 | **Tidak ada machine learning di MVP.** Semua keputusan berbasis aturan yang bisa dijelaskan. |
| A8 | **Mesin inti tidak boleh memanggil jaringan/internet.** Semua data dibaca dari file lokal yang berversi. |
| A9 | **Jangan menulis klaim pemasaran di kode atau UI** di luar daftar klaim yang diizinkan (`docs/07_REGISTRI_BUKTI_RINGKAS.md` §2). |
| A10 | **BioTrace tidak menerbitkan dokumen AMDAL resmi.** Teks UI dan laporan selalu menyebut "laporan verifikasi pendukung". |
| A11 | **Setiap kartu dan laporan memuat kalimat batas interpretasi**: deteksi DNA bukan bukti pasti ikan hidup di lokasi. |
| A12 | **Jangan menghapus data mentah atau file referensi berversi.** Versi baru dibuat sebagai folder baru. |
| A13 | **Unduhan data hanya lewat `scripts/fetch_data.py`** (atau cara manual di `scripts/fetch_instructions.md`), ke folder `raw/`, dengan log di `raw/DOWNLOAD_LOG.md`. Jangan mengunduh dari sumber lain atau menambahkan panggilan jaringan ke `biotrace_core/`. |
| A14 | **Nama spesies asli hanya boleh berasal dari file sumber di `raw/` atau kamus berversi.** Jangan mengisi nama spesies, checklist, atau status dari ingatan model. Tanpa file sumber, pakai nama fiktif berlabel SIMULASI. *Sejak r0.4 (D-033):* baris checklist/status boleh berasal dari sumber yang dikutip tetapi file-nya belum ada di `raw/` (mis. buku, situs, berita) bila ditandai `source_quality = sekunder` atau `berita` dan kutipannya tercatat di `sources.csv`; klaim yang bergantung padanya tidak pernah `safe`. Ingatan model tetap **bukan** sumber. |

## 3. Konvensi kode

### Python (`biotrace_core/`, `api/`)
- Python 3.11, type hints wajib, model data memakai **pydantic v2**.
- Format dan lint: `ruff format` + `ruff check`. Tes: `pytest`.
- Fungsi aturan mesin bersifat murni (pure function): input → output, tanpa I/O.
- Setiap aturan di 03 punya ID (misalnya `R-NAME-04`). Tulis ID itu di docstring fungsi dan di nama tes, misalnya `test_R_NAME_04_single_species_high_identity`.
- Semua angka ambang dibaca dari file rules YAML, tidak di-hardcode.
- Pengurutan stabil: sort berdasarkan kunci eksplisit (`asv_id`, `site_id`, `seq_id`) sebelum menulis output.

### Frontend (`web/`)
- React 18 + Vite + TypeScript (strict) + Tailwind. Grafik memakai Recharts.
- Tipe data API dibangkitkan dari skema pydantic (`scripts/export_schemas.py`) agar tidak berbeda.
- Semua teks UI dalam Bahasa Indonesia. Nama ilmiah ditulis miring (`<i>`).
- Label `SIMULASI` wajib terlihat jelas bila run memakai data demo sintetis.

### Penamaan
- Nama kolom, fungsi, variabel: bahasa Inggris, `snake_case` (Python) / `camelCase` (TS).
- Istilah domain mengikuti glosarium di `docs/01_KONSEP_INDUK.md` §11. Nilai enum keputusan memakai kode baku: `safe`, `with_note`, `must_verify`, `do_not_use` (label UI Indonesia: "Aman dilaporkan", "Dengan catatan", "Wajib verifikasi", "Jangan dipakai").

## 4. Cara bekerja

- **Tugas kecil dan jelas** → kerjakan, sertakan tes, jalankan `make test`.
- **Tugas yang menyentuh aturan, skema, atau keputusan** → baca dokumen terkait, usulkan perubahan di 09 dengan status `Diusulkan`, lalu tunggu persetujuan manusia.
- **Ragu atau dokumen diam** → tanya manusia. Jangan menebak domain biologi.
- **Commit message**: `area: ringkasan` (contoh: `naming: tambah aturan kompleks R-NAME-05`). Sebutkan ID aturan/fitur bila relevan.
- **Setiap PR** menyebut fitur (`F..`) atau aturan (`R-..`) yang dikerjakan dan status MVP/Roadmap-nya.

## 5. Penanda MVP vs Roadmap

Semua fitur dan bagian dokumen diberi tag:
- `[MVP]` = wajib ada untuk prototipe hackathon (submit 25 Oktober 2026 pukul 10:00 WIB).
- `[P1]` = bulan 1–6 setelah hackathon.
- `[P2]` = roadmap lebih jauh.

Jangan mengerjakan `[P1]`/`[P2]` sebelum semua `[MVP]` di area yang sama selesai dan lulus tes.

## 6. Kontak manusia

| Peran | Nama | Area keputusan |
|---|---|---|
| Ketua, produk & validasi | Bramantyo Kunni Nurrisqi | Arah produk, prioritas, bisnis |
| Backend & data | Bagus Athallah | Mesin, data, kamus referensi |
| Frontend & laporan | Agathan Khairy Bowo Laksono | Dashboard, Evidence Card, PDF |

Keputusan ilmiah (nama spesies, status endemik, ambang) **membutuhkan penasihat ahli ikan**. Selama belum ada, tandai semua ambang sebagai "usulan tim, belum dikalibrasi".
