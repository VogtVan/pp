"""Scenario `ui-team-season-again` -- `S` on a team at work opens the form on its files, and with nothing changed starts
the season they write; its refusals; on the bench's witnesses (`_teams`):
`core-review`, in its first season -- its declaration (`team declaration --json`: its members, `scribe` added; its role
`make`; its season's preset `seasons/files`; the season SEASON.md writes; the keys a start would change, `pending`) --,
then a `team start` that refuses and a declaration `start` would refuse (`ops`); what plays read from the witness's
journal, no command on screen:
- the overlay titled by the team, its season and the next; the side pane's SEASON.md on its preset; a line for
  `scribe`, declared, not in the face; the gap to the season under way said in the view by member, key by key
- with nothing changed, `ctrl+s` plays `team declare core-review --season --context 90` -- the context at the form's
  default --, then `team start core-review` without a flag of the season: the season SEASON.md writes
- a refusal of `team start` goes to the remedy line as the verb said it, after the declare that wrote SEASON.md: the
  line `palette.declare_refused` makes of it, short enough to stand whole on the remedy line, compared to what the
  function says (rule 2) -- the function called in the post's interpreter (`T.TEXTUAL`): `palette.py` imports rich
  and textual
- a declaration `start` would refuse opens nothing: its code on the remedy line, nothing played
- the owner's own line of documents: `ui-team-season-owned` (cut by case, rule 10)
Its siblings: `ui-team-season-new`, `ui-team-season-member`, `ui-team-season-packages`.
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source
F = support(__file__, "team_forms")    # the readers of a form by its zones, the keys that type

ERR = "pp-team: team-invalid -- `parallel: 0` is no whole number of 1 or more.\n"   # whole on the remedy line
CORE = T.DECLARATIONS["core-review"]
PENDING = {**CORE, "pending": [{"key": "agents", "started": {"lead": "agents/lead"}, "declared": {"scribe": "agents/scribe"}},
                               {"key": "roles", "started": {}, "declared": {"make": ["lead"]}}]}
def declare_refused(said: str, written: list[str]) -> str:
    """-> what `palette.declare_refused` says, in the post's interpreter."""
    code = ("import json, sys; sys.path.insert(0, sys.argv[1]); import palette; "
            "print(json.dumps(palette.declare_refused(*json.loads(sys.argv[2]))))")
    run = subprocess.run([*T.TEXTUAL, "-c", code, str(T.SKILL), json.dumps([said, written])], capture_output=True,
                         text=True)
    try:
        return json.loads(run.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return f"(no palette: {run.stderr.strip()[-160:]})"


REFUSING = T.script(declarations={**T.DECLARATIONS, "core-review": PENDING, "ops": T.REFUSED},
                    answers={"start": {"rc": 2, "err": ERR}})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-again", REFUSING, agents=T.SEASON_AGENTS)

    # --- the form on the files, the season they write, a start refused ----------------------------------------------
    shown = house.render("--render", "teams", *T.SEASON_SIZE, "--press", f"S,{T.TO_LINES},boxes")
    opened = house.render("--render", "teams", *T.SEASON_SIZE, "--press", "S,boxes")     # Preset: the file beside it
    title = P.title_of(shown.stdout) or [""]
    n = T.CORE["season"]["n"]
    added = T.season_line(shown.stdout, "scribe", "agents/scribe")
    reviewer = T.season_line(shown.stdout, "reviewer", "agents/reviewer")
    file, view = F.zone_rows(opened.stdout, "form-file"), F.zone_rows(shown.stdout, "form-view")
    preset = f"template: {T.FILES['template']}"
    gap = next((row for row in view if all(one["key"] in row for one in PENDING["pending"])), "")
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", "S,ctrl+s")
    remedy = T.remedy_of(done)
    if (shown.returncode == 0 and T.in_order(title[0], "core-review", str(n), str(n + 1)) and added
            and "agents/scribe" not in [one["path"] for one in T.CORE["members"]] and reviewer[3:4] == ["sonnet"]
            and preset in file and gap and "./pp" not in shown.stdout and done.returncode == 0
            and house.gestures() == [T.NEXT_DECLARED, T.NEXT]):
        held("S opens on the files, and starts the season they write", f"{title[0]!r}; {preset!r}; {gap!r}; {T.NEXT}")
    else:
        failures.append(f"  ✗ new season                  rc={shown.returncode},{done.returncode} {title} {added} "
                        f"{reviewer} {file} {view} {house.gestures()} {shown.stderr[-400:]!r}")
    wanted = declare_refused(ERR.strip(), ["SEASON.md"])
    if done.returncode == 0 and remedy == wanted:
        held("a refused start: the refusal said", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {remedy!r} {wanted!r} {done.stdout[-700:]!r}")

    # --- a declaration refused ---------------------------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", "down,S,ctrl+s")
    remedy = T.remedy_of(done)
    code = T.REFUSED["verdict"]["refusal"].split(" -- ")[0]
    if done.returncode == 0 and code in remedy.split() and P.overlay_rows(done.stdout) == [] and house.gestures() == []:
        held("a refused declaration opens nothing", remedy[:90])
    else:
        failures.append(f"  ✗ refused declaration         rc={done.returncode} {remedy!r} {house.gestures()} "
                        f"{done.stdout[-1500:]!r}")

    return 0
