"""Scenario `principal-hold` -- in a run its principal conducts, the conduction leaves by the
principal's call alone. The console tells the callers apart by the run the launcher names to the
harness it launches, `PP_CONDUCTED_RUN=<key>`: a keyed call on that run carrying it is the agent's, any
other the principal's. The agent's value is judged when it is given; a block the
engine renders on the agent's call and that MOVES the run or its view leaves through one seam and
is HELD at the run until the principal's bare call serves it -- the agent's tool return carries
what the act answers and one neutral line. A script's own text and a refusal are answers: they
reach the caller, and so does what only SHOWS (a peek, a bare script's manual, a
denied offer, a switch), cut under the host's cap, the rest on the agent's bare keyed call. One
output is held at a time.

The value and the principal's call:
- (a) the door's WORK said by the agent's print call, the proof block -- never served -- held and served by
  the principal's bare call; the agent's bare call refuses
  `principal-advances`: exit 2, no block, the slot the same
- (b) the agent's value is judged at once and its output held: one neutral line, rc 0; the trace
  says `answer` then `held`; the frames moved; the slot carries `held`, its act `value`
- (d) the principal's bare call serves the held output -- the block after the proof -- and the slot
  forgets it; traced `advance` with `held: true`
- (d2) the release cut under the principal's cap keeps it: the later bare calls under a roomier cap
  serve the rest in chunks under the release's cap
- (e) a faulty proof: the REPAIR is held, then served by the principal's call
- (f) no value given where one is due (the WORK said, the proof asked): the principal's bare call plays
  the empty-answer repair
- (g) the frontier: the principal's call carries the message, traced `prompt`, and the next
  exchange opens
- (h) a principal's call carrying a text over a held output refuses `output-held`
- (i) a chunk waiting (a reading past the floor of the principal's cap): the agent's bare call
  refuses, its value bounces `chunk-pending`; its `-peek` PLAYS (a view moves nothing: the block
  rendered, the chunk still waiting); a script it calls, its `-print`, its `-disable` and its `-enable` bounce
  `chunk-pending`, nothing played, nothing kept, the package in its state; the principal's bare call serves the chunk; the agent's `-skip`
  bounces, the principal's `-skip` drops the rest and serves the block's closing
- (j) a `-new` under a launcher that names the principal's run standing mid-exchange
  (`PP_CONDUCTED_RUN=<key>`) opens nothing; unnamed, or naming another run, it opens even while
  that run stands; once that run is parked on its AWAIT, the named `-new` opens a run
- (k) a whole exchange conducted by a launcher witness: the principal's `-new`, each output served to an
  agent witness that hands each print due and pipes its proof on the agent's call, the launcher's bare call
  serving the rest, the run parked on its AWAIT and its last output served -- no served output carries `./pp <key>` under a closing; the last one alone
  closes, on the AWAIT of the passage over, with no call under it
- (o) a repaired proof -- the PROVE of a root fused under its callee's line --: the boot's output asks it; once
  it fails, the REPAIR, a conduction already seen, comes back in the agent's tool return (traced `inline`, nothing
  held) with the callee's line and the PROVE again; the line handed again, the proof piped passes, never judged
  empty: one repair counted
- (n) the last FREE step of an output stays PENDING for the principal's call: the principal's boot closes
  on the TURN's WORK, the agent's `-peek` renders TURN{2/5}, a `-s` played there stacks on it -- the
  door's block, never served, is HELD even though it ends on a proof: one neutral line, nothing inline,
  the principal's bare call serves it; the WORK said by its print call, the principal's bare call
  resolves it and crosses the `§` of the document attached at turn.end in the same call
- (r) a text the agent hands where nothing is asked: the proof's step stands unasked (the test withdraws its ask
  at the slot, as a step no output asked yet); the stray production moves the run to that step's block, never
  served, asking a proof -- its DEVIATION says the stray text, yet it is no replay: HELD, nothing inline, the
  principal's bare call serves it

The acts held or answered:
- (a) `-mount`: one neutral line, no block; the mount written and the hold at the slot (`act:
  mount`); the principal's bare call serves the view
- (b) a script's `::mount`: the script's text in the tool return, the view held
- (q) a script's `::mount` on a step that asks a proof `=> tool_heredoc`: the mounted matter is new --
  the script's text and the neutral line in the tool return, the view HELD, nothing inline; the
  principal's bare call serves the readings and the proof's line
- (c) a script called bare: its manual ANSWERS the call -- the block in the tool return, the mount
  written at the slot, nothing held, nothing pending
- (g) `-peek`: the block in the tool return, nothing held
- (h) an offer not at this step: exit 2, the block and its DEVIATION in the tool return, nothing held
- (f) `-disable`: the fact AND the block in the tool return, the package out of the play, nothing held
- (i) while an output is held, a mount, a re-serve, a door and a value bounce on the console's held
  line: nothing played, nothing traced, the slot byte-identical; a peek, a switch, an unoffered name
  and a script PLAY -- they move nothing: the block in the tool return, the script run, its `::mount`
  JOINING the held output, whose readings stay first and whose step stands under one heading
- (p) a held output that another joins says its step ONCE: a script's view held, then the same script played
  again over it -- the output served carries one heading for the step that stands, its tools and its laws
  once, its line once, the matter the first view read still there
- (e) `-compacted`: the re-serve held (`act: compacted`)
- (d) a routed door: its frame pushed, its block held (`act: door`), nothing inline
- (m) a manual over the host's cap: the first chunk in the tool return, the rest served by the
  agent's bare keyed calls, the concatenation the body to the byte; after the last, the bare call
  refuses `principal-advances`
- (l) one seam: no line of the console prints `.rendered(` or `.shown(` itself
"""
from __future__ import annotations

import json

from conductor.core import messages
from conductor import Conductor, persistence
from conductor.core import language
from tests.harness import cli, support, titled, titles

run = support(__file__, "run")
LAST = f"=> {language.TERMINAL}  ("   # the last step: it stays `terminal`, rendered by its print call

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
MISSED = titled(language.DEVIATION)      # the line that opens a block's DEVIATION, its title the engine's
TALL = f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {TALL_CAP}\n---\n"
OFFERING = "---\nname: TURN\ntools: |\n  +PROVER\n---\n"      # the base's TURN offers the door to its WORK
FUSED = "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 60000\ninstructions_fusion: max\n---\n"
            # the fused stretch the template plays: the WORK is BATCHED, not asked -- what (n) proves
SAYP = "---\nname: SAYP\nkind: proc\ndescription: says one line\nproc: |\n  INFER\n---\nsay\n"
ROOTP = ("---\nname: ROOTP\nkind: proc\ndescription: proves its callee's line\nconstraints.production: |\n"
         "  Z1  say it plainly\nproc: |\n  CALL SAYP.md\n  PROVE\n---\nprove the callee\n")
FAILED = '[{"code": "Z1", "evidence": "off", "verdict": "fail"}]'
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
    return cli(env.engine, key, *words, cwd=env.root, stdin=stdin, env=run.agent(key))


def _principal(env, key: str, *words):
    return cli(env.engine, key, *words, cwd=env.root)


def _said(env, key: str) -> list:
    """The agent hands every print due by its print call -> the calls' outputs."""
    return [_agent(env, key, "-print", one["document"], "-", stdin="said\n")
            for one in persistence.prints_of(persistence.slot_of(env.made, key))]


def _served(env, key: str) -> list:
    """The prints handed (`_said`) -> their outputs; when the run moved on to a block never served,
    that block is held and the principal's bare call serving it closes the list."""
    outs = _said(env, key)
    return outs + [_principal(env, key)] if outs and _held(env, key) else outs


def _one_line(out) -> bool:
    return "▌" not in out.stdout and out.stdout.strip().count("\n") <= 1


def _bytes(env, key: str) -> bytes:
    return persistence.slot_of(env.made, key).read_bytes()


def _heading(text: str) -> str:
    return next((one for one in reversed(text.splitlines()) if one.startswith("▌ ") and "▸" in one), "")


def scenario(bench) -> int:
    import pp                                                                  # noqa: PLC0415
    held, failures = bench.held, bench.failures
    said = {act: messages.held(act) for act in messages.ACKNOWLEDGED}
    # one house for every act on a short door: each case opens its own run beside the others
    house = _house(bench, "hold-acts", ("wit",))

    # === the value and the principal's call =======================================================

    # --- (a) the agent's bare call refuses ------------------------------------------------------------
    key, opened = run.opened(house, "PROVER.md")
    asked = (_served(house, key) or [opened])[-1]          # the door's WORK said: the proof block, never served,
                                                           # held, then served by the principal's call
    before = _bytes(house, key)
    bare = _agent(house, key)
    if (opened.returncode == 0 and key and "proof" in asked.stdout and bare.returncode == 2
            and "principal-advances" in bare.stderr and "▌" not in bare.stdout and _bytes(house, key) == before):
        held("(a) the agent's bare call refuses", f"run {key}: `./pp {key}` on the agent's call -- "
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

    # --- (d2) the release keeps its cap: the rest under it, whatever the cap of the later calls -----------
    narrow, roomy = {"PP_PROMPT_CAP": "1000"}, {"PP_PROMPT_CAP": "100000"}
    key_d2, _ = run.opened(house, "PROVER.md")
    _served(house, key_d2)
    _agent(house, key_d2, "-", stdin=run.GOOD)            # the output held
    released = cli(house.engine, key_d2, cwd=house.root, env=narrow)
    rests_d2 = []
    while (persistence.pending_of(persistence.slot_of(house.made, key_d2)).get("matter") or
           persistence.pending_of(persistence.slot_of(house.made, key_d2)).get("steps")) and len(rests_d2) < 50:
        rests_d2.append(cli(house.engine, key_d2, cwd=house.root, env=roomy))
    if (released.returncode == 0 and "a reading continues" in released.stdout and len(released.stdout) <= 1001
            and rests_d2 and all(one.returncode == 0 and len(one.stdout) <= 1001 for one in rests_d2)):
        held("(d2) the release keeps its cap", f"the held output released under 1000, its rest served by "
             f"{len(rests_d2)} bare call(s) under a cap of 100000, none over 1000")
    else:
        failures.append(f"  ✗ (d2) the release's cap       rc={released.returncode} first={len(released.stdout)} "
                        f"rests={[len(one.stdout) for one in rests_d2]} {released.stderr[-160:]!r}")

    # --- (e) a faulty proof: the REPAIR held, then served ------------------------------------------------
    key2, _ = run.opened(house, "PROVER.md")
    _served(house, key2)                                   # the WORK said: the proof asked
    faulty = _agent(house, key2, "-", stdin='[{"code": "Z1", "evidence": "off", "verdict": "fail"}]')
    repaired = _principal(house, key2)
    kinds2 = run.kinds(house, key2)
    if (faulty.returncode == 0 and faulty.stdout.strip() == said["value"] and "repair" in kinds2
            and repaired.returncode == 0 and "REPAIR" in repaired.stdout and MISSED in repaired.stdout):
        held("(e) a faulty proof: the REPAIR is held, then served", "a bare fail on Z1: the trace says repair, the "
             "agent gets its one line, the principal's call renders the REPAIR block")
    else:
        failures.append(f"  ✗ (e) the held repair           rc={faulty.returncode}/{repaired.returncode} "
                        f"kinds={kinds2[-4:]} {repaired.stdout[-200:]!r}")

    # --- (f) no value where one is due: the empty-answer repair at the principal's call -------------------
    key3, _ = run.opened(house, "PROVER.md")
    _served(house, key3)                                   # the WORK said: the proof asked
    empty = _principal(house, key3)
    if empty.returncode == 0 and "REPAIR" in empty.stdout and "repair" in run.kinds(house, key3):
        held("(f) no value given: today's empty-answer repair", "the principal's bare call on a due proof "
             "renders the REPAIR")
    else:
        failures.append(f"  ✗ (f) the empty answer          rc={empty.returncode} {empty.stdout[-200:]!r}")

    # --- (g) the frontier: the principal's call carries the message ---------------------------------------
    parked, hops = served, 0
    while persistence.awaits_of(run.slot(house, key)) != persistence.MESSAGE and hops < 6:   # the turn to its end
        _said(house, key)
        parked = _principal(house, key)
        hops += 1
    frontier = (persistence.awaits_of(run.slot(house, key)) == persistence.MESSAGE)
    spoken = _principal(house, key, "the principal's next word")
    prompts = [e for e in run.trace(house, key) if e.get("kind") == "prompt"]
    if (frontier and spoken.returncode == 0 and "▌" in spoken.stdout
            and prompts and prompts[-1].get("text") == "the principal's next word"):
        held("(g) the frontier: the message rides the principal's call", f"parked after {hops} hop(s), "
             "the principal's call with a text traced `prompt`, the next exchange opened")
    else:
        failures.append(f"  ✗ (g) the frontier              frontier={frontier} rc={spoken.returncode} "
                        f"prompts={prompts[-1:]} {spoken.stdout[-160:]!r}")

    # --- (h) the principal's call with a text over a held output refuses -----------------------------------------
    key4, _ = run.opened(house, "PROVER.md")
    _served(house, key4)
    _agent(house, key4, "-", stdin=run.GOOD)
    over = _principal(house, key4, "some text")
    if over.returncode == 2 and "output-held" in over.stderr and _held(house, key4):
        held("(h) a text over a held output refuses", "output-held, exit 2, the hold intact")
    else:
        failures.append(f"  ✗ (h) output-held               rc={over.returncode} {over.stderr[-160:]!r}")

    # --- (i) a chunk waiting: a reading past the floor of the principal's cap ------------------------------
    # one house for the long readings: the floor cuts whatever the setting, the manual cuts at the host's
    tall = _house(bench, "hold-long", ("wit",))
    tall.write("SETTINGS.md", TALL)
    tall.write("LONG.md", run.PAST)
    tall.write("procs/LONGRUN.md", run.LONGRUN)
    key5, _ = run.opened(tall, "LONGRUN.md")
    pending = key5 and persistence.pending_of(persistence.slot_of(tall.made, key5)).get("matter")
    bare5 = _agent(tall, key5) if key5 else None
    valued5 = _agent(tall, key5, "a value") if key5 else None
    chunk = _principal(tall, key5) if key5 else None
    still = key5 and persistence.pending_of(persistence.slot_of(tall.made, key5)).get("matter")
    # a view moves nothing: it plays while the chunk waits; a gesture and a print bounce, the chunk untouched
    left_before = still
    peek5 = _agent(tall, key5, "-peek") if still else None
    kept_before = key5 and sum(run.kinds(tall, key5).count(kind) for kind in ("answer", "stray"))
    gest5 = _agent(tall, key5, "-s", "pp-probe", "go") if still else None
    print5 = _agent(tall, key5, "-print", "LONGRUN", "-", stdin="said\n") if still else None
    switches_before = key5 and dict(run.slot(tall, key5).get("switches") or {})
    off5 = _agent(tall, key5, "-disable", "wit") if still else None
    switches_off = key5 and dict(run.slot(tall, key5).get("switches") or {})
    on5 = _agent(tall, key5, "-enable", "wit") if still else None
    switches_after = key5 and dict(run.slot(tall, key5).get("switches") or {})
    kept_after = key5 and sum(run.kinds(tall, key5).count(kind) for kind in ("answer", "stray"))
    left_after = key5 and persistence.pending_of(persistence.slot_of(tall.made, key5)).get("matter")
    agent_skip = _agent(tall, key5, "-skip") if still else None
    led_skip = _principal(tall, key5, "-skip") if still else None
    gone = key5 and not persistence.pending_of(persistence.slot_of(tall.made, key5)).get("matter")
    if (pending and bare5.returncode == 2 and "principal-advances" in bare5.stderr
            and valued5.returncode == 0 and "chunk-pending" in valued5.stdout and "▌" not in valued5.stdout
            and chunk.returncode == 0 and "▌" in chunk.stdout
            and still and peek5.returncode == 0 and "▌" in peek5.stdout and "chunk-pending" not in peek5.stdout
            and all(one.returncode == 0 and one.stdout.startswith("pp: chunk-pending") and "▌" not in one.stdout
                    for one in (gest5, print5, off5, on5))
            and switches_before == switches_off == switches_after and "wit" not in switches_after
            and kept_after == kept_before and left_after == left_before
            and agent_skip.returncode == 0 and "chunk-pending" in agent_skip.stdout
            and led_skip.returncode == 0 and "▌" in led_skip.stdout and gone
            and "chunk-dropped" in run.kinds(tall, key5)):
        held("(i) a chunk waiting", "the agent's bare call refuses, its value bounces chunk-pending; its -peek "
             "renders the block; its gesture, its -print, its -disable and its -enable bounce chunk-pending, "
             "nothing kept, wit in its state, the chunk untouched; the principal's bare "
             "call serves the chunk; the agent's -skip bounces, the principal's drops the rest")
    else:
        failures.append(f"  ✗ (i) the chunk                 pending={bool(pending)} "
                        f"{bare5 and bare5.returncode}/{valued5 and valued5.returncode}/{chunk and chunk.returncode} "
                        f"peek={peek5 and peek5.stdout[:80]!r} gest={gest5 and (gest5.returncode, gest5.stdout[:80])!r} "
                        f"print={print5 and (print5.returncode, print5.stdout[:80])!r} kept={kept_before}->{kept_after} "
                        f"switch={off5 and (off5.returncode, off5.stdout[:80])!r}/{on5 and (on5.returncode, on5.stdout[:80])!r} "
                        f"switches={switches_before}->{switches_off}->{switches_after} "
                        f"same={left_after == left_before} {bare5 and bare5.stderr[-120:]!r}")

    # --- (j) the soft -new --------------------------------------------------------------------------------
    key6, _ = run.opened(house, "PROVER.md")              # mid-exchange: its WORK stands
    slots_before = len(persistence.slots(house.made))
    named = {run.CONDUCTED_RUN: key6}                            # the launcher names the run it conducts
    soft = cli(house.engine, "-new", cwd=house.root, env=named)
    slots_after_soft = len(persistence.slots(house.made))
    key8, unnamed = run.opened(house)                            # another conversation of the instance
    key9, other = run.opened(house, None, {run.CONDUCTED_RUN: "zzzzzz"})
    key7, second = run.opened(house)                            # a second conversation
    # the principal's runs to their AWAIT: the principal's bare calls, a proof asked piped by the agent
    for k in (key6, key7):
        hops = 0
        while k and hops < 8 and not (persistence.awaits_of(run.slot(house, k)) == persistence.MESSAGE):
            _said(house, k)
            out = _principal(house, k)
            if run.CODES.search(out.stdout):
                _agent(house, k, "-", stdin=run.GOOD)
            hops += 1
    parked_all = all((persistence.awaits_of(run.slot(house, k)) == persistence.MESSAGE) for k in (key6, key7) if k)
    opened_after = cli(house.engine, "-new", cwd=house.root, env=named)
    if (soft.returncode == 0 and key6 in soft.stdout and not run.key_of(soft.stdout)
            and "▌" not in soft.stdout and soft.stdout.strip().count("\n") == 0
            and slots_after_soft == slots_before
            and unnamed.returncode == 0 and key8 and other.returncode == 0 and key9
            and second.returncode == 0 and key7 and len({key6, key7, key8, key9}) == 4
            and parked_all and opened_after.returncode == 0 and run.key_of(opened_after.stdout)):
        held("(j) the soft -new", f"`-new` under PP_CONDUCTED_RUN={key6} mid-exchange: one line naming it, no "
             f"block, no slot; unnamed it opened {key8}, naming another run {key9}, a second {key7}; {key6} "
             "parked on its AWAIT, the named `-new` opens a run")
    else:
        failures.append(f"  ✗ (j) the soft -new             rc={soft.returncode} {soft.stdout[-160:]!r} "
                        f"slots={slots_after_soft}/{slots_before} unnamed={key8!r} other={key9!r} key7={key7!r} "
                        f"parked={parked_all} after={opened_after.returncode}")

    # --- (k) a whole exchange conducted by the launcher witness -------------------------------------------
    outputs = []
    key10, first = run.opened(house, "PROVER.md")
    outputs.append(first.stdout)
    calls = 0
    while key10 and calls < 10 and not (persistence.awaits_of(run.slot(house, key10)) == persistence.MESSAGE
                                         and not _held(house, key10)):   # parked, its last output served
        said10 = _said(house, key10)        # a step said `=> terminal`: its print call answers the agent
        if said10:
            outputs.append(said10[-1].stdout)
        else:
            if run.CODES.search(outputs[-1]):   # the agent witness pipes the proof
                _agent(house, key10, "-", stdin=run.proof_of(outputs[-1]))
            outputs.append(_principal(house, key10).stdout)
        calls += 1
    # an output of a run its principal conducts closes on a line where the passage is over, and nowhere
    # else: a value's call is named by its step, the end says AWAIT with no call under it
    commanded = [i for i, out in enumerate(outputs) if run.closing(out)]
    ended = run.closing(outputs[-1]).splitlines()
    proofs = sum(1 for e in run.trace(house, key10) if e.get("kind") == "answer")
    if (key10 and (persistence.awaits_of(run.slot(house, key10)) == persistence.MESSAGE)
            and commanded == [len(outputs) - 1] and ended[:1] == [f"{messages.SIGNAL} {language.AWAIT}"]
            and not any(line.startswith("./pp") for line in ended) and proofs >= 1):
        held("(k) a whole exchange by the launcher", f"run {key10}: {len(outputs)} outputs served, {calls} "
             f"principal call(s), {proofs} value(s) piped by the agent, parked; one closing, the AWAIT of the "
             "passage over, no call under it")
    else:
        failures.append(f"  ✗ (k) the launcher's exchange   key={key10!r} commanded={commanded} proofs={proofs} "
                        f"calls={calls} {[run.closing(outputs[i]) for i in commanded]!r}")

    # --- (o) a repaired proof comes back in the tool return, asked again with its callee's line -------------
    rep = bench.env("hold-repair")
    rep.write("SETTINGS.md", FUSED)
    rep.write("procs/SAYP.md", SAYP)
    rep.write("procs/ROOTP.md", ROOTP)
    key_o, opened_o = run.opened(rep, "ROOTP.md")
    asked_o = bool(run.CODES.search(opened_o.stdout))         # the boot's output: the callee's line, the proof fused
    said_o = _agent(rep, key_o, "-print", "SAYP", "-", stdin="said\n") if key_o else None
    failed_o = _agent(rep, key_o, "-", stdin=FAILED) if key_o else None   # the REPAIR: a conduction already seen
    inline_o = run.kinds(rep, key_o).count("inline") if key_o else -1
    held_o = bool(_held(rep, key_o)) if key_o else True
    again_o = _agent(rep, key_o, "-print", "SAYP", "-", stdin="said again\n") if key_o else None
    proved_o = _agent(rep, key_o, "-", stdin=run.proof_of(failed_o.stdout)) if failed_o is not None else None
    repairs_o = run.kinds(rep, key_o).count("repair") if key_o else -1
    if (asked_o and said_o.returncode == 0 and failed_o.returncode == 0 and "REPAIR" in failed_o.stdout
            and "(SAYP)" in failed_o.stdout and run.CODES.search(failed_o.stdout)
            and inline_o == 1 and not held_o and again_o.returncode == 0
            and proved_o.returncode == 0 and MISSED not in proved_o.stdout and repairs_o == 1):
        held("(o) a repaired proof comes back in the tool return", f"run {key_o}: the proof failed, the REPAIR -- "
             "SAYP's line and ROOTP's PROVE in one output -- answered the agent's call (traced inline, nothing "
             "held); the line handed again, the proof passed -- no empty answer, one repair on the trace")
    else:
        failures.append(f"  ✗ (o) the repaired proof        asked={asked_o} inline={inline_o} held={held_o} "
                        f"repairs={repairs_o} {failed_o and failed_o.stdout[-300:]!r} "
                        f"{proved_o and proved_o.stdout[-300:]!r}")

    # --- (n) the last FREE step stays pending for the principal's call ------------------------------------
    pend = _house(bench, "hold-pending")
    pend.write("procs/TURN.md", OFFERING)
    pend.write("procs/LATE.md", LATE)
    pend.write("SETTINGS.md", FUSED)
    late = f"INFER any {LAST}LATE)"           # LATE's step: the last said of the output it closes
    key_n, booted = run.opened(pend, None, None, "hello")
    peeked = _agent(pend, key_n, "-peek")
    door_n = _agent(pend, key_n, "-s", "PROVER")
    frames = run.slot(pend, key_n).get("frames", [])
    work = next((one for one in (frames[-2] if len(frames) > 1 else {}).get("instructions", [])
                 if one.get("keyword") == "WORK"), {})
    held_n = _held(pend, key_n).get("act")
    kinds_n = run.kinds(pend, key_n)
    door_served = _principal(pend, key_n) if key_n else None      # the door's block, held: the principal serves it
    key_s, _ = run.opened(pend, None, None, "hello")        # no door opened: the principal's call alone
    before_s = run.kinds(pend, key_s).count("block")
    _said(pend, key_s)                                      # the TURN's WORK said by its print call
    crossed = _principal(pend, key_s)
    kinds_s = run.kinds(pend, key_s)
    if (key_n and _heading(booted.stdout).endswith("TURN{2/4}") and f"WORK any {LAST}" in booted.stdout
            and late not in booted.stdout
            and peeked.returncode == 0 and _heading(peeked.stdout).endswith("TURN{2/4}")
            and f"WORK any {LAST}" in peeked.stdout
            and door_n.returncode == 0 and door_n.stdout.strip() == said["door"] and _one_line(door_n)
            and held_n == "door" and "inline" not in kinds_n and "held" in kinds_n
            and door_served.returncode == 0 and "▸ PROVER{" in _heading(door_served.stdout)
            and "proof" in door_served.stdout
            and frames and frames[-1].get("document", "").endswith("PROVER.md") and work.get("asked") is True
            and not work.get("done")
            and key_s and crossed.returncode == 0 and late in crossed.stdout
            and _heading(crossed.stdout).endswith("▸ LATE{1/1}")
            and len([one for one in titles(crossed.stdout) if "▸" in one and "{" in one]) == 1
            and crossed.stdout.count("▌ pp · run") == 1 and "pending" in kinds_s
            and "▶ " not in crossed.stdout.split(late)[0]):
        held("(n) the last FREE step stays pending for the principal", f"run {key_n}: the boot closes on TURN{{2/4}}, "
             "-peek renders it, -s PROVER stacks on the pending WORK and its block, never served, is held "
             "though it closes on a proof (one line back, nothing inline), the principal's call serves it; "
             "the principal's bare call resolves the WORK and "
             f"renders LATE{{1/1}} in ONE output, no order block before it (traced pending), its closing in "
             "LATE's segment, of the same laws")
    else:
        failures.append(f"  ✗ (n) the pending WORK         boot={_heading(booted.stdout)!r} peek={_heading(peeked.stdout)!r} "
                        f"door={door_n.stdout.strip()!r} held={held_n!r} inline={'inline' in kinds_n} "
                        f"served={door_served and _heading(door_served.stdout)!r} frames={[f.get('document', '') for f in frames]} work={work!r} "
                        f"crossed={_heading(crossed.stdout)!r} blocks={before_s}->{kinds_s.count('block')} "
                        f"pending={'pending' in kinds_s} {crossed.stdout!r}")

    # --- (r) a stray text where nothing is asked: the block it leads to, never served, is held ---------------
    key_r, _ = run.opened(house, "PROVER.md")
    _served(house, key_r)                                # the WORK said: the proof's block held, then served
    path_r = persistence.slot_of(house.made, key_r)
    state_r = json.loads(path_r.read_text(encoding="utf-8"))
    for one in state_r["frames"][-1]["instructions"]:
        if one.get("keyword") == "PROVE":
            one["asked"] = False                         # the proof stands, no output asked it yet
    path_r.write_text(json.dumps(state_r), encoding="utf-8")
    kinds_r = run.kinds(house, key_r)
    stray_r = _agent(house, key_r, "-", stdin="a text nobody asked for\n")
    new_r = run.kinds(house, key_r)[len(kinds_r):]
    held_r = _held(house, key_r)
    served_r = _principal(house, key_r) if key_r else None
    if (key_r and stray_r.returncode == 0 and stray_r.stdout.strip() == said["value"]
            and "stray" in new_r and "held" in new_r and "inline" not in new_r and held_r.get("act") == "value"
            and served_r.returncode == 0 and run.CODES.search(served_r.stdout) and MISSED in served_r.stdout):
        held("(r) a stray text leads to a block held", f"run {key_r}: a text handed where nothing is asked -- "
             "traced stray; the proof's block it moves to, never asked, held (one line back, nothing inline); "
             "the principal's call serves it with its DEVIATION")
    else:
        failures.append(f"  ✗ (r) the stray text           rc={stray_r.returncode} {stray_r.stdout[-240:]!r} "
                        f"trace={new_r} act={held_r.get('act')!r}")

    # === the acts held or answered ================================================================
    key, _ = run.opened(house, "OFFERS.md")

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

    # --- (q) a script's ::mount on a step that asks a proof: the mounted matter is new, held ------------
    key_q, _ = run.opened(house, "OFFERS.md")
    _served(house, key_q)                                 # the WORK said: the proof asked `=> tool_heredoc`
    asking = persistence.prints_of(persistence.slot_of(house.made, key_q)) == []
    kinds_q = run.kinds(house, key_q)
    proof_q = _agent(house, key_q, "-s", "pp-probe", "go")
    new_q = run.kinds(house, key_q)[len(kinds_q):]
    hold_q = _held(house, key_q)
    served_q = _principal(house, key_q)
    if (asking and proof_q.returncode == 0 and "probe: chain derived" in proof_q.stdout and "▌" not in proof_q.stdout
            and said["mount"] in proof_q.stdout.splitlines() and "inline" not in new_q and "held" in new_q
            and hold_q.get("act") == "mount" and "the mounted matter" in hold_q.get("matter", "")
            and served_q.returncode == 0 and "the mounted matter" in served_q.stdout
            and run.CODES.search(served_q.stdout) and not _held(house, key_q)):
        held("(q) a `::mount` on a proof step is held", f"run {key_q}: the proof asked `=> tool_heredoc`, the "
             "script's text and the neutral line back, the mounted view held (nothing inline); the principal's "
             "call serves the matter and the proof's line")
    else:
        failures.append(f"  ✗ (q) ::mount on a proof      asking={asking} rc={proof_q.returncode} "
                        f"{proof_q.stdout[:240]!r} trace={new_q} act={hold_q.get('act')!r}")

    # --- (c) a script called bare: its manual answers the call ---------------------------------------
    manual = _agent(house, key, "-s", "pp-probe")
    docs = [entry.get("doc") for entry in run.slot(house, key).get("mounted", [])]
    waiting = persistence.pending_of(persistence.slot_of(house.made, key))
    if (manual.returncode == 0 and "▌" in manual.stdout and titled(language.INFORMATION, "pp-probe") in manual.stdout
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
    if (stray.returncode == 2 and "▌" in stray.stdout and MISSED in stray.stdout
            and "NOBODY" in stray.stdout and not _held(house, key)):
        held("(h) a denied offer answers the call", "exit 2, the block and its DEVIATION in the tool "
             "return, nothing held")
    else:
        failures.append(f"  ✗ (h) denied                  rc={stray.returncode} {stray.stdout[:160]!r} "
                        f"held={_held(house, key).get('act')!r}")

    # --- (f) -disable -------------------------------------------------------------------------------------
    switched = _agent(house, key, "-disable", "wit")
    off = [name for name, said in (run.slot(house, key).get("switches") or {}).items() if said == "off"]
    fact = switched.stdout.split("▌", 1)[0]
    if (switched.returncode == 0 and "wit" in fact and "▌" in switched.stdout
            and "wit" in off and not _held(house, key)):
        held("(f) `-disable`: the fact and the block answer the call", "the fact then the block in the "
             "tool return, `wit` out of the play, nothing held")
    else:
        failures.append(f"  ✗ (f) -disable                rc={switched.returncode} {switched.stdout[:160]!r} "
                        f"off={off} held={_held(house, key).get('act')!r}")
    _agent(house, key, "-enable", "wit")

    # --- (i) one hold at a time: what moves the run bounces, what moves nothing plays ----------------------
    _agent(house, key, "-compacted")             # a hold: the re-serve waits for the principal
    frozen, kinds_held = _bytes(house, key), run.kinds(house, key)
    bounced = [_agent(house, key, *call) for call in (("-mount", '[{"doc": "EXT.md"}]'), ("-compacted",),
                                                       ("-s", "SIDE"))]
    bounced += [_agent(house, key, "-", stdin=run.GOOD), _agent(house, key, "-", stdin=run.GOOD)]
    same = _bytes(house, key) == frozen and run.kinds(house, key) == kinds_held
    peeked_held = _agent(house, key, "-peek")
    same_after_peek = _bytes(house, key) == frozen
    switched_held = _agent(house, key, "-disable", "wit")
    off_held = [name for name, said in (run.slot(house, key).get("switches") or {}).items() if said == "off"]
    _agent(house, key, "-enable", "wit")
    denied_held = _agent(house, key, "-s", "pp-nothing")
    held_before = _held(house, key)
    gestured_held = _agent(house, key, "-s", "pp-probe", "go")
    held_after = _held(house, key)
    _principal(house, key)
    read_before, read_after = ([one for one in titles(each.get("matter", ""))
                                if one.startswith(titled(language.INFORMATION))] for each in (held_before, held_after))
    stood = [one for one in titles(held_after.get("matter", "")) if "OFFERS{" in one]
    if (all(out.returncode == 0 and out.stdout.strip() == messages.bounced() for out in bounced) and same
            and peeked_held.returncode == 0 and "▌" in peeked_held.stdout and "OFFERS" in peeked_held.stdout
            and same_after_peek
            and switched_held.returncode == 0 and "▌" in switched_held.stdout and "wit" in off_held
            and denied_held.returncode == 2 and MISSED in denied_held.stdout
            and gestured_held.returncode == 0 and "probe: chain derived" in gestured_held.stdout
            and said["mount"] in gestured_held.stdout.splitlines()
            and held_before.get("act") == "compacted" and held_after.get("act") == "mount"
            and read_before and read_after[:len(read_before)] == read_before and len(stood) == 1
            and "the mounted matter" in held_after.get("matter", "")):
        held("(i) one output held at a time", "a mount, a re-serve, a door and two values bounce on the "
             "console's held line, rc 0, the slot byte-identical, nothing traced; the peek renders the block "
             "(slot untouched), the switch its fact and the block, the unoffered name its DEVIATION; the script "
             "runs and its `::mount` joins the held output: the readings of the re-serve first, in their order, "
             "the mounted matter with them, one heading for the step that stands")
    else:
        failures.append(f"  ✗ (i) the bounces             {[(o.returncode, o.stdout[:60]) for o in bounced]} same={same} "
                        f"peek={peeked_held.stdout[:60]!r} switch={switched_held.stdout[:60]!r} off={off_held} "
                        f"denied={denied_held.returncode} gest={gestured_held.stdout[:120]!r} "
                        f"acts={held_before.get('act')!r}->{held_after.get('act')!r} "
                        f"read={read_before}->{read_after} stood={len(stood)}")

    # --- (p) a held output that another joins says its step once -----------------------------------------
    key_p, _ = run.opened(house, "OFFERS.md")
    viewed = _agent(house, key_p, "-s", "pp-probe", "go")        # the view of the step that stands, held
    again = _agent(house, key_p, "-s", "pp-probe", "go")         # the same step viewed again: it joins the hold
    joined = _principal(house, key_p)
    shown = titles(joined.stdout)
    stepped = [one for one in shown if "OFFERS{" in one]
    asked = [one for one in joined.stdout.splitlines() if one.startswith("WORK ") and one.endswith("(OFFERS)")]
    if (viewed.returncode == 0 and again.returncode == 0 and joined.returncode == 0
            and len(stepped) == 1 and len(asked) == 1
            and [shown.count(titled(one)) for one in (language.TOOLS, language.CONSTRAINTS, language.INSTRUCTION)]
            == [1, 1, 1]
            and titled(language.INFORMATION, "EXT") in shown and not _held(house, key_p)):
        held("(p) a held output another joins says its step once", f"run {key_p}: the script's view held, the "
             "script played again over it; the output served carries one heading for OFFERS' step, its tools, "
             "its laws and its line once, the matter the first view read under it")
    else:
        failures.append(f"  ✗ (p) a joined hold             rc={viewed.returncode}/{again.returncode}/{joined.returncode} "
                        f"headings={len(stepped)} lines={len(asked)} {shown}")

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
            and any("the side door's brief" in read for read, *_ in hold.get("steps", []))
            and "inline" not in run.kinds(house, key)):
        held("(d) a routed door is held", f"one line back, the frame pushed ({frames} -> {pushed}), its "
             "block at the slot -- the door's brief in the group of its step --, nothing inline")
    else:
        failures.append(f"  ✗ (d) door                    rc={door.returncode} {door.stdout[:160]!r} "
                        f"act={hold.get('act')!r} frames={frames}->{pushed}")

    # --- (m) a manual over the host's cap -----------------------------------------------------------------
    body = "".join(f"long manual line {n:04d} -- the witness verb explained at length\n" for n in range(600))
    tall.write("skills/pp-tall/SKILL.md", "---\nname: pp-tall\ndescription: a tall manual\n---\n\n" + body)
    tall.write("skills/pp-tall/pp-tall.py", "def main(argv):\n    return 0\n")
    tall.write("procs/OFFERS.md", OFFERS.replace("  pp-probe\n", "  pp-probe\n  pp-tall\n"))
    key_t, _ = run.opened(tall, "OFFERS.md")
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
