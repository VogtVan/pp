"""Scenario `team-bounds` -- 6 case(s): the bounds of the tick, each met by a team of its own under the witness;
what the tick says to the owner when a bound is met, it says in the TEAM's name -- a notice, which asks nothing
and opens no debt. Four teams run side by side in one house; each case waits for its team, then reads its journal,
its face (`status --json`) and the owner's inbox.
- `budget: 0.015` holds: two wake-ups are paid (0.02), the third agent due is never launched -- `budget-spent`
  once, the team's notice to the owner; the face says the cost spent, the budget spent and the notice in the
  owner's inbox
- a ping-pong stops: under `wakes: 3`, two members trading `ask`/`reply` stop at the task's third wake-up --
  `wakes-spent` once, the team's notice to the owner, a later tick launches nothing more
- (a) a guard notices, `wakes-spent`: the team's notice to the owner and no `escalate`; `inbox --json` lists it
  under `notices` (`awaits: false`), never under `questions`; `inbox --seen` takes it away
- a costless provider is bounded: under `budget-wakes: 2`, two wake-ups play, the third due is never launched --
  `budget-spent {unit: wakes}` once; the face says the budget spent and the notice in the owner's inbox
- (b) a guard notices, `budget-spent`: the same as (a), on the costless bound
- `budget-wakes` counts from the start: two wake-ups on a first task, a second start under `budget-wakes: 2`
  still plays its own
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # budget: b delegates two, parallel 1: b1 plays, b2 is due when the budget is spent
        "b": [{"sleep": 0.2, "body": {"do": ["b1", "b2"]}}],
        "b1": [{"sleep": 0.3, "body": {"done": True}}],
        # wakes: f2 and c trade ask/reply on T1
        "f2": [{"sleep": 0.1, "body": {"do": ["c"]}},
               {"sleep": 0.1, "body": {"reply": {"to": "c", "text": "again"}}},
               {"sleep": 0.1, "body": {"reply": {"to": "c", "text": "and again"}}}],
        "c": [{"sleep": 0.1, "body": {"ask": {"to": "f2", "text": "q1"}}},
              {"sleep": 0.1, "body": {"ask": {"to": "f2", "text": "q2"}}},
              {"sleep": 0.1, "body": {"ask": {"to": "f2", "text": "q3"}}}],
        # budget-wakes: n delegates to n1, n's wake-up for n1's answer is the third
        "n": [{"sleep": 0.1, "body": {"do": ["n1"]}},
              {"sleep": 0.1, "body": {"done": "never reached"}}],
        "n1": [{"sleep": 0.1, "body": {"done": True}}],
        # the restart: an answer that is no JSON object, then a done per start
        "uw": [{"sleep": 0.1, "body": "prose"},
               {"sleep": 0.1, "body": {"done": "first"}},
               {"sleep": 0.1, "body": {"done": "second"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def inbox(name: str) -> dict:
        said = h.call("team", "inbox", name, "--json").stdout.strip()
        try:
            return json.loads(said) if said else {}
        except ValueError:
            return {"unreadable": said}

    def noticed(name: str, found: list[dict]) -> tuple:
        """-> whether the owner is told by a notice of the team alone, read in `inbox --json` and gone at `--seen`."""
        told = by_kind(found, "post", to="house")
        box = inbox(name)
        seen = h.call("team", "inbox", name, "--seen")
        after = inbox(name)
        ok = (seen.returncode == 0 and not by_kind(found, "post", verb="escalate")
              and [(one.get("from"), one.get("verb")) for one in told] == [(name, "notice")]
              and not box.get("questions") and [(one.get("id"), one.get("awaits")) for one in box.get("notices") or []]
              == [(told[0]["id"], False)] and not (after.get("notices") or after.get("questions")))
        return ok, told, box, after

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("budgeted", "---\nagents: |\n  b b\n  b1 b1\n  b2 b2\nreports: |\n  b1 b2 -> b\n"
                          "root: b\nparallel: 1\nbudget: 0.015\n---\nSpend little.\n")
    h.declare("pong", "---\nagents: |\n  f2 f2\n  c c\nreports: |\n  c -> f2\nroot: f2\nwakes: 3\n---\nStop the rally.\n")
    h.declare("nocost", "---\nagents: |\n  n n\n  n1 n1\nreports: |\n  n1 -> n\nroot: n\nbudget-wakes: 2\n---\n"
                        "Count the wake-ups.\n")
    h.declare("restart", "---\nagents: |\n  uw uw\nroot: uw\nbudget-wakes: 2\n---\nStart twice.\n")
    budgeted = h.call("team", "start", "budgeted", "--message", "review cheaply", *h.harnessed)
    pong = h.call("team", "start", "pong", "--message", "talk it over", *h.harnessed)
    nocost = h.call("team", "start", "nocost", "--message", "spend nothing", *h.harnessed)
    first_w = h.call("team", "start", "restart", "--message", "first", *h.harnessed)

    # --- budget: 0.015 holds: two wake-ups paid, the third not launched, the owner told ---------------
    spent = h.settled("budgeted", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), timeout=60)
    found = h.events("budgeted")
    spent_events = by_kind(found, "budget-spent")
    escalated = by_kind(found, "post", verb="notice", to="house")
    intents_b = [one.get("agent") for one in by_kind(found, "wake-intent")]
    face_b = h.face("budgeted")
    owner_b = [(one.get("id"), one.get("verb"), one.get("from"), one.get("task")) for one in face_b.get("owner_inbox") or []]
    if (budgeted.returncode == 0 and spent and len(spent_events) == 1
            and abs(spent_events[0].get("spent", 0) - 0.02) < 1e-9 and spent_events[0].get("budget") == 0.015
            and len(escalated) == 1 and escalated[0].get("from") == "budgeted"
            and sorted(intents_b) == ["b", "b1"] and "b2" not in intents_b
            and abs(float(face_b.get("cost") or 0) - 0.02) < 1e-9 and face_b.get("budget_spent") is True
            and owner_b == [(escalated[0]["id"], "notice", "budgeted", "T1")]):
        held("budget: 0.015 holds", f"two wake-ups paid (0.02), b2 not launched: budget-spent once, notice "
             f"#{escalated[0]['id']} budgeted -> house; the face says cost 0.02, budget_spent, the notice on T1 "
             "alone in the owner's inbox")
    else:
        failures.append(f"  ✗ budget                      rc={budgeted.returncode} spent={spent} events={spent_events} "
                        f"escalated={len(escalated)} intents={intents_b} cost={face_b.get('cost')} "
                        f"budget_spent={face_b.get('budget_spent')} owner={owner_b} {budgeted.stderr[-200:]!r}")

    # --- a ping-pong stops; (a) its notice in the owner's inbox ---------------------------------------
    spent_p = h.settled("pong", lambda found: bool(by_kind(found, "wakes-spent")) and all_ended(found), timeout=60)
    found_p = h.events("pong")
    intents_p = by_kind(found_p, "wake-intent")
    wakes_events = by_kind(found_p, "wakes-spent")
    esc_p = by_kind(found_p, "post", verb="notice", **{"from": "pong"})
    ok_a, told_a, box_a, after_a = noticed("pong", found_p)
    more = h.call("team", "tick", "pong")
    after_more = by_kind(h.events("pong"), "wake-intent")
    if (pong.returncode == 0 and spent_p and len(intents_p) == 3
            and all(one.get("task") == "T1" for one in intents_p)
            and len(wakes_events) == 1 and wakes_events[0].get("task") == "T1"
            and wakes_events[0].get("spent") == 3 and wakes_events[0].get("wakes") == 3
            and len(esc_p) == 1 and esc_p[0].get("to") == "house"
            and more.returncode == 0 and len(after_more) == 3):
        held("a ping-pong stops", "wakes 3: f2 and c trade ask/reply, the task's third wake-up is the last -- "
             "wakes-spent once, the notice pong -> house, a later tick launches nothing more")
    else:
        failures.append(f"  ✗ wakes bound                 rc={pong.returncode} spent={spent_p} "
                        f"intents={len(intents_p)}/{len(after_more)} events={wakes_events} esc={len(esc_p)} "
                        f"{pong.stderr[-150:]!r}")
    if pong.returncode == 0 and spent_p and ok_a:
        held("(a) a guard notices", f"wakes-spent: the team's notice #{told_a[0]['id']} to house, under notices "
             "(awaits false), gone at --seen; no escalate")
    else:
        failures.append(f"  ✗ (a) a guard notices      told={[(one.get('from'), one.get('verb')) for one in told_a]} "
                        f"box={box_a} after={after_a}")

    # --- a costless provider is bounded; (b) its notice in the owner's inbox ----------------------------
    spent_n = h.settled("nocost", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), timeout=60)
    found_n = h.events("nocost")
    bspent = by_kind(found_n, "budget-spent")
    face_n = h.face("nocost")
    ok_b, told_b, box_b, after_b = noticed("nocost", found_n)
    if (nocost.returncode == 0 and spent_n and len(by_kind(found_n, "wake-intent")) == 2
            and len(bspent) == 1 and bspent[0].get("unit") == "wakes"
            and bspent[0].get("spent") == 2 and bspent[0].get("budget") == 2
            and face_n.get("budget_spent") is True and len(face_n.get("owner_inbox") or []) == 1):
        held("a costless provider is bounded", "budget-wakes 2: two wake-ups play, the third due is never "
             "launched -- budget-spent {unit: wakes} once; the face says budget_spent and one post in the owner's inbox")
    else:
        failures.append(f"  ✗ budget-wakes                rc={nocost.returncode} spent={spent_n} "
                        f"intents={len(by_kind(found_n, 'wake-intent'))} bspent={bspent} "
                        f"budget_spent={face_n.get('budget_spent')} owner={face_n.get('owner_inbox')} "
                        f"{nocost.stderr[-150:]!r}")
    if nocost.returncode == 0 and spent_n and ok_b:
        held("(b) a guard notices", f"budget-spent: the team's notice #{told_b[0]['id']} to house, under notices "
             "(awaits false), gone at --seen; no escalate")
    else:
        failures.append(f"  ✗ (b) a guard notices      told={[(one.get('from'), one.get('verb')) for one in told_b]} "
                        f"box={box_b} after={after_b}")

    # --- budget-wakes counts from the start --------------------------------------------------------
    done_w1 = h.settled("restart", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    second_w = h.call("team", "start", "restart", "--message", "second", *h.harnessed)
    done_w2 = h.settled("restart", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=30)
    found_w = h.events("restart")
    starts = by_kind(found_w, "team-started")
    after_second = [one for one in by_kind(found_w, "wake-intent") if starts and one["id"] > starts[-1]["id"]]
    if (first_w.returncode == 0 and second_w.returncode == 0 and done_w1 and done_w2
            and len(after_second) == 1 and not by_kind(found_w, "budget-spent")):
        held("budget-wakes counts from the start", "two wake-ups on T1, then a second start under "
             "budget-wakes 2 plays its own: done T2, no budget-spent")
    else:
        failures.append(f"  ✗ wakes since start           {first_w.returncode}/{second_w.returncode} "
                        f"done={done_w1}/{done_w2} after={len(after_second)} "
                        f"spent={by_kind(found_w, 'budget-spent')}")
    return 0
