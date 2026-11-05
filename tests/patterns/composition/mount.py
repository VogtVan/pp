"""Scenario `mount` -- the pattern `composition/mount`, played from its demonstration:
- a contributor that declares `mount: <socket>` enters at the host's HOOK: its body, its law and its
  offer ride the block, it asks nothing; the same document without the verb brings nothing; the two
  entry verbs together refuse `attach-and-mount`
- mounted at a socket, it comes back at every passage: the HOOK of the next passage mounts it again,
  traced once per passage, its law once at each -- under both conductions
- the host names what mounts at its socket with `mounts:` -- on its base or on an overlay -- after the
  contributors, the body served once then spared under `proc_body_serve: once`; nothing without the
  line; a socket the host never hooks refuses `mounts-hook-unknown`, a name nowhere `reference-unknown`
- a skill mounts by printing `::mount`: the document's body and law join the view, its law is asked at
  the PROVE, the end of the passage sweeps it; a nested mount stacks its own addressable segment;
  a mount that extends the chain already mounted adds the documents absent; an address already there
  brings no law again -- nothing when nothing is asked of it, its body served or spared when asked --,
  the slot keeping its one entry, under both conductions; a name nowhere `mount-missing`, a malformed
  entry `mount-invalid`
- an entry that `replaces` addresses takes out the ones mounted for the passage before it adds its own:
  their laws leave the view, a law they carried no longer collides; an address not mounted does
  nothing, an entry a frame holds stays, the trace says `released` by `replaces`; a `replaces` that
  is not a list of addresses refuses `mount-invalid`, the slot untouched -- under both conductions
"""
from __future__ import annotations

import json

import pp as pp_cli
from conductor import compiling, persistence, render
from tests.harness import body_of, codes, demonstrated, demos, law, na_proof, plant, principal, traced

DEMOS = ("BENCH.md", "BOTH.md", "HALL.md", "LAMP.md", "NOTES.md", "TOOLKIT.md")
DRAWER, PATTERN = "composition", "mount"
DEMO = demos(DRAWER, PATTERN)
NEXT = "the next message"
SKILL = "def main(argv):\n    print('::mount ' + argv[0])\n    return 0\n"
ECHO = ("---\nname: ECHO\nkind: doc\ndescription: a second holder of a code NOTES holds.\n"
        "constraints.production: |\n  MT2  every measure you give is said twice.\n---\n\nThe echo.\n")


def _passage(env, key: str, first) -> list:
    """-> the blocks of one passage from `first` on: each step answered, the PROVE given its n/a
    proof, until the run parks on its AWAIT."""
    seen, block = [first], first
    while block is not None and not block.wait and len(seen) < 6:
        block = env.conductor(key).submit(na_proof(block) if block.judged else "")
        seen.append(block)
    return seen


def _mount(env, key: str, entries) -> str:
    """-> what a skill that prints `::mount <entries>` says, played in run `key` -- the skill is
    written at the test's time, never a demonstration."""
    import contextlib
    import io
    probe = env.write("probe-mount.py", SKILL)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        pp_cli._played(env.conductor(key), probe,
                       [entries if isinstance(entries, str) else json.dumps(entries)], "probe-mount")
    return buffer.getvalue()


def contributor(bench) -> None:
    """`mount: <socket>`: what it brings, the verb alone, the two verbs, one passage each."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("mount", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "HALL.md", "NOTES.md", "TOOLKIT.md"))
    bench_doc = env.made / "procs" / "BENCH.md"
    opener = env.conductor()
    opened = opener.start(bench_doc)
    key = opener.run_id
    shown = render(opened)
    if (opened.document == "BENCH" and opened.instruction.keyword == "INFER"
            and body_of(DEMO / "TOOLKIT.md") in shown and "MT1" in codes(opened)
            and "HALL" in [one.name for one in opened.tools] and "MT2" not in codes(opened)):
        held("a mounted contributor brings", "TOOLKIT enters at BENCH's HOOK: its body, MT1 and its "
             "offer HALL ride BENCH's own step; NOTES, named by no line, stays out")
    else:
        failures.append(f"  ✗ the contributor             {opened.stack!r} {codes(opened)}")

    # --- one passage: the next passage's HOOK mounts it again, its law once at each ------------
    first = _passage(env, key, opened)
    asked = [one for one in first if one is not None and one.judged]
    second = env.conductor(key).submit(NEXT)
    mounted = [one.get("docs") for one in traced(env, key) if one.get("kind") == "mounted"]
    if (asked and "MT1" in asked[0].judged and first[-1].wait
            and mounted == [["TOOLKIT.md"], ["TOOLKIT.md"]]
            and codes(opened).count("MT1") == 1 and codes(second).count("MT1") == 1):
        held("a mount comes back at each passage", "MT1 asked at BENCH's PROVE; the next message's "
             "HOOK mounts TOOLKIT again, traced `mounted` once per passage, MT1 once at each")
    else:
        failures.append(f"  ✗ each passage                asked={[one.judged for one in asked]} "
                        f"mounted={mounted} first={codes(opened)} second={codes(second)}")
    env.conductor(key).forget()

    # --- the same passages under the principal's conduction -----------------------------------
    led = bench.env("mount-principal", bare=True)
    plant(led, DRAWER, PATTERN, ("BENCH.md", "HALL.md", "NOTES.md", "TOOLKIT.md"))
    led_opener = led.conductor()
    led_opened = principal(lambda: led_opener.start(led.made / "procs" / "BENCH.md"))
    led_key = led_opener.run_id
    led_first = principal(lambda: _passage(led, led_key, led_opened))
    led_second = principal(lambda: led.conductor(led_key).submit(NEXT))
    led_mounted = [one.get("docs") for one in traced(led, led_key) if one.get("kind") == "mounted"]
    if (led_first[-1] is not None and led_first[-1].wait and led_mounted == [["TOOLKIT.md"], ["TOOLKIT.md"]]
            and codes(led_opened).count("MT1") == 1 and codes(led_second).count("MT1") == 1):
        held("each passage under the principal", "the same mount at each passage when the principal "
             "conducts: the run parks, the next message's HOOK mounts TOOLKIT again")
    else:
        failures.append(f"  ✗ under the principal         {[b and b.stack for b in led_first]} "
                        f"mounted={led_mounted} second={codes(led_second)}")
    led.conductor(led_key).forget()

    # --- the verb alone carries it -------------------------------------------------------------
    toolkit = env.made / "procs" / "TOOLKIT.md"
    toolkit.write_text(toolkit.read_text(encoding="utf-8").replace("mount: bench.open\n", ""),
                       encoding="utf-8")
    bare = env.conductor()
    plain = bare.start(bench_doc)
    if body_of(DEMO / "TOOLKIT.md") not in render(plain) and "MT1" not in codes(plain):
        held("the verb alone carries it", "TOOLKIT without its `mount:` line brings nothing to BENCH")
    else:
        failures.append(f"  ✗ without the verb            {codes(plain)}")
    bare.forget()

    # --- the two entry verbs are exclusive -----------------------------------------------------
    both = bench.env("mount-both", bare=True)
    plant(both, DRAWER, PATTERN, ("BENCH.md", "BOTH.md"))
    expect("attach-and-mount", lambda: compiling.build_tools(both.made))


def host(bench) -> None:
    """`mounts:` on the host, on its base or an overlay: after the contributors, spared once proven."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("mount-host")
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    plant(env, DRAWER, PATTERN, ("HALL.md", "LAMP.md", "NOTES.md"))
    compiling.build_tools(env.made)
    opener = env.conductor()
    opened = opener.start(env.made / "procs" / "HALL.md")
    key = opener.run_id
    _passage(env, key, opened)
    again = env.conductor(key).submit(NEXT)
    first_codes, second_codes = codes(opened), codes(again)
    notes = [row.get("state") for one in traced(env, key) if one.get("kind") == "block"
             for row in one.get("served") or [] if row.get("subject") == "NOTES"]
    if (first_codes.count("MT2") == 1 and second_codes.count("MT2") == 1
            and "MT3" in first_codes and first_codes.index("MT3") < first_codes.index("MT2")
            and "LAMP" in [one.name for one in opened.tools] and notes == ["served", "spared"]):
        held("the host mounts what its line names", "HALL's `mounts:` brings NOTES after LAMP's "
             "contributor, MT2 and its offer at both passages; the body served, then spared once proven")
    else:
        failures.append(f"  ✗ the host's line             first={first_codes} second={second_codes} notes={notes}")
    env.conductor(key).forget()

    # --- an overlay of the host names it too; a socket never hooked, a name nowhere ------------
    over = bench.env("mount-overlay", bare=True)
    plant(over, DRAWER, PATTERN, ("BENCH.md", "HALL.md", "NOTES.md", "TOOLKIT.md"))
    over.write("BENCH.md", "---\nname: BENCH\nmounts:\n  bench.open: NOTES.md\n---\n")
    compiling.build_tools(over.made)
    opener = over.conductor()
    overlaid = opener.start(over.made / "procs" / "BENCH.md")
    laws = codes(overlaid)
    if "MT2" in laws and "MT1" in laws and laws.index("MT1") < laws.index("MT2"):
        held("an overlay of the host names a mount", "the overlay's `mounts:` brings NOTES to BENCH, "
             "after TOOLKIT's contributor")
    else:
        failures.append(f"  ✗ the overlay's line          {laws}")
    opener.forget()
    over.write("BENCH.md", "---\nname: BENCH\nmounts:\n  nowhere.open: NOTES.md\n---\n")
    expect("mounts-hook-unknown", lambda: compiling.build_tools(over.made))
    over.write("BENCH.md", "---\nname: BENCH\nmounts:\n  bench.open: ABSENT.md\n---\n")
    expect("reference-unknown", lambda: compiling.build_tools(over.made))


def directive(bench) -> None:
    """`::mount` from a skill: the view, the PROVE, the sweep, the nested scope, the refusals."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("mount-directive", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "LAMP.md", "NOTES.md"))
    opener = env.conductor()
    opened = opener.start(env.made / "procs" / "BENCH.md")
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)
    said = _mount(env, key, [{"doc": "NOTES.md", "body": True}])
    view = env.conductor(key).peek()
    if (body_of(DEMO / "NOTES.md") in said and "MT2" in codes(view) and "LAMP" in [one.name for one in view.tools]
            and [one["doc"] for one in persistence.mounted_of(slot)] == ["NOTES.md"]
            and "::mount" not in said):
        held("a skill mounts by directive", "`::mount` never reaches the terminal: NOTES's body is "
             "served, MT2 and its offer LAMP join BENCH's step")
    else:
        failures.append(f"  ✗ the directive               {codes(view)} {said[:160]!r}")

    again = _mount(env, key, [{"doc": "NOTES.md"}])
    extended = _mount(env, key, [{"doc": "NOTES.md"}, {"doc": "LAMP.md"}])
    bodied = _mount(env, key, [{"doc": "NOTES.md", "body": True}])
    notes = [row.get("state") for one in traced(env, key) if one.get("kind") == "block"
             for row in one.get("served") or [] if row.get("subject") == "NOTES"]
    peeked = codes(env.conductor(key).peek())
    if ([one["doc"] for one in persistence.mounted_of(slot)] == ["NOTES.md", "LAMP.md"]
            and {"MT2", "MT3"} <= set(peeked) and peeked.count("MT2") == 1 and again and extended
            and len(notes) == 2 and all(one in ("served", "spared", "forced") for one in notes)
            and body_of(DEMO / "NOTES.md") not in again):
        held("a mount that extends the chain adds what is absent", "NOTES again brings nothing; NOTES then "
             "LAMP adds LAMP alone, MT3 beside MT2; NOTES asked for its body again: the body served again, forced or "
             f"spared ({notes[-1]}), MT2 once, the slot's one NOTES entry kept")
    else:
        failures.append(f"  ✗ the chain extended          {persistence.mounted_of(slot)} {peeked} notes={notes} "
                        f"{bodied[:120]!r}")
    expect("mount-missing", lambda: _mount(env, key, [{"doc": "GHOST.md"}]))
    expect("mount-invalid", lambda: _mount(env, key, ["NOTES.md"]))
    expect("mount-invalid", lambda: _mount(env, key, [{"doc": "NOTES.md", "scope": "beside"}]))

    proving = env.conductor(key).submit("")                 # BENCH's INFER answered: its PROVE
    stranger = env.conductor(key).submit(json.dumps(
        [{"code": "MT2", "evidence": "held", "verdict": "ok"}, {"code": "Q9", "evidence": "x", "verdict": "ok"}]))
    blocks = _passage(env, key, stranger)
    asked = [one for one in (proving,) if one is not None and one.judged]
    if (asked and "MT2" in asked[0].judged and (stranger.deviation or "").strip()
            and "Q9" in stranger.deviation and blocks[-1].wait and persistence.mounted_of(slot) == []):
        held("a mounted law is asked at the PROVE", "MT2 is owed at BENCH's PROVE like any law in "
             "force, a stranger code is refused; the run parks and the end of the passage sweeps the mount")
    else:
        failures.append(f"  ✗ the PROVE and the sweep     {[one.judged for one in asked]} "
                        f"{persistence.mounted_of(slot)} {stranger.deviation!r}")

    reopened = env.conductor(key).submit(NEXT)
    nested = _mount(env, key, [{"doc": "NOTES.md", "scope": "nested", "body": True}])
    routed = env.conductor(key).route("LAMP", 1)
    written = law(DRAWER, PATTERN, "NOTES.md", "MT2")
    if ("MT2" not in codes(reopened) and "▌ [2]" in nested and "▸ NOTES" in nested
            and written in nested.split("▌ [2]")[0] and nested.count(written) == 1 and "[MT2" in nested
            and body_of(DEMO / "NOTES.md") in nested.split("▌ [2]")[0]
            and routed and routed.get("frame") == "NOTES"):
        held("a nested mount stacks its segment", "the next passage opens without MT2; mounted "
             "nested, NOTES takes its own numbered segment, its law written there once and held as a "
             "code at the pending step, and `LAMP@1` routes to it")
    else:
        failures.append(f"  ✗ the nested scope            {codes(reopened)} {routed!r} {nested[:160]!r}")
    env.conductor(key).forget()


def extended(bench) -> None:
    """A mount that extends the chain already mounted, in a run its principal conducts: the documents
    already there are skipped, the new one enters -- the same state as in the LLM's run."""
    held, failures = bench.held, bench.failures
    env = bench.env("mount-extended", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "LAMP.md", "NOTES.md"))
    opener = env.conductor()
    principal(lambda: opener.start(env.made / "procs" / "BENCH.md"))
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)
    _mount(env, key, [{"doc": "NOTES.md"}])
    _mount(env, key, [{"doc": "NOTES.md"}, {"doc": "LAMP.md"}])
    _mount(env, key, [{"doc": "NOTES.md", "body": True}])
    peeked = codes(principal(lambda: env.conductor(key).peek()))
    if (persistence.mode_of(slot) == persistence.PRINCIPAL
            and [one["doc"] for one in persistence.mounted_of(slot)] == ["NOTES.md", "LAMP.md"]
            and peeked.count("MT2") == 1 and "MT3" in peeked):
        held("the chain extends under the principal's conduction", "NOTES then NOTES and LAMP, then NOTES's "
             "body again: LAMP alone added, MT2 once, as in the LLM's run")
    else:
        failures.append(f"  ✗ extended, principal        {persistence.mode_of(slot)} {persistence.mounted_of(slot)}")
    env.conductor(key).forget()


def replaced(bench, led: bool) -> None:
    """An entry's `replaces`: what is mounted for the passage and named leaves before the entry adds
    its own -- the run conducted by the LLM, or by its principal (`led`)."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    conduct = principal if led else (lambda call: call())
    who = "the principal" if led else "the LLM"
    env = bench.env(f"mount-replaces-{'principal' if led else 'llm'}", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "LAMP.md", "NOTES.md", "TOOLKIT.md"))
    toolkit = env.made / "procs" / "TOOLKIT.md"
    toolkit.write_text(toolkit.read_text(encoding="utf-8").replace("mount: bench.open", "mount: bench.initialize"),
                       encoding="utf-8")
    env.write("extra/ECHO.md", ECHO)
    opener = env.conductor()
    conduct(lambda: opener.start(env.made / "procs" / "BENCH.md"))
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)

    def docs() -> list[str]:
        return [one["doc"] for one in persistence.mounted_of(slot)]

    _mount(env, key, [{"doc": "NOTES.md"}])
    before = docs()
    _mount(env, key, [{"doc": "LAMP.md", "replaces": ["NOTES.md", "GHOST.md", "TOOLKIT.md"]}])
    peeked = codes(conduct(lambda: env.conductor(key).peek()))
    released = [(one.get("docs"), one.get("by")) for one in traced(env, key) if one.get("kind") == "released"]
    if (before == ["TOOLKIT.md", "NOTES.md"] and docs() == ["TOOLKIT.md", "LAMP.md"]
            and "MT3" in peeked and "MT1" in peeked and "MT2" not in peeked
            and released == [(["NOTES.md"], "replaces")]):
        held(f"an entry replaces what it names ({who})", "LAMP replacing NOTES, GHOST and TOOLKIT: NOTES "
             "leaves the slot and MT2 the view, GHOST mounted nowhere does nothing, TOOLKIT held by BENCH's "
             "frame stays with MT1; the trace says `released` by `replaces`")
    else:
        failures.append(f"  ✗ replaces ({who})           before={before} after={docs()} {peeked} released={released}")

    _mount(env, key, [{"doc": "NOTES.md"}])
    expect("mount-collision", lambda: _mount(env, key, [{"doc": "extra/ECHO.md"}]))
    standing = docs()
    expect("mount-invalid", lambda: _mount(env, key, [{"doc": "extra/ECHO.md", "replaces": "NOTES.md"}]))
    expect("mount-invalid", lambda: _mount(env, key, [{"doc": "extra/ECHO.md", "replaces": [3]}]))
    unchanged = docs() == standing
    _mount(env, key, [{"doc": "extra/ECHO.md", "replaces": ["NOTES.md"]}])
    peeked = codes(conduct(lambda: env.conductor(key).peek()))
    if unchanged and docs() == ["TOOLKIT.md", "LAMP.md", "extra/ECHO.md"] and peeked.count("MT2") == 1:
        held(f"a replaced law no longer collides ({who})", "ECHO carries MT2 like NOTES: refused beside "
             "it, entered once it replaces it; a malformed `replaces` refused, the slot untouched")
    else:
        failures.append(f"  ✗ replaced collision ({who}) unchanged={unchanged} {docs()} {peeked}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    contributor(bench)
    host(bench)
    directive(bench)
    extended(bench)
    replaced(bench, led=False)
    replaced(bench, led=True)
    return 0
