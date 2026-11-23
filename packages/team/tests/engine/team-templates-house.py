"""Scenario `team-templates-house` -- 15 case(s): the house's own TEMPLATES, `team templates --json` reading
`<house>/.pp/teams/templates/<directory>/<name>.md` then the package's -- the sibling of `team-templates`, its houses
and readings shared in `_templates.py`. No wake-up plays: every start is `--no-tick`.
- (a) the house's templates: a house laying `git/par-lot`, `loose/one`, `teams/supervisor-workers` and `teams/pair`
  sees each (`origin` house, `kind` document or preset); `teams/supervisor-workers` replaces the package's (its own
  members), the eight other team presets listed from the package; `plans/shared` (`requires: plan`) absent without
  the pin `plan`; a `templates/` of another package never read; no `template.md` listed
- (b) `requires:` judged on the pins: the same file listed by a house that pins `plan`, its `requires` said
- (c) the values and the lines said: a house laying `_templates.py`'s shelf -- each template says its `values`
  (`{name, description, default}`), a preset its `documents` (`{key, documents}` -- a key hole `{checker}` as written:
  a template knows no team), a document none; the text face one line per value and one per line of `documents:`
- (d) the package's examples: its documents by directory (`sources`, `contribution`, `review`, `integration`,
  `remote`) and its four presets of a season `seasons/<name>`, each line naming a document of the package, its keys
  the holes `{contributors}`, `{reviewers}`, `{integrator}` the preset declares with their key as default; every
  document named by a preset; every template says a description and a description per value; a house document of a
  package's name replaces it (`origin` house), the other documents of its directory still the package's
- (e) a team preset without `form:`: a house's `teams/pair` carrying its own `reports:` and `root:` -- `team declare
  --template teams/pair` writes them as they stand, `team start` reads them at `team-started`
- (f) a template refused: a directory or a name that is no slug refuses `template-invalid` citing the file, at
  `templates` and at `declare` alike; a document named `members` refuses `document-collision` naming the members'
  sheet at `start`, nothing written
- (g) a team preset's lines are defaults: `teams/crew` (form `star`, `all notes/plain`, `make guide/both`) named by a
  `TEAM.md` whose own line `all notes/dated` replaces the preset's -- the start renders `TEAM-x-dated.md` and
  `roles/TEAM-x-both.md`, not `plain`; the form makes the edges
- (h) a values file names a preset of its nature: `TEAM.md` naming `seasons/house-flow` and `SEASON.md` naming
  `teams/crew` refuse `template-unknown` at `start`, the directory and the journal byte for byte
- (i) an unreadable template is one refused line: `torn/open.md`, a front matter that never closes -- `team templates
  --json` answers rc 0, the line of `torn/open` carries its `refusal` (`template-invalid`), the others listed
- (j) a line replaces the preset's when the keys are equal once filled: `SEASON.md` naming `seasons/house-flow`
  (`{checker} review/pair`, `checker` `inspect` by default) writes `inspect review/law` -- the start renders
  `review/law` and not `review/pair`, whose value `lead` no line asks any more
- (k) a key is a hole by its name alone: a line `{{ notes/plain` refuses `season-invalid` at `start`, nothing written
- (l) two lines of one preset on one key once filled: `seasons/twice` (`{checker} notes/plain`, `inspect guide/both`,
  `checker` `inspect` by default) named by `SEASON.md` refuses `template-invalid` naming the preset, nothing written
- (m) a team preset by its edges: `teams/edges` carrying `reports:`, `root:` and `documents:`, without `form:` nor
  `members:` -- `team templates --json` says its team: `form` null, its members, its root and its edges
- (n) a template rendered dry: `team templates --render notes/dated --team rn --json` says `{template, text,
  values}`, its text the bytes `team start` wrote at `TEAM-rn-dated.md`, `day` from the team's values as a default,
  `--value day=sunday` given; a value given empty is withdrawn -- `--value day=` under `--team rn` takes the
  template's default `monday`, never the team's `friday`, and `review/pair --team rn --value lead=` refuses `value-missing`
  naming `lead`; `review/pair` without `lead` refuses `value-missing` naming it, `notes/nosuch` `template-unknown` --
  the team's directory and its journal byte for byte
- (o) a team preset's roles: `teams/squad` (form `star`, `roles: workers {others}`) -- `team templates --json`
  says its `roles` by place; `team declare sq --template teams/squad` writes the line `workers hand-1 hand-2` at the birth, and
  the start keeps it at `team-started.roles`; a `TEAM.md` naming the preset without `roles:` plays no key -- the
  preset's keys are written at the birth alone (`declared.roles` empty)
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
TEMPLATES = S.TEMPLATES
laid, code_of, kept = S.laid, S.code_of, S.kept
templates_of, preset = S.templates_of, S.preset


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    by_kind = T.by_kind

    # --- (a) the house's templates ------------------------------------------------------------------
    o = T.House(bench, script={}, slug="owner")
    shelf = o.house / "teams" / "templates"
    laid(shelf, S.HOUSE_TEMPLATES)
    agent_script = next(o.house.rglob("pp-agent.py"), None)
    if agent_script is not None:                     # another package's templates/: never read
        laid(agent_script.parents[2] / "templates", {"alien/x.md": "---\ndescription: x\n---\nX.\n"})
    found = templates_of(o)
    listed = o.call("team", "templates")
    house = {name: (one.get("kind"), one.get("origin")) for name, one in found.items() if one.get("origin") == "house"}
    if (agent_script is not None and house == {"git/par-lot": ("document", "house"), "loose/one": ("document", "house"),
                                                "teams/pair": ("preset", "house"),
                                                "teams/supervisor-workers": ("preset", "house")}
            and (found.get("teams/supervisor-workers") or {}).get("members") == ["boss", "hand-1", "hand-2"]
            and all((found.get(preset(one)) or {}).get("origin") == "package"
                    for one in TEMPLATES if one != "supervisor-workers")
            and "plans/shared" not in found and "alien/x" not in found
            and not any(name.endswith("/template") for name in found)
            and listed.returncode == 0 and "git/par-lot" in listed.stdout and "alien" not in listed.stdout):
        held("(a) the house's templates", "git/par-lot and loose/one (documents), teams/pair and the house's "
             "teams/supervisor-workers (presets, its own members), the eight other team presets from the package; "
             "plans/shared (requires plan) and another package's alien/x absent; no template.md")
    else:
        failures.append(f"  ✗ (a) house templates        house={house} agent={agent_script} "
                        f"members={(found.get('teams/supervisor-workers') or {}).get('members')} "
                        f"{listed.stderr.strip()[-160:]!r}")

    # --- (b) requires: judged on the pins ---------------------------------------------------------
    p = T.House(bench, script={}, packages=("agent", "team", "plan"), slug="planner")
    laid(p.house / "teams" / "templates", {key: text for key, text in S.HOUSE_TEMPLATES.items() if key.startswith("plans/")})
    planned = templates_of(p).get("plans/shared") or {}
    if (planned.get("origin"), planned.get("kind"), planned.get("requires")) == ("house", "document", ["plan"]):
        held("(b) requires: judged on the pins", "the house pinning plan lists plans/shared, requires [plan]")
    else:
        failures.append(f"  ✗ (b) requires              shared={planned}")

    # --- (c) the values and the lines said ----------------------------------------------------------------------
    c = T.House(bench, script={}, slug="contract")
    laid(c.house / "teams" / "templates", S.SHELF)
    said = templates_of(c)
    flow, by_batch, pair = (said.get("seasons/house-flow") or {}, said.get("sources/by-batch") or {},
                            said.get("review/pair") or {})
    text = c.call("team", "templates")
    if (flow.get("kind") == "preset"
            and flow.get("values") == [{"name": "checker", "description": "the role that reviews", "default": "inspect"}]
            and flow.get("documents") == [{"key": "all", "documents": ["notes/plain"]},
                                          {"key": "make", "documents": ["sources/by-batch"]},
                                          {"key": "{checker}", "documents": ["review/pair"]}]
            and "members" not in flow
            and by_batch.get("kind") == "document" and "documents" not in by_batch
            and by_batch.get("values") == [{"name": "remote", "description": "where the code goes", "default": "origin"},
                                           {"name": "branch", "description": "the branch pattern",
                                            "default": "batch-<lot>"}]
            and pair.get("values") == [{"name": "lead", "description": "who merges", "default": None}]
            and (said.get(preset("solo")) or {}).get("values") == []
            and text.returncode == 0
            and all(f"{one['name']} = {one['default']} -- {one['description']}" in text.stdout for one in flow["values"])
            and "lead -- who merges" in text.stdout and "documents: {checker} review/pair" in text.stdout):
        held("(c) the values and the lines said", "seasons/house-flow: value checker (inspect), documents all, make, "
             "{checker} as written; by-batch: remote and branch, no documents; pair: lead; teams/solo []; the text says "
             "each value and each line")
    else:
        failures.append(f"  ✗ (c) values and lines      flow={flow} by-batch={by_batch} pair={pair} "
                        f"{text.stdout[-400:]!r} {text.stderr.strip()[-160:]!r}")

    # --- (d) the package's examples -----------------------------------------------------------------------------
    documents = {directory: sorted(name.split("/")[1] for name, one in said.items()
                                   if name.startswith(f"{directory}/") and one.get("origin") == "package")
                 for directory in S.EXAMPLE_DOCUMENTS}
    presets = {name.split("/")[1]: one for name, one in said.items()
               if name.startswith("seasons/") and one.get("kind") == "preset" and one.get("origin") == "package"}
    lines = {name: [(line.get("key"), line.get("documents")) for line in one.get("documents") or []]
             for name, one in presets.items()}
    reached = {doc for found in lines.values() for _, docs in found for doc in docs if not doc.startswith("seasons/")}
    every = [one for one in said.values() if one.get("origin") == "package"]
    roles = {name: {value.get("name"): value.get("default") for value in one.get("values") or []
                    if value.get("name") in S.ROLE_VALUES} for name, one in presets.items()}
    wanted_roles = {name: {key.strip("{}"): S.ROLE_VALUES[key.strip("{}")] for key, _ in found if key != "all"}
                    for name, found in S.EXAMPLE_PRESETS.items()}
    laid(c.house / "teams" / "templates", {"review/read-files.md": "---\ndescription: the house's reading\n---\nRead.\n"})
    replaced = templates_of(c)
    if (documents == S.EXAMPLE_DOCUMENTS
            and lines == {name: [(key, list(docs)) for key, docs in found] for name, found in S.EXAMPLE_PRESETS.items()}
            and reached == {f"{directory}/{one}" for directory, names in S.EXAMPLE_DOCUMENTS.items() for one in names}
            and roles == wanted_roles
            and all(one.get("description") and all(value.get("description") for value in one.get("values") or [])
                    for one in every)
            and (replaced.get("review/read-files") or {}).get("origin") == "house"
            and (replaced.get("review/read-commits") or {}).get("origin") == "package"):
        held("(d) the package's examples", f"documents {S.EXAMPLE_DOCUMENTS}; presets {sorted(presets)}, each line "
             "naming package documents, keys {contributors} {reviewers} {integrator} defaulting to their key; every "
             "document named, every template and value described; the house's review/read-files replaces the package's")
    else:
        failures.append(f"  ✗ (d) the package's examples documents={documents} lines={lines} roles={roles} "
                        f"undescribed={[one.get('template') for one in every if not one.get('description')]} "
                        f"replaced={ {one: (replaced.get(one) or {}).get('origin') for one in ('review/read-files', 'review/read-commits')} }")

    # --- (e) a team preset without form: ----------------------------------------------------------------
    made = o.call("team", "declare", "duo", "--template", "teams/pair")
    started = o.call("team", "start", "duo", "--message", "go", "--no-tick", now="07:50")
    first = next(iter(by_kind(o.events("duo"), "team-started")), {})
    pair_said = found.get("teams/pair") or {}
    if (made.returncode == 0 and started.returncode == 0 and first.get("root") == "a"
            and first.get("reports") == [{"from": ["b"], "to": "a"}]
            and pair_said.get("reports") == [{"from": ["b"], "to": "a"}] and pair_said.get("root") == "a"
            and pair_said.get("form") is None):
        held("(e) a team preset without form:", "teams/pair: its reports b -> a and its root a written as they stand, "
             "read at team-started and listed by --json")
    else:
        failures.append(f"  ✗ (e) no form               rc={made.returncode}/{started.returncode} first={first} "
                        f"pair={pair_said} {(made.stderr or started.stderr).strip()[-160:]!r}")

    # --- (f) a template refused -------------------------------------------------------------------------
    wrong = []
    for files in ({"Bad_Dir/one.md": "---\ndescription: one\n---\nOne.\n"},
                  {"good/Bad_Name.md": "---\ndescription: one\n---\nOne.\n"}):
        laid(shelf, files)
        path = shelf / next(iter(files))
        read = o.call("team", "templates", "--json")
        made_bad = o.call("team", "declare", "ghost", "--template", "teams/solo")
        if not all(one.returncode == 2 and code_of(one) == "template-invalid" and str(path) in one.stderr
                   for one in (read, made_bad)):
            wrong.append(f"{path.name}: rc={read.returncode}/{made_bad.returncode} {read.stderr.strip()[-160:]!r}")
        path.unlink()
        path.parent.rmdir()
    laid(shelf, {"sheet/members.md": "---\ndescription: a sheet of my own\n---\nMine.\n"})
    o.declare("sh", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\ndocuments: |\n  all sheet/members\n---\n")
    before = kept(o, "sh")
    collided = o.call("team", "start", "sh", "--no-tick")
    if (not wrong and not (o.teams / "ghost").exists() and collided.returncode == 2
            and code_of(collided) == "document-collision" and "TEAM-sh-members.md" in collided.stderr
            and kept(o, "sh") == before):
        bench.refusals += 5
        held("(f) a template refused", "Bad_Dir/one and good/Bad_Name: template-invalid citing the file, at templates "
             "and at declare, no teams/ghost; sheet/members: document-collision naming TEAM-sh-members.md, nothing "
             "written")
    else:
        failures.append(f"  ✗ (f) refused templates      {wrong} collided={collided.returncode}/{code_of(collided)} "
                        f"{collided.stderr.strip()[-160:]!r}")

    # --- (g) a team preset's lines are defaults ----------------------------------------------------------------
    laid(c.house / "teams" / "templates", {
        "teams/crew.md": ("---\ndescription: a crew\nform: star\nmembers: |\n  boss\n  hand\ndocuments: |\n"
                          "  all notes/plain\n  make guide/both\n---\n{root} leads {others}.\n")})
    c.declare("x", "---\ntemplate: teams/crew\nagents: |\n  boss agents/boss\n  hand agents/hand\nschedule: off\n"
                   "roles: |\n  make hand\ndocuments: |\n  all notes/dated\n---\n")
    crewed = c.call("team", "start", "x", "--no-tick")
    began = (by_kind(c.events("x"), "team-started") or [{}])[-1]
    directory = c.teams / "x"
    rendered = sorted(str(one.relative_to(directory)) for one in directory.rglob("TEAM-x-*.md")
                      if one.name != "TEAM-x-members.md") if directory.is_dir() else []
    if (crewed.returncode == 0 and rendered == ["TEAM-x-dated.md", "roles/TEAM-x-both.md"]
            and began.get("reports") == [{"from": ["hand"], "to": "boss"}] and began.get("root") == "boss"
            and began.get("template") == {"template": "teams/crew", "origin": "house"}):
        held("(g) a team preset's lines are defaults", "teams/crew named by TEAM.md: its line all notes/dated replaces "
             "the preset's all, make guide/both kept from the preset -- TEAM-x-dated.md, roles/TEAM-x-both.md; the "
             "form star makes hand -> boss")
    else:
        failures.append(f"  ✗ (g) preset lines          rc={crewed.returncode} rendered={rendered} "
                        f"reports={began.get('reports')} template={began.get('template')} {crewed.stderr.strip()[-200:]!r}")

    # --- (h) a values file names a preset of its nature ----------------------------------------------------------
    c.declare("tn", "---\ntemplate: seasons/house-flow\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\n")
    c.declare("sn", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\n")
    (c.teams / "sn" / "SEASON.md").write_text("---\ntemplate: teams/crew\n---\n", encoding="utf-8")
    natures = {}
    for name, named in (("tn", "seasons/house-flow"), ("sn", "teams/crew")):
        before_n = kept(c, name)
        refused = c.call("team", "start", name, "--no-tick")
        natures[name] = (refused.returncode, code_of(refused), named in refused.stderr, kept(c, name) == before_n)
    if natures == {"tn": (2, "template-unknown", True, True), "sn": (2, "template-unknown", True, True)}:
        bench.refusals += 2
        held("(h) a values file names a preset of its nature", "TEAM.md naming seasons/house-flow, SEASON.md naming "
             "teams/crew: template-unknown, the directory and the journal byte for byte")
    else:
        failures.append(f"  ✗ (h) the preset's nature     {natures}")

    # --- (i) an unreadable template is one refused line ---------------------------------------------------------
    laid(c.house / "teams" / "templates", {"torn/open.md": "---\ndescription: a front matter left open\n"})
    torn = c.call("team", "templates", "--json")
    lines_t = {}
    for line in torn.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        lines_t[one.get("template")] = one
    refusal = str((lines_t.get("torn/open") or {}).get("refusal") or "")
    if (torn.returncode == 0 and refusal.startswith("template-invalid") and "seasons/house-flow" in lines_t
            and "refusal" not in lines_t["seasons/house-flow"]):
        held("(i) an unreadable template is one refused line", "torn/open: its line carries template-invalid, rc 0, "
             f"{len(lines_t) - 1} other lines listed")
    else:
        failures.append(f"  ✗ (i) a refused line          rc={torn.returncode} torn={lines_t.get('torn/open')} "
                        f"listed={len(lines_t)} {torn.stderr.strip()[-200:]!r}")

    # --- (j) a line replaces the preset's when the keys are equal once filled -------------------------------------
    c.declare("fk", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\nroles: |\n  make m\n  inspect m\n---\n")
    (c.teams / "fk" / "SEASON.md").write_text("---\ntemplate: seasons/house-flow\ndocuments: |\n  inspect review/law\n"
                                              "---\n", encoding="utf-8")
    filled = c.call("team", "start", "fk", "--no-tick")
    templates = [one.get("template") for one in (by_kind(c.events("fk"), "team-started") or [{}])[-1].get("documents") or []]
    if filled.returncode == 0 and templates == ["notes/plain", "sources/by-batch", "review/law"]:
        held("(j) a line replaces the preset's once filled", "inspect review/law replaces {checker} review/pair "
             "({checker} filled inspect): notes/plain, sources/by-batch, review/law rendered")
    else:
        failures.append(f"  ✗ (j) the filled key          rc={filled.returncode} templates={templates} "
                        f"{filled.stderr.strip()[-200:]!r}")

    # --- (k) a key is a hole by its name alone -----------------------------------------------------------------
    c.declare("kb", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\n")
    (c.teams / "kb" / "SEASON.md").write_text("---\ndocuments: |\n  {{ notes/plain\n---\n", encoding="utf-8")
    before_k = kept(c, "kb")
    braced = c.call("team", "start", "kb", "--no-tick")
    if braced.returncode == 2 and code_of(braced) == "season-invalid" and "{{" in braced.stderr and kept(c, "kb") == before_k:
        bench.refusals += 1
        held("(k) a key is a hole by its name alone", "{{ notes/plain: season-invalid naming the line, nothing written")
    else:
        failures.append(f"  ✗ (k) a braced key            rc={braced.returncode} code={code_of(braced)} "
                        f"same={kept(c, 'kb') == before_k} {braced.stderr.strip()[-200:]!r}")

    # --- (l) two lines of one preset on one key once filled -----------------------------------------------------
    laid(c.house / "teams" / "templates", {
        "seasons/twice.md": ("---\ndescription: one key twice\nvalues: |\n  checker = inspect -- the role that reviews\n"
                             "documents: |\n  {checker} notes/plain\n  inspect guide/both\n---\n"),
        "teams/edges.md": ("---\ndescription: a team by its edges\nreports: |\n  b -> a\nroot: a\ndocuments: |\n"
                           "  all notes/plain\n---\n{root} with {others}.\n")})
    c.declare("tw", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\nroles: |\n  inspect m\n---\n")
    (c.teams / "tw" / "SEASON.md").write_text("---\ntemplate: seasons/twice\n---\n", encoding="utf-8")
    before_tw = kept(c, "tw")
    twice = c.call("team", "start", "tw", "--no-tick")
    if (twice.returncode == 2 and code_of(twice) == "template-invalid" and "twice.md" in twice.stderr
            and kept(c, "tw") == before_tw):
        bench.refusals += 1
        held("(l) two lines of one preset on one key", "{checker} filled inspect beside inspect in seasons/twice: "
             "template-invalid naming the preset, nothing written")
    else:
        failures.append(f"  ✗ (l) one key twice           rc={twice.returncode} code={code_of(twice)} "
                        f"same={kept(c, 'tw') == before_tw} {twice.stderr.strip()[-200:]!r}")

    # --- (m) a team preset by its edges -----------------------------------------------------------------------
    edges = templates_of(c).get("teams/edges") or {}
    if (edges.get("kind") == "preset" and "form" in edges and edges.get("form") is None
            and edges.get("members") == ["a", "b"] and edges.get("root") == "a"
            and edges.get("reports") == [{"from": ["b"], "to": "a"}]
            and edges.get("documents") == [{"key": "all", "documents": ["notes/plain"]}]):
        held("(m) a team preset by its edges", "teams/edges, reports and root without form nor members: form null, "
             "members a b, root a, b -> a, its documents")
    else:
        failures.append(f"  ✗ (m) a preset by its edges   {edges}")

    # --- (n) a template rendered dry --------------------------------------------------------------------------
    c.declare("rn", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\ndocuments: |\n  all notes/dated\nvalues: |\n"
                    "  day = friday\n---\n")
    rn_start = c.call("team", "start", "rn", "--no-tick")
    written_rn = (c.teams / "rn" / "TEAM-rn-dated.md").read_text(encoding="utf-8") if rn_start.returncode == 0 else ""
    before_rn = kept(c, "rn")

    def rendered(*args: str) -> tuple:
        played = c.call("team", "templates", "--render", *args, "--json")
        try:
            return played, json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return played, {}

    as_team, face_t = rendered("notes/dated", "--team", "rn")
    given, face_g = rendered("notes/dated", "--team", "rn", "--value", "day=sunday")
    missing, _ = rendered("review/pair", "--team", "rn")
    withdrawn, face_w = rendered("notes/dated", "--team", "rn", "--value", "day=")
    emptied, _ = rendered("review/pair", "--team", "rn", "--value", "lead=")
    unknown, _ = rendered("notes/nosuch")
    if (rn_start.returncode == 0 and as_team.returncode == 0
            and face_t == {"template": "notes/dated", "text": written_rn,
                           "values": [{"name": "team", "value": "rn", "from": "default"},
                                      {"name": "day", "value": "friday", "from": "default"}]}
            and given.returncode == 0 and face_g.get("text") == written_rn.replace("friday", "sunday")
            and {"name": "day", "value": "sunday", "from": "given"} in face_g.get("values", [])
            and missing.returncode == 2 and code_of(missing) == "value-missing" and "lead" in missing.stderr
            and withdrawn.returncode == 0 and face_w.get("text") == written_rn.replace("friday", "monday")
            and {"name": "day", "value": "monday", "from": "default"} in face_w.get("values", [])
            and emptied.returncode == 2 and code_of(emptied) == "value-missing" and "lead" in emptied.stderr
            and unknown.returncode == 2 and code_of(unknown) == "template-unknown" and kept(c, "rn") == before_rn):
        bench.refusals += 3
        held("(n) a template rendered dry", "notes/dated for rn: the bytes of TEAM-rn-dated.md, day friday from the "
             "team; day=sunday given; day= withdrawn: monday, the default; review/pair lead=: value-missing; "
             "review/pair without lead: value-missing; notes/nosuch: template-unknown; nothing written")
    else:
        failures.append(f"  ✗ (n) rendered dry            rc={rn_start.returncode}/{as_team.returncode}/{given.returncode}/"
                        f"{missing.returncode}/{unknown.returncode} withdrawn={withdrawn.returncode} {face_w} "
                        f"emptied={emptied.returncode} {emptied.stderr.strip()[-120:]!r} face={face_t} "
                        f"written={written_rn!r} "
                        f"{(as_team.stderr or missing.stderr).strip()[-200:]!r}")

    # --- (o) a team preset's roles ------------------------------------------------------------------------------
    laid(c.house / "teams" / "templates", {
        "teams/squad.md": ("---\ndescription: a squad\nform: star\nmembers: |\n  boss\n  hand-1\n  hand-2\n"
                           "roles: |\n  workers {others}\n---\n{root} leads {others}.\n")})
    squad = templates_of(c).get("teams/squad") or {}
    born_sq = c.call("team", "declare", "sq", "--template", "teams/squad")
    text_sq = (c.teams / "sq" / "TEAM.md").read_text(encoding="utf-8") if (c.teams / "sq" / "TEAM.md").is_file() else ""
    started_sq = c.call("team", "start", "sq", "--no-tick")
    kept_sq = (by_kind(c.events("sq"), "team-started") or [{}])[-1].get("roles")
    c.declare("sr", "---\ntemplate: teams/squad\nagents: |\n  boss agents/boss\n  hand-1 agents/hand-1\nschedule: off\n---\n")
    said_sr = (S.declaration_of(c, "sr").get("declared") or {}).get("roles")
    if (squad.get("roles") == [{"role": "workers", "places": ["{others}"]}]
            and born_sq.returncode == 0 and "roles: |\n  workers hand-1 hand-2\n" in text_sq
            and started_sq.returncode == 0 and kept_sq == {"workers": ["hand-1", "hand-2"]}
            and said_sr == []):
        held("(o) a team preset's roles", "teams/squad: roles said by --json, written at the birth of sq and kept at "
             "its start; sr naming the preset without roles: no key played, the keys the birth's alone")
    else:
        failures.append(f"  ✗ (o) a preset's roles        roles={squad.get('roles')} rc={born_sq.returncode}/"
                        f"{started_sq.returncode} text={text_sq!r} kept={kept_sq} said={said_sr} "
                        f"{(born_sq.stderr or started_sq.stderr).strip()[-200:]!r}")
    return 0
