"""Scenario `front-matter` -- 5 case(s), in the monolith's order:
- the front matter IS YAML: types, comments, and null-means-absent
- le-front-matter-lu-une-fois: one file, two reads, ONE disk access
- le-front-matter-lu-une-fois: a document REWRITTEN between two reads renders its new text
- le-front-matter-lu-une-fois: a document gone refuses, memo or not
"""
from __future__ import annotations

import os

import time
from pathlib import Path

from conductor import Refusal, reading
from conductor.core import document as core_document


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the front matter IS YAML: types, comments, and null-means-absent --------------
    yaml_facts = reading.front_matter(
        "cycle: true\nmemory: 3\ntools:\n# a real comment\nname: X".splitlines())
    if (yaml_facts.get("cycle") is True and yaml_facts.get("memory") == 3
            and "tools" not in yaml_facts and "# a real comment" not in str(yaml_facts)
            and reading.truthy(True) and reading.truthy("true") and not reading.truthy("false")):
        held("the front matter is YAML", "true is a bool, 3 an int, a bare key is absent, "
             "# comments vanish -- one public norm, no house dialect")
    else:
        failures.append(f"  ✗ yaml front matter         {yaml_facts!r}")
    
    # --- le-front-matter-lu-une-fois: one file, two reads, ONE disk access -------------
    home = bench.temp()
    once = home / "ONCE.md"
    once.write_text("---\nname: ONCE\nkind: doc\n---\n\nfirst state\n",
                    encoding="utf-8")
    # the drawer never remembers a file younger than the clock's tick (le-banc-stable):
    # the memo case reads an AGED file -- what a document is, outside a bench
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
        first = core_document.read(once)
        second = core_document.read(once)
        disk_twice = hits[0]
        # a rewrite MUST be seen: a new state carries a new key, whatever the memo holds
        time.sleep(0.01)
        once.write_text("---\nname: ONCE\nkind: doc\nmarker: second\n---\n"
                        "\nsecond state\n", encoding="utf-8")
        third = core_document.read(once)
        disk_after = hits[0]
    finally:
        Path.read_text = raw

    if disk_twice == 1 and first.front == second.front:
        held("two reads, one disk access",
             f"the same file read twice touched the disk {disk_twice}x -- the state is the key")
    else:
        failures.append(f"  ✗ read memo                   {disk_twice} disk access(es) for two reads")

    # two writes of ONE size, inside one tick: the second text is what a read returns --
    # a fresh file is served from the disk, never from the drawer (le-banc-stable: the
    # bench's own flakes were this collision, caught by a probe on text_of)
    twin = once.parent / "TWIN.md"
    twin.write_text("---\nname: TWIN\nkind: doc\nmarker: aaaaa\n---\n\nx\n", encoding="utf-8")
    seen_first = core_document.read(twin).front.get("marker")
    twin.write_text("---\nname: TWIN\nkind: doc\nmarker: bbbbb\n---\n\nx\n", encoding="utf-8")
    seen_second = core_document.read(twin).front.get("marker")
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

    # --- le-front-matter-lu-une-fois: a document gone refuses, memo or not -------------
    once.unlink()
    bench.expect("document-missing", lambda: core_document.read(once))
    return 0
