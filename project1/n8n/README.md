# n8n/ — 도구 B (n8n Self-hosted) 산출물

프로젝트 1 **도구 B: n8n** 최종 워크플로·설계 기록·패치/빌드 스크립트·캔버스 캡처를 둔다.  
로컬 실행 본체(`n8n-runtime/`, `n8n-local/` 등)는 **gitignore 커밋 제외**이며, 그 안에는 **README를 두지 않는다.**  
이 `n8n/` 폴더에는 재현 가능한 산출물(워크플로 JSON·설계·스크립트)만 둔다. 로컬 기동 안내는 아래·`n8n_워크플로우_설계.md`를 본다.

| 항목 | 내용 |
|------|------|
| 역할 | Make와 동일 구조의 지출 메모 자동 분류 파이프라인 재현 |
| 런타임 | 로컬 Node (`npx n8n` / `n8n-runtime`), UI `http://localhost:5678` |
| 설치 | 아래 **「로컬 설치 · 기동」** — Node + Windows SDK + **node-gyp 11** 권장 경로 (실측 오류 포함) |
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

---

## 로컬 설치 · 기동 (Windows · 권장 경로)

이 과제의 n8n은 **Docker 없이 Node.js + npm** 으로 설치했다.  
런타임 폴더 `n8n-runtime/` 은 용량이 커서 **gitignore** 이며, 그 안에는 README를 두지 않는다.  
설치·오류 해결 기록의 원문 로그는 `n8n_워크플로우_설계.md` · 시각 자료는 `n8n_png/` 를 본다.

---

### ⚠ 중요: Visual Studio 2022만으로는 부족했다

| 오해 | 실제 (본 과제 실측) |
|------|---------------------|
| “VS 2022를 깔면 C++ 빌드가 된다” | **기본 설치만으로는** n8n 의존성(`isolated-vm`) 빌드에 필요한 **SDK·툴체인 구성 요소가 빠질 수 있다** |
| “VS Installer에서 Community를 설치했다” | **`--custom --add …` 로 SDK + VC Tools를 명시**하지 않으면 `gyp ERR! missing any Windows SDK` 가 난다 |
| “SDK까지 넣었으니 npm install 만 하면 된다” | n8n이 끌어오는 **node-gyp 8.x** 가 Windows 11 SDK 패키지 ID를 못 알아볼 수 있음 → **node-gyp 11 + 수동 rebuild** 가 추가로 필요했다 |

**다른 PC에서도 같은 패턴일 가능성이 높다.**  
아래 **필수 명령어 블록**을 순서대로 실행하는 것을 권장한다. (상세 설명은 B절 이하)

---

### ★ 필수 명령어 치트시트 (문제 해결에 필요했던 것)

> PowerShell에서 실행. 경로는 본인 클론 위치에 맞게 바꾼다.  
> **관리자 PowerShell** 이 안전할 때가 많다 (winget / 전역 npm).

#### ① Node.js (없으면 먼저)

- 설치: [https://nodejs.org](https://nodejs.org) **LTS** (실측: Node 25도 가능, engines는 ≥ 22)  
- 확인:

```powershell
node -v
npm -v
```

#### ② Visual Studio 2022 Community + **필수 구성 요소** (실측 명령)

> VS “껍데기”만 깔면 안 된다. **SDK + VC Tools 를 같이** 넣는다.

```powershell
winget install --id Microsoft.VisualStudio.2022.Community --exact --force --custom "--add Microsoft.VisualStudio.Component.Windows11SDK.22621 --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.VC.Tools.ARM64" --source winget
```

| 반드시 같이 넣는 구성 요소 | 역할 |
|---------------------------|------|
| `Windows11SDK.22621` | Windows 헤더/라이브러리 (없으면 **missing any Windows SDK**) |
| `VC.Tools.x86.x64` | MSVC C++ 컴파일러 (x64 빌드) |
| `VC.Tools.ARM64` | MSVC ARM64 툴 (환경에 따라 선택) |

#### ③ (여전히 SDK 오류면) Windows SDK 키트 추가

```powershell
winget install --id Microsoft.WindowsSDK.10.0.26100 -e
```

#### ④ **node-gyp 11** (VS·SDK 설치 후에도 거의 필수)

> 여기가 두 번째 함정. SDK가 있어도 **node-gyp 8** 이 “SDK 없음”으로 보고 빌드를 끊는다.

```powershell
npm install -g node-gyp@11.2.0
node-gyp -v
# → 11.x 여야 함
```

#### ⑤ n8n 설치 (전용 폴더)

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect
mkdir n8n-runtime -Force
cd n8n-runtime
if (-not (Test-Path package.json)) { npm init -y }

# 자동 빌드가 깨지는 경우가 많아 ignore-scripts 후 수동 재빌드 권장
npm install n8n@2.31.5 --no-fund --no-audit --ignore-scripts
```

#### ⑥ 네이티브 모듈 **수동 재빌드** (isolated-vm 등)

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime

# 오류 로그에 나온 패키지 폴더로 이동 후 (예: isolated-vm)
cd node_modules\isolated-vm
node-gyp rebuild
cd ..\..

# sqlite3 등도 동일하게
# cd node_modules\sqlite3
# node-gyp rebuild
# cd ..\..
```

실측에서 기동에 중요했던 예: **`isolated-vm`**, **`sqlite3`** (성공).  
일부 선택 패키지 실패는 기동에 지장 없을 수 있음.

#### ⑦ 기동

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime
npx n8n
# 브라우저: http://localhost:5678
```

#### 한 줄 요약

| 단계 | 없으면 생기는 일 |
|------|------------------|
| VS + **SDK + VC Tools** (②) | `missing any Windows SDK` / isolated-vm 빌드 실패 |
| **SDK 키트 추가** (③, 필요 시) | 여전히 SDK 경로·인식 문제 |
| **node-gyp 11** (④) | SDK 깔아도 node-gyp 8 이 SDK를 못 봄 |
| **node-gyp rebuild** (⑥) | `--ignore-scripts` 설치 후 네이티브 모듈 미빌드 상태 |

시각 요약: `n8n_png/n8n_friction_01_*.png` (SDK 부재) · `n8n_friction_02_*.png` (SDK + gyp11 재빌드).

---

### A. 한눈에 보는 권장 순서 (위 치트시트와 동일)

```text
1) Node.js 설치 (LTS · engines node >= 22 · 실측 Node 25)
2) winget VS 2022 Community + Windows11SDK.22621 + VC Tools   ← VS만 설치 ❌
3) (필요 시) WindowsSDK.10.0.26100 추가
4) npm i -g node-gyp@11                                     ← SDK 설치 후에도 필수에 가깝다
5) n8n-runtime 에 n8n@2.31.5 설치 (--ignore-scripts 권장)
6) isolated-vm / sqlite3 등 node-gyp rebuild
7) npx n8n → http://localhost:5678
8) owner 가입 → Credentials → 워크플로 Import
```

### B. Node.js 설치

1. [https://nodejs.org](https://nodejs.org) 에서 **LTS** 설치 (또는 본 과제 실측: Node **25.x**).  
2. 설치 시 **“Add to PATH”** 가 켜져 있는지 확인.  
3. **새** PowerShell 창에서 확인:

```powershell
node -v    # 예: v25.8.2  (22 이상이면 n8n 2.31 engines 충족)
npm -v
```

- `node` 를 못 찾으면 PATH 미적용 → 터미널을 닫았다 다시 열거나 Node를 재설치.  
- **Docker는 필수가 아님.** 본 프로젝트는 Docker 미설치 상태에서 진행했다.

### C. 우리가 겪은 오류와 원인 (실측)

#### 오류 1 — `missing any Windows SDK` (설치 실패의 핵심)

```text
npm error path ...\node_modules\isolated-vm
npm error gyp ERR! find VS - missing any Windows SDK
```

| 항목 | 내용 |
|------|------|
| 언제 | `npm install n8n` / `npx n8n` 최초 설치 시 |
| 왜 | n8n 의존성 **`isolated-vm`** 이 C++ **네이티브 모듈 컴파일**을 요구함 |
| 함정 | **VS 2022를 깔아도** SDK·VC Tools 구성 요소가 빠지면 **동일 오류**. “VS 있음 = 빌드 가능”이 아님 |
| 해결 명령 | 위 **★ 치트시트 ②** (필요 시 **③**) |
| 증거 이미지 | `n8n_png/n8n_friction_01_windows_sdk_missing.png` |

#### 오류 2 — SDK·VS 준비 후에도 같은 메시지 (node-gyp 버전)

| 항목 | 내용 |
|------|------|
| 언제 | VS + Windows11SDK.22621 / WindowsSDK 10.0.26100 설치 **이후** 재시도 |
| 왜 | n8n 의존 트리가 끌어오는 **node-gyp 8.4.1** 은 VS 패키지 ID `Windows10SDK.*` 위주만 인식. `Windows11SDK.22621` 등은 *missing any Windows SDK* 로 무시할 수 있음 |
| 해결 명령 | 위 **★ 치트시트 ④ + ⑥** (`node-gyp@11` + `node-gyp rebuild`) |
| 증거 이미지 | `n8n_png/n8n_friction_02_sdk_and_nodegyp_fix.png` |

#### 기타 (설치 중 부수적으로 나올 수 있음)

| 증상 | 해석 |
|------|------|
| `EBUSY` / `EPERM` (파일 잠금) | 백신·다른 터미널이 `node_modules` 를 잠금. 관련 node 프로세스 종료 후 재시도 |
| `cpu-features` / `better-sqlite3` 일부 실패 | 선택적 의존성. 실측에서 **기동에는 지장 없음** (필수: `isolated-vm`, `sqlite3` 등 성공) |

### D. 권장 설치 절차 (Windows PowerShell · 재현용)

관리자 권한이 필요한 단계는 winget/VS 설치뿐이다. 나머지는 일반 사용자 권한으로 가능하면 그렇게 한다.

#### 1) Visual Studio 2022 Community + C++ 도구 + Windows 11 SDK (winget · 실측)

본 과제는 **PowerShell에서 winget 한 줄**로 VS 2022 Community와 네이티브 빌드에 필요한 구성 요소를 설치했다.

```powershell
winget install --id Microsoft.VisualStudio.2022.Community --exact --force --custom "--add Microsoft.VisualStudio.Component.Windows11SDK.22621 --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.VC.Tools.ARM64" --source winget
```

| 옵션·구성 요소 | 의미 |
|----------------|------|
| `Microsoft.VisualStudio.2022.Community` | Visual Studio 2022 Community |
| `--exact --force` | 패키지 ID 정확 매칭·재설치/덮어쓰기 허용 |
| `Windows11SDK.22621` | Windows 11 SDK (10.0.22621) — node-gyp / 네이티브 빌드용 |
| `VC.Tools.x86.x64` | MSVC C++ 도구 (x86/x64) |
| `VC.Tools.ARM64` | MSVC C++ 도구 (ARM64, 선택적으로 포함) |
| `--source winget` | winget 원본 저장소 지정 |

설치 후 **새 PowerShell** 을 열고, VS Installer에서 구성 요소가 들어갔는지 확인해도 된다.

> **참고:** 이후 빌드 로그에서 SDK를 못 찾는 경우, 별도로 Windows SDK 10.0.26100 을 추가 설치하기도 했다 (아래 2).  
> VS에 넣은 `Windows11SDK.22621` 만으로는 **구형 node-gyp 8** 이 패키지를 인식하지 못해 오류 2가 이어질 수 있다 → **node-gyp 11** 필수.

#### 2) (필요 시) Windows SDK 추가 설치 (winget)

VS 설치 후에도 `missing any Windows SDK` 가 남거나, 키트 경로를 확실히 맞추고 싶을 때:

```powershell
winget install --id Microsoft.WindowsSDK.10.0.26100 -e
```

설치 후 확인 예:

- `C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um\windows.h` 존재 여부  
- 또는 `...\Include\10.0.22621.0\um\windows.h` (Windows11SDK.22621 경로)

#### 3) node-gyp 11 (전역)

```powershell
npm install -g node-gyp@11.2.0
node-gyp -v    # 11.x 인지 확인
```

#### 4) n8n 전용 폴더에 설치 (권장: 저장소 루트의 `n8n-runtime`)

```powershell
# 저장소 루트 (본인 클론 경로로 변경)
cd C:\Users\seong\Downloads\Codyssey_3_ProJect

mkdir n8n-runtime -Force
cd n8n-runtime

# package.json 이 없으면 최소 생성
if (-not (Test-Path package.json)) {
  npm init -y
}

# 스크립트 자동 빌드가 깨질 수 있어, 본 과제에서는 ignore-scripts 후 수동 재빌드 경로를 권장
npm install n8n@2.31.5 --no-fund --no-audit --ignore-scripts
```

#### 5) 네이티브 모듈 수동 재빌드 (핵심)

설치 직후 `isolated-vm` 등이 비어 있거나 이전 실패 잔여물이 있으면, **node-gyp 11** 로 다시 빌드한다.

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime

# 예시: isolated-vm (경로·버전 폴더는 node_modules 안 실제 이름에 맞춤)
cd node_modules\isolated-vm
node-gyp rebuild
cd ..\..

# sqlite3 등 추가 네이티브 모듈도 동일하게 rebuild
# cd node_modules\sqlite3
# node-gyp rebuild
```

본 과제에서 재빌드 성공으로 기동에 필요했던 예: `isolated-vm`, `sqlite3`, `@sentry/node-native-stacktrace` 등.

> PowerShell 한 줄로 패키지 폴더를 찾아 재빌드하는 방법은 환경마다 다르다.  
> 실패 시 오류 전문의 `path ...\node_modules\패키지명` 을 보고 그 디렉터리에서 `node-gyp rebuild` 한다.

#### 6) 기동

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime
npx n8n
```

### E. 정상 기동 시 터미널 로그 (실측 요지)

| 로그 | 의미 |
|------|------|
| `Initializing n8n process` | 프로세스 시작 |
| `n8n ready on ::, port 5678` | HTTP 에디터 포트 바인딩 |
| `n8n Task Broker ready on 127.0.0.1, port 5679` | 내부 태스크 브로커 |
| `Version: 2.31.5` | 본 프로젝트 검증 버전 |
| `Editor is now accessible via:` **`http://localhost:5678`** | 브라우저 접속 URL |
| `Press "o" to open in Browser.` | 터미널에서 `o` 로 브라우저 열기 가능 |

증거 이미지: `n8n_png/n8n_friction_03_n8n_ready.png`

브라우저에서 **http://localhost:5678** → 최초 **owner 계정 생성** → 로그인.

### F. 기동은 되지만 무시해도 되는 경고 (실측)

| 메시지 | 해석 |
|--------|------|
| `Failed to start Python task runner in internal mode... virtual environment is missing` | Python 러너 미구성. **JS 워크플로(본 과제)는 동작**. 프로덕션은 external mode 권장 안내 |
| `N8N_UNVERIFIED_PACKAGES_ENABLED` 등 deprecations | 향후 기본값 변경 예고. 당장 기동 실패 원인 아님 |
| `Running n8n outside a container is deprecated` | 장기적으로 Docker 권장. 본 과제는 Node/`npx` 로컬 기동으로 수행 |
| `[license SDK] Skipping renewal...` | 커뮤니티/로컬 라이선스 미초기화 — 일반적 |
| `DeprecationWarning: util._extend` | Node 쪽 의존성 경고 — 무시 가능 |

### G. 워크플로 불러오기 · 실행

**전제:** 프로젝트 1 **폼·응답 시트·결과 시트**가 이미 있어야 한다 (`../create_google_form_Project_1.js` 선행).

1. `http://localhost:5678` 로그인  
2. **Workflows → Import from File** → 이 폴더의 `n8n_지출_메모_자동_분류.workflow.json`  
3. Credentials 연결  
   - Google Sheets **Trigger** OAuth2  
   - Google Sheets OAuth2 (Append용 — Trigger와 **타입 분리**되는 경우가 있음)  
   - OpenAI API  
4. 시트·탭을 **본인이 만든 문서**로 지정 (레포 JSON은 `***…***` 마스킹)  
5. **Active** ON 또는 Test / Executions 에서 분기 확인  
6. 종료: 터미널 `Ctrl+C`

OAuth 실패 사례(클라이언트 없음, 테스트 사용자 403 등) 시각 자료:  
`n8n_png/n8n_friction_04_*.png` ~ `06_*.png`

### H. 빠른 점검표

| 확인 | 명령·방법 |
|------|-----------|
| Node | `node -v` (22+ 권장) |
| SDK | Windows Kits Include 경로에 `windows.h` |
| node-gyp | `node-gyp -v` → **11.x** |
| n8n 패키지 | `n8n-runtime\node_modules\n8n` 존재 |
| 기동 | `npx n8n` → `localhost:5678` |
| 트리거 | **`npx n8n` 프로세스가 떠 있는 동안만** Sheets 폴링 동작 |

### I. 대안: Docker (본 과제는 미사용)

공식은 컨테이너 배포를 권장한다. Docker Desktop + 공식 이미지로 올리면 네이티브 빌드 마찰을 줄일 수 있다.  
본 저장소 실측·보고서 「설정 난이도」는 **Windows + npm 경로의 마찰**을 그대로 기록하기 위해 **Docker 없이** 진행했다.

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
