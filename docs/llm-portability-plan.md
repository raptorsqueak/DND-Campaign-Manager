# LLM Portability Plan

**Goal:** run this campaign manager on any capable model (GPT, Gemini, a local model) instead of
only inside Claude Code, without forking the prompt corpus.

**Status:** Phase 0 complete. Phases 1–6 not started.

**How to use this document:** it is written as a work order. Hand a phase back to the assistant
verbatim — e.g. *"Do Phase 1 of docs/llm-portability-plan.md"* — and it should have everything it
needs without re-deriving the survey below. Phases are sequential; each is unusable until the one
above it exists. Do not start Phase 5 before Phase 4.

---

## The finding this plan rests on

A survey of the repo established:

- The application is **~5,200 lines of markdown and zero lines of code** — 17 slash commands, 7
  agents, `CLAUDE.md`, `README.md`.
- The prompt corpus contains **zero references** to any model or vendor. Nothing in the content is
  provider-locked.
- What *is* locked is the runtime the harness supplies: the tools, subagent dispatch, the interview
  loop, the approval prompt, and the conversation transcript acting as the state store.

So this is not a prompt-rewriting project. It is a runtime-building project, plus a decomposition
pass on the four longest commands.

**Estimate:** 2–4 weeks to parity for one developer, plus ongoing per-model tuning.

---

## Non-negotiables

Carry these through every phase.

1. **One prompt corpus.** Never fork the commands or agents into a "Claude version" and an "other
   version". `.claude/` becomes a shim pointing at `prompts/`; both runtimes read the same files.
2. **The privacy boundary does not move.** Everything in `CLAUDE.md` → *Data Sensitivity & Privacy*
   still applies. `campaigns/*` and `.claude/.meta/` stay git-ignored; no campaign name, PC name,
   homebrew NPC, or absolute path enters a committed file — including any new runtime code, test
   fixture, or eval transcript.
3. **The model is configuration.** No module above `runtime/providers.py` knows which model it got.
   No provider name in a command, an agent, or a convention file.
4. **Working state stays where it is.** Campaign data keeps its current on-disk layout. The port
   changes how files are *reached*, never their schema — an existing campaign folder must work
   under the new runtime with no migration.
5. **The DM's dice are the DM's.** Nothing in the runtime generates a die roll. (See
   `conventions/play-mode.md`.)

---

## Phase 0 — Provider-agnostic prep *(complete)*

Work worth doing whether or not the port ever happens. Both items removed a dependency on one
model's particular strengths.

| Item | What changed |
|---|---|
| Section-addressed edits | The proposal contract no longer carries `old_string`/`new_string`. Proposals address a heading or a line prefix; `bin/apply-proposal.py` resolves the bytes deterministically. See `docs/proposal-contract.md`. |
| Committed conventions | Tool-level behavior that lived in per-project memory now lives in `conventions/`, loaded via `CLAUDE.md`. Campaign-specific behavior moved to `campaigns/{slug}/conventions.md`. |

---

## Phase 1 — Spike before you build

**Budget: 1 hour. Do not skip this.**

Point the existing harness at a translating proxy (LiteLLM or equivalent) via `ANTHROPIC_BASE_URL`
and run a real session against GPT. No code changes. This is unsupported and somewhat janky; that
is fine, because it answers the only question that matters before a rewrite: *how badly do these
prompts degrade on another model?*

Exercise, in this order:

1. `/ask-dnd` — cheap, read-only, tests manifest-first loading.
2. `/plan-next-session` — tests a long procedural prompt and broad context assembly.
3. A play-mode turn with a routable fact — tests subagent dispatch and the edit contract.
4. `/sync-obsidian` — the 468-line worst case.

**Deliverable:** `docs/spike-findings.md` recording, per command, whether it completed, what it got
wrong, and whether the failure was *instruction-following* (prompt too long / too conditional) or
*capability* (couldn't do the task at all). Instruction-following failures are Phase 5 work.
Capability failures mean choosing a stronger model, not restructuring.

Only proceed if the findings justify it. A clean spike means the cheap route may be good enough.

---

## Phase 2 — Runtime skeleton

**Budget: 1–2 days.** Build the smallest thing that runs one command end to end.

```
runtime/
  providers.py   # model resolution; one function returning a chat client
  tools.py       # read, write, edit, glob, grep, bash
  loader.py      # parse prompts/**/*.md, split frontmatter, resolve arguments
  session.py     # SessionState (see below)
  cli.py         # entry point
```

**`SessionState`** replaces the transcript-sentinel scan. Fields, minimum:
`campaign_slug`, `campaign_path`, `play_mode: bool`, `session_number`, `turn_history`.
`/start-campaign` sets it; every other command reads it. The `ACTIVE CAMPAIGN:` block becomes a
*display* convention, not a storage mechanism.

**Tools:** scope them to the repo root plus the campaign's configured vault path. `bash` is the one
that needs a real allowlist — the commands use it for `ls`, `date`, `mkdir`, and appending JSONL.

**Definition of done:** `/campaign-info` (99 lines, read-mostly, no subagents) runs against a real
campaign folder under both a Claude model and a non-Claude model, producing equivalent output.

---

## Phase 3 — The agent layer

**Budget: 2–3 days.** The easiest phase: the proposal contract is already a strict schema, so it
maps directly onto structured outputs / function calling.

1. Load `prompts/agents/*.md`, honoring the `tools:` frontmatter as a per-agent allowlist.
2. Express the proposal contract from `docs/proposal-contract.md` as a JSON schema and enforce it
   at the provider boundary — do not parse a JSON block out of prose. This is a meaningful
   reliability upgrade over the current arrangement.
3. Wire `bin/apply-proposal.py` in as the applier. It already exists and is provider-independent.
4. Port the write policy: `stake_level: low` applies immediately, `high` batches for approval.

**Definition of done:** all seven agents callable; a low-stake player fact routes, proposes, and
applies correctly on a non-Claude model.

---

## Phase 4 — State and human-in-the-loop

**Budget: 3–5 days.** The interview loop is the part that is genuinely annoying to hand-roll.

- **Interviews.** Commands like `/add-player` and `/party-options` ask questions and resume. Use
  LangGraph `interrupt()` plus a checkpointer, or an equivalent suspend/resume mechanism. Do not
  fake it by replaying the whole conversation each turn.
- **The approval gate.** One node between propose and apply. It renders the batched confirmation
  and handles `y` / `n` / `review`.
- **The play-mode graph.** This is the one part of the system that is genuinely graph-shaped, and it
  maps onto LangGraph almost one to one:

  ```
  classify → dispatch (parallel fan-out) → aggregate
           → approve → apply → verify (high-stake only)
           → capture-rejection
  ```

  Source of truth for the semantics: `CLAUDE.md` → *Routing protocol*, Steps A–I. Port it as-is;
  do not redesign it during the port.

**Do not** force the 17 commands into a graph. Most are linear interviews and read better as
straight-line code.

**Definition of done:** a play-mode turn containing both a player fact and a rules question fans out
to two agents in parallel, applies one edit, answers the question, and survives a process restart
mid-interview.

---

## Phase 5 — The command layer

**Budget: 1–2 weeks.** The bulk of the work, and where the spike findings get spent.

Most commands port by copying the file and pointing the loader at it. Four do not — they are long
conditional procedures that currently succeed because one model follows a markdown flowchart well:

| Command | Lines | Why it needs decomposing |
|---|---|---|
| `/sync-obsidian` | 468 | Many independent sync steps, each with its own confirm-before-overwrite rule |
| `/add-content` | 364 | Branching intake (flat vs. wrapped), chapter splitting, generated summary + index |
| `/review-improvements` | 295 | Per-candidate interactive walk with four outcomes |
| `/plan-next-session` | 256 | Broad context assembly, then structured generation |

Decompose each into one model call per step with the branching in Python. The prompt file stays the
spec; the runtime executes it stepwise instead of handing over all 468 lines at once.

Also in this phase: **make manifest-first loading deterministic.** Today the model reads summaries
and decides what to open. Move that decision into code — keyword match over the manifest, then load
the selected files. Cheaper, more reliable, and no longer a per-turn prompt-adherence bet.

**Definition of done:** all 17 commands run under the new runtime; the four above run as multi-step
graphs; `/audit` passes on a real campaign.

---

## Phase 6 — Evaluation

**Budget: ongoing.** Without this, "does it still work on model X" is something you find out at the
table on a Friday night.

Build a golden-transcript suite: a fixture campaign (fully generic — placeholder cast per
`CLAUDE.md`), a set of input turns, and asserted outcomes. Assert on **applied file changes and
routing decisions**, not on prose. Run it per provider; a model swap is a config change plus a
test run.

Minimum coverage: one routing turn per agent, one interview command, one high-stake approval, one
rejection-capture path, and `/audit` clean.

---

## Open questions

Decide these when you reach them; do not pre-commit.

1. **UI.** There is a `.venv` provisioned with `textual` and a reference to a `bin/dnd-tui` that
   was never built. Terminal UI, web, or headless-plus-existing-editor?
2. **Does Claude Code remain the primary front end** with the Python runtime as an alternative, or
   does the runtime become primary? Affects how much the `.claude/` shim has to carry.
3. **Session transcription** (see the design note in `.claude/.meta/`) — build it inside the new
   runtime rather than as a Claude Code command, if the runtime lands first.
