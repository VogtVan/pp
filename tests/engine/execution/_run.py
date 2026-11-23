"""Support module of `tests/engine/execution/` (rule 10): what the run hosts share -- the key a
`-new` prints, the variables of the agent's call, a run opened on a door, its slot and its trace read back,
the closing and the matter of a rendered output, the steps an output says on `terminal` and the
productions due said by their print calls, the witness documents of the principal's mode,
a package of providers pinned by hand. Never collected; a host loads it by `support(__file__, "run")`.
"""
from __future__ import annotations

import json
import os
import re

from conductor import Conductor, persistence, settings
from conductor.core import language
from tests.harness import cli, vendor

CONDUCTED_RUN = "PP_CONDUCTED_RUN"          # the run a launcher conducts: on the agent's calls alone
KEY = re.compile(r"run ([0-9a-f]{6})")
SAID = f"=> {language.TERMINAL}  ("        # a step's line said on `terminal`, its document behind the parenthesis
CODES = re.compile(r"^INFER proof \[([^\]]*)\]", re.MULTILINE)   # the proof's own INSTRUCTION line, never a text that quotes one

PROVER = ("---\nname: PROVER\nkind: proc\ndescription: a witness\nconstraints.production: |\n"
          "  Z1  say it plainly\nproc: |\n  WORK\n  PROVE\n---\nprove\n")
GOOD = '[{"code": "Z1", "evidence": "said plainly", "verdict": "ok"}]'
LONGRUN = "---\nname: LONGRUN\nkind: proc\ndescription: a witness\nproc: |\n  SERVE LONG.md\n  WORK\n---\nread\n"
PAST = ("---\nname: LONG\nkind: doc\n---\n\n"   # past the floor of a principal's cap: it cuts whatever the setting
        + "long line of matter\n" * (2 * settings.PRINCIPAL_CAP // 20) + "\n")
CAP = "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n"

PACKAGE = "name: {name}\nversion: 0.0.1\ndescription: a witness package\nrequires: [kit]\n"
PROVIDER = ("---\nname: {name}\nkind: doc\ndescription: a witness provider\nprovides: {token}\n"
            "with: {skill}\n---\n\n{name} provides\n")


def key_of(text: str) -> str:
    """-> the run key an output's heading says, "" when none."""
    found = KEY.search(text)
    return found.group(1) if found else ""


def agent(key: str) -> dict:
    """-> the variables of the AGENT's call on the run `key`: its launcher names the run to its harness."""
    return {CONDUCTED_RUN: key}



def said(text: str) -> list:
    """-> the documents of the steps an output says on `terminal`, in order."""
    return [line.rsplit("(", 1)[1].rstrip(")") for line in text.splitlines() if SAID in line]


def say_due(env, key: str) -> str:
    """The agent's productions said, each by its print call, in the order they are due -> what asks the
    next value: the last print's line, or -- when the prints moved the run to a block never served,
    held -- that block, served by the principal's bare call."""
    answered = ""
    for document in env.conductor(key).prints_due():
        answered = cli(env.engine, key, "-print", document, "-", cwd=env.root, stdin="said\n",
                       env=agent(key)).stdout
    if answered and slot(env, key).get("held"):
        answered = cli(env.engine, key, cwd=env.root).stdout
    return answered

def opened(env, door: str | None = None, extra: dict | None = None, *words: str):
    """-> (the key, the first output): `-new` at the environment -- the principal's call --, on `door`
    when named, `extra` variables and `words` (a message) added."""
    variables = {**({"PP_DOOR": door} if door else {}), **(extra or {})}
    out = cli(env.engine, "-new", *words, cwd=env.root, env=variables or None)
    return key_of(out.stdout), out


def slot(env, key: str) -> dict:
    """-> the run's slot as JSON, {} when gone."""
    path = persistence.slot_of(env.made, key)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def trace(env, key: str) -> list[dict]:
    """-> every event of the run's own trace, in order."""
    log = slot(env, key).get("log") or ""
    path = env.made / persistence.DIRECTORY / log
    if not log or not path.is_file():
        return []
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def kinds(env, key: str) -> list[str]:
    """-> the kinds of the run's trace events, in order."""
    return [one.get("kind", "") for one in trace(env, key)]


def events(made) -> list[dict]:
    """-> every event of the instance's NEWEST trace file, in order."""
    log = sorted((made / ".sys" / "state").glob("session-*.jsonl"))[-1]
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def closing(text: str) -> str:
    """-> the lines from the closing's arrow to the end of a rendered output."""
    lines = text.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return "\n".join(lines[at:])


def matter(text: str, key: str, root) -> str:
    """-> the output without its heading line and its closing, the key and the root neutralized."""
    body = text.split("\n▶ ")[0]
    return body.replace(key, "KEY").replace(str(root), "WS").split("\n", 1)[-1]


def proof_of(text: str) -> str:
    """-> the proof a witness agent pipes: every code the output asks, said ok."""
    found = CODES.search(text)
    return json.dumps([{"code": one, "evidence": "said plainly", "verdict": "ok"}
                       for one in found.group(1).split()]) if found else "[]"


def under(variables: dict, call):
    """-> what `call` returns with `variables` set in THIS process -- the in-process twin of a call's
    environment (the agent's: `agent(key)`)."""
    spots = {name: os.environ.get(name) for name in variables}
    os.environ.update(variables)
    try:
        return call()
    finally:
        for name, spot in spots.items():
            if spot is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = spot


def pin_package(made, name: str, providers: dict[str, tuple[str, str, str]]) -> None:
    """A witness package of providers pinned by hand at `made`: one provider document per entry
    `{document: (token, skill, code)}`, each skill a script of `code`."""
    vendor(made, name, PACKAGE.format(name=name),
           {document: PROVIDER.format(name=document, token=token, skill=skill)
            for document, (token, skill, _) in providers.items()},
           {skill: code for _, skill, code in providers.values()})


def conductor_of(env, key: str | None = "t") -> Conductor:
    """-> a fresh conductor on the environment under `key`."""
    return Conductor(env.member, env.engine, key)
