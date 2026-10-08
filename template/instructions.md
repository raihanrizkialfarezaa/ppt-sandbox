# Instructions

Folder ini dibaca otomatis oleh `/generate` sebelum membuat presentasi.
Semua file `.md` di folder ini ikut dibaca. Baca `design-instructions.md` untuk aturan visual.

## 0. Cara memakai file ini

1. Konteks default repo ini adalah **seminar proposal (sempro) Tugas Akhir Raihan Rizki Alfareza, S1 Teknik Informatika UNESA**. Bila permintaan menyangkut proposal, sempro, sidang, atau penelitian ini, ikuti seluruh isi file ini tanpa menunggu diminta.
2. Bila permintaan jelas bertopik lain (misalnya pitch deck bisnis), pakai hanya bagian "Aturan umum" dan "Gaya bahasa", dan tetap pakai tema `unesa-sempro` kecuali pengguna menyebut tema lain.
3. **Urutan sumber kebenaran** bila ada konflik:
   1. Dokumen proposal yang sudah disetujui dosen: `Draft_Proposal_TA_Raihan_Rizki_Alfareza_23051204067_REVISI_28-09-2025_DIKERJAKAN.docx` (disebut "docx" di bawah).
   2. PPT eksisting: `Sempro_Raihan_Rizki_Alfareza_v23.pptx` (disebut "PPT eksisting").
   3. Permintaan pengguna pada sesi ini.
   Jika angka atau istilah di PPT eksisting berbeda dari docx, ikuti docx dan laporkan selisihnya di ringkasan akhir. Jangan mengarang angka, hasil, atau kutipan yang tidak ada di kedua sumber.

## 1. Identitas tetap (cover dan penutup)

| Elemen | Nilai |
|---|---|
| Penanda cover (kicker) | Seminar Proposal Tugas Akhir |
| Judul | Implementasi dan Evaluasi Arsitektur Event-Driven Microservices untuk Menjaga Konsistensi Transaksi pada Apotek Multicabang |
| Penulis | Raihan Rizki Alfareza |
| NIM / Prodi | NIM 23051204067, S1 Teknik Informatika, Fakultas Teknik |
| Pembimbing | I Made Suartana, S.Kom., M.Kom. |
| Institusi / tahun | Universitas Negeri Surabaya, 2026 |
| Logo | `assets/logos/unesa.png` (dipakai lewat `image:` pada slide cover) |
| Penutup | Judul "Terima kasih", subjudul "Mohon masukan dan arahan Bapak/Ibu Penguji.", tanpa tombol ajakan (`cta` dikosongkan) |

Judul tidak boleh diubah, dipersingkat, atau diparafrasekan pada cover.

## 2. Fakta terkunci (sudah ada di docx, jangan diubah)

**Masalah lapangan (Apotek Bisma, wawancara dan observasi 5 Juli 2026, narasumber Ibu Atik, pemilik)**
- 3 cabang aktif dan 1 gudang distribusi, tiap cabang punya kasir mandiri, gudang memakai Excel VBA, tidak ada sinkronisasi real-time.
- Sekitar 450 transaksi penjualan per hari (3 cabang). Rekonsiliasi 1 sampai 2 hari di cabang, 4 sampai 5 hari di gudang. Selisih antara stok fisik dan catatan sistem selalu muncul pada setiap rekonsiliasi bulanan.
- Pembingkaian yang benar: **data basi akibat catatan terpisah adalah masalah nyata yang sudah terjadi**; **lost update dan oversell adalah risiko bersyarat yang baru muncul bila sistem diintegrasikan**. Jangan menulis keduanya seolah sudah terjadi di Apotek Bisma.

**Lima masalah (Identifikasi Masalah)**: rekonsiliasi lambat; stok sistem tidak cocok dengan stok fisik; integrasi tanpa sinkronisasi berisiko lost update dan oversell; belum ada dasbor monitoring terpadu; konsekuensi tiap arsitektur belum terbukti.

**Empat rumusan masalah (RM) dan tujuan yang sejajar 1:1**
1. Merancang dan mengimplementasikan arsitektur event-driven microservices pada apotek multicabang dengan pembagian tanggung jawab fungsional dan sumber kebenaran data per layanan.
2. Konsistensi data pada masing-masing arsitektur saat terjadi konkurensi transaksi.
3. Keandalan transaksi pada masing-masing arsitektur saat terjadi gangguan atau kegagalan proses transaksi.
4. Perbandingan konsistensi data dan keandalan transaksi pada tiga kondisi arsitektur dengan beban kerja dan kondisi pengujian yang setara.

Performa dan kompleksitas operasional adalah **dimensi pendukung** yang dilaporkan terpisah, bukan RM.

**Tiga kondisi arsitektur (nama lengkap wajib, lihat bagian 3)**
- Monolith Terpusat: satu aplikasi Laravel, empat modul, satu MySQL bersama, pemanggilan fungsi internal.
- Event-Driven Microservices tanpa Proteksi Konsistensi Data: empat layanan NestJS, MySQL per layanan, RabbitMQ, tanpa lima mekanisme.
- Event-Driven Microservices dengan Proteksi Konsistensi Data: susunan identik dengan kondisi kedua, ditambah lima mekanisme.
- Perbandingan dua kondisi EDA mengisolasi dampak paket proteksi. Perbandingan Monolith vs EDA **bukan eksperimen satu variabel** (framework, jumlah basis data, dan komunikasi ikut berbeda); bacalah sebagai perbandingan arsitektur utuh.

**Empat layanan/domain**: Penjualan, Persediaan, Pembayaran, Pelaporan. Aturan otoritas data: data hanya diubah oleh layanan pemiliknya. Pelaporan tidak punya data otoritatif (hanya salinan/read model).

**Lima mekanisme proteksi**: Transactional Outbox; Durable Inbox dan Idempotency; Optimistic Concurrency Control (OCC); Saga dan Kompensasi; Broker, Retry, dan Dead-Letter Queue. Outbox dan OCC adalah fokus utama, sisanya mekanisme pendukung. Pengujian menilai paket secara keseluruhan, bukan kontribusi tiap mekanisme.

**Empat invariant bisnis**: (1) Available = On-Hand dikurangi Reserved; (2) Available tidak boleh di bawah 0; (3) saldo akhir = awal + masuk dikurangi terjual; (4) status final tidak boleh kembali aktif.

**Konsistensi data bukan Consistency pada ACID.** Konsistensi data di sini berarti kondisi akhir data benar setelah dipertukarkan lintas layanan; Consistency ACID hanya berlaku dalam satu transaksi basis data. Selisih sementara antarlayanan wajar; yang dinilai adalah kondisi akhir setelah recovery window.

**Empat skenario**: Penjualan Bersamaan, Mutasi Stok, Pembayaran Digital, QRIS Statis.

**Kode gangguan**: F1 producer berhenti sebelum event terbit; F2 event/notifikasi terkirim ganda; F3 consumer berhenti sebelum ACK; F4a jalur pesan ditunda; F4b notifikasi pembayaran terlambat atau tidak berurutan; F5 dua transaksi berebut stok; F6 pembayaran gagal setelah stok direservasi. F1 sampai F4a hanya berlaku pada kedua kondisi EDA. Tiga kondisi dibandingkan hanya pada skenario yang berlaku untuk ketiganya.

**Kriteria penerimaan (non-kompensatori, ditetapkan sebelum eksperimen)**: oversell, lost update, duplicate effect, permanent mismatch, untraceable event masing-masing = 0; terminal-state coverage dan compensation success = 100% pada penyebut yang berlaku; read-model lag tidak melebihi 60 detik. Performa tidak boleh menutupi pelanggaran integritas.

**Desain eksperimen**: beban 10, 50, 100 req/s; 30 replikasi per kombinasi; 37 kombinasi (15 + 10 dengan gangguan, 12 tanpa gangguan) x 3 tingkat beban x 30 replikasi = **3.330 run**; satu run = reset data, warm-up 60 dtk, beban 60 dtk dengan gangguan, recovery 60 dtk (bila ada gangguan), rekonsiliasi. Lingkungan: Laravel, NestJS, MySQL InnoDB, RabbitMQ, Docker Compose, satu host.

**Alur penelitian lima tahap** (alur mandiri, bukan DSRM): analisis kebutuhan dan aturan bisnis; perancangan arsitektur; pengembangan sistem; pengujian dan simulasi gangguan (pilot test, lalu eksperimen utama); analisis hasil.

**Analisis**: deskriptif saja (median, IQR, p95, minimum, maksimum; jumlah/proporsi untuk metrik integritas) dengan test oracle sebagai penentu benar atau salah. **Tidak ada uji signifikansi, ukuran efek, atau uji Friedman/Wilcoxon di proposal ini.**

**Batasan**: data sintetis dan beban simulasi, satu host Docker Compose, hasil berlaku pada parameter uji dan bukan klaim arsitektur terbaik. Di luar lingkup: aspek medis, FEFO, stock opname, resep, recall.

## 3. Terminologi wajib (hasil revisi dosen pembimbing)

| Aturan | Benar | Salah |
|---|---|---|
| Label kondisi | Nama deskriptif penuh | "Kondisi A/B/C", "Artefak A/B/C", "A: ...", "A-B-C" |
| Singkatan di slide | Setelah nama penuh didefinisikan di slide 6, boleh "EDA tanpa Proteksi" dan "EDA dengan Proteksi". Pada slide pertama yang menyebutnya, tulis nama penuh. | Huruf tunggal, singkatan yang belum didefinisikan |
| Kata kunci topik | konsistensi (data, transaksi) | efektivitas, efisiensi sebagai fokus |
| Paket mekanisme | proteksi, "paket proteksi konsistensi data" | perlindungan |
| "terpadu" | hanya untuk "visibilitas terpadu" / "dasbor terpadu" | untuk hal lain (pakai "setara", "seragam", "terkendali") |
| Urutan empat dimensi | konsistensi data, keandalan transaksi, performa, kompleksitas operasional | urutan lain |
| Metodologi | "alur penelitian lima tahap" | menyebut DSRM sebagai metode yang dipakai |
| Statistik | deskriptif (median, IQR, p95) | signifikan, uji hipotesis, ukuran efek |
| Gaya klaim | "diuji", "dibandingkan", "diamati" | "membuktikan", "unggul", "terbaik", "pasti lebih baik" |
| Gaya sitasi | Penulis (Tahun) + kata kerja + klaim, nama penulis di awal kalimat | sitasi menyelip di tengah kalimat |
| Richardson (2018) | "mendokumentasikan secara sistematis" pola Transactional Outbox | "memperkenalkan" |
| Tanda baca | koma, titik, titik dua, tanda kurung | em dash (tanda pisah panjang) di seluruh output, termasuk catatan pembicara |

**Prinsip urutan:** definisi mendahului rujukan. Kode F1 sampai F6, istilah metrik, dan ambang kriteria harus dijelaskan di slide atau baris sebelum slide yang memakainya dalam tabel atau matriks. Bila terpaksa memakai kode sebelum definisi, tulis arti singkatnya di tempat yang sama.

**Hindari kalimat meta** yang menceritakan proses penulisan ("pada slide ini akan dijelaskan...", "seperti telah direvisi..."). Tulis klaimnya langsung.

## 4. Struktur narasi default untuk sempro

Total isi 14 slide + 2 cadangan, sudah dipakai di PPT eksisting. Pertahankan urutan ini kecuali pengguna meminta lain. Jumlah slide yang diminta lebih sedikit: gabungkan, jangan membuang slide 1, 5, 6, 11, 14.

| No | Slide (judul berupa klaim, bukan topik) | Isi pokok | Sumber |
|---|---|---|---|
| 1 | Cover | Identitas tetap (bagian 1 file ini) | docx |
| 2 | Pencatatan terpisah: rekonsiliasi lambat dan selisih stok berulang | 4 angka lapangan, kondisi eksisting, risiko bila sinkronisasi tidak baik, pertanyaan penelitian | Bab I 1.1 |
| 3 | Lima masalah; perebutan stok diutamakan sebagai skenario uji | 5 masalah + ilustrasi dua kasir berebut stok 1 unit (oversell, lost update) | Bab I 1.2 |
| 4 | Studi terdahulu menjadi landasan; pengujian langsungnya masih terbuka | 4 kelompok literatur + ruang penelitian | Bab II 2.2, Tabel 2.1 |
| 5 | Empat rumusan masalah dijawab oleh empat tujuan yang sejajar | RM1 sampai RM4 + jawaban singkat per baris | Bab I 1.4 dan 1.5 |
| 6 | Tiga kondisi arsitektur dibandingkan dengan fungsi bisnis yang sama | 3 kartu arsitektur + pesan "yang berbeda hanya paket proteksi" | Bab III 3.1 |
| 7 | Konsistensi dinilai dari kondisi akhir data, bukan dari selisih sementara | 2 aspek, 4 invariant, siklus status transaksi, beda dari ACID | Bab II 2.1.2 |
| 8 | Satu data, satu pemilik: empat domain dengan otoritas data yang jelas | 4 layanan, data otoritatif, RabbitMQ, aturan otoritas | Bab III tabel batas domain dan otoritas data |
| 9 | Lima mekanisme proteksi, masing-masing menargetkan satu risiko | 5 mekanisme, risiko yang dicegah, kode F terkait | Bab II 2.1.3 |
| 10 | Alur penelitian lima tahap; pilot test mendahului eksperimen utama | 5 tahap, pilot test, kriteria lulus, lingkungan | Bab III 3.2 dan 3.3.1 |
| 11 | Kriteria integritas bersifat non-kompensatori; performa tidak menutupinya | 8 ambang metrik + dimensi pendukung | Bab III Tabel kriteria |
| 12 | Enam kode gangguan; F1-F4a hanya berlaku pada kedua EDA | 4 skenario + tabel F1 sampai F6 | Bab III Tabel gangguan |
| 13 | 3.330 run: 37 kombinasi x 3 tingkat beban x 30 replikasi | rumus perhitungan + isi satu run | Bab III 3.3.2 |
| 14 | Hasil berlaku pada parameter uji, bukan klaim arsitektur terbaik | batasan, luaran, terima kasih | Bab I 1.3, Bab III |
| 15 | Cadangan: parameter eksperimen dan peran tiap angka | tabel parameter | Bab III 3.3 |
| 16 | Cadangan: definisi operasional yang dipertegas | tabel definisi | Bab III tabel variabel |

Untuk presentasi non-sempro, pakai pola umum: cover, konteks, masalah, solusi/rancangan, metode, hasil atau rencana, penutup.

## 5. Catatan pembicara (wajib untuk deck sempro)

Isi field `notes:` pada setiap slide dengan format berikut (sama dengan PPT eksisting):

```
NASKAH LISAN
<2 sampai 6 kalimat bahasa lisan formal, orang pertama "saya", untuk dibaca saat presentasi>

CATATAN PERTAHANAN
- <antisipasi pertanyaan penguji, satu butir satu pertanyaan atau satu batas klaim>
- <rujukan Bab/Tabel di docx bila relevan>
```

- Naskah lisan tidak mengulang seluruh isi slide; ia menjelaskan alasan dan hubungan antarbagian.
- Catatan pertahanan memuat batas klaim yang jujur (misalnya "Monolith vs EDA bukan eksperimen satu variabel", "30 replikasi adalah keputusan praktis, tanpa klaim signifikansi").
- Slide cadangan cukup satu kalimat naskah lisan, sisanya catatan pertahanan.

## 6. Gaya bahasa dan kepadatan

- Bahasa Indonesia baku, nada akademis. Istilah teknis tetap bahasa Inggris dan dicetak miring bila muncul di paragraf (di slide tidak perlu miring).
- Judul slide berupa kalimat klaim lengkap, maksimum sekitar 75 karakter (dua baris pada 30 pt).
- Teks kartu dan butir pendek: maksimum sekitar 12 kata per butir. `desc` maksimum sekitar 90 karakter.
- Satu slide satu pesan utama. Pesan utama boleh diulang pada kotak penutup di bagian bawah slide.
- Dilarang membuat grafik, angka KPI, atau persentase hasil yang tidak ada di docx. Proposal ini belum punya data hasil eksperimen, jadi `chart` hanya boleh dipakai untuk visualisasi rancangan (misalnya rincian 3.330 run) dengan angka yang berasal dari docx.
- Kode gangguan, metrik, dan istilah teknis ditulis persis seperti di docx (misalnya `read-model lag`, `terminal-state coverage`).

## 7. Prosedur kerja `/generate` untuk deck ini

1. Baca file ini dan `design-instructions.md`.
2. Tulis brief ke `briefs/<slug>.yaml` dengan `theme: unesa-sempro` dan tanpa `theme_override` kecuali diminta.
3. Cover memakai `image: assets/logos/unesa.png`.
4. Pilih `type` slide berdasarkan tabel pemetaan di `design-instructions.md` bagian 4.
5. Jalankan build. Perbaiki semua WARN.
6. Jalankan pemeriksaan istilah terlarang (PowerShell, dari root repo):

```powershell
Select-String -Path briefs\<slug>.yaml -Pattern 'efektivitas','perlindungan','\u2014','DSRM','Friedman','Wilcoxon','signifikan','Artefak [ABC]','[Kk]ondisi [ABC]\b','\b[ABC]:' 
```

   Hasil harus kosong. Satu-satunya pengecualian: kata `DSRM` atau `signifikan` boleh muncul pada catatan pertahanan **hanya** dalam kalimat penyangkalan (contoh: "tidak memakai DSRM", "tanpa klaim signifikansi").
7. Laporkan singkat: path `.pptx`, `.pdf`, folder preview, daftar asumsi, dan selisih angka antara PPT eksisting dan docx bila ada.
