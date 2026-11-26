"""_common.frame -- `run`, the ONE that orders the steps of a migration.

    check, the lock taken last -> (--dry-run stops here, taking nothing) -> backup -> the lock's
    token written -> ./pp upgrade --from -> gestures -> table of counts -> cleanup when every count
    is equal -> ./pp doctor -> lock released, on a refusal too

A migration declares its gestures and its cleanup, nothing else: it never backs up, upgrades or
removes on its own. Nothing is written in the house before the check has passed and the backup
stands; the journal and the backup live BESIDE the house. From the end of the check to the end, the
frame holds the house's maintenance lock exclusive -- no pp process plays meanwhile -- and once the
backup stands it writes the lock's token and hands it to the console it launches."""
from __future__ import annotations

import argparse
import contextlib
import os
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

from . import backup, engine, house as houses
from .journal import Journal, equal, rows_of, table
from .refusal import BACKUP, LINE, MIGRATED, REFUSED, RESTORE, UNEQUAL, Refused

Gesture = Callable[[houses.House, object], Iterable[tuple]]
Cleanup = Callable[[houses.House], Iterable[Path]]


def run(argv: list[str], FROM: str, TO: str, GESTURES: list[tuple[str, Gesture]],
        CLEANUP: Cleanup | None) -> int:
    """Migrates the house `argv` names from `FROM` to `TO`. -> the exit code: 0 migrated, 2 refused,
    3 a count that differs."""
    for key in [one for one in os.environ if one.startswith("PP_")]:
        del os.environ[key]                  # the frame owns the environment the console inherits
    parser = argparse.ArgumentParser(prog="migrate.py", description=f"migrate a house from {FROM} to {TO}")
    parser.add_argument("house", help="the root of the house: the folder that holds its .pp/")
    parser.add_argument("--from", dest="source", required=True,
                        help=f"a checkout of the product at {TO} (its GitHub tag)")
    parser.add_argument("--dry-run", action="store_true", help="play the check alone and say the steps")
    try:
        args = parser.parse_args(argv)
    except SystemExit as stop:
        return REFUSED if stop.code else MIGRATED
    root = Path(args.house).expanduser().resolve()
    source = Path(args.source).expanduser().resolve()
    named = f"{root.name}.pre-{TO}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    target = root.parent / (named + backup.SUFFIX)
    journal = Journal()
    try:
        house, hold = check(root, source, FROM, TO, args.dry_run, journal)
    except Exception as error:                                         # noqa: BLE001 -- a code, never a crash
        return refused(failed("check", error), None, root)
    if hold is None:
        for name, _ in GESTURES:
            journal("would-play", gesture=name)
        journal("dry-run", backup=target, journal=target.with_name(named + ".log"))
        return MIGRATED
    try:
        try:
            journal.stage = "backup"
            journal.open(target.with_name(named + ".log"))
            journal("backup", path=target, bytes=backup.archive(root, target))
        except Exception as error:                                     # noqa: BLE001 -- no backup: nothing written
            return refused(failed("backup", error), None, root)
        try:
            return migrated(house, hold, source, TO, GESTURES, CLEANUP, journal, target)
        except Exception as error:                                     # noqa: BLE001 -- said with the way back
            refusal = failed(journal.stage, error)
            with contextlib.suppress(Exception):
                journal("refused", code=refusal.code, detail=refusal.detail)
            return refused(refusal, target, root)
    finally:
        engine.give(hold)


def failed(step: str, error: BaseException) -> Refused:
    """-> the refusal an error becomes: a Refused as it stands, any other error `<step>-failed`
    with its type and text, its traceback said on stderr."""
    if isinstance(error, Refused):
        return error
    traceback.print_exception(type(error), error, error.__traceback__)
    return Refused(f"{step}-failed", f"{type(error).__name__}: {error}")


def check(root: Path, source: Path, FROM: str, TO: str, dry: bool, journal: Journal):
    """-> the house and the hold of its lock, once everything a migration needs holds -- the lock
    taken LAST, its token not written; a dry run takes nothing (hold None) and only tries it. Refuses
    by code otherwise, nothing written: `house-missing`, `house-version`, `source-missing`,
    `source-version`, `space`, `house-busy`."""
    house = houses.read(root)
    if house.version != FROM:
        raise Refused("house-version", f"the house at {root} stands at {house.version}, this migration "
                                       f"starts from {FROM}")
    at_source = houses.source_version(source)
    if at_source is None:
        raise Refused("source-missing", f"{source} is not a checkout of the product")
    if at_source != TO:
        raise Refused("source-version", f"the source at {source} stands at {at_source}, this migration "
                                        f"needs {TO} -- its GitHub tag")
    size = weight(root)
    if not os.access(root.parent, os.W_OK) or shutil.disk_usage(root.parent).free < size:
        raise Refused("space", f"{root.parent} must be writable and hold {size} bytes for the backup")
    engine.mounted(root)
    if dry:
        if engine.busy(root):
            raise Refused("house-busy", f"a pp process lives in the house at {root} -- end it, then replay")
        hold = None
    else:
        hold = engine.take(root)
    journal("check", house=root, version=FROM, to=TO, source=source, instances=len(house.instances),
            plans=len(house.plans), teams=len(house.teams), bytes=size)
    if hold is not None:
        journal("lock", house=root)
    return house, hold


def migrated(house: houses.House, hold, source: Path, TO: str, GESTURES, CLEANUP, journal: Journal,
             target: Path) -> int:
    """The steps after the backup, under the house's lock, its token now written: the upgrade, the
    gestures, the counts, the cleanup, the doctor."""
    root = house.root
    journal.stage = "arm"
    engine.arm(hold)
    journal.stage = "upgrade"
    said(journal, "upgrade", engine.console(root, "upgrade", "--from", str(source)))
    house = houses.read(root)
    if house.version != TO:
        raise Refused("upgrade", f"the house stands at {house.version} after the upgrade, not {TO}")
    journal.stage = "mount"
    conductor = engine.mounted(root)
    rows: list[dict] = []
    for name, gesture in GESTURES:
        journal.stage = "gesture"
        journal("gesture", name=name)
        try:
            found = rows_of(root, gesture(house, conductor))
        except Refused:
            raise
        except Exception as error:                                  # noqa: BLE001 -- said, never lost
            refusal = failed("gesture", error)
            raise Refused(refusal.code, f"{name}: {refusal.detail}") from None
        journal("counted", gesture=name, rows=len(found))
        rows += found
    journal.stage = "counts"
    journal("counts", rows=rows, equal=equal(rows))
    print(table(rows), flush=True)
    if not equal(rows):
        journal("unequal")
        print(LINE.format(code="unequal", detail="a count differs, nothing removed"), file=sys.stderr)
        restoring(root, target)
        return UNEQUAL
    journal.stage = "cleanup"
    removed = cleaned(house, CLEANUP)
    journal("cleanup", removed=removed)
    journal.stage = "doctor"
    said(journal, "doctor", engine.console(root, "doctor"))
    journal("migrated", to=TO)
    return MIGRATED


def cleaned(house: houses.House, CLEANUP) -> list[str]:
    """Removes what the migration's cleanup names: a relative path read from the house's root, never
    from the current directory; a link removed as a link, never followed. Refuses `cleanup-outside`,
    nothing removed, for a path outside the house, the house itself or a path under a `.git`.
    -> the paths removed, under the house."""
    root = house.root
    paths = []
    for one in (CLEANUP(house) if CLEANUP else []):
        given = Path(one)
        whole = Path(os.path.normpath(given if given.is_absolute() else root / given))
        paths.append(whole.parent.resolve() / whole.name)
    outside = [str(one) for one in paths if one == root or not one.is_relative_to(root)
               or backup.SKIPPED in one.relative_to(root).parts]
    if outside:
        raise Refused("cleanup-outside", f"the cleanup names what it may not remove: {', '.join(outside)}")
    removed = []
    for path in paths:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            continue
        removed.append(path.relative_to(root).as_posix())
    return removed


def said(journal: Journal, step: str, done) -> None:
    """A console's call kept in the journal; a non-zero exit refuses under the step's name."""
    lines = (done.stdout + done.stderr).splitlines()
    journal(step, rc=done.returncode, lines=lines)
    if done.returncode != 0:
        raise Refused(step, (lines or ["(no output)"])[-1])


def weight(root: Path) -> int:
    """-> the bytes the backup reads: every file of the house but its own `.git`."""
    total = 0
    for here, directories, files in os.walk(root):
        if Path(here) == root:
            directories[:] = [name for name in directories if name != backup.SKIPPED]
        for name in files:
            try:
                total += (Path(here) / name).lstat().st_size
            except OSError:
                pass
    return total


def refused(refusal: Refused, target: Path | None, root: Path) -> int:
    print(LINE.format(code=refusal.code, detail=refusal.detail), file=sys.stderr, flush=True)
    if target is not None:
        restoring(root, target)
    return REFUSED


def restoring(root: Path, target: Path) -> None:
    """Says how to come back: the backup, and the commands that restore it -- never played."""
    print(BACKUP.format(path=target), file=sys.stderr)
    print(RESTORE.format(command=backup.restore(root, target)), file=sys.stderr, flush=True)
