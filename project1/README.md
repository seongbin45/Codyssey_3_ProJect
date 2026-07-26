# project1/ — 프로젝트 1: 지출 메모 자동 분류 (Make vs n8n)

Codyssey 미션 **[프로젝트 1]** 산출물만 모아 둔 폴더입니다.  
저장소 전체 입구·용어·재현 순서는 루트 [`../README.md`](../README.md) 를 먼저 보세요.

| 항목 | 내용 |
|------|------|
| 주제 | Google 폼 지출 메모 → AI 분류 → 고액/일반/검토 시트 |
| 도구 A | Make.com (`make/`) |
| 도구 B | n8n self-host (`n8n/`) |
| 비교 보고서 | `report/프로젝트1_자동화_도구_비교_분석_보고서.md` (**제출본**) |
| 상태 | 완료 |

## 이 폴더 안 지도

```text
project1/
├── README.md                         ← 지금 문서
├── create_google_form_Project_1.js   ← 폼·결과 시트 생성 (재현 시 1순위)
├── report/                           ← 비교 분석 보고서 + GIF 임베드
├── make/                             ← Make Blueprint·캔버스 캡처
├── n8n/                              ← n8n 워크플로 JSON·설계·마찰 이미지
│   ├── n8n_gif/                      ← 실행 녹화 원본(한글 파일명)
│   └── n8n_png/                      ← 설치·OAuth 마찰
└── gif/                              ← 보고서용 실행 GIF (영문 별칭 12개)
```

| 보고 싶은 것 | 경로 |
|--------------|------|
| 비교 보고서 | [`report/프로젝트1_자동화_도구_비교_분석_보고서.md`](./report/프로젝트1_자동화_도구_비교_분석_보고서.md) |
| Make Import | [`make/`](./make/) · [`make/README.md`](./make/README.md) |
| n8n Import·실행 | [`n8n/README.md`](./n8n/README.md) |
| 동작 GIF | [`gif/`](./gif/) |
| 폼 다시 만들기 | [`create_google_form_Project_1.js`](./create_google_form_Project_1.js) |

## 재현 순서 (중요)

```text
① 이 폴더의 create_google_form_Project_1.js 로 폼·시트 생성
② make/ 또는 n8n/ 워크플로 Import
③ 본인 시트·API 연결
④ 폼 테스트 제출
```

로컬 n8n 프로세스는 저장소 루트의 `n8n-runtime/` 에서 `npx n8n` (gitignore).  
상세 명령·로그 해석: [`n8n/README.md`](./n8n/README.md).

## 관련

| 경로 | 설명 |
|------|------|
| [`../README.md`](../README.md) | 저장소 전체 안내 |
| [`../미션.txt`](../미션.txt) | 미션 원문 |
| [`../project2/`](../project2/) | 프로젝트 2 (별개) |
