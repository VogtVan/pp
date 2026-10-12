"""Scenario `ui-real-team-start` -- a team started from the post on the REAL verbs of `team` (plan ui, batch
le-reel-des-equipes), its wake-ups played by the team witness, never a provider:
- `S` on `essai`, never started: its first season (batch l-overlay-de-saison), its lines left as they open, a
  message -- the command shown carries the `--harness` given after `--` to `./pp ui`
- `enter` plays the real `team start`: the journal says `team-started` with that harness under `launch`; the
  post follows the team until its task is done -- T1 `resolved`, `lead` `ended` with its run, the house's
  `responses.jsonl` with its answer; no process of the witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
KEYS = "S,g,o"


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-start", {"lead": [{"body": {"done": "started from the post"}}]})

    shown = team.render("--render", "teams", "--size", "200x50", "--press", KEYS)
    flat = _flat(shown.stdout)
    if shown.returncode == 0 and "./pp team start essai --message go" in flat and "--harness" in flat and team.events() == []:
        held("S shows the start with the harness of the post", "./pp team start essai --message go … --harness <the witness>; "
             "nothing written before enter")
    else:
        failures.append(f"  ✗ start shown                 rc={shown.returncode} {shown.stdout[-1500:]!r} {shown.stderr[-300:]!r}")

    done = team.render("--render", "teams", "--size", "200x50", "--press", KEYS + ",enter", "--wait", "team:done:40")
    flat = _flat(done.stdout)
    started = team.kinds("team-started")
    harness = ((started[0].get("launch") or {}).get("harness")) if started else None
    grammar = ((started[0].get("launch") or {}).get("provider")) if started else None
    finished = team.kinds("done", task="T1")
    state = team.state()
    lead = next((one for one in state.get("members") or [] if one.get("member") == "lead"), {})
    if (done.returncode == 0 and harness == team.harness and grammar == R.WITNESS_GRAMMAR and finished and lead.get("how") == "ended" and lead.get("run")
            and "resolved" in flat and lead["run"] in flat and len(team.responses()) == 1 and not team.alive()):
        held("the real start, followed to its end", f"team-started.launch.harness the witness, its grammar beside it; done T1; lead ended, run "
             f"{lead['run']} on the tab; responses.jsonl 1 line; no witness left")
    else:
        failures.append(f"  ✗ real start                  rc={done.returncode} harness={harness!r} grammar={grammar!r} done={finished} lead={lead} "
                        f"responses={len(team.responses())} alive={team.alive()} {done.stdout[-1500:]!r} {done.stderr[-400:]!r}")
    return 0
