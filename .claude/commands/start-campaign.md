# /start-campaign — Session Entry Point

This command starts or resumes a D&D 5e campaign management session.

---

## Step 1: Scan for Existing Campaigns

Use the Read tool (or Bash `ls`) to list all subdirectories inside `DND-Campaign-Manager/campaigns/`. For each directory found, read its `campaign.json` and extract: name, book, current_session, party_level, last_session.

If `DND-Campaign-Manager/campaigns/` does not exist or is empty, skip directly to **Create New Campaign**.

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

1. Read `DND-Campaign-Manager/campaigns/{slug}/campaign.json`
2. Read all files in `DND-Campaign-Manager/campaigns/{slug}/players/` — extract name, race, class, level for each
3. Count files in `DND-Campaign-Manager/campaigns/{slug}/npcs/`
4. Read the last 20 lines of `DND-Campaign-Manager/campaigns/{slug}/session-log.md` for recent context
5. **Supplement manifests** (don't load full content — just the manifest summaries):
   - `DND-Campaign-Manager/supplements/_manifest.json` (global)
   - `DND-Campaign-Manager/campaigns/{slug}/supplements/_manifest.json` (campaign)

   Extract the list of supplements with their `slug`, `title`, `kind`, and one-line summary (`summary_text` for flat entries, first sentence of `_summary.md` for wrapped entries — read just enough of `_summary.md` to get the gist).

   If a manifest doesn't exist, fall back to listing top-level `.md` filenames in the directory (legacy mode).
6. Ensure the meta directory exists: `mkdir -p DND-Campaign-Manager/campaigns/{slug}/.meta/` (idempotent — used by the routing/audit/improvement system)

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

Supplements available:
  Global ({n}):
    - {slug} ({kind}) — {one-line summary}
    - ...
  Campaign ({n}):
    - {slug} ({kind}) — {one-line summary}
    - ...

Custom Notes: {custom_notes}
Obsidian Vault: {obsidian_vault if set, otherwise "(none linked)"}

Recent Session: {last 2–3 sentences extracted from session-log.md}
```

If no players yet: show `Party: (none yet — use /add-player)`
If no quests: show `Active Quests: (none recorded)`
If no session log entries: show `Recent Session: (no sessions logged yet)`
If no `obsidian_vault` field in campaign.json: show `Obsidian Vault: (none linked — add "obsidian_vault" to campaign.json to enable)`

### Load table conventions

Read `campaigns/{campaign-slug}/conventions.md` if it exists. It holds how *this* table plays —
rules edition, default session tone, who plays which character, vault visibility — and applies for
the rest of the session. Where it conflicts with the committed `conventions/` files, the campaign
file wins; it is more specific.

Do not print its contents in the briefing. Add one line to the briefing confirming it loaded:

```
Table Conventions: loaded ({n} sections)
```

If the file does not exist, show `Table Conventions: (none — see conventions/README.md to add)`
and carry on. Do not offer to create one unless the user asks.

End the response with this exact block (required — other commands depend on it):

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DND-Campaign-Manager/campaigns/{campaign-slug}/
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

**Check for collision**: if `DND-Campaign-Manager/campaigns/{slug}/` already exists, append `-2`, `-3`, etc.

**Write** `DND-Campaign-Manager/campaigns/{slug}/campaign.json`:
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
- `DND-Campaign-Manager/campaigns/{slug}/players/`
- `DND-Campaign-Manager/campaigns/{slug}/npcs/`
- `DND-Campaign-Manager/campaigns/{slug}/supplements/`
- `DND-Campaign-Manager/campaigns/{slug}/.meta/` (used by the routing/audit/improvement system; safe to leave empty initially)

**Write** `DND-Campaign-Manager/campaigns/{slug}/session-log.md`:
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
Path: DND-Campaign-Manager/campaigns/{campaign-slug}/
```
