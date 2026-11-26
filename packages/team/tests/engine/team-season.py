"""Scenario `team-season` -- 9 case(s) (batch la-saison, 2026-10-12: row 82 of the study § 18, team 0.31.0): a
`team start` is a SEASON -- opened off season alone, after `team stop`: TEAM.md read again, the cost and the counts
afresh, the members' runs kept. Each case names the invariant of `team-sim-reframe.py` it replays; the profiles are
`team-season-profiles`'s. A season reads the team's TEMPLATE again (cases e to j, no wake-up: every start `--no-tick`).
- (a) a season after a team at work (I18): w asks the owner on T1; `team start` in season refuses `season-running`;
  `team stop` then `team start` open season 2, T1 stopped, the season's cost 0; T1 resumed, the reply wakes w in the
  SAME run, and T1 ends done
- (b) the season's budget (I10): `--budget 2 --budget-launches 5` over a TEAM.md at `budget: 1` -- the face says the
  cap 2, `budget-launches` 5 and the season's own; `team declaration` says no gap of `limits`; `--budget 0` refuses
  `budget-invalid`
- (c) a task's `launches:` counted afresh (I10): under `launches: 1`, k asks the owner, the reply finds the task
  `launches-spent`; a stop, a season and the task resumed, and k is woken again and ends the task
- (d) two seasons, two sets of documents (G2): `SEASON.md` naming the preset `seasons/house-flow`, then
  `seasons/lean` (`_templates.py`) -- each `team-started` keeps its own `documents` and their digests
- (e) the season keeps its preset: a team written by `team declare --template teams/supervisor-workers`, started --
  `team-started.template` its preset and its origin, `team-started.values` the values applied, the team as it plays in the journal's
  own keys (agents, reports, root, ceremonies, limits); the start RENDERS `TEAM-<name>.md`, its body the template's
  intention naming each member, its digest at `team-started.rendered`
- (f) a member added, no edge written: `c` added under `agents:` -- `pending` says `agents` and `reports`, the edges
  the form makes; a season, and `c`'s agent is born, its edge the form's, the intention rendered again with its
  name, its digest changed; the root taken out in season -- its line of `agents:` and its name in the preset's
  role key -- refuses `season-running`, the journal as it was
- (g) the template changed: `template: teams/chain` -- `pending` says `template` (the start's, the file's) and the chain's
  edges; a season, and `team-started` keeps the chain's edges, its template, no daily, the intention the new
  template's, rendered again (G11)
- (h) an edge taken out under a work still owed: on a journal written here -- r handed w a work on T1, w owes its
  answer, the season under way -- a `TEAM.md` where w reports to x refuses `season-running`, the journal byte for
  byte: no season starts over an open task; w's answer still reaches r along the edges of the season under way
- (j) a value changed: a `tree` started on its template's two squad leads, then `squads = 1` under `values:` --
  `pending` says `values` (the start's, the file's) and the edges one squad lead makes, no `template`
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")
S = support(__file__, "templates")
AT = "2026-10-01T09:00:00+00:00"
# The journal of `cut`: r handed w a work on T1 (#4), delivered, never answered.
CUT = [
    {"kind": "team-started", "agents": {"r": "agents/r", "w": "agents/w", "x": "agents/k"},
     "reports": [{"from": ["w", "x"], "to": "r"}], "root": "r", "principals": [], "owner": "house",
     "ceremonies": [], "entries": {}, "work": None, "launch": {}, "limits": {}, "schedule": None, "unit": "s",
     "digest": "000000000000"},
    {"kind": "task", "task": "T1", "from": "house", "to": "r", "text": "split it"},
    {"kind": "post", "task": "T1", "from": "house", "to": "r", "verb": "do", "text": "split it"},              # 3
    {"kind": "post", "task": "T1", "from": "r", "to": "w", "verb": "do", "text": "your half"},                 # 4
    {"kind": "wake-intent", "tag": "w-a", "agent": "w", "path": "agents/w", "task": "T1", "run": None,
     "index": 1, "messages": [4]},
    {"kind": "wake-launched", "tag": "w-a", "agent": "w", "run": "eee001", "pid": 3},
    {"kind": "wake-ended", "tag": "w-a", "agent": "w", "run": "eee001", "index": 1, "cost": 0.01},
]
TREE = ("---\ntemplate: teams/tree\n{values}agents: |\n  l agents/r\n  s agents/w\n  t agents/k\n  u agents/f\n"
        "  v agents/tpl-c\n---\nSplit it twice.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "r": [{"sleep": 0.1, "body": {"do": ["w"]}}, {"sleep": 0.1, "body": {"done": "merged"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
              {"sleep": 0.1, "body": {"done": "main"}}],
        "k": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which day?"}}},
              {"sleep": 0.1, "body": {"done": "monday"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def face(name: str) -> dict:
        played = cli(h.engine, "--instance", str(h.house), "team", "status", name, "--json", cwd=h.ws, env=h.env)
        try:
            return json.loads(played.stdout)
        except ValueError:
            return {}

    def reply(name: str) -> None:
        ask = [one["id"] for one in by_kind(h.events(name), "post", verb="ask")][-1]
        h.call("team", "post", name, "--task", "T1", "--reply", str(ask), "--message", "main")

    # --- (a) a season on a team at work: the member keeps its run -- I18 ---------------------------------
    h.declare("work", "---\nagents: |\n  r agents/r\n  w agents/w\nreports: |\n  w -> r\nroot: r\nschedule: off\n"
                      "---\nMerge together.\n")
    started = h.call("team", "start", "work", "--message", "merge PR 14", *h.harnessed)
    asked = h.settled("work", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    running = h.call("team", "start", "work", *h.harnessed)
    h.call("team", "stop", "work", "--no-tick")
    season = h.call("team", "start", "work", *h.harnessed, "--no-tick")
    opened = [one.get("task") for one in by_kind(h.events("work"), "task")]
    seasoned = face("work")
    h.call("team", "resume", "work", "--task", "T1", "--no-tick")
    reply("work")
    done = h.settled("work", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("work")
    w_runs = [one.get("run") for one in by_kind(found, "wake-launched", agent="w")]
    w_intents = [one.get("run") for one in by_kind(found, "wake-intent", agent="w")]
    if (started.returncode == 0 and asked and running.returncode == 2 and "season-running" in running.stderr
            and season.returncode == 0 and opened == ["T1"]
            and (seasoned.get("season") or {}).get("n") == 2 and seasoned.get("cost") == 0
            and [t.get("state") for t in seasoned.get("tasks") or []] == ["stopped"]
            and done and len(set(w_runs)) == 1 and w_intents == [None, w_runs[0]]):
        held("(a) a season after a team at work", f"in season: season-running; stopped, season 2, T1 stopped, cost 0; "
             f"T1 resumed, w woken in its run {w_runs[0]}, T1 done -- I18")
    else:
        failures.append(f"  ✗ (a) a season at work       rc={started.returncode}/{season.returncode} asked={asked} "
                        f"done={done} season={seasoned.get('season')} cost={seasoned.get('cost')} w={w_intents}/{w_runs} opened={opened} "
                        f"{season.stdout.strip()[-120:]!r} {season.stderr.strip()[-200:]!r}")

    # --- (b) the season's budget -- I10 --------------------------------------------------------------------------
    h.declare("funds", "---\nagents: |\n  f agents/f\nroot: f\nbudget: 1\nschedule: off\n---\nSpend within.\n")
    invalid = h.call("team", "start", "funds", "--message", "x", "--budget", "0", *h.harnessed, "--no-tick")
    funded = h.call("team", "start", "funds", "--message", "price it", "--budget", "2", "--budget-launches", "5",
                    *h.harnessed, "--no-tick")
    funds = face("funds")
    declared = cli(h.engine, "--instance", str(h.house), "team", "declaration", "funds", "--json", cwd=h.ws, env=h.env)
    try:
        pending = json.loads(declared.stdout).get("pending")
    except ValueError:
        pending = "unreadable"
    if (invalid.returncode == 2 and "budget-invalid" in invalid.stderr and funded.returncode == 0
            and (funds.get("budget") or {}).get("cap") == 2.0 and (funds.get("limits") or {}).get("budget-launches") == 5
            and funds.get("season") == {"n": 1, "at": (funds.get("started") or {}).get("at"), "state": "running",
                                        "budget": 2.0, "budget-launches": 5}
            and pending == []):
        held("(b) the season's budget", "--budget 0 refuses budget-invalid; --budget 2 --budget-launches 5 over TEAM.md's "
             "1: cap 2, budget-launches 5, the season's own said; declaration: no gap -- I10")
    else:
        failures.append(f"  ✗ (b) the season's budget    rc={invalid.returncode}/{funded.returncode} "
                        f"budget={funds.get('budget')} limits={funds.get('limits')} season={funds.get('season')} "
                        f"pending={pending} {invalid.stderr.strip()[-120:]!r} {funded.stderr.strip()[-160:]!r}")

    # --- (c) a task's launches: counted afresh -- I10 -----------------------------------------------------------
    h.declare("count", "---\nagents: |\n  k agents/k\nroot: k\nlaunches: 1\nschedule: off\n---\nOne launch.\n")
    h.call("team", "start", "count", "--message", "date the release", *h.harnessed)
    h.settled("count", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    reply("count")
    spent = h.settled("count", lambda found: bool(by_kind(found, "launches-spent")) and all_ended(found), 30)
    h.call("team", "stop", "count", "--no-tick")
    again = h.call("team", "start", "count", *h.harnessed, "--no-tick")
    h.call("team", "resume", "count", "--task", "T1")
    done_c = h.settled("count", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("count")
    starts = by_kind(found, "team-started")
    after = [one for one in by_kind(found, "wake-intent", agent="k") if len(starts) > 1 and one["id"] > starts[-1]["id"]]
    if spent and again.returncode == 0 and done_c and len(after) == 1:
        held("(c) a task's launches: counted afresh", "launches 1 spent at the reply; a stop, a season and T1 resumed, then "
             "k woken once more, T1 done -- I10")
    else:
        failures.append(f"  ✗ (c) launches afresh           spent={spent} rc={again.returncode} done={done_c} "
                        f"after={len(after)} {again.stderr.strip()[-200:]!r}")

    # --- (d) two seasons, two contracts -- G2 --------------------------------------------------------------------
    S.laid(h.house / "teams" / "templates", S.SHELF)
    h.declare("pact", "---\nagents: |\n  p agents/p\nroot: p\nschedule: off\nroles: |\n  make p\n  inspect p\n---\n"
                      "Two seasons.\n")
    season = h.teams / "pact" / "SEASON.md"
    season.write_text(S.SEASON, encoding="utf-8")
    first = h.call("team", "start", "pact", "--no-tick")
    season.write_text("---\ntemplate: seasons/lean\n---\n", encoding="utf-8")
    h.call("team", "stop", "pact", "--no-tick")
    second = h.call("team", "start", "pact", "--no-tick")
    kept = [one.get("documents") or [] for one in by_kind(h.events("pact"), "team-started")]
    digests = [sorted(one.get("rendered") or {}) for one in by_kind(h.events("pact"), "team-started")]
    if (first.returncode == 0 and second.returncode == 0
            and [[doc.get("template") for doc in one] for one in kept]
            == [["notes/plain", "sources/by-batch", "review/pair"], ["sources/by-batch"]]
            and digests == [["TEAM-pact-plain.md", "TEAM-pact.md", "roles/TEAM-pact-by-batch.md", "roles/TEAM-pact-pair.md"],
                            ["TEAM-pact-by-batch.md", "TEAM-pact.md"]]):
        held("(d) two seasons, two sets of documents", "season 1 keeps house-flow's three documents and their digests, "
             "season 2 lean's one document -- G2")
    else:
        failures.append(f"  ✗ (d) two contracts            rc={first.returncode}/{second.returncode} kept={kept} "
                        f"{(first.stderr or second.stderr).strip()[-200:]!r}")

    last_start = lambda name: (by_kind(h.events(name), "team-started") or [{}])[-1]
    pending_of = lambda name: {one["key"]: one for one in S.declaration_of(h, name).get("pending") or []}

    # --- (e) the season keeps its template ------------------------------------------------------------------------
    made = h.call("team", "declare", "tpl", "--template", "teams/supervisor-workers", "--member", "boss", "agents/r",
                  "--member", "a", "agents/w", "--member", "b", "agents/k")
    opened = h.call("team", "start", "tpl", "--message", "plan it", "--no-tick")
    first = last_start("tpl")
    intention = h.teams / "tpl" / "TEAM-tpl.md"
    read = lambda: intention.read_bytes() if intention.is_file() else b""
    said_one = read()
    if (made.returncode == 0 and opened.returncode == 0
            and first.get("template") == {"template": "teams/supervisor-workers", "origin": "package"}
            and first.get("values") == {"daily": S.DAILY}
            and first.get("agents") == {"boss": "agents/r", "a": "agents/w", "b": "agents/k"}
            and first.get("root") == "boss" and first.get("reports") == [{"from": ["a", "b"], "to": "boss"}]
            and [one.get("text") for one in first.get("ceremonies") or []] == [f"daily {S.DAILY} with a b -> boss"]
            and first.get("limits") == S.LIMITS
            and S.names_all(S.intention_of(said_one.decode()), ["boss", "a", "b"])
            and (first.get("rendered") or {}).get("TEAM-tpl.md") == S.digest(said_one)):
        held("(e) the season keeps its template", "team-started.template supervisor-workers, package, daily applied; "
             "agents, root boss, a b -> boss, the daily and the template's limits in the journal's own keys; "
             "TEAM-tpl.md rendered, its intention naming boss, a and b, its digest kept")
    else:
        failures.append(f"  ✗ (e) the season's template     rc={made.returncode}/{opened.returncode} first={first} "
                        f"{(made.stderr or opened.stderr).strip()[-200:]!r}")

    # --- (f) a member added, no edge written -------------------------------------------------------------------
    doc = h.teams / "tpl" / "TEAM.md"
    written = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    wider = written.replace("  b agents/k\n", "  b agents/k\n  c agents/tpl-c\n")
    doc.write_text(wider, encoding="utf-8")
    pending = pending_of("tpl")
    h.call("team", "stop", "tpl", "--no-tick")
    grown = h.call("team", "start", "tpl", "--no-tick")
    second = last_start("tpl")
    said_two = read()
    rootless = wider.replace("  boss agents/r\n", "").replace("  supervisor boss\n", "  supervisor\n")
    doc.write_text(rootless, encoding="utf-8")                # the root out of `agents:` and of the key that names it
    journal = h.journal_of("tpl").read_bytes() if h.journal_of("tpl").is_file() else b""
    dropped = h.call("team", "start", "tpl", "--no-tick")
    kept_journal = h.journal_of("tpl").is_file() and h.journal_of("tpl").read_bytes() == journal
    doc.write_text(wider, encoding="utf-8")
    edges = [{"from": ["a", "b", "c"], "to": "boss"}]
    if ("reports" not in S.keys_of(wider) and {"agents", "reports"} <= set(pending)
            and "boss" not in rootless.split("---")[1]
            and pending["agents"]["declared"] == {**(first.get("agents") or {}), "c": "agents/tpl-c"}
            and pending["reports"]["started"] == first.get("reports") and pending["reports"]["declared"] == edges
            and grown.returncode == 0 and second.get("reports") == edges and h.agent_stands("agents/tpl-c")
            and S.names_all(S.intention_of(said_two.decode()), ["boss", "a", "b", "c"])
            and not S.names_all(S.intention_of(said_one.decode()), ["c"])
            and (second.get("rendered") or {}).get("TEAM-tpl.md") == S.digest(said_two) != S.digest(said_one)
            and dropped.returncode == 2 and S.code_of(dropped) == "season-running" and kept_journal):
        bench.refusals += 1
        held("(f) a member added, no edge written", "c under agents: alone: pending agents and reports, a b c -> "
             "boss; a season, c born and reporting to boss, the intention rendered again with c, its digest "
             "changed; the root taken out in season refuses season-running, the journal as it was")
    else:
        failures.append(f"  ✗ (f) a member added            pending={pending} rc={grown.returncode}/{dropped.returncode} "
                        f"reports={second.get('reports')} born={h.agent_stands('agents/tpl-c')} "
                        f"code={S.code_of(dropped)} journal={kept_journal} {grown.stderr.strip()[-200:]!r}")

    # --- (g) the template changed --------------------------------------------------------------------------------
    doc.write_text(wider.replace("template: teams/supervisor-workers", "template: teams/chain"), encoding="utf-8")
    pending = pending_of("tpl")
    h.call("team", "stop", "tpl", "--no-tick")
    chained = h.call("team", "start", "tpl", "--no-tick")
    third = last_start("tpl")
    said_three = read()
    chain = [{"from": ["a"], "to": "boss"}, {"from": ["b"], "to": "a"}, {"from": ["c"], "to": "b"}]
    if ((pending.get("template") or {}).get("started") == "teams/supervisor-workers"
            and (pending.get("template") or {}).get("declared") == "teams/chain"
            and (pending.get("reports") or {}).get("declared") == chain
            and (pending.get("values") or {}).get("declared") == {}
            and chained.returncode == 0 and third.get("reports") == chain and third.get("ceremonies") == []
            and (third.get("template") or {}).get("template") == "teams/chain" and third.get("root") == "boss"
            and S.names_all(S.intention_of(said_three.decode()), ["boss", "a", "b", "c"])
            and S.intention_of(said_three.decode()) != S.intention_of(said_two.decode())
            and (third.get("rendered") or {}).get("TEAM-tpl.md") == S.digest(said_three)):
        held("(g) the template changed", "template: chain: pending template supervisor-workers -> chain, the "
             "chain's edges, no value left; a season keeps a -> boss, b -> a, c -> b, its template chain, no daily; "
             "the intention rendered again, the chain's -- G11")
    else:
        failures.append(f"  ✗ (g) the template changed      pending={pending} rc={chained.returncode} third={third} "
                        f"{chained.stderr.strip()[-200:]!r}")

    # --- (h) an edge taken out under a work still owed -----------------------------------------------------------
    front = "---\nagents: |\n  r agents/r\n  w agents/w\n  x agents/k\nreports: |\n{edges}root: r\nschedule: off\n---\nSplit it.\n"
    h.declare("cut", front.format(edges="  x -> r\n  w -> x\n"))
    h.written("cut", CUT, AT)
    journal_cut = h.journal_of("cut").read_bytes()
    moved = h.call("team", "start", "cut", "--no-tick")
    module = h.module()
    state = module.state_of(h.journal_of("cut"))
    try:
        answer = [(one.sender, one.to, one.verb, one.re, one.info)
                  for one in module.routed(state, state.wake.intents["w-a"],   # w's intent, as the state holds it
                                           [{"re": 4, "text": "half done"}])]
    except module.Refused as refusal:
        answer = [str(refusal)]
    if (moved.returncode == 2 and S.code_of(moved) == "season-running"
            and h.journal_of("cut").read_bytes() == journal_cut
            and answer == [("w", "r", "re", 4, None)]):
        bench.refusals += 1
        held("(h) an edge taken out under a work still owed", "w -> x written while r's work to w on T1 is owed, the "
             "season under way: season-running, the journal byte for byte; w's answer to #4 goes to r along the "
             "season's edges")
    else:
        failures.append(f"  ✗ (h) an edge taken out         rc={moved.returncode} code={S.code_of(moved)} "
                        f"same={h.journal_of('cut').read_bytes() == journal_cut} answer={answer} "
                        f"{moved.stderr.strip()[-240:]!r}")

    # --- (j) a value changed ------------------------------------------------------------------------------------
    h.declare("tr", TREE.format(values=""))
    planted = h.call("team", "start", "tr", "--no-tick")
    grown_tree = last_start("tr")
    h.declare("tr", TREE.format(values="values: |\n  squads = 1\n"))
    pending = pending_of("tr")
    if (planted.returncode == 0 and grown_tree.get("values") == {"squads": "2", "daily": S.DAILY}
            and grown_tree.get("reports") == [{"from": ["s", "t"], "to": "l"}, {"from": ["u"], "to": "s"},
                                              {"from": ["v"], "to": "t"}]
            and (pending.get("values") or {}).get("started") == {"squads": "2", "daily": S.DAILY}
            and (pending.get("values") or {}).get("declared") == {"squads": "1", "daily": S.DAILY}
            and (pending.get("reports") or {}).get("declared") == [{"from": ["s"], "to": "l"},
                                                                   {"from": ["t", "u", "v"], "to": "s"}]
            and "template" not in pending):
        held("(j) a value changed", "a tree started on two squad leads; squads = 1 under values: pending values "
             "squads 2 -> 1 and the edges of one squad lead, s -> l, t u v -> s; no pending template")
    else:
        failures.append(f"  ✗ (j) a value changed           rc={planted.returncode} started={grown_tree.get('template')} "
                        f"{grown_tree.get('reports')} pending={pending} {planted.stderr.strip()[-200:]!r}")
    return 0
