"""packages/steering/skills/pp-steering -- the LARGE book, read through a filter: on 100 000
archived steps, the five oldest born again 20 days ago, `list --archived --since` finds them past the
first pages of the walk, the newest born first, and its total counts that selection alone."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from tests.harness import support

K = support(__file__, "keeper")

NOW = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)


def at(days: float) -> str:
    return (NOW - timedelta(days=days)).isoformat()


def scenario(bench) -> int:
    big, play, mine = K.large_book(bench, "steering-filters-large", at(1), at(40))
    with K.case(bench, "every filter judges the archived page", "the five oldest steps born again 20 days ago: "
                "`list --archived --since` finds them at the end of the walk, the newest born first, its total "
                "the selection's") as check:
        reborn = {}
        for n in range(1, 6):
            one = K.kept(big).get(K.STEPS, f"{mine}.s.{n}").body
            reborn[f"{mine}.s.{n}"] = {**one, "at": at(20), "touched": at(20), "closed": at(20), "archived": at(19)}
        K.lay(big, reborn)
        found = json.loads(play("list", "--archived", "--since", at(25)[:10], "--json").stdout or "{}")
        check([one["id"] for one in found.get("rows", [])] == [f"{mine}.s.{n}" for n in range(5, 0, -1)]
              and found.get("total") == 5 and found.get("bound") == K.kept(big).limit(),
              f"the selection {[(k, v) for k, v in found.items() if k != 'rows']} {[one['id'] for one in found.get('rows', [])]}")
    return 0
