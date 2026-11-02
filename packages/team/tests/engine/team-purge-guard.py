"""Scenario `team-purge-guard` -- 2 case(s) (batch le-poids-des-runs, 2026-10-11: row 77 of the study § 18, team
0.23.0, agent 0.23.0): a member's run is GUARDED while its team lives. `agent purge` asks the engine before any
removal (`events.guarded`, the vector family `agent-run` pp-agent verifies) and `pp-team`, the family's guardian,
refuses the run a member of a living team holds; `agent` never names `team`.
- (a) held (I18): w asks the owner -- T1 open, w's run kept; `agent purge agents/w <key>` refuses `run-held`, dry
  and under `--yes`, naming the team, the member and `team reset`; the house's records and the agent's state the
  same to the byte
- (b) free once the team ends: the reply given, T1 resolved, no ceremony declared -- the dry purge of the same run
  passes and counts it
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from tests.harness import support

T = support(__file__, "team")


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root`."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()} \
        if root.is_dir() else {}


def quiet(*roots: Path, timeout: float = 20.0) -> list[dict[str, bytes]]:
    """-> the files under each root once two readings half a second apart agree: a wake-up that answered
    still releases its lock and closes its files after its `wake-ended`."""
    deadline = time.monotonic() + timeout
    seen = [files_under(root) for root in roots]
    while time.monotonic() < deadline:
        time.sleep(0.5)
        now = [files_under(root) for root in roots]
        if now == seen:
            return now
        seen = now
    return seen


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
              {"sleep": 0.1, "body": {"done": "merged"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    state = h.meta_of("agents/w") / ".sys" / "state"

    # --- (a) held: the run of a member of a living team is never purged -- I18 ---------------------------
    h.declare("keep", "---\nagents: |\n  w agents/w\nroot: w\nschedule: off\n---\nKeep the run.\n")
    started = h.call("team", "start", "keep", "--message", "merge PR 11", *h.harnessed)
    asked = h.settled("keep", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    key = next((one.get("run") for one in by_kind(h.events("keep"), "wake-ended", agent="w")), "") or ""
    records_before, state_before = quiet(h.records, state)
    dry = h.call("agent", "purge", "agents/w", key)
    sure = h.call("agent", "purge", "agents/w", key, "--yes")
    said = sure.stderr
    if (started.returncode == 0 and asked and key and dry.returncode == 2 and sure.returncode == 2
            and "run-held" in dry.stderr and "run-held" in said and "keep" in said and " w " in f" {said} "
            and "team reset" in said
            and files_under(h.records) == records_before and files_under(state) == state_before):
        bench.refusals += 2
        held("(a) held while the team lives", f"run {key} of agents/w, member w of keep: dry and --yes refuse "
             "run-held, team reset named; records and state the same to the byte -- I18")
    else:
        failures.append(f"  ✗ (a) held                   rc={started.returncode}/{dry.returncode}/{sure.returncode} "
                        f"asked={asked} key={key!r} {dry.stderr.strip()[-200:]!r} {said.strip()[-200:]!r} "
                        f"same={files_under(h.records) == records_before and files_under(state) == state_before}")

    # --- (b) free once the team ends -----------------------------------------------------------------------
    ask = next((one["id"] for one in by_kind(h.events("keep"), "post", verb="ask")), -1)
    replied = h.call("team", "post", "keep", "--task", "T1", "--reply", str(ask), "--message", "main")
    done = h.settled("keep", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    free = h.call("agent", "purge", "agents/w", key, "--json")
    try:
        told = json.loads(free.stdout)
    except ValueError:
        told = {}
    if (replied.returncode == 0 and done and free.returncode == 0 and told.get("dry") is True
            and [one.get("key") for one in told.get("runs") or []] == [key]):
        held("(b) free once the team ends", f"T1 resolved, no ceremony: the dry purge of {key} passes and counts it")
    else:
        failures.append(f"  ✗ (b) free                   rc={replied.returncode}/{free.returncode} done={done} "
                        f"{free.stdout[-200:]!r} {free.stderr.strip()[-200:]!r}")
    return 0
