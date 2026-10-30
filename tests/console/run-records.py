"""Scenario `run-records` -- what the engine keeps of a run, stamped, read and removed at the console:
- the turn-end stamp: without a run trace `-et` refuses `no-run`, nothing written; with runs it
  poses ONE `turn-end` line on the most recently written trace and stays INERT -- the `-peek`
  before and after render the same block
- `-stats` is keyless inspection: its table renders one row per run, no run opens, nothing
  advances; `-stats -json` hands the same figures to a tool, a bad argument answers the usage;
  `-stats --blocks` renders one table per block that carried a ledger, `-stats` bare untouched
- the run's key: a key of six DIGITS names its run, never a number of days; a CLOSED run keeps
  its key, its trace saying which run it is
- `-purge` removes for good what the engine keeps of a run -- its slot or renewal mark, every
  `session-<key>.*`, every trace of its key --, by key or by age, each run under its call lock
  tried without waiting; without `--yes` it says what it would remove and writes nothing; bare,
  the usage; an unknown key refuses `run-unknown`, a malformed date `purge-invalid`; `-json`
  gives the count as one object
"""
from __future__ import annotations

import json
import os
import re
from contextlib import suppress

from conductor import instance, persistence
from conductor.state import lock, traces
from tests.harness import bench_key, holding

OLD = 1_767_225_600          # 2026-01-01 00:00 UTC: a date before the cut the case names
KEYLESS = "session-20260901T000000Z.jsonl"
CLOCK = re.compile(r"\d{2}:\d{2}:\d{2}")
RULE = re.compile(r"^\|(\s*:?-+:?\s*\|)+$")      # a markdown table's separator row


def _listing(state) -> dict[str, bytes]:
    """-> every file of the state directory and its bytes: what a refusal or a dry run never moves."""
    return {one.name: one.read_bytes() for one in sorted(state.iterdir()) if one.is_file()}


def _of(listing: dict, key: str) -> list[str]:
    """-> the files of the run `key` in a listing: its slot, its renewal mark, its trace."""
    return [name for name in listing if name.startswith(f"session-{key}.") or name.endswith(f"-{key}.jsonl")]


def _still(shown: str) -> str:
    """The block without its clocked heading -- inertness is judged on the content."""
    return "\n".join(line for line in shown.splitlines() if not CLOCK.search(line))


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """-> every markdown table of a rendering: its header's cells and its rows' cells, the
    separator row checked to carry as many columns as the header."""
    lines, found, at = text.splitlines(), [], 0
    while at < len(lines) - 1:
        if lines[at].startswith("|") and RULE.match(lines[at + 1]) \
                and len(_cells(lines[at + 1])) == len(_cells(lines[at])):
            header, rows, at = _cells(lines[at]), [], at + 2
            while at < len(lines) and lines[at].startswith("|"):
                rows.append(_cells(lines[at]))
                at += 1
            found.append((header, rows))
        else:
            at += 1
    return found


def _titled(text: str) -> bool:
    """-> whether a rendering opens on its bold title line."""
    first = text.splitlines()[:1]
    return bool(first) and first[0].startswith("**") and first[0].endswith("**")


def _json(answer) -> dict:
    with suppress(ValueError):
        return json.loads(answer.stdout)
    return {}


def _stats(bench, env, state) -> str:
    """The run read back keyless: the table, the json, the blocks. -> the run's key."""
    held, failures = bench.held, bench.failures
    conductor = env.conductor()                  # a run under way, so the traces carry something
    conductor.resume(conductor.boot("BOOT.md"))
    key = bench_key(env.made)
    slots_before = sorted(p.name for p in state.glob("session-*.json"))
    traces_before = sorted(p.name for p in state.glob("session-*.jsonl"))

    # --- keyless inspection: the table, nothing opened ----------------------------------
    told = env.cli("-stats")
    whole = _json(env.cli("-stats", "-json"))
    slots_after = sorted(p.name for p in state.glob("session-*.json"))
    traces_after = sorted(p.name for p in state.glob("session-*.jsonl"))
    tables = _tables(told.stdout)
    rows = tables[0][1] if len(tables) == 1 else []
    if (told.returncode == 0 and _titled(told.stdout) and whole.get("runs")
            and [(row[0], row[1]) for row in rows]
            == [(run["stamp"], run["key"] or "—") for run in whole["runs"]]
            and slots_after == slots_before and traces_after == traces_before):
        held("-stats is keyless inspection", f"the table renders, {len(rows)} row(s) for the "
             "runs the json names, stamp and key in their columns; no slot and no trace appear")
    else:
        failures.append(f"  ✗ stats table                rc={told.returncode} {told.stdout.splitlines()[:4]} "
                        f"{told.stderr[-200:]}")

    # --- the json form, and the usage on a bad argument -------------------------------------
    as_json = env.cli("-stats", "7", "-json")
    payload = _json(as_json)
    bad = env.cli("-stats", "yesterday")
    if (as_json.returncode == 0 and payload and payload["scope"]["days"] == 7
            and payload["period"]["runs"] >= 1 and payload["runs"][0]["exchanges"]
            and bad.returncode != 0 and "-stats" in bad.stderr and not bad.stdout):
        held("-stats -json hands the figures", "scope, runs and the period; a bad argument "
             "answers the usage")
    else:
        failures.append(f"  ✗ stats json                 rc={as_json.returncode} "
                        f"{as_json.stdout[:120]!r} bad rc={bad.returncode}")

    # --- `--blocks`: what each output carried, the bare form untouched ------------------
    per_block = env.cli("-stats", "--blocks")
    ledger = _json(env.cli("-stats", "--blocks", "-json"))
    bare_again = env.cli("-stats")
    blocks = ledger.get("blocks", [])
    served = [line for one in blocks for line in one["served"]]
    carried = _tables(per_block.stdout)
    if (per_block.returncode == 0 and _titled(per_block.stdout) and served
            and [len(rows) for _, rows in carried] == [len(one["served"]) for one in blocks]
            and all({"subject", "state", "origin", "chars"} <= set(line) for line in served)
            and bare_again.stdout == told.stdout):
        held("-stats --blocks renders what the outputs carried",
             f"one table per block ({len(blocks)} of them, {len(served)} line(s) "
             "served), the json carrying the same ledger -- and `-stats` bare renders exactly "
             "what it rendered before the flag existed")
    else:
        failures.append(f"  ✗ stats blocks               rc={per_block.returncode} "
                        f"{per_block.stdout.splitlines()[:3]} served={len(served)}")
    return key


def _keyed(bench, env, state, key: str) -> None:
    """A run named by its key among several: a key of digits, a closed run."""
    held, failures = bench.held, bench.failures
    # --- a key of six DIGITS names its run, never a number of days ---------------------
    # the key is FORGED, never drawn: a run whose key is all digits comes up 6% of the
    # time ((10/16)^6), and a bench that waits for a draw is no bench
    digits = "123456"
    standing = state / f"session-{key}.json"
    log_name = json.loads(standing.read_text(encoding="utf-8"))["log"]
    standing.rename(state / f"session-{digits}.json")
    opened_line, *rest_of_trace = (state / log_name).read_text(encoding="utf-8").splitlines()
    forged = {**json.loads(opened_line), "run": digits}      # the trace says the same key
    (state / log_name).write_text("\n".join([json.dumps(forged), *rest_of_trace]) + "\n",
                                  encoding="utf-8")
    keyed = env.cli("-stats", digits)
    named = _json(env.cli("-stats", digits, "-json"))
    by_days = _json(env.cli("-stats", "7", "-json"))
    rows = [row for _, rows in _tables(keyed.stdout) for row in rows]
    if (keyed.returncode == 0 and [row[1] for row in rows] == [digits]
            and named.get("scope") == {"days": None, "key": digits}
            and [run["key"] for run in named.get("runs", [])] == [digits]
            and by_days.get("scope") == {"days": 7, "key": None}
            and len(by_days.get("runs", [])) > 1):
        held("a key of digits names its run", f"`-stats {digits}` renders THAT run and its "
             f"one row, while `-stats 7` still reads a number of days ({len(by_days['runs'])} "
             "runs) -- the form of a key is read before a count")
    else:
        failures.append(f"  ✗ stats digit key            rc={keyed.returncode} "
                        f"{rows} {named.get('scope')} {by_days.get('scope')}")

    # --- a CLOSED run keeps its key: the trace says which run it is --------------------
    opened = json.loads((state / log_name).read_text(encoding="utf-8").splitlines()[0])
    (state / f"session-{digits}.json").unlink()          # the slot dies, the trace stays
    closed = env.cli("-stats", digits)
    rows = [row for _, rows in _tables(closed.stdout) for row in rows]
    if opened.get("run") and closed.returncode == 0 and [row[1] for row in rows] == [digits]:
        held("a closed run keeps its key", "the trace's first line says which run it is, so "
             "`-stats <key>` finds a run whose slot is gone -- and the key column fills")
    else:
        failures.append(f"  ✗ stats closed run           rc={closed.returncode} "
                        f"opened={opened} {closed.stdout.splitlines()[:4]}")


def _purge(bench, env, state, a: str, b: str, c: str) -> None:
    """`-purge` on three runs a, b, c and a keyless trace: dry, by key, under a lock, by age."""
    held, failures = bench.held, bench.failures
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
    count = _json(as_json)
    runs = count.get("runs") or []
    if (as_json.returncode == 0 and count.get("dry") is True and len(runs) == 1 and runs[0].get("key") == b
            and runs[0].get("files") and isinstance(runs[0].get("bytes"), int)
            and count.get("files") == len(runs[0]["files"]) and count.get("bytes") == runs[0]["bytes"]
            and _of(_listing(state), b)):
        held("(h) -json: the count as one object", f"dry, {count.get('files')} file(s), {count.get('bytes')} bytes")
    else:
        failures.append(f"  ✗ (h) json                    rc={as_json.returncode} {as_json.stdout[:200]!r}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("records")
    state = env.made / instance.STATE

    # --- no run yet: no stamp ------------------------------------------------------------
    bare = env.cli("-et")
    if bare.returncode == 2 and "no-run" in bare.stderr:
        held("no run, no stamp", "no-run named, nothing written")
    else:
        failures.append(f"  ✗ no-run                     rc={bare.returncode} {bare.stderr[-80:]!r}")

    first = _stats(bench, env, state)

    keys = []
    for _ in range(3):
        opened = env.cli("-new")
        if opened.returncode:
            failures.append(f"-new failed: {opened.stderr.strip()[:200]}")
            return len(failures)
        keys.append(bench_key(env.made))
    a, b, c = keys

    # --- the stamp lands on the freshest trace, the verb inert ---------------------------
    before = env.cli("-peek").stdout
    stamped = env.cli("-et")
    after = env.cli("-peek").stdout
    trace = next(iter(sorted(state.glob(f"session-*-{c}.jsonl"))), None)
    last = json.loads(trace.read_text(encoding="utf-8").splitlines()[-1]) if trace else {}
    if (stamped.returncode == 0 and trace is not None and trace.name in stamped.stdout
            and last.get("kind") == "turn-end" and _still(before) == _still(after)):
        held("the stamp lands and the verb is inert",
             "one turn-end line on the freshest trace; the -peek before and after agree")
    else:
        failures.append(f"  ✗ stamp                      rc={stamped.returncode} "
                        f"{stamped.stdout.strip()!r} {last.get('kind')!r} same={before == after}")

    (state / KEYLESS).write_text('{"at": "2026-09-01T00:00:00.000+00:00", "kind": "new"}\n', encoding="utf-8")
    _purge(bench, env, state, a, b, c)
    _keyed(bench, env, state, first)
    return len(failures)
