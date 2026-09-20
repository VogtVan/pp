"""Scenario `wire-and-stamp` -- the harness link (plan pp-split, batch le-lien-au-harnais) -- 3 case(s):
- wire on a bare workspace writes .claude/settings.json with the Stop hook alone; wired
  again it touches NOTHING, prints the snippet and says the skip; provider-unknown refuses
- the stamp is gated at the SKILL: silent (rc 0, no line) while the switch is false, and
  the engine's turn-end line lands once it is true -- the wired hook never changes
- the console resolves `./pp monitoring-stamp` as the package's command; without the package the verb
  does not exist
"""
from __future__ import annotations

import json

from conductor.packaging import contributions
from conductor.state import instance


def _stamps(made) -> int:
    count = 0
    for trace in (made / instance.STATE).glob("session-*.jsonl"):
        count += sum(1 for line in trace.read_text(encoding="utf-8").splitlines()
                     if '"turn-end"' in line)
    return count


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("wirews", ("monitoring",))
    made = env.made
    settings_json = made.parent / ".claude" / "settings.json"

    # --- wire: born once, never overwritten, unknown refused ---------------------------
    rc, out, _ = contributions.run_skill(made, "pp-monitoring", ["wire", "claude"])
    written = settings_json.read_text(encoding="utf-8") if settings_json.is_file() else ""
    rc2, out2, _ = contributions.run_skill(made, "pp-monitoring", ["wire", "claude"])
    after = settings_json.read_text(encoding="utf-8")
    rc3, _, err3 = contributions.run_skill(made, "pp-monitoring", ["wire", "codex"])
    if (rc == 0 and '"Stop"' in written and "./pp monitoring-stamp" in written
            and rc2 == 0 and after == written and "skipped" in out2 and "./pp monitoring-stamp" in out2
            and rc3 == 2 and "provider-unknown" in err3):
        held("wire writes once and never overwrites",
             "the hook born on the bare workspace; the second wire prints the snippet "
             "and skips; codex refuses by name")
    else:
        failures.append(f"  ✗ wire                       rc={rc}/{rc2}/{rc3} same={after == written}")

    # --- the stamp gated at the skill ---------------------------------------------------
    env.cli("-new")                                       # a run, so a trace exists
    rc4, _, _ = contributions.run_skill(made, "pp-monitoring", ["stamp"])
    silent = _stamps(made)
    env.write("SETTINGS.md", env.read("SETTINGS.md")
              .replace("monitoring_capture: false", "monitoring_capture: true"))
    rc5, _, _ = contributions.run_skill(made, "pp-monitoring", ["stamp"])
    armed = _stamps(made)
    if rc4 == 0 and silent == 0 and rc5 == 0 and armed == 1:
        held("the switch interrupts at the skill",
             "stamp silent and lineless while false; one turn-end line once true")
    else:
        failures.append(f"  ✗ gated stamp                rc={rc4}/{rc5} lines={silent}/{armed}")

    # --- the console command, present with the package and absent without --------------
    con = env.cli("monitoring-stamp")
    bare = bench.env("nowire")
    missing = bare.cli("monitoring-stamp")
    if con.returncode == 0 and _stamps(made) == 2 and missing.returncode != 0:
        held("the console resolves the package's command",
             "./pp monitoring-stamp lands a second line; the kit-only console knows no such verb")
    else:
        failures.append(f"  ✗ console command            rc={con.returncode}/{missing.returncode} "
                        f"lines={_stamps(made)}")
    return len(failures)
