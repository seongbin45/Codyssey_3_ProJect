# make/ — 도구 A (Make.com) 산출물

프로젝트 1 **도구 A: Make.com** 시나리오 블루프린트와 캔버스 정지 이미지를 둔다.  
실행 중 화면 녹화(GIF)는 형제 폴더 `../make_gif/` 를 본다. 도구 B는 `../n8n/`.

| 항목 | 내용 |
|------|------|
| 역할 | 클라우드 SaaS로 동일 지출 분류 파이프라인 1차 구현 |
| 시나리오 흐름 | 응답 시트 폴링 → OpenAI JSON → Router 3분기 → Sheets Append×3 |
| 민감정보 | Blueprint·캡처 안 이메일·시트 ID는 레포에 노출되면 마스킹 |

## 파일 목록

| 파일 | 설명 |
|------|------|
| `Integration Google Forms, OpenAI (ChatGPT).blueprint.json` | Make **Import Blueprint** 용 시나리오 전체 내보내기. 모듈: Forms/Sheets Watch → OpenAI Chat(`json_object`) → Basic Router → Google Sheets Add a Row ×3(고액/일반/검토) |
| `Make_workflow_view.jpeg` | Make 시나리오 캔버스 **정지 스크린샷** (구성 한눈에 보기·보고서 보조) |
| `README.md` | 본 안내 |

## 시나리오 요약

```text
Google Forms / 응답 시트 폴링
  → OpenAI (gpt-4.1, json_object, parseJSONResponse)
  → Router
       ├─ 고액 (amount ≥ 50000)              → 탭「고액 지출 분류 결과」
       ├─ 일반 (amount < 50000 ∧ ≠분류불가) → 탭「일반 지출 분류 결과」
       └─ 미분류 (amount = 0 ∧ 분류불가)     → 탭「검토 필요」
```

헤더 6열(결과 시트): 타임스탬프 · 원본 메모 · 카테고리 · 금액 · 요약 · 특이사항

## Blueprint 가져오기

1. [Make.com](https://www.make.com) 로그인  
2. 시나리오 → **… → Import Blueprint**  
3. 이 폴더의 `.blueprint.json` 선택  
4. Google / OpenAI **Connection**을 본인 계정으로 재매핑  
5. 결과 시트·탭 이름이 프로젝트와 동일한지 확인  

> 제출·공유 시 Blueprint 안 계정 라벨·시트 ID가 보이면 마스킹한다. 공개 레포에는 ID 플레이스홀더(`***…***`) 정책을 따른다.

## 실행 데모 GIF (이 폴더 밖)

| 파일 | 내용 |
|------|------|
| `../make_gif/make_high_1_form.gif` | 고액 · 폼 응답 |
| `../make_gif/make_high_2_action.gif` | 고액 · 시나리오 액션 |
| `../make_gif/make_normal_1_form.gif` | 일반 · 폼 응답 |
| `../make_gif/make_normal_2_action.gif` | 일반 · 시나리오 액션 |
| `../make_gif/make_review_1_form.gif` | 미분류 · 폼 응답 |
| `../make_gif/make_review_2_action.gif` | 미분류 · 시나리오 액션 |

## 관련 문서

| 경로 | 설명 |
|------|------|
| `../미션.txt` | 미션 원문 |
| `../README.md` | 저장소 진행 상태 |
| `../report/프로젝트1_자동화_도구_비교_분석_보고서.md` | 비교 분석 보고서 |
| `../create_google_form.js` | 폼·결과 시트 생성 Apps Script |
| `../n8n/` | 동일 파이프라인 도구 B |
