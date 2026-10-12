"""Scenario `team-budget` -- 2 case(s) (batch le-budget-de-l-equipe, 2026-10-11: row 75 of the study § 18, team
0.22.0; realigned by la-part-calculee, team 0.29.0): a wake-up's share of the team's budget. Since agent 0.19.0
`--max-budget-usd` caps a RUN; the tick gives each wake-up an ALLOWANCE -- its part of the team's rest -- and hands
`agent start` the member's run cap: what the run spent plus the allowance; no cap per wake-up exists. Each case
names the invariant of `team-sim-reframe.py` it replays; the parts are `team-budget-parallel`'s, the rest shared
`team-budget-shared`'s, the budget raised `team-budget-raised`'s and `team-budget-raised-wakes`'s.
- (a) the allowance composed (I10r): `team start --max-budget-usd 5` refuses `flag-retired`, nothing written;
  `budget: 1`, one member -- u's first wake-up costs 0.4 and asks the owner: its intent carries 1.0 and its
  message's policy caps the run at 1.0; the reply wakes u again in its run: allowance 0.6, the run's cap 0.4 + 0.6;
  on a team without `budget:` no allowance and no cap
- (b) a journal written before (KPC31): a `team-started` whose `launch` kept `max_budget_usd` replays without
  refusal, the cap is never passed to `agent start`, and `status` says it once
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "u": [{"sleep": 0.1, "cost": 0.4, "body": {"ask": {"to": "house", "text": "which branch?"}}},
              {"sleep": 0.1, "body": {"done": "merged"}}],
        "f": [{"sleep": 0.1, "cost": 0.4, "body": {"ask": {"to": "house", "text": "which tag?"}}},
              {"sleep": 0.1, "body": {"done": "tagged"}}],
        "o": [{"sleep": 0.1, "body": {"done": "old"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def caps(tags: list[str]) -> list:
        """-> the run cap each wake-up's message carried to agent start, read at the house's messages.jsonl."""
        policies = {one.get("tag"): (one.get("policy") or {}) for one in T.lines(h.records / "messages.jsonl")}
        return [policies.get(tag, {}).get("max_budget_usd") for tag in tags]

    def reply(name: str) -> subprocess.CompletedProcess:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        return h.call("team", "post", name, "--task", "T1", "--reply", str(ask), "--message", "main")

    # --- (a) the allowance composed: the part of the rest, on the run spent -- I10r ---------------------------
    h.declare("share", "---\nagents: |\n  u agents/u\nroot: u\nbudget: 1\nschedule: off\n---\nSpend within.\n")
    h.declare("free", "---\nagents: |\n  f agents/f\nroot: f\nschedule: off\n---\nNo budget.\n")
    retired = h.call("team", "start", "share", "--message", "merge PR 9", *h.harnessed, "--max-budget-usd", "5")
    unwritten = not h.journal_of("share").exists()
    started = h.call("team", "start", "share", "--message", "merge PR 9", *h.harnessed)
    asked = h.settled("share", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    replied = reply("share")
    done = h.settled("share", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    intents = by_kind(h.events("share"), "wake-intent")
    free = h.call("team", "start", "free", "--message", "tag v1", *h.harnessed)
    asked_f = h.settled("free", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    replied_f = reply("free")
    done_f = h.settled("free", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    intents_f = by_kind(h.events("free"), "wake-intent")
    seen = (caps([one["tag"] for one in intents]), [one.get("allowance") for one in intents],
            caps([one["tag"] for one in intents_f]), [one.get("allowance") for one in intents_f])
    if (retired.returncode == 2 and "flag-retired" in retired.stderr and "budget:" in retired.stderr and unwritten
            and started.returncode == 0 and asked and replied.returncode == 0 and done and free.returncode == 0
            and asked_f and replied_f.returncode == 0 and done_f
            and seen == ([1.0, 1.0], [1.0, 0.6], [None, None], [None, None])):
        held("(a) the allowance composed", "--max-budget-usd refuses flag-retired, nothing written; budget 1: u's "
             "intents carry 1.0 then 0.6, its run capped at 1.0 both times (0.4 spent + 0.6); without budget: no "
             "allowance, no cap -- I10r")
    else:
        failures.append(f"  ✗ (a) the allowance composed rc={retired.returncode}/{started.returncode}/{replied.returncode}/"
                        f"{free.returncode} unwritten={unwritten} asked={asked}/{asked_f} done={done}/{done_f} "
                        f"caps, allowances={seen} {retired.stderr.strip()[-200:]!r}")

    # --- (b) a journal written before: its per-wake cap never passed -- KPC31 ---------------------------------
    h.declare("old", "---\nagents: |\n  o agents/o\nroot: o\nschedule: off\n---\nAn older start.\n")
    opened = h.call("team", "start", "old", "--message", "date v0", *h.harnessed, "--no-tick")
    journal = h.journal_of("old")
    rows = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    for one in rows:                                    # what a start before team 0.29.0 kept
        if one.get("kind") == "team-started":
            one["launch"]["max_budget_usd"] = 5.0
    journal.write_text("".join(json.dumps(one) + "\n" for one in rows), encoding="utf-8")
    ticked = h.call("team", "tick", "old")
    done_o = h.settled("old", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    capped = caps([one["tag"] for one in by_kind(h.events("old"), "wake-intent")])
    said = h.status_line("old", "launch · ")
    if opened.returncode == 0 and ticked.returncode == 0 and done_o and capped == [None] and "never passed" in said:
        held("(b) a journal written before", f"launch.max_budget_usd 5 kept: replayed, T1 done, no cap passed "
             f"({capped}); status `{said}` -- KPC31")
    else:
        failures.append(f"  ✗ (b) a journal before       rc={opened.returncode}/{ticked.returncode} done={done_o} "
                        f"caps={capped} status={said!r} {ticked.stderr.strip()[-200:]!r}")
    return 0
