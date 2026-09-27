import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

VK_API_VERSION = "5.199"
VK_API_BASE = "https://api.vk.com/method"

ACCESS_TOKEN = os.environ.get("VK_ACCESS_TOKEN")
GROUP_ID = os.environ.get("VK_GROUP_ID")

_LINK_PATTERN = re.compile(r'<a href="([^"]*)">([^<]*)</a>')
_BOLD_PATTERN = re.compile(r"</?b>")


def html_caption_to_vk_text(caption):
    text = _LINK_PATTERN.sub(r"\2: \1", caption)
    text = _BOLD_PATTERN.sub("", text)
    return text


def _call(method, access_token=None, **params):
    token = access_token or ACCESS_TOKEN
    if not token:
        raise RuntimeError("No VK access token: pass access_token= or set VK_ACCESS_TOKEN")
    params["access_token"] = token
    params["v"] = VK_API_VERSION
    resp = requests.post(f"{VK_API_BASE}/{method}", data=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"VK API error in {method}: {data['error']}")
    return data["response"]


def upload_wall_photo(photo_path, group_id=None, access_token=None):
    gid = group_id or GROUP_ID
    if not gid:
        raise RuntimeError("No VK group id: pass group_id= or set VK_GROUP_ID")

    upload_server = _call("photos.getWallUploadServer", access_token=access_token, group_id=gid)
    with open(photo_path, "rb") as photo:
        resp = requests.post(upload_server["upload_url"], files={"photo": photo}, timeout=120)
    resp.raise_for_status()
    uploaded = resp.json()

    saved = _call(
        "photos.saveWallPhoto",
        access_token=access_token,
        group_id=gid,
        photo=uploaded["photo"],
        server=uploaded["server"],
        hash=uploaded["hash"],
    )
    photo_obj = saved[0]
    return f"photo{photo_obj['owner_id']}_{photo_obj['id']}"


def post_to_wall(message, photo_path=None, group_id=None, access_token=None, from_group=1):
    gid = group_id or GROUP_ID
    if not gid:
        raise RuntimeError("No VK group id: pass group_id= or set VK_GROUP_ID")

    params = {"owner_id": f"-{gid}", "from_group": from_group, "message": message}
    if photo_path:
        params["attachment"] = upload_wall_photo(photo_path, group_id=gid, access_token=access_token)

    return _call("wall.post", access_token=access_token, **params)
