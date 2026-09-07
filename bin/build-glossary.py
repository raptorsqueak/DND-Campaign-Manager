#!/usr/bin/env python3
"""Build a Whisper decode prompt and a name-correction roster for one campaign.

Whisper confidently mangles proper nouns it has never seen. Two things fix that,
and this script produces both:

  decode-prompt.txt  a short glossary fed to the decoder via --prompt. Whisper only
                     honours roughly 224 tokens of prompt, so this holds the names in
                     *current rotation* only: the party, plus NPCs and places that
                     show up in campaign.json or the recent session log.

  roster.json        every name in the campaign, with aliases, for the post-decode
                     correction pass (bin/correct-names.py). The full roster is the
                     asset here -- a bigger model with no glossary still gets these wrong.

Reads only from the campaign folder at runtime; nothing campaign-specific is baked in.

Usage:
    python3 bin/build-glossary.py --campaign example-campaign
    python3 bin/build-glossary.py                      # auto-detects a lone campaign
    python3 bin/build-glossary.py --extra "Annam, Uthgardt"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Titles that precede a name; the bare name is also worth matching on.
TITLES = {
    "king", "queen", "prince", "princess", "lord", "lady", "captain", "commander",
    "guildmaster", "master", "mistress", "sir", "dame", "father", "mother", "chief",
    "great", "high", "archmage", "baron", "baroness", "duke", "duchess", "the",
}

# Words that look like names at a sentence start but aren't. Keeps the auto-detected
# place-name sweep from filling the prompt budget with noise.
NOT_NAMES = {
    "the", "a", "an", "and", "but", "or", "if", "when", "while", "after", "before",
    "he", "she", "they", "it", "his", "her", "their", "its", "this", "that", "these",
    "those", "there", "here", "then", "now", "party", "session", "summary", "quest",
    "quests", "location", "loot", "items", "notes", "progress", "completed", "dm",
    "npc", "npcs", "player", "players", "combat", "damage", "level", "chapter",
    "book", "campaign", "in", "in-game", "on", "at", "to", "from", "with", "for",
    "not", "no", "yes", "one", "two", "three", "four", "five", "six", "seven",
    "roll", "rolled", "save", "check", "attack", "spell", "round", "turn", "hit",
    "both", "every", "each", "all", "any", "some", "still", "first", "last", "next",
    # Structural words from the session log and campaign.json -- not proper nouns.
    "none", "game", "date", "interactions", "updates", "ruling", "rulings",
    "homebrew", "corrected", "carry", "map", "room", "area", "trap", "sack",
    "party", "awaiting", "sphere", "statue", "walls", "init", "initiative",
}

PROMPT_CHAR_BUDGET = 800  # ~224 tokens of comma-separated proper nouns


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def resolve_campaign(slug: str | None) -> Path:
    root = REPO / "campaigns"
    if not root.is_dir():
        die("no campaigns/ directory")
    if slug:
        path = root / slug
        if not path.is_dir():
            die(f"no such campaign: {slug}")
        return path
    dirs = [d for d in sorted(root.iterdir()) if d.is_dir() and (d / "campaign.json").exists()]
    if len(dirs) == 1:
        return dirs[0]
    die("pass --campaign (found %d campaigns)" % len(dirs))


def heading_name(md: Path) -> str | None:
    """The `# Name` heading of a character file, falling back to the filename."""
    try:
        for line in md.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            if line and not line.startswith("#"):
                break
    except OSError:
        return None
    return md.stem.replace("-", " ").title()


def aliases_for(name: str) -> list[str]:
    """Canonical form plus the fragments a transcript is likely to contain."""
    out = {name}
    words = [w for w in re.split(r"[\s]+", name) if w]
    # Strip leading titles: "Captain Roenor" -> "Roenor"
    stripped = [w for w in words if w.lower().strip(",") not in TITLES]
    if stripped and stripped != words:
        out.add(" ".join(stripped))
    # Individual significant words: "Harshnag the Grim" -> "Harshnag", "Grim"
    for w in stripped:
        w = w.strip(",.'\"")
        if len(w) >= 4 and w[0].isupper():
            out.add(w)
    return sorted(out, key=lambda s: (-len(s), s))


def collect(directory: Path, kind: str) -> list[dict]:
    if not directory.is_dir():
        return []
    entries = []
    for md in sorted(directory.glob("*.md")):
        name = heading_name(md)
        if not name:
            continue
        entries.append({"canonical": name, "kind": kind, "aliases": aliases_for(name)})
    return entries


def recent_text(campaign: Path, log_lines: int) -> str:
    """campaign.json state plus the tail of the session log -- i.e. what is in play now."""
    chunks = []
    cj = campaign / "campaign.json"
    if cj.exists():
        try:
            data = json.loads(cj.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            die(f"campaign.json is not valid JSON: {exc}")
        for key in ("current_location", "book", "setting", "custom_notes"):
            if isinstance(data.get(key), str):
                chunks.append(data[key])
        for quest in data.get("active_quests") or []:
            if isinstance(quest, str):
                chunks.append(quest)
    log = campaign / "session-log.md"
    if log.exists():
        tail = log.read_text(encoding="utf-8").splitlines()[-log_lines:]
        chunks.append("\n".join(tail))
    return "\n".join(chunks)


def sweep_proper_nouns(text: str, known: set[str], limit: int) -> list[str]:
    """Capitalized runs that aren't already roster names -- mostly place names."""
    counts: dict[str, int] = {}
    # Capitalized runs, optionally joined by lowercase connectors, so
    # "Eye of the All-Father" survives as one phrase rather than "Eye".
    pattern = r"\b([A-Z][A-Za-z'’-]{2,}(?:(?:\s+(?:of|the|and))*\s+[A-Z][A-Za-z'’-]{2,})*)\b"
    for match in re.finditer(pattern, text):
        phrase = re.sub(r"\s+", " ", match.group(1).strip(" -"))
        phrase = re.sub(r"[’']s$", "", phrase)  # "Annam's" and "Annam" are one term
        if phrase.isupper():                     # shouted log markers, not names
            continue
        parts = phrase.split()
        head = parts[0].lower()
        if head in NOT_NAMES or phrase.lower() in known:
            continue
        if len(parts) == 1 and head in NOT_NAMES:
            continue
        if any(part.lower() in known for part in parts):
            continue
        counts[phrase] = counts.get(phrase, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [phrase for phrase, _ in ranked[:limit]]


def build_prompt(terms: list[str], budget: int) -> str:
    """Comma-separated, truncated to the decoder's prompt budget."""
    kept: list[str] = []
    length = 0
    for term in terms:
        add = len(term) + 2
        if length + add > budget:
            break
        kept.append(term)
        length += add
    return ", ".join(kept)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", help="campaign slug (auto-detected if only one exists)")
    ap.add_argument("--out", help="output directory (default: campaigns/{slug}/.transcript-working/glossary)")
    ap.add_argument("--extra", default="", help="comma-separated extra terms to force into the prompt")
    ap.add_argument("--log-lines", type=int, default=250, help="lines of session-log.md tail to scan (default 250)")
    ap.add_argument("--places", type=int, default=14, help="max auto-detected place names (default 14)")
    ap.add_argument("--budget", type=int, default=PROMPT_CHAR_BUDGET, help="decode prompt char budget")
    args = ap.parse_args()

    campaign = resolve_campaign(args.campaign)
    slug = campaign.name

    players = collect(campaign / "players", "player")
    npcs = collect(campaign / "npcs", "npc")
    if not players and not npcs:
        die(f"no character files under {campaign}/players or {campaign}/npcs")

    roster = players + npcs
    known = {a.lower() for e in roster for a in e["aliases"]}

    context = recent_text(campaign, args.log_lines)
    ctx_lower = context.lower()

    # Everyone the players play is always in rotation.
    active = [e["canonical"] for e in players]
    # NPCs only if they are actually current -- the prompt budget is small.
    for entry in npcs:
        if any(a.lower() in ctx_lower for a in entry["aliases"]):
            active.append(entry["canonical"])

    places = sweep_proper_nouns(context, known, args.places)
    extra = [t.strip() for t in args.extra.split(",") if t.strip()]

    terms = extra + active + places
    seen, ordered = set(), []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            ordered.append(t)

    prompt = build_prompt(ordered, args.budget)

    out_dir = Path(args.out) if args.out else campaign / ".transcript-working" / "glossary"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "decode-prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    (out_dir / "roster.json").write_text(
        json.dumps(
            {
                "campaign": slug,
                "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entries": roster,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    dropped = len(ordered) - len(prompt.split(", ")) if prompt else len(ordered)
    print(f"campaign      : {slug}")
    print(f"roster        : {len(players)} players + {len(npcs)} NPCs = {len(roster)} entries")
    print(f"in rotation   : {len(active)} characters + {len(places)} places" + (f" + {len(extra)} manual" if extra else ""))
    print(f"decode prompt : {len(prompt)}/{args.budget} chars" + (f"  ({dropped} term(s) dropped over budget)" if dropped > 0 else ""))
    print(f"written       : {out_dir}/decode-prompt.txt")
    print(f"                {out_dir}/roster.json")
    if places:
        print(f"places seen   : {', '.join(places)}")


if __name__ == "__main__":
    main()
