"""
make_ascii_svg.py
Converts source-prepped.png into a self-typing monochrome ASCII SVG.

    python scripts/make_ascii_svg.py

Reads:  source-prepped.png
Writes: avi-ascii.svg   (rename the constant below if you like)
"""
from PIL import Image

INPUT = "source-prepped.png"
OUTPUT = "avi-ascii.svg"

COLS, ROWS = 100, 53
CHAR_W, CHAR_H = 7, 12          # px per glyph cell in the SVG grid
FILL = "#c9d1d9"                # single light-gray fill (monochrome on purpose)
FONT = "SFMono-Regular, Consolas, 'Liberation Mono', monospace"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing


def image_to_grid(path: str):
    img = Image.open(path).convert("L").resize((COLS, ROWS))
    px = img.load()
    grid = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            brightness = px[x, y]  # 0 (black) - 255 (white)
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            row.append(RAMP[idx])
        grid.append("".join(row))
    return grid


def build_svg(grid):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    total_rows = len(grid)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="{FONT}">',
        f'<rect width="100%" height="100%" fill="transparent"/>',
        '<style>',
        f'text {{ font-size: {CHAR_H - 2}px; fill: {FILL}; white-space: pre; }}',
        '</style>',
    ]

    for i, row_text in enumerate(grid):
        y = (i + 1) * CHAR_H - 2
        stagger = i * 0.03  # top-to-bottom stagger, seconds
        row_w = width
        clip_id = f"wipe{i}"
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="0" y="{i*CHAR_H}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{row_w}" '
            f'begin="{stagger:.2f}s" dur="0.8s" fill="freeze" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1"/>'
            f'</rect>'
        )
        parts.append('</clipPath>')
        escaped = (row_text.replace("&", "&amp;").replace("<", "&lt;"))
        parts.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y}">{escaped}</text>'
            # small "cursor" block riding the wipe edge
            f'<rect y="{i*CHAR_H}" width="{CHAR_W*0.6:.1f}" height="{CHAR_H}" fill="{FILL}" opacity="0.6">'
            f'<animate attributeName="x" from="0" to="{row_w}" '
            f'begin="{stagger:.2f}s" dur="0.8s" fill="freeze" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1"/>'
            f'<animate attributeName="opacity" from="0.6" to="0" '
            f'begin="{stagger+0.75:.2f}s" dur="0.15s" fill="freeze"/>'
            f'</rect>'
            f'</g>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    grid = image_to_grid(INPUT)
    svg = build_svg(grid)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")
