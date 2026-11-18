# qa-forge plugin

Bundles the `qa-forge` skill with slash commands, role-based subagents and default MCP servers.

## Install

```bash
/plugin install qa-forge --marketplace kaushalyacode/QA-Forge
```

On older Claude Code versions: `/plugin marketplace add kaushalyacode/QA-Forge` then `/plugin install qa-forge@qa-forge`.

## Components

| Type | Name | Purpose |
|---|---|---|
| Skill | `qa-forge` | The full framework (phases, references, templates, schemas, scripts, MCP profiles) |
| Command | `/qa-forge:setup` | Detect MCP servers, guide Jira/ADO/automation auth, create `qa/` workspace |
| Command | `/qa-forge:intake` | BRD/PRD file, Jira key/JQL, ADO id/WIQL → `requirements.json` + ambiguity log |
| Command | `/qa-forge:design` | Risk-based test cases + validation + RTM (`--gherkin` optional) |
| Command | `/qa-forge:plan` | Release test plan |
| Command | `/qa-forge:automate` | Automate cases via Playwright/Selenium/Appium/BrowserStack/API MCP + durable code |
| Command | `/qa-forge:execute` | Manual guided, exploratory or automated run → results |
| Command | `/qa-forge:bug` | Draft, de-duplicate and (after approval) file defects in Jira/ADO |
| Command | `/qa-forge:report` | RTM + test summary report with GO / NO-GO draft |
| Command | `/qa-forge:export` | ADO Test Plans / Xray / Zephyr CSV, Gherkin |
| Agent | `requirements-analyst` | Intake + testability review |
| Agent | `test-designer` | Test case design + coverage |
| Agent | `automation-engineer` | MCP-driven automation + code generation |
| Agent | `defect-triager` | Bug drafts + duplicate detection (never files on its own) |
| Agent | `qa-reporter` | Metrics, exit criteria, summary report |
| MCP | `playwright`, `chrome-devtools` | Zero-credential defaults (Node 18+ / `npx`) |

Credentialed servers (Jira Cloud/self-hosted, Azure DevOps cloud/on-prem, BrowserStack, Appium, Selenium, GitHub) are opt-in — `/qa-forge:setup` adds them to your project `.mcp.json` from `skills/qa-forge/mcp-profiles/`.

## Typical flow

```
/qa-forge:setup jira
/qa-forge:intake "project = SHOP AND fixVersion = 2.4.0"
/qa-forge:design all
/qa-forge:plan 2.4.0
/qa-forge:automate tag:smoke --with playwright
/qa-forge:execute regression --env staging
/qa-forge:bug TC-CHK-002-01 --jira
/qa-forge:report 2.4.0
```
