"""크립토 미션 공부방 봇 설정. 숫자·키워드는 여기서만 바꾸면 됩니다."""

ROOM_NAME = "크립토 미션 공부방"
MEMBER_LIMIT = 100  # 초대 링크 인원 제한

# 토픽(탭) 이름 → 내부 키. setup 실행 시 자동 생성되고 ID가 topics.json에 저장됩니다.
TOPICS = {
    "brief": "☀️ 데일리 브리핑",
    "market": "📈 시황·속보",
    "macro": "🌎 거시경제",
    "regulation": "🏛 규제·정책",
    "free": "💬 자유토론",
}

# 브리핑에 나오는 코인 (CoinGecko id, 표시 이름, 업비트 마켓)
COINS = [
    ("bitcoin", "BTC", "KRW-BTC"),
    ("ethereum", "ETH", "KRW-ETH"),
    ("ripple", "XRP", "KRW-XRP"),
]

# 1시간 변동률 속보 기준(%) — 넘으면 시황·속보 탭에 즉시 알림
ALERT_1H = {"BTC": 3.0, "ETH": 4.0, "XRP": 5.0}
ALERT_COOLDOWN_MIN = 180  # 같은 코인·같은 방향 알림 재발송 간격

# 아침 브리핑 거시 지표 (Yahoo Finance 심볼, 표시 이름, 소수점)
MACRO = [
    ("^GSPC", "S&P 500", 2),
    ("^IXIC", "나스닥", 2),
    ("DX-Y.NYB", "달러 인덱스", 2),
    ("^TNX", "미국채 10년", 3),
    ("KRW=X", "원/달러", 1),
    ("GC=F", "금", 1),
]

# 뉴스 RSS
FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://news.google.com/rss/search?q=XRP+OR+%EB%A6%AC%ED%94%8C+OR+%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8+when:1d&hl=ko&gl=KR&ceid=KR:ko",
    "https://news.google.com/rss/search?q=(SEC+OR+%22CLARITY+Act%22+OR+FOMC+OR+CPI)+crypto+when:1d&hl=en-US&gl=US&ceid=US:en",
]

# 속보 키워드 → 보낼 토픽. 제목에 하나라도 있으면 알림 (대소문자 무시)
KEYWORD_ROUTES = {
    "regulation": ["CLARITY Act", "클래리티", "SEC ", "증권거래위원회", "Senate", "상원", "stablecoin bill",
                   "가상자산법", "금융위", "ETF approval", "ETF 승인"],
    "macro": ["FOMC", "Fed rate", "기준금리", "Powell", "파월", "CPI", "소비자물가", "nonfarm", "고용지표", "Treasury yield"],
    "market": ["Ripple", "리플", "XRP ETF", "hack", "해킹", "liquidation", "청산"],
}
MAX_NEWS_ALERTS_PER_RUN = 3

DISCLAIMER = "ℹ️ 정보 공유 목적이며 특정 자산의 매수·매도 권유가 아닙니다."
