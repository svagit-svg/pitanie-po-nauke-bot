import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv

load_dotenv()
from bot.vk_client import html_caption_to_vk_text, post_to_wall

MSK = dt.timezone(dt.timedelta(hours=3))
HOURS = (8, 16)


def main():
    args = sys.argv[1:]
    blizko = "--blizko" in args
    args = [a for a in args if a != "--blizko"]
    start = dt.date.fromisoformat(args[0])
    slugs = args[1:]

    posts_dir = Path("channels/blizko/posts") if blizko else Path("posts")
    creds = {}
    if blizko:
        creds = {
            "group_id": os.environ["BLIZKO_VK_GROUP_ID"],
            "access_token": os.environ["BLIZKO_VK_ACCESS_TOKEN"],
        }

    for i, slug in enumerate(slugs):
        day = start + dt.timedelta(days=i // len(HOURS))
        when = dt.datetime(day.year, day.month, day.day, HOURS[i % len(HOURS)], tzinfo=MSK)
        caption = (posts_dir / f"{slug}_caption.html").read_text(encoding="utf-8")
        result = post_to_wall(html_caption_to_vk_text(caption), publish_date=when.timestamp(), **creds)
        print(f"{slug} -> {when.isoformat()} (post_id {result['post_id']})")


if __name__ == "__main__":
    main()
