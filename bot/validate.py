import re

_TAG_PATTERN = re.compile(r'</?(b|a)(?:\s+href="[^"]*")?>')
_MAX_CAPTION_LENGTH = 1024


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
