"""The SUPPORT module of the `continuity` area's engine scenarios (tests/README.md, rule 10):
the operator's edit of a `continuity_` key in the composed SETTINGS, and the entries a case adds
to the records of continuity -- through the instance's store, never a file. Loaded by
`support(__file__, "continuity")`.
"""
from __future__ import annotations

import re
from datetime import datetime

from conductor import store


def setting(env, key: str, value: str) -> bool:
    """The operator's edit of one key of the composed SETTINGS; -> whether the key stands."""
    text = env.read("SETTINGS.md")
    edited = re.sub(rf"^{key}: .*$", f"{key}: {value}", text, flags=re.M)
    env.write("SETTINGS.md", edited)
    return f"\n{key}: {value}" in "\n" + edited


def operations(made, stamped: list[tuple[datetime, str]]) -> None:
    """Operations ADDED to the record `operations`, in the order given: one dated entry each."""
    store.of(made).extend("operations", ({"at": when, "body": {"entry": text}} for when, text in stamped))


def history(made, when: datetime, text: str = "bench") -> None:
    """One digest ADDED to the record `history`, dated `when`."""
    store.of(made).append("history", {"synthesis": text}, at=when)


def entries(made, record: str = "operations") -> list:
    """-> the latest page of `record` (`store.read`), oldest first."""
    return list(store.of(made).read(record).rows)
