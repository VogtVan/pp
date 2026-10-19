"""Scenario `team-resume-blocked` -- 3 case(s) (batch la-reprise-d-une-tache, 2026-10-10: decisions 67-68
of the phase, team 0.18.0): `team resume` takes back an OPEN task a guard left with nobody due; the
counters count from the event, the team's budget never; each case names the invariant of
`team-sim-reframe.py` it replays.
- (a) a final failure (I23, I18): under `retries: 0`, u's first answer is no JSON object --
  `wake-failed response-unreadable` final, its run kept, `terminal`, the team's notice to the owner; a tick
  wakes nobody; `team resume` writes `resumed {from: [failed]}` and a note to u, the replay counts u's
  failures from zero and drops the failure's terminal; u is woken under its SAME run key and resolves T1
- (b) `wakes: 1` reached, then a snapshot (I10, I23): w asks the owner, the owner's reply finds the task's
  wake-ups spent -- `wakes-spent` once, nothing launched; `team resume --no-tick`, then `team snapshot`:
  `status` byte-identical before and after, the state read from the snapshot equal to the full replay key
  by key; a tick wakes w ONCE more -- its wake-ups counted from the resume, read from the snapshot -- and
  T1 resolves
- (c) the team's budget is never reset (I10): under `wakes: 1` and `budget-wakes: 1`, the task blocked by
  `wakes-spent`, `team resume` refuses `budget-spent`, the journal byte-identical
"""
from __future__ import annotations

import json
import subprocess
import sys

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "u": [{"sleep": 0.1, "body": "prose"}, {"sleep": 0.1, "body": {"done": "revived"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
              {"sleep": 0.1, "body": {"done": "answered"}}],
        "b": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which tag?"}}},
              {"sleep": 0.1, "body": {"done": "never"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    probe = T.probe_script(h, "state = mod.state_of(Path(sys.argv[1]))\n"
                              "print(json.dumps({'failures': [[a, t, n] for (a, t), n in state['failures'].items()],\n"
                              "                  'terminals': sorted([a, t] for a, t in state['terminals'])}))\n")

    def counters(name: str) -> dict:
        played = subprocess.run([sys.executable, str(probe), str(h.journal_of(name))], capture_output=True, text=True)
        return json.loads(played.stdout or "null") or {"probe": played.stderr[-300:]}

    # --- (a) a final failure taken back: u revived in its run -- I23, I18 ------------------------------
    h.declare("fall", "---\nagents: |\n  u agents/u\nroot: u\nretries: 0\nschedule: off\n---\nAnswer in JSON.\n")
    started = h.call("team", "start", "fall", "--message", "merge PR 7", *h.harnessed)
    failed = h.settled("fall", lambda found: bool(by_kind(found, "wake-failed", agent="u")) and all_ended(found), 60)
    h.call("team", "tick", "fall")
    found = h.events("fall")
    fell = next(iter(by_kind(found, "wake-failed", agent="u")), {})
    kept = fell.get("run")
    blocked = (fell.get("final") is True and not by_kind(found, "post", verb="re")
               and any(one.get("to") == "house" for one in by_kind(found, "post", verb="notice"))
               and len(by_kind(found, "wake-intent")) == 1)
    seen_before = counters("fall")
    resumed = h.call("team", "resume", "fall", "--task", "T1", "--message", "try again")
    done = h.settled("fall", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("fall")
    resumes = by_kind(found, "resumed")
    mark = resumes[0]["id"] if resumes else 10 ** 9
    after = {one.get("run") for one in by_kind(found, "wake-launched", agent="u") if one["id"] > mark}
    notes = [(one.get("to"), one.get("text")) for one in by_kind(found, "post", verb="note") if one["id"] > mark]
    if (started.returncode == 0 and failed and blocked and kept and resumed.returncode == 0 and done
            and seen_before.get("failures") == [["u", "T1", 1]] and seen_before.get("terminals") == [["u", "T1"]]
            and [(one.get("from")) for one in resumes] == [["failed"]] and notes == [("u", "try again")]
            and after == {kept} and result_of(found, "T1") == "revived"):
        held("(a) a final failure taken back", f"retries 0: u's prose final (run {kept} kept, its opening never "
             f"answered in its place, the notice to "
             f"house); resumed #{mark} from [failed], a note to u; u woken in run {kept}, T1 'revived' -- I23, I18")
    else:
        failures.append(f"  ✗ (a) a final failure taken back rc={started.returncode}/{resumed.returncode} failed={failed} "
                        f"blocked={bool(blocked)} kept={kept} done={done} before={seen_before} resumes={resumes} "
                        f"notes={notes} after={after} result={result_of(found, 'T1')!r} {resumed.stderr.strip()[-200:]!r}")

    # --- (b) wakes: 1 reached, resumed, snapshotted, woken once more -- I10, I23 -----------------------
    h.declare("spent", "---\nagents: |\n  w agents/w\nroot: w\nwakes: 1\nschedule: off\n---\nOne wake-up a time.\n")
    started_w = h.call("team", "start", "spent", "--message", "merge PR 8", *h.harnessed)
    asked = h.settled("spent", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    ask = next((one["id"] for one in by_kind(h.events("spent"), "post", verb="ask")), -1)
    replied = h.call("team", "post", "spent", "--task", "T1", "--reply", str(ask), "--message", "main")
    found = h.events("spent")
    spent_once = len(by_kind(found, "wakes-spent")) == 1 and len(by_kind(found, "wake-intent")) == 1
    resumed_w = h.call("team", "resume", "spent", "--task", "T1", "--no-tick")
    status_1 = h.call("team", "status", "spent").stdout
    face_1 = h.face("spent")
    snapped = h.call("team", "snapshot", "spent")
    status_2 = h.call("team", "status", "spent").stdout
    face_2 = h.face("spent")
    resumed_at = next((one["id"] for one in by_kind(h.events("spent"), "resumed")), None)
    t1_face = [(one.get("state"), one.get("resumed")) for one in face_1.get("tasks") or [] if one.get("id") == "T1"]
    same = T.probe_script(h, "journal = Path(sys.argv[1])\n"
                             "full = mod.replay([one for one in mod.lines_of(journal) if one.get('kind') != 'snapshot'])\n"
                             "cut = mod.state_of(journal)\n"
                             "print(json.dumps(sorted(key for key in full if key != 'messages' and full[key] != cut.get(key))))\n")
    compared = subprocess.run([sys.executable, str(same), str(h.journal_of("spent"))], capture_output=True, text=True)
    differing = json.loads(compared.stdout or "null")
    ticked = h.call("team", "tick", "spent")
    done_w = h.settled("spent", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("spent")
    if (started_w.returncode == 0 and asked and replied.returncode == 0 and spent_once and resumed_w.returncode == 0
            and snapped.returncode == 0 and status_1 == status_2 and face_1 == face_2
            and resumed_at is not None and t1_face == [("open", resumed_at)]
            and differing == [] and ticked.returncode == 0 and done_w
            and len(by_kind(found, "wake-intent")) == 2 and len(by_kind(found, "wakes-spent")) == 1
            and result_of(found, "T1") == "answered"):
        held("(b) wakes: 1 reached, taken back", "wakes-spent once; resumed (no tick), snapshot: status byte-identical, "
             "the snapshot's state equal to the full replay; a tick wakes w once more, T1 'answered' -- I10, I23")
    else:
        failures.append(f"  ✗ (b) wakes: 1 taken back      rc={started_w.returncode}/{replied.returncode}/"
                        f"{resumed_w.returncode}/{snapped.returncode}/{ticked.returncode} asked={asked} spent={spent_once} "
                        f"same_status={status_1 == status_2} differing={differing or compared.stderr[-300:]} done={done_w} "
                        f"intents={len(by_kind(found, 'wake-intent'))} {resumed_w.stderr.strip()[-200:]!r} T1={t1_face}/{resumed_at}")

    # --- (c) the team's budget is never reset -- I10 ---------------------------------------------------
    h.declare("broke", "---\nagents: |\n  b agents/b\nroot: b\nwakes: 1\nbudget-wakes: 1\nschedule: off\n---\n"
                       "One wake-up in all.\n")
    started_b = h.call("team", "start", "broke", "--message", "tag release", *h.harnessed)
    asked_b = h.settled("broke", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    ask_b = next((one["id"] for one in by_kind(h.events("broke"), "post", verb="ask")), -1)
    replied_b = h.call("team", "post", "broke", "--task", "T1", "--reply", str(ask_b), "--message", "v2")
    before = h.journal_of("broke").read_bytes()
    refused = h.call("team", "resume", "broke", "--task", "T1")
    if (started_b.returncode == 0 and asked_b and replied_b.returncode == 0 and by_kind(h.events("broke"), "wakes-spent")
            and refused.returncode == 2 and "budget-spent" in refused.stderr
            and h.journal_of("broke").read_bytes() == before):
        held("(c) the team's budget is never reset", "wakes 1 and budget-wakes 1: the task wakes-spent, "
             "team resume refuses budget-spent, the journal byte-identical -- I10")
    else:
        failures.append(f"  ✗ (c) the budget never reset    rc={started_b.returncode}/{replied_b.returncode}/"
                        f"{refused.returncode} asked={asked_b} {refused.stderr.strip()[-200:]!r} "
                        f"same={h.journal_of('broke').read_bytes() == before}")
    return 0
