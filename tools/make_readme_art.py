"""Draws the pictures in the README: docs/images/banner.png and docs/images/loop.png.

    python tools/make_readme_art.py

Needs Pillow and the Roboto fonts (Apache 2.0, from fonts.google.com) installed on the computer.
The pictures are drawings, not measurements: the bars in the banner show the idea of the skill
(costly, uneven audio blocks on the left; cheap, even ones on the right; the dashed line is the time
one block may take).
"""
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "images")
S = 2                                   # everything is drawn at twice the size and scaled down
BG = (5, 7, 12)
HOT = (255, 88, 52)
WARM = (255, 176, 64)
COOL = (40, 200, 240)
PALE = (200, 245, 255)
DIM = (96, 118, 136)
FONT_DIRS = [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"), "C:/Windows/Fonts",
             os.path.expanduser("~/.fonts"), "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF",
             "/usr/share/fonts/truetype/roboto", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]


def font(weight, px):
    name = "Roboto-%s.ttf" % weight
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return ImageFont.truetype(p, int(round(px * S)))
    sys.exit("make_readme_art: font %s not found (install Roboto from fonts.google.com)" % name)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def heat(t):                            # 0 = hot, 1 = cool
    return mix(HOT, WARM, t / 0.45) if t < 0.45 else mix(WARM, COOL, (t - 0.45) / 0.4)


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def text(d, xy, s, f, fill, spacing=0.0, align="l"):
    """Draws s with extra space between letters; xy is the left, center or right of the baseline box."""
    widths = [d.textlength(c, font=f) for c in s]
    total = sum(widths) + spacing * S * (len(s) - 1)
    x = xy[0] * S - (total / 2 if align == "c" else total if align == "r" else 0)
    for c, w in zip(s, widths):
        d.text((x, xy[1] * S), c, font=f, fill=fill)
        x += w + spacing * S


def canvas(w, h):
    img = Image.new("RGB", (w * S, h * S), BG)
    px = img.load()
    for y in range(h * S):              # a faint lift toward the bottom
        k = (y / (h * S)) ** 2
        c = mix(BG, (10, 16, 26), k)
        for x in range(w * S):
            px[x, y] = c
    return img


def glow(img, layer, radius, gain=1.0):
    """Adds layer and a blurred copy of it to img."""
    soft = layer.filter(ImageFilter.GaussianBlur(radius * S))
    if gain != 1.0:
        soft = soft.point(lambda v: int(min(255, v * gain)))
    return ImageChops.add(ImageChops.add(img, soft), layer)


def banner():
    W, H = 1280, 360
    img = canvas(W, H)
    rng = random.Random(3630)
    base, top_hot, top_cool = 300, 150, 262          # the floor, the tallest hot bar, the cool level
    budget = 196                                     # the dashed line: the time one block may take
    n, gap = 128, 3
    bw = (W - 2 * 28 - gap * (n - 1)) / n
    bars = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(bars)
    for i in range(n):
        t = i / (n - 1)
        fall = smooth(0.30, 0.66, t)                 # 0 on the left, 1 on the right
        level = 228 + (top_cool - 228) * fall        # the typical top of a bar at this place
        jitter = (1 - fall) * rng.uniform(-34, 30) + fall * rng.uniform(-3, 3)
        if fall < 0.5 and rng.random() < 0.16 * (1 - fall):
            jitter -= rng.uniform(40, 228 - top_hot)  # a costly block
        y = max(top_hot, min(base - 6, level + jitter))
        x0 = 28 + i * (bw + gap)
        c = heat(t * 0.9 + 0.1 * fall)
        over = y < budget
        d.rounded_rectangle([x0 * S, y * S, (x0 + bw) * S, base * S], radius=2 * S,
                            fill=c if not over else mix(c, (255, 255, 255), 0.18))
    # fade the bars toward the floor so they read as light, not as blocks
    fade = Image.new("L", img.size, 0)
    fd = ImageDraw.Draw(fade)
    for y in range(top_hot * S, base * S):
        k = (y - top_hot * S) / ((base - top_hot) * S)
        fd.line([(0, y), (img.size[0], y)], fill=int(255 * (1.0 - 0.72 * k)))
    bars = Image.composite(bars, Image.new("RGB", img.size, (0, 0, 0)), fade)
    img = glow(img, bars, 9, 0.9)
    d = ImageDraw.Draw(img)
    # the floor line and the block budget
    d.line([(0, base * S), (W * S, base * S)], fill=mix(BG, PALE, 0.35), width=S)
    x = 28
    while x < W - 28:
        d.line([(x * S, budget * S), ((x + 10) * S, budget * S)], fill=mix(BG, PALE, 0.55), width=S)
        x += 18
    text(d, (W - 28, budget - 20), "ONE BLOCK'S TIME", font("Medium", 11), mix(BG, PALE, 0.6), 2.0, "r")
    # title and caption
    text(d, (W / 2, 38), "mpc-plugin-optimize", font("Black", 62), (245, 252, 255), 0.5, "c")
    text(d, (W / 2, 114), "A CLAUDE SKILL", font("Medium", 15), COOL, 6.0, "c")
    text(d, (W / 2, 320), "MEASURED CPU SAVINGS FOR AKAI MPC PLUGINS, WITH THE SAME SOUND", font("Medium", 17),
         (196, 212, 224), 3.0, "c")
    # the thin lattice strip along the top
    for x in range(0, W, 12):
        d.line([(x * S, 0), ((x + 6) * S, 6 * S), ((x + 12) * S, 0)], fill=mix(BG, HOT if x < W * 0.45 else COOL, 0.8), width=S)
    return img.resize((W, H), Image.Resampling.LANCZOS)


STEPS = [("COUNT", "instructions in", "every audio block"),
         ("FIND", "the function and the", "pattern that cost them"),
         ("CHANGE", "one thing", "at a time"),
         ("PROVE", "the output is the", "same, bit for bit"),
         ("TIME", "old against new", "on the MPC")]


def loop():
    W, H = 1280, 300
    img = canvas(W, H)
    lines = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(lines)
    cy, r = 112, 44
    xs = [128 + i * (W - 256) / 4 for i in range(5)]
    cols = [heat(i / 4) for i in range(5)]
    for i, x in enumerate(xs):
        d.ellipse([(x - r) * S, (cy - r) * S, (x + r) * S, (cy + r) * S], outline=cols[i], width=3 * S)
        if i < 4:                                       # the arrow to the next step
            a, b = x + r + 14, xs[i + 1] - r - 14
            c = mix(cols[i], cols[i + 1], 0.5)
            d.line([(a * S, cy * S), (b * S, cy * S)], fill=c, width=2 * S)
            d.polygon([(b * S, cy * S), ((b - 12) * S, (cy - 7) * S), ((b - 12) * S, (cy + 7) * S)], fill=c)
    # the way back: from the last step under the row to the first
    yb, c = 252, mix(BG, PALE, 0.5)
    d.line([(xs[4] * S, (cy + r + 86) * S), (xs[4] * S, yb * S), (xs[0] * S, yb * S), (xs[0] * S, (cy + r + 92) * S)],
           fill=c, width=2 * S, joint="curve")
    d.polygon([(xs[0] * S, (cy + r + 82) * S), ((xs[0] - 7) * S, (cy + r + 94) * S), ((xs[0] + 7) * S, (cy + r + 94) * S)], fill=c)
    img = glow(img, lines, 7, 0.8)
    d = ImageDraw.Draw(img)
    for i, x in enumerate(xs):
        text(d, (x, cy - 25), str(i + 1), font("Black", 42), (245, 252, 255), 0, "c")
        name, l1, l2 = STEPS[i]
        text(d, (x, cy + r + 16), name, font("Bold", 19), cols[i], 4.0, "c")
        text(d, (x, cy + r + 44), l1, font("Regular", 15), (196, 212, 224), 0.2, "c")
        text(d, (x, cy + r + 63), l2, font("Regular", 15), (196, 212, 224), 0.2, "c")
    text(d, (W / 2, yb + 12), "KEEP WHAT THE DEVICE SHOWS AS FASTER, THEN GO AGAIN", font("Medium", 12), mix(BG, PALE, 0.7), 2.5, "c")
    return img.resize((W, H), Image.Resampling.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    banner().save(os.path.join(OUT, "banner.png"), optimize=True)
    loop().save(os.path.join(OUT, "loop.png"), optimize=True)
    print("wrote banner.png and loop.png to", OUT)


if __name__ == "__main__":
    main()
