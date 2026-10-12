"""Scenario `team-new` -- 2 case(s) (batch les-modeles-d-equipe, 2026-10-11: row 79 of the study § 18, team
0.25.0): a team is born from a TEMPLATE -- `team templates` lists five, `team new <name> --template <t>` writes
`teams/<name>/TEAM.md` judged by `start`'s own judge, and `team start` accepts it as it stands. No wake-up plays:
every start is `--no-tick`.
- (a) the templates: `team templates` says one line per template, `supervisor-workers`, `lead-reviewers`,
  `chain`, `solo`, `empty`; `--json` one object per template, its keys exactly `{template, description,
  members, root, reports, ceremony, limits, intention}`
- (b) each template written then started: its members at `agents/<team>/<member>`, its root, its edges, the
  daily of the two forms with two members or more reporting to the root, the default limits (`budget: 5`,
  `wakes: 8`, `timeout: 900`) and `schedule: off`, read at `team-started`; the intention names the members
  the team has; `empty` the smallest declaration -- no intention, no limit, the schedule `start` defaults to
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

TEMPLATES = ("supervisor-workers", "lead-reviewers", "chain", "solo", "empty")
KEYS = {"template", "description", "members", "root", "reports", "ceremony", "limits", "intention"}
LIMITS = {"budget": 5, "wakes": 8, "timeout": 900}
# template -> (members, root, edges, the daily's line or None)
SHAPES = {
    "supervisor-workers": (["supervisor", "worker-1", "worker-2"], "supervisor",
                           [{"from": ["worker-1", "worker-2"], "to": "supervisor"}],
                           "daily every weekday 09:30 with worker-1 worker-2 -> supervisor"),
    "lead-reviewers": (["lead", "reviewer-1", "reviewer-2"], "lead",
                       [{"from": ["reviewer-1", "reviewer-2"], "to": "lead"}],
                       "daily every weekday 09:30 with reviewer-1 reviewer-2 -> lead"),
    "chain": (["step-1", "step-2", "step-3"], "step-1",
              [{"from": ["step-2"], "to": "step-1"}, {"from": ["step-3"], "to": "step-2"}], None),
    "solo": (["worker"], "worker", [], None),
    "empty": (["lead"], "lead", [], None),
}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind = T.by_kind

    # --- (a) the templates read -----------------------------------------------------------------
    listed = h.call("team", "templates")
    said = [line.split()[0] for line in listed.stdout.splitlines() if line.strip()]
    faced = h.call("team", "templates", "--json")
    objects = [json.loads(line) for line in faced.stdout.splitlines() if line.strip()] if faced.returncode == 0 else []
    if (listed.returncode == 0 and said == list(TEMPLATES) and len(objects) == len(TEMPLATES)
            and all(set(one) == KEYS for one in objects) and [one["template"] for one in objects] == list(TEMPLATES)
            and all(one["members"] == SHAPES[one["template"]][0] and one["root"] == SHAPES[one["template"]][1]
                    for one in objects)):
        held("(a) the templates read", f"five lines ({', '.join(said)}); --json five objects, keys {sorted(KEYS)}")
    else:
        failures.append(f"  ✗ (a) templates              rc={listed.returncode}/{faced.returncode} said={said} "
                        f"objects={[sorted(one) for one in objects][:1]} {(listed.stderr or faced.stderr).strip()[-160:]!r}")

    # --- (b) each template written, then started ------------------------------------------------
    wrong = []
    for template in TEMPLATES:
        team = f"t-{template}"
        made = h.call("team", "new", team, "--template", template)
        doc = h.teams / team / "TEAM.md"
        text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
        started = h.call("team", "start", team, "--message", "go", "--no-tick", now="07:50")
        first = next(iter(by_kind(h.events(team), "team-started")), {})
        members, root, edges, daily = SHAPES[template]
        intention = text.split("---\n", 2)[-1].strip() if text.startswith("---\n") else None
        named = all(f"`{one}`" in intention for one in members) if intention else template == "empty"
        if not (made.returncode == 0 and started.returncode == 0
                and first.get("agents") == {one: f"agents/{team}/{one}" for one in members}
                and first.get("root") == root and first.get("reports") == edges
                and [one.get("text") for one in first.get("ceremonies") or []] == ([daily] if daily else [])
                and first.get("limits") == ({} if template == "empty" else LIMITS)
                and first.get("schedule") == (5 if template == "empty" else None) and named
                and (intention == "") == (template == "empty")
                and f"team start {team}" in made.stdout):
            wrong.append(f"{template}: rc={made.returncode}/{started.returncode} agents={first.get('agents')} "
                         f"root={first.get('root')} reports={first.get('reports')} limits={first.get('limits')} "
                         f"schedule={first.get('schedule')} named={named} "
                         f"{(made.stderr or started.stderr).strip()[-160:]!r}")
    if not wrong:
        held("(b) each template written then started", "five teams written by `team new` and started as they "
             "stand: members at agents/<team>/<member>, root, edges, the daily of the two wide forms, the default "
             "limits, schedule off; each intention names its members, `empty` none")
    else:
        failures.extend(f"  ✗ (b) {one}" for one in wrong)
    return 0
