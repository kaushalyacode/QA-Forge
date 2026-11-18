# Changelog

## 0.1.0 — 2026-11-18

### Added
- `qa-forge` skill: 9-phase QA workflow (connect, intake, risk, design, plan, RTM, execute, defects, report) with connected / assisted / manual modes.
- Requirements intake for BRD, PRD, SRS, Jira (JQL) and Azure DevOps (WIQL), testability review and ambiguity log.
- Guided authentication for Atlassian Rovo MCP (OAuth 2.1 / API token), Jira Server/DC (PAT), Azure DevOps (browser, Azure CLI, token env var, Entra remote), Azure DevOps Server (PAT), BrowserStack, Postman, TestRail, GitHub.
- MCP catalog and automation adapters for Playwright, Selenium, Appium, Chrome DevTools, BrowserStack, API testing; 15 ready-made MCP profiles.
- Scripts: `check_env`, `add_mcp_profile`, `extract_requirements`, `validate_testcases`, `build_rtm`, `export_tracker` (ADO / Xray / Zephyr / Gherkin), `report`.
- Templates: test plan, bug report, test summary report, project config. JSON Schemas for requirements, test cases, results.
- Claude Code plugin + marketplace: 9 slash commands, 5 role subagents, default Playwright + Chrome DevTools MCP servers.
- CI: unit tests (Python 3.9 / 3.13), plugin validation, example pipeline smoke test, skill zip artifact.
