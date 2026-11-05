"""Scenario `cadences` -- the pattern `automation/cadences`, played from its demonstration:
- the crossing: the anchored weekday crossed since the record's last entry is due, a fresh record
  is not, an absent one is; `since` narrows; `never` switches it off; an anchor out of form
  refuses `anchor-invalid`
- the witness's cadence plays SIGHTING at `boot.initialize` when due, its check pushes its signal;
  the cadence whose `play` resolves nowhere is said and skipped; a cadence not due is silent
- two boots on one unwritten period: the first CLAIMS it and plays, the second plays nothing and
  traces `cadence-claimed`; a claim holds while the claimant's saved state stands, a forgotten
  claimant is replaced; the record written, silence and one claim line
- under the principal's conduction a due cadence plays the same
- at the build: a cadence without `play` refuses `contribution-malformed`, one at a socket nobody
  opens `socket-unknown`, one at a socket of a package it does not require `dependency-undeclared`
The settings the anchor reads and the records it crosses are written at the test's time.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conductor import cadences, compiling, discovery, persistence, render
from tests.harness import bench_key, demonstrated, demos, manifests, principal, session_of, vendor

DRAWER, PATTERN = "automation", "cadences"
DEMOS = ("SIGHTING.md",)
MANIFESTS = ("nowhere.yaml", "playless.yaml", "unrequired.yaml", "witness.yaml")
WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _stamp(made, record: str, when: datetime) -> None:
    path = made / ".sys" / "records" / record
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"at": when.isoformat(timespec="seconds"), "entry": "bench"}) + "\n",
                    encoding="utf-8")


def _settings(made, day: str) -> None:
    (made / "SETTINGS.md").write_text(
        f"---\nname: SETTINGS\nkind: doc\nsighting_day: {day}\ninstructions_fusion: max\n---\n",
        encoding="utf-8")


def _boot(env) -> str:
    opener = env.conductor()
    return render(opener.start(opener.boot("BOOT.md")))


def _played(rendered: str) -> bool:
    """-> whether SIGHTING stands as a frame of the rendered output."""
    return "SIGHTING{" in rendered


def _sighting() -> str:
    return (demos(DRAWER, PATTERN) / "SIGHTING.md").read_text(encoding="utf-8")


def crossing(bench, made, today, today_name) -> None:
    """The predicate the declaration's anchor feeds."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    anchor = "@SETTINGS.sighting_day"
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    stale = cadences.crossing_due(made, anchor, "sightings.jsonl")
    _stamp(made, "sightings.jsonl", today)
    fresh = cadences.crossing_due(made, anchor, "sightings.jsonl")
    absent = cadences.crossing_due(made, anchor, "nothing.jsonl")
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    quiet = cadences.crossing_due(made, anchor, "sightings.jsonl", since="moves.jsonl")
    _stamp(made, "moves.jsonl", today - timedelta(days=1))
    moved = cadences.crossing_due(made, anchor, "sightings.jsonl", since="moves.jsonl")
    if stale and not fresh and absent and not quiet and moved:
        held("one crossing predicate", "stale record due, fresh not, absent due, `since` quiet not, "
             "`since` moved due")
    else:
        failures.append(f"  ✗ predicate                    {stale} {fresh} {absent} {quiet} {moved}")
    _settings(made, "never")
    if not cadences.crossing_due(made, anchor, "sightings.jsonl"):
        held("never never", "sighting_day: never switches every anchored work off")
    else:
        failures.append("  ✗ never                        due under never")
    expect("anchor-invalid", lambda: cadences.crossing_due(made, "caturday", "sightings.jsonl"))
    _settings(made, today_name)


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    found, declared = demonstrated(DRAWER, PATTERN), manifests(DRAWER, PATTERN)
    if found != sorted(DEMOS) or sorted(declared) != sorted(MANIFESTS):
        failures.append(f"  ✗ the demonstration           {found!r} {sorted(declared)!r} -- owed "
                        f"{sorted(DEMOS)!r} {sorted(MANIFESTS)!r}")
        return 0
    env = bench.env("cadenced")
    made = env.made
    vendor(made, "witness", declared["witness.yaml"], {"SIGHTING": _sighting()})
    today = datetime.now(timezone.utc)
    today_name = WEEK[today.weekday()]
    _settings(made, today_name)
    crossing(bench, made, today, today_name)

    # --- the cadence plays at its socket when due; the check pushes; the ghost is said ----------
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    first = _boot(env)
    latched = [one.get("signal") for one in persistence.signals_of(session_of(env.member.meta))]
    if _played(first) and "sighting-due" in latched:
        held("a cadence plays, a check pushes", "SIGHTING CALLed at boot.initialize, sighting-due latched -- "
             "both from the declaration, the engine names neither")
    else:
        failures.append(f"  ✗ cadence due                  played={_played(first)} latched={latched}")
    if "GHOST" not in first:
        held("an absent play is said", "ghost's GHOST.md resolves nowhere: the boot went on")
    else:
        failures.append("  ✗ ghost                        an unplayable cadence rendered")

    def _rediscovered():
        return env.__class__(name=env.name, made=env.made,
                             member=discovery.instance_member(env.engine), engine=env.engine)

    _stamp(made, "sightings.jsonl", today)
    if not _played(_boot(_rediscovered())):
        held("a cadence not due is silent", "the record stamped today, the boot carries no SIGHTING")
    else:
        failures.append("  ✗ cadence not due              SIGHTING played on a fresh record")

    # --- two boots on one unwritten period: the first claims and plays, the second nothing -----
    claims = made / ".sys" / "records" / "claims.jsonl"
    period = (today.date() - timedelta(days=(today.weekday() - WEEK.index(today_name)) % 7)).isoformat()

    def _claims() -> list[tuple]:
        if not claims.is_file():
            return []
        return [(one["cadence"], one["period"], one["run"]) for one in
                (json.loads(line) for line in claims.read_text(encoding="utf-8").splitlines() if line.strip())]

    def _events(key: str) -> list[dict]:
        slot = persistence.slot_of(made, key)
        log = persistence.trace_of(slot) or ""
        path = slot.parent / log
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()] if log and path.is_file() else []

    for slot in persistence.slots(made):        # the earlier boots' runs gone: their claim is void
        persistence.forget(slot)
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    a_block = _boot(_rediscovered())
    a_key = bench_key(made)
    b_block = _boot(_rediscovered())
    b_key = bench_key(made)
    said = [one for one in _events(b_key) if one.get("kind") == "cadence-claimed"]
    if (_played(a_block) and not _played(b_block)
            and _claims() == [("sighting", period, a_key)]
            and said and said[0].get("run") == a_key and said[0].get("period") == period):
        held("two boots, one play", f"A {a_key} claimed {period} and played SIGHTING; B {b_key} injected "
             "nothing and traced cadence-claimed")
    else:
        failures.append(f"  ✗ two boots                    A={_played(a_block)} "
                        f"B={_played(b_block)} claims={_claims()} said={said}")

    # --- one rule: a claim holds while the claimant's saved state stands -----------------------
    persistence.forget(persistence.slot_of(made, a_key))
    c_block = _boot(_rediscovered())
    c_key = bench_key(made)
    persistence.slot_of(made, c_key).with_name(f"session-{c_key}.wake.lock").touch()
    d_block = _boot(_rediscovered())           # C's saved state stands: its claim holds
    persistence.forget(persistence.slot_of(made, c_key))
    e_block = _boot(_rediscovered())           # C forgotten: its claim is void
    e_key = bench_key(made)
    if (_played(c_block) and not _played(d_block)
            and _played(e_block) and _claims() == [("sighting", period, e_key)]):
        held("one rule: the claimant's saved state", f"A forgotten -> C {c_key} played; a lock file "
             f"free beside C, its state standing -> D injected nothing; C forgotten -> E {e_key} played")
    else:
        failures.append(f"  ✗ one rule                     C={_played(c_block)} "
                        f"D={_played(d_block)} E={_played(e_block)} claims={_claims()}")

    # --- the record written: silence and no new claim; the same run claims once ----------------
    _stamp(made, "sightings.jsonl", today)
    before = _claims()
    f_block = _boot(_rediscovered())
    again = cadences.claim(made, "sighting", period, e_key, lambda run: True)
    if not _played(f_block) and _claims() == before and again is True and len(_claims()) == 1:
        held("the record written: silence, one claim line", f"{len(_claims())} claim line, the same run "
             "claims again: True")
    else:
        failures.append(f"  ✗ silence / idempotent         F={_played(f_block)} claims={_claims()} again={again}")

    # --- under the principal's conduction, a due cadence plays the same -------------------------
    for slot in persistence.slots(made):
        persistence.forget(slot)
    claims.unlink(missing_ok=True)
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    led = principal(lambda: _boot(_rediscovered()))
    if _played(led) and len(_claims()) == 1:
        held("a due cadence plays under the principal's conduction", "the boot of a run its principal "
             "conducts CALLs SIGHTING and claims the period once")
    else:
        failures.append(f"  ✗ principal cadence            played={_played(led)} claims={_claims()}")

    # --- what the build refuses of a cadence ---------------------------------------------------
    def building(manifest: str):
        house = bench.env("cadence-build")
        vendor(house.made, "witness", declared[manifest], {"SIGHTING": _sighting()})
        return lambda: compiling.build_tools(house.made)

    expect("contribution-malformed", building("playless.yaml"))
    expect("socket-unknown", building("nowhere.yaml"))
    expect("dependency-undeclared", building("unrequired.yaml"))
    return 0
