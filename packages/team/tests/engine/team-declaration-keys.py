"""Scenario `team-declaration-keys` -- 5 case(s) (split out of `team-declaration` by rule 10): the keys a
`TEAM.md` writes about the team itself -- its limits, its members' names and paths, its name, its description --
judged by `team start` and said by `team declaration`. No wake-up plays: every start is `--no-tick`.
- (e) a limit mis-written refuses: `parallel: 0`, `budget: free`, `retries: -1`, `timeout: soon`, `launches: 0`,
  `budget-launches: -1` -- `team-invalid` naming the key, no agent born, no journal
- (f) the name and the path judged: a name with `/`, a name declared twice, a path out of the house -- `team-invalid`
  naming them, no journal, no agent born
- (g) a team renamed: `name: Revue PR` written in the `TEAM.md` of a team at work -- the faces (`status`, `status
  <name>`, `declaration`) say `team` its directory and `name` the new name, at once and without a start; a post and
  a tick after it leave the journal's `team`, the calendar's mark and the directory as they were; a name of 81
  characters refuses `name-invalid` at the start, nothing written
- (h) a team described: `description:` in the `TEAM.md` of a team at work -- `status --json` (with and without a
  name) and `declaration --json` say `description`, a team without the key `null`; the journal carries no
  `description` key; a description rewritten is read at the next call, without a start; a description of two lines
  or of 201 characters refuses `team-invalid` at the start and is said refused by `declaration` (`description`
  `null`), the journal and `TEAM.md` byte-identical across the refusal
- (i) the bound of the team written by `declare`: `team declare <team> --parallel 2 --json` writes `parallel: 2`, the
  rest of `TEAM.md` at its bytes, `written` `["parallel"]`, the verdict ok; `--parallel 0` refuses `team-invalid`
  naming `parallel`, `--season --parallel 2` the usage (a key of `TEAM.md` alone) -- `TEAM.md` byte-identical across
  both refusals
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")
code = T.refusal_code


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={}, packages=("agent", "team", "steering", "plan"))

    def declaration(name: str) -> dict:
        return T.declaration_read(h, name)

    # --- (e) a limit mis-written refuses before anything is written -------------------------------
    limits = {"bad-par": ("z1", "parallel: 0", "parallel"), "bad-bud": ("z2", "budget: free", "budget"),
              "bad-ret": ("z3", "retries: -1", "retries"), "bad-tmo": ("z4", "timeout: soon", "timeout"),
              "bad-wak": ("z5", "launches: 0", "launches"), "bad-bwk": ("z6", "budget-launches: -1", "budget-launches")}
    for name, (agent, line, _key) in limits.items():
        h.declare(name, f"---\nagents: |\n  {agent} {agent}\nroot: {agent}\n{line}\n---\n")
    bad = {name: h.call("team", "start", name, "--message", "x", "--no-tick") for name in limits}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == "" for one in bad.values())
            and all(key in bad[name].stderr for name, (_agent, _line, key) in limits.items())
            and not any(h.agent_stands(agent) for agent, _line, _key in limits.values())
            and not any(h.journal_of(name).exists() for name in bad)):
        held("(e) a limit mis-written refuses", "parallel 0, budget free, retries -1, timeout soon, launches 0, "
             "budget-launches -1: team-invalid naming the key; no agent, no journal")
    else:
        failures.append("  ✗ (e) limits invalid          " + " ".join(f"{name}={one.returncode}:{one.stderr[-100:]!r}"
                                                                      for name, one in bad.items()))

    # --- (f) the name and the path judged -----------------------------------------------------------
    h.declare("slashed", "---\nagents: |\n  nm/r9 agents/r9\nroot: nm/r9\nschedule: off\n---\nA name with a slash.\n")
    h.declare("twice", "---\nagents: |\n  dn agents/a1x\n  dn agents/b1x\nroot: dn\nschedule: off\n---\nOne name twice.\n")
    h.declare("escaped", "---\nagents: |\n  ex ../x\nroot: ex\nschedule: off\n---\nA path out of the house.\n")
    judged = {name: h.call("team", "start", name, "--message", "x", "--no-tick") for name in ("slashed", "twice", "escaped")}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == "" for one in judged.values())
            and "nm/r9" in judged["slashed"].stderr and "dn" in judged["twice"].stderr and "../x" in judged["escaped"].stderr
            and not any(h.journal_of(name).exists() for name in judged)
            and not any(path.exists() for path in (h.ws / "nm", h.ws / "agents" / "r9", h.ws / "agents" / "a1x",
                                                   h.ws / "agents" / "b1x", h.ws / "ex", h.ws.parent / "x"))):
        held("(f) the name and the path judged", "a name with `/`, a name declared twice, a path out of the "
             "house: team-invalid naming them, no journal, no agent born")
    else:
        failures.append("  ✗ (f) name and path judged    "
                        + " ".join(f"{name}={one.returncode}:{one.stdout[-80:]!r}:{one.stderr[-100:]!r}" for name, one in judged.items()))
    # --- (g) a team renamed: the name moves, the identity stays ------------------------------------------
    h.declare("rn", "---\nagents: |\n  r agents/r\nroot: r\nschedule: 1\n---\nRename me.\n")
    opened = h.call("team", "start", "rn", "--message", "go", "--no-tick")
    mark = f"# pp-team {h.house}\n"                     # the house's one line, whatever its teams' names
    table = h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else ""
    declared_rn = h.teams / "rn" / "TEAM.md"
    declared_rn.write_text(declared_rn.read_text(encoding="utf-8").replace("---\nagents:", "---\nname: Revue PR\nagents:", 1),
                           encoding="utf-8")
    posted = h.call("team", "post", "rn", "--message", "again", "--no-tick")
    one_face = h.face("rn")
    listed = h.call("team", "status", "--json")
    badges = {one.get("team"): one for one in map(json.loads, listed.stdout.splitlines())} if listed.returncode == 0 else {}
    read_rn = declaration("rn")
    kinds = {one.get("team") for one in h.events("rn")}
    table_after = h.crontab.read_text(encoding="utf-8") if h.crontab.is_file() else ""
    h.declare("long", f"---\nname: {'x' * 81}\nagents: |\n  l agents/l\nroot: l\nschedule: off\n---\nToo long.\n")
    too_long = h.call("team", "start", "long", "--message", "x", "--no-tick")
    if (opened.returncode == 0 and posted.returncode == 0 and mark in table and table_after == table
            and one_face.get("team") == "rn" and one_face.get("name") == "Revue PR"
            and (badges.get("rn") or {}).get("name") == "Revue PR" and read_rn.get("name") == "Revue PR"
            and kinds == {"rn"} and (h.teams / "rn").is_dir()
            and too_long.returncode == 2 and "name-invalid" in too_long.stderr and not h.journal_of("long").exists()):
        bench.refusals += 1
        held("(g) a team renamed", "name: Revue PR on rn at work: status, status rn and declaration say team rn, name "
             "Revue PR; the journal's team, the calendar's mark and the directory unchanged across a post; 81 "
             "characters refuse name-invalid, no journal")
    else:
        failures.append(f"  ✗ (g) renamed                rc={opened.returncode}/{posted.returncode}/{too_long.returncode} "
                        f"mark={mark in table} same_table={table_after == table} face={one_face.get('team')}/"
                        f"{one_face.get('name')} badge={(badges.get('rn') or {}).get('name')} read={read_rn.get('name')} "
                        f"kinds={kinds} {(opened.stderr or posted.stderr or too_long.stderr).strip()[-200:]!r}")
    # --- (h) a team described: read at every call, never written to the journal ---------------------------------
    said_first, said_then = "Reviews the open PRs.", "Reviews the open PRs and merges the ready ones."
    plain = "---\nagents: |\n  dr agents/dr\nroot: dr\nschedule: off\n---\nDescribe me.\n"
    h.declare("ds", plain.replace("---\nagents:", f"---\ndescription: {said_first}\nagents:", 1))
    h.declare("nd", plain.replace("dr", "nr"))
    ds_doc = h.teams / "ds" / "TEAM.md"
    begun = h.call("team", "start", "ds", "--message", "go", "--no-tick")
    one_face, read_ds, read_nd = h.face("ds"), declaration("ds"), declaration("nd")
    badges = {one.get("team"): one for one in h.face()}
    journal_keys = {key for one in h.events("ds") for key in one}
    ds_doc.write_text(ds_doc.read_text(encoding="utf-8").replace(said_first, said_then), encoding="utf-8")
    rewritten = (h.face("ds").get("description"), declaration("ds").get("description"))
    refusals = {}
    for label, bad in (("two lines", f"description: |\n  {said_first}\n  A second line.\n"),
                       ("201 characters", f"description: {'x' * 201}\n")):
        ds_doc.write_text(plain.replace("---\nagents:", f"---\n{bad}agents:", 1), encoding="utf-8")
        before = (h.journal_of("ds").read_bytes(), ds_doc.read_bytes())
        again = h.call("team", "start", "ds", "--message", "again", "--no-tick")
        verdict = declaration("ds")
        refusals[label] = (again.returncode, code(again.stderr), code((verdict.get("verdict") or {}).get("refusal") or ""),
                           "description" in verdict and verdict["description"] is None,
                           (h.journal_of("ds").read_bytes(), ds_doc.read_bytes()) == before)
    if (begun.returncode == 0 and one_face.get("description") == said_first and read_ds.get("description") == said_first
            and (badges.get("ds") or {}).get("description") == said_first
            and "description" in read_nd and read_nd["description"] is None
            and "description" in (badges.get("nd") or {}) and badges["nd"]["description"] is None
            and "description" not in journal_keys and rewritten == (said_then, said_then)
            and all(one == (2, "team-invalid", "team-invalid", True, True) for one in refusals.values())):
        bench.refusals += 2
        held("(h) a team described", "status (with and without a name) and declaration say the description, null "
             "without the key; no journal key; rewritten, read at the next call; two lines and 201 characters refuse "
             "team-invalid, the journal and TEAM.md byte-identical")
    else:
        failures.append(f"  ✗ (h) described              rc={begun.returncode} face={one_face.get('description')!r} "
                        f"declaration={read_ds.get('description')!r}/{read_nd.get('description', '?')!r} "
                        f"badges={[(one, (badges.get(one) or {}).get('description', '?')) for one in ('ds', 'nd')]} "
                        f"journal_keys={'description' in journal_keys} rewritten={rewritten} refusals={refusals} "
                        f"{begun.stderr.strip()[-160:]!r}")

    # --- (i) the bound of the team written by `declare` ---------------------------------------------------------------
    h.declare("pl", "---\nagents: |\n  pa agents/pa\nroot: pa\nschedule: off\n---\nBound me.\n")
    pl_doc = h.teams / "pl" / "TEAM.md"
    stood = pl_doc.read_text(encoding="utf-8")
    bound = h.call("team", "declare", "pl", "--parallel", "2", "--json")
    try:
        bound_face = json.loads(bound.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        bound_face = {}
    written = pl_doc.read_text(encoding="utf-8")
    lines = written.splitlines(keepends=True)
    zero = h.call("team", "declare", "pl", "--parallel", "0", "--json")
    seasoned = h.call("team", "declare", "pl", "--season", "--parallel", "2", "--json")
    if (bound.returncode == 0 and lines.count("parallel: 2\n") == 1
            and "".join(one for one in lines if one != "parallel: 2\n") == stood
            and bound_face.get("written") == ["parallel"] and (bound_face.get("verdict") or {}).get("ok") is True
            and zero.returncode == 2 and code(zero.stderr) == "team-invalid" and "parallel" in zero.stderr
            and seasoned.returncode == 2 and "usage" in seasoned.stderr
            and pl_doc.read_text(encoding="utf-8") == written and not (h.teams / "pl" / "SEASON.md").exists()):
        bench.refusals += 2
        held("(i) the bound written by declare", "--parallel 2 writes parallel: 2, the rest of TEAM.md at its bytes, "
             "written [parallel], verdict ok; --parallel 0 refuses team-invalid, --season --parallel 2 the usage, "
             "TEAM.md byte-identical")
    else:
        failures.append(f"  ✗ (i) parallel declared       rc={bound.returncode}/{zero.returncode}/{seasoned.returncode} "
                        f"face={bound_face} file={written!r} {(bound.stderr or zero.stderr or seasoned.stderr).strip()[-200:]!r}")

    return 0
