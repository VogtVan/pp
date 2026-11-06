"""Scenario `team-member-run` -- 3 case(s): a member holds ONE run, ONE key and ONE session per task it carries,
the run opened at its first wake-up on the task, resumed at every later one there and named after the task; the
parallel between members is `team-member-run-parallel`. Three teams run side by side in one house, each under its
own names; each case waits for its team, then reads its journal and its face.
- (n) one run per task, named after it: nm opens T1 and delegates it to hp; T2 (`--name ddr4-price`), posted
  meanwhile, OPENS a second run, a second session; hp's answer on T1 resumes T1's run (`--run`); never two
  wake-ups of nm at once; `agent status --json` names T1's runs `one T1` (no name given) and T2's `ddr4-price`
- (p) a refused act keeps its run: ur's opening says a `do` off the edges -- `wake-refused` carrying its run,
  a note to ur; the launch the note brings resumes that key, one session
- (r) a name the house refuses: a ceremony whose name holds a zero-width space (no printable line) rung at hand
  opens rf's and rp's runs of the ceremony; `agent name` refuses `name-invalid`, said at each `wake-launched`
  (`name-refused`); each wake-up plays on, its run unnamed at `agent status --json`, the ring's task resolved,
  no wake-up failed -- the one carrier a house hands `agent name` unfit: a task's name is checked printable at its
  birth, a ceremony's is any word of the declaration
"""
from __future__ import annotations

import json
import threading

from tests.harness import support

T = support(__file__, "team")

ODD = "stand\u200bup"          # a ceremony's name the house refuses as a run's: U+200B is no printable character


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (n) one member, two tasks: T1 delegated to hp, T2 played while hp works
        "nm": {"T1": [{"sleep": 0.1, "body": {"do": ["hp"]}},
                      {"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "second"}}]},
        "hp": [{"sleep": 2.0, "body": {"done": "helped"}}],
        # (p) the opening answers a do to a member off the edges, then answers readably
        "ur": [{"sleep": 0.1, "body": {"do": ["ux"]}},
               {"sleep": 0.1, "body": {"done": "read at last"}}]})
    by_kind, all_ended, intents_on, result_of, runs_launched = (
        T.by_kind, T.all_ended, T.intents_on, T.result_of, T.runs_launched)
    done_on = lambda task: (lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found))

    # --- every team declared and started before the first wait: they run side by side ----------------------
    # (r)'s team, started and rung at hand beside the others' starts: its ring is the longest chain of the scenario
    h.declare("odd", "---\nagents: |\n  rf agents/rf\n  rp agents/rp\nreports: |\n  rp -> rf\nroot: rf\n"
                     f"ceremonies: |\n  {ODD} every weekday 09:30 with rp -> rf\nschedule: off\n---\nAn odd name.\n")
    played_r: dict = {}
    opening_r = threading.Thread(target=lambda: played_r.update(
        odd=h.call("team", "start", "odd", *h.harnessed, "--no-tick"), rung=h.call("team", "ring", "odd", ODD)))
    opening_r.start()
    h.declare("one", "---\nagents: |\n  nm agents/nm\n  hp agents/hp\nreports: |\n  hp -> nm\nroot: nm\n"
                     "schedule: off\n---\nOne member, two tasks.\n")
    h.declare("stray", "---\nagents: |\n  ur agents/ur\n  ux agents/ux\nreports: |\n  ur -> ux\nroot: ur\n"
                       "retries: 1\nschedule: off\n---\nAn answer off the edges.\n")
    one_t = h.call("team", "start", "one", "--message", "first task", *h.harnessed)
    stray = h.call("team", "start", "stray", "--message", "read it", *h.harnessed)
    # nm's second task, posted while its first one plays
    two_t = h.call("team", "post", "one", "--to", "nm", "--name", "ddr4-price", "--message", "second task")

    # --- (n) one run per task, named after it ----------------------------------------------------------
    both_n = h.settled("one", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=60)
    found_nm = h.events("one")
    launched_by_tag = {one.get("tag"): one.get("run") for one in by_kind(found_nm, "wake-launched")}
    on_t1, on_t2 = intents_on(found_nm, "nm", "T1"), intents_on(found_nm, "nm", "T2")
    key_t1 = launched_by_tag.get(on_t1[0]["tag"]) if on_t1 else None
    key_t2 = launched_by_tag.get(on_t2[0]["tag"]) if on_t2 else None
    open_nm, twice_n = set(), False
    for one in found_nm:                              # never two wake-ups of nm without an end
        if one.get("kind") == "wake-intent" and one.get("agent") == "nm":
            twice_n = twice_n or bool(open_nm)
            open_nm.add(one["tag"])
        elif one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            open_nm.discard(one.get("tag"))
    named = {}
    for path in ("agents/nm", "agents/hp"):
        for line in h.call("agent", "status", path, "--json").stdout.splitlines():
            one = json.loads(line)
            if one.get("run"):
                named[one["run"]] = one.get("name")
    key_hp = next((one.get("run") for one in by_kind(found_nm, "wake-launched", agent="hp")), None)
    seen_n = (len(on_t1), [one.get("run") for one in on_t1], len(on_t2), (on_t2 or [{}])[0].get("run"))
    if (one_t.returncode == 0 and two_t.returncode == 0 and both_n and key_t1 and key_t2 and key_t1 != key_t2
            and seen_n == (2, [None, key_t1], 1, None)
            and runs_launched(found_nm, "nm") == {key_t1, key_t2} and not twice_n
            and len({session for _, session in h.sessions_at("agents/nm")}) == 2
            and named.get(key_t1) == "one T1" and named.get(key_t2) == "ddr4-price" and named.get(key_hp) == "one T1"
            and result_of(found_nm, "T1") == "first" and result_of(found_nm, "T2") == "second"):
        held("(n) one run per task, named after it", f"nm opens T1 in {key_t1} and T2 in {key_t2}, two sessions; "
             "hp's answer resumes T1's key; never two wake-ups of nm; the runs named `one T1` and `ddr4-price`")
    else:
        failures.append(f"  ✗ (n) one run per task        {one_t.returncode}/{two_t.returncode} both={both_n} "
                        f"t1={key_t1} t2={key_t2} intents={seen_n} runs={runs_launched(found_nm, 'nm')} "
                        f"twice={twice_n} sessions={h.sessions_at('agents/nm')} names={named} hp={key_hp} "
                        f"results={result_of(found_nm, 'T1')!r}/{result_of(found_nm, 'T2')!r}")

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

    # --- (r) a name the house refuses: the wake-up plays on unnamed ------------------------------------------
    opening_r.join()
    odd, rung_r = played_r["odd"], played_r["rung"]
    done_r = h.settled("odd", lambda found: bool(by_kind(found, "done")) and all_ended(found)
                       and {one.get("agent") for one in by_kind(found, "wake-ended")} >= {"rf", "rp"}, timeout=60)
    found_r = h.events("odd")
    ring_r = next((one for one in by_kind(found_r, "task") if one.get("ceremony") == ODD), {})
    intents_r = {one["tag"]: one for one in by_kind(found_r, "wake-intent") if one.get("task") == ring_r.get("task")}
    launched_r = {one.get("agent"): one for one in by_kind(found_r, "wake-launched") if one.get("tag") in intents_r}
    names_r = {}
    for member, path in (("rf", "agents/rf"), ("rp", "agents/rp")):
        for line in h.call("agent", "status", path, "--json").stdout.splitlines():
            one = json.loads(line)
            if one.get("run") and one["run"] == (launched_r.get(member) or {}).get("run"):
                names_r[member] = one.get("name")
    tasks_r = {one.get("id"): one.get("state") for one in h.face("odd").get("tasks") or []}
    if (odd.returncode == 0 and rung_r.returncode == 0 and done_r and ring_r
            and set(launched_r) == {"rf", "rp"} and all(one.get("run") is None for one in intents_r.values())
            and all("name-invalid" in str(one.get("name-refused") or "") for one in launched_r.values())
            and set(names_r) == {"rf", "rp"} and not any(names_r.values())
            and tasks_r.get(ring_r.get("task")) == "resolved" and not by_kind(found_r, "wake-failed")):
        held("(r) a name the house refuses", f"the ring {ring_r.get('task')} opens rf's and rp's ceremony runs: "
             "wake-launched says name-refused (name-invalid) at each, the runs unnamed at agent status, the ring "
             "resolved, nothing failed")
    else:
        failures.append(f"  ✗ (r) a name refused          {odd.returncode}/{rung_r.returncode} done={done_r} "
                        f"{(odd.stderr + rung_r.stderr)[-300:]!r} ring={ring_r} "
                        f"launched={ {k: (v.get('run'), v.get('name-refused')) for k, v in launched_r.items()} } "
                        f"intents={[(one['id'], one.get('agent'), one.get('run')) for one in intents_r.values()]} "
                        f"names={names_r} tasks={tasks_r} failed={by_kind(found_r, 'wake-failed')}")

    return 0
