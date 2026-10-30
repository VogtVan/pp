"""Scenario `install` -- the install and its update path, on one house:
- the bench's source INSTALLS an instance: it knows home, writes its doors in the machine's
  console, no harness config; the boot plays off it -- the member's law and form on the first
  block, the turn's proven cession and its AWAIT, the cycle, the hook's pending block
- SYNC: the bundles are machine-owned and re-done, the DATA untouchable; a refused sync forgets
  nothing; a bare vendor is repaired; a pin the source does not carry refuses
"""
from __future__ import annotations

import json
import re
import shutil

from conductor import Conductor, Frame, Procedure, render, revive, discovery, instance, persistence, reading
from tests.harness import PLAYABLE, document, session_of, SOURCE, kept_document
import pp as pp_cli


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    playable = document(PLAYABLE)
    from conductor import install as install_module                       # noqa: PLC0415
    env = bench.env("alpha")                 # a BARE directory: no git anywhere
    alpha, made = env.root, env.made
    env.write_member("constraints.behavior: |\n  M1  the member's own law\noutput: table\n",
                     body="the member asks one table")   # a law on the first block, a form of its own

    expect("instance-exists", lambda: bench.install(alpha / ".pp", []))
    installed_engine = made / ".sys" / "engine" / "pp.py"
    booted = discovery.instance_member(installed_engine)
    if booted and booted.meta_name == ".pp" and booted.path == alpha:
        held("an installed engine knows home", "the instance dir's NAME is a parameter -- `.pp` here")
    else:
        failures.append(f"  ✗ instance discovery        {booted}")

    shell, call = install_module.door_call()
    names = ("CLAUDE.md", "AGENTS.md")
    doors = [(alpha / name).read_text(encoding="utf-8") if (alpha / name).is_file() else ""
             for name in names]
    if all(door == install_module.DOORS[name].format(shell=shell, console=call) and "skill" not in door
           for name, door in zip(names, doors)):
        held("the doors are written", "CLAUDE.md and AGENTS.md at the member root name the first call, "
             "no skill to invoke before it")
    else:
        failures.append(f"  ✗ doors                     {[d[:40] for d in doors]}")

    # the door names ONE call: the one that runs on the machine it was installed on
    here = f"```{shell}\n{call} -new\n```"
    other = ".\\pp" if call == "./pp" else "./pp"
    windows = install_module.DOOR.format(shell="powershell", console=".\\pp")
    if (all(here in door and f"{other} -new" not in door for door in doors)
            and ".\\pp -new" in windows and "./pp" not in windows):
        held("the door speaks the machine's console", f"{call} here, `.\\pp` under Windows -- "
             "both launchers are written, the door names the one that runs")
    else:
        failures.append(f"  ✗ door console              {call!r} {[d[-24:] for d in doors]}")

    if not (alpha / ".claude").exists():
        held("the install is harness-agnostic", "no harness config written -- the README instructs")
    else:
        failures.append("  ✗ install wrote harness config (.claude/) -- portability broken")

    def fresh() -> Conductor:
        return Conductor(booted, installed_engine, "t")

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
    if m1 and m1.text == "the member's own law":
        held("the member's law rides the first block",
             "M1 read from procs/MEMBER.md, in force on the boot's block as written")
    else:
        failures.append(f"  ✗ member law                 {m1}")

    if (opening.next_call and opening.next_call.rstrip().endswith(" t")
            and "<" not in opening.next_call):
        held("an INFER's NEXT_CALL asks for nothing but the keyed call",
             "pp never needs the agent's own output back -- CAPTURE_PROMPT is off by default")
    else:
        failures.append(f"  ✗ next_call                  {opening.next_call!r}")

    probe = fresh()
    probe._payloads = [("X", "the current document's own body -- served FIRST, in raw order"),
                        ("EARLIER", "context read after X, in raw order -- not really earlier")]
    reordered = probe._own_last(Frame(document=reading.read(playable), procedure=Procedure()))
    if [title for title, _ in reordered] == ["EARLIER", "X"]:
        held("an INFER's own document rides last", "whatever else was read moves ahead of it -- the freshest reading sits right before the ask")
    else:
        failures.append(f"  ✗ own_last                   {[t for t, _ in reordered]}")

    advance_made = bench.env("advance_probe").made
    (advance_made / "procs" / "TURN.md").write_text(   # the turn carries no production law of
        "---\nname: TURN\nconstraints.production: |\n  +Z1  the turn's work is proven.\n---\n",
        encoding="utf-8")                                # its own: an overlay arms the checkpoint

    advance_engine = advance_made / ".sys" / "engine" / "pp.py"
    advance_member = discovery.instance_member(advance_engine)

    def advance_conductor() -> Conductor:
        return Conductor(advance_member, advance_engine, "t")

    first = advance_conductor().resume(advance_conductor().boot("BOOT.md"))    # -> TURN's WORK
    checked = advance_conductor().resume(advance_conductor().boot("BOOT.md"))  # bare -- must NOT move
    if (first is not None and first.document == "TURN"
            and str(first.command).startswith("WORK") and not first.wait
            and checked is not None and checked.document == "TURN"
            and checked.position == first.position and checked.command == first.command):
        held("resume() alone never advances", "a pure status check -- safe to call as many times as asked;"
             " the turn's own WORK cedes, the checkpoint waits at the frontier")
    else:
        failures.append(f"  ✗ resume is idempotent       first={first and first.position} "
                        f"checked={checked and checked.position}")

    kit_prove = advance_conductor().submit("")    # the production said; the checkpoint gates
    kit_proof = json.dumps([{"code": one.code, "evidence": "held", "verdict": "ok"}
                            for one in kit_prove.constraints])
    kit_wait = advance_conductor().submit(kit_proof)   # proof ok; AWAIT rides
    if (kit_prove.output == "proof"
            and kit_wait is not None and kit_wait.wait and not kit_wait.command
            and kit_wait.document == "TURN"):
        held("the exchange closes on AWAIT",
             "the checkpoint gates, the frontier rides the proof")
    else:
        failures.append(f"  ✗ proven closing             {kit_prove and kit_prove.output!r} / "
                        f"{kit_wait and kit_wait.command!r}")

    next_exchange = advance_conductor().resume(advance_conductor().boot("BOOT.md"))
    if (next_exchange is not None and next_exchange.document == "TURN"
            and next_exchange.instruction.keyword == "WORK" and not next_exchange.wait
            and next_exchange.position == first.position):
        held("the next operator message finds a fresh proven cession",
             "resume rewinds the cycle then re-cedes -- every real message lands here directly")
    else:
        failures.append(f"  ✗ next exchange               {next_exchange and next_exchange.command!r}")

    rendered_wait = render(kit_wait)
    wait_lines = rendered_wait.splitlines()
    at = wait_lines.index(kit_wait.next_call) if kit_wait.next_call in wait_lines else -1
    if ("AWAIT" in rendered_wait and "NEXT_CALL" not in rendered_wait
            and at == len(wait_lines) - 1):
        held("AWAIT renders in place of NEXT_CALL", "the label says when to call, and nothing "
             "else: the command closes the output, the written PROVE before it asked its own proof")
    else:
        failures.append(f"  ✗ AWAIT render                {rendered_wait!r}")

    kit_boot = next((made / ".sys" / "vendor").glob("kit@*/procs/BOOT.md")).read_text(encoding="utf-8")
    kit_card = (made / ".sys" / "engine" / "refs" / "PP.COMMON.md").read_text(encoding="utf-8")
    if (reading.body_of(kit_boot).strip() == ""
            and kit_card == kept_document(SOURCE / "engine", "PP.COMMON").read_text(encoding="utf-8")):
        held("the protocol lives in ONE place", "BOOT's body is empty; PP.COMMON.md carries the card, served at boot")
    else:
        failures.append("  ✗ body/constraint split      the tacit mirror survives")

    if opening.output == "table":
        held("INFER takes its form from the document", "`output:` names the enumeration member")
    else:
        failures.append(f"  ✗ INFER output              {opening.output!r}")

    cycling = fresh().submit("")               # the member's table said: the turn cedes
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
    # the root parked, exhausted -- a bare call rewinds it and re-cedes
    if (cycling and cycling.document == "TURN"
            and cycling.instruction.keyword == "WORK"
            and cycled_again and cycled_again.document == "TURN"
            and cycled_again.instruction.keyword == "WORK"
            and not cycled_again.wait):
        held("TURN replays", "each exchange proven then parked on AWAIT -- the next bare call re-cedes, nothing ends")
    else:
        failures.append(f"  ✗ TURN cycle                 {cycling and cycling.command!r} / "
                        f"{cycled_again and cycled_again.command!r}")

    _, town_stack, _, _, _, _, _ = persistence.restore(session_of(booted.meta), revive)
    town_floor = town_stack.frames[0].procedure.instructions
    injected = [str(s) for s in town_floor if s.injected]
    if (cycled_again is not None and len(injected) == 1 and "MEMBER" in injected[0]
            and not (booted.meta / ".sys" / "records").exists()):
        held("install→boot end to end", "the base played and ships no seed: no record "
             "materializes; boot.initialize carries the member this case attached, nothing else")
    else:
        failures.append(f"  ✗ end to end                {cycled_again and cycled_again.command!r} / "
                        f"{[str(s) for s in town_floor]}")

    # the HOOK channel: a pending block renders for injection; a finished run is silence
    hooked_c = fresh()
    hooked_c.forget()
    pending = hooked_c.resume(hooked_c.boot("BOOT.md"))
    if pending and pending.next_call and render(pending).startswith("▌ pp ·"):
        held("the hook has something to say", "a pending block renders for injection")
    else:
        failures.append("  ✗ hook pending              nothing rendered")
    hooked_c.forget()

    # --- SYNC: bundles are machine-owned, the DATA is untouchable --------------------------
    (booted.meta / "procs" / "MINE.md").write_text(
        "---\nname: MINE\nkind: proc\nproc: |\n  HOOK mine\n---\nmy own\n",
        encoding="utf-8")
    (booted.meta / ".sys" / "records").mkdir(parents=True, exist_ok=True)
    (booted.meta / ".sys" / "records" / "notes.jsonl").write_text(
        '{"at": "2026-08-26T00:00:00", "entry": "the instance\'s own line"}\n', encoding="utf-8")
    kept_record = (booted.meta / ".sys" / "records" / "notes.jsonl").read_text(encoding="utf-8")
    kept_member = (booted.meta / "procs" / "MEMBER.md").read_text(encoding="utf-8")
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
            and (booted.meta / "procs" / "MEMBER.md").read_text(encoding="utf-8") == kept_member
            and (booted.meta / "procs" / "MINE.md").is_file()
            and not (booted.meta / ".sys" / "vendor" / "ghost@0.0.1").exists()
            and stale_session.exists()):
        held("sync updates, never touches", "bundles re-done, litter pruned, the standing "
             "session KEPT at constant pins, the data intact")
    else:
        failures.append("  ✗ sync                      bundle/data boundary broken")

    # a refused sync leaves the runs where they were: the composition is judged before any write
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
    shutil.rmtree(booted.meta / ".sys" / "vendor")
    expect("package-missing", lambda: fresh().boot("BOOT.md"))
    install_module.sync(booted)
    if fresh() is not None:
        held("sync repairs a bare vendor", "the gesture stands on the member alone")
    else:
        failures.append("  ✗ sync did not restand the conductor")

    # a pin the source does not carry: the sync refuses
    pinned = (booted.meta / instance.MANIFEST).read_text(encoding="utf-8")
    (booted.meta / instance.MANIFEST).write_text(
        re.sub(r"kit: \S+", "kit: 9.9.9", pinned), encoding="utf-8")
    expect("package-missing", lambda: install_module.sync(booted))
    (booted.meta / instance.MANIFEST).write_text(pinned, encoding="utf-8")

    return 0
