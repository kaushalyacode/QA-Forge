---
name: qa-forge
description: End-to-end QA team workflow framework. Use whenever the user wants to test software or run QA work - turning BRDs, PRDs, user stories, Jira issues or Azure DevOps work items into test scenarios and test cases, building a test plan or requirements traceability matrix (RTM), automating or executing tests through MCP servers (Playwright, Selenium, Appium, Chrome DevTools, BrowserStack, Postman and others), logging defects back to Jira or Azure DevOps, or producing test summary / release-readiness reports. Also use for setting up or authenticating QA tool integrations.
---

# QA Forge

A tool-agnostic framework that takes a QA team from **requirements → test design → execution → defects → reporting**, with every artifact traceable back to a requirement ID.

It does not assume any one tool. Every phase works in three modes, picked at runtime:

| Mode | When | How |
|---|---|---|
| **Connected** | An MCP server for the job is available (tool names visible) | Call the MCP tools directly |
| **Assisted** | No MCP, but a CLI/API or export path exists | Use `scripts/` to produce import files (CSV/JSON) the user uploads |
| **Manual** | Nothing connected | Produce documents + checklists; a human executes |

Never block on a missing integration — degrade to the next mode and say so in one line.

## Phase map

Run phases in order for a new feature; jump straight to a phase when asked for one thing ("write test cases for PROJ-123" → phases 1+3 only).

| # | Phase | Output | Reference |
|---|---|---|---|
| 0 | Connect & authenticate | Integration status table | `references/integrations-and-auth.md`, `references/mcp-catalog.md` |
| 1 | Requirements intake | `requirements.json` (normalized REQ-IDs + acceptance criteria) | `references/requirements-intake.md` |
| 2 | Analysis & risk | Ambiguity log, risk-ranked requirement list | `references/test-design.md` §Risk |
| 3 | Test design | `test-cases.json` (+ optional Gherkin) | `references/test-design.md` |
| 4 | Test planning | Test plan document | `templates/test-plan.md` |
| 5 | Traceability | `rtm.md` / `rtm.csv` | `scripts/build_rtm.py` |
| 6 | Execution & automation | Results JSON / JUnit XML + evidence | `references/automation-adapters.md`, `references/execution.md` |
| 7 | Defect management | Bug reports, pushed to tracker | `references/defects.md`, `templates/bug-report.md` |
| 8 | Reporting | Test summary report + go/no-go recommendation | `templates/test-summary-report.md`, `scripts/report.py` |

Read only the reference for the phase you are in.

## Workspace convention

Keep all artifacts in a `qa/` folder at the project root (create it if missing) so phases can hand off to each other and the team can commit it:

```
qa/
  qa-forge.config.json     # integrations, project keys, environments (no secrets)
  requirements/requirements.json
  test-cases/test-cases.json
  plans/<release>-test-plan.md
  runs/<date>-<env>/results.json   # + junit.xml, screenshots, traces
  defects/<BUG-ID>.md
  reports/<release>-summary.md
  rtm.md
```

Start from `templates/qa-forge.config.json`. Secrets **never** go in this folder — they live in environment variables or the MCP client's credential store (see auth reference).

## Core rules

1. **Traceability is mandatory.** Every test case carries `requirement_ids`; every defect carries `test_case_id` and `requirement_ids`. Run `scripts/build_rtm.py` after design and after execution; report uncovered requirements explicitly.
2. **Requirements first, then ask.** Ambiguities found in phase 1–2 go in an ambiguity log with a proposed assumption. Proceed on the assumption and flag it — don't stall the team — unless the ambiguity changes pass/fail of a critical-path test.
3. **Validate before handing off.** Run `scripts/validate_testcases.py` on any test-case file before exporting it or automating it.
4. **Read-only by default on trackers.** Reading Jira/ADO is free; creating or transitioning issues, test runs or bugs needs the user's go-ahead once per session (a batch preview first for >5 items).
5. **Evidence or it didn't happen.** A failed automated step records a screenshot/trace/console log path; a manual failure records actual vs expected.
6. **Least privilege.** Ask for the narrowest token scopes listed in the auth reference. Never echo, log or commit a token.

## Quick start

- *"Set up QA Forge"* → Phase 0: run `python scripts/check_env.py`, list available MCP tools, fill the config, show the status table.
- *"Here's the PRD, give me test cases"* → Phase 1 (`scripts/extract_requirements.py <file>`), then Phase 3, then validate + RTM.
- *"Automate TC-012 with Playwright"* → Phase 6, Playwright adapter.
- *"Log this failure in Jira/ADO"* → Phase 7.
- *"Are we ready to release?"* → Phase 8 with `scripts/report.py`.

## Scripts (Python 3.9+, stdlib only)

| Script | Purpose |
|---|---|
| `check_env.py` | Reports which integration credentials/env vars are present (never prints values) |
| `add_mcp_profile.py` | Merges ready-made server configs from `mcp-profiles/` (Playwright, Selenium, Appium, Chrome DevTools, BrowserStack, Jira Cloud/self-hosted, ADO cloud/on-prem, GitHub) into the project `.mcp.json` |
| `extract_requirements.py` | Pulls candidate requirements + acceptance criteria out of a BRD/PRD (md/txt/html) into `requirements.json` |
| `validate_testcases.py` | Schema + traceability checks on `test-cases.json` |
| `build_rtm.py` | Requirements × test cases × results → RTM (md/csv) with coverage % |
| `export_tracker.py` | Test cases → Azure DevOps test-case CSV, Jira (Xray/Zephyr) CSV, or Gherkin |
| `report.py` | Merges JUnit XML + manual results into metrics and a summary-report draft |

Run any script with `--help` for options. Schemas live in `schemas/`.
