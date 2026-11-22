import re

from PIL import Image

_TAG_PATTERN = re.compile(r'</?(b|a)(?:\s+href="[^"]*")?>')
_MAX_CAPTION_LENGTH = 1024


def validate_pitanie_cover(photo_path):
    """Keep nutrition post cards in the shared Telegram/Instagram format."""
    with Image.open(photo_path) as image:
        if image.size != (1080, 1350):
            raise ValueError(
                f"Nutrition cover must be 1080 × 1350 (4:5), got {image.size}: "
                f"{photo_path}. Regenerate it with render_cover_pitanie."
            )
        image.verify()


def validate_caption(text):
    stripped = _TAG_PATTERN.sub("", text)
    if "<" in stripped or ">" in stripped:
        idx = stripped.find("<") if "<" in stripped else stripped.find(">")
        snippet = stripped[max(0, idx - 20):idx + 20]
        raise ValueError(
            f"Stray '<' or '>' outside <b>/<a> tags breaks Telegram's HTML parser: ...{snippet}..."
        )
    if len(text) > _MAX_CAPTION_LENGTH:
        raise ValueError(
            f"Caption is {len(text)} chars, over Telegram's {_MAX_CAPTION_LENGTH}-char photo caption limit"
        )
