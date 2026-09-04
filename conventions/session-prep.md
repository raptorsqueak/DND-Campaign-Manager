# Session Prep

Rules for `/plan-next-session`, `/session-log`, and anything that writes a session note.

---

## Never script the players

Describe **what is there, who is there, and what is at stake**. Never write what a PC or a
companion does, feels, says, or notices.

✅ **Do** write:
- The situation — where, when, weather, mood
- NPCs present, their motivations, dispositions, and what they want
- Hooks and offers — *"the knight is willing to bet on an arm-wrestle"*
- What is at stake — encounter stats, loot, plot consequences
- DM-only secrets to seed, and how to seed them subtly
- Branch points and contingencies — *"if they decline, the road takes two extra days"*

❌ **Don't** write:
- *"Lyra will try to talk first"*
- *"Dain absolutely tries to con him"*
- *"Boon tries the temple door and gets bounced"*
- Any companion action, any player reaction, any dialogue from a PC

**Companions get identical protection to PCs.** They are played by people. An earlier version of
this rule wrongly treated them as DM-run NPCs with plannable beats, and produced *"Pip is
miserable and vocal about it"* in a plan. The DM's correction: *"I can't specify that Pip is
miserable and cold, only that it's cold out and the player would need to take the cue."*

**A character the DM plays is still not scriptable.** Notes about them are notes-to-self about
available options, never stage directions.

### The replacement move: write the stimulus, not the response

| Instead of | Write |
|---|---|
| *"Boon shivers"* | *"the fire's heat reaches about three feet; anything small enough to fit inside a coat has an obvious incentive"* |
| *"Lyra will try to free the prisoner"* | *"the prisoner is chained in plain view and visibly mistreated — have your branches ready if it's freed"* |
| *"Dain goes very still near the shrine"* | *"make sure Dain's player has clear line of sight to it; if they play into it, lean in; if not, drop it"* |

**Why:** *"Don't over play the companions and players — the players will do the role play, I just
need the story line and hooks so the players can decide how to play the scene."* A plan that
prescribes reactions robs the table of the discovery and constrains the DM to scenes the players
never chose.

---

## Plans are a skeleton

Capture the skeleton of the story and nothing more — enough structure to navigate confidently at
the table, with all the actual play left to the players. Concretely, what makes a plan land:

- **No act structure when the situation doesn't have one.** If the party has the run of a place,
  write location blocks *ready to run cold in any order* and say so. Use acts only when the
  session genuinely is a sequence.
- **A time cost on every block** (~10 / ~25 / ~35 min), plus a plain statement of what actually
  fits — *"room for one detour plus the audience, not two."* Lets the DM budget live instead of
  discovering the overrun at the ninety-minute mark.
- **Bullets with the numbers bolded inline.** DCs, damage, HP where they are needed. No paragraphs
  to parse mid-play.
- **Reference content lives outside the plan.** Room detail goes in separate pages the plan links
  to, so the plan stays thin and the detail is one click away.
- **Deliberate non-decisions, labelled as such.** When something belongs to the table, say it is
  unresolved on purpose rather than silently omitting it.
- **A short "watch" list** — the few things that would genuinely wreck the session if forgotten:
  hostile triggers, lethal traps, beats not to fire early.

---

## New items land in the next Before block

When a PC gains a notable item — magical, homebrew, a faction reward, anything the player will
want to remember — it must appear as a bullet in the `# Before` block of the next session-prep
notes. The DM uses Before to set the scene, and a new item is part of the mental loadout.

- During `/plan-next-session`, scan the previous session's log for new items (Loot, rewards,
  crafted or fused items) and seed them as one-line bullets: minimal mechanical hook plus flavour
  hook.
- When an item arrives *between* planning runs, drop a `**Carry to next planning session:**
  {item}` line in that session's DM Notes so the next planning pass surfaces it.

---

## A session is a single meetup

A session does not span multiple real-world days. If play covers multiple days, that is multiple
sessions.

- A session marked IN PROGRESS with a start date in the past almost certainly concluded that day
  and was never finalized — confirm before assuming it is live.
- Never carry a session block across calendar days.
- During briefings, derive "last session" from the most recent dated session block, not from the
  IN PROGRESS marker.

---

## Obsidian vault layout

When a campaign has `obsidian_vault` set and the DM accepts the sync prompt, write **both** files
by default — do not ask whether they also want the full plan:

1. **`{vault}/Sessions/{YYYY-MM-DD} {title}.md`** — the at-the-table note. Two sections only:
   `# Before` and `# During`. **No `# After` section** — it never gets filled in, and
   post-session reflection lives in the project's `session-log.md` instead. Put
   `*Full plan: [[{title}]]*` just below `# Before`.

2. **`{vault}/Campaign/{Book}/{Chapter}/{title}.md`** — the full, reusable plan. No date in the
   filename; it is reference material. Put `*Session notes: [[{YYYY-MM-DD} {title}]]*` at the top.

Both files convert PC and NPC names to `[[Name]]` wikilinks, including unresolved ones — they are
navigable in Obsidian either way. Match the vault's existing book and chapter folder names rather
than inventing a scheme. Titles are contextual to session content, not always destination-based;
follow the DM's lead rather than defaulting to *"To {Destination}"*. If a target file already
exists, confirm before overwriting.

### The `# Before` block stays tighter than the plan

The Sessions/ note is a table-side reference, not a condensed plan. The `*Full plan:*` link is the
escape hatch — if the DM needs detail, they click through.

- One line per act, with a time budget
- One line per encounter or scene option: NPC name plus a one-clause hook, no flavour
- One line per player thread: PC name, situation, no detail
- Skip flavour, alternative phrasings, and "if players go off-script" beats — those live in the
  full plan
- DM heads-up: three to five short reminders, no paragraphs

**Why:** a first attempt that captured key beats *with supporting bullets* came back as "still too
verbose." Bullets that fit on a screen, not a condensed plan.
