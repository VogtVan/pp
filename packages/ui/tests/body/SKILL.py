"""packages/ui/skills/pp-ui/SKILL.md -- the text it keeps: the description `./pp help` prints,
the calls, what the post needs, the refusals by name."""
from __future__ import annotations

from tests.harness import SOURCE, body_of, kept_document


def scenario(bench) -> int:
    doc = kept_document(SOURCE / "packages" / "ui", "SKILL")
    raw = doc.read_text(encoding="utf-8")
    front = raw.split("\n---\n", 1)[0]
    text = " ".join(body_of(doc).split())

    assert "name: pp-ui" in front
    assert "A main, not an engine" in front and "`tty-missing`" in front
    bench.held("the contract names the skill and its nature", "name pp-ui; the description says a main, "
               "not an engine, and the refusal without a terminal")

    for phrase in ("`./pp ui`", "`./pp ui --render <pane> --size WxH`", "`q` closes it",
                   "`./pp ui --render <pane> --press <keys>`", "from 40x8 up",
                   "`./pp ui <agent> [<agent> ...] [--run <key>] [-- <flags>]`", "ONE line of the CONDUCTION",
                   "opens WHOLE in an overlay on `enter` or a click", "`c` hides the lines of conduction", "ONE line per call of a tool (`⚙`", "rendered as markdown", "`ctrl+c` copies the selection",
                   "switching tabs reloads nothing", "`x` closes the tab",
                   "the table of the agents of the house", "`agent stats --json`",
                   "`1·Dialogue`, `2·Agents`, `3·Teams`", "the name of a run is asked in the overlay of its parameters", "`shift+enter`", "its NAME the last field",
                   "followed by how long the turn has run", "bold red at the cap",
                   "the bubble says the principal's message of the turn at", "read after each verdict",
                   "at most one per team, shared by the two tabs", "`N` gives birth to a team from a template", "`enter` opens the task's THREAD in an overlay",
                   "its kept flow (`agent flow --json`) replayed as lived turns", "as markdown, any other content as the text it is",
                   "on as many lines as the width asks",
                   "`P` purges the run under the cursor", "A purge is shown before it plays",
                   "`./pp ui` with no agent named opens them again",
                   "or `ctrl+g` sends `stop` during an exchange", "`escape` never stops a turn",
                   "`textual==8.2.8`", "The engine never imports it",
                   "a spinner turns on the tab's title", "`enter` waits: it sends nothing until the turn ended",
                   "ONE profile, `ProfileScreen`, wherever the post launches something", "`S` on a team opens one profile per line of its season", "the CHANGED parameters as a `set`", "`./pp agent add <path>` shown",
                   "`o` suspends the conduction of the conversation", "`k` opens the run's packages",
                   "`t` opens the list of Textual's themes", "the house itself first (`.`, named by its folder",
                   "Both tabs PILOT by the verbs of `team` alone", "a MENU on the left and a CENTRE of horizontal bands", "once its name is typed", "opens its run READ in a tab of the dialogue", "The team's ONE `team watch <name> --json`",
                   "its LAST ACTION", "is WRITTEN in an overlay, `GestureScreen`", "`B` raises its budget",
                   "`b` shows the owner's inbox", "`e` its declaration",
                   "`g` there rings the ceremony at hand (`team ring`)",
                   "its `--harness` rides `team start` when `S` starts a team"):
        assert phrase in text, phrase
    for refusal in ("tty-missing", "pane-unknown", "size-invalid", "press-invalid", "wait-invalid",
                    "argument-unknown", "uv-missing", "textual-missing", "chat-silent", "agent-unknown"):
        assert f"`{refusal}`" in text, refusal
    bench.held("the contract says the calls and the refusals", "open, the dialogue on an agent, render, press, "
               "wait, help; nine named refusals and the verb's own, one line on stderr, exit 2")
    return 0
