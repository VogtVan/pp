"""Scenario `team-purge-guard` -- 4 case(s) (batch le-poids-des-runs, 2026-10-11: row 77 of the study § 18, team
0.23.0, agent 0.23.0): a member's run is GUARDED while its team lives. `agent purge` asks the engine before any
removal (`events.guarded`, the vector family `agent-run` pp-agent verifies) and `pp-team`, the family's guardian,
refuses the run a member of a living team holds; `agent` never names `team`.
- (a) held (I18): w asks the owner -- T1 open, w's run kept; `agent purge agents/w <key>` refuses `run-held`, dry
  and under `--yes`, naming the team, the member and `team reset`; the house's records and the agent's state the
  same to the byte
- (b) free once the team ends: the reply given, T1 resolved, no ceremony declared -- the dry purge of the same run
  passes and counts it
- (c) `team reset` -- its cases here, `team-reset` past its target with them --: a console that keeps the run: a1 has
  no run, b1's run stands in the journal while its agent's instance is gone -- `team reset` says a1 first, then
  refuses `reset-failed` at b1, no `run-reset` written
- (d) a tick asked during the reset: the mark `tick.pending` laid beside the journal while `team reset --member a1`
  holds the tick's lock -- the reset plays the tick once it has written, and the mark is gone
"""
from __future__ import annotations

import json
import shutil
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

    # --- (c) a console that keeps the run ----------------------------------------------------------------------------
    h.declare("said", "---\nagents: |\n  a1 agents/a1\n  b1 agents/b1\nreports: |\n  b1 -> a1\nroot: a1\n"
                      "schedule: off\n---\nOne run kept.\n")
    begun_f = h.call("team", "start", "said", "--no-tick")
    shutil.rmtree(h.meta_of("agents/b1"), ignore_errors=True)            # b1's instance taken away by hand
    last_f = max((int(one.get("id") or 0) for one in h.events("said")), default=0)
    with h.journal_of("said").open("a", encoding="utf-8") as handle:     # b1's run, as the tick writes it
        for offset, one in enumerate((
                {"kind": "wake-intent", "tag": "b1-T1-e5e5e5", "agent": "b1", "path": "agents/b1", "task": "T1",
                 "run": None, "messages": []},
                {"kind": "wake-ended", "tag": "b1-T1-e5e5e5", "agent": "b1", "run": "e5e5e5", "state": "parked",
                 "cost": 0.0}), 1):
            handle.write(json.dumps({"at": "2026-11-15T12:00:00+00:00", "id": last_f + offset, "team": "said",
                                     **one}) + "\n")
    kept_f = h.call("team", "reset", "said")
    said_f = [one for one in kept_f.stdout.splitlines() if one.strip()]
    if (begun_f.returncode == 0 and kept_f.returncode == 2 and T.refusal_code(kept_f.stderr) == "reset-failed"
            and not by_kind(h.events("said"), "run-reset")):
        bench.refusals += 1
        held("(c) a console that keeps the run", "b1's console refused its run: reset-failed, no run-reset written")
    else:
        failures.append(f"  ✗ (c) the console keeps       rc={begun_f.returncode}/{kept_f.returncode} "
                        f"code={T.refusal_code(kept_f.stderr)} said={said_f} {kept_f.stderr[-200:]!r}")

    # --- (d) a tick asked during the reset ---------------------------------------------------------------------------
    pending = h.journal_of("said").parent / "tick.pending"
    pending.write_text("2026-11-15T12:00:00+00:00\n", encoding="utf-8")   # a tick met the reset's hold
    reset_g = h.call("team", "reset", "said", "--member", "a1")
    if reset_g.returncode == 0 and not pending.exists() and not by_kind(h.events("said"), "run-reset"):
        held("(d) a tick asked during the reset", "the mark tick.pending laid: the reset of a1 plays the tick once "
             "written, the mark gone")
    else:
        failures.append(f"  ✗ (d) a tick asked            rc={reset_g.returncode} pending={pending.exists()} "
                        f"{reset_g.stderr[-200:]!r}")
    return 0
