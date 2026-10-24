"""Generate one static HTML page per post for GitHub Pages.

VK group tokens cannot upload wall photos, so VK posts attach a link to
these pages instead; VK renders the og:image (the post cover) as a card.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES_BASE = "https://svagit-svg.github.io/pitanie-po-nauke-bot"

CHANNELS = {
    "pitanie": {
        "posts": ROOT / "posts",
        "covers": "covers",
        "name": "Питание по науке",
        "telegram": "https://t.me/pitanie_nauka",
    },
    "blizko": {
        "posts": ROOT / "channels/blizko/posts",
        "covers": "channels/blizko/covers",
        "name": "Близко",
        "telegram": "https://t.me/blizko_love",
    },
}

_TAG = re.compile(r"<[^>]+>")
_TITLE = re.compile(r"<b>(.*?)</b>", re.S)


def card_url(channel, slug):
    return f"{PAGES_BASE}/vk/{channel}/{slug}.html"


def _plain(fragment):
    return html.unescape(_TAG.sub("", fragment)).strip()


def render_card(channel, slug, caption):
    cfg = CHANNELS[channel]
    title_match = _TITLE.search(caption)
    title = _plain(title_match.group(1)) if title_match else cfg["name"]
    paragraphs = [_plain(p) for p in caption.split("\n\n")]
    body = next((p for p in paragraphs[1:] if p and not p.startswith("📚")), "")
    description = body[:200]
    image = f"{PAGES_BASE}/{cfg['covers']}/{slug}.png"
    esc = html.escape
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta property="og:type" content="article">
<meta property="og:site_name" content="{esc(cfg['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{card_url(channel, slug)}">
<style>
body {{ margin: 0; background: #f4f6f3; color: #1d2b22; font: 17px/1.5 -apple-system, "PT Sans", sans-serif; }}
main {{ max-width: 640px; margin: 0 auto; padding: 24px 16px; }}
img {{ width: 100%; border-radius: 12px; }}
a {{ color: #2e6b4a; }}
</style>
</head>
<body>
<main>
<img src="{image}" alt="">
<h1>{esc(title)}</h1>
<p>{esc(body)}</p>
<p><a href="{cfg['telegram']}">Читать «{esc(cfg['name'])}» в Telegram →</a></p>
</main>
</body>
</html>
"""


def main():
    count = 0
    for channel, cfg in CHANNELS.items():
        out_dir = ROOT / "vk" / channel
        out_dir.mkdir(parents=True, exist_ok=True)
        for caption_path in sorted(cfg["posts"].glob("*_caption.html")):
            slug = caption_path.name[: -len("_caption.html")]
            if not (ROOT / cfg["covers"] / f"{slug}.png").exists():
                continue
            caption = caption_path.read_text(encoding="utf-8")
            (out_dir / f"{slug}.html").write_text(render_card(channel, slug, caption), encoding="utf-8")
            count += 1
    (ROOT / ".nojekyll").touch()
    print(f"Generated {count} cards", file=sys.stderr)


if __name__ == "__main__":
    main()
