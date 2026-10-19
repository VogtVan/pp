"""Scenario `principal-hold` -- in a run its principal conducts, the conduction leaves by the
principal's call alone. The console tells the callers apart by the mark
`PP_CONDUCTED_BY_PRINCIPAL=true` on the keyed call: a marked call is the principal's, any other the
agent's. The agent's value is judged when it is given, by the one judge of both modes; a block the
engine renders on the agent's call and that MOVES the run or its view leaves through one seam and
is HELD at the run until the principal's bare call serves it -- the agent's tool return carries
what the act answers and one neutral line. A script's own text and a refusal are answers: they
reach the caller in both modes, and so does what only SHOWS (a peek, a bare script's manual, a
denied offer, a switch), cut under the host's cap, the rest on the agent's bare keyed call. One
output is held at a time.

The value and the principal's call:
- (a) the agent's bare call refuses `principal-advances`: exit 2, no block, the slot the same
- (b) the agent's value is judged at once and its output held: one neutral line, rc 0; the trace
  says `answer` then `held`; the frames moved; the slot carries `held`, its act `value`
- (d) the principal's bare call serves the held output -- the block after the proof -- and the slot
  forgets it; traced `advance` with `held: true`
- (e) a faulty proof: the REPAIR is held, then served by the principal's call
- (f) no value given where one is due: the principal's bare call plays the empty-answer repair
- (g) the frontier: the principal's call carries the message, traced `prompt`, and the next
  exchange opens
- (h) a marked call carrying a text over a held output refuses `output-held`
- (i) a chunk waiting (a reading past the floor of the principal's cap): the agent's bare call
  refuses, its value bounces `chunk-pending`, the principal's bare call serves the chunk
- (j) an unmarked `-new` under a launcher that names the principal's run standing mid-exchange
  (`PP_CONDUCTED_RUN=<key>`) opens nothing; unnamed, or naming another run, it opens even while
  that run stands; once that run is parked on its FINAL, the named `-new` opens a run
- (k) a whole exchange conducted by a launcher witness: `-new` marked, each output served to an
  agent witness that pipes its proof unmarked, the launcher's bare call serving the rest, the run
  parked on its FINAL -- no served output that moves the run carries `./pp <key>` under CONTINUE or
  FINAL (a closing that asks a value keeps its command)
- (l) the same proof at the same step on two runs: the LLM mode's tool return and the principal
  mode's served output are the same matter, their closings apart
- (m) the LLM's mode is today's: an unmarked value is judged and its block returned, a bare call
  advances; a mount, a script's view and a peek come back in the tool return; nothing held
- (n) the last FREE step of an output stays PENDING for the principal's call: the marked boot closes
  on the TURN's WORK, the agent's `-peek` renders TURN{2/4}, a `-s` played there stacks on it; the
  principal's bare call resolves the WORK and crosses the `§` of the document attached at turn.end
  in the same call; in the LLM's mode the WORK is batched

The acts held or answered:
- (a) `-mount`: one neutral line, no block; the mount written and the hold at the slot (`act:
  mount`); the principal's bare call serves the view
- (b) a script's `::mount`: the script's text in the tool return, the view held
- (c) a script called bare: its manual ANSWERS the call -- the block in the tool return, the mount
  written at the slot, nothing held, nothing pending
- (g) `-peek`: the block in the tool return, nothing held
- (h) an offer not at this step: exit 2, the block and its DEVIATION in the tool return, nothing held
- (f) `-disable`: the fact AND the block in the tool return, the package out of the play, nothing held
- (i) while an output is held, a mount, a re-serve, a peek, a switch, a `-s` and a value bounce on
  the console's held line: nothing played, nothing traced, the slot byte-identical
- (e) `-compacted`: the re-serve held (`act: compacted`)
- (d) a routed door: its frame pushed, its block held (`act: door`), nothing inline
- (m) a manual over the host's cap: the first chunk in the tool return, the rest served by the
  agent's bare keyed calls, the concatenation the body to the byte; after the last, the bare call
  refuses `principal-advances`
- (l) one seam: no line of the console prints `.rendered(` or `.shown(` itself
"""
from __future__ import annotations

from conductor import Conductor, persistence
from tests.harness import cli, support

run = support(__file__, "run")

OFFERS = run.PROVER.replace("PROVER", "OFFERS").replace(
    "constraints.production", "tools: |\n  pp-probe\n  SIDE\nconstraints.production")
SIDE = "---\nname: SIDE\nkind: proc\ndescription: a side door\nproc: |\n  WORK\n---\nthe side door's brief\n"
EXT = "---\nname: EXT\nkind: doc\n---\n\nthe mounted matter\n"
CONTRACT = "---\nname: pp-probe\ndescription: a witness script that mounts\n---\n\nthe probe's manual\n"
PROBE = ("def main(argv):\n"
         "    print('::mount [{\"doc\": \"EXT.md\", \"body\": true}]')\n"
         "    print('probe: chain derived')\n"
         "    return 0\n")
MOUNT = '[{"doc": "EXT.md", "body": true}]'
TALL_CAP = 20000
TALL = f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {TALL_CAP}\n---\n"
OFFERING = "---\nname: TURN\ntools: |\n  +PROVER\n---\n"      # the base's TURN offers the door to its WORK
FUSED = "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 60000\ninstructions_fusion: max\n---\n"
            # the fused stretch the template plays: the WORK is BATCHED, not asked -- what (n) proves
LATE = ("---\nname: LATE\nkind: proc\ndescription: a late word\nattach: turn.end\nproc: |\n  §\n  INFER\n"
        "---\n\nSay late.\n")                                 # opens on a section break, as THREADS does


def _house(bench, name: str, packages=()):
    """-> an environment carrying both doors (PROVER, OFFERS), the side door, the matter a mount
    reads and the probe script."""
    env = bench.env(name, packages)
    env.write("procs/PROVER.md", run.PROVER)
    env.write("procs/OFFERS.md", OFFERS)
    env.write("procs/SIDE.md", SIDE)
    env.write("EXT.md", EXT)
    env.write("skills/pp-probe/SKILL.md", CONTRACT)
    env.write("skills/pp-probe/pp-probe.py", PROBE)
    return env


def _pointer(env, key: str) -> list:
    """-> the done flags of every frame's instructions: where the run stands."""
    return [[one.get("done") for one in frame.get("instructions", [])]
            for frame in run.slot(env, key).get("frames", [])]


def _held(env, key: str) -> dict:
    return run.slot(env, key).get("held") or {}


def _agent(env, key: str, *words, stdin: str | None = None):
    return cli(env.engine, key, *words, cwd=env.root, stdin=stdin)


def _principal(env, key: str, *words):
    return cli(env.engine, key, *words, cwd=env.root, env=run.MARK)


def _one_line(out) -> bool:
    return "▌" not in out.stdout and out.stdout.strip().count("\n") <= 1


def _bytes(env, key: str) -> bytes:
    return persistence.slot_of(env.made, key).read_bytes()


def _heading(text: str) -> str:
    return next((one for one in reversed(text.splitlines()) if one.startswith("▌ ") and "▸" in one), "")


def scenario(bench) -> int:
    import pp                                                                  # noqa: PLC0415
    held, failures = bench.held, bench.failures
    said = {act: "pp: " + line for act, line in Conductor.HELD_SAID.items()}
    # one house for every act on a short door: each case opens its own run beside the others
    house = _house(bench, "hold-acts", ("wit",))

    # === the value and the principal's call =======================================================

    # --- (a) the agent's bare call refuses ------------------------------------------------------------
    key, opened = run.opened(house, True, "PROVER.md")
    asked = _principal(house, key)                         # the door's WORK closed: the proof asked
    before = _bytes(house, key)
    bare = _agent(house, key)
    if (opened.returncode == 0 and key and "proof" in asked.stdout and bare.returncode == 2
            and "principal-advances" in bare.stderr and "▌" not in bare.stdout and _bytes(house, key) == before):
        held("(a) the agent's bare call refuses", f"run {key}: `./pp {key}` without the mark -- "
             "principal-advances, exit 2, no block, the slot byte-identical")
    else:
        failures.append(f"  ✗ (a) the bare call             rc={bare.returncode} {bare.stderr[-200:]!r} "
                        f"asked={'proof' in asked.stdout} {opened.stderr[-200:]!r}")

    # --- (b) the agent's value: judged at once, its output held ----------------------------------------
    pointer_before, kinds_before = _pointer(house, key), run.kinds(house, key)
    valued = _agent(house, key, "-", stdin=run.GOOD)
    new_kinds = run.kinds(house, key)[len(kinds_before):]
    slot_held = _held(house, key)
    if (valued.returncode == 0 and valued.stdout.strip() == said["value"] and "▌" not in valued.stdout
            and new_kinds[:1] == ["answer"] and "held" in new_kinds and "block" in new_kinds
            and _pointer(house, key) != pointer_before
            and slot_held.get("matter") and slot_held.get("chars", 0) > 0 and slot_held.get("act") == "value"):
        held("(b) the value is judged at once, its output held", f"one line back ({valued.stdout.strip()!r}); "
             f"trace {new_kinds}; the frames moved; `held` at the slot, {slot_held.get('chars')} chars")
    else:
        failures.append(f"  ✗ (b) the held output           rc={valued.returncode} {valued.stdout[-200:]!r} "
                        f"kinds={new_kinds} moved={_pointer(house, key) != pointer_before} held={bool(slot_held)}")

    # --- (d) the principal's bare call serves the held output ------------------------------------------
    served = _principal(house, key)
    advances = [e for e in run.trace(house, key) if e.get("kind") == "advance"]
    if (served.returncode == 0 and "▌" in served.stdout and f"run {key}" in served.stdout
            and "held" not in run.slot(house, key) and advances and advances[-1].get("held") is True):
        held("(d) the principal's call serves the held output", "the block after the proof rendered, "
             "`held` gone from the slot, traced `advance` held: true")
    else:
        failures.append(f"  ✗ (d) the release               rc={served.returncode} {served.stdout[:200]!r} "
                        f"held={'held' in run.slot(house, key)} advances={advances[-1:]}")

    # --- (e) a faulty proof: the REPAIR held, then served ------------------------------------------------
    key2, _ = run.opened(house, True, "PROVER.md")
    _principal(house, key2)
    faulty = _agent(house, key2, "-", stdin="[]")
    repaired = _principal(house, key2)
    kinds2 = run.kinds(house, key2)
    if (faulty.returncode == 0 and faulty.stdout.strip() == said["value"] and "repair" in kinds2
            and repaired.returncode == 0 and "REPAIR" in repaired.stdout and "DEVIATION" in repaired.stdout):
        held("(e) a faulty proof: the REPAIR is held, then served", "`[]` on Z1: the trace says repair, the "
             "agent gets its one line, the principal's call renders the REPAIR block")
    else:
        failures.append(f"  ✗ (e) the held repair           rc={faulty.returncode}/{repaired.returncode} "
                        f"kinds={kinds2[-4:]} {repaired.stdout[-200:]!r}")

    # --- (f) no value where one is due: the empty-answer repair at the principal's call -------------------
    key3, _ = run.opened(house, True, "PROVER.md")
    _principal(house, key3)
    empty = _principal(house, key3)
    if empty.returncode == 0 and "REPAIR" in empty.stdout and "repair" in run.kinds(house, key3):
        held("(f) no value given: today's empty-answer repair", "the principal's bare call on a due proof "
             "renders the REPAIR, as a bare call does in the LLM's mode")
    else:
        failures.append(f"  ✗ (f) the empty answer          rc={empty.returncode} {empty.stdout[-200:]!r}")

    # --- (g) the frontier: the principal's call carries the message ---------------------------------------
    parked, hops = served, 0
    while "FINAL" not in run.closing(parked.stdout) and hops < 6:     # the door closed: the turn to its FINAL
        parked = _principal(house, key)
        hops += 1
    frontier = persistence.frontier_of(run.slot(house, key))
    spoken = _principal(house, key, "the principal's next word")
    prompts = [e for e in run.trace(house, key) if e.get("kind") == "prompt"]
    if (frontier and spoken.returncode == 0 and "▌" in spoken.stdout
            and prompts and prompts[-1].get("text") == "the principal's next word"):
        held("(g) the frontier: the message rides the principal's call", f"parked after {hops} hop(s), "
             "the marked call with a text traced `prompt`, the next exchange opened")
    else:
        failures.append(f"  ✗ (g) the frontier              frontier={frontier} rc={spoken.returncode} "
                        f"prompts={prompts[-1:]} {spoken.stdout[-160:]!r}")

    # --- (h) a marked call with a text over a held output refuses -----------------------------------------
    key4, _ = run.opened(house, True, "PROVER.md")
    _principal(house, key4)
    _agent(house, key4, "-", stdin=run.GOOD)
    over = _principal(house, key4, "some text")
    if over.returncode == 2 and "output-held" in over.stderr and _held(house, key4):
        held("(h) a text over a held output refuses", "output-held, exit 2, the hold intact")
    else:
        failures.append(f"  ✗ (h) output-held               rc={over.returncode} {over.stderr[-160:]!r}")

    # --- (i) a chunk waiting: a reading past the floor of the principal's cap ------------------------------
    # one house for the long readings: the floor cuts whatever the setting, the manual cuts at the host's
    tall = _house(bench, "hold-long")
    tall.write("SETTINGS.md", TALL)
    tall.write("LONG.md", run.PAST)
    tall.write("procs/LONGRUN.md", run.LONGRUN)
    key5, _ = run.opened(tall, True, "LONGRUN.md")
    pending = key5 and persistence.pending_of(persistence.slot_of(tall.made, key5)).get("matter")
    bare5 = _agent(tall, key5) if key5 else None
    valued5 = _agent(tall, key5, "a value") if key5 else None
    chunk = _principal(tall, key5) if key5 else None
    if (pending and bare5.returncode == 2 and "principal-advances" in bare5.stderr
            and valued5.returncode == 0 and "chunk-pending" in valued5.stdout and "▌" not in valued5.stdout
            and chunk.returncode == 0 and "▌" in chunk.stdout):
        held("(i) a chunk waiting", "the agent's bare call refuses, its value bounces chunk-pending, the "
             "principal's bare call serves the chunk")
    else:
        failures.append(f"  ✗ (i) the chunk                 pending={bool(pending)} "
                        f"{bare5 and bare5.returncode}/{valued5 and valued5.returncode}/{chunk and chunk.returncode} "
                        f"{bare5 and bare5.stderr[-120:]!r}")

    # --- (j) the soft -new --------------------------------------------------------------------------------
    key6, _ = run.opened(house, True, "PROVER.md")              # mid-exchange: its WORK stands
    slots_before = len(persistence.slots(house.made))
    named = {run.CONDUCTED_RUN: key6}                            # the launcher names the run it conducts
    soft = cli(house.engine, "-new", cwd=house.root, env=named)
    slots_after_soft = len(persistence.slots(house.made))
    key8, unnamed = run.opened(house)                            # another conversation of the instance
    key9, other = run.opened(house, False, None, {run.CONDUCTED_RUN: "zzzzzz"})
    key7, marked_new = run.opened(house, True)
    # the principal's runs to their FINAL: the principal's bare calls, a proof asked piped by the agent
    for k in (key6, key7):
        hops = 0
        while k and hops < 8 and not persistence.frontier_of(run.slot(house, k)):
            out = _principal(house, k)
            if run.CODES.search(out.stdout) and "heredoc" in out.stdout:
                _agent(house, k, "-", stdin=run.GOOD)
            hops += 1
    parked_all = all(persistence.frontier_of(run.slot(house, k)) for k in (key6, key7) if k)
    opened_after = cli(house.engine, "-new", cwd=house.root, env=named)
    if (soft.returncode == 0 and key6 in soft.stdout and not run.key_of(soft.stdout)
            and "▌" not in soft.stdout and soft.stdout.strip().count("\n") == 0
            and slots_after_soft == slots_before
            and unnamed.returncode == 0 and key8 and other.returncode == 0 and key9
            and marked_new.returncode == 0 and key7 and len({key6, key7, key8, key9}) == 4
            and parked_all and opened_after.returncode == 0 and run.key_of(opened_after.stdout)):
        held("(j) the soft -new", f"`-new` under PP_CONDUCTED_RUN={key6} mid-exchange: one line naming it, no "
             f"block, no slot; unnamed it opened {key8}, naming another run {key9}, marked {key7}; {key6} "
             "parked on its FINAL, the named `-new` opens a run")
    else:
        failures.append(f"  ✗ (j) the soft -new             rc={soft.returncode} {soft.stdout[-160:]!r} "
                        f"slots={slots_after_soft}/{slots_before} unnamed={key8!r} other={key9!r} key7={key7!r} "
                        f"parked={parked_all} after={opened_after.returncode}")

    # --- (k) a whole exchange conducted by the launcher witness -------------------------------------------
    outputs = []
    key10, first = run.opened(house, True, "PROVER.md")
    outputs.append(first.stdout)
    calls = 0
    while key10 and calls < 10 and not persistence.frontier_of(run.slot(house, key10)):
        if run.CODES.search(outputs[-1]) and "heredoc" in outputs[-1]:   # the agent witness pipes the proof
            _agent(house, key10, "-", stdin=run.proof_of(outputs[-1]))
        outputs.append(_principal(house, key10).stdout)
        calls += 1
    # a closing that MOVES the run carries no command; one that asks the tool a value keeps it
    commanded = [i for i, out in enumerate(outputs)
                 if ("CONTINUE" in run.closing(out) or "FINAL" in run.closing(out)) and "./pp" in run.closing(out)
                 and not any(word in run.closing(out) for word in ("stdin", "<your-choice>", "<output>"))]
    proofs = sum(1 for e in run.trace(house, key10) if e.get("kind") == "answer")
    if key10 and persistence.frontier_of(run.slot(house, key10)) and not commanded and proofs >= 1:
        held("(k) a whole exchange by the launcher", f"run {key10}: {len(outputs)} outputs served, {calls} "
             f"principal call(s), {proofs} value(s) piped unmarked, parked on its FINAL; no CONTINUE or "
             "FINAL carries `./pp`")
    else:
        failures.append(f"  ✗ (k) the launcher's exchange   key={key10!r} commanded={commanded} proofs={proofs} "
                        f"calls={calls} {[run.closing(outputs[i]) for i in commanded]!r}")

    # --- (l) the same matter in both modes, the closings apart --------------------------------------------
    key_llm, _ = run.opened(house, False, "PROVER.md")
    _agent(house, key_llm)
    returned = _agent(house, key_llm, "-", stdin=run.GOOD)
    key_led, _ = run.opened(house, True, "PROVER.md")
    _principal(house, key_led)
    _agent(house, key_led, "-", stdin=run.GOOD)
    delivered = _principal(house, key_led)
    by_llm, by_led = (run.matter(returned.stdout, key_llm, house.root),
                      run.matter(delivered.stdout, key_led, house.root))
    if (returned.returncode == 0 and delivered.returncode == 0 and by_llm == by_led
            and "./pp" in run.closing(returned.stdout) and "./pp" not in run.closing(delivered.stdout)
            and "▌" in delivered.stdout):
        held("(l) the same matter in both modes", "the tool return and the served output agree line for line "
             "under the heading; the LLM's closing carries the command, the principal's its note")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(by_llm.splitlines(), by_led.splitlines())) if a != b), None)
        failures.append(f"  ✗ (l) the matter                same={by_llm == by_led} drift={drift} "
                        f"{run.closing(returned.stdout)!r} {run.closing(delivered.stdout)!r}")

    # --- (m) the LLM's mode is today's: the value, the bare call, the views -------------------------------
    advanced = _agent(house, key_llm)
    key_view, _ = run.opened(house, False, "OFFERS.md")
    mounted_llm = _agent(house, key_view, "-mount", MOUNT)
    gesture_llm = _agent(house, key_view, "-s", "pp-probe", "go")
    peek_llm = _agent(house, key_view, "-peek")
    llm_kinds = run.kinds(house, key_llm) + run.kinds(house, key_view)
    if ("▌" in returned.stdout and not _held(house, key_llm) and advanced.returncode == 0
            and "▌" in advanced.stdout and "held" not in llm_kinds and "advance" not in llm_kinds
            and "▌" in mounted_llm.stdout and "▌" in peek_llm.stdout
            and "probe: chain derived" in gesture_llm.stdout and "▌" in gesture_llm.stdout
            and not _held(house, key_view)
            and said["mount"] not in mounted_llm.stdout + gesture_llm.stdout):
        held("(m) the LLM's mode is today's", "the value's block came back in the tool return, the bare call "
             "advanced; the mount, the script's view and the peek come back in the tool return, no neutral "
             "line; nothing held, no `held` nor `advance` on the trace")
    else:
        failures.append(f"  ✗ (m) the LLM's mode            rc={advanced.returncode} kinds={llm_kinds[-6:]} "
                        f"held={bool(_held(house, key_view))} {gesture_llm.stdout[:120]!r}")

    # --- (n) the last FREE step stays pending for the principal's call ------------------------------------
    pend = _house(bench, "hold-pending")
    pend.write("procs/TURN.md", OFFERING)
    pend.write("procs/LATE.md", LATE)
    pend.write("SETTINGS.md", FUSED)
    key_n, booted = run.opened(pend, True, None, None, "hello")
    peeked = _agent(pend, key_n, "-peek")
    door_n = _agent(pend, key_n, "-s", "PROVER")
    frames = run.slot(pend, key_n).get("frames", [])
    work = next((one for one in (frames[-2] if len(frames) > 1 else {}).get("instructions", [])
                 if one.get("keyword") == "WORK"), {})
    key_s, _ = run.opened(pend, True, None, None, "hello")        # no door opened: the principal's call alone
    before_s = run.kinds(pend, key_s).count("block")
    crossed = _principal(pend, key_s)
    kinds_s = run.kinds(pend, key_s)
    key_l, _ = run.opened(pend, False, None, None, "hello")
    work_l = next((one for frame in run.slot(pend, key_l).get("frames", []) for one in frame.get("instructions", [])
                   if one.get("keyword") == "WORK"), {})
    if (key_n and _heading(booted.stdout).endswith("TURN{2/4}") and "WORK any => response" in booted.stdout
            and "LATE" not in booted.stdout
            and peeked.returncode == 0 and _heading(peeked.stdout).endswith("TURN{2/4}")
            and "WORK any => response" in peeked.stdout
            and door_n.returncode == 0 and door_n.stdout.strip() == said["door"]
            and frames and frames[-1].get("document", "").endswith("PROVER.md") and work.get("asked") is True
            and not work.get("done")
            and key_s and crossed.returncode == 0 and "INFER any => response  (LATE)" in crossed.stdout
            and _heading(crossed.stdout).endswith("LATE{1/1}")
            and crossed.stdout.count("▌ pp · run") == 1 and "pending" in kinds_s
            and "▶ CONTINUE" not in crossed.stdout.split("INFER any => response  (LATE)")[0]
            and key_l and work_l.get("done") is True and not work_l.get("asked")
            and "batched" in run.kinds(pend, key_l) and "pending" not in run.kinds(pend, key_l)):
        held("(n) the last FREE step stays pending for the principal", f"run {key_n}: the boot closes on TURN{{2/4}}, "
             "-peek renders it, -s PROVER stacks on the pending WORK; the principal's bare call resolves it and "
             f"renders LATE{{1/1}} in ONE output, no order block before it (traced pending); the LLM's mode "
             "batches the WORK")
    else:
        failures.append(f"  ✗ (n) the pending WORK         boot={_heading(booted.stdout)!r} peek={_heading(peeked.stdout)!r} "
                        f"door={door_n.stdout.strip()!r} frames={[f.get('document', '') for f in frames]} work={work!r} "
                        f"crossed={_heading(crossed.stdout)!r} blocks={before_s}->{kinds_s.count('block')} "
                        f"pending={'pending' in kinds_s} llm={work_l.get('done')}/{work_l.get('asked')} {crossed.stdout!r}")

    # === the acts held or answered ================================================================
    key, _ = run.opened(house, True, "OFFERS.md")

    # --- (a) -mount ---------------------------------------------------------------------------------
    mounted = _agent(house, key, "-mount", MOUNT)
    hold = _held(house, key)
    docs = [entry.get("doc") for entry in run.slot(house, key).get("mounted", [])]
    served = _principal(house, key)
    if (mounted.returncode == 0 and mounted.stdout.strip() == said["mount"] and _one_line(mounted)
            and hold.get("act") == "mount" and "EXT.md" in docs
            and "▌" in served.stdout and "the mounted matter" in served.stdout and not _held(house, key)):
        held("(a) `-mount` is held", "one neutral line back, the mount and the hold at the slot, the "
             "principal's call serves the view with the mounted matter")
    else:
        failures.append(f"  ✗ (a) -mount                  rc={mounted.returncode} {mounted.stdout[:160]!r} "
                        f"act={hold.get('act')!r} docs={docs}")

    # --- (b) a script's ::mount ---------------------------------------------------------------------
    gesture = _agent(house, key, "-s", "pp-probe", "go")
    hold = _held(house, key)
    _principal(house, key)
    if (gesture.returncode == 0 and "probe: chain derived" in gesture.stdout and "▌" not in gesture.stdout
            and said["mount"] in gesture.stdout.splitlines() and hold.get("act") == "mount"
            and "the mounted matter" in hold.get("matter", "")):
        held("(b) a script's `::mount`", "its own text in the tool return, the view held")
    else:
        failures.append(f"  ✗ (b) ::mount                 rc={gesture.returncode} {gesture.stdout[:200]!r} "
                        f"act={hold.get('act')!r}")

    # --- (c) a script called bare: its manual answers the call ---------------------------------------
    manual = _agent(house, key, "-s", "pp-probe")
    docs = [entry.get("doc") for entry in run.slot(house, key).get("mounted", [])]
    waiting = persistence.pending_of(persistence.slot_of(house.made, key))
    if (manual.returncode == 0 and "▌" in manual.stdout and "INFORMATION — pp-probe" in manual.stdout
            and "the probe's manual" in manual.stdout and "pp-probe" in docs and not _held(house, key)
            and not waiting.get("matter")):
        held("(c) a bare script's manual answers the call", "the block with the manual in the tool "
             "return, the mount at the slot, nothing held, nothing pending")
    else:
        failures.append(f"  ✗ (c) manual                  rc={manual.returncode} {manual.stdout[:200]!r} "
                        f"docs={docs} held={_held(house, key).get('act')!r} pending={bool(waiting)}")

    # --- (g) -peek ------------------------------------------------------------------------------------
    frozen_peek = _bytes(house, key)
    peeked = _agent(house, key, "-peek")
    if (peeked.returncode == 0 and "▌" in peeked.stdout and "OFFERS" in peeked.stdout
            and not _held(house, key) and _bytes(house, key) == frozen_peek):
        held("(g) `-peek` answers the call", "the standing block in the tool return, nothing held, the "
             "slot byte-identical")
    else:
        failures.append(f"  ✗ (g) -peek                   rc={peeked.returncode} {peeked.stdout[:160]!r} "
                        f"held={_held(house, key).get('act')!r}")

    # --- (h) an offer not at this step ---------------------------------------------------------------
    stray = _agent(house, key, "-s", "NOBODY")
    if (stray.returncode == 2 and "▌" in stray.stdout and "DEVIATION" in stray.stdout
            and "NOBODY" in stray.stdout and not _held(house, key)):
        held("(h) a denied offer answers the call", "exit 2, the block and its DEVIATION in the tool "
             "return, nothing held")
    else:
        failures.append(f"  ✗ (h) denied                  rc={stray.returncode} {stray.stdout[:160]!r} "
                        f"held={_held(house, key).get('act')!r}")

    # --- (f) -disable -------------------------------------------------------------------------------------
    switched = _agent(house, key, "-disable", "wit")
    off = run.slot(house, key).get("off") or []
    fact = switched.stdout.split("▌", 1)[0]
    if (switched.returncode == 0 and "wit" in fact and "▌" in switched.stdout
            and "wit" in off and not _held(house, key)):
        held("(f) `-disable`: the fact and the block answer the call", "the fact then the block in the "
             "tool return, `wit` out of the play, nothing held")
    else:
        failures.append(f"  ✗ (f) -disable                rc={switched.returncode} {switched.stdout[:160]!r} "
                        f"off={off} held={_held(house, key).get('act')!r}")
    _agent(house, key, "-enable", "wit")

    # --- (i) one hold at a time ------------------------------------------------------------------------
    _agent(house, key, "-compacted")             # a hold: the re-serve waits for the principal
    frozen, kinds_held = _bytes(house, key), run.kinds(house, key)
    bounced = [_agent(house, key, *call) for call in (("-mount", '[{"doc": "EXT.md"}]'), ("-compacted",),
                                                       ("-peek",), ("-disable", "wit"), ("-s", "pp-nothing"))]
    bounced += [_agent(house, key, "-", stdin=run.GOOD), _agent(house, key, "-", stdin=run.GOOD)]
    same = _bytes(house, key) == frozen and run.kinds(house, key) == kinds_held
    _principal(house, key)
    if all(out.returncode == 0 and out.stdout.strip() == pp._HELD_BOUNCE for out in bounced) and same:
        held("(i) one output held at a time", "a mount, a re-serve, a peek, a switch, a `-s` and two values "
             "bounce on the console's held line, rc 0, the slot byte-identical, nothing traced")
    else:
        failures.append(f"  ✗ (i) the bounces             {[(o.returncode, o.stdout[:60]) for o in bounced]} same={same}")

    # --- (e) -compacted --------------------------------------------------------------------------------
    compacted = _agent(house, key, "-compacted")
    hold = _held(house, key)
    _principal(house, key)
    if (compacted.returncode == 0 and _one_line(compacted) and compacted.stdout.strip() == said["compacted"]
            and hold.get("act") == "compacted"):
        held("(e) `-compacted` is held", "one line back, the re-serve at the slot")
    else:
        failures.append(f"  ✗ (e) -compacted              rc={compacted.returncode} {compacted.stdout[:160]!r} "
                        f"act={hold.get('act')!r}")

    # --- (d) a routed door ------------------------------------------------------------------------------
    frames = len(run.slot(house, key).get("frames", []))
    door = _agent(house, key, "-s", "SIDE")
    hold = _held(house, key)
    pushed = len(run.slot(house, key).get("frames", []))
    _principal(house, key)
    if (door.returncode == 0 and _one_line(door) and door.stdout.strip() == said["door"]
            and hold.get("act") == "door" and pushed > frames
            and "the side door's brief" in hold.get("matter", "") and "inline" not in run.kinds(house, key)):
        held("(d) a routed door is held", f"one line back, the frame pushed ({frames} -> {pushed}), its "
             "block at the slot, nothing inline")
    else:
        failures.append(f"  ✗ (d) door                    rc={door.returncode} {door.stdout[:160]!r} "
                        f"act={hold.get('act')!r} frames={frames}->{pushed}")

    # --- (m) a manual over the host's cap -----------------------------------------------------------------
    body = "".join(f"long manual line {n:04d} -- the witness verb explained at length\n" for n in range(600))
    tall.write("skills/pp-tall/SKILL.md", "---\nname: pp-tall\ndescription: a tall manual\n---\n\n" + body)
    tall.write("skills/pp-tall/pp-tall.py", "def main(argv):\n    return 0\n")
    tall.write("procs/OFFERS.md", OFFERS.replace("  pp-probe\n", "  pp-probe\n  pp-tall\n"))
    key_t, _ = run.opened(tall, True, "OFFERS.md")
    first = _agent(tall, key_t, "-s", "pp-tall")
    pieces, rests = [first.stdout], []
    while len(pieces) < 12:
        rests.append(bool(persistence.viewing_of(persistence.slot_of(tall.made, key_t)).get("matter")))
        if not rests[-1]:
            break
        pieces.append(_agent(tall, key_t).stdout)
    after = _agent(tall, key_t)
    lines = [line for piece in pieces for line in piece.splitlines() if line.startswith("long manual line ")]
    if (first.returncode == 0 and len(pieces) >= 3 and all(len(one) <= TALL_CAP for one in pieces)
            and lines == body.splitlines() and not _held(tall, key_t)
            and after.returncode == 2 and "principal-advances" in after.stderr
            and rests == [True] * (len(pieces) - 1) + [False]
            and all("▶ CONTINUE" in run.closing(one) for one in pieces[:-1])):
        held("(m) a manual over the cap comes in chunks", f"{len(body)} characters in {len(pieces)} outputs "
             f"under {TALL_CAP}, the rest kept at the slot's view and served by the agent's bare calls, the "
             "lines whole and in order; after the last, the bare call refuses principal-advances")
    else:
        failures.append(f"  ✗ (m) the tall manual         rc={first.returncode} pieces={[len(one) for one in pieces]} "
                        f"rests={rests} lines={len(lines)}/{len(body.splitlines())} after={after.returncode} "
                        f"{first.stdout[-200:]!r} {first.stderr[-200:]!r}")

    # --- (l) one seam ------------------------------------------------------------------------------------
    console = (bench.source() / "engine" / "pp.py").read_text(encoding="utf-8")
    printed = [n for n, line in enumerate(console.splitlines(), 1) if ".rendered(" in line or ".shown(" in line]
    if not printed:
        held("(l) one seam", "no line of engine/pp.py calls `.rendered(` or `.shown(` itself")
    else:
        failures.append(f"  ✗ (l) the seam                lines {printed}")
    return 0
