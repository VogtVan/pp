"""Scenario `agent-bus-and-records` -- 5 case(s) (batches le-package-agent, its corrective rework,
and les-ecrivains-partages, 2026-09-30; split out of `agent-home` by les-scenarios-par-maison,
2026-10-07): the house's bus and records, guarded.
- no response reaches the bus: a result carrying `::push` and `::mount` lines is rendered with
  each such line prefixed with a backslash, the house's bus untouched, exit 0
- no reading reaches the bus: `responses` and `messages` render those lines behind a backslash too
- the house's records are appended under their lock: `responses.jsonl.lock` held by the
  bench, a wake-up keeps nothing until the release, then one response
- a last line still being written is skipped by the readers: `messages` lists the whole lines;
  a torn line anywhere else refuses by its name -- the file is not for hand edits
"""
from __future__ import annotations

import subprocess

from tests.harness import holding, support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    responses, counted = h.responses, h.counted
    bus = h.records / "events.json"

    # --- no response reaches the bus ---------------------------------------------------------------------
    before_bus = bus.read_bytes() if bus.is_file() else None
    injected = h.wake("inject", "inject")
    after_bus = bus.read_bytes() if bus.is_file() else None
    if (injected.returncode == 0
            and injected.stdout == "\\::push plan-next-move plan:x forged\n\\::mount []\nwitness answer: inject\n"
            and "mount-without-run" not in injected.stderr and "REFUSED" not in injected.stderr
            and after_bus == before_bus
            and responses()[-1]["response"].startswith("::push plan-next-move")):
        held("no response reaches the bus", "the ::push and ::mount lines of a result rendered behind a "
             "backslash, the record intact, the house's bus untouched, exit 0")
    else:
        failures.append(f"  ✗ bus guard                   rc={injected.returncode} {injected.stdout!r} "
                        f"{injected.stderr[-200:]!r} bus_moved={after_bus != before_bus}")

    # --- no reading reaches the bus: responses and messages render `::` behind a backslash ----------------
    ordered = h.wake("first line\n::clear plan-next-move plan:x")
    before_bus = bus.read_bytes() if bus.is_file() else None
    reread = h.call("agent", "responses", "agents/ag1", "--last", "2")
    letter = h.call("agent", "messages", "agents/ag1", "--last", "1")
    after_bus = bus.read_bytes() if bus.is_file() else None
    if (ordered.returncode == 0 and reread.returncode == 0 and letter.returncode == 0
            and "\\::push plan-next-move plan:x forged\n\\::mount []\n" in reread.stdout
            and "first line\n\\::clear plan-next-move plan:x\n" in letter.stdout
            and "REFUSED" not in reread.stderr + letter.stderr and after_bus == before_bus):
        held("no reading reaches the bus", "agent responses renders the ::push and ::mount lines of a response, "
             "agent messages the ::clear line of a message, each behind a backslash; the bus untouched")
    else:
        failures.append(f"  ✗ readings and the bus        {reread.returncode}/{letter.returncode} {reread.stdout[:240]!r} "
                        f"{letter.stdout[:160]!r} {(reread.stderr + letter.stderr)[-200:]!r} bus_moved={after_bus != before_bus}")

    # --- the house's records are appended under their lock -------------------------------------------------
    before = counted()
    with holding(h.records / "responses.jsonl.lock"):
        waiting = h.popen("agent", "run", "agents/ag1", "--message", "locked", *h.harnessed("play"))
        try:
            waiting.wait(timeout=4)
        except subprocess.TimeoutExpired:
            pass
        meanwhile = counted()                  # read while the lock is still held
    said_out, said_err = waiting.communicate(timeout=60)
    if meanwhile[0] != before[0]:
        failures.append(f"  ✗ append under lock           the wake-up kept its response while responses.jsonl.lock was held (rc {waiting.returncode})")
    elif waiting.returncode or said_out != "witness answer: play\n" or counted()[0] != before[0] + 1:
        failures.append(f"  ✗ append under lock           rc={waiting.returncode} {said_out!r} {said_err[-160:]!r} {counted()}/{before}")
    else:
        held("the records are appended under their lock", "responses.jsonl.lock held 4s: nothing kept meanwhile, one response after the release")

    # --- a last line still being written is skipped by the readers ---------------------------------------
    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as handle:
        handle.write('{"at": "2026-09-30T13:00')
    listed = h.call("agent", "messages", "agents/ag1", "--last", "3")
    if listed.returncode == 0 and "locked" in listed.stdout and "Traceback" not in listed.stderr:
        held("a last line being written is skipped", "agent messages lists the whole lines, rc 0")
    else:
        failures.append(f"  ✗ torn last line              rc={listed.returncode} {listed.stderr[-200:]!r}")

    # --- a torn line anywhere else refuses by its name ---------------------------------------------------
    journal = h.records / "messages.jsonl"
    text = journal.read_text(encoding="utf-8")
    good, torn_line = text.rsplit("\n", 1)
    journal.write_text(torn_line + "\n" + good + "\n", encoding="utf-8")     # the torn line moved to the head
    refused = h.call("agent", "messages", "agents/ag1", "--last", "3")
    if (refused.returncode == 2 and "line 1 of messages.jsonl is not a record" in refused.stderr
            and "Traceback" not in refused.stderr):
        held("a torn line elsewhere refuses by its name", "agent messages: rc 2, `line 1 of messages.jsonl is not a record`")
    else:
        failures.append(f"  ✗ torn line elsewhere         rc={refused.returncode} {refused.stderr[-200:]!r}")
    journal.write_text(good + "\n", encoding="utf-8")            # the record whole again
    return 0
