"""Scenario `team-status-rhythm` -- 1 case(s) (batch le-status-des-equipes of plan ui, 2026-10-10: team 0.20.0;
cut from `team-status-json` by les-faces-de-l-equipe, rule 10): the ceremonies of `team status <name> --json` --
their next ring, whether the next tick rings them, their last ring and its progress. A team `crew` (m root, r1 r2
reporting to m, the mandator pm; `daily every weekday 09:30 with r1 r2 -> m any 1`, `retro after daily with r1 ->
m`), the clock frozen by `PP_NOW` on Thursday 2026-10-01; T1 played first, as `team-status-json` plays it.
- the rhythm: the daily's next ring 2026-10-01T09:30 at 09:10, due at 09:31 before the tick, then
  2026-10-02T09:30 once rung, its last ring and the participants' progress; the retro `null` and
  not due until the daily resolves -- then due, on a copy of the journal cut at that resolution; on
  that copy, Friday 08:00 says 2026-10-02T09:30 and, the Friday rung, Monday 2026-10-05T09:30; a ring
  at hand says `manual-<id>` and `by`, and moves no date
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")

CREW = ("---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\nroot: m\n"
        "principals: |\n  pm\nceremonies: |\n  daily every weekday 09:30 with r1 r2 -> m any 1\n"
        "  retro after daily with r1 -> m\n---\nKeep the beat.\n")
KEYS = {"team", "owner", "principals", "started", "changed", "limits", "schedule", "cost", "budget_spent", "budget",
        "wakes", "last", "tasks", "members", "ceremonies", "owner_inbox", "waiting"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 0.1, "body": {"do": ["r1"]}}, {"sleep": 0.1, "body": {"done": "ok"}},
              {"sleep": 0.1, "body": {"done": "standup"}}, {"sleep": 0.1, "body": {"done": "retro"}}],
        "r1": [{"sleep": 0.1, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}},
               {"sleep": 0.1, "body": {"done": True}}],
        "r2": [{"sleep": 0.6, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def face(name: str | None = None, when: str = "2026-10-01T09:10") -> tuple:
        args = ("team", "status", *([name] if name else []), "--json")
        played = cli(h.engine, "--instance", str(h.house), *args, cwd=h.ws, env={**h.env, "PP_NOW": when})
        try:
            found = [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            found = []
        return played, found

    def ceremony(found: list, name: str) -> dict:
        return next((one for one in (found[0] if found else {}).get("ceremonies") or [] if one.get("name") == name), {})

    def member(found: list, name: str) -> dict:
        return next((one for one in (found[0] if found else {}).get("members") or [] if one.get("member") == name), {})

    h.declare("crew", CREW)
    h.declare("idle", "---\nagents: |\n  s s\nroot: s\n---\nNothing yet.\n")

    # --- T1, as team-status-json plays it -----------------------------------------------------------
    h.call("team", "start", "crew", "--message", "ship it", *h.harnessed, "--no-tick", now="09:10")
    first, first_obj = face("crew")
    h.call("team", "tick", "crew", now="09:15")
    h.settled("crew", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)

    # --- the rhythm --------------------------------------------------------------------------------
    daily_0910 = ceremony(first_obj, "daily")
    retro_0910 = ceremony(first_obj, "retro")
    _, before_ring = face("crew", "2026-10-01T09:31")
    rung = h.call("team", "tick", "crew", now="09:31")
    _, rung_obj = face("crew", "2026-10-01T09:31")
    daily_rung = ceremony(rung_obj, "daily")
    resolved = h.settled("crew", lambda found: len(by_kind(found, "done")) >= 3 and all_ended(found), 60)
    _, settled_obj = face("crew", "2026-10-01T09:40")
    daily_done, retro_done = ceremony(settled_obj, "daily"), ceremony(settled_obj, "retro")
    found = h.events("crew")
    daily_task = next((e["task"] for e in found if e.get("kind") == "task" and e.get("ceremony") == "daily"), None)
    cut = next((e["id"] for e in by_kind(found, "done", task=daily_task)), 0)
    h.declare("frozen", CREW)                          # the bench's hand on a disposable journal: crew's, cut
    h.journal_of("frozen").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("frozen").write_text("".join(json.dumps(e) + "\n" for e in found if e["id"] <= cut), encoding="utf-8")
    _, frozen_obj = face("frozen", "2026-10-01T09:40")
    _, friday_obj = face("frozen", "2026-10-02T08:00")
    with h.journal_of("frozen").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": "2026-10-02T07:31:00+00:00", "id": cut + 1, "kind": "ceremony-due",
                                 "team": "frozen", "ceremony": "daily", "period": "2026-10-02"}) + "\n")
    _, monday_obj = face("frozen", "2026-10-02T10:00")
    ring = h.call("team", "ring", "crew", "daily", "--as", "pm", "--no-tick", now="09:45")
    _, manual_obj = face("crew", "2026-10-01T09:45")
    daily_manual = ceremony(manual_obj, "daily")
    manual_id = next((e["id"] for e in by_kind(h.events("crew"), "ceremony-due") if e.get("by") == "pm"), -1)
    if (daily_0910.get("next_due") == "2026-10-01T09:30" and daily_0910.get("due") is False
            and daily_0910.get("quorum") == 1 and daily_0910.get("when") == {"kind": "weekday", "at": "09:30"}
            and daily_0910.get("last") is None and daily_0910.get("progress") == []
            and retro_0910.get("next_due") is None and retro_0910.get("due") is False
            and retro_0910.get("after") == "daily"
            and ceremony(before_ring, "daily").get("due") is True
            and ceremony(before_ring, "daily").get("next_due") == "2026-10-01T09:30"
            and rung.returncode == 0 and daily_rung.get("next_due") == "2026-10-02T09:30" and daily_rung.get("due") is False
            and (daily_rung.get("last") or {}).get("period") == "2026-10-01"
            and [p.get("member") for p in daily_rung.get("progress") or []] == ["r1", "r2"]
            and resolved and (daily_done.get("last") or {}).get("state") == "resolved"
            and any(p.get("answered") for p in daily_done.get("progress") or [])
            and (retro_done.get("last") or {}).get("period") == "2026-10-01"
            and ceremony(frozen_obj, "retro").get("due") is True and ceremony(frozen_obj, "retro").get("last") is None
            and ceremony(friday_obj, "daily").get("next_due") == "2026-10-02T09:30"
            and ceremony(monday_obj, "daily").get("next_due") == "2026-10-05T09:30"
            and ring.returncode == 0 and (daily_manual.get("last") or {}).get("period") == f"manual-{manual_id}"
            and (daily_manual.get("last") or {}).get("by") == "pm"
            and (daily_manual.get("last") or {}).get("state") == "open"
            and daily_manual.get("next_due") == "2026-10-02T09:30"):
        held("the rhythm", "daily 09:30 at 09:10, due at 09:31, then 2026-10-02T09:30 rung; the retro null, due once "
             f"the daily resolved (cut #{cut}); Friday 09:30, Monday 09:30 after Friday's ring; manual-{manual_id} by pm "
             "moves no date")
    else:
        failures.append(f"  ✗ the rhythm                  0910={daily_0910} retro={retro_0910} "
                        f"before={ceremony(before_ring, 'daily')} rung={daily_rung} resolved={resolved} "
                        f"done={daily_done} retro_done={retro_done} frozen={ceremony(frozen_obj, 'retro')} "
                        f"fri={ceremony(friday_obj, 'daily').get('next_due')} "
                        f"mon={ceremony(monday_obj, 'daily').get('next_due')} ring={ring.returncode} "
                        f"manual={daily_manual} {ring.stderr[-200:]!r}")

    return 0
