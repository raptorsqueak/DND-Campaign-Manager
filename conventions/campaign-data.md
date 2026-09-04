# Campaign Data

Rules for writing to campaign files — NPCs, players, supplements, and the vault.

---

## Check for name variants before creating an NPC file

Before creating a file in `campaigns/{slug}/npcs/`, search for variants of the name in **both**
the project `npcs/` directory and the vault's `NPCs/` tree. Prefer updating an existing file over
minting a new one.

Search for:
- The name with and without titles — King, Queen, Lord, Captain, Guildmaster, "the Grim"
- First name alone, last name alone, the full hyphenated form
- Nicknames and aliases used in the session log

```bash
ls campaigns/{slug}/npcs/ | grep -i "{rootname}"
find "{vault}/NPCs/" -iname "*{rootname}*"
```

If any variant exists, update it. If your draft's naming differs from the existing file, rename
your draft to match — the vault filename (`Harshnag the Grim.md`) usually dictates the canonical
form, and the project filename is its hyphen-cased version (`harshnag-the-grim.md`).

**Why:** an NPC file was created for a book character at the moment they appeared in play, without
noticing that a file under their full title already existed, pre-staged during earlier chapter
prep. Two files, divergent content, and a duplicate to untangle before the next sync.

---

## Check the book for a quest payoff before inventing a reason to travel

When planning a session that takes the party to a named location from the adventure book, check
whether an earlier questgiver already sent them there. Published adventures routinely seat
chapter-two quests at chapter-three destinations, with canonical rewards attached.

Before drafting the reception scene at a destination:

1. Read the book supplement's `_index.md` Quests / Hooks table for anything tied to that location.
2. Read any vault notes the DM has already written for that destination.
3. Check project NPC files for the questgivers who send parties there, to see whether the party
   has that quest in hand.
4. Use the **canonical book NPCs** at the destination — read the chapter file. Do not substitute
   names from adjacent lore for the region.

If a quest payoff exists, the scene centres on that payoff first; intel-sharing and faction beats
wrap around it. The canonical reward replaces any speculative magic item the assistant might
otherwise suggest.

**Why:** a session was planned around a generic invented motive for visiting a city, when the
party was actually carrying a letter of recommendation from a previous chapter's questgiver and
was owed a specific published reward. The rulers of the city were also invented, when the book
names them. Both had to be corrected.

---

## Ground details in the files before writing them

Before writing about a campaign element — a pet, a location, an NPC's history — read the player
files, NPC files, and session log. Do not write from recollection of the conversation.

**Why:** a plan described a pet doing something the creature's own file makes clear it would never
do, and placed it somewhere the last session log says it is not.

Related, and stronger: **never invent or extend a PC's lore.** Family, ancestors, mentors,
institutions, titles, hometown detail — those belong to the player and the DM. If asked to produce
narrative material about a PC's past, draft it in the reply for the DM to react to; do not write it
into `## Backstory` until the DM states it. And never re-attribute existing lore to a different
person — a one-generation slip silently rewrites a character's family history.

---

## Supplement layout: wrap only large content

The three-tier layout (`{slug}/_summary.md` + `_index.md` + content) is for **large reference
content only** — adventure books, or substantive rules supplements past roughly 300 lines.

- Small single-topic files (a house-rules page, a party backstory, a one-mechanic writeup) stay
  **flat**, registered in the manifest with `content_file` and an inline `summary_text`. Wrapping
  a 121-line file in a summary and an index costs more tokens than it saves and adds no
  findability.
- **Session-prep notes are not supplements.** A file named like `2026-05-01 To Yartar.md` is a
  planning artifact and belongs in `sessions/`, not in `supplements/`. Do not let consumers load
  it as reference material.
- When unsure where a file belongs, ask before restructuring.

---

## Mirror DM book state into the vault on sync

`/sync-obsidian` should also mirror each `campaigns/{slug}/supplement-state/{book}.md` to
`{vault}/Campaign/{Book}/_DM State.md`. Surface it as a normal sync step, not as an extra ask
afterwards.

- Match the book folder name the DM already uses for chapter prep in the vault.
- The `_` prefix sorts it to the top of the book folder.
- Header line: `*Mirror of \`campaigns/{slug}/supplement-state/{book}.md\` — refreshed via
  /sync-obsidian. Project source remains canonical.*`
- Convert PC and NPC names to `[[Name]]` wikilinks, including unresolved canonical book names.
- Overwrite on each sync — it is a pure mirror. If the DM has hand-edited it, ask first.

**Why:** the command spec covers players, NPCs, sessions, and items, but not book state — and the
DM keeps book progress visible at the table through the vault.
