import os
import sys
from pathlib import Path

from bot.telegram_client import edit_caption
from bot.validate import validate_caption

BASE = Path(__file__).resolve().parent / "channels" / "blizko"
BOT_TOKEN = os.environ["BLIZKO_BOT_TOKEN"]
CHANNEL = os.environ["BLIZKO_CHANNEL"]

if __name__ == "__main__":
    slug = sys.argv[1]
    message_id = int(sys.argv[2])
    caption = (BASE / "posts" / f"{slug}_caption.html").read_text(encoding="utf-8")
    validate_caption(caption)
    edit_caption(message_id, caption, chat=CHANNEL, bot_token=BOT_TOKEN)
    print(f"Отредактировано сообщение {message_id}")
