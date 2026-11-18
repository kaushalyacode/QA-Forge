#!/usr/bin/env python3
"""Export QA Forge test cases for import into trackers when no MCP is connected.

Formats:
  ado      Azure DevOps Test Plans CSV (Work Item Type, Title, Test Step, Step Action, Step Expected, ...)
  xray     Jira Xray Test Case Importer CSV (one row per step, grouped by Test ID)
  zephyr   Zephyr Scale CSV (Name, Objective, Precondition, Step, Expected Result, ...)
  gherkin  .feature files, one per requirement area, tagged with REQ/TC IDs
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from qa_common import load_list  # noqa: E402

ADO_PRIORITY = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}


def ado(cases, path, area_path="", iteration_path=""):
    cols = ["ID", "Work Item Type", "Title", "Test Step", "Step Action", "Step Expected",
            "Priority", "Area Path", "Iteration Path", "Tags"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for tc in cases:
            tags = "; ".join([tc["id"], *tc.get("requirement_ids", []), *tc.get("tags", [])])
            pre = "; ".join(tc.get("preconditions", []))
            title = f"{tc['id']} {tc['title']}"
            w.writerow(["", "Test Case", title, "", "", "", ADO_PRIORITY.get(tc.get("priority"), 2),
                        area_path, iteration_path, tags])
            n = 1
            if pre:
                w.writerow(["", "", "", n, f"Preconditions: {pre}", "Preconditions are met", "", "", "", ""])
                n += 1
            for st in tc["steps"]:
                w.writerow(["", "", "", n, st["action"], st["expected"], "", "", "", ""])
                n += 1


def xray(cases, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Test ID", "Summary", "Priority", "Labels", "Requirement", "Precondition", "Action", "Data", "Expected Result"])
        for i, tc in enumerate(cases, 1):
            labels = " ".join([tc["id"], *tc.get("tags", [])])
            data = "; ".join(f"{k}={v}" for k, v in (tc.get("test_data") or {}).items())
            for j, st in enumerate(tc["steps"]):
                first = j == 0
                w.writerow([i, tc["title"] if first else "", tc.get("priority", "") if first else "",
                            labels if first else "", ",".join(tc.get("requirement_ids", [])) if first else "",
                            "; ".join(tc.get("preconditions", [])) if first else "",
                            st["action"], data if first else "", st["expected"]])


def zephyr(cases, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Objective", "Precondition", "Priority", "Labels", "Coverage (Issues)", "Step", "Test Data", "Expected Result"])
        for tc in cases:
            for j, st in enumerate(tc["steps"]):
                first = j == 0
                w.writerow([f"{tc['id']} {tc['title']}" if first else "", tc["title"] if first else "",
                            "\n".join(tc.get("preconditions", [])) if first else "",
                            {"P1": "High", "P2": "Normal", "P3": "Low", "P4": "Low"}.get(tc.get("priority"), "Normal") if first else "",
                            " ".join(tc.get("tags", [])) if first else "",
                            ",".join(tc.get("requirement_ids", [])) if first else "",
                            st["action"], "", st["expected"]])


def gherkin(cases, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    groups = defaultdict(list)
    for tc in cases:
        area = tc["id"].split("-")[1] if "-" in tc["id"] else "MISC"
        groups[area].append(tc)
    written = []
    for area, tcs in groups.items():
        lines = [f"Feature: {area} acceptance tests", ""]
        for tc in tcs:
            tags = " ".join("@" + t for t in [*tc.get("requirement_ids", []), tc["id"], tc.get("priority", "")] if t)
            lines += [f"  {tags}", f"  Scenario: {tc['title']}"]
            for k, pre in enumerate(tc.get("preconditions", [])):
                lines.append(f"    {'Given' if k == 0 else 'And'} {pre}")
            for k, st in enumerate(tc["steps"]):
                kw = "When" if k == 0 else "And"
                lines.append(f"    {kw} {st['action']}")
                lines.append(f"    Then {st['expected']}")
            lines.append("")
        p = os.path.join(out_dir, f"{re.sub(r'[^a-z0-9]+', '_', area.lower())}.feature")
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        written.append(p)
    return written


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("test_cases")
    p.add_argument("--format", required=True, choices=["ado", "xray", "zephyr", "gherkin"])
    p.add_argument("-o", "--output", required=True, help="CSV path, or output directory for gherkin")
    p.add_argument("--area-path", default="", help="ADO Area Path")
    p.add_argument("--iteration-path", default="", help="ADO Iteration Path")
    p.add_argument("--filter-tag", help="only export cases with this tag")
    a = p.parse_args(argv)
    cases = load_list(a.test_cases, "test_cases")
    if a.filter_tag:
        cases = [c for c in cases if a.filter_tag in (c.get("tags") or [])]
    if a.format == "ado":
        ado(cases, a.output, a.area_path, a.iteration_path)
    elif a.format == "xray":
        xray(cases, a.output)
    elif a.format == "zephyr":
        zephyr(cases, a.output)
    else:
        files = gherkin(cases, a.output)
        print(f"wrote {len(files)} feature file(s) to {a.output}", file=sys.stderr)
        return 0
    print(f"exported {len(cases)} test cases -> {a.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
