"""Scenario `team-journal` -- 9 case(s) (batch l-equipe-et-son-journal, 2026-10-01, and its
rework; split out of `team-review` by les-scenarios-par-maison, 2026-10-07): a review team on
a throwaway house -- declared, started, posted to, stopped and read; no wake-up, no tick.
- a declared team starts: `team start review --message …` answers 0, the four agents are born
  at their paths under the house (every line `<name> <path>`, the name its path here), the journal
  opens on `team-started`, `task T1` and the `do` post owner -> m
- a wrong declaration refuses before anything is written: an edge to an agent nobody declared
  (`participant-unknown`), an `after` that loops (`ceremony-cycle`), no `root` (`root-missing`),
  an agents line without its path (`team-invalid`), no `TEAM.md` (`team-unknown`), a season of the
  standing team naming a member nobody declared (`--member nobody`: `participant-unknown`, team
  0.31.0 -- a season on a standing team is no longer refused) -- no agent created, no journal written
- a post enters at any time: a note on T1, a new task T2 to r1, a post `--as pm` from the mandator,
  `--as nobody` refused `principal-unknown`
- a post on a closed task is refused: `stop --task T2` writes `stopped`, then the stop, and returns the
  `do` left undelivered to its author, `post --task T2` refuses `task-closed`
- the state is read from the journal: `status review` twice gives the same bytes and moves nothing
- two posts at once do not mix: two lines, two ids, the journal reads again
- `status` without a name lists the teams declared under `teams/`, started or not
- a last line still being written is skipped by `status`; a torn line elsewhere refuses by its name
- (m3) a line written before (team 0.13.0): `m manager` is the member m played by the agent born at
  `manager`; its face (`status --json`) says the path `manager` and one `do` in its inbox
"""
from __future__ import annotations

import re

from tests.harness import race, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    journal = h.journal_of("review")

    # --- a declared team starts ---------------------------------------------------------------
    h.declare("review", T.REVIEW)
    started = h.call("team", "start", "review", "--message", "review PR 42", "--no-tick")
    found = h.events()
    kinds = [one.get("kind") for one in found]
    opening = found[0] if found else {}
    task = found[1] if len(found) > 1 else {}
    post = found[2] if len(found) > 2 else {}
    if (started.returncode == 0 and all(h.agent_stands(one) for one in ("m", "r1", "r2", "r3"))
            and kinds == ["team-started", "task", "post"]
            and [one.get("id") for one in found] == [1, 2, 3]
            and all(one.get("team") == "review" and one.get("at") for one in found)
            and opening.get("agents") == {"m": "m", "r1": "r1", "r2": "r2", "r3": "r3"}
            and opening.get("reports") == [{"from": ["r1", "r2", "r3"], "to": "m"}]
            and opening.get("root") == "m" and opening.get("principals") == ["pm"]
            and opening.get("owner") == "house"
            and [one.get("name") for one in opening.get("ceremonies", [])] == ["daily", "retro"]
            and opening.get("ceremonies", [{}])[1].get("after") == "daily"
            and task.get("task") == "T1" and task.get("from") == "house" and task.get("to") == "m"
            and post.get("task") == "T1" and post.get("verb") == "do" and post.get("from") == "house"
            and post.get("to") == "m" and post.get("text") == "review PR 42"
            and "T1" in started.stdout):
        held("a declared team starts", "team start review: rc 0, m r1 r2 r3 born at their paths, "
             "the journal opens on team-started, task T1, post do house -> m")
    else:
        failures.append(f"  ✗ team start                  rc={started.returncode} kinds={kinds} "
                        f"{started.stdout[-200:]!r} {started.stderr[-300:]!r}")

    # --- a wrong declaration refuses before anything is written -------------------------------
    h.declare("bad-edge", T.REVIEW.replace("r1 r2 r3 -> m", "r1 r9 -> m").replace("  m m\n", "  x1 x1\n")
              .replace("root: m", "root: x1").replace("-> m\n", "-> x1\n"))
    h.declare("bad-cycle", T.REVIEW.replace("daily every weekday 09:30 with r1 r2 r3 -> m", "daily after retro with r1 -> m")
              .replace("  m m\n", "  x2 x2\n").replace("root: m", "root: x2").replace("-> m\n", "-> x2\n"))
    h.declare("bad-root", T.REVIEW.replace("root: m\n", "").replace("  m m\n", "  x3 x3\n").replace("-> m\n", "-> x3\n"))
    h.declare("bad-type", T.REVIEW.replace("  r3 r3\n", "  x4\n").replace("r1 r2 r3 -> m", "r1 r2 -> m")
              .replace("with r1 r2 r3 -> m", "with r1 r2 -> m"))
    refused = {name: h.call("team", "start", name, "--message", "x", "--no-tick")
               for name in ("bad-edge", "bad-cycle", "bad-root", "bad-type", "nobody")}
    again = h.call("team", "start", "review", "--no-tick", "--member", "nobody", "--model", "m2")
    owed = {"bad-edge": "participant-unknown", "bad-cycle": "ceremony-cycle", "bad-root": "root-missing",
            "bad-type": "team-invalid", "nobody": "team-unknown"}
    journals = h.records / "teams"
    if (all(refused[name].returncode == 2 and code in refused[name].stderr and refused[name].stdout == ""
            for name, code in owed.items())
            and again.returncode == 2 and "participant-unknown" in again.stderr
            and not any(h.agent_stands(one) for one in ("x1", "x2", "x3", "x4", "r9"))
            and sorted(one.name for one in journals.iterdir()) == ["review"]
            and len(h.events()) == 3):
        held("a wrong declaration refuses before anything is written",
             "participant-unknown, ceremony-cycle, root-missing, team-invalid, team-unknown, a season's `--member nobody` "
             "-- no agent born, no journal written, the standing journal at 3 events")
    else:
        failures.append("  ✗ declaration refusals        "
                        + " ".join(f"{name}={one.returncode}:{one.stderr[-80:]!r}" for name, one in refused.items())
                        + f" again={again.returncode}:{again.stderr[-80:]!r} journals={sorted(one.name for one in journals.iterdir())}")

    # --- a post enters at any time ------------------------------------------------------------
    noted = h.call("team", "post", "review", "--task", "T1", "--message", "change of course", "--no-tick")
    opened = h.call("team", "post", "review", "--to", "r1", "--message", "look at the tests", "--no-tick")
    mandated = h.call("team", "post", "review", "--task", "T1", "--as", "pm", "--message", "from the product owner", "--no-tick")
    nobody = h.call("team", "post", "review", "--task", "T1", "--as", "nobody", "--message", "who", "--no-tick")
    found = h.events()
    by_kind = [(one.get("kind"), one.get("task"), one.get("verb"), one.get("from"), one.get("to")) for one in found[3:]]
    if (noted.returncode == 0 and opened.returncode == 0 and mandated.returncode == 0
            and nobody.returncode == 2 and "principal-unknown" in nobody.stderr
            and by_kind == [("post", "T1", "note", "house", "m"),
                            ("task", "T2", None, "house", "r1"),
                            ("post", "T2", "do", "house", "r1"),
                            ("post", "T1", "note", "pm", "m")]
            and [one.get("id") for one in found] == list(range(1, 8))
            and "T2" in opened.stdout and "#4" in noted.stdout):
        held("a post enters at any time", "a note on T1, a new task T2 to r1 with its do, a note --as pm "
             "from pm; --as nobody refuses principal-unknown")
    else:
        failures.append(f"  ✗ posts                       {noted.returncode}/{opened.returncode}/{mandated.returncode}/"
                        f"{nobody.returncode} {by_kind} {noted.stderr[-120:]!r} {opened.stderr[-120:]!r} "
                        f"{nobody.stderr[-120:]!r}")

    # --- a post on a closed task is refused ---------------------------------------------------
    stopped = h.call("team", "stop", "review", "--task", "T2", "--no-tick")
    late = h.call("team", "post", "review", "--task", "T2", "--message", "too late", "--no-tick")
    unknown = h.call("team", "post", "review", "--task", "T9", "--message", "nowhere", "--no-tick")
    found = h.events()
    halt, last, back = (found[-3], found[-2], found[-1]) if len(found) > 2 else ({}, {}, {})
    if (stopped.returncode == 0 and halt.get("kind") == "stopped" and halt.get("task") == "T2"
            and halt.get("by") == "house" and halt.get("id") == 8
            and last.get("kind") == "post" and last.get("verb") == "stop"
            and last.get("task") == "T2" and last.get("to") == "r1" and last.get("id") == 9
            and back.get("kind") == "returned" and back.get("message") == 6 and back.get("to") == "house"
            and late.returncode == 2 and "task-closed" in late.stderr
            and unknown.returncode == 2 and "task-unknown" in unknown.stderr and len(h.events()) == 10):
        held("a post on a closed task is refused", "stop --task T2 writes stopped #8, then post stop #9 and returns "
             "the do #6 to house; post --task T2 refuses task-closed, --task T9 task-unknown; the journal at 10 events")
    else:
        failures.append(f"  ✗ task-closed                 {stopped.returncode}/{late.returncode}/{unknown.returncode} "
                        f"{halt} {last} {back} {stopped.stderr[-120:]!r} {late.stderr[-120:]!r} {unknown.stderr[-120:]!r}")

    # --- the state is read from the journal ---------------------------------------------------
    before = journal.read_bytes()
    first = h.call("team", "status", "review")
    second = h.call("team", "status", "review")
    face = h.face("review")
    tasks = {one.get("id"): (one.get("state"), one.get("to"), one.get("messages")) for one in face.get("tasks") or []}
    boxes = {one.get("member"): (one.get("path"), [(box.get("verb"), box.get("from")) for box in one.get("pending") or []])
             for one in face.get("members") or []}
    owner_box = [(one.get("id"), one.get("verb"), one.get("from"), one.get("task"), one.get("returned"))
                 for one in face.get("owner_inbox") or []]
    if (first.returncode == 0 and first.stdout == second.stdout and first.stderr == second.stderr
            and journal.read_bytes() == before and face == h.face("review")
            and face.get("owner") == "house" and face.get("principals") == ["pm"]
            and tasks == {"T1": ("open", "m", 3), "T2": ("stopped", "r1", 2)}
            and boxes.get("m") == ("m", [("do", "house"), ("note", "house"), ("note", "pm")])
            and all(boxes.get(one) == (one, []) for one in ("r1", "r2", "r3"))
            and owner_box == [(6, "do", "house", "T2", True)]
            and (face.get("last") or {}).get("id") == 10 and (face.get("last") or {}).get("kind") == "returned"):
        held("the state is read from the journal", "status review twice: the same bytes, the journal untouched "
             "-- owner, pm, T1 open (m: do, note, note), T2 stopped (r1: its stop delivered at once; the do returned), the last event")
    else:
        failures.append(f"  ✗ status                      rc={first.returncode} same={first.stdout == second.stdout} "
                        f"{first.stdout[-400:]!r} {first.stderr[-200:]!r}")

    # --- two posts at once do not mix ---------------------------------------------------------
    count = len(h.events())
    raced = race(h.engine, [["--instance", str(h.house), "team", "post", "review", "--task", "T1", "--message", "one", "--no-tick"],
                            ["--instance", str(h.house), "team", "post", "review", "--task", "T1", "--message", "two", "--no-tick"]],
                 cwd=h.ws, env=h.env)
    found = h.events()
    ids = [one.get("id") for one in found]
    texts = sorted(str(one.get("text")) for one in found[count:])
    after = h.call("team", "status", "review")
    if (all(one.returncode == 0 for one in raced) and len(found) == count + 2
            and ids == list(range(1, count + 3)) and texts == ["one", "two"]
            and after.returncode == 0
            and [one.get("messages") for one in h.face("review").get("tasks") or [] if one.get("id") == "T1"] == [5]):
        held("two posts at once do not mix", f"race of two posts: two lines, ids {ids[-2:]}, the journal reads again")
    else:
        failures.append(f"  ✗ race                        {[one.returncode for one in raced]} ids={ids} texts={texts} "
                        f"{[one.stderr[-120:] for one in raced]!r} {h.face('review').get('tasks')}")

    # --- status without a name lists the teams declared ---------------------------------------
    h.declare("essai", T.REVIEW.replace("name: review", "name: essai"))
    listed = h.call("team", "status")
    lines = h.face()
    names = [one.get("team") for one in lines]
    by_team = {one.get("team"): one for one in lines}
    if (listed.returncode == 0 and len(listed.stdout.strip().splitlines()) == len(lines)
            and names == ["bad-cycle", "bad-edge", "bad-root", "bad-type", "essai", "review"]
            and (by_team["review"].get("tasks") or {}).get("open") == 1
            and sum((by_team["review"].get("tasks") or {}).values()) == 2
            and by_team["essai"].get("started") is None and by_team["essai"].get("state") == "never"):
        held("status without a name lists the teams", "one line per TEAM.md under teams/: review started with "
             "its tasks, essai declared and not started")
    else:
        failures.append(f"  ✗ status listing              rc={listed.returncode} {names} {lines} "
                        f"{listed.stderr[-200:]!r}")

    # --- a last line still being written is skipped; a torn line elsewhere refuses -------------
    whole = journal.read_text(encoding="utf-8")
    with journal.open("a", encoding="utf-8") as handle:
        handle.write('{"at": "2026-10-01T18:00')
    torn_tail = h.call("team", "status", "review")
    good, torn_line = journal.read_text(encoding="utf-8").rsplit("\n", 1)
    journal.write_text(torn_line + "\n" + good + "\n", encoding="utf-8")     # the torn line moved to the head
    torn_head = h.call("team", "status", "review")
    journal.write_text(whole, encoding="utf-8")                              # the journal whole again
    if (torn_tail.returncode == 0 and torn_tail.stdout == after.stdout and "Traceback" not in torn_tail.stderr
            and torn_head.returncode == 2 and journal.name in torn_head.stderr
            and re.search(r"\b1\b", torn_head.stderr) and "Traceback" not in torn_head.stderr):
        held("a torn last line is skipped, elsewhere it refuses", "status reads the whole lines; "
             "a torn line at the head: rc 2, the refusal naming journal.jsonl and its line 1")
    else:
        failures.append(f"  ✗ torn lines                  {torn_tail.returncode}/{torn_head.returncode} "
                        f"{torn_tail.stderr[-200:]!r} {torn_head.stderr[-200:]!r}")

    # --- (m3) a line written before reads as a name and a path [48] -----------------------------------------
    h.declare("older", "---\nname: review\nagents: |\n  m manager\nroot: m\nschedule: off\n---\nA line of before.\n")
    older = h.call("team", "start", "older", "--message", "read me", "--no-tick")
    status_o = h.call("team", "status", "older")
    member_o = next((one for one in h.face("older").get("members") or [] if one.get("member") == "m"), {})
    opening_o = next(iter(T.lines(h.journal_of("older"))), {})
    if (older.returncode == 0 and status_o.returncode == 0 and h.agent_stands("manager")
            and opening_o.get("agents") == {"m": "manager"} and member_o.get("path") == "manager"
            and [(one.get("verb"), one.get("from")) for one in member_o.get("pending") or []] == [("do", "house")]):
        held("(m3) a line of before is a name and a path", "`m manager`: the member m, played by the agent born "
             "at manager; its face says the path manager and one do in its inbox")
    else:
        failures.append(f"  ✗ (m3) a line of before       rc={older.returncode} manager={h.agent_stands('manager')} "
                        f"{opening_o.get('agents')} {member_o}")
    return 0
