"""gestures -- the commands the post plays as gestures -- those of the Teams and Tasks tabs, and the purge of the Agents tab: ONE argv per gesture, made from what is chosen (the team,
the task under the Tasks cursor, the member under the Members cursor, the fields of a gesture's overlay -- `to`,
`as`, `reply`, a name, a message, a budget --, the flags of a launch), and its PREVIEW -- the same list, as the operator would
type it. The tab shows `preview(argv)`, then plays `argv` itself: what is shown is what plays. A choice that
is missing -- no task, no member, no message where one is needed -- makes no argv: nothing plays. Pure: no
I/O, no Textual, and no state of a team judged -- `team` refuses what it refuses."""
from __future__ import annotations

import shlex
from typing import Sequence

from model.teams import PROFILE_KEYS, SeasonLine

CONSOLE = "./pp"


def preview(argv: Sequence[str]) -> str:
    """-> the command an argv plays, quoted as a shell would read it: `./pp team stop core-review --task T3`."""
    return f"{CONSOLE} {shlex.join(argv)}"


def _as(sender: str | None, owner: str | None) -> list[str]:
    """`--as` for a principal; the owner writes none -- `team` admits them by default."""
    return ["--as", sender] if sender and sender != owner else []


def post(team: str | None, message: str, task: str | None = None, to: str | None = None,
         reply: object = None, sender: str | None = None, owner: str | None = None,
         name: str | None = None) -> list[str] | None:
    """`team post`: a note -- or a reply under `reply` -- on `task`; a NEW task without one, named under `name`."""
    if not team or not message:
        return None
    return (["team", "post", team] + (["--task", task] if task else []) + (["--name", name] if name and not task else [])
            + (["--to", to] if to else []) + (["--reply", str(reply)] if reply is not None else []) + _as(sender, owner)
            + ["--message", message])


def stop(team: str | None, task: str | None = None, kill: bool = False, whole: bool = False) -> list[str] | None:
    """`team stop`: the task named -- its wake-ups ended under `kill` --, or every open task under `whole`."""
    if not team or (task is None and not whole):
        return None
    return ["team", "stop", team] + (["--task", task] if task else []) + (["--kill"] if kill else [])


def resume(team: str | None, task: str | None, message: str = "", sender: str | None = None,
           owner: str | None = None) -> list[str] | None:
    """`team resume`: the task named taken back, with a message to the members it revives or without."""
    if not team or not task:
        return None
    return ["team", "resume", team, "--task", task] + (["--message", message] if message else []) + _as(sender, owner)


def pause(team: str | None, paused: bool, sender: str | None = None, owner: str | None = None) -> list[str] | None:
    """`team pause` -- or `team resume` the team, never a task, when it is paused."""
    if not team:
        return None
    return ["team", "resume" if paused else "pause", team] + _as(sender, owner)


def tick(team: str | None) -> list[str] | None:
    """`team tick`: one advance of the team, now."""
    return ["team", "tick", team] if team else None


def seen(team: str | None) -> list[str] | None:
    """`team inbox --seen`: the owner has read what waited for them."""
    return ["team", "inbox", team, "--seen"] if team else None


def reset(team: str | None, member: str | None) -> list[str] | None:
    """`team reset --member`: the run of ONE member forgotten."""
    if not team or not member:
        return None
    return ["team", "reset", team, "--member", member]


def _value(flags: Sequence[str], name: str) -> str | None:
    """-> the value of `name` (`--harness`, `--provider`) among `flags`, as `--name value` or `--name=value`."""
    for at, one in enumerate(flags):
        if one == name and at + 1 < len(flags):
            return flags[at + 1]
        if one.startswith(name + "="):
            return one.split("=", 1)[1]
    return None


def harness_of(flags: Sequence[str]) -> list[str]:
    """-> `--harness <command>` and the `--provider <name>` beside it -- the grammar its output is read in -- as
    the flags after `--` of `./pp ui` give them, the launch flags the overlay of the parameters does not ask; []
    without a `--harness`; the other flags stay `agent chat`'s."""
    harness = _value(flags, "--harness")
    if harness is None:
        return []
    grammar = _value(flags, "--provider")
    return ["--harness", harness] + (["--provider", grammar] if grammar is not None else [])


def launch_of(chosen: Sequence[str], flags: Sequence[str]) -> list[str]:
    """-> the flags of a team's wake-ups: the parameters `chosen` in the overlay, then the harness of the post
    (`harness_of`) -- its grammar in place of the provider chosen, a caller's command being no provider launched."""
    harness = harness_of(flags)
    kept = list(chosen)
    if "--provider" in harness and "--provider" in kept:
        at = kept.index("--provider")
        del kept[at:at + 2]
    return kept + harness


def start(team: str | None, message: str, to: str | None = None, flags: Sequence[str] = (),
          name: str | None = None) -> list[str] | None:
    """`team start`: the team declared started on its first message -- its task named under `name` --, the flags
    of a launch after it."""
    if not team or not message:
        return None
    return (["team", "start", team, "--message", message] + (["--name", name] if name else [])
            + (["--to", to] if to else []) + list(flags))


def profile_flags(profile: dict) -> list[str]:
    """-> the flags a line of a season carries, in `team start`'s order: `--provider`, `--model`, `--effort`,
    `--permissions` -- a caller's command (`harness`) is no provider."""
    flags: list[str] = []
    for key in PROFILE_KEYS:
        value = profile.get(key)
        if value and not (key == "provider" and value == "harness"):
            flags += [f"--{key}", str(value)]
    return flags


def switched(line: SeasonLine, whole: SeasonLine, required: frozenset[str] = frozenset()) -> dict[str, bool]:
    """-> the switches a member's line composes: its own first, then those of `all` its agent says in the other
    state -- each only where it changes what the agent says (an agent that says nothing: its own alone, as given);
    never a package `required` switched off."""
    base = line.packages
    found: dict[str, bool] = {}
    for name, on in line.switches.items():
        if (name in required and not on) or (base is not None and base.get(name) == on):
            continue
        found[name] = on
    for name, on in whole.switches.items():
        if name in line.switches or (name in required and not on) or base is None or name not in base:
            continue
        if base[name] != on:
            found[name] = on
    return found


def _differs(typed: str, declared: object, kind) -> bool:
    """-> whether a field of the season differs from what `TEAM.md` declares: typed, and another number."""
    if not typed:
        return False
    try:
        return declared is None or kind(typed) != kind(declared)
    except (TypeError, ValueError):
        return True


def season(team: str | None, lines: Sequence[SeasonLine], message: str = "", name: str = "", usd: str = "",
           launches: str = "", declared: dict | None = None, required: frozenset[str] = frozenset(),
           flags: Sequence[str] = ()) -> list[str] | None:
    """`team start`: a SEASON of the team -- a first task under `message`, if any (without it the season stands on its
    ceremonies and the posts to come, team 0.38.0), named under `name` with it; `--budget` and `--budget-launches` where the season differs from what `TEAM.md` declares (`declared`,
    the limits of `declared`); what `all` carries (team keeps only what a start gives); the harness of the post
    (`launch_of`), before any `--member` -- what follows one is that member's --; then each member whose line
    differs from `all`: what it changes, and its switches (`switched`)."""
    if not team or not lines:
        return None
    whole, limits = lines[0], declared or {}
    argv = ["team", "start", team] + (["--message", message] if message else [])
    argv += ["--name", name] if message and name else []
    argv += ["--budget", usd] if _differs(usd, limits.get("budget"), float) else []
    argv += ["--budget-launches", launches] if _differs(launches, limits.get("budget-launches"), int) else []
    argv += launch_of(profile_flags(whole.profile), flags)
    for line in lines[1:]:
        own = profile_flags({key: value for key, value in line.profile.items() if whole.profile.get(key) != value})
        for package, on in switched(line, whole, required).items():
            own += ["--package", f"{package}={'on' if on else 'off'}"]
        argv += ["--member", str(line.member)] + own if own else []
    return argv


def budget(team: str | None, usd: str | None = None, launches: str | None = None, sender: str | None = None,
           owner: str | None = None) -> list[str] | None:
    """`team budget`: the team's budget raised to `usd` dollars, its `budget-launches` to `launches` -- the one given, or
    both; neither, nothing to play."""
    if not team or (not usd and not launches):
        return None
    return ["team", "budget", team] + ([usd] if usd else []) + (["--launches", launches] if launches else []) + _as(sender, owner)


def _members(text: str) -> list[list[str]]:
    """-> the lines of a members' field, each split on its blanks."""
    return [line.split() for line in text.splitlines() if line.strip()]


def new_gap(team: str, members: str, defaults: Sequence[str]) -> str:
    """-> why `new` makes no command yet -- no name, or members changed with a line short of its path; '' when it
    makes one."""
    if not team.strip():
        return "a name for the team"
    lines = _members(members)
    if lines != [[one] for one in defaults] and (not lines or any(len(line) != 2 for line in lines)):
        return "once the members change, every line names a member and its path, the template's lines too: `lead agents/lead`"
    return ""


def new(team: str, template: str | None, members: str, defaults: Sequence[str], root: str | None = None,
        principals: str = "", ceremony: bool = True, limits: dict | None = None, prefilled: dict | None = None,
        schedule: str = "") -> list[str] | None:
    """`team new`: a team written from `template` -- `--member <name> <path>` for each line of `members` once they
    differ from the template's `defaults` (left as they are, none: `team` writes its own paths), `--root`, a
    `--principal` per name, a limit typed otherwise than `prefilled`, `--schedule`, `--no-ceremony` when the
    template's ceremony is left out. No command without a name, nor with a changed member short of its path."""
    if not template or new_gap(team, members, defaults):
        return None
    argv = ["team", "new", team.strip(), "--template", template]
    lines = _members(members)
    if lines != [[one] for one in defaults]:
        for name, path in lines:
            argv += ["--member", name, path]
    argv += ["--root", root] if root else []
    for one in principals.split():
        argv += ["--principal", one]
    for key in ("budget", "launches", "timeout"):
        typed = str((limits or {}).get(key) or "").strip()
        if typed and typed != str((prefilled or {}).get(key, "")):
            argv += [f"--{key}", typed]
    argv += ["--schedule", schedule.strip()] if schedule.strip() else []
    return argv + ([] if ceremony else ["--no-ceremony"])


def ring(team: str | None, ceremony: str | None, sender: str | None = None, owner: str | None = None) -> list[str] | None:
    """`team ring`: the ceremony named rung at hand, now -- as a principal of the team under `sender`."""
    if not team or not ceremony:
        return None
    return ["team", "ring", team, ceremony] + _as(sender, owner)


def purge(agent: str | None, key: str | None = None, before: str | None = None, yes: bool = False,
          force: bool = False) -> list[str] | None:
    """`agent purge`: the run `key` of `agent`, or its runs before the date `before` -- without `--yes` the verb
    says what it would remove and writes nothing; `--force` over a clone with unsent commits."""
    if not agent or bool(key) == bool(before):
        return None
    return (["agent", "purge", agent] + ([key] if key else ["--before", str(before)]) + (["--yes"] if yes else [])
            + (["--force"] if force else []) + ["--json"])
