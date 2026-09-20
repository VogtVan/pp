"""packages/steering/procs/NEXT.md -- the text it keeps: the end of the answer -- the front
copied as served, then the choices -- with no tool and no condition to judge.

The phrases are matched on a whitespace-FLATTENED copy: the document wraps its prose at eighty
columns, and a phrase of the doctrine must not become invisible because a line broke inside it."""
from __future__ import annotations

import re

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "steering", "NEXT").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    front = text.split("---")[1]
    body = " ".join(text.split("---", 2)[2].split())

    # the shape: an INFER called by THREADS, no offer, the token it provides and reads
    for phrase in ("output: next", "next stdin", "`your best choice(s)`",
                   "`initiative | note | progress | age | next action(s)`", "one liberty",
                   "payloads: steering-threads", "provides: steering-threads",
                   "with: pp-steering status --due",
                   # the seam: the front and the choices render as two pieces
                   "a quoted note --, a blank line, then the CHOICES table"):
        assert phrase in flat, phrase
    assert re.search(r"^proc: \|\n  INFER\n", front, re.M)
    assert not re.search(r"^(tools|attach):", front, re.M)
    formats = re.search(r"^formats: .*$", front, re.M).group(0)
    assert len(formats) <= 350, len(formats)
    bench.held("NEXT is an INFER that offers nothing", "called by THREADS, no `attach:`, no `tools:`; "
               f"it provides and reads `steering-threads`; its `formats:` line {len(formats)} c")

    # the copy: no condition to judge, no replay, no line to recognise
    for phrase in ("Copy the `steering-threads` reading as it stands",
                   "it holds either the threads table with its `⏸` and `💤` lines, or one line",
                   "You never choose between them",
                   "the `steering-threads` reading copied unchanged"):
        assert phrase in flat, phrase
    for absent in ("when no thread was added, closed or worked", "since the table was last supplied to you",
                   "play `pp-steering status` again", "or the one line saying it did not change",
                   "thread table not changed since the last turn", "byte for byte"):
        assert absent not in flat, absent
    bench.held("NEXT copies the front, never judges it", "the reading copied as it stands, table or line; "
               "the condition, the replay and the line's own text are gone")

    # no gesture: the body names no verb of the keeper
    for verb in ("pp-steering close", "`close`", "`refer`", "`unlist`", "`reorder`", "`attach`", "`amend`"):
        assert verb not in body, verb
    bench.held("NEXT orders no gesture", "no verb of `pp-steering` in its body: every gesture lives "
               "under the WORK step of THREADS")

    # the choices and the note
    for phrase in ("the two next key actions you judge due",
                   "not necessarily two rows of the threads table",
                   "When one action alone is due, offer one choice and say so",
                   "names its work with its full address",
                   "what it unlocks and where it comes from",
                   "said as such",
                   "at the end of a `next action(s)` cell",
                   "after the age of a thread in the `💤` line",
                   "Write the front, a blank line, then the choices",
                   "Write nothing after the choices"):
        assert phrase in body, phrase
    assert "from different threads" not in body and "#id" not in body
    for absent in ("🪢", "braid", "`fil | avancement | âge | prochaine action`",
                   "`fil | note | avancement | âge | prochaine(s) action(s)`"):
        assert absent not in flat, absent
    bench.held("the choices are the two key actions", "one alone when one is due, each with its "
               "full address, what it unlocks and its origin; the note at a cell's end or after a "
               "footer age; the front first, a blank line, then the choices and nothing after them; "
               "the braid and the four-column table gone")

    size = len(text.split("---", 2)[2])
    assert size <= 1800, size
    for absent in ("confederation", "@<member>", "plan:", "lot:", "next move", "trivial"):
        assert absent not in body.lower(), absent
    bench.held("the base names no client, and weighs little", f"{size} c of body, "
               "no plan, improvement or federation vocabulary")
    return 0
