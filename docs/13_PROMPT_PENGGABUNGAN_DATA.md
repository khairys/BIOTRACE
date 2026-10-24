# 13 — Prompt penggabungan data repo Bagus ke repo utama

Salin seluruh blok di bawah ke Claude Code milik Bagus, dijalankan di klon `https://github.com/khairys/BIOTRACE` (repo utama), dengan repo lama Bagus (`https://github.com/BagusAth/BIOTRACE`) diklon di folder terpisah sebagai bahan.

---

```text
Kamu bekerja di repo utama BioTrace (https://github.com/khairys/BIOTRACE). Tugasmu:
memindahkan data kaya dari repo lama saya (https://github.com/BagusAth/BIOTRACE, klon di
folder terpisah, hanya dibaca) ke kamus berversi baru v0.3 di repo utama, mengikuti aturan
r0.4 yang sudah disiapkan.

BACA DULU, berurutan: AGENTS.md, CLAUDE.md, docs/01_KONSEP_INDUK.md, docs/09_LOG_KEPUTUSAN.md
(terutama D-029 sampai D-033), docs/04_SPESIFIKASI_DATA.md §2 dan §5 (R-CUR), docs/03 R-NAME-01
dan R-DEC-09, docs/12_BASELINE_IMPLEMENTASI.md. Prioritas bila konflik: 01 > 09 > 03 = 04.

KONTEKS:
- Kamus aktif saat ini data/reference/v0.2: checklist nyata 18 ikan introduksi Malili dari
  Herder 2012 dan Tantu & Nilawati 2007 (source_quality primer), 0 sekuens.
- Aturan aktif r0.4 (D-033): spesimen luar Indonesia/asal kosong dari spesies in_indonesia=true
  BOLEH dipakai tetapi diberi peringatan; checklist boleh bersumber sekunder/berita bila ditandai
  source_quality; klaim yang hanya bertumpu pada bukti itu tidak pernah "safe" (R-DEC-09).
- Data di repo lama: data/ref/v0.1/ref12S_taksonomi.csv dan aksesi_dicek.csv (896 aksesi
  GenBank dari mitohelper), checklist_malili.csv (termasuk endemik), status.csv (IUCN via GBIF),
  alias.csv, jalur_masuk.csv, sumber/invasif.csv, data/test/lake_st_pierre/ref/ (kamus 12S
  Kanada), data/test/results/.

ATURAN KERAS (jangan dilanggar):
- A1: jangan mengarang apa pun. Setiap baris wajib menunjuk sumber yang tercatat di sources.csv.
  Ingatan model BUKAN sumber.
- A12: jangan mengubah data/reference/v0.1, v0.2, raw/ yang sudah ada, atau precomputed/.
- A13: pakai file MENTAH yang sudah ada di laptop saya (folder data/raw/ repo lama) lewat cara
  manual scripts/fetch_instructions.md §6: salin byte-per-byte ke raw/, cocokkan SHA-256 dengan
  data/ref/v0.1/manifest.csv repo lama, catat di raw/DOWNLOAD_LOG.md. Hanya file yang hilang atau
  hash-nya tidak cocok yang diunduh ulang lewat scripts/fetch_data.py. Jangan memakai berkas
  turunan (ref12S.fasta, ref12S_taksonomi.csv, kelengkapan*.csv) sebagai sumber. Mesin inti
  (biotrace_core/) tidak boleh memanggil jaringan.
- A5: tidak ada sekuens eDNA/lingkungan (V4) di kamus.
- R-CUR-05: semua sekuens dipotong ke daerah MiFish-U lewat alat kurasi yang ada
  (biotrace_core/reference/curate.py, trim.py). Yang gagal dipotong ditolak, tidak dipaksa.
- Spesies yang tidak tercatat di Indonesia (in_indonesia=false) tidak masuk kamus Indonesia.
- Jangan mengubah ambang numerik di rules YAML. Bila perlu aturan baru: buat r0.5, catat di 09
  dengan status Diusulkan, perbarui tes, lalu berhenti dan tanya saya.
- Kerja di branch baru `data/merge-bagus`. Jangan push ke main, jangan merge.

LANGKAH:
1. Branch `data/merge-bagus`. Jalankan `uv run python scripts/project.py test` untuk memastikan
   titik awal hijau.
2. Tabel kurasi tim: salin checklist_malili.csv, status.csv, alias.csv, jalur_masuk.csv,
   sumber/invasif.csv dari repo lama ke raw/bagus_ref_v0.1/ apa adanya (byte sama), tambahkan
   README.md (asal: repo BagusAth/BIOTRACE commit <hash>, tanggal, isi) dan catat SHA-256 di
   raw/DOWNLOAD_LOG.md. Ini sumber sekunder: tabel kurasi tim, bukan file publikasi.
3. Sekuens dari file mentah lokal: salin data/raw/biotrace_ref_malili_v0.1.zip (dan isinya),
   data/raw/mitohelper/ (12S-seqs-derep-uniq.qza, 12S-tax-derep-uniq.qza), data/raw/genbank/
   esummary_*.json, data/raw/gbif/*.json dari repo lama ke raw/malili12s_mitohelper/ apa adanya.
   Cocokkan SHA-256 dengan manifest.csv repo lama dan simpan manifest itu sebagai
   manifest_rekan.csv. Sekuens diambil dari FASTA di dalam .qza/zip (arsip zip; ekstrak ke folder
   kerja, bukan menimpa raw/); voucher dan negara dari esummary_*.json. Bila esummary tidak memuat
   /specimen_voucher atau /country untuk suatu aksesi, barulah ambil GenBank flat file untuk
   aksesi itu saja lewat dataset baru di scripts/fetch_data.py.
4. Buat builder `prepare_indonesia_v03()` di scripts/prepare_data.py (pola sama dengan
   prepare_indonesia_v02), yang membangun data/reference/v0.3 dari v0.2 + data di atas:
   a. sequences: dari FASTA mitohelper + metadata esummary (flat file hanya untuk yang kurang). voucher_level: V2 bila ada /specimen_voucher; V3 bila
      tanpa voucher tetapi REFERENCE terbit di jurnal (bukan "Unpublished"/"Direct Submission");
      selain itu tetap masuk metadata tetapi curation_status rejected dengan alasan no_voucher.
      specimen_country dari /country atau /geo_loc_name: "ID" bila Indonesia, selain itu nama
      negaranya, kosong bila tidak ada. source_db genbank, license dari kebijakan NCBI.
      Lewatkan semua sekuens melalui curate_records (R-CUR, termasuk pemotongan MiFish dan
      konflik R-CUR-08). Simpan curation_report.
   b. taxa: nama dari GenBank /organism dan tabel tim; in_indonesia true hanya bila tercatat di
      checklist v0.2/tabel tim atau GBIF country=ID menurut kolom sumber_tercatat repo lama
      (catat sumbernya). Isi genus/family dari sumber; order kosong bila sumber tidak memberi.
   c. checklist: semua baris v0.2 tetap (primer). Tambahkan baris checklist_malili.csv dengan
      source_quality=sekunder (sumber Kottelat/Herder 2006/ensiklopedia/FishBase karena PDF-nya
      belum ada di raw/) dan source_quality=berita untuk Mongabay/Bisnis.com. Jangan menimpa baris
      primer; bila konflik status, simpan keduanya di notes dan pakai yang primer.
   d. status: IUCN dari status.csv repo lama (sumber "IUCN Red List via GBIF species API", type
      database). invasive_flag hanya bila sumber_invasif menyebut sumber.
   e. aliases: alias.csv repo lama (reviewed_by_expert=false).
   f. sources.csv: tambahkan semua sumber yang dikutip dengan type yang benar
      (peer_reviewed/book/database/news) dan tandai yang file-nya tidak ada di raw/.
   Tulis CHANGELOG yang jujur: berapa diterima/ditandai/ditolak dan alasannya.
5. Ubah kamus bawaan ke v0.3 (api/main.py reference_root, biotrace_core/cli.py --ref default,
   scripts/project.py setup).
6. Tes baru tests/test_reference_v03.py: memuat di mode normal; tidak ada V4; semua sekuens
   accepted sudah region_trimmed; tidak ada spesies in_indonesia=false yang accepted; setiap baris
   checklist punya source_id yang ada di sources.csv; baris non-primer bertanda sekunder/berita;
   v0.1 dan v0.2 utuh (hash manifest).
7. Validasi: jalankan `uv run biotrace validate loso --ref data/reference/v0.3 --out
   validation/results/<tanggal>_MALILI_r0.4.json` (bila jumlah spesies berreferensi cukup).
   Untuk Lake St. Pierre: susun ulang kamus Kanada sebagai modul validasi
   data/external/lake_st_pierre/<versi>/ (sumber diunduh lewat fetch_data.py, module "CA-QC"),
   lalu jalankan LOSO mode validasi. Hanya tulis angka dari run nyata.
8. Jalankan `uv run python scripts/project.py test`, `test-slow`, dan `build`. Demo SIMULASI
   harus tetap sama (bandingkan summary precomputed/matano_SIMULASI_v3_r0.4).
9. Catat D-034 di docs/09 (status Diusulkan): isi v0.3, angka kurasi, keputusan voucher di atas,
   dan apa yang perlu tinjauan ahli. Perbarui README bagian Status.
10. Commit per area (`data: ...`, `scripts: ...`, `tests: ...`, `docs: ...`), push branch, buka
    PR ke main dengan ringkasan angka dan daftar risiko. Jangan merge.

BERHENTI DAN TANYA bila: unduhan NCBI gagal sebagian, alat kurasi menolak hampir semua sekuens,
ada aturan yang harus diubah, atau sebuah nama/status tidak punya sumber yang bisa dikutip.

HASIL AKHIR yang saya harapkan: link PR, jumlah sekuens diterima/ditandai/ditolak per alasan,
jumlah spesies berreferensi per danau, cakupan endemik, hasil LOSO (bila ada), dan daftar item
yang menunggu tinjauan ahli.
```
