"""Scenario `team-roster` -- 5 case(s) (batch le-roster-et-son-contributeur): `team roster [--json]` READS the teams
of the HOUSE -- every team and every live recurrence, whatever instance calls it -- with the caller's MEMBERSHIP; the
contributor `TEAM_ROSTER` serves it at the start of an exchange outside the team's runs alone. One house, two teams:
`alpha` (lead at agents/lead, its root; scout at agents/scout) started on one task, `beta` (chief at agents/chief, its
root; helper at agents/helper) started without one, a recurrence described laid on it; agents/loner in no team.
`alpha` writes its root and its edge; `beta` names the preset `teams/supervisor-workers` and writes neither: its root is
the one the template's form makes of its members.
- (a) a house without a team: `roster` and `roster --json` say nothing, rc 0
- (b) the house's roster: one row per team -- `team`, `name`, `description`, `root` (beta's the form's, `chief`),
  `members`, `state`,
  `membership` `—` from the house --, one row per live recurrence -- `team`, `id`, `description`, `when`, `next_due`,
  `paused` --; nothing written (the team's records and directories byte-identical)
- (c) the roster read from an agent: the same teams and recurrences as the house's, the membership the caller's --
  `root (lead)` at agents/lead for alpha, `member (helper)` at agents/helper for beta, `—` elsewhere and at agents/loner
- (d) the contributor: a run of agents/loner and a run of agents/lead opened OUTSIDE a team receive the reading
  `team-roster` at their first output, the latter with its membership; lead's run of the team never receives it;
  the reading's size in characters said
- (e) the owner's inbox outside the team's runs alone: `team inbox` played from agents/lead says alpha's T1 done; the
  same call in a run of alpha (its root of documents, `PP_DOCUMENTS`) says nothing, rc 0 -- the contributor
  `TEAM_INBOX` serves nothing to a member
"""
from __future__ import annotations

import json
import re

from tests.harness import cli, support

T = support(__file__, "team")
ALPHA = "---\ndescription: Ships the alpha work.\nagents: |\n  lead agents/lead\n  scout agents/scout\n" \
        "reports: |\n  scout -> lead\nroot: lead\nschedule: off\n---\nShip it.\n"
BETA = "---\ntemplate: teams/supervisor-workers\nagents: |\n  chief agents/chief\n  helper agents/helper\n" \
       "schedule: off\n---\nKeep it.\n"
DAILY = "Sorts the inbox every morning."
READING = "INFORMATION — team-roster"
SHAPE = ("team", "name", "description", "root", "members", "state")


def _opened(h, path: str) -> str:
    """-> what a run of the agent opened WITHOUT a team's root serves, chunk after chunk."""
    meta = h.meta_of(path)
    opened = cli(h.engine, "--instance", str(meta), "-new", cwd=meta.parent, env=h.env)
    chunks = [opened.stdout]
    key = re.search(r"run ([0-9a-f]{6})", opened.stdout)
    for _ in range(12):
        if not key or "a reading continues" not in chunks[-1]:
            break
        chunks.append(cli(h.engine, "--instance", str(meta), key.group(1), cwd=meta.parent, env=h.env).stdout)
    return "".join(chunks)


def _section(output: str) -> str:
    """-> the `team-roster` reading of an output, its heading to the next section; "" when absent."""
    at = output.find(READING)
    if at < 0:
        return ""
    ends = [one for one in (output.find("\n▌ ", at), output.find("\n▶ ", at)) if one >= 0]
    return output[at:min(ends)] if ends else output[at:]


def _roster(h, path: str | None = None):
    """-> (rc, `roster --json` read -- {} when it says nothing --, its stdout), played at the house or at an agent."""
    meta = h.house if path is None else h.meta_of(path)
    played = cli(h.engine, "--instance", str(meta), "team", "roster", "--json", cwd=h.ws, env=h.env)
    try:
        return played.returncode, (json.loads(played.stdout) if played.stdout.strip() else {}), played.stdout
    except ValueError:
        return played.returncode, {"unreadable": played.stdout[-200:]}, played.stdout


def _tree(*roots) -> dict[str, bytes]:
    return {str(one): one.read_bytes() for root in roots if root.is_dir() for one in sorted(root.rglob("*"))
            if one.is_file()}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"lead": [{"sleep": 0.1, "body": {"done": "shipped"}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (a) a house without a team -----------------------------------------------------------------------------
    bare_json = h.call("team", "roster", "--json")
    bare_text = h.call("team", "roster")
    if (bare_json.returncode == 0 and bare_text.returncode == 0 and not bare_json.stdout.strip()
            and not bare_text.stdout.strip()):
        held("(a) a house without a team says nothing", "roster and roster --json: rc 0, no output")
    else:
        failures.append(f"  ✗ (a) a house without a team    rc={bare_json.returncode}/{bare_text.returncode} "
                        f"out={bare_json.stdout[-120:]!r}/{bare_text.stdout[-120:]!r} {bare_json.stderr[-160:]!r}")

    # --- two teams, a recurrence, an agent of no team ------------------------------------------------------------
    h.declare("alpha", ALPHA)
    h.declare("beta", BETA)
    h.call("agent", "add", "agents/loner")
    alpha = h.call("team", "start", "alpha", "--message", "ship", *h.harnessed)
    beta = h.call("team", "start", "beta", "--no-tick", *h.harnessed)
    laid = h.call("team", "post", "beta", "--to", "chief", "--message", "sort", "--every", "day 09:30",
                  "--description", DAILY, "--no-tick")
    shipped = h.settled("alpha", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 15)

    # --- (b) the house's roster ----------------------------------------------------------------------------------
    records = h.records / "teams"
    before = _tree(records, h.teams)
    rc_house, house, _ = _roster(h)
    after = _tree(records, h.teams)
    teams = {one.get("team"): one for one in house.get("teams") or []}
    recurrences = house.get("recurrences") or []
    daily = recurrences[0] if len(recurrences) == 1 else {}
    if (alpha.returncode == 0 and beta.returncode == 0 and laid.returncode == 0 and shipped and rc_house == 0
            and sorted(teams) == ["alpha", "beta"]
            and (teams["alpha"].get("description"), teams["alpha"].get("root"), teams["alpha"].get("members"))
            == ("Ships the alpha work.", "lead", 2)
            and (teams["beta"].get("description"), teams["beta"].get("root"), teams["beta"].get("members"))
            == (None, "chief", 2)
            and all(set(SHAPE) <= set(one) and one.get("membership") == "—" for one in teams.values())
            and (daily.get("team"), daily.get("id"), daily.get("description"), daily.get("paused"))
            == ("beta", "R1", DAILY, False) and "day 09:30" in str(daily.get("when")) and daily.get("next_due")
            and before == after and before):
        held("(b) the house's roster", f"alpha and beta, one row each (alpha described, beta without, its root chief "
             f"the form's), membership — "
             f"from the house; R1 of beta described, next due {daily.get('next_due')}; {len(before)} files unchanged")
    else:
        failures.append(f"  ✗ (b) the house's roster       rc={rc_house} starts={alpha.returncode}/{beta.returncode}/"
                        f"{laid.returncode} shipped={shipped} roster={house} unchanged={before == after} "
                        f"{(alpha.stderr or laid.stderr)[-160:]!r}")

    # --- (c) the roster read from an agent -----------------------------------------------------------------------
    plain = lambda face: ([{key: one.get(key) for key in SHAPE} for one in face.get("teams") or []],
                          face.get("recurrences"))
    seen = {path: _roster(h, path) for path in ("agents/lead", "agents/helper", "agents/loner")}
    membership = {path: {one.get("team"): one.get("membership") for one in face.get("teams") or []}
                  for path, (_, face, _) in seen.items()}
    wanted = {"agents/lead": {"alpha": "root (lead)", "beta": "—"},
              "agents/helper": {"alpha": "—", "beta": "member (helper)"},
              "agents/loner": {"alpha": "—", "beta": "—"}}
    if (house and all(rc == 0 and plain(face) == plain(house) for rc, face, _ in seen.values())
            and membership == wanted):
        held("(c) the roster read from an agent", "agents/lead, agents/helper and agents/loner read the house's two "
             "teams and its recurrence; membership root (lead), member (helper), — for the loner")
    else:
        failures.append(f"  ✗ (c) from an agent             rc={[one[0] for one in seen.values()]} "
                        f"membership={membership} same={[plain(one[1]) == plain(house) for one in seen.values()]} "
                        f"{[one[2][-120:] for one in seen.values()]}")

    # --- (d) the contributor: outside the team's runs alone ------------------------------------------------------
    loner_out = _section(_opened(h, "agents/loner"))
    lead_out = _section(_opened(h, "agents/lead"))
    team_run = "".join(h.prompts_of("lead"))
    if (loner_out and "alpha" in loner_out and "beta" in loner_out and "R1" in loner_out
            and lead_out and "root (lead)" in lead_out and "root (lead)" not in loner_out
            and team_run and READING not in team_run):
        held("(d) the contributor outside the team's runs", f"agents/loner's run reads team-roster "
             f"({len(loner_out)} c), agents/lead's run outside the team with root (lead) ({len(lead_out)} c); "
             f"lead's run of alpha never ({len(team_run)} c read)")
    else:
        failures.append(f"  ✗ (d) the contributor           loner={loner_out[:300]!r} lead={lead_out[:300]!r} "
                        f"team_run={len(team_run)}c reading={READING in team_run}")

    # --- (e) the owner's inbox: outside the team's runs alone --------------------------------------------------
    lead_meta = h.meta_of("agents/lead")
    outside = cli(h.engine, "--instance", str(lead_meta), "team", "inbox", cwd=h.ws, env=h.env)
    inside = cli(h.engine, "--instance", str(lead_meta), "team", "inbox", cwd=h.ws,
                 env={**h.env, "PP_DOCUMENTS": str(h.teams / "alpha")})
    if (shipped and outside.returncode == 0 and "alpha" in outside.stdout
            and inside.returncode == 0 and not inside.stdout.strip()):
        held("(e) the owner's inbox outside the team's runs", f"from agents/lead: {len(outside.stdout)} c naming "
             "alpha; in a run of alpha: nothing, rc 0")
    else:
        failures.append(f"  ✗ (e) the inbox in a team's run rc={outside.returncode}/{inside.returncode} "
                        f"outside={outside.stdout[-160:]!r} inside={inside.stdout[-160:]!r} {inside.stderr[-160:]!r}")
    return 0
