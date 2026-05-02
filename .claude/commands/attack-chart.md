# /attack-chart — Generate Combat Attack Chart

Generates a pre-filled combat table with stats for all party members, companions, and enemies. Players roll their own initiative; enemies have initiative and HP rolled automatically.

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Identify Enemies

If the user provided enemy names or counts after the command (e.g., `/attack-chart 2 ogres, 1 troll`), use those directly.

Otherwise, ask: "What enemies is the party fighting? (e.g., `2 ogres`, `1 hill giant`, `3 bandits`)"

Wait for their response before continuing.

---

## Step 2: Ask Output Preference

Ask: "Write to file or terminal? (`file` / `terminal`)"

Wait for their response before continuing.

---

## Step 3: Load Player & Companion Data

Read all `.md` files in `DNDCampaign/campaigns/{campaign-slug}/players/`. For each file, extract:

- **Name** — the character name from the `#` heading or filename (use `[[Name]]` wikilink format in the table)
- **AC** — look for AC in the Combat / Combat Stats section; if not found, use `—`
- **HP** — max HP only (a single number); if not found, use `—`
- **+ to hit** — primary attack bonus:
  - For martial characters (Fighter, Rogue): use the higher of STR or DEX modifier + proficiency bonus; if a specific weapon attack bonus is listed, use that
  - For spellcasters (Cleric, Bard, Wizard, etc.): use the listed spell attack bonus
  - If no attack info is found (e.g., non-combat companions like familiars or pets), use `—`
- **Initiative** — leave blank; players and companions roll their own

List players in alphabetical order by character name.

---

## Step 4: Look Up Enemy Stats

For each enemy, check in this order:

1. `DNDCampaign/campaigns/{campaign-slug}/npcs/` — read the file if it exists; extract AC, hit dice, DEX modifier, and attack bonus
2. `DNDCampaign/campaigns/{campaign-slug}/supplements/` and `DNDCampaign/supplements/` — for any homebrew stat blocks
3. Built-in 5e SRD knowledge — use the standard stat block for the creature type

Extract for each enemy:
- **AC**
- **Hit Dice** (e.g., `7d10+14`) — used to roll HP
- **+ to hit** (primary attack)
- **Initiative modifier** (DEX modifier, or listed initiative bonus)

If there are multiple of the same type, treat each as a separate row and number them (e.g., Ogre 1, Ogre 2).

---

## Step 5: Roll Dice for Enemies

For each enemy, simulate the following rolls. Generate genuinely varied random numbers — do not always produce average or round values.

- **HP**: Roll the hit dice (each die individually) and sum with the flat modifier. Example: for `5d8+10`, roll five d8s and add 10.
- **Initiative**: Roll 1d20 and add the initiative modifier.

Before outputting the table, print the HP calculations as plain text:

```
HP rolls:
Knight: 8d8+16 → 58
Guard 1: 2d8+2 → 9
Guard 2: 2d8+2 → 13
...
```

---

## Step 6: Output the Chart

Table format — Damage and Notes columns are always left blank:

```
| Combatant | Initiative | AC | HP | + to hit | Damage | Notes |
| --------- | ---------- | -- | -- | -------- | ------ | ----- |
```

Order: all entries from the players directory first (alphabetical), then a blank separator row, then enemies.

- **HP**: single number for all rows — max HP for players/companions, rolled value for enemies; use `—` if unknown
- **Damage**: always blank
- **Notes**: always blank

---

## Step 7: Route Output

**If terminal**: output the table as raw markdown directly in the response.

**If file**:
- Derive the filename from the enemy list: lowercase each entry, replace spaces with hyphens, join entries with hyphens, append `-attack-chart.md`.
  - Example: "1 knight, 8 guards" → `1-knight-8-guards-attack-chart.md`
- Write the table to `DNDCampaign/campaigns/{campaign-slug}/{filename}` — the file contains only the table, no extra text.
- Confirm: "Table written to `campaigns/{campaign-slug}/{filename}`"
