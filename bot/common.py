import calendar
import html
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
TOPICS_FILE = ROOT / "topics.json"
STATE_FILE = ROOT / "state.json"
KST = timezone(timedelta(hours=9))
UA = {"User-Agent": "Mozilla/5.0 (crypto-mission-bot)"}
DRY_RUN = os.environ.get("DRY_RUN") == "1"


def esc(s):
    return html.escape(str(s), quote=False)


def now_kst():
    return datetime.now(KST)


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- Telegram ----------

def tg(method, **params):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    r = requests.post(f"https://api.telegram.org/bot{token}/{method}", json=params, timeout=30)
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram {method} 실패: {data.get('description')}")
    return data["result"]


def send(topic_key, text):
    """토픽에 HTML 메시지 전송. 4096자 넘으면 나눠 보냄."""
    if DRY_RUN:
        print(f"\n===== [DRY RUN → {topic_key}] =====\n{text}\n")
        return
    topics = load_json(TOPICS_FILE, {})
    chat_id = topics.get("chat_id")
    if not chat_id:
        raise RuntimeError("topics.json 없음 — 먼저 'Setup room' 워크플로를 실행하세요.")
    thread_id = topics.get("topics", {}).get(topic_key)
    chunks, buf = [], ""
    for line in text.split("\n"):
        if len(buf) + len(line) + 1 > 3900:
            chunks.append(buf)
            buf = ""
        buf += line + "\n"
    chunks.append(buf)
    for c in chunks:
        params = dict(chat_id=chat_id, text=c.strip(), parse_mode="HTML",
                      disable_web_page_preview=True)
        if thread_id:
            params["message_thread_id"] = thread_id
        tg("sendMessage", **params)
        time.sleep(1)


# ---------- 시장 데이터 ----------

def coingecko_markets(ids):
    r = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params=dict(vs_currency="usd", ids=",".join(ids),
                    price_change_percentage="1h,24h,7d"),
        headers=UA, timeout=30)
    r.raise_for_status()
    return {c["id"]: c for c in r.json()}


def fear_greed():
    r = requests.get("https://api.alternative.me/fng/?limit=2", headers=UA, timeout=30)
    r.raise_for_status()
    d = r.json()["data"]
    return int(d[0]["value"]), d[0]["value_classification"], int(d[1]["value"])


FNG_KO = {"Extreme Fear": "극단적 공포", "Fear": "공포", "Neutral": "중립",
          "Greed": "탐욕", "Extreme Greed": "극단적 탐욕"}


def yahoo_quote(symbol):
    """마지막 종가와 전일 대비 변동률."""
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                     params=dict(range="5d", interval="1d"), headers=UA, timeout=30)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
    last, prev = closes[-1], closes[-2]
    return last, (last / prev - 1) * 100


def upbit_prices(markets):
    r = requests.get("https://api.upbit.com/v1/ticker", params={"markets": ",".join(markets)},
                     headers=UA, timeout=30)
    r.raise_for_status()
    return {t["market"]: t["trade_price"] for t in r.json()}


def fetch_news(feeds, hours=24):
    import feedparser
    cutoff = time.time() - hours * 3600
    items, seen = [], set()
    for url in feeds:
        try:
            f = feedparser.parse(url, agent=UA["User-Agent"])
        except Exception as e:  # 피드 하나 실패해도 계속
            print("feed error", url, e)
            continue
        for e in f.entries:
            t = e.get("published_parsed") or e.get("updated_parsed")
            ts = calendar.timegm(t) if t else time.time()
            title = e.get("title", "").strip()
            key = title.lower()[:80]
            if ts < cutoff or not title or key in seen:
                continue
            seen.add(key)
            src = e.get("source", {}).get("title") if e.get("source") else f.feed.get("title", "")
            items.append(dict(title=title, link=e.get("link", ""), ts=ts, source=src or ""))
    items.sort(key=lambda x: x["ts"], reverse=True)
    return items


def pct(v, digits=1):
    if v is None:
        return "-"
    arrow = "🔺" if v > 0 else ("🔻" if v < 0 else "▪️")
    return f"{arrow}{v:+.{digits}f}%"
