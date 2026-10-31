#!/usr/bin/env python3
"""
Al Huda Restaurant - photo pipeline
Crops the 8 uploaded 16:9 photos to the site's 4:5 slots using the
vision-model-guided horizontal windows, applies one consistent
editorial grade (auto-contrast, gentle saturation/contrast lift,
final-size unsharp mask) and emits optimized WebP data URIs.
"""
import base64, io, json, os
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

SRC = "/home/z/my-project/upload"
OUT = "/home/z/my-project/scripts/out"
os.makedirs(OUT, exist_ok=True)

FILES = {
    "hero":        "Somali_feast_commercial_menu_pho…_26f68eec_2K.jpg_f6a8616d_2K.jpg",
    "goat":        "Roasted_goat_and_rice_platter_644b1f2d_2K.jpg",
    "chickenrice": "Chicken_and_rice_dish_4ccde9dd_2K.jpg",
    "drumsticks":  "Pasta_and_tandoori_chicken_dish_b819fc7b_2K.jpg",
    "canjeero":    "Somali_sweet_crepes_on_plate_5e1a3f05_2K.jpg",
    "sambusa":     "Sambusas_and_chili_sauce_on_0b16206c_2K.jpg",
    "xalwo":       "Somali_Hilwa_and_pastry_platter_e249d36e_2K.jpg",
    "shaah":       "Somali_spiced_milk_tea_mug_aeb89120_2K.jpg",
}

# horizontal center (fraction of width) of the crop window:
# blend of vision-model focal point and gradient-energy optimum
CX = {
    "hero": 0.55, "goat": 0.522, "chickenrice": 0.514, "drumsticks": 0.467,
    "canjeero": 0.507, "sambusa": 0.491, "xalwo": 0.601, "shaah": 0.500,
}
# output pixel sizes (2x of CSS render size) and webp quality
SPEC = {
    "hero": (960, 1200, 78),
    "goat": (640, 800, 75), "chickenrice": (640, 800, 75), "drumsticks": (640, 800, 75),
    "canjeero": (640, 800, 75), "sambusa": (640, 800, 75),
    "xalwo": (640, 800, 75), "shaah": (640, 800, 75),
}


def crop_4x5(im, cx):
    """Crop a 4:5 portrait window at full height, centered at cx (fraction of width)."""
    w, h = im.size
    cw = int(round(h * 4 / 5))                      # window width for full height
    cw = min(cw, w)
    left = int(round(cx * w - cw / 2))
    left = max(0, min(left, w - cw))                # clamp into frame
    return im.crop((left, 0, left + cw, h))


def grade(im):
    """One consistent editorial grade for all photos."""
    try:
        im = ImageOps.autocontrast(im, cutoff=1, preserve_tone=True)
    except TypeError:
        im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Color(im).enhance(1.10)       # gentle saturation lift
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    return im


def to_webp(im, quality):
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


manifest = {}
crops_for_sheet = []
for key, fn in FILES.items():
    im = Image.open(os.path.join(SRC, fn))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im = crop_4x5(im, CX[key])
    im = grade(im)
    tw, th, q = SPEC[key]
    im = im.resize((tw, th), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    data = to_webp(im, q)
    path = os.path.join(OUT, key + ".webp")
    with open(path, "wb") as f:
        f.write(data)
    manifest[key] = {
        "webp_b64": base64.b64encode(data).decode("ascii"),
        "bytes": len(data),
        "size": [tw, th],
    }
    crops_for_sheet.append((key, im))
    print(f"{key:12s} {tw}x{th} q{q}  {len(data)/1024:7.1f} KB  -> {path}")

total = sum(m["bytes"] for m in manifest.values())
print(f"TOTAL: {total/1024:.1f} KB for 8 images")

# contact sheet of the final crops (for VLM verification)
from PIL import ImageDraw
TILE_W, TILE_H, LBL = 300, 375, 26
COLS = 4
ROWS = (len(crops_for_sheet) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * TILE_W, ROWS * (TILE_H + LBL)), "#cccccc")
d = ImageDraw.Draw(sheet)
for i, (key, im) in enumerate(crops_for_sheet):
    small = im.resize((TILE_W, TILE_H), Image.LANCZOS)
    c, r = i % COLS, i // COLS
    x0, y0 = c * TILE_W, r * (TILE_H + LBL)
    sheet.paste(small, (x0, y0))
    d.text((x0 + 8, y0 + TILE_H + 6), f"{i+1}. {key}", fill="#000000")
sheet.save(os.path.join(OUT, "crops_sheet.jpg"), "JPEG", quality=80)
print("crop sheet:", os.path.join(OUT, "crops_sheet.jpg"))

with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f)
print("manifest written")
