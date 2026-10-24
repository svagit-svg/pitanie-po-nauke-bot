import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.image_template import FONT_BOLD

S = 2400


def leaf_points(cx, cy, length, width, angle_deg, bend=0.04, n=120):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    up, down = [], []
    for i in range(n + 1):
        t = i / n
        prof = math.sin(math.pi * t) ** 0.85 * (1 - 0.18 * t)
        x = (t - 0.5) * length
        curve = bend * length * math.sin(math.pi * t)
        up.append((x, -width * prof + curve * -1))
        down.append((x, width * prof * 0.92 + curve * -1))
    pts = up + down[::-1]
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def vertical_gradient_mask(size, top, bottom):
    g = Image.new("RGB", size)
    d = ImageDraw.Draw(g)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        d.line([(0, y), (size[0], y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g


def main(out="covers/vk_avatar_pitanie.png"):
    bg = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(bg)
    top, bot = (20, 112, 66), (6, 66, 38)
    for y in range(S):
        t = y / (S - 1)
        d.line([(0, y), (S, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([S * 0.15, S * 0.02, S * 0.85, S * 0.62], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.12))
    bg = Image.composite(Image.new("RGB", (S, S), (60, 160, 100)), bg, glow)
    img = bg.convert("RGBA")

    cx, cy = S * 0.50, S * 0.31
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    big = leaf_points(cx + S * 0.02, cy, S * 0.50, S * 0.145, -45)
    ImageDraw.Draw(shadow).polygon([(x + S * 0.012, y + S * 0.02) for x, y in big], fill=(0, 30, 15, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(S * 0.015))
    img = Image.alpha_composite(img, shadow)

    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon(big, fill=255)
    grad = vertical_gradient_mask((S, S), (190, 232, 140), (110, 190, 100)).convert("RGBA")
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.paste(grad, (0, 0), mask)
    img = Image.alpha_composite(img, layer)

    small = leaf_points(cx - S * 0.085, cy + S * 0.075, S * 0.29, S * 0.082, -45, bend=0.03)
    m2 = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m2).polygon(small, fill=255)
    white = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    l2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    l2.paste(white, (0, 0), m2)
    img = Image.alpha_composite(img, l2)

    veins = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veins)
    a = math.radians(-45)
    for (px, py, ln, col, wd) in [
        (cx + S * 0.02, cy, S * 0.44, (255, 255, 255, 150), int(S * 0.006)),
        (cx - S * 0.085, cy + S * 0.075, S * 0.25, (90, 170, 110, 200), int(S * 0.005)),
    ]:
        x0, y0 = px - math.cos(a) * ln / 2, py - math.sin(a) * ln / 2
        x1, y1 = px + math.cos(a) * ln / 2, py + math.sin(a) * ln / 2
        vd.line([(x0, y0), (x1, y1)], fill=col, width=wd)
    img = Image.alpha_composite(img, veins)

    od = ImageDraw.Draw(img)

    f = ImageFont.truetype(FONT_BOLD, int(S * 0.10))
    y = S * 0.605
    td = ImageDraw.Draw(img)
    for line in ("ПИТАНИЕ", "ПО НАУКЕ"):
        bb = td.textbbox((0, 0), line, font=f)
        w = bb[2] - bb[0]
        x = (S - w) / 2 - bb[0]
        td.text((x + S * 0.004, y + S * 0.006), line, font=f, fill=(0, 40, 20, 70))
        td.text((x, y), line, font=f, fill=(255, 255, 255, 255))
        y += S * 0.125

    ring = S * 0.045
    td.ellipse([ring, ring, S - ring, S - ring], outline=(255, 255, 255, 110), width=int(S * 0.003))
    img.convert("RGB").resize((1024, 1024), Image.LANCZOS).save(out)


if __name__ == "__main__":
    main()
