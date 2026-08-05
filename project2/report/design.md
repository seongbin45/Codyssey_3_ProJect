# project2/report/design.md — 팀 문의/피드백 자동 분류 파이프라인

GitHub에서 이 문서를 열면 **구현 화면(§3.1)** 과 **실행 GIF(§7)** 를 바로 볼 수 있다.

## 1. 반복 업무 정의

FinFit 팀/제품에 들어오는 문의·피드백을 사람이 매번 읽고 "이거 긴급한가?"를 판단해서
담당자에게 전달하는 작업. 문의량이 늘면 판단·전달에 드는 시간이 누적된다.
이 워크플로우는 문의가 들어오는 즉시 AI가 긴급도·카테고리를 판단하고,
긴급 건만 담당자에게 즉시 알리고 나머지는 로그로만 남긴다.

## 2. 도구 선정

**Make.com** (도구 A 재사용, 프로젝트1과 계정 동일)

| 후보 | 판단 |
|---|---|
| Make (채택) | 클라우드 상시 구동 — 팀 문의를 "실제로" 상시 수신하는 시나리오에 적합. 프로젝트1에서 계정·연동 경험 있어 셋업 빠름 |
| n8n | 완전 무료지만 로컬/서버 상시 기동 필요 — 개인 PC 기반 데모에는 적합해도 "팀이 상시 쓰는 도구"로는 부적합 |

## 3. 워크플로우 구조

```
[Trigger] 문의 접수 폼 응답 감지 (Google Forms → 응답 시트 폴링)
      │
      ▼
[Action 1] OpenAI (Chat Completion, JSON 모드)
      │  문의 내용 → { urgency: "긴급"/"일반", category: "버그/기능요청/결제/기타", summary }
      ▼
[Filter/Router] 2-Way 조건 분기
      ├─ 긴급 (urgency = "긴급")  → [Action 2] Sheets 기록 + [Action 3] Slack 즉시 알림 (팀 채널)
      └─ 일반 (urgency = "일반")  → [Action 2] Sheets 기록만
```

- Trigger 1개 (폼 응답 감지) ✅
- Action 2개 이상 (AI 분류 + Sheets 기록, 긴급 시 알림까지 3개) ✅
- 조건 분기 1개 이상 (긴급/일반 2-way) ✅ — 프로젝트1의 3-way와 구조를 다르게 가져가 구분
- 보너스1 (AI 연동 Action) — OpenAI 분류로 자연 충족 ✅

### 3.1 구현 화면 (Make 캔버스)

시나리오 전체 구성 화면. (파일: `../make/Make_workflow_view.jpeg`)

![Make 구현 화면 — FinFit 문의 자동 분류](../make/Make_workflow_view.jpeg)

## 4. 필드 스키마 (OpenAI 응답)

```json
{
  "urgency": "긴급 또는 일반",
  "category": "버그, 기능요청, 결제, 기타 중 택1",
  "summary": "문의 내용을 15자 이내로 요약"
}
```

## 5. 알림 채널

**채택 (실동작):** Slack **공개 팀 채널** `새-채널` (`channelType = public`).  
DM(`im`/slackbot)은 초기 검증용으로만 쓰고, 제출·실사용은 팀 채널로 둔다.  
공개 Blueprint에는 채널 ID를 `***SLACK_TEAM_CHANNEL_ID***` 로 마스킹하고, Import 후 Make UI에서 `새-채널`을 다시 선택한다. (상세: [`../README.md`](../README.md) §7)

**대체안 (리스크 완화)**  
Slack 권한이 없을 경우 → Gmail 알림, 또는 결과 시트「긴급 문의」탭만으로 대체.

## 6. 테스트 케이스 (분기별 1회 이상 실행 증거용)

| # | 문의 내용 예시 | 기대 결과 | 실행 증거 GIF |
|---|---|---|---|
| 1 | "결제가 안 돼요, 지금 당장 필요해요" (또는 동등 긴급 문구) | urgency=긴급 → Sheets「긴급 문의」+ Slack | §7 긴급 3종 |
| 2 | "다크모드 지원 언제 되나요?" (또는 동등 일반 문구) | urgency=일반 → Sheets「일반 문의」만 | §7 일반 2종 |

파일 목록·명명 규칙 상세: [`../gif/README.md`](../gif/README.md)

---

## 7. 실행 결과 화면 (GIF — 설계 문서에서 바로 보기)

GitHub·VS Code 등 Markdown 미리보기에서 아래 이미지를 클릭·재생할 수 있다.  
원본 경로: `../gif/make_*.gif` (프로젝트1 보고서와 동일한 **문서 임베드** 방식).

### 7.1 긴급 분기

**① 폼 제출** — `../gif/make_urgent_1_form.gif`

![긴급 · 폼 양식 응답](../gif/make_urgent_1_form.gif)

**② Make 액션** — 시나리오 실행 → 「긴급 문의」탭 — `../gif/make_urgent_2_action.gif`

![긴급 · 에이전트 액션](../gif/make_urgent_2_action.gif)

**③ Slack 팀 채널 알림** — 공개 채널 `새-채널` — `../gif/make_urgent_3_slack.gif`

![긴급 · Slack 알림](../gif/make_urgent_3_slack.gif)

### 7.2 일반 분기

**① 폼 제출** — `../gif/make_normal_1_form.gif`

![일반 · 폼 양식 응답](../gif/make_normal_1_form.gif)

**② Make 액션** — 「일반 문의」탭만 (Slack 없음) — `../gif/make_normal_2_action.gif`

![일반 · 에이전트 액션](../gif/make_normal_2_action.gif)

### 7.3 증거 한눈에

| 분기 | form | action | 추가 |
|------|------|--------|------|
| 긴급 | [make_urgent_1_form.gif](../gif/make_urgent_1_form.gif) | [make_urgent_2_action.gif](../gif/make_urgent_2_action.gif) | [make_urgent_3_slack.gif](../gif/make_urgent_3_slack.gif) |
| 일반 | [make_normal_1_form.gif](../gif/make_normal_1_form.gif) | [make_normal_2_action.gif](../gif/make_normal_2_action.gif) | — |

구현 화면: [Make_workflow_view.jpeg](../make/Make_workflow_view.jpeg) · 재현·Slack 설정: [`../README.md`](../README.md)
