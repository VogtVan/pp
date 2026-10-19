"""Scenario `catalog` -- the contribution kinds and the catalog's sections:
- the contract of contributions: the base declares its sockets alone, one witness per kind is
  accepted and listed by the catalog, a command's `tty` is a field, each refusal plays by name
  and writes nothing, two packages open the same socket name
- the « Undescribed » section: an overlay inherits its base's description, a proc of the
  instance's own without one is named
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
    - {name: witness, anchor: witness_day, record: witness.jsonl, play: WITNESS.md, at: boot.ready}
  checks:
    - {signal: witness-due, predicate: record-crossing, record: witness.jsonl, anchor: witness_day}
  commands:
    - {verb: witness, skill: pp-witness}
  events:
    signals:
      witness-due: {priority: 3}
"""
TTY = WITNESS.replace("{verb: witness, skill: pp-witness}",
                      "{verb: witness, skill: pp-witness, tty: true}")
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
    """The contract of contributions: each kind accepted and listed, each refusal by name."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("contract").made

    # --- the kit declares its sockets and nothing else; plan declares nothing ------
    before = compiling.render_tools(made)
    kinds = [(one["package"], one["kind"]) for one in contributions.composed(made)]
    listed = [(package, kind) for package, kind, _ in _listed(before)]
    if kinds == [("kit", "sockets")] and listed == kinds:
        held("the base declares what it carries", "the kit its sockets -- nothing else: the "
             "card-drift checks and the protocol events are the engine's own")
    else:
        failures.append(f"  ✗ kit sockets                  {kinds} {listed}")

    # --- one witness per kind: accepted, composed in order, said by the catalog -----
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
    built = compiling.build_tools(made)
    if built.is_file() and any(package == "witness"
                               for package, _, _ in _listed(built.read_text(encoding="utf-8"))):
        held("the build accepts the witness", "tools.md written, the contributions listed")
    else:
        failures.append("  ✗ witness build                tools.md misses the witness")

    # --- a command at the terminal: `tty: true` is a field, the catalog says it --------
    _pin(made, "witness", TTY)
    command = next(one for one in contributions.composed(made)
                   if one["package"] == "witness" and one["kind"] == "commands")
    said = [_fields(said) for package, kind, said in _listed(compiling.render_tools(made))
            if (package, kind) == ("witness", "commands")]
    if command.get("tty") is True and said == [_declared(TTY, "commands")]:
        held("`tty: true` is a field of commands", "accepted at the build, the catalog says "
             "`tty=True` on the entry's line")
    else:
        failures.append(f"  ✗ tty accepted                 {command} {said}")
    _pin(made, "witness", WITNESS)
    built = compiling.build_tools(made)

    # --- the refusals, by name, nothing written --------------------------------------
    stamp = built.read_bytes()

    def rewrite(text: str):
        _pin(made, "witness", text)
        return lambda: compiling.build_tools(made)

    expect("contribution-kind-unknown",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  widgets: []\n"))
    expect("contribution-malformed",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  cadences:\n"
                   "    - {name: witness, anchor: witness_day, record: witness.jsonl}\n"))
    expect("socket-unknown",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  cadences:\n"
                   "    - {name: witness, anchor: witness_day, record: witness.jsonl,\n"
                   "       play: WITNESS.md, at: nowhere.socket}\n"))
    expect("command-taken",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  commands:\n"
                   "    - {verb: doctor, skill: pp-witness}\n"))
    expect("contribution-malformed",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  commands:\n"
                   "    - {verb: decade, skill: pp-witness}\n"))   # six hex digits: a key's form
    expect("command-skill-unknown",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  commands:\n"
                   "    - {verb: witness, skill: pp-nowhere}\n"))
    expect("contribution-malformed",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n  commands:\n"
                   "    - {verb: witness, skill: pp-witness, tty: oui}\n"))   # `tty` is true or false
    _pin(made, "rival", "name: rival\nversion: 0.0.1\nrequires: []\ncontributes:\n"
                        "  sockets: [witness.ready]\n")
    # the SAME declaration in two packages: two addresses, no collision -- the namespace
    # keeps each package's sockets apart
    rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n"
            "  sockets: [witness.ready]\n")
    contributions.validate(made)
    held("two packages open the same name", "rival.witness.ready and witness.witness.ready")
    pins = instance.read(made)
    del pins["packages"]["rival"]
    instance.write(made, pins)
    (made / ".sys" / "vendor" / "witness@0.0.1" / "procs" / "WITNESS.md").write_text(
        "---\nname: WITNESS\nkind: proc\ndescription: the witness proc\nproc: |\n"
        "  HOOK witness.ready\n---\n\nthe witness\n", encoding="utf-8")
    # a package addresses its OWN socket in three segments too: the count settles the reading
    expect("socket-unknown",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n"
                   "  sockets: [witness.ready]\n  cadences:\n"
                   "    - {name: witness, anchor: witness_day, record: witness.jsonl,\n"
                   "       play: WITNESS.md, at: witness.ready}\n"))
    # a declaration carries the MINIMUM -- `<proc>.<hook>`, never the package's own name
    expect("contribution-malformed",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n"
                   "  sockets: [witness.witness.ready]\n"))
    (made / ".sys" / "vendor" / "witness@0.0.1" / "procs" / "TWICE.md").write_text(
        "---\nname: TWICE\nkind: proc\ndescription: the doubling proc\nproc: |\n"
        "  HOOK twice.ready\n  HOOK twice.ready\n---\n\ntwice\n", encoding="utf-8")
    expect("socket-doubled",
           rewrite("name: witness\nversion: 0.0.1\nrequires: []\ncontributes:\n"
                   "  sockets: [witness.ready, twice.ready]\n"))
    if built.read_bytes() == stamp:
        held("a refusal writes nothing", "tools.md byte-identical after nine refused builds")
    else:
        failures.append("  ✗ refusal wrote                tools.md changed under a refusal")


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
