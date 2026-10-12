"""Scenario `marble-modes` -- 9 case(s) (plan core, batch le-document-de-la-conduction,
2026-10-06, its rework the same day): every section of the marble -- the engine, the base,
each package -- carries at most two files in its `system/`, `SYSTEM.COMMON.md` (what holds
in both modes) and `SYSTEM.CONDUCT.md` (what tells the LLM to make pp advance); the build
compiles `system.md` for a run the LLM conducts and `system.common.md` for a run its
principal conducts.
- (a) the build writes two marbles, `system.md` and `system.common.md`, each its receipt
- (b) every line of every `SYSTEM.CONDUCT.md` stands in `system.md`, none in
  `system.common.md` -- without exception
- (c) the sections compile in the order of the imports -- the engine (its card last), the
  base, each package -- each its COMMON, then its CONDUCT in `system.md` alone
- (h) no other file of `system/` is read, and a file without a body adds nothing
- (d) a run is served the marble of its mode, at its opening and after `-compacted`
- (e) a stale receipt of the principal's marble refuses a principal run's opening
- (f) `SYSTEM_PROMPT.md` under `override: true` composes one replace per marble
- (g) the doctor names both receipts, and the card a harness receives -- the card followed
  by the engine's `SYSTEM.CONDUCT.md` -- stands current, for the doctor and for the boot's
  card-drift
- (i) the package switch is the LLM's (batch la-suspension-par-l-agent): `system.md` carries
  the verb `-disable` and the principal's word on the packages, `system.common.md` neither
"""
from __future__ import annotations

import os

from conductor import compiling, install, persistence
from tests.harness import session_of
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, kept_document, load_script

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
COMMON = "system.common.md"
FILES = ("SYSTEM.COMMON.md", "SYSTEM.CONDUCT.md")


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


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    try:
        conduct = body_of(kept_document(SOURCE / "engine", "SYSTEM.CONDUCT"))
    except Exception as missing:          # without the engine's two files, every case is red
        failures.append(f"  ✗ the engine's section          {missing}")
        return 0
    env = bench.env("modes")
    sys = env.made / ".sys"
    llm, common = sys / "system.md", sys / COMMON

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
        return 0
    llm_text, common_text = llm.read_text(encoding="utf-8"), common.read_text(encoding="utf-8")

    # --- (i) the package switch in the LLM's marble alone -----------------------------------------
    if (llm_text.count("-disable") >= 2 and "PACKAGES play" in llm_text
            and "-disable" not in common_text and "PACKAGES play" not in common_text):
        held("(i) the switch is the LLM's", f"system.md says -disable {llm_text.count('-disable')} times and "
             "who says which packages play; system.common.md neither")
    else:
        failures.append(f"  ✗ (i) the switch               llm={llm_text.count('-disable')} "
                        f"common={common_text.count('-disable')}")

    # --- (b) every CONDUCT line in the LLM's marble alone, without exception -----------------------
    engine_root = sys / "engine"
    sections = [engine_root / "system"] + [root / "system" for root in sorted((sys / "vendor").glob("*@*"))]
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
    stacked_env = bench.env("modes-sayer", packages=("sayer",))
    stacked_sys = stacked_env.made / ".sys"
    kit_root = next((stacked_sys / "vendor").glob("kit@*"))
    sayer_root = next((stacked_sys / "vendor").glob("sayer@*"))
    base_conduct = kit_root / "system" / FILES[1]
    base_conduct.write_text("---\nname: SYSTEM.CONDUCT\nkind: doc\ndescription: the base's word to the "
                            "LLM\n---\nStand-in conduct: the bench's base tells the LLM to advance.\n",
                            encoding="utf-8")
    compiling.build_system(stacked_env.made)
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
    compiling.build_system(stacked_env.made)
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
    notes.write_text("---\nname: NOTES\nkind: doc\ndescription: another use\n---\n"
                     "Notes the marble never reads.\n", encoding="utf-8")
    compiling.build_system(stacked_env.made)
    after = {name: (stacked_sys / name).read_bytes() for name in ("system.md", COMMON)}
    empty.unlink()
    notes.unlink()
    compiling.build_system(stacked_env.made)
    if after == before and b"Notes the marble never reads." not in after["system.md"]:
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
    path = sys / compiling.RECEIPTS
    kept = path.read_text(encoding="utf-8")
    import yaml
    held_receipts = yaml.safe_load(kept)
    held_receipts[COMMON]["inputs"] = "0" * 64
    path.write_text(yaml.safe_dump(held_receipts, sort_keys=True), encoding="utf-8")
    expect("artifact-stale", lambda: _opened(env, True))
    path.write_text(kept, encoding="utf-8")
    env.conductor().forget()

    # --- (f) one replace per marble ----------------------------------------------------------------
    (env.made / "SYSTEM_PROMPT.md").write_text(
        "---\nname: SYSTEM_PROMPT\noverride: true\n---\nMy own base prompt.\n", encoding="utf-8")
    compiling.build_system(env.made)
    replaces = [sys / "system.replace.md", sys / "system.common.replace.md"]
    texts = [one.read_text(encoding="utf-8") if one.is_file() else "" for one in replaces]
    if (all(text.startswith("My own base prompt.") for text in texts)
            and conduct[:60] in texts[0] and conduct[:60] not in texts[1]):
        held("(f) one replace per marble", "under override: true, each replace leads with the "
             "operator's body and appends its own marble")
    else:
        failures.append(f"  ✗ (f) the replaces             {[one.is_file() for one in replaces]}")
    (env.made / "SYSTEM_PROMPT.md").unlink()
    compiling.build_system(env.made)

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
    return 0
