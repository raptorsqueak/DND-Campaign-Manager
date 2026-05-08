# /add-content — Intake a Supplement (Book / Rules / Lore / Backstory)

Guided intake for any new `.md` supplement. Copies the source into the right `supplements/` directory, splits adventure books by chapter, and generates a `_summary.md` + `_index.md` so every other command can load only what it needs.

This file is also the **authoritative spec** for the supplement layout — the templates at the bottom (manifest schema, summary, index, DM-state) are what every consumer command (`/ask-dnd`, `/plan-next-session`, `/generate-npc`, `rules-oracle`, `schema-auditor`) reads against.

---

## Step 0: Determine Scope

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block.

Ask:

> Where should this supplement live?
> 1. Global (`supplements/`) — applies to every campaign (house rules, homebrew, generic lore)
> 2. Campaign-specific (`campaigns/{slug}/supplements/`) — only this campaign

If an active campaign exists, default option 2 to that campaign. If no active campaign and the user picks 2, stop and say: "No active campaign. Run /start-campaign first or pick option 1 (global)."

Set `{target-root}`:
- Global → `DND-Campaign-Manager/supplements`
- Campaign → `DND-Campaign-Manager/campaigns/{campaign-slug}/supplements`

---

## Step 1: Source

Ask:

> What's the source? Either:
> - A path to an existing `.md` or `.pdf` file (will be read and converted into the supplement directory), or
> - Paste the markdown content here

Accept `.md` and `.pdf`. For PDFs: use the Read tool to extract content one page range at a time (max 20 pages per call), concatenate, and convert into clean markdown — preserve headings, lists, tables, and emphasis; drop page numbers, running headers/footers, and obvious OCR artifacts. The original PDF is **not** moved into the supplement directory; only the converted markdown is written. After conversion, show the user a preview (first ~40 lines) and ask `proceed / re-extract with different settings / cancel`.

If the user provides a path, verify the file exists and is readable. If they paste content, hold it in memory for later writing.

---

## Step 2: Kind

Ask:

> What kind of supplement is this?
> 1. `adventure-book` — a published or homebrew campaign book with chapters/levels (will be split per chapter)
> 2. `rules-supplement` — house rules, mechanics, errata
> 3. `lore` — setting, factions, regions, world background
> 4. `character-backstory` — PC or party-wide backstory material
> 5. `homebrew-mechanic` — a single new mechanic, item system, or subsystem

Capture as `{kind}`.

---

## Step 3: Slug

Suggest a slug derived from the source's `# Title` heading or filename: lowercase, kebab-case, no special characters. Example: "Storm King's Thunder" → `storm-kings-thunder`.

Ask:

> Use slug `{suggested-slug}`? (yes / different)

If a directory already exists at `{target-root}/{slug}/`, ask:

> A supplement with this slug already exists. Options:
> 1. Replace (delete existing, create fresh)
> 2. Use a different slug
> 3. Cancel

Capture as `{slug}`.

---

## Step 4: Copy / Split

Set `{dest-dir} = {target-root}/{slug}/`. Create it.

### If `kind == adventure-book`

Detect the chapter heading style. Scan the source for top-level headings matching, in priority order:
1. `^# Chapter \d+`
2. `^# Level \d+`
3. `^# Part \d+`
4. `^# Book \d+`

If a pattern matches at least 2 sections, use it as the split point. Show the user the detected chapter list and ask:

> Detected {N} chapters using pattern `{pattern}`. Proceed?
> 1. Yes, split by this pattern
> 2. Use a different heading level / pattern (specify)
> 3. Don't split — store as a single `content.md`

When splitting, write each chapter to `{dest-dir}/chapter-{NN}-{kebab-title}.md` (or `level-{NN}-...` / `part-{NN}-...` matching the detected pattern), where `NN` is zero-padded. Material before the first chapter heading goes into `chapter-00-front-matter.md` if non-trivial; otherwise discard the front matter and warn. Material after the last chapter (e.g., appendices) goes into `appendix-{letter-or-number}-{kebab-title}.md` if introduced by a clear `# Appendix X` heading; otherwise tack onto the previous chapter file.

### If `kind != adventure-book`

Write the entire source verbatim to `{dest-dir}/content.md`.

---

## Step 5: Generate `_summary.md`

Read the content (all chapter files, or `content.md`). Write `{dest-dir}/_summary.md` using the template at the bottom of this file. Aim for **150–300 words**. Cover:
- What this supplement is and where it came from (publisher / homebrew author / DM)
- What it contains (high-level scope, not exhaustive)
- When a command should consult it (the trigger conditions — locations, level range, NPCs, mechanics it owns)
- Any house-rule overrides or conflicts with RAW it's known to introduce

The summary is **always loaded** by any command that touches the campaign — keep it tight and decision-relevant.

---

## Step 6: Generate `_index.md`

Read every content file. Extract structured entries into `{dest-dir}/_index.md` using the template at the bottom. Sections (omit any that don't apply):
- **Chapters / Sections** — one line per file: title → relative file path
- **NPCs** — name → file path → 1-line role
- **Locations** — name → file path → region/parent location
- **Quests / Hooks** — name → file path → 1-line status hint
- **Magic Items / Mechanics** — name → file path
- **Monsters / Encounters** — distinctive named encounters only (not the whole bestiary), name → file path

The index is the **cheap-to-load entry point**. A consumer command reads `_summary.md` to decide if a supplement is relevant, then `_index.md` to find the right file, then loads only that file. Keep entries to one line each. Use exact heading anchors where helpful (e.g., `chapter-03-the-savage-frontier.md#yartar`).

---

## Step 7: Update `_manifest.json`

Read `{target-root}/_manifest.json` if it exists; otherwise initialize it with `{"supplements": []}`.

Append:

```json
{
  "slug": "{slug}",
  "title": "{title from source's first heading or user-provided}",
  "kind": "{kind}",
  "summary": "{slug}/_summary.md",
  "index":   "{slug}/_index.md",
  "added":   "{today's ISO date}"
}
```

If the slug already appears (the user chose "replace" earlier), update the existing entry in place rather than appending a duplicate.

Write the manifest back, sorted by `slug`, with two-space indent.

---

## Step 8: Create DM State Skeleton (campaign-scope adventure books only)

If `{target-root}` is a campaign and `{kind} == adventure-book`:

Ensure `DND-Campaign-Manager/campaigns/{campaign-slug}/supplement-state/` exists. Create `{campaign-slug}/supplement-state/{slug}.md` from the DM-state template at the bottom — empty section skeleton, ready for the DM to fill in as the campaign progresses.

If a state file already exists for this slug, leave it alone.

---

## Step 9: Confirm and Optionally Remove Source

Show the user the resulting tree:

```
{dest-dir}/
  _summary.md          (~250 words)
  _index.md            (12 chapters, 47 NPCs, 23 locations indexed)
  chapter-01-...md
  chapter-02-...md
  ...
{target-root}/_manifest.json  (updated)
{state-file-if-applicable}
```

If the user supplied a path in Step 1 and the source still exists at that path, ask:

> The original `{source-path}` is still in place. Options:
> 1. Delete it (the new directory is the source of truth)
> 2. Keep it (you'll clean it up manually)

Don't delete without explicit confirmation.

Final confirmation: "Added: `{slug}` ({kind}) under `{target-root}` — {N} chapter file(s), summary + index generated."

---

## Templates

### `_summary.md` template

```markdown
# {Title} — Summary

**Slug**: {slug}
**Kind**: {kind}
**Added**: {YYYY-MM-DD}
**Source**: {publisher / homebrew / DM-authored / etc.}

## What this is
{1–2 sentences: what the supplement is and where it came from.}

## Scope
{2–4 sentences: high-level coverage. For a book: level range, regions, main plot arc. For rules: which rules it touches. For lore: which entities/places it covers.}

## When to consult
{Bullet list of trigger conditions — be concrete.}
- {Trigger 1, e.g., "Any encounter set in the Silver Marches between levels 5–10"}
- {Trigger 2, e.g., "Questions about hill giant or frost giant lore"}
- {Trigger 3}

## Overrides / conflicts
{Any house-rule overrides of RAW, or known conflicts with other supplements. "(none known)" is a valid answer.}
```

### `_index.md` template

```markdown
# {Title} — Index

**Slug**: {slug}

> Index of named content within this supplement. Consumers should load only the file paths referenced here, not the whole supplement.

## Chapters / Sections

| # | Title | File |
|---|---|---|
| 1 | {Chapter 1 title} | `chapter-01-...md` |
| 2 | {Chapter 2 title} | `chapter-02-...md` |
| ... | ... | ... |

## NPCs

| Name | File | Role |
|---|---|---|
| {NPC name} | `chapter-XX-...md#anchor` | {1-line role} |

## Locations

| Name | File | Region |
|---|---|---|
| {Location name} | `chapter-XX-...md#anchor` | {Parent region} |

## Quests / Hooks

| Name | File | Status hint |
|---|---|---|
| {Quest name} | `chapter-XX-...md#anchor` | {e.g., "Tier 2 sidequest, requires level 5+"} |

## Magic Items / Mechanics

| Name | File |
|---|---|
| {Item or mechanic} | `chapter-XX-...md#anchor` |

## Notable Encounters

| Name | File |
|---|---|
| {Distinctive named encounter} | `chapter-XX-...md#anchor` |
```

### `_manifest.json` schema

```json
{
  "supplements": [
    {
      "slug": "string (kebab-case, unique within this manifest)",
      "title": "string (display title)",
      "kind": "adventure-book | rules-supplement | lore | character-backstory | homebrew-mechanic",
      "summary": "string (relative path from manifest dir, always ends in _summary.md)",
      "index":   "string (relative path from manifest dir, always ends in _index.md)",
      "added":   "string (ISO date YYYY-MM-DD)"
    }
  ]
}
```

Sorted by `slug` ascending. Two-space indent. UTF-8.

### `supplement-state/{slug}.md` template

```markdown
# {Title} — DM State

**Supplement**: `{slug}`
**Campaign**: {campaign name}

> Persistent DM-tracked state for this supplement. Records what's been used, modified, or skipped — separate from the canonical content.

## Chapters Completed
{empty until DM fills in. One bullet per chapter cleared, with session number.}

## NPCs (status)
{Named NPCs from this book whose status differs from canon — killed, recruited, modified, etc.}

## Encounters Modified
{Any encounter the DM altered from the book — what changed and why.}

## Skipped Content
{Anything intentionally cut from this campaign.}

## DM Notes
{Free-form notes about how this book is being run.}
```

---

## Implementation notes (for future maintainers)

- **Splitting heuristic** (Step 4) is intentionally loose — books vary. If detection fails, falling back to a single `content.md` is acceptable. The DM can always re-run `/add-content` after manually splitting the source.
- **Summary and index generation** (Steps 5–6) are AI tasks. The template is the contract; the prose inside is generated. When iterating on the prompt, the `_summary.md` should be re-generated *from* the content files, not from the original monolithic source — that way a DM who edits a chapter file later can re-run summary regeneration cleanly.
- **Idempotency**: re-running `/add-content` on the same slug with "replace" should produce a clean new directory and update (not duplicate) the manifest entry.
- **The manifest is the source of truth** for what supplements exist. A directory under `{target-root}` that isn't in the manifest is invisible to consumers (and a future `/audit` check will flag it).
