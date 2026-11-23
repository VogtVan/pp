"""Support of the `ui-tasks-sequence*` scenarios -- the SEQUENCE of the task under the cursor on the Tasks tab (rule
10): the house of the bench's `pp-team` witness they each install, the reading of a capture (`heads_of`, `placed`,
`inner_of`, `scales_of`), the model of a sequence loaded from the source, the probe that draws a sequence by
`palette.sequence_text` in a Textual subprocess, and the one that draws its head by `palette.sequence_head`."""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import subprocess
import sys

from tests.harness import SOURCE, support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

CURSOR = P.palette_constant("CURSOR")
SIZE = ("--size", "160x40")
MODEL = SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "model" / "teams.py"
SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
LABEL = r"#(\d+) [a-z]+(?: #\d+)?"                                # the head of a row: `#<id> <verb>`, its `#<re>`
SCALE = r"(\d\d:\d\d \((\d+):(\d\d):(\d\d)\))"                     # the scale of a row: the hour, then the delay
ANY_SCALE = r"\d[\dsmhd:]*(?: \(\d+:\d\d:\d\d\))?"                       # what a gutter says beside a head, any form
PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
from datetime import datetime
import palette
from model.teams import Sequence, SequenceRow

GROUPS = json.loads(sys.argv[2])
COLS = ("house", "lead", "reviewer")
start, dates = GROUPS[0]
rows = tuple(SequenceRow("post", 10 + n, at, COLS[n % 2], COLS[1 + n % 2], "do", None, f"post {n}")
             for n, at in enumerate(dates))
sequence = Sequence(COLS, rows, None, start)
frame = palette.sequence_frame(sequence, 160)
body = palette.sequence_text(sequence, 160)[1].plain.split("\\n")
said = getattr(palette, "scale_of", None)
moment = datetime.fromisoformat
print(json.dumps({
    "column": [line[frame.heads + 2:frame.gutter].strip() for line in body[:len(rows)]],
    "hours": [moment(at).astimezone().strftime("%H:%M") for at in dates],
    "expected": [[said(moment(at), moment(begun)) for at in ats] for begun, ats in GROUPS] if said else None}))
"""
HEAD_PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
import palette
from model.teams import Sequence, SequenceRow, TeamState, ThreadLine, sequence_of, with_roles

COLS = ("house", "lead", "reviewer")
rows = (SequenceRow("post", 10, "2026-10-10T09:00:00+00:00", "house", "lead", "do", None, "post"),)
said = {}
for case, roles, principals in (("bare", (), ()), ("parts", (("lead", ("workers", "reviewers")),), ("house", "pm"))):
    sequence = Sequence(COLS, rows, None, rows[0].at, roles=roles, principals=principals)
    frame = palette.sequence_frame(sequence, 160)
    lines = palette.sequence_head(sequence, frame).plain.split("\\n")
    said[case] = {"lines": len(lines), "under": {name: bool(lines[1][max(0, x - 2):x + 3].strip())
                                                 for name, x in zip(frame.columns, frame.xs)}}
given = json.loads(sys.argv[2])
sequence = with_roles(sequence_of([ThreadLine.read(one) for one in given["log"]]), TeamState.read(given["face"]))
frame = palette.sequence_frame(sequence, 160)
lines = palette.sequence_head(sequence, frame).plain.split("\\n")
said["team"] = {"lines": len(lines), "under": {name: bool(lines[1][max(0, x - 2):x + 3].strip())
                                               for name, x in zip(frame.columns, frame.xs)}}
print(json.dumps(said))
"""
ROLES = {"lead": ["workers", "reviewers"]}                          # the role keys the face gives, by member
THREADS_PROBE = """
import json, sys
sys.path.insert(0, sys.argv[1])
from model.teams import TeamState, Thread
from panes.sequence import Threads

given = json.loads(sys.argv[2])
state = TeamState.read(given["face"])
said = {}
try:
    threads = Threads(object(), lambda key: None, face=lambda team: state if team == state.team else None)
except TypeError as refused:
    said["refused"] = str(refused)[:200]
else:
    threads.threads[(state.team, "T3")] = thread = Thread("T3")
    thread.history(given["log"])
    sequence = threads.sequence((state.team, "T3"))
    said.update(roles=[[name, list(keys)] for name, keys in sequence.roles], principals=list(sequence.principals))
print(json.dumps(said))
"""


def model():
    """-> the module of the post's typed state, loaded from the source: pure, no Textual."""
    spec = importlib.util.spec_from_file_location("pp_ui_model_teams", MODEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # a dataclass reads its module there
    spec.loader.exec_module(module)
    return module


def placed(text: str, *parts: str) -> list[str]:
    """-> where a `--regions` capture puts each of `parts` of the band, a zone of the centre: its line, `x y w h`
    included."""
    return [one for one in text.split("\n") if one.split()[:2] in [["band", part] for part in parts]]


def inner_of(text: str) -> set[str]:
    """-> the zones of the centre a `--regions` capture says shown -- the band of a task is three zones under the
    table, the frame below its sequence or its result."""
    return {one.split()[1] for one in text.split("\n") if one.startswith("band ")}


def heads_of(text: str) -> list[int]:
    """-> the ids of the posts a sequence draws, in the order of its rows: the `#<id>` heading each row's gutter."""
    head = re.compile(rf"[{re.escape(CURSOR)}\s]{LABEL}(?:\s+{ANY_SCALE})?\s{{2,}}")   # a row's gutter, never the row said
    return [int(found.group(1)) for found in map(head.search, text.split("\n")) if found]


def scales_of(text: str) -> dict[int, str]:
    """-> the scale each row of a captured sequence says beside its head, by the id of its post."""
    return {int(one): said for one, said, *_ in re.findall(rf"{LABEL}\s+{SCALE}\s", text)}


def delay_of(scale: str) -> int | None:
    """-> the seconds the delay of a scale says, read by its fields (`(hh:mm:ss)`, the hours cumulated)."""
    found = re.search(SCALE, scale)
    return int(found.group(2)) * 3600 + int(found.group(3)) * 60 + int(found.group(4)) if found else None


def probe(bench, groups: list) -> tuple[dict, subprocess.CompletedProcess]:
    """-> what a sequence drawn by `palette.sequence_text` in a Textual subprocess says, for `groups` -- a list of
    `[start, [date, ...]]`, the first one drawn: its gutter column under the frame, the local hour of each of its
    dates, and the scale `palette.scale_of` gives every date of every group (None when the palette has none)."""
    return _probed(bench, "scale_probe.py", PROBE, json.dumps(groups))


def head_probe(bench, face: dict, log: list) -> tuple[dict, subprocess.CompletedProcess]:
    """-> the head `palette.sequence_head` draws in a Textual subprocess, by case -- `bare` a sequence `house`, `lead`,
    `reviewer` given no part, `parts` the same given the role keys of `lead` and the principals `house` and `pm`,
    `team` the sequence of the thread `log` given its parts by the team's `face` (`with_roles`) --: its number of lines,
    and whether its second line has a cell under each column."""
    return _probed(bench, "head_probe.py", HEAD_PROBE, json.dumps({"face": face, "log": log}))


def threads_probe(bench, face: dict, log: list) -> tuple[dict, subprocess.CompletedProcess]:
    """-> the parts `panes.sequence.Threads` gives the sequence of T3's thread `log` in a Textual subprocess, built on a
    pane that holds no face and handed the reading of the team's `face` at its birth (`face=`): `{roles, principals}`,
    or `{refused}` when it takes no such reading."""
    return _probed(bench, "threads_probe.py", THREADS_PROBE, json.dumps({"face": face, "log": log}))


def _probed(bench, name: str, source: str, *args: str) -> tuple[dict, subprocess.CompletedProcess]:
    """-> the JSON the last line of `source` says, played in a Textual subprocess on the skill's source."""
    script = bench.temp() / name
    script.write_text(source, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(script), str(SKILL), *args], capture_output=True, text=True, timeout=180)
    try:
        return json.loads(played.stdout.strip().splitlines()[-1]), played
    except (ValueError, IndexError):
        return {}, played


def house(bench, name: str, roles: dict | None = None):
    """-> the house of `pp-team`'s witness the scenario `name` plays: `core-review` and `ops` live -- the members of
    `core-review` given the role keys `roles` names, by member, when given."""
    script = T.script()
    core = T.LIVE_CORE if roles is None else {**T.LIVE_CORE, "members": [
        {**one, "roles": list(roles.get(one["member"], []))} for one in T.LIVE_CORE["members"]]}
    script["states"].update({"core-review": [core], "ops": [T.LIVE_OPS]})
    return T.Teams(bench, name, script)


def head_of(text: str) -> tuple[list[str], list[int]]:
    """-> the head of a captured sequence -- its lines from the one of the column names down to its lifelines: the
    lifelines the first line of the capture that holds lifeline glyphs alone (`LIFE`, `FOCUS_LIFE`, `WAKING` of
    `palette.py`), the names the nearest line above them that says something under every column -- and the x of each
    column; ([], []) without lifelines."""
    glyphs = lifeline_glyphs()
    lines = text.split("\n")
    for index, line in enumerate(lines):
        cells = line.split()
        if len(cells) >= 2 and set(cells) <= glyphs:
            xs = [x for x, one in enumerate(line) if one in glyphs]
            first = index - 1
            while first > 0 and not all(under(lines[first], x) for x in xs):
                first -= 1
            return lines[first:index + 1], xs
    return [], []


def under(line: str, x: int) -> bool:
    """-> whether a line of a captured head says something under the column at `x`."""
    return bool(line[max(0, x - 2):x + 3].strip())


def lifeline_glyphs() -> set[str]:
    """-> the glyphs of a lifeline, read from `palette.py`'s source: `LIFE, FOCUS_LIFE, WAKING = ...`."""
    for node in ast.parse(P.PALETTE.read_text(encoding="utf-8")).body:
        if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple)
                and "LIFE" in [one.id for one in node.targets[0].elts if isinstance(one, ast.Name)]):
            return {one.value for one in node.value.elts if isinstance(one, ast.Constant)}
    return set()
