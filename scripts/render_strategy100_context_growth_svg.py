#!/usr/bin/env python3
"""Render a reproducible SVG line chart from strategy100 per_turn.tsv files."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "strategy100"
OUT_FILE = ROOT / "assets" / "figures" / "strategy100_context_growth_log_20260211.svg"

WIDTH = 1600
HEIGHT = 900
MARGIN_LEFT = 120
MARGIN_RIGHT = 90
MARGIN_TOP = 100
MARGIN_BOTTOM = 140

PLOT_W = WIDTH - MARGIN_LEFT - MARGIN_RIGHT
PLOT_H = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

COLORS = {
    "baseline": "#e74c3c",
    "recap": "#f39c12",
    "snapshot": "#27ae60",
}


def read_points(tsv_path: Path) -> List[Tuple[int, int]]:
    points: List[Tuple[int, int]] = []
    with tsv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            turn = int(row["turn_index"])
            tokens = int(row["input_tokens"])
            if tokens > 0:
                points.append((turn, tokens))
    points.sort(key=lambda x: x[0])
    return points


def fmt_int(v: int) -> str:
    return f"{v:,}"


def map_x(turn: int, x_max: int) -> float:
    return MARGIN_LEFT + (turn / x_max) * PLOT_W


def map_y(val: int, y_min: int, y_max: int) -> float:
    lo = math.log10(y_min)
    hi = math.log10(y_max)
    pos = (math.log10(val) - lo) / (hi - lo)
    return MARGIN_TOP + (1.0 - pos) * PLOT_H


def build_svg(data: Dict[str, List[Tuple[int, int]]]) -> str:
    all_vals = [v for points in data.values() for _, v in points]
    y_min = min(all_vals)
    y_max = max(all_vals)
    x_max = max(t for points in data.values() for t, _ in points)

    # Keep dynamic range tight while preserving readable log ticks.
    y_min = int(10 ** math.floor(math.log10(y_min)))
    y_max = int(10 ** math.ceil(math.log10(y_max)))
    y_max = max(y_max, max(all_vals))

    decade_ticks: List[int] = []
    d = int(math.floor(math.log10(y_min)))
    d_end = int(math.ceil(math.log10(y_max)))
    while d <= d_end:
        decade_ticks.append(10 ** d)
        d += 1

    lines: List[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="100-turn context growth chart">'
    )
    lines.append('<rect width="100%" height="100%" fill="#ffffff" />')

    # Title and subtitle.
    lines.append(
        '<text x="70" y="56" font-family="Arial, Helvetica, sans-serif" '
        'font-size="54" font-weight="700" fill="#111111">'
        "100-Turn Context Growth: baseline vs recap vs snapshot"
        "</text>"
    )
    lines.append(
        '<text x="70" y="94" font-family="Arial, Helvetica, sans-serif" '
        'font-size="38" fill="#333333">'
        "input_tokens per turn (log scale)"
        "</text>"
    )

    # Plot border.
    lines.append(
        f'<rect x="{MARGIN_LEFT}" y="{MARGIN_TOP}" width="{PLOT_W}" height="{PLOT_H}" '
        'fill="#fafafa" stroke="#dddddd" stroke-width="1.5" />'
    )

    # Y grid + ticks.
    for tick in decade_ticks:
        if not (y_min <= tick <= y_max):
            continue
        y = map_y(tick, y_min, y_max)
        lines.append(
            f'<line x1="{MARGIN_LEFT}" y1="{y:.2f}" x2="{MARGIN_LEFT + PLOT_W}" y2="{y:.2f}" '
            'stroke="#e6e6e6" stroke-width="1" />'
        )
        lines.append(
            f'<text x="{MARGIN_LEFT - 14}" y="{y + 8:.2f}" text-anchor="end" '
            'font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#444444">'
            f"{fmt_int(tick)}"
            "</text>"
        )

    # X ticks (0..99, step 10).
    for turn in range(0, x_max + 1, 10):
        x = map_x(turn, x_max)
        lines.append(
            f'<line x1="{x:.2f}" y1="{MARGIN_TOP}" x2="{x:.2f}" y2="{MARGIN_TOP + PLOT_H}" '
            'stroke="#ececec" stroke-width="1" />'
        )
        lines.append(
            f'<text x="{x:.2f}" y="{MARGIN_TOP + PLOT_H + 38}" text-anchor="middle" '
            'font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#444444">'
            f"{turn}"
            "</text>"
        )

    # Axes.
    lines.append(
        f'<line x1="{MARGIN_LEFT}" y1="{MARGIN_TOP + PLOT_H}" x2="{MARGIN_LEFT + PLOT_W}" '
        f'y2="{MARGIN_TOP + PLOT_H}" stroke="#666666" stroke-width="2" />'
    )
    lines.append(
        f'<line x1="{MARGIN_LEFT}" y1="{MARGIN_TOP}" x2="{MARGIN_LEFT}" y2="{MARGIN_TOP + PLOT_H}" '
        'stroke="#666666" stroke-width="2" />'
    )

    # Axis labels.
    lines.append(
        f'<text x="{MARGIN_LEFT + PLOT_W / 2:.2f}" y="{HEIGHT - 44}" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#222222">'
        "Turn (0-99)"
        "</text>"
    )
    lines.append(
        f'<text x="48" y="{MARGIN_TOP + PLOT_H / 2:.2f}" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#222222" '
        f'transform="rotate(-90 48 {MARGIN_TOP + PLOT_H / 2:.2f})">'
        "input_tokens (log10)"
        "</text>"
    )

    # Strategy lines.
    for strategy in ("baseline", "recap", "snapshot"):
        points = data[strategy]
        poly = " ".join(
            f"{map_x(t, x_max):.2f},{map_y(v, y_min, y_max):.2f}" for t, v in points
        )
        lines.append(
            f'<polyline points="{poly}" fill="none" stroke="{COLORS[strategy]}" '
            'stroke-width="5" stroke-linejoin="round" stroke-linecap="round" />'
        )

    # Baseline failure marker at turn 29.
    fail_turn = 29
    fail_x = map_x(fail_turn, x_max)
    lines.append(
        f'<line x1="{fail_x:.2f}" y1="{MARGIN_TOP}" x2="{fail_x:.2f}" y2="{MARGIN_TOP + PLOT_H}" '
        'stroke="#e74c3c" stroke-width="3" stroke-dasharray="10,10" />'
    )
    lines.append(
        f'<text x="{fail_x + 14:.2f}" y="{MARGIN_TOP + 40}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#b63a2e">'
        "baseline failed at turn 29"
        "</text>"
    )

    # Legend.
    legend_x = MARGIN_LEFT + PLOT_W - 360
    legend_y = MARGIN_TOP + 34
    for idx, strategy in enumerate(("baseline", "recap", "snapshot")):
        y = legend_y + idx * 44
        lines.append(
            f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 56}" y2="{y}" '
            f'stroke="{COLORS[strategy]}" stroke-width="5" />'
        )
        lines.append(
            f'<text x="{legend_x + 70}" y="{y + 8}" '
            'font-family="Arial, Helvetica, sans-serif" font-size="30" fill="#222222">'
            f"{escape(strategy)}"
            "</text>"
        )

    recap_final = data["recap"][-1][1]
    snapshot_final = data["snapshot"][-1][1]
    ratio = recap_final / snapshot_final
    callout = f"snapshot uses ~{ratio:.1f}x fewer final input tokens than recap"

    # Callout box.
    box_x = 430
    box_y = HEIGHT - 210
    box_w = 740
    box_h = 96
    lines.append(
        f'<rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" rx="14" ry="14" '
        'fill="#fff5eb" stroke="#f39c12" stroke-width="3" />'
    )
    lines.append(
        f'<text x="{box_x + box_w / 2:.2f}" y="{box_y + 60}" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="700" '
        'fill="#2a2a2a">'
        f"{escape(callout)}"
        "</text>"
    )

    # Footer source.
    lines.append(
        f'<text x="70" y="{HEIGHT - 24}" font-family="Arial, Helvetica, sans-serif" '
        'font-size="24" fill="#666666">'
        "Source: moc-com/codex-reliability-probes / data/strategy100/**/per_turn.tsv"
        "</text>"
    )

    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    data = {
        "baseline": read_points(DATA_DIR / "baseline" / "per_turn.tsv"),
        "recap": read_points(DATA_DIR / "recap" / "per_turn.tsv"),
        "snapshot": read_points(DATA_DIR / "snapshot" / "per_turn.tsv"),
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(build_svg(data), encoding="utf-8")
    print(f"wrote: {OUT_FILE}")


if __name__ == "__main__":
    main()
