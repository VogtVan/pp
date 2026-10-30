"""Scenario `ui-tasks-sequence` -- the SEQUENCE of the task under the cursor on the Tasks tab, followed live, on ONE
house of the bench's `pp-team` witness whose script changes by `use()`:
- the model of a sequence (`model.teams.sequence_of`, loaded from the source): T3's thread gives its principal's column
  first, then its members in the order they appear, one row per post with its pair (from, to), the wake-up joined by
  its tag; centred on `reviewer`, its column first and the rows it sends, receives or wakes in alone
- the band of a task a wake-up plays: its detail, then its SEQUENCE and no result -- T3's thread read once the cursor
  rested on it (`log core-review T3`), one row per post in the order of their `id`
- the sequence followed live: `core-review`'s watch saying a post, a step of `lead`, a step of `reviewer`, then the end
  of `lead`'s wake-up -- the post's row added after the others, the pile of procs of `reviewer` under its name, `lead`'s
  gone with its wake-up; `tab` goes into the sequence, its cursor on the last row, `up` one row above
- the band keeps its place: the detail and the sequence where they stood before a post came, as `--regions` says
- the footer says the keys of where the focus stands: the sequence's (`w`) once it is focused, none of them before
- each row says, beside its head, the time since the row drawn before it -- the first since the task was born --, as
  the journal dates them: T3's #42 `+0s`, #44 `+1m`, #45 `+3m`; the model says the task's birth
"""
from __future__ import annotations

import importlib.util
import re
import sys

from tests.harness import SOURCE, support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

CURSOR = P.palette_constant("CURSOR")
SIZE = ("--size", "160x40")
MODEL = SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "model" / "teams.py"


def model():
    """-> the module of the post's typed state, loaded from the source: pure, no Textual."""
    spec = importlib.util.spec_from_file_location("pp_ui_model_teams", MODEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # a dataclass reads its module there
    spec.loader.exec_module(module)
    return module


def placed(text: str, *parts: str) -> list[str]:
    """-> where a `--regions` capture puts each of `parts` of the band: its line, `x y w h` included."""
    return [one for one in text.split("\n") if one.split()[:2] in [["inner", part] for part in parts]]


def inner_of(text: str) -> set[str]:
    """-> the parts of the band a `--regions` capture says shown."""
    return {one.split()[1] for one in text.split("\n") if one.startswith("inner ")}


def heads_of(text: str) -> list[int]:
    """-> the ids of the posts a sequence draws, in the order of its rows: the `#<id>` heading each row's gutter."""
    head = re.compile(rf"[{re.escape(CURSOR)}\s]#(\d+) [a-z]+(?: #\d+)?(?:\s+\+\S+)?\s{{2,}}")   # a row's gutter, never the row said
    return [int(found.group(1)) for found in map(head.search, text.split("\n")) if found]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script()
    script["states"].update({"core-review": [T.LIVE_CORE], "ops": [T.LIVE_OPS]})
    house = T.Teams(bench, "ui-tasks-sequence", script)
    posts = [one for one in T.T3_LOG if one["event"] == "post"]

    # --- the model of a sequence ------------------------------------------------------------------------
    teams = model()
    lines = [teams.ThreadLine.read(one) for one in T.T3_LOG]
    whole, centred = teams.sequence_of(lines), teams.sequence_of(lines, "reviewer")
    pairs = [(one.source, one.target) for one in whole.rows if one.kind == "post"]
    wakes = [(one.source, one.run, one.over) for one in whole.rows if one.kind == "wake"]
    mine = [one.id for one in centred.rows]
    if (whole.columns == ("house", "lead", "reviewer") and pairs == [(one["from"], one["to"]) for one in posts]
            and whole.start == T.T3_LOG[0]["at"]
            and wakes == [("reviewer", "a01389", True)] and centred.columns == ("reviewer", "lead", "house")
            and mine == [one["id"] for one in T.T3_LOG if "reviewer" in (one.get("from"), one.get("to"), one.get("agent"))]):
        held("the model of a sequence", f"columns {whole.columns}, pairs {pairs}, wake {wakes}; centred on reviewer "
             f"{centred.columns}, rows {mine}")
    else:
        failures.append(f"  ✗ model                       {whole} {centred}")

    # --- the band of a task a wake-up plays: its sequence, no result ------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE)
    resting = done
    reads = [one for one in house.journal_lines() if one == "log core-review T3"]
    gaps = dict((int(one), gap) for one, gap in re.findall(r"#(\d+) [a-z]+(?: #\d+)?\s+(\+\S+)\s", done.stdout))
    if gaps.get(42) == "+0s" and gaps.get(44) == "+1m" and gaps.get(45) == "+3m":
        held("each row says the time since the row before it", f"{gaps}")
    else:
        failures.append(f"  ✗ gaps                        {gaps} {done.stdout[-1600:]!r}")
    at_rest = house.render("--render", "tasks", *SIZE, "--regions").stdout
    regions = inner_of(at_rest)
    if (done.returncode == 0 and heads_of(done.stdout) == [one["id"] for one in posts] and len(reads) == 1
            and "tasks-sequence" in regions and "tasks-result" not in regions and "tasks-live" not in regions):
        held("a task a wake-up plays shows its sequence, no result", f"rows {heads_of(done.stdout)}, the thread read "
             f"{len(reads)} time; the band shows {sorted(regions)}")
    else:
        failures.append(f"  ✗ sequence                    rc={done.returncode} {heads_of(done.stdout)} {reads} "
                        f"{sorted(regions)} {done.stdout[-2400:]!r} {done.stderr[-400:]!r}")

    # --- the sequence followed live: a post added, the piles of the members, the cursor -------------------------
    watched = [{"sleep": 0.8}, T.WRITTEN] + T.TWO_WATCH    # #46 once the thread is read: added live
    script = T.script(watch={"core-review": watched})
    script["states"]["core-review"] = [T.LIVE_CORE]
    house.use(script)
    done = moved = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended:3", "--press", "tab,up")
    heads = heads_of(done.stdout)
    cursor = next((one.split("│", 1)[-1].lstrip(" ") for one in moved.stdout.split("\n")
                   if one.split("│", 1)[-1].lstrip(" ").startswith(CURSOR)), "")
    ids = sorted(one["id"] for one in posts + [T.WRITTEN])
    frame = {one["agent"]: one["stack"].split("▸")[-1].strip() for one in (T.STEP, T.LEAD_STEP)}
    if (done.returncode == 0 and heads == ids and frame["reviewer"] in done.stdout
            and frame["lead"] not in done.stdout and cursor.startswith(f"{CURSOR}#{T.WRITTEN['id']} ")):
        held("the sequence followed live", f"rows {heads}: #{T.WRITTEN['id']} in its place; reviewer's pile drawn, "
             f"lead's gone with its wake-up; tab, up: the cursor on {cursor.split()[0]!r}")
    else:
        failures.append(f"  ✗ live sequence               rc={done.returncode} {heads} {cursor!r} "
                        f"{done.stdout[-2400:]!r} {moved.stdout[-1200:]!r} {done.stderr[-400:]!r}")
    grown = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended:3", "--regions").stdout
    before, after = placed(at_rest, "tasks-detail", "tasks-sequence"), placed(grown, "tasks-detail", "tasks-sequence")
    if before and len(before) == 2 and before == after:
        held("the band keeps its place as the sequence grows", f"{after} before and after #{T.WRITTEN['id']} came")
    else:
        failures.append(f"  ✗ band in place               {before} {after}")
    keys = (P.keys_of(resting.stdout), P.keys_of(moved.stdout))
    if "[w]" not in keys[0] and "[w]" in keys[1]:
        held("the footer says the keys of the sequence once it is focused", "`w` absent on the tasks, there in the "
             "sequence")
    else:
        failures.append(f"  ✗ keys of the sequence        {keys!r}")

    return 0
