"""Scenario `sink` -- the pattern `outputs/sink`, played from its demonstration:
- a document that declares `sink: <skill>` hands its production to that skill: the step goes to the
  tool, the production reaches the skill on its standard input, what the skill prints comes back as a
  section of the next block, the ledger says `sink` with the skill, the trace counts the play
- a skill that refuses is said back and the run goes on; a malformed directive refuses `push-malformed`
The skills are written at the test's time.
"""
from __future__ import annotations

from conductor import render
from tests.harness import demonstrated, plant, traced

DRAWER, PATTERN = "outputs", "sink"
DEMOS = ("LOUD.md", "SOUR.md", "TALLIED.md")
SKILLS = {
    "pp-tally": "import sys\nlines = sys.stdin.read().splitlines()\nprint(f'tallied {len(lines)} line(s)')\n"
                "print('first:', lines[0] if lines else '')\n",
    "pp-sour": "import sys\nsys.stdin.read()\nsys.stderr.write('no tally today')\nsys.exit(1)\n",
    "pp-loud": "import sys\nsys.stdin.read()\nprint('::push half')\n",
}
PRODUCTION = "three apples\ntwo pears\n"


def _skills(env) -> None:
    for name, code in SKILLS.items():
        home = env.made / "skills" / name
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: a sink of the bench\n---\n\n{name}\n",
                                       encoding="utf-8")
        (home / f"{name}.py").write_text(code, encoding="utf-8")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("sink", bare=True)
    _skills(env)
    plant(env, DRAWER, PATTERN, DEMOS)

    def opened(name: str):
        runner = env.conductor("t")
        runner.forget()
        return runner.start(env.made / "procs" / name)

    asked = opened("TALLIED.md")
    after = env.conductor("t").submit(PRODUCTION)
    section = dict(after.payloads).get("sink pp-tally", "") if after is not None else ""
    ledger = [line for one in traced(env, "t") if one.get("kind") == "block" for line in (one.get("served") or [])
              if line.get("origin") == "sink"]
    plays = [one for one in traced(env, "t") if one.get("kind") == "sink"]
    if ("=> tool" in render(asked) and "tallied 2 line(s)" in section and PRODUCTION.splitlines()[0] in section
            and "INFORMATION — sink pp-tally" in render(after)
            and ledger and ledger[0].get("with") == "pp-tally" and plays and plays[0].get("skill") == "pp-tally"):
        held("the production goes to the skill", "TALLIED's step goes to the tool; pp-tally reads it on stdin and "
             "its words come back under `sink pp-tally`; the ledger says `sink`, the trace the play")
    else:
        failures.append(f"  ✗ the sink                    {section!r} ledger={ledger} plays={plays}")

    opened("SOUR.md")
    soured = env.conductor("t").submit(PRODUCTION)
    said = dict(soured.payloads).get("sink pp-sour", "") if soured is not None else ""
    if soured is not None and soured.wait and "refused (1)" in said and "no tally today" in said:
        held("a skill that refuses is said back", "pp-sour exits 1: its refusal and its words under `sink pp-sour`, "
             "the run parks as usual")
    else:
        failures.append(f"  ✗ the refusing skill          {said!r}")

    opened("LOUD.md")
    expect("push-malformed", lambda: env.conductor("t").submit(PRODUCTION))
    env.conductor("t").forget()
    return 0
