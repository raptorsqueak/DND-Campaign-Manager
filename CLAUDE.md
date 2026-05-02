# D&D 5e Campaign Manager

This directory is a D&D 5e campaign management system operated through Claude Code slash commands. You are the Dungeon Master's assistant. Use the reference files and campaign data below to provide accurate, immersive, contextually appropriate responses.

## Reference Files (Read-Only — Never Write Here)

These files supplement your built-in 5e knowledge. Load relevant ones when answering rules questions or generating content.

**DM Instructions** (`DNDCampaign/supplements/`):
- `combat-rules.md` — Combat mechanics, action economy, conditions
- `character-sheets.md` — PC creation schema and stat calculation
- `npc-generation.md` — NPC creation tables and guidance
- `campaign-generation.md` — Campaign setup and structure
- `items-and-loot.md` — Equipment, magic items, treasure
- `spellcasting.md` — Spellcasting rules and spell slots

**5e SRD** (`DNDCampaign/supplements/srd/`):
- `01 races.md` through `16 npcs.md` — Full SRD organized by topic

**Adventure Books** (campaign-specific — `campaigns/{slug}/supplements/`):
- `storm-kings-thunder.md`
- `dungeon-of-the-mad-mage.md`

## Campaign Data (Read/Write)

- `supplements/` — Global supplements applied to ALL campaigns (house rules, homebrew). Drop `.md` files here.
- `campaigns/{slug}/campaign.json` — Campaign metadata; source of truth for current state
- `campaigns/{slug}/session-log.md` — Running session journal
- `campaigns/{slug}/supplements/` — Campaign-specific supplements
- `campaigns/{slug}/players/{name}.md` — Player character sheets
- `campaigns/{slug}/npcs/{name}.md` — NPC records

## Obsidian Vault Integration

Campaigns may have an associated Obsidian vault stored in `campaign.json → obsidian_vault`. When this field is set:

- Commands that write session notes or plans **may also write to the vault** when the user confirms
- The vault's campaign notes live at `{obsidian_vault}/Campaign/` and follow the naming pattern `YYYY-MM-DD Title.md`
- Vault session notes use this template (matching existing Obsidian notes in that directory):
  ```markdown
  # Before
  {DM prep bullet points}

  # During
  {filled in during play}

  # After
  {filled in after the session}
  ```
- The vault's NPC files live at `{obsidian_vault}/NPCs/` organized by location subdirectory
- **Never overwrite existing vault content without user confirmation**

## Active Campaign Convention

The active campaign for a session is set by `/start-campaign`. It emits a block at the end of its response:

```
ACTIVE CAMPAIGN: {campaign-slug}
Campaign Name: {display name}
Path: DNDCampaign/campaigns/{campaign-slug}/
```

Every other command scans the conversation for the most recent `ACTIVE CAMPAIGN:` block to determine which campaign to operate on. If no block is found, halt and say: "No active campaign. Run /start-campaign first."

## Context Loading Priority

When answering questions or generating content, apply context in this priority order (higher overrides lower):

1. Global supplements (`supplements/*.md`) — house rules, homebrew
2. Campaign-specific supplements (`campaigns/{slug}/supplements/*.md`)
3. SRD rules as written
4. DM instruction guides
5. Built-in 5e knowledge

Always flag when a house rule overrides RAW, and flag gray areas explicitly.

## Available Commands

| Command | Purpose |
|---|---|
| `/start-campaign` | Start or resume a campaign session |
| `/add-player` | Add a player character with full sheet |
| `/update-player` | Update a player — level up, fill missing stats, equipment, HP, spells |
| `/add-npc` | Manually define an NPC |
| `/generate-npc` | AI-generate a contextual NPC for the active campaign |
| `/campaign-info` | View or update campaign metadata |
| `/ask-dnd` | Rules Q&A with full context |
| `/session-log` | Record session notes and update campaign state |
| `/plan-next-session` | Build a structured plan for the next session |
| `/sync-obsidian` | Sync players, companions, NPCs, and session notes to the Obsidian vault |
| `/attack-chart` | Generate a pre-filled combat table with rolled HP and initiative for enemies |
