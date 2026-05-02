# /ask-dnd — D&D 5e Rules Q&A

---

## Step 0: Check for Active Campaign (Optional)

Scan the conversation for the most recent `ACTIVE CAMPAIGN:` block. If found, extract `{campaign-slug}` and use campaign context. If not found, proceed with SRD and built-in knowledge only — this command works without an active campaign.

---

## Step 1: Get the Question

If a question was passed inline with the command (e.g., `/ask-dnd Can I grapple while prone?`), use it directly.

If the command was invoked with no question, ask: "What's your D&D question?"

---

## Step 2: Load Topic-Relevant SRD Files

Determine the topic from the question, then load the most relevant SRD markdown file(s) from `DNDCampaign/supplements/srd/`:

| Topic Keywords | Files to Load |
|---|---|
| race, racial, subrace, heritage | `01 races.md` |
| class, subclass, archetype, feature, level up | `02 classes.md`, `03 beyond1st.md` |
| equipment, weapon, armor, shield, tool, cost | `04 equipment.md` |
| feat | `05 feats.md` |
| skill, check, ability score, saving throw, proficiency | `06 mechanics.md` |
| combat, attack, action, bonus action, reaction, initiative, grapple, shove, opportunity attack | `07 combat.md`, `12 conditions.md` |
| condition, poisoned, frightened, restrained, stunned, incapacitated | `12 conditions.md` |
| spell, spellcasting, slot, concentration, ritual, cantrip | `08 spellcasting.md` |
| dungeon master, encounter, CR, challenge rating, rest, downtime, XP | `09 running.md` |
| magic item, attunement, rarity, identification | `10 magic items.md` |
| monster, creature, stat block, legendary, lair | `11 monsters.md`, `15 creatures.md` |
| NPC, humanoid stat block | `16 npcs.md` |
| god, deity, religion, domain | `13 gods.md` |
| plane, planar, outer plane, inner plane, astral | `14 planes.md` |

If the question is broad or doesn't match a specific topic, load `06 mechanics.md` and `07 combat.md` as defaults.

---

## Step 3: Always Load DM Instructions

Always also read all six DM instruction files:
- `DNDCampaign/supplements/combat-rules.md`
- `DNDCampaign/supplements/spellcasting.md`
- `DNDCampaign/supplements/items-and-loot.md`
- `DNDCampaign/supplements/character-sheets.md`
- `DNDCampaign/supplements/npc-generation.md`
- `DNDCampaign/supplements/campaign-generation.md`

---

## Step 4: Load Campaign Context (if active campaign found)

If an active campaign is set:

1. Read all `.md` files in `DNDCampaign/supplements/` (global supplements — house rules, homebrew)
2. Read all `.md` files in `DNDCampaign/campaigns/{campaign-slug}/supplements/` (campaign-specific supplements)
3. Read `DNDCampaign/campaigns/{campaign-slug}/campaign.json`

If the question references a specific player by name, read their file from `DNDCampaign/campaigns/{campaign-slug}/players/`.

If the question references an NPC by name, read their file from `DNDCampaign/campaigns/{campaign-slug}/npcs/`.

Check `campaign.json → book` and load the matching book file if applicable:
- "Storm King's Thunder" → `DNDCampaign/campaigns/{campaign-slug}/supplements/storm-kings-thunder.md`
- "Waterdeep: Dungeon of the Mad Mage" or "Dungeon of the Mad Mage" → `DNDCampaign/campaigns/{campaign-slug}/supplements/dungeon-of-the-mad-mage.md`

---

## Step 5: Answer

Apply context in this priority order:

1. **Global supplements** (house rules/homebrew from `supplements/`) — highest priority, override RAW
2. **Campaign supplements** — override SRD for this campaign
3. **SRD rules as written (RAW)** — from the loaded markdown files
4. **Built-in 5e knowledge** — for content beyond SRD (PHB subclasses, specific spell interactions, etc.)

**Format the answer**:
- Give the direct answer first, then cite the source ("Per SRD combat rules...", "Your house rules state...", "Per PHB Wizard subclass...")
- For gray areas or common DM rulings, explicitly flag: "RAW is X, but a common ruling / Sage Advice ruling is Y."
- If a supplement overrides SRD, say: "Your house rule overrides RAW here — [rule]."
- If the question is about a specific PC, reference their actual stats from the player file.
- If the question is about a specific book encounter or NPC, reference what the book file says.
- Keep answers concise but complete. Use a bullet list if multiple rules interact.

**No active campaign**: Answer using SRD + dm-instructions + built-in knowledge only. Note if content is beyond SRD.
