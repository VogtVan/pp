"""Behaviour: the STORE of an instance's records -- ONE SQLite base, `.sys/records/records.db`,
in WAL, the only code of the product that opens it (theme les-records-bornes, target socle).

A RECORD is one table of the common shape: `seq` (its rank, the primary key), `at` (the time
of the write, ISO UTC in the one form `now()` gives), `key` (optional: what a reader looks an
entry up by) and `body` (the entry, JSON). It is indexed on `at` and on `key`, and carries
beside it its FTS5 index of tokenizer `trigram` over the text of `body` -- external content,
the body stored once --, written by the store itself in the transaction of every write: one
function writes both, so the index never lags. Table and index are born at the record's first
write; a read of a record not written yet is an empty page and creates nothing.

The NAMES of the base: a record `<name>` (kebab) is the table `"r:<name>"`, its indexes
`"i:<name>:at"` and `"i:<name>:key"`, its trigram index `"f:<name>"` -- whose shadow tables
FTS5 names `"f:<name>_data"`, `_idx`, `_docsize`, `_config`. A record's name holds no `_`
and no `:`, so no two records, and no record and a shadow, ever share a name. A field of the body
given its index by `index` is the index `"j:<name>:<field>"`, apart from the record's own.

Every call opens its own connection: WAL, `synchronous=NORMAL`, a busy wait of
`STORE_BUSY_WAIT`; every write runs under `BEGIN IMMEDIATE`, every read in a short
transaction, so a reader never waits a writer and a writer waits another for the busy wait
at most, then refuses `store-busy`. A base SQLite finds corrupt, or no base at all, refuses
`store-corrupt`; any other error of SQLite refuses `store-failed`, its name cited: no caller
ever meets a raw sqlite3 error. No call returns entries without a bound: a read is a
`Page`, its rows, the `total` the filters select, the `bound` applied -- `records_read_limit`
at SETTINGS unless the caller asks fewer; no value lifts it -- and `next`, the cursor of the
following page. A read reads the bound before its transaction opens; a `transaction` reads it
at its first read; a write reads no SETTINGS.

The COMMON QUERY (target socle-exploitation) is the one grammar every reader filters by, answered
by SQLite and never after the read: `since` and `until` (an ISO date or time, or a duration
`<n>d|h|m` back from now; a date alone takes its whole day), `key` (exact), `prefix` (of the
key, by its index), `where` (fields of the body by equality, AND), `match` (a substring of 3
characters or more, whatever its case, through the trigram index alone: several words each,
a quoted text in sequence), `order` (`desc`, the newest page, by default; `asc`) and the cursor
`after` / `before` -- a seq, never an offset. The rows of a page stand in rank order whatever
the walk. `count` counts the same selection, or by `group` -- `day`, `key` or a field of the
body -- in a bounded page; `search` asks one text of every record.

`index` gives a field of the body an index of expression, `json_extract(body, '$."<field>"')`,
once: a `where` on that field -- `null` included -- then searches it instead of scanning the table.
The path of a field is written in the SQL as a literal, the field judged first (`FIELD_RE`: no quote
can enter it), because SQLite takes an index of expression only for the same expression, never for a
bound parameter.

`remove` takes out the entries of ONE key or of a PREFIX of the key -- one of the two, never
neither nor both, a prefix never empty: `store-remove-scope` -- and their entries of the trigram
index, in the transaction of the call; it returns how many it took out.

A SQLite without FTS5 (or without its `trigram` tokenizer, SQLite >= 3.34) refuses
`store-fts5-missing` before the base is opened: nothing is written.
"""
from __future__ import annotations

import contextlib
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from ..core.errors import Refusal
from . import instance

BASE = "records.db"            # under the instance's `.sys/records/`
STORE_BUSY_WAIT = 5            # seconds a call waits for another writer, like CALL_LOCK_WAIT
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")    # a record's name: kebab
AT_FORM = "%Y-%m-%dT%H:%M:%S.%fZ"                          # the one form of `at`
FIELD_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_-]*(\.[A-Za-z0-9_][A-Za-z0-9_-]*)*$")   # a field of the body
DURATION_RE = re.compile(r"^(\d+)([dhm])$")
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MATCH_MIN = 3                  # the trigram index finds nothing shorter
KEY_TOP = "\U0010ffff"         # above every key that opens on a prefix
FTS5_PROBE = "CREATE VIRTUAL TABLE temp.probe USING fts5(text, tokenize='trigram')"
_armed: bool | None = None     # whether this process's SQLite carries FTS5 and trigram


@dataclass(frozen=True)
class Entry:
    seq: int
    at: str
    key: str | None
    body: Any


@dataclass(frozen=True)
class Page:
    rows: tuple                # the entries, in rank order -- or (group, count) pairs
    total: int                 # the entries the filters select -- or the groups
    bound: int                 # the most entries this page could hold
    next: dict | None = None   # the cursor of the following page, `{"before"|"after": seq}`


def of(meta: Path, readonly: bool = False) -> "Store":
    """-> the store of the instance at `meta`; `readonly`, a store that never writes the base nor
    its files -- the console's reads."""
    return Store(Path(meta), readonly)


def now() -> str:
    """-> the time of a write, ISO UTC to the microsecond -- the one form of `at`."""
    return datetime.now(timezone.utc).strftime(AT_FORM)


AT_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?"
                   r"(Z|[+-]\d{2}:\d{2})?$")
# what `at` may say, read by this form alone whatever the Python: a date, `T` or a space,
# HH:MM[:SS[.f, 1 to 6 digits]], then `Z`, an offset `+HH:MM`/`-HH:MM`, or nothing -- UTC


def moment(at: Any) -> str:
    """-> `at` in the one form of the base, UTC to the microsecond. A text in the form `AT_RE`
    says -- without an offset it is taken in UTC --, or an AWARE `datetime`; None is now. Anything
    else -- another form, an impossible date, a naive `datetime`, whose zone nothing says --
    refuses `store-at-invalid`."""
    if at is None:
        return now()
    if isinstance(at, datetime):
        if at.tzinfo is None or at.tzinfo.utcoffset(at) is None:
            raise Refusal("store-at-invalid", f"`{at!r}` — a naive datetime: its zone is not said")
        return at.astimezone(timezone.utc).strftime(AT_FORM)
    said = AT_RE.fullmatch(at.strip()) if isinstance(at, str) else None
    if said is None:
        raise Refusal("store-at-invalid", f"`{at!r}` — a time `2026-11-20T17:45:00Z`, `T` or a space, "
                                          "an offset `+01:00` or none (UTC)")
    year, month, day, hour, minute, second, fraction, zone = said.groups()
    offset = timezone.utc
    if zone and zone != "Z":
        sign = 1 if zone[0] == "+" else -1
        offset = timezone(sign * timedelta(hours=int(zone[1:3]), minutes=int(zone[4:6])))
    try:
        when = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second or 0),
                        int((fraction or "0").ljust(6, "0")), tzinfo=offset)
    except ValueError:
        raise Refusal("store-at-invalid", f"`{at}` — no such time")
    return when.astimezone(timezone.utc).strftime(AT_FORM)


def _arm() -> None:
    """Refuses `store-fts5-missing` when this process's SQLite has no FTS5 trigram -- probed
    once per process, on a base in memory: the instance's base is never touched."""
    global _armed
    if _armed is None:
        probe = sqlite3.connect(":memory:")
        try:
            probe.execute(FTS5_PROBE)
            _armed = True
        except sqlite3.Error:
            _armed = False
        finally:
            probe.close()
    if not _armed:
        raise Refusal("store-fts5-missing",
                      f"SQLite {sqlite3.sqlite_version} carries no FTS5 with the `trigram` tokenizer "
                      "(3.34 or later, built with FTS5) — the records' store cannot open")


def _opened(conn: sqlite3.Connection, write: bool) -> None:
    """Opens the call's transaction -- a write's in WAL, the base turned to WAL first when it is
    not yet. The turn to WAL and the recovery of a WAL another connection is opening answer busy
    WITHOUT SQLite's busy wait (several writers creating the base together): those steps are
    tried again until `STORE_BUSY_WAIT` has passed, then refuse `store-busy`."""
    deadline = time.monotonic() + STORE_BUSY_WAIT
    while True:
        try:
            if write and conn.execute("PRAGMA journal_mode").fetchone()[0] != "wal":
                conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            return
        except sqlite3.OperationalError as error:
            if _named(error).code != "store-busy" or time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


SQLITE_SAID = (("database is locked", "SQLITE_BUSY"), ("database table is locked", "SQLITE_LOCKED"),
               ("file is not a database", "SQLITE_NOTADB"), ("database disk image is malformed", "SQLITE_CORRUPT"))
# a Python before 3.11 carries no `sqlite_errorname`: the name is read from SQLite's own message


def _named(error: sqlite3.Error) -> Refusal:
    """-> the refusal a sqlite3 error stands for: `store-busy` when another writer held the base
    past the wait (SQLITE_BUSY, SQLITE_LOCKED), `store-corrupt` for a base SQLite finds corrupt or
    no base at all (SQLITE_CORRUPT, SQLITE_NOTADB), `store-failed` for any other, its name cited."""
    said = str(error)
    name = str(getattr(error, "sqlite_errorname", "") or "")
    if not name:
        name = next((code for text, code in SQLITE_SAID if text in said.lower()), "")
    if name.startswith(("SQLITE_BUSY", "SQLITE_LOCKED")):
        return Refusal("store-busy", f"another writer held the records' base past {STORE_BUSY_WAIT} s — "
                                     "replay the call")
    if name.startswith(("SQLITE_CORRUPT", "SQLITE_NOTADB")):
        return Refusal("store-corrupt", f"the records' base cannot be read ({name}): {said}")
    return Refusal("store-failed", f"SQLite refused the records' base ({name or type(error).__name__}): {said}")


@dataclass(frozen=True)
class _Names:
    table: str
    at: str
    key: str
    index: str
    docsize: str


def _names(record: str) -> _Names:
    """-> the quoted names of a record in the base."""
    if not isinstance(record, str) or not NAME_RE.fullmatch(record):
        raise Refusal("store-record-invalid", f"`{record}` — a record's name is kebab-case")
    return _Names(f'"r:{record}"', f'"i:{record}:at"', f'"i:{record}:key"', f'"f:{record}"',
                  f'"f:{record}_docsize"')


def _text(body: Any) -> str:
    return json.dumps(body, ensure_ascii=False, separators=(",", ":"))


class Store:
    """The store of one instance: each verb opens its connection, `transaction` holds one."""

    def __init__(self, meta: Path, readonly: bool = False) -> None:
        self._meta = meta
        self._readonly = readonly
        self._path = meta / instance.RECORDS / BASE
        self._limit: int | None = None

    def limit(self) -> int:
        """-> `records_read_limit` of the instance's SETTINGS, read once per store."""
        if self._limit is None:
            from . import settings
            self._limit = settings.of(self._meta).records_read_limit
        return self._limit

    @contextlib.contextmanager
    def _connected(self, write: bool, bounded: bool, lazy: bool = False) -> Iterator["Session"]:
        _arm()
        limit = self.limit() if bounded else None          # before any transaction opens
        later = self.limit if lazy else None               # a transaction's: at its first read
        if write and self._readonly:
            raise Refusal("store-read-only", "a store opened read-only writes nothing")
        if not write and not self._path.is_file():
            yield Session(None, limit, False, later)
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # a read-only store opens the base `mode=ro` when a WAL stands beside it -- a WAL a
        # killed writer left is read, never checkpointed into the base; without a WAL an
        # ordinary connection reads, and, the last to close, leaves the files as it found them
        # (`mode=ro` would leave behind the WAL and the index it creates)
        stranded = self._readonly and self._path.with_name(BASE + "-wal").exists()
        target = self._path.as_uri() + "?mode=ro" if stranded else str(self._path)
        try:
            conn = sqlite3.connect(target, timeout=STORE_BUSY_WAIT, isolation_level=None, uri=stranded)
        except sqlite3.Error as error:
            raise _named(error) from None
        try:
            try:
                conn.execute(f"PRAGMA busy_timeout = {int(STORE_BUSY_WAIT * 1000)}")
                conn.execute("PRAGMA synchronous = NORMAL")
                _opened(conn, write)
                yield Session(conn, limit, write, later)
            except BaseException:
                if conn.in_transaction:
                    with contextlib.suppress(sqlite3.Error):
                        conn.execute("ROLLBACK")
                raise
            conn.execute("COMMIT")
        except sqlite3.Error as error:
            raise _named(error) from error
        finally:
            conn.close()

    @contextlib.contextmanager
    def transaction(self) -> Iterator["Session"]:
        """One write transaction: its reads see its writes; an exception undoes them all."""
        with self._connected(True, False, lazy=True) as session:
            yield session

    def append(self, record: str, body: Any, key: str | None = None, at: Any = None) -> int:
        with self._connected(True, False) as session:
            return session.append(record, body, key, at)

    def extend(self, record: str, entries: Iterable[dict]) -> list[int]:
        with self._connected(True, False) as session:
            return session.extend(record, entries)

    def put(self, record: str, key: str, body: Any, at: Any = None) -> int:
        with self._connected(True, False) as session:
            return session.put(record, key, body, at)

    def remove(self, record: str, key: str | None = None, prefix: str | None = None) -> int:
        _names(record)
        _scope(key, prefix)
        if not self._readonly and not self._path.is_file():
            return 0                                   # no base: nothing to take out, nothing born
        with self._connected(True, False) as session:
            return session.remove(record, key, prefix)

    def index(self, record: str, field: str) -> bool:
        with self._connected(True, False) as session:
            return session.index(record, field)

    def get(self, record: str, key: str) -> Entry | None:
        with self._connected(False, False) as session:
            return session.get(record, key)

    def read(self, record: str, last: int | None = None, after: int | None = None, **query) -> Page:
        with self._connected(False, True) as session:
            return session.read(record, last, after, **query)

    def after(self, record: str, seq: int) -> Page:
        with self._connected(False, True) as session:
            return session.after(record, seq)

    def count(self, record: str, **query) -> int | Page:
        # a bare count reads no SETTINGS; a count by group pages, so it reads the bound first
        with self._connected(False, query.get("group") is not None) as session:
            return session.count(record, **query)

    def search(self, text: str, records: Iterable[str] | None = None, **query) -> dict:
        with self._connected(False, True) as session:
            return session.search(text, records, **query)

    def summary(self) -> list[dict]:
        with self._connected(False, False) as session:
            return session.summary()

    def _explain(self, record: str, **query) -> list[str]:
        """The bench's reading of the plan of a page -- never a reader's way to the entries."""
        with self._connected(False, True) as session:
            return session._explain(record, **query)

    def records(self) -> list[str]:
        with self._connected(False, False) as session:
            return session.records()

    def _shape(self, record: str) -> dict:
        """The bench's reading of a record's form -- never a reader's way to the entries."""
        with self._connected(False, False) as session:
            return session._shape(record)

    def _matching(self, record: str, text: str) -> int:
        """The bench's count of the entries the trigram index finds -- until `search` serves them."""
        with self._connected(False, False) as session:
            return session._matching(record, text)


class Session:
    """The verbs on ONE connection, inside its transaction -- no connection when the base is not
    born yet: every read answers empty."""

    def __init__(self, conn: sqlite3.Connection | None, limit: int | None, write: bool = False,
                 later=None) -> None:
        self._conn = conn
        self._limit = limit
        self._write = write
        self._later = later      # a transaction's: the bound read at its first read

    def _bounded(self) -> int:
        """-> the bound of this session's reads: read before its transaction, or -- a transaction's --
        at its first read; a session opened to write alone reads nothing."""
        if self._limit is None and self._later is not None:
            self._limit = self._later()
        if self._limit is None:
            raise Refusal("store-unbounded", "a read needs the bound its store reads")
        return self._limit

    # --- the writes -------------------------------------------------------------------------

    def _born(self, record: str) -> _Names:
        """-> the record's names, its table and indexes created at its first write."""
        names = _names(record)
        if not self._write:
            raise Refusal("store-read-only", f"`{record}` — a read transaction writes nothing")
        if not self._exists(names):
            self._conn.execute(f"CREATE TABLE {names.table} (seq INTEGER PRIMARY KEY AUTOINCREMENT, "
                               "at TEXT NOT NULL, key TEXT, body TEXT NOT NULL)")
            self._conn.execute(f"CREATE INDEX {names.at} ON {names.table}(at)")
            self._conn.execute(f"CREATE INDEX {names.key} ON {names.table}(key, seq)")
            self._conn.execute(f"CREATE VIRTUAL TABLE {names.index} USING fts5(body, "
                               f"content='r:{record}', content_rowid='seq', tokenize='trigram')")
        return names

    def append(self, record: str, body: Any, key: str | None = None, at: Any = None) -> int:
        names = self._born(record)
        return self._insert(names, body, key, moment(at))

    def extend(self, record: str, entries: Iterable[dict]) -> list[int]:
        """Adds each `{"body": ..., "key": ..., "at": ...}` in order -- `key` and `at` optional; one
        entry refused refuses them all."""
        names = self._born(record)
        return [self._insert(names, one["body"], one.get("key"), moment(one.get("at"))) for one in entries]

    def put(self, record: str, key: str, body: Any, at: Any = None) -> int:
        """Creates the entry of `key`, or replaces in place the LATEST entry that carries it -- the
        same seq, the index entry of the old body taken out before the new one goes in; the older
        entries of the same key stay as they are."""
        if key is None:
            raise Refusal("store-key-missing", f"`{record}` — `put` writes the entry of a key")
        names = self._born(record)
        when = moment(at)
        found = self._conn.execute(f"SELECT seq, body FROM {names.table} WHERE key = ? "
                                   "ORDER BY seq DESC LIMIT 1", (key,)).fetchone()
        if found is None:
            return self._insert(names, body, key, when)
        seq, old = found
        text = _text(body)
        self._conn.execute(f"INSERT INTO {names.index}({names.index}, rowid, body) VALUES ('delete', ?, ?)",
                           (seq, old))
        self._conn.execute(f"UPDATE {names.table} SET at = ?, body = ? WHERE seq = ?", (when, text, seq))
        self._conn.execute(f"INSERT INTO {names.index}(rowid, body) VALUES (?, ?)", (seq, text))
        return seq

    def remove(self, record: str, key: str | None = None, prefix: str | None = None) -> int:
        """Takes out every entry of `key`, or of every key that opens on `prefix`, and their entries
        of the trigram index -- the index first, from the bodies it indexed -- in this transaction;
        -> how many. A record not born yet removes nothing and is not born."""
        names = _names(record)
        _scope(key, prefix)
        if not self._write:
            raise Refusal("store-read-only", f"`{record}` — a read transaction writes nothing")
        if not self._exists(names):
            return 0
        if key is not None:
            where, params = "key = ?", [str(key)]
        else:
            where, params = "key >= ? AND key < ?", [str(prefix), str(prefix) + KEY_TOP]
        self._conn.execute(f"INSERT INTO {names.index}({names.index}, rowid, body) "
                           f"SELECT 'delete', seq, body FROM {names.table} WHERE {where}", params)
        return self._conn.execute(f"DELETE FROM {names.table} WHERE {where}", params).rowcount

    def index(self, record: str, field: str) -> bool:
        """Gives the field `field` of the body its index -- the record born when it is not yet --;
        -> True when this call created it, False when it stood already."""
        _fields({field: ""})
        names = self._born(record)
        name = f"j:{record}:{field}"
        if self._conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = ?",
                              (name,)).fetchone() is not None:
            return False
        self._conn.execute(f'CREATE INDEX "{name}" ON {names.table}({_extract("body", field)})')
        return True

    def _insert(self, names: _Names, body: Any, key: str | None, at: str) -> int:
        text = _text(body)
        seq = self._conn.execute(f"INSERT INTO {names.table}(at, key, body) VALUES (?, ?, ?)",
                                 (at, key, text)).lastrowid
        self._conn.execute(f"INSERT INTO {names.index}(rowid, body) VALUES (?, ?)", (seq, text))
        return seq

    # --- the reads --------------------------------------------------------------------------

    def _exists(self, names: _Names) -> bool:
        return self._conn is not None and self._conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (names.table.strip('"'),)).fetchone() is not None

    def get(self, record: str, key: str) -> Entry | None:
        """-> the latest entry of `key`, None when the record holds none."""
        names = _names(record)
        if not self._exists(names):
            return None
        row = self._conn.execute(f"SELECT seq, at, key, body FROM {names.table} WHERE key = ? "
                                 "ORDER BY seq DESC LIMIT 1", (key,)).fetchone()
        return _entry(row) if row else None

    def _selection(self, table: str, index: str, since=None, until=None, key=None, prefix=None,
                   where=None, match=None) -> tuple[str, list[str], list]:
        """-> (the source, the clauses, their parameters) of the filters: every one a clause
        SQLite answers. A `match` drives the query from the trigram index (`CROSS JOIN`: the
        table is reached by its rank, never scanned)."""
        clauses: list[str] = []
        params: list = []
        source = table
        if match is not None:
            source = f"{index} CROSS JOIN {table} ON {table}.seq = {index}.rowid"
            clauses.append(f"{index} MATCH ?")
            params.append(_phrase(match))
        if since is not None:
            clauses.append(f"{table}.at >= ?")
            params.append(_instant(since, "since", end=False))
        if until is not None:
            clauses.append(f"{table}.at < ?")
            params.append(_instant(until, "until", end=True))
        if key is not None:
            clauses.append(f"{table}.key = ?")
            params.append(str(key))
        if prefix is not None:
            clauses.append(f"{table}.key >= ? AND {table}.key < ?")
            params += [str(prefix), str(prefix) + KEY_TOP]
        for field, value in _fields(where):
            if value is None:
                clauses.append(f"{_extract(f'{table}.body', field)} IS NULL")
            else:
                clauses.append(f"{_extract(f'{table}.body', field)} = ?")
                params.append(value)
        return source, clauses, params

    def _page_query(self, record: str, last, after, before, order, filters) -> tuple:
        """-> (table, the page's SQL, its parameters, the total's SQL, its parameters, bound, walk)."""
        names = _names(record)
        table, index = names.table, names.index
        bound = _bound(last, self._bounded())
        walk = _walk(order, after, before)
        source, clauses, params = self._selection(table, index, **filters)
        where = " AND ".join(clauses) or "1"
        # under a match the page walks the trigram index in the order of its rowid -- the seq --,
        # so that LIMIT stops at the page's last entry instead of sorting every match
        ranked = f"{index}.rowid" if filters.get("match") is not None else f"{table}.seq"
        cursor, more = [], []
        if after is not None:
            cursor.append(f"{ranked} > ?")
            more.append(_seq(after, "after"))
        if before is not None:
            cursor.append(f"{ranked} < ?")
            more.append(_seq(before, "before"))
        paged = " AND ".join([where] + cursor)
        sql = (f"SELECT {table}.seq, {table}.at, {table}.key, {table}.body FROM {source} WHERE {paged} "
               f"ORDER BY {ranked} {'DESC' if walk == 'desc' else 'ASC'} LIMIT ?")
        return (names, sql, params + more + [bound + 1], _counting(source, index, where, clauses), params,
                bound, walk)

    def count(self, record: str, group: str | None = None, last: int | None = None,
              order: str | None = None, after: int | None = None, before: int | None = None,
              **filters) -> int | Page:
        """-> without `group`, an INTEGER: how many entries the filters select. With `group` (`day`,
        `key` or a field of the body), a PAGE of `(group, count)` pairs -- by day the newest days
        first taken under `desc` (the default) or the oldest under `asc`; by key or by a field the
        most frequent values first, which takes no `order` --, its total the number of groups."""
        judge(group=group, last=last, order=order, after=after, before=before, counting=True, **filters)
        names = _names(record)
        table, index = names.table, names.index
        source, clauses, params = self._selection(table, index, **filters)
        where = " AND ".join(clauses) or "1"
        if group is None:
            if not self._exists(names):
                return 0
            return self._conn.execute(_counting(source, index, where, clauses), params).fetchone()[0]
        bound = _bound(last, self._bounded())
        walk = _walk(order, None, None)
        if group == "day":
            value, ranked = f"substr({table}.at, 1, 10)", f"g {'DESC' if walk == 'desc' else 'ASC'}"
        elif group == "key":
            value, ranked = f"{table}.key", "n DESC, g ASC"
        else:
            value, ranked = _extract(f"{table}.body", group), "n DESC, g ASC"
        if not self._exists(names):
            return Page((), 0, bound)
        grouped = f"SELECT {value} AS g, count(*) AS n FROM {source} WHERE {where} GROUP BY g"
        rows = self._conn.execute(f"{grouped} ORDER BY {ranked} LIMIT ?", params + [bound]).fetchall()
        if group == "day" and walk == "desc":
            rows.reverse()
        total = self._conn.execute(f"SELECT count(*) FROM ({grouped})", params).fetchone()[0]
        return Page(tuple((g, n) for g, n in rows), total, bound)

    def read(self, record: str, last: int | None = None, after: int | None = None, *,
             before: int | None = None, order: str | None = None, since=None, until=None,
             key: str | None = None, prefix: str | None = None, where: dict | None = None,
             match: str | None = None) -> Page:
        """-> a page in rank order: the newest entries the filters select (`desc`, the default),
        or the oldest (`asc`, the default after an `after`); `last` asks fewer than the limit,
        never more; `next` the cursor of the following page, None at the end."""
        filters = {"since": since, "until": until, "key": key, "prefix": prefix, "where": where, "match": match}
        judge(last=last, after=after, before=before, order=order, **filters)
        names, sql, params, counting, counted, bound, walk = self._page_query(
            record, last, after, before, order, filters)
        if not self._exists(names):
            return Page((), 0, bound)
        rows = self._conn.execute(sql, params).fetchall()
        more = len(rows) > bound
        rows = rows[:bound]
        if walk == "desc":
            rows.reverse()
        entries = tuple(_entry(row) for row in rows)
        total = self._conn.execute(counting, counted).fetchone()[0]
        following = None
        if more and entries:
            following = {"before": entries[0].seq} if walk == "desc" else {"after": entries[-1].seq}
        return Page(entries, total, bound, following)

    def _explain(self, record: str, last: int | None = None, after: int | None = None, *,
                 before: int | None = None, order: str | None = None, **filters) -> list[str]:
        """-> the plan SQLite follows for the page `read` would ask -- one line per step."""
        names, sql, params, _, _, _, _ = self._page_query(record, last, after, before, order, filters)
        if not self._exists(names):
            return []
        return [row[-1] for row in self._conn.execute(f"EXPLAIN QUERY PLAN {sql}", params)]

    def search(self, text: str, records: Iterable[str] | None = None, **query) -> dict:
        """-> `{record: page}` of the entries holding `text`, in every record or the ones named --
        the text and every filter judged before a name is read."""
        judge(match=text, **query)
        names = list(records) if records is not None else self.records()
        return {name: self.read(name, match=text, **query) for name in names}

    def summary(self) -> list[dict]:
        """-> each record of the base with its count and the dates of its first and last entries."""
        found = []
        for name in self.records():
            total, first, last = self._conn.execute(
                f"SELECT count(*), min(at), max(at) FROM {_names(name).table}").fetchone()
            found.append({"record": name, "total": total, "first": first, "last": last})
        return found

    def after(self, record: str, seq: int) -> Page:
        """-> the entries that follow `seq`, in rank order, a bounded page."""
        return self.read(record, after=seq)

    def records(self) -> list[str]:
        """-> the names of the records the base holds."""
        if self._conn is None:
            return []
        names = self._conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' "
                                   "AND name LIKE 'r:%' ORDER BY name").fetchall()
        return [name[2:] for (name,) in names]

    def _shape(self, record: str) -> dict:
        """-> what the record IS in the base, read without writing: the journal mode, its columns,
        its indexes, its tokenizer, its total, its index entries and whether every row has its
        index entry and every index entry its row."""
        names = _names(record)
        if not self._exists(names):
            return {"journal": None, "columns": [], "indexes": {}, "tokenizer": None,
                    "total": 0, "indexed": 0, "consistent": True}
        conn, table = self._conn, names.table.strip('"')
        columns = [row[1] for row in conn.execute(f"PRAGMA table_info('{table}')")]
        indexes = {row[1]: [one[2] for one in conn.execute(f"PRAGMA index_info('{row[1]}')")]
                   for row in conn.execute(f"PRAGMA index_list('{table}')")}
        sql = conn.execute("SELECT sql FROM sqlite_master WHERE name = ?", (names.index.strip('"'),)).fetchone()
        orphans = conn.execute(f"SELECT count(*) FROM {names.table} r LEFT JOIN {names.docsize} d "
                               "ON d.id = r.seq WHERE d.id IS NULL").fetchone()[0]
        strays = conn.execute(f"SELECT count(*) FROM {names.docsize} d LEFT JOIN {names.table} r "
                              "ON r.seq = d.id WHERE r.seq IS NULL").fetchone()[0]
        return {"journal": conn.execute("PRAGMA journal_mode").fetchone()[0],
                "columns": columns, "indexes": indexes,
                "tokenizer": "trigram" if sql and "tokenize='trigram'" in sql[0] else None,
                "total": conn.execute(f"SELECT count(*) FROM {names.table}").fetchone()[0],
                "indexed": conn.execute(f"SELECT count(*) FROM {names.docsize}").fetchone()[0],
                "consistent": orphans == 0 and strays == 0}

    def _matching(self, record: str, text: str) -> int:
        """-> how many entries the trigram index finds holding `text` (3 characters or more)."""
        names = _names(record)
        if not self._exists(names):
            return 0
        phrase = '"' + str(text).replace('"', '""') + '"'
        return self._conn.execute(f"SELECT count(*) FROM {names.index} WHERE {names.index} MATCH ?",
                                  (phrase,)).fetchone()[0]


def _counting(source: str, index: str, where: str, clauses: list[str]) -> str:
    """-> the SQL of a total: a match alone is counted on the trigram index, the table untouched;
    any other selection on its source."""
    if clauses == [f"{index} MATCH ?"]:
        return f"SELECT count(*) FROM {index} WHERE {where}"
    return f"SELECT count(*) FROM {source} WHERE {where}"


def judge(group=None, last=None, after=None, before=None, order=None, since=None, until=None,
          key=None, prefix=None, where=None, match=None, counting: bool = False) -> None:
    """Judges a query whole before anything is read: a malformed filter refuses `filter-invalid`,
    a match too short `match-short` -- the record named, known or not, is never opened first. A
    COUNT (`counting`) takes no cursor, and without a group neither `last` nor `order`."""
    if counting and (after is not None or before is not None):
        raise Refusal("filter-invalid", "a count takes no cursor: `after` and `before` page a read")
    if counting and group is None and (last is not None or order is not None):
        raise Refusal("filter-invalid", "`last` and `order` page the groups of a count")
    if last is not None:
        _bound(last, last if isinstance(last, int) and not isinstance(last, bool) and last > 0 else 1)
    for value, name in ((after, "after"), (before, "before")):
        if value is not None:
            _seq(value, name)
    if group is None:
        _walk(order, after, before)
    elif group == "day":
        _walk(order, None, None)
    elif group != "key" and not FIELD_RE.fullmatch(str(group)):
        raise Refusal("filter-invalid", f"`group: {group}` — `day`, `key` or a field of the body")
    elif order is not None:
        raise Refusal("filter-invalid", f"`group: {group}` — a count by value takes no `order`, the most "
                                        "frequent come first")
    for value, name, end in ((since, "since", False), (until, "until", True)):
        if value is not None:
            _instant(value, name, end)
    _fields(where)
    if match is not None:
        _phrase(match)


def _scope(key, prefix) -> None:
    """Judges what a `remove` takes out: one key, or one prefix of the key that is not empty."""
    if (key is None) == (prefix is None):
        raise Refusal("store-remove-scope", "`remove` takes out a `key` or a `prefix`, one of the two")
    if prefix is not None and str(prefix) == "":
        raise Refusal("store-remove-scope", "`prefix` — an empty prefix would take out every keyed entry")


def _extract(body: str, field: str) -> str:
    """-> the SQL of a field of the body, its path a literal -- the one expression `where`, `group`
    and `index` write, so that SQLite takes the field's index; the field judged by `FIELD_RE` before."""
    return f"json_extract({body}, '{_path(field)}')"


def _path(field: str) -> str:
    """-> the JSON path of a field of the body, each step quoted: `$."run-key"`, `$."a"."b"`."""
    return "$" + "".join(f'."{one}"' for one in str(field).split("."))


def _bound(last, limit: int) -> int:
    """-> the bound of a page: the limit, or fewer when `last` asks fewer -- a whole number >= 1."""
    if last is None:
        return limit
    if isinstance(last, bool) or not isinstance(last, int) or last < 1:
        raise Refusal("filter-invalid", f"`last: {last}` — a whole number, 1 or more")
    return min(last, limit)


def _walk(order, after, before) -> str:
    """-> the walk of a page: `order`, else `asc` after an `after`, `desc` otherwise."""
    if after is not None and before is not None:
        raise Refusal("filter-invalid", "`after` and `before` — one cursor at a time")
    walk = order if order is not None else ("asc" if after is not None else "desc")
    if walk not in ("asc", "desc"):
        raise Refusal("filter-invalid", f"`order: {order}` — `asc` or `desc`")
    if (walk == "desc" and after is not None) or (walk == "asc" and before is not None):
        raise Refusal("filter-invalid", f"`order: {walk}` — `after` walks asc, `before` walks desc")
    return walk


def _seq(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Refusal("filter-invalid", f"`{name}: {value}` — a seq, a whole number")
    return value


def _instant(value, name: str, end: bool) -> str:
    """-> the bound of a time filter in the one form the store writes `at` (`AT_FORM`, UTC): a
    duration back from now; a date, its whole day (`until` takes the day after, excluded); a time
    read as `moment` reads `at` -- `AT_RE`, without an offset in UTC."""
    said = str(value).strip()
    span = DURATION_RE.fullmatch(said)
    if span:
        unit = {"d": "days", "h": "hours", "m": "minutes"}[span.group(2)]
        return (datetime.now(timezone.utc) - timedelta(**{unit: int(span.group(1))})).strftime(AT_FORM)
    try:
        if DAY_RE.fullmatch(said):
            day = date.fromisoformat(said) + timedelta(days=1 if end else 0)
            return moment(f"{day.isoformat()}T00:00Z")
        return moment(said)
    except (ValueError, Refusal):
        raise Refusal("filter-invalid", f"`{name}: {value}` — an ISO date or time, or a duration `<n>d|h|m`")


def _fields(where) -> list[tuple[str, Any]]:
    """-> the (field, value) pairs of `where`, each field a path of the body."""
    pairs = list((where or {}).items())
    for field, value in pairs:
        if not FIELD_RE.fullmatch(str(field)):
            raise Refusal("filter-invalid", f"`where: {field}` — a field of the body, `name` or `a.b`")
        if isinstance(value, (dict, list)):
            raise Refusal("filter-invalid", f"`where: {field}` — compared by equality to a scalar")
    return pairs


def _phrase(text) -> str:
    """-> the FTS5 query of a `match`: each word, or the quoted text in sequence -- each of
    `MATCH_MIN` characters or more, else `match-short`."""
    said = str(text).strip()
    if len(said) >= 2 and said[0] == said[-1] == '"':
        terms = [said[1:-1]]
    else:
        terms = said.split()
    if not terms or any(len(one) < MATCH_MIN for one in terms):
        raise Refusal("match-short", f"`{text}` — a match is {MATCH_MIN} characters or more, each word")
    return " AND ".join('"' + one.replace('"', '""') + '"' for one in terms)


def _entry(row) -> Entry:
    seq, at, key, body = row
    return Entry(seq, at, key, json.loads(body))
