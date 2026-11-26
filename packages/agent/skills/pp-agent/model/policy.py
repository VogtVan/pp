"""What a launch is asked and what it asks of its harness: the flags of a call, the policy they give."""
from __future__ import annotations

from dataclasses import dataclass, fields, replace

from model.refusal import Refusal
from model.words import USAGE

SAID = ("conduct",)             # what no flag gives: a conversation's word on its run


@dataclass(frozen=True)
class Asked:
    """What a launch is asked: one field per flag of `run`, `chat`, `start`, `open` and `close`, as typed -- a
    flag without a value true once given, a flag given several times kept in the order it came --, and `conduct`,
    which no flag gives: false once a conversation said `conduct off`, None before any word. `max_budget_usd` is
    a number once a run resumed or a `set` of a conversation gave it."""
    message: str | None = None
    message_file: str | None = None
    model: str | None = None
    max_budget_usd: float | str | None = None
    permissions: str | None = None
    effort: str | None = None
    launches: str | None = None
    door: str | None = None
    documents: str | None = None
    run: str | None = None
    provider: str | None = None
    harness: str | None = None
    work: str | None = None
    base: str | None = None
    tag: str | None = None
    on_end: str | None = None
    new: bool = False
    json: bool = False
    quiet: bool = False
    heartbeat: str | None = None
    dry_run: bool = False
    detached: bool = False
    package: tuple[str, ...] = ()
    vector: tuple[str, ...] = ()
    conduct: bool | None = None

    @staticmethod
    def of(argv: list[str]) -> "Asked":
        """-> what the words of a call ask, `--<flag>` by `--<flag>`; a word that is no flag, a flag without its
        value: the usage. Two flags that exclude each other refuse in the verb's own words. What it refuses is
        raised, a `Refusal`."""
        known = {one.name.replace("_", "-"): one for one in fields(Asked) if one.name not in SAID}
        found: dict = {}
        index = 0
        while index < len(argv):
            word = argv[index]
            flag = known.get(word[2:]) if word.startswith("--") else None
            if flag is None:
                raise Refusal(USAGE)
            if flag.default is False:
                found[flag.name] = True
                index += 1
                continue
            if index + 1 >= len(argv):
                raise Refusal(USAGE)
            value = argv[index + 1]
            found[flag.name] = (*found.get(flag.name, ()), value) if flag.default == () else value
            index += 2
        asked = Asked(**found)
        if asked.message is not None and asked.message_file is not None:
            raise Refusal("one message: --message or --message-file, not both.")
        if asked.new and asked.run is not None:
            raise Refusal("one run: --new opens, --run <key> resumes, not both.")
        if asked.base is not None and asked.work is None:
            raise Refusal("`--base <ref>` names what `--work <repo>` cuts the branch from: give --work too.")
        return asked

    def resumed(self, policy: "Policy") -> "Asked":
        """-> these flags, completed by what a run's last `policy` names and they do not: the model, the cap
        of the budget, the permission regime, the effort -- a flag of the call always prevails."""
        return replace(self,
                       model=self.model if self.model is not None else policy.model,
                       max_budget_usd=self.max_budget_usd if self.max_budget_usd is not None else policy.max_budget_usd,
                       permissions=self.permissions if self.permissions is not None else policy.permissions,
                       effort=self.effort if self.effort is not None else policy.effort)


@dataclass(frozen=True)
class Policy:
    """What a launch asks of its harness: the model, the cap of the run's budget in USD, the permission regime,
    the effort -- None for what it does not name."""
    model: str | None = None
    max_budget_usd: float | str | None = None
    permissions: str | None = None
    effort: str | None = None

    @staticmethod
    def of(line: dict | None) -> "Policy":
        """-> the policy a mapping carries -- the `policy` of a line of `messages.jsonl`, what the engine's face
        judged --; no mapping, no policy named."""
        line = line if isinstance(line, dict) else {}
        return Policy(line.get("model"), line.get("max_budget_usd"), line.get("permissions"), line.get("effort"))

    def json(self) -> dict:
        """-> the mapping a record's line, a `--json` output and the engine's face read: the keys the policy
        names, in the order of its fields; no key for what it does not name."""
        return {one.name: getattr(self, one.name) for one in fields(self) if getattr(self, one.name) is not None}
