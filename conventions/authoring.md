# Working on This Project

Rules for editing the tool itself — commands, agents, docs, and configuration.

---

## Privacy

`CLAUDE.md` → *Data Sensitivity & Privacy* is the authoritative rule and is loaded every session.
The short version: nothing outside `campaigns/*` and `.claude/.meta/` may contain a campaign name
or slug, a PC or companion name, a homebrew NPC or item, or an absolute filesystem path.

Two habits that make compliance automatic:

- **Read specifics at runtime.** A command that needs campaign detail reads it from
  `campaigns/{slug}/` when it runs. It never bakes it into the committed file. The data agents
  already work this way.
- **Use the placeholder cast** in every example: campaign slug `example-campaign`; PCs Lyra
  (bard), Mira, Dain, Kael; companions Boon, Pip; pet Whiskers; homebrew NPCs Vexa Duvyr, Garrick
  Hale, Captain Roenor. Replace the display name *and* the derived filename — `lyra.md`, never a
  real PC's slug.

Published reference material is **not** private and needs no scrubbing: SRD, PHB, and published
adventure content — place names, published NPCs, book titles, class and subclass options.

Before finishing any edit to a committed file, scan your own output for the private items above.

---

## Keep the README generic

The README is a starter doc for someone standing up a fresh copy, not a description of one
populated campaign. No campaign-specific examples, no NPC location-mapping tables, no per-book
operational walkthroughs.

For structure sections, list only the folders a new user must create: `campaigns/{slug}` with
`players/`, `npcs/`, `sessions/`, and `supplements/`. Runtime directories that get created
automatically — `.meta/`, `supplement-state/`, flag files — are not setup steps.

Detailed operational instruction belongs in `CLAUDE.md` and `conventions/`.

---

## No blocking hooks

Do not install hooks in `.claude/settings.json` unless explicitly asked. If one is requested,
verify exhaustively that it exits 0 on **every** code path before suggesting it — and test both
branches.

**Why:** a `UserPromptSubmit` hook of the form `ls …flag >/dev/null 2>&1 && echo "…"` exited
non-zero whenever the flag file was absent, which was the common case. Every prompt came back
"operation blocked by hook" and the project became unusable until the settings file was moved
aside.

PLAY MODE routing does not need a hook. It works from the in-conversation `PLAY MODE: on` sentinel
emitted by `/start-session`; the hook was only a convenience for re-injecting the reminder each
turn.

---

## Don't commit

Do not run `git add`, `git commit`, or anything else that creates a commit unless asked in the
current turn. Read-only inspection (`git status`, `git diff`, `git log`) is fine.

When finishing a unit of work, summarize what changed and what is next — do not offer to commit.
Approval to commit in an earlier turn is not standing authorization.

---

## Agent design: separate collection from judgment

When building a command-and-agent pair, split investigation from judgment:

- **The orchestrator** (the slash command, in the main session) does the data collection — globs,
  reads, greps, manifest parses. It has deterministic tool execution and the user's context.
- **The subagent** receives the collected findings as structured JSON in its prompt. Its job
  narrows to: judge each finding, cluster, draft concrete records, return JSON.

Agent prompts should describe a contract — *"you receive this shape, return that shape"* — not
*"go find context."* Subagents may use Read/Glob/Grep, but reserve those for narrow verification
(fetching the exact lines it is about to quote), never for exploration.

**Why:** the `improvement-curator` was first written as "go read these N sources and produce
findings." Across three rounds of increasingly emphatic MUST/MANDATORY language it kept
short-circuiting on the first small source it read, declaring insufficient signal, and returning
empty — ignoring the other sources it had been told to check. Subagents satisfice on broad
investigation and no amount of prompt sharpening reliably fixes it. The hybrid — orchestrator
scans, agent judges — worked first try, with the same model and the same compute.

---

## Where new rules go

A correction that generalizes to any table goes in `conventions/`. A correction specific to one
table goes in that campaign's `campaigns/{slug}/conventions.md`. Keep the reason alongside the
rule; a rule without its reason gets argued away later.
