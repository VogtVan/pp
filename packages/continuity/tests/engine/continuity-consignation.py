"""Scenario `continuity-consignation` -- the agent consigns an operation whenever it holds one:
- no document of continuity opens after the work, whatever the effort: four exchanges
  under `light`, `medium` and `full`
- `pp-continuity` is offered at every turn's WORK: a `register` played there, in the middle
  of the exchange, writes one dated line
- through the console, a `register` played between two calls leaves the run where it stood
- continuity's section of the standing orders: the vendored fragment's body in both
  compilations, gone at the boot after `package.continuity: off`, back after `on`
- the kit alone carries neither the section nor the offer

Two houses: the instance with continuity, and the kit alone for the absence.
"""
from __future__ import annotations

import json
from pathlib import Path

from conductor import contributions
from conductor.core.errors import Refusal
from tests.harness import na_proof, session_of, support

C = support(__file__, "continuity")

WORK_STEP = "WORK any => words"       # the pending step an agent works from
MARBLES = ("system.md", "system.common.md")
EFFORTS = ("light", "medium", "full")


def _bundle(meta: Path) -> Path:
    return next((meta / ".sys" / "vendor").glob("continuity@*"))


def _section(meta: Path) -> str:
    """-> the body of the vendored `system/SYSTEM.COMMON.md`, its front matter dropped."""
    fragment = _bundle(meta) / "system" / "SYSTEM.COMMON.md"
    if not fragment.is_file():
        return ""
    return fragment.read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()


def _marbles(meta: Path) -> list[str]:
    return [(meta / ".sys" / name).read_text(encoding="utf-8") for name in MARBLES]


def _offered(conductor, name: str) -> bool:
    """-> whether the current output offers `name`, at one segment or at several."""
    try:
        return conductor.route(name) is not None
    except Refusal as refused:
        return refused.code == "address-ambiguous"


def _exchanges(env, key: str, count: int, at_work=None):
    """Drives `count` exchanges after the boot; -> the block each exchange rendered right
    after the work (where a turn.end contributor would open). `at_work(n, conductor)` is
    called while the n-th WORK is the current output."""
    def to_work(block):
        """Advances to the turn's WORK: one step per block under `full`, a proof answered n/a."""
        for _ in range(12):
            if block is None or block.command == "WORK":
                return block
            block = env.conductor(key).submit(na_proof(block) if block.judged else "")
        return block

    after_work = []
    opener = env.conductor(key)
    to_work(opener.start(opener.boot("BOOT.md")))
    for n in range(1, count + 1):
        if n > 1:
            to_work(env.conductor(key).submit("a message"))   # the operator's message: the WORK
        if at_work is not None:
            at_work(n, env.conductor(key))
        block = env.conductor(key).submit("")        # past the work
        after_work.append(block)
        pending = block
        while pending is not None and pending.command != "INFER" and not pending.wait:
            pending = env.conductor(key).submit("")
        if pending is not None and pending.command == "INFER":
            env.conductor(key).submit(na_proof(pending))   # the proof piped n/a: AWAIT
    return after_work


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("consignation", packages=("continuity",))
    meta = env.made
    record = meta / ".sys" / "records" / "operations.jsonl"
    own = {one.stem for one in (_bundle(meta) / "procs").glob("*.md")}   # continuity's documents

    def setting(key: str, value: str) -> None:
        if not C.setting(env, key, value):
            failures.append(f"  ✗ setting                    {key} absent from SETTINGS.md")

    def entries() -> list[dict]:
        text = record.read_text(encoding="utf-8") if record.is_file() else ""
        return [json.loads(one) for one in text.splitlines() if one.strip()]

    # --- every effort: nothing of continuity after the work, the offer at every WORK ---------
    opened, offered, landed = {}, {}, {}
    for level in EFFORTS:
        setting("conduction_effort", level)
        seen = []

        def at_work(n, conductor, level=level, seen=seen):
            routed = _offered(conductor, "pp-continuity")
            rc, _, _ = contributions.run_skill(meta, "pp-continuity", ["register", f"{level} {n}"])
            seen.append((routed, rc))

        blocks = _exchanges(env, level, 4, at_work)
        opened[level] = [b.document for b in blocks if b is not None and b.document in own]
        offered[level] = [one for one, _ in seen]
        landed[level] = [one["entry"] for one in entries() if one["entry"].startswith(level)]
    if all(opened[level] == [] for level in EFFORTS):
        held("nothing of continuity opens after the work", "four exchanges under light, medium and full: "
             f"the block after the work is never one of {sorted(own)}")
    else:
        failures.append(f"  ✗ after the work             {opened}")
    if (all(offered[level] == [True] * 4 for level in EFFORTS)
            and all(landed[level] == [f"{level} {n}" for n in range(1, 5)] for level in EFFORTS)):
        held("pp-continuity at every WORK, the line lands", "routed at each of the twelve WORKs; each `register` "
             "played there writes one dated line, in order")
    else:
        failures.append(f"  ✗ offer and register         offered={offered} landed={landed}")
    setting("conduction_effort", "none")

    # --- through the console: a register between two calls leaves the run as it stood -------
    reached = WORK_STEP in env.cli("-new").stdout
    key = session_of(meta).name[len("session-"):-len(".json")]
    for _ in range(12):
        if reached:
            break
        reached = WORK_STEP in env.cli(key).stdout
    before, count = session_of(meta).read_bytes(), len(entries())
    consigned = env.cli(key, "-s", "pp-continuity", "register", "between two calls")
    steady = session_of(meta).read_bytes() == before
    lines = entries()
    if (reached and consigned.returncode == 0 and steady and len(lines) == count + 1
            and lines[-1]["entry"] == "between two calls" and lines[-1]["at"]):
        held("a register between two calls moves nothing", "the console's `-s pp-continuity register` at a WORK: "
             "one dated line more, the run's session byte for byte the same")
    else:
        failures.append(f"  ✗ console register           work={reached} rc={consigned.returncode} steady={steady} "
                        f"lines={len(lines)}/{count} {consigned.stderr[-120:]!r}")

    # --- the section of the standing orders, switched off and back on -----------------------
    section = _section(meta)
    present = bool(section) and all(section in one for one in _marbles(meta))
    setting("package.continuity", "off")
    env.cli("-new")
    gone = bool(section) and not any(section in one for one in _marbles(meta))
    setting("package.continuity", "on")
    env.cli("-new")
    back = bool(section) and all(section in one for one in _marbles(meta))
    if present and gone and back:
        held("the section rides the standing orders", f"the vendored fragment's body ({len(section)} c) in "
             f"{' and '.join(MARBLES)}; gone at the boot after `off`, back after `on`")
    else:
        failures.append(f"  ✗ the section                fragment={bool(section)} present={present} "
                        f"off={gone} on={back}")

    # --- the kit alone: no section, no offer --------------------------------------------------
    bare = bench.env("consignation-kit")
    routes = []
    _exchanges(bare, "k", 2, lambda n, conductor: routes.append(_offered(conductor, "pp-continuity")))
    if routes == [False, False] and section and not any(section in one for one in _marbles(bare.made)):
        held("the kit alone knows no consignation", "two WORKs without the pp-continuity offer, "
             "no continuity section in either compilation")
    else:
        failures.append(f"  ✗ kit alone                  routes={routes}")
    return 0
