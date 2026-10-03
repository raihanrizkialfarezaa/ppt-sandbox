"""Validasi ringan — heuristik QA sebelum file diserahkan."""
from __future__ import annotations


def validate_brief(data: dict) -> list[str]:
    warnings: list[str] = []
    slides = data.get("slides", [])
    if not slides:
        warnings.append("brief tidak punya slides.")
    for i, s in enumerate(slides, 1):
        t = s.get("type", "?")
        if t not in ("cover", "agenda", "section", "bullets", "two-col", "stats",
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
    return warnings
