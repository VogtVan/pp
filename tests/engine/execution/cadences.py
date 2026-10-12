"""Scenario `cadences` -- a work DUE is a declaration (plan pp-split, batch
les-cadences-declarees; batch les-ecrivains-partages, 2026-09-30):
- one predicate: the anchored weekday crossed the record; `since` narrows; `never` never
- a declared cadence plays its document at its socket when due, nothing otherwise
- an absent `play` is said, never refused; a declared check pushes its signal
- two boots on one unwritten period: the first CLAIMS it and plays, the second injects
  nothing and says `cadence-claimed`
- one rule for every run (batch le-reveil-rendu-au-lanceur, 2026-10-03): a claim holds while the
  claimant's saved state stands, whatever file stands beside it; a forgotten claimant is replaced
- the record written at the boundary: silence and no claim; the same run claims once
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conductor import cadences, instance, persistence, render
from tests.harness import bench_key, session_of

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
# a WORK step, as HISTORY's
DOC = "---\nname: SIGHTING\nkind: proc\ndescription: the sighting digest\nproc: |\n  WORK\n---\n\nSIGHTING says the week\n"


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

    # --- two boots on one unwritten period: the first claims and plays, the second nothing --------
    claims = made / ".sys" / "records" / "claims.jsonl"
    weekday = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(today_name)
    period = (today.date() - timedelta(days=(today.weekday() - weekday) % 7)).isoformat()

    def _claims() -> list[tuple]:
        if not claims.is_file():
            return []
        return [(one["cadence"], one["period"], one["run"]) for one in
                (json.loads(line) for line in claims.read_text(encoding="utf-8").splitlines() if line.strip())]

    def _rediscovered():
        return env.__class__(name=env.name, made=env.made,
                             member=discovery.instance_member(env.engine), engine=env.engine)

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
    if ("SIGHTING says the week" in a_block and "SIGHTING says the week" not in b_block
            and _claims() == [("sighting", period, a_key)]
            and said and said[0].get("run") == a_key and said[0].get("period") == period):
        held("two boots, one play", f"the earlier runs forgotten; A {a_key} claimed {period} and played "
             f"SIGHTING; B {b_key} injected nothing and traced cadence-claimed")
    else:
        failures.append(f"  ✗ two boots                    A={'SIGHTING says' in a_block} "
                        f"B={'SIGHTING says' in b_block} claims={_claims()} said={said}")

    # --- one rule: a claim holds while the claimant's saved state stands --------------------------
    persistence.forget(persistence.slot_of(made, a_key))
    c_block = _boot(_rediscovered())
    c_key = bench_key(made)
    launcher = persistence.slot_of(made, c_key).with_name(f"session-{c_key}.wake.lock")
    launcher.touch()                           # a launcher's file beside C's slot, held by nobody
    d_block = _boot(_rediscovered())           # C's saved state stands: its claim holds
    persistence.forget(persistence.slot_of(made, c_key))
    e_block = _boot(_rediscovered())           # C forgotten: its claim is void
    e_key = bench_key(made)
    if ("SIGHTING says the week" in c_block and "SIGHTING says the week" not in d_block
            and "SIGHTING says the week" in e_block and _claims() == [("sighting", period, e_key)]):
        held("one rule: the claimant's saved state", f"A forgotten -> C {c_key} played; a launcher's file free "
             f"beside C, its state standing -> D injected nothing; C forgotten -> E {e_key} played")
    else:
        failures.append(f"  ✗ one rule                     C={'SIGHTING says' in c_block} "
                        f"D={'SIGHTING says' in d_block} E={'SIGHTING says' in e_block} claims={_claims()}")

    # --- the record written: silence and no new claim; the same run claims once ------------------------
    _stamp(made, "sightings.jsonl", today)
    before = _claims()
    f_block = _boot(_rediscovered())
    claim = getattr(cadences, "claim", None)
    again = claim(made, "sighting", period, e_key, lambda run: True) if claim else None
    if "SIGHTING says the week" not in f_block and _claims() == before and again is True and len(_claims()) == 1:
        held("the record written: silence, one claim line", f"{len(_claims())} claim line(s), the same run claims again: True")
    else:
        failures.append(f"  ✗ silence / idempotent         F={'SIGHTING says' in f_block} claims={_claims()} again={again}")
    return 0
