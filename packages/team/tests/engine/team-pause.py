"""Scenario `team-pause` -- 6 case(s): `team pause <name>` holds a team -- the tick reaps and routes the wake-ups
under way, it rings and wakes nobody -- and `team resume <name>` (no `--task`) takes it back where it was. Four teams
run side by side in one house, each under its own names, each its story played beside the others'; the ceremony team
plays under a frozen clock (`PP_NOW`), a Wednesday, then a Thursday and a Friday. Each case reads its team's journal
and its face (`team status --json`).
- (a) the refusals before any writing: `team-unknown`, `team-not-started`, `principal-unknown` on a pause;
  `team-not-paused` on a resume without `--task` of a team not paused -- rc 2 each, the journal byte-identical;
  then that team, waiting [due], is paused -- the object and the team's line say `paused`, `waiting_on []`,
  `paused {by, at}` -- and resumed with `--no-tick`: waiting [due] again, no `paused`
- (b) a pause while a wake-up plays: a delegates to b and is paused while it plays; its wake-up ends on its own and
  is reaped -- `wake-ended`, its `do` to b routed -- and nobody is woken: no `wake-intent` nor `ceremony-due` after
  `paused` through a post, three ticks and a snapshot; the face says `state: paused`, `paused {by, at}`,
  `waiting_on []`; a second pause refuses `team-paused`
- (c) the resume: `team resume` writes `unpaused {by: house}`, then a tick wakes b on T1 and a on T2 -- each member
  in its run --; T1 and T2 resolve; the face is idle, no longer paused
- (d) no relance under a pause: a debtor puts its `do` off while the team is paused -- no wake-up through three
  ticks; `team resume` relances it first, and T1 resolves on the root's answer
- (e) a ceremony resumed the same day: paused at 08:00, the tick of 09:31 rings nothing; a ring at hand at 09:40
  writes its task and wakes nobody, the face paused; `team resume` at 10:00 rings the day's period -- its hour
  passed, never rung -- and wakes the participants of both rings and their facilitator
- (f) a ceremony resumed the next day: the same team paused on Thursday at 08:00 and resumed on Friday at 09:00 --
  Thursday's period is never rung, nothing rings at the resume; the tick of Friday 09:31 rings Friday's
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")

CALM = ("---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n---\n"
        "Delegate, then conclude.\n")
DEBT = ("---\nagents: |\n  chief agents/chief\n  debtor agents/debtor\nreports: |\n  debtor -> chief\nroot: chief\n"
        "schedule: off\n---\nDelegate, then conclude.\n")
GONG = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
        "ceremonies: |\n  daily every weekday 09:30 with p1 p2 -> f\nschedule: off\n---\nRing on demand.\n")
WEDNESDAY, THURSDAY, FRIDAY = "2026-09-30T", "2026-10-01T", "2026-10-02T"
NEVER = 10 ** 9


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (b)(c) a delegates to b, slowly enough to be paused while it plays; then concludes T2, then T1
        "a": [{"sleep": 2.5, "body": {"do": ["b"]}}, {"sleep": 0.1, "body": {"done": "second"}},
              {"sleep": 0.1, "body": {"done": "first"}}],
        "b": [{"sleep": 0.1, "body": {"done": True}}],
        # (d) the debtor puts its do off while the team pauses, answers it once relanced
        "chief": [{"sleep": 0.1, "body": {"do": ["debtor"]}},
                  {"sleep": 0.1, "body": {"re": "DO", "text": "after the pause"}}],
        "debtor": [{"sleep": 4.0, "body": []}, {"sleep": 0.1, "body": {"re": "DO", "text": "debtor done"}}],
        # (e)(f) the ceremony's facilitator and participants
        "f": [{"sleep": 0.1, "body": {"done": "ok"}}] * 8,
        "p1": [{"sleep": 0.1, "body": {"done": True}}] * 8,
        "p2": [{"sleep": 0.1, "body": {"done": True}}] * 8})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    said = lambda obj: (obj.get("state"), obj.get("waiting_on"))

    def since(found: list[dict], kind: str) -> int:
        """-> the id of the LAST `kind` event of the journal, NEVER when none."""
        marks = [one["id"] for one in by_kind(found, kind)]
        return marks[-1] if marks else NEVER

    # --- every team declared and started before the first wait: they run side by side ---------------------
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    h.declare("idle", "---\nagents: |\n  i agents/i\nroot: i\nschedule: off\n---\nLater.\n")
    h.declare("calm", CALM)
    h.declare("debt", DEBT)
    h.declare("gong", GONG)
    # the start of calm ticks and launches a, whose witness then sleeps: the pause right after falls while a plays
    starts = {"idle": lambda: [h.call("team", "start", "idle", "--message", "later", *h.harnessed, "--no-tick")],
              "gong": lambda: [h.call("team", "start", "gong", "--message", "open the day", *h.harnessed,
                                      now=WEDNESDAY + "07:50")],
              "calm": lambda: [h.call("team", "start", "calm", "--message", "task one", *h.harnessed),
                               h.call("team", "pause", "calm")],
              "debt": lambda: [h.call("team", "start", "debt", "--message", "task one", *h.harnessed)]}
    with ThreadPoolExecutor(max_workers=len(starts)) as pool:
        started = dict(zip(starts, pool.map(lambda one: one(), starts.values())))

    # --- each team's story, played beside the others' -------------------------------------------------------
    def idle_story() -> dict:
        """(a) judged before anything is written; a team waiting [due] paused, then resumed --no-tick."""
        seen = {"before": h.journal_of("idle").read_bytes()}
        seen["refusals"] = {
            "team-unknown": h.call("team", "pause", "nope"),
            "team-not-started": h.call("team", "pause", "never"),
            "principal-unknown": h.call("team", "pause", "idle", "--as", "zz"),
            "team-not-paused": h.call("team", "resume", "idle")}
        seen["untouched"] = h.journal_of("idle").read_bytes() == seen["before"] and not h.journal_of("never").exists()
        seen["due"] = h.face("idle")
        seen["paused"] = h.call("team", "pause", "idle")
        seen["stood"] = h.face("idle")
        seen["line"] = next((one for one in h.face() if one.get("team") == "idle"), {})
        seen["resumed"] = h.call("team", "resume", "idle", "--no-tick")
        seen["back"] = h.face("idle")
        return seen

    def calm_story() -> dict:
        """(b) a's wake-up reaped under the pause, nobody woken; (c) the resume, each member in its run."""
        seen = {"reaped": h.settled("calm", lambda found: bool(by_kind(found, "wake-ended", agent="a"))
                                    and all_ended(found), 45)}
        seen["posted"] = h.call("team", "post", "calm", "--message", "task two")
        seen["ticks"] = [h.call("team", "tick", "calm") for _ in range(3)]
        seen["snap"] = h.call("team", "snapshot", "calm")
        seen["paused_found"] = h.events("calm")
        seen["paused_face"] = h.face("calm")
        seen["again"] = h.call("team", "pause", "calm")
        seen["resumed"] = h.call("team", "resume", "calm")
        seen["done"] = h.settled("calm", lambda found: bool(by_kind(found, "done", task="T1"))
                                 and bool(by_kind(found, "done", task="T2")) and all_ended(found), 60)
        seen["found"] = h.events("calm")
        seen["face"] = h.face("calm")
        return seen

    def debt_story() -> dict:
        """(d) the debtor's wake-up launched by the chief's on-end tick, paused while it plays; no relance under the
        pause; the resume relances."""
        seen = {"playing": h.settled("debt", lambda found: bool(by_kind(found, "wake-launched", agent="debtor")), 45)}
        seen["paused"] = h.call("team", "pause", "debt")
        seen["reaped"] = h.settled("debt", lambda found: bool(by_kind(found, "wake-ended", agent="debtor"))
                                   and all_ended(found), 45)
        seen["ticks"] = [h.call("team", "tick", "debt") for _ in range(3)]
        seen["paused_found"] = h.events("debt")
        seen["resumed"] = h.call("team", "resume", "debt")
        seen["done"] = h.settled("debt", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
        seen["found"] = h.events("debt")
        return seen

    def gong_story() -> dict:
        """(e) Wednesday: paused before the ceremony's hour, resumed after it; (f) paused on Thursday before the
        hour, resumed on Friday before it, Friday's hour ticked."""
        seen = {"opened": h.settled("gong", lambda found: bool(by_kind(found, "done", task="T1"))
                                    and all_ended(found), 45)}
        seen["paused_e"] = h.call("team", "pause", "gong", now=WEDNESDAY + "08:00")
        seen["silent"] = h.call("team", "tick", "gong", now=WEDNESDAY + "09:31")
        seen["rung"] = h.call("team", "ring", "gong", "daily", now=WEDNESDAY + "09:40")
        seen["stood"] = h.face("gong", now=WEDNESDAY + "09:40")
        seen["held_back"] = h.events("gong")
        seen["resumed_e"] = h.call("team", "resume", "gong", now=WEDNESDAY + "10:00")
        seen["settled_e"] = h.settled("gong", lambda found: len(by_kind(found, "done")) >= 3 and all_ended(found), 60)
        seen["found_e"] = h.events("gong")
        seen["paused_f"] = h.call("team", "pause", "gong", now=THURSDAY + "08:00")
        seen["thursday"] = h.call("team", "tick", "gong", now=THURSDAY + "18:00")
        seen["resumed_f"] = h.call("team", "resume", "gong", now=FRIDAY + "09:00")
        seen["early"] = h.events("gong")
        seen["friday"] = h.call("team", "tick", "gong", now=FRIDAY + "09:31")
        seen["settled_f"] = h.settled("gong", lambda found: len(by_kind(found, "done")) >= 4 and all_ended(found), 60)
        seen["found_f"] = h.events("gong")
        return seen

    stories = {"idle": idle_story, "calm": calm_story, "debt": debt_story, "gong": gong_story}
    with ThreadPoolExecutor(max_workers=len(stories)) as pool:
        told = dict(zip(stories, pool.map(lambda one: one(), stories.values())))

    # --- (a) judged before writing; paused and resumed, the face says it ------------------------------------
    idle, refusals = told["idle"], told["idle"]["refusals"]
    stood, line, back, due = idle["stood"], idle["line"], idle["back"], idle["due"]
    if (started["idle"][0].returncode == 0 and idle["untouched"]
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and said(due) == ("waiting", ["due"]) and idle["paused"].returncode == 0
            and said(stood) == ("paused", []) and said(line) == ("paused", [])
            and (stood.get("paused") or {}).get("by") == "house" and (stood.get("paused") or {}).get("at")
            and (line.get("paused") or {}).get("by") == "house" and (line.get("paused") or {}).get("at")
            and idle["resumed"].returncode == 0 and said(back) == ("waiting", ["due"]) and not back.get("paused")):
        held("(a) judged before writing", "team-unknown, team-not-started, principal-unknown, team-not-paused: rc 2 "
             "each, the journal byte-identical; waiting [due], then paused (object and line, paused {by, at}), then "
             "waiting [due] again after resume --no-tick")
    else:
        failures.append(f"  ✗ (a) judged before writing    rc={started['idle'][0].returncode}/{idle['paused'].returncode}/"
                        f"{idle['resumed'].returncode} untouched={idle['untouched']} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]} "
                        f"due={said(due)} stood={said(stood)}/{stood.get('paused')} line={said(line)}/{line.get('paused')} "
                        f"back={said(back)}/{back.get('paused')}")

    # --- (b) a pause while a wake-up plays: reaped, nobody woken -----------------------------------------
    calm = told["calm"]
    start_b, pause_b = started["calm"]
    found = calm["paused_found"]
    mark = since(found, "paused")
    launched_a = [one["id"] for one in by_kind(found, "wake-launched", agent="a")]
    after = [one for one in found if one["id"] > mark]
    obj = calm["paused_face"]
    if (start_b.returncode == 0 and pause_b.returncode == 0 and calm["reaped"] and calm["posted"].returncode == 0
            and all(one.returncode == 0 for one in calm["ticks"]) and calm["snap"].returncode == 0
            and [one.get("by") for one in by_kind(found, "paused")] == ["house"]
            and launched_a and launched_a[0] < mark and by_kind(after, "wake-ended", agent="a")
            and [(one.get("from"), one.get("to")) for one in by_kind(after, "post", verb="do")] == [("a", "b"),
                                                                                                ("house", "a")]
            and not by_kind(after, "wake-intent") and not by_kind(after, "ceremony-due")
            and said(obj) == ("paused", [])
            and (obj.get("paused") or {}).get("by") == "house" and (obj.get("paused") or {}).get("at")
            and calm["again"].returncode == 2 and "team-paused" in calm["again"].stderr):
        held("(b) a pause while a wake-up plays", f"paused #{mark} after a's launch #{launched_a[0]}; a's wake-up "
             "reaped, its do to b routed; no wake-intent through a post, 3 ticks and a snapshot; the face paused "
             "{by, at}, waiting on nothing; a second pause refused team-paused")
    else:
        failures.append(f"  ✗ (b) a pause                  rc={start_b.returncode}/{pause_b.returncode}/"
                        f"{calm['posted'].returncode}/{calm['snap'].returncode}/{calm['again'].returncode} "
                        f"reaped={calm['reaped']} launched={launched_a} mark={mark} "
                        f"after={[(one['id'], one['kind'], one.get('agent'), one.get('verb')) for one in after]} "
                        f"{pause_b.stderr.strip()[-160:]!r} {calm['again'].stderr.strip()[-160:]!r} "
                        f"face={said(obj)}/{obj.get('paused')}")

    # --- (c) the resume: each member in its run ---------------------------------------------------------
    runs_a = T.runs_launched(found, "a")
    found = calm["found"]
    lifts = by_kind(found, "unpaused")
    lift = lifts[0]["id"] if lifts else NEVER
    woken = sorted({(one.get("agent"), one.get("task")) for one in by_kind(found, "wake-intent") if one["id"] > lift})
    a_after = {one.get("run") for one in by_kind(found, "wake-launched", agent="a") if one["id"] > lift}
    obj = calm["face"]
    if (calm["resumed"].returncode == 0 and calm["done"] and [one.get("by") for one in lifts] == ["house"]
            and ("b", "T1") in woken and ("a", "T2") in woken
            and a_after and a_after <= runs_a
            and obj.get("state") == "idle" and not obj.get("paused")):
        held("(c) the resume", f"unpaused #{lift}; woken {woken}; a in its run {sorted(a_after)[0]}; T1 and T2 "
             "resolved; the face idle, not paused")
    else:
        failures.append(f"  ✗ (c) the resume               rc={calm['resumed'].returncode} done={calm['done']} "
                        f"{calm['resumed'].stderr.strip()[-200:]!r} lifts={lifts} woken={woken} runs={runs_a} "
                        f"after={a_after} face={obj.get('state')}/{obj.get('paused')}")

    # --- (d) no relance under a pause; the resume relances -----------------------------------------------
    debt = told["debt"]
    found = debt["paused_found"]
    mark_d = since(found, "paused")
    ended_d = [one["id"] for one in by_kind(found, "wake-ended", agent="debtor")]
    during = [one for one in by_kind(found, "wake-intent") if one["id"] > mark_d]
    found = debt["found"]
    lift_d = since(found, "unpaused")
    after_d = [(one.get("agent"), one.get("relance")) for one in by_kind(found, "wake-intent") if one["id"] > lift_d]
    if (started["debt"][0].returncode == 0 and debt["playing"] and debt["paused"].returncode == 0 and debt["reaped"]
            and ended_d and ended_d[0] > mark_d and all(one.returncode == 0 for one in debt["ticks"]) and not during
            and debt["resumed"].returncode == 0 and debt["done"]
            and after_d[:1] == [("debtor", "owed")] and result_of(found, "T1") == "after the pause"):
        held("(d) no relance under a pause", f"the debtor puts its do off while paused #{mark_d}: no wake-intent "
             f"through 3 ticks; unpaused #{lift_d}: {after_d[0]} first, T1 'after the pause'")
    else:
        failures.append(f"  ✗ (d) no relance under a pause rc={started['debt'][0].returncode}/{debt['paused'].returncode}/"
                        f"{debt['resumed'].returncode} playing={debt['playing']} reaped={debt['reaped']} mark={mark_d} "
                        f"ended={ended_d} during={[(one.get('agent'), one.get('relance')) for one in during]} "
                        f"done={debt['done']} after={after_d} result={result_of(found, 'T1')!r}")

    # --- (e) a ceremony resumed the same day: the day's period rung at the resume ---------------------------
    gong = told["gong"]
    mark_e = since(gong["held_back"], "paused")
    held_back = [one for one in gong["held_back"] if one["id"] > mark_e]
    found = gong["found_e"]
    periods_e = [one.get("period") for one in by_kind(found, "ceremony-due")]
    lift_e = since(found, "unpaused")
    woken_e = sorted({one.get("agent") for one in by_kind(found, "wake-intent") if one["id"] > lift_e})
    calls_e = [started["gong"][0]] + [gong[key] for key in ("paused_e", "silent", "rung", "resumed_e")]
    if (all(one.returncode == 0 for one in calls_e) and gong["opened"] and gong["settled_e"]
            and not by_kind(held_back, "wake-intent")
            and [str(one.get("period")).startswith("manual-") for one in by_kind(held_back, "ceremony-due")] == [True]
            and gong["stood"].get("state") == "paused"
            and len(periods_e) == 2 and periods_e[1] == WEDNESDAY.rstrip("T")
            and woken_e == ["f", "p1", "p2"]):
        held("(e) resumed the same day", f"no ring at 09:31 under the pause; the ring at hand waits, the face paused; "
             f"the resume at 10:00 rings {periods_e[1]}, then wakes {woken_e}")
    else:
        failures.append(f"  ✗ (e) resumed the same day     rc={[one.returncode for one in calls_e]} opened={gong['opened']} "
                        f"settled={gong['settled_e']} periods={periods_e} "
                        f"held_back={[(one['id'], one['kind']) for one in held_back]} woken={woken_e} "
                        f"face={gong['stood'].get('state')} {gong['rung'].stderr.strip()[-160:]!r} "
                        f"{gong['paused_e'].stderr.strip()[-160:]!r}")

    # --- (f) a ceremony resumed the next day: the period passed under the pause never rung ------------------
    mark_f = since(gong["early"], "paused")
    early = [one.get("period") for one in by_kind(gong["early"], "ceremony-due") if one["id"] > mark_f]
    periods_f = [one.get("period") for one in by_kind(gong["found_f"], "ceremony-due") if one["id"] > mark_f]
    calls_f = [gong[key] for key in ("paused_f", "thursday", "resumed_f", "friday")]
    if (all(one.returncode == 0 for one in calls_f) and gong["settled_f"] and lift_e < mark_f < NEVER
            and early == [] and periods_f == [FRIDAY.rstrip("T")]):
        held("(f) resumed the next day", f"paused #{mark_f} on Thursday: Thursday's period never rung, nothing at the "
             f"resume on Friday 09:00, Friday's {periods_f[0]} at 09:31")
    else:
        failures.append(f"  ✗ (f) resumed the next day     rc={[one.returncode for one in calls_f]} "
                        f"settled={gong['settled_f']} mark={mark_f} early={early} periods={periods_f} "
                        f"{gong['resumed_f'].stderr.strip()[-160:]!r} {gong['paused_f'].stderr.strip()[-160:]!r}")
    return 0
