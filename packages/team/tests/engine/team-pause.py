"""Scenario `team-pause` -- 3 case(s) (batch la-pause-de-l-equipe, 2026-10-12: row 83 of the study § 18,
team 0.32.0): `team pause <name>` holds a team -- the tick reaps and meets the waits, it rings and wakes
nobody -- and `team resume <name>` (no `--task`) takes it back where it was; each case names the invariant of
`team-sim-reframe.py` it replays.
- (a) the refusals before any writing: `team-unknown`, `team-not-started`, `principal-unknown` on a pause;
  `team-not-paused` on a resume without `--task` of a team not paused -- rc 2 each, the journal byte-identical
- (b) a pause while a wake-up plays (I24): a delegates to b and is paused while it plays; its wake-up ends on
  its own and is reaped -- `wake-ended`, its `do` to b routed -- and nobody is woken: no `wake-intent` after
  `paused` through a post (which says it), three ticks and a snapshot; `status --json` says `paused {by, at}`
  and `state: paused`, the text says `paused since`; a second pause refuses `team-paused`
- (c) the resume (I24, I18): `team resume` writes `unpaused {by: house}`, then a tick wakes b on T1 and a on T2
  -- each member in its run --; T1 and T2 resolve; the face no longer says paused
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

CALM = ("---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n---\n"
        "Delegate, then conclude.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "a": [{"sleep": 2.5, "body": {"do": ["b"]}}, {"sleep": 0.1, "body": {"done": "second"}},
              {"sleep": 0.1, "body": {"done": "first"}}],
        "b": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def face(name: str) -> dict:
        try:
            return json.loads(h.call("team", "status", name, "--json").stdout)
        except ValueError:
            return {}

    # --- (a) judged before anything is written -------------------------------------------------------
    h.declare("never", CALM)
    h.declare("idle", CALM)
    idle = h.call("team", "start", "idle", "--message", "later", *h.harnessed, "--no-tick")
    before = h.journal_of("idle").read_bytes()
    refusals = {
        "team-unknown": h.call("team", "pause", "nope"),
        "team-not-started": h.call("team", "pause", "never"),
        "principal-unknown": h.call("team", "pause", "idle", "--as", "zz"),
        "team-not-paused": h.call("team", "resume", "idle")}
    untouched = h.journal_of("idle").read_bytes() == before and not h.journal_of("never").exists()
    if (idle.returncode == 0 and untouched
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())):
        held("(a) judged before writing", "team-unknown, team-not-started, principal-unknown, team-not-paused: "
             "rc 2 each, the journal byte-identical")
    else:
        failures.append(f"  ✗ (a) judged before writing    rc={idle.returncode} untouched={untouched} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]}")

    # --- (b) a pause while a wake-up plays: reaped, nobody woken -- I24 ------------------------------
    h.declare("calm", CALM)
    started = h.call("team", "start", "calm", "--message", "task one", *h.harnessed)
    playing = h.settled("calm", lambda found: bool(by_kind(found, "wake-launched", agent="a")), 45)
    paused = h.call("team", "pause", "calm")
    reaped = h.settled("calm", lambda found: bool(by_kind(found, "wake-ended", agent="a")) and all_ended(found), 45)
    posted = h.call("team", "post", "calm", "--message", "task two")
    ticks = [h.call("team", "tick", "calm") for _ in range(3)]
    snap = h.call("team", "snapshot", "calm")
    found = h.events("calm")
    mark = next((one["id"] for one in by_kind(found, "paused")), 10 ** 9)
    after = [one for one in found if one["id"] > mark]
    obj = face("calm")
    text = h.call("team", "status", "calm").stdout
    again = h.call("team", "pause", "calm")
    if (started.returncode == 0 and playing and paused.returncode == 0 and reaped and posted.returncode == 0
            and all(one.returncode == 0 for one in ticks) and snap.returncode == 0
            and [one.get("by") for one in by_kind(found, "paused")] == ["house"]
            and by_kind(after, "wake-ended", agent="a")
            and [(one.get("from"), one.get("to")) for one in by_kind(after, "post", verb="do")] == [("a", "b"),
                                                                                                ("house", "a")]
            and not by_kind(after, "wake-intent") and not by_kind(after, "ceremony-due")
            and "paused: nobody woken until team resume" in posted.stdout
            and obj.get("state") == "paused" and obj.get("waiting_on") == []
            and (obj.get("paused") or {}).get("by") == "house" and (obj.get("paused") or {}).get("at")
            and "paused since " in text and again.returncode == 2 and "team-paused" in again.stderr):
        held("(b) a pause while a wake-up plays", f"paused #{mark}; a's wake-up reaped, its do to b routed; "
             "no wake-intent through a post, 3 ticks and a snapshot; the face paused -- I24")
    else:
        failures.append(f"  ✗ (b) a pause                  rc={started.returncode}/{paused.returncode}/{posted.returncode}/"
                        f"{snap.returncode}/{again.returncode} playing={playing} reaped={reaped} "
                        f"after={[(one['id'], one['kind'], one.get('agent'), one.get('verb')) for one in after]} "
                        f"post={posted.stdout.strip()[-160:]!r} {paused.stderr.strip()[-160:]!r} "
                        f"face={obj.get('state')}/{obj.get('waiting_on')}/{obj.get('paused')}")

    # --- (c) the resume: each member in its run -- I24, I18 -------------------------------------------
    runs = {member: T.runs_launched(found, member) for member in ("a",)}
    resumed = h.call("team", "resume", "calm")
    done = h.settled("calm", lambda found: bool(by_kind(found, "done", task="T1")) and bool(by_kind(found, "done", task="T2"))
                     and all_ended(found), 60)
    found = h.events("calm")
    lifts = by_kind(found, "unpaused")
    lift = lifts[0]["id"] if lifts else 10 ** 9
    woken = sorted({(one.get("agent"), one.get("task")) for one in by_kind(found, "wake-intent") if one["id"] > lift})
    a_after = {one.get("run") for one in by_kind(found, "wake-launched", agent="a") if one["id"] > lift}
    obj = face("calm")
    if (resumed.returncode == 0 and done and [one.get("by") for one in lifts] == ["house"]
            and ("b", "T1") in woken and ("a", "T2") in woken
            and a_after and a_after <= runs["a"]
            and obj.get("state") == "idle" and not obj.get("paused")
            and "paused since " not in h.call("team", "status", "calm").stdout):
        held("(c) the resume", f"unpaused #{lift}; woken {woken}; a in its run {sorted(a_after)[0]}; T1 and T2 "
             "resolved; the face idle -- I24, I18")
    else:
        failures.append(f"  ✗ (c) the resume               rc={resumed.returncode} done={done} {resumed.stderr.strip()[-200:]!r} "
                        f"lifts={lifts} woken={woken} runs={runs} after={a_after} face={obj.get('state')}/{obj.get('paused')}")
    return 0
