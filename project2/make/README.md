# project2/make/ — Make.com 산출물 (프로젝트 2)

**주제:** FinFit 팀 문의/피드백 자동 분류  
**도구:** Make.com · 설계: `../design.md`

## 파일 목록

| 파일 | 설명 | Git |
|------|------|-----|
| `FinFit_inquiry_auto_triage.blueprint.json` | 공개용 Blueprint (시트 ID **마스킹**) | ✅ 커밋 |
| `FinFit_inquiry_auto_triage.LOCAL.blueprint.json` | **실 ID 채운 Import용** (Apps Script 로그 반영) | ❌ gitignore |
| `local_ids.json` | 폼·시트 URL/ID 로컬 메모 | ❌ gitignore |
| `README.md` | 본 안내 | ✅ |
| `../_build_blueprint.py` | 마스킹 Blueprint 재생성 | ✅ |

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

### Import 후 필수 재매핑

| 모듈 | 할 일 | 로그/로컬 값 |
|------|--------|----------------|
| **1. Google Forms – Watch Responses** | Google 연결 · Spreadsheet = **폼 응답 시트** · Sheet = `Form Responses 1` | 로그 ① 응답 시트 URL의 `/d/{ID}/` |
| **2. OpenAI – Create a Completion** | OpenAI connection · `json_object` · parse JSON 유지 | 프로젝트1과 동일 계정 가능 |
| **3. Router** | 필터: `{{2.result.urgency}}` = `긴급` / `일반` | 수정 불필요(이미 설정) |
| **4. Sheets – 긴급 문의** | Spreadsheet = **결과 시트** · 탭 **`긴급 문의`** | 로그 ③ 결과 시트 URL |
| **5. Email – Send an Email** | To = 담당자 메일 · Email/Gmail connection | 직접 입력 (Slack 대체 가능) |
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
       ├─ urgency = "긴급" → [4] Sheets「긴급 문의」 + [5] Email 알림
       └─ urgency = "일반" → [6] Sheets「일반 문의」만
```

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
