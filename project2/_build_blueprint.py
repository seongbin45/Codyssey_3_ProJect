# -*- coding: utf-8 -*-
"""Build Make.com importable blueprint for project2 inquiry triage."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "make" / "Integration Google Forms, OpenAI (ChatGPT).blueprint.json"
OUT_DIR = ROOT / "make"
OUT = OUT_DIR / "FinFit_inquiry_auto_triage.blueprint.json"

SYSTEM = r"""당신은 FinFit 팀 문의/피드백 분류 비서입니다. 사용자 문의 텍스트를 분석하여 반드시 아래 JSON 구조로만 응답하세요. 마크다운 기호(```)를 절대 포함하지 말고 순수 JSON 문자열만 출력하세요.

{
  "urgency": "긴급 또는 일반 중 택1",
  "category": "버그, 기능요청, 결제, 기타 중 택1",
  "summary": "문의 내용을 15자 이내로 요약"
}

분류 규칙:
1. urgency는 "긴급" 또는 "일반"만 사용한다.
2. 다음이면 urgency를 "긴급"으로 한다:
   - 결제/결제 실패/환불/계좌/출금 등 금전 장애가 현재 진행 중이라고 호소하는 경우
   - 서비스 장애·접속 불가·데이터 손실 등 즉시 대응이 필요해 보이는 경우
   - "지금 당장", "급해요", "긴급", "막혔어요" 등 즉시성이 명시된 경우
3. 기능 요청, UI 개선, 일정 문의, 단순 질문 등은 urgency를 "일반"으로 한다.
4. category는 문의 성격에 맞게 버그/기능요청/결제/기타 중 하나만 고른다.
5. summary는 한국어 15자 이내 핵심만 적는다."""


def main() -> None:
    src = json.loads(SRC.read_text(encoding="utf-8"))

    trigger = copy.deepcopy(next(n for n in src["flow"] if n["id"] == 2))
    openai = copy.deepcopy(next(n for n in src["flow"] if n["id"] == 3))
    router = copy.deepcopy(next(n for n in src["flow"] if n["id"] == 11))
    sheet_tpl = copy.deepcopy(router["routes"][0]["flow"][0])

    # --- Trigger: Google Forms response sheet polling ---
    trigger["id"] = 1
    trigger["parameters"]["spreadsheetId"] = "***INQUIRY_RESPONSE_SHEET_ID***"
    trigger["parameters"]["sheetId"] = "Form Responses 1"
    rp = trigger["metadata"]["restore"]["parameters"]
    rp["spreadsheetId"] = {
        "mode": "chose",
        "label": "FinFit 문의 접수 폼 (응답) — Import 후 본인 시트 선택",
    }
    rp["sheetId"] = {"mode": "chose", "label": "Form Responses 1"}
    for col in trigger["metadata"]["interface"]:
        if col.get("name") == "0":
            col["label"] = "Timestamp (A)"
        elif col.get("name") == "1":
            col["label"] = "문의 내용 (B)"
        elif col.get("name") == "2":
            col["label"] = "연락처/이메일 (C, 선택)"
    trigger["metadata"]["designer"] = {"x": 0, "y": 0}

    # --- OpenAI JSON classification ---
    openai["id"] = 2
    openai["mapper"]["messages"] = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "{{1.`1`}}", "imageDetail": "auto"},
    ]
    openai["mapper"]["model"] = "gpt-4.1"
    openai["mapper"]["response_format"] = "json_object"
    openai["mapper"]["parseJSONResponse"] = True
    openai["metadata"]["designer"] = {"x": 300, "y": 0}

    def make_sheet(mid: int, sheet_name: str, filter_name: str, conditions, x: int, y: int):
        m = copy.deepcopy(sheet_tpl)
        m["id"] = mid
        m["parameters"] = {"__IMTCONN__": sheet_tpl["parameters"].get("__IMTCONN__")}
        m["filter"] = {"name": filter_name, "conditions": conditions}
        m["mapper"] = {
            "from": "drive",
            "mode": "select",
            "values": {
                "0": "{{1.`0`}}",
                "1": "{{1.`1`}}",
                "2": "{{2.result.urgency}}",
                "3": "{{2.result.category}}",
                "4": "{{2.result.summary}}",
                "5": "{{1.`2`}}",
            },
            "sheetId": sheet_name,
            "spreadsheetId": "/***INQUIRY_RESULT_SHEET_ID***",
            "includesHeaders": True,
            "insertDataOption": "INSERT_ROWS",
            "useColumnHeaders": False,
            "valueInputOption": "USER_ENTERED",
            "insertUnformatted": False,
        }
        restore = m.setdefault("metadata", {}).setdefault("restore", {})
        r_params = restore.setdefault("parameters", {})
        r_params["__IMTCONN__"] = (
            sheet_tpl.get("metadata", {})
            .get("restore", {})
            .get("parameters", {})
            .get("__IMTCONN__", {})
        )
        r_mapper = restore.setdefault("mapper", {})
        r_mapper["sheetId"] = {"mode": "chose", "label": sheet_name}
        r_mapper["spreadsheetId"] = {
            "mode": "chose",
            "label": "FinFit 문의 분류 결과 — Import 후 본인 시트 선택",
        }
        m["metadata"]["designer"] = {"x": x, "y": y}
        return m

    urgent_sheet = make_sheet(
        4,
        "긴급 문의",
        "긴급(urgency=긴급)",
        [[{"a": "{{2.result.urgency}}", "b": "긴급", "o": "text:equal"}]],
        750,
        -150,
    )
    normal_sheet = make_sheet(
        6,
        "일반 문의",
        "일반(urgency=일반)",
        [[{"a": "{{2.result.urgency}}", "b": "일반", "o": "text:equal"}]],
        750,
        150,
    )

    # Email alert on urgent branch (remap To + connection after import)
    email_mod = {
        "id": 5,
        "module": "email:ActionSendEmail",
        "version": 1,
        "parameters": {},
        "mapper": {
            "to": ["***ALERT_EMAIL***"],
            "subject": "[FinFit 긴급 문의] {{2.result.category}} — {{2.result.summary}}",
            "content": (
                "긴급 문의가 접수되었습니다.\n\n"
                "요약: {{2.result.summary}}\n"
                "카테고리: {{2.result.category}}\n"
                "긴급도: {{2.result.urgency}}\n"
                "원문: {{1.`1`}}\n"
                "접수시각: {{1.`0`}}\n"
            ),
        },
        "metadata": {
            "designer": {"x": 1000, "y": -150},
            "restore": {},
            "expect": [
                {"name": "to", "type": "array", "label": "To", "spec": {"type": "email"}},
                {"name": "subject", "type": "text", "label": "Subject"},
                {"name": "content", "type": "text", "label": "Content"},
            ],
            "interface": [],
        },
    }

    router["id"] = 3
    router["metadata"]["designer"] = {"x": 550, "y": 0}
    router["routes"] = [
        {"flow": [urgent_sheet, email_mod]},
        {"flow": [normal_sheet]},
    ]

    blueprint = {
        "name": "FinFit 팀 문의 피드백 자동 분류 (project2)",
        "flow": [trigger, openai, router],
        "metadata": {
            "instant": False,
            "version": 1,
            "scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": True,
                "autoCommitTriggerLast": True,
                "sequential": False,
                "slots": None,
                "confidential": False,
                "dataloss": False,
                "dlq": False,
                "freshVariables": False,
            },
            "designer": {"orphans": []},
            "zone": "us2.make.com",
            "notes": [
                {
                    "moduleId": None,
                    "content": (
                        "project2 FinFit 문의 자동 분류. Import 후 재매핑: "
                        "(1) Trigger=문의 폼 응답 시트 "
                        "(2) 결과 시트 탭「긴급 문의」「일반 문의」 "
                        "헤더: 타임스탬프|원본 문의|긴급도|카테고리|요약|연락처 "
                        "(3) OpenAI connection "
                        "(4) 긴급 Email To. "
                        "테스트: 결제 장애(긴급) / 다크모드 요청(일반)."
                    ),
                }
            ],
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(blueprint, ensure_ascii=False, indent=2), encoding="utf-8")
    json.loads(OUT.read_text(encoding="utf-8"))
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
