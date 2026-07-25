# -*- coding: utf-8 -*-
"""Normalize Make export: fix Slack text, bare sheet IDs, mask secrets for git."""
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

RESPONSE_ID = "1HefV2aTsP3Jgzk_pSVvqN9cUB9za6_K-daRWwR9OOc0"
RESULT_ID = "1yCGMpxsBQGoYPb8Dai0mImo5nJC073r9FqC5lDIH9ys"

SLACK_TEXT = (
    "*[FinFit 긴급 문의]* {{2.result.category}}\n"
    "요약: {{2.result.summary}}\n"
    "긴급도: {{2.result.urgency}}\n"
    "원문: {{1.`1`}}\n"
    "접수: {{1.`0`}}\n"
    "연락처: {{1.`2`}}"
)


def walk(nodes, fn):
    for n in nodes:
        fn(n)
        if n.get("module") == "builtin:BasicRouter":
            for r in n.get("routes") or []:
                walk(r.get("flow") or [], fn)


def fix_runtime(j: dict) -> dict:
    """Fixes that apply to both local and public copies."""

    def fix_node(n: dict) -> None:
        mapper = n.setdefault("mapper", {}) if n.get("mapper") is not None else {}
        params = n.setdefault("parameters", {}) if n.get("parameters") is not None else {}

        # Strip slash-wrapped spreadsheet IDs anywhere
        for bag in (params, mapper):
            if not isinstance(bag, dict):
                continue
            sid = bag.get("spreadsheetId")
            if isinstance(sid, str):
                bag["spreadsheetId"] = sid.strip().strip("/")

        # Slack: team channel (public/private), not DM/slackbot
        if n.get("module") == "slack:CreateMessage":
            mapper["text"] = mapper.get("text") or SLACK_TEXT
            mapper["mrkdwn"] = True
            mapper["channelWType"] = "list"
            mapper["idType"] = "channel"
            # public | private — not im (DM)
            ct = mapper.get("channelType")
            if ct in (None, "im", "mpim"):
                mapper["channelType"] = "public"
            # Drop DM channel IDs (D…) so Make forces re-select of C…/G… team channel
            ch = mapper.get("channel")
            if isinstance(ch, str) and (ch.startswith("D") or ch.startswith("***")):
                mapper["channel"] = "***SLACK_TEAM_CHANNEL_ID***"
            n["mapper"] = mapper
            # restore labels for designer
            restore = n.setdefault("metadata", {}).setdefault("restore", {})
            expect = restore.setdefault("expect", {})
            expect["channelType"] = {"label": "Public channel"}
            expect["channel"] = {
                "mode": "chose",
                "label": "Import 후 팀 채널 선택 (공개 또는 비공개)",
            }
            expect["idType"] = {"mode": "chose", "label": "Channel ID"}

        # Sheets values: ensure 6 columns mapped with expressions (not hardcoded)
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

        # OpenAI safety
        if n.get("module") == "openai-gpt-3:CreateCompletion":
            mapper["response_format"] = "json_object"
            mapper["parseJSONResponse"] = True
            n["mapper"] = mapper

    walk(j.get("flow") or [], fix_node)

    # Designer note
    meta = j.setdefault("metadata", {})
    meta["notes"] = [
        {
            "moduleId": None,
            "content": (
                "project2 FinFit 문의 자동 분류 (export 정리본). "
                "Import 후: (1) Google 연결+응답시트 탭 (Form Responses 1 또는 양식 응답 1) "
                "(2) 결과시트 긴급/일반 문의 탭 — spreadsheetId는 슬래시 없이 ID만 "
                "(3) OpenAI (4) Slack 채널+연결. "
                "긴급 분기 Slack 본문은 text 필드에 매핑됨."
            ),
        }
    ]
    return j


def mask_for_public(j: dict) -> dict:
    raw = json.dumps(j, ensure_ascii=False)
    raw = raw.replace(RESPONSE_ID, "***INQUIRY_RESPONSE_SHEET_ID***")
    raw = raw.replace(RESULT_ID, "***INQUIRY_RESULT_SHEET_ID***")
    # Slack channel IDs (DM/channel)
    raw = re.sub(
        r'"channel"\s*:\s*"[CDG][A-Z0-9]{8,}"',
        '"channel": "***SLACK_TEAM_CHANNEL_ID***"',
        raw,
    )
    raw = raw.replace("***SLACK_CHANNEL_ID***", "***SLACK_TEAM_CHANNEL_ID***")
    # connection numeric ids → leave or zero; Make re-binds on import
    raw = re.sub(
        r'choiseongbin45@gmail\.com',
        "cho***45@gmail.com",
        raw,
    )
    # workspace labels may contain email already masked
    return json.loads(raw)


def main() -> None:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    fixed = fix_runtime(deepcopy(src))

    # Local working copy (real IDs) — gitignored pattern *.LOCAL.blueprint.json
    OUT_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOCAL.write_text(
        json.dumps(fixed, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    public = mask_for_public(deepcopy(fixed))
    OUT_PUBLIC.write_text(
        json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # Keep Korean-named export in project2 root as public-masked too (safe to commit)
    OUT_KR.write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")

    print("LOCAL", OUT_LOCAL, "bytes", OUT_LOCAL.stat().st_size)
    print("PUBLIC", OUT_PUBLIC, "bytes", OUT_PUBLIC.stat().st_size)
    print("KR", OUT_KR, "bytes", OUT_KR.stat().st_size)

    # verify
    def check(path: Path, expect_real: bool) -> None:
        t = path.read_text(encoding="utf-8")
        j = json.loads(t)
        slack_ok = False
        slash = "/1yCGM" in t or "/1Hef" in t

        def fn(n):
            nonlocal slack_ok
            if n.get("module") == "slack:CreateMessage":
                slack_ok = bool((n.get("mapper") or {}).get("text"))
            sid = (n.get("mapper") or {}).get("spreadsheetId") or (
                n.get("parameters") or {}
            ).get("spreadsheetId")
            if isinstance(sid, str) and sid.startswith("/"):
                print("WARN slash id", path.name, sid)

        walk(j.get("flow") or [], fn)
        print(
            path.name,
            "slack_text",
            slack_ok,
            "has_real_response",
            RESPONSE_ID in t,
            "has_placeholder",
            "***INQUIRY" in t,
            "slash",
            slash,
            "expect_real",
            expect_real,
        )

    check(OUT_LOCAL, True)
    check(OUT_PUBLIC, False)
    check(OUT_KR, False)


if __name__ == "__main__":
    main()
