"""Validasi ringan — heuristik QA sebelum file diserahkan."""
from __future__ import annotations

from .layouts import agenda_need_h, est_lines


def estimate_overflow(data: dict) -> list[str]:
    """Prediksi luapan sebelum build memakai rumus yang sama dengan layouts."""
    out: list[str] = []
    for i, s in enumerate(data.get("slides", []), 1):
        t = s.get("type", "?")
        if t == "bullets":
            items = s.get("items", [])[:6]
            n = max(len(items), 1)
            if n >= 5:
                y0, bottom, gap, tsize, dsize = 2.5, 6.8, 0.12, 13.5, 11.0
            else:
                y0, bottom, gap, tsize, dsize = 2.55, 6.72, 0.16, 16, 12.5
            ch = (bottom - y0 - (n - 1) * gap) / n
            for j, it in enumerate(items, 1):
                it = it if isinstance(it, dict) else {"title": it}
                need = (0.24 + est_lines(it.get("title", ""), 10.0, tsize) * tsize * 1.3 / 72
                        + est_lines(it.get("desc", ""), 10.0, dsize) * dsize * 1.3 / 72)
                if need > (ch - 0.12) + 0.05:
                    out.append(f"slide {i} butir {j}: berisiko meluap, pendekkan title/desc.")
            if ch < 0.6:
                out.append(f"slide {i}: {n} butir terlalu padat, kurangi butir atau pecah slide.")
        elif t == "agenda":
            items = s.get("items", [])[:6]
            per_row = 3 if len(items) in (3, 6) else 4
            rows = [items[r:r + per_row] for r in range(0, len(items), per_row)]
            total = 0.0
            for row in rows:
                col_w = (11.9 - 0.5 * (len(row) - 1)) / len(row)
                total += max([agenda_need_h(it.get("title", ""), it.get("desc", ""), col_w, 14, 11)
                                for it in row] + [1.7])
            total += 0.35 * (len(rows) - 1)
            if total > 4.3:
                out.append(f"slide {i}: kartu agenda berisiko meluap, pendekkan desc.")
        elif t == "table":
            rows = s.get("rows", [])
            cols = max(len(s.get("headers", [])), max((len(r) for r in rows), default=0))
            if len(rows) > 9 or cols > 5:
                out.append(f"slide {i}: tabel {len(rows)}x{cols} melebihi 9x5, jadikan slide cadangan.")
            bh = 0.55 if len(rows) <= 5 else 0.45
            if 0.55 + len(rows) * bh > 4.2 and (4.2 - 0.55) / max(len(rows), 1) < 0.38:
                out.append(f"slide {i}: baris tabel terlalu pendek, kurangi baris.")
    return out


def validate_brief(data: dict) -> list[str]:
    warnings: list[str] = []
    slides = data.get("slides", [])
    if not slides:
        warnings.append("brief tidak punya slides.")
    for i, s in enumerate(slides, 1):
        t = s.get("type", "?")
        if t not in ("cover", "agenda", "section", "bullets", "facts", "two-col", "stats",
                     "chart", "table", "timeline", "image-text", "quote", "closing"):
            warnings.append(f"slide {i}: type '{t}' tidak dikenal, akan fallback ke bullets.")
        if t == "chart":
            c = s.get("chart", {})
            if not c.get("categories") or not c.get("series"):
                warnings.append(f"slide {i} chart: categories/series kosong.")
        if t == "table":
            if not s.get("headers") or not s.get("rows"):
                warnings.append(f"slide {i} table: headers/rows kosong.")
        # heuristik overflow
        for key in ("title", "body", "subtitle", "quote", "insight"):
            v = s.get(key, "")
            if isinstance(v, str) and len(v) > 400:
                warnings.append(f"slide {i}: '{key}' sangat panjang ({len(v)} char), risiko overflow.")
        items = s.get("items", []) or s.get("bullets", []) or []
        if isinstance(items, list) and len(items) > 6:
            warnings.append(f"slide {i}: {len(items)} items, hanya 6 pertama yang dirender.")
    warnings.extend(estimate_overflow(data))
    return warnings
