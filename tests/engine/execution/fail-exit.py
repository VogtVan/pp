"""Scenario `fail-exit` -- 6 case(s) (batch la-sortie-du-fail, 2026-10-04): an honest `fail` has a way
out, and a fix that holds does not wear the repair bound.
- (a) a `fail` carrying a non-empty `blocked` text before a FINAL: the FINAL renders, no REPAIR; the
  trace carries a `blocked` line with the code and its text, `-stats` counts it; the closing says
  the gap
- (b) an empty `blocked` is a bare `fail`: REPAIR 1
- (c) three exchanges, each a `fail` + `fix` whose mini-proof holds, under `work_repairs_allowed: 1`:
  never `repair-exhausted`, the repair counts read at 0
- (d) a relapse at the mini-proof counts one, as before
- (e) bare `fail`s under `work_repairs_allowed: 2`: the third hands back `repair-exhausted`
- (f) one object carrying `fix` and `blocked`: the repair plays in place, and the mini-proof that
  declares the gap again closes the checkpoint on the FINAL
"""
from __future__ import annotations

import json

from conductor import Conductor, Refusal, discovery, persistence, render, revive
from conductor.state import traces
from tests.harness import document, session_of

DOC = ("---\nname: GAPPED\nkind: proc\ndescription: a proven exchange\ncycle: true\n"
       "constraints.production: |\n  Z1  every claim comes with its rendering\nproc: |\n"
       "  INFER\n  FINAL\n---\nanswer the ask\n")


def _repairs(meta) -> int:
    """-> the repairs counted on the run's saved instructions, every frame."""
    restored = persistence.restore(session_of(meta), revive)
    return sum(one.repairs for frame in restored[1].frames for one in frame.procedure.instructions) if restored else -1


def _trace(meta) -> list[dict]:
    slot = session_of(meta)
    path = slot.parent / persistence.trace_of(slot)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    home = discovery.member(bench.town(["gapper"]).siblings, "gapper")
    script = bench.town(["engine"])["engine"].engine

    def conductor() -> Conductor:
        return Conductor(home, script, "t")

    def bound(allowed: int) -> None:
        (home.meta / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nwork_repairs_allowed: {allowed}\n---\n", encoding="utf-8")

    doc = document(DOC, at=home.meta)

    # --- (a) a declared gap closes the checkpoint -----------------------------------------------
    bound(3)
    conductor().start(doc)
    asked = conductor().submit("")
    closed = conductor().submit(json.dumps([{"code": "Z1", "evidence": "the claims stand unrendered",
                                             "verdict": "fail", "blocked": "the bench cannot run here"}]))
    shown = render(closed) if closed is not None else ""
    gaps = [one for one in _trace(home.meta) if one.get("kind") == "blocked"]
    counted_gaps = sum(one.blocked for one in traces.exchanges(_trace(home.meta)))
    if (asked is not None and asked.output == "proof" and closed is not None and closed.wait
            and not closed.repair and "(a gap declared: Z1 -- the bench cannot run here)" in shown
            and gaps and gaps[-1].get("gaps") == [{"code": "Z1", "text": "the bench cannot run here"}]
            and counted_gaps == 1):
        held("(a) a declared gap closes the checkpoint", "fail + blocked: the FINAL renders, REPAIR none, "
             "the trace says `blocked` Z1 with its text (-stats counts 1 gap), the closing says the gap")
    else:
        failures.append(f"  ✗ (a) the declared gap        wait={closed and closed.wait} repair={closed and closed.repair} "
                        f"{(closed.deviation if closed else '')!r} gaps={gaps[-1:]} counted={counted_gaps}")
    conductor().forget()

    # --- (b) an empty blocked is a bare fail ------------------------------------------------------
    conductor().start(doc)
    conductor().submit("")
    empty = conductor().submit(json.dumps([{"code": "Z1", "evidence": "off", "verdict": "fail", "blocked": "  "}]))
    if empty is not None and empty.repair == 1 and "your own proof failed" in (empty.deviation or ""):
        held("(b) an empty blocked is a bare fail", "REPAIR 1, the document replays")
    else:
        failures.append(f"  ✗ (b) the empty blocked       repair={empty and empty.repair} {(empty.deviation if empty else '')!r}")
    conductor().forget()

    # --- (c) three fixes that hold never wear the bound -------------------------------------------
    bound(1)
    conductor().start(doc)
    counted, outcome = [], ""
    try:
        for turn in range(3):
            conductor().submit("" if turn == 0 else f"message {turn + 1}")
            if turn:
                conductor().submit("")
            conductor().submit(json.dumps([{"code": "Z1", "evidence": "a claim unrendered",
                                            "verdict": "fail", "fix": "render the claim"}]))
            last = conductor().submit(json.dumps([{"code": "Z1", "evidence": "rendered: grep -c 1",
                                                   "verdict": "ok"}]))
            counted.append(_repairs(home.meta))
            outcome = "final" if last is not None and last.wait else "other"
    except Refusal as refused:
        outcome = refused.code
    if counted == [0, 0, 0] and outcome == "final":
        held("(c) three fixes that hold never wear the bound", "work_repairs_allowed 1, three exchanges "
             "each fail + fix then a mini-proof ok: repairs 0, 0, 0, the FINAL each time")
    else:
        failures.append(f"  ✗ (c) the fixes and the bound  counted={counted} outcome={outcome!r}")
    conductor().forget()

    # --- (d) a relapse counts one --------------------------------------------------------------------
    bound(3)
    conductor().start(doc)
    conductor().submit("")
    conductor().submit(json.dumps([{"code": "Z1", "evidence": "off", "verdict": "fail", "fix": "say it"}]))
    relapse = conductor().submit(json.dumps([{"code": "Z1", "evidence": "still off", "verdict": "fail"}]))
    if relapse is not None and "failed AGAIN" in (relapse.deviation or "") and _repairs(home.meta) == 1:
        held("(d) a relapse counts one", "the cheap branch closes, the document replays, one repair counted")
    else:
        failures.append(f"  ✗ (d) the relapse             {(relapse.deviation if relapse else '')!r} repairs={_repairs(home.meta)}")
    conductor().forget()

    # --- (e) bare fails hand back at the bound ---------------------------------------------------------
    bound(2)
    conductor().start(doc)
    bare = json.dumps([{"code": "Z1", "evidence": "the bench is out of reach", "verdict": "fail"}])
    conductor().submit("")
    conductor().submit(bare)                   # repair 1
    conductor().submit("")
    conductor().submit(bare)                   # repair 2
    conductor().submit("")
    expect("repair-exhausted", lambda: conductor().submit(bare))
    conductor().forget()

    # --- (f) fix and blocked together: in place, then the gap closes it --------------------------------
    bound(3)
    conductor().start(doc)
    conductor().submit("")
    placed = conductor().submit(json.dumps([{"code": "Z1", "evidence": "two claims unrendered", "verdict": "fail",
                                             "fix": "render what can be", "blocked": "the second needs the bench"}]))
    mixed = conductor().submit(json.dumps([{"code": "Z1", "evidence": "one claim rendered, one not",
                                            "verdict": "fail", "blocked": "the second needs the bench"}]))
    mixed_shown = render(mixed) if mixed is not None else ""
    if (placed is not None and "IN PLACE" in (placed.deviation or "") and mixed is not None and mixed.wait
            and "(a gap declared: Z1 -- the second needs the bench)" in mixed_shown and _repairs(home.meta) == 0):
        held("(f) fix and blocked: in place, then the gap closes it", "the repair plays in place, the "
             "mini-proof declares the gap, the FINAL says it; no repair counted")
    else:
        failures.append(f"  ✗ (f) fix and blocked         {(placed.deviation if placed else '')!r} "
                        f"wait={mixed and mixed.wait} {(mixed.deviation if mixed else '')!r} repairs={_repairs(home.meta)}")
    conductor().forget()
    return len(failures)
