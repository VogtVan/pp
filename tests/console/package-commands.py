"""Scenario `package-commands` -- a package's console verbs, captured and at the terminal:
- the captured verb: it resolves after the console's verbs, its skill run with the manifest's args
  then the operator's, its output relayed, its exit code returned; the bus harvests what it
  pushes; a mount has no run at the console and refuses; its stderr reaches the caller as it is
  written, before the skill ends
- `help` lists the packages' verbs after the console's own, in declaration order, each with its
  package and its skill's description
- the strangers: an undeclared verb answers the usage, a withdrawn verb is a stranger like any
  other, a declared command whose script is gone refuses `command-broken`
- the verb declared `tty: true`: the skill owns the console's three streams -- stdin read, stdout
  raw (directives included), its exit code returned as is; nothing of it is harvested, a
  `::mount` it prints is not judged; the same script without `tty` keeps the captured contract
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
import time

import yaml

from conductor import contributions, events, instance, metadata
from tests.harness import cli

WITNESS = """name: witness
version: 0.0.1
description: a package whose verbs run captured and at the terminal
requires: []
contributes:
  commands:
    - {verb: witness, skill: pp-witness, args: [from-manifest]}
    - {verb: grumble, skill: pp-grumble}
    - {verb: climb, skill: pp-climb}
    - {verb: slow, skill: pp-slow}
    - {verb: screen, skill: pp-screen, tty: true}
    - {verb: screen-captured, skill: pp-screen}
    - {verb: screen-wait, skill: pp-screen-wait, tty: true}
    - {verb: screen-relaunch, skill: pp-screen-relaunch, tty: true}
  events:
    vectors:
      project: {verify: pp-project}
      screen: {verify: pp-screen-verify}
    signals:
      witness-due: {priority: 3, standing: true}
      screen-due: {priority: 3, standing: true}
"""
MANIFEST = yaml.safe_load(WITNESS)
NAME = MANIFEST["name"]
COMMANDS = MANIFEST["contributes"]["commands"]

SKILLS = {
    "pp-witness": ("the witness skill -- prints what it is given",
                   "import sys\nprint('witness:', *sys.argv[1:])\n"
                   "print('::push witness-due project:witness the witness spoke')\n"),
    "pp-grumble": ("a skill that refuses, loudly",
                   "import sys\nprint('grumble: before the refusal')\n"
                   "sys.stderr.write('grumble: REFUSED -- by design\\n')\nsys.exit(3)\n"),
    "pp-climb": ("a skill that asks for a mount it cannot get at the console",
                 "print('climb: up')\nprint('::mount []')\n"),
    "pp-slow": ("a skill that speaks on stderr, then works a while",
                "import sys, time\nsys.stderr.write('slow: started\\n')\nsys.stderr.flush()\n"
                "time.sleep(1)\nprint('slow: done')\n"),
    "pp-project": ("the witness verifier -- every slug is a node",
                   "import sys\nsys.stdin.read()\nsys.exit(0)\n"),
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
    "pp-screen-verify": ("the screen verifier -- every slug is a node",
                         "import sys\nsys.stdin.read()\nsys.exit(0)\n"),
}

RAW = ["screen: read hello", "::push screen-due screen:x the screen spoke", "::mount []"]
VERB = re.compile(r"^  \./pp (\S+)", re.M)                       # a verb's line in the help
PACKAGED = re.compile(r"^  \./pp (\S+)\s+\((\S+)\) (.*)$", re.M)  # verb, package, description


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


def _captured(bench, made, engine) -> None:
    """The captured verbs: the run, the push, the help, the refusals relayed, the live stderr."""
    held, failures = bench.held, bench.failures
    # --- the verb runs its skill: manifest args first, the operator's after --------
    played = cli(engine, "witness", "a", "b")
    if (played.returncode == 0 and played.stdout.strip() == "witness: from-manifest a b"
            and "::push" not in played.stdout and not played.stderr):
        held("a command runs its skill", "`pp witness a b` -> the script's line with the "
             "manifest's args first; the directive never reaches the screen")
    else:
        failures.append(f"  ✗ command played               rc={played.returncode} "
                        f"{played.stdout!r} {played.stderr[:80]!r}")
    standing = events.standing_entries(made)
    if any("the witness spoke" in str(one) for one in standing):
        held("the bus harvests the push", "`::push` stood by the one collector on rc 0")
    else:
        failures.append(f"  ✗ push harvested               {standing!r}")

    # --- help composes: the console's verbs, then the package's, as declared --------
    helped = cli(engine, "help")
    text = helped.stdout
    verbs = VERB.findall(text)
    own = verbs[:len(verbs) - len(COMMANDS)]
    expected = [(str(one["verb"]), NAME, SKILLS[str(one["skill"])][0]) for one in COMMANDS]
    if (helped.returncode == 0 and {"help", "doctor"} <= set(own)
            and PACKAGED.findall(text) == expected
            and verbs[len(own):] == [verb for verb, _, _ in expected]
            and "admin" not in verbs):
        held("help is composed", f"the console's {len(own)} verbs, then the package's "
             f"{len(expected)} in declaration order, each with its package and its skill's "
             "description")
    else:
        failures.append(f"  ✗ help composed                {verbs!r} {PACKAGED.findall(text)!r}")

    # --- a skill's refusal is relayed: rc as is, stderr verbatim -------------------
    grumbled = cli(engine, "grumble")
    if (grumbled.returncode == 3 and grumbled.stdout.strip() == "grumble: before the refusal"
            and "grumble: REFUSED -- by design" in grumbled.stderr):
        held("a refusing skill is relayed", "rc 3 returned as is, stdout and stderr verbatim")
    else:
        failures.append(f"  ✗ grumble relayed              rc={grumbled.returncode} {grumbled.stderr[:80]!r}")

    # --- a mount has no run at the console ------------------------------------------
    climbed = cli(engine, "climb")
    if (climbed.returncode == 2 and "mount-without-run" in climbed.stderr
            and climbed.stdout.strip() == "climb: up"):
        held("a mount refuses at the console", "the skill ran, its lines relayed, "
             "`mount-without-run` said -- rc 2")
    else:
        failures.append(f"  ✗ mount refused                rc={climbed.returncode} {climbed.stderr[:80]!r}")

    # --- a verb no package declares is a stranger like any other -------------------
    gone = cli(engine, "admin")
    nowhere = cli(engine, "nothere")
    if (gone.returncode != 0 and "The KEY leads" in gone.stderr
            and nowhere.returncode != 0 and "The KEY leads" in nowhere.stderr):
        held("a withdrawn verb is a stranger", "`admin` left the console with its policy: "
             "undeclared, it answers the usage like `nothere` -- the console keeps no memory of it")
    else:
        failures.append(f"  ✗ admin/stranger               {gone.returncode} {nowhere.returncode}")

    # --- a skill's stderr reaches the caller while the skill runs ---------------------
    live = subprocess.Popen([sys.executable, str(engine), "slow"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    first = live.stderr.readline()
    read_at = time.monotonic()
    out, _ = live.communicate(timeout=30)
    ahead = time.monotonic() - read_at        # the skill sleeps 1 s after its stderr line
    if first.strip() == "slow: started" and ahead >= 0.5 and out.strip() == "slow: done" and live.returncode == 0:
        held("stderr is relayed as it is written", f"the skill's stderr line read {ahead:.1f}s before "
             "the console ended; its stdout relayed after, rc 0")
    else:
        failures.append(f"  ✗ stderr live                  first={first!r} ahead={ahead:.2f}s "
                        f"out={out!r} rc={live.returncode}")


def _terminal(bench, made, engine) -> None:
    """The verbs at the terminal: the streams, the code, the Ctrl-C, the relaunch, the captured twin."""
    held, failures = bench.held, bench.failures
    before = events.standing_entries(made)

    # --- a clean exit: the three streams are the skill's, nothing judged ------------
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

    # --- a failing exit: the code as is ---------------------------------------------
    failed = cli(engine, "screen", "3", stdin="hello\n")
    if failed.returncode == 3 and failed.stdout.splitlines() == RAW:
        held("the exit code is the answer", "rc 3 returned as is, the lines still raw")
    else:
        failures.append(f"  ✗ tty rc                       rc={failed.returncode} {failed.stdout!r}")

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

    # --- the same script captured: the captured contract, untouched -----------------
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


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("verbs")
    made, engine = env.made, env.engine

    # --- before any declaration: a bare stranger answers the usage -----------------
    stranger = cli(engine, "witness", "a")
    if stranger.returncode != 0 and "The KEY leads" in stranger.stderr and not stranger.stdout:
        held("undeclared, a verb is a stranger", "the usage answers, rc != 0")
    else:
        failures.append(f"  ✗ stranger before              rc={stranger.returncode} {stranger.stdout[:80]!r}")

    _pin(made)
    _captured(bench, made, engine)
    _terminal(bench, made, engine)

    # --- a declared command whose script is gone refuses by name --------------------
    (made / ".sys" / "vendor" / f"{NAME}@{MANIFEST['version']}" / "skills" / "pp-witness"
     / "pp-witness.py").unlink()
    broken = cli(engine, "witness")
    if broken.returncode == 2 and "command-broken" in broken.stderr and not broken.stdout:
        held("a broken command refuses", "`command-broken` names the verb and the skill, rc 2")
    else:
        failures.append(f"  ✗ command broken               rc={broken.returncode} {broken.stderr[:100]!r}")
    return 0
