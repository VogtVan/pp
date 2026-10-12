"""Scenario `team-season-profiles` -- 1 case(s) (batch la-saison, 2026-10-12: row 82 of the study § 18, team 0.31.0):
`--member <name>` gives a member its PROFILE for the season -- its model, effort, permissions, provider and package
switches over the team's flags --, replayed at each of its wake-ups in its run; TEAM.md stays without provider or
package. On a house pinning `agent`, `team`, `steering` and `plan`. The season itself is `team-season`'s, the
refusals `team-season-refusals`'s.
- (a) a member's profile (KS15): `--member b --model m2 --effort high --package plan=off` -- b's messages carry
  `{model: m2, effort: high}`, its run plays `plan` off, a keeps the team's launch; `members[].launch` says it;
  TEAM.md the same to the byte
"""
from __future__ import annotations

import hashlib
import json

from conductor import persistence
from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={
        "a": [{"sleep": 0.1, "body": {"do": ["b"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "b": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def face(name: str) -> dict:
        played = cli(h.engine, "--instance", str(h.house), "team", "status", name, "--json", cwd=h.ws, env=h.env)
        try:
            return json.loads(played.stdout)
        except ValueError:
            return {}

    def policies(path: str) -> list[dict]:
        return [one.get("policy") or {} for one in T.lines(h.records / "messages.jsonl") if one.get("to") == path]

    # --- (a) a member's profile -- KS15 ---------------------------------------------------------------------
    h.declare("prof", "---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n"
                      "---\nTwo profiles.\n")
    doc = h.teams / "prof" / "TEAM.md"
    sha = hashlib.sha256(doc.read_bytes()).hexdigest()
    started = h.call("team", "start", "prof", "--message", "review PR 15", *h.harnessed,
                     "--member", "b", "--model", "m2", "--effort", "high", "--package", "plan=off")
    done = h.settled("prof", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("prof")
    run_b = next((one.get("run") for one in by_kind(found, "wake-launched", agent="b")), "")
    off_b = persistence.off_of(persistence.slot_of(h.meta_of("agents/b"), run_b)) if run_b else ["?"]
    members = {one.get("member"): one.get("launch") for one in face("prof").get("members") or []}
    if (started.returncode == 0 and done and policies("agents/b") and all(p.get("model") == "m2" and p.get("effort") == "high"
                                                                          for p in policies("agents/b"))
            and all("model" not in p for p in policies("agents/a")) and off_b == ["plan"]
            and (members.get("b") or {}).get("model") == "m2" and (members.get("b") or {}).get("packages") == ["plan=off"]
            and (members.get("a") or {}).get("model") is None and (members.get("a") or {}).get("packages") == []
            and hashlib.sha256(doc.read_bytes()).hexdigest() == sha):
        held("(a) a member's profile", f"b on m2/high with plan off in its run {run_b}, a on the team's launch; "
             "members[].launch says it; TEAM.md the same to the byte -- KS15")
    else:
        failures.append(f"  ✗ (a) a member's profile     rc={started.returncode} done={done} b={policies('agents/b')} "
                        f"a={policies('agents/a')} off={off_b} members={members} {started.stderr.strip()[-200:]!r}")

    return 0
