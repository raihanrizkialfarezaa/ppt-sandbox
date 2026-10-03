"""Preview dua jalur:
1. PNG thumbnails + index.html — selalu tersedia (render aproksimasi via Pillow).
2. PDF via LibreOffice headless — bila `soffice` terinstal (opsional).
"""
from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int):
    for name in ("arial.ttf", "calibri.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_thumbs(brief: dict, theme: dict, out_dir: str) -> list[str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bg = theme["colors"]["bg"]
    accent = theme["colors"]["accent"]
    fg = theme["colors"]["text"]
    paths = []
    for i, s in enumerate(brief.get("slides", []), 1):
        img = Image.new("RGB", (1280, 720), bg)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 60, 720], fill=accent)
        d.text((100, 60), f"{i:02d} · {(s.get('type') or '').upper()}", font=_font(28), fill=accent)
        d.text((100, 110), str(s.get("title", ""))[:60], font=_font(52), fill=fg)
        sub = str(s.get("subtitle", "") or s.get("body", "") or s.get("insight", "") or "")[:140]
        d.text((100, 200), sub, font=_font(26), fill="#9CA3AF")
        # daftar item ringkas
        y = 300
        for it in (s.get("items") or s.get("bullets") or [])[:5]:
            label = it.get("title", it) if isinstance(it, dict) else str(it)
            d.text((120, y), f"• {str(label)[:70]}", font=_font(26), fill=fg)
            y += 45
        if s.get("chart"):
            c = s["chart"]
            d.text((100, 580), f"[chart:{c.get('kind','column')} cats={len(c.get('categories',[]))} series={len(c.get('series',[]))}]",
                   font=_font(24), fill=accent)
        p = out / f"slide-{i:02d}.png"
        img.save(p, "PNG")
        paths.append(str(p))
    # gallery html
    cards = "\n".join(
        f'<figure><img src="{Path(p).name}"><figcaption>Slide {i}</figcaption></figure>'
        for i, p in enumerate(paths, 1)
    )
    (out / "index.html").write_text(
        f"""<!doctype html><meta charset="utf-8"><title>Preview — {html.escape(brief.get('title','deck'))}</title>
<style>body{{background:#0b1220;color:#e5e7eb;font-family:Arial;margin:24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px}}
figure{{margin:0;background:#111827;border-radius:12px;overflow:hidden}}img{{width:100%;display:block}}
figcaption{{padding:8px 12px;color:#9ca3af}}</style>
<h1>Preview — {html.escape(brief.get('title','deck'))}</h1>
<p>{len(paths)} slide · aproksimasi PNG (bukan pixel-perfect PowerPoint) · buka .pptx untuk hasil final editable.</p>
<div class="grid">{cards}</div>""",
        encoding="utf-8",
    )
    return paths


def _find_soffice() -> str | None:
    found = shutil.which("soffice")
    if found:
        return found
    # Lokasi umum Windows bila belum masuk PATH
    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def try_export_pdf(pptx_path: str, out_dir: str) -> str | None:
    """Coba konversi ke PDF via soffice. Return path PDF atau None bila tak tersedia."""
    soffice = _find_soffice()
    if soffice is None:
        return None
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(pptx_path)],
            capture_output=True, timeout=120, check=False,
        )
        pdf = out / (Path(pptx_path).stem + ".pdf")
        return str(pdf) if pdf.exists() else None
    except Exception:
        return None
