"""Scenario `skill-loading` -- 2 case(s):
- a script skill that declares a dataclass under postponed annotations plays as a gesture
  through the console, exactly as it runs by hand
- the bench loader gives two homonymous scripts two names in `sys.modules`, each able to
  declare its own dataclass
"""
from __future__ import annotations

import sys

from tests.harness import load_script

DATED = '''from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stamp:
    day: str


def main(argv):
    print(f"dated: {Stamp(day='2026-09-13').day}")
    return 0
'''

WIRE = '''from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Host:
    name: str


HOST = Host(name={name!r})
'''


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- a dataclass skill plays through the console --------------------------------------
    env = bench.env("loading")
    home = env.made / "skills" / "dated"
    home.mkdir(parents=True)
    (home / "SKILL.md").write_text(
        "---\nname: dated\ndescription: a stamp carried by a dataclass\n---\nrun it.\n",
        encoding="utf-8")
    (home / "dated.py").write_text(DATED, encoding="utf-8")
    (env.made / "procs" / "CAPABILITIES.md").write_text(
        "---\nname: CAPABILITIES\ntools: |\n  +dated\n---\n", encoding="utf-8")
    opened = env.cli("-new")
    played = env.cli("-s", "dated", "now")
    if (opened.returncode == 0 and played.returncode == 0
            and "dated: 2026-09-13" in played.stdout and "Traceback" not in played.stderr):
        held("a dataclass skill plays as a gesture",
             "`./pp -s dated` runs the script in the console's process: its dataclass "
             "resolves its module, the skill prints what it prints by hand")
    else:
        failures.append(f"  ✗ dataclass gesture          rc={played.returncode} "
                        f"{(played.stderr or played.stdout).strip().splitlines()[-1:]!r}")

    # --- two homonymous scripts, two modules ---------------------------------------------
    loaded = []
    for name in ("claude", "codex"):
        spot = bench.temp() / "adapters" / name
        spot.mkdir(parents=True)
        (spot / "wire.py").write_text(WIRE.format(name=name), encoding="utf-8")
        loaded.append(load_script(spot / "wire.py"))
    names = [module.__name__ for module in loaded]
    if (len(set(names)) == 2 and all(sys.modules.get(one) is module
                                     for one, module in zip(names, loaded))
            and [module.HOST.name for module in loaded] == ["claude", "codex"]):
        held("homonymous scripts keep their own modules",
             f"two `wire.py` load as {names[0]} and {names[1]}, each registered in "
             "`sys.modules`, each with its own dataclass")
    else:
        failures.append(f"  ✗ homonymous scripts         {names!r}")
    return 0
