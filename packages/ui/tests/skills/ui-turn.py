"""Scenario `ui-turn` -- the turn under way, seen in a conversation's tab (plan ui, batch le-tour-en-cours),
on the bench's `pp-chat` witness: `ag3`'s script holds the flow 2 s after the principal's line.
- while the turn runs, a spinner glyph on the tab's title and at the head of the status; what is typed meanwhile stays in the message line and `enter` sends nothing -- the footer says `enter: waits`, the witness's journal has the first message alone
- once the turn ended, `enter` sends the line: the journal has both messages, in order
- at rest, no glyph anywhere and the footer says `enter: send`
- the glyph is drawn bold in the theme's accent and the duration of the turn follows it, on the status and the
  tab's title (`--styles`; batch le-pied-et-les-overlays)
The stop button is `ui-stop`'s.
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"                # the glyphs of a turn under way, as the palette turns them


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-turn")
    render, tabs_of = post.render, post.tabs_of

    # --- during the turn: the glyph, the line kept, enter waiting for the end of the turn -------------
    def spinning(line: str) -> bool:
        return any(glyph in line for glyph in SPINNER)

    def messages() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("message ")]

    post.clear_journal()
    during = render("ag3", "--render", "dialogue", "--size", "100x30", "--press", "h,i,enter,wait:principal,y,o,enter")
    text_d = during.stdout
    lines_d = text_d.rstrip("\n").split("\n")
    sent_d = messages()
    if (during.returncode == 0 and spinning(tabs_of(text_d)) and "ag3 · w00003" in tabs_of(text_d)
            and lines_d[-1].strip()[:1] in SPINNER and any(one.count("│") >= 2 and one.split("│")[1].strip() == "yo" for one in lines_d)
            and "[enter] waits" in P.keys_of(text_d) and sent_d == ["message ag3 hi"] and len(P.heads_of(text_d)) == 1):
        held("the turn under way is seen, the line kept", f"the bar {tabs_of(text_d).strip()!r}, the status opens on "
             f"{lines_d[-1].strip()[:1]!r}; `yo` typed during the turn stays in the line, the journal says {sent_d}; "
             "the footer says enter: waits")
    else:
        failures.append(f"  ✗ turn under way              rc={during.returncode} {sent_d} {text_d!r} {during.stderr[-300:]!r}")
    post.clear_journal()
    after = render("ag3", "--render", "dialogue", "--size", "100x34",
                   "--press", "h,i,enter,wait:principal,y,o,wait:waiting,enter", "--wait", "principal")
    sent_a = messages()
    if after.returncode == 0 and sent_a == ["message ag3 hi", "message ag3 yo"] and len(P.heads_of(after.stdout)) == 2:
        held("enter sends the line once the turn ended", f"the journal says {sent_a}, in this order; two ▶ in the transcript")
    else:
        failures.append(f"  ✗ sent after the turn        rc={after.returncode} {sent_a} {after.stdout!r} {after.stderr[-300:]!r}")
    rest = render("ag3", "--render", "dialogue", "--size", "100x30", "--press", "h,i,enter", "--wait", "waiting")
    text_rest = rest.stdout
    if (rest.returncode == 0 and "✓ parked" in text_rest and not spinning(text_rest)
            and "[enter] send" in P.keys_of(text_rest)):
        held("no glyph at rest", "after waiting: the verdict parked, no glyph anywhere, the footer says enter: send")
    else:
        failures.append(f"  ✗ at rest                     rc={rest.returncode} {text_rest!r} {rest.stderr[-300:]!r}")

    # --- the glyph bold in the accent, the duration of the turn ----------------------------------------
    seen = render("ag3", "--render", "dialogue", "--size", "100x30", "--press", "h,i,enter,wait:principal", "--styles")
    plain = P.ANSI.sub("", seen.stdout)
    status = plain.rstrip("\n").split("\n")[-1]
    look = P.styles_of(seen.stdout, r"ag3 · run w00003")
    timed = re.search(rf"^\s*[{SPINNER}] \d+ s ", status)
    if (seen.returncode == 0 and timed and re.search(rf"[{SPINNER}] \d+ s", tabs_of(plain))
            and any("1" in code.split(";")[:1] for code in look)):
        held("the glyph of the turn is seen", f"the status opens on {timed.group(0).strip()!r}, bold; the tab "
             f"{tabs_of(plain).strip()!r}")
    else:
        failures.append(f"  ✗ glyph of the turn           rc={seen.returncode} {status!r} {sorted(look)} {seen.stderr[-300:]!r}")
    return 0
