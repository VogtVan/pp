"""Scenario `team-delete-agents` -- `team delete <name> --agent <path>... --yes` takes the agents named away with the
team, by `agent remove` (batch les-equipes-au-poste, team 0.51.0):
- (f) taken away: on two teams at rest, `gone` (agents m and g) and `other` (g too), the dry face lists `agents`
  as the paths `gone` alone declares (m); `--agent agents/m --yes` removes `teams/gone`, its journal and `agents/m`
  whole -- the face says `removed` --; `agents/g` stands
- (g) a shared agent refuses: `--agent agents/g` (declared by `other` too) and `--agent agents/x` (declared by
  nobody) refuse `agent-shared` before anything is written -- the team's directory, its journal and the agents the same
  to the byte
"""
from __future__ import annotations

import json
from pathlib import Path

from tests.harness import support

T = support(__file__, "team")


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root` -- a lock's own file, laid at its first take, left out."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*"))
            if path.is_file() and path.suffix != ".lock"} if root.is_dir() else {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    records = h.records / "teams"
    h.declare("gone", "---\nagents: |\n  m agents/m\n  g agents/g\nreports: |\n  g -> m\nroot: m\nschedule: off\n---\nAt rest.\n")
    h.declare("other", "---\nagents: |\n  g agents/g\nroot: g\nschedule: off\n---\nShares g.\n")
    started = [h.call("team", "start", name, "--no-tick") for name in ("gone", "other")]

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
    return 0
