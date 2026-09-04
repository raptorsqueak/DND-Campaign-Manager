# /plan-next-session — Session Planning Assistant

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load Full Campaign Context

Read all of the following before asking any questions:

1. `DND-Campaign-Manager/campaigns/{campaign-slug}/campaign.json` — current state, location, quests, level, and `obsidian_vault` path (store this for use in Step 5)
2. `DND-Campaign-Manager/campaigns/{campaign-slug}/session-log.md` — full log for history; focus on last 3 sessions for immediate context
3. All files in `DND-Campaign-Manager/campaigns/{campaign-slug}/players/` — backstories, companions, hooks, equipment
4. All files in `DND-Campaign-Manager/campaigns/{campaign-slug}/npcs/` — standing relationships, outstanding threads
5. **Supplements (manifest-first)**:
   - Read `DND-Campaign-Manager/campaigns/{campaign-slug}/supplements/_manifest.json` and `DND-Campaign-Manager/supplements/_manifest.json`. Fall back to "scan top-level *.md files" if a manifest is missing.
   - Read every `summary_text` (flat entries) and every `_summary.md` (wrapped entries). These are cheap.
   - Always-load in full:
     - All flat `kind: rules-supplement` entries (DM instructions — combat-rules, spellcasting, items-and-loot, character-sheets, npc-generation, campaign-generation).
     - All flat `kind: character-backstory` and `kind: homebrew-mechanic` entries (the party's backstory and homebrew items inform every plan).
   - For wrapped `kind: adventure-book` entries (e.g., the active book): read `_index.md` to find chapter files matching the party's `current_location` from `campaign.json` and any chapters covering active quests. Load **only those chapter files**, not the whole book.
6. **Supplement state** (per-book DM tracking): Read every `.md` file in `DND-Campaign-Manager/campaigns/{campaign-slug}/supplement-state/` (chapters completed, NPCs killed/modified, encounters skipped). The plan must respect what's already been used.

The active book is determined by the campaign manifest entry whose summary text marks it as the campaign's primary book. The DM-state files name which book they track (filename matches the supplement slug).

---

## Step 2: Planning Interview

Tell the user: "Let's plan Session #{current_session + 1}. I'll ask a few questions to help build the session — brief answers are fine."

Ask **one at a time**, waiting for each response:

1. **Tone**: "What's the overall feel you want for this session? (e.g., tense combat-heavy, roleplay-driven, exploration, a mix, funny, dark)"
   — **Skip this question** if `campaigns/{campaign-slug}/conventions.md` states a default session tone. Use that, and say which tone you're using rather than asking.
2. **Focus**: "Is there a particular player, backstory thread, or quest you want to spotlight this session?"
3. **Location**: "Where does the session start, and do you have a sense of where it ends up?"
4. **Time available**: "Roughly how long is your session? (e.g., 2 hours, 3–4 hours, full day)"
5. **Constraints**: "Anything off the table or that you want to avoid this session? (e.g., a player is absent, avoid a specific topic, don't introduce new NPCs)"
6. **Anything set in stone**: "Is there any scene, moment, or beat you've already decided will happen? (or 'none')"

---

## Step 3: Generate the Session Plan

Using all loaded context and the answers above, produce a structured session plan.

The plan should:
- **Tie into recent events** from the session log — players should feel continuity
- **Weave in at least one player backstory thread** naturally (don't force all of them)
- **Include at least one moment that could pay off a companion dynamic** for one of the party's companions (drawn from player files and supplements)
- **Seed any active foreshadowing** tied to DM secrets noted in the campaign supplements
- **Use NPCs already on file** before introducing new ones
- **Respect the time constraint** — scale encounters and scenes to fit
- **Flag any DM secrets** that could be teased or advanced this session (clearly marked)

**Pick a plan shape first.** The three-act format below assumes the session has a driving sequence — the party is being carried from beat to beat. That is not always true. Choose:

- **Non-linear menu format** when the party sets its own agenda: a hub/city/settlement with several destinations, a dungeon or region explored at the party's discretion, a downtime or shopping session, a travel leg with optional sites, or any session where the DM's Step 2 answers describe *places* rather than a *sequence*. Use this by default whenever the party's next move is genuinely open.
- **Three-act format** when the session has committed momentum: a scheduled confrontation, a pursuit, an ambush the party walks into, a boss fight, a session opening mid-combat, or a scripted set piece.

If ambiguous, ask: "Is this session a sequence the party moves through, or a set of places they choose between?" **Do not default to three acts.**

### Non-linear menu format

```
=== SESSION #{n} PLAN ===
Campaign: {name}
Tone / Focus / Location / Estimated Length
Time Budget: ~{n} location blocks fit in {time}

## Opening Scene
{Where the party is and what puts the choice in front of them}

## Location Blocks
Each block is self-contained and playable in any order. Give every block a time cost so the DM can budget live.

### {Location name} — ~{n} min
**Who's here:** {NPCs on file}
**What's available:** {service, information, encounter, item}
**Hook:** {why the party would come here}
**If they push further:** {the deeper thing behind the obvious thing}

(repeat — aim for ~1.5x as many blocks as the time budget fits, so the choices are real)

## Standing Threads
{What progresses regardless of which blocks they pick — a timer, a pursuer, a rumor}

## If the party splits
{How to run parallel blocks without stalling the table}

## Backstory & Character Threads
## NPC Appearances
## Potential Loot / Rewards
## DM Eyes Only
{Include: what happens if the party never visits a given block}
===
```

### Three-act format

Display the plan in this format:

```
=== SESSION #{n} PLAN ===
Campaign: {name}
Session Date: TBD
Tone: {tone}
Focus: {focus}
Location: {location}
Estimated Length: {time}

---

## Opening Scene
{How the session begins — where the party is, what's immediately in front of them, what mood to set}

---

## Act 1: {title}
{First major beat — location, NPCs involved, goal, possible player actions}

**Encounter / Scene options:**
- {option A}
- {option B}

**If players go off-script:** {brief contingency note}

---

## Act 2: {title}
{Second major beat — builds on Act 1, escalates or pivots}

**Encounter / Scene options:**
- {option A}
- {option B}

**If players go off-script:** {brief contingency note}

---

## Act 3 / Closing Beat: {title}
{How the session ends — cliffhanger, resolution, revelation, or quiet moment. Should leave players wanting more.}

---

## Backstory & Character Threads
{Which player threads are being pulled on this session and how — one paragraph per active thread}

---

## NPC Appearances
{List each NPC likely to appear with one-line reminder of their standing and role this session}

---

## Potential Loot / Rewards
{Suggested loot tied to the session's encounters — keep appropriate to party level {party_level}}

---

## DM Eyes Only
{Plot threads to advance, secrets to seed, foreshadowing to drop, anything the players shouldn't see}

===
```

---

## Step 4: Refinement

After displaying the plan, ask:

```
Options:
  1. Expand a specific section
  2. Swap the focus to a different player/thread
  3. Add or remove an encounter
  4. Save this plan to the campaign supplements folder
  5. Done — looks good
```

**If saving**: Ask "What date is this session? (YYYY-MM-DD)" and "What's a short title for this session? (e.g., 'Heading to Yartar')" — then ensure `DND-Campaign-Manager/campaigns/{campaign-slug}/sessions/` exists and write the plan to `DND-Campaign-Manager/campaigns/{campaign-slug}/sessions/{YYYY-MM-DD} {title}.md`. Confirm: "Plan saved to sessions/{YYYY-MM-DD} {title}.md"

(Plans are session-prep artifacts, not reference supplements — they live in `sessions/` alongside `session-log.md`, not in `supplements/`. The supplements directory is for reference content like adventure books and rules supplements.)

**If expanding**: Produce the expanded section in full — stat blocks if combat, full NPC dialogue beats if roleplay, room descriptions if exploration.

**If swapping / adjusting**: Revise the affected sections and re-display.

Continue offering refinement options until the user selects "Done."

---

## Step 5: Obsidian Campaign Note

Once the user selects "Done", ask:

"Would you like to add a session prep note to your Obsidian vault? (yes / no)"

**If no**: end the command.

**If yes**:

Ask: "What's a short title for this session? (e.g., 'Heading to Yartar', 'Silverymoon Intrigue')"

Then derive the filename:
- Format: `{today's date YYYY-MM-DD} {title}.md`
- Write to: `{obsidian_vault}/Campaign/{filename}`

Write the note using the Obsidian session note template this campaign uses:

```markdown
# Before
{Bullet points of DM prep: key beats, NPC notes, encounter reminders, things to remember from the plan — drawn from the session plan's Opening Scene, Acts, and DM Eyes Only section. Keep each point brief; this is a reference, not a narrative.}

# During
{Leave blank — to be filled in during play}

# After
{Leave blank — to be filled in after the session}
```

The `# Before` section should be a condensed, table-ready version of the plan — the things the DM needs in front of them at the table. Stat blocks, boxed text, and full prose belong in the campaign supplements file. This note is the at-a-glance reference.

Confirm: "Obsidian note created: `Campaign/{filename}`"

---

### Full plan in DM-selected folder (optional)

After creating the Campaign note, ask:

"Would you also like to write the full plan to a specific vault folder? This is useful for reusable reference material — e.g., a book chapter folder. (yes / no)"

**If no**: end the command.

**If yes**:
- Ask: "Which folder? (relative to vault root — e.g., 'Storm King/Chapter 3 - The Savage Frontier')"
- Ask: "File title? (no date — this is reusable reference material — e.g., 'To Yartar')"
- Check that `{obsidian_vault}/{folder}/{title}.md` does not already exist. If it does, ask: "File already exists. Overwrite? (yes / no)" — if no, end the command.
- If the folder does not exist, create it.
- Read the saved supplements plan file (if saved in Step 4) or use the plan generated in Step 3.
- Before writing, modify the content:
  - Add a wikilink header at the top: `*Session notes: [[{today's date YYYY-MM-DD} {title}]]*`
  - Convert any unlinked occurrences of PC names (from player files) and NPC names (from NPC files) to `[[Name]]` wikilinks. Do not double-link names already inside `[[...]]`.
- Write `{obsidian_vault}/{folder}/{title}.md` with the modified content.
- Append a back-reference line to the Campaign note just below the `# Before` heading:
  `*Full plan: [[{title}]]*`

Confirm: "Full plan created: `{folder}/{title}.md`"
