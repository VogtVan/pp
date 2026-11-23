"""Scenario `team-season-stopped-paused` -- 2 case(s): the stop of a SEASON names silenced only the recurrences it
silences -- live and not paused, as the post names them (batch les-recurrences-tues-a-l-arret, s.1595) -- under a frozen
clock (`PP_NOW`, Thursday). The sibling of `team-season-cycle`. No wake-up plays: every call is `--no-tick` but the
pauses.
- (a) a team with two recurrences, R2 paused: `team stop c --json` writes `season-stopped.recurrences` `[R1]` and its
  face says the same; `team stop d` on a twin team says `recurrences silenced: R1`, never R2
- (b) a paused one stays paused: after `team start c`, `team pause c --recurrence R2` refuses `recurrence-paused`
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")
TEAM = "---\nagents: |\n  m agents/m\nroot: m\nschedule: 5m\n---\nHold the season.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    code = T.refusal_code

    def seasoned(name: str) -> None:
        """A team in season with R1 and R2 posted, R2 paused."""
        h.declare(name, TEAM)
        h.call("team", "start", name, "--no-tick", now="08:00")
        for hour in ("09:00", "10:00"):
            h.call("team", "post", name, "--every", f"day {hour}", "--message", f"at {hour}", "--no-tick", now="08:01")
        h.call("team", "pause", name, "--recurrence", "R2", now="08:02")

    # --- (a) the stop names the live recurrences that are not paused --------------------------------------------------
    seasoned("c")
    seasoned("d")
    stopped = h.call("team", "stop", "c", "--json", "--no-tick", now="08:10")
    said = h.call("team", "stop", "d", "--no-tick", now="08:10")
    try:
        face = json.loads(stopped.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    closing = (T.by_kind(h.events("c"), "season-stopped") or [{}])[-1]
    if (stopped.returncode == 0 and said.returncode == 0 and closing.get("recurrences") == ["R1"]
            and (face.get("stopped") or {}).get("recurrences") == ["R1"]
            and "recurrences silenced: R1" in said.stdout and "R2" not in said.stdout):
        held("(a) the stop silences R1 alone, R2 paused already", f"season-stopped.recurrences {closing.get('recurrences')}; "
             f"{said.stdout.strip().splitlines()[-1][-60:]!r}")
    else:
        failures.append(f"  ✗ (a) silenced               rc={stopped.returncode}/{said.returncode} "
                        f"closing={closing.get('recurrences')} face={face} said={said.stdout.strip()[-200:]!r} "
                        f"{(stopped.stderr or said.stderr).strip()[-200:]!r}")

    # --- (b) a paused one stays paused after the next start -----------------------------------------------------------
    again = h.call("team", "start", "c", "--no-tick", now="09:30")
    paused = h.call("team", "pause", "c", "--recurrence", "R2", now="09:31")
    if again.returncode == 0 and paused.returncode == 2 and code(paused.stderr) == "recurrence-paused":
        bench.refusals += 1
        held("(b) R2 still paused after the next start", "pause --recurrence R2: recurrence-paused")
    else:
        failures.append(f"  ✗ (b) still paused           rc={again.returncode}/{paused.returncode} "
                        f"{(again.stderr or paused.stderr).strip()[-200:]!r}")
    return 0
