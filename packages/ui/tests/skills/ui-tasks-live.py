"""Scenario `ui-tasks-live` -- the tasks a wake-up plays and the band of the task under the cursor, followed live, on
ONE house of the bench's `pp-team` witness (and `pp-chat` replaying the members' kept flows) whose script changes by
`use()`:
- the face saying `running` on core-review's T3 (`reviewer`) and on ops' T1 (`sre`): each of the two lines carries the
  spinner before its name, the tab's title the spinner and the count of such tasks, and the spinner's interval is
  alive (the render's word `spinning`)
- a member the face says running with no step seen: on ops' T1, `sre`'s `live:` line says its run and the age of its
  launch
- `core-review`'s watch saying two steps of `reviewer`'s wake-up on T3: the band of T3 says ONE `live:` line for
  `reviewer` -- its run, its last step, then the last call of a tool read from the flow of that exchange, `agent flow`
  asked for `agents/reviewer a01389 --exchange 3`
- a step of `lead` on T3 (its exchange 4), one of `reviewer` (its exchange 3), then the end of `lead`'s wake-up: two
  `live:` lines, each its run, its step and its call read from ITS exchange -- one `flow` reading per member
- the end of `lead`'s wake-up dims its line alone: `lead`'s drawn without bold, `reviewer`'s with
- the face read without `running`: no glyph on a line nor in the title, no interval alive
- a task no wake-up was seen on says its last event, as the face says it: ops' T1, its id, its kind and its age
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

LIVE, LAST, SPINNER = (P.palette_constant(name) for name in ("LIVE", "LAST", "SPINNER"))
SIZE = ("--size", "160x40")
OPENED = {**T.STEP, "event": "opened", "stack": None, "wait": None}
REVIEWER_CALL = next(one for one in T.KEPT["3"][0] if one["kind"] == "tool")
LEAD_CALL = next(one for one in T.LEAD_KEPT["4"] if one["kind"] == "tool")


def task_of(face: dict, task: str) -> dict:
    return next(one for one in face["tasks"] if one["id"] == task)


def line_of(text: str, mark: str) -> str:
    return next((one for one in text.split("\n") if mark in one), "")


def lives_of(text: str) -> list[str]:
    return [one.strip() for one in text.split("\n") if LIVE in one]




def flows_of(house, path: str, run: str, index: int) -> list[str]:
    return [one for one in house.chat_lines() if one.startswith("flow ") and f"{path} {run}" in one
            and f"--exchange {index}" in one]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script()
    script["states"].update({"core-review": [T.LIVE_CORE], "ops": [T.LIVE_OPS]})
    house = T.Teams(bench, "ui-tasks-live", script)
    t3, t1 = task_of(T.LIVE_CORE, "T3"), task_of(T.LIVE_OPS, "T1")
    names = (t3["name"], t1["text"][:20])
    turning = sum(1 for face in (T.LIVE_CORE, T.LIVE_OPS) for one in face["tasks"] if one.get("running"))
    glyph = f"[{re.escape(SPINNER)}]"

    # --- two tasks a wake-up plays; sre launched, no step seen -----------------------------------------
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning,down")
    rows = [line_of(done.stdout, name) for name in names]
    title = next((one for one in done.stdout.split("\n") if re.search(rf"{glyph} {turning}\b", one)
                  and not any(name in one for name in names)), "")
    last = P.status_of(done.stdout)
    if (done.returncode == 0 and all(re.search(glyph, one) for one in rows) and title
            and last == "spinning 1"):
        held("the tasks a wake-up plays turn", f"{rows[0].strip()[:40]!r}, {rows[1].strip()[:40]!r}; "
             f"{title.strip()[-24:]!r}; {last}")
    else:
        failures.append(f"  ✗ live tasks                  rc={done.returncode} {rows!r} {title!r} {last!r} "
                        f"{done.stdout[-2000:]!r} {done.stderr[-400:]!r}")
    wake = t1["running"][0]
    sre = line_of(done.stdout, f"{LIVE} {wake['member']}")
    if done.returncode == 0 and wake["run"] in sre and T.age_said(wake["since"]) in sre:
        held("a wake-up with no step seen says it was launched", sre.strip()[:60])
    else:
        failures.append(f"  ✗ launched                    rc={done.returncode} {sre!r} {done.stdout[-1500:]!r}")

    # --- the last step and the last call, on one line ------------------------------------------------
    house.use(T.script(watch={"core-review": [{"sleep": 0.3}, OPENED, T.STEP]}))
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--wait", "team:block:3")
    lives = lives_of(done.stdout)
    flows = flows_of(house, "agents/reviewer", T.STEP["run"], T.STEP["index"])
    said = lives[0] if len(lives) == 1 else ""
    if (done.returncode == 0 and said and T.STEP["agent"] in said and T.STEP["run"] in said
            and T.STEP["stack"] in said and REVIEWER_CALL["name"] in said and said.endswith(REVIEWER_CALL["title"])
            and said.index(T.STEP["stack"]) < said.index(REVIEWER_CALL["name"]) and flows):
        held("the band says the last action of the task", f"{said[:110]!r}; {flows}")
    else:
        failures.append(f"  ✗ last action                 rc={done.returncode} {lives} {house.chat_lines()} "
                        f"{done.stdout[-2000:]!r} {done.stderr[-400:]!r}")

    # --- two members, two lines, two readings; the end of lead's wake-up dims its line alone ---------------
    script = T.script(watch={"core-review": T.TWO_WATCH})
    script["states"]["ops"] = [T.LIVE_OPS]
    house.use(script)
    house.clear_journal()
    styled = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended:3", "--styles")
    plain = P.ANSI.sub("", styled.stdout)
    steps = {one["agent"]: one for one in (T.LEAD_STEP, T.STEP)}
    calls = {"lead": LEAD_CALL, "reviewer": REVIEWER_CALL}
    lines = {member: line_of(plain, f"{LIVE} {member}") for member in steps}
    readings = {member: flows_of(house, f"agents/{member}", step["run"], step["index"]) for member, step in steps.items()}
    if (styled.returncode == 0 and all(step["run"] in lines[member] and step["stack"] in lines[member]
                                       and calls[member]["name"] in lines[member] for member, step in steps.items())
            and all(len(one) == 1 for one in readings.values())):
        held("one live line per member, its call from its exchange", f"{lines['lead'].strip()[:60]!r}; "
             f"{lines['reviewer'].strip()[:60]!r}; {readings}")
    else:
        failures.append(f"  ✗ two members                 rc={styled.returncode} {lines!r} {house.chat_lines()} "
                        f"{plain[-2000:]!r} {styled.stderr[-400:]!r}")
    looks = {member: P.styles_of(styled.stdout, re.escape(f"{LIVE} {member}")) for member in steps}
    if styled.returncode == 0 and all(looks.values()) and not P.bold_in(looks["lead"]) and P.bold_in(looks["reviewer"]):
        held("the end of a wake-up dims its member's line alone", f"lead {sorted(looks['lead'])}, "
             f"reviewer {sorted(looks['reviewer'])}")
    else:
        failures.append(f"  ✗ dimmed                      rc={styled.returncode} {looks}")

    # --- none plays: no glyph, no interval; a task at rest says its last event ---------------------------------
    house.use(T.script())
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning,down")
    review = line_of(done.stdout, names[0])
    last = P.status_of(done.stdout)
    if done.returncode == 0 and review and not re.search(glyph, done.stdout) and last == "spinning 0":
        held("no wake-up, nothing turns", f"{review.strip()[:40]!r}; {last}")
    else:
        failures.append(f"  ✗ at rest                     rc={done.returncode} {review!r} {last!r} "
                        f"{done.stdout[-1500:]!r}")
    event = task_of(T.OPS, "T1")["last"]
    said = next((one.strip() for one in done.stdout.split("\n") if LAST in one), "")
    if (done.returncode == 0 and f"#{event['id']}" in said and event["kind"] in said
            and T.age_said(event["at"]) in said):
        held("a task at rest says its last event", said)
    else:
        failures.append(f"  ✗ at rest last                rc={done.returncode} {said!r} {done.stdout[-1500:]!r}")
    return 0
