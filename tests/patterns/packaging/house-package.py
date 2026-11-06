"""Scenario `house-package` -- the pattern `packaging/house-package`, played from its demonstration
on one house and an agent that borrows its machine:
- `chores`, placed under the house's `packages/`, is added like a package of the product: pinned,
  copied into the machine, its CHORES offering its script; the script, standard library alone,
  writes in the instance `PP_HOME` names
- a name the product also carries refuses `package-duplicate`, nothing written
- the agent born under the house plays `chores`, and switches it off for itself alone
- `doctor` copies again a file changed at the same version, `upgrade` follows a new version,
  `remove` takes the package out of the house and of its agent
- on a second house, `develop chores` plays the package from its sources, no copy: a script
  changed under a run plays at its next call under both conductions, a document changed is
  read at the next call, a key added to its settings fragment reads at its default; a new run
  recompiles the catalog and the marble its changed sources feed; the agent plays the sources
  too; `doctor` and `upgrade` leave the pin, renew no run for a new `version:`; `develop off`
  copies it back at its version; a package of the product refuses `develop-product`
The script `pp-chores` is written at the test's time, as the house would write it.
"""
from __future__ import annotations

import os
import re

from conductor import Conductor, compiling, discovery, instance, persistence, settings
from tests.harness import cli, demonstrated, demos, manifests

DRAWER, PATTERN = "packaging", "house-package"
DEMOS = ("CHORES.md",)
NAME = "chores"
TAKEN = "wit"                 # a witness package of the bench's source: a name the product carries
VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
SCRIPT = '''import os
import sys
from pathlib import Path

LISTED = Path(os.environ["PP_HOME"]) / "chores.txt"


def main(arguments):
    verb, words = (arguments[0] if arguments else ""), arguments[1:]
    if verb == "list":
        print(LISTED.read_text(encoding="utf-8") if LISTED.exists() else "", end="")
        return 0
    if verb != "add" or not words:
        print("pp-chores: verb-unknown -- add <chore> | list", file=sys.stderr)
        return 2
    with LISTED.open("a", encoding="utf-8") as listed:
        listed.write(" ".join(words) + "\\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''


def _place(home, manifest: str, procs: dict[str, str], script: str | None = None) -> None:
    """A package written under the house's `packages/`, as its operator writes one."""
    (home / "procs").mkdir(parents=True)
    (home / "package.yaml").write_text(manifest, encoding="utf-8")
    for name, text in procs.items():
        (home / "procs" / name).write_text(text, encoding="utf-8")
    if script is not None:
        skill = home / "skills" / f"pp-{NAME}"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"---\nname: pp-{NAME}\ndescription: the house's list of "
                                        f"chores\n---\n\npp-{NAME} add <chore> | list\n", encoding="utf-8")
        (skill / f"pp-{NAME}.py").write_text(script, encoding="utf-8")


def _offers(meta, name: str) -> bool:
    """-> whether the compiled catalog of `meta` offers the document `name`."""
    return f"**`{name}`**" in (meta / ".sys" / "tools.md").read_text(encoding="utf-8")


def _state(meta) -> tuple:
    """-> what an `add` moves: the manifest's bytes and the vendor's listing."""
    return ((meta / instance.MANIFEST).read_bytes(),
            sorted(path.name for path in (meta / instance.VENDOR).iterdir()))


def _opened(member, console, path, principal: bool) -> Conductor:
    """-> a run opened on `path`, conducted by the LLM or by its principal."""
    spot = os.environ.get(VARIABLE)
    if principal:
        os.environ[VARIABLE] = "true"
    else:
        os.environ.pop(VARIABLE, None)
    try:
        opener = Conductor(member, console)
        opener.start(path)
        return opener
    finally:
        if spot is None:
            os.environ.pop(VARIABLE, None)
        else:
            os.environ[VARIABLE] = spot


def develop(bench) -> None:
    """A second house plays `chores` from its sources."""
    held, failures = bench.held, bench.failures
    env = bench.env("house-develop")
    house, ws, console = env.made, env.root, env.engine
    homes = house / instance.PACKAGES
    sources = homes / NAME
    chores_proc = (demos(DRAWER, PATTERN) / "CHORES.md").read_text(encoding="utf-8")
    _place(sources, manifests(DRAWER, PATTERN)[f"{NAME}.yaml"], {"CHORES.md": chores_proc}, SCRIPT)

    # --- the pin: played from its sources, nothing copied ------------------------------------------
    pinned = cli(console, "develop", NAME, cwd=ws)
    copies = [path.name for path in (house / instance.VENDOR).iterdir() if path.name.startswith(f"{NAME}@")]
    if (pinned.returncode != 0 or instance.pins(house).get(NAME) != instance.DEVELOP or copies
            or instance.resolve(house, "CHORES.md") != sources / "procs" / "CHORES.md"):
        failures.append(f"  ✗ develop                     rc={pinned.returncode} {pinned.stderr.strip()[-300:]!r} "
                        f"pins={instance.pins(house)} copies={copies}")
        return
    held("develop plays a house package from its sources", f"{NAME}: develop pinned, no {NAME}@* under the "
         "vendor, CHORES resolves in the house's packages/")

    # --- under a run: the script, a document, a setting -- no verb ---------------------------------
    member = discovery.instance_member(console)
    listed = house / "chores.txt"
    runs = {principal: _opened(member, console, sources / "procs" / "CHORES.md", principal)
            for principal in (False, True)}
    script = sources / "skills" / f"pp-{NAME}" / f"pp-{NAME}.py"
    script.write_text(SCRIPT.replace('" ".join(words)', '"v2 " + " ".join(words)'), encoding="utf-8")
    played = {principal: cli(console, run.run_id, "-s", f"pp-{NAME}", "add", "mop", cwd=ws,
                             env={VARIABLE: "true"} if principal else None)
              for principal, run in runs.items()}
    lines = listed.read_text(encoding="utf-8").splitlines() if listed.is_file() else []
    if all(one.returncode == 0 for one in played.values()) and lines == ["v2 mop", "v2 mop"]:
        held("a script changed under a run plays at its next call", "the runs the LLM and the principal "
             "conduct both played the new script, no doctor")
    else:
        failures.append(f"  ✗ the script under a run      {[(one.returncode, one.stderr.strip()[-200:]) for one in played.values()]} "
                        f"lines={lines}")
    marker = "Sweep the porch first."
    (sources / "procs" / "CHORES.md").write_text(chores_proc + f"\n{marker}\n", encoding="utf-8")
    fragment = sources / settings.FRAGMENT
    fragment.parent.mkdir(parents=True)
    fragment.write_text(f"---\n{NAME}_size: 3\n---\n", encoding="utf-8")
    body = instance.resolve(house, "CHORES.md").read_text(encoding="utf-8")
    if marker in body and settings.default_of(house, f"{NAME}_size") == "3":
        held("a document and a setting changed under a run read at the next call", "CHORES resolves to "
             f"its source with the new text; `{NAME}_size` reads at its fragment's default, SETTINGS untouched")
    else:
        failures.append(f"  ✗ document and setting        marker={marker in body} "
                        f"default={settings.default_of(house, f'{NAME}_size')!r}")

    # --- a new run: the catalog and the marble its sources feed, recompiled ------------------------
    (sources / "procs" / "WEEK.md").write_text("---\nname: WEEK\nkind: proc\ndescription: the week's "
                                               "chores\nproc: |\n  WORK\n---\n\nPlan the week.\n",
                                               encoding="utf-8")
    law = "Every chore is said done."
    (sources / "system").mkdir()
    (sources / "system" / "SYSTEM.COMMON.md").write_text(f"---\nname: SYSTEM.COMMON\nkind: doc\n---\n\n{law}\n",
                                                         encoding="utf-8")
    try:
        fresh = Conductor(member, console)
        fresh.start(fresh.boot("BOOT.md"))
        refused = ""
    except Exception as refusal:          # artifact-stale before the lot
        refused = getattr(refusal, "code", repr(refusal))
    marble = (house / ".sys" / "system.md").read_text(encoding="utf-8")
    if not refused and _offers(house, "WEEK") and law in marble:
        held("a new run recompiles what the sources feed", "the boot found the sources moved: tools.md "
             "offers WEEK and system.md carries the package's section, no artifact-stale")
    else:
        failures.append(f"  ✗ the new run                 refused={refused!r} week={_offers(house, 'WEEK')} "
                        f"law={law in marble}")

    # --- the agent of the house plays the sources --------------------------------------------------
    born = cli(console, "-install", "agents/a", cwd=ws)
    agent = ws / "agents" / "a" / house.name
    if (born.returncode == 0 and _offers(agent, "WEEK")
            and instance.resolve(agent, "CHORES.md") == sources / "procs" / "CHORES.md"):
        held("the agent plays the sources", "agents/a offers WEEK and resolves CHORES in the house's packages/")
    else:
        failures.append(f"  ✗ the borrower                rc={born.returncode} {born.stderr.strip()[-300:]!r}")

    # --- doctor and upgrade leave the pin; a new version renews no run -----------------------------
    standing = persistence.slot_of(house, runs[False].run_id)
    doctored = cli(console, "doctor", cwd=ws)
    manifest = sources / "package.yaml"
    manifest.write_text(re.sub(r"version: 0\.0\.1", "version: 0.0.3", manifest.read_text(encoding="utf-8")),
                        encoding="utf-8")
    upgraded = cli(console, "upgrade", cwd=ws)
    copies = [path.name for path in (house / instance.VENDOR).iterdir() if path.name.startswith(f"{NAME}@")]
    if (doctored.returncode == 0 and upgraded.returncode == 0 and not copies
            and any(NAME in line and instance.DEVELOP in line for line in doctored.stdout.splitlines())
            and instance.pins(house).get(NAME) == instance.DEVELOP
            and standing.is_file() and persistence.renewed(standing) is None):
        held("doctor and upgrade leave the pin", f"doctor says {NAME} develop, nothing copied; a new "
             "`version:` moves no pin and renews no run")
    else:
        failures.append(f"  ✗ doctor and upgrade          rc={doctored.returncode}/{upgraded.returncode} "
                        f"{doctored.stdout.strip()[-200:]!r} {upgraded.stderr.strip()[-200:]!r} copies={copies} "
                        f"renewed={persistence.renewed(standing) if standing.is_file() else 'gone'}")

    # --- develop off: back to a copy at its version; a package of the product refuses ---------------
    off = cli(console, "develop", NAME, "off", cwd=ws)
    again = cli(console, "develop", NAME, "off", cwd=ws)
    if (off.returncode == 0 and instance.pins(house).get(NAME) == "0.0.3"
            and again.returncode == 2 and "develop-absent" in again.stderr
            and (house / instance.VENDOR / f"{NAME}@0.0.3" / "procs" / "WEEK.md").is_file()):
        held("develop off copies it back", f"{NAME} pinned at 0.0.3, its copy under the vendor; "
             "played again, it refuses develop-absent")
    else:
        failures.append(f"  ✗ develop off                 rc={off.returncode} {off.stderr.strip()[-300:]!r} "
                        f"pins={instance.pins(house)}")
    before = (house / instance.MANIFEST).read_bytes()
    product = cli(console, "develop", TAKEN, cwd=ws)
    if (product.returncode == 2 and "develop-product" in product.stderr
            and (house / instance.MANIFEST).read_bytes() == before):
        held("a package of the product refuses", f"`develop {TAKEN}` refuses develop-product, the manifest unchanged")
    else:
        failures.append(f"  ✗ develop-product             rc={product.returncode} {product.stderr.strip()[-300:]!r}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("house-package")
    house, ws, console = env.made, env.root, env.engine
    homes = house / instance.PACKAGES
    chores_proc = (demos(DRAWER, PATTERN) / "CHORES.md").read_text(encoding="utf-8")
    _place(homes / NAME, manifests(DRAWER, PATTERN)[f"{NAME}.yaml"], {"CHORES.md": chores_proc}, SCRIPT)

    # --- added like a package of the product -------------------------------------------------------
    added = cli(console, "add", NAME, cwd=ws)
    copy = house / instance.VENDOR / f"{NAME}@0.0.1"
    if added.returncode != 0 or instance.pins(house).get(NAME) != "0.0.1" or not copy.is_dir():
        failures.append(f"  ✗ add of a house package      rc={added.returncode} {added.stderr.strip()[-300:]!r} "
                        f"pins={instance.pins(house)}")
        return len(failures)
    member = discovery.instance_member(console)
    opener = Conductor(member, console)
    first = opener.start(copy / "procs" / "CHORES.md")
    offered = [one.name for one in first.tools] if first is not None else []
    played = cli(console, opener.run_id, "-s", f"pp-{NAME}", "add", "sweep", cwd=ws)
    listed = house / "chores.txt"
    if (_offers(house, "CHORES") and f"pp-{NAME}" in offered and played.returncode == 0
            and listed.is_file() and listed.read_text(encoding="utf-8").split() == ["sweep"]):
        held("a house package is added and played", f"{NAME}@0.0.1 pinned and copied into the machine, "
             f"CHORES offers pp-{NAME}, whose script wrote in the house with the standard library alone")
    else:
        failures.append(f"  ✗ the house package plays     offered={offered} rc={played.returncode} "
                        f"{played.stderr.strip()[-300:]!r}")

    # --- a name the product carries: refused, nothing written --------------------------------------
    _place(homes / TAKEN, f"name: {TAKEN}\nversion: 0.0.1\ndescription: a twin\nrequires: [kit]\n", {})
    before = _state(house)
    twin = cli(console, "add", TAKEN, cwd=ws)
    if twin.returncode == 2 and "package-duplicate" in twin.stderr and _state(house) == before:
        held("a name the product carries is refused", f"`add {TAKEN}` refuses package-duplicate, the "
             "manifest and the vendor unchanged")
    else:
        failures.append(f"  ✗ the duplicate               rc={twin.returncode} {twin.stderr.strip()[-300:]!r}")
    for path in sorted((homes / TAKEN).rglob("*"), reverse=True):
        path.unlink() if path.is_file() else path.rmdir()
    (homes / TAKEN).rmdir()

    # --- the agent of the house plays it, and switches it off for itself ---------------------------
    born = cli(console, "-install", "agents/a", cwd=ws)
    agent = ws / "agents" / "a" / house.name
    offered_there = born.returncode == 0 and _offers(agent, "CHORES")
    if offered_there:
        settings.write(agent, f"package.{NAME}", "off")
        compiling.build_tools(agent)
    if offered_there and not _offers(agent, "CHORES") and _offers(house, "CHORES"):
        held("the agent plays the house's package, and switches it off", f"agents/a offers CHORES from the "
             f"machine it borrows; `package.{NAME}: off` in its SETTINGS takes it out there alone")
    else:
        failures.append(f"  ✗ the borrower                rc={born.returncode} {born.stderr.strip()[-300:]!r} "
                        f"offered={offered_there}")

    # --- doctor, upgrade, remove: the verbs of a package -------------------------------------------
    source_proc = homes / NAME / "procs" / "CHORES.md"
    source_proc.write_text(chores_proc + "\nOne chore per call.\n", encoding="utf-8")
    doctored = cli(console, "doctor", cwd=ws)
    if doctored.returncode == 0 and (copy / "procs" / "CHORES.md").read_bytes() == source_proc.read_bytes():
        held("doctor copies a changed file again", f"{NAME}@0.0.1 in the machine equals the house's file")
    else:
        failures.append(f"  ✗ doctor                      rc={doctored.returncode} {doctored.stderr.strip()[-300:]!r}")

    manifest = homes / NAME / "package.yaml"
    manifest.write_text(re.sub(r"version: 0\.0\.1", "version: 0.0.2", manifest.read_text(encoding="utf-8")),
                        encoding="utf-8")
    upgraded = cli(console, "upgrade", cwd=ws)
    if (upgraded.returncode == 0 and instance.pins(house).get(NAME) == "0.0.2"
            and (house / instance.VENDOR / f"{NAME}@0.0.2").is_dir() and not copy.exists()):
        held("upgrade follows a new version", f"{NAME} 0.0.1 -> 0.0.2, pinned and copied, the old copy gone")
    else:
        failures.append(f"  ✗ upgrade                     rc={upgraded.returncode} "
                        f"{upgraded.stderr.strip()[-300:]!r} pins={instance.pins(house)}")

    removed = cli(console, "remove", NAME, cwd=ws)
    if (removed.returncode == 0 and NAME not in instance.pins(house)
            and not any(path.name.startswith(f"{NAME}@") for path in (house / instance.VENDOR).iterdir())
            and not _offers(house, "CHORES") and (homes / NAME / "package.yaml").is_file()):
        held("remove takes it out", f"{NAME} unpinned and gone from the machine; the house's own folder kept")
    else:
        failures.append(f"  ✗ remove                      rc={removed.returncode} {removed.stderr.strip()[-300:]!r}")
    develop(bench)
    return len(failures)

