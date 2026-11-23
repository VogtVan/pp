"""Scenario `ui-tasks-inbox` -- the owner's inbox opened from the Tasks tab (batch l-inbox-et-les-taches), on the bench's
`pp-team` witness:
- `b` on the Tasks tab reads `team inbox <team> --json` of the team of the task under the cursor and shows it in an
  overlay titled by the team; `enter` on its question opens the overlay that writes on the question's task, the reply
  chosen -- `enter` there plays a post naming `--task` and `--reply`, as the witness's journal says it; `b` alone
  plays nothing, no command shown
- `a` there plays `team inbox <team> --seen` -- all read -- and closes the overlay (ui 1.4.6)
- on the Dialogue tab `b` reads nothing of team
- the box is EventScreen's -- 95 % of the width, 90 % of the height (s.1426) --; each message on ONE row cut by `…`,
  and over the keys the pane that shows the message under the cursor whole, following it (s.1430)
- `x` on an info plays `team inbox <team> --seen --id <its id>`, the overlay stays open and the row leaves; `x` on a
  question plays the same, the team's refusal `inbox-question` on the remedy line and under the inbox's list, the row
  kept (s.1427, s.1704)
- `enter` on a question of the inbox whose task's face is older than the inbox (the question not yet in its
  `waiting`): the reply still goes with `--reply <id>` (s.1429)
- under the pilot (batch l-inbox-retournee, ui 1.4.12): the pane of the message under the cursor is as high for a message
  of one line as for a long one, which scrolls in it by a vertical bar (s.1464); it stands above the list (s.1465); a
  click on the row of a question highlights it and shows it, the inbox on top, no reply pushed (s.1466); `enter` on a
  question pushes the reply OVER the inbox, `escape` there gives the inbox back on top, the cursor where it was, and
  `enter` there plays the post `--task --reply`, the inbox on top again and read again (s.1467)
- the pane of the message under the cursor is half the box high at least, at two heights of the terminal, and framed:
  a border and a title on the widget (batch le-volet-de-l-inbox, ui 1.4.23, s.1518)
- the pane draws the message as markdown (batch l-inbox-en-markdown, ui 1.10.31): its text is the post's markdown
  widget holding the message's source, drawn with the looks of a heading, of code and of a link, its table boxed
  (rows of its border alone), its fence shaded over the pane's width, more rows drawn than its source holds, no row
  wider than the pane, no horizontal bar
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

QUESTION = {"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "text": "tests green?"}
INBOX = {"core-review": {"team": "core-review", "questions": [QUESTION], "done": [{"task": "T2", "id": 40}], "returned": []}}
REPLY = f"team post core-review --task {QUESTION['task']} --reply {QUESTION['id']} --message ok --no-tick"
SEEN = "team inbox core-review --seen"
WHOLE = "the second review is green on every bench " * 6 + "\nand the last word is END-OF-INFO"
INFO = {"id": 47, "from": "lead", "task": "T3", "text": WHOLE}
LONG = {"core-review": {**INBOX["core-review"], "infos": [INFO]}}
READ_INFO = "team inbox core-review --seen --id 47"
READ_ASK = "team inbox core-review --seen --id 45"
TALL = {"id": 48, "from": "lead", "task": "T3", "text": "\n".join(f"- the line {n} of a tall info" for n in range(30))}
MARKED = {"id": 49, "from": "lead", "task": "T3", "text": "# T3 delivered\n\n- `team resume` lifts a quota\n- see "
          "[the plan](https://example.org/plan)\n\n| render | before | after |\n|---|---|---|\n"
          + "\n".join(f"| team-quota-{n} {'wide ' * 12}| red | green in 14.2 s |" for n in range(3))
          + "\n\n```\n" + "a line of code " * 14 + "\n```"}
TALLER = {"core-review": {**INBOX["core-review"], "infos": [TALL, MARKED]}}
REFUSAL = "pp-team: inbox-question -- #45 waits for your answer: `team post core-review --task <id> --reply 45`"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-inbox", T.script(inbox=INBOX))

    # --- b: the inbox of the task's team; enter replies on the question's task ---------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b")
    rows = [one for one in P.overlay_rows(done.stdout) if one]
    read, unplayed = "inbox core-review" in house.journal_lines(), house.gestures()
    house.clear_journal()
    replied = house.render("--render", "tasks", "--size", "150x40", "--press", "b,enter,o,k,ctrl+enter")
    if (done.returncode == 0 and rows and "core-review" in rows[0] and any(f"#{QUESTION['id']}" in row for row in rows[1:])
            and "./pp" not in done.stdout and read and unplayed == []
            and replied.returncode == 0 and house.gestures() == [REPLY]):
        held("b opens the inbox of the task's team", f"{rows[0]!r}, #{QUESTION['id']} in it, no command, nothing played; "
             f"enter, ok, enter: {REPLY!r}")
    else:
        failures.append(f"  ✗ b on tasks                  rc={done.returncode}/{replied.returncode} "
                        f"{rows!r} {unplayed} {house.gestures()} {done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- a marks it all read and closes; b elsewhere reads nothing ----------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,a")
    played = house.gestures()
    house.clear_journal()
    other = house.render("--render", "dialogue", "--size", "150x40", "--press", "b")
    if (done.returncode == 0 and played == [SEEN] and not P.overlay_rows(done.stdout)
            and other.returncode == 0 and house.journal_lines() == []):
        held("a marks the inbox all read and closes; b elsewhere reads nothing", f"{played[0]}, the overlay closed; "
             "no call of team from the dialogue")
    else:
        failures.append(f"  ✗ all read                    rc={done.returncode}/{other.returncode} {played} "
                        f"{house.journal_lines()} {done.stdout[-600:]!r}")

    # --- the box, one row per message, the pane of the message under the cursor --------------------------------
    house.use(T.script(inbox=LONG))
    first = house.render("--render", "tasks", "--size", "150x40", "--press", "b")
    moved = house.render("--render", "tasks", "--size", "150x40", "--press", "b,down")
    rows = moved.stdout.split("\n")
    top = next((n for n, row in enumerate(rows) if "┏" in row and "┓" in row), -1)
    bottom = next((n for n, row in enumerate(rows) if n > top and "┗" in row), -1)
    wide = rows[top].index("┓") - rows[top].index("┏") + 1 if top >= 0 else 0
    high = bottom - top + 1 if top >= 0 and bottom > top else 0
    inside = P.overlay_rows(moved.stdout)
    listed = [one for one in inside if one.startswith("▊")]                 # the rows of the list, the pane apart
    info_rows = [one for one in listed if "#47 info" in one]
    whole = [one for one in inside if not one.startswith("▊")]
    if (first.returncode == 0 and moved.returncode == 0 and wide >= int(150 * 0.95) - 1 and high >= int(40 * 0.9) - 1
            and len(info_rows) == 1 and "…" in info_rows[0]
            and len([one for one in listed if "green on every bench" in one]) == 1
            and any("END-OF-INFO" in one for one in whole) and not any("END-OF-INFO" in one for one in listed)
            and not any("END-OF-INFO" in one for one in P.overlay_rows(first.stdout))
            and any("tests green?" in one for one in P.overlay_rows(first.stdout))):
        held("the box, one row per message, the pane under the cursor", f"box {wide}x{high} on 150x40; #47 on one row "
             "cut by …; on it the pane says its whole text (END-OF-INFO), on the question the question's")
    else:
        failures.append(f"  ✗ box and rows               rc={first.returncode}/{moved.returncode} box={wide}x{high} "
                        f"info_rows={info_rows} {moved.stdout[-2500:]!r}")

    # --- x on an info: one message read, the overlay open, the row gone ----------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,down,x")
    played = house.gestures()
    inside = P.overlay_rows(done.stdout)
    if (done.returncode == 0 and played == [READ_INFO] and any("inbox of core-review" in one for one in inside)
            and not any("#47 info" in one for one in inside if one.startswith("▊"))
            and any("#45" in one for one in inside)):
        held("x reads the one message under the cursor", f"{played[0]}; the overlay open, #47 gone, #45 kept")
    else:
        failures.append(f"  ✗ x on an info                rc={done.returncode} {played} {inside} {done.stdout[-1500:]!r}")

    # --- x on a question: the team's refusal on the remedy line, the row kept ----------------------------------
    house.use(T.script(inbox=LONG, answers={"inbox": {"rc": 2, "err": REFUSAL + "\n"}}))
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "b,x")
    played = house.gestures()
    inside = P.overlay_rows(done.stdout)
    gap = [one for one in inside if "inbox-question" in one and not one.startswith("▊")]
    if (done.returncode == 0 and played == [READ_ASK] and "inbox-question" in P.remedy_of(done.stdout)
            and any("#45" in one for one in inside) and gap):
        held("x on a question: the team refuses", f"{played[0]}; remedy {P.remedy_of(done.stdout)[:60]!r} and under the "
             "list, #45 kept")
    else:
        failures.append(f"  ✗ x on a question             rc={done.returncode} {played} "
                        f"remedy={P.remedy_of(done.stdout)!r} {inside}")

    # --- enter on a question the task's face does not hold yet: the reply still cites it ------------------------
    stale = {**T.CORE, "waiting": {"questions": [], "done": ["T2"], "returned": []}}
    house.use(T.script(inbox=INBOX, states={"core-review": [stale], "ops": [T.OPS]}))
    house.clear_journal()
    replied = house.render("--render", "tasks", "--size", "150x40", "--press", "b,enter,o,k,ctrl+enter")
    played = house.gestures()
    if replied.returncode == 0 and played == [REPLY]:
        held("enter on a question replies to it", f"the face's waiting empty, the inbox's #45: {played[0]!r}")
    else:
        failures.append(f"  ✗ reply on a stale face       rc={replied.returncode} {played} {replied.stdout[-1500:]!r}")

    # --- under the pilot: the pane fixed and on top, a click that selects, the reply over the inbox -------------
    house.use(T.script(inbox=TALLER))
    house.clear_journal()
    [(rc, said, err)] = T.piloted(bench, house, "ui-tasks-inbox", PROBE, "tasks", size="150x40")
    if rc != 0 or not said.get("opened"):
        failures.append(f"  ✗ inbox probe                 rc={rc} {said} {err[-1500:]!r}")
        return 0
    one, tall = said.get("one") or {}, said.get("tall") or {}
    if one.get("height") and one.get("height") == tall.get("height") and tall.get("bar") and tall.get("beyond"):
        held("the pane of the inbox does not follow the message and scrolls", f"{one['height']} rows for one line and "
             f"for #48, #48 beyond it by {tall['beyond']} rows, its vertical bar shown")
    else:
        failures.append(f"  ✗ pane fixed                  one={one} tall={tall}")
    marked = said.get("marked") or {}
    if (marked.get("widget") == "MarkdownText" and marked.get("source") and marked.get("bold") and marked.get("code")
            and marked.get("link") and 0 < marked.get("widest", 0) <= marked.get("width", 0)
            and marked.get("borders", 0) >= 3 and marked.get("fenced", 0) >= 1
            and marked.get("rows", 0) > (marked.get("source_rows") or 0)
            and not marked.get("bar") and marked.get("scroll_x") == 0):
        held("the pane of the inbox draws the message as markdown", f"{marked['widget']} on the source of #49, a heading, "
             f"code and a link drawn, {marked['borders']} border rows of a table, {marked['fenced']} shaded rows of a "
             f"fence, {marked['rows']} rows for {marked['source_rows']} of source; widest row {marked['widest']} of "
             f"{marked['width']}, no horizontal bar")
    else:
        failures.append(f"  ✗ markdown pane               {marked}")
    halves = said.get("halves") or []
    if (len(halves) == 2 and len({one["box"] for one in halves}) == 2
            and all(one["box"] and 2 * one["pane"] >= one["box"] and one["border"] and one["title"] for one in halves)):
        held("the pane of the inbox is half the box at least, framed", ", ".join(
            f"pane {one['pane']} of a box of {one['box']} on {one['size']}" for one in halves) + "; border and title shown")
    else:
        failures.append(f"  ✗ pane half and framed        {halves}")
    if said.get("pane_y") is not None and said.get("list_y") is not None and said["pane_y"] < said["list_y"]:
        held("the pane of the inbox stands above its list", f"pane at y={said['pane_y']}, list at y={said['list_y']}")
    else:
        failures.append(f"  ✗ pane on top                 pane_y={said.get('pane_y')} list_y={said.get('list_y')}")
    click = said.get("click") or {}
    if (click.get("top") == "InboxScreen" and click.get("highlighted") == 0 and not click.get("gesture")
            and click.get("shown")):
        held("a click on a question selects it, no reply", f"stack {click.get('stack')}, row 0 highlighted, shown")
    else:
        failures.append(f"  ✗ click on a question         {click}")
    over, back, sent = said.get("over") or [], said.get("back") or {}, said.get("sent") or {}
    played = house.gestures()
    calls = house.journal_lines()
    posted = next((n for n, line in enumerate(calls) if line.startswith("team post")), None)
    reread = posted is not None and any(line == "inbox core-review" for line in calls[posted + 1:])
    if (over[-2:] == ["InboxScreen", "GestureScreen"] and back.get("top") == "InboxScreen"
            and back.get("highlighted") == 0 and sent.get("top") == "InboxScreen" and played == [REPLY] and reread):
        held("the reply over the inbox", f"enter: {over[-2:]}; escape: {back['top']} on top, row 0; enter, ok, enter: "
             f"{played[0]!r}, {sent['top']} on top, the inbox read again")
    else:
        failures.append(f"  ✗ reply over the inbox        over={over} back={back} sent={sent} {played} {calls}")
    return 0


PROBE = """
import os
from panes.overlays import GestureScreen, InboxScreen
from textual.containers import VerticalScroll
from textual.widgets import OptionList


def names():
    return [type(one).__name__ for one in app.screen_stack]


async def opened(app, pilot):
    while len(app.screen_stack) > 1:
        app.pop_screen()
    await pilot.pause()
    await pilot.press("b")
    return await until(pilot, lambda: isinstance(app.screen, InboxScreen) and bool(app.screen.query("#inbox")))


async def probe(app, pilot, view, out):
    globals()["app"] = app
    out["opened"] = await opened(app, pilot)
    if not out["opened"]:
        return
    screen = app.screen
    listed, whole = screen.query_one("#inbox", OptionList), screen.query_one("#inbox-whole", VerticalScroll)
    tall = next(n for n, line in enumerate(screen.lines) if line[2] == 48)

    async def measured(index):
        listed.highlighted = index
        await pilot.pause()
        await pilot.pause()
        return {"height": whole.region.height, "bar": whole.show_vertical_scrollbar,
                "beyond": whole.virtual_size.height - whole.scrollable_content_region.height}
    out["one"], out["tall"] = await measured(0), await measured(tall)

    # the message as markdown: the post's markdown widget, its looks, no row wider than the pane
    from rich.cells import cell_len
    marked = next(n for n, line in enumerate(screen.lines) if line[2] == 49)
    listed.highlighted = marked
    await pilot.pause()
    await pilot.pause()
    text = screen.query_one("#inbox-text")
    drawn = text.render()
    spans = [(span.start, span.end, getattr(span.style, "rich_style", span.style))
             for span in getattr(drawn, "spans", [])]
    styles = [style for _, _, style in spans if not isinstance(style, str)]
    rows, starts, at = str(drawn).split("\\n"), [], 0
    for row in rows:
        starts.append(at)
        at += len(row) + 1
    shaded = [0] * len(rows)                 # the cells of each row on a background of their own
    for start, end, style in spans:
        if not isinstance(style, str) and style.bgcolor:
            for n, (first, row) in enumerate(zip(starts, rows)):
                shaded[n] += max(0, min(end, first + len(row)) - max(start, first))
    line = screen.lines[marked]
    out["marked"] = {"widget": type(text).__name__,
                     "source": len(line) > 4 and getattr(text, "source", None) == line[4],
                     "bold": any(one.bold for one in styles), "code": any(one.bgcolor for one in styles),
                     "link": any(one.link for one in styles),
                     "borders": sum(1 for row in rows if row.strip() and set(row.strip()) <= set("┌┬┐├┼┤└┴┘─")),
                     "fenced": sum(1 for count in shaded if 2 * count >= text.content_region.width),
                     "rows": len(rows), "source_rows": len(line[4].split("\\n")) if len(line) > 4 else None,
                     "widest": max((cell_len(row) for row in str(drawn).split("\\n")), default=0),
                     "width": text.content_region.width, "bar": whole.show_horizontal_scrollbar,
                     "scroll_x": whole.max_scroll_x}
    out["pane_y"], out["list_y"] = whole.region.y, listed.region.y

    # the pane against the box, at the size asked and at a taller terminal
    async def halved():
        box = screen.query_one("#box")
        return {"size": f"{app.size.width}x{app.size.height}", "box": box.region.height, "pane": whole.region.height,
                "border": whole.styles.border_top[0] not in ("", "none", "hidden"), "title": bool(whole.border_title)}
    width, height = app.size.width, app.size.height
    out["halves"] = [await halved()]
    await pilot.resize_terminal(width, height + 20)
    await pilot.pause()
    await pilot.pause()
    out["halves"].append(await halved())
    await pilot.resize_terminal(width, height)
    await pilot.pause()
    await pilot.pause()

    # a click on the question's row
    listed.highlighted = len(screen.lines) - 1
    await pilot.pause()
    x = listed.content_region.x - listed.region.x + 2
    y = listed.content_region.y - listed.region.y - int(listed.scroll_offset.y)
    await pilot.click("#inbox", offset=(x, y))
    await pilot.pause()
    await pilot.pause()
    top = app.screen
    out["click"] = {"stack": names(), "top": type(top).__name__,
                    "highlighted": top.query_one("#inbox", OptionList).highlighted if isinstance(top, InboxScreen) else None,
                    "gesture": any(isinstance(one, GestureScreen) for one in app.screen_stack),
                    "shown": isinstance(top, InboxScreen)
                             and "tests green?" in str(top.query_one("#inbox-text").render())}

    # enter on the question: the reply over the inbox; escape; enter, ok, enter
    if not await opened(app, pilot):
        return
    app.screen.query_one("#inbox", OptionList).highlighted = 0
    await pilot.pause()
    await pilot.press("enter")
    await until(pilot, lambda: isinstance(app.screen, GestureScreen), 5)
    out["over"] = names()
    await pilot.press("escape")
    await until(pilot, lambda: isinstance(app.screen, InboxScreen), 5)
    top = app.screen
    out["back"] = {"top": type(top).__name__,
                   "highlighted": top.query_one("#inbox", OptionList).highlighted if isinstance(top, InboxScreen) else None}
    if not isinstance(top, InboxScreen):
        return
    await pilot.press("enter")
    if not await until(pilot, lambda: isinstance(app.screen, GestureScreen), 5):
        return
    await pilot.press("o", "k", "ctrl+enter")
    log = os.environ.get("PP_UI_TEAM_LOG", "")

    def calls():
        return open(log, encoding="utf-8").read().splitlines() if log and os.path.isfile(log) else []

    def reread():
        found = calls()
        posted = [n for n, line in enumerate(found) if line.startswith("team post")]
        return bool(posted) and "inbox core-review" in found[posted[0] + 1:]
    await until(pilot, lambda: reread() and isinstance(app.screen, InboxScreen), 8)
    out["sent"] = {"top": type(app.screen).__name__, "stack": names()}
"""
