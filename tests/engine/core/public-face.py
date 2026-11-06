"""Scenario `public-face` -- the engine's ONE public face, and what stands behind it:
- the face: `__all__` names the whole API, `dir()` renders it, every name resolves; `record`
  is on it, the write regime a package's script imports; a name off the API refuses by
  AttributeError, and the face brings PyYAML with it
- the contract: what the PACKAGES take from the face is DERIVED from the skills' code,
  aliases resolved; every derived symbol resolves on the LIVE face (a module in `__all__`, a
  function on its module, a method on the object a call returns), a chain past the face is
  said, and a name removed from a throwaway copy of the face is named by the check
- the layering: `core/model.py` imports nothing, so its objects cross every layer
- the settings at the skills: no skill opens `SETTINGS.md` itself, and a key a fragment
  PRESETS by effort -- derived from the fragments -- is read through the face or not at all
"""
from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import conductor
from tests.harness import ENGINE, SOURCE

DOCUMENT = re.compile(r"SETTINGS\.md")


def skills() -> list:
    """-> every skill script of the product: `packages/<p>/skills/<name>/<name>.py`."""
    return sorted(one for one in SOURCE.glob("packages/*/skills/*/*.py")
                  if one.stem == one.parent.name)


# --- the face ------------------------------------------------------------------------------

def face(bench) -> None:
    """The API is whole, `record` is on it, and the face is closed."""
    held, failures = bench.held, bench.failures

    unresolved = [name for name in conductor.__all__ if not hasattr(conductor, name)]
    if not unresolved and set(conductor.__all__) <= set(dir(conductor)):
        held("the API is whole", f"{len(conductor.__all__)} names declared, each one resolves")
    else:
        failures.append(f"  ✗ API whole                  unresolved={unresolved}")

    if ("record" in conductor.__all__
            and hasattr(conductor.record, "held") and hasattr(conductor.record, "replace")):
        held("record is on the face", "the write regime a package's script imports: held, replace")
    else:
        failures.append("  ✗ record on the face         absent from the API")

    try:
        conductor.nothing_of_the_sort
        off = "reached"
    except AttributeError:
        off = "refused"
    if off == "refused" and "yaml" in sys.modules:
        held("the face is closed and whole", "an unknown name refuses; importing it brings the engine, PyYAML included")
    else:
        failures.append(f"  ✗ face closed                {off}, yaml loaded={'yaml' in sys.modules}")


# --- the contract --------------------------------------------------------------------------

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


def contract(bench) -> None:
    """What the packages take from the face is derived, carried, and guarded."""
    held, failures = bench.held, bench.failures

    surface = sorted({one for path in skills() for one in consumed(path)})
    if surface and {"record", "sections", "settings"} <= set(surface):
        held("the consumed surface is derived",
             f"{len(surface)} dotted paths read from {len(skills())} skills, aliases resolved")
    else:
        failures.append(f"  ✗ derivation                 {surface}")

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

    # the guard bites: `record` leaves a throwaway copy of the face -- its import and its
    # place in `__all__`
    home = bench.temp()
    shutil.copytree(ENGINE / "conductor", home / "conductor")
    init = home / "conductor" / "__init__.py"
    broken = (init.read_text(encoding="utf-8")
              .replace(", persistence, record, settings", ", persistence, settings")
              .replace('"reading", "record", "rendering"', '"reading", "rendering"'))
    assert "record" not in broken.split("__all__")[1], "the removal did not take"
    init.write_text(broken, encoding="utf-8")
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


# --- the layering --------------------------------------------------------------------------

def layering(bench) -> None:
    """The model crosses every layer because it depends on none of them."""
    tree = ast.parse((ENGINE / "conductor" / "core" / "model.py").read_text(encoding="utf-8"))
    inner = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and (n.level or 0) > 0]
    if not inner:
        bench.held("model.py depends on nothing", "the data objects cross every layer")
    else:
        bench.failures.append(f"  ✗ model.py imports          {[n.module for n in inner]}")


# --- the settings at the skills ------------------------------------------------------------

def preset_keys() -> set:
    """-> the keys a fragment presets by effort, read from the fragments themselves -- the bases'
    and the packages': the day one is added, this guard covers it without a line changing here."""
    found = set()
    for fragment in sorted([*SOURCE.glob("bases/*/settings/SETTINGS.md"),
                            *SOURCE.glob("packages/*/settings/SETTINGS.md")]):
        head = fragment.read_text(encoding="utf-8").split("---")[1]
        block = re.search(r"^effort: \|\n((?:  .*\n)+)", head, re.M)
        if block:
            found |= {line.split()[0] for line in block.group(1).splitlines() if line.strip()}
    return found


def code_of(path) -> str:
    """-> the file without its comment tails: a mention in prose is not a reader."""
    return "\n".join(line.split("#", 1)[0] for line in path.read_text(encoding="utf-8").splitlines())


def settings_at_the_skills(bench) -> None:
    """A setting is read through the face, never by hand."""
    held, failures = bench.held, bench.failures
    scripts = skills()

    openers = [one.stem for one in scripts
               if DOCUMENT.search(code_of(one)) and "of_package" not in code_of(one)]
    if not openers:
        held("no skill reads the settings by hand",
             f"{len(scripts)} skills, none opens SETTINGS.md on its own")
    else:
        failures.append(f"  ✗ hand readers               {openers}")

    presets = preset_keys()
    astray = [(one.stem, key) for one in scripts for key in presets
              if key in code_of(one) and "of_package" not in code_of(one)]
    if presets and not astray:
        held("a preset key goes through the face",
             f"{len(presets)} keys preset by an effort ({', '.join(sorted(presets))}), none read by hand")
    else:
        failures.append(f"  ✗ preset read by hand        {astray or 'no preset declared at all'}")


def scenario(bench) -> int:
    face(bench)
    contract(bench)
    layering(bench)
    settings_at_the_skills(bench)
    return 0
