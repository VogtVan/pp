"""Scenario `commands` -- a package's console verbs (plan pp-split, batch
les-commandes-des-packages):
- a declared command resolves after the console's verbs: the skill runs with the manifest's args then the operator's, its output relayed, its exit code returned
- `help` lists the commands after the console's own, composed from the declarations
- the bus harvests what the skill pushes; a mount has no run at the console and refuses
- a stranger still answers the usage, a system verb stays the console's, a broken command refuses by name
"""
from __future__ import annotations

from conductor import instance
from tests.harness import cli

WITNESS = """name: witness
version: 0.0.1
description: a package that declares one console verb
requires: []
contributes:
  commands:
    - {verb: witness, skill: pp-witness, args: [from-manifest]}
    - {verb: grumble, skill: pp-grumble}
    - {verb: climb, skill: pp-climb}
  events:
    vectors:
      project: {verify: pp-project}
    signals:
      witness-due: {priority: 3, standing: true}
"""

SKILLS = {
    "pp-witness": ("the witness skill -- prints what it is given",
                   "import sys\nprint('witness:', *sys.argv[1:])\n"
                   "print('::push witness-due project:witness the witness spoke')\n"),
    "pp-grumble": ("a skill that refuses, loudly",
                   "import sys\nprint('grumble: before the refusal')\n"
                   "sys.stderr.write('grumble: REFUSED -- by design\\n')\nsys.exit(3)\n"),
    "pp-climb": ("a skill that asks for a mount it cannot get at the console",
                 "print('climb: up')\nprint('::mount []')\n"),
    "pp-project": ("the witness verifier -- every slug is a node",
                   "import sys\nsys.stdin.read()\nsys.exit(0)\n"),
}


def _pin(made) -> None:
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "package.yaml").parent.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    for name, (said, code) in SKILLS.items():
        home = root / "skills" / name
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {said}\n---\n\n"
                                       "run it.\n", encoding="utf-8")
        (home / f"{name}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)


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

    # --- the verb runs its skill: manifest args first, the operator's after --------
    played = cli(engine, "witness", "a", "b")
    if (played.returncode == 0 and played.stdout.strip() == "witness: from-manifest a b"
            and "::push" not in played.stdout and not played.stderr):
        held("a command runs its skill", "`pp witness a b` -> the script's line with the "
             "manifest's args first; the directive never reaches the screen")
    else:
        failures.append(f"  ✗ command played               rc={played.returncode} "
                        f"{played.stdout!r} {played.stderr[:80]!r}")
    from conductor import events
    standing = events.standing_entries(made)
    if any("the witness spoke" in str(one) for one in standing):
        held("the bus harvests the push", "`::push` stood by the one collector on rc 0")
    else:
        failures.append(f"  ✗ push harvested               {standing!r}")

    # --- help composes: the console's verbs, then the packages' --------------------
    helped = cli(engine, "help")
    text = helped.stdout
    if (helped.returncode == 0 and "./pp help" in text
            and "./pp doctor" in text and "improvement" not in text
            and "admin" not in text.split("The packages' commands")[0]
            and "The packages' commands, resolved after the console's own:" in text
            and "./pp witness" in text and "(witness) the witness skill -- prints what it is given" in text
            and "./pp grumble" in text and "./pp climb" in text
            and text.index("./pp help") < text.index("./pp witness") < text.index("./pp grumble")
            < text.index("./pp climb") < text.index("The rest passes through")):
        held("help is composed", "the nine verbs, then witness/grumble/climb in declaration "
             "order, each with its package and its skill's description")
    else:
        failures.append(f"  ✗ help composed                {text[-400:]!r}")

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
        held("a withdrawn verb is a stranger", "`admin` left the console with its policy "
             "(batch l-administration-du-package): undeclared, it answers the usage like "
             "`nothere` -- the console keeps no memory of it")
    else:
        failures.append(f"  ✗ admin/stranger               {gone.returncode} {nowhere.returncode}")

    # --- a declared command whose script is gone refuses by name --------------------
    (made / ".sys" / "vendor" / "witness@0.0.1" / "skills" / "pp-witness" / "pp-witness.py").unlink()
    broken = cli(engine, "witness")
    if broken.returncode == 2 and "command-broken" in broken.stderr and not broken.stdout:
        held("a broken command refuses", "`command-broken` names the verb and the skill, rc 2")
    else:
        failures.append(f"  ✗ command broken               rc={broken.returncode} {broken.stderr[:100]!r}")
    return 0
