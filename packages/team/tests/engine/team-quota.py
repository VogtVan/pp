"""Scenario `team-quota` -- 5 case(s) (batch l-echec-du-harness-borne, team 1.25.0; s.1571): a launch that ends on the
provider's USAGE LIMIT is a stop of the member, never a failure: `quota-reached {agent, task, until, said}`, no retry,
no fall, no answer; the member is launched on NO task before `until`, or, without `until`, before `team resume --task`
on one of its tasks. One team under the modelled LLM's `quota` variant (`--provider model --model quota`, its `until`
an hour after the launch), `schedule: off`. The hour a limit ends is moved in the journal while the team rests
(`until_set`), never the clock: every launch past the limit meets it again, an hour later.
- (a) until: qa's launch on T1 ends on the limit -- ONE `quota-reached`, no `wake-ended`, no `wake-failed`, no notice,
  qa not suspected; T2 posted to qa launches nobody, nor a tick; `status --json` says `members[qa].quota {until, said,
  at}` and `log --json` the `quota-reached`; its `until` moved a minute into the past, a tick launches qa ONCE again --
  it meets the limit again, which holds it
- (b) no until: the last `quota-reached` without its `until` (`null`, a harness that says no hour): a tick launches
  nobody; `team resume --task T1` lifts it, qa is launched ONCE again
- (c) a season: the season stopped, a new one under the same provider and T1 resumed keep the limit -- the face says
  it, a tick launches nobody --; the next season that gives qa another provider, T1 resumed, (the witness, under claude's grammar) lifts it: the tick launches qa, which
  answers -- the limit was the old provider's
- (d) lifted (s.1811, team 1.35.11): the limit qa met in (b) holds an hour ahead -- a tick launches nobody; `team resume
  --quota --member zz` refuses `member-unknown`; `--quota` beside `--task`, and `--member` without `--quota`, are the
  usage; `team resume --quota --member qa --no-tick` writes ONE `quota-lifted {by, members: [qa]}`, said by `log --json`
  and by `log` as `quota-lifted qa · by <p>`; lifted, qa is held no more: `--quota --member qa` again refuses
  `quota-not-held`; the next tick launches qa once again; `team resume --quota` (the whole team) lifts it once more, qa
  launched again
- (e) a lift refused before any writing: `team resume --quota` on a team never declared (`team-unknown`), declared and
  never started (`team-not-started`), whose journal says a delete begun (`team-deleting`), and on q off season
  (`season-stopped`) -- rc 2 each, every journal byte-identical
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from tests.harness import support

T = support(__file__, "team")

AT = "2026-11-03T21:00:00+00:00"
GONE = [{"kind": "team-started", "agents": {"ga": "agents/ga"}, "reports": [], "root": "ga", "principals": [],
         "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None, "digest": "000000000000"},
        {"kind": "deleting", "by": "house"}]


def until_set(h, name: str, until: str | None) -> int | None:
    """The `until` of the team's last `quota-reached` written as given, while the team rests, every other field and id
    kept. -> the id of that event, None without one."""
    journal = h.journal_of(name)
    lines = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    last = max((each["id"] for each in lines if each.get("kind") == "quota-reached"), default=None)
    for each in lines:
        if each.get("id") == last:
            each["until"] = until
    journal.write_text("".join(json.dumps(each, ensure_ascii=False) + "\n" for each in lines), encoding="utf-8")
    return last


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind, all_ended = T.by_kind, T.all_ended
    h.declare("q", "---\nagents: |\n  qa agents/qa\nroot: qa\nschedule: off\n---\nWork while the provider lets you.\n")
    started = h.call("team", "start", "q", "--message", "work T1", "--provider", "model", "--model", "quota")
    stopped = lambda found: (bool(by_kind(found, "quota-reached")) or bool(by_kind(found, "wake-ended"))
                             or bool(by_kind(found, "wake-failed"))) and all_ended(found)
    first = h.settled("q", stopped, 30)

    # --- (a) until ----------------------------------------------------------------------------------------------
    posted = h.call("team", "post", "q", "--to", "qa", "--message", "work T2")
    before = h.call("team", "tick", "q")
    found = h.events("q")
    reached = by_kind(found, "quota-reached")
    one = reached[0] if reached else {}
    face = h.face("q")
    member = next((each for each in face.get("members") or [] if each.get("member") == "qa"), {})
    logged = [json.loads(line) for line in h.call("team", "log", "q", "--json").stdout.splitlines() if line.strip()]
    until = str(one.get("until") or "")
    launched = len(T.intents_of(found, "qa"))
    until_set(h, "q", (datetime.now(timezone.utc) - timedelta(minutes=1)).replace(microsecond=0).isoformat())
    past = h.call("team", "tick", "q")
    relaunched = h.settled("q", lambda each: len(by_kind(each, "quota-reached")) == 2 and all_ended(each), 30)
    relaunched = relaunched and len(T.intents_of(h.events("q"), "qa")) == 2
    if (started.returncode == 0 and posted.returncode == 0 and before.returncode == 0 and first and len(reached) == 1
            and one.get("agent") == "qa" and one.get("task") == "T1" and until and one.get("said")
            and not by_kind(found, "wake-ended") and not by_kind(found, "wake-failed")
            and not by_kind(found, "post", verb="notice") and member.get("health") is None and launched == 1
            and (member.get("quota") or {}).get("until") == until and (member.get("quota") or {}).get("said") == one.get("said")
            and (member.get("quota") or {}).get("at") and [each.get("event") for each in logged].count("quota-reached") == 1
            and past.returncode == 0 and relaunched):
        held("(a) until", f"qa's launch ends on the limit: quota-reached until {until}, no end, no failure, no notice, "
             "not suspected; T2 and a tick launch nobody; the face says members[qa].quota, the log the event; until "
             "moved into the past, a tick launches qa once again")
    else:
        failures.append(f"  ✗ (a) until                    rc={started.returncode}/{posted.returncode}/{before.returncode}/"
                        f"{past.returncode} first={first} reached={reached} launched={launched} "
                        f"ended={by_kind(found, 'wake-ended')} failed={by_kind(found, 'wake-failed')} "
                        f"face={ {k: member.get(k) for k in ('quota', 'health')} } relaunched={relaunched} "
                        f"{started.stderr[-200:]!r}")

    # --- (b) no until -------------------------------------------------------------------------------------------
    last = until_set(h, "q", None)
    held_b = h.call("team", "tick", "q")
    count_b = len(T.intents_of(h.events("q"), "qa"))
    resumed = h.call("team", "resume", "q", "--task", "T1")
    again = h.settled("q", lambda each: len(by_kind(each, "quota-reached")) == 3 and all_ended(each), 30)
    again = again and len(T.intents_of(h.events("q"), "qa")) == 3
    if last is not None and held_b.returncode == 0 and count_b == 2 and resumed.returncode == 0 and again:
        held("(b) no until", "the last quota-reached without its until: a tick launches nobody; resume --task T1 "
             "lifts it, qa launched once again")
    else:
        failures.append(f"  ✗ (b) no until                 last={last} rc={held_b.returncode}/{resumed.returncode} "
                        f"intents={count_b} again={again} {resumed.stderr[-200:]!r}")

    # --- (d) lifted ---------------------------------------------------------------------------------------------
    held_d = h.call("team", "tick", "q")
    count_d = len(T.intents_of(h.events("q"), "qa"))
    unknown = h.call("team", "resume", "q", "--quota", "--member", "zz")
    mixed = h.call("team", "resume", "q", "--quota", "--task", "T1")
    bare = h.call("team", "resume", "q", "--member", "qa")
    one_lift = h.call("team", "resume", "q", "--quota", "--member", "qa", "--no-tick")
    not_held = h.call("team", "resume", "q", "--quota", "--member", "qa", "--no-tick")
    text_log = [line for line in h.call("team", "log", "q").stdout.splitlines() if "quota-lifted" in line]
    lift_tick = h.call("team", "tick", "q")
    lifted_one = h.settled("q", lambda each: len(by_kind(each, "quota-reached")) == 4 and all_ended(each), 30)
    lifts = by_kind(h.events("q"), "quota-lifted")
    logged_d = [json.loads(line) for line in h.call("team", "log", "q", "--json").stdout.splitlines() if line.strip()]
    team_lift = h.call("team", "resume", "q", "--quota")
    lifted_all = h.settled("q", lambda each: len(by_kind(each, "quota-reached")) == 5 and all_ended(each), 30)
    count_after = len(T.intents_of(h.events("q"), "qa"))
    lifts_after = by_kind(h.events("q"), "quota-lifted")
    if (held_d.returncode == 0 and count_d == 3 and unknown.returncode != 0 and "member-unknown" in unknown.stderr
            and mixed.returncode != 0 and "usage:" in mixed.stderr and bare.returncode != 0 and "usage:" in bare.stderr
            and not_held.returncode != 0 and "quota-not-held" in not_held.stderr
            and len(text_log) == 1 and "quota-lifted qa · by " in text_log[0] and lift_tick.returncode == 0
            and one_lift.returncode == 0 and lifted_one and len(lifts) == 1
            and lifts[0].get("members") == ["qa"] and lifts[0].get("by")
            and [each.get("event") for each in logged_d].count("quota-lifted") == 1
            and team_lift.returncode == 0 and lifted_all and len(lifts_after) == 2
            and lifts_after[1].get("members") == ["qa"] and count_after == 5):
        held("(d) lifted", "a dated limit: a tick launches nobody; resume --quota --member qa writes quota-lifted, "
             f"said by the log ({text_log[0].strip()!r}); lifted, quota-not-held; the tick launches qa again; resume "
             "--quota lifts the whole team's; member-unknown; --quota with --task and --member alone, the usage")
    else:
        failures.append(f"  ✗ (d) lifted                   rc={held_d.returncode}/{unknown.returncode}/{mixed.returncode}/"
                        f"{bare.returncode}/{one_lift.returncode}/{not_held.returncode}/{lift_tick.returncode}/"
                        f"{team_lift.returncode} count={count_d}->{count_after} text_log={text_log} "
                        f"usage={'usage:' in mixed.stderr}/{'usage:' in bare.stderr} {not_held.stderr[-200:]!r} "
                        f"lifted={lifted_one}/{lifted_all} lifts={lifts_after} "
                        f"{one_lift.stderr[-200:]!r} {unknown.stderr[-200:]!r}")

    # --- (c) a season ---------------------------------------------------------------------------------------------
    h.off_season("q")                                    # the season stopped, T1 with it; resumed in the next
    same = h.call("team", "start", "q", "--no-tick")
    h.call("team", "resume", "q", "--task", "T1", "--no-tick")
    kept_tick = h.call("team", "tick", "q")
    kept = len(T.intents_of(h.events("q"), "qa"))
    kept_face = next((each for each in h.face("q").get("members") or [] if each.get("member") == "qa"), {})
    h.off_season("q")
    other = h.call("team", "start", "q", "--no-tick", *h.harnessed)
    h.call("team", "resume", "q", "--task", "T1", "--no-tick")
    lifted_tick = h.call("team", "tick", "q")
    answered = h.settled("q", lambda each: bool(by_kind(each, "wake-ended", agent="qa")) and all_ended(each), 30)
    lifted_face = next((each for each in h.face("q").get("members") or [] if each.get("member") == "qa"), {})
    if (all(call.returncode == 0 for call in (same, kept_tick, other, lifted_tick)) and kept == 5
            and kept_face.get("quota") is not None and answered and lifted_face.get("quota") is None
            and len(T.intents_of(h.events("q"), "qa")) >= 6):
        held("(c) a season", "the same provider's season keeps the limit, a tick launches nobody; a season under "
             "another provider lifts it: qa launched, it answers")
    else:
        failures.append(f"  ✗ (c) a season                 rc={[c.returncode for c in (same, kept_tick, other, lifted_tick)]} "
                        f"kept={kept} kept_quota={kept_face.get('quota')} answered={answered} "
                        f"lifted_quota={lifted_face.get('quota')} intents={len(T.intents_of(h.events('q'), 'qa'))} "
                        f"{other.stderr[-200:]!r}")
    # --- (e) a lift refused before any writing ------------------------------------------------------------------
    h.declare("unborn", "---\nagents: |\n  ua agents/ua\nroot: ua\nschedule: off\n---\nNever started.\n")
    h.declare("gone", "---\nagents: |\n  ga agents/ga\nroot: ga\nschedule: off\n---\nBeing deleted.\n")
    h.written("gone", GONE, AT)
    h.off_season("q")
    journals = {name: (h.journal_of(name).read_bytes() if h.journal_of(name).exists() else None)
                for name in ("unborn", "gone", "q")}
    lifts_e = {name: h.call("team", "resume", name, "--quota") for name in ("nope", "unborn", "gone", "q")}
    codes_e = {name: (call.returncode, T.refusal_code(call.stderr)) for name, call in lifts_e.items()}
    same_e = all((h.journal_of(name).read_bytes() if h.journal_of(name).exists() else None) == before
                 for name, before in journals.items())
    if codes_e == {"nope": (2, "team-unknown"), "unborn": (2, "team-not-started"), "gone": (2, "team-deleting"),
                   "q": (2, "season-stopped")} and same_e:
        held("(e) a lift refused before any writing", f"{codes_e}; every journal byte-identical")
    else:
        failures.append(f"  ✗ (e) a lift refused            codes={codes_e} same={same_e} "
                        f"{[call.stderr.strip()[-120:] for call in lifts_e.values()]}")
    return 0
