"""Scenario `team-declaration-roles` -- 5 case(s): the ROLE KEYS a `TEAM.md` declares under `roles: |`, one line
`<key> [<member> ...]` each -- read by `team declaration --json` (`declared.roles`, `declared.agents[].roles`), judged
by `start`'s own judge, kept by the season (`team-started.roles`) and followed by the gap (`pending` on `roles`). The
cases of `team-declaration` on the role keys, cut out of it by case (rule 10): its house is `_team.py`'s. No wake-up
plays: every start is `--no-tick`.
- (a) three keys declared: `make` (two members), `inspect` (a member that carries `make` too), `observe` (nobody) --
  `declared.roles` in the order declared, the reserved key with `members: []`, each member's keys on
  `declared.agents[]`, `verdict.ok` true
- (b) each defect refuses naming its cause, at the verdict of `declaration` and at `start`, nothing written: a key no
  slug, a key declared twice, a member twice on a line (`team-invalid`), a member `agents:` does not declare
  (`participant-unknown`) -- the team's directory and its journal byte for byte
- (c) free keys (G1): the same keys renamed keep their members; a team with edges, a root and a profile but no
  `roles:` has no role, whatever its links
- (d) the season: `start` keeps `team-started.roles`; `inspect` given to another member puts `roles` in `pending`, the
  season's and the declaration's; a stop and a second start empty `pending`, each `team-started` keeps its own roles; a journal
  whose `team-started` carries no `roles` reads as a team without a role
- (e) the views: a team never started under the preset `seasons/split` of `_templates.py`, `va` holding `make`, `vi`
  `inspect` -- `declared.views` says each member's keys and documents in order, each `{document, template,
  roles, effect, by}`: the notes for everyone (`served`, `head`), then the member's filtered bricks under `roles/`
  (`by` `vector`, the inspector's `mounted`, the maker's and the shared one `served`)
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
HEAD = ("---\nagents: |\n  ra agents/ra\n  rb agents/rb\n  rc agents/rc\nreports: |\n  rb rc -> ra\nroot: ra\n"
        "schedule: off\n")
ROLES = "roles: |\n  make ra rb\n  inspect rb\n  observe\n"
BODY = "---\nHold the roles.\n"


def code(said: str) -> str:
    """-> the refusal's code: the first token of what pp-team says, after its name."""
    words = said.strip().removeprefix("pp-team: ").split()
    return words[0].rstrip(":") if words else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})

    def declaration(name: str) -> dict:
        played = h.call("team", "declaration", name, "--json")
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    def faced(name: str) -> tuple[list, dict]:
        declared = declaration(name).get("declared") or {}
        return declared.get("roles"), {one.get("member"): one.get("roles") for one in declared.get("agents") or []}

    def kept(name: str) -> tuple[dict, bytes]:
        directory = h.teams / name
        files = {one.name: one.read_bytes() for one in directory.iterdir() if one.is_file()}
        journal = h.journal_of(name)
        return files, journal.read_bytes() if journal.is_file() else b""

    # --- (a) three keys declared ---------------------------------------------------------------------------
    h.declare("rl", HEAD + ROLES + BODY)
    face = declaration("rl")
    roles, by_member = faced("rl")
    if ((face.get("verdict") or {}).get("ok") is True
            and roles == [{"role": "make", "members": ["ra", "rb"]}, {"role": "inspect", "members": ["rb"]},
                          {"role": "observe", "members": []}]
            and by_member == {"ra": ["make"], "rb": ["make", "inspect"], "rc": []}):
        held("(a) three keys declared", "make ra rb, inspect rb, observe reserved: declared.roles in order, ra make, "
             "rb make and inspect, rc none, verdict ok")
    else:
        failures.append(f"  ✗ (a) three keys              verdict={face.get('verdict')} roles={roles} members={by_member}")

    # --- (b) each defect refuses, nothing written -------------------------------------------------------------
    started = h.call("team", "start", "rl", "--no-tick")
    doc = h.teams / "rl" / "TEAM.md"
    good = doc.read_text(encoding="utf-8")
    defects = {"team-invalid": ("roles: |\n  Make ra\n", "Make"),
               "team-invalid ": ("roles: |\n  make ra\n  make rb\n", "make"),
               "team-invalid  ": ("roles: |\n  make ra ra\n", "ra"),
               "participant-unknown": ("roles: |\n  make ghost\n", "ghost")}
    wrong = []
    for wanted, (lines, said) in defects.items():
        doc.write_text(good.replace(ROLES, lines), encoding="utf-8")
        before = kept("rl")
        verdict = (declaration("rl").get("verdict") or {}).get("refusal") or ""
        refused = h.call("team", "start", "rl", "--no-tick")
        if (refused.returncode != 2 or code(refused.stderr) != wanted.strip() or code(verdict) != wanted.strip()
                or said not in refused.stderr or kept("rl") != before):
            wrong.append(f"{wanted.strip()}: rc={refused.returncode} verdict={code(verdict)} "
                         f"same={kept('rl') == before} {refused.stderr.strip()[-160:]!r}")
    doc.write_text(good, encoding="utf-8")
    if started.returncode == 0 and not wrong:
        bench.refusals += len(defects)
        held("(b) each defect refuses", "a key no slug, a key twice, a member twice on a line: team-invalid; a member "
             "nobody declared: participant-unknown -- at the verdict and at start, the directory and the journal byte "
             "for byte")
    else:
        failures.append(f"  ✗ (b) defects                 rc={started.returncode} {wrong}")

    # --- (c) free keys: renamed, they keep their members; links make no role -- G1 ---------------------------
    h.declare("rr", HEAD + ROLES.replace("make", "build").replace("inspect", "check").replace("observe", "watch") + BODY)
    renamed, renamed_members = faced("rr")
    h.declare("nr", HEAD + BODY)
    profiled = h.call("team", "start", "nr", "--no-tick", "--member", "ra", "--model", "m-ra")
    none, none_members = faced("nr")
    if (renamed == [{"role": "build", "members": ["ra", "rb"]}, {"role": "check", "members": ["rb"]},
                    {"role": "watch", "members": []}]
            and renamed_members == {"ra": ["build"], "rb": ["build", "check"], "rc": []}
            and profiled.returncode == 0 and none == [] and none_members == {"ra": [], "rb": [], "rc": []}):
        held("(c) free keys", "make/inspect/observe renamed build/check/watch keep ra rb, rb, nobody; edges, a root "
             "and a profile without roles: no role -- G1")
    else:
        failures.append(f"  ✗ (c) free keys               renamed={renamed} {renamed_members} rc={profiled.returncode} "
                        f"none={none} {none_members} {profiled.stderr.strip()[-160:]!r}")

    # --- (d) the season ----------------------------------------------------------------------------------
    first = (T.by_kind(h.events("rl"), "team-started") or [{}])[-1].get("roles")
    doc.write_text(good.replace("  inspect rb\n", "  inspect rc\n"), encoding="utf-8")
    moved = {one.get("key"): one for one in declaration("rl").get("pending") or []}
    h.off_season("rl")
    again = h.call("team", "start", "rl", "--no-tick")
    settled = declaration("rl").get("pending")
    seasons = [one.get("roles") for one in T.by_kind(h.events("rl"), "team-started")]
    journal = h.journal_of("nr")
    if journal.is_file():
        journal.write_text("".join(json.dumps({key: value for key, value in one.items() if key != "roles"}) + "\n"
                                   for one in h.events("nr")), encoding="utf-8")
    bare = declaration("nr").get("pending")
    if (first == {"make": ["ra", "rb"], "inspect": ["rb"], "observe": []} and list(moved) == ["roles"]
            and moved["roles"].get("started") == first
            and moved["roles"].get("declared") == {"make": ["ra", "rb"], "inspect": ["rc"], "observe": []}
            and again.returncode == 0 and settled == []
            and seasons == [first, {"make": ["ra", "rb"], "inspect": ["rc"], "observe": []}] and bare == []):
        held("(d) the season", "team-started.roles kept; inspect to rc: pending roles, the season's and the "
             "declaration's; a second start: pending [], each season its roles; a journal without roles: no gap")
    else:
        failures.append(f"  ✗ (d) the season              first={first} moved={moved} rc={again.returncode} "
                        f"settled={settled} seasons={seasons} bare={bare} {again.stderr.strip()[-160:]!r}")

    # --- (e) the views ------------------------------------------------------------------------------------------
    S.laid(h.house / "teams" / "templates", S.SHELF)
    h.declare("vw", "---\nagents: |\n  va agents/va\n  vi agents/vi\nroot: va\nroles: |\n  make va\n  inspect vi\n"
                    "schedule: off\n---\nHold the views.\n")
    (h.teams / "vw" / "SEASON.md").write_text("---\ntemplate: seasons/split\n---\n", encoding="utf-8")
    views = {one.get("member"): one for one in (declaration("vw").get("declared") or {}).get("views") or []}

    def doc(document, template, roles, effect, by):
        return {"document": document, "template": template, "roles": roles, "effect": effect, "by": by}
    notes = doc("TEAM-vw-plain.md", "notes/plain", [], "served", "head")
    guide = doc("roles/TEAM-vw-both.md", "guide/both", ["inspect", "make"], "served", "vector")
    if (views.get("va") == {"member": "va", "roles": ["make"], "documents": [
            notes, guide, doc("roles/TEAM-vw-read.md", "sources/read", ["make"], "served", "vector")]}
            and views.get("vi") == {"member": "vi", "roles": ["inspect"], "documents": [
                notes, doc("roles/TEAM-vw-law.md", "review/law", ["inspect"], "mounted", "vector"), guide]}):
        held("(e) the views", "va: the notes by the head, both and read by its vector; vi: the notes, law "
             "mounted and both by its vector")
    else:
        failures.append(f"  ✗ (e) the views                {views}")
    return 0
