# Live Play

Rules for PLAY MODE — the assistant's behavior while a session is actually running.

---

## Short beats, not narration

Answer live-play prompts with **3–6 short bullets**. Fragments are fine. No scene-setting
paragraphs, no atmospheric prose, no boxed text.

- One line per beat: a sensory detail, an NPC line, a mechanical note, an available hook.
- NPC dialogue is welcome as a single quoted line, never a speech.
- Close with a one-line pointer to what is available next, not a paragraph explaining it.

**Why:** at the table the DM narrates. A long passage is something they have to read and compress
in real time while the players wait. The correction that produced this rule was blunt — *"dude,
not so much story telling. Just little bits"* — after a request for "the party makes a fire for
tea" came back as two hundred words about wind and starlight.

Prep documents are where detail belongs. This rule applies during play only; `/plan-next-session`
output and reference docs keep their normal depth.

---

## The DM rolls the dice

When a mechanic calls for a roll — a fusion table, an attack, a save, a random encounter — **do
not roll it.** No `$RANDOM`, no invented number, no "let's say it comes up 14."

Stage the inputs, say what is pending, and stop:

> Fusion #7 — inputs: rope, lantern oil, a pebble. Awaiting your d20.

Resolve only after the DM supplies the number.

**Why:** the DM rolls real dice at the table and wants the real result driving outcomes.

---

## Improvised detail is a suggestion, not a fact

Colour the assistant invents during play — a motive, a line of dialogue, a mannerism — is
**offered to the DM**, not something that happened. Do not write it into `npcs/*.md`,
`session-log.md`, or the vault as established fact unless the DM actually used it at the table.

- Record what the DM stated. Improvised colour goes into the session plan under an explicitly
  optional heading, or into DM Notes marked as unplayed.
- If invented detail is load-bearing enough to want in a file, say so and get a yes first.
- When the DM asks where a detail came from, **check the transcript** and answer with a clear
  split of what they supplied versus what was generated. Do not answer from memory or summary.

**Why:** the DM once named an NPC and nothing else; the assistant invented a motive and a repeated
line of dialogue around it and wrote all of it into the NPC file, the session log, and two vault
files as canon. Weeks later the DM asked *"did I tell you that or did you make it up?"* The
problem was not the invention — that was useful — it was that a motive-assigning line silently
became campaign history, and later planning would have built on it.

Same root as the no-scripting rule in `session-prep.md`: do not decide things that belong to the
people at the table.

---

## `/end-session` is a hard stop

When the DM types `/end-session` they are closing the laptop and leaving. They are **not** asking
for a wrap-up.

- Delete the play-mode flag, print a few lines, stop. No questions, no menus, no summary, no
  `campaign.json` or vault writes.
- Leave the IN PROGRESS block in `session-log.md` untouched — it is the record.
- Formalization happens in a **separate, later sitting**, often days later, via **`/review-session`**
  — the command built for exactly this, which orchestrates the rest. The DM will ask for it directly.

In that later sitting, treat the transcript as the source of truth when a recording was made, and
the IN PROGRESS block otherwise — the conversation may have been compacted and the notes may be
days old. Where a transcript and a live note disagree, the transcript wins, and say so: a live note
that recorded a ruling backwards will otherwise be trusted later. Sweep for what live play leaves
half-recorded: homebrew rulings that need registering in a supplement rather than only on a sheet,
NPC renames needing propagation, loot described but never confirmed taken, and chapter progress in
`supplement-state/{book}.md`.
