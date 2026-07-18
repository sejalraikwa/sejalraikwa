"""
make_info_card.py
Builds a small SVG styled like `neofetch` output: a title bar, then
colored key/value rows. This is where the "story numbers can't tell"
lives -- the contribution graph already covers stats.

    python scripts/make_info_card.py            # animated
    STATIC=1 python scripts/make_info_card.py    # frozen frame, for local previews

Writes: info-card.svg

EDIT THE `ROWS` LIST BELOW with your own info before running.
"""
import os

OUTPUT = "info-card.svg"
USERNAME = "sejalraikwa"

# ---- EDIT ME: your own key/value lines ----------------------------------
ROWS = [
    ("Now",        "Building & shipping things"),
    ("Prev",       "Your previous role / project"),
    ("Stack",      "Python * JavaScript * SQL"),
    ("Highlights", "A standout project or achievement"),
]
# --------------------------------------------------------------------------

WIDTH = 490
ROW_H = 34
TITLE_H = 40
HEIGHT = TITLE_H + ROW_H * len(ROWS) + 20

KEY_COLOR = "#39d353"     # green, matches the heatmap palette
VAL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
BORDER = "#30363d"
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', monospace"

STATIC = os.environ.get("STATIC") == "1"


def build_svg():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" font-family="{FONT}">',
        f'<rect width="100%" height="100%" rx="8" fill="{BG_COLOR}" stroke="{BORDER}"/>',
        # fake title bar dots
        f'<circle cx="20" cy="20" r="6" fill="#ff5f56"/>',
        f'<circle cx="40" cy="20" r="6" fill="#ffbd2e"/>',
        f'<circle cx="60" cy="20" r="6" fill="#27c93f"/>',
        f'<text x="{WIDTH/2}" y="25" text-anchor="middle" font-size="13" fill="#8b949e">'
        f'{USERNAME}@github</text>',
    ]

    for i, (key, val) in enumerate(ROWS):
        y = TITLE_H + i * ROW_H + 22
        delay = i * 0.25
        line = (
            f'<g>'
            f'<text x="24" y="{y}" font-size="15" fill="{KEY_COLOR}" font-weight="bold">{key}</text>'
            f'<text x="150" y="{y}" font-size="15" fill="{VAL_COLOR}">{val}</text>'
            f'</g>'
        )
        if not STATIC:
            line = (
                f'<g opacity="0" transform="translate(-12,0)">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-12,0" to="0,0" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
                f'<text x="24" y="{y}" font-size="15" fill="{KEY_COLOR}" font-weight="bold">{key}</text>'
                f'<text x="150" y="{y}" font-size="15" fill="{VAL_COLOR}">{val}</text>'
                f'</g>'
            )
        parts.append(line)

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}{' (static)' if STATIC else ''}")
