# 도구 B: n8n — 워크플로우 설계 및 설치 계획

> 프로젝트 1 도구 B. Make.com과 **동일한 업무 로직**을 재현한다.  
> 도구 B 후보로 Zapier를 검토했으나 Free 플랜(Zap당 트리거 1 + 액션 1, Paths 불가)으로는 멀티스텝+3분기 구조를 재현할 수 없어 **n8n 셀프호스트**로 전환함.

---

## 0. 결정 배경 (보고서용 요약)

| 항목 | 내용 |
|---|---|
| 원래 후보 | Zapier |
| 전환 이유 | Free 플랜 2단계 제한 + Paths(조건 분기)는 Professional 이상 → 동일 워크플로우 재현 시 유료 불가피 |
| 선택 | n8n Self-hosted (완전 무료, IF/Switch 노드 사용 가능) |
| 미션 정합성 | “자가호스팅 가능한 도구 + 무료 연동 앱” 권장 예시와 일치 |
| 보고서 기재 | 유료가 불가피했던 대안(Zapier)과 무료 대안(n8n)을 비교 분석에 함께 정리 |

---

## 1. 전제 두 가지 (구현 전 반드시 숙지)

### 1-1. 무료의 대가는 설치 마찰

- Zapier/Make: 가입 후 브라우저에서 바로 캔버스 사용.
- n8n 셀프호스트: **로컬에 Node(또는 Docker) 환경을 띄운 뒤** 웹 UI(`http://localhost:5678`)에 접속.
- “무료 = 마찰 없이 빠르다”가 **아님**. 설치·최초 owner 계정 생성·자격 증명(OAuth) 연결 시간을 **계획에 포함**.
- 비교 보고서 **「설정 난이도」** 항목의 핵심 소재.

### 1-2. Google Forms 전용 트리거 노드 없음

- Make 쪽 표기 “Google Forms – Watch Rows”도 실질적으로는 **폼 응답이 쌓이는 스프레드시트 폴링**.
- n8n도 동일하게 **Google Sheets Trigger(새 행 감지, 폴링)** 로 응답 시트를 감시.
- 업무 흐름·데이터 소스는 동일 → “동일 워크플로우 재현” 요건 OK.
- 노드 UI/캡처 상의 이름은 **Google Sheets** 로 나온다 (Forms가 아님). 보고서에 “트리거 구현 방식”으로 명시.

---

## 2. Make ↔ n8n 노드 대응표

```
[Trigger] Google Sheets – Row Added (응답 시트 폴링)
      │
      ▼
[Action 1] OpenAI – Message a Model (또는 Chat Completions)
      │  메모 텍스트 → { category, amount, summary, Classification }
      ▼
[Switch / IF] 3-Way 조건 분기
      ├─ 분기 A: amount ≥ 50000              → Sheets Append (고액 지출 분류 결과)
      ├─ 분기 B: amount < 50000 AND Classification ≠ 분류불가 → Sheets Append (일반 지출 분류 결과)
      └─ 분기 C: amount = 0 AND Classification = 분류불가     → Sheets Append (검토 필요)
```

| 단계 | Make | n8n (예정) |
|---|---|---|
| Trigger | Google Forms Watch Rows (실체: 응답 시트 폴링) | **Google Sheets Trigger** – On row added (응답 시트) |
| AI 파싱 | OpenAI Chat Completion (JSON) | **OpenAI** – Message a model / Chat (JSON, 동일 시스템 프롬프트) |
| 조건 분기 | Router 3-way | **Switch** 노드 (권장) 또는 IF 체인 |
| 기록 A/B/C | Google Sheets Add a Row × 3 | **Google Sheets** – Append or update row × 3 (탭별) |

분기 조건·시스템 프롬프트는 README 4·5절과 **완전 동일**하게 맞춘다.

---

## 3. 로컬 환경 점검 결과 (2026-07-22 기준)

| 항목 | 상태 |
|---|---|
| Node.js | ✅ v25.8.2 (`C:\Program Files\nodejs\node.exe`) |
| npm / npx | ✅ 11.11.1 |
| Docker | ❌ 미설치 (`docker` 명령 없음) |
| n8n engines | `node >= 22.22` — Node 25는 버전 조건 충족 |
| VS 2022 Community | ✅ 설치됨 (VC++ toolset v143) |
| **Windows SDK** | ✅ **10.0.26100** (winget) + VS `Windows11SDK.22621` |

### 설치 시도 로그 (설정 난이도 보고 소재)

| 시도 | 결과 |
|---|---|
| `npx n8n` | ~7분 후 실패 (Windows 파일 잠금 EBUSY/EPERM + 하위 네이티브 빌드 실패) |
| `n8n-local`에 `npm install n8n@2.31.5` | ~8분 후 실패 |

**실제 차단 에러 (핵심):**

```text
npm error path ...\node_modules\isolated-vm
npm error gyp ERR! find VS - missing any Windows SDK
```

- n8n 의존 패키지 `isolated-vm` 이 **네이티브 모듈 컴파일**을 요구함.
- VS 2022는 있으나 **Windows SDK가 없어** `node-gyp` 빌드가 중단됨.
- 이는 사용자가 미리 짚은 **「무료의 대가로 설치 마찰」** 이 실제로 터진 사례. 비교 보고서 「설정 난이도」에 그대로 쓸 것.

### 설치 재개 결과 (경로 A 완료)

1. **Windows SDK 설치 완료**  
   `winget install Microsoft.WindowsSDK.10.0.26100` → 성공 (버전 10.0.26100.7705).  
   레지스트리·`Windows Kits\10\Include\10.0.26100.0\um\windows.h` 확인됨.

2. **추가 함정 (보고서 소재)**  
   n8n 의존성 빌드에 쓰이는 **node-gyp 8.4.1** 은 VS 패키지 ID 접두사 `Windows10SDK.*` 만 인식하고, `Windows11SDK.22621` 은 “missing any Windows SDK” 로 무시함.  
   → 해결: 전역 **node-gyp 11.2.0** 설치 후 `--ignore-scripts` 로 n8n 설치, 이어서 네이티브 모듈을 node-gyp 11로 수동 재빌드.

3. **런타임 위치**  
   `C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime` (n8n@2.31.5)  
   - 재빌드 성공: `isolated-vm`, `sqlite3`, `@sentry/node-native-stacktrace`  
   - (선택) `cpu-features` / `better-sqlite3` 는 실패·미사용 — 기동에는 지장 없음

4. **기동 확인**  
   ```
   n8n ready on ::, port 5678
   Editor is now accessible via: http://localhost:5678
   ```

```powershell
# 재기동 (이 터미널에서 n8n이 이미 돌고 있을 수 있음)
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime
npx n8n
# 브라우저: http://localhost:5678  → 최초 접속 시 owner 계정 생성
```

---

## 4. 구현 단계 (차근차근)

| # | 단계 | 상태 | 비고 |
|---|---|---|---|
| 1 | 도구 B 결정 (n8n) + 전제 문서화 | ✅ 본 문서 | Zapier 전환 사유 포함 |
| 2 | 로컬 환경 확인 | ✅ | Node OK, Docker 없음 |
| 2b | npm 설치 시도 | ⚠️ 차단이었음 | Windows SDK + node-gyp 11로 해소 (3절) |
| 3 | Windows SDK 설치 + n8n 기동 | ✅ | `http://localhost:5678` 접근 가능 |
| 3b | owner 계정 생성 (브라우저) | ✅ | 가입 완료 (2026-07-23) |
| 4 | Google 자격 증명 연결 | ✅ | Sheets Trigger OAuth2 **Account connected** (Client ID `814669…58s7`). SA 키는 예비(Append 대안) |
| 5 | OpenAI 자격 증명 연결 | 🔄 | 워크플로우에 포함 — Import 후 credential 선택 |
| 6 | 워크플로우 노드 조립 | ✅ **최종안** | `C:\Users\seong\Downloads\지출 메모 자동 분류 (n8n).json` = 프로젝트 `n8n_지출_메모_자동_분류.workflow.json` |
| 7 | 테스트 3종 + 분기별 1회 이상 실행 캡처 | ⬜ | 고액 / 일반 / 미분류(+0원 정상) |
| 8 | 워크플로우 JSON Export + 구성·실행 스크린샷 | ⬜ | 이메일·키·시트 ID 가림 |
| 9 | 비교 분석 보고서에 도구 B·설정 난이도·트리거 방식 반영 | ⬜ | |

---

## 5. 자격 증명·리소스 (민감정보 주의)

| 리소스 | 용도 | 비고 |
|---|---|---|
| 응답 스프레드시트 | Trigger 감시 대상 | 폼 제출이 쌓이는 시트 (Make와 동일 자산 재사용 권장) |
| 결과 스프레드시트 | 분기별 Append | 탭: 고액 / 일반 / 검토 필요 |
| Google OAuth (n8n) | Sheets 트리거·쓰기 | Cloud Console 클라이언트 필요할 수 있음 — 구현 시 단계별 기록 |
| OpenAI API Key | 파싱 Action | 제출물 마스킹 |

Make와 **같은 폼·같은 결과 시트**를 쓰면 비교가 공정하고, 리소스 중복 생성을 피한다.

---

## 6. 비교 보고서에 미리 넣을 소재 (초안 메모)

1. **설정 난이도**: Make = 클라우드 가입 즉시 / n8n = Node 기동 + 로컬 URL + (필요 시) Google Cloud OAuth 설정.
2. **트리거 표기 vs 실체**: 둘 다 Forms 응답을 Sheets 폴링으로 감지. n8n은 노드명이 Sheets로 노출.
3. **무료 범위**: Make 월 Ops 한도 있음 / n8n 셀프호스트 실행 횟수 제한 없음(대신 본인 PC 상시 기동 필요).
4. **조건 분기 UX**: Make Router vs n8n Switch — 시각적 분기 표현 차이.
5. **Zapier를 쓰지 않은 이유**: Free 2단계·Paths 유료 → 동일 구조 재현 불가, 무료 대안으로 n8n 선택.

---

## 7. 최종 워크플로우 (확정 + Append 안정화 패치)

**원본 파일:** `C:\Users\seong\Downloads\지출 메모 자동 분류 (n8n).json`  
**프로젝트 복사본:** `n8n_지출_메모_자동_분류.workflow.json`  
**패치 스크립트:** `_patch_n8n_append.mjs` (재적용 가능)

### Append가 안 쌓이던 원인 후보와 패치

| # | 원인 후보 | 패치 |
|---|---|---|
| 1 | `documentId.mode: list` — UI 캐시에 의존 | **`mode: id`** + 스프레드시트 ID 고정 |
| 2 | `useAppend` 없음 — 빈 행 탐색/업데이트 방식 실패 가능 | **`options.useAppend: true`** (values:append API) |
| 3 | 컬럼 매핑 표현식/타입 불안정 | 6열 **String()** 강제 + schema 재고정 + `convertFieldsToString: true` |
| 4 | Code가 `runOnceForAllItems` + `$input.first()` — 다건 시 1건만 처리 | **`runOnceForEachItem`** + 아이템 단위 파싱 |
| 5 | OpenAI `textFormat`이 빈 객체로 깨짐 | **`json_object` 복구**, user `role` 보정 |
| 6 | 탭 이름 | `고액 지출 분류 결과` / `일반 지출 분류 결과` / `검토 필요` 유지 |

결과 시트 ID: `***RESULT_SHEET_ID***`  
헤더 6열: `타임스탬프 | 원본 메모 | 카테고리 | 금액 | 요약 | 특이사항`

```
Google Sheets Trigger1 (Form Responses 1 / ***RESPONSE_SHEET_ID***)
  → OpenAI 파싱 (gpt-4.1, Make 시스템 프롬프트, user=지출 메모)
  → JSON 정규화 (Code — Trigger1 노드명 참조)
  → Router 3분기
       ├─ amount ≥ 50000              → 고액 지출 기록
       ├─ amount < 50000 ∧ ≠분류불가 → 일반 지출 기록
       └─ amount = 0 ∧ 분류불가      → 검토 필요 기록
```

| 노드 | Credential |
|---|---|
| Google Sheets Trigger1 | Google Sheets Trigger account |
| OpenAI 파싱 | OpenAI account |
| Append ×3 | Google Sheets account |

active: false (제출 전 테스트 시 수동/Active 전환)  
Make blueprint과 동일 시트·동일 분기·동일 프롬프트.

## 7b. 다음 액션 (제출 마감용)

- [ ] 고액/일반/미분류 각 1회 Executions + 결과 시트 행 확인·캡처  
- [ ] 비교 분석 보고서 도구 B 절 작성

---

## 8. 자격 증명 연결 가이드 (브라우저에서 수행)

> API Key·Client Secret은 채팅/문서/스크린샷에 넣지 말 것. 제출 시 마스킹.

### 8-1. OpenAI Credential

1. n8n → **Credentials → Add credential → OpenAI**
2. [platform.openai.com/api-keys](https://platform.openai.com/api-keys) → **Create new secret key**
3. 키를 n8n **API Key** 칸에만 입력 (채팅·Git·스크린샷 금지)
4. 이름: `OpenAI - expense parse` → Save
5. (선택) Make와 동일 키/조직 사용 시 분류 결과 비교가 공정함

### 8-1b. OpenAI 노드 — **Make 블루프린트 1:1 대응**

출처: `Integration Google Forms, OpenAI (ChatGPT).blueprint.json`  
Make 모듈: `openai-gpt-3:CreateCompletion` (id 3)

| Make | 값 | n8n |
|---|---|---|
| select | `chat` | OpenAI → Message a Model / Chat |
| model | **`gpt-4.1`** | 동일 |
| response_format | **`json_object`** | JSON / JSON Object 모드 ON |
| parseJSONResponse | **true** | 가능하면 자동 JSON 파싱 ON (없으면 다음 Code 노드) |
| temperature | `1` | 1 |
| max_tokens | `2048` | 2048 |
| system | 아래 원문 | System message |
| user | `{{2.\`1\`}}` = 폼 응답 **2번째 열(지출 메모)** | User ← Trigger의 메모 열 |

**System (Make 원문 그대로 — n8n에 복사):**

```text
당신은 지출 내역 분석 비서입니다. 사용자의 메모를 분석하여 반드시 아래 JSON 구조로만 응답하세요. 마크다운 기호(```)를 절대 포함하지 말고 순수 JSON 문자열만 출력하세요.

{
  "category": "식비, 교통비, 문화생활, 생필품, 기타, 분류불가 중 택1",
  "amount": "지출 금액을 0 이상의 정수로만 기재",
  "summary": "지출 내역을 10자 이내로 요약",
  "Classification": "분류 가능 여/부 표시"
}

분류 규칙:
1. 메모에서 금액을 명확히 추출할 수 있고 그 값이 0보다 크면, amount에 해당 숫자를 그대로 기재하고 category는 내용에 맞게 분류하세요.
2. 실제로 비용이 들지 않은 정당한 지출(예: "무료 쿠폰으로 커피 받음", "친구가 밥 사줌")은 amount를 0으로 기재하되, category는 "분류불가"가 아니라 내용에 맞는 정상 카테고리로 분류하세요.
3. 아래에 해당하는 경우에만 Classification를 "분류불가"로, amount는 0으로 기재하세요.
   - 금액이 음수로 표현된 경우 (예: "-1000", "마이너스 5000원")
   - 금액을 특정할 수 없거나 메모에 금액 자체가 없는 경우
   - 지출 내용과 금액의 연결이 불명확해 파싱을 신뢰할 수 없는 경우
```

**User (Make `{{2.\`1\`}}` 대응):**

```text
{{ $json['지출 메모'] }}
```

Make Trigger: 시트 `Form Responses 1`, 스프레드시트 `***RESPONSE_SHEET_ID***`  
→ n8n Trigger도 **같은 ID / 시트명 `Form Responses 1`**.  
열 매핑: Make `0`=타임스탬프, `1`=지출 메모.

Make는 `parseJSONResponse: true` 로 `3.result.amount` 등에 바로 접근.  
n8n에서 파싱이 안 되면 OpenAI 다음 **Code**:

```javascript
// OpenAI 노드 출력 키는 UI 미리보기에 맞게 조정
const item = $input.first().json;
const raw = item.message?.content ?? item.text ?? item.content ?? item;
const parsed = typeof raw === 'string' ? JSON.parse(raw) : (raw.message?.content ? JSON.parse(raw.message.content) : raw);
const trigger = $('Google Sheets Trigger').first().json; // 노드 표시명에 맞게 수정
return [{
  json: {
    timestamp: trigger['타임스탬프'] ?? trigger['Timestamp'] ?? Object.values(trigger)[0],
    memo: trigger['지출 메모'] ?? Object.values(trigger)[1],
    category: parsed.category,
    amount: Number(parsed.amount) || 0,
    summary: parsed.summary,
    Classification: parsed.Classification,
  }
}];
```

### 8-1c. Switch / Sheets — Make Router 1:1

결과 스프레드시트: `***RESULT_SHEET_ID***`

| Make 필터 이름 | 조건 | 탭(sheetId) | 열 매핑 |
|---|---|---|---|
| 고액지출(50000이상) | `amount >= 50000` | `고액 지출 분류 결과` | A 타임스탬프, B 원본메모, C category, D amount, E summary |
| 일반지출(50000미만) | `amount < 50000` **AND** `Classification != 분류불가` | `일반 지출 분류 결과` | 동일 |
| 미분류,누락 | `amount == 0` **AND** `Classification == 분류불가` | `검토 필요` | 동일 |

Make values: `0←trigger.ts`, `1←trigger.memo`, `2←result.category`, `3←result.amount`, `4←result.summary` (특이사항 F열은 비움).

### 8-2. Google Sheets 연동 (권장: 서비스 계정)

Cloud 현황 (2026-07-23 기준):
- 프로젝트: `codyssey-no-code-automation` (추정)
- **Sheets API: 사용 설정됨** ✅
- OAuth 2.0 클라이언트: **아직 없음**
- 서비스 계정: `n8n-local-expense@codyssey-no-code-automation.iam.gserviceaccount.com` ✅

Self-hosted n8n에서는 **서비스 계정**이 OAuth보다 단순한 경우가 많음 (브라우저 동의 화면·리디렉션 URI 불필요).  
Make는 “내 Google 로그인”, n8n 서비스 계정은 “봇 계정에 시트를 공유”하는 방식 — 비교 보고서 **설정 난이도** 소재.

#### 경로 S — 서비스 계정 (지금 단계 권장)

**S1. 키(JSON) 발급** (올바른 파일 형태 확인 필수)
1. Cloud Console → **IAM 및 관리자 → 서비스 계정**
2. `n8n-local-expense` 클릭 → **키** 탭 → **키 추가 → 새 키 만들기 → JSON**
3. 다운로드 파일은 보통 `프로젝트명-xxxxx.json`, 크기 **약 2KB 전후**, 내용이 `{` 로 시작하고 `"type": "service_account"` 가 있어야 함.
4. **잘못된 예:** `eyJ...` 로 시작하는 한 줄 JWT(n8n API 키 등과 혼동) — 이건 Google SA 키가 아님. 삭제 후 위 절차로 재발급.
5. SA JSON은 **로컬에만** 보관. Git/채팅/스크린샷에 올리지 말 것.

**S2. 스프레드시트를 서비스 계정에 공유** (필수 — 빼먹으면 403)
1. **응답 시트** (`***RESPONSE_SHEET_ID***`) 열기 → 공유  
   → `n8n-local-expense@codyssey-no-code-automation.iam.gserviceaccount.com`  
   → 역할 **편집자**
2. **결과 시트** (`***RESULT_SHEET_ID***`) 도 동일하게 **편집자** 공유

**S3. n8n Credential**
1. n8n → Credentials → **Google Service Account** (또는 Google Sheets 노드에서 Service Account 방식)
2. JSON 내용 붙여넣기 / 필드 매핑 (Email, Private Key 등 — UI 안내에 따름)
3. 이름 예: `Google SA - n8n expense`
4. Save 후 Sheets 노드에서 Document ID를 **직접 입력** (피커 없이도 동작)

> (선택) 파일 목록 UI를 쓰고 싶으면 **Google Drive API** 도 사용 설정.  
> Document ID를 수동 입력하면 Sheets API만으로도 Trigger/Append 가능.

#### 경로 O — OAuth 클라이언트 (나중에 필요하면)

서비스 계정 대신 “내 Gmail로 로그인” 방식을 쓸 때:

1. **OAuth 동의 화면** 구성 (외부 + 테스트 사용자에 본인 Gmail)
2. **OAuth 클라이언트 ID** → 웹 애플리케이션  
   리디렉션 URI:
   ```text
   http://localhost:5678/rest/oauth2-credential/callback
   ```
3. n8n → **Google Sheets OAuth2 API** → Client ID/Secret → Sign in with Google

현재 화면에 “표시할 OAuth 클라이언트가 없습니다”인 것은 정상. 경로 S를 쓰면 **지금 만들 필요 없음**.

### 8-3. 확정 리소스 (Apps Script 생성 로그 기준)

> 제출물·스크린샷에는 URL/ID 전체를 가릴 것. 아래는 **로컬 n8n 설정용** 메모.

| 용도 | 문서 이름(추정) | ID |
|---|---|---|
| **Trigger** — 폼 응답 시트 | 지출 메모 입력 폼 (응답) | `***RESPONSE_SHEET_ID***` |
| **Action** — 분류 결과 시트 | 지출 자동 분류 결과 | `***RESULT_SHEET_ID***` |
| 폼 (수동 테스트 제출용) | 지출 메모 입력 폼 | viewform: `.../e/***FORM_VIEW_ID***/viewform` |

**n8n 노드 매핑**

| 노드 | Document | Sheet / 열 |
|---|---|---|
| Google Sheets Trigger | 응답 ID 위 | 보통 탭 이름 `Form Responses 1` 또는 `양식 응답 1` (열기 확인). 메모 열 = **「지출 메모」** (타임스탬프 옆) |
| Sheets Append × 3 | 결과 ID 위 | 탭: `고액 지출 분류 결과` / `일반 지출 분류 결과` / `검토 필요` (없으면 헤더 6열로 생성) |

헤더(결과 시트 각 탭 공통): `타임스탬프 | 원본 메모 | 카테고리 | 금액 | 요약 | 특이사항`

**조립 전 1분 점검**

1. 응답 시트 열어 헤더 행·탭 이름 확인 (언어/계정에 따라 `양식 응답 1` 등).
2. 결과 시트에 분기용 탭 3개가 있는지 확인. 스크립트 기본값은 탭 1개(`분류 결과`)만 만들 수 있음 → Make에서 이미 3탭으로 나눠 뒀다면 그대로 사용.

---

## 9. 워크플로우 조립 체크리스트 (자격 증명 후)

워크플로우 이름 예: `지출 메모 자동 분류 (n8n)`

| 순서 | 노드 | 설정 요점 |
|---|---|---|
| 1 | **Google Sheets Trigger** | Event: Row Added / 문서=응답 시트 / Sheet=응답 탭 / Poll 주기(예: 1분) |
| 2 | **OpenAI** | Message a model 또는 Chat; JSON 모드; 시스템 프롬프트 = README 4절 그대로; User = 메모 열 |
| 3 | **Code** (권장) | OpenAI 응답 문자열을 JSON parse → `amount`(number), `Classification` 등 필드 정규화 |
| 4 | **Switch** | 규칙: (A) `amount >= 50000` / (B) `amount < 50000` AND `Classification != 분류불가` / (C) fallback 또는 `Classification == 분류불가` |
| 5–7 | **Google Sheets** × 3 | Append row → 결과 시트의 각 탭; 열: 타임스탬프·원본 메모·category·amount·summary·특이사항 |

시스템 프롬프트·분기 조건은 **Make와 완전 동일** (README 4·5절).

### 테스트 입력 (각 분기 1회)

| 케이스 | 예시 메모 | 기대 분기 |
|---|---|---|
| 고액 | `노트북 구매 120000원` | A |
| 일반 | `점심 김밥 4500` | B |
| 미분류 | `햄버거 -1000` 또는 금액 없음 | C |
| (참고) 0원 정상 | `무료 쿠폰으로 커피 받음` | B (분류불가 아님) |

완료 후: 실행 로그 캡처 → Workflow **Download** (JSON Export) → `n8n-runtime` 또는 프로젝트 폴더에 백업.
