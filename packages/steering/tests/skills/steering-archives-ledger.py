"""packages/steering/skills/pp-steering -- the LARGE book, read without a filter: on 100 000
archived steps and 60 active ones, `list --sweep` serves the 60 and archives nothing, its query of
the active steps searching the index of `archived` and never walking the archived; `list --archived`
serves one page of the store's bound, the newest born first, and says the total of the archived --
its --json `{rows, total, bound}`."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from tests.harness import support

K = support(__file__, "keeper")

NOW = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)


def scenario(bench) -> int:
    big, play, _ = K.large_book(bench, "steering-ledger-large", (NOW - timedelta(days=1)).isoformat(),
                                (NOW - timedelta(days=40)).isoformat())
    with K.case(bench, "the ledger never walks the archived", "`list --sweep` serves the 60 active steps and "
                "archives nothing; the query of the active steps searches the index of `archived`") as check:
        ledger = play("list", "--sweep")
        lines = [one for one in ledger.stdout.splitlines() if one.strip()]
        check(ledger.returncode == 0 and len(lines) == 60 and all("un-pas-actif-" in one for one in lines),
              f"{len(lines)} lines {ledger.stderr[-200:]}")
        plan = " ".join(K.kept(big)._explain(K.STEPS, where={"archived": None}))
        check("j:steps:archived" in plan and "SCAN" not in plan.replace("SCAN USING", ""), f"the plan {plan}")

    with K.case(bench, "the archived page without a filter", "`list --archived` serves one page of the bound and "
                "says the total; its --json `{rows, total, bound}`, the newest born first") as check:
        bound = K.kept(big).limit()
        page = play("list", "--archived")
        shown = [one for one in page.stdout.splitlines() if "un-pas-archive-" in one]
        check(page.returncode == 0 and len(shown) == bound and str(K.LARGE) in page.stdout.replace(" ", ""),
              f"{len(shown)} shown {page.stdout[-160:]!r}")
        found = json.loads(play("list", "--archived", "--json").stdout or "{}")
        check(len(found.get("rows", [])) == bound and found.get("total") == K.LARGE and found.get("bound") == bound,
              f"the --json page {[(k, v) for k, v in found.items() if k != 'rows']}")
        numbers = [int(one["id"].rsplit(".", 1)[1]) for one in found.get("rows", [])]
        check(numbers == sorted(numbers, reverse=True) and numbers[:1] == [K.LARGE], "the newest born first")
    return 0
