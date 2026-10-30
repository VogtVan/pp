"""Scenario `ui-team-season-new` -- `S` on a team at work opens its NEXT season, line by line, shown and played, on the
bench's witnesses: `core-review`, in its first season -- its face (`status --json`: its `season`, `launch`,
`members[].launch`, what a member may not switch off, `required`), its declaration (`team declaration --json`: its
`declared` adds `scribe`, its budget below the season's own), the agents of `lead`, `reviewer` and `scribe`
(`agent status --json`) --, then a `team start` that refuses and a declaration `start` would refuse:
- a member edited in its profile composes its own `--member`: its model typed, `plan` switched off, its line's
  packages drawn as those of `reviewer`, whose face says `plan=off`
- `steering` switched off on `all`: one `--package steering=off` per member whose agent has it on -- `scribe`'s has none
- `team`, required: drawn in a look of its own in the packages of `all`, the cursor never on it, never composed `off`
- a name typed beside the message names the first task (`--name`)
- the overlay titled by the team, its season and the next; a line for `scribe`, declared, not in the face; with
  nothing changed and no message the preview, then the start, compose the season of before again -- `all` from
  `launch`, the member that differed, the budget the season gave itself above `TEAM.md`'s
- a refusal of `team start` goes to the remedy line as the verb said it
- a declaration `start` would refuse opens nothing: its code on the remedy line, nothing played
"""
from __future__ import annotations


from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SIZE = ("--size", "130x60")
TO_TABLE = "shift+tab,shift+tab"       # from the message of the first task up to the lines: the name, the table
TO_PACKAGES = "tab,tab,tab"            # in a profile, from the model down to the packages: effort, permissions, packages
PROVIDER = T.D.PROVIDER
AS_ALL = P.palette_constant("AS_ALL")
HEAD = f"team start core-review --budget 2 --provider {PROVIDER} --model opus --effort high"
REVIEWER = "--member reviewer --model sonnet --package plan=off"      # what `reviewer`'s launch changes of `all`
AGAIN = f"{HEAD} {REVIEWER}"
ERR = "pp-team: team-invalid -- teams/core-review/TEAM.md: `parallel: 0` is no whole number of 1 or more.\n"
REFUSING = T.script(declarations={**T.DECLARATIONS, "ops": T.REFUSED}, answers={"start": {"rc": 2, "err": ERR}})




def _line(text: str, member: str, path: str) -> list[str]:
    """-> the cells of the season's line of `member`, found by its name and its path; [] when it is missing."""
    return next((cells for cells in map(T.cells_of, P.overlay_rows(text)) if cells[:2] == [member, path]), [])




def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-new", agents=T.SEASON_AGENTS)

    # --- a member edited: its model, its packages ----------------------------------------------------------------
    member = f"S,{TO_TABLE},down,enter,h,a,i,k,u,{TO_PACKAGES},enter,space,enter,enter"
    shown = house.render("--render", "teams", *SIZE, "--press", member)
    lead, reviewer = _line(shown.stdout, "lead", "agents/lead"), _line(shown.stdout, "reviewer", "agents/reviewer")
    scribe = _line(shown.stdout, "scribe", "agents/scribe")
    preview = T.overlay_preview(shown, "./pp team start")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", member + ",ctrl+s")
    wanted = f"{HEAD} --member lead --model haiku --package plan=off {REVIEWER}"
    if done.returncode == 0 and house.gestures() == [wanted] and preview == f"./pp {wanted}" and lead[3:4] == ["haiku"]:
        held("a member edited composes its own --member", wanted)
    else:
        failures.append(f"  ✗ member edited               rc={shown.returncode},{done.returncode} {lead} {preview!r} "
                        f"{house.gestures()} {shown.stdout[-2500:]!r} {done.stderr[-400:]!r}")
    if (shown.returncode == 0 and lead and reviewer and lead[-1] == reviewer[-1] != AS_ALL and scribe[-1:] == [AS_ALL]
            and done.returncode == 0 and house.gestures() == [wanted]):
        held("plan off on a member's line", f"lead {lead[-1]!r} as reviewer's; {wanted}")
    else:
        failures.append(f"  ✗ member switch               {lead} {reviewer} {scribe} {house.gestures()}")

    # --- a switch of `all`, member by member ---------------------------------------------------------------------
    whole = f"S,{TO_TABLE},enter,{TO_PACKAGES},enter,down,space,enter,enter"
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", whole + ",ctrl+s")
    wanted = f"{HEAD} --member lead --package steering=off {REVIEWER} --package steering=off"
    if done.returncode == 0 and house.gestures() == [wanted]:
        held("steering off on all, for each member whose agent has it", wanted)
    else:
        failures.append(f"  ✗ all switch                  rc={done.returncode} {house.gestures()} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- `team`, required ----------------------------------------------------------------------------------------
    required = f"S,{TO_TABLE},enter,{TO_PACKAGES},enter,down,down,space"   # the second down would stand on `team`
    shown = house.render("--render", "teams", *SIZE, "--press", required, "--styles")
    top = P.on_top(shown.stdout)
    looks = {name: T.look_of(top, name) for name in ("plan", "steering", "team")}
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", required + ",enter,enter,ctrl+s")
    # the space lands on `plan`, the cursor past `team`: plan off for each member whose agent has it on
    wanted = f"{HEAD} --member lead --package plan=off {REVIEWER} --member scribe --package plan=off"
    if (shown.returncode == 0 and "team" in T.REQUIRED and all(looks.values())
            and looks["team"] not in (looks["plan"], looks["steering"]) and done.returncode == 0
            and house.gestures() == [wanted] and "team=off" not in wanted.split()):
        held("team required: greyed, never off", f"its look {looks['team']} beside {looks['steering']}; "
             f"{house.gestures()}")
    else:
        failures.append(f"  ✗ required                    rc={shown.returncode},{done.returncode} {looks} {house.gestures()} "
                        f"{P.ANSI.sub('', top)[-2500:]!r}")

    # --- a name beside the message --------------------------------------------------------------------------------
    named = f"team start core-review --message go --name Nova {AGAIN[len('team start core-review '):]}"
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "S,g,o,shift+tab,N,o,v,a,enter")
    if done.returncode == 0 and house.gestures() == [named]:
        held("S names the first task", named)
    else:
        failures.append(f"  ✗ named                       rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r}")

    # --- the season of before again, a start refused, a declaration refused ----------------------------------------
    house.use(REFUSING)
    shown = house.render("--render", "teams", *SIZE, "--press", "S")
    title = P.title_of(shown.stdout) or [""]
    n = T.CORE["season"]["n"]
    added = _line(shown.stdout, "scribe", "agents/scribe")
    reviewer = _line(shown.stdout, "reviewer", "agents/reviewer")
    preview = T.overlay_preview(shown, "./pp team start")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "S,ctrl+s")
    remedy = T.remedy_of(done)
    if (shown.returncode == 0 and T.in_order(title[0], "core-review", str(n), str(n + 1)) and added
            and "agents/scribe" not in [one["path"] for one in T.CORE["members"]] and reviewer[3:4] == ["sonnet"]
            and preview == f"./pp {AGAIN}" and done.returncode == 0 and house.gestures() == [AGAIN]):
        held("a new season composes the season of before", f"{title[0]!r}; {AGAIN}")
    else:
        failures.append(f"  ✗ new season                  rc={shown.returncode},{done.returncode} {title} {added} "
                        f"{preview!r} {house.gestures()} {shown.stdout[-2500:]!r} {shown.stderr[-400:]!r}")
    if done.returncode == 0 and remedy == ERR.strip():
        held("a refused start: the refusal said", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {remedy!r} {done.stdout[-700:]!r}")

    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "down,S,ctrl+s")
    remedy = T.remedy_of(done)
    code = T.REFUSED["verdict"]["refusal"].split(" -- ")[0]
    if done.returncode == 0 and code in remedy.split() and P.overlay_rows(done.stdout) == [] and house.gestures() == []:
        held("a refused declaration opens nothing", remedy[:90])
    else:
        failures.append(f"  ✗ refused declaration         rc={done.returncode} {remedy!r} {house.gestures()} "
                        f"{done.stdout[-1500:]!r}")
    return 0
