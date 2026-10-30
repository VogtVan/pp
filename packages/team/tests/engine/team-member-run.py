"""Scenario `team-member-run` -- 3 case(s): a member holds ONE run, ONE key and ONE session for the team's whole
work, its tasks arrive in that run, and it plays one wake-up at a time while the members run in parallel. Three
teams run side by side in one house, each under its own names; each case waits for its team, then reads its
journal and its face.
- (n) one run per member: nm's T2 arrives in the run of its T1 (`--run`), one session at `sessions.jsonl`; the
  face shows nm at agents/nm, nothing pending, its run that key, ended, on T1 and T2
- (p) a refused act keeps its run: ur's opening says a `do` off the edges -- `wake-refused` carrying its run,
  a note to ur; the launch the note brings resumes that key, one session
- (o) one wake-up at a time per member: tv1 tv2 tv3 of agents/trio launch together, three runs, three sessions;
  tl's `do` on T2 to tv1 while tv1 plays T1 waits, and arrives in tv1's run at its next wake-up; never two
  wake-ups of tv1 at once, no `run-busy`
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (n) one member, two tasks
        "nm": {"T1": [{"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "second"}}]},
        # (p) the opening answers a do to a member off the edges, then answers readably
        "ur": [{"sleep": 0.1, "body": {"do": ["ux"]}},
               {"sleep": 0.1, "body": {"done": "read at last"}}],
        # (o) three members on one agent; tv1 still plays T1 when T2 comes
        "tl": {"T1": [{"sleep": 0.2, "body": {"do": ["tv1", "tv2", "tv3"]}},
                      {"sleep": 0.1, "body": {"done": "T1 by three"}}],
               "T2": [{"sleep": 0.1, "body": {"do": ["tv1"]}},
                      {"sleep": 0.1, "body": {"done": "T2 by tv1"}}]},
        "tv1": {"T1": [{"sleep": 25.0, "body": {"done": True}}],   # long enough to be playing when T2 comes
                "T2": [{"sleep": 0.2, "body": {"done": True}}]},
        "tv2": [{"sleep": 6.0, "body": {"done": True}}],
        "tv3": [{"sleep": 6.0, "body": {"done": True}}]})
    by_kind, all_ended, intents_on, result_of, runs_launched = (
        T.by_kind, T.all_ended, T.intents_on, T.result_of, T.runs_launched)
    done_on = lambda task: (lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found))

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("one", "---\nagents: |\n  nm agents/nm\nroot: nm\nschedule: off\n---\nOne member, two tasks.\n")
    h.declare("stray", "---\nagents: |\n  ur agents/ur\n  ux agents/ux\nreports: |\n  ur -> ux\nroot: ur\n"
                       "retries: 1\nschedule: off\n---\nAn answer off the edges.\n")
    h.declare("trio", "---\nagents: |\n  tl agents/lead3\n  tv1 agents/trio\n  tv2 agents/trio\n  tv3 agents/trio\n"
                      "reports: |\n  tv1 tv2 tv3 -> tl\nroot: tl\nschedule: off\n---\nThree members on one agent.\n")
    trio = h.call("team", "start", "trio", "--message", "review PR 60", *h.harnessed)
    one_t = h.call("team", "start", "one", "--message", "first task", *h.harnessed)
    stray = h.call("team", "start", "stray", "--message", "read it", *h.harnessed)

    # the second task of each team, posted while its first one plays or once it is done
    three = h.settled("trio", lambda found: len([one for one in by_kind(found, "wake-launched")
                                                 if one.get("agent") in ("tv1", "tv2", "tv3")]) == 3, timeout=60)
    trio2 = h.call("team", "post", "trio", "--to", "tl", "--message", "review PR 61")
    first_n = h.settled("one", done_on("T1"), timeout=60)
    time.sleep(0.5)                                   # the on-end tick has left
    two_t = h.call("team", "post", "one", "--to", "nm", "--message", "second task")

    # --- (n) one run per member -------------------------------------------------------------------------
    second_n = h.settled("one", done_on("T2"), timeout=60)
    found_nm = h.events("one")
    key_nm = next((one.get("run") for one in by_kind(found_nm, "wake-ended", agent="nm")), "")
    on_t2 = intents_on(found_nm, "nm", "T2")
    face_nm = next((one for one in h.face("one").get("members", []) if one.get("member") == "nm"), {})
    seen_nm = (face_nm.get("path"), len(face_nm.get("pending") or []), face_nm.get("run"), face_nm.get("how"),
               face_nm.get("tasks"))
    if (one_t.returncode == 0 and first_n and two_t.returncode == 0 and second_n and key_nm
            and len(on_t2) == 1 and on_t2[0].get("run") == key_nm and runs_launched(found_nm, "nm") == {key_nm}
            and len({session for _, session in h.sessions_at("agents/nm")}) == 1
            and seen_nm == ("agents/nm", 0, key_nm, "ended", ["T1", "T2"])
            and result_of(found_nm, "T2") == "second"):
        held("(n) one run per member", f"nm's T2 arrives in its run {key_nm} (--run): one key, one session at "
             "sessions.jsonl; the face shows nm at agents/nm, nothing pending, that run, ended, on T1 T2")
    else:
        failures.append(f"  ✗ (n) one run per member      {one_t.returncode}/{two_t.returncode} first={first_n} "
                        f"second={second_n} key={key_nm} t2={[(one['id'], one.get('run')) for one in on_t2]} "
                        f"runs={runs_launched(found_nm, 'nm')} sessions={h.sessions_at('agents/nm')} face={seen_nm}")

    # --- (p) a refused act keeps its run ----------------------------------------------------------------
    done_p = h.settled("stray", done_on("T1"), timeout=60)
    found_s = h.events("stray")
    refused_s = by_kind(found_s, "wake-refused", agent="ur")
    intents_s = by_kind(found_s, "wake-intent", agent="ur")
    key_s = next((one.get("run") for one in by_kind(found_s, "wake-launched", agent="ur")), "")
    if (stray.returncode == 0 and done_p and len(refused_s) == 1 and refused_s[0].get("run") == key_s
            and not by_kind(found_s, "wake-failed")
            and len(intents_s) == 2 and intents_s[1].get("run") == key_s and runs_launched(found_s, "ur") == {key_s}
            and len({session for _, session in h.sessions_at("agents/ur")}) == 1
            and result_of(found_s, "T1") == "read at last"):
        held("(p) a refused act keeps its run", f"ur's opening says a do off the edges: wake-refused with its run "
             f"{key_s}, no failure; the launch the note brings resumes that key, one session; T1 done")
    else:
        failures.append(f"  ✗ (p) refused keeps its run    {stray.returncode} done={done_p} "
                        f"refused={[(one.get('why'), one.get('run')) for one in refused_s]} "
                        f"fails={by_kind(found_s, 'wake-failed')} "
                        f"intents={[(one['id'], one.get('run')) for one in intents_s]} key={key_s} "
                        f"sessions={h.sessions_at('agents/ur')}")

    # --- (o) one wake-up at a time per member, the parallel between members ------------------------------
    done_o = h.settled("trio", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=90)
    found_o = h.events("trio")
    tv_launched = {one.get("agent"): one for one in by_kind(found_o, "wake-launched")
                   if one.get("agent") in ("tv1", "tv2", "tv3") and one.get("tag") in
                   {i["tag"] for i in by_kind(found_o, "wake-intent") if i.get("task") == "T1"}}
    first_tv_end = min((one["id"] for one in by_kind(found_o, "wake-ended") if one.get("agent") in ("tv1", "tv2", "tv3")),
                       default=0)
    tv1_t1_end = next((one["id"] for one in by_kind(found_o, "wake-ended", agent="tv1")), 10 ** 9)
    tv1_t2 = intents_on(found_o, "tv1", "T2")
    do_t2 = next((one["id"] for one in by_kind(found_o, "post", verb="do") if one.get("task") == "T2"
                  and one.get("to") == "tv1"), 10 ** 9)
    open_tv1, twice = set(), False
    for one in found_o:                               # never two wake-ups of tv1 without an end
        if one.get("kind") == "wake-intent" and one.get("agent") == "tv1":
            twice = twice or bool(open_tv1)
            open_tv1.add(one["tag"])
        elif one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            open_tv1.discard(one.get("tag"))
    busy_o = [one for one in by_kind(found_o, "wake-failed") if "run-busy" in str(one.get("reason"))]
    keys_o = {member: runs_launched(found_o, member) for member in ("tv1", "tv2", "tv3")}
    if (trio.returncode == 0 and three and trio2.returncode == 0 and done_o
            and set(tv_launched) == {"tv1", "tv2", "tv3"} and all(one["id"] < first_tv_end for one in tv_launched.values())
            and all(len(keys) == 1 for keys in keys_o.values())
            and len(set().union(*keys_o.values())) == 3
            and len({session for _, session in h.sessions_at("agents/trio")}) == 3
            and do_t2 < tv1_t1_end and len(tv1_t2) == 1 and tv1_t2[0]["id"] > tv1_t1_end
            and tv1_t2[0].get("run") in keys_o["tv1"] and not twice and not busy_o
            and result_of(found_o, "T1") == "T1 by three" and result_of(found_o, "T2") == "T2 by tv1"):
        held("(o) one wake-up at a time per member", "tv1 tv2 tv3 of agents/trio launched together, three runs, "
             f"three sessions; tl's do on T2 to tv1 (#{do_t2}) while tv1 plays T1 waits, and arrives in tv1's run "
             f"after its end (#{tv1_t1_end}); never two wake-ups of tv1, no run-busy")
    else:
        failures.append(f"  ✗ (o) one wake-up per member  {trio.returncode}/{trio2.returncode} three={three} done={done_o} "
                        f"launched={ {k: v['id'] for k, v in tv_launched.items()} } first_end={first_tv_end} "
                        f"keys={keys_o} sessions={h.sessions_at('agents/trio')} do_t2={do_t2} tv1_end={tv1_t1_end} "
                        f"tv1_t2={[(one['id'], one.get('run')) for one in tv1_t2]} twice={twice} busy={len(busy_o)} "
                        f"results={result_of(found_o, 'T1')!r}/{result_of(found_o, 'T2')!r}")
    return 0
