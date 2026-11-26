"""The `season` domain, layer `rules`: what a season says, and what opening, holding and closing it writes.

A definition belongs here when it computes its answer from its arguments alone: the season a start asks for, the
packages switched on or off for a member, a member's profile, what a start kept, the gap between the season and the
team, whether a name is a member or a principal, the words of a refused context limit (`context_invalid`). It also holds
the DECISIONS of the season that read only the season and what comes before it, composing by `made` the bodies the
journal's writer receives: `team start`, judged before the hour is read (`start_asked`, which says whether a season
taken back needs it) and composed as `team-started` (`team_started`); the refusals of `team stop` (`season_asked`) and
its `season-stopped` (`season_stopped`), which receives the tasks and the recurrences stopped as values; `team pause`
(`paused_decided`); a paused team taken back (`unpause_asked`, `unpaused_decided`). The task and the post a start opens,
the tasks a stop chooses and what it writes of them are decided in `task/rules.py`, a recurrence stopped in
`rhythm/rules.py`: a decision lives in the domain whose bodies it composes. A decision DECLINES by a code, and the verb
or the act says the sentence; `limit_of`, which reads the words of a flag, declines by the sentence the refusal prints,
and its verb refuses it. No rule here refuses. It reads no disk, no clock and no environment and prints nothing: the
hour and what a verb read come to it as values, and what needs the system belongs to `store` or to a verb.
"""
from __future__ import annotations

import re

from house.model import MINUTE, Declined, decline
from declaration.model import DEFAULT_SCHEDULE
from season.model import LAUNCH_FLAGS, PENDING, SEASON_LIMITS, Paused, SeasonStopped, TeamStarted, Unpaused
from template.rules import season_said


def path_of(state: dict, member: str) -> str:
    """-> the path of the agent that plays `member`, read at `team-started.agents`: the team
    speaks names, the house addresses its agents by their paths."""
    started = state.season.started
    return str(((started.body.agents if started is not None else None) or {}).get(member, member))


def schedule_seconds(started: dict | None) -> int | None:
    """-> the net's step in seconds as the start kept it: `team-started.schedule` with its `unit` (`s`, team 0.41.0),
    minutes when a journal written before kept no unit, DEFAULT_SCHEDULE when the start kept nothing; None under
    `off`."""
    if started is None or "schedule" not in started.line:   # kept, even at null: the line says
        return DEFAULT_SCHEDULE
    value = started.body.schedule
    if value is None:
        return None
    return int(value) if started.body.unit == "s" else int(value) * MINUTE


def season_changes(asked: dict, packages: list, profiles: dict) -> list[tuple]:
    """-> the changes the season's FLAGS make to SEASON.md, in the form `values_written` takes -- a team's flag its
    key, a `--package` its line of `packages:`, a member's flag its key on the member's line of `profiles:`, the
    member's other tokens at their place --; [] when no flag gives a value. The one writer of these keys, for `start`
    (`season_flagged`) and for `declare --season`."""
    scalars = {key: asked[key] for key in (*LAUNCH_FLAGS, *SEASON_LIMITS) if asked.get(key) is not None}

    def profile_line(old: str | None, member: str, given: dict) -> str:
        tokens = old.split()[1:] if old else []
        pairs = [(key, str(value)) for key, value in given.items() if key != "packages"]
        pairs += [(f"package.{one.partition('=')[0]}", one.partition("=")[2]) for one in given.get("packages") or []]
        for key, value in pairs:
            at = next((rank for rank, token in enumerate(tokens) if token.partition("=")[0] == key), None)
            if at is None:
                tokens.append(f"{key}={value}")
            else:
                tokens[at] = f"{key}={value}"
        return " ".join([member, *tokens])

    changes: list[tuple] = [                           # a limit's number bare, the engine's reader types it; a
        #                                                share of the window `<n>%`, as `--context` says it
        (key, f"{window_share(str(value))}%" if key == "context"
         else str(value) if key in SEASON_LIMITS and re.fullmatch(r"[0-9]+(\.[0-9]+)?", str(value)) else season_said(value))
        for key, value in scalars.items()]
    if packages:
        changes.append(("packages", [(one.partition("=")[0], lambda old, new=one: new) for one in packages]))
    if profiles:
        changes.append(("profiles", [(member, lambda old, member=member, given=given: profile_line(old, member, given))
                                     for member, given in profiles.items()]))
    return changes


def kept_at_start(started: dict, key: str):
    """-> what `team-started` kept of one key of the front matter, in the journal's form -- a ceremony by
    its declaration line, the preset by its name (None without one), the team's values as applied (`{name:
    value}`)."""
    if key == "ceremonies":
        return [one.get("text") for one in started.body.ceremonies or []]
    if key == "template":
        return (started.body.template or {}).get("template")
    if key == "schedule":
        return schedule_seconds(started)
    empty = {"agents": {}, "reports": [], "principals": [], "entries": {}, "limits": {}, "roles": {}, "values": {}}
    return started.line.get(key, empty.get(key))            # the line as the start wrote it: `limits` untranslated


def gap(started: dict, team: dict) -> list[dict]:
    """-> what a new `start` would change: `{key, started, declared}` per key `team-started` kept that the team as
    it would play (`team_played`) now says otherwise, in `PENDING`'s order -- the edges, the root and the daily a form
    makes among them, the preset by its name, the team's values as applied. The body, the owner's word, is never
    pending: pp serves it to the team's runs as soon as it changes."""
    found = []
    for key in PENDING:
        now_said = ([one.text for one in team.ceremonies] if key == "ceremonies" else
                    (team.template or {}).get("template") if key == "template" else
                    values_kept(team) if key == "values" else getattr(team, key))
        then = kept_at_start(started, key)
        if then != now_said:
            found.append({"key": key, "started": then, "declared": now_said})
    return found


def template_kept(team: dict) -> dict | None:
    """-> what `team-started.template` keeps of the preset a team names: `{template, origin}` -- None without one:
    the key is not written."""
    named = team.template
    return None if named is None else {"template": named["template"], "origin": named["origin"]}


def values_kept(team: dict) -> dict[str, str]:
    """-> what `team-started.values` keeps of the values `TEAM.md` applies to its preset and its documents:
    `{name: value}`."""
    return {one["name"]: one["value"] for one in team.applied}


def is_member(state: dict, name) -> bool:
    started = state.season.started
    return name in ((started.body.agents if started is not None else None) or {})


def is_principal(state: dict, name) -> bool:
    """-> whether `name` is one a team answers to: its owner, a mandator of `principals:`, or the
    team itself (the author of a ceremony task)."""
    started = state.season.started
    if started is None:
        return False
    return name is not None and (name == started.body.owner or name == started.team
                                 or name in (started.body.principals or []))


def launch_kept(started: dict, member: str) -> dict:
    """-> `{model, provider}` a member's launch takes from the season: its profile's, else the team's launch -- `null`
    when neither names one."""
    kept, profile = started.body.launch or {}, profile_of(started, member)
    return {key: profile.get(key) if profile.get(key) is not None else kept.get(key) for key in ("model", "provider")}


def season_of(asked: dict) -> dict:
    """-> the season's own limits, `{budget, budget-launches, silence, context}` -- the ones given, each judged: a number
    of dollars above 0, whole numbers of 1 or more, a share of the window (`window_share`); DECLINES `budget-invalid`,
    `team-invalid` for `--silence`, `context-invalid` for `--context`."""
    found: dict = {}
    if asked.get("context") is not None:
        found["context"] = window_share(str(asked["context"]))
        if found["context"] is None:
            decline(context_invalid(str(asked["context"])))
    if asked["budget"] is not None:
        try:
            found["budget"] = float(asked["budget"])
        except ValueError:
            found["budget"] = 0.0
        if not found["budget"] > 0:
            decline(f"budget-invalid -- `--budget {asked['budget']}`: a number of dollars above 0.")
    if asked["budget-launches"] is not None:
        if not str(asked["budget-launches"]).isdigit() or int(asked["budget-launches"]) < 1:
            decline(f"budget-invalid -- `--budget-launches {asked['budget-launches']}`: a whole number of 1 or more.")
        found["budget-launches"] = int(asked["budget-launches"])
    if asked.get("silence") is not None:
        if not str(asked["silence"]).isdigit() or int(asked["silence"]) < 1:
            decline(f"team-invalid -- `--silence {asked['silence']}`: a whole number of 1 or more.")
        found["silence"] = int(asked["silence"])
    return found


def switches_composed(*lists: list) -> dict[str, str]:
    """-> `{name: "on"|"off"}` from lists of `<name>=on|off`, each later list covering the earlier name by name, the
    last word on a name winning within a list; the order is the order the names first came."""
    found: dict[str, str] = {}
    for values in lists:
        for value in values or []:
            name, _, state = str(value).partition("=")
            found[name] = state
    return found


def season_switches(started: dict, member: str | None = None) -> dict[str, str]:
    """-> the switches the season gives a member's wake-up, `{name: "on"|"off"}`: the team's packages
    (`team-started.packages`), covered name by name by the member's profile; the team's alone without a member."""
    return switches_composed(started.body.packages or [], profile_of(started, member).get("packages") or [])


def set_of(values: list) -> dict[str, str]:
    """-> `{name: on|off}` of a set (`season_set`), in its order."""
    return switches_composed(values)


def window_share(text: str) -> int | None:
    """-> the context limit a text says: a whole percentage of the window from 1 to 99, `70` worth `70%`; None for any
    other text."""
    said = text.strip()
    number = said[:-1] if said.endswith("%") else said
    return int(number) if number.isdigit() and 1 <= int(number) <= 99 else None


def limit_of(text: str, off: bool = False) -> int | None:
    """-> the context limit `--context` says (`window_share`) -- of a recurrence, of a task at its birth, of a season --;
    None for `off` where `off` is allowed (the limit taken away); `context-invalid` otherwise."""
    if off and text.strip() == "off":
        return None
    limit = window_share(text)
    if limit is None:
        decline(context_invalid(text, off))
    return limit


def season_now(state: dict) -> dict:
    """-> the season of a started team: its number `n` -- the starts the journal holds -- and its `state`, `running`,
    or `stopped` once a stop ended it."""
    return {"n": int(state.season.seasons or 1), "state": "stopped" if state.season.stopped else "running"}


def profile_of(started: dict, member: str | None) -> dict:
    """-> the member's profile of the season (`team-started.profiles`), {} for none."""
    return dict(((started.body.profiles or {}).get(member) or {})) if member else {}



def start_asked(state: dict) -> bool:
    """-> whether the season `team start` opens follows a stop -- `since`, the hour of the start, is then due --,
    judged under the journal's lock before the hour is read; refused by its code `team-deleting`, `season-running`
    (a season under way: started, not stopped)."""
    if state.season.deleting:
        raise Declined("team-deleting")
    if state.season.started is not None and not state.season.stopped:
        raise Declined("season-running")
    return bool(state.season.stopped)


def team_started(team, owner: str, opened: dict, documents: list, rendered: dict, digest: str | None,
                 since: str | None) -> list:
    """-> `team-started`: the season `team start` opens, in the keys and the order it writes them -- the team judged,
    the owner, the season SEASON.md and the flags give (`opened`), the documents kept and `rendered` as the start wrote
    them; `season`, `profiles`, `template`, `values`, `season-digest` (`digest`, SEASON.md's) and `since` (the hour of a
    start after a stop) only when they hold something."""
    return [TeamStarted.made(agents=team.agents, reports=team.reports, root=team.root,
                             principals=team.principals, owner=owner,
                             ceremonies=[one.json() for one in team.ceremonies],   # each as it is written
                             entries=team.entries, roles=team.roles, work=opened["work"],
                             launch=opened["launch"], limits=team.limits,
                             **({"season": opened["season"]} if opened["season"] else {}),
                             packages=opened["packages"],
                             **({"profiles": opened["profiles"]} if opened["profiles"] else {}),
                             schedule=team.schedule, unit="s", digest=team.digest,
                             **({"template": template_kept(team)} if team.template else {}),
                             **({"values": values_kept(team)} if team.applied else {}),
                             documents=documents, rendered=rendered,
                             **({"season_digest": digest} if digest else {}),
                             **({"since": since} if since is not None else {}))]


def season_asked(state: dict) -> None:
    """`team stop` and `team pause` judged under the journal's lock, before what they stop is chosen or who pauses is
    read: refused by its code `team-not-started`, `season-stopped` (off season already)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if state.season.stopped:
        raise Declined("season-stopped")


def season_stopped(owner: str, tasks: list, recurrences: list) -> list:
    """-> `season-stopped {by, tasks, recurrences}`: the season the owner ends, with the ids of the tasks it stopped
    and of the recurrences it silences."""
    return [SeasonStopped.made(by=owner, tasks=tasks, recurrences=recurrences)]


def paused_decided(state: dict, sender: str) -> list:
    """-> `paused {by}`: the team paused by `sender` -- the owner or the principal `--as` names; refused by its code
    `team-paused` (paused already)."""
    if state.season.paused:
        raise Declined("team-paused")
    return [Paused.made(by=sender)]


def unpause_asked(state: dict) -> None:
    """`team resume` without a task, judged before who resumes is read: refused by its code `team-not-started`,
    `team-deleting`."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if state.season.deleting:
        raise Declined("team-deleting")


def unpaused_decided(state: dict, sender: str) -> list:
    """-> `unpaused {by}`: the paused team taken back by `sender`; refused by its code `team-not-paused`."""
    if not state.season.paused:
        raise Declined("team-not-paused")
    return [Unpaused.made(by=sender)]


def context_invalid(text: str, off: bool = False) -> str:
    """-> the refusal of a context limit `window_share` does not read."""
    return (f"context-invalid -- `--context {text.strip()[:20]}`: a context limit is a share of the window, "
            "1% to 99%" + (", or off" if off else "") + ".")
