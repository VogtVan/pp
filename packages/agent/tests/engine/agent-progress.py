"""Scenario `agent-progress` -- 7 case(s) (batches la-progression-du-reveil, 2026-09-27, and
le-package-agent, rework B, 2026-10-07: the wake-up its principal conducts; split out of
`agent-home` by les-scenarios-par-maison, 2026-10-07): the wake-up followed, bounded, and the mark
that never leaks.
- (rework B) the mark does not leak: the witness finds neither `PP_CONDUCTED_BY_PRINCIPAL` nor
  `PP_NEW_KEY` in its environment; a bare call it tries is refused `principal-advances` and the
  wake-up goes on to its frontier; a `-new` it tries mid-exchange opens nothing (the soft line), and
  the one it tries at the launch of the FINAL opens a STRAY run -- said on stderr (`stray run <key>`),
  counted at the verdict, never forgotten by the house
- (rework B, le-plancher-du-mode-principal) the floor of the cap: `ag2`, born by `add` at the cap of
  200000, is woken in 2 launches (the boot, then the FINAL); its SETTINGS set back to the template's
  25000, in 2 still -- a run its principal conducts is cut under 200000 at least; its record says
  `launches`
- (rework B) the loop is bounded: a witness that never deposits its proof, under a law of production
  and `--launches 3`, ends on `launches-spent` -- exit 2, its last response kept with `launches` 3,
  the run standing, the wake lock free; `--launches 0` and `--launches soon` refuse `launches-invalid`
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
    bare_calls = h.calls(out_bare)
    known = set(keys(ag2_meta))                        # an agent with no run standing: a stray -new opens one
    out_stray = bench.temp() / "pstray"
    strayed = h.call("agent", "run", "ag2", "--message", "try -new", *h.harnessed_at("stray-new", out_stray, ag2_meta))
    new_keys = [one for one in keys(ag2_meta) if one not in known]
    stray_calls = h.calls(out_stray)
    stray_key = next((one for one in new_keys if f"stray run {one}" in strayed.stderr), "")
    ag2_responses = len([one for one in responses() if one.get("agent") == "ag2"])
    if (plain.returncode == 0 and "PP_CONDUCTED_BY_PRINCIPAL" not in plain_env and "PP_NEW_KEY" not in plain_env
            and "PP_CONDUCTED_BY_PRINCIPAL" not in h.environment(out_bare)
            and bared.returncode == 0 and f"run {key_bare} · exchange 1 · parked" in bared.stderr
            and bare_calls and all(one["rc"] == 2 and "principal-advances" in one["err"] for one in bare_calls)
            and refusals and all(one.get("code") == "principal-advances" for one in refusals)
            and strayed.returncode == 0 and len(new_keys) == 2 and stray_key
            and "a run is already open" in stray_calls[0]["out"] and stray_calls[0]["rc"] == 0
            and "1 stray run(s)" in strayed.stderr
            and persistence.slot_of(ag2_meta, stray_key).is_file()):
        held("the mark does not leak, a bare call is refused, a stray -new is said",
             f"the witness's environment carries no PP_CONDUCTED_BY_PRINCIPAL and no PP_NEW_KEY; its {len(bare_calls)} "
             f"bare call(s) refused principal-advances, the wake-up parked; its -new mid-exchange opened nothing (the "
             f"soft line), the one at the FINAL opened {stray_key}: `stray run {stray_key}` on stderr, counted at the "
             "verdict, the slot kept")
    else:
        failures.append(f"  ✗ the mark and the strays     env={sorted(plain_env)} bared={bared.returncode} key={key_bare!r} "
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
    if (capped.returncode == 0 and len(kept_capped) == 1 and kept_capped[0].get("launches") == 2
            and "2 launch(es)" in capped.stderr
            and chunked.returncode == 0 and len(kept_chunked) == 2 and kept_chunked[1].get("launches") == 2
            and "2 launch(es)" in chunked.stderr):
        held("the floor of the cap holds a lowered setting", "ag2 at the cap add wrote (200000): 2 launches, the boot "
             "whole then the FINAL; at the template's 25000: 2 still, the floor of a principal's cap; the record says launches")
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
    loop_line = h.status_line(key_loop, "ag2") if key_loop else ""
    zero = h.call("agent", "run", "ag2", "--message", "x", "--launches", "0", *h.harnessed_at("play", out_loop, ag2_meta))
    word = h.call("agent", "run", "ag2", "--message", "x", "--launches", "soon", *h.harnessed_at("play", out_loop, ag2_meta))
    if (looped.returncode == 2 and "launches-spent" in looped.stderr and looped.stdout == "witness answer: loop\n"
            and len(kept_loop) == 1 and kept_loop[0].get("launches") == 3 and kept_loop[0].get("harness_rc") == 0
            and "standing" in loop_line and "dead" not in loop_line
            and key_loop and not lock.held(A.launcher(ag2_meta, key_loop))
            and zero.returncode == 2 and "launches-invalid" in zero.stderr
            and word.returncode == 2 and "launches-invalid" in word.stderr
            and len(keys(ag2_meta)) == len(known) + 1):
        held("the loop is bounded", "a witness that never deposits its proof under --launches 3: launches-spent, "
             "exit 2, its last response kept with launches 3, the run standing, the wake lock free; --launches 0 "
             "and soon refuse launches-invalid, nothing launched")
    else:
        failures.append(f"  ✗ launches bound              rc={looped.returncode} kept={kept_loop} status={loop_line!r} "
                        f"{looped.stderr[-300:]!r} zero={zero.returncode} word={word.returncode} "
                        f"{zero.stderr[-120:]!r} {word.stderr[-120:]!r}")
    (ag2_meta / "procs" / "TURN.md").unlink()

    # --- the wake-up is followed on stderr -------------------------------------------------------------
    followed = h.wake("slow", "pause", "--heartbeat", "1")
    lines = followed.stderr.splitlines()

    def at(fragment: str) -> int:
        return next((i for i, one in enumerate(lines) if fragment in one), -1)

    opened, quiet, parked = at("· opened"), at("· no event for 1s"), at("· parked")
    verdict = at("pp-agent: agents/ag1 · run")
    launched, advanced = at("· launch 1 ·"), at("· advanced")
    staged = [i for i, one in enumerate(lines) if "BOOT ▸" in one]
    if (followed.returncode == 0 and followed.stdout == "witness answer: pause\n"
            and -1 < opened < quiet < parked < verdict and staged and opened < staged[0] < parked
            and -1 < launched < advanced < verdict
            and all(one.startswith("[") or one.startswith("pp-agent:") for one in lines)):
        held("the wake-up is followed", f"{len(lines)} stderr line(s): opened, {len(staged)} block(s), launch 1, "
             "no event for 1s, advanced, parked, then the verdict; stdout the response alone")
    else:
        failures.append(f"  ✗ progress                    rc={followed.returncode} {followed.stdout!r} {lines[:14]!r}")

    # --- --quiet leaves the verdict alone ----------------------------------------------------------------
    out_quiet = bench.temp() / "pquiet"
    hushed = h.call("agent", "run", "agents/ag1", "--message", "slow", "--heartbeat", "1", "--quiet",
                    *h.harnessed_at("pause", out_quiet))
    hushed_lines = hushed.stderr.splitlines()
    if (hushed.returncode == 0 and hushed.stdout == "witness answer: pause\n"
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
            and "launch" in events and "advanced" in events
            and any(one.get("event") == "block" and one.get("wait") for one in objects)
            and json.loads(machine.stdout).get("state") == "parked"):
        held("under --json the progress is JSON", f"{len(objects)} object(s) on stderr -- new, blocks, launch, "
             "advanced, quiet, the parked block -- then the verdict; stdout the record object")
    else:
        failures.append(f"  ✗ progress json               rc={machine.returncode} {machine.stderr[:400]!r}")
    return 0
