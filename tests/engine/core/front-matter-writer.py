"""conductor.core.sections -- the front matter WRITER: surgical edits proven byte-stable on
a real instance, every guard red, the code attribution unique. It came from the authoring
area at batch pp-split / le-noyau-generique / le-core-importable, when the writer descended
to the engine; `pp-authoring` keeps a scenario for its CONSOLE."""
from __future__ import annotations

import contextlib
import io
import sys

from conductor import Refusal, sections
from conductor.core import document

BATCH = """---
slug: un-lot-banc
kind: batch
plan: saga
phase: p1
status: doing
created: 2026-08-19
constraints.behavior: |
  KZQ1  a first bench law stands here.
item.1: une-etape  todo
---

# BATCH `un-lot-banc`

La prose du lot, jamais touchée.
"""

RISKY = ("yes", "3", "null", "a: b", "x #y", "- a", '"q"', "'q'", "@x", "%x", "`x", "0.10",
         "true", "~", "[a]", "{a}", "*x", "&x", "!x", "|x", ">x", "?x", ",x", "usage", "café: é")

BLOCKS = """---
name: BLOCKS
literal: |
  one
  two
chomped: |-
  kept
folded: >
  a folded
  line
folded-chomped: >-
  a description
  folded on two lines
---
"""

PROC = """---
name: BANC
kind: proc
description: a bench proc
---

The body.
"""


@contextlib.contextmanager
def fed(text: str):
    """The piped value a gesture reads on stdin."""
    spot, sys.stdin = sys.stdin, io.StringIO(text)
    try:
        yield
    finally:
        sys.stdin = spot


def guarded(call):
    """A LIBRARY refusal, said the way a console says it: the writer raises `Refusal`,
    and the bench's `expect_exit` judges a script's exit -- this is the translation the
    consoles do, played here so the guards keep their names and their count."""
    def played():
        try:
            return call()
        except Refusal as refusal:
            sys.stderr.write(f"sections: {refusal.code} -- {refusal}\n")
            raise SystemExit(2)
    return played


def scenario(bench) -> int:
    root = bench.env("kit", pin=False).made
    doc = root / "plans" / "saga" / "1-p1" / "1-un-lot-banc" / "BATCH.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(BATCH, encoding="utf-8")
    proc = root / "procs" / "BANC.md"
    proc.parent.mkdir(parents=True, exist_ok=True)
    proc.write_text(PROC, encoding="utf-8")

    before = doc.read_bytes()
    with fed("engine/pp.py\n"):
        sections.edit(doc, "serve", sections.bounded(sys.stdin.read().splitlines()), create=True)
    assert "serve: engine/pp.py" in doc.read_text(encoding="utf-8")
    sections.edit(doc, "serve", None, create=False)
    assert doc.read_bytes() == before
    bench.held("add then remove is byte-identical", "the untouched lines were never re-emitted -- "
               "the surgical splice leaves no trace")

    with fed("first line\nsecond line\n"):
        sections.edit(doc, "notes", sections.bounded(sys.stdin.read().splitlines()), create=True)
    assert "notes: |\n  first line\n  second line" in doc.read_text(encoding="utf-8")
    assert sections.get(doc, "notes") == "first line\nsecond line"
    with fed("only line\n"):
        sections.edit(doc, "notes", sections.bounded(sys.stdin.read().splitlines()), create=False)
    assert "notes: only line" in doc.read_text(encoding="utf-8")
    assert sections.get(doc, "constraints.behavior").startswith("KZQ1")
    sections.edit(doc, "notes", None, create=False)
    bench.held("the value takes the reader's shape", "several lines land as a block scalar, one line "
               "lands inline; get renders block scalars dedented")

    posed = []
    with fed("a law posed by its text alone.\nanother law, same gesture.\n"):
        posed += sections.constrain(root, doc, None, "production", sections.bounded(sys.stdin.read().splitlines()))
    with fed("a third law, later.\n"):
        posed += sections.constrain(root, doc, None, "behavior", sections.bounded(sys.stdin.read().splitlines()))
    text = doc.read_text(encoding="utf-8")
    assert len(posed) == 3 and len(set(posed)) == 3
    assert all(f"  {code}  " in text for code in posed)
    assert "KZQ1  a first bench law stands here." in text
    assert "constraints.production: |" in text and text.count("constraints.behavior: |") == 1
    assert "constraints: |" not in text
    with fed("a proc law under a named prefix.\n"):
        named = sections.constrain(root, proc, "KQX", "production", sections.bounded(sys.stdin.read().splitlines()))
    assert named == ["KQX1"] and "KQX1  a proc law" in proc.read_text(encoding="utf-8")
    with fed("a law with no section named.\n"):
        bench.expect_exit("section-missing", guarded(lambda: sections.constrain(root, proc, "KQX", "", ["x"])))
    bench.held("the codes derive, never collide, in the section named", "two successive poses continue "
               "the numbering across the two sections, the standing block survives verbatim, a named "
               "prefix obeys, a pose without its section refuses")

    bench.expect_exit("key-unknown", guarded(lambda: sections.get(doc, "absent-key")))
    with fed("x\n"):
        bench.expect_exit("key-taken", guarded(lambda: sections.edit(doc, "constraints.behavior", sections.bounded(sys.stdin.read().splitlines()), create=True)))
    with fed("\n"):
        bench.expect_exit("value-malformed", guarded(lambda: sections.bounded(sys.stdin.read().splitlines())))
    with fed("x" * 501 + "\n"):
        bench.expect_exit("budget", guarded(lambda: sections.bounded(sys.stdin.read().splitlines())))
    bench.held("the refusals hold", "key-unknown, key-taken, value-malformed, budget "
               "document-missing -- red, nothing written")

    sections.serve(doc, [["docs/REF.md[12-40,88-102]", "engine/pp.py"]])
    sections.serve(doc, [["notes/plan.md"]])
    text = doc.read_text(encoding="utf-8")
    assert "serve: |\n  docs/REF.md[12-40,88-102] engine/pp.py\n  notes/plan.md" in text
    by_hand = text.replace("serve: |\n  docs/REF.md[12-40,88-102] engine/pp.py\n  notes/plan.md",
                           "serve: |\n  bare/one.md two.md")
    with fed("bare/one.md two.md\n"):
        sections.serve(doc, [one.split() for one in sys.stdin.read().splitlines()], True)
    assert doc.read_text(encoding="utf-8") == by_hand
    bench.held("serve writes the grouping rows", "a row appends, ranges glued and lawful; the piped "
               "replacement is byte-identical to the hand-written section")

    for token in ("doc.md[3-2]", "doc.md[0-4]", "doc.md[2-5,4-9]", "doc.md[9-12,2-4]", "doc.md[a-b]"):
        bench.expect_exit("serve-range-malformed", guarded(lambda token=token: sections.valid_token(token)))
    bench.held("the ranges grammar refuses as one", "descending, zero-based, overlapping, unordered and "
               "unparsable ranges all red -- the writer speaks the engine's refusal")
    # --- a value the reader cannot read back as written is written so it can -------------
    lost = []
    for value in RISKY:
        sections.edit(proc, "risky", [value], create=True)
        try:
            read = document.front_matter(proc.read_text(encoding="utf-8").splitlines()[1:
                    proc.read_text(encoding="utf-8").splitlines()[1:].index("---") + 1]).get("risky")
        except Refusal as refusal:
            read = f"<{refusal.code}>"
        got = sections.get(proc, "risky")
        if read != value or got != value:
            lost.append((value, read, got))
        sections.edit(proc, "risky", None, create=False)
    blocks = proc.parent / "BLOCKS.md"
    blocks.write_text(BLOCKS, encoding="utf-8")
    shapes = {key: sections.get(blocks, key) for key in ("literal", "chomped", "folded", "folded-chomped")}
    if not lost and shapes == {"literal": "one\ntwo", "chomped": "kept", "folded": "a folded line",
                               "folded-chomped": "a description folded on two lines"}:
        bench.held("every value reads back as written", f"{len(RISKY)} risky values -- YAML indicators, "
                   "a colon inside, a comment mark, words YAML would type -- read back by the reader and "
                   "by get as the string given; get renders |, |-, > and >- by their text")
    else:
        bench.failures.append(f"  ✗ values read back           lost={lost!r} shapes={shapes!r}")
    return 0
