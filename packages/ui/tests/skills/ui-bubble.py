"""Scenario `ui-bubble` -- the BUBBLE of a conversation's tab: one line on top of the transcript saying the
principal's message of the turn at the top of the view (plan ui, batch la-zone-du-chat), on the bench's `pp-chat`
witness:
- three turns, each answer taller than the screen: at the end of the transcript the bubble says the third message;
  `home` on the transcript, the first; `end`, the third again
- scrolling lays out nothing but the bubble: the count of the transcript's layouts (`--press … layouts`) is the
  same before and after `home`
- a run taken up from the Agents tab says the last turn of its history: `history #2` and its message
- under `pp off` the bubble and the `pp OFF` banner both show, in looks of their own (`--styles`)
- the words of the agent in markdown (a table, a block of code) are ONE widget under the head of their block
  (`--press … nodes`)
- the application losing the terminal's focus leaves no widget focused and its focus off; taking it back gives the
  focus to the message line again (`--press … blur,focus`)
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")

SIZE = ("--size", "120x30")
TURNS = "i," + ",".join(["h,i,enter,wait:waiting"] * 3)   # i: to the line once, it stays there


def bubble_of(text: str) -> str:
    """-> the bubble's row of a capture: the principal's glyph, then on the same row the hour or `history #n`, then
    the message -- the transcript's own heads carry the message on the row under them; '' when none."""
    return next((row.strip() for row in text.split("\n")
                 if re.match(r"\s*▶ (\d\d:\d\d:\d\d|history #\d+)\S* +\S", P.SGR.sub("", row))), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-bubble", P.turns_script())
    render = post.render

    # --- the turn at the top of the view: the third at the end, the first after home, the third after end --------
    end = render("ag1", "--render", "dialogue", *SIZE, "--press", TURNS)
    home = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURNS},shift+tab,layouts,home,layouts")
    back = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURNS},shift+tab,home,end")
    said = [bubble_of(one.stdout) for one in (end, home, back)]
    if (all(one.returncode == 0 for one in (end, home, back)) and P.QUESTIONS[2] in said[0]
            and P.QUESTIONS[0] in said[1] and P.QUESTIONS[2] in said[2]):
        held("the bubble says the turn at the top of the view", f"at the end {said[0]!r}; after home {said[1]!r}; "
             f"after end {said[2]!r}")
    else:
        failures.append(f"  ✗ bubble                      {said} rc={[one.returncode for one in (end, home, back)]} "
                        f"{home.stdout[-1500:]!r} {home.stderr[-300:]!r}")

    # --- scrolling lays out nothing of the transcript ---------------------------------------------------------
    counted = re.search(r"^layouts (\d+) (\d+)$", home.stdout, re.M)
    if counted and counted.group(1) == counted.group(2) and int(counted.group(1)) > 0:
        held("scrolling lays out nothing of the transcript", f"the transcript's layouts before and after home: "
             f"{counted.group(1)} and {counted.group(2)}")
    else:
        failures.append(f"  ✗ layouts                     {counted.group(0) if counted else None!r} {home.stdout[-400:]!r}")

    # --- a run taken up: the turn of its history ----------------------------------------------------------------
    taken = render("--render", "dialogue", *SIZE, "--press", "2,enter,enter", "--wait", "waiting")
    said_h = bubble_of(taken.stdout)
    if taken.returncode == 0 and "history #2" in said_h and "and again" in said_h:
        held("a turn of history says its number", said_h)
    else:
        failures.append(f"  ✗ history                     {said_h!r} {taken.stdout!r} {taken.stderr[-300:]!r}")

    # --- under pp off: the bubble and the banner, each its own look --------------------------------------------
    post.use(P.conduct_script())
    paused = post.render(
        "ag1", "--render", "dialogue", *SIZE, "--styles", "--press", "i,h,i,enter,wait:waiting,escape,o",
        "--wait", "conduct")
    plain = P.ANSI.sub("", paused.stdout)
    banner, bubble = P.styles_of(paused.stdout, r"pp OFF"), P.styles_of(paused.stdout, r"▶ \d\d:\d\d:\d\d +hi\b")
    if paused.returncode == 0 and "pp OFF" in plain and bubble_of(plain) and banner and bubble and banner != bubble:
        held("the bubble is told apart from the pp OFF banner", f"{bubble_of(plain)!r} under the banner, their styles "
             f"{sorted(bubble)} and {sorted(banner)}")
    else:
        failures.append(f"  ✗ banner                      {sorted(bubble)} {sorted(banner)} {plain[:1200]!r} "
                        f"{paused.stderr[-300:]!r}")

    # --- the words in markdown, one widget; the application's focus lost, then taken back -----------------------
    post.use(P.markdown_script())
    worded = post.render("ag1", "--render", "dialogue", *SIZE, "--press", "i,h,i,enter,wait:waiting,nodes,blur,focus")
    nodes = re.search(r"^nodes (\d+)$", worded.stdout, re.M)
    if worded.returncode == 0 and nodes and int(nodes.group(1)) == 2:
        held("the words in markdown are one widget", f"the block of the agent's words: its head and its text, "
             f"{nodes.group(1)} widgets")
    else:
        failures.append(f"  ✗ nodes                       {nodes.group(0) if nodes else None!r} {worded.stdout[-600:]!r} "
                        f"{worded.stderr[-300:]!r}")
    focused = re.search(r"^focused (\S+) (\S+)$", worded.stdout, re.M)
    if worded.returncode == 0 and focused and focused.groups() == ("none:0", "message:1"):
        held("the application's focus lost, then taken back", "blur: no widget focused, its focus off; focus: the "
             "message line focused again, its focus on")
    else:
        failures.append(f"  ✗ focus                       {focused.group(0) if focused else None!r} "
                        f"{worded.stdout[-400:]!r}")
    return 0
