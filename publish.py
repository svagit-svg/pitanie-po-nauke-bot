import sys
from bot.telegram_client import send_photo, delete_message

if __name__ == "__main__":
    slug = sys.argv[1]
    delete_ids = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else []

    for msg_id in delete_ids:
        delete_message(msg_id)
        print(f"Удалено сообщение {msg_id}")

    with open(f"posts/{slug}_caption.html", encoding="utf-8") as f:
        caption = f.read()

    result = send_photo(f"covers/{slug}.png", caption)
    msg_id = result["result"]["message_id"]
    chat_username = result["result"]["chat"].get("username")
    print(f"Опубликовано: https://t.me/{chat_username}/{msg_id}")
