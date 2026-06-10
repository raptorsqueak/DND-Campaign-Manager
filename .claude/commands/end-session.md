# /end-session — Finish a Live Play Session (PLAY MODE off)

Turns off PLAY MODE and offers to formalize the in-progress session log into a proper session entry.

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say:

> "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Check Play Mode Status

Check if `DND-Campaign-Manager/campaigns/{campaign-slug}/.meta/play-mode.flag` exists.

- If **not present**: PLAY MODE was already off. Display:

  > "PLAY MODE is not currently active for {campaign-slug}. Nothing to end."

  Then emit the PLAY MODE OFF sentinel (Step 5) and stop.

- If **present**: read its contents to know the session start time, and continue.

---

## Step 2: Read the In-Progress Session Block

Read the last 80 lines of `DND-Campaign-Manager/campaigns/{campaign-slug}/session-log.md`.

Find a block matching:

```markdown
## Session {n} — IN PROGRESS (started {date})
```

If no in-progress block is found, the session had no logged events. Skip to Step 4 (PLAY MODE off, no formalization needed).

If found, display its `### Live Notes` bullets back to the user:

```
=== Session {n} live notes captured ===
- {bullet 1}
- {bullet 2}
- ...

({count} events logged over {duration})
```

---

## Step 3: Offer to Formalize

Ask:

```
What would you like to do?
  1. Run /session-log now to formalize this session (recommended — converts live notes
     into a proper Session N entry, updates campaign.json, optionally syncs to Obsidian)
  2. Just turn off PLAY MODE — keep the IN PROGRESS block as-is, formalize later
  3. Cancel — leave PLAY MODE on
```

Wait for user input.

- **1** → run `/session-log` (the existing slash command). It will read the in-progress block, walk through the recap interview using the captured bullets as a starting point, replace the IN PROGRESS block with a proper `## Session {n} — {date}` entry, and update campaign.json. After /session-log completes, return here and continue to Step 4.
- **2** → continue to Step 4 immediately.
- **3** → stop. PLAY MODE remains on. Do not delete the flag.

---

## Step 4: Delete the Play Mode Flag

```bash
rm -f DND-Campaign-Manager/campaigns/{campaign-slug}/.meta/play-mode.flag
```

The hook stops injecting routing reminders the moment the flag is gone.

---

## Step 5: Emit the PLAY MODE OFF Sentinel

End the response with this exact block:

```
PLAY MODE: off
Campaign: {campaign-slug}
Ended: {today's date / time}
```

Display a brief summary:

```
=== PLAY MODE OFF ===
Session ended after {duration if available}.
{If formalized: "Session N saved to session-log.md and campaign.json updated."}
{If not formalized: "Live notes preserved as IN PROGRESS block. Run /session-log later to finalize."}

Routing is off. Slash commands still work normally. Run /start-session to resume.
```
