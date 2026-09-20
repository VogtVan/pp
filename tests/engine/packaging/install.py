"""Scenario `install` -- 3 case(s), in the monolith's order:
- M2 end to end: the product INSTALLS an instance; the boot plays off it
- OVERLAY: a same-name document in a nearer space carries DELTAS, never a shadow
- SYNC: the update path -- bundles are machine-owned, the DATA is untouchable

The ADMIN's verb left with its policy (batch l-administration-du-package): the
coordination is a SETTING of the federation package, read by its own skill.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from conductor import Conductor, Frame, Procedure, render, revive, compiling, discovery, instance, persistence, reading
from tests.harness import PLAYABLE, document, pin_step, session_of, PRODUCT_ENGINE, SOURCE, body_of, kept_document, reaches
from tests.harness import quiet_improve as _quiet_improve
import pp as pp_cli



def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    playable = document(PLAYABLE)
    # --- M2 end to end: the product INSTALLS an instance; the boot plays off it --------
    from conductor import install as install_module                       # noqa: PLC0415
    product_engine = PRODUCT_ENGINE
    town = Path(tempfile.mkdtemp())          # a BARE directory: no git anywhere
    alpha = town / "alpha"
    made = install_module.install(product_engine, alpha / ".pp", [])
    pin_step(made)
    _quiet_improve(made)   # the closing fixtures here are not about the reflex

    expect("instance-exists", lambda: install_module.install(product_engine, alpha / ".pp", []))
    installed_engine = made / ".sys" / "engine" / "pp.py"
    booted = discovery.instance_member(installed_engine)
    if booted and booted.meta_name == ".pp" and booted.path == alpha:
        held("an installed engine knows home", "the instance dir's NAME is a parameter -- `.pp` here")
    else:
        failures.append(f"  ✗ instance discovery        {booted}")

    doors = [(alpha / name).read_text(encoding="utf-8") if (alpha / name).is_file() else ""
             for name in ("CLAUDE.md", "AGENTS.md")]
    if all("`pp` skill" in door for door in doors):
        held("the doors are written", "CLAUDE.md and AGENTS.md at the member root point the conductor")
    else:
        failures.append(f"  ✗ doors                     {[d[:40] for d in doors]}")

    if not (alpha / ".claude").exists():
        held("the install is harness-agnostic", "no harness config written -- the README instructs")
    else:
        failures.append("  ✗ install wrote harness config (.claude/) -- portability broken")

    def fresh() -> Conductor:
        return Conductor(booted, discovery.siblings_around(booted), installed_engine, "t")

    starter = fresh()
    opening = starter.resume(starter.boot("BOOT.md"))
    for _ in range(6):             # a long boot reading rides CONTINUEs first --
        if opening.command:        # land on the step block, wherever the budget cut
            break
        opening = fresh().resume(fresh().boot("BOOT.md"))
    if (opening and opening.instruction.keyword == "INFER" and not opening.options
            and opening.output == "table" and "./pp" in opening.next_call):
        held("the installed boot never PICKs", "0 scan, 0 choice -- identity is the slug, not an interaction")
    else:
        failures.append(f"  ✗ installed boot            {opening and (opening.instruction, opening.options)}")

    m1 = next((c for c in opening.constraints if c.code == "M1"), None)
    m2 = next((c for c in opening.constraints if c.code == "M2"), None)
    if (m1 and m1.text == "your name is AGENT"
            and m2 and m2.text == "you must behave like this: cooperative, honest, helpful, and respectful"):
        held("tags resolve on a vanilla instance",
             "M1 and M2 both live by default, both resolved -- no `@...` literal")
    else:
        failures.append(f"  ✗ default M1/M2 tags         {m1} / {m2}")

    kit_caps_text = next((made / ".sys" / "vendor").glob("kit@*/procs/CAPABILITIES.md")).read_text(encoding="utf-8")
    c1 = next((c for c in opening.constraints if c.code == "C1"), None)
    if c1 and c1.text in kit_caps_text:
        held("an instruction migrates out of the body", "CAPABILITIES' presentation rule is a constraint now, not a sentence in prose")
    else:
        failures.append(f"  ✗ CAPABILITIES C1            {c1}")

    c2 = next((c for c in opening.constraints if c.code == "C2"), None)
    c3 = next((c for c in opening.constraints if c.code == "C3"), None)
    if c2 and c2.text in kit_caps_text and c3 and c3.text in kit_caps_text:
        held("CAPABILITIES sheds its remaining instructions", "the body is a fact now; C1-C3 carry what it used to instruct")
    else:
        failures.append(f"  ✗ CAPABILITIES C2/C3         {c2} / {c3}")

    if (opening.next_call and opening.next_call.rstrip().endswith(" t")
            and "<" not in opening.next_call):
        held("an INFER's NEXT_CALL asks for nothing but the keyed call",
             "pp never needs the agent's own output back -- CAPTURE_PROMPT is off by default")
    else:
        failures.append(f"  ✗ next_call                  {opening.next_call!r}")

    rendered = render(opening)
    idx_constraints = rendered.index("▌ CONSTRAINTS")
    idx_instruction = rendered.index("▌ INSTRUCTION")
    idx_last_payload = max(rendered.rfind("▌ INFORMATION —"),
                           rendered.rfind("▌ NEXT INSTRUCTION CONTEXT —"))
    if idx_last_payload < idx_constraints < idx_instruction:
        held("constraints sit next to the instruction", "not stranded before a wall of PAYLOAD -- rule and ask share a screen")
    else:
        failures.append(f"  ✗ render order                payload={idx_last_payload} "
                        f"constraints={idx_constraints} instruction={idx_instruction}")

    probe = fresh()
    probe._payloads = [("X", "the current document's own body -- served FIRST, in raw order"),
                        ("EARLIER", "context read after X, in raw order -- not really earlier")]
    reordered = probe._own_last(Frame(document=reading.read(playable), procedure=Procedure()))
    if [title for title, _ in reordered] == ["EARLIER", "X"]:
        held("an INFER's own document rides last", "whatever else was read moves ahead of it -- the freshest reading sits right before the ask")
    else:
        failures.append(f"  ✗ own_last                   {[t for t, _ in reordered]}")

    advance_made = bench.env("advance_probe").made
    _quiet_improve(advance_made)   # the closing fixtures here are not about the reflex
    (advance_made / "MEMBER.md").write_text(   # a vanilla member carries no production law
        (advance_made / "MEMBER.md").read_text(encoding="utf-8")   # (identity is behavior):
        .replace("constraints.behavior: |", "constraints.production: |\n  Z1  the turn's work is proven.\n"
                 "constraints.behavior: |", 1), encoding="utf-8")   # the checkpoint needs one

    advance_engine = advance_made / ".sys" / "engine" / "pp.py"
    advance_member = discovery.instance_member(advance_engine)

    def advance_conductor() -> Conductor:
        return Conductor(advance_member, discovery.siblings_around(advance_member), advance_engine, "t")

    first = advance_conductor().resume(advance_conductor().boot("BOOT.md"))    # -> CAPABILITIES
    checked = advance_conductor().resume(advance_conductor().boot("BOOT.md"))  # bare -- must NOT move
    if (first is not None and first.document == "CAPABILITIES"
            and checked is not None and checked.document == "CAPABILITIES"
            and checked.position == first.position and checked.command == first.command):
        held("resume() alone never advances", "a pure status check -- safe to call as many times as asked")
    else:
        failures.append(f"  ✗ resume is idempotent       first={first and first.position} "
                        f"checked={checked and checked.position}")

    answered = advance_conductor().submit("")     # the bare `answer` CAPABILITIES' NEXT_CALL asks for
    if (answered is not None and answered.document == "TURN"
            and str(answered.command).startswith("WORK") and not answered.wait):
        held("the kit turn is proven under a production law",
             "the turn's own WORK cedes -- the checkpoint waits at the frontier")
    else:
        failures.append(f"  ✗ default proven turn        {answered and answered.command!r} / "
                        f"wait={answered and answered.wait} / {answered and answered.next_call!r}")

    kit_prove = advance_conductor().submit("")    # the production said; the checkpoint gates
    kit_proof = json.dumps([{"code": one.code, "evidence": "held", "verdict": "ok"}
                            for one in kit_prove.constraints])
    kit_wait = advance_conductor().submit(kit_proof)   # proof ok; FINAL rides
    if (kit_prove.output == "proof"
            and kit_wait is not None and kit_wait.wait and not kit_wait.command
            and kit_wait.document == "TURN"):
        held("the exchange closes on FINAL",
             "the checkpoint gates, the frontier rides the proof")
    else:
        failures.append(f"  ✗ kit proven closing         {kit_prove and kit_prove.output!r} / "
                        f"{kit_wait and kit_wait.command!r}")

    next_exchange = advance_conductor().resume(advance_conductor().boot("BOOT.md"))
    if (next_exchange is not None and next_exchange.document == "TURN"
            and next_exchange.instruction.keyword == "WORK" and not next_exchange.wait
            and next_exchange.position == answered.position):
        held("the next operator message finds a fresh proven cession",
             "resume rewinds the cycle then re-cedes -- every real message lands here directly")
    else:
        failures.append(f"  ✗ next exchange               {next_exchange and next_exchange.command!r}")

    rendered_wait = render(kit_wait)
    if ("FINAL" in rendered_wait and "NEXT_CALL" not in rendered_wait
            and "(once the operator replies -- the turn closes on its proof)"
            in rendered_wait):
        held("FINAL renders in place of NEXT_CALL", "the label says when to call -- and "
             "what the resumed turn will owe: the kit TURN closes on its proof")
    else:
        failures.append(f"  ✗ FINAL render                {rendered_wait!r}")

    kit_boot = next((made / ".sys" / "vendor").glob("kit@*/procs/BOOT.md")).read_text(encoding="utf-8")
    kit_card = next((made / ".sys" / "vendor").glob("kit@*/refs/PP.md")).read_text(encoding="utf-8")
    kit_capabilities = next((made / ".sys" / "vendor").glob("kit@*/procs/CAPABILITIES.md")).read_text(encoding="utf-8")
    if (reading.body_of(kit_boot).strip() == ""
            and kit_card == kept_document(SOURCE / "kit", "PP").read_text(encoding="utf-8")
            and "Deliver it in chat AS THE TABLE" not in kit_capabilities):
        held("the protocol lives in ONE place", "BOOT's body is empty; PP.md carries the card, served at boot")
    else:
        failures.append("  ✗ body/constraint split      the tacit mirror survives")

    if opening.output == "table":
        held("INFER takes its form from the document", "`output:` names the enumeration member")
    else:
        failures.append(f"  ✗ INFER output              {opening.output!r}")

    cycling = fresh().submit("")
    walker = fresh().submit("")                # close the lap, step-shape agnostic
    for _ in range(8):
        if walker is None or walker.wait:
            break
        if walker.document == "IMPROVE":
            walker = fresh().submit("none")
        elif (walker.instruction is not None
              and walker.instruction.keyword == "PROVE"):
            walker = fresh().submit(json.dumps(
                [{"code": one.code, "evidence": "held", "verdict": "ok"}
                 for one in walker.constraints]))
        else:
            walker = fresh().submit("")
    cycled_again = fresh().resume(fresh().boot(pp_cli.BOOT))   # the NOMINAL next exchange:
    # after the FINAL the frame is exhausted -- a bare call rewinds and re-cedes
    if (cycling and cycling.document == "TURN"
            and cycling.instruction.keyword == "WORK"
            and cycled_again and cycled_again.document == "TURN"
            and cycled_again.instruction.keyword == "WORK"
            and not cycled_again.end):
        held("TURN cycles", "each exchange proven then closed on FINAL -- the next bare call re-cedes, never END")
    else:
        failures.append(f"  ✗ TURN cycle                 {cycling and cycling.command!r} / "
                        f"{cycled_again and cycled_again.command!r}")

    _, town_stack, _, _, _, _, _, _ = persistence.restore(session_of(booted.meta), revive)
    town_floor = town_stack.frames[0].procedure.instructions
    if (cycled_again is not None and not any(s.injected for s in town_floor)
            and not (booted.meta / ".sys" / "records").exists()):
        held("install→boot end to end", "the kit played and ships no seed: no record "
             "materializes; boot.ready stands open -- no shipped client attaches")
    else:
        failures.append(f"  ✗ end to end                {cycled_again and cycled_again.command!r} / "
                        f"{[str(s) for s in town_floor]}")

    # --- OVERLAY: a same-name document in a nearer space carries DELTAS, never a shadow
    kit_turn = next((made / ".sys" / "vendor").glob("kit@*/procs/TURN.md"))
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  +X9  overlays add.\n  -T2\ntools: |\n  +CAPABILITIES\n---\n",
        encoding="utf-8")
    laws, tool_kit = compiling.effective(booted.meta, reading.read(kit_turn))
    if ([one.code for one in laws] == ["T1", "T3", "T4", "X9"]
            and [one.name for one in tool_kit] == ["CAPABILITIES"]
            and tool_kit[-1].contract.endswith("CAPABILITIES.md")):
        held("an overlay merges its deltas", "+X9 lands, -T2 leaves, +CAPABILITIES joins the bare TURN")
    else:
        failures.append(f"  ✗ overlay merge             {[one.code for one in laws]} / {tool_kit}")

    if instance.resolve(booted.meta, "TURN.md") == kit_turn:
        held("the base still executes", "the overlay never shadows -- resolution stays on the bundle")
    else:
        failures.append(f"  ✗ overlay shadowed          {instance.resolve(booted.meta, 'TURN.md')}")

    starter.forget()
    replay = fresh()
    landed = replay.resume(replay.boot("BOOT.md"))
    for _ in range(6):             # ride the boot reading's CONTINUEs to the step
        if landed and landed.command:
            break
        landed = fresh().resume(fresh().boot("BOOT.md"))
    replay2 = fresh().submit("")
    if (replay2 is not None and replay2.document == "TURN"
            and replay2.instruction.keyword == "WORK"):
        held("the overlaid boot still plays", "merged sections in force, the bundle's proc intact -- the turn still cedes")
    else:
        failures.append(f"  ✗ overlaid boot             {replay2 and replay2.command!r}")

    # a silent no-op delta is a lie -- and flow never extends by shadowing a proc
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  +T1  doubled.\n---\n", encoding="utf-8")
    expect("overlay-adds-existing",
           lambda: compiling.effective(booted.meta, reading.read(kit_turn)))
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -ZZ\n---\n", encoding="utf-8")
    expect("overlay-removes-nothing",
           lambda: compiling.effective(booted.meta, reading.read(kit_turn)))
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nproc: |\n  HOOK mine\n---\n", encoding="utf-8")
    expect("overlay-carries-proc",
           lambda: compiling.effective(booted.meta, reading.read(kit_turn)))
    (made / "procs" / "TURN.md").unlink()

    # the HOOK channel: a pending block renders for injection; a finished run is silence
    hooked_c = fresh()
    hooked_c.forget()
    pending = hooked_c.resume(hooked_c.boot("BOOT.md"))
    if pending and pending.next_call and render(pending).startswith("▌ pp ·"):
        held("the hook has something to say", "a pending block renders for injection")
    else:
        failures.append("  ✗ hook pending              nothing rendered")
    hooked_c.forget()

    # --- SYNC: the update path -- bundles are machine-owned, the DATA is untouchable ----
    (booted.meta / "procs" / "MINE.md").write_text(
        "---\nname: MINE\nkind: proc\nproc: |\n  HOOK mine\n---\nmy own\n",
        encoding="utf-8")
    (booted.meta / ".sys" / "records").mkdir(parents=True, exist_ok=True)
    (booted.meta / ".sys" / "records" / "notes.jsonl").write_text(
        '{"at": "2026-08-26T00:00:00", "entry": "the instance\'s own line"}\n', encoding="utf-8")
    kept_record = (booted.meta / ".sys" / "records" / "notes.jsonl").read_text(encoding="utf-8")
    kept_member = (booted.meta / "MEMBER.md").read_text(encoding="utf-8")
    vendored_boot = next((booted.meta / ".sys" / "vendor").glob("kit@*/procs/BOOT.md"))
    vendored_boot.write_text("tampered\n", encoding="utf-8")     # a bundle edit must not survive
    (booted.meta / ".sys" / "vendor" / "ghost@0.0.1").mkdir()              # nothing pins it: litter
    stale_session = session_of(booted.meta)
    stale_session.parent.mkdir(parents=True, exist_ok=True)
    stale_session.write_text("{}", encoding="utf-8")   # a run saved before the update
    made = install_module.sync(booted)
    survived = next((booted.meta / ".sys" / "vendor").glob("kit@*/procs/BOOT.md")).read_text(encoding="utf-8")
    if (made and "tampered" not in survived
            and (booted.meta / ".sys" / "records" / "notes.jsonl").read_text(encoding="utf-8") == kept_record
            and (booted.meta / "MEMBER.md").read_text(encoding="utf-8") == kept_member
            and (booted.meta / "procs" / "MINE.md").is_file()
            and not (booted.meta / ".sys" / "vendor" / "ghost@0.0.1").exists()
            and stale_session.exists()):
        held("sync updates, never touches", "bundles re-done, litter pruned, the standing "
             "session KEPT at constant pins, the data intact")
    else:
        failures.append("  ✗ sync                      bundle/data boundary broken")

    # --- le-sync-juge-avant-d-oublier: a refused sync leaves the runs where they were ------
    # the witness (S4.08, 2026-08-26): the slots were forgotten, then the composition refused
    (booted.meta / "procs" / "DEAD.md").write_text(
        "---\nname: DEAD\nkind: proc\noutput: nowhere\nproc: |\n  INFER\n---\nbody\n",
        encoding="utf-8")
    expect("reference-unknown", lambda: install_module.sync(booted))
    (booted.meta / "procs" / "DEAD.md").unlink()
    if stale_session.exists():
        held("a refused sync forgets nothing",
             "the composition is judged before any write: the slot stands, nothing played is true")
    else:
        failures.append("  ✗ refused sync forgot         the slot is gone")

    # a conductor cannot stand on missing bundles -- and the repair needs no conductor
    import shutil as _shutil
    _shutil.rmtree(booted.meta / ".sys" / "vendor")
    expect("package-missing", lambda: fresh().boot("BOOT.md"))
    install_module.sync(booted)
    if fresh() is not None:
        held("sync repairs a bare vendor", "the gesture stands on the member alone")
    else:
        failures.append("  ✗ sync did not restand the conductor")

    pinned = (booted.meta / instance.MANIFEST).read_text(encoding="utf-8")
    (booted.meta / instance.MANIFEST).write_text(pinned.replace("kit: ", "kit: 9.9.9 # ")
                                               if "kit: 9.9.9" not in pinned else pinned,
                                               encoding="utf-8")
    import re as _re
    (booted.meta / instance.MANIFEST).write_text(
        _re.sub(r"kit: \S+", "kit: 9.9.9", pinned), encoding="utf-8")
    expect("package-missing", lambda: install_module.sync(booted))
    (booted.meta / instance.MANIFEST).write_text(pinned, encoding="utf-8")

    return 0
