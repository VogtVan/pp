"""Scenario `contributions` -- the CONTRACT of contributions (plan pp-split, batch
le-contrat-des-contributions):
- today's manifests declare nothing and the build is byte-identical
- one witness per kind is accepted and the catalog says it
- each refusal plays by name, nothing written (a command's verb keeps the grammar, its skill is a script)
"""
from __future__ import annotations

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


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("contract").made

    # --- the kit declares its sockets and nothing else; plan declares nothing ------
    before = compiling.render_tools(made)
    kinds = [(one["package"], one["kind"]) for one in contributions.composed(made)]
    if (kinds == [("kit", "sockets")] + [("kit", "checks")] * 2
            + [("kit", "events")] and "`kit`** sockets:" in before):
        held("the base declares what it carries", "the kit its sockets, its two "
             "card-drift checks and its protocol events -- nothing else")
    else:
        failures.append(f"  ✗ kit sockets                  {kinds}")

    # --- one witness per kind: accepted, composed in order, said by the catalog -----
    _pin(made, "witness", WITNESS)
    composed = contributions.validate(made)
    kinds = [one["kind"] for one in composed if one["package"] == "witness"]
    catalog = compiling.render_tools(made)
    if (kinds == ["sockets", "cadences", "checks", "commands", "events"]
            and "## The CONTRIBUTIONS" in catalog
            and "`witness`** cadences: name=witness" in catalog):
        held("one witness per kind accepted", f"{len(kinds)} kinds composed in declaration "
             "order, the catalog says where the package plugs in")
    else:
        failures.append(f"  ✗ witness kinds                {kinds} {'CONTRIBUTIONS' in catalog}")
    built = compiling.build_tools(made)
    if built.is_file() and "witness" in built.read_text(encoding="utf-8"):
        held("the build accepts the witness", "tools.md written, the contributions listed")
    else:
        failures.append("  ✗ witness build                tools.md misses the witness")

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
    _pin(made, "rival", "name: rival\nversion: 0.0.1\nrequires: []\ncontributes:\n"
                        "  sockets: [witness.ready]\n")
    # the SAME declaration in two packages: two addresses, no collision -- the namespace
    # is what retired `socket-taken`
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
        held("a refusal writes nothing", "tools.md byte-identical after eight refused builds")
    else:
        failures.append("  ✗ refusal wrote                tools.md changed under a refusal")
    return 0
