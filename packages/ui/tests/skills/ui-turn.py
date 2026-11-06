"""Scenario `ui-turn` -- the turn under way, seen in a conversation's tab (plan ui, batch le-tour-en-cours),
on the bench's `pp-chat` witness: `ag3`'s script holds the flow 2 s after the principal's line.
- while the turn runs, a spinner glyph on the tab's title and in the TURN ZONE of the message line -- between the
  alert and the box, the glyph and how long the turn has run (batch la-saisie-et-le-tour) --, none in the activity
  zone of the status row; what is typed meanwhile stays in the message line and `enter` sends nothing -- the footer's
  `[enter]` entry is not the one at rest, the witness's journal has the first message alone; the box stands on the
  same column at rest and during the turn: the zone is kept, empty, at rest
- once the turn ended, `enter` sends the line: the journal has both messages, in order
- at rest, no glyph anywhere
- the glyph is drawn bold in the theme's accent and the duration of the turn follows it, in the turn zone and on the
  tab's title (`--styles`; batch le-pied-et-les-overlays)
- the stop button: `■` beside the message line and a `[ctrl+g]` entry in the footer during a turn alone, neither at
  rest (`ag1`'s second exchange runs until a `stop`)
- `escape` twice during the turn sends no `stop` (the witness's journal): the turn goes on
- `ctrl+g`, or `tab` to the button and `enter`, sends `stop` -- the journal says `stop ag1`, the verdict interrupted
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"                # the glyphs of a turn under way, as the palette turns them
ACTIVITY = re.compile(rf"([{SPINNER}] \d+ s)\s*·\s*\d\d:\d\d:\d\d\s*$")   # a turn in the status row, then the clock
ZONE = re.compile(rf"([{SPINNER}] \d+ s)\s*│")                                 # the turn zone, then the box's border


def box_at(text: str) -> int:
    """-> the column the message line's box opens on (`┌`), -1 without one."""
    tops = [line.index("┌") for line in text.split("\n") if "┌───" in line]
    return tops[-1] if tops else -1


def boxed(line: str, text: str) -> str:
    """-> what a row says inside the message line's box: between its `┌` column and its `┐` column, stripped."""
    tops = [one for one in text.split("\n") if "┌───" in one]
    if not tops:
        return ""
    left, right = tops[-1].index("┌"), tops[-1].index("┐")
    return line[left + 1:right].strip()


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
    during = render("ag3", "--render", "dialogue", "--size", "100x30", "--press", "i,h,i,enter,wait:principal,y,o,enter",
                    "--styles")
    text_d = P.ANSI.sub("", during.stdout)
    lines_d = text_d.rstrip("\n").split("\n")
    sent_d = messages()
    zoned = next((ZONE.search(one) for one in lines_d if ZONE.search(one)), None)
    if (during.returncode == 0 and spinning(tabs_of(text_d)) and "ag3 · w00003" in tabs_of(text_d)
            and zoned and not spinning(lines_d[-1])
            and any(boxed(one, text_d) == "yo" for one in lines_d)
            and P.entry_of(text_d, "enter") and sent_d == ["message ag3 hi"] and len(P.heads_of(text_d)) == 1):
        held("the turn under way is seen, the line kept", f"the bar {tabs_of(text_d).strip()!r}, the turn zone says "
             f"{zoned.group(1)!r} before the box, the status row no glyph; `yo` typed during the turn stays in the line, "
             f"the journal says {sent_d}; the footer says {P.entry_of(text_d, 'enter')!r}")
    else:
        failures.append(f"  ✗ turn under way              rc={during.returncode} {sent_d} zoned={zoned} {text_d!r} "
                        f"{during.stderr[-300:]!r}")
    post.clear_journal()
    after = render("ag3", "--render", "dialogue", "--size", "100x44",     # two turns of words blocks in view
                   "--press", "i,h,i,enter,wait:principal,y,o,wait:waiting,enter", "--wait", "principal")
    sent_a = messages()
    if after.returncode == 0 and sent_a == ["message ag3 hi", "message ag3 yo"] and len(P.heads_of(after.stdout)) == 2:
        held("enter sends the line once the turn ended", f"the journal says {sent_a}, in this order; two ▶ in the transcript")
    else:
        failures.append(f"  ✗ sent after the turn        rc={after.returncode} {sent_a} {after.stdout!r} {after.stderr[-300:]!r}")
    rest = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", "i,h,i,enter", "--wait", "waiting")
    text_rest = rest.stdout
    if (rest.returncode == 0 and "✓ parked" in text_rest and not spinning(text_rest)
            and P.entry_of(text_rest, "enter") and P.entry_of(text_rest, "enter") != P.entry_of(text_d, "enter")
            and box_at(text_rest) == box_at(text_d) > 0):
        held("no glyph at rest, the line unmoved", f"after waiting: the verdict parked, no glyph anywhere, the footer "
             f"says {P.entry_of(text_rest, 'enter')!r}, not {P.entry_of(text_d, 'enter')!r}; the box on column "
             f"{box_at(text_rest)} at rest as during the turn")
    else:
        failures.append(f"  ✗ at rest                     rc={rest.returncode} box={box_at(text_rest)}/{box_at(text_d)} "
                        f"{text_rest!r} {rest.stderr[-300:]!r}")

    # --- the glyph bold in the accent, the duration of the turn ----------------------------------------
    seen, plain = during, text_d                           # the turn under way, drawn with its styles
    look = P.styles_of(seen.stdout, rf"[{SPINNER}] \d+ s") - {"0", ""}      # the turn zone's styles
    if (seen.returncode == 0 and zoned and re.search(rf"[{SPINNER}] \d+ s", tabs_of(plain))
            and any("1" in code.split(";")[:1] for code in look)):
        held("the glyph of the turn is seen", f"the zone says {zoned.group(1)!r} before the box, bold; the tab "
             f"{tabs_of(plain).strip()!r}")
    else:
        failures.append(f"  ✗ glyph of the turn           rc={seen.returncode} zoned={zoned} {sorted(look)} {seen.stderr[-300:]!r}")
    # --- the stop button: there during a turn alone; escape stops nothing; ctrl+g and the button stop ----
    def stops() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("stop ")]

    TURNING = "i,h,i,enter,wait:waiting,g,o,enter,wait:conduction"   # ag1's second exchange runs until a stop
    post.clear_journal()
    turning = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", f"{TURNING},escape,escape",
                     "--wait", "none:1")
    if (turning.returncode == 0 and "■" in turning.stdout and P.entry_of(turning.stdout, "ctrl+g")
            and "■" not in text_rest and not P.entry_of(text_rest, "ctrl+g")):
        held("the stop button is there during a turn alone", "during ag1's second exchange: `■` beside the line and "
             f"{P.entry_of(turning.stdout, 'ctrl+g')!r} in the footer; at rest neither")
    else:
        failures.append(f"  ✗ stop button                 rc={turning.returncode} {P.keys_of(turning.stdout)!r} / "
                        f"{P.keys_of(text_rest)!r} {turning.stdout!r}")
    if turning.returncode == 0 and stops() == [] and "interrupted" not in turning.stdout:
        held("escape stops nothing", "escape twice during the turn: no stop in the witness's journal, the turn goes on")
    else:
        failures.append(f"  ✗ escape                      rc={turning.returncode} {post.journal_lines()} {turning.stdout!r}")
    post.clear_journal()
    keyed = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", f"{TURNING},ctrl+g", "--wait", "waiting")
    keyed_stops = stops()
    post.clear_journal()
    pressed = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", f"{TURNING},tab,enter",
                     "--wait", "waiting")
    if (keyed.returncode == 0 and keyed_stops == ["stop ag1"] and "interrupted" in keyed.stdout
            and pressed.returncode == 0 and stops() == ["stop ag1"] and "interrupted" in pressed.stdout
            and "■" not in pressed.stdout):
        held("ctrl+g and the button stop the turn", "ctrl+g: `stop ag1` in the journal, the verdict interrupted; tab to "
             "the button and enter: the same; the button gone at rest")
    else:
        failures.append(f"  ✗ stop                        {keyed_stops} {post.journal_lines()} {keyed.stdout[-500:]!r} / "
                        f"{pressed.stdout[-500:]!r}")
    return 0
