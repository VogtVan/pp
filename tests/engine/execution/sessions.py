"""Scenario `sessions` -- 21 case(s), in the monolith's order:
- `-new` on a run's own key: start() reopens THAT run fresh
(what the kit's CAPABILITIES does -- the catalog served in its frame, offered at the member
for the whole turn -- lives at `bases/kit/tests/engine/seeded-member.py`; the FINAL under
the kit's `capture_prompt` at `bases/kit/tests/engine/frontier-asks.py`)
- P3.2 the trace: one file per run, append-only, outliving new/reset/sync
- L2.7 SETTINGS.md: the tuning is the instance's own document, defaults otherwise
- le-message-a-l-ouverture: a message opens a run, the reprise takes one at any setting, a stray off the frontier bounces
- R7.9a les-coutures: the cut lands on a line, the mid-reading sheds its habit --
- L2.9 the guard: `^ @Doc.field` paces an instruction on a declared cadence
- L2.9 the register skill: append-only, budget-guarded, instance-homed
- L2.10 memory: the record read back by PERIOD -- free will, never forced
- L2.8 the context has a name: the proc-carrier's body is not a mere reading
- the member's laws ride the block as written; the card reaches the first block
- lot B: peek is DRY; a direct script call is the operator's raw escape hatch
- lot C: an UPPER name is a PROC, opened through pp -- conducted, scoped, purged
- tout-passe-par-pp: the reflex IS the call -- pp plays the skill, one gesture
- la-cle-avance: keyless never mutates; the key is the consent to advance
- les-blocs-se-compressent: fusion by invariant anchors
- R7.9a les-coutures: the order closing dresses for what it carries
- le-serve-du-membre: the cheatsheet's examples PLAY, the doors serve it, and a
- le-saut-de-section: the § holds before a CHAINING step too
- les-canaux-se-disent: the OUTPUT names form AND channel; excess is caught
- tout-est-un-skill: declared harness names offered, the indifference invariant
- chaque-conversation-tient-son-run: multi_session, one run PER conversation
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
from pathlib import Path
from conductor import Conductor, Refusal, render, compiling, discovery, persistence, reading
from tests.harness import steady, PLAYABLE, document, load_script, session_of, body_of, reaches, cli
from conductor import install as install_module



class Opened:
    """A door opened through the facade, read like the console would print it."""

    def __init__(self, block) -> None:
        self.returncode = 0 if block is not None else 2
        self.stdout = render(block) if block is not None else ""


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- the first environment: three instances side by side, `core` the home
    town = bench.town(["core", "perso", "sw7-hub"])
    siblings = town.siblings
    home = town["core"].member
    script = town["core"].engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")


    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, script, "t")


    # --- `-new` on a run's own key: start() reopens THAT run fresh ---------------------
    fresh_env = bench.env("fresh_start")
    fresh_made = fresh_env.made
    fresh_env.write_member()           # the boot opens on the member's brief, the turn one call later
    fresh_start = fresh_made.parent
    fresh_engine = fresh_made / ".sys" / "engine" / "pp.py"
    fresh_member = discovery.instance_member(fresh_engine)

    def fresh_start_conductor() -> Conductor:
        return Conductor(fresh_member, fresh_engine, "t")

    fresh_start_conductor().resume(fresh_start_conductor().boot("BOOT.md"))          # -> MEMBER
    fresh_start_conductor().submit("")                                            # -> the turn's inference
    resumed_again = fresh_start_conductor().resume(fresh_start_conductor().boot("BOOT.md"))
    own_key = persistence.run_id_of(persistence.slots(fresh_member.meta)[0])
    renew_c = Conductor(fresh_member, fresh_engine, own_key)
    renewed = renew_c.start(renew_c.boot("BOOT.md"))
    if (resumed_again is not None and resumed_again.document == "TURN"
            and renewed is not None and renewed.document == "MEMBER"
            and len(persistence.slots(fresh_member.meta)) == 1):
        held("re-new reopens the conversation's own run",
             "resume() keeps returning where the turn left off; start() on the run's key discards IT alone and reboots")
    else:
        failures.append(f"  ✗ new                        resumed={resumed_again and resumed_again.command!r} "
                        f"renewed={renewed and renewed.command!r}")

    # --- P3.2 the trace: one file per run, append-only, outliving new/reset/sync -------
    # the fresh_start sequence above IS the chronology: resume (run 1: new, block) ->
    # submit (answer, the turn's block) -> resume again (block repeated -- the double
    # call) -> re-new on the key (run 1's own trace closes on `reset`, a NEW file opens)
    trace_dir = fresh_member.meta / persistence.DIRECTORY
    second_name = persistence.trace_of(session_of(fresh_member.meta))
    second_trace = trace_dir / second_name if second_name else None
    second_events = ([json.loads(line) for line in
                      second_trace.read_text(encoding="utf-8").splitlines()]
                     if second_trace and second_trace.is_file() else [])
    older = sorted(one.name for one in trace_dir.glob("session-*.jsonl")
                   if one.name != second_name)
    first_trace = trace_dir / older[0] if older else None
    first_events = ([json.loads(line) for line in
                     first_trace.read_text(encoding="utf-8").splitlines()]
                    if first_trace and first_trace.is_file() else [])
    first_kinds = [one["kind"] for one in first_events]
    if (first_kinds and first_kinds[0] == "new" and "answer" in first_kinds
            and "block" in first_kinds and all("at" in one for one in first_events)):
        held("a run writes its own trace", "session-<UTC>.jsonl: new first, every event stamped, parseable")
    else:
        failures.append(f"  ✗ trace chronology           {first_kinds}")

    if (first_kinds[-1] == "reset" and first_kinds[-3:-1] == ["block", "block"]
            and first_events[-2].get("command") == first_events[-3].get("command")):
        held("the repeated call reads in the trace", "two identical blocks, no answer between -- the drift is visible")
    else:
        failures.append(f"  ✗ double call in trace       {first_kinds[-3:]}")

    if (second_trace is not None and first_trace is not None
            and second_trace.name != first_trace.name
            and second_events[0]["kind"] == "new" and first_kinds[-1] == "reset"):
        held("a new run opens a new file", "the discarded one closes on `reset` IN ITS OWN trace -- the chain reads per file")
    else:
        failures.append(f"  ✗ one file per run           {older!r} / {second_name!r}")

    closed = first_trace.read_bytes()
    fresh_start_conductor().submit("capability table")     # run 2 works on -- ITS file only
    if first_trace.read_bytes() == closed:
        held("a closed trace never moves again", "run 2's work lands in run 2's file, byte-identical run 1")
    else:
        failures.append("  ✗ closed trace mutated")

    fresh_start_conductor().forget()
    reset_event = json.loads(second_trace.read_text(encoding="utf-8").splitlines()[-1])
    noted_c = fresh_start_conductor()
    noted_c.resume(noted_c.boot("BOOT.md"))                # run 3 -- session was forgotten
    noted_c.noted(Refusal("probe-refusal", "lands in the trace"))
    third_trace = trace_dir / persistence.trace_of(session_of(fresh_member.meta))
    refusal_event = json.loads(third_trace.read_text(encoding="utf-8").splitlines()[-1])
    install_module.sync(fresh_member)          # constant pins: the run stands, nothing written
    kept_event = json.loads(third_trace.read_text(encoding="utf-8").splitlines()[-1])
    from conductor import instance as _instance
    moved = _instance.read(fresh_member.meta)
    moved["packages"] = {**_instance.pins(fresh_member.meta), "kit": "0.0.1-past"}
    _instance.write(fresh_member.meta, moved)
    install_module.upgrade(fresh_member)       # a version moves: the run is renewed, the trace says so
    sync_event = json.loads(third_trace.read_text(encoding="utf-8").splitlines()[-1])
    if (reset_event["kind"] == "reset"
            and refusal_event["kind"] == "refusal" and refusal_event["code"] == "probe-refusal"
            and kept_event["kind"] == "refusal" and sync_event["kind"] == "renewed"):
        held("reset, refusal and renewal say so", "each lands in the RUN'S file -- a sync at "
             "constant pins writes none of it, the upgrade that renews the run does")
    else:
        failures.append(f"  ✗ lifecycle events           {reset_event['kind']} / "
                        f"{refusal_event.get('kind')} / {sync_event['kind']}")

    # --- L2.7 SETTINGS.md: the tuning is the instance's own document, defaults otherwise
    # (that "absent file = defaults" holds is proven by the WHOLE suite: no fixture
    # above carries a SETTINGS.md, and none of them changed for this lot)
    if (fresh_member.meta / "SETTINGS.md").is_file():
        held("install seeds SETTINGS.md", "the template carries it -- the operator's file from day one")
    else:
        failures.append("  ✗ SETTINGS.md not seeded")

    tuned_siblings = bench.town(["solo"]).siblings
    tuned = discovery.member(tuned_siblings, "solo")
    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 500\nwork_repairs_allowed: 1\n"
        "verbatim_constraints: false\n---\n", encoding="utf-8")

    def tuned_conductor() -> Conductor:
        return Conductor(tuned, script, "t")

    asked = document("---\nname: ASK\ncycle: true\nconstraints.behavior: |\n  Z9  say it plainly\n"
                     "proc: |\n  INFER\n  FINAL\n---\nwhat would you do?\n")
    ask_block = tuned_conductor().start(asked)
    ask_rendered = render(ask_block)
    second = tuned_conductor().submit("the operator said X")   # the cycle reopens: Z9 re-emits
    second_rendered = render(second) if second is not None else ""
    if (ask_block.wait and "▶ FINAL" in ask_rendered
            and "say it plainly" in ask_rendered
            and "Z9" in second_rendered and "say it plainly" not in second_rendered):
        held("the codes mode takes effect",
             "the FINAL fires on the operator's message; the first emission says the "
             "text, the re-emission its code alone")
    else:
        failures.append(f"  ✗ tuned block                {ask_block.next_call!r} / {ask_rendered!r}")
    tuned_trace = tuned.meta / persistence.DIRECTORY / persistence.trace_of(
        session_of(tuned.meta))
    captured = [json.loads(line) for line in tuned_trace.read_text(encoding="utf-8").splitlines()]
    if any(one["kind"] == "prompt" and one["text"] == "the operator said X" for one in captured):
        held("the message lands in the trace", "the text handed at the frontier is traced `prompt` -- the session log")
    else:
        failures.append(f"  ✗ captured prompt            {[one['kind'] for one in captured]}")

    (tuned.meta / "TFORMS.md").write_text(
        "---\nname: TFORMS\ndescription: bench formats\nformats: |\n"
        "  json  inline  one valid JSON value\n---\n", encoding="utf-8")
    tuned_conductor().start(document(PLAYABLE, at=tuned.meta))
    tuned_conductor().submit("nobody")                       # repair 1 -- the whole allowance
    expect("repair-exhausted", lambda: tuned_conductor().submit("nobody"))

    # the serve reads WHOLE -- what an output cannot hold is the block's cut, proven
    # at engine/rendering/cut; here only that a big reading rides in one titled section
    (tuned.meta / "BIG.md").write_text("x" * 1200 + "\n", encoding="utf-8")
    (tuned.meta / "BIGRUN.md").write_text(
        "---\nname: BIGRUN\nproc: |\n  SERVE BIG.md\n  INFER\n---\n", encoding="utf-8")
    paced = tuned_conductor().start(tuned.meta / "BIGRUN.md")
    if paced.command == "INFER" and len(dict(paced.payloads)["BIG.md"]) == 1200:
        held("a reading rides whole", "1200 chars in one section, the instruction on the same "
             "output -- the serve counts nothing")
    else:
        failures.append(f"  ✗ whole reading              {paced.command!r} "
                        f"{sum(len(t) for _, t in paced.payloads)}")
    tuned_conductor().forget()

    # --- le-message-a-l-ouverture: a message OPENS a run -- traced `prompt` after `new`,
    #     before the first block; what a base serves of it is the base's own
    def tuned_events() -> list[dict]:
        trace_path = tuned.meta / persistence.DIRECTORY / persistence.trace_of(session_of(tuned.meta))
        return [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]

    opened_block = tuned_conductor().start(asked, "the trigger said Y")
    opened_events = tuned_events()
    opened_kinds = [one["kind"] for one in opened_events]
    if (opened_block is not None and opened_block.document == asked.stem and opened_block.wait
            and opened_kinds[:2] == ["new", "prompt"]
            and opened_events[1]["text"] == "the trigger said Y"
            and "block" in opened_kinds):
        held("a message opens a run", "start(ASK, text): the trace says new, prompt, then block -- "
             "the message is a line of the trace, the first block comes after it")
    else:
        failures.append(f"  ✗ message at -new            {opened_kinds[:4]} "
                        f"{opened_block and opened_block.document!r}")
    tuned_conductor().forget()

    # --- the reprise takes the message at ANY setting: no `capture_prompt` (no key, no
    #     preset) -- the FINAL is bare, the text at the frontier is the principal's word
    (tuned.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nconduction_effort: none\nmax_harness_tool_output: 500\n"
        "work_repairs_allowed: 1\n---\n", encoding="utf-8")
    bare_block = tuned_conductor().start(asked)
    bare_second = tuned_conductor().submit("the operator said X again")
    prompted = [one for one in tuned_events() if one["kind"] == "prompt"]
    if (bare_block is not None and bare_block.wait
            and "<the principal's next message>" not in bare_block.next_call
            and bare_second is not None and bare_second.document == asked.stem and bare_second.wait
            and prompted and prompted[-1]["text"] == "the operator said X again"):
        held("the reprise takes the message at any setting",
             "no capture_prompt anywhere: the FINAL closes bare, the text handed at the "
             "frontier is traced `prompt` and the floor replays -- the position decides")
    else:
        failures.append(f"  ✗ reprise without capture    {bare_block and bare_block.next_call!r} "
                        f"{bare_second and bare_second.document!r} "
                        f"{[one['text'] for one in prompted]}")
    tuned_conductor().forget()

    # --- off the frontier, a text handed to a step that awaits nothing is a STRAY:
    #     bounced softly, nothing traced -- still no setting in the way
    (tuned.meta / "NOTE.md").write_text("a note between steps\n", encoding="utf-8")
    (tuned.meta / "MID.md").write_text(
        "---\nname: MID\nproc: |\n  INFER\n  SERVE NOTE.md\n  INFER\n---\nsay two things\n",
        encoding="utf-8")
    mid_first = tuned_conductor().start(tuned.meta / "MID.md")
    strayed = tuned_conductor().submit("a stray production")
    stray_kinds = [one["kind"] for one in tuned_events()]
    if (mid_first is not None and not mid_first.wait
            and strayed is not None and "Nothing was recorded" in (strayed.deviation or "")
            and strayed.repair == 0 and "prompt" not in stray_kinds):
        held("a stray text off the frontier bounces", "a step that awaits nothing, no FINAL "
             "just closed: DEVIATION says it, 0 repair, no `prompt` in the trace")
    else:
        failures.append(f"  ✗ stray off the frontier     {strayed and strayed.deviation!r} "
                        f"{stray_kinds}")
    tuned_conductor().forget()

    same_lines = ["name: MEMO", "tools: |", "  alpha beta"]
    memo_a, memo_b = reading.front_matter(same_lines), reading.front_matter(same_lines)
    edited = reading.front_matter(["name: MEMO", "tools: |", "  alpha gamma"])
    if memo_a == memo_b and memo_a is not memo_b and edited["tools"] != memo_a["tools"]:
        held("the front matter parses once", "memoized by content -- equal reads, each its "
             "own top; an edited text misses the drawer")
    else:
        failures.append(f"  ✗ parse memo                  {memo_a is memo_b} {edited!r}")

    broken_siblings = bench.town(["broken"]).siblings
    broken = discovery.member(broken_siblings, "broken")
    (broken.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nmax_harness_tool_output: banana\n---\n", encoding="utf-8")
    expect("settings-invalid", lambda: Conductor(broken, script))
    (broken.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nverbatim_constraints: maybe\n---\n", encoding="utf-8")
    expect("settings-invalid", lambda: Conductor(broken, script))

    # --- L2.9 the guard: `^ @Doc.field` paces an instruction on a declared cadence -----
    paced_siblings = bench.town(["cadence"]).siblings
    paced_home = discovery.member(paced_siblings, "cadence")
    (paced_home.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nops_every: 1\n---\n", encoding="utf-8")
    (paced_home.meta / "OPS.md").write_text(
        "---\nname: OPS\nproc: |\n  INFER\n---\nconsign the last exchange\n",
        encoding="utf-8")
    loop_doc = paced_home.meta / "LOOP.md"
    loop_doc.write_text(
        "---\nname: LOOP\ncycle: true\nproc: |\n  CALL OPS.md ^ @SETTINGS.ops_every\n"
        "  INFER\n  FINAL\n---\nthe restitution\n", encoding="utf-8")

    def paced_c() -> Conductor:
        return Conductor(paced_home, script, "t")

    guard_first = paced_c().start(loop_doc)
    guard_second = paced_c().resume(loop_doc)
    guard_closed = paced_c().submit("")
    if (guard_first.document == "LOOP" and guard_first.wait
            and guard_second.document == "OPS" and not guard_second.wait
            and guard_closed.document == "LOOP" and guard_closed.wait):
        held("a guarded CALL paces on the setting",
             "never the first turn; from the second, the consignation opens the exchange")
    else:
        failures.append(f"  ✗ guard pacing               {guard_first.document}/"
                        f"{guard_second.document}/{guard_closed.document}")

    (paced_home.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nops_every: 3\n---\n", encoding="utf-8")
    paced_c().forget()
    walk = [paced_c().start(loop_doc).document]
    for _ in range(2, 8):
        step = paced_c().resume(loop_doc)
        walk.append(step.document)
        if step.document == "OPS":
            paced_c().submit("")
    if walk == ["LOOP", "LOOP", "LOOP", "OPS", "LOOP", "LOOP", "OPS"]:
        held("the cadence holds", "ops_every: 3 -- the record opens exchanges 4 and 7, none other")
    else:
        failures.append(f"  ✗ cadence                    {walk}")

    (paced_home.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nops_every: banana\n---\n", encoding="utf-8")
    paced_c().forget()
    expect("guard-invalid", lambda: paced_c().start(loop_doc))   # parsed before the
    # cadence check: a lie refuses at once, it does not wait for its turn

    (paced_home.meta / "SETTINGS.md").unlink()
    paced_c().forget()
    absent_first = paced_c().start(loop_doc)
    absent_second = paced_c().resume(loop_doc)
    if absent_first.document == "LOOP" and absent_second.document == "LOOP":
        held("an absent setting means off", "no SETTINGS.md, no field -- the guard skips, nothing refuses")
    else:
        failures.append(f"  ✗ guard absent               {absent_first.document}/{absent_second.document}")

    # --- L2.9/L2.10 and the TURN-offers-memory case migrated RED to continuity
    # (KPS21, batch la-purete-du-kit): the continuity skill left the kit.

    # --- L2.8 the context has a name: the proc-carrier's body is not a mere reading ----
    ctx_env = bench.env("ctx")
    ctx_made = ctx_env.made
    ctx_env.write("NOTE.md", "---\nname: NOTE\nkind: doc\ndescription: a reading of the member\n---\n\n"
                             "the note the member reads every session\n")
    ctx_env.write("procs/CAPS.md", "---\nname: CAPS\nkind: proc\ndescription: the member's brief\n"
                                   "proc: |\n  INFER\n---\n\nthe witness's capabilities, asked once\n")
    ctx_env.write_member("serve: |\n  reference: NOTE.md\nconstraints.behavior: |\n"
                         "  A1  the agent's own law rides the block\n",
                         body="the witness agent", proc="SERVE\n  CALL CAPS.md", name="AGENT")
    ctx_member = discovery.instance_member(ctx_made / ".sys" / "engine" / "pp.py")
    ctx_c = Conductor(ctx_member, ctx_made / ".sys" / "engine" / "pp.py")
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

    (paced_home.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nmax_harness_tool_output: 300\n---\n", encoding="utf-8")
    paced_c().forget()
    own_context = render(paced_c().start(loop_doc))
    if "NEXT INSTRUCTION CONTEXT — LOOP" in own_context:
        held("a root INFER contexts its own body", "the smallest case: the document asks, its body frames")
    else:
        failures.append(f"  ✗ own context                {own_context[:200]!r}")

    (paced_home.meta / "BIGREAD.md").write_text("y" * 1200 + "\n", encoding="utf-8")
    (paced_home.meta / "READER.md").write_text(
        "---\nname: READER\nproc: |\n  SERVE BIGREAD.md\n  INFER\n---\nread it all\n",
        encoding="utf-8")
    paced_c().forget()
    chunked = paced_c().start(paced_home.meta / "READER.md")
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

    # the memory-contract wording case migrated with the continuity skill.

    # --- lot B: peek is DRY; a direct script call is the operator's raw escape hatch ---
    def ctx_conductor() -> Conductor:
        return Conductor(ctx_member, ctx_made / ".sys" / "engine" / "pp.py")

    ctx_conductor().submit("")     # -> TURN stands, the kit's offers alone
    ctx_session = session_of(ctx_member.meta)
    ctx_log = ctx_session.parent / persistence.trace_of(ctx_session)
    frozen_state, frozen_trace = ctx_session.read_bytes(), ctx_log.read_bytes()
    peeked = ctx_conductor().peek()
    offers = [one.name for one in (peeked.tools if peeked else ())]
    elsewhere_offered = "pp-elsewhere" in offers
    upper_offered = "ELSEWHERE" in offers
    if (peeked is not None and peeked.document == "TURN"
            and not elsewhere_offered and not upper_offered
            and ctx_session.read_bytes() == frozen_state
            and ctx_log.read_bytes() == frozen_trace):
        held("peek is dry",
             "the block that STANDS -- nothing offered on the naked turn, state "
             "and trace byte-identical (the scoped-offer half migrated with the skills)")
    else:
        failures.append(f"  ✗ peek                        {peeked and peeked.document} "
                        f"{elsewhere_offered}/{upper_offered}")

    # the raw-escape-hatch cases of the two records migrated with the continuity
    # skill to its package -- the dispatch gate stays proven by the conducted paths above.

    # --- lot C: an UPPER name is a PROC, opened through pp -- conducted, scoped, purged
    (ctx_member.meta / "procs").mkdir(exist_ok=True)
    (ctx_member.meta / "procs" / "NOTE.md").write_text(
        "---\nname: NOTE\nkind: proc\ndescription: a scratch note, agent-opened\n"
        "output: line\nproc: |\n  INFER\n---\njot the note down\n",
        encoding="utf-8")
    (ctx_member.meta / "procs" / "TURN.md").write_text(      # the overlay offers NOTE and arms
        "---\nname: TURN\ntools: |\n  +NOTE\nconstraints.behavior: |\n"    # a law of the turn's own:
        "  +TB1  the turn's law rides every frame above it\n---\n", encoding="utf-8")   # the stack carries it down
    # an offer stands with the OUTPUT that carries it: the overlay written mid-exchange
    # reaches the screen and the router at the next advance, never before
    noted = [one.name for one in ctx_conductor().submit("").tools]
    seen_at_view = [one.name for one in ctx_conductor().peek().tools]
    note_offered, stranger_offered = "NOTE" in noted, "STRANGER" in noted
    opened = ctx_conductor().play("NOTE")
    if (note_offered and not stranger_offered and seen_at_view == noted
            and opened.document == "NOTE" and "▸ NOTE" in opened.stack
            and any(c.code == "TB1" for c in opened.constraints)):
        held("a proc opens conducted", "+NOTE offered by overlay -- the view shows the "
             "output's own list, and the proc plays STACKED over the turn, TB1 riding")
    else:
        failures.append(f"  ✗ play                        {note_offered}/{stranger_offered} "
                        f"{opened and opened.stack!r}")

    noted_back = ctx_conductor().submit("")
    replayed_clean = ctx_conductor().resume(ctx_conductor().boot("BOOT.md"))
    if (noted_back.document == "TURN" and not noted_back.wait
            and replayed_clean.document == "TURN"
            and "NOTE" not in replayed_clean.stack):
        held("the injected CALL never replays", "answered, the turn's own step returns; NOTE is purged clean")
    else:
        failures.append(f"  ✗ injected purge              {noted_back.document}/"
                        f"{replayed_clean.stack!r}")

    # --- tout-passe-par-pp: the reflex IS the call -- pp plays the skill, one gesture
    # (the kit's skills left with their packages: a LOCAL instance skill, OFFERED by the
    # member, proves the dispatch; an unoffered sibling proves the catch)
    note_home = ctx_made / "skills" / "pp-note"
    note_home.mkdir(parents=True, exist_ok=True)
    (note_home / "SKILL.md").write_text(
        "---\nname: pp-note\ndescription: a local note skill\n---\n\npp-note\n",
        encoding="utf-8")
    (note_home / "pp-note.py").write_text(
        "def main(arguments):\n    print('pp-note: nothing noted')\n    return 0\n", encoding="utf-8")
    hush_home = ctx_made / "skills" / "pp-hush"
    hush_home.mkdir(parents=True, exist_ok=True)
    (hush_home / "SKILL.md").write_text(
        "---\nname: pp-hush\ndescription: a skill nobody offers\n---\n\npp-hush\n",
        encoding="utf-8")
    (hush_home / "pp-hush.py").write_text(
        "def main(arguments):\n    print('pp-hush: hushed')\n    return 0\n", encoding="utf-8")
    (ctx_member.meta / "procs" / "TURN.md").write_text(      # the turn's overlay offers the skill:
        "---\nname: TURN\ntools: |\n  +NOTE\n  +pp-note\n---\n", encoding="utf-8")   # the offer lives
    compiling.build_tools(ctx_made)                            # with the step that stands
    ctx_conductor().forget()
    ctx_conductor().resume(ctx_conductor().boot("BOOT.md"))
    ctx_conductor().submit("")     # -> TURN stands: the member's pp-note offered
    before_reflex = session_of(ctx_member.meta).read_bytes()
    reflex = cli(ctx_made / ".sys" / "engine" / "pp.py", "-s", "pp-note", "now")
    if (reflex.returncode == 0 and "pp ·" not in reflex.stdout
            and "pp-note: nothing noted" in reflex.stdout
            and session_of(ctx_member.meta).read_bytes() == before_reflex):
        held("the reflex renders no block", "one scope in view: the skill's output alone, "
             "and the run does not move")
    else:
        failures.append(f"  ✗ dispatch gesture            rc={reflex.returncode} "
                        f"{reflex.stdout[:150]!r} {reflex.stderr[:80]!r}")

    frozen_catch = session_of(ctx_member.meta).read_bytes()
    (ctx_made / "procs" / "HUSH.md").write_text(
        "---\nname: HUSH\nkind: proc\ndescription: an unoffered proc\nproc: |\n  INFER\n---\n\nhush\n",
        encoding="utf-8")
    compiling.build_tools(ctx_made)
    denied_reflex = cli(ctx_made / ".sys" / "engine" / "pp.py", "-s", "pp-hush", "now")
    denied_proc = cli(ctx_made / ".sys" / "engine" / "pp.py", "-s", "HUSH")
    if (denied_reflex.returncode == 2 and denied_proc.returncode == 2
            and "DEVIATION" in denied_reflex.stdout
            and "the floor resumes below" in denied_reflex.stdout
            and "the floor resumes below" in denied_proc.stdout
            and "REPAIR" not in denied_reflex.stdout
            and session_of(ctx_member.meta).read_bytes() == frozen_catch):
        held("the catch does not lie", "out of scope -- script or proc: the pending block "
             "answers, no REPAIR heading, state byte-identical, nothing played")
    else:
        failures.append(f"  ✗ dispatch catch              rc={denied_reflex.returncode}/"
                        f"{denied_proc.returncode} {denied_reflex.stdout[:120]!r}")

    ghost = cli(ctx_made / ".sys" / "engine" / "pp.py", "frobnicate")
    if ghost.returncode != 0 and "The KEY leads" in (ghost.stdout + ghost.stderr):
        held("an unknown name gets the usage", "nothing resolved, nothing played")
    else:
        failures.append(f"  ✗ dispatch unknown            rc={ghost.returncode}")

    # --- la-cle-avance: keyless never mutates; the key is the consent to advance ------
    frozen_look = session_of(ctx_member.meta).read_bytes()
    looked = cli(ctx_made / ".sys" / "engine" / "pp.py")
    stale = cli(ctx_made / ".sys" / "engine" / "pp.py", "abc123")
    gone_flag = cli(ctx_made / ".sys" / "engine" / "pp.py", "-answer")
    if (looked.returncode == 0 and "▌ pp ·" in looked.stdout
            and session_of(ctx_member.meta).read_bytes() == frozen_look
            and stale.returncode == 2 and "run-unknown" in stale.stderr
            and gone_flag.returncode != 0
            and "are gone" in (gone_flag.stdout + gone_flag.stderr)):
        held("keyless never mutates", "the bare call shows and leaves the state "
             "byte-identical; a stale key refuses named; the old flags say they are gone")
    else:
        failures.append(f"  ✗ keyless inspection          rc={looked.returncode}/"
                        f"{stale.returncode} {stale.stderr[:80]!r}")

    # --- les-blocs-se-compressent: fusion by invariant anchors ------------------------
    fus_made = bench.env("fus", pin=False).made
    fus_member = discovery.instance_member(fus_made / ".sys" / "engine" / "pp.py")
    fus_engine = fus_made / ".sys" / "engine" / "pp.py"

    def fus_c() -> Conductor:
        return Conductor(fus_member, fus_engine, "t")

    trio = fus_made / "TRIO.md"
    trio.write_text(
        "---\nname: TRIO\nkind: proc\ndescription: three response steps\nproc: |\n"
        "  INFER\n  INFER\n  INFER\n"
        "  FINAL\n---\nthree things to say\n", encoding="utf-8")
    fused_out = fus_c().start(trio)
    fus_trace = [json.loads(line)["kind"] for line in
                 (fus_member.meta / persistence.DIRECTORY
                  / persistence.trace_of(persistence.slot_of(fus_member.meta, "t")))
                 .read_text(encoding="utf-8").splitlines()]
    fused_text = render(fused_out)
    if (fused_out.wait and fus_trace.count("batched") == 3
            and fused_text.count("▌ INSTRUCTION") == 1
            and fused_text.count("INFER free => ephemeral") == 3
            and "▶ FINAL ephemerals => response (TRIO)" in fused_text):
        held("fusion: max renders the certain stretch",
             "three DRAFT steps, one output -- the lines collapse under ONE title, "
             "and the FINAL closing orders their delivery")
    else:
        failures.append(f"  ✗ fusion max                  wait={fused_out.wait} "
                        f"batched={fus_trace.count('batched')} "
                        f"instr={fused_text.count('▌ INSTRUCTION')}")

    if ("▌ TRIO{1-3/4}" in fused_text                       # one segment heading, and
            and fused_text.count("▌ pp · run t · ") == 1      # the output's own says
            and fused_text.count("▌ TRIO") == 1):             # the key, once
        held("the heading says the stretch", "one heading for the fused steps -- the "
             "range {1-3/4}, written once the assembler knows where the merge stopped")
    else:
        failures.append(f"  ✗ fused range                 {fused_text.splitlines()[0]!r}")

    (fus_member.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: 2\n---\n", encoding="utf-8")
    fus_c().forget()
    capped = fus_c().start(trio)
    capped_text = render(capped)
    capped_rest = fus_c().forward("")
    if (capped_text.count("▌ INSTRUCTION") == 1
            and capped_text.count("INFER free => ephemeral") == 2 and not capped.wait
            and capped_rest is not None and capped_rest.wait):
        held("fusion: n caps the stretch", "two steps this output, the CONTINUE hands "
             "the rest -- the next call carries the third and the frontier")
    else:
        failures.append(f"  ✗ fusion cap                  {capped_text.count('▌ INSTRUCTION')} "
                        f"{capped_rest and capped_rest.wait}")

    (fus_member.meta / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n", encoding="utf-8")
    barred = fus_made / "BARRED.md"
    barred.write_text(
        "---\nname: BARRED\nkind: proc\ndescription: a section break\nproc: |\n"
        "  INFER\n  §\n  INFER\n  # §\n"
        "  INFER\n  FINAL\n---\nbroken in two\n", encoding="utf-8")
    fus_c().forget()
    first_half = fus_c().start(barred)
    second_half = fus_c().forward("")
    if (render(first_half).count("▌ INSTRUCTION") == 1 and not first_half.wait
            and second_half is not None and second_half.wait
            and render(second_half).count("▌ INSTRUCTION") == 1
            and render(second_half).count("INFER free => ephemeral") == 2):
        held("the § break holds and the # § stays a comment",
             "fusion never crosses the marked step; the commented barrier is inert -- "
             "uncommenting is what arms it")
    else:
        failures.append(f"  ✗ section break               "
                        f"{render(first_half).count('▌ INSTRUCTION')}/"
                        f"{second_half and render(second_half).count('▌ INSTRUCTION')}")

    # --- le-saut-de-section: the anchor decides, never the type -------------------------
    # the same break before a CHAINING step (SERVE) -- the keyword changes nothing, which
    # is what `the anchors decide, never the types` said the day the § was born
    (fus_made / "CHAINED.md").write_text(
        "---\nname: CHAINED\nkind: doc\n---\n\nread me\n", encoding="utf-8")
    chained = fus_made / "CHAINBAR.md"
    chained.write_text(
        "---\nname: CHAINBAR\nkind: proc\ndescription: a break before a chaining step\n"
        "proc: |\n  INFER\n  §\n  SERVE CHAINED.md\n  INFER\n  FINAL\n---\n"
        "the anchor decides\n", encoding="utf-8")
    fus_c().forget()
    chain_first = fus_c().start(chained)
    chain_next = fus_c().forward("")
    chain_shown = render(chain_first)
    if (chain_shown.count("▌ INSTRUCTION") == 1
            and "INFORMATION — CHAINED" not in chain_shown
            and chain_next is not None
            and "INFORMATION — CHAINED" in render(chain_next)):
        held("the § holds before a CHAINING step too",
             "a break before SERVE closes the output as one before INFER does -- "
             "the anchor decides, never the type")
    else:
        failures.append(f"  ✗ section break, chaining     "
                        f"{chain_shown.count('▌ INSTRUCTION')} instruction(s), "
                        f"reading served early={'INFORMATION — CHAINED' in chain_shown}")

    capped_doc = fus_made / "CAPPED.md"
    capped_doc.write_text(
        "---\nname: CAPPED\nkind: proc\ndescription: pins its own pace\nfusion: none\n"
        "proc: |\n  INFER\n  INFER\n  FINAL\n---\n"
        "one by one\n", encoding="utf-8")
    fus_c().forget()
    own_pace = fus_c().start(capped_doc)
    if render(own_pace).count("▌ INSTRUCTION") == 1:
        held("a document pins its own fusion", "`fusion: none` in the front matter -- "
             "the author's pace outranks the instance's max")
    else:
        failures.append(f"  ✗ document fusion             {render(own_pace).count('▌ INSTRUCTION')}")

    proven_pair = fus_made / "PAIR.md"
    proven_pair.write_text(
        "---\nname: PAIR\nkind: proc\ndescription: produce and prove, fused\n"
        "constraints.production: |\n  P9  say it plainly\nproc: |\n  WORK\n---\n"
        "the ask\n", encoding="utf-8")
    fus_c().forget()
    pair = fus_c().start(proven_pair)
    pair_text = render(pair)
    if ("WORK" in pair_text and pair.output == "proof"
            and "your proof on stdin" in pair.next_call
            and pair_text.count("▶ CONTINUE") + pair_text.count("▶ FINAL") == 1
            and pair_text.count("▌ pp · run t · ") == 1
            and pair_text.count("▌ PAIR") == 1
            and pair_text.count("say it plainly") == 1):
        held("produce and prove fuse legally, B-merged", "same frame: one heading, one "
             "CONSTRAINTS -- the proof terminal rides the block; one closing, the proof piped")
    else:
        failures.append(f"  ✗ fused pair                  {pair.next_call!r}")
    if "▌ PAIR{1-2/2}" in pair_text:
        held("the elided closing extends the range", "the proof step's heading is held "
             "by the opener -- {1-2/2} covers the whole B-merge")
    else:
        failures.append(f"  ✗ closing range               {pair_text.splitlines()[0]!r}")
    if (pair_text.count("▌ INSTRUCTION") == 1
            and "WORK free => response" in pair_text
            and "INFER proof [P9] on all produced areas => tool (heredoc)" in pair_text):
        held("the real turn collapses", "WORK and its briefless proof under ONE "
             "INSTRUCTION title -- nothing rides between them any more")
    else:
        failures.append(f"  ✗ turn collapse               "
                        f"{pair_text.count('▌ INSTRUCTION')}")
    pair_fail = fus_c().submit('[{"code": "P9", "evidence": "off", "verdict": "fail"}]')
    if (pair_fail is not None and pair_fail.repair >= 1 and "WORK" in render(pair_fail)
            and "▌ [2] PAIR{2/2} · REPAIR" in render(pair_fail)):
        held("a fused batch repairs whole", "the failing proof replays the document -- "
             "the batch re-renders, the REPAIR heading never elided (and numbered: "
             "the replay is a multi-heading output): the repaired step's own position")
    else:
        failures.append(f"  ✗ fused repair                {pair_fail and pair_fail.repair}")

    (fus_made / "NOTE.md").write_text("a note between steps\n", encoding="utf-8")
    split_doc = fus_made / "SPLIT.md"
    split_doc.write_text(
        "---\nname: SPLIT\nkind: proc\ndescription: a reading between steps\nproc: |\n"
        "  INFER\n  SERVE NOTE.md\n  INFER\n  FINAL\n---\nsay two things\n",
        encoding="utf-8")
    fus_c().forget()
    split_text = render(fus_c().start(split_doc))
    if (split_text.count("▌ INSTRUCTION") == 2
            and "a note between steps" in split_text):
        held("a payload between steps keeps its section", "the served reading rides "
             "between the lines -- they never collapse across it")
    else:
        failures.append(f"  ✗ payload splits sections     "
                        f"{split_text.count('▌ INSTRUCTION')}")

    (fus_made / "CHILD.md").write_text(
        "---\nname: CHILD\nkind: proc\ndescription: adds a law\nconstraints.behavior: |\n"
        "  Q2  the child's own law\nproc: |\n  INFER\n---\nthe child speaks\n",
        encoding="utf-8")
    (fus_made / "PARENT.md").write_text(
        "---\nname: PARENT\nkind: proc\ndescription: crosses a scope\nconstraints.behavior: |\n"
        "  Q1  the parent's law\nproc: |\n  INFER\n  CALL CHILD.md\n  FINAL\n---\n"
        "speak then call\n", encoding="utf-8")
    fus_c().forget()
    crossed = fus_c().start(fus_made / "PARENT.md")
    crossed_text = render(crossed)
    if (crossed_text.count("the parent's law") == 1
            and crossed_text.count("the child's own law") == 1
            and "[Q1]" in crossed_text):
        held("a new scope stacks with its delta", "the child's law verbatim, the parent's "
             "already-said text held as a code -- verbatim once per output (D-d)")
    else:
        failures.append(f"  ✗ delta verbatim              "
                        f"p={crossed_text.count(chr(39) + 's law')} "
                        f"[Q1]={'[Q1]' in crossed_text}")

    # --- R7.9a les-coutures: the order closing dresses for what it carries -----------
    if (crossed_text.count("▌ [") == 2                 # two segment headings, one
            and crossed_text.count("▌ pp · ") == 1     # output heading above them
            and crossed_text.rstrip().splitlines()[-3] == "▶ FINAL ephemerals => response (PARENT · CHILD)"
            and "closes on its proof" not in crossed_text.rstrip().splitlines()[-1]):
        held("the closing after segments is bare", "two headings for two scopes, then the "
             "signal alone -- no habit, and the delivery order rides it: drafts stand")
    else:
        failures.append(f"  ✗ bare closing                heads="
                        f"{crossed_text.count('▌ [')} "
                        f"{crossed_text.rstrip().splitlines()[-3:]!r}")

    solo_doc = fus_made / "SOLO.md"
    solo_doc.write_text(
        "---\nname: SOLO\nkind: proc\ndescription: one step then the frontier\n"
        "proc: |\n  WORK\n  FINAL\n---\nsay it\n", encoding="utf-8")
    fus_c().forget()
    solo_text = render(fus_c().start(solo_doc))
    if ("WORK free => response" in solo_text
            and solo_text.rstrip().splitlines()[-3] == "▶ FINAL"
            and "▶ FINAL ephemerals" not in solo_text):
        held("adjacent to the frontier, said directly", "no draft stands: the production "
             "is the response and the FINAL closes bare -- nothing to deliver twice")
    else:
        failures.append(f"  ✗ solo response               "
                        f"{solo_text.rstrip().splitlines()[-2:]!r}")

    proved_turn = fus_made / "PASK.md"
    proved_turn.write_text(
        "---\nname: PASK\nkind: proc\ndescription: a proved cycle\ncycle: true\n"
        "constraints.production: |\n  Q7  answer plainly\nproc: |\n  WORK\n  FINAL\n---\n"
        "serve the ask\n", encoding="utf-8")
    fus_c().forget()
    fus_c().start(proved_turn)              # WORK batched + PROVE terminal, fused
    pask_proof = fus_c().submit('[{"code": "Q7", "evidence": "plain", "verdict": "ok"}]')
    pask_text = render(pask_proof)
    if (pask_proof.wait and "closes on its proof" in pask_text
            and pask_text.startswith("▌ pp ·") and "answer plainly" in pask_text):
        held("the FINAL says what the resume owes", "a PROVE lives in the coming "
             "turn -- announced on the closing; alone, the order block keeps its habit")
    else:
        failures.append(f"  ✗ FINAL foresees               "
                        f"{pask_text.rstrip().splitlines()[-1:]!r}")

    # the author's-guide and cheatsheet cases live with their documents, at their
    # package's tests/.
    # --- les-canaux-se-disent: the OUTPUT names form AND channel; excess is caught ---
    chan_env = bench.env("chanws")
    chan_env.write_member("output: table\n")       # the boot opens on a draft step: `table => ephemeral`
    chan_made = chan_env.made
    chan_engine = chan_made / ".sys" / "engine" / "pp.py"
    chan_member = discovery.instance_member(chan_engine)
    def chan_c():
        return Conductor(chan_member, chan_engine)
    chan_open = chan_c().start(chan_c().boot("BOOT.md"))
    caught = chan_c().submit("| a table | pasted into the tool |")
    after_catch = chan_c().submit("")
    if ("table => ephemeral" in render(chan_open)
            and "is not the tool's" in caught.deviation and caught.repair == 0
            and caught.instruction.repairs == 0
            and after_catch.document == "TURN"
            and "any => ephemeral" in render(after_catch)):
        held("the channel is rendered and guarded", "the line says `form => ephemeral`; "
             "a pasted draft bounces soft -- 0 repair -- and the bare call advances")
    else:
        failures.append(f"  ✗ channels                  {caught.deviation!r} r={caught.repair}")

    (chan_made / "procs" / "PIPE.md").write_text(
        "---\nname: JOIN\ndescription: takes json\ninput: json\nproc: |\n  HOOK joined\n"
        "---\nx\n", encoding="utf-8")
    (chan_made / "procs" / "FEEDER.md").write_text(
        "---\nname: FEEDER\nkind: proc\ndescription: feeds\noutput: json\nproc: |\n"
        "  INFER\n  CALL PIPE.md\n---\nfeed it\n", encoding="utf-8")
    fed_block = chan_c().start(chan_made / "procs" / "FEEDER.md")
    (chan_made / "procs" / "ELECT.md").write_text(
        "---\nname: ELECT\nkind: proc\ndescription: elects\noutput: json\nproc: |\n"
        "  INFER\n  PICK one\n---\nlist then pick\n", encoding="utf-8")
    elect_c = chan_c(); elect_c.forget()
    elect_block = elect_c.start(chan_made / "procs" / "ELECT.md")
    if ("json => tool (heredoc)" in render(fed_block)
            and "json => tool" in render(elect_block)
            and "<output>" in elect_block.next_call):
        held("consumed channels say their mode", "a CALL-fed json pipes heredoc; a PICK-fed "
             "json rides the tool -- the election consumes")
    else:
        failures.append(f"  ✗ consumed channels         {render(fed_block)[-80:]!r}")
    chan_c().forget()

    # --- tout-est-un-skill: declared harness names offered, the indifference invariant
    (ctx_member.meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\ntools: |\n  +NOTE\n  +brainstorm\n---\n", encoding="utf-8")
    ctx_conductor().submit("")            # the offer stands with the output that carries it
    ghost_block = ctx_conductor().peek()
    ghost_tool = next((one for one in ghost_block.tools if one.name == "brainstorm"), None)
    if (ghost_tool is not None and ghost_tool.description == ""
            and "brainstorm" in render(ghost_block)):
        held("a declared harness skill is offered", "+name suffices -- name-only in the block, scoped like any tool")
    else:
        failures.append(f"  ✗ declared offered            {ghost_tool}")

    oriented = cli(ctx_made / ".sys" / "engine" / "pp.py", "-s", "brainstorm")
    if oriented.returncode == 0 and "yours, through your harness" in oriented.stdout:
        held("a declared name orients", "pp has nothing to run -- the harness does; no usage wall, no REPAIR")
    else:
        failures.append(f"  ✗ declared dispatch           rc={oriented.returncode} "
                        f"{oriented.stdout[:120]!r}")

    before_copy = steady(render(ctx_conductor().peek()))
    catalog_before = compiling.render_tools(ctx_member.meta)
    harness_copy = ctx_member.path / ".claude" / "skills" / "turn"
    harness_copy.mkdir(parents=True, exist_ok=True)
    (harness_copy / "SKILL.md").write_text(
        next((ctx_made / ".sys" / "vendor").glob("kit@*/procs/TURN.md")).read_text(encoding="utf-8"),
        encoding="utf-8")
    if (steady(render(ctx_conductor().peek())) == before_copy
            and compiling.render_tools(ctx_member.meta) == catalog_before):
        held("the indifference invariant", "a proc registered at the harness changes NOTHING for pp -- byte-identical")
    else:
        failures.append("  ✗ indifference                the harness copy leaked into pp")

    # --- chaque-conversation-tient-son-run: multi_session, one run PER conversation ---
    many_env = bench.env("many")
    many_env.write_member()           # the boot opens on the member's brief: a run that moved is told apart
    many_made = many_env.made
    many_engine = many_made / ".sys" / "engine" / "pp.py"
    many_member = discovery.instance_member(many_engine)

    def many_c(run: str | None = None) -> Conductor:
        return Conductor(many_member, many_engine, run)

    many_c("a1b2c3")            # naming a key needs no setting: the mode is the mode

    (many_made / "SETTINGS.md").write_text(   # the RETIRED key left in an operator's
        "---\nname: SETTINGS\nkind: doc\nmulti_session: true\n"          # file is INERT;
        "max_harness_tool_output: 60000\n---\n", encoding="utf-8")   # the wide-budget bench rule holds
    first_conv = many_c("alpha")
    one_block = first_conv.start(first_conv.boot("BOOT.md"))
    second_conv = many_c("beta")
    two_block = second_conv.start(second_conv.boot("BOOT.md"))
    if (len(persistence.slots(many_member.meta)) == 2
            and one_block.next_call.endswith(" alpha") and two_block.next_call.endswith(" beta")
            and own_key in renewed.next_call):
        held("each conversation holds its key", "two runs stand side by side; the key rides every printed command, the re-newed run's included")
    else:
        failures.append(f"  ✗ run keys                    {one_block.next_call!r} / "
                        f"{two_block.next_call!r}")

    moved = many_c("alpha").submit("")
    still = many_c("beta").resume(many_c("beta").boot("BOOT.md"))
    if (moved is not None and moved.document == "TURN"
            and still is not None and still.document == "MEMBER"):
        held("interleaved runs stay independent", "alpha advanced to its turn; beta still stands where beta stood")
    else:
        failures.append(f"  ✗ interleaving                {moved and moved.document!r} / "
                        f"{still and still.document!r}")

    expect("run-ambiguous", lambda: many_c().submit("whose run is this"))
    try:
        many_c().submit("still no key")
    except Refusal as caught:
        told = str(caught)
        if "-new" in told and "alpha" not in told and "beta" not in told:
            held("the warning points at -new, never the ids",
                 "the conversation's id was handed at `-new`; the tool never enumerates the standing runs")
        else:
            failures.append(f"  ✗ ambiguous wording          {told!r}")

    alpha_trace = persistence.trace_of(persistence.slot_of(many_member.meta, "alpha"))
    beta_trace = persistence.trace_of(persistence.slot_of(many_member.meta, "beta"))
    alpha_kinds = [json.loads(line)["kind"] for line in
                   (many_member.meta / persistence.DIRECTORY / alpha_trace)
                   .read_text(encoding="utf-8").splitlines()]
    beta_kinds = [json.loads(line)["kind"] for line in
                  (many_member.meta / persistence.DIRECTORY / beta_trace)
                  .read_text(encoding="utf-8").splitlines()]
    if alpha_trace != beta_trace and "answer" in alpha_kinds and "answer" not in beta_kinds:
        held("each run writes its own trace", "alpha's answer lands in alpha's file alone")
    else:
        failures.append(f"  ✗ per-run traces              {alpha_trace!r}/{beta_trace!r} "
                        f"{beta_kinds}")

    third_conv = many_c()
    third = third_conv.start(third_conv.boot("BOOT.md"))
    minted = {persistence.run_id_of(one) for one in persistence.slots(many_member.meta)}
    if (len(minted) == 3 and {"alpha", "beta"} <= minted
            and re.search(r" [0-9a-f]{6}", third.next_call)):
        held("-new opens BESIDE the others", "a fresh short id is minted; nothing standing was discarded")
    else:
        failures.append(f"  ✗ new beside                  {sorted(minted)}")

    if many_c("beta").forget() == 1 and len(persistence.slots(many_member.meta)) == 2 \
            and many_c().forget() == 2 and not persistence.slots(many_member.meta):
        held("reset is named or total", "`-run beta` drops one; bare, every run -- counted")
    else:
        failures.append(f"  ✗ reset                       {persistence.slots(many_member.meta)}")
    return 0
