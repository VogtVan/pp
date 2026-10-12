"""Scenario `ui-team-ring` -- a ceremony rung at hand from its overlay, and a ceremony leading to its task
(plan ui, batches les-ceremonies-au-poste and les-deux-onglets), on the bench's `pp-team` witness replaying
`CEREMONIAL`:
- `g` on the Teams tab opens the ceremonies, the command of the ring of the one under the cursor shown under
  them; `g` again plays it word for word; `escape` plays nothing; the team read again after it
- the `as` chosen in the overlay rides the ring: `--as pm`; the owner writes none
- a refusal of the verb -- `ceremony-open` -- on the remedy line as the verb said it
- `enter` on a ceremony: the Tasks tab shown, every task of the team, its cursor on the task of the last ring,
  its band and its last event; a ceremony never rung says so in the overlay
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

RING = "./pp team ring core-review daily"
AS_PM = "c,tab,space,down,enter"
OPEN = ("pp-team: ceremony-open -- T5 of `retro` is open: one ring at a time, ring again once it is resolved "
        "or stopped.\n")


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    states = {"core-review": [T.CEREMONIAL], "veille": [{"team": "veille", "started": None}]}
    house = T.Teams(bench, "ui-team-ring", T.script(states=states))

    # --- g: shown, then played; escape plays nothing ------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "g")
    preview = T.preview_in(shown, "./pp team ring")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "g,g")
    played, journal = house.gestures(), house.journal_lines()
    reread = bool(played) and "status core-review" in journal[journal.index(played[0]) + 1:]
    house.clear_journal()
    none = house.render("--render", "teams", "--size", "130x40", "--press", "g,escape")
    if (shown.returncode == 0 and done.returncode == 0 and preview == RING and played == [RING[len("./pp "):]]
            and reread and none.returncode == 0 and house.gestures() == []):
        held("g rings the ceremony under the cursor", f"{preview!r} shown, played as shown, the team read again; "
             "escape plays nothing")
    else:
        failures.append(f"  ✗ ring                        rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{journal} {house.gestures()} {shown.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- the as of the line ---------------------------------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", AS_PM)
    preview = T.preview_in(shown, "./pp team ring")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", AS_PM + ",g")
    played = house.gestures()
    if shown.returncode == 0 and done.returncode == 0 and preview == RING + " --as pm" and played == [preview[len("./pp "):]]:
        held("the as chosen rides the ring", preview)
    else:
        failures.append(f"  ✗ as pm                       rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-1200:]!r}")

    # --- a refusal on the remedy line ----------------------------------------------------------------
    house.use(T.script(states=states, answers={"ring": {"rc": 2, "err": OPEN}}))
    done = house.render("--render", "teams", "--size", "130x40", "--press", "c,down,g")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and "ceremony-open" in remedy and "T5 of `retro` is open" in remedy:
        held("a refusal goes to the remedy line as said", remedy[:100])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {remedy!r} {done.stdout[-900:]!r}")
    house.use(T.script(states=states))

    # --- enter: from a ceremony to its task ----------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "c,enter")
    flat, journal = _flat(done.stdout), house.journal_lines()
    if done.returncode == 0 and "T2 · resolved" in flat and "last: #40 done" in flat and not house.alive():
        held("enter leads a ceremony to its task", "daily: the Tasks tab, its cursor on T2, its band and its last "
             "event (#40 done)")
    else:
        failures.append(f"  ✗ enter daily                 rc={done.returncode} {journal} {done.stdout[-1400:]!r} "
                        f"{done.stderr[-300:]!r}")
    done = house.render("--render", "teams", "--size", "130x40", "--press", "c,down,down,enter")
    flat = _flat(done.stdout)
    if done.returncode == 0 and "review was never rung: no task to show" in flat:
        held("a ceremony never rung says so", "review was never rung: no task to show")
    else:
        failures.append(f"  ✗ enter review                rc={done.returncode} {done.stdout[-900:]!r}")
    return 0
