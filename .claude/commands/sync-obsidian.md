# /sync-obsidian — Sync Campaign Data with Obsidian Vault

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load Campaign Context

Read the following:

1. `DND-Campaign-Manager/campaigns/{campaign-slug}/campaign.json` — extract `obsidian_vault`, `name`, and `current_session`
2. All files in `DND-Campaign-Manager/campaigns/{campaign-slug}/players/` — character name, equipment, companion, stats
3. All files in `DND-Campaign-Manager/campaigns/{campaign-slug}/npcs/` — NPC name, role, location, standing, personality, DM notes
4. `DND-Campaign-Manager/campaigns/{campaign-slug}/session-log.md` — extract each `## Session {n}` block with its real-world date
5. All `.md` files in `DND-Campaign-Manager/campaigns/{campaign-slug}/supplements/` — identify session plan files (any with a `YYYY-MM-DD` prefix in the filename); store their `{date}` and `{title}` for Step 3c

If `obsidian_vault` is not set or is empty in campaign.json, stop and say: "No Obsidian vault configured for this campaign. Add an `obsidian_vault` path to campaign.json first (via /campaign-info)."

Store `{vault}` = the obsidian_vault path.

---

## Step 2: Scan the Obsidian Vault

Run a **single** `find` over all four target subtrees rather than separate `ls` calls per directory:

```bash
find "{vault}/Playable Characters" "{vault}/NPCs" "{vault}/Sessions" "{vault}/Items" -maxdepth 2 -type f -name '*.md' 2>/dev/null
```

The `2>/dev/null` suppresses errors for directories that don't exist (those simply contribute zero results). Partition the returned paths by their top-level subtree:

- `{vault}/Playable Characters/` — one file per PC/companion
- `{vault}/NPCs/` and all subdirectories — one file per NPC, organized by location (NPCs need depth 2 for location subdirectories — the `-maxdepth 2` above covers this)
- `{vault}/Sessions/` — session prep notes, filenames begin with YYYY-MM-DD
- `{vault}/Items/` — one file per item

If a subtree yielded zero results AND the directory itself is missing, note it and skip that category during the rest of the command. Do **not** issue separate per-directory `ls` calls — one `find` replaces all four.

---

## Step 3: Build Sync Report

### 3a: Players and Companions

For each file in `campaigns/{slug}/players/`:
- Extract the character name from the `# Name` heading or filename
- Search `{vault}/Playable Characters/` for a matching file (case-insensitive, ignore hyphens/spaces)
- Classify:
  - **✓ Synced** — vault file exists and all key sections are present (stats, equipment, backstory/personality)
  - **+ New** — no vault file exists; will be created
  - **⚠ Enrichable** — vault file exists but project has data the vault lacks; check all of:
    - Stats block (ability scores, AC, HP, initiative, spell DC/attack)
    - Equipment (any items in project not present in vault)
    - Backstory / personality / roleplaying notes
    - Companion info
    - Class features or abilities (for companions)

### 3b: NPCs

For each file in `campaigns/{slug}/npcs/`:
- Extract the NPC name from the `# Name` or `## Name` heading
- Search all subdirectories of `{vault}/NPCs/` for a matching file (case-insensitive)
- Classify:
  - **✓ Synced** — vault file exists
  - **+ New** — no vault file; will be created in the correct subdirectory
  - **⚠ Enrichable** — vault file exists but project has content the vault lacks

Also identify NPCs that are in the vault but NOT in the project — mark these **~ Vault-only**. They will never be modified.

### 3c: Session Plans

For each `.md` file in `campaigns/{slug}/supplements/` whose filename begins with a `YYYY-MM-DD` prefix:
- Extract `{date}` and `{title}` from the filename
- Check if `{vault}/Sessions/` has any file whose filename starts with `{date}`
- Classify:
  - **✓ Covered** — a Campaign vault note exists with that date prefix
  - **+ Missing** — no Campaign vault note for that date

### 3d: Campaign Notes

Parse `session-log.md` for each `## Session {n}` block — extract the real-world date (format: `YYYY-MM-DD`).
List `{vault}/Sessions/` files and parse dates from filenames (YYYY-MM-DD prefix).
For each session:
- **✓ Covered** — a Campaign vault note exists whose filename starts with that date
- **+ Missing** — no vault note for that date

### 3e: Display the Report

Display:

```
=== OBSIDIAN SYNC REPORT ===
Campaign: {name}
Vault: {vault}

PLAYABLE CHARACTERS & COMPANIONS ({count} in project)
  {icon} {Name} — {reason}
  ...

NPCS ({count} in project, {count} in vault)
  New (to be created): {count}
    + {Name} → NPCs/{subdirectory}/
    ...
  Enrichable (vault exists, project has more): {count}
    ⚠ {Name} — missing: {what}
    ...
  Synced: {count}
  Vault-only (will not be touched): {count}
    ~ {Name} ({subdirectory}/)
    ...

SESSION PLANS ({count} in supplements)
  ✓ {date} {title} — Sessions/{vault filename}
  + {date} {title} — no vault note
  ...

CAMPAIGN NOTES ({count} sessions in log)
  ✓ Session {n} ({date}) — {vault filename}
  + Session {n} ({date}) — no vault note
  ...

Summary: {n} items to create, {n} items to enrich
===
```

---

## Step 4: Confirm Sync Scope

Ask:

```
What would you like to sync?
  1. All (Players + Companions + NPCs + Session Plans + Campaign Notes)
  2. Players & Companions only
  3. NPCs only
  4. Session Plans only
  5. Campaign Notes only
  6. Cancel
```

If Cancel → end the command.

---

## Step 5: Sync Players and Companions

Process only the categories selected in Step 4.

### For each + New player or companion:

Determine if the file is a **PC** (has ability scores / class / player name) or a **Companion** (creature form, bonded to a PC, no human player).

**PC format** — write `{vault}/Playable Characters/{Name}.md`:

```markdown
{If the PC has a companion: "Companion is [[{CompanionName}]]"}

## Stats
**Race:** {race} | **Class:** {class} (Level {n}) | **Alignment:** {alignment}
**AC:** {n} | **HP:** {current}/{max} | **Initiative:** {+n} | **Speed:** {n} ft

## Equipment
{For each item in the project file:
  - If the item name matches a file in {vault}/Items/ → "- [[{Item Name}]]"
  - Otherwise → "- {item name}"}
```

If stats are missing or blank in the project file, omit that line rather than writing "—".

**Companion format** — write `{vault}/Playable Characters/{Name}.md`:

```markdown
# {Name}

**Type:** {apparent form / creature type}
**Bond:** [[{bonded PC name}]]

{2–4 sentences: key personality, communication style, most distinctive behaviors}

## Abilities
{notable abilities — telepathy, flight, combat role, etc.}

## Equipment / Treasure
{items from project file, with wikilinks where matching vault Items/ files exist}
```

Confirm each: `"Created: Playable Characters/{Name}.md"`

---

### For each ⚠ Enrichable player or companion:

Read the existing vault file in full.
Compare with the project file.
Check each of the following and note what is missing from the vault:

1. **Stats block** — ability scores, AC, HP, initiative, speed, proficiency bonus, spell DC/attack (if caster)
2. **Equipment** — any items present in the project but absent from the vault list
3. **Backstory** — if the project has a Backstory section and the vault does not
4. **Personality / Roleplaying Notes** — traits, ideals, bonds, flaws, or roleplaying guidance in the project but not in the vault
5. **Companion info** — companion wikilink or description if missing
6. **Abilities** — for companions: communication style, notable abilities, quirks

Compile all missing content into a single append block. Show:

```
⚠ Updating: Playable Characters/{Name}.md
  Will add: stats block, equipment ({n} items), backstory, personality
  [exact text to be appended]

Confirm? (yes / no / skip)
```

If **yes**: append all missing content to the vault file in one edit, preceded by `---`. NEVER remove or overwrite existing vault content.
If **no** or **skip**: leave unchanged.

---

## Step 6: Sync NPCs

Process only the categories selected in Step 4.

### Location mapping

Use this table to determine the vault subdirectory from the NPC's **Location** field in the project file:

| Location field contains… | Vault subdirectory |
|---|---|
| Waterdeep | `Waterdeep/` |
| Undermountain | `Undermountain/` |
| Amphail | `Amphail/` |
| Everlund | `Everlund/` |
| Triboar | `Triboar/` |
| Silverymoon / Silver Moon / Silvery Moon | `Silvery Moon/` |
| Underdark | `Underdark/` |
| Road / Wilderness / traveling / en route / journey | `Road & Wilderness/` |
| No match | root `NPCs/` — note to user that manual organization may be needed |

If the mapped subdirectory does not yet exist in the vault, create it.

---

### For each + New NPC:

Write `{vault}/NPCs/{subdirectory}/{NPC Name}.md`:

```markdown
- **Role:** {role}
- **Race/Type:** {race or creature type, if known}
- **Location:** {location}
- **Allegiance:** {affiliation, or omit if "None"}
- **Standing:** {Hostile / Unfriendly / Indifferent / Friendly / Allied} to party

**Personality:** {demeanor, motivation — 1–2 sentences}
**Secret:** *(DM) {secret, or omit if none}*
**Quirk:** {quirk, voice/speech patterns, or omit if none}

**Useful for:** {what they can offer the party}

**DM Notes:** *(DM) {dm notes, or omit if none}*
```

Omit any line where the project value is blank, "(none)", or "(not combat-relevant)".

Confirm each: `"Created: NPCs/{subdirectory}/{Name}.md"`

---

### For each ⚠ Enrichable NPC:

Read the existing vault file.
Identify what the project file has that the vault entry lacks (DM notes, combat stats, party history, additional personality detail, etc.).

Show:

```
⚠ Updating: NPCs/{subdirectory}/{Name}.md
  Will append: {what}
  [exact text to be added]

Confirm? (yes / no / skip)
```

If **yes**: append the missing content at the bottom of the vault file, preceded by `---`. NEVER remove or overwrite existing vault content.
If **no** or **skip**: leave unchanged.

---

## Step 7: Sync Session Plans

Process only the categories selected in Step 4.

For each session plan in `supplements/` that has no Campaign vault note (classified **+ Missing** in Step 3c):

Ask: `"Session plan '{date} {title}' has no vault note. Sync it? (yes / no / skip remaining)"`

If **yes**:

### Part A — Campaign summary note (Before/During/After)

- Check that `{vault}/Sessions/{date} {title}.md` does not already exist — if it does, warn and skip Part A.
- Read the plan file.
- From the plan's Opening Scene, Acts, and DM Eyes Only sections, generate condensed bullet points for the `# Before` section — key beats, encounter reminders, NPC notes, DM secrets. Keep each bullet brief; this is a table reference, not a narrative.
- Write `{vault}/Sessions/{date} {title}.md`:

```markdown
# Before
{condensed bullet points from the plan}

# During

# After
```

- Confirm: `"Created: Sessions/{date} {title}.md"`

### Part B — Full plan in DM-selected folder

Ask: `"Write the full plan to a specific vault folder for reference? (yes / no)"`

If **yes**:
- Ask: `"Which folder? (relative to vault root — e.g., 'Storm King/Chapter 3 - The Savage Frontier')"`
- Ask: `"File title? (no date — this is reusable reference material — e.g., 'To Yartar')"`
- Check that `{vault}/{folder}/{title}.md` does not already exist. If it does, ask: `"File already exists. Overwrite? (yes / no)"` — if no, skip Part B.
- If the folder does not exist in the vault, create it.
- Read the plan file content. Before writing:
  - Add a wikilink header at the top: `*Session notes: [[{date} {title}]]*`
  - Convert any unlinked occurrences of PC names (from player files) and NPC names (from NPC files) to `[[Name]]` wikilinks. Do not double-link names already inside `[[...]]`.
- Write `{vault}/{folder}/{title}.md` with the modified content.
- Append a back-reference line to the Campaign note created in Part A, just below the `# Before` heading:
  `*Full plan: [[{title}]]*`
- Confirm: `"Created: {folder}/{title}.md"`

If **no** (skip full plan): continue.

If **no** (skip this plan): move to the next.
If **skip remaining**: stop processing session plans.

For plans already **✓ Covered** in Step 3c: never touch their Campaign vault notes.

---

## Step 8: Sync Campaign Notes

Process only the categories selected in Step 4.

For each session in `session-log.md` that has no corresponding vault note:

Ask: `"Session {n} ({date}) has no vault note. Create one? (yes / no / skip remaining)"`

If **yes**:
- Ask: `"Short title for this session? (e.g., 'Heading to Yartar', or press Enter to use the session location)"`
  - If the user presses Enter or gives a blank response, derive the title from the session's **Location** field in the log.
- Derive filename: `{date} {title}.md`
- Check that this file does NOT already exist in `{vault}/Sessions/` — if it does, skip with a warning.
- Write `{vault}/Sessions/{filename}`:

```markdown
# Before

# During

# After
{Summary block from session-log.md for this session — the ### Summary section and any notable events}
```

The `# After` section is pre-populated from the session log. `# Before` and `# During` are left blank for the DM to fill in.

Confirm: `"Created: Sessions/{filename}"`

If **no**: skip this session.
If **skip remaining**: stop processing campaign notes.

For sessions that **already have** a vault note: never touch them.

---

## Step 9: Items Sync (Optional)

After the selected sync categories are complete, display a brief summary of what was done, then ask:

`"Sync complete. Would you like to also sync items? I'll check which items from player equipment lists don't have a vault file in Items/ yet and offer to create placeholder entries. (yes / no)"`

If **no** → end the command with the final summary (see below).

If **yes**:
- Collect all items mentioned in player equipment lists across all player files
- For each item, check if `{vault}/Items/{item name}.md` exists (case-insensitive)
- Display what's missing:

```
Items missing from vault Items/:
  + {Item Name}
  + {Item Name}
  ...

Create entries for all missing items? (yes / no / select)
```

- **yes**: create all
- **no**: skip
- **select**: list them numbered and ask which to create

For each item being created, write `{vault}/Items/{Item Name}.md`:

```markdown
{If the project player file contains an inline description of the item (e.g., in parentheses after the item name), use that as the description.}
{Otherwise, write a single line: "*(Description not yet filled in.)*"}
```

Never overwrite an existing Items/ file.

Confirm each: `"Created: Items/{Item Name}.md"`

---

## Step 10: Final Summary

Display:

```
=== SYNC COMPLETE ===
  Players & Companions: {n} created, {n} enriched, {n} skipped
  NPCs: {n} created, {n} enriched, {n} skipped
  Session Plans: {n} synced, {n} skipped
  Campaign Notes: {n} created, {n} skipped
  Items: {n} created (or "Not run")

Vault: {vault}
===
```
