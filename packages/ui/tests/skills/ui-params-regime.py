"""Scenario `ui-params-regime` -- the permission regime in the overlay of a run's parameters (plan ui, batches
la-maison-et-ses-themes and la-validation-des-listes; split out of `ui-params` by rule 10), on the bench's `pp-chat`
witness:
- `n` shows the field blank: `auto`, the harness's own judgment
- the list opened by `space`, `strict` chosen, then `enter` from the list itself: the conversation opens with
  `--permissions strict` after the flags the agent last played
- `bypass` shows its help as a warning: every check skipped
- `p` on a run passes it to `bypass` and `enter` from the list sends it alone as a `set`
- `enter` on the closed list opens the conversation and unrolls nothing
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-regime")
    render = post.render

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- the permission regime: blank at birth, strict on the flags, bypass warned, set on a run --------------
    regime = "tab,tab,tab,space"                   # from the model, three fields down, the list opened
    post.clear_journal()
    born = render("--render", "dialogue", "--size", "110x45",
                  "--press", f"2,n,{regime},down,down,enter,enter,wait:waiting", "--wait", "none:1")
    opens = journal("open")
    warned = render("--render", "agents", "--size", "110x45", "--press", f"n,{regime},down,down,down,enter", *PAUSE)
    post.clear_journal()
    passed = render("ag1", "--render", "dialogue", "--size", "110x45",
                    "--press", f"h,i,enter,wait:waiting,escape,p,{regime},down,down,down,enter,enter",
                    "--wait", "policy")
    sets = journal("set")
    shown = render("--render", "agents", "--size", "110x45", "--press", "n", *PAUSE)
    if (born.returncode == 0 and opens == [f"open ag1 --provider {P.PROVIDER} --model m1 --permissions strict"]
            and warned.returncode == 0 and "bypass: every check skipped -- the agent may do anything" in warned.stdout
            and passed.returncode == 0 and sets == ['set ag1 {"permissions": "bypass"}']
            and shown.returncode == 0 and "permissions" in shown.stdout and "auto -- the harness's own judgment" in shown.stdout):
        held("the permission regime is chosen and validated from the list", f"blank at birth (auto); space opens the "
             f"list, strict then enter opens with {opens}; bypass warned; on a run, bypass then enter sends {sets}")
    else:
        failures.append(f"  ✗ regime                      opens={opens} sets={sets} warned={'every check skipped' in warned.stdout} "
                        f"{born.stdout[-500:]!r} {passed.stdout[-500:]!r} {born.stderr[-200:]!r}")

    # --- enter on the closed list: the overlay validates, no list unrolls ------------------------------------
    post.clear_journal()
    closed = render("--render", "dialogue", "--size", "110x45",
                    "--press", "2,n,tab,tab,tab,enter,wait:waiting", "--wait", "none:1")
    opens = journal("open")
    if (closed.returncode == 0 and opens == [f"open ag1 --provider {P.PROVIDER} --model m1"]
            and "auto -- the harness's own judgment" not in closed.stdout and "bypass" not in closed.stdout):
        held("enter on the closed list validates", f"the journal says {opens}; the overlay closed, no option in sight")
    else:
        failures.append(f"  ✗ closed list                 rc={closed.returncode} opens={opens} {closed.stdout[-800:]!r} "
                        f"{closed.stderr[-200:]!r}")
    return 0
