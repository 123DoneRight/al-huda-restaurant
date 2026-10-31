#!/bin/bash
# Analyze each uploaded food photo with the vision model:
# description + horizontal subject position for the 16:9 -> 4:5 crop decision.
set -u
UP="/home/z/my-project/upload"
OUT="/tmp/vlm"
mkdir -p "$OUT"

PROMPT='This photo will be cropped from 16:9 landscape to a tall 4:5 portrait crop that keeps only the middle ~45% of the width, so I must choose the best horizontal window. Answer in EXACTLY this compact format, plain text, no markdown:
DESC: one sentence describing the food and setting
SUBJECT_X: the x-range occupied by the MAIN dish, as fractions of image width, e.g. 0.30-0.60
FOCAL: single strongest focal point as x,y fractions, e.g. 0.45,0.55
LEFT: what is in the left third of the frame
CENTER: what is in the center third
RIGHT: what is in the right third
VERDICT: best 4:5 crop window as x-range fractions, e.g. 0.25-0.65'

declare -A FILES=(
  [hero]="Somali_feast_commercial_menu_pho…_26f68eec_2K.jpg_f6a8616d_2K.jpg"
  [goat]="Roasted_goat_and_rice_platter_644b1f2d_2K.jpg"
  [chickenrice]="Chicken_and_rice_dish_4ccde9dd_2K.jpg"
  [drumsticks]="Pasta_and_tandoori_chicken_dish_b819fc7b_2K.jpg"
  [canjeero]="Somali_sweet_crepes_on_plate_5e1a3f05_2K.jpg"
  [sambusa]="Sambusas_and_chili_sauce_on_0b16206c_2K.jpg"
  [xalwo]="Somali_Hilwa_and_pastry_platter_e249d36e_2K.jpg"
  [shaah]="Somali_spiced_milk_tea_mug_aeb89120_2K.jpg"
)

for key in hero goat chickenrice drumsticks canjeero sambusa xalwo shaah; do
  f="${FILES[$key]}"
  echo "=== $key : $f ==="
  z-ai vision -p "$PROMPT" -i "$UP/$f" -o "$OUT/$key.json" && echo "saved $OUT/$key.json" || echo "FAILED $key"
done
echo "ALL DONE"
