"""Scenario `ui-spaces-list` -- the list of the spaces and what the row refuses to play (plan ui, batch
les-boutons-des-espaces), on the bench's `pp-chat` witness:
- the overflow is counted and listed: twelve openable spaces at 100 columns draw the first buttons then `… +n`; `e`
  opens the list of every space, open ones first; `enter` on a line writes its command on the witness's entry; the
  `… +n` button opens the same list
- a refusal is said: the run opened `DEEP` between the block the post read and the click -- the witness, as the engine,
  refuses `space-open` with the stack in its detail --, the wait lifts and the remedy says the refusal
What the row refuses to play, and a run without a space: `ui-spaces-turn`.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "100x30")
TURN = "i,h,i,enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-spaces-list", P.spaces_script(openable=P.MANY_OPENABLE))
    render = post.render
    names = [one["name"] for one in P.MANY_OPENABLE]

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("space ")]

    # --- the overflow is counted and listed ------------------------------------------------------------------
    rest = render("ag1", "--render", "dialogue", *SIZE, "--press", TURN)
    row = P.spaces_row(rest.stdout)
    shown = [name for name in names if f"+ {name}" in row]
    more = row[row.index("…"):].strip() if "…" in row else ""
    listed = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},escape,e")
    rows = P.overlay_rows(listed.stdout)
    post.clear_journal()
    chosen = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},escape,e,enter,wait:space")
    by_button = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},click:#space-more:1:0")
    rows_button = P.overlay_rows(by_button.stdout)
    hidden = len(names) - len(shown)
    if (rest.returncode == 0 and 0 < len(shown) < len(names) and more == f"… +{hidden}"
            and listed.returncode == 0 and all(any(name in one for one in rows) for name in names)
            and chosen.returncode == 0 and sent() == [P.spaced("ag1", {"kind": "open", "name": names[0]})]
            and by_button.returncode == 0 and all(any(name in one for one in rows_button) for name in names)):
        held("the overflow is counted and listed", f"{len(shown)} buttons then {more!r}; e lists {len(names)} spaces; "
             f"enter sent {sent()[0]!r}; the button opens the list too")
    else:
        failures.append(f"  ✗ overflow                    rc={rest.returncode} {row!r} shown={shown} more={more!r} "
                        f"rows={rows[:14]} {sent()} {listed.stderr[-300:]!r}")

    # --- a refusal is said ----------------------------------------------------------------------------------
    post.use(P.spaces_script(openable=[{"name": "DEEP", "segment": None}], opened=["DEEP"]))
    post.clear_journal()
    refused = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},click:#space-open-1:1:0,wait:refused")
    remedy, status = P.remedy_of(refused.stdout), P.status_of(refused.stdout)
    if (refused.returncode == 0 and "space-open" in remedy and "DEEP" in remedy
            and "open DEEP" not in status and sent() == [P.spaced("ag1", {"kind": "open", "name": "DEEP"})]):
        held("a refusal is said", f"{remedy[:90]!r}; the status waits no more")
    else:
        failures.append(f"  ✗ refused                     rc={refused.returncode} {remedy!r} {status!r} {sent()} "
                        f"{refused.stderr[-300:]!r}")

    return 0
