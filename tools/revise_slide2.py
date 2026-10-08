"""Revise only slide 2 of the v23 deck, preserving its original design/shapes."""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Sempro_Raihan_Rizki_Alfareza_v23.pptx"
OUTPUT = ROOT / "output" / "sempro-16-slide2-final.pptx"


def replace_text(shape, text: str, *, font_size: float | None = None, bold: bool | None = None):
    """Replace paragraph text while retaining original paragraph/run styling."""
    tf = shape.text_frame
    parts = text.split("\n")
    paragraphs = tf.paragraphs
    while len(paragraphs) < len(parts):
        tf.add_paragraph()
        paragraphs = tf.paragraphs
    for i, p in enumerate(paragraphs):
        value = parts[i] if i < len(parts) else ""
        if p.runs:
            p.runs[0].text = value
            for run in p.runs[1:]:
                run.text = ""
            if font_size is not None:
                p.runs[0].font.size = Pt(font_size)
            if bold is not None:
                p.runs[0].font.bold = bold
        elif value:
            p.text = value


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    prs = Presentation(str(SOURCE))
    slide = prs.slides[1]

    # Original v23 shapes are stable; these indexes are the four statistic cards,
    # existing-condition card, risk card, question, and source line.
    replace_text(slide.shapes[11], "Selalu", font_size=26, bold=True)
    replace_text(slide.shapes[12], "ada selisih stok fisik\nvs sistem tiap bulan")
    replace_text(slide.shapes[15], "Kasir mandiri di tiap cabang\nExcel VBA di gudang distribusi\nTanpa sinkronisasi real-time")
    replace_text(
        slide.shapes[19],
        "Dua transaksi kasir pada produk yang sama berisiko saling menimpa stok akhir (lost update).",
        font_size=16,
    )
    # Add a small explicit distinction beneath the unchanged risk statement.
    tf = slide.shapes[19].text_frame
    note = tf.add_paragraph()
    note_run = note.add_run()
    note_run.text = "Risiko integrasi; bukan kejadian pada sistem eksisting."
    note_run.font.name = "Calibri"
    note_run.font.size = Pt(12)
    note_run.font.italic = True
    note_run.font.color.rgb = RGBColor(91, 107, 138)
    note.space_before = Pt(3)

    replace_text(
        slide.shapes[20],
        "Pertanyaan penelitian: ketika catatan antarunit dihubungkan, apakah transaksi tetap konsisten?",
        font_size=18,
        bold=True,
    )
    # Update slide 2 speaker notes only; retain notes for every other slide.
    notes = slide.notes_slide.placeholders[1]
    notes.text = (
        "NASKAH LISAN\n"
        "Berdasarkan konfirmasi Ibu Atik, selisih antara stok fisik dan catatan sistem "
        "selalu muncul pada setiap rekonsiliasi bulanan. Ini adalah temuan lapangan, "
        "bukan klaim sebab-akibat. Lost update dan oversell merupakan risiko bersyarat "
        "bila catatan antarunit dihubungkan.\n\n"
        "CATATAN PERTAHANAN\n"
        "- Sumber: wawancara dan observasi dengan pemilik Apotek Bisma, 5 Juli 2026.\n"
        "- Risiko integrasi, bukan kejadian pada sistem eksisting."
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT))
    print(f"OK: only slide 2 revised from v23 -> {OUTPUT.relative_to(ROOT)}")
    print(f"OK: {len(prs.slides)} slides; slide 2 shapes retained ({len(slide.shapes)} shapes)")


if __name__ == "__main__":
    main()
