"""Scenario `ui-tabs` -- the tabs of the post of conversations (plan ui, batch le-poste-a-onglets),
on the bench's `pp-chat` witness replaying one scripted flow per agent:
- two agents: a tab each, the last opened active (the unread of a background tab is `ui-unread`'s)
- ten switches between two tabs: the witness was launched exactly twice (KD4)
- `x` closes the active tab and the witness gets `quit`; `n` goes to the Agents tab, where `n` opens a conversation with the agent under the cursor; `p` names the run of a tab (the name is the last field of its parameters); no `r` nor `ctrl+t` among the keys
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-tabs")
    render, tabs_of = post.render, post.tabs_of

    # --- two agents: a tab each, the last one active --------------------------------------------------
    two = render("ag1", "ag2", "--render", "dialogue", "--size", "100x30", "--press", "i,h,i,enter", "--wait", "waiting")
    text_2 = two.stdout
    bar_2 = tabs_of(text_2)
    status_2 = text_2.rstrip("\n").split("\n")[-1]
    if (two.returncode == 0 and "ag1 · w00001" in bar_2 and "ag2 · w00002" in bar_2 and "two says one" in text_2
            and "the agent says" not in text_2 and "ag2" in status_2 and "w00002" in status_2):
        held("two agents open two tabs, the last one active", f"bar {bar_2.strip()!r}; ag2's transcript, ag2 in the status")
    else:
        failures.append(f"  ✗ two tabs                    rc={two.returncode} {text_2!r} {two.stderr[-300:]!r}")

    # --- ten switches: exactly two launches (KD4) ----------------------------------------------------
    post.clear_journal()
    switched = render("ag1", "ag2", "--render", "dialogue", "--size", "100x30",
                      "--press", ",".join(["ctrl+left", "ctrl+right"] * 5))
    opens = [one for one in post.journal_lines() if one.startswith("open ")]
    if switched.returncode == 0 and opens == ["open ag1", "open ag2"] and "ag2 · w00002" in tabs_of(switched.stdout):
        held("switching tabs launches nothing", f"ten switches, the journal says {opens}")
    else:
        failures.append(f"  ✗ launches                    rc={switched.returncode} {post.journal_lines()} {tabs_of(switched.stdout)!r}")

    # --- x closes the active tab (quit to its verb), n through the Agents tab, p names ------------------
    post.clear_journal()
    closed = render("ag1", "ag2", "--render", "dialogue", "--size", "100x30", "--press", "escape,x")
    bar_x = tabs_of(closed.stdout)
    quits = [one for one in post.journal_lines() if one.startswith("quit ")]
    if closed.returncode == 0 and "ag1 · w00001" in bar_x and "ag2" not in bar_x and quits[:1] == ["quit ag2"]:
        held("x closes the active tab", f"bar {bar_x.strip()!r}; the journal says {quits} (ag2 first, at x; ag1 at the end)")
    else:
        failures.append(f"  ✗ x                           rc={closed.returncode} {bar_x!r} {post.journal_lines()} {closed.stderr[-200:]!r}")
    opened = render("ag1", "--render", "dialogue", "--size", "100x30",
                    "--press", "escape,n,down,n,enter", "--wait", "waiting")
    bar_n = tabs_of(opened.stdout)
    status_n = P.status_of(opened.stdout)
    if opened.returncode == 0 and "ag1 · w00001" in bar_n and "ag2 · w00002" in bar_n and "ag2" in status_n and "w00002" in status_n:
        held("n opens a conversation through the Agents tab", f"n, the cursor on ag2, n: bar {bar_n.strip()!r}")
    else:
        failures.append(f"  ✗ n                           rc={opened.returncode} {bar_n!r} {opened.stdout!r} {opened.stderr[-200:]!r}")
    post.clear_journal()
    renamed = render("ag1", "--render", "dialogue", "--size", "100x30", "--press",
                     "escape,p,wait:none:1.5,tab,tab,tab,tab,d,e,m,o,enter", "--wait", "none:1.5")
    bar_r2 = tabs_of(renamed.stdout)
    keys = P.keys_of(renamed.stdout)
    named = [one for one in post.journal_lines() if one.startswith("name ")]
    if (renamed.returncode == 0 and "demo" in bar_r2 and "ag1 · w00001" not in bar_r2
            and named == ["name ag1 w00001 demo"] and "^t" not in keys and "[r]" not in keys):
        held("p names the run of the tab", f"the journal says {named}; bar {bar_r2.strip()!r}; no r nor ctrl+t in "
             "the keys")
    else:
        failures.append(f"  ✗ p names                     rc={renamed.returncode} {bar_r2!r} {post.journal_lines()} {keys!r} {renamed.stderr[-200:]!r}")
    return 0
