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


def add_footer(slide, idx: int, total: int, theme, on_dark=None):
    cfg = theme.get("footer", {})
    if not cfg.get("show_number", True) and not cfg.get("text"):
        return
    if on_dark is None:
        on_dark = not is_light_theme(theme)
    color = MUT(theme, on_dark)
    blocks = []
    if cfg.get("text"):
        blocks.append({"text": cfg["text"], "size": theme["sizes"]["small"], "color": color, "font": theme["fonts"]["body"]})
    if cfg.get("show_number", True):
        if cfg.get("number_format", "fraction") == "plain":
            num = f"{idx}"
        else:
            num = f"{idx} / {total}"
        blocks.append({"text": num, "size": theme["sizes"]["small"], "color": color,
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
    if theme.get("title_bar", True):
        accent_bar(slide, 0.7, 1.95 if subtitle else 1.7, 1.2, 0.06, theme)


def is_light_theme(theme) -> bool:
    bg = theme["colors"]["bg"].lstrip("#").lower()
    # heuristik sederhana: luminance tinggi -> light
    try:
        r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) > 150
    except Exception:
        return False


# Layout konten (terang bila tema content_light) vs layout gelap (mengikuti bg).
CONTENT_TYPES = {"agenda", "bullets", "facts", "two-col", "chart", "table", "image-text"}


def content_is_light(theme) -> bool:
    if "content_light" in theme:
        return bool(theme["content_light"])
    return is_light_theme(theme)


def slide_is_light(slide_type: str, theme) -> bool:
    base_light = is_light_theme(theme)
    if slide_type in CONTENT_TYPES:
        return content_is_light(theme)
    return base_light


def MUT(theme, on_dark: bool) -> str:
    """Warna teks sekunder: muted biasa di slide terang, muted_dark di navy."""
    if on_dark:
        return theme["colors"].get("muted_dark", theme["colors"]["muted"])
    return theme["colors"]["muted"]


def BODY(theme) -> str:
    """Warna teks badan di slide terang."""
    return theme["colors"].get("body", theme["colors"]["text_dark"])


def est_lines(text: str, width_in: float, size_pt: float) -> int:
    """Perkiraan jumlah baris teks dalam lebar tertentu (anti-meluap)."""
    import math
    if not text:
        return 0
    cpl = max(width_in * 150.0 / max(size_pt, 6), 8)
    return max(int(math.ceil(len(str(text)) / cpl)), 1)


def card(slide, x, y, w, h, fill_hex):
    """Kartu: rounded rect tanpa garis tepi."""
    return solid_rect(slide, x, y, w, h, fill_hex, radius=True)


def badge(slide, x, y, text, fill_hex, color_hex, size=12, w=0.55, h=0.42, font="Calibri"):
    """Lencana kecil (angka/lencana kode): pill berisi teks tengah."""
    sp = solid_rect(slide, x, y, w, h, fill_hex, radius=True)
    tf = sp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = str(text)
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.name = font
    try:
        run.font.color.rgb = hex_to_rgb(color_hex)
    except Exception:
        pass
    return sp


def agenda_need_h(title: str, desc: str, col_w: float, title_size=15, desc_size=12) -> float:
    """Tinggi kartu agenda yang dibutuhkan (inci) berdasarkan isi teks."""
    tl = est_lines(title, col_w - 0.6, title_size)
    dl = est_lines(desc, col_w - 0.6, desc_size)
    return 0.62 + tl * 0.30 + dl * 0.235


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
         "color": MUT(theme, True), "font": theme["fonts"]["body"]},
    ])
    meta = "  •  ".join([x for x in [d.get("date"), d.get("author")] if x])
    if meta:
        textbox(slide, 0.9, 5.6, 6.8, 0.6, [
            {"text": meta, "size": theme["sizes"]["small"], "color": MUT(theme, True),
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
    set_bg(slide, theme, alt=content_is_light(theme))
    light = content_is_light(theme)
    title_block(slide, theme, d.get("kicker", "Agenda"), d.get("title", "Apa yang akan dibahas"),
                d.get("subtitle", ""), dark_text=light)
    items = d.get("items", [])[:6]
    n = max(len(items), 1)
    show_numbers = d.get("numbers", True)
    emphasis = d.get("emphasis", 0)
    per_row = 3 if n in (3, 6) else 4
    gold_dark = theme["colors"].get("gold_dark", theme["colors"]["accent"])

    def build(tsize, dsize):
        rows = [items[r:r + per_row] for r in range(0, len(items), per_row)]
        heights = []
        for row in rows:
            col_w = (11.9 - 0.5 * (len(row) - 1)) / len(row)
            need = max(agenda_need_h(it.get("title", ""), it.get("desc", ""), col_w, tsize, dsize)
                       for it in row)
            heights.append((row, col_w, max(need, 1.7)))
        return rows, heights

    rows, heights = build(15, 12)
    total = sum(h for _, _, h in heights) + 0.35 * (len(heights) - 1)
    if total > 4.2:  # teks panjang: kecilkan font sekali, lalu terima
        rows, heights = build(14, 11)
    y = 2.55
    for ri, (row, col_w, rh) in enumerate(heights):
        for ci, it in enumerate(row):
            i = ri * per_row + ci
            x = 0.7 + ci * (col_w + 0.5)
            is_hot = (i == emphasis)
            if light:
                fill = theme["colors"]["surface_dark"] if is_hot else theme["colors"].get("card", "#EEF2F8")
                tcol = "#FFFFFF" if is_hot else theme["colors"]["text_dark"]
                dcol = MUT(theme, True) if is_hot else theme["colors"]["muted"]
                ncol = theme["colors"]["accent"] if is_hot else gold_dark
            else:
                fill = theme["colors"]["surface_dark"]
                tcol = "#FFFFFF"
                dcol = MUT(theme, True)
                ncol = theme["colors"]["accent"]
            card(slide, x, y, col_w, rh, fill)
            ty = y + 0.18
            if show_numbers:
                textbox(slide, x + 0.25, ty, col_w - 0.5, 0.32, [
                    {"text": f"{i+1:02d}", "size": 13, "bold": True, "color": ncol,
                     "font": theme["fonts"]["head"]},
                ])
                ty += 0.32
            textbox(slide, x + 0.25, ty, col_w - 0.5, rh - (ty - y) - 0.18, [
                {"text": it.get("title", f"Poin {i+1}"), "size": 15, "bold": True,
                 "color": tcol, "font": theme["fonts"]["head"]},
                {"text": it.get("desc", ""), "size": 12, "color": dcol,
                 "font": theme["fonts"]["body"]},
            ])
        y += rh + 0.35


def l_section(slide, theme, d: dict):
    set_bg(slide, theme)
    accent_bar(slide, 0, 0, 0.14, 7.5, theme)
    textbox(slide, 1.2, 2.2, 10.9, 3.0, [
        {"text": (d.get("kicker") or "BAGIAN").upper(), "size": 14, "bold": True,
         "color": theme["colors"]["accent"], "font": theme["fonts"]["head"]},
        {"text": d.get("title", "Judul Bagian"), "size": 44, "bold": True,
         "color": theme["colors"]["text"], "font": theme["fonts"]["head"]},
        {"text": d.get("subtitle", ""), "size": 18, "color": MUT(theme, True),
         "font": theme["fonts"]["body"]},
    ])


def l_bullets(slide, theme, d: dict):
    set_bg(slide, theme, alt=content_is_light(theme))
    light = content_is_light(theme)
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Poin Utama"),
                d.get("subtitle", ""), dark_text=light)
    raw = d.get("items", [])[:6]
    items = [it if isinstance(it, dict) else {"title": it} for it in raw]
    numbered = d.get("numbered", False)
    n = max(len(items), 1)
    if n >= 5:  # padat: font lebih kecil, celah rapat
        y0, bottom, gap, tsize, dsize = 2.5, 6.8, 0.12, 13.5, 11.0
    else:
        y0, bottom, gap, tsize, dsize = 2.55, 6.72, 0.16, 16, 12.5
    card_h = (bottom - y0 - (n - 1) * gap) / n
    card_fill = theme["colors"].get("card", "#EEF2F8") if light else theme["colors"]["surface_dark"]
    tcol = theme["colors"]["text_dark"] if light else theme["colors"]["text"]
    y = y0
    for i, it in enumerate(items):
        card(slide, 0.7, y, 11.9, card_h, card_fill)
        # bilah aksen di dalam kartu
        solid_rect(slide, 0.88, y + 0.14, 0.07, max(card_h - 0.28, 0.1), theme["colors"]["accent"])
        tx = 1.25
        if numbered:
            badge(slide, tx, y + 0.14, f"{i+1}", theme["colors"]["primary"], "#FFFFFF", size=11)
            tx += 0.68
        textbox(slide, tx, y + 0.08, 0.7 + 11.9 - tx - 0.3, card_h - 0.16, [
            {"text": it.get("title", ""), "size": tsize, "bold": True, "color": tcol,
             "font": theme["fonts"]["head"]},
            {"text": it.get("desc", ""), "size": dsize, "color": theme["colors"]["muted"],
             "font": theme["fonts"]["body"]} if it.get("desc") else {"text": "", "size": 4,
             "color": card_fill, "font": theme["fonts"]["body"]},
        ])
        y += card_h + gap


def l_facts(slide, theme, d: dict):
    """Slide fakta lapangan: empat kartu ringkas + fakta dan risiko terpisah."""
    set_bg(slide, theme, alt=content_is_light(theme))
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Fakta Lapangan"),
                d.get("subtitle", ""), dark_text=True)
    facts = d.get("facts", [])[:4]
    n = max(len(facts), 1)
    gap = 0.22
    card_w = (11.9 - gap * (n - 1)) / n
    for i, fact in enumerate(facts):
        x = 0.7 + i * (card_w + gap)
        fill = theme["colors"]["surface_dark"] if i == n - 1 else theme["colors"].get("card", "#EEF2F8")
        value_color = theme["colors"]["accent"] if i == n - 1 else theme["colors"]["primary"]
        text_color = "#FFFFFF" if i == n - 1 else BODY(theme)
        sub_color = MUT(theme, True) if i == n - 1 else theme["colors"]["muted"]
        card(slide, x, 2.35, card_w, 1.75, fill)
        textbox(slide, x + 0.2, 2.55, card_w - 0.4, 1.35, [
            {"text": fact.get("value", ""), "size": 25, "bold": True, "color": value_color,
             "font": theme["fonts"]["head"], "align": PP_ALIGN.CENTER},
            {"text": fact.get("label", ""), "size": 12, "color": text_color,
             "font": theme["fonts"]["body"], "align": PP_ALIGN.CENTER},
            {"text": fact.get("detail", ""), "size": 10.5, "color": sub_color,
             "font": theme["fonts"]["body"], "align": PP_ALIGN.CENTER},
        ])

    # Dua area terpisah agar fakta lapangan tidak tercampur dengan risiko integrasi.
    card(slide, 0.7, 4.4, 5.72, 1.95, theme["colors"].get("card", "#EEF2F8"))
    textbox(slide, 1.0, 4.66, 5.12, 1.4, [
        {"text": "KONDISI EKSISTING", "size": 12, "bold": True,
         "color": theme["colors"].get("gold_dark", theme["colors"]["accent"]),
         "font": theme["fonts"]["body"]},
        {"text": d.get("existing", ""), "size": 14, "color": BODY(theme),
         "font": theme["fonts"]["body"]},
    ])
    card(slide, 6.88, 4.4, 5.72, 1.95, theme["colors"]["primary"])
    textbox(slide, 7.18, 4.66, 5.12, 1.4, [
        {"text": "RISIKO BILA DIHUBUNGKAN", "size": 12, "bold": True,
         "color": theme["colors"]["accent"], "font": theme["fonts"]["body"]},
        {"text": d.get("risk", ""), "size": 14, "color": "#FFFFFF",
         "font": theme["fonts"]["body"]},
        {"text": d.get("risk_note", ""), "size": 10.5, "color": MUT(theme, True),
         "font": theme["fonts"]["body"]},
    ])


def l_two_col(slide, theme, d: dict):
    set_bg(slide, theme, alt=content_is_light(theme))
    dark = content_is_light(theme)
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Dua Kolom"),
                d.get("subtitle", ""), dark_text=dark)
    left = d.get("left", {})
    right = d.get("right", {})
    card_fill = theme["colors"].get("card", "#EEF2F8") if dark else theme["colors"]["surface_dark"]
    hcol = theme["colors"]["text_dark"] if dark else theme["colors"]["accent"]
    for x, col in ((0.7, left), (6.9, right)):
        card(slide, x, 2.5, 5.7, 4.0, card_fill)
        textbox(slide, x + 0.35, 2.75, 5.0, 3.5, [
            {"text": col.get("heading", ""), "size": 18, "bold": True,
             "color": hcol, "font": theme["fonts"]["head"]},
            {"text": col.get("body", ""), "size": 14,
             "color": BODY(theme) if dark else theme["colors"]["text"],
             "font": theme["fonts"]["body"]},
        ])
        for b in col.get("bullets", [])[:5]:
            pass  # bullets sudah termasuk dalam body bila perlu


def l_stats(slide, theme, d: dict):
    set_bg(slide, theme)
    title_block(slide, theme, d.get("kicker", "Angka Kunci"), d.get("title", "Dampak dalam Angka"),
                d.get("subtitle", ""))
    items = d.get("items", [])[:4]
    n = max(len(items), 1)
    card_w = (11.9 - 0.6 * (n - 1)) / n
    for i, it in enumerate(items):
        x = 0.7 + i * (card_w + 0.6)
        card(slide, x, 2.9, card_w, 2.4, theme["colors"]["surface_dark"])
        textbox(slide, x + 0.3, 3.1, card_w - 0.6, 2.0, [
            {"text": it.get("value", "—"), "size": theme["sizes"]["kpi_value"], "bold": True,
             "color": theme["colors"]["accent"] if i == 0 else "#FFFFFF",
             "font": theme["fonts"]["head"]},
            {"text": it.get("label", ""), "size": theme["sizes"]["kpi_label"],
             "color": MUT(theme, True), "font": theme["fonts"]["body"]},
            {"text": it.get("desc", ""), "size": 11, "color": MUT(theme, True),
             "font": theme["fonts"]["body"]} if it.get("desc") else
            {"text": "", "size": 4, "color": theme["colors"]["surface_dark"],
             "font": theme["fonts"]["body"]},
        ])


def l_chart(slide, theme, d: dict):
    set_bg(slide, theme, alt=content_is_light(theme))
    dark = content_is_light(theme)
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
         "size": 14, "color": BODY(theme) if dark else theme["colors"]["text"],
         "font": theme["fonts"]["body"]},
        {"text": d.get("source", ""), "size": 11,
         "color": theme["colors"]["muted"], "font": theme["fonts"]["body"]},
    ])


def l_table(slide, theme, d: dict):
    set_bg(slide, theme, alt=content_is_light(theme))
    dark = content_is_light(theme)
    title_block(slide, theme, d.get("kicker", ""), d.get("title", "Tabel"),
                d.get("subtitle", ""), dark_text=dark)
    headers = d.get("headers", [])
    rows = d.get("rows", [])
    n_rows = len(rows) + 1
    n_cols = max(len(headers), max((len(r) for r in rows), default=0))
    if n_cols == 0:
        return
    # tinggi baris eksplisit agar tidak melar: header 0.55, isi adaptif
    header_h = 0.55
    body_h = 0.55 if len(rows) <= 5 else 0.45
    if header_h + len(rows) * body_h > 4.2:
        body_h = max((4.2 - header_h) / max(len(rows), 1), 0.36)
    total_h = header_h + len(rows) * body_h
    left, top, width = Inches(0.7), Inches(2.55), Inches(11.9)
    gframe = slide.shapes.add_table(n_rows, n_cols, left, top, width, Inches(total_h))
    tbl = gframe.table
    tbl.rows[0].height = Inches(header_h)
    for r in range(len(rows)):
        tbl.rows[r + 1].height = Inches(body_h)
    # lebar kolom: pakai col_widths (inci) bila diberikan, sisanya merata
    widths = d.get("col_widths") or []
    for c in range(n_cols):
        if c < len(widths):
            tbl.columns[c].width = Inches(widths[c])
        else:
            tbl.columns[c].width = int(width / n_cols)
    # header
    for c in range(n_cols):
        cell = tbl.cell(0, c)
        cell.text = ""
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.12)
        cell.margin_right = Inches(0.1)
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = headers[c] if c < len(headers) else ""
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.name = theme["fonts"]["head"]
        run.font.color.rgb = hex_to_rgb("#FFFFFF")
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(theme["colors"]["primary"])
    # body belang-belang
    for r, row in enumerate(rows):
        for c in range(n_cols):
            cell = tbl.cell(r + 1, c)
            cell.text = ""
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.1)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(row[c]) if c < len(row) else ""
            run.font.size = Pt(12)
            run.font.name = theme["fonts"]["body"]
            run.font.color.rgb = hex_to_rgb(BODY(theme) if dark else "#1A2B3C")
            cell.fill.solid()
            zebra = theme["colors"].get("card", "#F3F6FA")
            cell.fill.fore_color.rgb = hex_to_rgb(zebra if r % 2 == 0 else "#FFFFFF")


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
            {"text": it.get("desc", ""), "size": 12, "color": MUT(theme, True),
             "font": theme["fonts"]["body"], "align": PP_ALIGN.CENTER},
        ])


def l_image_text(slide, theme, d: dict):
    set_bg(slide, theme, alt=content_is_light(theme))
    dark = content_is_light(theme)
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
         "color": theme["colors"]["muted"] if not dark else BODY(theme),
         "font": theme["fonts"]["body"]},
    ])
    bullets = d.get("bullets", [])[:4]
    y = 4.4
    for b in bullets:
        textbox(slide, 7.0, y, 5.6, 0.5, [
            {"text": f"●  {b}" if isinstance(b, str) else f"●  {b.get('title','')}",
             "size": 13, "color": BODY(theme) if dark else theme["colors"]["text"],
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
         "color": MUT(theme, True), "font": theme["fonts"]["body"]},
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
        {"text": d.get("subtitle", ""), "size": 18, "color": MUT(theme, True),
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
    "facts": l_facts,
    "two-col": l_two_col,
    "stats": l_stats,
    "chart": l_chart,
    "table": l_table,
    "timeline": l_timeline,
    "image-text": l_image_text,
    "quote": l_quote,
    "closing": l_closing,
}
