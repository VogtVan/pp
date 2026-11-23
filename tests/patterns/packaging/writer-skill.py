"""Scenario `writer-skill` -- the pattern `packaging/writer-skill`, played from its demonstration:
- LEDGERED, a document of the package `ledger`, offers the package's writer, `pp-ledger`: the block
  names it among the step's offers
- eight writers started together, each from its own run, lose nothing: eight entries, none torn
- a writer waits while the record's lock is held, then writes; a reader reads at once, lock or not
- a guard refuses by its name, exit 2, the record byte-identical
The package is pinned from its manifest and LEDGERED; its writer and the `_core` it carries are
written at the test's time: the writer reaches the engine through `_core`, its instance by `home`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time

from conductor import Conductor, compiling, discovery, record
from tests.harness import demonstrated, demos, manifests, race, vendor

DRAWER, PATTERN = "packaging", "writer-skill"
DEMOS = ("LEDGERED.md",)
WRITER = '''import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _core import core, home

conductor = core(__file__)
LEDGER = home(__file__) / "ledger.txt"
BUDGET = 80


def refuse(code, reason):
    print(f"pp-ledger: {code} -- {reason}", file=sys.stderr)
    sys.exit(2)


def main(arguments):
    verb, words = (arguments[0] if arguments else ""), arguments[1:]
    if verb == "read":
        print(LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else "", end="")
        return 0
    if verb != "add":
        refuse("verb-unknown", "add <entry> | read")
    entry = " ".join(words).strip()
    if not entry:
        refuse("entry-empty", "an entry says something")
    if len(entry) > BUDGET:
        refuse("entry-budget", f"{len(entry)} characters, {BUDGET} at most")
    with conductor.record.held(LEDGER):
        lines = LEDGER.read_text(encoding="utf-8").splitlines() if LEDGER.exists() else []
        time.sleep(0.05)
        conductor.record.replace(LEDGER, "\\n".join([*lines, entry]) + "\\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''
WRITERS = 8


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("writer-skill")
    vendor(env.made, "ledger", manifests(DRAWER, PATTERN)["ledger.yaml"],
           {"LEDGERED": (demos(DRAWER, PATTERN) / "LEDGERED.md").read_text(encoding="utf-8")},
           {"pp-ledger": WRITER})
    package = env.made / ".sys" / "vendor" / "ledger@0.0.1"
    shutil.copy(next((bench.source() / "packages").glob("*/skills/_core.py")), package / "skills" / "_core.py")
    compiling.build_tools(env.made)
    member = discovery.instance_member(env.engine)
    ledger = env.made / "ledger.txt"

    def opened():
        opener = Conductor(member, env.engine)
        return opener.start(package / "procs" / "LEDGERED.md"), opener.run_id

    first, key = opened()
    offered = [one.name for one in first.tools] if first is not None else []
    if "pp-ledger" in offered:
        held("the writer is offered", "LEDGERED's step names pp-ledger among its offers")
    else:
        failures.append(f"  ✗ the offer                   {offered}")

    keys = [opened()[1] for _ in range(WRITERS)]
    done = race(env.engine, [[one, "-s", "pp-ledger", "add", f"entry-{n}"] for n, one in enumerate(keys)],
                cwd=env.root)
    lines = ledger.read_text(encoding="utf-8").splitlines() if ledger.exists() else []
    if (all(one.returncode == 0 for one in done) and len(lines) == WRITERS
            and sorted(lines) == sorted(f"entry-{n}" for n in range(WRITERS))):
        held("writers started together lose nothing", f"{WRITERS} runs wrote at once: {WRITERS} entries, "
             "each whole")
    else:
        failures.append(f"  ✗ concurrent writers          rc={[one.returncode for one in done]} {lines} "
                        f"{[one.stderr[-120:] for one in done if one.returncode]}")

    before = ledger.read_bytes()
    with record.held(ledger):
        waiting = subprocess.Popen([sys.executable, str(env.engine), key, "-s", "pp-ledger", "add", "late"],
                                   cwd=env.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        started = time.monotonic()
        reader = subprocess.run([sys.executable, str(env.engine), keys[0], "-s", "pp-ledger", "read"], cwd=env.root,
                                capture_output=True, text=True, timeout=30)
        read_in = time.monotonic() - started
        time.sleep(1.0)
        still = waiting.poll() is None and ledger.read_bytes() == before
    waiting.communicate(timeout=30)
    after = ledger.read_text(encoding="utf-8").splitlines()
    if (still and reader.returncode == 0 and reader.stdout.splitlines() == lines and read_in < 10
            and waiting.returncode == 0 and after == [*lines, "late"]):
        held("the lock holds the writer, never the reader", "under a held lock the writer waited and the "
             "record stood still; the reader read it at once; released, the entry landed last")
    else:
        failures.append(f"  ✗ the lock                    still={still} reader={reader.returncode} "
                        f"waiting={waiting.returncode} {after[-2:]}")

    before = ledger.read_bytes()
    empty = env.cli(key, "-s", "pp-ledger", "add")
    long = env.cli(key, "-s", "pp-ledger", "add", "x" * 81)
    if (empty.returncode == 2 and "entry-empty" in empty.stderr and long.returncode == 2
            and "entry-budget" in long.stderr and ledger.read_bytes() == before):
        held("a guard refuses by its name", "an empty entry and an entry past its budget exit 2 by their "
             "codes, the record byte-identical")
    else:
        failures.append(f"  ✗ the guards                  {empty.returncode} {empty.stderr[-120:]!r} "
                        f"{long.returncode} {long.stderr[-120:]!r}")
    return 0
