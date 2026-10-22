"""15분마다: 가격 급변 + 키워드 뉴스 속보. 중복 방지 상태는 state.json에 저장."""
import hashlib
import time
import traceback

from config import COINS, ALERT_1H, ALERT_COOLDOWN_MIN, FEEDS, KEYWORD_ROUTES, \
    MAX_NEWS_ALERTS_PER_RUN, DISCLAIMER
from common import (STATE_FILE, load_json, save_json, esc, now_kst, coingecko_markets,
                    fetch_news, send)


def price_alerts(state):
    mk = coingecko_markets([c[0] for c in COINS])
    last = state.setdefault("price_alert", {})
    for cid, sym, _ in COINS:
        c = mk.get(cid)
        if not c:
            continue
        ch = c.get("price_change_percentage_1h_in_currency")
        th = ALERT_1H.get(sym)
        if ch is None or th is None or abs(ch) < th:
            continue
        direction = "up" if ch > 0 else "down"
        key = f"{sym}_{direction}"
        if time.time() - last.get(key, 0) < ALERT_COOLDOWN_MIN * 60:
            continue
        last[key] = time.time()
        price = c["current_price"]
        p = f"${price:,.0f}" if price >= 100 else f"${price:,.4f}"
        icon, word = ("🚀", "급등") if ch > 0 else ("⚠️", "급락")
        text = (f"{icon} <b>{sym} 1시간 {word}</b> {ch:+.1f}%\n"
                f"현재 {p} · 24h {c.get('price_change_percentage_24h_in_currency', 0):+.1f}%\n"
                f"<i>{now_kst():%H:%M} KST · CoinGecko</i>\n\n"
                f"원인이 된 뉴스를 찾으면 이 글에 답글로 공유해 주세요.\n<i>{DISCLAIMER}</i>")
        send("market", text)


def route(title):
    t = title.lower()
    for topic, kws in KEYWORD_ROUTES.items():
        if any(k.lower() in t for k in kws):
            return topic
    return None


def news_alerts(state):
    seen = state.setdefault("seen_news", [])
    first_run = not seen
    sent = 0
    for n in fetch_news(FEEDS, hours=3):
        h = hashlib.md5(n["title"].lower().encode()).hexdigest()[:12]
        if h in seen:
            continue
        seen.append(h)
        topic = route(n["title"])
        if first_run or not topic or sent >= MAX_NEWS_ALERTS_PER_RUN:
            continue  # 첫 실행은 기록만 하고 보내지 않음(과거 뉴스 폭탄 방지)
        src = f" — {esc(n['source'])}" if n["source"] else ""
        send(topic, f'🔔 <b>속보</b>\n<a href="{esc(n["link"])}">{esc(n["title"])}</a>{src}')
        sent += 1
    state["seen_news"] = seen[-500:]


if __name__ == "__main__":
    state = load_json(STATE_FILE, {})
    for fn in (price_alerts, news_alerts):
        try:
            fn(state)
        except Exception:
            traceback.print_exc()
    save_json(STATE_FILE, state)
