"""tests.harness -- the product's ONE bench harness: what every scenario repeats.

The bench is the PRODUCT's: this harness at the product root, and the tests of each
AREA living at home under its own `tests/` -- the root's (engine, console, adapters),
`bases/<b>/tests/`, `packages/<p>/tests/` -- same structure, same harness
(tests/README.md writes the structure once). A SCENARIO is one file exposing
`scenario(bench)`: a line of cases over one or several pp ENVIRONMENTS, in declared
order, self-sufficient -- playable alone or in parallel (one process each). An
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
Hermetic: no dependency beyond the engine itself."""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

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
                                   # of a base and nothing of the kit's text (rule 9); the witness
                                   # packages under tests/witness/packages/ join it there
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
    back in deliberately) AND a WIDE serve budget -- landing positions must never
    depend on where the default budget happens to cut a growing doc set."""
    settings_file = meta / "SETTINGS.md"
    if settings_file.is_file():
        text = settings_file.read_text(encoding="utf-8")
        text = text.replace("instructions_fusion: max", "instructions_fusion: none")
        text = text.replace("conduction_effort: medium", "conduction_effort: none")
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
PRINCIPAL = "PP_CONDUCTED_BY_PRINCIPAL"         # the mark of a run its principal conducts


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


def principal(call):
    """-> what `call` returns played under the principal's conduction, in this process."""
    spot = os.environ.get(PRINCIPAL)
    os.environ[PRINCIPAL] = "true"
    try:
        return call()
    finally:
        if spot is None:
            os.environ.pop(PRINCIPAL, None)
        else:
            os.environ[PRINCIPAL] = spot


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

    def write_member(self, front: str = "", body: str = "The witness member.",
                     proc: str = "INFER", name: str = "MEMBER") -> Path:
        """The MEMBER a case needs, written at run time (rule 9): `procs/MEMBER.md`, a proc
        the stand-in's BOOT CALLs at `boot.initialize` through its `attach:` -- the engine's
        own mechanism, never a document added to the stand-in. `front` carries the keys
        the case proves (its laws, its offers, its serve rows, a `character:` a tag
        resolves), `proc` the steps the member plays once called, `name` what `@MEMBER.name`
        resolves to. The catalog is rebuilt, so what the member offers is cataloged."""
        return member_of(self.made, front, body, proc, name)


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
        elsewhere. The keyword arguments are `install.install`'s (`slug`, `doors`, `borrow`)."""
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
    cache = os.environ.get("XDG_CACHE_HOME")
    return (Path(cache) if cache else Path.home() / ".cache") / TMP_PASSES


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


def played(found: list[tuple[str, Path]], serial: bool) -> list[dict]:
    """One PASS of a selection: every scenario in its own process -- or all of them in
    this one, live, under `serial`."""
    pairs = [(name, str(path)) for name, path in found]
    if serial or len(found) == 1:
        return [play(name, path, live=True) for name, path in pairs]
    with ProcessPoolExecutor() as pool:
        return list(pool.map(play, [n for n, _ in pairs], [p for _, p in pairs]))


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
        if repeat > 1:
            rounds = [played(found, serial) for _ in range(repeat)]
            return report_repeat(rounds, time.perf_counter() - started, accused)
        results = played(found, serial)
    return report(results, time.perf_counter() - started, detail=detail or serial, accused=accused)
