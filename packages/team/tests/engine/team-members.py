"""Scenario `team-members` -- 4 case(s) (batch l-equipe-et-son-journal, rework, team 0.13.0, and the
corrective rework of le-package-agent, 2026-10-04; split out of `team-review` by
les-scenarios-par-maison, 2026-10-07): a team declares `<name> <path>` -- the member's name, then
the path of the agent that plays it.
- (m1) two members on one agent [48] (I20): `ra agents/dev`, `rb agents/dev` under `ml agents/lead`
  -- agents/dev born once, `team-started.agents` the names to their paths, two runs of agents/dev
  launched together (two keys, two sessions), each intent with its `path`, every head
  `[team pair · you are <member>]`
- (m1b) the neighbours line of two members of one agent quotes the first line of the neighbour's
  message, `« [team pair · you are ra] »`
- (m2) the name and the path judged: a name with `/`, a name twice, a path out of the house:
  `team-invalid`, nothing written, no agent born
- (m4) two births of one path at once [37] (KC33): five races of two `team start` declaring one new
  path -- each path born once, both teams started
"""
from __future__ import annotations

import re
import time

from tests.harness import race, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "ml": [{"sleep": 0.2, "body": {"do": ["ra", "rb"]}},
               {"sleep": 0.1, "body": {"done": "both read"}}],
        "ra": [{"sleep": 1.0, "body": {"done": True}}],
        "rb": [{"sleep": 1.0, "body": {"done": True}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    # --- (m1) two members on one agent [48] -- I20 --------------------------------------------------------
    h.declare("pair", "---\nagents: |\n  ml agents/lead\n  ra agents/dev\n  rb agents/dev\nreports: |\n  ra rb -> ml\n"
                      "root: ml\nschedule: off\n---\nTwo members on one agent.\n")
    pair = h.call("team", "start", "pair", "--message", "review PR 50", *h.harnessed)
    done_pair = h.settled("pair", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found_p = h.events("pair")
    started_p = next(iter(by_kind(found_p, "team-started")), {})
    launched_p = {one.get("agent"): one for one in by_kind(found_p, "wake-launched") if one.get("agent") in ("ra", "rb")}
    first_end = min((one["id"] for one in by_kind(found_p, "wake-ended") if one.get("agent") in ("ra", "rb")), default=0)
    intents_p = {one.get("agent"): one for one in by_kind(found_p, "wake-intent") if one.get("agent") in ("ra", "rb")}
    sessions_p = h.sessions_at("agents/dev")
    headed_p = {name: bool(h.prompts_of(name)) and all(re.search(rf"^\[team pair · you are {name}\]$", one, re.M)
                                                       for one in h.prompts_of(name)) for name in ("ml", "ra", "rb")}
    if (pair.returncode == 0 and done_pair
            and h.agent_stands("agents/dev")
            and not any((h.ws / one).exists() for one in ("ml", "ra", "rb"))
            and started_p.get("agents") == {"ml": "agents/lead", "ra": "agents/dev", "rb": "agents/dev"}
            and "(born: agents/lead, agents/dev)" in pair.stdout
            and set(launched_p) == {"ra", "rb"} and launched_p["ra"].get("run") != launched_p["rb"].get("run")
            and all(one["id"] < first_end for one in launched_p.values())
            and all(intents_p.get(name, {}).get("path") == "agents/dev" for name in ("ra", "rb"))
            and len(sessions_p) == 2 and len({run for run, _ in sessions_p}) == 2
            and len({session for _, session in sessions_p}) == 2
            and all(headed_p.values())
            and result_of(found_p, "T1") == "both read"):
        held("(m1) two members on one agent", f"ra and rb on agents/dev, born once; team-started.agents "
             f"{started_p.get('agents')}; two runs of agents/dev launched before the first end, two keys, two "
             "sessions; the journal in names, each intent with its path; every head `[team pair · you are <member>]` "
             "-- I20")
    else:
        failures.append(f"  ✗ (m1) two members, one agent rc={pair.returncode} done={done_pair} "
                        f"dev={h.agent_stands('agents/dev')} "
                        f"agents={started_p.get('agents')} launched={ {k: (v['id'], v.get('run')) for k, v in launched_p.items()} } "
                        f"first_end={first_end} paths={ {k: v.get('path') for k, v in intents_p.items()} } "
                        f"sessions={sessions_p} heads={headed_p} {pair.stdout[-200:]!r} {pair.stderr[-200:]!r}")

    # --- (m1b) the neighbours line of two members of one agent names the member -------------------------
    neighbours_p = [one.splitlines()[0] for name in ("ra", "rb") for one in h.prompts_of(name)
                    if one.startswith("[runs under way: ")]
    if neighbours_p and all(re.fullmatch(r"\[runs under way: [0-9a-f]{6} since \d\d:\d\d « \[team pair · you are r[ab]\] »\]",
                                         one) for one in neighbours_p):
        held("(m1b) the neighbours line names the member", f"{neighbours_p[0]!r}: the first line of the neighbour's "
             "message, the head of a team's wake-up")
    else:
        failures.append(f"  ✗ (m1b) neighbours line       {neighbours_p!r}")

    # --- (m2) the name and the path judged [48] ------------------------------------------------------------
    h.declare("slashed", "---\nagents: |\n  nm/r9 agents/r9\nroot: nm/r9\nschedule: off\n---\nA name with a slash.\n")
    h.declare("twice", "---\nagents: |\n  dn agents/a1x\n  dn agents/b1x\nroot: dn\nschedule: off\n---\nOne name twice.\n")
    h.declare("escaped", "---\nagents: |\n  ex ../x\nroot: ex\nschedule: off\n---\nA path out of the house.\n")
    judged = {name: h.call("team", "start", name, "--message", "x", "--no-tick") for name in ("slashed", "twice", "escaped")}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == "" for one in judged.values())
            and "nm/r9" in judged["slashed"].stderr and "dn" in judged["twice"].stderr and "../x" in judged["escaped"].stderr
            and not any(h.journal_of(name).exists() for name in judged)
            and not any(path.exists() for path in (h.ws / "nm", h.ws / "agents" / "r9", h.ws / "agents" / "a1x",
                                                   h.ws / "agents" / "b1x", h.ws / "ex", h.ws.parent / "x"))):
        held("(m2) the name and the path judged", "a name with `/`, a name declared twice, a path out of the "
             "house: team-invalid naming them, no journal, no agent born")
    else:
        failures.append("  ✗ (m2) name and path judged   "
                        + " ".join(f"{name}={one.returncode}:{one.stdout[-80:]!r}:{one.stderr[-100:]!r}" for name, one in judged.items()))

    # --- (m4) two births of one path at once [37] -- KC33 ----------------------------------------------------
    raced_births = []
    for n in range(1, 6):
        for side in ("a", "b"):
            h.declare(f"race{n}{side}", f"---\nagents: |\n  w{n}{side} shared/d{n}\nroot: w{n}{side}\nschedule: off\n---\n"
                                        "A birth raced.\n")
        both = race(h.engine, [["--instance", str(h.house), "team", "start", f"race{n}{side}", "--message", "x", "--no-tick"]
                               for side in ("a", "b")], cwd=h.ws, env=h.env)
        births = sum(1 for one in both if f"(born: shared/d{n})" in one.stdout)
        raced_births.append((n, [one.returncode for one in both], births,
                             h.agent_stands(f"shared/d{n}"),
                             [one.stderr.strip()[-120:] for one in both if one.returncode]))
    if all(rcs == [0, 0] and births == 1 and stands for _, rcs, births, stands, _ in raced_births):
        held("(m4) two births of one path at once", "five races of two team starts on one new path: each "
             "path born once, both teams started -- KC33")
    else:
        failures.append(f"  ✗ (m4) births raced           {raced_births}")
    return 0
