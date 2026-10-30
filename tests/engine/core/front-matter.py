"""Scenario `front-matter` -- the front matter read, memoized and written:
- the reader: the front matter IS YAML (types, comments, null-means-absent); one file read
  twice touches the disk once; a fresh file is never stale; a rewritten document is seen
  again; a document gone refuses, memo or not
- the block scalars: `>` folds into prose, `|` keeps the procedure's lines
- the writer: surgical edits byte-stable, the value in the reader's shape, law codes derived
  in the section named, every guard red, the serve rows and their ranges grammar, every value
  read back as written
- the sections of the laws: production then behavior, a bare `constraints:` refuses by name;
  an overlay's deltas carry their section; a law round-trips the wire
- the manifests: `instance.yaml` parses once per state of its file, a rewrite is read back,
  the memo hands out copies
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import time
from pathlib import Path

from conductor import Refusal, reading, sections
from conductor.core import document
from conductor.core.model import Constraint
from conductor.state import instance

FIRST_LAW = "KZQ1  a first bench law stands here."

BATCH = f"""---
slug: un-lot-banc
kind: batch
plan: saga
phase: p1
status: doing
created: 2026-08-19
constraints.behavior: |
  {FIRST_LAW}
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

SERVED = "serve: |\n  docs/REF.md[12-40,88-102] engine/pp.py\n  notes/plan.md"
SERVED_BY_HAND = "serve: |\n  bare/one.md two.md"


# --- the reader ----------------------------------------------------------------------------

def reader(bench) -> None:
    """The front matter is YAML, read once per state of its file."""
    held, failures = bench.held, bench.failures
    yaml_facts = reading.front_matter(
        "cycle: beat\nmemory: 3\ntools:\n# a real comment\nname: X".splitlines())
    if (yaml_facts.get("cycle") == "beat" and yaml_facts.get("memory") == 3
            and "tools" not in yaml_facts and "# a real comment" not in str(yaml_facts)
            and reading.truthy(True) and reading.truthy("true") and not reading.truthy("false")):
        held("the front matter is YAML", "true is a bool, 3 an int, a bare key is absent, "
             "# comments vanish -- one public norm, no house dialect")
    else:
        failures.append(f"  ✗ yaml front matter         {yaml_facts!r}")

    home = bench.temp()
    once = home / "ONCE.md"
    once.write_text("---\nname: ONCE\nkind: doc\n---\n\nfirst state\n",
                    encoding="utf-8")
    # the drawer never remembers a file younger than the clock's tick: the memo case reads
    # an AGED file -- what a document is, outside a bench
    aged = once.stat().st_mtime - 1
    os.utime(once, (aged, aged))
    hits = [0]
    raw = Path.read_text

    def counting(self, *a, **k):
        if self == once:
            hits[0] += 1
        return raw(self, *a, **k)

    Path.read_text = counting
    try:
        first = document.read(once)
        second = document.read(once)
        disk_twice = hits[0]
        # a rewrite MUST be seen: a new state carries a new key, whatever the memo holds
        time.sleep(0.01)
        once.write_text("---\nname: ONCE\nkind: doc\nmarker: second\n---\n"
                        "\nsecond state\n", encoding="utf-8")
        third = document.read(once)
        disk_after = hits[0]
    finally:
        Path.read_text = raw

    if disk_twice == 1 and first.front == second.front:
        held("two reads, one disk access",
             f"the same file read twice touched the disk {disk_twice}x -- the state is the key")
    else:
        failures.append(f"  ✗ read memo                   {disk_twice} disk access(es) for two reads")

    # two writes of ONE size, inside one tick: the second text is what a read returns --
    # a fresh file is served from the disk, never from the drawer
    twin = home / "TWIN.md"
    twin.write_text("---\nname: TWIN\nkind: doc\nmarker: aaaaa\n---\n\nx\n", encoding="utf-8")
    seen_first = document.read(twin).front.get("marker")
    twin.write_text("---\nname: TWIN\nkind: doc\nmarker: bbbbb\n---\n\nx\n", encoding="utf-8")
    seen_second = document.read(twin).front.get("marker")
    if seen_first == "aaaaa" and seen_second == "bbbbb":
        held("a fresh file is never stale", "two writes of one size inside the clock's tick: "
             "the second text is read -- the drawer waits until the file has aged")
    else:
        failures.append(f"  ✗ fresh file stale            {seen_first!r} then {seen_second!r}")

    if third.front.get("marker") == "second" and disk_after == 2:
        held("a rewritten document is seen again",
             "a new mtime and size carry a new key: the third read went back to the disk")
    else:
        failures.append(f"  ✗ stale read                  {third.front!r} after "
                        f"{disk_after} disk access(es)")

    once.unlink()
    bench.expect("document-missing", lambda: document.read(once))


# --- the block scalars ---------------------------------------------------------------------

def block_scalars(bench) -> None:
    """`>` folds into prose, `|` keeps the procedure's lines."""
    front = reading.front_matter(["description: >-", "  one", "  two", "proc: |", "  PICK x"])
    if front["description"] == "one two" and front["proc"] == "PICK x":
        bench.held("block scalars", "`>` folds into prose, `|` keeps the procedure's lines")
    else:
        bench.failures.append(f"  ✗ block scalars             {front}")


# --- the writer ----------------------------------------------------------------------------

@contextlib.contextmanager
def fed(text: str):
    """The piped value a gesture reads on stdin."""
    spot, sys.stdin = sys.stdin, io.StringIO(text)
    try:
        yield
    finally:
        sys.stdin = spot


def guarded(call):
    """A LIBRARY refusal, said the way a console says it: the writer raises `Refusal`, and
    `expect_exit` judges a script's exit -- the translation the consoles do."""
    def played():
        try:
            return call()
        except Refusal as refusal:
            sys.stderr.write(f"sections: {refusal.code} -- {refusal}\n")
            raise SystemExit(2)
    return played


def writer(bench) -> None:
    """The front matter WRITER: surgical edits byte-stable, every guard red, the code
    attribution unique across the documents of its root."""
    root = bench.temp()
    doc = root / "BATCH.md"
    doc.write_text(BATCH, encoding="utf-8")
    proc = root / "BANC.md"
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
    assert FIRST_LAW in text
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
    assert SERVED in text
    by_hand = text.replace(SERVED, SERVED_BY_HAND)
    with fed("bare/one.md two.md\n"):
        sections.serve(doc, [one.split() for one in sys.stdin.read().splitlines()], True)
    assert doc.read_text(encoding="utf-8") == by_hand
    bench.held("serve writes the grouping rows", "a row appends, ranges glued and lawful; the piped "
               "replacement is byte-identical to the hand-written section")

    for token in ("doc.md[3-2]", "doc.md[0-4]", "doc.md[2-5,4-9]", "doc.md[9-12,2-4]", "doc.md[a-b]"):
        bench.expect_exit("serve-range-malformed", guarded(lambda token=token: sections.valid_token(token)))
    bench.held("the ranges grammar refuses as one", "descending, zero-based, overlapping, unordered and "
               "unparsable ranges all red -- the writer speaks the engine's refusal")

    # a value the reader cannot read back as written is written so it can
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
    blocks = root / "BLOCKS.md"
    blocks.write_text(BLOCKS, encoding="utf-8")
    shapes = {key: sections.get(blocks, key) for key in ("literal", "chomped", "folded", "folded-chomped")}
    if not lost and shapes == {"literal": "one\ntwo", "chomped": "kept", "folded": "a folded line",
                               "folded-chomped": "a description folded on two lines"}:
        bench.held("every value reads back as written", f"{len(RISKY)} risky values -- YAML indicators, "
                   "a colon inside, a comment mark, words YAML would type -- read back by the reader and "
                   "by get as the string given; get renders |, |-, > and >- by their text")
    else:
        bench.failures.append(f"  ✗ values read back           lost={lost!r} shapes={shapes!r}")


# --- the sections of the laws --------------------------------------------------------------

def laws(bench) -> None:
    """A document declares its laws in two sections; the overlay and the wire carry the section."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    home = bench.temp()

    def doc(name: str, text: str) -> Path:
        path = home / f"{name}.md"
        path.write_text(text, encoding="utf-8")
        return path

    both = reading.read(doc("BOTH",
        "---\nname: LAWS\nconstraints.production: |\n  P1  the file ends on a newline\n"
        "constraints.behavior: |\n  H1  say what you do before you do it\n"
        "  # H2  a comment stays inert\n---\nx\n"))
    found = reading.constraints(both)
    expect("constraints-unsectioned", lambda: reading.constraints(reading.read(doc("BARE",
        "---\nname: LAWS\nconstraints: |\n  B1  the old regime\n---\nx\n"))))
    if [(one.code, one.section) for one in found] == [("P1", "production"), ("H1", "behavior")]:
        held("two sections, the bare key refuses", "P1 production, H1 behavior, the comment "
             "inert; a bare `constraints:` refuses `constraints-unsectioned`")
    else:
        failures.append(f"  ✗ sections read              {found}")
    expect("constraint-malformed", lambda: reading.constraints(reading.read(doc("NOCODE",
        "---\nname: LAWS\nconstraints.behavior: |\n  nocode\n---\nx\n"))))

    deltas = reading.constraint_deltas(reading.read(doc("TURN",
        "---\nname: TURN\nconstraints.production: |\n  +Q1  a fact rendered\n"
        "constraints.behavior: |\n  -T4\n  W1  a way of doing\n---\n")))
    if deltas == [("+", "Q1", "a fact rendered", "production"), ("-", "T4", "", ""),
                  ("+", "W1", "a way of doing", "behavior")]:
        held("the overlay deltas carry their section", "+Q1 production, -T4 by code alone, "
             "W1 behavior")
    else:
        failures.append(f"  ✗ overlay deltas             {deltas}")

    law = Constraint(code="H1", text="say it", section="behavior")
    older = Constraint.parse("P9  an older snapshot line")
    if (Constraint.parse(law.wire()) == law and law.wire() == "behavior:H1  say it"
            and str(law) == "H1  say it" and older.section == "production"
            and Constraint.parse(Constraint(code="P1", text="t").wire())
            == Constraint(code="P1", text="t")):
        held("a law round-trips the wire", "the section rides the snapshot as a prefix; a "
             "bare line reads as production")
    else:
        failures.append(f"  ✗ wire                       {law.wire()!r} {older}")


# --- the manifests -------------------------------------------------------------------------

def manifests(bench) -> None:
    """A manifest parses once per state of its file, and the memo hands out copies."""
    held, failures = bench.held, bench.failures
    made = bench.env("memo", ("wit",)).made
    parses = []                                        # one entry per yaml parse
    real = instance.yaml.safe_load
    instance.yaml.safe_load = lambda text: parses.append(1) or real(text)
    try:
        # the process's memos emptied first: what this process already read stays out of
        # the count, which says what one fresh read parses
        instance._parsed.clear()
        document._PARSED.clear()
        del parses[:]
        first = instance.read(made)
        for _ in range(4):
            instance.read(made)
        kit_root = next(one for one in instance.vendored(made) if one.name.startswith("kit@"))
        for _ in range(4):
            instance.manifest_of(kit_root)
            instance.vendored(made)
            instance.search_paths(made)
        count = 1 + len(instance.pins(made))               # instance.yaml + one per pin
        settings = 1 if (made / "SETTINGS.md").is_file() else 0   # the switches, read once too
        if len(parses) == count + settings and first.get("packages"):
            held("a manifest parses once", f"{count} parses for "
                 f"{5 + 4 * 3} reads of the instance and its {count - 1} packages, "
                 f"plus {settings} for the SETTINGS the package switches read")
        else:
            failures.append(f"  ✗ manifest memo                {len(parses)} parses, "
                            f"expected {count + settings} (the manifest, its pins and SETTINGS), packages={bool(first.get('packages'))}")

        # a rewrite is read back at the next call: the bytes decide, not a clock
        del parses[:]
        pinned = instance.read(made)
        before = list(pinned["packages"])
        pinned["packages"] = dict(reversed(list(pinned["packages"].items())))
        instance.write(made, pinned)                        # same size, new bytes, same tick
        reordered = list(instance.read(made)["packages"])
        again = len(parses)
        (made / instance.MANIFEST).write_text((made / instance.MANIFEST).read_text(encoding="utf-8"),
                                              encoding="utf-8")   # identical bytes, by hand
        instance.read(made)
        if reordered == list(reversed(before)) and again == 1 and len(parses) == 1:
            held("a rewrite is read back", "new bytes parse once more at the next "
                 "call, identical bytes rewritten by hand parse nothing")
        else:
            failures.append(f"  ✗ manifest rewrite             {before} {reordered} "
                            f"parses={parses}")

        # the memo never leaks: the caller's copy is its own
        edited = instance.read(made)
        edited["packages"]["ghost"] = "0"
        if "ghost" not in instance.read(made).get("packages", {}):
            held("the memo hands out copies", "a declaration edited before its write "
                 "leaves the memo untouched")
        else:
            failures.append("  ✗ manifest memo leaked         an edit reached the memo")
    finally:
        instance.yaml.safe_load = real


def scenario(bench) -> int:
    reader(bench)
    block_scalars(bench)
    writer(bench)
    laws(bench)
    manifests(bench)
    return 0
