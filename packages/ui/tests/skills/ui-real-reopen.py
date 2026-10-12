"""Scenario `ui-real-reopen` -- the post's memory on the REAL verb (plan ui, batch
le-reel-du-poste-recadre): two conversations with one agent are two runs; the post keeps both in the
space `ui` of the house's metadata, and `./pp ui` with no agent named opens both again, each with its
history read from the records.
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-reopen")

    two = post.render(R.AGENT, R.AGENT, "--render", "dialogue", "--size", "160x40", "--press",
                      "h,i,enter,wait:waiting,ctrl+left,y,o,enter", "--wait", R.EXCHANGE)
    kept = post.remembered()
    runs = sorted(one["run"] for one in post.status_json())
    pairs = sorted((str(one[0]), str(one[1])) if isinstance(one, (list, tuple)) else (str(one.get("agent")), str(one.get("run")))
                   for one in kept)
    if two.returncode == 0 and len(runs) == 2 and [run for _, run in pairs] == runs and {a for a, _ in pairs} == {R.AGENT}:
        held("two conversations are two runs, both kept", f"the metadata's space ui keeps {pairs}")
    else:
        failures.append(f"  ✗ real memory                 rc={two.returncode} kept={kept} runs={runs} {two.stdout!r} {two.stderr[-300:]!r}")

    again = post.render("--render", "dialogue", "--size", "160x40", keep=True)
    bar = R.P.Post.tabs_of(again.stdout)
    if again.returncode == 0 and all(run in bar for run in runs) and "history #1" in again.stdout:
        held("./pp ui with no agent opens both again", f"the bar {bar.strip()!r}; the active tab replays history #1")
    else:
        failures.append(f"  ✗ real reopen                 {again.stdout!r} {again.stderr[-300:]!r}")
    return 0
