---
description: Ingest requirements from a BRD/PRD file, Jira issue/JQL, or Azure DevOps work item/WIQL into qa/requirements/requirements.json
argument-hint: "<file path | JIRA-KEY | JQL | ADO work item id | WIQL>"
---

Use the `qa-forge` skill, Phase 1 (read `${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/references/requirements-intake.md`).

Source: $ARGUMENTS

- A file path → `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qa-forge/scripts/extract_requirements.py <file> --prefix <AREA> --source <brd|prd|srs> -o qa/requirements/requirements.json`, then review and clean up every item.
- A Jira key or JQL → fetch via the Atlassian/Jira MCP (include child issues); map fields as described in the reference.
- An ADO id or WIQL → fetch via the Azure DevOps MCP `work-items` tools; map fields as described.
- No MCP available → ask for an export (CSV/HTML) and process it as a file.

Then do the testability review, write `qa/requirements/ambiguity-log.md`, and report: number of requirements, how many have acceptance criteria, top ambiguities with proposed assumptions.
