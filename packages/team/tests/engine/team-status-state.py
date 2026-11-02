"""Scenario `team-status-state` -- 5 case(s): `team status --json` says the team's `state` -- derived from the replay,
never written -- and, while it waits, `waiting_on`: every guard that holds, in the order `woken_on` judges them
(`members`, `launches`, `budget`), then `owner`, `suspected`, `due`; the object and the team's line on the every-team
face say the same. The line counts what waits for the owner as the inbox does; the object says the team's season and
the launch its next wake-up gets. Six teams run side by side in one house, each under its own names; each case waits
for its team, then reads its faces.
- (a) the state and its guards: `flow` says `never` before its start, `waiting [due]` after a start without a tick,
  `working` while r1 and r2 play, `waiting [members, owner]` once r1 asked the owner and r2 answered, `idle` once T1
  is resolved
- (b) the wake-ups of a task: while r1 and r2 play on T1 -- their witnesses held at a gate until the face is read --,
  `tasks[T1].running` carries both -- member, tag, run, since, allowance --, then `[]` at their end
- (c) the guards of the bounds and of a failure: `dear` (`budget-launches: 1`) says `waiting [budget]`; `count`
  (`launches: 1`) says `waiting [launches]`; `fail` (`retries: 0`, its root dead, reaped by a tick at hand under
  `schedule: off`) says `waiting [owner, suspected]` -- the guards' notices hold nobody
- (d) the badge counts the inbox: e, the root, dies on T1 under `retries: 0` -- the team's notice about it to the
  owner --, then, past its interval, resolves T2 and T3: the line says `asks 0`, `notices 1`, `done 2`, as
  `inbox --json` counts them; `team inbox --seen`, then `done 0` and the notice kept, about e
- (e) the season and the launch: a second start says `season {n: 2}`; `launch` says the provider the start was
  given, every key of the face present, and never `max_budget_usd` -- not even the one an older journal kept; each
  member carries the same launch
"""
from __future__ import annotations

import json

from tests.harness import race, support

T = support(__file__, "team")

LAUNCH = {"harness", "provider", "model", "permissions", "effort", "packages"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (a)(b) m delegates to r1 and r2; r1 asks the owner; r2 answers
        "m": [{"sleep": 0.1, "body": {"do": ["r1", "r2"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "r1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
               {"sleep": 0.1, "body": {"done": True}}],
        "r2": [{"sleep": 0.1, "body": {"done": True}}],
        # (c) k and w ask the owner, then spend their bound; f dies
        "k": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which day?"}}}, {"sleep": 0.1, "body": {"done": "x"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which week?"}}}, {"sleep": 0.1, "body": {"done": "y"}}],
        "f": [{"sleep": 0.1, "body": "crash"}],
        # (d) e dies on T1, then resolves T2 and T3
        "e": [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": {"done": "two"}},
              {"sleep": 0.1, "body": {"done": "three"}}],
        # (e) s resolves each season's task
        "s": [{"sleep": 0.1, "body": {"done": "one"}}, {"sleep": 0.1, "body": {"done": "again"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    gate = bench.temp() / "gate-open"
    gated = T.gated(h, gate, ("r1", "r2"))

    def said(name: str) -> tuple:
        """-> (state, waiting_on) of the team's object, when its line on the every-team face says the same."""
        obj = h.face(name)
        line = next((one for one in h.face() if one.get("team") == name), {})
        if (obj.get("state"), obj.get("waiting_on")) != (line.get("state"), line.get("waiting_on")):
            return ("object and line differ", obj.get("state"), line.get("state"))
        return obj.get("state"), tuple(obj.get("waiting_on") or ())

    def on_t1(obj: dict):
        return next((t.get("running") for t in obj.get("tasks") or [] if t.get("id") == "T1"), None)

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("flow", "---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\n"
                      "root: m\nschedule: off\n---\nFlow.\n")
    h.declare("dear", "---\nagents: |\n  k agents/k\nroot: k\nbudget-launches: 1\nschedule: off\n---\nOne wake-up.\n")
    h.declare("count", "---\nagents: |\n  w agents/w\nroot: w\nlaunches: 1\nschedule: off\n---\nOne wake-up.\n")
    h.declare("fail", "---\nagents: |\n  f agents/f\nroot: f\nretries: 0\nschedule: off\n---\nIt dies.\n")
    h.declare("inbox", "---\nagents: |\n  e agents/e\nroot: e\nretries: 0\nschedule: off\n---\nAnswer the owner.\n")
    h.declare("twice", "---\nagents: |\n  s agents/s\n  t agents/t\nreports: |\n  t -> s\nroot: s\nschedule: off\n"
                       "---\nTwo seasons.\n")
    seen = {"never": said("flow")}
    team = ["--instance", str(h.house), "team"]
    flow, dear, count, fail, inbox, first = race(h.engine, [
        [*team, "start", "flow", "--message", "review PR 13", *gated, "--no-tick"],
        [*team, "start", "dear", "--message", "cut the branch", *h.harnessed],
        [*team, "start", "count", "--message", "date the release", *h.harnessed],
        [*team, "start", "fail", "--message", "do it", *h.harnessed],
        [*team, "start", "inbox", "--message", "price the DDR4", *h.harnessed],
        [*team, "start", "twice", "--message", "season one", *h.harnessed]], cwd=h.ws, env=h.env)
    seen["due"] = said("flow")
    ticked = h.call("team", "tick", "flow")

    # --- (a)(b) flow: r1 and r2 held at the gate, the faces read, the gate opened ---------------------------------
    gated_both = h.settled("flow", lambda found: {one.get("agent") for one in by_kind(found, "wake-launched")}
                           >= {"r1", "r2"}, 60)
    running, working = [], ("not caught",)
    for _ in range(300):                                  # bounded: the wake-ups stand under way until the gate opens
        obj = h.face("flow")
        line = next((one for one in h.face() if one.get("team") == "flow"), {})
        running = on_t1(obj) or []
        working = (obj.get("state"), line.get("state"), tuple(obj.get("waiting_on") or ()),
                   tuple(line.get("waiting_on") or ()))
        if (sorted(one.get("member") for one in running) == ["r1", "r2"] and all(one.get("run") for one in running)
                and working == ("working", "working", (), ())):
            break
    seen["working"] = ("working", ()) if working == ("working", "working", (), ()) else working
    gate.write_text("open", encoding="utf-8")

    # --- (c)(d) the dead roots reaped by a tick at hand: a dead wake-up fires no on-end -----------------------------
    guards = {}
    h.tick_until("fail", lambda found: bool(by_kind(found, "wake-failed", agent="f", final=True)))
    guards["blocked"] = said("fail")
    h.tick_until("inbox", lambda found: bool(by_kind(found, "post", verb="notice")) and all_ended(found))
    raised = bool(by_kind(h.events("inbox"), "post", verb="notice"))
    fell = T.finals_of(h.events("inbox"), "e")
    later = T.local_after(fell[0]["at"], 6).isoformat(timespec="seconds") if fell else None

    # --- every owner's gesture together: the answers to the asks, the second season, e's two tasks ------------------
    asked = h.settled("flow", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found)
                      and T.terminal_of(found, "r2") < 10 ** 9, 60)
    seen["members"] = said("flow")
    t1_ended = on_t1(h.face("flow"))
    h.settled("dear", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    h.settled("count", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    one_done = h.settled("twice", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    once = h.face("twice")
    journal = h.journal_of("twice")
    rows = [json.loads(one) for one in journal.read_text(encoding="utf-8").splitlines() if one.strip()]
    for one in rows:                                    # what an older start kept
        if one.get("kind") == "team-started":
            one["launch"]["max_budget_usd"] = 5.0
    journal.write_text("".join(json.dumps(one) + "\n" for one in rows), encoding="utf-8")

    def reply(name: str) -> list[str]:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        return [*team, "post", name, "--task", "T1", "--reply", str(ask), "--message", "main"]

    replied, replied_dear, replied_count, second, posted_t2, posted_t3 = race(h.engine, [
        reply("flow"), reply("dear"), reply("count"),
        [*team, "start", "twice", "--message", "season two", *h.harnessed],
        [*team, "post", "inbox", "--message", "price the DDR5", "--no-tick"],
        [*team, "post", "inbox", "--message", "price the HBM", "--no-tick"]], cwd=h.ws, env=h.env)

    # --- (c) the guards of the bounds ----------------------------------------------------------------------
    h.settled("dear", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), 30)
    guards["budget"] = said("dear")
    h.settled("count", lambda found: bool(by_kind(found, "launches-spent")) and all_ended(found), 30)
    guards["launches"] = said("count")

    # --- (d) the badge: e resolves two tasks past its interval ---------------------------------------------------
    h.tick_until("inbox", lambda found: len(by_kind(found, "done")) >= 2 and all_ended(found), timeout=60, now=later)

    def boxed() -> dict:
        """-> what `team inbox inbox --json` counts: questions, notices, tasks resolved, and whom the notices are about."""
        found = [json.loads(one) for one in h.call("team", "inbox", "inbox", "--json").stdout.splitlines()
                 if one.strip().startswith("{")]
        box = next((one for one in found if one.get("team") == "inbox"), {})
        return {"asks": len(box.get("questions") or []), "notices": len(box.get("notices") or []),
                "done": len(box.get("done") or []), "about": [one.get("about") for one in box.get("notices") or []]}

    counted = next((one for one in h.face() if one.get("team") == "inbox"), {})
    box_before = boxed()
    seen_box = h.call("team", "inbox", "inbox", "--seen")
    after = next((one for one in h.face() if one.get("team") == "inbox"), {})
    box_after = boxed()

    # --- (e) the season and the launch: the second start on a journal that kept a per-wake cap -------------------
    two_done = h.settled("twice", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), 60)
    twice = h.face("twice")

    # --- the end of flow ---------------------------------------------------------------------------------------
    h.settled("flow", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    seen["idle"] = said("flow")

    # --- (a) the state and its guards ---------------------------------------------------------------------
    wanted = {"never": ("never", ()), "due": ("waiting", ("due",)), "working": ("working", ()),
              "members": ("waiting", ("members", "owner")), "idle": ("idle", ())}
    if (flow.returncode, ticked.returncode, replied.returncode) == (0, 0, 0) and seen == wanted:
        held("(a) the state and its guards", "never, waiting [due], working, waiting [members, owner], idle -- "
             "the object and the line alike")
    else:
        failures.append(f"  ✗ (a) the state              rc={flow.returncode}/{ticked.returncode}/{replied.returncode} "
                        + " ".join(f"{key}={seen.get(key)}" for key in wanted if seen.get(key) != wanted[key])
                        + f" {flow.stderr.strip()[-160:]!r}")

    # --- (b) the wake-ups of a task -----------------------------------------------------------------------
    if (gated_both and asked and sorted(one.get("member") for one in running) == ["r1", "r2"]
            and all(one.get("tag") and one.get("run") and one.get("since") and "allowance" in one for one in running)
            and t1_ended == []):
        held("(b) the wake-ups of a task", f"T1 running {[(one['member'], one['run']) for one in running]}, then []")
    else:
        failures.append(f"  ✗ (b) running                gated={gated_both} asked={asked} running={running} "
                        f"after={t1_ended}")

    # --- (c) the guards of the bounds and of a failure -----------------------------------------------------
    wanted = {"budget": ("waiting", ("budget",)), "launches": ("waiting", ("launches",)),
              "blocked": ("waiting", ("owner", "suspected"))}
    if (dear.returncode, count.returncode, fail.returncode, replied_dear.returncode, replied_count.returncode) == \
            (0, 0, 0, 0, 0) and guards == wanted:
        held("(c) the guards of the bounds and of a failure", "[budget], [launches], [owner, suspected] -- "
             "the object and the line alike")
    else:
        failures.append(f"  ✗ (c) the guards             rc={dear.returncode}/{count.returncode}/{fail.returncode}/"
                        f"{replied_dear.returncode}/{replied_count.returncode} "
                        + " ".join(f"{key}={guards.get(key)}" for key in wanted if guards.get(key) != wanted[key]))

    # --- (d) the badge counts the inbox -----------------------------------------------------------------
    badge = {key: counted.get(key) for key in ("asks", "notices", "done")}
    badge_after = {key: after.get(key) for key in ("asks", "notices", "done")}
    if (inbox.returncode == posted_t2.returncode == posted_t3.returncode == 0 and raised
            and badge == {"asks": 0, "notices": 1, "done": 2}
            and box_before == {**badge, "about": ["e"]} and seen_box.returncode == 0
            and badge_after == {"asks": 0, "notices": 1, "done": 0} and box_after == {**badge_after, "about": ["e"]}):
        held("(d) the badge counts the inbox", "a notice and two tasks resolved: asks 0, notices 1, done 2, as inbox "
             "--json counts them; seen, done 0, the notice about e kept")
    else:
        failures.append(f"  ✗ (d) the badge              rc={inbox.returncode}/{posted_t2.returncode}/{posted_t3.returncode}/"
                        f"{seen_box.returncode} raised={raised} "
                        f"line={badge} box={box_before} after={badge_after} box_after={box_after}")

    # --- (e) the season and the launch --------------------------------------------------------------------
    provider = h.harnessed[h.harnessed.index("--provider") + 1] if "--provider" in h.harnessed else None
    launch = twice.get("launch") or {}
    members = [one.get("launch") for one in twice.get("members") or []]
    if (first.returncode == 0 and one_done and (once.get("season") or {}).get("n") == 1
            and second.returncode == 0 and two_done and (twice.get("season") or {}).get("n") == 2
            and (twice.get("season") or {}).get("at") == (twice.get("started") or {}).get("at")
            and set(launch) == LAUNCH and launch.get("provider") == provider and "max_budget_usd" not in launch
            and members == [launch, launch]):
        held("(e) the season and the launch", f"season 1 then 2; launch {launch}, no max_budget_usd; both members "
             "carry it")
    else:
        failures.append(f"  ✗ (e) the season and launch  rc={first.returncode}/{second.returncode} done={one_done}/"
                        f"{two_done} once={once.get('season')} twice={twice.get('season')} launch={launch} "
                        f"members={members} {second.stderr.strip()[-200:]!r}")
    return 0
