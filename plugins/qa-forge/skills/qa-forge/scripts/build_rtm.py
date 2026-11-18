#!/usr/bin/env python3
"""Build a Requirements Traceability Matrix: requirements x test cases x latest results (+ defects)."""
import argparse
import csv
import io
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from qa_common import load_list, load_results  # noqa: E402

ORDER = {"fail": 0, "blocked": 1, "flaky": 2, "not run": 3, "skipped": 4, "pass": 5}


def build(reqs, cases, results):
    rows = []
    for r in reqs:
        if r.get("status") in ("rejected", "deferred"):
            continue
        tcs = [t for t in cases if r["id"] in (t.get("requirement_ids") or [])]
        statuses = [results.get(t["id"], {}).get("status", "not run") for t in tcs]
        defects = sorted({d for t in tcs for d in results.get(t["id"], {}).get("defect_ids", [])})
        if not tcs:
            verdict = "NOT COVERED"
        elif not results:
            verdict = "designed"
        else:
            worst = min(statuses, key=lambda s: ORDER.get(s, 3))
            verdict = {"pass": "PASSED", "fail": "FAILED", "blocked": "BLOCKED", "flaky": "FLAKY"}.get(worst, "INCOMPLETE")
        rows.append({
            "requirement": r["id"],
            "source_id": r.get("source_id", ""),
            "title": r.get("title", ""),
            "priority": r.get("priority", ""),
            "test_cases": ", ".join(t["id"] for t in tcs),
            "results": ", ".join(f"{t['id']}:{s}" for t, s in zip(tcs, statuses)) if results else "",
            "defects": ", ".join(defects),
            "status": verdict,
        })
    covered = sum(1 for x in rows if x["status"] != "NOT COVERED")
    passed = sum(1 for x in rows if x["status"] == "PASSED")
    summary = {
        "requirements": len(rows),
        "covered": covered,
        "coverage_pct": round(100 * covered / len(rows), 1) if rows else 0.0,
        "passed": passed,
        "passed_pct": round(100 * passed / len(rows), 1) if rows else 0.0,
        "orphan_test_cases": sorted(t["id"] for t in cases
                                    if not set(t.get("requirement_ids") or []) & {r["id"] for r in reqs}),
    }
    return rows, summary


def to_markdown(rows, summary, with_results):
    cols = ["requirement", "source_id", "title", "priority", "test_cases"]
    if with_results:
        cols += ["results", "defects"]
    cols += ["status"]
    out = io.StringIO()
    out.write("# Requirements Traceability Matrix\n\n")
    out.write(f"**Coverage:** {summary['covered']}/{summary['requirements']} requirements "
              f"({summary['coverage_pct']}%)")
    if with_results:
        out.write(f" · **Passed:** {summary['passed']} ({summary['passed_pct']}%)")
    out.write("\n\n| " + " | ".join(c.replace("_", " ").title() for c in cols) + " |\n")
    out.write("|" + "---|" * len(cols) + "\n")
    for r in rows:
        out.write("| " + " | ".join(str(r[c]).replace("|", "\\|") for c in cols) + " |\n")
    if summary["orphan_test_cases"]:
        out.write(f"\nOrphan test cases (no known requirement): {', '.join(summary['orphan_test_cases'])}\n")
    return out.getvalue()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--requirements", required=True)
    p.add_argument("--test-cases", required=True)
    p.add_argument("--results", nargs="*", default=[], help="results.json and/or junit.xml files (later wins)")
    p.add_argument("-o", "--output", help=".md or .csv (default: markdown to stdout)")
    a = p.parse_args(argv)
    reqs = load_list(a.requirements, "requirements")
    cases = load_list(a.test_cases, "test_cases")
    results = load_results(a.results)
    rows, summary = build(reqs, cases, results)
    if a.output and a.output.endswith(".csv"):
        with open(a.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["requirement"])
            w.writeheader()
            w.writerows(rows)
    else:
        md = to_markdown(rows, summary, bool(results))
        if a.output:
            with open(a.output, "w", encoding="utf-8") as f:
                f.write(md)
        else:
            print(md)
    print(f"Coverage {summary['covered']}/{summary['requirements']} ({summary['coverage_pct']}%)"
          + (f", passed {summary['passed_pct']}%" if results else ""), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
