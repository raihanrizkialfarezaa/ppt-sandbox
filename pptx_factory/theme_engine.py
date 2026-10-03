"""Theme engine — fully dynamic, tidak ada template statis.

Semua visual berasal dari dict theme yang di-merge:
  base theme JSON + theme_override dari brief.
Sehingga setiap request bisa punya gaya berbeda tanpa file .potx.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from pptx.dml.color import RGBColor

THEMES_DIR = Path(__file__).parent / "themes"

DEFAULTS = {
    "name": "custom",
    "slide_w_in": 13.33,
    "slide_h_in": 7.5,
    "margin_in": 0.7,
    "colors": {
        "bg": "#0B1E33",
        "bg2": "#10294A",
        "surface": "#FFFFFF",
        "surface_dark": "#14283F",
        "primary": "#0B2C4A",
        "accent": "#2E9BFF",
        "accent2": "#FFB020",
        "text": "#FFFFFF",
        "text_dark": "#1A2B3C",
        "muted": "#8FA3B8",
        "line": "#24405E",
        "success": "#22C55E",
    },
    "fonts": {
        "head": "Calibri",
        "body": "Calibri Light",
        "fallback": "Arial",
    },
    "sizes": {
        "title": 40,
        "subtitle": 20,
        "h1": 32,
        "h2": 24,
        "body": 16,
        "small": 12,
        "kpi_value": 44,
        "kpi_label": 14,
    },
    "bg_style": "solid",  # solid | gradient | image-dim
    "content_light": False,  # True = slide konten terang, slide besar tetap navy
    "title_bar": True,  # False = tanpa bilah aksen di bawah judul
    "radius_in": 0.12,
    "footer": {"show_number": True, "number_format": "fraction", "text": "Confidential"},
    "chart_style": 2,
}


def hex_to_rgb(h: str) -> RGBColor:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def load_theme(name_or_path: str = "corporate-blue", override: dict | None = None) -> dict:
    """Load base theme lalu deep-merge dengan override dari brief."""
    theme = deepcopy(DEFAULTS)
    base_path = THEMES_DIR / f"{name_or_path}.json"
    if base_path.exists():
        with open(base_path, encoding="utf-8") as f:
            base = json.load(f)
        theme = _merge(theme, base)
    elif Path(str(name_or_path)).exists():
        with open(str(name_or_path), encoding="utf-8") as f:
            base = json.load(f)
        theme = _merge(theme, base)
    # name_or_path bisa juga berupa dict-key yang tidak ada -> pakai defaults
    if override:
        theme = _merge(theme, override)
    theme["name"] = override.get("name", theme.get("name", name_or_path)) if override else theme.get("name", name_or_path)
    return theme


def _merge(base: dict, extra: dict) -> dict:
    out = deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out
