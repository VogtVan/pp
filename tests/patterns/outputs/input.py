"""Scenario `input` -- the pattern `outputs/input`, played from its demonstration:
- a called document that declares `input:` opens on its caller's production: a line travels on the
  call's line; a callee's last production feeds the caller's next step across the pop -- a PICK, or a
  CALL whose callee takes it; `any` takes every form; a form the callee does not take refuses
  `format-mismatch`, next to the caller as across the pop
- a consumer that opens on an INFER is served what it received under `input`, once, under both
  conductions, and again after `-compacted`; one that opens on a PICK sees it as its OPTIONS alone
- a proven production crosses its PROVE: the consumer plays after the proof
"""
from __future__ import annotations

import json

from conductor import persistence, revive
from tests.harness import demonstrated, plant, principal

DRAWER, PATTERN = "outputs", "input"
DEMOS = ("ANYONE.md", "CHAIN.md", "ELECTOR.md", "FEEDELECTOR.md", "FEEDTAKER.md", "LISTER.md", "MAKERJ.md",
         "MAKERT.md", "MISMATCH.md", "NAMED.md", "PICKER.md", "PIPER.md", "SEEDER.md", "SHIP.md", "STRICT.md",
         "TAKER.md", "TOLERANT.md")
GIVEN = {"ok": 1}


def _said(code: str, evidence: str, verdict: str) -> str:
    return json.dumps([{"code": code, "evidence": evidence, "verdict": verdict}])


def feeds(bench) -> None:
    """The seed, the flow across the pop, `any`, the mismatch."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("input", bare=True)
    plant(env, DRAWER, PATTERN, DEMOS)

    def c():
        return env.conductor("t")

    def opened(name: str):
        c().forget()
        return c().start(env.made / "procs" / name)

    seeded = opened("SEEDER.md")
    ended = c().submit("io")
    if seeded.next_call.endswith(" <output>") and ended is not None and ended.wait:
        held("the seed opens the callee", "a `line` travels on the call's line; NAMED opens on SEEDER's production")
    else:
        failures.append(f"  ✗ the seed                    {seeded.next_call!r}")
    expect("format-mismatch", lambda: opened("MISMATCH.md"))

    asked = opened("PICKER.md")
    flowed = c().submit('["io"]')
    if asked.document == "LISTER" and list(flowed.options) == ["io"] and str(flowed.instruction) == "PICK member":
        held("a CALL yields its callee's production", "LISTER's list feeds PICKER's PICK")
    else:
        failures.append(f"  ✗ the flow                    {flowed.options!r}")
    chained = opened("CHAIN.md")
    shipped = c().submit('{"through": true}')
    if " -   (" in chained.next_call and chained.document == "MAKERJ" and shipped is not None and shipped.wait:
        held("consumption crosses the pop", "MAKERJ's last INFER is consumed by CHAIN's next CALL: captured, "
             "flowed, shipped")
    else:
        failures.append(f"  ✗ across the pop              {chained.next_call!r}")
    tolerant = opened("TOLERANT.md")
    if tolerant.document == "MAKERT" and "stdin" in tolerant.next_call:
        held("`any` takes every form", "MAKERT's table feeds ANYONE's `input: any` without a mismatch")
    else:
        failures.append(f"  ✗ any                         {tolerant.document!r}")
    c().forget()
    expect("format-mismatch", lambda: opened("STRICT.md"))
    c().forget()


def served(bench) -> None:
    """A consumer is served what it received; a PICK sees it as its OPTIONS alone."""
    held, failures = bench.held, bench.failures
    env = bench.env("input-served", bare=True)
    plant(env, DRAWER, PATTERN, ("ELECTOR.md", "FEEDELECTOR.md", "FEEDTAKER.md", "TAKER.md"))
    seen = {}
    for led in (False, True):
        def played():
            key = "p" if led else "l"
            env.conductor(key).forget()
            env.conductor(key).start(env.made / "procs" / "FEEDTAKER.md")
            return env.conductor(key).submit(json.dumps(GIVEN))
        taken = principal(played) if led else played()
        seen[led] = dict(taken.payloads).get("input") if taken is not None else None
    again = dict(env.conductor("l").compacted().payloads).get("input")
    env.conductor("l").forget()
    env.conductor("e").start(env.made / "procs" / "FEEDELECTOR.md")
    elected = env.conductor("e").submit(json.dumps(["io", "ep"]))
    env.conductor("e").forget()
    if (seen[False] is not None and json.loads(seen[False]) == GIVEN and seen[True] == seen[False]
            and again == seen[False] and elected is not None and elected.instruction.keyword == "PICK"
            and list(elected.options) == ["io", "ep"] and "input" not in dict(elected.payloads)):
        held("a consumer is served what it received", "TAKER opens on its INFER under `input`, the JSON as given, "
             "under both conductions and again after -compacted; ELECTOR opens on its PICK and sees it as its "
             "OPTIONS alone")
    else:
        failures.append(f"  ✗ the input section           {seen!r} again={again!r}")


def proven(bench) -> None:
    """A proven production crosses its PROVE: the consumer plays after the proof."""
    held, failures = bench.held, bench.failures
    env = bench.env("input-proven", bare=True)
    plant(env, DRAWER, PATTERN, ("PIPER.md", "SHIP.md"))
    runner = env.conductor("t")
    runner.forget()
    opening = runner.start(env.made / "procs" / "PIPER.md")
    env.conductor("t").submit('{"ok": 1}')
    done = env.conductor("t").submit(_said("Q1", "json.loads passes", "ok"))
    _, stack, _, _, _, _, _ = persistence.restore(persistence.slot_of(env.made, "t"), revive)
    shipped = stack.frames[0].procedure.instructions[-1]
    if " -   (" in opening.next_call and done is not None and done.wait and shipped.done:
        held("a proven production crosses its PROVE", "PIPER's JSON on stdin, proven, then shipped: the CALL "
             "after the PROVE played")
    else:
        failures.append(f"  ✗ the pipeline                {opening.next_call!r} {shipped.done!r}")
    env.conductor("t").forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    feeds(bench)
    served(bench)
    proven(bench)
    return 0
