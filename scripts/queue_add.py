import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bot.validate import validate_caption, validate_pitanie_cover

BASE = Path(__file__).resolve().parent.parent
QUEUE_PATH = BASE / "queue.json"

if __name__ == "__main__":
    slug = sys.argv[1]
    caption = (BASE / "posts" / f"{slug}_caption.html").read_text(encoding="utf-8")
    validate_caption(caption)
    validate_pitanie_cover(BASE / "covers" / f"{slug}.png")

    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    queue.append(slug)
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Добавлено в очередь: {slug} (позиция {len(queue)})")
