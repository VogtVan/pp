"""Scenario `records-verb` -- `./pp records`, the operator's and the agent's read of the records'
store (theme les-records-bornes, target socle-exploitation), 7 case(s):
- (a) `list`: each record with its count and its first and last dates, in a table or `--json`
- (b) `read`, `count` and `search`, their filters in options, in a table or `--json` -- `rows`,
  `total`, `bound`, `next` -- the same figures as the store's own query
- (c) an output holds under `max_harness_tool_output`: the page shrinks until it fits, says
  how many entries it shows, and the call that reads the rest -- replayed, it reads the next
  entries; in a table a body is an excerpt around the text searched
  -- a search over three records of entries of 20 000 c, a body of 20 000 quotes, a count of
  100 groups of values of 2 000 c: each output measured under the cap, `--json` and table
- (d) a wrong use refuses by its code -- `records-usage`, `record-unknown`, `filter-invalid`,
  `match-short` -- exit 2, nothing on stdout; the filters are judged before the record is known
- (e) nothing is written: the base and its files are the same after each call
- (f) beside a WAL a killed writer left, a read serves its entries and moves neither the base nor
  the WAL (the `-shm` index, SQLite's shared memory, is no data)
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys

from conductor import store
from conductor.core import messages

CAP = 12000
KILLED = """import os, sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from conductor import store
held = store.of(Path(sys.argv[2]))
reader = held._connected(False, True)
reader.__enter__().count("journal")          # a reader holds its snapshot: no checkpoint passes it
for n in range(10):
    held.append("journal", {"text": f"stranded {n}"})
os._exit(0)                                  # killed: the WAL stays, its entries not checkpointed
"""


def _state(made) -> dict:
    """-> every file under the records' directory with its size and its time -- what a write moves."""
    root = made / ".sys" / "records"
    return {str(path.relative_to(root)): (path.stat().st_size, path.stat().st_mtime_ns)
            for path in sorted(root.rglob("*")) if path.is_file()}


def _code(done) -> str | None:
    """-> the code of the refusal a call wrote on stderr, None when it refused nothing."""
    for line in done.stderr.splitlines():
        found = messages.read_refused(line)
        if found:
            return found[0]
    return None


def _cap(env, cap: int) -> None:
    path = env.made / "SETTINGS.md"
    path.write_text(re.sub(r"^max_harness_tool_output: \d+", f"max_harness_tool_output: {cap}",
                           path.read_text(encoding="utf-8"), count=1, flags=re.M), encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("records-verb")
    kept = store.of(env.made)
    env.filled("journal", 150)
    kept.extend("notes", [{"key": f"note-{n}", "body": {"n": n, "text": f"note {n} on the QUARTZ shelf"}}
                          for n in range(5)])
    kept.extend("big", [{"key": f"b{n}", "body": {"n": n, "text": ("x" * 900) + f" NEEDLE-{n} " + ("y" * 1100)}}
                        for n in range(40)])
    calls, moved = [], []

    def call(*args):
        before = _state(env.made)
        done = env.cli("records", *args)
        calls.append(args)
        if _state(env.made) != before:
            moved.append(args)
        return done

    # --- (a) list -------------------------------------------------------------------------
    listed = call("list", "--json")
    table = call("list")
    said = json.loads(listed.stdout) if listed.returncode == 0 else {}
    rows = {one["record"]: one for one in said.get("rows", [])}
    if (listed.returncode == 0 and table.returncode == 0 and set(rows) == {"journal", "notes", "big"}
            and rows["journal"]["total"] == 150 and rows["notes"]["total"] == 5
            and rows["journal"]["first"] <= rows["journal"]["last"]
            and all(name in table.stdout for name in rows)):
        held("(a) list says each record", "its count, its first and last dates, in a table and in --json")
    else:
        failures.append(f"  ✗ (a) list                    {listed.returncode} {listed.stdout[:300]!r} {listed.stderr[-300:]!r}")

    # --- (b) read, count, search ---------------------------------------------------------
    read = call("read", "journal", "--last", "10", "--prefix", "k1", "--json")
    page = json.loads(read.stdout) if read.returncode == 0 else {}
    same = kept.read("journal", last=10, prefix="k1")
    counted = call("count", "journal", "--group", "day", "--json")
    groups = json.loads(counted.stdout) if counted.returncode == 0 else {}
    bare = call("count", "notes", "--match", "quartz", "--json")
    searched = call("search", "quartz", "--json")
    found = json.loads(searched.stdout) if searched.returncode == 0 else {}
    tables = [call("read", "notes", "--where", "n=3"), call("count", "notes"), call("search", "QUARTZ")]
    if (page and [one["seq"] for one in page["rows"]] == [one.seq for one in same.rows]
            and page["total"] == same.total and page["bound"] == same.bound == 10
            and page["next"] == same.next and {"rows", "total", "bound", "next"} <= set(page)
            and groups.get("total") == 1 and groups["rows"][0][1] == 150
            and json.loads(bare.stdout).get("total") == 5
            and found.get("pages", {}).get("notes", {}).get("total") == 5
            and found["pages"].get("journal", {}).get("total") == 0
            and all(one.returncode == 0 and one.stdout for one in tables)
            and "note-3" in tables[0].stdout and "note-2" not in tables[0].stdout):
        held("(b) read, count and search", "their filters in options, --json the store's own figures, "
             "a table otherwise")
    else:
        failures.append(f"  ✗ (b) read/count/search      {read.stdout[:300]!r} {read.stderr[-300:]!r} "
                        f"{counted.stdout[:200]!r} {searched.stdout[:200]!r}")

    # --- (c) under the cap ---------------------------------------------------------------
    _cap(env, CAP)
    shrunk = call("read", "big", "--json")
    first = json.loads(shrunk.stdout) if shrunk.returncode == 0 else {}
    rest = call(*shlex.split(first.get("call", "./pp records"))[2:]) if first.get("call") else None
    second = json.loads(rest.stdout) if rest is not None and rest.returncode == 0 else {}
    excerpt = call("read", "big", "--match", "needle-39")
    widest = max((len(line) for line in excerpt.stdout.splitlines()), default=0)
    if (first and len(shrunk.stdout) <= CAP and 0 < first["shown"] < 40 and first["total"] == 40
            and len(first["rows"]) == first["shown"] and rest is not None and len(rest.stdout) <= CAP
            and second and max(one["seq"] for one in second["rows"]) < min(one["seq"] for one in first["rows"])
            and excerpt.returncode == 0 and "NEEDLE-39" in excerpt.stdout and widest < 400):
        held("(c) an output holds under the cap", f"{first['shown']} of 40 entries of 2 000 c in "
             f"{len(shrunk.stdout)} c, the call of the rest replayed; a table shows an excerpt")
    else:
        failures.append(f"  ✗ (c) under the cap          {len(shrunk.stdout)} {first.get('shown')} "
                        f"{first.get('call')!r} {shrunk.stderr[-300:]!r} {widest}")
    for name in ("wide-a", "wide-b", "wide-c"):
        kept.extend(name, [{"body": {"text": f"WIDE {name} " + "w" * 20000}} for _ in range(2)])
    kept.append("quotes", {"text": "QUOTED " + '"' * 20000})
    kept.extend("groups", [{"body": {"label": f"{n:03d}" + "g" * 2000}} for n in range(100)])
    heavy = {"search --json": call("search", "WIDE", "--json"), "search": call("search", "WIDE"),
             "quotes --json": call("read", "quotes", "--json"), "quotes": call("read", "quotes"),
             "groups --json": call("count", "groups", "--group", "label", "--json"),
             "groups": call("count", "groups", "--group", "label")}
    sizes = {name: (done.returncode, len(done.stdout)) for name, done in heavy.items()}
    parsed = {name: json.loads(done.stdout) for name, done in heavy.items()
              if name.endswith("--json") and done.returncode == 0}
    if (all(rc == 0 and 0 < size <= CAP for rc, size in sizes.values())
            and all(page["shown"] >= 1 for page in parsed["search --json"]["pages"].values() if page["total"])
            and sum(1 for page in parsed["search --json"]["pages"].values() if page["total"]) == 3
            and parsed["quotes --json"]["shown"] == 1 and parsed["groups --json"]["total"] == 100
            and 0 < parsed["groups --json"]["shown"] <= 100):
        held("(c) the heavy outputs hold under the cap", ", ".join(f"{name} {size} c" for name, (_, size)
                                                                  in sizes.items()))
    else:
        failures.append(f"  ✗ (c) heavy outputs           {sizes}")
    _cap(env, 25000)

    # --- (d) the refusals ----------------------------------------------------------------
    wrong = {"records-usage": [(), ("drop", "journal"), ("read",), ("read", "journal", "--colour", "red"),
                               ("list", "extra"), ("count", "journal", "--after", "3"),
                               ("count", "journal", "--group", "day", "--before", "9")],
             "record-unknown": [("read", "nowhere"), ("count", "nowhere")],
             "filter-invalid": [("read", "journal", "--since", "someday"), ("read", "journal", "--last", "0"),
                                ("read", "nowhere", "--since", "someday"),
                                ("count", "groups", "--group", "label", "--order", "asc"),
                                ("count", "nowhere", "--last", "3"), ("count", "nowhere", "--order", "asc")],
             "match-short": [("search", "ab"), ("search", "ab", "--records", "nowhere")]}
    def refusal(args) -> str | None:
        done = call(*args)
        return "stdout" if done.stdout or done.returncode != 2 else _code(done)

    said = {code: [refusal(args) for args in uses] for code, uses in wrong.items()}
    if all(found == [code] * len(uses) for (code, uses), found in zip(wrong.items(), said.values())):
        held("(d) a wrong use refuses by its code", ", ".join(wrong) + " -- nothing on stdout")
    else:
        failures.append(f"  ✗ (d) refusals                {said}")
    bench.refusals += sum(len(uses) for uses in wrong.values())

    # --- (e) nothing written -------------------------------------------------------------
    if not moved and (env.made / ".sys" / "records" / "records.db").is_file():
        held("(e) records never writes", f"{len(calls)} calls, the base and its files unchanged after each")
    else:
        failures.append(f"  ✗ (e) a call wrote            {moved}")

    # --- (f) a WAL left by a killed writer ------------------------------------------------
    killed = subprocess.run([sys.executable, "-c", KILLED, str(env.made / ".sys" / "engine"), str(env.made)],
                            capture_output=True, text=True, timeout=60)
    root = env.made / ".sys" / "records"

    def data() -> dict:
        return {name: ((root / name).stat().st_size, (root / name).stat().st_mtime_ns)
                if (root / name).exists() else None for name in ("records.db", "records.db-wal")}

    before = data()
    beside = [env.cli("records", *args) for args in (("read", "journal", "--last", "5", "--json"),
                                                     ("list", "--json"), ("count", "journal"))]
    after = data()
    read = json.loads(beside[0].stdout) if beside[0].returncode == 0 else {}
    texts = [one["body"].get("text") for one in read.get("rows", [])]
    if (killed.returncode == 0 and before["records.db-wal"] is not None and before == after
            and all(one.returncode == 0 for one in beside) and "stranded 9" in texts):
        held("(f) beside a killed writer's WAL, a read moves nothing", "its stranded entries served, the "
             "base and the WAL the same size and time after three calls")
    else:
        failures.append(f"  ✗ (f) the killed writer       {killed.returncode} {before} {after} {texts} "
                        f"{[one.stderr[-200:] for one in beside]}")
    return 0
