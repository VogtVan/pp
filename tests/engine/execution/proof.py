"""Scenario `proof` -- how a production proves itself before it leaves:
- the convergence loop: a proven INFER speaks in chat and its checkpoint presents as an INFER;
  an empty proof, a fail verdict, an ok one, n/a, a stranger verdict; a named fix repairs in
  place, its mini-proof is exact and a relapse replays; the pipeline crosses the checkpoint; a
  REPAIR reopens the document without re-serving; the repair bound holds across the reopenings;
  the wired TURN closes on FINAL and the next message reopens it; a linear FINAL is a pause
- the coverage: every code the proof line asks takes an object, a behavior code in addition
  passes, the mini-proof names the repaired code alone, nineteen codes pass whole
- the way out of a `fail`: a declared gap closes the checkpoint, an empty one is a bare fail,
  fixes that hold never wear the bound, a relapse counts one, bare fails hand back at the bound,
  a fix and a gap together
- the exit checkpoint: a frame proves on its way out, an empty answer repairs, the bound hands
  back, the silences of a frame without law or production, a relic `prove:` refuses, a cycle
  proves every lap, the proof gates the frontier, each segment proves before its delivery
- the sections: one CONSTRAINTS title, production first; the judge asks the production laws
  alone; an overlay adds in the section of its key; no law of production, no checkpoint
"""
from __future__ import annotations

import json

from conductor import Refusal, compiling, instance, persistence, reading, render, revive
from conductor.state import traces
from tests.harness import support

run = support(__file__, "run")

# --- the convergence loop ------------------------------------------------------------------------
CHATTY = ("---\nname: CHATTY\nkind: proc\ndescription: proven, chat-bound\n"
          "constraints.production: |\n  Z1  say it plainly\nproc: |\n  INFER\n---\nwrite the thing\n")
SHIPIT = ("---\nname: SHIPIT\ndescription: consumes the payload\ninput: json\nproc: |\n"
          "  HOOK shipped\n---\nship it\n")
PIPER = ("---\nname: PIPER\nkind: proc\ndescription: proven, pipeline-bound\noutput: json\n"
         "constraints.production: |\n  Q1  the payload is one json value\n"
         "proc: |\n  INFER\n  CALL SHIPIT.md\n---\nmake the payload\n")
REDO = "---\nname: REDO\noutput: json\nproc: |\n  INFER\n  SERVE READ.md\n  PICK member\n---\n"
PAUSED = ("---\nname: PAUSED\nkind: proc\ndescription: a linear proc with a pause\nproc: |\n"
          "  SERVE READ.md\n  FINAL\n  INFER\n---\npause then answer\n")
BOUND = "---\nname: SETTINGS\nkind: doc\nwork_repairs_allowed: {allowed}\n---\n"
WIRED = "---\nname: TURN\nconstraints.production: |\n  +Z2  the turn's work is proven.\n---\n"

# --- the coverage --------------------------------------------------------------------------------
NO_BEARING = "no bearing on this production"

# --- the way out of a fail -----------------------------------------------------------------------
GAPPED = ("---\nname: GAPPED\nkind: proc\ndescription: a proven exchange\ncycle: true\n"
          "constraints.production: |\n  Z1  every claim comes with its rendering\nproc: |\n"
          "  INFER\n  FINAL\n---\nanswer the ask\n")
GAP = "the bench cannot run here"
SECOND_GAP = "the second needs the bench"

# --- the exit checkpoint -------------------------------------------------------------------------
FUSION = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: {fusion}\n---\n"
EXITS = {
    "CALLER": ("---\nname: CALLER\nkind: proc\nconstraints.production: |\n"
               "  X1  the outer law rides the exit.\nproc: |\n  CALL CRAFT.md\n---\nouter\n"),
    "CRAFT": ("---\nname: CRAFT\nkind: proc\nconstraints.production: |\n"
              "  Y1  the crafted line is short.\nproc: |\n  INFER\n---\ncraft one line\n"),
    "PLAIN": "---\nname: PLAIN\nkind: proc\nproc: |\n  INFER\n---\none plain line\n",
    "HOLLOW": "---\nname: HOLLOW\nkind: proc\nproc: |\n  CALL PLAIN.md\n---\nhollow\n",
    "LOOP": ("---\nname: LOOP\nkind: proc\ncycle: true\nconstraints.production: |\n"
             "  L1  the lap's line lands.\nproc: |\n  INFER\n---\none line per cycle\n"),
    "ARMED": ("---\nname: ARMED\nkind: proc\nprove: auto\nconstraints.production: |\n"
              "  Z1  a relic switch.\nproc: |\n  INFER\n---\nrelic\n"),
    "TFIN": ("---\nname: TFIN\nkind: proc\ncycle: true\nconstraints.production: |\n"
             "  G1  the work lands\nproc: |\n  WORK\n  FINAL\n---\nwork then close\n"),
    "MFIN": ("---\nname: MFIN\nkind: proc\nconstraints.production: |\n"
             "  F1  the delivery lands.\nproc: |\n  INFER\n  FINAL\n  INFER\n  FINAL\n---\n"
             "two deliveries\n"),
}

# --- the sections --------------------------------------------------------------------------------
P1 = "P1  the line is under ten words"
H1 = "H1  say what you do before you do it"
TWO = ("---\nname: TWO\nkind: proc\ndescription: two sections\n"
       f"constraints.production: |\n  {P1}\nconstraints.behavior: |\n  {H1}\n"
       "proc: |\n  INFER\n---\nwrite one line\n")
OVERLAY = ("---\nname: TURN\nconstraints.behavior: |\n  +TB9  the overlay's way of doing\n"
           "constraints.production: |\n  +TP9  the overlay's rendered fact\n---\n")
QUIET = ("---\nname: QUIET\nkind: proc\ndescription: behavior alone\n"
         "constraints.behavior: |\n  H2  say what you do before you do it\n"
         "proc: |\n  INFER\n  FINAL\n---\nwrite one line\n")


def _said(code: str, evidence: str, verdict: str, **more: str) -> str:
    """-> a proof of one object."""
    return json.dumps([{"code": code, "evidence": evidence, "verdict": verdict, **more}])


def _keyword(block) -> str:
    """-> the keyword of the block's instruction, "" when none."""
    return block.instruction.keyword if block is not None and block.instruction is not None else ""


def _repairs(env) -> int:
    """-> the repairs counted on the run's saved instructions, every frame."""
    restored = persistence.restore(persistence.slot_of(env.made, "t"), revive)
    return (sum(one.repairs for frame in restored[1].frames for one in frame.procedure.instructions)
            if restored else -1)


def convergence(bench) -> None:
    """The convergence loop of a proven production: the checkpoint, its verdicts, its repairs."""
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    env = bench.env("prover", bare=True)

    def c():
        return run.conductor_of(env, "t")

    retired = env.write("X.md", "---\nname: X\nproc: |\n  PROVE\n---\nx\n")
    expect("prove-retired", lambda: c().start(retired))
    retired.unlink()
    env.write("READ.md", "some reading\n")

    chat_doc = env.write("CHATTY.md", CHATTY)
    chat_opening = c().start(chat_doc)
    if "stdin" not in chat_opening.next_call and chat_opening.command == "INFER":
        held("an unconsumed proven INFER speaks in chat",
             "the closing is the keyed call -- no switch announced: the checkpoint comes")
    else:
        failures.append(f"  ✗ prove chat closing          {chat_opening.next_call!r}")

    prove_block = c().submit("")
    prove_rendered = render(prove_block)
    if (prove_block.command == "INFER" and prove_block.output == "proof"
            and " -\n   (" in prove_block.next_call
            and "proving" not in prove_rendered
            and "INFER proof [" in prove_rendered
            and "on all produced areas => tool (heredoc)" in prove_rendered):
        held("PROVE presents as INFER, briefless",
             "author vocabulary alone -- the line says the form, the laws it judges and "
             "their plate, the catalog defines the format: no hardcoded order rides the block")
    else:
        failures.append(f"  ✗ prove block                 {prove_block.command!r} {prove_block.output!r}")

    uncovered = c().submit("[]")
    if (uncovered.position == 1 and uncovered.command == "INFER"
            and "names no law of production" in uncovered.deviation):
        held("a proof names the codes at risk",
             "an empty array proves nothing -- it REPAIRS the whole document")
    else:
        failures.append(f"  ✗ proof coverage              {uncovered.position} {uncovered.deviation!r}")

    drift = "tone drifted"
    c().submit("")                        # the reopened INFER, said again in chat
    prove_failed = c().submit(_said("Z1", drift, "fail"))
    if (prove_failed.position == 1 and "your own proof failed" in prove_failed.deviation
            and drift in prove_failed.deviation and "REPAIR 2" in render(prove_failed)):
        held("a fail verdict reopens the document",
             "REPAIR from instruction 1 -- the failing objects travel in the DEVIATION")
    else:
        failures.append(f"  ✗ proof fail                  {prove_failed.position} {prove_failed.deviation!r}")

    c().submit("")
    prove_passed = c().submit(_said("Z1", "plain words", "ok"))
    if over(prove_passed):
        held("an ok proof lets the run out", "the checkpoint opens, the document completes")
    else:
        failures.append(f"  ✗ proof pass                  {prove_passed and prove_passed.command!r}")
    c().forget()

    # --- n/a, and a verdict outside the three words --------------------------------------------
    c().start(chat_doc)
    c().submit("")
    prove_na = c().submit(_said("Z1", "no naming in this production", "n/a"))
    if over(prove_na):
        held("n/a passes and repairs nothing", "a law without bearing is said, not dressed "
             "as ok -- ok stays reserved for the verified")
    else:
        failures.append(f"  ✗ proof n/a                   {prove_na and prove_na.command!r}")
    c().forget()
    c().start(chat_doc)
    c().submit("")
    prove_odd = c().submit(_said("Z1", "x", "maybe"))
    if prove_odd.deviation and "`ok`, `fail` or `n/a`" in prove_odd.deviation:
        held("a stranger verdict deviates", "the enumeration says its three words")
    else:
        failures.append(f"  ✗ proof verdict enum          {prove_odd.deviation!r}")
    c().forget()

    # --- a named fix buys the in-place repair --------------------------------------------------
    reword = "reword plainly"
    c().start(chat_doc)
    c().submit("")
    fixed = c().submit(_said("Z1", drift, "fail", fix=reword))
    mini = c().submit(_said("Z1", "rewritten, greps clean", "ok"))
    if ("IN PLACE" in (fixed.deviation or "") and fixed.position == 2
            and reword in fixed.deviation and over(mini)):
        held("a named fix repairs in place", "the document stands, the failed code alone "
             "re-proves, the mini-proof lets the run out")
    else:
        failures.append(f"  ✗ fix in place                {fixed.deviation!r} {mini and mini.command!r}")
    c().forget()
    c().start(chat_doc)
    c().submit("")
    c().submit(_said("Z1", "off", "fail", fix="say it straight"))
    wrong_mini = c().submit(_said("Z9", "x", "ok"))
    relapse = c().submit(_said("Z1", "still off", "fail"))
    if ("covers exactly" in (wrong_mini.deviation or "") and wrong_mini.position == 2
            and "failed AGAIN" in (relapse.deviation or "") and relapse.position == 1):
        held("the mini-proof is exact and a relapse replays", "wrong coverage bounces to the "
             "codes, a second fail closes the cheap branch -- the document reopens")
    else:
        failures.append(f"  ✗ mini exactness/relapse      {wrong_mini.deviation!r} {relapse.deviation!r}")
    c().forget()

    # --- the pipeline crosses the checkpoint ---------------------------------------------------
    env.write("SHIPIT.md", SHIPIT)
    pipe_opening = c().start(env.write("PIPER.md", PIPER))
    c().submit('{"ok": 1}')
    pipe_done = c().submit(_said("Q1", "json.loads passes", "ok"))
    _, pipe_stack, _, _, _, _, _ = persistence.restore(persistence.slot_of(env.made, "t"), revive)
    shipped = pipe_stack.frames[0].procedure.instructions[-1]
    if " -   (" in pipe_opening.next_call and over(pipe_done) and shipped.done:
        held("the pipeline mode captures and flows",
             "consumption computes THROUGH the checkpoint -- stdin in, the production crosses the pop")
    else:
        failures.append(f"  ✗ prove pipeline              {pipe_opening.next_call!r} {shipped.done!r}")
    c().forget()

    # --- a REPAIR reopens the whole document, the reading stays served -------------------------
    c().start(env.write("REDO.md", REDO))
    c().submit('["prover"]')
    missed_pick = c().submit("nobody")
    refed = c().submit('["prover"]')
    if ("not in OPTIONS" in missed_pick.deviation
            and "READ.md" not in [n for n, _ in refed.payloads]
            and str(refed.instruction) == "PICK member"
            and over(c().submit("prover"))):
        held("a REPAIR reopens the whole document, re-serving nothing",
             "chained steps replay, the reading stays proven -- no second copy of what the "
             "agent already holds")
    else:
        failures.append(f"  ✗ document-scoped repair      {[n for n, _ in refed.payloads]} "
                        f"{missed_pick.deviation!r}")
    c().forget()

    # --- the bound holds across the reopenings: a reset count would hide the second fail -----
    env.write("SETTINGS.md", BOUND.format(allowed=1))
    c().start(chat_doc)
    c().submit("")
    c().submit(_said("Z1", "off", "fail"))                  # repair 1
    c().submit("")                                          # the reopened INFER
    expect("repair-exhausted", lambda: c().submit(_said("Z1", "still off", "fail")))
    c().forget()

    # --- the wired TURN: a law of production in force arms its checkpoint ----------------------
    wired = bench.env("wired")
    wired.write("procs/TURN.md", WIRED)

    def w():
        return run.conductor_of(wired, None)

    wired_work = w().resume(w().boot("BOOT.md"))            # -> TURN's own WORK
    wired_prove = w().submit("")                            # work said -> the checkpoint gates
    wired_proof = json.dumps([{"code": one.code, "evidence": "held", "verdict": "ok"}
                              for one in wired_prove.constraints])
    wired_wait = w().submit(wired_proof)                    # proof ok -> FINAL rides
    if (wired_work.document == "TURN" and not wired_work.wait
            and str(wired_work.command).startswith("WORK")
            and wired_prove.output == "proof"
            and wired_wait is not None and wired_wait.wait and not wired_wait.command
            and "▶ FINAL" in render(wired_wait) and wired_wait.document == "TURN"):
        held("the wired TURN closes on FINAL",
             "the checkpoint gates the frontier, proof ok => FINAL rides its answer")
    else:
        failures.append(f"  ✗ wired closing               {wired_wait and wired_wait.command!r} "
                        f"wait={wired_wait and wired_wait.wait}")

    wired_next = w().resume(w().boot("BOOT.md"))
    if (wired_next is not None and wired_next.document == "TURN"
            and not wired_next.wait and wired_next.instruction.repairs == 0):
        held("the next message reopens the cycle",
             "resume rewinds THEN re-cedes: the guard, the fresh INFER -- the operator's trace")
    else:
        failures.append(f"  ✗ wired next exchange         {wired_next and wired_next.document!r}")

    # --- a linear FINAL is a pause -------------------------------------------------------------
    pause_doc = env.write("PAUSED.md", PAUSED)
    paused = c().start(pause_doc)
    resumed_past = c().resume(pause_doc)
    ended = c().submit("")
    if (paused is not None and paused.wait and not paused.command
            and resumed_past.instruction.keyword == "INFER"
            and over(ended) and "▌ END" in render(ended)
            and "▶" not in render(ended)
            and "do not call the tool again" in ended.end):
        held("a pause is not a loop", "a linear FINAL closes ONE exchange; resumed, the proc goes on -- "
             "and finished is finished: END, unflagged (no call owed)")
    else:
        failures.append(f"  ✗ linear pause                {paused and paused.wait} / "
                        f"{resumed_past and str(resumed_past.instruction)!r} / "
                        f"{ended and ended.end!r}")
    c().forget()


def _covered_doc(codes: list[str]) -> str:
    """-> a cycled exchange under one law of production per code, and one behavior law B9."""
    laws = "".join(f"  {code}  the law {code} holds\n" for code in codes)
    return ("---\nname: COVERED\nkind: proc\ndescription: a proven exchange\ncycle: true\n"
            f"constraints.production: |\n{laws}constraints.behavior: |\n  B9  speak plainly\n"
            "proc: |\n  INFER\n  FINAL\n---\nanswer the ask\n")


def _covering(codes: list[str], verdict: str = "n/a") -> str:
    """-> a proof of one object per code, all of one verdict."""
    return json.dumps([{"code": code, "evidence": NO_BEARING, "verdict": verdict} for code in codes])


def coverage(bench) -> None:
    """Every code the proof line asks has an object in the proof; one left unnamed deviates, named."""
    held, failures = bench.held, bench.failures
    env = bench.env("coverer", bare=True)

    def c():
        return run.conductor_of(env, "t")

    three = ["Z1", "Z2", "Z3"]
    doc = env.write("COVERED.md", _covered_doc(three))

    c().start(doc)
    asked = c().submit("")
    holed = c().submit(_covering(["Z1", "Z2"]))
    if (asked is not None and list(asked.judged) == three and holed is not None and holed.repair == 1
            and "Z3" in (holed.deviation or "") and "unnamed" in (holed.deviation or "")):
        held("(a) a code left unnamed deviates", f"the line asks {list(asked.judged)}, the proof names two: "
             f"REPAIR 1, the DEVIATION says `{holed.deviation}`")
    else:
        failures.append(f"  ✗ (a) the unnamed code        judged={asked and list(asked.judged)} "
                        f"repair={holed and holed.repair} {(holed.deviation if holed else '')!r}")
    c().forget()

    c().start(doc)
    c().submit("")
    whole = c().submit(_covering(three))
    if whole is not None and whole.wait and not whole.repair and not whole.deviation:
        held("(b) the complete proof passes", "three objects for three codes asked: the FINAL renders")
    else:
        failures.append(f"  ✗ (b) the complete proof      wait={whole and whole.wait} "
                        f"{(whole.deviation if whole else '')!r}")
    c().forget()

    c().start(doc)
    c().submit("")
    extra = c().submit(_covering(three + ["B9"]))
    if extra is not None and extra.wait and not extra.deviation:
        held("(c) a behavior code in addition passes", "B9 named beside Z1-Z3: no deviation, the FINAL renders")
    else:
        failures.append(f"  ✗ (c) the behavior code       wait={extra and extra.wait} "
                        f"{(extra.deviation if extra else '')!r}")
    c().forget()

    c().start(doc)
    c().submit("")
    fixing = json.dumps([{"code": "Z1", "evidence": "a claim unrendered", "verdict": "fail", "fix": "render it"},
                         {"code": "Z2", "evidence": "held", "verdict": "ok"},
                         {"code": "Z3", "evidence": "no bearing", "verdict": "n/a"}])
    placed = c().submit(fixing)
    mini = c().submit(_said("Z1", "rendered: grep -c 1", "ok"))
    if (placed is not None and "IN PLACE" in (placed.deviation or "") and mini is not None and mini.wait
            and not mini.deviation):
        held("(d) the mini-proof covers the repaired code alone", "Z1 fixed in place, its mini-proof names Z1 "
             "alone: the FINAL renders")
    else:
        failures.append(f"  ✗ (d) the mini-proof          {(placed.deviation if placed else '')!r} "
                        f"wait={mini and mini.wait} {(mini.deviation if mini else '')!r}")
    c().forget()

    many = [f"Y{n}" for n in range(1, 20)]
    c().start(env.write("MANY.md", _covered_doc(many)))
    c().submit("")
    full_proof, short_proof = _covering(many), _covering(many[:16])
    passed = c().submit(full_proof)
    added = len(full_proof) - len(short_proof)
    if passed is not None and passed.wait and not passed.deviation:
        held("(e) nineteen codes, the complete proof passes", f"19 objects, {len(full_proof)} c; a proof leaving "
             f"three unnamed would be {len(short_proof)} c: the three explicit n/a cost {added} c "
             f"({added // 3} c an object)")
    else:
        failures.append(f"  ✗ (e) nineteen codes          wait={passed and passed.wait} "
                        f"{(passed.deviation if passed else '')!r}")
    c().forget()


def fail_exit(bench) -> None:
    """An honest `fail` has a way out, and a fix that holds does not wear the repair bound."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("gapper", bare=True)

    def c():
        return run.conductor_of(env, "t")

    def bound(allowed: int) -> None:
        env.write("SETTINGS.md", BOUND.format(allowed=allowed))

    doc = env.write("GAPPED.md", GAPPED)

    # --- a declared gap closes the checkpoint --------------------------------------------------
    bound(3)
    c().start(doc)
    asked = c().submit("")
    closed = c().submit(_said("Z1", "the claims stand unrendered", "fail", blocked=GAP))
    gaps = [one for one in run.trace(env, "t") if one.get("kind") == "blocked"]
    counted_gaps = sum(one.blocked for one in traces.exchanges(run.trace(env, "t")))
    if (asked is not None and asked.output == "proof" and closed is not None and closed.wait
            and not closed.repair and tuple(map(tuple, closed.gaps)) == (("Z1", GAP),)
            and GAP in render(closed)
            and gaps and gaps[-1].get("gaps") == [{"code": "Z1", "text": GAP}]
            and counted_gaps == 1):
        held("(a) a declared gap closes the checkpoint", "fail + blocked: the FINAL renders, REPAIR none, "
             "the trace says `blocked` Z1 with its text (-stats counts 1 gap), the closing says the gap")
    else:
        failures.append(f"  ✗ (a) the declared gap        wait={closed and closed.wait} repair={closed and closed.repair} "
                        f"{(closed.deviation if closed else '')!r} gaps={gaps[-1:]} counted={counted_gaps}")
    c().forget()

    # --- an empty blocked is a bare fail -------------------------------------------------------
    c().start(doc)
    c().submit("")
    empty = c().submit(_said("Z1", "off", "fail", blocked="  "))
    if empty is not None and empty.repair == 1 and "your own proof failed" in (empty.deviation or ""):
        held("(b) an empty blocked is a bare fail", "REPAIR 1, the document replays")
    else:
        failures.append(f"  ✗ (b) the empty blocked       repair={empty and empty.repair} "
                        f"{(empty.deviation if empty else '')!r}")
    c().forget()

    # --- three fixes that hold never wear the bound --------------------------------------------
    bound(1)
    c().start(doc)
    counted, outcome = [], ""
    try:
        for turn in range(3):
            c().submit("" if turn == 0 else f"message {turn + 1}")
            if turn:
                c().submit("")
            c().submit(_said("Z1", "a claim unrendered", "fail", fix="render the claim"))
            last = c().submit(_said("Z1", "rendered: grep -c 1", "ok"))
            counted.append(_repairs(env))
            outcome = "final" if last is not None and last.wait else "other"
    except Refusal as refused:
        outcome = refused.code
    if counted == [0, 0, 0] and outcome == "final":
        held("(c) three fixes that hold never wear the bound", "work_repairs_allowed 1, three exchanges "
             "each fail + fix then a mini-proof ok: repairs 0, 0, 0, the FINAL each time")
    else:
        failures.append(f"  ✗ (c) the fixes and the bound  counted={counted} outcome={outcome!r}")
    c().forget()

    # --- a relapse counts one ------------------------------------------------------------------
    bound(3)
    c().start(doc)
    c().submit("")
    c().submit(_said("Z1", "off", "fail", fix="say it"))
    relapse = c().submit(_said("Z1", "still off", "fail"))
    if relapse is not None and "failed AGAIN" in (relapse.deviation or "") and _repairs(env) == 1:
        held("(d) a relapse counts one", "the cheap branch closes, the document replays, one repair counted")
    else:
        failures.append(f"  ✗ (d) the relapse             {(relapse.deviation if relapse else '')!r} "
                        f"repairs={_repairs(env)}")
    c().forget()

    # --- bare fails hand back at the bound -----------------------------------------------------
    bound(2)
    c().start(doc)
    bare = _said("Z1", "the bench is out of reach", "fail")
    c().submit("")
    c().submit(bare)                      # repair 1
    c().submit("")
    c().submit(bare)                      # repair 2
    c().submit("")
    expect("repair-exhausted", lambda: c().submit(bare))
    c().forget()

    # --- fix and blocked together: in place, then the gap closes it ----------------------------
    bound(3)
    c().start(doc)
    c().submit("")
    placed = c().submit(_said("Z1", "two claims unrendered", "fail",
                              fix="render what can be", blocked=SECOND_GAP))
    mixed = c().submit(_said("Z1", "one claim rendered, one not", "fail", blocked=SECOND_GAP))
    if (placed is not None and "IN PLACE" in (placed.deviation or "") and mixed is not None and mixed.wait
            and tuple(map(tuple, mixed.gaps)) == (("Z1", SECOND_GAP),)
            and SECOND_GAP in render(mixed) and _repairs(env) == 0):
        held("(f) fix and blocked: in place, then the gap closes it", "the repair plays in place, the "
             "mini-proof declares the gap, the FINAL says it; no repair counted")
    else:
        failures.append(f"  ✗ (f) fix and blocked         {(placed.deviation if placed else '')!r} "
                        f"wait={mixed and mixed.wait} {(mixed.deviation if mixed else '')!r} repairs={_repairs(env)}")
    c().forget()


def exit_checkpoint(bench) -> None:
    """A frame proves on its way out; the proof gates every frontier it precedes."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("xitw")
    env.write("SETTINGS.md", FUSION.format(fusion="max"))
    for name, text in EXITS.items():
        env.write(f"procs/{name}.md", text)

    def c():
        return run.conductor_of(env, "t")

    def opened(name: str):
        """-> the first block of a fresh run of `name`."""
        one = c()
        one.forget()
        return one.start(one.boot(f"{name}.md"))

    # --- the checkpoint rises at the exit ------------------------------------------------------
    xit_opened = c().start(c().boot("CALLER.md"))
    xit_text = render(xit_opened) if xit_opened is not None else ""
    xit_armed = (_keyword(xit_opened) == "PROVE" and "X1" in xit_text and "Y1" in xit_text
                 and "(your proof on stdin -- heredoc)" in xit_text)
    xit_foreign = c().submit(_said("Q9", "no such law", "ok"))
    xit_repaired = (xit_foreign is not None and "REPAIR" in render(xit_foreign)
                    and "not in force" in (xit_foreign.deviation or "")
                    and _keyword(xit_foreign) == "PROVE")
    xit_risk = json.dumps([{"code": "X1", "evidence": "no bearing on the line", "verdict": "n/a"},
                           {"code": "Y1", "evidence": "short indeed", "verdict": "ok"}])
    xit_closed = c().submit(xit_risk)          # every code the line asks, X1 written n/a
    if xit_armed and xit_repaired and _keyword(xit_closed) != "PROVE":
        held("the exit checkpoint rises, no switch", "a frame with a law of production "
             "proves on its way out, inherited law on screen, no skip offered; a proof "
             "naming a law not in force REPAIRS; every code the line asks named lets it leave")
    else:
        failures.append(f"  ✗ exit checkpoint             {xit_armed}/{xit_repaired}/"
                        f"{_keyword(xit_closed)} {xit_text[-200:]!r}")

    empty_block = opened("CRAFT")
    empty_answer = c().submit("")              # an empty answer is NO proof: it repairs
    if (_keyword(empty_block) == "PROVE"
            and empty_answer is not None and "REPAIR" in render(empty_answer)):
        held("an empty answer repairs", "the checkpoint knows no skip: nothing piped, "
             "the document replays")
    else:
        failures.append(f"  ✗ exit empty                  "
                        f"{empty_answer and render(empty_answer)[-150:]!r}")
    c().submit(_said("Y1", "held", "ok"))

    # --- the bound hands back: the purged checkpoint cannot zero its own count -----------------
    opened("CALLER")
    lame = _said("Q9", "no such law", "ok")
    for _ in range(3):                         # work_repairs_allowed: the instance default 3
        c().submit(lame)
    expect("repair-exhausted", lambda: c().submit(lame))
    held("the exit bound still hands back", "the purged checkpoint cannot zero "
         "its own count -- a stable instruction carries it to the operator")

    # --- the silences: no law, and a frame that produced nothing -------------------------------
    quiet_runs = []
    for name in ("PLAIN", "HOLLOW"):
        quiet_runs.append(_keyword(opened(name)) != "PROVE")
        expect("run-complete", lambda: c().submit("x"))
    if all(quiet_runs):
        held("the exit knows its silences", "no law of production, and a frame that "
             "produced nothing -- two exits closing their run without one proof block")
    else:
        failures.append(f"  ✗ exit silences               {quiet_runs}")
    expect("prove-gone", lambda: opened("ARMED"))
    held("a relic prove: refuses", "the switch is gone -- a document still carrying it "
         "refuses by name at its opening")

    # --- a cycle proves every productive lap ---------------------------------------------------
    first_is = _keyword(opened("LOOP")) == "PROVE"
    second_is = _keyword(c().submit(_said("L1", "landed", "ok"))) == "PROVE"   # rewind -> lap 2
    if first_is and second_is:
        held("a cycle proves every productive lap", "the rewind purges the played "
             "checkpoint and the next lap earns its own")
    else:
        failures.append(f"  ✗ exit cycle                  {first_is}/{second_is}")
    c().forget()

    # --- the proof gates the frontier, step by step --------------------------------------------
    env.write("SETTINGS.md", FUSION.format(fusion="none"))
    opened("TFIN")
    fin_proof = c().submit("")                 # the WORK closes; the proof gates
    fin_front = c().submit(_said("G1", "landed", "ok"))     # proven -> the frontier delivers
    fin_ftext = render(fin_front) if fin_front is not None else ""
    fin_lap2 = c().submit("")                  # the resume opens on lap 2, not a proof
    if (_keyword(fin_proof) == "PROVE" and "proof given" in fin_ftext
            and _keyword(fin_lap2) != "PROVE"):
        held("the proof gates the frontier", "the adjacency breaks, the checkpoint "
             "lands BEFORE the delivery -- same turn; the promise is literal and "
             "the resume opens on fresh work")
    else:
        failures.append(f"  ✗ frontier gate               {_keyword(fin_proof)}/"
                        f"{'proof given' in fin_ftext}/{_keyword(fin_lap2)} {fin_ftext[-120:]!r}")

    opened("MFIN")
    proven = _said("F1", "landed", "ok")
    mf_p1 = c().submit("")                     # segment 1 closes -> its proof
    mf_f1 = c().submit(proven)                 # proven -> frontier 1
    c().submit("")                             # resume -> segment 2's INFER
    mf_p2 = c().submit("")                     # segment 2 closes -> its proof
    mf_f2 = c().submit(proven)                 # proven -> frontier 2
    mf_end = c().submit("")                    # exhausted, nothing unproven -> END
    mf_proofs = _keyword(mf_p1) == "PROVE" and _keyword(mf_p2) == "PROVE"
    mf_silent = not (_keyword(mf_end) == "PROVE" and not mf_end.instruction.done)
    if mf_proofs and mf_f1 is not None and mf_f2 is not None and mf_silent:
        held("each segment proves before ITS delivery", "two frontiers, two "
             "checkpoints, each ahead of its FINAL; the exhaustion owes nothing")
    else:
        failures.append(f"  ✗ multi-frontier              {mf_proofs} {_keyword(mf_end)}")

    opened("PLAIN")
    plain_trace = run.trace(env, "t")
    if plain_trace and "PROVE" not in json.dumps(plain_trace):
        held("no law, no checkpoint", "a frame without a law of production leaves "
             "without one proof kind in its trace -- nothing to prove, nothing to say")
    else:
        failures.append(f"  ✗ plain traced                {len(plain_trace)} event(s), a proof kind leaked")
    c().forget()


def sections(bench) -> None:
    """The two sections of the laws: how they render, what the judge asks, where an overlay adds."""
    held, over, failures = bench.held, bench.over, bench.failures
    env = bench.env("sect", bare=True)

    def c():
        return run.conductor_of(env, "t")

    # --- one title, two groups, the codes on the instruction line ------------------------------
    shown = render(c().start(env.write("TWO.md", TWO)))
    proof_block = c().submit("")               # the chat-bound INFER: said there, the key alone
    if (shown.count("▌ CONSTRAINTS") == 1
            and f"production:\n{P1}\nbehavior:\n{H1}" in shown
            and "INFER proof [P1] on all produced areas" in render(proof_block)
            and "law(s) owed" not in proof_block.next_call
            and proof_block.command == "INFER" and proof_block.output == "proof"):
        held("one title, production first, the codes on the line",
             "P1 under `production:`, H1 under `behavior:`; the checkpoint NAMES P1 and "
             "its plate, and the hint keeps the way back alone")
    else:
        failures.append(f"  ✗ sections rendered          {shown!r} {proof_block.next_call!r}")

    # --- the judge asks the production laws alone ----------------------------------------------
    behavior_only = c().submit(_said("H1", "said first", "ok"))
    c().submit("")                             # the reopened INFER, said in chat again
    production_only = c().submit(_said("P1", "wc -w -> 4", "ok"))
    if (behavior_only.deviation and "names no law of production" in behavior_only.deviation
            and over(production_only)):
        held("the proof asks the production laws alone",
             "H1 alone names no law of production; P1 alone lets the run out -- a behavior "
             "law is never owed")
    else:
        failures.append(f"  ✗ proof filter               {behavior_only.deviation!r} "
                        f"{production_only and production_only.command!r}")
    c().forget()

    # --- an overlay adds in the section of its key ---------------------------------------------
    overlay = env.write("procs/TURN.md", OVERLAY)
    laws, _ = compiling.effective(env.made, reading.read(instance.resolve(env.made, "TURN.md")))
    by_code = {one.code: one.section for one in laws}
    if by_code == {"TB9": "behavior", "TP9": "production"}:
        held("an overlay adds in the section of its key",
             "TB9 behavior, TP9 production -- the two laws in force on a TURN that "
             "carried none")
    else:
        failures.append(f"  ✗ overlay sections           {by_code}")
    overlay.unlink()

    # --- no law of production in force: no checkpoint ------------------------------------------
    first = c().start(env.write("QUIET.md", QUIET))
    closing = first if first.wait else c().submit("")   # fused, or one step later
    if (first.command == "INFER"
            and closing is not None and closing.wait and closing.output != "proof"
            and "no law of production in force" in render(closing)):
        held("no production law, no checkpoint", "an armed document with behavior laws alone "
             "reaches its FINAL without a proof block; the closing says why")
    else:
        failures.append(f"  ✗ quiet checkpoint           {first.next_call!r} "
                        f"{closing and (closing.output, closing.wait, render(closing)[-160:])!r}")
    c().forget()


def scenario(bench) -> int:
    convergence(bench)
    coverage(bench)
    fail_exit(bench)
    exit_checkpoint(bench)
    sections(bench)
    return 0
