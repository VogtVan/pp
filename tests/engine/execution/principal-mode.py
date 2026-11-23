"""Scenario `principal-mode` -- every run is conducted by its principal: no ending that moves the run
on carries a command, an output is cut under a FLOOR of the cap (the larger of the instance's
`max_harness_tool_output` and `settings.PRINCIPAL_CAP`, since the output reaches the harness on its
standard input), and the agent's call -- under the run its launcher names, `PP_CONDUCTED_RUN` -- never
gets a block it has not read: a block never served stays held for the principal's call, whatever its
step asks; only a REPLAY that asks a value (a repair) answers in the call's result.

The mode:
- (a) one mode: a `-new` without any variable opens a run its principal conducts -- the opening
  carries no call, the agent's bare call refuses `principal-advances`
- (c) the endings: an output that leaves a step pending or a value due renders no closing line -- a
  proof, a choice and a production the tool takes name the channel of their value on their own line;
  the end of the passage, where the stack awaits a message, closes on `AWAIT` with no call under it
- (c2) no last message asked: the pending FREE step keeps `=> terminal`, said by its print call;
  behind a proof, a choice and a production pp takes no line of the form `empty` is added (the frame
  counts what it counted, the stack awaits the value); no output carries `=> response`
- (d) the chunks: at a cap equal to the floor, one block past it cuts into several chunks; the
  intermediate chunks add no line above their `MORE` and the fact, no call; the last carries the
  foot of its form
- (e) the recovery texts: the soft catch closes on no line, and the trace says `stray` once with the
  step it answers (batch les-zones-muettes, 2026-10-29); a view past the cap comes cut and keeps
  nothing; an agent's value over a waiting reading bounces `chunk-pending`, unplayed
- (h) `-hook` serves the pending block of a run

The floor of the cap:
- (a) on an instance at 20000, an opening that serves a reading of 60000 characters comes in ONE
  output: nothing waits at the run
- (c) a setting above the floor holds: at 300000 a reading of 250000 characters comes whole
- (d) `settings.served_cap` is the one rule: raised to the floor at the prompt alone, a higher
  setting kept, a cap of 0 cutting nothing on either channel

The blocks never served, held; the replay in the call's result, on a house that poses no setting for it:
- (a) `-s LAPS` from the WORK, the field piped, the first lap's proof: each answered by the held line,
  the door's first block (the field asked), the first lap (its said line on `terminal` and the proof's)
  and the second each served by the principal's bare call, asking no last message; the trace says
  `held` door, value, value, never `inline`
- (b) the second lap's proof holds PROVER's checkpoint; its proof's answer is the TURN's WORK, a FREE
  step said on `terminal` on no closing line -- held, the value's held line, nothing inline; the agent's
  -peek over it renders the block (a view moves nothing) and its bare call refuses
- (c) the principal's bare call serves the held WORK on no closing line; the agent's print of it ends
  the passage, which the principal's next bare call serves closed on `AWAIT` with no call
- (e) under a host cap: a lap's proof that fails -- its REPAIR, a block already read -- answers the
  agent's call inline, cut under the cap, the rest served by the agent's bare keyed calls, nothing held
- (e2) a REPAIR that re-enters a callee whose payload renders anew (its provider's rendering changed) carries
  a reading never served: HELD, nothing inline, the principal's bare call serves it with the new rendering
- (f) the exchange played to its end, `-stats <key> -json` counts the inline outputs and the held ones,
  and the period's line says the inline ones per closed exchange
"""
from __future__ import annotations

import json

from conductor.core import messages
from conductor import Conductor, persistence, render, settings
from conductor.core import language
from conductor.rendering.render import last_line
from tests.harness import cli, stepped, support, titled

run = support(__file__, "run")

WORKS = "---\nname: WORKS\nkind: proc\ndescription: a witness\nproc: |\n  WORK\n  WORK\n---\nwork\n"
PICKER = ("---\nname: PICKER\nkind: proc\ndescription: a witness\noutput: json\nproc: |\n"
          "  INFER\n  PICK verdict\n---\nelect\n")
AT_FLOOR = f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {settings.PRINCIPAL_CAP}\n---\n"
LINE = "long line of matter\n"
SAID, LAST = f"=> {language.TERMINAL}  (", f"=> {language.RESPONSE}  ("   # a step said by its print, the last message

LAPPED = run.PROVER.replace("constraints.production", "tools: |\n  LAPS\nconstraints.production")
LAPS = ("---\nname: LAPS\nkind: proc\ndescription: a described door\noutput: any\nfield: |\n  two names\n"
        "constraints.production: |\n  LP1  the lap names its element\nproc: |\n  INFER\n  PROVE\n---\nlap\n")
REPLAY_CAP = 300          # the host's cap of case (e): under the size of a lap's REPAIR
TICK = ("#!/usr/bin/env python3\nfrom pathlib import Path\nmark = Path(__file__).with_name('ticks')\n"
        "count = int(mark.read_text()) + 1 if mark.exists() else 1\nmark.write_text(str(count))\n"
        "print(f'tick {count}')\n")   # a provider whose rendering changes at every run: a replay reads it anew
TICKER = {"TICKS": ("ticker", "pp-ticker", TICK)}
SAYT = ("---\nname: SAYT\nkind: proc\ndescription: says a line beside the ticker's rendering\npayloads: ticker\n"
        "proc: |\n  INFER\n---\nsay\n")
ROOTT = ("---\nname: ROOTT\nkind: proc\ndescription: proves its callee's line\nconstraints.production: |\n"
         "  Z1  say it plainly\nproc: |\n  CALL SAYT.md\n  PROVE\n---\nprove the callee\n")
MISSED_Z1 = '[{"code": "Z1", "evidence": "off", "verdict": "fail"}]'
FAILED = ('[{"code": "LP1", "evidence": "off", "verdict": "fail"}, '
          '{"code": "Z1", "evidence": "said plainly", "verdict": "ok"}]')   # a lap's proof that misses LP1
FUSED = "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\ninstructions_fusion: max\n---\n"
            # the fused stretch: a lap's line and its proof in ONE output, as the template plays it


def _long(chars: int) -> str:
    return "---\nname: LONG\nkind: doc\n---\n\n" + LINE * (chars // len(LINE)) + "\n"


def _settings(cap: int) -> str:
    return f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\n---\n"


def _waiting(env, key: str) -> str:
    return persistence.pending_of(persistence.slot_of(env.made, key)).get("matter", "") if key else ""


def _cap_house(bench, name: str, cap: int, chars: int):
    env = bench.env(name)
    env.write("SETTINGS.md", _settings(cap))
    env.write("LONG.md", _long(chars))
    env.write("procs/LONGRUN.md", run.LONGRUN)
    return env


def _inline_house(bench, name: str, laps: str, cap: int):
    env = bench.env(name)
    env.write("procs/PROVER.md", LAPPED)
    env.write("procs/LAPS.md", laps)
    env.write("SETTINGS.md", FUSED.format(cap=cap))
    return env


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    said = {act: messages.held(act) for act in messages.ACKNOWLEDGED}

    # === the mode =================================================================================

    # one run, the only one of its house: (h) hooks it
    marked = bench.env("mode-run")
    run.opened(marked)

    # --- (a) one mode: a `-new` without any variable opens a run its principal conducts ------------
    bare = bench.env("mode-bare")
    plain_key, plain = run.opened(bare)
    agents = cli(bare.engine, plain_key, cwd=bare.root, env=run.agent(plain_key)) if plain_key else None
    if (plain.returncode == 0 and plain_key and not run.closing(plain.stdout).count(f"./pp {plain_key}")
            and agents is not None and agents.returncode == 2 and "principal-advances" in agents.stderr):
        held("(a) one mode", f"run {plain_key}: `-new` without any variable -- the opening carries no call, "
             "the agent's bare call refuses `principal-advances`")
    else:
        failures.append(f"  ✗ (a) one mode                 rc={plain.returncode} key={plain_key!r} "
                        f"closing={run.closing(plain.stdout)!r} "
                        f"agent={agents.returncode if agents else None} {agents.stderr[-200:] if agents else ''!r}")

    # --- (c) the endings ----------------------------------------------------------------------------
    ends = bench.env("mode-ends")
    works, prover, picker = (ends.write(f"{name}.md", text)
                             for name, text in (("WORKS", WORKS), ("PROVER", run.PROVER), ("PICKER", PICKER)))

    def opened_on(env, path):
        env.conductor().forget()
        conductor = env.conductor()
        block = conductor.start(path)
        return conductor.run_id, block

    started, working = opened_on(ends, works)
    ends.conductor(started).printed("WORKS", "said")   # the first WORK said: the second pending
    _, finishing = ends.conductor(started).printed("WORKS", "said")   # its print ends the passage
    run_v, proving = opened_on(ends, prover)
    if proving.output != "proof":
        _, proving = ends.conductor(run_v).printed("PROVER", "said")   # the WORK said, the proof due
    counted = (proving.total, persistence.awaits_of(run.slot(ends, run_v)))   # read while the run stands
    run_p, inferring = opened_on(ends, picker)
    picking = ends.conductor(run_p).submit('["a", "b"]')
    texts = {name: render(one) for name, one in (("work", working), ("final", finishing),
                                                  ("prove", proving), ("infer", inferring),
                                                  ("pick", picking))}
    tails = {name: run.closing(text) for name, text in texts.items()}
    # an output a run's principal hands closes on a line where the passage is over, and nowhere else:
    # a value's call is named by the channel of its step, never by a foot; the end of the passage
    # says `AWAIT` alone -- the launcher carries the next message, no call stands under it
    closed = [name for name in texts if name != "final" and tails[name]]
    over = (finishing is not None and finishing.wait and finishing.label == language.AWAIT and not finishing.next_call
            and tails["final"].splitlines() == [f"{messages.SIGNAL} {language.AWAIT}"])
    handed = {"prove": (proving, language.TOOL_HEREDOC), "infer": (inferring, language.TOOL_HEREDOC),
              "pick": (picking, language.TOOL)}
    off = [name for name, (one, channel) in handed.items()
           if one.channel != channel or one.label or one.next_call]
    if not closed and over and not off:
        held("(c) a value's call is its step's channel, a passage over closes on AWAIT",
             "the FREE step, the proof, the choice and the production pp takes close on no line; the proof "
             "and the list name the heredoc channel, the choice the call's; the end of the passage closes "
             "on `AWAIT` with no call under it")
    else:
        failures.append(f"  ✗ (c) the endings              closed={closed} over={over} off={off} "
                        f"{tails['work']!r} {tails['final']!r} {tails['prove']!r}")

    # --- (c2) the last message ----------------------------------------------------------------------
    added = {"prove": (proving, "PROVER"), "infer": (inferring, "PICKER"), "pick": (picking, "PICKER")}
    lined = [name for name, (one, document) in added.items()
             if one.response or texts[name].rstrip().endswith(last_line(document))]
    stepless = [one for one in texts["final"].splitlines() if LAST in one or SAID in one]
    if (working.channel == language.TERMINAL and not working.response and SAID in texts["work"]
            and not any(LAST in text for text in texts.values())
            and not lined and counted == (2, persistence.PRODUCTION)
            and not finishing.response and not stepless):
        held("(c2) no output asks a last message",
             "the pending WORK keeps `=> terminal`, said by its print; behind the proof, the choice and the "
             "production pp takes no line of the form `empty` is added -- PROVER still counts 2 steps and "
             "awaits its value; no output carries `=> response`; the end of the passage renders no step")
    else:
        failures.append(f"  ✗ (c2) the last message        work={working.channel!r}/{working.response!r} "
                        f"lined={lined} counted={counted} final={finishing.response!r}/{stepless}")

    # --- (d) the chunks ----------------------------------------------------------------------------
    long = bench.env("mode-chunks")
    long.write("SETTINGS.md", AT_FLOOR)   # the cap: the floor itself
    long.write("LONG.md", run.PAST)
    longrun = long.write("LONGRUN.md", run.LONGRUN)

    def read_whole():
        # the host carries the standing orders (`PP_MARBLE`): the block is the reading alone
        long.conductor().forget()
        conductor = long.conductor()
        block = run.under({"PP_MARBLE": "1"}, lambda: conductor.start(longrun))
        run_key = conductor.run_id
        chunks = [long.conductor(run_key).rendered(block)]
        while long.conductor(run_key).pending() and len(chunks) < 100:
            chunks.append(long.conductor(run_key).next_chunk())
        return chunks

    whole_read = read_whole()
    middles = whole_read[:-1]
    if (len(whole_read) > 1
            and all(run.closing(one).startswith(f"{messages.closing(language.MORE)}\n{messages.fact(messages.READING)[:-1]}") and "./pp" not in run.closing(one)
                    and not one.split("\n▶ ")[0].rstrip().endswith(last_line("LONGRUN"))
                    and titled(language.INSTRUCTION) not in one
                    for one in middles)
            and not run.closing(whole_read[-1])):
        held("(d) the chunks, MORE at the prompt",
             f"{len(whole_read)} chunks; the {len(middles)} intermediate chunks add no line above their MORE "
             "and the fact, no call; the last carries the foot of its form")
    else:
        failures.append(f"  ✗ (d) the chunks               chunks={len(whole_read)} "
                        f"{middles[-1][-260:] if middles else ''!r}")

    # --- (e) the recovery texts --------------------------------------------------------------------
    catch_run, _ = opened_on(ends, works)
    caught = render(ends.conductor(catch_run).submit("a draft handed to the tool"))
    strayed = [str(one.get("instruction")).strip() for one in run.trace(ends, catch_run)
               if one.get("kind") == "stray"]          # read before the next opening forgets the run
    long.conductor().forget()
    viewer = long.conductor()
    viewed_block = viewer.start(longrun)
    view = long.conductor(viewer.run_id).shown(viewed_block)
    view_slot = persistence.slot_of(long.made, viewer.run_id)
    kept_view = persistence.viewing_of(view_slot).get("matter") or persistence.pending_of(view_slot).get("matter")
    bounce_key, _ = run.opened(long, "LONGRUN.md")          # a reading past the floor
    bounce_kinds = run.kinds(long, bounce_key)
    bounced = (cli(long.engine, bounce_key, "a value", cwd=long.root, env=run.agent(bounce_key))
               if bounce_key else None)
    if (not run.closing(caught) and strayed == ["WORK"]
            and len(view) <= settings.PRINCIPAL_CAP < len(run.PAST) and not kept_view
            and bounced is not None and bounced.returncode == 0 and "chunk-pending" in bounced.stdout
            and "▌" not in bounced.stdout and run.kinds(long, bounce_key) == bounce_kinds):
        held("(e) no recovery text says to call pp",
             "the soft catch closes on no line, `stray` traced once with the WORK; the view comes cut "
             f"({len(view)} characters of a {len(run.PAST)}-character reading), nothing kept; the value "
             "over a waiting reading bounces chunk-pending, nothing traced")
    else:
        failures.append(f"  ✗ (e) the recovery texts       caught={run.closing(caught)!r} "
                        f"strayed={strayed} "
                        f"view={len(view)} kept={bool(kept_view)} "
                        f"bounce_kinds={bounce_kinds}->{run.kinds(long, bounce_key)} "
                        f"bounced={bounced is not None and bounced.stdout[-200:]!r}")

    # --- (h) -hook serves the pending block ------------------------------------------------------------
    hooked = cli(marked.engine, "-hook", cwd=marked.root)
    if hooked.returncode == 0 and titled(language.INSTRUCTION) in hooked.stdout and not run.closing(hooked.stdout):
        held("(h) -hook serves the principal's block", "the pending block rendered, no closing line")
    else:
        failures.append(f"  ✗ (h) the hook                 rc={hooked.returncode} {hooked.stdout[-200:]!r}")

    # === the floor of the cap =====================================================================

    # --- (a) the floor -----------------------------------------------------------------------------------
    low = _cap_house(bench, "cap-low", 20000, 60000)
    key_a, out_a = run.opened(low, "LONGRUN.md")
    waiting_a = _waiting(low, key_a)
    if (out_a.returncode == 0 and key_a and not waiting_a
            and out_a.stdout.count(LINE.strip()) >= 2900 and len(out_a.stdout) > 20000):
        held("(a) the floor", f"run {key_a} at 20000: the opening serves "
             f"{len(out_a.stdout)} characters in one output, nothing waits")
    else:
        failures.append(f"  ✗ (a) the floor               rc={out_a.returncode} key={key_a!r} "
                        f"waiting={len(waiting_a)} chars={len(out_a.stdout)} {out_a.stderr[-200:]!r}")

    # --- (c) a setting above the floor holds -------------------------------------------------------------
    high = _cap_house(bench, "cap-high", 300000, 250000)
    key_c, out_c = run.opened(high, "LONGRUN.md")
    waiting_c = _waiting(high, key_c)
    if out_c.returncode == 0 and key_c and not waiting_c and len(out_c.stdout) > 250000:
        held("(c) a setting above the floor holds", f"at 300000 the reading comes whole: "
             f"{len(out_c.stdout)} characters")
    else:
        failures.append(f"  ✗ (c) above the floor         {len(out_c.stdout)}/{len(waiting_c)}")

    # --- (d) the one rule ----------------------------------------------------------------------------------
    floor = settings.PRINCIPAL_CAP
    ruled = {(20000, True): floor, (20000, False): 20000, (300000, True): 300000, (300000, False): 300000,
             (0, True): 0, (0, False): 0}
    got = {pair: settings.served_cap(*pair) for pair in ruled}
    if floor == 200000 and got == ruled:
        held("(d) served_cap is the one rule", f"floor {floor}: raised at the prompt alone, a higher setting "
             "kept, 0 cuts nothing on either channel")
    else:
        failures.append(f"  ✗ (d) served_cap              floor={floor} {got}")

    # === the answer in the call's result ============================================================

    # --- (a) the door, the field, the laps: each block never served, held -------------------------------------
    one = _inline_house(bench, "mode-inline", LAPS, 60000)
    def handed(env, run_key: str, document: str):
        """The agent's print of the step `document` said on `terminal`."""
        return cli(env.engine, run_key, "-print", document, "-", cwd=env.root, stdin="said\n", env=run.agent(run_key))

    def agent(env, run_key: str, *words, stdin=None):
        return cli(env.engine, run_key, *words, cwd=env.root, stdin=stdin, env=run.agent(run_key))

    def serve(env, run_key: str):
        """The principal's bare call: it serves the output held."""
        return cli(env.engine, run_key, cwd=env.root)

    key, _ = run.opened(one, "PROVER.md")
    handed(one, key, "PROVER")                          # the door's WORK, said before its proof
    acks = [agent(one, key, "-s", "LAPS")]
    door = serve(one, key)
    acks.append(agent(one, key, "-", stdin='["a", "b"]'))
    fielded = serve(one, key)
    handed(one, key, "LAPS")                            # the first lap's line, before its proof
    acks.append(agent(one, key, "-", stdin=run.proof_of(fielded.stdout)))
    lap_one = serve(one, key)
    holds = [e.get("act") for e in run.trace(one, key) if e.get("kind") == "held"]
    if (key and [out.stdout.strip() for out in acks] == [said["door"], said["value"], said["value"]]
            and door.returncode == 0 and "▌" in door.stdout and "INFER field" in door.stdout
            and f"=> {language.TOOL_HEREDOC}" in door.stdout and not run.closing(door.stdout)
            and not any(LAST in out for out in (door.stdout, fielded.stdout, lap_one.stdout))
            and f"INFER any {SAID}" in fielded.stdout
            and fielded.returncode == 0 and "LP1] on all produced" in fielded.stdout
            and f"=> {language.TOOL_HEREDOC}" in fielded.stdout
            and lap_one.returncode == 0 and "LP1] on all produced" in lap_one.stdout
            and "inline" not in run.kinds(one, key) and holds[-3:] == ["door", "value", "value"]
            and not run.slot(one, key).get("held")):
        held("(a) the door, the field and the laps are held", f"run {key}: `-s LAPS`, the field and the first lap's "
             "proof each answered by the held line; the principal's bare calls serve the field block (its line "
             "naming the heredoc channel, no closing), the first lap (its said line on `terminal`, with its "
             "proof's line), the second; no served block asks a last message; traced held door, value, value, "
             "never inline")
    else:
        failures.append(f"  ✗ (a) held laps                key={key!r} acks={[out.stdout.strip() for out in acks]} "
                        f"holds={holds} inline={'inline' in run.kinds(one, key)} door={door.stdout[-200:]!r} "
                        f"fielded={fielded.stdout[-200:]!r} held={bool(run.slot(one, key).get('held'))}")

    # --- (b) the last proof's answer moves the run on: held --------------------------------------------------
    handed(one, key, "LAPS")                            # the second lap's line
    agent(one, key, "-", stdin=run.proof_of(lap_one.stdout))
    lap_two = serve(one, key)                          # PROVER's checkpoint, held then served
    checkpoint = agent(one, key, "-", stdin=run.proof_of(lap_two.stdout))
    slot_held = run.slot(one, key).get("held") or {}
    # the agent's calls over the held output: a view plays (it moves nothing), the bare call refuses
    viewed = cli(one.engine, key, "-peek", cwd=one.root, env=run.agent(key))
    bare = cli(one.engine, key, cwd=one.root, env=run.agent(key))
    if (lap_two.returncode == 0 and "INFER proof [Z1]" in lap_two.stdout
            and checkpoint.returncode == 0 and checkpoint.stdout.strip() == said["value"]
            and slot_held.get("act") == "value"
            and any(f"WORK any {SAID}" in line for _, _, lines in slot_held.get("steps", []) for line in lines)
            and "▶" not in slot_held.get("tail", "")
            and viewed.returncode == 0 and "▌" in viewed.stdout and f"WORK any {SAID}" in viewed.stdout
            and (run.slot(one, key).get("held") or {}).get("act") == "value"
            and bare.returncode == 2 and "principal-advances" in bare.stderr):
        held("(b) a block that moves the run on stays held", "the second lap's proof holds PROVER's checkpoint, "
             "served by the principal; its proof answers one line, the TURN's WORK (a FREE step on `terminal`, no "
             "closing line) held at the slot, its line in the group of its step; the agent's -peek renders that "
             "block, the hold intact, and its bare call refuses principal-advances")
    else:
        failures.append(f"  ✗ (b) the held output         rc={lap_two.returncode}/{checkpoint.returncode} "
                        f"{lap_two.stdout[-160:]!r} {checkpoint.stdout!r} held={slot_held.get('act')!r} "
                        f"steps={slot_held.get('steps')!r} tail={slot_held.get('tail', '')!r} viewed={viewed.stdout[:80]!r} bare={bare.stderr!r}")

    # --- (c) the principal's bare calls serve the WORK, then the end of the passage ---------------------------------------
    served = cli(one.engine, key, cwd=one.root)
    handed(one, key, "TURN")                            # the agent's print of the WORK ends the passage
    final = cli(one.engine, key, cwd=one.root)
    ended = run.closing(final.stdout).splitlines()
    if (served.returncode == 0 and f"WORK any {SAID}" in served.stdout and not run.slot(one, key).get("held")
            and not run.closing(served.stdout)
            and final.returncode == 0 and ended[:1] == [f"{messages.SIGNAL} {language.AWAIT}"]
            and not any(line.startswith("./pp") for line in ended)
            and (persistence.awaits_of(run.slot(one, key)) == persistence.MESSAGE)):
        held("(c) the principal's bare calls serve", "the principal's bare call renders the held WORK on no "
             "closing line; once the agent printed it, the principal's next the end of the passage closed on `AWAIT` "
             "with no call, the run parked")
    else:
        failures.append(f"  ✗ (c) bare calls               rc={served.returncode}/{final.returncode} "
                        f"{served.stdout[-120:]!r} {final.stdout[-120:]!r}")

    # --- (e) a host cap: a replay comes inline, cut, the rest by the agent's bare calls -------------------
    three = _inline_house(bench, "mode-inline-cap", LAPS, REPLAY_CAP)
    key3, _ = run.opened(three, "PROVER.md")
    handed(three, key3, "PROVER")
    agent(three, key3, "-s", "LAPS")
    serve(three, key3)                                 # the field block
    agent(three, key3, "-", stdin='["a", "b"]')
    lapped = serve(three, key3)                        # the first lap and its proof's line, served whole
    handed(three, key3, "LAPS")
    first = agent(three, key3, "-", stdin=FAILED)       # the lap's proof fails: its REPAIR, already read, comes inline
    chunks, rests = [first.stdout], []
    for _ in range(8):
        rests.append(bool(persistence.viewing_of(persistence.slot_of(three.made, key3))))   # its matter, its steps
        if not rests[-1]:
            break
        chunks.append(cli(three.engine, key3, cwd=three.root, env=run.agent(key3)).stdout)
    inline3 = [e.get("act") for e in run.trace(three, key3) if e.get("kind") == "inline"]
    if (key3 and len(lapped.stdout) > REPLAY_CAP and first.returncode == 0 and "REPAIR" in first.stdout
            and len(chunks) > 1 and all(len(c) <= REPLAY_CAP for c in chunks)
            and rests == [True] * (len(chunks) - 1) + [False] and "LP1] on all produced" in chunks[-1]
            and inline3 == ["value"] and not run.slot(three, key3).get("held")):
        held("(e) a replay past the cap comes inline, cut", f"run {key3}: the lap held, then served whole by the "
             f"principal; its failed proof's REPAIR answers the agent's call in {len(chunks)} chunks under {REPLAY_CAP}, "
             "the last carrying the proof's line, nothing held, traced inline once")
    else:
        failures.append(f"  ✗ (e) the cap                  key={key3!r} rc={first.returncode} chunks={len(chunks)} "
                        f"sizes={[len(c) for c in chunks]} rests={rests} "
                        f"inline={inline3} {chunks[-1][-300:]!r}")

    # --- (e2) a replay that renders a payload anew carries a reading never served: held ----------------------
    four = _inline_house(bench, "mode-replay-fresh", LAPS, 60000)
    run.pin_package(four.made, "ticker", TICKER)
    four.write("procs/SAYT.md", SAYT)
    four.write("procs/ROOTT.md", ROOTT)
    key4, opened4 = run.opened(four, "ROOTT.md")          # SAYT's line and ROOTT's proof in one output: tick 1
    handed(four, key4, "SAYT")
    before4 = run.kinds(four, key4)
    missed4 = agent(four, key4, "-", stdin=MISSED_Z1)     # the REPAIR re-enters SAYT: its provider renders tick 2
    new4 = run.kinds(four, key4)[len(before4):]
    hold4 = run.slot(four, key4).get("held") or {}
    served4 = serve(four, key4)
    if (key4 and "tick 1" in opened4.stdout and missed4.returncode == 0 and missed4.stdout.strip() == said["value"]
            and "repair" in new4 and "provider" in new4 and "inline" not in new4 and hold4.get("act") == "value"
            and served4.returncode == 0 and "tick 2" in served4.stdout and "REPAIR" in served4.stdout):
        held("(e2) a replay with a reading never served is held", f"run {key4}: the proof missed, the REPAIR re-enters "
             "SAYT and its provider renders anew (tick 2): one line back, nothing inline; the principal's call "
             "serves the REPAIR with the new rendering")
    else:
        failures.append(f"  ✗ (e2) a fresh replay          key={key4!r} rc={missed4.returncode} {missed4.stdout[:240]!r} "
                        f"trace={new4} act={hold4.get('act')!r} {opened4.stderr[-200:]!r}")

    # --- (f) -stats counts the inline outputs and the held ones ------------------------------------------
    outputs, hops = [chunks[-1]], 0                     # the exchange to its end: the house's calls, the agent's values
    while key3 and hops < 12 and not (persistence.awaits_of(run.slot(three, key3)) == persistence.MESSAGE
                                      and not run.slot(three, key3).get("held")):
        due = three.conductor(key3).prints_due()
        if due:
            for document in due:
                handed(three, key3, document)
        elif run.CODES.search(outputs[-1]):
            agent(three, key3, "-", stdin=run.proof_of(outputs[-1]))
        if run.slot(three, key3).get("held"):
            outputs.append(serve(three, key3).stdout)
        hops += 1
    counted = cli(three.engine, "-stats", key3, "-json", cwd=three.root)
    spoken = cli(three.engine, "-stats", key3, cwd=three.root)
    try:
        period = json.loads(counted.stdout).get("period") or {}
    except ValueError:
        period = {}
    parked3 = persistence.awaits_of(run.slot(three, key3)) == persistence.MESSAGE
    if parked3 and period.get("inline") == 1 and period.get("held", 0) >= 3 and "1.0 inline" in spoken.stdout:
        held("(f) -stats counts the inline outputs", f"the exchange parked after {hops} call(s): 1 inline (the "
             f"REPAIR), {period.get('held')} held on the run; the period's line says `1.0 inline`")
    else:
        failures.append(f"  ✗ (f) stats                    parked={parked3} hops={hops} inline={period.get('inline')!r} "
                        f"held={period.get('held')!r} "
                        f"{spoken.stdout.splitlines()[-1:]!r}")
    return 0
