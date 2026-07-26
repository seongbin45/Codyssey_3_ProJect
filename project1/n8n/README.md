# n8n/ — 도구 B (n8n Self-hosted) 산출물

프로젝트 1 **도구 B: n8n** 최종 워크플로·설계 기록·패치/빌드 스크립트·캔버스 캡처를 둔다.  
로컬 실행 본체(`n8n-runtime/`, `n8n-local/` 등)는 **gitignore 커밋 제외**이며, 그 안에는 **README를 두지 않는다.**  
이 `n8n/` 폴더에는 재현 가능한 산출물(워크플로 JSON·설계·스크립트)만 둔다. 로컬 기동 안내는 아래·`n8n_워크플로우_설계.md`를 본다.

| 항목 | 내용 |
|------|------|
| 역할 | Make와 동일 구조의 지출 메모 자동 분류 파이프라인 재현 |
| 런타임 | 로컬 Node (`npx n8n` / `n8n-runtime`), UI `http://localhost:5678` |
| 트리거 | Google Forms 전용 노드 없음 → **Google Sheets Trigger** (응답 시트 Row Added) |

## 파일 목록

| 파일 | 설명 |
|------|------|
| `n8n_지출_메모_자동_분류.workflow.json` | **최종 워크플로 Export**. 노드: Google Sheets Trigger → OpenAI 파싱 → JSON 정규화(Code) → Switch/Router 3분기 → Sheets Append×3. 자격증명 ID는 로컬 전용 — Import 후 본인 Credentials 재연결 |
| `n8n_워크플로우_설계.md` | 도구 B 설계·설치 마찰·OAuth 이중 연결·분기 조건·트러블슈팅 기록 |
| `n8n_workflow_view.png` | n8n 에디터 캔버스 **정지 스크린샷** (전체 노드 배치) |
| `_build_n8n_workflow.mjs` | 워크플로 JSON을 코드로 조립·재생성할 때 쓰는 빌드 스크립트 (시스템 프롬프트·Code 노드 포함) |
| `_patch_n8n_append.mjs` | Append 미적재 이슈 대응 패치: `documentId` id 모드, `useAppend`, 컬럼 String 매핑, Code `runOnceForEachItem` 등 |
| `_review_results.mjs` | 결과 시트/실행 로그 스냅샷을 점검하는 보조 스크립트 |
| `README.md` | 본 안내 |

## 워크플로 구조

```text
Google Sheets Trigger1 (응답 시트 rowAdded)
  → OpenAI 파싱 (json_object)
  → JSON 정규화 (amount 숫자화, Classification 정리)
  → Router 3분기
       ├─ 고액 지출 기록  → 탭「고액 지출 분류 결과」
       ├─ 일반 지출 기록  → 탭「일반 지출 분류 결과」
       └─ 검토 필요 기록  → 탭「검토 필요」
```

| 분기 | 조건 |
|------|------|
| 고액 | `amount ≥ 50000` |
| 일반 | `amount < 50000` AND `Classification ≠ 분류불가` |
| 검토 | `amount = 0` AND `Classification = 분류불가` |

## Credentials (로컬만)

| 용도 | 타입 | 비고 |
|------|------|------|
| Trigger | Google Sheets **OAuth2** | 폴링용 |
| Append ×3 | Google Sheets **OAuth2** (별도 연결 가능) | Trigger와 타입/스코프 분리 이슈 문서화됨 |
| OpenAI | OpenAI API | 파싱 노드 |

시크릿·서비스 계정 JSON은 레포에 넣지 않는다 (`.gitignore`).

## 로컬 실행 방법 (Windows PowerShell · 실측)

런타임 디렉터리 `n8n-runtime/` 은 **gitignore** (대용량 `node_modules`).  
최초 1회 설치는 `n8n_워크플로우_설계.md` · friction 이미지(`n8n_png/`) 참고.  
아래는 **이미 `n8n@2.31.5` 가 설치된 뒤** 에디터를 띄우는 절차다.

### 1) 기동

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime
npx n8n
```

경로는 본인 PC의 클론 위치에 맞게 바꾼다.

### 2) 정상 기동 시 터미널에 보이는 것 (실측 로그 요지)

| 로그 | 의미 |
|------|------|
| `Initializing n8n process` | 프로세스 시작 |
| `n8n ready on ::, port 5678` | HTTP 에디터 포트 바인딩 |
| `n8n Task Broker ready on 127.0.0.1, port 5679` | 내부 태스크 브로커 |
| `Version: 2.31.5` | 본 프로젝트 검증 버전 |
| `Editor is now accessible via:` **`http://localhost:5678`** | 브라우저 접속 URL |
| `Press "o" to open in Browser.` | 터미널에서 `o` 로 브라우저 열기 가능 |

브라우저에서 **http://localhost:5678** 접속 → owner 로그인 → 워크플로 Import/Active.

### 3) 무시해도 되는 경고 (실측에서 동반됨)

기동은 되지만 아래 메시지가 뜰 수 있다. **에디터·워크플로 실행과 무관하거나 선택 사항**이다.

| 메시지 | 해석 |
|--------|------|
| `Failed to start Python task runner in internal mode... virtual environment is missing` | Python 러너 미구성. JS 워크플로(본 과제)는 동작. 프로덕션은 external mode 권장 안내 |
| `N8N_UNVERIFIED_PACKAGES_ENABLED` 등 deprecations | 향후 기본값 변경 예고. 당장 기동 실패 원인 아님 |
| `Running n8n outside a container is deprecated` | 장기적으로 Docker 권장. 본 과제는 Node/`npx` 로컬 기동으로 수행 |
| `[license SDK] Skipping renewal...` | 커뮤니티/로컬 라이선스 미초기화 — 일반적 |
| `DeprecationWarning: util._extend` | Node 쪽 의존성 경고 — 무시 가능 |

### 4) 워크플로 불러오기 · 실행

1. `http://localhost:5678` 로그인  
2. **Workflows → Import from File** → `n8n_지출_메모_자동_분류.workflow.json`  
3. Credentials 재연결 (Sheets Trigger OAuth2 / Sheets OAuth2 / OpenAI)  
4. 시트·탭 ID는 로컬 원본으로 매핑 (레포는 `***…***` 마스킹)  
5. **Active** ON 또는 **Test workflow** / Executions에서 분기 확인  
6. 종료: 터미널에서 `Ctrl+C`

### 5) 전제 (안 되면 먼저 볼 것)

- Node.js 설치됨 (`node -v`)  
- `n8n-runtime` 에 `n8n` 패키지 설치 완료 (실패 시 Windows SDK·node-gyp — `n8n_png/friction_*`)  
- **PC가 켜져 있고 `npx n8n` 프로세스가 떠 있어야** Sheets 폴링 트리거가 동작 (Make 클라우드와 다른 점)

## 실행 데모 GIF (이 폴더 밖)

| 경로 | 설명 |
|------|------|
| `n8n_gif/` | 한글 파일명 원본 + 매핑 README |
| `n8n_png/` | Windows SDK·OAuth 등 **설치 마찰** 이미지 |
| `../gif/n8n_*.gif` | 보고서용 영문 별칭 (내용 기준 매핑) |

## 스크립트 사용 (참고)

```text
# 저장소 루트에서
node project1/n8n/_build_n8n_workflow.mjs
node project1/n8n/_patch_n8n_append.mjs

# 또는 이 폴더(project1/n8n)에서
node _build_n8n_workflow.mjs
node _patch_n8n_append.mjs
```

공개 레포에서는 시트/폼 ID가 마스킹되어 있으므로, 로컬 원본 ID는 개인 환경에서만 복원한다.

## 관련 문서

| 경로 | 설명 |
|------|------|
| `../../README.md` | 저장소 전체 진행 상태 |
| `../report/프로젝트1_자동화_도구_비교_분석_보고서.md` | 비교 분석 (설정 난이도·마찰 포함) |
| `../make/` | 동일 파이프라인 도구 A |
| `../create_google_form_Project_1.js` | 프로젝트1 폼·결과 시트 생성 |
