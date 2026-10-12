"""Scenario `ui-params` -- the parameters of a run in ONE overlay (plan ui, batch l-overlay-du-run), on the
bench's `pp-chat` witness and its faces (`ag1` last played the fixture's provider and `{model: m1}`;
`providers --json` names two models of it):
- `n` on the Agents tab opens the overlay prefilled with what the agent last played: the fixture's provider, model m1,
  the models of `providers --json` in the help, read once as it opens; its keys say enter opens and space
  lists
- `enter` opens the conversation with the flags filled in after those of `--`: the journal says
  `open ag1 --harness x --provider <the fixture's> --model m2`; the status says what the run plays
- `p` before any message opens it prefilled with the policy `ready` said
- `p` on a conversation opens the same overlay, the provider fixed; a changed effort is sent alone as a `set`,
  the `policy` the witness answers reaches the status; `p` then `escape` sends nothing
The name of a run is `ui-params-name`'s.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params")
    render = post.render

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- n: the overlay, prefilled with what the agent last played -------------------------------------
    post.clear_journal()
    shown = render("--render", "agents", "--size", "110x40", "--press", "n", *PAUSE)
    text = shown.stdout
    if (shown.returncode == 0 and "a new run of ag1" in text and P.PROVIDER in text and "m1" in text
            and P.MODELS[0] in text and "provider" in text and "budget" in text and "effort" in text
            and "[enter] opens · [space] lists · [escape] cancels" in text and journal("providers") == ["providers --json"]):
        held("n opens the overlay prefilled", f"provider {P.PROVIDER}, model m1, the models of providers --json in the help "
             "(read once); provider, model, budget and effort on one screen; enter opens")
    else:
        failures.append(f"  ✗ overlay                     rc={shown.returncode} {post.journal_lines()} {text!r} {shown.stderr[-300:]!r}")

    # --- enter: the flags filled in, after those of `--` ---------------------------------------------
    post.clear_journal()
    opened = render("--render", "dialogue", "--size", "110x40", "--press", "2,n,m,2,enter,wait:waiting,h,i,enter",
                    "--wait", "waiting", "--", "--harness", "x")
    status = opened.stdout.rstrip("\n").split("\n")[-1]
    if (opened.returncode == 0 and journal("open") == [f"open ag1 --harness x --provider {P.PROVIDER} --model m2"]
            and "ag1 · run w00001" in status and f"{P.PROVIDER} · m1 · — · —" in status):
        held("enter opens the run with the flags", f"the journal says {journal('open')}; the status says "
             f"{P.PROVIDER} · m1 · — · — (what the witness's opened plays)")
    else:
        failures.append(f"  ✗ open                        rc={opened.returncode} {post.journal_lines()} {status!r} {opened.stderr[-300:]!r}")

    # --- p before any message: the overlay prefilled with the policy `ready` said -------------------------
    early = render("ag1", "--render", "dialogue", "--size", "110x40", "--press", "escape,p", *PAUSE)
    if (early.returncode == 0 and "provider fixed" in early.stdout and "the provider's default" not in early.stdout
            and "m1" in early.stdout):
        held("p before any message is prefilled", "the overlay opens on the model m1 that ready said, no placeholder")
    else:
        failures.append(f"  ✗ p early                     rc={early.returncode} {early.stdout!r} {early.stderr[-300:]!r}")

    # --- p: the provider fixed, a changed effort sent alone, the policy on the status; escape sends nothing
    post.clear_journal()
    fixed = render("ag1", "--render", "dialogue", "--size", "110x40", "--press", "h,i,enter,wait:waiting,escape,p", *PAUSE)
    post.clear_journal()
    changed = render("ag1", "--render", "dialogue", "--size", "110x40",
                     "--press", "h,i,enter,wait:waiting,escape,p,tab,tab,h,i,g,h,enter", "--wait", "policy")
    sets = journal("set")
    status = changed.stdout.rstrip("\n").split("\n")[-1]
    post.clear_journal()
    cancelled = render("ag1", "--render", "dialogue", "--size", "110x40",
                       "--press", "h,i,enter,wait:waiting,escape,p,escape", *PAUSE)
    if (fixed.returncode == 0 and "provider fixed" in fixed.stdout and "fixed for the run" in fixed.stdout
            and "[enter] sets · [space] lists" in fixed.stdout and changed.returncode == 0
            and sets == ['set ag1 {"effort": "high"}'] and f"{P.PROVIDER} · m1 · — · high" in status
            and cancelled.returncode == 0 and journal("set") == []):
        held("p sets what changed, escape sends nothing", f"the overlay with the provider fixed; the journal says "
             f"{sets}; the status says {P.PROVIDER} · m1 · — · high; p then escape: no set")
    else:
        failures.append(f"  ✗ p                           {fixed.stdout!r} / {sets} {status!r} / {post.journal_lines()} "
                        f"{changed.stderr[-300:]!r}")

    return 0
