"""
prep_photo.py
Run once per source photo:
    python scripts/prep_photo.py source-photo.jpg

Pipeline:
  1. Remove the background with rembg -> subject isolated on transparency.
  2. Boost local contrast with OpenCV CLAHE (fixes flatly-lit faces).
  3. Composite onto pure white so background maps to the blank end
     of the ASCII ramp (white -> space glyph).

Output: source-prepped.png (grayscale, same folder as input)
"""
import sys
import os
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep(input_path: str) -> str:
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # Step 1: remove background -> RGBA
    cutout_bytes = remove(input_bytes)
    cutout = Image.open(__import__("io").BytesIO(cutout_bytes)).convert("RGBA")

    # Step 2: CLAHE contrast boost on the RGB channels (in LAB space,
    # boosting only the L channel keeps colors from blowing out)
    rgba = np.array(cutout)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    rgb_boosted = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    # Step 3: composite onto pure white using the alpha mask
    white_bg = np.full_like(rgb_boosted, 255)
    alpha_f = (alpha.astype(np.float32) / 255.0)[:, :, None]
    composited = (rgb_boosted.astype(np.float32) * alpha_f +
                  white_bg.astype(np.float32) * (1 - alpha_f)).astype(np.uint8)

    # Grayscale for the ASCII step
    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)

    out_path = os.path.join(
        os.path.dirname(input_path) or ".",
        "source-prepped.png"
    )
    Image.fromarray(gray).save(out_path)
    print(f"Wrote {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
