---
description: Write the test plan for a release from requirements, risks and test cases
argument-hint: "<release name/version>"
---

Use the `qa-forge` skill, Phase 4. Fill `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/templates/test-plan.md` for release **$ARGUMENTS** and save it to `qa/plans/<release>-test-plan.md`.

Pull scope from `qa/requirements/requirements.json`, the risk register from the test cases' `risk` field, environments and exit criteria from `qa/qa-forge.config.json`, and tooling from the integrations that are connected. Leave `{{…}}` placeholders only where the information genuinely isn't available and list them at the end of your reply.
