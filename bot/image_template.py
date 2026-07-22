import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

SIZE = 1080
MARGIN = 90

BG_TOP = (248, 246, 240)
BG_BOTTOM = (232, 240, 233)
ACCENT = (39, 111, 79)
INK = (23, 33, 26)
MUTED = (99, 112, 103)

_FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
FONT_BOLD = os.path.join(_FONTS_DIR, "PTSans-Bold.ttf")
FONT_REGULAR = os.path.join(_FONTS_DIR, "PTSans-Regular.ttf")


def _vertical_gradient(size, top, bottom):
    img = Image.new("RGB", (size, size), top)
    draw = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (size, y)], fill=color)
    return img


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_headline(draw, text, max_width, max_height):
    size = 78
    while size > 40:
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = _wrap(draw, text, font, max_width)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.25
        if line_height * len(lines) <= max_height:
            return font, lines, line_height
        size -= 4
    font = ImageFont.truetype(FONT_BOLD, size)
    return font, _wrap(draw, text, font, max_width), draw.textbbox((0, 0), "Ag", font=font)[3] * 1.25


def render_cover(question, category, evidence, out_path):
    img = _vertical_gradient(SIZE, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    content_width = SIZE - 2 * MARGIN

    kicker_font = ImageFont.truetype(FONT_BOLD, 32)
    kicker = "ПИТАНИЕ ПО НАУКЕ"
    x = MARGIN
    for ch in kicker:
        draw.text((x, MARGIN), ch, font=kicker_font, fill=ACCENT)
        x += draw.textbbox((0, 0), ch, font=kicker_font)[2] + 6

    tag_font = ImageFont.truetype(FONT_BOLD, 30)
    tag_text = category.upper()
    tag_w = draw.textbbox((0, 0), tag_text, font=tag_font)[2]
    pad_x, pad_y = 26, 14
    tag_box = [
        SIZE - MARGIN - tag_w - 2 * pad_x,
        MARGIN - 8,
        SIZE - MARGIN,
        MARGIN - 8 + 30 + 2 * pad_y,
    ]
    draw.rounded_rectangle(tag_box, radius=(tag_box[3] - tag_box[1]) // 2, fill=ACCENT)
    draw.text((tag_box[0] + pad_x, tag_box[1] + pad_y - 2), tag_text, font=tag_font, fill=(255, 255, 255))

    headline_top = 300
    headline_bottom = 820
    font, lines, line_height = _fit_headline(
        draw, question, content_width, headline_bottom - headline_top
    )
    total_height = line_height * len(lines)
    y = headline_top + (headline_bottom - headline_top - total_height) / 2
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=INK)
        y += line_height

    rule_y = 900
    draw.line([(MARGIN, rule_y), (SIZE - MARGIN, rule_y)], fill=ACCENT, width=4)

    evidence_font = ImageFont.truetype(FONT_REGULAR, 30)
    draw.text((MARGIN, rule_y + 30), f"Уровень доказательности: {evidence}", font=evidence_font, fill=MUTED)

    img.save(out_path)
    return out_path


def render_avatar(out_path, monogram="ПН", size=512):
    dark = tuple(max(0, c - 25) for c in ACCENT)
    img = _vertical_gradient(size, ACCENT, dark).resize((size, size))
    draw = ImageDraw.Draw(img)

    font_size = int(size * 0.4)
    font = ImageFont.truetype(FONT_BOLD, font_size)
    bbox = draw.textbbox((0, 0), monogram, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
        monogram,
        font=font,
        fill=(248, 246, 240),
    )

    ring_margin = int(size * 0.08)
    draw.ellipse(
        [ring_margin, ring_margin, size - ring_margin, size - ring_margin],
        outline=(248, 246, 240),
        width=max(2, size // 128),
    )

    img.save(out_path)
    return out_path


def render_avatar_text(out_path, size=512):
    dark = tuple(max(0, c - 25) for c in ACCENT)
    img = _vertical_gradient(size, ACCENT, dark).resize((size, size))
    draw = ImageDraw.Draw(img)

    lines = ["ПИТАНИЕ", "ПО НАУКЕ"]
    font = ImageFont.truetype(FONT_BOLD, int(size * 0.135))
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.15
    y = (size - line_height * len(lines)) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((size - w) / 2 - bbox[0], y), line, font=font, fill=(248, 246, 240))
        y += line_height

    ring_margin = int(size * 0.08)
    draw.ellipse(
        [ring_margin, ring_margin, size - ring_margin, size - ring_margin],
        outline=(248, 246, 240),
        width=max(2, size // 128),
    )
    img.save(out_path)
    return out_path


def render_avatar_leaf(out_path, size=512):
    dark = tuple(max(0, c - 25) for c in ACCENT)
    img = _vertical_gradient(size, ACCENT, dark).resize((size, size)).convert("RGBA")

    diameter = int(size * 0.42)
    offset = int(diameter * 0.55)
    w = diameter + offset
    mask1 = Image.new("L", (w, diameter), 0)
    ImageDraw.Draw(mask1).ellipse([0, 0, diameter, diameter], fill=255)
    mask2 = Image.new("L", (w, diameter), 0)
    ImageDraw.Draw(mask2).ellipse([offset, 0, offset + diameter, diameter], fill=255)
    leaf_mask = ImageChops.darker(mask1, mask2)

    leaf = Image.new("RGBA", (w, diameter), (0, 0, 0, 0))
    leaf.paste((248, 246, 240, 255), (0, 0), leaf_mask)
    leaf = leaf.rotate(-45, expand=True, resample=Image.BICUBIC)

    lx = (size - leaf.width) // 2
    ly = (size - leaf.height) // 2 - int(size * 0.03)
    img.paste(leaf, (lx, ly), leaf)

    draw = ImageDraw.Draw(img)
    ring_margin = int(size * 0.08)
    draw.ellipse(
        [ring_margin, ring_margin, size - ring_margin, size - ring_margin],
        outline=(248, 246, 240),
        width=max(2, size // 128),
    )
    img.convert("RGB").save(out_path)
    return out_path


def _leaf_image(diameter, color=(248, 246, 240, 255)):
    offset = int(diameter * 0.55)
    w = diameter + offset
    mask1 = Image.new("L", (w, diameter), 0)
    ImageDraw.Draw(mask1).ellipse([0, 0, diameter, diameter], fill=255)
    mask2 = Image.new("L", (w, diameter), 0)
    ImageDraw.Draw(mask2).ellipse([offset, 0, offset + diameter, diameter], fill=255)
    leaf_mask = ImageChops.darker(mask1, mask2)
    leaf = Image.new("RGBA", (w, diameter), (0, 0, 0, 0))
    leaf.paste(color, (0, 0), leaf_mask)
    return leaf.rotate(-45, expand=True, resample=Image.BICUBIC)


def render_avatar_leaf_text(out_path, size=512):
    dark = tuple(max(0, c - 25) for c in ACCENT)
    img = _vertical_gradient(size, ACCENT, dark).resize((size, size)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    lines = ["ПИТАНИЕ", "ПО НАУКЕ"]
    font = ImageFont.truetype(FONT_BOLD, int(size * 0.10))
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.15

    leaf = _leaf_image(int(size * 0.22))
    gap = int(size * 0.045)
    block_height = leaf.height + gap + line_height * len(lines)
    top = (size - block_height) / 2

    img.paste(leaf, ((size - leaf.width) // 2, int(top)), leaf)

    y = top + leaf.height + gap
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((size - w) / 2 - bbox[0], y), line, font=font, fill=(248, 246, 240))
        y += line_height

    ring_margin = int(size * 0.08)
    draw.ellipse(
        [ring_margin, ring_margin, size - ring_margin, size - ring_margin],
        outline=(248, 246, 240),
        width=max(2, size // 128),
    )
    img.convert("RGB").save(out_path)
    return out_path


def render_avatar_light(out_path, monogram="ПН", size=512):
    img = Image.new("RGB", (size, size), BG_TOP)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(FONT_BOLD, int(size * 0.4))
    bbox = draw.textbbox((0, 0), monogram, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), monogram, font=font, fill=ACCENT)

    ring_margin = int(size * 0.08)
    draw.ellipse(
        [ring_margin, ring_margin, size - ring_margin, size - ring_margin],
        outline=ACCENT,
        width=max(2, size // 128),
    )
    img.save(out_path)
    return out_path


if __name__ == "__main__":
    render_cover(
        question="Правда ли, что яйца повышают холестерин и вредят сердцу?",
        category="Миф или правда?",
        evidence="высокий",
        out_path="covers/001_eggs_cholesterol.png",
    )
    print("saved covers/001_eggs_cholesterol.png")
