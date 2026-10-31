"""Scenario `ui-team-strip` -- under the member chosen on the Teams tab, the band of its tasks and the sequence of the
one chosen there, on the bench's `pp-team` witness:
- the band and the sequence keep their place: where `--regions` puts them with 2 tasks, they stand with 100
- the band of the member's tasks: 100 tasks, as many shown as the width holds, those hidden on each side counted -- the
  hidden and the shown make 100 --, three lines high at 80 and at 200 columns, the cursor on the newest open task;
  `home` the first, `j` the first open one, `>` a page further; its keys at the foot once focused
- the sequence of the task chosen there, centred on the member: its column first, `║`, then those it exchanged with,
  its thread read at `log`
- the band and the sequence stay as they are while the team is read again: `reviewer`'s band moved to T2, the members
  left and taken back, then two posts on the watch -- T2 still chosen, the sequence's rows those of T2, its thread read
  once and no other
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")
FOCUS_LIFE = P.palette_constant("FOCUS_LIFE")
STRIP = "3,tab,down"                              # the members, the cursor on `reviewer`
POSTS = [{"sleep": 4.0}, T.event("09:20:00", "post", 60, task="T3", **{"from": "lead"}, to="reviewer", verb="do",
                                 text="once more"),
         {"sleep": 0.5}, T.event("09:20:30", "post", 61, task="T3", **{"from": "reviewer"}, to="lead", verb="re", re=60,
                                 text="done")]


def strip_of(text: str) -> tuple[int, list[str], int, str]:
    """-> the band of a member's tasks as drawn: the tasks hidden before, the ids shown, the tasks hidden after, and
    the line of the task chosen."""
    lines = [one.split("│", 1)[-1] for one in text.split("\n")]
    at = next((index for index, one in enumerate(lines) if re.search(r"\[T\d+ ", one)), None)   # the task under the cursor
    if at is None:
        return 0, [], 0, ""
    row = lines[at]
    before, after = re.search(r"‹ (\d+)", row), re.search(r"(\d+) ›", row)
    return (int(before.group(1)) if before else 0, re.findall(r"\bT\d+\b", row), int(after.group(1)) if after else 0,
            lines[at + 1] if at + 1 < len(lines) else "")


def placed(text: str) -> list[str]:
    """-> where a `--regions` capture puts the band of the tasks and the sequence under it, `x y w h` included."""
    return [one for one in text.split("\n") if one.split()[:2] in (["band", "teams-strip"], ["band", "teams-sequence"])]


def strip_height(text: str) -> int | None:
    """-> the rows a `--regions` capture gives the band of the tasks."""
    found = re.search(r"band teams-strip x=\d+ y=\d+ w=\d+ h=(\d+)", text)
    return int(found.group(1)) if found else None



def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-strip")

    # --- the band of a member's tasks: 100 of them -------------------------------------------------------------
    few = placed(house.render("--render", "teams", "--size", "80x40", "--press", STRIP, "--regions").stdout)
    house.use(T.script(states={"core-review": [T.crowded()]}))
    captured = [house.render("--render", "teams", "--size", size, "--press", STRIP, "--regions").stdout
                for size in ("80x40", "200x50")]
    heights = [strip_height(one) for one in captured]
    if len(few) == 2 and few == placed(captured[0]):
        held("the band and the sequence keep their place", f"{few} with 2 tasks as with 100")
    else:
        failures.append(f"  ✗ band in place               {few} {placed(captured[0])}")
    done = house.render("--render", "teams", "--size", "200x50", "--press", STRIP + ",tab")
    before, shown, after, chosen = strip_of(done.stdout)
    moves = {}
    for keys in ("home", "home,j", "home,greater_than_sign"):
        moves[keys] = strip_of(house.render("--render", "teams", "--size", "200x50", "--press",
                                            f"{STRIP},tab,{keys}").stdout)
    homed, opened, paged = moves["home"], moves["home,j"], moves["home,greater_than_sign"]
    if (heights[0] == heights[1] == 4 and before + len(shown) + after == 100 and chosen.lstrip().startswith("T97")
            and homed[0] == 0 and homed[1][0] == "T1" and opened[3].lstrip().startswith("T42")
            and paged[3].lstrip().startswith(f"T{len(homed[1]) + 1}") and "[j]" in P.keys_of(done.stdout)):
        held("the band of a member's tasks pages through 100", f"{before} before, {len(shown)} shown, {after} after; "
             f"T97 chosen; home T1, j {opened[3].split()[0]}, > {paged[3].split()[0]}; {heights} rows high")
    else:
        failures.append(f"  ✗ band of tasks               {heights} {before} {shown} {after} {chosen!r} {moves} "
                        f"{done.stdout[-2400:]!r} {done.stderr[-400:]!r}")

    # --- the sequence of the task chosen, centred on the member --------------------------------------------------
    house.use(T.script())
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x50", "--press", STRIP)
    head = next((one for one in done.stdout.split("\n") if T.in_order(one, "reviewer", "lead", "house")), "")
    if (done.returncode == 0 and head and FOCUS_LIFE in done.stdout
            and "log core-review T3" in house.journal_lines()):
        held("the sequence of the task chosen, centred on the member", f"{' '.join(head.split()[-3:])!r}, its "
             f"column {FOCUS_LIFE}; T3's thread read")
    else:
        failures.append(f"  ✗ centred sequence            {head!r} {house.journal_lines()} {done.stdout[-2400:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- the team read again: the band keeps its task, the sequence its rows --------------------------------------
    house.use(T.script(watch={"core-review": POSTS}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x50", "--press",
                        f"{STRIP},tab,left,shift+tab,up,down,wait:team:post,wait:team:post")
    chosen = strip_of(done.stdout)[3].lstrip()
    heads = [int(one) for one in re.findall(r"#(\d+) [a-z]+(?: #\d+)?(?:\s+\+\S+)?\s{2,}", done.stdout)]
    logs = [one for one in house.journal_lines() if one.startswith("log ")]
    mine = [one["id"] for one in T.T2_LOG if one["event"] == "post"]
    reads = [one for one in house.journal_lines() if one == "status core-review"]
    if (done.returncode == 0 and chosen.startswith("T2") and heads == mine and logs.count("log core-review T2") == 1
            and set(logs) <= {"log core-review T2", "log core-review T3"} and len(reads) >= 2):
        held("the band and the sequence stay while the team is read again", f"T2 chosen after the members left and "
             f"came back and {len(reads)} readings of the team; rows {heads}; {logs}")
    else:
        failures.append(f"  ✗ stable                      {chosen!r} {heads} {logs} {reads} {done.stdout[-2400:]!r} "
                        f"{done.stderr[-400:]!r}")
    return 0
