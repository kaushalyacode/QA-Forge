#!/usr/bin/env python3
"""Extract candidate requirements + acceptance criteria from a BRD/PRD/SRS (markdown, text or html).

This is a recall net: review and edit the output before using it.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

NATIVE_ID = re.compile(r"\b((?:FR|NFR|BR|REQ|US|UC|SR|PR)-?\d+(?:\.\d+)*)\b", re.I)
NORMATIVE = re.compile(r"\b(shall|must|should|will be able to|is required to|needs? to)\b", re.I)
USER_STORY = re.compile(r"\bas an? (.+?),? i (?:want|need|would like) (.+?)(?:,? so that (.+?))?[.\n]", re.I | re.S)
AC_HEADER = re.compile(r"^\s*(?:#+\s*|\*\*|__)?\s*(acceptance criteria|ac|criteria)\b", re.I)
GWT = re.compile(r"^\s*[-*\d.)]*\s*(given|when|then|and|but)\b", re.I)
BULLET = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s+(.*)")
HEADING = re.compile(r"^\s*#{1,6}\s+(.*)")
NFR_HINT = re.compile(r"\b(performance|latency|response time|seconds|ms\b|uptime|availability|secure|encrypt|gdpr|pci|wcag|accessib|scalab|concurrent)", re.I)


def to_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".html", ".htm"}:
        raw = re.sub(r"<(br|/p|/li|/h\d|/tr)[^>]*>", "\n", raw, flags=re.I)
        raw = re.sub(r"<li[^>]*>", "\n- ", raw, flags=re.I)
        raw = re.sub(r"<[^>]+>", "", raw)
        raw = html.unescape(raw)
    return raw


def classify(text: str) -> str:
    if re.search(r"\b(wcag|screen reader|keyboard|contrast|accessib)", text, re.I):
        return "accessibility"
    if re.search(r"\b(encrypt|auth|password|token|permission|role|gdpr|pii|security)", text, re.I):
        return "security"
    if re.search(r"\b(latency|respon\w* (?:time|in)|seconds?|ms\b|p9\d|throughput|concurrent|load time)", text, re.I):
        return "performance"
    if NFR_HINT.search(text):
        return "non-functional"
    return "functional"


def extract(text: str, prefix: str):
    lines = text.splitlines()
    reqs, current, in_ac, section = [], None, False, ""
    n = 0

    def new(title, source_id=""):
        nonlocal n
        n += 1
        title = re.sub(r"\s+", " ", title).strip(" -*:#")
        return {
            "id": f"REQ-{prefix}-{n:03d}",
            "source": "other",
            "source_id": source_id,
            "title": title[:200],
            "type": classify(title),
            "priority": "P2",
            "acceptance_criteria": [],
            "tags": [t for t in [re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-")] if t],
            "status": "draft",
            "notes": "auto-extracted; review",
        }

    for line in lines:
        s = line.strip()
        if not s:
            continue
        h = HEADING.match(line)
        if h and not AC_HEADER.match(line):
            section = h.group(1).strip()[:40]
            in_ac = False
        if AC_HEADER.match(line):
            in_ac = True
            continue
        if current and (in_ac or GWT.match(line)):
            b = BULLET.match(line)
            item = (b.group(1) if b else s).strip()
            if GWT.match(line) or b:
                current["acceptance_criteria"].append(item)
                continue
        id_m = NATIVE_ID.search(s)
        story = USER_STORY.search(s + "\n")
        if id_m or story or (NORMATIVE.search(s) and len(s) > 20):
            if h and not id_m:
                continue  # headings are context, not requirements
            title = s
            if id_m:
                title = s[id_m.end():] or s
            current = new(title, id_m.group(1).upper() if id_m else "")
            if current["source_id"].startswith("NFR") and current["type"] == "functional":
                current["type"] = "non-functional"
            reqs.append(current)
            in_ac = False
    return reqs


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", type=Path)
    p.add_argument("-o", "--output", type=Path, help="write JSON here (default stdout)")
    p.add_argument("--prefix", default="APP", help="area code for minted IDs, e.g. CHK")
    p.add_argument("--source", default="other", choices=["brd", "prd", "srs", "confluence", "wiki", "other"])
    p.add_argument("--source-name", default="")
    a = p.parse_args(argv)
    reqs = extract(to_text(a.file), a.prefix.upper())
    for r in reqs:
        r["source"] = a.source
    doc = {
        "source_name": a.source_name or a.file.name,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "requirements": reqs,
    }
    out = json.dumps(doc, indent=2, ensure_ascii=False)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(out + "\n", encoding="utf-8")
        with_ac = sum(1 for r in reqs if r["acceptance_criteria"])
        print(f"{len(reqs)} candidate requirements ({with_ac} with acceptance criteria) -> {a.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
