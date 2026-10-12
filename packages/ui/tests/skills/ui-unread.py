"""Scenario `ui-unread` -- what a conversation of the background says (plan ui, batch le-poste-a-onglets;
cut out of `ui-tabs` by le-transcript-markdown, rule 10), on the bench's `pp-chat` witness:
- `ag3` (its witness holds 2 s before answering) gets a message, then `ctrl+right` makes `ag2` active while `ag3`
  speaks: its two answers and its verdict count as unread, bold on its title; `ctrl+left` makes it active with its
  own transcript, read again
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-unread")
    render, tabs_of = post.render, post.tabs_of

    # ag2 answered; ctrl+left -> ag3 active; a message sent to ag3, whose witness pauses 2 s before
    # answering (longer than a key's settling while a turn runs); ctrl+right at once -> ag2 active
    # while ag3 speaks: its two answers and its verdict count as unread
    unread = render("ag3", "ag2", "--render", "dialogue", "--size", "100x30",
                    "--press", "h,i,enter,wait:waiting,ctrl+left,y,o,enter,ctrl+right", "--wait", "verdict")
    text_u = unread.stdout
    bar_u = tabs_of(text_u)
    read = render("ag3", "ag2", "--render", "dialogue", "--size", "100x30",
                  "--press", "h,i,enter,wait:waiting,ctrl+left,y,o,enter,ctrl+right,wait:verdict,ctrl+left")
    text_r = read.stdout
    bar_r = tabs_of(text_r)
    if (unread.returncode == 0 and "ag3 · w00003 3" in bar_u and "two says one" in text_u and "three says" not in text_u
            and read.returncode == 0 and "ag3 · w00003 3" not in bar_r and "ag3 · w00003" in bar_r
            and "three says one" in text_r and "three says two" in text_r and "two says" not in text_r
            and "ag3 · run w00003" in text_r.rstrip("\n").split("\n")[-1]):
        held("a background tab counts its unread, read again when active", f"bar {bar_u.strip()!r} while ag2 is "
             f"active (two answers and a verdict unread); after ctrl+left {bar_r.strip()!r}, ag3's own transcript")
    else:
        failures.append(f"  ✗ unread                      rc={unread.returncode} {bar_u!r} {text_u!r} / rc={read.returncode} "
                        f"{bar_r!r} {text_r!r} {unread.stderr[-200:]!r}")
    return 0
