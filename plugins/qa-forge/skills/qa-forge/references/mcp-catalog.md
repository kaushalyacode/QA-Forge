# MCP catalog for QA

Pick at least one server per job the team needs. Ready-to-merge configs are in this skill's `mcp-profiles/` folder — copy the `mcpServers` entry into your project `.mcp.json` (Claude Code) or client config. Secrets are referenced as `${VAR}`.

| Job | Server | Package / endpoint | Notes |
|---|---|---|---|
| Web UI automation | **Playwright MCP** (Microsoft) | `npx @playwright/mcp@latest` | Accessibility-snapshot driven; chromium/firefox/webkit/msedge; `--headless`, `--device`, `--storage-state`, `--save-trace`; Docker image `mcr.microsoft.com/playwright/mcp` |
| Web UI (WebDriver shops) | **Selenium MCP** (Angie Jones) | `npx -y @angiejones/mcp-selenium` | Reuses existing Selenium/Grid estates |
| Browser debugging, perf, network | **Chrome DevTools MCP** (Google) | `npx chrome-devtools-mcp@latest` | Performance traces, Lighthouse-style audits, console + network inspection; `--headless --isolated` for CI |
| Mobile (iOS/Android) | **Appium MCP** (official) | `npx -y appium-mcp@latest` | Needs Node 22+, JDK, Android SDK / Xcode; local or remote Appium |
| Real devices & browser cloud | **BrowserStack MCP** | `npx -y @browserstack/mcp-server@latest` | Run Playwright/Selenium suites on real devices, accessibility scans; needs a BrowserStack plan |
| API testing | **Postman MCP** | Postman's official server (remote or `npx @postman/postman-mcp-server`) | Collections, environments, run collections |
| Performance / load | **Grafana k6 MCP** | `mcp-k6` | Generate and run k6 scripts |
| Requirements & defects (Atlassian) | **Atlassian Rovo MCP** | `https://mcp.atlassian.com/v2/mcp` | Jira + Confluence; OAuth 2.1 or admin-enabled API token |
| Requirements & defects (Jira on-prem) | **mcp-atlassian** (community) | `uvx mcp-atlassian` | Server/DC with PAT |
| Requirements, test plans, pipelines (Azure) | **Azure DevOps MCP** (Microsoft) | `npx -y @azure-devops/mcp <org>` or remote `https://mcp.dev.azure.com/<org>` | Domains incl. `test-plans` (create plans/suites/cases, read results) |
| ADO on-prem | **mcp-server-azure-devops** (community) | `npx -y @tiberriver256/mcp-server-azure-devops` | PAT only |
| Test management | TestRail / Qase / Xray / Zephyr community or vendor servers | varies | Check the vendor first; else use `scripts/export_tracker.py` CSV import |
| CI results, PRs | **GitHub MCP** | `https://api.githubcopilot.com/mcp/` or Docker `ghcr.io/github/github-mcp-server` | Read Actions runs, annotate PRs with QA status |

Package names and flags move fast — before installing, confirm against the vendor README (`npx <pkg> --help`).

## Choosing a web automation server

| Need | Choose |
|---|---|
| Greenfield, fast, cross-browser, auto-wait | Playwright MCP |
| Existing Selenium code / Grid | Selenium MCP |
| "Why is this page slow / failing?" | Chrome DevTools MCP (pair with Playwright) |
| Real Safari/iOS, many devices | BrowserStack MCP |
| Native mobile apps | Appium MCP (or BrowserStack App Automate) |

## Combining servers — reference chain

1. Jira/ADO MCP → read story + acceptance criteria (Phase 1)
2. Design test cases (Phase 3), export to ADO Test Plans via `test-plans` tools or CSV
3. Playwright MCP → explore the page, record locators, run the scenario (Phase 6)
4. Chrome DevTools MCP → on failure, capture console/network/perf
5. Jira/ADO MCP → file the bug with evidence links (Phase 7)
6. GitHub/ADO pipelines → post summary to the PR (Phase 8)

## Context hygiene

Each MCP server adds tools to the model's context. Enable only what the current phase needs: ADO `-d` domains, Playwright `--caps` for optional capabilities, and disable idle servers in the client. The plugin's default `.mcp.json` ships only the zero-credential servers (Playwright, Chrome DevTools); everything else is opt-in via `mcp-profiles/`.
