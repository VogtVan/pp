"""Scenario `entry` -- the paths a document enters by, and what it does at its entry:
- the entry paths: the entries are ONE table (`conductor.execution.entry.ENTRIES`), each path
  naming what it applies; a socket document's own law of production is proven once at the
  frontier, its successor defers too, a lawless one owes nothing, a slot saved with the old
  mark `socket: true` reads back as the socket path; the floor serves its `payloads:` and its
  overlays' rows; the re-serve replays the `serve:` sections its SERVEs played, a mount all
  its rows
- `exec:` at the entry: the owner's skill plays before the body and any service, its
  arguments resolve as the guards do; once per entry -- a CALL, a mount at every turn's
  beginning, each lap of an iterated door -- and never at `-peek`, `-compacted`, a repair or
  a chunk; a non-zero exit refuses atomically (`exec-refused`); the output goes to the bus
  alone (`exec-mount`); several execs play in the derived order, `order:` inverts it, an
  opposed pair refuses `order-cycle`; `-stats` counts the execs
"""
from __future__ import annotations

import json

from conductor import compiling, events, instance, persistence, render, revive

RECORD = "exec.record"
CONTRACT = "---\nname: {name}\ndescription: {said}\n---\n\n{name}\n"
CALLER = "---\nname: {name}\nkind: proc\ndescription: calls {callee}\nproc: |\n  CALL {callee}.md\n  INFER\n---\n\ncalls\n"

# --- the entry paths ------------------------------------------------------------------------

WITNESS = """name: witness
version: 0.0.1
description: a package providing a payload to the entry paths
requires: [kit]
"""
GIVER = """---
name: GIVER
kind: doc
description: the provider of the witness token
provides: witness
with: pp-witness hello
---

GIVER gives
"""
GIVER_SKILL = "#!/usr/bin/env python3\nimport sys\nprint('the witness skill says', *sys.argv[1:])\n"

TRIAGE = """---
name: TRIAGE
kind: proc
description: a socket document with a law of its own
attach: turn.begin
output: line
constraints.production: |
  TG1  the line opens on one class.
proc: |
  INFER
---

Classify the message.
"""
QUIET = """---
name: QUIET
kind: proc
description: a socket document without a law of production
attach: turn.begin
output: line
proc: |
  INFER
---

Say one line.
"""
LEAVER = """---
name: LEAVER
kind: proc
description: a socket document that leaves to a successor
attach: turn.begin
output: line
next: |
  AFTER.md
proc: |
  INFER
---

Leave.
"""
AFTER = """---
name: AFTER
kind: proc
description: the successor of a socket document, with a law of its own
output: line
constraints.production: |
  AF1  the successor's line lands.
proc: |
  INFER
---

After.
"""
FLOOR = """---
name: FLOOR
kind: proc
description: a floor that declares a payload
payloads: witness
proc: |
  WORK
---

the floor
"""
FLOOR_OVERLAY = """---
name: FLOOR
serve: |
  reference: EXTRA.md
---
"""
PACED = """---
name: PACED
kind: proc
description: a floor with two serve sections, one SERVE played
serve: |
  reference: FIRST.md

  reference: SECOND.md
proc: |
  SERVE
  WORK
  SERVE
  WORK
---

paced
"""
HOSTED = """---
name: HOSTED
kind: doc
serve: |
  reference: FIRST.md

  reference: SECOND.md
---

hosted
"""

# --- exec at the entry ----------------------------------------------------------------------

ALPHA = """name: alpha
version: 0.0.1
description: a witness package whose documents act at their entry
requires: [kit]
contributes:
  events:
    vectors:
      alpha-mark: {verify: pp-alpha}
    signals:
      alpha-note: {standing: true}
"""
BETA = """name: beta
version: 0.0.1
description: a second witness, overlaying alpha's entry with an exec of its own
requires: [alpha]
"""
FRAGMENT = """---
name: SETTINGS
kind: doc
description: alpha's own keys
alpha_mode: slow
---

## alpha

- `alpha_mode` -- the mode the witness stamps.
"""
ALPHA_DOC = """---
name: ALPHA
kind: doc
description: the field the witness's exec reads
mode: fast
---

alpha's field
"""
SEEN = """---
name: SEEN
kind: doc
description: what the witness last stamped
provides: alpha-seen
with: pp-alpha seen
---

seen
"""
ENTRY = """---
name: ENTRY
kind: proc
description: a proc that stamps at its entry and reads the stamp at its block
exec: {exec}
{extra}payloads: alpha-seen
proc: |
  INFER
---

entry says hi
"""
RESET = """---
name: RESET
kind: doc
description: the work of the turn's beginning
mount: turn.begin
exec: reset
---

reset brings
"""
OVERLAY = """---
name: ENTRY
exec: stamp over
{extra}---
"""
SKILL = '''import sys
from pathlib import Path

RECORD = Path.cwd() / "exec.record"
verb, args = (sys.argv[1] if len(sys.argv) > 1 else ""), sys.argv[2:]
if verb in ("stamp", "reset"):
    with open(RECORD, "a", encoding="utf-8") as out:
        out.write(" ".join(["{who}", verb, *args]).rstrip() + "\\n")
elif verb == "seen":
    lines = RECORD.read_text(encoding="utf-8").splitlines() if RECORD.exists() else []
    if lines:
        print(lines[-1])
elif verb == "verify":
    sys.stdin.read()
elif verb == "fail":
    print("{who} fails on purpose", file=sys.stderr)
    sys.exit(2)
elif verb == "push":
    print("::push alpha-note alpha-mark:x the exec noted it")
elif verb == "mountit":
    print(\'::mount [{{"doc": "procs/GATE.md"}}]\')
else:
    print("usage", file=sys.stderr)
    sys.exit(2)
'''
LAPS = '''import sys
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
sys.exit(0)
'''
LOOP = """---
name: LOOP
kind: proc
cycle: true
description: a floor that hooks the turn at every lap
exec: pp-mine stamp floor
proc: |
  HOOK turn.begin
  WORK
---

the loop
"""
GATE = "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: false\n---\n\nthe gate\n"


def _pin(made, name: str, manifest: str, files: dict[str, str]) -> None:
    """A witness package pinned by hand at `made`: its manifest and `files` under its root."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


def _alpha(made, entry_exec: str = "stamp @ALPHA.mode @SETTINGS.alpha_mode plain", entry_extra: str = "") -> None:
    _pin(made, "alpha", ALPHA, {
        "settings/SETTINGS.md": FRAGMENT,
        "procs/ALPHA.md": ALPHA_DOC,
        "procs/SEEN.md": SEEN,
        "procs/ENTRY.md": ENTRY.format(exec=entry_exec, extra=entry_extra),
        "procs/RESET.md": RESET,
        "skills/pp-alpha/SKILL.md": CONTRACT.format(name="pp-alpha", said="the alpha witness's skill"),
        "skills/pp-alpha/pp-alpha.py": SKILL.format(who="alpha"),
    })


def _mine(env) -> None:
    """The INSTANCE's own skill: an instance document names it in front of the verb."""
    env.write("skills/pp-mine/SKILL.md", CONTRACT.format(name="pp-mine", said="the instance's own skill"))
    env.write("skills/pp-mine/pp-mine.py", SKILL.format(who="mine"))


def _drive(env, first, cap: int = 12) -> list:
    """Advance to the frontier with bare submits -> every block met, the proofs piped n/a
    for the codes the checkpoint names."""
    seen = [first]
    while seen[-1] is not None and "▶ FINAL" not in render(seen[-1]) and len(seen) < cap:
        last = seen[-1]
        if last.instruction is not None and last.instruction.keyword == "PROVE":
            answer = json.dumps([{"code": code, "evidence": "bench", "verdict": "n/a"}
                                 for code in last.judged])
        else:
            answer = ""                       # a draft closes on the bare call
        seen.append(env.conductor("t").submit(answer))
    return [one for one in seen if one is not None]


def _proofs(seen) -> list:
    return [tuple(one.judged) for one in seen
            if one.instruction is not None and one.instruction.keyword == "PROVE"]


def _socket_env(bench, name: str, documents: dict[str, str]):
    """-> an environment whose `documents` (relpath -> text) are written and cataloged."""
    env = bench.env(name)
    for relpath, text in documents.items():
        env.write(relpath, text)
    compiling.build_tools(env.made)
    return env


def _key(env) -> str:
    return persistence.run_id_of(env.session())


def _trace(env) -> list[dict]:
    log = json.loads(env.session().read_text(encoding="utf-8"))["log"]
    lines = (env.made / ".sys" / "state" / log).read_text(encoding="utf-8").splitlines()
    return [json.loads(one) for one in lines if one.strip()]


def _execs(env) -> list[dict]:
    return [one for one in _trace(env) if one.get("kind") == "exec"]


def _record(env) -> list[str]:
    path = env.root / RECORD
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _fresh(env):
    """-> a conductor on a forgotten run, the record emptied."""
    opener = env.conductor()
    opener.forget()
    (env.root / RECORD).write_text("", encoding="utf-8")
    return opener


def entry_paths(bench) -> None:
    """The ENTRIES table, the socket's deferred proof, the floor's services, the re-serve."""
    held, failures = bench.held, bench.failures

    # --- the entries are ONE table, read at the engine's module ----------------------------
    from conductor.execution import entry
    table = dict(entry.ENTRIES)
    wanted = {"floor", "call", "door", "socket", "cadence", "successor", "lap", "mount",
              "reserve", "reserve-mount"}
    if wanted <= set(table) and "defer" in table["socket"] and "proof" in table["call"]:
        held("the entries are one table", f"{len(table)} paths, each naming what it applies -- "
             "the socket defers its proof, the call proves at its exit")
    else:
        failures.append(f"  ✗ the entry table             {sorted(table)}")

    # --- a socket document's own law is proven at the frontier -----------------------------
    socket = _socket_env(bench, "entry-socket", {"procs/TRIAGE.md": TRIAGE})
    opener = socket.conductor("t")
    seen = _drive(socket, opener.start(opener.boot("TURN.md")))
    proofs = _proofs(seen)
    final = render(seen[-1]) if seen else ""
    if proofs == [("TG1",)] and "▶ FINAL" in final:
        held("a socket document's law is proven", "attach: + TG1 -> ONE checkpoint at the "
             "frontier naming TG1, no proof at the socket's exit")
    else:
        failures.append(f"  ✗ socket law unproven         proofs={proofs} {final[-120:]!r}")

    # --- a slot saved with the old mark reads back as the socket path -------------------
    socket.conductor("t").forget()
    opener = socket.conductor("t")
    block = opener.start(opener.boot("TURN.md"))
    slot = socket.session()
    state = json.loads(slot.read_text(encoding="utf-8"))
    for frame in state["frames"]:
        for one in frame["instructions"]:
            if one.get("argument") == "TRIAGE.md":
                one.pop("site", None)
                one["socket"] = True
    slot.write_text(json.dumps(state), encoding="utf-8")
    seen = _drive(socket, socket.conductor("t").forward(""))
    if block is not None and _proofs(seen) == [("TG1",)]:
        held("an old slot reads back", "`socket: true` read as the socket path -- the debt "
             "deferred to the frontier, no refusal")
    else:
        failures.append(f"  ✗ old slot                    proofs={_proofs(seen)}")

    # --- the debt rides the socket's successor ------------------------------------------
    succ = _socket_env(bench, "entry-successor", {"procs/LEAVER.md": LEAVER, "procs/AFTER.md": AFTER})
    opener = succ.conductor("t")
    proofs = _proofs(_drive(succ, opener.start(opener.boot("TURN.md"))))
    if proofs == [("AF1",)]:
        held("the successor of a socket defers too", "LEAVER -> AFTER: AF1 proven at the "
             "frontier, once, not at AFTER's exit")
    else:
        failures.append(f"  ✗ successor law               proofs={proofs}")

    # --- a socket document without a law changes nothing -------------------------------
    quiet = _socket_env(bench, "entry-quiet", {"procs/QUIET.md": QUIET})
    opener = quiet.conductor("t")
    seen = _drive(quiet, opener.start(opener.boot("TURN.md")))
    if not _proofs(seen) and seen and "no law of production in force" in render(seen[-1]):
        held("a lawless socket document owes nothing", "QUIET plays, the FINAL owes no proof")
    else:
        failures.append(f"  ✗ quiet socket                proofs={_proofs(seen)}")

    # --- the floor serves its payloads and its overlays' rows at the opening ------------
    floor = bench.env("entry-floor")
    _pin(floor.made, "witness", WITNESS, {
        "procs/GIVER.md": GIVER,
        "skills/pp-witness/SKILL.md": CONTRACT.format(name="pp-witness", said="a witness script"),
        "skills/pp-witness/pp-witness.py": GIVER_SKILL,
    })
    floor.write("EXTRA.md", "---\nname: EXTRA\nkind: doc\n---\n\nthe extra reading\n")
    path = floor.write("procs/FLOOR.md", FLOOR)
    floor.write("FLOOR.md", FLOOR_OVERLAY)
    compiling.build_tools(floor.made)
    first = floor.conductor("t").start(path)
    subjects = [subject for subject, _ in first.payloads] if first is not None else []
    if "witness" in subjects and "EXTRA.md" in subjects:
        held("the floor serves its payloads and overlay rows", f"{subjects}")
    else:
        failures.append(f"  ✗ floor entry                 payloads={subjects}")

    # --- the re-serve replays the sections already played, a mount all its rows ---------
    floor.write("FIRST.md", "---\nname: FIRST\nkind: doc\n---\n\nthe first section\n")
    floor.write("SECOND.md", "---\nname: SECOND\nkind: doc\n---\n\nthe second section\n")
    floor.write("HOSTED.md", HOSTED)
    paced = floor.write("procs/PACED.md", PACED)
    compiling.build_tools(floor.made)
    opener = floor.conductor("t")
    opener.forget()
    opener.start(paced)                          # SERVE 1 played, the WORK stands
    key = _key(floor)
    again = {subject for subject, _ in floor.conductor(key).compacted().payloads}
    if "FIRST.md" in again and "SECOND.md" not in again:
        held("the re-serve keeps the SERVE pace", "the section its SERVE played comes back, "
             "the one still to play does not")
    else:
        failures.append(f"  ✗ re-serve pace               payloads={sorted(again)}")
    floor.conductor(key).mount([{"doc": "HOSTED.md"}])
    mounted = {subject for subject, _ in floor.conductor(key).compacted().payloads}
    if {"FIRST.md", "SECOND.md"} <= mounted:
        held("a mount replays all its rows", "HOSTED's two sections come back whole")
    else:
        failures.append(f"  ✗ mount rows                  payloads={sorted(mounted)}")


def exec_at_entry(bench) -> None:
    """`exec:` at the entry: before the body, once per entry, its arguments, atomic refusal,
    the bus, the order of several, the stats."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- an exec plays at the entry, before the body and the payload ------------------
    env = bench.env("acting")
    _alpha(env.made)
    _mine(env)
    env.write("procs/CALLER.md", CALLER.format(name="CALLER", callee="ENTRY"))
    compiling.build_tools(env.made)
    opener = _fresh(env)
    block = opener.start(opener.boot("CALLER.md"))
    seen = dict(block.payloads).get("alpha-seen", "") if block is not None else ""
    kinds = [one.get("kind") for one in _trace(env)]
    at_exec = kinds.index("exec") if "exec" in kinds else -1
    at_provider = kinds.index("provider") if "provider" in kinds else -1
    played = _execs(env)
    if (seen == "alpha stamp fast slow plain" and 0 <= at_exec < at_provider
            and len(played) == 1 and played[0].get("skill") == "pp-alpha"
            and played[0].get("verb") == "stamp" and played[0].get("document") == "ENTRY"
            and played[0].get("package") == "alpha" and played[0].get("rc") == 0):
        held("an exec plays at the entry", "ENTRY's `exec: stamp @ALPHA.mode @SETTINGS.alpha_mode "
             "plain` wrote `fast slow plain` before its payload read it -- the trace says "
             "exec, then provider")
    else:
        failures.append(f"  ✗ exec at entry               seen={seen!r} exec@{at_exec} provider@{at_provider} {played}")

    # --- the arguments: a word as it is, @Doc.field and @SETTINGS.<key> as the guards --
    if _record(env) == ["alpha stamp fast slow plain"]:
        held("the arguments resolve as the guards do", "`@ALPHA.mode` gave `fast`, "
             "`@SETTINGS.alpha_mode` the fragment's `slow`, `plain` passed as it is")
    else:
        failures.append(f"  ✗ exec arguments              {_record(env)}")

    # --- -peek and -compacted are no entries; a repair neither -----------------------
    env.conductor(_key(env)).peek()
    after_peek = len(_execs(env))
    env.conductor(_key(env)).compacted()
    after_compacted = len(_execs(env))
    if after_peek == 1 and after_compacted == 1:
        held("-peek and -compacted play no exec", "one line after the CALL, still one after both")
    else:
        failures.append(f"  ✗ peek/compacted              {after_peek} {after_compacted}")

    env.write("procs/JUDGE.md",
              "---\nname: JUDGE\nkind: proc\ndescription: judged\nexec: pp-mine stamp judge\n"
              "output: json\nproc: |\n  INFER\n  PICK member\n---\n\njudge\n")
    env.write("procs/CALLJ.md", CALLER.format(name="CALLJ", callee="JUDGE"))
    opener = _fresh(env)
    opener.start(opener.boot("CALLJ.md"))
    env.conductor(_key(env)).submit('["a", "b"]')
    repaired = env.conductor(_key(env)).submit("zzz")
    if (repaired is not None and repaired.deviation and _record(env) == ["mine stamp judge"]
            and len(_execs(env)) == 1):
        held("a repair plays no exec", "the PICK missed, JUDGE reopened from its first step, "
             "its exec left the one line of its CALL")
    else:
        failures.append(f"  ✗ repair                      {_record(env)} {len(_execs(env))}")

    # --- the floor at the boot, a mounted contributor at EVERY turn, the guard --------
    env.write("procs/GATE.md", GATE)
    env.write("procs/GATED.md",
              "---\nname: GATED\nkind: doc\ndescription: gated\nmount: turn.begin\n"
              "when: \"@GATE.open\"\nexec: pp-mine stamp gated\n---\n\ngated\n")
    compiling.build_tools(env.made)
    loop = env.write("procs/LOOP.md", LOOP)
    opener = _fresh(env)
    opener.start(loop)
    counts = [len(_execs(env))]
    env.conductor(_key(env)).submit("")
    counts.append(len(_execs(env)))
    env.conductor(_key(env)).submit("")
    counts.append(len(_execs(env)))
    lines = _record(env)
    if counts == [1, 2, 3] and lines == ["alpha reset"] * 3:
        held("a turn's beginning acts at every turn", "RESET (`mount: turn.begin`) stamped "
             "three turns; the floor is entered by no CALL and its own exec never plays, "
             "the rewind is no entry, and GATED under a false gate stamps nothing")
    else:
        failures.append(f"  ✗ turn.begin exec             counts={counts} {lines}")

    # --- each lap of an iterated door is an entry --------------------------------------
    env.write("skills/pp-laps/SKILL.md", CONTRACT.format(name="pp-laps", said="the iterator and its sink"))
    env.write("skills/pp-laps/pp-laps.py", LAPS)
    env.write("procs/LAPS.md", "---\nname: LAPS\nkind: doc\ndescription: laps\nprovides: laps\nwith: pp-laps next\n---\n")
    env.write("procs/DOOR.md",
              "---\nname: DOOR\nkind: proc\ndescription: the door\ncycle: laps\nsink: pp-laps\n"
              "exec: pp-mine stamp lap\nproc: |\n  INFER\n---\n\none line per element\n")
    env.write("procs/CALLLAP.md", CALLER.format(name="CALLLAP", callee="DOOR"))
    (env.root / "laps.txt").write_text("a\nb\nc\n", encoding="utf-8")
    (env.root / "laps.done").write_text("", encoding="utf-8")
    opener = _fresh(env)
    opener.start(opener.boot("CALLLAP.md"))
    env.conductor(_key(env)).submit("line a")
    env.conductor(_key(env)).submit("line b")
    out = env.conductor(_key(env)).submit("line c")
    lap_kinds = [one.get("kind") for one in _trace(env)]
    if (_record(env) == ["mine stamp lap"] * 3 and lap_kinds.count("lap") == 3
            and out is not None and out.document == "CALLLAP"):
        held("each lap is an entry", "the CALL opened lap `a`, the rewinds on `b` and `c` "
             "each played the exec -- three lines, then the door left")
    else:
        failures.append(f"  ✗ lap exec                    {_record(env)} laps={lap_kinds.count('lap')}")

    # --- a non-zero exit refuses: nothing pushed, nothing written ---------------------
    env.write("procs/BAD.md", "---\nname: BAD\nkind: doc\ndescription: fails\nexec: pp-mine fail\n---\n\nbad\n")
    before = env.session().read_bytes()
    expect("exec-refused", lambda: env.conductor(_key(env)).mount([{"doc": "procs/BAD.md"}]))
    if env.session().read_bytes() == before and not persistence.mounted_of(env.session()):
        held("a refused mount writes nothing", "the slot is byte-identical, no mount stands")
    else:
        failures.append("  ✗ refused mount               the slot moved")
    env.write("procs/BADPROC.md", "---\nname: BADPROC\nkind: proc\ndescription: fails\nexec: pp-mine fail\nproc: |\n  INFER\n---\n\nbad\n")
    env.write("procs/CALLBAD.md", CALLER.format(name="CALLBAD", callee="BADPROC"))
    opener = _fresh(env)
    expect("exec-refused", lambda: opener.start(opener.boot("CALLBAD.md")))
    stack = env.conductor(_key(env))._rebind(persistence.restore(env.session(), revive))
    refused_line = [one for one in _execs(env) if one.get("rc") == 2]
    if len(stack.frames) == 1 and stack.frames[0].document.name == "CALLBAD" and refused_line:
        held("a refused CALL pushes no frame", "the floor stands alone, the trace says rc 2")
    else:
        failures.append(f"  ✗ refused call                frames={[f.document.name for f in stack.frames]}")

    # --- the bus: a push stands, a mount refuses ---------------------------------------
    env.write("procs/PUSHER.md", "---\nname: PUSHER\nkind: doc\ndescription: pushes\nexec: pp-mine push\n---\n\npushes\n")
    env.write("procs/MOUNTER.md", "---\nname: MOUNTER\nkind: doc\ndescription: mounts\nexec: pp-mine mountit\n---\n\nmounts\n")
    opener = _fresh(env)
    opener.start(opener.boot("CALLER.md"))
    env.conductor(_key(env)).mount([{"doc": "procs/PUSHER.md"}])
    standing = [k for k in events.counters(env.made) if k.startswith("standing|alpha|alpha-note|alpha-mark:x")]
    if standing:
        held("an exec's push stands", "`::push alpha-note alpha-mark:x` latched at the bus")
    else:
        failures.append(f"  ✗ exec push                   {list(events.counters(env.made))}")
    expect("exec-mount", lambda: env.conductor(_key(env)).mount([{"doc": "procs/MOUNTER.md"}]))

    # --- -stats counts the execs ------------------------------------------------------
    stats = env.cli("-stats", _key(env)).stdout
    if "3 exec(s)" in stats:
        held("-stats counts the execs", "the run's line says 3 exec(s)")
    else:
        failures.append(f"  ✗ stats exec                  {stats[-300:]!r}")

    # --- a chunk serves, it plays nothing: its own cap ---------------------------------
    cut = bench.env("cutting")
    _mine(cut)
    cut.write("SETTINGS.md", cut.read("SETTINGS.md").replace("max_harness_tool_output: 60000",
                                                              "max_harness_tool_output: 1500"))
    cut.write("procs/BIG.md",
              "---\nname: BIG\nkind: proc\ndescription: a big body\nexec: pp-mine stamp big\n"
              "proc: |\n  INFER\n---\n\n" + ("a long line of matter\n" * 200))
    cut.write("procs/CALLER.md", CALLER.format(name="CALLER", callee="BIG"))
    opener = _fresh(cut)
    text = opener.rendered(opener.start(opener.boot("CALLER.md")))
    served = 1
    while cut.conductor(_key(cut)).pending():
        cut.conductor(_key(cut)).next_chunk()
        served += 1
    if served > 1 and "a reading continues" in text and _record(cut) == ["mine stamp big"]:
        held("a chunk plays no exec", f"{served} chunks served on bare calls, one exec line")
    else:
        failures.append(f"  ✗ chunk exec                  served={served} {_record(cut)}")

    # --- several exec on one document: the derived order, the preferences ------------
    def ordered(extra_over: str = "", extra_base: str = "") -> list[str]:
        """-> the record of ENTRY's execs on an instance of its own: alpha's base, beta's
        overlay, each preference written at its file."""
        ordering = bench.env("ordering")
        _alpha(ordering.made, entry_exec="stamp base", entry_extra=extra_base)
        _pin(ordering.made, "beta", BETA, {
            "overlays/ENTRY.md": OVERLAY.format(extra=extra_over),
            "skills/pp-beta/SKILL.md": CONTRACT.format(name="pp-beta", said="the beta witness's skill"),
            "skills/pp-beta/pp-beta.py": SKILL.format(who="beta"),
        })
        ordering.write("procs/CALLER.md", CALLER.format(name="CALLER", callee="ENTRY"))
        compiling.build_tools(ordering.made)
        opener = ordering.conductor()
        opener.start(opener.boot("CALLER.md"))
        return _record(ordering)

    derived = ordered()
    inverted = ordered(extra_over="order: |\n  exec before alpha\n")
    inert = ordered(extra_over="order: |\n  exec after gamma\n")
    if (derived == ["alpha stamp base", "beta stamp over"]
            and inverted == ["beta stamp over", "alpha stamp base"]
            and inert == ["alpha stamp base", "beta stamp over"]):
        held("several exec, ordered by their preferences", "alpha's base then beta's overlay by "
             "the topology; `order: exec before alpha` at beta's file puts beta first; a "
             "preference toward an absent gamma changes nothing")
    else:
        failures.append(f"  ✗ exec order                  {derived} {inverted} {inert}")
    expect("order-cycle", lambda: ordered(extra_over="order: |\n  exec before alpha\n",
                                          extra_base="order: |\n  exec before beta\n"))


def scenario(bench) -> int:
    entry_paths(bench)
    exec_at_entry(bench)
    return 0
