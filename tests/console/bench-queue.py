"""Scenario `bench-queue` -- the machine's queue of tokens, judged on real passes of a throwaway
source: the harness under test copied beside witness areas whose scenarios sleep, every pass
launched in its own process on a throwaway queue (`PP_BENCH_QUEUE`) with a CPU target worth a
few tokens on this machine, a memory target that never refuses, CPU counters that never move
(`PP_BENCH_STAT`: the verdict owes nothing to the machine's load) and a throwaway cache
(`XDG_CACHE_HOME`) -- the machine's own queue is never touched:
- two passes side by side: a pass of four arriving behind a pass of twenty takes the next token
  a scenario of the big one gives back, then one token in two, and ends before the big one has
  played half of its own; exactly as many scenarios at once as the tokens at most, both passes
  counted; the passes read the still counters; the header says the tokens and the passes ahead
  in the ring, the line under the table the longest wait and the pass's whole wait
- a `-serial` pass beside a wide one: the turn goes to the passes asking for a token, so the wide
  one takes several while the serial one plays a scenario
- a pass killed alone (SIGKILL on its pid, its workers left alive): the pass waiting behind it gets
  the tokens back and ends, no scenario of the dead pass starts after its death, and the queue
  names it no more
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

from tests import harness
from tests.harness import ENGINE, HERE

SLEEPER = '''import json
import os
import time


def scenario(bench):
    started = time.time()
    time.sleep({seconds})
    with open({log!r}, "a", encoding="utf-8") as out:
        out.write(json.dumps({{"pass": {label!r}, "pid": os.getpid(), "start": started,
                               "end": time.time()}}) + "\\n")
    bench.held("slept")
    return 0
'''

LAUNCH = ("import sys; sys.path[:0] = [sys.argv.pop(1), sys.argv.pop(1)]; "
          "from tests.harness import run; sys.exit(run(sys.argv[1:]))")

TOKENS = 2                 # what the CPU target is worth on this machine
NAP = 0.4                  # seconds: a witness scenario's sleep
BIG, SMALL = 20, 4
STILL = "cpu  1000 0 0 1000 0 0 0 0 0 0\n"     # CPU counters that never move: no load is ever read


class _House:
    """A throwaway source -- the harness under test and the witness areas -- and the
    environment its passes run in: a queue, a cache, the targets of the case."""

    def __init__(self, bench, areas: dict[str, tuple[int, float]], tokens: int = TOKENS) -> None:
        self.root = bench.temp() / "source"
        tests = self.root / "tests"
        tests.mkdir(parents=True)
        shutil.copy(HERE / "harness.py", tests / "harness.py")
        shutil.copy(HERE / "__init__.py", tests / "__init__.py")
        self.log = bench.temp() / "slept.jsonl"
        self.log.touch()
        for label, (count, seconds) in areas.items():
            (tests / label).mkdir()
            for one in range(count):
                (tests / label / f"s-{one:02d}.py").write_text(
                    SLEEPER.format(seconds=seconds, log=str(self.log), label=label), encoding="utf-8")
        self.queue = bench.temp() / "queue"
        self.stat = bench.temp() / "stat"
        self.stat.write_text(STILL, encoding="utf-8")
        cores = os.cpu_count() or 1
        self.env = {name: value for name, value in os.environ.items() if name != "UV_CACHE_DIR"}
        self.env.update({"XDG_CACHE_HOME": str(bench.temp()), "PP_BENCH_QUEUE": str(self.queue),
                         "PP_BENCH_CPU": f"{(tokens + 0.5) * 100 / cores:.6f}",
                         "PP_BENCH_MEMORY": "100", "PP_BENCH_STAT": str(self.stat)})
        self.launched: list[subprocess.Popen] = []

    def launch(self, label: str, *flags: str) -> subprocess.Popen:
        """A pass of one witness area, in its own process group -- the cleanup takes its workers."""
        one = subprocess.Popen([sys.executable, "-c", LAUNCH, str(ENGINE), str(self.root), label, *flags],
                               cwd=self.root, env=self.env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, start_new_session=True)
        self.launched.append(one)
        return one

    def state(self) -> dict | None:
        """-> the queue's state as the harness reads it, None when the harness keeps no queue."""
        snapshot, queue_of = getattr(harness, "snapshot", None), getattr(harness, "queue_of", None)
        if snapshot is None or queue_of is None:
            return None
        return snapshot(queue_of({"PP_BENCH_QUEUE": str(self.queue)}))

    def slept(self) -> list[dict]:
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line]

    def close(self) -> None:
        """Every process of every pass gone -- an orphan worker of a pass killed alone with them."""
        for one in self.launched:
            with _quiet():
                os.killpg(one.pid, signal.SIGKILL)
            one.wait()


class _quiet:
    def __enter__(self):
        return self

    def __exit__(self, kind, *_) -> bool:
        return kind is not None and issubclass(kind, ProcessLookupError)


def _until(holds, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if holds():
            return True
        time.sleep(0.02)
    return holds()


def _in_ring(state: dict | None, pid: int) -> bool:
    return bool(state) and any(one.get("pass") == pid for one in state.get("ring", []))


def _holds(state: dict | None, pid: int) -> bool:
    return bool(state) and any(one.get("pass") == pid for one in state.get("tokens", []))


def _said(form: str | None, output: str) -> dict | None:
    """-> the fields of the line the harness prints from `form`, read back from a pass's output."""
    if not form:
        return None
    pattern = re.sub(r"\\\{(\w+)[^}]*\}", lambda m: f"(?P<{m.group(1)}>.+?)", re.escape(form))
    found = re.search(rf"^(?:pp: |\s*){pattern}$", output, re.M)
    return found.groupdict() if found else None


def _most(intervals: list[tuple[float, float]]) -> int:
    """-> the most intervals open at once."""
    edges = sorted([(start, 1) for start, _ in intervals] + [(end, -1) for _, end in intervals])
    most = now = 0
    for _, step in edges:
        now += step
        most = max(most, now)
    return most


def _ring(bench) -> None:
    """Two passes side by side: the late small one is served in turn, the tokens are never exceeded."""
    held, failures = bench.held, bench.failures
    house = _House(bench, {"big": (BIG, NAP), "small": (SMALL, NAP)})
    seen: dict = {}

    def entered(pid: int) -> bool:
        state = house.state()
        entry = next((one for one in (state or {}).get("ring", []) if one.get("pass") == pid), None)
        if entry is not None:
            seen[pid] = entry.get("arrived")
        return entry is not None

    try:
        big = house.launch("big")
        joined = _until(lambda: entered(big.pid) or any(one["pass"] == "big" for one in house.slept()), 8)
        small = house.launch("small")
        _until(lambda: entered(small.pid) or small.poll() is not None, 8)
        small_out, _ = small.communicate(timeout=30)
        big_out, _ = big.communicate(timeout=30)
    finally:
        house.close()
    slept = house.slept()
    bigs = sorted(one["end"] for one in slept if one["pass"] == "big")
    smalls = sorted(one["end"] for one in slept if one["pass"] == "small")
    most = _most([(one["start"], one["end"]) for one in slept])
    if (joined and big.returncode == 0 and small.returncode == 0 and len(bigs) == BIG
            and len(smalls) == SMALL and most == TOKENS):
        held("the tokens bound both passes", f"{BIG} and {SMALL} scenarios, {TOKENS} tokens: "
             f"{most} played at once at most, the bound reached")
    else:
        failures.append(f"  ✗ the tokens' bound           rc={big.returncode}/{small.returncode} "
                        f"slept={len(bigs)}/{len(smalls)} most={most} joined={joined}")

    read = (house.state() or {}).get("cpu") or {}
    if read.get("total") == sum(int(one) for one in STILL.split()[1:9]):
        held("the passes read the still counters", "PP_BENCH_STAT names the CPU counters a "
             "throwaway pass reads: no load of the machine moves the verdict")
    else:
        failures.append(f"  ✗ the CPU counters read       {read!r}")

    arrived = seen.get(small.pid)
    starts = sorted(slept, key=lambda one: one["start"])
    first = next((one["start"] for one in starts if one["pass"] == "small"), None)
    freed = min((end for end in bigs if arrived is not None and end >= arrived), default=None)
    turns = [one["pass"] for one in starts if first is not None and one["start"] >= first][:2 * SMALL - 1]
    done_before = sum(1 for end in bigs if smalls and end <= smalls[-1])
    if (first is not None and freed is not None and first <= freed + 0.15
            and turns == (["small", "big"] * SMALL)[:2 * SMALL - 1] and done_before < BIG // 2):
        held("the late pass is served in turn", f"its first token comes {first - freed:+.2f}s after "
             f"a scenario of the big one ends, then one in two; it ends with {done_before} of the "
             f"big one's {BIG} played")
    else:
        failures.append(f"  ✗ the ring                    arrived={arrived} first={first} freed={freed} "
                        f"turns={turns} big done={done_before}")

    header = _said(getattr(harness, "QUEUE_SAID", None), small_out or "")
    waited = _said(getattr(harness, "WAIT_SAID", None), small_out or "")
    if (header and int(header["tokens"]) == TOKENS and int(header["passes"]) == 1
            and waited and float(waited["total"]) >= float(waited["longest"]) > 0):
        held("the pass says the queue", f"{header['tokens']} tokens, {header['passes']} pass "
             f"ahead at its entry; the longest wait {waited['longest']}s, {waited['total']}s in all")
    else:
        failures.append(f"  ✗ the pass's lines            header={header} waited={waited} "
                        f"{(small_out or '').splitlines()[:3]!r}")


def _turns(bench) -> None:
    """A -serial pass beside a wide one: the turn goes to the passes asking for a token."""
    held, failures = bench.held, bench.failures
    house = _House(bench, {"narrow": (3, 1.0), "wide": (8, 0.3)}, tokens=3)
    try:
        narrow = house.launch("narrow", "-serial")
        _until(lambda: _holds(house.state(), narrow.pid), 8)
        wide = house.launch("wide")
        narrow.communicate(timeout=30)
        wide.communicate(timeout=30)
    finally:
        house.close()
    slept = house.slept()
    played = sorted((one for one in slept if one["pass"] == "narrow"), key=lambda one: one["start"])
    wides = [one for one in slept if one["pass"] == "wide"]
    started = [sum(1 for other in wides if one["start"] < other["start"] < one["end"])
               for one in played[:-1]]           # the last one granted, the serial pass waits no more
    most = _most([(one["start"], one["end"]) for one in slept])
    if (narrow.returncode == 0 and wide.returncode == 0 and len(played) == 3 and len(wides) == 8
            and max(started, default=0) >= 2 and most <= 3):
        held("the turn goes to the passes asking", f"a -serial pass beside a wide one, 3 tokens: "
             f"{started} scenarios of the wide one start during the serial scenarios granted while it still waits, {most} at once")
    else:
        failures.append(f"  ✗ the turn of a serial pass    rc={narrow.returncode}/{wide.returncode} "
                        f"slept={len(played)}/{len(wides)} started={started} most={most}")


def _killed(bench) -> None:
    """A pass killed alone gives its tokens back: its orphan workers start nothing, the one behind it ends."""
    held, failures = bench.held, bench.failures
    house = _House(bench, {"victim": (6, 0.5), "survivor": (2, 0.2)})
    died, state = None, None
    try:
        victim = house.launch("victim")
        holding = _until(lambda: sum(1 for one in (house.state() or {}).get("tokens", [])
                                     if one.get("pass") == victim.pid) == TOKENS, 8)
        survivor = house.launch("survivor")
        waiting = _until(lambda: _in_ring(house.state(), survivor.pid), 8)
        os.kill(victim.pid, signal.SIGKILL)          # the pass alone: its workers live on
        victim.wait()
        died = time.time()
        try:
            survivor.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            pass
        time.sleep(1.2)                              # what an orphan worker would still play
        state = house.state()
    finally:
        house.close()
    named = [one for one in (state or {}).get("ring", []) + (state or {}).get("tokens", [])
             if one.get("pass") == victim.pid]
    ended = [one for one in house.slept() if one["pass"] == "survivor"]
    orphans = [one for one in house.slept() if one["pass"] == "victim" and died and one["start"] > died]
    if (holding and waiting and survivor.returncode == 0 and len(ended) == 2 and state is not None
            and not named and not orphans):
        held("a killed pass gives its tokens back", "its pid killed alone while it held its tokens: "
             "the pass waiting behind it ends, no scenario of the dead one starts after its death, "
             "the queue names it no more")
    else:
        failures.append(f"  ✗ the killed pass             holding={holding} waiting={waiting} "
                        f"rc={survivor.returncode} ended={len(ended)} orphans={len(orphans)} "
                        f"named={named} state={state is not None}")


def scenario(bench) -> int:
    _ring(bench)
    _turns(bench)
    _killed(bench)
    return 0
