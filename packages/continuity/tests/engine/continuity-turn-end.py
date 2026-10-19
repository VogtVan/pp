"""Scenario `continuity-turn-end` -- the consignation attaches to the turn:
- OPERATIONS opens at `turn.end` when its guard is due: the n-th completed exchange,
  nothing before; the kit alone never
- the block opens AFTER the work's own output, with `pp-continuity` offered: the
  consignation lands in the record from there
- the order at the socket is the requires topology then the name, the instance's own last
- through the console, call by call: the work, a gesture, the closing call that opens
  OPERATIONS, the consignation -- the line lands; a gesture played between the block and
  the consignation leaves the offer alive; `continuity_memory_frequency: 0` and the same
  calls open none. The subject there is the SEQUENCE, so the calls go through the console:
  in process the flow crosses several steps at once.

Two houses: the instance with continuity, and the kit alone for the absence.
"""
from __future__ import annotations

import json

from conductor import compiling, contributions, instance, render
from tests.harness import na_proof, session_of, support

C = support(__file__, "continuity")

WORK_STEP = "WORK any => response"       # the pending step an agent works from


def _exchanges(env, count: int, message: str = "a message", probe=None):
    """Drives `count` exchanges after the boot; -> the block each exchange rendered
    right after the work (where a turn.end contributor would open). `probe(n, block)`
    is called there, while that output is the current one."""
    key = "t"
    after_work = []
    opener = env.conductor(key)
    opener.start(opener.boot("BOOT.md"))            # the boot fuses up to the WORK step
    for n in range(1, count + 1):
        if n > 1:
            env.conductor(key).submit(message)       # the operator's message: the WORK
        block = env.conductor(key).submit("")        # past the work: what turn.end opens
        after_work.append(block)
        if probe is not None:
            probe(n, block)
        pending = block
        while pending is not None and pending.command != "INFER" and not pending.wait:
            pending = env.conductor(key).submit("")  # a contributor's own step, then the checkpoint
                                                     # -- or the frontier itself: a vanilla member owes no proof
        if pending is not None and pending.command == "INFER":
            env.conductor(key).submit(na_proof(pending))   # the proof piped n/a: FINAL
    return after_work


def _opens_operations(block) -> bool:
    return block is not None and "▸ OPERATIONS{" in render(block)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("turnend", packages=("continuity",))
    record = env.made / ".sys" / "records" / "operations.jsonl"

    def setting(key: str, value: str) -> None:
        if not C.setting(env, key, value):
            failures.append(f"  ✗ setting                    {key} absent from SETTINGS.md")

    def entries() -> list[dict]:
        text = record.read_text(encoding="utf-8") if record.is_file() else ""
        return [json.loads(one) for one in text.splitlines() if one.strip()]

    # --- four exchanges at the preset cadence, a witness attached beside --------------------
    env.write("procs/ZWITNESS.md",
              "---\nname: ZWITNESS\nkind: proc\ndescription: a witness attached at turn.end\n"
              "attach: turn.end\noutput: line\nproc: |\n  WORK\n---\n\nZWITNESS says hi\n")
    compiling.build_tools(env.made)
    order = instance.attached(env.made, "turn.end")
    seen, sequence = {}, []

    def probe(n, block):
        if n != 4:
            return
        c = env.conductor("t")
        routed = c.route("pp-continuity")             # ONE reader of what is offered: the offer map
        before = entries()
        rc, _, err = contributions.run_skill(
            env.made, "pp-continuity", ["register", "the consignation lands after the work"])
        seen.update(shown=render(block), routed=routed, before=before, rc=rc, err=err, lines=entries())
        sequence.append(block.document)                               # the first contributor's block
        sequence.append(env.conductor("t").submit("").document)       # the next advance: the second

    opened = [_opens_operations(b) for b in _exchanges(env, 4, probe=probe)]
    if opened == [False, False, False, True]:
        held("OPERATIONS opens at the n-th completed exchange",
             "frequency 3 (the effort's preset): exchanges 1-3 silent, the 4th opens OPERATIONS at turn.end")
    else:
        failures.append(f"  ✗ operation cadence          {opened}")
    if (seen and "pp-continuity" in seen["shown"] and seen["routed"] is not None and seen["rc"] == 0
            and seen["before"] == [] and len(seen["lines"]) == 1
            and seen["lines"][0]["entry"] == "the consignation lands after the work"):
        held("the consignation lands from the block after the work",
             "the OPERATIONS block offers pp-continuity (routed on the fused output); `register` writes ONE dated line")
    else:
        failures.append(f"  ✗ consignation lands         routed={seen.get('routed') is not None} "
                        f"rc={seen.get('rc')} {str(seen.get('err', ''))[-80:]!r} lines={len(seen.get('lines', []))}")
    if order == ("OPERATIONS.md", "ZWITNESS.md") and sequence == ["OPERATIONS", "ZWITNESS"]:
        held("the order at turn.end is topology then name, the instance last",
             "continuity's OPERATIONS opens before the instance's ZWITNESS, each in its own output -- no rank declared anywhere")
    else:
        failures.append(f"  ✗ order at turn.end          {order} {sequence}")
    (env.made / "procs" / "ZWITNESS.md").unlink()
    compiling.build_tools(env.made)               # the witness leaves: the console walks plain turns

    # --- through the console: the turn walked one call at a time ----------------------------
    setting("continuity_memory_frequency", "1")
    env.cli("-new")
    key = session_of(env.made).name[len("session-"):-len(".json")]
    said: list[str] = []

    def to_work(bound: int = 12) -> bool:
        """Bare calls until a turn's WORK stands again, one turn having closed: where
        an agent starts working, and where the consignation becomes due."""
        closed = False
        for _ in range(bound):
            out = env.cli(key).stdout
            said.append(out)
            closed = closed or "FINAL" in out
            if closed and WORK_STEP in out:
                return True
        return False

    reached = to_work()
    before = session_of(env.made).read_bytes()
    worked = env.cli(key, "-s", "pp-continuity", "recall", "last", "3")   # the agent's own work
    steady = session_of(env.made).read_bytes() == before
    closing = env.cli(key)                    # the call that closes the work
    consigned = env.cli(key, "-s", "pp-continuity", "register", "the turn answered")
    landed = entries()
    if (reached and worked.returncode == 0 and steady
            and "▸ OPERATIONS{1/1}" in closing.stdout and "pp-continuity" in closing.stdout
            and consigned.returncode == 0 and "consigned" in consigned.stdout
            and landed and landed[-1]["entry"] == "the turn answered"):
        held("the consignation lands in the lived sequence",
             "the work, a gesture that moves nothing, the closing call that opens "
             "OPERATIONS with `pp-continuity` offered, then the consignation -- the record "
             f"holds {len(landed)} line(s), the last one this turn's")
    else:
        failures.append(f"  ✗ la sequence                 work={reached}/{worked.returncode}/{steady} "
                        f"open={closing.stdout[:60]!r} consign={consigned.returncode} {len(landed)}")

    again = to_work()
    env.cli(key)                              # OPERATIONS opens again, the cadence is 1
    between = env.cli(key, "-s", "pp-continuity", "recall", "last", "1")  # played AFTER the block
    second = env.cli(key, "-s", "pp-continuity", "register", "the next turn answered")
    landed = entries()
    if (again and between.returncode == 0 and second.returncode == 0
            and "consigned" in second.stdout and landed and landed[-1]["entry"] == "the next turn answered"):
        held("a gesture between the block and the consignation costs nothing",
             "the OPERATIONS offer is still there after a routed gesture, and the second "
             "line lands -- the order of the agent's calls no longer decides")
    else:
        failures.append(f"  ✗ le geste intercale          {again}/{between.returncode}/"
                        f"{second.returncode} {second.stdout[:80]!r}")

    # --- the key at 0: the same calls, never -------------------------------------------------
    setting("continuity_memory_frequency", "0")
    said.clear()
    walked = sum(to_work() for _ in range(4))
    if walked == 4 and not any("▸ OPERATIONS{" in out for out in said):
        held("the key at 0 never opens OPERATIONS", "continuity_memory_frequency 0 (the bench's "
             "effort is none: the key rules): four turns walked by the console, no block")
    else:
        failures.append(f"  ✗ key at 0                   turns={walked} "
                        f"operations={sum('▸ OPERATIONS{' in out for out in said)}")

    # --- the kit alone: never, and no offer --------------------------------------------------
    renders = [render(b) for b in _exchanges(bench.env("turnend-kit"), 4) if b is not None]
    if not any("OPERATIONS" in one or "pp-continuity" in one for one in renders):
        held("the kit alone consigns nothing", "four exchanges: no OPERATIONS block, no pp-continuity offer")
    else:
        failures.append("  ✗ kit alone                  OPERATIONS or pp-continuity appeared")
    return 0
