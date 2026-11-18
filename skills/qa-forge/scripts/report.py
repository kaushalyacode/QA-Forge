#!/usr/bin/env python3
"""Compute execution metrics from results.json / JUnit XML and draft a test summary report.

Applies exit criteria from qa-forge.config.json when given, and proposes GO / GO WITH RISKS / NO-GO.
Open defect counts come from --defects (JSON list of {"id","severity","status"}) exported from the tracker.
"""
import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from qa_common import load_json, load_list, load_results  # noqa: E402

STATUSES = ["pass", "fail", "blocked", "skipped", "flaky"]


def pct(a, b):
    return round(100 * a / b, 1) if b else 0.0


def compute(cases, results, defects, criteria):
    total = len(cases)
    by_status = Counter(results.get(t["id"], {}).get("status", "not run") for t in cases)
    executed = total - by_status.get("not run", 0) - by_status.get("skipped", 0)
    by_prio = {}
    for prio in ("P1", "P2", "P3", "P4"):
        ts = [t for t in cases if t.get("priority") == prio]
        if not ts:
            continue
        c = Counter(results.get(t["id"], {}).get("status", "not run") for t in ts)
        ex = len(ts) - c.get("not run", 0) - c.get("skipped", 0)
        by_prio[prio] = {"total": len(ts), "executed_pct": pct(ex, len(ts)), "pass_pct": pct(c.get("pass", 0), ex), **c}
    open_defects = Counter(d.get("severity", "S3")[:2].upper() for d in defects
                           if str(d.get("status", "open")).lower() not in ("closed", "done", "resolved", "verified"))
    m = {
        "total": total,
        "executed": executed,
        "pass_rate": pct(by_status.get("pass", 0), executed),
        "by_status": dict(by_status),
        "by_priority": by_prio,
        "open_defects": dict(open_defects),
        "flaky": sorted(t["id"] for t in cases if results.get(t["id"], {}).get("status") == "flaky"),
    }
    checks = []
    if criteria:
        def add(name, target, actual, ok):
            checks.append({"criterion": name, "target": target, "actual": actual, "met": ok})
        if "p1_executed_pct" in criteria and "P1" in by_prio:
            a = by_prio["P1"]["executed_pct"]
            add("P1 executed %", criteria["p1_executed_pct"], a, a >= criteria["p1_executed_pct"])
        if "p2_executed_pct" in criteria and "P2" in by_prio:
            a = by_prio["P2"]["executed_pct"]
            add("P2 executed %", criteria["p2_executed_pct"], a, a >= criteria["p2_executed_pct"])
        if "regression_pass_pct" in criteria:
            add("Pass rate %", criteria["regression_pass_pct"], m["pass_rate"], m["pass_rate"] >= criteria["regression_pass_pct"])
        for sev in ("s1", "s2"):
            k = f"max_open_{sev}"
            if k in criteria:
                a = open_defects.get(sev.upper(), 0)
                add(f"Open {sev.upper()} defects", f"<= {criteria[k]}", a, a <= criteria[k])
    m["exit_checks"] = checks
    blocking = [c for c in checks if not c["met"] and ("defects" in c["criterion"] or c["criterion"].startswith("P1"))]
    if blocking or by_status.get("fail", 0) and any(results.get(t["id"], {}).get("status") == "fail"
                                                   and t.get("priority") == "P1" for t in cases):
        m["recommendation"] = "NO-GO"
    elif any(not c["met"] for c in checks) or by_status.get("fail", 0) or by_status.get("blocked", 0):
        m["recommendation"] = "GO WITH RISKS"
    else:
        m["recommendation"] = "GO"
    return m


def to_markdown(m, title):
    s = m["by_status"]
    lines = [f"# Test Summary Report — {title}", "",
             f"**Recommendation: {m['recommendation']}** (draft — confirm with the QA lead)", "",
             "## Execution summary", "",
             "| Total | Passed | Failed | Blocked | Skipped | Flaky | Not run | Pass rate |",
             "|---|---|---|---|---|---|---|---|",
             f"| {m['total']} | {s.get('pass', 0)} | {s.get('fail', 0)} | {s.get('blocked', 0)} | {s.get('skipped', 0)} "
             f"| {s.get('flaky', 0)} | {s.get('not run', 0)} | {m['pass_rate']}% |", "",
             "### By priority", "", "| Priority | Total | Executed % | Pass % | Failed |", "|---|---|---|---|---|"]
    for p, v in m["by_priority"].items():
        lines.append(f"| {p} | {v['total']} | {v['executed_pct']}% | {v['pass_pct']}% | {v.get('fail', 0)} |")
    lines += ["", "## Open defects", "", "| S1 | S2 | S3 | S4 |", "|---|---|---|---|",
              "| " + " | ".join(str(m["open_defects"].get(k, 0)) for k in ("S1", "S2", "S3", "S4")) + " |", ""]
    if m["exit_checks"]:
        lines += ["## Exit criteria", "", "| Criterion | Target | Actual | Met? |", "|---|---|---|---|"]
        lines += [f"| {c['criterion']} | {c['target']} | {c['actual']} | {'yes' if c['met'] else '**no**'} |" for c in m["exit_checks"]]
        lines.append("")
    if m["flaky"]:
        lines += ["## Flaky tests", "", ", ".join(m["flaky"]), ""]
    lines += ["## Risks, coverage gaps and next steps", "", "_Add the RTM coverage line and analyst commentary here._", ""]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--test-cases", required=True)
    p.add_argument("--results", nargs="+", required=True, help="results.json and/or junit.xml (later wins)")
    p.add_argument("--defects", help="JSON list of defects with id/severity/status")
    p.add_argument("--config", help="qa-forge.config.json (for exit criteria)")
    p.add_argument("--title", default="Release")
    p.add_argument("-o", "--output")
    a = p.parse_args(argv)
    cases = load_list(a.test_cases, "test_cases")
    results = load_results(a.results)
    defects = load_list(a.defects, "defects") if a.defects else []
    criteria = load_json(a.config).get("exit_criteria", {}) if a.config else {}
    m = compute(cases, results, defects, criteria)
    md = to_markdown(m, a.title)
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"{m['recommendation']}: pass rate {m['pass_rate']}% -> {a.output}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
