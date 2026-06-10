# /start-session — Begin a Live Play Session (PLAY MODE on)

Turns on PLAY MODE so freeform messages route automatically to the right agent. `/start-campaign` must have already been run.

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say:

> "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Check Existing Play Mode

If `DND-Campaign-Manager/campaigns/{campaign-slug}/.meta/play-mode.flag` already exists, say:

> "PLAY MODE is already active for {campaign-slug} (started {flag contents})."

Then output the PLAY MODE sentinel (Step 5) and stop — this is a no-op resume.

---

## Step 2: Set the Play Mode Flag

Ensure the meta directory exists, then write the flag file.

```bash
mkdir -p DND-Campaign-Manager/campaigns/{campaign-slug}/.meta
date -u +"%Y-%m-%dT%H:%M:%SZ" > DND-Campaign-Manager/campaigns/{campaign-slug}/.meta/play-mode.flag
```

The flag's existence enables the routing protocol (defined in CLAUDE.md). Its contents are the start timestamp.

---

## Step 3: Build a Brief "Previously On" Recap

Read in parallel:
1. `DND-Campaign-Manager/campaigns/{campaign-slug}/campaign.json` — current_session, party_level, current_location, in_game_date, active_quests
2. The last 60 lines of `DND-Campaign-Manager/campaigns/{campaign-slug}/session-log.md` — pull the most recent finalized `## Session N — {date}` block (NOT an in-progress block)

From the recent session block, extract a 2–3 sentence recap from its `### Summary` section if present, otherwise the first 2–3 bullets.

---

## Step 4: Display the Session Briefing

```
=== PLAY MODE ON ===
Campaign: {name} (Session {current_session + 1})
Party Level: {party_level}
Location: {current_location}
In-Game Date: {in_game_date or "(not tracked)"}

Previously: {2-3 sentence recap, or "(no prior session logged)"}

Active Quests:
  - {quest 1}
  - {quest 2}
  ...

Routing is live. Speak freely — facts about players, NPCs, campaign state, and session events
will be routed automatically. Rules questions will be answered without /ask-dnd. End with /end-session.
```

If active_quests is empty, show `Active Quests: (none recorded)`.

---

## Step 5: Emit the PLAY MODE Sentinel

End the response with this exact block (the routing protocol scans for it):

```
PLAY MODE: on
Campaign: {campaign-slug}
Started: {timestamp from flag}
```

The `ACTIVE CAMPAIGN:` block from /start-campaign remains the source of truth for which campaign is active; this block only tracks play state.
