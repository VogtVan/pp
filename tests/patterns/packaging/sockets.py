"""Scenario `sockets` -- the pattern `packaging/sockets`, played from its demonstration:
- the base declares its own sockets and nothing else; a package's declaration joins the catalog
- a package opens `<proc>.<hook>` and its proc HOOKs it; another package names it qualified,
  `<package>.<proc>.<hook>`, and mounts there; the two-segment form names the base, which opens no
  such socket, and a qualified socket no proc hooks is an orphan: both refused `attach-unhooked`;
  a package document attached where no proc hooks refuses the same
- a proc HOOKing a socket its manifest does not declare refuses `socket-undeclared`
- two packages opening the same name keep two addresses
- a package names its own socket in three segments too (`socket-unknown` on two), and declares the
  minimum, never its own name (`contribution-malformed`)
"""
from __future__ import annotations

import re

from conductor import compiling, contributions, instance
from tests.harness import demonstrated, demos, manifests, support, vendor

DRAWER, PATTERN = "packaging", "sockets"
DEMOS = ("BARE_STAMP.md", "DANGLING.md", "GONE_STAMP.md", "PASS.md", "STAMP.md")
MANIFESTS = ("mute.yaml", "opener.yaml", "overqualified.yaml", "rider.yaml", "rival.yaml", "selfish.yaml")
CONTRIBUTIONS = "\n## The CONTRIBUTIONS\n"
ENTRY = re.compile(r"^- \*\*`([^`]+)`\*\* (\w+): (.*)$", re.M)
packaging = support(__file__, "source")


def _doc(name: str) -> str:
    return (demos(DRAWER, PATTERN) / name).read_text(encoding="utf-8")


def _listed(made) -> list[tuple[str, str]]:
    """-> the catalog's contributions as (package, kind)."""
    catalog = compiling.render_tools(made)
    section = catalog.split(CONTRIBUTIONS, 1)[1].split("\n## ", 1)[0] if CONTRIBUTIONS in catalog else ""
    return [(package, kind) for package, kind, _ in ENTRY.findall(section)]


def addressed(bench, declared) -> None:
    """The socket opened by one package, named by another."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("addressed")
    made = env.made
    kinds = [(one["package"], one["kind"]) for one in contributions.composed(made)]
    if kinds == [("kit", "sockets")] and _listed(made) == kinds:
        held("the base declares its own sockets", "the kit its sockets, nothing else, said by the catalog")
    else:
        failures.append(f"  ✗ base sockets                 {kinds} {_listed(made)}")
    vendor(made, "opener", declared["opener.yaml"], {"PASS": _doc("PASS.md")})
    for stamp, socket, rc in (("STAMP", "opener.pass.begin", 0), ("BARE_STAMP", "pass.begin", 2),
                              ("GONE_STAMP", "opener.gone.begin", 2)):
        packaging.unpin(made, "rider")
        vendor(made, "rider", declared["rider.yaml"], {stamp: _doc(f"{stamp}.md")})
        built = env.cli("-build")
        if rc == 0 and built.returncode == 0 and "STAMP.md" in instance.mounting(made, socket) \
                and ("opener", "sockets") in _listed(made):
            held(f"mount `{socket}`", "accepted: opener's socket, qualified by its package; the "
                 "catalog lists opener's declaration")
        elif rc == 2 and built.returncode == 2 and "attach-unhooked" in built.stderr:
            held(f"mount `{socket}`", "refused attach-unhooked")
        else:
            failures.append(f"  ✗ mount {socket:<22} rc={built.returncode} {built.stderr.strip()[-160:]!r}")
    packaging.unpin(made, "rider")
    vendor(made, "rider", declared["rider.yaml"], {"DANGLING": _doc("DANGLING.md")})
    expect("attach-unhooked", lambda: compiling.render_registry(made))


def declared_sockets(bench, declared) -> None:
    """What a manifest declares of its sockets, and what refuses."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    def building(*packages: tuple[str, str, dict]):
        made = bench.env("declaring").made
        for name, manifest, documents in packages:
            vendor(made, name, declared[manifest], documents)
        return made

    made = building(("mute", "mute.yaml", {"PASS": _doc("PASS.md")}))
    expect("socket-undeclared", lambda: compiling.build_tools(made))
    made = building(("opener", "opener.yaml", {"PASS": _doc("PASS.md")}), ("rival", "rival.yaml", {}))
    try:
        composed = contributions.validate(made)
        base = instance.base_of(made)
        opened = sorted(contributions.address(one["package"], socket, base)
                        for one in composed if one["kind"] == "sockets" and one["package"] != base
                        for socket in one["value"])
        if opened == ["opener.pass.begin", "rival.pass.begin"]:
            held("two packages open the same name", "opener.pass.begin and rival.pass.begin, two addresses")
        else:
            failures.append(f"  ✗ same name                    {opened}")
    except Exception as error:                                            # noqa: BLE001
        failures.append(f"  ✗ same name                    {error}")
    made = building(("selfish", "selfish.yaml", {"PASS": _doc("PASS.md")}))
    expect("socket-unknown", lambda: compiling.build_tools(made))
    made = building(("overqualified", "overqualified.yaml", {}))
    expect("contribution-malformed", lambda: compiling.build_tools(made))


def scenario(bench) -> int:
    failures = bench.failures
    found, declared = demonstrated(DRAWER, PATTERN), manifests(DRAWER, PATTERN)
    if found != sorted(DEMOS) or sorted(declared) != sorted(MANIFESTS):
        failures.append(f"  ✗ the demonstration           {found!r} {sorted(declared)!r} -- owed "
                        f"{sorted(DEMOS)!r} {sorted(MANIFESTS)!r}")
        return 0
    addressed(bench, declared)
    declared_sockets(bench, declared)
    return 0
