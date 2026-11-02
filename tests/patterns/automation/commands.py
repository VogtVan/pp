"""Scenario `commands` -- the pattern `automation/commands`, played from its demonstration:
- undeclared, a verb is a stranger; declared, it resolves after the console's verbs, its skill run
  with the manifest's args then the operator's, its output relayed, its exit code returned; the
  bus harvests what it pushes; a mount has no run at the console; its stderr reaches the caller
  as it is written; `help` lists the package's verbs after the console's own; a withdrawn verb is
  a stranger, a command whose script is gone refuses `command-broken`
- the verb declared `tty: true`: the skill owns the three streams, nothing is harvested, its exit
  code is the answer; the same script without `tty` keeps the captured contract; the catalog says
  `tty=True`
- at the build: a verb the console owns refuses `command-taken`, a verb shaped like a run's key
  and a `tty` neither true nor false `contribution-malformed`, a skill nobody carries
  `command-skill-unknown`, a verb without the package's name `name-unprefixed`; the package's name
  alone and a prefixed verb pass
The skills are written at the test's time.
"""
from __future__ import annotations

import re
import subprocess
import sys
import time

import yaml

from conductor import compiling, events
from tests.harness import cli, manifests, vendor

DRAWER, PATTERN = "automation", "commands"
MANIFESTS = ("keylike.yaml", "skillless.yaml", "taken.yaml", "ttyless.yaml", "unprefixed.yaml", "witness.yaml")
SKILLS = {
    "pp-witness": "import sys\nprint('witness:', *sys.argv[1:])\n"
                  "print('::push witness-due witness-project:witness the witness spoke')\n",
    "pp-witness-grumble": "import sys\nprint('grumble: before the refusal')\n"
                          "sys.stderr.write('grumble: REFUSED -- by design\\n')\nsys.exit(3)\n",
    "pp-witness-climb": "print('climb: up')\nprint('::mount []')\n",
    "pp-witness-slow": "import sys, time\nsys.stderr.write('slow: started\\n')\nsys.stderr.flush()\n"
                       "time.sleep(1)\nprint('slow: done')\n",
    "pp-witness-project": "import sys\nsys.stdin.read()\nsys.exit(0)\n",
    "pp-witness-screen": "import sys\nline = sys.stdin.readline().rstrip('\\n')\nprint('screen: read', line)\n"
                         "print('::push witness-screen-due witness-project:x the screen spoke')\n"
                         "print('::mount []')\nsys.stderr.write('screen: on stderr\\n')\n"
                         "sys.exit(int(sys.argv[1]) if len(sys.argv) > 1 else 0)\n",
}
RAW = ["screen: read hello", "::push witness-screen-due witness-project:x the screen spoke", "::mount []"]
VERB = re.compile(r"^  \./pp (\S+)", re.M)                       # a verb's line in the help
PACKAGED = re.compile(r"^  \./pp (\S+)\s+\((\S+)\) (.*)$", re.M)  # verb, package, description
ENTRY = re.compile(r"^- \*\*`([^`]+)`\*\* (\w+): (.*)$", re.M)    # a contribution's line in the catalog


def _fields(said: str) -> dict[str, str]:
    return dict(part.split("=", 1) for part in said.split(", "))


def captured(bench, made, engine, commands) -> None:
    """The captured verbs: the run, the push, the help, the refusals relayed, the live stderr."""
    held, failures = bench.held, bench.failures
    played = cli(engine, "witness", "a", "b")
    if (played.returncode == 0 and played.stdout.strip() == "witness: from-manifest a b"
            and "::push" not in played.stdout and not played.stderr):
        held("a command runs its skill", "`pp witness a b` -> the script's line with the manifest's args "
             "first; the directive never reaches the screen")
    else:
        failures.append(f"  ✗ command played               rc={played.returncode} {played.stdout!r} {played.stderr[:80]!r}")
    if any("the witness spoke" in str(one) for one in events.standing_entries(made)):
        held("the bus harvests the push", "`::push` stood by the one collector on rc 0")
    else:
        failures.append(f"  ✗ push harvested               {events.standing_entries(made)!r}")

    text = cli(engine, "help").stdout
    verbs = VERB.findall(text)
    own = verbs[:len(verbs) - len(commands)]
    expected = [(str(one["verb"]), "witness", "a witness") for one in commands]
    if ({"help", "doctor"} <= set(own) and PACKAGED.findall(text) == expected
            and verbs[len(own):] == [verb for verb, _, _ in expected]):
        held("help is composed", f"the console's {len(own)} verbs, then the package's {len(expected)} in "
             "declaration order, each with its package and its skill's description")
    else:
        failures.append(f"  ✗ help composed                {verbs!r} {PACKAGED.findall(text)!r}")

    grumbled = cli(engine, "witness-grumble")
    if (grumbled.returncode == 3 and grumbled.stdout.strip() == "grumble: before the refusal"
            and "grumble: REFUSED -- by design" in grumbled.stderr):
        held("a refusing skill is relayed", "rc 3 returned as is, stdout and stderr verbatim")
    else:
        failures.append(f"  ✗ grumble relayed              rc={grumbled.returncode} {grumbled.stderr[:80]!r}")

    climbed = cli(engine, "witness-climb")
    if climbed.returncode == 2 and "mount-without-run" in climbed.stderr and climbed.stdout.strip() == "climb: up":
        held("a mount refuses at the console", "the skill ran, its lines relayed, `mount-without-run` -- rc 2")
    else:
        failures.append(f"  ✗ mount refused                rc={climbed.returncode} {climbed.stderr[:80]!r}")

    gone = cli(engine, "admin")
    nowhere = cli(engine, "nothere")
    if (gone.returncode == 2 and "verb-unknown" in gone.stderr and len(gone.stderr.splitlines()) <= 2
            and nowhere.returncode == 2 and "verb-unknown" in nowhere.stderr):
        held("a withdrawn verb is a stranger", "`admin`, undeclared, refuses verb-unknown like `nothere`")
    else:
        failures.append(f"  ✗ admin/stranger               {gone.returncode} {nowhere.returncode}")

    live = subprocess.Popen([sys.executable, str(engine), "witness-slow"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    first = live.stderr.readline()
    read_at = time.monotonic()
    out, _ = live.communicate(timeout=30)
    ahead = time.monotonic() - read_at        # the skill sleeps 1 s after its stderr line
    if first.strip() == "slow: started" and ahead >= 0.5 and out.strip() == "slow: done" and live.returncode == 0:
        held("stderr is relayed as it is written", f"the skill's stderr line read {ahead:.1f}s before the "
             "console ended; its stdout relayed after, rc 0")
    else:
        failures.append(f"  ✗ stderr live                  first={first!r} ahead={ahead:.2f}s out={out!r}")


def terminal(bench, made, engine) -> None:
    """The verb at the terminal: the streams, the code, the captured twin, the catalog's field."""
    held, failures = bench.held, bench.failures
    before = events.standing_entries(made)
    drawn = cli(engine, "witness-screen", stdin="hello\n")
    if drawn.returncode == 0 and drawn.stdout.splitlines() == RAW and drawn.stderr == "screen: on stderr\n":
        held("the skill owns the three streams", "stdin read, stdout raw -- the `::push` and `::mount` lines "
             "reach the caller as written --, stderr as is, rc 0")
    else:
        failures.append(f"  ✗ tty streams                  rc={drawn.returncode} {drawn.stdout!r} {drawn.stderr[:120]!r}")
    if events.standing_entries(made) == before:
        held("nothing is harvested", "the bus stands as before: a skill at the terminal never speaks to it")
    else:
        failures.append(f"  ✗ tty harvested                {events.standing_entries(made)!r}")
    failed = cli(engine, "witness-screen", "3", stdin="hello\n")
    if failed.returncode == 3 and failed.stdout.splitlines() == RAW:
        held("the exit code is the answer", "rc 3 returned as is, the lines still raw")
    else:
        failures.append(f"  ✗ tty rc                       rc={failed.returncode} {failed.stdout!r}")
    twin = cli(engine, "witness-captured", stdin="hello\n")
    if (twin.returncode == 2 and twin.stdout.splitlines() == ["screen: read hello"]
            and "mount-without-run" in twin.stderr
            and any("the screen spoke" in str(one) for one in events.standing_entries(made))):
        held("the captured twin keeps its contract", "the directives hidden, the push harvested, "
             "`mount-without-run` said -- rc 2")
    else:
        failures.append(f"  ✗ captured twin                rc={twin.returncode} {twin.stdout!r} {twin.stderr[:120]!r}")
    said = [_fields(line) for package, kind, line in ENTRY.findall(compiling.render_tools(made))
            if (package, kind) == ("witness", "commands")]
    screen = next((one for one in said if one.get("verb") == "witness-screen"), {})
    if screen.get("tty") == "True" and all("tty" not in one for one in said if one is not screen):
        held("`tty: true` is a field of commands", "accepted at the build, the catalog says `tty=True` on "
             "the entry's line, the captured verbs carry none")
    else:
        failures.append(f"  ✗ tty in the catalog           {said}")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    declared = manifests(DRAWER, PATTERN)
    if sorted(declared) != sorted(MANIFESTS):
        failures.append(f"  ✗ the demonstration           {sorted(declared)!r} -- owed {sorted(MANIFESTS)!r}")
        return 0
    env = bench.env("verbs")
    made, engine = env.made, env.engine
    stranger = cli(engine, "witness", "a")
    if stranger.returncode == 2 and "verb-unknown" in stranger.stderr and not stranger.stdout:
        held("undeclared, a verb is a stranger", "verb-unknown in one line, rc 2")
    else:
        failures.append(f"  ✗ stranger before              rc={stranger.returncode} {stranger.stdout[:80]!r}")
    vendor(made, "witness", declared["witness.yaml"], {}, SKILLS)
    compiling.build_tools(made)
    held("a prefixed verb and the package's name pass the build", "`witness` and `witness-*`, each skill "
         "`pp-witness[-<name>]`")
    commands = yaml.safe_load(declared["witness.yaml"])["contributes"]["commands"]
    captured(bench, made, engine, commands)
    terminal(bench, made, engine)

    (made / ".sys" / "vendor" / "witness@0.0.1" / "skills" / "pp-witness" / "pp-witness.py").unlink()
    broken = cli(engine, "witness")
    if broken.returncode == 2 and "command-broken" in broken.stderr and not broken.stdout:
        held("a broken command refuses", "`command-broken` names the verb and the skill, rc 2")
    else:
        failures.append(f"  ✗ command broken               rc={broken.returncode} {broken.stderr[:100]!r}")

    def building(manifest: str):
        house = bench.env("commands-build")
        vendor(house.made, "witness", declared[manifest], {}, {"pp-witness": "print('ok')\n"})
        before = (house.made / ".sys" / "tools.md").read_bytes()
        stamps.append((house.made / ".sys" / "tools.md", before))
        return lambda: compiling.build_tools(house.made)

    stamps: list = []
    expect("command-taken", building("taken.yaml"))
    expect("contribution-malformed", building("keylike.yaml"))
    expect("command-skill-unknown", building("skillless.yaml"))
    expect("contribution-malformed", building("ttyless.yaml"))
    expect("name-unprefixed", building("unprefixed.yaml"))
    if all(path.read_bytes() == before for path, before in stamps):
        held("a refused build writes nothing", f"tools.md byte-identical after each of the {len(stamps)} refusals")
    else:
        failures.append("  ✗ refused build wrote          tools.md moved")
    return 0
