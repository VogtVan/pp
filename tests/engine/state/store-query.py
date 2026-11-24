"""Scenario `store-query` -- the common query of the records' store (theme les-records-bornes,
target socle-exploitation), 11 case(s):
- (a) `since` and `until` bound the time, by ISO date or time, or by a duration (`7d`, `12h`)
- (b) `key` finds the entries of one key, `prefix` the entries whose key opens on it
- (c) `where` compares fields of the body by equality, several together (AND)
- (d) `match` finds a substring, whatever its case, through the trigram index -- the query plan
  names the index and scans no table; several words each, quoted words in sequence; under three
  characters refuses `match-short`
- (e) `order` desc by default -- the newest page --, asc on demand; the rows of a page in rank
  order; `next` is the cursor of the following page (`before` or `after`), None at the end, and
  walking it reads every entry once
- (f) the filters combine, and `total` counts what they select
- (g) `count` by `group`: by day and by a field of the body, a bounded page of groups
- (h) `search` finds a substring in every record, or in the ones named: one page per record
- (i) a malformed filter refuses `filter-invalid` and reads nothing -- a record unknown included;
  a group by key or by a field takes no `order`; a count takes no cursor, and without a group
  neither `last` nor `order`
- (j) `where` compares `null` as absent (`IS NULL`), and reaches a field whose name holds a dash
- (k) `index` gives a field of the body its index, once: a `where` on that field -- `null` included --
  then searches the index instead of scanning the table, and answers the same entries; a second call
  creates nothing; a malformed field refuses `filter-invalid`, a read-only store `store-read-only`
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from conductor import Refusal, store

LEVELS = ("info", "warn", "error")


def _stamp(when: datetime) -> str:
    return when.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _seeded(env) -> store.Store:
    """`log`: 60 entries, six a day from 2026-11-01 to 2026-11-10, keyed by agent, with a level,
    a run and a text; `fresh`: two entries 3 and 10 days old."""
    kept = store.of(env.made)
    start = datetime(2026, 11, 1, 8, tzinfo=timezone.utc)
    kept.extend("log", ({"at": _stamp(start + timedelta(days=n // 6, hours=n % 6)),
                         "key": f"agent-{n % 3}/run-{n % 2}",
                         "body": {"n": n, "level": LEVELS[n % 3], "run": n % 2,
                                  "text": f"Entry {n} said ZEPHYR-{n:02d} to the house"}}
                        for n in range(60)))
    now = datetime.now(timezone.utc)
    kept.extend("fresh", [{"at": _stamp(now - timedelta(days=10)), "body": {"age": "old"}},
                          {"at": _stamp(now - timedelta(days=3)), "body": {"age": "new"}}])
    return kept


def _ns(page) -> list:
    return [one.body.get("n") for one in page.rows]


def timed(bench, kept) -> None:
    """(a) since and until."""
    held, failures = bench.held, bench.failures
    day = kept.read("log", since="2026-11-03", until="2026-11-03")
    span = kept.read("log", since="2026-11-02T10:00", until="2026-11-04T00:00:00Z")
    recent = kept.read("fresh", since="7d")
    hours = kept.read("fresh", since="96h")
    fraction = kept.read("log", since="2026-11-02T10:00:00.5", until="2026-11-04 01:00+01:00")
    offset = kept.read("log", since="2026-11-02T11:00:00+01:00", until="2026-11-03T19:00-05:00")
    if (_ns(day) == list(range(12, 18)) and day.total == 6
            and _ns(span) == list(range(8, 18)) and span.total == 10
            and _ns(fraction) == list(range(9, 18)) and _ns(offset) == list(range(8, 18))
            and [one.body["age"] for one in recent.rows] == ["new"] and hours.total == 1):
        held("(a) since and until bound the time", "a day, a span of times -- a fraction of a second, a "
             "space, an offset, read in UTC as the store writes `at` --, a duration in days and hours")
    else:
        failures.append(f"  ✗ (a) since/until             {_ns(day)} {_ns(span)} {_ns(fraction)} {_ns(offset)} "
                        f"{recent} {hours.total}")


def keyed(bench, kept) -> None:
    """(b) key and prefix."""
    held, failures = bench.held, bench.failures
    exact = kept.read("log", key="agent-1/run-0", order="asc")
    opened = kept.read("log", prefix="agent-2/", order="asc")
    none = kept.read("log", prefix="agent-9")
    if (_ns(exact) == [n for n in range(60) if n % 3 == 1 and n % 2 == 0] and exact.total == 10
            and _ns(opened) == [n for n in range(60) if n % 3 == 2] and opened.total == 20
            and none.total == 0 and none.rows == ()):
        held("(b) key and prefix", "the entries of one key; the entries whose key opens on a prefix")
    else:
        failures.append(f"  ✗ (b) key/prefix              {_ns(exact)} {_ns(opened)} {none}")


def compared(bench, kept) -> None:
    """(c) where."""
    held, failures = bench.held, bench.failures
    one = kept.read("log", where={"level": "warn"}, order="asc")
    two = kept.read("log", where={"level": "warn", "run": 1}, order="asc")
    nested = kept.read("fresh", where={"age": "old"})
    if (_ns(one) == [n for n in range(60) if n % 3 == 1] and one.total == 20
            and _ns(two) == [n for n in range(60) if n % 3 == 1 and n % 2 == 1] and two.total == 10
            and nested.total == 1):
        held("(c) where compares the body", "one field, then two together; a number compared as a number")
    else:
        failures.append(f"  ✗ (c) where                   {_ns(one)} {_ns(two)} {nested.total}")


def matched(bench, kept) -> None:
    """(d) match, by the index alone; match-short."""
    held, failures = bench.held, bench.failures
    found = kept.read("log", match="zephyr-07")
    words = kept.read("log", match="entry HOUSE zephyr", order="asc")
    phrase = kept.read("log", match='"Entry 1 said"')
    plan = kept._explain("log", match="zephyr", since="2026-11-02", order="desc")
    walked = kept._explain("log", match="zephyr", before=40)
    indexed = any("f:log" in line and "VIRTUAL TABLE" in line for line in plan + walked)
    scanned = [line for line in plan + walked if line.startswith("SCAN") and "r:log" in line]
    sorted_after = [line for line in plan + walked if "TEMP B-TREE" in line]
    if (_ns(found) == [7] and found.total == 1
            and words.total == 60 and phrase.total == 1 and _ns(phrase) == [1]
            and indexed and not scanned and not sorted_after):
        held("(d) match goes through the trigram index", "a substring whatever its case, each word, a "
             f"quoted sequence; the plan walks the index in rank order, no sort: {' / '.join(plan)}")
    else:
        failures.append(f"  ✗ (d) match                   {_ns(found)} {words.total} {phrase.total} {plan}")
    for short in ("ze", '"ze"', "zephyr ab"):
        bench.expect("match-short", lambda short=short: kept.read("log", match=short))


def paged(bench, kept, env) -> None:
    """(e) order, the cursor, the walk."""
    held, failures = bench.held, bench.failures
    newest = kept.read("log", last=5)
    oldest = kept.read("log", last=5, order="asc")
    walked, cursor, pages = [], {}, 0
    while True:
        page = kept.read("log", last=7, **cursor)
        walked += _ns(page)
        pages += 1
        if page.next is None or pages > 20:
            break
        cursor = page.next
    forward, cursor = [], {}
    while True:
        page = kept.read("log", last=25, order="asc", **cursor)
        forward += _ns(page)
        if page.next is None:
            break
        cursor = page.next
    if (_ns(newest) == [55, 56, 57, 58, 59] and newest.next == {"before": newest.rows[0].seq}
            and _ns(oldest) == [0, 1, 2, 3, 4] and oldest.next == {"after": oldest.rows[-1].seq}
            and sorted(walked) == list(range(60)) and len(walked) == 60 and pages == 9
            and forward == list(range(60))):
        held("(e) the cursor walks every entry once", "desc by default, asc on demand, rows in rank "
             "order, `next` a seq -- never an offset")
    else:
        failures.append(f"  ✗ (e) order and cursor        {_ns(newest)} {newest.next} {_ns(oldest)} "
                        f"{oldest.next} {pages} {sorted(walked) == list(range(60))} {forward}")


def combined(bench, kept) -> None:
    """(f) the filters together."""
    held, failures = bench.held, bench.failures
    page = kept.read("log", since="2026-11-05", until="2026-11-08", prefix="agent-0/", where={"run": 0},
                     match="house", order="asc")
    want = [n for n in range(24, 48) if n % 3 == 0 and n % 2 == 0]
    if _ns(page) == want and page.total == len(want) and kept.count("log", prefix="agent-0/", match="zephyr") == 20:
        held("(f) the filters combine", f"since, until, prefix, where and match: {len(want)} entries, "
             "counted the same")
    else:
        failures.append(f"  ✗ (f) combined                {_ns(page)} {want}")


def grouped(bench, kept) -> None:
    """(g) count by group."""
    held, failures = bench.held, bench.failures
    days = kept.count("log", group="day", order="asc")
    levels = kept.count("log", group="level", where={"run": 1})
    few = kept.count("log", group="day", last=3)
    if (days.rows == tuple((f"2026-11-{d:02d}", 6) for d in range(1, 11)) and days.total == 10
            and dict(levels.rows) == {"info": 10, "warn": 10, "error": 10} and levels.total == 3
            and few.rows == (("2026-11-08", 6), ("2026-11-09", 6), ("2026-11-10", 6))
            and few.total == 10 and few.bound == 3):
        held("(g) count by group", "by day and by a field, a bounded page of groups with their total")
    else:
        failures.append(f"  ✗ (g) groups                  {days} {levels} {few}")


def searched(bench, kept) -> None:
    """(h) search across the records."""
    held, failures = bench.held, bench.failures
    kept.append("notes", {"text": "a zephyr passed"})
    everywhere = kept.search("ZEPHYR")
    named = kept.search("zephyr", records=["notes"])
    if (set(everywhere) >= {"log", "notes", "fresh"} and everywhere["log"].total == 60
            and everywhere["notes"].total == 1 and everywhere["fresh"].total == 0
            and len(everywhere["log"].rows) == min(60, everywhere["log"].bound)
            and list(named) == ["notes"]):
        held("(h) search finds in every record", "one page per record with its total; the records named alone")
    else:
        failures.append(f"  ✗ (h) search                  {dict((k, v.total) for k, v in everywhere.items())} {list(named)}")


def refused(bench, kept) -> None:
    """(i) filter-invalid."""
    for call in (lambda: kept.read("log", since="yesterday"),
                 lambda: kept.read("log", until="2026-13-40"),
                 lambda: kept.read("log", where={"le vel": "x"}),
                 lambda: kept.read("log", order="sideways"),
                 lambda: kept.read("log", after=3, before=9),
                 lambda: kept.count("log", group="no such"),
                 lambda: kept.read("log", last=0),
                 lambda: kept.count("log", group="level", order="asc"),
                 lambda: kept.count("log", group="key", order="desc"),
                 lambda: kept.read("nowhere", since="someday"),
                 lambda: kept.read("log", since="2026-11-02T10:00+0100"),
                 lambda: kept.count("log", last=3),
                 lambda: kept.count("log", order="asc"),
                 lambda: kept.count("nowhere", last=3),
                 lambda: kept.count("log", after=3),
                 lambda: kept.count("log", group="day", before=9),
                 lambda: kept.search("zephyr", records=["nowhere"], until="2026-02-30")):
        bench.expect("filter-invalid", call)


def nulled(bench, kept) -> None:
    """(j) where null and a dashed field."""
    held, failures = bench.held, bench.failures
    kept.extend("dashed", [{"body": {"run-key": "r1", "gone": None}}, {"body": {"run-key": "r2"}},
                           {"body": {"run-key": "r1", "gone": "here"}}])
    dashed = kept.read("dashed", where={"run-key": "r1"})
    empty = kept.read("dashed", where={"gone": None})
    grouped = kept.count("dashed", group="run-key")
    if (dashed.total == 2 and empty.total == 2 and dict(grouped.rows) == {"r1": 2, "r2": 1}):
        held("(j) where null and a dashed field", "null compares as absent; `run-key` reached as a quoted "
             "path, to filter and to group")
    else:
        failures.append(f"  ✗ (j) null and dash           {dashed.total} {empty.total} {grouped}")


def indexed(bench, kept, env) -> None:
    """(k) the index of a field of the body."""
    held, failures = bench.held, bench.failures
    before = kept.read("log", where={"level": "warn"}, order="asc")
    scanned = kept._explain("log", where={"level": "warn"})
    made = kept.index("log", "level")
    again = kept.index("log", "level")
    after = kept.read("log", where={"level": "warn"}, order="asc")
    plan = kept._explain("log", where={"level": "warn"})
    nulls = kept._explain("dashed", where={"gone": None}) if kept.index("dashed", "gone") else []
    empty = kept.read("dashed", where={"gone": None})
    dashed = kept.index("dashed", "run-key")
    by_dash = kept._explain("dashed", where={"run-key": "r1"})
    used = [line for line in plan if line.startswith("SEARCH") and "j:log:level" in line]
    if (any(line.startswith("SCAN") and "r:log" in line for line in scanned)
            and made is True and again is False and dashed is True
            and _ns(after) == _ns(before) and after.total == before.total == 20
            and used and not [line for line in plan if line.startswith("SCAN")]
            and any("j:dashed:gone" in line for line in nulls) and empty.total == 2
            and any("j:dashed:run-key" in line for line in by_dash)):
        held("(k) a field of the body gets its index", f"the plan searches it instead of scanning: {' / '.join(plan)}; "
             "the same entries, null and a dashed field included; a second call creates nothing")
    else:
        failures.append(f"  ✗ (k) the field index         {made} {again} {scanned} {plan} {nulls} {by_dash} {after.total}")
    bench.expect("filter-invalid", lambda: kept.index("log", "le vel"))
    bench.expect("store-read-only", lambda: store.of(env.made, readonly=True).index("log", "run"))


def scenario(bench) -> int:
    env = bench.env("store-query")
    kept = _seeded(env)
    timed(bench, kept)
    keyed(bench, kept)
    compared(bench, kept)
    matched(bench, kept)
    paged(bench, kept, env)
    combined(bench, kept)
    grouped(bench, kept)
    searched(bench, kept)
    refused(bench, kept)
    nulled(bench, kept)
    indexed(bench, kept, env)
    try:
        kept.read("log", where={"level": "warn"}, cursor=1)
        bench.failures.append("  ✗ an unknown filter         accepted")
    except TypeError:
        bench.held("an unknown filter is no parameter", "the query takes its named filters alone")
    except Refusal:
        bench.failures.append("  ✗ an unknown filter         refused instead of TypeError")
    return 0
