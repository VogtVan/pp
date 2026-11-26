"""Scenario `team-contract-render` -- 12 case(s): the DOCUMENTS of a team, rendered at `team start` from the lines of
`documents:` -- `<key>|all <document> ...` -- of `teams/<name>/TEAM.md` and of `SEASON.md`, read by one code: each
document `<directory>/<name>` (a template of the house or of the package) or `<name>` (a file of the team's directory)
rendered once as `TEAM-<team>-<name>.md`, at the root for `all`, under `roles/` for a role key; the values of
`values:` filling its holes; `team-started` keeping `documents` and `rendered`. The house's documents and presets are
`_templates.py`'s; the package's presets are `team-templates-presets`'s (rule 10). A team is stopped before its
next season, and before its values are written. No wake-up plays but in (h).
- (a) the documents rendered by role: a team of three keys (`make` ma mb, `inspect` mi mb, `watch` none) whose
  `TEAM.md` says `all notes/dated` (its value `day = friday`) and `watch guide/both`, under a `SEASON.md` naming the
  preset `seasons/house-flow` (`all notes/plain`, `make sources/by-batch`, `{checker} review/pair`, `checker`
  `inspect` by default) and giving `lead` -- the root's two documents, `roles/` the three others, the holes filled in
  the head and the body, `{{` one brace, `<lot>` left, no template key; `declared.views` each member's documents,
  each once; `declared.documents` the lines by key, the team's and the season's; `team-started.documents` and
  `rendered`, no `organization` nor `compose`
- (b) each refusal names its cause and writes nothing: `document-unknown` (a template, a file of the directory),
  `role-unknown`, `value-missing`, `value-unknown`, `value-undeclared`, `document-collision` (two documents of one
  name), `document-holes` (a file of the directory with a hole), `template-unknown`, `season-invalid` (`compose:`, a
  line with no `=`) -- the team's directory and its journal byte for byte
- (c) rendered again: a value changed -- the document rendered anew, its digest changed, the other's the same; the
  preset `seasons/lean` chosen -- the documents nobody names removed, `roles/` with them, `by-batch` at the root
- (d) a rendered document edited by hand refuses `rendered-edited` naming it, nothing written; deleted, it is
  rendered again
- (e) no season: a team without `SEASON.md` renders no document and keeps `documents` empty; `SEASON.md` removed
  after a season with documents: they are removed at the next start
- (f) a preset's lines are defaults: a `SEASON.md` line `make sources/trunk` replaces the preset's line of `make`,
  its other lines kept
- (g) a name taken and a mounted document judged: a `TEAM-<name>-plain.md` written by hand refuses
  `document-collision` naming it; a mounted document with a law coded outside `TM` refuses `common-code-prefix`; a
  mounted document serving `TEAM-<name>-pair.md` while the same start stops naming `review/pair` refuses
  `common-serve-unknown` -- nothing written in any
- (h) the owner's word: the body of `SEASON.md` named by the head of `TEAM-<name>.md` beside the team's documents;
  rewritten after the start, the next wake-up serves the new body without a start; a `SEASON.md` without a body
  is not named
- (i) the keys of a line: `{checker}` filled to `inspect` reaches rb, `checker = audit` reaches rb by another key; a
  key `TEAM.md` does not declare refuses `role-unknown` naming the key and its origin -- the preset, `SEASON.md` --,
  the verdict the same, nothing written; a key hole nothing declares refuses `value-undeclared`
- (j) the team's documents kept through seasons: `all notes/dated` of `TEAM.md` stands byte for byte under
  `house-flow` then `lean`; `declared.documents` says the line of `all` from both files; `day = sunday` puts
  `values` and `documents` in `pending`; the line taken out, its document leaves at the next start
- (k) a file of the team's directory: `all mine` serves `mine.md` as it stands, `{{` kept, rendered as
  `TEAM-<name>-mine.md`; under a role key it opens on a front matter
- (l) the season written by `team declare --season`: `--template seasons/house-flow --value lead=alice --document
  "all notes/dated"` gives birth to `SEASON.md` with these three keys alone, `pending` saying `documents`, no event
  and no document rendered; the next start renders them; on a `SEASON.md` that holds a comment, a `model:` and a
  body, `--value`, `--no-document` and `--body-file` each write their key alone; refused, nothing written:
  `template-unknown`, `value-unknown`, `team-unknown`, `flag-retired` for `--compose`
"""
from __future__ import annotations

import json
import re

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
laid, code_of, digest, kept = S.laid, S.code_of, S.digest, S.kept
SEASON = S.SEASON
ONE = "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\nroles: |\n  make m\n  inspect m\n---\nHold the work.\n"
THREE = ("---\nagents: |\n  ma agents/ma\n  mi agents/mi\n  mb agents/mb\nreports: |\n  mi mb -> ma\nroot: ma\n"
         "schedule: off\nroles: |\n  make ma mb\n  inspect mi mb\n  watch\ndocuments: |\n  all notes/dated\n"
         "  watch guide/both\nvalues: |\n  day = friday\n---\nHold the roles.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"m": [{"sleep": 0.1, "body": {"done": "ok"}}]})
    laid(h.house / "teams" / "templates", S.SHELF)

    def team(name: str, season: str | None, text: str = ONE) -> None:
        h.declare(name, text)
        if season is not None:
            (h.teams / name / "SEASON.md").write_text(season, encoding="utf-8")

    def start(name: str):
        h.off_season(name)                                 # a next season opens off season alone
        return h.call("team", "start", name, "--no-tick")

    def started_at(name: str) -> dict:
        return (T.by_kind(h.events(name), "team-started") or [{}])[-1]

    def text(name: str, document: str) -> str | None:
        path = h.teams / name / document
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def files(name: str) -> list[str]:
        own = {f"TEAM-{name}.md", f"TEAM-{name}-members.md"}
        directory = h.teams / name
        return sorted(str(one.relative_to(directory)) for one in directory.rglob(f"TEAM-{name}-*.md")
                      if one.name not in own)

    def faced(name: str) -> dict:
        played = h.call("team", "declaration", name, "--json")
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    def verdict_code(name: str) -> str:
        return ((faced(name).get("verdict") or {}).get("refusal") or "").split(" --")[0].strip()

    def views(name: str) -> dict:
        return {one.get("member"): sorted(doc.get("document") for doc in one.get("documents") or [])
                for one in (faced(name).get("declared") or {}).get("views") or []}

    def head_served(name: str) -> list[str]:
        found = re.search(r"^serve: \|\n((?:  .*\n)+)", text(name, f"TEAM-{name}.md") or "", re.M)
        return found.group(1).split() if found else []

    season_of = lambda name: h.teams / name / "SEASON.md"

    # --- (a) the documents rendered by role -----------------------------------------------------------------
    team("a", SEASON, THREE)
    played = start("a")
    began = started_at("a")
    wanted = {"TEAM-a-dated.md": "Notes of a, read on friday.\n", "TEAM-a-plain.md": "Notes of a.\n",
              "roles/TEAM-a-both.md": "---\n---\nzzbothbody\n",
              "roles/TEAM-a-by-batch.md": "---\n---\nPush to origin on batch-<lot>, named after <lot>.\n",
              "roles/TEAM-a-pair.md": "---\nserve: |\n  TEAM-a-members.md\n---\nalice reads it; write {braces}.\n"}
    rendered = {one: text("a", one) for one in files("a")}
    root = ["TEAM-a-dated.md", "TEAM-a-members.md", "TEAM-a-plain.md"]
    said_views = views("a")
    lines = (faced("a").get("declared") or {}).get("documents")
    documents = sorted((one.get("document"), one.get("template"), one.get("origin"), tuple(one.get("roles") or []))
                       for one in began.get("documents") or [])
    if (played.returncode == 0 and rendered == wanted
            and said_views == {"ma": sorted([*root, "roles/TEAM-a-by-batch.md"]),
                               "mi": sorted([*root, "roles/TEAM-a-pair.md"]),
                               "mb": sorted([*root, "roles/TEAM-a-by-batch.md", "roles/TEAM-a-pair.md"])}
            and lines == [{"key": "all", "team": ["notes/dated"], "season": ["notes/plain"]},
                          {"key": "watch", "team": ["guide/both"], "season": []},
                          {"key": "make", "team": [], "season": ["sources/by-batch"]},
                          {"key": "inspect", "team": [], "season": ["review/pair"]}]
            and documents == sorted([("TEAM-a-dated.md", "notes/dated", "house", ()),
                                     ("TEAM-a-plain.md", "notes/plain", "house", ()),
                                     ("roles/TEAM-a-both.md", "guide/both", "house", ("watch",)),
                                     ("roles/TEAM-a-by-batch.md", "sources/by-batch", "house", ("make",)),
                                     ("roles/TEAM-a-pair.md", "review/pair", "house", ("inspect",))])
            and {one: began.get("rendered", {}).get(one) for one in wanted}
            == {one: digest(body.encode("utf-8")) for one, body in wanted.items()}
            and "organization" not in began and "compose" not in began):
        held("(a) the documents rendered by role", "TEAM.md all notes/dated + watch guide/both, SEASON.md house-flow: "
             "two documents at the root, three under roles/, holes filled, {{ one brace, <lot> left; ma, mi, mb each "
             "their keys' documents once; declared.documents by key from both files; team-started documents and "
             "rendered, no organization nor compose")
    else:
        failures.append(f"  ✗ (a) by role                rc={played.returncode} rendered={rendered} views={said_views} "
                        f"lines={lines} documents={documents} keys={sorted(began)} {played.stderr.strip()[-200:]!r}")

    # --- (b) each refusal names its cause and writes nothing ---------------------------------------------------
    laid(h.house / "teams" / "templates", {"notes/broken.md": "---\ndescription: a hole\n---\nHello {nowhere}.\n",
                                           "other/plain.md": "---\ndescription: another plain\n---\nOther.\n"})
    team("b", None)
    first = start("b")
    h.off_season("b")
    (h.teams / "b" / "holed.md").write_text("Hello {who}.\n", encoding="utf-8")
    asks = {
        "document-unknown": ("---\ndocuments: |\n  all notes/nosuch\n---\n", "notes/nosuch"),
        "document-unknown ": ("---\ndocuments: |\n  make mine\n---\n", "mine"),
        "role-unknown": ("---\ndocuments: |\n  ghost notes/plain\n---\n", "ghost"),
        "value-missing": ("---\ntemplate: seasons/house-flow\n---\n", "lead"),
        "value-unknown": ("---\ntemplate: seasons/house-flow\nvalues: |\n  lead = alice\n  ghost = x\n---\n", "ghost"),
        "value-undeclared": ("---\ndocuments: |\n  all notes/broken\n---\n", "nowhere"),
        "document-collision": ("---\ndocuments: |\n  all notes/plain\n  make other/plain\n---\n", "plain"),
        "document-holes": ("---\ndocuments: |\n  all holed\n---\n", "holed"),
        "template-unknown": ("---\ntemplate: seasons/nosuch\n---\n", "seasons/nosuch"),
        "season-invalid": ("---\ncompose: |\n  notes plain\n---\n", "compose"),
        "season-invalid ": ("---\ntemplate: seasons/house-flow\nvalues: |\n  lead alice\n---\n", "lead alice"),
    }
    wrong = []
    for code, (season, said) in asks.items():
        season_of("b").write_text(season, encoding="utf-8")
        before = kept(h, "b")
        refused = start("b")
        if (refused.returncode != 2 or code_of(refused) != code.strip() or said not in refused.stderr
                or kept(h, "b") != before):
            wrong.append(f"{code.strip()}: rc={refused.returncode} same={kept(h, 'b') == before} "
                         f"{refused.stderr.strip()[-200:]!r}")
    if first.returncode == 0 and not wrong:
        bench.refusals += len(asks)
        held("(b) each refusal writes nothing", "document-unknown twice, role-unknown, value-missing, value-unknown, "
             "value-undeclared, document-collision, document-holes, template-unknown, season-invalid twice: each "
             "naming its cause, the directory and the journal byte for byte")
    else:
        failures.append(f"  ✗ (b) refused                rc={first.returncode} {wrong}")

    # --- (c) rendered again: a value changed, a preset of fewer documents ----------------------------------------
    team("c", SEASON)
    start("c")
    then = started_at("c").get("rendered") or {}
    season_of("c").write_text(SEASON.replace("alice", "bob"), encoding="utf-8")
    again = start("c")
    now = started_at("c").get("rendered") or {}
    pair_now = text("c", "roles/TEAM-c-pair.md")
    season_of("c").write_text("---\ntemplate: seasons/lean\n---\n", encoding="utf-8")
    leaner = start("c")
    lean = started_at("c")
    if (again.returncode == 0 and pair_now == "---\nserve: |\n  TEAM-c-members.md\n---\nbob reads it; write {braces}.\n"
            and now.get("roles/TEAM-c-pair.md") != then.get("roles/TEAM-c-pair.md")
            and now.get("TEAM-c-plain.md") == then.get("TEAM-c-plain.md")
            and leaner.returncode == 0 and files("c") == ["TEAM-c-by-batch.md"]
            and not (h.teams / "c" / "roles").exists()
            and [one.get("document") for one in lean.get("documents") or []] == ["TEAM-c-by-batch.md"]):
        held("(c) rendered again", "lead alice -> bob: roles/TEAM-c-pair.md rendered anew, its digest changed, "
             "plain's the same; lean chosen: the documents nobody names removed with roles/, by-batch at the root")
    else:
        failures.append(f"  ✗ (c) again                  rc={again.returncode}/{leaner.returncode} pair={pair_now!r} "
                        f"then={then} now={now} files={files('c')} {(again.stderr or leaner.stderr).strip()[-200:]!r}")

    # --- (d) a rendered document edited by hand -------------------------------------------------------------
    team("d", SEASON)
    start("d")
    edited = h.teams / "d" / "TEAM-d-plain.md"
    edited.write_text((edited.read_text(encoding="utf-8") if edited.is_file() else "") + "My own line.\n",
                      encoding="utf-8")
    h.off_season("d")
    before = kept(h, "d")
    refused = start("d")
    same = kept(h, "d") == before
    edited.unlink(missing_ok=True)
    restored = start("d")
    if (refused.returncode == 2 and code_of(refused) == "rendered-edited" and "TEAM-d-plain.md" in refused.stderr
            and same and restored.returncode == 0 and text("d", "TEAM-d-plain.md") == "Notes of d.\n"):
        bench.refusals += 1
        held("(d) a rendered document edited", "edited: rendered-edited naming TEAM-d-plain.md, the directory and "
             "the journal byte for byte; deleted: rendered again")
    else:
        failures.append(f"  ✗ (d) edited                 rc={refused.returncode}/{restored.returncode} same={same} "
                        f"{refused.stderr.strip()[-200:]!r} {restored.stderr.strip()[-200:]!r}")

    # --- (e) no season ------------------------------------------------------------------------------------
    team("e", None)
    bare = start("e")
    season_of("c").unlink(missing_ok=True)
    dropped = start("c")
    if (bare.returncode == 0 and files("e") == [] and started_at("e").get("documents") == []
            and dropped.returncode == 0 and files("c") == [] and started_at("c").get("documents") == []):
        held("(e) no season", "no SEASON.md: no document, documents empty; SEASON.md removed after a season with "
             "documents: TEAM-c-by-batch.md removed at the next start")
    else:
        failures.append(f"  ✗ (e) no season             rc={bare.returncode}/{dropped.returncode} e={files('e')} "
                        f"c={files('c')} {dropped.stderr.strip()[-200:]!r}")

    # --- (f) a preset's lines are defaults --------------------------------------------------------------------
    team("f", "---\ntemplate: seasons/house-flow\nvalues: |\n  lead = alice\ndocuments: |\n  make sources/trunk\n---\n")
    replaced = start("f")
    if (replaced.returncode == 0
            and files("f") == ["TEAM-f-plain.md", "roles/TEAM-f-pair.md", "roles/TEAM-f-trunk.md"]
            and text("f", "roles/TEAM-f-trunk.md") == "---\n---\nPush to origin on main.\n"):
        held("(f) a preset's lines are defaults", "make sources/trunk replaces the preset's make line; all and "
             "{checker} kept from the preset")
    else:
        failures.append(f"  ✗ (f) preset lines           rc={replaced.returncode} files={files('f')} "
                        f"{replaced.stderr.strip()[-200:]!r}")

    # --- (g) a name taken, a mounted document judged ---------------------------------------------------------
    team("g", SEASON)
    (h.teams / "g" / "TEAM-g-plain.md").write_text("# The owner's notes\n", encoding="utf-8")
    before_taken = kept(h, "g")
    taken = start("g")
    same_taken = kept(h, "g") == before_taken
    (h.teams / "g" / "TEAM-g-plain.md").unlink(missing_ok=True)
    laid(h.house / "teams" / "templates", {
        "rules/strict.md": "---\ndescription: strict\nmount: turn.begin\nconstraints.behavior: |\n  KX1  keep it short.\n"
                           "---\nStrict.\n",
        "rules/served.md": "---\ndescription: serves the review\nmount: turn.begin\nconstraints.behavior: |\n"
                           "  TM1  read the review first.\nserve: |\n  TEAM-{team}-pair.md\n---\nServed.\n"})
    season_of("g").write_text("---\ndocuments: |\n  all rules/strict\n---\n", encoding="utf-8")
    before_mount = kept(h, "g")
    mounted = start("g")
    same_mount = kept(h, "g") == before_mount
    team("gs", "---\nvalues: |\n  lead = alice\ndocuments: |\n  all review/pair\n---\n")
    first_gs = start("gs")
    season_of("gs").write_text("---\ndocuments: |\n  all rules/served\n---\n", encoding="utf-8")
    h.off_season("gs")
    before_served = kept(h, "gs")
    dropped = start("gs")
    same_served = kept(h, "gs") == before_served
    if (taken.returncode == 2 and code_of(taken) == "document-collision" and "TEAM-g-plain.md" in taken.stderr
            and same_taken and mounted.returncode == 2 and code_of(mounted) == "common-code-prefix"
            and "KX1" in mounted.stderr and same_mount and not h.journal_of("g").exists()
            and first_gs.returncode == 0 and dropped.returncode == 2 and code_of(dropped) == "common-serve-unknown"
            and "TEAM-gs-pair.md" in dropped.stderr and same_served):
        bench.refusals += 3
        held("(g) a name taken, a mounted document judged", "TEAM-g-plain.md by hand: document-collision naming it; "
             "a document mounting KX1: common-code-prefix; a mounted document serving TEAM-gs-pair.md as the start "
             "stops naming review/pair: common-serve-unknown; nothing written in any")
    else:
        failures.append(f"  ✗ (g) taken / mounted        rc={taken.returncode}/{mounted.returncode}/{first_gs.returncode}/"
                        f"{dropped.returncode} same={same_taken}/{same_mount}/{same_served} "
                        f"{taken.stderr.strip()[-200:]!r} {mounted.stderr.strip()[-200:]!r} {dropped.stderr.strip()[-200:]!r}")

    # --- (h) the owner's word: served by its name, read again when it changes ------------------------------------
    team("h", SEASON + "Season word one.\n")
    team("h0", SEASON)
    opened = h.call("team", "start", "h", "--message", "go", *h.harnessed, "--no-tick")
    start("h0")
    served = head_served("h")
    season_of("h").write_text(SEASON + "Season word two.\n", encoding="utf-8")
    h.call("team", "tick", "h")
    woke = h.settled("h", lambda found: bool(T.by_kind(found, "done")) and T.all_ended(found), 60)
    prompt = (h.prompts_of("m") or [""])[0]
    at = prompt.find("INFORMATION — SEASON.md")
    if (opened.returncode == 0 and "SEASON.md" in served and served.index("SEASON.md") > served.index("TEAM-h.md")
            and "TEAM-h-plain.md" in served and woke and at >= 0 and "Season word two." in prompt[at:]
            and "Season word one." not in prompt and "SEASON.md" not in head_served("h0")):
        held("(h) the owner's word", f"the head serves {served}; rewritten after the start, the wake-up reads "
             "`Season word two.` under SEASON.md; a SEASON.md without a body is not named")
    else:
        failures.append(f"  ✗ (h) the owner's word        rc={opened.returncode} served={served} woke={woke} at={at} "
                        f"h0={head_served('h0')} {opened.stderr.strip()[-200:]!r}")

    # --- (i) the keys of a line ---------------------------------------------------------------------------------
    laid(h.house / "teams" / "templates", {
        "seasons/observing.md": "---\ndescription: a key\ndocuments: |\n  observe notes/plain\n---\n"})
    two = ("---\nagents: |\n  ra agents/ra\n  rb agents/rb\nreports: |\n  rb -> ra\nroot: ra\nschedule: off\n"
           "roles: |\n  make ra\n  inspect rb\n  audit rb\n---\nHold the roles.\n")
    team("ri", SEASON, two)
    passed = start("ri")
    reached = views("ri")
    team("rl", SEASON.replace("  lead = alice\n", "  lead = alice\n  checker = audit\n"), two)
    other_key = start("rl")
    audit = [one.get("roles") for one in started_at("rl").get("documents") or [] if one.get("template") == "review/pair"]
    refusals = {}
    for name, season, said in (("rj", "---\ntemplate: seasons/observing\n---\n", ("observe", "observing.md")),
                               ("rk", "---\ndocuments: |\n  ghost notes/plain\n---\n", ("ghost", "SEASON.md")),
                               ("rm", "---\ndocuments: |\n  {nowhere} notes/plain\n---\n", ("nowhere",))):
        team(name, season, two)
        before_r = kept(h, name)
        refused = start(name)
        refusals[name] = (refused.returncode, code_of(refused), all(one in refused.stderr for one in said),
                          kept(h, name) == before_r, verdict_code(name) if name == "rj" else code_of(refused))
    if (passed.returncode == 0 and "roles/TEAM-ri-pair.md" in reached.get("rb", [])
            and "roles/TEAM-ri-pair.md" not in reached.get("ra", [])
            and "roles/TEAM-ri-by-batch.md" in reached.get("ra", [])
            and other_key.returncode == 0 and audit == [["audit"]]
            and refusals == {"rj": (2, "role-unknown", True, True, "role-unknown"),
                             "rk": (2, "role-unknown", True, True, "role-unknown"),
                             "rm": (2, "value-undeclared", True, True, "value-undeclared")}):
        bench.refusals += 3
        held("(i) the keys of a line", "{checker} filled to inspect: pair reaches rb, by-batch ra; checker = audit: "
             "pair on audit; role-unknown from the preset (observe, observing.md) and from SEASON.md (ghost), the "
             "verdict the same; {nowhere} value-undeclared; nothing written")
    else:
        failures.append(f"  ✗ (i) the keys of a line     rc={passed.returncode}/{other_key.returncode} views={reached} "
                        f"audit={audit} refusals={refusals} {(passed.stderr or other_key.stderr).strip()[-200:]!r}")

    # --- (j) the team's documents kept through seasons --------------------------------------------------------
    own = ("---\nagents: |\n  m agents/m\nroot: m\nschedule: off\nroles: |\n  make m\n  inspect m\ndocuments: |\n"
           "  all notes/dated\nvalues: |\n  day = friday\n---\nHold the work.\n")
    team("p", SEASON, own)
    one = start("p")
    dated_one = text("p", "TEAM-p-dated.md")
    season_of("p").write_text("---\ntemplate: seasons/lean\n---\n", encoding="utf-8")
    two_started = start("p")
    dated_two = text("p", "TEAM-p-dated.md")
    said = (faced("p").get("declared") or {}).get("documents")
    h.declare("p", own.replace("friday", "sunday"))
    moved = [entry.get("key") for entry in faced("p").get("pending") or []]
    h.declare("p", own.replace("documents: |\n  all notes/dated\n", "").replace("values: |\n  day = friday\n", ""))
    three = start("p")
    if (one.returncode == 0 and dated_one == "Notes of p, read on friday.\n" and two_started.returncode == 0
            and dated_two == dated_one and said == [{"key": "all", "team": ["notes/dated"],
                                                     "season": ["sources/by-batch"]}]
            and moved == ["values", "documents"] and three.returncode == 0 and text("p", "TEAM-p-dated.md") is None
            and "TEAM-p-dated.md" not in (started_at("p").get("rendered") or {})):
        held("(j) the team's documents kept through seasons", "all notes/dated of TEAM.md: the same bytes under "
             "house-flow then lean; declared.documents the line of all from both files; day = sunday: pending values "
             "and documents; the line taken out: the document leaves")
    else:
        failures.append(f"  ✗ (j) the team's documents    rc={one.returncode}/{two_started.returncode}/{three.returncode} "
                        f"dated={dated_one!r}/{dated_two!r} said={said} moved={moved} "
                        f"{(one.stderr or three.stderr).strip()[-200:]!r}")

    # --- (k) a file of the team's directory -------------------------------------------------------------------
    team("k", "---\ndocuments: |\n  all mine\n  make theirs\n---\n")
    (h.teams / "k" / "mine.md").write_text("Mine, {{as it stands}}.\n", encoding="utf-8")
    (h.teams / "k" / "theirs.md").write_text("Theirs.\n", encoding="utf-8")
    local = start("k")
    if (local.returncode == 0 and text("k", "TEAM-k-mine.md") == "Mine, {{as it stands}}.\n"
            and text("k", "roles/TEAM-k-theirs.md") == "---\n---\nTheirs.\n"
            and {one.get("template"): one.get("origin") for one in started_at("k").get("documents") or []}
            == {"mine": "team", "theirs": "team"}):
        held("(k) a file of the team's directory", "all mine: mine.md served as it stands as TEAM-k-mine.md, {{ kept; "
             "make theirs: roles/TEAM-k-theirs.md opening on a front matter; origin team")
    else:
        failures.append(f"  ✗ (k) a file of the directory rc={local.returncode} files={files('k')} "
                        f"{local.stderr.strip()[-200:]!r}")

    # --- (l) the season written by `team declare --season` -------------------------------------------------------
    def declare(name: str, *args: str):
        played = h.call("team", "declare", name, "--season", *args, "--json")
        try:
            return played, json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return played, {}

    rest = lambda found: {one: data for one, data in found.items() if one != "SEASON.md"}
    team("w", None)
    bare = start("w")
    h.off_season("w")
    before_w = kept(h, "w")
    born, face_w = declare("w", "--template", "seasons/house-flow", "--value", "lead=alice", "--document",
                           "all notes/dated")
    after_w = kept(h, "w")
    wanted_w = b"---\ntemplate: seasons/house-flow\nvalues: |\n  lead = alice\ndocuments: |\n  all notes/dated\n---\n"
    under = start("w")
    season_of("w").write_text("---\n# the season's note\ntemplate: seasons/house-flow\nmodel: m-1\nvalues: |\n"
                              "  lead = alice\ndocuments: |\n  all notes/dated\n---\nThe season's word.\n", encoding="utf-8")
    word = bench.temp() / "season-word.md"
    word.write_text("Another season.\n", encoding="utf-8")
    steps = (
        (("--value", "lead=bob"), ["values"], lambda body: body.replace("  lead = alice\n", "  lead = bob\n")),
        (("--no-document", "all"), ["documents"], lambda body: body.replace("documents: |\n  all notes/dated\n", "")),
        (("--body-file", str(word)), ["body"], lambda body: body.replace("The season's word.\n", "Another season.\n")),
    )
    h.off_season("w")
    still, wrong = kept(h, "w"), []
    for args, keys, change in steps:
        played, face = declare("w", *args)
        now = kept(h, "w")
        wanted = change(still[0]["SEASON.md"].decode("utf-8")).encode("utf-8")
        if not (played.returncode == 0 and now[0].get("SEASON.md") == wanted and wanted != still[0]["SEASON.md"]
                and rest(now[0]) == rest(still[0]) and now[1] == still[1] and face.get("written") == keys):
            wrong.append(f"{' '.join(args)}: rc={played.returncode} face={face} file={now[0].get('SEASON.md')!r} "
                         f"{played.stderr.strip()[-160:]!r}")
        still = now
    refused = {"template-unknown": declare("w", "--template", "seasons/nosuch")[0],
               "value-unknown": declare("w", "--value", "ghost=x")[0],
               "team-unknown": declare("nobody", "--template", "seasons/house-flow", "--value", "lead=alice")[0],
               "flag-retired": declare("w", "--compose", "notes plain")[0]}
    codes = {code: (one.returncode, code_of(one)) for code, one in refused.items()}
    if (bare.returncode == 0 and "SEASON.md" not in before_w[0] and born.returncode == 0
            and after_w[0].get("SEASON.md") == wanted_w and rest(after_w[0]) == before_w[0] and after_w[1] == before_w[1]
            and face_w.get("file") == "teams/w/SEASON.md" and face_w.get("written") == ["template", "values", "documents"]
            and face_w.get("verdict") == {"ok": True, "refusal": None}
            and [one.get("key") for one in face_w.get("pending") or []] == ["documents"]
            and under.returncode == 0 and text("w", "TEAM-w-dated.md") == "Notes of w, read on monday.\n"
            and not wrong and codes == {code: (2, code) for code in refused} and kept(h, "w") == still
            and not (h.teams / "nobody").exists()):
        bench.refusals += len(refused)
        held("(l) the season written by team declare --season", "SEASON.md born with template, values, documents "
             "alone, pending [documents], no event, no document rendered; the next start renders them; --value, "
             "--no-document, --body-file each its key alone; template-unknown, value-unknown, team-unknown, "
             "flag-retired for --compose: nothing written")
    else:
        failures.append(f"  ✗ (l) declare --season        rc={bare.returncode}/{born.returncode}/{under.returncode} "
                        f"season={after_w[0].get('SEASON.md')!r} face={face_w} wrong={wrong} codes={codes} "
                        f"same={kept(h, 'w') == still} {(born.stderr or under.stderr).strip()[-200:]!r}")

    return 0
