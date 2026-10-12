"""Scenario `agent-locks` -- 7 case(s) (batches le-verrou-de-reveil, 2026-09-30, les-ecrivains-partages,
le-verrou-de-la-machine and l-agent-detache; split out of `agent-home` by les-scenarios-par-maison,
2026-10-07): the wake lock, the machine's maintenance, the neighbours.
- the wake lock: a second wake-up of a run whose wake lock is held refuses `run-busy`, nothing
  launched, no record moved; `status` says `running (a wake-up plays)` and `list` counts it
- the launcher's lock spans the wake-up: held while the witness plays (it pauses), present and
  free after
- the house's `upgrade` refuses `maintenance-busy` while a pp process lives at the agent (the
  machine held shared through it), and while another maintenance holds the machine; the pins
  and the slot intact
- a wake-up under the machine's maintenance refuses `maintenance-in-progress` before any launch
- the neighbours line: a solo wake-up gets none; with another run's wake lock held, `--dry-run`
  composes `[runs under way: <key> since HH:MM « <head> »]` -- the local hour of the mark, the first
  line of its message --, a blank line, then the head of the message
- two wake-ups of one agent at once (`race`, a prompt file each): both answer 0, the later one
  reads the other in its neighbours line, the record keeps the bare messages
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime

from conductor import instance, persistence
from conductor.state import lock
from tests.harness import cli, holding, race, support

A = support(__file__, "agent")
HEAD = A.HEAD


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    keys, counted = h.keys, h.counted
    h.wake("first ask")                                   # one run parked, whose wake lock the cases hold
    key = keys()[0] if keys() else ""
    launcher = A.launcher

    # --- the wake lock: a second wake-up of the same run refuses run-busy ----------------------------
    recorded = counted()
    with holding(launcher(h.agent_meta, key)):
        busy = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "again", *h.harnessed("play"))
        running = h.call("agent", "status", "agents/ag1")
        roster = h.call("agent", "list")
    if busy.returncode == 2 and "run-busy" in busy.stderr and key in busy.stderr and counted() == recorded:
        held("a second wake-up of a run refuses run-busy", f"the wake lock of {key} held by the bench: rc 2, "
             "no record moved, nothing launched")
    else:
        failures.append(f"  ✗ run-busy                    rc={busy.returncode} {busy.stderr[-200:]!r} {counted()}/{recorded}")

    # --- status says running while the wake lock is held ---------------------------------------------
    status_line = next((one for one in running.stdout.splitlines() if one.startswith(f"run {key} ·")), "")
    if (running.returncode == 0 and "running (a wake-up plays)" in status_line
            and roster.returncode == 0 and re.search(r"^agents/ag1 · \d+ run\(s\) · 1 running · \d+ response\(s\)$", roster.stdout, re.M)):
        held("status and list say a run under way", f"{status_line!r}; list counts 1 running")
    else:
        failures.append(f"  ✗ status running              {running.returncode}/{roster.returncode} {status_line!r} {roster.stdout!r}")

    # --- the wake lock is held during a wake-up, present and free after ------------------------------------
    known = set(keys())
    playing = h.popen("agent", "run", "agents/ag1", "--message", "slow lock", *h.harnessed("pause"))
    time.sleep(1.2)                                    # the witness pauses 1.6 s at its first launch
    fresh = [one for one in keys() if one not in known]
    during = bool(fresh) and lock.held(launcher(h.agent_meta, fresh[0]))
    playing.communicate(timeout=60)
    after = bool(fresh) and launcher(h.agent_meta, fresh[0]).exists() and not lock.held(launcher(h.agent_meta, fresh[0]))
    if playing.returncode == 0 and during and after:
        held("the launcher's lock spans the wake-up", f"held while {fresh[0]} plays, present and free after")
    else:
        failures.append(f"  ✗ wake lock held              rc={playing.returncode} fresh={fresh} during={during} after={after}")

    # --- upgrade refuses while a pp process lives at the agent, or under another maintenance -----------
    pins_before = instance.pins(h.agent_meta)
    with lock.serving(h.agent_meta):                 # the bench, a pp process of the agent
        cut_up = cli(h.engine, "upgrade", cwd=h.ws, env=h.env)
    with holding(lock.maintenance_of(h.agent_meta)):
        twice = cli(h.engine, "upgrade", cwd=h.ws, env=h.env)
    if (cut_up.returncode == 2 and "maintenance-busy" in cut_up.stderr
            and twice.returncode == 2 and "maintenance-busy" in twice.stderr
            and instance.pins(h.agent_meta) == pins_before and persistence.slot_of(h.agent_meta, key).is_file()):
        held("upgrade refuses under a process at the agent or another maintenance", "maintenance-busy twice; "
             "the pins and the slot intact")
    else:
        failures.append(f"  ✗ maintenance-busy            {cut_up.returncode}/{twice.returncode} {cut_up.stderr[-200:]!r} "
                        f"{twice.stderr[-200:]!r}")

    # --- a wake-up refuses during maintenance, nothing launched --------------------------------------
    recorded, runs_before = counted(), len(keys())
    with holding(lock.maintenance_of(h.agent_meta)):
        blocked = h.wake("x")
    if (blocked.returncode == 2 and "maintenance-in-progress" in blocked.stderr
            and counted() == recorded and len(keys()) == runs_before):
        held("a wake-up refuses during maintenance", "maintenance-in-progress before any launch: no run, no record")
    else:
        failures.append(f"  ✗ maintenance-in-progress     rc={blocked.returncode} {blocked.stderr[-200:]!r}")

    # --- the neighbours line: absent alone, composed from the wake locks held ------------------------
    out_solo = bench.temp() / "psolo"
    solo = h.call("agent", "run", "agents/ag1", "--message", "solo", *h.harnessed_at("play", out_solo))
    launcher(h.agent_meta, key).write_text(json.dumps({"at": "2026-09-30T09:12:00+00:00",
                                                       "message": "bug Y\nthe rest of the message"}) + "\n",
                                           encoding="utf-8")            # the mark a launcher writes
    with holding(launcher(h.agent_meta, key)):
        shown = h.wake("with a neighbour", "play", "--dry-run")
    local = datetime.fromisoformat("2026-09-30T09:12:00+00:00").astimezone().strftime("%H:%M")
    expected = f"[runs under way: {key} since {local} « bug Y »]"
    if (solo.returncode == 0 and h.read(".prompt.w-1.1", out_solo).startswith(f"{HEAD}\nsolo\n\n▌") and shown.returncode == 0
            and f"{expected}\n\n{HEAD}\nwith a neighbour" in shown.stdout):
        held("the neighbours line heads the prompt", f"a solo wake-up gets none; with {key} under way, --dry-run "
             f"composes {expected!r} then the head of the message")
    else:
        failures.append(f"  ✗ neighbours                  {solo.returncode}/{shown.returncode} prompt={h.read('.prompt.w-1.1', out_solo)[:40]!r} "
                        f"expected={expected!r} shown={shown.stdout[-300:]!r}")

    # --- two wake-ups at once: both answer, the record keeps the bare message, one sees the other ------
    out_a, out_b = bench.temp() / "pa", bench.temp() / "pb"
    both = race(h.engine, [["--instance", str(h.house), "agent", "run", "agents/ag1", "--message", "task alpha",
                            *h.harnessed_at("pause", out_a)],
                           ["--instance", str(h.house), "agent", "run", "agents/ag1", "--message", "task beta",
                            *h.harnessed_at("pause", out_b)]], cwd=h.ws, env=h.env)
    prompt_a = h.read(".prompt.w-1.1", out_a)
    prompt_b = h.read(".prompt.w-1.1", out_b)
    saw_a = prompt_a.startswith("[runs under way: ") and "« task beta »" in prompt_a and f"\n\n{HEAD}\ntask alpha\n\n▌" in prompt_a
    saw_b = prompt_b.startswith("[runs under way: ") and "« task alpha »" in prompt_b and f"\n\n{HEAD}\ntask beta\n\n▌" in prompt_b
    bare_messages = {one.get("message") for one in h.messages()[-2:]}
    if (all(one.returncode == 0 for one in both) and (saw_a or saw_b)
            and f"{HEAD}\ntask alpha\n\n▌" in prompt_a and f"{HEAD}\ntask beta\n\n▌" in prompt_b
            and bare_messages == {"task alpha", "task beta"}):
        held("two wake-ups of one agent play together", f"rc 0 and 0; the later one read the other in its "
             f"neighbours line (alpha saw beta: {saw_a}, beta saw alpha: {saw_b}); the record keeps the bare messages")
    else:
        failures.append(f"  ✗ two at once                 rc={[one.returncode for one in both]} saw={saw_a}/{saw_b} "
                        f"a={prompt_a[:120]!r} b={prompt_b[:120]!r} {[one.stderr[-120:] for one in both]!r}")
    return 0
