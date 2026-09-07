#!/usr/bin/env python3
"""Fuzzy-correct proper nouns in a Whisper transcript against a campaign roster.

Whisper's decode prompt only biases ~224 tokens, so it will still emit "Harsh Nag",
"Claw Nex", "Worm Blood". This pass runs the *full* roster (every file in players/
and npcs/) over the finished transcript and repairs what the prompt could not reach.

Deliberately conservative, and every substitution is logged -- a wrong correction that
happens silently is worse than a misspelling that stays visible.

Usage:
    python3 bin/correct-names.py transcript.txt --roster .../roster.json
    python3 bin/correct-names.py transcript.txt --roster r.json -o fixed.txt --threshold 0.88
    python3 bin/correct-names.py transcript.txt --roster r.json --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

# Common English words that fuzzy-match short names too easily. A candidate in this
# set is never corrected, regardless of score.
COMMON = {
    "about", "above", "after", "again", "against", "already", "alright", "always",
    "another", "answer", "anyone", "anything", "around", "because", "before",
    "behind", "being", "better", "between", "cannot", "could", "course", "different",
    "doing", "don't", "double", "enough", "every", "everyone", "everything", "first",
    "found", "friend", "getting", "going", "gonna", "great", "guess", "happen",
    "happened", "having", "hundred", "inside", "instead", "little", "looking",
    "makes", "making", "maybe", "mean", "might", "minute", "moment", "money",
    "nothing", "number", "okay", "other", "people", "perfect", "place", "point",
    "probably", "quite", "really", "right", "rolled", "rolling", "second", "seems",
    "should", "something", "sorry", "sound", "start", "still", "stuff", "sure",
    "take", "taking", "thanks", "their", "there", "these", "thing", "think",
    "those", "though", "thought", "three", "through", "together", "tonight",
    "trying", "turn", "twenty", "under", "until", "wait", "wanna", "want", "watch",
    "where", "which", "while", "whole", "would", "yeah", "years",
    # Every word below caused a real false positive on a live session transcript:
    # Back->Black, Then->Tharn, Fine->Fiona, Usually->Sally, Tastes->Toast, Stories->Story.
    "back", "then", "fine", "usually", "tastes", "taste", "stories", "blocked",
    "block", "isle", "aisle", "also", "always", "away", "black", "bring", "call",
    "came", "come", "does", "done", "down", "even", "ever", "from", "give", "good",
    "hall", "hand", "have", "head", "help", "here", "into", "just", "keep", "kind",
    "know", "last", "left", "like", "look", "made", "make", "many", "more", "most",
    "move", "much", "must", "need", "next", "once", "only", "open", "over", "part",
    "past", "play", "pull", "push", "read", "real", "rest", "room", "said", "same",
    "seen", "send", "side", "some", "stop", "such", "sure", "tell", "than", "that",
    "them", "they", "this", "time", "told", "took", "turn", "used", "very", "wall",
    "well", "went", "were", "what", "when", "will", "with", "work", "your",
    # Table vocabulary that must never be reshaped into a character name.
    "attack", "advantage", "armor", "bonus", "charisma", "check", "constitution",
    "critical", "damage", "dexterity", "disadvantage", "fireball", "initiative",
    "intelligence", "magic", "paladin", "ranger", "reaction", "rogue", "saving",
    "spell", "strength", "throw", "wisdom", "wizard",
}


VOWELS = str.maketrans("", "", "aeiouy'’- ")


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def skeleton(word: str) -> str:
    """Consonant skeleton -- 'Kayl' and 'Kael' both reduce to 'kl'.

    Edit distance alone cannot connect short names whose vowels were misheard, which is
    exactly the common Whisper failure on a 4-6 letter name.
    """
    return word.lower().translate(VOWELS)


def load_aliases(roster_path: Path, min_len: int) -> dict[str, tuple[str, str, bool]]:
    """alias (lowercased) -> (alias as written, canonical name, is_fragment).

    Substitution uses the *alias* spelling, not the canonical one: a transcript that
    says "Harsh Nag" should become "Harshnag", not "Harshnag the Grim".
    """
    try:
        data = json.loads(roster_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"error: cannot read roster {roster_path}: {exc}")
    table: dict[str, tuple[str, str, bool]] = {}
    for entry in data.get("entries", []):
        canonical = entry.get("canonical")
        if not canonical:
            continue
        for alias in entry.get("aliases", []):
            key = alias.lower()
            if len(key.replace(" ", "")) < min_len:
                continue
            # A single word taken out of a multi-word name ("Black" from "Black Cat")
            # is a weak alias: it collides with ordinary speech far more readily than
            # a full name does, so it is held to a stricter standard below.
            fragment = " " not in alias.strip() and " " in canonical.strip()
            if key not in table or len(canonical) > len(table[key][1]):
                table[key] = (alias, canonical, fragment)
    return table


def best_match(candidate: str, aliases: dict[str, tuple[str, str, bool]], threshold: float) -> tuple[str, str, float] | None:
    """Closest alias to `candidate`, comparing with and without internal spaces.

    The space-stripped comparison is what catches Whisper splitting one name into
    two words ("Harsh Nag" -> "Harshnag").
    """
    cand = candidate.lower()
    cand_tight = cand.replace(" ", "").replace("-", "")
    best: tuple[str, str, float] | None = None
    for alias, (display, canonical, fragment) in aliases.items():
        alias_tight = alias.replace(" ", "").replace("-", "")
        # Cheap length gate before the expensive comparison.
        if abs(len(cand_tight) - len(alias_tight)) > 3:
            continue
        score = max(ratio(cand, alias), ratio(cand_tight, alias_tight))
        if fragment:
            # No phonetic rescue for name fragments, and a higher bar on edit distance.
            accept = score >= threshold + 0.06
        else:
            # Second path: vowels misheard but the consonant spine survived.
            skel = ratio(skeleton(cand_tight), skeleton(alias_tight))
            accept = score >= threshold or (skel >= 0.85 and score >= 0.65)
        if accept and (best is None or score > best[2]):
            best = (display, canonical, score)
    return best


ARGS_MIN_CANDIDATE = 4


def correct(text: str, aliases: dict[str, tuple[str, str, bool]], threshold: float, max_words: int) -> tuple[str, list[tuple[str, str, float]]]:
    exact = set(aliases)
    words = list(re.finditer(r"[A-Za-z][A-Za-z'’-]*", text))
    out: list[str] = []
    changes: list[tuple[str, str, float]] = []
    cursor = 0   # index into `text`
    i = 0        # index into `words`

    while i < len(words):
        match = None
        # Prefer the longest n-gram, so a two-word name wins over its first word.
        for span in range(min(max_words, len(words) - i), 0, -1):
            start, end = words[i].start(), words[i + span - 1].end()
            candidate = text[start:end]
            if "\n" in candidate:
                continue
            key = candidate.lower()
            bare, suffix = re.subn(r"[’']s$", "", key)[0], ""
            if bare != key:
                suffix = candidate[len(candidate) - 2:]  # keep "'s" / "’s" intact
                key = bare
            if candidate.split()[0].lower() in {"the", "a", "an"}:
                continue  # "The Isle" is prose, not a name
            if key in exact or key in COMMON:
                break  # already correct, or a word we refuse to touch
            if len(candidate.replace(" ", "")) < ARGS_MIN_CANDIDATE:
                continue
            if not candidate[0].isupper():
                continue  # names are capitalized; prose starting lowercase is not one
            if any(w.lower() in COMMON for w in candidate.split()):
                continue  # never absorb an ordinary word into a name
            if span > 1 and not all(w[:1].isupper() for w in candidate.split()):
                continue  # a split name is capitalized throughout ("Harsh Nag")
            hit = best_match(key, aliases, threshold)
            if hit:
                match = (start, end, candidate, hit[0] + suffix, hit[1], hit[2], span)
                break
        if match:
            start, end, candidate, display, canonical, score, span = match
            out.append(text[cursor:start])
            out.append(display)
            changes.append((candidate, display, score))
            cursor = end
            i += span
        else:
            i += 1

    out.append(text[cursor:])
    return "".join(out), changes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript", help="transcript text file to correct")
    ap.add_argument("--roster", required=True, help="roster.json from bin/build-glossary.py")
    ap.add_argument("-o", "--output", help="output file (default: overwrite the transcript in place)")
    ap.add_argument("--threshold", type=float, default=0.82, help="similarity 0-1 required to correct (default 0.82)")
    ap.add_argument("--min-alias", type=int, default=5, help="ignore roster aliases shorter than this (default 5)")
    ap.add_argument("--max-words", type=int, default=3, help="longest n-gram to test (default 3)")
    ap.add_argument("--dry-run", action="store_true", help="report substitutions without writing")
    args = ap.parse_args()

    src = Path(args.transcript)
    if not src.exists():
        sys.exit(f"error: no such transcript: {src}")

    aliases = load_aliases(Path(args.roster), args.min_alias)
    if not aliases:
        sys.exit("error: roster contained no usable aliases")

    text = src.read_text(encoding="utf-8")
    fixed, changes = correct(text, aliases, args.threshold, args.max_words)

    tally: dict[tuple[str, str], list[float]] = {}
    for was, now, score in changes:
        tally.setdefault((was, now), []).append(score)

    print(f"roster aliases : {len(aliases)}")
    print(f"substitutions  : {len(changes)} ({len(tally)} distinct)")
    for (was, now), scores in sorted(tally.items(), key=lambda kv: -len(kv[1])):
        print(f"  {was!r} -> {now!r}  ×{len(scores)}  (best {max(scores):.2f})")

    if args.dry_run:
        print("dry run -- nothing written")
        return

    dest = Path(args.output) if args.output else src
    dest.write_text(fixed, encoding="utf-8")
    log = dest.with_suffix(dest.suffix + ".corrections.tsv")
    with log.open("w", encoding="utf-8") as fh:
        fh.write("heard\tcorrected\tcount\tbest_score\n")
        for (was, now), scores in sorted(tally.items()):
            fh.write(f"{was}\t{now}\t{len(scores)}\t{max(scores):.3f}\n")
    print(f"written        : {dest}")
    print(f"corrections log: {log}")


if __name__ == "__main__":
    main()
