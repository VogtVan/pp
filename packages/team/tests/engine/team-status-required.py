"""Scenario `team-status-required` -- 2 case(s) (batch les-packages-requis, 2026-10-12: team 0.32.1): `team status
--json` says `required`, the packages a member may not switch off -- `team` and what it requires --, the very list
the judge of `package-required` names; on a house pinning `agent`, `team`, `steering` and `plan`, a team `crew`
started (`--no-tick`) and a team `none` never started:
- (a) the face says them (KPQ1): the object of `crew`, the object of `none` and each line without a name carry
  `required`, sorted, `team` in it, `plan` and `steering` out of it -- the same names `team start --member n
  --package agent=off` refuses `package-required` with
- (b) nothing else moves (KPQ2): the text of `status crew` the same bytes before and after the faces are read
"""
from __future__ import annotations

import hashlib
import json
import re

from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={})

    def face(*name: str) -> list[dict]:
        played = cli(h.engine, "--instance", str(h.house), "team", "status", *name, "--json", cwd=h.ws, env=h.env)
        try:
            return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            return []

    def text_sha() -> str:
        return hashlib.sha256(h.call("team", "status", "crew").stdout.encode()).hexdigest()[:12]

    h.declare("crew", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\nKeep going.\n")
    h.declare("none", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    h.call("team", "start", "crew", "--message", "go", *h.harnessed, "--no-tick")
    before = text_sha()

    # --- (a) the face says them -- KPQ1 ------------------------------------------------------------------------
    named, never, lines = face("crew"), face("none"), face()
    refused = h.call("team", "start", "none", "--message", "x", *h.harnessed, "--no-tick",
                     "--member", "n", "--package", "agent=off")
    judged = re.search(r"the team needs it \(([^)]*)\)", refused.stderr)
    needed = sorted(one.strip() for one in judged.group(1).split(",")) if judged else None
    said = [(one.get("team"), one.get("required")) for one in named + never + lines]
    if (needed and "team" in needed and "plan" not in needed and "steering" not in needed
            and len(said) == 4 and all(required == needed for _, required in said)):
        held("(a) the face says the required packages", f"{needed} on crew, on none never started and on each "
             "line -- the names package-required gives -- KPQ1")
    else:
        failures.append(f"  ✗ (a) required              needed={needed} said={said} {refused.stderr[-200:]!r}")

    # --- (b) nothing else moves -- KPQ2 ------------------------------------------------------------------------
    after = text_sha()
    if before == after and set(never[0] if never else {}) == {"team", "started", "state", "waiting_on", "required"}:
        held("(b) the text keeps its bytes", f"status crew sha {before} before and after; none says "
             "{team, started, state, waiting_on, required} -- KPQ2")
    else:
        failures.append(f"  ✗ (b) bytes                  {before} {after} {never}")
    return 0
