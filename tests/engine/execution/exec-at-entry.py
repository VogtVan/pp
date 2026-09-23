"""Scenario `exec-at-entry` -- a document ACTS at its entry (plan core, batch
l-exec-a-l-entree, 2026-09-15):
- `exec:` plays the OWNER's skill before the body and any service: the payload of the
  same document reads what the exec just wrote, the trace says `exec` before `provider`
- a document `mount: turn.begin` plays its exec at EVERY turn; the floor is entered by
  no CALL and the session rewind is no entry: the floor's own exec never plays
- once per entry: a CALL, a mount, each lap of an iterated door leave ONE `exec` line;
  `-peek`, a chunk, `-compacted` and a repair leave none
- the arguments: words pass as they are, `@Doc.field` and `@SETTINGS.<key>` resolve as
  the guards do
- a non-zero exit refuses `exec-refused`: the frame is not pushed, the mount is not
  written -- the slot is byte-identical
- the output goes to the bus alone: a `::push` stands, a `::mount` refuses `exec-mount`
- a guarded contributor whose guard is false plays no exec
- several exec on one document -- the base's and an overlay's, each its own skill --
  play in the derived order, inverted by `order: exec before|after <package>`; a
  preference toward an absent package is inert; two opposed refuse `order-cycle`
- `-stats` counts the execs of the run
"""
from __future__ import annotations

import json
from conductor import compiling, events, instance, persistence, revive

RECORD = "exec.record"

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
CONTRACT = "---\nname: {name}\ndescription: {said}\n---\n\n{name}\n"
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
CALLER = "---\nname: {name}\nkind: proc\ndescription: calls {callee}\nproc: |\n  CALL {callee}.md\n  INFER\n---\n\ncalls\n"
GATE = "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: false\n---\n\nthe gate\n"


def _pin(made, name: str, manifest: str, files: dict[str, str]) -> None:
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


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures

    def key(env) -> str:
        return persistence.run_id_of(env.session())

    def trace(env) -> list[dict]:
        log = json.loads(env.session().read_text(encoding="utf-8"))["log"]
        lines = (env.made / ".sys" / "state" / log).read_text(encoding="utf-8").splitlines()
        return [json.loads(one) for one in lines if one.strip()]

    def execs(env) -> list[dict]:
        return [one for one in trace(env) if one.get("kind") == "exec"]

    def record(env) -> list[str]:
        path = env.root / RECORD
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    def fresh(env):
        opener = env.conductor()
        opener.forget()
        (env.root / RECORD).write_text("", encoding="utf-8")
        return opener

    # --- an exec plays at the entry, before the body and the payload ------------------
    env = bench.env("acting")
    _alpha(env.made)
    _mine(env)
    env.write("procs/CALLER.md", CALLER.format(name="CALLER", callee="ENTRY"))
    compiling.build_tools(env.made)
    opener = fresh(env)
    block = opener.start(opener.boot("CALLER.md"))
    seen = dict(block.payloads).get("alpha-seen", "") if block is not None else ""
    kinds = [one.get("kind") for one in trace(env)]
    at_exec = kinds.index("exec") if "exec" in kinds else -1
    at_provider = kinds.index("provider") if "provider" in kinds else -1
    played = execs(env)
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
    if record(env) == ["alpha stamp fast slow plain"]:
        held("the arguments resolve as the guards do", "`@ALPHA.mode` gave `fast`, "
             "`@SETTINGS.alpha_mode` the fragment's `slow`, `plain` passed as it is")
    else:
        failures.append(f"  ✗ exec arguments              {record(env)}")

    # --- -peek and -compacted are no entries; a repair neither -----------------------
    env.conductor(key(env)).peek()
    after_peek = len(execs(env))
    env.conductor(key(env)).compacted()
    after_compacted = len(execs(env))
    if after_peek == 1 and after_compacted == 1:
        held("-peek and -compacted play no exec", "one line after the CALL, still one after both")
    else:
        failures.append(f"  ✗ peek/compacted              {after_peek} {after_compacted}")

    env.write("procs/JUDGE.md",
              "---\nname: JUDGE\nkind: proc\ndescription: judged\nexec: pp-mine stamp judge\n"
              "output: json\nproc: |\n  INFER\n  PICK member\n---\n\njudge\n")
    env.write("procs/CALLJ.md", CALLER.format(name="CALLJ", callee="JUDGE"))
    opener = fresh(env)
    opener.start(opener.boot("CALLJ.md"))
    env.conductor(key(env)).submit('["a", "b"]')
    repaired = env.conductor(key(env)).submit("zzz")
    if (repaired is not None and repaired.deviation and record(env) == ["mine stamp judge"]
            and len(execs(env)) == 1):
        held("a repair plays no exec", "the PICK missed, JUDGE reopened from its first step, "
             "its exec left the one line of its CALL")
    else:
        failures.append(f"  ✗ repair                      {record(env)} {len(execs(env))}")

    # --- the floor at the boot, a mounted contributor at EVERY turn, the guard --------
    turns = bench.env("turning")
    _alpha(turns.made)
    _mine(turns)
    turns.write("procs/GATE.md", GATE)
    turns.write("procs/GATED.md",
                "---\nname: GATED\nkind: doc\ndescription: gated\nmount: turn.begin\n"
                "when: \"@GATE.open\"\nexec: pp-mine stamp gated\n---\n\ngated\n")
    compiling.build_tools(turns.made)
    floor = turns.write("procs/LOOP.md", LOOP)
    opener = fresh(turns)
    opener.start(floor)
    counts = [len(execs(turns))]
    turns.conductor(key(turns)).submit("")
    counts.append(len(execs(turns)))
    turns.conductor(key(turns)).submit("")
    counts.append(len(execs(turns)))
    lines = record(turns)
    if (counts == [1, 2, 3] and lines == ["alpha reset"] * 3):
        held("a turn's beginning acts at every turn", "RESET (`mount: turn.begin`) stamped "
             "three turns; the floor is entered by no CALL and its own exec never plays, "
             "the rewind is no entry, and GATED under a false gate stamps nothing")
    else:
        failures.append(f"  ✗ turn.begin exec             counts={counts} {lines}")

    # --- each lap of an iterated door is an entry --------------------------------------
    laps = bench.env("lapping")
    _mine(laps)
    laps.write("skills/pp-laps/SKILL.md", CONTRACT.format(name="pp-laps", said="the iterator and its sink"))
    laps.write("skills/pp-laps/pp-laps.py", LAPS)
    laps.write("procs/LAPS.md", "---\nname: LAPS\nkind: doc\ndescription: laps\nprovides: laps\nwith: pp-laps next\n---\n")
    laps.write("procs/DOOR.md",
               "---\nname: DOOR\nkind: proc\ndescription: the door\ncycle: laps\nsink: pp-laps\n"
               "exec: pp-mine stamp lap\nproc: |\n  INFER\n---\n\none line per element\n")
    laps.write("procs/CALLER.md", CALLER.format(name="CALLER", callee="DOOR"))
    (laps.root / "laps.txt").write_text("a\nb\nc\n", encoding="utf-8")
    (laps.root / "laps.done").write_text("", encoding="utf-8")
    opener = fresh(laps)
    opener.start(opener.boot("CALLER.md"))
    laps.conductor(key(laps)).submit("line a")
    laps.conductor(key(laps)).submit("line b")
    out = laps.conductor(key(laps)).submit("line c")
    lap_kinds = [one.get("kind") for one in trace(laps)]
    if (record(laps) == ["mine stamp lap"] * 3 and lap_kinds.count("lap") == 3
            and out is not None and out.document == "CALLER"):
        held("each lap is an entry", "the CALL opened lap `a`, the rewinds on `b` and `c` "
             "each played the exec -- three lines, then the door left")
    else:
        failures.append(f"  ✗ lap exec                    {record(laps)} laps={lap_kinds.count('lap')}")

    # --- a chunk serves, it plays nothing --------------------------------------------
    cut = bench.env("cutting")
    _mine(cut)
    cut.write("SETTINGS.md", cut.read("SETTINGS.md").replace("max_harness_tool_output: 60000",
                                                              "max_harness_tool_output: 1500"))
    cut.write("procs/BIG.md",
              "---\nname: BIG\nkind: proc\ndescription: a big body\nexec: pp-mine stamp big\n"
              "proc: |\n  INFER\n---\n\n" + ("a long line of matter\n" * 200))
    cut.write("procs/CALLER.md", CALLER.format(name="CALLER", callee="BIG"))
    opener = fresh(cut)
    text = opener.rendered(opener.start(opener.boot("CALLER.md")))
    served = 1
    while cut.conductor(key(cut)).pending():
        cut.conductor(key(cut)).next_chunk()
        served += 1
    if served > 1 and "a reading continues" in text and record(cut) == ["mine stamp big"]:
        held("a chunk plays no exec", f"{served} chunks served on bare calls, one exec line")
    else:
        failures.append(f"  ✗ chunk exec                  served={served} {record(cut)}")

    # --- a non-zero exit refuses: nothing pushed, nothing written ---------------------
    env.write("procs/BAD.md", "---\nname: BAD\nkind: doc\ndescription: fails\nexec: pp-mine fail\n---\n\nbad\n")
    before = env.session().read_bytes()
    expect("exec-refused", lambda: env.conductor(key(env)).mount([{"doc": "procs/BAD.md"}]))
    if env.session().read_bytes() == before and not persistence.mounted_of(env.session()):
        held("a refused mount writes nothing", "the slot is byte-identical, no mount stands")
    else:
        failures.append("  ✗ refused mount               the slot moved")
    env.write("procs/BADPROC.md", "---\nname: BADPROC\nkind: proc\ndescription: fails\nexec: pp-mine fail\nproc: |\n  INFER\n---\n\nbad\n")
    env.write("procs/CALLBAD.md", CALLER.format(name="CALLBAD", callee="BADPROC"))
    opener = fresh(env)
    expect("exec-refused", lambda: opener.start(opener.boot("CALLBAD.md")))
    stack = env.conductor(key(env))._rebind(persistence.restore(env.session(), revive))
    refused_line = [one for one in execs(env) if one.get("rc") == 2]
    if len(stack.frames) == 1 and stack.frames[0].document.name == "CALLBAD" and refused_line:
        held("a refused CALL pushes no frame", "the floor stands alone, the trace says rc 2")
    else:
        failures.append(f"  ✗ refused call                frames={[f.document.name for f in stack.frames]}")

    # --- the bus: a push stands, a mount refuses ---------------------------------------
    env.write("procs/PUSHER.md", "---\nname: PUSHER\nkind: doc\ndescription: pushes\nexec: pp-mine push\n---\n\npushes\n")
    env.write("procs/MOUNTER.md", "---\nname: MOUNTER\nkind: doc\ndescription: mounts\nexec: pp-mine mountit\n---\n\nmounts\n")
    env.write("procs/GATE.md", GATE)
    opener = fresh(env)
    opener.start(opener.boot("CALLER.md"))
    env.conductor(key(env)).mount([{"doc": "procs/PUSHER.md"}])
    standing = [k for k in events.counters(env.made) if k.startswith("standing|alpha|alpha-note|alpha-mark:x")]
    if standing:
        held("an exec's push stands", "`::push alpha-note alpha-mark:x` latched at the bus")
    else:
        failures.append(f"  ✗ exec push                   {list(events.counters(env.made))}")
    expect("exec-mount", lambda: env.conductor(key(env)).mount([{"doc": "procs/MOUNTER.md"}]))

    # --- -stats counts the execs ------------------------------------------------------
    stats = env.cli("-stats", key(env)).stdout
    if "3 exec(s)" in stats:
        held("-stats counts the execs", "the run's line says 3 exec(s)")
    else:
        failures.append(f"  ✗ stats exec                  {stats[-300:]!r}")

    # --- several exec on one document: the derived order, the preferences ------------
    def ordered(extra_over: str = "", extra_base: str = "") -> list[str]:
        made = bench.env("ordering").made
        _alpha(made, entry_exec="stamp base", entry_extra=extra_base)
        _pin(made, "beta", BETA, {
            "overlays/ENTRY.md": OVERLAY.format(extra=extra_over),
            "skills/pp-beta/SKILL.md": CONTRACT.format(name="pp-beta", said="the beta witness's skill"),
            "skills/pp-beta/pp-beta.py": SKILL.format(who="beta"),
        })
        (made / "procs").mkdir(exist_ok=True)
        (made / "procs" / "CALLER.md").write_text(CALLER.format(name="CALLER", callee="ENTRY"), encoding="utf-8")
        compiling.build_tools(made)
        from conductor import discovery
        member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
        from conductor import Conductor
        opener = Conductor(member, discovery.siblings_around(member), made / ".sys" / "engine" / "pp.py")
        opener.start(opener.boot("CALLER.md"))
        path = made.parent / RECORD
        return path.read_text(encoding="utf-8").splitlines() if path.exists() else []

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
    return 0
