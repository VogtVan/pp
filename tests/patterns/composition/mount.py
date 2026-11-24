"""Scenario `mount` -- the pattern `composition/mount`, played from its demonstration:
- a contributor that declares `mount: <socket>` enters at the host's HOOK: its body, its law and its
  offer ride the block, it asks nothing; the same document without the verb brings nothing; the two
  entry verbs together refuse `attach-and-mount`
- mounted at a socket, it comes back at every passage: the HOOK of the next passage mounts it again,
  traced once per passage, its law once at each
- the host names what mounts at its socket with `mounts:` -- on its base or on an overlay -- after the
  contributors, the body served once then spared under `proc_body_serve: once`; nothing without the
  line; a socket the host never hooks refuses `mounts-hook-unknown`, a name nowhere `reference-unknown`
- a repair that replays the host in the same passage plays its HOOK again: what the passage already
  mounted is not mounted again -- each law once among the codes of the replayed block, `mounted` traced
  once for the passage, the proof then given leads the run to its AWAIT
- a skill mounts by printing `::mount`: the document's body and law join the view, its law is asked at
  the PROVE, the end of the passage sweeps it; a mount makes no segment -- its offer routes on the segment
  of the step that stands, the one address of the output, and an entry that names a `scope` refuses;
  a mount that extends the chain already mounted adds the documents absent; an address already there
  brings no law again -- nothing when nothing is asked of it, its body served or spared when asked --,
  the slot keeping its one entry; a name nowhere `mount-missing`, a malformed
  entry `mount-invalid`
- an entry that `replaces` addresses takes out the ones mounted for the passage before it adds its own:
  their laws leave the view, a law they carried no longer collides; an address not mounted does
  nothing, an entry a frame holds stays, the trace says `released` by `replaces`; a `replaces` that
  is not a list of addresses refuses `mount-invalid`, the slot untouched
- on an output its principal holds open, a skill's mounts join that output and render no block: the principal's
  bare call serves one output, the step that stands assembled once after the last mount with the laws of every
  mount in force; without the hold, the same mounts render that step once each
"""
from __future__ import annotations

import json

import os

import pp as pp_cli
from conductor import Refusal, compiling, persistence, render
from conductor.state import context
from tests.harness import body_of, codes, demonstrated, demos, law, na_proof, plant, stepped, traced

DEMOS = ("BENCH.md", "BOTH.md", "HALL.md", "LAMP.md", "NOTES.md", "TOOLKIT.md")
DRAWER, PATTERN = "composition", "mount"
DEMO = demos(DRAWER, PATTERN)
NEXT = "the next message"
SKILL = "def main(argv):\n    print('::mount ' + argv[0])\n    return 0\n"
ECHO = ("---\nname: ECHO\nkind: doc\ndescription: a second holder of a code NOTES holds.\n"
        "constraints.production: |\n  MT2  every measure you give is said twice.\n---\n\nThe echo.\n")


def _passage(env, key: str, first) -> list:
    """-> the blocks of one passage from `first` on: each step answered -- the lines said printed --, the
    PROVE given its n/a proof, until the run parks on its AWAIT."""
    seen, block = [first], first
    while block is not None and not block.wait and len(seen) < 6:
        block = stepped(lambda: env.conductor(key), na_proof(block) if block.judged else "")
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


def replayed(bench) -> None:
    """A repair that replays the host in the same passage: the HOOK plays again, and what the
    passage already mounted -- a contributor, what the overlay's `mounts:` names -- is not mounted
    again."""
    held, failures = bench.held, bench.failures
    env = bench.env("mount-replayed", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "HALL.md", "NOTES.md", "TOOLKIT.md"))
    env.write("BENCH.md", "---\nname: BENCH\nmounts:\n  bench.open: NOTES.md\n---\n")
    compiling.build_tools(env.made)
    opener = env.conductor()
    opened = opener.start(env.made / "procs" / "BENCH.md")
    key = opener.run_id
    proving = stepped(lambda: env.conductor(key))           # BENCH's INFER printed: its PROVE
    missed = json.dumps([{"code": code, "evidence": "off", "verdict": "fail" if code == "MT2" else "n/a"}
                         for code in (proving.judged or ())])
    try:
        reopened = env.conductor(key).submit(missed)         # the fail replays BENCH: its HOOK again
    except Refusal as refusal:
        failures.append(f"  ✗ the replayed socket         refused {refusal.code!r} -- {refusal}")
        env.conductor(key).forget()
        return
    rest = _passage(env, key, reopened)
    mounted = [one.get("docs") for one in traced(env, key) if one.get("kind") == "mounted"]
    laws = codes(reopened)
    if (proving.judged and "MT2" in proving.judged and (reopened.deviation or "").strip()
            and reopened.instruction is not None and reopened.instruction.keyword == "INFER"
            and laws.count("MT1") == 1 and laws.count("MT2") == 1
            and mounted == [["TOOLKIT.md", "NOTES.md"]] and codes(opened) == laws
            and rest[-1] is not None and rest[-1].wait):
        held("a replayed socket mounts nothing again", "MT2 failed at BENCH's PROVE: the repair replays "
             "BENCH's HOOK, TOOLKIT and NOTES already in the view stay, MT1 and MT2 once each in the "
             "replayed block, `mounted` traced once for the passage; the proof then given parks the run")
    else:
        failures.append(f"  ✗ the replayed socket         {reopened.stack!r} {laws} mounted={mounted} "
                        f"deviation={reopened.deviation!r} wait={rest[-1] and rest[-1].wait}")
    env.conductor(key).forget()


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

    proving = stepped(lambda: env.conductor(key))           # BENCH's INFER printed: its PROVE
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
    again = _mount(env, key, [{"doc": "NOTES.md", "body": True}])
    routed = env.conductor(key).route("LAMP", 1)
    written = law(DRAWER, PATTERN, "NOTES.md", "MT2")
    headed = [one for one in again.splitlines() if one.startswith("▌ ") and "{" in one]
    if ("MT2" not in codes(reopened) and len(headed) == 1 and "BENCH{" in headed[0] and "NOTES" not in headed[0]
            and again.count(written) == 1 and body_of(DEMO / "NOTES.md") in again
            and len(persistence.segments_of(slot)) == 1 and routed and routed.get("frame") == "BENCH"):
        held("a mount makes no segment", f"the next passage opens without MT2; NOTES mounted with its body: one "
             f"segment, `{headed[0]}`, its body a reading there, MT2 written once in its laws, one entry in the "
             "offer map, and `LAMP@1` routes to BENCH's step")
    else:
        failures.append(f"  ✗ the mount and the segment   {codes(reopened)} {routed!r} {headed} "
                        f"written={again.count(written)} {again[:160]!r}")
    expect("address-stale", lambda: env.conductor(key).route("LAMP", 2))
    env.conductor(key).forget()


def extended(bench) -> None:
    """A mount that extends the chain already mounted: the documents already there are skipped, the
    new one enters."""
    held, failures = bench.held, bench.failures
    env = bench.env("mount-extended", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "LAMP.md", "NOTES.md"))
    opener = env.conductor()
    opener.start(env.made / "procs" / "BENCH.md")
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)
    _mount(env, key, [{"doc": "NOTES.md"}])
    _mount(env, key, [{"doc": "NOTES.md"}, {"doc": "LAMP.md"}])
    _mount(env, key, [{"doc": "NOTES.md", "body": True}])
    peeked = codes(env.conductor(key).peek())
    if ([one["doc"] for one in persistence.mounted_of(slot)] == ["NOTES.md", "LAMP.md"]
            and peeked.count("MT2") == 1 and "MT3" in peeked):
        held("the chain extends", "NOTES then NOTES and LAMP, then NOTES's "
             "body again: LAMP alone added, MT2 once")
    else:
        failures.append(f"  ✗ extended                   {persistence.mounted_of(slot)}")
    env.conductor(key).forget()


def held_open(bench) -> None:
    """A skill's mounts on an output its principal holds open (`PP_HOLD_OUTPUT`): each joins the output, no
    block is rendered; the release assembles the step that stands once -- beside the same mounts unheld."""
    held, failures = bench.held, bench.failures

    def holding(call):
        """-> what `call` returns under the principal's hold, in this process."""
        os.environ[context.HOLD] = "true"
        try:
            return call()
        finally:
            os.environ.pop(context.HOLD, None)

    def after_mounts(env, key: str) -> list[int]:
        """-> how many blocks the run's trace says after each of its mounts, in order."""
        events = traced(env, key)
        mounted = [rank for rank, one in enumerate(events) if one.get("kind") == "mounted"] + [len(events)]
        return [len([one for one in events[start:end] if one.get("kind") == "block"])
                for start, end in zip(mounted, mounted[1:])]

    def played(name: str, hold: bool):
        env = bench.env(name, bare=True)
        plant(env, DRAWER, PATTERN, ("BENCH.md", "LAMP.md", "NOTES.md"))
        conduct = holding if hold else (lambda call: call())
        opener = env.conductor()
        if hold:
            opener.open_output()
        first = conduct(lambda: opener.start(env.made / "procs" / "BENCH.md"))
        said = conduct(lambda: opener.delivered(first))
        key = opener.run_id
        conduct(lambda: _mount(env, key, [{"doc": "NOTES.md", "body": True}]))
        conduct(lambda: _mount(env, key, [{"doc": "LAMP.md", "body": True}]))
        return env, key, said

    env, key, said = played("mount-held-open", True)
    slot = persistence.slot_of(env.made, key)
    waiting, before = persistence.held_of(slot), after_mounts(env, key)
    released = env.conductor(key).release()
    in_force = [str(one).split()[0] for one in (persistence.segments_of(slot) or [{}])[-1].get("constraints", [])]
    twin, twin_key, _ = played("mount-unheld", False)
    if (waiting.get("open") is True and before == [0, 0] and after_mounts(env, key) == [0, 1]
            and not persistence.held_of(slot) and "MT2" in in_force and "MT3" in in_force
            and body_of(DEMO / "NOTES.md") in released and body_of(DEMO / "LAMP.md") in released
            and released.index(body_of(DEMO / "NOTES.md")) < released.index(body_of(DEMO / "LAMP.md"))
            and len(persistence.segments_of(slot)) == 1 and after_mounts(twin, twin_key) == [1, 1]):
        held("mounts join an output held open", "NOTES then LAMP on the output BENCH's principal holds: no block "
             "at either mount; the release renders BENCH's step once, in one segment, MT2 and MT3 in force, the "
             "two bodies read in the order they were mounted; unheld, the step renders at each mount")
    else:
        failures.append(f"  ✗ held open                   open={waiting.get('open')} before={before} "
                        f"after={after_mounts(env, key)} in_force={in_force} twin={after_mounts(twin, twin_key)} "
                        f"{said!r} {released[-300:]!r}")
    env.conductor(key).forget()
    twin.conductor(twin_key).forget()


def replaced(bench) -> None:
    """An entry's `replaces`: what is mounted for the passage and named leaves before the entry adds
    its own."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("mount-replaces", bare=True)
    plant(env, DRAWER, PATTERN, ("BENCH.md", "LAMP.md", "NOTES.md", "TOOLKIT.md"))
    toolkit = env.made / "procs" / "TOOLKIT.md"
    toolkit.write_text(toolkit.read_text(encoding="utf-8").replace("mount: bench.open", "mount: bench.initialize"),
                       encoding="utf-8")
    env.write("extra/ECHO.md", ECHO)
    opener = env.conductor()
    opener.start(env.made / "procs" / "BENCH.md")
    key = opener.run_id
    slot = persistence.slot_of(env.made, key)

    def docs() -> list[str]:
        return [one["doc"] for one in persistence.mounted_of(slot)]

    _mount(env, key, [{"doc": "NOTES.md"}])
    before = docs()
    _mount(env, key, [{"doc": "LAMP.md", "replaces": ["NOTES.md", "GHOST.md", "TOOLKIT.md"]}])
    peeked = codes(env.conductor(key).peek())
    released = [(one.get("docs"), one.get("by")) for one in traced(env, key) if one.get("kind") == "released"]
    if (before == ["TOOLKIT.md", "NOTES.md"] and docs() == ["TOOLKIT.md", "LAMP.md"]
            and "MT3" in peeked and "MT1" in peeked and "MT2" not in peeked
            and released == [(["NOTES.md"], "replaces")]):
        held("an entry replaces what it names", "LAMP replacing NOTES, GHOST and TOOLKIT: NOTES "
             "leaves the slot and MT2 the view, GHOST mounted nowhere does nothing, TOOLKIT held by BENCH's "
             "frame stays with MT1; the trace says `released` by `replaces`")
    else:
        failures.append(f"  ✗ replaces                    before={before} after={docs()} {peeked} released={released}")

    _mount(env, key, [{"doc": "NOTES.md"}])
    expect("mount-collision", lambda: _mount(env, key, [{"doc": "extra/ECHO.md"}]))
    standing = docs()
    expect("mount-invalid", lambda: _mount(env, key, [{"doc": "extra/ECHO.md", "replaces": "NOTES.md"}]))
    expect("mount-invalid", lambda: _mount(env, key, [{"doc": "extra/ECHO.md", "replaces": [3]}]))
    unchanged = docs() == standing
    _mount(env, key, [{"doc": "extra/ECHO.md", "replaces": ["NOTES.md"]}])
    peeked = codes(env.conductor(key).peek())
    if unchanged and docs() == ["TOOLKIT.md", "LAMP.md", "extra/ECHO.md"] and peeked.count("MT2") == 1:
        held("a replaced law no longer collides", "ECHO carries MT2 like NOTES: refused beside "
             "it, entered once it replaces it; a malformed `replaces` refused, the slot untouched")
    else:
        failures.append(f"  ✗ replaced collision         unchanged={unchanged} {docs()} {peeked}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    contributor(bench)
    host(bench)
    replayed(bench)
    directive(bench)
    extended(bench)
    held_open(bench)
    replaced(bench)
    return 0
