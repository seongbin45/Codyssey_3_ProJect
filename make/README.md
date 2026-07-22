# make/ — 도구 A (Make.com) 산출물

프로젝트 1의 **도구 A: Make.com** 시나리오와 관련 자산을 둔다.  
도구 B(n8n) 산출물은 형제 폴더 `../n8n/` 을 본다.

## 포함 파일

| 파일 | 설명 |
|------|------|
| `Integration Google Forms, OpenAI (ChatGPT).blueprint.json` | Make 시나리오 내보내기(Blueprint). Trigger → OpenAI JSON 파싱 → Router 3분기 → Sheets Append×3 |
| `SERWMN5fwEF.jpeg` | Make 관련 참고/구성 이미지 (제출 시 계정·URL 노출 여부 확인 후 마스킹) |
| `README.md` | 본 안내 |

## 시나리오 요약

```text
Google Forms / 응답 시트 폴링
  → OpenAI (gpt-4.1, json_object)
  → Router
       ├─ 고액 (amount ≥ 50000)     → 탭「고액 지출 분류 결과」
       ├─ 일반 (미만 ∧ ≠분류불가)   → 탭「일반 지출 분류 결과」
       └─ 미분류 (0 ∧ 분류불가)     → 탭「검토 필요」
```

## Blueprint 가져오기

1. [Make.com](https://www.make.com) 로그인  
2. 시나리오 생성 → **… → Import Blueprint**  
3. 이 폴더의 `.blueprint.json` 선택  
4. Google / OpenAI 연결(Connection)을 본인 계정으로 다시 매핑  
5. 결과 시트·탭 이름이 프로젝트와 같은지 확인  

> 제출·공유 시 Blueprint 안 계정 라벨 이메일·시트 ID가 보이면 마스킹한다.

## 실행 데모 GIF

Make **실행 화면 GIF**는 확장자 구분을 위해 루트 `../gifs/` 에 둔다.

| 파일 | 내용 |
|------|------|
| `../gifs/make_high_1_form.gif` | 고액 · 폼 응답 |
| `../gifs/make_high_2_action.gif` | 고액 · 시나리오 액션 |
| `../gifs/make_normal_1_form.gif` | 일반 · 폼 응답 |
| `../gifs/make_normal_2_action.gif` | 일반 · 시나리오 액션 |
| `../gifs/make_review_1_form.gif` | 미분류(기타) · 폼 응답 |
| `../gifs/make_review_2_action.gif` | 미분류(기타) · 시나리오 액션 |

## 관련 문서

- 미션: `../미션.txt`
- 진행 상태: `../README.md`
- 비교 분석 보고서: `../report/프로젝트1_자동화_도구_비교_분석_보고서.md`
- 폼/시트 생성 스크립트: `../create_google_form.js`
