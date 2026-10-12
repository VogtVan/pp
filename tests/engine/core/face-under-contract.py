"""Scenario `face-under-contract` -- what the PACKAGES take from the public face is a
contract (plan pp-split, batch le-banc-de-la-face):
- the consumed surface is DERIVED from the skills' code, aliases resolved -- never a list
  written here, so a symbol a package starts using tomorrow enters the check by itself
- every derived symbol resolves on the LIVE face: a module in `__all__`, a function on its
  module, a method on the object a call returns
- a chain that runs past the face belongs to the consumer: it is said, never counted as a gap
- breaking the face reddens HERE: a name removed on a throwaway copy is named by the check
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import conductor
from tests.harness import ENGINE, SOURCE


def skills() -> list:
    """-> every skill script of the product: `packages/<p>/skills/<name>/<name>.py`."""
    return sorted(one for one in SOURCE.glob("packages/*/skills/*/*.py")
                  if one.stem == one.parent.name)


def consumed(path: Path) -> set:
    """-> the dotted paths on the face this file reaches, aliases resolved. `core(...)`
    is the root; a name or a function that returns a face path becomes a root in turn."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: dict = {}

    def reached(node):
        """-> the face path this expression names, or None when it names something else."""
        if isinstance(node, ast.Call):
            called = node.func
            if isinstance(called, ast.Name):
                return "" if called.id == "core" else roots.get(called.id)
            return reached(called)
        if isinstance(node, ast.Name):
            return roots.get(node.id)
        if isinstance(node, ast.Attribute):
            base = reached(node.value)
            return None if base is None else (base + "." + node.attr).lstrip(".")
        return None

    for node in ast.walk(tree):           # the aliases first: `engine = core(...)`, `face = engine.settings`
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and (found := reached(node.value)) is not None:
                roots[target.id] = found
        if isinstance(node, ast.FunctionDef):     # and `def regime(): return core(...).record`
            for inner in ast.walk(node):
                if isinstance(inner, ast.Return) and inner.value is not None:
                    if (found := reached(inner.value)) is not None:
                        roots[node.name] = found

    return {found for node in ast.walk(tree) if isinstance(node, ast.Attribute)
            if (found := reached(node))}


def returned(call):
    """-> the TYPE a call gives back, or None. The engine writes its annotations as
    strings (`from __future__ import annotations`), so the name is looked up where the
    function lives -- that is how `settings.of(...).of_package` resolves at all."""
    hint = getattr(call, "__annotations__", {}).get("return")
    if isinstance(hint, type):
        return hint
    if isinstance(hint, str):
        home = sys.modules.get(getattr(call, "__module__", ""))
        found = getattr(home, hint, None) if home else None
        return found if isinstance(found, type) else None
    return None


def resolve(dotted: str, face=conductor) -> tuple:
    """-> (held, past): the part of the chain the face owns, and what runs past it. A call
    on the way is followed by its RETURN type's attributes -- `settings.of(...).of_package`
    is the method of what `of` gives back, and `.append` past it is the consumer's own."""
    held, current = [], face
    for name in dotted.split("."):
        if hasattr(current, name):
            held.append(name)
            current = getattr(current, name)
            if callable(current) and not isinstance(current, type):
                current = returned(current) or current
        else:
            return ".".join(held), dotted[len(".".join(held)) + 1:]
    return dotted, ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    surface = sorted({one for path in skills() for one in consumed(path)})
    if surface and {"record", "sections", "settings"} <= set(surface):
        held("the consumed surface is derived",
             f"{len(surface)} dotted paths read from {len(skills())} skills, aliases resolved")
    else:
        failures.append(f"  ✗ derivation                 {surface}")

    # --- every derived symbol resolves on the live face; what runs past it is said
    missing, beyond = [], []
    for dotted in surface:
        owned, past = resolve(dotted)
        if not owned:
            missing.append(dotted)
        elif past:
            beyond.append(f"{owned} + .{past}")
    if not missing:
        held("the face carries what the packages take",
             f"{len(surface) - len(beyond)} resolved whole"
             + (f"; past the face and said: {', '.join(beyond)}" if beyond else ""))
    else:
        failures.append(f"  ✗ absent from the face       {missing}")

    # --- the guard BITES: a name removed on a throwaway copy is named
    home = Path(tempfile.mkdtemp(prefix="face-"))
    try:
        shutil.copytree(ENGINE / "conductor", home / "conductor")
        face = home / "conductor" / "__init__.py"
        # `record` leaves the face: its import and its place in `__all__`
        broken = (face.read_text(encoding="utf-8")
                  .replace(", persistence, record, settings", ", persistence, settings")
                  .replace('"reading", "record", "rendering"', '"reading", "rendering"'))
        assert "record" not in broken.split("__all__")[1], "the removal did not take"
        face.write_text(broken, encoding="utf-8")
        probe = ("import sys; sys.path.insert(0, %r); import conductor;"
                 " print('record' in dir(conductor))" % str(home))
        done = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
        gone = done.returncode == 0 and done.stdout.strip() == "False"
        taken = [one for one in surface if one.split(".")[0] == "record"]
        if gone and taken:
            held("the guard bites", f"`record` removed on a copy: {len(taken)} consumed paths "
                                    "would be named -- the red lands at the face, not at a skill")
        else:
            failures.append(f"  ✗ guard blunt                removed={gone} consumers={taken}")
    finally:
        shutil.rmtree(home, ignore_errors=True)
    return 0
