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

Determine the topic from the question, then load the most relevant SRD markdown file(s) from `DND-Campaign-Manager/supplements/srd/`:

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

## Step 3: Load Supplements (Manifest-First)

For each scope (always include global; include campaign if active campaign is set):

| Scope | Manifest path |
|---|---|
| Global | `DND-Campaign-Manager/supplements/_manifest.json` |
| Campaign | `DND-Campaign-Manager/campaigns/{campaign-slug}/supplements/_manifest.json` |

For each manifest:

1. **Read the manifest**. If it doesn't exist, fall back to: read all top-level `.md` files in that scope's supplements directory (legacy mode).
2. **Read summaries first**:
   - **Flat entry** (has `content_file`): the entry's `summary_text` field IS the summary — already loaded with the manifest.
   - **Wrapped entry** (has `summary`, `index`): read the `_summary.md` file referenced.
3. **Decide which supplements are relevant** to this question:
   - **Always-load** (any rules question): every flat `kind: rules-supplement` (combat, spellcasting, items-and-loot, character-sheets, npc-generation, campaign-generation, etc.) — these are house rules / homebrew that override RAW.
   - **Topical match** for any other supplement whose `summary_text` / `_summary.md` mentions keywords from the question.
   - **Campaign-relevance** (if active campaign): every `kind: character-backstory` and `kind: homebrew-mechanic` entry — these are campaign-specific context that affects rulings.
4. **For wrapped entries judged relevant**: read the `_index.md`. From the index, identify the specific content file(s) (chapter, section, NPC entry) most relevant to the question. Load **only those files**, not the whole supplement.
5. **For flat entries judged relevant**: read the full `content_file`.

This avoids loading 16,000+ lines of an adventure book to answer "what's the AC of plate?". A rules question about plate triggers global flat-supplement loads (a few hundred lines) plus the SRD equipment file — not the campaign book.

---

## Step 4: Load Campaign-Specific Files (if active campaign found)

Also load:

1. `DND-Campaign-Manager/campaigns/{campaign-slug}/campaign.json`
2. If the question references a specific player by name, read their file from `players/`.
3. If the question references an NPC by name, read their file from `npcs/`.
4. If the question references a location, NPC, or quest from the active book, the wrapped-entry index in Step 3 should have surfaced the right chapter file already — load it.

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
