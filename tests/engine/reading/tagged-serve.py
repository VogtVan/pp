"""Scenario `tagged-serve` -- 5 case(s) (plan core, phase la-lecture):
- ONE grammar: a table of tokens played against the reader, the writer and the lint's
  scan gives the same names and the same verdicts
- a token serves the lines between TWO TAGS whatever the document is: the same cases on a
  `.md`, a `.py` and a `.yaml` -- a tag is read at the start of a line, the end tag is
  excluded and sought after the start, either end may stay open, the selection is hashed
- a row whose token carries blanks is cut right, by a section's SERVE, a `SERVE <doc>`
  and a mount's row; the reading is titled by the token as written, spared when proven
- what is absent is SAID (a start tag gone: `missing`; an end tag gone: served to the
  end), what is badly written REFUSES by its name
- the writer writes what the reader reads back, and discourages a line range
"""
from __future__ import annotations

import json
from pathlib import Path

from conductor import Refusal, reading, sections, topology

WELL = {
    "d.md": ("d.md", (), None),
    "d.md[2-3,5-9]": ("d.md", ((2, 3), (5, 9)), None),
    "d.py[def a..def b]": ("d.py", (), ("def a", "def b")),
    "d.md[## Target..## Tests]": ("d.md", (), ("## Target", "## Tests")),
    "d.md[..## Target]": ("d.md", (), ("", "## Target")),
    "d.md[## Delivery..]": ("d.md", (), ("## Delivery", "")),
}
TORN = ("d.md[..]", "d.md[a..b..c]", "d.md[abc]", "d.md[## A")

# one witness per kind of document: a head, a line that MENTIONS the second tag before it
# stands, then three tagged parts -- the third one indented
WITNESSES = {
    "W.md": (("## Alpha", "## Beta", "## Gamma"), "## Be",
             "# Title\nsee ## Beta below\n## Alpha\na1\n## Beta\nb1\nb2\n  ## Gamma\ng1\n"),
    "w.py": (("def alpha", "def beta", "def gamma"), "def be",
             "import os\n# def beta comes second\ndef alpha():\n    return 1\ndef beta():\n"
             "    x = 2\n    return x\n  def gamma():\n    return 3\n"),
    "w.yaml": (("alpha:", "beta:", "gamma:"), "bet",
               "top: 0\n# beta: comes second\nalpha:\n  a: 1\nbeta:\n  b: 1\n  c: 2\n"
               "  gamma:\n  g: 1\n"),
}

PROC = """---
name: TAGGED
kind: proc
description: a witness whose rows carry tokens with blanks
serve: |
  reference: W.md[## Beta..## Gamma] NOTE.md
  reference: W.md[## Beta..## Gamma]
  reference: W.md[## Nowhere..## Gamma] W.md[## Alpha..## Nowhere]
proc: |
  SERVE
  SERVE W.md[..## Alpha]
  INFER
---

The witness of the tagged rows.
"""
BAD = "---\nname: BAD\nkind: proc\ndescription: a badly written row\nserve: |\n  {row}\nproc: |\n  SERVE\n  INFER\n---\n\nbad\n"


def _verdict(call) -> str:
    try:
        call()
    except Refusal as refusal:
        return refusal.code
    return "ok"


def _trace(made) -> list[dict]:
    return [json.loads(line)
            for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- (1) the table: one grammar, three readers -----------------------------------------
    wrong = []
    for token, (name, ranges, span) in WELL.items():
        read_name, cut = reading.ranged(token)
        scanned = topology.references(Path("w.md"), {"serve": f"reference: {token} other.md"})
        if not (read_name == name and cut == ranges and getattr(cut, "span", None) == span
                and bool(cut) == bool(ranges or span)
                and _verdict(lambda token=token: sections.valid_token(token)) == "ok"
                and scanned == [("serve", name), ("serve", "other.md")]):
            wrong.append(token)
    for token in TORN:
        verdicts = {_verdict(lambda token=token: reading.ranged(token)),
                    _verdict(lambda token=token: sections.valid_token(token)),
                    _verdict(lambda token=token: topology.references(Path("w.md"), {"serve": token}))}
        if verdicts != {"serve-range-malformed"}:
            wrong.append(f"{token} -> {sorted(verdicts)}")
    if not wrong:
        held("one grammar, three readers", f"{len(WELL)} well-formed and {len(TORN)} torn tokens: "
             "the reader, the writer and the lint's scan give the same names and verdicts")
    else:
        failures.append(f"  ✗ the table of tokens         {wrong}")

    # --- (2) the cut between two tags, the same cases on three kinds of document -----------
    env = bench.env("tags")
    for name, (tags, prefix, text) in WITNESSES.items():
        path = env.write(name, text)
        lines = text.splitlines()
        at = [next(i for i, line in enumerate(lines) if line.lstrip().startswith(tag)) for tag in tags]
        expected = {
            (tags[1], tags[2]): lines[at[1]:at[2]],
            ("", tags[1]): lines[:at[1]],
            (tags[2], ""): lines[at[2]:],
            (prefix, tags[2]): lines[at[1]:at[2]],
            (tags[2], tags[1]): lines[at[2]:],          # the end is sought AFTER the start
        }
        off = []
        hashes = {reading.served(path)[1]}
        for span, want in expected.items():
            got, tag, missing = reading.spanned(path, span)
            if got != "\n".join(want) + "\n" or missing != ("end" if span == (tags[2], tags[1]) else ""):
                off.append((span, got, missing))
            hashes.add(tag)
        gone = reading.spanned(path, ("nowhere at all", tags[2]))
        if not off and gone[0] == "" and gone[2] == "start" and len(hashes) == 4:
            held(f"two tags cut a {path.suffix}", "both tags, an open start, an open end, a prefix; "
                 "the mention before the tag ignored, the end excluded, the selection hashed")
        else:
            failures.append(f"  ✗ the cut of {name:<17}{off} {gone} {len(hashes)} hashes")

    # --- (3) a row with blanks, by a section, a `SERVE <doc>` and a mount ------------------
    env.write("NOTE.md", "the note\n")
    env.write("TAGGED.md", PROC)
    first = env.conductor("t")
    first.forget()
    served = first.start(env.made / "TAGGED.md").payloads
    titles = [subject for subject, _ in served if subject.startswith(("W.md", "NOTE.md"))]
    texts = dict(served)
    ledger = [line for one in _trace(env.made) if one.get("kind") == "block"
              for line in (one.get("served") or [])]
    states = [(line["subject"], line["state"]) for line in ledger
              if line["subject"].startswith(("W.md", "NOTE.md"))]
    if (titles[:2] == ["W.md[## Beta..## Gamma]", "NOTE.md"]
            and texts["W.md[## Beta..## Gamma]"].strip() == "## Beta\nb1\nb2"
            and texts.get("W.md[..## Alpha]", "").strip() == "# Title\nsee ## Beta below"
            and states.count(("W.md[## Beta..## Gamma]", "spared")) == 1):
        held("a row with blanks is cut right", "two readings titled by their tokens as written, "
             "the same token spared the second time, a `SERVE <doc>` with a tag served")
    else:
        failures.append(f"  ✗ the row with blanks         {titles} {states}")

    env.write("NODE.md", "---\nname: NODE\nkind: doc\nserve: |\n  reference: w.py[def beta..def gamma] NOTE.md\n---\n\nnode\n")
    mounted = env.conductor("t").mount([{"doc": "NODE.md"}])
    if "w.py[def beta..def gamma]\n" in mounted and "    x = 2" in mounted and "return 3" not in mounted:
        held("a mount's row reads the same", "the tagged token of a mounted document is served "
             "under its own title")
    else:
        failures.append(f"  ✗ the mount's row             {mounted[-400:]!r}")

    # --- (4) the absent is said, the badly written refuses ---------------------------------
    stale = [one for one in _trace(env.made) if one.get("kind") == "signal"
             and one.get("signal") == "serve-stale"]
    if (("W.md[## Nowhere..## Gamma]", "missing") in states
            and texts.get("W.md[## Alpha..## Nowhere]", "").strip().endswith("g1")
            and len(stale) == 2):
        held("what is absent is said", "a start tag gone: `missing`, its line in the block; an end "
             "tag gone: served to the end; `serve-stale` pushed for each")
    else:
        failures.append(f"  ✗ the absent tags             {states} {len(stale)} signal(s)")
    for row in ("W.md[..]", "W.md[a..b..c]", "W.md[abc]", "W.md[## Beta"):
        env.write("BAD.md", BAD.format(row=row))
        torn = env.conductor("b")
        torn.forget()
        expect("serve-range-malformed", lambda torn=torn: torn.start(env.made / "BAD.md"))

    # --- (5) the writer: what it writes reads back, and a line range is discouraged --------
    doc = env.write("WRITTEN.md", "---\nname: WRITTEN\nkind: doc\n---\n\nwritten\n")
    row = ["reference:", "W.md[## Beta..## Gamma]", "NOTE.md"]
    quiet = sections.serve(doc, [row])
    back = reading.serve_sections(reading.read(doc))
    loud = sections.serve(doc, [["w.py[1-2]", "w.py[def alpha..]"]])
    if (back == ((tuple(row),),) and "w.py[" not in quiet and "W.md" not in quiet
            and loud.count("w.py[1-2]") == 1 and "w.py[def alpha..]" not in loud
            and "prefer tags" in loud):
        held("the writer and the reader agree", "a row with blanks reads back identical; the answer "
             "discourages a line range and says nothing of a whole or a tagged token")
    else:
        failures.append(f"  ✗ the writer                  {back!r} {quiet!r} {loud!r}")
    return 0
