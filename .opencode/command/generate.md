---
description: Generate PPT full-editable dari topik singkat. Contoh: /generate Kopi Nusantara, dark premium, 8 slide
---

Buatkan presentasi dari permintaan berikut: $ARGUMENTS

Sebelum mulai, baca dulu `template/instructions.md` dan
`template/design-instructions.md` (plus file `.md` lain di `template/`
bila ada) dan ikuti isinya.

Bila folder `references/` berisi file `.pptx` (selain README), jadikan acuan:
jalankan `python tools/ref.py --file references/<nama>.pptx` untuk membaca
gayanya, lalu tiru warna/font/strukturnya via `theme_override` dan pemilihan
layout. Bila permintaan menyebut file rujukan tertentu, pakai file itu.

Langkah wajib:
1. Tentukan judul, tema (`corporate-blue` / `minimal-light` / `dark-premium`, atau warna custom via `theme_override`), dan daftar slide (maks 12) sesuai permintaan. Bila permintaan tidak menyebut detail, pilih yang wajar: cover, agenda, 3-6 slide isi (campur `bullets`/`stats`/`chart`/`table`/`timeline` yang paling cocok), `closing`.
2. Tulis brief ke `briefs/<slug-judul>.yaml` mengikuti kontrak `briefs/example.yaml`. Type valid: `cover, agenda, section, bullets, two-col, stats, chart, table, timeline, image-text, quote, closing`. Chart harus native editable (`kind: column|bar|line|pie|doughnut|area`), jangan `backend: mpl` kecuali grafik sangat kompleks.
3. Jalankan `.\ppt.cmd --brief briefs\<slug-judul>.yaml` dari `B:\app\ppt sandbox` (tambah `--tema <nama>` bila permintaan menyebut tema).
4. Bila ada WARN validasi/overflow, perbaiki brief dan build ulang hingga bersih.
5. Laporkan singkat saja: path `.pptx`, `.pdf`, dan folder preview yang dihasilkan.
