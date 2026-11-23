"""Scenario `ui-spaces-list` -- the spaces that do not fit and what the row refuses to play (plan ui, batch
les-boutons-des-espaces), on the bench's `pp-chat` witness:
- the row folds (batch les-espaces-sans-overlay): twelve openable spaces at 100 columns draw a button each, on as
  many rows as they need, no `… +n`, no list of the spaces and no `e` for it in the footer; the last button plays as the first, the message typed
  as its text (batch le-bouton-et-la-bulle)
- a refusal is said: the run opened `DEEP` between the block the post read and the click -- the witness, as the engine,
  refuses `space-open` with the stack in its detail --, the wait lifts and the remedy says the refusal
- `e` binds nothing on a conversation (part 2): on the bench's `pp-team` witness, `e` is bound on the Tasks tab
  (its recurrences) and not once the dialogue is shown -- Textual's active bindings, read by the pilot
What the row refuses to play, and a run without a space: `ui-spaces-turn`.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
T = support(__file__, "teams")
SIZE = ("--size", "100x30")
TURN = "i,h,i,ctrl+enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-spaces-list", P.spaces_script(openable=P.MANY_OPENABLE))
    render = post.render
    names = [one["name"] for one in P.MANY_OPENABLE]

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("space ")]

    # --- the row folds: every space a button, on as many rows as they need ----------------------------------------
    rest = render("ag1", "--render", "dialogue", *SIZE, "--press", TURN)
    rows = P.spaces_rows(rest.stdout)
    shown = [name for name in names if any(f"+ {name}" in row for row in rows)]
    post.clear_journal()
    last = render("ag1", "--render", "dialogue", *SIZE, "--press",
                  f"{TURN},o,k,click:#space-open-{len(names)}:1:0,wait:space")
    if (rest.returncode == 0 and shown == names and len(rows) > 1 and not any("…" in row for row in rows)
            and not P.entry_of(rest.stdout, "e") and last.returncode == 0 and sent() == [P.spaced("ag1", {"kind": "open", "name": names[-1], "text": "ok"})]):
        held("the row folds, every space a button", f"{len(shown)} buttons on {len(rows)} rows, no … +n, no [e] in the footer; the last "
             f"sent {sent()[0]!r}")
    else:
        failures.append(f"  ✗ fold                        rc={rest.returncode} rows={rows} shown={shown} {sent()} "
                        f"{P.entry_of(rest.stdout, 'e')!r} "
                        f"{last.stderr[-300:]!r}")

    # --- a refusal is said ----------------------------------------------------------------------------------
    post.use(P.spaces_script(openable=[{"name": "DEEP", "segment": None}], opened=["DEEP"]))
    post.clear_journal()
    refused = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},o,k,click:#space-open-1:1:0,wait:refused")
    remedy, status = P.remedy_of(refused.stdout), P.status_of(refused.stdout)
    if (refused.returncode == 0 and "space-open" in remedy and "DEEP" in remedy
            and "open DEEP" not in status and sent() == [P.spaced("ag1", {"kind": "open", "name": "DEEP", "text": "ok"})]):
        held("a refusal is said", f"{remedy[:90]!r}; the status waits no more")
    else:
        failures.append(f"  ✗ refused                     rc={refused.returncode} {remedy!r} {status!r} {sent()} "
                        f"{refused.stderr[-300:]!r}")

    # --- e binds nothing on a conversation --------------------------------------------------------------------------
    house = T.Teams(bench, "ui-spaces-list-e")
    [(rc, seen, err)] = T.piloted(bench, house, "ui-spaces-list-e", PROBE, "tasks", size="130x40")
    if rc == 0 and seen == {"tasks": True, "dialogue": False}:
        held("e binds nothing on a conversation", f"the active bindings name e: {seen}")
    else:
        failures.append(f"  ✗ e                           rc={rc} {seen} {err[-600:]!r}")
    return 0


# whether `e` is among the active bindings on the Tasks tab, then once the dialogue is shown
PROBE = """
async def probe(app, pilot, view, out):
    def bound():
        return any(one.binding.key == "e" for one in app.active_bindings.values())
    out["tasks"] = bound()
    app.show_pane("dialogue")
    await app.pane_settled()
    await pilot.pause()
    out["dialogue"] = bound()
"""
