# D&D Campaign Manager

A D&D 5e campaign management system that runs entirely inside [Claude Code](https://claude.ai/code). No app, no dashboard — just slash commands in your terminal that act as a full Dungeon Master's assistant: tracking players, NPCs, session notes, rules questions, and session planning, with optional two-way sync to an [Obsidian](https://obsidian.md) vault.

Inspired by [claude-dungeon-master](https://github.com/PinchOfData/claude-dungeon-master) by PinchOfData.

---

## What It Does

- **Player character sheets** — create and update full 5e sheets with derived stats, skills, spell slots, and equipment
- **NPC management** — manually add NPCs or AI-generate contextual ones from your campaign state
- **Session logging** — record what happened, update quest state, and keep a running campaign journal
- **Session planning** — generate structured three-act session plans tied to active quests, backstory threads, and NPC relationships
- **Rules Q&A** — ask 5e rules questions answered against the SRD, your house rules, and campaign supplements
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

Claude Code will automatically load `CLAUDE.md` as project context. All slash commands will be available immediately.

### 3. Start your first campaign

```
/start-campaign
```

This walks you through creating a new campaign or resuming an existing one. Once started, all other commands are available.

---

## Obsidian Vault Setup

If you want to use `/sync-obsidian`, your Obsidian vault needs these folders:

```
YourVault/
├── Campaign/             # Session prep notes (YYYY-MM-DD Title.md format)
├── Items/                # Magic items and equipment
├── NPCs/                 # NPC files, organized by location subfolder
│   ├── Waterdeep/
│   ├── Silvery Moon/
│   ├── Road & Wilderness/
│   └── ...               # Add subfolders per location as needed
└── Playable Characters/  # PC and companion files
```

Once your vault exists, add its path to your campaign:

```
/campaign-info
```

Select **Edit metadata** and set the `obsidian_vault` field to the absolute path of your vault (e.g. `/Users/yourname/Documents/MyVault`).

### NPC location mapping

`/sync-obsidian` automatically files new NPCs into the correct subfolder based on their recorded location:

| NPC location contains… | Vault subfolder |
|---|---|
| Waterdeep | `NPCs/Waterdeep/` |
| Undermountain | `NPCs/Undermountain/` |
| Silverymoon / Silvery Moon | `NPCs/Silvery Moon/` |
| Amphail | `NPCs/Amphail/` |
| Everlund | `NPCs/Everlund/` |
| Triboar | `NPCs/Triboar/` |
| Underdark | `NPCs/Underdark/` |
| Road / Wilderness / journey | `NPCs/Road & Wilderness/` |
| No match | `NPCs/` (root — organize manually) |

---

## Commands

| Command | Description |
|---|---|
| `/start-campaign` | Start a new campaign or resume an existing one. Sets the active campaign for all other commands. |
| `/add-player` | Add a player character with a full 5e sheet — ability scores, skills, saves, spells, equipment, and backstory. |
| `/update-player` | Update any field on a character sheet: level up, fill missing stats, add equipment, adjust HP, edit spells, or free-form edit. |
| `/add-npc` | Manually define an NPC with role, personality, secrets, combat stats, and DM notes. |
| `/generate-npc` | AI-generate a contextual NPC based on your current campaign state, location, and party level. |
| `/campaign-info` | View or update campaign metadata: location, quests, party level, Obsidian vault path, and custom notes. |
| `/ask-dnd` | Rules Q&A answered against the SRD, your house rules, and campaign supplements. Flags when house rules override RAW. |
| `/session-log` | Record session notes, update quest state, and append to the campaign journal. |
| `/plan-next-session` | Build a structured session plan with three acts, NPC appearances, loot, and DM-only secrets. Optionally write prep notes to your Obsidian vault. |
| `/sync-obsidian` | Sync players, companions, NPCs, and session notes to your Obsidian vault. Never deletes existing vault content. |

---

## Project Structure

```
dnd-campaign-manager/
├── CLAUDE.md                          # Project context and command documentation
├── .claude/
│   └── commands/                      # Slash command definitions
│       ├── start-campaign.md
│       ├── add-player.md
│       ├── update-player.md
│       ├── add-npc.md
│       ├── generate-npc.md
│       ├── campaign-info.md
│       ├── ask-dnd.md
│       ├── session-log.md
│       ├── plan-next-session.md
│       └── sync-obsidian.md
├── supplements/                       # Global supplements (house rules, homebrew)
│   ├── combat-rules.md
│   ├── character-sheets.md
│   ├── npc-generation.md
│   ├── campaign-generation.md
│   ├── items-and-loot.md
│   ├── spellcasting.md
│   └── srd/                           # D&D 5e SRD (see License)
│       ├── 01 races.md
│       └── ...
└── campaigns/
    └── {campaign-slug}/
        ├── campaign.json              # Campaign state and metadata
        ├── session-log.md             # Running session journal
        ├── players/                   # Player character sheets
        ├── npcs/                      # NPC records
        └── supplements/               # Campaign-specific supplements and session plans
```

### Adding house rules or homebrew

Drop any `.md` file into `supplements/` to make it available to all campaigns, or into `campaigns/{slug}/supplements/` for a single campaign. Claude will load and apply these automatically, and will flag when they override RAW.

### Campaign supplements

Adventure book summaries live in `campaigns/{slug}/supplements/` (e.g. `storm-kings-thunder.md`). Session plans generated by `/plan-next-session` are saved there too.

---

## How It Works

Every command is a Markdown file in `.claude/commands/` — a step-by-step instruction set that Claude follows when you invoke the slash command. Claude Code loads `CLAUDE.md` as persistent project context, so rules, supplements, and campaign data are always in scope.

The **active campaign** is tracked by a block that `/start-campaign` emits at the end of its response:

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DNDCampaign/campaigns/{campaign-slug}/
```

Every other command scans the conversation for this block to know which campaign to operate on. No environment variables or config files needed — the conversation itself is the state.

---

## Credits

- Inspired by [claude-dungeon-master](https://github.com/PinchOfData/claude-dungeon-master) by [PinchOfData](https://github.com/PinchOfData)
- D&D 5e SRD content sourced from the [PinchOfData](https://github.com/PinchOfData/claude-dungeon-master) project

---

## License

**CLAUDE.md and all files in `.claude/commands/`:** MIT License — see [LICENSE](LICENSE)

**D&D 5e SRD content** (`supplements/srd/`): Open Gaming License v1.0a — see [`supplements/srd/LICENSE`](supplements/srd/LICENSE)

*Dungeons & Dragons, D&D, and related marks are trademarks of Wizards of the Coast. This project is unofficial fan content, not affiliated with or endorsed by Wizards of the Coast.*
