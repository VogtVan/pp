"""Scenario `team-status-json` -- 9 case(s): `team status --json` is the face a program reads -- ONE object for a
team named, one line per team declared without a name, each task with its `text` and its `last`, each face with
`required`. One house pinning `agent`, `team`, `steering` and `plan`; the clock frozen by `PP_NOW` on Thursday
2026-10-01. A team `crew` (m root, r1 r2 reporting to m, the mandator pm; `daily every weekday 09:30 with r1 r2 -> m
any 1`, `retro after daily with r1 -> m`), a team `texts` (w root, w1 reporting to w, `daily every weekday 09:30 with
w1 -> w`), a team `req` (q alone, `schedule: off`) started `--no-tick`, and two teams declared, never started: `idle`
and `none`.
- the team: after `start --no-tick`, crew's object carries the keys a program reads, T1 held by m, m's `do` pending;
  after T1 (m delegates to r1 in three words, its TURN between two other productions, r1 answers, m concludes), T1
  resolved with its delegation answered, r2 -- never woken -- has m's and r1's answers unseen, the owner's waiting box
  says T1 done, 3 wake-ups launched
- the cost of each task: every task says `cost`, the sum of its wake-ups' ends; the tasks' sum is the team's
- every team: without a name, one line per team declared, sorted; `idle` as `{team, started: null, state: never,
  waiting_on: [], required}`, which `status idle --json` says too; crew's line counts what waits for the owner
- refused: a flag of no verb's is the usage, a team nobody declared is `team-unknown`, nothing on stdout
- the text and the last: T1 of texts says the message of `start` as `text` and its `do` post as `last`; once
  resolved, its `last` is still the last object `log --json --task T1` gives, its wake-ups among them
- the snapshot: T2 opened, `team snapshot`, then every task's `text` and `last` as before; a note on T2 after it
  moves T2's `last` to that note, T1's stays
- the ring: a daily rung at hand -- its task says the ring's consigne as `text`, the task event's, and its `last` is
  the last object of its log
- (a) the face says the required packages: req's object, none's object and every line without a name carry
  `required`, sorted, `team` in it, `plan` and `steering` out of it -- each name in it switched off at `team start
  --member n` is refused `package-required`, `plan` and `steering` switched off pass that judge
- (b) the text keeps its bytes: the text of `status req` the same bytes before and after the faces are read
"""
from __future__ import annotations

import hashlib
import json
import re

from tests.harness import support

T = support(__file__, "team")

CREW = ("---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\nroot: m\n"
        "principals: |\n  pm\nceremonies: |\n  daily every weekday 09:30 with r1 r2 -> m any 1\n"
        "  retro after daily with r1 -> m\n---\nKeep the beat.\n")
TEXTS = ("---\nagents: |\n  w agents/w\n  w1 agents/w1\nreports: |\n  w1 -> w\nroot: w\n"
         "ceremonies: |\n  daily every weekday 09:30 with w1 -> w\n---\nShip together.\n")
REQ = "---\nagents: |\n  q agents/q\nroot: q\nschedule: off\n---\nKeep going.\n"
NONE = "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n"
TEAMS = ["crew", "idle", "none", "req", "texts"]
# The keys of a team's object the cases read; a new field leaves them standing.
READ = {"team", "owner", "principals", "changed", "schedule", "cost", "wakes", "tasks", "members", "waiting",
        "required"}
# The keys of crew's line without a name the cases read.
LINE = {"team", "state", "waiting_on", "tasks", "running", "asks", "done", "required"}
NEVER = {"team": "idle", "started": None, "state": "never", "waiting_on": [], "required": ["agent", "kit", "team"]}
REFUSAL = re.compile(r"^pp-team: ([a-z][a-z-]*)", re.M)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={
        "m": [{"sleep": 0.1, "mode": "kit-words", "body": {"do": ["r1"]}}, {"sleep": 0.1, "body": {"done": "ok"}},
              {"sleep": 0.1, "body": {"done": "standup"}}, {"sleep": 0.1, "body": {"done": "retro"}}],
        "r1": [{"sleep": 0.1, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}},
               {"sleep": 0.1, "body": {"done": True}}],
        "r2": [{"sleep": 0.6, "body": {"done": True}}],
        "w": [{"sleep": 0.1, "body": {"do": ["w1"]}}, {"sleep": 0.1, "body": {"done": "shipped"}}],
        "w1": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def refusal(played) -> str:
        found = REFUSAL.search(played.stderr)
        return found.group(1) if found else ""

    def member(obj: dict, name: str) -> dict:
        return next((one for one in obj.get("members") or [] if one.get("member") == name), {})

    def tasks(when: str) -> dict:
        return {one.get("id"): one for one in h.face("texts", when).get("tasks") or []}

    def logged(task: str, when: str) -> list[dict]:
        played = h.call("team", "log", "texts", "--json", "--task", task, now=when)
        try:
            return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            return []

    def logged_last(task: str, when: str) -> dict | None:
        found = logged(task, when)
        return {"id": found[-1].get("id"), "kind": found[-1].get("event"), "at": found[-1].get("at")} if found else None

    def text_sha() -> str:
        return hashlib.sha256(h.call("team", "status", "req", now="09:40").stdout.encode()).hexdigest()[:12]

    h.declare("crew", CREW)
    h.declare("idle", "---\nagents: |\n  s s\nroot: s\n---\nNothing yet.\n")
    h.declare("texts", TEXTS)
    h.declare("req", REQ)
    h.declare("none", NONE)

    # every team started before the first wait: crew and texts run side by side
    started = h.call("team", "start", "crew", "--message", "ship it", *h.harnessed, "--no-tick", now="09:10")
    first = h.face("crew", "09:10")
    t1 = (first.get("tasks") or [{}])[0]
    pending_m = member(first, "m").get("pending") or []
    text_started = h.call("team", "start", "texts", "--message", "ship the release notes", *h.harnessed, "--no-tick",
                          now="09:10")
    text_first = tasks("09:10").get("T1") or {}
    text_first_log = logged_last("T1", "09:10")
    req_started = h.call("team", "start", "req", "--message", "go", *h.harnessed, "--no-tick", now="09:10")
    ticked = h.call("team", "tick", "crew", now="09:15")
    text_ticked = h.call("team", "tick", "texts", now="09:15")

    # --- the team ----------------------------------------------------------------------------------
    done_t1 = h.settled("crew", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    after = h.face("crew", "09:20")
    t1_after = next((task for task in after.get("tasks") or [] if task.get("id") == "T1"), {})
    found = h.events("crew")
    ended = {(e.get("agent"), e["id"]) for e in by_kind(found, "wake-ended")}
    unseen = {(u.get("member"), u.get("task"), u.get("id")) for u in member(after, "r2").get("unseen") or []}
    waiting = after.get("waiting") or {}
    if (started.returncode == 0 and READ <= set(first)
            and first.get("team") == "crew" and first.get("owner") == "house" and first.get("principals") == ["pm"]
            and first.get("schedule") == {"minutes": 5, "laid": True} and first.get("changed") is False
            and t1.get("id") == "T1" and t1.get("state") == "open" and t1.get("holders") == ["m"]
            and [(p.get("verb"), p.get("from"), p.get("task")) for p in pending_m] == [("do", "house", "T1")]
            and member(first, "m").get("run") is None and member(first, "m").get("path") == "agents/m"
            and ticked.returncode == 0 and done_t1 and after
            and t1_after.get("state") == "resolved" and t1_after.get("holders") == []
            and [(one.get("from"), one.get("to"), one.get("answered") is not None) for one in t1_after.get("dos") or []]
            == [("m", "r1", True)]
            and unseen == {(agent, "T1", eid) for agent, eid in ended} and {u[0] for u in unseen} == {"m", "r1"}
            and member(after, "m").get("how") == "ended" and member(after, "m").get("tasks") == ["T1"]
            and waiting.get("done") == ["T1"] and (after.get("wakes") or {}).get("launched") == 3):
        held("the team", f"one object, the {len(READ)} keys read among its {len(first)}; T1 held by m, its do "
             f"pending; after T1: resolved, the delegation m -> r1 answered, r2's unseen {sorted(unseen)}, waiting "
             "done T1, 3 wake-ups launched")
    else:
        failures.append(f"  ✗ the team                    rc={started.returncode}/{ticked.returncode} "
                        f"missing={sorted(READ - set(first))} t1={t1} pending={pending_m} done={done_t1} "
                        f"t1_after={t1_after} unseen={unseen} ended={ended} waiting={waiting} "
                        f"{started.stderr[-200:]!r}")

    # --- the cost of each task ------------------------------------------------------------------------
    tasks_after = after.get("tasks") or []
    costs = [task.get("cost") for task in tasks_after]
    team_cost = after.get("cost")
    if (costs and all(isinstance(one, (int, float)) and one > 0 for one in costs)
            and isinstance(team_cost, (int, float)) and abs(sum(costs) - team_cost) < 1e-6):
        held("the cost of each task", f"tasks {[(task.get('id'), task.get('cost')) for task in tasks_after]}, "
             f"their sum {team_cost} the team's")
    else:
        failures.append(f"  ✗ task cost                   costs={costs} team={team_cost}")

    # --- every team --------------------------------------------------------------------------------
    every = h.face(None, "09:50")
    alone = h.face("idle", "09:50")
    idle_line = next((one for one in every if one.get("team") == "idle"), {})
    crew_line = next((one for one in every if one.get("team") == "crew"), {})
    if ([one.get("team") for one in every] == TEAMS
            and all(idle_line.get(key) == value for key, value in NEVER.items()) and alone == idle_line
            and LINE <= set(crew_line)
            and crew_line.get("tasks", {}).get("open") == 0 and crew_line.get("tasks", {}).get("resolved") == 1
            and crew_line.get("running") == 0 and crew_line.get("asks") == 0 and crew_line.get("done") == 1
            and crew_line.get("state") == "idle" and crew_line.get("waiting_on") == []):
        held("every team", f"{len(every)} lines, sorted; idle {{team, started: null, state: never}} -- the same "
             f"alone; crew {crew_line.get('tasks')}, idle, done 1")
    else:
        failures.append(f"  ✗ every team                  every={every} alone={alone}")

    # --- refused -----------------------------------------------------------------------------------
    flagged = h.call("team", "status", "crew", "--json", "--task", "T1")
    unknown = h.call("team", "status", "nobody", "--json")
    if (flagged.returncode == 2 and refusal(flagged) == "usage" and flagged.stdout == ""
            and unknown.returncode == 2 and refusal(unknown) == "team-unknown" and unknown.stdout == ""):
        held("refused", "--task beside --json: the usage; a team nobody declared: team-unknown")
    else:
        failures.append(f"  ✗ refused                     rc={flagged.returncode}/{unknown.returncode} "
                        f"{flagged.stderr[-120:]!r} {unknown.stderr[-120:]!r}")

    # --- the text and the last ---------------------------------------------------------------------
    text_done = h.settled("texts", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    text_after = tasks("09:20").get("T1") or {}
    text_after_log = logged_last("T1", "09:20")
    kinds = [one.get("event") for one in logged("T1", "09:20")]
    if (text_started.returncode == 0 and text_first.get("text") == "ship the release notes"
            and text_first_log is not None and text_first.get("last") == text_first_log
            and text_first_log["kind"] == "post"
            and text_ticked.returncode == 0 and text_done and text_after.get("state") == "resolved"
            and text_after.get("text") == "ship the release notes" and text_after.get("last") == text_after_log
            and "wake-ended" in kinds and text_after_log["id"] > text_first_log["id"]):
        held("the text and the last", f"T1 says its message; last #{text_first_log['id']} post at its start, "
             f"#{text_after_log['id']} {text_after_log['kind']} once resolved -- the log's last each time")
    else:
        failures.append(f"  ✗ the text and the last       rc={text_started.returncode}/{text_ticked.returncode} "
                        f"done={text_done} first={text_first} first_log={text_first_log} after={text_after} "
                        f"after_log={text_after_log} kinds={kinds} {text_started.stderr[-200:]!r}")

    # --- the snapshot ------------------------------------------------------------------------------
    opened = h.call("team", "post", "texts", "--message", "draft the changelog", "--no-tick", now="09:25")
    before = tasks("09:26")
    snapped = h.call("team", "snapshot", "texts", now="09:27")
    kept = tasks("09:28")
    noted = h.call("team", "post", "texts", "--task", "T2", "--message", "mind the dates", "--no-tick", now="09:29")
    note_id = max((e["id"] for e in by_kind(h.events("texts"), "post", task="T2")), default=-1)
    moved = tasks("09:29")
    same = {key: (one.get("text"), one.get("last")) for key, one in before.items()} == \
        {key: (one.get("text"), one.get("last")) for key, one in kept.items()}
    if (opened.returncode == 0 and snapped.returncode == 0 and noted.returncode == 0 and same
            and (before.get("T2") or {}).get("text") == "draft the changelog"
            and ((moved.get("T2") or {}).get("last") or {}).get("id") == note_id
            and (moved.get("T2") or {}).get("last") == logged_last("T2", "09:29")
            and (moved.get("T1") or {}).get("last") == (before.get("T1") or {}).get("last")):
        held("the snapshot", f"T1 and T2 the same text and last across it; the note #{note_id} on T2 after it "
             "is T2's last, T1's unmoved")
    else:
        failures.append(f"  ✗ the snapshot                rc={opened.returncode}/{snapped.returncode}/{noted.returncode} "
                        f"same={same} before={before} kept={kept} moved={moved} note={note_id} "
                        f"{snapped.stderr[-200:]!r}")

    # --- the ring ----------------------------------------------------------------------------------
    rung = h.call("team", "ring", "texts", "daily", "--no-tick", now="09:31")
    ring_event = next((e for e in reversed(h.events("texts")) if e.get("kind") == "task" and e.get("ceremony") == "daily"),
                      {})
    ring_task = tasks("09:32").get(ring_event.get("task")) or {}
    if (rung.returncode == 0 and ring_event and ring_task.get("text") == ring_event.get("text")
            and ring_task.get("text") and ring_task.get("name") == ring_event.get("name")
            and ring_task.get("last") == logged_last(ring_event["task"], "09:32")):
        held("the ring", f"{ring_event['task']} « {ring_task.get('name')} » says its consigne "
             f"({len(ring_task['text'])} chars), its last the log's")
    else:
        failures.append(f"  ✗ the ring                    rc={rung.returncode} event={ring_event} task={ring_task} "
                        f"{rung.stderr[-200:]!r}")

    # --- (a) the face says the required packages ------------------------------------------------------
    sha_before = text_sha()
    named, never, lines = h.face("req"), h.face("none"), h.face()
    needed = named.get("required") or []
    judged = {}
    for package in [*needed, "plan", "steering"]:
        # a package switched off, then a switch off its form: the judge stops at the first it refuses
        played = h.call("team", "start", "none", "--message", "x", *h.harnessed, "--no-tick",
                        "--member", "n", "--package", f"{package}=off", "--package", "bad")
        judged[package] = (played.returncode, refusal(played))
    said = [(one.get("team"), one.get("required")) for one in [named, never, *lines]]
    if (req_started.returncode == 0 and needed == sorted(needed) and "team" in needed
            and "plan" not in needed and "steering" not in needed
            and len(said) == 2 + len(TEAMS) and all(required == needed for _, required in said)
            and all(judged[one] == (2, "package-required") for one in needed)
            and judged["plan"] == judged["steering"] == (2, "package-invalid")):
        held("(a) the face says the required packages", f"{needed} on req, on none never started and on each "
             "line -- each refused package-required, plan and steering past that judge -- KPQ1")
    else:
        failures.append(f"  ✗ (a) required              rc={req_started.returncode} needed={needed} said={said} "
                        f"judged={judged}")

    # --- (b) the text keeps its bytes ------------------------------------------------------------------
    sha_after = text_sha()
    if sha_before == sha_after and {"team", "started", "state", "waiting_on", "required"} <= set(never):
        held("(b) the text keeps its bytes", f"status req sha {sha_before} before and after; none says "
             "{team, started, state, waiting_on, required} -- KPQ2")
    else:
        failures.append(f"  ✗ (b) bytes                  {sha_before} {sha_after} {never}")
    return 0
