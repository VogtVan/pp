"""_common.refusal -- a refusal by code, and the exit codes of a migration.

0  the house is migrated: every count equal, the cleanup done, `./pp doctor` passed
2  refused -- at the check or the backup, the house untouched; at a later step, the steps after it
   not played and nothing removed, but the house may be half migrated: restore the backup
3  a count differs after the gestures: nothing removed
"""

import re

MIGRATED, REFUSED, UNEQUAL = 0, 2, 3

LINE = "migrate: refused {code} -- {detail}"     # the refusal said on stderr: its code first
BACKUP = "migrate: the backup stands at {path}"  # said after a refusal or a count that differs
RESTORE = "migrate: to restore it: {command}"    # the commands that restore the backup, never played


def _reader(form: str, field: str) -> re.Pattern:
    head, tail = form.split("{" + field + "}")
    return re.compile(re.escape(head) + (r"([a-z0-9-]+)" if tail else r"(.+)$") + re.escape(tail.split("{")[0]), re.M)


def code_of(said: str) -> str | None:
    """-> the code of the refusal a migration said on stderr, read by its LINE; None without one."""
    found = _reader(LINE, "code").search(said)
    return found.group(1) if found else None


def restore_of(said: str) -> str | None:
    """-> the restoring commands a migration said on stderr, read by its RESTORE line."""
    found = _reader(RESTORE, "command").search(said)
    return found.group(1) if found else None


class Refused(Exception):
    """A step that refuses: its CODE (`house-version`, `source-version`, `house-busy`, `space`, or a
    gesture's own) and a detail for the user. The frame stops at the step that raised it."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
