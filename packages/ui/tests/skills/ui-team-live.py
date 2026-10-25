"""Scenario `ui-team-live` -- the Teams and Tasks tabs follow their teams live, one watch per team, on ONE house of the
bench's `pp-team` witness whose script changes by `use()`:
- the Tasks tab, the Teams tab, the Tasks tab again and T3's thread opened: `watch core-review` and `watch ops` once
  each, never `watch veille` nor a watch of a task -- the two tabs and the thread share their team's watch
- the post's end ends each watch: `watch-end core-review`, `watch-end ops`, no witness left
- choosing another team ends the watch of the first and opens one on the second
- moving the cursor opens nothing: no history read without `enter`
- `escape` closes the thread: no overlay, T3 in its band again, no watch of a task
- `enter` on T3 opens its thread: its history -- the ask #45 that `waiting.questions` counts drawn apart from the post
  #44 --, then the live flow, #44 once, #48 after; the step of `reviewer` on its live line; the history read again
  brings #46, written meanwhile, in its place, and #49 -- the team's one watch, ended with the post
- a post on the watch makes `status <team> --json` read again -- the status line at 170 columns says the event the
  second face names --, a quiet reads nothing
- the column `live` of Members: a member running with no step seen says its age, a step of `reviewer` on the watch
  puts its last frame in its line, a member at rest takes neither
- the thread of T3 in the events of a debt: each line says the fields of its event -- the message a `re` answers, a
  `was`, the run and the relance of a wake-intent, the tick that answered in a member's place, the member a notice is
  about --; the tick's words drawn in one colour without bold, the notice the owner awaits drawn apart from the line
  of the same tick's suspicion
"""
from __future__ import annotations

import re
from datetime import datetime

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

LIVE = P.palette_constant("LIVE")
POST_48 = T.event("09:13:00", "post", 48, task="T3", **{"from": "lead"}, to="reviewer", verb="re", re=47, text="412 held")
ENDED_49 = T.event("09:14:00", "wake-ended", 49, tag="reviewer-T3-3", agent="reviewer", run="a01389", launch=3, cost=0.02)
WATCH = [{"sleep": 1.0}, T.T3_LOG[3], {"sleep": 0.4}, POST_48, T.STEP, {"sleep": 0.3}, ENDED_49]
READS = T.T3_READS + [sorted(T.T3_READS[1] + [POST_48, ENDED_49], key=lambda one: one["id"])]
POST = {"event": "post", "id": 48, "task": "T4", "from": "pm", "to": "lead", "verb": "do", "text": "a new task"}


def hour(event: dict) -> str:
    """-> the hour of an event of the faces, in local time: what heads its line beside its id."""
    return datetime.fromisoformat(event["at"]).astimezone().strftime("%H:%M:%S")


def head(event: dict) -> str:
    """-> the pattern of the head of an event's line in a thread: its id, then its hour."""
    return rf"#{event['id']}\s+{re.escape(hour(event))}"


def rows_of(lines: list[str], event: dict) -> list[int]:
    """-> the indexes of the lines an event heads."""
    return [index for index, line in enumerate(lines) if re.search(head(event), line)]




def member_row(text: str, member: str) -> str:
    return next((one for one in text.split("\n") if f" {member} " in one and f"agents/{member}" in one), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-live")
    tasks = ("--render", "tasks", "--size", "130x40")

    # --- both tabs shown and a thread opened: one watch per team started ------------------------------
    house.clear_journal()
    done = house.render(*tasks, "--press", "3,4,enter")
    watches = [one for one in house.journal_lines() if one.startswith("watch")]
    per_task = [one for one in watches if re.fullmatch(r"watch \S+ \S+", one)]
    shown = rows_of(P.overlay_rows(done.stdout), T.T3_LOG[0])
    if (done.returncode == 0 and watches.count("watch core-review") == 1 and watches.count("watch ops") == 1
            and not per_task and "watch veille" not in watches and shown):
        held("one watch per team started, none per task", f"{[one for one in watches if not one.startswith('watch-end')]}"
             f"; #{T.T3_LOG[0]['id']} of T3's thread in its overlay")
    else:
        failures.append(f"  ✗ watches                     rc={done.returncode} {watches} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- the post's end ends each ---------------------------------------------------------------------
    ended = [one for one in watches if one.startswith("watch-end")]
    if sorted(ended) == ["watch-end core-review", "watch-end ops"] and not house.alive():
        held("the post's end ends each watch", f"{sorted(ended)}; no witness left")
    else:
        failures.append(f"  ✗ ended                       {watches} alive={house.alive()}")

    # --- another team chosen: the first watch ended, one on the second -----------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "120x34", "--press", "down")
    journal = [one for one in house.journal_lines() if one.startswith("watch")]
    if (done.returncode == 0 and journal == ["watch core-review", "watch-end core-review", "watch ops",
                                              "watch-end ops"] and not house.alive()):
        held("one watch, on the team chosen", f"{journal}; no witness left")
    else:
        failures.append(f"  ✗ watch switched              rc={done.returncode} {journal} alive={house.alive()} "
                        f"{done.stderr[-400:]!r}")

    # --- moving the cursor opens nothing ---------------------------------------------------------------
    house.clear_journal()
    done = house.render(*tasks, "--press", "shift+tab,tab,down,up")
    logs = [one for one in house.journal_lines() if one.startswith("log ")]
    if done.returncode == 0 and logs == [] and not house.alive():
        held("moving the cursor opens nothing", "shift+tab, tab, down, up: no history read without enter")
    else:
        failures.append(f"  ✗ quick moves                 rc={done.returncode} {logs} alive={house.alive()}")

    # --- escape closes the thread ----------------------------------------------------------------------
    house.clear_journal()
    done = house.render(*tasks, "--press", "enter,escape")
    journal = house.journal_lines()
    watched = [one for one in journal if one.startswith("watch")]
    t3 = next(one for one in T.CORE["tasks"] if one["id"] == "T3")
    if (done.returncode == 0 and not P.overlay_rows(done.stdout) and not rows_of(done.stdout.split("\n"), T.T3_LOG[0])
            and "log core-review T3" in journal and t3["text"] in done.stdout
            and not any(one.endswith(" T3") for one in watched)):
        held("escape closes the thread", f"{watched}; no overlay, T3's text in its band again")
    else:
        failures.append(f"  ✗ thread closed               rc={done.returncode} {journal} {done.stdout[-900:]!r}")

    # --- the history, then the live flow, without a hole or a twin ----------------------------------
    script = T.script(watch={"core-review": WATCH})
    script["log"]["core-review/T3"] = READS
    house.use(script)
    house.clear_journal()
    done = house.render(*tasks, "--press", "enter,wait:team:wake-ended", "--styles")
    lines = P.ANSI.sub("", done.stdout).split("\n")
    by_id = {one["id"]: one for one in READS[-1]}
    at = {number: rows_of(lines, by_id[number]) for number in (41, 44, 45, 46, 48, 49)}
    ask, post = (P.styles_of(done.stdout, head(by_id[number])) for number in (45, 44))
    live = next((line for line in lines if LIVE in line), "")
    journal = house.journal_lines()
    if (done.returncode == 0 and all(at[one] for one in (41, 45, 48, 49)) and len(at[44]) == 1 and len(at[46]) == 1
            and at[45][0] < at[46][0] < at[48][0] < at[49][0] and P.bold_in(ask - post)
            and T.STEP["agent"] in live and T.STEP["stack"] in live and journal.count("log core-review T3") >= 2
            and "watch core-review T3" not in journal and journal.count("watch core-review") == 1
            and "watch-end core-review" in journal and not house.alive()):
        held("the thread of a task: its history, then its live flow", f"#44 once, #46 and #49 read again in their place, "
             f"#48 after #45, drawn apart ({sorted(ask - post)}); {live.strip()[:70]!r}; "
             f"{journal.count('log core-review T3')} history readings, the team's one watch, ended with the post")
    else:
        failures.append(f"  ✗ thread                      rc={done.returncode} {at} {sorted(ask)} {sorted(post)} {live!r} "
                        f"{journal} alive={house.alive()} {lines[-45:]!r} {done.stderr[-400:]!r}")

    # --- a post reads the team again, a quiet does not ------------------------------------------------
    script = T.script(watch={"core-review": [{"sleep": 0.5}, POST, {"sleep": 0.5}, {"event": "quiet", "seconds": 1}]})
    script["states"]["core-review"] = [T.CORE, T.CORE_NEXT]
    house.use(script)
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "170x34", "--press", "wait:team:post,wait:team:quiet")
    journal = house.journal_lines()
    reads = [one for one in journal if one == "status core-review"]
    status = P.status_of(done.stdout)
    first, then = (f"#{one['last']['id']}" for one in (T.CORE, T.CORE_NEXT))
    if (done.returncode == 0 and then in status and first not in status and len(reads) == 2
            and journal.count("watch core-review") == 1 and journal.count("status") == 1
            and journal[-1] == "watch-end core-review" and not house.alive()):
        held("a post reads the team again, a quiet does not", f"{then} on the status, not {first}; the journal "
             f"{journal}; no witness left")
    else:
        failures.append(f"  ✗ live                        rc={done.returncode} {status!r} {journal} "
                        f"alive={house.alive()} {done.stdout[-900:]!r} {done.stderr[-400:]!r}")

    # --- the column live: the age, then the last step; a member at rest ----------------------------------------
    house.use(T.script(watch={"core-review": [{"sleep": 0.6}, T.STEP]}))
    before = house.render("--render", "teams", "--size", "150x34")
    after = house.render("--render", "teams", "--size", "150x34", "--press", "wait:team:block")
    reviewer = next(one for one in T.CORE["members"] if one["member"] == T.STEP["agent"])
    age = T.age_said(reviewer["since"])
    frame = T.STEP["stack"].split("▸")[-1].strip()
    rows = {(name, when): member_row(done.stdout, name) for when, done in (("before", before), ("after", after))
            for name in ("reviewer", "lead")}
    if (before.returncode == 0 and after.returncode == 0 and age in rows["reviewer", "before"]
            and frame not in rows["reviewer", "before"] and frame in rows["reviewer", "after"]
            and rows["lead", "before"] and rows["lead", "after"] == rows["lead", "before"]
            and frame not in rows["lead", "after"] and age not in rows["lead", "after"]):
        held("the column live of Members", f"{rows['reviewer', 'before'].strip()[-30:]!r} -> "
             f"{rows['reviewer', 'after'].strip()[-30:]!r}; lead {rows['lead', 'after'].strip()[-10:]!r}")
    else:
        failures.append(f"  ✗ column live                 rc={before.returncode},{after.returncode} {age!r} {rows!r} "
                        f"{after.stdout[-1500:]!r}")

    # --- the thread in the events of a debt -------------------------------------------------------------------
    script = T.script()
    script["log"]["core-review/T3"] = T.DEBT_LOG
    script["states"]["core-review"] = [{**T.CORE, "waiting": T.DEBT_WAITING}]
    house.use(script)
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "enter", "--styles")
    plain = P.ANSI.sub("", done.stdout).split("\n")
    debt = {one["id"]: one for one in T.DEBT_LOG}
    lines = {number: next((plain[at] for at in rows_of(plain, debt[number])), "") for number in (46, 48, 49, 50, 51, 52)}
    expected = {number: [str(debt[number][key]) for key in ("from", "to", "re", "was", "run", "relance", "by", "about")
                         if debt[number].get(key) is not None] for number in lines}
    missing = {number: [one for one in said if one not in lines[number]] for number, said in expected.items()}
    missing = {number: said for number, said in missing.items() if said}
    tick = T.look_of(done.stdout, debt[50]["by"], within=f"#{50} ")
    preempted = T.look_of(done.stdout, "preempted", within=f"#{50} ")
    notice, suspicion = (P.styles_of(done.stdout, head(debt[number])) for number in (51, 52))
    if (done.returncode == 0 and not missing and tick is not None and not tick[0] and tick[1] is not None
            and preempted == tick and P.bold_in(notice - suspicion)):
        held("the thread speaks the debt", f"{ {number: said for number, said in expected.items()} }; the tick "
             f"{tick}, the notice #51 apart from #52 ({sorted(notice - suspicion)})")
    else:
        failures.append(f"  ✗ thread debt                 rc={done.returncode} missing={missing} {tick} {preempted} "
                        f"{sorted(notice)} {sorted(suspicion)} {plain[-45:]!r} {done.stderr[-300:]!r}")
    return 0
