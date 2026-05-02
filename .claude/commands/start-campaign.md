# /start-campaign — Session Entry Point

This command starts or resumes a D&D 5e campaign management session.

---

## Step 1: Scan for Existing Campaigns

Use the Read tool (or Bash `ls`) to list all subdirectories inside `DNDCampaign/campaigns/`. For each directory found, read its `campaign.json` and extract: name, book, current_session, party_level, last_session.

If `DNDCampaign/campaigns/` does not exist or is empty, skip directly to **Create New Campaign**.

If campaigns are found, present a numbered list:

```
Existing campaigns:
1. Storm King's Thunder  (Book: Storm King's Thunder | Session 12 | Level 5 | Last played: 2026-03-15)
2. Mad Mage              (Book: Dungeon of the Mad Mage | Session 3 | Level 6 | Last played: 2026-01-20)

Type a number to resume, or "new" to start a new campaign.
```

If a `campaign.json` is missing or unreadable, show that entry as `(corrupt — skipping)`.

---

## Step 2: Handle User Selection

Wait for user input.

- **Number selected** → Resume Existing Campaign (see below)
- **"new"** → Create New Campaign (see below)

---

## Resume Existing Campaign

1. Read `DNDCampaign/campaigns/{slug}/campaign.json`
2. Read all files in `DNDCampaign/campaigns/{slug}/players/` — extract name, race, class, level for each
3. Count files in `DNDCampaign/campaigns/{slug}/npcs/`
4. Read the last 20 lines of `DNDCampaign/campaigns/{slug}/session-log.md` for recent context
5. Read all `.md` files in `DNDCampaign/supplements/` (global supplements)
6. Read all `.md` files in `DNDCampaign/campaigns/{slug}/supplements/` (campaign supplements)

Display a session briefing:

```
=== CAMPAIGN RESUMED ===
Campaign: {name}
Book: {book}
Session: #{current_session}
Party Level: {party_level}
Current Location: {current_location}
In-Game Date: {in_game_date}

Party ({count} players):
  - {character name} ({race} {class} Lv{level}) — played by {player name}
  - ...

NPCs on file: {count}

Active Quests:
  - {quest}
  - ...

Custom Notes: {custom_notes}
Obsidian Vault: {obsidian_vault if set, otherwise "(none linked)"}

Recent Session: {last 2–3 sentences extracted from session-log.md}
```

If no players yet: show `Party: (none yet — use /add-player)`
If no quests: show `Active Quests: (none recorded)`
If no session log entries: show `Recent Session: (no sessions logged yet)`
If no `obsidian_vault` field in campaign.json: show `Obsidian Vault: (none linked — add "obsidian_vault" to campaign.json to enable)`

End the response with this exact block (required — other commands depend on it):

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DNDCampaign/campaigns/{campaign-slug}/
```

---

## Create New Campaign

Ask the following questions **one at a time**, waiting for each answer before asking the next:

1. "What's the name of your campaign?"
2. "What adventure book or source are you running? (e.g., Storm King's Thunder, homebrew)"
3. "What is the setting? (e.g., Forgotten Realms, Eberron, homebrew world)"
4. "What level will the party start at?"
5. "Any custom notes about this campaign — house rules summary, tone, special rules? (type 'none' to skip)"

After collecting all answers:

**Derive the slug**: lowercase the campaign name, replace spaces with hyphens, remove apostrophes and special characters. Example: "Curse of Strahd" → `curse-of-strahd`.

**Check for collision**: if `DNDCampaign/campaigns/{slug}/` already exists, append `-2`, `-3`, etc.

**Write** `DNDCampaign/campaigns/{slug}/campaign.json`:
```json
{
  "name": "{campaign name}",
  "slug": "{slug}",
  "book": "{book}",
  "setting": "{setting}",
  "system": "D&D 5e",
  "created": "{today's date YYYY-MM-DD}",
  "last_session": "{today's date YYYY-MM-DD}",
  "current_session": 0,
  "party_level": {starting level},
  "in_game_date": "",
  "current_location": "",
  "active_quests": [],
  "obsidian_vault": "",
  "custom_notes": "{notes or empty string}"
}
```

**Create directories**:
- `DNDCampaign/campaigns/{slug}/players/`
- `DNDCampaign/campaigns/{slug}/npcs/`
- `DNDCampaign/campaigns/{slug}/supplements/`

**Write** `DNDCampaign/campaigns/{slug}/session-log.md`:
```markdown
# Session Log — {campaign name}
```

Display confirmation:

```
=== NEW CAMPAIGN CREATED ===
Campaign: {name}
Book: {book}
Setting: {setting}
Starting Level: {level}

Next steps:
  /add-player      — Add your first player character
  /campaign-info   — Update current location and in-game date
  /ask-dnd         — Ask rules questions
  /generate-npc    — Generate a contextual NPC

To link an Obsidian vault: add "obsidian_vault": "/path/to/vault" to campaign.json
```

End with the required block:

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DNDCampaign/campaigns/{campaign-slug}/
```
