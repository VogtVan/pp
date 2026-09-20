"""Scenario `threads-before-next` -- the threads are kept before the surface renders them
(plan steering, phase le-proc-next, batch le-texte-du-next):
- THREADS opens at the turn's end as a WORK step that offers the keeper, and NEXT is not in
  its output: the section break holds the surface back
- a step delivered during the THREADS step reaches the table NEXT serves in the next output
- NEXT declares no tool of its own (the offers of the frames above it still reach its segment:
  refusing a gesture under an INFER is the engine's, plan core)
Every turn is played by the CONSOLE; the write by the vendored keeper, in a subprocess.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _keeper_script(meta: Path) -> Path:
    return next((meta / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"


def _console(meta: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run([str(meta.parent / "pp"), *args], input=stdin, capture_output=True, text=True,
                          cwd=str(meta.parent))
    return done.stdout + done.stderr


def _keeper(meta: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run([sys.executable, str(_keeper_script(meta)), *args], input=stdin, capture_output=True,
                          text=True, cwd=str(meta.parent))
    return done.stdout + done.stderr


def _advance(meta: Path, key: str, last: str) -> str:
    """-> the next output: a proof answered n/a, anything else a bare call."""
    judged = re.search(r"INFER proof \[([^\]]*)\]", last)
    if judged:
        codes = judged.group(1).split() or ["none"]
        return _console(meta, key, "-", stdin=json.dumps(
            [{"code": c, "evidence": "bench", "verdict": "n/a"} for c in codes]))
    return _console(meta, key)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("tbn", packages=("steering",))
    meta = env.made
    _keeper(meta, "open", "le-fil-tenu", stdin="le-premier-pas | the first step\nle-second-pas | the second step\n")
    record = json.loads((meta / ".sys" / "records" / "threads.json").read_text(encoding="utf-8"))
    tid, thread = next(iter(record["threads"].items()))

    output = _console(meta, "-new")
    key = output.split("run ", 1)[1].split()[0]
    threads_output = ""
    for _ in range(20):
        if "THREADS{" in output:
            threads_output = output
            break
        output = _advance(meta, key, output)
    if (threads_output and "WORK" in threads_output and "pp-steering" in threads_output
            and "NEXT{" not in threads_output):
        held("THREADS is a WORK step, NEXT waits behind it",
             "the turn's end opens THREADS, which offers the keeper; the surface is not in its output")
    else:
        failures.append(f"  ✗ threads step               {threads_output[-300:]!r}")

    _keeper(meta, "done", tid, thread["steps"][0])                 # the induced work, under THREADS
    next_output = ""
    output = _console(meta, key)
    for _ in range(10):
        if "NEXT{" in output:
            next_output = output
            break
        output = _advance(meta, key, output)
    row = next((line for line in next_output.splitlines() if line.startswith("| le-fil-tenu |")), "")
    if "1/2" in row and "`le-second-pas`" in row and "THREADS{" not in next_output.split("NEXT{", 1)[0][-200:]:
        held("the table NEXT copies is computed after the work",
             "a step delivered under THREADS reads delivered in the next output's table")
    else:
        failures.append(f"  ✗ fresh table                row={row!r}")
    return 0
