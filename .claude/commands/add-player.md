# /add-player — Add a Player Character

---

## Step 0: Check Active Campaign

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If none is found, stop and say: "No active campaign. Run /start-campaign first."

Extract `{campaign-slug}`.

---

## Step 1: Load Reference Context

Read:
- `DNDCampaign/campaigns/{campaign-slug}/campaign.json` (to know party_level and setting)
- `DNDCampaign/supplements/character-sheets.md` (PC schema and stat calculation reference)

---

## Step 2: Character Creation Interview

Tell the user: "Let's add a new player character. I'll ask you questions one at a time — answer each before I ask the next."

Ask in this sequence, one question at a time:

1. **Player name**: "What is the player's real name?"
2. **Character name**: "What is the character's name?"
3. **Concept**: "Describe the character in a sentence or two — who are they, what kind of adventurer?"
4. **Race**: Briefly list the SRD races with one-line descriptions (Human, Elf, Dwarf, Halfling, Gnome, Half-Elf, Half-Orc, Tiefling, Dragonborn, plus any campaign-specific races). Ask: "Which race? Or describe a homebrew race."
5. **Class**: Briefly list the SRD classes (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard). Ask: "Which class?"
6. **Background**: Ask: "What background? (Common options: Acolyte, Criminal, Folk Hero, Noble, Sage, Soldier, Outlander, etc.) Describe a custom one if preferred."
7. **Alignment**: Ask: "What alignment?"
8. **Ability score method**: Ask: "How are you generating ability scores? (a) Standard array: 15,14,13,12,10,8 / (b) Point buy / (c) Rolled"
   - If (a): Tell them the array values and ask which score goes to each ability (STR, DEX, CON, INT, WIS, CHA)
   - If (b): Explain point buy rules (27 points, costs 1pt per point from 8–13, 2pts for 14, 3pts for 15) and ask for their 6 scores
   - If (c): Ask them to provide their 6 rolled scores and which ability each goes to
9. **Equipment**: Ask: "List your starting equipment. Include armor type if worn."
10. **Gold**: Ask: "How much starting gold do you have?"
11. **Backstory**: Ask: "Give your character's backstory — a paragraph or more is great."
12. **Personality trait**: Ask: "What is one personality trait?"
13. **Ideal**: Ask: "What is your character's ideal (a principle they live by)?"
14. **Bond**: Ask: "What is your bond (a person, place, or thing you care about)?"
15. **Flaw**: Ask: "What is your character's flaw?"
16. **Spells** (only if class is Bard, Cleric, Druid, Paladin, Ranger, Sorcerer, Warlock, or Wizard): Ask: "Which spells do you know or have prepared at level {party_level}? List cantrips and leveled spells separately."

---

## Step 3: Calculate Derived Stats

Using the class, race, scores, and level from campaign.json, calculate:

- **Ability modifiers**: floor((score - 10) / 2) for each ability
- **Proficiency bonus**: +2 at levels 1–4, +3 at 5–8, +4 at 9–12, +5 at 13–16, +6 at 17–20
- **Initiative**: DEX modifier
- **Saving throw proficiencies**: per class (e.g., Fighter = STR + CON)
- **Skill proficiencies**: from class list + background + any racial bonuses
- **Skill modifiers**: relevant ability modifier + proficiency bonus if proficient
- **AC**: 
  - No armor: 10 + DEX mod (or class feature like Unarmored Defense)
  - Light armor: base AC + DEX mod
  - Medium armor: base AC + min(DEX mod, 2)
  - Heavy armor: fixed base AC (no DEX)
  - Shield: +2
- **HP at level 1**: max hit die + CON modifier. For higher levels, ask: "What is your current HP maximum?"
- **Hit dice**: class hit die × level
- **Speed**: by race (Human/Elf/Half-Elf/Half-Orc/Tiefling/Dragonborn = 30ft; Dwarf/Gnome/Halfling = 25ft)
- **Spell save DC** (if applicable): 8 + proficiency bonus + spellcasting ability modifier
- **Spell attack bonus** (if applicable): proficiency bonus + spellcasting ability modifier
- **Spell slots** (if applicable): per class and level from SRD tables

Show a preview of the complete character sheet using the schema below. Ask: "Does this look correct? Anything to change before I save?"

---

## Step 4: Write the File

After confirmation, derive the filename: lowercase character name, replace spaces with hyphens, remove special characters. Example: "Thyra Ironwood" → `thyra-ironwood.md`.

If a file with that name already exists in `players/`, ask: "A character named {name} already exists. Overwrite, or use a different filename?"

Write to `DNDCampaign/campaigns/{campaign-slug}/players/{filename}.md` using this schema:

```markdown
# {Character Name}

**Player**: {player name}
**Campaign**: {campaign name}
**Last Updated**: {today's date}

## Basic Info
- **Race**: {race}
- **Class**: {class} (Level {level})
- **Background**: {background}
- **Alignment**: {alignment}
- **Age / Appearance**: {from concept description}

## Ability Scores
| Stat | Score | Modifier |
|------|-------|----------|
| STR  | {n}   | {+/-n}   |
| DEX  | {n}   | {+/-n}   |
| CON  | {n}   | {+/-n}   |
| INT  | {n}   | {+/-n}   |
| WIS  | {n}   | {+/-n}   |
| CHA  | {n}   | {+/-n}   |

## Combat Stats
- **AC**: {n}
- **HP**: {current} / {max}
- **Hit Dice**: {n}d{n}
- **Speed**: {n} ft
- **Initiative**: {+/-n}
- **Proficiency Bonus**: +{n}

## Saving Throws
- **Proficient**: {list}
- **Values**: STR {+/-n}, DEX {+/-n}, CON {+/-n}, INT {+/-n}, WIS {+/-n}, CHA {+/-n}

## Skills
| Skill | Modifier | Proficient |
|-------|----------|------------|
| Acrobatics (DEX) | {+/-n} | {Yes/No} |
| Animal Handling (WIS) | {+/-n} | {Yes/No} |
| Arcana (INT) | {+/-n} | {Yes/No} |
| Athletics (STR) | {+/-n} | {Yes/No} |
| Deception (CHA) | {+/-n} | {Yes/No} |
| History (INT) | {+/-n} | {Yes/No} |
| Insight (WIS) | {+/-n} | {Yes/No} |
| Intimidation (CHA) | {+/-n} | {Yes/No} |
| Investigation (INT) | {+/-n} | {Yes/No} |
| Medicine (WIS) | {+/-n} | {Yes/No} |
| Nature (INT) | {+/-n} | {Yes/No} |
| Perception (WIS) | {+/-n} | {Yes/No} |
| Performance (CHA) | {+/-n} | {Yes/No} |
| Persuasion (CHA) | {+/-n} | {Yes/No} |
| Religion (INT) | {+/-n} | {Yes/No} |
| Sleight of Hand (DEX) | {+/-n} | {Yes/No} |
| Stealth (DEX) | {+/-n} | {Yes/No} |
| Survival (WIS) | {+/-n} | {Yes/No} |

## Proficiencies
- **Weapons**: {list}
- **Armor**: {list}
- **Tools**: {list or none}
- **Languages**: {list}

## Features & Traits
{racial and class features at current level, listed by name and brief description}

## Equipment
{gear list, one item per line}

## Currency
- **Gold**: {gp}

## Spellcasting
*(Remove this section if not a spellcaster)*
- **Spellcasting Ability**: {ability}
- **Spell Save DC**: {n}
- **Spell Attack Bonus**: {+n}
- **Spell Slots**: {1st: n/n, 2nd: n/n, ...}

### Cantrips
{list}

### Spells Known / Prepared
{list by level}

## Backstory
{backstory text}

## Personality
- **Trait**: {trait}
- **Ideal**: {ideal}
- **Bond**: {bond}
- **Flaw**: {flaw}

## Session Notes
*(Updated after sessions)*
```

Confirm: "Saved: {character name} — {race} {class} (Level {level}) to players/{filename}.md"
