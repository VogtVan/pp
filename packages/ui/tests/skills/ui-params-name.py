"""Scenario `ui-params-name` -- the NAME of a run in the overlay of its parameters (plan ui, batch
le-pied-et-les-overlays; cut from `ui-params`, rule 10), on the bench's `pp-chat` witness:
- the name is the overlay's last field, under the profile; typed at `n`, the tab says it at once and `agent name` plays once the flow's
  `opened` says the key -- after the first message, never before
The name changed by `p` is `ui-params-rename`'s.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
TO_NAME = "tab,tab,tab,tab,tab"      # from the model, down to the name: budget, effort, permissions, packages, name


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-name")
    render, tabs_of = post.render, post.tabs_of

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- the name of the run: at n, played once opened says the key ---------------------------------------
    post.clear_journal()
    before = render("--render", "dialogue", "--size", "110x40", "--press",
                    f"2,n,wait:none:1.5,{TO_NAME},d,e,m,o,enter,wait:waiting", *PAUSE)
    named_early = journal("name")
    post.clear_journal()
    after = render("--render", "dialogue", "--size", "110x40", "--press",
                   f"2,n,wait:none:1.5,{TO_NAME},d,e,m,o,enter,wait:waiting,h,i,enter,wait:waiting", *PAUSE)
    order = [one.split(" ")[0] for one in post.journal_lines() if one.split(" ")[0] in ("open", "message", "name")]
    if (before.returncode == 0 and "demo" in tabs_of(before.stdout) and named_early == []
            and after.returncode == 0 and journal("name") == ["name ag1 w00001 demo"]
            and order == ["open", "message", "name"]):
        held("the name typed at n plays once the run is opened", f"the tab says demo before any message, no name "
             f"played; then the journal says {order}")
    else:
        failures.append(f"  ✗ name at n                   {tabs_of(before.stdout)!r} {named_early} {post.journal_lines()} "
                        f"{after.stderr[-300:]!r}")

    return 0
