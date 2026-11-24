"""gestures -- the commands the post plays as gestures -- those of the Teams and Tasks tabs, and the purge of the Agents tab: ONE argv per gesture, made from what is chosen (the team,
the task under the Tasks cursor, the member under the Members cursor, the fields of a gesture's overlay -- `to`,
`as`, `reply`, a name, a message, a budget --, the flags of a launch), played as it is and never shown -- a verb that
ticks without its tick (`untied`), the post ticking apart --; and its SUMMARY,
what the gesture did in words, for the status line (`summary`). A choice that
is missing -- no task, no member, no message where one is needed -- makes no argv: nothing plays. Pure: no
I/O, no Textual, and no state of a team judged -- `team` refuses what it refuses."""
from __future__ import annotations

import re
from typing import Sequence

from model import files
from model.teams import PROFILE_KEYS, SeasonLine

TICKING = frozenset({"start", "post", "stop", "resume", "budget", "ring", "recurrence"})   # the verbs of team that tick
DONE = {"pause": "paused", "tick": "ticked", "start": "started", "declare": "wrote the values of", "delete": "deleted",
        "budget": "set the budget of", "inbox": "marked seen the inbox of"}   # a verb of team, said once played


CODE = re.compile(r"[a-z][a-z0-9-]*")       # the code a verb opens its refusal on: `season-stopped`


def refusal(said: str) -> tuple[str, str]:
    """-> the code and the phrase of what a verb said refusing -- `pp-team: season-stopped -- core-review is off
    season` gives `season-stopped` and `core-review is off season`; a line without a code gives `""` and the line."""
    line = said.strip()
    head, colon, rest = line.partition(": ")
    if colon and " " not in head:
        line = rest
    code, dashes, phrase = line.partition(" -- ")
    return (code, phrase.strip()) if dashes and CODE.fullmatch(code) else ("", line)


def summary(argv: Sequence[str]) -> str:
    """-> what a gesture did, in words, for the status line -- `stopped T3 of core-review`, `posted a new task to ops`
    --, never its command."""
    words = list(argv)
    tool, verb, target = (words + ["", "", ""])[:3]
    task, recurrence = _value(words, "--task"), _value(words, "--recurrence")
    if tool == "agent":
        return f"purged runs of {target}" if verb == "purge" else f"{verb} {target}".strip()
    if verb == "post":
        if "--reply" in words:
            return f"replied on {task} of {target}"
        if task:
            return f"wrote on {task} of {target}"
        return f"laid a recurrence on {target}" if "--every" in words else f"posted a new task to {target}"
    if verb == "stop":
        if recurrence:
            return f"stopped the recurrence {recurrence} of {target}"
        if task:
            return f"{'ended the wake-ups of' if '--kill' in words else 'stopped'} {task} of {target}"
        return f"stopped every open task of {target}"
    if verb in ("pause", "resume") and recurrence:
        return f"{'paused' if verb == 'pause' else 'resumed'} the recurrence {recurrence} of {target}"
    if verb == "resume":
        return f"took back {task} of {target}" if task else f"resumed {target}"
    if verb == "recurrence":
        if "--now" in words:
            return f"launched the recurrence {words[3]} of {target} now"
        return f"made {task} of {target} come back" if task else f"changed the recurrence {words[3]} of {target}"
    if verb == "rename":
        return f"renamed {target} to {words[3]}"
    if verb == "ring":
        return f"rang {words[3]} of {target}"
    if verb == "reset":
        return f"forgot the run of {_value(words, '--member')} in {target}"
    if verb == "inbox" and "--id" in words:
        return f"marked #{_value(words, '--id')} read in the inbox of {target}"
    return f"{DONE.get(verb, verb)} {target}".strip()


def untied(argv: list[str] | None) -> list[str] | None:
    """-> a gesture of `team` whose verb TICKS at its end (`TICKING`) played WITHOUT its tick: `--no-tick` after the
    team's own flags -- before a season's first `--member`, whose flags are that member's. The post plays the tick
    apart once the verb has answered (`faces.play_gesture`), never under the bound of a verb: a tick launches the
    members due, one after the other. None, and any other verb, as they are."""
    if not argv or argv[0] != "team" or len(argv) < 3 or argv[1] not in TICKING or "--no-tick" in argv:
        return argv
    at = next((n for n in range(3, len(argv)) if argv[n] == "--member" and argv[n - 1] not in ("--message", "--name")),
              len(argv))
    return argv[:at] + ["--no-tick"] + argv[at:]


def _as(sender: str | None, owner: str | None) -> list[str]:
    """`--as` for a principal; the owner writes none -- `team` admits them by default."""
    return ["--as", sender] if sender and sender != owner else []


def post(team: str | None, message: str, task: str | None = None, to: str | None = None,
         reply: object = None, sender: str | None = None, owner: str | None = None,
         name: str | None = None, every: str | None = None, context: str | None = None,
         ask: bool = False) -> list[str] | None:
    """`team post`: a note -- a question under `ask`, or a reply under `reply` -- on `task`; a NEW task without one, named under `name`, and
    coming back at each period of `every` under the context limit `context` -- passed as typed: `team` judges them; a
    limit without a period is not passed."""
    if not team or not message:
        return None
    return untied(["team", "post", team] + (["--task", task] if task else [])
                  + (["--name", name] if name and not task else [])
                  + (["--to", to] if to else []) + (["--reply", str(reply)] if reply is not None else [])
                  + (["--ask"] if ask and task and reply is None else [])
                  + (["--every", every] if every and not task else [])
                  + (["--context", context] if context and every and not task else []) + _as(sender, owner)
                  + ["--message", message])


def stop(team: str | None, task: str | None = None, kill: bool = False, whole: bool = False,
         recurrence: str | None = None) -> list[str] | None:
    """`team stop`: the task named -- its wake-ups ended under `kill` --, every open task under `whole`, or the
    recurrence named, its open occurrence left alone."""
    if not team or (task is None and not whole and not recurrence):
        return None
    if recurrence:
        return untied(["team", "stop", team, "--recurrence", recurrence])
    return untied(["team", "stop", team] + (["--task", task] if task else []) + (["--kill"] if kill else []))


def recur(team: str | None, recurrence: str | None, every: str | None = None, message: str | None = None,
          context: str | None = None) -> list[str] | None:
    """`team recurrence`: the recurrence named changed -- its period `every`, its text `message`, its context limit
    `context` (`off` takes it away) --, each passed as typed and only when given; nothing without one."""
    flags = ((["--every", every] if every else []) + (["--context", context] if context else [])
             + (["--message", message] if message else []))
    if not team or not recurrence or not flags:
        return None
    return untied(["team", "recurrence", team, recurrence] + flags)


def launch(team: str | None, recurrence: str | None) -> list[str] | None:
    """`team recurrence --now`: one occurrence more of the recurrence named, opened now, its planning untouched."""
    if not team or not recurrence:
        return None
    return untied(["team", "recurrence", team, recurrence, "--now"])


def plan(team: str | None, task: str | None, every: str, context: str = "") -> list[str] | None:
    """`team recurrence --task`: the task named, given once, made to come back at each period of `every` under the
    context limit `context` -- passed as typed; nothing without a task and a period."""
    if not team or not task or not every:
        return None
    return untied(["team", "recurrence", team, "--task", task, "--every", every] + (["--context", context] if context else []))


def resume(team: str | None, task: str | None, message: str = "", sender: str | None = None,
           owner: str | None = None, to: str | None = None) -> list[str] | None:
    """`team resume`: the task named taken back, with a message or without -- to the member `to` names, or `all`, else
    to the members it revives."""
    if not team or not task:
        return None
    return untied(["team", "resume", team, "--task", task] + (["--to", to] if to else [])
                  + (["--message", message] if message else []) + _as(sender, owner))


def pause(team: str | None, paused: bool, sender: str | None = None, owner: str | None = None) -> list[str] | None:
    """`team pause` -- or `team resume` the team, never a task, when it is paused."""
    if not team:
        return None
    return untied(["team", "resume" if paused else "pause", team] + _as(sender, owner))


def pause_recurrence(team: str | None, recurrence: str | None, paused: bool, sender: str | None = None,
                     owner: str | None = None) -> list[str] | None:
    """`team pause --recurrence`: the recurrence named paused, its periods skipped -- or `team resume --recurrence`, which
    ticks, when it is paused."""
    if not team or not recurrence:
        return None
    return untied(["team", "resume" if paused else "pause", team, "--recurrence", recurrence] + _as(sender, owner))


def tick(team: str | None) -> list[str] | None:
    """`team tick`: one advance of the team, now."""
    return ["team", "tick", team] if team else None


def seen(team: str | None) -> list[str] | None:
    """`team inbox --seen`: the owner has read all that waited for them."""
    return ["team", "inbox", team, "--seen"] if team else None


def read(team: str | None, message: object) -> list[str] | None:
    """`team inbox --seen --id`: the owner has read the ONE message `message` of their inbox."""
    return ["team", "inbox", team, "--seen", "--id", str(message)] if team and message is not None else None


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
    return untied(["team", "start", team, "--message", message] + (["--name", name] if name else [])
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


def switched(now: dict[str, bool], then: dict[str, bool], required: frozenset[str] = frozenset()) -> list[str]:
    """-> the `--package <name>=on|off` of each package whose state `now` differs from `then`, never a package
    `required` switched off."""
    flags: list[str] = []
    for name in dict.fromkeys([*now, *then]):
        if name in now and now[name] != then.get(name) and not (name in required and not now[name]):
            flags += ["--package", f"{name}={'on' if now[name] else 'off'}"]
    return flags


def _differs(typed: str, declared: object, kind) -> bool:
    """-> whether a field of the season differs from what it opened on: typed, and another number."""
    if not typed:
        return False
    try:
        return declared is None or kind(typed) != kind(declared)
    except (TypeError, ValueError):
        return True


def percent(said: object) -> float:
    """-> a share of the context window as a number: `90`, `90%` and `90.0` alike -- `team start` writes `90%`."""
    return float(str(said).strip().removesuffix("%").strip())


def season(lines: Sequence[SeasonLine], opened: Sequence[SeasonLine], usd: str = "", launches: str = "",
           limits: dict | None = None, required: frozenset[str] = frozenset(), flags: Sequence[str] = (),
           silence: str = "", context: str = "") -> list[str]:
    """The flags of the season `team declare --season` writes into SEASON.md, what the form changed of the season it
    opened on: `--budget` and `--budget-launches` typed otherwise than the season's `limits`, `--silence` and
    `--context` typed otherwise than theirs; what `all` changes of its profile (`opened[0]`), then the harness of the
    post (`launch_of`), then the packages whose state `all` changed (`switched`), before any `--member` -- what follows
    one is that member's --; then each member whose line changed: its profile's keys, and the packages its own
    switches changed. [] without a line."""
    if not lines:
        return []
    whole, before = lines[0], (list(opened) or [SeasonLine(None)])[0]
    limits = limits or {}
    argv: list[str] = []
    argv += ["--budget", usd] if _differs(usd, limits.get("budget"), float) else []
    argv += ["--budget-launches", launches] if _differs(launches, limits.get("budget-launches"), int) else []
    argv += ["--silence", silence] if silence and silence != str(limits.get("silence") or "") else []
    argv += ["--context", context] if _differs(context, limits.get("context"), percent) else []
    changed = {key: value for key, value in whole.profile.items() if before.profile.get(key) != value}
    argv += launch_of(profile_flags(changed), flags) + switched(whole.played(), before.played(), required)
    then = {line.member: line for line in list(opened)[1:]}
    for line in lines[1:]:
        was = then.get(line.member) or SeasonLine(line.member, line.path)
        own = profile_flags({key: value for key, value in line.profile.items() if was.profile.get(key) != value})
        played = line.played(whole)
        own += switched({name: played.get(name, on) for name, on in line.switches.items()}
                        | {name: played[name] for name in was.switches if name not in line.switches and name in played},
                        was.switches, required)
        argv += ["--member", str(line.member)] + own if own else []
    return argv


def season_declared(team: str | None, declared: list[str] | None, launched: Sequence[str]) -> list[str] | None:
    """`team declare <team> --season`: the keys `declared_values` gives (`declared`, its argv), then the season's
    flags (`launched`, `season`'s) -- a member's profile last, `--json` at the end; None when neither changes."""
    if not team or (not declared and not launched):
        return None
    head = [one for one in declared if one != "--json"] if declared else ["team", "declare", team, "--season"]
    return head + list(launched) + ["--json"]


def season_started(team: str | None) -> list[str] | None:
    """`team start <team>`: the next SEASON of the team, the one SEASON.md writes -- no flag of the season, no task."""
    return untied(["team", "start", team]) if team else None


def budget(team: str | None, usd: str | None = None, launches: str | None = None, sender: str | None = None,
           owner: str | None = None) -> list[str] | None:
    """`team budget`: the team's budget raised to `usd` dollars, its `budget-launches` to `launches` -- the one given, or
    both; neither, nothing to play."""
    if not team or (not usd and not launches):
        return None
    return untied(["team", "budget", team] + ([usd] if usd else []) + (["--launches", launches] if launches else [])
                  + _as(sender, owner))


def _number(value: object) -> str:
    """-> a number typed or said, written the one way (`2`, `2.5`); a text that reads as none, as it is."""
    try:
        return f"{float(str(value)):g}"
    except (TypeError, ValueError):
        return str(value or "").strip()


def _lines(opened: dict, key: str) -> list[str]:
    said = opened.get(key)
    return list(said) if isinstance(said, list) else []


def declared_values(team: str | None, opened: dict, typed: dict, season: bool = False,
                    default_members: Sequence[str] = (), body: str | None = None) -> list[str] | str | None:
    """`team declare <team> [--season]`: the keys of a values file -- TEAM.md, SEASON.md under `season` -- written from
    the fields of its form, each flag the change of ONE key or ONE line between what the file says (`opened`,
    `files.read` of the face's text) and what is `typed`: `description` and `template`; `values` (`<name> = <value>`
    per line, `--value`, `--no-value`) and `documents` (`<key>|all <document> ...` per line, `--document`,
    `--no-document`), a line named by its first word; for TEAM.md, `agents` (`<name> <path>` per line, `--member`,
    `--no-member` -- a team to be born whose lines are its preset's names alone, `default_members`, names none),
    `roles` (`<key> <member> ...`, `--role`, `--no-role`), `reports` (`<member>... -> <member>` per line, `--report`,
    `--no-report` the member reported to), `root`, `principals` (one name per word), the limits `budget`, `launches`,
    `parallel`, `timeout` and `schedule`; for both, the BODY typed (`body` in `typed`) against the one the file holds (`body`, None
    when not compared): `--body-file -`, the body then given on the verb's input (`body_input`). -> the argv, `--json`
    last; None when nothing changed; a reason
    when the typed values make none: no name, a line of the members short of its path, or what `team declare` cannot
    take out -- the template, a principal, the root, a limit, the schedule or the description emptied."""
    name = str(team or "").strip()
    if not name:
        return "a name for the team"
    flags: list[str] = []
    said = lambda key: str(typed.get(key) or "").strip()
    was = lambda key: str(opened.get(key) or "").strip() if not isinstance(opened.get(key), list) else ""
    if not season and said("description") != was("description"):
        if not said("description"):
            return "the description cannot be emptied here: type one"
        flags += ["--description", said("description")]
    if said("template") != was("template"):
        if not said("template"):
            return "the template cannot be taken out here: choose one"
        flags += ["--template", said("template")]
    for key, flag, contrary in (("values", "--value", "--no-value"), ("documents", "--document", "--no-document")):
        new, gone = files.line_changes(key, _lines(opened, key), files.lines_of(typed.get(key)))
        for line in new:
            flags += [flag, (f"{line.partition('=')[0].strip()}={line.partition('=')[2].strip()}"
                             if key == "values" else line)]
        for one in gone:
            flags += [contrary, one]
    if body is not None and said("body") != body.strip():
        flags += ["--body-file", "-"]
    if season:
        return ["team", "declare", name, "--season"] + flags + ["--json"] if flags else None
    typed_members = files.lines_of(typed.get("agents"))
    if not (not _lines(opened, "agents") and [line.split() for line in typed_members] == [[one] for one in default_members]):
        if any(len(line.split()) != 2 for line in typed_members):
            return "every line of the members names a member and its path: `lead agents/lead`"
        new, gone = files.line_changes("agents", _lines(opened, "agents"), typed_members)
        for line in new:
            flags += ["--member", *line.split()]
        for one in gone:
            flags += ["--no-member", one]
    new, gone = files.line_changes("roles", _lines(opened, "roles"), files.lines_of(typed.get("roles")))
    for line in new:
        flags += ["--role", *line.split()]
    for one in gone:
        flags += ["--no-role", one]
    new, gone = files.line_changes("reports", _lines(opened, "reports"), files.lines_of(typed.get("reports")))
    for line in new:
        flags += ["--report", line]
    for one in gone:
        flags += ["--no-report", one]
    if said("root") != was("root"):
        if not said("root"):
            return "the root cannot be emptied here: name a member"
        flags += ["--root", said("root")]
    before, now = _lines(opened, "principals"), said("principals").split()
    gone = [one for one in before if one not in now]
    if gone:
        return f"{' '.join(gone)} cannot be taken out here"
    for one in now:
        flags += ["--principal", one] if one not in before else []
    for key in ("budget", "launches", "parallel", "timeout", "schedule"):
        typed_one = _number(said(key)) if key != "schedule" else said(key)
        opened_one = _number(was(key)) if key != "schedule" else was(key)
        if typed_one != opened_one:
            if not typed_one:
                return f"the {key} cannot be emptied here: type a value"
            flags += [f"--{key}", typed_one]
    return ["team", "declare", name] + flags + ["--json"] if flags else None



def body_input(argv: list[str] | None, typed: dict) -> tuple[list[str], str] | list[str] | None:
    """-> a `team declare` that reads its body on its input (`--body-file -`) with that input: `(argv, the body typed,
    one line break last)`; any other argv as it is."""
    if not argv or "--body-file" not in argv:
        return argv
    text = str(typed.get("body") or "").strip()
    return argv, (text + "\n" if text else "")


def delete(team: str | None, agents: Sequence[str] = ()) -> list[str] | None:
    """`team delete --yes`: the team removed with what it made -- its journal, its timer, its calendar line, its runs --
    and, one `--agent` each, the agents checked in the overlay; the others stay."""
    if not team:
        return None
    argv = ["team", "delete", team]
    for one in agents:
        argv += ["--agent", one]
    return argv + ["--yes"]


def rename(team: str | None, new: str) -> list[str] | None:
    """`team rename`: the team's directory and journal moved to the new name typed; nothing without one."""
    if not team or not new.strip():
        return None
    return ["team", "rename", team, new.strip()]


def ring(team: str | None, ceremony: str | None, sender: str | None = None, owner: str | None = None) -> list[str] | None:
    """`team ring`: the ceremony named rung at hand, now -- as a principal of the team under `sender`."""
    if not team or not ceremony:
        return None
    return untied(["team", "ring", team, ceremony] + _as(sender, owner))


def purge(agent: str | None, key: str | None = None, before: str | None = None, yes: bool = False,
          force: bool = False) -> list[str] | None:
    """`agent purge`: the run `key` of `agent`, or its runs before the date `before` -- without `--yes` the verb
    says what it would remove and writes nothing; `--force` over a clone with unsent commits."""
    if not agent or bool(key) == bool(before):
        return None
    return (["agent", "purge", agent] + ([key] if key else ["--before", str(before)]) + (["--yes"] if yes else [])
            + (["--force"] if force else []) + ["--json"])
