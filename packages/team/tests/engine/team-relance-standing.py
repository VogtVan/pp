"""Scenario `team-relance-standing` -- 2 case(s) (cut out of `team-relance`, rule 10): a run that STANDS is continued,
never relanced, and `launches:` alone bounds its continuations; two teams play side by side on one house.
- (c) a STANDING debtor is continued, not relanced: st, whose entry cuts two acts by a `§`, says an `info` in its first
  launch and stands (`wake-ended {state: standing}`) while it still owes the opening; the tick relaunches its run on
  T1 as a continuation -- no `relance` on the intent, which says `continued` and keeps no beat, the head opening on
  the module's NOTHING_NEW, never on RELANCED, and without the identity line a wake-up's head opens on --, it answers
  the opening there, and T1 resolves
- (d) a STANDING member that says nothing is continued while it does not park (batch le-battement-du-reveil): under
  `silence: 1` and `launches: 5`, ms stands at every `§` of its entry and says prose alone; its opening launch and
  four continuations, `continued` and no beat on each -- no `silence`: a continuation counts for nothing --, then
  `launches-spent` on T1 (5 of 5), the team's notice to house, and no intent more through two ticks
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # stand: st says an info, stands at the § of its entry, then answers the opening
        "st": [{"sleep": 0.1, "body": {"info": {"to": "house", "text": "working on it"}}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "stood and done"}}],
        # mutestand: ms stands at every § of its entry and says prose alone
        "ms": [{"sleep": 0.1, "body": "prose"}] * 8})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    ended = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
    relanced = h.module().RELANCED
    limit = getattr(h.module(), "DEFAULT_SILENCE", 3)

    h.declare("stand", "---\nagents: |\n  st agents/st\nroot: st\nentries: |\n  do -> ACTS.md\nschedule: off\n---\n"
                       "Say where you stand, then conclude.\n")
    (h.teams / "stand" / "ACTS.md").write_text("---\nproc: |\n  INFER\n  §\n  INFER\noutput: team-act\n---\n"
                                              "# ACTS\n\nSay one act at each step.\n", encoding="utf-8")
    h.declare("mutestand", "---\nagents: |\n  ms agents/ms\nroot: ms\nentries: |\n  do -> STEPS.md\nschedule: off\n"
                           "silence: 1\nlaunches: 5\n---\nSay where you stand.\n")
    (h.teams / "mutestand" / "STEPS.md").write_text("---\nproc: |\n" + "  §\n".join(["  INFER\n"] * 8)
                                                   + "output: team-act\n---\n# STEPS\n\nSay one act at each step.\n",
                                                   encoding="utf-8")
    stand = h.call("team", "start", "stand", "--message", "stand, then answer", *h.harnessed)
    mutestand = h.call("team", "start", "mutestand", "--message", "stand and say", *h.harnessed)

    # --- (c) a standing debtor is continued, not relanced ------------------------------------------------------
    nothing_new = h.module().NOTHING_NEW
    done_st = h.settled("stand", ended, 60)
    found = h.events("stand")
    st = T.intents_of(found, "st")
    ends = [one.get("state") for one in by_kind(found, "wake-ended", agent="st")]
    prompts = h.prompts_of("st")
    head_1 = prompts[0].split("▌ pp · run", 1)[0] if prompts else ""
    head_2 = prompts[1].split("▌ pp · run", 1)[0] if len(prompts) > 1 else ""
    identity = T.identity_pattern(h.module())
    if (stand.returncode == 0 and done_st and len(st) == 2 and [one.get("relance") for one in st] == [None, None]
            and [(one.get("continued"), one.get("beat")) for one in st] == [(False, limit), (True, None)]
            and identity.findall(head_1) == [("stand", "st")] and not identity.findall(head_2)
            and ends[:1] == ["standing"] and nothing_new in head_2 and relanced not in head_2
            and result_of(found, "T1") == "stood and done" and h.module() is h.module()):
        held("(c) a standing debtor is continued", f"st says an info and stands (launch 1 standing) while it owes the "
             f"opening; relaunched as a continuation (continued, no beat, no relance, the head {nothing_new!r} without "
             "the identity line), it answers: T1 done")
    else:
        failures.append(f"  ✗ (c) standing debtor         rc={stand.returncode} done={done_st} "
                        f"relances={[one.get('relance') for one in st]} "
                        f"said={[(one.get('continued'), one.get('beat')) for one in st]} "
                        f"identity={identity.findall(head_1)}/{identity.findall(head_2)} ends={ends} head={head_2[:200]!r} "
                        f"result={result_of(found, 'T1')!r} once={h.module() is h.module()} {stand.stderr[-200:]!r}")

    # --- (d) a standing member that says nothing is continued until launches: ---------------------------------
    over = h.settled("mutestand", lambda found: bool(by_kind(found, "silence") or by_kind(found, "launches-spent"))
                     and all_ended(found), 60)
    ticks = [h.call("team", "tick", "mutestand") for _ in range(2)]
    found = h.events("mutestand")
    ms = T.intents_of(found, "ms")
    fell = [(one.get("agent"), one.get("task")) for one in by_kind(found, "silence")]
    gone = [(one.get("task"), one.get("spent"), one.get("launches")) for one in by_kind(found, "launches-spent")]
    told = [(one.get("from"), one.get("to"), one.get("about")) for one in by_kind(found, "post", verb="notice")]
    if (mutestand.returncode == 0 and over and all(one.returncode == 0 for one in ticks)
            and [(one.get("relance"), bool(one.get("messages")), one.get("continued"), one.get("beat")) for one in ms]
            == [(None, True, False, 1)] + [(None, False, True, None)] * 4
            and not fell and gone == [("T1", 5, 5)] and told == [("mutestand", "house", None)]):
        held("(d) a standing member is continued until launches:", "ms stands and says prose: its opening launch and four "
             "continuations (continued, no beat), no silence; then launches-spent on T1 (5 of 5) and the team's notice "
             "to house; no intent through 2 ticks")
    else:
        failures.append(f"  ✗ (d) standing member continued rc={mutestand.returncode} over={over} "
                        f"intents={[(one.get('relance'), one.get('messages'), one.get('continued'), one.get('beat')) for one in ms]} "
                        f"fell={fell} gone={gone} told={told} "
                        f"ends={[one.get('state') for one in by_kind(found, 'wake-ended', agent='ms')]}")
    return 0
