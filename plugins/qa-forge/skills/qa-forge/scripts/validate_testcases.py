#!/usr/bin/env python3
"""Validate a QA Forge test-cases.json: structure, IDs, steps, and (optionally) traceability to requirements.

Exit code 0 = no errors (warnings allowed), 1 = errors found.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from qa_common import PRIORITIES, load_list  # noqa: E402

ID_RE = re.compile(r"^TC-[A-Z0-9]+(-[A-Z0-9]+)*$")
VAGUE = re.compile(r"\b(works|correctly|properly|as expected|everything|fine|ok)\b", re.I)
LEVELS = {"unit", "api", "integration", "e2e", "ui", "manual-exploratory"}
RISKS = {"high", "medium", "low"}


def validate(cases, req_ids=None):
    errors, warnings = [], []
    seen = set()
    for i, tc in enumerate(cases):
        where = tc.get("id") or f"#{i}"
        tid = tc.get("id", "")
        if not tid:
            errors.append(f"{where}: missing id")
        elif not ID_RE.match(tid):
            errors.append(f"{where}: id must match TC-<AREA>-... (uppercase)")
        if tid in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(tid)
        if len(tc.get("title", "")) < 5:
            errors.append(f"{where}: title missing or too short")
        rids = tc.get("requirement_ids") or []
        if not rids:
            errors.append(f"{where}: no requirement_ids (traceability is mandatory)")
        elif req_ids is not None:
            for r in rids:
                if r not in req_ids:
                    errors.append(f"{where}: unknown requirement {r}")
        if tc.get("priority") not in PRIORITIES:
            errors.append(f"{where}: priority must be one of {', '.join(PRIORITIES)}")
        if tc.get("level") and tc["level"] not in LEVELS:
            errors.append(f"{where}: level '{tc['level']}' not in {sorted(LEVELS)}")
        if tc.get("risk") and tc["risk"] not in RISKS:
            errors.append(f"{where}: risk must be high|medium|low")
        steps = tc.get("steps") or []
        if not steps:
            errors.append(f"{where}: no steps")
        for n, st in enumerate(steps, 1):
            if not str(st.get("action", "")).strip():
                errors.append(f"{where} step {n}: empty action")
            exp = str(st.get("expected", "")).strip()
            if not exp:
                errors.append(f"{where} step {n}: empty expected result")
            elif VAGUE.search(exp) and len(exp) < 40:
                warnings.append(f"{where} step {n}: vague expected result '{exp}'")
    # suite-level: high-risk requirements should have at least one negative/boundary case
    by_req = {}
    for tc in cases:
        for r in tc.get("requirement_ids") or []:
            by_req.setdefault(r, []).append(tc)
    for r, tcs in by_req.items():
        if any(t.get("risk") == "high" for t in tcs):
            if not any(t.get("type") in ("negative", "boundary") or {"negative", "boundary"} & set(t.get("tags") or []) for t in tcs):
                warnings.append(f"{r}: high-risk requirement has no negative/boundary test case")
    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("test_cases")
    p.add_argument("--requirements", help="requirements.json to check traceability against")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = p.parse_args(argv)
    cases = load_list(a.test_cases, "test_cases")
    req_ids = None
    if a.requirements:
        req_ids = {r["id"] for r in load_list(a.requirements, "requirements")}
    errors, warnings = validate(cases, req_ids)
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    print(f"{len(cases)} test cases: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (a.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
