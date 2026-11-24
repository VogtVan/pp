"""Scenario `ui-tasks-stats` -- the cells of the Tasks table read by Textual's pilot, on the bench's `pp-team` witness
replaying the faces of `team` for three declared teams -- `core-review` and `ops` started, `veille` never (`_tasks`):
- a task's name and its holders each held to `TASK_CELL` cells of `palette.py`, the last `…` past it, on a task with a
  long name and four holders
- what `team stats <name> --all --json` says of each task over all its seasons (its `by_task`; T3 worked in two), in
  the table's columns: its elapsed time and its effort, its cost, its launches, its `do` and its `re`, its failures,
  its largest share of the context -- a task the stats do not name, its cells empty; `stats <name> --all` read per
  team started, its refusal no stats; T3's elapsed time the wall from the first event of its first season to the
  last of its second (`first`, `last`), its active time and its effort summed
- the base of the costs chosen in the settings (batch la-base-de-cout-en-reglages, s.1921): the footer's key opens
  them; `launches`, then `tokens`, chosen in their list -- `escape` then asks before losing it, a second `escape`
  gives the settings back -- and sent, is the base the Teams tab and the Tasks table hold,
  the titles of the summary and of the dashboard say it, a click on its word in the summary's title changes nothing;
  the cost in USD first, then its column under a title of its own in each base -- never `lnch`, the launches'
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-stats")

    # --- what team stats says of each task: elapsed, effort, cost, launches, do, re, failures, ctx max ----------
    script = T.script(stats={"core-review": S.STATS})
    script["states"]["core-review"] = [{**T.CORE, "tasks": T.CORE["tasks"] + [S.LONG]}]
    house.use(script)
    house.clear_journal()
    [(rc, seen, err)] = T.piloted(bench, house, "ui-tasks-stats", S.PROBE, "tasks")
    columns, lines = seen.get("columns") or [], seen.get("rows") or []
    row_of = lambda task, team, read=(columns, lines): next(
        (dict(zip(read[0], one)) for one in read[1] if one[:1] == [task] and team in one), {})
    t3, t1 = row_of("T3", "core-review"), row_of(T.OPS["tasks"][0]["id"], "ops")
    reads = {one for one in house.journal_lines() if one.startswith("stats ") and one.endswith(" --all")}
    t9 = row_of(S.LONG["id"], "core-review")
    held_to = {one: (len(t9.get(one, "")), t9.get(one, "")[-1:] == S.CUT) for one in ("task", "holder")}
    if isinstance(S.CELL, int) and held_to == {"task": (S.CELL, True), "holder": (S.CELL, True)}:
        held("a task's name and its holders held to their cells", f"T9's name ({len(S.LONG['name'])}) and its four "
             f"holders: {held_to}, {S.CELL} cells at most, the last the mark of a cut")
    else:
        failures.append(f"  ✗ cells held                  rc={rc} CELL={S.CELL!r} {held_to} {t9} {err[-600:]!r}")
    if (rc == 0 and columns == list(S.COLUMNS) and [t3.get(one) for one in S.COLUMNS[6:]] == S.SAID
            and [t1.get(one) for one in S.COLUMNS[6:]] == [""] * 8
            and reads == {"stats core-review --all", "stats ops --all"}):
        held("each task's numbers come from team stats", f"{columns[6:]}: T3 over its two seasons {S.SAID}; ops' "
             f"{T.OPS['tasks'][0]['id']} without stats, its cells empty; read {sorted(reads)}")
    else:
        failures.append(f"  ✗ stats columns               rc={rc} {columns} t3={t3} t1={t1} {reads} {err[-1500:]!r}")
    based = {base: seen.get(base) or [[], []] for base in S.BASED}
    found = {base: (read[0][8:9], row_of("T3", "core-review", read).get(S.BASED[base][0]),
                    row_of("T3", "core-review", read).get("lnch"), len(set(read[0])) == len(read[0]))
             for base, read in based.items()}
    said = {base: seen.get(f"{base}-said") for base in S.BASED}
    if (rc == 0 and seen.get("first") == ["usd", "usd"]
            and all(one == ["SettingsScreen", "ConfirmScreen", "SettingsScreen", base, base, True, True, base] for base, one in said.items())
            and all(said == ([title], cost, "4", True) for (title, cost), said in zip(S.BASED.values(), found.values()))):
        held("the cost follows the base chosen in the settings", f"usd first; {S.SETTINGS_KEY} opens the settings, escape on a choice changed asks, "
             "each base chosen there held by the Teams tab and the Tasks table, said by the titles of the summary and of "
             "the dashboard, unchanged by a click on its word; the cost column under its own title, never lnch's -- "
             f"{', '.join(f'{base} {title} {cost}' for base, (title, cost) in S.BASED.items())}; lnch 4 beside it")
    else:
        failures.append(f"  ✗ base of the cost            first={seen.get('first')} {said} {found} {err[-800:]!r}")
    house.use(T.script())
    return 0
