"""Scenario `ui-tasks-live` -- the tasks a wake-up plays, on the bench's `pp-team` witness whose script changes by
`use()`:
- the face saying `running` on core-review's T3 (`reviewer`) and on ops' T1 (`sre`): each of the two lines carries the
  spinner before its name, the tab's title the spinner and the count of such tasks, and the spinner's interval is
  alive (the render's word `spinning`)
- the face read without `running`: no glyph on a line nor in the title, no interval alive
- an ask to the owner that waits for its answer (s.1702): core-review's #45 in the face's `waiting.questions`, the
  tab's title carries the badge `ASKED` and the count of the asks due, drawn in the theme's `$error`; the face read
  with #45 answered, no cell of the title in `$error`
- the messages of the inbox `b` opens (s.1705): core-review's face says two (#45, T2 done), the cursor on its T3 --
  the footer's `b` drawn on the theme's `$warning`, the count 2 in that span; `b`, `down`, `x` on T2 done, `escape`:
  the tasks read again say one, the span counts 1 without a change of tab; on the Teams tab, core-review chosen, the
  same span counts 2
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SPINNER = P.palette_constant("SPINNER")
ASKED = P.palette_constant("ASKED")
ERROR = "38;2;185;60;91"            # textual-dark's `$error` as Textual 8.2.8's colour system makes it, a foreground
WARNING_BG = "48;2;254;166;43"      # textual-dark's `$warning` the same way, a background
QUESTION = {"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "text": "tests green?"}
INBOX = {"core-review": {"team": "core-review", "questions": [QUESTION], "done": [{"task": "T2", "id": 40}]}}
ANSWERED = {**T.CORE, "waiting": {**T.CORE["waiting"], "questions": []}}      # #45 answered
READ = {**T.CORE, "waiting": {**T.CORE["waiting"], "done": []}}               # T2 done marked read


def task_of(face: dict, task: str) -> dict:
    return next(one for one in face["tasks"] if one["id"] == task)


def line_of(text: str, mark: str) -> str:
    return next((one for one in text.split("\n") if mark in one), "")


def spans_of(row: str) -> list[tuple[str, str]]:
    """-> the runs of a raw row of a `--styles` capture, each (its SGR parameters, its text)."""
    found, current = [], ""
    for part in re.split(r"(\x1b\[[0-9;]*m)", row):
        sgr = P.SGR.fullmatch(part)
        if sgr:
            current = sgr.group(1)
        elif part:
            found.append((current, part))
    return found


def drawn_in(text: str, code: str, within: str) -> str:
    """-> the text of the cells drawn with the SGR parameters `code`, on the rows whose bare text holds `within`."""
    return "".join(part for row in text.split("\n") if within in P.ANSI.sub("", row)
                   for params, part in spans_of(row) if code in params)


def b_count(text: str) -> int | None:
    """-> the count the footer's span on `$warning` carries, None when no span of the footer is drawn so."""
    footer = "\n".join(text.rstrip("\n").split("\n")[-6:])
    span = drawn_in(footer, WARNING_BG, "[b]")
    found = re.search(r"\d+", span) if "[b]" in span else None
    return int(found.group()) if found else None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script()
    script["states"].update({"core-review": [T.LIVE_CORE], "ops": [T.LIVE_OPS]})
    house = T.Teams(bench, "ui-tasks-live", script)
    t3, t1 = task_of(T.LIVE_CORE, "T3"), task_of(T.LIVE_OPS, "T1")
    names = (t3["name"], t1["text"][:20])
    turning = sum(1 for face in (T.LIVE_CORE, T.LIVE_OPS) for one in face["tasks"] if one.get("running"))
    glyph = f"[{re.escape(SPINNER)}]"

    # --- two tasks a wake-up plays ---------------------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning,down", "--styles")
    plain = P.ANSI.sub("", done.stdout)
    rows = [line_of(plain, name) for name in names]
    title = next((one for one in plain.split("\n") if re.search(rf"{glyph} {turning}\b", one)
                  and not any(name in one for name in names)), "")
    last = P.status_of(plain)
    badge = drawn_in(done.stdout, ERROR, "4·Tasks")
    if (done.returncode == 0 and all(re.search(glyph, one) for one in rows) and title
            and last == "spinning 1"):
        held("the tasks a wake-up plays turn", f"{rows[0].strip()[:40]!r}, {rows[1].strip()[:40]!r}; "
             f"{title.strip()[-24:]!r}; {last}")
    else:
        failures.append(f"  ✗ live tasks                  rc={done.returncode} {rows!r} {title!r} {last!r} "
                        f"{plain[-2000:]!r} {done.stderr[-400:]!r}")

    # --- an ask due: the badge of the title in `$error` -- s.1702 ---------------------------------------
    due = len([one for face in (T.LIVE_CORE, T.LIVE_OPS) for one in face["waiting"]["questions"]])
    if done.returncode == 0 and ASKED in badge and re.search(rf"\b{due}\b", badge):
        held("an ask due badges the title in $error", f"{badge.strip()!r} drawn {ERROR} on the row of 4·Tasks")
    else:
        failures.append(f"  ✗ the badge of an ask due      rc={done.returncode} badge={badge!r} "
                        f"{[row for row in done.stdout.split(chr(10)) if '4·Tasks' in P.ANSI.sub('', row)]!r}")

    # --- none plays: no glyph, no interval ------------------------------------------------------------
    script = T.script()
    script["states"].update({"core-review": [ANSWERED]})
    house.use(script)
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning,down", "--styles")
    plain = P.ANSI.sub("", done.stdout)
    review = line_of(plain, names[0])
    last = P.status_of(plain)
    badge = drawn_in(done.stdout, ERROR, "4·Tasks")
    if done.returncode == 0 and review and not re.search(glyph, plain) and last == "spinning 0":
        held("no wake-up, nothing turns", f"{review.strip()[:40]!r}; {last}")
    else:
        failures.append(f"  ✗ at rest                     rc={done.returncode} {review!r} {last!r} "
                        f"{plain[-1500:]!r}")
    if done.returncode == 0 and not badge and ASKED not in line_of(plain, "4·Tasks"):
        held("the ask answered, no badge", "no cell of the row of 4·Tasks drawn in $error")
    else:
        failures.append(f"  ✗ the badge after the answer   rc={done.returncode} badge={badge!r} "
                        f"{line_of(plain, '4·Tasks')!r}")

    # --- the messages of the inbox `b` opens counted on `$warning` -- s.1705 -------------------------------
    house.use(T.script(inbox=INBOX))
    house.clear_journal()
    before = house.render("--render", "tasks", "--size", "150x40", "--styles")
    script = T.script(inbox=INBOX)
    script["states"].update({"core-review": [T.CORE, READ]})
    house.use(script)
    house.clear_journal()
    after = house.render("--render", "tasks", "--size", "150x40", "--press", "b,down,x,escape", "--styles")
    house.use(T.script(inbox=INBOX))
    teams = house.render("--render", "teams", "--size", "150x40", "--styles")
    counted = [b_count(one.stdout) for one in (before, after, teams)]
    if all(one.returncode == 0 for one in (before, after, teams)) and counted == [2, 1, 2]:
        held("b counts the inbox on $warning", f"Tasks on T3: 2; x on T2 done: 1, the tab unchanged; Teams on "
             f"core-review: 2 -- each read in the span drawn {WARNING_BG}")
    else:
        failures.append(f"  ✗ the count of b              rc={[one.returncode for one in (before, after, teams)]} "
                        f"counted={counted} {P.ANSI.sub('', after.stdout)[-1200:]!r} {after.stderr[-400:]!r}")
    return 0
