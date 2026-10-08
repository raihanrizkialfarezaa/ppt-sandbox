"""Asset pipeline — Pillow: resize/crop aman + placeholder bila gambar absen."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def ensure_image(src: str | None, dest: str, max_w: int = 1600, bg="#10294A", label: str = "IMAGE") -> str:
    """Pastikan ada file gambar valid di `dest`. Jika src hilang, buat placeholder."""
    dest_p = Path(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    if src and Path(src).exists():
        try:
            im = Image.open(src).convert("RGB")
            im.thumbnail((max_w, max_w))
            im.save(dest_p, "PNG")
            return str(dest_p)
        except Exception:
            pass
    # placeholder 16:9
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 64)
    except Exception:
        font = ImageFont.load_default()
    t = label[:28]
    bb = d.textbbox((0, 0), t, font=font)
    d.text(((w - (bb[2] - bb[0])) / 2, (h - (bb[3] - bb[1])) / 2), t, fill="white", font=font)
    img.save(dest_p, "PNG")
    return str(dest_p)


def key_out_black(src: str, dest: str, thresh: int = 40) -> str:
    """Membuat piksel nyaris-hitam menjadi transparan (untuk logo emas di atas hitam).

    Mengembalikan path PNG RGBA. Bila gagal, kembalikan src apa adanya.
    """
    from pathlib import Path as _P

    dest_p = _P(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    try:
        im = Image.open(src).convert("RGBA")
        px = im.load()
        assert px is not None
        w, h = im.size
        for yy in range(h):
            for xx in range(w):
                r, g, b, a = px[xx, yy]
                if max(r, g, b) < thresh:
                    px[xx, yy] = (r, g, b, 0)
        im.save(dest_p, "PNG")
        return str(dest_p)
    except Exception:
        return src


def fit_for_slide(src: str, dest: str, box_w: int = 1200, box_h: int = 700) -> str:
    dest_p = Path(dest)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.thumbnail((box_w, box_h))
    canvas = Image.new("RGB", (box_w, box_h), (16, 24, 40))
    x = (box_w - im.width) // 2
    y = (box_h - im.height) // 2
    canvas.paste(im, (x, y))
    canvas.save(dest_p, "PNG")
    return str(dest_p)
