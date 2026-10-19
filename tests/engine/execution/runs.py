"""Scenario `runs` -- the run's life and its trace:
- an untouched `-new` is the LLM's mode, to the byte: two throwaways, one without the
  principal's variable and one under `false`, print the same lines (the key and the root
  apart), no mode at the slot nor on the `new` line, no door heading
- the first output says its key in its heading
- `-new` on a run's own key reopens THAT run fresh
- the trace: one file per run, append-only, every event stamped; the repeated call reads in
  it; a re-new closes the old file on `reset` and opens a new one, never touched again;
  reset, refusal and renewal each land in the run's own file
- a message at the frontier is traced `prompt`; a message opens a run (`new`, `prompt`,
  then the block); the reprise takes the message at any setting; a stray text off the
  frontier bounces, nothing traced
- peek is dry; the keyless call never mutates, a stale key refuses `run-unknown`
- one run per conversation: each holds its key, interleaved runs stay independent, a
  keyless advance among several refuses `run-ambiguous` and points at `-new`, never the
  ids; each run writes its own trace; `-new` opens beside the others; reset is named or total
- the boot's weight: the run weighs honestly (no part counted twice, the frame never
  negative); the serve budget never brakes the boot
"""
from __future__ import annotations

import json
import re

from conductor import Conductor, Refusal, render, persistence
from conductor import install as install_module, instance
from tests.harness import cli, document, session_of, support

run = support(__file__, "run")

DAILY = "---\nname: DAILY\nkind: proc\ndescription: a door\nproc: |\n  WORK\n---\nsay the day\n"
ASK = ("---\nname: ASK\ncycle: true\nconstraints.behavior: |\n  Z9  say it plainly\n"
       "proc: |\n  INFER\n  FINAL\n---\nwhat would you do?\n")
REFERENCE = ("---\nname: REF\nkind: doc\ndescription: a long reference\n---\n\n"
             + ("all work and no play makes a dull reference line\n" * 36)
             + "\nTHE-VERY-END\n")


def lines_of(path) -> list[dict]:
    """-> every event of a trace file, in order; [] when the file is absent."""
    if path is None or not path.is_file():
        return []
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- an untouched -new is the LLM's mode, to the byte ---------------------------------------
    plain, falsy = bench.env("runs-plain"), bench.env("runs-false")
    for one in (plain, falsy):
        one.write("procs/DAILY.md", DAILY)     # a door stands ready; nobody names it
    key_plain, first = run.opened(plain)
    key_false, second = run.opened(falsy, False, None, {run.VARIABLE: "false"})
    lines = [out.stdout.replace(key or "?", "KEY").replace(str(env.root), "WS").splitlines()[1:]
             for out, key, env in ((first, key_plain, plain), (second, key_false, falsy))]
    said = [("conducted_by" in run.slot(env, key))
            or any("conducted_by" in one for one in run.trace(env, key) if one.get("kind") == "new")
            for env, key in ((plain, key_plain), (falsy, key_false))]
    doored = [re.search(r"▸ DAILY", out.stdout) or "door" in run.kinds(env, key)
              for out, env, key in ((first, plain, key_plain), (second, falsy, key_false))]
    if (first.returncode == 0 and second.returncode == 0 and lines[0] and lines[0] == lines[1]
            and not any(said) and not any(doored)):
        held("(a) the LLM's mode is today's", f"{len(lines[0])} lines identical without the variable "
             "and under `false`; no mode at the slot nor on the `new` line, no door heading")
    else:
        drift = next((i for i, (a, b) in enumerate(zip(*lines)) if a != b), None)
        failures.append(f"  ✗ (a) the LLM's mode            rc={first.returncode}/{second.returncode} "
                        f"drift={drift} said={said} doored={doored} {second.stderr[-200:]!r}")

    text = first.stdout
    if (first.returncode == 0 and text.startswith("▌ pp · run ")
            and len(key_plain) == 6 and f"./pp {key_plain}" in text):
        held("the first output says its key", "`pp · run <key> · ...` opens the boot -- "
             "the head sits inside a harness preview, the closing outside")
    else:
        failures.append(f"  ✗ key in the head             {text.splitlines()[:1]!r}")

    # --- -new on a run's own key reopens THAT run fresh ------------------------------------------
    env = bench.env("runs")
    env.write_member()                 # the boot opens on the member's brief, the turn one call later
    member, engine = env.member, env.engine

    run.conductor_of(env).resume(run.conductor_of(env).boot("BOOT.md"))      # -> MEMBER
    run.conductor_of(env).submit("")                                          # -> the turn
    resumed_again = run.conductor_of(env).resume(run.conductor_of(env).boot("BOOT.md"))
    own_key = persistence.run_id_of(persistence.slots(member.meta)[0])
    renew_c = Conductor(member, engine, own_key)
    renewed = renew_c.start(renew_c.boot("BOOT.md"))
    if (resumed_again is not None and resumed_again.document == "TURN"
            and renewed is not None and renewed.document == "MEMBER"
            and len(persistence.slots(member.meta)) == 1):
        held("re-new reopens the conversation's own run",
             "resume() keeps returning where the turn left off; start() on the run's key discards IT alone and reboots")
    else:
        failures.append(f"  ✗ new                        resumed={resumed_again and resumed_again.command!r} "
                        f"renewed={renewed and renewed.command!r}")

    # --- the trace: the sequence above IS the chronology -- resume (new, block), submit
    #     (answer, the turn's block), resume again (the block repeated), re-new on the key
    #     (the first file closes on `reset`, a new file opens)
    trace_dir = member.meta / persistence.DIRECTORY
    second_name = persistence.trace_of(session_of(member.meta))
    second_trace = trace_dir / second_name if second_name else None
    second_events = lines_of(second_trace)
    older = sorted(one.name for one in trace_dir.glob("session-*.jsonl") if one.name != second_name)
    first_trace = trace_dir / older[0] if older else None
    first_events = lines_of(first_trace)
    first_kinds = [one["kind"] for one in first_events]
    if (first_kinds and first_kinds[0] == "new" and "answer" in first_kinds
            and "block" in first_kinds and all("at" in one for one in first_events)):
        held("a run writes its own trace", "session-<UTC>.jsonl: new first, every event stamped, parseable")
    else:
        failures.append(f"  ✗ trace chronology           {first_kinds}")

    if (first_kinds[-1:] == ["reset"] and first_kinds[-3:-1] == ["block", "block"]
            and first_events[-2].get("command") == first_events[-3].get("command")):
        held("the repeated call reads in the trace", "two identical blocks, no answer between -- the drift is visible")
    else:
        failures.append(f"  ✗ double call in trace       {first_kinds[-3:]}")

    if (second_trace is not None and first_trace is not None
            and second_trace.name != first_trace.name and second_events
            and second_events[0]["kind"] == "new" and first_kinds[-1:] == ["reset"]):
        held("a new run opens a new file", "the discarded one closes on `reset` IN ITS OWN trace -- the chain reads per file")
    else:
        failures.append(f"  ✗ one file per run           {older!r} / {second_name!r}")

    closed = first_trace.read_bytes() if first_trace else b""
    run.conductor_of(env).submit("capability table")      # the second run works on -- ITS file only
    if first_trace and first_trace.read_bytes() == closed:
        held("a closed trace never moves again", "the second run's work lands in its own file, the first byte-identical")
    else:
        failures.append("  ✗ closed trace mutated")

    run.conductor_of(env).forget()
    reset_event = lines_of(second_trace)[-1]
    noted_c = run.conductor_of(env)
    noted_c.resume(noted_c.boot("BOOT.md"))                # a third run: the second was forgotten
    noted_c.noted(Refusal("probe-refusal", "lands in the trace"))
    third_trace = trace_dir / persistence.trace_of(session_of(member.meta))
    refusal_event = lines_of(third_trace)[-1]
    install_module.sync(member)                # constant pins: the run stands, nothing written
    kept_event = lines_of(third_trace)[-1]
    moved = instance.read(member.meta)
    moved["packages"] = {**instance.pins(member.meta), "kit": "0.0.1-past"}
    instance.write(member.meta, moved)
    install_module.upgrade(member)             # a version moves: the run is renewed, the trace says so
    sync_event = lines_of(third_trace)[-1]
    if (reset_event["kind"] == "reset"
            and refusal_event["kind"] == "refusal" and refusal_event["code"] == "probe-refusal"
            and kept_event["kind"] == "refusal" and sync_event["kind"] == "renewed"):
        held("reset, refusal and renewal say so", "each lands in the RUN'S file -- a sync at "
             "constant pins writes none of it, the upgrade that renews the run does")
    else:
        failures.append(f"  ✗ lifecycle events           {reset_event['kind']} / "
                        f"{refusal_event.get('kind')} / {sync_event['kind']}")

    # --- peek is dry: the block that stands, state and trace byte-identical ---------------------
    Conductor(member, engine).forget()
    run.conductor_of(env).resume(run.conductor_of(env).boot("BOOT.md"))      # -> MEMBER
    run.conductor_of(env).submit("")                                          # -> TURN stands
    slot_path = session_of(member.meta)
    log_path = slot_path.parent / persistence.trace_of(slot_path)
    frozen_state, frozen_trace = slot_path.read_bytes(), log_path.read_bytes()
    peeked = run.conductor_of(env).peek()
    offers = [one.name for one in (peeked.tools if peeked else ())]
    if (peeked is not None and peeked.document == "TURN"
            and "pp-elsewhere" not in offers and "ELSEWHERE" not in offers
            and slot_path.read_bytes() == frozen_state and log_path.read_bytes() == frozen_trace):
        held("peek is dry", "the block that STANDS -- nothing offered on the naked turn, state "
             "and trace byte-identical")
    else:
        failures.append(f"  ✗ peek                        {peeked and peeked.document} {offers}")

    # --- keyless never mutates; the key is the consent to advance -------------------------------
    looked = cli(engine)
    stale = cli(engine, "abc123")
    if (looked.returncode == 0 and "▌ pp ·" in looked.stdout
            and slot_path.read_bytes() == frozen_state
            and stale.returncode == 2 and "run-unknown" in stale.stderr):
        held("keyless never mutates", "the bare call shows and leaves the state "
             "byte-identical; a stale key refuses named")
    else:
        failures.append(f"  ✗ keyless inspection          rc={looked.returncode}/"
                        f"{stale.returncode} {stale.stderr[:80]!r}")

    # --- the message at the frontier: traced `prompt` ---------------------------------------------
    asked = document(ASK)
    run.conductor_of(env).start(asked)
    run.conductor_of(env).submit("the operator said X")      # the cycle reopens on the message
    if any(one["kind"] == "prompt" and one.get("text") == "the operator said X"
           for one in run.trace(env, "t")):
        held("the message lands in the trace", "the text handed at the frontier is traced `prompt` -- the session log")
    else:
        failures.append(f"  ✗ captured prompt            {run.kinds(env, 't')}")

    # --- a message OPENS a run: `prompt` after `new`, before the first block --------------------
    opened_block = run.conductor_of(env).start(asked, "the trigger said Y")
    opened_events = run.trace(env, "t")
    opened_kinds = [one["kind"] for one in opened_events]
    if (opened_block is not None and opened_block.document == asked.stem and opened_block.wait
            and opened_kinds[:2] == ["new", "prompt"]
            and opened_events[1].get("text") == "the trigger said Y"
            and "block" in opened_kinds):
        held("a message opens a run", "start(ASK, text): the trace says new, prompt, then block -- "
             "the message is a line of the trace, the first block comes after it")
    else:
        failures.append(f"  ✗ message at -new            {opened_kinds[:4]} "
                        f"{opened_block and opened_block.document!r}")
    run.conductor_of(env).forget()

    # --- the reprise takes the message at ANY setting: the FINAL is bare, the text at the
    #     frontier is the principal's word
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nconduction_effort: none\n"
                             "max_harness_tool_output: 60000\nwork_repairs_allowed: 1\n---\n")
    bare_block = run.conductor_of(env).start(asked)
    bare_second = run.conductor_of(env).submit("the operator said X again")
    prompted = [one for one in run.trace(env, "t") if one["kind"] == "prompt"]
    if (bare_block is not None and bare_block.wait
            and bare_second is not None and bare_second.document == asked.stem and bare_second.wait
            and prompted and prompted[-1].get("text") == "the operator said X again"):
        held("the reprise takes the message at any setting",
             "the FINAL closes bare, the text handed at the frontier is traced `prompt` and "
             "the floor replays -- the position decides")
    else:
        failures.append(f"  ✗ reprise                    {bare_block and bare_block.next_call!r} "
                        f"{bare_second and bare_second.document!r} "
                        f"{[one.get('text') for one in prompted]}")
    run.conductor_of(env).forget()

    # --- off the frontier, a text handed to a step that awaits nothing is a STRAY ---------------
    env.write("NOTE.md", "a note between steps\n")
    mid = env.write("MID.md", "---\nname: MID\nproc: |\n  INFER\n  SERVE NOTE.md\n  INFER\n---\n"
                              "say two things\n")
    mid_first = run.conductor_of(env).start(mid)
    strayed = run.conductor_of(env).submit("a stray production")
    stray_kinds = run.kinds(env, "t")
    if (mid_first is not None and not mid_first.wait
            and strayed is not None and (strayed.deviation or "").strip()
            and strayed.repair == 0 and "prompt" not in stray_kinds):
        held("a stray text off the frontier bounces", "a step that awaits nothing, no FINAL "
             "just closed: a DEVIATION, 0 repair, no `prompt` in the trace")
    else:
        failures.append(f"  ✗ stray off the frontier     {strayed and strayed.deviation!r} "
                        f"{stray_kinds}")
    run.conductor_of(env).forget()

    # --- one run PER conversation: the key is the conversation's ----------------------------------
    many = falsy
    many.write_member()                # the boot opens on the member's brief: a run that moved is told apart
    Conductor(many.member, many.engine).forget()     # the -new above leaves no run standing

    def many_c(key: str | None = None) -> Conductor:
        return Conductor(many.member, many.engine, key)

    many_c("a1b2c3")                   # naming a key needs no setting: the mode is the mode
    many.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 60000\n---\n")
    first_conv = many_c("alpha")
    one_block = first_conv.start(first_conv.boot("BOOT.md"))
    second_conv = many_c("beta")
    two_block = second_conv.start(second_conv.boot("BOOT.md"))
    if (len(persistence.slots(many.made)) == 2
            and one_block.next_call.endswith(" alpha") and two_block.next_call.endswith(" beta")
            and own_key in renewed.next_call):
        held("each conversation holds its key", "two runs stand side by side; the key rides every "
             "printed command, the re-newed run's included")
    else:
        failures.append(f"  ✗ run keys                    {one_block.next_call!r} / "
                        f"{two_block.next_call!r}")

    moved_on = many_c("alpha").submit("")
    still = many_c("beta").resume(many_c("beta").boot("BOOT.md"))
    if (moved_on is not None and moved_on.document == "TURN"
            and still is not None and still.document == "MEMBER"):
        held("interleaved runs stay independent", "alpha advanced to its turn; beta still stands where beta stood")
    else:
        failures.append(f"  ✗ interleaving                {moved_on and moved_on.document!r} / "
                        f"{still and still.document!r}")

    expect("run-ambiguous", lambda: many_c().submit("whose run is this"))
    try:
        many_c().submit("still no key")
        failures.append("  ✗ ambiguous                   a keyless advance among two runs did not refuse")
    except Refusal as caught:
        told = str(caught)
        if "-new" in told and "alpha" not in told and "beta" not in told:
            held("the warning points at -new, never the ids",
                 "the conversation's id was handed at `-new`; the tool never enumerates the standing runs")
        else:
            failures.append(f"  ✗ ambiguous wording          {told!r}")

    alpha_trace = persistence.trace_of(persistence.slot_of(many.made, "alpha"))
    beta_trace = persistence.trace_of(persistence.slot_of(many.made, "beta"))
    alpha_kinds, beta_kinds = run.kinds(many, "alpha"), run.kinds(many, "beta")
    if alpha_trace != beta_trace and "answer" in alpha_kinds and "answer" not in beta_kinds:
        held("each run writes its own trace", "alpha's answer lands in alpha's file alone")
    else:
        failures.append(f"  ✗ per-run traces              {alpha_trace!r}/{beta_trace!r} {beta_kinds}")

    third_conv = many_c()
    third = third_conv.start(third_conv.boot("BOOT.md"))
    minted = {persistence.run_id_of(one) for one in persistence.slots(many.made)}
    if (len(minted) == 3 and {"alpha", "beta"} <= minted
            and re.search(r" [0-9a-f]{6}", third.next_call)):
        held("-new opens BESIDE the others", "a fresh short id is minted; nothing standing was discarded")
    else:
        failures.append(f"  ✗ new beside                  {sorted(minted)}")

    if (many_c("beta").forget() == 1 and len(persistence.slots(many.made)) == 2
            and many_c().forget() == 2 and not persistence.slots(many.made)):
        held("reset is named or total", "`-run beta` drops one; bare, every run -- counted")
    else:
        failures.append(f"  ✗ reset                       {persistence.slots(many.made)}")

    # --- the boot's weight: the measure on a fused run, in process ------------------------------
    weigh_c = Conductor(plain.member, plain.engine, "w")
    weigh_c.start(weigh_c.boot("BOOT.md"))
    weigh_c.submit("a table said")
    served = weigh_c._served
    if served.get("blocks", 0) >= 2 and served.get("frame", -1) >= 0 <= served.get("total", -1):
        held("the run weighs honestly", f"{served['blocks']} blocks, total "
             f"{served['total']} chars, frame {served['frame']} -- never negative: coded "
             "constraints weigh their codes, a fused segment weighs once")
    else:
        failures.append(f"  ✗ honest weigh                 {served!r}")

    # --- the boot's payloads ride OUTSIDE the serve budget ------------------------------------------
    lean = bench.env("runs-lean", bare=True)    # no standing orders
    for one in (plain, lean):
        one.write("REF.md", REFERENCE)
        one.write_member("serve: |\n  reference: REF.md\n", body="the member", proc="SERVE\n  INFER")
    cli(plain.engine, "-reset")
    lean_boot = cli(lean.engine, "-new").stdout
    full_boot = cli(plain.engine, "-new").stdout
    if "THE-VERY-END" in lean_boot and "THE-VERY-END" in full_boot:
        held("the budget never brakes the boot", "the same reading arrives whole with and "
             "without the standing orders aboard -- the serve budget models the harness's "
             "inline limit for the serve mechanism, not the boot's weight")
    else:
        failures.append(f"  ✗ boot unbraked                lean={'THE-VERY-END' in lean_boot} "
                        f"full={'THE-VERY-END' in full_boot}")
    return 0
