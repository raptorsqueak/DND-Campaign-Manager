# /audit — Run a Schema / Consistency / Coverage Audit

Crawls the active campaign's data, surfaces issues, writes a checklist report. Read-only audit; no files are modified except the report itself at `.meta/audit-report.md`.

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say:

> "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Parse Scope Argument

Accept an optional inline argument:

| Argument | Effect |
|---|---|
| (none) or `all` | Run the full audit (coverage + consistency + drift) |
| `players` | Coverage check on player/companion files only |
| `npcs` | Coverage check on NPC files only |
| `campaign` | Coverage check on campaign.json only |
| `consistency` | Cross-file checks only (skip per-file coverage) |
| `drift` | Schema-drift checks only |
| `fix N` | Apply the suggested fix for issue N from the most recent audit report (interactive) |

Examples: `/audit`, `/audit players`, `/audit fix 3`.

If the argument is `fix N`, jump to **Step 5: Apply a Fix**.

---

## Step 2: Dispatch the schema-auditor Agent

Invoke the Agent tool with:

- `subagent_type`: `schema-auditor`
- `description`: `"Audit {campaign-slug} ({scope})"`
- `prompt`:
  ```
  campaign_slug: {campaign-slug}
  scope: {scope}
  ```

The agent reads everything it needs and returns a markdown report with a JSON summary block at the end.

---

## Step 3: Write the Report

Take the agent's response and write it verbatim to `DND-Campaign-Manager/campaigns/{campaign-slug}/.meta/audit-report.md` (overwriting any previous report).

If `.meta/` doesn't exist, create it first.

---

## Step 4: Display Summary

Show the user:

```
=== AUDIT COMPLETE ===
Campaign: {name}
Scope: {scope}

Coverage: {N error}, {N warning}, {N info}
Consistency: {N issues}
Schema Drift: {N error}, {N warning}, {N info}

Top issues:
  1. {first error from report}
  2. {second error}
  3. ...

Full report: campaigns/{campaign-slug}/.meta/audit-report.md

Next steps:
  /audit fix N   — apply suggested fix for issue N (auto-fixable issues only)
  /update-player — fix data gaps interactively
  /campaign-info — fix campaign.json metadata gaps
```

If there are zero issues at all severity levels, say:

```
=== AUDIT COMPLETE ===
No issues found. Campaign data is clean.
```

---

## Step 5: Apply a Fix (when invoked as `/audit fix N`)

1. Read `.meta/audit-report.md`. If it doesn't exist, say:
   > "No audit report found. Run /audit first."

2. Parse the JSON block at the end of the report. Find the issue with `id: N`.

3. If `auto_fixable: false`, say:
   > "Issue {N}: {description}. This requires manual intervention via {suggested command}. Want me to launch it? (y / n)"

4. If `auto_fixable: true`, display:
   ```
   Issue {N} ({severity}): {description}
   File: {file}
   Field: {field}
   Suggested fix: {suggested_fix}

   Apply this fix? (y / n / show diff)
   ```

5. On `y`: dispatch the appropriate agent (`player-data`, `npc-data`, or `campaign-state`) with a constructed `utterance` describing the fix. Apply via the standard write policy. Report the result.

6. On `show diff`: display the proposed before/after, then re-prompt y/n.

7. On `n`: skip and re-display the audit summary so the user can pick a different issue.

---

## Notes

- The auditor is read-only — running `/audit` never modifies player/NPC/campaign files. Only `.meta/audit-report.md` is written.
- The audit is point-in-time; running it again refreshes everything.
- Issues marked `info` are informational only (e.g. "Last Updated more than 30 days old"). Don't pester the user about these.
- If the audit reveals a schema drift pattern that affects many files (e.g. "12 NPC files use level-2 heading"), the auditor will summarize rather than list each one. Use the JSON block to see the full list if needed.
