"""Scenario `front-when-changed` -- the front is served at the boot and when the table changed
since it was last SUPPLIED to the run (plan steering, phase le-proc-next, batch
le-front-quand-il-change):
- turn 1 (a boot) serves the table; turn 2 without a write serves the one line
- a step delivered, a thread opened, a thread closed, a step reordered during a turn serve the
  table at that turn; a thread renamed and a step amended alone do not: the line
- a write made BETWEEN two turns -- another session's, the operator's hand -- serves the table
  at the next turn: what counts is the table last supplied, never the turn's beginning
- a compaction declared during a turn serves the table
- two runs: a write made by one is due to the other at its next turn, once
- `status` without the flag renders the table whatever the snapshot
- the snapshot record holds, per run, the worked_at of every open thread as last supplied,
  and the exchange it was supplied at
Every turn is played by the CONSOLE (KFQ2); the writes by the vendored keeper, in a subprocess.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from tests.harness import load_script


def _keeper_script(meta: Path) -> Path:
    return next((meta / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"


def _console(meta: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run([str(meta.parent / "pp"), *args], input=stdin, capture_output=True, text=True,
                          cwd=str(meta.parent))
    return done.stdout + done.stderr


def _keeper(meta: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run([sys.executable, str(_keeper_script(meta)), *args], input=stdin, capture_output=True,
                          text=True, cwd=str(meta.parent))
    return done.stdout + done.stderr


def _to_final(meta: Path, key: str, outputs: list[str]) -> list[str]:
    """Plays the exchange to its FINAL: a proof answered n/a, IMPROVE answered `none`."""
    for _ in range(30):
        last = outputs[-1]
        if "the bare call alone serves them" in last:
            outputs.append(_console(meta, key))
            continue
        if "▶ FINAL" in last or "▶ END" in last:
            break
        judged = re.search(r"INFER proof \[([^\]]*)\]", last)
        if judged:
            codes = judged.group(1).split() or ["none"]
            outputs.append(_console(meta, key, "-", stdin=json.dumps(
                [{"code": c, "evidence": "bench -- nothing to judge", "verdict": "n/a"} for c in codes])))
            continue
        if "IMPROVE{" in last:
            outputs.append(_console(meta, key, "none"))
            continue
        outputs.append(_console(meta, key))
    return outputs


def _turn(meta: Path, key: str | None, message: str = "a message", compacted: bool = False,
          during=None) -> tuple[str, list[str]]:
    """One exchange of a run, opened then played to its FINAL: -> (the key, every output). A
    message opens a later exchange; `compacted` declares a compaction once it is open; `during`
    is a gesture played while the exchange is open, before its blocks."""
    if key is None:
        first = _console(meta, "-new")
        key = first.split("run ", 1)[1].split()[0]
        outputs = [first]
    else:
        outputs = [_console(meta, key, message)]
        if compacted:
            outputs.append(_console(meta, key, "-compacted"))
    if during is not None:
        during()
    return key, _to_final(meta, key, outputs)


def _front(outputs: list[str], line: str) -> str:
    """-> what the `steering-threads` section carried at the first block that served it."""
    for one in outputs:
        if "INFORMATION — steering-threads" in one:
            return "table" if "| initiative | note | progress |" in one else "line" if line in one else "other"
    return "none"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("fwc", packages=("steering", "improvement"))
    meta = env.made
    line = load_script(_keeper_script(meta)).NOT_CHANGED     # the keeper's own line, never a literal here
    record = meta / ".sys" / "records" / "threads.json"
    _keeper(meta, "open", "le-fil-du-front", stdin="le-premier-pas | the first step\nle-second-pas | the second step\n")

    def state() -> dict:
        return json.loads(record.read_text(encoding="utf-8"))

    def tid_of(name: str) -> str:
        return next(tid for tid, one in state()["threads"].items() if one["name"] == name)

    front = tid_of("le-fil-du-front")
    first_step, second_step = state()["threads"][front]["steps"]

    # --- one run, the seven turns and a compaction ---------------------------------------------
    key, t1 = _turn(meta, None)
    _, t2 = _turn(meta, key, "turn 2, nothing written")
    plain = _console(meta, key, "-s", "pp-steering", "status")                       # KFQ3, at the turn's FINAL
    _, t3 = _turn(meta, key, "turn 3", during=lambda: _keeper(meta, "done", front, first_step))
    _, t4 = _turn(meta, key, "turn 4", during=lambda: _keeper(meta, "open", "le-fil-ouvert", stdin="un-pas | a step\n"))
    _, t5 = _turn(meta, key, "turn 5", during=lambda: _keeper(meta, "close", tid_of("le-fil-ouvert")))
    _, t6 = _turn(meta, key, "turn 6", during=lambda: _keeper(meta, "reorder", front, second_step, "1"))
    _, t7 = _turn(meta, key, "turn 7", during=lambda: (_keeper(meta, "rename", front, "le-fil-renomme"),
                                                       _keeper(meta, "amend", front, second_step, "a text amended")))
    _, t8 = _turn(meta, key, "turn 8, compacted", compacted=True)
    _keeper(meta, "attach", front, "--as", "le-troisieme-pas")      # BETWEEN two turns: another session, a hand
    _, t9 = _turn(meta, key, "turn 9, after a write between the turns")
    _, t10 = _turn(meta, key, "turn 10, nothing written")
    fronts = [_front(one, line) for one in (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10)]
    wanted = ["table", "line", "table", "table", "table", "table", "line", "table", "table", "line"]
    if fronts == wanted and "| initiative | note | progress |" in plain and "| le-fil-du-front |" in plain and "| threads |" not in plain:
        held("the front is served at the boot and when the table changed since last supplied",
             "turn 1 the table; turn 2 the one line; a step delivered, a thread opened, a thread closed, "
             "a step reordered during the turn: the table; a rename and an amend alone: the line; a "
             "compaction: the table; a write made between two turns: the table at the next turn, then the "
             "line -- and `status` without the flag renders the table at the line's turn")
    else:
        failures.append(f"  ✗ front when changed         {fronts} plain={'| initiative | note | progress |' in plain}")

    # --- two runs: what one writes is due to the other at its next turn, once --------------------
    key_b, b1 = _turn(meta, None)
    _, b2 = _turn(meta, key_b, "B turn 2, nothing written")
    _keeper(meta, "done", front, second_step)                        # run A's hand, between B's turns
    _, b3 = _turn(meta, key_b, "B turn 3, after A wrote")
    _, b4 = _turn(meta, key_b, "B turn 4, nothing written")
    _, a11 = _turn(meta, key, "A turn 11, after its own hand wrote")
    _, a12 = _turn(meta, key, "A turn 12, nothing written")
    two = [_front(one, line) for one in (b1, b2, b3, b4, a11, a12)]
    if two == ["table", "line", "table", "line", "table", "line"]:
        held("two runs, each supplied what it has not seen",
             "run B boots on the table, then the line; a write made between B's turns is due to B once, "
             "and to A at its next turn once -- each run compares with the table IT was last supplied")
    else:
        failures.append(f"  ✗ two runs                   {two}")

    # --- the snapshot record: per run, the open threads' worked_at as last supplied, and when ----
    seen_path = meta / ".sys" / "records" / "threads-seen.json"
    seen = json.loads(seen_path.read_text(encoding="utf-8")) if seen_path.is_file() else {}
    current = {tid: one["worked_at"] for tid, one in state()["threads"].items()}
    if (seen.get(key, {}).get("threads") == current and seen.get(key_b, {}).get("threads") == current
            and seen[key]["exchange"] == 11 and seen[key_b]["exchange"] == 3 and set(seen) <= {key, key_b}):
        held("the snapshot record",
             "`threads-seen.json` holds, for each run, the worked_at of every open thread as the table was "
             "last supplied to it and the exchange of that supply -- A at its 11th, B at its 3rd, both "
             "equal to the record now, no other run kept")
    else:
        failures.append(f"  ✗ the snapshot record        {seen}")
    return 0
