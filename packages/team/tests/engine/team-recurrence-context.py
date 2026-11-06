"""Scenario `team-recurrence-context` -- 2 case(s) (batch la-limite-de-contexte, team 1.2.0; study § 21, row 120): a
recurrence carries a CONTEXT LIMIT (`team post … --every "<when>" --context <n>%`), and the member's first wake-up on a
NEW occurrence renews the recurrence's run once the last measure of that run, kept at `wake-ended`, reached it. One team
under a frozen clock (`PP_NOW`), Monday 2026-10-05 then Tuesday. The witness measures the tokens of its calls; under a
caller's command the house knows no window, so while the team rests the case writes into the measures kept the
`window` and the `used` a house that launched a provider would have written (`measured_in`) -- the renewal is judged on
the journal alone. The change of a limit by `team recurrence` is `team-recurrence-changed`'s.
- (a) judged before writing: `--context` without `--every` (the usage), `--context 0%`, `120%`, `abc`, `off` at a pose
  (`context-invalid`) -- rc 2, the journal byte-identical
- (b) the renewal: four recurrences of `day 09:00`, each to its member, all played by one agent -- ra (`--context 50%`,
  Monday measured past it), rb (`--context 50`, measured under it), rc (no limit, measured past 50 %), rd (`--context
  50%`, no measure); Tuesday ra writes ONE `run-renewed {member, recurrence, task, run, used, limit}` and OPENS a new run
  (its intent `run: null`) named after ra, which asks the owner; once that new run is measured past the limit, the
  owner's answer wakes la again within the occurrence: it resumes the new run, no second renewal; rb, rc and rd resume
  their Monday run; `status --json` says `recurrences[].context` [50, 50, null, 50]; `log --json` the `run-renewed`
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

MONDAY, TUESDAY = T.MONDAY, T.TUESDAY
WINDOW = 100_000                                          # the window a launched provider's house would have declared
TEAM = ("---\nagents: |\n  lm agents/m\n  la agents/w\n  lb agents/w\n  lc agents/w\n  ld agents/w\nreports: |\n"
        "  la lb lc ld -> lm\nroot: lm\nschedule: off\n---\nKeep the recurrences.\n")


def measured_in(h, name: str) -> None:
    """The measures kept at the team's `wake-ended` given the `window` and the `used` a house that launched a provider
    would have said -- written while the team rests, every id and every other field kept."""
    journal = h.journal_of(name)
    lines = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    for one in lines:
        if one.get("kind") == "wake-ended" and isinstance(one.get("context"), dict):
            tokens = int(one["context"].get("tokens") or 0)
            one["context"] = {**one["context"], "window": WINDOW, "used": round(tokens / WINDOW, 4)}
    journal.write_text("".join(json.dumps(one, ensure_ascii=False) + "\n" for one in lines), encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    past, under = int(WINDOW * 0.6), int(WINDOW * 0.3)    # 60 % and 30 % of the window
    measured = lambda sent, body: {"sleep": 0.1, "calls": [{"name": "Read", "sent": sent}], "body": body}
    h.scripted(**{                                         # each occurrence by its task: Monday T1-T4, Tuesday T5-T8
        "la": {"T1": [measured(past, {"done": "monday"})],
               "T5": [measured(past, {"ask": {"to": "house", "text": "which branch?"}}),
                      measured(past, {"done": "tuesday"})]},
        "lb": {"T2": [measured(under, {"done": True})], "T6": [measured(under, {"done": True})]},
        "lc": {"T3": [measured(past, {"done": True})], "T7": [measured(past, {"done": True})]},
        "ld": {"T4": [{"sleep": 0.1, "body": {"done": True}}], "T8": [{"sleep": 0.1, "body": {"done": True}}]}})
    by_kind, all_ended = T.by_kind, T.all_ended
    h.declare("lim", TEAM)
    started = h.call("team", "start", "lim", *h.harnessed, now=MONDAY + "07:50")

    # --- (a) judged before writing -------------------------------------------------------------------------------
    before = h.journal_of("lim").read_bytes()
    pose = lambda *rest: h.call("team", "post", "lim", "--message", "x", "--to", "la", *rest, now=MONDAY + "07:55")
    refused = {"usage": pose("--context", "50%"),
               "context-invalid": pose("--every", "day 09:00", "--context", "0%"),
               "context-invalid ": pose("--every", "day 09:00", "--context", "120%"),
               "context-invalid  ": pose("--every", "day 09:00", "--context", "abc"),
               "context-invalid   ": pose("--every", "day 09:00", "--context", "off")}
    usage = pose("--task", "T1", "--every", "day 09:00").stderr.strip()     # the usage as `post` says it
    untouched = h.journal_of("lim").read_bytes() == before
    if (started.returncode == 0 and untouched and refused["usage"].returncode == 2
            and refused["usage"].stderr.strip() == usage
            and all(one.returncode == 2 and code.strip() in one.stderr for code, one in refused.items()
                    if code != "usage")):
        held("(a) judged before writing", "--context without --every the usage; 0%, 120%, abc, off context-invalid: rc 2, "
             "the journal byte-identical")
    else:
        failures.append(f"  ✗ (a) judged before writing    started={started.returncode} untouched={untouched} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refused.items()]}")

    # --- (b) the renewal --------------------------------------------------------------------------------------------
    poses = [h.call("team", "post", "lim", "--message", f"keep {who}", "--to", who, "--name", name, "--every", "day 09:00",
                    *limit, "--no-tick", now=MONDAY + "08:00")
             for who, name, limit in (("la", "ra", ("--context", "50%")), ("lb", "rb", ("--context", "50")),
                                      ("lc", "rc", ()), ("ld", "rd", ("--context", "50%")))]
    monday = h.call("team", "tick", "lim", now=MONDAY + "09:01")
    first = h.settled("lim", lambda found: len(by_kind(found, "done")) == 4 and all_ended(found), 45)
    measured_in(h, "lim")
    tuesday = h.call("team", "tick", "lim", now=TUESDAY + "09:01")
    asked = h.settled("lim", lambda found: len(by_kind(found, "done")) == 7 and all_ended(found)
                      and bool(by_kind(found, "post", verb="ask", to="house")), 45)
    measured_in(h, "lim")
    question = next(iter(by_kind(h.events("lim"), "post", verb="ask", to="house")), {})
    answered = h.call("team", "post", "lim", "--task", "T5", "--reply", str(question.get("id")), "--message", "main",
                      now=TUESDAY + "10:00")
    second = h.settled("lim", lambda found: len(by_kind(found, "done")) == 8 and all_ended(found), 45)
    found = h.events("lim")
    task_of = {one.get("task"): one.get("recurrence") for one in by_kind(found, "task")}
    runs = lambda member, rec: [(one.get("task"), one.get("run")) for one in by_kind(found, "wake-intent", agent=member)
                                if task_of.get(one.get("task")) == rec]
    launched = {one.get("tag"): one.get("run") for one in by_kind(found, "wake-launched")}
    keys = [launched.get(one.get("tag")) for one in by_kind(found, "wake-intent", agent="la")]
    renewed = by_kind(found, "run-renewed")
    kept = {member: runs(member, rec) for member, rec in (("lb", "R2"), ("lc", "R3"), ("ld", "R4"))}
    named = {one.get("run"): one.get("name")
             for one in (json.loads(line) for line in h.call("agent", "status", "agents/w", "--json").stdout.splitlines()
                         if line.strip()) if one.get("run")}
    face = h.face("lim", now=TUESDAY + "12:00")
    logged = [json.loads(line) for line in h.call("team", "log", "lim", "--json", now=TUESDAY + "12:00").stdout
              .splitlines() if line.strip()]
    one = renewed[0] if renewed else {}
    if (all(call.returncode == 0 for call in (*poses, monday, tuesday, answered)) and first and asked and second
            and len(renewed) == 1 and one.get("member") == "la" and one.get("recurrence") == "R1"
            and one.get("task") == "T5" and one.get("run") == keys[0] and one.get("limit") == 50
            and float(one.get("used") or 0) * 100 >= 50
            and [run for _, run in runs("la", "R1")] == [None, None, keys[1]] and len(set(keys)) == 2
            and named.get(keys[1]) == "ra"
            and all(len(intents) == 2 and intents[0][1] is None and intents[1][1] is not None
                    for intents in kept.values())
            and [entry.get("context") for entry in face.get("recurrences") or []] == [50, 50, None, 50]
            and [entry.get("run") for entry in logged if entry.get("event") == "run-renewed"] == [keys[0]]):
        held("(b) the renewal", f"ra: run-renewed {one.get('run')} at used {one.get('used')} >= 50%, a new run {keys[1]} "
             "named ra; the owner's answer within the occurrence resumed it, past the limit; rb, rc, rd kept their run; "
             "the face's limits [50, 50, null, 50]; log --json run-renewed")
    else:
        failures.append(f"  ✗ (b) the renewal            rc={[call.returncode for call in (*poses, monday, tuesday, answered)]} "
                        f"first={first} asked={asked} second={second} renewed={renewed} ra_intents={runs('la', 'R1')} "
                        f"ra_keys={keys} kept={kept} named={named} "
                        f"ends={[(e.get('agent'), e.get('context')) for e in by_kind(found, 'wake-ended')]} "
                        f"limits={[e.get('context') for e in face.get('recurrences') or []]} "
                        f"{answered.stderr.strip()[-200:]!r}")
    return 0
