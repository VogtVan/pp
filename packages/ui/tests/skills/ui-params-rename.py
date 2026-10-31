"""Scenario `ui-params-rename` -- what `p` plays by a verb of its own, never as a `set`, on the bench's `pp-chat`
witness:
- the name of the run changed by `p` plays at once (`agent name`), no `set`, the tab saying it
- a name the verb refuses (`name-invalid`, 61 characters) goes to the remedy line, the tab unchanged
- the packages of the run (`ag1`'s run plays `plan`, `steering` and `ghost`): their line, toggled in their overlay,
  sends one `package` per line changed at the profile's `enter`, no `set`
The policy `p` sends as a `set`: `ui-params-run`.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
TO_NAME = "tab,tab,tab,tab"          # from the model, down to the name: budget, effort, permissions, name
TO_PACKAGES = "tab,tab,tab,tab"      # from the model, down to the packages of a run that plays some
SENT = "i,h,i,enter,wait:waiting,escape"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-rename")
    render, tabs_of = post.render, post.tabs_of

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- p: the name changed plays at once ------------------------------------------------------------------
    post.clear_journal()
    renamed = render("ag1", "--render", "dialogue", "--size", "110x40", "--press",
                     f"escape,p,wait:none:1.5,{TO_NAME},o,t,h,e,r,enter", *PAUSE)   # the field selects its text: typed over
    names, sets = journal("name"), journal("set")
    if renamed.returncode == 0 and names == ["name ag1 w00001 other"] and sets == [] and "other" in tabs_of(renamed.stdout):
        held("p names the run", f"the journal says {names}, no set; the tab says other")
    else:
        failures.append(f"  ✗ name by p                   {names} {sets} {tabs_of(renamed.stdout)!r} {post.journal_lines()} "
                        f"{renamed.stderr[-300:]!r}")

    # --- name-invalid on the remedy line ------------------------------------------------------------------
    long = ",".join(["a"] * 61)
    refused = render("ag1", "--render", "dialogue", "--size", "160x40", "--press",
                     f"escape,p,wait:none:1.5,{TO_NAME},{long},enter", *PAUSE)
    remedy = P.remedy_of(refused.stdout)
    if refused.returncode == 0 and "name-invalid" in remedy and "a" * 61 not in tabs_of(refused.stdout):
        held("a name the verb refuses goes to the remedy line", remedy[:100])
    else:
        failures.append(f"  ✗ name-invalid                {remedy!r} {tabs_of(refused.stdout)!r} {refused.stderr[-300:]!r}")

    # --- a run that plays packages: one `package` per line changed at the profile's enter ------------------
    post.use(P.held_script())
    post.clear_journal()
    profiled = render("ag1", "--render", "dialogue", "--size", "160x30", "--press",
                      f"{SENT},p,wait:none:1.5,{TO_PACKAGES},enter,space,enter,enter", *PAUSE)
    packages = journal("package")
    if profiled.returncode == 0 and packages == [P.switched("ag1", "plan", False)] and journal("set") == []:
        held("p sends the packages changed", f"{packages}; no set")
    else:
        failures.append(f"  ✗ p packages                  rc={profiled.returncode} {post.journal_lines()} "
                        f"{profiled.stdout[-1200:]!r} {profiled.stderr[-300:]!r}")
    return 0
