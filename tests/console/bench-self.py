"""Scenario `bench-self` -- the bench's own mechanics, judged by the bench:
- the hermetic bench: the session's pp variables never reach a throwaway instance, dropped once
  at the entry, a second drop finding none
- the pass's temp on disk: `tmp_pass()` gives the pass its own directory under the user's cache --
  never the system's temp, a tmpfs in RAM on WSL --, `tempfile` and every child write there
  (`TMPDIR`, `TEMP`, `TMP`), a directory whose pass died is swept, the pass's own removed at its end
  and the environment given back
- the engine judged: the conductor the bench imports comes from the source; a vendored engine
  hands `-test` over to the engine of the source its instance declares; a root scenario's
  environment stands on the bench's stand-in for the base, any other area's on the product's
  kit -- `KIT_BOUND` is empty (rule 9); `env.write_member()` writes the member a case needs at
  run time, the stand-in keeping its four files
- the report's lines: a long label keeps a gap before its detail; the report counts out loud and
  details on demand; a count that moves between passes is a red of its own; several runs
  standing, the bench means the freshest; the time targets say and never redden, the list
  readable; a scenario within 10 % over the target says nothing (rule 10)
- the streams: what a scenario writes rides one buffer in its order; a failing scenario renders
  both its streams with its ✗; `expect_exit` hands the case its text and the report the rest
- the support modules (rule 10): a `_<name>.py` beside the scenarios is never collected and
  `support()` loads it; one that exposes `scenario(bench)` is refused by the lint; a compared
  sentence is accused by `pinned()`, refused under rule 2 once `PINNED_REFUSES` is on;
  `kept_document` keeps the product's document, never one under a dotted directory
- the script loader: two homonymous scripts load under two names in `sys.modules`, each able to
  declare its own dataclass
- the skill loader: `load_skill` reads a skill of several modules as one object -- a name defined
  in a module of a package, `dir()` listing what its modules bind, a name two modules define refused,
  a name one imports from the other never a second definition; `replaced()` poses a value for the caller in another module and gives
  the name back; two skills whose packages share their names keep their own, an import made at a
  call included, `sys.path` and the bare names of `sys.modules` left as they were; a star import
  defines nothing; `replaced()` gives a class its `staticmethod` and its `classmethod` back as they
  stood and takes away what it added; a name nobody defines and two modules bind to two objects is
  refused; `replaced()` reaches a name imported under another name
- the machine's queue: the tokens it may give, the smallest bound winning -- the CPU target's
  share of the cores less the tokens in play, none past the CPU target or the memory target, one
  whenever none is in play; `bench.json` and `PP_BENCH_*` set the targets; the pool of a pass is
  never wider than the queue's ceiling; under `-serial` and alone, every scenario plays under one
  token of its own (the passes side by side: `bench-queue`)
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import conductor
from conductor import instance, render
from tests import harness
from tests.harness import (ENGINE, KIT_BOUND, PRODUCT_ENGINE, SOURCE, WITNESSES, Bench, bench_key,
                           cli, hermetic, kept_document, load_script, play, report, report_repeat,
                           support)

SEEN = "import os;print(sorted(k for k in os.environ if k.startswith('PP_')))"

BOTH = """
import sys

def scenario(bench):
    print("out: first")
    print("err: second", file=sys.stderr)
    print("out: third")
    return 0
"""

FALLS = """
import sys

def scenario(bench):
    print("out: falling")
    print("err: falling", file=sys.stderr)
    return 1
"""

REFUSES = """
import sys

def scenario(bench):
    def refuse():
        print("bench-witness-refusal", file=sys.stderr)
        raise SystemExit(2)

    text = bench.expect_exit("bench-witness-refusal", refuse)
    print("out: the case read", "bench-witness-refusal" in text)
    return 0
"""

DECOY = "---\nname: SYSTEM\nkind: doc\n---\nnot the product's\n"

WIRE = '''from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Host:
    name: str


HOST = Host(name={name!r})
'''

# a witness skill: an entry that poses its folder on `sys.path` as a skill's entry does, a package of two
# modules -- `journal` imports a name of `records`, both define `LIMIT` -- and a module beside the entry; a
# package `model` whose `__init__.py` reads its module by a star; a package `rules` whose module `records`
# imports `sessions` under another name -- two packages, two modules `records`
SKILL_ENTRY = """from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from store import journal  # noqa: E402

NAME = {name!r}


def parent():
    return os.getppid()


def late():
    import aside
    from store import records
    return aside.WORD, records.sessions()[0].name
"""

SKILL_RECORDS = """from __future__ import annotations

from dataclasses import dataclass

LIMIT = 3


@dataclass(frozen=True)
class Record:
    name: str

    @staticmethod
    def of(name):
        return Record(name)

    @classmethod
    def made(cls, name):
        return cls(name)


class Kept(Record):
    pass


def sessions():
    return [Record({name!r})]
"""

SKILL_JOURNAL = """from store.records import sessions

LIMIT = 3


def told():
    return [one.name for one in sessions()]
"""


def _spoken(results: list[dict], detail: bool = False) -> tuple[str, int]:
    """-> what the report prints for these results, and its exit code."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        code = report(results, 0.9, detail=detail)
    return said.getvalue(), code


def _thrown(bench, name: str, text: str) -> str:
    """A scenario written at the run under the bench's throwaway directory: the case reads
    what `play` renders of it and never writes on the streams of the process that carries it
    -- a test that printed to prove itself would judge itself."""
    path = bench.temp() / f"{name}.py"
    path.write_text(text, encoding="utf-8")
    return str(path)


def _hermetic(bench) -> None:
    """The session lends the bench nothing: the drop runs first, the scenario's process its own."""
    held, failures = bench.held, bench.failures
    os.environ["PP_MARBLE"] = "1"                 # a scenario owns its process: what it
    os.environ["PP_RUN"] = "zzzzzz"               # poses here reaches its children alone
    dropped = hermetic()
    left = sorted(name for name in os.environ if name.startswith("PP_"))
    inherited = subprocess.run([sys.executable, "-c", SEEN], capture_output=True, text=True)
    if dropped == ["PP_MARBLE", "PP_RUN"] and not left and inherited.stdout.strip() == "[]":
        held("the session lends the bench nothing", "PP_MARBLE and PP_RUN named as dropped, "
             "none left in the environment, and a child process sees none either -- one site "
             "at the entry covers every launcher")
    else:
        failures.append(f"  ✗ the bench is hermetic       {dropped!r} {left!r} "
                        f"{inherited.stdout.strip()!r}")

    if hermetic() == []:
        held("nothing to drop says nothing", "a second call finds no pp variable and "
             "renders an empty list -- the line that names them keeps quiet")
    else:
        failures.append("  ✗ the drop is idempotent      a second call still found pp variables")


def _temp_on_disk(bench) -> None:
    """The pass writes its houses on disk, never in the system's temp."""
    held, failures = bench.held, bench.failures
    home = harness.tmp_home()
    home.mkdir(parents=True, exist_ok=True)
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    stale = home / f"{dead.pid}-stale"
    stale.mkdir(exist_ok=True)
    before = {name: os.environ.get(name) for name in harness.TMP_VARIABLES}
    system = Path("/tmp").resolve()
    with harness.tmp_pass() as mine:
        made = Path(tempfile.mkdtemp())
        seen = subprocess.run([sys.executable, "-c", "import tempfile; print(tempfile.gettempdir())"],
                              capture_output=True, text=True).stdout.strip()
        named = {name: os.environ.get(name) for name in harness.TMP_VARIABLES}
    after = {name: os.environ.get(name) for name in harness.TMP_VARIABLES}
    if (mine.parent == home and made.parent == mine and Path(seen) == mine
            and system not in mine.resolve().parents and set(named.values()) == {str(mine)}
            and not stale.exists() and not mine.exists() and after == before):
        held("the pass's temp is on disk", f"under {home.name}/ of the user's cache: tempfile and a child write "
             "there, a dead pass's directory swept, the pass's own removed, the environment given back")
    else:
        failures.append(f"  ✗ temp on disk               mine={mine} made={made} seen={seen!r} named={named} "
                        f"stale={stale.exists()} left={mine.exists()} after={after} before={before}")


def _engine(bench) -> None:
    """The engine the bench judges, the engine a vendored `-test` hands over to, the base by area."""
    held, failures = bench.held, bench.failures
    # --- the provenance: one code judges, in process and in subprocess ---------------
    imported = Path(conductor.__file__).resolve().parent
    if imported == (ENGINE / "conductor").resolve():
        held("the bench judges the source", f"`conductor` is imported from {imported} -- "
             f"the same tree {PRODUCT_ENGINE.name} installs every throwaway instance from, "
             "so both halves of the bench judge one code")
    else:
        failures.append(f"  ✗ the engine judged           {imported} -- not {ENGINE / 'conductor'}")

    # --- the hand-over: the vendored engine hands the call over ----------------------
    env = bench.env("relay")
    source_engine = Path(instance.read(env.made)["source"]) / "engine" / "pp.py"
    answer = cli(env.engine, "-test", "nothing-answers-to-this-name")
    if (f"bench on {source_engine}" in answer.stdout and answer.returncode == 2
            and "no scenario answers" in answer.stdout):
        held("a vendored engine hands the bench over", "its `-test` opens on the header line "
             "of the engine its instance declares as SOURCE and returns the usual refusal -- "
             "the call plays where the product lives, whatever was typed")
    else:
        failures.append(f"  ✗ the bench was not handed over rc {answer.returncode}: "
                        f"{answer.stdout[:160]!r}")

    # --- the witness member: the member a case needs, written at run time ------------
    witnessed = bench.env("membered")
    written = witnessed.write_member("character: >-\n  curt, dry wit\nconstraints.behavior: |\n"
                                     "  M1  your name is @MEMBER.name\n  M2  you behave: @MEMBER.character\n",
                                     body="A terse witness.", name="Sextant")
    opener = witnessed.conductor("t")
    first = opener.start(opener.boot("BOOT.md"))
    texts = {one.code: one.text for one in first.constraints} if first is not None else {}
    kept = sorted(str(one.relative_to(WITNESSES / "kit")) for one in (WITNESSES / "kit").rglob("*")
                  if one.is_file() and "__pycache__" not in one.parts)
    if (written == witnessed.made / "procs" / "MEMBER.md"
            and first is not None and "▸ MEMBER" in first.stack
            and first.instruction is not None and first.instruction.keyword == "INFER"
            and texts.get("M1") == "your name is Sextant"
            and texts.get("M2") == "you behave: curt, dry wit"
            and "A terse witness." in render(first)
            and kept == ["package.yaml", "procs/BOOT.md", "procs/TURN.md", "system/SYSTEM.md"]):
        held("env.write_member() writes the member at run time", "procs/MEMBER.md attached at "
             "boot.initialize: the boot calls it first, M1 and M2 in force with their tags resolved, "
             f"its body served; the stand-in keeps its {len(kept)} files")
    else:
        failures.append(f"  ✗ the witness member          {written} stack={first and first.stack!r} "
                        f"{texts!r} kept={kept}")
    witnessed.conductor("t").forget()

    # --- the base by area: the stand-in at the root, the kit elsewhere ---------------
    vendored_kit = next((env.made / ".sys" / "vendor").glob("kit@*"))
    stand_in = instance.manifest_of(vendored_kit)
    elsewhere = Bench("kit")
    try:
        if ("STAND-IN" in str(stand_in.get("description", ""))
                and stand_in == instance.manifest_of(WITNESSES / "kit")
                and "base" not in instance.read(env.made)
                and bench.on_stand_in() and bench.engine() != PRODUCT_ENGINE
                and bench.source() == bench.engine().parent.parent
                and not elsewhere.on_stand_in() and elsewhere.engine() == PRODUCT_ENGINE
                and KIT_BOUND == ()):
            held("the base follows the area", "a root scenario's environment vendors the "
                 "bench's stand-in as `kit`, its manifest naming no `base:`, its source the "
                 "witness source; a bench of another area installs from the product's own "
                 "engine; KIT_BOUND names no sector")
        else:
            failures.append(f"  ✗ the base by area            {stand_in.get('description', '')[:40]!r} "
                            f"{bench.engine()} {elsewhere.engine()} {KIT_BOUND!r}")
    finally:
        elsewhere.teardown()


def _lines(bench) -> None:
    """The report's lines: the column, the default, the passes, the run meant, the targets."""
    held, failures = bench.held, bench.failures
    # --- the label: a long label glued to its detail keeps a gap ---------------------
    probe = Bench()
    spoken = io.StringIO()
    with contextlib.redirect_stdout(spoken):
        probe.held("x" * 40, "detail")
        probe.held("short", "detail")
    lines = spoken.getvalue().splitlines()
    if (len(lines) == 2 and lines[0].endswith("x detail")
            and lines[1] == f"  ✓ {'short':<32}detail"):
        held("a long label keeps its gap",
             "the column holds for a short label; a longer one is followed by one space")
    else:
        failures.append(f"  ✗ bench line                  {lines!r}")

    # --- the default: the report counts out loud and details on demand ---------------
    made = [{"name": "area/chatty", "out": "  ✓ a green one holds\n", "held": 1,
             "refusals": 0, "failures": [], "seconds": 0.1},
            {"name": "area/quiet", "out": "", "held": 2, "refusals": 1,
             "failures": [], "seconds": 0.2},
            {"name": "area/red", "out": "  ✓ the last one before the fall\n", "held": 1,
             "refusals": 0, "failures": ["  ✗ area/red                     boom"],
             "seconds": 0.3}]
    plain, plain_code = _spoken(made)
    detailed, detailed_code = _spoken(made, detail=True)
    counted = [line for line in plain.splitlines() if " held " in line]
    if (plain_code == 1 and detailed_code == 1
            and "a green one holds" not in plain          # a quiet green keeps its detail
            and "the last one before the fall" in plain   # a failing one always speaks
            and "a green one holds" in detailed
            and counted == [line for line in detailed.splitlines() if " held " in line]
            and "boom" in plain and "1 failure(s)" in plain):
        held("the table counts, the detail waits", "a green scenario's lines wait for the "
             "flag; a failing one renders them with its ✗, and the table is the same either way")
    else:
        failures.append(f"  ✗ the report's default        {counted!r}")

    # --- the passes: a count that moves between passes is a red ----------------------
    def pass_of(held_steady: int) -> list[dict]:
        return [{"name": "area/steady", "out": "", "held": 4, "refusals": 0,
                 "failures": [], "seconds": 0.1},
                {"name": "area/moving", "out": "", "held": held_steady, "refusals": 0,
                 "failures": [], "seconds": 0.1}]

    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        shaken = report_repeat([pass_of(3), pass_of(2)], 1.0)
    unmoved = io.StringIO()
    with contextlib.redirect_stdout(unmoved):
        steady = report_repeat([pass_of(3), pass_of(3)], 1.0)
    shaken_said, steady_said = said.getvalue(), unmoved.getvalue()
    if (shaken == 1 and steady == 0 and "area/moving" in shaken_said
            and "3 held / 2 held" in shaken_said and "area/steady" not in shaken_said
            and "1 scenario(s) moved" in shaken_said and "steady." in steady_said):
        held("a count that moves is a red", "two passes of one selection: the scenario "
             "whose count changed is named with what it held pass by pass, the steady one "
             "is not -- and two identical passes say the bench is steady")
    else:
        failures.append(f"  ✗ the passes compared         {shaken}/{steady} "
                        f"{shaken_said.splitlines()[-3:]!r}")

    if "`-detail`" in plain and "1 scenario(s)" in plain and "`-detail`" not in detailed:
        held("the silence says itself", "one line names how many scenarios keep their "
             "detail and the flag that renders it -- under the flag there is nothing to say")
    else:
        failures.append(f"  ✗ the silence is announced    {plain.splitlines()[-4:]!r}")

    # --- the run meant: several runs standing, the bench means the freshest ----------
    env = bench.env("many")
    state = env.made / ".sys" / "state"
    state.mkdir(parents=True, exist_ok=True)
    for name, log in (("aaaaaa", "session-a.jsonl"), ("ffffff", "session-f.jsonl")):
        (state / f"session-{name}.json").write_text(json.dumps({"log": log}), encoding="utf-8")
        time.sleep(0.01)                     # the slots are written one after the other
    meant = bench_key(env.made)
    again = bench_key(env.made)
    if meant == "ffffff" == again:
        held("several runs standing, the freshest is meant", "two slots side by side: the "
             "bench names the one written last, twice in a row -- an instance carries one "
             "run per conversation, and a fixture says which it means")
    else:
        failures.append(f"  ✗ the run meant               {meant!r} then {again!r}")

    # --- the time targets: they say, and the list stays readable ---------------------
    slow = [{"name": f"area/slow-{i}", "out": "", "held": 1, "refusals": 0,
             "failures": [], "seconds": 30.0} for i in range(12)]
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        verdict = report(slow, 50.0)
    lines = said.getvalue().splitlines()
    warned = [line for line in lines if "took" in line and "target" in line]
    rest = [line for line in lines if "more over the" in line]
    walled = [line for line in lines if "the wall took" in line]
    if (verdict == 0 and len(warned) == 5 and len(rest) == 1 and "7" in rest[0]
            and not walled and "green." in said.getvalue()):
        held("the targets say, they never redden", "twelve scenarios over the target render "
             "five lines and one for the seven others; a wall under its own target says "
             "nothing, and the verdict is green -- a target is a word, never a failure")
    else:
        failures.append(f"  ✗ the time targets            rc={verdict} warned={len(warned)} "
                        f"rest={rest!r} wall={len(walled)}")

    # --- the tolerance: within 10 % over the target, silence; past it, the ⚠ (rule 10) --
    near = [{"name": f"area/took-{seconds}", "out": "", "held": 1, "refusals": 0, "failures": [],
             "seconds": float(seconds)} for seconds in (21, 23)]
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        report(near, 23.5)
    warned = [line for line in said.getvalue().splitlines() if "took" in line and "target" in line]
    if len(warned) == 1 and "area/took-23" in warned[0] and "area/took-21" not in said.getvalue().split("wall")[-1]:
        held("10 % over the target is tolerated", f"21 s says nothing, 23 s says {warned[0].strip()!r}")
    else:
        failures.append(f"  ✗ the tolerance               {warned!r}")


def _streams(bench) -> None:
    """What a scenario writes: one buffer, in its order; a ✗ brings it back; a refusal nests."""
    held, failures = bench.held, bench.failures
    # --- both streams, one buffer, the order kept -------------------------------------
    both = play("witness/both", _thrown(bench, "both", BOTH))
    written = [line for line in both["out"].splitlines() if line[:4] in ("out:", "err:")]
    if written == ["out: first", "err: second", "out: third"]:
        held("both streams, one buffer", "a scenario prints on stdout, on stderr, then on "
             "stdout again: the three lines come back in its detail, in the order it wrote them")
    else:
        failures.append(f"  ✗ the two streams captured    {written!r}")

    # --- a ✗ carries everything the scenario wrote -------------------------------------
    fallen = play("witness/falls", _thrown(bench, "falls", FALLS))
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        verdict = report([fallen], 0.9)
    spoken = said.getvalue()
    if verdict == 1 and "out: falling" in spoken and "err: falling" in spoken:
        held("a failure renders both streams", "the report shows the lines of a scenario "
             "that failed without any flag -- whichever stream they were written on")
    else:
        failures.append(f"  ✗ the failure's detail        rc={verdict} "
                        f"{spoken.splitlines()[:4]!r}")

    # --- expect_exit under the capture -------------------------------------------------
    refused = play("witness/refuses", _thrown(bench, "refuses", REFUSES))
    detail = refused["out"]
    if (not refused["failures"] and refused["refusals"] == 1
            and "out: the case read True" in detail
            and detail.count("bench-witness-refusal") == 1):     # the ✓ line alone
        held("a refusal stays the case's own", "expect_exit swaps the stream under the "
             "capture: the case reads the refusal it expects, the report keeps the ✓ and "
             "the text is neither doubled nor lost")
    else:
        failures.append(f"  ✗ the refusal nested          {refused['failures']!r} "
                        f"{detail!r}")


def _support(bench) -> None:
    """The support modules of an area, the lint of the structure and of the sentences."""
    held, failures = bench.held, bench.failures
    area = bench.temp() / "tests"               # a throwaway AREA: one scenario, one support module
    area.mkdir()
    (area / "_x.py").write_text("ANSWER = 42\n\n\ndef twice(n):\n    return 2 * n\n", encoding="utf-8")
    (area / "y.py").write_text("def scenario(bench):\n    return 0\n", encoding="utf-8")
    kept = harness.areas
    harness.areas = lambda: [("", area)]        # the runner reads the areas by this name alone
    try:
        names = [name for name, _ in harness.scenarios([])]
        refused = harness.lint(harness.scenarios([]))
        (area / "_bad.py").write_text("def scenario(bench):\n    return 0\n", encoding="utf-8")
        refused_bad = harness.lint(harness.scenarios([]))
        (area / "_bad.py").unlink()
        words = " ".join(["word"] * 9)
        (area / "z.py").write_text(
            f"def scenario(bench):\n    bench.held('{words}')\n"
            f"    assert '{words}' in str(bench)\n    return 0\n", encoding="utf-8")
        (area / "w.py").write_text(
            f"def scenario(bench):\n    bench.held('{words}')\n    return 0\n", encoding="utf-8")
        accused = dict(harness.pinned(harness.scenarios([])))
        armed = harness.PINNED_REFUSES
        try:
            harness.PINNED_REFUSES = False
            refused_off = harness.lint(harness.scenarios([]))
            harness.PINNED_REFUSES = True
            refused_on = harness.lint(harness.scenarios([]))
        finally:
            harness.PINNED_REFUSES = armed
    finally:
        harness.areas = kept

    # --- the support module: never collected, nothing to lint -------------------------
    if names == ["y"] and refused == []:
        held("a support module is never a scenario", "`_x.py` beside `y.py`: the runner collects "
             "`y` alone, the lint says nothing")
    else:
        failures.append(f"  ✗ support collected           names={names} refused={refused}")

    # --- an opt-in area: out of the default pass, in when the selection names it -------
    extra = bench.temp() / "extra" / "tests"
    extra.mkdir(parents=True)
    (extra / "opt-in").write_text("", encoding="utf-8")
    (extra / "v.py").write_text("def scenario(bench):\n    return 0\n", encoding="utf-8")
    harness.areas = lambda: [("", area), ("extra", extra)]
    try:
        whole = [name for name, _ in harness.by_default(harness.scenarios([]), [])]
        asked = [name for name, _ in harness.by_default(harness.scenarios(["extra"]), ["extra"])]
        by_name = [name for name, _ in harness.by_default(harness.scenarios(["v"]), ["v"])]
        linted = [name for name, _ in harness.scenarios([])]
    finally:
        harness.areas = kept
    if "extra/v" not in whole and asked == ["extra/v"] and by_name == ["extra/v"] and "extra/v" in linted:
        held("an opt-in area plays only when named", "`extra/tests/opt-in`: the default pass leaves "
             "`extra/v` out, `extra` or `v` plays it, the lint still reads it")
    else:
        failures.append(f"  ✗ opt-in area                 whole={whole} asked={asked} by_name={by_name}")

    # --- the loading: the module beside the scenario, by name -------------------------
    module = support(str(area / "y.py"), "x")
    if getattr(module, "ANSWER", None) == 42 and module.twice(21) == 42:
        held("support() loads the module beside the scenario", "`support(__file__, 'x')` -> `_x.py`, "
             "ANSWER 42, twice(21) 42")
    else:
        failures.append(f"  ✗ support loaded              {module!r}")

    # --- the lint: a support module that plays is refused with its rule ---------------
    if (len(refused_bad) == 1 and "_bad" in refused_bad[0] and "rule 10" in refused_bad[0]
            and "scenario(bench)" in refused_bad[0]):
        held("the lint refuses a support module that plays", refused_bad[0][:90])
    else:
        failures.append(f"  ✗ support that plays          {refused_bad}")

    # --- the lint of the sentences: the compared sentence accused, the held line never --
    if list(accused) == ["z"] and accused["z"] == 1 and refused_off == []:
        held("a compared sentence is accused", "`z` compares one, `w` only holds one: "
             "`pinned()` names `z` alone, the lint stays silent while the switch is off")
    else:
        failures.append(f"  ✗ accused                     {accused} {refused_off}")
    if len(refused_on) == 1 and refused_on[0].startswith("z:") and "rule 2" in refused_on[0]:
        held("armed, the lint refuses it", refused_on[0][:90])
    else:
        failures.append(f"  ✗ armed lint                  {refused_on}")

    # --- the kept document: the product's, never a dotted directory's -----------------
    # (on a copy of the engine's system/: the source tree is what other scenarios stage
    # meanwhile -- a decoy written there tears their copy)
    engine = bench.temp() / "engine"
    shutil.copytree(SOURCE / "engine" / "system", engine / "system")
    kept_doc = kept_document(engine, "SYSTEM")
    decoy = engine / ".decoy" / "system" / "SYSTEM.md"
    decoy.parent.mkdir(parents=True, exist_ok=True)
    decoy.write_text(DECOY, encoding="utf-8")
    same = kept_document(engine, "SYSTEM") == kept_doc
    if same and kept_doc == engine / "system" / "SYSTEM.md":
        held("the harness keeps the product's text", "a SYSTEM.md under a dotted directory "
             "of the source changes nothing: `engine/system/SYSTEM.md` stays the kept document")
    else:
        failures.append(f"  ✗ harness decoy               {kept_doc}")


def _homonyms(bench) -> None:
    """Two scripts of one name, two modules: the loader keys them by their place."""
    held, failures = bench.held, bench.failures
    loaded = []
    for name in ("claude", "codex"):
        spot = bench.temp() / "adapters" / name
        spot.mkdir(parents=True)
        (spot / "wire.py").write_text(WIRE.format(name=name), encoding="utf-8")
        loaded.append(load_script(spot / "wire.py"))
    names = [module.__name__ for module in loaded]
    if (len(set(names)) == 2 and all(sys.modules.get(one) is module
                                     for one, module in zip(names, loaded))
            and [module.HOST.name for module in loaded] == ["claude", "codex"]):
        held("homonymous scripts keep their own modules",
             f"two `wire.py` load as {names[0]} and {names[1]}, each registered in "
             "`sys.modules`, each with its own dataclass")
    else:
        failures.append(f"  ✗ homonymous scripts         {names!r}")


SKILL_TASK = """class Task:
    pass


def tasks():
    return [Task()]
"""

SKILL_RULES = """from store.records import sessions as listed


def counted():
    return len(listed())
"""


def _skills(bench) -> None:
    """A skill of several modules, loaded as one object: its names, its doubles, its replacements, its own imports."""
    held, failures = bench.held, bench.failures
    path, modules = list(sys.path), set(sys.modules)
    loaded = {}
    for name in ("one", "two"):                     # two skills, the same names: `pp-witness`, `store`, `aside`
        folder = bench.temp() / "pp-witness"
        for package in ("store", "model", "rules"):
            (folder / package).mkdir(parents=True)
        (folder / "model" / "__init__.py").write_text("from model.task import *\n", encoding="utf-8")
        (folder / "model" / "task.py").write_text(SKILL_TASK, encoding="utf-8")
        (folder / "rules" / "records.py").write_text(SKILL_RULES, encoding="utf-8")
        (folder / "pp-witness.py").write_text(SKILL_ENTRY.format(name=name), encoding="utf-8")
        (folder / "aside.py").write_text(f"WORD = {name!r}\n", encoding="utf-8")
        (folder / "store" / "records.py").write_text(SKILL_RECORDS.format(name=name), encoding="utf-8")
        (folder / "store" / "journal.py").write_text(SKILL_JOURNAL, encoding="utf-8")
        if name == "one":                           # a package with its `__init__.py`, and one without
            (folder / "store" / "__init__.py").write_text("", encoding="utf-8")
        loaded[name] = harness.load_skill(folder / "pp-witness.py")
    one, two = loaded["one"], loaded["two"]

    # --- a name reads on the object, whichever module defines it ----------------------
    read = one.sessions()
    if (one.NAME == "one" and [record.name for record in read] == ["one"] and type(read[0]) is one.Record
            and getattr(one, "absent", None) is None):
        held("a skill's names read on one object", "`NAME` of the entry, `sessions` and the dataclass `Record` "
             "of `store/records.py` read on the loaded skill; a name it does not bind is an AttributeError")
    else:
        failures.append(f"  ✗ a skill's names             {getattr(one, 'NAME', None)!r} {read!r}")

    # --- dir() lists what the skill binds, as it does of a loaded script ----------------
    listed = dir(one)
    if ({"NAME", "journal", "sessions", "Record", "told", "LIMIT"} <= set(listed) and "absent" not in listed
            and not [name for name in listed if name.startswith("_Skill")]):
        held("dir() lists the names a skill binds", "`dir()` of the loaded skill names what its entry and its "
             "two modules bind, a name defined twice included, and nothing of the object's own")
    else:
        failures.append(f"  ✗ dir() of a skill            {[name for name in listed if not name.startswith('__')]}")

    # --- a name two modules define is refused, the two modules named ------------------
    doubled = []
    for reading in (lambda: one.LIMIT, lambda: one.replaced("LIMIT", 5).__enter__()):
        try:
            doubled.append(reading())
        except harness.Doubled as refused:
            doubled.append((refused.name, refused.modules))
    if doubled == [("LIMIT", ["store/journal.py", "store/records.py"])] * 2:
        held("a name defined twice is refused", "`LIMIT`, defined in `store/journal.py` and in "
             "`store/records.py` with one value: its reading and its replacement both name the two modules")
    else:
        failures.append(f"  ✗ a name defined twice        {doubled!r}")

    # --- a name imported by another module is the same definition ---------------------
    if one.sessions is one.journal.sessions:
        held("an imported name is no second definition", "`sessions`, defined in `store/records.py` and "
             "imported by `store/journal.py`, reads without a refusal")
    else:
        failures.append(f"  ✗ an imported name            {one.sessions!r} {one.journal.sessions!r}")

    # --- replaced(): the caller in another module, a dotted name, then the name back ---
    with one.replaced("sessions", lambda: [one.Record("posed")]):
        posed = one.told()
    with one.replaced("os.getppid", lambda: -7):
        pointed = one.parent()
    try:
        one.sessions = None
        assigned = True
    except AttributeError:
        assigned = False
    if (posed == ["posed"] and one.told() == ["one"] and pointed == -7 and one.parent() == os.getppid()
            and not assigned):
        held("replaced() reaches every module that binds the name", "`told` of `store/journal.py` calls the "
             "value posed for `sessions`, then the former one; `os.getppid` is posed on the module the skill "
             "imported and given back; an assignment on the object is refused")
    else:
        failures.append(f"  ✗ replaced()                  posed={posed!r} then={one.told()!r} pointed={pointed!r} "
                        f"assigned={assigned}")

    # --- a star import binds what it reads: it defines nothing -------------------------
    try:
        starred = one.Task is one.task.Task and type(one.tasks()[0]) is one.Task
    except harness.Doubled as refused:
        starred = refused.modules
    if starred is True:
        held("a star import defines nothing", "`Task` and `tasks`, defined in `model/task.py` and read by "
             "`model/__init__.py` through `from model.task import *`, read without a refusal")
    else:
        failures.append(f"  ✗ a star import               {starred!r}")

    # --- replaced() on a class: what stood comes back as it stood, what was added leaves ---
    kinds = [type(vars(one.Record)[name]) for name in ("of", "made")]
    with (one.replaced("Record.of", staticmethod(lambda name: "posed")),
          one.replaced("Record.made", classmethod(lambda cls, name: "posed")),
          one.replaced("Kept.of", staticmethod(lambda name: "kept"))):
        on_class = (one.Record.of("x"), one.Record.made("x"), one.Kept.of("x"))
    back = [type(vars(one.Record)[name]) for name in ("of", "made")]
    if (on_class == ("posed", "posed", "kept") and back == kinds == [staticmethod, classmethod]
            and (one.Record.of("x").name, one.Record.made("y").name) == ("x", "y") and "of" not in vars(one.Kept)):
        held("replaced() gives a class its methods back", "`Record.of`, a staticmethod, and `Record.made`, a "
             "classmethod, posed then given back as they stood; `Kept.of`, inherited, posed on `Kept` then taken away")
    else:
        failures.append(f"  ✗ replaced() on a class       posed={on_class!r} back={back} kinds={kinds} "
                        f"kept={'of' in vars(one.Kept)}")

    # --- a name nobody defines, bound to two objects, is refused -----------------------
    try:
        two_bound = one.records
    except harness.Doubled as refused:
        two_bound = (refused.name, refused.modules)
    if two_bound == ("records", ["rules", "store/__init__.py"]) and one.journal.told() == ["one"]:
        held("a name bound to two objects is refused", "`records`, the module of `rules` and the module of "
             "`store`, defined nowhere: its reading names the two packages; `journal`, one module bound by the "
             "entry and by `store`, reads")
    else:
        failures.append(f"  ✗ a name bound to two objects {two_bound!r}")

    # --- replaced() reaches a name imported under another name -------------------------
    with one.replaced("sessions", lambda: []):
        aliased = one.counted()
    if aliased == 0 and one.counted() == 1:
        held("replaced() reaches an import under another name", "`counted` of `rules/records.py` calls `sessions` "
             "as `listed`: it counts the value posed, then the former one")
    else:
        failures.append(f"  ✗ replaced() and an alias     posed={aliased!r} then={one.counted()!r}")

    # --- two skills, the same package names: each its own, nothing left behind ---------
    late = (one.late(), two.late())                 # an import made at the call resolves the skill's own
    stray = sorted(name for name in set(sys.modules) - modules if not name.startswith(harness.SKILLS))
    if (two.NAME == "two" and (one.told(), two.told()) == (["one"], ["two"])
            and late == (("one", "one"), ("two", "two")) and sys.path == path and stray == []):
        held("two skills never meet", "two `pp-witness` with a package `store` and a module `aside` each, "
             "loaded one after the other: each reads its own names, at the load and at an import made by a "
             f"call; `sys.path` as it was, no name in `sys.modules` outside `{harness.SKILLS}…`")
    else:
        failures.append(f"  ✗ two skills                  {getattr(two, 'NAME', None)!r} late={late!r} "
                        f"path={[one for one in sys.path if one not in path]} stray={stray}")


class _Pool:
    """A pool that plays nothing: it keeps the number of workers it was asked for."""
    asked: list = []

    def __init__(self, max_workers=None) -> None:
        _Pool.asked.append(max_workers)

    def __enter__(self):
        return self

    def __exit__(self, *_) -> bool:
        return False

    def map(self, call, names, *rest) -> list[dict]:
        return [{"name": name} for name in names]


TOKENED = """import json
from pathlib import Path

from tests import harness


def scenario(bench):
    state = harness.snapshot(harness.Queue(Path({queue!r}), 100.0, 100.0))
    with open({log!r}, "a", encoding="utf-8") as out:
        out.write(json.dumps([[one["pid"], one["pass"]] for one in state["tokens"]]) + "\\n")
    return 0
"""


def _queue(bench) -> None:
    """The machine's queue: the bound, its targets, the pool's width, a token for every scenario."""
    held, failures = bench.held, bench.failures
    giga = 1 << 30
    home = bench.temp()
    try:
        half = harness.Queue(home, 50.0, 80.0)
        ruled = [harness.allowance(half, 8, 0, 0.1, (16 * giga, 10 * giga), giga),   # the cores bound
                 harness.allowance(half, 8, 3, 0.1, (16 * giga, 10 * giga), giga),   # the tokens in play
                 harness.allowance(half, 8, 2, 0.9, (16 * giga, 10 * giga), giga),   # the CPU past its target
                 harness.allowance(half, 8, 2, 0.1, (16 * giga, 4 * giga), giga),    # the memory past its own
                 harness.allowance(half, 8, 0, 0.9, (16 * giga, giga), giga),         # none in play: one
                 harness.allowance(half, 8, 1, None, None, giga)]                     # unreadable: the cores
    except Exception as error:
        ruled = repr(error)
    if ruled == [4, 1, 0, 0, 1, 3]:
        held("the smallest bound wins", "50 % of 8 cores give 4, 3 in play leave 1, the CPU or the "
             "memory past its target give none, none in play gives 1 whatever the load, the "
             "readings missing leave the cores")
    else:
        failures.append(f"  ✗ the queue's bound            {ruled!r}")

    # --- the targets: bench.json, then the pass's own variables, else the defaults -----
    try:
        default = harness.queue_of({"XDG_CACHE_HOME": str(home)})
        (home / harness.QUEUE_SETTINGS).write_text(json.dumps({"cpu": 50, "memory": 60}), encoding="utf-8")
        written = harness.queue_of({"PP_BENCH_QUEUE": str(home)})
        own = harness.queue_of({"PP_BENCH_QUEUE": str(home), "PP_BENCH_CPU": "25", "PP_BENCH_MEMORY": "x"})
        targets = [(one.cpu, one.memory, harness.ceiling(one, 8)) for one in (default, written, own)]
        placed = default.home == home / harness.QUEUE_HOME and written.home == home
    except Exception as error:
        targets, placed = repr(error), False
    expected = [(harness.QUEUE_TARGETS["cpu"], harness.QUEUE_TARGETS["memory"],
                 int(harness.QUEUE_TARGETS["cpu"] * 8 / 100)), (50.0, 60.0, 4), (25.0, 60.0, 2)]
    if placed and targets == expected:
        held("bench.json and PP_BENCH_* set the targets", f"8 cores: the defaults give "
             f"{expected[0][2]} tokens, bench.json at 50 % gives 4, PP_BENCH_CPU at 25 % gives 2 and "
             "a memory target that is no number is ignored; the queue under the user's cache "
             "unless PP_BENCH_QUEUE names one")
    else:
        failures.append(f"  ✗ the queue's targets         {targets!r} placed={placed}")

    # --- the pool: never wider than the queue's ceiling --------------------------------
    cores = os.cpu_count() or 1
    pooled = harness.Queue(bench.temp(), (3.5 * 100) / cores, 100.0)
    found = [(f"area/{one}", Path(f"{one}.py")) for one in "abcde"]
    kept_pool = harness.ProcessPoolExecutor
    _Pool.asked = []
    try:
        harness.ProcessPoolExecutor = _Pool
        harness.played(found, False, pooled)
        asked, left = list(_Pool.asked), harness.snapshot(pooled)
    except Exception as error:
        asked, left = repr(error), {}
    finally:
        harness.ProcessPoolExecutor = kept_pool
    if asked == [3] and left.get("ring") == [] and left.get("tokens") == []:
        held("the pool is the queue's ceiling", f"five scenarios, a CPU target worth 3 tokens: "
             f"{asked[0]} workers, and the pass out of the ring at its end")
    else:
        failures.append(f"  ✗ played() and the pool         {asked!r} {left!r}")

    # --- -serial and alone: every scenario under a token of its own --------------------
    queue = harness.Queue(bench.temp(), 100.0, 100.0)
    log = bench.temp() / "tokens.jsonl"
    log.touch()
    witness = _thrown(bench, "tokened", TOKENED.format(queue=str(queue.home), log=str(log)))
    try:
        serial = harness.played([("w/a", Path(witness)), ("w/b", Path(witness))], True, queue)
        alone = harness.played([("w/c", Path(witness))], False, queue)
        seen = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        left = harness.snapshot(queue)
    except Exception as error:
        serial, alone, seen, left = [], [], repr(error), {}
    me = os.getpid()
    if (seen == [[[me, me]]] * 3 and all("waited" in one for one in serial + alone)
            and left.get("ring") == [] and left.get("tokens") == []):
        held("-serial and alone take a token", "two scenarios under -serial, then one alone: each "
             "reads one token in play, its own and its pass's, and the queue is empty after")
    else:
        failures.append(f"  ✗ the token of a serial pass   {seen!r} {left!r}")


def scenario(bench) -> int:
    _hermetic(bench)          # first: it poses and drops variables of the process itself
    _temp_on_disk(bench)
    _engine(bench)
    _lines(bench)
    _streams(bench)
    _support(bench)
    _homonyms(bench)
    _skills(bench)
    _queue(bench)
    return 0
