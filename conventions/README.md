# Conventions

Behavioral rules for the assistant that are **not derivable from the commands and agents alone** —
the accumulated corrections that make this tool behave like a useful DM's assistant rather than a
generic one.

These live in the repo, and they are committed, because they are part of the tool. Clone this
project and you get the commands, the agents, *and* the judgment. Previously most of this sat in
per-project assistant memory on one machine, which meant a fresh clone behaved noticeably worse
than the original and nobody could see why.

## What lives here vs. what lives with the campaign

| | Goes in `conventions/` (committed) | Goes in `campaigns/{slug}/conventions.md` (git-ignored) |
|---|---|---|
| Scope | How the **tool** should behave for anyone | How **this table** plays |
| Examples | Live play gets short bullets; never script a PC; check for NPC name variants before creating a file | Which rules edition this table uses; the default session tone; who plays which character; whether the vault is DM-only |
| Test | Would this still be right for a stranger's campaign? | Would a different group answer this differently? |

If a rule names a specific character, book, campaign, or house rule, it is campaign-level. The
privacy boundary in `CLAUDE.md` applies here with no exceptions: nothing in `conventions/` may
contain a campaign name, a PC name, a homebrew NPC or item, or an absolute path.

## Files

| File | Covers |
|---|---|
| `play-mode.md` | Live play — response length, dice, what may be written down |
| `session-prep.md` | Session plans and notes — the skeleton principle, what never gets scripted, the vault layout |
| `campaign-data.md` | Writing to campaign files — name collisions, factual grounding, supplement shape |
| `authoring.md` | Working on this project itself — privacy, hooks, commits, agent design |

## How they load

`CLAUDE.md` imports these files, so they are in context every session alongside the main
instructions. If you are running this corpus under a harness that does not expand imports, read
`conventions/*.md` at session start — they are part of the system prompt, not reference material.

## Adding to them

When the DM corrects the assistant and the correction generalizes, it belongs in a file here:
state the rule, state why (the correction that produced it), and state how to apply it. Keep the
"why" — a rule without its reason gets argued away six months later.

If the correction is specific to one table, it belongs in that campaign's `conventions.md`
instead. When in doubt, apply the test in the table above.

## Campaign conventions template

`campaigns/{slug}/conventions.md` is optional and free-form. A useful starting shape:

```markdown
# {Campaign Name} — Table Conventions

## Default session tone
{the standing mix — so /plan-next-session can stop asking}

## Rules editions in play
{which edition for feats, subclasses, anything the table has settled}

## Who plays whom
{character → player, including any the DM runs; note that DM-run does not mean scriptable}

## Vault visibility
{is the Obsidian vault DM-only, or do players read it?}

## Anything else this table does differently
```

Keep it short. It is loaded on every `/start-campaign`, and anything that belongs to every table
belongs in the committed files instead.
