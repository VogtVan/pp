"""Scenario `command-at-terminal` -- a package's console verb declared `tty: true`
(plan ui, batch l-entree-au-terminal):
- the skill owns the console's three streams: it reads stdin, its stdout reaches the caller raw (directives included), its exit code is returned as is
- nothing of it is harvested: the bus stands as before the call, a `::mount` it prints is not judged
- the same script without `tty` keeps the captured contract: the push harvested, the directives hidden, `mount-without-run` refused
- the Ctrl-C is the skill's (the rework of 2026-10-07): a SIGINT to the whole group -- the console and the skill, as at a terminal -- is handled by the skill alone (`interrupted`, its rc 130 returned, no traceback); a SIGINT to the console alone leaves the skill to end on its own terms (`done`, rc 0)
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys

from conductor import events, instance
from tests.harness import cli

WITNESS = """name: screen
version: 0.0.1
description: a package whose verb draws on the terminal
requires: []
contributes:
  commands:
    - {verb: screen, skill: pp-screen, tty: true}
    - {verb: screen-captured, skill: pp-screen}
    - {verb: screen-wait, skill: pp-screen-wait, tty: true}
  events:
    vectors:
      screen: {verify: pp-screen-verify}
    signals:
      screen-due: {priority: 3, standing: true}
"""

SKILLS = {
    "pp-screen": ("a skill that reads its stdin, speaks on both streams and exits as told",
                  "import sys\n"
                  "line = sys.stdin.readline().rstrip('\\n')\n"
                  "print('screen: read', line)\n"
                  "print('::push screen-due screen:x the screen spoke')\n"
                  "print('::mount []')\n"
                  "sys.stderr.write('screen: on stderr\\n')\n"
                  "sys.exit(int(sys.argv[1]) if len(sys.argv) > 1 else 0)\n"),
    "pp-screen-wait": ("a skill that waits at the terminal and handles its own Ctrl-C",
                       "import signal, sys, time\n"
                       "def bye(*_):\n    print('screen: interrupted')\n    sys.stdout.flush()\n    sys.exit(130)\n"
                       "signal.signal(signal.SIGINT, bye)\n"
                       "sys.stderr.write('screen: waiting\\n')\nsys.stderr.flush()\n"
                       "time.sleep(2)\nprint('screen: done')\n"),
    "pp-screen-verify": ("the screen verifier -- every slug is a node",
                         "import sys\nsys.stdin.read()\nsys.exit(0)\n"),
}

RAW = ["screen: read hello", "::push screen-due screen:x the screen spoke", "::mount []"]


def _pin(made) -> None:
    root = made / ".sys" / "vendor" / "screen@0.0.1"
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    for name, (said, code) in SKILLS.items():
        home = root / "skills" / name
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {said}\n---\n\n"
                                       "run it.\n", encoding="utf-8")
        (home / f"{name}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["screen"] = "0.0.1"
    instance.write(made, pins)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("terminal")
    made, engine = env.made, env.engine
    _pin(made)
    before = events.standing_entries(made)

    # --- at the terminal, a clean exit: the three streams are the skill's, nothing judged --
    drawn = cli(engine, "screen", stdin="hello\n")
    if (drawn.returncode == 0 and drawn.stdout.splitlines() == RAW
            and drawn.stderr == "screen: on stderr\n"):
        held("the skill owns the three streams", "stdin read (`hello`), stdout raw -- the "
             "`::push` and the `::mount` lines reach the caller as written --, stderr as is, rc 0: "
             "no `mount-without-run`")
    else:
        failures.append(f"  ✗ tty streams                  rc={drawn.returncode} "
                        f"{drawn.stdout!r} {drawn.stderr[:120]!r}")
    if events.standing_entries(made) == before:
        held("nothing is harvested", "the bus stands as before the call: a skill at the "
             "terminal never speaks to it")
    else:
        failures.append(f"  ✗ tty harvested                {events.standing_entries(made)!r}")

    # --- at the terminal, a failing exit: the code as is -----------------------------------
    failed = cli(engine, "screen", "3", stdin="hello\n")
    if failed.returncode == 3 and failed.stdout.splitlines() == RAW:
        held("the exit code is the answer", "rc 3 returned as is, the lines still raw")
    else:
        failures.append(f"  ✗ tty rc                       rc={failed.returncode} {failed.stdout!r}")

    # --- the Ctrl-C is the skill's: the group's SIGINT, as at a terminal ------------------------
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

    # --- a SIGINT to the console alone: the skill ends on its own terms ------------------------
    live = waiting("screen-wait")
    os.kill(live.pid, signal.SIGINT)               # the console alone
    out, err = live.communicate(timeout=30)
    if live.returncode == 0 and out.strip() == "screen: done" and "Traceback" not in err:
        held("a SIGINT to the console alone spares the skill", "the console waited, the skill "
             "finished on its own (`done`), rc 0")
    else:
        failures.append(f"  ✗ console SIGINT               rc={live.returncode} {out!r} {err[-200:]!r}")

    # --- the same script captured: today's contract, untouched -----------------------------
    captured = cli(engine, "screen-captured", stdin="hello\n")
    standing = events.standing_entries(made)
    if (captured.returncode == 2 and captured.stdout.splitlines() == ["screen: read hello"]
            and "mount-without-run" in captured.stderr
            and any("the screen spoke" in str(one) for one in standing)):
        held("the captured twin keeps its contract", "the directives hidden, the push "
             "harvested, `mount-without-run` said -- rc 2")
    else:
        failures.append(f"  ✗ captured twin                rc={captured.returncode} "
                        f"{captured.stdout!r} {captured.stderr[:120]!r} {standing!r}")
    return 0
