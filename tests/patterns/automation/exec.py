"""Scenario `exec` -- the pattern `automation/exec`, played from its demonstration:
- STAMPED, CALLed by DESK, plays `pp-stamp` at its entry, before its body and before the payload it
  names -- the trace says exec, then provider; its arguments resolve as a guard reads them
- `-peek` and `-compacted` are no entries; JUDGED, CALLed by TRIAL, is repaired without a second exec
- LOOP, the floor, never plays its own exec; RESET, mounted at `loop.open`, plays at every passage;
  GATED, under a false GATE, plays nothing
- LAPPED, the iterated door ROUNDS CALLs, plays at each lap
- a non-zero exit refuses `exec-refused` and writes nothing: SPOILT's mount stands nowhere, BROKEN's
  CALL from ASKER pushes no frame
- PUSHER's `::push` stands at the bus, MOUNTER's `::mount` refuses `exec-mount`; `-stats` counts
- the chunks of BIG, CALLed by READER, play no exec
- ENTRY's base and its overlays play in the requires order, `order: exec before|after` moves the file
  that writes it and nothing else, a preference toward an absent package is inert, two opposed refuse
  `order-cycle`
- at the build: UNSKILLED and UNTAGGED refuse `reference-unknown`; IDLE, a package's document neither
  called nor mounted, and a reference refuse `exec-unplayable`
- under the principal's conduction one entry plays one exec, the principal's call doubles nothing
The skills, the package that provides the stamp back, and the packages that carry ENTRY, its
overlays and IDLE are written at the test's time.
"""
from __future__ import annotations

from conductor import compiling, events, persistence, revive
from tests.harness import demonstrated, demos, plant, principal, traced, vendor

DRAWER, PATTERN = "automation", "exec"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("ASKER.md", "BIG.md", "BROKEN.md", "DESK.md", "ENTRY.ahead.md", "ENTRY.gamma.md", "ENTRY.md",
         "ENTRY.opposed.md", "ENTRY.overlay.md", "GATE.md", "GATED.md", "HALL.md", "IDLE.md",
         "JUDGED.md", "LAPPED.md", "LAPS.md", "LOOP.md", "MOUNTER.md", "PUSHER.md", "READER.md",
         "RESET.md", "ROUNDS.md", "SPOILT.md", "STAMPED.md", "TRIAL.md", "UNSKILLED.md",
         "UNTAGGED.md")
RECORD = "exec.record"
STAMP = '''import sys
from pathlib import Path

RECORD = Path.cwd() / "exec.record"
verb, args = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
if verb in ("stamp", "reset"):
    with open(RECORD, "a", encoding="utf-8") as out:
        out.write(" ".join(["%s", verb, *args]).rstrip() + "\\n")
elif verb == "seen":
    lines = RECORD.read_text(encoding="utf-8").splitlines() if RECORD.exists() else []
    if lines:
        print(lines[-1])
elif verb == "verify":
    sys.stdin.read()
elif verb == "fail":
    print("%s fails on purpose", file=sys.stderr)
    sys.exit(2)
elif verb == "push":
    print("::push alpha-note alpha-mark:x the exec noted it")
elif verb == "mountit":
    print(\'::mount [{"doc": "procs/GATE.md"}]\')
else:
    sys.exit(2)
'''
ITERATOR = '''import sys
from pathlib import Path

ROOT = Path.cwd()


def due():
    done = set((ROOT / "laps.done").read_text().split()) if (ROOT / "laps.done").exists() else set()
    for line in (ROOT / "laps.txt").read_text().split():
        if line not in done:
            return line
    return None


if sys.argv[1:] == ["next"]:
    element = due()
    if element:
        print(element)
    sys.exit(0)
production = sys.stdin.read()
element = due()
if element and element in production:
    with open(ROOT / "laps.done", "a") as out:
        out.write(element + "\\n")
'''
ALPHA = """name: alpha
version: 0.0.1
description: a witness package -- it provides the stamp back, carries ENTRY and declares the note
requires: [kit]
contributes:
  events:
    vectors:
      alpha-mark: {verify: pp-alpha}
    signals:
      alpha-note: {standing: true}
"""
BETA = "name: beta\nversion: 0.0.1\ndescription: a witness package overlaying ENTRY\nrequires: [alpha]\n"
DELTA = "name: delta\nversion: 0.0.1\ndescription: a third witness package overlaying ENTRY\nrequires: [beta]\n"
SEEN = """---
name: SEEN
kind: doc
description: what the stamp last wrote, served back
provides: alpha-seen
with: pp-alpha seen
---
"""


def _text(name: str) -> str:
    return (DEMO / name).read_text(encoding="utf-8")


def _skill(made, name: str, code: str) -> None:
    home = made / "skills" / name
    home.mkdir(parents=True, exist_ok=True)
    (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: a witness\n---\n\n{name}\n", encoding="utf-8")
    (home / f"{name}.py").write_text(code, encoding="utf-8")


def _house(bench, name: str, documents: dict[str, str] | None = None, demos_: tuple[str, ...] = (),
           laps: bool = False):
    """-> a house carrying `pp-stamp` (and `pp-laps` when `laps`), the package `alpha` (`documents` in
    its `procs/`) and the demonstrations `demos_` in its own `procs/`, built."""
    env = bench.env(name)
    _skill(env.made, "pp-stamp", STAMP % ("mine", "mine"))
    if laps:
        _skill(env.made, "pp-laps", ITERATOR)
    vendor(env.made, "alpha", ALPHA, {"SEEN": SEEN, **(documents or {})},
           {"pp-alpha": STAMP % ("alpha", "alpha")})
    plant(env, DRAWER, PATTERN, demos_)
    compiling.build_tools(env.made)
    return env


def _key(env) -> str:
    return persistence.run_id_of(env.session())


def _execs(env) -> list[dict]:
    return [one for one in traced(env, _key(env)) if one.get("kind") == "exec"]


def _record(env) -> list[str]:
    path = env.root / RECORD
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _fresh(env):
    """-> a conductor on a forgotten run, the record emptied."""
    opener = env.conductor()
    opener.forget()
    (env.root / RECORD).write_text("", encoding="utf-8")
    return opener


def entries(bench) -> None:
    """The entry before the body, the arguments, the non-entries, the passages, the laps."""
    held, failures = bench.held, bench.failures
    env = _house(bench, "exec-entries", demos_=("DESK.md", "STAMPED.md", "TRIAL.md", "JUDGED.md", "LOOP.md",
                                                 "RESET.md", "GATE.md", "GATED.md", "ROUNDS.md", "LAPPED.md",
                                                 "LAPS.md"), laps=True)
    opener = _fresh(env)
    block = opener.start(opener.boot("DESK.md"))
    seen = dict(block.payloads).get("alpha-seen", "") if block is not None else ""
    kinds = [one.get("kind") for one in traced(env, _key(env))]
    at_exec = kinds.index("exec") if "exec" in kinds else -1
    at_provider = kinds.index("provider") if "provider" in kinds else -1
    played = _execs(env)
    if (seen == "mine stamp fast 60000 plain" and 0 <= at_exec < at_provider and len(played) == 1
            and played[0].get("skill") == "pp-stamp" and played[0].get("verb") == "stamp"
            and played[0].get("document") == "STAMPED" and played[0].get("rc") == 0):
        held("an exec plays at the entry", "STAMPED's exec wrote its stamp before the payload read it back -- "
             "the trace says exec, then provider")
    else:
        failures.append(f"  ✗ exec at entry               seen={seen!r} exec@{at_exec} provider@{at_provider} {played}")

    if _record(env) == ["mine stamp fast 60000 plain"]:
        held("the arguments resolve as the guards do", "`@STAMPED.mode` gave `fast`, "
             "`@SETTINGS.max_harness_tool_output` its value, `plain` passed as it is")
    else:
        failures.append(f"  ✗ exec arguments              {_record(env)}")

    env.conductor(_key(env)).peek()
    after_peek = len(_execs(env))
    env.conductor(_key(env)).compacted()
    after_compacted = len(_execs(env))
    if after_peek == 1 and after_compacted == 1:
        held("-peek and -compacted play no exec", "one line after the CALL, still one after both")
    else:
        failures.append(f"  ✗ peek/compacted              {after_peek} {after_compacted}")

    opener = _fresh(env)
    opener.start(opener.boot("TRIAL.md"))
    env.conductor(_key(env)).submit('["a", "b"]')
    repaired = env.conductor(_key(env)).submit("zzz")
    if (repaired is not None and repaired.deviation and _record(env) == ["mine stamp judge"]
            and len(_execs(env)) == 1):
        held("a repair plays no exec", "the PICK missed, JUDGED reopened from its first step, "
             "its exec left the one line of its CALL")
    else:
        failures.append(f"  ✗ repair                      {_record(env)} {len(_execs(env))}")

    opener = _fresh(env)
    opener.start(opener.boot("LOOP.md"))
    counts = [len(_execs(env))]
    env.conductor(_key(env)).submit("")
    counts.append(len(_execs(env)))
    env.conductor(_key(env)).submit("")
    counts.append(len(_execs(env)))
    lines = _record(env)
    if counts == [1, 2, 3] and lines == ["mine reset"] * 3:
        held("a passage's beginning acts at every passage", "RESET (`mount: loop.open`) stamped three "
             "passages; the floor is entered by no CALL and its own exec never plays, the rewind is no "
             "entry, and GATED under a false gate stamps nothing")
    else:
        failures.append(f"  ✗ loop.open exec              counts={counts} {lines}")

    (env.root / "laps.txt").write_text("a\nb\nc\n", encoding="utf-8")
    (env.root / "laps.done").write_text("", encoding="utf-8")
    opener = _fresh(env)
    opener.start(opener.boot("ROUNDS.md"))
    env.conductor(_key(env)).submit("line a")
    env.conductor(_key(env)).submit("line b")
    out = env.conductor(_key(env)).submit("line c")
    lap_kinds = [one.get("kind") for one in traced(env, _key(env))]
    if (_record(env) == ["mine stamp lap"] * 3 and lap_kinds.count("lap") == 3
            and out is not None and out.document == "ROUNDS"):
        held("each lap is an entry", "the CALL opened lap `a`, the rewinds on `b` and `c` each played the "
             "exec -- three lines, then the door left")
    else:
        failures.append(f"  ✗ lap exec                    {_record(env)} laps={lap_kinds.count('lap')}")


def bounds(bench) -> None:
    """The atomic refusal, the bus, the stats, the chunk."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = _house(bench, "exec-bounds", demos_=("DESK.md", "STAMPED.md", "GATE.md", "SPOILT.md", "BROKEN.md",
                                                "PUSHER.md", "MOUNTER.md", "ASKER.md"))
    opener = _fresh(env)
    opener.start(opener.boot("DESK.md"))
    before = env.session().read_bytes()
    expect("exec-refused", lambda: env.conductor(_key(env)).mount([{"doc": "procs/SPOILT.md"}]))
    if env.session().read_bytes() == before and not persistence.mounted_of(env.session()):
        held("a refused mount writes nothing", "the slot is byte-identical, no mount stands")
    else:
        failures.append("  ✗ refused mount               the slot moved")
    opener = _fresh(env)
    expect("exec-refused", lambda: opener.start(opener.boot("ASKER.md")))
    stack = env.conductor(_key(env))._rebind(persistence.restore(env.session(), revive))
    refused_line = [one for one in _execs(env) if one.get("rc") == 2]
    if len(stack.frames) == 1 and stack.frames[0].document.name == "ASKER" and refused_line:
        held("a refused CALL pushes no frame", "the floor stands alone, the trace says rc 2")
    else:
        failures.append(f"  ✗ refused call                frames={[f.document.name for f in stack.frames]}")

    opener = _fresh(env)
    opener.start(opener.boot("DESK.md"))
    env.conductor(_key(env)).mount([{"doc": "procs/PUSHER.md"}])
    standing = [k for k in events.counters(env.made) if k.startswith("standing|alpha|alpha-note|alpha-mark:x")]
    if standing:
        held("an exec's push stands", "`::push alpha-note alpha-mark:x` latched at the bus")
    else:
        failures.append(f"  ✗ exec push                   {list(events.counters(env.made))}")
    expect("exec-mount", lambda: env.conductor(_key(env)).mount([{"doc": "procs/MOUNTER.md"}]))

    stats = env.cli("-stats", _key(env)).stdout
    if "3 exec(s)" in stats:
        held("-stats counts the execs", "the run's line says 3 exec(s)")
    else:
        failures.append(f"  ✗ stats exec                  {stats[-300:]!r}")

    cut = _house(bench, "exec-chunks", demos_=("BIG.md", "READER.md"))
    cut.write("SETTINGS.md", cut.read("SETTINGS.md").replace("max_harness_tool_output: 60000",
                                                              "max_harness_tool_output: 1500"))
    opener = _fresh(cut)
    text = opener.rendered(opener.start(opener.boot("READER.md")))
    served = 1
    while cut.conductor(_key(cut)).pending():
        cut.conductor(_key(cut)).next_chunk()
        served += 1
    if served > 1 and "a reading continues" in text and _record(cut) == ["mine stamp big"]:
        held("a chunk plays no exec", f"{served} chunks served on bare calls, one exec line")
    else:
        failures.append(f"  ✗ chunk exec                  served={served} {_record(cut)}")


def ordered(bench) -> None:
    """Several execs on one document: the derived order, the preferences, the cycle."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    def play(base: str, overlay: str, third: str = "", after: str = "") -> list[str]:
        """-> the record of ENTRY's execs: `base` in alpha, `overlay` in beta, `third` in delta when
        named, `after` an `order:` line the base writes, HALL calling."""
        based = _text(base)
        if after:
            based = based.replace("proc: |", f"order: |\n  {after}\nproc: |", 1)
        env = _house(bench, "exec-order", {"ENTRY": based}, ("HALL.md",))
        layers = [("beta", BETA, overlay)] + ([("delta", DELTA, third)] if third else [])
        for name, manifest, layer in layers:
            vendor(env.made, name, manifest, {}, {f"pp-{name}": STAMP % (name, name)})
            overlays = env.made / ".sys" / "vendor" / f"{name}@0.0.1" / "overlays"
            overlays.mkdir(parents=True, exist_ok=True)
            (overlays / "ENTRY.md").write_text(_text(layer), encoding="utf-8")
        compiling.build_tools(env.made)
        opener = _fresh(env)
        opener.start(opener.boot("HALL.md"))
        return _record(env)

    derived = play("ENTRY.md", "ENTRY.overlay.md")
    inverted = play("ENTRY.md", "ENTRY.ahead.md")
    inert = play("ENTRY.md", "ENTRY.gamma.md")
    if (derived == ["alpha stamp base", "beta stamp over"]
            and inverted == ["beta stamp over", "alpha stamp base"]
            and inert == ["alpha stamp base", "beta stamp over"]):
        held("several exec, ordered by their preferences", "alpha's base then beta's overlay by the "
             "requires order; `order: exec before alpha` at beta's file puts beta first; a preference "
             "toward an absent gamma changes nothing")
    else:
        failures.append(f"  ✗ exec order                  {derived} {inverted} {inert}")
    ahead = play("ENTRY.md", "ENTRY.overlay.md", "ENTRY.ahead.md")
    behind = play("ENTRY.md", "ENTRY.overlay.md", "ENTRY.overlay.md", after="exec after delta")
    if (ahead == ["delta stamp over", "alpha stamp base", "beta stamp over"]
            and behind == ["beta stamp over", "delta stamp over", "alpha stamp base"]):
        held("a preference moves its declarant alone", "delta's overlay `before alpha` plays first, beta's "
             "keeps its rank after alpha's base; alpha's base `after delta` plays last, beta and delta keep "
             "their order")
    else:
        failures.append(f"  ✗ exec order, three            {ahead} {behind}")
    expect("order-cycle", lambda: play("ENTRY.opposed.md", "ENTRY.ahead.md"))


def built(bench) -> None:
    """What the build refuses of an `exec:`."""
    expect = bench.expect

    def building(demo: str, where: str = "instance"):
        env = bench.env("exec-build")
        _skill(env.made, "pp-stamp", STAMP % ("mine", "mine"))
        if where == "instance":
            plant(env, DRAWER, PATTERN, (demo,))
        else:
            vendor(env.made, "alpha", ALPHA, {} if where == "refs" else {demo[:-3]: _text(demo)},
                   {"pp-alpha": STAMP % ("alpha", "alpha")})
            if where == "refs":
                refs = env.made / ".sys" / "vendor" / "alpha@0.0.1" / "refs"
                refs.mkdir(parents=True, exist_ok=True)
                (refs / demo).write_text(_text(demo), encoding="utf-8")
        return lambda: compiling.build_tools(env.made)

    expect("reference-unknown", building("UNSKILLED.md"))
    expect("reference-unknown", building("UNTAGGED.md"))
    expect("exec-unplayable", building("IDLE.md", "package"))
    expect("exec-unplayable", building("IDLE.md", "refs"))


def conducted(bench) -> None:
    """Under the principal's conduction: one entry, one exec; the principal's call doubles nothing."""
    held, failures = bench.held, bench.failures
    env = _house(bench, "exec-principal", demos_=("DESK.md", "STAMPED.md"))
    opener = _fresh(env)
    first = principal(lambda: opener.start(opener.boot("DESK.md")))
    key = opener.run_id
    once = len(_execs(env))
    again = principal(lambda: env.conductor(key).forward("", by_principal=True))
    if first is not None and again is not None and once == 1 and len(_execs(env)) == 1 \
            and _record(env) == ["mine stamp fast 60000 plain"]:
        held("one entry, one exec, under the principal's conduction", "STAMPED stamped once; the "
             "principal's bare call served the step again and played nothing")
    else:
        failures.append(f"  ✗ principal exec              {once} {len(_execs(env))} {_record(env)}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    entries(bench)
    bounds(bench)
    ordered(bench)
    built(bench)
    conducted(bench)
    return 0
