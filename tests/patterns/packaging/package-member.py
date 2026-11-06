"""Scenario `package-member` -- the pattern `packaging/package-member`, played from its demonstration:
- a package's `user/` lands at the instance's root at the install: the base's layer first, then the
  one package's over it, silently; the member placed is fingerprinted at the manifest
- one bearer beside the base: two packages carrying `user/` refuse `user-packages-conflict`,
  nothing written
- `add` replaces a file still as it was placed silently -- the base's seed, or the same copy again
  after a `remove` -- and keeps an edited one as `<name>.old` before placing its own
- a base without `user/` places no member, and the run boots
"""
from __future__ import annotations

import hashlib

from conductor import Conductor, install, instance
from tests.harness import PATTERNS, support

DRAWER, PATTERN = "packaging", "package-member"
HOME = PATTERNS / DRAWER / PATTERN
OWED = {"manifests": ["ada.yaml", "bram.yaml", "hearth.yaml"],
        "users": ["ada", "bram", "hearth"]}
packaging = support(__file__, "source")


def _laid() -> dict:
    return {folder: sorted(path.name for path in (HOME / folder).glob("*")) for folder in OWED}


def _member(name: str) -> bytes:
    return (HOME / "users" / name / "MEMBER.md").read_bytes()


def _source(bench):
    """-> a source carrying ada and bram, and hearth: a base on the stand-in's procs with a `user/`."""
    hearth = packaging.parts(PATTERN, "hearth")
    hearth["procs"] = {path.stem: path.read_text(encoding="utf-8")
                       for path in sorted((bench.source() / "bases" / "kit" / "procs").glob("*.md"))}
    return packaging.source(bench, {name: packaging.parts(PATTERN, name) for name in ("ada", "bram")},
                            bases={"hearth": hearth})


def placed(bench, root) -> None:
    """The install places the base's layer, then the package's; one bearer beside the base."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made, _ = packaging.installed(bench, root, "hearth", [], base="hearth")
    member = (made / "MEMBER.md").read_bytes() if (made / "MEMBER.md").is_file() else b""
    if (member == _member("hearth")
            and instance.read(made).get("member_seed") == hashlib.sha256(member).hexdigest()):
        held("the base's layer lands at the root", "hearth's MEMBER.md at the instance's root, its "
             "fingerprint at the manifest")
    else:
        failures.append(f"  ✗ base layer                   {member[:40]!r} {instance.read(made).get('member_seed')}")

    layered, _ = packaging.installed(bench, root, "layered", ["ada"], base="hearth")
    if ((layered / "MEMBER.md").read_bytes() == _member("ada")
            and not (layered / "MEMBER.md.old").exists()):
        held("the package's layer over the base's", "hearth and ada: ada's MEMBER.md at the root, "
             "silently -- the base's layer is no rival")
    else:
        failures.append(f"  ✗ layered                      {(layered / 'MEMBER.md').read_bytes()[:40]!r}")

    target = bench.temp() / "rivals" / ".pp"
    expect("user-packages-conflict",
           lambda: install.install(root / "engine" / "pp.py", target, ["ada", "bram"], base="hearth"))
    if not target.exists():
        held("two bearers write nothing", "ada and bram both carry user/: refused before the "
             "instance's directory exists")
    else:
        failures.append(f"  ✗ rivals wrote                 {sorted(p.name for p in target.iterdir())}")


def added(bench, root) -> None:
    """`add` replaces a placed file silently and keeps an edited one as `.old`."""
    held, failures = bench.held, bench.failures
    made, member = packaging.installed(bench, root, "added", [], base="hearth")
    install.add_package(member, "ada")
    pristine = (made / "MEMBER.md").read_bytes() == _member("ada") and not (made / "MEMBER.md.old").exists()
    install.remove_package(member, "ada")
    install.add_package(member, "ada")
    same = (made / "MEMBER.md").read_bytes() == _member("ada") and not (made / "MEMBER.md.old").exists()
    if pristine and same:
        held("a placed file is replaced silently", "the base's seed swapped for ada's at add; ada "
             "removed then added again, the same copy: no .old")
    else:
        failures.append(f"  ✗ pristine add                 {pristine}/{same}")

    edited, editor = packaging.installed(bench, root, "edited", [], base="hearth")
    words = (edited / "MEMBER.md").read_bytes() + b"\nthe operator's own words\n"
    (edited / "MEMBER.md").write_bytes(words)
    install.add_package(editor, "ada")
    if ((edited / "MEMBER.md").read_bytes() == _member("ada")
            and (edited / "MEMBER.md.old").read_bytes() == words):
        held("an edited file is kept as .old", "the operator's member saved as MEMBER.md.old, ada's "
             "placed")
    else:
        failures.append(f"  ✗ edited add                   old={(edited / 'MEMBER.md.old').exists()}")


def bare(bench, root) -> None:
    """A base without `user/` places no member, and the run boots."""
    held, failures = bench.held, bench.failures
    made, member = packaging.installed(bench, root, "bare", [])
    engine = made / ".sys" / "engine" / "pp.py"
    conductor = Conductor(member, engine, "t")
    block = conductor.start(conductor.boot("BOOT.md"))
    conductor.forget()
    if (not (made / "MEMBER.md").exists() and "member_seed" not in instance.read(made)
            and block is not None):
        held("a base without user/ places no member", "the stand-in carries none: no MEMBER.md at the "
             "root, no fingerprint at the manifest; the run boots")
    else:
        failures.append(f"  ✗ bare base                    member={(made / 'MEMBER.md').exists()} "
                        f"block={block is not None}")


def scenario(bench) -> int:
    failures = bench.failures
    laid = _laid()
    if laid != OWED:
        failures.append(f"  ✗ the demonstration           {laid!r} -- owed {OWED!r}")
        return 0
    root = _source(bench)
    placed(bench, root)
    added(bench, root)
    bare(bench, root)
    return 0
