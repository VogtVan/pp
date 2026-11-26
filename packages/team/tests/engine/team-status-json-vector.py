"""Scenario `team-status-json-vector` -- 2 case(s): the member's vector and role keys `team status --json` says,
the case of `team-status-json` cut out of it by case (rule 10). Its house is `_team.py`'s, pinning the packages of
`team-status-json`'s.
- (c) the member's vector: a team `rv` under the preset `seasons/split` of `_templates.py`, `va` holding `make` and
  `check`, `inspect` reserved, `vn` no key, started `--no-tick` -- `members[].vector` is `team-member:rv/va` for va,
  absent for vn, whose season gives no filtered document
- (d) the member's role keys: on the same team, `members[].roles` is `["make", "check"]` for va -- the keys of `roles:`
  that name it, in the order declared --, `[]` for vn
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={})
    S.laid(h.house / "teams" / "templates", S.SHELF)
    h.declare("rv", "---\nagents: |\n  va agents/va\n  vn agents/vn\nroot: va\nroles: |\n  make va\n  check va\n  inspect\n"
                    "schedule: off\n---\nHold the vector.\n")
    (h.teams / "rv" / "SEASON.md").write_text("---\ntemplate: seasons/split\n---\n", encoding="utf-8")
    begun = h.call("team", "start", "rv", "--no-tick")
    by_member = {one.get("member"): one for one in h.face("rv").get("members") or []}
    if (begun.returncode == 0 and (by_member.get("va") or {}).get("vector") == "team-member:rv/va"
            and "vn" in by_member and "vector" not in by_member["vn"]):
        held("(c) the member's vector", "va (make, its season's documents of a role): team-member:rv/va; vn: no vector")
    else:
        failures.append(f"  ✗ (c) the member's vector    rc={begun.returncode} members={by_member} "
                        f"{begun.stderr.strip()[-200:]!r}")
    roles = {member: one.get("roles") for member, one in by_member.items()}
    if begun.returncode == 0 and roles == {"va": ["make", "check"], "vn": []}:
        held("(d) the member's role keys", "va: [make, check], in the order declared; vn: []")
    else:
        failures.append(f"  ✗ (d) the member's role keys roles={roles}")
    return 0
