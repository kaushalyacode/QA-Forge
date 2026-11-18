---
description: Run a suite - guided manual execution, exploratory session, or automated run - and record results
argument-hint: "<smoke|regression|risk|REQ-IDs|TC-IDs> [--env staging] [--manual|--exploratory]"
---

Use the `qa-forge` skill, Phase 6 (read `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/references/execution.md`).

Suite and options: $ARGUMENTS

- `--manual`: walk the tester through one case at a time and record pass/fail/blocked with actual results and evidence.
- `--exploratory`: propose a charter, timebox it, take session notes, then turn repeatable findings into new test cases.
- Otherwise run automated cases via the configured adapter or the team's test command, collecting JUnit XML in the run folder.

Write `qa/runs/<YYYY-MM-DD>-<env>/results.json`. Offer (don't auto-run) `/qa-forge:bug` for each failure and ask before syncing results to Jira/ADO.
