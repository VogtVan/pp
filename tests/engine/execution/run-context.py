"""Scenario `run-context` -- a script the engine launched knows ITS run (plan core,
batch le-contexte-du-run, 2026-09-15). Every value is read by a script the CONSOLE
launched, never by a function call of the bench:
- the same witness skill, played as a payload provider, as a sink and by `-s`, writes
  the key of the run that launched it
- the values follow the exchanges: `exchange 1 / is_new / is_boot` at the first, none of
  it at the second; `-compacted` declared during the third makes `is_boot` true THERE
  and false at the fourth
- two runs opened beside each other never see each other's key
- without a run -- a package command at the keyless console -- `context-no-run`; a
  `PP_RUN` inherited from the shell designates nothing
- the face is read-only: the slot is byte-identical around a `-s` reading
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from conductor import compiling, instance, persistence
from tests.harness import SOURCE

RECORD = "ctx.record"

ALPHA = """name: alpha
version: 0.0.1
description: a witness package whose skill asks its run
requires: [kit]
contributes:
  commands:
    - {verb: alpha-ctx, skill: pp-alpha, args: [ctx, command]}
"""
CTXDOC = """---
name: CTXDOC
kind: doc
description: the witness's context, served as a payload
provides: alpha-ctx
with: pp-alpha ctx provider
---

ctx
"""
SKILL = '''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _core

RECORD = Path.cwd() / "ctx.record"


def _line(label):
    conductor = _core.core(__file__)
    ctx = conductor.context.current(_core.home(__file__))
    return " ".join([label, ctx.key, str(ctx.exchange()),
                     str(ctx.is_new()).lower(), str(ctx.is_boot()).lower()])


def main(arguments):
    if arguments[:1] == ["ctx"]:
        label = " ".join(arguments[1:]) or "bare"
    else:
        sys.stdin.read()          # the SINK: the production arrives on stdin
        label = "sink"
    try:
        line = _line(label)
    except Exception as wrong:
        print(f"{label} refused {getattr(wrong, 'code', type(wrong).__name__)}", file=sys.stderr)
        return 2
    with open(RECORD, "a", encoding="utf-8") as out:
        out.write(line + "\\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''
ASK = """---
name: ASK
kind: proc
description: reads the witness's context, hands its answer to the witness
payloads: alpha-ctx
sink: pp-alpha
output: line
proc: |
  INFER
---

say one line
"""
LOOP = """---
name: LOOP
kind: proc
cycle: true
description: one CALL per exchange
tools: |
  pp-alpha
proc: |
  CALL ASK.md
  FINAL
---

the loop
"""


def _pin_alpha(made) -> None:
    root = made / ".sys" / "vendor" / "alpha@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "pp-alpha").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(ALPHA, encoding="utf-8")
    (root / "procs" / "CTXDOC.md").write_text(CTXDOC, encoding="utf-8")
    (root / "skills" / "_core.py").write_text(
        (SOURCE / "packages" / "steering" / "skills" / "_core.py").read_text(encoding="utf-8"),
        encoding="utf-8")
    (root / "skills" / "pp-alpha" / "SKILL.md").write_text(
        "---\nname: pp-alpha\ndescription: the witness that asks its run\n---\n\npp-alpha\n",
        encoding="utf-8")
    (root / "skills" / "pp-alpha" / "pp-alpha.py").write_text(SKILL, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["alpha"] = "0.0.1"
    instance.write(made, pins)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("context")
    _pin_alpha(env.made)
    env.write("procs/ASK.md", ASK)
    env.write("procs/LOOP.md", LOOP)
    settings_before = env.read("SETTINGS.md")
    compiling.build_tools(env.made)
    # a run opens on the floor LOOP by the facade, once; every call that launches the
    # witness afterwards -- the resume, the answer, `-compacted`, `-s`, the command --
    # goes through the console
    from conductor import Conductor, discovery
    member = discovery.instance_member(env.engine)

    def new_run() -> str:
        opener = Conductor(member, discovery.siblings_around(member), env.engine)
        opener.start(env.made / "procs" / "LOOP.md")
        return opener.run_id

    def record() -> list[str]:
        path = env.root / RECORD
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def clear() -> None:
        (env.root / RECORD).write_text("", encoding="utf-8")

    # --- the three launch paths, one run, four exchanges with -compacted at the third --
    clear()
    key = new_run()                                  # exchange 1: CALL ASK -> the provider
    first = env.cli(key, "hello")                    # the sink, then FINAL
    env.cli(key)                                     # exchange 2: the provider again
    env.cli(key, "again")
    env.cli(key)                                     # exchange 3
    env.cli(key, "-compacted")                       # declared: the re-serve replays the provider
    env.cli(key, "third")
    env.cli(key)                                     # exchange 4
    gesture = env.cli(key, "-s", "pp-alpha", "ctx", "gesture")
    lines = record()
    expected = [f"provider {key} 1 true true", f"sink {key} 1 true true",
                f"provider {key} 2 false false", f"sink {key} 2 false false",
                f"provider {key} 3 false false", f"provider {key} 3 false true",
                f"sink {key} 3 false true", f"provider {key} 4 false false",
                f"gesture {key} 4 false false"]
    if lines == expected and first.returncode == 0 and gesture.returncode == 0:
        held("a script knows its run, by every path", "provider, sink and `-s` all wrote "
             f"`{key}`; exchange 1 is new and boot, 2 neither, the compaction declared at 3 "
             "makes boot true there and false at 4")
    else:
        failures.append(f"  ✗ run context                 {lines} rc={first.returncode}/{gesture.returncode} "
                        f"{gesture.stderr[-200:]!r}")

    # --- the face is read-only around a `-s` reading ----------------------------------
    before = env.session().read_bytes() if len(persistence.slots(env.made)) == 1 else b""
    env.cli(key, "-s", "pp-alpha", "ctx", "again")
    after = env.session().read_bytes() if len(persistence.slots(env.made)) == 1 else b"?"
    if before and before == after:
        held("the face is read-only", "the slot is byte-identical around the reading")
    else:
        failures.append("  ✗ face wrote                  the slot moved around a reading")

    # --- two runs beside each other never see each other's key -----------------------
    clear()
    other = new_run()                                # a second run, beside the first
    env.cli(other, "one")
    env.cli(key, "-s", "pp-alpha", "ctx", "first")
    env.cli(other)
    env.cli(key, "-s", "pp-alpha", "ctx", "first")
    lines = record()
    if (lines == [f"provider {other} 1 true true", f"sink {other} 1 true true",
                  f"first {key} 4 false false", f"provider {other} 2 false false",
                  f"first {key} 4 false false"] and key != other):
        held("two runs never see each other", f"`{other}` at its exchanges 1 and 2, `{key}` "
             "still at its 4th -- each script wrote the key of the call that launched it")
    else:
        failures.append(f"  ✗ two runs                    {lines}")

    # --- without a run, a named refusal; an inherited PP_RUN designates nothing ------
    keyless = env.cli("alpha-ctx")
    inherited = subprocess.run([sys.executable, str(env.engine), "alpha-ctx"],
                               cwd=env.root, capture_output=True, text=True,
                               env={**os.environ, "PP_RUN": "zzzzzz"})
    if (keyless.returncode == 2 and "context-no-run" in keyless.stderr
            and inherited.returncode == 2 and "context-no-run" in inherited.stderr
            and "run-unknown" not in inherited.stderr):
        held("without a run, the face refuses", "`./pp alpha-ctx` says `context-no-run`; "
             "a `PP_RUN=zzzzzz` inherited from the shell is dropped by the keyless console")
    else:
        failures.append(f"  ✗ no run                      rc={keyless.returncode}/{inherited.returncode} "
                        f"{keyless.stderr[-120:]!r} {inherited.stderr[-120:]!r}")
    if settings_before != env.read("SETTINGS.md"):
        failures.append("  ✗ settings moved              the scenario wrote the operator's file")
    return 0
