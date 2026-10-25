"""Scenario `doc` -- the pattern `context/doc`, played from its demonstration:
- a `kind: doc` document is never played: a proc serves it by `SERVE`, its body rides the block of
  the proc's own step, and no frame opens on it
- mounted, its laws and its offers are in force at the step it joins, its body served when asked
- a document that carries a `proc:` outside a kind the engine plays is named by the build's lint;
  a proc that carries one is not
"""
from __future__ import annotations

from conductor import compiling
from tests.harness import body_of, codes, demonstrated, demos, plant

DRAWER, PATTERN = "context", "doc"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("CHARTER.md", "LOOKUP.md", "READER.md", "STRAY.md")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("doc", bare=True)
    plant(env, DRAWER, PATTERN, ("CHARTER.md", "LOOKUP.md", "READER.md"))
    charter = body_of(DEMO / "CHARTER.md")

    opener = env.conductor()
    read = opener.start(env.made / "procs" / "READER.md")
    served = dict(read.payloads) if read is not None else {}
    if (read is not None and read.document == "READER" and read.instruction.keyword == "INFER"
            and any(charter in text for text in served.values()) and "CHARTER" not in read.stack
            and "DC1" not in codes(read)):
        held("a doc is served, never played", "READER's SERVE brings CHARTER's body to READER's own step; "
             "no frame opens on CHARTER, its law stays out")
    else:
        failures.append(f"  ✗ the served doc              {read and read.stack!r} {sorted(served)}")
    opener.forget()

    opener = env.conductor()
    opener.start(env.made / "procs" / "LOOKUP.md")
    key = opener.run_id
    said = env.conductor(key).mount([{"doc": "CHARTER.md", "body": True}])
    view = env.conductor(key).peek()
    if ("DC1" in codes(view) and "LOOKUP" in [one.name for one in view.tools] and charter in said
            and view.document == "LOOKUP"):
        held("a mounted doc brings its laws and offers", "CHARTER mounted on LOOKUP's step: DC1 in force, "
             "its offer LOOKUP, its body served")
    else:
        failures.append(f"  ✗ the mounted doc             {codes(view)} {[one.name for one in view.tools]}")
    env.conductor(key).forget()

    env.write("plans/STRAY.md", (DEMO / "STRAY.md").read_text(encoding="utf-8"))
    said = [one for one in compiling.lint(env.made) if "carries a `proc:`" in one]
    if any("plans/STRAY.md" in one for one in said) and not any("READER" in one for one in said):
        held("a stray proc: is named, a proc's is not", "STRAY, a document with a `proc:` and no played "
             "kind, is named by the lint; READER, a proc, is not")
    else:
        failures.append(f"  ✗ the lint                    {said!r}")
    return 0
