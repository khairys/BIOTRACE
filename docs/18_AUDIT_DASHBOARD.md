# 18 — Audit isi dashboard terhadap gambar referensi [MVP]

Tanggal: 25 Oktober 2026. Keputusan presentasi: D-041. Gambar pengguna adalah referensi tata letak, bukan sumber fakta ilmiah.

| Bagian | Kondisi dan implementasi |
|---|---|
| Ringkasan keputusan | Jumlah klaim, taksa, keputusan dan cakupan berasal dari run. Tambahan narasi dan kartu keputusan yang memfilter tabel. |
| Penyebab ketidakpastian | Sebelumnya tersebar per klaim; sekarang jumlah klaim per penyebab terlihat langsung. Penyebab boleh tumpang tindih. |
| Data masuk | Nama berkas tersimpan, hash, versi, peringatan dan provenance ditampilkan. Tidak mengklaim nama unggahan asli atau dimensi sampel yang tidak disimpan dalam respons hasil. |
| Tabel klaim | Tambahan tombol Lihat bukti, sorotan pilihan, penyebab dan fraksi celah. Tetap memiliki pencarian, filter, urut dan paginasi. |
| Evidence Card | Sebelumnya hanya drawer setelah klik; sekarang kartu langsung terlihat di samping tabel, dapat diperbesar. Pada layar kecil berada di bawah tabel. |
| Rincian bukti | Nama lab, nama laporan/tingkat, nilai, skor, kandidat, kemiripan, selisih kandidat, voucher, aksesi, replikat, bacaan, kontrol, alasan ID/EN, asal-usul, tindak lanjut dan batas interpretasi berasal dari klaim. |
| Cakupan kamus | Tambahan filter perairan dan distribusi voucher. Grafik 12 genus dengan celah tertinggi diberi batas tampilan; seluruh rincian bisa dibuka. Perairan tidak tercampur tanpa label. |
| Prioritas barcode | Semua baris dapat ditampilkan dan diunduh CSV, dengan perairan, lokasi dan petunjuk terdekat yang tersedia. Angka skor tidak disebut jumlah klaim terdampak. |
| Analisis tambahan | Perbandingan nama lab, grafik keputusan per lokasi dan peta tetap tersedia dalam bagian yang dapat dibuka. |

Data yang belum dapat ditampilkan sebagai fakta: galat terkalibrasi per nilai A–D, pengesahan ahli, koordinat/tanggal yang tidak ada pada sumber, jumlah referensi mentah per spesies sebelum kurasi, dan pengelompokan endemik per famili yang tidak disertakan dalam kontrak hasil. Tidak memakai angka dari gambar untuk mengisi kekosongan ini. Peta tetap menyatakan koordinat tidak tersedia bila kosong; tidak membuat titik perkiraan.

Pengelompokan endemik dan perbandingan sekuens mentah versus layak membutuhkan penggabungan snapshot checklist/taksonomi/sekuens yang tepat untuk **versi run**, melalui kontrak API tambahan. Ini pekerjaan lanjutan yang terpisah dari informasi cakupan genus yang sudah tersedia, bukan nilai yang boleh ditebak frontend.

Tidak ada perubahan aturan biologis, ambang, data mentah, referensi berversi, atau hasil pra-hitung. Label SIMULASI dan batas interpretasi tetap terlihat. Verifikasi perubahan: build TypeScript/Vite dan smoke browser untuk pilihan klaim, pembesaran kartu, bahasa, filter kosong, unduhan CSV serta lebar layar kecil.
