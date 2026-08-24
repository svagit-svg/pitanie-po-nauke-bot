import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MIN_ITEMS = 4  # 2 days of runway at 2 posts/day

QUEUES = {
    "pitanie": BASE / "queue.json",
    "blizko": BASE / "channels" / "blizko" / "queue.json",
}


def main():
    low = []
    for name, path in QUEUES.items():
        count = len(json.loads(path.read_text(encoding="utf-8")))
        print(f"{name}: {count} posts queued")
        if count < MIN_ITEMS:
            low.append(f"{name} ({count} left)")

    if low:
        print(f"::error::Queue running low: {', '.join(low)}. Refill soon.")
        sys.exit(1)


if __name__ == "__main__":
    main()
