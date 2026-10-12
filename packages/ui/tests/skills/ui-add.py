"""Scenario `ui-add` -- an agent born from the post (plan ui, batch l-overlay-du-run), on the bench's `pp-chat`
witness and its faces:
- `a` on the Agents tab asks the path in an overlay, the exact command `./pp agent add <path>` under the line,
  following what is typed
- `enter` plays `agent add <path>`: the journal says it, the table read again carries the new agent
- a path the verb refuses (`agent-exists`) goes to the remedy line as the verb said it, the table unchanged
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the verb and the reading


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-add")
    render = post.render

    asked = render("--render", "agents", "--size", "110x30", "--press", "a,a,g,3")
    post.clear_journal()
    born = render("--render", "agents", "--size", "110x30", "--press", "a,a,g,4,enter", *PAUSE)
    added = [one for one in post.journal_lines() if one.startswith("add ")]
    refused = render("--render", "agents", "--size", "110x30", "--press", "a,a,g,1,enter", *PAUSE)
    lines = refused.stdout.rstrip("\n").split("\n")
    if (asked.returncode == 0 and "path of the new agent" in asked.stdout and "./pp agent add ag3" in asked.stdout
            and born.returncode == 0 and added == ["add ag4"] and "ag4" in born.stdout
            and refused.returncode == 0 and "pp-agent: agent-exists" in lines[-2] and "ag4" in refused.stdout):
        held("a gives birth to an agent", "the preview `./pp agent add ag3` follows the line; enter plays add ag4, "
             "the table carries it; ag1 refused agent-exists on the remedy line")
    else:
        failures.append(f"  ✗ add                         {asked.stdout!r} / {added} {born.stdout!r} / {lines[-3:]}")
    return 0
