"""Scenario `team-grammar` -- 3 case(s) (batches la-grammaire-des-reveils, 2026-10-09, and la-grammaire-par-defaut,
2026-10-11): `team start` takes `--provider` beside `--harness` -- the grammar `pp-agent` reads the command's output
in, kept at `team-started.launch` and passed to every `agent start`; without it the start refuses.
- `--harness <witness> --provider <the other grammar>`: the witness answers in that grammar; `team-started.launch`
  keeps both, the wake-up ends (`wake-ended`) and the task is `done` with the answer read in that grammar
- `--harness <witness> --provider <the witness's grammar>`: the task `done` with the answer
- `--harness` alone refuses `grammar-missing` before anything is written: no `team-started`, no task, no agent born
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "g": [{"sleep": 0.1, "body": {"done": "read in the other grammar"}, "grammar": T.OTHER_GRAMMAR}],
        "c": [{"sleep": 0.1, "body": {"done": "read in the witness's grammar"}}]})

    # --- --provider beside --harness: the grammar passed to every wake-up ---------------------------
    h.declare("grammar", "---\nagents: |\n  g g\nroot: g\nschedule: off\n---\nAnswer in JSON.\n")
    started = h.call("team", "start", "grammar", "--message", "say it", *T.harnessing(h.harness, T.OTHER_GRAMMAR))
    done = h.settled("grammar", lambda found: bool(T.by_kind(found, "done")), timeout=60)
    found = h.events("grammar")
    launch = next((one.get("launch") for one in found if one.get("kind") == "team-started"), {})
    ended = T.by_kind(found, "wake-ended")
    if (started.returncode == 0 and done and launch == {"harness": h.harness, "provider": T.OTHER_GRAMMAR}
            and len(ended) == 1 and T.result_of(found, "T1") == "read in the other grammar"):
        held("--provider names the grammar of the team's --harness", f"team-started.launch {sorted(launch)}; the "
             f"wake-up ended (run {ended[0].get('run')}), T1 done with the answer read in {T.OTHER_GRAMMAR}'s grammar")
    else:
        failures.append(f"  ✗ provider beside harness     rc={started.returncode} {started.stderr[-200:]!r} done={done} "
                        f"launch={launch} kinds={[one.get('kind') for one in found]}")

    # --- the witness's grammar named: the task done ------------------------------------------------------
    h.declare("plain", "---\nagents: |\n  c c\nroot: c\nschedule: off\n---\nAnswer in JSON.\n")
    plain = h.call("team", "start", "plain", "--message", "say it", *h.harnessed)
    done_c = h.settled("plain", lambda found: bool(T.by_kind(found, "done")), timeout=60)
    found_c = h.events("plain")
    launch_c = next((one.get("launch") for one in found_c if one.get("kind") == "team-started"), {})
    if (plain.returncode == 0 and done_c and launch_c == {"harness": h.harness, "provider": T.WITNESS_GRAMMAR}
            and T.result_of(found_c, "T1") == "read in the witness's grammar"):
        held("--harness with the witness's grammar", f"team-started.launch {sorted(launch_c)}; T1 done with the answer")
    else:
        failures.append(f"  ✗ witness's grammar           rc={plain.returncode} {plain.stderr[-200:]!r} done={done_c} "
                        f"launch={launch_c} kinds={[one.get('kind') for one in found_c]}")

    # --- --harness alone: refused before anything is written --------------------------------------------
    h.declare("bare", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\n---\nAnswer in JSON.\n")
    alone = h.call("team", "start", "bare", "--message", "say it", "--harness", h.harness)
    if (alone.returncode == 2 and "grammar-missing" in alone.stderr and h.events("bare") == []
            and not (h.ws / "agents" / "b").exists()):
        bench.refusals += 1
        held("--harness alone refuses", "grammar-missing, exit 2: no team-started, no task, no agent born")
    else:
        failures.append(f"  ✗ harness alone               rc={alone.returncode} {alone.stderr[-200:]!r} "
                        f"kinds={[one.get('kind') for one in h.events('bare')]} born={(h.ws / 'agents' / 'b').exists()}")
    return 0
