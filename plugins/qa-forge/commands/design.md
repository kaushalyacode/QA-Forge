---
description: Design risk-based test cases from the normalized requirements and validate them
argument-hint: "[REQ-IDs | tag | all] [--gherkin]"
---

Use the `qa-forge` skill, Phases 2–3 (read `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/references/test-design.md`).

Scope: $ARGUMENTS (default: all `approved`/`draft` requirements in `qa/requirements/requirements.json`).

1. Score risk per requirement.
2. Design test cases with the techniques the risk level calls for, writing `qa/test-cases/test-cases.json` (append; keep existing IDs stable).
3. Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/validate_testcases.py qa/test-cases/test-cases.json --requirements qa/requirements/requirements.json` — fix every error.
4. Build the RTM: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/build_rtm.py --requirements qa/requirements/requirements.json --test-cases qa/test-cases/test-cases.json -o qa/rtm.md`.
5. If `--gherkin` was requested, also run `export_tracker.py --format gherkin -o qa/features`.

Reply with the coverage line, counts by priority/risk, and any requirement left uncovered.
