# Proposal Contract

The JSON every write-proposing agent (`player-data`, `npc-data`, `campaign-state`,
`session-recorder`) returns, and that the orchestrator applies.

**Core rule: proposals address content, never bytes.** A proposal names a heading, a line
prefix, or a JSON field. It never reproduces existing file content. `bin/apply-proposal.py`
resolves the address against the file on disk and does the edit.

This replaced an earlier `old_string` / `new_string` contract that required the agent to
reproduce existing file bytes exactly. That worked, but it made every write depend on verbatim
recall, failed silently on whitespace drift, and was the single least portable thing in the
project. Addressing is also more legible in a confirmation prompt: *"append to `## Pets`"* reads
better than a wall of bytes.

---

## Shape

```json
{
  "proposals": [
    {
      "file": "campaigns/{slug}/players/{name}.md",
      "operation": "append-to-section",
      "target": { "section": "## Pets" },
      "content": "- **Whiskers** — Tressym, rides on her shoulder.",
      "stake_level": "low",
      "confidence": 0.95,
      "summary": "lyra.md → Pets: added Whiskers",
      "rationale": "why this file and this section"
    }
  ],
  "questions": [
    { "context": "what was ambiguous", "ask": "specific question to put to the user" }
  ],
  "no_action_reason": "string, only when proposals and questions are both empty"
}
```

`summary`, `rationale`, `stake_level`, and `confidence` are unchanged from before.
`stake_level: low` auto-applies; `high` batches for end-of-turn confirmation.

---

## Operations

### Markdown files

| Operation | Addresses with | `content` is |
|---|---|---|
| `append-to-section` | `target.section` | lines added at the end of that section |
| `replace-section` | `target.section` | the section's entire new body (heading kept) |
| `insert-section` | `target.section` (the **new** heading, with `#` marks) + `target.after_section` | the new section's body |
| `replace-line` | `target.match` (line prefix) + optional `target.section` to scope it | the replacement line(s) |
| `append-to-file` | — | lines added at end of file |
| `create-file` | — | the whole file |

### JSON files (`campaign.json`)

| Operation | Addresses with | Carries |
|---|---|---|
| `set-field` | `target.field` (dot path, e.g. `party_level`) | `value` — any JSON value |
| `array-append` | `target.field` | `value` — the element to add (no-op if already present) |
| `array-remove` | `target.field` | `value` — exact match, else unique prefix match |

JSON edits go through a real parser and re-serialize with 2-space indent. No comma surgery, no
byte matching, no risk of producing invalid JSON.

---

## Addressing rules

**`target.section`** — the heading text. Matching ignores case and `#` marks, so `## Pets`,
`Pets`, and `pets` all resolve to the same heading. The section runs to the next heading of the
same or higher level. A heading that appears twice in one file is an error, not a guess.

**`target.match`** — a prefix of the line's *stripped* text, e.g. `- **HP**:`. It must match
exactly one line. If it matches several, the applier says so and names the count; lengthen the
prefix or add `target.section` to scope it. Never pass a whole line as the prefix — the point is
that you do not need to know the rest of it.

**`target.after_section`** — for `insert-section` only: the existing heading the new section goes
after. Use it to keep files in canonical schema order. Omit it (or pass `"(top)"`) to insert
before the first heading.

**Paths** are repo-relative and may not contain `..`. Absolute paths are rejected — they leak the
filesystem tree into a proposal that may end up in a log.

---

## Applying

```bash
bin/apply-proposal.py --dry-run < proposal.json   # unified diff, writes nothing
bin/apply-proposal.py < proposal.json             # apply
bin/apply-proposal.py --input batch.json          # a whole agent response, in order
```

It accepts a single proposal object, a bare array, or a full agent response with a
`proposals` key. Exit `0` applied, `1` addressing failed, `2` malformed input. On failure it
prints what went wrong and what to do about it, and leaves the file untouched.

**Orchestrator flow:**

1. Collect proposals from the agents.
2. Apply `stake_level: low` immediately: pipe the proposal to `bin/apply-proposal.py`.
3. Batch `stake_level: high` into one confirmation prompt. On `review`, run `--dry-run` per
   proposal to show the diff.
4. If the applier exits non-zero, **do not fall back to hand-editing.** The addressing failed for
   a reason — a missing section, an ambiguous prefix. Re-invoke the agent with the error message
   so it can re-address, or ask the user.
5. Reverting is re-addressing, not an inverse byte swap: propose the opposite change against the
   same target.

If the script cannot be run at all, resolve the address by reading the file and use the Edit
tool — but the script is the intended path, because it is the one that behaves identically on
every model.

---

## Why this is also the porting seam

`bin/apply-proposal.py` is stdlib-only and knows nothing about any model or harness. When the
runtime in `docs/llm-portability-plan.md` gets built, it imports this module rather than
reimplementing it, and the contract above becomes the JSON schema handed to structured outputs.
The write path is already provider-independent.
