"""CLI: build .pptx dari brief YAML."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pptx_factory.builder import build_from_brief


def main():
    ap = argparse.ArgumentParser(description="Build PPTX full-editable dari brief YAML")
    ap.add_argument("--brief", required=True, help="path brief YAML")
    ap.add_argument("--out", required=True, help="path output .pptx")
    ap.add_argument("--workdir", default=".", help="working dir untuk resolve gambar")
    args = ap.parse_args()

    res = build_from_brief(args.brief, args.out, workdir=args.workdir)
    print(f"OK: {res['pptx']} ({res['slides']} slide, tema {res['theme']})")
    for w in res.get("warnings", []):
        print(f"WARN: {w}")


if __name__ == "__main__":
    main()
