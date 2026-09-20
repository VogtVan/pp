---
name: pp-authoring
description: >-
  Write front matter SECTIONs by script, never by hand: get, set, add or remove any conducted-document key while untouched content stays byte-for-byte; write constraints from their TEXT alone as the script inventories declared codes and derives collision-free ones. Deterministic, atomic, budget-guarded.
---

# `pp-authoring` — the sections' base, one writer

## What it is

A **local, deterministic script**: the sole writer of front matter sections. Edits are SURGICAL — only the targeted key's span moves; every other line stays untouched rather than re-emitted, making round-trips byte-stable. Multi-line values use block scalar (`key: |`); a single line stays inline when the engine reader reads it back as written, and is written double-quoted otherwise (`a: b`, `yes`, `#`) — what is written is what is read.

## How to call it

```
./pp <key> -s pp-authoring section get <doc> <key>
./pp <key> -s pp-authoring section set <doc> <key>       (value on stdin)
./pp <key> -s pp-authoring section add <doc> <key>       (value on stdin)
./pp <key> -s pp-authoring section remove <doc> <key>
./pp <key> -s pp-authoring section constrain <doc> [<prefix>] --section production|behavior
                                                         (law texts on stdin, one per line)
./pp <key> -s pp-authoring section serve <doc> <token ...>   (one grouping row appended)
./pp <key> -s pp-authoring section serve <doc> -             (the whole section, rows on stdin)
```

`section` is the group the package's writer answers to: the verb follows it, and
the package keeps room for the writers its other crafts will ask for.

`serve` writes a framing's READINGS, one grouping per line — useful node references and, for a batch, touched/dependent code. Tokens may carry useful ranges, `<name>[x-y,...,u-v]`: 1-based, ascending, disjoint, ordered, and validated exactly like the engine (`serve-range-malformed` on both sides). Without ranges, a line is byte-identical to hand-written form. A token row appends to the LAST section; piped `-` writes the whole block preserving blanks. A blank line separates SECTIONS; bare SERVE plays one whole section. A section is a DECLARATION: mounts play every line on plan nodes; on `proc:` documents it plays only on a bare `SERVE` in that procedure — write section and moment together (`set <doc> proc`, procedure on stdin, one SERVE per section at its head).

`<doc>` is relative to the instance root or absolute. A serve TOKEN resolves like the engine: bare name in the instance, then packages (package ref by name), then the member repo root (`README.md`, `design/target.md`). `constrain` is the law writer: provide texts only; it scans all declared instance codes, vendored and local (the build collision-lint universe), continues the prefix beyond every taken code, writes the block, and SAYS the attributed codes. Name the prefix yourself or let it derive from the document slug.

## Guards (exit 2, nothing written)

- `document-missing` · `frontmatter-missing` — the target must exist;
- `key-unknown` · `key-taken` · `key-invalid` — the CRUD's own borders;
- `value-malformed` · `budget` — an empty value writes nothing; each line stays under 500 characters;
- `token-invalid` · `serve-range-malformed` — a serve token is one name with glued, lawful ranges;
- run outside an installed instance refuses — there is nowhere to write.

## What you never do

- You never edit a front matter section by hand — this script is the one writer of the sections.
- You never choose a constraint code — the text is yours, the code is the script's.
