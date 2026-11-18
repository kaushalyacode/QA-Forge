---
description: Automate test cases through an available MCP server (Playwright, Selenium, Appium, BrowserStack, API) and generate durable test code
argument-hint: "<TC-IDs | tag> [--with playwright|selenium|appium|browserstack|api] [--code-only]"
---

Use the `qa-forge` skill, Phase 6 (read `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/references/automation-adapters.md`). Consider delegating to the `automation-engineer` agent for more than three test cases.

Target: $ARGUMENTS

1. Load the cases from `qa/test-cases/test-cases.json`; validate them first.
2. Pick the adapter: the one named with `--with`, else `integrations.automation` in `qa/qa-forge.config.json`, else whichever matching MCP server is available.
3. Unless `--code-only`, drive the app live through the MCP server to discover real locators and run the steps, capturing evidence on failure.
4. Generate durable code in the team's framework under `integrations.automation.code_path`, with the TC and REQ IDs in each test title.
5. Update each case's `automation` block and write results to `qa/runs/<date>-<env>/results.json`.

Report: automated, passed, failed (with evidence paths), and anything not automatable and why.
