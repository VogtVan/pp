"""Scenario `team-launch` -- 5 case(s): what `team start` takes and keeps for the team's wake-ups, what it refuses,
and the machine's lock over the tick. Six teams are declared in one house, each under its own names: the maintenance
team plays alone under the lock, then the others start and run side by side.
- `--harness <witness> --provider <the other grammar>`: the witness answers in that grammar; `team-started.launch`
  keeps both, the wake-up ends (`wake-ended`) and the task is `done` with the answer read in that grammar
- `--harness` alone refuses `grammar-missing` before anything is written: no `team-started`, no task, no agent born
- the house's machine under its maintenance lock held exclusive: `team tick` refuses `maintenance-in-progress` and
  the journal gains no event; released, the tick plays
- `team start --effort low` keeps the effort among the launch flags at `team-started`, and the wake-up's
  `agent start` gets `--effort low`
- the agent's path: `r9 squad/r9` with `r9 -> m9` is born at `squad/r9/.pp` without a door and as a member (its boot
  without the catalog: `capabilities` false, read by the engine's settings face), the team's TURN written in the
  team's directory and none at the agent, woken by the tick and ended as `r9`, the face says `r9` at `squad/r9`;
  `x ../x` refuses `team-invalid`, no journal written
"""
from __future__ import annotations

from conductor import contributions, settings
from tests.harness import SOURCE, holding, load_script, support

T = support(__file__, "team")
A = contributions.module_at(SOURCE / "packages" / "agent" / "tests" / "engine" / "_agent.py")   # `harness_artifacts`


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "g": [{"sleep": 0.1, "body": {"done": "read in the other grammar"}, "grammar": T.OTHER_GRAMMAR}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- the machine under maintenance, alone in the house: the tick writes nothing -------------------------
    # played before the other teams start: the lock refuses every tick of the house while it is held
    h.declare("maint", "---\nagents: |\n  mt mt\nroot: mt\nschedule: off\n---\nUnder maintenance.\n")
    begun_m = h.call("team", "start", "maint", "--message", "x", *h.harnessed, "--no-tick")
    before_m = h.events("maint")
    with holding(h.house / ".sys" / "state" / "maintenance.lock"):
        ticked_m = h.call("team", "tick", "maint")
        under_m = h.events("maint")
    freed_m = h.call("team", "tick", "maint")
    after_m = h.events("maint")

    # --- every other team declared and started before the first wait: they run side by side ----------------
    h.declare("grammar", "---\nagents: |\n  g g\nroot: g\nschedule: off\n---\nAnswer in JSON.\n")
    h.declare("bare", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\n---\nAnswer in JSON.\n")
    h.declare("efforted", T.REVIEW)
    h.declare("squad", "---\nagents: |\n  m9 m9\n  r9 squad/r9\nreports: |\n  r9 -> m9\n"
                       "root: r9\nschedule: off\n---\nA squad whose reviewer lives under squad/.\n")
    h.declare("outside", "---\nagents: |\n  x ../x\nroot: x\nschedule: off\n---\nOutside.\n")
    started = h.call("team", "start", "grammar", "--message", "say it", *T.harnessing(h.harness, T.OTHER_GRAMMAR))
    alone = h.call("team", "start", "bare", "--message", "say it", "--harness", h.harness)
    efforted = h.call("team", "start", "efforted", "--message", "review with effort", "--effort", "low", "--no-tick")
    squad = h.call("team", "start", "squad", "--message", "review the squad's PR", *h.harnessed)
    outside = h.call("team", "start", "outside", "--message", "x", "--no-tick")

    # --- --provider beside --harness: the grammar passed to every wake-up ---------------------------
    done = h.settled("grammar", lambda found: bool(by_kind(found, "done")), timeout=60)
    found = h.events("grammar")
    launch = next((one.get("launch") for one in found if one.get("kind") == "team-started"), {})
    ended = by_kind(found, "wake-ended")
    if (started.returncode == 0 and done and launch == {"harness": h.harness, "provider": T.OTHER_GRAMMAR}
            and len(ended) == 1 and T.result_of(found, "T1") == "read in the other grammar"):
        held("--provider names the grammar of the team's --harness", f"team-started.launch {sorted(launch)}; the "
             f"wake-up ended (run {ended[0].get('run')}), T1 done with the answer read in {T.OTHER_GRAMMAR}'s grammar")
    else:
        failures.append(f"  ✗ provider beside harness     rc={started.returncode} {started.stderr[-200:]!r} done={done} "
                        f"launch={launch} kinds={[one.get('kind') for one in found]}")

    # --- --harness alone: refused before anything is written --------------------------------------------
    if (alone.returncode == 2 and "grammar-missing" in alone.stderr and h.events("bare") == []
            and not (h.ws / "agents" / "b").exists()):
        bench.refusals += 1
        held("--harness alone refuses", "grammar-missing, exit 2: no team-started, no task, no agent born")
    else:
        failures.append(f"  ✗ harness alone               rc={alone.returncode} {alone.stderr[-200:]!r} "
                        f"kinds={[one.get('kind') for one in h.events('bare')]} born={(h.ws / 'agents' / 'b').exists()}")

    # --- the machine under maintenance: the tick refuses, the journal unchanged -----------------------------
    if (begun_m.returncode == 0 and ticked_m.returncode == 2 and "maintenance-in-progress" in ticked_m.stderr
            and under_m == before_m and freed_m.returncode == 0 and len(after_m) > len(before_m)):
        held("the machine under maintenance: the tick refuses, the journal unchanged",
             f"maintenance-in-progress, {len(before_m)} events before and under; released, the tick plays")
    else:
        failures.append(f"  ✗ tick under maintenance      start={begun_m.returncode} tick rc={ticked_m.returncode} "
                        f"{ticked_m.stderr.strip()[-120:]!r} events {len(before_m)} -> {len(under_m)} -> {len(after_m)} "
                        f"freed={freed_m.returncode}")

    # --- the effort rides the launch -------------------------------------------------------------------------
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
    resolved = h.settled("squad", lambda found: any(one.get("kind") == "done" for one in found)
                         and all_ended(found), timeout=60)
    squad_events = h.events("squad")
    r9 = h.ws / "squad" / "r9"
    wirings = A.harness_artifacts(bench)          # what the adapters' wire() write: doors, cards, launchers
    doors = [one.name for one in r9.iterdir() if one.name in wirings] if r9.is_dir() else ["?"]
    ended_by = [one.get("agent") for one in squad_events if one.get("kind") == "wake-ended"]
    face = h.face("squad")
    paths = {one.get("member"): one.get("path") for one in face.get("members") or []}
    profile = settings.referenced(h.meta_of("squad/r9"), "@SETTINGS.capabilities") if h.agent_stands("squad/r9") else ""
    if (squad.returncode == 0 and resolved and h.agent_stands("squad/r9") and not doors and profile.lower() == "false"
            and (h.teams / "squad" / "TURN.md").is_file() and not (h.meta_of("squad/r9") / "procs" / "TURN.md").exists()
            and not (h.ws / "agents" / "squad").exists()
            and ended_by == ["r9"] and paths == {"m9": "m9", "r9": "squad/r9"}
            and outside.returncode == 2 and "team-invalid" in outside.stderr
            and not h.journal_of("outside").exists()):
        held("an agent is its path in a team", "the member r9 born at squad/r9/.pp, no door, capabilities false, the "
             "team's TURN in teams/squad/ and none at the agent, woken by the tick and ended as r9, the face says r9 at "
             "squad/r9; `../x` refuses team-invalid, no journal")
    else:
        failures.append(f"  ✗ team agent path             rc={squad.returncode} resolved={resolved} doors={doors} "
                        f"profile={profile!r} ended={ended_by} paths={paths} "
                        f"outside={outside.returncode}:{outside.stderr[-160:]!r} {squad.stderr[-200:]!r}")
    return 0
