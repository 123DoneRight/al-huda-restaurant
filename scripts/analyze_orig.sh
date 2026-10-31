#!/bin/bash
# Precise edge analysis of ORIGINAL photos: what touches each frame edge,
# and the exact plate bounding box (for crop window math).
set -u
UP="/home/z/my-project/upload"
OUT="/tmp/vlm"
mkdir -p "$OUT"

PROMPT='Analyze this 16:9 food photo precisely for cropping purposes. Answer in EXACTLY this format, plain text:
MAIN: the main dish/plate and its bounding box as fractions of width and height, like x:0.30-0.70 y:0.15-0.85
TOP: what content touches or is cut by the TOP edge of the photo (or "empty margin")
BOTTOM: what content touches or is cut by the BOTTOM edge (or "empty margin")
LEFT: what content is in the left 20% of the width
RIGHT: what content is in the right 20% of the width
MARGIN: approximate empty margin around the main plate as fractions, top/bottom/left/right'

declare -A FILES=(
  [goat]="Roasted_goat_and_rice_platter_644b1f2d_2K.jpg"
  [chickenrice]="Chicken_and_rice_dish_4ccde9dd_2K.jpg"
  [drumsticks]="Pasta_and_tandoori_chicken_dish_b819fc7b_2K.jpg"
  [canjeero]="Somali_sweet_crepes_on_plate_5e1a3f05_2K.jpg"
  [sambusa]="Sambusas_and_chili_sauce_on_0b16206c_2K.jpg"
  [xalwo]="Somali_Hilwa_and_pastry_platter_e249d36e_2K.jpg"
)

for key in goat chickenrice drumsticks canjeero sambusa xalwo; do
  echo "=== $key ==="
  z-ai vision -p "$PROMPT" -i "$UP/${FILES[$key]}" -o "$OUT/orig_$key.json" >/dev/null 2>&1 && echo ok || echo FAILED
done
echo DONE