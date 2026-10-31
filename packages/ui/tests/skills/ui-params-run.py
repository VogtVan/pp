"""Scenario `ui-params-run` -- `p`, the overlay of a running run's parameters, on the bench's `pp-chat` witness
(`ready` and `opened` say the policy `{model: m1}`):
- `p` before any message opens the overlay prefilled with the policy `ready` said: model m1, no example in its place
- `p` on a conversation sends what changed alone, as ONE `set`: the effort typed and the regime chosen from its list
  (`bypass`), the `policy` the witness answers reaching the status; `p` then `escape`, and `p` then `enter` with
  nothing changed, send nothing
- at 80x24, `tab` from the model reaches the last field: `permissions` and the overlay's keys in sight
The name and the packages `p` plays by their own verbs: `ui-params-rename`.
"""
from __future__ import annotations

import json

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "110x45")
TURN = "i,h,i,enter,wait:waiting,escape"   # a message sent, the line left
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face


def firsts(text: str) -> list[str]:
    """-> the first word of every row of the overlay: a field's title, or its value before its arrow."""
    return [row.split()[0] for row in P.overlay_rows(text) if row.split()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-run")
    render = post.render

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- p before any message: the overlay prefilled with the policy `ready` said -------------------------
    early = render("ag1", "--render", "dialogue", *SIZE, "--press", "escape,p", *PAUSE)
    if early.returncode == 0 and "m1" in firsts(early.stdout):
        held("p before any message is prefilled", "the model field holds m1, the policy ready said")
    else:
        failures.append(f"  ✗ p early                     rc={early.returncode} {early.stdout!r} {early.stderr[-300:]!r}")

    # --- p: the effort typed and bypass chosen, sent as one set; the policy on the status ------------------
    post.clear_journal()
    changed = render("ag1", "--render", "dialogue", *SIZE, "--press",
                     f"{TURN},p,wait:none:1.5,tab,tab,h,i,g,h,tab,space,down,down,down,enter,enter", *PAUSE)
    sets = [json.loads(one.split(" ", 2)[2]) for one in journal("set")]
    status = P.status_of(changed.stdout)
    if changed.returncode == 0 and sets == [{"effort": "high", "permissions": "bypass"}] and "· high" in status:
        held("p sends what changed as one set", f"the journal says set ag1 {sets[0]}; the status says the effort high")
    else:
        failures.append(f"  ✗ p set                       {post.journal_lines()} {status!r} {changed.stdout[-1500:]!r} "
                        f"{changed.stderr[-300:]!r}")

    # --- p then escape, p then enter with nothing changed: nothing sent -----------------------------------
    post.clear_journal()
    still = render("ag1", "--render", "dialogue", *SIZE, "--press",
                   f"{TURN},p,escape,p,enter", *PAUSE)
    if still.returncode == 0 and journal("set") == [] and journal("name") == [] and journal("package") == []:
        held("nothing changed, nothing sent", "p then escape, p then enter: no set, no name, no package")
    else:
        failures.append(f"  ✗ still                       {post.journal_lines()} {still.stderr[-300:]!r}")

    # --- at 80x24: the last field and the overlay's keys in sight ------------------------------------------
    small = render("ag1", "--render", "dialogue", "--size", "80x24", "--press",
                   f"{TURN},p,wait:none:1.5,tab,tab,tab", *PAUSE)
    rows = P.overlay_rows(small.stdout)
    if (small.returncode == 0 and P.field_title("permissions") in firsts(small.stdout)
            and any(row.startswith("[enter]") for row in rows)):
        held("the parameters reach their last field at 80x24", "Permissions and the overlay's keys in sight")
    else:
        failures.append(f"  ✗ params 80x24                rc={small.returncode} {small.stdout!r} {small.stderr[-300:]!r}")
    return 0
