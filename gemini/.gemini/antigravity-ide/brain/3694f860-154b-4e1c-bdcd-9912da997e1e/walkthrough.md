# [Make.com] 지능형 지출 관리 워크플로우 구축 가이드

이 문서는 AI 모듈과 Router를 결합할 때 발생하는 기술적 오류를 완벽하게 방어하기 위한 설정 가이드입니다. 미션 보고서 작성 시 '구현 과정 요약' 및 '어려웠던 점/해결 방안' 섹션에 이 내용을 활용하시면 매우 훌륭한 결과물이 될 것입니다.

## 1. OpenAI 모듈 안전 설정 (JSON 파싱 에러 방지)

LLM의 출력값을 다음 모듈(Google Sheets 등)에서 사용하려면 반드시 구조화된 데이터(JSON)로 받아야 합니다.

- **Response Format**: `JSON object` 선택
- **마크다운 격리**: LLM이 ```json 과 같은 마크다운 태그를 붙이지 못하도록 프롬프트에 명시적으로 차단 지시를 넣어야 합니다.

### System Prompt (복사해서 사용)
```text
당신은 지출 내역 분석 비서입니다. 사용자의 메모를 분석하여 반드시 아래 JSON 구조로만 응답하세요. 마크다운 기호(```)를 절대 포함하지 말고 순수 JSON 문자열만 출력하세요.

{
  "category": "식비, 교통비, 문화생활, 생필품, 기타, 분류불가 중 택1 (String)",
  "amount": 지출 금액을 숫자로만 기재, 유추 불가 시 0 (Number),
  "summary": "지출 내역을 10자 이내로 요약 (String)"
}
```

### User Prompt
```text
{{구글 폼 Trigger의 '지출 메모' 필드 매핑}}
```
*(실제 Make.com 화면에서는 구글 폼의 데이터를 드래그 앤 드롭으로 매핑합니다.)*

---

## 2. Router 3-Way 분기 설정 (Null / 에러 방지)

사용자가 금액을 아예 입력하지 않거나, LLM이 `null`을 반환할 경우 `parseNumber()` 함수가 오류를 일으킬 수 있습니다. 이를 방지하기 위해 `ifempty` 함수를 감싸서 기본값(0)을 부여하는 것이 핵심입니다.

### 분기 A (고액 지출)
> 5만 원 이상인 경우 실행됩니다. 구글 시트에 기록하고 Slack으로 고액 지출 경고를 보냅니다.
* **조건명**: 고액 지출 (5만 원 이상)
* **조건식**: `{{ifempty(parseNumber(OpenAI_출력값.amount); 0)}}` **[Greater than or equal to]** `50000`

### 분기 B (일반 지출)
> 1원 이상 5만 원 미만인 경우 실행됩니다. 구글 시트에만 조용히 기록합니다.
* **조건명**: 일반 지출 (5만 원 미만)
* **조건식 1**: `{{ifempty(parseNumber(OpenAI_출력값.amount); 0)}}` **[Less than]** `50000`
* **AND**
* **조건식 2**: `{{ifempty(parseNumber(OpenAI_출력값.amount); 0)}}` **[Not equal to]** `0`

### 분기 C (예외 및 수동 검토)
> 금액을 유추할 수 없거나 분류가 불가능한 쓰레기 값이 들어왔을 때 실행됩니다. 시트 기록 후 수동 확인을 요청합니다.
* **조건명**: 금액 누락 또는 분류 불가
* **조건식 1**: `{{ifempty(parseNumber(OpenAI_출력값.amount); 0)}}` **[Equal to]** `0`
* **OR**
* **조건식 2**: `{{OpenAI_출력값.category}}` **[EqualTo]** `분류불가`

---

## 3. 최종 Action 모듈(Google Sheets & Slack) 매핑 가이드

Router 이후 각 분기에 달릴 액션 모듈들의 구체적인 매핑 값입니다.

### Google Sheets (Add a Row) 매핑 규칙 (분기 A, B, C 공통)
* **날짜 (A열)**: `{{Timestamp}}` (구글 폼 Trigger)
* **원본 메모 (B열)**: `{{지출 메모}}` (구글 폼 Trigger)
* **카테고리 (C열)**: `{{1.category}}` (OpenAI 모듈 출력값)
* **금액 (D열)**: `{{1.amount}}` (OpenAI 모듈 출력값)
* **요약 (E열)**: `{{1.summary}}` (OpenAI 모듈 출력값)
* **특이사항 (F열)**:
  * 분기 A / B: (비워두거나 `정상` 입력)
  * 분기 C: `검토 필요 (금액/카테고리 확인 요망)`

### Slack (Send a Message) 알림 매핑 규칙
* **분기 A (고액 지출)** 채널 전송:
```text
🚨 [고액 지출 발생]
- 요약: {{1.summary}}
- 금액: {{1.amount}}원
- 원본 메모: {{지출 메모}}
```
* **분기 C (예외 처리)** 채널 전송:
```text
⚠️ [지출 데이터 검토 요청]
자동 분류에 실패했거나 금액이 누락되었습니다. 시트를 확인해 주세요.
- 원본 메모: {{지출 메모}}
```

---

## 4. [도구 B] Zapier 전환 방안 설계

미션 요구사항인 '서로 다른 2개 이상의 도구 사용'을 충족하기 위해, Make에서 검증된 로직을 Zapier의 **Paths (조건 분기)** 기능으로 옮기는 설계입니다.

1. **Trigger**: Google Forms – New Response in Spreadsheet
2. **Step 2 (Action - OpenAI)**: ChatGPT 모듈을 통해 위와 동일한 JSON 구조로 파싱 수행
3. **Step 3 (Paths - 조건 분기)**: 3개의 Path 생성
   * **Path A (고액)**: `Amount` Greater than or equal to `50000`
   * **Path B (일반)**: `Amount` Less than `50000` **AND** `Amount` Not equal to `0`
   * **Path C (예외)**: `Amount` Equal to `0` **OR** `Category` Equal to `분류불가`
4. **각 Path 내부 Action**: Make와 동일하게 Google Sheets(Create Spreadsheet Row) 및 Slack(Send Channel Message) 액션 배치

> [!WARNING]
> **Zapier Paths 평가 시 주의사항 (Null 방어)**
> Make.com에서는 `ifempty()` 함수를 통해 필드 누락이나 Null 값을 쉽게 0으로 대체할 수 있었습니다. 그러나 Zapier의 Paths는 필드 자체가 누락되거나 Null일 경우 조건 평가 자체에서 에러(Halt)가 발생할 수 있습니다. 
> 따라서 Zapier 연동 시에는 OpenAI System Prompt의 지시(금액 유추 불가 시 무조건 숫자 0 반환)가 절대적으로 지켜지도록 프롬프트를 더욱 엄격하게 통제해야 합니다.

---

## 💡 테스트 방법

위 설정을 마친 후, 구글 폼에 아래 3가지 케이스를 제출하여 Make 및 Zapier에서 각 분기가 1회 이상 정상 실행되는지 확인하고 해당 화면을 캡처하세요.

1. **분기 A 테스트**: "어제 소고기 회식으로 150000원 결제함"
2. **분기 B 테스트**: "편의점에서 물이랑 과자 4500원어치 삼"
3. **분기 C 테스트**: "안녕 반가워 내일 뭐해" (금액 누락/의미 없는 텍스트)
