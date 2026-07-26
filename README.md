# Codyssey 노코드 자동화 — 지출 분류 & 문의 분류

이 저장소는 **코드를 거의 쓰지 않고** 반복 업무를 자동화하는 과제(미션)의 결과물입니다.  
채점자·동료·나중에 다시 여는 본인까지, **배경 지식 없이** 이 문서만으로 전체 그림을 잡을 수 있게 썼습니다.

| 항목 | 내용 |
|------|------|
| 커리큘럼 | Codyssey · AI 도구 학습 · **노코드 자동화 기초** |
| 미션 원문 | [`미션.txt`](./미션.txt) |
| 저장소 상태 | **프로젝트 1 = 제출본 완료** · **프로젝트 2 = 구현·검증 진행 중** |
| 원격 | `origin/main`에 커밋·푸시하며 관리 |

---

## 1. 30초 요약 — 무엇을 만들었나?

### 프로젝트 1 (완료)

사용자가 Google 폼에 **지출 메모**를 적으면:

1. 자동으로 **AI(OpenAI)** 가 금액·카테고리·요약·분류 가능 여부를 뽑고  
2. 규칙에 따라 **고액 / 일반 / 검토(미분류)** 세 갈래로 나눈 뒤  
3. Google 스프레드시트 **해당 탭**에 한 줄씩 기록합니다.

같은 흐름을 **두 가지 도구**로 각각 만들고, 어떤 점이 다른지 **비교 보고서**로 정리했습니다.

| 구분 | 도구 | 형태 |
|------|------|------|
| 도구 A | **Make.com** | 클라우드 (브라우저에서 항상 동작) |
| 도구 B | **n8n** | 내 PC에 설치해 실행 (셀프호스트) |

Zapier Free는 “단계 수 제한” 때문에 이 구조를 못 만들어서 **채택하지 않았습니다.**

### 프로젝트 2 (진행 중)

**FinFit 팀 문의/피드백**을 폼으로 받으면 AI가 **긴급/일반**을 나누고,  
긴급만 **Slack 팀 채널**로 알리고, 둘 다 시트에 남기는 자동화입니다. (도구: **Make**)

→ 자세한 설계·Blueprint: [`project2/README.md`](./project2/README.md)

---

## 2. 이 README를 읽는 순서 (처음 온 사람용)

```text
① 이 문서 1~4절          → 무엇을 했는지·흐름이 뭔지
② project1/report/프로젝트1_…보고서.md → 비교·장단점·증거(GIF) 제출 본문
③ project1/make/ · project1/n8n/ README    → 도구별로 파일이 뭐가 있는지
④ project1/gif/ · project1/n8n/n8n_png/    → 화면 녹화·설치 마찰 이미지
⑤ project2/             → 자유 주제 (별개 과제)
```

**채점·리뷰만 할 때:** `project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md` 와 `project1/gif/` 를 보면 됩니다. (폼을 다시 만들 필요 없음)

**본인 계정으로 시나리오를 다시 돌릴 때:**  
반드시 **폼·시트 생성(§6.2) → Make/n8n Import·연결(§6.3~6.4)** 순서.  
폼 없이 Blueprint만 Import하면 Trigger/Append 대상이 없어 실패합니다.

---

## 3. 용어를 먼저 (Trigger / Action / 분기)

| 용어 | 쉬운 말 | 이 프로젝트에서의 예 |
|------|---------|----------------------|
| **Trigger** | “언제 시작할까?” | 폼 응답 시트에 **새 행**이 생기면 |
| **Action** | “그때 무엇을 할까?” | OpenAI로 분석, 시트에 쓰기, Slack 보내기 |
| **조건 분기** | “경우에 따라 다른 길” | 금액 5만 원 이상이면 고액 탭, 아니면 … |
| **Blueprint / Workflow JSON** | 시나리오 설계도 파일 | Make·n8n에 **가져오기(Import)** 해서 복원 |

미션 공통 최소 조건: Trigger ≥ 1, Action ≥ 2, 조건 분기 ≥ 1, **각 분기가 실제로 1번 이상 실행**된 증거.

---

## 4. 프로젝트 1 — 업무 흐름 (한 장)

```text
[사용자] Google 폼에 지출 메모 제출
        │
        ▼
[응답 스프레드시트] 새 행 추가  ← Make/n8n 이 여기를 감시 (Trigger)
        │
        ▼
[OpenAI] 메모 → JSON
        { category, amount, summary, Classification }
        │
        ▼
[Router / Switch]
   ├─ amount ≥ 50000                    → 탭「고액 지출 분류 결과」
   ├─ amount < 50000 이고 분류 가능     → 탭「일반 지출 분류 결과」
   └─ amount = 0 이고 분류불가          → 탭「검토 필요」
```

### 테스트 입력 예 (각 분기 1회 이상 검증함)

| 분기 | 예 |
|------|-----|
| 고액 | `테스트 노트북 200000원` |
| 일반 | `마트에서 식용유 5800원` |
| 검토 | `분류 잘 모르겠음 -5000` (음수 등) |

### AI가 쓰는 JSON 필드

- **category**: 식비, 교통비, 문화생활, 생필품, 기타, 분류불가 중 하나  
- **amount**: 0 이상 정수  
- **summary**: 짧은 요약  
- **Classification**: 분류 가능 / 분류불가 (정상 0원 지출과 파싱 실패를 구분)

시스템 프롬프트 전문·세부 분기 표는 비교 보고서와 워크플로 파일에 있습니다.  
더 보려면: `project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md`, `project1/n8n/n8n_지출_메모_자동_분류.workflow.json`, `project1/n8n/n8n_워크플로우_설계.md`.

---

## 5. 폴더 지도 — “이 파일은 어디?”

```text
Codyssey_3_ProJect/
├── README.md                      ← 지금 읽는 문서 (저장소 전체 안내)
├── 미션.txt                       ← 과제 요구사항 원문
├── other/                         ← 도구 사전 조사 (Zapier/Make/n8n)
│
├── project1/                      ← 프로젝트 1 전체 산출물
│   ├── create_google_form_Project_1.js
│   ├── report/                    ← 비교 분석 보고서 (제출 핵심)
│   ├── make/                      ← 도구 A Make Blueprint·캡처
│   ├── n8n/                       ← 도구 B 워크플로·설계·n8n_gif·n8n_png
│   └── gif/                       ← 실행 GIF (Make 6 + n8n 6)
│
├── project2/                      ← 프로젝트 2 문의 분류 (Make)
│
├── n8n-runtime/                   ← 로컬 n8n 설치 본체 (Git에 안 올림)
└── n8n-local/                     ← 로컬 실험용 (Git에 안 올림)
```

| 보고 싶은 것 | 가는 곳 |
|--------------|---------|
| **비교 보고서 (글 + GIF 임베드)** | [`project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md`](./project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md) |
| **Make 시나리오 가져오기** | [`project1/make/`](./project1/make/) 안 `.blueprint.json` · [`project1/make/README.md`](./project1/make/README.md) |
| **n8n 워크플로 가져오기** | [`project1/n8n/n8n_지출_메모_자동_분류.workflow.json`](./project1/n8n/n8n_지출_메모_자동_분류.workflow.json) · [`project1/n8n/README.md`](./project1/n8n/README.md) |
| **동작 화면 녹화** | [`project1/gif/`](./project1/gif/) (`make_*.gif`, `n8n_*.gif`) |
| **n8n 설치가 왜 힘든지** | [`project1/n8n/n8n_png/`](./project1/n8n/n8n_png/) |
| **프로젝트 2** | [`project2/README.md`](./project2/README.md) |
| **폼·시트 만들기 (재현 시 1순위)** | `project1/create_google_form_Project_1.js` → 그다음 Make/n8n (§6.2 선행) |

각 **커밋되는 폴더**에는 그 폴더 전용 `README.md`가 있습니다.  
**Git에 올리지 않는 폴더**(`n8n-runtime/` 등)에는 README를 두지 않습니다. 실행 안내는 `project1/n8n/README.md`에 있습니다.

---

## 6. 실행·재현 방법 (개요)

### 반드시 지킬 순서 (직접 다시 돌릴 때)

```text
① Google 폼 + 응답 시트 + 결과 시트 만들기   ← 여기가 먼저
        │
        ▼
② Make Blueprint / n8n 워크플로 Import
        │
        ▼
③ 도구 안에서 “어느 폼·어느 시트인지” 연결(재매핑)
        │
        ▼
④ 시나리오 ON / n8n Active 후, 폼에 테스트 제출
```

**왜 폼·시트가 선행인가?**

- Make·n8n 시나리오는 “언제 시작할지·어디에 쓸지”를 **이미 존재하는 Google 리소스**에 붙입니다.  
- 폼·응답 시트·결과 시트(탭)가 없으면 Trigger가 감시할 대상이 없고, Append 할 탭도 없습니다.  
- Blueprint/JSON 안의 시트 ID는 레포에서 **마스킹**되어 있거나 **만든 사람 PC 전용**이라, 다른 환경에서는 **본인이 만든 폼·시트 ID로 다시 지정**해야 합니다.  
- 따라서 **스크립트(또는 수동)로 폼·시트를 만든 다음** → Make/n8n을 Import·연결하는 순서가 맞습니다.  
  순서를 바꾸면 “Import는 됐는데 404 / 시트 없음 / 빈 실행”이 납니다.

프로젝트 2도 동일합니다: `create_google_form_Project_2.js` → 그다음 Make Blueprint.

### 6.1 아무것도 설치하지 않고 “결과만” 보기

(폼을 다시 만들 필요 없음 — 이미 찍어 둔 증거만 봄)

1. 이 README 1~4절  
2. [`project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md`](./project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md)  
3. [`project1/gif/`](./project1/gif/) 의 Make·n8n GIF  

→ 제출 증거·비교 논지를 이해하기에 충분합니다.

### 6.2 (선행) Google 폼·시트 만들기

**직접 시나리오를 재현·수정할 때만** 필요합니다. 채점용으로 GIF·보고서만 볼 때는 생략 가능합니다.

**프로젝트 1**

1. [script.google.com](https://script.google.com) → 새 프로젝트  
2. [`project1/create_google_form_Project_1.js`](./project1/create_google_form_Project_1.js) 전체 붙여넣기  
3. 함수 `createExpenseForm` 실행 (최초 1회 Google 권한 허용)  
4. **실행 로그**에서 확인·보관할 것:  
   - 폼 편집 URL / 응답(공유) URL  
   - **응답 스프레드시트** URL (Trigger 대상)  
   - **결과 스프레드시트** URL (탭: 고액·일반·검토)  

**프로젝트 2**

- 같은 방식으로 [`project2/create_google_form_Project_2.js`](./project2/create_google_form_Project_2.js) 의 `createInquiryForm`  
- 로그의 응답 시트·결과 시트(긴급/일반 탭) ID를 이후 Make 재매핑에 사용  

로그에 나온 URL·ID는 **비공개로만** 두고, 공개 레포에는 넣지 않습니다.

### 6.3 Make 시나리오 다시 돌리기 (도구 A)

**전제:** §6.2 로 폼·응답 시트·결과 시트가 준비되어 있어야 함.

1. [Make.com](https://www.make.com) 가입·로그인  
2. Scenario → **Import Blueprint** → `project1/make/Integration Google Forms, OpenAI (ChatGPT).blueprint.json`  

3. Google·OpenAI **연결(Connection)** 을 본인 계정으로 다시 연결  
4. 모듈마다 Spreadsheet/Sheet 를 **§6.2에서 만든 본인 시트**로 지정 (placeholder ID 그대로 두면 404)  
5. 시나리오 ON / Run once 후 **폼에 테스트 제출**  

세부: [`project1/make/README.md`](./project1/make/README.md)

### 6.4 n8n 다시 돌리기 (도구 B) — 실측 명령

**전제:**

1. **§6.2 폼·시트 완료**  
2. Node.js 설치, `n8n-runtime` 에 n8n 패키지 설치 완료  
   (설치 실패 시 Windows SDK·node-gyp → `project1/n8n/n8n_png/`, `project1/n8n/n8n_워크플로우_설계.md`)

n8n은 **내 PC에서 서버를 켠 뒤** 브라우저로 편집합니다.

```powershell
cd C:\Users\seong\Downloads\Codyssey_3_ProJect\n8n-runtime
npx n8n
```

정상 기동 시 터미널 요지:

- `n8n ready on ::, port 5678`
- `Version: 2.31.5`
- `Editor is now accessible via: http://localhost:5678`

그다음:

1. 브라우저 **http://localhost:5678**  
2. 워크플로 JSON Import (`project1/n8n/n8n_지출_메모_자동_분류.workflow.json`)  
3. Google/OpenAI Credentials 연결  
4. Trigger·Append 노드의 문서를 **§6.2에서 만든 시트**로 지정  
5. Active ON → 폼 테스트 제출  

Python runner 경고·deprecation 문구가 나와도 **이 과제 워크플로 실행과는 별개**인 경우가 많습니다.  
전체 표: **[`project1/n8n/README.md` — 로컬 실행 방법](./project1/n8n/README.md)** · 보고서 §3.2.

**중요:** PC를 끄거나 `npx n8n` 을 종료하면 트리거가 멈춥니다. Make(클라우드)와 가장 큰 실사용 차이입니다.

---

## 7. 보안 (제출·공개 레포 공통)

| 하지 말 것 | 대신 |
|------------|------|
| API Key, 토큰, 비밀번호 커밋 | 환경·Make/n8n Connection에만 보관 |
| 시트/폼 전체 URL·ID 그대로 공개 | `***RESULT_SHEET_ID***` 등 플레이스홀더 |
| 이메일 전체 노출 | `cho***45@gmail.com` 처럼 일부 가림 |

GIF·스크린샷에도 가능하면 이메일·전체 시트 ID를 가립니다.

---

## 8. 산출물 상태 (한눈에)

### 프로젝트 1

| 산출물 | 상태 | 위치 |
|--------|------|------|
| Make 워크플로 | ✅ | `project1/make/*.blueprint.json`, 캡처 |
| n8n 워크플로 | ✅ | `project1/n8n/*.workflow.json` |
| 비교 보고서 | ✅ 제출본 | `project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md` |
| 실행 GIF (분기×도구) | ✅ | `project1/gif/` |
| n8n 설치 마찰 이미지 | ✅ | `project1/n8n/n8n_png/` |
| 보너스1 AI 연동 | ✅ (OpenAI 파싱) | — |
| 보너스2 실패 알림 | 선택·미구현 | — |

### 프로젝트 2

| 산출물 | 상태 | 위치 |
|--------|------|------|
| 업무 정의·설계 | ✅ | `project2/design.md` |
| Make Blueprint | ✅ (LOCAL 실동작) | `project2/make/` |
| 긴급→Slack 팀 채널 | 설정·검증 중 | `project2/README.md` |
| 제출용 캡처 세트 | 진행 | — |

---

## 9. 자주 하는 질문

**Q. 코드를 몰라도 되나?**  
A. 과제의 본체는 Make/n8n 화면 구성입니다. Apps Script·패치 스크립트는 “폼을 빨리 만들거나 설정을 고칠 때”용이며, 없어도 도구 UI로 동일 구조를 만들 수 있습니다.

**Q. 레포만 클론하면 n8n이 바로 뜨나?**  
A. 아닙니다. `n8n-runtime` 은 Git에 없어서, 본인 PC에 Node로 설치·기동해야 합니다. 보고·채점만이면 GIF·보고서로 충분합니다.

**Q. Make와 n8n 트리거 이름이 다른데 같은 건가?**  
A. 둘 다 **폼 응답이 쌓이는 스프레드시트의 새 행**을 감시합니다. n8n에는 Forms 전용 트리거가 없어 Sheets Trigger로 표기됩니다.

**Q. 응답 시트와 결과 시트가 뭐가 다른가?**  
A. **응답 시트** = 폼이 자동으로 쌓는 원본 로그(Trigger가 감시). **결과 시트** = 자동화가 분류 후 쓰는 탭 3개(고액/일반/검토). 둘은 다른 스프레드시트 파일입니다.

**Q. OpenAI 키는 어디에?**  
A. 레포에 없습니다. Make Connection / n8n Credentials에 본인 API 키를 넣습니다. 키가 없으면 AI 단계가 실패합니다.

**Q. 폴더마다 README가 있는 이유?**  
A. 그 폴더만 열어도 “이게 뭔 파일인지” 알 수 있게 하기 위함입니다. **gitignore 폴더에는 README를 두지 않습니다.**

---

## 10. 작업 규칙 (기여자·본인)

1. 수정 후 **`origin/main`에 커밋·푸시**  
2. **커밋 대상 폴더**에 파일 추가·이동 시 그 폴더 `README.md`도 갱신  
3. 비밀·실 ID는 커밋하지 않기 (project2의 `*.LOCAL.blueprint.json`, `local_ids.json` 등은 gitignore)

---

## 11. 더 읽을 문서

| 문서 | 내용 |
|------|------|
| [`미션.txt`](./미션.txt) | 공식 요구·보너스·제약 |
| [`project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md`](./project1/report/프로젝트1_자동화_도구_비교_분석_보고서.md) | 비교 표, 장단점, GIF 증거 |
| [`project1/n8n/README.md`](./project1/n8n/README.md) | n8n 실행·Import·경고 로그 해석 |
| [`project1/make/README.md`](./project1/make/README.md) | Make Blueprint Import |
| [`project2/README.md`](./project2/README.md) | 자유 주제 현황 |
| [`other/README.md`](./other/README.md) | 도구 사전 조사 |

---

*처음 온 사람을 위한 입구 문서입니다. 세부 설정·트러블슈팅은 각 폴더 README와 비교 보고서를 보세요.*
