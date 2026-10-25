"""The SUPPORT module of the `continuity` area's engine scenarios (tests/README.md, rule 10):
the operator's edit of a `continuity_` key in the composed SETTINGS, and the record of
operations a case writes. Loaded by `support(__file__, "continuity")`.
"""
from __future__ import annotations

import json
import re
from datetime import datetime


def setting(env, key: str, value: str) -> bool:
    """The operator's edit of one key of the composed SETTINGS; -> whether the key stands."""
    text = env.read("SETTINGS.md")
    edited = re.sub(rf"^{key}: .*$", f"{key}: {value}", text, flags=re.M)
    env.write("SETTINGS.md", edited)
    return f"\n{key}: {value}" in "\n" + edited


def operations(made, stamped: list[tuple[datetime, str]]) -> None:
    """The record of operations, written whole: one dated entry a line."""
    path = made / ".sys" / "records" / "operations.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps({"at": when.isoformat(timespec="seconds"), "entry": text})
                            + "\n" for when, text in stamped), encoding="utf-8")
