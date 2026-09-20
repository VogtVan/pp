"""Scenario `console-script` -- 1 case(s), in the monolith's order:
- le-console-dans-les-blocs: the workspace speaks `pp`, machine-owned
"""
from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
from conductor import Conductor, compiling, discovery, instance, persistence
from tests.harness import PRODUCT_ENGINE
from conductor import install as install_module
import pp as pp_cli


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    product_engine = PRODUCT_ENGINE
    # --- le-console-dans-les-blocs: the workspace speaks `pp`, machine-owned ----------
    import subprocess, sys as sys_mod                                    # noqa: PLC0415
    from conductor import console_command                                # noqa: PLC0415
    con_made = bench.env("conws").made
    con_ws = con_made.parent
    con_sh, con_cmd = con_ws / "pp", con_ws / "pp.cmd"
    sh_text = con_sh.read_text(encoding="utf-8")
    cmd_text = con_cmd.read_text(encoding="utf-8")
    if (console_command(windows=False) == "./pp" and console_command(windows=True) == ".\\pp"
            and 'exec uv run "$here/.pp/.sys/engine/pp.py" "$@"' in sh_text
            and "machine file" in sh_text and bool(con_sh.stat().st_mode & 0o111)
            and 'uv run "%~dp0.pp\\.sys\\engine\\pp.py" %*' in cmd_text
            and "machine file" in cmd_text):
        held("the console is written", "pp + pp.cmd at the root, pure passthrough -- "
             "both spellings, exec bit set")
    else:
        failures.append(f"  ✗ console written           {sh_text!r}")

    con_engine = con_made / ".sys" / "engine" / "pp.py"
    con_member = discovery.instance_member(con_engine)
    con_c = Conductor(con_member, discovery.siblings_around(con_member), con_engine)
    con_c.start(con_c.boot("BOOT.md"))
    slots_before = persistence.slots(con_made)
    con_sh.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
    doctor_told = install_module.doctor(con_member)
    doctor_again = install_module.doctor(con_member)
    if (con_sh.read_text(encoding="utf-8") == sh_text
            and any(str(con_sh) in one for one in doctor_told)
            and not any(str(con_sh) in one for one in doctor_again)
            and persistence.slots(con_made) == slots_before and slots_before):
        held("doctor repairs the console", "an edit is overwritten byte-stable; "
             "constant pins keep the standing run")
    else:
        failures.append(f"  ✗ doctor                    {doctor_told} / {doctor_again}")

    (con_made / "procs" / "upgrade.md").write_text(
        "---\nname: upgrade\ndescription: a shadow\n---\nbody\n", encoding="utf-8")
    shadow_said = [one for one in compiling.lint(con_made) if "skill-shadows-verb" in one]
    (con_made / "procs" / "upgrade.md").unlink()
    if shadow_said and "`upgrade`" in shadow_said[0]:
        held("a shadowing name is told", "a reserved console verb on a skill is a named lint")
    else:
        failures.append(f"  ✗ shadow lint               {shadow_said}")

    spoken_help = io.StringIO()
    with contextlib.redirect_stdout(spoken_help):
        help_rc = pp_cli.main(["help"])
    if (help_rc == 0 and "./pp upgrade" in spoken_help.getvalue()
            and "./pp doctor" in spoken_help.getvalue()
            and "admin" not in spoken_help.getvalue()
            and "The operator's console" in spoken_help.getvalue()):
        held("help speaks to the operator", "the console's own usage, not the agent's")
    else:
        failures.append(f"  ✗ help                      rc={help_rc}")

    if install_module.upgrade(con_member) == [] and persistence.slots(con_made) == slots_before:
        held("upgrade current is a statement", "nothing moved, nothing touched -- the run stands")
    else:
        failures.append("  ✗ upgrade no-op             touched a current instance")
    held_kit = instance.pins(con_made)["kit"]
    downgraded = instance.read(con_made)
    downgraded["packages"] = {**instance.pins(con_made), "kit": "0.0.1-past"}
    instance.write(con_made, downgraded)
    up_told = install_module.upgrade(con_member)
    if (f"kit 0.0.1-past -> {held_kit}" in up_told
            and "1 run(s) closed by the update" in up_told
            and instance.pins(con_made)["kit"] == held_kit
            and not persistence.slots(con_made)
            and (con_made / ".sys" / "vendor" / f"kit@{held_kit}").is_dir()):
        held("upgrade moves the pins", "source versions land, re-materialized; "
             "the closed runs are counted")
    else:
        failures.append(f"  ✗ upgrade                   {up_told}")

    taken_ws = Path(tempfile.mkdtemp()) / "takenws"
    taken_ws.mkdir(parents=True)
    (taken_ws / "pp").write_text("#!/bin/sh\nthe operator's own tool\n", encoding="utf-8")
    expect("pp-name-taken",
           lambda: install_module.install(product_engine, taken_ws / ".pp", []))
    if not instance.is_instance(taken_ws / ".pp"):
        held("a stranger keeps its name", "no instance seeded over a foreign pp")
    else:
        failures.append("  ✗ pp-name-taken             the install wrote anyway")

    proc_version = subprocess.run([sys_mod.executable, str(con_engine), "version"],
                                  cwd=con_ws, capture_output=True, text=True)
    (con_ws / ".claude" / "skills" / "pp").mkdir(parents=True)
    proc_repo = subprocess.run([sys_mod.executable, str(con_engine), "repo", "sibling"],
                               cwd=con_ws, capture_output=True, text=True)
    sib = con_ws.parent / "sibling"
    if (proc_version.returncode == 0 and f"kit {held_kit}" in proc_version.stdout
            and "source " in proc_version.stdout
            and proc_repo.returncode == 0 and instance.is_instance(sib / ".pp")
            and (sib / "pp").is_file()
            and (sib / ".claude" / "skills" / "pp" / "SKILL.md").is_file()
            and (sib / "claude-pp").is_file()
            and instance.pins(sib / ".pp") == instance.pins(con_made)):
        held("repo seeds a wired sibling", "this instance's packages, the detected "
             "providers, its own console")
    else:
        failures.append(f"  ✗ repo/version              {proc_version.stdout!r} "
                        f"{proc_repo.stdout!r} {proc_repo.stderr!r}")
    return 0
