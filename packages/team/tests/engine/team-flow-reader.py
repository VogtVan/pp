"""Scenario `team-flow-reader` -- 2 case(s) (batch les-echecs-du-tick, team 0.41.0; KET10; study § 21, row 106): the
reader of a member's flow starts at the exchange the launch OPENED, found by its tag -- never at a kept rank alone.
- (a) a journal of before routes nothing old: T1 played whole under the witness (q answers o's `do`), then every
  `flow` rank taken out of the journal's `wake-ended` lines -- a journal written before team 0.40.0 --; T2 posted,
  o delegates to q again: q's launch on T2 routes its own answer alone (one `wake-routed` of its tag, its `line` past
  the old verdict's), no old act is routed again (q's two `re` cite two different `do`s), its `wake-ended.flow` is the
  rank of ITS verdict, T2 done
- (b) a chat between two launches is skipped: an exchange of q's run opened by the house outside the team (`agent run
  --run`, a verdict after the kept rank) stands between T2 and T3: q's launch on T3 routes its own answer, T3 done
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "o": {task: [{"sleep": 0.1, "body": {"do": ["q"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": f"{task} done"}}]
              for task in ("T1", "T2", "T3")},
        "q": {task: [{"sleep": 0.1, "body": {"re": "DO", "text": f"part of {task}"}}] for task in ("T1", "T2", "T3")}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    closed = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)

    # --- (a) a journal of before routes nothing old ---------------------------------------------------------------
    h.declare("aged", "---\nagents: |\n  o agents/o\n  q agents/q\nreports: |\n  q -> o\nroot: o\nschedule: off\n---\n"
                      "Count the parts.\n")
    started = h.call("team", "start", "aged", "--message", "first", *h.harnessed)
    done1 = h.settled("aged", closed("T1"), timeout=40)
    journal = h.journal_of("aged")
    before = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    old_rank = max((int(one.get("flow") or 0) for one in before if one.get("kind") == "wake-ended" and one.get("agent") == "q"), default=0)
    journal.write_text("".join(json.dumps({key: value for key, value in one.items() if key != "flow"}) + "\n"
                               for one in before), encoding="utf-8")                  # a journal written before 0.40.0
    posted = h.call("team", "post", "aged", "--message", "second")
    done2 = h.settled("aged", closed("T2"), timeout=40)
    found = h.events("aged")
    q_t2 = T.intents_on(found, "q", "T2")
    tag2 = q_t2[0].get("tag") if q_t2 else None
    routed2 = [one for one in by_kind(found, "wake-routed", tag=tag2)]
    ended2 = [one for one in by_kind(found, "wake-ended", tag=tag2)]
    answers = [one.get("re") for one in by_kind(found, "post", verb="re", **{"from": "q"})]
    dos = [one["id"] for one in by_kind(found, "post", verb="do", to="q")]
    if (started.returncode == 0 and done1 and posted.returncode == 0 and done2 and old_rank > 0 and len(q_t2) == 1
            and len(routed2) == 1 and int(routed2[0].get("line") or 0) > old_rank
            and len(ended2) == 1 and int(ended2[0].get("flow") or 0) > int(routed2[0].get("line") or 0)
            and answers == dos and result_of(found, "T2") == "T2 done"):
        held("(a) a journal of before routes nothing old", f"q's launch on T2 found its exchange by its tag past the old "
             f"verdict (line {routed2[0].get('line')} > {old_rank}): one act routed, its two re cite its two do, "
             f"wake-ended.flow {ended2[0].get('flow')}, T2 'T2 done'")
    else:
        failures.append(f"  ✗ (a) a journal of before     rc={started.returncode}/{posted.returncode} done={done1}/{done2} "
                        f"old_rank={old_rank} intents={len(q_t2)} routed={[(one.get('line'), one.get('words')) for one in routed2]} "
                        f"ended={[one.get('flow') for one in ended2]} answers={answers} dos={dos} "
                        f"result={result_of(found, 'T2')!r}")

    # --- (b) a chat between two launches is skipped ----------------------------------------------------------------
    run_q = next((one.get("run") for one in reversed(found) if one.get("kind") == "wake-ended" and one.get("agent") == "q"), None)
    chatted = h.call("agent", "run", "agents/q", "--run", str(run_q), "--message", "a word outside the team", *h.harnessed)
    posted3 = h.call("team", "post", "aged", "--message", "third")
    done3 = h.settled("aged", closed("T3"), timeout=40)
    found = h.events("aged")
    q_t3 = T.intents_on(found, "q", "T3")
    tag3 = q_t3[0].get("tag") if q_t3 else None
    routed3 = by_kind(found, "wake-routed", tag=tag3)
    answers = [one.get("re") for one in by_kind(found, "post", verb="re", **{"from": "q"})]
    dos = [one["id"] for one in by_kind(found, "post", verb="do", to="q")]
    if (chatted.returncode == 0 and posted3.returncode == 0 and done3 and len(q_t3) == 1 and len(routed3) == 1
            and answers == dos and result_of(found, "T3") == "T3 done"):
        held("(b) a chat between two launches is skipped", f"an exchange of run {run_q} opened outside the team between "
             "T2 and T3: q's launch on T3 routed its own answer alone, T3 'T3 done'")
    else:
        failures.append(f"  ✗ (b) a chat between launches rc={chatted.returncode}/{posted3.returncode} done={done3} "
                        f"intents={len(q_t3)} routed={len(routed3)} answers={answers} dos={dos} "
                        f"result={result_of(found, 'T3')!r} {chatted.stderr[-160:]!r}")
    return 0
