"""Scenario `team-templates` -- 3 case(s): a team is born from a PRESET -- `team templates` lists every template file
the house sees (`<directory>/<name>.md` under the house's `.pp/teams/templates/` then the package's), one line each,
`team declare <name> --template teams/<t>` writes `teams/<name>/TEAM.md` naming a team preset of the package, the
declaration judged by `start`'s own judge, and `teams/<name>/TEAM-<name>.md`, the intention -- and `team start`
accepts them as they stand. No wake-up plays: every start is `--no-tick`.
- (a) the templates read: `team templates --json` says one object per file, `{template, kind, origin, description,
  values}` each -- the package's nine team presets `teams/<t>` (`kind` preset, `origin` package, with `documents`,
  `form`, `members`, `root`, `reports`, `ceremony`, `limits`, `intention`, its members and root those of the
  preset, the values each declares: `daily`, a `tree`'s `squads`, and `roles` for the five that give role
  keys: `supervisor` and `workers`, `lead` and `reviewers`, `experts`, `twins`, `specialists`), its four presets of a season `seasons/<t>` and
  its documents (`kind` document); no `template.md` listed; the text one line per file, its first word the
  template's name, and under it one line per value it declares, its first word the value's name
- (b) each team preset written then started (the first five): the `TEAM.md` written names its `template:` and lists
  its `agents:`, without `reports:` nor `root:`; `declaration --json` says `declared.template` and the root, the
  edges and the daily the form makes of the members; started, `team-started` keeps them in its own keys -- its
  members at `agents/<team>/<member>`, its root, its edges, the daily of the two forms with two members or more
  reporting to the root, the default limits (`budget: 5`, `launches: 24`, `timeout: 900`) and `schedule: off` --,
  `template` (`{template, origin}`), `values` (the values applied) and `roles` (the preset's keys); the intention
  names each member by its id; `empty` the smallest declaration -- no intention, no limit, the schedule `start`
  defaults to
- (c) the four written then started: `council`, `triage` and `cross-check` on the form `star` without a ceremony,
  `tree` with the daily of its squad leads and two levels of edges; the `TEAM.md` written, `declared` and
  `team-started` as in (b); each intention names its members by their ids, no hole of the template left in it
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
FIRST = S.FIRST
TEMPLATES = S.TEMPLATES
KEYS = S.KEYS
LINE_KEYS = S.LINE_KEYS
LIMITS = S.LIMITS
SHAPES = S.SHAPES
FORMS = S.FORMS
LISTED = S.LISTED
intention_of = S.intention_of
names_all = S.names_all
templates_of = S.templates_of
preset = S.preset


def valued(h, team: str, template: str, root: str, edges: list, daily) -> bool:
    """-> whether the `TEAM.md` `team declare` wrote names its template and its members and writes no edge and no root,
    and `declaration --json` says the template and what its form makes of the members."""
    doc = h.teams / team / "TEAM.md"
    keys = S.keys_of(doc.read_text(encoding="utf-8") if doc.is_file() else "")
    said = S.declaration_of(h, team).get("declared") or {}
    named = said.get("template") or {}
    return ("template" in keys and "agents" in keys and not {"reports", "root"} & set(keys)
            and (named.get("template"), named.get("origin")) == (preset(template), "package")
            and [(one.get("name"), one.get("value")) for one in named.get("values") or []] == S.VALUES[template]
            and said.get("root") == root and said.get("reports") == edges
            and said.get("ceremonies") == ([daily] if daily else []))


def kept(first: dict, template: str) -> bool:
    """-> whether `team-started` keeps the preset, its origin, the values applied and the preset's role keys."""
    return (first.get("template") == {"template": preset(template), "origin": "package"}
            and first.get("values", {}) == dict(S.VALUES[template]) and (first.get("roles") or {}) == S.ROLES[template])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    started_from = S.started_from

    # --- (a) the templates read -----------------------------------------------------------------
    listed = h.call("team", "templates")
    lines_said = [line for line in listed.stdout.splitlines() if line.strip()]
    said = [line.split()[0] for line in lines_said if not line.startswith(" ")]
    valued_said = {}
    for line in lines_said:
        if not line.startswith(" "):
            current = valued_said.setdefault(line.split()[0], [])
        else:
            current.append(line.split()[0])
    found = templates_of(h)
    teams = {name: one for name, one in found.items() if name.startswith(f"{S.PRESET}/")}
    seasons = sorted(name for name in found if name.startswith("seasons/") and found[name].get("kind") == "preset")
    documents = sorted(name for name, one in found.items() if one.get("kind") == "document")
    wanted_documents = sorted([f"{directory}/{one}" for directory, names in S.EXAMPLE_DOCUMENTS.items() for one in names]
                              + [f"seasons/{one}-summary" for one in S.EXAMPLE_PRESETS])
    if (listed.returncode == 0 and sorted(said) == sorted(found)
            and sorted(teams) == sorted(preset(one) for one in TEMPLATES)
            and seasons == sorted(f"seasons/{one}" for one in S.EXAMPLE_PRESETS) and documents == wanted_documents
            and not any(name.endswith("/template") for name in found)
            and all(LINE_KEYS <= set(one) and one.get("origin") == "package" for one in found.values())
            and all(set(teams[preset(one)]) == KEYS | ({"roles"} if S.ROLES[one] else set())
                    and teams[preset(one)]["kind"] == "preset" for one in TEMPLATES)
            and all({line.get("role"): line.get("places") for line in teams[preset(one)].get("roles") or []}
                    == S.PLACES[one] for one in TEMPLATES)
            and all([(value.get("name"), value.get("default")) for value in teams[preset(one)]["values"]] == S.VALUES[one]
                    for one in TEMPLATES)
            and all([name for name, _ in S.VALUES[one]] == valued_said.get(preset(one)) for one in TEMPLATES)
            and all((teams[preset(one)]["members"], teams[preset(one)]["root"]) == LISTED[one] for one in TEMPLATES)):
        held("(a) the templates read", f"one line per file: the nine team presets ({', '.join(sorted(teams))}), "
             f"{len(seasons)} presets of a season, {len(documents)} documents, no template.md; a line per value "
             f"declared under its template; --json one object per file, keys {sorted(LINE_KEYS)}, a team preset's "
             f"{sorted(KEYS - LINE_KEYS)}, `roles` for the five that give role keys "
             f"({', '.join(one for one in TEMPLATES if S.ROLES[one])})")
    else:
        failures.append(f"  ✗ (a) templates              rc={listed.returncode} said={said[:4]} teams={sorted(teams)} "
                        f"seasons={seasons} documents={documents} keys={[sorted(one) for one in list(teams.values())[:1]]} "
                        f"{listed.stderr.strip()[-160:]!r}")

    # --- (b) each of the first five written, then started ---------------------------------------
    wrong = []
    for template in FIRST:
        team = f"t-{template}"
        made = h.call("team", "declare", team, "--template", preset(template))
        members, root, edges, daily = SHAPES[template]
        written = valued(h, team, template, root, edges, daily)
        text, started, first = started_from(h, team)
        intention = intention_of(text)
        named = intention == "" if template == "empty" else names_all(intention, members)
        if not (made.returncode == 0 and (text or template == "empty") and started.returncode == 0
                and written and kept(first, template)
                and first.get("agents") == {one: f"agents/{team}/{one}" for one in members}
                and first.get("root") == root and first.get("reports") == edges
                and [one.get("text") for one in first.get("ceremonies") or []] == ([daily] if daily else [])
                and first.get("limits") == ({} if template == "empty" else LIMITS)
                and first.get("schedule") == (300 if template == "empty" else None) and named):
            wrong.append(f"{template}: rc={made.returncode}/{started.returncode} agents={first.get('agents')} "
                         f"root={first.get('root')} reports={first.get('reports')} limits={first.get('limits')} "
                         f"schedule={first.get('schedule')} named={named} written={written} "
                         f"template={first.get('template')}/{first.get('values')} "
                         f"{(made.stderr or started.stderr).strip()[-160:]!r}")
    if not wrong:
        held("(b) each template written then started", "five teams written by `team declare`, each TEAM.md naming its "
             "template and its agents, no reports nor root; declared.template and the form's root, edges and daily; "
             "started as they stand: members at agents/<team>/<member>, root, edges, the daily of the two wide "
             "forms, the default limits, schedule off, team-started.template; each intention names its members, "
             "`empty` none")
    else:
        failures.extend(f"  ✗ (b) {one}" for one in wrong)

    # --- (c) the four after them written, then started ------------------------------------------
    wrong = []
    for template, (members, root, edges, daily, limits) in FORMS.items():
        team = f"t-{template}"
        made = h.call("team", "declare", team, "--template", preset(template))
        written = valued(h, team, template, root, edges, daily)
        text, started, first = started_from(h, team)
        intention = intention_of(text)
        if not (made.returncode == 0 and started.returncode == 0 and written and kept(first, template)
                and first.get("agents") == {one: f"agents/{team}/{one}" for one in members}
                and first.get("root") == root and first.get("reports") == edges
                and [one.get("text") for one in first.get("ceremonies") or []] == ([daily] if daily else [])
                and first.get("limits") == limits and first.get("schedule") is None
                and names_all(intention, members) and not re.search(r"\{[a-z]+\}", intention)):
            wrong.append(f"{template}: rc={made.returncode}/{started.returncode} agents={first.get('agents')} "
                         f"root={first.get('root')} reports={first.get('reports')} limits={first.get('limits')} "
                         f"ceremonies={first.get('ceremonies')} named={names_all(intention, members)} "
                         f"written={written} template={first.get('template')}/{first.get('values')} "
                         f"{(made.stderr or started.stderr).strip()[-160:]!r}")
    if not wrong:
        held("(c) the four written then started", "council, triage, cross-check (star, no daily) and tree (lead over "
             "two squad leads over two workers each, the squads' daily, budget 10 launches 24) written by `team declare` "
             "without reports nor root, declared and started as their forms make them, team-started.template kept; "
             "each intention names its members, no hole left")
    else:
        failures.extend(f"  ✗ (c) {one}" for one in wrong)
    return 0
