"""Satu-satunya command PPT Sandbox.

    .\\ppt.cmd --brief briefs\\saya.yaml [--nama deck-saya] [--tema dark-premium] [--no-pdf]
    .\\ppt.cmd --judul "Deck Saya" [--tema minimal-light] [--nama deck-saya]
    .\\ppt.cmd --list-tema

Tanpa subcommand: --brief = produksi dari brief; --judul = bikin starter lalu
langsung produksi; --list-tema = lihat tema. Semua dalam sekali jalan:
.pptx full-editable + preview PNG/HTML + PDF.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pptx_factory.builder import build_from_dict  # noqa: E402
from pptx_factory.preview import render_thumbs, try_export_pdf  # noqa: E402
from pptx_factory.theme_engine import THEMES_DIR, load_theme  # noqa: E402


def slug(s: str) -> str:
    s = (s or "").lower().strip().replace(" ", "-")
    s = re.sub(r"[^a-z0-9\-_]+", "", s)
    return s or "deck"


STARTER = """title: "{judul}"
theme: {tema}
theme_override:
  footer:
    show_number: true
    text: ""
slides:
  - type: cover
    kicker: "Presentasi"
    title: "{judul}"
    subtitle: "Tulis subjudul di sini"
    author: "Nama Anda"
    date: "Oktober 2026"

  - type: bullets
    kicker: "Poin"
    title: "Poin utama"
    items:
      - {{title: "Poin 1", desc: "Penjelasan singkat."}}
      - {{title: "Poin 2", desc: "Penjelasan singkat."}}
      - {{title: "Poin 3", desc: "Penjelasan singkat."}}

  - type: chart
    kicker: "Data"
    title: "Grafik (klik di PowerPoint untuk ubah data)"
    chart:
      kind: column
      categories: ["A", "B", "C"]
      series:
        - {{name: "Seri 1", values: [10, 20, 30]}}
    insight: "Tulis insight 1 kalimat di sini."

  - type: closing
    kicker: "Terima kasih"
    title: "Terima Kasih"
    subtitle: "kontak@contoh.id"
    cta: "Hubungi Kami"
"""


def list_tema() -> int:
    files = sorted(THEMES_DIR.glob("*.json"))
    if not files:
        print("Belum ada tema.")
        return 1
    print("Tema tersedia:")
    for f in files:
        try:
            t = load_theme(f.stem)
            print(f"  - {f.stem}: bg={t['colors']['bg']} accent={t['colors']['accent']} "
                  f"font={t['fonts']['head']}")
        except Exception as e:
            print(f"  - {f.stem}: (rusak: {e})")
    return 0


def produksi(brief_path: Path, nama: str, tema_override: str, no_pdf: bool) -> int:
    if not brief_path.exists():
        print(f"BATAL: brief tidak ditemukan: {brief_path}")
        return 1
    with open(brief_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if tema_override:
        data["theme"] = tema_override
    nama = nama or slug(data.get("title") or brief_path.stem)
    out_pptx = ROOT / "output" / f"{nama}.pptx"
    preview_dir = ROOT / "output" / f"preview-{nama}"

    res = build_from_dict(data, str(out_pptx), workdir=str(ROOT))
    print(f"OK: {out_pptx.relative_to(ROOT)} ({res['slides']} slide, tema {res['theme']})")
    for w in res.get("warnings", []):
        print(f"WARN: {w}")

    theme = load_theme(data.get("theme", "corporate-blue"), data.get("theme_override"))
    thumbs = render_thumbs(data, theme, str(preview_dir))
    print(f"OK: {len(thumbs)} PNG + index.html di {preview_dir.relative_to(ROOT)}")

    if not no_pdf:
        pdf = try_export_pdf(str(out_pptx), str(ROOT / "output"))
        print(f"OK: PDF {Path(pdf).relative_to(ROOT)}" if pdf else "SKIP PDF: soffice tidak ditemukan.")

    # QA pixel-true via PowerPoint (gerbang mutu: gagal QA = jangan serahkan)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("qa", str(ROOT / "tools" / "qa.py"))
        assert spec is not None and spec.loader is not None
        qa = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qa)
        qa_dir = ROOT / "output" / f"qa-{nama}"
        paths = qa.export_pngs(str(out_pptx), str(qa_dir))
        print(f"OK: QA {len(paths)} PNG pixel-true di {qa_dir.relative_to(ROOT)} (WAJIB dibaca sebelum serah)")
    except Exception as e:
        print(f"SKIP QA PNG: {e}")
    print(f"Selesai. Buka {out_pptx.relative_to(ROOT)} di PowerPoint untuk edit final.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="ppt", description="Satu command produksi PPT: .pptx + preview + PDF.")
    ap.add_argument("--brief", default="", help="Path brief YAML (produksi dari brief).")
    ap.add_argument("--judul", default="", help="Judul deck (bikin starter lalu langsung produksi).")
    ap.add_argument("--nama", default="", help="Nama output (default dari judul).")
    ap.add_argument("--tema", default="", help="Tema dasar (untuk --judul) atau timpa tema brief.")
    ap.add_argument("--no-pdf", action="store_true", help="Lewati export PDF.")
    ap.add_argument("--force", action="store_true", help="Timpa brief starter bila sudah ada.")
    ap.add_argument("--list-tema", action="store_true", help="Lihat tema yang tersedia.")
    args = ap.parse_args()

    if args.list_tema:
        return list_tema()

    if args.brief:
        bp = Path(args.brief)
        if not bp.is_absolute():
            bp = ROOT / bp
        return produksi(bp, args.nama, args.tema, args.no_pdf)

    if args.judul:
        nama = args.nama or slug(args.judul)
        bp = ROOT / "briefs" / f"{nama}.yaml"
        if bp.exists() and not args.force:
            print(f"BATAL: {bp.relative_to(ROOT)} sudah ada. Pakai --force untuk timpa, "
                  f"atau --nama lain.")
            return 1
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(STARTER.format(judul=args.judul, tema=args.tema or "corporate-blue"),
                      encoding="utf-8")
        print(f"OK: brief starter -> {bp.relative_to(ROOT)} (edit dulu bila perlu)")
        return produksi(bp, nama, "", args.no_pdf)

    ap.print_help()
    print('\nContoh: .\\ppt.cmd --brief briefs\\example.yaml')
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
