"""Scenario `team-info-wakes` -- 2 case(s) (batch le-message-info, team 0.47.0; study § 19, row 114): the infos
that WAKE, and the answer nobody gives.
- (c) a principal's info wakes: `post --task` without `--reply` writes `{verb: info}` and the member is launched with
  it at its head; `resume --task` writes an `info` to the member it revives; the team's word on a refused act is an
  `info` (`wake-refused`, then the launch goes on)
- (d) a `re` that cites an info is refused by its name (`answers an info`), nothing posted, the launch goes on
"""
from __future__ import annotations

import json
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "q": [{"sleep": 0.1, "body": {"re": "DO", "text": "ok"}}],
        "b": [{"sleep": 0.1, "body": []}, {"sleep": 0.1, "body": {"re": "DO", "text": "back"}}],
        "t": [{"sleep": 0.1, "body": [{"do": {"nobody": "x"}}]}, {"sleep": 0.1, "body": {"re": "DO", "text": "fine"}}],
        "c": [{"sleep": 0.1, "body": [{"re": "INFO", "text": "noted"}, {"re": "DO", "text": "ok"}]},
              {"sleep": 0.1, "body": {"re": "DO", "text": "ok at last"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    h.declare("posted", "---\nagents: |\n  q agents/q\nroot: q\nschedule: off\n---\nRead the owner.\n")
    h.declare("back", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\n---\nTaken back.\n")
    h.declare("told", "---\nagents: |\n  t agents/t\nroot: t\nschedule: off\n---\nA stray act.\n")
    h.declare("cite", "---\nagents: |\n  c agents/c\nroot: c\nschedule: off\n---\nNever answer an info.\n")
    started = {"told": h.call("team", "start", "told", "--message", "do it", *h.harnessed)}
    quiet = {name: h.call("team", "start", name, "--message", "do it", "--no-tick", *h.harnessed)
             for name in ("posted", "back", "cite")}

    # --- (c) a principal's info wakes; resume and a refused act write info --------------------------------------
    posted = h.call("team", "post", "posted", "--task", "T1", "--message", "the deadline moved")
    ticked_b = h.call("team", "tick", "back")
    cited = h.call("team", "post", "cite", "--task", "T1", "--message", "fyi")
    done_q = h.settled("posted", ended, timeout=60)
    found_q = h.events("posted")
    post_q = next((one for one in by_kind(found_q, "post", verb="info")), {})
    intents_q = [(one.get("agent"), one.get("messages")) for one in by_kind(found_q, "wake-intent")]
    prompt_q = h.prompts_of("q")
    stood = h.settled("back", lambda found: bool(by_kind(found, "wake-ended", agent="b")), timeout=60)
    stopped = h.call("team", "stop", "back", "--task", "T1")
    resumed = h.call("team", "resume", "back", "--task", "T1", "--message", "go on")
    done_b = h.settled("back", ended, timeout=60)
    found_b = h.events("back")
    mark = next((one["id"] for one in by_kind(found_b, "resumed")), 10 ** 9)
    info_b = [(one.get("from"), one.get("to"), one.get("text")) for one in by_kind(found_b, "post", verb="info")
              if one["id"] > mark]
    done_t = h.settled("told", ended, timeout=60)
    found_t = h.events("told")
    refused_t = [str(one.get("why")) for one in by_kind(found_t, "wake-refused", agent="t")]
    info_t = [(one.get("from"), one.get("to")) for one in by_kind(found_t, "post", verb="info")]
    if (quiet["posted"].returncode == 0 and posted.returncode == 0 and done_q
            and (post_q.get("from"), post_q.get("to"), post_q.get("text")) == ("house", "q", "the deadline moved")
            and len(intents_q) == 1 and post_q["id"] in intents_q[0][1]
            and len(prompt_q) == 1 and f"#{post_q['id']} INFO from house on T1" in prompt_q[0]
            and result_of(found_q, "T1") == "ok"
            and quiet["back"].returncode == 0 and ticked_b.returncode == 0 and stood and stopped.returncode == 0
            and resumed.returncode == 0 and done_b and info_b == [("house", "b", "go on")]
            and result_of(found_b, "T1") == "back"
            and started["told"].returncode == 0 and done_t and len(refused_t) == 1 and "nobody" in refused_t[0]
            and info_t == [("told", "t")] and result_of(found_t, "T1") == "fine"):
        held("(c) a principal's info wakes", f"post --task wrote info #{post_q['id']} house -> q, q launched with it at "
             f"its head ('INFO from house'); resume wrote info house -> b; the refused act of t got the team's info; "
             "T1 ok / back / fine")
    else:
        failures.append(f"  ✗ (c) a principal's info       rc={quiet['posted'].returncode}/{posted.returncode}/"
                        f"{quiet['back'].returncode}/{ticked_b.returncode}/{stopped.returncode}/{resumed.returncode} "
                        f"done={done_q}/{done_b}/{done_t} post_q={post_q} intents_q={intents_q} prompts={len(prompt_q)} "
                        f"info_b={info_b} refused_t={refused_t} info_t={info_t} "
                        f"results={result_of(found_q, 'T1')!r}/{result_of(found_b, 'T1')!r}/{result_of(found_t, 'T1')!r} "
                        f"{posted.stderr.strip()[-150:]!r} {resumed.stderr.strip()[-150:]!r}")

    # --- (d) a re that cites an info is refused -------------------------------------------------------------------
    done_c = h.settled("cite", ended, timeout=60)
    found_c = h.events("cite")
    info_c = next((one["id"] for one in by_kind(found_c, "post", verb="info", **{"from": "house"})), None)
    refused_c = [str(one.get("why")) for one in by_kind(found_c, "wake-refused", agent="c")]
    told_c = [(one.get("from"), one.get("to")) for one in by_kind(found_c, "post", verb="info") if one.get("from") == "cite"]
    posted_c = [one["id"] for one in by_kind(found_c, "post", verb="re", **{"from": "c"})]
    if (quiet["cite"].returncode == 0 and cited.returncode == 0 and done_c and info_c is not None
            and len(refused_c) == 1 and f"re #{info_c} answers an info" in refused_c[0]
            and told_c == [("cite", "c")] and len(posted_c) == 1 and len(T.intents_of(found_c, "c")) == 2
            and not by_kind(found_c, "wake-failed") and result_of(found_c, "T1") == "ok at last"):
        held("(d) a re to an info is refused", f"c's act [re #{info_c}, re DO] refused ('{refused_c[0][:40]}…'), nothing "
             "posted, the team's info to c; its next launch answers: T1 'ok at last', no failure")
    else:
        failures.append(f"  ✗ (d) a re to an info          rc={quiet['cite'].returncode}/{cited.returncode} done={done_c} "
                        f"info={info_c} refused={refused_c} told={told_c} posted={posted_c} "
                        f"intents={len(T.intents_of(found_c, 'c'))} fails={by_kind(found_c, 'wake-failed')} "
                        f"result={result_of(found_c, 'T1')!r}")

    return 0
