"""Scenario `ui-params-rename` -- the NAME of a run changed in the overlay of its parameters (plan ui, batch
le-pied-et-les-overlays; cut from `ui-params-name`, rule 10), on the bench's `pp-chat` witness:
- changed by `p`, it plays at once, no `set`; `p` then `enter` with nothing changed plays nothing
- a name the verb refuses (`name-invalid`, 61 characters) goes to the remedy line
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
TO_NAME = "tab,tab,tab,tab"          # from the model, down to the name: budget, effort, permissions, name


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-rename")
    render, tabs_of = post.render, post.tabs_of

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- p: the name changed plays at once; nothing changed, nothing played -------------------------------
    post.clear_journal()
    renamed = render("ag1", "--render", "dialogue", "--size", "110x40", "--press",
                     f"escape,p,wait:none:1.5,{TO_NAME},o,t,h,e,r,enter", *PAUSE)   # the field selects its text: typed over
    names, sets = journal("name"), journal("set")
    post.clear_journal()
    still = render("ag1", "--render", "dialogue", "--size", "110x40", "--press", "escape,p,wait:none:1.5,enter", *PAUSE)
    if (renamed.returncode == 0 and names == ["name ag1 w00001 other"] and sets == [] and "other" in tabs_of(renamed.stdout)
            and still.returncode == 0 and journal("name") == [] and journal("set") == []):
        held("p names the run, an empty name plays nothing", f"the journal says {names}, no set; the tab says other; "
             "p then enter: nothing played")
    else:
        failures.append(f"  ✗ name by p                   {names} {sets} {tabs_of(renamed.stdout)!r} {post.journal_lines()} "
                        f"{renamed.stderr[-300:]!r}")

    # --- name-invalid on the remedy line ------------------------------------------------------------------
    long = ",".join(["a"] * 61)
    refused = render("ag1", "--render", "dialogue", "--size", "160x40", "--press",
                     f"escape,p,wait:none:1.5,{TO_NAME},{long},enter", *PAUSE)
    remedy = refused.stdout.rstrip("\n").split("\n")[-2]
    if refused.returncode == 0 and "name-invalid" in remedy and "a" * 61 not in tabs_of(refused.stdout):
        held("a name the verb refuses goes to the remedy line", remedy.strip()[:100])
    else:
        failures.append(f"  ✗ name-invalid                {remedy!r} {tabs_of(refused.stdout)!r} {refused.stderr[-300:]!r}")
    return 0
