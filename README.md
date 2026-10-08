# PPT Sandbox — bikin .pptx full-editable

Tulis brief YAML (atau suruh `/generate`), dapat `.pptx` native yang
**semua teks/tabel/chart-nya bisa diedit di PowerPoint**, plus preview PNG+HTML
dan PDF. Semua dependensi sudah terinstal (Python 3.12, `python-pptx`, LibreOffice).

## Cara utama: `/generate`

Di dalam sesi opencode, cukup ketik (argumen opsional, boleh kosong):

```
/generate
/generate pitch deck kopi, dark premium, 8 slide
/generate slide 5: ganti tabel RM jadi dua kolom; rasio 16:9 tetap
```

`/generate` membaca `template/instructions.md` + `template/design-instructions.md`
(konteks default: sempro TA), meniru gaya `.pptx` di `references/` bila ada,
lalu menulis brief, build, dan memperbaiki WARN hingga bersih. Revisi tinggal
dicopas ke `/generate` lagi. Definisi command: `.opencode/command/generate.md`.

## Cara manual: `.\ppt.cmd`

```powershell
cd "B:\app\ppt sandbox"

# Produksi dari brief (nama output otomatis dari judul)
.\ppt.cmd --brief briefs\example.yaml

# Produksi + ganti nama + timpa tema
.\ppt.cmd --brief briefs\example.yaml --nama deck-saya --tema dark-premium

# Dari nol: bikin starter lalu langsung produksi
.\ppt.cmd --judul "Deck Saya" --tema minimal-light

# Lihat tema
.\ppt.cmd --list-tema
```

Hasil selalu tiga: `output\<nama>.pptx` (full-editable) +
`output\preview-<nama>\` (PNG + `index.html`) + `output\<nama>.pdf`.
Tambahkan `--no-pdf` untuk lewati PDF.

## Cara granular (opsional)

```powershell
# Build saja
python tools\build.py --brief briefs\example.yaml --out output\contoh.pptx --workdir .

# Preview saja (PNG+HTML selalu, PDF via LibreOffice yang sudah terinstal)
python tools\preview.py --brief briefs\example.yaml --pptx output\contoh.pptx --out output\preview-contoh

# Intip gaya file rujukan
python tools\ref.py --file references\Sempro_Raihan_Rizki_Alfareza_v23.pptx
```

## Tema

| Tema | Gaya | Kapan dipakai |
|---|---|---|
| `unesa-sempro` | Hibrida navy/putih, Cambria+Calibri, footer UNESA | Default deck sempro; **jangan** `theme_override` kecuali diminta |
| `corporate-blue` | Navy penuh, aksen biru | Pitch deck / korporat umum |
| `minimal-light` | Putih bersih, aksen biru | Dokumen ringan, cetak |
| `dark-premium` | Hitam pekat, aksen emas | Presentasi premium |

`theme_override:` di brief menimpa warna/font per-request (tema lain).

## Menulis brief

* `theme:` + tiap slide `type:` salah satu dari `cover, agenda, section, bullets, two-col, stats, chart, table, timeline, image-text, quote, closing`.
* Chart default = **native editable** (`kind: column|bar|line|pie|doughnut|area`). `backend: mpl` hanya untuk grafik kompleks (jadi PNG + wajib `insight`).
* Tabel mendukung `col_widths: [...]` (inci per kolom).
* Gambar via `image: assets/...`. Bila file hilang: placeholder + WARN (build tidak gagal).
* `notes:` per slide menjadi catatan pembicara di PowerPoint.
* Deck sempro: ikuti `template/instructions.md` (fakta terkunci, terminologi, `notes` NASKAH LISAN + CATATAN PERTAHANAN) dan cek istilah terlarang sebelum serah (prosedur di sana bagian 7).
* Contoh: `briefs/example.yaml` (umum), `briefs/sempro-16.yaml` (sempro 16 slide).

## Fitur builder

* `content_light: true` = slide konten terang, slide besar (cover/section/stats/timeline/quote/closing) tetap gelap.
* `title_bar: false` = tanpa bilah aksen di bawah judul.
* Footer: teks kiri + nomor (`number_format: plain` = angka saja, `fraction` = n/total), warna menyesuaikan gelap/terang slide.
* Tabel: header warna `primary`, baris selang putih + warna `card`, teks via warna `body`.

## Struktur

```
.opencode/command/generate.md  definisi /generate
pptx_factory/  builder, theme_engine, layouts (12), charts_native, charts_mpl, assets, validate, preview
pptx_factory/themes/  unesa-sempro, corporate-blue, minimal-light, dark-premium
tools/         ppt.py (command utama, sudah termasuk QA PNG), build.py, preview.py (granular), ref.py (baca gaya rujukan), qa.py (export PNG pixel-true via PowerPoint)
ppt.cmd / ppt.ps1  wrapper sekali jalan
briefs/        example.yaml (umum), sempro-16.yaml (sempro)
template/      instructions.md, design-instructions.md (konteks default /generate)
references/    *.pptx rujukan (saat ini: v23 sempro)
assets/        fonts, icons, images, logos (saat ini: unesa.png)
output/        <nama>.pptx, <nama>.pdf, preview-<nama>/ (PNG + index.html), .cache/
```

## Catatan Windows

* Ukuran slide 13.33x7.5 (16:9). Font Calibri/Cambria bawaan Windows.
* PDF via LibreOffice headless (sudah terinstal + terdeteksi otomatis).
