"""render -- a pane of the post as TEXT, without a terminal: the app runs headless at the
asked size under Textual's test pilot, settles, and its screen is printed through a
recording console -- the same path `App.export_screenshot` takes to make its SVG, exported
as text instead -- under `--styles`, with the ANSI styles of what is drawn, the look of each line
the bench compares. What the bench and `--render` read is exactly what the compositor drew.
`rendered` is a coroutine: the entry awaits it on the loop the conversations were opened on."""
from __future__ import annotations

import asyncio
import io

from rich.console import Console
from textual.app import App

from model import FRAME, Size

LAYOUTS = "layouts"                  # a word of the keys: the count of the transcript's arrangements, noted there
SPINNING = "spinning"                # a word of the keys: whether the spinner's interval is alive, noted there


def screen_text(app: App, styles: bool = False) -> str:
    """-> the screen of a RUNNING app, as text, line by line -- with its ANSI styles when asked."""
    width, height = app.size
    console = Console(width=width, height=height, file=io.StringIO(), force_terminal=True,
                      color_system="truecolor", record=True, legacy_windows=False, safe_box=False)
    console.print(app.screen._compositor.render_update(full=True,
                                                       screen_stack=app._background_screens))
    return console.export_text(styles=styles)


def regions_text(app: App, pane: str) -> str:
    """-> where the parts of a pane stand on the screen, one line each, `<part> <id> x=<x> y=<y> w=<w> h=<h>` --
    its menu, its folded line, and each band of its centre that is shown: what the bench measures to say that a
    centre is a pile of horizontal bands, and that a menu folds on a narrow screen."""
    lines = []
    root = app.query_one(f"#pane-{pane}")
    for part, selector in (("menu", ".menu"), ("fold", ".fold")):
        for one in root.query(selector):
            region = one.region
            lines.append(f"{part} {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
    for centre in root.query(".centre"):
        for one in centre.children:
            region = one.region
            if one.display and region.width and region.height:
                lines.append(f"band {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
    return "\n".join(lines) + "\n"


WAIT_SECONDS = 10.0                  # the default bound of `--wait`


async def rendered(app, pane: str, size: Size, keys: tuple[str, ...] = (), wait: str | None = None,
                   seconds: float = WAIT_SECONDS, styles: bool = False, regions: bool = False) -> str:
    """-> the pane `pane` (or the whole frame) at `size`, after the `keys` are pressed in
    order (Textual's key names: `2`, `tab`, `ctrl+left`) and, with `wait`, after one more
    event of that kind than before the LAST key pressed reached any conversation (within
    `seconds`), as text ending with a newline -- its ANSI styles kept under `styles`; under `regions`, where the
    parts of the pane stand instead (`regions_text`). The word `layouts` among the keys notes, at that point, how
    many arrangements the active conversation's transcript computed: the counts noted close the text on one line,
    `layouts <n> <n> …`; the word `spinning` notes whether the spinner's interval is alive (1, else 0), closing the
    text on `spinning <n> <n> …`."""
    async with app.run_test(size=(size.width, size.height)) as pilot:
        await app.settled()                    # the conversations of the start in their tabs, the agents read
        await pilot.pause()
        if pane != FRAME:
            app.show_pane(pane)
        await app.pane_settled()               # the pane shown read what its showing asked
        seen = app.counts()
        counted: list[int] = []
        spun: list[int] = []
        for key in keys:
            if key == LAYOUTS:
                await pilot.pause()
                counted.append(app.layouts())
            elif key == SPINNING:
                await app.pane_settled()
                await pilot.pause()
                spun.append(app.spinning())
            elif key.startswith("wait:"):
                # a pause in the sequence: one more event of that kind than BEFORE the last key
                # pressed (the flow may have answered already, within the key's own settling)
                await _one_more(app, key[5:], seconds, seen.get(key[5:], 0))
                await pilot.pause()
            else:
                seen = app.counts()
                await pilot.press(key)
                await app.pane_settled()
        if wait:
            await _one_more(app, wait, seconds, seen.get(wait, 0))
        await pilot.pause()
        await app.pane_settled(final=True)     # a thread whose cursor rests too
        await pilot.pause()                    # what the last reading changed, laid out before it is printed
        text = regions_text(app, pane) if regions else screen_text(app, styles)
    text = text if text.endswith("\n") else text + "\n"
    return (text + (f"{LAYOUTS} {' '.join(str(one) for one in counted)}\n" if counted else "")
            + (f"{SPINNING} {' '.join(str(one) for one in spun)}\n" if spun else ""))


async def _one_more(app, kind: str, seconds: float, before: int | None = None) -> None:
    """Waits until the conversations took ONE MORE event of `kind` than `before` (their count
    now, by default) -- or the flow ended, or `seconds` passed."""
    count = app.saw(kind) if before is None else before
    deadline = asyncio.get_event_loop().time() + seconds
    while app.saw(kind) <= count and not app.saw("ended"):
        if asyncio.get_event_loop().time() >= deadline:
            return
        await asyncio.sleep(0.05)


def text_of(app, pane: str, size: Size, keys: tuple[str, ...] = (), wait: str | None = None,
            seconds: float = WAIT_SECONDS) -> str:
    """The same, on a loop of its own -- for a post opened on no conversation."""
    return asyncio.run(rendered(app, pane, size, keys, wait, seconds))
