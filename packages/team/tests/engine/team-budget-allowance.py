"""Scenario `team-budget-allowance` -- 6 case(s): a wake-up's ALLOWANCE -- its part of the team's rest,
min((budget - the cost kept) / k, the rest no wake-up under way holds), k the wake-ups that may play together,
min(`parallel`, the members) -- and the run cap `agent start` gets: what the run spent plus the allowance; no cap
per wake-up exists; and the parallel bound of the tick. Six teams run side by side in one house, each under its
own names; each case waits for its team, then reads its journal.
- (a) the allowance composed (I10r): `team start --max-budget-usd 5` refuses `flag-retired`, nothing written;
  `budget: 1`, one member -- u's first wake-up costs 0.4 and asks the owner: its intent carries 1.0 and its
  message's policy caps the run at 1.0; the reply wakes u again in its run: allowance 0.6, the run's cap 0.4 + 0.6;
  on a team without `budget:` no allowance and no cap
- (b) a journal written before: a `team-started` whose `launch` keeps `max_budget_usd` replays without
  refusal, the cap is never passed to `agent start`, the face's launch never carries it, and the status gives it
  one `launch` line
- (a) the members due together launch together (I10p, I10r): `budget: 1`, `parallel: 2`, three members; on T1 l
  delegates to r1 and r2 -- two intents of 0.5 each, no `deferred`, both wake-ups under way at once; every intent's
  allowance is its part
- (b) the rest shared (I10r, I10p): on T2 of the same team, the 0.4 spent by T1 kept, l delegates to r1 and r2
  again -- launched together, 0.3 each (the rest 0.6 over k = 2), neither `deferred`; at every intent the cost
  kept plus the allowances under way stays within the budget
- (b) k without `parallel:` (I10r): three members, no `parallel:` -- k = 3; a1 ends at 0.2 while a2 plays, and every
  intent's part is min((1 - the cost kept) / 3, the rest)
- `parallel: 1` holds: p delegates to p1 p2 p3, the journal read in order never shows two intents without an end,
  `deferred` is written for the agents held back, the team ends
"""
from __future__ import annotations

import json
import re
import subprocess

from tests.harness import support

T = support(__file__, "team")

REFUSAL = re.compile(r"^pp-team: ([a-z][a-z-]*)", re.M)


def within(found: list[dict], budget: float) -> bool:
    """-> whether, at every intent, the cost kept plus the allowances of the intents without an end (this one
    included) stays within the budget -- I10r replayed on the journal."""
    cost, open_ = 0.0, {}
    for one in found:
        if one["kind"] in ("wake-ended", "wake-failed"):
            cost += float(one.get("cost") or 0)
        if one["kind"] in ("wake-ended", "wake-failed", "wake-killed"):
            open_.pop(one.get("tag"), None)
        if one["kind"] == "wake-intent":
            open_[one["tag"]] = float(one.get("allowance") or 0)
            if cost + sum(open_.values()) > budget + 1e-9:
                return False
    return True


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (a) the allowance composed: u spends 0.4 then asks; f the same without budget
        "u": [{"sleep": 0.1, "cost": 0.4, "body": {"ask": {"to": "house", "text": "which branch?"}}},
              {"sleep": 0.1, "body": {"done": "merged"}}],
        "f": [{"sleep": 0.1, "cost": 0.4, "body": {"ask": {"to": "house", "text": "which tag?"}}},
              {"sleep": 0.1, "body": {"done": "tagged"}}],
        # (b) a journal written before
        "o": [{"sleep": 0.1, "body": {"done": "old"}}],
        # the parts under parallel 2 (T1), then the rest shared (T2): T1's reviews spend 0.4 together
        "l": {"T1": [{"sleep": 0.1, "cost": 0, "body": {"do": ["r1", "r2"]}},
                     {"sleep": 0.1, "cost": 0, "body": {"done": "both"}}],
              "T2": [{"sleep": 0.1, "cost": 0, "body": {"do": ["r1", "r2"]}},
                     {"sleep": 0.1, "cost": 0, "body": {"done": "both again"}}]},
        "r1": {"T1": [{"sleep": 1.5, "cost": 0.2, "body": {"done": True}}],
               "T2": [{"sleep": 1.5, "cost": 0, "body": {"done": True}}]},
        "r2": {"T1": [{"sleep": 1.5, "cost": 0.2, "body": {"done": True}}],
               "T2": [{"sleep": 0.1, "cost": 0, "body": {"done": True}}]},
        # (b) k without parallel: -- three members
        "a": [{"sleep": 0.1, "cost": 0, "body": {"do": ["a1", "a2"]}}, {"sleep": 0.1, "cost": 0, "body": {"done": "both"}}],
        "a1": [{"sleep": 0.2, "cost": 0.2, "body": {"done": True}}],
        "a2": [{"sleep": 2.0, "cost": 0.1, "body": {"done": True}}],
        # parallel: 1 -- one at a time
        "p": [{"sleep": 0.2, "body": {"do": ["p1", "p2", "p3"]}}, {"sleep": 0.2, "body": {"done": "all three"}}],
        "p1": [{"sleep": 0.3, "body": {"done": True}}],
        "p2": [{"sleep": 0.3, "body": {"done": True}}],
        "p3": [{"sleep": 0.3, "body": {"done": True}}]})
    by_kind, all_ended, parts_held, peak = T.by_kind, T.all_ended, T.parts_held, T.peak
    done_on = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)
    asked_ended = lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found)

    def caps(tags: list[str]) -> list:
        """-> the run cap each wake-up's message carried to agent start, read at the house's messages.jsonl."""
        policies = {one.get("tag"): (one.get("policy") or {}) for one in T.lines(h.records / "messages.jsonl")}
        return [policies.get(tag, {}).get("max_budget_usd") for tag in tags]

    def reply(name: str) -> subprocess.CompletedProcess:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        return h.call("team", "post", name, "--task", "T1", "--reply", str(ask), "--message", "main")

    def code(played: subprocess.CompletedProcess) -> str:
        found = REFUSAL.search(played.stderr)
        return found.group(1) if found else ""

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("share", "---\nagents: |\n  u agents/u\nroot: u\nbudget: 1\nschedule: off\n---\nSpend within.\n")
    h.declare("free", "---\nagents: |\n  f agents/f\nroot: f\nschedule: off\n---\nNo budget.\n")
    h.declare("old", "---\nagents: |\n  o agents/o\nroot: o\nschedule: off\n---\nAn older start.\n")
    h.declare("pair", "---\nagents: |\n  l agents/l\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> l\n"
                      "root: l\nparallel: 2\nbudget: 1\nschedule: off\n---\nShare the rest.\n")
    h.declare("trio", "---\nagents: |\n  a agents/a\n  a1 agents/a1\n  a2 agents/a2\nreports: |\n  a1 a2 -> a\n"
                      "root: a\nbudget: 1\nschedule: off\n---\nThree parts.\n")
    h.declare("limited", "---\nagents: |\n  p p\n  p1 p1\n  p2 p2\n  p3 p3\n"
                         "reports: |\n  p1 p2 p3 -> p\nroot: p\nparallel: 1\n---\nOne at a time.\n")
    retired = h.call("team", "start", "share", "--message", "merge PR 9", *h.harnessed, "--max-budget-usd", "5")
    unwritten = not h.journal_of("share").exists()
    started = h.call("team", "start", "share", "--message", "merge PR 9", *h.harnessed)
    free = h.call("team", "start", "free", "--message", "tag v1", *h.harnessed)
    opened = h.call("team", "start", "old", "--message", "date v0", *h.harnessed, "--no-tick")
    journal = h.journal_of("old")
    rows = T.lines(journal)
    for one in rows:                                    # what an older start kept: a per-wake cap
        if one.get("kind") == "team-started":
            one["launch"]["max_budget_usd"] = 5.0
    journal.write_text("".join(json.dumps(one) + "\n" for one in rows), encoding="utf-8")
    ticked = h.call("team", "tick", "old")
    paired = h.call("team", "start", "pair", "--message", "review PR 11", *h.harnessed)
    trio = h.call("team", "start", "trio", "--message", "review PR 12", *h.harnessed)
    limited = h.call("team", "start", "limited", "--message", "review in turn", *h.harnessed)

    # --- the longest chain first: pair's T1 ends, its T2 opens on the rest -----------------------------------
    done_t1 = h.settled("pair", done_on("T1"), 60)
    second = h.call("team", "post", "pair", "--message", "review PR 10")

    # --- (a) the allowance composed: the part of the rest, on the run spent -- I10r ---------------------------
    asked = h.settled("share", asked_ended, 60)
    replied = reply("share")
    asked_f = h.settled("free", asked_ended, 60)
    replied_f = reply("free")
    done = h.settled("share", done_on("T1"), 60)
    done_f = h.settled("free", done_on("T1"), 60)
    intents = by_kind(h.events("share"), "wake-intent")
    intents_f = by_kind(h.events("free"), "wake-intent")
    seen = (caps([one["tag"] for one in intents]), [one.get("allowance") for one in intents],
            caps([one["tag"] for one in intents_f]), [one.get("allowance") for one in intents_f])
    if (retired.returncode == 2 and code(retired) == "flag-retired" and unwritten
            and started.returncode == 0 and asked and replied.returncode == 0 and done and free.returncode == 0
            and asked_f and replied_f.returncode == 0 and done_f
            and seen == ([1.0, 1.0], [1.0, 0.6], [None, None], [None, None])):
        held("(a) the allowance composed", "--max-budget-usd refuses flag-retired, nothing written; budget 1: u's "
             "intents carry 1.0 then 0.6, its run capped at 1.0 both times (0.4 spent + 0.6); without budget: no "
             "allowance, no cap -- I10r")
    else:
        failures.append(f"  ✗ (a) the allowance composed rc={retired.returncode}/{started.returncode}/{replied.returncode}/"
                        f"{free.returncode} code={code(retired)!r} unwritten={unwritten} asked={asked}/{asked_f} "
                        f"done={done}/{done_f} caps, allowances={seen} {retired.stderr.strip()[-200:]!r}")

    # --- (b) a journal written before: its per-wake cap never passed -----------------------------------
    done_o = h.settled("old", done_on("T1"), 60)
    capped = caps([one["tag"] for one in by_kind(h.events("old"), "wake-intent")])
    face = h.face("old")
    launch_lines = [line for line in h.call("team", "status", "old").stdout.splitlines() if line.startswith("launch · ")]
    free_lines = [line for line in h.call("team", "status", "free").stdout.splitlines() if line.startswith("launch · ")]
    if (opened.returncode == 0 and ticked.returncode == 0 and done_o and capped == [None]
            and face.get("team") == "old" and "max_budget_usd" not in (face.get("launch") or {"max_budget_usd": "?"})
            and face.get("budget") is None and len(launch_lines) == 1 and free_lines == []):
        held("(b) a journal written before", f"launch.max_budget_usd 5 kept: replayed, T1 done, no cap passed "
             f"({capped}); the face's launch carries no cap, the status gives it one launch line")
    else:
        failures.append(f"  ✗ (b) a journal before       rc={opened.returncode}/{ticked.returncode} done={done_o} "
                        f"caps={capped} face.launch={face.get('launch')} budget={face.get('budget')} "
                        f"launch lines={len(launch_lines)}/{len(free_lines)} {ticked.stderr.strip()[-200:]!r}")

    # --- (a) the members due together launch together -- I10p, I10r ------------------------------------------
    done_t2 = h.settled("pair", done_on("T2"), 60)
    found = h.events("pair")
    parts = {one["agent"]: one.get("allowance") for one in by_kind(found, "wake-intent", task="T1") if one["agent"] != "l"}
    t1_end = next((one["id"] for one in by_kind(found, "done", task="T1")), 10 ** 9)
    peak_t1 = peak([one for one in found if one["id"] <= t1_end])
    if (paired.returncode == 0 and done_t1 and parts == {"r1": 0.5, "r2": 0.5} and not by_kind(found, "deferred")
            and peak_t1 == 2 and parts_held(found, 1.0, 2)):
        held("(a) the members due together launch together", "budget 1, parallel 2: on T1 r1 and r2 get 0.5 each, "
             "no deferred, both under way at once -- I10p, I10r")
    else:
        failures.append(f"  ✗ (a) together               rc={paired.returncode} done={done_t1} parts={parts} "
                        f"deferred={by_kind(found, 'deferred')} peak={peak_t1} held={parts_held(found, 1.0, 2)}")

    # --- (b) the rest shared: r1 and r2 each their part, launched together -- I10r, I10p ---------------------
    spent_t1 = round(sum(float(one.get("cost") or 0) for one in found if one.get("kind") == "wake-ended"
                         and one["id"] < t1_end), 6)
    on_t2 = by_kind(found, "wake-intent", task="T2")
    r1 = next((one for one in on_t2 if one["agent"] == "r1"), {})
    r2 = next((one for one in on_t2 if one["agent"] == "r2"), {})
    r1_end = next((one["id"] for one in found if one["kind"] == "wake-ended" and one.get("tag") == r1.get("tag")), -1)
    if (second.returncode == 0 and done_t2 and spent_t1 == 0.4 and r1.get("allowance") == 0.3
            and r2.get("allowance") == 0.3 and not by_kind(found, "deferred") and r2.get("id", 10 ** 9) < r1_end
            and within(found, 1.0)):
        held("(b) the rest shared", "T1 kept 0.4: on T2 r1 and r2 launched together, 0.3 each, neither deferred; "
             "cost + allowances within 1 at every intent -- I10r, I10p")
    else:
        failures.append(f"  ✗ (b) the rest shared        rc={second.returncode} done={done_t2} spent={spent_t1} "
                        f"r1={r1.get('allowance')} r2={r2.get('allowance')} deferred={by_kind(found, 'deferred')} "
                        f"r1_end={r1_end} r2_at={r2.get('id')} within={within(found, 1.0)}")

    # --- (b) k without parallel: -- the members, three -- I10r ---------------------------------------------
    done_b = h.settled("trio", done_on("T1"), 60)
    found = h.events("trio")
    parts = [(one["agent"], one.get("allowance")) for one in by_kind(found, "wake-intent")]
    if (trio.returncode == 0 and done_b and parts[:3] == [("a", 0.333333), ("a1", 0.333333), ("a2", 0.333333)]
            and len(parts) == 4 and parts_held(found, 1.0, 3)):
        held("(b) k without parallel:", f"three members: k 3, parts {parts} -- each min((1 - cost) / 3, the rest) "
             "-- I10r")
    else:
        failures.append(f"  ✗ (b) k without parallel    rc={trio.returncode} done={done_b} parts={parts} "
                        f"held={parts_held(found, 1.0, 3)}")

    # --- parallel: 1 holds: never two intents without an end, the rest deferred ---------------------
    done_l = h.settled("limited", lambda found: any(one.get("kind") == "done" for one in found) and all_ended(found))
    found = h.events("limited")
    deferred = by_kind(found, "deferred")
    started_l = next((one for one in found if one.get("kind") == "team-started"), {})
    if (limited.returncode == 0 and done_l and peak(found) == 1 and len(deferred) >= 2
            and {one.get("agent") for one in deferred} <= {"p1", "p2", "p3"}
            and started_l.get("limits") == {"parallel": 1} and len(by_kind(found, "wake-intent")) == 5):
        held("parallel: 1 holds", f"peak of intents without an end {peak(found)}, {len(deferred)} deferred, "
             "5 wake-ups, done")
    else:
        failures.append(f"  ✗ parallel                    rc={limited.returncode} done={done_l} peak={peak(found)} "
                        f"deferred={[(one.get('agent'), one.get('task')) for one in deferred]} "
                        f"limits={started_l.get('limits')} {limited.stderr[-200:]!r}")
    return 0
