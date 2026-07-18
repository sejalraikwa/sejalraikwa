"""
render_heatmap_svg.py
Reads data/contributions.json and draws the classic 53-week x 7-day
calendar of rounded, colored boxes using a GitHub-ish green ramp.
Reveals once with a diagonal, line-after-line slide-down, then freezes
(no looping "glow"). Adds a Less->More legend and a stats footer.

    python scripts/render_heatmap_svg.py

Writes: contrib-heatmap.svg
"""
import json
import os

INPUT = os.path.join("data", "contributions.json")
OUTPUT = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

CELL = 12
GAP = 3
COLS = 53
ROWS = 7
MARGIN_L = 30
MARGIN_T = 20
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', monospace"


def level_color(day):
    level = day.get("level", 0)
    if level and level < len(PALETTE):
        return PALETTE[level]
    count = day.get("count", 0)
    if count == 0:
        return PALETTE[0]
    elif count < 3:
        return PALETTE[1]
    elif count < 6:
        return PALETTE[2]
    elif count < 10:
        return PALETTE[3]
    else:
        return PALETTE[4]


def build_svg(data):
    days = data["days"]
    stats = data.get("stats", {})

    width = MARGIN_L + COLS * (CELL + GAP) + 160  # extra room for legend
    height = MARGIN_T + ROWS * (CELL + GAP) + 50   # extra room for footer

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="{FONT}">',
        f'<style>',
        f'.cell {{ opacity: 0; transform: translateY(-6px); '
        f'animation: reveal 0.35s ease-out forwards; }}',
        f'@keyframes reveal {{ to {{ opacity: 1; transform: translateY(0); }} }}',
        f'</style>',
        f'<rect width="100%" height="100%" fill="transparent"/>',
    ]

    # pad days into a 53x7 grid, oldest first, column-major (weeks)
    for i, day in enumerate(days[-(COLS * ROWS):]):
        col = i // ROWS
        row = i % ROWS
        x = MARGIN_L + col * (CELL + GAP)
        y = MARGIN_T + row * (CELL + GAP)
        color = level_color(day)
        delay = (col * ROWS + row) * 0.004  # diagonal-ish, fast stagger
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
            f'<title>{day["date"]}: {day["count"]} contributions</title>'
            f'</rect>'
        )

    # legend: Less -> More
    legend_x = MARGIN_L + COLS * (CELL + GAP) + 20
    legend_y = MARGIN_T
    parts.append(f'<text x="{legend_x}" y="{legend_y+9}" font-size="11" fill="#8b949e">Less</text>')
    for i, color in enumerate(PALETTE):
        lx = legend_x + 32 + i * (CELL + 2)
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    parts.append(
        f'<text x="{legend_x + 32 + len(PALETTE)*(CELL+2) + 6}" y="{legend_y+9}" '
        f'font-size="11" fill="#8b949e">More</text>'
    )

    # footer stats
    total = stats.get("total_last_year", 0)
    current_streak = stats.get("current_streak", 0)
    longest_streak = stats.get("longest_streak", 0)
    footer_y = MARGIN_T + ROWS * (CELL + GAP) + 30
    footer_text = (
        f'{total} contributions in the last year - '
        f'current streak {current_streak}d - longest streak {longest_streak}d'
    )
    parts.append(
        f'<text x="{MARGIN_L}" y="{footer_y}" font-size="12" fill="#8b949e">{footer_text}</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    with open(INPUT) as f:
        data = json.load(f)
    svg = build_svg(data)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")
