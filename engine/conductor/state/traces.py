"""Behaviour: reading the traces back -- what the runs cost, exchange by exchange.

The trace is written by `log.record` and never read by the engine while it
conducts; this module is the ONE reader, for the console (`-stats`), for an audit
that draws a sample, for an upkeep pass that wants the period's counters. An
EXCHANGE runs from the operator's message (the `prompt`, or the run's `new`) to
the closing that waits for the operator (`block` with `wait: true`). Inside it,
every interval belongs to the event that ends it: a piped proof owns the seconds
the agent spent writing it, a script call owns its own, a rendered block owns the
work done before the call came back. A block re-rendered by a script call (the
pending block shown again) is counted apart from the blocks that moved the flow. The
mass is read in estimated tokens first (`tokens ≈`, the figure every model bill speaks)
and in characters beside; the agent's answers are weighed apart, at their own lines.
"""
from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median

GAP = timedelta(minutes=30)          # an exchange longer than this is a hole, not a measure
PROOF = "PROVE"
WORK_KINDS = ("block", "batched", "mounted", "signal", "signal-refused", "repair",
              "repair-in-place", "refusal", "reset", "sync", "switch")


@dataclass
class Exchange:
    started: datetime
    ended: datetime | None = None
    blocks: int = 0
    reshows: int = 0
    chunks: int = 0                          # the chunks of cut outputs served on bare calls
    proofs: int = 0
    repairs: int = 0
    refusals: int = 0
    gestures: int = 0
    laps: int = 0                            # the laps of the iterated doors opened in the exchange
    execs: int = 0                           # the `exec:` played at the documents' entries
    switches: int = 0                        # the packages switched out of the play, or back in
    mass: int | None = None                  # None: no block of this exchange carried a weight
    tokens: int | None = None                # None: no block carried a token estimate
    parts: dict[str, int] = field(default_factory=dict)
    given: dict[str, int] = field(default_factory=lambda: {"chars": 0, "tokens": 0})
                                             # the agent's answers, weighed at the source
    seconds: dict[str, float] = field(default_factory=lambda: {"work": 0.0, "proof": 0.0,
                                                               "gesture": 0.0, "answer": 0.0})

    @property
    def duration(self) -> timedelta | None:
        return None if self.ended is None else self.ended - self.started

    @property
    def gap(self) -> bool:
        return self.duration is not None and self.duration > GAP

    def as_dict(self) -> dict:
        return {"started": self.started.isoformat(timespec="seconds"),
                "ended": self.ended.isoformat(timespec="seconds") if self.ended else None,
                "seconds": round(self.duration.total_seconds(), 1) if self.duration else None,
                "gap": self.gap, "blocks": self.blocks, "reshows": self.reshows,
                "proofs": self.proofs, "repairs": self.repairs,
                "refusals": self.refusals, "gestures": self.gestures, "laps": self.laps,
                "execs": self.execs, "switches": self.switches, "mass": self.mass,
                "tokens": self.tokens, "parts": dict(self.parts), "given": dict(self.given),
                "spent": {key: round(value, 1) for key, value in self.seconds.items()}}


@dataclass
class Run:
    path: Path
    key: str
    exchanges: list[Exchange]

    @property
    def stamp(self) -> str:
        return _stamp_of(self.path)

    def as_dict(self) -> dict:
        return {"trace": self.path.name, "key": self.key, "stamp": self.stamp,
                "exchanges": [one.as_dict() for one in self.exchanges],
                **_totals(self.exchanges)}


def read(path: Path) -> list[dict]:
    """-> the events of one trace, in order; a line that is not JSON is skipped."""
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def exchanges(events: list[dict]) -> list[Exchange]:
    """-> the exchanges of one trace, closed or not (the last may still be open)."""
    found: list[Exchange] = []
    current: Exchange | None = None
    previous_at: datetime | None = None
    previous_kind = ""
    for event in events:
        at = _at(event)
        kind = event.get("kind", "")
        if at is None:
            continue
        if kind in ("cut", "chunk") and found and (current is None or not current.blocks):
            # the rest of a block that closed its exchange: read before the operator's
            # next message, it belongs to the exchange that block closed
            if kind == "chunk":
                found[-1].chunks += 1
            continue
        if current is None:
            current = Exchange(started=at)
            previous_at, previous_kind = at, kind
            if kind in ("new", "prompt"):
                continue
        if kind in ("new", "prompt"):
            # the operator's message opens the next exchange -- its own interval is
            # the operator's time, never the conduction's
            current.started = at
            previous_at, previous_kind = at, kind
            continue
        elapsed = (at - previous_at).total_seconds() if previous_at else 0.0
        if kind == "answer":
            weighed = event.get("weight")
            if isinstance(weighed, dict):          # an older engine wrote no weight here
                for key in ("chars", "tokens"):
                    current.given[key] = current.given.get(key, 0) + int(weighed.get(key, 0))
            if event.get("instruction", "").strip() == PROOF:
                current.proofs += 1
                current.seconds["proof"] += elapsed
            else:
                current.seconds["answer"] += elapsed
        elif kind == "gesture":
            current.gestures += 1
            current.seconds["gesture"] += elapsed
        else:
            current.seconds["work"] += elapsed
            if kind == "block":
                if previous_kind == "gesture":
                    current.reshows += 1
                else:
                    current.blocks += 1
                weight = event.get("weight")
                if isinstance(weight, dict):
                    current.mass = (current.mass or 0) + int(weight.get("total", 0))
                    if "tokens" in weight:
                        current.tokens = (current.tokens or 0) + int(weight["tokens"])
                    for part, value in weight.items():
                        if part not in ("total", "tokens"):
                            current.parts[part] = current.parts.get(part, 0) + int(value)
            elif kind == "chunk":
                current.chunks += 1
            elif kind in ("repair", "repair-in-place"):
                current.repairs += 1
            elif kind == "refusal":
                current.refusals += 1
            elif kind == "lap":
                current.laps += 1
            elif kind == "exec":
                current.execs += 1
            elif kind == "switch":
                current.switches += 1
        previous_at, previous_kind = at, kind
        if kind == "block" and event.get("wait"):
            current.ended = at
            found.append(current)
            current = None
    if current is not None and (current.blocks or current.proofs or current.gestures):
        found.append(current)              # the exchange under way: open, said as such
    return found


def runs(state: Path, days: int | None = None, key: str | None = None) -> list[Run]:
    """-> the runs of an instance's state directory, oldest first: every trace within
    `days` (all of them when None), or the ONE trace a run's key maps to."""
    if not state.is_dir():
        return []
    keyed = _keys(state)
    chosen = []
    for path in sorted(state.glob("session-*.jsonl")):
        if key is not None and keyed.get(path.name) != key:
            continue
        opened = _opened(path)
        if days is not None and opened is not None \
                and opened < datetime.now(timezone.utc) - timedelta(days=days):
            continue
        chosen.append(Run(path=path, key=keyed.get(path.name, ""), exchanges=exchanges(read(path))))
    return chosen


def summary(found: list[Run]) -> dict:
    """-> the period's figures: the totals over every run, and the durations' shape
    over the closed exchanges that are not holes."""
    every = [one for run in found for one in run.exchanges]
    totals = _totals(every)
    return {"runs": len(found), **totals}


def blocks(found: list[Run]) -> list[dict]:
    """-> one entry per BLOCK that served something, in the traces' order: its stack, its
    weight and the LEDGER the engine wrote -- what entered the output, in the order it
    entered, each line saying where it came from and who asked. A trace written by an
    older engine carries no ledger and yields nothing here."""
    found_blocks = []
    for run in found:
        for event in read(run.path):
            if event.get("kind") != "block" or not event.get("served"):
                continue
            found_blocks.append({"run": run.key or run.path.name, "at": event.get("at", ""),
                                 "stack": event.get("stack", ""),
                                 "weight": event.get("weight") or {},
                                 "served": list(event.get("served") or [])})
    return found_blocks


def render_blocks(found: list[Run], days: int | None, key: str | None) -> str:
    """The operator's table of what the OUTPUTS carried: one table per block, its lines in
    the order they were served -- the subject, its state, where it came from, the document
    that asked, its package and its mass. The run's own total closes it."""
    scope = (f"run {key}" if key else f"the last {days} day(s)" if days is not None
             else "every trace")
    every = blocks(found)
    if not every:
        return (f"**pp -- what the blocks carried, {scope}**\n\nNo block of these traces "
                "carries a ledger: the engine that wrote them did not say where its matter "
                "came from.")
    head = [f"**pp -- what the blocks carried, {scope}**"]
    total_chars = total_tokens = 0
    for n, one in enumerate(every, 1):
        weight = one["weight"]
        head += ["", f"**{n}. {one['stack']}** -- {_mass(weight.get('total'))} c, "
                     f"tokens ≈ {_mass(weight.get('tokens'))}"
                     f" (payload {_mass(weight.get('payload'))} c)", "",
                 "| # | subject | state | origin | asked by | package | c | ≈ tk |",
                 "|---:|---|---|---|---|---|---:|---:|"]
        for rank, line in enumerate(one["served"], 1):
            origin = str(line.get("origin", ""))
            for key_, mark in (("nature", ""), ("with", "← "), ("at", "@ ")):
                if line.get(key_):
                    origin += f" ({mark}{line[key_]})"
            said = _mass(line.get("chars"))
            if line.get("state") == "spared" and line.get("spared"):
                said = f"— (spared {_mass(line['spared'])})"
            head.append(f"| {rank} | {line.get('subject', '')} | {line.get('state', '')}"
                        f" | {origin} | {line.get('by') or '—'} | {line.get('package') or '—'}"
                        f" | {said} | {_mass(line.get('tokens')) if line.get('chars') else '—'} |")
            total_chars += int(line.get("chars") or 0)
            total_tokens += int(line.get("tokens") or 0)
    head += ["", f"{len(every)} block(s) carrying a ledger -- {_mass(total_chars)} c served, "
                 f"tokens ≈ {_mass(total_tokens)}"]
    return "\n".join(head)


def render(found: list[Run], days: int | None, key: str | None) -> str:
    """The operator's table: one row per run, the period's line last."""
    scope = (f"run {key}" if key else f"the last {days} day(s)" if days is not None
             else "every trace")
    head = [f"**pp -- what the runs cost, {scope}**", "",
            "| run | key | exchanges | blocks (+reshows) | tokens ≈ | mass | proofs | repairs |"
            " refusals | script calls | median | mean | p90 |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    rows = []
    for run in found:
        t = _totals(run.exchanges)
        rows.append(f"| {run.stamp} | {run.key or '—'} | {t['exchanges']}"
                    f"{' (' + str(t['open']) + ' open)' if t['open'] else ''}"
                    f" | {t['blocks']} (+{t['reshows']}) | {_mass(t['tokens'])} | {_mass(t['mass'])}"
                    f" | {t['proofs']}"
                    f" | {t['repairs']} | {t['refusals']} | {t['gestures']}"
                    f" | {_clock(t['median'])} | {_clock(t['mean'])} | {_clock(t['p90'])} |")
    period = summary(found)
    tail = ["", f"{period['runs']} run(s), {period['exchanges']} exchange(s)"
            f"{' (' + str(period['open']) + ' open)' if period['open'] else ''}"
            f", {period['gaps']} hole(s) over {GAP.seconds // 60} min excluded from the durations"
            f" -- {period['blocks']} block(s) + {period['reshows']} reshow(s) + {period['chunks']} chunk(s), tokens ≈ {_mass(period['tokens'])},"
            f" mass {_mass(period['mass'])} ({_parts(period['parts'])}); the agent's answers tokens ≈"
            f" {_mass(period['given']['tokens'])} ({_mass(period['given']['chars'])} chars);"
            f" {period['proofs']} proof(s),"
            f" {period['repairs']} repair(s), {period['refusals']} refusal(s), {period['gestures']} script call(s), {period['laps']} lap(s),"
            f" {period['execs']} exec(s), {period['switches']} switch(es);"
            f" time conducted {_clock(period['conducted'])} -- work {_clock(period['spent']['work'])},"
            f" proofs {_clock(period['spent']['proof'])}, script calls {_clock(period['spent']['gesture'])},"
            f" answers {_clock(period['spent']['answer'])}"]
    return "\n".join(head + rows + tail)


def render_json(found: list[Run], days: int | None, key: str | None) -> str:
    return json.dumps({"scope": {"days": days, "key": key}, "runs": [one.as_dict() for one in found],
                       "period": summary(found)}, ensure_ascii=False, indent=1)


# --- helpers -----------------------------------------------------------------------

def _at(event: dict) -> datetime | None:
    try:
        return datetime.fromisoformat(str(event.get("at", "")))
    except ValueError:
        return None


def _stamp_of(path: Path) -> str:
    raw = path.name[len("session-"):].split(".")[0].rstrip("Z")
    try:
        return datetime.strptime(raw[:15], "%Y%m%dT%H%M%S").strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return path.stem


def _opened(path: Path) -> datetime | None:
    raw = path.name[len("session-"):].split(".")[0].rstrip("Z")
    try:
        return datetime.strptime(raw[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _keys(state: Path) -> dict[str, str]:
    """-> trace file name -> run key. The SLOT answers first -- the standing runs, as
    it always did; a trace no slot claims says which run it is itself, at its opening
    line, so a CLOSED run keeps its key. A trace written before that line carried the
    run is left keyless, exactly as it was."""
    found = {}
    for slot in state.glob("session-*.json"):
        try:
            data = json.loads(slot.read_text(encoding="utf-8"))
        except ValueError:
            continue
        log_name = str(data.get("log", ""))
        if log_name:
            found[log_name] = slot.stem[len("session-"):]
    for trace in state.glob("session-*.jsonl"):
        if trace.name in found:
            continue
        with contextlib.suppress(OSError, ValueError):
            with trace.open(encoding="utf-8") as handle:
                opened = json.loads(handle.readline() or "{}")
            if opened.get("kind") == "new" and opened.get("run"):
                found[trace.name] = str(opened["run"])
    return found


def _totals(every: list[Exchange]) -> dict:
    closed = [one for one in every if one.ended is not None and not one.gap]
    durations = sorted(one.duration.total_seconds() for one in closed)
    masses = [one.mass for one in every if one.mass is not None]
    estimates = [one.tokens for one in every if one.tokens is not None]
    given = {"chars": 0, "tokens": 0}
    parts: dict[str, int] = {}
    spent = {"work": 0.0, "proof": 0.0, "gesture": 0.0, "answer": 0.0}
    for one in every:
        for part, value in one.parts.items():
            parts[part] = parts.get(part, 0) + value
        for key, value in one.given.items():
            given[key] = given.get(key, 0) + value
        for bucket, value in one.seconds.items():
            spent[bucket] = spent.get(bucket, 0.0) + value
    return {
        "exchanges": len(every),
        "open": sum(1 for one in every if one.ended is None),
        "gaps": sum(1 for one in every if one.gap),
        "blocks": sum(one.blocks for one in every),
        "reshows": sum(one.reshows for one in every),
        "chunks": sum(one.chunks for one in every),
        "laps": sum(one.laps for one in every),
        "execs": sum(one.execs for one in every),
        "switches": sum(one.switches for one in every),
        "mass": sum(masses) if masses else None,
        "tokens": sum(estimates) if estimates else None,
        "parts": parts,
        "given": given,
        "proofs": sum(one.proofs for one in every),
        "repairs": sum(one.repairs for one in every),
        "refusals": sum(one.refusals for one in every),
        "gestures": sum(one.gestures for one in every),
        "median": median(durations) if durations else None,
        "mean": mean(durations) if durations else None,
        "p90": durations[min(len(durations) - 1, int(round(0.9 * (len(durations) - 1))))]
        if durations else None,
        "conducted": sum(durations),
        "spent": {key: round(value, 1) for key, value in spent.items()},
    }


def _clock(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m{seconds % 60:02d}"
    return f"{seconds // 3600}h{(seconds % 3600) // 60:02d}"


def _mass(value: int | None) -> str:
    return "—" if value is None else f"{value:,}".replace(",", " ")


def _parts(parts: dict[str, int]) -> str:
    if not parts:
        return "no weight in these traces"
    return ", ".join(f"{name} {_mass(value)}" for name, value in sorted(parts.items()))
