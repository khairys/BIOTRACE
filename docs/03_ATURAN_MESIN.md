# 03 — Spesifikasi Ilmiah dan Aturan Mesin

| Atribut | Isi |
|---|---|
| Versi dokumen | 1.0 · 24 Oktober 2026 |
| Versi aturan | **r0.1** (`biotrace_core/rules/rules_r0.1.yaml`) |
| Status ambang | **Usulan tim, belum dikalibrasi ahli.** Semua angka adalah parameter berversi |
| Tunduk pada | `01_KONSEP_INDUK.md`, `09_LOG_KEPUTUSAN.md` |
| Basis | PRD v2 (aturan penamaan, skor L1–L4, matriks keputusan), ditambah kompleks, level voucher, dan aturan celah kerabat dari riset 24 Oktober 2026 |

Setiap aturan punya ID `R-<AREA>-<nomor>`. Kode dan tes wajib menyebut ID ini (aturan AGENTS.md §3).

---

## 0. Gambaran pipeline

```
Input (reads, metadata, FASTA | taxonomy lab)
  │
  ├─ Tahap 0  PRA-PROSES   R-PRE-*    bentuk tabel panjang, filter data nyasar, kontrol negatif, bentuk klaim
  ├─ Tahap 1  PENAMAAN     R-NAME-*   BLAST ke kamus wilayah → tingkat nama aman
  ├─ Tahap 2  PENILAIAN    R-SCORE-*  L4, L1, L2 (skor) + L3 (label) → nilai A–D
  ├─ Tahap 3  PENYEBAB     R-CAUSE-*  referensi / marker / sampel / lokasi
  ├─ Tahap 4  KEPUTUSAN    R-DEC-*    safe / with_note / must_verify / do_not_use + tindak lanjut
  ├─ Tahap 5  ASAL-USUL    R-ORIG-*   teks "kemungkinan"
  ├─ Tahap 6  CELAH        R-COV-*, R-GAP-*   peta kelengkapan + daftar prioritas barcode
  └─ Tahap 7  AUDIT        R-AUD-*    SHA-256, versi, sidik jari laporan
```

Semua tahap adalah fungsi murni. Urutan output selalu disortir (`site_id`, lalu `asv_id`).

---

## 1. Parameter r0.1

| Parameter | Nilai | Dipakai di | Keterangan |
|---|---|---|---|
| `marker_default` | `12S_MiFish_U` | semua | Marker utama |
| `min_query_coverage` | 0.90 | R-NAME-02 | Kecocokan BLAST harus menutup ≥90% panjang ASV |
| `hit_window_pct` | 0.5 | R-NAME-04 | Jendela kecocokan dari kemiripan terbaik (poin persen) |
| `unknown_below_pct` | 95.0 | R-NAME-03 | Di bawah ini = tidak dikenal |
| `species_min_pct` | 98.0 | R-NAME-07 | Minimal untuk tingkat spesies |
| `congener_gap_policy` | `strict` | R-NAME-08 | `strict`: satu kerabat tanpa referensi sudah cukup untuk menurunkan tingkat; `threshold`: turun bila P ≥ `reference_cause_p_missing` |
| `l1_high_pct` / `l1_high_gap` | 99.0 / 1.0 | R-SCORE-02 | Syarat L1 = 2 |
| `l1_mid_pct` / `l1_mid_gap` | 98.0 / 0.5 | R-SCORE-02 | Syarat L1 = 1 |
| `l1_penalty_ref_fraction_below` | 0.5 | R-SCORE-02 | L1 dikurangi 1 bila fraksi kerabat yang punya referensi < 0,5 |
| `reference_cause_p_missing` | 0.5 | R-CAUSE-01 | Penyebab "referensi" bila P ≥ 0,5 |
| `min_total_reads` | 10 | R-SCORE-06 | Total bacaan klaim di bawah ini → nilai maksimal D |
| `tag_jump_fraction` | 0.001 | R-PRE-02 | Bacaan < 0,1% dari total bacaan ASV itu dalam run dianggap data nyasar |
| `l4_full` | 1.0 | R-SCORE-01 | Fraksi replikat positif untuk L4 = 2 |
| `l4_partial` | 0.66 | R-SCORE-01 | Fraksi replikat positif untuk L4 = 1 |
| `l4_single_replicate_score` | 1 | R-SCORE-01 | Skor L4 bila lokasi hanya punya 1 replikat (disertai peringatan) |
| `allowed_voucher_levels` | `[V1, V2, V3]` | R-NAME-01 | Level voucher yang boleh mendukung klaim |
| `baseline_species_pct` | 97.0 | R-VAL-01 | Baseline pembanding "BLAST-97%" |

Format file YAML ada di `04_SPESIFIKASI_DATA.md` §7.

---

## 2. Tahap 0 — Pra-proses

**R-PRE-01 Bentuk tabel panjang.** Tabel bacaan format lebar (kolom pertama `asv_id`, kolom lain = `sample_id`) diubah ke format panjang (`asv_id`, `sample_id`, `reads`). Baris dengan `reads = 0` dibuang setelah konversi.

**R-PRE-02 Filter data nyasar.** Untuk setiap ASV, hitung `total_asv_reads` = jumlah bacaan ASV itu di semua sampel run. Bacaan sebuah sampel untuk ASV itu yang `< tag_jump_fraction × total_asv_reads` diubah menjadi 0, dan dicatat sebagai flag `tag_jump_removed` (jumlah baris dicatat di laporan).

**R-PRE-03 Kontrol negatif.** Sampel dengan `sample_type` diawali `kontrol_negatif` dikelompokkan per `extraction_batch`. Sebuah ASV diberi flag `in_negative_control` untuk sebuah klaim bila ASV itu punya bacaan > 0 (setelah R-PRE-02) di kontrol negatif mana pun pada `extraction_batch` yang sama dengan sampel lapangan positif dari klaim itu. Bila batch tidak punya kontrol negatif sama sekali, catat peringatan `no_negative_control_in_batch` (tidak mengubah skor di r0.1).

**R-PRE-04 Bentuk klaim.** Satu klaim = satu pasangan (`asv_id`, `site_id`) yang punya bacaan > 0 di ≥1 sampel lapangan (`sample_type = sampel`) di lokasi itu setelah R-PRE-02. `claim_id = "{site_id}__{asv_id}"`. Kontrol positif tidak membentuk klaim.

**R-PRE-05 Perairan.** Setiap `site_id` harus memetakan ke tepat satu `waterbody_id`. Bila satu lokasi punya lebih dari satu `waterbody_id`, proses berhenti dengan galat validasi.

---

## 3. Tahap 1 — Penamaan

### 3.1 Cakupan kamus

**R-NAME-01 Cakupan referensi.** Pencocokan memakai hanya sekuens yang memenuhi semua syarat:
- berada di modul kamus Indonesia aktif (`data/reference/<versi>/`), bukan `data/external/`;
- `curation_status = accepted`;
- `voucher_level ∈ allowed_voucher_levels` (V1–V3);
- `marker` sama dengan marker run;
- spesiesnya punya `in_indonesia = true` di `taxa.csv`.

### 3.2 Mode dengan FASTA

**R-NAME-02 BLAST.** Jalankan `blastn` untuk setiap ASV ke database kamus aktif (parameter di `05_ARSITEKTUR.md` §6). Buang hit dengan cakupan query < `min_query_coverage`. Ringkas menjadi **satu hit terbaik per spesies** (kemiripan tertinggi; bila sama, bitscore tertinggi; bila sama, `seq_id` terkecil secara alfabet).

**R-NAME-03 Tidak dikenal.** Bila tidak ada hit, atau kemiripan terbaik `best_pct < unknown_below_pct`, maka `reported_rank = unknown`, `reported_name = "tidak dikenal"`. Penyebab: `reference`. ASV dimasukkan ke daftar prioritas barcode (R-GAP-02). Hit terdekat disimpan hanya sebagai informasi "kerabat terdekat".

**R-NAME-04 Himpunan kandidat.** `S` = semua spesies dengan `pct ≥ best_pct − hit_window_pct`. Definisi selisih: `gap = best_pct − pct spesies terbaik di luar S`. Bila tidak ada spesies di luar S, `gap = ∞`.

**R-NAME-05 Kompleks.** Bila `|S| > 1` dan semua anggota S termasuk dalam satu kompleks di `complexes.csv` yang cakupannya memuat `waterbody_id` klaim, maka `reported_rank = complex`, `reported_name = label kompleks`. Penyebab: `marker`. Syarat tambahan: lihat R-NAME-08 untuk kerabat tanpa referensi.

**R-NAME-06 Tingkat takson bersama (LCA).** Bila `|S| > 1` dan R-NAME-05 tidak berlaku, laporkan tingkat takson terendah yang sama untuk semua anggota S (genus → famili → ordo). Penyebab: `marker`. Dua kecocokan 100% diperlakukan sama: BioTrace tidak memilih salah satu.

**R-NAME-07 Kandidat spesies.** Bila `|S| = 1` dan `best_pct ≥ species_min_pct`, spesies itu menjadi kandidat. Lanjut ke R-NAME-08.

**R-NAME-08 Celah kerabat (congener gap).** Ambil `U` = spesies satu genus dengan kandidat yang ada di checklist `waterbody_id` klaim tetapi **tidak** punya referensi yang memenuhi R-NAME-01.
- Bila `U` kosong → laporkan spesies (`reported_rank = species`).
- Bila `U` tidak kosong, `congener_gap_policy = strict`, dan semua anggota U **plus** kandidat termasuk satu kompleks yang cakupannya memuat perairan itu → turun ke **kompleks**. Penyebab: `reference`.
- Bila `U` tidak kosong dan `strict` (selain kasus di atas) → turun ke **genus**. Penyebab: `reference`.
- Bila `threshold`: turun ke genus hanya bila `P_missing ≥ reference_cause_p_missing`.

Aturan yang sama berlaku untuk hasil R-NAME-05. Kompleks hanya dipertahankan bila semua anggota U termasuk kompleks itu; bila tidak, turun ke genus dengan penyebab `reference`.

**R-NAME-09 Kemiripan menengah.** Bila `|S| = 1` dan `unknown_below_pct ≤ best_pct < species_min_pct`, laporkan genus. Penyebab: `reference`.

### 3.3 Mode tanpa FASTA (taksonomi lab)

**R-NAME-10 Spesies tidak tercatat di Indonesia.** Bila nama dari lab adalah spesies dengan `in_indonesia = false` atau tidak ada di `taxa.csv`, laporkan genusnya. Penyebab: `location`. (Pada mode FASTA aturan ini tidak terpicu karena R-NAME-01 sudah membatasi referensi.)

**R-NAME-12 Pakai kolom lab.** Tanpa FASTA, gunakan `taxon`, `rank`, `pct_identity`, `runner_up_taxon`, `runner_up_pct_identity`:
- `best_pct = pct_identity`.
- S = {taxon} ditambah runner-up bila `pct_identity − runner_up_pct_identity ≤ hit_window_pct`.
- Bila runner-up berada di luar jendela, `gap = pct_identity − runner_up_pct_identity`. Bila runner-up berada di dalam jendela, spesies terbaik di luar S tidak diketahui, sehingga `gap = 0` (konservatif). Bila runner-up kosong, `gap = ∞`.
- Bila `rank` lab di atas spesies, gunakan rank itu sebagai titik awal (tidak pernah dinaikkan ke spesies).
- Terapkan R-NAME-03 s.d. R-NAME-11 dengan data ini.
- Setiap klaim diberi catatan `assessed_with_lab_database = true` dan teks "dinilai dengan database lab".

### 3.4 Alias hibrida

**R-NAME-11 Alias.** Bila nama hasil (atau nama lab) ada di `aliases.csv`, misalnya spesies induk louhan, ganti `reported_name` dengan label alias ("kemungkinan louhan hibrida") dan `reported_rank = hybrid_alias`. Nama asli disimpan di `taxon_lab`/`best_match`. Tambahkan label L3 `hybrid_alias` dan `invasive` bila kategori alias itu invasif.

**Urutan evaluasi alias.** R-NAME-11 dievaluasi **sebelum** R-NAME-05 s.d. R-NAME-10. Bila nama lab (mode tanpa FASTA) atau semua anggota S (mode FASTA) ada di `aliases.csv` dengan alias yang sama, klaim langsung menjadi `hybrid_alias` dan aturan R-NAME-05 s.d. R-NAME-10 dilewati. Penyebab `marker` tetap ditambahkan bila `|S| > 1`.

### 3.5 Urutan tingkat

`species` < `complex` < `genus` < `family` < `order` < `unknown`. `hybrid_alias` diperlakukan setara `species` untuk penilaian, tetapi selalu membawa label invasif.

---

## 4. Tahap 2 — Penilaian

### 4.1 Skor

**R-SCORE-01 L4 Sinyal lab (0–2).** Untuk klaim di lokasi `site_id`: `n_rep` = jumlah sampel lapangan di lokasi itu, `n_pos` = jumlah sampel lapangan dengan bacaan ASV > 0, `f = n_pos / n_rep`.
- `n_rep ≥ 2` dan `f ≥ l4_full` → 2
- `n_rep ≥ 2` dan `f ≥ l4_partial` → 1
- `n_rep = 1` → `l4_single_replicate_score`, dengan peringatan `single_replicate`
- lainnya → 0

**R-SCORE-02 L1 Kamus (0–2).**
- `best_pct ≥ l1_high_pct` dan `gap ≥ l1_high_gap` → 2
- `best_pct ≥ l1_mid_pct` dan `gap ≥ l1_mid_gap` → 1
- lainnya → 0

Lalu dikurangi 1 (minimal 0) bila fraksi kerabat satu genus di checklist perairan yang punya referensi `< l1_penalty_ref_fraction_below`. Untuk klaim `unknown`, L1 = 0.

**R-SCORE-03 L2 Kewajaran lokasi (0–1).**
- Tingkat spesies/alias: 1 bila spesies (atau entri alias) ada di checklist `waterbody_id`; selain itu 0.
- Tingkat kompleks/genus/famili/ordo: 1 bila ≥1 spesies dari takson itu ada di checklist perairan; selain itu 0.
- `unknown`: 0, tanpa memicu penyebab lokasi.

**R-SCORE-04 L3 Label (tidak mengubah skor).** Label yang mungkin:
- `endemic`: takson yang dilaporkan, atau semua anggota S, endemik di checklist.
- `threatened`: kategori IUCN CR, EN, atau VU.
- `invasive`: berstatus invasif di `status.csv` atau lewat alias.
- `hybrid_alias`: dari R-NAME-11.
- `possible_unreferenced_endemic`: klaim di atas tingkat spesies atau `unknown`, dan genus (atau kerabat terdekat) punya spesies endemik di perairan itu yang belum punya referensi.

**R-SCORE-05 Total dan nilai.** `total = L1 + L2 + L4` (0–5). Pemetaan: 5 → **A**, 4 → **B**, 2–3 → **C**, 0–1 → **D**.

**R-SCORE-06 Batas maksimal D.** Nilai menjadi **D**, apa pun totalnya, bila:
- flag `in_negative_control` aktif, atau
- total bacaan klaim (jumlah di semua sampel lapangan lokasi itu) `< min_total_reads`.

Simpan alasan di `cap_reason`.

### 4.2 Peluang spesies asli belum di kamus

**R-SCORE-07 P_missing.** Untuk genus dari takson yang dilaporkan (atau kerabat terdekat bila `unknown`) di perairan klaim:

```
P_missing = (n_genus − r_genus) / n_genus
```

`n_genus` = jumlah spesies genus itu di checklist perairan. `r_genus` = jumlah yang punya ≥1 referensi memenuhi R-NAME-01. Bila `n_genus = 0`, `P_missing = null` dan catat `genus_not_in_checklist`.

---

## 5. Tahap 3 — Penyebab ketidakpastian

| ID | Penyebab | Pemicu |
|---|---|---|
| R-CAUSE-01 | `reference` | `P_missing ≥ reference_cause_p_missing`, atau `95 ≤ best_pct < 98`, atau penurunan oleh R-NAME-08, atau `unknown` |
| R-CAUSE-02 | `marker` | `|S| > 1` (termasuk kompleks dan LCA) |
| R-CAUSE-03 | `sample` | `in_negative_control`, atau `L4 = 0`, atau total bacaan < `min_total_reads` |
| R-CAUSE-04 | `location` | `L2 = 0` pada klaim selain `unknown`, atau R-NAME-10 |

**R-CAUSE-05 Fallback.** Bila klaim bernilai B–D atau `reported_rank ≠ species` tetapi belum punya penyebab, tetapkan dari lapisan terlemah dengan urutan: L4 < 2 → `sample`; L1 < 2 dan `best_pct < l1_high_pct` → `reference`; L1 < 2 lainnya → `marker`; L2 < 1 → `location`.

Invarian (wajib dites): setiap klaim B–D atau di atas tingkat spesies punya ≥1 penyebab.

### Tindak lanjut per penyebab

| Penyebab | Tindak lanjut |
|---|---|
| `reference` | Laporkan pada tingkat aman; masukkan ke daftar prioritas barcode |
| `marker` | Pakai marker kedua (COI atau 16S) atau survei tangkap |
| `sample` | Tinjau batch ekstraksi; ulang PCR; periksa kontrol negatif |
| `location` | Konfirmasi dengan survei; periksa kemungkinan sumber DNA lain (aliran dari hulu, keramba, limbah pasar) |

---

## 6. Tahap 4 — Keputusan

Aturan dievaluasi berurutan. Aturan pertama yang cocok yang dipakai.

| Urutan | ID | Kondisi | Keputusan |
|---|---|---|---|
| 1 | R-DEC-05 | `reported_rank = unknown` dan penyebab memuat `sample` | `do_not_use` |
| 2 | R-DEC-06 | `reported_rank = unknown` | `with_note`; teks: "ikan tidak dikenal, kemungkinan belum ada di kamus" |
| 3 | R-DEC-08 | Nilai A–B, tingkat spesies/alias, dan `L2 = 0` (catatan baru untuk perairan ini) | `with_note` (bila ada label L3: `must_verify`) |
| 4 | R-DEC-01 | Nilai A–B | `safe` |
| 5 | R-DEC-03 | Nilai C–D dan ada label L3 (`endemic`, `threatened`, `invasive`, `hybrid_alias`) | `must_verify` |
| 6 | R-DEC-02 | Nilai C tanpa label L3 | `with_note` |
| 7 | R-DEC-04 | Nilai D tanpa label L3 | `do_not_use` |

**R-DEC-07 Teks tambahan.**
- Label `invasive` dengan nilai C–D → tambahkan "Jangan dijadikan dasar pemberantasan sebelum dicek."
- Label `endemic` dengan nilai D → tambahkan "Klaim tidak dibuang agar tidak berujung kesimpulan 'tidak ada' yang keliru."
- Label `possible_unreferenced_endemic` → tambahkan "Kemungkinan ikan endemik yang belum ada di kamus."

Label L3 `possible_unreferenced_endemic` saja **tidak** memicu R-DEC-03 di r0.1; label itu tetap ditampilkan.

---

## 7. Tahap 5 — Kemungkinan asal-usul

**R-ORIG-01.** Setiap Evidence Card untuk takson yang punya entri di `checklist.csv`/`introductions.csv` menampilkan tiga hal, selalu dengan kata "kemungkinan":
1. **Status di lokasi**: asli, endemik, introduksi, invasif, atau tidak tercatat.
2. **Jalur masuk tercatat** (khusus introduksi): budidaya, perdagangan ikan hias, tebar benih, lepas tidak sengaja. Sumber dari `introductions.csv`.
3. **Kemungkinan sumber DNA lain**: aliran dari hulu, keramba, limbah pasar. Sumber dari `site_context.csv` bila diisi pengguna, atau teks umum.

**R-ORIG-02.** Kartu tidak pernah menyebut populasi atau sungai asal ikan.

---

## 8. Tahap 6 — Peta celah dan daftar prioritas barcode

**R-COV-01 Cakupan.** Untuk setiap (`waterbody_id`, genus) di checklist: `n` = jumlah spesies, `r` = jumlah dengan ≥1 referensi R-NAME-01, `P_missing = (n − r)/n`. Dihitung ulang setiap versi kamus dan disimpan di `coverage.csv` versi itu.

**R-COV-02 Ringkasan kamus.** Per versi: jumlah sekuens per status kurasi, per level voucher, jumlah spesies berreferensi, dan cakupan total per perairan (`Σr / Σn`).

**R-GAP-01 Prioritas spesies.** Untuk setiap spesies di checklist perairan proyek yang belum punya referensi, hitung skor: endemik +3, terancam +2, genusnya muncul dalam klaim run ini dengan penyebab `reference` +2, invasif +1. Urutkan menurun berdasarkan skor, lalu nama.

**R-GAP-02 ASV tidak dikenal.** Setiap ASV `unknown` masuk daftar bersama lokasi, total bacaan, dan kerabat terdekat (bila ada) sebagai petunjuk.

---

## 9. Tahap 7 — Audit

**R-AUD-01.** Hitung SHA-256 setiap file input (byte asli).

**R-AUD-02.** `run_fingerprint` = SHA-256 dari JSON kanonik (kunci disortir, tanpa spasi) berisi: hash input, `reference_version` + hash `manifest.json` kamus, `rules_version` + hash file YAML, versi `biotrace_core`, versi BLAST+, dan parameter efektif. **Waktu tidak dimasukkan.**

**R-AUD-03.** `report_fingerprint` = SHA-256 dari `claims.csv` kanonik (UTF-8, LF, kolom dan baris tersortir, angka diformat 2 desimal) digabung dengan `run_fingerprint`.

**R-AUD-04.** Input dan versi yang sama wajib menghasilkan `report_fingerprint` identik (diuji otomatis).

---

## 10. Teks alasan (Indonesia / Inggris)

Templat disimpan di `biotrace_core/rules/reasons_r0.1.yaml`. Contoh wajib:

| Kunci | Bahasa Indonesia | English |
|---|---|---|
| `unknown` | Kemiripan terbaik {best_pct}% di bawah ambang {unknown_below_pct}%. Spesies aslinya kemungkinan belum ada di kamus. | Best match {best_pct}% is below the {unknown_below_pct}% threshold. The true species is likely missing from the reference. |
| `complex` | {n} spesies dalam {window}% dari kecocokan terbaik, semuanya anggota {complex_label}. Marker ini tidak bisa membedakan mereka. | {n} species within {window}% of the best match all belong to {complex_label}. This marker cannot separate them. |
| `lca` | {n} spesies dalam {window}% dari kecocokan terbaik. Nama diturunkan ke {rank} {name}. | {n} species within {window}% of the best match. Name lowered to {rank} {name}. |
| `congener_gap` | {k} dari {n} kerabat {genus} di {waterbody} belum punya referensi. Spesies aslinya bisa salah satu dari mereka. | {k} of {n} {genus} relatives in {waterbody} have no reference. The true species may be one of them. |
| `mid_identity` | Kemiripan {best_pct}% cukup untuk genus, belum cukup untuk spesies (minimal {species_min_pct}%). | {best_pct}% identity supports genus but not species (minimum {species_min_pct}%). |
| `l1` | Kemiripan {best_pct}%, selisih dengan spesies lain {gap}%. | {best_pct}% identity, {gap}% gap to the next species. |
| `l2_yes` / `l2_no` | Tercatat / tidak tercatat di checklist {waterbody}. | Recorded / not recorded in the {waterbody} checklist. |
| `l4` | Terdeteksi di {n_pos} dari {n_rep} replikat. | Detected in {n_pos} of {n_rep} replicates. |
| `neg_control` | DNA yang sama muncul di kontrol negatif batch {batch}. | The same DNA appears in negative control of batch {batch}. |
| `low_reads` | Total bacaan {reads}, di bawah {min_total_reads}. | Total reads {reads}, below {min_total_reads}. |
| `not_in_indonesia` | Nama dari lab tidak tercatat di Indonesia; diturunkan ke genus. | The lab's name is not recorded in Indonesia; lowered to genus. |
| `alias` | Nama induk louhan; kemungkinan louhan hibrida (invasif). | Flowerhorn parent species; likely flowerhorn hybrid (invasive). |
| `lab_db` | Dinilai dengan database lab, bukan kamus BioTrace. | Assessed with the lab's database, not the BioTrace reference. |
| `limit` | Deteksi DNA bukan bukti pasti ikan hidup di lokasi. | DNA detection is not proof that the fish lives at the site. |

---

## 11. Fixture uji dan contoh kerja

> **Fixture FX-1 adalah data fiktif untuk tes perangkat lunak, bukan data ilmiah.** Nama genus sengaja dibuat fiktif agar tidak tertukar dengan data asli.

### 11.1 Fixture FX-1

Perairan `DANAU_UJI`. Marker `12S_MiFish_U`. Semua spesies `in_indonesia = true` kecuali yang ditandai.

| Spesies | Status di DANAU_UJI | Referensi (accepted, V1–V3) | Kompleks |
|---|---|---|---|
| *Piscis alpha* | endemik | ada | KX_PISCIS |
| *Piscis beta* | endemik | ada | KX_PISCIS |
| *Piscis gamma* | endemik | **tidak** | KX_PISCIS |
| *Gobio delta* | endemik | ada | — |
| *Gobio epsilon* | asli | ada | — |
| *Gobio lambda* | **tidak di checklist** (tercatat di perairan lain Indonesia) | ada | — |
| *Rasbo zeta* | asli | ada | — |
| *Rasbo eta* | asli | **tidak** | — |
| *Rasbo theta* | asli | **tidak** | — |
| *Rasbo iota* | asli | ada | — |
| *Tilapa omega* | introduksi, invasif | ada | — |
| entri alias `louhan_hybrid` | introduksi, invasif | — | — |
| *Piscis externus* | — (`in_indonesia = false`) | tidak ada di kamus Indonesia | — |

Kompleks `KX_PISCIS` (label "kompleks *Piscis* DANAU_UJI"): anggota alpha, beta, gamma; cakupan DANAU_UJI.
Alias: `Amphilophus citrinellus`, `Amphilophus labiatus` → `louhan_hybrid` ("kemungkinan louhan hibrida", invasif).

Cakupan: *Piscis* n=3, r=2, P=0,33 · *Gobio* n=2, r=2, P=0 (lambda tidak di checklist) · *Rasbo* n=4, r=2, P=0,50 · *Tilapa* n=1, r=1, P=0.

Lokasi `S1`: 3 replikat lapangan, `extraction_batch = B1`, satu kontrol negatif B1.

### 11.2 Contoh kerja (wajib menjadi tes)

| # | Input ringkas | Penamaan | L1 / L2 / L4 → nilai | Penyebab | Label L3 | Keputusan |
|---|---|---|---|---|---|---|
| E1 | *G. delta* 99,6%; terbaik di luar S *G. epsilon* 97,9%; 3/3 replikat; 1.200 bacaan | R-NAME-07/08 → **spesies** *G. delta* | 2 / 1 / 2 → **A** | — | endemic | `safe` |
| E2 | *P. alpha* 99,6%, *P. beta* 99,4%; di luar S terbaik 85,0%; 3/3; 800 bacaan | R-NAME-05 → **kompleks** *Piscis* DANAU_UJI (U={gamma} ⊂ kompleks) | 2 / 1 / 2 → **A** | marker | endemic | `safe` |
| E3 | *P. alpha* 99,8%, *P. beta* 98,9% (di luar jendela); 2/3; 500 bacaan | S={alpha}; U={gamma} ⊂ KX_PISCIS → **kompleks** | L1: gap 0,9 → 1 / 1 / 1 → **C** | reference | endemic | `must_verify` |
| E4 | *R. zeta* 99,5%; di luar S *R. iota* 97,0%; 3/3; 900 bacaan | U={eta, theta}, tanpa kompleks → **genus** *Rasbo* | 2 (fraksi ref 0,5, tidak < 0,5) / 1 / 2 → **A** | reference | — | `safe` |
| E5 | Terbaik *R. iota* 91,2%; 3/3; 300 bacaan | R-NAME-03 → **tidak dikenal** | 0 / 0 / 2 → C | reference | — (genus *Rasbo* tanpa spesies endemik) | `with_note` (R-DEC-06) |
| E6 | Seperti E5, tetapi ASV juga ada di kontrol negatif B1 | **tidak dikenal** | cap → D | reference, sample | — | `do_not_use` (R-DEC-05) |
| E7 | *G. epsilon* 96,5% (satu-satunya); 3/3; 400 bacaan | R-NAME-09 → **genus** *Gobio* | 0 / 1 / 2 → **C** | reference | — | `with_note` |
| E8 | *T. omega* 99,9%, gap 3,0; 3/3; 2.000 bacaan; ada di kontrol negatif B1 | **spesies** *T. omega* | 2/1/2 = 5 → cap **D** | sample | invasive | `must_verify` + teks "jangan dasar pemberantasan" |
| E9 | Tanpa FASTA. Lab: *Amphilophus citrinellus* 99,0%, runner-up *A. labiatus* 98,8%; 3/3; 600 bacaan | S={citrinellus, labiatus}, gap = 0 (R-NAME-12) → alias → **"kemungkinan louhan hibrida"** | 0 / 1 / 2 → **C** | marker | invasive, hybrid_alias | `must_verify`; catatan "dinilai dengan database lab" |
| E10 | Tanpa FASTA. Lab: *Piscis externus* 99,5%, tanpa runner-up; 3/3; 700 bacaan | R-NAME-10 → **genus** *Piscis* | 2 (P=0,33 → fraksi 0,67) / 1 / 2 → **A** | location | possible_unreferenced_endemic | `safe` + teks kemungkinan endemik |
| E11 | *G. delta* 99,6%, gap 1,7; 1/3; total 7 bacaan | **spesies** | 2 / 1 / 0 → 3, cap → **D** | sample | endemic | `must_verify` |
| E12 | *G. lambda* 99,7%, gap 2,0; 3/3; 1.000 bacaan | **spesies** *G. lambda* (U kosong) | 2 / **0** / 2 → **B** | location | — | `with_note` (R-DEC-08, catatan baru untuk perairan) |

Catatan E5: `unknown` tidak memicu penyebab lokasi (R-SCORE-03).

---

## 12. Validasi mesin

**R-VAL-01 Baseline.** "BLAST-97%" = laporkan spesies dari hit terbaik bila kemiripan ≥ `baseline_species_pct`, tanpa aturan lain.

**R-VAL-02 Leave-one-species-out.** Untuk setiap spesies X di kamus uji, hapus semua sekuens X, lalu cocokkan sekuens X ke kamus sisanya. Hitung:
- (a) proporsi yang dilaporkan sebagai spesies lain dengan keputusan `safe` = **nama keliru lolos sebagai aman**;
- (b) proporsi yang dilaporkan kompleks/genus/tidak dikenal;
- bandingkan dengan baseline R-VAL-01.

Rincian rencana uji ada di `06_VALIDASI_DAN_UJI.md`.

---

## 13. Sitasi metode (wajib di halaman Metode dan PDF)

- Polanco F. A. dkk. 2025. *Environmental DNA* 7(2):e70077. https://doi.org/10.1002/edn3.70077 (konsep skor keyakinan berlapis)
- Mai dkk. 2026. PhyloRef. *Ecology and Evolution* 16(3):e73159. https://doi.org/10.1002/ece3.73159 (kurasi anomali filogenetik)
- Marques V. dkk. 2021. GAPeDNA. *Diversity and Distributions* 27:1880–1892. https://doi.org/10.1111/ddi.13142 (analisis celah referensi)
- Zhu T. dkk. 2023. MitoFish/MiFish pipeline. *Mol Biol Evol* 40(3). https://doi.org/10.1093/molbev/msad035
- Thalinger B. dkk. 2021. Validation scale. *Environmental DNA*. https://doi.org/10.1002/edn3.189
