"""Scenario `ui-relief` -- what the post's frame and transcript set apart (plan ui, batch l-en-tete-et-le-relief), on the
bench's `pp-chat` witness and a witness of `version -json`:
- the header says the engine's version and the post's, read from `./pp version -json`, beside the house's root
- in a turn, the principal's message stands at least four columns to the right of the agent's answer and on a background
  the answer does not have -- in a dark theme and in a light one (`--styles`)
- under `pp off`, the banner stands just above the message line, under the transcript
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

    # --- pp off: the banner just above the message line --------------------------------------------------------
    post.use(P.conduct_script())
    paused = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", f"{SENT},o", "--wait", "conduct")
    rows = paused.stdout.split("\n")
    banner = next((n for n, one in enumerate(rows) if "pp OFF" in one), -1)
    answer = max((n for n, one in enumerate(rows) if "✓ parked" in one), default=-1)    # the transcript's last verdict
    rule = next((n for n in range(banner + 1, len(rows)) if rows[n].strip().startswith("─")), -1) if banner >= 0 else -1
    if paused.returncode == 0 and banner > answer >= 0 and rule == banner + 1:
        held("the pp OFF banner sits on the message line", f"row {banner}: under the transcript (its last answer row "
             f"{answer}), the message line's rule right under it")
    else:
        failures.append(f"  ✗ banner                      rc={paused.returncode} banner={banner} answer={answer} rule={rule} "
                        f"{paused.stdout[-1500:]!r}")
    return 0
