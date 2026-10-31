#!/bin/bash
# Per-crop verification at full resolution with fair criteria:
# plates touching top/bottom is inherent to the original tight shots and OK.
set -u
OUTD="/home/z/my-project/scripts/out"
R="/tmp/vlm/cropcheck"
mkdir -p "$R"

PROMPT='This is a 4:5 portrait crop for a restaurant dish card. The ORIGINAL photo was 16:9 landscape and tightly framed (the plate often intentionally fills the top and bottom of the original frame - that is fine and expected). Judge ONLY: (1) is the main food subject substantially visible and appetizing, (2) is anything important awkwardly sliced at the LEFT or RIGHT edge of THIS crop, (3) is the composition balanced enough for a dish card. Answer in exactly two lines:
SCORE: PASS or FAIL
WHY: one short sentence'

declare -A NAMES=(
  [hero]="table feast with multiple plates"
  [goat]="roasted goat/lamb with yellow rice"
  [chickenrice]="chicken curry with yellow rice"
  [drumsticks]="grilled chicken drumsticks with pasta"
  [canjeero]="pancake stack"
  [sambusa]="samosas with green sauce"
  [xalwo]="cookies and dark cake platter"
  [shaah]="glass mug of milky tea"
)

for key in hero goat chickenrice drumsticks canjeero sambusa xalwo shaah; do
  echo "=== $key ==="
  z-ai vision -p "$PROMPT This card is for: ${NAMES[$key]}." -i "$OUTD/$key.webp" -o "$R/$key.json" >/dev/null 2>&1 && echo ok || echo FAILED
done
echo DONE