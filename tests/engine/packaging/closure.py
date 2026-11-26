"""Scenario `closure` -- what `remove` refuses, where a source carries its base, and the pin
`upgrade` lets go (plan pp-split, batch la-resolution-des-dependances; plan pp-fixes, s.1698):
- remove refuses a name the instance does not pin
- a base lives under bases/: a source whose kit sits at the root is not the product
- (g1) a package the source no longer carries: `upgrade` lets its pin go -- the manifest without
  it, its bundle out of the vendor, its records kept, its keys under `unowned`, one line naming it
- (g2) the same, the upgrade DELEGATED to the source's engine (another version than the one in place)
- (g3) a package gone that a kept pin still requires at the source refuses `package-unknown`, and
  the base gone refuses the same: the manifest the same to the byte
- (g4) a package of the HOUSE whose folder is gone, pinned at its version and played from its
  sources (`develop`): the upgrade lets its pin go as in (g1)
The closure, `add`, the requires topology, `package-required-by` and the closed reading are the
pattern `packaging/manifest`'s; the keys a removal leaves `unowned` `packaging/settings-fragment`'s;
the record a removal leaves `packaging/seed`'s; the base `remove` refuses `packaging/base`'s.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from conductor import discovery, install, instance, store
from tests.harness import INSTANCE, cli

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.initialize, turn.begin, turn.end]\n")


def scenario(bench) -> int:
    expect = bench.expect
    env = bench.env("closed")
    kit_version = instance.pins(env.made)["kit"]

    # --- remove refuses a name nobody pinned ---------------------------------------------
    expect("package-unpinned", lambda: install.remove_package(env.member, "nowhere"))

    # --- a base lives under bases/, a package under packages/, nothing at the root --------
    # (batch les-bases-sous-un-toit): a source whose kit sits at the root is not the product
    rooted = Path(tempfile.mkdtemp()) / "rooted"
    (rooted / "kit").mkdir(parents=True)
    (rooted / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
    expect("package-unknown", lambda: install.package_dir(rooted, "kit", env.made))
    _gone(bench)
    return len(bench.failures)


def _unowned(meta: Path) -> list[str]:
    """-> the keys SETTINGS files under the `unowned` mark, in order."""
    lines = (meta / "SETTINGS.md").read_text(encoding="utf-8").splitlines()
    lines = lines[1:lines.index("---", 1)]                 # the front matter
    mark = install.SEPARATOR.format(name="unowned")
    at = lines.index(mark) + 1 if mark in lines else len(lines)
    keys = []
    for line in lines[at:]:
        if line.startswith(install.SEPARATOR.split("{")[0]):
            break
        if ":" in line and not line.startswith("#"):
            keys.append(line.split(":", 1)[0].strip())
    return keys


def _dropped(meta: Path, name: str, version: str, told: list[str], record: str = "operations",
             key: str = "continuity_recall_days") -> list[str]:
    """-> what is wrong with `name@version` let go at `meta` -- [] when the pin, the bundle and
    the keys left, the record `record` stayed -- a record of the store when its name carries no
    suffix, its entry still there; a seeded file otherwise --, `key` stands under `unowned` and
    one line named it."""
    wrong = []
    if name in instance.pins(meta):
        wrong.append(f"pinned {instance.pins(meta)}")
    if (instance.bundle_home(meta) / f"{name}@{version}").exists():
        wrong.append("bundle still vendored")
    kept = ((meta / instance.RECORDS / record).is_file() if "." in record
            else store.of(meta).count(record) == 1)
    if not kept:
        wrong.append("records gone")
    if key not in _unowned(meta):
        wrong.append(f"unowned={_unowned(meta)}")
    if len([line for line in told if line.split(" ", 1)[0] == name]) != 1:
        wrong.append(f"told={told}")
    return wrong


def _house(meta: Path, name: str) -> Path:
    """A package of the house written under `meta`'s `packages/`: a key of its own and a record
    it seeds. -> its folder."""
    home = instance.house_packages(meta) / name
    (home / "settings").mkdir(parents=True)
    (home / "seed").mkdir()
    (home / instance.PACKAGE_MANIFEST).write_text(
        f"name: {name}\nversion: 0.0.1\ndescription: a package of the house\nrequires: [kit]\n",
        encoding="utf-8")
    (home / "settings" / "SETTINGS.md").write_text(
        f"---\nname: SETTINGS\nkind: fragment\npackage: {name}\ndescription: {name}'s key\n"
        f"{name}_depth: 2\ntypes: |\n  {name}_depth  natural\n---\n## {name.title()}\n",
        encoding="utf-8")
    (home / "seed" / f"{name}.jsonl").write_text("", encoding="utf-8")
    return home


def _gone(bench) -> None:
    """(g1-g4) the pins a source no longer carries, at the upgrade."""
    held, failures, expect = bench.held, bench.failures, bench.expect
    engine = bench.source_with("kit")                 # a copy of the product: packages may leave it
    source = engine.parent.parent
    homes = bench.temp()
    made = install.install(engine, homes / "a" / INSTANCE, ["continuity", "doc"])
    other = install.install(engine, homes / "b" / INSTANCE, ["continuity"])
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
    version = instance.pins(made)["continuity"]
    for one in (made, other):            # the record continuity wrote, which its removal keeps
        store.of(one).append("operations", {"entry": "an operation before the removal"})
    aside = bench.temp()

    # --- (g1) the source lets continuity go: the upgrade lets its pin go -------------------------
    shutil.move(source / "packages" / "continuity", aside / "continuity")
    try:
        told = install.upgrade(member)
        wrong = _dropped(made, "continuity", version, told)
    except Exception as error:                                            # noqa: BLE001
        wrong = [f"{type(error).__name__}: {error}"]
    if not wrong:
        held("(g1) the gone package let go", f"continuity@{version}: unpinned, its bundle out, "
             "the record operations kept, continuity_* under unowned, one line names it")
    else:
        failures.append(f"  ✗ (g1) the gone package       {'; '.join(wrong)[:400]}")

    # --- (g3) a gone prerequisite of a kept pin, and the base gone: refused, nothing written ------
    manifest = made / instance.MANIFEST
    for gone, home in (("steering", source / "packages"), ("kit", source / "bases")):
        before = manifest.read_bytes()
        shutil.move(home / gone, aside / gone)
        expect("package-unknown", lambda: install.upgrade(member))
        shutil.move(aside / gone, home / gone)
        if manifest.read_bytes() == before:
            held(f"(g3) {gone} gone: nothing written", "the manifest the same to the byte")
        else:
            failures.append(f"  ✗ (g3) {gone} gone             the manifest moved: {instance.pins(made)}")

    # --- (g4) a package of the house whose folder is gone, at its version, then from its sources --
    for name, develop in (("attic", False), ("porch", True)):
        try:
            home = _house(made, name)
            install.add_package(member, name)
            if develop:
                install.develop(member, name)
            pinned = instance.pins(made)[name]
            shutil.rmtree(home)
            told = install.upgrade(member)
            wrong = _dropped(made, name, pinned, told, f"{name}.jsonl", f"{name}_depth")
        except Exception as error:                                        # noqa: BLE001
            pinned, wrong = "", [f"{type(error).__name__}: {error}"]
        if not wrong:
            held(f"(g4) the house's {name} let go", f"pinned {pinned}, its folder gone: unpinned, no "
                 f"bundle, {name}.jsonl kept, {name}_depth under unowned, one line names it")
        else:
            failures.append(f"  ✗ (g4) the house's {name}      {'; '.join(wrong)[:400]}")

    # --- (g2) the same, the upgrade delegated to the source's engine ------------------------------
    leaf = source / "engine" / "conductor" / "core" / "version.py"
    leaf.write_text(leaf.read_text(encoding="utf-8").replace('VERSION = "', 'VERSION = "9.', 1),
                    encoding="utf-8")
    upgraded = cli(other / ".sys" / "engine" / "pp.py", "upgrade", cwd=other.parent)
    told = [line.removeprefix("pp: ") for line in upgraded.stdout.splitlines()]
    wrong = ([f"rc={upgraded.returncode} {upgraded.stderr.strip()[-300:]}"] if upgraded.returncode
             else _dropped(other, "continuity", version, told))
    if not wrong:
        held("(g2) let go by delegation", f"the source's engine {install.source_version(source)} "
             "played the upgrade: continuity unpinned, its bundle out, its records and keys kept")
    else:
        failures.append(f"  ✗ (g2) by delegation          {'; '.join(wrong)[:400]}")
