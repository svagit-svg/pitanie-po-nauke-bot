import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.telegram_client import send_photo

BASE = Path(__file__).resolve().parent.parent / "channels" / "blizko"
QUEUE_PATH = BASE / "queue.json"
BOT_TOKEN = os.environ["BLIZKO_BOT_TOKEN"]
CHANNEL = os.environ["BLIZKO_CHANNEL"]


def main():
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    if not queue:
        print("Очередь пуста — публиковать нечего")
        return

    slug = queue.pop(0)
    caption = (BASE / "posts" / f"{slug}_caption.html").read_text(encoding="utf-8")

    result = send_photo(str(BASE / "covers" / f"{slug}.png"), caption, chat=CHANNEL, bot_token=BOT_TOKEN)
    chat_username = result["result"]["chat"].get("username")
    msg_id = result["result"]["message_id"]
    print(f"Опубликовано: https://t.me/{chat_username}/{msg_id}")

    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
