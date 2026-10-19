"""Scenario `conduction-core` -- the conductor's core loop:
- every refusal reddens on the code it names; a run with no yield ends on a block
- the block: one instruction, options fed by the pipeline, one instruction line
- a run served but unanswered comes back the same; a wrong or an empty answer is a repair
- the pointer survives on disk; the state IS the instruction stack (taken, given)
- the closing is binary: a PICK closes on CONTINUE
- constraints: pushed on entry, re-emitted verbatim; a malformed one refuses
- CALL opens a frame: constraints and tools accumulate, the callee's body rides, the
  stack survives a reload, the callee resolves back to the caller
- `tools:` resolves against the document's own instance; an unresolved name is declared
- a pin without its bundle refuses
- HOOK: a named socket -- what attaches is CALLed there, marked injected, and survives a
  reload; an empty HOOK is a no-op; an attach finds its HOOK
- the registry names a constraint's holder
- skills and procs compile into ONE catalog, idempotent
- a resume keeps its checkout; a run saved under another name keeps the launched member
- the engine runs installed; a document changed under a saved run refuses; no run refuses
- metrics: a block is weighed part by part, a session accumulates
- the CLI renders a block, then the END block
- a tag resolves to another document's own front matter, an unresolved one refuses
- SETTINGS.md: seeded by the install, its repair allowance and its budget read, a lie refused
- the guard: `^ @Doc.field` paces a CALL on a declared cadence, absent means off
- the context: the pending document's body is CONTEXT, a root INFER contexts its own,
  a reading and its ask share one output, the signal mark is one and last, the member's
  laws ride the block as written, the card reaches the first block
- the channels: the form and channel are rendered and a pasted draft bounces soft;
  consumed channels say their mode
- the packages' overlay order is the requires topology; the catalog addresses unpinned
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from conductor import (Conductor, Member, Stack, render, revive, compiling, discovery, instance,
                       metrics, navigation, persistence, reading)
from tests.harness import PLAYABLE, REFUSED, body_of, document, reaches, session_of, support

run = support(__file__, "run")

FORMATS = ("---\nname: {name}\ndescription: bench formats\nformats: |\n"
           "  json  inline  one valid JSON value\n---\n")
SKILL_DESCRIPTION = "y"                # what the catalog's skill entry carries
PROC_DESCRIPTION = "z"                 # what the catalog's proc entry carries
NAME = "Sextant"                       # the member's name a tag resolves
CHARACTER = "curt, dry wit"            # the member's character a tag resolves
LAW_NAME = "your name is"              # the member's laws, the tag their tail
LAW_CHARACTER = "you must behave like this:"


def entry(catalog: str, name: str) -> tuple[str, str]:
    """-> (the entry line, the line under it) the catalog lists for `name`, ("", "") when absent."""
    lines = catalog.splitlines()
    at = next((i for i, line in enumerate(lines) if line.startswith(f"- **`{name}`**")), None)
    if at is None:
        return "", ""
    return lines[at], lines[at + 1] if at + 1 < len(lines) else ""


def scenario(bench) -> int:
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    # --- the home: one bare instance, `core`
    core = bench.env("core", bare=True)
    siblings = core.siblings()
    home = core.member
    script = core.engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")

    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, script, "t")

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

    (home.meta / "HFORMS.md").write_text(FORMATS.format(name="HFORMS"), encoding="utf-8")
    playable = document(PLAYABLE)
    names = ["alpha", "beta", "gamma"]
    listed = json.dumps(names)

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
    block = conductor().submit(listed)
    if list(block.options) == names and block.output == "options":
        held("options and output", "fed by the pipeline, and the form is a NAME of the enumeration")
    else:
        failures.append(f"  ✗ options / output          {block.options} / {block.output}")

    rendered = render(block)
    missing = [f for f in ("OPTIONS", "INSTRUCTION", "CONTINUE") if f not in rendered]
    pick_lines = [l for l in rendered.splitlines() if l.strip().startswith("PICK")]
    if not missing and len(pick_lines) == 1 and "options => tool" in pick_lines[0]:
        held("the block's shape", "three sections, ONE instruction line -- the form and "
             "channel ride it as its suffix")
    else:
        failures.append(f"  ✗ block shape               {missing} {pick_lines!r}")

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
    conductor().submit(listed)
    empty = conductor().submit("")
    if wrong.deviation and empty.deviation and wrong.repair == 1 and empty.repair == 2:
        held("a wrong and an empty answer", "each named, each counted — REPAIR 1 then 2")
    else:
        failures.append(f"  ✗ wrong/empty               {wrong.deviation!r} / {empty.deviation!r}")

    conductor().submit(listed)
    conductor().submit("nobody")
    conductor().submit(listed)
    expect("repair-exhausted", lambda: conductor().submit("nobody"))

    if "REPAIR" in render(wrong) and "DEVIATION" in render(wrong):
        held("a repair block says so", "REPAIR in the heading, DEVIATION in the body")
    else:
        failures.append("  ✗ a repair block looks like a normal one")

    # --- the pointer SURVIVES: a brand new object picks the run up --------------------
    conductor().forget()
    conductor().resume(playable)
    conductor().submit(listed)
    if over(conductor().submit("gamma")):
        held("the run completes", "the last answer landed; the COMPLETION block closes it")
    else:
        failures.append("  ✗ completion                no completion block after the last step")

    member, stack, _, _, _, _, _ = persistence.restore(session_of(home.meta), revive)
    steps = stack.frames[-1].procedure.instructions
    if member == "core" and all(one.done for one in steps):
        held("the pointer survived", "reloaded from disk by another object -- still home")
    else:
        failures.append(f"  ✗ pointer survival          {member} / {[s.done for s in steps]}")

    # --- the state IS the instruction stack: each one carries what it took and gave ----
    if (steps[0].taken is None and steps[0].given == names
            and steps[1].taken == steps[0].given and steps[1].given == "gamma"):
        held("the pipeline", "each instruction takes what the one before it gave")
    else:
        failures.append(f"  ✗ pipeline                  {[(s.taken, s.given) for s in steps]}")

    # --- the closing is BINARY -- CONTINUE now, FINAL later, nothing else --------------
    conductor().forget()                  # the completed run dropped: the document opens anew
    pick_render = render(conductor().resume(playable))
    if "▶ CONTINUE" in pick_render:
        held("the closing is binary", "a PICK closes on CONTINUE -- the closing says what comes, "
             "and every block carries its own INSTRUCTION")
    else:
        failures.append(f"  ✗ binary closing              {pick_render[-120:]!r}")
    conductor().forget()

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

    # --- `tools:` resolves against the document's OWN instance --------------------------
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
    _, hooked_stack, _, _, _, _, _ = persistence.restore(session_of(home.meta), revive)
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

    (home.meta / "HOLDER.md").write_text(
        "---\nname: HOLDER\nkind: proc\nproc: |\n  HOOK bench.ready\n---\n", encoding="utf-8")
    if "attach" not in compiling.render_registry(home.meta):
        held("an attach finds its HOOK", "the registry passes once a proc declares the socket")
    else:
        failures.append("  ✗ the registry still complains about a satisfied attach")

    # --- one constraint, ONE holder: the registry is what makes a holder visible -------
    (home.meta / "ONE.md").write_text("---\nname: O\nconstraints.behavior: |\n  RGX  a thing\n---\n",
                                      encoding="utf-8")
    registry = compiling.render_registry(home.meta)
    if "`RGX`" in registry and "ONE.md" in registry:
        held("the registry names holders", "code, holder, statement — for dedup, never served")
    else:
        failures.append(f"  ✗ registry                  {registry[:80]!r}")

    # --- skills AND procs compile into ONE catalog (TOOLS), and the drop is never silent
    (home.meta / "skills" / "a-skill").mkdir(parents=True)
    (home.meta / "skills" / "a-skill" / "SKILL.md").write_text(
        f"---\nname: a-skill\ndescription: {SKILL_DESCRIPTION}\n---\nbody\n", encoding="utf-8")
    (home.meta / "skills" / "a-stub").mkdir(parents=True)
    (home.meta / "skills" / "a-stub" / "SKILL.md").write_text("go read elsewhere\n", encoding="utf-8")
    (home.meta / "A_PROC.md").write_text(
        f"---\nname: A_PROC\nkind: proc\ndescription: {PROC_DESCRIPTION}\nproc: |\n  PICK x\n---\nbody\n",
        encoding="utf-8")
    compiled = compiling.render_tools(home.meta)
    skill_line, skill_contract = entry(compiled, "a-skill")
    proc_line, proc_contract = entry(compiled, "A_PROC")
    if (skill_line.endswith(f" {SKILL_DESCRIPTION}") and skill_contract.strip() == "contract: a-skill"
            and proc_line.endswith(f" {PROC_DESCRIPTION}") and proc_contract.strip() == "contract: A_PROC.md"
            and "`a-stub`" in compiled
            and "- `nobody-home`" in compiled.splitlines()
            and compiled == compiling.render_tools(home.meta)):
        held("ONE catalog, one kind", "own skills and procs one entry each, described, their contract "
             "under; the stub named; the declared harness name listed; same bytes twice")
    else:
        failures.append(f"  ✗ compiled tools             {compiled[:200]!r}")

    # --- resuming must KEEP the checkout: looking the name up would lose a worktree ---
    wt = bench.env("core-a_plan", bare=True)       # an instance at a worktree's path
    worktree = wt.root
    (wt.made / "WFORMS.md").write_text(FORMATS.format(name="WFORMS"), encoding="utf-8")
    elsewhere_checkout = Conductor(Member(path=worktree, name="core"), script)
    elsewhere_checkout.forget()
    elsewhere_checkout.start(document(PLAYABLE, at=wt.made))
    resumed = Conductor(Member(path=worktree, name="core"), script)
    resumed.resume(wt.made / "DOC.md")
    if resumed.member.path == worktree:
        held("a resume keeps its checkout", "a worktree stays a worktree, not the main one")
    else:
        failures.append(f"  ✗ resume lost the checkout  {resumed.member.path}")

    # --- a run saved under another NAME keeps the launched member, and says so -----------
    # (the facade knows no siblings to look a name up in)
    moved = Conductor(Member(path=worktree, name="core-b"), script)
    moved_block = moved.resume(wt.made / "DOC.md")
    moved_slot = session_of(wt.made)
    moved_lines = [json.loads(line) for line in
                   (moved_slot.parent / persistence.trace_of(moved_slot))
                   .read_text(encoding="utf-8").splitlines() if line.strip()]
    said = [one for one in moved_lines if one.get("kind") == "member-moved"]
    if (moved_block is not None and moved.member.name == "core-b"
            and moved.member.path == worktree
            and said and said[-1].get("was") == "core" and said[-1].get("now") == "core-b"):
        held("a run saved under another name keeps the launched member",
             "no lookup beside: the member is the one the engine was launched on, and the "
             "trace says `member-moved` with both names")
    else:
        failures.append(f"  ✗ member moved              {moved.member.name} {said!r}")

    # --- the engine runs installed: outside an instance it conducts nothing, and says --
    expect("engine-uninstalled", lambda: Conductor.here(bench.temp() / "pp.py"))

    # --- a document that changed under a saved run is refused, not guessed ------------
    conductor().forget()
    conductor().start(playable)
    document(PLAYABLE.replace("  PICK member\n", ""), at=playable.parent)
    expect("session-stale", lambda: conductor().resume(playable))
    playable.write_text(PLAYABLE, encoding="utf-8")

    persistence.forget(session_of(home.meta))
    expect("no-run", lambda: conductor().submit("core"))

    # --- metrics: what is served is weighed, part by part, and the parts add up -------
    reader = conductor()
    reader.forget()
    riding = reader.start(document("---\nname: X\nproc: |\n  HOOK warp\n"
                                   "  SERVE TAGGED.md\n  INFER\n---\n"))
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

    # --- the CLI renders a block, then the END block -----------------------------------
    import pp as pp_cli                                                        # noqa: PLC0415
    (home.meta / pp_cli.BOOT).write_text(PLAYABLE, encoding="utf-8")
    persistence.forget(session_of(home.meta))
    spoken = io.StringIO()
    with contextlib.redirect_stdout(spoken):
        cli = conductor()
        shown = pp_cli.report(cli, cli.resume(cli.boot(pp_cli.BOOT)))
        mid = conductor()
        fed = pp_cli.report(mid, mid.submit('["alpha", "beta"]'))
        after = conductor()
        done = pp_cli.report(after, after.submit("beta"))
    spoken_text = spoken.getvalue()
    if shown == fed == done == 0 and "PICK member" in spoken_text and "▌ END" in spoken_text:
        held("the CLI", "renders a block, then the END block closes the run")
    else:
        failures.append(f"  ✗ CLI                       rc={shown}/{done} — {spoken_text!r}")

    # --- SETTINGS.md: the tuning is the instance's own document ---------------------------
    # one bare instance carries the settings cases: each writes the SETTINGS.md it reads
    tuned_env = bench.env("solo", bare=True)
    tuned, tuned_engine = tuned_env.member, tuned_env.engine

    def tuned_conductor() -> Conductor:
        return run.conductor_of(tuned_env, "t")

    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 500\nwork_repairs_allowed: 1\n"
        "verbatim_constraints: false\n---\n", encoding="utf-8")
    (tuned.meta / "TFORMS.md").write_text(FORMATS.format(name="TFORMS"), encoding="utf-8")
    tuned_conductor().start(document(PLAYABLE, at=tuned.meta))
    tuned_conductor().submit("nobody")                       # repair 1 -- the whole allowance
    expect("repair-exhausted", lambda: tuned_conductor().submit("nobody"))

    # the serve reads WHOLE -- what an output cannot hold is the block's cut (rendering/cut);
    # here only that a big reading rides in one titled section
    (tuned.meta / "BIG.md").write_text("x" * 1200 + "\n", encoding="utf-8")
    (tuned.meta / "BIGRUN.md").write_text(
        "---\nname: BIGRUN\nproc: |\n  SERVE BIG.md\n  INFER\n---\n", encoding="utf-8")
    whole = tuned_conductor().start(tuned.meta / "BIGRUN.md")
    if whole.command == "INFER" and len(dict(whole.payloads)["BIG.md"]) == 1200:
        held("a reading rides whole", "1200 chars in one section, the instruction on the same "
             "output -- the serve counts nothing")
    else:
        failures.append(f"  ✗ whole reading              {whole.command!r} "
                        f"{sum(len(t) for _, t in whole.payloads)}")
    tuned_conductor().forget()

    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nmax_harness_tool_output: banana\n---\n", encoding="utf-8")
    expect("settings-invalid", lambda: Conductor(tuned, tuned_engine))
    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nverbatim_constraints: maybe\n---\n", encoding="utf-8")
    expect("settings-invalid", lambda: Conductor(tuned, tuned_engine))

    # --- the guard: `^ @Doc.field` paces an instruction on a declared cadence -----------
    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nops_every: 1\n---\n", encoding="utf-8")
    (tuned.meta / "OPS.md").write_text(
        "---\nname: OPS\nproc: |\n  INFER\n---\nconsign the last exchange\n",
        encoding="utf-8")
    loop_doc = tuned.meta / "LOOP.md"
    loop_doc.write_text(
        "---\nname: LOOP\ncycle: true\nproc: |\n  CALL OPS.md ^ @SETTINGS.ops_every\n"
        "  INFER\n  FINAL\n---\nthe restitution\n", encoding="utf-8")

    guard_first = tuned_conductor().start(loop_doc)
    guard_second = tuned_conductor().resume(loop_doc)
    guard_closed = tuned_conductor().submit("")
    if (guard_first.document == "LOOP" and guard_first.wait
            and guard_second.document == "OPS" and not guard_second.wait
            and guard_closed.document == "LOOP" and guard_closed.wait):
        held("a guarded CALL paces on the setting",
             "never the first turn; from the second, the consignation opens the exchange")
    else:
        failures.append(f"  ✗ guard pacing               {guard_first.document}/"
                        f"{guard_second.document}/{guard_closed.document}")

    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nops_every: 3\n---\n", encoding="utf-8")
    tuned_conductor().forget()
    walk = [tuned_conductor().start(loop_doc).document]
    for _ in range(2, 8):
        step = tuned_conductor().resume(loop_doc)
        walk.append(step.document)
        if step.document == "OPS":
            tuned_conductor().submit("")
    if walk == ["LOOP", "LOOP", "LOOP", "OPS", "LOOP", "LOOP", "OPS"]:
        held("the cadence holds", "ops_every: 3 -- the record opens exchanges 4 and 7, none other")
    else:
        failures.append(f"  ✗ cadence                    {walk}")

    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nops_every: banana\n---\n", encoding="utf-8")
    tuned_conductor().forget()
    expect("guard-invalid", lambda: tuned_conductor().start(loop_doc))   # parsed before the
    # cadence check: a lie refuses at once, it does not wait for its turn

    (tuned.meta / "SETTINGS.md").unlink()
    tuned_conductor().forget()
    absent_first = tuned_conductor().start(loop_doc)
    absent_second = tuned_conductor().resume(loop_doc)
    if absent_first.document == "LOOP" and absent_second.document == "LOOP":
        held("an absent setting means off", "no SETTINGS.md, no field -- the guard skips, nothing refuses")
    else:
        failures.append(f"  ✗ guard absent               {absent_first.document}/{absent_second.document}")

    # --- the context has a name: the proc-carrier's body is not a mere reading ----------
    ctx = bench.env("ctx")
    ctx_made = ctx.made
    if (ctx_made / "SETTINGS.md").is_file():
        held("install seeds SETTINGS.md", "the template carries it -- the operator's file from day one")
    else:
        failures.append("  ✗ SETTINGS.md not seeded")

    ctx.write("NOTE.md", "---\nname: NOTE\nkind: doc\ndescription: a reading of the member\n---\n\n"
                         "the note the member reads every session\n")
    ctx.write("procs/CAPS.md", "---\nname: CAPS\nkind: proc\ndescription: the member's brief\n"
                               "proc: |\n  INFER\n---\n\nthe witness's capabilities, asked once\n")
    ctx.write_member("serve: |\n  reference: NOTE.md\nconstraints.behavior: |\n"
                     "  A1  the agent's own law rides the block\n",
                     body="the witness agent", proc="SERVE\n  CALL CAPS.md", name="AGENT")
    ctx_c = run.conductor_of(ctx, None)
    ctx_rendered = render(ctx_c.resume(ctx_c.boot("BOOT.md")))
    if ("NEXT INSTRUCTION CONTEXT — CAPS" in ctx_rendered
            and "INFORMATION — CAPS" not in ctx_rendered
            and "INFORMATION — standing orders" in ctx_rendered
            and "INFORMATION — NOTE.md" in ctx_rendered
            and "INFORMATION — AGENT" in ctx_rendered
            and ctx_rendered.index("INFORMATION — AGENT") < ctx_rendered.index("INFORMATION — NOTE.md")):
        held("the pending document's body is CONTEXT",
             "CAPS alone promotes; the standing orders, the member's body and its reading "
             "stay INFORMATION, the body before the row it serves")
    else:
        failures.append(f"  ✗ context label              {ctx_rendered[:400]!r}")

    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nmax_harness_tool_output: 300\n---\n", encoding="utf-8")
    tuned_conductor().forget()
    own_context = render(tuned_conductor().start(loop_doc))
    if "NEXT INSTRUCTION CONTEXT — LOOP" in own_context:
        held("a root INFER contexts its own body", "the smallest case: the document asks, its body frames")
    else:
        failures.append(f"  ✗ own context                {own_context[:200]!r}")

    (tuned.meta / "BIGREAD.md").write_text("y" * 1200 + "\n", encoding="utf-8")
    (tuned.meta / "READER.md").write_text(
        "---\nname: READER\nproc: |\n  SERVE BIGREAD.md\n  INFER\n---\nread it all\n",
        encoding="utf-8")
    tuned_conductor().forget()
    chunked = tuned_conductor().start(tuned.meta / "READER.md")
    if chunked.command == "INFER" and "NEXT INSTRUCTION CONTEXT" in render(chunked):
        held("a reading and its ask share one output", "the document rides its section, the "
             "pending step its context and its INSTRUCTION -- one screen, no order block")
    else:
        failures.append(f"  ✗ reading and ask            {chunked.command!r}")

    signal_rendered = render(chunked)
    signal_lines = signal_rendered.rstrip().splitlines()
    if (signal_rendered.count("▶") == 1
            and signal_lines[-2].startswith("▶ ")
            and signal_lines[-1].startswith("./pp")):
        held("the signal mark is one and last",
             "▶ appears once per block, right above the exact command owed")
    else:
        failures.append(f"  ✗ signal mark                 count={signal_rendered.count('▶')} "
                        f"{signal_lines[-2:]!r}")

    # --- the member's laws ride the block as written --------------------------------------
    member_laws = {line.split()[0]: line.strip() for line in
                   str(reading.read(ctx_made / "procs" / "MEMBER.md").front.get("constraints.behavior", ""))
                   .splitlines() if line.strip()}
    if member_laws.get("A1") and member_laws["A1"] in ctx_rendered:
        held("the member's laws ride the block as written", "A1 read from procs/MEMBER.md, "
             "verbatim in the first block -- the constraint the agent reads is the document's")
    else:
        failures.append(f"  ✗ member laws in block        {member_laws}")

    pp_card = ctx_made / ".sys" / "engine" / "refs" / "PP.md"
    if reaches(ctx_rendered, body_of(pp_card)):
        held("one rule, one source", "the card carries the protocol -- and the boot SERVES it: the first block reads it back")
    else:
        failures.append("  ✗ conducted-answer rule       the card does not reach the block")
    run.conductor_of(ctx, None).forget()       # every run of the instance, dropped

    # --- a tag resolves to another document's own front matter -----------------------------
    # the same instance, its member rewritten: each case reads the member it writes
    def persona_boot():
        c = ctx.conductor("t")
        return c.resume(c.boot("BOOT.md"))

    ctx.write_member(f"character: >-\n  {CHARACTER}\nconstraints.behavior: |\n"
                     f"  M1  {LAW_NAME} @MEMBER.name\n  M2  {LAW_CHARACTER} @MEMBER.character\n",
                     body="A terse crew member.", name=NAME)
    persona_opening = persona_boot()
    texts = {c.code: c.text for c in persona_opening.constraints} if persona_opening else {}
    if (texts.get("M1") == f"{LAW_NAME} {NAME}"
            and texts.get("M2") == f"{LAW_CHARACTER} {CHARACTER}"):
        held("a tag resolves to another document's own front matter",
             "@MEMBER.name / @MEMBER.character, both live at the first cession, both resolved")
    else:
        failures.append(f"  ✗ persona tags               {texts}")

    persistence.forget(session_of(ctx_made))
    ctx.write_member("constraints.behavior: |\n  M1  @NOPE.name knows nothing\n",
                     body="A terse crew member.", name="Compass")
    expect("tag-unresolved", persona_boot)

    persistence.forget(session_of(ctx_made))
    ctx.write_member("constraints.behavior: |\n  M1  your character is @MEMBER.character\n",
                     body="A terse crew member.", name="Compass")
    expect("tag-unresolved", persona_boot)
    run.conductor_of(ctx, None).forget()

    # --- the OUTPUT names form AND channel; excess is caught ------------------------------
    ctx.write_member("output: table\n")       # the boot opens on a response step: `table => response`

    def chan_c():
        return run.conductor_of(ctx, None)

    chan_open = chan_c().start(chan_c().boot("BOOT.md"))
    caught = chan_c().submit("| a table | pasted into the tool |")
    after_catch = chan_c().submit("")
    if ("table => response" in render(chan_open)
            and caught.deviation and caught.repair == 0
            and caught.instruction.repairs == 0
            and after_catch.document == "TURN"
            and "any => response" in render(after_catch)):
        held("the channel is rendered and guarded", "the line says `form => response`; "
             "a pasted draft bounces soft -- 0 repair -- and the bare call advances")
    else:
        failures.append(f"  ✗ channels                  {caught.deviation!r} r={caught.repair}")

    (ctx_made / "procs" / "PIPE.md").write_text(
        "---\nname: JOIN\ndescription: takes json\ninput: json\nproc: |\n  HOOK joined\n"
        "---\nx\n", encoding="utf-8")
    (ctx_made / "procs" / "FEEDER.md").write_text(
        "---\nname: FEEDER\nkind: proc\ndescription: feeds\noutput: json\nproc: |\n"
        "  INFER\n  CALL PIPE.md\n---\nfeed it\n", encoding="utf-8")
    fed_block = chan_c().start(ctx_made / "procs" / "FEEDER.md")
    (ctx_made / "procs" / "ELECT.md").write_text(
        "---\nname: ELECT\nkind: proc\ndescription: elects\noutput: json\nproc: |\n"
        "  INFER\n  PICK one\n---\nlist then pick\n", encoding="utf-8")
    elect_c = chan_c()
    elect_c.forget()
    elect_block = elect_c.start(ctx_made / "procs" / "ELECT.md")
    if ("json => tool (heredoc)" in render(fed_block)
            and "json => tool" in render(elect_block)
            and "<output>" in elect_block.next_call):
        held("consumed channels say their mode", "a CALL-fed json pipes heredoc; a PICK-fed "
             "json rides the tool -- the election consumes")
    else:
        failures.append(f"  ✗ consumed channels         {render(fed_block)[-80:]!r}")
    chan_c().forget()

    # --- a vendored witness package on the same instance: the packaging cases below --------
    wit_root = ctx_made / ".sys" / "vendor" / "witness@0.0.1"
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
    pins = instance.read(ctx_made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(ctx_made, pins)

    # --- the packages' overlay order is the REQUIRES topology: the client wins ---------
    meta = ctx.member.meta
    kit = next(one for one in instance.vendored(meta) if one.name.startswith("kit@"))
    (kit / "overlays").mkdir(exist_ok=True)
    (kit / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  TK8  the dependency's overlay law.\n"
        "  TK9  the dependency's other law.\n---\n", encoding="utf-8")
    (wit_root / "overlays").mkdir()
    (wit_root / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK8\n---\n", encoding="utf-8")
    topo_order = [one.name.split("@")[0] for one in instance.vendored(meta)]
    topo_laws = [one.code for one in
                 compiling.effective(meta, reading.read(instance.resolve(meta, "TURN.md")))[0]]
    topo_pins = instance.read(meta)
    topo_pins["packages"] = dict(reversed(list(topo_pins["packages"].items())))
    instance.write(meta, topo_pins)
    topo_again = [one.name.split("@")[0] for one in instance.vendored(meta)]
    if (topo_order == ["kit", "witness"] and topo_again == ["kit", "witness"]
            and topo_laws == ["TK9"]):
        held("the overlay order is the requires topology", "the client's overlay amends "
             "its dependency's and wins (-TK8 lands, TK9 stands), pins order proven irrelevant")
    else:
        failures.append(f"  ✗ overlay topology            {topo_order} {topo_again} {topo_laws}")

    # --- the catalog addresses contracts unpinned: names resolve, vendor paths die -----
    catalog = compiling.render_tools(meta)
    if ("@0." not in catalog
            and "contract: pp-wit\n" in catalog
            and "contract: WNOTE.md\n" in catalog):
        held("the catalog addresses unpinned", "a skill by its bare name, a document by "
             "name.md -- no vendored path written")
    else:
        failures.append(f"  ✗ catalog unpinned            {catalog[:200]!r}")

    return 0
