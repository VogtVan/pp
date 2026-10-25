"""Scenario `principal-mode` -- a run is conducted by the LLM or by its principal, set at `-new`
under `PP_CONDUCTED_BY_PRINCIPAL=true`; in the principal's mode no ending that moves the run on
carries a command, an output is cut under a FLOOR of the cap (the larger of the instance's
`max_harness_tool_output` and `settings.PRINCIPAL_CAP`, since the output reaches the harness on its
standard input), and `conduction: hybrid` answers the agent's call with the block whose closing asks
it a VALUE -- a block that moves the run on stays held for the principal's call.

The mode:
- (b) under `true`: `conducted_by: principal` at the slot and on the trace's `new` line
- (c) the endings: CONTINUE, AWAIT and an unconsumed FREE step render no command; a proof, a choice
  and a production the tool takes keep theirs
- (d) the chunks: at a cap equal to the floor of the principal's, one block past it cuts into as
  many chunks in both modes, the same matter in the same order; the principal's intermediate chunks
  carry no command
- (e) the recovery texts: the principal's soft catch closes without a command where the LLM's keeps
  it; a view past the cap comes cut and keeps nothing; an agent's value over a waiting reading
  bounces `chunk-pending`, unplayed
- (f) an upgrade's renewal keeps the mode: the mark carries it, the reopened run has it
- (g) any other value refuses `conducted-by-invalid` and leaves no slot
- (h) `-hook` serves the pending block of a run conducted by its principal

The floor of the cap:
- (a) under the mark, on an instance at 20000, an opening that serves a reading of 60000 characters
  comes in ONE output: nothing waits at the run
- (c) a setting above the floor holds under the mark: at 300000 a reading of 250000 characters comes
  whole
- (d) `settings.served_cap` is the one rule: raised to the floor under the mark alone, a higher
  setting kept, a cap of 0 cutting nothing in either mode

The hybrid conduction:
- (a) `-s LAPS` from the WORK answers the door's first block (the field asked) inline; the field
  piped answers the first lap inline (its words and the proof's command); each proof the next; the
  trace says `inline` with its act; nothing held meanwhile
- (b) the last proof's answer is the TURN's WORK, a FREE step on a bare CONTINUE -- held, the value's
  held line, nothing inline
- (c) the principal's bare calls serve the held WORK, then the AWAIT
- (e) under a host cap: an inline block past the cap comes cut, the rest served by the agent's bare
  keyed calls, the reading it staged proven once the last chunk left
- (f) `-stats <key> -json` counts the inline outputs, the period's line says them
"""
from __future__ import annotations

import json
import os

from conductor import Conductor, persistence, render, settings
from tests.harness import cli, support

run = support(__file__, "run")

WORKS = "---\nname: WORKS\nkind: proc\ndescription: a witness\nproc: |\n  WORK\n  WORK\n---\nwork\n"
PICKER = ("---\nname: PICKER\nkind: proc\ndescription: a witness\noutput: json\nproc: |\n"
          "  INFER\n  PICK verdict\n---\nelect\n")
AT_FLOOR = f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {settings.PRINCIPAL_CAP}\n---\n"
LINE = "long line of matter\n"

LAPPED = run.PROVER.replace("constraints.production", "tools: |\n  LAPS\nconstraints.production")
LAPS = ("---\nname: LAPS\nkind: proc\ndescription: a described door\noutput: any\nfield: |\n  two names\n"
        "constraints.production: |\n  LP1  the lap names its element\nproc: |\n  INFER\n  PROVE\n---\nlap\n")
LAPS_LONG = LAPS.replace("proc: |\n  INFER\n  PROVE", "proc: |\n  SERVE LONG.md\n  INFER\n  PROVE")
LAP_READ = "---\nname: LONG\nkind: doc\n---\n\n" + "a long line of matter to read\n" * 300 + "\n"
HYBRID = ("---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\ninstructions_fusion: max\n"
          "conduction: hybrid\n---\n")
            # the fused stretch: a lap's line and its proof in ONE output, as the template plays it


def _long(chars: int) -> str:
    return "---\nname: LONG\nkind: doc\n---\n\n" + LINE * (chars // len(LINE)) + "\n"


def _settings(cap: int) -> str:
    return f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\n---\n"


def _new_line(env, key: str) -> dict:
    return next((one for one in run.trace(env, key) if one.get("kind") == "new"), {})


def _waiting(env, key: str) -> str:
    return persistence.pending_of(persistence.slot_of(env.made, key)).get("matter", "") if key else ""


def _cap_house(bench, name: str, cap: int, chars: int):
    env = bench.env(name)
    env.write("SETTINGS.md", _settings(cap))
    env.write("LONG.md", _long(chars))
    env.write("procs/LONGRUN.md", run.LONGRUN)
    return env


def _hybrid_house(bench, name: str, laps: str, cap: int):
    env = bench.env(name)
    env.write("procs/PROVER.md", LAPPED)
    env.write("procs/LAPS.md", laps)
    env.write("SETTINGS.md", HYBRID.format(cap=cap))
    return env


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    said = {act: "pp: " + line for act, line in Conductor.HELD_SAID.items()}

    # === the mode =================================================================================

    # --- (b) the principal's mode at the slot and the trace ------------------------------------------
    # one run, the only one of its house: (h) hooks it, (g) adds none
    marked = bench.env("mode-run")
    key, opened = run.opened(marked, True)
    if (opened.returncode == 0 and key and run.slot(marked, key).get("conducted_by") == "principal"
            and _new_line(marked, key).get("conducted_by") == "principal"):
        held("(b) the mode is the run's", f"run {key}: `conducted_by: principal` at its slot and on its "
             "`new` line")
    else:
        failures.append(f"  ✗ (b) the mode at the run       rc={opened.returncode} key={key!r} "
                        f"slot={run.slot(marked, key).get('conducted_by') if key else None} {opened.stderr[-200:]!r}")

    # --- (c) the endings ----------------------------------------------------------------------------
    ends = bench.env("mode-ends")
    works, prover, picker = (ends.write(f"{name}.md", text)
                             for name, text in (("WORKS", WORKS), ("PROVER", run.PROVER), ("PICKER", PICKER)))

    def opened_on(env, path, value="true"):
        env.conductor().forget()
        conductor = env.conductor()
        block = run.under(value, lambda: conductor.start(path))
        return conductor.run_id, block

    started, working = opened_on(ends, works)
    ends.conductor(started).submit("")                 # the second WORK: pending, its closing bare
    finishing = ends.conductor(started).submit("")     # the frontier comes at the principal's call
    run_v, proving = opened_on(ends, prover)
    if proving.output != "proof":
        proving = ends.conductor(run_v).submit("")
    run_p, inferring = opened_on(ends, picker)
    picking = ends.conductor(run_p).submit('["a", "b"]')
    texts = {name: render(one) for name, one in (("work", working), ("final", finishing),
                                                  ("prove", proving), ("infer", inferring),
                                                  ("pick", picking))}
    tails = {name: run.closing(text) for name, text in texts.items()}
    bare = [name for name in ("work", "final") if "./pp" in tails[name]]
    kept = [name for name in ("prove", "infer", "pick") if "./pp" not in tails[name]]
    # no note redoes the standing orders: the closing stands bare, its look-ahead alone
    noted = (tails["work"].strip() == "▶ CONTINUE"
             and tails["final"].splitlines()[0] == "▶ AWAIT"
             and all("message" not in line for line in tails["final"].splitlines()[1:]))
    _, llm_work = opened_on(ends, works, None)
    if not bare and not kept and noted and "./pp" in run.closing(render(llm_work)):
        held("(c) no ending that moves the run carries a command",
             "CONTINUE and AWAIT render bare, the look-ahead alone; the proof, the choice and the "
             "production the tool takes keep `./pp <key>`; the LLM's CONTINUE keeps its command")
    else:
        failures.append(f"  ✗ (c) the endings              commanded={bare} uncommanded={kept} noted={noted} "
                        f"{tails['work']!r} {tails['final']!r}")

    # --- (d) the chunks ----------------------------------------------------------------------------
    long = bench.env("mode-chunks")
    long.write("SETTINGS.md", AT_FLOOR)   # one cap in both modes: the floor itself
    long.write("LONG.md", run.PAST)
    longrun = long.write("LONGRUN.md", run.LONGRUN)

    def read_whole(value):
        # the host carries the standing orders (`PP_MARBLE`): each mode has its own marble,
        # and the block compared in both modes is the reading alone
        long.conductor().forget()
        conductor = long.conductor()
        os.environ["PP_MARBLE"] = "1"
        try:
            block = run.under(value, lambda: conductor.start(longrun))
        finally:
            os.environ.pop("PP_MARBLE", None)
        run_key = conductor.run_id
        chunks = [long.conductor(run_key).rendered(block)]
        while long.conductor(run_key).pending() and len(chunks) < 100:
            chunks.append(long.conductor(run_key).next_chunk())
        return chunks

    by_llm, by_principal = read_whole(None), read_whole("true")

    def matter(chunks):
        # the reading's lines in order, each chunk's heading and closing left out: the room of a
        # chunk is the cap less ITS closing, which each mode words its own way -- the seam may move
        # by a line, the matter never does
        return [line for one in chunks for line in one.split("\n▶ ")[0].splitlines()[1:]
                if line.strip()]

    middles = by_principal[:-1]
    if (len(by_llm) > 1 and len(by_llm) == len(by_principal) and matter(by_llm) == matter(by_principal)
            and all("./pp" not in run.closing(one) for one in middles)
            and all("./pp" in run.closing(one) for one in by_llm[:-1])):
        held("(d) the same chunks, a new injunction",
             f"{len(by_llm)} chunks in both modes, the same matter in order; the principal's {len(middles)} "
             "intermediate chunks show no command, the LLM's keep theirs")
    else:
        failures.append(f"  ✗ (d) the chunks               llm={len(by_llm)} principal={len(by_principal)} "
                        f"{middles[-1][-260:] if middles else ''!r}")

    # --- (e) the recovery texts --------------------------------------------------------------------
    catch_run, _ = opened_on(ends, works)
    caught = render(ends.conductor(catch_run).submit("a draft handed to the tool"))
    llm_run, _ = opened_on(ends, works, None)
    llm_caught = render(ends.conductor(llm_run).submit("a draft handed to the tool"))
    long.conductor().forget()
    viewer = long.conductor()
    viewed_block = run.under("true", lambda: viewer.start(longrun))
    view = long.conductor(viewer.run_id).shown(viewed_block)
    view_slot = persistence.slot_of(long.made, viewer.run_id)
    kept_view = persistence.viewing_of(view_slot).get("matter") or persistence.pending_of(view_slot).get("matter")
    bounce_key, _ = run.opened(long, True, "LONGRUN.md")          # a reading past the floor
    bounce_kinds = run.kinds(long, bounce_key)
    bounced = cli(long.engine, bounce_key, "a value", cwd=long.root) if bounce_key else None
    if ("./pp" not in run.closing(caught) and "./pp" in run.closing(llm_caught)
            and len(view) <= settings.PRINCIPAL_CAP < len(run.PAST) and not kept_view
            and bounced is not None and bounced.returncode == 0 and "chunk-pending" in bounced.stdout
            and "▌" not in bounced.stdout and run.kinds(long, bounce_key) == bounce_kinds):
        held("(e) no recovery text says to call pp",
             "the principal's soft catch closes without `./pp`, the LLM's keeps it; the view comes cut "
             f"({len(view)} characters of a {len(run.PAST)}-character reading), nothing kept; the value "
             "over a waiting reading bounces chunk-pending, nothing traced")
    else:
        failures.append(f"  ✗ (e) the recovery texts       caught={run.closing(caught)!r} llm={run.closing(llm_caught)!r} "
                        f"view={len(view)} kept={bool(kept_view)} "
                        f"bounce_kinds={bounce_kinds}->{run.kinds(long, bounce_key)} "
                        f"bounced={bounced is not None and bounced.stdout[-200:]!r}")

    # --- (f) the renewal keeps the mode -------------------------------------------------------------
    renew_run, _ = opened_on(ends, works)
    slot = persistence.slot_of(ends.made, renew_run)
    persistence.renew(slot, {"kit": "0"}, {"kit": "1"}, "2026-10-05T00:00:00Z")
    mark = persistence.renewed(slot) or {}
    reopened = ends.conductor(renew_run).resume(ends.conductor(renew_run).boot("BOOT.md"))
    if (mark.get("conducted_by") == "principal" and reopened is not None
            and run.slot(ends, renew_run).get("conducted_by") == "principal"):
        held("(f) the renewal keeps the mode", f"run {renew_run}: the mark carries `conducted_by`, "
             "the reopened run is conducted by its principal")
    else:
        failures.append(f"  ✗ (f) the renewal              mark={mark} slot={run.slot(ends, renew_run).get('conducted_by')}")

    # --- (g) any other value refuses ----------------------------------------------------------------
    before = len(persistence.slots(marked.made))
    refused = cli(marked.engine, "-new", cwd=marked.root, env={run.VARIABLE: "yes"})
    if (refused.returncode == 2 and "conducted-by-invalid" in refused.stderr
            and len(persistence.slots(marked.made)) == before):
        held("(g) any other value refuses", "`PP_CONDUCTED_BY_PRINCIPAL=yes`: conducted-by-invalid, "
             "exit 2, no slot")
    else:
        failures.append(f"  ✗ (g) the odd value            rc={refused.returncode} {refused.stderr[-200:]!r} "
                        f"slots={len(persistence.slots(marked.made))}/{before}")

    # --- (h) -hook serves the principal's pending block ----------------------------------------------
    hooked = cli(marked.engine, "-hook", cwd=marked.root)
    if hooked.returncode == 0 and "▶ " in hooked.stdout and "./pp" not in run.closing(hooked.stdout):
        held("(h) -hook serves the principal's block", "the pending block rendered, its closing without a command")
    else:
        failures.append(f"  ✗ (h) the hook                 rc={hooked.returncode} {hooked.stdout[-200:]!r}")

    # === the floor of the cap =====================================================================

    # --- (a) the floor under the mark ------------------------------------------------------------------
    low = _cap_house(bench, "cap-low", 20000, 60000)
    key_a, out_a = run.opened(low, True, "LONGRUN.md")
    waiting_a = _waiting(low, key_a)
    if (out_a.returncode == 0 and key_a and not waiting_a
            and out_a.stdout.count(LINE.strip()) >= 2900 and len(out_a.stdout) > 20000):
        held("(a) the floor under the mark", f"run {key_a} at 20000: the opening serves "
             f"{len(out_a.stdout)} characters in one output, nothing waits")
    else:
        failures.append(f"  ✗ (a) the floor               rc={out_a.returncode} key={key_a!r} "
                        f"waiting={len(waiting_a)} chars={len(out_a.stdout)} {out_a.stderr[-200:]!r}")

    # --- (c) a setting above the floor holds -------------------------------------------------------------
    high = _cap_house(bench, "cap-high", 300000, 250000)
    key_c, out_c = run.opened(high, True, "LONGRUN.md")
    waiting_c = _waiting(high, key_c)
    if out_c.returncode == 0 and key_c and not waiting_c and len(out_c.stdout) > 250000:
        held("(c) a setting above the floor holds", f"at 300000 the reading comes whole under the mark: "
             f"{len(out_c.stdout)} characters")
    else:
        failures.append(f"  ✗ (c) above the floor         marked={len(out_c.stdout)}/{len(waiting_c)}")

    # --- (d) the one rule ----------------------------------------------------------------------------------
    floor = settings.PRINCIPAL_CAP
    ruled = {(20000, True): floor, (20000, False): 20000, (300000, True): 300000, (300000, False): 300000,
             (0, True): 0, (0, False): 0}
    got = {pair: settings.served_cap(*pair) for pair in ruled}
    if floor == 200000 and got == ruled:
        held("(d) served_cap is the one rule", f"floor {floor}: raised under the mark alone, a higher setting "
             "kept, 0 cuts nothing in either mode")
    else:
        failures.append(f"  ✗ (d) served_cap              floor={floor} {got}")

    # === the hybrid conduction ====================================================================

    # --- (a) hybrid: the door, the field, the laps answered inline ---------------------------------------
    one = _hybrid_house(bench, "mode-hybrid", LAPS, 60000)
    key, _ = run.opened(one, True, "PROVER.md")
    door = cli(one.engine, key, "-s", "LAPS", cwd=one.root)
    fielded = cli(one.engine, key, "-", cwd=one.root, stdin='["a", "b"]')
    lap_one = cli(one.engine, key, "-", cwd=one.root, stdin=run.proof_of(fielded.stdout))
    inline = [e for e in run.trace(one, key) if e.get("kind") == "inline"]
    if (key and door.returncode == 0 and "▌" in door.stdout and "INFER field" in door.stdout
            and f"./pp {key} -" in run.closing(door.stdout) and said["door"] not in door.stdout.splitlines()
            and fielded.returncode == 0 and "▌" in fielded.stdout and "LP1] on all produced" in fielded.stdout
            and f"./pp {key} -" in fielded.stdout and said["value"] not in fielded.stdout.splitlines()
            and lap_one.returncode == 0 and "LP1] on all produced" in lap_one.stdout
            and [e.get("act") for e in inline] == ["door", "value", "value"]
            and not run.slot(one, key).get("held")):
        held("(a) the door, the field and the laps come inline", f"run {key}: `-s LAPS` answers the field block, "
             "its closing piping the field; the field the first lap with its proof's command, the proof the "
             "second lap; traced inline door, value, value; nothing held")
    else:
        failures.append(f"  ✗ (a) inline                   key={key!r} rc={door.returncode}/{fielded.returncode}/"
                        f"{lap_one.returncode} inline={[e.get('act') for e in inline]} door={door.stdout[-200:]!r} "
                        f"fielded={fielded.stdout[-200:]!r} held={bool(run.slot(one, key).get('held'))}")

    # --- (b) the last proof's answer moves the run on: held --------------------------------------------------
    lap_two = cli(one.engine, key, "-", cwd=one.root, stdin=run.proof_of(lap_one.stdout))
    checkpoint = cli(one.engine, key, "-", cwd=one.root, stdin=run.proof_of(lap_two.stdout))
    slot_held = run.slot(one, key).get("held") or {}
    if (lap_two.returncode == 0 and "INFER proof [Z1]" in lap_two.stdout
            and checkpoint.returncode == 0 and checkpoint.stdout.strip() == said["value"]
            and slot_held.get("act") == "value" and "WORK any => response" in slot_held.get("matter", "")
            and "CONTINUE" in slot_held.get("tail", "")):
        held("(b) a block that moves the run on stays held", "the second lap's proof answers PROVER's checkpoint "
             "inline; its proof answers one line, the TURN's WORK (a FREE step, a bare CONTINUE) held at the slot")
    else:
        failures.append(f"  ✗ (b) the AWAIT                rc={lap_two.returncode}/{checkpoint.returncode} "
                        f"{lap_two.stdout[-160:]!r} {checkpoint.stdout!r} held={slot_held.get('act')!r} "
                        f"matter={slot_held.get('matter', '')[-80:]!r}")

    # --- (c) the principal's bare calls serve the WORK, then the AWAIT ---------------------------------------
    served = cli(one.engine, key, cwd=one.root, env=run.MARK)
    final = cli(one.engine, key, cwd=one.root, env=run.MARK)
    if (served.returncode == 0 and "WORK any => response" in served.stdout and not run.slot(one, key).get("held")
            and final.returncode == 0 and "▶ AWAIT" in final.stdout
            and (persistence.awaits_of(run.slot(one, key)) == persistence.MESSAGE)):
        held("(c) the agent's bare call refuses, the principal's serves", "the principal's bare call renders "
             "the held WORK, its next the AWAIT, the run parked")
    else:
        failures.append(f"  ✗ (c) bare calls               rc={served.returncode}/{final.returncode} "
                        f"{served.stdout[-120:]!r} {final.stdout[-120:]!r}")

    # --- (e) a host cap: the inline block cut, the rest by the agent's bare calls --------------------------
    three = _hybrid_house(bench, "mode-hybrid-cap", LAPS_LONG, 2000)
    three.write("procs/LONG.md", LAP_READ)
    key3, _ = run.opened(three, True, "PROVER.md")
    cli(three.engine, key3, "-s", "LAPS", cwd=three.root)
    first = cli(three.engine, key3, "-", cwd=three.root, stdin='["a", "b"]')
    proven_first = len(run.slot(three, key3).get("proven") or [])
    chunks, rests = [first.stdout], []
    for _ in range(8):
        rests.append(bool(persistence.viewing_of(persistence.slot_of(three.made, key3)).get("matter")))
        if not rests[-1]:
            break
        chunks.append(cli(three.engine, key3, cwd=three.root).stdout)
    proven_last = len(run.slot(three, key3).get("proven") or [])
    if (key3 and first.returncode == 0 and len(chunks) > 1 and all(len(c) <= 2000 for c in chunks)
            and rests == [True] * (len(chunks) - 1) + [False] and "LP1] on all produced" in chunks[-1]
            and "a long line of matter" in "".join(chunks)
            and proven_last == proven_first + 1):
        held("(e) an inline block past the cap", f"run {key3}: {len(chunks)} chunks under 2000, the last carrying "
             "the proof's command, the reading proven once the last left (not before), nothing waiting")
    else:
        failures.append(f"  ✗ (e) the cap                  key={key3!r} rc={first.returncode} chunks={len(chunks)} "
                        f"sizes={[len(c) for c in chunks]} rests={rests} proven={proven_first}->{proven_last} "
                        f"{chunks[0][-160:]!r}")

    # --- (f) -stats counts the inline outputs --------------------------------------------------------------
    counted = cli(one.engine, "-stats", key, "-json", cwd=one.root)
    spoken = cli(one.engine, "-stats", key, cwd=one.root)
    try:
        period = json.loads(counted.stdout).get("period") or {}
    except ValueError:
        period = {}
    if period.get("inline") == 4 and period.get("held") == 1 and "4.0 inline" in spoken.stdout:
        held("(f) -stats counts the inline outputs", "4 inline (the door, the field, two proofs), 1 held on the run; "
             "the period's line says `4.0 inline`")
    else:
        failures.append(f"  ✗ (f) stats                    inline={period.get('inline')!r} held={period.get('held')!r} "
                        f"{spoken.stdout.splitlines()[-1:]!r}")
    return 0
