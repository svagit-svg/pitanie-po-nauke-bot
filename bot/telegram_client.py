import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL")


def _api_base(bot_token=None):
    token = bot_token or BOT_TOKEN
    if not token:
        raise RuntimeError("No bot token: pass bot_token= or set TELEGRAM_BOT_TOKEN")
    return f"https://api.telegram.org/bot{token}"


def get_me(bot_token=None):
    resp = requests.get(f"{_api_base(bot_token)}/getMe", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_chat(chat=CHANNEL, bot_token=None):
    resp = requests.get(f"{_api_base(bot_token)}/getChat", params={"chat_id": chat}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_message(text, chat=CHANNEL, parse_mode="HTML", disable_preview=True, reply_to=None, bot_token=None):
    data = {
        "chat_id": chat,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_preview,
    }
    if reply_to:
        data["reply_to_message_id"] = reply_to
    resp = requests.post(f"{_api_base(bot_token)}/sendMessage", data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_photo(photo_path, caption, chat=CHANNEL, parse_mode="HTML", reply_to=None, bot_token=None):
    data = {"chat_id": chat, "caption": caption, "parse_mode": parse_mode}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    with open(photo_path, "rb") as photo:
        resp = requests.post(
            f"{_api_base(bot_token)}/sendPhoto",
            data=data,
            files={"photo": photo},
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()


def edit_caption(message_id, caption, chat=CHANNEL, parse_mode="HTML", bot_token=None):
    resp = requests.post(
        f"{_api_base(bot_token)}/editMessageCaption",
        data={
            "chat_id": chat,
            "message_id": message_id,
            "caption": caption,
            "parse_mode": parse_mode,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def set_chat_photo(photo_path, chat=CHANNEL, bot_token=None):
    with open(photo_path, "rb") as photo:
        resp = requests.post(
            f"{_api_base(bot_token)}/setChatPhoto",
            data={"chat_id": chat},
            files={"photo": photo},
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()


def delete_message(message_id, chat=CHANNEL, bot_token=None):
    resp = requests.post(
        f"{_api_base(bot_token)}/deleteMessage",
        data={"chat_id": chat, "message_id": message_id},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
