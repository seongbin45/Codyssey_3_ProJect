# gif/ — 프로젝트 2 실행 증명 GIF (Make)

FinFit 팀 문의/피드백 자동 분류 시나리오의 **폼 제출 + 실행 결과** 화면 증명.

| 항목 | 내용 |
|------|------|
| 도구 | Make.com only |
| 분기 | `urgent`(긴급) / `normal`(일반) |
| 명명 | `make_{분기}_{단계}.gif` |
| 원본 녹화 | `Videos/screen/` (로컬) → 여백 crop 후 `fixed/` → 본 폴더 GIF |
| 해상도 | 데스크톱 클립 가로 최대 960px · Slack 세로 클립 가로 480px |

## 명명 규칙

| 토큰 | 의미 |
|------|------|
| `make` | 도구 Make.com |
| `urgent` | 긴급 분기 (`urgency = 긴급`) |
| `normal` | 일반 분기 (`urgency = 일반`) |
| `1_form` | Google 문의 폼 입력·제출 |
| `2_action` | Make 시나리오 실행 + 결과 시트 확인 |
| `3_slack` | 긴급 Slack 알림 — **Public `#새-채널`** · Make 앱 메시지 |

## 파일 목록 (5)

| 파일 | 시연 내용 | 기대 결과 |
|------|-----------|-----------|
| `make_urgent_1_form.gif` | 긴급 문의 폼 작성·제출 | 응답 시트에 행 추가 |
| `make_urgent_2_action.gif` | Make 실행 → 긴급 경로 | 「긴급 문의」탭 기록 |
| `make_urgent_3_slack.gif` | Slack **`#새-채널`(공개)** 에서 Make 앱 긴급 메시지 | 헤더·본문에 `#새-채널` 표시 |
| `make_normal_1_form.gif` | 일반 문의 폼 작성·제출 | 응답 시트에 행 추가 |
| `make_normal_2_action.gif` | Make 실행 → 일반 경로 | 「일반 문의」탭만 · Slack 없음 |

> **설계 문서에서 보기:** 위 GIF는 [`../report/design.md`](../report/design.md) **§7** 에 Markdown으로 임베드되어 있다.  
> 채점·리뷰 시 GitHub에서 `report/design.md` 만 열면 구현 화면(§3.1) + 실행 GIF(§7)를 한 문서에서 확인할 수 있다.

## 변환 메모

- 원본 1920×1080 녹화에 **우측·하단 검은 여백**이 있어 crop 후 GIF화함 (내용 채움 ≈ 100%).
- palettegen / paletteuse (ffmpeg) · 데스크톱 fps 10 · Slack fps 8.
- 구현 화면(캔버스) 정지 이미지는 `../make/Make_workflow_view.jpeg` 또는 `../screen.png` 참고.

## 관련 경로

| 경로 | 설명 |
|------|------|
| [`../report/design.md`](../report/design.md) | 설계 + GIF 임베드 (GitHub 열람) |
| `../README.md` | 프로젝트 2 체크리스트 |
| `../make/` | Blueprint · Import 안내 |
| `../../project1/gif/` | 프로젝트 1 GIF 명명 참고 |
