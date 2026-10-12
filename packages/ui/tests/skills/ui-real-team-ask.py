"""Scenario `ui-real-team-ask` -- a question of a member to the owner, open in the thread of its task, on the
REAL verbs of `team` (plan ui, batch le-reel-des-equipes), its wake-ups played by the team witness, never a
provider: `dev` asks the owner a question; on the Tasks tab, `enter` on T1 opens its thread, which shows it `[open]`
(the reply to it is `ui-real-team-pilot`'s); the cost of the kept flow of one exchange of `dev`'s real wake-up,
`agent flow <path> <run> --exchange 1 --json` -- what the band of a task reads at each step --, measured in seconds
and bytes (batch le-suivi-des-taches)
"""
from __future__ import annotations

import time

from tests.harness import support

R = support(__file__, "real_team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team, ask, owner, begun = R.asking(bench, "ui-real-team-ask")
    asked = bool(ask)

    # --- the question, open in the thread -----------------------------------------------------------
    shown = team.render("--render", "tasks", "--size", "200x50", "--press", "enter")
    line = next((one for one in shown.stdout.split("\n") if f"#{ask.get('id')} " in one and "→" in one), "")
    if begun and asked and ask.get("to") == owner and "[open]" in line:
        held("a question to the owner is open in the thread", f"#{ask.get('id')} ask from dev to {owner} [open]")
    else:
        failures.append(f"  ✗ question open               begun={begun} asked={asked} ask={ask} owner={owner!r} "
                        f"{line!r} {shown.stdout[-1500:]!r}")

    # --- the cost of the kept flow of one exchange, on the real verb ------------------------------------
    member = next((one for one in team.state().get("members") or [] if one.get("member") == "dev"), {})
    began = time.monotonic()
    read = team.call("agent", "flow", str(member.get("path")), str(member.get("run")), "--exchange", "1", "--json")
    spent = time.monotonic() - began
    kinds = [line.split('"kind": "', 1)[1].split('"', 1)[0] for line in read.stdout.splitlines() if '"kind": "' in line]
    if read.returncode == 0 and "opened" in kinds and "verdict" in kinds:
        held("the kept flow of one exchange, measured", f"agent flow {member.get('path')} {member.get('run')} --exchange 1 "
             f"--json: {spent:.2f} s, {len(read.stdout.encode())} bytes, {len(kinds)} events")
    else:
        failures.append(f"  ✗ flow measured               rc={read.returncode} {member} {kinds} {read.stderr[-300:]!r}")

    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
