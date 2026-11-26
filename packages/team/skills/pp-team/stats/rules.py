"""The `stats` domain, layer `rules`: the stats of a team, computed from its journal's events.

A definition belongs here when it computes a figure from the events and the values it is given: the wake-ups and the
tasks read from the journal, their costs and their times, the median of the seasons. It reads no disk, no clock and no
environment and prints nothing: the time comes to it as an argument. The stats of each season, which compose lines and
decide nothing, are a face (`season_stats`, `stats/faces.py`).

The events come decoded: `stats_verb` decodes each line of the journal once, and a rule reads `one.kind`, `one.at` and
the fields of `one.body`. The stats read the whole history, so dead kinds too, such as `wait-met`, which have no body:
of those a rule reads only what the line carries, `one.line` -- as `task_of_event` does for the task and the tag of an
event of any kind.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

from stats.model import COMPARED, CONCENTRATION, CONTEXT_BANDS, COST_BASES, DURATIONS, ENDS, MEDIAN_OF


def moment(at) -> datetime | None:
    """-> an event's `at` as an aware datetime (a naive one read as UTC); None when it reads as none."""
    try:
        found = datetime.fromisoformat(str(at))
    except (TypeError, ValueError):
        return None
    return found if found.tzinfo is not None else found.replace(tzinfo=timezone.utc)


def ranked(values: list, share: float):
    """-> the value at `share` of the values by the NEAREST RANK -- the ceil(share x n)-th of them sorted, the
    first for share 0 --, None without a value: the one rule of every median (0.5) and p90 (0.9) of the stats."""
    found = sorted(one for one in values if one is not None)
    if not found:
        return None
    return found[max(0, math.ceil(share * len(found)) - 1)]


def spans_union(spans: list[tuple[datetime, datetime]]) -> float:
    """-> the seconds of wall time at least one of the spans covers."""
    total, reach = 0.0, None
    for start, end in sorted(spans):
        if reach is None or start > reach:
            total += (end - start).total_seconds()
            reach = end
        elif end > reach:
            total += (end - reach).total_seconds()
            reach = end
    return total


def costs_of(wakes: list[dict]) -> dict:
    """-> what the wake-ups cost in each base: `usd` the sum of the costs reported (None when none reports one,
    never 0), `launches` the wake-ups launched, `tokens` the tokens sent -- a wake-up without `tokens` counts its
    end's `context.tokens`, the floor of one call, and makes the sum `tokens_estimated` --, None when no wake-up
    measured any."""
    usd = [one["usd"] for one in wakes if one["usd"] is not None]
    tokens = [one["tokens"] for one in wakes if one["tokens"] is not None]
    return {"usd": round(sum(usd), 6) if usd else None,
            "launches": sum(1 for one in wakes if one["launched"] is not None),
            "tokens": sum(tokens) if tokens else None,
            "tokens_estimated": any(one["estimated"] for one in wakes)}


def per(value, count):
    """-> value / count, None when either is none or the count is 0."""
    if value is None or not count:
        return None
    return round(value / count, 4)


def per_hour(value, seconds):
    """-> value per hour of `seconds`, None when either is none or the seconds are 0."""
    if value is None or not seconds:
        return None
    return round(value * 3600 / seconds, 4)


def per_each(cost: dict, count) -> dict:
    """-> a cost divided by a count in each base, `{usd, launches, tokens}`: None where the cost is none or the count
    0 -- the cost per delegation when the count is the delegations."""
    return {base: per(cost[base], count) for base in COST_BASES}


def shares_of(part: dict, whole: dict) -> dict:
    """-> the share of a cost in a whole cost in each base, `{usd, launches, tokens}`: None where either is none or the
    whole 0."""
    return {base: per(part[base], whole[base]) for base in COST_BASES}


def delegations_of(lines: list[dict]) -> int:
    """-> the delegations of a season: the `do` its tasks' lines count, the one that opens a task included."""
    return sum(one["do"] for one in lines)


def per_launch_of(cost: dict) -> dict:
    """-> what one launch cost, `{usd, tokens}`: said without a comparison."""
    return {"usd": per(cost["usd"], cost["launches"]), "tokens": per(cost["tokens"], cost["launches"])}


def per_effort_hour_of(cost: dict, effort) -> dict:
    """-> the cost of an hour of effort, `{usd, tokens}`: the cost divided by the effort in hours, the effort of the
    failed wake-ups included -- an hour lost makes the hour dearer."""
    return {"usd": per_hour(cost["usd"], effort), "tokens": per_hour(cost["tokens"], effort)}


def costs_summed(costs: list[dict]) -> dict:
    """-> costs added up base by base: `usd` and `tokens` None where none measured one, `tokens_estimated` where one
    says it."""
    usd = [one["usd"] for one in costs if one["usd"] is not None]
    tokens = [one["tokens"] for one in costs if one["tokens"] is not None]
    return {"usd": round(sum(usd), 6) if usd else None, "launches": sum(one["launches"] for one in costs),
            "tokens": sum(tokens) if tokens else None,
            "tokens_estimated": any(one["tokens_estimated"] for one in costs)}


def stopped_of(lines: list[dict], cost: dict) -> dict:
    """-> the tasks stopped among the lines given, `{tasks, cost, share}`: how many, what they cost in each base, the
    share of `cost` it is -- a season's tasks stopped at its end, or every task's last state over the seasons. Where
    `cost` is known, the part and its share are 0 when no stopped task measured one, never None: a share of 0 is
    judged, an absent one is not."""
    stopped = [one for one in lines if one["state"] == "stopped"]
    part = costs_summed([one["cost"] for one in stopped])
    for base in COST_BASES:
        if cost[base] is not None and part[base] is None:
            part[base] = 0.0 if base == "usd" else 0
    share = {base: None if cost[base] is None else per(part[base], cost[base]) or 0.0 for base in COST_BASES}
    return {"tasks": len(stopped), "cost": part, "share": share}


def root_of(member: str | None, wakes: list[dict], cost: dict) -> dict:
    """-> the root member of a team in a season, `{member, cost, share}`: what its wake-ups cost in each base and the
    share of the season's cost it is; without a root, its cost and share None in the three bases."""
    if member is None:
        return {"member": None, "cost": {**{base: None for base in COST_BASES}, "tokens_estimated": False},
                "share": {base: None for base in COST_BASES}}
    part = costs_of([one for one in wakes if one["agent"] == member])
    return {"member": member, "cost": part, "share": shares_of(part, cost)}


def caps_of(started, raised: list) -> dict:
    """-> the caps of a season, `{usd, launches}`: what its `team-started` bounds -- its `limits`, its `season` over
    them, as the season's fold reads them --, raised by each `budget-raised` of the season in its order; None where
    nothing caps."""
    limits = {**dict(started.body.limits or {}),
              **{key: value for key, value in (started.body.season or {}).items() if value is not None}}
    usd, launches = limits.get("budget"), limits.get("budget-launches")
    for one in raised:
        if one.body.budget is not None:
            usd = one.body.budget
        if one.body.launches is not None:
            launches = one.body.launches
    return {"usd": None if usd is None else float(usd), "launches": None if launches is None else int(launches)}


def budget_of(caps: dict, cost: dict, active, running: bool) -> dict | None:
    """-> a season's budget in time, `{usd, launches}`, each `{cap, spent, share, per_active_hour, hours_left}`: its
    cap, what the season spent, its share of the cap, the pace of the spending per hour of active time, and the hours
    left at that pace -- the rest of the cap divided by the pace, the reserve of the wake-ups under way not counted,
    None once the season is stopped or without a pace --; a base None without a cap, the whole None without any."""
    def held(cap, spent):
        if cap is None:
            return None
        rest = max(0.0, cap - spent)
        return {"cap": cap, "spent": spent, "share": per(spent, cap), "per_active_hour": per_hour(spent, active),
                "hours_left": per(rest * active / 3600, spent) if running and active else None}
    if caps["usd"] is None and caps["launches"] is None:
        return None
    return {"usd": held(caps["usd"], round(cost["usd"] or 0.0, 6)),
            "launches": held(caps["launches"], cost["launches"])}


def times_of(wakes: list[dict], clock: datetime) -> dict:
    """-> the active time of the wake-ups (the union of their spans `wake-launched` -> end, a wake-up in flight up
    to `clock`) and their effort (the sum of those spans), in seconds."""
    spans = [(one["launched"], one["ended"] or clock) for one in wakes if one["launched"] is not None]
    spans = [(start, max(start, end)) for start, end in spans]
    return {"active": round(spans_union(spans)),
            "effort": round(sum((end - start).total_seconds() for start, end in spans))}


def wakes_read(events: list[dict], seasons: list[int]) -> dict[str, dict]:
    """-> every wake-up of the journal by its tag: its member, its task, its season (that of its intent), the hours
    of its intent, launch and end, the kind of its end and its reason, what it cost in each base, the share of
    the context its end left (`used`), the `model` and the `provider` its `wake-launched` names (None where it names
    none), and its `duration` in seconds from its launch to its end -- None for a wake-up not launched or not ended --,
    read in the same one pass."""
    wakes: dict[str, dict] = {}
    for rank, one in enumerate(events):
        kind = one.kind
        if kind == "wake-intent":
            body = one.body
            wakes[body.tag] = {"tag": body.tag, "agent": body.agent, "task": body.task, "season": seasons[rank],
                               "intent": moment(one.at), "launched": None, "ended": None, "end": None,
                               "reason": None, "usd": None, "tokens": None, "estimated": False, "used": None,
                               "model": None, "provider": None, "duration": None}
            continue
        if kind != "wake-launched" and kind not in ENDS:   # the kinds that carry a wake-up's tag and are read here
            continue
        wake = wakes.get(one.body.tag)
        if wake is None:
            continue
        if kind == "wake-launched" and wake["launched"] is None:
            wake.update(launched=moment(one.at), model=one.body.model, provider=one.body.provider)
        elif kind in ENDS and wake["end"] is None:
            body = one.body                        # of the four ends, a failure alone says a reason, a kill no cost,
            #                                        an end alone its context and its tokens
            wake.update(ended=moment(one.at), end=kind, reason=body.reason if kind == "wake-failed" else None)
            cost = body.cost if kind != "wake-killed" else None
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                wake["usd"] = float(cost)
            said = body.context if kind == "wake-ended" else None
            context = said if isinstance(said, dict) else {}
            sent, floor = body.tokens if kind == "wake-ended" else None, context.get("tokens")
            if isinstance(sent, int) and not isinstance(sent, bool):
                wake["tokens"] = sent
            elif isinstance(floor, int) and not isinstance(floor, bool):
                wake["tokens"], wake["estimated"] = floor, True
            if kind == "wake-ended" and isinstance(context.get("used"), (int, float)):
                wake["used"] = float(context["used"])
    for wake in wakes.values():                    # the wake-ups read, not the journal again
        if wake["launched"] is not None and wake["ended"] is not None:
            wake["duration"] = max(0.0, (wake["ended"] - wake["launched"]).total_seconds())
    return wakes


def part_cost(wakes: list[dict], whole: dict) -> dict:
    """-> what a part of a season's wake-ups cost (`costs_of`), where `whole` is the season's cost: 0 in each base
    where the season's cost is known and no wake-up of the part reports one -- a band, a line or a slot without a
    launch, or whose wake-ups report no cost, costs nothing, it is not unknown (D11, D12) --, None where the season's
    is unknown."""
    cost = costs_of(wakes)
    for base, nothing in (("usd", 0.0), ("tokens", 0)):
        if cost[base] is None and whole[base] is not None:
            cost[base] = nothing
    return cost


def part_share(cost: dict, whole: dict) -> dict:
    """-> the share of a part's cost in the season's, base by base: 0 for a part that costs nothing where the season's
    cost is known, None where it is unknown."""
    return {base: None if whole[base] is None else 0.0 if cost[base] == 0 else per(cost[base], whole[base])
            for base in COST_BASES}


def part_of(wakes: list[dict], whole: dict, clock: datetime) -> dict:
    """-> what a part of a season's wake-ups weighs, `{launches, cost, share, effort, per_launch, per_effort_hour}`:
    its launches, its cost in each base and its share of the season's cost (`whole`), its effort in seconds (a wake-up
    in flight up to `clock`), its cost per launch and of an effort hour; a part whose wake-ups report no cost, or
    without one, costs 0 and its share is 0 where the season's cost is known (`part_cost`, `part_share`), its cost per
    launch and per effort hour None without a launch or an effort."""
    cost, effort = part_cost(wakes, whole), times_of(wakes, clock)["effort"]
    return {"launches": cost["launches"], "cost": cost, "share": part_share(cost, whole), "effort": effort,
            "per_launch": per_launch_of(cost), "per_effort_hour": per_effort_hour_of(cost, effort)}


def by_model_of(wakes: list[dict], whole: dict, clock: datetime) -> list[dict]:
    """-> a season's wake-ups by the model and the provider their `wake-launched` names, one line each, `{model,
    provider, ...part_of}`: the most launched first, the line without a model last -- the launches whose
    `wake-launched` names none, and the ends without a launch that carry a cost (`launch-refused`, `launch-failed`),
    their model unknown: never under a model guessed (D10, D12). A wake-up never launched that carries no cost is in no
    line; the shares add up to 1 in each base where the season's cost is known."""
    groups: dict[tuple, list[dict]] = {}
    for one in wakes:
        if one["launched"] is None and one["usd"] is None and one["tokens"] is None:
            continue
        groups.setdefault((one["model"], one["provider"]), []).append(one)
    lines = [{"model": model, "provider": provider, **part_of(held, whole, clock)}
             for (model, provider), held in groups.items()]
    return sorted(lines, key=lambda one: (one["model"] is None, -one["launches"]))


def models_of(wakes: list[dict]) -> list:
    """-> the models of a member's launches, the most used first -- at a tie, the first come --, None last for its
    launches that name none."""
    counts: dict = {}
    for one in wakes:
        if one["launched"] is not None:
            counts[one["model"]] = counts.get(one["model"], 0) + 1
    named = sorted((one for one in counts if one is not None), key=lambda one: -counts[one])
    return named + ([None] if None in counts else [])


def bands_of(wakes: list[dict], bounds: tuple, measure, whole: dict, clock: datetime) -> list[dict]:
    """-> one line per band of `bounds`, in their order, `{from, to, launches, cost, share, per_launch,
    per_effort_hour}` (`part_of`, its effort left out): the wake-ups whose `measure` stands from the band's bound, that
    bound included, to the next one, the last band without an end -- a wake-up without a measure in no band, never in
    one guessed."""
    lines = []
    for rank, low in enumerate(bounds):
        high = bounds[rank + 1] if rank + 1 < len(bounds) else None
        held = [one for one in wakes if measure(one) is not None and measure(one) >= low
                and (high is None or measure(one) < high)]
        part = part_of(held, whole, clock)
        del part["effort"]
        lines.append({"from": low, "to": high, **part})
    return lines


def by_duration_of(wakes: list[dict], whole: dict, clock: datetime) -> list[dict]:
    """-> a season's finished launches by the band of their duration (`DURATIONS`): what the opening of a launch
    costs."""
    return bands_of(wakes, DURATIONS, lambda one: one["duration"], whole, clock)


def by_band_of(wakes: list[dict], whole: dict, clock: datetime) -> list[dict]:
    """-> a season's wake-ups by the band of the context their end left (`CONTEXT_BANDS`): what the context adds to
    the hour."""
    return bands_of(wakes, CONTEXT_BANDS, lambda one: one["used"], whole, clock)


def tasks_read(own: list[dict], wakes: dict[str, dict], births: dict[str, dict]) -> dict[str, dict]:
    """-> the tasks of ONE season by their id, in the order they come in it: a task born in it (its `task` event),
    woken in it (a `wake-intent` on it) or closed or stopped in it (its `done`, its `stopped`). Each says its name, the
    season it was born in, its state at the season's end -- `resolved` at its `done`, `stopped` at its `stopped`,
    `open` again at its `resumed`, `open` when the season says none --, the hours of its first and last event in the
    season, its `do` and its `re` there (the tick's apart), and its wake-ups of the season by their tags."""
    def task_of_event(one) -> str | None:              # any kind, a dead one without a body among them: its line
        line = one.line
        return line.get("task") if line.get("task") else (wakes.get(line.get("tag")) or {}).get("task")
    tasks: dict[str, dict] = {}
    for one in own:
        kind = one.kind
        if kind in ("task", "done", "stopped"):
            task = one.body.task
        elif kind == "wake-intent" and wakes.get(one.body.tag):
            task = one.body.task or wakes[one.body.tag].get("task")
        else:
            continue
        if task and task not in tasks:
            born = births.get(task) or {}
            tasks[task] = {"task": task, "name": born.get("name"), "season": born.get("season"), "state": "open",
                           "first": None, "last": None, "do": 0, "re": 0, "tags": []}
    for one in own:
        held = tasks.get(task_of_event(one))
        if held is None:
            continue
        kind, at = one.kind, moment(one.at)
        if at is not None:
            held["first"] = at if held["first"] is None else min(held["first"], at)
            held["last"] = at if held["last"] is None else max(held["last"], at)
        if kind == "wake-intent" and one.body.tag in wakes:
            held["tags"].append(one.body.tag)
        elif kind == "done":
            held["state"] = "resolved"
        elif kind == "stopped" and held["state"] == "open":
            held["state"] = "stopped"
        elif kind == "resumed" and held["state"] == "stopped":
            held["state"] = "open"
        elif kind == "post" and one.body.verb == "do":
            held["do"] += 1
        elif kind == "post" and one.body.verb == "re" and one.body.by != "tick":
            held["re"] += 1
    return tasks


def tasks_total(seasons: list[dict]) -> list[dict]:
    """-> each task's line over all the seasons, in the order it first comes, without `season` nor what a season
    judges (`share`, `against`): its season lines summed -- its costs base by base (None where no season measured one;
    `tokens_estimated` where one says it), its `do`, its `re`, its failures, its active time and its effort --, its
    `first` event the earliest of theirs and its `last` the latest, its elapsed time the wall between them, the largest
    share of the context they say, its name and its state as its last line says them, the `seasons` its lines come
    from, its cost `per_delegation` and of an effort hour (`per_effort_hour`) over them all."""
    plus = lambda one, other: None if one is None and other is None else round((one or 0) + (other or 0), 6)
    found: dict[str, dict] = {}
    for season in seasons:
        for line in season["by_task"]:
            held = found.get(line["task"])
            if held is None:
                found[line["task"]] = {**{key: value for key, value in line.items()
                                          if key not in ("season", "share", "against")},
                                       "cost": dict(line["cost"]), "time": dict(line["time"]),
                                       "seasons": [season["season"]]}
                continue
            held["seasons"].append(season["season"])
            held.update(name=line["name"], state=line["state"], do=held["do"] + line["do"], re=held["re"] + line["re"],
                        failures=held["failures"] + line["failures"],
                        context_max=max((one for one in (held["context_max"], line["context_max"]) if one is not None),
                                        default=None))
            cost = held["cost"]
            cost.update(usd=plus(cost["usd"], line["cost"]["usd"]),
                        launches=cost["launches"] + line["cost"]["launches"],
                        tokens=plus(cost["tokens"], line["cost"]["tokens"]),
                        tokens_estimated=cost["tokens_estimated"] or line["cost"]["tokens_estimated"])
            for key in ("active", "effort"):
                held["time"][key] += line["time"][key]
            if moment(line["first"]) is not None and (moment(held["first"]) is None
                                                      or moment(line["first"]) < moment(held["first"])):
                held["first"] = line["first"]
            if moment(line["last"]) is not None and (moment(held["last"]) is None
                                                     or moment(line["last"]) > moment(held["last"])):
                held["last"] = line["last"]
            if moment(held["first"]) is not None and moment(held["last"]) is not None:
                held["time"]["elapsed"] = round((moment(held["last"]) - moment(held["first"])).total_seconds())
    for held in found.values():
        held["per_delegation"] = per_each(held["cost"], held["do"])
        held["per_effort_hour"] = per_effort_hour_of(held["cost"], held["time"]["effort"])
    return list(found.values())


def seasons_median(seasons: list[dict]) -> dict:
    """-> the median of each measure of `MEDIAN_OF` over the seasons given, in their shape."""
    found: dict = {}
    for group, key in MEDIAN_OF:
        found.setdefault(group, {})[key] = ranked([one[group][key] for one in seasons], 0.5)
    return found


def judged(value, median, over: int) -> dict:
    """-> a measure against the median of the seasons played, `{median, ratio, over}`: the median, the measure divided
    by it -- None when either is none or the median 0: a null median judges nothing --, the seasons it is taken over."""
    return {"median": median, "ratio": per(value, median), "over": over}


def known_of(seasons: list[dict]) -> dict:
    """-> for each measure of `COMPARED`, how many of the seasons given hold a value of it -- those its median is
    taken over --, in their shape: `{group: {key: count}}`."""
    found: dict = {}
    for group, key in COMPARED:
        found.setdefault(group, {})[key] = sum(1 for one in seasons if one[group][key] is not None)
    return found


def against_of(season: dict, median: dict, known: dict) -> dict:
    """-> each measure of `COMPARED` of a season against its median, in their shape: `{group: {key: judged}}`, over
    the seasons that hold a value of it (`known_of`)."""
    found: dict = {}
    for group, key in COMPARED:
        found.setdefault(group, {})[key] = judged(season[group][key], median[group][key], known[group][key])
    return found


def hour_against(line: dict, median: dict, known: dict) -> dict:
    """-> a line's cost of an effort hour against the median of the seasons' one, `{usd, tokens}`, each `judged` over
    the seasons that hold a value of it -- the same median as the season's."""
    return {base: judged(line["per_effort_hour"][base], median["per_effort_hour"][base], known["per_effort_hour"][base])
            for base in ("usd", "tokens")}


def task_against(line: dict, median: dict, known: dict) -> dict:
    """-> a task's cost per delegation and of an effort hour against the median of the seasons' ones:
    `{per_delegation: {usd, launches, tokens}, per_effort_hour: {usd, tokens}}`, each `judged` over the seasons that
    hold a value of it."""
    return {"per_delegation": {base: judged(line["per_delegation"][base], median["per_delegation"][base],
                                            known["per_delegation"][base]) for base in COST_BASES},
            "per_effort_hour": hour_against(line, median, known)}


def member_against(line: dict, median: dict, known: dict) -> dict:
    """-> a member's cost of an effort hour against the median of the seasons' one: `{per_effort_hour: {usd,
    tokens}}`."""
    return {"per_effort_hour": hour_against(line, median, known)}


def total_of(seasons: list[dict], lines: list[dict]) -> dict:
    """-> the seasons given added up, an empty one adding nothing: how many, their cost base by base (None where none
    measured one), their delegations, the cost per delegation, per launch and per effort hour over them all, their
    failures; and, from the lines of their tasks over all of them (`tasks_total`), each task once, its tasks by their
    last state, those stopped with their cost (`stopped_tasks`)."""
    cost = costs_summed([one["cost"] for one in seasons])
    delegations = sum(one["delegations"] for one in seasons)
    return {"seasons": len(seasons), "cost": cost, "delegations": delegations,
            "per_delegation": per_each(cost, delegations), "per_launch": per_launch_of(cost),
            "per_effort_hour": per_effort_hour_of(cost, sum(one["time"]["effort"] for one in seasons)),
            "tasks": {"closed": sum(1 for one in lines if one["state"] == "resolved"),
                      "stopped": sum(1 for one in lines if one["state"] == "stopped"),
                      "open": sum(1 for one in lines if one["state"] == "open")},
            "stopped_tasks": stopped_of(lines, cost), "failed": sum(one["losses"]["failed"] for one in seasons)}


def concentration_of(values: list) -> dict:
    """-> how many of the costs given, the dearest first, carry `CONCENTRATION` of their sum, `{tasks, of}`: `of` the
    costs known; `tasks` None when they sum to nothing."""
    found = sorted((one for one in values if one is not None), reverse=True)
    whole, reach = sum(found), 0
    if not found or whole <= 0:
        return {"tasks": None, "of": len(found)}
    for rank, one in enumerate(found, 1):
        reach += one
        if reach >= CONCENTRATION * whole:
            return {"tasks": rank, "of": len(found)}
    return {"tasks": len(found), "of": len(found)}


def task_cost_of(lines: list[dict]) -> dict:
    """-> the cost of a task over the lines given that launched at least one wake-up, base by base: its `median`, its
    `p90` and its `concentration` -- the same tasks in every base, a cost not known aside."""
    launched = [one for one in lines if one["cost"]["launches"]]
    found = {}
    for base in COST_BASES:
        values = [one["cost"][base] for one in launched]
        found[base] = {"median": ranked(values, 0.5), "p90": ranked(values, 0.9),
                       "concentration": concentration_of(values)}
    return found
