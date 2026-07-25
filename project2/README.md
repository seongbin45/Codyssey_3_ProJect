# project2/ — 프로젝트 2: 자유 주제 자동화

Codyssey 미션 **[프로젝트 2] 자유 주제 자동화 설계 및 구현**.  
프로젝트 1(`../make/`, `../n8n/`, `../report/`)과 **폴더로만 구분**하고, 브랜치는 나누지 않는다 (`main` 유지).

| 항목 | 내용 |
|------|------|
| 상태 | **주제 확정 — 팀 문의/피드백 자동 분류 (도구: Make)** |
| 선정 주제 | FinFit 팀 문의·피드백 긴급도/카테고리 자동 분류 |
| 도구 | **Make.com** (클라우드 상시 구동 · 프로젝트1 계정 재사용) |
| 설계 문서 | `design.md` |
| 공통 구조 | Trigger 1+ · Action 2+ · 조건 분기 1+ · **각 분기 1회 이상 실행 증거** |
| 자동 실행 | Trigger 발생 시 **자동** 실행 (설계 문서만 제출 불가) |

---

## 1. 미션 산출물 체크리스트 (프로젝트 2)

| # | 요구 | 상태 |
|---|------|------|
| 1 | 자동화할 **반복 업무 1개** 정의 | ✅ 문의/피드백 긴급 분류 (`design.md` §1) |
| 2 | **도구 1개** 선정 + 선정 이유 | ✅ Make — 상시 클라우드 (`design.md` §2) |
| 3 | 워크플로우 **설계 문서** (설명 또는 다이어그램) | ✅ `design.md` |
| 4 | **구현 화면** 캡처 | ⬜ Make Import·연동 후 캡처 |
| 5 | **실행 결과** 캡처 (분기별 1회 이상) | ⬜ 긴급/일반 테스트 케이스 |
| 6 | 실제 동작 워크플로우 (Export/Blueprint 등) | ✅ `make/FinFit_inquiry_auto_triage.blueprint.json` (Import용 · 연결 재매핑 필요) |

### 공통 기능 요구 (프로젝트 1과 동일 코어)

- Trigger ≥ 1  
- Action ≥ 2  
- 조건 분기(Filter/Router) ≥ 1 → **분기 경로마다 1회 이상 실행 확인**  
- (권장) 보너스1: 생성형 AI Action — 분류·요약에 자연스럽게 붙일 수 있음  
- (선택) 보너스2: 실패 알림·재시도  

---

## 2. 선정 주제 (확정)

**팀 문의/피드백 자동 분류** · 도구 **Make.com** · 상세는 `design.md`.

| 단계 | 내용 |
|------|------|
| Trigger | Google Forms 문의 접수 → 응답 시트 폴링 |
| Action | OpenAI JSON 분류 → Sheets 기록 (+ 긴급 시 Slack/이메일) |
| 분기 | `urgency = 긴급` / `일반` (2-way) |
| 테스트 | 결제 장애(긴급) · 다크모드 요청(일반) — `design.md` §6 |

### 검토만 했던 후보 (미채택)

| # | 주제 | 미채택 요약 |
|---|------|-------------|
| 2 | RSS/뉴스 요약 알림 | 실무 스토리 약함 · 계정 장벽은 낮음 |
| 3 | 캘린더 리마인더 | 개인 일정 중심 · 팀 문의 실사용과 거리 |

**Make 선정 이유 (요약):** 팀 문의를 노트북 전원과 무관하게 상시 수신하려면 클라우드가 맞고, 프로젝트1 Make 계정·연동 재사용이 빠르다. n8n은 로컬 상시 기동이 필요해 “팀 상시 도구” 스토리에 불리하다.

---

## 3. 제약 · 보안 (프로젝트 1과 동일 규칙)

| 규칙 | 내용 |
|------|------|
| 민감정보 | API Key, 토큰, 비밀번호 **노출 금지** |
| 마스킹 | 시트/폼 ID → `***…_ID***`, 이메일 → `cho***45@…` 형태 일부 가림 |
| 과금 | **무료 플랜 우선** (Make Free 월 1,000 크레딧 등). 유료 불가피 시 이유 + 무료 대안을 설계 문서에 기록 |
| 권장 조합 예 | Google Sheets + Gmail/Email + Webhook · Sheets + Slack/Discord + Webhook |
| 커밋 | 변경 시 `origin/main`에 커밋·푸시 (저장소 작업 규칙) |

---

## 4. 이 폴더 구조

```text
project2/
├── README.md              # 본 문서 (주제·체크리스트·규칙)
├── design.md              # 워크플로우 설계 (확정 초안)
├── make/                  # Make Blueprint·캡처 — 구현 시 추가
└── gif/ 또는 captures/    # 실행 증명 — 구현 시 추가
```

### 현재 파일

| 파일 | 설명 |
|------|------|
| `README.md` | 진행 상태·체크리스트·규칙 |
| `design.md` | 업무 정의, Make 선정 이유, 2-way 구조, JSON 스키마, 테스트 케이스 |
| `make/FinFit_inquiry_auto_triage.blueprint.json` | Make Import용 (마스킹) |
| `FinFit 팀 문의 피드백 자동 분류 (project2).blueprint.json` | Make Export 정리본 (마스킹, Slack 본문 포함) |
| `make/README.md` | Import 절차·시트 헤더·재매핑 안내 |
| `create_google_form_Project_2.js` | 문의 폼·결과 시트(긴급/일반 탭) Apps Script |
| `_build_blueprint.py` | Blueprint 재생성 스크립트 |

파일·하위 폴더를 추가할 때마다 **해당 폴더 README** 또는 본 README 표를 갱신한다.

---

## 5. 폴더 README 규칙 (저장소 공통)

| 규칙 | 설명 |
|------|------|
| 필수 | **커밋 대상** 산출물 폴더마다 `README.md` |
| 내용 | 목적, **파일별 설명 표**, 관련 경로, 주의사항 |
| 갱신 | 파일 추가·이동·이름 변경 시 **같은 커밋**에서 README 수정 |
| 하지 않음 | **커밋 제외 폴더**(`.gitignore`)에는 README를 만들지 않는다 |

---

## 6. 다음 액션

1. [x] 주제·도구 확정 + `design.md`  
2. [x] Make Import용 Blueprint — `make/FinFit_inquiry_auto_triage.blueprint.json`  
3. [x] Google 문의 폼 + 결과 시트 탭「긴급 문의」「일반 문의」 (Apps Script 로그 완료 · ID는 `make/local_ids.json` 로컬)  
4. [ ] Make에서 **`*.LOCAL.blueprint.json` Import** → Connection + Email To (`make/README.md`)  
5. [ ] 테스트 2건 실행 · 캡처 · 체크리스트 4–5 닫기

---

## 관련 경로

| 경로 | 설명 |
|------|------|
| `../미션.txt` | 프로젝트 2 요구·보너스·제약 원문 |
| `../README.md` | 저장소 전체 진행 상태 |
| `../report/` | 프로젝트 1 비교 보고서 (제출본) |
| `../make/`, `../n8n/` | 프로젝트 1 도구 산출물 (참고·패턴 재사용) |
