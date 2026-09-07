# /end-session — Stop Play, Immediately

**This command is a hard stop. The DM is packing up to leave.**

Do the minimum: turn PLAY MODE off and get out of the way. **Ask nothing. Offer nothing. Formalize nothing.**

---

## Rules

- **No questions.** Do not ask whether to formalize, sync, or save anything.
- **No menus.** Do not present numbered options.
- **No formalization.** Do not rewrite the IN PROGRESS block, do not touch `campaign.json`, do not touch the vault, do not run `/session-log`.
- **No summary of the session.** A one-line pointer is enough.
- Keep the whole response to a few lines. The laptop is closing.

The IN PROGRESS block stays exactly as it is. It is the record, and it will be formalized in a later sitting via `/session-log`.

---

## Step 1: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, say "No active campaign." and stop.

Extract `{campaign-slug}`.

## Step 2: Delete the Play Mode Flag

```bash
rm -f campaigns/{campaign-slug}/.meta/play-mode.flag
```

If the flag did not exist, PLAY MODE was already off — say so in the one-line summary and continue to Step 3 anyway.

## Step 3: Respond

Output exactly this shape and nothing more:

```
=== PLAY MODE OFF ===
Session {n} live notes preserved in session-log.md as an IN PROGRESS block.

To wrap up whenever you're ready (no rush — days later is fine):
  /review-session     finalize the log, sync the vault, transcribe the recording

PLAY MODE: off
Campaign: {campaign-slug}
Ended: {today's date}
```

`{n}` comes from the IN PROGRESS block heading if one exists; otherwise omit that line entirely.

---

## Note for the deferred wrap-up

The wrap-up belongs to **`/review-session`**, which is built for exactly this and runs days later.
When finalizing a session that ended this way, remember the live notes may be **days old** and the conversation may have been compacted. Read the IN PROGRESS block as the source of truth rather than relying on conversation memory, and check whether these were captured during play:

- Homebrew or DM rulings made at the table (register them in the campaign's `party-options` or an appropriate supplement, not only on a character sheet)
- NPC renames or status changes that need propagating across `npcs/`, the vault, and `supplement-state/`
- Loot that was described but never confirmed as taken
- `supplement-state/{book}.md` progress for the chapter that was played
