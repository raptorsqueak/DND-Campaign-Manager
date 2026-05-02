# /generate-npc — AI-Generate a Contextual NPC

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load Full Campaign Context

Read in this order:

1. `DNDCampaign/campaigns/{campaign-slug}/campaign.json`
2. `DNDCampaign/campaigns/{campaign-slug}/session-log.md` (last 30 lines for current situation)
3. All files in `DNDCampaign/campaigns/{campaign-slug}/npcs/` (to avoid name and role duplication)
4. All files in `DNDCampaign/campaigns/{campaign-slug}/players/` (for backstory connection opportunities)
5. All `.md` files in `DNDCampaign/campaigns/{campaign-slug}/supplements/`
6. All `.md` files in `DNDCampaign/supplements/`
7. `DNDCampaign/supplements/npc-generation.md`

Then check `campaign.json → book` and load the matching adventure book file if known:
- "Storm King's Thunder" → `DNDCampaign/campaigns/{campaign-slug}/supplements/storm-kings-thunder.md`
- "Waterdeep: Dungeon of the Mad Mage" or "Dungeon of the Mad Mage" → `DNDCampaign/campaigns/{campaign-slug}/supplements/dungeon-of-the-mad-mage.md`

---

## Step 2: Get Generation Context

Ask the user one question:

"What do you need this NPC for? Describe the scene, situation, or role — include location, tone, and any constraints (faction, moral alignment, age, species, etc.)"

Examples:
- "A scarred veteran guarding the gates of Nightstone who distrusts strangers"
- "A jovial gnome merchant who sells questionable magical curiosities"
- "A mysterious contact who knows about the cult's inner circle but has their own agenda"

---

## Step 3: Generate the NPC

Using all loaded context, generate a complete NPC that:

- Fits the campaign's book, setting, and tone (including `custom_notes` from campaign.json)
- Does NOT duplicate the name or exact role of any NPC currently in the `npcs/` directory
- Does NOT use the name of a named canon NPC from the loaded book file
- Uses the personality generation guidance from `npc-generation.md` (demeanor, motivation, secret, quirk, humanizing detail)
- Has a clear hook: an immediate want, an obstacle, and something that makes them memorable
- Includes combat stats if their role implies potential combat (using the Quick NPC Creation approach from npc-generation.md)
- Considers player backstories for connection opportunities that add richness

Display the full generated NPC using the schema below, clearly labeled as a preview:

```markdown
=== GENERATED NPC (PREVIEW) ===

# {NPC Name}

**Type**: {Major NPC / Minor NPC / Recurring / One-Shot}
**Source**: Generated
**Campaign**: {campaign name}
**Created**: {today's date}

## Identity
- **Role**: {role}
- **Location**: {location}
- **Affiliation**: {affiliation or "None"}

## Appearance
{2–3 sentence physical description with a distinctive visual detail}

## Personality
- **Demeanor**: {how they come across to strangers}
- **Motivation**: {what they want / what drives them}
- **Secret**: {something they're hiding — DM eyes only}
- **Voice/Speech**: {speech pattern, accent, verbal tic}
- **Quirk**: {physical habit or distinctive behavior}

## Relationship to Party
- **Standing**: {Hostile / Unfriendly / Indifferent / Friendly / Allied}
- **History**: No prior contact

## What They Can Offer
{specific information, quest hooks, goods, or services}

## Combat Stats
*(if applicable)*
- **CR / Role**: 
- **AC**: 
- **HP**: 
- **Attack**: 
- **Damage**: 
- **Notable Abilities**: 

## DM Notes
{plot threads, connections to other NPCs or player backstories, planned arcs}
===
```

Then ask:

```
Options:
  1. Save this NPC
  2. Adjust something (describe what to change)
  3. Regenerate entirely
```

---

## Step 4: Save, Adjust, or Regenerate

- **Save**: Derive filename (lowercase, hyphens), check for collision in `npcs/`, write file. Confirm: "Saved: {name} — {role}"
- **Adjust**: Apply the requested changes to the generated NPC, display the revised version, ask again.
- **Regenerate**: Generate a completely new NPC. Do not reuse the name or core concept of the discarded one.

If saving and a filename collision exists: "An NPC named {name} already exists. Overwrite, or use a different filename?"
