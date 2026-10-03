---
description: Buatkan atau revisi PPT. Cukup /generate saja, atau tambah topik dan catatan revisi sesukamu.
---

Permintaan: $ARGUMENTS (boleh kosong, boleh topik singkat, boleh catatan revisi yang dicopas).

Aturan:
- Semua opsional. Jangan bertanya, langsung putuskan yang paling wajar.
- Baca `template/instructions.md` dan `template/design-instructions.md` dulu dan ikuti isinya (itu konteks default).
- Bila permintaan adalah revisi/catatan atas deck yang sudah ada, edit brief YAML deck itu lalu build ulang. Bila topik baru, buat brief baru mengikuti kontrak `briefs/example.yaml` (type: cover, agenda, section, bullets, two-col, stats, chart, table, timeline, image-text, quote, closing; chart native editable).
- Bila ada `.pptx` di `references/`, intip gayanya dengan `python tools/ref.py --file references/<nama>.pptx` lalu tiru via `theme_override`.
- Build dengan `.\ppt.cmd --brief briefs\<slug>.yaml` dari `B:\app\ppt sandbox`. Perbaiki semua WARN, build ulang hingga bersih.
- Laporkan singkat: path `.pptx`, `.pdf`, folder preview.
