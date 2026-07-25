# n8n/ — 도구 B (n8n Self-hosted) 산출물

프로젝트 1 **도구 B: n8n** 최종 워크플로·설계 기록·패치/빌드 스크립트·캔버스 캡처를 둔다.  
로컬 실행 본체(`n8n-runtime/` 등)는 **gitignore** — 이 폴더에는 재현 가능한 산출물만 둔다.

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

## 실행 데모 GIF (이 폴더 밖)

| 경로 | 설명 |
|------|------|
| `../make_gif/n8n_*.gif` | 보고서용 영문 별칭 (내용 기준 매핑) |
| `../n8n_gif/` | 한글 파일명 원본 + 매핑 README |
| `../png/` | Windows SDK·OAuth 등 **설치 마찰** 이미지 |

## 스크립트 사용 (참고)

```text
# 워크플로 재생성 (환경에 따라 경로·ID 수정 필요)
node n8n/_build_n8n_workflow.mjs

# Append 패치 적용
node n8n/_patch_n8n_append.mjs
```

공개 레포에서는 시트/폼 ID가 마스킹되어 있으므로, 로컬 원본 ID는 개인 환경에서만 복원한다.

## 관련 문서

| 경로 | 설명 |
|------|------|
| `../README.md` | 저장소 전체 진행 상태 |
| `../report/프로젝트1_자동화_도구_비교_분석_보고서.md` | 비교 분석 (설정 난이도·마찰 포함) |
| `../make/` | 동일 파이프라인 도구 A |
| `../create_google_form_Project_1.js` | 프로젝트1 폼·결과 시트 생성 |
