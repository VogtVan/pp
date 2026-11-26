"""The `declaration` domain, layer `rules`: what a declaration is worth, judged from the values it is given.

A definition belongs here when it judges or shapes a declaration from its arguments alone: a description checked, the
roles a template gives, the team a template shapes from its values, the step of the net read from the front matter, the
limits a front matter sets, a ceremony read from its line and checked, given as a `Ceremony`, the order of the
ceremonies; the name a team is shown by and its description, from its front matter; the team as it plays judged whole
from the front matter and the bytes it is given, given as a `Team`, with the intention rendered by the function the act
gives it; and the changes `declare`'s flags make to a values file, from the flags and the preset already read at a
birth. It reads no disk, no clock and no environment and prints nothing: a judgement that fails DECLINES (`Declined`),
and the act or the verb that called it refuses. One refusal still comes from below: a limit that is no number is
refused by `numbered` (`template/rules.py`) itself. It may call the engine it is given for reading a text alone -- a
name's form, a section, a front matter, a document made of a text -- and nothing else of it.

`roles: |` of `TEAM.md` declares ROLE KEYS, one `<key> [<member> ...]` per line: the key a slug said once, the
author's own word -- pp reserves none and deduces none from an edge, the root, a profile or a member's name --, its
members declared by `agents:`, each once on its line; a key without a member is reserved, and said. A key chooses
documents, never a right: a line of `documents:` names the key it reaches (`documents/acts.py`). A team preset's `roles:` names,
after each key, PLACES of the preset's form, written as holes: `{root}` the root, `{others}` every other member,
`{last}` the last member, and for `tree` alone `{squads}` the squad leads and `{workers}` the workers. `star`,
`chain` and a preset without `form:` have `{root}`, `{others}` and `{last}`; `one` has `{root}` and `{last}`; a
place the form does not have, or a member's name, refuses `template-invalid`. At the birth alone, each place is
filled with the members the form puts there for the team declared, and the lines are written into `TEAM.md`.
Kept by every season at `team-started.roles` (`{key: [members]}`),
followed by `declaration`, said by the members' sheet.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from house.model import HOUSE, decline
from house.rules import block, path_valid, seconds_of_duration
from template.model import SEASON_DOC
from declaration.model import (DEFAULT_SCHEDULE, DESCRIPTION_CHARS, DOWS, LIMITS, MODES, NAME_CHARS, RETIRED_LIMITS,
                               Ceremony, Team)
from template.rules import daily_of, documents_none, formed, numbered, season_said


def described_well(said) -> bool:
    """-> whether a description is one line of 1 to `DESCRIPTION_CHARS` printable characters, its edges stripped."""
    return bool(said) and len(said) <= DESCRIPTION_CHARS and said.isprintable()


def preset_roles(template: dict, team: dict) -> list[str]:
    """-> the lines of `roles:` a team preset gives a team at its birth: each of its keys with the members the form
    puts in the places its line names (`team`, `formed`'s, its `places`), each once, in the order the places say --
    a key whose places hold nobody stays, reserved."""
    lines = []
    for line in template.roles:
        key, *places = line.split()
        held = [one for place in places for one in team.places[place.strip("{}")]]
        lines.append(" ".join([key, *dict.fromkeys(held)]))
    return lines


def shaped(front: dict, template: dict, values: dict[str, str], members: list[str]) -> tuple[dict, dict]:
    """-> (the front matter of a `TEAM.md` as it plays under its template, the team its form makes of the members
    -- `formed`): the template's limits and `schedule:` where
    `TEAM.md` writes none; under a `form:`, the edges the form makes of the members when `TEAM.md` writes no
    `reports:`, its root when `TEAM.md` writes no `root:` -- a root written is the form's head --, and the daily
    added to `TEAM.md`'s ceremonies unless one of them is named `daily`. The daily counts the members who report to
    the root in the edges as the team plays (`daily_of`): `TEAM.md`'s own when it writes `reports:`, the form's
    otherwise. A template without `form:` makes no edge and no root: `TEAM.md` writes its own."""
    made = {**template.limits, **({} if template.schedule is None else {"schedule": template.schedule}),
            **front}
    said = str(front.get("root") or "").strip() or None
    team = formed(template, members, said, values)
    if template.form is None:
        return made, team
    daily = team.ceremony
    if "reports" not in front:
        made["reports"] = "\n".join(team.reports)
    else:                                              # the edges TEAM.md writes: who reports to the root there
        edges = [line.split("->", 1) for line in block(front, "reports") if "->" in line]
        chiefs = [one for sources, target in edges if target.split() == [team.root] for one in sources.split()]
        daily = daily_of(template.form, values, list(dict.fromkeys(chiefs)), team.root)
    if said is None:
        made["root"] = team.root
    ceremonies = block(front, "ceremonies")
    if daily and not any(line.split()[0] == "daily" for line in ceremonies):
        made["ceremonies"] = "\n".join([*ceremonies, daily])
    return made, team


def schedule_of(front: dict, path: Path) -> int | None:
    """-> the net's step in SECONDS: `schedule:` of `TEAM.md` -- `off` (None: no net, ever), `<n>s`, `<n>m`, `<n>h`
    or a bare whole number of minutes, DEFAULT_SCHEDULE when the key is absent; any other value refuses
    `team-invalid` naming the four forms."""
    if "schedule" not in front:
        return DEFAULT_SCHEDULE
    value = front["schedule"]
    if value is False or (isinstance(value, str) and value.strip() == "off"):
        return None
    seconds = seconds_of_duration(value)
    if seconds is None:
        decline(f"team-invalid -- {path}: `schedule: {value}` -- `off`, or how long the team's timer sleeps at most, "
                "a second at least: `10s`, `2m`, `1h`, or a bare number of minutes (`5`).")
    return seconds


def when_of(words: list[str]) -> dict | None:
    """-> the period an `every` names, `{kind, at}` -- `day`, `weekday` or a day of the week, then the local hour
    `HH:MM` --, or None when the words say anything else: the ONE reader of a period, a ceremony's and a
    recurrence's."""
    at = words[1] if len(words) == 2 else ""
    timed = (len(at) == 5 and at[2] == ":" and at[:2].isdigit() and at[3:].isdigit()
             and int(at[:2]) < 24 and int(at[3:]) < 60)
    if len(words) != 2 or words[0] not in ("day", "weekday", *DOWS) or not timed:
        return None
    return {"kind": words[0], "at": at}


def ceremony_of(line: str, agents: dict, path: Path) -> Ceremony:
    """-> one ceremony as its line declares it: `<name> every … [with a b -> c [any <n>]]` or
    `<name> after <other> … [with a b -> c [any <n>]]` -- the name, the mode, what it follows, its
    participants, its facilitator and its quorum (n of the participants whose answers are enough for the
    facilitator to conclude, said in its consigne and holding nothing, `None` for all); the rest of the words kept as the text the rhythm will read."""
    words = line.split()
    if len(words) < 2 or words[1] not in MODES:
        decline(f"team-invalid -- {path}: ceremonies: `{line}` -- a line is `<name> every …` or `<name> after <other> …`.")
    name, mode = words[0], words[1]
    spec = words[2:words.index("with")] if "with" in words else words[2:]
    after, when = None, None
    if mode == "after":
        if len(spec) != 1 or spec[0] == "with":
            decline(f"team-invalid -- {path}: ceremonies: `{line}` -- `after` names the ceremony it follows, "
                   "and nothing else.")
        after = spec[0]
    else:
        when = when_of(spec)
        if when is None:
            decline(f"team-invalid -- {path}: ceremonies: `{line}` -- the when is "
                   "`every day|weekday|mon..sun HH:MM`.")
    participants: list[str] = []
    facilitator, quorum = None, None
    if "with" in words:
        tail = words[words.index("with") + 1:]
        if "->" in tail:
            at = tail.index("->")
            participants, targets = tail[:at], tail[at + 1:]
            if len(targets) == 3 and targets[1] == "any":       # the quorum: `-> c any <n>`
                n = targets[2]
                if not n.isdigit() or not 1 <= int(n) <= len(participants):
                    decline(f"team-invalid -- {path}: ceremonies: `{line}` -- the quorum is `any <n>`, n from 1 to "
                           f"the {len(participants)} participant(s).")
                quorum, targets = int(n), targets[:1]
            if len(targets) != 1:
                decline(f"team-invalid -- {path}: ceremonies: `{line}` -- one facilitator after `->`, "
                       "then `any <n>` at most.")
            facilitator = targets[0]
        else:
            participants = tail
        for one in participants + ([facilitator] if facilitator else []):
            if one not in agents:
                decline(f"participant-unknown -- {path}: ceremony `{name}` names `{one}`, a member nobody declared.")
    if facilitator is None or not participants:
        decline(f"team-invalid -- {path}: ceremonies: `{line}` -- a ceremony owes its participants and its "
               "facilitator: `with a b -> c`.")
    return Ceremony(name=name, mode=mode, after=after, when=when, participants=participants,
                    facilitator=facilitator, quorum=quorum, text=line)


def acyclic(ceremonies: list[dict], path: Path) -> None:
    """The `after` graph must be a DAG: a loop would ring for ever -- `ceremony-cycle`."""
    follows = {one.name: one.after for one in ceremonies}
    for start in follows:
        seen, step = [start], follows[start]
        while step is not None:
            if step in seen:
                decline(f"ceremony-cycle -- {path}: `{' -> '.join(seen + [step])}` -- `after` loops; the chain "
                       "of ceremonies must end.")
            seen.append(step)
            step = follows.get(step)


def limits_of(front: dict, path: Path) -> dict:
    """-> the bounds `TEAM.md` declares, each judged: `parallel` a whole number of 1 or more,
    `budget` a number above 0 (dollars), `retries` a whole number of 0 or more, `timeout` a
    number of seconds above 0, `launches` (the launches of one task) and `budget-launches` (the
    launches of the season) whole numbers of 1 or more, `suspect-max` a duration (`20s`, `2m`, bare minutes),
    kept in seconds, `silence` a whole number of 1 or more (the silent passages in a row that make a member
    suspected; DEFAULT_SILENCE without it); an absent key is no bound; any other value
    refuses `team-invalid` naming the key and the value; a key of before (`launches`, `budget-launches`: the
    bounds counted wake-ups) refuses `limit-retired` naming the key that took its place."""
    found: dict = {}
    for key, now in RETIRED_LIMITS.items():
        if key in front:
            decline(f"limit-retired -- {path}: `{key}:` is gone -- the bounds count launches: say `{now}:`.")
    for key in LIMITS:
        if key not in front:
            continue
        value = front[key]
        whole = isinstance(value, int) and not isinstance(value, bool)
        number = whole or (isinstance(value, float) and value == value)
        if key == "parallel" and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `parallel: {value}` -- a whole number of 1 or more.")
        if key == "budget" and (not number or value <= 0):
            decline(f"team-invalid -- {path}: `budget: {value}` -- a number of dollars above 0.")
        if key == "retries" and (not whole or value < 0):
            decline(f"team-invalid -- {path}: `retries: {value}` -- a whole number of 0 or more.")
        if key == "timeout" and (not number or value <= 0):
            decline(f"team-invalid -- {path}: `timeout: {value}` -- a number of seconds above 0.")
        if key in ("launches", "budget-launches") and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `{key}: {value}` -- a whole number of 1 or more.")
        if key == "silence" and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `silence: {value}` -- a whole number of 1 or more: the exchanges in a "
                    "row a member that owes an answer may end without a message to the team before it is suspected.")
        if key == "suspect-max":                           # kept in seconds: the longest interval of a suspicion
            value = seconds_of_duration(value)
            if value is None:
                decline(f"team-invalid -- {path}: `suspect-max: {front[key]}` -- a duration: seconds (`20s`), "
                        "minutes (`2m`, `10`).")
        found[key] = value
    return found


def judged(conductor, front: dict, data: bytes, path: Path, name: str, owner: str, made: dict | None,
           rendered) -> Team:
    """-> the team a declaration's text declares, judged whole -- the agents and their types, the
    edges, the root, the mandators, the ceremonies (their names, participants and `after`
    graph), `key-moved` for a `work:` (the season's, in SEASON.md),
    the members' names (`owner`'s refused: the owner signs its messages with it), the role keys (`roles:`,
    `<key> [<member> ...]` per line: the author's words, each a slug said once, its
    members declared, each once on its line, a key without a member reserved), the name shown -- `name:`, the
    directory's name without it --, the `description:` (None without
    it; never written to the journal) and the digest; each defect
    DECLINES by its name (`Declined`, its
    text the refusal `start` writes). Under what `TEAM.md` names (`made`: its `template` -- `template_of`'s, None
    without one --, the values `applied`, what `documents_of` `read`), the members once judged, the front matter is
    the one the preset shapes (`shaped`); `template` says the preset named and the values it declares, as applied --
    `{template, origin, values: [{name, value, from}]}`, None without a preset --, `applied` every value the team
    applies, `read` its documents' lines for the start to render (`documents_rendered`), `intention` the preset's
    intention rendered for the team by `rendered` -- the face `team_played` gives, `intention_rendered` --, "" without
    a preset. Called by `team_played` alone."""
    said = front.get("name")
    shown = name if said is None else str(said).strip()
    if not shown or len(shown) > NAME_CHARS or not shown.isprintable():
        decline(f"name-invalid -- {path}: `name: {' '.join(str(said).split())[:40]}` -- a team's name is one line of 1 "
                f"to {NAME_CHARS} printable characters.")
    told = front.get("description")
    description = None if told is None else str(told).strip()
    if description is not None and not described_well(description):
        decline(f"team-invalid -- {path}: `description: {' '.join(str(told).split())[:40]}` -- a team's description is "
                f"one line of 1 to {DESCRIPTION_CHARS} printable characters.")
    agents: dict[str, str] = {}
    for line in block(front, "agents"):
        words = line.split()
        if len(words) != 2:
            decline(f"team-invalid -- {path}: agents: `{line}` -- one line per member, `<name> <path>`.")
        member, at = words
        if not conductor.instance.valid_slug(member):
            decline(f"team-invalid -- {path}: agents: `{member}` -- a member's name is one slug (lowercase, "
                   "digits and single dashes), no `/`.")
        if member == owner:
            decline(f"team-invalid -- {path}: agents: `{member}` -- the name of the team's owner, who signs its "
                    "messages with it: give the member another name.")
        if not path_valid(conductor, at):
            decline(f"team-invalid -- {path}: agents: `{at}` -- an agent is its path under the house, slugs "
                   f"(lowercase, digits and single dashes) joined by `/`, or `{HOUSE}` for the house itself.")
        if member in agents:
            decline(f"team-invalid -- {path}: agents: `{member}` declared twice -- one name per member.")
        agents[member] = at
    if not agents:
        decline(f"team-invalid -- {path}: `agents:` declares nobody.")
    template = (made or {}).get("template")
    values = {one["name"]: one["value"] for one in (made or {}).get("applied") or []}
    shape = None
    if template is not None:
        front, shape = shaped(front, template, values, list(agents))
    reports = []
    for line in block(front, "reports"):
        if "->" not in line:
            decline(f"team-invalid -- {path}: reports: `{line}` -- an edge is `a b -> c`.")
        left, right = line.split("->", 1)
        sources, targets = left.split(), right.split()
        if not sources or len(targets) != 1:
            decline(f"team-invalid -- {path}: reports: `{line}` -- members on the left, one member on the right.")
        for one in sources + targets:
            if one not in agents:
                decline(f"participant-unknown -- {path}: reports: `{one}` is a member nobody declared.")
        reports.append({"from": sources, "to": targets[0]})
    root_agent = str(front.get("root") or "").strip()
    if not root_agent:
        decline(f"root-missing -- {path}: `root:` names the member a task goes to when no `--to` names one.")
    if root_agent not in agents:
        decline(f"participant-unknown -- {path}: root `{root_agent}` is a member nobody declared.")
    principals = []
    for line in block(front, "principals"):
        if len(line.split()) != 1:
            decline(f"team-invalid -- {path}: principals: `{line}` -- one name per line.")
        principals.append(line)
    ceremonies = [ceremony_of(line, agents, path) for line in block(front, "ceremonies")]
    names = [one.name for one in ceremonies]
    for one in ceremonies:
        if names.count(one.name) > 1:
            decline(f"team-invalid -- {path}: ceremonies: `{one.name}` declared twice.")
        if one.after is not None and one.after not in names:
            decline(f"team-invalid -- {path}: ceremonies: `{one.name}` follows `{one.after}`, a ceremony nobody declared.")
    acyclic(ceremonies, path)
    entries: dict[str, str] = {}
    for line in block(front, "entries"):
        if "->" not in line:
            decline(f"team-invalid -- {path}: entries: `{line}` -- one line is `<trigger> -> <document>`.")
        trigger, document = (part.strip() for part in line.split("->", 1))
        if not trigger or len(document.split()) != 1:
            decline(f"team-invalid -- {path}: entries: `{line}` -- one trigger, one document.")
        if trigger != "do" and trigger not in names:
            decline(f"team-invalid -- {path}: entries: `{trigger}` is neither `do` nor a declared "
                   "ceremony's name.")
        if trigger in entries:
            decline(f"team-invalid -- {path}: entries: `{trigger}` declared twice.")
        entries[trigger] = document
    roles: dict[str, list[str]] = {}
    for line in block(front, "roles"):
        key, *members = line.split()
        if not conductor.instance.valid_slug(key):
            decline(f"team-invalid -- {path}: roles: `{key}` -- a role key is one slug (lowercase, digits and single "
                    "dashes), the author's own word.")
        if key in roles:
            decline(f"team-invalid -- {path}: roles: `{key}` declared twice -- one line per key.")
        for at, member in enumerate(members):
            if member not in agents:
                decline(f"participant-unknown -- {path}: roles: `{member}` is a member nobody declared.")
            if member in members[:at]:
                decline(f"team-invalid -- {path}: roles: `{line}` -- `{member}` twice on the line.")
        roles[key] = members
    if "work" in front:
        decline(f"key-moved -- {path}: `work:` is the season's -- move the line to teams/{name}/{SEASON_DOC}.")
    applied = (made or {}).get("applied") or []
    named = [one["name"] for one in (template.values if template is not None else None) or []]
    return Team(agents=agents, reports=reports, root=root_agent, principals=principals,
                ceremonies=ceremonies, entries=entries, roles=roles,
                limits=limits_of(front, path), schedule=schedule_of(front, path),
                name=shown, description=description, digest=hashlib.sha256(data).hexdigest()[:12],
                template=None if template is None else
                         {"template": template.template, "origin": template.origin,
                          "values": [value for value in applied if value["name"] in named]},
                applied=applied, read=(made or {}).get("read") or documents_none(path),
                intention="" if template is None else rendered(
                    template, shape, values, any(one.name == "daily" for one in ceremonies)))


def name_shown(front: dict, name: str) -> str:
    """-> the name a team is SHOWN by, from the front matter of its `TEAM.md`: its `name:`, one line of 1 to
    `NAME_CHARS` printable characters -- the directory's name, `name`, when the key is absent or says no such line."""
    said = front.get("name")
    shown = "" if said is None else str(said).strip()
    return shown if shown and len(shown) <= NAME_CHARS and shown.isprintable() else name


def description_shown(front: dict) -> str | None:
    """-> what a team DOES, from the front matter of its `TEAM.md`: its `description:` when it is one judged line
    (`described_well`), None otherwise."""
    said = front.get("description")
    shown = "" if said is None else str(said).strip()
    return shown if described_well(shown) else None


def declare_changes(name: str, asked: dict, template) -> tuple[list[tuple], list[str]]:
    """-> (the changes `declare`'s flags make to a values file, in the form `values_written` takes, the keys they
    name): `description:` JSON-quoted, so that any printable sentence reads back; `template:`; `values:`, a line
    `<name> = <value>` per `--value`; `documents:`, the WHOLE line of each `--document`, named by its key; `agents:`, a
    line `<name> <path>` per `--member`; `reports:`, the line of each `--report`, named by its target (`row_named`);
    `roles:`, the WHOLE line of each `--role`, its key then the members given;
    `root:`; `principals:`, a line per `--principal`; a limit and `schedule:` under their keys. Each line takes the
    place of every line of the block with the same name, so a name written on several lines is left on one. Each
    contrary (`--no-value`, `--no-document`, `--no-member`, `--no-role`, `--no-report` its target) takes out every
    line of that name, nothing where none stands. At a BIRTH (`template`: the preset `--template` names, as
    `template_of` reads it in `declare_verb` when no `TEAM.md` stands; None otherwise), what the preset gives a
    team no flag describes: its role keys, filled by place (`preset_roles`), its default members at
    `agents/<name>/<member>` without a `--member`, and, for a preset without `form:`, its own `reports:` and its root
    as they stand -- a form's edges and root are never written: every `start` makes them again. DECLINES what
    `preset_roles` and `formed` decline at a birth, `team-invalid` for a principal that is not one name and
    `team-invalid` for a limit that is no number (`numbered`)."""
    changes: list[tuple] = []
    out = lambda old: None
    said = lambda line: (lambda old: line)

    def lines_of_block(key: str, set_: list[tuple[str | None, str]], gone: list[str]) -> None:
        if set_ or gone:
            changes.append((key, [*((word, out) for word in gone), *((word, said(line)) for word, line in set_)]))

    if asked["description"] is not None:
        changes.append(("description", json.dumps(asked["description"].strip(), ensure_ascii=False)))
    if asked["template"] is not None:
        changes.append(("template", season_said(asked["template"])))
    lines_of_block("values", [(named, f"{named} = {value}".rstrip()) for named, value in asked["value"]],
                   asked["no-value"])
    lines_of_block("documents", [(line.split()[0], line) for line in asked["document"]], asked["no-document"])
    members, reports, head, keys = list(asked["member"]), [], asked["root"], []
    if template is not None:
        members = members or [(one, f"agents/{name}/{one}") for one in template.members]
        if template.roles:                             # the preset's role keys, filled by place at the birth
            values = {**{one["name"]: one["default"] or "" for one in template.values}, **dict(asked["value"])}
            keys = preset_roles(template, formed(template, [member for member, _ in members], head, values))
        if template.form is None:                      # no form: the preset's edges and its root are written
            reports = list(template.reports)
            head = head or (str(template.root) if template.root else members[0][0] if members else None)
    lines_of_block("agents", [(member, f"{member} {at}") for member, at in members], asked["no-member"])
    lines_of_block("roles", [(line.split()[0], line) for line in keys], [])
    lines_of_block("reports", [(None, edge) for edge in reports], [])
    lines_of_block("reports", list(asked["report"]), asked["no-report"])
    lines_of_block("roles", [(key, " ".join([key, *held])) for key, held in asked["role"]], asked["no-role"])
    if head is not None:
        changes.append(("root", season_said(head)))
    for one in asked["principal"]:
        if not one or len(one.split()) != 1 or one != one.strip():
            decline(f"team-invalid -- `--principal {one}`: one name, no blank.")
    lines_of_block("principals", [(one, one) for one in asked["principal"]], [])
    for flag, whole in (("budget", False), ("launches", True), ("parallel", True), ("timeout", False)):
        if asked[flag] is not None:
            changes.append((flag, str(numbered(flag, asked[flag], whole))))
    if asked["schedule"] is not None:                  # `off`, `5s`, `2m`, minutes: the judge reads it
        bare = re.fullmatch(r"[A-Za-z0-9]+", asked["schedule"])
        changes.append(("schedule", asked["schedule"] if bare else json.dumps(asked["schedule"])))
    return changes, [key for key, _ in changes]
