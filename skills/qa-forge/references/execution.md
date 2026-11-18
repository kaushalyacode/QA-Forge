# Phase 6b — Execution (manual, automated, exploratory)

## Before a run

- Entry criteria from the test plan met (build deployed, smoke green, data seeded).
- Create a run folder: `qa/runs/<YYYY-MM-DD>-<env>/`.
- Choose the suite: `smoke` (P1 happy paths), `regression` (tags), `feature` (REQ IDs in scope), or `risk` (risk = high).

## Manual guided execution

Walk the tester through one case at a time: show preconditions + test data, then each step with its expected result, and record `pass | fail | blocked | skipped` plus actual result and evidence path. Write results in `results.json` (schema `schemas/results.schema.json`):

```json
{"run_id": "2026-11-18-staging", "environment": "staging", "build": "2.4.0-rc1",
 "results": [{"test_case_id": "TC-CHK-004-02", "status": "fail", "executed_by": "kau",
   "executed_at": "2026-11-18T14:02:00Z", "duration_s": 95,
   "actual": "Total dropped to $40.00", "evidence": ["shots/tc-chk-004-02.png"], "defect_ids": []}]}
```

## Exploratory sessions

Session-based: charter ("Explore X with Y to discover Z"), timebox 30–90 min, notes, bugs, questions, coverage areas. Save as `qa/runs/<run>/exploratory-<area>.md`. Convert repeatable findings into new test cases.

## Automated runs

Run via the adapter (see `automation-adapters.md`) or the team's CI. Collect JUnit XML into the run folder. `scripts/report.py` maps JUnit testcases back to TC IDs by finding `TC-…` in the test name.

## Syncing results to trackers

- **Azure DevOps Test Plans** (connected, `test-plans` domain): ensure plan → suite → test cases exist; record outcomes per test point. If the MCP version lacks a result-update tool, publish JUnit from the pipeline (`PublishTestResults@2`) instead.
- **Jira + Xray/Zephyr**: import JUnit via the vendor's REST import or the CI plugin; otherwise attach the summary report to the release/epic.
- Ask before writing results to a tracker (rule 4).

## Flaky tests

A test that passes on retry is **flaky**, not passed. Tag it `flaky`, quarantine from the gating suite, and open a maintenance task with the failure pattern (timing, data, order dependency, environment).

## Exit

Check exit criteria from the plan (e.g. 100% P1 executed, 0 open critical/high defects, ≥95% pass on regression), then go to Phase 8.
