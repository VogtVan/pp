"""Scenario `repair` -- the pattern `rules/repair`, played from its demonstration:
- a bare `fail` reopens the whole document from its first step, `REPAIR` in the heading, the failing
  objects in the DEVIATION; a named fix repairs in place and its mini-proof re-proves the fixed code
  alone, exactly, a relapse closing the cheap branch; a missed PICK reopens the document without
  serving its reading again; a block served again without an answer comes back the same, no repair
- the way out of a `fail`: a declared gap closes the checkpoint and the closing says it, an empty one
  is a bare fail; fixes that hold never wear the bound nor -stats; a relapse counts one; a fix and a gap
  together; an empty answer to a PROVE repairs
- the bound: bare fails, misses at a PROVE and missed PICKs hand back at `work_repairs_allowed`
  (`repair-exhausted`), the count kept across the reopenings
- a fused batch repairs whole, the heading of every replayed step saying `REPAIR`, under both
  conductions; under the principal's conduction the same repair replays
SETTINGS and the reading are written at the test's time.
"""
from __future__ import annotations

import json

from conductor import Refusal, persistence, render, revive
from conductor.state import traces
from tests.harness import demonstrated, plant, principal, traced

DRAWER, PATTERN = "rules", "repair"
DEMOS = ("BROKE.md", "CALLER.md", "CLAIM.md", "CRAFT.md", "PAIR.md", "REDO.md")
BOUND = "---\nname: SETTINGS\nkind: doc\nwork_repairs_allowed: {allowed}\n---\n"
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n"
LISTED = '["prover"]'
DRIFT = "tone drifted"
GAP = "the bench cannot run here"
SECOND_GAP = "the second needs the bench"


def _said(code: str, evidence: str, verdict: str, **more: str) -> str:
    """-> a proof of one object."""
    return json.dumps([{"code": code, "evidence": evidence, "verdict": verdict, **more}])


def _repairs(env) -> int:
    """-> the repairs counted on the run's saved instructions, every frame."""
    restored = persistence.restore(persistence.slot_of(env.made, "t"), revive)
    return (sum(one.repairs for frame in restored[1].frames for one in frame.procedure.instructions)
            if restored else -1)


def _stated(env) -> int:
    """-> the repairs `-stats` counts on the run's trace."""
    return sum(one.repairs for one in traces.exchanges(traced(env, "t")))


def replays(bench) -> None:
    """A fail replays, a fix repairs in place, a miss reopens without re-serving, a re-serve is no miss."""
    held, failures = bench.held, bench.failures
    env = bench.env("repair", bare=True)
    plant(env, DRAWER, PATTERN, ("CLAIM.md", "REDO.md"))
    env.write("READ.md", "some reading\n")

    def c():
        return env.conductor("t")

    def opened(name: str):
        c().forget()
        return c().start(env.made / "procs" / name)

    opened("CLAIM.md")
    c().submit("")
    failed = c().submit(_said("Z1", DRIFT, "fail"))
    if (failed.position == 1 and "your own proof failed" in failed.deviation and DRIFT in failed.deviation
            and "REPAIR 1" in render(failed) and "DEVIATION" in render(failed)):
        held("a bare fail reopens the document", "REPAIR from step 1, the failing object in the DEVIATION")
    else:
        failures.append(f"  ✗ the bare fail               {failed.position} {failed.deviation!r}")

    reword = "reword plainly"
    opened("CLAIM.md")
    c().submit("")
    fixed = c().submit(_said("Z1", DRIFT, "fail", fix=reword))
    mini = c().submit(_said("Z1", "rewritten, greps clean", "ok"))
    if "IN PLACE" in (fixed.deviation or "") and fixed.position == 2 and reword in fixed.deviation and mini.wait:
        held("a named fix repairs in place", "the document stands, the failed code alone re-proves, the "
             "mini-proof lets the run out")
    else:
        failures.append(f"  ✗ the fix in place            {fixed.deviation!r}")
    opened("CLAIM.md")
    c().submit("")
    c().submit(_said("Z1", "off", "fail", fix="say it straight"))
    wrong_mini = c().submit(_said("Z9", "x", "ok"))
    relapse = c().submit(_said("Z1", "still off", "fail"))
    if ("covers exactly" in (wrong_mini.deviation or "") and wrong_mini.position == 2
            and "failed AGAIN" in (relapse.deviation or "") and relapse.position == 1):
        held("the mini-proof is exact and a relapse replays", "a wrong coverage asks the codes again, a second "
             "fail closes the cheap branch: the document reopens")
    else:
        failures.append(f"  ✗ the mini-proof              {wrong_mini.deviation!r} {relapse.deviation!r}")

    opened("REDO.md")
    again = c().resume(env.made / "procs" / "REDO.md")
    again2 = c().resume(env.made / "procs" / "REDO.md")
    if render(again2) == render(again) and again2.instruction.repairs == 0:
        held("a block served again is no miss", "the very same block, no repair counted")
    else:
        failures.append(f"  ✗ the re-serve                repairs={again2.instruction.repairs}")
    c().submit(LISTED)
    missed = c().submit("nobody")
    refed = c().submit(LISTED)
    if ("not in OPTIONS" in missed.deviation and "REPAIR" in render(missed)
            and "READ.md" not in [n for n, _ in refed.payloads] and str(refed.instruction) == "PICK member"
            and c().submit("prover").wait):
        held("a missed PICK reopens the document, re-serving nothing", "the chained steps replay, the reading "
             "stays proven")
    else:
        failures.append(f"  ✗ the missed PICK             {[n for n, _ in refed.payloads]} {missed.deviation!r}")
    c().forget()


def ways_out(bench) -> None:
    """An honest fail has a way out; a fix that holds does not wear the bound; the bound hands back."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("repair-exits", bare=True)
    plant(env, DRAWER, PATTERN, ("CLAIM.md", "REDO.md"))
    env.write("READ.md", "some reading\n")

    def c():
        return env.conductor("t")

    def bound(allowed: int) -> None:
        env.write("SETTINGS.md", BOUND.format(allowed=allowed))

    def opened(name: str = "CLAIM.md"):
        c().forget()
        return c().start(env.made / "procs" / name)

    bound(3)
    opened()
    c().submit("")
    closed = c().submit(_said("Z1", "the claims stand unrendered", "fail", blocked=GAP))
    gaps = [one for one in traced(env, "t") if one.get("kind") == "blocked"]
    counted = sum(one.blocked for one in traces.exchanges(traced(env, "t")))
    if (closed is not None and closed.wait and not closed.repair and tuple(map(tuple, closed.gaps)) == (("Z1", GAP),)
            and GAP in render(closed) and gaps and gaps[-1].get("gaps") == [{"code": "Z1", "text": GAP}] and counted == 1):
        held("a declared gap closes the checkpoint", "fail + blocked: the AWAIT renders and says the gap, no "
             "repair, the trace says `blocked` (-stats counts 1 gap)")
    else:
        failures.append(f"  ✗ the declared gap            {closed and closed.deviation!r} {gaps[-1:]} {counted}")
    opened()
    c().submit("")
    empty = c().submit(_said("Z1", "off", "fail", blocked="  "))
    if empty is not None and empty.repair == 1 and "your own proof failed" in (empty.deviation or ""):
        held("an empty blocked is a bare fail", "REPAIR 1, the document replays")
    else:
        failures.append(f"  ✗ the empty blocked           {empty and empty.deviation!r}")

    bound(1)
    opened()
    counts, outcome = [], ""
    try:
        for turn in range(3):
            c().submit("" if turn == 0 else f"message {turn + 1}")
            if turn:
                c().submit("")
            c().submit(_said("Z1", "a claim unrendered", "fail", fix="render the claim"))
            last = c().submit(_said("Z1", "rendered: grep -c 1", "ok"))
            counts.append(_repairs(env))
            outcome = "parked" if last is not None and last.wait else "other"
    except Refusal as refused:
        outcome = refused.code
    stated = _stated(env)
    if counts == [0, 0, 0] and outcome == "parked" and stated == 0:
        held("fixes that hold never wear the bound", "work_repairs_allowed 1, three exchanges of fail + fix "
             "then a mini-proof ok: repairs 0, 0, 0, and -stats counts none")
    else:
        failures.append(f"  ✗ the fixes and the bound     {counts} {outcome!r} stats={stated}")

    bound(3)
    opened()
    c().submit("")
    c().submit(_said("Z1", "off", "fail", fix="say it"))
    relapse = c().submit(_said("Z1", "still off", "fail"))
    if relapse is not None and "failed AGAIN" in (relapse.deviation or "") and _repairs(env) == 1 == _stated(env):
        held("a relapse counts one", "the cheap branch closes, the document replays, one repair counted, "
             "-stats the same")
    else:
        failures.append(f"  ✗ the relapse                 {relapse and relapse.deviation!r} {_repairs(env)} "
                        f"stats={_stated(env)}")

    opened()
    c().submit("")
    placed = c().submit(_said("Z1", "two claims unrendered", "fail", fix="render what can be", blocked=SECOND_GAP))
    mixed = c().submit(_said("Z1", "one claim rendered, one not", "fail", blocked=SECOND_GAP))
    if ("IN PLACE" in (placed.deviation or "") and mixed is not None and mixed.wait
            and tuple(map(tuple, mixed.gaps)) == (("Z1", SECOND_GAP),) and SECOND_GAP in render(mixed)
            and _repairs(env) == 0):
        held("a fix and a gap together", "the repair plays in place, the mini-proof declares the gap, the AWAIT "
             "says it; no repair counted")
    else:
        failures.append(f"  ✗ fix and gap                 {placed.deviation!r} {mixed and mixed.deviation!r}")

    bound(2)
    opened()
    bare = _said("Z1", "the bench is out of reach", "fail")
    for _ in range(2):
        c().submit("")
        c().submit(bare)
    c().submit("")
    expect("repair-exhausted", lambda: c().submit(bare))

    bound(1)
    opened()
    c().submit("")
    c().submit(_said("Z1", "off", "fail"))
    c().submit("")
    expect("repair-exhausted", lambda: c().submit(_said("Z1", "still off", "fail")))

    bound(3)
    opened("REDO.md")
    c().submit(LISTED)
    for _ in range(3):
        c().submit("nobody")
        c().submit(LISTED)
    expect("repair-exhausted", lambda: c().submit("nobody"))
    c().forget()


def at_prove(bench) -> None:
    """An empty answer to a PROVE repairs; misses at a PROVE hand back at the bound."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("repair-prove")
    plant(env, DRAWER, PATTERN, ("CALLER.md", "CRAFT.md"))
    env.write("SETTINGS.md", FUSED)

    def c():
        return env.conductor("t")

    def opened(name: str):
        one = c()
        one.forget()
        return one.start(one.boot(name))

    asked = opened("CRAFT.md")
    empty = c().submit("")
    if asked.instruction.keyword == "PROVE" and empty is not None and "REPAIR" in render(empty):
        held("an empty answer to a PROVE repairs", "nothing piped is no proof: the document replays")
    else:
        failures.append(f"  ✗ the empty answer            {empty and render(empty)[-150:]!r}")
    opened("CALLER.md")
    lame = _said("Q9", "no such law", "ok")
    for _ in range(3):                         # work_repairs_allowed: the instance's default, 3
        c().submit(lame)
    expect("repair-exhausted", lambda: c().submit(lame))
    c().forget()


def closed_early(bench) -> None:
    """A repaired PROVE the output closes early is asked again at the bare call, never judged empty."""
    held, failures = bench.held, bench.failures
    env = bench.env("repair-broke", bare=True)
    env.write("SETTINGS.md", FUSED)               # the INFER and the `§` in one output
    plant(env, DRAWER, PATTERN, ("BROKE.md",))

    def c():
        return env.conductor("t")

    c().forget()
    c().start(env.made / "procs" / "BROKE.md")   # the INFER batched, the `§` closes the output
    asked = c().submit("")                       # the bare call crosses: the PROVE asked
    repaired = c().submit(_said("B1", "off", "fail"))   # REPAIR 1: the INFER replays, the `§` closes again
    again = c().submit("")                       # the bare call crosses again
    count = _repairs(env)
    closed = c().submit(_said("B1", "landed", "ok"))
    if (asked is not None and asked.instruction.keyword == "PROVE" and asked.command == "INFER"
            and repaired is not None and repaired.repair == 1 and not repaired.command
            and again is not None and again.instruction.keyword == "PROVE" and again.command == "INFER"
            and not again.deviation and count == 1 and closed is not None and closed.wait
            and not closed.deviation):
        held("a repaired PROVE closed early is asked again", "REPAIR 1 replays the INFER and the `§` "
             "closes the output on the PROVE; the bare call asks it again, no empty answer, one repair "
             "counted, the proof lets the run park")
    else:
        failures.append(f"  ✗ repaired, closed early       {asked and asked.instruction.keyword}/"
                        f"{repaired and repaired.repair} {again and again.command!r} "
                        f"{(again.deviation if again else '')!r} repairs={count} "
                        f"replayed={repaired and repaired.command!r}")
    c().forget()


def fused(bench) -> None:
    """A fused batch repairs whole."""
    held, failures = bench.held, bench.failures
    env = bench.env("repair-fused", pin=False)
    env.write("SETTINGS.md", FUSED)
    plant(env, DRAWER, PATTERN, ("PAIR.md",))
    runner = env.conductor("t")
    runner.forget()
    runner.start(env.made / "procs" / "PAIR.md")
    failed = env.conductor("t").submit(_said("P9", "off", "fail"))
    if failed is not None and failed.repair >= 1 and "PAIR{1/2} · REPAIR 1" in render(failed):
        held("a fused batch repairs whole", "the failing proof replays the document: the batch re-renders, "
             "the replayed WORK's heading says REPAIR 1")
    else:
        failures.append(f"  ✗ the fused repair            {failed and failed.repair} {failed and render(failed)[:200]!r}")
    env.conductor("t").forget()
    opener = env.conductor()
    opener.forget()
    principal(lambda: opener.start(env.made / "procs" / "PAIR.md"))
    key = opener.run_id
    led = principal(lambda: env.conductor(key).submit(_said("P9", "off", "fail")))
    if led is not None and "PAIR{1/2} · REPAIR 1" in render(led):
        held("the same mark under the principal's conduction", "the replayed WORK's heading says REPAIR 1")
    else:
        failures.append(f"  ✗ the principal's fused repair {led and render(led)[:200]!r}")
    env.conductor(key).forget()


def conducted(bench) -> None:
    """Under the principal's conduction the same fail replays the document."""
    held, failures = bench.held, bench.failures
    env = bench.env("repair-principal", bare=True)
    plant(env, DRAWER, PATTERN, ("CLAIM.md",))
    opener = env.conductor()
    opener.forget()
    principal(lambda: opener.start(env.made / "procs" / "CLAIM.md"))
    key = opener.run_id
    principal(lambda: env.conductor(key).submit(""))
    failed = principal(lambda: env.conductor(key).submit(_said("Z1", DRIFT, "fail")))
    principal(lambda: env.conductor(key).submit(""))
    parked = principal(lambda: env.conductor(key).submit(_said("Z1", "plain words", "ok")))
    if failed is not None and failed.position == 1 and "REPAIR 1" in render(failed) and parked is not None and parked.wait:
        held("both conductions repair the same", "under the principal's conduction the bare fail reopens CLAIM, "
             "REPAIR 1; the proof then lets the run park")
    else:
        failures.append(f"  ✗ the principal's repair      {failed and failed.position} {parked and parked.wait}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    replays(bench)
    ways_out(bench)
    at_prove(bench)
    closed_early(bench)
    fused(bench)
    conducted(bench)
    return 0
