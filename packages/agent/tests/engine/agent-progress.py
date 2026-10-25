"""Scenario `agent-progress` -- 8 case(s) (batches la-progression-du-reveil, 2026-09-27, and
le-package-agent, rework B, 2026-10-07: the wake-up its principal conducts; split out of
`agent-home` by les-scenarios-par-maison, 2026-10-07): the wake-up followed, bounded, and the mark
that never leaks.
- (rework B) the mark does not leak: the witness finds neither `PP_CONDUCTED_BY_PRINCIPAL` nor
  `PP_NEW_KEY` in its environment; a bare call it tries is refused `principal-advances` and the
  wake-up goes on to its AWAIT; a `-new` it tries mid-exchange opens nothing (rc 0, no run) -- and
  since the bare AWAIT is launched no more (plan fixes2), no launch stands at a parked run: no stray
- (rework B, le-plancher-du-mode-principal) the floor of the cap: `ag2`, born by `add` at the cap of
  200000, is woken in 2 launches (the boot, then the AWAIT); its SETTINGS set back to the template's
  25000, in 2 still -- a run its principal conducts is cut under 200000 at least; its record says
  `launches`
- (rework B) the loop is bounded: a witness that never deposits its proof, under a law of production
  and `--launches 3`, ends on `launches-spent` -- exit 2, its last response kept with `launches` 3,
  the run standing, the wake lock free; `--launches 0` and `--launches soon` refuse `launches-invalid`
- a spent bound keeps the step: under `--launches 1` on a root of documents whose entry leaves to two INFER
  steps cut by a `§`, the first launch answers ACT{1/2}; the advance serves ACT{2/2} with the WORK after it in
  one output, which the bound leaves to nobody: kept `pending` at the record, it is the very prompt of the next
  wake-up's launch (`--run`), no call made; that launch answers both, the run parks
- the wake-up is followed: while a witness pauses mid-turn, stderr says `opened`, the blocks,
  `launch 1`, `advanced`, `no event for 1s` under `--heartbeat 1`, then `parked` and the verdict;
  stdout is the response
- `--quiet` leaves the verdict alone on stderr; the witness receives the same prompts
- `--heartbeat` is judged: 0 or a word refuses `heartbeat-invalid`, nothing launched
- under `--json` the progress is one JSON object per line on stderr (`at`, `run`, `event`), the
  launcher's own events (`launch`, `advanced`) among the run's
"""
from __future__ import annotations

import json
from pathlib import Path

from conductor import persistence
from conductor.state import lock
from tests.harness import support

A = support(__file__, "agent")
HEAD = A.HEAD


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    keys, counted, responses = h.keys, h.counted, h.responses
    ag2_meta = h.born("ag2")                              # an agent born by `add`: the cap of 200000 at its SETTINGS
    h.lawful()                                            # both agents owe a proof: two launches, the boot with the
    h.lawful(ag2_meta)                                    # WORK then the AWAIT (plan fixes1)

    # --- the mark does not leak; a bare call is refused; a stray -new is said (g) ----------------------------
    runs_before = sorted(keys())
    plain = h.wake("plain play")
    plain_env = h.environment()
    out_bare = bench.temp() / "pbare"
    bared = h.call("agent", "run", "agents/ag1", "--message", "try the bare call", *h.harnessed_at("bare", out_bare))
    key_bare = next((one for one in keys() if one not in set(runs_before) and one != (keys()[0] if keys() else "")), "")
    key_bare = next((one for one in keys() if one not in set(runs_before)
                     and any(m.get("message") == "try the bare call" and m.get("run") == one for m in h.messages())), "")
    refusals = [one for one in h.trace(key_bare) if one.get("kind") == "refusal"] if key_bare else []
    bare_calls = [one for one in h.calls(out_bare) if one.get("args") == [key_bare]]   # its proof deposit apart
    known = set(keys(ag2_meta))                        # an agent with no run standing: a stray -new opens one
    out_stray = bench.temp() / "pstray"
    strayed = h.call("agent", "run", "ag2", "--message", "try -new", *h.harnessed_at("stray-new", out_stray, ag2_meta))
    new_keys = [one for one in keys(ag2_meta) if one not in known]
    stray_calls = [one for one in h.calls(out_stray) if one.get("args", [])[:1] == ["-new"]]   # its proof call apart
    ag2_responses = len([one for one in responses() if one.get("agent") == "ag2"])
    if (plain.returncode == 0 and "PP_CONDUCTED_BY_PRINCIPAL" not in plain_env and "PP_NEW_KEY" not in plain_env
            and "PP_CONDUCTED_BY_PRINCIPAL" not in h.environment(out_bare)
            and bared.returncode == 0 and f"run {key_bare} · exchange 1 · parked" in bared.stderr
            and bare_calls and all(one["rc"] == 2 and "principal-advances" in one["err"] for one in bare_calls)
            and refusals and all(one.get("code") == "principal-advances" for one in refusals)
            and strayed.returncode == 0 and len(new_keys) == 1 and len(stray_calls) == 2
            and all(one["rc"] == 0 for one in stray_calls)
            and h.environment(out_stray).get("PP_CONDUCTED_RUN") == new_keys[0]
            and "stray run" not in strayed.stderr):
        held("the mark does not leak, a bare call is refused, a stray -new opens nothing",
             f"the witness's environment carries no PP_CONDUCTED_BY_PRINCIPAL and no PP_NEW_KEY, and PP_CONDUCTED_RUN "
             f"names the run it plays; its {len(bare_calls)} "
             f"bare call(s) refused principal-advances, the wake-up parked; its two -new, both mid-exchange, opened "
             "nothing (the soft line) -- the bare AWAIT is launched no more, so no launch stands at a parked run")
    else:
        failures.append(f"  ✗ the mark and the strays     env={sorted(plain_env)} stray_env={h.environment(out_stray).get('PP_CONDUCTED_RUN')!r} "
                        f"bared={bared.returncode} key={key_bare!r} bared_err={bared.stderr[-200:]!r} "
                        f"calls={bare_calls[:2]} refusals={[one.get('code') for one in refusals]} "
                        f"strayed={strayed.returncode} new={new_keys} stray_calls={stray_calls[:2]} "
                        f"{strayed.stderr[-300:]!r}")

    # --- the floor of the cap holds a lowered setting (h) --------------------------------------------------------------------
    out2 = bench.temp() / "p2"
    capped = h.call("agent", "run", "ag2", "--message", "one piece", *h.harnessed_at("play", out2, ag2_meta))
    kept_capped = [one for one in responses() if one.get("agent") == "ag2"][ag2_responses:]
    ag2_settings = ag2_meta / "SETTINGS.md"
    text2 = ag2_settings.read_text(encoding="utf-8")
    ag2_settings.write_text(text2.replace("max_harness_tool_output: 200000", "max_harness_tool_output: 25000", 1), encoding="utf-8")
    chunked = h.call("agent", "run", "ag2", "--message", "two pieces", *h.harnessed_at("play", out2, ag2_meta))
    ag2_settings.write_text(text2, encoding="utf-8")
    kept_chunked = [one for one in responses() if one.get("agent") == "ag2"][ag2_responses:]
    # TWO launches: the boot with the WORK, then the checkpoint one block later (never fused under a `=> response`);
    # the bare AWAIT the proof leaves is served and launched no more
    if (capped.returncode == 0 and len(kept_capped) == 1 and kept_capped[0].get("launches") == 2
            and "2 launch(es)" in capped.stderr
            and chunked.returncode == 0 and len(kept_chunked) == 2 and kept_chunked[1].get("launches") == 2
            and "2 launch(es)" in chunked.stderr):
        held("the floor of the cap holds a lowered setting", "ag2 at the cap add wrote (200000): 2 launches, the boot "
             "with the WORK, then the checkpoint; at the template's 25000: 2 still, the floor of a principal's "
             "cap; the record says launches")
    else:
        failures.append(f"  ✗ the floor and launches       {capped.returncode}/{chunked.returncode} "
                        f"{[one.get('launches') for one in kept_chunked]} {capped.stderr[-200:]!r} {chunked.stderr[-200:]!r}")

    # --- the loop is bounded (f) ---------------------------------------------------------------------------------
    (ag2_meta / "procs").mkdir(exist_ok=True)
    (ag2_meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.production: |\n  TL1  the answer names the witness\n---\n\n# A law for the bench\n",
        encoding="utf-8")
    known = set(keys(ag2_meta))
    out_loop = bench.temp() / "ploop"
    looped = h.call("agent", "run", "ag2", "--message", "never prove", "--launches", "3",
                    *h.harnessed_at("loop", out_loop, ag2_meta))
    key_loop = next((one for one in keys(ag2_meta) if one not in known), "")
    kept_loop = [one for one in responses() if one.get("run") == key_loop]
    loop_state = h.face(key_loop, "ag2").get("state") if key_loop else None
    zero = h.call("agent", "run", "ag2", "--message", "x", "--launches", "0", *h.harnessed_at("play", out_loop, ag2_meta))
    word = h.call("agent", "run", "ag2", "--message", "x", "--launches", "soon", *h.harnessed_at("play", out_loop, ag2_meta))
    if (looped.returncode == 2 and "launches-spent" in looped.stderr and kept_loop
            and looped.stdout == f"{A.composed(kept_loop[-1])}\n" and "witness answer: loop" in looped.stdout
            and len(kept_loop) == 1 and kept_loop[0].get("launches") == 3 and kept_loop[0].get("harness_rc") == 0
            and loop_state == "standing"
            and key_loop and not lock.held(A.launcher(ag2_meta, key_loop))
            and zero.returncode == 2 and "launches-invalid" in zero.stderr
            and word.returncode == 2 and "launches-invalid" in word.stderr
            and len(keys(ag2_meta)) == len(known) + 1):
        held("the loop is bounded", "a witness that never deposits its proof under --launches 3: launches-spent, "
             "exit 2, its last response kept with launches 3, the run standing, the wake lock free; --launches 0 "
             "and soon refuse launches-invalid, nothing launched")
    else:
        failures.append(f"  ✗ launches bound              rc={looped.returncode} kept={kept_loop} state={loop_state!r} "
                        f"{looped.stderr[-300:]!r} zero={zero.returncode} word={word.returncode} "
                        f"{zero.stderr[-120:]!r} {word.stderr[-120:]!r}")
    (ag2_meta / "procs" / "TURN.md").unlink()

    # --- a spent bound leaves the run on the step its launch answered: the next wake-up advances it ------
    # a root of documents: ENTRY.md at turn.begin leaves to ACT.md, two INFER steps said in the chat,
    # cut by a `§` -- the second output carries ACT{2/2} and the WORK that follows it in one piece
    docs = h.ws / "teams" / "acts"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "ENTRY.md").write_text("---\nproc: |\n  SERVE\nserve: |\n  ENTRY.md\nattach: turn.begin\nnext: ACT.md\n"
                                   "---\n# ENTRY\n\nThe acts follow.\n", encoding="utf-8")
    (docs / "ACT.md").write_text("---\nproc: |\n  INFER\n  §\n  INFER\noutput: line\n---\n# ACT\n\nSay one line.\n",
                                 encoding="utf-8")
    known = set(keys(ag2_meta))
    out_acts = bench.temp() / "pacts"
    first_act = h.call("agent", "run", "ag2", "--message", "act", "--launches", "1", "--documents", "teams/acts",
                       *h.harnessed_at("play", out_acts, ag2_meta))
    key_act = next((one for one in keys(ag2_meta) if one not in known), "")
    second_act = h.call("agent", "run", "ag2", "--run", key_act, "--message", "go on", "--launches", "1",
                        *h.harnessed_at("play", out_acts, ag2_meta)) if key_act else None
    prompts_act = sorted(Path(out_acts.as_posix()).parent.glob(out_acts.name + ".prompt.*"),
                         key=lambda one: int(one.name.rsplit(".", 1)[1]))
    texts_act = [one.read_text(encoding="utf-8") for one in prompts_act]
    stacks_act = [[line for line in text.splitlines() if "ACT{" in line or line.startswith("WORK ")] for text in texts_act]
    advanced_act = [one.get("event") for one in h.trace(key_act, ag2_meta) if one.get("kind") == "advance"] if key_act else []
    kept_act = [one for one in responses() if one.get("run") == key_act]
    if (first_act.returncode == 2 and "launches-spent" in first_act.stderr and key_act
            and second_act is not None and second_act.returncode == 0
            and len(texts_act) == 2 and len(kept_act) == 2
            and any("ACT{1/2}" in line for line in stacks_act[0]) and not any("ACT{2/2}" in line for line in stacks_act[0])
            and any("ACT{2/2}" in line for line in stacks_act[1]) and any(line.startswith("WORK ") for line in stacks_act[1])
            and kept_act[0].get("pending") and "ACT{2/2}" in kept_act[0]["pending"] and "pending" not in kept_act[1]
            and texts_act[1].endswith(kept_act[0]["pending"])
            and h.face(key_act, "ag2").get("state") == "parked"):
        held("a spent bound keeps the step", f"run {key_act}: launch 1 answers ACT{{1/2}}, the advance serves "
             "ACT{2/2} with the WORK after it in one output, kept `pending` at the record (launches-spent); the "
             "second wake-up launches on that very output, no call made, and parks")
    else:
        failures.append(f"  ✗ spent keeps the step        rc={first_act.returncode}/{getattr(second_act, 'returncode', None)} "
                        f"key={key_act} prompts={len(texts_act)} stacks={stacks_act} "
                        f"pending={[bool(one.get('pending')) for one in kept_act]} "
                        f"state={h.face(key_act, 'ag2').get('state') if key_act else None!r} "
                        f"{first_act.stderr[-200:]!r} {(second_act.stderr if second_act else '')[-200:]!r}")

    # --- the wake-up is followed on stderr -------------------------------------------------------------
    followed = h.wake("slow", "pause", "--heartbeat", "1")
    lines = followed.stderr.splitlines()

    def at(fragment: str) -> int:
        return next((i for i, one in enumerate(lines) if fragment in one), -1)

    opened, quiet, parked = at("· opened"), at("· no event for 1s"), at("· parked")
    verdict = at("pp-agent: agents/ag1 · run")
    launched = at("· launch 1 ·")
    advanced = max(at("· advanced"), at("· served held output"))   # the house's own call between the launches
    staged = [i for i, one in enumerate(lines) if "BOOT ▸" in one]
    if (followed.returncode == 0 and followed.stdout == f"{A.composed(responses()[-1])}\n"
            and "witness answer: pause" in followed.stdout
            and -1 < opened < quiet < parked < verdict and staged and opened < staged[0] < parked
            and -1 < launched < advanced < verdict
            and all(one.startswith("[") or one.startswith("pp-agent:") for one in lines)):
        held("the wake-up is followed", f"{len(lines)} stderr line(s): opened, {len(staged)} block(s), launch 1, "
             "no event for 1s, the house's call between the launches, parked, then the verdict; stdout the response alone")
    else:
        failures.append(f"  ✗ progress                    rc={followed.returncode} {followed.stdout!r} {lines[:14]!r}")

    # --- --quiet leaves the verdict alone ----------------------------------------------------------------
    out_quiet = bench.temp() / "pquiet"
    hushed = h.call("agent", "run", "agents/ag1", "--message", "slow", "--heartbeat", "1", "--quiet",
                    *h.harnessed_at("pause", out_quiet))
    hushed_lines = hushed.stderr.splitlines()
    if (hushed.returncode == 0 and hushed.stdout == f"{A.composed(responses()[-1])}\n"
            and "witness answer: pause" in hushed.stdout
            and len(hushed_lines) == 1 and hushed_lines[0].startswith("pp-agent: agents/ag1 · run")
            and h.read(".prompt.w-1.1", out_quiet).startswith(f"{HEAD}\nslow\n\n▌ pp · run ")):
        held("--quiet leaves the verdict alone", "one stderr line, the verdict; stdout the response; the "
             "witness received the same prompts as a followed wake-up")
    else:
        failures.append(f"  ✗ quiet                       rc={hushed.returncode} {hushed_lines!r} prompt={h.read('.prompt.w-1.1', out_quiet)[:60]!r}")

    # --- --heartbeat is judged ----------------------------------------------------------------------------
    runs_before, recorded = len(keys()), counted()
    zero = h.wake("x", "play", "--heartbeat", "0")
    word = h.wake("x", "play", "--heartbeat", "soon")
    if (zero.returncode == 2 and "heartbeat-invalid" in zero.stderr
            and word.returncode == 2 and "heartbeat-invalid" in word.stderr
            and len(keys()) == runs_before and counted() == recorded):
        held("--heartbeat is judged", "0 and a word refuse heartbeat-invalid; no run opened, no record")
    else:
        failures.append(f"  ✗ heartbeat judged            {zero.returncode}/{word.returncode} "
                        f"{zero.stderr[-160:]!r} {word.stderr[-160:]!r}")

    # --- under --json the progress is JSON ------------------------------------------------------------
    machine = h.wake("slow", "pause", "--heartbeat", "1", "--json")
    objects, verdicts = [], []
    for one in machine.stderr.splitlines():
        if one.startswith("pp-agent:"):
            verdicts.append(one)
            continue
        try:
            objects.append(json.loads(one))
        except ValueError:
            objects.append({"unparsed": one})
    events = [one.get("event") for one in objects]
    if (machine.returncode == 0 and len(verdicts) == 1 and objects
            and all({"at", "run", "event"} <= set(one) for one in objects)
            and events[0] == "new" and "quiet" in events and "block" in events
            and "launch" in events and ("advanced" in events or "served" in events)
            and any(one.get("event") == "block" and one.get("wait") for one in objects)
            and json.loads(machine.stdout).get("state") == "parked"):
        held("under --json the progress is JSON", f"{len(objects)} object(s) on stderr -- new, blocks, launch, "
             "advanced, quiet, the parked block -- then the verdict; stdout the record object")
    else:
        failures.append(f"  ✗ progress json               rc={machine.returncode} {machine.stderr[:400]!r}")
    return 0
