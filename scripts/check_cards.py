#!/usr/bin/env python3
"""Pixel-level check: crop each .dcard__img box from the QA screenshots and
measure color variance - a blank/placeholder box would be near-uniform."""
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright

HTML = "/home/z/my-project/download/Al Huda Restaurant v1.2.html"
OUT = "/home/z/my-project/scripts/out/shots"

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 390, "height": 844})
    page.goto("file://" + HTML, wait_until="networkidle")
    page.wait_for_timeout(3500)
    # scroll through so lazy + ScrollTrigger reveals fire
    total = page.evaluate("document.body.scrollHeight")
    y = 0
    while y < total:
        page.evaluate(f"window.scrollTo(0,{y})")
        page.wait_for_timeout(260)
        y += 600
    page.evaluate("document.getElementById('dishes').scrollIntoView()")
    page.wait_for_timeout(1200)
    # per-card boxes in viewport coords + full-page screenshot
    boxes = page.evaluate(
        "() => [...document.querySelectorAll('.dcard')].map(c => {"
        " const r = c.querySelector('.dcard__img').getBoundingClientRect();"
        " const name = c.querySelector('.h3').textContent;"
        " return {name, x: r.x, y: r.y + window.scrollY, w: r.width, h: r.height,"
        " op: getComputedStyle(c).opacity} })")
    page.screenshot(path=f"{OUT}/mobile_plates_full.png", full_page=True)
    im = Image.open(f"{OUT}/mobile_plates_full.png").convert("RGB")
    print(f"full-page shot {im.size}")
    for bxc in boxes:
        x, y, w, h = bxc["x"], bxc["y"], bxc["w"], bxc["h"]
        crop = im.crop((int(x), int(y), int(x + w), int(y + h)))
        a = np.asarray(crop, dtype=np.float32)
        # variance across channels + mean saturation proxy (max-min channel)
        std = float(a.std())
        sat = float((a.max(axis=2) - a.min(axis=2)).mean())
        crop.save(f"{OUT}/card_{bxc['name'].replace(' ', '_')}.png")
        print(f"{bxc['name']:20s} opacity={bxc['op']:>4} std={std:6.1f} colorfulness={sat:6.1f}"
              f"  {'BLANK?' if std < 8 else 'has photo content'}")
    b.close()
