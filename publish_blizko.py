import os
import sys
from pathlib import Path

from bot.telegram_client import send_photo, delete_message

BASE = Path(__file__).resolve().parent / "channels" / "blizko"
BOT_TOKEN = os.environ["BLIZKO_BOT_TOKEN"]
CHANNEL = os.environ["BLIZKO_CHANNEL"]

if __name__ == "__main__":
    slug = sys.argv[1]
    delete_ids = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else []

    for msg_id in delete_ids:
        delete_message(msg_id, chat=CHANNEL, bot_token=BOT_TOKEN)
        print(f"Удалено сообщение {msg_id}")

    caption = (BASE / "posts" / f"{slug}_caption.html").read_text(encoding="utf-8")
    result = send_photo(str(BASE / "covers" / f"{slug}.png"), caption, chat=CHANNEL, bot_token=BOT_TOKEN)
    msg_id = result["result"]["message_id"]
    chat_username = result["result"]["chat"].get("username")
    print(f"Опубликовано: https://t.me/{chat_username}/{msg_id}")
