"""Scenario `ui-agents` -- the AGENTS tab of the post (plan ui, batch le-poste-sans-hub), on the
bench's `pp-chat` witness replaying the faces of `agent`:
- the table of the agents: one line per agent (its runs, the state of its last run, its sums, the hour of its last event), read from `agent list --json` and one `agent status --json` per agent; the status says the count and the hour of the reading
- `enter` on an agent opens the overlay of its runs (name, run, exchanges, state, cost, launches, last hour)
- `enter` on a run resumes it in a tab of the dialogue: its history replayed dim first, then the live flow; the witness got `exchanges` then `chat --run`
- `s` in the overlay stacks the statistics of the run over it: `ui-run-stats`
- the overlay of the runs shows pp's share and the context of each run, `~xx %` (the tokens without a window), `—`
  without a flow
- `n` on an agent opens a new conversation with it in a tab of the dialogue; `u` reads the faces again
- `a` asks the path of a new agent in an overlay, the exact command `./pp agent add <path>` under the line, following
  what is typed; `enter` plays `agent add <path>`, the table read again carries the new agent; a path the verb refuses
  (`agent-exists`) goes to the remedy line, the table unchanged
- the width of the overlay and the house heading the table: `ui-agents-overlay`
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-agents")
    render, tabs_of = post.render, post.tabs_of

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- the table of the agents ----------------------------------------------------------------
    post.clear_journal()
    shown = render("--render", "agents", "--size", "120x30")
    text = shown.stdout
    lines = text.rstrip("\n").split("\n")
    if (shown.returncode == 0 and "ag1" in text and "ag2" in text and "standing" in text and "0.35" in text
            and re.search(r"\b2\b\D+\b3\b", lines[-1]) and P.entry_of(text, "enter") and P.entry_of(text, "n")
            and journal("list") == ["list --json"] and journal("status") == ["status ag1 --json", "status ag2 --json"]):
        held("the Agents tab lists the agents", "ag1 (2 runs, its last standing, 0.35 USD) and ag2; the status counts "
             "2 agents and 3 runs; the journal says one list and one status per agent")
    else:
        failures.append(f"  ✗ table                       rc={shown.returncode} {text!r} {post.journal_lines()} {shown.stderr[-300:]!r}")

    # --- enter on an agent: the overlay of its runs ------------------------------------------------
    runs = render("--render", "dialogue", "--size", "120x30", "--press", "2,enter")
    text_o = runs.stdout
    row_1 = next((line for line in text_o.split("\n") if "w00001" in line), "")
    row_9 = next((line for line in text_o.split("\n") if "w00009" in line), "")
    title_o = P.title_of(text_o)
    if (runs.returncode == 0 and title_o[:1] and "ag1" in title_o[0] and "w00001" in text_o and "w00009" in text_o
            and "w00002" not in text_o and "[enter]" in text_o and "[esc]" in text_o
            and "~33%" in row_1 and "~17%" in row_1
            and "~98%" in row_9 and "~6.8k" in row_9):
        held("enter opens the overlay of the agent's runs", "ag1's two runs, w00001 and w00009, its own keys; "
             "pp and ctx: ~33% / ~17% of the window, ~98% / ~6.8k tokens without one")
    else:
        failures.append(f"  ✗ runs overlay                rc={runs.returncode} {text_o!r} {runs.stderr[-300:]!r}")

    # --- enter on a run: resumed with its history in a tab of the dialogue ---------------------------
    post.clear_journal()
    resumed = render("--render", "dialogue", "--size", "120x30", "--press", "2,enter,enter", "--wait", "waiting")
    text_r = resumed.stdout
    bar = tabs_of(text_r)
    asked = [one["message"] for one in P.FACES["exchanges"]["ag1"]["w00001"]]
    status_r = P.status_of(text_r)
    if (resumed.returncode == 0 and "ag1 · w00001" in bar and all(one in text_r for one in asked)
            and re.search(r"0\.19\D+3\b", text_r) and not P.heads_of(text_r)
            and "ag1" in status_r and "w00001" in status_r
            and journal("exchanges") == ["exchanges ag1 w00001 --json"] and journal("open") == ["open ag1 --run w00001"]):
        held("enter on a run resumes it with its history", f"bar {bar.strip()!r}; its two exchanges in history, no turn lived; "
             "the journal says exchanges then chat --run w00001")
    else:
        failures.append(f"  ✗ resume                      rc={resumed.returncode} {bar!r} {text_r!r} {post.journal_lines()} {resumed.stderr[-300:]!r}")

    # --- n on an agent: the overlay of its parameters, enter opens with what it last played; u reads again
    post.clear_journal()
    fresh = render("--render", "dialogue", "--size", "120x30", "--press", "2,n,enter", "--wait", "waiting")
    bar_f = tabs_of(fresh.stdout)
    opens = journal("open")
    post.clear_journal()
    reread = render("--render", "agents", "--size", "120x30", "--press", "u", "--wait", "waiting:1")
    lists = journal("list")
    if (fresh.returncode == 0 and "ag1 · w00001" in bar_f and opens == [f"open ag1 --provider {P.PROVIDER} --model m1"]
            and reread.returncode == 0 and len(lists) == 2):
        held("n opens a new conversation, u reads again", f"bar {bar_f.strip()!r}, the journal says {opens}; "
             f"u: {len(lists)} readings")
    else:
        failures.append(f"  ✗ new and reread              rc={fresh.returncode} {bar_f!r} {opens} / lists={lists} "
                        f"{fresh.stderr[-200:]!r}")

    # --- a: an agent born from the post; a path refused --------------------------------------------------
    asked = render("--render", "agents", "--size", "110x30", "--press", "a,a,g,3")
    post.clear_journal()
    born = render("--render", "agents", "--size", "110x30", "--press", "a,a,g,4,enter", "--wait", "none:1.5")
    added = journal("add ")
    refused = render("--render", "agents", "--size", "110x30", "--press", "a,a,g,1,enter", "--wait", "none:1.5")
    if (asked.returncode == 0 and P.title_of(asked.stdout) and "./pp agent add ag3" in asked.stdout
            and born.returncode == 0 and added == ["add ag4"] and "ag4" in born.stdout
            and refused.returncode == 0 and "agent-exists" in P.remedy_of(refused.stdout) and "ag4" in refused.stdout):
        held("a gives birth to an agent", "the preview `./pp agent add ag3` follows the line; enter plays add ag4, "
             "the table carries it; ag1 refused agent-exists on the remedy line")
    else:
        failures.append(f"  ✗ add                         {asked.stdout!r} / {added} {born.stdout!r} / {P.remedy_of(refused.stdout)!r}")
    return 0
