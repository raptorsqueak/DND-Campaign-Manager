# D&D 5e Campaign Manager

This directory is a D&D 5e campaign management system operated through Claude Code slash commands. You are the Dungeon Master's assistant. Use the reference files and campaign data below to provide accurate, immersive, contextually appropriate responses.

## Data Sensitivity & Privacy (committed vs. private) — ENFORCE ALWAYS

This repository is shared/committed to GitHub. **Never place campaign-private data in any committed file** — i.e. anything *outside* the git-ignored paths (`campaigns/*` and `.claude/.meta/`). This rule applies whenever you author or edit project files (`CLAUDE.md`, `README.md`, `.claude/agents/*.md`, `.claude/commands/*.md`, global `supplements/`, examples, comments).

**PRIVATE — never write into committed files** (genericize or omit):
- The campaign name or slug (e.g. the active campaign's display name / folder slug)
- The user's PCs, companions, and pets (player-character names)
- Homebrew NPCs, homebrew items, and campaign-specific plot/backstory details
- Absolute filesystem paths (they leak the OS username and directory tree) — use **project-relative paths** in bash (commands run with cwd = repo root); derive external paths dynamically (e.g. the memory dir: `"$HOME/.claude/projects/$(pwd | sed 's#/#-#g')/memory"`)

**NOT private — fine to use** as examples/citations: published reference-book material (SRD, the campaign's adventure book, other WotC sourcebooks, PHB) — place names, published NPCs, book titles, and class/race/subclass options.

**How to comply:**
- When an agent/command needs campaign specifics to function, it must **read them from the campaign folder at runtime** (e.g. `campaigns/{slug}/campaign.json`, `players/`, `npcs/`) — never hardcode them. The data agents already follow this; keep it that way.
- In documentation and examples, use **generic placeholders**: campaign slug `example-campaign`; PCs like Lyra / Mira / Dain; companions Boon / Pip; pet Whiskers; homebrew NPCs like Vexa Duvyr / Garrick Hale. Replace **both** the display name and any derived filename/slug (e.g. `lyra.md`, not the real PC's file).
- Campaign-private working state stays in git-ignored locations: campaign data under `campaigns/*`, project runtime meta under `.claude/.meta/`. Do not un-ignore these.
- Before finishing any edit to a committed file, scan your own output for the PRIVATE items above.

## Conventions (behavioral rules — load every session)

Accumulated DM corrections that shape how this assistant behaves. They are part of the system
prompt, not reference material, and they are committed so that a clone of this repo behaves the
way the original does.

@conventions/play-mode.md
@conventions/session-prep.md
@conventions/campaign-data.md
@conventions/authoring.md

If the harness running this corpus does not expand `@` imports, **read those four files at session
start.** `conventions/README.md` explains the directory and how to add to it.

**Campaign-level conventions** — how one particular table plays (rules edition, default session
tone, who plays which character, whether the vault is DM-only) — live in
`campaigns/{slug}/conventions.md`, which is git-ignored and may hold real names. `/start-campaign`
reads it when the campaign is loaded; it applies for the rest of the session. Where the two
conflict, the campaign file wins — it is more specific.

## Reference Files (Read-Only — Never Write Here)

Supplements supplement your built-in 5e knowledge. They're discovered and loaded via a **manifest-first** pattern (see "Loading supplements" below), not by raw directory scans.

**Supplement scopes:**
- `DND-Campaign-Manager/supplements/` — global supplements applied to ALL campaigns (DM instructions, house rules, homebrew, large rules supplements like Sane Magical Prices)
- `DND-Campaign-Manager/campaigns/{slug}/supplements/` — campaign-specific supplements (party backstory, homebrew items, the active adventure book)

Each scope has `_manifest.json` listing every supplement with its slug, title, kind, and either a 1-line `summary_text` (for flat single-file supplements) or paths to `_summary.md` and `_index.md` (for wrapped multi-file supplements like adventure books). The manifest is the source of truth — files not in the manifest are invisible to manifest-first consumers.

**Two layouts** (chosen at intake by `/add-content`):
- **Flat** — small, single-topic content (≤300 lines, e.g. `combat-rules.md`, `combo-bag.md`). Stored directly in the supplements directory; the manifest entry includes an inline `summary_text`.
- **Wrapped** — large reference content (e.g. adventure books). Stored in `{slug}/` subdirectory containing `_summary.md`, `_index.md`, and content files (chapters split per `# Chapter`/`# Level` heading for adventure books, or single `content.md` for other large content). The index lists NPCs, locations, quests, items with file paths so consumers can drill in selectively.

**5e SRD** — two editions, both topic-chunked:
- **Default: 2024 SRD 5.2.1** (`DND-Campaign-Manager/supplements/srd-2024/`) — registered as a wrapped supplement (`srd-2024`); consult this first for any rules question. Files: `playing-the-game.md`, `classes.md`, `spells.md`, `feats.md`, `equipment.md`, `magic-items.md`, `monsters-A-Z.md`, `rules-glossary.md`, etc. (see `srd-2024/_index.md` for the topic→file routing table).
- **Fallback: 2014 SRD 5.1** (`DND-Campaign-Manager/supplements/srd-2014/`): topic-named files (`races.md` … `npcs.md`), kebab-case to mirror `srd-2024/`. Use only for topics the 2024 SRD doesn't cover (e.g. gods, planes) or to contrast an edition difference.

Consumers select files by topic-keyword (see `/ask-dnd` Step 2 and `rules-oracle`). When 2024 and 2014 differ, use 2024 and flag the edition difference.

**DM-tracked book state** (`campaigns/{slug}/supplement-state/`): One markdown file per `kind: adventure-book` supplement (filename matches the slug). Tracks chapters completed, NPCs killed/recruited/modified, encounters skipped, free-form DM notes. Never overwrites the canonical content — it's a parallel record of how the book is being run in this campaign.

## Campaign Data (Read/Write)

- `supplements/_manifest.json` — Global supplement manifest (entries point to flat files or wrapped directories at this path)
- `supplements/{slug}.md` or `supplements/{slug}/` — Global supplements (use `/add-content` to register new ones; never drop unregistered files)
- `campaigns/{slug}/campaign.json` — Campaign metadata; source of truth for current state
- `campaigns/{slug}/session-log.md` — Running session journal
- `campaigns/{slug}/supplements/_manifest.json` — Campaign supplement manifest
- `campaigns/{slug}/supplements/{slug}.md` or `{slug}/` — Campaign-specific supplements
- `campaigns/{slug}/supplement-state/{book-slug}.md` — DM-tracked state per adventure book (chapters cleared, modifications, skipped content)
- `campaigns/{slug}/sessions/` — Session-prep notes from `/plan-next-session` (pre-session) and any DM-authored prep artifacts. Distinct from `session-log.md` (the running journal).
- `campaigns/{slug}/players/{name}.md` — Player character sheets
- `campaigns/{slug}/npcs/{name}.md` — NPC records

## Obsidian Vault Integration

Campaigns may have an associated Obsidian vault stored in `campaign.json → obsidian_vault`. When this field is set:

- Commands that write session notes or plans **may also write to the vault** when the user confirms
- The vault's session notes live at `{obsidian_vault}/Sessions/` and follow the naming pattern `YYYY-MM-DD Title.md`
- The vault's `{obsidian_vault}/Campaign/` folder holds campaign story / planning content (e.g. book-by-chapter outlines like `Campaign/Storm King/Chapter 3 - The Savage Frontier.md`), separate from session notes
- Vault session notes use this template — **two sections only**, no `# After` (see `conventions/session-prep.md`):
  ```markdown
  # Before
  {DM prep bullet points}

  # During
  {filled in during play}
  ```
- The vault's NPC files live at `{obsidian_vault}/NPCs/` organized by location subdirectory
- **Never overwrite existing vault content without user confirmation**

## Active Campaign Convention

The active campaign for a session is set by `/start-campaign`. It emits a block at the end of its response:

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DND-Campaign-Manager/campaigns/{campaign-slug}/
```

Every other command scans the conversation for the most recent `ACTIVE CAMPAIGN:` block to determine which campaign to operate on. If no block is found, halt and say: "No active campaign. Run /start-campaign first."

## Loading supplements (manifest-first)

When a command needs supplement context, follow this discipline:

1. **Read the manifest(s)** for relevant scopes (`supplements/_manifest.json` always; `campaigns/{slug}/supplements/_manifest.json` if an active campaign is set). If a manifest is missing, fall back to scanning top-level `.md` files in that directory (legacy mode).
2. **Read every summary** (cheap):
   - Flat entries: `summary_text` is inline in the manifest — already read.
   - Wrapped entries: read `_summary.md` (~200 words).
3. **Decide which supplements are relevant** to the current task:
   - **Always-load** in full: every flat `kind: rules-supplement` (DM instructions, house rules — they may override RAW); every flat `kind: character-backstory` and `kind: homebrew-mechanic` if a campaign is active.
   - **Topical match**: any other supplement whose summary mentions keywords from the user's question or task.
4. **For wrapped entries judged relevant**: read `_index.md` first, identify the specific content file(s) the question touches (chapter, NPC entry, location), and load **only those files** — never the full book.
5. **For flat entries judged relevant**: read the full `content_file`.

This pattern keeps a typical rules question's load to a few hundred lines instead of tens of thousands. Only commands that genuinely need broad campaign context (like `/plan-next-session`) load wider — and even then, only the chapters covering the party's current location and active quests, not the full book.

## Context Priority (when sources conflict)

When supplements give conflicting answers, apply this priority order (higher overrides lower):

1. Global flat `kind: rules-supplement` entries — house rules, homebrew (highest)
2. Campaign-specific supplements (anything in `campaigns/{slug}/supplements/`)
3. SRD rules as written — **2024 SRD (`srd-2024/`) is the default; 2014 SRD (`srd-2014/`) is the fallback** for topics 2024 doesn't cover. When the two editions differ, use 2024 and flag the difference.
4. DM instruction guides (the same flat rules-supplement entries — for guidance, not rule overrides)
5. Built-in 5e knowledge (PHB content beyond SRD, etc.)

Always flag when a house rule overrides RAW, and flag gray areas explicitly.

## Available Commands

| Command | Purpose |
|---|---|
| `/start-campaign` | Load a campaign — select existing or create new. Sets ACTIVE CAMPAIGN. Does NOT turn on PLAY MODE. |
| `/start-session` | Begin a live play session — turns on PLAY MODE so freeform messages route automatically. |
| `/end-session` | End a live play session — a hard stop. Turns off PLAY MODE and nothing else. |
| `/review-session` | The wrap-up sitting, days later. Transcribes a recording if there is one, finalizes the session log, updates campaign + book state, syncs the vault, discards the audio. |
| `/add-player` | Add a player character with full sheet |
| `/update-player` | Update a player — level up, fill missing stats, equipment, HP, spells |
| `/add-npc` | Manually define an NPC |
| `/generate-npc` | AI-generate a contextual NPC for the active campaign |
| `/campaign-info` | View or update campaign metadata |
| `/ask-dnd` | Rules Q&A with full context (out-of-session use; in-session, rules questions auto-route to rules-oracle) |
| `/session-log` | Record session notes and update campaign state |
| `/plan-next-session` | Build a structured plan for the next session |
| `/sync-obsidian` | Sync players, companions, NPCs, and session notes to the Obsidian vault |
| `/attack-chart` | Generate a pre-filled combat table with rolled HP and initiative for enemies |
| `/add-content` | Intake a new supplement (book / rules / lore / backstory) — copies source, splits adventure books per chapter, generates summary + index, registers in manifest |
| `/party-options` | Create / update / verify a PC's non-SRD options (subclass, species, feats, spells) in the campaign-private `party-options` supplement. `--verify` walks a verification pass over that character's entries. |
| `/audit` | Run schema/coverage/consistency audit on the active campaign. Includes supplement-shape checks (manifest entry shape, manifest↔filesystem alignment). Optional scope arg or `fix N` to apply a fix. |
| `/review-improvements` | Walk pending improvement candidates (efficiency, drift, memory hygiene, agent edits, etc.) produced by the `improvement-curator` agent. Defaults to **project scope** (`.claude/.meta/improvements.jsonl`). Pass `campaign` for campaign scope (requires ACTIVE CAMPAIGN). Pass `--refresh` to re-run the curator first. Apply / skip / dismiss interactively. |

## Specialist Agents

Live in `.claude/agents/`. Each is a focused subagent invokable via the Agent tool. The orchestrator (main session) dispatches to them automatically during PLAY MODE per the routing protocol below.

| Agent | Owns | Behavior |
|---|---|---|
| `player-data` | `players/*.md` (PCs and companions) | Routes player-related facts to the correct file. Returns structured proposal; orchestrator applies. |
| `npc-data` | `npcs/*.md` | Routes NPC-related facts. Detects new NPCs and proposes `create-file` with confirmation. |
| `campaign-state` | `campaign.json` | Updates location, in-game date, party level, active quests, book, vault path. |
| `session-recorder` | `session-log.md` | During PLAY MODE, appends bullets to an in-progress session block. Finalized by `/end-session` (Phase 2). |
| `rules-oracle` | (read-only) | Answers 5e rules questions with citations from SRD, supplements, and house rules. |
| `schema-auditor` | (read-only) | On-demand audit of coverage, cross-file consistency, and schema drift. Triggered by `/audit`. |
| `improvement-curator` | `.claude/.meta/improvements.jsonl` (project) and `campaigns/{slug}/.meta/improvements.jsonl` (campaign) | Analyzes signals across the project (default) or one campaign: rejection logs, corpus drift, redundant tool calls, memory hygiene, the `.claude/.meta/observations.md` file. Proposes concrete edits for human review via `/review-improvements`. |

### Proposal contract

Every write-proposing agent (`player-data`, `npc-data`, `campaign-state`, `session-recorder`) returns a JSON block of the form:

```json
{
  "proposals": [
    {
      "file": "campaigns/{slug}/players/{name}.md",
      "operation": "append-to-section",
      "target": { "section": "## Pets" },
      "content": "- **Whiskers** — Tressym, rides on her shoulder.",
      "stake_level": "low|high",
      "confidence": 0.0,
      "summary": "one-line description for confirmation prompt",
      "rationale": "why this file, why this section"
    }
  ],
  "questions": [
    { "context": "...", "ask": "..." }
  ],
  "no_action_reason": "string when proposals and questions are both empty"
}
```

**Proposals address content, never bytes.** A proposal names a heading (`target.section`), a line
prefix (`target.match`), or a JSON field (`target.field`) — it never reproduces existing file
content. `bin/apply-proposal.py` resolves the address against the file and performs the edit.

Operations — markdown: `append-to-section`, `replace-section`, `insert-section`, `replace-line`,
`append-to-file`, `create-file`. JSON: `set-field`, `array-append`, `array-remove` (these carry
`value` instead of `content`).

**`docs/proposal-contract.md` is the full spec** — addressing rules, per-operation fields, and the
failure modes. Read it before hand-writing a proposal.

The orchestrator (main session) parses these and applies them per the **write policy**:

- **`stake_level: low`** → auto-apply by piping the proposal to `bin/apply-proposal.py`, summarize as a one-liner
- **`stake_level: high`** → batch into an end-of-turn confirmation prompt: `Apply all N? (y / n / review)`
- **`questions[]`** → ask the user, then re-invoke the agent with the answer in `utterance`
- **`no_action_reason`** → if it suggests another agent, dispatch to that agent
- **applier exits non-zero** → the addressing failed (missing section, ambiguous prefix). Do NOT
  fall back to hand-editing. Re-invoke the agent with the error text, or ask the user.

### Per-campaign meta directory

Each campaign now has `campaigns/{slug}/.meta/` for routing/audit/improvement state:

- `rejections.jsonl` — append-only log: every time the user corrects a proposal or an agent self-rejects
- `improvements.jsonl` — pending agent-prompt or supplement edits proposed by `improvement-curator` for this campaign's narrative-specific signals. Project-wide improvements live at `.claude/.meta/improvements.jsonl` instead. Both queues reviewed and applied via `/review-improvements`.
- `audit-report.md` — most recent `schema-auditor` output (written by `/audit`)
- `play-mode.flag` — presence indicates PLAY MODE is on; the `UserPromptSubmit` hook checks for this

### Routing protocol (active when PLAY MODE is on)

PLAY MODE is on when the conversation contains a recent `PLAY MODE: on` sentinel block AND the file `campaigns/{slug}/.meta/play-mode.flag` exists. The `UserPromptSubmit` hook injects a routing reminder on every turn while the flag is present.

For every freeform user turn during PLAY MODE (i.e. messages NOT starting with `/`), follow this protocol:

#### Step A — Classify the turn

Decide which of these the message contains. A single message can hit multiple categories (e.g. "Lyra took 8 damage and what's the AC of plate?" is both fact-to-route AND rules-question):

| Category | Signal | Dispatch to |
|---|---|---|
| **rules-question** | how does X work, what's the AC of Y, can I do Z, RAW vs ruling | `rules-oracle` |
| **player-fact** | mentions a known PC, companion, or "the bard/wizard/etc" referring to a unique class in the party | `player-data` |
| **npc-fact** | names a known NPC OR introduces a new named character with role/location | `npc-data` |
| **campaign-fact** | location change, in-game date, party-wide level up, quest open/close, book transition | `campaign-state` |
| **session-event** | combat outcome, decision, key plot beat, item found — narrative-worthy | `session-recorder` |
| **chit-chat** | OOC banter, table talk, meta about Claude itself | ignore |

If unsure, lean toward dispatching. Agents have `no_action_reason` outputs; an agent that says "this isn't mine" is cheap.

#### Step B — Dispatch in parallel

For each non-empty category, invoke its agent via the Agent tool. Run all dispatches in **a single message with parallel Agent tool calls** — no sequential waiting.

Each Agent call uses:
- `subagent_type`: the agent name (`player-data`, `npc-data`, `campaign-state`, `session-recorder`, `rules-oracle`)
- `description`: short ("Route player fact", "Answer rules question")
- `prompt`: a self-contained brief including:
  - `campaign_slug` (from `ACTIVE CAMPAIGN:` block)
  - `utterance` (the user's message, possibly trimmed to the relevant fragment)
  - `mode: propose` (default; use `verify` for post-write self-review)
  - For session-recorder, include `play_mode: on`

#### Step C — Aggregate proposals

Parse the JSON block from each agent. Collect all `proposals[]`, all `questions[]`, and any `no_action_reason` route hints.

If an agent returned `no_action_reason` suggesting a different agent, dispatch to that agent in a follow-up parallel batch (max one re-route per turn — prevents loops).

#### Step D — Apply write policy

For each proposal, apply by `stake_level`:

- **`stake_level: low`** — apply immediately: pipe the proposal to `bin/apply-proposal.py`. Summarize each as a one-liner in your reply, e.g.:
  > ✓ lyra.md → Pets: added Whiskers

- **`stake_level: high`** — collect into a single batched confirmation prompt at the end of the turn:
  ```
  ┌─ Pending changes (3 high-stake) ─
  │ 1. lyra.md  → Class: Bard L9 → L10
  │ 2. campaign.json → party_level 9 → 10
  │ 3. ash.md (new) → companion file for Mira
  └─
  Apply all? (y / n / review)
  ```
  - **y** → apply all in sequence via `bin/apply-proposal.py` (pass the whole batch with `--input`)
  - **n** → discard all, log as agent self-rejected (`outcome: agent-self-rejected`) to `.meta/rejections.jsonl`
  - **review** → walk one at a time, using `--dry-run` to show the diff: `[1/3] lyra.md: Bard L9 → L10. apply / skip / edit / quit`

If `questions[]` is non-empty for any proposal, ask those first — answers may change which proposals are valid. After the user answers, re-invoke the agent with the answer in `utterance`.

#### Step E — Post-write self-review (high-stake writes only)

After a **high-stake** proposal has been applied (user said `y` or `apply` in the batch confirmation), re-invoke the proposing agent with `mode: verify`. Pass:

- `campaign_slug`
- `utterance` (the original message that produced the proposal)
- `applied_proposal` (the proposal object that was applied)

The agent re-reads the file and returns a verification block:

```json
{
  "verification": {
    "matches_intent": true|false,
    "schema_intact": true|false,
    "anomalies": ["..."],
    "summary": "one-line status"
  }
}
```

- If `matches_intent: false` OR `anomalies` is non-empty: surface to the user as `⚠ Heads up: {summary}` and offer `revert / accept / investigate`. On `revert`, propose the opposite change against the same target and apply it — reverting is re-addressing, not an inverse byte swap.
- If clean: silently proceed. Don't add noise.

**Skip self-review for low-stake writes** — the cost (additional agent invocation per write) isn't worth it for low-risk changes. If a low-stake write later turns out wrong, the rejection-capture path (Step G) handles it.

Run all post-write verifications for a turn in **a single parallel batch** of Agent calls.

#### Step F — Answer rules questions

If `rules-oracle` was dispatched, surface its answer text directly (it returns prose, not JSON). Place rules answers ABOVE the change summary, since they're typically what the user is waiting for.

#### Step G — Capture rejection signal

Two distinct triggers append to `campaigns/{slug}/.meta/rejections.jsonl`:

**G1. User correction.** When the user's NEXT turn after a routed change contains correction language, log it. Trigger phrases (case-insensitive substring match is fine — be liberal):

- "no, that's wrong"
- "you put it in the wrong [file/place/section]"
- "{X} belongs to / is {Y}, not {Z}"
- "that should have been {…}"
- "undo that"
- "revert"
- explicit edit of the same field via `/update-player`, `/add-npc`, or other slash command immediately following

**G2. Agent self-rejection.** When an agent returned `no_action_reason` AND your next user turn indicates that was wrong ("you should have updated Lyra", "but {fact} is about {entity}"), log it.

**How to write the record.** Use the `Bash` tool to append a single JSON line:

```bash
echo '{"ts":"2026-05-02T18:42:13Z","session":36,"agent":"player-data","utterance":"...","proposed":{...},"outcome":"user-corrected","correction":"Whiskers belongs to Lyra","reason":null}' >> campaigns/{slug}/.meta/rejections.jsonl
```

Required JSON fields:
- `ts` — ISO-8601 UTC timestamp (use `date -u +"%Y-%m-%dT%H:%M:%SZ"`)
- `session` — current session number from campaign.json, or `null` if not in PLAY MODE
- `agent` — name of the agent that proposed the rejected change (or that returned the no_action_reason for self-rejection)
- `utterance` — the original user message that triggered routing
- `proposed` — the full proposal object (or `null` for self-rejection)
- `outcome` — one of `"user-corrected"`, `"agent-self-rejected"`, `"applied-then-reverted"`
- `correction` — what the user said the right answer was, or `null`
- `reason` — free-text reason if known, else `null`

After logging, re-route the original utterance with the correction context (G1) or dispatch to the right agent (G2). One re-route per turn — prevents loops.

**Don't double-log.** A single rejection should produce exactly one record, even if the user says it multiple ways across turns. Track recently-logged rejections in your turn working memory.

#### Step H — Bypass rules

These NEVER route — they always execute as written:

- Slash commands (`/anything`) — bypass routing entirely
- Direct meta-commands ("show me the audit", "what agents do you have")
- Anything during an active explicit flow (e.g. mid-`/update-player` interview) — the active command owns the conversation until it completes

If you can't tell whether a message is routable or chit-chat, default to: dispatch with low confidence. Cheaper than missing a fact.

#### Step I — Performance note

Each Agent dispatch costs tokens (subagent has its own context). For very obvious one-shot facts, consider whether the orchestrator could just edit directly. **Default: dispatch.** The cost is worth the consistency, the audit trail, and the rejection capture. Only skip dispatch if the change is purely cosmetic and unambiguous (e.g. fixing a typo in a file you just wrote).
