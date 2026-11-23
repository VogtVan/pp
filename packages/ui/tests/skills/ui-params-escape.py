"""Scenario `ui-params-escape` -- `escape` on `p`, the overlay of a running run's parameters (batch
l-echap-qui-garde-la-saisie), cut out of `ui-params-run` by case (rule 10), on the bench's `pp-chat` witness:
- the effort typed, `escape` asks first: `escape` there gives the profile back, `high` still typed, and `ctrl+enter`
  sends it as one `set`
- `p` then `escape` closes the profile as it opened, `p` then `ctrl+enter` with nothing changed sends nothing; the
  effort typed, `escape` then `ctrl+enter` in the confirmation closes it, nothing sent
"""
from __future__ import annotations

import json

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "110x45")
TURN = "i,h,i,ctrl+enter,wait:waiting,escape"   # a message sent, the line left
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
EFFORT = "p,wait:none:1.5,tab,tab,h,i,g,h"      # the overlay, its effort typed


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-escape")
    render = post.render

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- escape, escape: the profile back as typed, then sent ---------------------------------------------------
    post.clear_journal()
    back = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},{EFFORT},escape,escape,ctrl+enter", *PAUSE)
    sets = [json.loads(one.split(" ", 2)[2]) for one in journal("set")]
    if back.returncode == 0 and sets == [{"effort": "high"}]:
        held("escape in the confirmation gives the profile back", f"the effort kept: set ag1 {sets[0]}")
    else:
        failures.append(f"  ✗ back                        {post.journal_lines()} {back.stderr[-300:]!r}")

    # --- escape, ctrl+enter on the profile as it opened: nothing sent; typed, escape then ctrl+enter: left ------
    post.clear_journal()
    left = render("ag1", "--render", "dialogue", *SIZE, "--press",
                  f"{TURN},p,escape,p,ctrl+enter,{EFFORT},escape,ctrl+enter", *PAUSE)
    if (left.returncode == 0 and journal("set") == [] and journal("name") == [] and journal("package") == []
            and not P.title_of(left.stdout)):
        held("escape closes a profile as it opened, ctrl+enter leaves one typed", "p, escape: closed; p, ctrl+enter: "
             "nothing changed, nothing sent; the effort typed, escape, ctrl+enter: no set, the overlay gone")
    else:
        failures.append(f"  ✗ left                        {post.journal_lines()} {P.title_of(left.stdout)} "
                        f"{left.stderr[-300:]!r}")
    return 0
