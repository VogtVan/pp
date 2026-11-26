"""Scenario `import` -- the pattern `composition/import`, played from its demonstration:
- a document that writes `imports:` brings the documents it names before itself, in the order
  written: a skill mounts TASK, and CHARTER then GROUND enter the view before it, their laws and
  their offer ahead of TASK's, their bodies served, each imported entry naming its importer
- the import is transitive and a document already in the view does not enter twice: GROUND
  mounted first, TASK then enters alone
- an imported document lives as long as its importer: mounted for the passage, it leaves at the
  park with it; mounted at a point, it comes back with it at the next passage
- an importer that leaves by `replaces` takes its imports with it, except the one another
  document in the view still imports: that one stays, naming that document; the trace says
  `released`
- a proc that imports holds its imports for its frame's life: they enter once at its entry, before
  its `initialize` contributors, their laws at the park and at the next passage, their bodies
  served once; they leave with the frame when it pops, the trace says `released`
- the offer of an imported document comes before its importer's; the trace `initialize` of a proc that
  imports names its imports
- a passage entry a proc imports, directly or through its imports, takes the frame's hold and names its
  importer of the frame; a held importer keeps a passage entry it imports at the park, its hold given,
  as its entry recorded it -- its file rewritten without its imports changes nothing;
  a frame's import another entry still imports stays at the pop, naming that entry
- each imported document is judged by its own `when:`; the lines of one block enter in the order
  written; an imported document's `serve:` rows are served with it
- an overlay adds imports to its document: an overlay of STUDY, an overlay of an instance's TURN
- refusals: a cycle `import-cycle` at the build and at the mount, a name nowhere
  `reference-unknown`, a value badly written `imports-malformed` (a list, two names on a line, an
  overlay that removes), the host's table gone `mounts-gone`, the file named
"""
from __future__ import annotations

import contextlib
import io
import json

import pp as pp_cli
from conductor import Refusal, compiling, persistence, render
from tests.harness import body_of, codes, demonstrated, demos, na_proof, plant, stepped, traced

DRAWER, PATTERN = "composition", "import"
DEMOS = ("AUDIT.md", "CHARTER.md", "DESK.md", "GROUND.md", "LEDGER.md", "PIN.md", "POST.md",
         "ROUND.md", "SEAL.md", "STUDY.md", "SWITCH.md", "TASK.md")
DEMO = demos(DRAWER, PATTERN)
GROUNDS = ("CHARTER.md", "GROUND.md", "LEDGER.md")
NEXT = "the next message"
SKILL = "def main(argv):\n    print('::mount ' + argv[0])\n    return 0\n"


def _mount(env, key: str, entries) -> str:
    """-> what a skill that prints `::mount <entries>` says, played in run `key`."""
    probe = env.write("probe-mount.py", SKILL)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        pp_cli._played(env.conductor(key), probe, [json.dumps(entries)], "probe-mount")
    return buffer.getvalue()


def _passage(env, key: str, first) -> list:
    """-> the blocks of one passage from `first` on, each step answered, until the run parks."""
    seen, block = [first], first
    while block is not None and not block.wait and len(seen) < 8:
        block = stepped(lambda: env.conductor(key), na_proof(block) if block.judged else "")
        seen.append(block)
    return seen


def _view(env, key: str) -> list[tuple]:
    """-> the slot's view: (address, its importer, its holder) per entry, in order."""
    return [(one["doc"], one.get("import", ""), one.get("held", ""))
            for one in persistence.mounted_of(persistence.slot_of(env.made, key))]


def _mounted(env, key: str) -> list[list[str]]:
    return [one.get("docs") for one in traced(env, key) if one.get("kind") == "mounted"]


def _ordered(laws: list[str], *wanted: str) -> bool:
    return all(one in laws for one in wanted) and [laws.index(one) for one in wanted] == sorted(
        laws.index(one) for one in wanted)


def mounted(bench) -> None:
    """A skill mounts TASK: the order, the bodies, the importers; the park takes them all."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-mounted", bare=True)
    plant(env, DRAWER, PATTERN, ("DESK.md", "TASK.md") + GROUNDS)
    opener = env.conductor()
    opened = opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    try:
        said = _mount(env, key, [{"doc": "TASK.md"}])
    except Refusal as refusal:
        failures.append(f"  ✗ the import's order          refused {refusal.code!r} -- {refusal}")
        return
    view = env.conductor(key).peek()
    laws, offer = codes(view), [one.name for one in view.tools]
    if (_view(env, key) == [("CHARTER.md", "GROUND.md", ""), ("GROUND.md", "TASK.md", ""), ("TASK.md", "", "")]
            and _ordered(laws, "IM1", "IM2", "IM3") and "LEDGER" in offer
            and body_of(DEMO / "CHARTER.md") in said and body_of(DEMO / "GROUND.md") in said
            and _mounted(env, key) == [["CHARTER.md", "GROUND.md", "TASK.md"]]):
        held("the imported enter before", "TASK mounted: CHARTER then GROUND enter before it, each naming its "
             "importer; IM1, IM2 before IM3, GROUND's offer LEDGER, both bodies served, one `mounted`")
    else:
        failures.append(f"  ✗ the import's order          view={_view(env, key)} {laws} {offer} "
                        f"mounted={_mounted(env, key)}")
    blocks = _passage(env, key, opened)
    if blocks[-1] is not None and blocks[-1].wait and _view(env, key) == []:
        held("the imported leave at the park", "the passage parks: TASK, GROUND and CHARTER leave the slot")
    else:
        failures.append(f"  ✗ the park                    view={_view(env, key)}")
    env.conductor(key).forget()

    # --- the document already in the view does not enter twice --------------------------------------
    opener = env.conductor()
    opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    _mount(env, key, [{"doc": "GROUND.md"}])
    _mount(env, key, [{"doc": "TASK.md"}])
    laws = codes(env.conductor(key).peek())
    if (_view(env, key) == [("CHARTER.md", "GROUND.md", ""), ("GROUND.md", "", ""), ("TASK.md", "", "")]
            and laws.count("IM2") == 1 and laws.count("IM1") == 1
            and _mounted(env, key) == [["CHARTER.md", "GROUND.md"], ["TASK.md"]]):
        held("a document in the view enters once", "GROUND mounted first brings CHARTER; TASK then enters "
             "alone, GROUND kept as it stood, IM1 and IM2 once")
    else:
        failures.append(f"  ✗ already in the view         view={_view(env, key)} {laws} mounted={_mounted(env, key)}")
    env.conductor(key).forget()


def posted(bench) -> None:
    """POST mounted at DESK's point imports GROUND: both leave at the park and come back together."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-posted", bare=True)
    plant(env, DRAWER, PATTERN, ("DESK.md", "POST.md") + GROUNDS)
    opener = env.conductor()
    try:
        opened = opener.start(env.made / "procs" / "DESK.md")
    except Refusal as refusal:
        failures.append(f"  ✗ the point's import          refused {refusal.code!r} -- {refusal}")
        return
    key = opener.run_id
    first = _view(env, key)
    blocks = _passage(env, key, opened)
    parked = _view(env, key)
    again = env.conductor(key).submit(NEXT)
    if (first == [("CHARTER.md", "GROUND.md", ""), ("GROUND.md", "POST.md", ""), ("POST.md", "", "")]
            and _ordered(codes(opened), "IM1", "IM2", "IM5") and blocks[-1].wait and parked == []
            and _ordered(codes(again), "IM1", "IM2", "IM5") and _view(env, key) == first
            and _mounted(env, key) == [["CHARTER.md", "GROUND.md", "POST.md"]] * 2):
        held("an import lives with its importer", "POST mounted at desk.open brings GROUND and CHARTER; the "
             "park sweeps the three, the next passage mounts them again together")
    else:
        failures.append(f"  ✗ the point's import          first={first} parked={parked} again={_view(env, key)} "
                        f"{codes(opened)} {codes(again)} mounted={_mounted(env, key)}")
    env.conductor(key).forget()


def replaced(bench) -> None:
    """TASK replaced: GROUND leaves with it, CHARTER stays -- AUDIT imports it."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-replaced", bare=True)
    plant(env, DRAWER, PATTERN, ("AUDIT.md", "DESK.md", "TASK.md") + GROUNDS)
    opener = env.conductor()
    opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    try:
        _mount(env, key, [{"doc": "TASK.md"}])
        _mount(env, key, [{"doc": "AUDIT.md"}])
        _mount(env, key, [{"doc": "LEDGER.md", "replaces": ["TASK.md"]}])
    except Refusal as refusal:
        failures.append(f"  ✗ the importer replaced       refused {refusal.code!r} -- {refusal}")
        return
    laws = codes(env.conductor(key).peek())
    released = [(sorted(one.get("docs") or []), one.get("by")) for one in traced(env, key)
                if one.get("kind") == "released"]
    if (_view(env, key) == [("CHARTER.md", "AUDIT.md", ""), ("AUDIT.md", "", ""), ("LEDGER.md", "", "")]
            and "IM1" in laws and "IM4" in laws and "IM2" not in laws and "IM3" not in laws
            and released == [(["GROUND.md", "TASK.md"], "replaces")]):
        held("an importer takes its imports out", "LEDGER replacing TASK: TASK and GROUND leave, CHARTER stays "
             "naming AUDIT, which imports it too; the trace says `released` by `replaces`")
    else:
        failures.append(f"  ✗ the importer replaced       view={_view(env, key)} {laws} released={released}")
    env.conductor(key).forget()


CRATE = ("---\nname: CRATE\nkind: doc\ndescription: an importer with an offer of its own.\n"
         "imports: |\n  GROUND.md\ntools: |\n  DESK\n---\n\nThe crate.\n")
ATTIC = "---\nname: ATTIC\nkind: proc\ndescription: a proc with a contributor at its entry.\nproc: |\n  WORK\n---\n\nThe attic.\n"
BEAM = ("---\nname: BEAM\nkind: doc\ndescription: held at the attic's entry, importing the ground.\n"
        "mount: attic.initialize\nimports: |\n  GROUND.md\n---\n\nThe beam.\n")


def offered(bench) -> None:
    """The offer of an imported document comes before its importer's."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-offered", bare=True)
    plant(env, DRAWER, PATTERN, ("DESK.md",) + GROUNDS)
    env.write("procs/CRATE.md", CRATE)
    opener = env.conductor()
    opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    _mount(env, key, [{"doc": "CRATE.md"}])
    offer = [one.name for one in env.conductor(key).peek().tools]
    if "LEDGER" in offer and "DESK" in offer and offer.index("LEDGER") < offer.index("DESK"):
        held("the imported offer comes first", f"CRATE imports GROUND: GROUND's LEDGER before CRATE's DESK ({offer})")
    else:
        failures.append(f"  ✗ the offer's order           {offer}")
    env.conductor(key).forget()


def taken_by_frame(bench) -> None:
    """A passage entry a proc imports takes the frame's hold; a held importer keeps a passage entry at the
    park; a frame's import another entry imports stays at the pop, naming that entry."""
    held, failures = bench.held, bench.failures

    # --- POST in the view, STUDY opened: GROUND and CHARTER take STUDY's hold ---------------------------
    env = bench.env("import-taken", bare=True)
    plant(env, DRAWER, PATTERN, ("DESK.md", "POST.md", "SEAL.md", "STUDY.md", "SWITCH.md") + GROUNDS)
    opener = env.conductor()
    opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    before = _view(env, key)
    try:
        studied = env.conductor(key).open("STUDY")
    except Refusal as refusal:
        failures.append(f"  ✗ the frame takes the hold     refused {refusal.code!r} -- {refusal}")
        return
    entered = _view(env, key)
    _passage(env, key, studied)
    parked, laws = _view(env, key), codes(env.conductor(key).peek())
    env.conductor(key).close()
    released = [(sorted(one.get("docs") or []), one.get("holder")) for one in traced(env, key)
                if one.get("kind") == "released"]
    if (before == [("CHARTER.md", "GROUND.md", ""), ("GROUND.md", "POST.md", ""), ("POST.md", "", "")]
            and entered == [("CHARTER.md", "GROUND.md", "1:STUDY"), ("GROUND.md", "STUDY.md", "1:STUDY"),
                            ("POST.md", "", "")]
            and parked == [("CHARTER.md", "GROUND.md", "1:STUDY"), ("GROUND.md", "STUDY.md", "1:STUDY")]
            and "IM2" in laws and not any(holder == "1:STUDY" for _, _, holder in _view(env, key))
            and (["CHARTER.md", "GROUND.md"], "1:STUDY") in released):
        held("a passage import takes the frame's hold", "POST brought GROUND and CHARTER; STUDY opened imports "
             "GROUND: both held by 1:STUDY, naming STUDY and GROUND; the park sweeps POST alone, IM2 in force; "
             "STUDY closed releases them")
    else:
        failures.append(f"  ✗ the frame takes the hold     before={before} entered={entered} parked={parked} "
                        f"{laws} after={_view(env, key)} released={released}")
    env.conductor(key).forget()

    # --- a held importer keeps a passage entry at the park ----------------------------------------------
    attic = bench.env("import-held-keeper", bare=True)
    plant(attic, DRAWER, PATTERN, ("DESK.md", "POST.md") + GROUNDS)
    attic.write("procs/ATTIC.md", ATTIC)
    attic.write("procs/BEAM.md", BEAM)
    opener = attic.conductor()
    opener.start(attic.made / "procs" / "DESK.md")
    key = opener.run_id
    opened = attic.conductor(key).open("ATTIC")
    _passage(attic, key, opened)
    if _view(attic, key) == [("CHARTER.md", "GROUND.md", "1:ATTIC"), ("GROUND.md", "BEAM.md", "1:ATTIC"),
                             ("BEAM.md", "", "1:ATTIC")]:
        held("a held importer keeps a passage entry", "BEAM, held at ATTIC's entry, imports GROUND which POST "
             "brought: at the park GROUND stays naming BEAM, CHARTER under it, both held by 1:ATTIC")
    else:
        failures.append(f"  ✗ the held keeper              view={_view(attic, key)}")
    attic.conductor(key).forget()

    # --- the entry answers, not the file: BEAM rewritten without its imports before the park ------------
    opener = attic.conductor()
    opener.start(attic.made / "procs" / "DESK.md")
    key = opener.run_id
    opened = attic.conductor(key).open("ATTIC")
    attic.write("procs/BEAM.md", BEAM.replace("imports: |\n  GROUND.md\n", ""))
    _passage(attic, key, opened)
    attic.write("procs/BEAM.md", BEAM)
    if _view(attic, key) == [("CHARTER.md", "GROUND.md", "1:ATTIC"), ("GROUND.md", "BEAM.md", "1:ATTIC"),
                             ("BEAM.md", "", "1:ATTIC")]:
        held("the entry answers, not the file", "BEAM rewritten without its `imports:` before the park: GROUND "
             "stays naming BEAM, as BEAM's entry recorded it")
    else:
        failures.append(f"  ✗ the entry answers           view={_view(attic, key)}")
    attic.conductor(key).forget()

    # --- a frame's import another entry imports stays at the pop ----------------------------------------
    rounded = bench.env("import-pop-kept", bare=True)
    plant(rounded, DRAWER, PATTERN, ("POST.md", "ROUND.md", "SEAL.md", "STUDY.md", "SWITCH.md") + GROUNDS)
    opener = rounded.conductor()
    opener.start(rounded.made / "procs" / "ROUND.md")
    key = opener.run_id
    _mount(rounded, key, [{"doc": "POST.md"}])
    after = stepped(lambda: rounded.conductor(key))
    if (after is not None and after.document == "ROUND"
            and _view(rounded, key) == [("CHARTER.md", "GROUND.md", ""), ("GROUND.md", "POST.md", ""),
                                        ("POST.md", "", "")]):
        held("a frame's import kept at the pop", "STUDY imported GROUND, then a skill mounted POST which imports "
             "it: STUDY popped, GROUND stays naming POST, CHARTER under it, none held any more")
    else:
        failures.append(f"  ✗ kept at the pop              {after and after.document} view={_view(rounded, key)}")
    rounded.conductor(key).forget()


def _switch(env, value: str) -> None:
    env.write("procs/SWITCH.md", (DEMO / "SWITCH.md").read_text(encoding="utf-8").replace(
        "open: false", f"open: {value}"))


def held_by_frame(bench) -> None:
    """STUDY imports: held by its frame, before PIN, its laws over two passages, the bodies once."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-held", bare=True)
    plant(env, DRAWER, PATTERN, ("PIN.md", "SEAL.md", "STUDY.md", "SWITCH.md") + GROUNDS)
    opener = env.conductor()
    try:
        first = opener.start(env.made / "procs" / "STUDY.md")
    except Refusal as refusal:
        failures.append(f"  ✗ the proc's import           refused {refusal.code!r} -- {refusal}")
        return
    key = opener.run_id
    shown = render(first)
    entry = _view(env, key)
    if (entry == [("CHARTER.md", "GROUND.md", "0:STUDY"), ("GROUND.md", "STUDY.md", "0:STUDY"),
                  ("PIN.md", "", "0:STUDY")]
            and _ordered(codes(first), "IM1", "IM2", "IM6") and "IM7" not in codes(first)
            and body_of(DEMO / "GROUND.md") in shown and body_of(DEMO / "CHARTER.md") in shown
            and _mounted(env, key) == [["CHARTER.md", "GROUND.md"], ["PIN.md"]]):
        held("a proc's imports enter at its entry", "STUDY opens: CHARTER and GROUND enter held by its frame, "
             "before PIN its initialize contributor; SEAL, its guard shut, does not; the bodies served")
    else:
        failures.append(f"  ✗ the proc's import           view={entry} {codes(first)} mounted={_mounted(env, key)}")
    initialized = [one.get("imports") for one in traced(env, key)
                   if one.get("kind") == "initialize" and one.get("document") == "STUDY"]
    if initialized == [["GROUND.md", "SEAL.md"]]:
        held("the entry's trace says the imports", "`initialize` of STUDY carries imports [GROUND.md, SEAL.md]")
    else:
        failures.append(f"  ✗ the initialize trace         {initialized}")
    parked, texts = [], []
    block = first
    for _ in range(2):
        seen = _passage(env, key, block)
        parked.append(env.conductor(key).peek())
        texts += [render(one) for one in seen[1:] if one is not None]
        block = env.conductor(key).submit(NEXT)
        texts.append(render(block))
    if (all(_ordered(codes(one), "IM1", "IM2", "IM6") for one in parked + [block])
            and not any(body_of(DEMO / "GROUND.md") in text for text in texts)
            and _view(env, key) == entry and len(_mounted(env, key)) == 2):
        held("the frame holds its imports", "IM1 and IM2 at both parks and the passage after, GROUND's body "
             "not served again, the view as the entry left it, nothing mounted again")
    else:
        failures.append(f"  ✗ held by the frame           {[codes(one) for one in parked]} view={_view(env, key)} "
                        f"mounted={_mounted(env, key)}")
    env.conductor(key).forget()

    # --- the guard of the imported, open ---------------------------------------------------------------
    _switch(env, "true")
    opener = env.conductor()
    opened = opener.start(env.made / "procs" / "STUDY.md")
    if "IM7" in codes(opened) and ("SEAL.md", "STUDY.md", "0:STUDY") in _view(env, opener.run_id):
        held("an import is judged by its own when:", "SWITCH open: true -- SEAL enters with STUDY, IM7 in force")
    else:
        failures.append(f"  ✗ the import's guard          {codes(opened)} view={_view(env, opener.run_id)}")
    order = [doc for doc, _, _ in _view(env, opener.run_id)]
    if order == ["CHARTER.md", "GROUND.md", "SEAL.md", "PIN.md"]:
        held("the lines enter in the order written", "STUDY imports GROUND then SEAL: the view holds CHARTER, "
             "GROUND, SEAL in that order, then PIN")
    else:
        failures.append(f"  ✗ the order written           {order}")
    opener.forget()


ROOTED = ("---\nname: ROOTED\nkind: doc\ndescription: an imported document that reads a path.\n"
          "serve: |\n  notes/basis.md\n---\n\nThe rooted document.\n")
LEAN = ("---\nname: LEAN\nkind: doc\ndescription: a document that imports ROOTED.\n"
        "imports: |\n  ROOTED.md\n---\n\nThe lean document.\n")
BASIS = "The basis a row of the imported document names."


def readings(bench) -> None:
    """An imported document's `serve:` row is served with it."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-readings", bare=True)
    plant(env, DRAWER, PATTERN, ("DESK.md",))
    env.write("procs/ROOTED.md", ROOTED)
    env.write("procs/LEAN.md", LEAN)
    (env.root / "notes").mkdir(exist_ok=True)
    (env.root / "notes" / "basis.md").write_text(BASIS + "\n", encoding="utf-8")
    opener = env.conductor()
    opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    said = _mount(env, key, [{"doc": "LEAN.md"}])
    if BASIS in said and "notes/basis.md" in said and _view(env, key) == [("ROOTED.md", "LEAN.md", ""), ("LEAN.md", "", "")]:
        held("an import brings its readings", "LEAN mounted: ROOTED enters before it, its row notes/basis.md "
             "served with it")
    else:
        failures.append(f"  ✗ the import's readings       view={_view(env, key)} {said[-300:]!r}")
    env.conductor(key).forget()


def popped(bench) -> None:
    """ROUND calls STUDY: STUDY's imports leave when its frame pops."""
    held, failures = bench.held, bench.failures
    env = bench.env("import-popped", bare=True)
    plant(env, DRAWER, PATTERN, ("ROUND.md", "SEAL.md", "STUDY.md", "SWITCH.md") + GROUNDS)
    opener = env.conductor()
    try:
        studied = opener.start(env.made / "procs" / "ROUND.md")
    except Refusal as refusal:
        failures.append(f"  ✗ the frame popped            refused {refusal.code!r} -- {refusal}")
        return
    key = opener.run_id
    inside = _view(env, key)
    rounded = stepped(lambda: env.conductor(key))
    released = [(sorted(one.get("docs") or []), one.get("holder")) for one in traced(env, key)
                if one.get("kind") == "released"]
    if (studied.document == "STUDY" and "IM2" in codes(studied)
            and inside == [("CHARTER.md", "GROUND.md", "1:STUDY"), ("GROUND.md", "STUDY.md", "1:STUDY")]
            and rounded is not None and rounded.document == "ROUND" and "IM2" not in codes(rounded)
            and "IM1" not in codes(rounded) and _view(env, key) == []
            and released == [(["CHARTER.md", "GROUND.md"], "1:STUDY")]):
        held("the imports leave with the frame", "STUDY's step carries IM2; STUDY popped, ROUND's step carries "
             "neither IM1 nor IM2, the slot empty, the trace says `released` by 1:STUDY")
    else:
        failures.append(f"  ✗ the frame popped            {studied.document}:{codes(studied)} inside={inside} "
                        f"{rounded and rounded.document}:{codes(rounded)} released={released}")
    env.conductor(key).forget()


def overlaid(bench) -> None:
    """An overlay adds imports: STUDY's, then an instance's TURN."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("import-overlay", bare=True)
    plant(env, DRAWER, PATTERN, ("AUDIT.md", "SEAL.md", "STUDY.md", "SWITCH.md") + GROUNDS)
    env.write("STUDY.md", "---\nname: STUDY\nimports: |\n  AUDIT.md\n---\n")
    opener = env.conductor()
    try:
        opened = opener.start(env.made / "procs" / "STUDY.md")
    except Refusal as refusal:
        failures.append(f"  ✗ the overlay's import        refused {refusal.code!r} -- {refusal}")
        return
    if ([doc for doc, _, _ in _view(env, opener.run_id)] == ["CHARTER.md", "GROUND.md", "AUDIT.md"]
            and _ordered(codes(opened), "IM1", "IM2", "IM4")):
        held("an overlay adds an import", "STUDY's overlay imports AUDIT: it enters after GROUND, CHARTER "
             "once for both")
    else:
        failures.append(f"  ✗ the overlay's import        view={_view(env, opener.run_id)} {codes(opened)}")
    opener.forget()
    env.write("STUDY.md", "---\nname: STUDY\nimports: |\n  -SEAL.md\n---\n")
    expect("imports-malformed", lambda: compiling.build_tools(env.made))

    turn = bench.env("import-turn")
    plant(turn, DRAWER, PATTERN, GROUNDS)
    turn.write("procs/TURN.md", "---\nname: TURN\nimports: |\n  GROUND.md\n---\n")
    built = turn.cli("-build")
    booted = turn.conductor()
    try:
        first = booted.start(booted.boot("BOOT.md"), "the first ask")
    except Refusal as refusal:
        failures.append(f"  ✗ the turn's import           refused {refusal.code!r} -- {refusal}")
        return
    if (built.returncode == 0 and _ordered(codes(first), "IM1", "IM2")
            and _view(turn, booted.run_id) == [("CHARTER.md", "GROUND.md", "1:TURN"),
                                               ("GROUND.md", "TURN.md", "1:TURN")]):
        held("an instance's TURN imports", "the overlay of TURN imports GROUND: GROUND and CHARTER held by "
             "TURN's frame from the first block")
    else:
        failures.append(f"  ✗ the turn's import           rc={built.returncode} {codes(first)} "
                        f"view={_view(turn, booted.run_id)} {built.stderr[-200:]!r}")
    booted.forget()


def refusals(bench) -> None:
    """A cycle, a name nowhere, a value badly written, the table gone."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("import-refusals", bare=True)
    plant(env, DRAWER, PATTERN, ("DESK.md",) + GROUNDS)
    knot = "---\nname: KNOT\nkind: doc\ndescription: a knot.\nimports: |\n  TIE.md\n---\n\nThe knot.\n"
    tie = "---\nname: TIE\nkind: doc\ndescription: a tie.\nimports: |\n  KNOT.md\n---\n\nThe tie.\n"
    env.write("extra/TIE.md", tie.replace("KNOT.md", "extra/KNOT.md"))
    env.write("extra/KNOT.md", knot.replace("TIE.md", "extra/TIE.md"))
    opener = env.conductor()
    opener.start(env.made / "procs" / "DESK.md")
    key = opener.run_id
    expect("import-cycle", lambda: _mount(env, key, [{"doc": "extra/KNOT.md"}]))
    if _view(env, key) == []:
        held("a refused import mounts nothing", "the cycle refused at the mount, the slot untouched")
    else:
        failures.append(f"  ✗ the refused mount           view={_view(env, key)}")
    env.conductor(key).forget()
    (env.made / "extra" / "KNOT.md").unlink()
    (env.made / "extra" / "TIE.md").unlink()

    env.write("procs/KNOT.md", knot)
    env.write("procs/TIE.md", tie)
    expect("import-cycle", lambda: compiling.build_tools(env.made))
    (env.made / "procs" / "TIE.md").unlink()
    expect("reference-unknown", lambda: compiling.build_tools(env.made))
    env.write("procs/KNOT.md", knot.replace("imports: |\n  TIE.md", "imports: [GROUND.md]"))
    expect("imports-malformed", lambda: compiling.build_tools(env.made))
    env.write("procs/KNOT.md", knot.replace("TIE.md", "GROUND.md CHARTER.md"))
    expect("imports-malformed", lambda: compiling.build_tools(env.made))
    env.write("procs/KNOT.md", knot.replace("imports: |\n  TIE.md", "mounts:\n  knot.open: GROUND.md"))
    expect("mounts-gone", lambda: compiling.build_tools(env.made))
    try:
        compiling.build_tools(env.made)
        said = ""
    except Refusal as refusal:
        said = str(refusal)
    if "KNOT.md" in said and "imports:" in said:
        held("the table gone names its file", "`mounts-gone` names KNOT.md and points to `imports:`")
    else:
        failures.append(f"  ✗ the table gone              {said!r}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    mounted(bench)
    posted(bench)
    replaced(bench)
    held_by_frame(bench)
    offered(bench)
    taken_by_frame(bench)
    readings(bench)
    popped(bench)
    overlaid(bench)
    refusals(bench)
    return 0
