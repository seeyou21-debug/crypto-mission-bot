"""한 번만 실행: 그룹 찾기 → 토픽 생성 → 100명 초대 링크 생성 → topics.json 저장."""
from config import TOPICS, MEMBER_LIMIT, ROOM_NAME, DISCLAIMER
from common import TOPICS_FILE, load_json, save_json, tg


def find_group():
    for u in reversed(tg("getUpdates", allowed_updates=["message", "my_chat_member"])):
        chat = (u.get("message") or u.get("my_chat_member") or {}).get("chat", {})
        if chat.get("type") == "supergroup":
            return chat
    raise SystemExit("그룹을 찾지 못했습니다. 봇을 관리자로 추가한 뒤 그룹에 /setup 이라고 한 번 입력하고 다시 실행하세요.")


if __name__ == "__main__":
    data = load_json(TOPICS_FILE, {})
    if not data.get("chat_id"):
        chat = find_group()
        data = {"chat_id": chat["id"], "title": chat.get("title"), "topics": {}}
        print("그룹 발견:", chat.get("title"), chat["id"])
    me = tg("getMe")
    member = tg("getChatMember", chat_id=data["chat_id"], user_id=me["id"])
    if member.get("status") != "administrator":
        raise SystemExit("봇이 관리자가 아닙니다. 관리자로 지정하고 '토픽 관리', '초대 링크' 권한을 켜 주세요.")

    for key, name in TOPICS.items():
        if key not in data["topics"]:
            t = tg("createForumTopic", chat_id=data["chat_id"], name=name)
            data["topics"][key] = t["message_thread_id"]
            print("토픽 생성:", name)

    if not data.get("invite_link"):
        link = tg("createChatInviteLink", chat_id=data["chat_id"],
                  name="유튜브 고정댓글", member_limit=MEMBER_LIMIT)
        data["invite_link"] = link["invite_link"]
    print("\n★ 고정 댓글에 넣을 초대 링크 (선착순 %d명):\n%s\n" % (MEMBER_LIMIT, data["invite_link"]))

    save_json(TOPICS_FILE, data)

    # 환영 공지 (데일리 브리핑 탭에 고정)
    rules = (f"👋 <b>{ROOM_NAME}에 오신 걸 환영합니다</b>\n\n"
             "여기는 숫자를 같이 읽는 방입니다.\n"
             "• ☀️ 데일리 브리핑 — 매일 08:30 아침 숫자, 22:00 미국장 전 체크, 월요일 주간 일정\n"
             "• 📈 시황·속보 — 가격 급변·주요 뉴스 자동 알림\n"
             "• 🌎 거시경제 / 🏛 규제·정책 — 금리·달러·의회 소식\n"
             "• 💬 자유토론 — 해석과 질문은 여기서\n\n"
             "<b>방 규칙</b>\n"
             "1. 매수·매도 권유, 목표가 단정, 수익 인증 금지\n"
             "2. 다른 방·유료방·거래소 추천 링크 홍보 금지\n"
             "3. 운영자는 절대 먼저 DM하지 않습니다. 송금·개인정보 요구는 100% 사칭입니다.\n\n"
             f"<i>{DISCLAIMER}</i>")
    msg = tg("sendMessage", chat_id=data["chat_id"], text=rules, parse_mode="HTML",
             message_thread_id=data["topics"]["brief"])
    try:
        tg("pinChatMessage", chat_id=data["chat_id"], message_id=msg["message_id"])
    except Exception as e:
        print("공지 고정 실패(권한 확인):", e)
    print("완료!")
