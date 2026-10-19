"""Scenario `steering-front-served` -- the front the console serves, and when:
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
- the threads are kept before the surface renders them: THREADS opens at the turn's end as a
  WORK step that offers the keeper, NEXT behind its section break, and a step delivered under
  THREADS reaches the table NEXT serves in the next output
Every turn is played by the CONSOLE; the writes by the vendored keeper, in a subprocess.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from tests.harness import support

S = support(__file__, "steering")


def _advance(meta: Path, key: str, last: str) -> str:
    """-> the next output: a proof answered n/a, anything else a bare call."""
    judged = re.search(r"INFER proof \[([^\]]*)\]", last)
    if judged:
        codes = judged.group(1).split() or ["none"]
        return S.console(meta, key, "-", stdin=json.dumps(
            [{"code": c, "evidence": "bench -- nothing to judge", "verdict": "n/a"} for c in codes]))
    return S.console(meta, key)


def _to_final(meta: Path, key: str, outputs: list[str]) -> list[str]:
    """Plays the exchange to its FINAL: a proof answered n/a."""
    for _ in range(30):
        last = outputs[-1]
        if "the bare call alone serves them" in last:
            outputs.append(S.console(meta, key))
            continue
        if "▶ FINAL" in last or "▶ END" in last:
            break
        outputs.append(_advance(meta, key, last))
    return outputs


def _turn(meta: Path, key: str | None, message: str = "a message", compacted: bool = False,
          during=None) -> tuple[str, list[str]]:
    """One exchange of a run, opened then played to its FINAL: -> (the key, every output). A
    message opens a later exchange; `compacted` declares a compaction once it is open; `during`
    is a gesture played while the exchange is open, before its blocks."""
    if key is None:
        first = S.console(meta, "-new")
        key = first.split("run ", 1)[1].split()[0]
        outputs = [first]
    else:
        outputs = [S.console(meta, key, message)]
        if compacted:
            outputs.append(S.console(meta, key, "-compacted"))
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
    env = bench.env("fwc", packages=("steering",))
    meta = env.made
    line = S.keeper_module(meta).NOT_CHANGED     # the keeper's own line, never a literal here
    record = meta / ".sys" / "records" / "threads.json"
    S.keeper(meta, "open", "le-fil-du-front", stdin="le-premier-pas | the first step\nle-second-pas | the second step\n")

    def state() -> dict:
        return json.loads(record.read_text(encoding="utf-8"))

    def tid_of(name: str) -> str:
        return next(tid for tid, one in state()["threads"].items() if one["name"] == name)

    front = tid_of("le-fil-du-front")
    first_step, second_step = state()["threads"][front]["steps"]

    # --- one run, the seven turns and a compaction ---------------------------------------------
    key, t1 = _turn(meta, None)
    _, t2 = _turn(meta, key, "turn 2, nothing written")
    plain = S.console(meta, key, "-s", "pp-steering", "status")                       # at the turn's FINAL
    _, t3 = _turn(meta, key, "turn 3", during=lambda: S.keeper(meta, "done", front, first_step))
    _, t4 = _turn(meta, key, "turn 4", during=lambda: S.keeper(meta, "open", "le-fil-ouvert", stdin="un-pas | a step\n"))
    _, t5 = _turn(meta, key, "turn 5", during=lambda: S.keeper(meta, "close", tid_of("le-fil-ouvert")))
    _, t6 = _turn(meta, key, "turn 6", during=lambda: S.keeper(meta, "reorder", front, second_step, "1"))
    _, t7 = _turn(meta, key, "turn 7", during=lambda: (S.keeper(meta, "rename", front, "le-fil-renomme"),
                                                       S.keeper(meta, "amend", front, second_step, "a text amended")))
    _, t8 = _turn(meta, key, "turn 8, compacted", compacted=True)
    S.keeper(meta, "attach", front, "--as", "le-troisieme-pas")      # BETWEEN two turns: another session, a hand
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
    S.keeper(meta, "done", front, second_step)                        # run A's hand, between B's turns
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

    # --- a third run: THREADS keeps the threads, NEXT renders them after -------------------------
    S.keeper(meta, "open", "le-fil-tenu", stdin="le-premier-pas | the first step\nle-second-pas | the second step\n")
    held_tid = tid_of("le-fil-tenu")
    output = S.console(meta, "-new")
    key_c = output.split("run ", 1)[1].split()[0]
    threads_output = ""
    for _ in range(20):
        if "THREADS{" in output:
            threads_output = output
            break
        output = _advance(meta, key_c, output)
    if (threads_output and "WORK" in threads_output and "pp-steering" in threads_output
            and "NEXT{" not in threads_output):
        held("THREADS is a WORK step, NEXT waits behind it",
             "the turn's end opens THREADS, which offers the keeper; the surface is not in its output")
    else:
        failures.append(f"  ✗ threads step               {threads_output[-300:]!r}")

    S.keeper(meta, "done", held_tid, state()["threads"][held_tid]["steps"][0])     # the induced work, under THREADS
    next_output = ""
    output = S.console(meta, key_c)
    for _ in range(10):
        if "NEXT{" in output:
            next_output = output
            break
        output = _advance(meta, key_c, output)
    row = next((one for one in next_output.splitlines() if one.startswith("| le-fil-tenu |")), "")
    if "1/2" in row and "`le-second-pas`" in row and "THREADS{" not in next_output.split("NEXT{", 1)[0][-200:]:
        held("the table NEXT copies is computed after the work",
             "a step delivered under THREADS reads delivered in the next output's table")
    else:
        failures.append(f"  ✗ fresh table                row={row!r}")
    return 0
