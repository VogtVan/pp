"""Scenario `ui-team-season` -- `S` opens the SEASON of the team chosen (plan ui, batch l-overlay-de-saison), on the
bench's witnesses -- the declaration (`team declaration --json`, its `declared`), the team's face (`status --json`, its
`season`, `launch`, `members[].launch`) and the agents of the members (`agent status --json`, their `last`):
- `veille`, never started, its agents never played: « first season of veille », a line `all` and one per member of
  `declared`; no message, nothing played; a message typed, `ctrl+s` plays `team start veille --message go` alone
- the same team, its agents played before: the lines prefilled from their `last` -- `all` from the root's agent, a
  member `·` where it is `all` --, and the command carries what `all` holds, then what a member changes
- `core-review`, at work: « new season of core-review (season 1 -> 2) », a member `declared` adds shown; `ctrl+s` with
  nothing changed and no message plays the season of before again -- `all` from `launch`, the member that differed,
  the budget the season gave itself above `TEAM.md`'s
- a member edited in its profile composes its own `--member`
- a declaration `start` would refuse opens nothing: the refusal on the remedy line, nothing played
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

SIZE = ("--size", "130x60")
TO_TABLE = "shift+tab,shift+tab"         # from the message of the first task up to the lines: the name, the table
P = T.D.PROVIDER


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- a first season, its agents never played -------------------------------------------------------------
    bare = T.Teams(bench, "ui-team-season")
    bare.clear_journal()
    empty = bare.render("--render", "teams", *SIZE, "--press", "down,down,S,ctrl+s")
    flat = _flat(empty.stdout)
    rows = [one for one in empty.stdout.split("\n") if "scout" in one or "writer" in one]
    if (empty.returncode == 0 and "first season of veille" in flat and len(rows) >= 2
            and "the team's first message" in flat and bare.gestures() == []):
        held("a first season shows its members, nothing played without a message",
             f"first season of veille; {len(rows)} lines of members; the gap said")
    else:
        failures.append(f"  ✗ first season shown          rc={empty.returncode} {bare.gestures()} {empty.stdout[-2500:]!r} "
                        f"{empty.stderr[-400:]!r}")

    bare.clear_journal()
    done = bare.render("--render", "teams", *SIZE, "--press", "down,down,S,g,o,ctrl+s")
    if done.returncode == 0 and bare.gestures() == ["team start veille --message go"]:
        held("a first season of agents never played starts bare", bare.gestures()[0])
    else:
        failures.append(f"  ✗ first season bare           rc={done.returncode} {bare.gestures()} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- a first season, its agents played before -------------------------------------------------------------
    house = T.Teams(bench, "ui-team-season-last", agents=T.SEASON_AGENTS)
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "down,down,S")
    writer = next((one for one in shown.stdout.split("\n") if "writer" in one and "agents/writer" in one), "")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "down,down,S,g,o,ctrl+s")
    wanted = f"team start veille --message go --provider {P} --model opus --effort high --member writer --model sonnet"
    if (shown.returncode == 0 and "sonnet" in writer and "·" in writer and done.returncode == 0
            and house.gestures() == [wanted]):
        held("a first season prefilled from the agents' last", f"{writer.strip(' ┃│')[:70]!r}; {wanted}")
    else:
        failures.append(f"  ✗ first season prefilled      rc={shown.returncode},{done.returncode} {writer!r} "
                        f"{house.gestures()} {shown.stdout[-2500:]!r} {done.stderr[-400:]!r}")

    # --- a new season: the season of before composed again --------------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "S")
    flat = _flat(shown.stdout)
    scribe = next((one for one in shown.stdout.split("\n") if "scribe" in one and "agents/scribe" in one), "")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "S,ctrl+s")
    again = (f"team start core-review --budget 2 --provider {P} --model opus --effort high "
             f"--member reviewer --model sonnet --package plan=off")
    if (shown.returncode == 0 and "new season of core-review (season 1 -> 2)" in flat and scribe
            and done.returncode == 0 and house.gestures() == [again]):
        held("a new season composes the season of before", again)
    else:
        failures.append(f"  ✗ new season                  rc={shown.returncode},{done.returncode} {scribe!r} "
                        f"{house.gestures()} {shown.stdout[-2500:]!r} {done.stderr[-400:]!r}")

    # --- a member edited ------------------------------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", f"S,{TO_TABLE},down,enter,h,a,i,k,u,enter,ctrl+s")
    edited = (f"team start core-review --budget 2 --provider {P} --model opus --effort high --member lead --model haiku "
              f"--member reviewer --model sonnet --package plan=off")
    if done.returncode == 0 and house.gestures() == [edited]:
        held("a member edited composes its own --member", edited)
    else:
        failures.append(f"  ✗ member edited               rc={done.returncode} {house.gestures()} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- a declaration start would refuse ------------------------------------------------------------------------
    house.use(T.script(declarations={**T.DECLARATIONS, "ops": T.REFUSED}))
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "down,S,g,o,ctrl+s")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and "team-invalid" in remedy and "season of ops" not in done.stdout and house.gestures() == []:
        held("a refused declaration opens nothing", remedy[:90])
    else:
        failures.append(f"  ✗ refused declaration         rc={done.returncode} {remedy!r} {house.gestures()} "
                        f"{done.stdout[-1500:]!r}")
    return 0
