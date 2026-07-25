# 실행 증명 GIF (Make · n8n)

비교 보고서(`report/…`)가 참조하는 **영문 파일명** 미디어 폴더.

| 접두어 | 도구 | 분기 패턴 |
|--------|------|-----------|
| `make_*` | Make.com | `{high\|normal\|review}_{1_form\|2_action}.gif` |
| `n8n_*` | n8n self-host | 동일 패턴 |

## Make (6)

| 파일 | 내용 |
|------|------|
| `make_high_1_form.gif` / `make_high_2_action.gif` | 고액 |
| `make_normal_1_form.gif` / `make_normal_2_action.gif` | 일반 |
| `make_review_1_form.gif` / `make_review_2_action.gif` | 미분류(기타) |

## n8n (6)

원본 한글 녹화: `../n8n_gif/` (파일명 혼동 주의 → 그 폴더 README 참고).

| 파일 | 검증 입력 (2026-07-25) | 결과 탭 |
|------|------------------------|---------|
| `n8n_high_1_form.gif` / `n8n_high_2_action.gif` | 테스트 노트북 200000원 | 고액 지출 분류 결과 |
| `n8n_normal_1_form.gif` / `n8n_normal_2_action.gif` | 마트에서 식용유 5800원 | 일반 지출 분류 결과 |
| `n8n_review_1_form.gif` / `n8n_review_2_action.gif` | 분류 잘 모르겠음 -5000 | 검토 필요 |

워크플로우 정지 캡처: `../n8n/n8n_workflow_view.png`, `../make/Make_workflow_view.jpeg`
