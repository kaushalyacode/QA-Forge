# Requirements Traceability Matrix

**Coverage:** 4/6 requirements (66.7%) · **Passed:** 1 (16.7%)

| Requirement | Source Id | Title | Priority | Test Cases | Results | Defects | Status |
|---|---|---|---|---|---|---|---|
| REQ-CHK-001 | FR-1 | The system shall allow a logged-in shopper to apply one promo code per order. | P2 | TC-CHK-001-01, TC-CHK-001-02 | TC-CHK-001-01:pass, TC-CHK-001-02:pass |  | PASSED |
| REQ-CHK-002 | FR-2 | The system must reject expired or unknown promo codes with a clear message. | P2 | TC-CHK-002-01 | TC-CHK-002-01:fail | SHOP-981 | FAILED |
| REQ-CHK-003 | FR-3 | The promo field must accept 4 to 20 alphanumeric characters. | P2 | TC-CHK-003-01 | TC-CHK-003-01:not run |  | INCOMPLETE |
| REQ-CHK-004 |  | As a returning shopper, I want my applied code to persist if I refresh the page, so that I don't have to re-enter it. | P2 |  |  |  | NOT COVERED |
| REQ-CHK-005 | NFR-1 | Applying a promo code should respond in under 1 second at p95. | P2 |  |  |  | NOT COVERED |
| REQ-CHK-006 | NFR-2 | The promo field must be operable by keyboard and announced by screen readers (WCAG 2.2 AA). | P2 | TC-CHK-006-01 | TC-CHK-006-01:blocked |  | BLOCKED |
