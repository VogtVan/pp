"""Scenario `ui-team-reads` -- what the tabs of the teams read and show in an overlay, playing nothing, and the two
gestures the inbox leads to, on the bench's `pp-team` witness:
- `l` on the Teams tab reads `team log <team> --json` and shows every event of the journal, by its id, in an overlay
  titled by the team
- the band of a resolved task on the Tasks tab reads `team result <team> <task>` and shows each key of its
  JSON with its value; on an open task the verb's refusal, `task-open`, goes to the remedy line, no overlay opened
- outside the Teams and Tasks tabs `l` and `v` call nothing of `team`
- `e` reads `team declaration <team> --json` and shows, in an overlay titled by the team and its path, the path, the
  instant of the start, `TEAM.md` whole, one row between the start and the text when nothing is pending; nothing
  played
- a declaration `start` would refuse shows the refusal's code, `team-invalid`
- a team never started dates no start
- `b` reads `team inbox <team> --json` and shows the questions waiting for the owner, the tasks done and the posts
  returned, each by its ids and its words, with the command of `x` under them; nothing played
- `x` in the inbox plays `team inbox <team> --seen`; `escape` plays nothing
- `enter` on a question opens the overlay that writes on its task, the question chosen: `enter` there plays
  `team post <team> --task <task> --reply <id> --message <text>`, as shown
- the keys a start would change stand one row each, the key, its started value and its declared value, under the
  start
- `e` plays nothing: the journal holds readings alone
- an inbox where nothing waits shows its title and its command, no post in its body
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
INBOX = {"core-review": {"team": "core-review", "questions": [QUESTION], "done": [DONE], "returned": [RETURNED]}}
DECLARATIONS = {**T.DECLARATIONS, "ops": T.REFUSED}
CORE = DECLARATIONS["core-review"]
PENDING = {**CORE, "changed": True, "pending": [{"key": "root", "started": "lead", "declared": "reviewer"},
                                                {"key": "limits", "started": {"budget": 2.0},
                                                 "declared": {"budget": 5.0}}]}
REPLY = f"team post core-review --task {QUESTION['task']} --reply {QUESTION['id']} --message ok"
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
    house = T.Teams(bench, "ui-team-reads", T.script(declarations=DECLARATIONS, inbox=INBOX))

    def shown(pane: str, keys: str):
        house.clear_journal()
        done = house.render("--render", pane, *SIZE, "--press", keys)
        return done, _body(done)

    # --- l: the whole journal of the team -------------------------------------------------------------------
    done, rows = shown("teams", "l")
    ids = [f"#{one['id']}" for one in T.TEAM_LOG]
    firsts = [row.split()[0] for row in rows[1:] if row.split()]
    if (done.returncode == 0 and rows and "core-review" in rows[0] and all(one in firsts for one in ids)
            and "log core-review" in house.journal_lines() and house.gestures() == []):
        held("l shows the whole journal", f"team log core-review --json in an overlay, {ids[0]} to {ids[-1]}")
    else:
        failures.append(f"  ✗ journal                     rc={done.returncode} {house.journal_lines()} {rows!r} "
                        f"{done.stderr[-300:]!r}")

    # --- a resolved task's result in its band, an open task's refusal to v -------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--press", "shift+tab,shift+tab,down,down,tab,tab,down")
    rows = [one.split("│", 1)[-1].strip(" │") for one in done.stdout.split("\n")]
    value = T.RESULTS["core-review/T2"]
    pairs = [f"{json.dumps(key)}: {json.dumps(one)}" for key, one in value.items()]
    if (done.returncode == 0 and all(any(row.strip().rstrip(",") == pair for row in rows) for pair in pairs)
            and "result core-review T2" in house.journal_lines()):
        held("a resolved task's result in its band", f"team result core-review T2, {', '.join(pairs)}")
    else:
        failures.append(f"  ✗ result                      rc={done.returncode} {house.journal_lines()} {rows!r}")

    done, rows = shown("tasks", "v")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and not rows and "task-open" in remedy.split() and "T3" in remedy.split():
        held("v on an open task: the refusal on the remedy line", remedy)
    else:
        failures.append(f"  ✗ result refused              rc={done.returncode} {remedy!r} {rows!r} {done.stdout[-600:]!r}")

    done, _ = shown("dialogue", "l,v")
    played = house.journal_lines()
    if done.returncode == 0 and played == []:
        held("l and v act on the tabs of the teams alone", "no call of team from the dialogue")
    else:
        failures.append(f"  ✗ keys elsewhere              rc={done.returncode} {played}")

    # --- e: the declaration, refused, never started ---------------------------------------------------------
    done, rows = shown("teams", "e")
    between = _between(rows, CORE["started"], CORE["text"])
    text = [one.strip() for one in CORE["text"].split("\n") if one.strip()]
    if (done.returncode == 0 and rows and _holds(rows[0], "core-review", CORE["path"])
            and any(row.split()[-1:] == [CORE["path"]] for row in rows[1:]) and between is not None
            and len(between) == 1 + len(CORE["pending"]) and rows[-1 - len(text):-1] == text
            and "declaration core-review" in house.journal_lines() and house.gestures() == []):
        held("e shows the declaration", "its path, its start, nothing pending, TEAM.md whole; nothing played")
    else:
        failures.append(f"  ✗ declaration                 rc={done.returncode} {house.journal_lines()} between={between} "
                        f"{rows!r} {done.stderr[-400:]!r}")

    done, rows = shown("teams", "down,e")
    code = T.REFUSED["verdict"]["refusal"].split(" -- ")[0]
    if (done.returncode == 0 and rows and "ops" in rows[0] and any(code in row.split() for row in rows[1:])
            and house.gestures() == []):
        held("a declaration start would refuse says its refusal", f"{code} in the overlay of ops")
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {code} {rows!r}")

    done, rows = shown("teams", "down,down,e")
    veille = DECLARATIONS["veille"]
    if (done.returncode == 0 and rows and _holds(rows[0], "veille", veille["path"])
            and not any(INSTANT.search(row) for row in rows) and "name: veille" in rows):
        held("a team never started says so", f"{veille['path']}, no start dated")
    else:
        failures.append(f"  ✗ never started               rc={done.returncode} {rows!r}")

    # --- b: the inbox, x seen, escape nothing, a question answered ------------------------------------------
    done, rows = shown("teams", "b")
    lines = ((QUESTION["id"], QUESTION["verb"], QUESTION["from"], QUESTION["task"], QUESTION["text"]),
             (DONE["task"], DONE["id"]),
             (RETURNED["id"], RETURNED["verb"], RETURNED["from"], RETURNED["task"], RETURNED["text"]))
    found = [any(_holds(row, *(f"#{one}" if isinstance(one, int) else one for one in words)) for row in rows[1:])
             for words in lines]
    preview = T.preview_in(done, "./pp team inbox")
    if (done.returncode == 0 and rows and "core-review" in rows[0] and all(found) and preview == f"./pp {SEEN}"
            and "inbox core-review" in house.journal_lines() and house.gestures() == []):
        held("b shows the owner's inbox", f"#{QUESTION['id']} on {QUESTION['task']}, {DONE['task']} done, "
             f"#{RETURNED['id']} returned; {preview!r} under them; nothing played")
    else:
        failures.append(f"  ✗ the box                     rc={done.returncode} {found} {preview!r} "
                        f"{house.journal_lines()} {rows!r} {done.stderr[-400:]!r}")

    done, _ = shown("teams", "b,x")
    played = house.gestures()
    none, _ = shown("teams", "b,escape")
    if done.returncode == 0 and played == [SEEN] and none.returncode == 0 and house.gestures() == []:
        held("x marks the inbox seen", f"{played[0]}; escape plays nothing")
    else:
        failures.append(f"  ✗ seen                        rc={done.returncode} {played} {house.gestures()} "
                        f"{done.stdout[-900:]!r}")

    staged, _ = shown("teams", "b,enter,o,k")
    preview = T.preview_in(staged, "./pp team post")
    done, _ = shown("teams", "b,enter,o,k,enter")
    played = house.gestures()
    if staged.returncode == 0 and done.returncode == 0 and preview == f"./pp {REPLY}" and played == [REPLY]:
        held("enter on a question replies to it", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ reply                       rc={staged.returncode},{done.returncode} {preview!r} {played} "
                        f"{staged.stdout[-1500:]!r} {staged.stderr[-400:]!r}")

    # --- the keys a start would change; an inbox where nothing waits ----------------------------------------
    house.use(T.script(declarations={**DECLARATIONS, "core-review": PENDING}))
    done, rows = shown("teams", "e")
    between = _between(rows, PENDING["started"], PENDING["text"]) or []
    keyed = [any(_holds(row, one["key"], _value(one["started"]), _value(one["declared"])) for row in between)
             for one in PENDING["pending"]]
    if done.returncode == 0 and len(between) == 1 + len(PENDING["pending"]) and all(keyed) and house.gestures() == []:
        held("the keys a start would change are said", ", ".join(one["key"] for one in PENDING["pending"])
             + f": {len(PENDING['pending'])} row(s) under the start")
    else:
        failures.append(f"  ✗ pending                     rc={done.returncode} {keyed} {between!r} {rows!r}")
    lines = house.journal_lines()
    if lines and all(not one.startswith("team ") for one in lines):
        held("e plays nothing", f"{len(lines)} reading(s) in the journal, no gesture")
    else:
        failures.append(f"  ✗ readings alone              {lines}")

    done, rows = shown("teams", "b")
    preview = T.preview_in(done, "./pp team inbox")
    if (done.returncode == 0 and rows and "core-review" in rows[0] and preview == f"./pp {SEEN}"
            and not any(re.search(r"#\d+", row) for row in rows[1:])):
        held("an empty inbox says so", f"its title and {preview!r}, no post in its body")
    else:
        failures.append(f"  ✗ empty                       rc={done.returncode} {preview!r} {rows!r}")
    return 0
