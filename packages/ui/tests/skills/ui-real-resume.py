"""Scenario `ui-real-resume` -- a run taken up from the Agents tab on the REAL verb (plan ui, batch
le-reel-du-poste-recadre), a real run of two exchanges made first at the post:
- `enter` on the agent, then on its run in the overlay, resumes the run in a tab: its history replayed from
  the records (`history #1`, `#2`), then a third message makes a third line of `responses.jsonl` on the
  same run, `agent status --json` at three exchanges
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-resume")
    made = post.talk()
    runs = post.status_json()
    if made.returncode != 0 or len(runs) != 1 or len(post.responses()) != 2:
        failures.append(f"  ✗ real run                    rc={made.returncode} runs={runs} {made.stderr[-300:]!r}")
        return 0

    resumed = post.render("--render", "dialogue", "--size", "120x60", "--press", "2,down,enter,enter,wait:waiting,h,e,y,enter",
                          "--wait", R.EXCHANGE)
    text = resumed.stdout
    third, runs_3 = post.responses(), post.status_json()
    if (resumed.returncode == 0 and "history #1" in text and "history #2" in text and "✓ parked" in text
            and len(third) == 3 and len({one["run"] for one in third}) == 1 and len(runs_3) == 1
            and runs_3[0]["exchanges"] == 3):
        held("enter resumes the real run with its history", "history #1 and #2 replayed, then a third exchange: "
             "responses.jsonl 3 lines on one run, status --json at 3 exchanges")
    else:
        failures.append(f"  ✗ real resume                 {text!r} responses={len(third)} runs={runs_3} {resumed.stderr[-300:]!r}")
    return 0
