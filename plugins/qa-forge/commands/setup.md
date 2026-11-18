---
description: Set up QA Forge in this project - detect MCP servers, guide Jira / Azure DevOps / automation authentication, create the qa/ workspace
argument-hint: "[jira|ado|playwright|selenium|appium|browserstack|all]"
---

Use the `qa-forge` skill, Phase 0 (read `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/references/integrations-and-auth.md`).

Focus: $ARGUMENTS (if empty, cover everything the team uses — ask which trackers and automation stack in one question).

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/check_env.py` and list the MCP tools already available in this session.
2. If `qa/qa-forge.config.json` doesn't exist, copy `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/templates/qa-forge.config.json` there and fill what you know.
3. For each missing integration, walk the user through the auth path for their deployment (cloud vs on-prem), with the least-privilege scopes. Offer to add the right profile with `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/add_mcp_profile.py <profile> --target .mcp.json`. Never ask the user to paste a secret into chat.
4. Make sure `.gitignore` covers `qa/.env`, `qa/.auth/`, `storageState*.json`.
5. Smoke-test each connected server read-only and finish with the integration status table.
