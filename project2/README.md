# project2/ — 프로젝트 2: 자유 주제 자동화

Codyssey 미션 **[프로젝트 2] 자유 주제 자동화 설계 및 구현**.  
프로젝트 1(`../make/`, `../n8n/`, `../report/`)과 **폴더로만 구분**하고, 브랜치는 나누지 않는다 (`main` 유지).

| 항목 | 내용 |
|------|------|
| 상태 | **제출본 완료** — 미션 프로젝트 2 필수 항목 충족 (문서 교차검증 반영) |
| 선정 주제 | FinFit 팀 문의·피드백 긴급도/카테고리 자동 분류 |
| 도구 | **Make.com** (클라우드 상시 구동 · 프로젝트1 계정 재사용) |
| 설계 문서 | [`report/design.md`](./report/design.md) (GitHub에서 GIF·캡처 열람) |
| 공통 구조 | Trigger 1+ · Action 2+ · 조건 분기 1+ · **각 분기 1회 이상 실행 증거** |
| 자동 실행 | Trigger(폼 응답) 발생 시 시나리오 ON이면 **자동** 실행 (설계 문서만 제출 불가) |
| 보너스1 | ✅ OpenAI JSON 분류 · 보너스2(실패 알림)는 선택·미구현 |

---

## 1. 미션 산출물 체크리스트 (프로젝트 2)

| # | 요구 | 상태 |
|---|------|------|
| 1 | 자동화할 **반복 업무 1개** 정의 | ✅ 문의/피드백 긴급 분류 (`report/design.md` §1) |
| 2 | **도구 1개** 선정 + 선정 이유 | ✅ Make — 상시 클라우드 (`report/design.md` §2) |
| 3 | 워크플로우 **설계 문서** (설명 또는 다이어그램) | ✅ [`report/design.md`](./report/design.md) (§3 · **§3.1·§7 캡처/GIF 임베드**) |
| 4 | **구현 화면** 캡처 | ✅ `make/Make_workflow_view.jpeg` — **`report/design.md` §3.1** |
| 5 | **실행 결과** 캡처 (분기별 1회 이상) | ✅ `gif/` 5종 — **`report/design.md` §7** |
| 6 | 실제 동작 워크플로우 (Export/Blueprint 등) | ✅ 공개 마스킹 Blueprint + LOCAL 실동작 확인 |

### 공통 기능 요구 (프로젝트 1과 동일 코어)

- Trigger ≥ 1  
- Action ≥ 2  
- 조건 분기(Filter/Router) ≥ 1 → **분기 경로마다 1회 이상 실행 확인**  
- (권장) 보너스1: 생성형 AI Action — 분류·요약에 자연스럽게 붙일 수 있음  
- (선택) 보너스2: 실패 알림·재시도  

---

## 2. 선정 주제 (확정)

**팀 문의/피드백 자동 분류** · 도구 **Make.com** · 상세는 [`report/design.md`](./report/design.md).

| 단계 | 내용 |
|------|------|
| Trigger | Google Forms 문의 접수 → 응답 시트 폴링 |
| Action | OpenAI JSON 분류 → Sheets 기록 (+ 긴급 시 **Slack 팀 채널** 알림) |
| 분기 | `urgency = 긴급` / `일반` (2-way) |
| 긴급 알림 | Slack `Create a Message` → **Public channel** · 채널명 **`새-채널`** (아래 §7) |
| 테스트 | 결제 장애(긴급) · 다크모드 요청(일반) — `report/design.md` §6 |

### 검토만 했던 후보 (미채택)

| # | 주제 | 미채택 요약 |
|---|------|-------------|
| 2 | RSS/뉴스 요약 알림 | 실무 스토리 약함 · 계정 장벽은 낮음 |
| 3 | 캘린더 리마인더 | 개인 일정 중심 · 팀 문의 실사용과 거리 |

**Make 선정 이유 (요약):** 팀 문의를 노트북 전원과 무관하게 상시 수신하려면 클라우드가 맞고, 프로젝트1 Make 계정·연동 재사용이 빠르다. n8n은 로컬 상시 기동이 필요해 “팀 상시 도구” 스토리에 불리하다.

---

## 3. 제약 · 보안 (프로젝트 1과 동일 규칙)

| 규칙 | 내용 |
|------|------|
| 민감정보 | API Key, 토큰, 비밀번호 **노출 금지** |
| 마스킹 | 시트/폼 ID → `***…_ID***`, 이메일 → `cho***45@…` 형태 일부 가림 |
| 과금 | **무료 플랜 우선** (Make Free 월 1,000 크레딧 등). 유료 불가피 시 이유 + 무료 대안을 설계 문서에 기록 |
| 권장 조합 예 | Google Sheets + Gmail/Email + Webhook · Sheets + Slack/Discord + Webhook |
| 커밋 | 변경 시 `origin/main`에 커밋·푸시 (저장소 작업 규칙) |

---

## 4. 이 폴더 구조

```text
project2/
├── README.md              # 본 문서 (주제·체크리스트·규칙·Slack 채널)
├── report/
│   ├── README.md
│   └── design.md          # 설계 + 구현 화면·GIF 임베드 (GitHub 열람용)
├── make/                  # Make Blueprint·캡처
├── gif/                   # 실행 증명 GIF (5)
├── create_google_form_Project_2.js
└── FinFit 팀 문의 피드백 자동 분류 (project2).blueprint.json
```

### 현재 파일

| 파일 | 설명 |
|------|------|
| `README.md` | 진행 상태·체크리스트·규칙·**Slack 팀 채널** |
| **`report/design.md`** | 설계 본문 + **구현 화면·실행 GIF 임베드** (제출·채점 주 문서) |
| `report/README.md` | report 폴더 안내 |
| `make/FinFit_inquiry_auto_triage.blueprint.json` | Make Import용 (시트·Slack ID **마스킹**) |
| `FinFit 팀 문의 피드백 자동 분류 (project2).blueprint.json` | Make Export 정리본 (공개 마스킹 · Slack 본문 템플릿 포함) |
| `make/README.md` | Import 절차·시트 헤더·재매핑 안내 |
| `gif/` | 긴급/일반 form·action + Slack 실행 GIF (`gif/README.md`) |
| `create_google_form_Project_2.js` | 문의 폼·결과 시트(긴급/일반 탭) Apps Script |
| `_build_blueprint.py` | Blueprint 재생성 스크립트 |

파일·하위 폴더를 추가할 때마다 **해당 폴더 README** 또는 본 README 표를 갱신한다.

---

## 5. 폴더 README 규칙 (저장소 공통)

| 규칙 | 설명 |
|------|------|
| 필수 | **커밋 대상** 산출물 폴더마다 `README.md` |
| 내용 | 목적, **파일별 설명 표**, 관련 경로, 주의사항 |
| 갱신 | 파일 추가·이동·이름 변경 시 **같은 커밋**에서 README 수정 |
| 하지 않음 | **커밋 제외 폴더**(`.gitignore`)에는 README를 만들지 않는다 |

---

## 6. 구현·검증 완료 목록

1. [x] 주제·도구 확정 + `report/design.md`  
2. [x] Make Import용 Blueprint — `make/…LOCAL.blueprint.json` **실동작 확인** (공개본은 마스킹)  
3. [x] Google 문의 폼 + 결과 시트 탭「긴급 문의」「일반 문의」  
4. [x] Make 연결 재매핑 (Google / OpenAI / Slack)  
5. [x] **긴급 분기** 테스트 — Slack 메시지 전송 성공  
6. [x] **일반 분기** 실행 + GIF (`gif/make_normal_*.gif`)  
7. [x] 실행 증명 GIF 5종 — `gif/README.md` (녹화 여백 crop 후 변환)  
8. [x] Slack **팀 공개 채널** `새-채널` (`channelType=public`, DM 아님) — §7  
9. [x] 미션 기준 교차검증 — 필수 항목 충족 · 루트 README 상태와 동기화  

**재현 시 주의:** 공개 Blueprint Import 후 Slack·시트 ID는 Make UI에서 본인 리소스로 다시 고른다 (`***…***` 플레이스홀더 그대로 실행 금지).

---

## 7. Slack 채널 (긴급 알림) — GIF 교차검증

실동작 모듈: **`slack:CreateMessage`** (긴급 Router 경로만).

### 7.0 교차검증 결론 (문서 ↔ GIF)

| 구분 | 내용 |
|------|------|
| 설계 초안 후보 | 팀 채널을 **공개 또는 비공개** 중 고르는 방향 |
| **최종 검증·제출** | **Public(공개) 채널 `#새-채널`** 만 사용 |
| GIF에 보이는가? | **예.** `gif/make_urgent_3_slack.gif` 헤더·본문에 **`# 새-채널` / `#새-채널`**, 발신 **Make 앱**, 본문 `[FinFit 긴급 문의]…` |
| 불일치였던 점 | `make/README`·Blueprint 라벨 등에 **「공개 또는 비공개」** 가 남아 최종 증거와 어긋남 → **본 절·GIF 기준으로 통일** |

설계 문서 임베드: [`report/design.md`](./report/design.md) §5 · §7.1 ③

### 7.1 Blueprint 설정 (제출·재현용 요약)

| 항목 | 값 | 비고 |
|------|-----|------|
| 모듈 | `slack:CreateMessage` | 긴급 경로만 |
| Connection | Slack **bot** connection | 워크스페이스 Make 연동 |
| Channel type | **`public`** (`Public channel`) | **private / im 미사용** |
| 채널 이름 | **`#새-채널`** | GIF·Make label 동일 |
| 채널 ID (실값) | `C…` (예: Export `C0BM…`) | 공개 레포는 `***SLACK_TEAM_CHANNEL_ID***` |
| 메시지 | mrkdwn 템플릿 | 카테고리·요약·긴급도·원문·접수·연락처 |

```text
*[FinFit 긴급 문의]* {{2.result.category}}
요약: {{2.result.summary}}
긴급도: {{2.result.urgency}}
원문: {{1.1}}
접수: {{1.0}}
연락처: {{1.2}}
```

### 7.2 공개 Blueprint vs Make 실시나리오

| 구분 | Slack `channel` |
|------|-----------------|
| **Git 공개본** | `***SLACK_TEAM_CHANNEL_ID***` (마스킹) · type=`public` |
| **Make 실동작** | Public 목록에서 **`새-채널`** 선택 |

Import 직후 플레이스홀더 그대로면 `channel_not_found`.  
**Public channel → `새-채널` 재선택** 후 Save.

### 7.3 Make에서 연결하는 절차

1. 긴급 분기 **Slack – Create a Message**  
2. **Channel type** = `Public channel`  
3. **Public channel** = **`새-채널`**  
4. 채널에 Make 봇 `/invite`  
5. Text 유지 → Save → 긴급 1건 → **`#새-채널`** 확인 (GIF와 동일 UI)

| 쓰지 않음 | 최종 사용 |
|-----------|-----------|
| DM / `im` / Private channel | **Public · `#새-채널`** |
| `***SLACK_TEAM_CHANNEL_ID***` 그대로 실행 | Make에서 실 채널 선택 |

### 7.4 실행 증거

| 증거 | 경로 | GIF에서 확인 |
|------|------|----------------|
| Slack `#새-채널` + Make 메시지 | `gif/make_urgent_3_slack.gif` | 채널명·Make 앱·긴급 본문 |
| 긴급 시트 + 시나리오 | `gif/make_urgent_2_action.gif` | Router 긴급 경로 |

---

## 관련 경로

| 경로 | 설명 |
|------|------|
| `../미션.txt` | 프로젝트 2 요구·보너스·제약 원문 |
| `../README.md` | 저장소 전체 진행 상태 |
| `gif/` | 실행 증명 GIF |
| `make/README.md` | Import·Slack 재매핑 상세 |
| `../report/` | 프로젝트 1 비교 보고서 (제출본) |
| `../project1/make/`, `../project1/n8n/` | 프로젝트 1 도구 산출물 (참고) |
