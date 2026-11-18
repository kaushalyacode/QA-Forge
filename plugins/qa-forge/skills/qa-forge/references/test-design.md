# Phases 2–3 — Risk analysis and test design

## Risk-based prioritization (Phase 2)

Score each requirement: **Risk = Likelihood (1–3) × Impact (1–3)**.

- Likelihood ↑: new code, complex logic, many integrations, history of defects, unclear requirement.
- Impact ↑: money, security/privacy, legal/compliance, data loss, core user journey, many users.

| Score | Level | Design depth | Automation |
|---|---|---|---|
| 7–9 | High | All applicable techniques below, negative + edge cases, NFR checks | Automate the happy path + top negatives; run every build |
| 4–6 | Medium | EP + BVA + main negatives | Automate the happy path |
| 1–3 | Low | Happy path + one negative | Manual/exploratory |

Record as `risk` on each test case (`high|medium|low`) so the plan and report can slice by it.

## Design techniques (Phase 3)

Pick per requirement; note the technique in the test case `technique` field.

| Technique | Use when | Example |
|---|---|---|
| Equivalence partitioning (EP) | Input ranges / classes | Age: <18, 18–65, >65, non-numeric |
| Boundary value analysis (BVA) | Numeric/length limits | Password 8–64 chars → 7, 8, 64, 65 |
| Decision table | Combinations of business rules | Discount by member tier × cart value × promo |
| State transition | Workflows / statuses | Order: created → paid → shipped → delivered / cancelled |
| Pairwise / combinatorial | Many config params | Browser × OS × locale × role |
| Use-case / user journey | End-to-end flows | Guest checkout with saved address |
| Error guessing | Known weak spots | Double-submit, back button, expired session, emoji, RTL text |
| CRUD matrix | Data entities | Create/read/update/delete × role permissions |
| Exploratory charter | Novel or vague areas | "Explore promo codes with stacking attempts for 30 min" |

Always cover, where relevant: negative input, empty/null, max length, special characters/unicode, permissions per role, concurrency/duplicate actions, network failure, localization, accessibility (keyboard + screen reader + contrast — WCAG 2.2 AA), and the non-functional REQs (performance, security).

## Test case record

Schema: `schemas/test-cases.schema.json`. Validate with `scripts/validate_testcases.py`.

```json
{
  "id": "TC-CHK-004-02",
  "title": "Expired promo code is rejected and total is unchanged",
  "requirement_ids": ["REQ-CHK-004"],
  "type": "functional",
  "level": "e2e",
  "priority": "P1",
  "risk": "high",
  "technique": "EP",
  "preconditions": ["User is logged in", "Cart contains 1 item priced $50.00", "Promo code SPRING24 expired yesterday"],
  "test_data": {"promo_code": "SPRING24"},
  "steps": [
    {"action": "Open the checkout page", "expected": "Order total shows $50.00"},
    {"action": "Enter SPRING24 in the promo field and press Apply", "expected": "Message 'This code has expired' is shown"},
    {"action": "Read the order total", "expected": "Order total still shows $50.00"}
  ],
  "automation": {"candidate": true, "status": "not_automated", "framework": "", "path": ""},
  "tags": ["checkout", "negative", "regression"]
}
```

ID rule: `TC-<AREA>-<REQ#>-<NN>`. Steps: one observable action each; every step has an expected result; no "verify everything works".

`level`: `unit | api | integration | e2e | ui | manual-exploratory`. Push checks down the pyramid: if a rule can be verified at API level, design it there and keep one e2e smoke.

## Gherkin output (optional)

For BDD teams, emit `.feature` files with `scripts/export_tracker.py --format gherkin`. Tag scenarios with `@REQ-CHK-004 @TC-CHK-004-02 @P1` so traceability survives into the automation code.

## Coverage self-check before handing off

- Every `approved` REQ has ≥1 test case; every acceptance criterion maps to ≥1 step's expected result.
- High-risk REQs have negative and boundary cases.
- No test case references a REQ ID that doesn't exist (the validator enforces this when given `--requirements`).
- Run `scripts/build_rtm.py` and paste the coverage line into your reply.
