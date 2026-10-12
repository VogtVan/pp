"""Scenario `plan-purity` -- the package holds nothing that is not its own (plan pp-split,
phase plan, batch la-purete-de-plan):
- every settings key wears the package's prefix, and the package sows nothing
- no OPTIONAL neighbour is named: what it names, it requires
- what it takes from the ENGINE goes through the vendored bootstrap, and every name it
  takes stands on the public face
- its tests live with it, and no artifact of its own sits in the kit or the engine: the
  two prose mentions that remain are FROZEN here, so a new one reddens by name
"""
from __future__ import annotations

import re

from tests.harness import SOURCE

HOME = SOURCE / "packages" / "plan"
OPTIONAL = ("authoring", "continuity", "improvement", "federation", "doc", "daneel")
# the engine's PROSE mentions of this package, frozen: docstrings that name it as an
# EXAMPLE and drive nothing. A new line anywhere reddens -- prose is counted, never
# rewritten from here (it belongs to the core's own documentary pass).
PROSE = {("engine/conductor/core/sections.py", "pp-plan"),
         ("engine/conductor/state/settings.py", "plan_implementation_care")}
NAMES = re.compile(r"pp-plan|plan-next-move|plan_implementation|NEXT_MOVE\.md|plans/<slug>")


def _sources(home):
    return [one for one in sorted(home.rglob("*"))
            if one.is_file() and one.suffix in (".py", ".md", ".yaml")
            and "__pycache__" not in one.parts]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the keys wear the prefix, and nothing is sown ------------------------------------
    fragment = (HOME / "settings" / "SETTINGS.md").read_text(encoding="utf-8")
    front = fragment.split("---")[1] if fragment.startswith("---") else ""
    model = ("name", "kind", "package", "description", "types")
    keys = [line.split(":")[0] for line in front.splitlines()
            if re.match(r"^[a-z_]+:", line) and line.split(":")[0] not in model]
    sown = (HOME / "seed").exists()
    if keys and all(one.startswith("plan_") for one in keys) and not sown:
        held("the keys wear the prefix and nothing is sown",
             f"{', '.join(keys)} -- and no seed/ directory: the mode plants nothing in an instance")
    else:
        failures.append(f"  ✗ prefix and seeds            keys={keys} sown={sown}")

    # --- what it names, it requires --------------------------------------------------------
    named = {}
    for path in _sources(HOME):
        if path.parts[-2:][0] == "tests" or "tests" in path.relative_to(HOME).parts:
            continue                     # a bench composes what it needs to prove
        text = path.read_text(encoding="utf-8")
        for neighbour in OPTIONAL:
            # a package is NAMED the way the house names one: backticked in prose, or as a
            # path or a skill in code -- `doc` the package, never `doc` the local variable
            if re.search(rf"`{neighbour}`|packages/{neighbour}\b|\bpp-{neighbour}\b", text):
                named.setdefault(neighbour, []).append(str(path.relative_to(HOME)))
    if not named:
        held("what it names, it requires", "no optional neighbour appears in the package's "
             "own files -- only steering, which its manifest declares")
    else:
        failures.append(f"  ✗ optional neighbours         {named}")

    # --- what it takes from the engine goes through the face -------------------------------
    from conductor import __all__ as face
    keeper = (HOME / "skills" / "pp-plan" / "pp-plan.py").read_text(encoding="utf-8")
    taken = set(re.findall(r"core\(__file__\)\.(\w+)", keeper))
    direct = re.findall(r"^\s*(?:from|import)\s+conductor", keeper, re.MULTILINE)
    if taken and taken <= set(face) and not direct:
        held("what it takes from the engine stands on the face",
             f"{', '.join(sorted(taken))} -- reached by the vendored bootstrap, and every one "
             "of them is a name the public face exports")
    else:
        failures.append(f"  ✗ engine surface              taken={sorted(taken)} direct={direct}")

    # --- no artifact of its own in the kit or the engine; the prose is frozen ---------------
    strays, prose = [], set()
    for area in ("engine", "kit"):
        for path in _sources(SOURCE / area):
            for line in path.read_text(encoding="utf-8").splitlines():
                if NAMES.search(line):
                    spot = str(path.relative_to(SOURCE))
                    known = [one for one in PROSE if one[0] == spot and one[1] in line]
                    (prose.add((spot, known[0][1])) if known else strays.append(f"{spot}: {line.strip()[:60]}"))
    if not strays and prose == PROSE:
        held("no artifact of its own outside the package",
             f"the kit and the engine name it in {len(PROSE)} PROSE lines and nowhere else -- "
             "frozen here, so a new mention reddens by name; rewriting them is the core's own pass")
    else:
        failures.append(f"  ✗ kit and engine              strays={strays} prose={sorted(prose)}")
    return 0
