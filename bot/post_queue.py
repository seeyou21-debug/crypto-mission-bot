"""queue/*.json (Claude가 작성한 요약)을 텔레그램에 올리고 sent/로 옮김.
파일 형식: {"topic": "macro", "text": "<b>HTML</b> 본문"}"""
import json
import shutil
import traceback

from config import TOPICS
from common import ROOT, send

if __name__ == "__main__":
    for f in sorted((ROOT / "queue").glob("*.json")):
        try:
            item = json.loads(f.read_text(encoding="utf-8"))
            topic = item.get("topic") if item.get("topic") in TOPICS else "brief"
            send(topic, item["text"])
            shutil.move(str(f), ROOT / "sent" / f.name)
            print("posted", f.name)
        except Exception:
            traceback.print_exc()
