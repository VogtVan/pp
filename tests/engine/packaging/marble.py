"""Scenario `marble` -- the marble: the standing rules a run receives, compiled from the
`system/` sections of the engine, the base and each package.
- the standing rules: `system.md` at install, byte-stable across builds; the replace lock of
  `SYSTEM_PROMPT.md` (one replace per marble under `override: true`); the standing-orders
  channel with and without `PP_MARBLE`
- the modes: every section carries at most `SYSTEM.COMMON.md` (both modes) and
  `SYSTEM.CONDUCT.md` (what tells the LLM to make pp advance); the build writes `system.md` for
  a run the LLM conducts and `system.common.md` for a run its principal conducts, each with its
  receipt; the package switch, the CONDUCT lines, the order of the imports, the two names
  alone, the marble served per mode, a stale receipt, the doctor and the card a harness receives
- the sections: the engine's orders and card, the base's precision, the other packages after;
  a base without `system/SYSTEM.COMMON.md` refuses (`base-silent`); card-drift is the engine's
"""
from __future__ import annotations

import os

import yaml

from conductor import Conductor, compiling, discovery, install, persistence, render
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, kept_document, load_script, session_of

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
COMMON = "system.common.md"
FILES = ("SYSTEM.COMMON.md", "SYSTEM.CONDUCT.md")
PROSE = "just prose, no front matter\n"
OWN = "My own base prompt."
ZEBRA = "Zebra orders hold."
BASE_CONDUCT = "Stand-in conduct: the bench's base tells the LLM to advance."
NOTES = "Notes the marble never reads."


def _prompt(override: bool) -> str:
    return f"---\nname: SYSTEM_PROMPT\noverride: {str(override).lower()}\n---\n{OWN}\n"


def _sentences(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if len(line.strip()) >= 20]


def _standing(block) -> str:
    return next((text for title, text in (block.payloads if block else ())
                 if title == "standing orders"), "")


def _opened(env, principal: bool):
    spot = os.environ.get(VARIABLE)
    if principal:
        os.environ[VARIABLE] = "true"
    else:
        os.environ.pop(VARIABLE, None)
    try:
        env.conductor().forget()
        conductor = env.conductor()
        return conductor, conductor.start(conductor.boot("BOOT.md"))
    finally:
        if spot is None:
            os.environ.pop(VARIABLE, None)
        else:
            os.environ[VARIABLE] = spot


def _head(path) -> str:
    return body_of(path)[:60] if path.is_file() else ""


def _engine_heads() -> tuple[str, str]:
    """-> the openings of the engine's two sections, read at the source."""
    return (body_of(kept_document(SOURCE / "engine", "SYSTEM.COMMON"))[:60],
            body_of(kept_document(SOURCE / "engine", "SYSTEM.CONDUCT"))[:60])


def standing(bench, env) -> None:
    """The standing rules compiled at install, the replace lock, the standing-orders channel."""
    held, failures = bench.held, bench.failures
    made = env.made
    system_art = made / ".sys" / "system.md"
    replaces = [made / ".sys" / "system.replace.md", made / ".sys" / "system.common.replace.md"]
    orders, conduct = _engine_heads()
    first = system_art.read_bytes() if system_art.is_file() else b""
    compiling.build_system(made)
    compiled = first.decode("utf-8")
    if (system_art.is_file() and orders in compiled and conduct in compiled
            and system_art.read_bytes() == first
            and not (made / "SYSTEM_PROMPT.md").exists()
            and not any(one.exists() for one in replaces)):
        held("the marble compiles, append-only",
             "system.md at install, byte-stable across builds; SYSTEM_PROMPT.md never "
             "seeded, no replace artifact unasked")
    else:
        failures.append(f"  ✗ marble compile              {system_art.is_file()} {first[:60]!r}")

    prompt = made / "SYSTEM_PROMPT.md"
    prompt.write_text(PROSE, encoding="utf-8")
    compiling.build_system(made)
    warned_bare = (not any(one.exists() for one in replaces)
                   and any("override: true" in one for one in compiling.lint(made)))
    prompt.write_text(_prompt(False), encoding="utf-8")
    compiling.build_system(made)
    warned_false = (not any(one.exists() for one in replaces)
                    and any("override: true" in one for one in compiling.lint(made)))
    prompt.write_text(_prompt(True), encoding="utf-8")
    compiling.build_system(made)
    texts = [one.read_text(encoding="utf-8") if one.is_file() else "" for one in replaces]
    granted = (all(text.startswith(OWN) and orders in text and text.index(OWN) < text.index(orders)
                   for text in texts)
               and conduct in texts[0] and conduct not in texts[1]
               and not any("override: true" in one for one in compiling.lint(made)))
    prompt.write_text(_prompt(False), encoding="utf-8")
    compiling.build_system(made)
    retracted = not any(one.exists() for one in replaces)
    prompt.unlink()
    compiling.build_system(made)
    if warned_bare and warned_false and granted and retracted:
        held("the replace lock holds", "no `override: true`, no effect -- said by lint; "
             "granted, the user body leads and the marble appends; revoked, the artifact retracts")
    else:
        failures.append(f"  ✗ replace lock                {warned_bare}/{warned_false}/"
                        f"{bool(granted)}/{retracted}")

    marbled_engine = made / ".sys" / "engine" / "pp.py"
    marbled_member = discovery.instance_member(marbled_engine)

    def marbled_boot() -> str:
        one = Conductor(marbled_member, marbled_engine)
        block = one.start(one.boot("BOOT.md"))
        one.forget()
        return render(block) if block else ""

    served_boot = marbled_boot()
    os.environ["PP_MARBLE"] = "1"
    try:
        quiet_boot = marbled_boot()
    finally:
        del os.environ["PP_MARBLE"]
    if ("INFORMATION — standing orders" in served_boot
            and orders in served_boot
            and "standing orders" not in quiet_boot):
        held("the standing orders find their channel",
             "no PP_MARBLE: the boot serves them first; a wired marble declares itself "
             "and the boot stays quiet")
    else:
        failures.append(f"  ✗ standing orders channel     {('standing orders' in served_boot)}/"
                        f"{('standing orders' in quiet_boot)}")


def modes(bench, env, sayer) -> None:
    """Two marbles, one per mode: what each carries, in which order, and what each run is served."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    try:
        conduct_doc = kept_document(SOURCE / "engine", "SYSTEM.CONDUCT")
        conduct = body_of(conduct_doc)
    except Exception as missing:          # without the engine's two files, every case is red
        failures.append(f"  ✗ the engine's section          {missing}")
        return
    sys_dir = env.made / ".sys"
    llm, common = sys_dir / "system.md", sys_dir / COMMON

    # --- (a) two marbles, two receipts -----------------------------------------------------------
    receipts = compiling.receipts(env.made)
    if (llm.is_file() and common.is_file()
            and all((receipts.get(name) or {}).get("inputs") == compiling.receipt_inputs(env.made)
                    for name in ("system.md", COMMON))):
        held("(a) two marbles, two receipts", "system.md and system.common.md compiled at the "
             "install, each with its receipt on the same inputs")
    else:
        failures.append(f"  ✗ (a) two marbles              {llm.is_file()}/{common.is_file()} "
                        f"{sorted(receipts)}")
        return
    llm_text, common_text = llm.read_text(encoding="utf-8"), common.read_text(encoding="utf-8")

    # --- (i) the package switch in the LLM's marble alone -----------------------------------------
    switch = [line.strip() for line in conduct.splitlines() if "-disable" in line]
    if (len(switch) >= 2 and all(one in llm_text for one in switch)
            and not any(one in common_text for one in switch) and "-disable" not in common_text):
        held("(i) the switch is the LLM's", f"the {len(switch)} lines of the engine's "
             "SYSTEM.CONDUCT.md that name -disable, the principal's word on the packages "
             "among them, stand in system.md; system.common.md says none")
    else:
        failures.append(f"  ✗ (i) the switch               lines={len(switch)} "
                        f"llm={llm_text.count('-disable')} common={common_text.count('-disable')}")

    # --- (b) every CONDUCT line in the LLM's marble alone, without exception -----------------------
    engine_root = sys_dir / "engine"
    sections = [engine_root / "system"] + [root / "system" for root in sorted((sys_dir / "vendor").glob("*@*"))]
    lines = [one for section in sections if (section / FILES[1]).is_file()
             for one in _sentences(body_of(section / FILES[1]))]
    absent = [one for one in lines if one not in llm_text]
    leaked = [one for one in lines if one in common_text]
    if lines and not absent and not leaked:
        held("(b) every CONDUCT line in system.md alone", f"{len(lines)} lines of the "
             "SYSTEM.CONDUCT.md files: all in system.md, none in system.common.md")
    else:
        failures.append(f"  ✗ (b) the CONDUCT lines        absent={absent[:2]!r} leaked={leaked[:2]!r}")

    # --- (c) section by section, COMMON then CONDUCT, the card last of the engine's ---------------
    # (the stand-in base carries its COMMON alone: a CONDUCT is written into its vendored copy
    # for this case, so the base's two files take their places like the engine's)
    stacked_sys = sayer.made / ".sys"
    kit_root = next((stacked_sys / "vendor").glob("kit@*"))
    sayer_root = next((stacked_sys / "vendor").glob("sayer@*"))
    base_conduct = kit_root / "system" / FILES[1]
    base_conduct.write_text("---\nname: SYSTEM.CONDUCT\nkind: doc\ndescription: the base's word to the "
                            f"LLM\n---\n{BASE_CONDUCT}\n", encoding="utf-8")
    compiling.build_system(sayer.made)
    stacked = (stacked_sys / "system.md").read_text(encoding="utf-8")
    stacked_common = (stacked_sys / COMMON).read_text(encoding="utf-8")
    card_head = body_of(kept_document(SOURCE / "engine", "PP"))[:60]
    engine_files = [_head(stacked_sys / "engine" / "system" / name) for name in FILES]
    kit_files = [_head(kit_root / "system" / name) for name in FILES]
    sayer_common = _head(sayer_root / "system" / FILES[0])
    expected = [engine_files[0], engine_files[1], card_head, kit_files[0], kit_files[1], sayer_common]
    order = [stacked.find(one) if one else -1 for one in expected]
    expected_common = [engine_files[0], card_head, kit_files[0], sayer_common]
    order_common = [stacked_common.find(one) if one else -1 for one in expected_common]
    base_conduct.unlink()
    compiling.build_system(sayer.made)
    if (-1 not in order and order == sorted(order)
            and -1 not in order_common and order_common == sorted(order_common)
            and engine_files[1] not in stacked_common and kit_files[1] not in stacked_common):
        held("(c) the sections in the order of the imports", "system.md: the engine's COMMON, "
             "CONDUCT and card, the base's COMMON and CONDUCT, the sayer's COMMON; system.common.md: "
             "the same without a CONDUCT")
    else:
        failures.append(f"  ✗ (c) the order                {order} / {order_common}")

    # --- (h) the two names alone; a file without a body adds nothing ------------------------------
    before = {name: (stacked_sys / name).read_bytes() for name in ("system.md", COMMON)}
    empty = sayer_root / "system" / FILES[1]
    notes = sayer_root / "system" / "NOTES.md"
    empty.write_text("---\nname: SYSTEM.CONDUCT\nkind: doc\ndescription: nothing to say\n---\n",
                     encoding="utf-8")
    notes.write_text(f"---\nname: NOTES\nkind: doc\ndescription: another use\n---\n{NOTES}\n",
                     encoding="utf-8")
    compiling.build_system(sayer.made)
    after = {name: (stacked_sys / name).read_bytes() for name in ("system.md", COMMON)}
    empty.unlink()
    notes.unlink()
    compiling.build_system(sayer.made)
    if after == before and NOTES.encode("utf-8") not in after["system.md"]:
        held("(h) the two names alone", "an empty SYSTEM.CONDUCT.md and a NOTES.md in the sayer's "
             "system/ leave both marbles byte-identical")
    else:
        failures.append(f"  ✗ (h) the names read           "
                        f"{[after[name] == before[name] for name in before]}")

    # --- (d) the marble of the run's mode, at the opening and after -compacted -------------------
    led, led_block = _opened(env, True)
    led_compacted = env.conductor(led.run_id).compacted()
    plain, plain_block = _opened(env, False)
    if (_standing(led_block) == common_text.strip() and _standing(plain_block) == llm_text.strip()
            and _standing(led_compacted) == common_text.strip()):
        held("(d) each run its mode's marble", "a run its principal conducts is served "
             "system.common.md, at its opening and after -compacted; a run the LLM conducts "
             "system.md")
    else:
        failures.append(f"  ✗ (d) the served marble        principal={_standing(led_block)[:40]!r} "
                        f"llm={_standing(plain_block)[:40]!r} compacted={_standing(led_compacted)[:40]!r}")
    env.conductor().forget()

    # --- (e) a stale receipt of the principal's marble refuses ------------------------------------
    path = sys_dir / compiling.RECEIPTS
    kept = path.read_text(encoding="utf-8")
    held_receipts = yaml.safe_load(kept)
    held_receipts[COMMON]["inputs"] = "0" * 64
    path.write_text(yaml.safe_dump(held_receipts, sort_keys=True), encoding="utf-8")
    expect("artifact-stale", lambda: _opened(env, True))
    path.write_text(kept, encoding="utf-8")
    env.conductor().forget()

    # --- (g) the doctor and the card a harness receives ---------------------------------------------
    ws = env.made.parent
    load_script(install.product_root(PRODUCT_ENGINE) / "adapters" / "claude" / "wire.py").wire(ws, env.made)
    card = (ws / ".claude" / "skills" / "pp" / "SKILL.md").read_text(encoding="utf-8")
    told = install.verify(env.member)
    booted, _ = _opened(env, False)
    latched = [one.get("signal") for one in persistence.signals_of(session_of(env.made))]
    booted.forget()
    if ("card-drift" not in latched and conduct[:60] in card and card_head in card
            and card.index(card_head) < card.index(conduct[:60])
            and any(one.startswith("receipt system.md: current") for one in told)
            and any(one.startswith(f"receipt {COMMON}: current") for one in told)
            and any(one.startswith("card .claude") and one.endswith("current") for one in told)):
        held("(g) the doctor and the card", "the harness card is the card followed by the "
             "engine's SYSTEM.CONDUCT.md; the verifier names both receipts and the card current, "
             "and the boot latches no card-drift on it")
    else:
        failures.append(f"  ✗ (g) the doctor               {told!r} latched={latched!r}")


def sections(bench, env, sayer) -> None:
    """The sections in order, a silent base, the other packages after the base, the card's drift."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = env.made
    compiled = (made / ".sys" / "system.md").read_text(encoding="utf-8")

    # --- the sections, in order ----------------------------------------------------------
    engine_root = made / ".sys" / "engine"
    orders = body_of(engine_root / "system" / "SYSTEM.COMMON.md")[:60]
    card = body_of(engine_root / "refs" / "PP.md")[:60]
    kit_root = next((made / ".sys" / "vendor").glob("kit@*"))
    common = kit_root / "system" / "SYSTEM.COMMON.md"
    precision = body_of(common)[:60]
    common_kept = common.read_bytes()
    common.write_bytes(common_kept + f"\n{ZEBRA}\n".encode("utf-8"))
    compiling.build_system(made)
    layered = (made / ".sys" / "system.md").read_text(encoding="utf-8")
    common.write_bytes(common_kept)
    compiling.build_system(made)
    order = [layered.find(orders), layered.find(card), layered.find(precision), layered.find(ZEBRA)]
    if (-1 not in order and order == sorted(order)
            and (made / ".sys" / "system.md").read_text(encoding="utf-8") == compiled):
        held("the marble compiles in sections", "the engine's orders and its card, then the "
             "base's precision -- and byte-identical once the base's text is restored")
    else:
        failures.append(f"  ✗ sections                    {order}")

    # --- a silent base refuses at the build ----------------------------------------------
    common.unlink()
    expect("base-silent", lambda: compiling.build_system(made))
    common.write_bytes(common_kept)
    compiling.build_system(made)
    held("a silent base refuses", "a base without its SYSTEM.COMMON.md says nothing of its "
         "principal: `base-silent`, nothing compiled")

    # --- another package's section stands after the base's -------------------------------
    stacked = (sayer.made / ".sys" / "system.md").read_text(encoding="utf-8")
    sayer_root = next((sayer.made / ".sys" / "vendor").glob("sayer@*"))
    fragment = body_of(sayer_root / "system" / "SYSTEM.COMMON.md")[:60]
    placed = [stacked.find(orders), stacked.find(card), stacked.find(precision), stacked.find(fragment)]
    if -1 not in placed and placed == sorted(placed):
        held("the other packages come after the base", "the sayer's section compiles after the "
             "engine's orders and card and the base's precision")
    else:
        failures.append(f"  ✗ packages section            {placed}")

    # --- card-drift is the engine's: pushed with no check declared by the base ------------
    ws = made.parent
    projected = ws / ".claude" / "skills" / "pp" / "SKILL.md"
    if not projected.is_file():                           # wired once per workspace
        load_script(install.product_root(PRODUCT_ENGINE) / "adapters" / "claude" / "wire.py").wire(ws, made)
    pristine = projected.read_text(encoding="utf-8") == install.card(made)
    manifest = (kit_root / "package.yaml").read_text(encoding="utf-8")
    projected.write_text(projected.read_text(encoding="utf-8") + "\nOLD LAW\n", encoding="utf-8")
    member = discovery.instance_member(engine_root / "pp.py")
    conductor = Conductor(member, engine_root / "pp.py", "t")
    conductor.start(conductor.boot("BOOT.md"))
    latched = persistence.signals_of(session_of(made))
    conductor.forget()
    verified = install.verify(member)
    if (pristine and "card-drift" not in manifest
            and any(one.get("signal") == "card-drift" and one.get("source") == "engine" for one in latched)
            and any("DRIFTED" in one for one in verified)):
        held("the card is the engine's, and so is its drift", "the projection is byte-identical to "
             "engine/refs/PP.md followed by engine/system/SYSTEM.CONDUCT.md; edited, the boot pushes "
             "`card-drift` from the engine though the base declares no check, and the verifier "
             "names the drifted card")
    else:
        failures.append(f"  ✗ engine card-drift           pristine={pristine} "
                        f"manifest-clean={'card-drift' not in manifest} {latched!r}")


def scenario(bench) -> int:
    plain = bench.env("marble")
    sayer = bench.env("marble-sayer", packages=("sayer",))
    standing(bench, plain)
    modes(bench, plain, sayer)
    sections(bench, plain, sayer)
    return 0
