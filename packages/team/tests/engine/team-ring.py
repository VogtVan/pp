"""Scenario `team-ring` -- 5 case(s): `team ring <name> <ceremony>` rings a ceremony at hand, out of its
hour; a ceremony line ending on `any <n>` closes the facilitator's wait at the n-th answer; a task may carry
a name, and a ring names its task. Four teams run side by side in one house, each under its own names and
at its own frozen clock (`PP_NOW`); each case waits for its team, then reads its journal and its faces.
- (a) judged before writing: `team-unknown`, `team-not-started`, `ceremony-unknown`, `principal-unknown`,
  the usage without a ceremony -- rc 2, the journal byte-identical; a quorum out of its range at `start`
  (`any 0`, `any 3` of two participants, `any x`) refuses `team-invalid`, no journal
- (b) a ring at hand, then the every at its hour: at 08:00 `team ring gong daily --no-tick` writes
  `ceremony-due {daily, manual-<its id>, by: house}` -- `log --json` gives it back --, ONE task to f with
  its opening `do` to f and a `do` to p1 and p2; a second ring while that task is open refuses
  `ceremony-open` and writes no ring; a tick plays the ring: the participants answer, f resolves the
  task; the tick of 09:31 rings the daily's date, once
- (c) a quorum of 2 of 3: `daily every weekday 09:30 with r1 r2 r3 -> chair any 2`; the tick of 09:31
  rings -- `wait {chair, any 2, to r1 r2 r3}` after the three delegations --; r1 and r2 answer quickly, r3
  slowly; chair is woken after the second answer and before r3's end, delivered r1's and r2's answers and
  not r3's; chair resolves the daily while r3 still plays
- (d) a task named at its birth: `start --name`, `post --name`, a task without one -- a name a user types
  (`Prix de la DDR4`, `  Réunion fournisseurs  ` kept trimmed); the `task` event carries `name` (absent
  without), `status --json` says it with each task's state (`null` without), `log --json` too; an empty
  name, a line break, 81 characters refuse `name-invalid`, the journal byte-identical
- (e) a ring at hand on Thursday 10:05 names its task `daily 2026-10-01 10:05`; the facilitator's `do` goes
  to each participant on that task; neither the task nor a `do` carries the ceremony's declaration line
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def ring_team(facilitator: str, one: str, two: str, tail: str = "") -> str:
    """-> a TEAM.md: a facilitator and two participants, a daily ringing on weekdays, no schedule."""
    return (f"---\nagents: |\n  {facilitator} agents/{facilitator}\n  {one} agents/{one}\n  {two} agents/{two}\n"
            f"reports: |\n  {one} {two} -> {facilitator}\nroot: {facilitator}\n"
            f"ceremonies: |\n  daily every weekday 09:30 with {one} {two} -> {facilitator}{tail}\n"
            "schedule: off\n---\nRing on demand.\n")


QUORUM = ("---\nagents: |\n  chair agents/chair\n  r1 agents/r1\n  r2 agents/r2\n  r3 agents/r3\n"
          "reports: |\n  r1 r2 r3 -> chair\nroot: chair\n"
          "ceremonies: |\n  daily every weekday 09:30 with r1 r2 r3 -> chair any 2\n"
          "schedule: off\n---\nTwo voices suffice.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (b) the ring at hand: f answers the root, the manual ring, the dated ring
        "f": [{"sleep": 0.1, "body": {"done": "root"}}, {"sleep": 0.1, "body": {"done": "manual standup"}},
              {"sleep": 0.1, "body": {"done": "daily standup"}}],
        "p1": [{"sleep": 0.2, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}],
        "p2": [{"sleep": 0.2, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}}],
        # (c) the quorum: r3 ends seconds after r2 -- chair's wake-up falls between, with room under load
        "chair": [{"sleep": 0.1, "body": {"done": "root"}}, {"sleep": 0.1, "body": {"done": "quorum standup"}}],
        "r1": [{"sleep": 0.1, "body": {"done": True}}],
        "r2": [{"sleep": 0.3, "body": {"done": True}}],
        "r3": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    root_ended = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)

    # --- every team declared and started before the first wait: they run side by side ---------------
    h.declare("never", ring_team("v", "v1", "v2"))
    h.declare("gong", ring_team("f", "p1", "p2"))
    h.declare("quorum", QUORUM)
    bad_teams = {"q0": ring_team("w", "w1", "w2", " any 0"), "q3": ring_team("x", "x1", "x2", " any 3"),
                 "qx": ring_team("y", "y1", "y2", " any x")}
    for name, text in bad_teams.items():
        h.declare(name, text)
    h.declare("named", ring_team("buyer", "b1", "b2"))
    h.declare("rung", ring_team("host", "h1", "h2"))
    started = h.call("team", "start", "gong", "--message", "open the day", *h.harnessed, now="07:50")
    gate_q = bench.temp() / "quorum-gate"               # r3 held until chair resolves the daily
    q_started = h.call("team", "start", "quorum", "--message", "open the day", *T.gated(h, gate_q, ("r3",)),
                       now="09:10")
    bad = {name: h.call("team", "start", name, "--message", "x", "--no-tick", now="07:55") for name in bad_teams}
    n_started = h.call("team", "start", "named", "--message", "watch the prices", "--name", "  Réunion fournisseurs  ",
                       *h.harnessed, "--no-tick", now="07:50")
    r_started = h.call("team", "start", "rung", "--message", "open the day", *h.harnessed, "--no-tick", now="07:50")

    # the quorum's ring goes first: r3's long answer plays while the other cases run
    q_root = h.settled("quorum", root_ended, 45)
    q_rung = h.call("team", "tick", "quorum", now="09:31")

    # --- (a) judged before anything is written -------------------------------------------------------
    root = h.settled("gong", root_ended, 45)
    before = h.journal_of("gong").read_bytes()
    refusals = {
        "team-unknown": h.call("team", "ring", "nope", "daily", now="07:55"),
        "team-not-started": h.call("team", "ring", "never", "daily", now="07:55"),
        "ceremony-unknown": h.call("team", "ring", "gong", "weekly", now="07:55"),
        "principal-unknown": h.call("team", "ring", "gong", "daily", "--as", "zz", now="07:55"),
        "usage": h.call("team", "ring", "gong", now="07:55")}
    untouched = h.journal_of("gong").read_bytes() == before
    if (started.returncode == 0 and root and untouched
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and all(one.returncode == 2 and "team-invalid" in one.stderr for one in bad.values())
            and not any(h.journal_of(name).exists() for name in bad)):
        held("(a) judged before writing", "team-unknown, team-not-started, ceremony-unknown, principal-unknown, the "
             "usage: rc 2, the journal byte-identical; any 0, any 3 of two, any x: team-invalid, no journal")
    else:
        failures.append(f"  ✗ (a) judged before writing    rc={started.returncode} root={root} untouched={untouched} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]} "
                        f"{[(name, one.returncode, one.stderr.strip()[-120:]) for name, one in bad.items()]}")

    # --- (b) a ring at hand, a second refused, then the every at its hour ----------------------------
    # the ring and the second ring laid before the tick that plays them: the task is open at the second
    rung = h.call("team", "ring", "gong", "daily", "--no-tick", now="08:00")
    found = h.events("gong")
    manual = next(iter(by_kind(found, "ceremony-due", ceremony="daily")), {})
    task = next((one for one in found if one.get("kind") == "task" and one.get("ceremony") == "daily"), {})
    dos = [one.get("to") for one in by_kind(found, "post", verb="do") if one.get("task") == task.get("task")]
    delegs = [one.get("to") for one in T.delegated(found, task=task.get("task"))]
    again = h.call("team", "ring", "gong", "daily", "--no-tick", now="08:01")
    single = len(by_kind(h.events("gong"), "ceremony-due")) == 1
    played = h.call("team", "tick", "gong", now="08:01")

    # while gong's ring plays, the named team is written and read -- no wake-up there, every call `--no-tick`
    posted = h.call("team", "post", "named", "--message", "price of DDR4", "--name", "Prix de la DDR4", "--no-tick",
                    now="07:51")
    bare = h.call("team", "post", "named", "--message", "anything else", "--no-tick", now="07:52")
    journal = h.journal_of("named")
    n_before = journal.read_bytes() if journal.is_file() else b""
    invalid = [h.call("team", "post", "named", "--message", "x", "--name", given, "--no-tick", now="07:53")
               for given in ("   ", "line one\nline two", "x" * 81)]
    n_untouched = (journal.read_bytes() if journal.is_file() else b"") == n_before
    named_face = h.face("named", now="07:54")
    named_log = h.call("team", "log", "named", "--json", now="07:54")

    resolved = h.settled("gong", lambda found: bool(by_kind(found, "done", task=task.get("task")))
                         and all_ended(found), 45)
    dated = h.call("team", "tick", "gong", now="09:31")
    rang = h.call("team", "ring", "rung", "daily", "--no-tick", now="10:05")      # (e), while the daily plays
    daily = h.settled("gong", lambda found: len(by_kind(found, "ceremony-due")) == 2
                      and len(by_kind(found, "done")) == 3 and all_ended(found), 45)
    found = h.events("gong")
    dues = by_kind(found, "ceremony-due")
    logged = [json.loads(line) for line in h.call("team", "log", "gong", "--json", now="09:40").stdout.splitlines()
              if line.strip()]
    logged_dues = [(one.get("ceremony"), one.get("period"), one.get("by")) for one in logged
                   if one.get("event") == "ceremony-due"]
    if (rung.returncode == 0 and played.returncode == 0
            and manual.get("period") == f"manual-{manual.get('id')}" and manual.get("by") == "house"
            and task.get("to") == "f" and task.get("period") == manual.get("period")
            and sorted(dos) == ["f", "p1", "p2"] and sorted(delegs) == ["p1", "p2"]
            and again.returncode == 2 and "ceremony-open" in again.stderr and single and resolved
            and result_of(found, task.get("task")) == "manual standup"
            and dated.returncode == 0 and daily and [one.get("period") for one in dues][1:] == ["2026-10-01"]
            and logged_dues[:1] == [("daily", manual.get("period"), "house")]):
        held("(b) a ring at hand, then the every", f"08:00: ceremony-due {manual.get('period')} by house (log --json "
             f"too), {task.get('task')} to f, its opening to f and a do to p1 and p2; a second ring ceremony-open; "
             "'manual standup'; 09:31 rings 2026-10-01, once")
    else:
        failures.append(f"  ✗ (b) a ring at hand           rc={rung.returncode}/{again.returncode}/{played.returncode}/"
                        f"{dated.returncode} "
                        f"manual={manual} task={task} dos={dos} delegs={delegs} single={single} resolved={resolved} "
                        f"daily={daily} dues={[(one.get('period'), one.get('by')) for one in dues]} "
                        f"logged={logged_dues} {rung.stderr.strip()[-200:]!r} {again.stderr.strip()[-200:]!r}")

    # --- (c) a quorum of 2 of 3 ----------------------------------------------------------------------
    q_resolved = h.settled("quorum", lambda found: bool(by_kind(found, "done", task="T2")), 45)
    found = h.events("quorum")
    gate_q.write_text("open", encoding="utf-8")
    declared = next(iter(by_kind(found, "team-started")), {}).get("ceremonies") or [{}]
    waits = [(one.get("agent"), one.get("task"), one.get("any"), sorted(one.get("to") or []))
             for one in by_kind(found, "wait")]
    last_deleg = max((one["id"] for one in T.delegated(found, task="T2")), default=10 ** 9)
    wait_id = next((one["id"] for one in by_kind(found, "wait")), -1)
    on_t2 = next((one for one in by_kind(found, "wake-intent", agent="chair") if one.get("task") == "T2"), {})
    answer_of = {one.get("from"): one["id"] for one in by_kind(found, "post", verb="re", task="T2")}
    closed = next((one["id"] for one in by_kind(found, "done", task="T2")), 10 ** 9)
    q_done = h.settled("quorum", all_ended, 45)
    after = h.events("quorum")
    r3_end = next((one["id"] for one in by_kind(after, "wake-ended", agent="r3")), 10 ** 9)
    r3_answer = next((one["id"] for one in by_kind(after, "post", verb="re", task="T2") if one.get("from") == "r3"),
                     None)
    delivered = set(on_t2.get("messages") or [])
    if (q_started.returncode == 0 and q_root and declared[0].get("quorum") == 2 and q_rung.returncode == 0
            and q_resolved and waits == [("chair", "T2", 2, ["r1", "r2", "r3"])] and wait_id > last_deleg
            and on_t2 and on_t2["id"] < closed < r3_end < 10 ** 9
            and "r1" in answer_of and "r2" in answer_of and "r3" not in answer_of
            and {answer_of["r1"], answer_of["r2"]} <= delivered and r3_answer is not None
            and r3_answer not in delivered and result_of(found, "T2") == "quorum standup" and q_done):
        held("(c) a quorum of 2 of 3", f"wait {{chair, any 2}} #{wait_id} after the delegations; chair woken "
             f"#{on_t2['id']} with r1's #{answer_of['r1']} and r2's #{answer_of['r2']}, T2 'quorum standup' "
             f"#{closed}, both before r3's end #{r3_end}")
    else:
        failures.append(f"  ✗ (c) a quorum of 2 of 3       rc={q_started.returncode}/{q_rung.returncode} root={q_root} "
                        f"declared={declared} resolved={q_resolved} waits={waits} wait={wait_id}/{last_deleg} "
                        f"chair={on_t2} answers={answer_of} r3={r3_end}/{r3_answer} done={q_done} "
                        f"{q_started.stderr.strip()[-200:]!r} {q_rung.stderr.strip()[-200:]!r}")

    # --- (d) a task named at its birth ---------------------------------------------------------------
    tasks = by_kind(h.events("named"), "task")
    named = {one["id"]: (one.get("name", "?"), one.get("state")) for one in named_face.get("tasks") or []}
    logged_names = [json.loads(line).get("name") for line in named_log.stdout.splitlines()
                    if line.strip() and json.loads(line).get("event") == "task"]
    if (n_started.returncode == 0 and posted.returncode == 0 and bare.returncode == 0
            and [one.get("name") for one in tasks] == ["Réunion fournisseurs", "Prix de la DDR4", None]
            and "name" not in tasks[2]
            and named == {"T1": ("Réunion fournisseurs", "open"), "T2": ("Prix de la DDR4", "open"),
                          "T3": (None, "open")}
            and logged_names == ["Réunion fournisseurs", "Prix de la DDR4", None]
            and all(one.returncode == 2 and "name-invalid" in one.stderr for one in invalid) and n_untouched):
        bench.refusals += 3
        held("(d) a task named at its birth", "start and post --name write a name a user types (`Réunion "
             "fournisseurs` trimmed, `Prix de la DDR4`); status --json and log --json say it (null without), each "
             "task open; empty, two lines, 81 characters refuse name-invalid")
    else:
        failures.append(f"  ✗ (d) named                  rc={n_started.returncode}/{posted.returncode}/{bare.returncode}/"
                        f"{[one.returncode for one in invalid]} tasks={[one.get('name') for one in tasks]} face={named} "
                        f"log={logged_names} untouched={n_untouched} {[one.stderr.strip()[-100:] for one in invalid]!r} "
                        f"{n_started.stderr.strip()[-160:]!r}")

    # --- (e) a ring names its task -------------------------------------------------------------------
    found = h.events("rung")
    ring_task = next((one for one in by_kind(found, "task") if one.get("ceremony") == "daily"), {})
    dos = [one for one in by_kind(found, "post", verb="do") if one.get("task") == ring_task.get("task")
           and one.get("from") == "host"]                    # the participants' dos; the opening goes to host
    declaration = next(line.strip() for line in ring_team("host", "h1", "h2").splitlines() if " every " in line)
    said = [ring_task.get("text") or ""] + [one.get("text") or "" for one in dos]
    if (r_started.returncode == 0 and rang.returncode == 0 and ring_task.get("name") == "daily 2026-10-01 10:05"
            and ring_task.get("to") == "host" and sorted(one.get("to") for one in dos) == ["h1", "h2"]
            and all(one and declaration not in one for one in said)):
        held("(e) a ring names its task", f"`{ring_task.get('name')}` to host, its do to h1 and h2 on "
             f"{ring_task.get('task')} -- never the declaration line")
    else:
        failures.append(f"  ✗ (e) a ring names its task    rc={r_started.returncode}/{rang.returncode} task={ring_task} "
                        f"dos={dos} {rang.stderr.strip()[-160:]!r}")
    return 0
