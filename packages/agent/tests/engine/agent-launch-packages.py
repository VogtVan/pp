"""Scenario `agent-launch-packages` -- 4 case(s) (batch les-packages-au-lancement, 2026-10-12, agent 0.24.0): a wake-up
plays the packages its caller names -- `--package <name>=on|off`, repeated, on `run` and `start`, played on the run
under the principal's mark by the conversation's waiting list before every launch, an opening as a resume; on a
house pinning `agent`, `steering` and `plan` (`plan` mounts `NEXT_MOVE` at `turn.end`, so a run parked at its FINAL
holds it). The flag on `chat` is `agent-chat-packages`'s.
- (a) an opening: `run --package plan=off` opens a run that plays `plan` off -- the run's switch traced once,
  stderr says `package plan off`
- (b) a resume: a run parked with `plan` held by its turn, resumed with `--package plan=off`, plays `plan` off from
  the exchange's first launch; the run of (a) resumed with `--package plan=on` plays it again
- (c) refusals leave nothing (KPL32): `nowhere=off`, the base and `plan=maybe` refuse `package-unpinned`,
  `package-base` and `package-invalid` -- no run opened, the house's records as they were
- (d) `start` and `--dry-run` (KPL34): the detached wake-up plays the switch; a dry run says `package plan off` and
  opens nothing
"""
from __future__ import annotations

from conductor import instance, persistence
from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench, packages=("agent", "steering", "plan"))
    keys, counted = h.keys, h.counted

    def off(key: str) -> list:
        return persistence.off_of(persistence.slot_of(h.agent_meta, key)) if key else ["?"]

    def switches(key: str) -> int:
        return len([one for one in h.trace(key) if one.get("kind") == "switch"]) if key else -1

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    # --- (a) an opening plays the packages named -----------------------------------------------------------
    known = set(keys())
    opened = h.wake("un", "play", "--package", "plan=off")
    key_a = fresh(known)
    if opened.returncode == 0 and key_a and off(key_a) == ["plan"] and switches(key_a) == 1 \
            and "package plan off" in opened.stderr:
        held("(a) an opening plays the packages named", f"run {key_a}: plan off, the switch traced once, stderr says "
             "`package plan off`")
    else:
        failures.append(f"  ✗ (a) opening                rc={opened.returncode} key={key_a!r} off={off(key_a)} "
                        f"switches={switches(key_a)} {opened.stderr[-300:]!r}")

    # --- (b) a resume, the package held by the parked turn --------------------------------------------------
    known = set(keys())
    parked = h.wake("un")
    key_b = fresh(known)
    resumed = h.call("agent", "run", "agents/ag1", "--run", key_b, "--message", "deux", "--package", "plan=off",
                     *h.harnessed("play"))
    back = h.call("agent", "run", "agents/ag1", "--run", key_a, "--message", "deux", "--package", "plan=on",
                  *h.harnessed("play"))
    if parked.returncode == 0 and resumed.returncode == 0 and off(key_b) == ["plan"] \
            and switches(key_b) == 1 and back.returncode == 0 and off(key_a) == [] and switches(key_a) == 2:
        held("(b) a resume plays them too", f"run {key_b} parked with plan held, resumed with plan=off: off from its "
             f"exchange; run {key_a} resumed with plan=on: on again")
    else:
        failures.append(f"  ✗ (b) resume                 rc={parked.returncode}/{resumed.returncode}/{back.returncode} "
                        f"off_b={off(key_b)} off_a={off(key_a)} switches={switches(key_b)}/{switches(key_a)} "
                        f"{resumed.stderr[-300:]!r}")

    # --- (c) refusals leave nothing --------------------------------------------------------------------------
    before_keys, before_counts = sorted(keys()), counted()
    base = instance.base_of(h.agent_meta)
    refusals = {code: h.wake("never", "play", "--package", value)
                for code, value in (("package-unpinned", "nowhere=off"), ("package-base", f"{base}=off"),
                                    ("package-invalid", "plan=maybe"))}
    if (all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and sorted(keys()) == before_keys and counted() == before_counts):
        held("(c) refusals leave nothing", "package-unpinned, package-base, package-invalid before anything: no run "
             "opened, the records as they were -- KPL32")
    else:
        failures.append("  ✗ (c) refusals               " + " ".join(f"{code}={one.returncode}:{one.stderr[-120:]!r}"
                                                                  for code, one in refusals.items())
                        + f" keys={sorted(set(keys()) - set(before_keys))} counts={before_counts}/{counted()}")

    # --- (d) start and --dry-run -------------------------------------------------------------------------------
    before_keys, before_counts = sorted(keys()), counted()
    dry = h.wake("never", "play", "--package", "plan=off", "--dry-run")
    unopened = sorted(keys()) == before_keys and counted() == before_counts
    started = h.call("agent", "start", "agents/ag1", "--message", "trois", "--package", "plan=off", *h.harnessed("play"))
    key_d = A.report_of(started).get("key", "")
    waited = h.call("agent", "wait", "agents/ag1", key_d, "--timeout", "60") if key_d else None
    if (dry.returncode == 0 and "  package plan off" in dry.stdout.splitlines() and unopened
            and started.returncode == 0 and key_d and waited is not None and waited.returncode == 0
            and off(key_d) == ["plan"] and switches(key_d) == 1):
        held("(d) start and --dry-run", f"the dry run says `package plan off`, opens nothing; start's run {key_d} plays "
             "plan off -- KPL34")
    else:
        failures.append(f"  ✗ (d) start, dry run         rc={dry.returncode}/{started.returncode}/"
                        f"{waited.returncode if waited else None} unopened={unopened} key={key_d!r} off={off(key_d)} "
                        f"{dry.stdout[-200:]!r} {started.stderr[-200:]!r}")
    return 0
