# 노코드 자동화 기초 — 프로젝트 1: 지출 메모 자동 분류 파이프라인

> Codyssey "AI 도구 학습" 커리큘럼 — 노코드 자동화 기초: 워크플로우 설계 미션  
> 프로젝트1: 동일 워크플로우를 **도구 A(Make.com) + 도구 B(n8n)** 로 구현·비교. 비교 분석 보고서·프로젝트2는 별도.  
> **작업 규칙:** 이 저장소에서 수정이 생기면 **GitHub(`origin/main`)에 먼저 커밋·푸시**한다.

---

## 1. 이 워크플로우가 속한 위치

| 구분 | 내용 |
|---|---|
| 소속 프로젝트 | **프로젝트 1** (동일 워크플로우를 2개 이상 도구로 구현·비교) — 프로젝트 2(자유 주제)와는 별개 |
| 주제 | 지능형 지출 관리 및 고액 지출 분류 파이프라인 |
| 도구 A | Make.com (아래 2~6절 — 구현 진행 중) |
| 도구 B | **n8n (Self-hosted)** — **최종 워크플로우 확정** → `n8n/n8n_지출_메모_자동_분류.workflow.json` |

### 도구 B 결정 (Zapier → n8n)

| 후보 | 판단 |
|---|---|
| Zapier Free | Zap당 트리거 1 + 액션 1(2단계). Paths/멀티스텝 분기 불가 → **본 구조(최소 4단계+3분기) 재현 불가** |
| Zapier 유료/체험 | 가능하나 결제·체험 의존. 미션은 무료 조합 우선 |
| **n8n 셀프호스트 (채택)** | IF/Switch·멀티스텝 완전 무료. “자가호스팅 가능한 도구” 권장 예시와 일치 |

**구현 전 전제 (중요)**

1. **설치 마찰**: 무료의 대가로 Docker 또는 Node로 로컬 기동이 필요. “무료 = 즉시 사용”이 아님 → 설치 시간을 일정에 넣는다. 비교 보고서 「설정 난이도」 소재.
2. **트리거 노드명**: n8n에 Google Forms 전용 트리거 없음. Make의 “Forms Watch Rows”와 같이 **응답 스프레드시트 폴링(Google Sheets Trigger)** 으로 동일 구조 재현. 캡처·보고서에는 노드명이 Sheets로 표시됨을 명시.

---

## 2. 워크플로우 구조

```
[Trigger] 응답 시트 폴링 (Make: Forms Watch Rows 표기 / n8n: Google Sheets Trigger)
      │
      ▼
[Action 1] OpenAI (Chat Completion, JSON 모드)
      │  메모 텍스트 → { category, amount, summary, Classification } 추출
      ▼
[Router / Switch] 3-Way 조건 분기
      ├─ 분기 A: 고액 지출 (amount ≥ 50000)                         → Sheets 탭 "고액 지출 분류 결과"
      ├─ 분기 B: 일반 지출 (amount < 50000 AND Classification ≠ 분류불가) → Sheets 탭 "일반 지출 분류 결과"
      └─ 분기 C: 미분류/예외 (amount = 0 AND Classification = 분류불가)  → Sheets 탭 "검토 필요"
```

**도구 A (Make)**  
- Trigger 1개 (응답 시트 폴링) ✅  
- Action 2개 이상 (OpenAI 파싱 + Google Sheets 기록) ✅  
- 조건 분기 1개 이상 (3-Way Router) ✅  
- 보너스1 (AI 연동 Action) ✅  
- 보너스2 (실패 알림/재시도) — **미구현**

**도구 B (n8n)** — 동일 구조 목표, 구현 전  
- Trigger: Google Sheets (응답 시트 새 행)  
- 분기: Switch (또는 IF) 3-way  
- 설치: 로컬 `npx n8n` (Docker 미설치, Node v25 확인됨)

---

## 3. 사용 리소스 (계정 정보는 마스킹 처리할 것)

| 리소스 | 설명 | 스프레드시트/폼 ID (제출 캡처 시 가림) |
|---|---|---|
| 구글 폼 | "지출 메모 입력 폼" — 장문형 질문 **「지출 메모」** 1개 | 폼 ID: `1j2SzYUWOGPSxLRA6hrQtthPQBuKoE95suSw2rtGqUnI` |
| 응답 스프레드시트 | 폼 제출이 쌓이는 시트 — **n8n/Make Trigger 대상** | `1aZZXJaWqMkydaAICT42N2GKtZiAMbPk6PYCHg3PtUQ4` |
| 결과 스프레드시트 | "지출 자동 분류 결과" — 분기별 Append 대상 | `1wz8bcpjNRIwq8o-skC49M2orEjfBNRpW2eETmjvwmrg` |
| Google 계정 | `cho***45@gmail.com` | 스크린샷에서도 가릴 것 |

- 스크립트 최초 생성 시 결과 시트 탭은 **「분류 결과」1개**였을 수 있음. Make 구현 기준 README 구조는 탭 3개(**고액 지출 분류 결과 / 일반 지출 분류 결과 / 검토 필요**), 헤더 6열: 타임스탬프·원본 메모·카테고리·금액·요약·특이사항. n8n 조립 전 결과 시트에 이 3탭이 있는지 확인하고, 없으면 동일 헤더로 추가할 것.
- 폼/시트는 `create_google_form.js` (Google Apps Script)로 생성. **제출용 스크린샷·공유 문서에 URL 전체·시트 ID 노출 금지.**

---

## 4. AI 파싱 모듈 — 시스템 프롬프트 (최종 적용본)

```text
당신은 지출 내역 분석 비서입니다. 사용자의 메모를 분석하여 반드시 아래 JSON 구조로만 응답하세요. 마크다운 기호(```)를 절대 포함하지 말고 순수 JSON 문자열만 출력하세요.

{
  "category": "식비, 교통비, 문화생활, 생필품, 기타, 분류불가 중 택1",
  "amount": "지출 금액을 0 이상의 정수로만 기재",
  "summary": "지출 내역을 10자 이내로 요약",
  "Classification": "분류 가능 여/부 표시"
}

분류 규칙:
1. 메모에서 금액을 명확히 추출할 수 있고 그 값이 0보다 크면, amount에 해당 숫자를 그대로 기재하고 category는 내용에 맞게 분류하세요.
2. 실제로 비용이 들지 않은 정당한 지출(예: "무료 쿠폰으로 커피 받음", "친구가 밥 사줌")은 amount를 0으로 기재하되, category는 "분류불가"가 아니라 내용에 맞는 정상 카테고리로 분류하세요.
3. 아래에 해당하는 경우에만 Classification를 "분류불가"로, amount는 0으로 기재하세요.
   - 금액이 음수로 표현된 경우 (예: "-1000", "마이너스 5000원")
   - 금액을 특정할 수 없거나 메모에 금액 자체가 없는 경우
   - 지출 내용과 금액의 연결이 불명확해 파싱을 신뢰할 수 없는 경우
```

`category`(품목 분류)와 `Classification`(유효성 플래그: 정상/분류불가)을 별도 필드로 분리해, 정상적인 0원 지출(규칙2)과 파싱 실패·무효 지출(규칙3)을 구분함.

---

## 5. 조건 분기(Router) 로직 (최종 확정)

| 분기 | 조건 |
|---|---|
| A. 고액 지출 | `amount ≥ 50000` |
| B. 일반 지출 | `amount < 50000` AND `Classification ≠ "분류불가"` |
| C. 미분류/예외 | `amount = 0` AND `Classification = "분류불가"` |

세 조건 모두 실행 로그로 정상 작동 확인 전이라면, 아래 7번 체크리스트의 "3개 분기 재실행 및 캡처" 항목을 통해 검증할 것.

---

## 6. 트러블슈팅 로그 (보고서 "구현 과정 요약"에 그대로 활용 가능)

1. **Google Sheets 매핑 누락** — Add a Row 모듈 3개 전부 `values`가 비어있어 빈 행만 삽입되던 문제 → 분기별로 타임스탬프/원본 메모/카테고리/금액/요약 컬럼 매핑 완료. ✅ 해결됨 (실행 로그로 확인: `updatedRange`, `updatedCells` 정상 반환)
2. **미분류 분기 필터 로직 오류** — 최초엔 OpenAI 응답 객체 전체(`{{3.result}}`)를 숫자 `0`과 비교해 항상 거짓 판정되던 문제, 중간 수정에서는 필드는 고쳤으나 조건을 OR로 묶어 정상 0원 지출까지 미분류 분기로 새는 문제가 있었음 → `amount` 필드 참조로 교체 + `Classification` 필드 분리 + 두 조건을 AND로 묶어 최종 해결. ✅ 해결됨
3. **음수 금액 처리 정책 부재** — "햄버거 -1000" 테스트 시 GPT가 부호를 무시하고 절댓값(1000)만 추출해 정상 지출로 오분류됨 → 시스템 프롬프트에 "음수/무료지출/파싱불가"를 구분하는 규칙과 `Classification` 필드를 추가해 Make 시나리오에 반영함. ✅ 해결됨 (재실행 테스트로 3개 분기 정상 라우팅 확인 필요 — 7번 체크리스트 참고)
4. **계획서(walkthrough.md)와 구현물 불일치 — Slack 알림** — 최초 설계에는 분기 A/C에 Slack 알림이 포함돼 있었으나, 보너스2는 포함하지 않기로 결정함. ✅ 결정 완료 (구현 안 함)

---

## 7. 미완료 항목 (제출 전 체크리스트)

- [x] Router 필터 최종본 Make에 반영 (5번 표 참고)
- [x] 시스템 프롬프트 교체·재배포 (4번 참고)
- [x] 고아 모듈 삭제, 시나리오 이름 정리 (Sora/Whisper 미사용 표기 제거)
### 도구 A (Make)
- [ ] 테스트 3종(고액/일반/미분류-예외 + 무료지출 0원 케이스) 재실행 → 3개 분기 각각 최소 1회 실행 확인 및 캡처
- [ ] 워크플로우 구성 화면 스크린샷 캡처 (계정 이메일·시트 ID 가림 처리) — 캔버스의 OpenAI 모듈 표시명("ChatGPT, Sora, Whisper")은 Make 앱 자체 이름이라 그대로 둬도 무방

### 도구 B (n8n)
- [x] Zapier 대신 n8n 채택 결정 + 전제(설치 마찰, Sheets 트리거) 문서화
- [x] 로컬 환경 확인 (Node ✅ / Docker ❌)
- [x] Windows SDK 10.0.26100 설치 (winget) + node-gyp 11로 네이티브 모듈 재빌드
- [x] n8n@2.31.5 로컬 기동 확인 (`n8n-runtime/`, http://localhost:5678)
- [x] owner 계정 가입 완료
- [x] Google Sheets Trigger OAuth2 Account connected
- [x] 최종 워크플로우 JSON 확정 — `n8n/n8n_지출_메모_자동_분류.workflow.json`
- [x] Credentials: Trigger OAuth2 + Sheets OAuth2 + OpenAI 연결
- [x] Append 패치 반영 + 결과 검증 — 고액·일반 7/23 행 확인, 검토는 7/21 음수 행으로 분기 입증
- [x] 비교 분석 보고서 초안 — `report/프로젝트1_자동화_도구_비교_분석_보고서.md`
- [x] Make 동작 GIF 6개 — `gifs/make_*.gif`
- [x] n8n 설치·OAuth 마찰 이미지 — `png/n8n_setup_or_oauth.*` + friction 01–06
- [ ] **n8n 실행 GIF만** 촬영: `gifs/n8n_workflow_overview` 등
- [ ] 테스트 3종 + 분기별 1회 이상 캡처 + 워크플로우 JSON Export

### 공통
- [ ] 프로젝트1 비교 분석 보고서 작성 (도구명·구현 요약·비교 항목 5개 이상·장단점·적합 상황 — Zapier 미채택 사유도 포함)
- [ ] **프로젝트2(자유 주제) 반복 업무 정의 및 구현** — 현재 완전히 미착수, 프로젝트1과 별개로 새로 시작해야 함

---

## 8. 저장소 디렉터리 구조

```text
Codyssey_3_ProJect/
├── README.md                 # 본 문서 (진행 상태)
├── 미션.txt                  # 미션 원문
├── create_google_form.js     # 폼·결과 시트 생성 Apps Script
├── Integration Google Forms, OpenAI (ChatGPT).blueprint.json  # Make 시나리오
├── gifs/                     # Make 실행 GIF (make_*.gif), n8n 실행 GIF 예정
├── png/                      # n8n 설치·OAuth 마찰 PNG/GIF + 렌더 스크립트
├── n8n/                      # n8n 워크플로·설계·패치 스크립트
│   ├── n8n_지출_메모_자동_분류.workflow.json
│   ├── n8n_워크플로우_설계.md
│   ├── _patch_n8n_append.mjs
│   └── ...
├── report/                   # 비교 분석 보고서 Markdown
│   └── 프로젝트1_자동화_도구_비교_분석_보고서.md
├── other/                    # 사전 조사 등 기타 문서
│   └── README.md             # (구 AI_자동화_도구_비교_분석.md)
├── n8n-runtime/              # 로컬 n8n 설치 (gitignore, 미커밋)
└── n8n-local/                # 로컬 실험용 (gitignore, 미커밋)
```

## 9. 참고 파일

- `report/프로젝트1_자동화_도구_비교_분석_보고서.md` — 프로젝트1 비교 분석 보고서 초안
- `gifs/` — Make 실동작 GIF · n8n 실행 GIF 촬영본 위치
- `png/` — n8n 설치·OAuth 마찰 이미지 (`README.md`, `_render_setup_friction.py`)
- `n8n/n8n_지출_메모_자동_분류.workflow.json` — n8n 최종 워크플로우
- `n8n/n8n_워크플로우_설계.md` — 도구 B 설계·설치 기록
- `create_google_form.js` — 폼/결과 시트 생성용 Google Apps Script
- `Integration Google Forms, OpenAI (ChatGPT).blueprint.json` — Make 시나리오 내보내기
- `other/README.md` — 도구 사전 조사 (Zapier/Make/n8n)
- `미션.txt` — 미션 명세