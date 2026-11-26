"""Scenario `agent-layers` -- the six layers of the skill `pp-agent`, read on the syntax tree of the skill its
house vendors; nothing is launched:
- every module imports the layers its own may import, and no other: `model` none; `rules`, `store` and `faces`
  `model` alone; `acts` `model`, `rules` and `store`; `verbs` the five others; the entry any
- `model`, `rules` and `faces` carry no effect: no module that reaches the system, no call that prints, opens or
  reads the keyboard, no exit raised
- every dataclass of `model` is frozen
"""
from __future__ import annotations

import ast

from conductor import instance
from tests.harness import support

A = support(__file__, "agent")
LAYERS = {"model": (), "rules": ("model",), "store": ("model",), "acts": ("model", "rules", "store"),
          "faces": ("model",), "verbs": ("model", "rules", "store", "acts", "faces")}   # a layer: what it may import
PURE = ("model", "rules", "faces")                 # the layers that carry no effect
WORLD = ("os", "sys", "pathlib", "subprocess", "shutil", "time", "datetime", "socket", "tempfile", "io",
         "threading", "signal")                    # the modules that reach the system
SPEAKING = ("print", "open", "input", "exit", "quit")   # the calls that print, open, read the keyboard or leave


def frozen(mark) -> bool:
    """Whether a `dataclass` decorator says `frozen=True`."""
    return isinstance(mark, ast.Call) and any(
        one.arg == "frozen" and isinstance(one.value, ast.Constant) and one.value.value is True for one in mark.keywords)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench, born=False)
    skill = next(iter((h.house / instance.VENDOR).glob("agent@*"))) / "skills" / "pp-agent"
    strays, effects, thawed, found = [], [], [], set()
    imports, classes = 0, 0
    for path in sorted(skill.rglob("*.py")):
        parts = path.relative_to(skill).parts
        layer = parts[0] if len(parts) > 1 else None          # the entry stands above the layers
        where = "/".join(parts)
        found.add(layer)
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [node.module or ""] if isinstance(node, ast.ImportFrom) else [one.name for one in node.names]
                for name in names:
                    top = name.split(".")[0]
                    if top in LAYERS:
                        imports += 1
                        if layer is not None and top != layer and top not in LAYERS[layer]:
                            strays.append(f"{where}:{node.lineno} imports {name}")
                    elif layer in PURE and top in WORLD:
                        effects.append(f"{where}:{node.lineno} imports {name}")
            if layer in PURE:
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in SPEAKING:
                    effects.append(f"{where}:{node.lineno} calls {node.func.id}")
                raised = node.exc.func if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) else (
                    node.exc if isinstance(node, ast.Raise) else None)
                if isinstance(raised, ast.Name) and raised.id == "SystemExit":
                    effects.append(f"{where}:{node.lineno} raises SystemExit")
            if layer == "model" and isinstance(node, ast.ClassDef):
                marks = [one for one in node.decorator_list if "dataclass" in ast.dump(one)]
                classes += bool(marks)
                if marks and not any(frozen(one) for one in marks):
                    thawed.append(f"{where}:{node.lineno} {node.name}")

    # --- every module imports the layers its own may import ----------------------------------------------------
    if found == {None, *LAYERS} and imports and not strays:
        held("the layers import what their table allows", f"{imports} imports of a layer in the six layers and the "
             "entry, none outside the table")
    else:
        failures.append(f"  ✗ the imports of the layers   found={sorted(str(one) for one in found)} imports={imports} "
                        f"strays={strays}")

    # --- model, rules and faces carry no effect ------------------------------------------------------------------
    if not effects:
        held("model, rules and faces carry no effect", "no module that reaches the system, no call that prints, "
             "opens or reads, no exit raised")
    else:
        failures.append(f"  ✗ an effect in a pure layer   {effects}")

    # --- every dataclass of model is frozen ----------------------------------------------------------------------
    if classes and not thawed:
        held("every dataclass of model is frozen", f"{classes} dataclasses, each `frozen=True`")
    else:
        failures.append(f"  ✗ a dataclass not frozen      classes={classes} {thawed}")
    return 0
