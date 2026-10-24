# Templat lapangan dan permintaan lab (F36) `[P2]`

Kolom diambil langsung dari model data (`biotrace_core/models.py`) dan spesifikasi [04 §1](../docs/04_SPESIFIKASI_DATA.md). Templat ini hanya struktur kosong; tidak memuat contoh nama spesies atau koordinat.

| Berkas | Untuk | Kolom wajib |
|---|---|---|
| `metadata_template.csv` | Tim lapangan, satu baris per sampel/replikat, termasuk kontrol negatif | `sample_id, site_id, waterbody_id, latitude, longitude, collection_date, sample_type, extraction_batch, marker` |
| `reads_long_template.csv` | Lab, tabel bacaan format panjang | `asv_id, sample_id, reads` |
| `taxonomy_template.csv` | Lab, bila FASTA ASV tidak diserahkan | `asv_id, taxon, rank, pct_identity` |

## Daftar permintaan standar ke lab

Minta lab menyerahkan, untuk setiap run sekuensing:

1. **FASTA ASV** (`asv_id` sama dengan tabel bacaan). Dengan FASTA, BioTrace mencocokkan ulang ke kamusnya sendiri.
2. **Tabel bacaan** per `asv_id` × `sample_id`, angka bilangan bulat, termasuk baris kontrol negatif.
3. **Kontrol negatif per batch ekstraksi** (`sample_type`: `kontrol_negatif_lapangan`, `kontrol_negatif_ekstraksi`, atau `kontrol_negatif_pcr`; `extraction_batch` sama dengan sampel yang diawasinya). Tanpa kontrol, klaim tidak bisa lolos audit L4.
4. **Replikat** per lokasi dan nomornya (`replicate`).
5. **Marker dan primer** yang dipakai (`marker`, mis. `12S_MiFish_U`).
6. Bila tanpa FASTA: **taksonomi lab** dengan persen identitas terbaik dan runner-up, serta nama database referensi (`reference_db`).

Data tidak dikirim ke layanan luar; seluruh analisis berjalan di perangkat lokal.
