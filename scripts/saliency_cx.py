#!/usr/bin/env python3
"""Compute saliency (gradient energy) optimal 4:5 crop windows for the
contested images and print recommended cx values."""
import numpy as np
from PIL import Image, ImageOps
import os

SRC = "/home/z/my-project/upload"
FILES = {
    "goat":        "Roasted_goat_and_rice_platter_644b1f2d_2K.jpg",
    "drumsticks":  "Pasta_and_tandoori_chicken_dish_b819fc7b_2K.jpg",
    "xalwo":       "Somali_Hilwa_and_pastry_platter_e249d36e_2K.jpg",
    "sambusa":     "Sambusas_and_chili_sauce_on_0b16206c_2K.jpg",
    "canjeero":    "Somali_sweet_crepes_on_plate_5e1a3f05_2K.jpg",
    "chickenrice": "Chicken_and_rice_dish_4ccde9dd_2K.jpg",
    "hero":        "Somali_feast_commercial_menu_pho…_26f68eec_2K.jpg_f6a8616d_2K.jpg",
    "shaah":       "Somali_spiced_milk_tea_mug_aeb89120_2K.jpg",
}
VLM_CX = {"hero": 0.50, "goat": 0.57, "chickenrice": 0.52, "drumsticks": 0.48,
          "canjeero": 0.505, "sambusa": 0.50, "xalwo": 0.58, "shaah": 0.50}

for key, fn in FILES.items():
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, fn))).convert("L")
    im = im.resize((688, 384))  # downscale for speed; aspect preserved
    a = np.asarray(im, dtype=np.float32)
    gx = np.abs(np.diff(a, axis=1))            # horizontal gradient energy
    energy = gx.sum(axis=0)                     # per-column energy
    energy = np.convolve(energy, np.ones(21) / 21, mode="same")  # smooth
    w = energy.shape[0]
    win = int(round(384 * 4 / 5))               # window width at this scale
    win = min(win, w)
    # slide window, maximize contained energy with slight center preference
    best_cx, best_score = 0.5, -1
    for left in range(0, w - win + 1, 2):
        s = energy[left:left + win].sum()
        cx = (left + win / 2) / w
        pen = 1 - 0.15 * abs(cx - VLM_CX[key])  # gentle pull to VLM focal
        s *= pen
        if s > best_score:
            best_score, best_cx = s, cx
    print(f"{key:12s} energy-optimal cx={best_cx:.3f}   (VLM focal {VLM_CX[key]})   -> use {0.5*best_cx+0.5*VLM_CX[key]:.3f}")
