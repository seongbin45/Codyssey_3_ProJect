# project2/make/ — Make.com 산출물 (프로젝트 2)

**주제:** FinFit 팀 문의/피드백 자동 분류  
**도구:** Make.com · 설계: `../design.md`

## 파일 목록

| 파일 | 설명 | Git |
|------|------|-----|
| `FinFit_inquiry_auto_triage.blueprint.json` | 공개용 Blueprint (시트·Slack ID **마스킹**, Slack 본문 포함) | ✅ 커밋 |
| `../FinFit 팀 문의 피드백 자동 분류 (project2).blueprint.json` | Make Export 정리본 (동일 공개 마스킹) | ✅ 커밋 |
| `FinFit_inquiry_auto_triage.LOCAL.blueprint.json` | **실 ID** Import용 (로컬 전용) | ❌ gitignore |
| `local_ids.json` | 폼·시트 URL/ID 로컬 메모 | ❌ gitignore |
| `README.md` | 본 안내 | ✅ |
| `../_normalize_export_blueprint.py` | Export → 수정·마스킹 재생성 | ✅ |
| `../_build_blueprint.py` | 초기 생성 스크립트 (참고) | ✅ |
| `../create_google_form_Project_2.js` | 문의 폼·결과 시트 생성 Apps Script | ✅ |

## 리소스 준비 상태 (2026-07-26 Apps Script 로그 기준)

| 순서 | 로그 항목 | Make에서 쓸 곳 | ID 위치 |
|------|-----------|----------------|---------|
| 1 | 폼 응답 시트 URL | 모듈 1 Spreadsheet | `local_ids.json` → `response_sheet_id` |
| 2 | 폼 편집 / 응답(공유) URL | 테스트 제출용 (시나리오 밖) | `form_edit_id` / viewform |
| 3 | 결과 시트 URL (탭: 긴급 문의 / 일반 문의) | 모듈 4·6 Spreadsheet | `result_sheet_id` |

> 실제 ID·URL은 **채팅 로그 / `local_ids.json` / `.LOCAL.blueprint.json`** 에만 둔다. 공개 레포·커밋에는 넣지 않는다.

## Make에 올리기 (권장: LOCAL Blueprint)

1. [Make.com](https://www.make.com) 로그인  
2. **Scenarios → Create a new scenario**  
3. **… → Import Blueprint**  
4. **`FinFit_inquiry_auto_triage.LOCAL.blueprint.json`** 선택 (없으면 공개용 JSON + 아래 재매핑)  
5. Connection 연결 후 **Run once** · 스케줄 ON  

> **Module Not Found (`email:ActionSendEmail`)**  
> 구 Blueprint의 기본 Email 앱이 계정/리전에 없으면 빨간 `!` 가 뜬다.  
> 현재 Blueprint는 **Gmail – Send an Email** 로 바꿔 두었다.  
> 이미 Import한 시나리오면: 빨간 모듈 삭제 → **+** → **Gmail** → **Send an Email** 추가 후  
> To / 제목 / 본문에 `{{2.result.*}}`, `{{1.1}}` 매핑. 알림 없이 가려면 모듈만 지워도 됨(긴급 시트 기록은 유지).

### Import 후 필수 재매핑

| 모듈 | 할 일 | 로그/로컬 값 |
|------|--------|----------------|
| **1. Google Forms – Watch Responses** | Google 연결 · Spreadsheet = **폼 응답 시트** · Sheet = `Form Responses 1` | 로그 ① 응답 시트 URL의 `/d/{ID}/` |
| **2. OpenAI – Create a Completion** | OpenAI connection · `json_object` · parse JSON 유지 | 프로젝트1과 동일 계정 가능 |
| **3. Router** | 필터: `{{2.result.urgency}}` = `긴급` / `일반` | 수정 불필요(이미 설정) |
| **4. Sheets – 긴급 문의** | Spreadsheet = **결과 시트** · 탭 **`긴급 문의`** | 로그 ③ 결과 시트 URL |
| **5. Slack – Create a Message** | Slack 연결 · **팀 채널(공개/비공개)** · Text 템플릿 | **DM(`im`/slackbot) 사용 안 함.** 아래「Slack 팀 채널」참고 |
| **6. Sheets – 일반 문의** | 동일 결과 시트 · 탭 **`일반 문의`** | 로그 ③ |

**LOCAL Blueprint** 를 쓰면 1·4·6의 시트 ID는 이미 채워져 있어 **Connection 선택 + Email To** 만 하면 된다.  
UI에서 시트가 안 보이면 Spreadsheet를 한 번 다시 고르거나 ID 붙여넣기 모드를 사용한다.

## 시트·폼 스펙 (이미 생성됨)

### 문의 접수 폼

| 항목 | 내용 |
|------|------|
| 질문 B (장문) | **문의 내용** → Blueprint `{{1.1}}` |
| 질문 C (선택) | 연락처 → `{{1.2}}` |
| 응답 시트 | Trigger 대상 · 탭 보통 `Form Responses 1` |

### 결과 스프레드시트

탭: **`긴급 문의`**, **`일반 문의`** · 헤더 권장:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 타임스탬프 | 원본 문의 | 긴급도 | 카테고리 | 요약 | 연락처 |

## 시나리오 구조 (Blueprint 내용)

```text
[1] google-forms:watchRows     문의 폼 응답 폴링
  → [2] openai-gpt-3:CreateCompletion   JSON { urgency, category, summary }
  → [3] builtin:BasicRouter
       ├─ urgency = "긴급" → [4] Sheets「긴급 문의」 + [5] Slack Create a Message
       └─ urgency = "일반" → [6] Sheets「일반 문의」만
```

### Slack 팀 채널로 바꾸기 (DM → 공개/비공개 채널)

Blueprint 기본값: `channelType = public` (Make UI에서 **Private channel** 로 바꿀 수 있음).

**Make 시나리오에서 지금 고치기**

1. 긴급 분기 **Slack – Create a Message** 모듈 열기  
2. **Channel type**  
   - 공개 채널 → `Public channel`  
   - 비공개 채널 → `Private channel`  
   - **`Direct message` / `im` 사용하지 않음**  
3. **User (Channel ID) / Channel**  
   - 목록에서 팀 채널 선택 (예: `#finfit-alerts`, `#general`)  
   - 목록에 없으면 Slack에서 채널 생성 후, 봇을 **채널에 초대** (`/invite @make` 또는 앱 이름)  
4. **Text** 유지 (긴급 템플릿)  
5. Save → 긴급 테스트 1건 → 해당 채널에 메시지 확인  

| 이전 (동작은 했으나 데모용) | 목표 |
|---------------------------|------|
| `channelType: im` · ID `D…` (DM/slackbot) | `public` 또는 `private` · ID `C…` / `G…` (팀 채널) |

### Export 정리 시 고친 점

| 이슈 | 조치 |
|------|------|
| Slack `text` 비어 있음 | 긴급 알림 본문 템플릿 삽입 (`{{2.result.*}}`, `{{1.1}}`) |
| Slack DM(`im`) | 기본을 **팀 public 채널**로 변경, DM ID 제거 |
| `spreadsheetId` 슬래시 감싸기 | ID만 남김 → Sheets 404 방지 |
| 실 시트/채널 ID 공개 노출 | 공개 Blueprint는 `***…***` 마스킹 |

## Google Sheets `[404] Requested entity was not found` 점검

Make 로그에 **Origin: Google Sheets** / **404** 이면 거의 항상 **스프레드시트·탭을 못 찾은 것**이다 (OpenAI 모델 문제 아님).

| 순서 | 확인할 것 | 올바른 값 (Apps Script 생성 기준) |
|------|-----------|-----------------------------------|
| 1 | **Google connection** 이 시트를 연 계정과 같은가 | 폼/시트를 만든 Gmail |
| 2 | **Trigger(Watch)** Spreadsheet | 폼 **응답** 시트 (Apps Script 로그의 응답 시트 URL · `/d/`와 `/edit` 사이 ID) |
| 3 | Trigger **Sheet(탭) 이름** | 영어 UI: `Form Responses 1` · **한국어 UI면 `양식 응답 1`** → 드롭다운에서 **실제 탭 이름** 선택 |
| 4 | **Add a Row** Spreadsheet | **결과** 시트 (응답 시트와 **다른** 파일 · 로그의 결과 시트 URL) |
| 5 | Add a Row **Sheet** | 정확히 **`긴급 문의`** / **`일반 문의`** (띄어쓰기 포함) |
| 6 | Spreadsheet ID 입력 형식 | **ID만** 붙여넣기. `/ID/` 처럼 슬래시로 감싸지 말 것 |
| 7 | 브라우저에서 시트 열림 | 로그 URL이 404/권한 오류면 Make도 404 |

**한 번에 고치는 방법 (권장)**  
각 Google Sheets / Forms 모듈에서 Spreadsheet·Sheet 필드를 **지우고 → 목록에서 다시 고르기** (검색: `FinFit`).  
ID를 직접 붙여넣었다면 앞뒤 공백·슬래시를 제거한다.

**Run once 팁**  
Trigger가 “새 행”만 볼 때는 폼을 **한 건 제출한 뒤** Run once 하거나, Watch 모듈에서 기존 행을 수동 매핑한다.

## 테스트 (design.md §6)

| 입력 (문의 내용) | 기대 |
|------------------|------|
| 결제가 안 돼요, 지금 당장 필요해요 | 긴급 탭 + 이메일 |
| 다크모드 지원 언제 되나요? | 일반 탭만 |

## 보안

- 레포의 Blueprint에는 시트 ID·알림 메일을 `***…***` 로 둔다.  
- Export 다시 올릴 때 실제 ID·이메일이 들어오면 커밋 전 마스킹.  
- 계정 라벨 이메일은 `cho***45@…` 형태 유지.

## 관련 경로

| 경로 | 설명 |
|------|------|
| `../design.md` | 업무·선정 이유·스키마 |
| `../README.md` | 프로젝트2 진행 체크리스트 |
| `../../make/` | 프로젝트1 Make Blueprint (참고 원본) |
