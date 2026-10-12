"""Scenario `team-declaration-judged` -- 3 case(s) (batch la-declaration-jugee, 2026-10-12: team 0.32.2): `team
declaration <name> --json` says `declared`, the front matter of `TEAM.md` as start's own judge reads it -- what the
NEXT season will have, never the last start's. No wake-up plays: every start is `--no-tick`.
- (a) a team never started: `declared` carries its members and their paths in the order declared, its root, its
  edges, its principals, its limits, its schedule, its ceremonies' lines (KDJ3)
- (b) a team started under a season's `--budget 30`, then a member added to its `TEAM.md`: `declared` says the
  new member and `TEAM.md`'s own budget (5) -- `status --json` keeps the start's members and the season's limit --;
  started again, `team-started` keeps the members and the limits `declared` said (KDJ3); the text of `declaration`
  the same bytes before and after the face is read (KDJ4)
- (c) a broken `TEAM.md`: `declared: null` beside the refused verdict
"""
from __future__ import annotations

import hashlib
import json

from tests.harness import cli, support

T = support(__file__, "team")

FIRST = ("---\nagents: |\n  lead agents/lead\n  dev agents/dev\nreports: |\n  dev -> lead\nroot: lead\n"
         "principals: |\n  pm\nbudget: 5\nwakes: 8\nschedule: off\nceremonies: |\n"
         "  daily every weekday 09:30 with dev -> lead\n---\nShip it.\n")
WIDER = FIRST.replace("  dev agents/dev\n", "  dev agents/dev\n  qa agents/qa\n").replace("  dev -> lead", "  dev qa -> lead")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})

    def face(*args: str) -> dict:
        played = cli(h.engine, "--instance", str(h.house), *args, "--json", cwd=h.ws, env=h.env)
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    def text_sha(name: str) -> str:
        return hashlib.sha256(h.call("team", "declaration", name).stdout.encode()).hexdigest()[:12]

    # --- (a) a team never started -- KDJ3 -----------------------------------------------------------------------
    h.declare("new", FIRST)
    said = face("team", "declaration", "new").get("declared") or {}
    wanted = {"agents": [{"member": "lead", "path": "agents/lead"}, {"member": "dev", "path": "agents/dev"}],
              "root": "lead", "reports": [{"from": ["dev"], "to": "lead"}], "principals": ["pm"],
              "limits": {"budget": 5.0, "wakes": 8}, "schedule": None,
              "ceremonies": ["daily every weekday 09:30 with dev -> lead"], "entries": {}, "work": None}
    if said == wanted:
        held("(a) a team never started says its declaration", "members in order, root, edges, principals, limits, "
             "schedule off, the daily's line -- KDJ3")
    else:
        failures.append(f"  ✗ (a) never started          {said}")

    # --- (b) what the next season will have -- KDJ3, KDJ4 -------------------------------------------------------
    h.declare("crew", FIRST)
    h.call("team", "start", "crew", "--message", "go", "--budget", "30", *h.harnessed, "--no-tick")
    h.declare("crew", WIDER)
    before = text_sha("crew")
    declared = face("team", "declaration", "crew").get("declared") or {}
    after = text_sha("crew")
    state = face("team", "status", "crew")
    h.call("team", "start", "crew", *h.harnessed, "--no-tick")
    started = [one for one in h.events("crew") if one.get("kind") == "team-started"][-1]
    members = [one.get("member") for one in declared.get("agents") or []]
    if (members == ["lead", "dev", "qa"] and declared.get("limits", {}).get("budget") == 5.0
            and [one.get("member") for one in state.get("members") or []] == ["lead", "dev"]
            and (state.get("limits") or {}).get("budget") == 30.0
            and list(started.get("agents") or {}) == members and started.get("limits") == declared.get("limits")
            and before == after):
        held("(b) the next season's declaration", f"declared {members}, budget 5 where status says the start's "
             f"two members and the season's 30; the next start keeps what declared said; text sha {before} -- KDJ3 KDJ4")
    else:
        failures.append(f"  ✗ (b) next season            declared={declared} status_members="
                        f"{[one.get('member') for one in state.get('members') or []]} limits={state.get('limits')} "
                        f"started={started.get('agents')} {started.get('limits')} {before} {after}")

    # --- (c) a broken TEAM.md -----------------------------------------------------------------------------------
    h.declare("broken", FIRST.replace("root: lead", "root: ghost"))
    broken = face("team", "declaration", "broken")
    if "declared" in broken and broken["declared"] is None and (broken.get("verdict") or {}).get("ok") is False:
        held("(c) a refused verdict declares nothing", f"declared null beside {broken['verdict']['refusal'][:60]!r}")
    else:
        failures.append(f"  ✗ (c) broken                 {broken}")
    return 0
