"""Scenario `ui-team-clock` -- a freshness is a duration, the post has ONE clock, and the status line of Teams narrows
in order, on the bench's `pp-team` witness replaying faces whose instants are posed at the reading (`aged`): first
`core-review` paused 10 min ago, its last event 3 min ago, `reviewer` launched 12 s ago, `TEAM.md` changed since its
start; then its last event 2 h ago and `ops`' 3 d ago:
- Teams says ages: `reviewer`'s wake-up in `live`, the pause beside who paused, the last event on the status line --
  each as long ago as the face's instant; no hour on the screen but the status line's two
- the status line narrows in order: at 200 columns it says every part, at 150, 100 and 80 it loses the last event,
  then the members, the tasks, the cost, the wake-ups, the state, in that order, each part kept whole; the team's
  name, its alert and the two hours -- the reading's and the post's clock -- stay at every width
- Tasks says ages: T3's last event in the table, `reviewer`'s launch on the `live` line of its band; no hour but the
  status line's
- the coarse units: the last event in hours on the status line, ops' task in days in the table, T3's last event in
  hours on its band; no hour on Tasks but the status line's
- the thread of a task keeps the hour of each event, as the post's clock reads the face's instant
"""
from __future__ import annotations

import re
from datetime import datetime

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SEP = P.palette_constant("SEP")
HOUR = re.compile(r"\d\d:\d\d:\d\d")
DROP = ("last", "members", "tasks", "cost", "wakes", "state")     # what a status line too wide loses, first first


def clocks(text: str) -> list[str]:
    """-> the rows of a capture carrying an hour, the status line (the last) left out."""
    return [one for one in text.rstrip("\n").split("\n")[:-1] if HOUR.search(one)]




def age_in(text: str, iso: str, before: str) -> str:
    """-> the age of the instant `iso` the text says, as the post counts it at its unit: one of the ages the bench
    counts between `before` (counted before the render) and now -- '' when it says none."""
    after = T.age_said(iso)
    ages = {before, after}
    low, high = before.split(" "), after.split(" ")
    if len(low) == len(high) == 2 and low[1] == high[1]:
        ages |= {f"{n} {low[1]}" for n in range(int(low[0]), int(high[0]) + 1)}
    return next((one for one in sorted(ages) if re.search(rf"(?<![\w.]){re.escape(one)}(?!\w)", text)), "")




def parts_of(status: str, face: dict, badge: dict, house: str) -> list[tuple[str, str]]:
    """-> the parts of a status line of Teams, `(kind, text)`, each kind told by the face's data: its team, its state,
    its tasks as the badge counts them, its members' count, its cost, its wake-ups against their bound, its last
    event (its age after it), the hours; what none of them claims is an alert."""
    found: list[tuple[str, str]] = []
    wakes, last = face["wakes"], face["last"]
    for text in (one.strip() for one in status.strip().split(SEP)):
        if not found and text == house:
            kind = "house"
        elif found and found[-1][0] == "last" and f"#{last['id']}" in found[-1][1] and not HOUR.search(text):
            kind = "last"                                       # the age of the last event, after it
        elif text == face["team"]:
            kind = "team"
        elif text == face["state"]:
            kind = "state"
        elif all(f"{n} {key}" in text for key, n in badge["tasks"].items()):
            kind = "tasks"
        elif re.fullmatch(rf"{len(face['members'])}\D*", text):
            kind = "members"
        elif f"{face['cost']:.2f}" in text:
            kind = "cost"
        elif f"{wakes['launched']}/{wakes['bound']}" in text:
            kind = "wakes"
        elif T.in_order(text, f"#{last['id']}", last["kind"]):
            kind = "last"
        elif HOUR.search(text):
            kind = "hour"
        else:
            kind = "alert"
        found.append((kind, text))
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    core = {**T.aged(T.LIVE_CORE, last=180, since=12, paused=600), "changed": True}
    script = T.script()
    script["states"]["core-review"] = [core]
    script["states"]["ops"] = [T.aged(T.OPS, last=180, since=12)]
    house = T.Teams(bench, "ui-team-clock", script)
    badge = next(one for one in T.BADGES if one["team"] == core["team"])
    reviewer = next(one for one in core["members"] if one["member"] == "reviewer")
    pause, last = core["paused"], core["last"]

    # --- Teams: the ages of the live, the pause and the last event; one clock ----------------------------------
    before = {key: T.age_said(iso) for key, iso in (("since", reviewer["since"]), ("paused", pause["at"]),
                                                     ("last", last["at"]))}
    wide = house.render("--render", "teams", "--size", "200x34")
    rows = wide.stdout.rstrip("\n").split("\n")
    status = rows[-1] if rows else ""
    live = next((one for one in rows if T.in_order(one, reviewer["path"], reviewer["run"])), "")
    since = age_in(live, reviewer["since"], before["since"])
    paused = next((one for one in rows if T.in_order(one, core["state"], pause["by"]) and age_in(one, pause["at"],
                                                                                              before["paused"])), "")
    tail = status.split(f"#{last['id']} {last['kind']}", 1)[-1] if f"#{last['id']} {last['kind']}" in status else ""
    aged = age_in(tail.split(SEP)[1] if SEP in tail else "", last["at"], before["last"])
    hours = clocks(wide.stdout)
    if wide.returncode == 0 and since and paused and aged and not hours and len(HOUR.findall(status)) == 2:
        held("Teams says durations, one clock", f"{reviewer['member']} since {since}, paused by {pause['by']} "
             f"{age_in(paused, pause['at'], before['paused'])} ago, #{last['id']} {last['kind']} {aged} ago; no hour but "
             f"the status line's two")
    else:
        failures.append(f"  ✗ teams ages                  rc={wide.returncode} hours={hours} {before} {live!r} {paused!r} "
                        f"{status!r} {wide.stdout[-1800:]!r} {wide.stderr[-300:]!r}")

    # --- the status line, narrowed --------------------------------------------------------------------------------
    full = parts_of(status, core, badge, house.ws.name)
    lines, kept = {}, {}
    for width in (150, 100, 80):
        done = house.render("--render", "teams", "--size", f"{width}x30")
        lines[width] = P.status_of(done.stdout).rstrip() if done.returncode == 0 else ""
        kept[width] = parts_of(lines[width], core, badge, house.ws.name)
    kinds = [kind for kind, _ in full]
    whole = all(kind in kinds for kind in ("team", "alert", *DROP)) and kinds.count("hour") == 2
    dropped = {width: [kind for kind in DROP if kind in kinds and kind not in [one for one, _ in parts]]
               for width, parts in kept.items()}
    ordered = all(one == list(DROP[:len(one)]) for one in dropped.values())
    standing = all([part for part in full if part[0] in ("house", "team", "alert")]
                   == [part for part in parts if part[0] in ("house", "team", "alert")]
                   and [kind for kind, _ in parts].count("hour") == 2 and HOUR.search(parts[-1][1])
                   and all(part in full or part[0] == "hour" for part in parts) for parts in kept.values())
    if (whole and ordered and standing and len(dropped[150]) <= len(dropped[100]) < len(dropped[80])
            and "last" in dropped[80]):
        held("the status line narrows in order", "; ".join(f"{w}: loses {', '.join(dropped[w]) or 'nothing'}"
                                                         for w in dropped)
             + " -- the name, its alert and the two hours at every width, each part whole")
    else:
        failures.append(f"  ✗ status                      {full} {dropped} {lines!r}")

    # --- Tasks: the ages of the last event and of the launch; one clock -------------------------------------------
    task = next(one for one in core["tasks"] if one["id"] == "T3")
    wake = task["running"][0]
    before = {"last": T.age_said(task["last"]["at"]), "since": T.age_said(wake["since"])}
    tasks = house.render("--render", "tasks", "--size", "150x40")
    rows = tasks.stdout.split("\n")
    row = next((one for one in rows if task["name"] in one and core["team"] in one), "")
    launched = next((one for one in rows if T.in_order(one, wake["member"], wake["run"])), "")
    hours = clocks(tasks.stdout)
    in_row, in_live = age_in(row, task["last"]["at"], before["last"]), age_in(launched, wake["since"], before["since"])
    if tasks.returncode == 0 and in_row and in_live and not hours:
        held("Tasks says durations", f"T3's last event {in_row} ago in the table, {wake['member']}'s run {wake['run']} "
             f"launched {in_live} ago on its band; no hour but the status line's")
    else:
        failures.append(f"  ✗ tasks ages                  rc={tasks.returncode} hours={hours} {before} {row!r} "
                        f"{launched!r} {tasks.stdout[-1500:]!r} {tasks.stderr[-300:]!r}")

    # --- the coarse units: hours and days ---------------------------------------------------------------------------
    core = T.aged(T.CORE, last=2 * 3600 + 30, since=12)
    ops = T.aged(T.OPS, last=3 * 86400 + 60, since=12)
    house.use(T.script(states={"core-review": [core], "ops": [ops]}))
    task, far = next(one for one in core["tasks"] if one["id"] == "T3"), ops["tasks"][0]
    before = {"last": T.age_said(core["last"]["at"]), "T3": T.age_said(task["last"]["at"]),
              "ops": T.age_said(far["last"]["at"])}
    teams = house.render("--render", "teams", "--size", "170x34")
    tasks = house.render("--render", "tasks", "--size", "150x40")
    status = P.status_of(teams.stdout)
    named = f"#{core['last']['id']} {core['last']['kind']}"
    tail = status.split(named, 1)[-1] if named in status else ""
    hourly = age_in(tail.split(SEP)[1] if SEP in tail else "", core["last"]["at"], before["last"])
    rows = tasks.stdout.split("\n")
    row = next((one for one in rows if T.in_order(one, far["id"], ops["team"])), "")
    daily = age_in(row, far["last"]["at"], before["ops"])
    band = next((one for one in rows if T.in_order(one, f"#{task['last']['id']}", task["last"]["kind"])), "")
    banded = age_in(band, task["last"]["at"], before["T3"])
    if (teams.returncode == 0 and tasks.returncode == 0 and hourly.endswith(" h") and daily.endswith(" d")
            and banded.endswith(" h") and not clocks(tasks.stdout)):
        held("the coarse units", f"{named} {hourly} on the status line, ops' {far['id']} {daily} in the table, "
             f"#{task['last']['id']} {task['last']['kind']} {banded} on T3's band")
    else:
        failures.append(f"  ✗ units                       rc={teams.returncode},{tasks.returncode} {before} {status!r} "
                        f"{row!r} {band!r} {clocks(tasks.stdout)}")

    # --- the thread keeps its hours -------------------------------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "enter")
    dated = {one["id"]: f"{datetime.fromisoformat(one['at']).astimezone():%H:%M:%S}" for one in T.T3_LOG}
    missing = [f"#{n} {hour}" for n, hour in dated.items()
               if not re.search(rf"#{n} {hour}\b", done.stdout)]
    if done.returncode == 0 and not missing:
        held("the thread keeps the hour of each event", f"{len(dated)} events, each at the hour of its instant: "
             f"#{next(iter(dated))} {next(iter(dated.values()))}, …")
    else:
        failures.append(f"  ✗ thread hours                rc={done.returncode} missing={missing} {done.stdout[-1200:]!r}")
    return 0
