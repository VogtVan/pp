"""Scenario `instance-names` -- how an instance and its members are named:
- the siblings: an instance recognizes its members by their `instance.yaml` alone -- a
  bystander git checkout is never one; the root is the member's PARENT, the same answer
  whatever the process's cwd; the discovery asks nothing of the outside
- kebab(): lowercase, runs of anything else become one dash, trimmed at the edges

The members are bare instance trees: a directory carrying `.sys/instance.yaml` is an
instance, and the discovery reads nothing else.
"""
from __future__ import annotations

import ast
import inspect
import os
import tempfile
from pathlib import Path

from conductor import discovery, instance


def _member(workspace: Path) -> Path:
    """Writes a bare instance under `workspace`. -> the path its installed engine would hold."""
    meta = workspace / instance.DIRECTORY
    (meta / instance.MANIFEST).parent.mkdir(parents=True)
    (meta / instance.MANIFEST).write_text("packages: {}\n", encoding="utf-8")
    return meta / instance.SYS / "engine" / "pp.py"


def siblings(bench) -> None:
    """The members around an instance: recognized by their instance, rooted at the parent."""
    held, failures = bench.held, bench.failures
    # --- an instance never sees an unrelated git checkout as a sibling ----------------------
    crowded = Path(tempfile.mkdtemp())
    for stranger in ("core", "perso"):
        (crowded / stranger / ".git").mkdir(parents=True)
    mine = discovery.instance_member(_member(crowded / "mine"))
    seen = discovery.names(discovery.siblings_around(mine))
    if seen == ["mine"]:
        held("installed members ignore bystander repos", "unrelated `.git` siblings never leak into OPTIONS")
    else:
        failures.append(f"  ✗ bystander leaked          {seen}")

    # --- the root is the PARENT: the same answer whatever the process's cwd -----------------
    around_root = Path(tempfile.mkdtemp())
    lodged = discovery.instance_member(_member(around_root / "alpha"))
    _member(around_root / "beta")
    was = Path.cwd()
    roots, names = [], []
    try:
        for where in (around_root / "alpha", around_root, Path(tempfile.mkdtemp())):
            os.chdir(where)
            around = discovery.siblings_around(lodged)
            roots.append(around.root.resolve())
            names.append(discovery.names(around))
    finally:
        os.chdir(was)
    if roots == [around_root.resolve()] * 3 and names == [["alpha", "beta"]] * 3:
        held("the root is the member's parent", "three working directories, one answer -- "
             "the members share a first-degree ancestor, nothing is asked of the outside")
    else:
        failures.append(f"  ✗ root moved with the cwd    {roots} {names}")

    # --- the module asks nothing of the outside ---------------------------------------------
    source = inspect.getsource(discovery)
    calls = [node for node in ast.walk(ast.parse(source))
             if isinstance(node, ast.Call) and "subprocess" in ast.dump(node.func)]
    if "subprocess" not in source and not calls:
        held("the discovery asks nothing of the outside", "no subprocess in the module: the "
             "root is a path lookup, and no external command is a prerequisite of the engine")
    else:
        failures.append(f"  ✗ discovery shells out       {len(calls)} call(s)")


def kebab(bench) -> None:
    """kebab(): lowercase, runs of anything else become one dash, trimmed at the edges."""
    held, failures = bench.held, bench.failures
    if (instance.kebab("My Workspace") == "my-workspace"
            and instance.kebab("sw7_hub--infra!!") == "sw7-hub-infra"
            and instance.kebab("--Edges--") == "edges"):
        held("kebab() normalizes", "lowercase, one dash per run, no leading/trailing dash")
    else:
        failures.append("  ✗ kebab()")


def scenario(bench) -> int:
    siblings(bench)
    kebab(bench)
    return 0
