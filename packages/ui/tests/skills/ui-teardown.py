"""Scenario `ui-teardown` -- the post leaves cleanly while a flow still speaks (plan ui, batch la-course-du-statut),
on the bench's `pp-chat` witness: a flow that keeps saying `waiting` every few milliseconds, the post rendered and
left in the middle of it, three times -- every render exits 0 with its capture; no `NoMatches` on stderr (the footer
gone while an event or a tick still writes the status line)."""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
RENDERS = 3


def chatty_script() -> dict:
    """ag1 opens, then says `waiting` every 2 ms for about four seconds -- events still arriving as the post leaves."""
    flow = P.script("w00001", "the agent says")
    flow["opening"] = flow["opening"] + [one for _ in range(2000) for one in ({"sleep": 0.002}, {"kind": "waiting"})]
    return {"agents": {"ag1": flow}, "faces": P.FACES}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-teardown", chatty_script())
    renders = [post.render("ag1", "--render", "dialogue", "--size", "100x30", "--wait", "none:0.3")
               for _ in range(RENDERS)]
    broken = [one for one in renders if one.returncode != 0 or "NoMatches" in one.stderr or "ag1" not in one.stdout]
    if not broken:
        held("the post leaves while the flow speaks", f"{RENDERS} renders left mid-flow: rc 0, the capture whole, "
             "no NoMatches")
    else:
        failures.append(f"  ✗ teardown                    {len(broken)}/{RENDERS} broken: rc={broken[0].returncode} "
                        f"{broken[0].stderr[-1500:]!r}")
    return 0
