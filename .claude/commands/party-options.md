# /party-options — Create / Update / Verify a PC's non-SRD options

Maintains the campaign-private **`party-options`** supplement — paraphrased references for the class, subclass, species, feats, and spells a character uses that the SRD doesn't carry. Builds or updates the entries for one PC (or companion), or runs a verification pass over them.

**Usage:**
- `/party-options [name]` — create or update the party-options entries for that character (interview fills gaps).
- `/party-options [name] --verify` — run the verification process over that character's existing entries.

If `[name]` is omitted, the command lists characters and asks.

This command writes only under `campaigns/{slug}/supplements/party-options/`, which is **git-ignored** — so character names and build details are fine there. (This command *file* is committed, so it hardcodes none of them; everything is read from the campaign at runtime.)

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Parse Args & Select the Character

1. Parse the argument string: the first non-flag token is `{name}`; the presence of `--verify` sets **verify mode** (otherwise **create/update mode**).
2. If `{name}` is missing or doesn't match a file, list `campaigns/{campaign-slug}/players/` (PCs and companions) and ask which to use.
3. **Read the character's sheet in full** (`players/{name}.md`). Extract: race/species, class + subclass, level, feats, spell save DC, and any spells listed. This sheet is the **source of truth** for what the character actually has.

---

## Step 2: Ensure the Supplement Scaffold

Check that `campaigns/{campaign-slug}/supplements/party-options/` exists and is registered in `campaigns/{campaign-slug}/supplements/_manifest.json`.

If the directory or manifest entry is **missing**, create it before continuing:
- Create `party-options/_summary.md` and `party-options/_index.md` from the templates at the bottom of this file.
- Add the manifest entry (template at bottom).
- Create book subfolders lazily as needed (see Step 3A).

If it already exists, read `_index.md` (the routing table) so you know what's already documented.

---

## Step 3: Branch on Mode

- **Create/update mode** → Step 3A.
- **Verify mode** (`--verify`) → Step 3B.

---

## Step 3A: Create / Update the Character's Entries

Goal: ensure every **non-SRD** option on the character's sheet has a paraphrased entry in the right place. Honor these principles throughout:

- **SRD-first / delta.** Before authoring anything, check `supplements/srd-2024/` (and `srd-2014/` for fallback topics). If the option's full text is already in the SRD, **do not duplicate it** — add a one-line pointer to the SRD file instead. Only author content the SRD lacks (PHB/other-book subclasses, PHB-only feats/spells, non-SRD species).
- **Paraphrase, never copy.** Summarize mechanics in your own words. Do **not** reproduce verbatim book text. Mark anything you're not fully certain of with **`⚠ VERIFY`**.
- **Option 3 edition handling.** This party mixes rule editions. Lead each class/subclass entry with the **edition the sheet actually uses**, then add a short "differences" section for the other edition where they diverge. If the sheet's edition is ambiguous, ask the user.
- **Source book per option.** Each option lives in a book subfolder. Ask the user which book an option comes from if it isn't obvious. Folder slugs: `phb-2024`, `phb-2014`, `motmv` (Monsters of the Multiverse), `xge`, `tce`, etc. (lowercase, kebab).

### 3A.1 — Inventory what's needed
From the sheet, build a checklist of the character's options and classify each:
| Option | Type | In SRD? | Action |
|---|---|---|---|
| species | race | check `character-origins.md` | pointer if present, else author |
| class core | class | usually in SRD | pointer (summarize chassis only if a companion tracks it) |
| subclass | class | rarely in SRD | author (Option 3) |
| each feat | feat | check `srd-2024/feats.md` | add to `{book}/feats.md` (one-liner if SRD) |
| notable spells | spell | check `srd-2024/spells.md` | only PHB-only spells → `{book}/spells.md` |

Confirm the source book + edition for each non-SRD option with the user where unclear.

### 3A.2 — Write the files
For each non-SRD option, create or update the target file under the correct book subfolder:
- **Species** → `{book}/races/{species}.md`
- **Subclass / full class** → `{book}/classes/{class-or-subclass}.md`. Subclass-only files stay thin (subclass features + cross-ref SRD for the chassis); give a fuller chassis summary only when a **companion** tracks that class.
- **Feats** → `{book}/feats.md` (the character's feats detailed; SRD feats as `→ SRD` one-liners).
- **Spells** → `{book}/spells.md` (PHB-only spells; SRD-first).

When **updating** an existing file, append/modify rather than overwriting unrelated content, and note who uses the option.

### 3A.3 — Update routing & manifest
- Add/refresh rows in `_index.md` (Topic | Source | file | who) and the keyword routing table.
- Ensure the manifest entry exists (Step 2).

### 3A.4 — Summarize
Report what was created/updated, and **list every `⚠ VERIFY` marker authored**. Suggest: "Run `/party-options {name} --verify` to confirm these against your book."

---

## Step 3B: Verify the Character's Entries

Goal: bring the character's party-options entries into confirmed agreement with the sheet and the source books. This is an interactive pass.

### 3B.1 — Gather
Read the character's sheet and every party-options file that references them (their species, subclass/class, their rows in `feats.md` / `spells.md`).

### 3B.2 — Run checks and build a report
1. **Sheet ↔ options consistency.** Compare race, class, subclass, level, feats, spell save DC, and listed spells. Flag every mismatch (e.g., sheet says one subclass edition, file documents another).
2. **SRD overlap.** Flag anything documented here whose full text is actually in the SRD — recommend replacing with a pointer.
3. **Completeness.** Flag any feature/feat/spell on the sheet that has **no** party-options entry yet.
4. **Verify markers.** Collect every `⚠ VERIFY` in the character's files.

Display the findings as a numbered checklist grouped by the four categories.

### 3B.3 — Walk the items interactively
For each flagged item (mismatches, SRD-overlap, missing, and `⚠ VERIFY` markers), present it one at a time:

```
[3/8] sorcerer.md — Metamagic SP cost for Twinned Spell marked ⚠ VERIFY.
Documented: "1 SP". Confirm against your PHB.
  confirm (remove marker) / correct (give the right value) / skip / quit
```

- **confirm** → remove the `⚠ VERIFY` marker (and fix wording if the user adds detail).
- **correct** → apply the user's correction, then clear the marker.
- For **mismatches** → ask which side is right (sheet or file) and reconcile both if needed (a sheet fix may warrant `/update-player`).
- **SRD-overlap** → on approval, replace the duplicated text with an SRD pointer.
- **missing** → offer to author the entry now (drop into Step 3A.2 for that one option).
- **skip** → leave as-is. **quit** → stop the walk.

### 3B.4 — Summarize
Report: markers cleared, corrections applied, mismatches reconciled, entries added, and anything still outstanding (skipped / unresolved).

---

## Templates

### Manifest entry (campaign `_manifest.json`)
```json
{
  "slug": "party-options",
  "title": "Party Options — non-SRD class/subclass/species/feat/spell reference",
  "kind": "rules-supplement",
  "summary": "party-options/_summary.md",
  "index": "party-options/_index.md",
  "added": "{today}"
}
```

### `_summary.md` (created once)
State: purpose (non-SRD delta over the SRD for options in play), campaign-private/git-ignored, **paraphrased not verbatim** with `⚠ VERIFY` convention, the source books covered, and a "who uses what" list. Note it's the delta — SRD is the default; this fills gaps.

### `_index.md` (created once, then kept current)
A "Files" table (Topic | Source | file | who), a keyword→file routing table, and a "Cross-reference (already in SRD — don't duplicate)" section pointing core class chassis, most spells, and SRD feats back to `srd-2024/`.

### Per-file conventions
- **Species/subclass/class file:** lead with the in-play edition; a "differences" section for the other edition; a "Sheet reconciliation" note listing anything to confirm. Cross-ref the SRD for shared chassis text.
- **`feats.md`:** the character's feats in full (with the 2024 +1 ASI rider noted); all other book feats as one-line summaries; SRD feats as `→ SRD`.
- **`spells.md`:** SRD-first instructions; only author PHB-only spells, each confirmed absent from `srd-2024/spells.md` before adding.
- Always mark uncertain specifics with `⚠ VERIFY`.
