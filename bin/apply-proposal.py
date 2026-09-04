#!/usr/bin/env python3
"""Apply a section-addressed proposal to a campaign file.

Reads one proposal (or a JSON array of proposals) from stdin or --input and applies
it deterministically. Proposals address a heading, a line prefix, or a JSON field --
never raw file bytes -- so the model never has to reproduce existing content exactly.

Usage:
    bin/apply-proposal.py --dry-run < proposal.json     # show a diff, change nothing
    bin/apply-proposal.py < proposal.json               # apply
    bin/apply-proposal.py --input proposals.json        # apply a batch, in order

Exit codes:
    0  applied (or dry-run produced a clean diff)
    1  addressing failed -- heading missing, prefix matched zero or many lines, bad path
    2  malformed proposal

Stdlib only, no dependencies. See docs/proposal-contract.md for the contract.
"""

import argparse
import difflib
import json
import os
import re
import sys

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

MARKDOWN_OPS = {
    "append-to-section",
    "replace-section",
    "insert-section",
    "replace-line",
    "append-to-file",
    "create-file",
}
JSON_OPS = {"set-field", "array-append", "array-remove"}


class ProposalError(Exception):
    """Addressing or validation failure. Message is shown to the user verbatim."""


# ---------------------------------------------------------------- helpers


def normalize_heading(text):
    """'## Pets' and 'pets' both normalize to 'pets'."""
    return text.lstrip("#").strip().casefold()


def find_section(lines, heading):
    """Return (heading_index, body_start, body_end) for a heading.

    body_end is exclusive and stops at the next heading of the same or higher
    level (fewer or equal '#'), or end of file.
    """
    want = normalize_heading(heading)
    matches = []
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and normalize_heading(m.group(2)) == want:
            matches.append((i, len(m.group(1))))

    if not matches:
        raise ProposalError(
            f"section {heading!r} not found. Headings present: "
            + ", ".join(repr(m.group(2)) for m in
                        (HEADING_RE.match(l) for l in lines) if m)
        )
    if len(matches) > 1:
        raise ProposalError(
            f"section {heading!r} appears {len(matches)} times; "
            "narrow it or use replace-line with a match prefix"
        )

    idx, level = matches[0]
    end = len(lines)
    for j in range(idx + 1, len(lines)):
        m = HEADING_RE.match(lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    return idx, idx + 1, end


def trim_trailing_blanks(lines, start, end):
    """Walk back past trailing blank lines in [start, end); return new end."""
    while end > start and not lines[end - 1].strip():
        end -= 1
    return end


def as_lines(content):
    """Split proposal content into lines without trailing empties."""
    return content.rstrip("\n").split("\n") if content else []


def dotted_get(obj, path):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            part = int(part)
        elif part not in cur:
            raise ProposalError(f"field {path!r} not found in JSON (missing {part!r})")
        cur = cur[part]
    return cur


def dotted_set(obj, path, value):
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            if part not in cur:
                raise ProposalError(f"field {path!r} not found in JSON (missing {part!r})")
            cur = cur[part]
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


# ---------------------------------------------------------------- markdown ops


def apply_markdown(text, prop):
    op = prop["operation"]
    target = prop.get("target") or {}
    content = prop.get("content", "")
    lines = text.split("\n")

    if op == "append-to-file":
        body = trim_trailing_blanks(lines, 0, len(lines))
        return "\n".join(lines[:body] + [""] + as_lines(content)) + "\n"

    if op == "replace-line":
        match = target.get("match")
        if not match:
            raise ProposalError("replace-line requires target.match")
        lo, hi = 0, len(lines)
        if target.get("section"):
            _, lo, hi = find_section(lines, target["section"])
        hits = [i for i in range(lo, hi) if lines[i].strip().startswith(match)]
        if not hits:
            where = f" within {target['section']!r}" if target.get("section") else ""
            raise ProposalError(f"no line starting with {match!r}{where}")
        if len(hits) > 1:
            raise ProposalError(
                f"{len(hits)} lines start with {match!r}; lengthen the prefix "
                "or scope it with target.section"
            )
        new = list(lines)
        new[hits[0] : hits[0] + 1] = as_lines(content)
        return "\n".join(new)

    if op == "append-to-section":
        if not target.get("section"):
            raise ProposalError("append-to-section requires target.section")
        _, body_start, body_end = find_section(lines, target["section"])
        insert_at = trim_trailing_blanks(lines, body_start, body_end)
        new = lines[:insert_at] + as_lines(content) + lines[insert_at:]
        return "\n".join(new)

    if op == "replace-section":
        if not target.get("section"):
            raise ProposalError("replace-section requires target.section")
        _, body_start, body_end = find_section(lines, target["section"])
        new = lines[:body_start] + as_lines(content) + [""] + lines[body_end:]
        return "\n".join(new)

    if op == "insert-section":
        heading = target.get("section")
        if not heading:
            raise ProposalError("insert-section requires target.section (the new heading)")
        if not heading.lstrip().startswith("#"):
            raise ProposalError(
                f"insert-section target.section must include the '#' marks, got {heading!r}"
            )
        try:
            find_section(lines, heading)
        except ProposalError:
            pass
        else:
            raise ProposalError(
                f"section {heading!r} already exists; use append-to-section or replace-section"
            )

        after = target.get("after_section")
        if after in (None, "", "(top)"):
            at = 0
            for i, line in enumerate(lines):
                if HEADING_RE.match(line):
                    at = i
                    break
            block = [heading, ""] + as_lines(content) + [""]
        else:
            _, body_start, body_end = find_section(lines, after)
            at = trim_trailing_blanks(lines, body_start, body_end)
            block = ["", heading, ""] + as_lines(content)

        new = lines[:at] + block + lines[at:]
        return "\n".join(new)

    raise ProposalError(f"unknown markdown operation {op!r}")


# ---------------------------------------------------------------- json ops


def apply_json(text, prop):
    op = prop["operation"]
    target = prop.get("target") or {}
    field = target.get("field")
    if not field:
        raise ProposalError(f"{op} requires target.field")
    if "value" not in prop:
        raise ProposalError(f"{op} requires a 'value'")

    data = json.loads(text)
    value = prop["value"]

    if op == "set-field":
        dotted_set(data, field, value)
    elif op == "array-append":
        arr = dotted_get(data, field)
        if not isinstance(arr, list):
            raise ProposalError(f"field {field!r} is not an array")
        if value not in arr:
            arr.append(value)
    elif op == "array-remove":
        arr = dotted_get(data, field)
        if not isinstance(arr, list):
            raise ProposalError(f"field {field!r} is not an array")
        hits = [x for x in arr if x == value] or [
            x for x in arr if isinstance(x, str) and isinstance(value, str)
            and x.startswith(value)
        ]
        if not hits:
            raise ProposalError(f"no entry in {field!r} matching {value!r}")
        if len(hits) > 1:
            raise ProposalError(f"{len(hits)} entries in {field!r} match {value!r}")
        arr.remove(hits[0])
    else:
        raise ProposalError(f"unknown JSON operation {op!r}")

    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------- driver


def apply_one(prop, dry_run):
    for key in ("file", "operation"):
        if key not in prop:
            raise ProposalError(f"proposal is missing required key {key!r}")

    path = prop["file"]
    op = prop["operation"]
    if os.path.isabs(path) or ".." in path.split(os.sep):
        raise ProposalError(f"file must be a repo-relative path without '..', got {path!r}")

    if op == "create-file":
        if os.path.exists(path):
            raise ProposalError(f"{path} already exists; create-file will not overwrite")
        before, after = "", prop.get("content", "")
    else:
        if not os.path.exists(path):
            raise ProposalError(f"{path} does not exist")
        with open(path, encoding="utf-8") as fh:
            before = fh.read()
        if op in JSON_OPS:
            after = apply_json(before, prop)
        elif op in MARKDOWN_OPS:
            after = apply_markdown(before, prop)
        else:
            raise ProposalError(f"unknown operation {op!r}")

    if before == after:
        print(f"  no change: {path} ({op})")
        return

    if dry_run:
        diff = difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
        )
        sys.stdout.writelines(diff)
        return

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(after)
    print(f"  applied: {path} -- {prop.get('summary', op)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="JSON file to read (default: stdin)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print a unified diff instead of writing")
    args = ap.parse_args()

    raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON -- {exc}", file=sys.stderr)
        return 2

    if isinstance(payload, dict) and "proposals" in payload:
        proposals = payload["proposals"]
    elif isinstance(payload, dict):
        proposals = [payload]
    else:
        proposals = payload

    failures = 0
    for i, prop in enumerate(proposals, 1):
        try:
            apply_one(prop, args.dry_run)
        except ProposalError as exc:
            failures += 1
            print(f"error [{i}/{len(proposals)}] {prop.get('file', '?')}: {exc}",
                  file=sys.stderr)
        except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
            failures += 1
            print(f"error [{i}/{len(proposals)}] {prop.get('file', '?')}: "
                  f"{type(exc).__name__}: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
