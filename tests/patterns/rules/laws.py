"""Scenario `laws` -- the pattern `rules/laws`, played from its demonstration:
- the laws ride every block in full text, under ONE CONSTRAINTS title, each group opening on its
  label, production first; the proof line names the production codes; a law line without its code
  refuses `constraint-malformed`
- under `verbatim_constraints: false` a law's text renders at its first emission of the run and its
  code at every re-emission, a new frame's law says its text; no registry is served nor written;
  after `-compacted` the texts return
- a law redone by its code keeps the section of its first emission across the processes a routed
  frame spans: the laps of a described door routed from a WORK render `production:` with their own
  law alone and the inherited codes under `behavior:`, their proof line asks their own law, their
  heading counts the lap's steps; a successor shows no `production:` section
- an overlay adds each law in the section of its key
- the build: a code the author declares twice WARNS and the build passes, the derived table names it
  once, no registry file; the same double in a package's documents refuses `constraint-doubled`; a
  law line out of form is dropped with a warning in the author's document and refuses in a
  package's; a bare `constraints:` refuses `constraints-unsectioned`
SETTINGS, the placement of the overlay and the package's copies are written at the test's time.
"""
from __future__ import annotations

import json
import re

from conductor import compiling, instance, reading, render
from tests.harness import cli, demonstrated, demos, law, plant

DRAWER, PATTERN = "rules", "laws"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("CODED.md", "DESK.md", "DOUBLE.md", "FRESH.md", "LAPS.md", "LEFT.md", "OLD.md", "RIDE.md",
         "RIGHT.md", "ROUTE.md", "SHIFTED.md", "SHIFTED.overlay.md", "STAGE.md", "TORN.md", "TWIN.md",
         "TWO.md")
LEAN = "---\nname: SETTINGS\nkind: doc\nverbatim_constraints: false\nmax_harness_tool_output: 60000\n---\n"
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\nmax_harness_tool_output: 200000\n---\n"
KEY = re.compile(r"run ([0-9a-f]{6})")
PROOF = re.compile(r"^INFER proof \[([^\]]*)\]", re.M)     # the codes a proof line asks for
HEAD = re.compile(r"▸ LAPS\{([0-9-]+)/(\d+)\}")              # a lap's heading: its steps' range


def _text(name: str) -> str:
    return (DEMO / name).read_text(encoding="utf-8")


def _said(name: str, code: str) -> str:
    """-> the text of the law `code` of the demonstration `name`, without its code."""
    return law(DRAWER, PATTERN, name, code).split(None, 1)[1]


def _section(text: str, title: str) -> list[str]:
    """-> the lines of the LAST `▌ <title>` section of `text`."""
    lines = text.splitlines()
    starts = [i for i, one in enumerate(lines) if one == f"▌ {title}"]
    if not starts:
        return []
    out = []
    for one in lines[starts[-1] + 1:]:
        if one.startswith(("▌ ", "▶ ")):
            break
        out.append(one)
    return out


def _opened(env, name: str):
    runner = env.conductor("t")
    runner.forget()
    return runner.start(env.made / "procs" / name)


def riding(bench) -> None:
    """The laws ride every block in full text, one title, production first; a line without code refuses."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("laws", bare=True)
    plant(env, DRAWER, PATTERN, ("RIDE.md", "TORN.md", "TWO.md"))

    first = _opened(env, "RIDE.md")
    owed = [("L1", _said("RIDE.md", "L1")), ("L2", _said("RIDE.md", "L2"))]
    shown = render(first)
    if [(one.code, one.text) for one in first.constraints] == owed and all(text in shown for _, text in owed):
        held("the laws ride the block", "RIDE's L1 and L2 in full text on its block -- never a reference")
    else:
        failures.append(f"  ✗ the ride                    {first.constraints}")
    env.conductor("t").forget()

    two = render(_opened(env, "TWO.md"))
    proof_block = env.conductor("t").submit("")
    labelled = [lines[0] for lines in (_section(two, "CONSTRAINTS"), _section(shown, "CONSTRAINTS")) if lines]
    if (two.count("▌ CONSTRAINTS") == 1
            and f"production:\n{law(DRAWER, PATTERN, 'TWO.md', 'P1')}\nbehavior:\n{law(DRAWER, PATTERN, 'TWO.md', 'H1')}" in two
            and labelled == ["production:", "behavior:"]
            and PROOF.findall(render(proof_block)) == ["P1"] and proof_block.output == "proof"):
        held("one title, production first, each group labelled", "TWO: P1 under `production:`, H1 under "
             "`behavior:`; RIDE's behavior laws open on their label; the proof line names P1")
    else:
        failures.append(f"  ✗ the sections                {labelled} {_section(two, 'CONSTRAINTS')!r}")
    env.conductor("t").forget()
    expect("constraint-malformed", lambda: _opened(env, "TORN.md"))


def codes(bench) -> None:
    """Under codes mode a law's text renders once per run, its code after; the texts return after
    a compaction."""
    held, failures = bench.held, bench.failures
    env = bench.env("laws-codes", bare=True)
    env.write("SETTINGS.md", LEAN)
    plant(env, DRAWER, PATTERN, ("CODED.md", "FRESH.md"))
    w4 = law(DRAWER, PATTERN, "CODED.md", "W4")
    y1 = law(DRAWER, PATTERN, "FRESH.md", "Y1")
    opener = env.conductor()
    opener.forget()
    first = render(opener.start(env.made / "procs" / "CODED.md"))
    key = opener.run_id
    second = render(env.conductor(key).submit(""))
    written = any((env.made / ".sys" / name).is_file() for name in ("constraints.md", "_constraints.md"))
    if (w4 in first and "INFORMATION — constraints" not in first and not written
            and w4 not in second and "W4" in second and y1 in second):
        held("the first emission is verbatim, the re-emission its code", "W4's text on CODED's first block, "
             "its code on the next while FRESH's Y1 says its text; no registry served, no file written")
    else:
        failures.append(f"  ✗ the codes mode              {w4 in first} {w4 in second} {y1 in second} {written}")
    compacted = render(env.conductor(key).compacted())
    if _said("CODED.md", "W4") in compacted and "INFORMATION — constraints" not in compacted:
        held("the texts return after a compaction", "after -compacted every law says its text again")
    else:
        failures.append("  ✗ the compacted texts")
    env.conductor(key).forget()


def sections(bench) -> None:
    """A law redone by its code keeps the section of its first emission across processes."""
    held, failures = bench.held, bench.failures
    env = bench.env("laws-sections")
    env.write("SETTINGS.md", FUSED)
    plant(env, DRAWER, PATTERN, ("DESK.md", "LAPS.md", "LEFT.md", "RIGHT.md", "ROUTE.md", "STAGE.md"))

    def opened() -> str:
        out = cli(env.engine, "-new", "go", cwd=env.root, env={"PP_DOOR": "DESK.md"})
        return KEY.search(out.stdout).group(1) if KEY.search(out.stdout) else ""

    key = opened()
    cli(env.engine, key, "-s", "LAPS", cwd=env.root)
    lap1 = cli(env.engine, key, "-", cwd=env.root, stdin='["alpha", "beta", "gamma"]')
    proof = json.dumps([{"code": "LP1", "evidence": "alpha", "verdict": "ok"}])
    lap2 = cli(env.engine, key, "-", cwd=env.root, stdin=proof)
    lap3 = cli(env.engine, key, "-", cwd=env.root, stdin=proof)
    laps = [lap1.stdout, lap2.stdout, lap3.stdout]
    good = []
    for text in laps:
        constraints = "\n".join(_section(text, "CONSTRAINTS"))
        under = constraints.split("behavior:")[0] if "behavior:" in constraints else constraints
        good.append(constraints.startswith("production:") and "LP1" in under and "B1" not in under
                    and "behavior:" in constraints and "B1" in constraints.split("behavior:")[-1]
                    and PROOF.findall(text) == ["LP1"])
    if all(good) and all(one.returncode == 0 for one in (lap1, lap2, lap3)):
        held("the laps keep their sections", "three laps: `production: [LP1]`, DESK's B1 under `behavior:`, "
             "the proof line asks `[LP1]` alone")
    else:
        failures.append(f"  ✗ the laps                    good={good} {_section(laps[0], 'CONSTRAINTS')!r} "
                        f"proof={[PROOF.findall(t) for t in laps]}")
    heads = [HEAD.findall(text) for text in laps]
    if all(found and found[-1] == ("1-2", "2") for found in heads):
        held("the lap counter is stable", f"three laps headed {[found[-1] for found in heads]}: the line and "
             "its PROVE")
    else:
        failures.append(f"  ✗ the counter                 {heads}")

    key = opened()
    staged = cli(env.engine, key, "-s", "ROUTE", cwd=env.root)
    if "PICK next" not in staged.stdout:
        cli(env.engine, key, cwd=env.root)        # STAGE's line said: the bare call closes it, the PICK comes
    left = cli(env.engine, key, "LEFT.md", cwd=env.root)
    constraints = _section(left.stdout, "CONSTRAINTS")
    if left.returncode == 0 and "▸ LEFT" in left.stdout and "production:" not in constraints and "behavior:" in constraints:
        held("a successor shows no production section", f"LEFT's block: {constraints}")
    else:
        failures.append(f"  ✗ the successor               rc={left.returncode} {constraints!r} {left.stdout[-200:]!r}")


def overlaid(bench) -> None:
    """An overlay adds each law in the section of its key."""
    held, failures = bench.held, bench.failures
    env = bench.env("laws-overlay", bare=True)
    plant(env, DRAWER, PATTERN, ("SHIFTED.md",))
    env.write("SHIFTED.md", _text("SHIFTED.overlay.md"))
    laws, _ = compiling.effective(env.made, reading.read(instance.resolve(env.made, "SHIFTED.md")))
    if {one.code: one.section for one in laws} == {"SB1": "behavior", "SP1": "production",
                                                   "SB9": "behavior", "SP9": "production"}:
        held("an overlay adds in the section of its key", "SB9 behavior, SP9 production, beside SHIFTED's own")
    else:
        failures.append(f"  ✗ the overlay's sections      {[(one.code, one.section) for one in laws]}")


def build(bench) -> None:
    """The build: the author's law defects warn, a package's refuse; a bare `constraints:` refuses."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("laws-build")
    meta = env.made
    env.write_member()
    kit = next((meta / instance.VENDOR).glob("kit@*")) / "procs"

    def clear(*names: str) -> None:
        for name in names:
            (meta / "procs" / name).unlink(missing_ok=True)
            (kit / name).unlink(missing_ok=True)

    plant(env, DRAWER, PATTERN, ("DOUBLE.md", "TWIN.md"))
    built = env.cli("-build")
    warned = [one for one in compiling.lint(meta) if one.startswith("constraint-doubled")]
    registry = compiling.render_registry(meta)
    written = any((meta / instance.SYS / name).is_file() for name in ("constraints.md", "_constraints.md"))
    if built.returncode == 0 and warned and "WARNING" in built.stdout and registry.count("`Z9`") == 1 and not written:
        held("the author's double warns", "-build rc=0, the warning names Z9, Z9 once in the derived table, "
             "no registry file")
    else:
        failures.append(f"  ✗ the author's double         rc={built.returncode} {warned}")
    clear("DOUBLE.md", "TWIN.md")

    for name in ("DOUBLE.md", "TWIN.md"):
        (kit / name).write_text(_text(name), encoding="utf-8")
    expect("constraint-doubled", lambda: compiling.render_registry(meta))
    clear("DOUBLE.md", "TWIN.md")

    plant(env, DRAWER, PATTERN, ("TORN.md",))
    warned = [one for one in compiling.lint(meta) if one.startswith("constraint-malformed")]
    if warned and "Z7" in compiling.declarations(meta):
        held("the author's line out of form is dropped", "the warning names it, Z7 still declared")
    else:
        failures.append(f"  ✗ the line out of form        {warned}")
    clear("TORN.md")
    (kit / "TORN.md").write_text(_text("TORN.md"), encoding="utf-8")
    expect("constraint-malformed", lambda: compiling.render_registry(meta))
    clear("TORN.md")

    plant(env, DRAWER, PATTERN, ("OLD.md",))
    expect("constraints-unsectioned", lambda: compiling.render_registry(meta))
    clear("OLD.md")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    riding(bench)
    codes(bench)
    sections(bench)
    overlaid(bench)
    build(bench)
    return 0
