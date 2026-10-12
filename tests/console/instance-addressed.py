"""Scenario `instance-addressed` -- 6 case(s) (batch l-instance-adressee, 2026-09-26):
- `--instance <dir>` opens a run on that instance from anywhere, with the PRODUCT engine
- `PP_HOME=<dir>` does the same, read at the resolution alone
- both given, the flag wins
- a directory carrying no instance refuses `instance-missing`
- the form of yesterday holds: the vendored engine called bare plays its own instance,
  the launcher's text is the install's
- the keyed form advances the run the flag opened, wherever the flag stands in the call
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from conductor import install, persistence
from tests.harness import PRODUCT_ENGINE, bench_key, cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("addressed").made
    other = bench.env("other").made
    elsewhere = Path(tempfile.mkdtemp())

    # --- the flag: a run opens on the addressed instance, from anywhere ------------------
    run = cli(PRODUCT_ENGINE, "--instance", str(made), "-new", cwd=elsewhere)
    slots = persistence.slots(made)
    if run.returncode == 0 and "▌ INSTRUCTION" in run.stdout and len(slots) == 1 \
            and slots[0].is_relative_to(made / ".sys" / "state"):
        held("--instance opens the run there", "the product engine, called from a foreign "
             "directory, boots the addressed instance: one slot under its .sys/state")
    else:
        failures.append(f"  ✗ --instance                 rc={run.returncode} {run.stderr[:120]!r} {slots}")

    # --- the variable: read at the resolution, the same instance --------------------------
    run = cli(PRODUCT_ENGINE, "-new", cwd=elsewhere, env={"PP_HOME": str(made)})
    if run.returncode == 0 and "▌ INSTRUCTION" in run.stdout and len(persistence.slots(made)) == 2:
        held("PP_HOME opens the run there", "a second run on the same instance, addressed "
             "by the variable alone")
    else:
        failures.append(f"  ✗ PP_HOME                    rc={run.returncode} {run.stderr[:120]!r}")

    # --- both given: the flag wins --------------------------------------------------------
    run = cli(PRODUCT_ENGINE, "--instance", str(other), "-new", cwd=elsewhere,
              env={"PP_HOME": str(made)})
    if run.returncode == 0 and len(persistence.slots(other)) == 1 and len(persistence.slots(made)) == 2:
        held("the flag wins over the variable", "the run opened on the flag's instance, "
             "the variable's untouched")
    else:
        failures.append(f"  ✗ flag over variable         rc={run.returncode} "
                        f"{len(persistence.slots(other))}/{len(persistence.slots(made))}")

    # --- a directory with no instance refuses by name ------------------------------------
    run = cli(PRODUCT_ENGINE, "--instance", str(elsewhere), "-new", cwd=elsewhere)
    if run.returncode == 2 and "instance-missing" in run.stderr:
        held("instance-missing", "refused -- a directory carrying no instance.yaml is no address")
    else:
        failures.append(f"  ✗ instance-missing           rc={run.returncode} {run.stderr[:120]!r}")

    # --- the form of yesterday holds -----------------------------------------------------
    engine = made / ".sys" / "engine" / "pp.py"
    run = cli(engine, "-new", cwd=elsewhere)
    launcher = (made.parent / "pp").read_text(encoding="utf-8")
    if run.returncode == 0 and len(persistence.slots(made)) == 3 \
            and launcher == install.CONSOLE.format(meta=made.name):
        held("the vendored engine plays bare", "no flag, no variable: the installed engine "
             "conducts the instance it lives in, and the launcher is the install's text")
    else:
        failures.append(f"  ✗ yesterday's form           rc={run.returncode} {run.stderr[:120]!r}")

    # --- the keyed form, the flag anywhere in the call -----------------------------------
    key = bench_key(made)
    run = cli(PRODUCT_ENGINE, key, "--instance", str(made), cwd=elsewhere)
    if run.returncode == 0 and "pp · run " + key in run.stdout:
        held("the keyed call is addressed too", "`<key> --instance <dir>` advances that "
             "instance's run: the flag is read wherever it stands")
    else:
        failures.append(f"  ✗ keyed form                 rc={run.returncode} {run.stderr[:120]!r}")
    return 0
