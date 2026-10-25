"""Scenario `adapter-wiring` -- what each host's wiring writes, and how its projections live:
- per host: claude's launcher pair and card, codex's config, rules and shared card, gemini's door,
  command and launcher, cursor's doors and allowlist -- each written once, then the operator's;
  the wired providers read back from the artifacts
- the doors follow the flags; a standing instance gains an adapter on day 2, its form guarded at
  the edges; gemini's wiring refuses upfront without its binary
- `-claude` from the console: the card, the permissions and the receipt in `settings.json`, an
  operator's own settings untouched, an operator's own CLAUDE.md untouched and said
- the flags cumulate: any order of claude, codex and cursor wires the same bytes
- the projections: the marble compiled once and served once, a card that follows its contract
  while pristine and lands a candidate once edited, a receipt with nothing to carry refuses, the
  codex merge byte-preserves foreign keys, the doctor replays every wired adapter
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from conductor import Conductor, compiling, discovery, render
from conductor import install as install_module
from tests.harness import SOURCE, body_of, cli, kept_document, load_script, pin_step


def _adapters(bench) -> Path:
    """-> the adapters directory of the source the bench installs from."""
    return install_module.product_root(bench.engine()) / "adapters"


def per_host(bench) -> None:
    """One instance wired by claude, codex and gemini in turn, then read back; cursor wires
    an instance of its own and joins the first one's shared card."""
    held, failures = bench.held, bench.failures
    adapters_root = _adapters(bench)
    wired_made = bench.env("wired").made
    wired_ws = wired_made.parent

    # --- claude: the launcher pair, the replace switch, written once --------------------
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

    # --- codex: config, rules and the cross-vendor card ---------------------------------
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

    # --- gemini: the one door, the inline command, the launcher -------------------------
    gemini_wire = load_script(adapters_root / "gemini" / "wire.py")
    gemini_wire.wire(wired_ws, wired_made)
    gdoor = wired_ws / "GEMINI.md"
    gcommand = wired_ws / ".gemini" / "commands" / "pp.toml"
    door_text = gdoor.read_text(encoding="utf-8") if gdoor.is_file() else ""
    command_text = gcommand.read_text(encoding="utf-8") if gcommand.is_file() else ""
    gemini_wire.wire(wired_ws, wired_made)
    if ("-new" in door_text and "conducted" in door_text and "skill" not in door_text and "`/pp`" not in door_text
            and not (wired_ws / ".gemini" / "settings.json").exists()
            and 'prompt = """' in command_text and "conducted" in command_text
            and (wired_ws / "gemini-pp").is_file()
            and "GEMINI_SYSTEM_MD" in ((wired_ws / "gemini-pp.cmd").read_text(encoding="utf-8")
                                       if (wired_ws / "gemini-pp.cmd").is_file() else "")
            and gdoor.read_text(encoding="utf-8") == door_text
            and gcommand.read_text(encoding="utf-8") == command_text):
        held("gemini wires door and card", "GEMINI.md is the one door -- run -new, nothing to invoke "
             "before --, no settings file; /pp serves the card inline; the launcher stands -- written once")
    else:
        failures.append(f"  ✗ gemini adapter              {door_text[:60]!r} {command_text[:60]!r}")

    if install_module.wired_providers(wired_ws) == ["claude", "codex", "gemini"]:
        held("wired providers read from artifacts",
             "claude+codex+gemini detected; cursor stays behind codex's shared card -- said")
    else:
        failures.append(f"  ✗ provider detection          {install_module.wired_providers(wired_ws)}")

    # --- cursor: every door, the shared card, the allowlist -----------------------------
    cursor_only = Path(tempfile.mkdtemp()) / "solo"
    cursor_made = install_module.install(bench.engine(), cursor_only / ".pp", [], doors=False)
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
    cursor_wire.wire(wired_ws, wired_made)   # the card already there from codex: shared, no clash
    doors = [(cursor_only / name).read_text(encoding="utf-8") for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md")]
    one_door = (len(set(doors)) == 1 and "-new" in doors[0]
                and all(word not in doors[0] for word in ("skill", "`/pp`", "command")))
    if (shared_ok and one_door and (wired_ws / ".agents" / "skills" / "pp" / "SKILL.md").is_file()
            and (wired_ws / ".cursor" / "permissions.json").is_file()):
        held("cursor opens every door", "-cursor writes ALL the doors (multi-model harness) -- ONE text, "
             "`-new` and no skill to invoke --, the cross-vendor card AND its terminalAllowlist "
             "prefix -- the shared card never blocks the permissions")
    else:
        failures.append(f"  ✗ cursor wire                 {shared_ok} one_door={one_door}")


def day_two(bench) -> None:
    """A codex-only workspace from the console, then wired again on day 2 by its own engine;
    gemini's probe installs a workspace of its own."""
    held, failures = bench.held, bench.failures
    console = bench.engine()

    # --- the doors follow the flags ------------------------------------------------------
    scoped = Path(tempfile.mkdtemp()) / "scoped"
    codex_only = cli(console, "-install", str(scoped), "-codex")
    if (codex_only.returncode == 0 and (scoped / "AGENTS.md").is_file()
            and not (scoped / "CLAUDE.md").exists()):
        held("doors follow the flags", "-codex alone: AGENTS.md stands, no CLAUDE.md litter; "
             "a bare install keeps the two generic doors")
    else:
        failures.append(f"  ✗ door scoping                rc={codex_only.returncode}")

    # --- day 2: the standing instance gains claude, codex answers already wired ----------
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
    day2_nowhere = cli(console, "-install", "-codex")
    if (day2_junk.returncode == 2 and "install-ambiguous" in day2_junk.stderr
            and day2_nowhere.returncode == 2 and "instance-missing" in day2_nowhere.stderr):
        held("the day-2 form guards its edges", "junk beside the host flags refuses "
             "named; outside an instance there is nothing to wire")
    else:
        failures.append(f"  ✗ day-2 guards                {day2_junk.returncode}/"
                        f"{day2_nowhere.returncode} {day2_nowhere.stderr[:80]!r}")

    # --- gemini without its binary refuses before anything is installed -----------------
    gws = Path(tempfile.mkdtemp()) / "gws"
    gemini_probe = cli(console, "-install", str(gws), "-gemini")
    if shutil.which("gemini") is None:
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


def console_claude(bench) -> None:
    """`-install -claude` from the console on a fresh workspace, read for its card, its
    permissions and its receipt; a second workspace carries the operator's own settings."""
    held, failures = bench.held, bench.failures
    hamlet = Path(tempfile.mkdtemp())
    console = bench.engine()
    claude_rc = cli(console, "-install", str(hamlet / "ws"), "-claude").returncode
    skill = hamlet / "ws" / ".claude" / "skills" / "pp" / "SKILL.md"
    settings_file = hamlet / "ws" / ".claude" / "settings.json"
    settings_text = (settings_file.read_text(encoding="utf-8")
                     if settings_file.is_file() else "")
    try:
        read = json.loads(settings_text) if settings_text else {}
    except ValueError:
        read = {}

    # --- the card and the permissions; the operator's own settings stay ------------------
    wired = (claude_rc == 0 and skill.is_file()
             and skill.read_text(encoding="utf-8") == install_module.card(hamlet / "ws" / ".pp")
             and "Bash(./pp:*)" in settings_text
             and ".pp/.sys/engine/pp.py:*" in settings_text
             and bool(read))                      # valid JSON, the allowlist in
    own = hamlet / "ws2" / ".claude" / "settings.json"
    own.parent.mkdir(parents=True)
    own.write_text('{"mine": true}', encoding="utf-8")   # the operator's own file
    own_door = hamlet / "ws2" / "CLAUDE.md"
    own_door.write_text("my own notes\n", encoding="utf-8")
    second = cli(console, "-install", str(hamlet / "ws2"), "-claude")
    untouched = (json.loads(own.read_text(encoding="utf-8")) == {"mine": True}
                 and own_door.read_text(encoding="utf-8") == "my own notes\n"
                 and f"{own_door} already exists" in second.stdout)
    if wired and untouched:
        held("-claude wires card and permissions", "the skill copied, Bash(./pp:*) allowed "
             "(the :* covers the run key) -- an operator's own settings stays untouched")
    else:
        failures.append(f"  ✗ -claude adapter           rc={claude_rc} wired={wired} untouched={untouched}")

    # --- the receipt rides the one channel of the editor's extension ---------------------
    if (claude_rc == 0 and read.get("env") == {"PP_MARBLE": "1"}
            and "Bash(./pp:*)" in (read.get("permissions") or {}).get("allow", [])):
        held("the receipt rides settings.json", "env.PP_MARBLE = \"1\" beside permissions.allow -- the one "
             "channel of the editor's extension")
    else:
        failures.append(f"  ✗ receipt                     rc={claude_rc} {read!r}")


def cumulated(bench) -> None:
    """Two fresh workspaces wired by claude, codex and cursor in opposite orders, compared
    byte for byte outside `.pp/`; gemini sits out, its wiring needs the binary."""
    held, failures = bench.held, bench.failures
    adapters_root = _adapters(bench)
    trees = []
    for order in (["claude", "codex", "cursor"], ["cursor", "codex", "claude"]):
        ws = Path(tempfile.mkdtemp()) / "cumul"
        with contextlib.redirect_stdout(io.StringIO()):
            made = install_module.install(bench.engine(), ws / ".pp", [])
            pin_step(made)
            for pname in order:
                load_script(adapters_root / pname / "wire.py").wire(ws, made)
        trees.append({str(p.relative_to(ws)): p.read_bytes()
                      for p in sorted(ws.rglob("*"))
                      if p.is_file() and ".pp" not in p.relative_to(ws).parts})
    if (trees[0] == trees[1]
            and ".agents/skills/pp/SKILL.md" in trees[0]
            and "GEMINI.md" in trees[0] and "claude-pp" in trees[0]
            and "pp" in trees[0]):
        held("flags cumulate without clobber",
             "claude+codex+cursor in either order -- byte-identical surface, one shared card")
    else:
        failures.append(f"  ✗ flag cumul                "
                        f"{sorted(set(trees[0]) ^ set(trees[1]))}")


def projections(bench) -> None:
    """One instance whose engine card is amended between wirings: the claude card and the
    codex config follow it, are edited by the operator, and are replayed by the doctor."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    adapters_root = _adapters(bench)
    made = bench.env("dna").made
    ws = made.parent
    system = (made / ".sys" / "system.md").read_text(encoding="utf-8")
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")

    def conductor() -> Conductor:
        return Conductor(member, made / ".sys" / "engine" / "pp.py", "t")

    # --- the marble: envelope then canon in one system.md, served once -------------------
    boot = render(conductor().start(conductor().boot("BOOT.md")))
    canon_head = body_of(kept_document(SOURCE / "engine", "PP"))[:80]
    marble_head = body_of(kept_document(SOURCE / "engine", "SYSTEM.COMMON"))[:60]
    if (canon_head in system
            and system.index(marble_head) < system.index(canon_head)
            and boot.count(canon_head) == 1
            and "INFORMATION — pp" not in boot):
        held("the ADN compiles and never doubles", "envelope then canon in ONE system.md; "
             "the boot carries it once as standing orders -- the card serve is gone")
    else:
        failures.append(f"  ✗ ADN compile                 canon-in-system={canon_head in system} "
                        f"boot-count={boot.count(canon_head)}")

    # --- the claude card: pristine follows, edited keeps and gets a candidate ------------
    claude = load_script(adapters_root / "claude" / "wire.py")
    claude.wire(ws, made)
    card = ws / ".claude" / "skills" / "pp" / "SKILL.md"
    engine_card = made / ".sys" / "engine" / "refs" / "PP.md"   # the engine's own card
    pristine_ok = card.read_text(encoding="utf-8") == install_module.card(made)

    def amend(line: str) -> None:
        engine_card.write_text(engine_card.read_text(encoding="utf-8").replace("", f"\n{line}", 1),
                               encoding="utf-8")

    amend("new law of the land")
    claude.wire(ws, made)
    refreshed = "new law of the land" in card.read_text(encoding="utf-8")
    card.write_text(card.read_text(encoding="utf-8") + "\nMY OWN NOTE\n", encoding="utf-8")
    amend("another law")
    told = claude.wire(ws, made)
    candidate = card.parent / (card.name + ".candidate")
    edited_kept = ("MY OWN NOTE" in card.read_text(encoding="utf-8")
                   and "another law" not in card.read_text(encoding="utf-8")
                   and candidate.is_file()
                   and "another law" in candidate.read_text(encoding="utf-8")
                   and any("candidate" in one for one in told))
    if pristine_ok and refreshed and edited_kept:
        held("a projection lives with provenance", "fresh copy byte-identical; a pristine "
             "card follows the new contract; an edited one is preserved -- the current "
             "projection lands beside it as a candidate, and the drift is said")
    else:
        failures.append(f"  ✗ projection lifecycle        {pristine_ok}/{refreshed}/"
                        f"{edited_kept}")

    # --- a receipt with no marble to carry ------------------------------------------------
    os.environ["PP_MARBLE"] = "1"
    try:
        (made / ".sys" / "system.md").rename(made / ".sys" / "system.hidden")
        expect("marble-missing", lambda: conductor().start(conductor().boot("BOOT.md")))
    finally:
        (made / ".sys" / "system.hidden").rename(made / ".sys" / "system.md")
        del os.environ["PP_MARBLE"]
    held("a lying receipt refuses", "PP_MARBLE declared with nothing compiled to "
         "carry -- the boot refuses rather than playing blind")

    # --- the codex config: foreign keys byte-preserved, an edited field never touched ----
    codex = load_script(adapters_root / "codex" / "wire.py")
    codex.wire(ws, made)
    config = ws / ".codex" / "config.toml"
    config.write_text(config.read_text(encoding="utf-8")
                      + '\n[model]\nprovider = "operator-custom"\n', encoding="utf-8")
    amend("third law")
    compiling.build_system(made)
    merged_told = codex.wire(ws, made)
    merged_text = config.read_text(encoding="utf-8")
    merge_ok = ('provider = "operator-custom"' in merged_text
                and "third law" in merged_text
                and any("byte-preserved" in one for one in merged_told))
    edited = re.sub(r'developer_instructions = """\n', 'developer_instructions = """\nOPERATOR PREFACE\n',
                    merged_text, count=1)
    config.write_text(edited, encoding="utf-8")
    amend("fourth law")
    compiling.build_system(made)
    edited_told = codex.wire(ws, made)
    edited_ok = ("OPERATOR PREFACE" in config.read_text(encoding="utf-8")
                 and "fourth law" not in config.read_text(encoding="utf-8")
                 and (config.parent / "config.toml.candidate").is_file()
                 and any("candidate" in one for one in edited_told))
    if merge_ok and edited_ok:
        held("the codex merge is hardened", "a pristine managed field follows the new "
             "contract with every foreign key byte-preserved; an edited one is never "
             "touched -- the fresh projection lands as candidate")
    else:
        failures.append(f"  ✗ codex merge                 {merge_ok}/{edited_ok} "
                        f"{merged_told!r}")

    # --- the doctor replays every wired adapter ------------------------------------------
    doc_told = install_module.doctor(member)
    if ("MY OWN NOTE" in card.read_text(encoding="utf-8")
            and any("candidate" in one or "refreshed" in one for one in doc_told)):
        held("doctor refreshes the projections", "the repair pass replays every wired "
             "adapter -- pristine surfaces follow, edited ones stay and are diagnosed")
    else:
        failures.append(f"  ✗ doctor refresh              {doc_told!r}")


def scenario(bench) -> int:
    per_host(bench)
    day_two(bench)
    console_claude(bench)
    cumulated(bench)
    projections(bench)
    return 0
