"""Scenario `ui-team-form-season-silence` -- the silence of a season's form says where its value comes from (batch
le-silence-de-saison-dit, s.1644), on the bench's `pp-team` witness: `core-review`, its declaration three ways --
TEAM.md `silence: 4` and SEASON.md none; TEAM.md `silence: 4` and SEASON.md `silence: 2`; neither:
- `S`, Launch: the help under the field silence is `palette.season_silence_help` for the source of the value --
  `TEAM.md`, `SEASON.md`, or None for the team's default, which `team declaration --json` does not say -- and TEAM.md's
  value, compared to what the function says (rule 2), never to a sentence
Its sibling, cut by case (rule 10): `ui-team-form-season-silence-whole` (the field takes a whole number).
The function is called in the post's interpreter (`T.TEXTUAL`): `palette.py` imports rich and textual.
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import support

F = support(__file__, "team_forms")
N = support(__file__, "team_new")
T = F.T

MEMBERS = [("lead", "agents/lead"), ("reviewer", "agents/reviewer")]
CASES = {"TEAM.md": ({"budget": 1.0, "silence": 4}, {}, ["TEAM.md", 4]),
         "SEASON.md": ({"budget": 1.0, "silence": 4}, {"silence": 2}, ["SEASON.md", 4]),
         "default": ({"budget": 1.0}, {}, [None, None])}


def face(limits: dict, season_limits: dict) -> dict:
    return T.declaration("core-review", MEMBERS, limits, template="teams/supervisor-workers",
                         season={**T.CORE_SEASON, "limits": season_limits})


def said_by_palette(calls: list[list]) -> list[str]:
    """-> what `palette.season_silence_help` says for each of `calls`, in the post's interpreter."""
    code = ("import json, sys; sys.path.insert(0, sys.argv[1]); import palette; "
            "print(json.dumps([palette.season_silence_help(*one) for one in json.loads(sys.argv[2])]))")
    run = subprocess.run([*T.TEXTUAL, "-c", code, str(T.SKILL), json.dumps(calls)], capture_output=True, text=True)
    try:
        return json.loads(run.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return [f"(no palette: {run.stderr.strip()[-160:]})"] * len(calls)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season-silence")
    wanted = dict(zip(CASES, said_by_palette([call for _, _, call in CASES.values()])))
    shown = {}
    for case, (limits, season_limits, _) in CASES.items():
        house.use(T.script(declarations={**T.DECLARATIONS, "core-review": face(limits, season_limits)}))
        out = house.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_LAUNCH},boxes")
        shown[case] = " ".join(N.help_under(F.fields(out.stdout), "silence").split())
    if all(shown[case] == " ".join(wanted[case].split()) for case in CASES):
        held("the silence says its source", "; ".join(f"{case}: {shown[case]!r}" for case in CASES))
    else:
        failures.append(f"  ✗ source                      shown={shown} wanted={wanted}")
    return 0
