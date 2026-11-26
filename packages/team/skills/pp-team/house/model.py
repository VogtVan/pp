"""The `house` domain, layer `model`: the values every other domain of pp-team stands on.

A definition belongs here when it is plain data and does nothing: a constant (a file name under the house, a flag, the
usage line) or a type (an exception a judgement raises, a frozen class that carries a record). Nothing here reads the
disk, the clock or the environment. `house` comes first in the order of the domains, so every module of the skill may
read what this one holds.

It holds `Typed`, the bare base of every typed value of the model -- a body, a part, an event, the state, a carrier: it
carries no method, and `plain` knows a typed value by it. A typed value reads by its attributes alone, never by key, and
two typed values are equal only when they are the same object. `Body` is the base of the body of one kind of event: its
`KIND`, its fields in the order its writers write them, `KINDS` -- the kinds it reads, its own and the kind of an old
journal it translates -- and `of`, the body a line of the journal carries. Every body is read the same way: `of` takes
once per class what it reads, fills the instance at once without the frozen `__init__`, and reads a key that is no name
of a field through the class's table `KEYS`; a field declared without a default is required, and `of` raises `KeyError`
at its key when the line lacks it. A writer COMPOSES a body by `made`, which keeps the fields it is given in their
order, and adds to it by `but`; its `json()` gives `kind` then those fields alone, so the line written is the one the
writer's literal writes today. `Part` is the base of one part of the team's state, a field per key it holds, with `of`,
the part a working state holds. `plain` gives a value with every typed value in it turned into its `json()`: what a JSON
writer receives.
"""
from __future__ import annotations

from dataclasses import MISSING, fields, replace
from typing import ClassVar

TEAMS = "teams"                  # under the house's root: one directory per team, its TEAM.md
TEAM_DOC = "TEAM.md"
JOURNAL = "journal.jsonl"        # under the house's records: teams/<name>/journal.jsonl
BORDER = "---"
NOW = "PP_NOW"                   # names the tick's wall clock (ISO, naive local): the bench, a try
HOUSE = "."                                      # the path of the house itself: the agent pp-agent never adds nor removes
RETIRED_FLAGS = {"--wakes": "--launches", "--budget-wakes": "--budget-launches"}
MINUTE = 60                                      # the seconds of `m` and of a bare number of minutes in a duration
HOUR = 60 * MINUTE                               # the seconds of `h`
USAGE = ("usage: pp-team start <name> [--message <text> [--to <member>] [--name <text>]] [--budget <usd>] "
         "[--budget-launches <n>] [--context <n>%] [--provider <name>] [--harness <command>] "
         "[--model <m>] [--permissions auto|strict|bypass] "
         "[--effort low|medium|high|xhigh|max] [--no-tick] [--package <name>=on|off]... "
         "[--member <member> [--provider <name>] [--model <m>] [--effort <e>] [--permissions <p>] "
         "[--package <name>=on|off]...]... | "
         "post <name> [--message <text>] [--to <member>] [--task <id> [--ask] | [--name <text>] [--context <n>%]] [--reply <id>] [--stop] "
         "[--as <principal>] [--every \"day|weekday|mon..sun HH:MM\" [--context <n>%] [--description <text>]] "
         "[--no-tick] | stop <name> [--task <id>] [--kill] [--json] [--no-tick] | "
         "stop <name> --recurrence <R<n>> [--no-tick] | "
         "recurrence <name> <R<n>> [--every \"day|weekday|mon..sun HH:MM\"] [--context <n>%|off] [--message <text>] "
         "[--description <text>] [--as <principal>] [--no-tick] | "
         "recurrence <name> <R<n>> --now [--as <principal>] [--no-tick] | "
         "recurrence <name> --task <T<n>> --every \"day|weekday|mon..sun HH:MM\" [--context <n>%] "
         "[--description <text>] [--as <principal>] "
         "[--no-tick] | "
         "tick <name> | tick --all [--entry] | follow <name> <tag> | "
         "timer <name> --sleep <seconds> --due <local date-time> --token <token> | "
         "status [<name>] [--json] | "
         "watch <name> [--task <id>] [--json] [--heartbeat <seconds>] [--for <seconds>] [--until-done] | "
         "log <name> [--task <id>] [--last <n>] [--json] | result <name> [<task>] | "
         "responses <name> [--since <id>] [--agent <member>] [--task <t>] [--last <n>] [--json] | "
         "stats <name> [--season <n> | --all] [--cost usd|launches|tokens] [--json] | "
         "inbox [<name>] [--seen [--id <n>] | --json] | roster [--json] | "
         "snapshot <name> | entry <name> --run <key> | reset <name> [--member <member>] | "
         "pause <name> [--as <principal>] | resume <name> [--as <principal>] [--no-tick] | "
         "pause <name> --recurrence <R<n>> [--as <principal>] | "
         "resume <name> --recurrence <R<n>> [--as <principal>] [--no-tick] | "
         "resume <name> --task <id> [--to <member>|all] [--message <text>] [--as <principal>] [--no-tick] | "
         "resume <name> --quota [--member <member>] [--as <principal>] [--no-tick] | "
         "budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick] | "
         "ring <name> <ceremony> [--as <principal>] [--no-tick] | templates [--json] | "
         "templates --render <directory>/<name> [--value <name>=<value>]... "
         "[--team <name> [[--season] --text-file <path>|-]] [--json] | "
         "document <directory>/<name> [--new | --body-file <path>|- | --delete] [--json] | "
         "declare <name> [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]... "
         "[--document \"<key>|all <document> ...\"]... [--no-document <key>]... [--body-file <path>|-] "
         "[--member <name> <path>]... [--no-member <name>]... [--role <key> [<member> ...]]... [--no-role <key>]... "
         "[--report \"<member>... -> <member>\"]... [--no-report <member>]... "
         "[--root <member>] [--principal <p>]... [--budget <usd>] [--launches <n>] [--parallel <n>] [--timeout <s>] "
         "[--schedule <n>s|<n>m|<n>h|<minutes>|off] [--description <text>] [--json] | "
         "declare <name> --season [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]... "
         "[--document \"<key>|all <document> ...\"]... [--no-document <key>]... [--body-file <path>|-] "
         "[--budget <usd>] [--budget-launches <n>] [--silence <n>] [--context <n>%] [--provider <name>] [--model <m>] "
         "[--effort low|medium|high|xhigh|max] [--permissions auto|strict|bypass] [--harness <command>] "
         "[--package <name>=on|off]... [--json] [--member <member> [--provider <name>] [--model <m>] [--effort <e>] "
         "[--permissions <p>] [--silence <n>] [--package <name>=on|off]...]... | "
         "declaration <name> [--json] [[--season] --text-file <path>|-] | "
         "delete <name> [--agent <path>]... [--yes] [--json] | rename <name> <new> [--json]")
MANY = ("vector", "value")                         # the flags of `flags` a verb takes several times: a list


IMMUTABLE = (type(None), bool, int, float, str, tuple, frozenset)   # the defaults a body's field may take


class Declined(Exception):
    """A declaration the judge does not accept: its text is the refusal `start` writes."""


def decline(said: str) -> None:
    raise Declined(said)


class Typed:
    """A TYPED value of the model: a body, a part, an event, the state, a carrier. It reads by its attributes, and
    `json()` gives the dictionary a JSON writer takes; `plain()` knows it by this base."""


class Body(Typed):
    """What ONE kind of event carries beyond `kind`, `id`, `at`, `team`: a frozen class per kind, its `KIND`, its fields in
    the order its writers write them. `KINDS`: the kinds it reads, its own alone unless it also reads the kind of an old
    journal. `KEYS`: a field -> its key in the line, for a key that is no name of a field (`from`, `name-refused`).
    `of(line)`: the body a line carries, made without the frozen `__init__` -- the fields at their defaults, then the
    keys of the line its fields name, each under its key -- from what `reading()` takes once per class; a class that
    reads a key of an old journal redefines `of` and calls `super().of`. A field declared without a default is REQUIRED:
    `of` raises `KeyError(<key>)` on a line without it, as the fold that read it by `[...]` did. `reading()` refuses at
    load a class with a `__post_init__`, which `of` does not call, or a field whose default is not immutable.
    `made(**fields)`: the body a writer COMPOSES, born by the class's `__init__`, which keeps the names given in the
    order the writer gives them; `but(**fields)`: one more composed body, the fields given added after the others or
    given their new values in place. `json()` has two paths. A body READ gives `kind` then all its fields, `None`
    included; the line itself is kept by its event. A body COMPOSED gives `kind`
    then the names given and no other, in their order, a name given at `None` written at `None` -- the line its
    writer's literal writes today. On both paths a field is written under its key."""
    KIND: ClassVar[str] = ""
    KINDS: ClassVar[tuple] = ()
    KEYS: ClassVar[dict] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        annotated = [name for name in ("KIND", "KINDS", "KEYS") if name in vars(cls).get("__annotations__", {})]
        if annotated:                              # an annotation would make it a field, written by `json()`
            raise TypeError(f"{cls.__qualname__} annotates {', '.join(annotated)}: a body's kinds and keys are class "
                            "variables -- write `KIND = ...` without an annotation")
        if "KINDS" not in vars(cls):
            cls.KINDS = (cls.KIND,)

    @classmethod
    def reading(cls) -> tuple:
        """-> how the class reads a line, taken once per class: the fields at their defaults, the fields read under
        their own name, the pairs (field, key) read under another key, the keys a line must carry -- of the fields
        without a default, in their order. A class that this reading would wrong is refused: a `__post_init__`,
        which `of` does not call; a field whose default is made by a factory or is not immutable, which one instance
        would share with the next."""
        held = cls.__dict__.get("_reading")
        if held is None:
            if hasattr(cls, "__post_init__"):
                raise TypeError(f"{cls.__qualname__} defines __post_init__: a body is read without its __init__")
            blank, named = {}, []
            for one in fields(cls):
                named.append(one.name)
                if one.default is MISSING and one.default_factory is MISSING:
                    continue                       # required: the line carries it
                if one.default is MISSING or type(one.default) not in IMMUTABLE:
                    raise TypeError(f"{cls.__qualname__}.{one.name} has no immutable default: a body's fields "
                                    "default to None, a number, a text or a tuple, or have none and are required")
                blank[one.name] = one.default
            keys = cls.KEYS
            renamed = tuple((name, key) for name, key in keys.items() if name in named)
            required = tuple(keys.get(name, name) for name in named if name not in blank)
            held = (blank, frozenset(named) - {name for name, _ in renamed}, renamed, required)
            cls._reading = held
        return held

    @classmethod
    def of(cls, line: dict):
        blank, own, renamed, required = cls.__dict__.get("_reading") or cls.reading()
        for key in required:
            if key not in line:
                raise KeyError(key)
        made = object.__new__(cls)                 # frozen to any other code: filled once, here, without __init__
        values = made.__dict__
        values.update(blank)
        for key, value in line.items():
            if key in own:
                values[key] = value
        for name, key in renamed:
            if key in line:
                values[name] = line[key]
        return made

    @classmethod
    def made(cls, **given):
        """-> the body a writer COMPOSES: born by the class's `__init__`, the fields not given at their default, and the
        names given kept, in the order the writer gives them, beside the fields (`_given`), which `json()` renders and
        nothing else. A name is a field's (`sender`, never `from`); a name that is no field, or a required field not
        given, raises `TypeError`."""
        made = cls(**given)
        object.__setattr__(made, "_given", tuple(given))
        return made

    def but(self, **more):
        """-> a composed body more: the fields given take their new values, a field already given keeps its place, a new
        one comes after -- as `dict.update` on the literal; this body stays as it is. A body read from a line is not
        amended: `TypeError`."""
        given = self.__dict__.get("_given")
        if given is None:
            raise TypeError(f"{type(self).__qualname__} was read from a line: a body read is not amended")
        made = replace(self, **more)
        object.__setattr__(made, "_given", given + tuple(name for name in more if name not in given))
        return made

    def json(self) -> dict:
        keys, given = self.KEYS, self.__dict__.get("_given")
        if given is not None:                      # composed: `kind`, then the names its writer gave, in their order
            return {"kind": self.KIND, **{keys.get(name, name): getattr(self, name) for name in given}}
        return {"kind": self.KIND, **{keys.get(one.name, one.name): getattr(self, one.name) for one in fields(self)}}


class Part(Typed):
    """One PART of the team's state: a frozen class per domain, a field per key of the state it holds. `json()`: its
    keys and their values; `of(state)`: the part a working state holds, its keys -- a typing batch redefines it."""

    @classmethod
    def of(cls, state: dict):
        return cls(**{one.name: state.get(one.name) for one in fields(cls)})

    def json(self) -> dict:
        return {one.name: getattr(self, one.name) for one in fields(self)}


def plain(value):
    """-> `value` with every typed value in it given as its `json()`: what a JSON writer takes."""
    if isinstance(value, Typed):
        return plain(value.json())
    if isinstance(value, dict):
        return {key: plain(one) for key, one in value.items()}
    if isinstance(value, list):
        return [plain(one) for one in value]
    if isinstance(value, tuple):
        return tuple(plain(one) for one in value)
    return value
