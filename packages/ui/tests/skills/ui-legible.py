"""Scenario `ui-legible` -- a post read at a glance (plan ui, batch le-poste-lisible), on the bench's `pp-chat` witness:
- a table whose rows open on 🛠️ (`U+FE0F` after it) and 🚀: no `U+FE0F` in the capture, the `│` of both rows at the
  same columns
- `o`: the banner `pp OFF` heads the conversation's tab and the message line says `pp off`; `o` again: both gone
- `escape`, `s` on a conversation: the statistics of its run stacked -- the same overlay as the Agents tab's, ctx
  and pp's share included --, `stats ag1 w00001 --json` in the journal (once for the gauge after the verdict, once
  for `s`); the footer at rest says `[s] stats` and
  nothing of a stop (the stop is `ui-stop`'s)
"""
from __future__ import annotations

import unicodedata

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "160x30")
SENT = "h,i,enter,wait:waiting,escape"
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the face


def columns(text: str) -> int:
    """-> the columns a terminal gives `text`: none to a combining mark (`U+FE0F`), two to a wide character."""
    return sum(0 if unicodedata.category(ch) == "Mn" else 2 if unicodedata.east_asian_width(ch) in "WF" else 1
               for ch in text)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the table aligned, no U+FE0F ---------------------------------------------------------------
    table = P.Post(bench, "ui-legible-table", P.emoji_script()).render(
        "ag1", "--render", "dialogue", *SIZE, "--press", "h,i,enter", "--wait", "waiting")
    rows = [row for row in table.stdout.split("\n") if "build" in row or "ship" in row]
    bars = [[columns(row[:n]) for n, ch in enumerate(row) if ch in "│┃"] for row in rows]
    if (table.returncode == 0 and "️" not in table.stdout and len(rows) == 2 and bars[0] and bars[0] == bars[1]):
        held("the table's rows align", f"no U+FE0F in the capture; the bars of both rows at columns {bars[0]}")
    else:
        failures.append(f"  ✗ table                       rc={table.returncode} fe0f={chr(0xfe0f) in table.stdout} "
                        f"rows={rows} bars={bars} {table.stderr[-300:]!r}")

    # --- pp off seen in the tab, gone at pp on --------------------------------------------------------
    post = P.Post(bench, "ui-legible-conduct", P.conduct_script())
    off = post.render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},o", "--wait", "conduct")
    on = post.render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},o,wait:conduct,o", "--wait", "conduct")
    if (off.returncode == 0 and "pp OFF" in off.stdout and "pp off -- the message goes to the agent bare" in off.stdout
            and on.returncode == 0 and "pp OFF" not in on.stdout and "the message goes to the agent bare" not in on.stdout):
        held("pp off is seen in the tab", "after o the banner `pp OFF` and the message line `pp off …`; after o again, neither")
    else:
        failures.append(f"  ✗ pp off                      rc={off.returncode}/{on.returncode} {off.stdout!r} / {on.stdout!r}")

    # --- s on a conversation: its run's statistics; the footer --------------------------------------------
    chat = P.Post(bench, "ui-legible-stats")
    chat.clear_journal()
    stats = chat.render("ag1", "--render", "dialogue", "--size", "160x50", "--press", f"{SENT},s", *PAUSE)
    said = [one for one in chat.journal_lines() if one.startswith("stats ")]
    footer = chat.render("ag1", "--render", "dialogue", *SIZE, "--press", SENT)
    if (stats.returncode == 0 and "blocks      9" in stats.stdout and said == ["stats ag1 w00001 --json"] * 2
            and "context     ~17% of 1M tokens" in stats.stdout and "pp          ~33% of the flow" in stats.stdout
            and footer.returncode == 0 and "stop the turn" not in footer.stdout and "[s] stats" in footer.stdout):
        held("s shows the run's statistics from its tab", f"the journal says {said}; blocks 9 in the overlay; "
             "the footer at rest says [s] stats and nothing of a stop")
    else:
        failures.append(f"  ✗ s                           rc={stats.returncode}/{footer.returncode} {chat.journal_lines()} "
                        f"{stats.stdout!r} / {footer.stdout[-600:]!r} {stats.stderr[-300:]!r}")
    return 0
