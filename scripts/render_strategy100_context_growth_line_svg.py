#!/usr/bin/env python3
"""Render a publication-ready strategy100 context growth line chart (SVG).

This script reads:
  data/strategy100/{baseline,recap,snapshot}/per_turn.tsv

And writes:
  assets/figures/strategy100_context_growth_line_20260211.svg
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "strategy100"
OUT = ROOT / "assets" / "figures" / "strategy100_context_growth_line_20260211.svg"

WIDTH = 1800
HEIGHT = 1100
LEFT = 240
RIGHT = 120
TOP = 180
BOTTOM = 320
PLOT_W = WIDTH - LEFT - RIGHT
PLOT_H = HEIGHT - TOP - BOTTOM

COLORS = {
    "baseline": "#e74c3c",
    "recap": "#f39c12",
    "snapshot": "#27ae60",
}


def read_points(path: Path) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            t = int(row["turn_index"])
            y = int(row["input_tokens"])
            rows.append((t, y))
    rows.sort(key=lambda r: r[0])
    return rows


def fmt_num(n: int) -> str:
    return f"{n:,}"


def x_px(turn: int, x_max: int) -> float:
    return LEFT + (turn / x_max) * PLOT_W


def y_px(val: int, y_min: int, y_max: int) -> float:
    lo = math.log10(y_min)
    hi = math.log10(y_max)
    p = (math.log10(val) - lo) / (hi - lo)
    return TOP + (1.0 - p) * PLOT_H


def build_svg() -> str:
    baseline = read_points(DATA_ROOT / "baseline" / "per_turn.tsv")
    recap = read_points(DATA_ROOT / "recap" / "per_turn.tsv")
    snapshot = read_points(DATA_ROOT / "snapshot" / "per_turn.tsv")

    x_max = 99
    y_vals = [y for _, y in baseline + recap + snapshot if y > 0]
    y_min_data = min(y_vals)
    y_max_data = max(y_vals)

    # Clamp to clean log ticks while preserving data range.
    y_min = min(10_000, 10 ** int(math.floor(math.log10(y_min_data))))
    y_max = max(20_000_000, 10 ** int(math.ceil(math.log10(y_max_data))))

    # Keep sparse ticks to avoid visual crowding.
    ticks = [10_000, 50_000, 200_000, 1_000_000, 5_000_000, 20_000_000]

    def poly(points: list[tuple[int, int]]) -> str:
        return " ".join(
            f"{x_px(t, x_max):.2f},{y_px(y, y_min, y_max):.2f}" for t, y in points if y > 0
        )

    recap_final = recap[-1][1]
    snapshot_final = snapshot[-1][1]
    ratio = recap_final / snapshot_final

    lines: list[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-label="100-turn context growth line chart">'
    )
    lines.append(
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="100%" stop-color="#f8fafc"/>'
        "</linearGradient>"
        "</defs>"
    )
    lines.append('<rect x="0" y="0" width="100%" height="100%" fill="url(#bg)" />')

    # Header
    lines.append(
        '<text x="80" y="66" font-family="Arial, Helvetica, sans-serif" '
        'font-size="52" font-weight="700" fill="#111827">'
        "100-Turn Context Growth: baseline vs recap vs snapshot"
        "</text>"
    )
    lines.append(
        '<text x="80" y="112" font-family="Arial, Helvetica, sans-serif" '
        'font-size="30" fill="#374151">'
        "input_tokens per turn (log scale)"
        "</text>"
    )

    # Legend (above plot: fixed, non-overlapping area)
    legend_y = 150
    legend_x = LEFT + 10
    for i, key in enumerate(("baseline", "recap", "snapshot")):
        x0 = legend_x + i * 240
        lines.append(
            f'<line x1="{x0}" y1="{legend_y}" x2="{x0 + 54}" y2="{legend_y}" '
            f'stroke="{COLORS[key]}" stroke-width="6" />'
        )
        lines.append(
            f'<text x="{x0 + 66}" y="{legend_y + 8}" '
            'font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#1f2937">'
            f"{escape(key)}"
            "</text>"
        )

    # Plot panel
    lines.append(
        f'<rect x="{LEFT}" y="{TOP}" width="{PLOT_W}" height="{PLOT_H}" '
        'fill="#ffffff" stroke="#d1d5db" stroke-width="1.5" rx="8" />'
    )

    # Snapshot segment bands (every 10 turns) for interpretability.
    for start in range(0, 100, 10):
        if (start // 10) % 2 == 1:
            x0 = x_px(start, x_max)
            x1 = x_px(min(start + 10, x_max), x_max)
            lines.append(
                f'<rect x="{x0:.2f}" y="{TOP}" width="{(x1 - x0):.2f}" height="{PLOT_H}" '
                'fill="#ecfdf5" opacity="0.45" />'
            )

    # Y grid and labels.
    for v in ticks:
        if not (y_min <= v <= y_max):
            continue
        y = y_px(v, y_min, y_max)
        lines.append(
            f'<line x1="{LEFT}" y1="{y:.2f}" x2="{LEFT + PLOT_W}" y2="{y:.2f}" '
            'stroke="#e5e7eb" stroke-width="1" />'
        )
        lines.append(
            f'<text x="{LEFT - 16}" y="{y + 8:.2f}" text-anchor="end" '
            'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#4b5563">'
            f"{fmt_num(v)}"
            "</text>"
        )

    # X grid and labels.
    for t in range(0, 100, 10):
        x = x_px(t, x_max)
        lines.append(
            f'<line x1="{x:.2f}" y1="{TOP}" x2="{x:.2f}" y2="{TOP + PLOT_H}" '
            'stroke="#eef2f7" stroke-width="1" />'
        )
        lines.append(
            f'<text x="{x:.2f}" y="{TOP + PLOT_H + 40}" text-anchor="middle" '
            'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#4b5563">'
            f"{t}"
            "</text>"
        )

    # Axes
    lines.append(
        f'<line x1="{LEFT}" y1="{TOP + PLOT_H}" x2="{LEFT + PLOT_W}" y2="{TOP + PLOT_H}" '
        'stroke="#6b7280" stroke-width="2" />'
    )
    lines.append(
        f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{TOP + PLOT_H}" '
        'stroke="#6b7280" stroke-width="2" />'
    )
    lines.append(
        f'<text x="{LEFT + PLOT_W / 2:.2f}" y="{HEIGHT - 248}" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#111827">'
        "Turn (0-99)"
        "</text>"
    )
    lines.append(
        f'<text x="70" y="{TOP + PLOT_H / 2:.2f}" text-anchor="middle" '
        'transform="rotate(-90 70 '
        f'{TOP + PLOT_H / 2:.2f})" font-family="Arial, Helvetica, sans-serif" '
        'font-size="28" fill="#111827">'
        "input_tokens"
        "</text>"
    )

    # Series lines
    lines.append(
        f'<polyline points="{poly(baseline)}" fill="none" stroke="{COLORS["baseline"]}" '
        'stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />'
    )
    lines.append(
        f'<polyline points="{poly(recap)}" fill="none" stroke="{COLORS["recap"]}" '
        'stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />'
    )
    lines.append(
        f'<polyline points="{poly(snapshot)}" fill="none" stroke="{COLORS["snapshot"]}" '
        'stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />'
    )

    # Baseline fail marker at turn 29.
    fail_x = x_px(29, x_max)
    lines.append(
        f'<line x1="{fail_x:.2f}" y1="{TOP}" x2="{fail_x:.2f}" y2="{TOP + PLOT_H}" '
        'stroke="#ef4444" stroke-width="2.5" stroke-dasharray="9,8" />'
    )
    lines.append(
        f'<text x="{fail_x + 12:.2f}" y="{TOP + 52}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#b91c1c">'
        "baseline failed at turn 29"
        "</text>"
    )

    # Final points (markers only; labels moved to metric cards below plot).
    recap_x, recap_y = x_px(99, x_max), y_px(recap[-1][1], y_min, y_max)
    snap_x, snap_y = x_px(99, x_max), y_px(snapshot[-1][1], y_min, y_max)
    lines.append(
        f'<circle cx="{recap_x:.2f}" cy="{recap_y:.2f}" r="6.5" fill="{COLORS["recap"]}" />'
    )
    lines.append(
        f'<circle cx="{snap_x:.2f}" cy="{snap_y:.2f}" r="6.5" fill="{COLORS["snapshot"]}" />'
    )

    # Metric cards below plot (collision-free text area).
    card_y = HEIGHT - 200
    card_h = 76
    card_w = 360
    recap_card_x = LEFT + 80
    snapshot_card_x = recap_card_x + card_w + 36
    lines.append(
        f'<rect x="{recap_card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" '
        'fill="#fff7ed" stroke="#f39c12" stroke-width="2.5" />'
    )
    lines.append(
        f'<text x="{recap_card_x + 20}" y="{card_y + 32}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#92400e">'
        "recap final input_tokens"
        "</text>"
    )
    lines.append(
        f'<text x="{recap_card_x + 20}" y="{card_y + 60}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700" fill="#78350f">'
        f"{fmt_num(recap_final)}"
        "</text>"
    )

    lines.append(
        f'<rect x="{snapshot_card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" '
        'fill="#ecfdf5" stroke="#22c55e" stroke-width="2.5" />'
    )
    lines.append(
        f'<text x="{snapshot_card_x + 20}" y="{card_y + 32}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#166534">'
        "snapshot final input_tokens"
        "</text>"
    )
    lines.append(
        f'<text x="{snapshot_card_x + 20}" y="{card_y + 60}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700" fill="#14532d">'
        f"{fmt_num(snapshot_final)}"
        "</text>"
    )

    # Impact callout
    callout = f"snapshot uses ~{ratio:.1f}x fewer final input tokens than recap"
    call_x = snapshot_card_x + card_w + 36
    call_y = card_y
    call_w = 520
    call_h = 76
    lines.append(
        f'<rect x="{call_x}" y="{call_y}" width="{call_w}" height="{call_h}" rx="12" '
        'fill="#fff7ed" stroke="#f59e0b" stroke-width="3" />'
    )
    lines.append(
        f'<text x="{call_x + 24:.2f}" y="{call_y + 33}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" '
        'fill="#1f2937">'
        "impact"
        "</text>"
    )
    lines.append(
        f'<text x="{call_x + 24:.2f}" y="{call_y + 61}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" '
        'fill="#1f2937">'
        f"{escape(callout)}"
        "</text>"
    )

    # Footer
    lines.append(
        f'<text x="80" y="{HEIGHT - 26}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="21" fill="#6b7280">'
        "Source: moc-com/codex-reliability-probes / data/strategy100/**/per_turn.tsv"
        "</text>"
    )

    lines.append("</svg>")
    return "\n".join(lines)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_svg(), encoding="utf-8")
    print(f"wrote: {OUT}")


if __name__ == "__main__":
    main()
