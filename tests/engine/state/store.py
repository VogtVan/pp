"""Scenario `store` -- the records' store of an instance (theme les-records-bornes, target socle),
20 case(s):
- (a) the base `.sys/records/records.db` is born at the first write, in WAL; a read before it
  creates nothing
- (b) a record is ONE table of the common shape -- `seq`, `at`, `key`, `body` -- indexed on `at`
  and on `key`, with its FTS5 `trigram` index beside it
- (c) `append` gives each entry its rank, `extend` adds several in one call, in order
- (d) `put` creates the entry of a key, then replaces it in place; `get` reads it back
- (e) the trigram index follows every write: as many index entries as rows, a written substring
  is found, the old value of a replaced key is not
- (f) `read` is bounded: `last`, `after`, the `total` of the record and the `bound` applied --
  `records_read_limit` when nothing lower is asked, never lifted
- (g) `transaction` holds a read and writes in one write transaction, all or nothing
- (h) writers of several processes lose no entry, neither in the table nor in its index
- (i) a reader answers at once while a write transaction stands open, without its entries
- (j) a SQLite without FTS5 refuses at the opening, by its code, and writes nothing
- (k) a package's script reaches the store through a package's `_core.py`, `core(__file__).store`
- (l) records named `x`, `x-at`, `x-key`, `x-data`, `x-docsize`, `x-config`, `x-idx` live together:
  tables, indexes and the FTS5 shadow tables never share a name
- (m) a writer that waits longer than `STORE_BUSY_WAIT` refuses `store-busy`; a base that is no
  base refuses `store-corrupt` -- never a raw sqlite3 error
- (n) the shape of a record is read without the write lock, and a writer holding its
  transaction does not falsify it
- (o) a write reads no SETTINGS: an append plays where a read refuses the settings
- (p) several processes create the base together at their first write, nothing lost
- (q) `put` on a key that carries several entries replaces the latest alone
- (r) `read(last, after)` together: the first `last` entries after `after`
- (s) `at`: any time received is stored in the canonical ISO UTC of `now()`; an unreadable one
  refuses `store-at-invalid`, nothing written
- (t) `remove` takes out the entries of a key or of a prefix of the key and their trigram index
  entries in one transaction, undone with it; neither a key nor a prefix, both, or an empty
  prefix refuse `store-remove-scope`; a record never written removes nothing and is not born
The bench fills a synthetic record in one call (`env.filled`); no case opens the base itself.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conductor import Refusal, store
from tests.harness import SOURCE

WRITER = """import sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from conductor import store
held = store.of(Path(sys.argv[2]))
for n in range(int(sys.argv[4])):
    held.append("shared", {"writer": sys.argv[3], "n": n})
"""

SKILL = """import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _core import core, home
conductor = core(__file__)
held = conductor.store.of(home(__file__))
seq = held.append("skill", {"from": "vendored"}, key="probe")
print(seq, held.get("skill", "probe").body["from"], conductor.store.__file__)
"""

CREATOR = """import sys, time
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from conductor import store
time.sleep(max(0.0, float(sys.argv[3]) - time.time()))
held = store.of(Path(sys.argv[2]))
for n in range(20):
    held.append("born", {"writer": sys.argv[4], "n": n})
"""


def _limit(env, value: int) -> None:
    """The operator's edit: `records_read_limit` posed at the throwaway's SETTINGS."""
    path = env.made / "SETTINGS.md"
    head, rest = path.read_text(encoding="utf-8").split("\n---\n", 1)
    lines = [line for line in head.splitlines() if not line.startswith("records_read_limit:")]
    path.write_text("\n".join(lines + [f"records_read_limit: {value}"]) + "\n---\n" + rest,
                    encoding="utf-8")


def born(bench, env) -> None:
    """(a) and (b): the base and the shape of a record."""
    held, failures = bench.held, bench.failures
    base = env.made / ".sys" / "records" / "records.db"
    kept = store.of(env.made)
    empty = kept.read("journal")
    absent = not base.exists()
    kept.append("journal", {"text": "first"})
    shape = kept._shape("journal")
    if absent and empty.rows == () and empty.total == 0 and base.is_file() and shape["journal"] == "wal":
        held("(a) the base is born at the first write, in WAL", "a read before it creates nothing")
    else:
        failures.append(f"  ✗ (a) the base                absent={absent} empty={empty} shape={shape}")
    indexes = shape["indexes"]
    if (shape["columns"] == ["seq", "at", "key", "body"]
            and any(one == ["at"] for one in indexes.values())
            and any(one[:1] == ["key"] for one in indexes.values())
            and shape["tokenizer"] == "trigram"):
        held("(b) one table of the common shape", f"columns {shape['columns']}, indexes on at and key, "
             "its FTS5 trigram index beside it")
    else:
        failures.append(f"  ✗ (b) the shape               {shape}")


def ranked(bench, env) -> None:
    """(c) append and extend."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    first = kept.append("ranks", {"n": 0})
    second = kept.append("ranks", {"n": 1}, key="k1")
    more = kept.extend("ranks", [{"body": {"n": n}} for n in range(2, 6)])
    page = kept.read("ranks")
    if ([first, second] + list(more) == [1, 2, 3, 4, 5, 6]
            and [one.body["n"] for one in page.rows] == list(range(6))
            and [one.seq for one in page.rows] == [1, 2, 3, 4, 5, 6]
            and page.rows[1].key == "k1" and page.rows[0].key is None
            and all(one.at.endswith("Z") for one in page.rows)):
        held("(c) append and extend rank in order", "each entry its seq, the key kept, the time in UTC")
    else:
        failures.append(f"  ✗ (c) append and extend       {first} {second} {more} {page}")


def keyed(bench, env) -> None:
    """(d) and (e): put, get, and the index that follows every write."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    born_at = kept.put("steps", "s.1", {"title": "alphabetical"})
    kept.put("steps", "s.2", {"title": "unrelated"})
    again = kept.put("steps", "s.1", {"title": "zygomatic"})
    got = kept.get("steps", "s.1")
    missing = kept.get("steps", "s.9")
    if (born_at == again and got is not None and got.body == {"title": "zygomatic"} and got.seq == born_at
            and missing is None and kept.count("steps") == 2):
        held("(d) put replaces the entry of its key in place", "the same seq, the new body, no twin")
    else:
        failures.append(f"  ✗ (d) put and get             {born_at} {again} {got} {missing}")
    kept.extend("steps", [{"key": "s.3", "body": {"title": "phabet in a list"}}])
    shape = kept._shape("steps")
    if (shape["total"] == shape["indexed"] == 3 and shape["consistent"]
            and kept._matching("steps", "gomat") == 1
            and kept._matching("steps", "lphabetical") == 0
            and kept._matching("steps", "phabet") == 1
            and kept._matching("journal", "irs") == 1):
        held("(e) the trigram index follows every write", "as many index entries as rows, a substring "
             "found, the old value of a replaced key no more")
    else:
        failures.append(f"  ✗ (e) the index               {shape} "
                        f"{[kept._matching('steps', one) for one in ('gomat', 'lphabetical', 'phabet')]}")


def bounded(bench, env) -> None:
    """(f) read: last, after, total, bound -- and the harness's synthetic filler."""
    held, failures = bench.held, bench.failures
    _limit(env, 40)
    kept = store.of(env.made)
    filled = env.filled("big", 250)
    whole = kept.read("big")
    last = kept.read("big", last=10)
    wide = kept.read("big", last=1000)
    after = kept.read("big", after=200)
    tail = kept.after("big", 245)
    if (filled == 250
            and whole.total == 250 and whole.bound == 40 and len(whole.rows) == 40
            and whole.rows[-1].seq == 250 and whole.rows[0].seq == 211
            and last.bound == 10 and [one.seq for one in last.rows] == list(range(241, 251))
            and wide.bound == 40 and len(wide.rows) == 40
            and after.bound == 40 and [one.seq for one in after.rows] == list(range(201, 241))
            and [one.seq for one in tail.rows] == list(range(246, 251)) and tail.total == 250
            and kept.count("big") == 250):
        held("(f) every read is a bounded page", "the last entries by default, `last` and `after`, the "
             "record's total and the bound applied -- the setting's, never lifted")
    else:
        failures.append(f"  ✗ (f) bounded reads           {whole.total} {whole.bound} {len(whole.rows)} "
                        f"{last.bound} {wide.bound} {after.bound} {[one.seq for one in tail.rows]}")
    _limit(env, 100)


def transacted(bench, env) -> None:
    """(g) a read and writes in one transaction, all or nothing."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    with kept.transaction() as tx:
        seen = tx.count("tx")
        tx.append("tx", {"n": seen})
        tx.put("tx", "last", {"n": tx.count("tx")})
    try:
        with kept.transaction() as tx:
            tx.append("tx", {"n": "lost"})
            raise RuntimeError("the transaction fails")
    except RuntimeError:
        pass
    page = kept.read("tx")
    if [one.body for one in page.rows] == [{"n": 0}, {"n": 1}] and kept._shape("tx")["indexed"] == 2:
        held("(g) a transaction is all or nothing", "its read sees its own writes; a failure leaves "
             "neither the rows nor their index")
    else:
        failures.append(f"  ✗ (g) the transaction         {page}")


def concurrent(bench, env) -> None:
    """(h) writers of several processes lose nothing."""
    held, failures = bench.held, bench.failures
    engine = str(env.made / ".sys" / "engine")
    writers, each = 4, 50
    procs = [subprocess.Popen([sys.executable, "-c", WRITER, engine, str(env.made), f"w{n}", str(each)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for n in range(writers)]
    errors = [proc.communicate(timeout=60)[1] for proc in procs]
    shape = store.of(env.made)._shape("shared")
    if (all(proc.returncode == 0 for proc in procs)
            and shape["total"] == shape["indexed"] == writers * each and shape["consistent"]):
        held("(h) concurrent writers lose nothing", f"{writers} processes × {each} appends = "
             f"{writers * each} rows and as many index entries")
    else:
        failures.append(f"  ✗ (h) concurrent writers      {shape} {errors}")


def reading(bench, env) -> None:
    """(i) a reader during an open write transaction."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    before = kept.count("journal")
    with kept.transaction() as tx:
        tx.append("journal", {"text": "uncommitted"})
        started = time.perf_counter()
        seen = store.of(env.made).read("journal")
        spent = time.perf_counter() - started
    after = kept.count("journal")
    if seen.total == before and spent < 1.0 and after == before + 1:
        held("(i) a reader never waits a writer", f"answered in {spent * 1000:.1f} ms, without the "
             "uncommitted entry")
    else:
        failures.append(f"  ✗ (i) the reader              {seen.total} {before} {after} {spent:.3f}s")


def unarmed(bench) -> None:
    """(j) without FTS5, the opening refuses and writes nothing."""
    held, failures = bench.held, bench.failures
    env = bench.env("unarmed")
    base = env.made / ".sys" / "records" / "records.db"
    probe = store.FTS5_PROBE
    store.FTS5_PROBE = probe.replace("fts5(", "fts5_absent(")
    store._armed = None
    try:
        bench.expect("store-fts5-missing", lambda: store.of(env.made).append("journal", {"text": "x"}))
    finally:
        store.FTS5_PROBE = probe
        store._armed = None
    if not base.exists():
        held("(j) no FTS5, nothing written", "the refusal comes before the base is opened")
    else:
        failures.append("  ✗ (j) no FTS5                 the base was written")


def vendored(bench, env) -> None:
    """(k) a package's script reaches the store through the engine its instance carries."""
    held, failures = bench.held, bench.failures
    home = env.made / ".sys" / "vendor" / "wit@0.0.1" / "skills" / "pp-wit"
    home.mkdir(parents=True, exist_ok=True)
    (home / "pp-wit.py").write_text(SKILL, encoding="utf-8")
    shutil.copy(SOURCE / "packages" / "continuity" / "skills" / "_core.py", home / "_core.py")
    done = subprocess.run([sys.executable, str(home / "pp-wit.py")], capture_output=True, text=True,
                          timeout=60)
    said = done.stdout.split()
    kept = store.of(env.made).get("skill", "probe")
    if (done.returncode == 0 and len(said) == 3 and said[1] == "vendored"
            and Path(said[2]).is_relative_to(env.made / ".sys" / "engine")
            and kept is not None and kept.seq == int(said[0])):
        held("(k) a package reaches the store", "through a package's `_core.py`: `conductor.store` of the "
             "vendored engine, the entry read back by the bench")
    else:
        failures.append(f"  ✗ (k) the vendored store      {done.returncode} {done.stdout!r} {done.stderr[-400:]!r}")


def named(bench, env) -> None:
    """(l) the namespaces of tables, indexes and FTS5 shadows apart."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    names = ("x", "x-at", "x-key", "x-data", "x-docsize", "x-config", "x-idx")
    for name in names:
        kept.append(name, {"record": f"{name} first"}, key="one")
        kept.put(name, "one", {"record": f"{name} again"})
        kept.append(name, {"record": f"{name} second"})
    shapes = {name: kept._shape(name) for name in names}
    found = {name: kept._matching(name, f'"{name} again"') for name in names}
    if (set(kept.records()) >= set(names)
            and all(one["total"] == one["indexed"] == 2 and one["consistent"] for one in shapes.values())
            and all(count == 1 for count in found.values())):
        held("(l) records of neighbour names live together", f"{', '.join(names)}: each its table, its "
             "indexes and its trigram index, two entries each")
    else:
        failures.append(f"  ✗ (l) the names               {shapes} {found}")


def named_refusals(bench) -> None:
    """(m) store-busy and store-corrupt."""
    held, failures = bench.held, bench.failures
    env = bench.env("refusals")
    kept = store.of(env.made)
    kept.append("journal", {"text": "first"})
    wait = store.STORE_BUSY_WAIT
    store.STORE_BUSY_WAIT = 0.3
    spent = 0.0
    try:
        with kept.transaction() as tx:
            tx.append("journal", {"text": "held"})
            started = time.perf_counter()
            bench.expect("store-busy", lambda: store.of(env.made).append("journal", {"text": "waits"}))
            spent = time.perf_counter() - started
    finally:
        store.STORE_BUSY_WAIT = wait
    base = env.made / ".sys" / "records" / "records.db"
    for one in base.parent.glob("records.db*"):
        one.unlink()
    base.write_bytes(b"this is no base at all, only words " * 200)
    bench.expect("store-corrupt", lambda: store.of(env.made).read("journal"))
    bench.expect("store-corrupt", lambda: store.of(env.made).append("journal", {"text": "x"}))
    for one in base.parent.glob("records.db*"):
        one.unlink()
    base.mkdir()                                   # a base that cannot be opened at all
    bench.expect("store-failed", lambda: store.of(env.made).append("journal", {"text": "x"}))
    if 0.2 <= spent < 3.0:
        held("(m) the refusals are named", f"store-busy after {spent:.2f} s of a 0.3 s wait; a base of words "
             "store-corrupt, to read and to write")
    else:
        failures.append(f"  ✗ (m) the busy wait           {spent:.2f}s")


def shaped(bench, env) -> None:
    """(n) the shape is read without writing, beside an open writer."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    before = kept._shape("journal")
    with kept.transaction() as tx:
        tx.append("journal", {"text": "uncommitted"})
        started = time.perf_counter()
        during = store.of(env.made)._shape("journal")
        spent = time.perf_counter() - started
    if (during["total"] == during["indexed"] == before["total"] and during["consistent"]
            and spent < 1.0):
        held("(n) the shape reads beside a writer", f"answered in {spent * 1000:.1f} ms, the committed "
             "entries alone, the index consistent")
    else:
        failures.append(f"  ✗ (n) the shape               {before} {during} {spent:.3f}s")


def unsettled(bench) -> None:
    """(o) a write reads no SETTINGS."""
    held, failures = bench.held, bench.failures
    env = bench.env("unsettled")
    path = env.made / "SETTINGS.md"
    head, rest = path.read_text(encoding="utf-8").split("\n---\n", 1)
    path.write_text(head + "\nrecords_read_limit: none\n---\n" + rest, encoding="utf-8")
    kept = store.of(env.made)
    seq = kept.append("journal", {"text": "written"})
    kept.put("journal", "k", {"text": "put"})
    bench.expect("settings-invalid", lambda: store.of(env.made).read("journal"))
    with store.of(env.made).transaction() as tx:
        tx.append("journal", {"text": "a transaction that writes alone"})
    try:
        with store.of(env.made).transaction() as tx:
            tx.append("journal", {"text": "undone"})
            tx.read("journal")
        refused = ""
    except Refusal as refusal:
        refused, bench.refusals = refusal.code, bench.refusals + 1
    if seq == 1 and refused == "settings-invalid" and store.of(env.made).count("journal") == 3:
        held("(o) a write reads no SETTINGS", "append, put and a transaction that writes alone play where a "
             "read refuses the settings; a transaction reads them at its first read, and is undone")
    else:
        failures.append(f"  ✗ (o) the write               {seq}")


def created(bench) -> None:
    """(p) several processes create the base together."""
    held, failures = bench.held, bench.failures
    env = bench.env("created")
    engine = str(env.made / ".sys" / "engine")
    start = time.time() + 1.0
    procs = [subprocess.Popen([sys.executable, "-c", CREATOR, engine, str(env.made), str(start), f"w{n}"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for n in range(6)]
    errors = [proc.communicate(timeout=60)[1] for proc in procs]
    shape = store.of(env.made)._shape("born")
    if all(proc.returncode == 0 for proc in procs) and shape["total"] == shape["indexed"] == 120 \
            and shape["consistent"] and shape["journal"] == "wal":
        held("(p) the base is born under several writers", "6 processes × 20 first writes at once: 120 rows, "
             "as many index entries, in WAL")
    else:
        failures.append(f"  ✗ (p) the birth               {shape} {[one[-300:] for one in errors]}")


def latest(bench, env) -> None:
    """(q) put replaces the latest entry of its key alone."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    older = kept.append("multi", {"v": "older"}, key="k")
    newer = kept.append("multi", {"v": "newer"}, key="k")
    replaced = kept.put("multi", "k", {"v": "replaced"})
    rows = {one.seq: one.body["v"] for one in kept.read("multi").rows}
    if replaced == newer and rows == {older: "older", newer: "replaced"}:
        held("(q) put replaces the latest entry of its key", "the older entry of the same key untouched")
    else:
        failures.append(f"  ✗ (q) put on several          {replaced} {rows}")


def windowed(bench, env) -> None:
    """(r) read(last, after) together."""
    held, failures = bench.held, bench.failures
    page = store.of(env.made).read("big", last=5, after=100)
    if [one.seq for one in page.rows] == [101, 102, 103, 104, 105] and page.total == 250 and page.bound == 5:
        held("(r) last and after together", "the first five entries after 100, the record's total")
    else:
        failures.append(f"  ✗ (r) last and after         {[one.seq for one in page.rows]} {page.total}")


def timed(bench, env) -> None:
    """(s) at normalized to the canonical ISO UTC; store-at-invalid."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    said = {"2026-11-20T17:45:00+00:00": "2026-11-20T17:45:00.000000Z",
            "2026-11-20 18:45:00.5+01:00": "2026-11-20T17:45:00.500000Z",
            "2026-11-20T17:45Z": "2026-11-20T17:45:00.000000Z",
            "2026-11-20T17:45:00.123456Z": "2026-11-20T17:45:00.123456Z",
            "2026-11-20T12:45:00.12-05:00": "2026-11-20T17:45:00.120000Z",
            "2026-11-20 17:45:00": "2026-11-20T17:45:00.000000Z"}
    stored = {}
    for given in said:
        seq = kept.append("timed", {"given": given}, at=given)
        stored[given] = kept.read("timed", last=1).rows[-1].at if seq else None
    before = kept.count("timed")
    for wrong in ("yesterday", "2026-11-20", "2026-11-20T17", "2026-11-20T17:45:00+0100",
                  "2026-11-20T17:45:00.1234567Z", "2026-13-40T00:00", datetime(2026, 11, 20, 17, 45)):
        bench.expect("store-at-invalid", lambda wrong=wrong: kept.append("timed", {"x": 1}, at=wrong))
    aware = kept.append("timed", {"x": "aware"}, at=datetime(2026, 11, 20, 18, 45, tzinfo=timezone(timedelta(hours=1))))
    stored["aware"] = kept.read("timed", last=1).rows[-1].at if aware else None
    said = {**said, "aware": "2026-11-20T17:45:00.000000Z"}
    bench.expect("store-at-invalid", lambda: kept.extend("timed", [{"body": {"x": 1}},
                                                                     {"body": {"x": 2}, "at": "2026-13-40"}]))
    shape = store.now()
    if stored == said and kept.count("timed") == before + 1 and len(shape) == len(said["2026-11-20T17:45Z"]):
        held("(s) every time stored in one form", "T or a space, minutes, seconds and fractions, Z, an offset "
             "or none (UTC), an aware datetime: the canonical UTC of now(); a date alone, an offset without its "
             "colon, seven decimals, a naive datetime refuse store-at-invalid, a batch with one of them whole")
    else:
        failures.append(f"  ✗ (s) at                      {stored} {kept.count('timed')} {before}")


def removed(bench, env) -> None:
    """(t) remove by key or by prefix, the index with the rows, in one transaction."""
    held, failures = bench.held, bench.failures
    kept = store.of(env.made)
    kept.extend("gone", [{"key": "run:a/1", "body": {"text": "alphaone"}},
                         {"key": "run:a/2", "body": {"text": "alphatwo"}},
                         {"key": "run:ab/1", "body": {"text": "abthree"}},
                         {"key": "solo", "body": {"text": "solitary"}},
                         {"key": "solo", "body": {"text": "solitude"}},
                         {"body": {"text": "keyless"}}])
    by_key = kept.remove("gone", key="solo")
    by_prefix = kept.remove("gone", prefix="run:a/")
    none = kept.remove("gone", key="absent")
    try:
        with kept.transaction() as tx:
            undone = tx.remove("gone", prefix="run:")
            raise RuntimeError("the transaction fails")
    except RuntimeError:
        pass
    shape = kept._shape("gone")
    left = sorted(one.key or "" for one in kept.read("gone").rows)
    found = {text: kept._matching("gone", text) for text in ("alphaone", "alphatwo", "solit", "abthree", "keyless")}
    for scope in ({}, {"key": "solo", "prefix": "run:"}, {"prefix": ""}):
        bench.expect("store-remove-scope", lambda scope=scope: kept.remove("gone", **scope))
    unborn = kept.remove("never", key="k")
    if (by_key == 2 and by_prefix == 2 and none == 0 and undone == 1
            and left == ["", "run:ab/1"] and shape["total"] == shape["indexed"] == 2 and shape["consistent"]
            and found == {"alphaone": 0, "alphatwo": 0, "solit": 0, "abthree": 1, "keyless": 1}
            and unborn == 0 and "never" not in kept.records()):
        held("(t) remove takes out a key or a prefix, its index with it", "2 by key, 2 by prefix, a "
             "neighbour prefix kept; the index entries gone in the same transaction, undone with it; "
             "no scope, both or an empty prefix refuse; a record never written is not born")
    else:
        failures.append(f"  ✗ (t) remove                  {by_key} {by_prefix} {none} {left} {shape} {found} {unborn}")


def scenario(bench) -> int:
    env = bench.env("store")
    born(bench, env)
    ranked(bench, env)
    keyed(bench, env)
    bounded(bench, env)
    transacted(bench, env)
    concurrent(bench, env)
    reading(bench, env)
    unarmed(bench)
    vendored(bench, env)
    named(bench, env)
    named_refusals(bench)
    shaped(bench, env)
    unsettled(bench)
    created(bench)
    latest(bench, env)
    windowed(bench, env)
    timed(bench, env)
    removed(bench, env)
    try:
        store.of(env.made).append("Bad Name", {})
        bench.failures.append("  ✗ a record's name           `Bad Name` accepted")
    except Refusal as refusal:
        bench.refusals += 1
        if refusal.code != "store-record-invalid":
            bench.failures.append(f"  ✗ a record's name           {refusal.code}")
    return 0
