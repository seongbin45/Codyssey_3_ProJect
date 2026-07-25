# n8n-runtime/ — 로컬 n8n 설치 (커밋 제외)

이 디렉터리는 **로컬에서 n8n을 실행하기 위한 설치 트리**다.  
`node_modules` 등 용량이 커서 **Git에 올리지 않는다** (루트 `.gitignore`).

| 항목 | 내용 |
|------|------|
| 목적 | `npx`/`npm` 기반 n8n 기동, Windows 네이티브 빌드 산출물 보관 |
| 커밋 | ❌ 저장소 미포함 |
| 재현 | 워크플로 JSON은 `../n8n/n8n_지출_메모_자동_분류.workflow.json` |

## 보통 포함되는 것 (로컬)

| 항목 | 설명 |
|------|------|
| `package.json` / lock | n8n 버전 고정 |
| `node_modules/` | 의존성 (수 GB 가능) |
| `.n8n/` 등 | 로컬 DB·자격증명 (절대 커밋 금지) |

## 기동 (예시)

```text
cd n8n-runtime
npx n8n
# → http://localhost:5678
```

Windows에서 `isolated-vm` 빌드 실패 시 Windows SDK + node-gyp 11이 필요할 수 있다.  
증거 이미지: `../png/n8n_friction_0*.png`, 서술: `../n8n/n8n_워크플로우_설계.md`.

## 관련 경로

| 경로 | 설명 |
|------|------|
| `../n8n/` | Export 워크플로·패치 스크립트 (커밋됨) |
| `../n8n-local/` | 별도 실험용 로컬 트리 (역시 gitignore) |
| `../.gitignore` | 이 폴더 제외 규칙 |
