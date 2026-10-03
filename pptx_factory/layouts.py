"""12 layout builder — semuanya native editable shapes/textbox/table/chart.

Semua koordinat dalam inch, canvas default 13.33 x 7.5 (16:9).
Tidak memakai placeholder template: tiap slide mulai dari blank layout.
"""
from __future__ import annotations

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

from .charts_native import build_chart
from .theme_engine import hex_to_rgb


# ---------- primitives ----------

def set_bg(slide, theme, alt: bool = False):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme["colors"]["bg2"] if alt else theme["colors"]["bg"])


def _para(tf, text, size=16, bold=False, color="#FFFFFF", font="Calibri Light", align=None, space_after=Pt(4)):
    p = tf.add_paragraph() if len(tf.paragraphs) > 0 and tf.paragraphs[0].text != "" else tf.paragraphs[0]
    # jika paragraf pertama masih kosong, pakai itu; selain itu tambah baru
    if p.text != "" and text:
        p = tf.add_paragraph()
    p.text = ""
    p.space_after = space_after
    if align is not None:
        p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font
    try:
        run.font.color.rgb = hex_to_rgb(color)
    except Exception:
        pass
    return p


def textbox(slide, left, top, width, height, blocks: list, anchor=MSO_ANCHOR.TOP):
    tx = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tx.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for b in blocks:
        if first:
            # isi paragraf pertama yang auto-terbuat
            p = tf.paragraphs[0]
            p.text = ""
            p.space_after = Pt(4)
            if b.get("align") is not None:
                p.alignment = b["align"]
            run = p.add_run()
            run.text = b.get("text", "")
            run.font.size = Pt(b.get("size", 16))
            run.font.bold = b.get("bold", False)
            run.font.name = b.get("font", "Calibri Light")
            try:
                run.font.color.rgb = hex_to_rgb(b.get("color", "#FFFFFF"))
            except Exception:
                pass
            first = False
        else:
            _para(tf, b.get("text", ""), size=b.get("size", 16), bold=b.get("bold", False),
                  color=b.get("color", "#FFFFFF"), font=b.get("font", "Calibri Light"),
                  align=b.get("align"), space_after=Pt(b.get("space_after_pt", 4)))
    return tx


def solid_rect(slide, left, top, width, height, fill_hex, line_hex=None, radius=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sp = slide.shapes.add_shape(shape_type, Inches(left), Inches(top), Inches(width), Inches(height))
    sp.fill.solid()
    sp.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    if line_hex:
        sp.line.color.rgb = hex_to_rgb(line_hex)
        sp.line.width = Pt(1)
    else:
        sp.line.fill.background()
    return sp


def accent_bar(slide, left, top, width, height, theme):
    return solid_rect(slide, left, top, width, height, theme["colors"]["accent"])


def add_footer(slide, idx: int, total: int, theme, light_on_dark=True):
    cfg = theme.get("footer", {})
    if not cfg.get("show_number", True) and not cfg.get("text"):
        return
    color = theme["colors"]["muted"]
    blocks = []
    if cfg.get("text"):
        blocks.append({"text": cfg["text"], "size": theme["sizes"]["small"], "color": color, "font": theme["fonts"]["body"]})
    if cfg.get("show_number", True):
        blocks.append({"text": f"{idx} / {total}", "size": theme["sizes"]["small"], "color": color,
                       "font": theme["fonts"]["body"], "align": PP_ALIGN.RIGHT})
    if blocks:
        textbox(slide, 0.7, 7.0, 11.9, 0.35, blocks)


def title_block(slide, theme, kicker: str, title: str, subtitle: str = "", dark_text: bool = False):
    tc = theme["colors"]["text_dark"] if dark_text else theme["colors"]["text"]
    mc = theme["colors"]["muted"] if not dark_text else theme["colors"]["muted"]
    blocks = []
    if kicker:
        blocks.append({"text": kicker.upper(), "size": 12, "bold": True, "color": theme["colors"]["accent"],
                       "font": theme["fonts"]["head"]})
    blocks.append({"text": title, "size": theme["sizes"]["h1"], "bold": True, "color": tc,
                   "font": theme["fonts"]["head"]})
    if subtitle:
        blocks.append({"text": subtitle, "size": theme["sizes"]["body"], "color": mc,
                       "font": theme["fonts"]["body"]})
    textbox(slide, 0.7, 0.35, 11.9, 1.6, blocks)
    accent_bar(slide, 0.7, 1.95 if subtitle else 1.7, 1.2, 0.06, theme)


def is_light_theme(theme) -> bool:
    bg = theme["colors"]["bg"].lstrip("#").lower()
    # heuristik sederhana: luminance tinggi -> light
    try:
        r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) > 150
    except Exception:
        return False


# ---------- 12 layouts ----------

def l_cover(slide, theme, d: dict):
    set_bg(slide, theme)
    # aksen kanan sebagai panel visual
    solid_rect(slide, 8.3, 0, 5.03, 7.5, theme["colors"]["bg2"], theme["colors"]["line"])
    accent_bar(slide, 8.3, 0, 0.08, 7.5, theme)
    img = d.get("image")
    if img:
        try:
            slide.shapes.add_picture(img, Inches(8.6), Inches(0.6), Inches(4.4), Inches(4.4))
        except Exception:
            pass
    textbox(slide, 0.9, 1.4, 6.8, 3.5, [
        {"text": (d.get("kicker") or "").upper(), "size": 13, "bold": True,
         "color": theme["colors"]["accent"], "font": theme["fonts"]["head"]},
        {"text": d.get("title", "Judul Presentasi"), "size": theme["sizes"]["title"],
         "bold": True, "color": theme["colors"]["text"], "font": theme["fonts"]["head"]},
        {"text": d.get("subtitle", ""), "size": theme["sizes"]["subtitle"],
         "color": theme["colors"]["muted"], "font": theme["fonts"]["body"]},
    ])
    meta = "  •  ".join([x for x in [d.get("date"), d.get("author")] if x])
    if meta:
        textbox(slide, 0.9, 5.6, 6.8, 0.6, [
            {"text": meta, "size": theme["sizes"]["small"], "color": theme["colors"]["muted"],
             "font": theme["fonts"]["body"]}])
    if img is None:
        # kartu aksen default bila tanpa gambar
        solid_rect(slide, 8.9, 1.0, 3.8, 3.2, theme["colors"]["accent"], radius=True)
        textbox(slide, 9.2, 1.9, 3.2, 1.6, [
            {"text": d.get("cover_stat", "85%"), "size": 54, "bold": True, "color": "#FFFFFF",
             "font": theme["fonts"]["head"], "align": PP_ALIGN.CENTER},
            {"text": d.get("cover_stat_label", "tetap editable"), "size": 13, "color": "#FFFFFF",
             "font": theme["fonts"]["body"], "align": PP_ALIGN.CENTER},
        ])


def l_agenda(slide, theme, d: dict):
    set_bg(slide, theme, alt=is_light_theme(theme))
    dark = is_light_theme(theme)
    title_block(slide, theme, d.get("kicker", "Agenda"), d.get("title", "Apa yang akan dibahas"),
                d.get("subtitle", ""), dark_text=dark)
    items = d.get("items", [])
    n = max(len(items), 1)
    col_w = (11.9 - 0.5 * (min(n, 4) - 1)) / min(n, 4)
    for i, it in enumerate(items[:6]):
        col = i % 4
        row = i // 4
        x = 0.7 + col * (col_w + 0.5)
        y = 2.5 + row * 2.2
        solid_rect(slide, x, y, col_w, 1.9,
                   "#FFFFFF" if not dark else theme["colors"]["surface_dark"],
                   theme["colors"]["line"], radius=True)
        textbox(slide, x + 0.25, y + 0.2, col_w - 0.5, 1.5, [
            {"text": f"{i+1:02d}", "size": 13, "bold": True, "color": theme["colors"]["accent"],
             "font": theme["fonts"]["head"]},
            {"text": it.get("title", f"Poin {i+1}"), "size": 15, "bold": True,
             "color": "#1A2B3C" if not dark else "#FFFFFF", "font": theme["fonts"]["head"]},
            {"text": it.get("desc", ""), "size": 12,
             "color": "#5B6B7C" if not dark else theme["colors"]["muted"],
             "font": theme["fonts"]["body"]},
        ])


def l_section(slide, theme, d: dict):
    set_bg(slide, theme)
    accent_bar(slide, 0, 0, 0.14, 7.5, theme)
    textbox(slide, 1.2, 2.2, 10.9, 3.0, [
        {"text": (d.get("kicker") or "BAGIAN").upper(), "size": 14, "bold": True,
         "color": theme["colors"]["accent"], "font": theme["fonts"]["head"]},
        {"text": d.get("title", "Judul Bagian"), "size": 44, "bold": True,
         "color": theme["colors"]["text"], "font": theme["fonts"]["head"]},
        {"text": d.get("subtitle", ""), "size": 18, "color": theme["colors"]["muted"],
         "font": theme["fonts"]["body"]},
    ])


def l_bullets(slide, theme, d: dict):
    set_bg(slide, theme, alt=is_light_theme(theme))
    dark = is_light_theme(theme)
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Poin Utama"),
                d.get("subtitle", ""), dark_text=dark)
    items = d.get("items", [])
    y = 2.5
    for it in items[:6]:
        if isinstance(it, str):
            it = {"title": it}
        solid_rect(slide, 0.7, y, 0.08, 0.9, theme["colors"]["accent"])
        textbox(slide, 1.0, y - 0.08, 11.6, 1.1, [
            {"text": it.get("title", ""), "size": 17, "bold": True,
             "color": theme["colors"]["text_dark"] if dark else theme["colors"]["text"],
             "font": theme["fonts"]["head"]},
            {"text": it.get("desc", ""), "size": 13,
             "color": theme["colors"]["muted"] if not dark else "#5B6B7C",
             "font": theme["fonts"]["body"]} if it.get("desc") else {"text": "", "size": 4,
             "color": theme["colors"]["bg"], "font": theme["fonts"]["body"]},
        ])
        y += 0.95 if not it.get("desc") else 1.25


def l_two_col(slide, theme, d: dict):
    set_bg(slide, theme, alt=is_light_theme(theme))
    dark = is_light_theme(theme)
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Dua Kolom"),
                d.get("subtitle", ""), dark_text=dark)
    left = d.get("left", {})
    right = d.get("right", {})
    for x, col in ((0.7, left), (6.9, right)):
        textbox(slide, x, 2.5, 5.7, 4.0, [
            {"text": col.get("heading", ""), "size": 18, "bold": True,
             "color": theme["colors"]["accent"], "font": theme["fonts"]["head"]},
            {"text": col.get("body", ""), "size": 14,
             "color": theme["colors"]["text_dark"] if dark else theme["colors"]["text"],
             "font": theme["fonts"]["body"]},
        ])
        for b in col.get("bullets", [])[:5]:
            pass  # bullets sudah termasuk dalam body bila perlu
    # garis pemisah
    solid_rect(slide, 6.55, 2.5, 0.03, 4.0, theme["colors"]["line"])


def l_stats(slide, theme, d: dict):
    set_bg(slide, theme)
    title_block(slide, theme, d.get("kicker", "Angka Kunci"), d.get("title", "Dampak dalam Angka"),
                d.get("subtitle", ""))
    items = d.get("items", [])[:4]
    n = max(len(items), 1)
    card_w = (11.9 - 0.6 * (n - 1)) / n
    for i, it in enumerate(items):
        x = 0.7 + i * (card_w + 0.6)
        solid_rect(slide, x, 2.7, card_w, 3.3, theme["colors"]["surface_dark"],
                   theme["colors"]["line"], radius=True)
        accent_bar(slide, x, 2.7, card_w, 0.09, theme)
        textbox(slide, x + 0.3, 3.0, card_w - 0.6, 2.7, [
            {"text": it.get("value", "—"), "size": theme["sizes"]["kpi_value"], "bold": True,
             "color": theme["colors"]["accent2"] if i == 0 else "#FFFFFF",
             "font": theme["fonts"]["head"]},
            {"text": it.get("label", ""), "size": theme["sizes"]["kpi_label"],
             "color": theme["colors"]["muted"], "font": theme["fonts"]["body"]},
            {"text": it.get("desc", ""), "size": 11, "color": theme["colors"]["muted"],
             "font": theme["fonts"]["body"]} if it.get("desc") else
            {"text": "", "size": 4, "color": theme["colors"]["surface_dark"],
             "font": theme["fonts"]["body"]},
        ])


def l_chart(slide, theme, d: dict):
    set_bg(slide, theme, alt=is_light_theme(theme))
    dark = is_light_theme(theme)
    title_block(slide, theme, d.get("kicker", "Data"), d.get("title", "Grafik"),
                d.get("subtitle", ""), dark_text=dark)
    chart = d.get("chart", {})
    img = d.get("chart_image")  # fallback matplotlib PNG
    insight = d.get("insight", "")
    if img:
        try:
            slide.shapes.add_picture(img, Inches(0.7), Inches(2.5), Inches(7.6), Inches(4.2))
        except Exception:
            pass
    else:
        build_chart(slide, (0.7, 2.5, 7.6, 4.2), chart.get("kind", "column"),
                    chart.get("categories", []), chart.get("series", []), theme)
    textbox(slide, 8.7, 2.5, 3.9, 4.2, [
        {"text": "INSIGHT", "size": 12, "bold": True, "color": theme["colors"]["accent"],
         "font": theme["fonts"]["head"]},
        {"text": insight or "Tulis 1–2 kalimat makna data ini untuk audiens.",
         "size": 14, "color": theme["colors"]["text_dark"] if dark else theme["colors"]["text"],
         "font": theme["fonts"]["body"]},
        {"text": d.get("source", ""), "size": 11,
         "color": theme["colors"]["muted"], "font": theme["fonts"]["body"]},
    ])


def l_table(slide, theme, d: dict):
    set_bg(slide, theme, alt=is_light_theme(theme))
    dark = is_light_theme(theme)
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Tabel"),
                d.get("subtitle", ""), dark_text=dark)
    headers = d.get("headers", [])
    rows = d.get("rows", [])
    n_rows = len(rows) + 1
    n_cols = max(len(headers), max((len(r) for r in rows), default=0))
    if n_cols == 0:
        return
    left, top, width, height = Inches(0.7), Inches(2.5), Inches(11.9), Inches(4.2)
    gframe = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    tbl = gframe.table
    # lebar kolom merata
    for c in range(n_cols):
        tbl.columns[c].width = int(width / n_cols)
    # header
    for c in range(n_cols):
        cell = tbl.cell(0, c)
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = headers[c] if c < len(headers) else ""
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.name = theme["fonts"]["head"]
        run.font.color.rgb = hex_to_rgb("#FFFFFF")
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(theme["colors"]["primary"] if not dark else "#1F2937")
    # body belang-belang
    for r, row in enumerate(rows):
        for c in range(n_cols):
            cell = tbl.cell(r + 1, c)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(row[c]) if c < len(row) else ""
            run.font.size = Pt(11)
            run.font.name = theme["fonts"]["body"]
            run.font.color.rgb = hex_to_rgb(theme["colors"]["text_dark"] if dark else "#1A2B3C")
            cell.fill.solid()
            cell.fill.fore_color.rgb = hex_to_rgb("#F3F6FA" if r % 2 == 0 else "#FFFFFF")


def l_timeline(slide, theme, d: dict):
    set_bg(slide, theme)
    title_block(slide, theme, d.get("kicker", "Roadmap"), d.get("title", "Timeline"),
                d.get("subtitle", ""))
    items = d.get("items", [])[:5]
    n = max(len(items), 1)
    # garis horizontal
    solid_rect(slide, 0.9, 4.2, 11.5, 0.05, theme["colors"]["line"])
    seg = 11.5 / n
    for i, it in enumerate(items):
        x = 0.9 + i * seg + seg / 2
        # dot
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - 0.14), Inches(4.06), Inches(0.28), Inches(0.28))
        dot.fill.solid()
        dot.fill.fore_color.rgb = hex_to_rgb(theme["colors"]["accent"])
        dot.line.fill.background()
        textbox(slide, x - seg / 2 + 0.1, 2.6, seg - 0.2, 1.4, [
            {"text": it.get("date", ""), "size": 12, "bold": True, "color": theme["colors"]["accent"],
             "font": theme["fonts"]["head"], "align": PP_ALIGN.CENTER},
            {"text": it.get("title", ""), "size": 14, "bold": True, "color": "#FFFFFF",
             "font": theme["fonts"]["head"], "align": PP_ALIGN.CENTER},
        ])
        textbox(slide, x - seg / 2 + 0.1, 4.5, seg - 0.2, 1.6, [
            {"text": it.get("desc", ""), "size": 12, "color": theme["colors"]["muted"],
             "font": theme["fonts"]["body"], "align": PP_ALIGN.CENTER},
        ])


def l_image_text(slide, theme, d: dict):
    set_bg(slide, theme, alt=is_light_theme(theme))
    dark = is_light_theme(theme)
    img = d.get("image")
    # gambar kiri
    if img:
        try:
            slide.shapes.add_picture(img, Inches(0.7), Inches(0.5), Inches(5.8), Inches(6.5))
        except Exception:
            solid_rect(slide, 0.7, 0.5, 5.8, 6.5, theme["colors"]["line"])
    else:
        solid_rect(slide, 0.7, 0.5, 5.8, 6.5, theme["colors"]["bg2"], theme["colors"]["line"])
        textbox(slide, 1.0, 3.0, 5.2, 1.0, [
            {"text": "TEMPAT GAMBAR", "size": 16, "bold": True, "color": theme["colors"]["muted"],
             "font": theme["fonts"]["head"], "align": PP_ALIGN.CENTER}])
    textbox(slide, 7.0, 0.7, 5.6, 5.6, [
        {"text": (d.get("kicker") or "").upper(), "size": 12, "bold": True,
         "color": theme["colors"]["accent"], "font": theme["fonts"]["head"]},
        {"text": d.get("title", "Judul"), "size": theme["sizes"]["h1"], "bold": True,
         "color": theme["colors"]["text_dark"] if dark else theme["colors"]["text"],
         "font": theme["fonts"]["head"]},
        {"text": d.get("body", ""), "size": 14,
         "color": theme["colors"]["muted"] if not dark else "#4B5563",
         "font": theme["fonts"]["body"]},
    ])
    bullets = d.get("bullets", [])[:4]
    y = 4.4
    for b in bullets:
        textbox(slide, 7.0, y, 5.6, 0.5, [
            {"text": f"●  {b}" if isinstance(b, str) else f"●  {b.get('title','')}",
             "size": 13, "color": theme["colors"]["text_dark"] if dark else theme["colors"]["text"],
             "font": theme["fonts"]["body"]}])
        y += 0.45


def l_quote(slide, theme, d: dict):
    set_bg(slide, theme)
    solid_rect(slide, 2.2, 1.2, 8.9, 5.1, theme["colors"]["surface_dark"],
               theme["colors"]["line"], radius=True)
    textbox(slide, 2.9, 1.8, 7.5, 3.6, [
        {"text": "\u201C", "size": 60, "bold": True, "color": theme["colors"]["accent"],
         "font": theme["fonts"]["head"]},
        {"text": d.get("quote", "Kutipan inspiratif di sini."), "size": 24,
         "color": "#FFFFFF", "font": theme["fonts"]["body"]},
        {"text": f"— {d.get('author', 'Anonim')}", "size": 14,
         "color": theme["colors"]["muted"], "font": theme["fonts"]["body"]},
    ])


def l_closing(slide, theme, d: dict):
    set_bg(slide, theme)
    textbox(slide, 1.2, 1.8, 10.9, 3.0, [
        {"text": (d.get("kicker") or "TERIMA KASIH").upper(), "size": 14, "bold": True,
         "color": theme["colors"]["accent"], "font": theme["fonts"]["head"],
         "align": PP_ALIGN.CENTER},
        {"text": d.get("title", "Terima Kasih"), "size": 54, "bold": True,
         "color": theme["colors"]["text"], "font": theme["fonts"]["head"],
         "align": PP_ALIGN.CENTER},
        {"text": d.get("subtitle", ""), "size": 18, "color": theme["colors"]["muted"],
         "font": theme["fonts"]["body"], "align": PP_ALIGN.CENTER},
    ])
    cta = d.get("cta", "")
    if cta:
        solid_rect(slide, 5.4, 5.2, 2.5, 0.8, theme["colors"]["accent"], radius=True)
        textbox(slide, 5.4, 5.28, 2.5, 0.7, [
            {"text": cta, "size": 15, "bold": True, "color": "#FFFFFF",
             "font": theme["fonts"]["head"], "align": PP_ALIGN.CENTER}])


LAYOUTS = {
    "cover": l_cover,
    "agenda": l_agenda,
    "section": l_section,
    "bullets": l_bullets,
    "two-col": l_two_col,
    "stats": l_stats,
    "chart": l_chart,
    "table": l_table,
    "timeline": l_timeline,
    "image-text": l_image_text,
    "quote": l_quote,
    "closing": l_closing,
}
