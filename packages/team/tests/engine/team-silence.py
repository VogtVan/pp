"""Scenario `team-silence` -- 3 case(s) (batches le-silence-au-detecteur, team 0.48.0, and le-battement-du-reveil; study
§ 19, row 115): the silence as the detector's second input, counted in PASSAGES -- a wake-up and its continuations,
until the run parks --, its limit, a mute worker. `team-silence-long` (a long task informed) and `team-silence-mute` (a
mute root suspected, tried) carry the other cases.
- (c) a mute worker unblocks its supervisor: w's wake-up and two relances `owed`, each a wake-up (`continued` false)
  whose `wake-intent` keeps the BEAT -- 3, 2, 1: the exchanges left, this one counted, after 0, 1 and 2 silent
  passages --, `log --json` saying both; then `silence {passages: 3}`; the `do` it owes is answered
  in its place (`suspected: true`, no `returned`: a launch delivered it), sup is woken, its head hands the `do` back
  with the text sup wrote, said delivered without an answer, and closes T1; no `preempted` anywhere -- KSD13
- (d) the count is right, read from the journal alone, written by hand without `continued` and again with it, the
  same counts: a wake-up that stands and its continuation that parks are ONE silent passage, a continuation counts for
  nothing; an act of the member, a `resume` and a season set it to zero; a passage of a member that owes nothing counts
  not; a passage that parks while the member waits for its principal's answer counts not, the one after the answer
  does; a member suspected by a failed launch does not fall by silence, its interval passed, on a silent passage older
  than its fall (`silences`): it was not tried; a run that stands on a closed occurrence of a recurrence is held as
  parked after its one continuation there, so the first launch on the next occurrence is a wake-up for the count as
  for its intent, and its silent passage counts; `status --json` read twice without a tick is the same bytes -- KSD12
- (e) the limit: `silence: 0` refuses `team-invalid`; `team start --silence 5` is the season's, `--member s --silence 2`
  the member's, over it
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

AT = "2026-11-03T21:00:00+00:00"
WORK = "sort the second shelf"                    # what sup writes to w
STARTED = {"kind": "team-started", "agents": {"m": "agents/m"}, "reports": [], "root": "m", "principals": [],
           "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None, "digest": "000000000000"}


def exchange(tag: str, task: str, messages: list, state: str, agent: str = "m", continued: bool | None = None) -> list[dict]:
    """-> one launch of a member on the task as the journal keeps it: its intent, its launch, its end in `state`; with
    `continued`, the intent says whether it continues a standing run -- a journal of before says nothing."""
    return [{"kind": "wake-intent", "tag": tag, "agent": agent, "path": f"agents/{agent}", "task": task, "run": f"k-{agent}",
             "index": 1, "messages": messages, **({} if continued is None else {"continued": continued})},
            {"kind": "wake-launched", "tag": tag, "agent": agent, "run": f"k-{agent}", "pid": 1, "launch": 1},
            {"kind": "wake-ended", "tag": tag, "agent": agent, "run": f"k-{agent}", "launch": 1, "state": state, "cost": 0.01}]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "sup": [{"sleep": 0.1, "body": {"do": {"w": WORK}}}, {"sleep": 0.1, "body": {"re": "DO", "text": "closed without w"}}],
        "w": [{"sleep": 0.1, "body": []}] * 6,
        "r": [{"sleep": 0.1, "body": {"do": ["s"]}}],
        "s": [{"sleep": 4.0, "body": []}] * 3})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    module = h.module()

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    def member_face(name: str, member: str, now: str | None = None) -> dict:
        return next((one for one in h.face(name, now=now).get("members") or [] if one.get("member") == member), {})

    h.declare("stuck", "---\nagents: |\n  sup agents/sup\n  w agents/w\nreports: |\n  w -> sup\nroot: sup\nschedule: off\n"
                       "---\nDelegate, then conclude.\n")
    started = {"stuck": h.call("team", "start", "stuck", "--message", "do it", *h.harnessed)}

    # --- (c) a mute worker unblocks its supervisor ---------------------------------------------------------------
    done_c = h.settled("stuck", ended, timeout=90)
    found = h.events("stuck")
    to_w = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "sup"})), None)
    relances_w = [one.get("relance") for one in T.intents_of(found, "w")]
    limit = getattr(module, "DEFAULT_SILENCE", 3)
    beats_w = [(one.get("continued"), one.get("beat")) for one in T.intents_of(found, "w")]
    logged = [json.loads(one) for one in h.call("team", "log", "stuck", "--json").stdout.splitlines() if one.strip()]
    said_w = [(one.get("continued"), one.get("beat")) for one in logged
              if one.get("event") == "wake-intent" and one.get("agent") == "w"]
    in_place = [one for one in by_kind(found, "post", verb="re", **{"from": "w"}) if one.get("by") == "tick"]
    preempted = [one for one in found if one.get("preempted")]
    back = {}                                         # what sup's heads hand back to it, by the message's id
    for one in h.prompts_of("sup"):
        back.update(T.handed_back(module, one))
    if (started["stuck"].returncode == 0 and done_c and relances_w == [None, "owed", "owed"]
            and beats_w == [(False, limit), (False, limit - 1), (False, limit - 2)] and limit == 3 and said_w == beats_w
            and [(one.get("agent"), one.get("passages")) for one in by_kind(found, "silence")] == [("w", limit)]
            and [(one.get("re"), one.get("suspected"), one.get("returned"), one.get("to")) for one in in_place]
            == [(to_w, True, None, "sup")]
            and (back.get(to_w) or {}).get("how") == "suspected" and back[to_w].get("text") == WORK
            and not preempted and not by_kind(found, "post", verb="notice") and result_of(found, "T1") == "closed without w"):
        held("(c) a mute worker unblocks its supervisor", f"w woken then relanced owed twice, each a wake-up, the beats "
             f"{[beat for _, beat in beats_w]} at its intents and in log --json; silence at the third silent passage; its do "
             f"#{to_w} answered in its place (suspected, not returned), sup's head hands it back, delivered without an "
             "answer, and sup closes T1; nothing preempted, no notice")
    else:
        failures.append(f"  ✗ (c) a mute worker            rc={started['stuck'].returncode} done={done_c} relances={relances_w} "
                        f"beats={beats_w} logged={said_w} "
                        f"silences={[(one.get('agent'), one.get('passages')) for one in by_kind(found, 'silence')]} "
                        f"in_place={[(one.get('re'), one.get('suspected'), one.get('returned'), one.get('to')) for one in in_place]} "
                        f"back={back} preempted={len(preempted)} result={result_of(found, 'T1')!r}")

    # --- (d) the count, read from the journal alone ---------------------------------------------------------------
    opening = [{"kind": "task", "task": "T1", "from": "house", "to": "m", "text": "count it"},
               {"kind": "post", "task": "T1", "from": "house", "to": "m", "verb": "do", "text": "count it"}]
    pair = {**STARTED, "agents": {"m": "agents/m", "n": "agents/n"}, "reports": [{"from": ["n"], "to": "m"}]}
    h.declare("count", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\nCount.\n")
    h.declare("duo", "---\nagents: |\n  m agents/m\n  n agents/n\nreports: |\n  n -> m\nroot: m\nschedule: off\n---\nCount.\n")

    def journals(said: bool | None) -> dict:
        """-> the journals of the case, by name: (team, member, events) -- `said` writes `continued` on every intent, as
        a journal of now does; None leaves it out, as a journal of before."""
        mark = (lambda value: None) if said is None else (lambda value: value)
        launch = lambda tag, messages, state, continued, agent="m": exchange(tag, "T1", messages, state, agent, mark(continued))
        # two passages: a wake-up that stands, its continuation that parks; a relance that stands, its continuation
        parked = (launch("s", [3], "standing", False) + launch("a", [], "parked", True)
                  + launch("b", [3], "standing", False) + launch("c", [], "parked", True))
        info = [{"kind": "post", "task": "T1", "from": "m", "to": "house", "verb": "info", "text": "at work"}]
        # n answers its do, then two passages where it owes nothing (a principal's info each), then a new do: one
        owing = (launch("m1", [3], "parked", False)
                 + [{"kind": "post", "task": "T1", "from": "m", "to": "n", "verb": "do", "text": "first"}]            # 7
                 + launch("n1", [7], "parked", False, "n")
                 + [{"kind": "post", "task": "T1", "from": "n", "to": "m", "verb": "re", "re": 7, "text": "done"},     # 11
                    {"kind": "post", "task": "T1", "from": "house", "to": "n", "verb": "info", "text": "fyi"}]         # 12
                 + launch("n2", [12], "parked", False, "n")
                 + [{"kind": "post", "task": "T1", "from": "house", "to": "n", "verb": "info", "text": "fyi"}]         # 16
                 + launch("n3", [16], "parked", False, "n")
                 + [{"kind": "post", "task": "T1", "from": "m", "to": "n", "verb": "do", "text": "second"}]           # 20
                 + launch("n4", [20], "parked", False, "n"))
        # m asks its principal: two passages park while it waits, one after the answer
        asked = (launch("q1", [3], "parked", False)
                 + [{"kind": "post", "task": "T1", "from": "m", "to": "house", "verb": "ask", "text": "which?"},      # 7
                    {"kind": "post", "task": "T1", "from": "house", "to": "m", "verb": "info", "text": "fyi"}]         # 8
                 + launch("q2", [8], "parked", False)
                 + [{"kind": "post", "task": "T1", "from": "house", "to": "m", "verb": "info", "text": "fyi"}]         # 12
                 + launch("q3", [12], "parked", False)
                 + [{"kind": "post", "task": "T1", "from": "house", "to": "m", "verb": "re", "re": 7, "text": "this"}]  # 16
                 + launch("q4", [16], "parked", False))
        # two occurrences of one recurrence, one run: m answers the first and its run stands there, one continuation on
        # the closed task and it stands still; then its launch on the second occurrence parks in silence
        occurrence = lambda task, day: [
            {"kind": "task", "task": task, "from": "house", "to": "m", "text": "count it", "recurrence": "R1", "period": day},
            {"kind": "post", "task": task, "from": "house", "to": "m", "verb": "do", "text": "count it"}]
        carrier = (occurrence("T1", "2026-11-03") + launch("o1", [3], "standing", False)
                   + [{"kind": "post", "task": "T1", "from": "m", "to": "house", "verb": "re", "re": 3, "text": "counted"},
                      {"kind": "done", "task": "T1", "result": "counted"}]
                   + launch("o2", [], "standing", True)
                   + occurrence("T2", "2026-11-04")                                                                   # 12, 13
                   + exchange("o3", "T2", [13], "parked", "m", mark(False)))
        return {"parked": ("count", "m", [STARTED] + opening + parked),
                "carrier": ("count", "m", [STARTED] + carrier),
                "acted": ("count", "m", [STARTED] + opening + parked + info + launch("d", [3], "parked", False)),
                "resumed": ("count", "m", [STARTED] + opening + parked
                            + [{"kind": "resumed", "task": "T1", "by": "house", "from": ["stopped"]}]),
                "season": ("count", "m", [STARTED] + opening + parked + [STARTED]),
                "owing": ("duo", "n", [pair] + opening + owing),
                "asked": ("duo", "m", [pair] + opening + asked)}

    counts, same = {}, []
    passages = {"parked": 2, "acted": 1, "resumed": 0, "season": 0, "owing": 1, "asked": 1, "carrier": 1}
    again = ("parked", "owing", "asked", "carrier")   # the journals written a second time, `continued` on every intent
    for said in (None, True):
        for label, (name, member, events) in journals(said).items():
            if said and label not in again:
                continue
            h.written(name, events, AT)
            counts[(label, said)] = member_face(name, member).get("silence")
            if label == "parked" and said is None:
                same.append(h.call("team", "status", name, "--json").stdout == h.call("team", "status", name, "--json").stdout)
    wanted = {(label, said): [{"task": "T2" if label == "carrier" else "T1", "passages": n, "limit": limit}]
              for label, n in passages.items() for said in (None, True) if said is None or label in again}
    # n's passage on its do parks in silence, then its launch dies for good: suspected by that failure. Its interval
    # passed, the silence of before its fall is no fall: nothing tried it
    fallen = ([pair] + opening + exchange("m1", "T1", [3], "parked")
              + [{"kind": "post", "task": "T1", "from": "m", "to": "n", "verb": "do", "text": "first"}]               # 7
              + exchange("n1", "T1", [7], "parked", "n")
              + [{"kind": "wake-intent", "tag": "n2", "agent": "n", "path": "agents/n", "task": "T1", "run": "k-n",
                  "index": 2, "messages": [7], "relance": "owed"},
                 {"kind": "wake-launched", "tag": "n2", "agent": "n", "run": "k-n", "pid": 1, "launch": 2},
                 {"kind": "wake-failed", "tag": "n2", "agent": "n", "task": "T1", "final": True, "reason": "wake-dead"}])
    h.written("duo", fallen, AT)
    state = module.replay(T.lines(h.journal_of("duo")))
    judged = {"suspected": module.suspicion_of(state, "n") is not None,
              "passages": module.silence_of(state, "n", "T1") if "passages_of" in dir(module) else None,
              "fell": [(one.get("agent"), one.get("task")) for one in module.silences(state, "duo", T.local_after(AT, 6), "n")
                       if one.get("kind") == "silence"]}
    if counts == wanted and same == [True] and judged == {"suspected": True, "passages": 1, "fell": []}:
        held("(d) the count is right", "a wake-up that stands and its continuation that parks are one silent passage: two "
             "of them count 2; an info of m then one passage counts 1; a resume, a season count 0; n's two passages "
             "owing nothing count not, the one of its new do counts 1; m's two passages parked while it waits for house "
             "count not, the one after the answer counts 1; the same with and without `continued`; n, suspected by a "
             "failed launch, its interval passed: no fall on its silent passage of before; a run held as parked on a "
             "closed occurrence: its launch on the next one counts 1; status --json twice the same bytes -- KSD12")
    else:
        failures.append(f"  ✗ (d) the count                counts={counts} same={same} judged={judged}")

    # --- (e) the limit: TEAM.md, the season, the profile -----------------------------------------------------------
    h.declare("bad", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\nsilence: 0\n---\nBad.\n")
    refused = h.call("team", "start", "bad", "--message", "x", *h.harnessed)
    h.declare("lim", "---\nagents: |\n  r agents/r\n  s agents/s\nreports: |\n  s -> r\nroot: r\nschedule: off\n---\nLimits.\n")
    seasoned = h.call("team", "start", "lim", "--message", "do it", "--silence", "5", *h.harnessed,
                      "--member", "s", "--silence", "2")
    h.settled("lim", lambda found: bool(T.by_kind(found, "wake-launched", agent="s")), timeout=60)   # s plays: it owes
    face_e = h.face("lim")
    limits_e = {one.get("member"): [(s.get("task"), s.get("limit")) for s in one.get("silence") or []]
                for one in face_e.get("members") or []}
    if (refused.returncode == 2 and "team-invalid" in refused.stderr and "silence" in refused.stderr
            and seasoned.returncode == 0 and (face_e.get("limits") or {}).get("silence") == 5
            and limits_e.get("r") == [("T1", 5)] and limits_e.get("s") == [("T1", 2)]):
        held("(e) the limit", "silence: 0 refuses team-invalid; --silence 5 is the season's limit (r), --member s --silence 1 "
             "the member's (s, 2)")
    else:
        failures.append(f"  ✗ (e) the limit                rc={refused.returncode}/{seasoned.returncode} "
                        f"{refused.stderr.strip()[-120:]!r} limits={face_e.get('limits')} per_member={limits_e} "
                        f"owes={[(one.get('member'), one.get('owes')) for one in face_e.get('members') or []]} "
                        f"intents={[(one.get('agent'), one.get('relance')) for one in T.by_kind(h.events('lim'), 'wake-intent')]} "
                        f"refused={[one.get('why') for one in T.by_kind(h.events('lim'), 'wake-refused')]} "
                        f"{seasoned.stderr.strip()[-160:]!r}")
    return 0
