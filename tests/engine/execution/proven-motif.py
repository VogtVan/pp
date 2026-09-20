"""Scenario `proven-motif` -- 7 case(s), in the monolith's order:
- lot b: PROVEN_INFERENCE.md -- the kit carries the motif, opt-in by CALL
- la-semaine-se-sert: the weekly digest, guaranteed by pp
- l-effort-seul: the effort presets the weight keys, the rest stays the operator's
  (les-cles-mortes, 2026-09-05: `conduction`, `conduction_profile` and `document_serve`
  died with their three cases -- the switch, the natural words, the role)
- the settings follow the engine at upgrade: seeds BARE,
- relic comments stand, empty keys FILL, the old serve carries, a stranger
- the template seeds every key VALUED -- the install's contract
- the system is ONE: the effort presets the kit's keys in code, a prefixed
- la-forme-se-customise: a format definition is YOURS to override
"""
from __future__ import annotations

import json
from pathlib import Path
from conductor import Conductor, render, revive, compiling, discovery, instance, persistence, reading, settings
from tests.harness import load_script, session_of, SOURCE, kept_document, body_of, reaches



def scenario(bench) -> int:
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    # --- lot b: PROVEN_INFERENCE.md -- the kit carries the motif, opt-in by CALL -------
    from conductor import install as install_module                       # noqa: PLC0415
    proven_made = bench.env("proven").made
    proven_member = discovery.instance_member(proven_made / ".sys" / "engine" / "pp.py")

    def proven_c() -> Conductor:
        return Conductor(proven_member, discovery.siblings_around(proven_member),
                         proven_made / ".sys" / "engine" / "pp.py")

    wrap_doc = proven_made / "procs" / "WRAP.md"
    wrap_doc.write_text(
        "---\nname: WRAP\nkind: proc\ndescription: wraps the motif\n"
        "constraints.production: |\n  W1  the ship is named\nproc: |\n"
        "  WORK\n---\nthe ask: name the ship\n", encoding="utf-8")
    wrapped = proven_c().start(wrap_doc)
    if (wrapped.document == "WRAP" and wrapped.command == "WORK"
            and "-sp" not in wrapped.next_call
            and "PROVEN_INFERENCE" not in (proven_made / ".sys" / "tools.md").read_text(encoding="utf-8")):
        held("the motif is the language", "WORK/PROVE inline -- chat-bound here; no motif document left to catalog")
    else:
        failures.append(f"  ✗ kit motif                   {wrapped.document!r} {wrapped.next_call!r}")

    proven_c().submit("")                       # the production, said in chat
    motif_fail = proven_c().submit('[{"code": "W1", "evidence": "off", "verdict": "fail"}]')
    proven_c().submit("")
    motif_ok = proven_c().submit('[{"code": "W1", "evidence": "named", "verdict": "ok"}]')
    if (motif_fail.document == "WRAP" and motif_fail.position == 1
            and "your own proof failed" in motif_fail.deviation and over(motif_ok)):
        held("the motif loops and lands", "a failed proof reopens ITS document; an ok one lets the caller finish")
    else:
        failures.append(f"  ✗ motif loop                  {motif_fail.position} "
                        f"{motif_fail.deviation!r} {motif_ok and motif_ok.command!r}")
    proven_c().forget()

    (proven_made / "procs" / "TAKER.md").write_text(
        "---\nname: TAKER\ndescription: takes the proven production\ninput: any\nproc: |\n"
        "  HOOK taken\n---\ntake it\n", encoding="utf-8")
    chain_doc = proven_made / "procs" / "CHAIN.md"
    chain_doc.write_text(
        "---\nname: CHAIN\nkind: proc\ndescription: chains the motif\n"
        "constraints.production: |\n  C9  the payload is made\nproc: |\n"
        "  WORK\n  CALL TAKER.md\n---\nmake then ship\n",
        encoding="utf-8")
    chained = proven_c().start(chain_doc)
    proven_c().submit("the payload")
    chain_done = proven_c().submit('[{"code": "C9", "evidence": "the payload", "verdict": "ok"}]')
    _, chain_stack, _, _, _, _, _, _ = persistence.restore(session_of(proven_member.meta), revive)
    made_call = chain_stack.frames[0].procedure.instructions[0]
    if (" -   (" in chained.next_call and over(chain_done)
            and made_call.given == "the payload"):
        held("the motif feeds a pipeline", "output any -- captured on stdin, the proven production crosses to the taker")
    else:
        failures.append(f"  ✗ motif pipeline              {chained.next_call!r} {made_call.given!r}")
    proven_c().forget()

    # the weekly-digest case (la-semaine-se-sert) and the digest guards migrated
    # RED to the continuity phase (KPS21, batch la-purete-du-kit): the cadence, HISTORY
    # and the continuity skill left the kit. The env stays: the conduction cases below live on it.
    weekly_made = bench.env("weekly").made
    weekly_member = discovery.instance_member(weekly_made / ".sys" / "engine" / "pp.py")

    def weekly_c() -> Conductor:
        return Conductor(weekly_member, discovery.siblings_around(weekly_member),
                         weekly_made / ".sys" / "engine" / "pp.py")
    # --- l-effort-seul: the effort presets the weight keys, the rest stays the operator's
    (weekly_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\n"
        "conduction_effort: light\n"
        "verbatim_constraints: true\nmax_harness_tool_output: 26000\n---\n", encoding="utf-8")
    styled = weekly_c()._settings
    if (styled.effort == "light"
            and not styled.verbatim_constraints  # light presets the weights over the written key
            and styled.body_serve == "once" and styled.fusion == 0
            and styled.harness_cap == 26000):
        held("the effort presets alone", "light presets verbatim false, fusion max and body "
             "once over the written keys -- the cap stays the operator's; no role, no "
             "serve regime: the dead keys are gone")
    else:
        failures.append(f"  ✗ effort alone                {styled!r}")
    (weekly_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nconduction_effort: heavy\n---\n", encoding="utf-8")
    expect("settings-invalid", weekly_c)

    # --- the settings follow the engine at upgrade: seeds BARE, ---------------------
    #     the stale body entry gives way to the template's successors
    (weekly_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\n"
        "max_harness_tool_output: 26000\n---\n\n"
        "# SETTINGS\n\n"
        "- `stale_key` — the OLD prose, stale the day the template moved on\n"
        "  and its continuation line.\n"
        "- `capture_prompt` — the operator's own words, byte-for-byte.\n",
        encoding="utf-8")
    sync_settings = install_module.sync_settings
    sync_source = SOURCE
    sync_told = sync_settings(weekly_made, sync_source)
    synced = (weekly_made / "SETTINGS.md").read_text(encoding="utf-8")
    resynced = sync_settings(weekly_made, sync_source)
    template_text = (sync_source / "template" / "instance" / "SETTINGS.md").read_text(encoding="utf-8")
    template_body = template_text.split("\n---\n", 1)[1]
    from conductor import settings as tuning_module
    sync_fragments = tuning_module.fragments(weekly_made)
    synced_body = synced.split("\n---\n", 1)[1]
    synced_keys = [l.split(":", 1)[0] for l in synced.split("\n---\n", 1)[0].splitlines()
                   if l and l[0] not in "#- " and ":" in l and not l.startswith("name")
                   and not l.startswith("kind") and not l.startswith("description")]
    template_keys = [l.split(":", 1)[0] for l in template_text.split("\n---\n", 1)[0].splitlines()
                     if l and l[0] not in "#- " and ":" in l and not l.startswith("name")
                     and not l.startswith("kind") and not l.startswith("description")]
    switch_keys = [f"package.{name}" for name in instance.pins(weekly_made)   # the engine's
                   if name != instance.base_of(weekly_made)]                   # switches, one per pin
    composed_keys = template_keys + switch_keys + [key for one in sync_fragments for key, _ in one.defaults]
    composed_body = template_body + "".join("\n" + one.body + ("" if one.body.endswith("\n") else "\n")
                                            for one in sync_fragments)
    sections = [synced_body.index(f"## {one.name.capitalize()} — ") for one in sync_fragments]
    if ("max_harness_tool_output: 26000" in synced
            and "conduction_effort: medium" in synced
            and "conduction:" not in synced and "document_serve" not in synced
            and synced_keys == composed_keys
            and synced_body == composed_body
            and "## System — " in synced_body
            and sections == sorted(sections)
            and all(f"# ---- {one.name} ----" in synced for one in sync_fragments)
            and "the OLD prose" not in synced
            and weekly_c()._settings.harness_cap == 26000
            and not resynced):
        held("the settings are composed", "the engine's template then every fragment in the "
             "requires topology -- keys grouped and marked, one named section each -- the "
             "operator's VALUES kept, every "
             "missing key lands VALUED -- and the sync is idempotent")
    else:
        failures.append(f"  ✗ settings sync               {sync_told!r} {resynced!r} "
                        f"{synced_keys == composed_keys} {synced_body == composed_body} "
                        f"{synced[:600]!r}")

    # --- relic comments stand, empty keys FILL, the old serve carries, a stranger
    #     key travels after the known ones
    (weekly_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nstranger_day: never\nconduction: auto\n"
        "conduction_effort: medium\ncapture_prompt:\n"
        "cap.improvement: 4\n# memory: 5\n---\n", encoding="utf-8")
    healed_told = sync_settings(weekly_made, sync_source)
    healed = (weekly_made / "SETTINGS.md").read_text(encoding="utf-8")
    healed_front = healed.split("\n---\n", 1)[0]
    if ("capture_prompt: false" in healed
            and "# memory: 5" in healed
            and "conduction: auto" in healed        # a dead key the operator still carries:
            and "cap.improvement: 4" in healed      # an unowned stranger, kept, theirs to remove
            and healed_front.index("cap.improvement") > healed_front.index("conduction_effort")
            and healed_front.index("stranger_day") > healed_front.index("cap.improvement")
            and healed_front.index("conduction: auto") > healed_front.index("cap.improvement")
            and healed_front.index("# memory: 5") > healed_front.index("stranger_day")
            and any("filled" in one for one in healed_told)):
        held("no key stays empty", "a key standing EMPTY fills with the default it "
             "silently played, the operator's own keys -- a dead one included -- travel "
             "after the known ones, a commented relic stays at the tail")
    else:
        failures.append(f"  ✗ empty fill                  {healed_told!r} {healed[:400]!r}")

    # --- the template seeds every key VALUED -- the install's contract --------------
    seed_contract = install_module.SEEDS
    template_front = reading.read(
        sync_source / "template" / "instance" / "SETTINGS.md").front
    unseeded = [key for key, _ in seed_contract if key not in template_front]
    empty_seeded = [key for key, value in template_front.items()
                    if value is None or str(value).strip() == ""]
    package_keys = [(one.name, key) for one in sync_fragments for key, _ in one.defaults]
    if (not unseeded and not empty_seeded
            and "conduction" not in template_front
            and "conduction_profile" not in template_front
            and "document_serve" not in template_front
            and str(template_front.get("conduction_effort")) == "medium"
            and "implementation_care" not in template_front
            and "session_memory_frequency" not in template_front
            and "workspace_improvement" not in template_front
            and all(key.startswith(name + "_") for name, key in package_keys)
            and all(key in one.types for one in sync_fragments for key, _ in one.defaults)):
        held("the template seeds the protocol alone", "every protocol key present, bare, "
             "none empty -- effort medium, no dead key; every package "
             "key prefixed and typed at its fragment (the kit carries none since "
             "la-purete-du-kit)")
    else:
        failures.append(f"  ✗ template completeness       missing {unseeded!r} "
                        f"empty {empty_seeded!r} {package_keys!r}")

    # --- the system is ONE: the effort presets the kit's keys in code, a prefixed ---
    #     relic migrates back, a rename renamed follows its chain
    if True:
        (weekly_made / "SETTINGS.md").write_text(
            "---\nname: SETTINGS\nkind: doc\nconduction_effort: light\n---\n", encoding="utf-8")
        light_front = tuning_module.effective(
            reading.read(weekly_made / "SETTINGS.md").front, weekly_made)
        (weekly_made / "SETTINGS.md").write_text(
            "---\nname: SETTINGS\nkind: doc\nconduction_effort: full\n---\n", encoding="utf-8")
        full_front = tuning_module.effective(
            reading.read(weekly_made / "SETTINGS.md").front, weekly_made)
        # the reflex-preset case migrated with the kit's fragment to improvement (KPS21,
        # batch la-purete-du-kit); the fragment preset mechanism is proven at resources.

        # --- le-corps-une-fois: the effort presets proc_body_serve, the key is one of two words
        if (light_front.get("proc_body_serve") == "once"
                and full_front.get("proc_body_serve") == "always"):
            held("the effort presets the body's serve", "light puts proc_body_serve to once, "
                 "full to always -- the sixth weight knob")
        else:
            failures.append(f"  ✗ effort on the body          {light_front.get('proc_body_serve')!r} "
                            f"{full_front.get('proc_body_serve')!r}")
        (weekly_made / "SETTINGS.md").write_text(
            "---\nname: SETTINGS\nkind: doc\nconduction_effort: medium\nproc_body_serve: always\n---\n",
            encoding="utf-8")
        medium_front = tuning_module.effective(
            reading.read(weekly_made / "SETTINGS.md").front, weekly_made)
        (weekly_made / "SETTINGS.md").write_text(
            "---\nname: SETTINGS\nkind: doc\nconduction_effort: none\nproc_body_serve: once\n---\n",
            encoding="utf-8")
        none_front = tuning_module.effective(
            reading.read(weekly_made / "SETTINGS.md").front, weekly_made)
        if (medium_front.get("proc_body_serve") == "once"
                and none_front.get("proc_body_serve") == "once"):
            held("medium and none on the body's serve", "medium presets once over the "
                 "operator's always; under none the bare key rules -- once stays once")
        else:
            failures.append(f"  ✗ medium/none on the body     {medium_front.get('proc_body_serve')!r} "
                            f"{none_front.get('proc_body_serve')!r}")
        (weekly_made / "SETTINGS.md").write_text(
            "---\nname: SETTINGS\nkind: doc\nproc_body_serve: sometimes\n---\n", encoding="utf-8")
        expect("settings-invalid", weekly_c)
        bad_root = weekly_made / ".sys" / "vendor" / "badpkg@0.0.1"
        (bad_root / "settings").mkdir(parents=True)
        (bad_root / "package.yaml").write_text("name: badpkg\nversion: 0.0.1\nrequires: []\n",
                                               encoding="utf-8")
        (bad_root / "settings" / "SETTINGS.md").write_text(
            "---\nname: SETTINGS\nkind: fragment\npackage: badpkg\nloose_key: 1\n---\n",
            encoding="utf-8")
        pinned_text = (weekly_made / ".sys" / "instance.yaml").read_text(encoding="utf-8")
        (weekly_made / ".sys" / "instance.yaml").write_text(
            pinned_text.replace("packages:\n", "packages:\n  badpkg: 0.0.1\n"), encoding="utf-8")
        expect("settings-fragment-invalid", lambda: tuning_module.fragments(weekly_made))
        (weekly_made / ".sys" / "instance.yaml").write_text(pinned_text, encoding="utf-8")
        import shutil
        shutil.rmtree(bad_root)

    # --- la-forme-se-customise: a format definition is YOURS to override ---------------
    (proven_made / "FORMATS.md").write_text(
        "---\nname: FORMATS\nkind: doc\ndescription: local overrides\nformats: |\n"
        "  table  stdin  the operator's own table style\n---\n", encoding="utf-8")
    shaped = compiling.format_enumeration(proven_member.meta)
    catalog_shaped = compiling.render_tools(proven_member.meta)
    if (shaped["table"][1] == "the operator's own table style"
            and shaped["table"][2] == "FORMATS.md"
            and shaped["free"][1].startswith("structure with titled sections")
            and shaped["free"][2] == "engine"
            and "the operator's own table style" in catalog_shaped):
        held("a format is yours to override",
             "the instance redeclares a DESCENDED name and wins -- instance over "
             "packages over engine, customizing is redeclaring at home")
    else:
        failures.append(f"  ✗ format override             {shaped.get('table')!r} / "
                        f"{shaped.get('free')!r}")
    (proven_made / "FORMATS.md").unlink()

    installed_forms = compiling.format_enumeration(proven_member.meta)
    if ("✅ done" in installed_forms["table"][1]
            and installed_forms["table"][2] == "engine"
            and installed_forms["free"][2] == "engine"
            and (weekly_made / "FORMATS.md").is_file()):
        held("the mechanical forms reach the enumeration from the engine",
             "table's rich shape rides language.FORMATS -- FORMATS.md stays the home of overrides")
    else:
        failures.append(f"  ✗ airy presentation           {installed_forms['table'][1][:60]!r} / "
                        f"{installed_forms['free'][1][:60]!r}")
    return 0
