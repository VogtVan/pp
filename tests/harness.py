"""tests.harness -- the product's ONE bench harness: what every scenario repeats.

The bench is the PRODUCT's: this harness at the product root, and the tests of each
AREA living at home under its own `tests/` -- the root's (engine, console, adapters),
`kit/tests/`, `packages/<p>/tests/`, `template/tests/` -- same structure, same harness
(tests/README.md writes the structure once). A SCENARIO is one file exposing
`scenario(bench)`: a line of cases over one or several pp ENVIRONMENTS, in declared
order, self-sufficient -- playable alone or in parallel (one process each). An
ENVIRONMENT is a pp instance installed in a throwaway directory from the product
engine: its documents are the operator's side, `.sys/state` is pp's alone. A
CONDUCTOR is the engine's in-process facade over an environment -- fresh at every
call, like the console's. The tests that keep a document's TEXT live under a
`body/` root, one file named as the document, and share ONE environment the harness
holds (`bench.shared()`), never mutated, played in one process. The runner collects
every area, names a scenario by its area and path, lints the structure before any
scenario plays: `./pp -test [-serial] [area|name|path ...]`. Hermetic: no dependency
beyond the engine itself."""
from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
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
SYSTEM_PACKAGES = ()               # the shared environment is KIT-ONLY: a scenario that
                                   # needs a package pins its own env (KPS17)
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DOCUMENT_NAME = re.compile(r"^[A-Z][A-Z0-9_-]*$")


def areas() -> list[tuple[str, Path]]:
    """-> (prefix, tests dir) of every area carrying tests: the root (no prefix),
    the kit, each package, the template -- the product's bench, one harness."""
    found = [("", HERE)]
    for name, home in (("kit", SOURCE / "kit"), ("template", SOURCE / "template")):
        if (home / "tests").is_dir():
            found.append((name, home / "tests"))
    for package in sorted((SOURCE / "packages").glob("*/tests")):
        found.append((package.parent.name, package))
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


def quiet_improve(meta) -> None:
    """The seeded switch, flipped off -- for fixtures whose subject is not the reflex."""
    settings_doc = meta / "SETTINGS.md"
    settings_doc.write_text(settings_doc.read_text(encoding="utf-8")
                            .replace("workspace_improvement: true",
                                     "workspace_improvement: false"), encoding="utf-8")


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


REFUSED = [
    ("front-matter-missing", "no front matter at all\n"),
    ("front-matter-unterminated", "---\nname: X\nproc: |\n  PICK x\n"),
    ("procedure-undeclared", "---\nname: X\n---\nno proc key anywhere\n"),
    ("unknown-keyword", "---\nname: X\nproc: |\n  DANCE badly\n---\n"),
    ("options-empty", "---\nname: X\nproc: |\n  PICK x\n---\n"),
    ("instruction-malformed", "---\nname: X\nproc: |\n  SERVE READ.md ^ memory\n---\n"),
    ("front-matter-invalid", "---\nname: [unclosed\nproc: |\n  INFER\n---\n"),
    ("front-matter-invalid", "---\n- a\n- list\n---\n"),
]


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


def body_of(document: Path) -> str:
    """-> the BODY a document serves (front matter off) -- what a
    mechanics case compares a rendering with, never a literal of the text."""
    text = document.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        text = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    return text.strip()


def kept_document(area: Path, name: str) -> Path:
    """-> the document a body test keeps, by its name, under its area at the source --
    the proc first when a name lives twice (kit/procs/NEXT.md before kit/admin/NEXT.md)."""
    found = [p for p in sorted(area.rglob(f"{name}.md")) if "/tests/" not in p.as_posix()]
    return next((p for p in found if p.parent.name == "procs"), found[0])


def serve_tags(document: Path) -> list[tuple[str, str, str]]:
    """-> (name, start, end) for every tagged token of a document's `serve:` rows -- the
    parts it reads by tag; a body test checks that each tag opens a line of the document
    it names, so a heading moved elsewhere reddens here, never at a member as serve-stale."""
    front = document.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    block = re.search(r"^serve: \|\n((?:  .*\n?)*)", front, re.M)
    found = []
    for name, inside in re.findall(r"(\S+)\[([^\]]*)\]", block.group(1) if block else ""):
        if ".." in inside:
            start, end = inside.split("..", 1)
            found.append((name, start, end))
    return found


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


# What the suite costs, measured on 2026-09-20 over its 187 scenarios: median 0.5s,
# mean 2.4s, p90 7.2s, slowest 38.6s (federation-braids), wall 43-48s in parallel for
# 420-500s of CPU. A target says what we refuse to exceed, so it sits well above the
# p90 and well under the slowest: at 20s three scenarios are named, at 4s thirty-one
# were -- and a warning that sounds thirty-one times warns of nothing.
WALL_TARGET = 60.0                              # seconds: the whole bench, in parallel
SCENARIO_TARGET = 20.0                          # seconds: any one scenario
WARNED_SHOWN = 5                                # lines before the rest is one line


def cli(engine: Path, *args: str, cwd: Path | None = None,
        stdin: str | None = None) -> subprocess.CompletedProcess:
    """The console, exercised as the operator or the agent would -- the bench's own
    interpreter runs the engine (what `uv run` resolves to, without its start-up).
    `stdin` feeds a piped production: `./pp <key> -` reads the step's answer there."""
    return subprocess.run([sys.executable, str(engine), *args], capture_output=True,
                          text=True, cwd=cwd, input=stdin)


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
        return Conductor(self.member, self.siblings(), self.engine, key)

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

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.refusals = 0
        self.held_count = 0
        self.times: list[tuple[str, float]] = []
        self._temps: list[Path] = []
        self._shared: Env | None = None
        self._pristine: dict[tuple[str, ...], Path] = {}

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

    @staticmethod
    def over(block) -> bool:
        """The END block: the conduction stopped, constraints on screen, no call left."""
        return block is not None and not block.next_call and bool(block.end)

    def temp(self) -> Path:
        """A throwaway directory the teardown removes."""
        made = Path(tempfile.mkdtemp())
        self._temps.append(made)
        return made

    def env(self, name: str, packages: tuple[str, ...] = (), pin: bool = True,
            bare: bool = False, at: Path | None = None) -> Env:
        """An ENVIRONMENT on demand: `<temp>/<name>/.pp` installed from the product
        engine, the bench's settings pinned -- created once here, evolving with the
        cases that drive it, torn down at the end. Never shared with another scenario.
        `bare` drops the compiled marble AND the settings document: no standing orders
        ride the blocks, no build receipt guards the boot, the engine's seeds tune it
        -- the engine's MECHANICS alone, what the cases on a bare member prove."""
        root = (at or self.temp()) / name
        pristine = self._pristine.get(tuple(packages))
        if pristine is None:                       # the install, once per bench and package set
            pristine = self.temp() / "pristine"
            install.install(PRODUCT_ENGINE, pristine / INSTANCE, list(packages))
            self._pristine[tuple(packages)] = pristine
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

    def shared(self) -> Env:
        """The ONE environment the body tests share: installed once per bench with the
        system packages, NEVER mutated by a test -- they read, render, assert."""
        if self._shared is None:
            self._shared = self.env("shared", SYSTEM_PACKAGES)
        return self._shared

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
    whole, by its last segment, by a leading path or an area (`kit`, `body`)."""
    found = []
    for prefix, home in areas():
        for path in sorted(home.rglob("*.py")):
            if path.name in ("harness.py", "__init__.py") or "__pycache__" in path.parts:
                continue
            name = path.relative_to(home).with_suffix("").as_posix()
            name = f"{prefix}/{name}" if prefix else name
            if not selection or any(name == one or name.endswith("/" + one) or name.startswith(one + "/")
                                    or f"/{one}/" in f"/{name}/" for one in selection):
                found.append((name, path))
    return found


def is_body(name: str) -> bool:
    return "/body/" in f"/{name}/"


PINNED_CHARS, PINNED_WORDS = 40, 6     # a SENTENCE: shorter than that, a literal is a
                                       # form the engine renders, not a document's prose


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


def lint(found: list[tuple[str, Path]]) -> list[str]:
    """The structure, checked before any scenario plays (tests/README.md, rule 4):
    a body/<NAME>.py keeps a document <NAME>.md of its area; a phrase a body keeps
    appears in no other test; a scenario's name is kebab, or the document's name
    under body/. -> the refusals, empty when the structure stands."""
    refused: list[str] = []
    kept: dict[str, str] = {}          # a body test -> the TEXT of the document it keeps
    homes = {prefix: home.parent for prefix, home in areas()}
    for name, path in found:
        stem = path.stem
        if is_body(name):
            prefix = name.split("/", 1)[0] if "/" in name and name.split("/", 1)[0] in homes else ""
            area = homes.get(prefix, SOURCE)
            documents = [one for one in sorted(area.rglob(f"{stem}.md")) if "/tests/" not in one.as_posix()]
            if not DOCUMENT_NAME.match(stem) or not documents:
                refused.append(f"{name}: a body/ test keeps ONE document of its area and bears its "
                               f"name -- no {stem}.md under {area.relative_to(SOURCE) or '.'}")
                continue
            kept[name] = "\n".join(one.read_text(encoding="utf-8") for one in documents)
        elif not KEBAB.match(stem):
            refused.append(f"{name}: a scenario's name is kebab (english, by its subject) -- "
                           f"a document's name belongs under body/")
    for name, path in found:                     # the KEPT DOCUMENTS are the reference, not
        if is_body(name) or not kept:            # the phrases a body test happens to pin
            continue
        for phrase in sorted(_pinned(path)):
            owner = next((one for one, text in kept.items() if phrase in text), None)
            if owner:
                refused.append(f"{name}: compares with a sentence of the document {owner} keeps "
                               f"({phrase[:60]!r}) -- the mechanics compare with the document "
                               f"read at run time, never a literal")
                break
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
    bench = Bench()
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


def play_many(pairs: list[tuple[str, str]], live: bool = False) -> list[dict]:
    """The body scenarios, one after the other on ONE bench: they share its
    environment (`bench.shared()`) and never mutate it -- one process, one teardown."""
    bench = Bench()
    results = []
    try:
        for name, path in pairs:
            out = io.StringIO()
            held, refusals, failures_before = bench.held_count, bench.refusals, len(bench.failures)
            started = time.perf_counter()
            try:
                with captured(out, live):
                    module = load_script(Path(path))
                    code = module.scenario(bench)
                if code:
                    bench.failures.append(f"  ✗ {name:<28}exit {code}")
            except BaseException as error:                                # noqa: BLE001
                bench.failures.append(f"  ✗ {name:<28}raised {type(error).__name__}: {error}\n"
                                      + "".join(traceback.format_exc()))
            results.append({"name": name, "out": out.getvalue(), "held": bench.held_count - held,
                            "refusals": bench.refusals - refusals,
                            "failures": bench.failures[failures_before:],
                            "seconds": time.perf_counter() - started})
    finally:
        bench.teardown()
    return results


def report(results: list[dict], wall: float, detail: bool = False) -> int:
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
    over = [one for one in results if one["seconds"] > SCENARIO_TARGET]
    for one in over[:WARNED_SHOWN]:              # the target: said, never failing the count
        print(f"  ⚠ {one['name']} took {one['seconds']:.1f}s -- over the {SCENARIO_TARGET:.0f}s target")
    if len(over) > WARNED_SHOWN:                 # the list stays readable whatever the target
        print(f"  ⚠ {len(over) - WARNED_SHOWN} more over the {SCENARIO_TARGET:.0f}s target")
    if wall > WALL_TARGET and len(results) > 1:
        print(f"  ⚠ the wall took {wall:.1f}s -- over the {WALL_TARGET:.0f}s target")
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


def played(found: list[tuple[str, Path]], serial: bool) -> list[dict]:
    """One PASS of a selection: the body scenarios together on one bench, every other
    in its own process -- or all of them in this one, live, under `serial`."""
    bodies = [(name, str(path)) for name, path in found if is_body(name)]
    others = [(name, str(path)) for name, path in found if not is_body(name)]
    if serial or len(found) == 1:
        return play_many(bodies, live=True) + [play(name, path, live=True) for name, path in others]
    with ProcessPoolExecutor() as pool:
        grouped = pool.submit(play_many, bodies) if bodies else None
        results = list(pool.map(play, [n for n, _ in others], [p for _, p in others]))
        return (grouped.result() + results) if grouped is not None else results


def report_repeat(rounds: list[list[dict]], wall: float) -> int:
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
    or the selected ones: the structure linted first, the body scenarios together on one
    bench in one process, every other scenario in its own process; `-serial` plays
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
    found = scenarios(selection)
    if not found:
        print(f"pp: no scenario answers to {' '.join(selection) or 'the bench'} -- "
              f"the names are the files under {HERE} and every area's tests/")
        return 2
    refused = lint(scenarios([]))
    if refused:
        print("pp: the bench's structure refuses -- nothing played (tests/README.md):")
        print("\n".join(f"  ✗ {one}" for one in refused))
        return 2
    started = time.perf_counter()
    if repeat > 1:
        rounds = [played(found, serial) for _ in range(repeat)]
        return report_repeat(rounds, time.perf_counter() - started)
    return report(played(found, serial), time.perf_counter() - started,
                  detail=detail or serial)
