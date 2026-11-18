---
description: Draft a defect from a failed test (with evidence) and file it in Jira or Azure DevOps after preview
argument-hint: "<TC-ID or failure description> [--jira|--ado]"
---

Use the `qa-forge` skill, Phase 7 (read `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/references/defects.md`). The `defect-triager` agent can handle batches.

Input: $ARGUMENTS

1. Gather the failure: test case, latest result, evidence paths, environment, build.
2. Search the tracker for duplicates; if one exists, propose a comment instead of a new bug.
3. Draft the report from `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/templates/bug-report.md` with severity and proposed priority.
4. Show the preview. Only after the user approves, create it via the Jira or Azure DevOps MCP, link it to the requirement and test case, and attach evidence. Without an MCP, save `qa/defects/<id>.md`.
5. Write the returned key into the result record's `defect_ids`.
