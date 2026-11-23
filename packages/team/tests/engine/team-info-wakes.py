"""Scenario `team-info-wakes` -- 3 case(s) (batch le-message-info, team 0.47.0; study § 19, row 114): the infos
that WAKE, and the answer nobody gives.
- (c) a principal's info wakes: `post --task` without `--reply` writes `{verb: info}` and the member is launched with
  it at its head; `resume --task` writes an `info` to the member it revives -- b's first launch holds at a gate until
  `stop --task` is posted: its end finds T1 stopped and relances nobody --; the team's word on a refused act is an
  `info` (`wake-refused`, then the launch goes on)
- (d) a `re` that cites an info is refused by its name (`answers an info`), nothing posted, the launch goes on
- (e) a principal's question (team 1.35.14, s.1816): `post --task --ask` writes `{verb: ask}` house -> k, a debt k
  owes; k's launch answers it by a `re` citing it, then closes T1; `stats --json` counts it under
  `principal.from_principal` (1 asked, 1 answered); `--ask` without `--task`, beside `--reply` or `--stop` is the
  usage, nothing written
"""
from __future__ import annotations

import json
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gate_b = bench.temp() / "back.gate"                  # (c): b's first launch holds here until T1 is stopped
    h = T.House(bench, script={
        "q": [{"sleep": 0.1, "body": {"re": "DO", "text": "ok"}}],
        "b": [{"sleep": 0.1, "words": [{"gate": str(gate_b)}, []]},
              {"sleep": 0.1, "body": {"re": "DO", "text": "back"}}],
        "t": [{"sleep": 0.1, "body": [{"do": {"nobody": "x"}}]}, {"sleep": 0.1, "body": {"re": "DO", "text": "fine"}}],
        "k": [{"sleep": 0.1, "body": [{"re": "ASK", "text": "v2"}, {"re": "DO", "text": "tagged"}]}],
        "c": [{"sleep": 0.1, "body": [{"re": "INFO", "text": "noted"}, {"re": "DO", "text": "ok"}]},
              {"sleep": 0.1, "body": {"re": "DO", "text": "ok at last"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    h.declare("posted", "---\nagents: |\n  q agents/q\nroot: q\nschedule: off\n---\nRead the owner.\n")
    h.declare("back", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\n---\nTaken back.\n")
    h.declare("told", "---\nagents: |\n  t agents/t\nroot: t\nschedule: off\n---\nA stray act.\n")
    h.declare("cite", "---\nagents: |\n  c agents/c\nroot: c\nschedule: off\n---\nNever answer an info.\n")
    h.declare("quiz", "---\nagents: |\n  k agents/k\nroot: k\nschedule: off\n---\nAnswer the owner.\n")
    started = {"told": h.call("team", "start", "told", "--message", "do it", *h.harnessed)}
    quiet = {name: h.call("team", "start", name, "--message", "do it", "--no-tick", *h.harnessed)
             for name in ("posted", "back", "cite", "quiz")}

    # --- (c) a principal's info wakes; resume and a refused act write info --------------------------------------
    posted = h.call("team", "post", "posted", "--task", "T1", "--message", "the deadline moved")
    ticked_b = h.call("team", "tick", "back")
    cited = h.call("team", "post", "cite", "--task", "T1", "--message", "fyi")
    done_q = h.settled("posted", ended, timeout=60)
    found_q = h.events("posted")
    post_q = next((one for one in by_kind(found_q, "post", verb="info")), {})
    intents_q = [(one.get("agent"), one.get("messages")) for one in by_kind(found_q, "wake-intent")]
    prompt_q = h.prompts_of("q")
    held_b = h.settled("back", lambda found: bool(by_kind(found, "wake-launched", agent="b")), timeout=60)
    stopped = h.call("team", "stop", "back", "--task", "T1")
    gate_b.write_text("go", encoding="utf-8")
    stood = h.settled("back", lambda found: bool(by_kind(found, "wake-ended", agent="b")), timeout=60)
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
            and quiet["back"].returncode == 0 and ticked_b.returncode == 0 and held_b and stood
            and stopped.returncode == 0
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

    # --- (e) a principal's question: an ask, an answer due ---------------------------------------------------------
    before_e = h.journal_of("quiz").read_bytes()
    misused = [h.call("team", "post", "quiz", *args, "--message", "which tag?", "--no-tick")
               for args in (("--ask",), ("--task", "T1", "--ask", "--reply", "2"), ("--task", "T1", "--ask", "--stop"))]
    same_e = h.journal_of("quiz").read_bytes() == before_e
    quizzed = h.call("team", "post", "quiz", "--task", "T1", "--ask", "--message", "which tag?")
    closed_e = h.settled("quiz", ended, 60)
    found_e = h.events("quiz")
    asked_e = by_kind(found_e, "post", verb="ask")
    answers_e = [one for one in by_kind(found_e, "post", verb="re", **{"from": "k"})
                 if asked_e and one.get("re") == asked_e[0]["id"]]
    counted_e = h.call("team", "stats", "quiz", "--json")
    try:
        loop_e = json.loads(counted_e.stdout)["season"]["principal"]["from_principal"]
    except (ValueError, KeyError, TypeError):
        loop_e = None
    if (all(one.returncode == 2 and "usage" in one.stderr for one in misused) and same_e and quizzed.returncode == 0
            and closed_e and [(one.get("from"), one.get("to"), one.get("text")) for one in asked_e]
            == [("house", "k", "which tag?")] and len(answers_e) == 1 and answers_e[0].get("text") == "v2"
            and result_of(found_e, "T1") == "tagged"
            and loop_e is not None and (loop_e["asked"], loop_e["answered"]) == (1, 1)):
        held("(e) a principal's question", f"--ask wrote ask #{asked_e[0]['id']} house -> k, k answered it (re "
             f"#{answers_e[0]['id']}) and closed T1; stats: from_principal {loop_e}; --ask without --task, with --reply, "
             "with --stop: the usage, nothing written")
    else:
        failures.append(f"  ✗ (e) a principal's question  misused={[(one.returncode, one.stderr[-60:]) for one in misused]} "
                        f"same={same_e} rc={quizzed.returncode} closed={closed_e} asked={asked_e} answers={answers_e} "
                        f"result={result_of(found_e, 'T1')!r} loop={loop_e} {counted_e.stderr[-200:]!r} "
                        f"{quizzed.stderr[-200:]!r}")
    return 0
