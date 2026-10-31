"""Post cards for «Питание по науке» in the VK community brand style:
deep green gradient with a glow, the two-leaf mark and soft hills."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.image_template import FONT_BOLD, FONT_REGULAR, _wrap
from scripts.make_vk_avatar_pitanie import leaf_points

OUT_SIZE = 1080
S = OUT_SIZE * 2
M = 180

TOP = (20, 112, 66)
BOTTOM = (5, 58, 34)
GLOW = (70, 170, 105)
LEAF_TOP = (190, 232, 140)
LEAF_BOTTOM = (110, 190, 100)
WHITE = (255, 255, 255)
SOFT = (232, 244, 228)


def _gradient(top, bottom):
    g = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(g)
    for y in range(S):
        t = y / (S - 1)
        d.line([(0, y), (S, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g


def _paint_leaf(img, pts, top, bottom, alpha=255):
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=alpha)
    layer = _gradient(top, bottom).convert("RGBA")
    layer.putalpha(mask)
    return Image.alpha_composite(img, layer)


def _fit(draw, text, max_w, max_h, start=200, stop=100):
    for size in range(start, stop - 1, -4):
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = _wrap(draw, text, font, max_w)
        line_h = int(size * 1.18)
        if line_h * len(lines) <= max_h:
            return font, lines, line_h
    font = ImageFont.truetype(FONT_BOLD, stop)
    return font, _wrap(draw, text, font, max_w), int(stop * 1.18)


def render_cover_pitanie(question, category, out_path):
    img = _gradient(TOP, BOTTOM).convert("RGBA")

    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([S * 0.35, -S * 0.25, S * 1.25, S * 0.55], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.13))
    img = Image.composite(Image.new("RGBA", (S, S), GLOW + (255,)), img, glow)

    hills = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hills)
    hd.ellipse([-S * 0.5, S * 0.80, S * 1.1, S * 1.45], fill=(60, 160, 95, 70))
    hd.ellipse([S * 0.1, S * 0.86, S * 1.7, S * 1.5], fill=(150, 210, 120, 50))
    img = Image.alpha_composite(img, hills)

    # Large translucent leaf bleeding off the bottom-right corner.
    deco = leaf_points(S * 0.84, S * 0.78, S * 0.66, S * 0.19, -45, bend=0.04)
    img = _paint_leaf(img, deco, LEAF_TOP, LEAF_BOTTOM, alpha=55)

    # Brand mark: the two-leaf logo next to the channel name.
    mx, my = M + 46, M + 40
    big = leaf_points(mx + 6, my - 4, 120, 34, -45, bend=0.04, n=80)
    small = leaf_points(mx - 20, my + 16, 70, 20, -45, bend=0.03, n=60)
    img = _paint_leaf(img, big, LEAF_TOP, LEAF_BOTTOM)
    img = _paint_leaf(img, small, WHITE, WHITE)

    d = ImageDraw.Draw(img)
    kicker = ImageFont.truetype(FONT_BOLD, 58)
    x = M + 120
    for ch in "ПИТАНИЕ ПО НАУКЕ":
        d.text((x, my - 34), ch, font=kicker, fill=WHITE)
        x += d.textbbox((0, 0), ch, font=kicker)[2] + 9

    tag_font = ImageFont.truetype(FONT_BOLD, 54)
    tag = category.upper()
    bb = d.textbbox((0, 0), tag, font=tag_font)
    pad_x, pad_y = 44, 26
    box_h = (bb[3] - bb[1]) + 2 * pad_y
    gap = 60

    area_top, area_bottom = S * 0.17, S * 0.80
    font, lines, line_h = _fit(d, question, S - 2 * M - 60, area_bottom - area_top - box_h - gap)
    block_h = box_h + gap + line_h * len(lines)
    y0 = area_top + (area_bottom - area_top - block_h) / 2

    box = [M, y0, M + (bb[2] - bb[0]) + 2 * pad_x, y0 + box_h]
    d.rounded_rectangle(box, radius=box_h // 2, fill=LEAF_TOP)
    d.text((box[0] + pad_x - bb[0], box[1] + pad_y - bb[1]), tag, font=tag_font, fill=BOTTOM)

    y = y0 + box_h + gap
    for line in lines:
        d.text((M + 5, y + 8), line, font=font, fill=(0, 40, 20, 110))
        d.text((M, y), line, font=font, fill=WHITE)
        y += line_h

    foot = ImageFont.truetype(FONT_REGULAR, 50)
    d.line([(M, S * 0.86), (M + 120, S * 0.86)], fill=LEAF_TOP, width=8)
    footer = {"Практика": "Идеи на каждый день", "С улыбкой": "Немного юмора"}.get(category, "Разбор с источниками")
    d.text((M, S * 0.875), footer, font=foot, fill=SOFT)

    img.convert("RGB").resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS).save(out_path)
    return out_path
