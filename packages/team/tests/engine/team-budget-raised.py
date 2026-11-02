"""Scenario `team-budget-raised` -- 4 case(s): `team budget` raises a started team's bounds without a start --
`budget-raised`, the replay's limits raised and `budget-spent` lifted, the members' runs kept --; `team resume`
judges the team's budget before whether the task is blocked. Four teams run side by side in one house, each under
its own names; each case reads its team's journal, its face (`team status <name> --json`) and the codes of the
refusals.
- (c) the budget raised in money: `budget: 0.015`, two wake-ups paid (0.02), `budget-spent`; `team budget` at or
  below what is spent refuses `budget-invalid`, a team never started refuses `team-not-started`; `team budget 1`
  writes `budget-raised` and the member due is woken
- (d) the budget raised in launches: `budget-launches: 1`, the member asks the owner, the reply finds the bound
  spent; `team budget --launches 2` and the member is woken in its SAME run, the task done; the face carries the
  money spent and left and the launches against the raised bound
- (d) a task the budget alone holds: under `budget-launches: 1` only, the reply finds the bound spent; `team resume`
  refuses `budget-spent` -- never `task-not-blocked` -- and writes nothing
- (e) two writers: two `team budget --launches` played together, five times -- every `budget-raised` kept, the
  journal's ids consecutive
"""
from __future__ import annotations

import re
import subprocess
import sys

from tests.harness import support

T = support(__file__, "team")

REFUSAL = re.compile(r"^pp-team: (\S+) -- ", re.M)


def codes_of(played: subprocess.CompletedProcess) -> list[str]:
    """-> the codes of the refusals a call wrote on stderr, in order."""
    return REFUSAL.findall(played.stderr or "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (c) b delegates to b1 and b2 under one parallel slot: the money runs out before b2
        "b": [{"sleep": 0.2, "body": {"do": ["b1", "b2"]}}, {"sleep": 0.1, "body": {"done": "paid"}}],
        "b1": [{"sleep": 0.2, "body": {"done": True}}],
        "b2": [{"sleep": 0.1, "body": {"done": True}}],
        # (d) in launches: w asks the owner, then closes once the bound is raised
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which date?"}}},
              {"sleep": 0.1, "body": {"done": "dated"}}],
        # (d) the budget alone holds: k asks the owner, never woken again
        "k": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which day?"}}},
              {"sleep": 0.1, "body": {"done": "never"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    asked = lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found)
    done_t1 = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)

    def reply(name: str, text: str) -> subprocess.CompletedProcess:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        return h.call("team", "post", name, "--task", "T1", "--reply", str(ask), "--message", text)

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("paid", "---\nagents: |\n  b agents/b\n  b1 agents/b1\n  b2 agents/b2\nreports: |\n  b1 b2 -> b\n"
                      "root: b\nparallel: 1\nbudget: 0.015\nschedule: off\n---\nSpend little.\n")
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\n---\nNever started.\n")
    h.declare("dated", "---\nagents: |\n  w agents/w\nroot: w\nbudget-launches: 1\nbudget: 3\nschedule: off\n---\n"
                       "One launch.\n")
    h.declare("held", "---\nagents: |\n  k agents/k\nroot: k\nbudget-launches: 1\nschedule: off\n---\nOne launch.\n")
    h.declare("count", "---\nagents: |\n  writer agents/writer\nroot: writer\nbudget-launches: 1\nschedule: off\n---\n"
                       "One launch.\n")
    paid = h.call("team", "start", "paid", "--message", "review cheaply", *h.harnessed)
    dated = h.call("team", "start", "dated", "--message", "date the release", *h.harnessed)
    started_k = h.call("team", "start", "held", "--message", "cut the branch", *h.harnessed)
    counted = h.call("team", "start", "count", "--message", "date the release", *h.harnessed, "--no-tick")

    # --- (e) two writers: two `team budget` at once, five times --------------------------------------------
    before = len(h.events("count"))
    for n in range(5):
        pair = [subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "budget", "count",
                                  "--launches", str(launches), "--no-tick"],
                                 cwd=str(h.ws), env={**h.env}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for launches in (3 + 2 * n, 4 + 2 * n)]
        for one in pair:
            one.communicate(timeout=60)
    found = h.events("count")
    ids = [one["id"] for one in found]
    raised_n = sorted(one.get("launches") for one in by_kind(found[before:], "budget-raised"))
    if (counted.returncode == 0 and ids and ids == list(range(ids[0], ids[0] + len(ids)))
            and raised_n == list(range(3, 13))):
        held("(e) two writers", f"two team budget at once, five times: 10 budget-raised kept, "
             f"{len(ids)} ids consecutive")
    else:
        failures.append(f"  ✗ (e) two writers           rc={counted.returncode} ids={ids[-12:]} raised={raised_n}")

    # --- (c) the budget raised in money ----------------------------------------------------------------
    spent = h.settled("paid", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), 60)
    low = h.call("team", "budget", "paid", "0.02")
    unstarted = h.call("team", "budget", "never", "1")
    raised = h.call("team", "budget", "paid", "1")
    done_c = h.settled("paid", done_t1, 60)
    found = h.events("paid")
    raises = by_kind(found, "budget-raised")
    after = [one["agent"] for one in by_kind(found, "wake-intent") if raises and one["id"] > raises[0]["id"]]
    if (paid.returncode == 0 and spent and low.returncode == 2 and codes_of(low) == ["budget-invalid"]
            and unstarted.returncode == 2 and codes_of(unstarted) == ["team-not-started"]
            and raised.returncode == 0 and len(raises) == 1 and raises[0].get("budget") == 1.0 and done_c
            and "b2" in after and len(by_kind(found, "budget-spent")) == 1):
        held("(c) the budget raised in money", f"0.02 spent of 0.015: budget-spent; 0.02 refuses budget-invalid, a "
             f"team never started team-not-started; budget 1 raised #{raises[0]['id']}, then {' '.join(after)} "
             "woken, T1 done")
    else:
        failures.append(f"  ✗ (c) raised in money        rc={paid.returncode}/{low.returncode}/{unstarted.returncode}/"
                        f"{raised.returncode} spent={spent} raises={raises} after={after} done={done_c} "
                        f"codes={codes_of(low)}/{codes_of(unstarted)} {raised.stderr.strip()[-200:]!r}")

    # --- (d) the budget raised in launches: the member woken in its SAME run ---------------------------------
    asked_w = h.settled("dated", asked, 60)
    replied_w = reply("dated", "main")
    spent_w = by_kind(h.events("dated"), "budget-spent")
    raised_w = h.call("team", "budget", "dated", "--launches", "2")
    done_w = h.settled("dated", done_t1, 60)
    found = h.events("dated")
    first_run = next((one.get("run") for one in by_kind(found, "wake-ended", agent="w")), None)
    runs = [one.get("run") for one in by_kind(found, "wake-intent", agent="w")]
    face = h.face("dated")
    if (dated.returncode == 0 and asked_w and replied_w.returncode == 0 and len(spent_w) == 1
            and spent_w[0].get("unit") == "launches" and raised_w.returncode == 0 and done_w
            and runs == [None, first_run] and first_run
            and face.get("budget") == {"cap": 3.0, "spent": 0.02, "reserved": 0.0, "left": 2.98}
            and face.get("launches") == {"launched": 2, "bound": 2} and face.get("budget_spent") is False):
        held("(d) the budget raised in launches", f"budget-launches 1 spent; --launches 2 raised; w woken in its run "
             f"{first_run}, T1 done; the face's budget {face['budget']}, launches {face['launches']}")
    else:
        failures.append(f"  ✗ (d) raised in launches     rc={dated.returncode}/{replied_w.returncode}/"
                        f"{raised_w.returncode} asked={asked_w} spent={spent_w} done={done_w} runs={runs} "
                        f"first={first_run} budget={face.get('budget')} launches={face.get('launches')} "
                        f"budget_spent={face.get('budget_spent')!r} {raised_w.stderr.strip()[-200:]!r}")

    # --- (d) a task the budget alone holds: resume says budget-spent, writes nothing --------------------------
    asked_k = h.settled("held", asked, 60)
    replied_k = reply("held", "monday")
    spent_k = by_kind(h.events("held"), "budget-spent")
    before_k = h.journal_of("held").read_bytes()
    refused_k = h.call("team", "resume", "held", "--task", "T1")
    if (started_k.returncode == 0 and asked_k and replied_k.returncode == 0 and spent_k and refused_k.returncode == 2
            and codes_of(refused_k) == ["budget-spent"] and h.journal_of("held").read_bytes() == before_k):
        held("(d) a task the budget alone holds", "budget-launches 1 spent at the reply: team resume refuses "
             "budget-spent, never task-not-blocked, the journal untouched")
    else:
        failures.append(f"  ✗ (d) the budget alone holds rc={started_k.returncode}/{replied_k.returncode}/"
                        f"{refused_k.returncode} asked={asked_k} spent={spent_k} codes={codes_of(refused_k)}")
    return 0
