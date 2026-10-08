# Design Instructions

Spesifikasi visual untuk `/generate`. Diturunkan langsung dari `Sempro_Raihan_Rizki_Alfareza_v23.pptx` (16 slide) dan dokumen proposal yang sudah disetujui dosen. Aturan isi dan terminologi ada di `instructions.md`.

## 1. Tema bawaan

- **Tema default: `unesa-sempro`** (`pptx_factory/themes/unesa-sempro.json`). Pakai `theme: unesa-sempro` pada brief dan **jangan** menimpa warna atau font lewat `theme_override`, kecuali pengguna meminta eksplisit.
- Tema ini hibrida: **cover, section, stats, timeline, quote, dan closing berlatar navy**, sedangkan **slide konten (agenda, bullets, two-col, chart, table, image-text) berlatar putih**. Perilaku ini diatur oleh kunci `content_light: true` pada tema.
- Canvas 13,33 x 7,5 inci (16:9), margin kiri-kanan 0,6 inci, area isi y 1,6 sampai 6,9 inci.

### Palet

| Peran | Hex | Dipakai untuk |
|---|---|---|
| Navy utama | `#12284C` | latar cover/penutup, judul slide, header tabel, kartu penekanan, lencana angka |
| Emas aksen | `#C9A227` | label kecil huruf kapital di atas navy, bilah aksen, lencana kode (F1, F5), satu penekanan per slide |
| Emas gelap | `#8A6D0B` | teks penekanan di atas latar terang (emas biasa kurang kontras di atas putih) |
| Kartu | `#EEF2F8` | latar kartu dan baris tabel selang-seling pada slide putih |
| Biru sekunder | `#2F5D9E` | status "selesai/hasil akhir" pada diagram status, simpul sekunder |
| Navy tengah | `#2A4373` | kartu gelap di atas navy, simpul basis data pada kartu navy |
| Biru muda | `#CADCFC` | teks sekunder di atas navy (`muted_dark`) |
| Abu kebiruan | `#5B6B8A` | teks sekunder di atas putih (`muted`), sumber, catatan kaki |
| Teks isi | `#1B2640` | teks badan di atas kartu terang |
| Garis/simpul DB | `#D5DEEC` | garis tipis, simpul basis data pada kartu terang |
| Merah / Hijau | `#B3412F` / `#2E7D5B` | hanya untuk status gagal/berhasil pada diagram, tidak untuk dekorasi |

### Tipografi

| Elemen | Font | Ukuran | Gaya |
|---|---|---|---|
| Judul slide | Cambria | 30 pt | tebal, navy, rata kiri, maksimum 2 baris |
| Judul cover | Cambria | 34 pt | tebal, putih |
| Angka besar (KPI, rumus) | Cambria | 36 sampai 40 pt | tebal, navy (emas di atas navy) |
| Judul kartu | Calibri | 17 sampai 20 pt | tebal, navy |
| Teks badan | Calibri | 15 sampai 18 pt | reguler, `#1B2640` |
| Keterangan kartu | Calibri | 13 sampai 15 pt | `#5B6B8A` |
| Label kecil atas navy | Calibri | 13 pt | tebal, huruf kapital, emas |
| Catatan kaki / sumber | Calibri | 12 pt | `#5B6B8A` |
| Footer | Calibri | 12 pt | `#5B6B8A` |

Lantai ukuran: tidak ada teks di bawah **12 pt**. Cambria hanya untuk judul dan angka besar; semua lainnya Calibri.

## 2. Anatomi slide

- **Judul**: kalimat klaim di kiri atas (x 0,6; y 0,35; lebar 12,1; tinggi 1,0). **Tanpa** kicker di atas judul pada slide konten dan **tanpa** garis aksen di bawah judul (`title_bar: false` sudah di tema; biarkan kolom `kicker` kosong pada slide konten).
- **Cover**: latar navy penuh, label emas "SEMINAR PROPOSAL TUGAS AKHIR", judul Cambria putih, nama penulis tebal, baris NIM/prodi dan baris pembimbing berwarna biru muda, logo UNESA di sisi kanan, baris "Universitas Negeri Surabaya | 2026".
- **Footer** (semua slide): kiri "S1 Teknik Informatika  |  Universitas Negeri Surabaya", kanan nomor slide (angka saja, tanpa "/ total"). Pada slide navy warna footer biru muda.
- **Kartu**: isi `#EEF2F8`, tanpa garis tepi, sudut hampir siku (radius kecil). Satu kartu penekanan per baris/slide berwarna navy dengan label emas dan teks putih.
- **Kotak penutup pesan**: batang lebar di dasar slide (y sekitar 5,6 sampai 6,8), isi navy dengan teks putih tebal, atau putih dengan teks navy tebal bila slide sudah padat. Dipakai untuk satu kalimat pesan utama slide.
- **Lencana bernomor**: kotak/lingkaran navy dengan angka putih; lencana yang disorot memakai emas gelap `#8A6D0B`. Hanya satu sorotan per daftar.
- **Lencana kode** (F1, F5, dst.): kotak emas `#C9A227` dengan teks navy tebal; lencana netral memakai `#D5DEEC`.
- **Sumber**: baris kecil di bawah isi, awali dengan "Sumber:" (contoh: "Sumber: wawancara dan observasi dengan pemilik Apotek Bisma, 5 Juli 2026").

## 3. Aturan komposisi

1. Satu slide, satu pesan. Judul klaim memuat pesan itu; kotak penutup mengulanginya hanya bila slide padat.
2. Maksimum **6 item** per daftar atau baris kartu (batas builder). Untuk 5 kartu sejajar pakai `agenda`.
3. Teks badan per slide sekitar 40 kata di luar tabel. Lebih dari itu, pecah slide atau pindahkan ke `notes`.
4. Kontras: putih atau biru muda di atas navy; navy atau `#1B2640` di atas putih/`#EEF2F8`. Emas `#C9A227` tidak dipakai sebagai warna teks di atas putih (pakai `#8A6D0B`).
5. Warna melambangkan peran, bukan dekorasi: navy = struktur, emas = sorotan tunggal, merah/hijau = hanya status gagal/berhasil.
6. Jangan menaruh teks di atas gambar tanpa panel solid. Jangan memakai gradasi, bayangan, atau animasi.
7. Tabel: header navy dengan teks putih tebal, baris selang-seling putih dan `#EEF2F8`, teks 14 pt, maksimum 9 baris dan 5 kolom. Lebih dari itu, jadikan slide cadangan.
8. Angka dan kode ditulis persis seperti di docx (misalnya `3.330`, `F4a`, `≤ 60 dtk`).
9. Tidak ada em dash di teks slide, maupun catatan pembicara.

## 4. Pemetaan pola PPT eksisting ke `type` builder

Builder hanya menyediakan 12 tipe slide. Tabel ini menunjukkan tipe terdekat untuk tiap pola PPT eksisting dan apa yang hilang. Pilih tipe di kolom "Pakai".

| Pola di PPT eksisting | Slide | Pakai | Kecocokan | Yang perlu diketahui |
|---|---|---|---|---|
| Cover navy dengan logo | 1 | `cover` + `image: assets/logos/unesa.png` | Tinggi | Ada bilah emas vertikal dan panel logo di sisi kanan, sedikit berbeda dari PPT asli. |
| Judul + daftar 5 masalah bernomor | 3 | `bullets` (maks 6, `title` + `desc`) | Sedang | Tanpa lencana angka dan tanpa ilustrasi samping. Taruh ilustrasi dua kasir sebagai `image-text` terpisah bila perlu. |
| 4 kartu angka lapangan + dua kartu + pertanyaan penelitian | 2 | `stats` (4 item) | Rendah | `stats` berlatar navy, beda dengan slide 2 asli yang putih. Pakai maksimum sekali per deck. Alternatif: `bullets` dengan angka di `title`. |
| 4 atau 5 kartu kolom | 4, 9 | `agenda` (maks 6 item, `title` + `desc`) | Sedang | Tanpa lencana kode dan tanpa baris "menargetkan risiko". Tulis risiko di `desc`. |
| Baris RM1 sampai RM4 dengan tujuan sejajar | 5 | `table` (kolom: RM, Rumusan masalah, Tujuan; `col_widths: [1.2, 6.2, 4.7]`) | Sedang | Lencana RM navy diganti sel biasa. |
| Tiga kartu arsitektur dengan diagram mini | 6 | `agenda` 3 item (`numbers: false`, nama penuh di `title`, susunan di `desc`) | Tinggi | Tanpa lencana dan tanpa diagram; nama penuh tetap terpenuhi di judul kartu. Bila ada gambar diagram, pakai `image-text` (bagian 5). |
| Dua aspek + empat invariant + siklus status | 7 | `two-col` (kiri aspek, kanan invariant) | Sedang | Siklus status: pakai gambar (Gambar 3.3 docx) pada slide `image-text` terpisah. |
| Empat layanan + RabbitMQ + aturan otoritas | 8 | `agenda` 4 item + kalimat aturan di `subtitle` | Sedang | Tanpa simpul basis data. |
| Lima tahap alur penelitian | 10 | `timeline` (5 item) | Sedang | Berlatar navy. Pilot test dijelaskan di `desc` tahap 4. |
| Delapan ambang metrik | 11 | `table` (kolom: Metrik, Ambang, Arti) | Sedang | 8 baris muat. |
| Empat skenario + tabel F1 sampai F6 | 12 | `table` (kolom: Kode, Gangguan, Skenario, Berlaku, Bukti; `col_widths: [0.8, 3.3, 2.9, 1.25, 3.85]`) | Tinggi | Nama empat skenario ditulis di `subtitle`. |
| Rumus 15 + 10 + 12 = 37, x 3 x 30 = 3.330 | 13 | `stats` (4 item: 37, 3, 30, 3.330) + isi satu run di `subtitle` | Sedang | Tanda operator tidak tergambar, tulis di `label`. |
| Batasan dan Luaran dua kartu + terima kasih | 14 | `two-col` lalu `closing` | Sedang | `closing` berlatar navy tanpa `cta`. |
| Tabel cadangan | 15, 16 | `table` dengan judul diawali "Cadangan:" | Tinggi | `col_widths: [3.3, 3.5, 5.3]` (parameter), `[2.3, 6.6, 3.2]` (definisi). |

Prioritaskan tipe berkecocokan Tinggi atau Sedang. Jangan memakai `quote` dan `section` pada deck sempro kecuali diminta.

## 5. Diagram dan gambar

- Builder tidak menggambar diagram (kotak, panah, silinder). Untuk arsitektur, alur, dan siklus status gunakan **gambar PNG**:
  1. Pertama, pakai gambar yang sudah ada di docx: Gambar 2.1 kerangka berpikir, Gambar 3.1 alur penelitian, Gambar 3.2 perbandingan tiga kondisi arsitektur, Gambar 3.3 status transaksi dan jalur pemulihan. Letakkan di `assets/images/` dan rujuk lewat `image:`.
  2. Bila perlu diagram baru, render dengan palet bagian 1 (navy, emas, biru sekunder, `#EEF2F8`), font Calibri, latar putih atau transparan, dan resolusi minimal 1600 px lebar.
- Gambar selalu didampingi judul klaim dan satu kalimat pesan; jangan hanya gambar.
- Bila file gambar tidak ada, builder membuat placeholder. Anggap itu WARN: laporkan di ringkasan akhir.

## 6. Grafik

Proposal belum memiliki data hasil. Grafik native (`chart`) hanya untuk memvisualkan rancangan dengan angka dari docx (misalnya komposisi 3.330 run). Warna seri: navy `#12284C`, emas `#C9A227`, biru sekunder `#2F5D9E`. Dilarang membuat grafik yang tampak seperti hasil eksperimen.

## 7. Catatan pembicara

Isi `notes:` mengikuti format di `instructions.md` bagian 5. Catatan pembicara tidak tampil di slide dan tidak mempengaruhi desain, tetapi tetap bebas em dash dan bebas kata terlarang.

## 8. Batas builder yang perlu diingat

| Keterbatasan builder saat ini | Cara menyiasati |
|---|---|
| Tidak ada logo kecil di footer (PPT asli punya) | Tambahkan manual di PowerPoint atau lewat pengembangan builder berikutnya |
| Tidak ada lencana angka, lencana kode, panah, simpul diagram | Pakai gambar PNG (bagian 5) |
| Maks 6 item per daftar, 4 stat, 5 timeline | Pecah slide |
| Cover memakai panel kanan dan bilah emas vertikal | Terima sebagai variasi kecil, jangan menimpa layout |
| Slide `stats`, `timeline`, `quote`, `section` selalu navy | Pakai hemat; pola putih PPT asli diwakili `bullets`, `agenda`, `table`, `two-col` |
| `table` mendukung `col_widths` (inci) dan baris selang-seling, tidak ada sel bergabung | Hindari tabel dengan sel gabungan |

## 9. Daftar periksa visual sebelum menyerahkan

- [ ] Tema `unesa-sempro`, tanpa `theme_override` warna atau font.
- [ ] Cover memuat judul penuh, nama, NIM, pembimbing, logo, "Universitas Negeri Surabaya | 2026".
- [ ] Setiap slide konten punya judul klaim, tidak lebih dari 2 baris.
- [ ] Tidak ada teks di bawah 12 pt, tidak ada teks emas di atas putih.
- [ ] Maksimum satu sorotan emas per slide, maksimum satu slide `stats`.
- [ ] Footer dan nomor slide ada di semua slide.
- [ ] Tabel tidak melebihi 9 baris dan 5 kolom.
- [ ] Preview PNG diperiksa: tidak ada teks terpotong, tumpang tindih, atau kontras rendah.
- [ ] Lolos pemeriksaan istilah terlarang di `instructions.md` bagian 7.
