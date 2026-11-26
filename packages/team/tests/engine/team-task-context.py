"""Scenario `team-task-context` -- 1 case (batch le-run-renouvele-en-tache, team 1.24.0; s.1573): a task's run is
RENEWED at the member's wake-up once its last measure reached the task's CONTEXT LIMIT -- the task's own (`team post …
--context <n>%`), else the season's (`team start … --context <n>%`, `context:` of SEASON.md); the renewal of a
recurrence's run is `team-recurrence-context`'s. The witness measures the tokens of its calls; under a caller's command the
house knows no window, so while the team rests the case writes into the measures kept the `window` and the `used` a house
that launched a provider would have written (`House.measured_in`) -- the renewal is judged on the journal alone.
- (t) a task's run renewed past its threshold: `start --context 50%` writes `context: 50%` into SEASON.md; `--context` on
  an open task is the usage, `--context 0%` at a post and `--context abc` at a start `context-invalid`, the journal
  byte-identical; three members played by one agent each ask the owner and park on their task -- ca on T1 (no threshold
  of its own: the season's 50 %), cb on T2 (`--context 90%`, over the season's), cc on T3 (`--context 50%`) -- measured
  at 60 %, 60 % and 30 % of the window; the owner's answers wake them: ca alone gets `run-renewed {why: context, limit:
  50}`, written after its run parked, and a NEW run whose head opens on T1's history; cb and cc resume their run; in a
  team without a threshold, cd measured at 60 % resumes its run
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "team")

WINDOW = 100_000             # the window a launched provider's house would have declared (team-recurrence-context)
HISTORY = re.compile(r"^\[history of (\S+) for (\S+)\]$", re.M)   # the head of a new run's history (team-reset)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # each asks the owner and parks, measured; the owner's answer brings the launch that renews or resumes
    h = T.House(bench, script={member: {task: [{"sleep": 0.1, "calls": [{"name": "Read", "sent": sent}],
                                                "body": {"ask": {"to": "house", "text": "which branch?"}}},
                                               {"sleep": 0.1, "body": {"done": member}}]}
                               for member, task, sent in (("ca", "T1", 60_000), ("cb", "T2", 60_000),
                                                          ("cc", "T3", 30_000), ("cd", "T1", 60_000))})
    by_kind, all_ended, intents_on = T.by_kind, T.all_ended, T.intents_on

    # --- the season's threshold, judged before writing, then one task per member ---------------------------
    h.declare("cap", "---\nagents: |\n  ca agents/c\n  cb agents/c\n  cc agents/c\nroot: ca\nschedule: off\n---\n"
                     "Ask, then answer.\n")
    h.declare("bare", "---\nagents: |\n  cd agents/c\nroot: cd\nschedule: off\n---\nAsk, then answer.\n")
    cap = h.call("team", "start", "cap", "--context", "50%", "--no-tick", *h.harnessed)
    bare = h.call("team", "start", "bare", "--message", "work T1", "--no-tick", *h.harnessed)
    season_t = (h.teams / "cap" / "SEASON.md").read_text(encoding="utf-8") if (h.teams / "cap" / "SEASON.md").is_file() else ""
    journal_t = lambda: h.journal_of("cap").read_bytes() if h.journal_of("cap").is_file() else b""
    before_t = journal_t()
    refused_t = {"usage": h.call("team", "post", "cap", "--task", "T1", "--context", "50%", "--message", "x"),
                 "context-invalid": h.call("team", "post", "cap", "--to", "cb", "--context", "0%", "--message", "x"),
                 "context-invalid ": h.call("team", "start", "cap", "--context", "abc", "--no-tick")}
    usage_t = h.call("team", "post", "cap", "--task", "T1", "--every", "day 09:00", "--message", "x").stderr.strip()
    untouched_t = journal_t() == before_t
    posts_t = [h.call("team", "post", "cap", "--to", member, "--message", f"work {task}", *limit)
               for member, task, limit in (("ca", "T1", ()), ("cb", "T2", ("--context", "90%")),
                                           ("cc", "T3", ("--context", "50%")))]
    ticked_t = h.call("team", "tick", "bare")

    # --- (t) a task's run renewed past its threshold ---------------------------------------------------------------
    asked_t = {name: h.settled(name, lambda found, n=n: len(by_kind(found, "post", verb="ask", to="house")) == n
                               and all_ended(found), 60) for name, n in (("cap", 3), ("bare", 1))}
    for name in ("cap", "bare"):
        h.measured_in(name, WINDOW)
    answers_t = [h.call("team", "post", name, "--task", one.get("task"), "--reply", str(one.get("id")), "--message", "main")
                 for name in ("cap", "bare") for one in by_kind(h.events(name), "post", verb="ask", to="house")]
    done_t = {name: h.settled(name, lambda found, n=n: len(by_kind(found, "done")) == n and all_ended(found), 60)
              for name, n in (("cap", 3), ("bare", 1))}
    found_t = {name: h.events(name) for name in ("cap", "bare")}
    keys_t = {name: {one.get("tag"): one.get("run") for one in by_kind(found, "wake-launched")}
              for name, found in found_t.items()}
    runs_t = {member: [(one.get("run"), keys_t[name].get(one.get("tag"))) for one in intents_on(found_t[name], member, task)]
              for name, member, task in (("cap", "ca", "T1"), ("cap", "cb", "T2"), ("cap", "cc", "T3"),
                                         ("bare", "cd", "T1"))}
    renewed_t = by_kind(found_t["cap"], "run-renewed") + by_kind(found_t["bare"], "run-renewed")
    one_t = renewed_t[0] if renewed_t else {}
    first_ca = (runs_t["ca"] or [(None, None)])[0][1]
    parked_ca = next((one for one in by_kind(found_t["cap"], "wake-ended", agent="ca") if one.get("run") == first_ca), {})
    heads_ca = [HISTORY.findall(prompt.split("▌ pp · run", 1)[0]) for prompt in h.prompts_of("ca")]
    season_lines = [line.strip() for line in season_t.splitlines()]
    if (cap.returncode == 0 and bare.returncode == 0 and "context: 50%" in season_lines and untouched_t
            and refused_t["usage"].returncode == 2 and refused_t["usage"].stderr.strip() == usage_t
            and all(one.returncode == 2 and code.strip() in one.stderr for code, one in refused_t.items() if code != "usage")
            and all(one.returncode == 0 for one in (*posts_t, ticked_t, *answers_t)) and len(answers_t) == 4
            and all(asked_t.values()) and all(done_t.values())
            and len(renewed_t) == 1 and one_t.get("member") == "ca" and one_t.get("task") == "T1"
            and one_t.get("why") == "context" and one_t.get("limit") == 50 and "recurrence" not in one_t
            and one_t.get("run") == first_ca and float(one_t.get("used") or 0) * 100 >= 50
            and parked_ca.get("state") == "parked" and int(one_t.get("id") or 0) > int(parked_ca.get("id") or 10 ** 9)
            and [run for run, _ in runs_t["ca"]] == [None, None] and len({key for _, key in runs_t["ca"]}) == 2
            and len(heads_ca) == 2 and heads_ca[0] == [] and heads_ca[1] == [("T1", "ca")]
            and all([run for run, _ in runs_t[member]] == [None, runs_t[member][0][1]] and runs_t[member][0][1]
                    for member in ("cb", "cc", "cd"))):
        held("(t) a task's run renewed past its threshold", f"SEASON.md context: 50%; the usage and context-invalid "
             f"refused, the journal byte-identical; ca past the season's 50 %: run-renewed #{one_t.get('id')} after its "
             f"parked end #{parked_ca.get('id')}, a new run {runs_t['ca'][1][1]} told T1's history; cb (90 %), cc "
             "(under) and cd (no threshold) resume their run")
    else:
        failures.append(f"  ✗ (t) renewed past its threshold  rc={cap.returncode}/{bare.returncode} season={season_lines} "
                        f"untouched={untouched_t} refused={[(c, o.returncode, o.stderr.strip()[-100:]) for c, o in refused_t.items()]} "
                        f"posts={[o.returncode for o in (*posts_t, ticked_t, *answers_t)]} asked={asked_t} done={done_t} "
                        f"renewed={renewed_t} runs={runs_t} parked={parked_ca} heads={heads_ca} "
                        f"{(cap.stderr + bare.stderr)[-200:]!r}")

    return 0
