"""Scenario `principal-advances` -- 13 case(s) (plan core, batch la-remise, 2026-10-07): in a run
its principal conducts, the conduction leaves by the principal's call alone. The console tells
the callers apart by the mark `PP_CONDUCTED_BY_PRINCIPAL=true` on the keyed call: a marked call
is the principal's, any other the agent's. The agent's value is judged when it is given, by the
one judge of both modes; its rendered output is HELD at the run until the principal's bare call
serves it.
- (a) the agent's bare call refuses `principal-advances`: exit 2, no block, the slot the same
- (b) the agent's value is judged at once and its output held: one neutral line (`value judged`),
  rc 0; the trace says `answer` then `held`; the frames moved; the slot carries `held`, its act
  `value`
- (c) a second value, and a `-s`, while an output is held bounce: one line, rc 0, `held` intact,
  nothing more traced
- (d) the principal's bare call serves the held output -- the block after the proof -- and the slot
  forgets it; traced `advance` with `held: true`
- (e) a faulty proof: the REPAIR is held, then served by the principal's call
- (f) no value given where one is due: the principal's bare call plays today's empty-answer repair
- (g) the frontier: the principal's call carries the message, traced `prompt`, and the next
  exchange opens
- (h) a marked call carrying a text over a held output refuses `output-held`
- (i) a chunk waiting (a reading past the floor of the principal's cap): the agent's bare call refuses, its value bounces `chunk-pending`, the
  principal's bare call serves the chunk
- (j) an unmarked `-new` while a principal's run stands mid-exchange opens nothing and says so;
  once that run is parked on its FINAL, the same `-new` opens a run
- (k) a whole exchange conducted by a launcher witness: `-new` marked, each output served to an
  agent witness that pipes its proof unmarked, the launcher's bare call serving the rest, the run
  parked on its FINAL -- and no served output that moves the run carries `./pp <key>` under
  CONTINUE or FINAL (a closing that asks a value keeps its command)
- (l) the same proof at the same step on two throwaways: the LLM mode's tool return and the
  principal mode's served output are the same matter, their closings apart
- (m) the LLM's mode is today's: an unmarked value is judged and its block returned, a bare call
  advances
"""
from __future__ import annotations

import json
import re

from conductor import persistence, settings
from tests.harness import cli

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
MARK = {VARIABLE: "true"}
KEY = re.compile(r"run ([0-9a-f]{6})")
CODES = re.compile(r"INFER proof \[([^\]]*)\]")
PROVER = ("---\nname: PROVER\nkind: proc\ndescription: a witness\nconstraints.production: |\n"
          "  Z1  say it plainly\nproc: |\n  WORK\n---\nprove\n")
PAST = ("---\nname: LONG\nkind: doc\n---\n\n"   # past the floor of a principal's cap: it cuts whatever the setting
        + "long line of matter\n" * (2 * settings.PRINCIPAL_CAP // 20) + "\n")
LONGRUN = "---\nname: LONGRUN\nkind: proc\ndescription: a witness\nproc: |\n  SERVE LONG.md\n  WORK\n---\nread\n"
CAP = "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n"
GOOD = '[{"code": "Z1", "evidence": "said plainly", "verdict": "ok"}]'


def _slot(env, key: str) -> dict:
    path = persistence.slot_of(env.made, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _trace(env, key: str) -> list[dict]:
    log = _slot(env, key).get("log") or ""
    trace = env.made / persistence.DIRECTORY / log
    if not log or not trace.is_file():
        return []
    return [json.loads(one) for one in trace.read_text(encoding="utf-8").splitlines() if one.strip()]


def _kinds(env, key: str) -> list[str]:
    return [one.get("kind", "") for one in _trace(env, key)]


def _pointer(env, key: str) -> list:
    """-> the done flags of every frame's instructions: where the run stands."""
    return [[one.get("done") for one in frame.get("instructions", [])]
            for frame in _slot(env, key).get("frames", [])]


def _closing(text: str) -> str:
    lines = text.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return "\n".join(lines[at:])


def _matter(text: str, key: str, root: str) -> str:
    """-> the output without its heading line and its closing, keys and paths neutralized."""
    body = text.split("\n▶ ")[0]
    return body.replace(key, "KEY").replace(root, "WS").split("\n", 1)[-1]


def _prover_env(bench, name: str):
    env = bench.env(name)
    env.write("procs/PROVER.md", PROVER)
    return env


def _opened(env, marked: bool, extra: dict | None = None):
    """-> (the key, the first output): the run opened on the PROVER door."""
    variables = {"PP_DOOR": "PROVER.md", **(extra or {})}
    if marked:
        variables.update(MARK)
    out = cli(env.engine, "-new", cwd=env.root, env=variables)
    found = KEY.search(out.stdout)
    return (found.group(1) if found else ""), out


def _to_proof(env, key: str, marked: bool):
    """-> the output that asks the proof: the door's WORK closed by a bare call."""
    return cli(env.engine, key, cwd=env.root, env=MARK if marked else None)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- (a) the agent's bare call refuses ------------------------------------------------------------
    one = _prover_env(bench, "pa-bare")
    key, opened = _opened(one, marked=True)
    asked = _to_proof(one, key, marked=True)
    before = persistence.slot_of(one.made, key).read_bytes()
    bare = cli(one.engine, key, cwd=one.root)
    if (opened.returncode == 0 and key and "proof" in asked.stdout and bare.returncode == 2
            and "principal-advances" in bare.stderr and "▌" not in bare.stdout
            and persistence.slot_of(one.made, key).read_bytes() == before):
        held("(a) the agent's bare call refuses", f"run {key}: `./pp {key}` without the mark -- "
             "principal-advances, exit 2, no block, the slot byte-identical")
    else:
        failures.append(f"  ✗ (a) the bare call             rc={bare.returncode} {bare.stderr[-200:]!r} "
                        f"asked={'proof' in asked.stdout} {opened.stderr[-200:]!r}")

    # --- (b) the agent's value: judged at once, its output held ----------------------------------------
    pointer_before, kinds_before = _pointer(one, key), _kinds(one, key)
    valued = cli(one.engine, key, "-", cwd=one.root, stdin=GOOD)
    kinds_after = _kinds(one, key)
    new_kinds = kinds_after[len(kinds_before):]
    slot_held = _slot(one, key).get("held") or {}
    if (valued.returncode == 0 and valued.stdout.strip().startswith("pp: value judged")
            and valued.stdout.count("\n") <= 1 and "▌" not in valued.stdout
            and new_kinds[:1] == ["answer"] and "held" in new_kinds and "block" in new_kinds
            and _pointer(one, key) != pointer_before
            and slot_held.get("matter") and slot_held.get("chars", 0) > 0
            and slot_held.get("act") == "value"):
        held("(b) the value is judged at once, its output held", f"one line back ({valued.stdout.strip()!r}); "
             f"trace {new_kinds}; the frames moved; `held` at the slot, {slot_held.get('chars')} chars")
    else:
        failures.append(f"  ✗ (b) the held output           rc={valued.returncode} {valued.stdout[-200:]!r} "
                        f"kinds={new_kinds} moved={_pointer(one, key) != pointer_before} held={bool(slot_held)}")

    # --- (c) a second value and a gesture bounce while an output is held --------------------------------
    frozen = persistence.slot_of(one.made, key).read_bytes()
    kinds_held = _kinds(one, key)
    again = cli(one.engine, key, "-", cwd=one.root, stdin=GOOD)
    gesture = cli(one.engine, key, "-s", "pp-nothing", cwd=one.root)
    if (again.returncode == 0 and gesture.returncode == 0
            and all("held for your principal" in out.stdout and "▌" not in out.stdout for out in (again, gesture))
            and persistence.slot_of(one.made, key).read_bytes() == frozen and _kinds(one, key) == kinds_held):
        held("(c) a second value and a `-s` bounce", "one line each, rc 0, the slot byte-identical, nothing traced")
    else:
        failures.append(f"  ✗ (c) the bounces               rc={again.returncode}/{gesture.returncode} "
                        f"{again.stdout[-120:]!r} {gesture.stdout[-120:]!r} same={persistence.slot_of(one.made, key).read_bytes() == frozen}")

    # --- (d) the principal's bare call serves the held output ----------------------------------------------
    served = cli(one.engine, key, cwd=one.root, env=MARK)
    advances = [e for e in _trace(one, key) if e.get("kind") == "advance"]
    if (served.returncode == 0 and "▌" in served.stdout and f"run {key}" in served.stdout
            and "held" not in _slot(one, key) and advances and advances[-1].get("held") is True):
        held("(d) the principal's call serves the held output", f"the block after the proof rendered, "
             "`held` gone from the slot, traced `advance` held: true")
    else:
        failures.append(f"  ✗ (d) the release               rc={served.returncode} {served.stdout[:200]!r} "
                        f"held={'held' in _slot(one, key)} advances={advances[-1:]}")

    # --- (e) a faulty proof: the REPAIR held, then served ----------------------------------------------------
    two = _prover_env(bench, "pa-repair")
    key2, _ = _opened(two, marked=True)
    _to_proof(two, key2, marked=True)
    faulty = cli(two.engine, key2, "-", cwd=two.root, stdin="[]")
    repaired = cli(two.engine, key2, cwd=two.root, env=MARK)
    kinds2 = _kinds(two, key2)
    if (faulty.returncode == 0 and "value judged" in faulty.stdout and "repair" in kinds2
            and repaired.returncode == 0 and "REPAIR" in repaired.stdout and "DEVIATION" in repaired.stdout):
        held("(e) a faulty proof: the REPAIR is held, then served", "`[]` on Z1: the trace says repair, the "
             "agent gets its one line, the principal's call renders the REPAIR block")
    else:
        failures.append(f"  ✗ (e) the held repair           rc={faulty.returncode}/{repaired.returncode} "
                        f"kinds={kinds2[-4:]} {repaired.stdout[-200:]!r}")

    # --- (f) no value where one is due: today's repair at the principal's call -------------------------------
    three = _prover_env(bench, "pa-empty")
    key3, _ = _opened(three, marked=True)
    _to_proof(three, key3, marked=True)
    empty = cli(three.engine, key3, cwd=three.root, env=MARK)
    if empty.returncode == 0 and "REPAIR" in empty.stdout and "repair" in _kinds(three, key3):
        held("(f) no value given: today's empty-answer repair", "the principal's bare call on a due proof "
             "renders the REPAIR, as a bare call does in the LLM's mode")
    else:
        failures.append(f"  ✗ (f) the empty answer          rc={empty.returncode} {empty.stdout[-200:]!r}")

    # --- (g) the frontier: the principal's call carries the message -------------------------------------------
    parked = served
    hops = 0
    while "FINAL" not in _closing(parked.stdout) and hops < 6:     # the door closed: the turn to its FINAL
        parked = cli(one.engine, key, cwd=one.root, env=MARK)
        hops += 1
    frontier = persistence.frontier_of(_slot(one, key))
    spoken = cli(one.engine, key, "the principal's next word", cwd=one.root, env=MARK)
    prompts = [e for e in _trace(one, key) if e.get("kind") == "prompt"]
    if (frontier and spoken.returncode == 0 and "▌" in spoken.stdout
            and prompts and prompts[-1].get("text") == "the principal's next word"):
        held("(g) the frontier: the message rides the principal's call", f"parked after {hops} hop(s), "
             "the marked call with a text traced `prompt`, the next exchange opened")
    else:
        failures.append(f"  ✗ (g) the frontier              frontier={frontier} rc={spoken.returncode} "
                        f"prompts={prompts[-1:]} {spoken.stdout[-160:]!r}")

    # --- (h) a marked call with a text over a held output refuses ---------------------------------------------
    four = _prover_env(bench, "pa-held-text")
    key4, _ = _opened(four, marked=True)
    _to_proof(four, key4, marked=True)
    cli(four.engine, key4, "-", cwd=four.root, stdin=GOOD)
    over = cli(four.engine, key4, "some text", cwd=four.root, env=MARK)
    if over.returncode == 2 and "output-held" in over.stderr and _slot(four, key4).get("held"):
        held("(h) a text over a held output refuses", "output-held, exit 2, the hold intact")
    else:
        failures.append(f"  ✗ (h) output-held               rc={over.returncode} {over.stderr[-160:]!r}")

    # --- (i) a chunk waiting ---------------------------------------------------------------------------------
    long = bench.env("pa-chunks")
    long.write("SETTINGS.md", CAP)
    long.write("LONG.md", PAST)
    long.write("procs/LONGRUN.md", LONGRUN)
    cut = cli(long.engine, "-new", cwd=long.root, env={**MARK, "PP_DOOR": "LONGRUN.md"})
    key5 = KEY.search(cut.stdout).group(1) if KEY.search(cut.stdout) else ""
    pending = key5 and persistence.pending_of(persistence.slot_of(long.made, key5)).get("matter")
    bare5 = cli(long.engine, key5, cwd=long.root) if key5 else None
    valued5 = cli(long.engine, key5, "a value", cwd=long.root) if key5 else None
    chunk = cli(long.engine, key5, cwd=long.root, env=MARK) if key5 else None
    if (pending and bare5.returncode == 2 and "principal-advances" in bare5.stderr
            and valued5.returncode == 0 and "chunk-pending" in valued5.stdout
            and chunk.returncode == 0 and "▌" in chunk.stdout):
        held("(i) a chunk waiting", "the agent's bare call refuses, its value bounces chunk-pending, the "
             "principal's bare call serves the chunk")
    else:
        failures.append(f"  ✗ (i) the chunk                 pending={bool(pending)} "
                        f"{bare5 and bare5.returncode}/{valued5 and valued5.returncode}/{chunk and chunk.returncode} "
                        f"{bare5 and bare5.stderr[-120:]!r}")

    # --- (j) the soft -new -----------------------------------------------------------------------------------
    five = _prover_env(bench, "pa-new")
    key6, _ = _opened(five, marked=True)                     # mid-exchange: its WORK stands
    slots_before = len(persistence.slots(five.made))
    soft = cli(five.engine, "-new", cwd=five.root)
    slots_after_soft = len(persistence.slots(five.made))
    marked_new = cli(five.engine, "-new", cwd=five.root, env=MARK)
    key7 = KEY.search(marked_new.stdout).group(1) if KEY.search(marked_new.stdout) else ""
    # both runs to their FINAL: the principal's bare calls, a proof asked piped by the agent
    for k in (key6, key7):
        hops = 0
        while k and hops < 8 and not persistence.frontier_of(_slot(five, k)):
            out = cli(five.engine, k, cwd=five.root, env=MARK)
            if CODES.search(out.stdout) and "heredoc" in out.stdout:
                cli(five.engine, k, "-", cwd=five.root, stdin=GOOD)
            hops += 1
    parked_all = all(persistence.frontier_of(_slot(five, k)) for k in (key6, key7) if k)
    opened_after = cli(five.engine, "-new", cwd=five.root)
    if (soft.returncode == 0 and "a run is already open" in soft.stdout and key6 in soft.stdout
            and "▌" not in soft.stdout and slots_after_soft == slots_before
            and marked_new.returncode == 0 and key7 and key7 != key6
            and parked_all and opened_after.returncode == 0 and KEY.search(opened_after.stdout)):
        held("(j) the soft -new", f"unmarked `-new` beside {key6} mid-exchange: one line, no slot; marked, "
             f"it opened {key7}; both parked on their FINAL, the unmarked `-new` opens a run")
    else:
        failures.append(f"  ✗ (j) the soft -new             rc={soft.returncode} {soft.stdout[-160:]!r} "
                        f"slots={slots_after_soft}/{slots_before} key7={key7!r} "
                        f"parked={parked_all} after={opened_after.returncode}")

    # --- (k) a whole exchange conducted by the launcher witness -----------------------------------------------
    six = _prover_env(bench, "pa-launcher")

    def agent(output: str, key: str) -> None:
        """The agent witness: reads the served output; a proof asked is piped, unmarked."""
        codes = CODES.search(output)
        if codes and "heredoc" in output:
            proof = json.dumps([{"code": c, "evidence": "the witness said it plainly", "verdict": "ok"}
                                for c in codes.group(1).split()])
            cli(six.engine, key, "-", cwd=six.root, stdin=proof)

    outputs = []
    first = cli(six.engine, "-new", cwd=six.root, env={**MARK, "PP_DOOR": "PROVER.md"})
    key8 = KEY.search(first.stdout).group(1) if KEY.search(first.stdout) else ""
    outputs.append(first.stdout)
    calls = 0
    while key8 and calls < 10 and not persistence.frontier_of(_slot(six, key8)):
        agent(outputs[-1], key8)
        outputs.append(cli(six.engine, key8, cwd=six.root, env=MARK).stdout)
        calls += 1
    # a closing that MOVES the run carries no command; one that asks the tool a value keeps it
    commanded = [i for i, out in enumerate(outputs)
                 if ("CONTINUE" in _closing(out) or "FINAL" in _closing(out)) and "./pp" in _closing(out)
                 and not any(word in _closing(out) for word in ("stdin", "<your-choice>", "<output>"))]
    proofs = sum(1 for e in _trace(six, key8) if e.get("kind") == "answer")
    if key8 and persistence.frontier_of(_slot(six, key8)) and not commanded and proofs >= 1:
        held("(k) a whole exchange by the launcher", f"run {key8}: {len(outputs)} outputs served, {calls} "
             f"principal call(s), {proofs} value(s) piped unmarked, parked on its FINAL; no CONTINUE or "
             "FINAL carries `./pp`")
    else:
        failures.append(f"  ✗ (k) the launcher's exchange   key={key8!r} parked={key8 and persistence.frontier_of(_slot(six, key8))} "
                        f"commanded={commanded} proofs={proofs} calls={calls} "
                        f"{[_closing(outputs[i]) for i in commanded]!r}")

    # --- (l) the same matter in both modes, the closings apart --------------------------------------------------
    llm, led = _prover_env(bench, "pa-llm"), _prover_env(bench, "pa-led")
    key9, _ = _opened(llm, marked=False)
    _to_proof(llm, key9, marked=False)
    returned = cli(llm.engine, key9, "-", cwd=llm.root, stdin=GOOD)
    key10, _ = _opened(led, marked=True)
    _to_proof(led, key10, marked=True)
    cli(led.engine, key10, "-", cwd=led.root, stdin=GOOD)
    delivered = cli(led.engine, key10, cwd=led.root, env=MARK)
    same = _matter(returned.stdout, key9, str(llm.root)) == _matter(delivered.stdout, key10, str(led.root))
    if (returned.returncode == 0 and delivered.returncode == 0 and same
            and "./pp" in _closing(returned.stdout) and "./pp" not in _closing(delivered.stdout)
            and "▌" in delivered.stdout):
        held("(l) the same matter in both modes", "the tool return and the served output agree line for line "
             "under the heading; the LLM's closing carries the command, the principal's its note")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(_matter(returned.stdout, key9, str(llm.root)).splitlines(),
                                                       _matter(delivered.stdout, key10, str(led.root)).splitlines()))
                      if a != b), None)
        failures.append(f"  ✗ (l) the matter                same={same} drift={drift} "
                        f"{_closing(returned.stdout)!r} {_closing(delivered.stdout)!r}")

    # --- (m) the LLM's mode is today's ---------------------------------------------------------------------
    advanced = cli(llm.engine, key9, cwd=llm.root)
    if ("▌" in returned.stdout and "held" not in _slot(llm, key9) and advanced.returncode == 0
            and "▌" in advanced.stdout and "held" not in _kinds(llm, key9) and "advance" not in _kinds(llm, key9)):
        held("(m) the LLM's mode is today's", "the value's block came back in the tool return, nothing held, "
             "the bare call advanced; no `held` nor `advance` on the trace")
    else:
        failures.append(f"  ✗ (m) the LLM's mode            rc={advanced.returncode} kinds={_kinds(llm, key9)[-5:]}")
    return 0
