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

WIDTH = 1600
HEIGHT = 980
LEFT = 120
RIGHT = 80
TOP = 130
BOTTOM = 190
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

    # Geometric tick sequence gives readable log-grid labels.
    ticks = [
        10_000,
        20_000,
        50_000,
        100_000,
        200_000,
        500_000,
        1_000_000,
        2_000_000,
        5_000_000,
        10_000_000,
        20_000_000,
    ]

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
        '<text x="70" y="60" font-family="Arial, Helvetica, sans-serif" '
        'font-size="52" font-weight="700" fill="#111827">'
        "100-Turn Context Growth: baseline vs recap vs snapshot"
        "</text>"
    )
    lines.append(
        '<text x="70" y="100" font-family="Arial, Helvetica, sans-serif" '
        'font-size="30" fill="#374151">'
        "input_tokens per turn (log scale)"
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
            f'<text x="{LEFT - 14}" y="{y + 8:.2f}" text-anchor="end" '
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
            f'<text x="{x:.2f}" y="{TOP + PLOT_H + 38}" text-anchor="middle" '
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
        f'<text x="{LEFT + PLOT_W / 2:.2f}" y="{HEIGHT - 70}" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#111827">'
        "Turn (0-99)"
        "</text>"
    )
    lines.append(
        f'<text x="44" y="{TOP + PLOT_H / 2:.2f}" text-anchor="middle" '
        'transform="rotate(-90 44 '
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
        f'<text x="{fail_x + 10:.2f}" y="{TOP + 38}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#b91c1c">'
        "baseline failed at turn 29"
        "</text>"
    )

    # Final point callouts.
    recap_x, recap_y = x_px(99, x_max), y_px(recap[-1][1], y_min, y_max)
    snap_x, snap_y = x_px(99, x_max), y_px(snapshot[-1][1], y_min, y_max)
    lines.append(
        f'<circle cx="{recap_x:.2f}" cy="{recap_y:.2f}" r="6.5" fill="{COLORS["recap"]}" />'
    )
    lines.append(
        f'<circle cx="{snap_x:.2f}" cy="{snap_y:.2f}" r="6.5" fill="{COLORS["snapshot"]}" />'
    )
    lines.append(
        f'<text x="{recap_x - 6:.2f}" y="{recap_y - 12:.2f}" text-anchor="end" '
        'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#92400e">'
        f"recap final: {fmt_num(recap_final)}"
        "</text>"
    )
    lines.append(
        f'<text x="{snap_x - 6:.2f}" y="{snap_y - 12:.2f}" text-anchor="end" '
        'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#166534">'
        f"snapshot final: {fmt_num(snapshot_final)}"
        "</text>"
    )

    # Legend
    legend_x = LEFT + PLOT_W - 360
    legend_y = TOP + 32
    for i, key in enumerate(("baseline", "recap", "snapshot")):
        y = legend_y + i * 40
        lines.append(
            f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 54}" y2="{y}" '
            f'stroke="{COLORS[key]}" stroke-width="5" />'
        )
        lines.append(
            f'<text x="{legend_x + 66}" y="{y + 7}" '
            'font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#1f2937">'
            f"{escape(key)}"
            "</text>"
        )

    # Impact callout
    callout = f"snapshot uses ~{ratio:.1f}x fewer final input tokens than recap"
    call_x = 355
    call_y = HEIGHT - 146
    call_w = 900
    call_h = 78
    lines.append(
        f'<rect x="{call_x}" y="{call_y}" width="{call_w}" height="{call_h}" rx="12" '
        'fill="#fff7ed" stroke="#f59e0b" stroke-width="3" />'
    )
    lines.append(
        f'<text x="{call_x + call_w / 2:.2f}" y="{call_y + 49}" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-size="32" font-weight="700" '
        'fill="#1f2937">'
        f"{escape(callout)}"
        "</text>"
    )

    # Footer
    lines.append(
        f'<text x="70" y="{HEIGHT - 18}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="22" fill="#6b7280">'
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

