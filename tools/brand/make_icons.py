#!/usr/bin/env python3
"""Render the BeamPlay launcher icon and Android TV banner (PIL only).

Design: dark night-blue tile, a projector lens on the left emitting a soft light beam,
three AirPlay-style arcs at the end of the beam.  Run from the repo root:
    python3 tools/brand/make_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RES = "app/src/main/res"
BG_TOP, BG_BOT = (16, 24, 48), (6, 10, 22)
BEAM = (255, 214, 120)
ARC = (120, 200, 255)
FONT = "app/src/main/res/font"


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(BG_TOP[i] * (1 - t) + BG_BOT[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def mark(size):
    """The beam+waves mark on a transparent square canvas."""
    s = size
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    # light beam (soft cone)
    beam = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(beam)
    lx, ly = int(s * 0.24), int(s * 0.5)
    d.polygon([(lx, ly - s * 0.07), (int(s * 0.72), int(s * 0.22)),
               (int(s * 0.72), int(s * 0.78)), (lx, ly + s * 0.07)], fill=BEAM + (150,))
    beam = beam.filter(ImageFilter.GaussianBlur(s * 0.035))
    layer.alpha_composite(beam)
    d = ImageDraw.Draw(layer)
    # lens
    r = s * 0.12
    d.ellipse([lx - r, ly - r, lx + r, ly + r], fill=(235, 240, 250, 255))
    r2 = s * 0.075
    d.ellipse([lx - r2, ly - r2, lx + r2, ly + r2], fill=(40, 60, 110, 255))
    r3 = s * 0.03
    d.ellipse([lx - r3 + s * 0.02, ly - r3 - s * 0.02, lx + r3 + s * 0.02, ly + r3 - s * 0.02],
              fill=(255, 255, 255, 220))
    # waves (arcs centred on the lens, at the beam end)
    w = max(2, int(s * 0.035))
    for i, rad in enumerate((0.44, 0.55, 0.66)):
        R = s * rad
        alpha = 255 - i * 55
        d.arc([lx - R, ly - R, lx + R, ly + R], start=-32, end=32, fill=ARC + (alpha,), width=w)
    return layer


def launcher(size):
    big = 1024
    img = gradient(big, big).convert("RGBA")
    img.alpha_composite(mark(big))
    # rounded tile
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big * 0.22), fill=255)
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def banner():
    W, H = 1280, 720
    img = gradient(W, H).convert("RGBA")
    m = mark(520)
    img.alpha_composite(m, (10, (H - 520) // 2))
    d = ImageDraw.Draw(img)
    font_path = next((os.path.join(FONT, f) for f in sorted(os.listdir(FONT))
                      if f.endswith((".ttf", ".otf")) and "bold" in f.lower()), None) \
        or next(os.path.join(FONT, f) for f in os.listdir(FONT) if f.endswith((".ttf", ".otf")))
    size = 170
    while True:  # largest size that fits right of the mark
        f = ImageFont.truetype(font_path, size)
        if d.textlength("BeamPlay", font=f) <= W - 560 - 60:
            break
        size -= 4
    d.text((560, H // 2), "BeamPlay", font=f, fill=(240, 244, 255), anchor="lm")
    return img.convert("RGB").resize((320, 180), Image.LANCZOS)


if __name__ == "__main__":
    for dpi, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        launcher(px).save(f"{RES}/mipmap-{dpi}/ic_launcher.png")
    banner().save(f"{RES}/drawable-nodpi/app_banner.png")
    launcher(512).save("docs/icon.png")
    print("icons written")
