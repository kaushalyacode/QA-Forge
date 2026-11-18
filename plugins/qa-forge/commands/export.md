---
description: Export test cases for import into Azure DevOps Test Plans, Jira Xray, Zephyr Scale, or as Gherkin feature files
argument-hint: "<ado|xray|zephyr|gherkin> [--filter-tag tag]"
---

Use the `qa-forge` skill. Prefer the connected tracker's MCP when it can create test cases directly (e.g. ADO `test-plans` domain) — ask before writing. Otherwise:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/validate_testcases.py qa/test-cases/test-cases.json
python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/export_tracker.py qa/test-cases/test-cases.json --format $ARGUMENTS -o qa/exports/<file>
```

Use `.csv` outputs for ado/xray/zephyr and a directory for gherkin. Tell the user where to import the file (ADO: Test Plans → suite → Import from CSV; Xray: Test Case Importer; Zephyr Scale: Import test cases from CSV).
