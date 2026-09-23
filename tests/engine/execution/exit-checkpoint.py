"""Scenario `exit-checkpoint` -- 2 case(s), in the monolith's order:
- PP7 P1/L1 le-checkpoint-de-sortie: a frame proves on its way out
- PP7 P1/L2 les-annonces-et-traces: the agent sees the exit coming
(la-preuve-sans-interrupteur, 2026-09-05: no `prove:` arms a frame, no `-sp` skips a
checkpoint -- a law of production in force is what arms it, an empty answer repairs)
"""
from __future__ import annotations

import json
from pathlib import Path
from conductor import Conductor, render, discovery


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- PP7 P1/L1 le-checkpoint-de-sortie: a frame proves on its way out ------------
    xit_made = bench.env("xitw").made
    xit_engine = xit_made / ".sys" / "engine" / "pp.py"
    xit_member = discovery.instance_member(xit_engine)
    (xit_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n",
        encoding="utf-8")
    (xit_made / "MEMBER.md").write_text(
        (xit_made / "MEMBER.md").read_text(encoding="utf-8")
        .rstrip() + "\nshaped by hand\n", encoding="utf-8")
    (xit_made / "procs").mkdir(exist_ok=True)
    (xit_made / "procs" / "CALLER.md").write_text(
        "---\nname: CALLER\nkind: proc\nconstraints.production: |\n"
        "  X1  the outer law rides the exit.\nproc: |\n  CALL CRAFT.md\n---\n"
        "outer\n", encoding="utf-8")
    (xit_made / "procs" / "CRAFT.md").write_text(
        "---\nname: CRAFT\nkind: proc\nconstraints.production: |\n"
        "  Y1  the crafted line is short.\nproc: |\n  INFER\n---\n"
        "craft one line\n", encoding="utf-8")
    (xit_made / "procs" / "PLAIN.md").write_text(
        "---\nname: PLAIN\nkind: proc\nproc: |\n  INFER\n---\n"
        "one plain line\n", encoding="utf-8")
    (xit_made / "procs" / "HOLLOW.md").write_text(
        "---\nname: HOLLOW\nkind: proc\nproc: |\n  CALL PLAIN.md\n---\n"
        "hollow\n", encoding="utf-8")
    (xit_made / "procs" / "LOOP.md").write_text(
        "---\nname: LOOP\nkind: proc\ncycle: true\nconstraints.production: |\n"
        "  L1  the lap's line lands.\nproc: |\n  INFER\n---\n"
        "one line per cycle\n", encoding="utf-8")
    (xit_made / "procs" / "ARMED.md").write_text(
        "---\nname: ARMED\nkind: proc\nprove: auto\nconstraints.production: |\n"
        "  Z1  a relic switch.\nproc: |\n  INFER\n---\nrelic\n", encoding="utf-8")

    def xit_c() -> Conductor:
        return Conductor(xit_member, discovery.siblings_around(xit_member), xit_engine, "t")

    xit_opened = xit_c().start(xit_c().boot("CALLER.md"))
    xit_text = render(xit_opened) if xit_opened is not None else ""
    xit_armed = (xit_opened is not None
                 and xit_opened.instruction is not None
                 and xit_opened.instruction.keyword == "PROVE"
                 and "X1" in xit_text and "Y1" in xit_text
                 and "(your proof on stdin -- heredoc)" in xit_text
                 and "-sp" not in xit_text)
    xit_foreign = xit_c().submit(json.dumps(
        [{"code": "Q9", "evidence": "no such law", "verdict": "ok"}]))
    xit_repaired = (xit_foreign is not None and "REPAIR" in render(xit_foreign)
                    and "not in force" in (xit_foreign.deviation or "")
                    and xit_foreign.instruction is not None
                    and xit_foreign.instruction.keyword == "PROVE")
    xit_risk = json.dumps([{"code": "Y1", "evidence": "short indeed", "verdict": "ok"}])
    xit_closed = xit_c().submit(xit_risk)          # the code at risk alone: X1 is n/a unnamed
    xit_out = (xit_closed is None
               or xit_closed.instruction is None
               or xit_closed.instruction.keyword != "PROVE")
    if xit_armed and xit_repaired and xit_out:
        held("the exit checkpoint rises, no switch", "a frame with a law of production "
             "proves on its way out, inherited law on screen, no skip offered; a proof "
             "naming a law not in force REPAIRS; the codes at risk alone let it leave")
    else:
        failures.append(f"  ✗ exit checkpoint             {xit_armed}/{xit_repaired}/"
                        f"{xit_out} {xit_text[-200:]!r}")

    empty_c = xit_c()
    empty_c.forget()
    empty_block = empty_c.start(empty_c.boot("CRAFT.md"))
    empty_answer = xit_c().submit("")       # an empty answer is NO proof: it repairs
    if (empty_block is not None and empty_block.instruction is not None
            and empty_block.instruction.keyword == "PROVE"
            and empty_answer is not None and "REPAIR" in render(empty_answer)):
        held("an empty answer repairs", "the checkpoint knows no skip: nothing piped, "
             "the document replays")
    else:
        failures.append(f"  ✗ exit empty                  "
                        f"{empty_answer and render(empty_answer)[-150:]!r}")
    xit_c().submit(json.dumps([{"code": "Y1", "evidence": "held", "verdict": "ok"}]))

    none_c = xit_c()
    none_c.forget()
    none_c.start(none_c.boot("CRAFT.md"))
    none_answer = xit_c().submit("[]")      # an empty array names no code: it repairs
    if none_answer is not None and "names no law of production" in (none_answer.deviation or ""):
        held("a proof names at least one code", "the codes at risk, one at least -- an "
             "empty array is no proof")
    else:
        failures.append(f"  ✗ exit no code                {none_answer and none_answer.deviation!r}")
    xit_c().forget()

    bound_c = xit_c()
    bound_c.forget()
    bound_c.start(bound_c.boot("CALLER.md"))
    lame = json.dumps([{"code": "Q9", "evidence": "no such law", "verdict": "ok"}])
    for _ in range(3):                     # work_repairs_allowed: the instance default 3
        xit_c().submit(lame)
    expect("repair-exhausted", lambda: xit_c().submit(lame))
    if True:
        held("the exit bound still hands back", "the purged checkpoint cannot zero "
             "its own count -- a stable instruction carries it to the operator")

    quiet_runs = []
    for name in ("PLAIN.md", "HOLLOW.md"):
        one_c = xit_c()
        one_c.forget()
        landed = one_c.start(one_c.boot(name))
        quiet_runs.append(landed is None or landed.instruction is None
                          or landed.instruction.keyword != "PROVE")
        expect("run-complete", lambda: xit_c().submit("x"))
    if all(quiet_runs):
        held("the exit knows its silences", "no law of production, and a frame that "
             "produced nothing -- two exits closing their run without one proof block")
    else:
        failures.append(f"  ✗ exit silences               {quiet_runs}")
    relic_c = xit_c()
    relic_c.forget()
    expect("prove-gone", lambda: relic_c.start(relic_c.boot("ARMED.md")))
    held("a relic prove: refuses", "the switch is gone -- a document still carrying it "
         "refuses by name at its opening")

    loop_c = xit_c()
    loop_c.forget()
    first_pass = loop_c.start(loop_c.boot("LOOP.md"))
    first_is = (first_pass is not None and first_pass.instruction is not None
                and first_pass.instruction.keyword == "PROVE")
    second_pass = xit_c().submit(json.dumps(      # proven -> rewind -> lap 2 -> checkpoint
        [{"code": "L1", "evidence": "landed", "verdict": "ok"}]))
    second_is = (second_pass is not None and second_pass.instruction is not None
                 and second_pass.instruction.keyword == "PROVE")
    if first_is and second_is:
        held("a cycle proves every productive lap", "the rewind purges the played "
             "checkpoint and the next lap earns its own")
    else:
        failures.append(f"  ✗ exit cycle                  {first_is}/{second_is}")
    xit_c().forget()

    # --- PP7 P1/L2 les-annonces-et-traces: the agent sees the exit coming ------------
    (xit_made / "procs" / "ANN.md").write_text(
        "---\nname: ANN\nkind: proc\nconstraints.production: |\n"
        "  A1  the announced line lands.\nproc: |\n  INFER\n---\n"
        "one announced line\n", encoding="utf-8")
    (xit_made / "procs" / "TFIN.md").write_text(
        "---\nname: TFIN\nkind: proc\ncycle: true\nconstraints.production: |\n"
        "  G1  the work lands\nproc: |\n"
        "  WORK\n  FINAL\n---\nwork then close\n", encoding="utf-8")
    (xit_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: none\n---\n",
        encoding="utf-8")

    ann_c = xit_c()
    ann_c.forget()
    ann_block = ann_c.start(ann_c.boot("ANN.md"))
    ann_text = render(ann_block) if ann_block is not None else ""
    ann_next = xit_c().submit("")                  # the INFER said in chat: the exit comes
    ann_trace = max((xit_made / ".sys" / "state").glob("session-*.jsonl"),
                    key=lambda one: one.stat().st_mtime).read_text(encoding="utf-8")
    if (ann_block is not None and "[-sp]" not in ann_text and "-sp" not in ann_text
            and ann_next is not None and "INFER proof" in render(ann_next)
            and "proof-skipped" not in ann_trace):
        held("the closing announces no switch", "the last step of a frame carries the "
             "bare call; the checkpoint rises at the exit, nothing skipped in the trace")
    else:
        failures.append(f"  ✗ exit announced              {ann_text[-120:]!r} "
                        f"{ann_next and render(ann_next)[-120:]!r}")
    xit_c().submit(json.dumps([{"code": "A1", "evidence": "landed", "verdict": "ok"}]))

    fin_c = xit_c()
    fin_c.forget()
    fin_start = fin_c.start(fin_c.boot("TFIN.md"))   # the due checkpoint BREAKS the
    fin_stext = render(fin_start) if fin_start is not None else ""  # adjacency
    fin_proof = xit_c().submit("")           # the WORK closes; the proof gates
    fin_gates = (fin_proof is not None and fin_proof.instruction is not None
                 and fin_proof.instruction.keyword == "PROVE")
    fin_front = xit_c().submit(json.dumps(   # proven -> the frontier delivers
        [{"code": "G1", "evidence": "landed", "verdict": "ok"}]))
    fin_ftext = render(fin_front) if fin_front is not None else ""
    fin_lap2 = xit_c().submit("")            # the resume opens on lap 2, NOT a proof
    fin_clean = (fin_lap2 is None or fin_lap2.instruction is None
                 or fin_lap2.instruction.keyword != "PROVE")
    if ("[-sp]" not in fin_stext and fin_gates
            and "the turn closes on its proof" in fin_ftext
            and "pipe or -sp" not in fin_ftext
            and fin_clean):
        held("the proof gates the frontier", "the adjacency breaks, the checkpoint "
             "lands BEFORE the delivery -- same turn; the promise is literal and "
             "the resume opens on fresh work")
    else:
        failures.append(f"  ✗ frontier gate               {'[-sp]' in fin_stext}/"
                        f"{fin_gates}/{'closes on its proof' in fin_ftext}/"
                        f"{fin_clean} {fin_ftext[-120:]!r}")

    (xit_made / "procs" / "MFIN.md").write_text(
        "---\nname: MFIN\nkind: proc\nconstraints.production: |\n"
        "  F1  the delivery lands.\nproc: |\n"
        "  INFER\n  FINAL\n  INFER\n  FINAL\n---\ntwo deliveries\n",
        encoding="utf-8")
    mf_c = xit_c()
    mf_c.forget()
    mf_c.start(mf_c.boot("MFIN.md"))
    proven = json.dumps([{"code": "F1", "evidence": "landed", "verdict": "ok"}])
    mf_p1 = xit_c().submit("")               # segment 1 closes -> its proof
    mf_f1 = xit_c().submit(proven)           # proven -> frontier 1
    mf_i2 = xit_c().submit("")               # resume -> segment 2's INFER
    mf_p2 = xit_c().submit("")               # segment 2 closes -> its proof
    mf_f2 = xit_c().submit(proven)           # proven -> frontier 2
    mf_end = xit_c().submit("")              # exhausted, nothing unproven -> END
    mf_proofs = all(one is not None and one.instruction is not None
                    and one.instruction.keyword == "PROVE" for one in (mf_p1, mf_p2))
    mf_silent = (mf_end is None or mf_end.instruction is None
                 or not (mf_end.instruction.keyword == "PROVE"
                         and not mf_end.instruction.done))
    if mf_proofs and mf_f1 is not None and mf_f2 is not None and mf_silent:
        held("each segment proves before ITS delivery", "two frontiers, two "
             "checkpoints, each ahead of its FINAL; the exhaustion owes nothing")
    else:
        failures.append(f"  ✗ multi-frontier              {mf_proofs} "
                        f"{mf_end and mf_end.instruction and mf_end.instruction.keyword}")

    plain_c = xit_c()
    plain_c.forget()
    plain_c.start(plain_c.boot("PLAIN.md"))
    plain_trace = max((xit_made / ".sys" / "state").glob("session-*.jsonl"),
                      key=lambda one: one.stat().st_mtime).read_text(encoding="utf-8")
    if "PROVE" not in plain_trace:
        held("no law, no checkpoint", "a frame without a law of production leaves "
             "without one proof kind in its trace -- nothing to prove, nothing to say")
    else:
        failures.append("  ✗ plain traced                a proof kind leaked")
    (xit_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n",
        encoding="utf-8")
    xit_c().forget()
    return 0
