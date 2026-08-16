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


def _fit_headline(draw, text, max_width, max_height, start_size=78, min_size=40):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(FONT_BOLD, size)
        lines = _wrap(draw, text, font, max_width)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.25
        if line_height * len(lines) <= max_height:
            return font, lines, line_height
        size -= 4
    font = ImageFont.truetype(FONT_BOLD, size)
    return font, _wrap(draw, text, font, max_width), draw.textbbox((0, 0), "Ag", font=font)[3] * 1.25


def render_cover(
    question,
    category,
    out_path,
    accent=ACCENT,
    bg_top=BG_TOP,
    bg_bottom=BG_BOTTOM,
    kicker="ПИТАНИЕ ПО НАУКЕ",
):
    img = _vertical_gradient(SIZE, bg_top, bg_bottom)
    draw = ImageDraw.Draw(img)
    content_width = SIZE - 2 * MARGIN

    kicker_font = ImageFont.truetype(FONT_BOLD, 32)
    x = MARGIN
    for ch in kicker:
        draw.text((x, MARGIN), ch, font=kicker_font, fill=accent)
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
    draw.rounded_rectangle(tag_box, radius=(tag_box[3] - tag_box[1]) // 2, fill=accent)
    draw.text((tag_box[0] + pad_x, tag_box[1] + pad_y - 2), tag_text, font=tag_font, fill=(255, 255, 255))

    headline_top = 300
    headline_bottom = 900
    font, lines, line_height = _fit_headline(
        draw, question, content_width, headline_bottom - headline_top
    )
    total_height = line_height * len(lines)
    y = headline_top + (headline_bottom - headline_top - total_height) / 2
    for line in lines:
        draw.text((MARGIN, y), line, font=font, fill=INK)
        y += line_height

    rule_y = 960
    draw.line([(MARGIN, rule_y), (SIZE - MARGIN, rule_y)], fill=accent, width=4)

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


def _rings_image(diameter, color=(248, 246, 240, 255)):
    r = diameter // 2
    sep = int(r * 1.05)
    w, h = 2 * r + sep, 2 * r
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    stroke = max(4, diameter // 16)
    draw.ellipse([0, 0, 2 * r, 2 * r], outline=color, width=stroke)
    draw.ellipse([sep, 0, sep + 2 * r, 2 * r], outline=color, width=stroke)
    return img


def render_avatar_leaf_text(
    out_path,
    size=512,
    accent=ACCENT,
    lines=("ПИТАНИЕ", "ПО НАУКЕ"),
    icon="leaf",
    font_scale=0.10,
):
    dark = tuple(max(0, c - 25) for c in accent)
    img = _vertical_gradient(size, accent, dark).resize((size, size)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(FONT_BOLD, int(size * font_scale))
    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.15

    icon_img = _leaf_image(int(size * 0.22)) if icon == "leaf" else _rings_image(int(size * 0.24))
    gap = int(size * 0.045)
    block_height = icon_img.height + gap + line_height * len(lines)
    top = (size - block_height) / 2

    img.paste(icon_img, ((size - icon_img.width) // 2, int(top)), icon_img)

    y = top + icon_img.height + gap
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


def render_chat_meme(
    messages,
    out_path,
    accent=ACCENT,
    kicker="ПИТАНИЕ ПО НАУКЕ",
    size=SIZE,
):
    bg = (241, 241, 246)
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)

    kicker_font = ImageFont.truetype(FONT_BOLD, 30)
    x = MARGIN
    for ch in kicker:
        draw.text((x, 50), ch, font=kicker_font, fill=accent)
        x += draw.textbbox((0, 0), ch, font=kicker_font)[2] + 5

    tag_font = ImageFont.truetype(FONT_BOLD, 26)
    tag_text = "ПЕРЕПИСКА"
    tag_w = draw.textbbox((0, 0), tag_text, font=tag_font)[2]
    pad_x, pad_y = 20, 11
    tag_box = [
        size - MARGIN - tag_w - 2 * pad_x,
        42,
        size - MARGIN,
        42 + 26 + 2 * pad_y,
    ]
    draw.rounded_rectangle(tag_box, radius=(tag_box[3] - tag_box[1]) // 2, fill=accent)
    draw.text((tag_box[0] + pad_x, tag_box[1] + pad_y - 1), tag_text, font=tag_font, fill=(255, 255, 255))

    draw.line([(MARGIN, 112), (size - MARGIN, 112)], fill=(220, 220, 227), width=2)

    bubble_font = ImageFont.truetype(FONT_REGULAR, 38)
    max_bubble_width = int(size * 0.66)
    pad_x, pad_y = 30, 22
    y = 160

    total_height_needed = sum(
        (len(_wrap(draw, text, bubble_font, max_bubble_width - 2 * pad_x)) *
         draw.textbbox((0, 0), "Ag", font=bubble_font)[3] * 1.3 + 2 * pad_y + 24)
        for text, _ in messages
    )
    if total_height_needed > size - y - MARGIN:
        bubble_font = ImageFont.truetype(FONT_REGULAR, 32)
        pad_x, pad_y = 24, 18

    line_height = draw.textbbox((0, 0), "Ag", font=bubble_font)[3] * 1.3

    for text, sender in messages:
        lines = _wrap(draw, text, bubble_font, max_bubble_width - 2 * pad_x)
        bubble_w = max(draw.textbbox((0, 0), line, font=bubble_font)[2] for line in lines) + 2 * pad_x
        bubble_h = len(lines) * line_height + 2 * pad_y - (line_height - draw.textbbox((0, 0), "Ag", font=bubble_font)[3])

        if sender == "me":
            x1 = size - MARGIN - bubble_w
            fill = accent
            text_color = (255, 255, 255)
        else:
            x1 = MARGIN
            fill = (228, 228, 233)
            text_color = (30, 30, 34)

        draw.rounded_rectangle([x1, y, x1 + bubble_w, y + bubble_h], radius=30, fill=fill)
        ty = y + pad_y - (line_height - draw.textbbox((0, 0), "Ag", font=bubble_font)[3]) / 2
        for line in lines:
            draw.text((x1 + pad_x, ty), line, font=bubble_font, fill=text_color)
            ty += line_height
        y += bubble_h + 24

    img.save(out_path)
    return out_path


def render_expectation_reality(
    expectation,
    reality,
    out_path,
    accent=ACCENT,
    bg_top=BG_TOP,
    bg_bottom=BG_BOTTOM,
    kicker="ПИТАНИЕ ПО НАУКЕ",
    label1="ОЖИДАНИЕ",
    label2="РЕАЛЬНОСТЬ",
    size=SIZE,
):
    img = _vertical_gradient(size, bg_top, bg_bottom)
    draw = ImageDraw.Draw(img)
    content_width = size - 2 * MARGIN

    kicker_font = ImageFont.truetype(FONT_BOLD, 30)
    x = MARGIN
    for ch in kicker:
        draw.text((x, MARGIN), ch, font=kicker_font, fill=accent)
        x += draw.textbbox((0, 0), ch, font=kicker_font)[2] + 5

    mid_y = size // 2
    label_font = ImageFont.truetype(FONT_BOLD, 32)

    draw.text((MARGIN, 200), label1.upper(), font=label_font, fill=accent)
    font1, lines1, lh1 = _fit_headline(draw, expectation, content_width, mid_y - 40 - 260, start_size=58)
    y = 260
    for line in lines1:
        draw.text((MARGIN, y), line, font=font1, fill=INK)
        y += lh1

    draw.line([(MARGIN, mid_y), (size - MARGIN, mid_y)], fill=accent, width=3)

    draw.text((MARGIN, mid_y + 40), label2.upper(), font=label_font, fill=accent)
    font2, lines2, lh2 = _fit_headline(draw, reality, content_width, size - MARGIN - (mid_y + 100), start_size=58)
    y = mid_y + 100
    for line in lines2:
        draw.text((MARGIN, y), line, font=font2, fill=INK)
        y += lh2

    img.save(out_path)
    return out_path


if __name__ == "__main__":
    render_cover(
        question="Правда ли, что яйца повышают холестерин и вредят сердцу?",
        category="Миф или правда?",
        out_path="covers/001_eggs_cholesterol.png",
    )
    print("saved covers/001_eggs_cholesterol.png")
