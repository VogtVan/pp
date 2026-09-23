"""Scenario `cadences` -- a work DUE is a declaration (plan pp-split, batch
les-cadences-declarees):
- one predicate: the anchored weekday crossed the record; `since` narrows; `never` never
- a declared cadence plays its document at its socket when due, nothing otherwise
- an absent `play` is said, never refused; a declared check pushes its signal
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conductor import cadences, instance, persistence, render
from tests.harness import session_of

WITNESS = """name: witness
version: 0.0.1
description: a package with a cadence and a check
requires: [kit]
contributes:
  cadences:
    - {name: sighting, anchor: "@SETTINGS.sighting_day", record: sightings.jsonl, play: SIGHTING.md, at: boot.ready}
    - {name: ghost, anchor: "@SETTINGS.sighting_day", record: ghosts.jsonl, play: GHOST.md, at: boot.ready}
  checks:
    - {signal: sighting-due, predicate: record-crossing, record: sightings.jsonl, anchor: "@SETTINGS.sighting_day"}
  events:
    signals:
      sighting-due: {priority: 3, door: SIGHTING}
"""
DOC = "---\nname: SIGHTING\nkind: proc\ndescription: the sighting digest\nproc: |\n  HOOK sighting.read\n---\n\nSIGHTING says the week\n"


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


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("cadenced")
    made = env.made
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "procs").mkdir(parents=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (root / "procs" / "SIGHTING.md").write_text(DOC, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)
    today = datetime.now(timezone.utc)
    today_name = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][today.weekday()]
    _settings(made, today_name)

    # --- the predicate: a stale record is due, a fresh one is not, never never -------
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    stale = cadences.crossing_due(made, "@SETTINGS.sighting_day", "sightings.jsonl")
    _stamp(made, "sightings.jsonl", today)
    fresh = cadences.crossing_due(made, "@SETTINGS.sighting_day", "sightings.jsonl")
    absent = cadences.crossing_due(made, "@SETTINGS.sighting_day", "nothing.jsonl")
    _stamp(made, "sightings.jsonl", today - timedelta(days=8))
    quiet = cadences.crossing_due(made, "@SETTINGS.sighting_day", "sightings.jsonl", since="moves.jsonl")
    _stamp(made, "moves.jsonl", today - timedelta(days=1))
    moved = cadences.crossing_due(made, "@SETTINGS.sighting_day", "sightings.jsonl", since="moves.jsonl")
    if stale and not fresh and absent and not quiet and moved:
        held("one crossing predicate", "stale record due, fresh not, absent due, `since` "
             "quiet not, `since` moved due")
    else:
        failures.append(f"  ✗ predicate                    {stale} {fresh} {absent} {quiet} {moved}")
    _settings(made, "never")
    if not cadences.crossing_due(made, "@SETTINGS.sighting_day", "sightings.jsonl"):
        held("never never", "sighting_day: never switches every anchored work off")
    else:
        failures.append("  ✗ never                        due under never")
    expect("anchor-invalid", lambda: cadences.crossing_due(made, "caturday", "sightings.jsonl"))
    _settings(made, today_name)

    # --- a declared cadence plays at its socket when due; the check pushes --------------
    first = _boot(env)
    latched = [one.get("signal") for one in persistence.signals_of(session_of(env.member.meta))]
    if "SIGHTING says the week" in first and "sighting-due" in latched:
        held("a cadence plays, a check pushes", "SIGHTING.md CALLed at boot.ready, "
             "sighting-due latched -- both from the declaration, the engine names neither")
    else:
        failures.append(f"  ✗ cadence due                  played={'SIGHTING says' in first} latched={latched}")
    if "GHOST" not in first:
        held("an absent play is said", "ghost's GHOST.md resolves nowhere: the "
             "boot went on")
    else:
        failures.append("  ✗ ghost                        an unplayable cadence rendered")
    _stamp(made, "sightings.jsonl", today)
    from conductor import discovery
    fresh_env = env.__class__(name=env.name, made=env.made,
                              member=discovery.instance_member(env.engine), engine=env.engine)
    second = _boot(fresh_env)
    if "SIGHTING says the week" not in second:
        held("a cadence not due is silent", "the record stamped today, the boot "
             "carries no SIGHTING")
    else:
        failures.append("  ✗ cadence not due              SIGHTING played on a fresh record")
    return 0
