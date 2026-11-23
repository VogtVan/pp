"""tests.harness -- the product's ONE bench harness: what every scenario repeats.

The bench is the PRODUCT's: this harness at the product root, and the tests of each
AREA living at home under its own `tests/` -- the root's (engine, console, adapters),
`bases/<b>/tests/`, `packages/<p>/tests/` -- same structure, same harness
(tests/README.md writes the structure once). A SCENARIO is one file exposing
`scenario(bench)`: a line of cases over one or several pp ENVIRONMENTS, in declared
order, self-sufficient -- playable alone or in parallel (one process each), always under
one token of the machine's QUEUE, which every pass of the machine shares. An
ENVIRONMENT is a pp instance installed in a throwaway directory from the engine the
scenario's area stands on -- at the root, a witness source whose base is the bench's
STAND-IN (`tests/witness/kit/`), elsewhere the product's own (rule 9): its documents
are the operator's side, `.sys/state` is pp's alone. A
CONDUCTOR is the engine's in-process facade over an environment -- fresh at every
call, like the console's. A scenario proves behavior, never the wording of a text
(tests/README.md, rules 1-2), and plays in its own process. A scenario is ONE
house and ONE subject, under `SCENARIO_TARGET`; what the scenarios of an area share lives
in a SUPPORT module beside them, `_<name>.py`, never collected, loaded by `support()`
(rule 10). The runner collects every area, names a scenario by its area and path, lints
the structure before any scenario plays: `./pp -test [-serial] [area|name|path ...]`.
The QUEUE lives under the user's cache (`pp-bench-queue/`, or `PP_BENCH_QUEUE`): a token
per scenario, given to the passes in turn, as many as the CPU and memory targets
(`bench.json`, `PP_BENCH_CPU`, `PP_BENCH_MEMORY`) allow at each demand.
Hermetic: no dependency beyond the engine itself."""
from __future__ import annotations

import ast
import builtins
import contextlib
import importlib.util
import io
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import types
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from conductor.core import messages
from conductor import Conductor, Siblings, Member, Refusal, discovery, install, instance, persistence
from conductor import VERSION as ENGINE_VERSION

HERE = Path(__file__).resolve().parent          # <product>/tests -- the root area
SOURCE = HERE.parent                            # the product checkout (engine, kit, packages, template)
ENGINE = SOURCE / "engine"                      # engine/
PRODUCT_ENGINE = ENGINE / "pp.py"               # the engine an environment is installed from
INSTANCE = instance.DIRECTORY                   # the instance directory's name, the engine's own
WITNESS = "kit"                    # the base the ROOT area's environments stand on: the bench's
WITNESSES = HERE / "witness"       # STAND-IN under tests/witness/kit/, taking the product's base's
                                   # name and place in the witness source -- what the engine asks
                                   # of a base and nothing of the kit's text (rule 9) -- never a
                                   # `system/SYS.md`: a case writes the instance's (`system_of`);
                                   # the witness packages under tests/witness/packages/ join it there
KIT_BOUND = ()                     # root sectors standing on the product's kit: none --
                                   # every root scenario proves the engine on the stand-in
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def areas() -> list[tuple[str, Path]]:
    """-> (prefix, tests dir) of every area carrying tests: the root (no prefix),
    the template, each base, each package -- the product's bench, one harness."""
    found = [("", HERE)]
    if (SOURCE / "template" / "tests").is_dir():
        found.append(("template", SOURCE / "template" / "tests"))
    for area in ("bases", "packages"):
        for home in sorted((SOURCE / area).glob("*/tests")):
            found.append((home.parent.name, home))
    return found


# --- the helpers every scenario may need ------------------------------------------

def freshest(meta) -> Path:
    """-> the slot written LAST. Several runs standing side by side is the normal life
    of an instance -- one per conversation -- so a bench says which one it means: the
    run that worked most recently, never the first by the alphabet of its key."""
    return max(persistence.slots(meta), key=lambda slot: slot.stat().st_mtime_ns)


def bench_key(meta) -> str:
    """-> the key of the run a bench's CLI advance carries: the freshest standing."""
    return persistence.run_id_of(freshest(meta))


def pin_step(meta) -> None:
    """The bench rule: step-by-step flows pin `fusion: none` (fusion fixtures opt
    back in deliberately), the laws in full, a body at every CALL, AND a WIDE serve
    budget -- landing positions must never depend on where the default budget happens to cut a growing
    doc set."""
    settings_file = meta / "SETTINGS.md"
    if settings_file.is_file():
        text = settings_file.read_text(encoding="utf-8")
        text = text.replace("instructions_fusion: max", "instructions_fusion: none")
        text = text.replace("conduction_effort: medium", "conduction_effort: none")
        text = text.replace("verbatim_constraints: false", "verbatim_constraints: true")
        text = text.replace("proc_body_serve: once", "proc_body_serve: always")
        text = text.replace("max_harness_tool_output: 25000", "max_harness_tool_output: 60000")
        settings_file.write_text(text, encoding="utf-8")


PLAYABLE = """---
name: X
output: json
proc: |
  INFER
  PICK member
---
the body carries prose, never the procedure
"""


def session_of(meta: Path) -> Path:
    """-> the slot of the run a fixture means: the FRESHEST standing, so an environment
    carrying several runs names the one that worked last; none standing points at a void
    slot (exists() is False)."""
    return freshest(meta) if persistence.slots(meta) else persistence.slot_of(meta, "void")


def na_proof(block) -> str:
    """-> the proof a bench pipes at a checkpoint it does not judge: every code the block
    names said n/a -- a checkpoint has no skip, the bench renders what the engine asks."""
    import json as _json
    return _json.dumps([{"code": code, "evidence": "bench -- nothing to judge", "verdict": "n/a"}
                        for code in (block.judged or ("none",))])


def document(text: str, at: Path | None = None) -> Path:
    path = (at or Path(tempfile.mkdtemp())) / "DOC.md"
    path.write_text(text, encoding="utf-8")
    return path


def load_script(path: Path):
    """A module loaded by PATH -- the bench's own loader for skill scripts and adapters,
    registered in `sys.modules` before it runs, as the console's `_load` does."""
    name = re.sub(r"\W", "_", f"bench_{path.parent.name}_{path.stem}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SKILLS = "bench_skill_"             # what opens the private names a loaded skill's modules stand under
_SKILLS = itertools.count(1)        # one private home per load: two loads never share a name
_ABSENT = object()                  # what a holder that does not hold a name itself is said to hold


class Doubled(Exception):
    """A name of a skill whose reading has no single answer: two of its modules define it, or none defines it
    and two bind it to different objects. `modules` names them, each by its path under the skill's folder."""

    def __init__(self, name: str, modules: list[str]) -> None:
        super().__init__(f"`{name}` has no single answer: {' and '.join(modules)} each bind their own")
        self.name, self.modules = name, modules


def imported(source: str) -> list[tuple[str, str, int, str | None]]:
    """-> what a module's source binds by an `import` at its own level, each (the name bound, the module read,
    its level, the name read there): `import a.b` binds `a` and reads no name, `from a import x as y` binds `y`
    and reads `x`, `from a import *` binds and reads `*`. An import inside a function or a class binds nothing
    of the module."""
    found, nodes = [], [ast.parse(source)]
    while nodes:
        for child in ast.iter_child_nodes(nodes.pop()):
            if isinstance(child, ast.Import):
                found += [(alias.asname or alias.name.partition(".")[0], alias.name, 0, None) for alias in child.names]
            elif isinstance(child, ast.ImportFrom):
                found += [(alias.asname or alias.name, child.module or "", child.level, alias.name)
                          for alias in child.names]
            elif not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                nodes.append(child)
    return found


def exported(module) -> list[str]:
    """-> the names `from <module> import *` binds: its `__all__`, else every name without a leading underscore."""
    return list(getattr(module, "__all__", None) or (name for name in vars(module) if not name.startswith("_")))


class Skill:
    """A skill LOADED -- its entry (`pp-<name>.py`), every module of the packages under its folder and every
    module beside the entry that it imports -- read as ONE object. `skill.<name>` is that name whichever module
    defines it: a name two modules DEFINE is refused (`Doubled`); a name one module imports from another, by
    its name or through a star, is the same definition; a name the skill only imports (`os`) reads when every
    module binds the same object under it, and is refused when two bind different ones.
    `dir(skill)` lists the names it binds, its modules together, as `dir()` of a loaded script does.
    `replaced()` poses a value wherever the skill binds a name, under that name or the one an import gave it; an
    assignment on the object is refused. What took a value at its definition -- an argument's default, a table
    written at a module's level -- keeps it: `replaced()` reaches names, never the copies made of their value.
    The modules stand in `sys.modules` under private names, `bench_skill_<n>_<folder>.<module>`, and the skill's
    own imports resolve to them by the `__import__` of its modules' builtins, at the load and at any later call:
    no bare name of its packages enters `sys.modules`, its folder leaves `sys.path` with the load, and two skills
    whose packages share their names never meet."""

    def __init__(self, entry: Path) -> None:
        entry = entry.resolve()
        vars(self).update(_Skill__folder=entry.parent, _Skill__modules={}, _Skill__reads={},
                          _Skill__home=f"{SKILLS}{next(_SKILLS)}_" + re.sub(r"\W", "_", entry.parent.name),
                          _Skill__builtins={**vars(builtins), "__import__": self.__import})
        standing = list(sys.path)
        try:
            self.__executed("", re.sub(r"\W", "_", entry.stem), entry, None)
            for bare in self.__packaged():
                self.__module(bare)
        finally:                                   # an entry poses its folder on the path: the load takes it back
            sys.path[:] = [one for one in sys.path if one in standing or Path(one).resolve() != entry.parent]

    def __getattr__(self, name: str):
        if name.startswith("_Skill__"):
            raise AttributeError(name)
        return self.__found(name)

    def __dir__(self) -> list[str]:
        """-> the names the skill binds, its modules together: what `dir()` of a loaded script lists."""
        return sorted({name for module in self.__all() for name in vars(module)})

    def __setattr__(self, name: str, value) -> None:
        raise AttributeError(f"`{name}` is replaced by `replaced()`: an assignment on the loaded skill would not "
                             "reach the modules that bind the name")

    @contextlib.contextmanager
    def replaced(self, name: str, value):
        """`value` in the place of `name` for the time of a `with`: posed in the module that defines the name
        and in every module that imports it from there, under its own name or another (`from acts.wake import
        launched as woke`) -- read on each module's syntax, never on the value it holds --, then what each held
        given back. A dotted name (`os.kill`, `Task.of`) is posed on what the skill reads under its head, a
        module it imported or a class: what the holder itself held comes back as it stood (a `staticmethod`
        stays one), what it only inherited leaves it."""
        head, _, leaf = name.rpartition(".")
        if head:
            holder = self
            for part in head.split("."):
                holder = getattr(holder, part)
            getattr(holder, leaf)                  # a name its holder does not answer is not replaced
            places = [(holder, leaf)]
        else:
            places = self.__bindings(name)
        former = [vars(holder).get(bound, _ABSENT) for holder, bound in places]
        for holder, bound in places:
            setattr(holder, bound, value)
        try:
            yield value
        finally:
            for (holder, bound), kept in zip(places, former):
                if kept is _ABSENT:
                    delattr(holder, bound)
                else:
                    setattr(holder, bound, kept)

    def __all(self) -> list:
        """-> the skill's modules, the entry first, then the others by their bare name."""
        return [self.__modules[bare] for bare in sorted(self.__modules)]

    def __found(self, name: str):
        """-> what the skill binds under `name`: its one definition, else the one object its modules import
        under it; refused (`Doubled`) when two modules define it, or when none does and two bind different
        objects."""
        bound = [module for module in self.__all() if name in vars(module)]
        if not bound:
            raise AttributeError(f"the skill under {self.__folder} binds no `{name}`")
        if len(bound) == 1 or (name.startswith("__") and name.endswith("__")):
            return vars(bound[0])[name]
        defined = [module for module in bound if self.__defines(module, name)]
        if len(defined) == 1:
            return vars(defined[0])[name]
        if defined or any(vars(module)[name] is not vars(bound[0])[name] for module in bound):
            raise Doubled(name, [self.__place_of(module) for module in defined or bound])
        return vars(bound[0])[name]

    def __defines(self, module, name: str) -> bool:
        """-> whether that module defines the name it binds: neither read by an import, nor a module."""
        return name not in self.__read_by(module) and not isinstance(vars(module)[name], types.ModuleType)

    def __bindings(self, name: str) -> list[tuple]:
        """-> where the skill binds what `name` reads, each (module, the name bound there): the module that
        defines it -- every module that binds it when none defines it --, then every module that imports it from
        one of those, under that name, under another or through a star."""
        self.__found(name)
        every = self.__all()
        bound = [module for module in every if name in vars(module)]
        places = [(module, name) for module in [one for one in bound if self.__defines(one, name)] or bound]
        for holder, held in places:                # the list grows as it is read: an import of an import
            for module in every:
                for alias, source, level, read in self.__imports(module):
                    if read is None or self.__origin(module, source, level) is not holder:
                        continue
                    if read == held:
                        reached = (module, alias)
                    elif read == "*" and held in exported(holder):
                        reached = (module, held)
                    else:
                        continue
                    if reached not in places:
                        places.append(reached)
        return places

    def __imports(self, module) -> list[tuple[str, str, int, str | None]]:
        """-> the imports of that module's own level, read once from its source."""
        if module.__name__ not in self.__reads:
            file = getattr(module, "__file__", None)
            self.__reads[module.__name__] = imported(Path(file).read_text(encoding="utf-8")) if file else []
        return self.__reads[module.__name__]

    def __read_by(self, module) -> set[str]:
        """-> the names that module binds by an import, those a star reads among them."""
        names = set()
        for bound, source, level, read in self.__imports(module):
            origin = self.__origin(module, source, level) if read == "*" else None
            names |= {bound} if origin is None else set(exported(origin))
        return names

    def __origin(self, module, source: str, level: int):
        """-> the module an import of `module` reads: the skill's own by its bare name, else the interpreter's;
        None when neither holds it."""
        bare = self.__bare(vars(module), source, level)
        if bare and bare in self.__modules:
            return self.__modules[bare]
        return None if level else sys.modules.get(source)

    @staticmethod
    def __bare(scope, name: str, level: int) -> str:
        """-> the bare name an import reads: a relative one counted from the importing module's package, its
        private home dropped."""
        if not level:
            return name
        package = ((scope or {}).get("__package__") or "").split(".")[1:]
        return ".".join(package[:len(package) - level + 1] + ([name] if name else []))

    def __place_of(self, module) -> str:
        """-> that module's path under the skill's folder."""
        at = getattr(module, "__file__", None) or module.__path__[0]
        return Path(at).relative_to(self.__folder).as_posix()

    def __place(self, bare: str) -> tuple[Path | None, Path | None] | None:
        """-> where the skill's folder keeps the module of that bare name, (its file, its package's directory):
        a package by its `__init__.py`, a module by its file, a directory alone a package without a file; None
        when the folder holds none."""
        at = self.__folder.joinpath(*bare.split("."))
        if (at / "__init__.py").is_file():
            return at / "__init__.py", at
        if at.with_name(f"{at.name}.py").is_file():
            return at.with_name(f"{at.name}.py"), None
        return (None, at) if at.is_dir() else None

    def __packaged(self) -> list[str]:
        """-> the bare names of the modules the packages under the folder hold, each package before its modules;
        a file whose name is no identifier is no module."""
        found = set()
        for file in self.__folder.rglob("*.py"):
            parts = file.relative_to(self.__folder).with_suffix("").parts
            parts = parts[:-1] if parts[-1] == "__init__" else parts
            if len(file.relative_to(self.__folder).parts) > 1 and all(part.isidentifier() for part in parts):
                found.update(".".join(parts[:n]) for n in range(1, len(parts) + 1))
        return sorted(found)

    def __module(self, bare: str):
        """-> the skill's module of that bare name (`store.records`), executed at its first demand, its package
        before it."""
        if bare in self.__modules:
            return self.__modules[bare]
        above, _, leaf = bare.rpartition(".")
        package = self.__module(above) if above else None
        place = self.__place(bare)
        if place is None:
            raise ModuleNotFoundError(f"No module named {bare!r}", name=bare)
        module = self.__executed(bare, bare, *place)
        if package is not None:
            setattr(package, leaf, module)
        return module

    def __executed(self, bare: str, private: str, file: Path | None, directory: Path | None):
        """-> one module of the skill executed under its private name, the skill's import in its builtins,
        registered before it runs as `load_script` does."""
        name = f"{self.__home}.{private}"
        if file is None:
            module = types.ModuleType(name)
            module.__path__, module.__package__ = [str(directory)], name
        else:
            spec = importlib.util.spec_from_file_location(
                name, file, submodule_search_locations=[str(directory)] if directory else None)
            module = importlib.util.module_from_spec(spec)
        module.__dict__["__builtins__"] = self.__builtins
        sys.modules[name] = self.__modules[bare] = module
        if file is not None:
            try:
                spec.loader.exec_module(module)
            except BaseException:
                del sys.modules[name], self.__modules[bare]
                raise
        return module

    def __import(self, name: str, globals=None, locals=None, fromlist=(), level: int = 0):
        """The `__import__` of the skill's modules: a name the skill's folder holds is the skill's own module,
        under its private name; any other name goes the interpreter's way."""
        if level:
            name = self.__bare(globals, name, level)
        elif self.__place(name.partition(".")[0]) is None:
            return builtins.__import__(name, globals, locals, fromlist, level)
        module = self.__module(name)
        if not fromlist:
            return self.__modules[name.partition(".")[0]]
        for one in fromlist:                       # `from store import journal`: a module of the package
            if one != "*" and not hasattr(module, one) and self.__place(f"{name}.{one}") is not None:
                self.__module(f"{name}.{one}")
        return module


def load_skill(path: Path) -> Skill:
    """-> the skill whose entry is at `path` (`pp-agent.py`, `pp-team.py`), loaded: ONE object for its entry
    and its modules, whichever module defines a name -- the bench's one loader of a skill of several modules."""
    return Skill(path)


def support(file: str, name: str):
    """-> the SUPPORT module `_<name>.py` beside the scenario at `file`, or above it in its sector
    (rule 10): what the scenarios of one area share -- a witness, the declarations, the factory
    of their houses -- written once, loaded by path as a scenario is, and never collected as one;
    the nearest one wins, and a sector's sub-directories (`conduction/zones/`) share their sector's."""
    here = Path(file).resolve().parent
    for folder in (here, *here.parents):
        candidate = folder / f"_{name}.py"
        if candidate.is_file():
            return load_script(candidate)
        if folder.name == "tests":
            break
    return load_script(here / f"_{name}.py")


def body_of(document: Path) -> str:
    """-> the BODY a document serves (front matter off) -- what a
    mechanics case compares a rendering with, never a literal of the text."""
    text = document.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        text = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    return text.strip()


def kept_document(area: Path, name: str) -> Path:
    """-> the document of an area at the source, by its name -- what a mechanics case
    compares a rendering with, the proc first when a name lives twice (kit/procs/NEXT.md before kit/admin/NEXT.md)."""
    found = [p for p in sorted(area.rglob(f"{name}.md")) if published(p, area)]
    return next((p for p in found if p.parent.name == "procs"), found[0])


def published(path: Path, area: Path) -> bool:
    """-> whether a document under `area` is the PRODUCT's: a bench file (`/tests/`) is
    not, and neither is anything under a dotted directory -- a member's instance
    (`.pp/`, its vendored copies of the product's documents) or a
    projected card (`.claude/`): rule 7, the operator's matter is not the product."""
    relative = path.relative_to(area).parts
    return "tests" not in relative and not any(part.startswith(".") for part in relative)


def steady(rendered: str) -> str:
    """-> the rendering without its OUTPUT HEADING: the heading carries the hour and the
    time since -new, so two renderings of one standing block differ across a second --
    a byte-identity compare reads the rest (le-banc-stable)."""
    return "\n".join(line for line in rendered.splitlines()
                     if not line.startswith("▌ pp · "))


def reaches(rendered: str, text: str, length: int = 120) -> bool:
    """The document's text REACHES a rendering: its opening lines ride whole (a
    budget may cut the rest) -- the mechanics' text-agnostic assert."""
    head = text.strip()[:length]
    return head in rendered


# --- the patterns: what a test of `tests/patterns/` reads of its pattern and of its run ------

PATTERNS = ENGINE / "patterns"                  # engine/patterns/<drawer>/<pattern>/procs
AGENT = "PP_CONDUCTED_RUN"                     # the run a launcher conducts, named to its harness: a
                                                # keyed call on that run carrying it is the agent's


def demos(drawer: str, pattern: str) -> Path:
    """-> the directory of a pattern's demonstration documents."""
    return PATTERNS / drawer / pattern / "procs"


def demonstrated(drawer: str, pattern: str) -> list[str]:
    """-> the names of a pattern's demonstration documents, sorted."""
    return sorted(path.name for path in demos(drawer, pattern).glob("*.md"))


def manifests(drawer: str, pattern: str) -> dict[str, str]:
    """-> a pattern's demonstration manifests, `{file name: text}` sorted by name -- what a
    package declares, read from `manifests/*.yaml` and pinned by `vendor`."""
    folder = PATTERNS / drawer / pattern / "manifests"
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(folder.glob("*.yaml"))}


def fragments(drawer: str, pattern: str) -> dict[str, str]:
    """-> a pattern's demonstration settings fragments, `{file name: text}` sorted by name --
    what a package's `settings/` carries, read from `fragments/*.md` and pinned by `vendor`."""
    folder = PATTERNS / drawer / pattern / "fragments"
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(folder.glob("*.md"))}


def plant(env, drawer: str, pattern: str, names: tuple[str, ...]) -> None:
    """Each named demonstration document written into the house's `procs/`, read from the pattern."""
    for name in names:
        env.write(f"procs/{name}", (demos(drawer, pattern) / name).read_text(encoding="utf-8"))


def law(drawer: str, pattern: str, name: str, code: str) -> str:
    """-> the line of the law `code` as a demonstration document's front matter writes it -- an
    overlay's added law without its `+`, as it renders."""
    text = (demos(drawer, pattern) / name).read_text(encoding="utf-8")
    return next(line.strip().lstrip("+") for line in text.splitlines()
                if line.strip().lstrip("+").startswith(f"{code}  "))


def codes(block) -> list[str]:
    """-> the codes of the laws in force on a block, in order; none without a block."""
    return [one.code for one in block.constraints] if block is not None else []


def closing(rendered: str) -> list[str]:
    """-> the lines from the closing's arrow to the end of a rendering."""
    lines = rendered.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return lines[at:]


def titled(section: str, subject: str = "") -> str:
    """-> the line that opens a section in a rendering: the bar, then the title the engine's list
    says (`conductor.core.messages`), with the subject it serves -- what a scenario looks for among
    `titles()`, never a title typed again."""
    return f"{messages.MARK} {messages.titled(section, subject)}"


def titles(rendered: str) -> list[str]:
    """-> the section headings and the closing arrow of a rendering, in order, the output's heading
    left out."""
    return [line for line in rendered.splitlines()
            if line.startswith(("▌ ", "▶ ")) and not line.startswith("▌ pp · ")]


def traced(env, key: str) -> list[dict]:
    """-> every event of the run's own trace, in order."""
    slot = persistence.slot_of(env.made, key)
    log = json.loads(slot.read_text(encoding="utf-8")).get("log") if slot.is_file() else ""
    path = env.made / persistence.DIRECTORY / (log or "")
    if not log or not path.is_file():
        return []
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def agents(key: str) -> dict[str, str]:
    """-> the variables of the AGENT's call on the run `key`, as its launcher's harness carries them --
    any call without them is the principal's."""
    return {AGENT: key}


def vendor(made, name: str, manifest: str, documents: dict[str, str],
           skills: dict[str, str] | None = None, fragment: str | None = None,
           overlays: dict[str, str] | None = None) -> None:
    """A witness package pinned by hand at `made`, as an install vendors one: its `manifest`,
    its `documents` `{name: text}` under `procs/`, its `overlays` `{name: text}` under
    `overlays/`, its `skills` `{name: code}` each beside its SKILL.md, its settings
    `fragment` as `settings/SETTINGS.md`, and the instance's pins naming it."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for document, text in (overlays or {}).items():
        (root / "overlays").mkdir(exist_ok=True)
        (root / "overlays" / f"{document}.md").write_text(text, encoding="utf-8")
    if fragment is not None:
        (root / "settings").mkdir(exist_ok=True)
        (root / "settings" / "SETTINGS.md").write_text(fragment, encoding="utf-8")
    for document, text in documents.items():
        (root / "procs" / f"{document}.md").write_text(text, encoding="utf-8")
    for skill, code in (skills or {}).items():
        home = root / "skills" / skill
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: a witness\n---\n\n{skill}\n",
                                       encoding="utf-8")
        (home / f"{skill}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


# What the suite costs, measured on 2026-09-20 over its 187 scenarios: median 0.5s,
# mean 2.4s, p90 7.2s, slowest 38.6s, wall 43-48s in parallel for
# 420-500s of CPU. A target says what we refuse to exceed, so it sits well above the
# p90 and well under the slowest: at 20s three scenarios are named, at 4s thirty-one
# were -- and a warning that sounds thirty-one times warns of nothing.
WALL_TARGET = 60.0                              # seconds: the whole bench, in parallel
SCENARIO_TARGET = 20.0                          # seconds: any one scenario
SCENARIO_TOLERANCE = 0.10                       # a scenario within 10 % over its target is not
                                                # an order to split (rule 10): 22 s says nothing
WARNED_SHOWN = 5                                # lines before the rest is one line

# What a scenario holds in memory, measured on 2026-11-07 01:37 over `ui/skills/ui-tasks`
# played alone: `uv run engine/pp.py -test ui-tasks`, the VmRSS of its process tree summed
# from /proc every 50 ms -- a peak of 270 512 kB over 7 processes (ru_maxrss says 60 608 kB,
# the largest process alone). A ui scenario is the heaviest kind: the machine's queue gives
# no token that would take the memory past its target with one scenario more (s.1339 -- 20
# workers froze WSL; s.1567 -- five passes, each sized alone, brought it down on 2026-11-11).
SCENARIO_MEMORY = 270_512 * 1024                # bytes: any one scenario, its children counted
MEMINFO = Path("/proc/meminfo")


def cli(engine: Path, *args: str, cwd: Path | None = None,
        stdin: str | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """The console, exercised as the operator or the agent would -- the bench's own
    interpreter runs the engine (what `uv run` resolves to, without its start-up).
    `stdin` feeds a piped production: `./pp <key> -` reads the step's answer there;
    `env` adds variables to the child's environment (a `PP_HOME` a case addresses
    an instance with -- the bench's own environment stays clean, rule 6)."""
    return subprocess.run([sys.executable, str(engine), *args], capture_output=True,
                          text=True, cwd=cwd, input=stdin,
                          env=None if env is None else {**os.environ, **env})


def printed(env, key: str | None = None, text: str = "said"):
    """The agent's prints, played in process on the environment's run: every production due when
    the call is made is handed by its print call, in the order it is due. -> the block the last
    print moved the run to, None when the run stood there (a value still awaited, the last message
    alone, nothing due). What the block moved to says on `terminal` is due in its turn: the next
    call's."""
    for document in env.conductor(key).prints_due():
        said, block = env.conductor(key).printed(document, text)
        if said == "caught":
            raise AssertionError(f"the print of `{document}` was caught: {block.deviation}")
        if block is not None:
            return block
    return None


def stepped(make, answer: str = "", text: str = "said", by: str = "submit"):
    """ONE move of a run played in process, `make` a factory of fresh conductors on it: the
    productions due are handed by their print call, and the block the last print moved the run to
    comes back; when no print moved it (nothing due, a value still awaited), `submit(answer)` does
    -- the bare call, or the value the step awaits (`by` names the facade's verb: `forward`)."""
    for document in make().prints_due():
        said, block = make().printed(document, text)
        if said == "caught":
            raise AssertionError(f"the print of `{document}` was caught: {block.deviation}")
        if block is not None:
            return block
    return getattr(make(), by)(answer)


def race(engine: Path, calls: list[list[str]], cwd: Path | None = None,
         env: dict[str, str] | None = None) -> list[subprocess.CompletedProcess]:
    """N console calls launched TOGETHER and waited for -- the bench's way to put several
    writers on one run at once; each result as `cli` gives it, in the order of `calls`."""
    started = [subprocess.Popen([sys.executable, str(engine), *args], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, cwd=cwd,
                                env=None if env is None else {**os.environ, **env})
               for args in calls]
    done = []
    for process, args in zip(started, calls):
        out, err = process.communicate()
        done.append(subprocess.CompletedProcess([sys.executable, str(engine), *args],
                                                process.returncode, out, err))
    return done


@contextlib.contextmanager
def holding(path: Path):
    """A lock HELD by the test's own process for the block's time -- the deterministic
    holder a red-before case needs: a console call, in another process, meets it."""
    from conductor.state import lock
    lease = lock.try_(path)
    if lease is None:
        raise RuntimeError(f"{path} is already held")
    try:
        yield lease
    finally:
        lock.release(lease)


# --- the environment: one pp instance, its documents and its state -----------------

@dataclass(frozen=True)
class Env:
    """One pp ENVIRONMENT -- an instance installed in a throwaway directory from the
    product engine. `made` is the instance (`<root>/.pp`), `member` the workspace pp
    sees, `engine` the installed engine a conductor or the console drives. The
    documents under `made` are the operator's side; `.sys/state` is pp's alone."""

    name: str
    made: Path
    member: Member
    engine: Path

    @property
    def root(self) -> Path:
        return self.made.parent

    def siblings(self) -> Siblings:
        return discovery.siblings_around(self.member)

    def conductor(self, key: str | None = None) -> Conductor:
        """A fresh conductor at every call -- what survives, survives on disk."""
        return Conductor(self.member, self.engine, key)

    def write(self, relpath: str, text: str) -> Path:
        """The operator's edit: a document written into the instance."""
        path = self.made / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def read(self, relpath: str) -> str:
        return (self.made / relpath).read_text(encoding="utf-8")

    def session(self) -> Path:
        return session_of(self.made)

    def cli(self, *args: str) -> subprocess.CompletedProcess:
        return cli(self.engine, *args, cwd=self.root)

    def filled(self, record: str, count: int) -> int:
        """A SYNTHETIC record of the instance's store: `count` entries added to `record` in one
        transaction by `store.extend` -- each a body `{"n", "text"}` of a few hundred characters,
        keyed `k<n>` --; the bench never opens the base itself. -> the entries added."""
        from conductor import store
        text = "synthetic entry of the bench, a record filled to measure what a read costs " * 4
        return len(store.of(self.made).extend(
            record, ({"key": f"k{n}", "body": {"n": n, "text": f"{n} {text}"}} for n in range(count))))

    def write_member(self, front: str = "", body: str = "The witness member.",
                     proc: str = "INFER", name: str = "MEMBER") -> Path:
        """The MEMBER a case needs, written at run time (rule 9): `procs/MEMBER.md`, a proc
        the stand-in's BOOT CALLs at `boot.initialize` through its `attach:` -- the engine's
        own mechanism, never a document added to the stand-in. `front` carries the keys
        the case proves (its laws, its offers, its serve rows, a `character:` a tag
        resolves), `proc` the steps the member plays once called, `name` what `@MEMBER.name`
        resolves to. The catalog is rebuilt, so what the member offers is cataloged."""
        return member_of(self.made, front, body, proc, name)

    def write_system(self, production: str = "", behavior: str = "", extra: str = "") -> Path:
        """The instance's SYSTEM LAWS a case needs, written at run time (rule 9): `system_of`."""
        return system_of(self.made, production, behavior, extra)


def system_of(made: Path, production: str = "", behavior: str = "", extra: str = "") -> Path:
    """The instance's SYSTEM LAWS a case needs, written at run time (rule 9): `system/SYS.md`
    at `made`, its laws alone -- one `CODE  text` per line in each section --, `extra` the
    front lines a case of the build's refusals adds. The witness base carries no SYS.md."""
    def section(key: str, laws: str) -> str:
        lines = [line.strip() for line in laws.splitlines() if line.strip()]
        return f"{key}: |\n" + "".join(f"  {line}\n" for line in lines) if lines else ""
    path = made / "system" / "SYS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: SYS\nkind: sys\ndescription: the bench's system laws\n{extra}"
                    f"{section('constraints.production', production)}"
                    f"{section('constraints.behavior', behavior)}---\n", encoding="utf-8")
    return path


def member_of(made: Path, front: str = "", body: str = "The witness member.",
              proc: str = "INFER", name: str = "MEMBER") -> Path:
    """`Env.write_member` for an instance a case installed by hand: the same document,
    written at `made`."""
    from conductor import compiling
    steps = "".join(f"  {line.strip()}\n" for line in proc.splitlines() if line.strip())
    extra = front if not front or front.endswith("\n") else front + "\n"
    path = made / "procs" / "MEMBER.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {name}\nkind: proc\ndescription: the witness member\n"
                    f"attach: boot.initialize\n{extra}proc: |\n{steps}---\n\n{body}\n", encoding="utf-8")
    compiling.build_tools(made)
    return path


@dataclass(frozen=True)
class Town:
    """Several environments installed side by side -- what `siblings_around` sees
    from any of them: instances beside one another, nothing legacy about it."""

    root: Path
    envs: dict[str, Env]

    @property
    def siblings(self) -> Siblings:
        return Siblings(root=self.root, meta_name=INSTANCE)

    def __getitem__(self, name: str) -> Env:
        return self.envs[name]

    def __iter__(self):
        return iter(self.envs.values())


# --- the bench: the count, the environments, the time --------------------------------

class Bench:
    """One bench per scenario: its cases report to it, it reports to the runner."""

    def __init__(self, area: str = "") -> None:
        self.area = area                       # the AREA of the scenario it plays: "" at the root
        self.failures: list[str] = []
        self.refusals = 0
        self.held_count = 0
        self.times: list[tuple[str, float]] = []
        self._temps: list[Path] = []
        self._pristine: dict[tuple, Path] = {}
        self._witness: dict[str, Path] = {}

    def held(self, label: str, detail: str = "") -> None:
        self.held_count += 1
        sep = "" if len(label) < 32 else " "     # a label past the column keeps its gap
        print(f"  ✓ {label:<32}{sep}{detail}")

    def expect(self, code: str, call) -> None:
        """The guard must refuse with the code it names -- anything else reddens."""
        self.refusals += 1
        try:
            call()
            self.failures.append(f"  ✗ {code:<28}ACCEPTED -- the guard does not refuse")
        except Refusal as refusal:
            if refusal.code == code:
                self.held(code, "refused")
            else:
                self.failures.append(f"  ✗ {code:<28}refused as {refusal.code!r}")
        except Exception as error:                                        # noqa: BLE001
            self.failures.append(f"  ✗ {code:<28}raised {type(error).__name__}: {error}")

    def expect_exit(self, code: str, call) -> str:
        """A SCRIPT's refusal: the call must exit non-zero with `code` on stderr --
        the regime of the skills (a package's scripts). -> the stderr."""
        self.refusals += 1
        spot, sys.stderr = sys.stderr, io.StringIO()
        try:
            call()
        except SystemExit as stop:
            text = sys.stderr.getvalue()
            if stop.code and code in text:
                self.held(code, "refused")
            else:
                self.failures.append(f"  ✗ {code:<28}exit {stop.code} -- {text.strip()[:80]}")
            return text
        except Exception as error:                                        # noqa: BLE001
            self.failures.append(f"  ✗ {code:<28}raised {type(error).__name__}: {error}")
            return ""
        finally:
            sys.stderr = spot
        self.failures.append(f"  ✗ {code:<28}ACCEPTED -- the script does not refuse")
        return ""

    def temp(self) -> Path:
        """A throwaway directory the teardown removes."""
        made = Path(tempfile.mkdtemp())
        self._temps.append(made)
        return made

    def source_with(self, base: str) -> Path:
        """A WITNESS source: the product copied under a temp dir (its published parts and
        the root bench's harness -- no repository) with `bases/<base>/` in it -- the
        bench's own base when `tests/witness/<base>/` carries it, in the place of the
        product's of that name (the stand-in `kit`), a copy of the kit renamed otherwise
        (what a scenario moving a real kit's versions needs) -- the one way `package_dir`
        finds a base the product does not carry, and the source an install on that base
        seeds from. Made once per bench; -> its engine."""
        engine = self._witness.get(base)
        if engine is None:
            copy = self.temp() / "witness"
            for part in ("engine", "bases", "packages", "template", "adapters", "tools"):
                shutil.copytree(SOURCE / part, copy / part,
                                ignore=shutil.ignore_patterns("__pycache__", "tests", ".*"))
            (copy / "tests").mkdir()          # the harness alone: a vendored `-test` hands
            shutil.copy(HERE / "harness.py", copy / "tests" / "harness.py")   # over to it
            standing = copy / "bases" / WITNESS
            if self.on_stand_in():            # the ROOT area: the stand-in takes the kit's
                shutil.rmtree(standing)       # place, whatever base the source then adds,
                shutil.copytree(WITNESSES / WITNESS, standing,   # and the witness packages
                                ignore=shutil.ignore_patterns("__pycache__", ".*"))   # join
                for package in sorted((WITNESSES / "packages").glob("*/")):
                    shutil.copytree(package, copy / "packages" / package.name,
                                    ignore=shutil.ignore_patterns("__pycache__", ".*"))
            placed = copy / "bases" / base
            if base != WITNESS:               # another base: the standing one, renamed
                shutil.copytree(standing, placed,
                                ignore=shutil.ignore_patterns("__pycache__", "tests", ".*"))
                manifest = placed / instance.PACKAGE_MANIFEST
                kit_name = str(instance.manifest_of(standing)["name"])
                manifest.write_text(manifest.read_text(encoding="utf-8")
                                    .replace(f"name: {kit_name}\n", f"name: {base}\n", 1),
                                    encoding="utf-8")
            engine = copy / "engine" / "pp.py"
            self._witness[base] = engine
        return engine

    def env(self, name: str, packages: tuple[str, ...] = (), pin: bool = True,
            bare: bool = False, at: Path | None = None, base: str | None = None) -> Env:
        """An ENVIRONMENT on demand: `<temp>/<name>/.pp` installed from the product
        engine, the bench's settings pinned -- created once here, evolving with the
        cases that drive it, torn down at the end. Never shared with another scenario.
        `bare` drops the compiled marble AND the settings document: no standing orders
        ride the blocks, no build receipt guards the boot, the engine's seeds tune it
        -- the engine's MECHANICS alone, what the cases on a bare member prove.
        `base` installs on another base package: the product's own engine when the product
        carries it (`bases/<base>/`), the witness source that carries it otherwise. Left
        out, a ROOT scenario's environment stands on the bench's stand-in for the base
        (`tests/witness/kit/`, installed from the witness source as the role's default,
        the manifest saying no `base:`): the engine's mechanics owe nothing to the kit's
        text (rule 9). Any other area's stands on the product's own kit, as
        `bench.shared()` always does."""
        root = (at or self.temp()) / name
        pristine = self._pristine.get((tuple(packages), base))
        if pristine is None:                       # the install, once per bench and package set
            pristine = self.temp() / ("pristine" if base is None else f"pristine-{base}")
            carried = base is not None and (SOURCE / "bases" / base).is_dir()
            if base is None:
                engine = self.engine()
            else:
                engine = PRODUCT_ENGINE if carried and not self.on_stand_in() else self.source_with(base)
            install.install(engine, pristine / INSTANCE, list(packages), base=base)
            self._pristine[(tuple(packages), base)] = pristine
        shutil.copytree(pristine, root, symlinks=True)   # a copy is an install, for free
        made = root / INSTANCE
        declared = instance.read(made)
        declared["slug"] = instance.kebab(name)    # the environment's own identity
        instance.write(made, declared)
        if bare:
            (made / ".sys" / "system.md").unlink(missing_ok=True)
            (made / "SETTINGS.md").unlink(missing_ok=True)
        elif pin:
            pin_step(made)
        engine = made / ".sys" / "engine" / "pp.py"
        return Env(name=name, made=made, member=discovery.instance_member(engine), engine=engine)

    def install(self, target: Path, packages: list[str] | tuple[str, ...] = (), **kw) -> Path:
        """An instance installed BY HAND at `target` -- what a case does when the install
        itself, or the place, is its subject -- from the engine the scenario's area stands
        on: the witness source's at the root (the stand-in base), the product's own
        elsewhere. The keyword arguments are `install.install`'s (`slug`, `base`, `borrow`)."""
        return install.install(self.engine(), target, list(packages), **kw)

    def engine(self) -> Path:
        """-> the engine the scenario's area installs from: the witness source's at the
        root -- its `bases/kit` the bench's stand-in --, the product's own elsewhere; what
        a case names when it drives the console's own `-install`."""
        return self.source_with(WITNESS) if self.on_stand_in() else PRODUCT_ENGINE

    def on_stand_in(self) -> bool:
        """-> whether this bench's environments stand on the stand-in: every root
        scenario does (`KIT_BOUND` names none that still stands on the kit)."""
        return not self.area

    def source(self) -> Path:
        """-> the ROOT of the source the scenario's area installs from: the witness source
        at the root (its `bases/kit` the stand-in, the witness packages beside the
        product's), the product checkout elsewhere -- what a case copies or reduces when
        it builds a source of its own."""
        return self.engine().parent.parent

    def town(self, names: list[str], packages: tuple[str, ...] = (), pin: bool = True,
                   bare: bool = True) -> Town:
        """Several environments installed side by side in one town -- the siblings a
        neighbourhood case needs; BARE by default: the mechanics cases that grew on
        the monolith prove the engine, not the marble."""
        root = self.temp()
        return Town(root=root, envs={name: self.env(name, packages, pin, bare, at=root) for name in names})

    @contextlib.contextmanager
    def timed(self, name: str):
        started = time.perf_counter()
        try:
            yield
        finally:
            self.times.append((name, time.perf_counter() - started))

    def teardown(self) -> None:
        for made in self._temps:
            shutil.rmtree(made, ignore_errors=True)
        self._temps.clear()


# --- the runner: every scenario, or the named ones -- in parallel, or serial ----------

def scenarios(selection: list[str]) -> list[tuple[str, Path]]:
    """-> (name, path) of the scenario files of every area, sorted -- a name is the
    area's prefix and the path under its tests/ without the suffix (`engine/core`,
    `kit/engine/turn-positions`, `<package>/skills/<script>`); a selection matches a name
    whole, by its last segment, by a leading path or an area (`kit`, `plan`)."""
    found = []
    for prefix, home in areas():
        for path in sorted(home.rglob("*.py")):
            if (path.name in ("harness.py", "__init__.py") or "__pycache__" in path.parts
                    or any(part.startswith("_") for part in path.relative_to(home).parts)
                                                        # a SUPPORT module, or the MATERIAL of its area under a
                                                        # `_<name>/` directory -- a witness skill of a set (rule 10)
                    or WITNESSES in path.parents):      # a witness package's script is a fixture
                continue
            name = path.relative_to(home).with_suffix("").as_posix()
            name = f"{prefix}/{name}" if prefix else name
            if not selection or any(name == one or name.endswith("/" + one) or name.startswith(one + "/")
                                    or f"/{one}/" in f"/{name}/" for one in selection):
                found.append((name, path))
    return found


def area_of(name: str) -> str:
    """-> the AREA a scenario's name opens on: its prefix when an area bears it (`kit`,
    `template`, a package), "" at the root (`engine/…`, `console/…`, `adapters/…`)."""
    prefix = name.split("/", 1)[0]
    return prefix if any(prefix == one for one, _ in areas() if one) else ""


OPT_IN = "opt-in"      # a file under an area's tests/: the area plays only when a selection names it


def by_default(found: list[tuple[str, Path]], selection: list[str]) -> list[tuple[str, Path]]:
    """-> the scenarios a pass plays out of `found`: an area whose tests/ carries an `opt-in`
    file plays only when the selection names it -- the area, a path under it, or one of its
    scenarios by name; a pass without a selection leaves it out, the lint still reads it."""
    opted = {prefix for prefix, home in areas() if prefix and (home / OPT_IN).is_file()}

    def named(name: str) -> bool:
        area = name.split("/", 1)[0]
        return any(one == area or one.startswith(area + "/") or name == one
                   or name.endswith("/" + one) for one in selection)
    return [(name, path) for name, path in found
            if name.split("/", 1)[0] not in opted or named(name)]


PINNED_CHARS, PINNED_WORDS = 40, 6     # a SENTENCE: shorter than that, a literal is a
                                       # form the engine renders, not a document's prose
PINNED_REFUSES = True                  # rule 2: armed, the lint refuses an accused file and
                                       # nothing plays; off, the accused are said on every pass


def _pinned(path: Path) -> set[str]:
    """-> the sentences a test file COMPARES with. Two filters, and both are needed: the
    literal must ride a comparison or an assert -- a held line's wording is prose for the
    reader, never a pin -- and it must be long enough to be a sentence, because the short
    forms (`▌ INSTRUCTION`, `=> tool`, `a reading continues`) are what the ENGINE renders,
    quoted by the card and the cheat sheets because they document it."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        carriers = ([node.left, *node.comparators] if isinstance(node, ast.Compare)
                    else [node.test] if isinstance(node, ast.Assert) else [])
        for one in carriers:
            for maybe in ast.walk(one):
                if (isinstance(maybe, ast.Constant) and isinstance(maybe.value, str)
                        and len(maybe.value.strip()) >= PINNED_CHARS
                        and "\n" not in maybe.value
                        and len(maybe.value.split()) >= PINNED_WORDS):
                    found.add(maybe.value.strip())
    return found


def pinned(found: list[tuple[str, Path]]) -> list[tuple[str, int]]:
    """-> (name, sentences) of every scenario and support module that COMPARES a sentence
    (rule 2): what it compares is a field, an event, a code, a structure or a constant read
    from the module that prints it, never a sentence typed again in the test."""
    accused = [(name, len(_pinned(path))) for name, path in found]
    for prefix, home in areas():
        for path in sorted(home.rglob("_*.py")):
            if "__pycache__" in path.parts or WITNESSES in path.parents or path.name == "__init__.py":
                continue
            shown = f"{prefix}/{path.relative_to(home).as_posix()}" if prefix else path.relative_to(home).as_posix()
            accused.append((shown, len(_pinned(path))))
    return [(name, count) for name, count in accused if count]


def lint(found: list[tuple[str, Path]]) -> list[str]:
    """The structure, checked before any scenario plays (tests/README.md, rule 4): a
    scenario's name is kebab; a `_<name>.py` beside the scenarios is a support module
    and exposes no `scenario(bench)` (rule 10). -> the refusals, empty when the
    structure stands. Armed (`PINNED_REFUSES`), it refuses a sentence compared (rule 2)."""
    refused: list[str] = []
    for name, path in found:
        if not KEBAB.match(path.stem):
            refused.append(f"{name}: a scenario's name is kebab (english, by its subject)")
    for prefix, home in areas():                 # a SUPPORT module (rule 10) plays nothing: what
        for path in sorted(home.rglob("_*.py")):   # the scenarios of its area share, never a case
            if ("__pycache__" in path.parts or WITNESSES in path.parents
                    or path.name == "__init__.py"):
                continue
            if re.search(r"^def scenario\(", path.read_text(encoding="utf-8"), re.M):
                shown = f"{prefix}/{path.relative_to(home).as_posix()}" if prefix else path.relative_to(home).as_posix()
                refused.append(f"{shown}: a `_<name>.py` beside the scenarios is a SUPPORT module (rule 10) "
                               f"-- it exposes no `scenario(bench)`; a scenario is a kebab file of its own")
    if PINNED_REFUSES:
        refused += [f"{name}: compares {count} sentence(s) (rule 2) -- compare a field, an event, "
                    f"a code, a structure or a module's constant" for name, count in pinned(found)]
    return refused

def captured(out: io.StringIO, live: bool):
    """What a scenario writes belongs to its DETAIL, whichever stream it wrote it on:
    both go to one buffer, in the order it wrote them, where the report can hide them,
    render them under `-detail` or bring them back with a ✗. `live` wraps nothing --
    the detail goes out at the fly, which is what that mode is for."""
    if live:
        return contextlib.nullcontext()
    wrapped = contextlib.ExitStack()
    wrapped.enter_context(contextlib.redirect_stdout(out))
    wrapped.enter_context(contextlib.redirect_stderr(out))
    return wrapped


def play(name: str, path: str, live: bool = False) -> dict:
    """One scenario on its own bench -- its output captured unless `live` -- and what
    it leaves: the count, the failures, the time. A scenario that raises reddens;
    the bench never crashes."""
    bench = Bench(area_of(name))
    out = io.StringIO()
    started = time.perf_counter()
    try:
        with captured(out, live):
            module = load_script(Path(path))
            code = module.scenario(bench)
        if code:
            bench.failures.append(f"  ✗ {name:<28}exit {code}")
    except BaseException as error:                                        # noqa: BLE001
        bench.failures.append(f"  ✗ {name:<28}raised {type(error).__name__}: {error}\n"
                              + "".join(traceback.format_exc()))
    finally:
        bench.teardown()
    return {"name": name, "out": out.getvalue(), "held": bench.held_count,
            "refusals": bench.refusals, "failures": bench.failures,
            "seconds": time.perf_counter() - started}


def accused_lines(accused: list[tuple[str, int]]) -> list[str]:
    """-> the warning of rule 2 while the lint is not armed: the count, then the accused,
    five at most and the rest in one line -- said, never failing the count."""
    if not accused:
        return []
    lines = [f"  ⚠ {len(accused)} scenario(s) compare a sentence (rule 2)"]
    lines += [f"  ⚠ {name} -- {count} sentence(s)" for name, count in accused[:WARNED_SHOWN]]
    if len(accused) > WARNED_SHOWN:
        lines.append(f"  ⚠ {len(accused) - WARNED_SHOWN} more compare a sentence")
    return lines


def report(results: list[dict], wall: float, detail: bool = False,
           accused: list[tuple[str, int]] = ()) -> int:
    """The COUNT always, the detail on demand: the table, the targets, the failures and
    the verdict ride every call; the lines a scenario printed wait for `-detail` --
    unless it FAILED, where they come with its ✗."""
    quiet = [one for one in results if one["out"] and not (detail or one["failures"])]
    for one in results:
        if one["out"] and one not in quiet:
            print(one["out"], end="")
    print()
    for one in results:
        print(f"  {one['seconds']:7.1f}s  {one['name']:<40}{one['held']:>4} held  {one['refusals']:>3} refusals")
    held = sum(one["held"] for one in results)
    refusals = sum(one["refusals"] for one in results)
    busy = sum(one["seconds"] for one in results)
    slowest = max(results, key=lambda one: one["seconds"]) if results else None
    print(f"  {wall:7.1f}s  wall ({busy:.1f}s busy) -- {len(results)} scenario(s), {held} held, {refusals} refusals"
          + (f"; slowest {slowest['name']} {slowest['seconds']:.1f}s" if slowest else ""))
    waits = [one["waited"] for one in results if "waited" in one]
    if waits:                                    # what the machine's queue cost the pass
        print("  " + WAIT_SAID.format(longest=max(waits), total=sum(waits)))
    if quiet:
        print(f"  -- {len(quiet)} scenario(s) keep their detail; `-detail` renders it")
    over = [one for one in results if one["seconds"] > SCENARIO_TARGET * (1 + SCENARIO_TOLERANCE)]
    tolerated = f"{SCENARIO_TARGET:.0f}s target (+{SCENARIO_TOLERANCE:.0%} tolerated)"
    for one in over[:WARNED_SHOWN]:              # the target: said, never failing the count
        print(f"  ⚠ {one['name']} took {one['seconds']:.1f}s -- over the {tolerated}")
    if len(over) > WARNED_SHOWN:                 # the list stays readable whatever the target
        print(f"  ⚠ {len(over) - WARNED_SHOWN} more over the {tolerated}")
    if wall > WALL_TARGET and len(results) > 1:
        print(f"  ⚠ the wall took {wall:.1f}s -- over the {WALL_TARGET:.0f}s target")
    for line in accused_lines(list(accused)):
        print(line)
    failures = [line for one in results for line in one["failures"]]
    if failures:
        print("\n".join(failures))
        print(f"\npp: {len(failures)} failure(s).")
        return 1
    print("\npp: green.")
    return 0


def hermetic() -> list[str]:
    """The session's OWN pp variables, out of the bench's environment: a `PP_MARBLE`
    or a `PP_RUN` inherited from the operator's shell makes a throwaway instance boot
    as a wired one. The criterion is the PREFIX -- what pp exposes wears its name --
    and the drop happens at the bench's entry, so every child inherits it, whatever
    launches it. -> the names dropped, in order."""
    dropped = sorted(name for name in os.environ if name.startswith("PP_"))
    for name in dropped:
        os.environ.pop(name, None)
    return dropped


UV_PASSES = "pp-bench-uv"            # beside the user's uv cache: one directory per pass of the bench
UV_ENVIRONMENTS = "environments-v2"   # the bucket where uv builds one environment per script path


TMP_PASSES = "pp-bench-tmp"           # under the user's cache: one directory per pass, its houses and their temp files
TMP_VARIABLES = ("TMPDIR", "TEMP", "TMP")   # where `tempfile` and every child look for their temp, on any system


def tmp_home() -> Path:
    """-> where the passes put their temp: `pp-bench-tmp/` under the user's cache (`XDG_CACHE_HOME`, else
    `~/.cache`), on disk."""
    return user_cache() / TMP_PASSES


@contextlib.contextmanager
def tmp_pass():
    """The pass's OWN temp, on disk. Every house of the bench is installed under the temp, and the system's
    may be a tmpfs held in RAM (WSL's /tmp: 5.9 GB), which a whole pass fills until the machine falls. The
    pass's directory stands under `tmp_home()`; `TMPDIR`, `TEMP` and `TMP` name it for every child, and
    `tempfile` writes there in this process; it leaves with the pass, the environment given back. A pass
    directory whose bench died is swept at the next entry; any other name there is left alone. -> the
    pass's temp."""
    home = tmp_home()
    home.mkdir(parents=True, exist_ok=True)
    for stale in home.iterdir():
        pid = stale.name.split("-", 1)[0]
        if stale.is_dir() and "-" in stale.name and pid.isdigit() and not alive(int(pid)):
            shutil.rmtree(stale, ignore_errors=True)
    mine = Path(tempfile.mkdtemp(prefix=f"{os.getpid()}-", dir=home))
    inherited = {name: os.environ.get(name) for name in TMP_VARIABLES}
    kept = tempfile.tempdir
    for name in TMP_VARIABLES:
        os.environ[name] = str(mine)
    tempfile.tempdir = str(mine)
    try:
        yield mine
    finally:
        for name, value in inherited.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        tempfile.tempdir = kept
        shutil.rmtree(mine, ignore_errors=True)


def uv_cache() -> Path | None:
    """-> the user's uv cache (`uv cache dir`), None when uv is not on the PATH."""
    if shutil.which("uv") is None:
        return None
    found = subprocess.run(["uv", "cache", "dir"], capture_output=True, text=True)
    return Path(found.stdout.strip()) if found.returncode == 0 and found.stdout.strip() else None


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@contextlib.contextmanager
def uv_pass():
    """The pass's OWN uv cache. uv builds one environment per script PATH, and every house of the bench
    is a new path: in the user's cache those environments stay forever. The pass's cache stands beside
    the user's, on its filesystem -- uv moves a wheel it unpacks into the cache by a rename --, every
    bucket of it a symlink to the user's (the wheels shared, a new one downloaded once for all) but
    `environments-v2/`, its own; `UV_CACHE_DIR` names it for every child, and it leaves with the pass,
    the user's buckets untouched. A pass directory whose bench died is swept at the next entry. Without
    uv, nothing is set. -> the pass's cache, or None."""
    user = uv_cache()
    if user is None or not user.is_dir():
        yield None
        return
    home = user.parent / UV_PASSES
    home.mkdir(parents=True, exist_ok=True)
    for stale in home.iterdir():
        pid = stale.name.split("-", 1)[0]
        if pid.isdigit() and not alive(int(pid)):
            shutil.rmtree(stale, ignore_errors=True)
    mine = Path(tempfile.mkdtemp(prefix=f"{os.getpid()}-", dir=home))
    for one in user.iterdir():
        if one.name != UV_ENVIRONMENTS and not one.name.startswith("."):
            (mine / one.name).symlink_to(one)
    (mine / UV_ENVIRONMENTS).mkdir()
    inherited = os.environ.get("UV_CACHE_DIR")
    os.environ["UV_CACHE_DIR"] = str(mine)
    try:
        yield mine
    finally:
        if inherited is None:
            os.environ.pop("UV_CACHE_DIR", None)
        else:
            os.environ["UV_CACHE_DIR"] = inherited
        shutil.rmtree(mine, ignore_errors=True)


# --- the machine's queue: one token per scenario, shared by every pass ---------------
#
# Every pass of the machine plays its scenarios under the tokens of ONE queue, a directory
# under the user's cache: a state file written under the file lock of the same directory, no
# service process. A pass enters the RING with its scenarios still waiting and leaves it when
# none is left; a free token goes to the next pass of the ring, from the cursor, a process of
# which asks for one now -- arrival order, one turn each, a pass whose processes all hold their
# token passed over. The bound is judged at every demand, the
# smallest winning: the CPU target's share of the cores in play, none while the machine's CPU
# over the last second is past that target, none when one scenario more would take the
# memory past its target -- and one whenever none is in play, so that a load from elsewhere
# slows the bench down to one scenario at a time and never stops it. A token or a place in
# the ring whose process is gone is taken back at every reading of the state, and the demand
# of a pass that is gone is never served: its orphan worker stops without playing.

QUEUE_HOME = "pp-bench-queue"          # under the user's cache, beside the passes' temp
QUEUE_SETTINGS = "bench.json"          # the machine's targets: {"cpu": 80, "memory": 80}
QUEUE_STATE = "state.json"             # the ring, the cursor, the tokens, the last CPU reading
QUEUE_LOCK = "lock"                    # the file the state is read and written under
QUEUE_TARGETS = {"cpu": 80.0, "memory": 80.0}   # percent: when bench.json and the variables say nothing
QUEUE_VARIABLES = {"cpu": "PP_BENCH_CPU", "memory": "PP_BENCH_MEMORY"}   # a pass's own targets
QUEUE_POLL = 0.05                      # seconds between two demands of a scenario waiting for its token
QUEUE_ASKING = 4 * QUEUE_POLL          # seconds a demand keeps its pass in the turn: a process asking
                                       # renews it at every poll, one giving its token back poses it
CPU_WINDOW = 1.0                       # seconds: the CPU reading a demand compares, renewed past it
CPU_STALE = 10.0                       # seconds: an older reading measures no current load
STAT = Path("/proc/stat")
PROCESSES = Path("/proc")

QUEUE_SAID = ("the pass plays each scenario under a token of the machine's queue ({home}): {tokens} at once "
              "at most, the pass's CPU target of {cpu:g}% of {cores} cores; fewer while the machine's CPU is "
              "busier than that target or one scenario more would take the machine's memory past the pass's "
              "memory target of {memory:g}%, never fewer than one -- {playing} in use now, {passes} other "
              "pass(es) waiting")
WAIT_SAID = "{longest:7.1f}s  the longest wait of a scenario for its token ({total:.1f}s waited by all of them together)"


@dataclass(frozen=True)
class Queue:
    """The machine's queue as one pass plays it: its directory and this pass's targets, in
    percent -- `cpu` of the cores (the tokens at most, and the load past which none is given),
    `memory` of the machine's memory, one scenario more counted -- and the CPU counters it reads
    the load from, /proc/stat unless `PP_BENCH_STAT` names others."""
    home: Path
    cpu: float
    memory: float
    stat: Path = STAT


def user_cache(environ=None) -> Path:
    """-> the user's cache: `XDG_CACHE_HOME`, else `~/.cache`."""
    cache = (os.environ if environ is None else environ).get("XDG_CACHE_HOME")
    return Path(cache) if cache else Path.home() / ".cache"


def queue_of(environ) -> Queue:
    """-> the queue a pass plays on, read from `environ` before `hermetic()` drops the pp
    variables: `PP_BENCH_QUEUE` names its directory, else `pp-bench-queue/` under the user's
    cache; the targets are `bench.json`'s there, `PP_BENCH_CPU` and `PP_BENCH_MEMORY` override
    them for this pass alone, `QUEUE_TARGETS` when nothing says -- a target that is no positive
    number is ignored; `PP_BENCH_STAT` names the CPU counters the pass reads its load from."""
    named = environ.get("PP_BENCH_QUEUE")
    home = Path(named) if named else user_cache(environ) / QUEUE_HOME
    targets = dict(QUEUE_TARGETS)
    try:
        written = json.loads((home / QUEUE_SETTINGS).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        written = {}
    for key, variable in QUEUE_VARIABLES.items():
        for value in ((written if isinstance(written, dict) else {}).get(key), environ.get(variable)):
            try:
                number = float(value) if value is not None and not isinstance(value, bool) else 0.0
            except (TypeError, ValueError):
                number = 0.0
            if number > 0:
                targets[key] = number
    counters = environ.get("PP_BENCH_STAT")
    return Queue(home=home, cpu=targets["cpu"], memory=targets["memory"],
                 stat=Path(counters) if counters else STAT)


def memory() -> tuple[int, int] | None:
    """-> the machine's memory and what it can still give, in bytes (`MemTotal`,
    `MemAvailable` of /proc/meminfo), None when it cannot be read -- off Linux, say."""
    found = {}
    try:
        for line in MEMINFO.read_text(encoding="utf-8").splitlines():
            name, _, rest = line.partition(":")
            if name in ("MemTotal", "MemAvailable"):
                found[name] = int(rest.split()[0]) * 1024
    except (OSError, ValueError, IndexError):
        return None
    if len(found) < 2:
        return None
    return found["MemTotal"], found["MemAvailable"]


def cpu_times(stat: Path = STAT) -> tuple[int, int] | None:
    """-> the machine's CPU time so far and its idle part, in ticks (the `cpu` line of
    `stat`, /proc/stat), None when it cannot be read."""
    try:
        fields = stat.read_text(encoding="utf-8").splitlines()[0].split()
        ticks = [int(one) for one in fields[1:9]]
    except (OSError, ValueError, IndexError):
        return None
    if fields[0] != "cpu" or len(ticks) < 5:
        return None
    return sum(ticks), ticks[3] + ticks[4]               # idle and iowait


def ceiling(queue: Queue, cores: int) -> int:
    """-> the tokens the machine gives at most: the CPU target's share of the cores, one at least."""
    return max(1, int(queue.cpu * cores / 100 + 1e-9))


def allowance(queue: Queue, cores: int, playing: int, busy: float | None,
              held: tuple[int, int] | None, scenario: int = SCENARIO_MEMORY) -> int:
    """-> the tokens the queue may give now, the smallest bound winning: the ceiling less the
    `playing` tokens; none while `busy`, the share of the machine's CPU over the last second,
    is past the CPU target; none when `held` -- the memory and what it can still give -- would
    pass the memory target with one scenario more; one when none is in play, whatever the load.
    A reading that is None bounds nothing."""
    room = ceiling(queue, cores) - playing
    if busy is not None and busy * 100 > queue.cpu:
        room = 0
    if held is not None:
        total, available = held
        if total - available + scenario > queue.memory / 100 * total:
            room = 0
    if playing == 0:
        room = max(room, 1)
    return max(0, room)


def identity(pid: int) -> str | None:
    """-> what tells process `pid` from a later one of the same number -- its start time, field
    22 of /proc/<pid>/stat --, "" where /proc is not there and the process lives, None when it
    is gone."""
    if not PROCESSES.is_dir():
        return "" if alive(pid) else None
    try:
        stat = (PROCESSES / str(pid) / "stat").read_text(encoding="utf-8")
    except OSError:
        return None
    fields = stat.rpartition(")")[2].split()
    return fields[19] if len(fields) > 19 else ""


def _living(pid: int, since: str | None) -> bool:
    now = identity(pid)
    return now is not None and (not since or not now or now == since)


@contextlib.contextmanager
def _locked(queue: Queue):
    """The queue's state, read and written under its file lock alone: the dead taken back at
    every reading, the state written back when it moved. -> the state, to read or change."""
    queue.home.mkdir(parents=True, exist_ok=True)
    with open(queue.home / QUEUE_LOCK, "a+b") as lock:
        _lock(lock, True)
        try:
            path = queue.home / QUEUE_STATE
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                state = None
            if not isinstance(state, dict):
                state = {}
            read = json.dumps(state, sort_keys=True)
            for key, empty in (("seq", 0), ("cursor", 0), ("ring", []), ("tokens", [])):
                state.setdefault(key, empty)
            state["tokens"] = [one for one in state["tokens"]
                               if _living(one["pid"], one["since"]) and _living(one["pass"], one["pass_since"])]
            state["ring"] = [one for one in state["ring"] if _living(one["pass"], one["since"])]
            yield state
            if json.dumps(state, sort_keys=True) != read:
                written = path.with_name(f"{QUEUE_STATE}.{os.getpid()}")
                written.write_text(json.dumps(state), encoding="utf-8")
                os.replace(written, path)
        finally:
            _lock(lock, False)


def _lock(handle, taken: bool) -> None:
    try:
        import fcntl
    except ImportError:                                  # Windows: the first byte, the same promise
        import msvcrt
        handle.seek(0)
        if not taken:
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            return
        while True:
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                time.sleep(QUEUE_POLL)
    fcntl.flock(handle, fcntl.LOCK_EX if taken else fcntl.LOCK_UN)


def snapshot(queue: Queue) -> dict:
    """-> the queue's state as it stands, the dead taken back."""
    with _locked(queue) as state:
        return json.loads(json.dumps(state))


def _busy(state: dict, now: float, stat: Path) -> float | None:
    """-> the share of the machine's CPU busy since the reading the state keeps of `stat`,
    renewed when older than `CPU_WINDOW`; None without a recent reading to compare."""
    kept = state.get("cpu")
    if kept and kept.get("stat") != str(stat):
        kept = None                                      # the counters of another source compare nothing
    if kept and 0 <= now - kept["at"] < CPU_WINDOW:
        return kept["busy"]
    read = cpu_times(stat)
    if read is None:
        return None
    total, idle = read
    busy = None
    if kept and now - kept["at"] <= CPU_STALE and total > kept["total"]:
        busy = 1 - (idle - kept["idle"]) / (total - kept["total"])
    state["cpu"] = {"stat": str(stat), "at": now, "total": total, "idle": idle, "busy": busy}
    return busy


def enter(queue: Queue, owner: tuple[int, str | None], waiting: int) -> None:
    """The pass `owner` -- its pid and identity -- enters the ring with its scenarios waiting."""
    with _locked(queue) as state:
        state["ring"] = [one for one in state["ring"] if one["pass"] != owner[0]]
        state["seq"] += 1
        state["ring"].append({"pass": owner[0], "since": owner[1], "seq": state["seq"],
                              "waiting": waiting, "arrived": time.time()})


def leave(queue: Queue, owner: tuple[int, str | None]) -> None:
    """The pass `owner` out of the ring, and every token of its own given back."""
    with _locked(queue) as state:
        state["ring"] = [one for one in state["ring"] if one["pass"] != owner[0]]
        state["tokens"] = [one for one in state["tokens"] if one["pass"] != owner[0]]


def _asking(entry: dict, now: float) -> bool:
    """-> whether a process of the pass at `entry` asks for a token now."""
    return any(now - one[2] <= QUEUE_ASKING for one in entry.get("asking", []))


def _asks(entry: dict, me: tuple[int, str | None], now: float) -> None:
    """The demand of `me` on its pass's place in the ring, renewed."""
    entry["asking"] = [one for one in entry.get("asking", [])
                       if one[0] != me[0] and now - one[2] <= QUEUE_ASKING] + [[me[0], me[1], now]]


def _granted(state: dict, queue: Queue, owner: tuple[int, str | None],
             me: tuple[int, str | None]) -> bool | None:
    """One demand of `me`, a scenario of the pass `owner`: the token when the turn is its pass's
    and the bound allows one -- the cursor moved past the pass, the pass out of the ring once
    nothing of it waits. The turn goes from the cursor to the next pass a process of which asks
    now: a pass whose processes all hold their token is passed over. -> None when the pass is
    gone: its demand is never served."""
    if not _living(*owner):
        return None
    now = time.time()
    entry = next((one for one in state["ring"] if one["pass"] == owner[0]), None)
    if entry is None:                                    # a pass the ring lost: it enters again
        state["seq"] += 1
        entry = {"pass": owner[0], "since": owner[1], "seq": state["seq"], "waiting": 1, "arrived": now}
        state["ring"].append(entry)
    entry["waiting"] = max(1, entry["waiting"])          # a demand is a scenario waiting
    _asks(entry, me, now)
    asking = sorted((one for one in state["ring"] if one["waiting"] > 0 and _asking(one, now)),
                    key=lambda one: one["seq"])
    turn = next((one for one in asking if one["seq"] > state["cursor"]), asking[0])
    if turn is not entry:
        return False
    if allowance(queue, os.cpu_count() or 1, len(state["tokens"]), _busy(state, now, queue.stat),
                 memory()) < 1:
        return False
    state["tokens"].append({"pid": me[0], "since": me[1], "pass": owner[0], "pass_since": owner[1],
                            "taken": now})
    entry["waiting"] -= 1
    entry["asking"] = [one for one in entry["asking"] if one[0] != me[0]]
    state["cursor"] = entry["seq"]
    if entry["waiting"] <= 0:
        state["ring"].remove(entry)
    return True


def take(queue: Queue, owner: tuple[int, str | None]) -> float | None:
    """A token for this process, a scenario of the pass `owner`: one demand every `QUEUE_POLL`
    until it is given. -> the seconds waited, None when the pass is gone."""
    me = (os.getpid(), identity(os.getpid()))
    started = time.perf_counter()
    while True:
        with _locked(queue) as state:
            granted = _granted(state, queue, owner, me)
        if granted is None:
            return None
        if granted:
            return time.perf_counter() - started
        time.sleep(QUEUE_POLL)


def give_back(queue: Queue, owner: tuple[int, str | None]) -> None:
    """The token of this process, back to the queue: while its pass still waits, the process
    asks again at once, so its pass keeps its turn."""
    me = (os.getpid(), identity(os.getpid()))
    with _locked(queue) as state:
        state["tokens"] = [one for one in state["tokens"] if one["pid"] != me[0]]
        entry = next((one for one in state["ring"] if one["pass"] == owner[0]), None)
        if entry is not None and entry["waiting"] > 0:
            _asks(entry, me, time.time())


def queued(name: str, path: str, queue: Queue, owner: tuple[int, str | None], live: bool = False) -> dict:
    """One scenario under one token: taken before `play`, given back after, the wait in its result.
    A worker whose pass is gone stops there, playing nothing."""
    waited = take(queue, owner)
    if waited is None:
        os._exit(0)
    try:
        result = play(name, path, live)
    finally:
        give_back(queue, owner)
    result["waited"] = waited
    return result


def queue_said(queue: Queue) -> str:
    """-> the line a pass opens with: the machine's tokens, those in play, the passes ahead."""
    state = snapshot(queue)
    cores = os.cpu_count() or 1
    return QUEUE_SAID.format(home=queue.home, tokens=ceiling(queue, cores), cpu=queue.cpu, cores=cores,
                             memory=queue.memory, playing=len(state["tokens"]), passes=len(state["ring"]))


def played(found: list[tuple[str, Path]], serial: bool, queue: Queue) -> list[dict]:
    """One PASS of a selection on the machine's queue: every scenario under one token, in its
    own process -- the pool never wider than the queue's ceiling -- or all of them in this one,
    live, under `serial` or alone. The pass enters the ring with its scenarios and leaves it
    at its end, whatever ends it."""
    pairs = [(name, str(path)) for name, path in found]
    owner = (os.getpid(), identity(os.getpid()))
    enter(queue, owner, len(pairs))
    try:
        if serial or len(pairs) == 1:
            return [queued(name, path, queue, owner, live=True) for name, path in pairs]
        width = min(len(pairs), ceiling(queue, os.cpu_count() or 1))
        with ProcessPoolExecutor(max_workers=width) as pool:
            return list(pool.map(queued, [n for n, _ in pairs], [p for _, p in pairs],
                                 itertools.repeat(queue), itertools.repeat(owner)))
    finally:
        leave(queue, owner)


def report_repeat(rounds: list[list[dict]], wall: float,
                  accused: list[tuple[str, int]] = ()) -> int:
    """Several passes of one selection, compared: a scenario whose count or verdict MOVED
    from one pass to the next is named with what it held, pass by pass -- the rest holds
    in one line. A pass that failed says so; a count that moved is a red of its own, which
    is the shape a load-dependent scenario takes when it does not fail outright."""
    names = [one["name"] for one in rounds[0]]
    moved, failed = [], []
    for name in names:
        seen = [next((one for one in lap if one["name"] == name), None) for lap in rounds]
        marks = [(one["held"], one["refusals"], bool(one["failures"])) if one else None
                 for one in seen]
        if any(one is not None and one[2] for one in marks):
            failed.append(name)
        if len(set(marks)) > 1:
            moved.append((name, [f"{one[0]} held" if one else "absent" for one in marks]))
    for lap, results in enumerate(rounds, 1):  # the FIRST pass that failed says why
        spoken = [one for one in results if one["failures"]]
        if spoken:
            print(f"pp: pass {lap} of {len(rounds)} --")
            for one in spoken:
                if one["out"]:
                    print(one["out"], end="")
                print("\n".join(one["failures"]))
            break
    print(f"\n  {wall:7.1f}s  {len(rounds)} pass(es) of {len(names)} scenario(s)"
          f" -- {sum(one['held'] for one in rounds[0])} held at the first")
    for line in accused_lines(list(accused)):
        print(line)
    for name, marks in moved:
        print(f"  ✗ {name:<40}{' / '.join(marks)}")
    if moved or failed:
        print(f"\npp: {len(moved)} scenario(s) moved, {len(failed)} failed -- the bench is "
              f"not steady.")
        return 1
    print("\npp: steady.")
    return 0


def run(selection: list[str] | None = None) -> int:
    """`./pp -test [-serial|-detail] [-repeat <n>] [area|name|path ...]` -- every scenario of every area
    or the selected ones: the structure linted first, every scenario in its own
    process; `-serial` plays
    them one after the other in this process, output live, and `-detail` renders the
    lines the scenarios printed instead of the count alone, and `-repeat <n>` plays the
    selection n times and names whatever moved between the passes."""
    print(f"pp: bench on {PRODUCT_ENGINE} -- conductor {ENGINE_VERSION}")
    queue = queue_of(os.environ)                 # the pass's own pp variables, read before the drop
    dropped = hermetic()
    if dropped:
        print(f"pp: the bench drops {', '.join(dropped)} -- a throwaway instance boots on its own")
    selection = list(selection or [])
    serial = "-serial" in selection
    detail = "-detail" in selection
    repeat = 1
    if "-repeat" in selection:
        at = selection.index("-repeat")
        laps = selection[at + 1] if at + 1 < len(selection) else ""
        if not laps.isdigit() or int(laps) < 1:
            print("pp: -repeat takes a number of passes -- `./pp -test <selection> -repeat 10`")
            return 2
        repeat = int(laps)
        del selection[at:at + 2]
    selection = [one for one in selection if one not in ("-serial", "-detail")]
    found = by_default(scenarios(selection), selection)
    if not found:
        print(f"pp: no scenario answers to {' '.join(selection) or 'the bench'} -- "
              f"the names are the files under {HERE} and every area's tests/")
        return 2
    refused = lint(scenarios([]))
    if refused:
        print("pp: the bench's structure refuses -- nothing played (tests/README.md):")
        print("\n".join(f"  ✗ {one}" for one in refused))
        return 2
    accused = [(name, count) for name, count in pinned(scenarios([]))
               if any(name == one for one, _ in found)]
    started = time.perf_counter()
    with tmp_pass() as temp, uv_pass():
        print(f"pp: the pass writes its houses under {temp}")
        print(f"pp: {queue_said(queue)}")
        if repeat > 1:
            rounds = [played(found, serial, queue) for _ in range(repeat)]
            return report_repeat(rounds, time.perf_counter() - started, accused)
        results = played(found, serial, queue)
    return report(results, time.perf_counter() - started, detail=detail or serial, accused=accused)
