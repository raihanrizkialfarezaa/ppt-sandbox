"""Fallback matplotlib -> PNG (untuk grafik kompleks/infografis).

Chart PNG ini TIDAK editable-datanya, jadi hanya dipakai bila
native chart tidak cukup (donut multi-ring, annotated, sparkline).
Selalu sertakan data-table editable di sampingnya bila memakai ini.
"""
from __future__ import annotations

from pathlib import Path


def render_mpl_chart(kind: str, labels: list, series: list, colors: list, out_png: str, title: str = "") -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    vals = series[0]["values"] if series else []
    if kind == "donut":
        ax.pie(vals, labels=labels, colors=colors or None, startangle=90,
               wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2))
        ax.axis("equal")
    elif kind == "line":
        for i, s in enumerate(series):
            ax.plot(labels, s["values"], marker="o", linewidth=2.5,
                    color=(colors[i] if colors and i < len(colors) else None), label=s.get("name", ""))
        ax.legend(frameon=False, fontsize=9)
        ax.grid(alpha=0.2)
    else:  # bar / column
        x = range(len(labels))
        n = max(len(series), 1)
        w = 0.8 / n
        for i, s in enumerate(series):
            offs = [(xi - 0.4 + w / 2 + i * w) for xi in x]
            ax.bar(offs, s["values"], width=w, color=(colors[i] if colors and i < len(colors) else None),
                   label=s.get("name", ""))
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=9)
        if len(series) > 1:
            ax.legend(frameon=False, fontsize=9)
        ax.grid(axis="y", alpha=0.2)

    if title:
        ax.set_title(title, fontsize=12, color="#333333")
    plt.tight_layout()
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return str(out)
