"""Scenario `team-laws-and-paths` -- 4 case(s) (batches l-equipe-au-reel, 2026-10-02,
le-verrou-de-la-machine, 2026-10-03, la-politique-du-lancement and le-package-agent, reworks of
2026-10-03; split out of `team-review` by les-scenarios-par-maison, 2026-10-07): what a start
lays at the agents, the machine's lock, the launch flags, the agent's path.
- the law reaches the team's runs (realigned by les-fichiers-sous-l-equipe, 2026-10-10): `team start`
  writes `TURN.md` in the team's directory, the bytes of the skill's `agent-turn.md`, nothing at the
  agents; a wake-up of the team reads the law under `production:`; an agent's own overlay standing is
  kept and said; a second start rewrites nothing; `log` says `of 2 wakes` under the costless budget
- the house's machine under its maintenance lock held exclusive: `team tick` refuses
  `maintenance-in-progress` and the journal gains no event; released, the tick plays
- `team start --effort low` keeps the effort among the launch flags at `team-started`, and the
  wake-up's `agent start` gets `--effort low`
- the agent's path: every agent of a team is born at its path under the house (`m`, `r1`…, not under
  `agents/`); `r9 squad/r9` with `r9 -> m9`: born at `squad/r9/.pp` without a door, the team's TURN
  written in the team's directory, woken by the tick and ended as `r9`, `status` says `r9 · squad/r9`; `x ../x` refuses
  `team-invalid`, no journal written
"""
from __future__ import annotations

from conductor import contributions, install
from tests.harness import SOURCE, holding, load_script, support

T = support(__file__, "team")
A = contributions.module_at(SOURCE / "packages" / "agent" / "tests" / "engine" / "_agent.py")   # `harness_artifacts`


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "ka": [{"sleep": 0.1, "mode": "kit", "body": {"do": ["ka1"]}},
               {"sleep": 0.1, "mode": "kit", "body": {"done": "the date"}}],
        "ka1": [{"sleep": 0.1, "mode": "kit", "body": {"done": "2026-10-02"}}],
        "n": [{"sleep": 0.1, "body": {"do": ["n1"]}},
              {"sleep": 0.1, "body": {"done": "never reached"}}],
        "n1": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- the law reaches the agents ---------------------------------------------------------------
    h.declare("kit", "---\nagents: |\n  ka ka\n  ka1 ka1\nreports: |\n  ka1 -> ka\nroot: ka\n---\nAnswer as the kit delivers.\n")
    h.declare("nocost", "---\nagents: |\n  n n\n  n1 n1\nreports: |\n  n1 -> n\nroot: n\nbudget-wakes: 2\n---\nCount the wake-ups.\n")
    kit = h.call("team", "start", "kit", "--message", "what is the date?", *h.harnessed)
    nocost = h.call("team", "start", "nocost", "--message", "spend nothing", *h.harnessed)
    done_k = h.settled("kit", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    spent_n = h.settled("nocost", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), timeout=60)
    source = h.team_module().parent / "agent-turn.md"
    laid_ka = h.teams / "kit" / "TURN.md"
    laid_ka1 = h.meta_of("ka1") / "procs" / "TURN.md"
    install.install(h.engine, h.meta_of("ox"), [], slug="ox", doors=False, borrow=True)   # born under the house
    own = h.meta_of("ox") / "procs" / "TURN.md"
    own.parent.mkdir(parents=True, exist_ok=True)
    own.write_text("---\nname: TURN\nconstraints.behavior: |\n  OX1  keep it short.\n---\n", encoding="utf-8")
    h.declare("owned", "---\nagents: |\n  ox ox\nroot: ox\nschedule: off\n---\nThe agent's own overlay.\n")
    owned = h.call("team", "start", "owned", "--message", "x", "--no-tick")
    before_mtime = laid_ka.stat().st_mtime_ns if laid_ka.is_file() else 0
    again_k = h.call("team", "start", "kit", "--message", "again", "--no-tick")
    same_mtime = laid_ka.is_file() and laid_ka.stat().st_mtime_ns == before_mtime
    block = "\n".join(h.prompts_of("ka1"))                  # what the team's wake-up of ka1 was served
    law = next((line for line in (source.read_text(encoding="utf-8").splitlines() if source.is_file() else [])
                if line.strip()[:2].isalpha() and line.strip()[2:3].isdigit()), "").strip()
    log_n = h.call("team", "log", "nocost")
    if (kit.returncode == 0 and done_k and nocost.returncode == 0 and spent_n
            and source.is_file() and laid_ka.is_file() and not laid_ka1.exists()
            and laid_ka.read_bytes() == source.read_bytes()
            and owned.returncode == 0 and "kept" in owned.stderr and "ox" in owned.stderr
            and own.read_text(encoding="utf-8").count("OX1") == 1
            and again_k.returncode == 0 and same_mtime
            and law and law.split()[0] in block and "production:" in block
            and "of 2 wakes" in log_n.stdout):
        held("the law reaches the team's runs", f"teams/kit/TURN.md, the bytes of agent-turn.md, nothing at ka1; "
             f"ka1's wake-up shows {law.split()[0]} under production:; ox's own overlay kept and said; a second "
             "start rewrites nothing; log says `of 2 wakes`")
    else:
        failures.append(f"  ✗ law at the agents           kit={kit.returncode}/{done_k} nocost={nocost.returncode}/{spent_n} "
                        f"source={source.is_file()} laid={laid_ka.is_file()}/{laid_ka1.is_file()} "
                        f"owned={owned.returncode}:{owned.stderr[-150:]!r} same_mtime={same_mtime} law={law[:40]!r} "
                        f"in_block={bool(law) and law.split()[0] in block} log={'of 2 wakes' in log_n.stdout}")

    # --- the machine under maintenance: the tick writes nothing -------------------------------------
    h.declare("maint", "---\nagents: |\n  mt mt\nroot: mt\nschedule: off\n---\nUnder maintenance.\n")
    begun_m = h.call("team", "start", "maint", "--message", "x", *h.harnessed, "--no-tick")
    before_m = h.events("maint")
    with holding(h.house / ".sys" / "state" / "maintenance.lock"):
        ticked_m = h.call("team", "tick", "maint")
        under_m = h.events("maint")
    freed_m = h.call("team", "tick", "maint")
    if (begun_m.returncode == 0 and ticked_m.returncode == 2 and "maintenance-in-progress" in ticked_m.stderr
            and under_m == before_m and freed_m.returncode == 0
            and len(h.events("maint")) > len(before_m)):
        held("the machine under maintenance: the tick refuses, the journal unchanged",
             f"maintenance-in-progress, {len(before_m)} events before and under; released, the tick plays")
    else:
        failures.append(f"  ✗ tick under maintenance      start={begun_m.returncode} tick rc={ticked_m.returncode} "
                        f"{ticked_m.stderr.strip()[-120:]!r} events {len(before_m)} -> {len(under_m)} "
                        f"freed={freed_m.returncode}")

    # --- the effort rides the launch (batch la-politique-du-lancement, rework 2026-10-03) -----------
    h.declare("efforted", T.REVIEW)
    efforted = h.call("team", "start", "efforted", "--message", "review with effort", "--effort", "low", "--no-tick")
    opened_e = next((one for one in h.events("efforted") if one.get("kind") == "team-started"), {})
    flags = load_script(h.team_module()).launch_flags({"effort": "low", "model": "m"})
    if (efforted.returncode == 0 and opened_e.get("launch") == {"effort": "low"}
            and flags == ["--model", "m", "--effort", "low"]):
        held("the effort rides the launch", "team start --effort low keeps {'effort': 'low'} at team-started; "
             "the wake-up's agent start gets --model m --effort low")
    else:
        failures.append(f"  ✗ team effort                 rc={efforted.returncode} launch={opened_e.get('launch')} "
                        f"flags={flags} {efforted.stderr[-200:]!r}")

    # --- an agent is its path: a squad member born, laid and woken where TEAM.md says ----------------
    h.declare("squad", "---\nagents: |\n  m9 m9\n  r9 squad/r9\nreports: |\n  r9 -> m9\n"
                       "root: r9\nschedule: off\n---\nA squad whose reviewer lives under squad/.\n")
    h.declare("outside", "---\nagents: |\n  x ../x\nroot: x\nschedule: off\n---\nOutside.\n")
    squad = h.call("team", "start", "squad", "--message", "review the squad's PR", *h.harnessed)
    resolved = h.settled("squad", lambda found: any(one.get("kind") == "done" for one in found)
                         and all_ended(found), timeout=60)
    squad_events = h.events("squad")
    r9 = h.ws / "squad" / "r9"
    wirings = A.harness_artifacts(bench)          # what the adapters' wire() write: doors, cards, launchers
    doors = [one.name for one in r9.iterdir() if one.name in wirings] if r9.is_dir() else ["?"]
    ended_by = [one.get("agent") for one in squad_events if one.get("kind") == "wake-ended"]
    looked = h.call("team", "status", "squad")
    outside = h.call("team", "start", "outside", "--message", "x", "--no-tick")
    if (squad.returncode == 0 and resolved and h.agent_stands("squad/r9") and not doors
            and (h.teams / "squad" / "TURN.md").is_file() and not (h.meta_of("squad/r9") / "procs" / "TURN.md").exists()
            and not (h.ws / "agents" / "squad").exists()
            and ended_by == ["r9"] and looked.returncode == 0 and "r9 · squad/r9 · inbox" in looked.stdout
            and outside.returncode == 2 and "team-invalid" in outside.stderr and "../x" in outside.stderr
            and not h.journal_of("outside").exists()):
        held("an agent is its path in a team", "the member r9 born at squad/r9/.pp, no door, the team's TURN "
             "in teams/squad/ and none at the agent, woken by the tick and ended as r9, status says `r9 · squad/r9`; "
             "`../x` refuses team-invalid, no journal")
    else:
        failures.append(f"  ✗ team agent path             rc={squad.returncode} resolved={resolved} doors={doors} "
                        f"ended={ended_by} {looked.stdout[-200:]!r} outside={outside.returncode}:{outside.stderr[-160:]!r} "
                        f"{squad.stderr[-200:]!r}")
    return 0
