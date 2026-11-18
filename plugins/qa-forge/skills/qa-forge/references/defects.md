# Phase 7 — Defect management

## Before filing

1. Reproduce at least twice; note the reproduction rate if intermittent.
2. Search the tracker for duplicates (Jira: `project = KEY AND type = Bug AND text ~ "promo expired" AND statusCategory != Done`; ADO: WIQL `[System.WorkItemType] = 'Bug' AND [System.Title] CONTAINS 'promo'`). If found, comment with new evidence instead of filing.
3. Isolate: smallest steps, which environments/browsers, first bad build if known.

## Severity vs priority

| Severity | Meaning |
|---|---|
| S1 Critical | Crash, data loss/corruption, security breach, core journey blocked with no workaround |
| S2 High | Major function broken, workaround is painful |
| S3 Medium | Function partly wrong, reasonable workaround |
| S4 Low | Cosmetic, copy, minor UX |

Priority (P1–P4) is the business's fix order; propose it, let the triage owner set it.

## Bug report content

Use `templates/bug-report.md`. Required: title (`[Area] Symptom when condition`), environment + build, preconditions, numbered steps, expected, actual, severity, evidence, linked `test_case_id` and `requirement_ids`, reproduction rate.

## Field mapping

| QA Forge | Jira | Azure DevOps |
|---|---|---|
| title | Summary | System.Title |
| description (env, preconditions, steps, expected, actual) | Description | Microsoft.VSTS.TCM.ReproSteps (HTML) |
| severity | Severity custom field or label `severity-s2` | Microsoft.VSTS.Common.Severity (`2 - High`) |
| priority | Priority | Microsoft.VSTS.Common.Priority (1–4) |
| environment | Environment | Microsoft.VSTS.TCM.SystemInfo |
| requirement link | Issue link "is caused by"/"relates to" the story | Related / Tested By link to the story |
| test case link | Link to Xray/Zephyr test | Tested By link to the Test Case work item |
| evidence | Attachments | Attachments |
| build | Affects Version | Microsoft.VSTS.Build.FoundIn |

Fill project-specific custom field ids in `qa-forge.config.json → integrations.jira.field_map`.

## Filing

Connected: show the user a preview (one block per bug, or a table for a batch), then create via the Jira/ADO MCP and link. Assisted: write `qa/defects/<id>.md` and a CSV for bulk import. Put the returned key into the result record's `defect_ids`.

## Retest & close

When a fix lands: re-run the linked test case(s) plus neighbours in the same area (regression around the fix), comment the result with build number, then transition (Jira: *Done/Verified*; ADO: *Closed* or *Resolved → Closed*) — with user approval.
