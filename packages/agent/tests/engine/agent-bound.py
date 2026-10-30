"""Scenario `agent-bound` -- 2 case(s) (plan moteur-0.2.0, phase le-moteur-et-le-kit, batch le-refus-qui-gare,
2026-10-28): the launcher at the REPAIR BOUND of a run it conducts, under the witness harness in its `stubborn`
mode (a bare `fail` at every proof) and the agent's TURN under a law of production:
- the bound parks the run: `agent run` plays the launches up to the bound (the boot's WORK, then one per
  proof: the first and three repairs), the witness's last call is refused `repair-exhausted`, and the house
  STOPS by itself -- no marked call after the refusal (the trace says one `stopped`, one `refusal`, no
  `advance` after them), the verdict says `parked`, rc 0, `status --json` says the run parked; nothing of
  the house reads the mark (the exchange count of the verdict reads the passage, not the mark: phase B)
- the principal's word takes the step up: `--run <key> --message …` under the plain witness serves the
  step with its DEVIATION and the message under `the principal's word` in the first prompt of the resume,
  the trace says `taken-up`, the mark is gone, the proof then lets the passage end -- exchange 1, parked,
  one launch (the AWAIT after the proof is served, launched on nothing)
"""
from __future__ import annotations

import json

from conductor import persistence
from conductor.core import language
from tests.harness import support

A = support(__file__, "agent")
WORD = "look at the bench again"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    h.lawful()

    # --- the bound parks the run, the house stops by itself -----------------------------------------
    woken = h.wake("first ask", "stubborn", "--json")
    keys = h.keys()
    key = keys[0] if keys else ""
    report = A.report_of(woken) if woken.stdout.strip() else {}
    trace = h.trace(key) if key else []
    kinds = [one.get("kind") for one in trace]
    stopped_at = kinds.index("stopped") if "stopped" in kinds else -1
    after = kinds[stopped_at + 1:] if stopped_at >= 0 else kinds
    calls = h.calls()
    last_call = calls[-1] if calls else {}
    slot = persistence.slot_of(h.agent_meta, key) if key else None
    mark = persistence.stopped_of(slot) if slot else {}
    if (woken.returncode == 0 and key and report.get("launches") == 5 and f"run {key}" in woken.stderr
            and " · parked · " in woken.stderr and h.face(key).get("state") == "parked"
            and kinds.count("stopped") == 1 and kinds.count("refusal") == 1 and "advance" not in after
            and last_call.get("rc") == 2 and "repair-exhausted" in last_call.get("err", "")
            and mark.get("repairs") == 3 and persistence.awaits(slot) == persistence.MESSAGE):
        held("the bound parks the run, the house stops by itself", f"run {key}: 5 launches, the witness's last call "
             "refused repair-exhausted, one `stopped` and one `refusal` traced and no advance after them, the "
             "verdict parked, rc 0, status parked, the mark at the slot with 3 repairs")
    else:
        failures.append(f"  ✗ the bound                   rc={woken.returncode} launches={report.get('launches')} "
                        f"after={after} last={last_call.get('rc')} {last_call.get('err', '')[-80:]!r} mark={mark} "
                        f"face={h.face(key).get('state')} {woken.stderr[-300:]!r}")

    # --- the principal's word takes the step up ------------------------------------------------------
    launches_before = report.get("launches") or 0
    resumed = h.wake(WORD, "play", "--run", key, "--json") if key else None
    again = A.report_of(resumed) if resumed is not None and resumed.stdout.strip() else {}
    session = h.read(".session") if key else ""
    first_prompt = h.read(f".prompt.{session}.{launches_before + 1}") if session else ""
    trace = h.trace(key) if key else []
    kinds = [one.get("kind") for one in trace]
    if (resumed is not None and resumed.returncode == 0 and f"run {key} · exchange 1 · parked" in resumed.stderr
            and "DEVIATION" in first_prompt and language.WORD in first_prompt and WORD in first_prompt
            and "REPAIR" not in first_prompt.split("\n")[0]
            and kinds.count("taken-up") == 1 and not persistence.stopped_of(slot)
            and h.face(key).get("exchanges") == 1 and again.get("launches") == 1):
        held("the principal's word takes the step up", f"`--run {key} --message` serves the step with its DEVIATION "
             "and the word as a reading, `taken-up` traced, the mark gone; the plain witness proves, the passage "
             "ends: exchange 1, parked, 1 launch (the AWAIT served, launched on nothing)")
    else:
        failures.append(f"  ✗ the take-up                 rc={resumed and resumed.returncode} "
                        f"deviation={'DEVIATION' in first_prompt} word={language.WORD in first_prompt} "
                        f"taken={kinds.count('taken-up')} mark={persistence.stopped_of(slot) if slot else None} "
                        f"face={h.face(key)} launches={again.get('launches')} {(resumed.stderr[-300:] if resumed else '')!r}")
    return 0
