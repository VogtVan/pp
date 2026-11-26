"""Scenario `team-delete-agents` -- `team delete <name> --agent <path>... --yes` takes the agents named away with the
team, by `agent remove` (batch les-equipes-au-poste, team 0.51.0):
- (f) taken away: on two teams at rest, `gone` (agents m and g) and `other` (g too), the dry face lists `agents`
  as the paths `gone` alone declares (m); `--agent agents/m --yes` removes `teams/gone`, its journal and `agents/m`
  whole -- the face says `removed` --; `agents/g` stands
- (g) a shared agent refuses: `--agent agents/g` (declared by `other` too) and `--agent agents/x` (declared by
  nobody) refuse `agent-shared` before anything is written -- the team's directory, its journal and the agents the same
  to the byte
- (h) an agent the house's console does not remove: `home` (hm played by the house, `.`) holds T1's run K at the
  house, which also holds a run O opened outside the team; `--agent . --yes` refuses `agent-kept` before anything is
  written -- the team's directory, its journal and both slots the same to the byte --; the dry face lists no agent
  and K among its runs at `.`; `delete home --yes` removes the team and purges K, O stands and the house with it
- (i) a team never started: `delete --yes` without a journal removes its directory -- the face says no journal
- (j) runs nobody holds: a run of a wake-up whose member the start never named -- no path for it -- is no run of the
  team's face; a run at an agent whose directory is gone is listed, nothing purged there, and `--agent` of that agent
  removes nothing -- the team removed, `removed` empty
- (k) a delete taken up, its runs half purged: the journal names a run the agent still keeps and one it no longer
  knows (`run-unknown`, purged by an earlier delete): the purge plays again on the one kept, the team removed
- (l) the removal refused: a run of the agent named still held by its wake lock -- `agent remove` refuses, the delete
  says `delete-failed`, the agent stands; released, `delete --agent --yes` without `--json` removes it and the team
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from conductor import persistence
from tests.harness import cli, holding, support

T = support(__file__, "team")


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root` -- a lock's own file, laid at its first take, left out."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*"))
            if path.is_file() and path.suffix != ".lock"} if root.is_dir() else {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={**T.PAPER_SCRIPT, "hm": [{"sleep": 0.1, "body": {"done": "home"}}]})
    records = h.records / "teams"
    h.declare("gone", "---\nagents: |\n  m agents/m\n  g agents/g\nreports: |\n  g -> m\nroot: m\nschedule: off\n---\nAt rest.\n")
    h.declare("other", "---\nagents: |\n  g agents/g\nroot: g\nschedule: off\n---\nShares g.\n")
    started = [h.call("team", "start", name, "--no-tick") for name in ("gone", "other")]
    h.declare("home", "---\nagents: |\n  hm .\nroot: hm\nschedule: off\n---\nThe house plays a member.\n")
    home = h.call("team", "start", "home", "--message", "one task", *h.harnessed)

    def kept(name: str) -> tuple:
        return (files_under(h.teams / name), files_under(records / name),
                files_under(h.ws / "agents" / "m"), files_under(h.ws / "agents" / "g"))

    # --- (g) a shared agent refuses, nothing written -----------------------------------------------------------
    before = kept("gone")
    shared = h.call("team", "delete", "gone", "--agent", "agents/g", "--yes")
    nobody = h.call("team", "delete", "gone", "--agent", "agents/x", "--yes")
    if (all(one.returncode == 0 for one in started) and h.agent_stands("agents/m") and h.agent_stands("agents/g")
            and shared.returncode == 2 and "agent-shared" in shared.stderr
            and nobody.returncode == 2 and "agent-shared" in nobody.stderr and kept("gone") == before):
        bench.refusals += 2
        held("(g) a shared agent refuses", "agents/g (declared by other) and agents/x (by nobody): agent-shared, the "
             "directory, the journal and the agents the same to the byte")
    else:
        failures.append(f"  ✗ (g) agent-shared           rc={[one.returncode for one in started]}/{shared.returncode}/"
                        f"{nobody.returncode} stands={h.agent_stands('agents/m')}/{h.agent_stands('agents/g')} "
                        f"same={kept('gone') == before} {shared.stderr[-200:]!r} {nobody.stderr[-200:]!r}")

    # --- (f) taken away ----------------------------------------------------------------------------------------
    dry = h.call("team", "delete", "gone", "--json")
    try:
        told = json.loads(dry.stdout)
    except ValueError:
        told = {}
    removed = h.call("team", "delete", "gone", "--agent", "agents/m", "--yes", "--json")
    try:
        result = json.loads(removed.stdout)
    except ValueError:
        result = {}
    if (dry.returncode == 0 and told.get("agents") == ["agents/m"] and removed.returncode == 0
            and result.get("removed") == ["agents/m"] and not (h.teams / "gone").exists()
            and not (records / "gone").exists() and not (h.ws / "agents" / "m").exists()
            and h.agent_stands("agents/g") and (h.teams / "other" / "TEAM.md").is_file()):
        held("(f) taken away", "the dry face lists agents/m alone; --agent agents/m --yes: teams/gone, its journal and "
             "agents/m gone, removed said; agents/g and other stand")
    else:
        failures.append(f"  ✗ (f) taken away             rc={dry.returncode}/{removed.returncode} told={told.get('agents')} "
                        f"result={result} dir={(h.teams / 'gone').exists()} m={(h.ws / 'agents' / 'm').exists()} "
                        f"g={h.agent_stands('agents/g')} {removed.stderr[-300:]!r}")

    # --- (h) an agent the house's console does not remove -----------------------------------------------------
    done_h = h.settled("home", lambda found: bool(T.by_kind(found, "done", task="T1")) and T.all_ended(found), 60)
    key = next((one.get("run") for one in T.by_kind(h.events("home"), "wake-ended", agent="hm")), "") or ""
    outside = cli(h.engine, "--instance", str(h.house), "-new", cwd=h.ws, env=h.env)
    other = (re.search(r"run ([0-9a-f]{6})", outside.stdout) or [None, ""])[1]
    slots = lambda: tuple(persistence.slot_of(h.house, one).is_file() for one in (key, other))
    stood = (files_under(h.teams / "home"), files_under(records / "home"), slots())
    kept_h = h.call("team", "delete", "home", "--agent", ".", "--yes")
    after = (files_under(h.teams / "home"), files_under(records / "home"), slots())
    dry_h = h.call("team", "delete", "home", "--json")
    try:
        told_h = json.loads(dry_h.stdout)
    except ValueError:
        told_h = {}
    gone_h = h.call("team", "delete", "home", "--yes", "--json")
    if (home.returncode == 0 and done_h and key and other and stood[2] == (True, True)
            and kept_h.returncode == 2 and T.refusal_code(kept_h.stderr) == "agent-kept" and after == stood
            and dry_h.returncode == 0 and told_h.get("agents") == []
            and [(one.get("path"), one.get("run")) for one in told_h.get("runs") or []] == [(".", key)]
            and gone_h.returncode == 0 and not (h.teams / "home").exists() and not (records / "home").exists()
            and slots() == (False, True) and persistence.slot_of(h.house, other).is_file()):
        bench.refusals += 1
        held("(h) an agent the house's console does not remove", f"--agent . refuses agent-kept, nothing written; the "
             f"dry face lists no agent and run {key} at `.`; delete --yes purges {key}, the house's run {other} stands")
    else:
        failures.append(f"  ✗ (h) the house kept           rc={home.returncode}/{kept_h.returncode}/{dry_h.returncode}/"
                        f"{gone_h.returncode} done={done_h} key={key!r} other={other!r} stood={stood[2]} "
                        f"same={after == stood} code={T.refusal_code(kept_h.stderr)} agents={told_h.get('agents')} "
                        f"runs={told_h.get('runs')} slots={slots()} {(home.stderr + gone_h.stderr)[-300:]!r}")

    def appended(name: str, events: list[dict]) -> None:
        """Events appended to the team's journal by the bench while the team rests, numbered after its last."""
        last = max((int(one.get("id") or 0) for one in h.events(name)), default=0)
        with h.journal_of(name).open("a", encoding="utf-8") as handle:
            for offset, one in enumerate(events, 1):
                handle.write(json.dumps({"at": "2026-11-15T12:00:00+00:00", "id": last + offset, "team": name,
                                         **one}) + "\n")

    def ended(member: str, path: str | None, task: str, run: str) -> list[dict]:
        """-> a wake-up of `member` on `task` ended in `run`, as the tick writes it; `path` None: none said."""
        tag = f"{member}-{task}-{run}"
        return [{"kind": "wake-intent", "tag": tag, "agent": member, **({"path": path} if path else {}), "task": task,
                 "run": None, "messages": []},
                {"kind": "wake-ended", "tag": tag, "agent": member, "run": run, "state": "parked", "cost": 0.0}]

    def told_by(played) -> dict:
        try:
            return json.loads(played.stdout)
        except ValueError:
            return {}

    # --- (i) a team never started ------------------------------------------------------------------------------
    h.declare("unborn", "---\nagents: |\n  ub agents/ub\nroot: ub\nschedule: off\n---\nNever started.\n")
    unborn = h.call("team", "delete", "unborn", "--yes", "--json")
    result_i = told_by(unborn)
    if (unborn.returncode == 0 and result_i.get("dry") is False and result_i.get("journal") is None
            and not (h.teams / "unborn").exists() and not (records / "unborn").exists()):
        held("(i) a team never started", "delete --yes without a journal: the directory removed, no journal said")
    else:
        failures.append(f"  ✗ (i) never started           rc={unborn.returncode} result={result_i} "
                        f"dir={(h.teams / 'unborn').exists()} {unborn.stderr[-200:]!r}")

    # --- (j) runs nobody holds -----------------------------------------------------------------------------------
    h.declare("ghost", "---\nagents: |\n  gm agents/gm\nroot: gm\nschedule: off\n---\nIts agent gone.\n")
    begun_j = h.call("team", "start", "ghost", "--no-tick")
    shutil.rmtree(h.ws / "agents" / "gm", ignore_errors=True)           # the agent's directory taken away by hand
    appended("ghost", ended("gm", "agents/gm", "T1", "a1a1a1") + ended("xx", None, "T1", "b2b2b2"))
    dry_j = told_by(h.call("team", "delete", "ghost", "--json"))
    gone_j = h.call("team", "delete", "ghost", "--agent", "agents/gm", "--yes", "--json")
    result_j = told_by(gone_j)
    if (begun_j.returncode == 0
            and [(one.get("member"), one.get("path"), one.get("run")) for one in dry_j.get("runs") or []]
            == [("gm", "agents/gm", "a1a1a1")] and dry_j.get("agents") == ["agents/gm"]
            and gone_j.returncode == 0 and result_j.get("removed") == [] and not (h.teams / "ghost").exists()
            and not (records / "ghost").exists()):
        held("(j) runs nobody holds", "xx's run, no path for it, is no run of the face; gm's run at its gone agent "
             "listed, nothing purged there, --agent agents/gm removes nothing; the team removed")
    else:
        failures.append(f"  ✗ (j) runs nobody holds       rc={begun_j.returncode}/{gone_j.returncode} dry={dry_j} "
                        f"result={result_j} {gone_j.stderr[-200:]!r}")

    # --- (k) a delete taken up, its runs half purged -------------------------------------------------------------
    h.declare("half", "---\nagents: |\n  hp agents/hp\nroot: hp\nschedule: off\n---\nHalf purged.\n")
    begun_k = h.call("team", "start", "half", "--no-tick")
    if not h.agent_stands("agents/hp"):
        h.call("agent", "add", "agents/hp")
    opened_k = cli(h.engine, "--instance", str(h.meta_of("agents/hp")), "-new", cwd=h.meta_of("agents/hp").parent,
                   env=h.env)
    key_k = (re.search(r"run ([0-9a-f]{6})", opened_k.stdout) or [None, ""])[1]
    appended("half", ended("hp", "agents/hp", "T1", key_k) + ended("hp", "agents/hp", "T2", "c3c3c3"))
    kept_k = persistence.slot_of(h.meta_of("agents/hp"), key_k).is_file() if key_k else False
    gone_k = h.call("team", "delete", "half", "--yes", "--json")
    if (begun_k.returncode == 0 and key_k and kept_k and gone_k.returncode == 0
            and not persistence.slot_of(h.meta_of("agents/hp"), key_k).is_file()
            and not (h.teams / "half").exists() and h.agent_stands("agents/hp")):
        held("(k) a delete taken up, half purged", f"run c3c3c3 unknown at agents/hp, run {key_k} kept: purged again "
             "alone, the team removed, the agent stands")
    else:
        failures.append(f"  ✗ (k) half purged             rc={begun_k.returncode}/{gone_k.returncode} key={key_k!r} "
                        f"kept={kept_k} dir={(h.teams / 'half').exists()} {gone_k.stderr[-300:]!r}")

    # --- (l) the removal refused ---------------------------------------------------------------------------------
    h.declare("keep", "---\nagents: |\n  kp agents/kp\nroot: kp\nschedule: off\n---\nIts agent busy.\n")
    begun_l = h.call("team", "start", "keep", "--no-tick")
    if not h.agent_stands("agents/kp"):
        h.call("agent", "add", "agents/kp")
    state_l = h.meta_of("agents/kp") / ".sys" / "state"
    state_l.mkdir(parents=True, exist_ok=True)
    wake_l = state_l / "session-d4d4d4.wake.lock"
    with holding(wake_l):                                                  # a conversation of the agent's own
        refused_l = h.call("team", "delete", "keep", "--agent", "agents/kp", "--yes")
        stands_l = h.agent_stands("agents/kp")
    wake_l.unlink(missing_ok=True)
    removed_l = h.call("team", "delete", "keep", "--agent", "agents/kp", "--yes")
    if (begun_l.returncode == 0 and refused_l.returncode == 2 and T.refusal_code(refused_l.stderr) == "delete-failed"
            and stands_l and removed_l.returncode == 0 and not h.agent_stands("agents/kp")
            and not (h.ws / "agents" / "kp").exists() and not (h.teams / "keep").exists()):
        bench.refusals += 1
        held("(l) the removal refused", "agents/kp's run held: agent remove refused, delete-failed, the agent stands; "
             "released, delete --agent --yes removes it and the team")
    else:
        failures.append(f"  ✗ (l) removal refused         rc={begun_l.returncode}/{refused_l.returncode}/"
                        f"{removed_l.returncode} code={T.refusal_code(refused_l.stderr)} stands={stands_l} "
                        f"after={h.agent_stands('agents/kp')} {refused_l.stderr[-200:]!r} {removed_l.stderr[-200:]!r}")
    return 0
