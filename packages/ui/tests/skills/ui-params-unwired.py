"""Scenario `ui-params-unwired` -- the parameters of a new run on a house wired with no provider (plan ui,
batch l-overlay-du-run, its rework): the witness's faces say no provider and a `last` played by a caller's
command (`harness`), as on a house whose agents run under `--harness` alone:
- `n` on the Agents tab opens the overlay with no provider chosen, its help saying the house is wired with none
- `enter` opens the conversation with the flags of `--` alone: no `--provider` is composed
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    faces = {**P.FACES, "providers": [],
             "status": {"ag1": [dict(P.FACES["status"]["ag1"][0]),
                                {"agent": "ag1", "providers": [], "last": {"provider": "harness", "policy": {}}}]}}
    post = P.Post(bench, "ui-params-unwired", {"agents": {"ag1": P.script("w00001", "the agent says")}, "faces": faces})

    shown = post.render("--render", "agents", "--size", "110x40", "--press", "n", *PAUSE)
    opened = post.render("--render", "dialogue", "--size", "110x40", "--press", "2,n,enter,wait:waiting",
                         "--wait", "none:0.5", "--", "--harness", "x")
    opens = [one for one in post.journal_lines() if one.startswith("open ")]
    if (shown.returncode == 0 and "a new run of ag1" in shown.stdout and "wired with no provider" in shown.stdout
            and opened.returncode == 0 and opens == ["open ag1 --harness x"]):
        held("n on a house wired with no provider", f"no provider chosen, the help says so; enter: the journal says {opens}")
    else:
        failures.append(f"  ✗ unwired                     rc={shown.returncode} {shown.stdout[-400:]!r} "
                        f"{shown.stderr[-300:]!r} / {opens}")
    return 0
