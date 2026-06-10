# D&D Campaign Manager

My intent on this project is to accelerate the ideation process and hand off some of the administrative tasks to an LLM. Ideally the LLM will provide a scaffolding for story telling – when Claude tries to provide more, simply tell it that it’s providing too much detail to reign it back in. When you plan a session, it should generate a campaign page and a session notes page in your Obsidian vault. Session should be bullet points that point to the campaign notes to provide refernce.

Now with out further ado, we'll let he LLM do one of those administrative tasks (creating a README.md):

A D&D 5e campaign management system that runs entirely inside [Claude Code](https://claude.ai/code). No app, no dashboard — just slash commands in your terminal that act as a full Dungeon Master's assistant: tracking players, NPCs, session notes, rules questions, and session planning, with optional two-way sync to an [Obsidian](https://obsidian.md) vault.

During live play, a **PLAY MODE** routing layer reads your freeform table talk and dispatches it to specialist agents that keep your campaign files up to date automatically — no slash command required.

Inspired by [claude-dungeon-master](https://github.com/PinchOfData/claude-dungeon-master) by PinchOfData.

---

## What It Does

- **Player character sheets** — create and update full 5e sheets with derived stats, skills, spell slots, and equipment
- **NPC management** — manually add NPCs or AI-generate contextual ones from your campaign state
- **Live play mode** — start a session and just narrate; specialist agents route facts to the right files (players, NPCs, campaign state, session log) and ask before high-stake writes
- **Session logging** — record what happened, update quest state, and keep a running campaign journal
- **Session planning** — generate structured session plans tied to active quests, backstory threads, and NPC relationships
- **Rules Q&A** — ask 5e rules questions answered against the SRD, your house rules, and campaign supplements
- **Supplement intake** — register adventure books, rules supplements, and lore; large books are split per chapter and summarized/indexed for cheap, selective loading
- **Combat prep** — generate a pre-filled attack chart with rolled HP and initiative for an encounter
- **Audit & self-improvement** — run integrity audits on campaign data, and review automatically-proposed improvements to the system itself
- **Obsidian sync** — push players, companions, NPCs, and session notes into your Obsidian vault without ever deleting existing content

---

## Requirements

- [Claude Code](https://claude.ai/code) — the CLI tool (requires a Claude subscription or Anthropic API key)
- [Obsidian](https://obsidian.md) *(optional)* — for vault sync features

No other dependencies. Everything runs through Claude Code slash commands.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/raptorsqueak/dnd-campaign-manager.git
cd dnd-campaign-manager
```

### 2. Open in Claude Code

```bash
claude
```

Claude Code automatically loads `CLAUDE.md` as project context. All slash commands are available immediately.

### 3. Start your first campaign

```
/start-campaign
```

This walks you through creating a new campaign or resuming an existing one, and sets the **active campaign** that every other command operates on. It creates the campaign's folders for you.

### 4. Begin live play (optional)

```
/start-session
```

This turns on **PLAY MODE**. While it's on, your freeform messages are read and routed to specialist agents automatically. Run `/end-session` to turn it off and finalize the session log.

---

## Commands

| Command | Description |
|---|---|
| `/start-campaign` | Load a campaign — create a new one or resume an existing one. Sets the active campaign for all other commands. Does **not** turn on PLAY MODE. |
| `/start-session` | Begin a live play session — turns on PLAY MODE so freeform messages route automatically. |
| `/end-session` | End a live play session — offers to finalize the in-progress session log, then turns off PLAY MODE. |
| `/add-player` | Add a player character with a full 5e sheet — ability scores, skills, saves, spells, equipment, and backstory. |
| `/update-player` | Update any field on a character sheet: level up, fill missing stats, add equipment, adjust HP, edit spells, or free-form edit. |
| `/add-npc` | Manually define an NPC with role, personality, secrets, combat stats, and DM notes. |
| `/generate-npc` | AI-generate a contextual NPC based on your current campaign state, location, and party level. |
| `/campaign-info` | View or update campaign metadata: location, quests, party level, Obsidian vault path, and custom notes. |
| `/ask-dnd` | Rules Q&A answered against the SRD, your house rules, and campaign supplements. Flags when house rules override RAW. (In PLAY MODE, rules questions auto-route to the `rules-oracle` agent.) |
| `/session-log` | Record session notes, update quest state, and append to the campaign journal. |
| `/plan-next-session` | Build a structured session plan tied to active quests, NPC appearances, loot, and DM-only secrets. Optionally write prep notes to your Obsidian vault. |
| `/attack-chart` | Generate a pre-filled combat table with rolled HP and initiative for an encounter's enemies. |
| `/add-content` | Intake a new supplement (book / rules / lore / backstory): copies the source, splits adventure books per chapter, generates a summary + index, and registers it in the manifest. |
| `/sync-obsidian` | Sync players, companions, NPCs, and session notes to your Obsidian vault. Never deletes existing vault content. |
| `/audit` | Run a schema / coverage / consistency audit on the active campaign, including supplement-shape checks. Optionally apply a suggested fix. |
| `/review-improvements` | Walk pending improvement candidates (efficiency, drift, memory hygiene, agent edits) proposed by the `improvement-curator` agent. Apply / skip / dismiss interactively. |

---

## PLAY MODE & Specialist Agents

When PLAY MODE is on, every freeform turn (anything not starting with `/`) is classified and dispatched to the relevant specialist agents in parallel. Each agent owns a slice of the campaign data and returns a structured proposal; the main session applies low-stake changes immediately and batches high-stake changes for your confirmation.

| Agent | Owns | Role |
|---|---|---|
| `player-data` | `players/*.md` | Routes player- and companion-related facts to the right sheet. |
| `npc-data` | `npcs/*.md` | Routes NPC facts; detects new NPCs and proposes creating a file. |
| `campaign-state` | `campaign.json` | Updates location, in-game date, party level, active quests, and active book. |
| `session-recorder` | `session-log.md` | Appends events to the in-progress session block during play. |
| `rules-oracle` | *(read-only)* | Answers 5e rules questions with citations from SRD, supplements, and house rules. |
| `schema-auditor` | *(read-only)* | On-demand audit of coverage, consistency, and schema drift (via `/audit`). |
| `improvement-curator` | improvement queue | Analyzes rejection logs, drift, and other signals to propose system improvements for human review. |

The full routing protocol, write policy, and proposal contract are documented in [`CLAUDE.md`](CLAUDE.md).

---

## Supplements (manifest-first)

Supplements extend Claude's built-in 5e knowledge with house rules, homebrew, lore, and adventure books. They are discovered through a **manifest** rather than raw directory scans, so a typical rules question loads only a few hundred lines instead of an entire book.

**Two scopes:**

- `supplements/` — global supplements applied to **all** campaigns (house rules, homebrew, large rules references, the SRD)
- `campaigns/{slug}/supplements/` — campaign-specific supplements (party backstory, homebrew items, the active adventure book)

Each scope has a `_manifest.json` that is the source of truth. Files not listed in the manifest are invisible to the system — always register content with `/add-content` rather than dropping files in by hand.

**Two layouts** (chosen automatically at intake):

- **Flat** — small, single-topic content (≤300 lines). Stored as a single `.md` file; the manifest entry carries a one-line summary.
- **Wrapped** — large reference content (adventure books). Stored in a `{slug}/` subdirectory with a summary, an index, and content files (adventure books are split per chapter). Consumers read the summary and index first, then drill into only the specific chapter / NPC / location they need.

The **SRD** lives in `supplements/srd/`, already chunked by topic.

When sources conflict, priority is: global rules-supplements (house rules / homebrew) → campaign-specific supplements → SRD → DM guidance → built-in 5e knowledge. Claude always flags when a house rule overrides RAW.

---

## Project Structure

The repo ships with the system files; campaign folders are created for you by `/start-campaign`. The minimum a campaign needs:

```
dnd-campaign-manager/
├── CLAUDE.md                          # Project context, routing protocol, write policy
├── README.md
├── .claude/
│   ├── commands/                      # Slash command definitions (one .md per command)
│   └── agents/                        # Specialist subagent definitions
├── supplements/                       # Global supplements (manifest + content + srd/)
│   └── _manifest.json
└── campaigns/
    └── {campaign-slug}/
        ├── campaign.json              # Campaign state and metadata (source of truth)
        ├── session-log.md             # Running session journal
        ├── players/                   # Player character & companion sheets
        ├── npcs/                      # NPC records
        ├── sessions/                  # Session-prep notes from /plan-next-session
        └── supplements/               # Campaign-specific supplements (+ _manifest.json)
```

The commands create additional working directories under a campaign as needed (e.g. for audit, routing, and book-progress state). You don't create those by hand.

### Adding supplements

Use `/add-content` to register house rules, homebrew, lore, or an adventure book. It chooses the flat or wrapped layout, generates summaries/indexes, and updates the manifest. Global content goes to `supplements/`; campaign-specific content goes to `campaigns/{slug}/supplements/`. Claude loads and applies these automatically and flags when they override RAW.

---

## Obsidian Vault Setup

If you want to use `/sync-obsidian`, your Obsidian vault needs these folders:

```
YourVault/
├── Sessions/             # Session notes (YYYY-MM-DD Title.md format)
├── Campaign/             # Campaign story / planning content
├── NPCs/                 # NPC files (add location subfolders as you like)
└── Playable Characters/  # PC and companion files
```

Once your vault exists, add its path to your campaign:

```
/campaign-info
```

Select **Edit metadata** and set the `obsidian_vault` field to the absolute path of your vault (e.g. `/Users/yourname/Documents/MyVault`).

`/sync-obsidian` never deletes existing vault content. If you organize NPCs into location subfolders under `NPCs/`, it files new NPCs into the matching subfolder based on their recorded location.

---

## How It Works

Every command is a Markdown file in `.claude/commands/` — a step-by-step instruction set Claude follows when you invoke the slash command. Every specialist agent is a Markdown file in `.claude/agents/`. Claude Code loads `CLAUDE.md` as persistent project context, so rules, supplements, and the routing protocol are always in scope.

The **active campaign** is tracked by a block that `/start-campaign` emits at the end of its response:

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DND-Campaign-Manager/campaigns/{campaign-slug}/
```

Every other command scans the conversation for the most recent such block to know which campaign to operate on. **PLAY MODE** is likewise signaled by a `PLAY MODE: on` sentinel plus a flag file the commands manage. No environment variables or external config — the conversation and a few flag files are the state.

---

## Credits

- Inspired by [claude-dungeon-master](https://github.com/PinchOfData/claude-dungeon-master) by [PinchOfData](https://github.com/PinchOfData)
- D&D 5e SRD content sourced from the [PinchOfData](https://github.com/PinchOfData/claude-dungeon-master) project

---

## License

**CLAUDE.md and all files in `.claude/commands/`:** MIT License — see [LICENSE](LICENSE)

**D&D 5e SRD content** (`supplements/srd/`): Open Gaming License v1.0a — see [`supplements/srd/LICENSE`](supplements/srd/LICENSE)

*Dungeons & Dragons, D&D, and related marks are trademarks of Wizards of the Coast. This project is unofficial fan content, not affiliated with or endorsed by Wizards of the Coast.*
