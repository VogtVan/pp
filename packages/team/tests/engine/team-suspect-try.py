"""Scenario `team-suspect-try` -- 2 case(s) (cut out of `team-suspect`, rule 10): the TRY of a suspected member and
the health view. One team, `pair` (r1, r2) under `retries: 1`: r2 dies twice on r1's `do` (T1) and is suspected.
- (b) the try and the interval doubled: `PP_NOW` past the interval, T2's `do` to r2 wakes it -- its try --, it dies
  once and its failure is final at once (no silent retry for a suspected member); the next interval is the double
- (c) the health view: while r2 is suspected, the head of r1's wake-ups says `[not answering at the moment: r2 --
  tried again at HH:MM]` -- none before r2 fell, the first interval's hour at the end of T1 and at T2's opening, the
  doubled one once its try failed
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "r1": {task: [{"sleep": 0.1, "body": {"do": ["r2"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": f"{task} done"}}]
               for task in ("T1", "T2")},
        "r2": {"T1": [T.DEATH, T.DEATH], "T2": [T.DEATH]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    closed = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)
    health_line = T.health_pattern(h.module())

    h.declare("pair", T.SUSPECT_PAIR.format(a="r1", b="r2"))
    started = h.call("team", "start", "pair", "--message", "build it", *h.harnessed)
    T.ticked(h, [("pair", closed("T1"), None)])
    first = T.finals_of(h.events("pair"), "r2")
    hour = T.local_after(first[0]["at"], 5).strftime("%H:%M:%S") if first else "?"
    later = T.local_after(first[0]["at"], 6).isoformat(timespec="seconds") if first else None
    posted = h.call("team", "post", "pair", "--message", "second part", now=later)
    T.ticked(h, [("pair", closed("T2"), later)])
    found = h.events("pair")

    # --- (b) the try after the interval, final at once, the interval doubled ----------------------------------
    tried = T.intents_on(found, "r2", "T2")
    second = [one for one in T.finals_of(found, "r2") if one.get("task") == "T2"]
    doubled = T.local_after(second[0]["at"], 10).strftime("%H:%M:%S") if second else "?"
    if (started.returncode == 0 and posted.returncode == 0 and len(first) == 1 and len(tried) == 1 and len(second) == 1
            and not [one for one in by_kind(found, "wake-failed", agent="r2", task="T2") if not one.get("final")]
            and result_of(found, "T2") == "T2 done"):
        held("(b) the try, the interval doubled", f"PP_NOW past {hour}: T2's do wakes r2 once -- its try --, it dies and "
             f"its failure is final at once; tried again at {doubled} (2 x 5 min); T2 'T2 done'")
    else:
        failures.append(f"  ✗ (b) the try                  rc={started.returncode}/{posted.returncode} finals={len(first)} "
                        f"tried={len(tried)} second={len(second)} result={result_of(found, 'T2')!r} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found]}")

    # --- (c) the health view in r1's heads ---------------------------------------------------------------------
    heads = [health_line.findall(one) for one in h.prompts_of("r1")]
    expected = [[], [("r2", hour)], [("r2", hour)], [("r2", doubled)]]
    if heads == expected:
        held("(c) the health view", f"r1's heads: none before r2 fell, then 'r2 -- tried again at {hour}' at the end of "
             f"T1 and at T2's opening, 'at {doubled}' after its try failed")
    else:
        failures.append(f"  ✗ (c) the health view          heads={heads} expected={expected}")
    return 0
