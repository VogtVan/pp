"""Scenario `ui-team-gestures` -- writing on a task in its overlay, what `ctrl+enter` plays read from the journal of the
bench's `pp-team` witness, no command shown on screen:
- `m` on T3 (the first task running): an overlay titled by the task and its team, `to` / `as` / `reply to` read from
  `team status --json` (the members, the owner and the principals, the questions of the task), then the text --
  `post core-review --task T3 --to reviewer --reply 45 --as pm --message ok`; the tasks read again after it
- the owner writes no `--as`; a text on two lines (`enter` goes to the line) leaves whole; the note goes to the root by
  default (`--to lead`)
- the keys (batch les-touches-du-poste): `enter` on a closed list goes to the next field and plays nothing -- the ask
  below reaches its `kind` from the text it lands on --; `ctrl+j`, the name a terminal gives `ctrl+enter`, plays
- its `kind` (ui 1.10.35, s.1816): `info` at the opening -- no flag --; `ask` chosen plays `--ask`; a reply is neither
- a reply chosen, `to` left as it is: no `--to`, the reply goes to the author of the question; `ask` beside a reply
  plays nothing, the overlay kept; the root marked in the list `to` and chosen at the opening of a note (s.1816)
(a new task, `n`: `ui-tasks-new-task`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture

TYPED = "m,o,k,shift+tab,space,down,enter,shift+tab,space,down,enter,shift+tab,space,down,down,enter"
#        the text, a reply chosen -- `to` blank --, `as` on pm, `to` chosen on reviewer, past the blank and lead
POST = "team post core-review --task T3 --to reviewer --reply 45 --as pm --message ok --no-tick"
TWO_LINES = "team post core-review --task T3 --to lead --message 'ok\ngo'"
ASKED = "team post core-review --task T3 --to lead --ask --message ok --no-tick"
REPLIED = "team post core-review --task T3 --reply 45 --message ok --no-tick"
REPLY = "shift+tab,space,down,enter"              # from the text: `reply to` set on the task's question
ASK = "shift+tab,shift+tab,shift+tab,space,down,enter"   # from `reply to`: `kind` set on `ask`
TASK = next(one for one in T.CORE["tasks"] if one["id"] == "T3")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-gestures")

    # --- m: the line, its lists, what it plays --------------------------------------------------------
    shown = house.render("--render", "tasks", "--size", "200x50", "--press", TYPED)
    title = " ".join(P.title_of(shown.stdout))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "200x50", "--press", TYPED + ",ctrl+enter")
    played = house.gestures()
    journal = house.journal_lines()
    reread = played and journal.index(played[0]) < len(journal) - 1 and \
        "status core-review" in journal[journal.index(played[0]) + 1:]
    if (shown.returncode == 0 and done.returncode == 0 and played == [POST] and "./pp" not in shown.stdout
            and reread and T.in_order(title, TASK["id"], TASK["name"], T.CORE["team"])):
        held("m plays the fields of its overlay", f"{played[0]!r}, no command on screen; the tasks read again after it")
    else:
        failures.append(f"  ✗ the line                    rc={shown.returncode},{done.returncode} {played} "
                        f"{title!r} {journal} {shown.stdout[-1600:]!r} {done.stderr[-400:]!r}")

    # --- m by the owner: no --as, a text on two lines -------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "m,o,k,enter,g,o,ctrl+j")
    raw = house.journal.read_text(encoding="utf-8") if house.journal.is_file() else ""
    if done.returncode == 0 and TWO_LINES in raw and "--as" not in raw:
        held("the owner writes no --as", TWO_LINES.split(" --message")[0])
        held("a text on two lines leaves whole, ctrl+j plays", "--message 'ok\\ngo'")
    else:
        failures.append(f"  ✗ owner, two lines            rc={done.returncode} {raw!r} {done.stdout[-900:]!r}")

    # --- m as a question: the kind `ask` -------------------------------------------------------------------
    house.clear_journal()
    asked = house.render("--render", "tasks", "--size", "130x40", "--press",
                         "m,o,k,shift+tab,enter,shift+tab,shift+tab,shift+tab,shift+tab,space,down,enter,ctrl+enter")
    if asked.returncode == 0 and house.gestures() == [ASKED]:
        held("m asks a question, enter on a list plays nothing", f"enter on reply to: back to the text; kind ask: {ASKED!r}")
    else:
        failures.append(f"  ✗ ask                         rc={asked.returncode} {house.gestures()} {asked.stdout[-900:]!r}")

    # --- m as a reply: to its author; an ask beside it plays nothing; the root marked ---------------------
    house.clear_journal()
    replied = house.render("--render", "tasks", "--size", "130x40", "--press", f"m,o,k,{REPLY},ctrl+enter")
    played = house.gestures()
    house.clear_journal()
    refused = house.render("--render", "tasks", "--size", "130x40", "--press", f"m,o,k,{REPLY},{ASK},ctrl+enter")
    kept = [one for one in P.overlay_rows(refused.stdout) if one]
    if replied.returncode == 0 and played == [REPLIED] and refused.returncode == 0 and house.gestures() == [] and kept:
        held("a reply goes to its author, an ask beside it plays nothing", f"{REPLIED!r}; kind ask with the reply: "
             f"nothing played, the overlay kept ({len(kept)} rows)")
    else:
        failures.append(f"  ✗ reply and ask               rc={replied.returncode}/{refused.returncode} {played} "
                        f"{house.gestures()} {refused.stdout[-900:]!r}")
    [(rc, seen, err)] = T.piloted(bench, house, "ui-team-gestures", PROBE, "tasks", size="130x40")
    options, root = seen.get("options") or [], T.CORE.get("root")
    marked = [value for prompt, value in options if prompt != value]
    if (rc == 0 and options and marked == [root] and any(prompt.startswith(root) and prompt != root
                                                          for prompt, value in options if value == root)
            and seen.get("value") == root):
        held("the root marked in the list to", f"{root} the one option whose prompt is not its value, chosen at the "
             f"opening; {len(options)} options")
    else:
        failures.append(f"  ✗ root marked                 rc={rc} {seen} {err[-900:]!r}")
    return 0


# the options of the field `to` of `m` and its value at the opening
PROBE = """
from panes.overlays import GestureScreen


async def probe(app, pilot, view, out):
    table = app.query_one("#tasks-list")
    if not await until(pilot, lambda: table.row_count > 0, 8):
        return
    await pilot.press("m")
    if not await until(pilot, lambda: isinstance(app.screen, GestureScreen), 5):
        return
    field = next(one for one in app.screen.fields if one.key == "to")
    out["options"] = [[str(prompt), value] for prompt, value in field.options]
    out["value"] = app.screen.values().get("to")
"""
