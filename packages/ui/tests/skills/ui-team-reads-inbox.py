"""Scenario `ui-team-reads-inbox` -- the owner's inbox of a team in an overlay, playing nothing, and the gestures it
leads to (cut from `ui-team-reads`, rule 10), on the bench's `pp-team` witness:
- `b` reads `team inbox <team> --json` and shows the questions waiting for the owner, the tasks done and the posts
  returned, each by its ids and its words, no command shown; nothing played
- `a` in the inbox plays `team inbox <team> --seen`, all read (ui 1.4.6: `x` reads one message); `escape` plays nothing
- `enter` on a question opens the overlay that writes on its task, the question chosen: `enter` there plays
  `team post <team> --task <task> --reply <id> --message <text>`, as the witness's journal says it
- the infos stand in the inbox (batch l-inbox-et-les-taches): two `info` lines between the notices and the tasks done,
  the latest first (s.1585), one of them a note of before said so; `enter` on an info opens no reply -- the inbox stays on top as it was
- an inbox where nothing waits shows its title, no post in its body
"""
from __future__ import annotations

import json
import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "130x40")
INSTANT = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d")
QUESTION = {"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "text": "tests green?"}
DONE = {"task": "T2", "id": 40}
RETURNED = {"id": 33, "verb": "note", "from": "house", "task": "T1", "text": "the deadline moved"}
INFOS = [{"id": 46, "verb": "info", "from": "reviewer", "task": "T3", "text": "build green"},
         {"id": 47, "verb": "info", "from": "core-review", "task": "T3", "text": "lead is back", "was": "note"}]
INBOX = {"core-review": {"team": "core-review", "questions": [QUESTION], "infos": INFOS, "done": [DONE],
                         "returned": [RETURNED]}}
DECLARATIONS = {**T.DECLARATIONS, "ops": T.REFUSED}
CORE = DECLARATIONS["core-review"]
PENDING = {**CORE, "changed": True, "pending": [{"key": "root", "started": "lead", "declared": "reviewer"},
                                                {"key": "limits", "started": {"budget": 2.0},
                                                 "declared": {"budget": 5.0}}]}
REPLY = f"team post core-review --task {QUESTION['task']} --reply {QUESTION['id']} --message ok --no-tick"
SEEN = "team inbox core-review --seen"


def _body(done) -> list[str]:
    """-> the rows of the overlay of a render, blank ones left out, its title first."""
    return [one for one in P.overlay_rows(done.stdout) if one]


def _holds(row: str, *words: object) -> bool:
    return all(str(one) in row for one in words)


def _value(one: object) -> str:
    """-> a pending key's value as a row can hold it: a word as it is, any other value its JSON."""
    return one if isinstance(one, str) else json.dumps(one, ensure_ascii=False)


def _between(rows: list[str], started: dict, text: str) -> list[str] | None:
    """-> the rows between the start's row and the first line of `TEAM.md`, or None when either is missing."""
    at = next((n for n, row in enumerate(rows) if started["at"] in row), None)
    first = text.split("\n")[0]
    end = next((n for n, row in enumerate(rows) if at is not None and n > at and row == first), None)
    return rows[at + 1:end] if at is not None and end is not None else None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-reads-inbox", T.script(declarations=DECLARATIONS, inbox=INBOX))

    def shown(pane: str, keys: str):
        house.clear_journal()
        done = house.render("--render", pane, *SIZE, "--press", keys)
        return done, _body(done)

    # --- b: the inbox, a all read, escape nothing, a question answered ------------------------------------------
    done, rows = shown("teams", "b")
    lines = ((QUESTION["id"], QUESTION["verb"], QUESTION["from"], QUESTION["task"], QUESTION["text"]),
             (DONE["task"], DONE["id"]),
             (RETURNED["id"], RETURNED["verb"], RETURNED["from"], RETURNED["task"], RETURNED["text"]))
    found = [any(_holds(row, *(f"#{one}" if isinstance(one, int) else one for one in words)) for row in rows[1:])
             for words in lines]
    if (done.returncode == 0 and rows and "core-review" in rows[0] and all(found) and "./pp" not in done.stdout
            and "inbox core-review" in house.journal_lines() and house.gestures() == []):
        held("b shows the owner's inbox", f"#{QUESTION['id']} on {QUESTION['task']}, {DONE['task']} done, "
             f"#{RETURNED['id']} returned; no command; nothing played")
    else:
        failures.append(f"  ✗ the box                     rc={done.returncode} {found} "
                        f"{house.journal_lines()} {rows!r} {done.stderr[-400:]!r}")

    done, _ = shown("teams", "b,a")
    played = house.gestures()
    none, _ = shown("teams", "b,escape")
    if done.returncode == 0 and played == [SEEN] and none.returncode == 0 and house.gestures() == []:
        held("a marks the inbox all read", f"{played[0]}; escape plays nothing")
    else:
        failures.append(f"  ✗ seen                        rc={done.returncode} {played} {house.gestures()} "
                        f"{done.stdout[-900:]!r}")

    done, _ = shown("teams", "b,enter,o,k,ctrl+enter")
    played = house.gestures()
    if done.returncode == 0 and played == [REPLY]:
        held("enter on a question replies to it", f"{REPLY!r} played")
    else:
        failures.append(f"  ✗ reply                       rc={done.returncode} {played} "
                        f"{done.stdout[-1500:]!r} {done.stderr[-400:]!r}")

    # --- the infos stand in the inbox, between the notices and the tasks done; enter on one replies to nothing ---
    done, rows = shown("teams", "b")
    order = [next((n for n, row in enumerate(rows[1:]) if f"#{one}" in row or f"{one} done" in row), None)
             for one in (QUESTION["id"], INFOS[1]["id"], INFOS[0]["id"], DONE["task"], RETURNED["id"])]   # the latest first
    noted = next((row for row in rows[1:] if f"#{INFOS[1]['id']}" in row), "")
    staged, _ = shown("teams", "b,down,enter")
    on_top = [one for one in P.overlay_rows(P.on_top(staged.stdout)) if one]
    if (done.returncode == 0 and None not in order and order == sorted(order)
            and all(_holds(row, "info", one["from"], one["task"], one["text"]) for row, one in
                    ((next(row for row in rows[1:] if f"#{one['id']}" in row), one) for one in INFOS))
            and "note" in noted and staged.returncode == 0                     # the list as it was, the pane apart
            and [one for one in on_top if one.startswith("▊")] == [one for one in rows if one.startswith("▊")]
            and house.gestures() == []):
        held("the infos stand in the inbox", f"#{INFOS[1]['id']} (a note of before) then #{INFOS[0]['id']} between the "
             f"question and {DONE['task']} done; enter on one opens no reply")
    else:
        failures.append(f"  ✗ infos                       rc={done.returncode}/{staged.returncode} order={order} "
                        f"{noted!r} {house.gestures()} {rows!r} {on_top!r}")

    # --- an inbox where nothing waits ---------------------------------------------------------------------
    house.use(T.script(declarations=DECLARATIONS))
    done, rows = shown("teams", "b")
    if (done.returncode == 0 and rows and "core-review" in rows[0] and "./pp" not in done.stdout
            and not any(re.search(r"#\d+", row) for row in rows[1:])):
        held("an empty inbox says so", "its title, no post in its body, no command")
    else:
        failures.append(f"  ✗ empty                       rc={done.returncode} {rows!r}")
    return 0
