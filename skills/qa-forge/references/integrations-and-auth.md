# Phase 0 — Integrations & authentication (guided)

Walk the user through this once per project. Output a status table:

```
| Integration      | Mode       | Auth method        | Status | Next step |
|------------------|------------|--------------------|--------|-----------|
| Jira Cloud       | Connected  | OAuth 2.1 (Rovo)   | OK     | –         |
| Azure DevOps     | Assisted   | PAT (env)          | Missing| Create PAT, scopes below |
| Playwright MCP   | Connected  | none               | OK     | –         |
```

## Step 1 — Detect what's already there

1. Look at the tool list for MCP tools whose names contain `jira`, `atlassian`, `azure`/`ado`/`devops`, `playwright`, `selenium`, `appium`, `browserstack`, `chrome-devtools`, `postman`, `testrail`, `xray`, `zephyr`, `qase`, `github`.
2. Run `python scripts/check_env.py` — it lists which credential env vars are set (names only, never values) and which CLIs (`az`, `gh`, `npx`, `java`, `adb`) exist.
3. Read `qa/qa-forge.config.json` if present.

## Step 2 — Pick the auth path per system

### Jira / Confluence (Atlassian Cloud) — official Rovo MCP server

- Endpoint: `https://mcp.atlassian.com/v2/mcp` (Streamable HTTP). Older setups use `/v1/mcp` — v2 exposes the newer tool set; follow the Atlassian setup guide for your client.
- **OAuth 2.1 (interactive, recommended for people):** add the server, the client opens a browser consent screen, pick the site. Actions respect the user's Jira permissions.
- **API token (headless/CI):** disabled by default — an **org admin** must enable *Allow API token authentication* in admin.atlassian.com → Security → Rovo MCP server. Then either
  - personal token: `Authorization: Basic base64(email:api_token)`, or
  - service-account key: `Authorization: Bearer <key>`.
  Minimum scopes: `read:jira-work`, `write:jira-work` (only if creating bugs), `read:jira-user`.
- Claude Code:
  ```bash
  claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp
  # headless variant
  claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp \
    --header "Authorization: Basic ${ATLASSIAN_BASIC_AUTH}"
  ```
- Claude.ai / desktop: add the Atlassian connector from the connectors directory.

### Jira Server / Data Center (self-hosted)

Rovo doesn't cover on-prem. Use the community `mcp-atlassian` server (Python, `uvx mcp-atlassian`) with a **Personal Access Token**:
`JIRA_URL`, `JIRA_PERSONAL_TOKEN` (Server/DC) or `JIRA_USERNAME` + `JIRA_API_TOKEN` (Cloud). Profile: `mcp-profiles/jira-selfhosted.json`.

### Azure DevOps Services (cloud) — official Microsoft server

- **Remote (preview)** `https://mcp.dev.azure.com/<org>` — Microsoft Entra ID OAuth only. Some clients (Claude Desktop/Code, Cursor) can't complete Entra auth to it yet; if it fails, use local.
- **Local** `npx -y @azure-devops/mcp <org>` (Node 20+). Auth options:
  - Interactive browser login (default)
  - `--authentication azcli` after `az login` (good for devs already on Azure CLI)
  - `--authentication envvar` with `ADO_MCP_AUTH_TOKEN` (headless/CI)
- Limit tools with domains: `-d core work work-items test-plans` (always include `core`). Add `pipelines` to read test results from builds, `repositories` for PR checks.
- **PAT scopes** (least privilege for QA): Work Items *Read & write*, Test Management *Read & write*, Build *Read*, Code *Read*. Create at `https://dev.azure.com/<org>/_usersSettings/tokens`, expiry ≤ 90 days.

### Azure DevOps Server (on-prem)

PAT only. Community server `@tiberriver256/mcp-server-azure-devops` with `AZURE_DEVOPS_ORG_URL=https://server/tfs/Collection`, `AZURE_DEVOPS_AUTH_METHOD=pat`, `AZURE_DEVOPS_PAT`. Profile: `mcp-profiles/ado-onprem.json`.

### Automation / device clouds

| System | Auth | Env vars |
|---|---|---|
| Playwright MCP | none (local browser). For logged-in tests use `--storage-state` with a saved auth file, never typed passwords in prompts | – |
| Selenium MCP | none locally; Grid URL if remote | `SELENIUM_REMOTE_URL` (optional) |
| Appium MCP | none; needs SDKs | `ANDROID_HOME`, optional `CAPABILITIES_CONFIG` |
| Chrome DevTools MCP | none | – |
| BrowserStack MCP | username + access key | `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY` |
| Postman MCP | API key | `POSTMAN_API_KEY` |
| TestRail (community MCP) | user + API key | `TESTRAIL_URL`, `TESTRAIL_USERNAME`, `TESTRAIL_API_KEY` |
| GitHub MCP | OAuth or fine-grained PAT (Actions read, Issues r/w) | `GITHUB_PERSONAL_ACCESS_TOKEN` |

## Step 3 — Store secrets safely

- Put secrets in the shell profile / OS keychain / CI secret store, referenced from MCP config as `${VAR}`. Claude Code expands `${VAR}` in `.mcp.json`.
- Add `qa/.env` and `*.auth.json` / `storageState*.json` to `.gitignore`.
- Never paste a token into chat. If the user does, tell them to rotate it.
- Prefer OAuth for humans and service accounts/PATs with expiry for CI.

## Step 4 — Smoke test each connection

| System | Read-only smoke call |
|---|---|
| Jira | Search `project = <KEY> ORDER BY created DESC` limit 1 |
| ADO | List projects (core), then one WIQL query |
| Playwright | Navigate to the app base URL, take an accessibility snapshot |
| BrowserStack | List available browsers/devices |

Record results in the status table and in `qa/qa-forge.config.json` → `integrations.<name>.status`.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Jira 401 with API token | Admin hasn't enabled API-token auth for Rovo MCP, or wrong email/token pair |
| Jira site not selectable | Site not linked to an Atlassian organization, or IP allowlist blocks the MCP |
| ADO 203/401 | PAT expired or missing scope; org name misspelled; on-prem URL needs collection path |
| ADO remote server won't auth in Claude | Entra-only remote; switch to local `@azure-devops/mcp` with `azcli` or `envvar` |
| Playwright "browser not installed" | `npx playwright install chromium` |
| Appium session fails | `ANDROID_HOME` wrong, emulator not booted (`adb devices`), or Appium driver missing (`appium driver install uiautomator2`) |
