# 크립토 미션 공부방 봇

텔레그램 토픽 그룹에 정보를 자동으로 올리는 봇입니다.

| 언제 | 무엇을 | 어느 탭에 | 누가 돌리나 |
|---|---|---|---|
| 매일 08:30 | 코인 시세·김프·공포탐욕, 미 증시·달러·국채·환율·금, 밤사이 헤드라인 | ☀️ 데일리 브리핑 | GitHub Actions (무료) |
| 15분마다 | 1시간 급등락 (BTC 3% / ETH 4% / XRP 5%), 규제·거시 키워드 속보 | 📈 시황 / 🏛 규제 / 🌎 거시 | GitHub Actions (무료) |
| 매일 22:00 | 오늘 밤 미국 일정, ETF 자금 흐름, 규제 소식 요약 | ☀️ 데일리 브리핑 | Claude 예약 작업 |
| 월요일 08:00 | 이번 주 경제·의회·코인 일정표 | ☀️ 데일리 브리핑 | Claude 예약 작업 |

---

## 세팅 (약 15분, 한 번만 하면 됨)

### 1. 텔레그램 봇 만들기
1. 텔레그램에서 **@BotFather** 검색 → `/newbot`
2. 봇 이름(예: 크립토 미션 봇)과 아이디(예: cryptomission_study_bot) 입력
3. 받은 **토큰**(`123456:ABC...` 형태)을 복사해 두기. 이 토큰은 비밀번호와 같으니 아무 데도 공개하지 마세요.

### 2. 그룹 만들기
1. 새 그룹 만들기 → 이름 "크립토 미션 공부방"
2. 그룹 설정 → **주제(Topics)** 켜기
3. 그룹 설정 → 관리자 → 봇 추가 → 권한 중 **주제 관리, 메시지 고정, 초대 링크로 사용자 초대** 켜기
4. 그룹 채팅창에 `/setup` 한 번 입력 (봇이 그룹을 알아보게 하는 용도, 24시간 안에 3단계 진행)

### 3. GitHub 저장소 만들기
1. github.com 가입/로그인 → New repository → 이름 `crypto-mission-bot` → **Public** 선택
   (Public이면 Actions가 무제한 무료. 토큰은 Secrets에 들어가서 공개되지 않습니다)
2. "uploading an existing file" 클릭 → 이 폴더 안의 파일·폴더 전부 끌어다 놓고 Commit
   - `.github` 폴더가 꼭 같이 올라가야 합니다 (숨김 폴더라 안 보이면 보기 설정에서 숨김 파일 표시)
3. Settings → Secrets and variables → Actions → New repository secret
   - Name: `TELEGRAM_BOT_TOKEN` / Value: 1단계 토큰

### 4. 방 자동 세팅
1. 저장소 Actions 탭 → **Setup room** → Run workflow
2. 완료되면 그룹에 토픽 5개 + 환영·규칙 공지가 생깁니다
3. 실행 로그에 나온 **초대 링크**(선착순 100명 제한)를 유튜브 고정 댓글에 넣으세요

### 5. 테스트
Actions 탭 → **Morning briefing** → Run workflow → 데일리 브리핑 탭에 글이 오면 성공.
이후부터는 시간 맞춰 자동으로 올라갑니다.

### 6. Claude 예약 작업 연결 (22:00 체크, 월요일 일정표)
GitHub → Settings(계정) → Developer settings → Fine-grained tokens → Generate
- Repository access: `crypto-mission-bot` 하나만
- Permissions: **Contents → Read and write**
- 만든 토큰을 Claude에게 전달하면 예약 작업 2개를 만들어 드립니다.

---

## 바꾸고 싶을 때
- 코인 추가, 급등락 기준, 키워드, 뉴스 출처 → `bot/config.py`
- 아침 브리핑 시간 → `.github/workflows/morning.yml`의 cron (UTC 기준, KST −9시간)
- 잠깐 멈추기 → Actions 탭에서 워크플로 선택 → ··· → Disable

## 알아둘 점
- GitHub 예약 실행은 몇 분 늦을 수 있습니다.
- 첫 속보 실행은 기존 뉴스를 기록만 하고 보내지 않습니다(옛날 뉴스가 한꺼번에 쏟아지는 것 방지).
- 초대 링크 100명이 차면 링크가 자동으로 막힙니다. 더 받으려면 `topics.json`에서 `invite_link` 줄을 지우고 Setup room을 다시 실행하세요.
