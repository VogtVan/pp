"""Scenario `ui-sequence-body` -- the BODY of a sequence virtualised (plan pp-fixes, batch
le-corps-virtualise-de-la-sequence): `panes.sequence_body.SequenceBody`, a `ScrollView` that draws one row per
`render_line` by `palette.sequence_row`, keeps each row drawn by its index, and never draws a row out of the view --
on a `Sequence` of 425 rows and 10 columns built in memory, no house, in a Textual app of 180x50 played in a
subprocess:
- the lines of `render_line`, at the top then after `scroll_end`, are the lines of the body `palette.sequence_text`
  draws, in text and in styles
- the first draw: `drawn` at most the height of the view
- a row added under the same frame draws the row added and the rows of the cursor alone; a width or a gutter
  changed empties the cache: `framed` +1, the view drawn again
- 50 `show` before a pause: `framed` +1 and one row drawn
- a `show` then a pause on the 425 rows -- a row added, the live case -- lays one frame and draws one row; its time,
  net of what a bare pause costs the pilot, is said beside the 272 ms `Static.update` took, and never fails the
  scenario: a time depends on the load of the pass (rule 10)
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE

SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
ROWS, COLUMNS, WIDTH, HEIGHT = 425, 10, 180, 50
BEFORE_MS = 272.0           # what `Static.update` of the body cost on banking-build T2 (the batch's measure)
PROBE = """
import asyncio, json, sys, time
sys.path.insert(0, sys.argv[1])
ROWS, COLUMNS, WIDTH, HEIGHT = (int(one) for one in sys.argv[2:6])
from rich.text import Text
from textual.app import App
from textual.strip import Strip
import palette
from model.teams import Sequence, SequenceRow
from panes.sequence_body import SequenceBody

COLS = tuple(["principal"] + [f"member-{n}" for n in range(1, COLUMNS)])


def row(n, kind="post", **more):
    at = f"2026-11-07T10:{(n * 7 // 60) % 60:02d}:{(n * 7) % 60:02d}+00:00"
    if kind == "wake":
        return SequenceRow("wake", n, at, COLS[1 + n % (COLUMNS - 1)], run=f"r{n:05d}", over=n % 3 == 0, **more)
    if kind == "mark":
        return SequenceRow("mark", n, at, COLS[1 + n % (COLUMNS - 1)], verb="done", **more)
    source, target = COLS[n % COLUMNS], COLS[(n * 3 + 1) % COLUMNS]
    verb = ("do", "ask", "re", "stop")[n % 4]
    return SequenceRow("post", n, at, source, target, verb, n - 1 if verb == "re" else None,
                       f"message {n} said to {target} by {source} with some words after it", **more)


def rows(count):
    return tuple(row(n, "wake" if n % 11 == 5 else "mark" if n % 23 == 7 else "post") for n in range(count))


def sequence(count, start="2026-11-07T10:00:00+00:00"):
    return Sequence(COLS, rows(count), COLS[1], start)


def strips(body):
    return [[(seg.text, str(seg.style or "")) for seg in body.render_line(y)] for y in range(body.size.height)]


def expected(body, seq, width, cursor, scroll_y):
    head, text = palette.sequence_text(seq, width, cursor)
    lines = text.split("\\n")
    base, view, console = body.rich_style, body.size.width, body.app.console
    found = []
    for y in range(body.scrollable_content_region.height):
        index = y + scroll_y
        if index < len(lines):
            strip = Strip(list(lines[index].render(console))).apply_style(base).crop_extend(0, view, base)
        else:
            strip = Strip.blank(view, base)
        found.append([(seg.text, str(seg.style or "")) for seg in strip.simplify()])
    return found


def simplified(body):
    return [[(seg.text, str(seg.style or "")) for seg in body.render_line(y).simplify()]
            for y in range(body.scrollable_content_region.height)]


class Probe(App):
    def compose(self):
        yield SequenceBody(id="body")


async def main():
    app, out = Probe(), {}
    async with app.run_test(size=(WIDTH, HEIGHT)) as pilot:
        body = app.query_one(SequenceBody)
        seq = sequence(ROWS)
        cursor = ROWS - 1
        out["mounted"] = [body.drawn, body.framed, body.frame is None]
        body.show(seq, WIDTH, cursor)
        await pilot.pause()
        view = body.scrollable_content_region.width
        height = body.scrollable_content_region.height
        out["view"] = [view, height]
        out["virtual"] = list(body.virtual_size)
        out["top_equal"] = simplified(body) == expected(body, seq, WIDTH, cursor, 0)
        out["first_drawn"], out["first_framed"], out["height"] = body.drawn, body.framed, body.size.height
        body.scroll_end(animate=False)
        await pilot.pause()
        scrolled = body.scroll_offset.y
        out["scrolled"] = scrolled
        out["end_equal"] = simplified(body) == expected(body, seq, WIDTH, cursor, scrolled)
        out["end_drawn"] = body.drawn
        # a row added under the same frame, the cursor following it
        drawn, framed = body.drawn, body.framed
        more = Sequence(COLS, seq.rows + (row(ROWS),), COLS[1], seq.start)
        body.show(more, WIDTH, ROWS)
        await pilot.pause()
        body.scroll_end(animate=False)
        await pilot.pause()
        out["added"] = [body.drawn - drawn, body.framed - framed, body.frame is not None and body.frame == frame_before(seq)]
        # a width changed: the frame changes, the cache empties
        drawn, framed = body.drawn, body.framed
        body.show(more, WIDTH + 80, ROWS)
        await pilot.pause()
        out["widened"] = [body.drawn - drawn, body.framed - framed, body.size.height]
        # a gutter changed: a row dated days later widens the scale, its delay in hours cumulated (252:00:00)
        drawn, framed = body.drawn, body.framed
        late = Sequence(COLS, more.rows + (SequenceRow("post", ROWS + 1, "2026-11-17T22:00:00+00:00", COLS[2], COLS[3], "do", None, "late"),), COLS[1], more.start)
        gutter_before = body.frame.gutter
        body.show(late, WIDTH + 80, ROWS + 1)
        await pilot.pause()
        body.scroll_end(animate=False)
        await pilot.pause()
        out["gutter"] = [body.drawn - drawn, body.framed - framed, gutter_before, body.frame.gutter, body.size.height]
        # 50 show before a pause: the cursor walked over the first rows, the view at the top
        body.scroll_home(animate=False)
        await pilot.pause()
        body.show(late, WIDTH, None)
        await pilot.pause()
        drawn, framed = body.drawn, body.framed
        for at in range(49, -1, -1):
            body.show(late, WIDTH, at)
        await pilot.pause()
        out["fifty"] = [body.drawn - drawn, body.framed - framed]
        # a show that changes nothing does not refresh
        drawn, framed = body.drawn, body.framed
        body.show(late, WIDTH, 0)
        await pilot.pause()
        out["same"] = [body.drawn - drawn, body.framed - framed]
        # the cost of a show then a pause on the 425 rows: a row added, the cursor on it -- the live case --,
        # net of what a bare pause costs the pilot (the median of three, measured just before)
        body.show(seq, WIDTH, cursor)
        await pilot.pause()
        body.scroll_end(animate=False)
        await pilot.pause()
        bare = []
        for _ in range(3):
            started = time.perf_counter()
            await pilot.pause()
            bare.append((time.perf_counter() - started) * 1000)
        out["bare_ms"] = sorted(bare)[1]
        drawn, framed = body.drawn, body.framed
        started = time.perf_counter()
        body.show(more, WIDTH, ROWS)
        await pilot.pause()
        out["gross_ms"] = (time.perf_counter() - started) * 1000
        out["ms"] = out["gross_ms"] - out["bare_ms"]
        out["ms_drawn"], out["ms_framed"] = body.drawn - drawn, body.framed - framed
    print(json.dumps(out))


def frame_before(seq):
    return palette.sequence_frame(seq, WIDTH, None)


asyncio.run(main())
"""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    probe = bench.temp() / "sequence-body-probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL), str(ROWS), str(COLUMNS), str(WIDTH), str(HEIGHT)],
                            capture_output=True, text=True, cwd=bench.temp(), timeout=120)
    try:
        said = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        said = {}
    if played.returncode != 0 or not said:
        failures.append(f"  ✗ probe                       rc={played.returncode} {played.stderr[-1200:]!r}")
        return 0
    view = said.get("view") or [0, 0]
    height = view[1]

    # --- the lines of render_line are the lines of palette.sequence_text --------------------------------------
    if said.get("top_equal") and said.get("end_equal") and said.get("scrolled", 0) > 0:
        held("render_line draws palette's lines", f"{height} lines equal in text and styles under the widget's "
             f"base style, at the top then at scroll {said['scrolled']}; virtual {said['virtual']}")
    else:
        failures.append(f"  ✗ lines                       top={said.get('top_equal')} end={said.get('end_equal')} "
                        f"scrolled={said.get('scrolled')} virtual={said.get('virtual')}")

    # --- the first draw draws the view alone -------------------------------------------------------------------
    first, lines = said.get("first_drawn", ROWS), said.get("height", 0)
    if (said.get("mounted") == [0, 0, True] and 0 < first <= lines and said.get("first_framed") == 1
            and said.get("end_drawn", ROWS) <= first + height):
        held("the first draw stops at the view", f"nothing before show; {first} rows drawn of {ROWS} for a view "
             f"{lines} high, one frame; {said['end_drawn']} after scroll_end")
    else:
        failures.append(f"  ✗ first draw                  mounted={said.get('mounted')} drawn={first} "
                        f"framed={said.get('first_framed')} height={lines} end={said.get('end_drawn')}")

    # --- a row added draws it and the cursor's rows; a width or a gutter changed empties the cache ------------
    added, widened, gutter = said.get("added") or [], said.get("widened") or [], said.get("gutter") or []
    if (len(added) == 3 and added[0] == 2 and added[1] == 1 and added[2]
            and len(widened) == 3 and widened[1] == 1 and widened[0] >= widened[2] - 1
            and len(gutter) == 5 and gutter[1] == 1 and gutter[3] > gutter[2] and gutter[0] >= gutter[4] - 1):
        held("a row added redraws it and the cursor", f"+{added[0]} rows drawn, same frame; a width changed: frame +1, "
             f"{widened[0]} drawn; the gutter {gutter[2]} -> {gutter[3]}: frame +1, {gutter[0]} drawn")
    else:
        failures.append(f"  ✗ cache                       added={added} widened={widened} gutter={gutter}")

    # --- 50 show before a pause: one frame, one row drawn; a show that changes nothing: none -------------------
    fifty, same = said.get("fifty") or [], said.get("same") or []
    if fifty == [1, 1] and same == [0, 0]:
        held("50 show give one frame and one draw", f"drawn +{fifty[0]}, framed +{fifty[1]}; an equal show: +0 +0")
    else:
        failures.append(f"  ✗ fifty                       fifty={fifty} same={same}")

    # --- the cost ------------------------------------------------------------------------------------------------
    ms, gross, bare = said.get("ms"), said.get("gross_ms", 0), said.get("bare_ms", 0)
    if isinstance(ms, (int, float)) and said.get("ms_framed") == 1 and said.get("ms_drawn") == 1:
        held("a show then a pause lays one frame, draws one row",
             f"{ms:.1f} ms for a row added on {ROWS} rows, against {BEFORE_MS:.0f} ms for `Static.update`: show and "
             f"pause {gross:.1f} ms, of which a bare pause {bare:.1f} ms")
    else:
        failures.append(f"  ✗ cost                        framed +{said.get('ms_framed')} drawn +{said.get('ms_drawn')} "
                        f"(want 1, 1); {ms} ms net")
    return 0
