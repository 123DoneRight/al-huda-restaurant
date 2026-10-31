#!/usr/bin/env python3
"""Combine QA screenshots into two labeled grids for vision-model review."""
from PIL import Image, ImageDraw
import os

OUT = "/home/z/my-project/scripts/out/shots"
grids = [
    ("desktop", ["desktop_hero", "desktop_plates", "desktop_menu", "desktop_sheet"]),
    ("mobile", ["mobile_hero", "mobile_plates", "mobile_menu"]),
]
for name, shots in grids:
    ims = [(s, Image.open(os.path.join(OUT, s + ".png"))) for s in shots]
    scale = 900 / max(im.width for _, im in ims)
    th = int(max(im.height for _, im in ims) * scale)
    cols = 2
    rows = (len(ims) + 1) // 2
    LBL = 30
    W, H = cols * 900, rows * (th + LBL)
    grid = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(grid)
    for i, (label, im) in enumerate(ims):
        w = int(im.width * scale)
        small = im.resize((w, int(im.height * scale)), Image.LANCZOS)
        c, r = i % cols, i // cols
        x0, y0 = c * 900, r * (th + LBL)
        grid.paste(small, (x0 + (900 - w) // 2, y0))
        d.text((x0 + 10, y0 + th + 8), label, fill="#000000")
    path = os.path.join(OUT, f"grid_{name}.jpg")
    grid.save(path, "JPEG", quality=80)
    print(path, grid.size, f"{os.path.getsize(path)/1024:.0f}KB")
