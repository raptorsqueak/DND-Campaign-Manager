# /plan-next-session — Session Planning Assistant

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load Full Campaign Context

Read all of the following before asking any questions:

1. `DNDCampaign/campaigns/{campaign-slug}/campaign.json` — current state, location, quests, level, and `obsidian_vault` path (store this for use in Step 5)
2. `DNDCampaign/campaigns/{campaign-slug}/session-log.md` — full log for history; focus on last 3 sessions for immediate context
3. All files in `DNDCampaign/campaigns/{campaign-slug}/players/` — backstories, companions, hooks, equipment
4. All files in `DNDCampaign/campaigns/{campaign-slug}/npcs/` — standing relationships, outstanding threads
5. All `.md` files in `DNDCampaign/campaigns/{campaign-slug}/supplements/`
6. All `.md` files in `DNDCampaign/supplements/`

Then load the relevant book file based on `campaign.json → book`:
- "Storm King's Thunder" → `DNDCampaign/campaigns/{campaign-slug}/supplements/storm-kings-thunder.md`
- "Dungeon of the Mad Mage" → `DNDCampaign/campaigns/{campaign-slug}/supplements/dungeon-of-the-mad-mage.md`

---

## Step 2: Planning Interview

Tell the user: "Let's plan Session #{current_session + 1}. I'll ask a few questions to help build the session — brief answers are fine."

Ask **one at a time**, waiting for each response:

1. **Tone**: "What's the overall feel you want for this session? (e.g., tense combat-heavy, roleplay-driven, exploration, a mix, funny, dark)"
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

**If saving**: Ask "What date is this session? (YYYY-MM-DD)" and "What's a short title for this session? (e.g., 'Heading to Yartar')" — then write the plan to `DNDCampaign/campaigns/{campaign-slug}/supplements/{YYYY-MM-DD} {title}.md` and confirm: "Plan saved to supplements/{YYYY-MM-DD} {title}.md"

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
