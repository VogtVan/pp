"""Scenario `ui-agents-season` -- the Agents tab says the season of the teams and follows the disk (batch
les-agents-et-la-saison), on the bench's two witnesses: `pp-team` replays `core-review` (its members `lead` and
`reviewer`, each with the launch its season gives it), `pp-chat` the agents `agents/reviewer` (a member) and
`agents/solo` (of no team), its `list` a sequence of answers:
- the table has no `team` column -- an agent may be a member of several teams -- and no `season` column (the season
  lives on the Teams tab); the teams are read with the agents all the same, once the tab is shown: the marks of the
  runs stand on them
- `s` on the Teams tab opens the season of the team chosen READ ONLY: titled by the team, its lines `all`, `lead`,
  `reviewer` from `team status --json` alone, no `ctrl+s` in its keys, nothing of `agent providers` nor a `status` of
  the team more than the tab's own reading; the column of the packages says the packages on of `all`'s set, and of a
  member what it changes; `enter` on a line shows its profile closed, its packages each with its state -- the set its
  face says
- `S` on the Agents tab opens nothing
- a team gesture reads the catalogue again: `D` on the Teams tab and the team's name typed play `team delete`, and the
  agent the next `list` says appears without `u`
- the round sees the disk: at the bench's pace (`PP_UI_LIST_PERIOD` one second), a `list` equal to the catalogue plays no
  `agent status`; a `list` that gains an agent reads that agent's status alone
"""
from __future__ import annotations

import json
from pathlib import Path

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")
AS_ALL = P.palette_constant("AS_ALL")
ON = " ".join(name for name, on in T.switches_set(T.LAUNCH["packages"]).items() if on)   # all's packages on

REVIEWER, SOLO, BORN = "agents/reviewer", "agents/solo", "agents/ag3"
LIST = T.MEMBER_FACES["list"] + [{"agent": SOLO, "runs": 1, "running": 0, "responses": 1}]
GROWN = LIST + [{"agent": BORN, "runs": 0, "running": 0, "responses": 0}]
SOLO_STATUS = [{"agent": SOLO, "run": "c00001", "name": "", "exchanges": 1, "state": "parked", "stack": "", "session": "s-c",
                "provider": P.PROVIDER, "cost_usd": 0.01, "launches": 1, "responses": 1, "first_message": "alone",
                "first_at": "2026-10-10T09:00:00+00:00", "last_at": "2026-10-10T09:01:00+00:00", "context": None},
               {"agent": SOLO, "providers": [P.PROVIDER], "last": None}]
BORN_STATUS = [{"agent": BORN, "providers": [P.PROVIDER], "last": None}]
DELETE = "D,c,o,r,e,minus,r,e,v,i,e,w,enter"


def agents(house, lists: list) -> None:
    """The witness of `agent` says these lists, call after call, and the statuses of every agent they name."""
    faces = {**T.MEMBER_FACES, "list": lists, "providers": T.PROVIDERS,
             "status": {**T.MEMBER_FACES["status"], SOLO: SOLO_STATUS, BORN: BORN_STATUS}}
    Path(house.env["PP_UI_CHAT_SCRIPT"]).write_text(json.dumps({"faces": faces}), encoding="utf-8")


def rows_of(text: str) -> list[str]:
    return [one for one in text.split("\n") if "agents/" in one or "agent" in one]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-agents-season", T.script(answers={"delete": {"rc": 0, "out": ""}}))
    agents(house, [LIST])

    # --- the table says the team, the model and the effort ---------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "agents", "--size", "150x30")
    rows = done.stdout.split("\n")
    member, alone = T.cells_by_name(rows, "agent", REVIEWER), T.cells_by_name(rows, "agent", SOLO)
    if (done.returncode == 0 and member and alone and "team" not in member and "season" not in member
            and "status core-review" in house.journal_lines()):
        held("no team column, the teams read", f"{REVIEWER}: {sorted(member)}; the teams read with the agents")
    else:
        failures.append(f"  ✗ columns                     rc={done.returncode} {member} {alone} {house.journal_lines()} "
                        f"{done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- s on the Teams tab: the season of the team chosen, read only ----------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", "--size", "150x50")
    reads = [one for one in house.journal_lines() if one.startswith("status core-review")]
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "150x50", "--press", "s")
    title = P.title_of(done.stdout) or [""]
    body = [T.cells_of(one) for one in P.overlay_rows(done.stdout)]
    names = [cells[0] for cells in body if cells and cells[0] in ("all", "lead", "reviewer")]
    keys = next((one for one in P.overlay_rows(done.stdout) if "[esc]" in one), "")
    chat = house.chat_lines()
    reads_s = [one for one in house.journal_lines() if one.startswith("status core-review")]
    cells = {cells[0]: cells[-1] for cells in body if cells and cells[0] in ("all", "lead", "reviewer")}
    profile = house.render("--render", "teams", "--size", "150x50", "--press", "s,down,down,enter")
    top = P.title_of(P.on_top(profile.stdout)) or [""]
    top_keys = next((one for one in P.overlay_rows(P.on_top(profile.stdout)) if "[enter]" in one), "")
    played = [(name, "on" if on else "off") for name, on in
              T.switches_set(T.CORE["members"][1]["launch"]["packages"]).items()]
    said = next((one for one in P.overlay_rows(P.on_top(profile.stdout))
                 if T.in_order(one, *(word for pair in played for word in pair))), "")
    if (shown.returncode == 0 and done.returncode == 0 and "core-review" in title[0] and "season 1" in title[0]
            and names == ["all", "lead", "reviewer"] and keys and "ctrl+s" not in keys
            and not any(one.startswith("providers") for one in chat) and len(reads_s) == len(reads)
            and cells.get("all") == ON and "plan" in cells.get("reviewer", "")
            and cells.get("lead") == AS_ALL
            and profile.returncode == 0 and "reviewer" in top[0] and top_keys and "opens" not in top_keys and said):
        held("s on Teams opens the season read only", f"{title[0]!r}: {names}, packages {cells}; keys {keys!r}; no "
             f"providers, {len(reads_s)} status of the team as without s; enter: {top[0]!r}, closed, {said.strip()!r}")
    else:
        failures.append(f"  ✗ season read only            rc={done.returncode}/{profile.returncode} {title} {names} {keys!r} "
                        f"{chat} reads={len(reads)}/{len(reads_s)} {cells} {top} {top_keys!r} {said!r} "
                        f"{P.on_top(profile.stdout)[-1500:]!r} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-300:]!r}")

    done = house.render("--render", "agents", "--size", "150x30", "--press", "S")
    if done.returncode == 0 and not P.title_of(done.stdout):
        held("S on Agents opens nothing", "no overlay")
    else:
        failures.append(f"  ✗ S on agents                 rc={done.returncode} {P.title_of(done.stdout)} {done.stdout[-600:]!r}")

    # --- a team gesture reads the catalogue again --------------------------------------------------------------
    agents(house, [LIST, GROWN])
    house.clear_journal()
    done = house.render("--render", "agents", "--size", "150x30", "--press", f"3,{DELETE},2", "--wait", "none:1.5")
    lists = [one for one in house.chat_lines() if one.startswith("list")]
    if (done.returncode == 0 and house.gestures()[-1:] == ["team delete core-review --yes"] and len(lists) == 2
            and BORN in done.stdout):
        held("a team gesture reads the catalogue again", f"{house.gestures()[-1]}: {len(lists)} readings of the list, "
             f"{BORN} in the table without u")
    else:
        failures.append(f"  ✗ gesture reloads             rc={done.returncode} {house.gestures()} lists={len(lists)} "
                        f"{BORN in done.stdout} {done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    # --- the round sees the disk ---------------------------------------------------------------------------------
    env = dict(house.env)
    house.env["PP_UI_LIST_PERIOD"] = "1"              # the round at the bench's pace
    agents(house, [LIST] * 6)
    house.clear_journal()
    same = house.render("--render", "agents", "--size", "150x30", "--press", "rest:3")
    statuses_same = [one for one in house.chat_lines() if one.startswith("status agents/")]
    lists_same = [one for one in house.chat_lines() if one.startswith("list")]
    agents(house, [LIST, GROWN])
    house.clear_journal()
    grown = house.render("--render", "agents", "--size", "150x30", "--press", "rest:3")
    statuses_grown = [one for one in house.chat_lines() if one.startswith("status agents/")]
    lists_grown = [one for one in house.chat_lines() if one.startswith("list")]
    house.env = env
    if (same.returncode == 0 and len(lists_same) >= 2 and len(statuses_same) == 2 and BORN not in same.stdout
            and grown.returncode == 0 and len(lists_grown) >= 2 and statuses_grown.count(f"status {BORN} --json") == 1
            and len(statuses_grown) == 3 and BORN in grown.stdout):
        held("the round sees the disk", f"a list equal to the catalogue: {len(lists_same)} lists, {len(statuses_same)} "
             f"statuses (the first reading's); a list that gains {BORN}: its status alone, the table carries it")
    else:
        failures.append(f"  ✗ the round                   rc={same.returncode}/{grown.returncode} lists={lists_same}/{lists_grown} "
                        f"same={statuses_same} grown={statuses_grown} {grown.stdout[-1200:]!r} {grown.stderr[-300:]!r}")
    return 0
