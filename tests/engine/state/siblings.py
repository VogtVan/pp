"""Scenario `siblings` -- 3 case(s), in the monolith's order:
- an INSTALLED member never sees an unrelated git checkout as a sibling
- the root is the member's PARENT: the same answer whatever the process's cwd
  (batch la-racine-sans-git -- git used to answer the relative `.git`, resolved
  against the cwd, so the root moved with the caller)
- the module asks nothing of the outside: no subprocess reaches its source
"""
from __future__ import annotations

import ast
import contextlib
import inspect
import io
import os
import tempfile
from pathlib import Path
from conductor import discovery
import pp as pp_cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- an INSTALLED member never sees an unrelated git checkout as a sibling ---------
    crowded = Path(tempfile.mkdtemp())
    for stranger in ("core", "perso"):
        (crowded / stranger / ".git").mkdir(parents=True)
    with contextlib.redirect_stdout(io.StringIO()):
        pp_cli.main(["-install", str(crowded / "mine")])
    mine = discovery.instance_member(crowded / "mine" / ".pp" / ".sys" / "engine" / "pp.py")
    seen = discovery.names(discovery.siblings_around(mine))
    if seen == ["mine"]:
        held("installed members ignore bystander repos", "unrelated `.git` siblings never leak into OPTIONS")
    else:
        failures.append(f"  ✗ federation leaked          {seen}")

    # --- the root is the PARENT: the same answer whatever the process's cwd -----------
    siblings = Path(tempfile.mkdtemp())
    with contextlib.redirect_stdout(io.StringIO()):
        for name in ("alpha", "beta"):
            pp_cli.main(["-install", str(siblings / name)])
    lodged = discovery.instance_member(siblings / "alpha" / ".pp" / ".sys" / "engine" / "pp.py")
    was = Path.cwd()
    roots, names = [], []
    try:
        for where in (siblings / "alpha", siblings, Path(tempfile.mkdtemp())):
            os.chdir(where)
            around = discovery.siblings_around(lodged)
            roots.append(around.root.resolve())
            names.append(discovery.names(around))
    finally:
        os.chdir(was)
    if roots == [siblings.resolve()] * 3 and names == [["alpha", "beta"]] * 3:
        held("the root is the member's parent", "three working directories, one answer -- "
             "the members share a first-degree ancestor, nothing is asked of the outside")
    else:
        failures.append(f"  ✗ root moved with the cwd    {roots} {names}")

    # --- the module asks nothing of the outside ---------------------------------------
    source = inspect.getsource(discovery)
    calls = [node for node in ast.walk(ast.parse(source))
             if isinstance(node, ast.Call) and "subprocess" in ast.dump(node.func)]
    if "subprocess" not in source and not calls:
        held("the discovery asks nothing of the outside", "no subprocess in the module: the "
             "root is a path lookup, and no external command is a prerequisite of the engine")
    else:
        failures.append(f"  ✗ discovery shells out       {len(calls)} call(s)")
    return 0
