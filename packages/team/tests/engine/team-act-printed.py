"""Scenario `team-act-printed` -- 1 case: an act a member HANDS to pp by its print call is routed once. A team of
one root whose turn asks its work as a production said to the principal (a contributor stands behind it); the
witness prints the root's answer to the task's opening -- the call and its result streamed as a tool's -- and its
last message says nothing more:
- the flow of the launch carries the act as ONE `words`, its text what the witness handed, byte for byte; the
  team's journal carries one `wake-routed` of the launch, at that line of the flow, one answer posted, and the
  task done on the text the act gave
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")
SAID = "handed by the print call"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"pr": [{"sleep": 0.1, "body": {"re": "DO", "text": SAID}}]})
    h.speaks("agents/pr")
    h.declare("printed", "---\nagents: |\n  pr agents/pr\nroot: pr\nschedule: off\n---\nSay it to pp.\n")
    started = h.call("team", "start", "printed", "--message", "answer by a print", *h.harnessed)
    done = h.settled("printed", lambda found: bool(T.by_kind(found, "done", task="T1")) and T.all_ended(found),
                     timeout=25)
    found = h.events("printed")
    tag = next((one.get("tag") for one in T.intents_on(found, "pr", "T1")), None)
    routed = T.by_kind(found, "wake-routed", tag=tag)
    run = next((one.get("run") for one in T.by_kind(found, "wake-launched", tag=tag)), None)
    flow = T.lines(T.flow_file(h, "agents/pr", str(run))) if run else []
    handed = [one.get("text") for one in T.lines(h.out / "pr.printed")]
    acts = [one.get("text") for one in flow if one.get("kind") == "words" and one.get("text") in handed]
    at = int(routed[0].get("line") or 0) if routed else 0
    line = flow[at - 1] if 0 < at <= len(flow) else {}
    answers = T.by_kind(found, "post", verb="re", **{"from": "pr"})
    if (started.returncode == 0 and done and len(handed) == 1 and acts == handed and len(routed) == 1
            and line.get("kind") == "words" and line.get("text") == handed[0] and len(answers) == 1
            and T.result_of(found, "T1") == SAID):
        held("an act handed by its print call is routed once", f"run {run}: the witness printed its answer, the flow "
             f"carries it as one words, byte for byte; one wake-routed at line {at}, one answer posted, T1 done on "
             "its text")
    else:
        failures.append(f"  ✗ an act printed              rc={started.returncode} done={done} handed={handed!r} "
                        f"acts={acts!r} routed={[(one.get('line'), one.get('words')) for one in routed]} "
                        f"line={json.dumps(line)[:160]} answers={len(answers)} result={T.result_of(found, 'T1')!r} "
                        f"words={[one.get('text') for one in flow if one.get('kind') == 'words']!r} "
                        f"{started.stderr.strip()[-200:]!r}")
    return 0
