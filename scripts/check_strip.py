#!/usr/bin/env python3
"""Proper card verification: horizontally scroll the dish strip on mobile and
screenshot each card in-viewport; also test the horizontal drag interaction."""
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright

HTML = "/home/z/my-project/download/Al Huda Restaurant v1.2.html"
OUT = "/home/z/my-project/scripts/out/shots"

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 390, "height": 844}, has_touch=True)
    page.goto("file://" + HTML, wait_until="networkidle")
    page.wait_for_timeout(3500)
    page.evaluate("document.getElementById('dishes').scrollIntoView()")
    page.wait_for_timeout(1200)

    strip_info = page.evaluate(
        "() => { const s = document.getElementById('strip');"
        " return {sw: s.scrollWidth, cw: s.clientWidth, cards: s.querySelectorAll('.dcard').length} }")
    print("strip:", strip_info)

    names = page.evaluate(
        "() => [...document.querySelectorAll('.dcard .h3')].map(h => h.textContent)")
    n = strip_info["cards"]
    sw, cw = strip_info["sw"], strip_info["cw"]
    for i in range(n):
        target = i * (sw - cw) / max(1, n - 1)
        page.evaluate(f"() => document.getElementById('strip').scrollTo({{left: {target}, behavior: 'instant'}})")
        page.wait_for_timeout(450)
        shot = f"{OUT}/mcard_{i}.png"
        page.screenshot(path=shot)
        im = Image.open(shot).convert("RGB")
        a = np.asarray(im, dtype=np.float32)
        std = float(a.std())
        print(f"card {i+1} {names[i]:20s} scrolled-to, viewport shot std={std:6.1f}")

    # drag interaction: mouse down on strip, move left, check scrollLeft changed
    before = page.evaluate("document.getElementById('strip').scrollLeft")
    box = page.evaluate(
        "() => { const r = document.getElementById('strip').getBoundingClientRect();"
        " return {x: r.x, y: r.y, w: r.width, h: r.height} }")
    cx, cy = box["x"] + box["w"] / 2, box["y"] + 80
    page.mouse.move(cx, cy)
    page.mouse.down()
    for dx in range(0, 160, 20):
        page.mouse.move(cx - dx, cy, steps=3)
        page.wait_for_timeout(30)
    page.mouse.up()
    page.wait_for_timeout(300)
    after = page.evaluate("document.getElementById('strip').scrollLeft")
    print(f"drag: scrollLeft {before} -> {after}  {'DRAG WORKS' if after > before + 30 else 'DRAG STUCK'}")

    # progress bar reflects scroll
    bar = page.evaluate(
        "() => { const b = document.getElementById('bar');"
        " const r = b.getBoundingClientRect(); return r.width }")
    print(f"progress bar width after scroll: {bar:.0f}px")
    b.close()
