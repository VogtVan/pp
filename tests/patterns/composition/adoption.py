"""Scenario `adoption` -- the pattern `composition/adoption`, played from its demonstration:
- `+<name>` adopts a skill of the harness on offer: a conductible one joins the catalog described
  and its law the registry; an incompatible one stays offered by its name alone, the build saying
  why, and its call orients without playing; an unoffered copy is no name at all; a declared name
  found nowhere is offered bare and its call orients; a skill copied into the harness changes
  nothing for pp
- the adopted skill IS a call: opened on the parked run it plays in its frame, its law in force,
  its body the brief; closed, the law falls with the frame
- a borrower adopts a proc of its house the same way: described in its catalog, opened as a door
  and never mounted, its law in its registry
The skills of the harness, the house and the borrower are written at the test's time.
"""
from __future__ import annotations

import ast
import re

from conductor import compiling, instance, render
from tests.harness import cli, codes, demonstrated, demos, plant, session_of, steady

DRAWER, PATTERN = "composition", "adoption"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("HOUSE.md", "REVUE.md", "TURN.house.md", "TURN.offer.md")
STYLE = "the house style, judged by its own law"
SKILLS = {
    "housestyle": f"---\nname: housestyle\ndescription: {STYLE}\nconstraints.behavior: |\n"
                  "  H1  the house voice is plain and short.\n---\nApply the house style to the work.\n",
    "rawtool": "just prose, no front matter\n",
    "hidden": "---\nname: hidden\ndescription: compatible but never offered\n---\nunreachable\n",
}


def _heading(out: str) -> str:
    """-> the last heading of a rendered output that names a stack, its segment number dropped."""
    lines = [one for one in out.splitlines() if one.startswith("▌ ") and "▸" in one]
    return re.sub(r"^▌ \[\d+\] ", "▌ ", lines[-1]) if lines else ""


def _harness(env, name: str, text: str) -> None:
    """A skill of the harness written at the workspace's first skill folder."""
    home = env.root / instance.HARNESS_HOMES[0] / name
    home.mkdir(parents=True, exist_ok=True)
    (home / "SKILL.md").write_text(text, encoding="utf-8")


def harness(bench) -> None:
    """The skills of the harness, adopted on offer."""
    held, failures = bench.held, bench.failures
    env = bench.env("adoption")
    for name, text in SKILLS.items():
        _harness(env, name, text)
    env.write("procs/TURN.md", (DEMO / "TURN.offer.md").read_text(encoding="utf-8"))
    meta = env.made
    catalog, registry, warnings = compiling.render_tools(meta), compiling.render_registry(meta), compiling.lint(meta)
    adopted = instance.adopted(meta, "housestyle")
    raw = instance.adopted(meta, "rawtool")
    lacking = compiling.conductible(raw) if raw is not None else ""
    if (adopted is not None and f"- **`housestyle`** (harness) — {STYLE}\n  contract: {adopted}\n" in catalog
            and "- `rawtool`" in catalog and "**`rawtool`**" not in catalog and "hidden" not in catalog
            and "`H1`" in registry and "hidden" not in registry
            and lacking and any(one.startswith("offered-not-conductible: `rawtool`") and lacking in one
                                for one in warnings)
            and not any("housestyle" in one for one in warnings)):
        held("adoption on offer", "housestyle joins the catalog described and H1 the registry; rawtool stays "
             "a bare name, `offered-not-conductible` saying why; the unoffered hidden is nowhere")
    else:
        failures.append(f"  ✗ the adoption                {warnings!r}")

    opener = env.conductor()
    block = opener.start(opener.boot("BOOT.md"))
    bare = next((one for one in block.tools if one.name == "brainstorm"), None)
    if bare is not None and bare.description == "" and "brainstorm" in render(block):
        held("a name found nowhere is offered bare", "+brainstorm: in the step's offers, name only")
    else:
        failures.append(f"  ✗ the bare name               {bare}")
    opener.forget()

    settings = meta / "SETTINGS.md"             # one output carries the door's step and the parked closing
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "instructions_fusion: none", "instructions_fusion: max"), encoding="utf-8")
    opener = env.conductor()
    block = opener.start(opener.boot("BOOT.md"))
    key = opener.run_id
    while block is not None and not block.wait:
        block = env.conductor(key).submit("[]" if block.judged else "")

    def state() -> bytes:
        return session_of(meta).read_bytes()

    before = state()
    oriented = [env.cli("-s", "brainstorm"), env.cli("-s", "rawtool")]
    if (all(one.returncode == 0 and "▌" not in one.stdout and len(one.stdout.splitlines()) == 1
            and f"`{name}`" in one.stdout for one, name in zip(oriented, ("brainstorm", "rawtool")))
            and state() == before):
        held("an unconducted name orients", "brainstorm and rawtool: one line, rc 0, no block, the run unmoved")
    else:
        failures.append(f"  ✗ the orientation             {[one.returncode for one in oriented]} "
                        f"{oriented[0].stdout[:120]!r}")

    played = env.cli("-s", "housestyle")
    standing_view = env.cli("-peek")
    in_force = re.search(r"^(H1  |\[.*\bH1\b)", played.stdout, re.MULTILINE) is not None
    if (played.returncode == 0 and "▸ housestyle{1/1}" in played.stdout and in_force
            and _heading(played.stdout) and _heading(played.stdout) == _heading(standing_view.stdout)
            and "NEXT INSTRUCTION CONTEXT — housestyle" in played.stdout and "▶ AWAIT" in played.stdout):
        held("an adopted skill is a call", "opened on the parked run: its frame, H1 in force, its body the "
             "brief; the output's last heading and -peek name the frame that stands; the run stays parked")
    else:
        failures.append(f"  ✗ the call                    rc={played.returncode} force={in_force} "
                        f"last={_heading(played.stdout)!r} peek={_heading(standing_view.stdout)!r} "
                        f"await={'▶ AWAIT' in played.stdout} {played.stdout[-500:]!r}")
    closed = env.cli(key)
    back = env.conductor(key).peek()
    if closed.returncode == 0 and back is not None and "housestyle" not in back.stack and "H1" not in codes(back):
        held("the adopted frame pops clean", "closed, the law falls with its frame")
    else:
        failures.append(f"  ✗ the pop                     {back and back.stack!r} {codes(back)}")

    invisible = env.cli("-s", "hidden")
    usage = ast.get_docstring(ast.parse(env.engine.read_text(encoding="utf-8"))).splitlines()[0]
    if (invisible.returncode == 2 and "▌ DEVIATION" in invisible.stdout and "hidden" in invisible.stdout
            and usage not in invisible.stdout + invisible.stderr):
        held("an unoffered copy is no name", "hidden, in the harness's folder but offered nowhere: refused "
             "under the pending block's DEVIATION, as any name not offered, never the console's usage")
    else:
        failures.append(f"  ✗ the unoffered copy          rc={invisible.returncode} {invisible.stdout[:160]!r}")

    view, listed = steady(render(env.conductor(key).peek())), compiling.render_tools(meta)
    _harness(env, "turn", (DEMO / "TURN.offer.md").read_text(encoding="utf-8"))
    if steady(render(env.conductor(key).peek())) == view and compiling.render_tools(meta) == listed:
        held("a skill copied into the harness changes nothing", "a TURN copied to the harness's skill "
             "folder: the view and the catalog byte-identical")
    else:
        failures.append("  ✗ the indifference            the harness copy leaked into pp")
    env.conductor(key).forget()


def house(bench) -> None:
    """A borrower adopts a proc of its house: described, opened as a door, never mounted."""
    held, failures = bench.held, bench.failures
    env = bench.env("adoption-house")
    plant(env, DRAWER, PATTERN, ("HOUSE.md", "REVUE.md"))
    revue = env.made / "procs" / "REVUE.md"          # the house mounts it at its own boot: a borrower never does
    revue.write_text(revue.read_text(encoding="utf-8").replace("kind: proc\n", "kind: proc\nmount: boot.initialize\n"),
                     encoding="utf-8")
    console = env.made / ".sys" / "engine" / "pp.py"
    cli(console, "-install", "agents/b", cwd=env.root)
    borrower = env.root / "agents" / "b" / env.made.name
    (borrower / "procs").mkdir(exist_ok=True)
    (borrower / "procs" / "TURN.md").write_text((DEMO / "TURN.house.md").read_text(encoding="utf-8"),
                                                encoding="utf-8")
    catalog = compiling.render_tools(borrower)
    if (instance.adopted(borrower, "REVUE") == revue and "**`REVUE`** (house)" in catalog
            and str(revue) in catalog and "- `REVUE`\n" not in catalog):
        held("a borrower adopts the house's proc on offer", "+REVUE at its TURN: described in its catalog, "
             "its contract the house's procs/REVUE.md")
    else:
        failures.append(f"  ✗ the house proc listed       {instance.adopted(borrower, 'REVUE')}")
    home = env.root / "agents" / "b"
    first = cli(console, "--instance", str(borrower), "-new", cwd=home)
    door = cli(console, "--instance", str(borrower), "-s", "REVUE", cwd=home)
    if (first.returncode == 0 and "▸ REVUE" not in first.stdout and "HS1" not in first.stdout
            and door.returncode == 0 and "▸ REVUE{" in door.stdout and "RV1" in door.stdout):
        held("the adopted proc is a door, never a mount", "the borrower's boot mounts nothing of the house; "
             "`-s REVUE` opens its frame, RV1 in force")
    else:
        failures.append(f"  ✗ the house door              rc={first.returncode}/{door.returncode} {door.stdout[-200:]!r}")
    (borrower / "procs" / "MINE.md").write_text(
        "---\nname: MINE\nkind: doc\nconstraints.production: |\n  RV1  the borrower's own law.\n---\n",
        encoding="utf-8")
    registry = compiling.render_registry(borrower)
    doubled = [one for one in compiling.lint(borrower) if one.startswith("constraint-doubled: `RV1`")]
    if "`RV1`" in registry and doubled and "REVUE.md" in doubled[0]:
        held("the adopted proc's law joins the registry", "RV1 registered; the borrower's own RV1 is said "
             "doubled against the house's REVUE")
    else:
        failures.append(f"  ✗ the house registry          {doubled}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    harness(bench)
    house(bench)
    return 0
