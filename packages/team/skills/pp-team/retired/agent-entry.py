#!/usr/bin/env python3
"""team-entry -- the decider of the team documents of an agent's instance (`procs/TEAM-<team>.md`):
prints the document the wake-up under way plays next, as the house's `team entry <team> --run <key>`
says it. The engine plays it at the exit of such a document, with `PP_RUN` (the run's key) and
`PP_HOME` (the agent's instance); the house is the first instance above the agent that carries the
machine the agent borrows. Nothing is written."""
import os
import subprocess
import sys
from pathlib import Path

ENGINE = (".sys", "engine", "pp.py")             # where an instance carries its machine's console
OWN = ("PP_HOME", "PP_CALL", "PP_RUN")           # the agent's run: the house's console serves another instance


def main(argv: list[str]) -> int:
    run, home = os.environ.get("PP_RUN", ""), os.environ.get("PP_HOME", "")
    if len(argv) != 1 or not run or not home:
        sys.stderr.write("team-entry: usage: team-entry <team> -- played by the engine under PP_RUN and PP_HOME\n")
        return 2
    meta = Path(home)
    house = next((above / meta.name for above in meta.parent.parents
                  if (above / meta.name).joinpath(*ENGINE).is_file()), None)
    if house is None:
        sys.stderr.write(f"team-entry: no house above {meta} -- no instance there carries the machine\n")
        return 2
    env = {key: value for key, value in os.environ.items() if key not in OWN}
    done = subprocess.run([sys.executable, str(house.joinpath(*ENGINE)), "--instance", str(house),
                           "team", "entry", argv[0], "--run", run], capture_output=True, text=True, env=env)
    sys.stdout.write(done.stdout)
    sys.stderr.write(done.stderr)
    return done.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
