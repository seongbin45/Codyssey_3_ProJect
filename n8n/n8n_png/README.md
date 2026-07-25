# n8n_png/ — n8n 설치·OAuth 마찰 미디어

실행 데모 GIF가 아니라, n8n **설치·빌드·Google OAuth 연결** 과정에서 겪은 마찰을  
로그 문구 기반으로 재구성한 **정지 패널 + 스토리보드 애니메이션**을 둔다.  
비교 보고서의「설정 난이도」근거 자료.

| 항목 | 내용 |
|------|------|
| 목적 | Self-host 무료의 대가(Windows SDK, node-gyp, OAuth)를 시각 증거로 남김 |
| 폰트 | Windows 맑은 고딕 (`malgun.ttf`) — 한글 깨짐 방지 |
| 실행 GIF 위치 | `../../make/make_gif/` (이 폴더 아님) |

## 파일 목록

### 생성 스크립트

| 파일 | 설명 |
|------|------|
| `_render_setup_friction.py` | 6장면 PNG + 합본 GIF/PNG 재생성. Pillow 사용, 맑은 고딕 경로 탐색 |

### 스토리보드 (합본)

| 파일 | 설명 |
|------|------|
| `n8n_setup_or_oauth.gif` | 6장면 순환 애니메이션 |
| `n8n_setup_or_oauth.png` | 합본 또는 대표 정지본 |

### 장면별 정지 이미지 (01–06)

| 파일 | 로그·상황 출처 |
|------|----------------|
| `n8n_friction_01_windows_sdk_missing.png` | `isolated-vm` / missing Windows SDK |
| `n8n_friction_02_sdk_and_nodegyp_fix.png` | winget SDK 설치 → node-gyp 11 재빌드 |
| `n8n_friction_03_n8n_ready.png` | n8n 기동·owner 가입 완료 |
| `n8n_friction_04_oauth_client_not_found.png` | OAuth client not found / 접근 차단 |
| `n8n_friction_05_oauth_test_users.png` | 테스트 사용자·동의 화면 이슈 |
| `n8n_friction_06_credentials_connected.png` | Sheets Trigger + Sheets Append + OpenAI 연결 완료 |

## 재생성

```text
py -3.12 n8n/n8n_png/_render_setup_friction.py
```

출력 경로: **이 폴더(`n8n_png/`)**. 스크립트 수정 후 장면 문구를 바꾸면 보고서 캡션과 맞는지 확인한다.

## 관련 경로

| 경로 | 설명 |
|------|------|
| `../n8n_워크플로우_설계.md` | 설치·OAuth 서술형 기록 |
| `../../report/…보고서.md` | 마찰 GIF/PNG 임베드 |
| `../../make/make_gif/` | 실행(런타임) 증명 GIF |
