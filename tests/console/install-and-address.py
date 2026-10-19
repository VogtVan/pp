"""Scenario `install-and-address` -- an instance installed, named, given its console and addressed:
- `install -package <name>` extends an existing instance in place; beside a workspace or
  another flag it refuses `install-ambiguous`
- `install <workspace>` appends `.pp` itself; `-base <name>` composes on the named base
- the slug: the kebab of the workspace name or `-slug`, an invalid one refused;
  `instance.slug()` reads the declared slug or derives one
- the console: `pp` and `pp.cmd` at the root, machine-owned passthroughs; a skill named
  after a console verb is a lint; `help` lists the console's verbs; a foreign `pp` refuses
  the install and keeps its name
- the address: `--instance <dir>` and `PP_HOME` open a run on that instance from anywhere,
  the flag winning; a directory with no instance refuses; the vendored engine plays its own
  instance bare; the keyed call reads the flag wherever it stands
- `repo <name>` seeds a sibling with this instance's pins, providers and console
"""
from __future__ import annotations

import contextlib
import io

from conductor import compiling, console_command, contributions, discovery, install, instance, persistence
from tests.harness import PRODUCT_ENGINE, bench_key, cli, pin_step
import pp as pp_cli


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    engine = bench.engine()
    depot = bench.temp()

    # --- install -package: an existing instance extended, no recreation -------------------
    solo = install.install(engine, depot / "solo" / ".pp", [])
    pin_step(solo)
    solo_member = discovery.instance_member(solo / ".sys" / "engine" / "pp.py")
    added = install.add_package(solo_member, "wit")
    pinned = instance.pins(solo)
    if pinned.get("wit") and added.is_dir() and added.name == f"wit@{pinned['wit']}":
        held("install -package adds to an existing instance",
             "pinned, vendored, catalog recompiled -- no recreation")
    else:
        failures.append(f"  ✗ add_package                {pinned} {added}")
    expect("package-installed", lambda: install.add_package(solo_member, "wit"))
    expect("package-unknown", lambda: install.add_package(solo_member, "nope"))
    ambiguous = cli(engine, "-install", str(depot / "solo"), "-package", "wit")
    if ambiguous.returncode == 2 and "install-ambiguous" in ambiguous.stderr:
        held("install -package is exclusive", "a workspace or another flag alongside it refuses")
    else:
        failures.append(f"  ✗ install-ambiguous          rc={ambiguous.returncode} {ambiguous.stderr!r}")

    # --- install <workspace>: the instance directory appended; -base names the base -------
    suffixed = cli(engine, "-install", str(depot / "workspace"), "wit").returncode
    if (suffixed == 0 and instance.is_instance(depot / "workspace" / ".pp")
            and (depot / "workspace" / "CLAUDE.md").is_file()
            and not instance.is_instance(depot / "workspace")):
        held("install <workspace> suffixes .pp", "the bare argument is not the instance dir")
    else:
        failures.append(f"  ✗ install suffix            rc={suffixed} {list((depot / 'workspace').iterdir())}")
    based = cli(bench.source_with("kit-witness"), "-install", str(depot / "based"), "-base", "kit-witness")
    manifest = instance.read(depot / "based" / ".pp") if based.returncode == 0 else {}
    if (based.returncode == 0 and manifest.get("base") == "kit-witness"
            and list(manifest.get("packages") or {}) == ["kit-witness"]):
        held("-base names the base", "`-install <ws> -base kit-witness`: `base:` at the manifest, "
             "the composition is the witness alone")
    else:
        failures.append(f"  ✗ -base                     rc={based.returncode} {based.stderr[:120]!r} {manifest}")

    # --- the slug: the workspace's kebab by default, `-slug` overrides --------------------
    default_rc = cli(engine, "-install", str(depot / "My Workspace")).returncode
    default_slug = instance.read(depot / "My Workspace" / ".pp").get("slug")
    given_rc = cli(engine, "-install", str(depot / "other"), "-slug", "sw7-hub-infra").returncode
    given_slug = instance.read(depot / "other" / ".pp").get("slug")
    invalid = cli(engine, "-install", str(depot / "bad"), "-slug", "Not Kebab!")
    invalid_refused = invalid.returncode == 2 and "slug-invalid" in invalid.stderr
    if (default_rc == 0 and default_slug == "my-workspace"
            and given_rc == 0 and given_slug == "sw7-hub-infra"
            and invalid_refused and not (depot / "bad").exists()):
        held("the slug defaults and overrides", "kebab of the workspace name, or `-slug`, never both silently")
    else:
        failures.append(f"  ✗ slug                      default={default_slug!r} given={given_slug!r} "
                        f"invalid_refused={invalid_refused}")
    undeclared = bench.env("Undeclared Dir").made          # a manifest that says no slug
    stripped = instance.read(undeclared)
    stripped.pop("slug", None)
    instance.write(undeclared, stripped)
    if (instance.slug(depot / "other" / ".pp") == "sw7-hub-infra"
            and instance.slug(undeclared) == "undeclared-dir"):
        held("instance.slug() reads or derives", "declared in instance.yaml, or kebab of the workspace")
    else:
        failures.append(f"  ✗ instance.slug()           {instance.slug(undeclared)!r}")

    # --- the console: machine-owned passthroughs at the root ------------------------------
    made = bench.env("addressed").made
    root = made.parent
    sh, cmd = root / "pp", root / "pp.cmd"
    sh_text, cmd_text = sh.read_text(encoding="utf-8"), cmd.read_text(encoding="utf-8")
    if (console_command(windows=False) == "./pp" and console_command(windows=True) == ".\\pp"
            and sh_text == install.CONSOLE.format(meta=made.name) and '"$@"' in sh_text
            and cmd_text == install.CONSOLE_CMD.format(meta=made.name) and "%*" in cmd_text
            and bool(sh.stat().st_mode & 0o111)):
        held("the console is written", "pp + pp.cmd at the root, pure passthrough -- "
             "both spellings, exec bit set")
    else:
        failures.append(f"  ✗ console written           {sh_text!r}")

    (made / "procs" / "upgrade.md").write_text(
        "---\nname: upgrade\ndescription: a shadow\n---\nbody\n", encoding="utf-8")
    shadow_said = [one for one in compiling.lint(made) if "skill-shadows-verb" in one]
    (made / "procs" / "upgrade.md").unlink()
    if shadow_said and "`upgrade`" in shadow_said[0]:
        held("a shadowing name is told", "a reserved console verb on a skill is a named lint")
    else:
        failures.append(f"  ✗ shadow lint               {shadow_said}")

    spoken = io.StringIO()
    with contextlib.redirect_stdout(spoken):
        help_rc = pp_cli.main(["help"])
    usage = spoken.getvalue()
    listed = [verb for verb in sorted(contributions.SYSTEM_VERBS) if f"./pp {verb}" in usage]
    if (help_rc == 0 and usage.startswith(pp_cli.CONSOLE_HELP)
            and listed == sorted(contributions.SYSTEM_VERBS) and "admin" not in usage):
        held("help speaks to the operator", "the console's own usage, not the agent's")
    else:
        failures.append(f"  ✗ help                      rc={help_rc} listed={listed}")

    taken = depot / "takenws"
    taken.mkdir()
    (taken / "pp").write_text("#!/bin/sh\nthe operator's own tool\n", encoding="utf-8")
    expect("pp-name-taken", lambda: install.install(engine, taken / ".pp", []))
    if not instance.is_instance(taken / ".pp"):
        held("a stranger keeps its name", "no instance seeded over a foreign pp")
    else:
        failures.append("  ✗ pp-name-taken             the install wrote anyway")

    # --- the address: --instance and PP_HOME, from a directory foreign to the instance ----
    other = bench.env("other").made
    elsewhere = bench.temp()
    run = cli(PRODUCT_ENGINE, "--instance", str(made), "-new", cwd=elsewhere)
    slots = persistence.slots(made)
    if (run.returncode == 0 and "▌ INSTRUCTION" in run.stdout and len(slots) == 1
            and slots[0].is_relative_to(made / ".sys" / "state")):
        held("--instance opens the run there", "the product engine, called from a foreign "
             "directory, boots the addressed instance: one slot under its .sys/state")
    else:
        failures.append(f"  ✗ --instance                 rc={run.returncode} {run.stderr[:120]!r} {slots}")

    run = cli(PRODUCT_ENGINE, "-new", cwd=elsewhere, env={"PP_HOME": str(made)})
    if run.returncode == 0 and "▌ INSTRUCTION" in run.stdout and len(persistence.slots(made)) == 2:
        held("PP_HOME opens the run there", "a second run on the same instance, addressed "
             "by the variable alone")
    else:
        failures.append(f"  ✗ PP_HOME                    rc={run.returncode} {run.stderr[:120]!r}")

    run = cli(PRODUCT_ENGINE, "--instance", str(other), "-new", cwd=elsewhere,
              env={"PP_HOME": str(made)})
    if run.returncode == 0 and len(persistence.slots(other)) == 1 and len(persistence.slots(made)) == 2:
        held("the flag wins over the variable", "the run opened on the flag's instance, "
             "the variable's untouched")
    else:
        failures.append(f"  ✗ flag over variable         rc={run.returncode} "
                        f"{len(persistence.slots(other))}/{len(persistence.slots(made))}")

    run = cli(PRODUCT_ENGINE, "--instance", str(elsewhere), "-new", cwd=elsewhere)
    if run.returncode == 2 and "instance-missing" in run.stderr:
        held("instance-missing", "refused -- a directory carrying no instance.yaml is no address")
    else:
        failures.append(f"  ✗ instance-missing           rc={run.returncode} {run.stderr[:120]!r}")

    vendored = made / ".sys" / "engine" / "pp.py"
    run = cli(vendored, "-new", cwd=elsewhere)
    if (run.returncode == 0 and len(persistence.slots(made)) == 3
            and sh.read_text(encoding="utf-8") == install.CONSOLE.format(meta=made.name)):
        held("the vendored engine plays bare", "no flag, no variable: the installed engine "
             "conducts the instance it lives in, and the launcher is the install's text")
    else:
        failures.append(f"  ✗ vendored bare              rc={run.returncode} {run.stderr[:120]!r}")

    key = bench_key(made)
    run = cli(PRODUCT_ENGINE, key, "--instance", str(made), cwd=elsewhere)
    if run.returncode == 0 and "pp · run " + key in run.stdout:
        held("the keyed call is addressed too", "`<key> --instance <dir>` advances that "
             "instance's run: the flag is read wherever it stands")
    else:
        failures.append(f"  ✗ keyed form                 rc={run.returncode} {run.stderr[:120]!r}")

    # --- repo: a sibling seeded and wired like this workspace -----------------------------
    kit = instance.pins(made)["kit"]
    version = cli(vendored, "version", cwd=root)
    (root / ".claude" / "skills" / "pp").mkdir(parents=True)
    repo = cli(vendored, "repo", "sibling", cwd=root)
    sibling = root.parent / "sibling"
    if (version.returncode == 0 and f"kit {kit}" in version.stdout and "source " in version.stdout
            and repo.returncode == 0 and instance.is_instance(sibling / ".pp")
            and (sibling / "pp").is_file()
            and (sibling / ".claude" / "skills" / "pp" / "SKILL.md").is_file()
            and (sibling / "claude-pp").is_file()
            and instance.pins(sibling / ".pp") == instance.pins(made)):
        held("repo seeds a wired sibling", "this instance's packages, the detected "
             "providers, its own console")
    else:
        failures.append(f"  ✗ repo/version              {version.stdout!r} "
                        f"{repo.stdout!r} {repo.stderr!r}")
    return 0
