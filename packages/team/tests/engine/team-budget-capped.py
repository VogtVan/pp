"""Scenario `team-budget-capped` -- 2 case(s) (batch la-part-calculee, 2026-10-11: row 75 of the study § 18,
team 0.29.0, agent 0.23.3): a wake-up its run's cap stopped between two launches -- its response's `error` is
`budget-spent` -- FAILS `budget-share {share, spent}`, read before its body, never `response-unreadable`. The case
names the invariant of `team-sim-reframe.py` it replays.
- (a) retried in its run (I18): `budget: 1`, two members; l spends 0.8 of its share 0.5 -- `wake-failed
  budget-share`, then the retry resumes the SAME run with a new share and T1 is done
- (b) final (I10): under `retries: 0` the same failure is final -- `terminal`, and the escalate to the owner says
  the share
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "l": [{"sleep": 0.1, "cost": 0.8, "body": {"done": "too dear"}}, {"sleep": 0.1, "cost": 0.05, "body": {"done": "paid"}}],
        "f": [{"sleep": 0.1, "cost": 0.8, "body": {"done": "too dear"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (a) retried in its run -- I18 ---------------------------------------------------------------------
    h.declare("dear", "---\nagents: |\n  l agents/l\n  r agents/r\nreports: |\n  r -> l\nroot: l\nbudget: 1\n"
                      "schedule: off\n---\nSpend within your share.\n")
    started = h.call("team", "start", "dear", "--message", "price the DDR4", *h.harnessed)
    done = h.settled("dear", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("dear")
    fails = by_kind(found, "wake-failed", agent="l")
    runs = [one.get("run") for one in by_kind(found, "wake-intent", agent="l")]
    first = next((one.get("run") for one in by_kind(found, "wake-launched", agent="l")), None)
    if (started.returncode == 0 and done and len(fails) == 1 and fails[0].get("reason") == "budget-share"
            and fails[0].get("share") == 0.5 and fails[0].get("spent") == 0.8 and fails[0].get("final") is False
            and fails[0].get("run") == first and runs == [None, first]):
        held("(a) retried in its run", f"l spent 0.8 of its share 0.5: wake-failed budget-share, retried in its run "
             f"{first}, T1 done -- I18")
    else:
        failures.append(f"  ✗ (a) retried in its run     rc={started.returncode} done={done} fails={fails} runs={runs} "
                        f"first={first} {started.stderr.strip()[-200:]!r}")

    # --- (b) final: the escalate says the share -- I10 ------------------------------------------------------
    h.declare("last", "---\nagents: |\n  f agents/f\n  g agents/g\nreports: |\n  g -> f\nroot: f\nbudget: 1\n"
                      "retries: 0\nschedule: off\n---\nSpend within your share.\n")
    started_b = h.call("team", "start", "last", "--message", "price the DDR5", *h.harnessed)
    ended = h.settled("last", lambda found: bool(by_kind(found, "terminal", agent="f")) and all_ended(found), 60)
    found = h.events("last")
    fails = by_kind(found, "wake-failed", agent="f")
    escalate = next((one.get("text", "") for one in by_kind(found, "post", verb="escalate")), "")
    if (started_b.returncode == 0 and ended and len(fails) == 1 and fails[0].get("reason") == "budget-share"
            and fails[0].get("final") is True and "budget-share" in escalate and "share 0.5" in escalate
            and not [one for one in found if str(one.get("reason", "")).startswith("response-unreadable")]):
        held("(b) final", f"retries 0: budget-share final, terminal, the escalate says `{escalate}` -- I10")
    else:
        failures.append(f"  ✗ (b) final                  rc={started_b.returncode} ended={ended} fails={fails} "
                        f"escalate={escalate!r}")
    return 0
