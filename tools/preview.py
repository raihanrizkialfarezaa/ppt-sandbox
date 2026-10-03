"""CLI: preview PNG+HTML dan coba export PDF."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pptx_factory.preview import render_thumbs, try_export_pdf
from pptx_factory.theme_engine import load_theme


def main():
    ap = argparse.ArgumentParser(description="Preview deck: PNG+HTML, opsional PDF")
    ap.add_argument("--brief", required=True)
    ap.add_argument("--pptx", required=True)
    ap.add_argument("--out", default="output/preview")
    args = ap.parse_args()

    with open(args.brief, encoding="utf-8") as f:
        brief = yaml.safe_load(f)
    theme = load_theme(brief.get("theme", "corporate-blue"), brief.get("theme_override"))
    thumbs = render_thumbs(brief, theme, args.out)
    print(f"OK: {len(thumbs)} thumbnails + index.html di {args.out}")
    pdf = try_export_pdf(args.pptx, str(Path(args.out).parent))
    if pdf:
        print(f"OK: PDF {pdf}")
    else:
        print("SKIP PDF: soffice tidak ditemukan — install LibreOffice untuk export PDF.")


if __name__ == "__main__":
    main()
