"""Scenario `ui-real-conduct` -- the suspension of the conduction and the packages of a run from the post, on the
REAL verb and the witness harness of `agent`:
- after `o`, the next message launches the witness ONCE with a prompt that carries the message and no line of
  pp's output; the last line of `responses.jsonl` says `conducted: false`, the transcript the verdict `agent flow
  --json` keeps for it; the footer's `[o]` entry is not the one of a conducted run
- `k` lists the packages the run plays (the house's, borrowed); `space` on the first one then `enter` asks its
  switch, which the verb plays at once or holds until the next launch (`pending`); after the next message its
  trace says `switch` once, the transcript says the package off and no `⧗` is left on the tab
"""
from __future__ import annotations

import json

from conductor.core.model import Block
from tests.harness import cli, support

R = support(__file__, "real")
P = R.P                               # the footer's keys, read on any number of lines
YES, WAITS = (P.palette_constant(name) for name in ("YES", "WAITS"))


def verdicts(post, key: str) -> list[str]:
    """-> the states of the verdicts the run's flow kept, in order (`agent flow --json`)."""
    played = cli(post.engine, "agent", "flow", R.AGENT, key, "--json", cwd=post.ws)
    return [one["state"] for one in (json.loads(line) for line in played.stdout.splitlines() if line.strip())
            if one.get("kind") == "verdict"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-conduct")

    # --- o: the next message is bare -------------------------------------------------------------------
    before = post.launches()
    bare = post.render(R.AGENT, "--render", "dialogue", "--size", "160x50", "--press",
                       "i,h,i,enter,wait:waiting,escape,o,wait:conduct,i,y,o,enter", "--wait", R.EXCHANGE)
    prompt, responses = post.prompt(), post.responses()
    launched = post.launches() - before
    runs = post.status_json()
    states = verdicts(post, runs[0]["run"]) if runs else []
    of_pp = [line for line in prompt.splitlines() if line.startswith(Block.MARK)]

    # --- k: the run's packages, the first one switched off --------------------------------------------
    switched = post.render(R.AGENT, "--render", "dialogue", "--size", "160x50", "--press",
                           "i,h,i,enter,wait:waiting,escape,k,space,enter,wait:package,i,y,o,enter", "--wait", R.EXCHANGE)
    off, on = P.entry_of(bare.stdout, "o"), P.entry_of(switched.stdout, "o")
    if (bare.returncode == 0 and "yo" in prompt and not of_pp and responses and responses[-1].get("conducted") is False
            and launched == 2 and len(states) == 2 and states[1] != states[0] and f"{YES} {states[1]}" in bare.stdout
            and off and on and off != on):
        held("o makes the next exchange bare", f"the witness launched {launched} times (1 conducted, 1 bare); the last "
             f"prompt carries yo and no line of pp; responses.jsonl says conducted false; the verdicts {states}; the "
             f"footer {off!r}, conducted {on!r}")
    else:
        failures.append(f"  ✗ real bare                   launched={launched} prompt={prompt[:200]!r} states={states} "
                        f"o={off!r}/{on!r} last={responses[-1:]} {bare.stdout!r} {bare.stderr[-300:]!r}")

    runs = post.status_json()
    keys = sorted(one["run"] for one in runs)
    trace = [step for run in keys for step in post.trace(run) if step.get("kind") == "switch"]
    name = str(trace[0].get("package", "")) if trace else ""
    if (switched.returncode == 0 and len(trace) == 1 and name and f"{name} off" in switched.stdout
            and WAITS not in P.Post.tabs_of(switched.stdout)):
        held("k switches a package of the real run", f"the trace says switch {name} once; the transcript says {name} off; "
             f"no {WAITS} after the next message")
    else:
        failures.append(f"  ✗ real package                switches={trace} {switched.stdout!r} {switched.stderr[-300:]!r}")
    return 0
