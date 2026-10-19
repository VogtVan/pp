"""Scenario `sockets` -- how the sockets compose their contributors and where they cut:
- ONE source, the documents' `attach:`, in the requires topology of their homes then by name;
  a contributor's guard lives on itself (`when: @Doc.field`, judged as an instruction's
  guard); a payload is a skill's output rendered at the document that names the token, a
  refusal said; a contributor ORDERS itself (`order: <hook> before|after <package>` inverts
  the derived order), two that each want to come first refuse `order-cycle`; a contributor
  declaring `mount: <socket>` is MOUNTED there -- its body, laws, tools and payloads ride the
  block, it asks nothing --, the same document without the verb renders nothing, the two verbs
  together refuse `attach-and-mount`, a mounted contributor re-enters at every lap; the turn's
  sockets are declared by the base, HOOKed by TURN, said by the catalog and inert without a
  contributor
- the HOST mounts too: `mounts:` on the hooking document or on its overlay names what mounts at
  its socket -- after the contributors, guarded by the document's own `when:`, at every lap,
  its body spared once proven under `proc_body_serve: once`; nothing without the line; a socket
  the proc never hooks refuses `mounts-hook-unknown`, a name nowhere `reference-unknown`
- a contributor that declares `payloads:` serves its body WITH the section its tokens render,
  before it, and not at all when nothing rendered
- the cut at the turn's end belongs to the contributor that needs it: a floor with nothing at
  `turn.end` closes the WORK's output on FINAL; a pass opening on `§` at `turn.end` keeps the
  cut, its socket's scripted reading computed at the advance, after the work
"""
from __future__ import annotations

import os
import re

from conductor import compiling, contributions, discovery, instance, render
from tests.harness import cli, support

run = support(__file__, "run")

SAYS = "{name} says hi"
NOTE = """---
name: {name}
kind: proc
description: a witness of the {name} socket
{extra}proc: |
  HOOK {lower}.read
---

""" + SAYS + "\n"
WITNESS = """name: witness
version: 0.0.1
description: a package hooking the boot and providing a payload
requires: [kit]
contributes:
  sockets: [first.read]
"""
OTHER = """name: other
version: 0.0.1
description: a second package hooking the boot, to close the order loop
requires: [witness]
contributes:
  sockets: [other.read]
"""
FIRST = "attach: boot.ready\npayloads: witness witness-broken\n"
HOSTED_BODY = "HOSTED brings its body"
HOSTED = """---
name: HOSTED
kind: doc
description: a contributor that brings at its socket and asks nothing
{verb}payloads: witness
constraints.production: |
  H1  the hosted law binds at the socket.
tools: |
  SECOND
---

""" + HOSTED_BODY + "\n"
LOOP = """---
name: LOOP
kind: proc
cycle: true
description: a floor that hooks its socket at every lap
proc: |
  HOOK turn.begin
  WORK
---

the loop
"""
SPOKEN = "the witness skill says"
SKILL = f"#!/usr/bin/env python3\nimport sys\nprint('{SPOKEN}', *sys.argv[1:])\n"
BROKEN = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('the broken skill refuses\\n')\nsys.exit(2)\n"

INBOX_BRIEF = "INBOX brief: one line per thing that waits."
INBOX = """---
name: INBOX
kind: doc
description: what waits -- its body the brief of the section its script renders
mount: turn.begin
provides: witness-inbox
with: pp-witness-inbox say
payloads: witness-inbox
---

""" + INBOX_BRIEF + "\n"
INBOX_SKILL = "#!/usr/bin/env python3\nimport os\nprint(os.environ.get('INBOX_SAYS', ''))\n"
WAITS = "T1 waits for you"

PASS = """name: witness
version: 0.0.1
description: a package whose pass plays after the work, on its own socket
requires: [kit]
contributes:
  sockets: [thr.begin]
"""
THR = """---
name: THR
kind: proc
description: the pass -- opens on a section break, hooks its own socket, then works
attach: turn.end
proc: |
  §
  HOOK thr.begin
  WORK
---

THR: the pass.
"""
STAMP = """---
name: STAMP
kind: doc
description: a reading on the pass's socket, computed by a script that counts its runs
mount: witness.thr.begin
provides: witness-stamp
with: pp-witness-stamp now
payloads: witness-stamp
---

STAMP says how many times its script ran.
"""
STAMPED = "stamp #"
STAMP_SKILL = """#!/usr/bin/env python3
import os
p = os.environ["STAMP_FILE"]
n = sum(1 for _ in open(p)) + 1 if os.path.exists(p) else 1
open(p, "a").write(f"run {n}\\n")
print(f"%s{n}")
""" % STAMPED
FLOOR = """---
name: FLOOR
kind: proc
cycle: true
description: the floor -- the two sockets around the WORK, no section break
output: any
proc: |
  HOOK turn.begin
  WORK
  HOOK turn.end
  FINAL
---

the floor: answer the ask.
"""


def _pin_witness(made, first: str = FIRST) -> None:
    """The boot's witness package: FIRST attached at the boot with its two payloads, a
    provider that speaks and one that refuses."""
    run.vendor(made, "witness", WITNESS,
               {"FIRST": NOTE.format(name="FIRST", lower="first", extra=first),
                "GIVER": run.PROVIDER.format(name="GIVER", token="witness", skill="pp-witness hello"),
                "BREAKER": run.PROVIDER.format(name="BREAKER", token="witness-broken",
                                               skill="pp-witness-broken")},
               {"pp-witness": SKILL, "pp-witness-broken": BROKEN})


def _boot_block(env):
    opener = env.conductor()
    return opener.start(opener.boot("BOOT.md"))


def _boot(env) -> str:
    return render(_boot_block(env))


def _roomy(env) -> None:
    """The boot serves the standing orders in the block: a cap at the host's default would
    cut it, and a chunk closes on its own CONTINUE -- a case that reads the WHOLE output
    raises the cap; the fusion stays the instance's (max)."""
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "max_harness_tool_output: 25000", "max_harness_tool_output: 200000"), encoding="utf-8")


def _closing(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("▶")]


def hooks(bench) -> None:
    """The sockets compose their contributors: the source, the guard, the payload, the order,
    the mount, the turn's sockets."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("hooked")
    made = env.made
    _pin_witness(made)
    env.write("procs/SECOND.md", NOTE.format(name="SECOND", lower="second", extra="attach: boot.ready\n"))
    env.write("procs/GATED.md", NOTE.format(name="GATED", lower="gated", extra="attach: boot.ready\nwhen: \"@GATE.open\"\n"))
    env.write("procs/GATE.md", "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: false\n---\n\nthe gate\n")
    compiling.build_tools(made)
    first_says, second_says, gated_says = (SAYS.format(name=one) for one in ("FIRST", "SECOND", "GATED"))

    # --- ONE source, the order: the package's FIRST, then the instance's SECOND --------
    first = _boot(env)
    at_first, at_second = first.find(first_says), first.find(second_says)
    if 0 <= at_first < at_second:
        held("one source, topology then name", "every contributor attaches itself: the "
             "package's FIRST plays before the instance's SECOND")
    else:
        failures.append(f"  ✗ hook order                   first={at_first} second={at_second}")

    # --- the guard on the contributor: GATE.open false -> no block; true -> plays -----
    if gated_says not in first:
        held("a guard not due renders nothing", "GATED waits on @GATE.open: false")
    else:
        failures.append("  ✗ guard                        GATED played under a false gate")
    env.write("procs/GATE.md", "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: true\n---\n\nthe gate\n")
    second = _boot(env.__class__(name=env.name, made=env.made,
                                 member=discovery.instance_member(env.engine), engine=env.engine))
    if gated_says in second:
        held("a guard due plays", "GATED rides the boot once @GATE.open is true")
    else:
        failures.append("  ✗ guard due                    GATED absent under a true gate")

    # --- the payload: the skill's output at the document that names the token --------
    if "INFORMATION — witness" in first and f"{SPOKEN} hello" in first:
        held("a payload is a skill's output", "pp-witness hello rendered as INFORMATION — "
             "witness at FIRST's CALL")
    else:
        failures.append("  ✗ payload                      the witness section is missing")
    if "INFORMATION — witness-broken" in first and "pp-witness-broken refused (2)" in first and second_says in first:
        held("a refusing skill is said", "INFORMATION — witness-broken carries the refusal, the "
             "boot went on to SECOND")
    else:
        failures.append("  ✗ broken payload               the refusal was not said or stopped the boot")

    # --- a contributor ORDERS itself: the instance's SECOND asks to precede the package --
    env.write("procs/SECOND.md",
              NOTE.format(name="SECOND", lower="second",
                          extra="attach: boot.ready\norder: |\n  boot.ready before witness\n"))
    inverted = _boot(env)
    inv_first, inv_second = inverted.find(first_says), inverted.find(second_says)
    if 0 <= inv_second < inv_first:
        held("a preference inverts the derived order", "SECOND declares `boot.ready before "
             "witness` and plays first -- the requires topology said the opposite")
    else:
        failures.append(f"  ✗ order preference             first={inv_first} second={inv_second}")

    # --- two contributors that each want to come first: the cycle refuses, both named ---
    cycle = bench.env("hook-cycle")
    _pin_witness(cycle.made, FIRST + "order: |\n  boot.ready before other\n")
    run.vendor(cycle.made, "other", OTHER,
               {"OTHER": NOTE.format(name="OTHER", lower="other",
                                     extra="attach: boot.ready\norder: |\n  boot.ready before witness\n")})
    compiling.build_tools(cycle.made)
    expect("order-cycle", lambda: _boot(cycle))

    # --- the MOUNTED contributor: it enters the view at its socket, it asks nothing ----
    hosted = bench.env("hosted-socket")
    _pin_witness(hosted.made)
    hosted.write("procs/SECOND.md", NOTE.format(name="SECOND", lower="second", extra="attach: boot.ready\n"))
    hosted.write("procs/HOSTED.md", HOSTED.format(verb="mount: boot.ready\n"))
    compiling.build_tools(hosted.made)
    block = _boot_block(hosted)
    with_verb = render(block)
    codes = [one.code for one in block.constraints]
    offered = [one.name for one in block.tools]
    if (HOSTED_BODY in with_verb and "H1" in codes and "SECOND" in offered
            and f"{SPOKEN} hello" in with_verb):
        held("a mounted contributor brings", "HOSTED declares `mount: boot.ready` without a "
             "proc: its body, its law H1, its offer and its payload ride the block")
    else:
        failures.append(f"  ✗ mount at socket              codes={codes} tools={offered}")

    hosted.write("procs/HOSTED.md", HOSTED.format(verb=""))
    bare_block = _boot_block(hosted)
    without_verb = render(bare_block)
    if (HOSTED_BODY not in without_verb
            and "H1" not in [one.code for one in bare_block.constraints]):
        held("the verb alone carries it", "the same document without `mount:` renders nothing")
    else:
        failures.append("  ✗ mount without the verb       HOSTED rode a boot that never named it")

    # --- the two entry verbs are EXCLUSIVE ---------------------------------------------
    hosted.write("procs/HOSTED.md", HOSTED.format(verb="attach: boot.ready\nmount: boot.ready\n"))
    expect("attach-and-mount", lambda: compiling.build_tools(hosted.made))

    # --- the DURATION: a mounted contributor re-enters at every lap ---------------------
    lap = bench.env("hosted-laps")
    lap.write("procs/HOSTED.md", HOSTED.format(verb="mount: turn.begin\n").replace("payloads: witness\n", ""))
    lap.write("procs/SECOND.md", NOTE.format(name="SECOND", lower="second", extra="attach: boot.ready\n"))
    compiling.build_tools(lap.made)
    floor = lap.write("LOOP.md", LOOP)
    first_lap = lap.conductor().start(floor)
    second_lap = lap.conductor().submit("the first lap is done")
    first_codes = [one.code for one in first_lap.constraints]
    second_codes = [one.code for one in second_lap.constraints]
    if first_codes.count("H1") == 1 and second_codes.count("H1") == 1:
        held("a mounted contributor re-enters each lap", "the rewind sweeps the mount and "
             "the socket mounts it again -- H1 rides both laps, once each, no collision")
    else:
        failures.append(f"  ✗ mount duration               first={first_codes} second={second_codes}")

    # --- the turn's sockets: declared by the base, hooked by TURN, said, inert -----------
    bare = bench.env("bare-turn")
    boot_bare = _boot(bare)
    turn = instance.resolve(bare.made, "TURN.md").read_text(encoding="utf-8")
    declared = next((one for one in contributions.composed(bare.made)
                     if one["kind"] == "sockets" and one["package"] == "kit"), {})
    sockets = [str(one) for one in declared.get("value") or []]
    catalog = (bare.made / ".sys" / "tools.md").read_text(encoding="utf-8")
    said = next((line.split(":", 1)[1].strip().split(", ") for line in catalog.splitlines()
                 if line.startswith("- **`kit`** sockets:")), [])
    if ({"turn.begin", "turn.end"} <= set(sockets) and said == sockets
            and all(f"HOOK {one}" in turn for one in ("turn.begin", "turn.end"))
            and SAYS.format(name="").strip() not in boot_bare):
        held("the turn's sockets stand inert", "the base declares them, TURN hooks begin and end, "
             "the catalog says them, a bare instance plays no contributor")
    else:
        failures.append(f"  ✗ turn sockets                 declared={sockets} said={said} "
                        "-- missing in TURN or leaking into a bare boot")


HOST_LINE = "mounts:\n  turn.begin: HOSTED.md\n"
CONTRIBUTOR = """---
name: CONTRIB
kind: doc
description: a contributor that mounts itself at the socket
mount: turn.begin
constraints.production: |
  H2  the contributor's law binds first.
---

CONTRIB brings its body
"""


def _served(made) -> list[tuple[str, str]]:
    """-> (subject, state) of every reading the blocks' ledgers name, in trace order."""
    import json
    found = []
    for log in sorted((made / ".sys" / "state").glob("session-*.jsonl")):
        for line in filter(str.strip, log.read_text(encoding="utf-8").splitlines()):
            one = json.loads(line)
            if one.get("kind") == "block":
                found += [(row["subject"], row.get("state", "")) for row in one.get("served") or []]
    return found


def host_mounts(bench) -> None:
    """The HOST names what mounts at its socket: `mounts:` on the base or its overlay."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("host-mounts")
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    env.write("procs/HOSTED.md", HOSTED.format(verb="").replace("payloads: witness\n", ""))
    env.write("procs/SECOND.md", NOTE.format(name="SECOND", lower="second", extra="attach: boot.ready\n"))
    env.write("procs/CONTRIB.md", CONTRIBUTOR)
    floor = env.write("procs/LOOP.md", LOOP)
    env.write("LOOP.md", "---\nname: LOOP\n" + HOST_LINE + "---\n")      # the overlay names it
    compiling.build_tools(env.made)
    first = env.conductor().start(floor)
    second = env.conductor().submit("the first lap is done")
    first_codes = [one.code for one in first.constraints]
    second_codes = [one.code for one in second.constraints]
    offered = [one.name for one in first.tools]
    hosted = [state for subject, state in _served(env.made) if subject == "HOSTED"]
    if (first_codes.count("H1") == 1 and second_codes.count("H1") == 1 and "SECOND" in offered
            and "H2" in first_codes and first_codes.index("H2") < first_codes.index("H1")
            and hosted == ["served"]):
        held("the host mounts what its overlay names", "`mounts: {turn.begin: HOSTED.md}` on LOOP's "
             "overlay: H1 and the offer at both laps, once each, after the contributor's H2; the "
             "body served at the first lap only, proven")
    else:
        failures.append(f"  ✗ host mounts                  first={first_codes} second={second_codes} "
                        f"tools={offered} hosted={hosted}")

    env.write("procs/GATE.md", "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: false\n---\n\nthe gate\n")
    env.write("procs/HOSTED.md", HOSTED.format(verb='when: "@GATE.open"\n').replace("payloads: witness\n", ""))
    env.conductor().forget()
    gated = [one.code for one in env.conductor().start(floor).constraints]
    env.write("LOOP.md", "---\nname: LOOP\n---\n")
    env.write("procs/HOSTED.md", HOSTED.format(verb="").replace("payloads: witness\n", ""))
    env.conductor().forget()
    without = [one.code for one in env.conductor().start(floor).constraints]
    if "H1" not in gated and "H1" not in without and "H2" in without:
        held("the guard and the line decide", "HOSTED's own `when:` false mounts nothing; without "
             "the host's line HOSTED never rides, the contributor still does")
    else:
        failures.append(f"  ✗ host guard or line           gated={gated} without={without}")

    env.write("LOOP.md", "---\nname: LOOP\nmounts:\n  nowhere: HOSTED.md\n---\n")
    expect("mounts-hook-unknown", lambda: compiling.build_tools(env.made))
    env.write("LOOP.md", "---\nname: LOOP\nmounts:\n  turn.begin: ABSENT.md\n---\n")
    expect("reference-unknown", lambda: compiling.build_tools(env.made))


def contributor_body(bench) -> None:
    """A contributor's body rides WITH the section its tokens render, before it -- never alone."""
    held, failures = bench.held, bench.failures
    env = bench.env("contributor-body", pin=False)
    _roomy(env)
    run.vendor(env.made, "witness",
               run.PACKAGE.format(name="witness"), {"INBOX": INBOX}, {"pp-witness-inbox": INBOX_SKILL})
    env.cli("-build")
    silent = cli(env.engine, "-new", cwd=env.root, env={"INBOX_SAYS": ""})
    if silent.returncode == 0 and "INFORMATION — INBOX" not in silent.stdout and "witness-inbox" not in silent.stdout:
        held("nothing rendered, no brief", "the provider printed nothing: the block carries neither the "
             "section nor the body that explains it")
    else:
        failures.append(f"  ✗ silent contributor           rc={silent.returncode} body={'INFORMATION — INBOX' in silent.stdout} "
                        f"{silent.stderr[-160:]!r}")
    env.conductor().forget()
    spoken =cli(env.engine, "-new", cwd=env.root, env={"INBOX_SAYS": WAITS})
    text = spoken.stdout
    at_body, at_section = text.find("INFORMATION — INBOX"), text.find("INFORMATION — witness-inbox")
    if spoken.returncode == 0 and 0 <= at_body < at_section and WAITS in text and INBOX_BRIEF in text:
        held("a line rendered, the brief then its section", "the body comes with the section it explains, "
             "before it")
    else:
        failures.append(f"  ✗ speaking contributor         rc={spoken.returncode} body={at_body} section={at_section} "
                        f"{spoken.stderr[-160:]!r}")


def turn_end_cut(bench) -> None:
    """The cut at the turn's end: FINAL with nothing at `turn.end`, CONTINUE under a pass."""
    held, failures = bench.held, bench.failures

    # --- nothing at turn.end: the WORK's output closes on FINAL --------------------------
    env = bench.env("floor-alone", pin=False)
    _roomy(env)
    env.write("procs/FLOOR.md", FLOOR)
    env.cli("-build")
    opened = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "FLOOR.md"})
    if "▶ FINAL" in _closing(opened.stdout) and "▶ CONTINUE" not in opened.stdout and "FLOOR{2/4}" in opened.stdout:
        held("an empty turn's end closes on FINAL", "one output: the WORK's block, the frontier at "
             "its foot, no bare call to play")
    else:
        failures.append(f"  ✗ floor alone                  {_closing(opened.stdout)} {opened.stderr[-120:]!r}")

    # --- a pass opening on § keeps the cut; its socket's reading comes after the work ----
    env = bench.env("floor-pass", pin=False)
    _roomy(env)
    run.vendor(env.made, "witness", PASS, {"THR": THR, "STAMP": STAMP}, {"pp-witness-stamp": STAMP_SKILL})
    env.write("procs/FLOOR.md", FLOOR)
    built = env.cli("-build")
    stamp = str(env.made.parent / "stamps.txt")
    at = {"PP_DOOR": "FLOOR.md", "STAMP_FILE": stamp}
    opened = cli(env.engine, "-new", cwd=env.root, env=at)
    found = re.search(r"run (\w{6})", opened.stdout)
    runs = lambda: open(stamp).read().count("\n") if os.path.exists(stamp) else 0  # noqa: E731
    if built.returncode == 0 and found and "▶ CONTINUE" in _closing(opened.stdout) and runs() == 0 \
            and "witness-stamp" not in opened.stdout:
        held("the pass's leading § holds the cut", "the WORK's output closes on CONTINUE; the "
             "script of the pass's socket has not run")
    else:
        failures.append(f"  ✗ pass cut                     rc={built.returncode} {_closing(opened.stdout)} "
                        f"runs={runs()} {(opened.stderr or built.stderr)[-160:]!r}")
        return
    advanced = cli(env.engine, found.group(1), cwd=env.root, env=at)
    if ("INFORMATION — witness-stamp" in advanced.stdout and f"{STAMPED}1" in advanced.stdout
            and runs() == 1 and "THR" in advanced.stdout):
        held("the socket's reading comes after the work", "the advance renders the pass with the "
             "reading its script computed then, once")
    else:
        failures.append(f"  ✗ pass reading                 runs={runs()} {_closing(advanced.stdout)} "
                        f"{advanced.stderr[-160:]!r}")


def scenario(bench) -> int:
    hooks(bench)
    host_mounts(bench)
    contributor_body(bench)
    turn_end_cut(bench)
    return 0
