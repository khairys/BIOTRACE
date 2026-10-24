# 12 — Baseline implementasi prototipe `[MVP]`

Dasar: instruksi pengguna setelah audit, 24 Oktober 2026: implementasikan keseluruhan berdasarkan docs, dataset tertunda menyusul. Konfirmasi berikutnya: accepted + flag conflict dan wajib turun tingkat (K-004); parameter thread dipisah dari fingerprint (K-006). Ini otorisasi pengerjaan prototipe, bukan kalibrasi ilmiah.

- Rules r0.1 disimpan; **r0.2** menjadi baseline eksekusi pertama dengan parameter numerik tetap dari 03/04 dan perubahan konflik yang dikonfirmasi manusia. Semua ambang berlabel usulan tim, belum dikalibrasi ahli.
- K-004: duplikat lintas spesies yang lolos seluruh syarat kurasi berstatus accepted dengan flag conflict. Semua pasangan identik dipertahankan agar kandidat tidak menyembunyikan ambiguitas; flag tidak mengizinkan V4/asal asing/marker salah.
- K-006: thread, lokasi executable, dan durasi dicatat dalam execution; parameter analitis, versi BLAST, input, kamus dan aturan masuk fingerprint.
- K-005/K-007: mode simulation eksplisit, kamus demo terpisah, nama berkas memuat SIMULASI, seluruh tabel berflag true; FASTA mewarisi flag run. Reads lebar mengecualikan is_simulated dari kolom sampel. Mode normal hanya menggunakan modul ID, spesimen ID dan data nonsimulasi. Mode validation mengizinkan marker luar yang dinyatakan sumber tanpa klaim Indonesia.
- K-008: angka kurasi dari 04 dan bobot prioritas dari 03 ikut YAML. Median dihitung hanya dari kandidat dalam satu impor dan satu marker yang telah berhasil dipotong. Bila tidak ada kandidat, impor tidak menerima sekuens.
- K-011: P_missing null untuk LCA lintas genus; tidak mengarang genus. Label endemik/terancam/invasif pada agregat memerlukan dukungan semua kandidat yang diketahui. Label possible_unreferenced_endemic tetap terpisah. Jika tidak ada takson bersama sampai ordo, hasil unknown.
- Konfirmasi manusia berikutnya: contoh E2/E3 boleh menampilkan endemic dan possible_unreferenced_endemic sekaligus, mengikuti R-SCORE-04. Tambahan label tersebut tidak mengubah keputusan.
- K-009: alat dan halaman validasi diimplementasikan sebagai kebutuhan teknis MVP; validasi biologis/ahli tetap mengikuti tahap P1 pada 01. Angka hanya dari run nyata, dan hasil simulasi tidak dipresentasikan sebagai validasi ilmiah.
- K-010: salinan dokumen project/ dipertahankan, tanpa menambah materi pitch.
- Dataset Indonesia yang belum layak tidak dipromosikan menjadi kamus aktif. Manifest kamus nyata kosong menjelaskan status kesiapan; dashboard dapat menjalankan demo SIMULASI dan menerima kamus lokal berversi yang telah dikurasi.

Dokumen ini menjelaskan pilihan implementasi konservatif dalam lingkup instruksi manusia. Persetujuan taksonomi, status, keanggotaan kompleks, dan kalibrasi ambang tetap membutuhkan ahli sesuai AGENTS. Entri log keputusan lama dipertahankan.
