"""Scenario `proof` -- 4 case(s), in the monolith's order:
- PROVE: the convergence loop closes -- author keyword, agent-side INFER
- la-preuve-honnete: n/a is the honest word for a law without bearing
- le-fail-repare-en-place: a named fix buys the in-place repair
- le-wait-s-ecrit: the frontier is DECLARED -- FINAL keyword, ternary closing
"""
from __future__ import annotations

import json
from pathlib import Path
from conductor import Conductor, render, revive, discovery, persistence
from tests.harness import document, session_of
from tests.harness import quiet_improve as _quiet_improve


def scenario(bench) -> int:
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    # --- the first environment: three instances side by side, `core` the home
    town = bench.town(["core", "perso", "sw7-hub"])
    siblings = town.siblings
    home = town["core"].member
    script = town["core"].engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")


    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, siblings, script, "t")


    # --- PROVE: the convergence loop closes -- author keyword, agent-side INFER --------
    prove_siblings = bench.town(["prover"]).siblings
    prove_home = discovery.member(prove_siblings, "prover")

    def prove_c() -> Conductor:
        return Conductor(prove_home, prove_siblings, script, "t")

    expect("prove-retired", lambda: prove_c().start(document(
        "---\nname: X\nproc: |\n  PROVE\n---\nx\n", at=prove_home.meta)))
    (prove_home.meta / "READ.md").write_text("some reading\n", encoding="utf-8")
    (prove_home.meta / "PFORMS.md").write_text(
        "---\nname: PFORMS\ndescription: local formats\nformats: |\n"
        "  json  stdin  one valid JSON value\n---\n", encoding="utf-8")
    expect("prove-retired", lambda: prove_c().start(document(
        "---\nname: X\nproc: |\n  SERVE READ.md\n  PROVE\n---\nx\n", at=prove_home.meta)))

    chat_text = ("---\nname: CHATTY\nkind: proc\ndescription: proven, chat-bound\n"
                 "constraints.production: |\n  Z1  say it plainly\nproc: |\n  INFER\n---\n"
                 "write the thing\n")
    chat_doc = document(chat_text, at=prove_home.meta)
    chat_opening = prove_c().start(chat_doc)
    if ("-sp" not in chat_opening.next_call and "stdin" not in chat_opening.next_call
            and chat_opening.command == "INFER"):
        held("an unconsumed proven INFER speaks in chat",
             "the closing is the keyed call -- no switch announced: the checkpoint comes")
    else:
        failures.append(f"  ✗ prove chat closing          {chat_opening.next_call!r}")

    prove_block = prove_c().submit("")
    prove_rendered = render(prove_block)
    if (prove_block.command == "INFER" and prove_block.output == "proof"
            and " -\n   (" in prove_block.next_call
            and "Prove the RESULT" not in prove_rendered
            and "proving" not in prove_rendered
            and "INFER proof [" in prove_rendered
            and "on all produced areas => tool (heredoc)" in prove_rendered):
        held("PROVE presents as INFER, briefless",
             "author vocabulary alone -- the line says the form, the laws it judges and "
             "their plate, the catalog defines the format: no hardcoded order rides the block")
    else:
        failures.append(f"  ✗ prove block                 {prove_block.command!r} {prove_block.output!r}")

    uncovered = prove_c().submit("[]")
    if (uncovered.position == 1 and uncovered.command == "INFER"
            and "names no law of production" in uncovered.deviation):
        held("a proof names the codes at risk",
             "an empty array proves nothing -- it REPAIRS the whole document")
    else:
        failures.append(f"  ✗ proof coverage              {uncovered.position} {uncovered.deviation!r}")

    prove_c().submit("")                        # the reopened INFER, said again in chat
    prove_failed = prove_c().submit('[{"code": "Z1", "evidence": "tone drifted", "verdict": "fail"}]')
    if (prove_failed.position == 1 and "your own proof failed" in prove_failed.deviation
            and "tone drifted" in prove_failed.deviation and "REPAIR 2" in render(prove_failed)):
        held("a fail verdict reopens the document",
             "REPAIR from instruction 1 -- the failing objects travel in the DEVIATION")
    else:
        failures.append(f"  ✗ proof fail                  {prove_failed.position} {prove_failed.deviation!r}")

    prove_c().submit("")
    prove_passed = prove_c().submit('[{"code": "Z1", "evidence": "plain words", "verdict": "ok"}]')
    if over(prove_passed):
        held("an ok proof lets the run out", "the checkpoint opens, the document completes")
    else:
        failures.append(f"  ✗ proof pass                  {prove_passed and prove_passed.command!r}")
    prove_c().forget()

    # --- la-preuve-honnete: n/a is the honest word for a law without bearing ----------
    prove_c().start(chat_doc)
    prove_c().submit("")
    prove_na = prove_c().submit('[{"code": "Z1", "evidence": "no naming in this production", "verdict": "n/a"}]')
    if over(prove_na):
        held("n/a passes and repairs nothing", "a law without bearing is said, not dressed "
             "as ok -- ok stays reserved for the verified")
    else:
        failures.append(f"  ✗ proof n/a                   {prove_na and prove_na.command!r}")
    prove_c().forget()
    prove_c().start(chat_doc)
    prove_c().submit("")
    prove_odd = prove_c().submit('[{"code": "Z1", "evidence": "x", "verdict": "maybe"}]')
    if prove_odd.deviation and "`ok`, `fail` or `n/a`" in prove_odd.deviation:
        held("a stranger verdict deviates", "the enumeration says its three words")
    else:
        failures.append(f"  ✗ proof verdict enum          {prove_odd.deviation!r}")
    prove_c().forget()

    # --- le-fail-repare-en-place: a named fix buys the in-place repair ----------------
    prove_c().start(chat_doc)
    prove_c().submit("")
    fixed = prove_c().submit(
        '[{"code": "Z1", "evidence": "tone drifted", "verdict": "fail", "fix": "reword plainly"}]')
    mini = prove_c().submit('[{"code": "Z1", "evidence": "rewritten, greps clean", "verdict": "ok"}]')
    if ("IN PLACE" in (fixed.deviation or "") and fixed.position == 2
            and "reword plainly" in fixed.deviation and over(mini)):
        held("a named fix repairs in place", "the document stands, the failed code alone "
             "re-proves, the mini-proof lets the run out")
    else:
        failures.append(f"  ✗ fix in place                {fixed.deviation!r} {mini and mini.command!r}")
    prove_c().forget()
    prove_c().start(chat_doc)
    prove_c().submit("")
    prove_c().submit(
        '[{"code": "Z1", "evidence": "off", "verdict": "fail", "fix": "say it straight"}]')
    wrong_mini = prove_c().submit('[{"code": "Z9", "evidence": "x", "verdict": "ok"}]')
    relapse = prove_c().submit('[{"code": "Z1", "evidence": "still off", "verdict": "fail"}]')
    if ("covers exactly" in (wrong_mini.deviation or "") and wrong_mini.position == 2
            and "failed AGAIN" in (relapse.deviation or "") and relapse.position == 1):
        held("the mini-proof is exact and a relapse replays", "wrong coverage bounces to the "
             "codes, a second fail closes the cheap branch -- the document reopens")
    else:
        failures.append(f"  ✗ mini exactness/relapse      {wrong_mini.deviation!r} {relapse.deviation!r}")
    prove_c().forget()

    (prove_home.meta / "SHIPIT.md").write_text(
        "---\nname: SHIPIT\ndescription: consumes the payload\ninput: json\nproc: |\n"
        "  HOOK shipped\n---\nship it\n", encoding="utf-8")
    pipe_doc = document(
        "---\nname: PIPER\nkind: proc\ndescription: proven, pipeline-bound\noutput: json\n"
        "constraints.production: |\n  Q1  the payload is one json value\n"
        "proc: |\n  INFER\n  CALL SHIPIT.md\n---\nmake the payload\n",
        at=prove_home.meta)
    pipe_opening = prove_c().start(pipe_doc)
    prove_c().submit('{"ok": 1}')
    pipe_done = prove_c().submit('[{"code": "Q1", "evidence": "json.loads passes", "verdict": "ok"}]')
    _, pipe_stack, _, _, _, _, _, _ = persistence.restore(session_of(prove_home.meta), revive)
    shipped = pipe_stack.frames[0].procedure.instructions[-1]
    if (" -   (" in pipe_opening.next_call and over(pipe_done) and shipped.done):
        held("the pipeline mode captures and flows",
             "consumption computes THROUGH the checkpoint -- stdin in, the production crosses the pop")
    else:
        failures.append(f"  ✗ prove pipeline              {pipe_opening.next_call!r} {shipped.done!r}")
    prove_c().forget()

    replay_doc = document(
        "---\nname: REDO\noutput: json\nproc: |\n  INFER\n  SERVE READ.md\n  PICK member\n---\n",
        at=prove_home.meta)
    prove_c().start(replay_doc)
    prove_c().submit('["prover"]')
    missed_pick = prove_c().submit("nobody")
    refed = prove_c().submit('["prover"]')
    if ("not in OPTIONS" in missed_pick.deviation
            and "READ.md" not in [n for n, _ in refed.payloads]
            and str(refed.instruction) == "PICK member"
            and over(prove_c().submit("prover"))):
        held("a REPAIR reopens the whole document, re-serving nothing",
             "chained steps replay, the reading stays proven -- no second copy of what the "
             "agent already holds (les-cles-mortes, 2026-09-05)")
    else:
        failures.append(f"  ✗ document-scoped repair      {[n for n, _ in refed.payloads]} "
                        f"{missed_pick.deviation!r}")
    prove_c().forget()

    (prove_home.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nwork_repairs_allowed: 1\n---\n", encoding="utf-8")
    bound_doc = document(chat_text, at=prove_home.meta)
    prove_c().start(bound_doc)
    prove_c().submit("")
    prove_c().submit('[{"code": "Z1", "evidence": "off", "verdict": "fail"}]')     # repair 1
    prove_c().submit("")                                                            # reopened INFER
    expect("repair-exhausted", lambda: prove_c().submit(
        '[{"code": "Z1", "evidence": "still off", "verdict": "fail"}]'))
    # the bound held ACROSS the reopening: had `reopen` reset the counts, the second
    # fail would have registered as the first, and the operator never got the hand

    prove_c().forget()
    (prove_home.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nwork_repairs_allowed: 1\n---\n", encoding="utf-8")

    # --- le-wait-s-ecrit: the frontier is DECLARED -- FINAL keyword, ternary closing ----
    wired_made = bench.env("wired").made
    _quiet_improve(wired_made)   # the closing fixtures here are not about the reflex
    (wired_made / "MEMBER.md").write_text(   # a vanilla member carries no production law
        (wired_made / "MEMBER.md").read_text(encoding="utf-8")   # (identity is behavior):
        .replace("constraints.behavior: |", "constraints.production: |\n  Z2  the turn's work is proven.\n"
                 "constraints.behavior: |", 1), encoding="utf-8")   # the checkpoint needs one

    wired_member = discovery.instance_member(wired_made / ".sys" / "engine" / "pp.py")
    # the kit TURN ships WIRED (`HOOK / WORK / ... / FINAL`, the checkpoint engine-armed)
    # -- no bundle edit: the `prove` setting rules, a `sync` never un-wires an instance

    def wired_c() -> Conductor:
        return Conductor(wired_member, discovery.siblings_around(wired_member),
                         wired_made / ".sys" / "engine" / "pp.py")

    wired_c().resume(wired_c().boot("BOOT.md"))          # -> CAPABILITIES
    wired_infer = wired_c().submit("")
    wired_prove = wired_c().submit("")                   # work said -> the checkpoint GATES
    wired_proof = json.dumps([{"code": one.code, "evidence": "held", "verdict": "ok"}
                              for one in wired_prove.constraints])
    wired_wait = wired_c().submit(wired_proof)           # proof ok -> FINAL rides
    if (wired_infer.document == "TURN" and not wired_infer.wait
            and wired_prove.output == "proof"
            and wired_wait is not None and wired_wait.wait and not wired_wait.command
            and "▶ FINAL" in render(wired_wait) and wired_wait.document == "TURN"):
        held("the wired TURN closes on FINAL",
             "the checkpoint gates the frontier, proof ok => FINAL rides its answer")
    else:
        failures.append(f"  ✗ wired closing               {wired_wait and wired_wait.command!r} "
                        f"wait={wired_wait and wired_wait.wait}")

    wired_next = wired_c().resume(wired_c().boot("BOOT.md"))
    if (wired_next is not None and wired_next.document == "TURN"
            and not wired_next.wait and wired_next.instruction.repairs == 0):
        held("the next message reopens the cycle",
             "resume rewinds THEN re-cedes: the guard, the fresh INFER -- the operator's trace")
    else:
        failures.append(f"  ✗ wired next exchange         {wired_next and wired_next.document!r}")

    pause_doc = document(
        "---\nname: PAUSED\nkind: proc\ndescription: a linear proc with a pause\nproc: |\n"
        "  SERVE READ.md\n  FINAL\n  INFER\n---\npause then answer\n",
        at=prove_home.meta)
    paused = prove_c().start(pause_doc)
    resumed_past = prove_c().resume(pause_doc)
    ended = prove_c().submit("")
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
    prove_c().forget()
    return 0
