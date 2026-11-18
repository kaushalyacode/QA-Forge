# Phase 6a — Automation adapters

One test case (`test-cases.json`) → executed or turned into code through whichever adapter is available. Each adapter has the same contract:

1. **Input**: a validated test case with `automation.candidate = true`.
2. **Explore** the target live (MCP) to get real, stable locators — never invent selectors.
3. **Run** the steps, asserting each `expected`.
4. **Capture evidence** on failure (screenshot, trace, console, network).
5. **Emit** a result record (`schemas/results.schema.json`) and, when asked, durable code in the team's framework.
6. **Update** the test case: `automation.status`, `framework`, `path`.

## Locator policy (all web/mobile adapters)

Prefer, in order: role + accessible name → label → test id (`data-testid`) → text → CSS. No XPath on layout, no nth-child, no auto-generated class names. If the app lacks test ids on critical controls, log it as a testability improvement.

## Playwright MCP

- Flow: `browser_navigate` → `browser_snapshot` (accessibility tree gives refs) → `browser_click` / `browser_type` / `browser_fill_form` / `browser_select_option` → `browser_snapshot` or `browser_wait_for` to assert → `browser_take_screenshot` on failure. Read `browser_console_messages` and `browser_network_requests` when a step fails.
- Logged-in flows: start the server with `--storage-state=qa/.auth/user.json` (gitignored) rather than typing credentials.
- Devices: `--device "iPhone 15"`; browsers: `--browser firefox|webkit|msedge`.
- Durable code: generate `@playwright/test` TypeScript using `getByRole`/`getByLabel`/`getByTestId` and web-first assertions (`await expect(locator).toHaveText(...)`). Put the IDs in the title so JUnit output maps back:
  ```ts
  test('TC-CHK-004-02 Expired promo code is rejected @REQ-CHK-004 @P1', async ({ page }) => { ... });
  ```
  Run with `npx playwright test --reporter=junit,html` → `qa/runs/<run>/junit.xml`.

## Selenium MCP

- Flow: `start_browser` → `navigate` → `find_element` / `click_element` / `send_keys` / `get_element_text` → `take_screenshot`.
- Durable code: match the team's language (Java + JUnit5/TestNG, Python + pytest, C# + NUnit). Use explicit waits, Page Object Model, IDs in test names.

## Appium MCP

- Prereqs: emulator/simulator running (`adb devices` / `xcrun simctl list`), Appium driver installed.
- Flow: create session with capabilities (platformName, `appium:automationName` UiAutomator2/XCUITest, `appium:app` or bundle id, `appium:udid` for remote) → find by accessibility id → act → screenshot/page source on failure.
- Prefer accessibility ids; they double as a11y checks.

## Chrome DevTools MCP

Diagnostic companion, not a test runner: performance trace for NFR checks (LCP, INP, CLS against the thresholds in the REQ), console errors during a scenario, failing network calls. Attach findings to the defect.

## BrowserStack MCP

Use to run an existing Playwright/Selenium suite across a browser/device matrix or for real-device manual sessions and accessibility scans. Build the matrix from the pairwise design (Phase 3), not "everything".

## API (Postman MCP or plain HTTP)

For `level: api` test cases: one request per step, assert status, schema and key fields; chain auth tokens via environment variables, never hard-code. Export to a Postman collection or to code (pytest + requests, REST Assured, supertest) as the team prefers.

## Accessibility

On every e2e UI case marked `accessibility` or high-risk: keyboard-only pass, check snapshot for missing names/roles, and run axe (`@axe-core/playwright`) in generated code. Report against WCAG 2.2 AA.

## No MCP available

Generate the durable code anyway, tell the user the exact run command, and ask them to share the JUnit XML — `scripts/report.py` ingests it.
