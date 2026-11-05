"""Scenario `catalog` -- the contribution kinds and the catalog's sections:
- the contract of contributions: one witness per kind is accepted, composed in declaration
  order and listed by the catalog
- the « Undescribed » section: an overlay inherits its base's description, a proc of the
  instance's own without one is named
The two readings, the forms a package declares and the imposed forms are the pattern
`outputs/formats`'s; a cadence's and a command's own refusals and `tty` are the patterns
`automation/cadences` and `automation/commands`; the base's sockets, a package's and their
refusals `packaging/sockets`'; an unknown kind `packaging/manifest`'s; a socket hooked twice
`composition/hook`'s; a refused build writing nothing `composition-lint`'s.
"""
from __future__ import annotations

import re

import yaml

from conductor import compiling, contributions, instance

WITNESS = """name: witness
version: 0.0.1
description: a package that declares one contribution of every kind
requires: [kit]
contributes:
  sockets: [witness.ready]
  cadences:
    - {name: witness, anchor: witness_day, record: witness.jsonl, play: WITNESS.md, at: boot.initialize}
  checks:
    - {signal: witness-due, predicate: record-crossing, record: witness.jsonl, anchor: witness_day}
  commands:
    - {verb: witness, skill: pp-witness}
  events:
    signals:
      witness-due: {priority: 3}
"""
CONTRIBUTIONS = "\n## The CONTRIBUTIONS\n"
UNDESCRIBED = "\n## Undescribed\n"
ENTRY = re.compile(r"^- \*\*`([^`]+)`\*\* (\w+): (.*)$", re.M)


def _section(catalog: str, heading: str) -> str:
    """-> the body of the catalog's section opened by `heading`, empty when absent."""
    return catalog.split(heading, 1)[1].split("\n## ", 1)[0] if heading in catalog else ""


def _listed(catalog: str) -> list[tuple[str, str, str]]:
    """-> the catalog's contributions as (package, kind, what the line says)."""
    return ENTRY.findall(_section(catalog, CONTRIBUTIONS))


def _fields(said: str) -> dict[str, str]:
    """-> the `key=value` parts of an executed contribution's line."""
    return dict(part.split("=", 1) for part in said.split(", "))


def _declared(manifest: str, kind: str) -> dict[str, str]:
    """-> the first entry `manifest` declares under `kind`, its values as the catalog says them."""
    return {key: str(value) for key, value in yaml.safe_load(manifest)["contributes"][kind][0].items()}


def _pin(made, name: str, text: str) -> None:
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(text, encoding="utf-8")
    home = root / "skills" / "pp-witness"      # a command's skill is a SCRIPT of the
    home.mkdir(parents=True, exist_ok=True)    # composition: the build checks it stands
    (home / "SKILL.md").write_text("---\nname: pp-witness\ndescription: the witness skill\n"
                                   "---\n\nsay what you were given.\n", encoding="utf-8")
    (home / "pp-witness.py").write_text("import sys\nprint('witness:', *sys.argv[1:])\n",
                                        encoding="utf-8")
    procs = root / "procs"                     # the document the contributions name
    procs.mkdir(exist_ok=True)                 # stands in the package: a reference
    if not (procs / "WITNESS.md").is_file():   # resolves or the build refuses it
        (procs / "WITNESS.md").write_text(
            "---\nname: WITNESS\nkind: proc\ndescription: the witness proc\nproc: |\n"
            "  INFER\n---\n\nthe witness\n", encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


def contract(bench) -> None:
    """The contract of contributions: one witness per kind accepted, composed and listed."""
    held, failures = bench.held, bench.failures
    made = bench.env("contract").made
    _pin(made, "witness", WITNESS)
    composed = contributions.validate(made)
    kinds = [one["kind"] for one in composed if one["package"] == "witness"]
    listed = {kind: said for package, kind, said in _listed(compiling.render_tools(made))
              if package == "witness"}
    if (kinds == ["sockets", "cadences", "checks", "commands", "events"]
            and list(listed) == kinds
            and _fields(listed["cadences"]) == _declared(WITNESS, "cadences")):
        held("one witness per kind accepted", f"{len(kinds)} kinds composed in declaration "
             "order, the catalog says where the package plugs in")
    else:
        failures.append(f"  ✗ witness kinds                {kinds} {listed}")


def undescribed(bench) -> None:
    """The « Undescribed » section names what no entry of the catalog describes."""
    held, failures = bench.held, bench.failures
    env = bench.env("undescribed")
    env.write("procs/TURN.md", "---\nname: TURN\ntools: |\n  +nothing\n---\n")
    env.write("procs/BARE.md", "---\nname: BARE\nkind: proc\nproc: |\n  INFER\n---\n\nbare\n")
    catalog = compiling.render_tools(env.made)
    section = _section(catalog, UNDESCRIBED)
    if section and "`BARE`" in section and "`TURN`" not in section and "**`TURN`**" in catalog:
        held("an overlay inherits its base's description", "TURN described by the base, its overlay not "
             "named; the bare proc of the instance is named")
    else:
        failures.append(f"  ✗ undescribed                 {section.strip()[:120]!r}")


def scenario(bench) -> int:
    contract(bench)
    undescribed(bench)
    return 0
