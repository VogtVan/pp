"""Scenario `team-layers` -- 10 case(s): the domains and the layers of the skill `pp-team`, read on the syntax tree of
the skill its house vendors; nothing is launched:
- the form: beside the entry, one folder per domain of `ORDER`, every one of them and none other; in a folder, its
  `__init__.py` and modules named after a layer of `LAYERS`, nothing else; the entry defines `main` and nothing else
- the order: a module of `model`, `replay`, `rules` or `faces` imports no domain that follows its own in `ORDER`
- `model`, `replay`, `rules` and `faces` carry no effect: no module of `WORLD` imported, no call of `SPEAKING`, no
  `SystemExit` raised, no method of `REACHING` called -- a path that reads or writes the disk, a clock read --, no
  clock of `CLOCKS` named, called or not;
  `pathlib` and `datetime` are imported as types
- every dataclass of a `model.py` is frozen
- the skill imports nothing but the standard library, its own folders, `_core` and `conductor`: no module of pp-agent
  nor of pp-ui
- the table of the layers holds on the imports (`TABLE`): each import of a module of the skill by a module of a
  domain's folder -- at the head or in a body, absolute or relative, a layer named as a module or as a name of its
  folder (`skill_imports`) -- is one its layer may make, the two exceptions of `EXCEPTIONS` aside; a
  domain's folder imported whole is out of the table; red, one line per import out of the table: the module, its
  line, what it imports
- the order holds on `store`: a store imports no domain that follows its own in `ORDER`
- a pure layer calls on `conductor` only what `CONDUCTOR` names (C37 made precise): a text reader of the engine, its
  `Refusal` raised or caught, a `Document` built -- on the parameter or on a name bound to it (`engine_reached`) --,
  and imports nothing of the engine
- no cycle of imports: none between the `acts.py`, none between the modules of the skill; red, one line per cycle,
  its modules sorted
- every import of a domain stands at the head: in a domain's folder, no module imports a domain after its first
  definition, in a body included; the entry aside, which imports its verbs after `sys.path.insert`; red, one line per
  module, the lines of its late imports
"""
from __future__ import annotations

import ast
import sys

from tests.harness import support

T = support(__file__, "team")
ENTRY = "pp-team.py"
ORDER = ("house", "template", "declaration", "season", "documents", "task", "rhythm", "wake", "budget", "health", "net",
         "journal", "tick", "stats", "watch", "status", "admin")   # the domains, each after those it may import
LAYERS = ("model", "replay", "rules", "faces", "store", "acts", "verbs")   # the modules a domain's folder may hold
PURE = ("model", "replay", "rules", "faces")      # the layers that carry no effect and follow the order
WORLD = ("os", "sys", "subprocess", "shutil", "time", "socket", "tempfile", "io", "threading", "signal", "queue",
         "secrets", "importlib", "ctypes", "winreg", "builtins")   # the modules that reach the system
SPEAKING = ("print", "open", "input", "exit", "quit", "__import__")   # the calls that print, open, read the keyboard,
#                                                                       leave or import
REACHING = ("now", "today", "cwd", "home", "exists", "is_file", "is_dir", "is_symlink", "iterdir", "glob", "rglob",
            "stat", "lstat", "resolve", "samefile", "open", "read_text", "read_bytes", "write_text", "write_bytes", "mkdir",
            "touch", "unlink", "rmdir", "rename", "symlink_to", "hardlink_to", "chmod", "lchmod", "readlink", "owner",
            "group", "walk", "is_mount", "is_socket", "is_fifo", "is_block_device", "is_char_device", "expanduser",
            "absolute")                            # a clock, a path on the disk
BARE = ("group",)                                  # a path's methods that take no positional argument, a match's do:
#                                                    `found.group(1)` reads a match, `path.group()` the disk
CLOCKS = ("datetime.now", "datetime.today", "datetime.utcnow", "date.today")   # a clock, named whether called or not
OWN = ("_core", "conductor")                       # beside the library and the skill's folders: the engine alone
ASIDE = ("retired", "__pycache__")                 # what the skill's folder holds that is no module of it
TABLE = {"model": ("model",), "replay": ("model", "rules", "replay"), "rules": ("model", "rules"),
         "faces": ("model", "rules", "faces"), "store": ("model", "store"),
         "acts": ("model", "replay", "rules", "faces", "store", "acts"),
         "verbs": ("model", "replay", "rules", "faces", "store", "acts", "verbs")}   # a layer -> the layers it may
#                                                    import, its own among them, of its domain or of another
EXCEPTIONS = {
    # a store imports the rules of `house`: computed paths without effect (`team_doc`, `journal_of`, `agent_meta`...),
    # the socle every layer imports (C40, Q1 of C53)
    ("store", "house.rules"): "a store reads the paths house.rules computes",
    # the journal's store reads the lines and folds them: the fold is a pure calculation (Q3 of C53)
    ("journal.store", "journal.replay"): "journal/store.py folds the lines it reads",
}
CONDUCTOR = ("instance.valid_slug", "reading.front_matter", "reading.ranged", "Refusal", "Document")   # with
#                                                    `sections.*`: what a pure layer may call on `conductor` (C37)


def allowed(module: str, layer: str, imported_module: str) -> bool:
    """Whether the module `module` (`<domain>.<layer>`) may import `imported_module` by the table of the layers."""
    their = imported_module.split(".")[1]
    if (layer, imported_module) in EXCEPTIONS or (module, imported_module) in EXCEPTIONS:
        return True
    return their in TABLE[layer]


def skill_imports(node, domain: str) -> list[tuple[str, list[str]]]:
    """-> the modules of the skill an import statement reads, each `(<domain>.<layer>, names)` -- or `(<domain>, [])`
    for a domain's folder imported whole --, whatever its form: `from a.b import x`, `import a.b`, `from a import b`
    (a layer named as a module of its folder), and the relative forms, `from . import b` and `from .b import x` in the
    folder `domain`, `from ..a import b` and `from ..a.b import x` from the skill's root. The library, `_core` and
    `conductor` are no module of the skill."""
    if isinstance(node, ast.Import):
        found = []
        for one in node.names:
            parts = one.name.split(".")
            if parts[0] in ORDER and (len(parts) == 1 or len(parts) == 2 and parts[1] in LAYERS):
                found.append((one.name, []))
        return found
    if not isinstance(node, ast.ImportFrom):
        return []
    names = [one.name for one in node.names]
    if node.level == 1:                            # within the module's own folder
        base = [domain, *(node.module.split(".") if node.module else [])]
    elif node.level == 2:                          # from the skill's root
        base = node.module.split(".") if node.module else []
    elif node.level == 0:
        base = (node.module or "").split(".")
    else:
        return []
    if not base or base[0] not in ORDER:
        return []
    if len(base) == 2 and base[1] in LAYERS:       # `from a.b import x`: the module a.b
        return [(".".join(base), names)]
    if len(base) == 1:                             # `from a import b`: the modules a.b its names are
        return [(f"{base[0]}.{one}", [one]) for one in names if one in LAYERS]
    return []


def scopes_of(tree) -> list[tuple[ast.AST, list[ast.AST], int | None]]:
    """-> each scope of a module -- the module, then each function and lambda, an enclosing scope before the scopes
    it holds -- with the nodes it holds itself, those of the functions nested in it left to their own scope, and the
    rank of the scope that encloses it (None for the module). A function's decorators and defaults are its
    enclosing scope's: they are read there."""
    found: list[list] = []

    def own(scope, parent):
        found.append([scope, [], parent])
        rank, held = len(found) - 1, found[-1][1]
        stack = list(ast.iter_child_nodes(scope))
        while stack:
            node = stack.pop()
            held.append(node)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                stack.extend(node.decorator_list if not isinstance(node, ast.Lambda) else [])
                stack.extend(default for default in node.args.defaults + node.args.kw_defaults if default)
                own(node, rank)                    # a nested function: its own scope, within this one
                continue
            stack.extend(ast.iter_child_nodes(node))

    own(tree, None)
    return [tuple(one) for one in found]


def bound_in(scope, held: list[ast.AST]) -> set[str]:
    """-> the names a scope binds itself: its parameters, the names it assigns, loops over, opens `with` or `except`
    under, imports, and the functions and classes it defines -- the names an enclosing scope's alias does not reach."""
    names = set()
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        arguments = scope.args
        names |= {one.arg for one in arguments.posonlyargs + arguments.args + arguments.kwonlyargs}
        names |= {one.arg for one in (arguments.vararg, arguments.kwarg) if one is not None}
    for node in held:
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names |= {(one.asname or one.name).split(".")[0] for one in node.names}
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
    return names


def engine_reached(tree, where: str) -> list[str]:
    """-> what a module of a pure layer reaches of the engine beyond `CONDUCTOR` (C37): each call on `conductor` --
    the parameter, or a name bound to it or to one of its attributes (`c = conductor`, `r = conductor.record`) in the
    function or in a scope that encloses it, unless the function binds that name itself -- whose dotted path
    `CONDUCTOR` does not name, and each import of the engine (`import conductor`, `from conductor… import`), one line each."""
    reached, aliases_of = [], []
    for scope, held, parent in scopes_of(tree):
        aliases = {} if parent is None else {name: path for name, path in aliases_of[parent].items()
                                             if name not in bound_in(scope, held)}   # what the scopes around it bound
        aliases["conductor"] = ""                  # the parameter, wherever it is named
        aliases_of.append(aliases)
        changed = True
        while changed:                             # the names this scope binds to the engine, as many hops as written
            changed = False
            for node in held:
                targets = (node.targets if isinstance(node, ast.Assign) else [node.target]
                           if isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and node.value is not None else [])
                if not targets:
                    continue
                chain, inner = [], node.value
                while isinstance(inner, ast.Attribute):
                    chain.append(inner.attr)
                    inner = inner.value
                if isinstance(inner, ast.Name) and inner.id in aliases:
                    path = ".".join(part for part in [aliases[inner.id], *reversed(chain)] if part)
                    for target in targets:
                        if isinstance(target, ast.Name) and aliases.get(target.id) != path:
                            aliases[target.id] = path
                            changed = True
        seen = set()
        for node in held:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = [one.name for one in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                if not getattr(node, "level", 0) and any(one.split(".")[0] == "conductor" for one in modules):
                    reached.append(f"{where}:{node.lineno} imports {', '.join(modules)}")
            if isinstance(node, ast.Attribute) and id(node) not in seen:
                chain, inner = [], node
                while isinstance(inner, ast.Attribute):
                    seen.add(id(inner))
                    chain.append(inner.attr)
                    inner = inner.value
                if isinstance(inner, ast.Name) and inner.id in aliases:
                    called = ".".join(part for part in [aliases[inner.id], *reversed(chain)] if part)
                    if called not in CONDUCTOR and not called.startswith("sections."):
                        reached.append(f"{where}:{node.lineno} calls conductor.{called}")
    return reached


def strongly_connected(graph: dict) -> list[list[str]]:
    """-> the cycles of a graph of modules: each strongly connected component of more than one module, sorted."""
    index, low, stack, on, found, counter = {}, {}, [], set(), [], [0]

    def visit(node):
        index[node] = low[node] = counter[0]
        counter[0] += 1
        stack.append(node)
        on.add(node)
        for other in sorted(graph.get(node, ())):
            if other not in index:
                visit(other)
                low[node] = min(low[node], low[other])
            elif other in on:
                low[node] = min(low[node], index[other])
        if low[node] == index[node]:
            component = []
            while True:
                other = stack.pop()
                on.discard(other)
                component.append(other)
                if other == node:
                    break
            if len(component) > 1:
                found.append(sorted(component))

    for node in sorted(graph):
        if node not in index:
            visit(node)
    return sorted(found)


def frozen(mark) -> bool:
    """Whether a `dataclass` decorator says `frozen=True`."""
    return isinstance(mark, ast.Call) and any(
        one.arg == "frozen" and isinstance(one.value, ast.Constant) and one.value.value is True for one in mark.keywords)


def imported(node) -> list[tuple[str, int]]:
    """-> the modules an import reads, each (its name, its level)."""
    if isinstance(node, ast.ImportFrom):
        return [(node.module or "", node.level)]
    return [(one.name, 0) for one in node.names]


def dotted(node) -> str:
    """-> the dotted name an attribute reads (`datetime.datetime.now`), "" when it reads no bare name."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    return ".".join([node.id, *reversed(parts)]) if isinstance(node, ast.Name) else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    skill = h.team_module().parent
    strays, folders = [], []
    for path in sorted(skill.iterdir()):
        if path.name in ASIDE or path.name == ENTRY:
            continue
        if not path.is_dir():                      # a document of the skill (SKILL.md) stands beside the entry
            strays += [path.name] if path.suffix == ".py" else []
            continue
        if path.name not in ORDER:
            strays.append(path.name)
            continue
        folders.append(path.name)
        for one in sorted(path.iterdir()):
            if one.name not in ASIDE and one.name != "__init__.py" and (
                    one.suffix != ".py" or one.stem not in LAYERS or one.is_dir()):
                strays.append(f"{path.name}/{one.name}")
        if not (path / "__init__.py").is_file():
            strays.append(f"{path.name}/ without __init__.py")

    backward, effects, thawed, foreign = [], [], [], []
    pure, domain_imports, classes = 0, 0, 0
    files = [skill / ENTRY] + [file for name in folders for file in sorted((skill / name).glob("*.py"))]
    for path in files:
        parts = path.relative_to(skill).parts
        domain, layer = (parts[0], path.stem) if len(parts) > 1 else (None, None)
        where = "/".join(parts)
        pure += layer in PURE
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name, level in imported(node):
                    top = name.split(".")[0]
                    if level or top in ORDER:
                        read = domain if level else top
                        domain_imports += 1
                        if layer in PURE and read in ORDER and domain in ORDER and ORDER.index(read) > ORDER.index(domain):
                            backward.append(f"{where}:{node.lineno} imports {name}")
                    elif top not in sys.stdlib_module_names and top not in OWN and top != "__future__":
                        foreign.append(f"{where}:{node.lineno} imports {name}")
                    if layer in PURE and top in WORLD:
                        effects.append(f"{where}:{node.lineno} imports {name}")
            if layer in PURE:
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in SPEAKING:
                    effects.append(f"{where}:{node.lineno} calls {node.func.id}")
                if isinstance(node, ast.Call) and dotted(node.func) in {f"builtins.{one}" for one in SPEAKING}:
                    effects.append(f"{where}:{node.lineno} calls {dotted(node.func)}")
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in REACHING
                        and not (node.func.attr in BARE and node.args)):
                    effects.append(f"{where}:{node.lineno} calls .{node.func.attr}()")
                raised = node.exc.func if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) else (
                    node.exc if isinstance(node, ast.Raise) else None)
                if (isinstance(raised, ast.Name) and raised.id == "SystemExit") or (
                        isinstance(raised, ast.Attribute) and raised.attr == "SystemExit"):
                    effects.append(f"{where}:{node.lineno} raises SystemExit")
                if isinstance(node, ast.Attribute) and any(
                        f".{dotted(node)}".endswith(f".{clock}") for clock in CLOCKS):
                    effects.append(f"{where}:{node.lineno} names {dotted(node)}")
            if layer == "model" and isinstance(node, ast.ClassDef):
                marks = [one for one in node.decorator_list if "dataclass" in ast.dump(one)]
                classes += bool(marks)
                if marks and not any(frozen(one) for one in marks):
                    thawed.append(f"{where}:{node.lineno} {node.name}")

    # --- the form: the folders of the domains, the modules of the layers, the entry ------------------------------
    missing = [name for name in ORDER if name not in folders]
    defined = []                                   # what the entry defines: its functions, classes and assignments
    for node in ast.parse((skill / ENTRY).read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.append(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            defined += [one.id for target in targets for one in ast.walk(target) if isinstance(one, ast.Name)]
    if not missing and not strays and defined == ["main"]:
        held("the folders are domains, the modules layers", f"the {len(folders)} domain folders of ORDER beside {ENTRY}; "
             f"{len(files) - 1} file(s) in them, each its __init__.py or a layer; the entry defines main alone")
    else:
        failures.append(f"  ✗ the form of the skill        missing={missing} strays={strays} "
                        f"entry defines {len(defined)}: {defined[:8]}{' …' if len(defined) > 8 else ''}")

    # --- the order of the domains on the layers without effect --------------------------------------------------
    if not backward:
        held("no pure layer imports a later domain", f"{domain_imports} import(s) of a domain, {pure} module(s) of "
             "model, replay, rules or faces, none against the order")
    else:
        failures.append(f"  ✗ an import against the order  {backward}")

    # --- model, replay, rules and faces carry no effect ---------------------------------------------------------
    if not effects:
        held("model, replay, rules and faces carry no effect", f"{pure} module(s): no module that reaches the system, "
             "no call that prints, opens, imports or reads the disk, no clock, no exit raised")
    else:
        failures.append(f"  ✗ an effect in a pure layer   {effects}")

    # --- every dataclass of a model is frozen -------------------------------------------------------------------
    if not thawed:
        held("every dataclass of a model is frozen", f"{classes} dataclass(es) in the models, each `frozen=True`")
    else:
        failures.append(f"  ✗ a dataclass not frozen      {thawed}")

    # --- the skill imports the library, its folders and the engine alone ----------------------------------------
    if not foreign:
        held("the skill imports no other package", f"{len(files)} module(s): the standard library, the skill's own "
             "folders, _core and conductor alone")
    else:
        failures.append(f"  ✗ an import outside the skill  {foreign}")

    # --- the table of the layers, the order on store, conductor, the cycles -------------------------------------
    out_of_table, store_backward, calls, graph, late = [], [], [], {}, {}
    for path in files[1:]:                         # the modules of the domains' folders: the entry is no layer
        domain, layer = path.parent.name, path.stem
        if layer not in TABLE:                     # an `__init__.py`
            continue
        module = f"{domain}.{layer}"
        graph.setdefault(module, set())
        tree = ast.parse(path.read_text(encoding="utf-8"))
        first = next((rank for rank, node in enumerate(tree.body)
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))), len(tree.body))
        head = {id(node) for node in tree.body[:first]}   # the statements before the module's first definition
        for node in ast.walk(tree):                # at the head, at the foot or in a body (TL4)
            targets = skill_imports(node, domain)
            if targets and id(node) not in head:   # an import of a domain after the first definition (C12, C48)
                late.setdefault(f"{domain}/{layer}.py", []).append(node.lineno)
            for name, names in targets:
                parts = name.split(".")
                if name != module:
                    graph[module].add(name)
                said = f"{domain}/{layer}.py:{node.lineno} imports {name}" + (f" ({', '.join(names)})" if names else "")
                if len(parts) != 2:            # a domain's folder imported whole: any of its layers within reach
                    out_of_table.append(said)
                    continue
                if not allowed(module, layer, name):
                    out_of_table.append(said)
                if layer == "store" and ORDER.index(parts[0]) > ORDER.index(domain):
                    store_backward.append(said)
        if layer in PURE:
            calls += engine_reached(tree, f"{domain}/{layer}.py")
    if not out_of_table:
        held("the table of the layers holds on the imports", f"{len(graph)} module(s): each import one its layer may "
             f"make, the {len(EXCEPTIONS)} exceptions aside -- {'; '.join(EXCEPTIONS.values())}")
    else:
        failures.append(f"  ✗ imports out of the table of the layers ({len(out_of_table)})\n"
                        + "\n".join(f"      {one}" for one in sorted(out_of_table)))
    if not store_backward:
        held("no store imports a later domain", f"{sum(1 for one in graph if one.endswith('.store'))} store(s), "
             "none against the order")
    else:
        failures.append(f"  ✗ a store imports a later domain ({len(store_backward)})\n"
                        + "\n".join(f"      {one}" for one in sorted(store_backward)))
    if not calls:
        held("a pure layer calls on conductor what C37 permits", "a text reader of the engine, its Refusal, a "
             "Document -- nothing else")
    else:
        failures.append(f"  ✗ a pure layer calls on conductor beyond C37 ({len(calls)})\n"
                        + "\n".join(f"      {one}" for one in sorted(calls)))
    acts = {one: {other for other in edges if other.endswith(".acts")} for one, edges in graph.items()
            if one.endswith(".acts")}
    loops = [("acts", one) for one in strongly_connected(acts)] + [("modules", one) for one in strongly_connected(graph)]
    if not loops:
        held("no cycle of imports", f"{len(acts)} acts.py, {len(graph)} module(s): no cycle between the acts, none "
             "between the modules")
    else:
        failures.append(f"  ✗ cycles of imports ({len(loops)})\n"
                        + "\n".join(f"      {kind}: {', '.join(one)}" for kind, one in loops))
    if not late:
        held("every import of a domain stands at the head", f"{len(graph)} module(s): no import of a domain after "
             "the module's first definition, the entry aside")
    else:
        failures.append(f"  ✗ imports of a domain after the first definition ({len(late)} module(s), "
                        f"{sum(len(one) for one in late.values())} import(s))\n"
                        + "\n".join(f"      {where}: lines {', '.join(map(str, lines))}"
                                    for where, lines in sorted(late.items())))
    return 0
