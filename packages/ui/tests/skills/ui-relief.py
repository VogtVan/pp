"""Scenario `ui-relief` -- what the post's frame and transcript set apart (plan ui, batch l-en-tete-et-le-relief), on the
bench's `pp-chat` witness and a witness of `version -json`:
- the header says the engine's version and the post's, read from `./pp version -json`, beside the house's root
- in a turn, the principal's message stands at least four columns to the right of the agent's answer and on a background
  the answer does not have -- in a dark theme and in a light one (`--styles`)
- under `pp off`, the alert zone left of the message line says the pause glyph on the message line's own row, and
  the message line stands where it stood before (batch les-zones-fixes)
- the message line holds its columns: the zones of the gauge, the alert and the message keep their columns before any
  verdict, during a turn and after the verdict that fills the gauge; the stop button shows in its kept place
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from tests.harness import support

P = support(__file__, "dialogue")

ENGINE, POST = "9.9.9-bench", "8.8.8"
FACE = {"source": "/the/source", "machine": None, "engine": ENGINE, "at_source": None,
        "packages": {"kit": "1.0.0", "ui": POST}}
TURN = "i,h,i,enter,wait:waiting"
SENT = "i,h,i,enter,wait:waiting,escape"
SEGMENT = re.compile(r"\x1b\[([0-9;]*)m([^\x1b]*)")
BACKGROUND = re.compile(r"(?:^|;)48;2;(\d+;\d+;\d+)")
THEMES = ("textual-dark", "textual-light")
LINE_SIZE = ("--size", "120x30")


def background_of(row: str, text: str) -> str | None:
    """-> the background (`r;g;b`) the styled `row` gives the segment carrying `text`, None without one."""
    for codes, said in SEGMENT.findall(row):
        if text in said:
            found = BACKGROUND.search(codes)
            return found.group(1) if found else None
    return None


def column_of(plain: str) -> int:
    return len(plain) - len(plain.lstrip())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-relief")
    faces = Path(post.env["PP_UI_FACES"])
    (faces / "version").write_text(f"#!/bin/sh\nprintf '%s\\n' '{json.dumps(FACE)}'\n", encoding="utf-8")
    (faces / "version").chmod(0o755)

    # --- the header: the engine's version and the post's ---------------------------------------------------
    framed = post.render("--render", "frame", "--size", "120x24")
    head = framed.stdout.split("\n")[0]
    if framed.returncode == 0 and ENGINE in head and POST in head and str(post.ws) in head:
        held("the header says the versions", head.strip()[:110])
    else:
        failures.append(f"  ✗ header                      rc={framed.returncode} {head!r} {framed.stderr[-300:]!r}")

    # --- the principal set apart: four columns to the right, a background of its own, in two themes ---------------
    for theme in THEMES:
        P.keep_theme(post.made, theme)
        lived = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--styles", "--press", TURN, keep=True)
        rows = lived.stdout.split("\n")
        plain = [P.ANSI.sub("", one) for one in rows]
        said = next((n for n, one in enumerate(plain) if one.strip() == "hi"), -1)
        answered = next((n for n, one in enumerate(plain) if one.strip() == "the agent says one"), -1)
        shift = column_of(plain[said]) - column_of(plain[answered]) if said >= 0 and answered >= 0 else None
        own = background_of(rows[said], "hi") if said >= 0 else None
        other = background_of(rows[answered], "the agent says one") if answered >= 0 else None
        if lived.returncode == 0 and shift is not None and shift >= 4 and own and own != other:
            held(f"the principal is set apart ({theme})", f"its message {shift} columns to the right of the answer, "
                 f"background {own} against {other}")
        else:
            failures.append(f"  ✗ principal ({theme})        rc={lived.returncode} shift={shift} own={own} other={other} "
                            f"{lived.stderr[-300:]!r}")

    # --- pp off: the mark in the alert zone, on the message line's row; the line where it stood ---------------
    post.use(P.conduct_script())
    sent = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--regions", "--press", SENT)
    paused_at = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--regions", "--press", f"{SENT},o",
                            "--wait", "conduct")
    paused = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", f"{SENT},o", "--wait", "conduct")
    before, after = P.zones_of(sent.stdout), P.zones_of(paused_at.stdout)
    alert, message = after.get("alert"), after.get("message")
    rows = paused.stdout.split("\n")
    glyph = P.palette_constant("PAUSED")
    cells = [row[alert[0]:alert[0] + alert[2]] for row in rows[alert[1]:alert[1] + alert[3]]] if alert else []
    if (paused.returncode == 0 and alert and message and alert[1] == message[1] and alert[0] + alert[2] <= message[0]
            and any(glyph in one for one in cells) and before.get("message") == message):
        held("the pp OFF mark sits in the alert zone", f"alert {alert} left of the message {message}, on its row; "
             "the message line where it stood before")
    else:
        failures.append(f"  ✗ alert                       rc={paused.returncode} alert={alert} message={message} "
                        f"before={before.get('message')} cells={cells} {paused.stderr[-300:]!r}")

    # --- the message line holds its columns: rest, a turn under way, the verdict that fills the gauge ----------
    post.use(P.SCRIPT)
    line = ("context", "alert", "message")
    states = {"rest": post.render("ag1", "--render", "dialogue", *LINE_SIZE, "--regions"),
              "turn": post.render("ag3", "--render", "dialogue", *LINE_SIZE, "--regions", "--press", "i,h,i,enter,wait:principal"),
              "verdict": post.render("ag1", "--render", "dialogue", *LINE_SIZE, "--regions", "--press", TURN)}
    placed = {name: {zone: P.zones_of(done.stdout).get(zone, (None, None, None))[::2] for zone in line}
              for name, done in states.items()}              # (x, w): the columns of each zone
    stop = P.zones_of(states["turn"].stdout).get("stop")
    message = P.zones_of(states["turn"].stdout).get("message")
    if (all(done.returncode == 0 for done in states.values()) and all(None not in one for one in placed["rest"].values())
            and placed["rest"] == placed["turn"] == placed["verdict"] and stop and message
            and stop[0] == message[0] + message[2]):
        held("the message line holds its columns", f"(x, w) {placed['rest']} at rest, during a turn and after the "
             f"verdict; the stop button at {stop[0]} during the turn, in its kept place")
    else:
        failures.append(f"  ✗ line zones                  {placed} stop={stop} {states['rest'].stderr[-300:]!r}")
    return 0
