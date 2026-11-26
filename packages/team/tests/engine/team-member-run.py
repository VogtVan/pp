"""Scenario `team-member-run` -- 5 case(s): a member holds ONE run, ONE key and ONE session per task it carries,
the run opened at its first wake-up on the task, resumed at every later one there and named after the task; the
parallel between members is `team-member-run-parallel`. Five teams run side by side in one house, each under its
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
- (s) each run its own face: pa ends T1 parked in one run, T2 opens a second (a `do` to pb, parked), pb's answer
  resumes it; while that launch plays and once it ended, `team status --json` says in `members[pa].runs[]` the `how`,
  `since` and `context` of each run's own launches in the journal; pa's `run`, `how`, `since` and `context` keep
  their values -- the last launch's run and hour, the context of pa's last end --, and `members[pa].tasks` lists
  the tasks of BOTH runs, T1 and T2, not those of the last run alone (s.1470)
- (h) the house plays a member: hm is the path `.`, its role `keep` holding a document of the shelf
  (`keep notes/plain`); its wake-ups on T1 and T2 open two runs IN THE HOUSE, each slot
  under the team's root of documents, each flow opened with the vector `team-member:home/hm` and nothing refused;
  no prompt of hm carries the readings `team-inbox` nor `team-roster` while the owner's `team inbox` holds T1
  resolved; `team status --json` says hm's `path` `.`; `team reset home --member hm` forgets T1's and T2's runs
  alone -- a run of the house opened outside the team stands
"""
from __future__ import annotations

import json
import re
import threading
from pathlib import Path

from conductor import persistence
from tests.harness import cli, support

T = support(__file__, "team")
S = support(__file__, "templates")

MEMBER_H = "team-member:home/hm"   # the vector of the member the house plays
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
               {"sleep": 0.1, "body": {"done": "read at last"}}],
        # (s) pa ends T1 in one run, then plays T2 in a second: a do to pb, then a long resumed launch -- each
        # launch measured apart (`sent`), so each end keeps its own context
        "pa": {"T1": [{"sleep": 0.1, "calls": [{"name": "Read", "sent": 11000}], "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "calls": [{"name": "Read", "sent": 22000}], "body": {"do": ["pb"]}},
                      {"sleep": 2.0, "calls": [{"name": "Read", "sent": 33000}], "body": {"done": "second"}}]},
        "pb": [{"sleep": 0.1, "body": {"done": True}}],
        # (h) the house plays hm: one launch per task
        "hm": {"T1": [{"sleep": 0.1, "body": {"done": "home one"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "home two"}}]}})
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
    h.declare("pair", "---\nagents: |\n  pa agents/pa\n  pb agents/pb\nreports: |\n  pb -> pa\nroot: pa\n"
                      "schedule: off\n---\nTwo runs.\n")
    pair_started = h.call("team", "start", "pair", "--message", "first task", *h.harnessed)
    pair_posted = h.call("team", "post", "pair", "--to", "pa", "--message", "second task")
    S.laid(h.house / "teams" / "templates", {"notes/plain.md": S.SHELF["notes/plain.md"]})   # a role's document: the vector mounts
    h.declare("home", "---\nagents: |\n  hm .\nroot: hm\nschedule: off\nroles: |\n  keep hm\n"
                      "documents: |\n  keep notes/plain\n---\n"
                      "The house plays a member.\n")
    home_started = h.call("team", "start", "home", "--message", "first task", *h.harnessed)
    home_posted = h.call("team", "post", "home", "--to", "hm", "--message", "second task")   # woken once T1 ended

    def member_of(obj: dict, name: str) -> dict:
        return next((one for one in obj.get("members") or [] if one.get("member") == name), {})

    def pair_expected(found: list[dict]) -> tuple[dict, dict]:
        """-> (each run of pa: its how, since, context, from that run's launches in the journal; pa's own fields as
        the face said them before: its last launch's run and hour, the context of its last end)."""
        intents = by_kind(found, "wake-intent", agent="pa")
        launched = {one.get("tag"): one for one in by_kind(found, "wake-launched", agent="pa")}
        ends = {one.get("tag"): one for one in found if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed")}
        run = lambda one: (launched.get(one["tag"]) or {}).get("run") or one.get("run")
        runs = {}
        for key in dict.fromkeys(run(one) for one in intents if run(one)):
            mine = [one for one in intents if run(one) == key]
            open_ = [one for one in mine if one["tag"] not in ends]
            last = ends.get(mine[-1]["tag"]) or {}
            told = [ends[one["tag"]].get("context") for one in mine if one["tag"] in ends
                    and ends[one["tag"]].get("kind") == "wake-ended" and ends[one["tag"]].get("context") is not None]
            runs[key] = ({"how": "running", "since": open_[-1].get("at")} if open_ else
                         {"how": last.get("state"), "since": last.get("at")}) | {"context": (told or [None])[-1]}
        last_end = (by_kind(found, "wake-ended", agent="pa") or [{}])[-1]
        mine = {"run": run(intents[-1]) if intents else None,
                "since": (launched.get(intents[-1]["tag"]) or {}).get("at") if intents and intents[-1]["tag"] not in ends
                else None, "context": last_end.get("context")}
        return runs, mine

    def pair_face(obj: dict) -> tuple[dict, dict]:
        pa = member_of(obj, "pa")
        return ({one.get("run"): {key: one.get(key, "absent") for key in ("how", "since", "context")}
                 for one in pa.get("runs") or []},
                {key: pa.get(key) for key in ("run", "since", "context")} | {"how": pa.get("how")})

    def playing(found: list[dict]) -> bool:
        """pa's second launch on T2 launched and not ended: the resumed run plays."""
        on_t2 = intents_on(found, "pa", "T2")
        tags = {one.get("tag") for one in by_kind(found, "wake-launched", agent="pa")}
        ended = {one.get("tag") for one in found if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed")}
        return len(on_t2) == 2 and on_t2[1]["tag"] in tags and on_t2[1]["tag"] not in ended

    # (s) read while pa's resumed launch plays: before any other wait, the other teams play on meanwhile
    pair_playing = h.settled("pair", playing, 60)
    pair_running_found = h.events("pair")
    pair_running = h.face("pair")
    pair_playing = pair_playing and playing(h.events("pair"))   # the face read while it still plays

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

    # --- (s) each run its own face ---------------------------------------------------------------------------
    pair_done = h.settled("pair", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 60)
    pair_ended = h.face("pair")
    pair_ended_found = h.events("pair")
    runs_on, mine_on = pair_expected(pair_running_found)
    face_runs_on, face_mine_on = pair_face(pair_running)
    runs_off, mine_off = pair_expected(pair_ended_found)
    face_runs_off, face_mine_off = pair_face(pair_ended)
    keys = list(runs_off)
    if (pair_started.returncode == 0 and pair_posted.returncode == 0 and pair_playing and pair_done
            and len(keys) == 2 and runs_on.get(keys[0], {}).get("how") == "parked"
            and runs_on.get(keys[1], {}).get("how") == "running"
            and runs_off.get(keys[1], {}).get("how") in ("standing", "parked")
            and None not in [one.get("context") for one in (*runs_on.values(), *runs_off.values())]
            and runs_on[keys[0]]["context"] != mine_on["context"]
            and face_runs_on == runs_on and face_runs_off == runs_off
            and face_mine_on == mine_on | {"how": "running"} and face_mine_off == mine_off | {"how": "ended"}
            and member_of(pair_running, "pa").get("tasks") == ["T1", "T2"]
            and member_of(pair_ended, "pa").get("tasks") == ["T1", "T2"]):
        held("(s) each run its own face", f"pa's runs {keys}: playing {face_runs_on}, then {face_runs_off} -- each "
             f"its journal's; pa's own run {face_mine_on.get('run')}, how running then ended, its since and context "
             "unmoved -- KFPR1; its tasks T1 and T2, those of both runs")
    else:
        failures.append(f"  ✗ (s) each run its own face   rc={pair_started.returncode}/{pair_posted.returncode} "
                        f"playing={pair_playing} done={pair_done} runs={runs_on}/{runs_off} "
                        f"face={face_runs_on}/{face_runs_off} mine={mine_on}/{mine_off} "
                        f"face_mine={face_mine_on}/{face_mine_off} tasks={member_of(pair_running, 'pa').get('tasks')}/"
                        f"{member_of(pair_ended, 'pa').get('tasks')} {pair_started.stderr[-200:]!r}")

    # --- (h) the house plays a member ----------------------------------------------------------------------------
    both_h = h.settled("home", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=60)
    found_h = h.events("home")
    keys_h = [one.get("run") for one in by_kind(found_h, "wake-launched", agent="hm")]
    team_dir = (h.teams / "home").resolve()
    slots_h = {key: persistence.slot_of(h.house, key) for key in keys_h if key}
    rooted = {key: slot.is_file() and Path(persistence.documents_of(slot) or "/").resolve() == team_dir
              for key, slot in slots_h.items()}
    flows_h = {key: T.lines(T.flow_file(h, ".", key)) for key in slots_h}
    vectors_h = {key: [one.get("vectors") for one in found if one.get("kind") == "opened"] for key, found in flows_h.items()}
    refused_h = [one for found in flows_h.values() for one in found if one.get("kind") == "refused"]
    prompts_h = h.prompts_of("hm")
    served_h = [name for name in ("team-inbox", "team-roster") if any(f"INFORMATION — {name}" in one for one in prompts_h)]
    inbox_h = h.call("team", "inbox", "--json")
    inboxed = [json.loads(line).get("team") for line in inbox_h.stdout.splitlines() if line.startswith("{")]
    path_h = member_of(h.face("home"), "hm").get("path")
    outside = cli(h.engine, "--instance", str(h.house), "-new", cwd=h.ws, env=h.env)
    other_h = (re.search(r"run ([0-9a-f]{6})", outside.stdout) or [None, ""])[1]
    reset_h = h.call("team", "reset", "home", "--member", "hm")
    reset_runs = [one.get("run") for one in by_kind(h.events("home"), "run-reset", member="hm")]
    if (home_started.returncode == 0 and home_posted.returncode == 0 and both_h
            and len(set(keys_h)) == 2 and None not in keys_h and all(rooted.values())
            and all(one and all(MEMBER_H in (vectors or []) for vectors in one) for one in vectors_h.values())
            and not refused_h and not by_kind(found_h, "wake-failed")
            and len(prompts_h) == 2 and not served_h and inbox_h.returncode == 0 and "home" in inboxed
            and path_h == "."
            and other_h and reset_h.returncode == 0 and sorted(reset_runs) == sorted(keys_h)
            and not any(slot.is_file() for slot in slots_h.values())
            and persistence.slot_of(h.house, other_h).is_file()):
        held("(h) the house plays a member", f"hm at `.`: T1 and T2 in runs {keys_h} of the house, under teams/home, "
             f"each opened with {MEMBER_H}, nothing refused; no team-inbox nor team-roster in its prompts; status "
             f"path `.`; reset --member hm forgets those two, the house's run {other_h} stands")
    else:
        failures.append(f"  ✗ (h) the house plays a member rc={home_started.returncode}/{home_posted.returncode} "
                        f"done={both_h} keys={keys_h} rooted={rooted} vectors={vectors_h} "
                        f"refused={refused_h} failed={by_kind(found_h, 'wake-failed')} prompts={len(prompts_h)} "
                        f"served={served_h} inbox={inbox_h.returncode}/{inboxed} path={path_h!r} "
                        f"other={other_h!r} reset={reset_h.returncode}/{reset_runs} "
                        f"slots={[slot.is_file() for slot in slots_h.values()]} "
                        f"{(home_started.stderr + reset_h.stderr)[-300:]!r}")

    return 0
