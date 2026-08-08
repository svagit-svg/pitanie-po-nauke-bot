import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.telegram_client import send_photo
from bot.validate import validate_caption

QUEUE_PATH = Path(__file__).resolve().parent.parent / "queue.json"


def main():
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    if not queue:
        print("::error::Queue is empty — nothing was published. Refill queue.json.")
        sys.exit(1)

    slug = queue.pop(0)
    caption = Path(f"posts/{slug}_caption.html").read_text(encoding="utf-8")
    validate_caption(caption)

    result = send_photo(f"covers/{slug}.png", caption)
    chat_username = result["result"]["chat"].get("username")
    msg_id = result["result"]["message_id"]
    print(f"Опубликовано: https://t.me/{chat_username}/{msg_id}")

    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
