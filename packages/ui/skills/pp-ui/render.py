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
from textual import events
from textual.app import App

from model import FRAME, Size

LAYOUTS = "layouts"                  # a word of the keys: the count of the transcript's arrangements, noted there
SPINNING = "spinning"                # a word of the keys: whether the spinner's interval is alive, noted there
REST = "rest:"                       # a word of the keys: `rest:<seconds>` lets that time pass, the screen's timers playing
NODES = "nodes"                      # a word of the keys: the widgets of the transcript's last block of the agent, noted there
BLUR, FOCUS = "blur", "focus"        # words of the keys: the application loses, or takes back, the focus of the terminal --
                                     # the widget focused then and the application's focus noted


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
    its menu, its folded line, and each band of its centre that is shown, then each part of that band that is shown
    and named (`inner`): what the bench measures to say that a centre is a pile of horizontal bands, that a menu folds
    on a narrow screen, and what a band holds; then every fixed ZONE of the screen (class `zone`) that is laid out,
    shown or hidden -- what it measures to say that nothing moves a zone."""
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
                for inner in one.children:
                    area = inner.region
                    if inner.id and inner.display and area.width and area.height:
                        lines.append(f"inner {inner.id} x={area.x} y={area.y} w={area.width} h={area.height}")
    for one in app.screen.query(".zone"):
        region = one.region
        if region.width and region.height:
            lines.append(f"zone {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
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
    text on `spinning <n> <n> …`; the word `rest:<seconds>` lets that time pass, the screen's timers playing; the word
    `nodes` notes how many widgets the last block of the agent's words in the active transcript holds, closing the text
    on `nodes <n> <n> …`; the words `blur` and `focus` make the application lose and take back the focus of the terminal,
    each noting the widget focused then (its id, `none` without one) and the application's focus (1, else 0), closing
    the text on `focused <id>:<n> <id>:<n> …`."""
    async with app.run_test(size=(size.width, size.height)) as pilot:
        await app.settled()                    # the conversations of the start in their tabs, the agents read
        await pilot.pause()
        if pane != FRAME:
            app.show_pane(pane)
        await app.pane_settled()               # the pane shown read what its showing asked
        seen = app.counts()
        counted: list[int] = []
        spun: list[int] = []
        nodes: list[int] = []
        focused: list[str] = []
        for key in keys:
            if key == LAYOUTS:
                await pilot.pause()
                counted.append(app.layouts())
            elif key == SPINNING:
                await app.pane_settled()
                await pilot.pause()
                spun.append(app.spinning())
            elif key == NODES:
                await pilot.pause()
                nodes.append(app.nodes())
            elif key in (BLUR, FOCUS):
                app.post_message(events.AppBlur() if key == BLUR else events.AppFocus())
                await pilot.pause()
                widget = app.screen.focused
                focused.append(f"{(widget.id or type(widget).__name__) if widget is not None else 'none'}:"
                               f"{int(app.app_focus)}")
            elif key.startswith(REST):
                await asyncio.sleep(float(key[len(REST):]))
                await pilot.pause()
                await app.pane_settled()
            elif key.startswith("wait:"):
                # a pause in the sequence: one more event of that kind than BEFORE the last key
                # pressed (the flow may have answered already, within the key's own settling)
                await _one_more(app, key[5:], seconds, seen.get(key[5:], 0))
                await pilot.pause()
            else:
                seen = app.counts()
                await pilot.press(key)
                if app.return_code is not None:   # the post left on a key (a verb asked of the console): nothing to show
                    return ""
                await app.pane_settled()
        if wait:
            await _one_more(app, wait, seconds, seen.get(wait, 0))
        await pilot.pause()
        await app.pane_settled(final=True)     # a thread whose cursor rests too
        await pilot.pause()                    # what the last reading changed, laid out before it is printed
        text = regions_text(app, pane) if regions else screen_text(app, styles)
    text = text if text.endswith("\n") else text + "\n"
    return (text + (f"{LAYOUTS} {' '.join(str(one) for one in counted)}\n" if counted else "")
            + (f"{SPINNING} {' '.join(str(one) for one in spun)}\n" if spun else "")
            + (f"{NODES} {' '.join(str(one) for one in nodes)}\n" if nodes else "")
            + (f"focused {' '.join(focused)}\n" if focused else ""))


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
