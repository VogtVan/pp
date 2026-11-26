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
- a system law placed at `.pp/system/SYS.md` heads its group whole in every output, alike under
  `verbatim_constraints` true and false, never its code; the proof line names it
SETTINGS, the placement of the overlay and the package's copies are written at the test's time.
"""
from __future__ import annotations

import json
import re

from conductor import compiling, instance, persistence, reading, render
from tests.harness import cli, demonstrated, demos, law, plant, stepped

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

    held_system = "".join(f"{one}\n" for one in compiling.system_laws(env.made) if one.section == "behavior")
    two = render(_opened(env, "TWO.md"))
    proof_block = stepped(lambda: env.conductor("t"))      # TWO's line printed: the proof comes
    labelled = [lines[0] for lines in (_section(two, "CONSTRAINTS"), _section(shown, "CONSTRAINTS")) if lines]
    if (two.count("▌ CONSTRAINTS") == 1
            and (f"production:\n{law(DRAWER, PATTERN, 'TWO.md', 'P1')}\nbehavior:\n{held_system}"
                 f"{law(DRAWER, PATTERN, 'TWO.md', 'H1')}") in two
            and labelled == ["production:", "behavior:"]
            and PROOF.findall(render(proof_block)) == ["P1"] and proof_block.output == "proof"):
        held("one title, production first, each group labelled", "TWO: P1 under `production:`, H1 under "
             "`behavior:` after the engine's system laws; RIDE's behavior laws open on their label; the proof "
             "line names P1")
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
    second = render(stepped(lambda: env.conductor(key)))
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

    def printing(key: str) -> list:
        """The agent's prints at the console: every production due at the run, by its print call."""
        due = [one["document"] for one in persistence.prints_of(persistence.slot_of(env.made, key))]
        return [cli(env.engine, key, "-print", one, "-", cwd=env.root, stdin="said") for one in due]

    key = opened()
    cli(env.engine, key, "-s", "LAPS", cwd=env.root)
    printing(key)                                # the lines DESK and the turn said, printed before the field
    lap1 = cli(env.engine, key, "-", cwd=env.root, stdin='["alpha", "beta", "gamma"]')
    proof = json.dumps([{"code": "LP1", "evidence": "alpha", "verdict": "ok"}])
    printing(key)                                # the lap's line, said beside its proof, printed first
    lap2 = cli(env.engine, key, "-", cwd=env.root, stdin=proof)
    printing(key)
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
    moved = [one.stdout for one in printing(key)]    # the lines said before the fork, printed before its value
    if "PICK next" not in staged.stdout and not any("PICK next" in one for one in moved):
        cli(env.engine, key, cwd=env.root)        # nothing moved to the PICK: the bare call brings it
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


def system(bench) -> None:
    """A system law placed at `.pp/system/SYS.md` heads `production:` whole in two outputs in a row,
    under `verbatim_constraints` true and false alike, where a document's law comes back as its code
    under codes mode; the proof line names it."""
    held, failures = bench.held, bench.failures
    said: dict[bool, list[str]] = {}
    for verbatim in (True, False):
        env = bench.env(f"laws-system-{str(verbatim).lower()}", bare=True)
        env.write("SETTINGS.md", LEAN.replace("verbatim_constraints: false", f"verbatim_constraints: {str(verbatim).lower()}"))
        plant(env, DRAWER, PATTERN, ("TWO.md",))
        env.write("system/SYS.md", (DEMO.parent / "systems" / "SYS.md").read_text(encoding="utf-8"))
        placed = [one for one in compiling.system_laws(env.made) if one.code == "SYS3"]
        opener = env.conductor()
        opener.forget()
        first = render(opener.start(env.made / "procs" / "TWO.md"))
        key = opener.run_id
        second = render(stepped(lambda: env.conductor(key)))      # TWO's line printed: the proof comes
        p1 = law(DRAWER, PATTERN, "TWO.md", "P1")
        heads = [f"production:\n{placed[0]}\n" in text for text in (first, second)] if placed else []
        coded = [line for text in (first, second) for line in text.splitlines()
                 if line.startswith("[") and "SYS3" in line]
        said[verbatim] = [line for text in (first, second) for line in text.splitlines()
                          if placed and line == str(placed[0])]
        documents = (p1 in second) == verbatim and ("[P1]" in second) != verbatim
        mode = f"verbatim {str(verbatim).lower()}"
        if (heads == [True, True] and not coded and p1 in first and documents
                and PROOF.findall(second) == ["SYS3 P1"]):
            held(f"a system law rides whole, {mode}", "SYS3 heads `production:` whole in two outputs in a row "
                 f"while P1 {'says its text again' if verbatim else 'comes back as its code'}; TWO's proof line "
                 "asks `[SYS3 P1]`")
        else:
            failures.append(f"  ✗ the system law, {mode}      heads={heads} coded={coded} documents={documents} "
                            f"proof={PROOF.findall(second)} {_section(second, 'CONSTRAINTS')!r}")
        env.conductor(key).forget()
    if said[True] and said[True] == said[False]:
        held("a system law reads alike under both settings", "the two outputs say SYS3 the same under "
             "verbatim true and false")
    else:
        failures.append(f"  ✗ the system law alike          {said!r}")


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
    system(bench)
    return 0
