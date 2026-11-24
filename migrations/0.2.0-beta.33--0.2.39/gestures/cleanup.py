"""What 0.2.39 no longer reads, removed once every count is equal (the backup keeps it):

- in every instance, the files the store took over -- `operations.jsonl`, `history.jsonl`,
  `steps.json` and their `.lock` -- and the marble `.sys/system.common.md`;
- in every team, the `TEAM-<name>.md` whose intention now stands in the body of `TEAM.md`;
- beside every instance, a door file the old install wrote (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`)
  only while its bytes are still the ones it wrote: an edited door is the user's, kept and said."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import DATA, RECORDS
from .teams import document, moved

TAKEN = ("operations.jsonl", "history.jsonl", "steps.json")
MARBLE = Path(".sys") / "system.common.md"


def cleanup(house) -> list[Path]:
    doors = json.loads((DATA / "doors.json").read_text(encoding="utf-8"))
    found: list[Path] = []
    for meta in house.instances:
        for name in TAKEN:
            found += [one for one in (meta / RECORDS / name, meta / RECORDS / f"{name}.lock") if one.is_file()]
        if (meta / MARBLE).is_file():
            found.append(meta / MARBLE)
        for name, digests in doors.items():
            path = meta.parent / name
            if not path.is_file():
                continue
            if hashlib.sha256(path.read_bytes()).hexdigest() in digests:
                found.append(path)
            else:
                print(f"migrate: cleanup: {path.relative_to(house.root)} kept -- edited since the install wrote "
                      "it; 0.2.39 no longer reads it", flush=True)
    found += [document(team) for team in house.teams if moved(team)]
    return found
