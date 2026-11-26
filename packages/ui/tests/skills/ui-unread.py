"""Scenario `ui-unread` -- what a conversation of the background says (plan ui, batch le-poste-a-onglets;
cut out of `ui-tabs` by le-transcript-markdown, rule 10), on the bench's `pp-chat` witness:
- `ag3` (its witness holds 2 s before answering) gets a message and `ctrl+right` in one burst, neither key settled
  before the other: `ag2` is active before `ag3` speaks, whatever the machine's load; its two answers and its verdict
  count as unread, bold on its title; `ctrl+left` makes it active with its own transcript, read again
- the conversations of the start opened on a row of tabs that handles its own activation late (the bench's
  `witness/_row-of-tabs`, 0.4 s, what a loaded machine does): the last one named is active all the same, and a message
  goes to it (batch les-rouges-ui-sous-charge)
- the row of tabs closed while the conversations of the start are adopted (`witness/_row-of-tabs`, its pump closed at
  the second tab): the post does not freeze, it ends within `BOUND` seconds, rc 0 -- no tab activated on a row
  that is going: the active tab stays the row's own, ag3, never ag2 the last named, and no message leaves
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

from tests.harness import support

P = support(__file__, "dialogue")
ROW_OF_TABS = Path(__file__).resolve().parents[1] / "witness" / "_row-of-tabs"
BOUND = 20.0                     # seconds a render of a closed row may take before the post is said frozen


def bounded(post, env: dict, *args: str):
    """`./pp ui …` as `post.render` plays it, `BOUND` seconds at most: None when the post froze -- its process group
    killed, its witnesses with it."""
    P.forget(post.made)
    child = subprocess.Popen([sys.executable, str(post.engine), "ui", *args], cwd=post.ws, text=True,
                             env={**os.environ, **post.env, **env}, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True)
    try:
        out, err = child.communicate(timeout=BOUND)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        child.communicate()
        return None
    return P.rendered(subprocess.CompletedProcess(child.args, child.returncode, out, err))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-unread")
    render, tabs_of = post.render, post.tabs_of

    # ag2 answered; ctrl+left -> ag3 active; a message sent to ag3, whose witness pauses 2 s before answering,
    # and ctrl+right back to back with the enter that sends it (`burst:`): ag2 is active before ag3 speaks,
    # however long a key takes to settle -- its two answers and its verdict count as unread
    unread = render("ag3", "ag2", "--render", "dialogue", "--size", "100x30",
                    "--press", "i,h,i,ctrl+enter,wait:waiting,ctrl+left,i,y,o,burst:ctrl+enter:ctrl+right", "--wait", "verdict")
    text_u = unread.stdout
    bar_u = tabs_of(text_u)
    read = render("ag3", "ag2", "--render", "dialogue", "--size", "100x30",
                  "--press", "i,h,i,ctrl+enter,wait:waiting,ctrl+left,i,y,o,burst:ctrl+enter:ctrl+right,wait:verdict,ctrl+left")
    text_r = read.stdout
    bar_r = tabs_of(text_r)
    if (unread.returncode == 0 and "ag3 · w00003 3" in bar_u and "two says one" in text_u and "three says" not in text_u
            and read.returncode == 0 and "ag3 · w00003 3" not in bar_r and "ag3 · w00003" in bar_r
            and "three says one" in text_r and "three says two" in text_r and "two says" not in text_r
            and "ag3" in P.status_of(text_r) and "w00003" in P.status_of(text_r)):
        held("a background tab counts its unread, read again when active", f"bar {bar_u.strip()!r} while ag2 is "
             f"active (two answers and a verdict unread); after ctrl+left {bar_r.strip()!r}, ag3's own transcript")
    else:
        failures.append(f"  ✗ unread                      rc={unread.returncode} {bar_u!r} {text_u!r} / rc={read.returncode} "
                        f"{bar_r!r} {text_r!r} {unread.stderr[-200:]!r}")

    # the row of tabs handles its own activation of the first tab 0.4 s late: ag2, the last named, is active and
    # takes the message
    plain = post.env
    post.env = {**plain, "PYTHONPATH": str(ROW_OF_TABS), "PP_UI_SLOW_TABS": "0.4"}
    post.clear_journal()
    slow = render("ag3", "ag2", "--render", "dialogue", "--size", "100x30", "--press", "i,h,i,ctrl+enter", "--wait", "waiting")
    said = [one for one in post.journal_lines() if one.startswith("message ")]
    if slow.returncode == 0 and said == ["message ag2 hi"] and "ag2" in P.status_of(slow.stdout):
        held("the last conversation named is active on a slow row of tabs", f"{said}; status "
             f"{P.status_of(slow.stdout).strip()[:40]!r}")
    else:
        failures.append(f"  ✗ slow row of tabs            rc={slow.returncode} {said} {P.status_of(slow.stdout)!r} "
                        f"{slow.stderr[-300:]!r}")

    # the row of tabs closed at the second tab, while the conversations of the start are adopted: no freeze
    post.env = plain
    post.clear_journal()
    closed = bounded(post, {"PYTHONPATH": str(ROW_OF_TABS), "PP_UI_CLOSED_ROW": "1"},
                     "ag3", "ag2", "--render", "dialogue", "--size", "100x30")
    sent = [one for one in post.journal_lines() if one.startswith("message ")]
    active = P.status_of(closed.stdout).split("·")[1].strip() if closed is not None and "·" in P.status_of(
        closed.stdout) else ""
    if closed is not None and closed.returncode == 0 and active == "ag3" and not sent:
        held("a row of tabs closed during the adoption freezes nothing", f"the post rendered within {BOUND:.0f} s, "
             f"rc 0, nothing activated: the row's own tab {active!r} active, not ag2; no message sent")
    elif closed is None:
        failures.append(f"  ✗ closed row of tabs           the post froze: no end in {BOUND:.0f} s")
    else:
        failures.append(f"  ✗ closed row of tabs           rc={closed.returncode} active={active!r} (ag3 expected, "
                        f"the row's own) sent={sent} {closed.stderr[-300:]!r}")
    return 0
