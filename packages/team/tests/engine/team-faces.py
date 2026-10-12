"""Scenario `team-faces` -- 3 case(s) (batch les-faces-de-l-equipe, 2026-10-11: row 81 of the study § 18, team
0.30.0): `team status --json` says what the post would recount -- the line of each team counts what waits for the
owner as the inbox does, and the object says the team's season and the launch its next wake-up gets; the text of
`status` keeps its bytes. The state and its guards are `team-faces-state`'s.
- (a) the badge counts the inbox: e escalates T1 to the owner, then resolves T2 and T3 -- the line says `asks 1`
  (`ask` and `escalate`, as `inbox` says « 1 escalation ») and `done 2`; `team inbox --seen`, then `done 0`
- (b) the season and the launch: a second start says `season {n: 2}`; `launch` says the provider the start was
  given, every key of the face present, and never `max_budget_usd` -- not even the one an older journal kept;
  each member carries the same launch
- (c) the text: `team status` on a journal written by hand, its sha -- the same bytes before and after the batch,
  the sha compared at its Delivery
"""
from __future__ import annotations

import hashlib
import json

from tests.harness import cli, support

T = support(__file__, "team")

LAUNCH = {"harness", "provider", "model", "permissions", "effort", "launches", "packages"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "e": [{"sleep": 0.1, "body": {"escalate": "which market?"}}, {"sleep": 0.1, "body": {"done": "two"}},
              {"sleep": 0.1, "body": {"done": "three"}}],
        "s": [{"sleep": 0.1, "body": {"done": "one"}}, {"sleep": 0.1, "body": {"done": "again"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def line(name: str) -> dict:
        played = cli(h.engine, "--instance", str(h.house), "team", "status", "--json", cwd=h.ws, env=h.env)
        try:
            found = [json.loads(one) for one in played.stdout.splitlines() if one.strip()]
        except ValueError:
            found = []
        return next((one for one in found if one.get("team") == name), {})

    def face(name: str) -> dict:
        played = cli(h.engine, "--instance", str(h.house), "team", "status", name, "--json", cwd=h.ws, env=h.env)
        try:
            return json.loads(played.stdout)
        except ValueError:
            return {}

    # --- (a) the badge counts the inbox -----------------------------------------------------------------
    h.declare("inbox", "---\nagents: |\n  e agents/e\nroot: e\nschedule: off\n---\nAnswer the owner.\n")
    started = h.call("team", "start", "inbox", "--message", "price the DDR4", *h.harnessed)
    raised = h.settled("inbox", lambda found: bool(by_kind(found, "post", verb="escalate")) and all_ended(found), 60)
    for text in ("price the DDR5", "price the HBM"):
        h.call("team", "post", "inbox", "--message", text)
        h.settled("inbox", lambda found: len(by_kind(found, "done")) >= (1 if text.endswith("DDR5") else 2)
                  and all_ended(found), 60)
    counted = line("inbox")
    said = h.call("team", "inbox", "inbox").stdout
    seen = h.call("team", "inbox", "inbox", "--seen")
    after = line("inbox")
    if (started.returncode == 0 and raised and counted.get("asks") == 1 and counted.get("done") == 2
            and "1 escalation" in said and seen.returncode == 0 and after.get("done") == 0 and after.get("asks") == 1):
        held("(a) the badge counts the inbox", f"an escalation and two tasks resolved: asks 1, done 2 -- inbox says "
             f"« 1 escalation »; seen, done 0 -- KFE6")
    else:
        failures.append(f"  ✗ (a) the badge              rc={started.returncode}/{seen.returncode} raised={raised} "
                        f"line={counted} inbox={said!r} after={after}")

    # --- (b) the season and the launch --------------------------------------------------------------------
    h.declare("twice", "---\nagents: |\n  s agents/s\n  t agents/t\nreports: |\n  t -> s\nroot: s\nschedule: off\n"
                       "---\nTwo seasons.\n")
    first = h.call("team", "start", "twice", "--message", "season one", *h.harnessed)
    one_done = h.settled("twice", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    once = face("twice")
    journal = h.journal_of("twice")
    rows = [json.loads(one) for one in journal.read_text(encoding="utf-8").splitlines() if one.strip()]
    for one in rows:                                    # what a start before team 0.29.0 kept
        if one.get("kind") == "team-started":
            one["launch"]["max_budget_usd"] = 5.0
    journal.write_text("".join(json.dumps(one) + "\n" for one in rows), encoding="utf-8")
    second = h.call("team", "start", "twice", "--message", "season two", *h.harnessed)
    two_done = h.settled("twice", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), 60)
    twice = face("twice")
    provider = h.harnessed[h.harnessed.index("--provider") + 1] if "--provider" in h.harnessed else None
    launch = twice.get("launch") or {}
    members = [one.get("launch") for one in twice.get("members") or []]
    if (first.returncode == 0 and one_done and (once.get("season") or {}).get("n") == 1
            and second.returncode == 0 and two_done and (twice.get("season") or {}).get("n") == 2
            and (twice.get("season") or {}).get("at") == (twice.get("started") or {}).get("at")
            and set(launch) == LAUNCH and launch.get("provider") == provider and "max_budget_usd" not in launch
            and members == [launch, launch]):
        held("(b) the season and the launch", f"season 1 then 2; launch {launch}, no max_budget_usd; both members "
             "carry it")
    else:
        failures.append(f"  ✗ (b) the season and launch  rc={first.returncode}/{second.returncode} done={one_done}/"
                        f"{two_done} once={once.get('season')} twice={twice.get('season')} launch={launch} "
                        f"members={members} {second.stderr.strip()[-200:]!r}")

    # --- (c) the text keeps its bytes: a journal written by hand ------------------------------------------
    h.declare("fixed", "---\nagents: |\n  f agents/f\nroot: f\nschedule: off\n---\nA journal by hand.\n")
    at = "2026-10-01T09:00:00+00:00"
    events = [{"kind": "team-started", "agents": {"f": "agents/f"}, "reports": [], "root": "f", "principals": [],
               "owner": "house", "ceremonies": [], "entries": {}, "work": None, "launch": {"model": "m1"},
               "limits": {"budget": 1.0}, "schedule": None, "digest": "000000000000"},
              {"kind": "task", "task": "T1", "from": "house", "to": "f", "text": "count"},
              {"kind": "post", "task": "T1", "from": "house", "to": "f", "verb": "do", "text": "count"},
              {"kind": "wake-intent", "tag": "f-T1-aaaaaa", "agent": "f", "path": "agents/f", "task": "T1", "run": None,
               "index": 1, "messages": [3], "allowance": 1.0},
              {"kind": "wake-launched", "tag": "f-T1-aaaaaa", "agent": "f", "run": "abc123", "pid": 1},
              {"kind": "wake-ended", "tag": "f-T1-aaaaaa", "agent": "f", "run": "abc123", "index": 1, "cost": 0.25},
              {"kind": "post", "task": "T1", "from": "f", "to": "house", "verb": "ask", "text": "which?"}]
    h.journal_of("fixed").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("fixed").write_text("".join(json.dumps({"at": at, "id": n, "team": "fixed", **one}) + "\n"
                                             for n, one in enumerate(events, 1)), encoding="utf-8")
    text = h.call("team", "status", "fixed")
    digest = hashlib.sha256(text.stdout.encode()).hexdigest()[:12]
    if text.returncode == 0 and "T1" in text.stdout:
        held("(c) the text", f"team status on a journal by hand: {len(text.stdout)} bytes, sha {digest} -- KFE5")
    else:
        failures.append(f"  ✗ (c) the text               rc={text.returncode} {text.stderr.strip()[-200:]!r}")
    return 0
