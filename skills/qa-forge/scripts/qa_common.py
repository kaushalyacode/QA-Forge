"""Shared helpers for QA Forge scripts (stdlib only)."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

TC_ID = re.compile(r"\bTC-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
PRIORITIES = ("P1", "P2", "P3", "P4")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_list(path, key):
    """Load a QA Forge file that is either {key: [...]} or a bare list."""
    data = load_json(path)
    if isinstance(data, list):
        return data
    return data.get(key, [])


def parse_junit(path):
    """Yield result dicts from a JUnit XML file, mapping test names to TC IDs."""
    root = ET.parse(path).getroot()
    out = []
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '')} {case.get('name', '')}"
        m = TC_ID.search(name.upper())
        if not m:
            continue
        if case.find("failure") is not None or case.find("error") is not None:
            status = "fail"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "pass"
        try:
            dur = float(case.get("time") or 0)
        except ValueError:
            dur = 0.0
        out.append({"test_case_id": m.group(0), "status": status, "duration_s": dur, "source": str(path)})
    return out


def load_results(paths):
    """Load results from any mix of results.json and junit .xml files.
    The last result per test case wins (pass after fail in a later file = retest)."""
    latest = {}
    for p in paths or []:
        p = Path(p)
        if p.suffix.lower() == ".xml":
            rows = parse_junit(p)
        else:
            rows = load_list(p, "results")
        for r in rows:
            latest[r["test_case_id"]] = r
    return latest
