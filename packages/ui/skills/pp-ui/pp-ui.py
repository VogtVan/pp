#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["textual==8.2.8", "pyyaml>=6"]
# ///
"""pp-ui -- the ENTRY of the post, without Textual.

The console plays this script at the terminal (`tty: true`): the three streams are the
operator's own. This file judges what needs no Textual -- the usage, the arguments,
`tty-missing` -- then RE-EXECUTES itself under `uv run --script`, where the inline
metadata above gives it Textual; the process is replaced (`execvp`) -- under Windows, where
exec would end the process the console waits for, the new one is a child waited for --, so
the streams, the working directory and `PP_HOME` pass as they are. Under that interpreter the same
file opens the post, or renders one pane as text and exits. The agents named open their
conversations ON THE LOOP THE POST RUNS ON, before it draws, and each first event is
waited for: a refusal of the verb (`agent-unknown`, `run-unknown`, `run-busy`) is relayed
in one line, nothing drawn, no second launch. With no agent named, the post opens again
the conversations its memory kept (`memory.recall`) at once, each DORMANT -- no `agent chat`
launched before a gesture speaks to it --, its history read once the post stands.

  pp ui [<agent> ...] [--run <key>] [-- <flags for agent chat>]   the post; `q` closes it -- a `--harness`
                                            after `--` rides `team start` from the Teams tab too, its
                                            `--provider` with it
  pp ui [<agent> ...] --render <pane> [--size WxH] [--press <keys>] [--wait <kind>[:<seconds>]] [--styles]
        [--regions]                         the pane as text, no terminal needed, after the keys
                                            (comma-separated; `wait:<kind>` pauses for one more
                                            event of that kind; `rest:<seconds>` lets that time
                                            pass; `team:<event>` an object of the
                                            Teams tab's watch; `layouts` notes how many times the
                                            transcript was laid out again, `nodes` the widgets of
                                            the last block of the agent's words, `blur` and `focus`
                                            make the application lose and take back the terminal's
                                            focus and note the widget focused, each said on a last
                                            line) and
                                            one more event of `--wait`;
                                            `--styles` keeps the ANSI styles of what is drawn;
                                            `--regions` says where the menu, the folded line and
                                            each band of the centre stand instead
  pp ui --help                              the usage

Refusals are ONE line on stderr, exit 2: tty-missing · pane-unknown · size-invalid ·
press-invalid · wait-invalid · argument-unknown · uv-missing · textual-missing · chat-silent,
and the verb's own relayed as they are.
"""
from __future__ import annotations

import asyncio
import os
import re
import shutil
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import faces  # noqa: E402  (the seam to the verbs: no Textual)
from model import PANE_KEYS, House, Size  # noqa: E402  (pure data: no Textual)

USAGE = ("usage: pp ui [<agent> ...] [--run <key>] [--render <pane> [--size WxH] [--press <keys>] "
         "[--wait <kind>[:<seconds>]] [--styles] [--regions]] [--help] [-- <flags for agent chat>] -- the post of the house "
         "on its terminal (q closes it); each agent named opens its conversation in a tab (--run resumes "
         "a run of the last one); --render prints a pane as text and exits, after the comma-separated "
         "keys are pressed (--styles: with their ANSI styles)")
REEXEC_MARK = "PP_UI_REEXEC"         # set on the re-executed process: a second miss is a refusal
FIRST_EVENT_WAIT = 10.0              # seconds the first event of a conversation gets before `chat-silent`
CODE = re.compile(r"\b([a-z]+(?:-[a-z]+)+)\b")   # the first kebab word of a refusal: its code


@dataclass(frozen=True)
class Ask:
    render: str | None               # the pane to print, None to open the post
    size: Size
    press: tuple[str, ...]           # the keys pressed before the pane is printed
    agents: tuple[tuple[str, str | None], ...]   # (agent, run) of each conversation to open, in order
    wait: str | None                 # the kind `--render` waits one more of
    seconds: float                   # how long it waits
    flags: tuple[str, ...]           # what goes to `agent chat` as it is
    styles: bool = False             # `--render` keeps the ANSI styles of the screen
    regions: bool = False            # `--render` says where the parts of the pane stand


def refuse(code: str, detail: str) -> int:
    sys.stderr.write(f"pp-ui: {code} -- {detail}\n")
    return 2


def parse(argv: list[str]) -> Ask | int:
    """-> the Ask the words make, or the exit code of the refusal they earn."""
    words = list(argv)
    flags: tuple[str, ...] = ()
    if "--" in words:
        at = words.index("--")
        words, flags = words[:at], tuple(words[at + 1:])
    render, size, press, wait, styles, regions = None, "80x24", "", "", False, False
    agents: list[tuple[str, str | None]] = []
    while words:
        word = words.pop(0)
        if word in ("-h", "--help"):
            print(USAGE)
            return 0
        if word == "--render" and words:
            render = words.pop(0)
        elif word == "--size" and words:
            size = words.pop(0)
        elif word == "--press" and words:
            press = words.pop(0)
        elif word == "--run" and words and agents:
            agents[-1] = (agents[-1][0], words.pop(0))
        elif word == "--wait" and words:
            wait = words.pop(0)
        elif word == "--styles":
            styles = True
        elif word == "--regions":
            regions = True
        elif not word.startswith("-"):
            agents.append((word, None))
        else:
            return refuse("argument-unknown", f"`{word}` -- {USAGE}")
    if render is not None and render not in PANE_KEYS:
        return refuse("pane-unknown", f"`{render}` -- the panes are {', '.join(PANE_KEYS)}")
    parsed = Size.parse(size)
    if parsed is None:
        return refuse("size-invalid", f"`{size}` -- WxH, at least {Size.MIN_WIDTH}x{Size.MIN_HEIGHT}")
    keys = tuple(one.strip() for one in press.split(",") if one.strip())
    if press and not keys:
        return refuse("press-invalid", f"`{press}` -- comma-separated key names, `2,3` or `tab`")
    for one in keys:
        if one.startswith("rest:"):
            try:
                rested = float(one[len("rest:"):]) > 0
            except ValueError:
                rested = False
            if not rested:
                return refuse("press-invalid", f"`{one}` -- `rest:<seconds>`, a number above 0")
    team = "team:" if wait.startswith("team:") else ""        # `team:<event>`: an object of the Teams tab's watch
    kind, seconds = (wait[len(team):].split(":", 1) + [""])[:2] if wait else ("", "")
    kind = team + kind if kind else ""
    try:
        bound = float(seconds) if seconds else 10.0
    except ValueError:
        bound = -1.0
    if wait and (not kind or bound <= 0):
        return refuse("wait-invalid", f"`{wait}` -- `<kind>` or `<kind>:<seconds>`, `waiting:30`")
    return Ask(render, parsed, keys, tuple(agents), kind or None, bound, flags, styles, regions)


def house_here() -> House:
    """The house is named by `PP_HOME` (the instance the console serves: its parent is the
    house), by the working directory when the script is run by hand."""
    home = os.environ.get("PP_HOME")
    root = Path(home).resolve().parent if home else Path.cwd()
    return House.at(root)


def reexec(argv: list[str], system: str = os.name) -> int:
    """The same script under uv, which carries Textual: in this process's place where the system allows it,
    else a child waited for -- a Ctrl-C is the child's while it plays -- whose exit code is given back."""
    if os.environ.get(REEXEC_MARK):
        return refuse("textual-missing", "uv ran the script without Textual -- no cache and no "
                                         "network reach `textual==8.2.8`")
    if shutil.which("uv") is None:
        return refuse("uv-missing", "`uv` is not on the PATH; the post needs it for Textual")
    os.environ[REEXEC_MARK] = "1"
    command = ["uv", "run", "--quiet", "--script", str(HERE / "pp-ui.py"), *argv]
    if faces.in_place(system):
        os.execvp("uv", command)
    previous = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        return subprocess.call(command)
    finally:
        signal.signal(signal.SIGINT, previous)


def relayed(opening, agent: str) -> int:
    """-> the exit code of the verb's refusal, said in one line: the first stderr line that
    names a code (uv may speak first), or `chat-silent` when nothing came."""
    if opening.silent:
        return refuse("chat-silent", f"`agent chat {agent} --json` said nothing in {FIRST_EVENT_WAIT:.0f}s")
    first = opening.first
    said = [one for one in str(first.fields.get("stderr", "")).splitlines() if one.strip()]
    bodies = [(one, re.sub(r"^[\w.-]+:\s*", "", one)) for one in said]   # `pp-agent: <code> -- …`
    named = next(((one, body) for one, body in bodies if CODE.search(body)), None)
    line, body = named or ((said[0], said[0]) if said else (f"exit {first.fields.get('rc')}",) * 2)
    found = CODE.search(body)
    return refuse(found.group(1) if found else "chat-ended", line)


def once(pairs) -> list[tuple[str, str | None]]:
    """-> the (agent, run) pairs, a run kept at its first place alone; a pair without a run (a new
    conversation) stays as many times as it is asked."""
    seen: set = set()
    kept = []
    for agent, run in pairs:
        if run and (agent, run) in seen:
            continue
        seen.add((agent, run))
        kept.append((agent, run))
    return kept


async def play(house: House, ask: Ask) -> int:
    """Opens each conversation named on this loop, then the post on the same loop -- or, none named, gives the post
    each conversation the memory kept, DORMANT, nothing read nor launched before the post stands: the post reads
    their histories once it is drawn; a run named twice opens once."""
    import memory
    from app import PostApp
    from faces.chat import Conversation, Opening, opened
    from faces.team import close_all as close_watches
    from render import rendered
    openings, histories = [], []
    named = once(ask.agents)
    agents: list[tuple[str, str | None]] = list(named)
    for agent, run in named:
        opening = await opened(house.root, agent, run, ask.flags, FIRST_EVENT_WAIT)
        if opening.silent or opening.refused:
            for one in openings:
                await one.conversation.close(timeout=1.0)
            await opening.conversation.close(timeout=1.0)
            return relayed(opening, agent)
        openings.append(opening)
    theme, note, kept = await asyncio.to_thread(lambda: (memory.theme(), memory.relaunched(),
                                                         [] if ask.agents else memory.recall()))
    if not ask.agents:
        for agent, run in once(kept):
            dormant = Conversation(house.root, agent, run, ask.flags)
            openings.append(Opening(dormant, dormant.events(), None))
            histories.append(None)               # read by the post once it stands
            agents.append((agent, run))
    app = PostApp(house, openings, agents, ask.flags, histories, theme, note)
    try:
        if ask.render is not None:
            sys.stdout.write(await rendered(app, ask.render, ask.size, ask.press, ask.wait, ask.seconds,
                                            ask.styles, ask.regions))
            return int(app.return_code or 0)     # a gesture that asked the console a verb leaves on its code
        await app.run_async()
        return int(app.return_code or 0)
    finally:
        await app.flushed()                    # the writes of the memory asked, done before the post leaves
        for one in openings:                   # `q` closed them already; a crash does not leave one
            await one.conversation.close(timeout=1.0)
        await close_watches()                  # the Teams tab's watch, ended whole


def main(argv: list[str]) -> int:
    ask = parse(argv)
    if isinstance(ask, int):
        return ask
    if ask.render is None and not (sys.stdin.isatty() and sys.stdout.isatty()):
        return refuse("tty-missing", "the post draws on a terminal: run `pp ui` from one, or ask "
                                     "`--render <pane> --size WxH` for the text of a pane")
    try:
        import textual  # noqa: F401  -- present under the re-executed interpreter alone
    except ImportError:
        return reexec(argv)
    return asyncio.run(play(house_here(), ask))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
