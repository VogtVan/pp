"""Scenario `ui-team-budget` -- `B`, the budget of the team chosen raised (plan ui, batch les-overlays-des-gestes),
on the bench's `pp-team` witness:
- `B` opens an overlay prefilled from `team status --json`: `budget` 2.00 (its cap), `wakes` 40 (its bound), the
  state `spent/cap · reserved · left` and the wake-ups said above them
- only a field CHANGED composes its argument -- `team budget core-review 5`, `team budget core-review --wakes 60`;
  nothing changed plays nothing and says so
- a refusal of the verb (`budget-invalid`) goes to the remedy line as the verb said it
- a team without `budget:` opens with the field empty: `team budget ops 3`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

ERASE = ",".join(["backspace"] * 4)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-budget")

    def played(keys: str):
        house.clear_journal()
        done = house.render("--render", "teams", "--size", "130x40", "--press", keys)
        return done, house.gestures()

    shown = house.render("--render", "teams", "--size", "130x40", "--press", "B")
    flat = " ".join(shown.stdout.split())
    if (shown.returncode == 0 and "raise the budget of core-review" in flat and "budget 1.84/2.00 USD" in flat and "left 0.06" in flat and "wakes 7/40" in flat
            and "2.00" in flat and "40" in flat):
        held("B opens prefilled from the face", "budget 1.84/2.00 USD · reserved 0.10 · left 0.06 · wakes 7/40")
    else:
        failures.append(f"  ✗ prefilled                   rc={shown.returncode} {shown.stdout[-1500:]!r} {shown.stderr[-400:]!r}")

    done, gestures = played("B,enter")
    if done.returncode == 0 and gestures == [] and "nothing changed" in " ".join(done.stdout.split()):
        held("nothing changed plays nothing", "said under the fields")
    else:
        failures.append(f"  ✗ unchanged                   rc={done.returncode} {gestures} {done.stdout[-900:]!r}")

    preview = T.preview_in(house.render("--render", "teams", "--size", "130x40", "--press", f"B,{ERASE},5"),
                           "./pp team budget")
    done, gestures = played(f"B,{ERASE},5,enter")
    if done.returncode == 0 and preview == "./pp team budget core-review 5" and gestures == [preview[len("./pp "):]]:
        held("the budget changed alone", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ budget                      rc={done.returncode} {preview!r} {gestures} {done.stdout[-900:]!r}")

    done, gestures = played("B,tab,backspace,backspace,6,0,enter")
    if done.returncode == 0 and gestures == ["team budget core-review --wakes 60"]:
        held("the wake-ups changed alone", gestures[0])
    else:
        failures.append(f"  ✗ wakes                       rc={done.returncode} {gestures} {done.stdout[-900:]!r}")

    house.use(T.script(answers={"budget": {"rc": 2, "err": "pp-team: budget-invalid -- 1 is at or below what the "
                                                         "team spent since its start (1.84 USD).\n"}}))
    done, gestures = played(f"B,{ERASE},1,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and gestures == ["team budget core-review 1"] and "budget-invalid -- 1 is at or below" in remedy:
        held("a refusal goes to the remedy line as said", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {gestures} {remedy!r} {done.stdout[-700:]!r}")

    house.use(T.script())
    done, gestures = played("down,B,3,enter")
    if done.returncode == 0 and gestures == ["team budget ops 3"]:
        held("a team without budget: starts empty", gestures[0])
    else:
        failures.append(f"  ✗ no budget                   rc={done.returncode} {gestures} {done.stdout[-900:]!r}")
    return 0
