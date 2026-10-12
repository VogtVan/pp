"""Scenario `path-is-the-repository` -- 4 case(s) (plan core, batch un-chemin-est-celui-du-depot):
- a serve token that is a PATH (it carries a `/`) serves the repository's file when the
  repository holds it, even when the instance holds a homonym under `.sys/`
- without the repository's file the instance answers -- what a member without the source sees --
  and `.sys/...` addresses the machine either way
- the ledger says the place: `repository` for the first, `machine` for the second
- a shadowing is SAID once: the engine's own signal `serve-shadowed` when both homonyms stand,
  nothing when one alone does
"""
from __future__ import annotations

import json

WITNESS = """---
name: PATHS
kind: proc
description: a witness that serves one path twice -- by the repository, by the machine
serve: |
  code: engine/x.py .sys/engine/x.py
proc: |
  SERVE
  INFER
---

The witness of the two homonyms.
"""
AT_REPOSITORY = "FROM = 'the repository'\n"
AT_MACHINE = "FROM = 'the machine'\n"


def _trace(made) -> list[dict]:
    """-> every line of every trace of the instance -- two runs born in one second share
    no order a file name could tell."""
    return [json.loads(line)
            for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("paths")
    env.write("PATHS.md", WITNESS)
    env.write(".sys/engine/x.py", AT_MACHINE)
    at_repository = env.root / "engine" / "x.py"
    at_repository.parent.mkdir(parents=True, exist_ok=True)
    at_repository.write_text(AT_REPOSITORY, encoding="utf-8")

    # --- both homonyms stand: the path is the repository's, `.sys/` addresses the machine ---
    first = env.conductor("t")
    first.forget()
    block = first.start(env.made / "PATHS.md")
    served = dict(block.payloads)
    if (served.get("engine/x.py", "").strip() == AT_REPOSITORY.strip()
            and served.get(".sys/engine/x.py", "").strip() == AT_MACHINE.strip()):
        held("a path is the repository's", "`engine/x.py` serves the repository's file though "
             "the instance holds a homonym under `.sys/`; `.sys/engine/x.py` serves the machine")
    else:
        failures.append(f"  ✗ the repository's path       engine/x.py={served.get('engine/x.py')!r} "
                        f".sys/engine/x.py={served.get('.sys/engine/x.py')!r}")

    lines = _trace(env.made)
    ledger = [line for one in lines if one.get("kind") == "block" for line in (one.get("served") or [])]
    places = {line["subject"]: line.get("package") for line in ledger}
    if places.get("engine/x.py") == "repository" and places.get(".sys/engine/x.py") == "machine":
        held("the ledger says the place", "`repository` for what the repository served, "
             "`machine` for what `.sys/` served")
    else:
        failures.append(f"  ✗ the place                   engine/x.py={places.get('engine/x.py')!r} "
                        f".sys/engine/x.py={places.get('.sys/engine/x.py')!r}")

    shadowed = [one for one in lines if one.get("kind") == "signal"
                and one.get("signal") == "serve-shadowed"]
    if len(shadowed) == 1:
        held("a shadowing is said once", "both homonyms stand: the engine pushes `serve-shadowed` "
             "for that path, one time in the run")
    else:
        failures.append(f"  ✗ the shadowing               {shadowed!r}")

    # --- the repository's file gone: the instance answers, and nothing is shadowed ----------
    at_repository.unlink()
    second = env.conductor("u")
    block = second.start(env.made / "PATHS.md")
    alone = dict(block.payloads)
    quiet = [one for one in _trace(env.made) if one.get("kind") == "signal"
             and one.get("signal") == "serve-shadowed"]
    if alone.get("engine/x.py", "").strip() == AT_MACHINE.strip() and len(quiet) == len(shadowed):
        held("without the repository's file the instance answers", "`engine/x.py` serves the "
             "machine's copy -- what a member without the source sees -- and no shadowing is said")
    else:
        failures.append(f"  ✗ the instance alone          engine/x.py={alone.get('engine/x.py')!r} "
                        f"{quiet!r}")
    return 0
