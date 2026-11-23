"""Scenario `conduction-core` -- the conductor's core loop:
- a front matter that is not a mapping of valid YAML refuses by its code (the reading refusals
  a document can carry live with the pattern `steps/proc`); a run with no yield ends on a block
- the block: one instruction, options fed by the pipeline, one instruction line
- the pointer survives on disk; the state IS the instruction stack (taken, given)
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
- metrics: a block is weighed part by part, a session accumulates; a block merged into the segment
  of another frame counts no law; a mount is weighed with the block that renders it -- its body in
  `payload`, its law in `constraints`, the parts equal to the total
- the CLI renders a block, then the AWAIT block that parks the run
- SETTINGS.md: seeded by the install, its repair allowance and its budget read, a lie refused
- the context: the pending document's body is CONTEXT, a root INFER contexts its own,
  a reading and its ask share one output, the signal mark is one and last, the member's
  laws ride the block as written, the card reaches the first block
- the channels: the form and channel are rendered and a pasted draft bounces soft;
  consumed channels say their mode
- the packages' overlay order is the requires topology; the catalog addresses unpinned
- the system laws: said whole at the head of their groups of the first CONSTRAINTS of each output,
  two outputs in a row, under `verbatim_constraints` true and false alike, never a code; a fused
  output of two segments says them once; they weigh once per output
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from conductor.core import messages
from conductor import (Conductor, Member, Stack, render, revive, compiling, discovery, instance,
                       metrics, navigation, persistence, reading)
from conductor.core import language
import re

from tests.harness import PLAYABLE, body_of, cli, document, reaches, session_of, stepped, support

run = support(__file__, "run")
KEY = re.compile(r"run ([0-9a-f]{6})")

FORMATS = ("---\nname: {name}\ndescription: bench formats\nformats: |\n"
           "  json  inline  one valid JSON value\n---\n")
SKILL_DESCRIPTION = "y"                # what the catalog's skill entry carries
PROC_DESCRIPTION = "z"                 # what the catalog's proc entry carries
UNREADABLE = ("---\nname: [unclosed\nproc: |\n  INFER\n---\n",    # not valid YAML
              "---\n- a\n- list\n---\n")                           # not a mapping

def parked(block) -> bool:
    """The run parked: its root exhausted, the closing waits for the principal's message."""
    return block is not None and block.wait



def entry(catalog: str, name: str) -> tuple[str, str]:
    """-> (the entry line, the line under it) the catalog lists for `name`, ("", "") when absent."""
    lines = catalog.splitlines()
    at = next((i for i, line in enumerate(lines) if line.startswith(f"- **`{name}`**")), None)
    if at is None:
        return "", ""
    return lines[at], lines[at + 1] if at + 1 < len(lines) else ""


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- the home: one bare instance, `core`
    core = bench.env("core", bare=True)
    siblings = core.siblings()
    home = core.member
    script = core.engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")

    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, script, "t")

    # --- a front matter that cannot be read refuses by its code -------------------------
    for text in UNREADABLE:
        expect("front-matter-invalid", lambda t=text: conductor().start(document(t)))
    expect("document-missing", lambda: conductor().start(Path("/nowhere/DOC.md")))
    expect("unknown-member", lambda: discovery.member(siblings, "nobody"))
    expect("stack-empty", lambda: navigation.current(Stack()))

    # a run that finishes without ever yielding still ENDS ON A BLOCK: the terminal
    # order rides with the floor's constraints -- the agent never decides on a bare drain
    finished = conductor().start(document("---\nname: X\nproc: |\n  HOOK done\n---\n"))
    if parked(finished):
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
    missing = [f for f in (language.OPTIONS, language.INSTRUCTION) if f not in rendered]
    pick_lines = [l for l in rendered.splitlines() if l.strip().startswith("PICK")]
    if (not missing and len(pick_lines) == 1 and f"options => {language.TOOL}  (" in pick_lines[0]
            and not block.label and not block.next_call):
        held("the block's shape", "two sections, ONE instruction line -- the form and "
             "channel ride it as its suffix -- and no closing")
    else:
        failures.append(f"  ✗ block shape               {missing} {pick_lines!r}")

    # --- the pointer SURVIVES: a brand new object picks the run up --------------------
    conductor().forget()
    conductor().resume(playable)
    conductor().submit(listed)
    if parked(conductor().submit("gamma")):
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

    if parked(caller.submit("a")):
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
    if (parked(hooked_end) and [str(s) for s in floor_steps] == ["HOOK bench.ready", "CALL EXTRA.md"]
            and floor_steps[1].injected
            and "the extra's prose" in dict(hooked_end.payloads).get("EXTRA", "")):
        held("HOOK expands into CALLs", "the attached proc plays there, marked injected")
    else:
        failures.append(f"  ✗ HOOK expansion            {[str(s) for s in floor_steps]}")
    hooked.forget()

    idle = conductor()
    idle.forget()
    if parked(idle.start(document("---\nname: H\nproc: |\n  HOOK nobody.there\n---\n"))):
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
    stepped(conductor)
    reloaded = conductor().resume(survivor_doc)
    if reloaded.instruction.keyword == "INFER" and parked(stepped(conductor)):
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

    # --- a document that changes under a saved run: the passage ends on the steps it was
    #     playing, the next message reseats the stack on the new declaration, nothing replayed
    def reseats(slot) -> list[dict]:
        return [json.loads(line) for line in (slot.parent / persistence.trace_of(slot))
                .read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("kind") == "reseated"]

    (home.meta / "RESEATED.md").write_text("---\nname: RESEATED\nproc: |\n  INFER\n  INFER\n---\n",
                                           encoding="utf-8")
    holder = document("---\nname: H\nproc: |\n  INFER\n  CALL RESEATED.md\n---\n")
    conductor().forget()
    conductor().start(holder)                                   # H's INFER pending
    root = stepped(conductor)                               # RESEATED, the root, at 1/2
    holder.write_text("---\nname: H\nconstraints.behavior: |\n  RS1  the new law\nproc: |\n"
                      "  SERVE\n  INFER\n  CALL RESEATED.md\n---\n", encoding="utf-8")
    (home.meta / "RESEATED.md").write_text("---\nname: RESEATED\nproc: |\n  INFER\n  INFER\n"
                                           "  INFER\n---\n", encoding="utf-8")
    ended = stepped(conductor)                              # the old steps: 2/2, pending for the principal
    rested = stepped(conductor)                             # the principal's bare call parks the run
    slot = session_of(home.meta)
    said = reseats(slot)
    taken = conductor().submit("the next message")              # reseated: RESEATED 1/3, H 3/3
    state = json.loads(slot.read_text(encoding="utf-8"))
    holder_done = [one.get("done") for one in state["frames"][0]["instructions"]]
    moved = reseats(slot)
    if (root is not None and root.stack == "DOC ▸ RESEATED{1/2}"
            and ended is not None and ended.stack == "DOC ▸ RESEATED{2/2}"
            and rested is not None and rested.wait
            and said == [] and "RS1" in [one.code for one in ended.constraints]
            and taken is not None and taken.stack == "DOC ▸ RESEATED{1/3}" and not taken.wait
            and holder_done == [True, True, False]
            and sorted(one.get("document") for one in moved) == ["DOC", "RESEATED"]
            and [one.get("after") for one in moved if one.get("document") == "DOC"] == [3]):
        held("a document changed under the run", "the passage ends on the steps it played (the "
             "root parks at 2/2) under the new law RS1; the next message reseats both frames -- the "
             "root on its three steps, the holder's SERVE and INFER done, its CALL holding the root "
             "-- each traced `reseated`, nothing replayed")
    else:
        failures.append(f"  ✗ reseated                    {root and root.stack!r} "
                        f"{ended and (ended.stack, ended.wait)!r} {rested and rested.wait!r} "
                        f"{taken and (taken.stack, taken.wait)!r} "
                        f"holder={holder_done} said={said} moved={moved}")

    holder.write_text("---\nname: H\nproc: |\n  INFER\n---\n", encoding="utf-8")
    stepped(conductor)
    stepped(conductor)                                      # the root's last step, pending for the principal
    lost = stepped(conductor)                               # the principal's bare call parks the run
    viewed = conductor().peek()                                 # a view reseats nothing
    kept = [one.get("keyword") for one in
            json.loads(slot.read_text(encoding="utf-8"))["frames"][0]["instructions"]]
    if (lost is not None and lost.wait and viewed is not None and len(reseats(slot)) == 2
            and kept == ["SERVE", "INFER", "CALL"]):
        held("only the opening reseats", "parked over a holder that lost its CALL, `-peek` leaves "
             "the saved steps and writes no `reseated`")
        expect("session-stale", lambda: conductor().submit("the next message"))
    else:
        failures.append(f"  ✗ the lost CALL               {lost and (lost.stack, lost.wait)!r}")
    conductor().forget()

    persistence.forget(session_of(home.meta))
    expect("no-run", lambda: conductor().submit("core"))

    # --- metrics: what is served is weighed, part by part, and the parts add up -------
    lawful = conductor()
    lawful.forget()
    first = lawful.start(document("---\nname: X\nconstraints.behavior: |\n  RG3  never touch a neighbour\n"
                                  "proc: |\n  INFER\n---\n"))
    lawful.forget()
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

    # a fused output: each block weighs what it adds, and the blocks add up to the output
    fuser = conductor()
    fuser.forget()
    fused = fuser.start(document("---\nname: X\nfusion: max\nproc: |\n  INFER\n"
                                 "  SERVE TAGGED.md\n  INFER\n---\n"))
    served = dict(fuser._served)
    if (fused.stacked and served.get("blocks", 0) > 1 and served.get("total") == len(render(fused))
            and sum(served[part] for part in metrics.PARTS) == served["total"]):
        held("the blocks of a fused output add up to it", f"{served['blocks']} blocks, {served['total']} "
             "characters: the steps stacked and the block that closes weigh the output they make, part by part")
    else:
        failures.append(f"  ✗ fused metrics             {served} output={len(render(fused))}")
    fuser.forget()

    # a block merged into the segment of another frame counts no law: the laws are the opener's;
    # the system laws are said whole once per output, and weigh there
    said_system = sum(len(str(one)) + 1 for one in compiling.system_laws(home.meta))
    (home.meta / "CHILDW.md").write_text("---\nname: CHILDW\nkind: proc\nfusion: max\nproc: |\n  INFER\n---\n\n"
                                         "the child's line\n", encoding="utf-8")
    law = "RG4  say it once"
    joiner = conductor()
    joiner.forget()
    joined = joiner.start(document(f"---\nname: X\nfusion: max\nconstraints.behavior: |\n  {law}\n"
                                   "proc: |\n  INFER\n  CALL CHILDW.md\n---\n"))
    joint = dict(joiner._served)
    shown = render(joined) if joined is not None else ""
    if (joined is not None and len(joined.stacked) == 1 and joint.get("blocks", 0) >= 2
            and joint.get("total") == len(shown) and sum(joint[part] for part in metrics.PARTS) == joint["total"]
            and joint.get("constraints") == len(law) + 1 + said_system and shown.count(law) == 1):
        held("a block merged into a segment counts no law", f"two steps of two frames under one law, one segment: "
             f"{joint['blocks']} blocks, {joint['total']} characters, the law weighed once beside "
             f"the system laws ({joint['constraints']}), the parts add up to the output")
    else:
        failures.append(f"  ✗ merged metrics            {joint} output={len(shown)} "
                        f"segments={joined and len(joined.stacked)}")
    joiner.forget()

    # a mount is weighed with the block that renders it: its body in `payload`, its law in `constraints`
    body, mounted_law = "the mounted matter, weighed\n", "MW1  the mounted law holds"
    (home.meta / "WEIGHED.md").write_text(f"---\nname: WEIGHED\nkind: doc\nconstraints.behavior: |\n  {mounted_law}\n"
                                          f"---\n\n{body}", encoding="utf-8")
    host = conductor()
    host.forget()
    host.start(document("---\nname: X\nproc: |\n  INFER\n  INFER\n---\n"))
    stood = dict(host._served)
    mounter = conductor()
    view = mounter.mount([{"doc": "WEIGHED.md", "body": True}])
    grown = {part: mounter._served.get(part, 0) - stood.get(part, 0) for part in (*metrics.PARTS, "total", "blocks")}
    if (grown["blocks"] == 1 and grown["total"] == len(view)
            and sum(grown[part] for part in metrics.PARTS) == grown["total"]
            and grown["payload"] >= len(body.strip())
            and grown["constraints"] == len(mounted_law) + 1 + said_system):
        held("a mount is weighed with the block that renders it", f"one block, {grown['total']} characters: the "
             f"mounted body in `payload` ({grown['payload']}), its law in `constraints` beside the "
             f"system laws its output says ({grown['constraints']}), the parts equal to the total")
    else:
        failures.append(f"  ✗ mount metrics             {grown} view={len(view)}")
    mounter.forget()

    piled = metrics.add(metrics.add({}, riding, render(riding)), riding, render(riding))
    if piled["blocks"] == 2 and piled["total"] == 2 * weighed["total"]:
        held("the session accumulates", "a run is a session: the floor never pops")
    else:
        failures.append(f"  ✗ accumulation              {piled}")

    # --- the CLI renders a block, then the AWAIT block that parks the run ----------------
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
    if shown == fed == done == 0 and "PICK member" in spoken_text and "▶ AWAIT" in spoken_text:
        held("the CLI", "renders a block, then the AWAIT block parks the run")
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

    (tuned.meta / "OPS.md").write_text(
        "---\nname: OPS\nproc: |\n  INFER\n---\nconsign the last exchange\n",
        encoding="utf-8")
    loop_doc = tuned.meta / "LOOP.md"
    loop_doc.write_text(
        "---\nname: LOOP\nproc: |\n  CALL OPS.md ^ @SETTINGS.ops_every\n"
        "  INFER\n---\nthe restitution\n", encoding="utf-8")

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
    if (messages.titled(language.CONTEXT, "CAPS") in ctx_rendered
            and messages.titled(language.INFORMATION, "CAPS") not in ctx_rendered
            and messages.titled(language.INFORMATION, "standing orders") in ctx_rendered
            and messages.titled(language.INFORMATION, "NOTE.md") in ctx_rendered
            and messages.titled(language.INFORMATION, "AGENT") in ctx_rendered
            and ctx_rendered.index(messages.titled(language.INFORMATION, "AGENT")) < ctx_rendered.index(messages.titled(language.INFORMATION, "NOTE.md"))):
        held("the pending document's body is CONTEXT",
             "CAPS alone promotes; the standing orders, the member's body and its reading "
             "stay INFORMATION, the body before the row it serves")
    else:
        failures.append(f"  ✗ context label              {ctx_rendered[:400]!r}")

    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nmax_harness_tool_output: 300\n---\n", encoding="utf-8")
    tuned_conductor().forget()
    own_context = render(tuned_conductor().start(loop_doc))
    if messages.titled(language.CONTEXT, "LOOP") in own_context:
        held("a root INFER contexts its own body", "the smallest case: the document asks, its body frames")
    else:
        failures.append(f"  ✗ own context                {own_context[:200]!r}")

    (tuned.meta / "BIGREAD.md").write_text("y" * 1200 + "\n", encoding="utf-8")
    (tuned.meta / "READER.md").write_text(
        "---\nname: READER\nproc: |\n  SERVE BIGREAD.md\n  INFER\n---\nread it all\n",
        encoding="utf-8")
    tuned_conductor().forget()
    chunked = tuned_conductor().start(tuned.meta / "READER.md")
    if chunked.command == "INFER" and language.CONTEXT in render(chunked):
        held("a reading and its ask share one output", "the document rides its section, the "
             "pending step its context and its INSTRUCTION -- one screen, no order block")
    else:
        failures.append(f"  ✗ reading and ask            {chunked.command!r}")

    ending = stepped(tuned_conductor)          # printed, then the principal's bare call: the passage ends
    signal_rendered = render(ending) if ending is not None else ""
    signal_lines = signal_rendered.rstrip().splitlines()
    marked = [i for i, line in enumerate(signal_lines) if line.startswith("▶ ")]
    if (signal_rendered.count("▶") == 1 and marked
            and all(line.startswith("   (") for line in signal_lines[marked[0] + 1:])):
        held("the signal mark is one and last",
             "▶ appears once per block, the AWAIT that parks the run with no command under it; the note alone after it")
    else:
        failures.append(f"  ✗ signal mark                 count={signal_rendered.count('▶')} "
                        f"{signal_lines[-3:]!r}")

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

    # --- the OUTPUT names form AND channel; excess is caught ------------------------------
    ctx.write_member("output: table\n")       # the boot opens on a said step: `table => terminal`

    def chan_c():
        return run.conductor_of(ctx, None)

    chan_open = chan_c().start(chan_c().boot("BOOT.md"))
    caught = chan_c().submit("| a table | pasted into the tool |")
    after_catch = stepped(chan_c)
    if (f"table => {language.TERMINAL}" in render(chan_open)
            and caught.deviation and caught.repair == 0
            and caught.instruction.repairs == 0
            and after_catch.document == "TURN"
            and f"any => {language.TERMINAL}" in render(after_catch)):
        held("the channel is rendered and guarded", "the line says `form => terminal`; "
             "a pasted draft comes back -- 0 repair -- and its print advances")
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
    elected = elect_c.submit('["a", "b"]')
    footless = [one for one in (fed_block, elect_block, elected) if one.label or one.next_call]
    if (fed_block.output == "json" and fed_block.channel == language.TOOL_HEREDOC
            and elect_block.output == language.LIST and elect_block.channel == language.TOOL_HEREDOC
            and elected.output == "options" and elected.channel == language.TOOL
            and f"=> {language.TOOL_HEREDOC}  (" in render(fed_block)
            and f"=> {language.TOOL}  (" in render(elected) and not footless):
        held("a value's channel says how it is handed", "a CALL-fed json and the list a PICK elects from "
             "are piped by a heredoc, whatever the document's `output:`; the choice travels on the call; "
             "no closing repeats the call")
    else:
        failures.append(f"  ✗ value channels            {fed_block.channel!r} {elect_block.channel!r} "
                        f"{elected.channel!r} foot={[one.next_call for one in footless]!r}")
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

    system_said(bench)
    return 0


SAYS = ("---\nname: SAYS\nkind: proc\nconstraints.production: |\n  CP1  the line is short.\n"
        "constraints.behavior: |\n  CB1  say it plainly.\nproc: |\n  INFER\n  INFER\n---\nSay a line.\n")
OUTER = ("---\nname: OUTER\nkind: proc\nconstraints.behavior: |\n  OB1  the outer law.\n"
         "proc: |\n  INFER\n  CALL INNER.md\n---\nthe outer line\n")
INNER = ("---\nname: INNER\nkind: proc\nconstraints.behavior: |\n  IB1  the inner law.\n"
         "proc: |\n  INFER\n---\nthe inner line\n")


def _constraints(text: str) -> list[list[str]]:
    """-> the lines of every `▌ CONSTRAINTS` section of an output, in order."""
    found, lines = [], text.splitlines()
    for at, line in enumerate(lines):
        if line == f"▌ {language.CONSTRAINTS}":
            section = []
            for one in lines[at + 1:]:
                if not one.strip() or one.startswith("▌ "):
                    break
                section.append(one)
            found.append(section)
    return found


def system_said(bench) -> None:
    """A system law is said whole in every output, at the head of its group of the first
    CONSTRAINTS section, under `verbatim_constraints` true and false alike -- two outputs in a
    row, never its code; a fused output of two segments says it once."""
    held, failures = bench.held, bench.failures
    said: dict[bool, list[list[str]]] = {}
    for verbatim in (True, False):
        env = bench.env(f"core-sys-{str(verbatim).lower()}")
        env.write("SETTINGS.md", f"---\nname: SETTINGS\nkind: doc\nverbatim_constraints: {str(verbatim).lower()}\n"
                                 "instructions_fusion: none\n---\n")
        env.write("procs/SAYS.md", SAYS)
        env.write_system(production="SYS7  the system's production law holds.",
                         behavior="SYS8  the system's behavior law holds.")
        system = compiling.system_laws(env.made)
        opened = cli(env.engine, "-new", "go", cwd=env.root, env={"PP_DOOR": "SAYS.md"})
        key = (KEY.search(opened.stdout) or KEY.search("run ------")).group(1)
        second = cli(env.engine, key, "-print", "SAYS", "-", cwd=env.root, stdin="said")
        outputs = [opened.stdout, second.stdout]
        sections = [_constraints(one) for one in outputs]
        whole = all(one and all(str(law) in one[0] for law in system)
                    and sum(str(law) in line for part in one for line in part for law in system) == len(system)
                    for one in sections)
        firsts = [str(next(law for law in system if law.section == name)) for name in ("production", "behavior")]
        heads = all(one and one[0][0] == "production:" and one[0][1] == firsts[0]
                    and one[0][one[0].index("behavior:") + 1] == firsts[1] for one in sections)
        coded = [line for one in sections for part in one for line in part
                 if line.startswith("[") and any(law.code in line for law in system)]
        documents = ("CB1  say it plainly." in "\n".join(sections[1][0]) if sections[1] else False) == verbatim
        said[verbatim] = [[line for line in one[0] if any(line == str(law) for law in system)]
                          for one in sections if one]
        if opened.returncode == 0 and second.returncode == 0 and whole and heads and not coded and documents:
            held(f"the system law whole, verbatim {str(verbatim).lower()}",
                 f"two outputs in a row: {', '.join(law.code for law in system)} whole at the head of "
                 "their groups of the first CONSTRAINTS, never a code; CB1 "
                 + ("whole again" if verbatim else "back as its code"))
        else:
            failures.append(f"  ✗ system law, verbatim {verbatim}   rc={opened.returncode}/{second.returncode} "
                            f"whole={whole} heads={heads} coded={coded} documents={documents} {sections!r}")
    if said[True] and said[True] == said[False]:
        held("the system law reads alike under both settings", "the system lines of the two outputs are "
             "the same under verbatim true and false")
    else:
        failures.append(f"  ✗ system law alike            {said!r}")

    env = bench.env("core-sys-fused")
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n")
    env.write("procs/OUTER.md", OUTER)
    env.write("procs/INNER.md", INNER)
    env.write_system(behavior="SYS8  the system's behavior law holds.")
    system = compiling.system_laws(env.made)
    fused = cli(env.engine, "-new", "go", cwd=env.root, env={"PP_DOOR": "OUTER.md"})
    sections = _constraints(fused.stdout)
    once = bool(sections) and all(sum(str(law) == line for part in sections for line in part) == 1
                                  and str(law) in sections[0] for law in system)
    if fused.returncode == 0 and len(sections) >= 2 and once and "IB1  the inner law." in "\n".join(sections[-1]):
        held("a fused output says the system law once", f"{len(sections)} CONSTRAINTS sections in one output: "
             "the system laws whole in the first, absent from the next")
    else:
        failures.append(f"  ✗ fused system law            rc={fused.returncode} {sections!r}")
