"""Scenario `package-commands` -- what the console does with the PROCESS of a package's verb at the
terminal; what a package declares and gets from a verb is the pattern `automation/commands`:
- the Ctrl-C at the terminal is the skill's: a SIGINT to the whole group is handled by the skill
  alone (`interrupted`, rc 130, no traceback); a SIGINT to the console alone leaves the skill to
  end on its own terms (`done`, rc 0)
- `RELAUNCH`: a skill that ends on it after writing `then: doctor` in its package's space of the
  metadata -- the console, its hold on the machine left, plays `doctor`, then the same command
  again, told `PP_RELAUNCHED=doctor <its exit code>` (the hand-pinned witness makes this house's
  doctor refuse: its code is told as it is); `then: remove` refuses `relaunch-invalid`, nothing
  played after; a console already played again gives the code back as is -- never a loop
"""
from __future__ import annotations

import os
import re
import signal
import subprocess
import sys

import yaml

from conductor import contributions, instance, metadata
from tests.harness import cli

WITNESS = """name: witness
version: 0.0.1
description: a package whose verbs wait at the terminal and ask the console to play again
requires: []
contributes:
  commands:
    - {verb: screen-wait, skill: pp-screen-wait, tty: true}
    - {verb: screen-relaunch, skill: pp-screen-relaunch, tty: true}
"""
MANIFEST = yaml.safe_load(WITNESS)
NAME = MANIFEST["name"]
COMMANDS = MANIFEST["contributes"]["commands"]

SKILLS = {
    "pp-screen-wait": ("a skill that waits at the terminal and handles its own Ctrl-C",
                       "import signal, sys, time\n"
                       "def bye(*_):\n    print('screen: interrupted')\n    sys.stdout.flush()\n    sys.exit(130)\n"
                       "signal.signal(signal.SIGINT, bye)\n"
                       "sys.stderr.write('screen: waiting\\n')\nsys.stderr.flush()\n"
                       "time.sleep(1)\nprint('screen: done')\n"),
    "pp-screen-relaunch": ("a skill that asks the console for a maintenance verb at its first launch",
                           "import json, os, sys\n"
                           "verb, counter, record, code = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])\n"
                           "n = int(open(counter).read()) + 1 if os.path.exists(counter) else 1\n"
                           "open(counter, 'w').write(str(n))\n"
                           "if n == 1:\n"
                           "    kept = json.load(open(record)) if os.path.exists(record) else {}\n"
                           f"    kept[{NAME!r}] = {{'then': verb}}\n"
                           "    os.makedirs(os.path.dirname(record), exist_ok=True)\n"
                           "    json.dump(kept, open(record, 'w'))\n"
                           "    sys.exit(code)\n"
                           "print('screen: relaunched', os.environ.get('PP_RELAUNCHED', ''))\n"),
}



def _pin(made) -> None:
    """The witness package pinned by hand: its manifest and its skills vendored, its pin written."""
    root = made / ".sys" / "vendor" / f"{NAME}@{MANIFEST['version']}"
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    for name, (said, code) in SKILLS.items():
        home = root / "skills" / name
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {said}\n---\n\n"
                                       "run it.\n", encoding="utf-8")
        (home / f"{name}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][NAME] = MANIFEST["version"]
    instance.write(made, pins)


def _terminal(bench, made, engine) -> None:
    """The verbs at the terminal: the Ctrl-C, the relaunch."""
    held, failures = bench.held, bench.failures
    # --- the Ctrl-C is the skill's: the group's SIGINT, as at a terminal ------------
    def waiting(*flags: str) -> subprocess.Popen:
        """The console on `screen-wait`, in a session of its own: the group a terminal would signal."""
        live = subprocess.Popen([sys.executable, str(engine), *flags], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, start_new_session=True)
        assert live.stderr is not None
        live.stderr.readline()                     # `screen: waiting`: the skill is up
        return live

    live = waiting("screen-wait")
    os.killpg(live.pid, signal.SIGINT)             # the console AND the skill, as a terminal does
    out, err = live.communicate(timeout=30)
    if (live.returncode == 130 and out.strip() == "screen: interrupted"
            and "Traceback" not in err and "KeyboardInterrupt" not in err):
        held("the group's SIGINT is the skill's", "the skill handled it (`interrupted`), its rc 130 "
             "returned as is, the console said nothing")
    else:
        failures.append(f"  ✗ group SIGINT                 rc={live.returncode} {out!r} {err[-200:]!r}")

    # --- a SIGINT to the console alone: the skill ends on its own terms -------------
    live = waiting("screen-wait")
    os.kill(live.pid, signal.SIGINT)               # the console alone
    out, err = live.communicate(timeout=30)
    if live.returncode == 0 and out.strip() == "screen: done" and "Traceback" not in err:
        held("a SIGINT to the console alone spares the skill", "the console waited, the skill "
             "finished on its own (`done`), rc 0")
    else:
        failures.append(f"  ✗ console SIGINT               rc={live.returncode} {out!r} {err[-200:]!r}")

    # --- RELAUNCH: the console leaves its hold, plays the verb asked, plays the command again --
    record = metadata.path_of(made)
    code = str(getattr(contributions, "RELAUNCH", 75))
    counter = bench.temp() / "relaunch.count"
    relaunched = cli(engine, "screen-relaunch", "doctor", str(counter), str(record), code)
    launches = int(counter.read_text()) if counter.is_file() else 0
    refused_count = bench.temp() / "refused.count"
    refused = cli(engine, "screen-relaunch", "remove", str(refused_count), str(record), code)
    refused_launches = int(refused_count.read_text()) if refused_count.is_file() else 0
    once_count = bench.temp() / "once.count"
    once = cli(engine, "screen-relaunch", "doctor", str(once_count), str(record), code,
               env={"PP_RELAUNCHED": "doctor 0"})
    once_launches = int(once_count.read_text()) if once_count.is_file() else 0
    told = re.search(r"screen: relaunched doctor (\d+)", relaunched.stdout)
    if (relaunched.returncode == 0 and launches == 2 and told
            and ("pp: " in relaunched.stderr) == (told.group(1) != "0")
            and refused.returncode == 2 and "relaunch-invalid" in refused.stderr and refused_launches == 1
            and once.returncode == int(code) and once_launches == 1):
        held("RELAUNCH plays the verb asked, then the command again", f"then: doctor -- doctor played out of the "
             f"console's hold, the skill launched twice and told `doctor {told.group(1)}` (doctor's own code); "
             "then: remove refused relaunch-invalid, launched once; a console already played again gives "
             f"{code} back, launched once -- never a loop")
    else:
        failures.append(f"  ✗ relaunch                     rc={relaunched.returncode}/{refused.returncode} "
                        f"launches={launches}/{refused_launches}/{once_launches} once_rc={once.returncode} "
                        f"{relaunched.stdout[-300:]!r} "
                        f"{relaunched.stderr[-300:]!r} {refused.stderr[-200:]!r}")



def scenario(bench) -> int:
    env = bench.env("verbs")
    _pin(env.made)
    _terminal(bench, env.made, env.engine)
    return 0
