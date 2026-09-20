"""Scenario `conduction` -- 33 case(s), in the monolith's order:
- every refusal reddens on the code it names
- the block: one instruction, options fed by the pipeline
- a run served but unanswered simply comes back: nothing happened
- DRIFT the tool actually WATCHED: the answer it was handed
- the pointer SURVIVES: a brand new object picks the run up
- the state IS the instruction stack: each one carries what it took and gave
- SERVE does not yield: the TOOL reads, and the document rides the next block --
- a `serve:` ROW may hold several documents -- one bare SERVE, both ride together
- a bare SERVE dequeues one `serve:` ROW -- pacing across a PICK, one row at a time
- la-section-serve: a SECTION serves whole -- three lines, one bare SERVE
- the proof is per DOCUMENT: a reading never rides twice, whatever brought it
- CONTINUE: what one output cannot hold comes on the next call
- le-rendu-a-un-motif: ONE motif -- `▌ TITLE`, flush content, no walls
- IO.2: the closing is BINARY -- CONTINUE now, FINAL later, nothing else
- `./` addresses the DECLARED root, a bare name the CURRENT member
- la-racine-du-repo: a bare name falls back to the ROOT OF THE REPO -- the
- the same CONTENT is not served twice: a run proves a reading once
- constraints: pushed on entry, re-emitted VERBATIM in every block
- CALL opens a new frame: constraints+tools ACCUMULATE, the stack shows both
- `tools:` resolves against the document's OWN `.meta` (federal, vendored)
- a PACKAGE contributes procedures: LOADED off vendor, never imported by name
- HOOK: a named socket -- whatever attaches is CALLed there, marked injected
- one constraint, ONE holder: the registry is what makes a duplicate visible
- skills AND procs compile into ONE catalog (TOOLS), and the drop is never silent
- resuming must KEEP the checkout: looking the name up would lose a worktree
- a document that changed under a saved run is refused, not guessed
- metrics: what is served is weighed, part by part, and the parts add up
- the CLI is exercised too: it bit once because nothing covered it
- the plan package's TURN overlay: the plan mode rides every turn
- the serve doctrine rides the procs: references above, code in sections
- the packages' overlay order is the REQUIRES topology: the client wins
- the catalog addresses contracts unpinned: names resolve, vendor paths die
- the confederation: a tagged step crosses at the NEXT's own computation

The ADMIN's conditional spaces died with their subject (batch
l-administration-du-package): the engine names no role, the coordination is a SETTING
of the federation package, and `<package>/admin/` is not a space any more.
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from conductor import Conductor, Stack, render, revive, compiling, discovery, instance, metrics, navigation, persistence, reading
from tests.harness import PLAYABLE, REFUSED, document, session_of, PRODUCT_ENGINE



def scenario(bench) -> int:
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    proven_engine = PRODUCT_ENGINE
    # --- the first environment: three instances side by side, `core` the home
    town = bench.town(["core", "perso", "sw7-hub"])
    siblings = town.siblings
    home = town["core"].member
    script = town["core"].engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")


    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, siblings, script, "t")


    # --- every refusal reddens on the code it names ------------------------------------
    for code, text in REFUSED:
        expect(code, lambda t=text: conductor().start(document(t)))
    expect("document-missing", lambda: conductor().start(Path("/nowhere/DOC.md")))
    expect("unknown-member", lambda: discovery.member(siblings, "nobody"))
    expect("stack-empty", lambda: navigation.current(Stack()))

    # a run that finishes without ever yielding still ENDS ON A BLOCK: the terminal
    # order rides with the floor's constraints -- the agent never decides on a bare drain
    finished = conductor().start(document("---\nname: X\nproc: |\n  HOOK done\n---\n"))
    if over(finished):
        held("a run with no yield", "ends on the COMPLETION block -- constraints on screen")
    else:
        failures.append("  ✗ a no-yield run did not end on a completion block")

    (home.meta / "HFORMS.md").write_text(
        "---\nname: HFORMS\ndescription: bench formats\nformats: |\n"
        "  json  inline  one valid JSON value\n---\n", encoding="utf-8")
    playable = document(PLAYABLE)

    # --- the block: one instruction, options fed by the pipeline -----------------------
    conductor().forget()
    chained = conductor().resume(document(
        "---\nname: C\nproc: |\n  HOOK warp\n  INFER\n---\n"))
    if chained.instruction.keyword == "INFER" and (chained.position, chained.total) == (2, 2):
        held("the yielding instruction", "INFER at 2/2 -- HOOK chained without yielding")
    else:
        failures.append(f"  ✗ yielding instruction      {chained.instruction} {chained.position}/{chained.total}")

    conductor().forget()
    conductor().resume(playable)
    block = conductor().submit('["core", "perso", "sw7-hub"]')
    if list(block.options) == ["core", "perso", "sw7-hub"] and block.output == "options":
        held("options and output", "fed by the pipeline, and the form is a NAME of the enumeration")
    else:
        failures.append(f"  ✗ options / output          {block.options} / {block.output}")

    rendered = render(block)
    missing = [f for f in ("OPTIONS", "INSTRUCTION", "CONTINUE")
               if f not in rendered]
    pick_lines = [l for l in rendered.splitlines() if l.strip().startswith("PICK")]
    if (not missing and "▌ OUTPUT" not in rendered
            and len(pick_lines) == 1 and "options => tool" in pick_lines[0]):
        held("the block's shape", "three sections, ONE instruction line -- the form and "
             "channel ride it as its suffix, the OUTPUT section is gone")
    else:
        failures.append(f"  ✗ block shape               {missing} {pick_lines!r}")

    if "IN CHAT" not in rendered:
        held("no IN CHAT reminder", "the agent narrates on its own -- the block doesn't nag")
    else:
        failures.append("  ✗ IN CHAT still rendered")

    # --- a run served but unanswered simply comes back: nothing happened -------------
    # (the root BODY rode the OPENING block once -- re-serves are compared to each other)
    again = conductor().resume(playable)
    again2 = conductor().resume(playable)
    if render(again2) == render(again) and again2.instruction.repairs == 0:
        held("a resume re-serves", "the very same block — the tool holds nothing against anyone")
    else:
        failures.append(f"  ✗ re-served                 repairs={again2.instruction.repairs}")

    # --- DRIFT the tool actually WATCHED: the answer it was handed -------------------
    # (a repair replays the document to its FIRST yield -- the producer re-feeds between)
    wrong = conductor().submit("nobody")
    conductor().submit('["core", "perso", "sw7-hub"]')
    empty = conductor().submit("")
    if ("not in OPTIONS" in wrong.deviation and "empty answer" in empty.deviation
            and empty.repair == 2):
        held("a wrong and an empty answer", "each named, each counted — REPAIR 1 then 2")
    else:
        failures.append(f"  ✗ wrong/empty               {wrong.deviation!r} / {empty.deviation!r}")

    conductor().submit('["core", "perso", "sw7-hub"]')
    conductor().submit("nobody")
    conductor().submit('["core", "perso", "sw7-hub"]')
    expect("repair-exhausted", lambda: conductor().submit("nobody"))

    if "REPAIR" in render(wrong) and "DEVIATION" in render(wrong):
        held("a repair block says so", "REPAIR in the heading, DEVIATION in the body")
    else:
        failures.append("  ✗ a repair block looks like a normal one")

    # --- the pointer SURVIVES: a brand new object picks the run up --------------------
    conductor().forget()
    conductor().resume(playable)
    conductor().submit('["core", "perso", "sw7-hub"]')
    if over(conductor().submit("sw7-hub")):
        held("the run completes", "the last answer landed; the COMPLETION block closes it")
    else:
        failures.append("  ✗ completion                no completion block after the last step")

    member, stack, _, _, _, _, _, _ = persistence.restore(session_of(home.meta), revive)
    steps = stack.frames[-1].procedure.instructions
    if member == "core" and all(one.done for one in steps):
        held("the pointer survived", "reloaded from disk by another object -- still home")
    else:
        failures.append(f"  ✗ pointer survival          {member} / {[s.done for s in steps]}")

    # --- the state IS the instruction stack: each one carries what it took and gave ----
    if (steps[0].taken is None and steps[0].given == ["core", "perso", "sw7-hub"]
            and steps[1].taken == steps[0].given and steps[1].given == "sw7-hub"):
        held("the pipeline", "each instruction takes what the one before it gave")
    else:
        failures.append(f"  ✗ pipeline                  {[(s.taken, s.given) for s in steps]}")

    # --- SERVE does not yield: the TOOL reads, and the document rides the next block --
    reader = conductor()
    reader.forget()
    riding = reader.start(document("---\nname: X\nproc: |\n  HOOK warp\n"
                                   "  SERVE TAGGED.md\n  INFER\n---\n"))
    if [name for name, _ in riding.payloads] == ["TAGGED.md"] and riding.instruction.keyword == "INFER":
        held("SERVE rides the block", "the tool read it; the agent is asked nothing about it")
    else:
        failures.append(f"  ✗ SERVE payload             {[n for n, _ in riding.payloads]}")

    reader.forget()
    closing = reader.start(document("---\nname: X\nproc: |\n  SERVE TAGGED.md\n---\n"))
    if over(closing) and [n for n, _ in closing.payloads] == ["TAGGED.md"] \
            and "some corpus" in closing.payloads[0][1]:
        held("served with nothing to ask", "the payload rides the COMPLETION block — never a bare drain")
    else:
        failures.append("  ✗ a payload was swallowed at completion")

    # --- a `serve:` ROW may hold several documents -- one bare SERVE, both ride together ----
    (home.meta / "UNO.md").write_text("uno\n", encoding="utf-8")
    (home.meta / "DOS.md").write_text("dos\n", encoding="utf-8")
    bundled = document("---\nname: X\nserve: |\n  UNO.md DOS.md\nproc: |\n  SERVE\n---\n")
    together = conductor()
    together.forget()
    bundled_end = together.start(bundled)
    if over(bundled_end) and bundled_end.payloads == (("UNO.md", "uno"), ("DOS.md", "dos")):
        held("one ROW, one SERVE", "UNO and DOS ride the SAME call, untagged -- the row decides the batch")
    else:
        failures.append(f"  ✗ bundled row               {bundled_end and bundled_end.payloads}")
    together.forget()

    # --- a bare SERVE dequeues one `serve:` ROW -- pacing across a PICK, one row at a time ----
    (home.meta / "FIRST.md").write_text("first\n", encoding="utf-8")
    (home.meta / "SECOND.md").write_text("second\n", encoding="utf-8")
    paced = document("---\nname: X\nserve: |\n  FIRST.md\n\n  SECOND.md\nproc: |\n"
                     "  SERVE\n  INFER\n  SERVE\n---\n")
    pacer = conductor()
    pacer.forget()
    first_block = pacer.start(paced)
    if ([n for n, _ in first_block.payloads] == ["FIRST.md"]
            and first_block.instruction.keyword == "INFER"):
        held("a bare SERVE reads one SECTION", "FIRST's paragraph rides this block; SECOND's waits its turn")
    else:
        failures.append(f"  ✗ paced serve — first block {first_block.payloads} "
                        f"/ {first_block.instruction}")
    paced_end = pacer.submit("")
    if over(paced_end) and paced_end.payloads == (("SECOND.md", "second"),):
        held("the next bare SERVE follows", "SECOND's section rides only once the PICK is answered")
    else:
        failures.append(f"  ✗ paced serve — second entry {paced_end and paced_end.payloads}")
    pacer.forget()

    expect("serve-exhausted", lambda: conductor().start(
        document("---\nname: X\nserve: |\n  TAGGED.md\nproc: |\n  SERVE\n  SERVE\n---\n")))

    # --- la-section-serve: a SECTION serves whole -- three lines, one bare SERVE --------
    (home.meta / "TRES.md").write_text("tres\n", encoding="utf-8")
    whole_section = document("---\nname: X\nserve: |\n  UNO.md\n  DOS.md\n  TRES.md\nproc: |\n"
                             "  SERVE\n  INFER\n---\n")
    sectioned = conductor()
    sectioned.forget()
    section_block = sectioned.start(whole_section)
    if ([n for n, _ in section_block.payloads] == ["UNO.md", "DOS.md", "TRES.md"]
            and section_block.instruction.keyword == "INFER"):
        held("a section serves WHOLE", "three lines, one SERVE -- the paragraph is the unit, "
             "the line never beats the rhythm")
    else:
        failures.append(f"  ✗ whole section             {section_block.payloads}")
    sectioned.forget()

    # --- the proof is per DOCUMENT: a reading never rides twice, whatever brought it ----
    twice = document("---\nname: X\nserve: |\n  UNO.md DOS.md\n\n  UNO.md TRES.md\nproc: |\n"
                     "  SERVE\n  INFER\n  SERVE\n  INFER\n  SERVE DOS.md\n---\n")
    once_c = conductor()
    once_c.forget()
    once_c.start(twice)
    second = once_c.submit("")            # the chat INFER takes nothing back: the bare advance
    second_texts = dict(second.payloads)
    third = once_c.submit("")
    third_texts = dict(third.payloads) if third else {}
    if ([n for n, _ in second.payloads] == ["TRES.md"] and second_texts.get("TRES.md") == "tres"
            and over(third) and not third_texts):
        held("a document is proven once", "UNO in two sections rides once, the second section "
             "renders nothing for it; an explicit SERVE DOS.md after DOS's section renders nothing")
    else:
        failures.append(f"  ✗ proven once               {second.payloads} / {third and third.payloads}")
    once_c.forget()

    # --- le-rendu-a-un-motif: ONE motif -- `▌ TITLE`, flush content, no walls ----------
    cut2 = conductor()
    (home.meta / "LONG.md").write_text("a served line\n", encoding="utf-8")
    first_chunk = cut2.start(document("---\nname: X\nproc: |\n  SERVE LONG.md\n---\n"))
    if "▌ INFORMATION — LONG" in render(first_chunk):
        held("a served document says its title", "one titled section per reading -- the cut "
             "of an overflowing output is the block's business, never the reading's")
    else:
        failures.append(f"  ✗ served title               {first_chunk.payloads[:1]!r}")
    motif = render(first_chunk)
    if ("─" not in motif
            and all(line.startswith("▌ ") for line in motif.splitlines()
                    if line.split(" ")[0] in ("▌",))
            and motif.startswith("▌ pp · ")):
        held("one motif, two characters", "`▌ TITLE` everywhere, no rule walls, no tag in what is served")
    else:
        failures.append(f"  ✗ motif                      {motif[:120]!r}")
    cut2.forget()

    # --- IO.2: the closing is BINARY -- CONTINUE now, FINAL later, nothing else --------
    pick_render = render(conductor().resume(playable))
    if "▶ CONTINUE" in pick_render and "NEXT_CALL" not in pick_render:
        held("the closing is binary", "a PICK closes on CONTINUE -- the closing says what comes, "
             "and every block now carries its own INSTRUCTION")
    else:
        failures.append(f"  ✗ binary closing              {pick_render[-120:]!r}")
    conductor().forget()

    # --- `./` addresses the DECLARED root, a bare name the CURRENT member -------------
    (home.meta / instance.MANIFEST).parent.mkdir(exist_ok=True)
    (home.meta / instance.MANIFEST).write_text("installed: '2026-07-30'\n", encoding="utf-8")

    # --- la-racine-du-repo: a bare name falls back to the ROOT OF THE REPO -- the
    # instance and the packages keep the upper hand, a name nothing answers to is gone
    hub = discovery.member(siblings, "sw7-hub")
    (hub.path / "README.md").write_text("the repo's own readme\n", encoding="utf-8")
    (hub.path / "design").mkdir(exist_ok=True)
    (hub.path / "design" / "target.md").write_text("the target\n", encoding="utf-8")
    (hub.meta / "OWN.md").write_text("the member's\n", encoding="utf-8")
    (hub.path / "OWN.md").write_text("the repo's twin -- never served\n", encoding="utf-8")
    away = Conductor(hub, siblings, script)
    away.forget()
    at_root = dict(away.start(document(
        "---\nname: X\nproc: |\n  SERVE README.md\n  SERVE design/target.md\n  SERVE OWN.md\n"
        "  SERVE NOWHERE.md\n---\n", at=hub.meta)).payloads)
    if (at_root.get("README.md", "").startswith("the repo's own readme")
            and at_root.get("design/target.md", "").startswith("the target")
            and at_root.get("OWN.md", "").startswith("the member's")
            and "gone" in at_root.get("NOWHERE.md", "")):
        held("a bare name reaches the repo's root", "README.md and design/target.md resolve at "
             "the repo and title by their token; the instance's OWN wins over the repo's twin; "
             "NOWHERE is gone, said")
    else:
        failures.append(f"  ✗ repo root resolution      {sorted(at_root)} / {at_root}")
    away.forget()      # that run was legitimately opened in hub -- do not leave it behind

    # --- the same CONTENT is not served twice: a run proves a reading once -----------
    (home.meta / "TWICE.md").write_text("same bytes\n", encoding="utf-8")
    (home.meta / "COPY.md").write_text("same bytes\n", encoding="utf-8")
    once = conductor()
    once.forget()
    once_end = once.start(document("---\nname: X\nproc: |\n  SERVE TWICE.md\n  SERVE COPY.md\n---\n"))
    once_texts = dict(once_end.payloads)
    if ([name for name, _ in once_end.payloads] == ["TWICE.md"]
            and once_texts["TWICE.md"].startswith("same bytes")):
        held("a document is served once", "the second SERVE renders nothing -- same content, "
             "same proof, the text never rides twice")
    else:
        failures.append(f"  ✗ the same document was served twice  {once_end.payloads}")

    # --- constraints: pushed on entry, re-emitted VERBATIM in every block ------------
    lawful = document("---\nname: X\noutput: json\nconstraints.behavior: |\n  RG3  never touch a neighbour\n"
                      "  RG16 a GO names its step\nproc: |\n  INFER\n  PICK member\n---\n")
    bound = conductor()
    bound.forget()
    first = bound.start(lawful)
    if [(c.code, c.text) for c in first.constraints] == [("RG3", "never touch a neighbour"),
                                                         ("RG16", "a GO names its step")]:
        held("constraints ride the block", "in full text — an id alone dies twenty turns later")
    else:
        failures.append(f"  ✗ constraints               {first.constraints}")
    if "CONSTRAINTS" in render(first) and "never touch a neighbour" in render(first):
        held("re-emitted verbatim", "every block carries them, never a reference")
    else:
        failures.append("  ✗ constraints not rendered in the block")
    expect("constraint-malformed", lambda: conductor().start(
        document("---\nname: X\nconstraints.behavior: |\n  lonely\nproc: |\n  PICK x\n---\n")))
    bound.forget()

    # --- CALL opens a new frame: constraints+tools ACCUMULATE, the stack shows both ---
    (home.meta / "skills" / "helper-skill").mkdir(parents=True)
    (home.meta / "skills" / "helper-skill" / "SKILL.md").write_text(
        "---\nname: helper-skill\ndescription: a tool worth knowing about.\n---\nbody\n",
        encoding="utf-8")
    (home.meta / "CALLEE.md").write_text(
        "---\nname: CALLEE\noutput: json\nconstraints.behavior: |\n  RG2  inner law.\ntools: |\n  helper-skill\nproc: |\n"
        "  INFER\n  PICK who\n---\nthe callee's own prose.\n", encoding="utf-8")
    caller_doc = document("---\nname: CALLER\nconstraints.behavior: |\n  RG1  outer law.\nproc: |\n"
                          "  CALL CALLEE.md\n  HOOK back\n---\n")
    caller = conductor()
    caller.forget()
    opened = caller.start(caller_doc)
    entered = caller.submit('["a", "b"]')
    if ([c.code for c in entered.constraints] == ["RG1", "RG2"]
            and [t.name for t in entered.tools] == ["helper-skill"]
            and entered.stack == "DOC ▸ CALLEE{2/2}"
            and str(entered.instruction) == "PICK who"):
        held("CALL accumulates and descends", "RG1+RG2 and tools in force, the path "
             "shown -- the ancestor bare, the active frame carries the pointer")
    else:
        failures.append(f"  ✗ CALL descent              {[c.code for c in entered.constraints]} "
                        f"/ {[t.name for t in entered.tools]} / {entered.stack!r} / {entered.instruction}")

    if ([n for n, _ in opened.payloads] == ["CALLEE"]
            and "the callee's own prose" in opened.payloads[0][1]):
        held("CALL serves the callee's BODY", "prose rides the block, exactly like a SERVE would")
    else:
        failures.append(f"  ✗ CALL body payload         {opened.payloads}")

    if ("[helper-skill]" in render(entered)
            and "a tool worth knowing about" not in render(entered)):
        held("tools ride the block by NAME", "the menu is lean -- descriptions live in the served catalog")
    else:
        failures.append("  ✗ tools render                not the bracketed names")

    reentered = conductor().resume(caller_doc)
    if (reentered.stack == entered.stack and str(reentered.instruction) == str(entered.instruction)
            and reentered.tools == entered.tools and reentered.constraints == entered.constraints):
        held("the stack survives a reload", "a fresh object sees both frames again")
    else:
        failures.append(f"  ✗ CALL stack did not survive a reload  {reentered.stack!r}")

    if over(caller.submit("a")):
        held("the callee resolves the CALL", "control returns, the caller then finishes too")
    else:
        failures.append("  ✗ CALL did not resolve back to the caller")
    caller.forget()

    # --- `tools:` resolves against the document's OWN `.meta` (federal, vendored) -------
    document_with_tool = reading.read(document(
        "---\nname: X\ntools: |\n  helper-skill\nproc: |\n  PICK x\n---\n", at=home.meta))
    resolved = compiling.tools_of(document_with_tool)
    if (len(resolved) == 1 and resolved[0].name == "helper-skill"
            and resolved[0].description == "a tool worth knowing about."
            and resolved[0].contract.endswith("helper-skill/SKILL.md")
            and "contract:" in str(resolved[0])):
        held("tools_of resolves a name", "description AND contract path -- free will can read the dish")
    else:
        failures.append(f"  ✗ tools_of                  {resolved}")

    declared_doc = reading.read(document(
        "---\nname: X\ntools: |\n  nobody-home\nproc: |\n  PICK x\n---\n", at=home.meta))
    declared_tools = compiling.tools_of(declared_doc)
    if (len(declared_tools) == 1 and declared_tools[0].name == "nobody-home"
            and declared_tools[0].description == "" and declared_tools[0].contract == ""):
        held("an unresolved tools: name is DECLARED", "a harness skill, offered name-only -- the harness describes it")
    else:
        failures.append(f"  ✗ declared harness tool      {declared_tools}")

    # --- a PACKAGE contributes procedures: LOADED off vendor, never imported by name ---
    (home.meta / instance.MANIFEST).write_text("installed: '2026-07-30'\npackages:\n  fedmini: '1'\n",
                                             encoding="utf-8")
    mini = home.meta / ".sys" / "vendor" / "fedmini@1" / "skills" / "mini"
    mini.mkdir(parents=True)

    # a pin without its bundle refuses: a missing package would amputate the layer silently
    (home.meta / instance.MANIFEST).write_text(
        "installed: '2026-07-30'\npackages:\n  fedmini: '1'\n  ghost: '9'\n", encoding="utf-8")
    expect("package-missing", lambda: instance.vendored(home.meta))
    (home.meta / instance.MANIFEST).write_text("installed: '2026-07-30'\npackages:\n  fedmini: '1'\n",
                                             encoding="utf-8")

    # --- HOOK: a named socket -- whatever attaches is CALLed there, marked injected ----
    (home.meta / "procs").mkdir(exist_ok=True)
    (home.meta / "procs" / "EXTRA.md").write_text(
        "---\nname: EXTRA\nkind: proc\nattach: bench.ready\nproc: |\n  HOOK depth\n---\n"
        "the extra's prose\n", encoding="utf-8")
    hooked = conductor()
    hooked.forget()
    hooked_end = hooked.start(document("---\nname: H\nproc: |\n  HOOK bench.ready\n---\n"))
    _, hooked_stack, _, _, _, _, _, _ = persistence.restore(session_of(home.meta), revive)
    floor_steps = hooked_stack.frames[0].procedure.instructions
    if (over(hooked_end) and [str(s) for s in floor_steps] == ["HOOK bench.ready", "CALL EXTRA.md"]
            and floor_steps[1].injected
            and "the extra's prose" in dict(hooked_end.payloads).get("EXTRA", "")):
        held("HOOK expands into CALLs", "the attached proc plays there, marked injected")
    else:
        failures.append(f"  ✗ HOOK expansion            {[str(s) for s in floor_steps]}")
    hooked.forget()

    idle = conductor()
    idle.forget()
    if over(idle.start(document("---\nname: H\nproc: |\n  HOOK nobody.there\n---\n"))):
        held("an empty HOOK is a no-op", "nothing attached, nothing played, no ceremony")
    else:
        failures.append("  ✗ an empty HOOK was not transparent")
    idle.forget()

    # an INJECTED instruction survives the reload: staleness checks the DECLARED part only
    survivor_doc = document(
        "---\nname: H\nproc: |\n  INFER\n  HOOK bench.ready\n  INFER\n---\n")
    survivor = conductor()
    survivor.forget()
    survivor.start(survivor_doc)
    survivor.submit("")
    reloaded = conductor().resume(survivor_doc)
    if reloaded.instruction.keyword == "INFER" and over(conductor().submit("")):
        held("an injected CALL survives the reload", "the run resumes past it, and completes")
    else:
        failures.append(f"  ✗ injected survival         {reloaded.instruction}")
    conductor().forget()

    # an attach pointing at no declared HOOK WARNS here -- these are the author's own
    # documents, and a law the author wrote never blocks the build (the refusal between
    # packages lives at engine/packaging/author-lint)
    if any(one.startswith("attach-unhooked") for one in compiling.lint(home.meta)):
        held("an attach without HOOK warns", "the author's attach is named, the build passes")
    else:
        failures.append("  ✗ an orphaned attach went unsaid")
    (home.meta / "HOLDER.md").write_text(
        "---\nname: HOLDER\nkind: proc\nproc: |\n  HOOK bench.ready\n---\n", encoding="utf-8")
    if "attach" not in compiling.render_registry(home.meta):
        held("an attach finds its HOOK", "the registry passes once a proc declares the socket")
    else:
        failures.append("  ✗ the registry still complains about a satisfied attach")

    # --- one constraint, ONE holder: the registry is what makes a duplicate visible ---
    (home.meta / "ONE.md").write_text("---\nname: O\nconstraints.behavior: |\n  RGX  a thing\n---\n",
                                      encoding="utf-8")
    registry = compiling.render_registry(home.meta)
    (home.meta / "TWO.md").write_text("---\nname: T\nconstraints.behavior: |\n  RGX  a thing\n---\n",
                                      encoding="utf-8")
    if "`RGX`" in registry and "ONE.md" in registry:
        held("the registry names holders", "code, holder, statement — for dedup, never served")
    else:
        failures.append("  ✗ registry                  {registry[:80]!r}")
    if any(one.startswith("constraint-doubled") for one in compiling.lint(home.meta)):
        held("a double the author holds warns", "RGX is named, the first declaration is kept")
    else:
        failures.append("  ✗ a doubled code went unsaid")
    (home.meta / "TWO.md").unlink()

    # --- skills AND procs compile into ONE catalog (TOOLS), and the drop is never silent
    (home.meta / "skills" / "a-skill").mkdir(parents=True)
    (home.meta / "skills" / "a-skill" / "SKILL.md").write_text(
        "---\nname: a-skill\ndescription: y\n---\nbody\n", encoding="utf-8")
    (home.meta / "skills" / "a-stub").mkdir(parents=True)
    (home.meta / "skills" / "a-stub" / "SKILL.md").write_text("go read elsewhere\n", encoding="utf-8")
    (home.meta / "A_PROC.md").write_text(
        "---\nname: A_PROC\nkind: proc\ndescription: z\nproc: |\n  PICK x\n---\nbody\n",
        encoding="utf-8")
    compiled = compiling.render_tools(home.meta)
    if ("`a-skill`** — y" in compiled and "`a-stub`" in compiled and "`A_PROC`** — z" in compiled
            and "contract: " in compiled and "Legacy" not in compiled
            and "Harness skills (declared)" in compiled and "`nobody-home`" in compiled
            and compiled == compiling.render_tools(home.meta)):
        held("ONE catalog, one kind", "own skills mainstream, Legacy dead, the declared harness names derived and listed")
    else:
        failures.append(f"  ✗ compiled tools             {compiled[:200]!r}")

    # --- resuming must KEEP the checkout: looking the name up would lose a worktree ---
    wt = bench.env("core-a_plan", bare=True)       # an instance at a worktree's path
    worktree = wt.root
    (wt.made / "WFORMS.md").write_text(
        "---\nname: WFORMS\ndescription: bench formats\nformats: |\n"
        "  json  inline  one valid JSON value\n---\n", encoding="utf-8")
    from conductor import Member                                          # noqa: PLC0415
    elsewhere_checkout = Conductor(Member(path=worktree, name="core"), siblings, script)
    elsewhere_checkout.forget()
    elsewhere_checkout.start(document(PLAYABLE, at=wt.made))
    resumed = Conductor(Member(path=worktree, name="core"), siblings, script)
    resumed.resume(wt.made / "DOC.md")
    if resumed.member.path == worktree:
        held("a resume keeps its checkout", "a worktree stays a worktree, not the main one")
    else:
        failures.append(f"  ✗ resume lost the checkout  {resumed.member.path}")

    # --- the engine runs installed: outside an instance it conducts nothing, and says --
    expect("engine-uninstalled", lambda: Conductor.here(bench.temp() / "pp.py"))
    town_of_one = bench.temp()
    (town_of_one / "loose" / ".git").mkdir(parents=True)   # a git checkout is no member
    if discovery.members(discovery.Siblings(root=town_of_one)) == []:
        held("a checkout is no member", "an instance makes a member, a .git does not")
    else:
        failures.append("  ✗ a bare git checkout was listed as a member")

    # --- a document that changed under a saved run is refused, not guessed ------------
    conductor().forget()
    conductor().start(playable)
    document(PLAYABLE.replace("  PICK member\n", ""), at=playable.parent)
    expect("session-stale", lambda: conductor().resume(playable))
    playable.write_text(PLAYABLE, encoding="utf-8")

    persistence.forget(session_of(home.meta))
    expect("no-run", lambda: conductor().submit("core"))

    # --- metrics: what is served is weighed, part by part, and the parts add up -------
    weighed = metrics.weigh(riding, render(riding))
    parts = sum(weighed[part] for part in metrics.PARTS)
    if (parts == weighed["total"] and weighed["payload"] > 0
            and metrics.weigh(first, render(first))["constraints"] > 0):
        held("a block is weighed", "the parts add up to the whole -- no unmeasured remainder")
    else:
        failures.append(f"  ✗ metrics                   {weighed}")

    piled = metrics.add(metrics.add({}, riding, render(riding)), riding, render(riding))
    if piled["blocks"] == 2 and piled["total"] == 2 * weighed["total"]:
        held("the session accumulates", "a run is a session: the floor never pops")
    else:
        failures.append(f"  ✗ accumulation              {piled}")

    # --- the CLI is exercised too: it bit once because nothing covered it -------------
    import pp as pp_cli                                                        # noqa: PLC0415
    (home.meta / pp_cli.BOOT).write_text(PLAYABLE, encoding="utf-8")
    persistence.forget(session_of(home.meta))
    spoken = io.StringIO()
    with contextlib.redirect_stdout(spoken):
        cli = conductor()
        shown = pp_cli.report(cli, cli.resume(cli.boot(pp_cli.BOOT)))
        mid = conductor()
        fed = pp_cli.report(mid, mid.submit('["core", "perso"]'))
        after = conductor()
        done = pp_cli.report(after, after.submit("perso"))
    said = spoken.getvalue()
    if shown == fed == done == 0 and "PICK member" in said and "▌ END" in said:
        held("the CLI", "renders a block, then the END block closes the run")
    else:
        failures.append(f"  ✗ CLI                       rc={shown}/{done} — {said!r}")

    # --- a vendored witness package: the environment the packaging cases below exercise
    pmode_made = bench.env("pmode", pin=False).made
    pmode_member = discovery.instance_member(pmode_made / ".sys" / "engine" / "pp.py")
    wit_root = pmode_made / ".sys" / "vendor" / "witness@0.0.1"
    (wit_root / "procs").mkdir(parents=True)
    (wit_root / "package.yaml").write_text(
        "name: witness\nversion: 0.0.1\ndescription: the topology witness\nrequires: [kit]\n",
        encoding="utf-8")
    (wit_root / "procs" / "WNOTE.md").write_text(
        "---\nname: WNOTE\nkind: proc\ndescription: the witness note\nproc: |\n  INFER\n---\n\nthe note\n",
        encoding="utf-8")
    (wit_root / "skills" / "pp-wit").mkdir(parents=True)
    (wit_root / "skills" / "pp-wit" / "SKILL.md").write_text(
        "---\nname: pp-wit\ndescription: the witness skill\n---\n\npp-wit\n", encoding="utf-8")
    (wit_root / "skills" / "pp-wit" / "pp-wit.py").write_text("print('wit')\n", encoding="utf-8")
    pmode_pins = instance.read(pmode_made)
    pmode_pins["packages"]["witness"] = "0.0.1"
    instance.write(pmode_made, pmode_pins)

    # --- the packages' overlay order is the REQUIRES topology: the client wins ---------
    pmode_kit = next(one for one in instance.vendored(pmode_member.meta)
                     if one.name.startswith("kit@"))
    (pmode_kit / "overlays").mkdir(exist_ok=True)
    (pmode_kit / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  TK8  the dependency's overlay law.\n---\n",
        encoding="utf-8")
    (wit_root / "overlays").mkdir()
    (wit_root / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK8\n---\n", encoding="utf-8")
    topo_order = [one.name.split("@")[0] for one in instance.vendored(pmode_member.meta)]
    topo_laws = [one.code for one in
                 compiling.effective(pmode_member.meta,
                                     reading.read(instance.resolve(pmode_member.meta,
                                                                   "TURN.md")))[0]]
    topo_pins = instance.read(pmode_member.meta)
    topo_pins["packages"] = dict(reversed(list(topo_pins["packages"].items())))
    instance.write(pmode_member.meta, topo_pins)
    topo_again = [one.name.split("@")[0] for one in instance.vendored(pmode_member.meta)]
    if (topo_order == ["kit", "witness"] and topo_again == ["kit", "witness"]
            and "TK8" not in topo_laws and "T1" in topo_laws):
        held("the overlay order is the requires topology", "the client's overlay amends "
             "its dependency's and wins (-TK8 lands), pins order proven irrelevant")
    else:
        failures.append(f"  \u2717 overlay topology            {topo_order} {topo_again} "
                        f"{topo_laws}")

    # --- the catalog addresses contracts unpinned: names resolve, vendor paths die -----
    pmode_catalog = compiling.render_tools(pmode_member.meta)
    if ("@0." not in pmode_catalog
            and "contract: pp-wit\n" in pmode_catalog
            and "contract: WNOTE.md\n" in pmode_catalog
            and "is a PIN" in pmode_catalog):
        held("the catalog addresses unpinned", "a skill by its bare name, a document by "
             "name.md -- the header says a vendored path is a pin, never written")
    else:
        failures.append(f"  \u2717 catalog unpinned            {pmode_catalog[:200]!r}")

    return 0
