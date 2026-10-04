import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.vk_client import html_caption_to_vk_text, post_to_wall

MSK = dt.timezone(dt.timedelta(hours=3))
HOURS = (8, 16)


def main():
    start = dt.date.fromisoformat(sys.argv[1])
    slugs = sys.argv[2:]
    for i, slug in enumerate(slugs):
        day = start + dt.timedelta(days=i // len(HOURS))
        when = dt.datetime(day.year, day.month, day.day, HOURS[i % len(HOURS)], tzinfo=MSK)
        caption = Path(f"posts/{slug}_caption.html").read_text(encoding="utf-8")
        result = post_to_wall(html_caption_to_vk_text(caption), publish_date=when.timestamp())
        print(f"{slug} -> {when.isoformat()} (post_id {result['post_id']})")


if __name__ == "__main__":
    main()
