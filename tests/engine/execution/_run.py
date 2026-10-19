"""Support module of `tests/engine/execution/` (rule 10): what the run hosts share -- the key a
`-new` prints, the principal's mark, a run opened on a door, its slot and its trace read back,
the closing and the matter of a rendered output, the witness documents of the principal's mode,
a witness package pinned by hand. Never collected; a host loads it by `support(__file__, "run")`.
"""
from __future__ import annotations

import json
import os
import re

from conductor import Conductor, instance, persistence, settings
from tests.harness import cli

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"     # the mark of the principal's call
CONDUCTED_RUN = "PP_CONDUCTED_RUN"          # the run a launcher conducts
MARK = {VARIABLE: "true"}
KEY = re.compile(r"run ([0-9a-f]{6})")
CODES = re.compile(r"INFER proof \[([^\]]*)\]")

PROVER = ("---\nname: PROVER\nkind: proc\ndescription: a witness\nconstraints.production: |\n"
          "  Z1  say it plainly\nproc: |\n  WORK\n---\nprove\n")
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


def opened(env, marked: bool = False, door: str | None = None, extra: dict | None = None, *words: str):
    """-> (the key, the first output): `-new` at the environment, on `door` when named, under the
    principal's mark when `marked`, `extra` variables and `words` (a message) added."""
    variables = {**({"PP_DOOR": door} if door else {}), **(MARK if marked else {}), **(extra or {})}
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


def under(value: str | None, call):
    """-> what `call` returns with the principal's variable set to `value` (None: absent) in THIS
    process -- the in-process twin of the console's mark."""
    spot = os.environ.get(VARIABLE)
    if value is None:
        os.environ.pop(VARIABLE, None)
    else:
        os.environ[VARIABLE] = value
    try:
        return call()
    finally:
        if spot is None:
            os.environ.pop(VARIABLE, None)
        else:
            os.environ[VARIABLE] = spot


def vendor(made, name: str, manifest: str, documents: dict[str, str],
           skills: dict[str, str] | None = None) -> None:
    """A witness package pinned by hand at `made`, as an install vendors one: its `manifest`,
    its `documents` `{name: text}` under `procs/`, its `skills` `{name: code}` each beside its
    SKILL.md, and the instance's pins naming it."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for document, text in documents.items():
        (root / "procs" / f"{document}.md").write_text(text, encoding="utf-8")
    for skill, code in (skills or {}).items():
        home = root / "skills" / skill
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: a witness\n---\n\n{skill}\n",
                                       encoding="utf-8")
        (home / f"{skill}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


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
