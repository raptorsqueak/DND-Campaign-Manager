# /update-player — Update a Player Character Sheet

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Select a Player

List all files in `DND-Campaign-Manager/campaigns/{campaign-slug}/players/`, with each file representing a player's information.

Display a numbered list of the available players, asking which player to update.

Read the selected player's file in full before continuing.

---

## Step 2: Update Menu

Display:

```
Updating: {Character Name} — {Race} {Class} Level {level}

What would you like to update?
  1. Level up
  2. Fill in missing stats (ability scores, AC, HP, skills, etc.)
  3. Equipment — add, remove, or change items
  4. Currency — update gold or other currency
  5. HP — update current or maximum HP
  6. Spell slots & spells — update remaining slots or spell list
  7. Backstory / personality — edit narrative fields
  8. Session notes — add notes from a recent session
  9. Free edit — describe what to change in plain language

(You can also list multiple numbers to do several at once, e.g. "1 3 4")
```

Wait for the user's selection, then handle each chosen option as described below. If multiple options are selected, handle them in order.

---

## Option 1: Level Up

Ask: "What level are they going to? (current level is {n})"

If leveling up more than one level at once, apply changes for each level in sequence.

For each new level:

**1. HP increase**
- Ask: "Roll your hit die (d{n}) and add your CON modifier ({+/-n}), or take the average ({average + CON mod}). What's the result?"
- Add to HP maximum.

**2. Proficiency bonus**
- Check if proficiency bonus increases (increases at levels 5, 9, 13, 17). If so, note it — all proficient skills, saves, and spell DCs/attacks increase automatically.

**3. Class features**
- List the new class features gained at this level based on the character's class (use built-in 5e knowledge). Describe each briefly.
- If an **Ability Score Improvement** is gained (Fighter: 4, 6, 8, 10, 12, 14, 16, 19; most others: 4, 8, 12, 16, 19):
  - Ask: "ASI or feat? If ASI, which scores and by how much? If feat, which feat?"
  - Apply the improvement and recalculate affected modifiers.

**4. Spellcasting (if applicable)**
- Update spell slots to the new level's table.
- Ask: "Do you learn any new spells at this level? List them, or 'none'."

**5. Update the file**
- Increment `Class` level
- Update HP max
- Update proficiency bonus if changed
- Add new class features to Features & Traits section
- Update ability scores if ASI was taken
- Recalculate all affected modifiers (saves, skills, spell DC, spell attack)
- Update spell slots and spell list

Display a summary of all changes made.

---

## Option 2: Fill In Missing Stats

Read the player file and identify fields that are blank, `—`, or missing.

For each missing field, ask for the value — group related fields into a single question where it makes sense (e.g. ask for all six ability scores at once if none are filled in).

Common fields to check:
- Ability scores (STR, DEX, CON, INT, WIS, CHA)
- AC and armor type
- HP maximum
- Class and subclass
- Saving throw proficiencies
- Skill proficiencies
- Weapon/armor/tool/language proficiencies
- Class features and racial traits
- Spellcasting details (if applicable)

Once all values are collected, recalculate derived stats (modifiers, save values, skill modifiers, spell DC, spell attack) and write the complete updated sheet.

---

## Option 3: Equipment

Ask: "What's changing?
  a. Add items
  b. Remove items
  c. Replace an item
  d. Describe the change in plain language"

Apply the stated change to the Equipment section. If an item affects AC, HP, or other stats, update those as well.

---

## Option 4: Currency

Ask: "What's the new gold total? Or describe the change (e.g. 'spent 50gp', 'gained 200gp')."

Update the Currency section. If the player file has a ledger format, append a new row with the change and running total.

---

## Option 5: HP

Ask: "Current HP, max HP, or both?"

Update accordingly. If max HP is changing (e.g. effect, feat, or correction), note the reason.

---

## Option 6: Spell Slots & Spells

Ask: "What's changing?
  a. Update remaining spell slots (current session tracking)
  b. Add or remove spells from the spell list
  c. Reset all slots to full (after long rest)"

Apply the change. If adding spells, ask for name and level.

---

## Option 7: Backstory / Personality

Display the current text for the relevant field(s). Ask: "What would you like to change or add?"

Apply the edit — append to existing text rather than overwrite unless the user explicitly says to replace it.

---

## Option 8: Session Notes

Append to the `## Session Notes` section of the player file:

```markdown
**{today's date}** — {note}
```

Ask: "What's the note?" Keep it brief — this section is for in-play tracking, not narrative.

---

## Option 9: Free Edit

Ask: "Describe what to change."

Parse the request and apply it to the appropriate section(s) of the file. If the change is ambiguous, confirm before writing.

---

## Step 3: Write & Confirm

After all selected options are handled:

1. Update `**Last Updated**: {today's date}` at the top of the file
2. Write the updated file
3. Display a summary:

```
Updated: {Character Name}
Changes:
  - {change 1}
  - {change 2}
  - ...
```

Then ask: "Anything else to update on {character name}, or are you done?"

If more changes: return to the update menu.
If done: end the command.
