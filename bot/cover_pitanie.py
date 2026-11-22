"""Post cards for «Питание по науке» in the VK community brand style:
deep green gradient with a glow, the two-leaf mark and soft hills."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.image_template import FONT_BOLD, _wrap
from scripts.make_vk_avatar_pitanie import leaf_points

OUT_WIDTH = 1080
OUT_HEIGHT = 1350
WIDTH = OUT_WIDTH * 2
HEIGHT = OUT_HEIGHT * 2
M = 240

TOP = (20, 112, 66)
BOTTOM = (5, 58, 34)
GLOW = (70, 170, 105)
LEAF_TOP = (190, 232, 140)
LEAF_BOTTOM = (110, 190, 100)
WHITE = (255, 255, 255)


def _gradient(top, bottom):
    g = Image.new("RGB", (WIDTH, HEIGHT))
    d = ImageDraw.Draw(g)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        d.line([(0, y), (WIDTH, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g


def _paint_leaf(img, pts, top, bottom, alpha=255):
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=alpha)
    layer = _gradient(top, bottom).convert("RGBA")
    layer.putalpha(mask)
    return Image.alpha_composite(img, layer)


def _fit(draw, text, max_w, max_h, start=200, stop=64):
    for size in range(start, stop - 1, -4):
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = _wrap(draw, text, font, max_w)
        line_h = int(size * 1.18)
        if line_h * len(lines) <= max_h and all(
            draw.textlength(line, font=font) <= max_w for line in lines
        ):
            return font, lines, line_h
    raise ValueError("Cover title is too long to fit within the safe area")


def render_cover_pitanie(question, category, out_path):
    """Render a 4:5 card with text inside the central square and 3:4 crops."""
    img = _gradient(TOP, BOTTOM).convert("RGBA")

    glow = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(glow).ellipse([WIDTH * 0.35, -HEIGHT * 0.25, WIDTH * 1.25, HEIGHT * 0.55], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(WIDTH * 0.13))
    img = Image.composite(Image.new("RGBA", (WIDTH, HEIGHT), GLOW + (255,)), img, glow)

    hills = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hills)
    hd.ellipse([-WIDTH * 0.5, HEIGHT * 0.80, WIDTH * 1.1, HEIGHT * 1.45], fill=(60, 160, 95, 70))
    hd.ellipse([WIDTH * 0.1, HEIGHT * 0.86, WIDTH * 1.7, HEIGHT * 1.5], fill=(150, 210, 120, 50))
    img = Image.alpha_composite(img, hills)

    # Large translucent leaf bleeding off the bottom-right corner.
    deco = leaf_points(WIDTH * 0.84, HEIGHT * 0.78, WIDTH * 0.66, WIDTH * 0.19, -45, bend=0.04)
    img = _paint_leaf(img, deco, LEAF_TOP, LEAF_BOTTOM, alpha=55)

    # Brand mark: the two-leaf logo next to the channel name.
    # Keep the logo below the top edge of a centered square preview.
    mx, my = M + 46, 470
    big = leaf_points(mx + 6, my - 4, 120, 34, -45, bend=0.04, n=80)
    small = leaf_points(mx - 20, my + 16, 70, 20, -45, bend=0.03, n=60)
    img = _paint_leaf(img, big, LEAF_TOP, LEAF_BOTTOM)
    img = _paint_leaf(img, small, WHITE, WHITE)

    d = ImageDraw.Draw(img)
    kicker = ImageFont.truetype(FONT_BOLD, 48)
    x = M + 120
    for ch in "ПИТАНИЕ ПО НАУКЕ":
        d.text((x, my - 34), ch, font=kicker, fill=WHITE)
        x += d.textlength(ch, font=kicker) + 5

    tag_font = ImageFont.truetype(FONT_BOLD, 48)
    tag = category.upper()
    bb = d.textbbox((0, 0), tag, font=tag_font)
    pad_x, pad_y = 44, 26
    box_h = (bb[3] - bb[1]) + 2 * pad_y
    gap = 60

    area_top, area_bottom = 820, 2180
    font, lines, line_h = _fit(d, question, WIDTH - 2 * M, area_bottom - area_top - box_h - gap)
    block_h = box_h + gap + line_h * len(lines)
    y0 = area_top + (area_bottom - area_top - block_h) / 2

    box = [M, y0, M + (bb[2] - bb[0]) + 2 * pad_x, y0 + box_h]
    d.rounded_rectangle(box, radius=box_h // 2, fill=LEAF_TOP)
    d.text((box[0] + pad_x - bb[0], box[1] + pad_y - bb[1]), tag, font=tag_font, fill=BOTTOM)

    y = y0 + box_h + gap
    for line in lines:
        d.text((M + 5, y + 8), line, font=font, fill=(0, 40, 20, 110), anchor="lt")
        d.text((M, y), line, font=font, fill=WHITE, anchor="lt")
        y += line_h

    result = img.convert("RGB").resize((OUT_WIDTH, OUT_HEIGHT), Image.LANCZOS)
    if Path(out_path).suffix.lower() in {".jpg", ".jpeg"}:
        result.save(out_path, quality=95, subsampling=0, optimize=True)
    else:
        result.save(out_path)
    return out_path
