import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def get_me():
    resp = requests.get(f"{API_BASE}/getMe", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_chat(chat=CHANNEL):
    resp = requests.get(f"{API_BASE}/getChat", params={"chat_id": chat}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_message(text, chat=CHANNEL, parse_mode="HTML", disable_preview=True, reply_to=None):
    data = {
        "chat_id": chat,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_preview,
    }
    if reply_to:
        data["reply_to_message_id"] = reply_to
    resp = requests.post(f"{API_BASE}/sendMessage", data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_photo(photo_path, caption, chat=CHANNEL, parse_mode="HTML", reply_to=None):
    data = {"chat_id": chat, "caption": caption, "parse_mode": parse_mode}
    if reply_to:
        data["reply_to_message_id"] = reply_to
    with open(photo_path, "rb") as photo:
        resp = requests.post(
            f"{API_BASE}/sendPhoto",
            data=data,
            files={"photo": photo},
            timeout=30,
        )
    resp.raise_for_status()
    return resp.json()


def edit_caption(message_id, caption, chat=CHANNEL, parse_mode="HTML"):
    resp = requests.post(
        f"{API_BASE}/editMessageCaption",
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


def set_chat_photo(photo_path, chat=CHANNEL):
    with open(photo_path, "rb") as photo:
        resp = requests.post(
            f"{API_BASE}/setChatPhoto",
            data={"chat_id": chat},
            files={"photo": photo},
            timeout=30,
        )
    resp.raise_for_status()
    return resp.json()


def delete_message(message_id, chat=CHANNEL):
    resp = requests.post(
        f"{API_BASE}/deleteMessage",
        data={"chat_id": chat, "message_id": message_id},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
