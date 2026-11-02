"""Scenario `run-context` -- the pattern `packaging/run-context`, played from its demonstration.
Every value is read by the package's script, started by the CONSOLE, never by a function call of the
bench; the script reaches the engine through its package's bootstrap `_core` and asks
`conductor.context.current(home)`:
- RUNNER CALLs ASK at every passage: ASK's `exec:`, the provider of the payload it names, its sink
  and a `-s` gesture all write the key of the run that started them
- the values follow the exchanges: `exchange 1 / is_new / is_boot` at the first, none of it at the
  second; `-compacted` declared during the third makes `is_boot` true THERE and false at the fourth
- the face is read-only: the slot is byte-identical around a `-s` reading
- two runs opened beside each other never see each other's key
- the script started outside any run refuses `context-no-run`; under a key no run holds,
  `run-unknown`
- under the principal's conduction the first exchange counts the same
The package `alpha` is pinned from its manifest and documents; its script and the `_core` it carries
are written at the test's time.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

from conductor import Conductor, compiling, discovery, persistence
from tests.harness import PRINCIPAL, cli, demonstrated, demos, manifests, principal, vendor

DRAWER, PATTERN = "packaging", "run-context"
DEMOS = ("ASK.md", "CTXDOC.md", "RUNNER.md")
RECORD = "ctx.record"
SCRIPT = '''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _core import core, home

RECORD = Path.cwd() / "ctx.record"


def _line(label):
    conductor = core(__file__)
    ctx = conductor.context.current(home(__file__))
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


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("run-context")
    documents = {name[:-3]: (demos(DRAWER, PATTERN) / name).read_text(encoding="utf-8") for name in DEMOS}
    vendor(env.made, "alpha", manifests(DRAWER, PATTERN)["alpha.yaml"], documents, {"pp-alpha": SCRIPT})
    package = env.made / ".sys" / "vendor" / "alpha@0.0.1"
    shutil.copy(next((bench.source() / "packages").glob("*/skills/_core.py")), package / "skills" / "_core.py")
    settings_before = env.read("SETTINGS.md")
    compiling.build_tools(env.made)
    member = discovery.instance_member(env.engine)
    script = package / "skills" / "pp-alpha" / "pp-alpha.py"

    def new_run() -> str:
        opener = Conductor(member, env.engine)
        opener.start(package / "procs" / "RUNNER.md")
        return opener.run_id

    def record() -> list[str]:
        path = env.root / RECORD
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def clear() -> None:
        (env.root / RECORD).write_text("", encoding="utf-8")

    # --- the four path, one run, four exchanges with -compacted at the third ---------
    clear()
    key = new_run()                                  # exchange 1: CALL ASK -> exec, provider
    first = env.cli(key, "hello")                    # the sink, then AWAIT
    env.cli(key)                                     # exchange 2
    env.cli(key, "again")
    env.cli(key)                                     # exchange 3
    env.cli(key, "-compacted")                       # declared: the re-serve replays the provider
    env.cli(key, "third")
    env.cli(key)                                     # exchange 4
    gesture = env.cli(key, "-s", "pp-alpha", "ctx", "gesture")
    lines = record()
    expected = [f"exec {key} 1 true true", f"provider {key} 1 true true", f"sink {key} 1 true true",
                f"exec {key} 2 false false", f"provider {key} 2 false false", f"sink {key} 2 false false",
                f"exec {key} 3 false false", f"provider {key} 3 false false",
                f"provider {key} 3 false true", f"sink {key} 3 false true",
                f"exec {key} 4 false false", f"provider {key} 4 false false",
                f"gesture {key} 4 false false"]
    if lines == expected and first.returncode == 0 and gesture.returncode == 0:
        held("a script knows its run, by every path", "exec, provider, sink and `-s` all wrote "
             f"`{key}`; exchange 1 is new and boot, 2 neither, the compaction declared at 3 makes boot "
             "true there and false at 4")
    else:
        failures.append(f"  ✗ run context                 {lines} rc={first.returncode}/{gesture.returncode} "
                        f"{gesture.stderr[-200:]!r}")

    # --- the face is read-only around a `-s` reading ------------------------------------------
    before = env.session().read_bytes() if len(persistence.slots(env.made)) == 1 else b""
    env.cli(key, "-s", "pp-alpha", "ctx", "again")
    after = env.session().read_bytes() if len(persistence.slots(env.made)) == 1 else b"?"
    if before and before == after:
        held("the face is read-only", "the slot is byte-identical around the reading")
    else:
        failures.append("  ✗ face wrote                  the slot moved around a reading")

    # --- two runs beside each other never see each other's key -------------------------------
    clear()
    other = new_run()                                # a second run, beside the first
    env.cli(other, "one")
    env.cli(key, "-s", "pp-alpha", "ctx", "first")
    env.cli(other)
    env.cli(key, "-s", "pp-alpha", "ctx", "first")
    lines = record()
    if (lines == [f"exec {other} 1 true true", f"provider {other} 1 true true", f"sink {other} 1 true true",
                  f"first {key} 4 false false", f"exec {other} 2 false false",
                  f"provider {other} 2 false false", f"first {key} 4 false false"] and key != other):
        held("two runs never see each other", f"`{other}` at its exchanges 1 and 2, `{key}` still at "
             "its 4th -- each script wrote the key of the call that started it")
    else:
        failures.append(f"  ✗ two runs                    {lines}")

    # --- started outside any run, and under a key no run holds ------------------------------
    bare = {name: value for name, value in os.environ.items() if not name.startswith("PP_")}
    keyless = subprocess.run([sys.executable, str(script), "ctx", "alone"], cwd=env.root,
                             capture_output=True, text=True, env=bare)
    unknown = subprocess.run([sys.executable, str(script), "ctx", "stranger"], cwd=env.root,
                             capture_output=True, text=True, env={**bare, "PP_RUN": "zzzzzz"})
    if (keyless.returncode == 2 and "context-no-run" in keyless.stderr
            and unknown.returncode == 2 and "run-unknown" in unknown.stderr):
        held("without its run, the face refuses", "started outside any run: `context-no-run`; "
             "under `PP_RUN=zzzzzz`, a key no run holds: `run-unknown`")
    else:
        failures.append(f"  ✗ no run                      rc={keyless.returncode}/{unknown.returncode} "
                        f"{keyless.stderr[-120:]!r} {unknown.stderr[-120:]!r}")

    # --- under the principal's conduction, the first exchange counts the same ----------------
    clear()
    led = principal(new_run)
    cli(env.engine, led, "hello", cwd=env.root)                    # the agent's production, the sink
    cli(env.engine, led, cwd=env.root, env={PRINCIPAL: "true"})   # the principal's bare call: the AWAIT
    marked = cli(env.engine, led, "the next message", cwd=env.root, env={PRINCIPAL: "true"})
    if record() == [f"exec {led} 1 true true", f"provider {led} 1 true true", f"sink {led} 1 true true",
                    f"exec {led} 2 false false", f"provider {led} 2 false false"] and marked.returncode == 0:
        held("both conductions count the same exchanges", f"`{led}`, opened by its principal: exchange 1 "
             "new and boot, the principal's next message opens exchange 2")
    else:
        failures.append(f"  ✗ principal context           {record()} rc={marked.returncode} {marked.stderr[-160:]!r}")

    if settings_before != env.read("SETTINGS.md"):
        failures.append("  ✗ settings moved              the scenario wrote the operator's file")
    return 0
