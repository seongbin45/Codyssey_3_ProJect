# project2/make/ — Make.com 산출물 (프로젝트 2)

**주제:** FinFit 팀 문의/피드백 자동 분류  
**도구:** Make.com · 설계: `../design.md`

## 파일 목록

| 파일 | 설명 |
|------|------|
| `FinFit_inquiry_auto_triage.blueprint.json` | **Make Import Blueprint** — 시나리오 전체 (Trigger→OpenAI→Router 2갈래→Sheets±Email) |
| `README.md` | 본 안내 (Import 절차·시트 준비) |
| `../_build_blueprint.py` | Blueprint 재생성 스크립트 (프로젝트1 Blueprint 기반) |

## Make에 바로 올리기 (Import)

1. [Make.com](https://www.make.com) 로그인  
2. **Scenarios → Create a new scenario** (또는 빈 시나리오)  
3. 하단 메뉴 **… (More) → Import Blueprint**  
4. `FinFit_inquiry_auto_triage.blueprint.json` 선택 → Save  
5. 아래 **재매핑** 후 **Run once** / 스케줄 ON  

> Connection ID·시트 ID는 플레이스홀더(`***…***`)이거나 프로젝트1 계정의 옛 ID일 수 있다. **반드시 본인 연결·시트로 다시 고른다.**

## Import 후 필수 재매핑

| 모듈 | 할 일 |
|------|--------|
| **1. Google Forms – Watch Responses** | 문의 폼의 **응답 스프레드시트** + 시트 `Form Responses 1` 선택. Google connection 연결 |
| **2. OpenAI – Create a Completion** | OpenAI connection 연결. 모델 `gpt-4.1` / `json_object` / parse JSON 유지 |
| **3. Router** | 필터 확인: `{{2.result.urgency}}` = `긴급` / `일반` |
| **4. Google Sheets – Add a Row (긴급 문의)** | 결과 스프레드시트 + 탭 **「긴급 문의」** |
| **5. Email – Send an Email** | 수신 주소(To)를 담당자 메일로. Email/Gmail connection 연결. Slack 쓰면 이 모듈을 Slack으로 교체 가능 |
| **6. Google Sheets – Add a Row (일반 문의)** | 동일 결과 스프레드시트 + 탭 **「일반 문의」** |

## 시트·폼 준비 (Import 전 권장)

### 문의 접수 폼 (Google Forms)

| 항목 | 권장 |
|------|------|
| 제목 | FinFit 문의 접수 (또는 동일) |
| 질문 B (장문) | **문의 내용** (필수) |
| 질문 C (단문, 선택) | 연락처/이메일 |
| 응답 시트 | 폼 응답 → 스프레드시트 연결 (Trigger 대상) |

### 결과 스프레드시트

탭 2개 생성, **1행 헤더**:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 타임스탬프 | 원본 문의 | 긴급도 | 카테고리 | 요약 | 연락처 |

- 탭 이름 정확히: **`긴급 문의`**, **`일반 문의`** (Blueprint `sheetId`와 일치)

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
