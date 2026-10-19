"""Scenario `ui-team-budget` -- `B` raises the budget of the team chosen, on the bench's `pp-team` witness:
- `B` opens an overlay titled by the team, prefilled from `team status --json`: `budget` 2.00 (its cap), `wakes` 40
  (its bound), the figures spent/cap, reserved, left and the wake-ups launched/bound said above the fields
- nothing changed plays nothing, and says why where the command stands otherwise, the overlay open
- only a field CHANGED composes its argument -- `team budget core-review 5`, shown then played
- the wake-ups changed alone: `team budget core-review --wakes 60`
- a refusal of the verb goes to the remedy line by its code, `budget-invalid`
- a team without `budget:` opens with the field empty: `team budget ops 3`
- under `--styles` the titles `Budget`, `Wakes`, `As` bold and the free fields left empty showing their examples
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "130x40")
ERASE = ",".join(["backspace"] * 4)






def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-budget")

    def played(keys: str):
        house.clear_journal()
        done = house.render("--render", "teams", *SIZE, "--press", keys)
        return done, house.gestures()

    # --- B: the overlay of core-review, prefilled from its face -----------------------------------------------
    face = T.CORE
    budget, wakes = face["budget"], face["wakes"]
    shown = house.render("--render", "teams", *SIZE, "--press", "B")
    rows, title = P.overlay_rows(shown.stdout), P.title_of(shown.stdout)
    figures = (f"{budget['spent']:.2f}/{budget['cap']:.2f}", f"{budget['reserved']:.2f}", f"{budget['left']:.2f}",
               f"{wakes['launched']}/{wakes['bound']}")
    if (shown.returncode == 0 and len(title) == 2 and face["team"] in title[0].split() and T.in_order(title[1], *figures)
            and P.field_of(rows, "budget") == [f"{budget['cap']:.2f}"] and P.field_of(rows, "wakes") == [str(wakes["bound"])]
            and not P.under_fields(rows)):
        held("B opens prefilled from the face", f"{face['team']}: {' · '.join(figures)} above the fields, "
             f"{budget['cap']:.2f} and {wakes['bound']} in them")
    else:
        failures.append(f"  ✗ prefilled                   rc={shown.returncode} {title} {rows!r} {shown.stderr[-400:]!r}")

    # --- nothing changed, enter: nothing played, the reason under the fields -------------------------------------
    done, gestures = played("B,enter")
    said = P.under_fields(P.overlay_rows(done.stdout))
    if (done.returncode == 0 and gestures == [] and P.title_of(done.stdout) == title and said
            and not any(row.startswith("./pp") for row in said)):
        held("nothing changed plays nothing", "said under the fields")
    else:
        failures.append(f"  ✗ unchanged                   rc={done.returncode} {gestures} {said} {done.stdout[-900:]!r}")

    # --- a field changed alone: its argument alone -----------------------------------------------------------
    preview = T.preview_in(house.render("--render", "teams", *SIZE, "--press", f"B,{ERASE},5"), "./pp team budget")
    done, gestures = played(f"B,{ERASE},5,enter")
    if done.returncode == 0 and preview == f"./pp team budget {face['team']} 5" and gestures == [preview[len("./pp "):]]:
        held("the budget changed alone", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ budget                      rc={done.returncode} {preview!r} {gestures} {done.stdout[-900:]!r}")

    done, gestures = played("B,tab,backspace,backspace,6,0,enter")
    if done.returncode == 0 and gestures == [f"team budget {face['team']} --wakes 60"]:
        held("the wake-ups changed alone", gestures[0])
    else:
        failures.append(f"  ✗ wakes                       rc={done.returncode} {gestures} {done.stdout[-900:]!r}")

    # --- a refusal of the verb: its code on the remedy line ----------------------------------------------------
    house.use(T.script(answers={"budget": {"rc": 2, "err": "pp-team: budget-invalid -- 1 is at or below what the "
                                                         "team spent since its start (1.84 USD).\n"}}))
    done, gestures = played(f"B,{ERASE},1,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and gestures == [f"team budget {face['team']} 1"] and "budget-invalid" in remedy.split():
        held("a refusal goes to the remedy line as said", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {gestures} {remedy!r} {done.stdout[-700:]!r}")

    # --- a team without budget: the field empty, its example in its place, the titles bold ---------------------
    house.use(T.script())
    done, gestures = played("down,B,3,enter")
    if done.returncode == 0 and gestures == ["team budget ops 3"]:
        held("a team without budget: starts empty", gestures[0])
    else:
        failures.append(f"  ✗ no budget                   rc={done.returncode} {gestures} {done.stdout[-900:]!r}")

    styled = house.render("--render", "teams", "--size", "120x60", "--press", "down,B", "--styles")
    bare = P.ANSI.sub("", styled.stdout)
    titles = [P.field_title(one) for one in ("budget", "wakes", "as")]
    examples = [P.palette_constant("BUDGET_EXAMPLE"), P.palette_constant("WAKES_EXAMPLE")]
    looks = {one: T.look_of(styled.stdout, one) for one in titles}
    if (styled.returncode == 0 and all(one and one[0] for one in looks.values())
            and all(one in bare for one in examples)):
        held("the form reads at a glance", f"{', '.join(titles)} bold; {', '.join(examples)} in the empty fields")
    else:
        failures.append(f"  ✗ looks                       rc={styled.returncode} {looks} {bare[-1500:]!r}")
    return 0
