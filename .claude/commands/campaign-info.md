# /campaign-info — View or Update Campaign Metadata

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load and Display Current Info

Read:
- `DNDCampaign/campaigns/{campaign-slug}/campaign.json`
- List all files in `DNDCampaign/campaigns/{campaign-slug}/players/` — for each, extract character name, race, class, level from the file header
- List all files in `DNDCampaign/campaigns/{campaign-slug}/npcs/` — count by Type field (Major NPC / Minor NPC / Recurring / One-Shot)
- List filenames in `DNDCampaign/supplements/`
- List filenames in `DNDCampaign/campaigns/{campaign-slug}/supplements/`

Display:

```
=== CAMPAIGN INFO ===
Name: {name}
Book: {book}
Setting: {setting}
System: D&D 5e
Created: {created}
Last Session: {last_session}
Session: #{current_session}
Party Level: {party_level}
Current Location: {current_location or "(not set)"}
In-Game Date: {in_game_date or "(not set)"}

Party ({count} players):
  - {character name} — {race} {class} Lv{level}
  - ...
  (or "(no players yet — use /add-player)")

NPCs on file: {total} ({major} major, {minor} minor, {recurring} recurring, {one-shot} one-shot)

Active Quests:
  - {quest}
  (or "(none recorded)")

Custom Notes:
  {custom_notes or "(none)"}

Global Supplements:
  {list filenames or "(none — drop .md files into DNDCampaign/supplements/)"}

Campaign Supplements:
  {list filenames or "(none — drop .md files into DNDCampaign/campaigns/{slug}/supplements/)"}
```

---

## Step 2: Offer Updates

Ask:

```
Would you like to update anything?
  1. Current location
  2. In-game date
  3. Party level
  4. Add a quest
  5. Remove a quest
  6. Edit custom notes
  7. Change book or setting
  8. Nothing — just viewing
```

Wait for user input.

---

## Step 3: Apply Updates

Based on selection, ask for the new value and write the updated field back to `campaign.json`.

- **1 — Location**: Ask "What is the current location?" → update `current_location`
- **2 — In-game date**: Ask "What is the in-game date?" → update `in_game_date`
- **3 — Party level**: Ask "What level is the party now?" → update `party_level`
- **4 — Add quest**: Ask "Describe the new quest." → append to `active_quests` array
- **5 — Remove quest**: Show numbered list of current quests → ask which to remove → remove from array
- **6 — Custom notes**: Ask "Enter updated notes (this will replace existing notes)." → update `custom_notes`
- **7 — Book/setting**: Ask "New book?" then "New setting?" → update `book` and `setting`
- **8** — Display: "No changes made."

After each update: "Updated: {field} → {new value}"

Then ask: "Anything else to update? (Enter a number or 'done')"

Repeat until the user says "done" or selects option 8.

**Note**: If the user wants to rename the campaign, warn them: "Renaming only updates the display name — the slug and folder path do not change." Then update `name` in campaign.json only.
