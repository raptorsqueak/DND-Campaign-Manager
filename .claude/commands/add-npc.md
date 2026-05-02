# /add-npc — Manually Add an NPC

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: NPC Interview

Tell the user: "Let's add an NPC. Answer as much or as little as you know — type 'skip' for anything you want to leave blank."

Ask one at a time:

1. **Name**: "What is the NPC's name?"
2. **Type**: "Is this a Major NPC, Minor NPC, Recurring character, or a One-Shot?"
3. **Role**: "What is their role or occupation? (e.g., blacksmith, city guard captain, cult leader)"
4. **Location**: "Where are they typically found?"
5. **Affiliation**: "Any faction or organization? (or 'none')"
6. **Appearance**: "Brief physical description?"
7. **Personality**: "Key personality traits, motivation, or defining quirks?"
8. **Secret**: "Any secret they're hiding? (or 'none' — DM eyes only)"
9. **Party relationship**: "How do they relate to the party? (Hostile / Unfriendly / Indifferent / Friendly / Allied)"
10. **History with party**: "What has happened between this NPC and the party so far? (or 'none yet')"
11. **Usefulness**: "What can this NPC offer the party? (information, quests, goods, services, etc.)"
12. **Combat stats**: "Does this NPC need combat stats? (yes / no / maybe)"
    - If **yes**: "Provide CR or role (e.g., CR 3 assassin) and any known stats, or type 'suggest' and I'll recommend stats."
    - If **suggest**: read `npc-generation.md` and suggest HP, AC, attack, damage based on the NPC's archetype and CR. Ask: "Do these work, or adjust?"
    - If **no** or **maybe**: leave stats section blank or note "(not combat-relevant)"
13. **DM notes**: "Any private DM notes — plot role, planned arcs, secrets, connections to other NPCs? (or 'none')"

---

## Step 2: Check for Name Collision

Before writing, check if `DNDCampaign/campaigns/{campaign-slug}/npcs/` already contains a file matching this NPC's name slug.

If a collision exists, ask: "An NPC named {name} already exists. Options: (1) View existing file, (2) Overwrite, (3) Use a different filename"

---

## Step 3: Write the File

Derive filename: lowercase NPC name, replace spaces with hyphens, remove special characters. Example: "Brother Aldric" → `brother-aldric.md`.

Write to `DNDCampaign/campaigns/{campaign-slug}/npcs/{filename}.md`:

```markdown
# {NPC Name}

**Type**: {Major NPC / Minor NPC / Recurring / One-Shot}
**Source**: Manual
**Campaign**: {campaign name}
**Created**: {today's date}

## Identity
- **Role**: {role}
- **Location**: {location}
- **Affiliation**: {affiliation or "None"}

## Appearance
{appearance description or "(not described)"}

## Personality
- **Demeanor**: {traits}
- **Motivation**: {motivation}
- **Secret**: {secret or "(none known)"}
- **Quirk**: {physical or speech quirk, if any}

## Relationship to Party
- **Standing**: {Hostile / Unfriendly / Indifferent / Friendly / Allied}
- **History**: {history or "No prior contact"}

## What They Can Offer
{what they can give the party, or "(nothing currently)"}

## Combat Stats
*(Remove or leave blank if not combat-relevant)*
- **CR / Role**: 
- **AC**: 
- **HP**: 
- **Attack**: 
- **Damage**: 
- **Notable Abilities**: 

## DM Notes
{dm notes or "(none)"}
```

Confirm: "Saved: {NPC name} — {role} ({standing} to party)"
