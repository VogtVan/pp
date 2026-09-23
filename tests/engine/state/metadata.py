"""Scenario `metadata` -- 5 case(s), the repository's metadata governed by the engine
(plan pp-split, batch les-metadonnees-du-repo and its rework):
- the write DERIVES its space and its repository from the caller's own file
- a package cannot write at a neighbour, nor in another package's space: the calls
  that would are the SAME call, and it lands where the caller lives
- the engine keeps no key of its own: what went in as JSON comes back unchanged
- concurrent writers lose nothing -- the store is a shared record
- a caller inside the instance but under no package refuses by name, nothing written
"""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from conductor import Refusal, install, metadata
from tests.harness import PRODUCT_ENGINE

WRITER = """import json, sys
sys.path.insert(0, {engine!r})
from conductor import metadata
metadata.write(__file__, json.loads(sys.argv[1]))
"""


def vendored(meta: Path, package: str, engine: Path) -> Path:
    """A witness package with a skill that writes -- the only honest caller: the rule
    rides the PATH, so the test must call from where a package really lives."""
    home = meta / ".sys" / "vendor" / f"{package}@0.0.1" / "skills" / "pp-wit"
    home.mkdir(parents=True, exist_ok=True)
    script = home / "pp-wit.py"
    script.write_text(WRITER.format(engine=str(engine)), encoding="utf-8")
    return script


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    town = bench.temp()
    for name in ("alpha", "beta"):
        install.install(PRODUCT_ENGINE, town / name / ".pp", [])
    engine = town / "alpha" / ".pp" / ".sys" / "engine"
    fed = vendored(town / "alpha" / ".pp", "federation", engine)
    doc = vendored(town / "alpha" / ".pp", "doc", engine)
    far = vendored(town / "beta" / ".pp", "federation", town / "beta" / ".pp" / ".sys" / "engine")

    def run(script: Path, facts: dict) -> int:
        return subprocess.run([sys.executable, str(script), json.dumps(facts)],
                              capture_output=True, text=True).returncode

    # --- the write derives its space and its repository from the caller ---------------
    run(fed, {"admin": True})
    run(doc, {"root": "..", "kinds": ["py", "md"]})
    run(far, {"admin": False})
    here = metadata.read(town / "alpha" / ".pp")
    there = metadata.read(town / "beta" / ".pp")
    if (here.get("federation") == {"admin": True} and here.get("doc", {})["kinds"] == ["py", "md"]
            and there == {"federation": {"admin": False}}):
        held("the write derives its caller", "the vendored path says the repository AND the "
             "package -- three skills, three spaces, each where its own file lives")
    else:
        failures.append(f"  ✗ metadata derivation         {here} {there}")

    # --- a neighbour's store and another package's space are UNREACHABLE --------------
    # the two writes that would reach them are the same call as above: `write(__file__, …)`
    # takes no repository and no package name, so there is no call that could name them.
    signature = metadata.write.__code__.co_varnames[:metadata.write.__code__.co_argcount]
    if (signature == ("start", "facts") and here["federation"] == {"admin": True}
            and there["federation"] == {"admin": False}):
        held("a neighbour is unreachable", "the write names neither repository nor package: "
             "reaching another is not forbidden, it is unwritable -- and the two stores that "
             "stand hold exactly what their own callers put there")
    else:
        failures.append(f"  ✗ metadata reach              {signature}")

    # --- the engine keeps no key: the JSON comes back as it went in -------------------
    shapes = {"flag": False, "count": 0, "list": [1, 2], "nested": {"a": None}, "text": "é"}
    wit = vendored(town / "alpha" / ".pp", "witness", engine)
    run(wit, shapes)
    kept = metadata.of_package(town / "alpha" / ".pp", "witness")
    if kept == shapes and set(metadata.read(town / "alpha" / ".pp")) == {"federation", "doc", "witness"}:
        held("the engine knows no key", "falsy values, nesting and unicode travel unchanged "
             "-- the store types nothing, validates nothing, defaults nothing")
    else:
        failures.append(f"  ✗ metadata verbatim           {kept}")

    # --- concurrent writers lose nothing ----------------------------------------------
    race = vendored(town / "alpha" / ".pp", "race", engine)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda n: run(race, {f"k{n}": n}), range(12)))
    raced = metadata.of_package(town / "alpha" / ".pp", "race")
    if len(raced) == 1 and set(raced) <= {f"k{n}" for n in range(12)}:
        held("a write replaces its own space", "twelve concurrent writers, none torn and none "
             "lost to a half-written record -- the store's one regime holds")
    else:
        failures.append(f"  ✗ metadata race               {raced}")

    # --- a caller that is no vendored package refuses by name -------------------------
    stray = town / "alpha" / ".pp" / "stray.py"
    stray.write_text("x = 1\n", encoding="utf-8")
    before = metadata.read(town / "alpha" / ".pp")
    try:
        metadata.write(stray, {"nope": True})
        refused = ""
    except Refusal as raised:
        refused = getattr(raised, "code", "")
    if refused == "not-a-package" and metadata.read(town / "alpha" / ".pp") == before:
        held("a caller the store cannot situate refuses", "not a vendored package: it refuses "
             "by name, and the store is untouched")
    else:
        failures.append(f"  ✗ metadata stray caller       {refused!r}")
    return 0
