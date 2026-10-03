"""Native editable charts via python-pptx (data bisa diubah di PowerPoint)."""
from __future__ import annotations

from pptx.chart.data import CategoryChartData, ChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches

KIND_MAP = {
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "line": XL_CHART_TYPE.LINE,
    "pie": XL_CHART_TYPE.PIE,
    "doughnut": XL_CHART_TYPE.DOUGHNUT,
    "area": XL_CHART_TYPE.AREA,
}


def build_chart(slide, rect_in: tuple, kind: str, categories: list, series: list, theme: dict):
    """series = [{name, values:[...]}]. Mengembalikan chart object."""
    kind_key = (kind or "column").lower()
    ctype = KIND_MAP.get(kind_key, XL_CHART_TYPE.COLUMN_CLUSTERED)

    if kind_key in ("pie", "doughnut"):
        cd = ChartData()
        cd.categories = categories
        s0 = series[0] if series else {"name": "Series", "values": [1]}
        cd.add_series(s0.get("name", "Series"), tuple(s0.get("values", [])))
    else:
        cd = CategoryChartData()
        cd.categories = categories
        for s in series:
            cd.add_series(s.get("name", ""), tuple(s.get("values", [])))

    x, y, cx, cy = (Inches(v) for v in rect_in)
    gframe = slide.shapes.add_chart(ctype, x, y, cx, cy, cd)
    chart = gframe.chart
    chart.has_legend = len(series) > 1 or kind_key in ("line", "area")
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    try:
        chart.chart_style = int(theme.get("chart_style", 2))
    except Exception:
        pass
    if kind_key == "line" and len(chart.series) > 0:
        try:
            chart.series[0].smooth = True
        except Exception:
            pass
    # value labels untuk pie/doughnut agar informatif
    if kind_key in ("pie", "doughnut"):
        try:
            plot = chart.plots[0]
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.show_percentage = True
            dl.show_category_name = False
        except Exception:
            pass
    return chart
