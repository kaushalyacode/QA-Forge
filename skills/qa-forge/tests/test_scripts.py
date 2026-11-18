"""Unit tests for QA Forge scripts. Run: python -m unittest discover -s tests"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
EX = ROOT / "examples" / "checkout"

import build_rtm  # noqa: E402
import check_env  # noqa: E402
import export_tracker  # noqa: E402
import extract_requirements  # noqa: E402
import report  # noqa: E402
import validate_testcases  # noqa: E402
from qa_common import load_list, load_results  # noqa: E402


class ExtractTests(unittest.TestCase):
    def test_extracts_ids_stories_and_criteria(self):
        reqs = extract_requirements.extract(extract_requirements.to_text(EX / "PRD-checkout-promo.md"), "CHK")
        ids = [r["source_id"] for r in reqs]
        for native in ("FR-1", "FR-2", "FR-3", "NFR-1", "NFR-2"):
            self.assertIn(native, ids)
        self.assertTrue(any(r["title"].lower().startswith("as a returning shopper") for r in reqs))
        fr1 = next(r for r in reqs if r["source_id"] == "FR-1")
        self.assertEqual(len(fr1["acceptance_criteria"]), 2)
        nfr1 = next(r for r in reqs if r["source_id"] == "NFR-1")
        self.assertEqual(nfr1["type"], "performance")
        nfr2 = next(r for r in reqs if r["source_id"] == "NFR-2")
        self.assertEqual(nfr2["type"], "accessibility")
        self.assertEqual(len({r["id"] for r in reqs}), len(reqs))


class ValidateTests(unittest.TestCase):
    def test_example_is_valid(self):
        cases = load_list(EX / "test-cases.json", "test_cases")
        errors, _ = validate_testcases.validate(cases)
        self.assertEqual(errors, [])

    def test_catches_problems(self):
        bad = [{"id": "tc-1", "title": "x", "requirement_ids": [], "priority": "high",
                "steps": [{"action": "", "expected": ""}]},
               {"id": "TC-A-1", "title": "Duplicate check", "requirement_ids": ["REQ-NOPE"], "priority": "P1",
                "steps": [{"action": "click", "expected": "works"}]},
               {"id": "TC-A-1", "title": "Duplicate check", "requirement_ids": ["REQ-A-1"], "priority": "P1",
                "risk": "high", "steps": [{"action": "click", "expected": "ok"}]}]
        errors, warnings = validate_testcases.validate(bad, {"REQ-A-1"})
        text = "\n".join(errors)
        for needle in ("id must match", "title missing", "no requirement_ids", "priority must",
                       "empty action", "empty expected", "unknown requirement REQ-NOPE", "duplicate id"):
            self.assertIn(needle, text)
        self.assertTrue(any("vague" in w for w in warnings))
        self.assertTrue(any("high-risk" in w for w in warnings))


class RtmAndReportTests(unittest.TestCase):
    def setUp(self):
        self.reqs = [{"id": f"REQ-CHK-00{i}", "title": f"r{i}", "priority": "P1", "status": "approved"} for i in range(1, 7)]
        self.cases = load_list(EX / "test-cases.json", "test_cases")
        self.results = load_results([EX / "junit.xml", EX / "manual-results.json"])

    def test_results_merge_later_wins(self):
        self.assertEqual(self.results["TC-CHK-001-01"]["status"], "pass")      # junit only
        self.assertEqual(self.results["TC-CHK-002-01"]["defect_ids"], ["SHOP-981"])  # manual overrides junit
        self.assertEqual(self.results["TC-CHK-006-01"]["status"], "blocked")

    def test_rtm(self):
        rows, s = build_rtm.build(self.reqs, self.cases, self.results)
        status = {r["requirement"]: r["status"] for r in rows}
        self.assertEqual(status["REQ-CHK-001"], "PASSED")
        self.assertEqual(status["REQ-CHK-002"], "FAILED")
        self.assertEqual(status["REQ-CHK-003"], "INCOMPLETE")
        self.assertEqual(status["REQ-CHK-004"], "NOT COVERED")
        self.assertEqual(status["REQ-CHK-006"], "BLOCKED")
        self.assertEqual(s["covered"], 4)
        self.assertEqual(s["coverage_pct"], 66.7)
        md = build_rtm.to_markdown(rows, s, True)
        self.assertIn("SHOP-981", md)

    def test_report_no_go_on_failed_p1(self):
        defects = json.loads((EX / "defects.json").read_text())
        m = report.compute(self.cases, self.results, defects,
                           {"p1_executed_pct": 100, "max_open_s2": 0, "regression_pass_pct": 95})
        self.assertEqual(m["recommendation"], "NO-GO")
        self.assertEqual(m["open_defects"], {"S2": 1})
        self.assertIn("NO-GO", report.to_markdown(m, "2.4.0"))

    def test_report_go_when_all_pass(self):
        res = {t["id"]: {"test_case_id": t["id"], "status": "pass"} for t in self.cases}
        m = report.compute(self.cases, res, [], {"p1_executed_pct": 100, "max_open_s1": 0})
        self.assertEqual(m["recommendation"], "GO")


class ExportTests(unittest.TestCase):
    def test_all_formats(self):
        cases = load_list(EX / "test-cases.json", "test_cases")
        with tempfile.TemporaryDirectory() as d:
            export_tracker.ado(cases, os.path.join(d, "ado.csv"))
            ado = Path(d, "ado.csv").read_text().splitlines()
            self.assertTrue(ado[0].startswith("ID,Work Item Type,Title,Test Step"))
            self.assertEqual(sum(1 for line in ado if ",Test Case," in line), len(cases))
            export_tracker.xray(cases, os.path.join(d, "xray.csv"))
            export_tracker.zephyr(cases, os.path.join(d, "zephyr.csv"))
            files = export_tracker.gherkin(cases, os.path.join(d, "features"))
            feat = Path(files[0]).read_text()
            self.assertIn("@REQ-CHK-001 @TC-CHK-001-01 @P1", feat)
            self.assertIn("Scenario:", feat)


class McpProfileTests(unittest.TestCase):
    def test_all_profiles_valid_and_merge(self):
        import add_mcp_profile
        names = add_mcp_profile.available()
        self.assertIn("playwright", names)
        with tempfile.TemporaryDirectory() as d:
            target = Path(d, ".mcp.json")
            target.write_text(json.dumps({"mcpServers": {"playwright": {"command": "custom"}}}))
            added, skipped, _ = add_mcp_profile.merge(target, names)
            cfg = json.loads(target.read_text())
            self.assertEqual(cfg["mcpServers"]["playwright"]["command"], "custom")  # existing kept
            self.assertIn("playwright", skipped)
            self.assertIn("azure-devops", cfg["mcpServers"])
            self.assertNotIn("_notes", cfg)
            for spec in cfg["mcpServers"].values():
                self.assertTrue("command" in spec or "url" in spec)


class EnvTests(unittest.TestCase):
    def test_never_leaks_values(self):
        integ, _ = check_env.check({"BROWSERSTACK_USERNAME": "u", "BROWSERSTACK_ACCESS_KEY": "s3cret"})
        bs = next(r for r in integ if r["integration"] == "BrowserStack")
        self.assertTrue(bs["configured"])
        self.assertNotIn("s3cret", json.dumps(integ))


if __name__ == "__main__":
    unittest.main()
