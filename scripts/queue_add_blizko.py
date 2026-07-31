import json
import sys
from pathlib import Path

QUEUE_PATH = Path(__file__).resolve().parent.parent / "channels" / "blizko" / "queue.json"

if __name__ == "__main__":
    slug = sys.argv[1]
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    queue.append(slug)
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Добавлено в очередь: {slug} (позиция {len(queue)})")
