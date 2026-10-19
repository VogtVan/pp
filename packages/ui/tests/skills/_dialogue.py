"""_dialogue -- what the scenarios of the post of conversations share (rule 10): the witness
`pp-chat` posed under PP_UI_FACES with one scripted flow per agent, the journal of its
launches, a house pinning `ui`, the renders of the post, and the post's memory of the
conversations it keeps open -- forgotten before each render unless a case keeps it."""
from __future__ import annotations

import ast
import json
import re
import shutil
from pathlib import Path

from conductor import metadata
from tests.harness import SOURCE, cli

# The provider the post's faces name, and its models: names of fixture -- the post reads faces, never an
# adapter, so no provider of the product is named here (KA12).
PROVIDER = "prov"
MODELS = ["prov-large-5", "prov-small-5"]

WITNESS = SOURCE / "packages" / "ui" / "tests" / "witness" / "pp-chat"
CONDUCTION = "▌ pp · run w00001 · 10:00:00 · +0:00:01\n▌ BOOT ▸ MEMBER ▸ TURN{2/4}\n\n▌ INSTRUCTION\nWORK any => response"
LONG = "\n".join(f"line {n:02d} of the output -- " + "a reading served whole, " * 6 for n in range(1, 80)) \
    + "\nline 80 -- the end of the output"


def conduction(exchange: int, launch: int, text: str = CONDUCTION, parked: bool = False) -> dict:
    """A `conduction` as `agent` says it: its text, its size, the blocks the trace wrote for it."""
    stack = "BOOT ▸ MEMBER ▸ TURN{4/4}" if parked else "BOOT ▸ MEMBER ▸ TURN{2/4}"
    return {"kind": "conduction", "exchange": exchange, "launch": launch, "text": text, "chars": len(text),
            "blocks": [{"stack": "BOOT ▸ MEMBER ▸ CAPABILITIES{2/2}", "command": "./pp w00001", "wait": False},
                       {"stack": stack, "command": "./pp w00001", "wait": parked}]}


def script(run: str, said: str, pause: float = 0.0, cap: dict | None = None) -> dict:
    """One agent's flow: `ready` and `waiting` at once, then two exchanges (the second never ends: it waits for
    `stop`); the principal's line always reads `hi`, whatever was typed -- the witness replays a script."""
    first = [{"kind": "opened", "agent": "agents/ag", "exchange": 1, "resumed": False, "standing": False,
              "provider": PROVIDER, "policy": {"model": "m1"}, **({"cap": cap} if cap else {})},
             {"kind": "principal", "exchange": 1, "text": "hi"}]
    if pause:
        first.append({"sleep": pause})
    first += [{"kind": "step", "event": "launch", "launch": 1, "chars": 1200},
              conduction(1, 1),
              {"kind": "words", "exchange": 1, "launch": 1, "text": f"{said} one"},
              {"kind": "agent", "exchange": 1, "launch": 1, "cost_usd": 0.01},
              {"kind": "step", "event": "refusal", "code": "budget"},
              {"kind": "step", "event": "repair", "n": 1},
              conduction(1, 2, parked=True),
              {"kind": "words", "exchange": 1, "launch": 2, "text": f"{said} two"},
              {"kind": "agent", "exchange": 1, "launch": 2, "cost_usd": 0.02},
              {"kind": "response", "index": 1, "response": f"{said} one\n\n{said} two", "state": "parked"},
              {"kind": "verdict", "exchange": 1, "state": "parked", "cost_usd": 0.03, "launches": 2},
              {"kind": "waiting"}]
    second = [{"kind": "principal", "exchange": 2, "text": "go"},
              conduction(2, 1)]
    ready = {"kind": "ready", "agent": "agents/ag", "resumed": False, "provider": PROVIDER, "policy": {"model": "m1"},
             "conducted": True, **({"cap": cap} if cap else {})}
    return {"run": run, "provider": PROVIDER, "policy": {"model": "m1"}, "opening": [ready, {"kind": "waiting"}],
            "exchanges": [first, second],
            "stopped": [{"kind": "verdict", "exchange": 2, "state": "interrupted", "launches": 1,
                         "reason": "interrupted"}, {"kind": "waiting"}]}


FACES = {
    "list": [{"agent": "ag1", "runs": 2, "running": 0, "responses": 3,
              "weight": {"lines": 9, "files": 4, "bytes": 1200000, "flow": 34000}},
             {"agent": "ag2", "runs": 1, "running": 0, "responses": 1,
              "weight": {"lines": 2, "files": 1, "bytes": 812, "flow": None}}],
    "status": {
        "ag1": [{"agent": "ag1", "run": "w00001", "name": "", "exchanges": 2, "state": "parked", "stack": "",
                 "session": "s-1", "provider": "harness", "cost_usd": 0.25, "launches": 5, "responses": 2,
                 "first_message": "hello there", "first_at": "2026-10-08T09:00:00+00:00", "last_at": "2026-10-08T09:05:00+00:00",
                 "context": {"tokens": 170000, "used": 0.17, "pp": 0.3294},
                 "weight": {"lines": 9, "files": 4, "bytes": 1200000, "flow": 34000}},
                {"agent": "ag1", "run": "w00009", "name": "", "exchanges": 1, "state": "standing", "stack": "TURN",
                 "session": "s-2", "provider": "harness", "cost_usd": 0.1, "launches": 2, "responses": 1,
                 "first_message": "later", "first_at": "2026-10-08T10:00:00+00:00", "last_at": "2026-10-08T10:01:00+00:00",
                 "context": {"tokens": 6800, "used": None, "pp": 0.98}},
                {"agent": "ag1", "providers": [PROVIDER], "last": {"provider": PROVIDER, "policy": {"model": "m1"}},
                 "packages": [{"name": "plan", "on": True}, {"name": "steering", "on": True}]}],
        "ag2": [{"agent": "ag2", "run": "w00002", "name": "", "exchanges": 1, "state": "parked", "stack": "",
                 "session": "s-3", "provider": "harness", "cost_usd": None, "launches": 1, "responses": 1,
                 "first_message": "yo", "first_at": "2026-10-08T11:00:00+00:00", "last_at": "2026-10-08T11:00:30+00:00",
                 "context": None},
                {"agent": "ag2", "providers": [PROVIDER], "last": None}]},
    "purge": {"ag1": {"runs": {"w00001": {"key": "w00001", "lines": {"responses.jsonl": 2, "messages.jsonl": 2},
                                          "files": ["session-w00001.json", "session-w00001.jsonl"],
                                          "bytes": 1200000, "workdir": None, "flow": 34000},
                               "w00009": {"key": "w00009", "lines": {"responses.jsonl": 1, "messages.jsonl": 1},
                                          "files": ["session-w00009.json"], "bytes": 812, "workdir": None,
                                          "flow": None}},
                      "before": {"2026-10-09": ["w00001", "w00009"]}}},
    "providers": [{"provider": PROVIDER, "spells": ["model", "max_budget_usd", "permissions", "effort"],
                   "models": list(MODELS)}],
    "exchanges": {"ag1": {"w00001": [
        {"agent": "ag1", "run": "w00001", "index": 1, "at": "2026-10-08T09:00:00+00:00", "message": "hello there",
         "response": "witness answer: play", "cost_usd": 0.19, "launches": 3, "error": None, "harness_rc": 0},
        {"agent": "ag1", "run": "w00001", "index": 2, "at": "2026-10-08T09:05:00+00:00", "message": "and again",
         "response": None, "cost_usd": None, "launches": None, "error": None, "harness_rc": None}]}},
    "stats": {"ag1": {"w00001": {"agent": "ag1", "run": "w00001", "cost_usd": 0.25, "launches": 5, "exchanges": 2,
                                 "conduction": {"key": "w00001", "exchanges": 2, "blocks": 9, "chunks": 4, "proofs": 2,
                                                "repairs": 0, "refusals": 1, "gestures": 3, "mass": 12000, "tokens": 3000,
                                                "spent": {"work": 10.5, "proof": 2.0, "gesture": 1.0, "answer": 3.0}},
                                 "context": {"flow": {"principal": 400, "conduction": 50000, "pp_input": 2000,
                                                      "pp_result": 4000, "tool_input": 3000, "tool_result": 100000,
                                                      "words": 8000, "thinking": 2600, "total": 170000},
                                             "window": 1000000, "used": 0.17,
                                             "pp": {"tokens": 56000, "share": 0.3294, "served": 54000},
                                             "calls": 42, "reread": 3600000, "since": None}},
                      "w00009": {"agent": "ag1", "run": "w00009", "cost_usd": 0.1, "launches": 2, "exchanges": 1,
                                 "conduction": {"key": "w00009", "exchanges": 1, "blocks": 4, "tokens": 900,
                                                "spent": {"work": 3725, "proof": 303, "answer": 12.34}},
                                 "context": None}}},
}
SCRIPT = {"agents": {"ag1": script("w00001", "the agent says", pause=0.4),
                     "ag2": script("w00002", "two says"),
                     "ag3": script("w00003", "three says", pause=2.0),   # a turn long enough to be seen
                     "ag4": script("w00004", "four says", cap={"set": 20000, "applied": 200000}),   # a raised cap
                     "ag5": script("w00005", "five says", cap={"set": 200000, "applied": 200000})},
          "faces": FACES}


MARKDOWN = ("Here is the plan:\n\n| step | state |\n|---|---|\n| frame | done |\n| build | doing |\n\n"
            "```python\nprint(\"hello\")\n```\n")


def long_script() -> dict:
    """`ag1`'s flow whose second conduction is 80 lines long, each wider than the screen -- what an
    overlay must show whole, folded to its width --, and whose second launch says one step."""
    flow = script("w00001", "the agent says")
    first = []
    for one in flow["exchanges"][0]:
        if one.get("kind") == "conduction" and one.get("launch") == 2:
            first += [conduction(1, 2, LONG, parked=True),
                      {"kind": "step", "event": "block", "stack": "BOOT ▸ MEMBER ▸ TURN{4/4}", "wait": True}]
        else:
            first.append(one)
    flow["exchanges"][0] = first
    return {"agents": {"ag1": flow}, "faces": FACES}


ANSWER = "\n".join(f"answer line {n:02d} -- " + "the agent explains at length, " * 2 for n in range(1, 80)) \
    + "\nanswer line 80 -- the end of the answer"


def long_answer_script() -> dict:
    """`ag1`'s flow whose first launch says 4k characters over 80 lines -- the block of its words, whole."""
    flow = script("w00001", "the agent says")
    for event in flow["exchanges"][0]:
        if event.get("kind") == "words" and event.get("launch") == 1:
            event["text"] = ANSWER
    return {"agents": {"ag1": flow}, "faces": FACES}


PRODUCTIONS = ("the first production", "the second production", "the third production")


def words_script() -> dict:
    """`ag1`'s flow whose first launch says three productions -- three `words`, one launch, as a fused block is
    said --, its response their composition."""
    flow = script("w00001", "the agent says")
    first = []
    for one in flow["exchanges"][0]:
        if one.get("kind") == "words" and one.get("launch") == 1:
            first += [{"kind": "words", "exchange": 1, "launch": 1, "text": text} for text in PRODUCTIONS]
            continue
        if one.get("kind") == "response":
            one = {**one, "response": "\n\n".join(PRODUCTIONS + ("the agent says two",))}
        first.append(one)
    flow["exchanges"][0] = first
    return {"agents": {"ag1": flow}, "faces": FACES}


EMOJI_TABLE = "| step | state |\n|---|---|\n| \U0001F6E0\uFE0F build | done |\n| \U0001F680 ship | doing |\n"


QUESTIONS = ("the first question", "the second question", "the third question")


def turns_script() -> dict:
    """`ag1`'s flow of three turns that each end, their messages `QUESTIONS` in order and each last words `ANSWER`, 80
    lines long -- a transcript taller than the screen, whose turn at the top of the view changes as it scrolls."""
    flow = script("w00001", "the agent says")
    turns = []
    for number, question in enumerate(QUESTIONS, start=1):
        turn = [dict(one) for one in flow["exchanges"][0]]
        for one in turn:
            if "exchange" in one:
                one["exchange"] = number
            if one.get("kind") == "principal":
                one["text"] = question
            if one.get("kind") == "words" and one.get("launch") == 2:
                one["text"] = ANSWER
            if one.get("kind") == "response":
                one["response"] = ANSWER
        turns.append(turn)
    flow["exchanges"] = turns
    return {"agents": {"ag1": flow}, "faces": FACES}


def emoji_script() -> dict:
    """`ag1`'s flow whose last words are a table of two rows: one opens on an emoji \"text by default\" with its
    selector `U+FE0F` (🛠️), the other on an emoji \"emoji by default\" (🚀)."""
    flow = script("w00001", "the agent says")
    for event in flow["exchanges"][0]:
        if event.get("kind") == "words" and event.get("launch") == 2:
            event["text"] = EMOJI_TABLE
        if event.get("kind") == "response":
            event["response"] = EMOJI_TABLE
    return {"agents": {"ag1": flow}, "faces": FACES}


def emoji_answer_script() -> dict:
    """`ag1`'s flow whose first launch says the table of `EMOJI_TABLE` -- the block of its words, its rows drawn
    on the terminal's columns."""
    flow = script("w00001", "the agent says")
    for event in flow["exchanges"][0]:
        if event.get("kind") == "words" and event.get("launch") == 1:
            event["text"] = EMOJI_TABLE
    return {"agents": {"ag1": flow}, "faces": FACES}


def markdown_script() -> dict:
    """`ag1`'s flow whose second launch says markdown -- a table of two columns and a block of code."""
    flow = script("w00001", "the agent says")
    for event in flow["exchanges"][0]:
        if event.get("kind") == "words" and event.get("launch") == 2:
            event["text"] = MARKDOWN
        if event.get("kind") == "response":
            event["response"] = MARKDOWN
    return {"agents": {"ag1": flow}, "faces": FACES}


def tools_script() -> dict:
    """`ag1`'s flow whose first launch, after its conduction, says what the agent did -- a call of pp and its
    result, two counts of thought (50 then 188 tokens) then its text (a thought to open: a count alone is
    stale, `ui-stale`), a `Read` whose result is an error, then words -- the launch's own words follow them."""
    flow = script("w00001", "the agent says")
    calls = [{"kind": "tool", "exchange": 1, "launch": 1, "id": "t1", "name": "Bash", "title": "./pp w00001 -",
              "shell": "./pp w00001 -", "input": {"command": "./pp w00001 -"}, "pp": True},
             {"kind": "tool-result", "exchange": 1, "launch": 1, "id": "t1", "content": "proof taken\nheld 3 codes",
              "error": False},
             {"kind": "thinking", "exchange": 1, "launch": 1, "tokens": 50},
             {"kind": "thinking", "exchange": 1, "launch": 1, "tokens": 188},
             {"kind": "thinking", "exchange": 1, "launch": 1, "text": "the proof first"},
             {"kind": "tool", "exchange": 1, "launch": 1, "id": "t2", "name": "Read", "title": "/nowhere/file.md",
              "shell": None, "input": {"file_path": "/nowhere/file.md"}, "pp": False},
             {"kind": "tool-result", "exchange": 1, "launch": 1, "id": "t2", "content": "File does not exist.",
              "error": True},
             {"kind": "words", "exchange": 1, "launch": 1, "text": "let me read the proof"}]
    first = []
    for one in flow["exchanges"][0]:
        first.append(one)
        if one.get("kind") == "conduction" and one.get("launch") == 1:
            first += calls
    flow["exchanges"][0] = first
    return {"agents": {"ag1": flow}, "faces": FACES}


THOUGHT = "I weigh the proof before I pipe it"


def thinking_script() -> dict:
    """`ag1`'s flow where each launch thinks: launch 1 says a count alone (`~42 tokens`, nothing to show), launch 2
    a count then its text -- the same line judged again when the text comes."""
    flow = script("w00001", "the agent says")
    first = []
    for one in flow["exchanges"][0]:
        first.append(one)
        if one.get("kind") == "conduction" and one.get("launch") == 1:
            first.append({"kind": "thinking", "exchange": 1, "launch": 1, "tokens": 42})
        if one.get("kind") == "conduction" and one.get("launch") == 2:
            first += [{"kind": "thinking", "exchange": 1, "launch": 2, "tokens": 30},
                      {"kind": "thinking", "exchange": 1, "launch": 2, "text": THOUGHT}]
    flow["exchanges"][0] = first
    return {"agents": {"ag1": flow}, "faces": FACES}


def budget_script(spent: list[float], cap: float | None = 2.0) -> dict:
    """`ag1`'s flow where the run has a budget: `ready` says it untouched, then each exchange's `opened` and
    `verdict` say it spent as `spent` gives it, one value per exchange (agent 0.19.0: `budget {cap, spent, left}`,
    `null` without a cap)."""
    flow = script("w00001", "the agent says")

    def said(used: float) -> dict | None:
        return None if cap is None else {"cap": cap, "spent": used, "left": round(cap - used, 6)}
    flow["opening"][0]["budget"] = said(0.0)
    exchanges = []
    for number, used in enumerate(spent, start=1):
        turn = [dict(one) for one in flow["exchanges"][0]]
        for one in turn:
            if "exchange" in one:
                one["exchange"] = number
            if one.get("kind") == "opened":
                one["budget"] = said(spent[number - 2] if number > 1 else 0.0)
            if one.get("kind") == "verdict":
                one["budget"] = said(used)
        exchanges.append(turn)
    flow["exchanges"] = exchanges
    return {"agents": {"ag1": flow}, "faces": FACES}


def heads_of(text: str) -> list[str]:
    """-> the heads of the principal's blocks in the transcript of a capture: `▶ HH:MM:SS` alone on its row, its
    message on the row under it -- the bubble, whose message stands on its own row, left out."""
    return [row for row in text.split("\n") if re.fullmatch(r"\s*▶ \d\d:\d\d:\d\d\s*", row)]


def keys_rows(text: str) -> list[str]:
    """-> the lines of the footer's keys, top first: the footer grows when the width does not hold them all,
    its keys lines standing above the remedy and the status, each opening on `[` or on the label of a group of keys
    (`member:`)."""
    lines = text.rstrip("\n").split("\n")[:-2]
    found: list[str] = []
    while lines and re.match(r"(\[|[a-z]+: )", lines[-1].strip()):
        found.insert(0, lines.pop().strip())
    return found


def keys_of(text: str) -> str:
    """-> the keys of the footer, every line of them joined by ` · `."""
    return " · ".join(keys_rows(text))


def entry_of(text: str, key: str) -> str:
    """-> the entry of the footer that `key` opens (`[b] …`), up to the next entry -- what a toggle changes; '' when the
    footer offers no such key."""
    found = re.search(rf"\[{re.escape(key)}\]([^\[]*?)(?: · |$)", keys_of(text))
    return found.group(0).rstrip(" ·") if found else ""


def switched(agent: str, name: str, on: bool) -> str:
    """-> the line the witness journals for a package switched: the verb, the agent, the JSON it was sent."""
    return f"package {agent} {json.dumps({'name': name, 'on': on})}"


def title_of(text: str) -> list[str]:
    """-> the title of the overlay of a capture: its first rows of text inside the border, up to the first blank row."""
    rows = text.split("\n")
    top = next((n for n, row in enumerate(rows) if "┏" in row and "┓" in row), -1)
    if top < 0:
        return []
    left, right = rows[top].index("┏"), rows[top].index("┓")
    found: list[str] = []
    for row in rows[top + 1:]:
        inner = row[left + 1:right].strip() if len(row) > right else ""
        if not inner and not found:
            continue                              # the box's padding above the title
        if not inner or inner.startswith("━"):
            break
        found.append(inner)
    return found


def overlay_rows(text: str) -> list[str]:
    """-> the rows inside the overlay's border of a capture, each stripped -- the screen around it left out."""
    rows = text.split("\n")
    top = next((n for n, row in enumerate(rows) if "┏" in row and "┓" in row), -1)
    if top < 0:
        return []
    left, right = rows[top].index("┏"), rows[top].index("┓")
    found: list[str] = []
    for row in rows[top + 1:]:
        if len(row) <= right or row[left] == "┗":
            break
        found.append(row[left + 1:right].strip(" │").strip())
    return found


def on_top(text: str) -> str:
    """-> the capture from the top of the overlay drawn last on: the readers of an overlay read it."""
    rows = text.split("\n")
    tops = [n for n, row in enumerate(rows) if "┏" in row and "┓" in row]
    return "\n".join(rows[tops[-1]:]) if tops else ""


def field_of(rows: list[str], name: str) -> list[str]:
    """-> the lines inside the box of the field `name` of a form's overlay rows, a list's arrow left out."""
    at = next((n for n, row in enumerate(rows) if row == field_title(name)), None)
    if at is None or at + 1 >= len(rows) or not rows[at + 1].startswith("┌"):
        return []
    found = []
    for row in rows[at + 2:]:
        if row.startswith("└"):
            return found
        found.append(row.rstrip("▼").strip())
    return []


def under_fields(rows: list[str]) -> list[str]:
    """-> what a form says under its fields: the rows past the last box and its help, up to its keys."""
    last = max((n for n, row in enumerate(rows) if row.startswith("└")), default=None)
    if last is None:
        return []
    rest = rows[last + 1:]
    help_end = next((n for n, row in enumerate(rest) if not row), len(rest))
    return [row for row in rest[help_end:] if row and not row.startswith("[")]


def status_of(text: str) -> str:
    """-> the status line of a capture: its last row."""
    return text.rstrip("\n").split("\n")[-1]


def remedy_of(text: str) -> str:
    """-> the remedy line of a capture: the row above the status."""
    rows = text.rstrip("\n").split("\n")
    return rows[-2].strip() if len(rows) >= 2 else ""


SGR = re.compile(r"\x1b\[([0-9;]*)m")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")          # every control sequence of a `--styles` capture


def styles_of(text: str, pattern: str) -> frozenset:
    """-> the styles (SGR sequences) the first row of a `--styles` capture matching `pattern` is drawn with --
    the signature of a line's look, compared with another's; empty when no row matches."""
    for row in text.split("\n"):
        if re.search(pattern, SGR.sub("", row)):
            return frozenset(SGR.findall(row)) - {"0", ""}
    return frozenset()


PALETTE = SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "palette.py"


def palette_constant(name: str) -> str:
    """-> the string constant `name` of `palette.py`, read from its source: the module imports rich and textual,
    which the bench's interpreter lacks."""
    for node in ast.parse(PALETTE.read_text(encoding="utf-8")).body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name and isinstance(node.value, ast.Constant):
                return node.value.value
            if isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                for one, value in zip(target.elts, node.value.elts):
                    if isinstance(one, ast.Name) and one.id == name and isinstance(value, ast.Constant):
                        return value.value
    raise KeyError(name)


def field_title(name: str) -> str:
    """-> the title a form gives the field `name`, as `palette.field_title` makes it: its first letter in capital."""
    return name[:1].upper() + name[1:]


def bold_in(styles: frozenset) -> bool:
    """-> whether a look (`styles_of`) is bold."""
    return any("1" in one.split(";") for one in styles)


def keep_theme(made: Path, name: str) -> None:
    """Writes the theme the post was left in into a throwaway house's memory -- the bench's own hand, as `forget`."""
    path = metadata.path_of(made)
    kept = json.loads(path.read_text(encoding="utf-8") or "{}") if path.is_file() else {}
    kept["ui"] = {"theme": name}
    path.write_text(json.dumps(kept), encoding="utf-8")


PACKAGES = [{"name": "plan", "on": True}, {"name": "steering", "on": True}]


def conduct_script() -> dict:
    """`ag1`'s flow as the suspension sees it: `opened` says the run's packages -- `ghost` among
    them, a name the witness's own list lacks, so that choosing it is refused `package-unknown` --,
    and every message after `conduct off` replays a BARE exchange (one answer, no conduction, no
    step, the verdict `unconducted`); `ag2`'s `opened` says no packages, a flow from before them."""
    flow = script("w00001", "the agent says")
    flow["exchanges"][0][0]["packages"] = [dict(one) for one in PACKAGES] + [{"name": "ghost", "on": True}]
    flow["opening"][0]["packages"] = [dict(one) for one in PACKAGES] + [{"name": "ghost", "on": True}]
    flow["packages"] = [dict(one) for one in PACKAGES]
    flow["unconducted"] = [{"kind": "principal", "exchange": 2, "text": "go"},
                           {"kind": "words", "exchange": 2, "launch": 1, "text": "bare answer"},
                           {"kind": "agent", "exchange": 2, "launch": 1, "cost_usd": 0.01},
                           {"kind": "response", "index": 2, "response": "bare answer", "state": "unconducted"},
                           {"kind": "verdict", "exchange": 2, "state": "unconducted", "cost_usd": 0.01, "launches": 1},
                           {"kind": "waiting"}]
    return {"agents": {"ag1": flow, "ag2": script("w00002", "two says")}, "faces": FACES}


def held_script() -> dict:
    """`conduct_script`'s flows, where a switch of `steering` WAITS for the next message (`held`), as a run whose
    view holds the package makes it wait at `agent`; a switch of `plan` plays at once."""
    script = conduct_script()
    script["agents"]["ag1"]["held"] = ["steering"]
    return script


def refusing(stderr: str) -> dict:
    """An agent's flow that the verb refuses before any event: the witness says `stderr` and
    exits 2, as `agent chat` does on `run-busy` or `provider-ambiguous`."""
    return {"refuse": stderr}


def forget(made: Path) -> None:
    """Takes the post's memory out of a throwaway house: the space `ui` of its metadata, so
    that a render without an agent named opens on nothing (the bench's own hand on its house)."""
    path = metadata.path_of(made)
    if path.is_file():
        kept = json.loads(path.read_text(encoding="utf-8") or "{}")
        kept.pop("ui", None)
        path.write_text(json.dumps(kept), encoding="utf-8")


def remembered(made: Path) -> list:
    """-> the conversations the post keeps open, as the engine reads its space `ui`."""
    return metadata.of_package(made, "ui").get("open") or []


class Post:
    """A throwaway house pinning `ui`, the witness and its script, the journal: `render`
    plays `./pp ui …` there (the post's memory forgotten first, unless `keep`), `tabs_of`
    reads the nested tab bar of a capture."""

    def __init__(self, bench, name: str, script: dict | None = None) -> None:
        env = bench.env(name, packages=("ui",))
        self.made = env.made
        self.ws, self.engine = env.made.parent, env.engine
        faces = bench.temp() / "faces"
        faces.mkdir(exist_ok=True)
        shutil.copy(WITNESS, faces / "agent")
        (faces / "agent").chmod(0o755)
        self.script_file = bench.temp() / "dialogue-script.json"
        self.use(script or SCRIPT)
        self.journal = bench.temp() / "chat.log"
        self.env = {"PP_UI_FACES": str(faces), "PP_UI_CHAT_SCRIPT": str(self.script_file),
                    "PP_UI_CHAT_LOG": str(self.journal)}

    def use(self, script: dict) -> None:
        """The witness replays this script from the next render on; the house, its memory and the journal stay."""
        self.script_file.write_text(json.dumps(script), encoding="utf-8")

    def render(self, *args: str, witnessed: bool = True, keep: bool = False):
        if not keep:
            forget(self.made)
        return cli(self.engine, "ui", *args, cwd=self.ws, env=self.env if witnessed else None)

    def remembered(self) -> list:
        return remembered(self.made)

    @staticmethod
    def tabs_of(text: str) -> str:
        """The nested tab bar of the dialogue: the line under the post's own tabs and their bar."""
        lines = text.split("\n")
        return lines[3] if len(lines) > 3 else ""

    def journal_lines(self) -> list[str]:
        return self.journal.read_text(encoding="utf-8").splitlines() if self.journal.is_file() else []

    def clear_journal(self) -> None:
        if self.journal.is_file():
            self.journal.unlink()
