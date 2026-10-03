# PPT Sandbox — bikin .pptx full-editable dari brief

Kemampuan ala Claude/GPT workspace: tulis brief YAML, dapat `.pptx` native yang
**semua teks/tabel/chart-nya bisa diedit di PowerPoint**, plus preview PNG+HTML
dan PDF (bila LibreOffice terinstal).

## Satu-satunya command

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

Satu command, tanpa subcommand. Hasil selalu tiga:
`output\<nama>.pptx` (full-editable) + `output\preview-<nama>\` (PNG + `index.html`)
+ `output\<nama>.pdf`. Tambahkan `--no-pdf` untuk lewati PDF.

## Cara granular (opsional)

```powershell
# 1. install
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. build contoh
python tools\build.py --brief briefs\example.yaml --out output\contoh.pptx --workdir .

# 3. preview (PNG+HTML selalu, PDF bila ada soffice)
python tools\preview.py --brief briefs\example.yaml --pptx output\contoh.pptx --out output\preview
```

Buka `output\preview\index.html` untuk QA cepat, buka `.pptx` di PowerPoint untuk hasil final.

## Menulis brief baru

* `theme:` nama base (`corporate-blue`, `minimal-light`, `dark-premium`) + `theme_override:` untuk warna/font dinamis per-request.
* Tiap slide: `type:` salah satu dari `cover, agenda, section, bullets, two-col, stats, chart, table, timeline, image-text, quote, closing`.
* Chart default = **native editable** (`kind: column|bar|line|pie|doughnut|area`). Tambahkan `backend: mpl` hanya untuk grafik kompleks (otomatis jadi PNG + wajib sertakan insight).
* Gambar: isi `image: assets/images/foto.png`. Bila file hilang, otomatis placeholder (tidak gagal build).
* Lihat `briefs/example.yaml` sebagai kontrak lengkap.

## Struktur

```
pptx_factory/  builder, theme_engine, layouts (12), charts_native, charts_mpl, assets, validate, preview
tools/         ppt.py (command utama), build.py, preview.py (granular)
ppt.cmd / ppt.ps1  wrapper sekali jalan
briefs/        *.yaml (kontrak deck)
template/      instructions.md, design-instructions.md (konteks bebas untuk /generate)
references/    *.pptx rujukan + tools/ref.py untuk membaca gayanya
assets/        fonts, icons, images, logos
output/        *.pptx, preview/*.png + index.html, *.pdf (opsional)
```

## Catatan Windows

* Ukuran slide 13.33x7.5 (16:9). Font default Calibri (bawaan Windows).
* PDF butuh LibreOffice: `winget install TheDocumentFoundation.LibreOffice` lalu `soffice` tersedia di PATH.
