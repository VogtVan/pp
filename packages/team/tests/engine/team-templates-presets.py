"""Scenario `team-templates-presets` -- 8 case(s): the package's EXAMPLES -- its nine team presets `teams/<t>`, its four
presets of a season `seasons/<t>`, their summaries and its documents by subject -- as files of the model of documents
by role, and the teams they make. The sibling of `team-templates`, its readings shared in `_templates.py`. A team is
stopped before its next season. No wake-up plays: every start is `--no-tick`.
- (a) the files: no `template.md` under the package's `templates/`; no front matter names a sort, a composition or
  an organization; each team preset's head comment names `team declare <name> --template teams/<t>`; each preset of
  a season says its summary for `all`; every document of the package is named by a line of a preset of a season --
  none orphan --, and every document a line names is a document of the package
- (b) the presets of a season rendered: one team of four members -- `contributors` ra, `reviewers` rb, `integrator`
  rc, rd none, and `writers` ra rb -- opens four seasons, one per preset `seasons/<name>` of the package, `SEASON.md`
  giving the values without a default alone: each start passes, its documents of the package's origin, one per
  document (`roles/` for a role's), no hole left, the views read on the first; `contributors = writers` reaches ra
  and rb; a team declaring no role refuses `role-unknown` naming `contributors`, nothing written; the characters
  each member receives said
- (c) a team preset, then a preset of a season: `team declare sw --template teams/supervisor-workers` writes the
  preset's role keys at the birth (`supervisor supervisor`, `workers worker-1 worker-2`), then `team declare sw
  --season --template seasons/worktree-and-requests --value contributors=workers --value reviewers=supervisor` and
  the values without a default: the start passes, the workers receive `pushed-commits`, the supervisor
  `read-commits`, all three the summary, the source and the remote -- `TEAM.md`, `declaration --json`, its views
- (d) the preset's role keys at the birth alone: a team born of `teams/supervisor-workers` starts with its keys, then
  `team declare --no-role` takes out every one -- `TEAM.md` without `roles:` --, and the next start gives it none:
  `team-started` and `declaration --json` say no role key
- (e) the keys by place, a star (s.1597): `teams/supervisor-workers` born with its own members `wa wb wc` and `--root
  wb` -- `TEAM.md` says `supervisor wb` (the place `{root}`) and `workers wa wc` (`{others}`)
- (f) the keys by place, a tree (s.1597): a house preset `teams/squads` of form `tree` whose `roles:` name `{root}`,
  `{squads}`, `{workers}` and `{last}`, born with `x0` to `x6` -- `boss x0`, `chiefs x1 x2`, `crew x3 x4 x5 x6`,
  `tail x6`
- (g) a line that names a member (s.1597): a house preset `teams/named` whose `roles:` line names a member refuses
  `template-invalid` at `team templates --json` and at `team declare --template`, nothing written
- (h) a place its form does not have (A4): a house preset `teams/starred` of form `star` whose `roles:` name
  `{workers}`, and `teams/chained` of form `chain` whose `roles:` name `{squads}`, each refuse `template-invalid` at
  `team templates --json` and at `team declare --template`, nothing written
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
code_of, kept = S.code_of, S.kept
PACKAGE = Path(__file__).resolve().parents[2] / "templates"
RETIRED = re.compile(r"\bsorts?\b|compos|organi[sz]ation|\bbricks?\b", re.I)


def front_of(path: Path) -> str:
    """-> the front matter of a template, its borders excluded; '' when it has none."""
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[1] if text.startswith("---\n") and text.count("---\n") >= 2 else ""


def lines_of(front: str) -> list[tuple[str, list[str]]]:
    """-> the lines of a front matter's `documents: |` block, `(key, documents)`."""
    found = re.search(r"^documents: \|\n((?:  .*\n)+)", front, re.M)
    return [(line.split()[0], line.split()[1:]) for line in found.group(1).splitlines()] if found else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})

    def start(name: str):
        h.off_season(name)                                 # a next season opens off season alone
        return h.call("team", "start", name, "--no-tick")

    def text(name: str, document: str) -> str | None:
        path = h.teams / name / document
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def files(name: str) -> list[str]:
        own = {f"TEAM-{name}.md", f"TEAM-{name}-members.md"}
        directory = h.teams / name
        return sorted(str(one.relative_to(directory)) for one in directory.rglob(f"TEAM-{name}-*.md")
                      if one.name not in own)

    def views(name: str) -> dict:
        declared = S.declaration_of(h, name).get("declared") or {}
        return {one.get("member"): sorted(doc.get("document") for doc in one.get("documents") or []
                                          if doc.get("document") != f"TEAM-{name}-members.md")
                for one in declared.get("views") or []}

    def started_at(name: str) -> dict:
        return (T.by_kind(h.events(name), "team-started") or [{}])[-1]

    season_of = lambda name: h.teams / name / "SEASON.md"

    # --- (a) the files ------------------------------------------------------------------------------------------
    every = sorted(PACKAGE.rglob("*.md"))
    fronts = {f"{one.parent.name}/{one.stem}": front_of(one) for one in every}
    sorts = [name for name in fronts if name.endswith("/template")]
    retired = [name for name, front in fronts.items() if RETIRED.search(front)]
    unnamed = [one for one in S.TEMPLATES if f"team declare <name> --template teams/{one}" not in
               " ".join(line.lstrip("# ") for line in fronts.get(f"teams/{one}", "").splitlines() if line.startswith("#"))]
    seasons = {name: lines_of(front) for name, front in fronts.items() if name.startswith("seasons/") and lines_of(front)}
    summaryless = [name for name, said in seasons.items() if f"{name}-summary" not in dict(said).get("all", [])]
    documents = {name for name, front in fronts.items() if not lines_of(front) and not name.startswith("teams/")}
    named = {one for said in seasons.values() for _, docs in said for one in docs}
    orphans, ghosts = sorted(documents - named), sorted(named - documents)
    if (not sorts and not retired and not unnamed and sorted(seasons) == sorted(f"seasons/{one}" for one in S.EXAMPLE_PRESETS)
            and not summaryless and not orphans and not ghosts):
        held("(a) the files", f"{len(every)} files, no template.md; no front matter says sort, compose, organization "
             f"or brick; the nine team presets' heads name `team declare <name> --template teams/<t>`; "
             f"{len(seasons)} presets of a season, each its summary for all; {len(documents)} documents, each named "
             "by a preset, none orphan, none a line names missing")
    else:
        failures.append(f"  ✗ (a) the files                template.md={sorts} retired words={retired} "
                        f"heads without their declare={unnamed} seasons={sorted(seasons)} summaryless={summaryless} "
                        f"orphans={orphans} ghosts={ghosts}")

    # --- (b) the presets of a season rendered -------------------------------------------------------------------
    four = ("---\nagents: |\n  ra agents/ra\n  rb agents/rb\n  rc agents/rc\n  rd agents/rd\nreports: |\n"
            "  rb rc rd -> ra\nroot: ra\nschedule: off\n{roles}---\nHold the examples.\n")
    keys = "roles: |\n  contributors ra\n  reviewers rb\n  integrator rc\n  writers ra rb\n"
    h.declare("ex", four.format(roles=keys))

    def season(preset: str, extra: dict | None = None) -> str:
        given = {**S.EXAMPLE_GIVEN[preset], **(extra or {})}
        return (f"---\ntemplate: seasons/{preset}\nvalues: |\n"
                + "".join(f"  {name} = {value}\n" for name, value in given.items()) + "---\n")

    def placed(name: str, key: str, doc: str) -> str:
        return f"TEAM-{name}-{doc.split('/')[1]}.md" if key == "all" else f"roles/TEAM-{name}-{doc.split('/')[1]}.md"

    reach = {"{contributors}": ["ra"], "{reviewers}": ["rb"], "{integrator}": ["rc"]}
    wrong_b, masses = [], {}
    for preset, lines in S.EXAMPLE_PRESETS.items():
        season_of("ex").write_text(season(preset), encoding="utf-8")
        played = start("ex")
        began = started_at("ex")
        wanted_docs = sorted(placed("ex", key, doc) for key, docs in lines for doc in docs)
        texts = {one: text("ex", one) for one in wanted_docs}
        holes = [one for one, body in texts.items() if body is None or re.search(r"\{[a-z0-9-]+\}", body)]
        got = views("ex") if not masses else None                 # the views read once, on the first preset
        wanted_views = {member: sorted(placed("ex", key, doc) for key, docs in lines for doc in docs
                                       if key == "all" or member in reach[key])
                        for member in ("ra", "rb", "rc", "rd")}
        seen = wanted_views if got is None else got
        if (played.returncode != 0 or files("ex") != wanted_docs or holes or seen != wanted_views
                or {one.get("origin") for one in began.get("documents") or []} != {"package"}):
            wrong_b.append(f"{preset}: rc={played.returncode} files={files('ex')} holes={holes} views={seen} "
                           f"{played.stderr.strip()[-240:]!r}")
            continue
        masses[preset] = {member: sum(len(texts[one]) for one in docs) for member, docs in seen.items()}
    season_of("ex").write_text(season("files", {"contributors": "writers"}), encoding="utf-8")
    writers = start("ex")
    writers_said = views("ex")
    h.declare("ey", four.format(roles=""))
    season_of("ey").write_text(season("files"), encoding="utf-8")
    before_y = kept(h, "ey")
    roleless = start("ey")
    if (not wrong_b and writers.returncode == 0
            and all("roles/TEAM-ex-copied-files.md" in writers_said.get(one, []) for one in ("ra", "rb"))
            and roleless.returncode == 2 and code_of(roleless) == "role-unknown" and "contributors" in roleless.stderr
            and kept(h, "ey") == before_y):
        bench.refusals += 1
        held("(b) the presets of a season rendered", "four seasons on seasons/files, worktree-and-requests, "
             "plan-branch, clone-and-integration: each rendered from the package, no hole, the roles reaching ra, "
             "rb, rc; contributors = writers reaches ra rb; no role declared: role-unknown naming contributors, "
             "nothing written; characters received (contributor ra, reviewer rb, integrator rc, none rd): "
             f"{ {name: list(found.values()) for name, found in masses.items()} }")
    else:
        failures.append(f"  ✗ (b) the presets of a season {wrong_b} writers={writers.returncode}/{writers_said} "
                        f"roleless={roleless.returncode}/{code_of(roleless)} {roleless.stderr.strip()[-200:]!r}")

    # --- (c) a team preset, then a preset of a season -----------------------------------------------------------
    born = h.call("team", "declare", "sw", "--template", "teams/supervisor-workers")
    keyed = "roles: |\n  supervisor supervisor\n  workers worker-1 worker-2\n" in (text("sw", "TEAM.md") or "")
    given = [f"{name}={value}" for name, value in {**S.EXAMPLE_GIVEN["worktree-and-requests"],
                                                    "contributors": "workers", "reviewers": "supervisor"}.items()]
    seasoned = h.call("team", "declare", "sw", "--season", "--template", "seasons/worktree-and-requests",
                      *[word for one in given for word in ("--value", one)])
    played = start("sw")
    common = [placed("sw", "all", doc) for doc in S.EXAMPLE_PRESETS["worktree-and-requests"][0][1]]
    wanted = {"supervisor": sorted([*common, "roles/TEAM-sw-read-commits.md"]),
              **{one: sorted([*common, "roles/TEAM-sw-pushed-commits.md"]) for one in ("worker-1", "worker-2")}}
    seen = views("sw")
    if born.returncode == 0 and keyed and seasoned.returncode == 0 and played.returncode == 0 and seen == wanted:
        held("(c) a team preset, then a preset of a season", "teams/supervisor-workers born with its keys "
             "supervisor and workers, then seasons/worktree-and-requests with contributors = workers, reviewers = "
             "supervisor: started; worker-1 and "
             "worker-2 receive pushed-commits, the supervisor read-commits, all three the summary, worktree-per-batch "
             "and review-requests")
    else:
        failures.append(f"  ✗ (c) team then season          rc={born.returncode}/{seasoned.returncode}/"
                        f"{played.returncode} keyed={keyed} views={seen} "
                        f"{(born.stderr or seasoned.stderr or played.stderr).strip()[-240:]!r}")

    # --- (d) the preset's role keys at the birth alone ------------------------------------------------------------
    h.call("team", "declare", "sv", "--template", "teams/supervisor-workers")
    first = start("sv")
    keys_first = sorted(started_at("sv").get("roles") or {})
    h.off_season("sv")
    cut = h.call("team", "declare", "sv", "--no-role", "supervisor", "--no-role", "workers")
    unkeyed = "roles:" not in (text("sv", "TEAM.md") or "roles:")
    again = start("sv")
    keys_again = sorted(started_at("sv").get("roles") or {})
    declared_keys = sorted(one.get("role") for one in
                           (S.declaration_of(h, "sv").get("declared") or {}).get("roles") or [])
    if (first.returncode == 0 and keys_first == ["supervisor", "workers"] and cut.returncode == 0 and unkeyed
            and again.returncode == 0 and keys_again == [] and declared_keys == []):
        held("(d) the preset's role keys at the birth alone", "teams/supervisor-workers started with supervisor "
             "and workers; every key taken out, TEAM.md without roles:; the next start gives none -- team-started "
             "and declaration --json say no key")
    else:
        failures.append(f"  ✗ (d) the preset's keys at birth  rc={first.returncode}/{cut.returncode}/"
                        f"{again.returncode} first={keys_first} unkeyed={unkeyed} again={keys_again} "
                        f"declared={declared_keys} {(cut.stderr or again.stderr).strip()[-240:]!r}")

    # --- (e) the keys by place, a star (s.1597) -----------------------------------------------------------------
    star = h.call("team", "declare", "sp", "--template", "teams/supervisor-workers", "--member", "wa", "agents/sp/wa",
                  "--member", "wb", "agents/sp/wb", "--member", "wc", "agents/sp/wc", "--root", "wb")
    star_text = text("sp", "TEAM.md") or ""
    if star.returncode == 0 and "roles: |\n  supervisor wb\n  workers wa wc\n" in star_text:
        held("(e) the keys by place, a star", "teams/supervisor-workers born with wa wb wc, root wb: supervisor wb, "
             "workers wa wc")
    else:
        failures.append(f"  ✗ (e) the keys by place, star  rc={star.returncode} "
                        f"roles={star_text.split('roles:', 1)[-1].split(chr(10) + 'root', 1)[0]!r} "
                        f"{star.stderr.strip()[-200:]!r}")

    # --- (f) the keys by place, a tree (s.1597) -----------------------------------------------------------------
    shelf = h.house / "teams" / "templates"
    S.laid(shelf, {"teams/squads.md": ("---\ndescription: a tree keyed by place\nform: tree\nmembers: |\n  lead\n"
                                       "  s1\n  s2\n  w1\n  w2\n  w3\n  w4\nroles: |\n  boss {root}\n"
                                       "  chiefs {squads}\n  crew {workers}\n  tail {last}\nvalues: |\n"
                                       "  squads = 2 -- the squad leads\n---\n{root} leads {squads}.\n")})
    xs = [f"x{n}" for n in range(7)]
    tree = h.call("team", "declare", "sq", "--template", "teams/squads",
                  *[word for one in xs for word in ("--member", one, f"agents/sq/{one}")])
    tree_text = text("sq", "TEAM.md") or ""
    if (tree.returncode == 0
            and "roles: |\n  boss x0\n  chiefs x1 x2\n  crew x3 x4 x5 x6\n  tail x6\n" in tree_text):
        held("(f) the keys by place, a tree", "teams/squads born with x0..x6: boss x0, chiefs x1 x2, crew x3 x4 x5 "
             "x6, tail x6")
    else:
        failures.append(f"  ✗ (f) the keys by place, tree  rc={tree.returncode} "
                        f"text={tree_text[:400]!r} {tree.stderr.strip()[-200:]!r}")

    # --- (g) a line that names a member (s.1597) ----------------------------------------------------------------
    S.laid(shelf, {"teams/named.md": ("---\ndescription: a key that names a member\nform: star\nmembers: |\n"
                                      "  a\n  b\nroles: |\n  leads a\n---\n{root} with {others}.\n")})
    listed = {}
    for line in h.call("team", "templates", "--json").stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        listed[one.get("template")] = one
    named = listed.get("teams/named") or {}
    refused = h.call("team", "declare", "nm", "--template", "teams/named")
    if (code_of_said(named.get("refusal") or "") == "template-invalid"
            and refused.returncode == 2 and code_of(refused) == "template-invalid"
            and not (h.teams / "nm").exists()):
        bench.refusals += 2
        held("(g) a line that names a member", "teams/named, roles: leads a -- template-invalid at templates --json "
             "and at declare, nothing written")
    else:
        failures.append(f"  ✗ (g) a line naming a member   listed={named.get('refusal') or named.get('roles')} "
                        f"declare={refused.returncode}/{code_of(refused)} dir={(h.teams / 'nm').exists()}")

    # --- (h) a place its form does not have (A4) ----------------------------------------------------------------
    S.laid(shelf, {"teams/starred.md": ("---\ndescription: a star keyed by a tree's place\nform: star\nmembers: |\n"
                                        "  a\n  b\nroles: |\n  crew {workers}\n---\n{root} with {others}.\n"),
                   "teams/chained.md": ("---\ndescription: a chain keyed by a tree's place\nform: chain\nmembers: |\n"
                                        "  a\n  b\nroles: |\n  chiefs {squads}\n---\n{root} then {last}.\n")})
    listed = {}
    for line in h.call("team", "templates", "--json").stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        listed[one.get("template")] = one
    outside = {}
    for preset, team in (("teams/starred", "st"), ("teams/chained", "ch")):
        declared = h.call("team", "declare", team, "--template", preset)
        outside[preset] = (code_of_said((listed.get(preset) or {}).get("refusal") or ""), declared.returncode,
                           code_of(declared), (h.teams / team).exists())
    if all(said == ("template-invalid", 2, "template-invalid", False) for said in outside.values()):
        bench.refusals += 4
        held("(h) a place its form does not have", "teams/starred (star, crew {workers}) and teams/chained (chain, "
             "chiefs {squads}) -- template-invalid at templates --json and at declare, nothing written")
    else:
        failures.append(f"  ✗ (h) a place outside the form {outside}")
    return 0


def code_of_said(said: str) -> str:
    """-> the refusal's code at the head of a refusal's text: its first word."""
    return said.split()[0] if said.split() else ""
