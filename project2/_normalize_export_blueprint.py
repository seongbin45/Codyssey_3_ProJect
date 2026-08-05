# -*- coding: utf-8 -*-
"""Normalize Make export: Slack text, bare sheet IDs, mask secrets for git.

Real spreadsheet IDs must come only from gitignored make/local_ids.json.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "FinFit 팀 문의 피드백 자동 분류 (project2).blueprint.json"
OUT_PUBLIC = ROOT / "make" / "FinFit_inquiry_auto_triage.blueprint.json"
OUT_LOCAL = ROOT / "make" / "FinFit_inquiry_auto_triage.LOCAL.blueprint.json"
OUT_KR = ROOT / "FinFit 팀 문의 피드백 자동 분류 (project2).blueprint.json"
LOCAL_IDS_PATH = ROOT / "make" / "local_ids.json"  # gitignored

SLACK_TEXT = (
    "*[FinFit 긴급 문의]* {{2.result.category}}\n"
    "요약: {{2.result.summary}}\n"
    "긴급도: {{2.result.urgency}}\n"
    "원문: {{1.`1`}}\n"
    "접수: {{1.`0`}}\n"
    "연락처: {{1.`2`}}"
)

# Google Drive/Sheets file id shape (not a secret template)
_BARE_GOOGLE_ID = re.compile(r"(?<![*A-Za-z0-9_-])1[A-Za-z0-9_-]{30,}(?![*A-Za-z0-9_-])")


def walk(nodes, fn):
    for n in nodes:
        fn(n)
        if n.get("module") == "builtin:BasicRouter":
            for r in n.get("routes") or []:
                walk(r.get("flow") or [], fn)


def load_local_ids() -> dict:
    if not LOCAL_IDS_PATH.exists():
        return {}
    try:
        return json.loads(LOCAL_IDS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def fix_runtime(j: dict) -> dict:
    def fix_node(n: dict) -> None:
        mapper = n.get("mapper") if isinstance(n.get("mapper"), dict) else {}
        params = n.get("parameters") if isinstance(n.get("parameters"), dict) else {}

        for bag in (params, mapper):
            sid = bag.get("spreadsheetId")
            if isinstance(sid, str):
                bag["spreadsheetId"] = sid.strip().strip("/")

        if n.get("module") == "slack:CreateMessage":
            mapper["text"] = mapper.get("text") or SLACK_TEXT
            mapper["mrkdwn"] = True
            mapper["channelWType"] = "list"
            mapper["idType"] = "channel"
            if mapper.get("channelType") in (None, "im", "mpim"):
                mapper["channelType"] = "public"
            ch = mapper.get("channel")
            if isinstance(ch, str) and (ch.startswith("D") or ch.startswith("***")):
                mapper["channel"] = "***SLACK_TEAM_CHANNEL_ID***"
            n["mapper"] = mapper
            restore = n.setdefault("metadata", {}).setdefault("restore", {})
            expect = restore.setdefault("expect", {})
            expect["channelType"] = {"label": "Public channel"}
            expect["channel"] = {
                "mode": "chose",
                # Final verified in gif/make_urgent_3_slack.gif: #새-채널 (public)
                "label": "Import 후 Public channel → #새-채널 선택",
            }

        if n.get("module") == "google-sheets:addRow":
            mapper["values"] = {
                "0": "{{1.`0`}}",
                "1": "{{1.`1`}}",
                "2": "{{2.result.urgency}}",
                "3": "{{2.result.category}}",
                "4": "{{2.result.summary}}",
                "5": "{{1.`2`}}",
            }
            n["mapper"] = mapper

        if n.get("module") == "openai-gpt-3:CreateCompletion":
            mapper["response_format"] = "json_object"
            mapper["parseJSONResponse"] = True
            n["mapper"] = mapper

        if params:
            n["parameters"] = params
        if mapper and n.get("module") != "google-sheets:addRow":
            if n.get("module") != "slack:CreateMessage":
                n["mapper"] = mapper

    walk(j.get("flow") or [], fix_node)
    j.setdefault("metadata", {})["notes"] = [
        {
            "moduleId": None,
            "content": (
                "project2 FinFit 문의 자동 분류. Import 후 Google/OpenAI/Slack 재연결. "
                "시트 ID는 슬래시 없이. Slack 최종 검증: Public channel #새-채널 "
                "(증거: gif/make_urgent_3_slack.gif). DM(im) 사용 안 함."
            ),
        }
    ]
    return j


def mask_for_public(j: dict) -> dict:
    raw = json.dumps(j, ensure_ascii=False)
    ids = load_local_ids()
    for key, ph in (
        ("response_sheet_id", "***INQUIRY_RESPONSE_SHEET_ID***"),
        ("result_sheet_id", "***INQUIRY_RESULT_SHEET_ID***"),
        ("form_edit_id", "***FORM_EDIT_ID***"),
    ):
        if ids.get(key):
            raw = raw.replace(ids[key], ph)

    raw = _BARE_GOOGLE_ID.sub("***GOOGLE_FILE_ID***", raw)
    # tighten spreadsheet fields
    raw = re.sub(
        r'("spreadsheetId"\s*:\s*")\*\*\*GOOGLE_FILE_ID\*\*\*',
        r"\1***INQUIRY_SHEET_ID***",
        raw,
    )
    raw = re.sub(
        r'"channel"\s*:\s*"[CDG][A-Z0-9]{8,}"',
        '"channel": "***SLACK_TEAM_CHANNEL_ID***"',
        raw,
    )
    # full gmail → partial (do not touch already masked ***)
    raw = re.sub(
        r"(?<![*])([A-Za-z0-9._%+-]{2,4})[A-Za-z0-9._%+-]*@gmail\.com",
        r"\1***@gmail.com",
        raw,
    )
    raw = re.sub(r"cho[^*@\s]{0,20}\*\*\*@gmail\.com", "cho***45@gmail.com", raw)
    raw = re.sub(r'"__IMTCONN__"\s*:\s*\d+', '"__IMTCONN__": 0', raw)
    return json.loads(raw)


def apply_local_sheet_ids(j: dict, ids: dict) -> dict:
    resp, result = ids.get("response_sheet_id"), ids.get("result_sheet_id")

    def set_ids(n: dict) -> None:
        if n.get("module") == "google-forms:watchRows" and resp:
            p = n.setdefault("parameters", {})
            p["spreadsheetId"] = resp
        if n.get("module") == "google-sheets:addRow" and result:
            m = n.setdefault("mapper", {})
            m["spreadsheetId"] = result

    walk(j.get("flow") or [], set_ids)
    return j


def main() -> None:
    src_path = SRC if SRC.exists() else OUT_PUBLIC
    if not src_path.exists():
        raise SystemExit("No blueprint source found")
    src = json.loads(src_path.read_text(encoding="utf-8"))
    fixed = fix_runtime(deepcopy(src))
    public = mask_for_public(deepcopy(fixed))

    OUT_PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    pub_text = json.dumps(public, ensure_ascii=False, indent=2)
    OUT_PUBLIC.write_text(pub_text, encoding="utf-8")
    OUT_KR.write_text(pub_text, encoding="utf-8")

    ids = load_local_ids()
    local = apply_local_sheet_ids(deepcopy(public), ids) if ids else deepcopy(fixed)
    local = fix_runtime(local)
    if ids:
        local = apply_local_sheet_ids(local, ids)
    OUT_LOCAL.write_text(json.dumps(local, ensure_ascii=False, indent=2), encoding="utf-8")

    # verify no bare google ids in public
    for path in (OUT_PUBLIC, OUT_KR):
        leaked = _BARE_GOOGLE_ID.findall(path.read_text(encoding="utf-8"))
        if leaked:
            raise SystemExit(f"{path.name} still has bare IDs: {leaked}")
        # reject unmasked gmail local-parts (anything@gmail without ***)
        if re.search(r"(?<![*])[A-Za-z0-9._%+-]{5,}@gmail\.com", path.read_text(encoding="utf-8")):
            raise SystemExit(f"{path.name} still has unmasked gmail address")
    print("OK public masked; LOCAL written", OUT_LOCAL.stat().st_size)


if __name__ == "__main__":
    main()
