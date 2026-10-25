"""packages/steering/skills/pp-steering -- the ARCHIVES, the keeper played as a script in a
subprocess as the console runs it, every call under a frozen clock (`PP_NOW`): `sweep`
archives a step older than `steering_life_days` -- its age read from its recall when it has
one, from its last touch otherwise -- then the least recently touched steps still to do past
`steering_active_max`, and says each one; `recall` brings a step back and restarts its age;
`review` lists the steps still to do, the least recently touched first; `list --archived`
shows the archived ones. Archiving and recalling move `archived` and `recalled` alone."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

from tests.harness import support

K = support(__file__, "keeper")

NOW = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
KEPT = ("name", "at", "work", "comment", "status", "reason", "labels", "key", "touched")


def scenario(bench) -> int:
    root = bench.env("steering-archives", ("steering",), pin=False).made
    script = K.script_of(root)
    run = K.player(script, root.parent)

    def at(days: float = 0) -> str:
        return (NOW - timedelta(days=days)).isoformat()

    def play(when: str, *args: str):
        return run(*args, env={**os.environ, K.CLOCK: when})

    def added(when: str, name: str) -> str:
        played = play(when, "add", name, f"le travail de {name}")
        if played.returncode != 0:
            raise AssertionError(played.stderr)
        return max(K.record(root)["steps"], key=lambda sid: int(sid.rsplit(".", 1)[1]))

    def data(when: str, *args: str) -> list[dict]:
        played = play(when, *args, "--json")
        if played.returncode != 0:
            raise AssertionError(played.stderr)
        return json.loads(played.stdout)

    def rest(sid: str) -> dict:
        """-> what archiving and recalling must leave alone."""
        step = K.record(root)["steps"][sid]
        return {field: step[field] for field in KEPT}

    # --- the age ------------------------------------------------------------------------------
    with K.case(bench, "sweep archives by age", "a step touched 16 days ago is archived, one touched 14 days "
                "ago is not; sweep names the archived step by its id; a second sweep archives nothing; the rest "
                "of each step byte-identical") as check:
        old = added(at(16), "le-pas-ancien")
        young = added(at(14), "le-pas-recent")
        before = {sid: rest(sid) for sid in (old, young)}
        swept = play(at(), "sweep")
        steps = K.record(root)["steps"]
        check(swept.returncode == 0 and old in swept.stdout and young not in swept.stdout, swept.stdout + swept.stderr)
        check(steps[old]["archived"] == datetime.fromisoformat(at()).isoformat(timespec="microseconds")
              and steps[young]["archived"] is None, "the old archived at the clock, the young kept")
        check({sid: rest(sid) for sid in (old, young)} == before, "archiving moved another field")
        still = K.spool(root).read_bytes()
        again = play(at(), "sweep")
        check(again.returncode == 0 and old not in again.stdout and K.spool(root).read_bytes() == still,
              "a second sweep wrote")

    # --- the ceiling --------------------------------------------------------------------------
    with K.case(bench, "sweep holds the ceiling", "with steering_active_max at 3 and five recent open steps, "
                "the two least recently touched are archived; a done step counts for nothing") as check:
        play(at(), "done", young)
        K.set_to(root, "steering_active_max", 3)
        fives = [added(at(days), f"le-pas-{days}") for days in (5, 4, 3, 2, 1)]
        closed = added(at(6), "le-pas-clos")
        play(at(), "done", closed)
        before = {sid: rest(sid) for sid in fives}
        play(at(), "sweep")
        steps = K.record(root)["steps"]
        check([steps[sid]["archived"] is not None for sid in fives] == [True, True, False, False, False],
              f"archived {[steps[sid]['archived'] for sid in fives]}")
        check(steps[closed]["archived"] is None and steps[young]["archived"] is None, "the done steps untouched")
        check({sid: rest(sid) for sid in fives} == before, "the ceiling moved another field")
        K.set_to(root, "steering_active_max", 60)

    # --- the recall ---------------------------------------------------------------------------
    with K.case(bench, "recall restarts the age", "recall empties `archived` and sets `recalled` at the clock; "
                "a sweep right after keeps the step; recall of an active step refuses step-active, nothing "
                "written; the rest of the step byte-identical") as check:
        before = rest(old)
        played = play(at(), "recall", old)
        step = K.record(root)["steps"][old]
        check(played.returncode == 0 and step["archived"] is None
              and step["recalled"] == datetime.fromisoformat(at()).isoformat(timespec="microseconds"), played.stderr)
        play(at(), "sweep")
        check(K.record(root)["steps"][old]["archived"] is None, "the recalled step archived again")
        check(rest(old) == before, "recalling moved another field")
        kept = K.spool(root).read_bytes()
        K.refused(bench, play(at(), "recall", old), "step-active")
        check(K.spool(root).read_bytes() == kept, "step-active wrote")

    # --- the archived and the review ----------------------------------------------------------
    with K.case(bench, "list and review", "`list --archived` returns the archived steps alone, `list` none of "
                "them; `review` returns the active steps still to do, the least recently touched first, each "
                "with its name and id") as check:
        archived = {sid for sid, step in K.record(root)["steps"].items() if step["archived"]}
        check({one["id"] for one in data(at(), "list", "--archived")} == archived and archived, f"archived {archived}")
        check(not archived & {one["id"] for one in data(at(), "list", "--all")}, "list shows an archived step")
        seen = data(at(), "review")
        due = [sid for sid, step in K.record(root)["steps"].items()
               if not step["archived"] and step["status"] in ("open", "waiting")]
        check({one["id"] for one in seen} == set(due) and all(one["name"] for one in seen), f"review {seen}")
        ages = [one.get("recalled") or one["touched"] for one in seen]
        check(ages == sorted(ages), "the least recently touched first")

    # --- the settings -------------------------------------------------------------------------
    with K.case(bench, "the life is a setting", "steering_life_days at 1 archives a step touched two days "
                "ago; the composed SETTINGS carries the five keys of the fragment and none of the table's") as check:
        two = added(at(2), "le-pas-de-deux-jours")
        K.set_to(root, "steering_life_days", 1)
        play(at(), "sweep")
        check(K.record(root)["steps"][two]["archived"] is not None, "life_days not read")
        K.set_to(root, "steering_life_days", 15)
        lines = (root / "SETTINGS.md").read_text(encoding="utf-8").splitlines()
        front = lines[1:lines.index("---", 1)]
        keys = {line.split(":", 1)[0] for line in front if line.startswith("steering_")}
        check(keys == {"steering_step_budget", "steering_name_max", "steering_note_budget", "steering_life_days",
                       "steering_active_max"}, f"the keys {sorted(keys)}")

    return 0
