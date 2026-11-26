"""The `stats` domain, layer `faces`: how the stats are put into words.

A definition belongs here when it turns the stats into what a user reads -- the line of a task or of a member, a
duration, a cost in its unit, a share, the text of a season, and the stats of every season of a journal
(`season_stats`), computed by the rules and put in lines here -- and gives it back without printing it. It reads
the journal's events decoded, by their fields; the `reply` key of an answer written before, which no body names, it
reads on the line.
"""
from __future__ import annotations

import math
from datetime import datetime

from stats.model import COST_BASES, SLOT
from stats.rules import (against_of, budget_of, by_band_of, by_duration_of, by_model_of, caps_of, costs_of,
                         delegations_of, known_of, member_against, models_of, moment, part_cost, per, per_each,
                         per_effort_hour_of, per_launch_of, ranked, root_of, seasons_median, shares_of, stopped_of,
                         task_against, task_cost_of, tasks_read, tasks_total, times_of, total_of, wakes_read)


def task_face(task: dict, wakes: list[dict], clock: datetime) -> dict:
    """-> one task's line of a season's stats, read on the season alone: what its wake-ups of the season cost in
    each base, its `do` and `re` there, its failed wake-ups, its three times (elapsed from its first to its last
    event of the season), the hours of those two events (`first`, `last`), the largest share of the context its
    wake-ups left, the cost of an hour of its effort (`per_effort_hour`)."""
    elapsed = (task["last"] - task["first"]).total_seconds() if task["first"] and task["last"] else 0
    hour = lambda at: None if at is None else at.isoformat()
    cost, times = costs_of(wakes), times_of(wakes, clock)
    return {"task": task["task"], "name": task["name"], "season": task["season"], "state": task["state"],
            "cost": cost, "do": task["do"], "re": task["re"],
            "failures": sum(1 for one in wakes if one["end"] == "wake-failed"),
            "time": {"elapsed": round(elapsed), **times},
            "first": hour(task["first"]), "last": hour(task["last"]),
            "context_max": max((one["used"] for one in wakes if one["used"] is not None), default=None),
            "per_effort_hour": per_effort_hour_of(cost, times["effort"])}


def member_face(member: str, roles: list[str], wakes: list[dict], posts: list[dict], answered: dict,
                clock: datetime) -> dict:
    """-> one member's line of a season's stats: its role keys, what it cost in each base and per launch, the `do`
    it received and the `re` it gave (the tick's apart), its failed wake-ups, its three times (elapsed from its first
    launch to its last end), the largest share of the context its wake-ups left, the median delay from a `do` it
    received to its first `re` citing it, the cost of an hour of its effort (`per_effort_hour`), the models of its
    launches, the most used first (`models_of`)."""
    cost, times = costs_of(wakes), times_of(wakes, clock)
    spans = [one for one in wakes if one["launched"] is not None]
    elapsed = ((max(one["ended"] or clock for one in spans) - min(one["launched"] for one in spans)).total_seconds()
               if spans else 0)
    dos = [one for one in posts if one.body.verb == "do" and one.body.to == member]
    delays = [(answered[one.id] - moment(one.at)).total_seconds() for one in dos
              if one.id in answered and moment(one.at) is not None]
    return {"member": member, "roles": roles, "models": models_of(wakes), "cost": cost,
            "per_launch": {"usd": per(cost["usd"], cost["launches"]), "tokens": per(cost["tokens"], cost["launches"])},
            "do": len(dos),
            "re": sum(1 for one in posts
                      if one.body.verb == "re" and one.body.sender == member and one.body.by != "tick"),
            "failures": sum(1 for one in wakes if one["end"] == "wake-failed"),
            "time": {"elapsed": round(max(0.0, elapsed)), **times},
            "context_max": max((one["used"] for one in wakes if one["used"] is not None), default=None),
            "do_re_median": None if not delays else round(ranked(delays, 0.5)),
            "per_effort_hour": per_effort_hour_of(cost, times["effort"])}


def lasted(seconds) -> str:
    """-> a duration said short: `8 s`, `52 min`, `1 h 49`; `-` for none."""
    if seconds is None:
        return "-"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} s"
    if seconds < 3600:
        return f"{seconds // 60} min"
    return f"{seconds // 3600} h {seconds % 3600 // 60:02d}"


def costed_as(cost: dict, base: str) -> str:
    """-> a cost said in its base: `41.2 USD`, `38 launches`, `1200000 tokens` (`~` when estimated), `-` unknown."""
    value = cost.get(base)
    if value is None:
        return "-"
    if base == "usd":
        return f"{value:.2f} USD"
    if base == "tokens":
        return f"{'~' if cost.get('tokens_estimated') else ''}{value} tokens"
    return f"{value} launches"


def share_said(value) -> str:
    return "-" if value is None else f"{round(100 * value)} %"


def said(value, decimals: int = 2) -> str:
    """-> a figure as the text says it, to be read: a cost, a pace, a median or a ratio with two decimals, hours with
    one (`decimals`), `-` for none -- the JSON keeps its four."""
    return "-" if value is None else f"{value:.{decimals}f}"


def ratio_said(judged: dict) -> str:
    """-> a measure against its median, `median 2.90 · x1.46`; `x-` without a ratio."""
    return f"median {said(judged['median'])} · x{said(judged['ratio'])}"


def head_lines(one: dict, base: str) -> list[str]:
    """-> the head of one season's stats as text, its costs said in `base`: what it spent, against its cap and at what
    pace when the base has one (`spent`), its delegations and its tasks (`work`), its cost per delegation against the
    median, and per effort hour and per launch when the base is not the launches (`price`), its launches per
    delegation against the median and its root member's share (`load`)."""
    unit = {"usd": "USD", "launches": "launches", "tokens": "tokens"}[base]
    tasks, cost, budget, root = one["tasks"], one["cost"], (one["budget"] or {}).get(base), one["root"]
    spent = f"  spent     {costed_as(cost, base)}" + ("" if budget is None else
                                                    f" of {costed_as({base: budget['cap']}, base)} · "
                                                    f"{share_said(budget['share'])} · "
                                                    f"{said(budget['per_active_hour'])} {unit} / active hour · "
                                                    f"{said(budget['hours_left'], 1)} h left")
    price = (f"  price     {said(one['per_delegation'][base])} {unit} / delegation · "
             f"{ratio_said(one['against']['per_delegation'][base])}")
    if base != "launches":
        price += (f" · {said(one['per_effort_hour'][base])} {unit} / effort hour · "
                  f"{said(one['per_launch'][base])} {unit} / launch")
    return [spent,
            f"  work      {one['delegations']} delegations · {tasks['closed']} closed · "
            f"{tasks['stopped']} stopped · {tasks['open']} open",
            price,
            f"  load      {said(one['per_delegation']['launches'])} launches / delegation · "
            f"{ratio_said(one['against']['per_delegation']['launches'])} · "
            f"root {root['member'] or '-'} {share_said(root['share'][base])}"]


def total_line(total: dict, base: str) -> str:
    """-> the total of the seasons played as one line of text, its costs said in `base`."""
    tasks = total["tasks"]
    return (f"  all   {total['seasons']} seasons  {costed_as(total['cost'], base)}  "
            f"{total['delegations']} delegations  {said(total['per_delegation'][base])} / delegation  "
            f"{tasks['closed']} closed · {tasks['stopped']} stopped · "
            f"{tasks['open']} open  {total['failed']} failed")


def part_said(label: str, one: dict, base: str) -> str:
    """-> a part of a season's launches as text, its costs said in `base`: its label, its launches, its cost and its
    share, its cost per launch and of an effort hour -- the cost and those two left out under `launches`, which the
    launches and the share say."""
    unit = {"usd": "USD", "launches": "launches", "tokens": "tokens"}[base]
    if base == "launches":
        return f"{label} {one['launches']} launches · {share_said(one['share'][base])}"
    return (f"{label} {one['launches']} launches · {costed_as(one['cost'], base)} · {share_said(one['share'][base])} · "
            f"{said(one['per_launch'][base])} {unit} / launch · {said(one['per_effort_hour'][base])} {unit} / effort hour")


def bound_said(one: dict, unit: str, scale: int = 1) -> str:
    """-> the bounds of a band, `60-180 s`, `90 %-` for the last one, without an end."""
    low = f"{round(one['from'] * scale)}"
    return f"{low}-{round(one['to'] * scale)} {unit}" if one["to"] is not None else f"{low} {unit}-"


def launches_lines(one: dict, base: str) -> list[str]:
    """-> the launches of one season as text, its costs said in `base`, ONE line each part (D10): a line `model` per
    line of `by_model`, a line `duration` per band of `by_duration`, a line `band` per band of `context.by_band`, each
    part said by `part_said`; then the cost by slot (`slots`)."""
    named = lambda line: (line["model"] or "no model") + (f" ({line['provider']})" if line["provider"] else "")
    figure = (lambda value: said(value)) if base == "usd" else (lambda value: "-" if value is None else f"{value}")
    slots = " ".join(figure(value) for value in one["time"]["cost_by_slot"][base])
    unit = {"usd": "USD", "launches": "launches", "tokens": "tokens"}[base]
    return [*(f"  model     {part_said(named(line), line, base)}" for line in one["by_model"]),
            *(f"  duration  {part_said(bound_said(line, 's'), line, base)}" for line in one["by_duration"]),
            *(f"  band      {part_said(bound_said(line, '%', 100), line, base)}" for line in one["context"]["by_band"]),
            f"  slots     cost by {lasted(one['time']['slot'])} at the end of a launch: {slots} {unit}"]


def season_lines(one: dict, base: str) -> list[str]:
    """-> one season's stats as text, its costs said in `base`: its head (`head_lines`), then each block, its launches
    among them (`launches_lines`)."""
    tasks, cost, times, losses = one["tasks"], one["cost"], one["time"], one["losses"]
    lines = [f"season {one['season']} · {one['state']} · {one['started']} -> {one['ended'] or 'now'} · "
             f"{lasted(times['elapsed'])}" + (" · empty" if one["empty"] else ""),
             *head_lines(one, base),
             f"  tasks     {tasks['closed']} closed · {tasks['stopped']} stopped · {tasks['open']} open",
             f"  cost      {costed_as(cost, base)} · {cost['launches']} launches",
             f"  time      {lasted(times['elapsed'])} elapsed · {lasted(times['active'])} active "
             f"({share_said(times['active_share'])}) · {lasted(times['effort'])} effort · "
             f"x{said(times['parallelism'])} parallel",
             f"  opening   median {lasted(one['opening']['median'])} · p90 {lasted(one['opening']['p90'])}",
             f"  principal {one['principal']['asked']} asked · {one['principal']['answered']} answered · "
             f"median {lasted(one['principal']['wait_median'])} · max {lasted(one['principal']['wait_max'])}",
             f"  context   median {share_said(one['context']['median'])} · p90 {share_said(one['context']['p90'])} · "
             f"{one['context']['renewals']} renewals",
             *launches_lines(one, base),
             f"  losses    {losses['failed']} failed ({costed_as(losses['cost'], base)}) "
             + " ".join(f"{reason} {count}" for reason, count in losses["reasons"].items())
             + f" · {losses['silences']} silences"]
    return lines


def season_stats(events: list[dict], clock: datetime) -> list[dict]:
    """-> the stats of every SEASON of a journal, oldest first -- a season runs from one `team-started` to the next,
    numbered by its rank from 1; computed from the journal's events alone, `clock` the hour a season or a wake-up still
    under way counts up to. A season ends at the next `team-started`, the last one at its `season-stopped`, or runs
    (`running`, `paused` under a pause). Each says its bounds and its state; `empty` when no wake-up launched in it; its
    tasks (`tasks_read`: born, woken, closed or stopped in it), counted by their state at its end -- born, closed,
    stopped, open --, each read on the season alone, so that its `by_task` sum to its cost; its `cost` in the three
    bases (`costs_of`); its `time` (elapsed, active, effort, their ratios, the effort by slot of `SLOT` seconds from
    its start, and the cost by slot in each base, each wake-up's in the slot of its end); the `opening` of a wake-up
    (`wake-intent` -> `wake-launched`); the `principal`'s questions (an `ask` of a member to the owner, a mandator or
    the team) and the wait of their first answer, and under `from_principal` the questions a principal asked a member
    (`post --ask`) and the wait of theirs; the `context` its wake-ups left at their end, the runs renewed, and its
    wake-ups by the band of that context (`by_band_of`); its `losses` -- the wake-ups failed, their cost and their
    reasons (the head of each reason, before its `:`), the silences --; its `delegations` (the `do` of its tasks'
    lines), its cost `per_delegation`, `per_launch` and `per_effort_hour`, its `root` member's cost and share, its
    tasks stopped at its end with their cost (`stopped_tasks`); its `budget` in time (`caps_of`, `budget_of`), None
    without a cap; its wake-ups `by_model` (`by_model_of`) and its finished launches `by_duration`
    (`by_duration_of`); then one line `by_task` and one `by_member` (`task_face`, `member_face`), each with its `share`
    of the season's cost and its cost `per_effort_hour`, a task's with its cost `per_delegation`; last, each season,
    each of its tasks and each of its members `against` the median of the seasons played, the season read among them
    (`against_of`, `task_against`, `member_against`)."""
    events = [one for one in events if one.kind != "snapshot"]
    starts = [rank for rank, one in enumerate(events) if one.kind == "team-started"]
    seasons, number = [], 0
    for rank, one in enumerate(events):
        if one.kind == "team-started":
            number += 1
        seasons.append(number)
    wakes = wakes_read(events, seasons)
    births = {}                                      # a task by its id -> its name and the season of its birth
    for rank, one in enumerate(events):
        if one.kind == "task" and one.body.task not in births:
            births[one.body.task] = {"name": one.body.name, "season": seasons[rank]}
    answered: dict[int, datetime] = {}               # a message by its id -> the hour of its first answer
    for one in events:
        if one.kind != "post":
            continue
        verb = one.body.verb                         # `reply`, the key of a reply of before, no body names: its line
        cited = one.body.re if verb == "re" else one.line.get("reply") if verb == "reply" else None
        if isinstance(cited, int) and cited not in answered and moment(one.at):
            answered[cited] = moment(one.at)
    found = []
    for number, rank in enumerate(starts, 1):
        started = events[rank]
        last = starts[number] if number < len(starts) else len(events)
        own = events[rank:last]
        stop = next((one for one in own if one.kind == "season-stopped"), None)
        pause = None
        for one in own:
            pause = one if one.kind == "paused" else None if one.kind == "unpaused" else pause
        begun = moment(started.at) or clock
        if number < len(starts):
            until, state = events[last].at, "stopped"
        elif stop is not None:
            until, state = stop.at, "stopped"
        else:
            until, state = None, "paused" if pause is not None else "running"
        ended = None if until is None else moment(until) or clock
        elapsed = max(0.0, ((ended or clock) - begun).total_seconds())
        mine = [one for one in wakes.values() if one["season"] == number]
        tasks = tasks_read(own, {tag: one for tag, one in wakes.items() if one["season"] == number}, births)
        held_tasks = list(tasks.values())
        posts = [one for one in own if one.kind == "post"]
        cost = costs_of(mine)
        closed = sum(1 for one in held_tasks if one["state"] == "resolved")
        times = times_of(mine, clock)
        slots = [0.0] * max(1, math.ceil(elapsed / SLOT))
        for one in mine:
            if one["launched"] is None:
                continue
            start = max(0.0, (one["launched"] - begun).total_seconds())
            end = max(start, ((one["ended"] or clock) - begun).total_seconds())
            while start < end:
                slot = int(start // SLOT)
                edge = min(end, (slot + 1) * SLOT)
                if slot >= len(slots):
                    slots.extend([0.0] * (slot + 1 - len(slots)))
                slots[slot] += edge - start
                start = edge
        ends: dict[int, list[dict]] = {}             # a wake-up's cost goes to the slot of its end, where it is written
        for one in mine:
            if one["launched"] is None and one["end"] is None:
                continue                             # an intent alone: no launch, no cost
            at = (one["ended"] if one["ended"] is not None else clock if one["end"] is None
                  else one["launched"] or one["intent"] or begun)   # in flight up to now, as its effort; an end
            #                                                         without an hour at its launch
            ends.setdefault(max(0, int((at - begun).total_seconds() // SLOT)), []).append(one)
        if ends and max(ends) >= len(slots):
            slots.extend([0.0] * (max(ends) + 1 - len(slots)))
        by_slot = [part_cost(ends.get(rank, []), cost) for rank in range(len(slots))]
        held = dict(started.body.roles or {})
        agents = list((started.body.agents or {}).keys())
        principals = {started.body.owner, started.team, *(started.body.principals or [])} - {None}
        asks = [one for one in posts if one.body.verb == "ask" and one.body.to in principals
                and one.body.sender in agents]
        waits = [(answered[one.id] - moment(one.at)).total_seconds() for one in asks
                 if one.id in answered and moment(one.at) is not None]
        questions = [one for one in posts if one.body.verb == "ask" and one.body.sender in principals
                     and one.body.to in agents]
        awaited = [(answered[one.id] - moment(one.at)).total_seconds() for one in questions
                   if one.id in answered and moment(one.at) is not None]
        openings = [(one["launched"] - one["intent"]).total_seconds() for one in mine
                    if one["launched"] is not None and one["intent"] is not None]
        used = [one["used"] for one in mine]
        failed = [one for one in mine if one["end"] == "wake-failed"]
        reasons: dict[str, int] = {}
        for one in failed:
            head = str(one["reason"] or "unknown").split(":")[0].strip()
            reasons[head] = reasons.get(head, 0) + 1
        by_task = [task_face(task, [wakes[tag] for tag in task["tags"]], clock) for task in held_tasks]
        for line in by_task:
            line.update(share=shares_of(line["cost"], cost), per_delegation=per_each(line["cost"], line["do"]))
        delegations = delegations_of(by_task)
        by_member = [member_face(member, [key for key, members in held.items() if member in members],
                                 [one for one in mine if one["agent"] == member], posts, answered, clock)
                     for member in agents]
        for line in by_member:
            line["share"] = shares_of(line["cost"], cost)
        found.append({
            "season": number, "started": started.at, "ended": until,
            "stopped": None if stop is None else stop.at, "state": state, "empty": not cost["launches"],
            "tasks": {"born": sum(1 for one in held_tasks if one["season"] == number), "closed": closed,
                      "stopped": sum(1 for one in held_tasks if one["state"] == "stopped"),
                      "open": sum(1 for one in held_tasks if one["state"] == "open")},
            "cost": cost, "delegations": delegations, "per_delegation": per_each(cost, delegations),
            "per_launch": per_launch_of(cost), "per_effort_hour": per_effort_hour_of(cost, times["effort"]),
            "root": root_of(started.body.root, mine, cost), "stopped_tasks": stopped_of(by_task, cost),
            "budget": budget_of(caps_of(started, [one for one in own if one.kind == "budget-raised"]), cost,
                                times["active"], state != "stopped"),
            "time": {"elapsed": round(elapsed), **times, "active_share": per(times["active"], round(elapsed)),
                     "parallelism": per(times["effort"], times["active"]), "slot": SLOT,
                     "effort_by_slot": [round(one) for one in slots],
                     "cost_by_slot": {base: [one[base] for one in by_slot] for base in COST_BASES}},
            "opening": {"count": len(openings), "median": ranked(openings, 0.5), "p90": ranked(openings, 0.9)},
            "principal": {"asked": len(asks), "answered": len(waits),
                          "wait_median": None if not waits else round(ranked(waits, 0.5)),
                          "wait_max": None if not waits else round(max(waits)),
                          "from_principal": {"asked": len(questions), "answered": len(awaited),
                                             "wait_median": None if not awaited else round(ranked(awaited, 0.5)),
                                             "wait_max": None if not awaited else round(max(awaited))}},
            "context": {"median": ranked(used, 0.5), "p90": ranked(used, 0.9),
                        "max": max((one for one in used if one is not None), default=None),
                        "renewals": sum(1 for one in own if one.kind == "run-renewed"),
                        "by_band": by_band_of(mine, cost, clock)},
            "losses": {"failed": len(failed), "cost": costs_of(failed), "reasons": reasons,
                       "silences": sum(1 for one in own if one.kind == "silence")},
            "by_model": by_model_of(mine, cost, clock), "by_duration": by_duration_of(mine, cost, clock),
            "by_task": by_task, "by_member": by_member})
    played = [one for one in found if not one["empty"]]
    median, known = seasons_median(played), known_of(played)
    for one in found:                                # each season against the seasons played, itself among them
        one["against"] = against_of(one, median, known)
        for line in one["by_task"]:
            line["against"] = task_against(line, median, known)
        for line in one["by_member"]:
            line["against"] = member_against(line, median, known)
    return found


def every_season(seasons: list[dict]) -> dict:
    """-> the stats of every season of a journal, `--all`: the seasons in which a wake-up launched, their median, the
    empty ones apart, each task over all its seasons (`tasks_total`); the `total` of the seasons played, their tasks
    once each; the `task_cost` over those same tasks, the launched ones."""
    full = [one for one in seasons if not one["empty"]]
    by_task, played = tasks_total(seasons), tasks_total(full)
    return {"seasons": full, "median": seasons_median(full),
            "empty": [one["season"] for one in seasons if one["empty"]],
            "by_task": by_task, "total": total_of(full, played), "task_cost": task_cost_of(played)}
