# Test Plan — {{Product}} {{Release}}

| Field | Value |
|---|---|
| Version | 1.0 |
| Owner (QA lead) | {{name}} |
| Requirement sources | {{BRD/PRD links, Jira JQL or ADO query}} |
| Last updated | {{YYYY-MM-DD}} |

## 1. Objective
What this round of testing must prove, in one or two sentences.

## 2. Scope
**In scope** — features / REQ IDs: {{REQ-… list or query}}
**Out of scope** — with reason: {{…}}

## 3. Test approach
| Level | What | Who | Tooling |
|---|---|---|---|
| API | Business rules, contracts | SDET | Postman MCP / pytest |
| E2E UI | Critical journeys | SDET | Playwright MCP |
| Mobile | {{…}} | {{…}} | Appium MCP / BrowserStack |
| Manual / exploratory | New & high-risk areas | QA | Charters |
| Non-functional | Performance {{targets}}, security {{scope}}, accessibility WCAG 2.2 AA | {{…}} | Chrome DevTools MCP, k6, axe |

Techniques and depth follow the risk table (`references/test-design.md`).

## 4. Risk register
| REQ-ID | Risk | Likelihood | Impact | Score | Mitigation |
|---|---|---|---|---|---|

## 5. Environments & data
| Env | URL | Build source | Data strategy | Accounts (secret store reference, never the secret) |
|---|---|---|---|---|

Browser/device matrix: {{from pairwise design}}

## 6. Entry criteria
- Build deployed to {{env}}, smoke suite green
- Requirements in scope are `approved`; ambiguity log has no blocking items
- Test data and accounts available

## 7. Exit criteria
- 100% of P1 and ≥{{90}}% of P2 test cases executed
- 0 open S1/S2 defects; S3 have agreed owners/dates
- Regression pass rate ≥{{95}}% (flaky excluded and listed)
- Requirement coverage {{100}}% for in-scope REQs (RTM)

## 8. Suspension & resumption
Suspend if: smoke fails, environment down > {{2h}}, > {{30}}% blocked. Resume when the cause is fixed and smoke is green.

## 9. Deliverables
Test cases (`qa/test-cases/`), RTM (`qa/rtm.md`), run results (`qa/runs/`), defects (tracker), summary report (`qa/reports/`).

## 10. Schedule & roles
| Milestone | Date | Owner |
|---|---|---|

## 11. Approvals
| Role | Name | Date |
|---|---|---|
