# /review-improvements — Review and Apply Improvement Candidates

Walks the pending improvement candidates produced by the `improvement-curator` agent. For each candidate, the user chooses to apply, skip, dismiss, or inspect supporting evidence.

Defaults to **project scope** — improvements that affect the tool overall (efficiency, structural drift, memory hygiene, redundant tool calls). Pass `campaign` to walk a single campaign's queue instead.

Accepts an optional flag:

| Argument | Effect |
|---|---|
| (none) | Project scope. Walk only the current pending queue in `.claude/.meta/improvements.jsonl`. |
| `--refresh` | Run signal collection + `improvement-curator` first, append candidates, then walk. |
| `campaign` | Switch to campaign scope (requires ACTIVE CAMPAIGN). Use `campaigns/{slug}/.meta/improvements.jsonl`. |
| `campaign --refresh` | Combine — campaign-scope refresh + walk. |

---

## Architecture

This command does the **signal collection** inline (in the orchestrator's context where deterministic Bash + Read + Glob are reliable). The `improvement-curator` agent receives a fully-collected findings JSON and only judges/clusters/drafts candidates. The subagent's job is narrow and reliable; broad investigation lives here.

---

## Step 0: Resolve scope

If the user passed `campaign`, set `scope = "campaign:{slug}"`:
- Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none, stop:
  > "No active campaign. Run /start-campaign first, or run /review-improvements without 'campaign' for project scope."
- Set `improvements_path = DND-Campaign-Manager/campaigns/{slug}/.meta/improvements.jsonl`.

Otherwise, set `scope = "project"`:
- Set `improvements_path = DND-Campaign-Manager/.claude/.meta/improvements.jsonl`.

---

## Step 1: Auto-refresh decision

Check whether `improvements_path` exists and has content.

**Auto-refresh trigger** (treat as `--refresh` was passed):
- **Project scope** — if `improvements_path` does not exist OR is empty, auto-refresh. Project scans always have something to look at.
- **Campaign scope** — if `improvements_path` does not exist OR is empty, AND `campaigns/{slug}/.meta/rejections.jsonl` exists and is non-empty, auto-refresh.

If `--refresh` is set (explicitly or by auto-trigger), proceed to Step 2. Otherwise skip to Step 4.

---

## Step 2: Collect signals (orchestrator does this inline)

Run the following data collection in parallel where possible. The output of this step is a single `findings` JSON object that gets passed to the curator agent in Step 3.

### Stream A — Rejection logs

```bash
# Project scope: aggregate across all campaigns
ls campaigns/*/.meta/rejections.jsonl 2>/dev/null | xargs -r cat

# Campaign scope: that campaign's log
cat campaigns/{slug}/.meta/rejections.jsonl
```

Parse each line as JSON. Build an array of `{ts, session, agent, utterance, proposed, outcome, correction, reason}` records.

### Stream B — User observations (project scope only)

Read `.claude/.meta/observations.md` if it exists. Parse each `- ` bullet under the `## Active observations` heading. Each bullet is one signal. Build an array of `{text, line_number}`.

### Stream C — Corpus structural-drift scan (project scope only)

**C1 — NPC heading distribution:**

```bash
# Count files starting with "# " (canonical) vs "## " (non-canonical) on first non-blank line
for f in campaigns/*/npcs/*.md; do
  head -1 "$f"
done 2>/dev/null | awk '/^# /{l1++} /^## /{l2++} END {print "level1=" (l1+0) " level2=" (l2+0)}'
```

If one form dominates ≥80% but a minority diverges (or one form is universal except for outliers), record a `corpus_drift` finding: `{kind: "heading-drift", scope: "npcs", dominant: "##", count_dominant: 67, count_outlier: 4, dominant_share: 0.94}`.

**C2 — Player section presence:**

```bash
for f in campaigns/*/players/*.md; do
  echo "=== $f ==="
  grep -E "^## (Combat|Combat Stats|Personality|Equipment|Backstory|Spellcasting)" "$f"
done
```

For each canonical section, count which player files have it. Flag any file missing `## Personality`, `## Combat Stats`, etc. Record findings like `{kind: "missing-section", file: "...", section: "## Personality"}` or `{kind: "variant-heading", file: "...", canonical: "## Combat Stats", actual: "## Combat"}`.

**C3 — Agent/command boilerplate:**

Read each `.claude/agents/*.md` and `.claude/commands/*.md`. Check:
- Commands: does each have a `Step 0` active-campaign check (where applicable — exclude `/start-campaign` itself)? Grep for `ACTIVE CAMPAIGN:`.
- Agents: does each agent's `tools:` frontmatter line match the tool set its body references?

Record any inconsistency.

### Stream D — Stale references (project scope only)

```bash
# Find references to specific NPC file paths in agents/commands
grep -nE "campaigns/\{[^}]+\}/(npcs|players|supplements|sessions)/" \
  .claude/agents/*.md \
  .claude/commands/*.md
```

For each pattern path, verify the target directory exists in at least one campaign. Also check `.claude/agents/<name>.md` references — confirm each named agent exists in `.claude/agents/`.

Record `{kind: "stale-path", file: "...", line: N, reference: "...", reason: "..."}` for each broken pointer.

### Stream E — Memory hygiene (project scope only)

```bash
# List all memory files (memory dir is derived from the current project path)
MEMDIR="$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"
ls "$MEMDIR"/*.md

# Check slug naming
for f in "$MEMDIR"/*.md; do
  grep -m1 "^name:" "$f"
done
```

- **Slug-naming drift:** Read each file's `name:` frontmatter. Flag inconsistencies (snake_case vs kebab-case in the same memory dir).
- **Index sync:** Compare files in the memory dir against entries in `MEMORY.md`. Flag any memory file not indexed, or any index entry pointing at a missing file.

Record findings.

### Stream F — Existing improvements queue (dedupe)

Read `improvements_path`. Parse pending entries. Pass these to the curator so it can dedupe.

### Build the findings JSON

Assemble all streams into one object:

```json
{
  "scope": "project | campaign:{slug}",
  "collected_at": "2026-06-07T...",
  "streams": {
    "A_rejections": [ ... ],
    "B_observations": [ ... ],
    "C_corpus_drift": [ ... ],
    "D_stale_references": [ ... ],
    "E_memory": [ ... ],
    "F_pending_for_dedupe": [ ... ]
  },
  "totals": {
    "A": <count>,
    "B": <count>,
    "C": <count>,
    "D": <count>,
    "E": <count>,
    "F": <count>
  }
}
```

Display to the user:
> *"Collected signals: A rejections={n}, B observations={n}, C corpus-drift={n}, D stale-ref={n}, E memory={n}, F pending={n}. Dispatching curator for judgment..."*

---

## Step 3: Dispatch the curator with collected findings

Invoke the `improvement-curator` agent via the Agent tool:

- `subagent_type`: `improvement-curator`
- `description`: `"Judge improvements ({scope})"`
- `prompt`: the **complete findings JSON** from Step 2, prefixed with:

```
scope: {scope}

You are receiving pre-collected findings. Your job is to JUDGE each finding,
cluster where appropriate, and draft candidate improvement records.
You do not need to fetch any data yourself — everything is provided below.

findings:
{the JSON object from Step 2}
```

The agent returns:

```json
{
  "scope": "project | campaign:{slug}",
  "candidates": [ { ...improvement record... } ],
  "discarded": [ { "finding_id": "...", "reason": "..." } ],
  "summary": "string"
}
```

---

## Step 4: Append candidates to the queue

If `candidates` is non-empty:
- Ensure `improvements_path`'s parent directory exists.
- For each candidate, append the JSON object as a single line to `improvements_path`. Use Bash with proper JSON escaping.

Display: *"Curator drafted {n} candidates ({m} discarded). Queue updated."*

---

## Step 5: Walk the pending queue

Read `improvements_path`. Parse each line. Filter to `status: pending`. Sort by `confidence` descending.

If empty:
```
=== NO PENDING IMPROVEMENTS ===
Scope: {scope}
Queue is empty.
```
Stop.

Otherwise, for each pending candidate:

```
─── Improvement {idx}/{total}  ({scope}) ───
ID:         {id}
Agent:      {agent}
Type:       {type}
Target:     {target_file}
Confidence: {confidence}
Evidence:   {evidence.length} signal(s)

Rationale: {rationale}

--- Diff (section: {proposed_diff.section}) ---
BEFORE:
{proposed_diff.before}

AFTER:
{proposed_diff.after}

Actions: a)pply  s)kip  d)ismiss  e)vidence  q)uit
```

For new-file candidates (`proposed_diff.operation == "create"`), display the path + full content instead of before/after.

### a) apply

Edit-mode: use the Edit tool on `target_file` with `proposed_diff.before` → `proposed_diff.after`. If the Edit fails (text drifted), report and offer skip/dismiss/quit.

Create-mode: confirm path doesn't exist (warn if it does), use Write tool with `proposed_diff.content`.

Then rewrite the matching JSONL line with `status: "applied"` and `applied_ts: <now>`.

Display: *"✓ Applied."*

### s) skip
Leave pending. Continue.

### d) dismiss
Rewrite the JSONL line with `status: "dismissed"` and `dismissed_ts: <now>`. Display dismissal.

### e) evidence
For each entry in `evidence[]`, show details based on `source`:
- `rejection`: grep the rejection log for `ref`, display the record.
- `observation`: show the bullet text from `observations.md`.
- `corpus-scan` / `memory-scan`: show file:line.
Then re-prompt the same candidate.

### q) quit
Stop walking. Go to Step 6.

---

## Step 6: Summary

```
=== REVIEW COMPLETE ===
Scope:     {scope}
Walked:    {n} candidates
Applied:   {applied}
Dismissed: {dismissed}
Skipped:   {skipped}  (remain pending)

Queue state: {pending_after} pending, {applied_total} applied (lifetime), {dismissed_total} dismissed (lifetime)
```

---

## Notes

- The orchestrator does the investigation; the curator does the judgment. Subagents are unreliable at broad "go fetch context" tasks but reliable at constrained "given these facts, draft these records" tasks.
- `improvements.jsonl` is append-only at the agent level. Status transitions happen here via single-line rewrites.
- Apply will fail safely if `before` no longer matches the target file — re-run `--refresh` to regenerate against current state.
- **Manual-only.** No hooks invoke this automatically.
- **`.claude/.meta/observations.md`** is the user's free-form friction notes. Drop bullets in any time; the next `--refresh` picks them up.
