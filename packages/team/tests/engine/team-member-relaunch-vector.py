"""Scenario `team-member-relaunch-vector` -- 3 case(s): a member's run taken up again with its VECTORS, on the house of
`_relaunch.py` -- mi's run stood launches-spent, the tick took it up and it parked:
- (a) the standing run taken up (s.1550): the tick's second launch on mi's run opens with both vectors and mounts
  them -- no `refused` in the run's flow before its park
- (b) an address refused before the message: the parked run relaunched with `plan:ghost/ph/bt` refuses
  `vector-refused`, `path-unknown` in the detail, the run as it was -- its exchanges, the messages on record
- (d) a mount refused once the message opened the exchange (A2): the parked run relaunched with its own run's vector,
  `agent-run:./<key>` -- its family's verifier, `pp-agent`, accepts it before the message, and the block of the
  exchange the message opens does not offer `pp-agent`: rc 2, `vector-refused`, `offer-absent`; the message on
  record at `messages.jsonl`, the `refused` event in the run's flow, the refusal saying the run stands on the
  exchange that message opened, `agent status --json` saying the run standing, never `dead`
Its sibling: `team-member-relaunch-vector-parked` (the parked run relaunched, cut from this one).
"""
from __future__ import annotations

import json

from tests.harness import support

L = support(__file__, "relaunch")
NODE, GHOST, MEMBER = L.NODE, L.GHOST, L.MEMBER


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    r = L.Relaunched(bench)
    started, posted, settled, key = r.started, r.posted, r.settled, r.key
    flow, relaunch, turns = r.flow, r.relaunch, r.turns
    messages = lambda: len(r.messages())

    # --- (a) the standing run taken up -- s.1550 -----------------------------------------------------------------
    before = flow()
    opened = [one for one in before if one.get("kind") == "opened"]
    verdicts = [one.get("state") for one in before if one.get("kind") == "verdict"]
    if (started.returncode == 0 and posted.returncode == 0 and settled and key and verdicts == ["standing", "parked"]
            and [one.get("vectors") for one in opened] == [[NODE, MEMBER], [NODE, MEMBER]]
            and not any(one.get("kind") == "refused" for one in before)):
        held("(a) the standing run taken up", f"mi's run {key} stood launches-spent, the tick's second launch opened "
             "with the node and the member's vector, mounted both, parked -- no refused (s.1550)")
    else:
        failures.append(f"  ✗ (a) the standing run        rc={started.returncode}/{posted.returncode} settled={settled} "
                        f"key={key!r} verdicts={verdicts} opened={[one.get('vectors') for one in opened]} "
                        f"refused={[one.get('detail') for one in before if one.get('kind') == 'refused']}")

    # --- (b) an address refused before the message -----------------------------------------------------------
    turns_b, messages_b = turns(), messages()
    ghost = relaunch(GHOST, MEMBER)
    last = (ghost.stderr.strip().splitlines() or [""])[-1]
    if (ghost.returncode == 2 and last.startswith("pp-agent: vector-refused -- ") and "path-unknown" in last
            and turns() == turns_b and messages() == messages_b):
        held("(b) an address refused before the message", f"{GHOST}: vector-refused, path-unknown in the detail; "
             f"run {key} kept its {turns_b} exchange(s), no message recorded")
    else:
        failures.append(f"  ✗ (b) an address refused      rc={ghost.returncode} last={last[-200:]!r} "
                        f"turns={turns_b}/{turns()} messages={messages_b}/{messages()}")

    # --- (d) a mount refused after the message: the message on record, the run standing -- A2 -----------------
    own = f"agent-run:./{key}"                             # verified by pp-agent, which no block of TURN offers
    said = relaunch(own, message="own run")
    last = (said.stderr.strip().splitlines() or [""])[-1]
    recorded = [one for one in r.messages() if one.get("run") == key and one.get("message") == "own run"]
    refused = [one for one in flow() if one.get("kind") == "refused" and "offer-absent" in str(one.get("detail"))]
    faces = [json.loads(line) for line in r.h.call("agent", "status", "agents/mi", "--json").stdout.splitlines()
             if line.startswith("{")]
    state = next((one.get("state") for one in faces if one.get("run") == key), None)
    if (said.returncode == 2 and last.startswith(f"pp-agent: vector-refused -- {own}: offer-absent")
            and "stands on the exchange" in last and len(recorded) == 1 and len(refused) == 1
            and state not in (None, "dead")):
        held("(d) a mount refused after the message", f"{own} refused offer-absent at its mount: the message on "
             f"record, the refused event in the flow, the run {state} -- {last[-80:]!r}")
    else:
        failures.append(f"  ✗ (d) refused after the message rc={said.returncode} last={last[-260:]!r} "
                        f"recorded={len(recorded)} refused={len(refused)} state={state}")
    return 0
