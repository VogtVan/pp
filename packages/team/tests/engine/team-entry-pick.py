"""Scenario `team-entry-pick` -- 2 case(s) (batch le-rythme-et-les-entrees, rework, team 0.13.3;
split out of `team-review` by les-scenarios-par-maison, 2026-10-07): the entry a wake-up elects,
read back by `team entry`; an entry missing at an agent.
- (u) the neutral and `do` (I22): `entries: | do -> WORK.md` elects `WORK.md` at the opening AND at the
  resume; `team entry <team> --run <key>` names a ceremony's wake-up's entry, an opening's found by its
  tag at `messages.jsonl`, the neutral for an ended wake-up and an unknown key -- the journal's bytes
  unchanged; the team's documents in its directory, none at the agent (realigned by
  les-fichiers-sous-l-equipe, 2026-10-10)
- (v) an entry missing at an agent that plays it: `entry-missing` naming the agent and the document,
  exit 2 -- no agent born, no journal, no team document laid
"""
from __future__ import annotations

import json
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "wk": [{"sleep": 0.1, "body": {"done": "one"}},
               {"sleep": 0.1, "body": {"done": "two"}}]})
    by_kind, all_ended, runs_launched = T.by_kind, T.all_ended, T.runs_launched

    # --- (u) the neutral and `do` [55] -- I22; `team entry` writes nothing ----------------------------------
    h.entry_laid("agents/wk", "WORK.md", T.WORK_DOC)
    h.declare("dowork", "---\nagents: |\n  wk agents/wk\nroot: wk\nentries: |\n  do -> WORK.md\n"
                        "schedule: off\n---\nEvery task on WORK.md.\n")
    dowork = h.call("team", "start", "dowork", "--message", "one", *h.harnessed)
    one_u = h.settled("dowork", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    dowork2 = h.call("team", "post", "dowork", "--message", "two")
    two_u = h.settled("dowork", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=60)
    found_u = h.events("dowork")
    key_wk = next((one.get("run") for one in by_kind(found_u, "wake-ended", agent="wk")), "")
    wk_elected = h.elected("agents/wk", key_wk)
    for one in ("agents/pk", "agents/fk"):           # a team whose wake-ups the bench forges, never launched
        h.entry_laid(one, "DAILY.md", T.DAILY_DOC)
        h.entry_laid(one, "WORK.md", T.WORK_DOC)
    h.declare("pick", "---\nagents: |\n  fk agents/fk\n  pk agents/pk\nreports: |\n  pk -> fk\nroot: fk\n"
                      "ceremonies: |\n  daily every weekday 09:30 with pk -> fk\n"
                      "entries: |\n  daily -> DAILY.md\n  do -> WORK.md\nschedule: off\n---\nPick.\n")
    pick = h.call("team", "start", "pick", "--message", "x", *h.harnessed, "--no-tick")
    found_k = h.events("pick")
    last_k = max(one["id"] for one in found_k)
    with h.journal_of("pick").open("a", encoding="utf-8") as handle:
        for offset, line in enumerate((
                {"kind": "task", "task": "T2", "from": "pick", "to": "fk", "ceremony": "daily", "period": "2026-10-01"},
                {"kind": "wake-intent", "tag": "pick-a", "agent": "pk", "path": "agents/pk", "task": "T2",
                 "run": "aaa111", "index": 2, "messages": []},
                {"kind": "wake-intent", "tag": "pick-b", "agent": "fk", "path": "agents/fk", "task": "T1",
                 "run": None, "index": 1, "messages": []},
                {"kind": "wake-intent", "tag": "pick-c", "agent": "pk", "path": "agents/pk", "task": "T1",
                 "run": "ccc333", "index": 1, "messages": []},
                {"kind": "wake-ended", "tag": "pick-c", "agent": "pk", "run": "ccc333", "index": 1, "cost": 0}), 1):
            handle.write(json.dumps({"at": "2026-10-04T12:00:00+00:00", "id": last_k + offset, "team": "pick",
                                     **line}) + "\n")
    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as handle:   # pick-b's opening, before its event
        handle.write(json.dumps({"at": "2026-10-04T12:00:01+00:00", "from": "house", "to": "agents/fk",
                                 "run": "bbb222", "message": "x", "policy": {}, "tag": "pick-b", "pid": 1}) + "\n")
    before_k = h.journal_of("pick").read_bytes()
    said_k = {key: h.call("team", "entry", "pick", "--run", key) for key in ("aaa111", "bbb222", "ccc333", "ddd444")}
    bare_k = h.call("team", "entry", "pick")
    team_doc_k = h.teams / "pick" / "TEAM-pick.md"
    front_k = team_doc_k.read_text(encoding="utf-8") if team_doc_k.is_file() else ""
    laid_k = [(h.teams / "pick" / "TEAM-IDLE.md").is_file(), (h.teams / "pick" / "TURN.md").is_file(),
              not (h.meta_of("agents/pk") / "procs" / "TEAM-pick.md").exists(),
              not (h.meta_of("agents/pk") / "skills" / "team-entry").exists()]
    if (dowork.returncode == 0 and one_u and dowork2.returncode == 0 and two_u and key_wk
            and runs_launched(found_u, "wk") == {key_wk} and wk_elected == ["WORK.md", "WORK.md"]
            and pick.returncode == 0
            and {key: (one.returncode, one.stdout) for key, one in said_k.items()}
            == {"aaa111": (0, "DAILY.md\n"), "bbb222": (0, "WORK.md\n"), "ccc333": (0, "TEAM-IDLE.md\n"),
                "ddd444": (0, "TEAM-IDLE.md\n")}
            and bare_k.returncode == 2 and h.journal_of("pick").read_bytes() == before_k
            and "attach: turn.begin" in front_k and "next: DAILY.md WORK.md TEAM-IDLE.md" in front_k
            and "decide: pp-team entry pick" in front_k and all(laid_k)):
        held("(u) the neutral and do", f"wk opened then resumed: {wk_elected}; "
             "team entry pick --run: a ceremony's wake-up DAILY.md, an opening found by its tag WORK.md, an ended "
             "one and an unknown key TEAM-IDLE.md, nothing written; TEAM-pick.md, TEAM-IDLE.md and TURN.md in "
             "teams/pick/, none at the agent -- I22")
    else:
        failures.append(f"  ✗ (u) neutral and do           {dowork.returncode}/{dowork2.returncode}/{pick.returncode} "
                        f"one={one_u} two={two_u} key={key_wk} elected={wk_elected} "
                        f"said={ {key: (one.returncode, one.stdout, one.stderr[-120:]) for key, one in said_k.items()} } "
                        f"bare={bare_k.returncode} same={h.journal_of('pick').read_bytes() == before_k} "
                        f"front={front_k[:200]!r} laid={laid_k}")

    # --- (v) an entry missing at an agent refuses before anything is written [55] ---------------------------
    h.entry_laid("agents/gf", "DAILY.md", T.DAILY_DOC)
    h.declare("gap", "---\nagents: |\n  gf agents/gf\n  gp agents/gp\nreports: |\n  gp -> gf\nroot: gf\n"
                     "ceremonies: |\n  daily every weekday 09:30 with gp -> gf\n"
                     "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nA hole.\n")
    gap = h.call("team", "start", "gap", "--message", "x", *h.harnessed, "--no-tick")
    if (gap.returncode == 2 and "entry-missing" in gap.stderr and "agents/gp" in gap.stderr
            and "DAILY.md" in gap.stderr and gap.stdout == ""
            and not h.journal_of("gap").exists() and not h.agent_stands("agents/gp")
            and not (h.meta_of("agents/gf") / "procs" / "TEAM-gap.md").exists()):
        held("(v) an entry missing refuses", "DAILY.md absent at agents/gp: team start gap refuses entry-missing "
             "naming the agent and the document, exit 2; no agent born, no journal, no team document laid")
    else:
        failures.append(f"  ✗ (v) entry missing           rc={gap.returncode} journal={h.journal_of('gap').exists()} "
                        f"born={h.agent_stands('agents/gp')} {gap.stderr[-300:]!r}")
    return 0
