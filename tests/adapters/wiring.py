"""Scenario `wiring` -- 3 case(s), in the monolith's order:
- les-trois-cablages: the marble wired per host
- lot fix: les recus refusent, le processus se relaie
- LJ2 l-adapter-jour-2: a standing instance gains an adapter
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from conductor import Conductor, render, compiling, discovery, instance, persistence
from tests.harness import load_script, pin_step, ENGINE_VERSION, PRODUCT_ENGINE, SOURCE, body_of, kept_document, reaches, cli, session_of
from conductor import install as install_module


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    product_engine = PRODUCT_ENGINE
    # --- les-trois-cablages: the marble wired per host --------------------------------
    wired_made = bench.env("wired").made
    wired_ws = wired_made.parent
    adapters_root = install_module.product_root(product_engine) / "adapters"
    claude_wire = load_script(adapters_root / "claude" / "wire.py")
    claude_wire.wire(wired_ws, wired_made)
    launcher = wired_ws / "claude-pp"
    launcher_text = launcher.read_text(encoding="utf-8") if launcher.is_file() else ""
    runnable = launcher.is_file() and bool(launcher.stat().st_mode & 0o111)
    launcher.write_text("#!/bin/sh\n# mine\n", encoding="utf-8")
    claude_wire.wire(wired_ws, wired_made)
    kept = launcher.read_text(encoding="utf-8") == "#!/bin/sh\n# mine\n"
    twin_text = ((wired_ws / "claude-pp.cmd").read_text(encoding="utf-8")
                 if (wired_ws / "claude-pp.cmd").is_file() else "")
    if (runnable and "--append-system-prompt-file" in launcher_text
            and "--system-prompt-file" in launcher_text
            and "system.replace.md" in launcher_text
            and "PP_MARBLE=1" in launcher_text
            and "%~dp0" in twin_text and "--append-system-prompt-file" in twin_text
            and "PP_MARBLE" in twin_text
            and (wired_ws / ".claude" / "skills" / "pp" / "SKILL.md").is_file()
            and kept):
        held("claude wires the marble", "claude-pp appends by default, its .cmd twin too; "
             "the replace artifact switches the flag; written once, then the operator's own")
    else:
        failures.append(f"  ✗ claude marble wire          {runnable}/{kept} {launcher_text[:80]!r}")

    codex_wire = load_script(adapters_root / "codex" / "wire.py")
    codex_wire.wire(wired_ws, wired_made)
    codex_config = wired_ws / ".codex" / "config.toml"
    codex_rules = wired_ws / ".codex" / "rules" / "default.rules"
    codex_text = codex_config.read_text(encoding="utf-8") if codex_config.is_file() else ""
    rules_text = codex_rules.read_text(encoding="utf-8") if codex_rules.is_file() else ""
    codex_wire.wire(wired_ws, wired_made)
    if ('developer_instructions = """' in codex_text and "conducted" in codex_text
            and "shell_environment_policy" in codex_text and "PP_MARBLE" in codex_text
            and codex_config.read_text(encoding="utf-8") == codex_text
            and (wired_ws / ".agents" / "skills" / "pp" / "SKILL.md").is_file()
            and "prefix_rule" in rules_text and "pp.py" in rules_text
            and "execpolicy check" in rules_text
            and codex_rules.read_text(encoding="utf-8") == rules_text):
        held("codex wires the full surface", "card at .agents/skills (Cursor reads it too), "
             "developer_instructions appends, a prefix rule guards the invocation -- written once")
    else:
        failures.append(f"  ✗ codex adapter               {codex_text[:60]!r} {rules_text[:60]!r}")

    gemini_wire = load_script(adapters_root / "gemini" / "wire.py")
    gemini_wire.wire(wired_ws, wired_made)
    gdoor = wired_ws / "GEMINI.md"
    gcommand = wired_ws / ".gemini" / "commands" / "pp.toml"
    door_text = gdoor.read_text(encoding="utf-8") if gdoor.is_file() else ""
    command_text = gcommand.read_text(encoding="utf-8") if gcommand.is_file() else ""
    gemini_wire.wire(wired_ws, wired_made)
    if ("/pp" in door_text and "conducted" in door_text
            and not (wired_ws / ".gemini" / "settings.json").exists()
            and 'prompt = """' in command_text and "conducted" in command_text
            and (wired_ws / "gemini-pp").is_file()
            and "GEMINI_SYSTEM_MD" in ((wired_ws / "gemini-pp.cmd").read_text(encoding="utf-8")
                                       if (wired_ws / "gemini-pp.cmd").is_file() else "")
            and gdoor.read_text(encoding="utf-8") == door_text
            and gcommand.read_text(encoding="utf-8") == command_text):
        held("gemini wires door and card", "GEMINI.md is a native door pointing at /pp -- "
             "no settings file; /pp serves the card inline; the launcher stands -- written once")
    else:
        failures.append(f"  ✗ gemini adapter              {door_text[:60]!r} {command_text[:60]!r}")

    if install_module.wired_providers(wired_ws) == ["claude", "codex", "gemini"]:
        held("wired providers read from artifacts",
             "claude+codex+gemini detected; cursor stays behind codex's shared card -- said")
    else:
        failures.append(f"  ✗ provider detection          {install_module.wired_providers(wired_ws)}")

    cursor_only = Path(tempfile.mkdtemp()) / "solo"
    cursor_made = install_module.install(product_engine, cursor_only / ".pp", [], doors=False)
    pin_step(cursor_made)
    cursor_wire = load_script(adapters_root / "cursor" / "wire.py")
    cursor_wire.wire(cursor_only, cursor_made)
    solo_card = cursor_only / ".agents" / "skills" / "pp" / "SKILL.md"
    solo_permissions = cursor_only / ".cursor" / "permissions.json"
    shared_ok = (not (cursor_only / ".codex").exists() and solo_card.is_file()
                 and solo_permissions.is_file()
                 and "./pp" in json.loads(
                     solo_permissions.read_text(encoding="utf-8"))["terminalAllowlist"]
                 and all((cursor_only / name).is_file()
                         for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")))
    cursor_wire.wire(wired_ws, wired_made)   # card already there from -codex: shared, no clash
    if (shared_ok and (wired_ws / ".agents" / "skills" / "pp" / "SKILL.md").is_file()
            and (wired_ws / ".cursor" / "permissions.json").is_file()):
        held("cursor opens every door", "-cursor writes ALL the doors (multi-model harness), "
             "the cross-vendor card AND its terminalAllowlist prefix -- the shared card "
             "never blocks the permissions")
    else:
        failures.append(f"  ✗ cursor wire                 {shared_ok}")

    scoped = Path(tempfile.mkdtemp()) / "scoped"
    codex_only = cli(product_engine, "-install", str(scoped), "-codex")
    if (codex_only.returncode == 0 and (scoped / "AGENTS.md").is_file()
            and not (scoped / "CLAUDE.md").exists()):
        held("doors follow the flags", "-codex alone: AGENTS.md stands, no CLAUDE.md litter; "
             "a bare install keeps the two generic doors")
    else:
        failures.append(f"  ✗ door scoping                rc={codex_only.returncode}")

    # --- lot fix: les recus refusent, le processus se relaie --------------------------
    rcpt_made = bench.env("rcpt").made
    rcpt_ws = rcpt_made.parent
    rcpt_member = discovery.instance_member(rcpt_made / ".sys" / "engine" / "pp.py")

    def rcpt_c() -> Conductor:
        return Conductor(rcpt_member, discovery.siblings_around(rcpt_member),
                         rcpt_made / ".sys" / "engine" / "pp.py", "t")

    rcpt_held = compiling.receipts(rcpt_made)
    rcpt_first = rcpt_c().start(rcpt_c().boot("BOOT.md"))
    rcpt_c().forget()
    if (all((rcpt_held.get(name) or {}).get("engine") == ENGINE_VERSION
            for name in ("system.md", "tools.md"))
            and rcpt_held["system.md"]["inputs"] == compiling.receipt_inputs(rcpt_made)
            and rcpt_first is not None and "recall drift" not in render(rcpt_first)):
        held("every build leaves a receipt", "system and tools each carry engine + "
             "inputs; a receipted boot passes, no drift said")
    else:
        failures.append(f"  ✗ build receipts              {rcpt_held!r}")

    load_script(adapters_root / "claude" / "wire.py").wire(rcpt_ws, rcpt_made)
    told_one = install_module.doctor(rcpt_member)
    art_before = (rcpt_made / ".sys" / "system.md").read_bytes()
    told_two = install_module.doctor(rcpt_member)
    if (not any("refreshed" in one or "candidate" in one for one in told_two)
            and (rcpt_made / ".sys" / "system.md").read_bytes() == art_before
            and not any("STALE" in one or "DRIFTED" in one for one in told_two)
            and any(one.startswith("receipt system.md: current") for one in told_two)
            and any(one.startswith("card .claude") for one in told_two)):
        held("doctor twice is silence", "no projection moves, the artifacts hold their "
             "bytes, and the verifier names every receipt and card current")
    else:
        failures.append(f"  ✗ doctor x2                   {told_two!r}")

    receipts_path = rcpt_made / ".sys" / "receipts.yaml"
    receipts_text = receipts_path.read_text(encoding="utf-8")
    receipts_path.write_text(receipts_text.replace(ENGINE_VERSION, "0.1.0-alpha.0"),
                             encoding="utf-8")
    expect("artifact-stale", lambda: rcpt_c().start(rcpt_c().boot("BOOT.md")))
    receipts_path.unlink()
    expect("artifact-stale", lambda: rcpt_c().start(rcpt_c().boot("BOOT.md")))
    receipts_path.write_text(receipts_text, encoding="utf-8")
    late_input = next((rcpt_made / ".sys" / "vendor").glob("kit@*")) / "system" / "ZZ-late.md"
    late_input.write_text("---\nname: ZZ\nkind: doc\ndescription: a moved input\n---\n"
                          "Late law.\n", encoding="utf-8")
    expect("artifact-stale", lambda: rcpt_c().start(rcpt_c().boot("BOOT.md")))
    late_input.unlink()
    rcpt_back = rcpt_c().start(rcpt_c().boot("BOOT.md"))
    rcpt_c().forget()
    if rcpt_back is not None:
        held("a stale artifact refuses the boot", "wrong engine, no receipt and moved "
             "inputs each refuse aloud and name the repair; receipts restored, the boot passes")
    else:
        failures.append("  ✗ artifact-stale recovery     the restored receipt did not boot")

    # --- le-recu-du-catalogue: the instance's own inputs moved -> the boot recompiles ------
    # the witness (S4.01-S4.04, 2026-08-26): FORMATS.md edited without -build, the run booted
    # on a catalog that still served a dead format
    (rcpt_made / "FORMATS.md").write_text(
        "---\nname: FORMATS\nkind: doc\nformats: |\n  motto  inline  one line, the house motto\n---\n",
        encoding="utf-8")
    catalog_boot = rcpt_c().start(rcpt_c().boot("BOOT.md"))
    rcpt_c().forget()
    catalog_text = (rcpt_made / ".sys" / "tools.md").read_text(encoding="utf-8")
    catalog_receipt = (compiling.receipts(rcpt_made).get("tools.md") or {}).get("catalog")
    if (catalog_boot is not None and "`motto`" in catalog_text
            and catalog_receipt == compiling.catalog_inputs(rcpt_made)):
        held("a moved catalog recompiles at the boot", "a format declared after the build is "
             "in the catalog the boot serves; the receipt follows")
    else:
        failures.append(f"  ✗ catalog receipt             motto={'`motto`' in catalog_text} "
                        f"receipt={catalog_receipt is not None}")
    (rcpt_made / "procs" / "DEADFMT.md").write_text(
        "---\nname: DEADFMT\nkind: proc\noutput: nowhere\nproc: |\n  INFER\n---\nbody\n",
        encoding="utf-8")
    expect("reference-unknown", lambda: rcpt_c().start(rcpt_c().boot("BOOT.md")))
    (rcpt_made / "procs" / "DEADFMT.md").unlink()

    rcpt_card = rcpt_ws / ".claude" / "skills" / "pp" / "SKILL.md"
    rcpt_card.write_text(rcpt_card.read_text(encoding="utf-8") + "\nOLD LAW\n",
                         encoding="utf-8")
    rcpt_c().start(rcpt_c().boot("BOOT.md"))
    # the drift is a DECLARED check now (predicate card-drift): the boot pushes the
    # signal and the run latches it -- the improve serves it, not a boot payload
    drift_latched = persistence.signals_of(session_of(rcpt_made))
    rcpt_c().forget()
    drift_verify = install_module.verify(rcpt_member)
    if (any(one.get("signal") == "card-drift" for one in drift_latched)
            and any("DRIFTED" in one for one in drift_verify)):
        held("a drifted card is said", "the boot latches card-drift -- an old card "
             "cannot conduct in silence; the verifier names the drifted card")
    else:
        failures.append(f"  ✗ recall drift                {drift_latched!r} / {drift_verify!r}")

    xver_made = bench.env("xver").made
    old_engine = xver_made / ".sys" / "engine"
    (old_engine / "conductor" / "core" / "version.py").write_text('VERSION = "0.1.0-alpha.0"\n',
                                                         encoding="utf-8")
    neutered = (old_engine / "conductor" / "packaging" / "compiling.py").read_text(encoding="utf-8")
    (old_engine / "conductor" / "packaging" / "compiling.py").write_text(
        neutered.replace('if root.name.startswith("kit@") and card.is_file():',
                         "if False:"), encoding="utf-8")
    xver_stale = instance.read(xver_made)
    xver_stale["engine"] = "0.1.0-alpha.0"
    instance.write(xver_made, xver_stale)
    (xver_made / ".sys" / "system.md").write_text("old envelope alone\n", encoding="utf-8")
    (xver_made / ".sys" / "receipts.yaml").unlink()
    crossed = cli(old_engine / "pp.py", "upgrade")
    xver_system = (xver_made / ".sys" / "system.md").read_text(encoding="utf-8")
    xver_receipt = (compiling.receipts(xver_made).get("system.md") or {})
    if (crossed.returncode == 0
            and "engine 0.1.0-alpha.0 -> " in crossed.stdout
            and reaches(xver_system, body_of(kept_document(SOURCE / "kit", "PP")))
            and xver_receipt.get("engine") == ENGINE_VERSION):
        held("the old engine hands the compile over", "upgrade run BY alpha.0 copies the "
             "current engine then delegates its tail: the marble carries the canon and "
             "the receipt names the NEW engine -- pin N+1 is compiled by code N+1")
    else:
        failures.append(f"  ✗ cross-version upgrade       rc={crossed.returncode} "
                        f"receipt={xver_receipt!r} {crossed.stderr[-120:]!r}")

    # --- LJ2 l-adapter-jour-2: a standing instance gains an adapter -------------------
    scoped_engine = scoped / ".pp" / ".sys" / "engine" / "pp.py"
    day2 = cli(scoped_engine, "-install", "-claude")
    day2_again = cli(scoped_engine, "-install", "-codex")
    if (day2.returncode == 0 and (scoped / "CLAUDE.md").is_file()
            and (scoped / "claude-pp").is_file()
            and day2_again.returncode == 0
            and "already wired" in day2_again.stdout):
        held("an adapter lands on day 2", "`-install -claude` alone wires the CURRENT "
             "instance -- the codex-only workspace gains the claude surface; replayed "
             "on codex, the write-once artifacts answer `already wired`")
    else:
        failures.append(f"  ✗ day-2 adapter               rc={day2.returncode}/"
                        f"{day2_again.returncode} {(day2_again.stdout or day2.stderr)[-80:]!r}")
    day2_junk = cli(scoped_engine, "-install", "-codex", "-slug", "x")
    day2_nowhere = cli(product_engine, "-install", "-codex")
    if (day2_junk.returncode == 2 and "install-ambiguous" in day2_junk.stderr
            and day2_nowhere.returncode == 2 and "instance-missing" in day2_nowhere.stderr):
        held("the day-2 form guards its edges", "junk beside the host flags refuses "
             "named; outside an instance there is nothing to wire")
    else:
        failures.append(f"  ✗ day-2 guards                {day2_junk.returncode}/"
                        f"{day2_nowhere.returncode} {day2_nowhere.stderr[:80]!r}")

    import shutil as shutil_mod                                           # noqa: PLC0415
    gws = Path(tempfile.mkdtemp()) / "gws"
    gemini_probe = cli(product_engine, "-install", str(gws), "-gemini")
    if shutil_mod.which("gemini") is None:
        gemini_ok = (gemini_probe.returncode == 2 and "gemini-missing" in gemini_probe.stderr
                     and not (gws / ".pp").exists())
        detail = "no gemini on PATH: refused UPFRONT, nothing installed"
    else:
        gemini_ok = gemini_probe.returncode == 0 and "gemini-pp" in gemini_probe.stdout
        detail = "gemini present: launcher written, baseline composed or the miss said"
    if gemini_ok:
        held("gemini wiring guards its baseline", detail)
    else:
        failures.append(f"  ✗ gemini wire                 rc={gemini_probe.returncode} "
                        f"{(gemini_probe.stderr or gemini_probe.stdout)[:100]!r}")
    return 0
