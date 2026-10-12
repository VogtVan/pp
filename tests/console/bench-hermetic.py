"""Scenario `bench-hermetic` -- 1 case(s):
- le-banc-hermetique: the session's pp variables never reach a throwaway instance
"""
from __future__ import annotations

import os
import subprocess
import sys

from tests.harness import hermetic

SEEN = "import os;print(sorted(k for k in os.environ if k.startswith('PP_')))"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- le-banc-hermetique: a wired session lends the bench nothing --------------
    os.environ["PP_MARBLE"] = "1"                 # a scenario owns its process: what it
    os.environ["PP_RUN"] = "zzzzzz"               # poses here reaches its children alone
    dropped = hermetic()
    left = sorted(name for name in os.environ if name.startswith("PP_"))
    inherited = subprocess.run([sys.executable, "-c", SEEN], capture_output=True, text=True)
    if dropped == ["PP_MARBLE", "PP_RUN"] and not left and inherited.stdout.strip() == "[]":
        held("the session lends the bench nothing", "PP_MARBLE and PP_RUN named as dropped, "
             "none left in the environment, and a child process sees none either -- one site "
             "at the entry covers every launcher")
    else:
        failures.append(f"  ✗ the bench is hermetic       {dropped!r} {left!r} "
                        f"{inherited.stdout.strip()!r}")

    if hermetic() == []:
        held("nothing to drop says nothing", "a second call finds no pp variable and "
             "renders an empty list -- the line that names them keeps quiet")
    else:
        failures.append("  ✗ the drop is idempotent      a second call still found pp variables")
    return 0
