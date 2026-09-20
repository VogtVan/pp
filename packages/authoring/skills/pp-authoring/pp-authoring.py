#!/usr/bin/env python3
"""DETERMINISTIC writer of front matter SECTIONS -- the base every specialized
script and every framing rests on: one call touches ONE key, everything
else travels VERBATIM, byte for byte.

The edit is SURGICAL: the document is split in lines, the targeted key's span
alone is replaced -- untouched keys are not re-emitted, they are simply never
touched. A multi-line value is a block scalar (`key: |` and its 2-space indented
lines); a single line is inline when the engine's reader reads it back as written,
double-quoted otherwise -- what is written is what is read.

  pp-authoring.py section get <doc> <key>          -> the value, block scalars dedented
  pp-authoring.py section set <doc> <key>          -> replaces the value (stdin)
  pp-authoring.py section add <doc> <key>          -> a new key at the front matter's end (stdin)
  pp-authoring.py section remove <doc> <key>       -> the key leaves, span and all
  pp-authoring.py section constrain <doc> [<prefix>] --section production|behavior
                                                   -> law TEXTS piped one per line, written in
                                                      the NAMED section (production: proven at
                                                      every checkpoint; behavior: served at every
                                                      block, never proven -- the section is said,
                                                      never guessed): the script inventories the
                                                      instance's declared codes, derives the free
                                                      ones and writes the block -- the agent
                                                      never chooses a code
  pp-authoring.py section serve <doc> <token ...>  -> ONE row appended to `serve:` -- a
                                                      token may carry line ranges,
                                                      `<name>[x-y,...,u-v]`, validated
                                                      exactly as the engine parses them
  pp-authoring.py section serve <doc> -            -> the whole `serve:` section replaced
                                                      by the rows piped one per line

Guards -- exit 2, nothing written: document-missing, frontmatter-missing,
key-unknown, key-taken, key-invalid, value-malformed, budget. Writes are atomic.

The conductor plays this skill: an agent reaches it as `./pp <key> -s pp-authoring section ...`,
and pp runs it with its own interpreter -- what the engine depends on, it may depend on.
"""
from __future__ import annotations

import sys
from pathlib import Path



def refuse(code: str, detail: str) -> None:
    sys.stderr.write(f"pp-authoring: {code} -- {detail}\n")
    raise SystemExit(2)


def home() -> Path:
    """-> the instance this vendored copy belongs to -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import home as walk                       # noqa: E402 -- the bootstrap
    found = walk(__file__)
    if found is None:
        refuse("not-an-instance", "not inside an installed instance -- nothing to write to")
    return found



def resolve(root: Path, spec: str) -> Path:
    path = (root / spec) if not Path(spec).is_absolute() else Path(spec)
    if not path.is_file():
        refuse("document-missing", f"{spec} names no document under the instance")
    return path


def piped_value(sections) -> list[str]:
    """-> the piped value, bounded by the library: the dispatch reads stdin, the library
    judges what it holds."""
    return sections.bounded(sys.stdin.read().splitlines())


def library():
    """-> the engine's front matter writer -- the ONE home of the span, the derived
    codes and the rows grammar; this script is its dispatch."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                  # noqa: E402 -- the bootstrap
    return core(__file__).sections


def main(argv: list[str]) -> int:
    """The dispatch: it reads stdin, calls the engine's writer, and TRANSLATES a raised
    refusal into the line this skill has always printed."""
    try:
        return dispatch(argv)
    except Exception as raised:
        if type(raised).__name__ != "Refusal":
            raise
        refuse(getattr(raised, "code", "refused"), str(raised).split(" — ", 1)[-1])


def dispatch(argv: list[str]) -> int:
    """`section` is the group this package's writer answers to; the verb follows it."""
    if len(argv) < 3 or argv[0] != "section":
        sys.stderr.write(__doc__)
        return 2
    verb, spec, rest = argv[1], argv[2], argv[3:]
    sections = library()
    root = home()
    path = resolve(root, spec)
    if verb == "get" and len(rest) == 1:
        print(sections.get(path, rest[0]))
    elif verb == "set" and len(rest) == 1:
        sections.edit(path, rest[0], piped_value(sections), create=False)
        print(f"pp-authoring: set -- {rest[0]} in {path.name}")
    elif verb == "add" and len(rest) == 1:
        sections.edit(path, rest[0], piped_value(sections), create=True)
        print(f"pp-authoring: added -- {rest[0]} in {path.name}")
    elif verb == "remove" and len(rest) == 1:
        sections.edit(path, rest[0], None, create=False)
        print(f"pp-authoring: removed -- {rest[0]} from {path.name}")
    elif verb == "constrain":
        section = rest[rest.index("--section") + 1] if "--section" in rest and rest.index("--section") + 1 < len(rest) else ""
        prefix = [one for one in rest if one != "--section" and one != section]
        if len(prefix) > 1:
            sys.stderr.write(__doc__)
            return 2
        posed = sections.constrain(root, path, prefix[0] if prefix else None, section,
                                   piped_value(sections))
        print(f"pp-authoring: posed -- {' '.join(posed)} in constraints.{section} on {path.name}")
    elif verb == "serve" and rest:
        whole = rest == ["-"]
        rows = [one.split() for one in sys.stdin.read().splitlines()] if whole else [rest]
        if whole:
            while rows and not rows[-1]:
                rows.pop()
            while rows and not rows[0]:
                rows.pop(0)
            if not any(rows):
                refuse("value-malformed",
                       "an empty serve section writes nothing -- `remove` deletes")
        outcome = sections.serve(path, rows, whole)
        print(f"pp-authoring: served -- {outcome} on {path.name}")
    else:
        sys.stderr.write(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
