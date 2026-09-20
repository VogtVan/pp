"""Scenario `hooks` -- the sockets compose their contributors (plan pp-split, batch
les-hooks-de-session):
- ONE source, the documents' `attach:`, in the requires topology of their homes then by name
  (`hooks:` retired at la-porte-unique-du-contenu)
- a contributor's guard lives on itself: `when: @Doc.field`, judged as an instruction's guard
- a payload is a skill's output, rendered at the document that names the token; a refusal is said
- the turn's sockets are HOOKed and inert without a contributor
- a contributor ORDERS itself: `order: <hook> before|after <package>` inverts the derived
  order, and two contributors that each want to come first refuse `order-cycle` (batch
  l-ordre-au-contributeur)
- a contributor declaring `mount: <socket>` is MOUNTED there instead of called: its body,
  its laws, its tools and its payloads come with the block and it asks nothing; the same
  document without the verb renders nothing, the two verbs together refuse
  `attach-and-mount`, and a mounted contributor re-enters at every lap (batch
  le-mount-au-socket)
"""
from __future__ import annotations

from conductor import Conductor, compiling, discovery, instance, render

NOTE = """---
name: {name}
kind: proc
description: a witness of the {name} socket
{extra}proc: |
  HOOK {lower}.read
---

{name} says hi
"""
WITNESS = """name: witness
version: 0.0.1
description: a package hooking the boot and providing a payload
requires: [kit]
contributes:
  sockets: [first.read]
"""

# the witness package's providers live at DOCUMENTS of its own, as every provider does
# since le-payload-au-document -- the manifest names no skill any more, and one document
# serves one skill, so two tokens with two skills make two documents
GIVER = """---
name: {name}
kind: doc
description: a provider of the witness package
provides: {token}
with: {skill}
---

{name} gives
"""
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

HOSTED brings its body
"""

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

SKILL = "#!/usr/bin/env python3\nimport sys\nprint('the witness skill says', *sys.argv[1:])\n"
BROKEN = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('the broken skill refuses\\n')\nsys.exit(2)\n"


def _pin_witness(made) -> None:
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (root / "procs" / "FIRST.md").write_text(
        NOTE.format(name="FIRST", lower="first",
                    extra="attach: boot.ready\npayloads: witness witness-broken\n"), encoding="utf-8")
    (root / "procs" / "GIVER.md").write_text(
        GIVER.format(name="GIVER", token="witness", skill="pp-witness hello"), encoding="utf-8")
    (root / "procs" / "BREAKER.md").write_text(
        GIVER.format(name="BREAKER", token="witness-broken", skill="pp-witness-broken"), encoding="utf-8")
    for name, code in (("pp-witness", SKILL), ("pp-witness-broken", BROKEN)):
        home = root / "skills" / name
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {name}\ndescription: a witness script\n---\n\n{name}\n",
                                       encoding="utf-8")
        (home / f"{name}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)


OTHER = """name: other
version: 0.0.1
description: a second package hooking the boot, to close the order loop
requires: [witness]
contributes:
  sockets: [other.read]
"""


def _pin_other(made) -> None:
    """The second package of the CYCLE: it wants to precede `witness`, which wants to
    precede it -- two preferences that loop, and the socket refuses by name."""
    root = made / ".sys" / "vendor" / "other@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(OTHER, encoding="utf-8")
    (root / "procs" / "OTHER.md").write_text(
        NOTE.format(name="OTHER", lower="other",
                    extra="attach: boot.ready\norder: |\n  boot.ready before witness\n"),
        encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["other"] = "0.0.1"
    instance.write(made, pins)


def _boot_block(env):
    opener = env.conductor()
    return opener.start(opener.boot("BOOT.md"))


def _boot(env) -> str:
    return render(_boot_block(env))


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("hooked")
    made = env.made
    _pin_witness(made)
    env.write("procs/SECOND.md", NOTE.format(name="SECOND", lower="second", extra="attach: boot.ready\n"))
    env.write("procs/GATED.md", NOTE.format(name="GATED", lower="gated", extra="attach: boot.ready\nwhen: \"@GATE.open\"\n"))
    env.write("procs/GATE.md", "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: false\n---\n\nthe gate\n")
    compiling.build_tools(made)

    # --- ONE source, the order: the package's FIRST, then the instance's SECOND --------
    first = _boot(env)
    at_first, at_second = first.find("FIRST says hi"), first.find("SECOND says hi")
    if 0 <= at_first < at_second:
        held("one source, topology then name", "every contributor attaches itself: the "
             "package's FIRST plays before the instance's SECOND")
    else:
        failures.append(f"  ✗ hook order                   first={at_first} second={at_second}")

    # --- the guard on the contributor: GATE.open false -> no block; true -> plays -----
    if "GATED says hi" not in first:
        held("a guard not due renders nothing", "GATED waits on @GATE.open: false")
    else:
        failures.append("  ✗ guard                        GATED played under a false gate")
    env.write("procs/GATE.md", "---\nname: GATE\nkind: doc\ndescription: the gate\nopen: true\n---\n\nthe gate\n")
    second = _boot(env.__class__(name=env.name, made=env.made,
                                 member=discovery.instance_member(env.engine), engine=env.engine))
    if "GATED says hi" in second:
        held("a guard due plays", "GATED rides the boot once @GATE.open is true")
    else:
        failures.append("  ✗ guard due                    GATED absent under a true gate")

    # --- the payload: the skill's output at the document that names the token --------
    if "INFORMATION — witness" in first and "the witness skill says hello" in first:
        held("a payload is a skill's output", "pp-witness hello rendered as INFORMATION — "
             "witness at FIRST's CALL")
    else:
        failures.append("  ✗ payload                      the witness section is missing")
    if "INFORMATION — witness-broken" in first and "pp-witness-broken refused (2)" in first and "SECOND says hi" in first:
        held("a refusing skill is said", "INFORMATION — witness-broken carries the refusal, the "
             "boot went on to SECOND")
    else:
        failures.append("  ✗ broken payload               the refusal was not said or stopped the boot")

    # --- the turn's sockets: hooked, inert ----------------------------------------------
    turn = instance.resolve(made, "TURN.md").read_text(encoding="utf-8")
    # --- a contributor ORDERS itself: the instance's SECOND asks to precede the package --
    env.write("procs/SECOND.md",
              NOTE.format(name="SECOND", lower="second",
                          extra="attach: boot.ready\norder: |\n  boot.ready before witness\n"))
    inverted = _boot(env)
    inv_first, inv_second = inverted.find("FIRST says hi"), inverted.find("SECOND says hi")
    if 0 <= inv_second < inv_first:
        held("a preference inverts the derived order", "SECOND declares `boot.ready before "
             "witness` and plays first -- the requires topology said the opposite")
    else:
        failures.append(f"  \u2717 order preference             first={inv_first} second={inv_second}")
    env.write("procs/SECOND.md", NOTE.format(name="SECOND", lower="second", extra="attach: boot.ready\n"))

    # --- two contributors that each want to come first: the cycle refuses, both named ---
    cycle = bench.env("hook-cycle")
    _pin_witness(cycle.made)
    (cycle.made / ".sys" / "vendor" / "witness@0.0.1" / "procs" / "FIRST.md").write_text(
        NOTE.format(name="FIRST", lower="first",
                    extra="attach: boot.ready\npayloads: witness witness-broken\n"
                          "order: |\n  boot.ready before other\n"),
        encoding="utf-8")
    _pin_other(cycle.made)
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
    if ("HOSTED brings its body" in with_verb and "H1" in codes and "SECOND" in offered
            and "the witness skill says hello" in with_verb):
        held("a mounted contributor brings", "HOSTED declares `mount: boot.ready` without a "
             "proc: its body, its law H1, its offer and its payload ride the block")
    else:
        failures.append(f"  ✗ mount at socket              codes={codes} tools={offered}")

    hosted.write("procs/HOSTED.md", HOSTED.format(verb=""))
    bare_block = _boot_block(hosted)
    without_verb = render(bare_block)
    if ("HOSTED brings its body" not in without_verb
            and "H1" not in [one.code for one in bare_block.constraints]):
        held("the verb alone carries it", "the same document without `mount:` renders nothing")
    else:
        failures.append("  ✗ mount without the verb       HOSTED rode a boot that never named it")

    # --- the two entry verbs are EXCLUSIVE ---------------------------------------------
    hosted.write("procs/HOSTED.md", HOSTED.format(verb="attach: boot.ready\nmount: boot.ready\n"))
    expect("attach-and-mount", lambda: compiling.build_tools(hosted.made))
    hosted.write("procs/HOSTED.md", HOSTED.format(verb="mount: boot.ready\n"))
    compiling.build_tools(hosted.made)

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

    bare = bench.env("bare-turn")
    boot_bare = _boot(bare)
    if ("HOOK turn.begin" in turn and "HOOK turn.end" in turn
            and "says hi" not in boot_bare
            and "**`kit`** sockets: boot.ready, turn.begin, turn.end" in boot_bare):
        held("the turn's sockets stand inert", "TURN hooks begin and end, the "
             "catalog says them, a bare instance plays no contributor")
    else:
        failures.append("  ✗ turn sockets                 missing in TURN or leaking into a bare boot")
    return 0
