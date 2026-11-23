"""Scenario `ui-tasks-band-asks` -- the asks to the principal in the sequence of the Tasks tab (s.1584, cut out of
`ui-tasks-band-sequence` at 22 s), on the bench's `pp-team` witness:
- an ask to the principal kept in sight (s.1584): T3's thread long enough that its body ends far below reviewer's ask
  #45, which the face's `waiting.questions` holds -- the row of #45 left the body's sight, its line pinned above the
  body under the mark `ASKED`, the band's summary counting 1 question; the ask answered (#46, the face's `waiting`
  empty), no line pinned, no question counted
- the ask's task closed with no answer (s.1584, review #9628): T3 stopped, the face's `waiting` empty -- no line
  pinned, no question counted
- beyond three asks that wait (review #9628): #45 and three more asks of T3 in the face's `waiting` -- the pinned line
  shows what it can and says how many asks it does not show, the shown and the unshown making the four
"""
from __future__ import annotations

import re

from tests.harness import support

S = support(__file__, "tasks_sequence")
T, P = S.T, S.P

AFTER = [T.event(T.clock(10 + n), "post", 50 + n, task="T3", **{"from": ("lead", "reviewer")[n % 2]},
                 to=("reviewer", "lead")[n % 2], verb="do", text=f"part {n + 1} of the review")
         for n in range(24)]
LONG_T3 = T.T3_LOG + AFTER                                   # #45 asked, then 24 posts after it
ANSWERED_T3 = sorted(T.T3_LOG + [T.WRITTEN], key=lambda one: one["id"]) + AFTER
COUNTED = re.compile(r"\bquestions\s+1\b")                   # the field of the band's summary
COUNTED_ANY = re.compile(r"\bquestions\s+\d+\b")
STOPPED_AT = T.ago(3600)                                     # an hour ago: T3 stays in `recent` whatever the day
CLOSED_T3 = LONG_T3 + [T.event(T.clock(40), "stopped", 74, task="T3", **{"from": "house"})]
ASKS = [T.event(T.clock(10 + n), "post", 50 + n, task="T3", **{"from": ("lead", "reviewer")[n % 2]}, to="house",
                verb="ask", text=f"question {n + 1} of the review") for n in range(3)]
FOUR_T3 = T.T3_LOG + ASKS + AFTER[3:]                        # #45, #50, #51, #52 asked, then posts after them


def asked() -> str | None:
    try:
        return P.palette_constant("ASKED")
    except KeyError:
        return None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- an ask to the principal kept in sight -- s.1584 -------------------------------------------------------
    house = S.house(bench, "ui-tasks-band-asks")
    script = T.script(log={**T.script()["log"], "core-review/T3": LONG_T3})
    script["states"].update({"core-review": [T.LIVE_CORE], "ops": [T.LIVE_OPS]})
    house.use(script)
    waiting = house.render("--render", "tasks", *S.SIZE)
    answered_face = {**T.LIVE_CORE, "waiting": {**T.LIVE_CORE["waiting"], "questions": []}}
    script = T.script(log={**T.script()["log"], "core-review/T3": ANSWERED_T3})
    script["states"].update({"core-review": [answered_face], "ops": [T.LIVE_OPS]})
    house.use(script)
    answered = house.render("--render", "tasks", *S.SIZE)
    mark = asked()
    drawn = S.heads_of(waiting.stdout)
    pinned = [one for one in waiting.stdout.split("\n") if mark and f"{mark} #45" in one]
    if (waiting.returncode == 0 and answered.returncode == 0 and drawn and 45 not in drawn and max(drawn) == 73
            and len(pinned) == 1 and COUNTED.search(waiting.stdout)
            and not any(mark and mark in one for one in answered.stdout.split("\n"))
            and not COUNTED.search(answered.stdout)):
        held("an ask to the principal kept in sight", f"#45 out of the body's rows ({min(drawn)}..{max(drawn)}), its "
             f"line pinned under {mark!r}, the summary counts 1 question; answered by #46: nothing pinned, none counted")
    else:
        failures.append(f"  ✗ an ask kept in sight        rc={waiting.returncode}/{answered.returncode} mark={mark!r} "
                        f"drawn={drawn} pinned={pinned} counted={bool(COUNTED.search(waiting.stdout))}/"
                        f"{bool(COUNTED.search(answered.stdout))} {waiting.stdout[-2500:]!r}")

    # --- the ask's task closed with no answer: nothing pinned, nothing counted ---------------------------------
    stopped = {**next(one for one in T.CORE["tasks"] if one["id"] == "T3"), "state": "stopped", "ended": STOPPED_AT,
               "last": {"id": 74, "kind": "stopped", "at": STOPPED_AT}, "running": []}
    closed_face = {**T.CORE, "tasks": [stopped if one["id"] == "T3" else one for one in T.CORE["tasks"]],
                   "waiting": {**T.CORE["waiting"], "questions": []}}
    script = T.script(log={**T.script()["log"], "core-review/T3": CLOSED_T3})
    script["states"].update({"core-review": [closed_face], "ops": [T.LIVE_OPS]})
    house.use(script)
    closed = house.render("--render", "tasks", *S.SIZE)
    drawn = S.heads_of(closed.stdout)
    if (closed.returncode == 0 and drawn and max(drawn) >= 73 and "T3" in closed.stdout
            and not any(mark and f"{mark} #" in one for one in closed.stdout.split("\n"))
            and not COUNTED_ANY.search(closed.stdout)):
        held("the ask's task closed with no answer", f"T3 stopped, its rows drawn ({min(drawn)}..{max(drawn)}): "
             "nothing pinned, no question counted")
    else:
        failures.append(f"  ✗ the ask's task closed       rc={closed.returncode} drawn={drawn} "
                        f"pinned={[one for one in closed.stdout.split(chr(10)) if mark and mark in one]} "
                        f"counted={bool(COUNTED_ANY.search(closed.stdout))} {closed.stdout[-2500:]!r}")

    # --- beyond three asks that wait: the pinned line says how many it does not show -----------------------------
    four = [45] + [one["id"] for one in ASKS]
    four_face = {**T.LIVE_CORE, "waiting": {**T.LIVE_CORE["waiting"], "questions": [
        {"id": one, "verb": "ask", "from": "reviewer", "task": "T3"} for one in four]}}
    script = T.script(log={**T.script()["log"], "core-review/T3": FOUR_T3})
    script["states"].update({"core-review": [four_face], "ops": [T.LIVE_OPS]})
    house.use(script)
    many = house.render("--render", "tasks", *S.SIZE)
    lines = many.stdout.split("\n")
    shown = [int(found.group(1)) for found in (re.search(rf"{re.escape(mark or '?')} #(\d+) ask", one) for one in lines)
             if found]
    more = [int(found.group(1)) for found in (re.search(rf"{re.escape(mark or '?')} (\d+) more", one) for one in lines)
            if found]
    if (many.returncode == 0 and len(more) == 1 and more[0] >= 1 and len(shown) + 1 <= 3
            and len(shown) + more[0] == len(four) and set(shown) <= set(four) and re.search(r"\bquestions\s+4\b", many.stdout)):
        held("beyond three asks, the pinned line says the rest", f"{shown} pinned, then {more[0]} more said; the "
             "summary counts 4 questions")
    else:
        failures.append(f"  ✗ beyond three asks            rc={many.returncode} shown={shown} more={more} "
                        f"{[one for one in lines if mark and mark in one]}")
    return 0
