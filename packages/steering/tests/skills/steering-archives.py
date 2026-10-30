"""packages/steering/skills/pp-steering -- the ARCHIVES, the keeper played as a script in a
subprocess as the console runs it, every call under a frozen clock (`PP_NOW`): `sweep`
archives a step older than `steering_life_days` -- its age read from its recall when it has
one, from its last touch otherwise -- then the least recently touched steps still to do past
`steering_active_max`, and says each one; `recall` brings a step back and restarts its age;
`review` lists the steps still to do, the least recently touched first; `list --archived`
shows the archived ones. Archiving and recalling move `archived` and `recalled` alone. On a
record laid by hand: `board` (the counts, the week, the durations, the least touched, the labels
and their freshest steps), `labels`, the filters of `list` (the key's family among them) and its groupings, all read from the
fields; `list --sweep` sweeps, lists, and names at its foot what it has just archived."""
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
                "ago is not; sweep names the archived step by its short id; a second sweep archives nothing; the rest "
                "of each step byte-identical") as check:
        old = added(at(16), "le-pas-ancien")
        young = added(at(14), "le-pas-recent")
        before = {sid: rest(sid) for sid in (old, young)}
        swept = play(at(), "sweep")
        steps = K.record(root)["steps"]
        check(swept.returncode == 0 and f"[{K.short(old)}]" in swept.stdout and f"[{K.short(young)}]" not in swept.stdout,
              swept.stdout + swept.stderr)
        check(steps[old]["archived"] == datetime.fromisoformat(at()).isoformat(timespec="microseconds")
              and steps[young]["archived"] is None, "the old archived at the clock, the young kept")
        check({sid: rest(sid) for sid in (old, young)} == before, "archiving moved another field")
        still = K.spool(root).read_bytes()
        again = play(at(), "sweep")
        check(again.returncode == 0 and f"[{K.short(old)}]" not in again.stdout and K.spool(root).read_bytes() == still,
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
                "ago; the composed SETTINGS carries the six keys of the fragment and none of the table's") as check:
        two = added(at(2), "le-pas-de-deux-jours")
        K.set_to(root, "steering_life_days", 1)
        play(at(), "sweep")
        check(K.record(root)["steps"][two]["archived"] is not None, "life_days not read")
        K.set_to(root, "steering_life_days", 15)
        lines = (root / "SETTINGS.md").read_text(encoding="utf-8").splitlines()
        front = lines[1:lines.index("---", 1)]
        keys = {line.split(":", 1)[0] for line in front if line.startswith("steering_")}
        check(keys == {"steering_step_budget", "steering_name_max", "steering_note_budget", "steering_life_days",
                       "steering_active_max", "steering_board_per_label"}, f"the keys {sorted(keys)}")

    # --- a record laid by hand: the views read its fields --------------------------------------
    member = root.resolve().parent.name
    sid = {n: f"{member}.s.{n}" for n in range(1, 10)}
    day = 86400

    def laid(n: int, status: str, born: float, touched: float, labels=(), closed=None, archived=None,
             recalled=None, key=None, work=None) -> dict:
        return {"name": f"le-pas-pose-{n}", "at": at(born), "work": work or f"le travail {n}", "comment": "",
                "status": status, "reason": "pourquoi" if status in ("waiting", "dropped") else "",
                "labels": list(labels), "key": key, "touched": at(touched),
                "archived": None if archived is None else at(archived),
                "recalled": None if recalled is None else at(recalled), "closed": None if closed is None else at(closed)}

    steps = {sid[1]: laid(1, "open", 20, 1, ("alpha",), key="plan-lot:demo/survey/map"),
             sid[2]: laid(2, "open", 10, 9, ("alpha",), recalled=8, key="plan-phase:demo/survey"),
             sid[3]: laid(3, "waiting", 5, 4, ("alpha", "beta")),
             sid[4]: laid(4, "done", 6, 2, closed=2),
             sid[5]: laid(5, "dropped", 3, 1, ("beta",), closed=1),
             sid[6]: laid(6, "done", 30, 20, closed=20, archived=3),
             sid[7]: laid(7, "open", 2, 2, recalled=0.5, work="plan-lot:demo/survey/map, named and never keyed"),
             sid[8]: laid(8, "done", 1, 1)}
    labels = {"alpha": {"note": "la note alpha", "order": [sid[1], sid[2], sid[3]]},
              "beta": {"note": "", "order": [sid[3], sid[5]]}}
    K.spool(root).write_text(json.dumps({"counters": {"s": 8}, "steps": steps, "labels": labels}, ensure_ascii=False,
                                        indent=1) + "\n", encoding="utf-8")

    with K.case(bench, "board reads the fields", "the counts by status, the week, the durations to closure "
                "and the ages (median, p90, max), the least touched, each label with its freshest steps, the "
                "unlabelled") as check:
        seen = json.loads(play(at(), "board", "--json").stdout or "{}")
        check(seen.get("counts") == {"open": {"active": 3, "archived": 0}, "waiting": {"active": 1, "archived": 0},
                                     "done": {"active": 2, "archived": 1}, "dropped": {"active": 1, "archived": 0}},
              f"counts {seen.get('counts')}")
        check(seen.get("week") == {"born": 5, "done": 1, "dropped": 1, "archived": 1, "recalled": 1},
              f"week {seen.get('week')}")
        check(seen.get("resolution") == {"count": 3, "median": 4 * day, "p90": 10 * day, "max": 10 * day},
              f"resolution {seen.get('resolution')}")
        check(seen.get("age") == {"count": 4, "median": day, "p90": 8 * day, "max": 8 * day}, f"age {seen.get('age')}")
        check(seen.get("least_touched") == [sid[2], sid[3], sid[1], sid[7]], f"least {seen.get('least_touched')}")
        check(seen.get("labels") == [
            {"name": "alpha", "note": "la note alpha", "open": 2, "waiting": 1, "touched": at(1),
             "recent": [sid[1], sid[3], sid[2]]},
            {"name": "beta", "note": "", "open": 0, "waiting": 1, "touched": at(4), "recent": [sid[3]]}],
            f"labels {seen.get('labels')}")
        check(seen.get("unlabelled") == {"open": 1, "waiting": 0, "recent": [sid[7]]}, f"unlabelled {seen.get('unlabelled')}")
        text = play(at(), "board").stdout
        check("[s.2]" in text and f"[{sid[2]}]" not in text, "the text says the short ids")

    with K.case(bench, "labels counts each label", "one entry per label, its note and counts in the active steps "
                "still to do; --all counts the closed ones too") as check:
        seen = {one["name"]: one for one in json.loads(play(at(), "labels", "--json").stdout or "[]")}
        check((seen.get("alpha") or {}).get("open") == 2 and seen["alpha"]["waiting"] == 1
              and seen["alpha"]["oldest"] == at(8) and seen["alpha"]["latest"] == at(1), f"alpha {seen.get('alpha')}")
        every = {one["name"]: one for one in json.loads(play(at(), "labels", "--all", "--json").stdout or "[]")}
        check((every.get("beta") or {}).get("dropped") == 1 and every["beta"]["latest"] == at(1), f"beta {every.get('beta')}")

    def ids(*args: str) -> list[str]:
        return [one["id"] for one in data(at(), "list", *args)]

    with K.case(bench, "list filters on the fields", "--status widens to the statuses named, --older and --newer "
                "read the age, --since and --before the birth, --key the family of the key, combined with --label") as check:
        check(ids("--status", "waiting") == [sid[3]], "--status waiting")
        check(set(ids("--status", "done")) == {sid[4], sid[8]}, "--status done")
        check(set(ids("--older", "3d")) == {sid[2], sid[3]}, "--older")
        check(set(ids("--newer", "3d")) == {sid[1], sid[7]}, "--newer")
        check(ids("--since", at(3)[:10]) == [sid[7]], "--since")
        check(set(ids("--before", at(9)[:10])) == {sid[1], sid[2]}, "--before")
        check(set(ids("--older", "3d", "--label", "alpha")) == {sid[2], sid[3]}, "combined")
        K.refused(bench, play(at(), "list", "--older", "trois"), "step-invalid")
        check(ids("--key", "plan-lot") == [sid[1]], "--key reads the family of the key alone")
        check(set(ids("--key", "plan-lot", "--key", "plan-phase")) == {sid[1], sid[2]}, "--key repeated")
        check(ids("--key", "plan-phase", "--label", "alpha") == [sid[2]], "--key combined with --label")
        check(ids("--key", "zorg") == [], "--key of a family no step carries")
        K.refused(bench, play(at(), "list", "--key", "plan-lot:demo"), "step-invalid")

    with K.case(bench, "list groups by a field", "--by label puts a step under each of its labels, the unlabelled "
                "last; --by status follows the statuses; --by age the slices of age") as check:
        def groups(by: str) -> list:
            played = play(at(), "list", "--by", by, "--json")
            return [(one["group"], [step["id"] for step in one["steps"]]) for one in json.loads(played.stdout or "[]")]
        check(groups("label") == [("alpha", [sid[1], sid[3], sid[2]]), ("beta", [sid[3]]), (None, [sid[7]])],
              f"label {groups('label')}")
        check(groups("status") == [("open", [sid[7], sid[1], sid[2]]), ("waiting", [sid[3]])], f"status {groups('status')}")
        check(groups("age") == [("<1d", [sid[7]]), ("1-3d", [sid[1]]), ("3-7d", [sid[3]]), ("7-15d", [sid[2]])],
              f"age {groups('age')}")

    with K.case(bench, "list --sweep names what it archives", "a step past its life is archived by `list --sweep`, "
                "absent from the lines and named at their foot; a second call names nothing") as check:
        forged = K.record(root)
        forged["steps"][sid[9]] = laid(9, "open", 18, 16)
        forged["counters"]["s"] = 9
        K.spool(root).write_text(json.dumps(forged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        first, second = play(at(), "list", "--sweep"), play(at(), "list", "--sweep")
        check(first.returncode == 0 and "[s.9]" in first.stdout and "[s.1]" in first.stdout, first.stdout + first.stderr)
        check(K.record(root)["steps"][sid[9]]["archived"] is not None, "not archived")
        check(second.returncode == 0 and "[s.9]" not in second.stdout, "a second call names it again")

    return 0
