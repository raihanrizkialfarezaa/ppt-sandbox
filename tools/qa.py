"""QA visual pixel-true: export tiap slide .pptx menjadi PNG memakai PowerPoint asli.

Ini gerbang mutu permanen: setiap deck yang diserahkan HARUS lolos inspeksi
visual PNG ini (tidak ada teks terpotong, tumpang tindih, kontras rendah,
tabel gepeng) sebelum dilaporkan ke pengguna.

    python tools\\qa.py --pptx output\\sempro-16.pptx --out output\\qa-sempro-16

Butuh PowerPoint terinstal (Windows). Tanpa itu, pakai PDF + preview HTML.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def export_pngs(pptx: str, out_dir: str, width: int = 1920) -> list[str]:
    try:
        import win32com.client  # noqa: F401
    except ImportError:
        print("BATAL: pywin32 belum terinstal (pip install pywin32).")
        return []
    import win32com.client

    pptx_p = Path(pptx).resolve()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    # bersihkan hasil lama
    for f in out.glob("slide-*.png"):
        f.unlink()

    app = win32com.client.Dispatch("PowerPoint.Application")
    try:
        pres = app.Presentations.Open(str(pptx_p), False, False, False)
        try:
            height = int(width * pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth)
            paths = []
            for i, slide in enumerate(pres.Slides, 1):
                p = (out / f"slide-{i:02d}.png").resolve()
                slide.Export(str(p), "PNG", width, height)
                paths.append(str(p))
            return paths
        finally:
            pres.Close()
    finally:
        app.Quit()


def main() -> int:
    ap = argparse.ArgumentParser(description="QA visual: export PNG per slide via PowerPoint")
    ap.add_argument("--pptx", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1920)
    args = ap.parse_args()
    paths = export_pngs(args.pptx, args.out, args.width)
    if not paths:
        return 1
    print(f"OK: {len(paths)} PNG pixel-true di {args.out}")
    for p in paths:
        print(f"  {Path(p).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
