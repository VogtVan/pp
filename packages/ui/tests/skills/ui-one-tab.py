"""Scenario `ui-one-tab` -- one run, one tab (plan ui, batch l-onglet-unique-par-run), on the bench's `pp-chat`
witness replaying the faces of `agent`:
- a run resumed twice from the Agents tab gives one tab and one opening, its history read once
- a run whose tab ended (the verb refused) resumed again is taken up IN PLACE -- one tab, its first refusal still in
  its transcript, then the second; two openings, no second `exchanges`
- `n` twice opens two tabs: a new run is never taken for another
"""
from __future__ import annotations

import copy

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-one-tab")
    render, tabs_of = post.render, post.tabs_of

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- one run, one tab: resumed twice, one tab and one opening -----------------------------------------
    post.clear_journal()
    again = render("--render", "dialogue", "--size", "120x30", "--press", "2,enter,enter,escape,2,enter,enter",
                   "--wait", "waiting")
    bar_a = tabs_of(again.stdout)
    if (again.returncode == 0 and len([one for one in bar_a.split("  ") if one.strip()]) == 1
            and journal("open") == ["open ag1 --run w00001"] and journal("exchanges") == ["exchanges ag1 w00001 --json"]):
        held("a run resumed twice is one tab", f"bar {bar_a.strip()!r}; one opening, one history read")
    else:
        failures.append(f"  ✗ resumed twice               rc={again.returncode} {bar_a!r} {post.journal_lines()} {again.stderr[-300:]!r}")

    # --- a tab that ended, resumed again: taken up in place --------------------------------------------
    refused = copy.deepcopy(P.SCRIPT)
    refused["agents"]["ag1"] = P.refusing("pp-agent: run-busy -- a wake-up plays run w00001")
    busy = P.Post(bench, "ui-one-tab-ended", refused)
    busy.clear_journal()
    ended = busy.render("--render", "dialogue", "--size", "120x30", "--press", "2,enter,enter,escape,2,enter,enter",
                        "--wait", "ended:2")
    bar_e = tabs_of(ended.stdout)
    opens_e = [one for one in busy.journal_lines() if one.startswith("open ")]
    reads_e = [one for one in busy.journal_lines() if one.startswith("exchanges ")]
    if (ended.returncode == 0 and bar_e.count("ag1 · w00001") == 1 and ended.stdout.count("a wake-up plays run w00001") >= 2
            and opens_e == ["open ag1 --run w00001", "open ag1 --run w00001"] and reads_e == ["exchanges ag1 w00001 --json"]):
        held("an ended tab is taken up in place", f"bar {bar_e.strip()!r}; the first refusal still in the transcript, then the "
             "second; two openings, one history read")
    else:
        failures.append(f"  ✗ ended in place              rc={ended.returncode} {bar_e!r} {busy.journal_lines()} "
                        f"{ended.stdout[-900:]!r} {ended.stderr[-300:]!r}")

    # --- n twice: two new runs, two tabs ----------------------------------------------------------------
    post.clear_journal()
    news = render("--render", "dialogue", "--size", "120x30", "--press", "2,n,enter,escape,2,n,enter", "--wait", "waiting:2")
    bar_n = tabs_of(news.stdout)
    if news.returncode == 0 and bar_n.count("ag1 · w00001") == 2 and len(journal("open")) == 2:
        held("n twice opens two tabs", f"bar {bar_n.strip()!r}; two openings")
    else:
        failures.append(f"  ✗ n twice                     rc={news.returncode} {bar_n!r} {post.journal_lines()} {news.stderr[-300:]!r}")
    return 0
