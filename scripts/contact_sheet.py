#!/usr/bin/env python3
"""Build a contact sheet of the 8 uploaded images for visual review."""
from PIL import Image, ImageOps, ImageDraw
import os

SRC = "/home/z/my-project/upload"
files = [
    "Somali_feast_commercial_menu_pho…_26f68eec_2K.jpg_f6a8616d_2K.jpg",
    "Roasted_goat_and_rice_platter_644b1f2d_2K.jpg",
    "Chicken_and_rice_dish_4ccde9dd_2K.jpg",
    "Pasta_and_tandoori_chicken_dish_b819fc7b_2K.jpg",
    "Somali_sweet_crepes_on_plate_5e1a3f05_2K.jpg",
    "Sambusas_and_chili_sauce_on_0b16206c_2K.jpg",
    "Somali_Hilwa_and_pastry_platter_e249d36e_2K.jpg",
    "Somali_spiced_milk_tea_mug_aeb89120_2K.jpg",
]

TILE_W, TILE_H = 440, 550
LABEL_H = 34
COLS, ROWS = 4, 2
sheet = Image.new("RGB", (COLS * TILE_W, ROWS * (TILE_H + LABEL_H)), "#dddddd")
draw = ImageDraw.Draw(sheet)

for idx, fn in enumerate(files):
    im = Image.open(os.path.join(SRC, fn))
    im = ImageOps.exif_transpose(im).convert("RGB")
    orig_w, orig_h = im.size
    # fit whole image into tile (letterbox) so we can judge composition
    scale = min(TILE_W / orig_w, TILE_H / orig_h)
    tw, th = int(orig_w * scale), int(orig_h * scale)
    small = im.resize((tw, th), Image.LANCZOS)
    col, row = idx % COLS, idx // COLS
    x0, y0 = col * TILE_W, row * (TILE_H + LABEL_H)
    sheet.paste(small, (x0 + (TILE_W - tw) // 2, y0 + (TILE_H - th) // 2))
    tag = f"{idx+1}: {fn[:34]} ({orig_w}x{orig_h})"
    draw.text((x0 + 8, y0 + TILE_H + 8), tag, fill="#000000")
    print(f"{idx+1}. {fn}  -> {orig_w}x{orig_h}  ratio {orig_w/orig_h:.2f}")

sheet.save("/tmp/contact.jpg", "JPEG", quality=72)
print("sheet:", sheet.size, os.path.getsize("/tmp/contact.jpg"))
