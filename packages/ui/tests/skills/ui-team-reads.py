"""Scenario `ui-team-reads` -- what the tabs of the teams read and show in an overlay, playing nothing, on the bench's
`pp-team` witness:
- `l` on the Teams tab reads `team log <team> --json` and shows every event of the journal, by its id, in an overlay
  titled by the team
- the band of a resolved task on the Tasks tab reads `team result <team> <task>` and shows each key of its
  JSON with its value; on an open task the verb's refusal, `task-open`, goes to the remedy line, no overlay opened
- outside the Teams and Tasks tabs `l` and `v` call nothing of `team`
- `e` reads `team declaration <team> --json` and shows, in an overlay titled by the team and its path, the declaration
  rendered as markdown (batch les-reglages-des-formulaires): a title, the team and its path; a table -- the verdict,
  the instant of the start, nothing pending --, then `TEAM.md`, its keys in a block of code (the blocks of the markdown, `blocks`:
  a title, a table, a block of code); no mark of markdown left raw; nothing played
- a declaration `start` would refuse shows the refusal's code, `team-invalid`, in the row of its verdict
- a team never started dates no start: `not started`, TEAM.md's keys whole
- the keys a start would change are counted in the row `pending`, then stand one row each, the key, its started value
  and its declared value
- `e` plays nothing: the journal holds readings alone
- the inbox: `ui-team-reads-inbox` (cut by case, rule 10)
"""
from __future__ import annotations

import json
import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SIZE = ("--size", "130x40")
TALL = ("--size", "130x60")            # the declaration's overlay tall enough for TEAM.md whole
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


def _cells(rows: list[str], key: str) -> list[str]:
    """-> the words of the cell beside `key` in the table of the declaration -- its row parted by `│` --; [] without
    it."""
    cells = [row.split("│") for row in rows if "│" in row]
    return next((one[1].split() for one in cells if one[0].strip() == key and len(one) > 1), [])


def _within(rows: list[str], lines: list[str]) -> bool:
    """-> whether `lines` stand in `rows` one after the other, in their order -- a block of code read whole."""
    at = next((n for n, row in enumerate(rows) if lines and row == lines[0]), None)
    return at is not None and rows[at:at + len(lines)] == lines


def _blocks(text: str) -> list[str]:
    """-> the kinds of the blocks of the markdown on top, as the closing line `blocks` says them."""
    line = next((one for one in text.splitlines() if one.startswith("blocks ")), "")
    return line[len("blocks "):].split(",") if line else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-reads", T.script(declarations=DECLARATIONS, inbox=INBOX))

    def shown(pane: str, keys: str, size: tuple = SIZE):
        house.clear_journal()
        done = house.render("--render", pane, *size, "--press", keys)
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
    edge = T.edge_of(done.stdout) or 0
    rows = [one[edge:].strip() for one in done.stdout.split("\n")]
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

    # --- e: the declaration rendered as markdown, never started, refused ----------------------------------------
    done, rows = shown("teams", "e,blocks", TALL)
    blocks = _blocks(done.stdout)
    front = [one.strip() for one in CORE["text"].split("\n")[1:CORE["text"].split("\n").index("---", 1)]]
    said = {key: _cells(rows, key) for key in ("verdict", "started", "pending")}
    if (done.returncode == 0 and len(rows) > 1 and _holds(rows[0], "core-review", CORE["path"])
            and _holds(rows[1], "core-review", CORE["path"]) and said["verdict"] == ["ok"]
            and said["started"][:1] == [CORE["started"]["at"]] and said["pending"] == ["nothing", "pending"]
            and _within(rows, front) and {"MarkdownH1", "MarkdownTable", "MarkdownFence"} <= set(blocks)
            and "---" not in rows and not any(row.startswith(("#", "|", "```")) for row in rows[1:])
            and "declaration core-review" in house.journal_lines() and house.gestures() == []):
        held("e shows the declaration rendered", f"{said}; TEAM.md's keys in a block of code; blocks {sorted(set(blocks))}; "
             "nothing played")
    else:
        failures.append(f"  ✗ declaration                 rc={done.returncode} {house.journal_lines()} {said} {blocks} "
                        f"{rows!r} {done.stderr[-400:]!r}")

    done, rows = shown("teams", "down,e", TALL)
    code = T.REFUSED["verdict"]["refusal"].split(" -- ")[0]
    if (done.returncode == 0 and rows and "ops" in rows[0] and code in _cells(rows, "verdict")
            and house.gestures() == []):
        held("a declaration start would refuse says its refusal", f"{code} in the overlay of ops")
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {code} {rows!r}")

    done, rows = shown("teams", "down,down,e", TALL)
    veille = DECLARATIONS["veille"]
    lines = veille["text"].split("\n")
    if (done.returncode == 0 and rows and _holds(rows[0], "veille", veille["path"])
            and not any(INSTANT.search(row) for row in rows) and _cells(rows, "started") == ["not", "started"]
            and _within(rows, [one.strip() for one in lines[1:lines.index("---", 1)]])):   # TEAM.md whole
        held("a team never started says so", f"{veille['path']}, no start dated")
    else:
        failures.append(f"  ✗ never started               rc={done.returncode} {rows!r}")

    # --- the keys a start would change ----------------------------------------
    house.use(T.script(declarations={**DECLARATIONS, "core-review": PENDING}))
    done, rows = shown("teams", "e", TALL)
    keyed = [any(_holds(row, one["key"], _value(one["started"]), _value(one["declared"])) for row in rows)
             for one in PENDING["pending"]]
    counted = _cells(rows, "pending")
    if (done.returncode == 0 and all(keyed) and counted[:1] == [str(len(PENDING["pending"]))]
            and house.gestures() == []):
        held("the keys a start would change are said", ", ".join(one["key"] for one in PENDING["pending"])
             + f": {' '.join(counted)}, one row each")
    else:
        failures.append(f"  ✗ pending                     rc={done.returncode} {keyed} {counted} {rows!r}")
    lines = house.journal_lines()
    if lines and all(not one.startswith("team ") for one in lines):
        held("e plays nothing", f"{len(lines)} reading(s) in the journal, no gesture")
    else:
        failures.append(f"  ✗ readings alone              {lines}")

    return 0
