"""Scenario `team-continuation` -- 5 case(s): the continuation of a standing run (batch la-continuation-par-tache);
three teams play side by side on one house, each member's entry cutting its acts by a `§`; the old runs standing
on closed tasks are `team-continuation-closed`, a changed model alone `team-continuation-model` (rule 10).
- (a) an answer that arrives before the continuation waits for the launch after it (s.1377): ea delegates to ed in
  its first launch -- its entry puts that act ahead of the output's last step, so it is handed by its print call
  and routed at once -- and plays on, held at a gate the case opens once ed's answer stands in the journal; ea stands on
  its second act. The first launch after that
  stand is a continuation -- `messages: []`, `[nothing new]` at its head, ed's answer not there --; ed's `re` is
  delivered to the launch after, whose act answers the opening: T1 done
- (b) a run standing on a CLOSED task is continued until it parks (s.1404): cl answers the opening in its first
  launch -- T1 resolved -- and stands on its second act; the tick continues its run all the same, `messages: []`, no
  relance, the head opening on the module's CLOSED_HEAD; it says an `info` and parks -- no launch more through two
  ticks
- (c) nothing is delivered to a run that stands, however many launches its passage takes (s.1377, seen on a real
  team on 2026-11-10): eb's entry cuts THREE acts; it delegates to ef and stands, plays its second act -- held at a
  gate until ef's answer stands in the journal -- and stands AGAIN; its third launch is a continuation still -- `messages: []`, `[nothing new]`, ef's answer
  not there -- and parks; ef's `re` opens the launch after, a turn of its own, whose act answers the opening
- (d) a season that changes a member's model opens it a new run (s.1569): sm (T1) and sk (T2) start under `--model m1`,
  each `wake-launched` keeping the run's `model` and `provider`; each asks the owner and parks; the season stopped, a
  new one gives sm `--model m2`, T1 and T2 resumed; the owner's answers wake them: sm gets `run-renewed {why: model}` and a NEW run, launched under m2, whose
  head opens on T1's history; sk resumes its run under m1
- (e) a season that changes the PROVIDER of a member whose run stands renews it at once: sv's first launch, under
  claude, holds at a gate; the season stopped, a new one gives sv `--provider codex`, T1 resumed; the gate opens, sv says its first act and stands;
  its next launch is no continuation of that run under another provider: `run-renewed {why: model, was.provider
  claude, now.provider codex}`, a NEW run under codex whose head opens on T1's history, continued then under codex,
  whose act answers the opening: T1 done -- no launch failed
"""
from __future__ import annotations

import re
import time

from tests.harness import support

T = support(__file__, "team")

ACTS = "---\nproc: |\n  INFER\n  §\n  INFER\noutput: team-act\n---\n# ACTS\n\nSay one act at each step.\n"
HISTORY = re.compile(r"^\[history of (\S+) for (\S+)\]$", re.M)   # the head of a new run's history (team-reset)
OPENING_E = 3                                    # (e): the start's `do`, after `team-started` and `task`
AHEAD = ("---\nproc: |\n  INFER\n  INFER\n  §\n  INFER\noutput: team-act\n---\n# AHEAD\n\n"
         "Say one act at each step.\n")    # its first act stands ahead of the output's last step: said to pp by its
# print call, it is routed while the launch plays on
THREE = "---\nproc: |\n  INFER\n  §\n  INFER\n  §\n  INFER\noutput: team-act\n---\n# THREE\n\nSay one act at each step.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gate_e = bench.temp() / "sv.gate"                    # (e): sv's first launch waits for it
    gate_a = bench.temp() / "ea.gate"                    # (a): ea plays on until ed's answer stands in the journal
    gate_c = bench.temp() / "eb.gate"                    # (c): eb plays its second act until ef's answer stands
    h = T.House(bench, script={
        # (a) ea delegates and plays on, at a gate, until ed answered; it stands, proves, then concludes on ed's answer
        "ea": [{"words": [{"do": ["ed"]}, {"gate": str(gate_a)}]},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "the proof played"}}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "T1 on ed's answer"}}],
        "ed": [{"sleep": 0.1, "body": {"done": "ed's part"}},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "ed's proof"}}}],
        # (c) eb delegates and stands, plays its second act at a gate until ef answered and stands again, parks at its third;
        # ef's answer opens the launch after
        "eb": [{"sleep": 0.1, "body": {"do": ["ef"]}},
               {"words": [{"gate": str(gate_c)}, {"info": {"to": "house", "text": "the second act"}}]},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "the proof played"}}},
               {"sleep": 0.1, "body": {"re": "DO", "text": "T1 on ef's answer"}}],
        "ef": [{"sleep": 1.5, "body": {"done": "ef's part"}},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "ef's second act"}}},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "ef's proof"}}}],
        # (b) cl closes T1 in its first act and stands; its continuation says an info
        "cl": [{"sleep": 0.1, "body": {"re": "DO", "text": "closed first"}},
               {"sleep": 0.1, "body": {"info": {"to": "house", "text": "the proof played"}}}],
        # (d) each asks the owner and parks; the owner's answer brings the launch that renews or resumes
        **{member: [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
                    {"sleep": 0.1, "body": {"done": member}}] for member in ("sm", "sk")},
        # (e) sv holds at a gate under claude, then stands; its runs after speak codex
        "sv": [{"words": [{"gate": str(gate_e)}, {"info": {"to": "house", "text": "the first act"}}]},
               {"grammar": "codex", "sleep": 0.1, "body": {"info": {"to": "house", "text": "renewed"}}},
               {"grammar": "codex", "sleep": 0.1, "body": {"re": OPENING_E, "text": "T1 under codex"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    module = h.module()
    nothing_new, closed_head = module.NOTHING_NEW, getattr(module, "CLOSED_HEAD", None)

    # --- both teams declared and started side by side ------------------------------------------------------
    h.declare("early", "---\nagents: |\n  ea agents/ea\n  ed agents/ed\nreports: |\n  ed -> ea\nroot: ea\n"
                       "entries: |\n  do -> AHEAD.md\nschedule: off\n---\nDelegate, prove, then conclude.\n")
    (h.teams / "early" / "AHEAD.md").write_text(AHEAD, encoding="utf-8")
    h.declare("closing", "---\nagents: |\n  cl agents/cl\nroot: cl\nentries: |\n  do -> ACTS.md\nschedule: off\n---\n"
                         "Conclude, then prove.\n")
    (h.teams / "closing" / "ACTS.md").write_text(ACTS, encoding="utf-8")
    h.declare("thrice", "---\nagents: |\n  eb agents/eb\n  ef agents/ef\nreports: |\n  ef -> eb\nroot: eb\n"
                        "entries: |\n  do -> THREE.md\nschedule: off\n---\nDelegate, act, prove, then conclude.\n")
    (h.teams / "thrice" / "THREE.md").write_text(THREE, encoding="utf-8")
    early = h.call("team", "start", "early", "--message", "delegate, prove, conclude", *h.harnessed)
    thrice = h.call("team", "start", "thrice", "--message", "delegate, act, prove, conclude", *h.harnessed)
    closing = h.call("team", "start", "closing", "--message", "conclude, then prove", *h.harnessed)
    h.declare("swap", "---\nagents: |\n  sm agents/s\n  sk agents/s\nroot: sm\nschedule: off\n---\nAsk, then answer.\n")
    swap = h.call("team", "start", "swap", "--message", "work T1", *h.harnessed,
                  "--member", "sm", "--model", "m1", "--member", "sk", "--model", "m1")
    swap_posted = h.call("team", "post", "swap", "--to", "sk", "--message", "work T2")
    h.declare("move", "---\nagents: |\n  sv agents/v\nroot: sv\nentries: |\n  do -> ACTS.md\nschedule: off\n---\n"
                      "Act, then act again.\n")
    (h.teams / "move" / "ACTS.md").write_text(ACTS, encoding="utf-8")
    move = h.call("team", "start", "move", "--message", "act twice", *h.harnessed)
    held_e = h.settled("move", lambda found: bool(by_kind(found, "wake-launched", agent="sv")), 20)
    h.off_season("move")                                 # the season stopped: T1 with it, sv's launch under way
    season_e = h.call("team", "start", "move", "--no-tick", "--member", "sv", "--provider", "codex")
    h.call("team", "resume", "move", "--task", "T1", "--no-tick")
    gate_e.write_text("open", encoding="utf-8")

    # the answers ea and eb play through: each gate opens on the answer's post, whatever the machine's load
    answered = lambda member: lambda found: bool(by_kind(found, "post", verb="re", **{"from": member}))
    heard_a = h.settled("early", answered("ed"), 40)
    gate_a.write_text("open", encoding="utf-8")
    heard_c = h.settled("thrice", answered("ef"), 40)
    gate_c.write_text("open", encoding="utf-8")

    # --- (b) a run standing on a closed task is continued until it parks -------------------------------------
    parked = h.settled("closing", lambda found: "parked" in [one.get("state") for one in by_kind(found, "wake-ended")]
                       and all_ended(found), 20)
    ticks = [h.call("team", "tick", "closing") for _ in range(2)]
    found = h.events("closing")
    cl = T.intents_of(found, "cl")
    ends = [one.get("state") for one in by_kind(found, "wake-ended", agent="cl")]
    done_b = next((one["id"] for one in by_kind(found, "done", task="T1")), 10 ** 9)
    prompts = h.prompts_of("cl")
    head_2 = prompts[1].split("▌ pp · run", 1)[0] if len(prompts) > 1 else ""
    said = [one.get("text") for one in by_kind(found, "post", verb="info", **{"from": "cl"})]
    if (closing.returncode == 0 and parked and all(one.returncode == 0 for one in ticks)
            and [(one.get("relance"), bool(one.get("messages"))) for one in cl] == [(None, True), (None, False)]
            and cl[1]["id"] > done_b and ends == ["standing", "parked"] and closed_head and closed_head in head_2
            and nothing_new not in head_2 and said == ["the proof played"]
            and result_of(found, "T1") == "closed first"):
        held("(b) a run standing on a closed task is continued", f"cl closes T1 (#{done_b}) and stands; continued all "
             f"the same (#{cl[1]['id']}, nothing delivered, the head {closed_head!r}), it says an info and parks; "
             "no launch more through 2 ticks")
    else:
        failures.append(f"  ✗ (b) standing on a closed task  rc={closing.returncode} parked={parked} "
                        f"intents={[(one.get('relance'), one.get('messages'), one['id']) for one in cl]} done={done_b} "
                        f"ends={ends} closed_head={closed_head!r} head={head_2[:200]!r} said={said} "
                        f"result={result_of(found, 'T1')!r}")

    # --- (a) an answer that arrives before the continuation waits for the launch after it ---------------------
    done_a = h.settled("early", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40)
    time.sleep(0.5)
    found_a = h.events("early")
    ea = T.intents_of(found_a, "ea")
    ends_ea = [one.get("state") for one in by_kind(found_a, "wake-ended", agent="ea")]
    stood = next((one["id"] for one in by_kind(found_a, "wake-ended", agent="ea")), 0)
    re_ed = next((one["id"] for one in by_kind(found_a, "post", verb="re", **{"from": "ed"})), None)
    heads_ea = [one.split("▌ pp · run", 1)[0] for one in h.prompts_of("ea")]
    cites_ed = lambda head: re_ed is not None and re.search(rf"^#{re_ed} RE #\d+ from ed on T1", head, re.M) is not None
    shape_a = [(one.get("relance"), one.get("messages")) for one in ea]
    if (early.returncode == 0 and heard_a and done_a and re_ed is not None and re_ed < stood and len(ea) >= 3
            and ends_ea[:2] == ["standing", "parked"] and shape_a[1] == (None, [])
            and len(heads_ea) >= 3 and nothing_new in heads_ea[1] and not cites_ed(heads_ea[1])
            and shape_a[2] == (None, [re_ed]) and cites_ed(heads_ea[2])
            and result_of(found_a, "T1") == "T1 on ed's answer"):
        held("(a) an answer before the continuation waits", f"ed's re #{re_ed} arrives while ea plays; ea stands "
             f"(#{stood}); its continuation delivers nothing ({nothing_new!r}), it plays the proof and parks; the "
             "launch after delivers the re, whose act answers the opening: T1 done")
    else:
        failures.append(f"  ✗ (a) answer before continuation  rc={early.returncode} heard={heard_a} done={done_a} re={re_ed} stood={stood} "
                        f"intents={shape_a} ends={ends_ea} nothing_new={[nothing_new in one for one in heads_ea]} "
                        f"cites={[cites_ed(one) for one in heads_ea]} result={result_of(found_a, 'T1')!r}")

    # --- (c) nothing is delivered to a run that stands, however many launches its passage takes ---------------
    done_c = h.settled("thrice", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found_c = h.events("thrice")
    eb = T.intents_of(found_c, "eb")
    ends_eb = [one.get("state") for one in by_kind(found_c, "wake-ended", agent="eb")]
    re_ef = next((one["id"] for one in by_kind(found_c, "post", verb="re", **{"from": "ef"})), None)
    heads_eb = [one.split("▌ pp · run", 1)[0] for one in h.prompts_of("eb")]
    cites_ef = lambda head: re_ef is not None and re.search(rf"^#{re_ef} RE #\d+ from ef on T1", head, re.M) is not None
    shape_c = [(one.get("relance"), one.get("messages")) for one in eb]
    if (thrice.returncode == 0 and heard_c and done_c and re_ef is not None and len(eb) >= 4 and re_ef < eb[2]["id"]
            and ends_eb[:3] == ["standing", "standing", "parked"]
            and shape_c[1] == (None, []) and shape_c[2] == (None, []) and len(heads_eb) >= 4
            and nothing_new in heads_eb[2] and not cites_ef(heads_eb[2])
            and shape_c[3] == (None, [re_ef]) and cites_ef(heads_eb[3])
            and result_of(found_c, "T1") == "T1 on ef's answer"):
        held("(c) nothing is delivered to a run that stands", f"ef's re #{re_ef} arrives while eb plays its second act; "
             f"eb stands twice; its third launch (#{eb[2]['id']}) is a continuation still ({nothing_new!r}) and parks; "
             f"the launch after (#{eb[3]['id']}) delivers the re, a turn of its own: T1 done")
    else:
        failures.append(f"  ✗ (c) delivered to a standing run  rc={thrice.returncode} heard={heard_c} done={done_c} re={re_ef} "
                        f"intents={[(one['id'], *shape) for one, shape in zip(eb, shape_c)]} ends={ends_eb} "
                        f"nothing_new={[nothing_new in one for one in heads_eb]} "
                        f"cites={[cites_ef(one) for one in heads_eb]} result={result_of(found_c, 'T1')!r}")

    # --- (d) a season that changes a member's model opens it a new run -----------------------------------------
    asked_d = h.settled("swap", lambda found: len(by_kind(found, "post", verb="ask", to="house")) == 2
                        and all_ended(found), 40)
    h.off_season("swap")                                 # the season stopped: T1 and T2 with it
    season_d = h.call("team", "start", "swap", "--no-tick", "--member", "sm", "--model", "m2")
    for task in ("T1", "T2"):
        h.call("team", "resume", "swap", "--task", task, "--no-tick")
    answers_d = [h.call("team", "post", "swap", "--task", one.get("task"), "--reply", str(one.get("id")), "--message", "main")
                 for one in by_kind(h.events("swap"), "post", verb="ask", to="house")]
    done_d = h.settled("swap", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), 40)
    found_d = h.events("swap")
    launched_d = {one.get("tag"): one for one in by_kind(found_d, "wake-launched")}
    runs_d = {member: [(one.get("run"), (launched_d.get(one.get("tag")) or {}).get("run"),
                        (launched_d.get(one.get("tag")) or {}).get("model"),
                        (launched_d.get(one.get("tag")) or {}).get("provider")) for one in T.intents_of(found_d, member)]
              for member in ("sm", "sk")}
    renewed_d = by_kind(found_d, "run-renewed")
    one_d = renewed_d[0] if renewed_d else {}
    heads_sm = [HISTORY.findall(prompt.split("▌ pp · run", 1)[0]) for prompt in h.prompts_of("sm")]
    sm, sk = runs_d["sm"], runs_d["sk"]
    if (swap.returncode == 0 and swap_posted.returncode == 0 and season_d.returncode == 0 and asked_d and done_d
            and len(answers_d) == 2 and all(one.returncode == 0 for one in answers_d)
            and len(sm) == 2 and len(sk) == 2
            and [(run, model, provider) for run, _, model, provider in sm] == [(None, "m1", "claude"), (None, "m2", "claude")]
            and sm[0][1] and sm[1][1] and sm[0][1] != sm[1][1]
            and [(run, key, model) for run, key, model, _ in sk] == [(None, sk[0][1], "m1"), (sk[0][1], sk[0][1], "m1")]
            and len(renewed_d) == 1 and one_d.get("member") == "sm" and one_d.get("why") == "model"
            and one_d.get("run") == sm[0][1] and one_d.get("task") == "T1"
            and heads_sm[:1] == [[]] and heads_sm[1:] == [[("T1", "sm")]]):
        held("(d) a changed model opens a new run", f"sm's run {sm[0][1]} opened under m1, the new season gives it m2: "
             f"run-renewed (why model), a new run {sm[1][1]} under m2 told T1's history; sk resumes {sk[0][1]} under m1")
    else:
        failures.append(f"  ✗ (d) a changed model           rc={swap.returncode}/{swap_posted.returncode}/{season_d.returncode} "
                        f"asked={asked_d} done={done_d} answers={[one.returncode for one in answers_d]} runs={runs_d} "
                        f"renewed={renewed_d} heads={heads_sm} {(swap.stderr + season_d.stderr)[-200:]!r}")

    # --- (e) a changed provider renews a standing run at once ------------------------------------------------
    done_e = h.settled("move", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
                       or len(by_kind(found, "wake-failed", agent="sv")) >= 2, 30)
    found_e = h.events("move")
    launched_e = {one.get("tag"): one for one in by_kind(found_e, "wake-launched")}
    sv = [(one.get("run"), (launched_e.get(one.get("tag")) or {}).get("run"),
           (launched_e.get(one.get("tag")) or {}).get("provider")) for one in T.intents_of(found_e, "sv")]
    ends_e = [one.get("state") for one in by_kind(found_e, "wake-ended", agent="sv")]
    renewed_e = by_kind(found_e, "run-renewed")
    one_e = renewed_e[0] if renewed_e else {}
    heads_sv = [HISTORY.findall(prompt.split("▌ pp · run", 1)[0]) for prompt in h.prompts_of("sv")]
    opening_e = next((one["id"] for one in by_kind(found_e, "post", verb="do", task="T1")), None)
    if (move.returncode == 0 and season_e.returncode == 0 and held_e and done_e and opening_e == OPENING_E and len(sv) == 3
            and [(run, provider) for run, _, provider in sv] == [(None, "claude"), (None, "codex"), (sv[1][1], "codex")]
            and result_of(found_e, "T1") == "T1 under codex"
            and sv[0][1] and sv[1][1] and sv[0][1] != sv[1][1] and ends_e[:3] == ["standing", "standing", "parked"]
            and not by_kind(found_e, "wake-failed") and len(renewed_e) == 1 and one_e.get("why") == "model"
            and one_e.get("run") == sv[0][1] and (one_e.get("was") or {}).get("provider") == "claude"
            and (one_e.get("now") or {}).get("provider") == "codex"
            and heads_sv[:2] == [[], [("T1", "sv")]]):
        held("(e) a changed provider renews a standing run", f"sv stands in {sv[0][1]} opened under claude; the season "
             f"gives it codex: run-renewed (provider claude -> codex), a new run {sv[1][1]} under codex told T1's "
             "history, continued under codex, its answer closing T1; no launch failed")
    else:
        failures.append(f"  ✗ (e) a changed provider        rc={move.returncode}/{season_e.returncode} held={held_e} "
                        f"done={done_e} intents={sv} ends={ends_e} renewed={renewed_e} heads={heads_sv} "
                        f"failed={[(one.get('reason'), one.get('why')) for one in by_kind(found_e, 'wake-failed')]} "
                        f"{season_e.stderr[-200:]!r}")
    return 0
