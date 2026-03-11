"""Generate matplotlib charts and return them as base64-encoded PNGs plus JSON data."""
import io
import base64
import logging
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    plt.style.use("ggplot")


def generate_chart(
    data: list[dict],
    chart_type: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    label_column: Optional[str] = None,
    title: str = "",
) -> tuple[dict, str]:
    """Render a chart and return ``(chart_data_json, base64_png)``."""
    df = pd.DataFrame(data)
    if df.empty:
        return {}, ""

    x_col, y_col, label_col = _resolve_columns(df, x_column, y_column, label_column)

    renderers = {
        "bar": _bar,
        "line": _line,
        "pie": _pie,
    }
    renderer = renderers.get(chart_type, _bar)
    chart_data, fig = renderer(df, x_col, y_col, label_col, title)

    image_b64 = _fig_to_base64(fig)
    plt.close(fig)

    return chart_data, image_b64


# ---------------------------------------------------------------------------
# Column resolution
# ---------------------------------------------------------------------------

def _resolve_columns(
    df: pd.DataFrame,
    x_column: Optional[str],
    y_column: Optional[str],
    label_column: Optional[str],
) -> tuple[str, str, Optional[str]]:
    columns = list(df.columns)
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    non_numeric = [c for c in columns if c not in numeric]

    x = x_column if x_column and x_column in columns else (non_numeric[0] if non_numeric else columns[0])
    y = y_column if y_column and y_column in columns else (numeric[0] if numeric else columns[-1])
    lbl = label_column if label_column and label_column in columns else None
    return x, y, lbl


# ---------------------------------------------------------------------------
# Chart renderers
# ---------------------------------------------------------------------------

def _bar(df: pd.DataFrame, x: str, y: str, lbl: Optional[str], title: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = df[x].astype(str).tolist()
    values = pd.to_numeric(df[y], errors="coerce").fillna(0).tolist()

    colors = plt.cm.Set2.colors[: len(labels)]
    ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title[:80] or f"{y} by {x}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return _chart_json("bar", labels, y, values), fig


def _line(df: pd.DataFrame, x: str, y: str, lbl: Optional[str], title: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = df[x].astype(str).tolist()
    values = pd.to_numeric(df[y], errors="coerce").fillna(0).tolist()

    ax.plot(labels, values, marker="o", linewidth=2, markersize=6, color="#2196F3")
    ax.fill_between(range(len(labels)), values, alpha=0.1, color="#2196F3")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title[:80] or f"{y} over {x}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return _chart_json("line", labels, y, values), fig


def _pie(df: pd.DataFrame, x: str, y: str, lbl: Optional[str], title: str):
    fig, ax = plt.subplots(figsize=(8, 8))
    col = lbl or x
    labels = df[col].astype(str).tolist()[:8]
    values = pd.to_numeric(df[y], errors="coerce").fillna(0).tolist()[:8]

    colors = plt.cm.Set3.colors[: len(labels)]
    ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
    ax.set_title(title[:80] or f"{y} Distribution")
    plt.tight_layout()

    return _chart_json("pie", labels, y, values), fig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chart_json(chart_type: str, labels: list, y_label: str, values: list) -> dict:
    """Return a Chart.js-compatible data dict."""
    return {
        "chart_type": chart_type,
        "labels": labels,
        "datasets": [{"label": y_label, "data": values}],
    }


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
