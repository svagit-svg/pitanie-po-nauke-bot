import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bot.image_template import FONT_BOLD, FONT_REGULAR
from make_vk_avatar_pitanie import leaf_points

W, H = 1080 * 2, 1920 * 2


def grad(w, h, top, bot):
    g = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return g


def centered(d, text, font, y, fill, shadow=None):
    bb = d.textbbox((0, 0), text, font=font)
    x = (W - (bb[2] - bb[0])) / 2 - bb[0]
    if shadow:
        d.text((x + 6, y + 8), text, font=font, fill=shadow)
    d.text((x, y), text, font=font, fill=fill)
    return bb[3] - bb[1]


def main(out="covers/vk_mobile_cover_pitanie.png"):
    img = grad(W, H, (20, 112, 66), (5, 58, 34)).convert("RGBA")

    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.1, H * 0.08, W * 0.9, H * 0.42], fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.12))
    img = Image.composite(Image.new("RGBA", (W, H), (70, 170, 105, 255)), img, glow)

    wave = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave)
    wd.ellipse([-W * 0.4, H * 0.62, W * 1.4, H * 1.35], fill=(60, 160, 95, 70))
    wd.ellipse([-W * 0.2, H * 0.74, W * 1.6, H * 1.45], fill=(150, 210, 120, 55))
    img = Image.alpha_composite(img, wave)

    cx, cy = W * 0.50, H * 0.215
    big = leaf_points(cx + W * 0.02, cy, W * 0.40, W * 0.115, -45, bend=0.04)
    sm = leaf_points(cx - W * 0.065, cy + W * 0.06, W * 0.23, W * 0.065, -45, bend=0.03)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([(x + 10, y + 18) for x, y in big], fill=(0, 30, 15, 110))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(14)))
    for pts, top, bot in ((big, (190, 232, 140), (110, 190, 100)), (sm, (255, 255, 255), (255, 255, 255))):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(grad(W, H, top, bot).convert("RGBA"), (0, 0), m)
        img = Image.alpha_composite(img, layer)

    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONT_BOLD, 250)
    y = H * 0.335
    for line in ("ПИТАНИЕ", "ПО НАУКЕ"):
        h = centered(d, line, f_title, y, (255, 255, 255), shadow=(0, 40, 20, 90))
        y += 290
    f_tag = ImageFont.truetype(FONT_REGULAR, 100)
    y += 40
    for line in ("Мифы и научные данные", "о еде — без рекламы"):
        centered(d, line, f_tag, y, (232, 244, 228))
        y += 140

    f_item = ImageFont.truetype(FONT_REGULAR, 92)
    items = ["Проверенные источники", "Научные данные", "Практичные советы"]
    y = H * 0.605
    for text in items:
        r = 80
        bb = d.textbbox((0, 0), text, font=f_item)
        total = 2 * r + 50 + (bb[2] - bb[0])
        x0 = (W - total) / 2
        d.ellipse([x0, y, x0 + 2 * r, y + 2 * r], outline=(235, 248, 230, 230), width=7)
        leaf = leaf_points(x0 + r, y + r, 85, 26, -45, bend=0.03, n=60)
        d.polygon(leaf, fill=(235, 248, 230, 255))
        d.text((x0 + 2 * r + 50 - bb[0], y + r - (bb[3] + bb[1]) / 2), text, font=f_item, fill=(255, 255, 255))
        y += 2 * r + 70

    img.convert("RGB").resize((1080, 1920), Image.LANCZOS).save(out)


if __name__ == "__main__":
    main()
