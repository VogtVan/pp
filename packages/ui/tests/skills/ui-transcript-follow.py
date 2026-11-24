"""Scenario `ui-transcript-follow` -- where the transcript stands as its content and its height move, `ui-transcript`'s
sibling (rule 10): on a `TranscriptView` in a Textual app played in a subprocess, no house:
- the end followed (s.1416), the transcript alone: a view at its end -- reached by `end`, then one `down` more that
  moves nothing -- stays at its end as a turn is added (`scroll_y == max_scroll_y`); a view the principal raised
  (`home`) stays where it stood as what follows a message arrives -- the message itself brings the view back, (d)
- the end HELD and the history STILL (s.1498, batch le-suivi-de-la-fin), the transcript above a message box that
  grows with its text: (a) a view brought back to its end, the box growing in the frame of an answer -- the view
  ends at the new end, and at the next answer; (b) the box growing first, then an answer; `end` pressed in a raised
  view while an answer arrives; (c) a raised view inside the turn under way: answers arrive, a call is placed above,
  the steps' line unfolds above, `c` folds the conduction above, the terminal narrows -- the row at the top of the
  view stays the same row of the same block; (d) a raised view, a message of the principal added: its head in view,
  the end followed at the next answer -- a message taller than the view shows its head at the top, a message that
  arrives in a run read leaves the view where it stands; (e) `rebuild` with a turn of history above, on a raised
  view: the same row at the top
Where the view stands is read in its scroll and its rows, the row at its top against the row it held before the
movement: no text of the test is compared (rule 2).
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE

SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
FOLLOW = r'''
import asyncio, json, sys
sys.path.insert(0, sys.argv[1])
from textual.app import App
from textual.containers import Vertical
from textual.widgets import TextArea
from model.dialogue import Event, Turn
from panes.transcript import Block, TranscriptView


def turn(n):
    said = lambda kind, **fields: Event(kind, f"2026-11-09T10:00:{n:02d}+00:00", "r00001", fields)
    return [said("principal", text=f"question {n}"),
            said("conduction", launch=1, chars=1200, blocks=[{"stack": "BOOT ▸ MEMBER ▸ TURN{2/4}"}], text="served"),
            said("step", event="launch", launch=1),
            said("words", launch=1, text=f"the answer to {n}\n\na second paragraph"),
            said("agent", launch=1, cost_usd=0.01),
            said("verdict", state="parked", cost_usd=0.01, launches=1)]


class Probe(App):
    def compose(self):
        yield TranscriptView()


class Lined(App):
    """The transcript above a message box that grows with its text, as a conversation's tab lays them."""
    CSS = "#bottom { dock: bottom; height: auto; } TextArea { height: auto; max-height: 8; }"

    def compose(self):
        yield TranscriptView()
        yield Vertical(TextArea(id="message"), id="bottom")


def answer(n):
    return Event("words", f"2026-11-09T10:01:{n:02d}+00:00", "r00001",
                 {"launch": 1, "text": f"one more answer, {n}\n\nits second paragraph"})


async def past(app, pilot, events=None):
    """-> the view over a past of twenty turns -- or over `events` --, laid out, at its end."""
    view = app.query_one(TranscriptView)
    await view.rebuild(events or [one for n in range(20) for one in turn(n)])
    await pilot.pause()
    return view


def height(view):
    return view.scrollable_content_region.height


def ended(view):
    """-> whether the view stands at its end, its last row drawn."""
    return view.scroll_offset.y == view.max_scroll_y and view.scroll_offset.y + height(view) >= view._total


def place(view):
    """-> where the view stands, said."""
    return f"scroll_y {view.scroll_offset.y} of {view.max_scroll_y}, {height(view)} row(s) in view"


def top(view):
    """-> the row at the top of the view: its block's key, the row within it, its text."""
    item, within = view._at(view.scroll_offset.y)
    return [repr(view._key(item)), within, view._rows_of(item)[within][0].plain]


async def wheeled(view, pilot):
    """The view raised six rows then brought back to its end, as the wheel does: one scroll at a time, at once."""
    view.scroll_to(y=view.scroll_y - 6, animate=False)
    await pilot.pause()
    view.scroll_to(y=view.max_scroll_y, animate=False)
    await pilot.pause()


async def shrunk(together):
    """(a), (b) the view lower by two rows -- the message box taking three lines -- in the frame of an answer, or
    before it."""
    app = Lined()
    async with app.run_test(size=(100, 30)) as pilot:
        view = await past(app, pilot)
        await wheeled(view, pilot)
        checks, tall, box = {"at its end before": ended(view)}, height(view), app.query_one("#message")
        if together:
            await view.add(answer(1))
            box.text = "one\ntwo\nthree"
        else:
            box.text = "one\ntwo\nthree"
            await pilot.pause()
            await pilot.pause()
            checks["at its end, the box grown"] = ended(view)
            await view.add(answer(1))
        await pilot.pause()
        await pilot.pause()
        checks.update({"the view lower": height(view) < tall, "at the new end": ended(view)})
        said = place(view)
        await view.add(answer(2))
        await pilot.pause()
        checks["at the end of the next answer"] = ended(view)
        name = "a: the view lower in the frame of an answer" if together else "b: the view lower, then an answer"
        return {"case": name, "checks": checks, "said": f"{said}, then {place(view)}"}


async def ending():
    """(b) `end` in a raised view while an answer arrives: the scroll under way ends at the new end."""
    app = Lined()
    async with app.run_test(size=(100, 30)) as pilot:
        view = await past(app, pilot)
        view.focus()
        view.scroll_to(y=view.max_scroll_y - 100, animate=False)
        await pilot.pause()
        checks = {"raised before": not ended(view)}
        view.action_scroll_end()
        await pilot.pause(0.1)
        checks["the scroll under way"] = view.scroll_offset.y < view.max_scroll_y
        await view.add(answer(1))
        await pilot.pause(2.5)
        checks["at the new end"] = ended(view)
        return {"case": "b: end pressed in a raised view as an answer arrives", "checks": checks, "said": place(view)}


def under_way():
    """-> a past of five turns, then a turn under way: its message, its conduction -- no step yet --, ten blocks
    of words."""
    said = lambda kind, n, **fields: Event(kind, f"2026-11-09T10:02:{n:02d}+00:00", "r00001", fields)
    return ([one for n in range(5) for one in turn(n)]
            + [said("principal", 0, text="a question under way"),
               said("conduction", 1, launch=1, chars=1200, blocks=[{"stack": "TURN{2/4}"}], text="served")]
            + [said("words", 2 + n, launch=1, text=f"words {n} of the turn under way\n\ntheir second paragraph")
               for n in range(10)])


async def still():
    """(c) a view raised inside the turn under way: what comes at the end, above the view, or folds above it
    leaves the row at its top where it is."""
    said = lambda kind, n, **fields: Event(kind, f"2026-11-09T10:03:{n:02d}+00:00", "r00001", fields)
    app = Lined()
    async with app.run_test(size=(100, 30)) as pilot:
        view = await past(app, pilot, under_way())
        words = [one for one in view._items if isinstance(one, Block) and one.voice == "agent"]
        view.scroll_to(y=view._tops[words[-8].index] + 1, animate=False)   # the first paragraph of a block of the turn
        await pilot.pause()
        stood, checks = top(view), {"raised": not ended(view)}

        async def same(name, loose=False):
            await pilot.pause()
            await pilot.pause()
            now = top(view)
            kept = now[:2] == stood[:2] and (stood[2].startswith(now[2]) if loose else now[2] == stood[2])
            checks[name] = kept and bool(now[2].strip())
        await view.add(answer(1))
        await view.add(answer(2))
        await same("answers at the end")
        await view.add(said("tool", 1, id="t1", name="Bash", input={"command": "ls"}))
        await same("a call placed above")
        await view.add(said("step", 2, event="launch", launch=1))
        await same("the steps' line unfolded above")
        view.toggle_conduction()
        await same("c: the conduction folded above")
        await pilot.resize_terminal(40, 30)
        await same("the terminal narrowed", loose=True)
        return {"case": "c: a raised view keeps the row at its top", "checks": checks,
                "said": f"the row {stood[1]} of a block of words, {place(view)}"}


async def sent(tall):
    """(d) a message of the principal added on a raised view: the view shows it -- its head at the top when it
    is taller than the view --, then follows the end."""
    app = Lined()
    async with app.run_test(size=(100, 30)) as pilot:
        view = await past(app, pilot)
        view.scroll_to(y=10, animate=False)
        await pilot.pause()
        checks = {"raised before": not ended(view)}
        text = "\n\n".join(f"paragraph {n} of a long message" for n in range(30)) if tall else "a new message"
        await view.add(Event("principal", "2026-11-09T10:04:00+00:00", "r00001", {"text": text}))
        await pilot.pause()
        await pilot.pause()
        head = view._tops[view._items[-1].index] - view.scroll_offset.y
        rows = view._total - view._tops[view._items[-1].index]
        if tall:
            checks.update({"taller than the view": rows > height(view), "its head at the top": head == 0})
        else:
            checks.update({"its head in view": 0 <= head < height(view), "at the end": ended(view)})
        said = place(view)
        await view.add(answer(1))
        await pilot.pause()
        checks["at the end of the next answer"] = ended(view)
        name = "d: a message taller than the view, sent from a raised view" if tall \
            else "d: a message sent from a raised view"
        return {"case": name, "checks": checks,
                "said": f"its head on row {head} of the view, {said}, then {place(view)}"}


class Read(App):
    """The transcript of a run read: nobody sends a message from it."""

    def compose(self):
        yield TranscriptView(steps_alone=True)


async def read():
    """(d) a message that arrives in a run read: a raised view stays on the row at its top."""
    app = Read()
    async with app.run_test(size=(100, 30)) as pilot:
        view = await past(app, pilot)
        view.scroll_to(y=10, animate=False)
        await pilot.pause()
        stood, total = top(view), view._total
        await view.add(Event("principal", "2026-11-09T10:04:00+00:00", "r00001", {"text": "a message of the team"}))
        await view.add(answer(1))
        await pilot.pause()
        checks = {"raised": not ended(view), "rows added": view._total > total,
                  "the same row at the top": top(view) == stood}
        return {"case": "d: a message that arrives in a run read", "checks": checks, "said": place(view)}


async def rebuilt():
    """(e) `rebuild` on a raised view, a turn of history above: the same row at the top."""
    app = Lined()
    async with app.run_test(size=(100, 30)) as pilot:
        events = [one for n in range(20) for one in turn(n)]
        view = await past(app, pilot, events)
        words = [one for one in view._items if isinstance(one, Block) and one.voice == "agent"]
        view.scroll_to(y=view._tops[words[4].index] + 1, animate=False)
        await pilot.pause()
        stood, total = top(view), view._total
        kept = Turn(exchange=1, message="an earlier question", history=True, at="2026-11-09T09:00:00+00:00",
                    answer="An earlier answer, kept.")
        await view.rebuild(events, [kept])
        await pilot.pause()
        await pilot.pause()
        checks = {"raised": not ended(view), "rows above": view._total > total,
                  "the same row at the top": top(view) == stood}
        return {"case": "e: rebuild on a raised view", "checks": checks,
                "said": f"the row {stood[1]} of a block of words, {place(view)}"}


async def main():
    app, out = Probe(), {}
    async with app.run_test(size=(100, 30)) as pilot:
        view = app.query_one(TranscriptView)
        await view.rebuild([one for n in range(20) for one in turn(n)])
        view.focus()
        await pilot.pause()
        for n, (case, keys) in enumerate((("end", ("end", "down")), ("raised", ("home",)))):
            await pilot.press(*keys)
            await pilot.pause()
            before = (view.scroll_y, view.max_scroll_y)
            for one in turn(20 + n)[case == "raised":]:   # raised: what follows the message, without it
                await view.add(one)
            await pilot.pause()
            out[case] = [*before, view.scroll_y, view.max_scroll_y]
    out["held"] = [await shrunk(True), await shrunk(False), await ending(), await still(), await sent(False),
                   await sent(True), await read(), await rebuilt()]
    print(json.dumps(out))


asyncio.run(main())
'''


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the end followed: a view at its end stays there as a turn arrives, a view raised does not move -------
    probe = bench.temp() / "transcript-follow-probe.py"
    probe.write_text(FOLLOW, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL)], capture_output=True, text=True, cwd=bench.temp(),
                            timeout=180)
    try:
        follow = json.loads(played.stdout.strip().splitlines()[-1])
        end, raised = follow["end"], follow["raised"]
    except (ValueError, IndexError, KeyError):
        end = raised = None
    if (played.returncode == 0 and end and raised and end[0] == end[1] and end[3] > end[1] and end[2] == end[3]
            and raised[0] < raised[1] and raised[3] > raised[1] and raised[2] == raised[0]):
        held("the end followed as a turn arrives", f"at the end (end, down): scroll_y {end[0]} of {end[1]}, after "
             f"the turn {end[2]} of {end[3]}; raised (home): scroll_y {raised[0]}, after the turn {raised[2]} of {raised[3]}")
    else:
        failures.append(f"  ✗ end followed                rc={played.returncode} (scroll_y, max) before then after: "
                        f"at the end {end}, raised {raised} {played.stderr[-600:]!r}")

    # --- the end held as the view's height or the content moves; a raised view still; a message sent shown -------
    for one in (follow.get("held", []) if end else []):
        missed = [name for name, kept in one["checks"].items() if not kept]
        if not missed:
            held(one["case"], f"{', '.join(one['checks'])}: {one['said']}")
        else:
            failures.append(f"  ✗ {one['case']}: not {', not '.join(missed)} -- {one['said']}")
    if end and len(follow.get("held", [])) != 8:
        failures.append(f"  ✗ the end held                {len(follow.get('held', []))} case(s) read, 8 expected")
    return 0
