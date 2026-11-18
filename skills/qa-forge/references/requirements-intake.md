# Phase 1 — Requirements intake

Goal: turn whatever the team has (BRD, PRD, user stories, Jira issues, ADO work items, Confluence/wiki pages, emails) into one normalized `qa/requirements/requirements.json` that every later phase keys off.

## 1. Identify the source type

| Source | Typical shape | How to read it |
|---|---|---|
| **BRD** (Business Requirements Document) | Business goals, stakeholders, business rules, "The system shall…" statements, often numbered `BR-x` | File → `scripts/extract_requirements.py`; then human-level review |
| **PRD** (Product Requirements Document) | Problem, personas, user stories, functional + non-functional reqs, acceptance criteria, out-of-scope | Same script; user stories become one REQ each |
| **FRS / SRS** | Numbered functional specs `FR-x`, `NFR-x` | Script preserves the native IDs |
| **Jira** Epic / Story / Task / Bug | Summary, description, acceptance criteria (field or description section), links, labels, fix version | Connected: Jira MCP search/get (JQL). Assisted: Jira CSV export |
| **Azure DevOps** Epic / Feature / User Story / PBI / Bug | Title, Description, Acceptance Criteria field, Area/Iteration path, links | Connected: ADO MCP `work-items` domain (WIQL). Assisted: ADO query → CSV export |
| **Confluence / wiki page** | Free-form | Atlassian MCP (Confluence) or ADO `wiki` domain; then treat as BRD/PRD |
| Figma / screenshots | UI states | Extract UI states and validation rules as REQs tagged `ui` |

## 2. Pull from trackers (connected mode)

**Jira (JQL examples)**
- One issue and its children: `key = PROJ-123 OR parent = PROJ-123`
- Sprint scope: `project = PROJ AND sprint in openSprints() AND issuetype in (Story, Bug)`
- Release scope: `project = PROJ AND fixVersion = "2.4.0"`

Map: `key → source_id`, `summary → title`, acceptance criteria (custom field, or `h3. Acceptance Criteria` / `**Acceptance Criteria**` section in description) → `acceptance_criteria[]`, `priority → priority`, `labels/components → tags`.

**Azure DevOps (WIQL examples)**
```sql
SELECT [System.Id], [System.Title], [System.WorkItemType], [Microsoft.VSTS.Common.AcceptanceCriteria]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] IN ('User Story', 'Product Backlog Item', 'Bug')
  AND [System.IterationPath] UNDER @currentIteration
```
Map: `System.Id → source_id`, `System.Title → title`, `Microsoft.VSTS.Common.AcceptanceCriteria` (HTML → split on `<li>`/line breaks) → `acceptance_criteria[]`, `Microsoft.VSTS.Common.Priority (1–4) → priority (P1–P4)`, `System.AreaPath → component`.

## 3. Extract from documents (assisted mode)

```bash
python scripts/extract_requirements.py path/to/PRD.md --source-name "Checkout PRD v3" -o qa/requirements/requirements.json
```

The script finds numbered IDs (`FR-12`, `BR-3`, `NFR-1`, `REQ-7`, `US-4`), normative sentences (`shall`, `must`, `should`, `will`), user stories (`As a … I want … so that …`) and Given/When/Then blocks, and attaches the acceptance criteria that follow each one. For `.docx`/`.pdf`, convert to text first (pandoc / pdftotext) or read the file directly and write the JSON by hand to the same schema.

**Then review every extracted item yourself.** The script is a recall net, not a judge: merge duplicates, split compound requirements ("…and…"), drop non-testable statements into the ambiguity log.

## 4. Normalized requirement record

Schema: `schemas/requirements.schema.json`.

```json
{
  "id": "REQ-CHK-004",
  "source": "jira",
  "source_id": "SHOP-412",
  "title": "Apply a single promo code at checkout",
  "type": "functional",
  "priority": "P1",
  "acceptance_criteria": [
    "Valid code reduces order total by the configured discount",
    "Expired code shows 'This code has expired' and total is unchanged",
    "Only one code can be active per order"
  ],
  "tags": ["checkout", "pricing"],
  "status": "approved",
  "notes": ""
}
```

ID rule: keep the native ID as `source_id`; mint a stable `id` of the form `REQ-<AREA>-<NNN>` so test cases don't break if tickets are re-keyed.

`type`: `functional | non-functional | business-rule | ui | integration | data | security | performance | accessibility | compliance`.

## 5. Testability review (feeds Phase 2)

For each requirement, check INVEST-style testability and log problems in `qa/requirements/ambiguity-log.md`:

| Check | Red flag | Action |
|---|---|---|
| Measurable | "fast", "user-friendly", "secure" | Propose a number (e.g. p95 < 2 s) as an assumption |
| Complete | No error/edge behaviour described | Propose expected behaviour; mark `assumed` |
| Unambiguous | "and/or", "etc.", "as appropriate" | Split or ask |
| Consistent | Conflicts with another REQ | Log both IDs |
| Has acceptance criteria | None | Draft them in Given/When/Then; mark `draft` |

Ambiguity log row: `| # | REQ-ID | Issue | Proposed assumption | Owner | Status |`.

When the source is a tracker and the user agrees, post the open questions back as a comment on the issue/work item.
