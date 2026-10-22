"""매일 08:30 KST 숫자 브리핑 → ☀️ 데일리 브리핑 탭."""
import traceback

from config import COINS, MACRO, FEEDS, DISCLAIMER, ROOM_NAME
from common import (esc, now_kst, coingecko_markets, fear_greed, FNG_KO, yahoo_quote,
                    upbit_prices, fetch_news, pct, send)

WEEKDAY = "월화수목금토일"


def build():
    d = now_kst()
    lines = [f"☀️ <b>{ROOM_NAME} 아침 브리핑</b> · {d:%m/%d}({WEEKDAY[d.weekday()]})", ""]

    # 코인
    usdkrw = None
    try:
        usdkrw, _ = yahoo_quote("KRW=X")
    except Exception:
        traceback.print_exc()
    try:
        mk = coingecko_markets([c[0] for c in COINS])
        up = {}
        try:
            up = upbit_prices([c[2] for c in COINS])
        except Exception:
            traceback.print_exc()
        lines.append("<b>🪙 코인</b> (24h · 7d)")
        for cid, sym, upm in COINS:
            c = mk.get(cid)
            if not c:
                continue
            price = c["current_price"]
            p = f"${price:,.0f}" if price >= 100 else f"${price:,.4f}"
            row = (f"• {sym} {p}  {pct(c.get('price_change_percentage_24h_in_currency'))}"
                   f" · {pct(c.get('price_change_percentage_7d_in_currency'))}")
            if usdkrw and upm in up:
                kimp = (up[upm] / (price * usdkrw) - 1) * 100
                row += f"  <i>김프 {kimp:+.1f}%</i>"
            lines.append(row)
    except Exception:
        traceback.print_exc()
        lines.append("• 코인 시세를 불러오지 못했습니다")

    try:
        v, cls, prev = fear_greed()
        lines.append(f"• 공포·탐욕 지수 <b>{v}</b> ({FNG_KO.get(cls, cls)}, 전일 {prev})")
    except Exception:
        traceback.print_exc()
    lines.append("")

    # 거시
    lines.append("<b>🌎 거시 지표</b> (직전 거래일 종가)")
    for sym, name, dg in MACRO:
        try:
            last, chg = yahoo_quote(sym)
            val = f"{last:,.{dg}f}" + ("%" if sym == "^TNX" else "")
            lines.append(f"• {name} {val}  {pct(chg, 2)}")
        except Exception:
            traceback.print_exc()
    lines.append("")

    # 뉴스 헤드라인
    news = fetch_news(FEEDS, hours=14)[:6]
    if news:
        lines.append("<b>📰 밤사이 헤드라인</b>")
        for n in news:
            src = f" — {esc(n['source'])}" if n["source"] else ""
            lines.append(f'• <a href="{esc(n["link"])}">{esc(n["title"])}</a>{src}')
        lines.append("")

    lines.append("오늘 눈에 띄는 숫자가 있다면 💬 자유토론에서 같이 읽어요.")
    lines.append(f"<i>{DISCLAIMER}</i>")
    return "\n".join(lines)


if __name__ == "__main__":
    send("brief", build())
