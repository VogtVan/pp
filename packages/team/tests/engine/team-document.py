"""Scenario `team-document` -- 7 case(s): `team document <directory>/<name>`, the one writer of a house's documents
under `<house>/.pp/teams/templates/` -- it reads a document's source, creates one (`--new`), replaces its text after a
judgment (`--body-file`) and deletes it (`--delete`); the documents of the package are read only. Its houses and
readings shared in `_templates.py`. No wake-up plays: nothing is started.
- (a) the source read: a house document `notes/own` says its text whole, origin `house`, its path; a package document
  `review/read-commits` origin `package`, its text the package file's; a preset `seasons/files` kind `preset`; under
  `--json` one object `{template, origin, kind, path, text}`; `notes/nosuch` refuses `document-unknown` -- nothing
  written anywhere
- (b) the creation: `--new notes/fresh` writes the skeleton under `.pp/teams/templates/notes/fresh.md` (a
  `description:`, a title, no preset key), `team templates --json` lists it `document` `house`, `--render` renders
  it; a second `--new` refuses `document-exists`, the file byte for byte; `--new review/read-commits` creates the
  house's own, which masks the package's -- said by the verb, `origin` house at `templates --json`
- (c) the replacement judged: `--body-file` with a valid text replaces the house document byte for byte, `-` reads
  standard input; a front matter that never closes, a preset key (`documents`, `form`, `members`) or a line of
  `values:` of another form refuse `document-invalid`, the file byte for byte; a package document refuses
  `document-readonly`, an unknown one `document-unknown`
- (d) the deletion guarded: a house document named by a line of a `TEAM.md`, of a `SEASON.md` or of a house preset
  refuses `document-used`, the output naming the team or the preset, the file and the key; once detached it is
  deleted; a document alone in its directory leaves no directory; the house's `review/read-commits` deleted gives the
  package's back, said; a package document refuses `document-readonly`, an unknown one `document-unknown`
- (e) the usage and its refusals: `team document` alone is the usage, which names the verb; a name that is not
  `<slug>/<slug>` refuses `template-invalid`; two actions, `--body-file` without a path, an unknown flag are the
  usage; no refusal writes
- (f) the text read in bytes (s.1603): a house document written with CRLF line endings, handed back as it stands by
  `--body-file <path>` and by `--body-file -`, says `unchanged` -- the file byte for byte
- (g) the preset never masked (s.1604): `--new seasons/files`, a preset of the package, refuses `document-preset` --
  no house file of that name, the house's templates byte for byte
Every case: the teams' directories and the package's templates at their bytes (KVD1), every refusal leaving the
house's templates at their bytes (KVD2).
"""
from __future__ import annotations

import hashlib
import json

from tests.harness import cli, support

T = support(__file__, "team")
S = support(__file__, "templates")
laid, code_of, templates_of = S.laid, S.code_of, S.templates_of

SHELF = {
    "notes/own.md": "---\ndescription: the house's own notes\n---\n# Own\n\nNotes of {team}.\n",
    "used/by-team.md": "---\ndescription: named by a team\n---\nTeam.\n",
    "used/by-season.md": "---\ndescription: named by a season\n---\nSeason.\n",
    "used/by-preset.md": "---\ndescription: named by a preset\n---\nPreset.\n",
    "alone/gone.md": "---\ndescription: alone in its directory\n---\nGone.\n",
    "seasons/mine.md": "---\ndescription: the house's preset\ndocuments: |\n  {checker} used/by-preset\n---\n",
}
VALID = "---\ndescription: replaced\nvalues: |\n  day = monday -- the day it is read\n---\n# Fresh\n\nRead on {day}.\n"
PIPED = "---\ndescription: piped\n---\n# Piped\n"
BROKEN = {"a front matter that never closes": "---\ndescription: torn\n# no end\n",
          "a preset key documents": "---\ndescription: x\ndocuments: |\n  all notes/own\n---\nX.\n",
          "a preset key form": "---\ndescription: x\nform: star\n---\nX.\n",
          "a preset key members": "---\ndescription: x\nmembers: |\n  a\n---\nX.\n",
          "a line of values of another form": "---\ndescription: x\nvalues: |\n  day monday\n---\nX.\n"}
FIVE = {"template", "origin", "kind", "path", "text"}


def prints(place) -> dict:
    """-> every file under `place`, at any depth: {relative path: sha256}; {} when it stands not."""
    return ({str(one.relative_to(place)): hashlib.sha256(one.read_bytes()).hexdigest()
             for one in sorted(place.rglob("*")) if one.is_file()} if place.is_dir() else {})


def read_json(played) -> dict:
    try:
        return json.loads(played.stdout.strip().splitlines()[-1]) if played.returncode == 0 else {}
    except (ValueError, IndexError):
        return {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={}, slug="docs")
    shelf = h.house / "teams" / "templates"
    laid(shelf, SHELF)
    script = next(h.house.rglob("pp-team.py"), None)
    package = script.parents[2] / "templates" if script is not None else h.house / "missing"

    def call(*args: str, stdin: str | None = None):
        return cli(h.engine, "--instance", str(h.house), "team", "document", *args, cwd=h.ws, stdin=stdin, env=h.env)

    def worlds() -> tuple[dict, dict]:
        return prints(h.teams), prints(package)

    def refused(played, code: str) -> bool:
        return played.returncode == 2 and code_of(played) == code

    # --- (a) the source read ------------------------------------------------------------------------------------------
    before, shelf_before = worlds(), prints(shelf)
    own, own_json = call("notes/own"), read_json(call("notes/own", "--json"))
    commits = read_json(call("review/read-commits", "--json"))
    preset_read = read_json(call("seasons/files", "--json"))
    unknown = call("notes/nosuch")
    commits_file = package / "review" / "read-commits.md"
    if (own.returncode == 0 and SHELF["notes/own.md"] in own.stdout and "house" in own.stdout
            and "notes/own.md" in own.stdout
            and set(own_json) == FIVE and own_json.get("origin") == "house" and own_json.get("kind") == "document"
            and own_json.get("text") == SHELF["notes/own.md"] and own_json.get("template") == "notes/own"
            and str(own_json.get("path", "")).endswith("teams/templates/notes/own.md")
            and commits.get("origin") == "package" and commits_file.is_file()
            and commits.get("text") == commits_file.read_text(encoding="utf-8")
            and preset_read.get("kind") == "preset" and preset_read.get("origin") == "package"
            and refused(unknown, "document-unknown")
            and worlds() == before and prints(shelf) == shelf_before):
        held("(a) the source read", "notes/own: its text whole, house, its path; --json five keys; review/read-commits "
             "package, the package file's text; seasons/files kind preset; notes/nosuch document-unknown; nothing "
             "written")
    else:
        failures.append(f"  ✗ (a) the source read        rc={own.returncode} json={own_json} commits={commits.get('origin')} "
                        f"preset={preset_read.get('kind')} unknown={unknown.returncode}/{code_of(unknown)} "
                        f"{(own.stderr or unknown.stderr).strip()[-200:]!r}")

    # --- (b) the creation ---------------------------------------------------------------------------------------------
    before = worlds()
    fresh = shelf / "notes" / "fresh.md"
    made = call("notes/fresh", "--new")
    text = fresh.read_text(encoding="utf-8") if fresh.is_file() else ""
    head = text.split("---\n", 2)[1] if text.startswith("---\n") and text.count("---\n") >= 2 else ""
    listed = templates_of(h).get("notes/fresh") or {}
    rendered = h.call("team", "templates", "--render", "notes/fresh", "--value", "team=x")
    bytes_fresh = fresh.read_bytes() if fresh.is_file() else b""
    again = call("notes/fresh", "--new")
    masked = call("review/read-commits", "--new")
    mask = shelf / "review" / "read-commits.md"
    seen = templates_of(h).get("review/read-commits") or {}
    if (made.returncode == 0 and fresh.is_file() and "description:" in head
            and not any(f"\n{key}:" in f"\n{head}" for key in ("documents", "form", "members"))
            and "\n# " in f"\n{text.split('---', 2)[-1]}"
            and (listed.get("kind"), listed.get("origin")) == ("document", "house")
            and rendered.returncode == 0
            and refused(again, "document-exists") and fresh.read_bytes() == bytes_fresh
            and masked.returncode == 0 and mask.is_file() and "package" in masked.stdout
            and seen.get("origin") == "house"
            and worlds() == before):
        held("(b) the creation", "notes/fresh born from the skeleton (description:, a title, no preset key), listed "
             "document house, rendered; a second --new document-exists, byte for byte; review/read-commits created in "
             "the house, the package's masked and said")
    else:
        failures.append(f"  ✗ (b) the creation           rc={made.returncode} text={text!r} listed={listed} "
                        f"render={rendered.returncode} again={again.returncode}/{code_of(again)} "
                        f"masked={masked.returncode} {masked.stdout.strip()[-120:]!r} seen={seen.get('origin')} "
                        f"{(made.stderr or masked.stderr).strip()[-200:]!r}")

    # --- (c) the replacement judged -----------------------------------------------------------------------------------
    before = worlds()
    good = bench.temp() / "valid.md"
    good.write_text(VALID, encoding="utf-8")
    replaced = call("notes/fresh", "--body-file", str(good))
    replaced_ok = fresh.is_file() and fresh.read_text(encoding="utf-8") == VALID
    piped = call("notes/own", "--body-file", "-", stdin=PIPED)
    own_file = shelf / "notes" / "own.md"
    piped_ok = own_file.read_text(encoding="utf-8") == PIPED
    wrong = []
    for why, broken in BROKEN.items():
        path = bench.temp() / "broken.md"
        path.write_text(broken, encoding="utf-8")
        standing = prints(shelf)
        played = call("notes/fresh", "--body-file", str(path))
        if not (refused(played, "document-invalid") and prints(shelf) == standing):
            wrong.append(f"{why}: rc={played.returncode} {played.stderr.strip()[-160:]!r}")
    standing = prints(shelf)
    readonly = call("review/read-files", "--body-file", str(good))
    nosuch = call("notes/nosuch", "--body-file", str(good))
    if (replaced.returncode == 0 and replaced_ok and piped.returncode == 0 and piped_ok and not wrong
            and refused(readonly, "document-readonly") and refused(nosuch, "document-unknown")
            and prints(shelf) == standing and not (shelf / "review" / "read-files.md").exists()
            and worlds() == before):
        bench.refusals += len(BROKEN) + 2
        held("(c) the replacement judged", "a valid text replaces notes/fresh byte for byte, `-` reads stdin; a front "
             "matter that never closes, the keys documents, form, members and a values line of another form: "
             "document-invalid, byte for byte; review/read-files document-readonly; notes/nosuch document-unknown")
    else:
        failures.append(f"  ✗ (c) the replacement        rc={replaced.returncode}/{piped.returncode} "
                        f"ok={replaced_ok}/{piped_ok} wrong={wrong} readonly={readonly.returncode}/"
                        f"{code_of(readonly)} nosuch={nosuch.returncode}/{code_of(nosuch)} "
                        f"{(replaced.stderr or piped.stderr).strip()[-200:]!r}")

    # --- (d) the deletion guarded -------------------------------------------------------------------------------------
    h.declare("ta", "---\nagents: |\n  m agents/m\nroot: m\ndocuments: |\n  all used/by-team notes/own\n---\n")
    h.declare("tb", "---\nagents: |\n  m agents/m\nroot: m\n---\n")
    (h.teams / "tb" / "SEASON.md").write_text("---\ndocuments: |\n  readers used/by-season\n---\n", encoding="utf-8")
    before = worlds()
    standing = prints(shelf)
    by_team, by_season, by_preset = (call("used/by-team", "--delete"), call("used/by-season", "--delete"),
                                     call("used/by-preset", "--delete"))
    guarded = (refused(by_team, "document-used") and "ta" in by_team.stderr and "TEAM.md" in by_team.stderr
               and "all" in by_team.stderr
               and refused(by_season, "document-used") and "tb" in by_season.stderr
               and "SEASON.md" in by_season.stderr and "readers" in by_season.stderr
               and refused(by_preset, "document-used") and "seasons/mine" in by_preset.stderr
               and "{checker}" in by_preset.stderr
               and prints(shelf) == standing and worlds() == before)
    h.declare("ta", "---\nagents: |\n  m agents/m\nroot: m\n---\n")
    before = worlds()
    detached = call("used/by-team", "--delete")
    gone = call("alone/gone", "--delete")
    back = call("review/read-commits", "--delete")
    seen = templates_of(h).get("review/read-commits") or {}
    standing = prints(shelf)
    readonly = call("review/read-files", "--delete")
    nosuch = call("notes/nosuch", "--delete")
    if (guarded and detached.returncode == 0 and not (shelf / "used" / "by-team.md").exists()
            and (shelf / "used").is_dir()
            and gone.returncode == 0 and not (shelf / "alone").exists()
            and back.returncode == 0 and "package" in back.stdout and seen.get("origin") == "package"
            and refused(readonly, "document-readonly") and refused(nosuch, "document-unknown")
            and prints(shelf) == standing and worlds() == before):
        bench.refusals += 5
        held("(d) the deletion guarded", "used/by-team, used/by-season, used/by-preset: document-used naming ta TEAM.md "
             "all, tb SEASON.md readers, seasons/mine {checker}; detached, used/by-team deleted; alone/ removed with "
             "its last document; the house's review/read-commits deleted, the package's back and said; review/read-files "
             "document-readonly; notes/nosuch document-unknown")
    else:
        failures.append(f"  ✗ (d) the deletion           guarded={guarded} "
                        f"{by_team.returncode}/{code_of(by_team)} {by_team.stderr.strip()[-160:]!r} "
                        f"{by_season.stderr.strip()[-120:]!r} {by_preset.stderr.strip()[-120:]!r} "
                        f"detached={detached.returncode} gone={gone.returncode} back={back.returncode} "
                        f"{back.stdout.strip()[-120:]!r} seen={seen.get('origin')} readonly={readonly.returncode}/"
                        f"{code_of(readonly)} nosuch={nosuch.returncode}/{code_of(nosuch)} "
                        f"{(detached.stderr or gone.stderr or back.stderr).strip()[-200:]!r}")

    # --- (e) the usage and its refusals -------------------------------------------------------------------------------
    before, standing = worlds(), prints(shelf)
    bare = call()
    names = [call(one) for one in ("notes", "Bad_Dir/x", "notes/Bad_Name", "a/b/c")]
    usages = [call(*args) for args in (("notes/own", "--new", "--delete"),
                                       ("notes/own", "--new", "--body-file", str(good)),
                                       ("notes/own", "--body-file"), ("notes/own", "--nosuch"))]
    if (bare.returncode == 2 and "usage: pp-team" in bare.stderr and "document <directory>/<name>" in bare.stderr
            and all(refused(one, "template-invalid") for one in names)
            and all(one.returncode == 2 and "usage: pp-team" in one.stderr for one in usages)
            and prints(shelf) == standing and worlds() == before):
        bench.refusals += 1 + len(names) + len(usages)
        held("(e) the usage and its refusals", "team document alone: the usage naming the verb; notes, Bad_Dir/x, "
             "notes/Bad_Name, a/b/c: template-invalid; two actions, --body-file without a path, an unknown flag: the "
             "usage; nothing written")
    else:
        failures.append(f"  ✗ (e) the usage               bare={bare.returncode} {bare.stderr.strip()[-160:]!r} "
                        f"names={[(one.returncode, code_of(one)) for one in names]} "
                        f"usages={[one.returncode for one in usages]}")

    # --- (f) the text read in bytes (s.1603) --------------------------------------------------------------------------
    crlf = "---\r\ndescription: written under Windows\r\n---\r\n# Own\r\n\r\nTwo lines.\r\n"
    own_file = shelf / "notes" / "own.md"
    own_file.write_bytes(crlf.encode("utf-8"))
    same = bench.temp() / "crlf.md"
    same.write_bytes(crlf.encode("utf-8"))
    before = worlds()
    by_file = read_json(call("notes/own", "--body-file", str(same), "--json"))
    file_kept = own_file.read_bytes() == crlf.encode("utf-8")
    own_file.write_bytes(crlf.encode("utf-8"))
    by_stdin = read_json(call("notes/own", "--body-file", "-", "--json", stdin=crlf))
    stdin_kept = own_file.read_bytes() == crlf.encode("utf-8")
    if (by_file.get("done") == "unchanged" and file_kept and by_stdin.get("done") == "unchanged" and stdin_kept
            and worlds() == before):
        held("(f) the text read in bytes", "a CRLF house document handed back by --body-file <path> and by "
             "--body-file -: unchanged, the file byte for byte")
    else:
        failures.append(f"  ✗ (f) the text in bytes       file={by_file.get('done')}/{file_kept} "
                        f"stdin={by_stdin.get('done')}/{stdin_kept}")

    # --- (g) the preset never masked (s.1604) -------------------------------------------------------------------------
    before, standing = worlds(), prints(shelf)
    masking = call("seasons/files", "--new")
    if (refused(masking, "document-preset") and not (shelf / "seasons" / "files.md").exists()
            and prints(shelf) == standing and worlds() == before):
        bench.refusals += 1
        held("(g) the preset never masked", "--new seasons/files, a preset of the package: document-preset, no house "
             "file, the templates byte for byte")
    else:
        failures.append(f"  ✗ (g) the preset masked       rc={masking.returncode}/{code_of(masking)} "
                        f"file={(shelf / 'seasons' / 'files.md').exists()} {masking.stdout.strip()[-160:]!r}")
    return 0
