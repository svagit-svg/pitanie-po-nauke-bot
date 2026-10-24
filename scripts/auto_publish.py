import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.telegram_client import send_photo
from bot.validate import validate_caption
from bot.vk_client import html_caption_to_vk_text, post_to_wall

QUEUE_PATH = Path(__file__).resolve().parent.parent / "queue.json"


def main():
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    if not queue:
        print("::error::Queue is empty — nothing was published. Refill queue.json.")
        sys.exit(1)

    slug = queue.pop(0)
    caption = Path(f"posts/{slug}_caption.html").read_text(encoding="utf-8")
    validate_caption(caption)
    cover_path = f"covers/{slug}.png"

    result = send_photo(cover_path, caption)
    chat_username = result["result"]["chat"].get("username")
    msg_id = result["result"]["message_id"]
    print(f"Опубликовано в Telegram: https://t.me/{chat_username}/{msg_id}")

    try:
        vk_result = post_to_wall(html_caption_to_vk_text(caption), photo_path=cover_path)
        print(f"Опубликовано в VK: post_id {vk_result.get('post_id')}")
    except Exception as exc:
        print(f"::warning::VK publish failed, Telegram post already sent — {exc}")

    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
