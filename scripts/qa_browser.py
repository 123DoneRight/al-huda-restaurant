#!/usr/bin/env python3
"""Headless QA of the built site: console errors, image loading, placeholder
badges, sheet interaction, and section screenshots at desktop + mobile sizes."""
import json, os, sys
from playwright.sync_api import sync_playwright

HTML = "/home/z/my-project/download/Al Huda Restaurant v1.2.html"
OUT = "/home/z/my-project/scripts/out/shots"
os.makedirs(OUT, exist_ok=True)
results = {"console_errors": [], "failed_requests": []}

with sync_playwright() as p:
    browser = p.chromium.launch()
    for label, vw, vh in (("desktop", 1440, 960), ("mobile", 390, 844)):
        page = browser.new_page(viewport={"width": vw, "height": vh})
        page.on("console", lambda m: results["console_errors"].append(f"[{m.type}] {m.text}")
                if m.type in ("error",) else None)
        page.on("requestfailed", lambda r: results["failed_requests"].append(r.url[:120]))
        page.goto("file://" + HTML, wait_until="networkidle")
        page.wait_for_timeout(3800)  # let the veil lift + hero timeline finish

        # scroll through the page so ScrollTrigger reveals fire, then rest
        total = page.evaluate("document.body.scrollHeight")
        y = 0
        while y < total:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(240)
            y += 700
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(900)

        # ---- functional checks (desktop only, run once is enough) ----
        if label == "desktop":
            checks = {}
            checks["hero img decoded"] = page.evaluate(
                "() => { const i = document.querySelector('#hero-art .arch img');"
                " return i && i.complete && i.naturalWidth > 0 }")
            checks["7 dish imgs decoded"] = page.evaluate(
                "() => [...document.querySelectorAll('.dcard__img img')]"
                ".every(i => i.complete && i.naturalWidth > 0)")
            checks["dish img count == 7"] = page.evaluate(
                "document.querySelectorAll('.dcard__img img').length") == 7
            checks["no photo placeholder badges"] = page.evaluate(
                "() => !document.querySelector('#hero-art [data-placeholder], .dcard__img [data-placeholder], .dcard__img.ph')")
            badge_texts = page.evaluate(
                "() => [...document.querySelectorAll('.ph')].map(e => e.getAttribute('data-placeholder'))")
            checks["remaining .ph slots = story/cater/map only"] = sorted(badge_texts) == [
                "Catering photo", "Founder or cook portrait", "Static map image"]
            # hero parallax safety: img must cover arch at rest
            checks["hero img covers arch"] = page.evaluate(
                "() => { const a = document.querySelector('#hero-art .arch').getBoundingClientRect();"
                " const i = document.querySelector('#hero-art .arch img').getBoundingClientRect();"
                " return i.top <= a.top + 1 && i.bottom >= a.bottom - 1 && i.left <= a.left + 1 && i.right >= a.right - 1 }")
            # sheet interaction: click Details on card 4 (Chicken Suqaar)
            page.evaluate("document.querySelectorAll('.dcard')[3].scrollIntoView({block:'center'})")
            page.wait_for_timeout(600)
            page.click("document.querySelectorAll('.dcard__more')[3]", force=True) \
                if False else page.evaluate("document.querySelectorAll('.dcard__more')[3].click()")
            page.wait_for_timeout(650)
            checks["sheet opens"] = page.evaluate(
                "() => document.getElementById('sheet').classList.contains('is-open')")
            checks["sheet title = Chicken Suqaar"] = page.evaluate(
                "() => document.getElementById('sheet-t').textContent") == "Chicken Suqaar"
            sheet_img = page.evaluate(
                "() => { const w = document.getElementById('sheet-imgw');"
                " const i = document.getElementById('sheet-img');"
                " return !w.hidden && i.src.startsWith('data:image/webp') && i.naturalWidth > 0 }")
            checks["sheet shows dish photo"] = sheet_img
            page.screenshot(path=f"{OUT}/{label}_sheet.png")
            page.evaluate("closeSheet()")
            page.wait_for_timeout(400)
            results["checks"] = checks

        # ---- section screenshots ----
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(700)
        page.screenshot(path=f"{OUT}/{label}_hero.png")
        page.evaluate("document.getElementById('dishes').scrollIntoView()")
        page.wait_for_timeout(900)
        page.screenshot(path=f"{OUT}/{label}_plates.png")
        page.evaluate("document.getElementById('menu').scrollIntoView()")
        page.wait_for_timeout(900)
        page.screenshot(path=f"{OUT}/{label}_menu.png")
        page.close()

    browser.close()

print(json.dumps(results, indent=1))
bad = [k for k, v in results.get("checks", {}).items() if not v]
print("\nCHECKS:", "ALL PASS" if not bad else f"FAILED: {bad}")
if results["console_errors"] or results["failed_requests"]:
    print("console errors:", results["console_errors"][:6])
    print("failed requests:", results["failed_requests"][:6])
sys.exit(1 if bad or results["console_errors"] else 0)
