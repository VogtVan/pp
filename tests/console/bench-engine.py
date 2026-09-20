"""Scenario `bench-engine` -- 2 case(s):
- la-provenance: the conductor the bench judges comes from the source
- la-reprise-de-main: a vendored engine hands `-test` over to the product's own
"""
from __future__ import annotations

from pathlib import Path

import conductor
from tests.harness import ENGINE, PRODUCT_ENGINE, cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- la-provenance: one code judges, in process and in subprocess ---------------
    imported = Path(conductor.__file__).resolve().parent
    if imported == (ENGINE / "conductor").resolve():
        held("the bench judges the source", f"`conductor` is imported from {imported} -- "
             f"the same tree {PRODUCT_ENGINE.name} installs every throwaway instance from, "
             "so both halves of the bench judge one code")
    else:
        failures.append(f"  ✗ the engine judged           {imported} -- not {ENGINE / 'conductor'}")

    # --- la-reprise-de-main: the vendored engine hands the call over ----------------
    env = bench.env("relay")
    answer = cli(env.engine, "-test", "nothing-answers-to-this-name")
    if (f"bench on {PRODUCT_ENGINE}" in answer.stdout and answer.returncode == 2
            and "no scenario answers" in answer.stdout):
        held("a vendored engine hands the bench over", "its `-test` opens on the SOURCE "
             "engine's header line and returns the usual refusal -- the call plays where "
             "the product lives, whatever was typed")
    else:
        failures.append(f"  ✗ the bench was not handed over rc {answer.returncode}: "
                        f"{answer.stdout[:160]!r}")
    return 0
