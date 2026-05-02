# /session-log — Record Session Notes

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load Current State

Read:
- `DNDCampaign/campaigns/{campaign-slug}/campaign.json` (current session number, quests, location, level)
- The last 30 lines of `DNDCampaign/campaigns/{campaign-slug}/session-log.md` (for continuity)

The session being logged is session number `{current_session + 1}` (one beyond what's in campaign.json).

---

## Step 2: Session Recap Interview

Tell the user: "Let's log Session #{current_session + 1}. Answer the following — brief answers are fine. Type 'skip' for anything you want to leave blank."

Ask one at a time:

1. **Real-world date**: "What was the date of this session?"
2. **Location**: "Where did most of this session take place in-game?"
3. **In-game date**: "What is the in-game date at the end of this session? (or 'skip' if not tracking)"
4. **Summary**: "Briefly summarize what happened this session."
5. **Completed quests**: "Were any quests completed? List them, or 'none'."
6. **New quests**: "Were any new quests picked up? List them, or 'none'."
7. **Key NPCs**: "Any significant NPC interactions to note? (encounters, changes, deaths, alliances) — or 'none'."
8. **Loot**: "Any notable loot or key items gained? — or 'none'."
9. **Level up**: "Did the party level up? If yes, what level are they now? If no, type 'no'."
10. **DM notes**: "Any private DM notes to record? (plot threads, player decisions, upcoming hooks, secrets revealed) — or 'skip'."

---

## Step 3: Append Session Log Entry

Append this block to `DNDCampaign/campaigns/{campaign-slug}/session-log.md`:

```markdown

---

## Session {n} — {real-world date}
**In-Game Date**: {in_game_date or "Not tracked"}
**Location**: {location}

### Summary
{summary}

### Quest Updates
- **Completed**: {list or "None"}
- **New**: {list or "None"}

### NPC Interactions
{npc notes or "None noted"}

### Loot & Items
{loot or "None noted"}

### DM Notes
{dm notes or "None"}
```

---

## Step 4: Update campaign.json

Update the following fields in `DNDCampaign/campaigns/{campaign-slug}/campaign.json`:

- `current_session` → increment by 1 (set to {current_session + 1})
- `last_session` → real-world date entered by user (YYYY-MM-DD format)
- `in_game_date` → new in-game date (if provided and not skipped)
- `current_location` → location entered by user
- `active_quests` → remove any completed quests listed, add any new quests listed
- `party_level` → update if user said the party leveled up

---

## Step 5: Optional Player Updates

Ask: "Would you like to update any player character sheets? (current HP, spell slots, inventory, level, notes) — yes or no"

If **yes**:
- List all players in `DNDCampaign/campaigns/{campaign-slug}/players/`
- Ask: "Which player(s) do you want to update? List names or 'all'."
- For each selected player, ask what to update (HP, spell slots, equipment, session notes, level, features gained)
- Apply changes to the relevant `.md` files, updating the `Last Updated` date and `Session Notes` section

If **no**: skip.

---

## Step 6: Confirm

Display:

```
Session {n} logged.
Campaign state updated: Session #{n}, Level {party_level}, Location: {current_location}
Active Quests: {list}
```
