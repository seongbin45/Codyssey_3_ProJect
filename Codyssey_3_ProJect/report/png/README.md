# 보고서 GIF 자산

## Make — 완료 ✅

원본: 프로젝트 루트 `.png/`  
복사본·별칭: 이 폴더

| 별칭 (보고서 링크) | 원본 |
|--------------------|------|
| `make_high_1_form.gif` | `고액_지출_1_폼_양식_응답.gif` |
| `make_high_2_action.gif` | `고액_지출_2_실제_에이전트_액션.gif` |
| `make_normal_1_form.gif` | `일반_지출_1_폼_양식_응답.gif` |
| `make_normal_2_action.gif` | `일반_지출_2_실제_에이전트_액션.gif` |
| `make_review_1_form.gif` | `기타_지출_1_폼_양식_응답.gif` |
| `make_review_2_action.gif` | `기타_지출_2_실제_에이전트_액션.gif` |

## n8n — 실행(분기) 촬영 필요 ⬜

| 파일명 | 내용 |
|--------|------|
| `n8n_workflow_overview.gif` | 캔버스 전체 |
| `n8n_run_high.gif` | 고액 실행 end-to-end |
| `n8n_run_normal.gif` | 일반 실행 |
| `n8n_run_review.gif` | 미분류 실행 |

## n8n — 설치·OAuth 마찰 ✅ (로그 기반 생성)

세션 터미널 로그·실측 OAuth 오류 문구로 재구성 (`_render_setup_friction.py`).

| 파일 | 내용 |
|------|------|
| `n8n_setup_or_oauth.gif` / `.png` | 6장면 스토리보드 |
| `n8n_friction_01_windows_sdk_missing.png` | SDK 부재 node-gyp 에러 |
| `n8n_friction_02_sdk_and_nodegyp_fix.png` | SDK 설치 + gyp11 |
| `n8n_friction_03_n8n_ready.png` | localhost:5678 기동 |
| `n8n_friction_04_oauth_client_not_found.png` | OAuth client not found |
| `n8n_friction_05_oauth_test_users.png` | 테스트 사용자 403 |
| `n8n_friction_06_credentials_connected.png` | credential 이중 연결 |

재생성: `python report/gifs/_render_setup_friction.py` (Python 3.12 + Pillow)

녹화 시 이메일·시트 URL·API 키 마스킹.
