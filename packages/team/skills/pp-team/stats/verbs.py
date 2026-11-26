"""The `stats` domain, layer `verbs`: the command line of the verb that shows a team's stats.

A definition belongs here when it plays that verb: it reads its arguments, prints the stats of a season or of every
season as text or as JSON, and refuses with the usage. A verb is where the skill meets its caller: it may print, end the
call and use every other layer.
"""
from __future__ import annotations

import json
from datetime import timezone

from house.model import USAGE
from house.rules import journal_of, team_doc
from house.store import lines_of, machine_house, named_team, refuse, tick_now
from house.verbs import flags
from journal.model import Event
from stats.model import COST_BASES, STATS_FLAGS
from stats.faces import costed_as, every_season, said, season_lines, season_stats, share_said, total_line


def stats_verb(rest: list[str]) -> int:
    """`team stats`: the stats of a season of the team, computed from its journal alone (`season_stats`) -- the one
    under way or the last by default, `--season <n>` another, `--all` every season not empty with their median, the
    empty ones apart, each task over all its seasons, their total and the cost of a task (`every_season`);
    `--cost usd|launches|tokens` the base the text says its costs in, `--json` the object with the three bases.
    Nothing written."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, STATS_FLAGS)
    base = asked["cost"] or "usd"
    if asked["all"] and asked["season"] is not None:
        refuse(USAGE)
    if base not in COST_BASES:
        refuse(f"cost-invalid -- `--cost {base}`: one of {', '.join(COST_BASES)}.")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    seasons = season_stats([Event.of(line) for line in lines_of(journal_of(root, name))],   # decoded once read
                           tick_now().astimezone(timezone.utc))
    if not seasons:
        refuse(f"team-not-started -- {name} was never started.")
    if asked["all"]:
        every = {"team": name, "base": base, **every_season(seasons)}
        full = every["seasons"]
        if asked["json"]:
            print(json.dumps(every, ensure_ascii=False))
            return 0
        print(f"{name} · {len(seasons)} seasons · {len(every['empty'])} empty")
        for one in full:
            print(f"  s.{one['season']:<3} {str(one['started'])[:10]}  {costed_as(one['cost'], base):>16}  "
                  f"{one['tasks']['closed']:>3} closed  active {share_said(one['time']['active_share'])}  "
                  f"x{said(one['time']['parallelism'])}")
        print(total_line(every["total"], base))
        if every["empty"]:
            print("  empty: " + ", ".join(str(one) for one in every["empty"]))
        return 0
    chosen = seasons[-1]
    if asked["season"] is not None:
        chosen = next((one for one in seasons if str(one["season"]) == asked["season"]), None)
        if chosen is None:
            refuse(f"season-unknown -- {name} has no season `{asked['season']}`: its seasons are 1 to {len(seasons)}.")
    if asked["json"]:
        print(json.dumps({"team": name, "base": base, "season": chosen}, ensure_ascii=False))
        return 0
    print(f"{name} · " + "\n".join(season_lines(chosen, base)))
    return 0
