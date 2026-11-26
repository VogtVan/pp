"""_common.journal -- the journal of a migration, and its table of counts.

The journal is one JSON object per line, `{"at", "step", ...}`, BESIDE the house: what was checked,
backed up, upgraded, played, counted, removed. Until it is opened (after the check) it keeps its
entries in memory; a dry run never opens it. Each entry is also said on the standard output."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class Journal:
    def __init__(self) -> None:
        self.path: Path | None = None
        self.entries: list[dict] = []
        self.stage = "check"          # the step under way: what an error is named after, `<stage>-failed`

    def __call__(self, step: str, **fields) -> None:
        entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "step": step, **fields}
        self.entries.append(entry)
        said = " ".join(f"{key}={value}" for key, value in fields.items() if key != "lines")
        print(f"migrate: {step} {said}".rstrip(), flush=True)
        if self.path is not None:
            self._write([entry])

    def open(self, path: Path) -> None:
        """From now on every entry is written at `path`, the ones held so far first."""
        self.path = path
        self._write(self.entries)

    def _write(self, entries: list[dict]) -> None:
        with open(self.path, "a", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry, default=str) + "\n")


def rows_of(root: Path, rows) -> list[dict]:
    """-> the count rows a gesture returned, `(instance, record, before, after)`, as objects: the
    instance said by its path under the house."""
    found = []
    for instance, record, before, after in rows or []:
        path = Path(instance)
        where = path.relative_to(root).as_posix() if path.is_absolute() and path.is_relative_to(root) else str(instance)
        found.append({"instance": where, "record": record, "before": before, "after": after})
    return found


def equal(rows: list[dict]) -> bool:
    return all(row["before"] == row["after"] for row in rows)


def table(rows: list[dict]) -> str:
    """-> the counts as a markdown table, one row per instance and record."""
    lines = ["| instance | record | before | after | |", "|---|---|---:|---:|---|"]
    lines += [f"| {row['instance']} | {row['record']} | {row['before']} | {row['after']} | "
              f"{'=' if row['before'] == row['after'] else 'DIFFERS'} |" for row in rows]
    return "\n".join(lines)
