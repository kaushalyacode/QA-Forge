# PRD — Checkout promo codes (v1.2)

## Overview
Shoppers can apply a promotional code at checkout to reduce their order total.

## Functional requirements

FR-1 The system shall allow a logged-in shopper to apply one promo code per order.

**Acceptance Criteria**
- Given a valid code, when the shopper applies it, then the order total is reduced by the configured discount
- Given a second code, when the shopper applies it, then the first code is replaced and only one discount applies

FR-2 The system must reject expired or unknown promo codes with a clear message.

Acceptance Criteria
- Given an expired code, when applied, then "This code has expired" is shown and the total is unchanged
- Given an unknown code, when applied, then "Code not recognised" is shown

FR-3 The promo field must accept 4 to 20 alphanumeric characters.

## User stories
As a returning shopper, I want my applied code to persist if I refresh the page, so that I don't have to re-enter it.

## Non-functional requirements
NFR-1 Applying a promo code should respond in under 1 second at p95.
NFR-2 The promo field must be operable by keyboard and announced by screen readers (WCAG 2.2 AA).
