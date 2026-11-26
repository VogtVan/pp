"""Scenario `zones/space` -- the zone `space` of the conduction (an output opened or closed by `-open` / `-close`), played under the
modelled LLM by the fewest roots that cross it, and read on the sheet of that play: the zone crossed, every
exchange played at cost 0
without a hole, parked unless its root expects otherwise, no `rouge-conduction` and no `trou` on its lines
(tests/README.md, rule 11; `zone_case` in the support); and the free step of the space: in the launch of
the root `space` that closes ROOM, ROOM's production is printed BEFORE `-close` (the message says the line,
then closes), and the production held back while `-close` plays -- the step of the turn the space returns
to -- is printed after `pp: closed`, in the same launch: a space left is not served again.
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")
ZONE = "space"
ROOTS = ('space', 'ledger', 'space-by-principal')


def closing(folder) -> tuple[str, bool, str]:
    """-> the case of the free step around `-close`, read on the flow of the root `space`."""
    calls: dict = {}
    for one in C.flow_of(folder, "space-relayed"):
        if one.get("kind") == "tool" and one.get("launch") is not None:
            calls.setdefault(one["launch"], []).append(str(one.get("shell") or "").splitlines()[0].split())
    launch = next((done for done in calls.values() if any(words[-1:] == ["-close"] for words in done)), [])
    at = next((n for n, words in enumerate(launch) if words[-1:] == ["-close"]), -1)
    printed = [(n, words[words.index("-print") + 1]) for n, words in enumerate(launch) if "-print" in words]
    before = [document for n, document in printed if n < at]
    after = [document for n, document in printed if n > at]
    kept = at >= 0 and "ROOM" in before and bool(after)
    return ("the free step around -close", kept, f"before -close {before}, after it {after}" if kept
            else f"launch={[' '.join(words[-2:]) for words in launch]} before={before} after={after}")


def scenario(bench) -> int:
    return C.zone_case(bench, ZONE, ROOTS, closing)
