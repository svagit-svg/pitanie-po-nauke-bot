import sys
from bot.telegram_client import edit_caption
from bot.validate import validate_caption

if __name__ == "__main__":
    slug = sys.argv[1]
    message_id = int(sys.argv[2])
    with open(f"posts/{slug}_caption.html", encoding="utf-8") as f:
        caption = f.read()
    validate_caption(caption)
    edit_caption(message_id, caption)
    print(f"Отредактировано сообщение {message_id}")
