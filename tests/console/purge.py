"""Scenario `purge` -- 8 case(s) (plan core, batch la-purge, 2026-10-11): `./pp -purge` removes for
good what the engine keeps of a run -- its slot or renewal mark, every `session-<key>.*`, every trace
of its key --, by key or by age, each run under its call lock tried without waiting; without `--yes`
it says what it would remove and writes nothing.
- (a) bare: the usage in one line, nothing written
- (b) `-purge A`: one line for A and the total, the state directory byte-identical
- (c) `-purge A --yes`: every file of A gone, B and C byte-identical, the trace reader without A
- (d) B's call lock held by the bench's own process: `-purge B C --yes` refuses `call-busy`, no file
  removed
- (e) `--before`: C's trace and a keyless trace dated before, B recent: C and the keyless trace go,
  B stays
- (f) an unknown key refuses `run-unknown`, a malformed date `purge-invalid`, nothing removed
- (g) a renewal mark is purged as a slot
- (h) `-json`: the count as one object, `dry` true without `--yes`
"""
from __future__ import annotations

import json
import os

from conductor import instance, persistence
from conductor.state import lock, traces
from tests.harness import bench_key, holding

OLD = 1_767_225_600          # 2026-01-01 00:00 UTC: a date before the cut the case names
KEYLESS = "session-20260901T000000Z.jsonl"


def _listing(state) -> dict[str, bytes]:
    """-> every file of the state directory and its bytes: what a refusal or a dry run never moves."""
    return {one.name: one.read_bytes() for one in sorted(state.iterdir()) if one.is_file()}


def _of(listing: dict, key: str) -> list[str]:
    return [name for name in listing if name.startswith(f"session-{key}.") or name.endswith(f"-{key}.jsonl")]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("purge")
    state = env.made / instance.STATE
    keys = []
    for _ in range(3):
        opened = env.cli("-new")
        if opened.returncode:
            failures.append(f"-new failed: {opened.stderr.strip()[:200]}")
            return len(failures)
        keys.append(bench_key(env.made))
    a, b, c = keys
    (state / KEYLESS).write_text('{"at": "2026-09-01T00:00:00.000+00:00", "kind": "new"}\n', encoding="utf-8")

    # --- (a) bare: the usage ------------------------------------------------------------------------
    before = _listing(state)
    bare = env.cli("-purge")
    if bare.returncode != 0 and "-purge" in bare.stderr and bare.stderr.strip().count("\n") == 0 \
            and _listing(state) == before:
        held("(a) bare: the usage in one line", "nothing written")
    else:
        failures.append(f"  ✗ (a) bare                    rc={bare.returncode} {bare.stderr.strip()[:160]!r}")

    # --- (b) the count, nothing written ---------------------------------------------------------------
    said = env.cli("-purge", a)
    if said.returncode == 0 and a in said.stdout and "--yes" in said.stdout and _listing(state) == before:
        held("(b) without --yes: the count, nothing written", "the state directory byte-identical")
    else:
        failures.append(f"  ✗ (b) dry                     rc={said.returncode} {said.stdout[:200]!r} "
                        f"same={_listing(state) == before}")

    # --- (c) a run purged leaves nothing of its own ---------------------------------------------------
    gone = env.cli("-purge", a, "--yes")
    after = _listing(state)
    others = {name: data for name, data in before.items() if name not in _of(before, a)}
    counted = {run.key for run in traces.runs(state)}
    if (gone.returncode == 0 and _of(before, a) and not _of(after, a)
            and all(after.get(name) == data for name, data in others.items())
            and a not in counted and {b, c} <= counted):
        held("(c) --yes: every file of A gone, the others byte-identical", f"{len(_of(before, a))} file(s) "
             "removed, the trace reader no longer counts A")
    else:
        failures.append(f"  ✗ (c) purge                   rc={gone.returncode} {gone.stderr.strip()[:160]!r} "
                        f"left={_of(after, a)} counted={sorted(counted)}")

    # --- (d) a run a call holds: nothing removed ------------------------------------------------------
    with holding(lock.call_of(env.made, b)):
        frozen = _listing(state)
        busy = env.cli("-purge", b, c, "--yes")
        same = _listing(state) == frozen
    if busy.returncode == 2 and "call-busy" in busy.stderr and same:
        held("(d) a call lock held: call-busy, no file removed", "B and C intact")
    else:
        failures.append(f"  ✗ (d) call-busy               rc={busy.returncode} {busy.stderr.strip()[:160]!r} same={same}")

    # --- (e) by age -----------------------------------------------------------------------------------
    for name in _of(_listing(state), c) + [KEYLESS]:
        if name.endswith(".jsonl"):
            os.utime(state / name, (OLD, OLD))
    aged = env.cli("-purge", "--before", "2026-06-01", "--yes")
    now = _listing(state)
    if aged.returncode == 0 and not _of(now, c) and KEYLESS not in now and _of(now, b):
        held("(e) --before: the old run and the keyless trace go, the recent run stays",
             f"{c} and {KEYLESS} removed, {b} kept")
    else:
        failures.append(f"  ✗ (e) before                  rc={aged.returncode} {aged.stdout[:200]!r} "
                        f"c={_of(now, c)} keyless={KEYLESS in now} b={_of(now, b)}")

    # --- (f) the refusals -----------------------------------------------------------------------------
    still = _listing(state)
    unknown = env.cli("-purge", "abcdef", "--yes")
    malformed = env.cli("-purge", "--before", "2026-13-45", "--yes")
    if (unknown.returncode == 2 and "run-unknown" in unknown.stderr
            and malformed.returncode == 2 and "purge-invalid" in malformed.stderr and _listing(state) == still):
        held("(f) run-unknown, purge-invalid", "exit 2 twice, nothing removed")
    else:
        failures.append(f"  ✗ (f) refusals                {unknown.stderr.strip()[:100]!r} {malformed.stderr.strip()[:100]!r}")

    # --- (g) a renewal mark ---------------------------------------------------------------------------
    env.cli("-new")
    d = bench_key(env.made)
    persistence.renew(persistence.slot_of(env.made, d), {"kit": "0"}, {"kit": "1"}, "2026-10-05T00:00:00Z")
    renewed = persistence.renewed(persistence.slot_of(env.made, d)) is not None
    marked = env.cli("-purge", d, "--yes")
    if renewed and marked.returncode == 0 and not _of(_listing(state), d):
        held("(g) a renewal mark is purged as a slot", f"{d} gone")
    else:
        failures.append(f"  ✗ (g) renewal mark            renewed={renewed} rc={marked.returncode} "
                        f"{marked.stderr.strip()[:160]!r} left={_of(_listing(state), d)}")

    # --- (h) the count in JSON ------------------------------------------------------------------------
    as_json = env.cli("-purge", b, "-json")
    try:
        count = json.loads(as_json.stdout)
    except ValueError:
        count = {}
    runs = count.get("runs") or []
    if (as_json.returncode == 0 and count.get("dry") is True and len(runs) == 1 and runs[0].get("key") == b
            and runs[0].get("files") and isinstance(runs[0].get("bytes"), int)
            and count.get("files") == len(runs[0]["files"]) and count.get("bytes") == runs[0]["bytes"]
            and _of(_listing(state), b)):
        held("(h) -json: the count as one object", f"dry, {count.get('files')} file(s), {count.get('bytes')} bytes")
    else:
        failures.append(f"  ✗ (h) json                    rc={as_json.returncode} {as_json.stdout[:200]!r}")
    return len(failures)
