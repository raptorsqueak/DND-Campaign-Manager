# /review-session — Finalize a Session After the Fact

The wrap-up sitting. `/end-session` closes the laptop; **this** is what runs days later when the DM
sits down to actually finish the session — Friday's game reviewed on Monday.

Where the session lands in the lifecycle:

| Command | When |
|---|---|
| `/plan-next-session` | days before, to build the plan |
| `/start-session` | the night of, to open PLAY MODE |
| `/end-session` | the night of, to stop and go home |
| **`/review-session`** | **days later, to finalize, sync, and transcribe** |

This command is **not** a hard stop and **is** allowed to ask questions. It orchestrates the
existing commands rather than replacing them — `/session-log`, `/sync-obsidian` and the transcript
scripts all remain usable on their own.

**Assume the conversation has been compacted and the live notes are days old.** Read files; do not
work from memory of the session.

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say:

> "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`. Then confirm PLAY MODE is off — if
`campaigns/{campaign-slug}/.meta/play-mode.flag` exists, say so and ask whether the DM meant
`/end-session` first. Do not delete the flag here.

---

## Step 1: Find What There Is to Review

Collect, in parallel — this is the orchestrator's job, not a subagent's:

1. `campaigns/{campaign-slug}/campaign.json` — `current_session`, `last_session`, location, quests
2. `campaigns/{campaign-slug}/session-log.md` — is there an `IN PROGRESS` block? What session
   number and start date does it carry?
3. **A recording**, if one exists. Check the audio drop directory (`{obsidian_vault}/_audio/` by
   default, or wherever the DM says). Note the filename, duration, and mtime.
4. `campaigns/{campaign-slug}/.transcript-working/` — is there an unconsumed transcript from a
   previous partial run?
5. `campaigns/{campaign-slug}/supplement-state/{book}.md` — what session is it refreshed through?
6. The vault's `Sessions/` note for the session date, if `obsidian_vault` is set.

Report what you found as a short checklist, then work down it. If there is nothing to review — no
IN PROGRESS block, no recording, book state current — say so and stop.

---

## Step 2: Transcribe, If There Is a Recording

Only when Step 1 found audio. Confirm the file and the session date with the DM first, since the
transcript is dated from the recording's mtime by default and a Monday review of a Friday game
must carry **Friday's** date.

```bash
bin/transcribe.sh {audio-file} --campaign {campaign-slug} --date {session-date}
```

- Runs at roughly 8 minutes per hour of audio. Run it in the background and get on with Step 3
  rather than blocking on it.
- It normalizes the audio, regenerates the name glossary from the current roster, transcribes, and
  fuzzy-corrects proper nouns. It **never** touches the source audio.
- Read the correction log it prints. Fuzzy correction is conservative but not perfect; note any
  substitution that looks wrong so you can read around it.
- If `bin/transcribe.sh` reports whisper is not installed, tell the DM and offer
  `bin/install-whisper.sh` — do not install it unprompted.

---

## Step 3: Finalize the Session Log

**The transcript is the better source when one exists.** The live notes are scoreboard fragments
typed mid-play; the transcript has what was actually said and ruled. Where they disagree, the
transcript wins — and say so explicitly in the DM Notes, because a live note that got a ruling
backwards will otherwise be trusted later.

Draft the finalized `## Session {n} — {date}` block in the house format (see the previous session's
block): a prose `### Summary`, then `### Quest Updates`, `### NPC Interactions`, `### Loot & Items`,
`### DM Notes`.

**Show the draft to the DM before replacing the IN PROGRESS block.** Write it to
`campaigns/{campaign-slug}/sessions/{date} Session {n} log draft.md` so it survives review.

With no transcript, fall back to `/session-log`'s interview against the IN PROGRESS block.

### Sweep for what live play leaves half-recorded

Check each of these explicitly and report the result, even when the answer is "nothing":

- **Homebrew or DM rulings** made at the table — these must be registered in a supplement, not
  just the session log. Put a ruling next to the rule it modifies, so the two are read together.
- **NPC renames or status changes** needing propagation across `npcs/`, the vault, and
  `supplement-state/`
- **Loot described but never confirmed taken** — see `conventions/campaign-data.md`; a described
  item is not an acquired item, and being played with is not being carried
- **New items** that must appear in the next `# Before` block
- **Seeds and warnings that were finally spent** — a standing ⚠ note that has now paid off should
  become a "build forward from this" note, not stay a warning

---

## Step 4: Update Campaign State

Once the log block is written:

- `current_session` → the finalized session number
- `last_session` → the session's date
- `current_location` → where the party actually ended up (this drifts during play and the live
  update is often never applied)
- `active_quests` → add and close as the session warrants. Closing a quest is high-stake; confirm.

Apply via `bin/apply-proposal.py` with `set-field` / `array-append` / `array-remove`.

---

## Step 5: Update Book State

Refresh `campaigns/{campaign-slug}/supplement-state/{book}.md`:

- A bullet for the session under the current chapter
- Refresh the "current position" and "still ahead" lines — mark cleared areas
- Register the session's rulings here when the book is where they apply
- Bump the "last refreshed" line

---

## Step 6: Sync the Vault

If `obsidian_vault` is set, run the `/sync-obsidian` flow: players, NPCs, session notes, and the
`{vault}/Campaign/{Book}/_DM State.md` mirror.

- **Never overwrite something the DM wrote during play.** Append the finalized log to the session
  note under its own heading, below the live `# During` block.
- Check the `_DM State.md` mirror for hand edits before overwriting it — it is a pure mirror only
  if nobody has touched it.

---

## Step 7: Discard the Recording

**Only after the log block is actually written**, and as an explicit, reported step.

Delete the transcript, its corrections log, the intermediate WAV, and **the source audio**. A
failed or abandoned review must leave all of them alone — otherwise a bad run loses the session
twice over.

```
✓ transcript and source audio discarded
```

Say plainly that there is no going back: the recording is unfiltered audio of real people talking
for hours, it is not retained, and if the log turns out to be missing something later the source is
gone. That is the intended behavior.

If the DM has an editor open on the transcript, tell them — the file is gone from disk but a write
from their buffer would recreate it.

---

## Step 8: Report and Point Forward

Close with what changed, what is still open, and the one next step:

```
Session {n} finalized.
  session-log.md    finalized block written
  campaign.json     session {n}, {date}, location updated
  {book}.md         chapter progress + {k} ruling(s) registered
  vault             session note + _DM State mirror synced
  recording         discarded

Still open:
  - {anything deliberately left}

Next: /plan-next-session
```
