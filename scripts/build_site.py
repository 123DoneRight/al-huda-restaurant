#!/usr/bin/env python3
"""
Al Huda Restaurant v1.1 -> v1.2 build
Integrates the 8 real photos (hero feast + 7 signature plates) into the site:
  - hero arch gets the feast photo (parallax-safe 120% height img)
  - signature plates strip rebuilt with 7 cards in the client's order
    (Xalwo, Sambusa, Canjeero, Chicken Suqaar, Chicken drumsticks,
     Bariis iyo hilib, Shaah) - Chicken Suqaar replaces the old beef Suqaar
  - marquee + Mains menu updated for consistency
  - dish detail sheet now shows the photo too
  - photo CSS (object-fit cover, clipping, hover zoom preserved)
All edits are exact-string replacements with count assertions.
"""
import json, os, sys

SRC_HTML = "/home/z/my-project/upload/Al Huda Restaurant v1.1.html"
MANIFEST = "/home/z/my-project/scripts/out/manifest.json"
OUT_HTML = "/home/z/my-project/download/Al Huda Restaurant v1.2.html"
os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)

with open(SRC_HTML, encoding="utf-8") as f:
    html = f.read()
with open(MANIFEST) as f:
    M = json.load(f)


def uri(key):
    return "data:image/webp;base64," + M[key]["webp_b64"]


def rep(old, new, count=1):
    global html
    found = html.count(old)
    assert found == count, f"anchor found {found}x (expected {count}): {old[:90]!r}"
    html = html.replace(old, new, count)


# ---------------------------------------------------------------- 1. photo CSS
css_anchor = ".arch{border-radius:999px 999px 0 0}"
photo_css = """
/* real photography */
.hero__art .arch{overflow:hidden;background:var(--sky-200)}
.hero__art .arch img{position:absolute;left:0;top:-10%;width:100%;height:120%;object-fit:cover;display:block}
.dcard__img{position:relative;overflow:hidden;background:var(--sky-200)}
.dcard__img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
img.art{-webkit-user-drag:none;user-select:none}
.dcard__img::after{content:"";position:absolute;inset:0;z-index:1;box-shadow:inset 0 0 0 1px rgba(15,43,70,.08);pointer-events:none;border-radius:inherit}
.sheet__img{position:relative;width:100%;aspect-ratio:16/10;overflow:hidden;border-radius:6px;background:var(--sky-200)}
.sheet__img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}"""
rep(css_anchor, css_anchor + photo_css)

# ---------------------------------------------------------------- 2. hero photo
hero_alt = "A Somali table feast at Al Huda: spiced rice with goat, sambusas, pasta and sweets"
rep(
    '<div class="arch ph" data-art="hero" data-placeholder="Hero photo or video"></div>',
    '<div class="arch"><img class="art" src="' + uri("hero") + '" alt="' + hero_alt
    + '" width="960" height="1200" decoding="async" draggable="false"></div>',
)

# ---------------------------------------------------------------- 3. signature plates (7 cards)
def card(num, key, alt, name, price, tags, story, ing, note):
    tag_spans = "".join('<span class="tag">' + t + "</span>" for t in tags)
    tags_attr = ",".join(tags)
    return (
        '      <li class="dcard" data-name="' + name + '" data-story="' + story
        + '" data-ing="' + ing + '" data-note="' + note + '" data-tags="' + tags_attr + '">\n'
        '        <span class="dcard__num">' + num + "</span>\n"
        '        <div class="dcard__img"><img class="art" src="' + uri(key)
        + '" alt="' + alt + '" width="640" height="800" loading="lazy" decoding="async" draggable="false">'
        '<button class="dcard__more" type="button">Details</button></div>\n'
        '        <div class="dcard__row"><h3 class="h3">' + name + "</h3>"
        '<span class="price">' + price + "</span></div>\n"
        '        <p class="dcard__story">' + story + "</p>\n"
        '        <div class="tags">' + tag_spans + "</div>\n"
        "      </li>"
    )


CARDS = [
    card("01", "xalwo",
         "Somali xalwo halwa with butter pastries on a platter",
         "Xalwo", "$7", ["Vegetarian"],
         "Sweet halwa and butter pastry, scented with cardamom and nutmeg.",
         "Sugar, cornstarch, ghee, cardamom, nutmeg, almonds",
         "Traditionally served with coffee at celebrations."),
    card("02", "sambusa",
         "Golden fried sambusas served with green basbaas chili sauce",
         "Sambusa", "$8", ["Halal", "Spicy"],
         "Crisp triangles filled with spiced beef or lentil.",
         "Wheat pastry, beef or lentils, onion, chili, cilantro",
         "Order of three. Lentil option is vegetarian."),
    card("03", "canjeero",
         "Stack of soft Somali canjeero pancakes on a plate",
         "Canjeero", "$9", ["Vegetarian"],
         "Spongy fermented pancake with ghee and sugar, or stew.",
         "Wheat and corn flour, yeast, water, ghee, sugar",
         "Made fresh on the pan each morning."),
    card("04", "chickenrice",
         "Chicken suqaar with vegetables over yellow bariis rice",
         "Chicken Suqaar", "$22", ["Halal", "Spicy"],
         "Chicken sautéed with peppers, onion and xawaash, served over bariis.",
         "Chicken, basmati rice, bell pepper, onion, garlic, xawaash spice blend, cilantro",
         "Comes with banana and basbaas, our green chili sauce."),
    card("05", "drumsticks",
         "Grilled chicken drumsticks served with pasta and salad",
         "Chicken drumsticks", "$18", ["Halal"],
         "Grilled drumsticks with pasta (basto), salad and basbaas.",
         "Chicken drumsticks, spaghetti, bell pepper, onion, garlic, green chili sauce",
         "Pasta the Somali way — ask for banana and hot sauce."),
    card("06", "goat",
         "Roasted goat shoulder with yellow spiced rice and salad",
         "Bariis iyo hilib", "$26", ["Halal"],
         "Goat shoulder over rice perfumed with cardamom and clove.",
         "Basmati rice, goat, cardamom, cloves, cinnamon, raisins, ghee",
         "Served with banana and basbaas, our green chili sauce."),
    card("07", "shaah",
         "Glass mug of shaah, Somali spiced milk tea",
         "Shaah", "$4", ["Vegetarian"],
         "Milk tea simmered with cardamom, cinnamon and ginger.",
         "Black tea, milk, cardamom, cinnamon, ginger, sugar",
         "Refills are part of the welcome."),
]

track_open = '<ul class="strip__track" id="track">'
i0 = html.index(track_open) + len(track_open)
i1 = html.index("</ul>", i0)
html = html[:i0] + "\n" + "\n".join(CARDS) + "\n    " + html[i1:]

# ---------------------------------------------------------------- 4. marquee (both sets)
mq_old = ('<div class="marquee__set"><span>Bariis iyo hilib</span><i></i><span>Suqaar</span><i></i>'
          "<span>Canjeero</span><i></i><span>Sambusa</span><i></i><span>Xalwo</span><i></i>"
          "<span>Shaah</span><i></i></div>")
mq_new = ('<div class="marquee__set"><span>Xalwo</span><i></i><span>Sambusa</span><i></i>'
          "<span>Canjeero</span><i></i><span>Chicken Suqaar</span><i></i>"
          "<span>Chicken drumsticks</span><i></i><span>Bariis iyo hilib</span><i></i>"
          "<span>Shaah</span><i></i></div>")
rep(mq_old, mq_new, 2)

# ---------------------------------------------------------------- 5. Mains menu consistency
rep(
    '<h3 class="h3">Suqaar</h3><i class="leader"></i><span class="price">$22</span></div>'
    "<p>Cubed beef, peppers, onion, xawaash.</p>",
    '<h3 class="h3">Chicken Suqaar</h3><i class="leader"></i><span class="price">$22</span></div>'
    "<p>Sautéed chicken, peppers, onion, xawaash, over rice.</p>",
)
rep(
    '<p>Chicken stew with potato, carrot and spice.</p><div class="tags"><span class="tag">Halal</span></div></li>',
    '<p>Chicken stew with potato, carrot and spice.</p><div class="tags"><span class="tag">Halal</span></div></li>\n'
    '        <li class="item"><div class="item__top"><h3 class="h3">Chicken drumsticks</h3>'
    '<i class="leader"></i><span class="price">$18</span></div>'
    "<p>Grilled, with pasta (basto) and salad.</p>"
    '<div class="tags"><span class="tag">Halal</span></div></li>',
)

# ---------------------------------------------------------------- 6. dish sheet gets the photo
rep(
    '<button class="sheet__x" id="sheet-x" type="button">Close</button>',
    '<button class="sheet__x" id="sheet-x" type="button">Close</button>\n'
    '    <div class="sheet__img" id="sheet-imgw" hidden><img id="sheet-img" alt=""></div>',
)
rep(
    "  function openSheet(li,btn){\n"
    "    lastBtn=btn;\n"
    "    $('#sheet-t').textContent=li.getAttribute('data-name');",
    "  function openSheet(li,btn){\n"
    "    lastBtn=btn;\n"
    "    var im=$('.dcard__img img',li),si=$('#sheet-img'),sw=$('#sheet-imgw');\n"
    "    if(im&&si&&sw){si.src=im.getAttribute('src');si.alt=im.alt||li.getAttribute('data-name');sw.hidden=false}else if(sw){sw.hidden=true}\n"
    "    $('#sheet-t').textContent=li.getAttribute('data-name');",
)

# ---------------------------------------------------------------- write + sanity
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

checks = {
    "photo placeholders gone": 'data-placeholder="Dish photo' not in html
    and 'data-placeholder="Hero photo' not in html,
    "7 cards": html.count('<li class="dcard"') == 7,
    "7 imgs in strip": html.count('<div class="dcard__img"><img class="art"') == 7,
    "no ph on photo slots": 'class="dcard__img ph"' not in html
    and 'class="arch ph" data-art="hero"' not in html,
    "chicken suqaar card": 'data-name="Chicken Suqaar"' in html,
    "drumsticks card": 'data-name="Chicken drumsticks"' in html,
    "old beef suqaar gone": 'data-name="Suqaar"' not in html,
    "marquee updated x2": html.count("<span>Chicken Suqaar</span>") == 2,
    "menu suqaar updated": html.count("<h3 class=\"h3\">Chicken Suqaar</h3>") >= 2,
    "sheet img wired": 'id="sheet-imgw"' in html and "si.src=im.getAttribute" in html,
    "photo css present": ".dcard__img img{position:absolute;inset:0" in html,
    "images not native-draggable": html.count('draggable="false"') == 8
    and "img.art{-webkit-user-drag:none" in html,
    "drawn art kept for story/cater/map": all(
        f'data-art="{k}"' in html for k in ("story", "cater", "map")
    ),
}
bad = [k for k, ok in checks.items() if not ok]
for k, ok in checks.items():
    print(("PASS " if ok else "FAIL ") + k)
if bad:
    sys.exit("FAILED: " + ", ".join(bad))
print(f"\nWROTE {OUT_HTML}  ({os.path.getsize(OUT_HTML)/1024:.0f} KB)")
