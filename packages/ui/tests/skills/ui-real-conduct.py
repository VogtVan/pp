"""Scenario `ui-real-conduct` -- the suspension of the conduction from the post, on the REAL verb
(plan ui, batch le-reel-du-poste-recadre) and the witness harness of `agent`:
- after `o`, the next message launches the witness ONCE with a prompt that carries the message and
  nothing of pp; the last line of `responses.jsonl` says `conducted: false`; the footer says `pp off`
- `o` again: the next message is conducted again -- the witness's prompt opens on pp's output
- `k` lists the packages the run plays (the house's, borrowed); `space` on the first one then `enter` asks its
  switch, which the verb plays at once or holds until the next launch (`pending`); after the next message its
  trace says `switch` once, the transcript says the package off and no `⧗` is left on the tab
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real")
P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines
PP = "▌ pp · run "


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-conduct")

    # --- o: the next message is bare -------------------------------------------------------------------
    before = post.launches()
    bare = post.render(R.AGENT, "--render", "dialogue", "--size", "160x50", "--press",
                       "h,i,enter,wait:waiting,escape,o,wait:conduct,i,y,o,enter", "--wait", R.EXCHANGE)
    lines = bare.stdout.rstrip("\n").split("\n")
    prompt, responses = post.prompt(), post.responses()
    launched = post.launches() - before
    if (bare.returncode == 0 and "yo" in prompt and PP not in prompt
            and responses and responses[-1].get("conducted") is False and launched == 3
            and "[o] pp: off" in P.keys_of(bare.stdout) and "unconducted" in bare.stdout):
        held("o makes the next exchange bare", f"the witness launched {launched} times (2 conducted, 1 bare); the last "
             "prompt carries yo and no line of pp; responses.jsonl says conducted false; the footer [o] pp: off")
    else:
        failures.append(f"  ✗ real bare                   launched={launched} prompt={prompt[:200]!r} "
                        f"last={responses[-1:]} {bare.stdout!r} {bare.stderr[-300:]!r}")

    # --- o again: conducted again ----------------------------------------------------------------------
    back = post.render(R.AGENT, "--render", "dialogue", "--size", "160x50", "--press",
                       "h,i,enter,wait:waiting,escape,o,wait:conduct,o,wait:conduct,i,y,o,enter", "--wait", R.EXCHANGE)
    prompt_b = post.prompt()
    if back.returncode == 0 and PP in prompt_b and post.responses()[-1].get("conducted") is not False:
        held("o again brings the conduction back", "the next prompt opens on pp's output; the record line is conducted")
    else:
        failures.append(f"  ✗ real back                   prompt={prompt_b[:200]!r} last={post.responses()[-1:]} "
                        f"{back.stderr[-300:]!r}")

    # --- k: the run's packages, the first one switched off --------------------------------------------
    switched = post.render(R.AGENT, "--render", "dialogue", "--size", "160x50", "--press",
                           "h,i,enter,wait:waiting,escape,k,space,enter,wait:package,i,y,o,enter", "--wait", R.EXCHANGE)
    runs = post.status_json()
    key = runs[-1]["run"] if runs else ""
    keys = sorted(one["run"] for one in runs)
    trace = [step for run in keys for step in post.trace(run) if step.get("kind") == "switch"]
    name = str(trace[0].get("package", "")) if trace else ""
    if (switched.returncode == 0 and len(trace) == 1 and name and f"{name} off" in switched.stdout
            and "⧗" not in (switched.stdout.split("\n") + [""] * 4)[3]):       # the row of the conversations' tabs
        held("k switches a package of the real run", f"the trace says switch {name} once; the transcript says {name} off; "
             "no ⧗ after the next message")
    else:
        failures.append(f"  ✗ real package                key={key} switches={trace} {switched.stdout!r} {switched.stderr[-300:]!r}")
    return 0
