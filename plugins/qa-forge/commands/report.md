---
description: Produce the RTM and test summary report with a GO / GO WITH RISKS / NO-GO recommendation
argument-hint: "<release> [run folder(s)]"
---

Use the `qa-forge` skill, Phase 8. Release and runs: $ARGUMENTS (default: all folders under `qa/runs/`, oldest first so later results win).

1. If a tracker is connected, export open defects for the release to `qa/reports/defects.json` (`id`, `severity`, `status`).
2. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/build_rtm.py --requirements qa/requirements/requirements.json --test-cases qa/test-cases/test-cases.json --results <results.json/junit.xml files> -o qa/rtm.md`
3. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/report.py --test-cases qa/test-cases/test-cases.json --results <same files> --defects qa/reports/defects.json --config qa/qa-forge.config.json --title "<release>" -o qa/reports/<release>-summary.md`
4. Complete the draft using `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/templates/test-summary-report.md`: coverage gaps, risks going live, deviations, flaky tests.

The recommendation is a draft for the QA lead — say so, and lead your reply with it plus the two or three facts that drive it.
