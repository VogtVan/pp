"""Scenario `prove` -- the pattern `rules/prove`, played from its demonstration:
- a written PROVE with nothing due resolves on its line; after a production it presents as an INFER
  without a brief, its line naming the codes at risk, piped on stdin; an empty array names no law and
  repairs; `ok` lets the run out, `n/a` passes and repairs nothing, a verdict outside the three words
  deviates
- the coverage: a code the line asks left unnamed deviates, named; the complete proof passes; a
  behavior code in addition passes; a fixed code's mini-proof names it alone among the others;
  nineteen codes pass whole
- the point of proof: a PROVE asks every law of production on screen, the inherited one included, and
  a code no law in force carries repairs; it pays armed or not (a callee's line under its caller's
  law, proven by the caller's PROVE); without a PROVE nothing is due and nothing is traced; idle, it
  renders a line; a document without a law of production reaches its AWAIT without a proof block;
  the proof asks the production laws alone; a replayed root proves every productive passage; the
  frontier stands bare after the PROVE; each segment proves before its own delivery; a law of
  production an overlay adds to the root arms the root's PROVE before the AWAIT
- under the principal's conduction: the same PROVE asked, proven, the run parked
SETTINGS and the placement of the overlay are written at the test's time.
"""
from __future__ import annotations

import json

from conductor import Refusal, render
from tests.harness import demonstrated, demos, plant, principal, traced

DRAWER, PATTERN = "rules", "prove"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("ALONE.md", "BARE.md", "CALLER.md", "CLAIM.md", "COVERED.md", "CRAFT.md", "IDLE.md", "LATER.md",
         "LOOP.md", "MANY.md", "MFIN.md", "MUTE.md", "MUTECALL.md", "NOLAW.md", "NOPROVE.md", "PLAIN.md",
         "QUIET.md", "TFIN.md", "TURN.overlay.md", "TWO.md")
FUSION = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: {fusion}\n---\n"
NO_BEARING = "no bearing on this production"


def _said(code: str, evidence: str, verdict: str, **more: str) -> str:
    """-> a proof of one object."""
    return json.dumps([{"code": code, "evidence": evidence, "verdict": verdict, **more}])


def _covering(codes: list[str], verdict: str = "n/a") -> str:
    """-> a proof of one object per code, all of one verdict."""
    return json.dumps([{"code": code, "evidence": NO_BEARING, "verdict": verdict} for code in codes])


def _keyword(block) -> str:
    """-> the keyword of the block's instruction, "" when none."""
    return block.instruction.keyword if block is not None and block.instruction is not None else ""


def asked(bench) -> None:
    """The PROVE's line, the verdicts."""
    held, failures = bench.held, bench.failures
    env = bench.env("prove", bare=True)
    plant(env, DRAWER, PATTERN, ("ALONE.md", "CLAIM.md"))

    def c():
        return env.conductor("t")

    def opened(name: str):
        c().forget()
        return c().start(env.made / "procs" / name)

    alone = opened("ALONE.md")
    if alone is not None and alone.wait and "nothing due" in render(alone) and alone.output != "proof":
        held("a PROVE with nothing due resolves on its line", "ALONE, one PROVE and no law: the step "
             "resolves on its line and the run parks")
    else:
        failures.append(f"  ✗ the lone PROVE              {alone and render(alone)[-200:]!r}")

    opened("CLAIM.md")
    block = c().submit("")
    shown = render(block)
    if (block.command == "INFER" and block.output == "proof"
            and block.next_call.endswith(" - <<'EOF'\n<proof>\nEOF")
            and "proving" not in shown and "INFER proof [Z1]" in shown
            and "on all produced areas => tool  (" in shown):
        held("PROVE presents as INFER, briefless", "the line says the form, the codes at risk, their "
             "plate and the tool; the closing shows the heredoc with `<proof>` in the production's place")
    else:
        failures.append(f"  ✗ the proof block             {block.command!r} {block.output!r}")
    empty = c().submit("[]")
    if empty.position == 1 and empty.command == "INFER" and "names no law of production" in empty.deviation:
        held("a proof names the codes at risk", "an empty array proves nothing: the document repairs")
    else:
        failures.append(f"  ✗ the empty array             {empty.position} {empty.deviation!r}")
    c().submit("")
    passed = c().submit(_said("Z1", "plain words", "ok"))
    if passed is not None and passed.wait:
        held("an ok proof lets the run out", "the checkpoint opens, the run parks")
    else:
        failures.append(f"  ✗ ok                          {passed and passed.command!r}")

    opened("CLAIM.md")
    c().submit("")
    na = c().submit(_said("Z1", "no naming in this production", "n/a"))
    if na is not None and na.wait:
        held("n/a passes and repairs nothing", "a law without bearing is said, not dressed as ok")
    else:
        failures.append(f"  ✗ n/a                         {na and na.command!r}")
    opened("CLAIM.md")
    c().submit("")
    odd = c().submit(_said("Z1", "x", "maybe"))
    if odd.deviation and "`ok`, `fail` or `n/a`" in odd.deviation:
        held("a verdict outside the three words deviates", "the enumeration says its three words")
    else:
        failures.append(f"  ✗ the stranger verdict        {odd.deviation!r}")
    c().forget()


def coverage(bench) -> None:
    """Every code the line asks takes an object; one left unnamed deviates, named."""
    held, failures = bench.held, bench.failures
    env = bench.env("prove-coverage", bare=True)
    plant(env, DRAWER, PATTERN, ("COVERED.md", "MANY.md"))
    three = ["Z1", "Z2", "Z3"]

    def c():
        return env.conductor("t")

    def opened(name: str):
        c().forget()
        c().start(env.made / "procs" / name)
        return c().submit("")

    line = opened("COVERED.md")
    holed = c().submit(_covering(["Z1", "Z2"]))
    if (line is not None and list(line.judged) == three and holed is not None and holed.repair == 1
            and "Z3" in (holed.deviation or "") and "unnamed" in (holed.deviation or "")):
        held("a code left unnamed deviates", f"the line asks {list(line.judged)}, the proof names two: REPAIR 1, "
             "the DEVIATION names Z3")
    else:
        failures.append(f"  ✗ the unnamed code            {line and list(line.judged)} {holed and holed.deviation!r}")
    opened("COVERED.md")
    whole = c().submit(_covering(three))
    if whole is not None and whole.wait and not whole.repair and not whole.deviation:
        held("the complete proof passes", "three objects for three codes asked: the AWAIT renders")
    else:
        failures.append(f"  ✗ the complete proof          {whole and whole.deviation!r}")
    opened("COVERED.md")
    extra = c().submit(_covering(three + ["B9"]))
    if extra is not None and extra.wait and not extra.deviation:
        held("a behavior code in addition passes", "B9 named beside Z1-Z3: no deviation, the AWAIT renders")
    else:
        failures.append(f"  ✗ the behavior code           {extra and extra.deviation!r}")
    opened("COVERED.md")
    placed = c().submit(json.dumps([{"code": "Z1", "evidence": "a claim unrendered", "verdict": "fail", "fix": "render it"},
                                    {"code": "Z2", "evidence": "held", "verdict": "ok"},
                                    {"code": "Z3", "evidence": "no bearing", "verdict": "n/a"}]))
    mini = c().submit(_said("Z1", "rendered: grep -c 1", "ok"))
    if placed is not None and "IN PLACE" in (placed.deviation or "") and mini is not None and mini.wait and not mini.deviation:
        held("the mini-proof covers the repaired code alone", "Z1 fixed in place among three, its mini-proof "
             "names Z1 alone: the AWAIT renders")
    else:
        failures.append(f"  ✗ the mini-proof              {placed and placed.deviation!r} {mini and mini.deviation!r}")
    many = [f"Y{n}" for n in range(1, 20)]
    opened("MANY.md")
    full_proof = _covering(many)
    passed = c().submit(full_proof)
    if passed is not None and passed.wait and not passed.deviation:
        held("nineteen codes, the complete proof passes", f"19 objects, {len(full_proof)} c")
    else:
        failures.append(f"  ✗ nineteen codes              {passed and passed.deviation!r}")
    c().forget()


def checkpoint(bench) -> None:
    """The written PROVE: what it asks, what it pays, where nothing is due, where it lands."""
    held, failures = bench.held, bench.failures
    env = bench.env("prove-checkpoint")
    env.write("SETTINGS.md", FUSION.format(fusion="max"))
    plant(env, DRAWER, PATTERN, ("BARE.md", "CALLER.md", "CRAFT.md", "IDLE.md", "LATER.md", "LOOP.md", "MFIN.md",
                                 "MUTE.md", "MUTECALL.md", "NOLAW.md", "NOPROVE.md", "PLAIN.md", "QUIET.md",
                                 "TFIN.md", "TWO.md"))

    def c():
        return env.conductor("t")

    def opened(name: str):
        one = c()
        one.forget()
        return one.start(one.boot(name))

    def blocks(name: str, cap: int = 6) -> list:
        """-> the blocks of a fresh run of `name`, bare submits, the proofs piped n/a."""
        seen = [opened(name)]
        while seen[-1] is not None and len(seen) < cap and not seen[-1].wait:
            last = seen[-1]
            answer = (json.dumps([{"code": code, "evidence": "bench", "verdict": "n/a"} for code in last.judged])
                      if _keyword(last) == "PROVE" else "")
            try:
                seen.append(c().submit(answer))
            except Refusal:
                break
        return [one for one in seen if one is not None]

    first = opened("CALLER.md")
    text = render(first) if first is not None else ""
    armed = (_keyword(first) == "PROVE" and "X1" in text and "Y1" in text
             and "<<'EOF'\n<proof>\nEOF" in text)
    foreign = c().submit(_said("Q9", "no such law", "ok"))
    repaired = (foreign is not None and "REPAIR" in render(foreign) and "not in force" in (foreign.deviation or "")
                and _keyword(foreign) == "PROVE")
    closed = c().submit(json.dumps([{"code": "X1", "evidence": "no bearing on the line", "verdict": "n/a"},
                                    {"code": "Y1", "evidence": "short indeed", "verdict": "ok"}]))
    if armed and repaired and closed is not None and closed.wait:
        held("a PROVE asks every law on screen", "CRAFT's PROVE asks its Y1 and CALLER's X1; a code no law in "
             "force carries repairs; every code named lets the run out")
    else:
        failures.append(f"  ✗ the written checkpoint      {armed}/{repaired}/{closed and closed.wait} {text[-200:]!r}")

    later = opened("LATER.md")
    later_text = render(later) if later is not None else ""
    if ("LATER ▸ BARE{" in later_text and "INFER any => words  (BARE)" in later_text
            and _keyword(later) == "PROVE" and list(later.judged) == ["X2"]):
        held("it pays armed or not", "BARE produces under X2 alone and pops without a PROVE; LATER's PROVE "
             "asks X2 for that line")
    else:
        failures.append(f"  ✗ armed or not                {_keyword(later)} {later_text[-200:]!r}")
    c().submit(_said("X2", "held", "ok"))

    no_blocks = blocks("NOPROVE.md")
    no_text = "\n".join(render(one) for one in no_blocks)
    mute_blocks = blocks("MUTECALL.md")
    if (not any(_keyword(one) == "PROVE" for one in no_blocks) and "▶ AWAIT" in no_text and "N1" in no_text
            and "PROVE" not in [_keyword(one) for one in mute_blocks]
            and "Y2" in "\n".join(render(one) for one in mute_blocks)):
        held("no PROVE, nothing due", "NOPROVE closes on its AWAIT without a checkpoint under N1; MUTE pops "
             "under its Y2 without one")
    else:
        failures.append(f"  ✗ nothing due                 {[_keyword(one) for one in no_blocks]}")

    idle = opened("IDLE.md")
    idle_text = render(idle) if idle is not None else ""
    nolaw_text = "\n".join(render(one) for one in blocks("NOLAW.md"))
    if ("nothing due since the last proof" in idle_text and "INFER any => words  (IDLE)" in idle_text
            and _keyword(idle) == "PROVE" and list(idle.judged) == ["I1"]
            and "no law of production in force" in nolaw_text and "▶ AWAIT" in nolaw_text):
        held("a PROVE with nothing due renders a line", "IDLE's first PROVE resolves on a line, its second asks "
             "I1 once the line is said; NOLAW's PROVE says no law of production is in force")
    else:
        failures.append(f"  ✗ the idle line               {idle_text[-200:]!r} {nolaw_text[-200:]!r}")

    env.write("SETTINGS.md", FUSION.format(fusion="none"))
    quiet = opened("QUIET.md")
    closing = quiet if quiet.wait else c().submit("")
    if (quiet.command == "INFER" and closing is not None and closing.wait and closing.output != "proof"
            and "no law of production in force" in render(closing)):
        held("no law of production, no proof block", "QUIET, behavior laws alone and a PROVE, reaches its "
             "AWAIT without a proof block; the PROVE's line says why")
    else:
        failures.append(f"  ✗ the quiet checkpoint        {closing and render(closing)[-160:]!r}")

    opened("TWO.md")
    c().submit("")
    behavior = c().submit(_said("H1", "said first", "ok"))
    c().submit("")
    production = c().submit(_said("P1", "wc -w -> 4", "ok"))
    if (behavior.deviation and "names no law of production" in behavior.deviation
            and production is not None and production.wait):
        held("the proof asks the production laws alone", "H1 alone names no law of production; P1 alone lets "
             "the run out")
    else:
        failures.append(f"  ✗ the production filter       {behavior.deviation!r}")

    env.write("SETTINGS.md", FUSION.format(fusion="max"))
    first_is = _keyword(opened("LOOP.md")) == "PROVE"
    parked = c().submit(_said("L1", "landed", "ok"))
    second_is = _keyword(c().submit("")) == "PROVE"
    if first_is and parked is not None and parked.wait and second_is:
        held("a replayed root proves every productive passage", "the PROVE asks at each passage; the parked "
             "run reopens and earns its own")
    else:
        failures.append(f"  ✗ the replayed passages       {first_is}/{parked and parked.wait}/{second_is}")

    env.write("SETTINGS.md", FUSION.format(fusion="none"))
    opened("TFIN.md")
    proof = c().submit("")
    front = c().submit(_said("G1", "landed", "ok"))
    front_text = render(front) if front is not None else ""
    lap2 = c().submit("")
    if _keyword(proof) == "PROVE" and "▶ AWAIT" in front_text and "proof given" not in front_text and _keyword(lap2) != "PROVE":
        held("the frontier stands bare after the PROVE", "the proof lands before the delivery, the AWAIT "
             "foresees nothing, the next passage opens on fresh work")
    else:
        failures.append(f"  ✗ the frontier                {_keyword(proof)}/{_keyword(lap2)} {front_text[-120:]!r}")

    opened("MFIN.md")
    proven = _said("F1", "landed", "ok")
    p1 = c().submit("")
    f1 = c().submit(proven)
    p2 = c().submit("")
    f2 = c().submit(proven)
    end = c().submit("")
    if (_keyword(p1) == "PROVE" and _keyword(p2) == "PROVE" and f1 is not None and _keyword(f1) == "INFER"
            and not f1.wait and f2 is not None and f2.wait and end is not None and _keyword(end) == "INFER"):
        held("each segment proves before its own delivery", "two checkpoints, each ahead of its delivery; the "
             "root exhausted parks the run")
    else:
        failures.append(f"  ✗ the segments                {_keyword(p1)}/{_keyword(f1)}/{_keyword(p2)}/{_keyword(end)}")

    opened("PLAIN.md")
    plain = traced(env, "t")
    if plain and "PROVE" not in json.dumps(plain):
        held("no PROVE written, nothing traced", "PLAIN writes no PROVE: no proof kind in its trace")
    else:
        failures.append(f"  ✗ the plain trace             {len(plain)} event(s)")
    c().forget()


def rooted(bench) -> None:
    """A law of production an overlay adds to the root arms the root's PROVE before the AWAIT."""
    held, failures = bench.held, bench.failures
    env = bench.env("prove-root")
    env.write("procs/TURN.md", (DEMO / "TURN.overlay.md").read_text(encoding="utf-8"))

    def w():
        return env.conductor(None)

    work = w().resume(w().boot("BOOT.md"))
    proving = w().submit("")
    proof = json.dumps([{"code": one.code, "evidence": "held", "verdict": "ok"} for one in proving.constraints])
    waiting = w().submit(proof)
    following = w().resume(w().boot("BOOT.md"))
    if (work.document == "TURN" and not work.wait and str(work.command).startswith("WORK")
            and proving.output == "proof" and waiting is not None and waiting.wait and not waiting.command
            and "▶ AWAIT" in render(waiting) and waiting.document == "TURN"
            and following is not None and following.document == "TURN" and not following.wait
            and following.instruction.repairs == 0):
        held("an overlay's law arms the root's PROVE", "TURN's WORK, its PROVE asks the added Z2, proven: AWAIT; "
             "the next message reopens TURN with no repair")
    else:
        failures.append(f"  ✗ the root's PROVE            {waiting and waiting.command!r} {following and following.document!r}")


def conducted(bench) -> None:
    """Under the principal's conduction the same PROVE is asked, proven, and the run parks."""
    held, failures = bench.held, bench.failures
    env = bench.env("prove-principal", bare=True)
    plant(env, DRAWER, PATTERN, ("CLAIM.md",))
    opener = env.conductor()
    opener.forget()
    principal(lambda: opener.start(env.made / "procs" / "CLAIM.md"))
    key = opener.run_id
    proving = principal(lambda: env.conductor(key).submit(""))
    parked = principal(lambda: env.conductor(key).submit(_said("Z1", "plain words", "ok")))
    if proving is not None and proving.output == "proof" and list(proving.judged) == ["Z1"] and parked is not None and parked.wait:
        held("both conductions ask the same proof", "under the principal's conduction CLAIM's PROVE asks Z1, "
             "the proof lets the run park")
    else:
        failures.append(f"  ✗ the principal's proof       {proving and proving.output!r} {parked and parked.wait}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    asked(bench)
    coverage(bench)
    checkpoint(bench)
    rooted(bench)
    conducted(bench)
    return 0
