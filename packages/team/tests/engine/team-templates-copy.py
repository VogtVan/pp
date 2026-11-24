"""Scenario `team-templates-copy` -- 5 case(s): `team declare <name> --document "<key> <document> ..."`, a line of
`documents:` in `TEAM.md`, the one file `team declare` writes: nothing is copied, nothing is rendered at a birth --
`team start` renders the document -- and what a birth refuses before its first write. The sibling of
`team-templates`, its houses and readings shared in `_templates.py`. No wake-up plays: every start is `--no-tick`.
- (h) the line written: a house laying `git/par-lot` -- `team declare demo --template teams/supervisor-workers
  --document "all git/par-lot" --body-file <file>` writes `TEAM.md` and no other file: `documents:` holds
  `all git/par-lot`, the body of `TEAM.md` is the file's text
- (i) refused before any write: `--template teams/ghost` `template-unknown`; `--compose` `flag-retired`, naming
  `--document`; a line naming `git/inconnu`, `plans/shared` (hidden by `requires: plan`) or a directory nobody lays
  `document-unknown`; `--teams` the usage -- no `teams/<name>` left behind
- (j) the document rendered: `demo` starts -- `TEAM-demo-par-lot.md` rendered, the body of `par-lot.md` without its
  front matter, served by the head of `TEAM-demo.md`, kept at `team-started.documents`, `TEAM.md` at its bytes
- (k) a birth without a preset: without a member `team-invalid`, no `teams/<name>` left behind; with `--member a
  <path> --root a` and a line of `documents:`, `TEAM.md` written without `template:`, its declaration judged `ok`
- (m) a preset is never a line of `documents:`: a house laying `seasons/house-flow` -- `team declare ghost-8
  --template teams/solo --document "all seasons/house-flow"` refuses `document-unknown`, naming `template:`; no
  `teams/ghost-8` left behind
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
HOUSE = S.HOUSE_TEMPLATES
laid = S.laid
code_of = S.code_of
body_of = S.intention_of


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    o = T.House(bench, script={}, slug="owner")
    shelf = o.house / "teams" / "templates"
    laid(shelf, {key: text for key, text in HOUSE.items() if key.startswith(("git/", "plans/"))})

    # --- (h) the line written -----------------------------------------------------------------------
    word = bench.temp() / "word.md"
    word.write_text("Ship on Fridays.\n", encoding="utf-8")
    made = o.call("team", "declare", "demo", "--template", "teams/supervisor-workers", "--document", "all git/par-lot",
                  "--body-file", str(word))
    directory = o.teams / "demo"
    files = sorted(one.name for one in directory.iterdir()) if directory.is_dir() else []
    declared = (directory / "TEAM.md").read_text(encoding="utf-8") if (directory / "TEAM.md").is_file() else ""
    if (made.returncode == 0 and files == ["TEAM.md"] and "documents: |\n  all git/par-lot\n" in declared
            and declared.endswith("---\n" + word.read_text(encoding="utf-8"))):
        held("(h) the line written", "--template teams/supervisor-workers --document 'all git/par-lot' --body-file: "
             "TEAM.md alone in teams/demo, documents: all git/par-lot, its body the file's text")
    else:
        failures.append(f"  ✗ (h) the line written       rc={made.returncode} files={files} declared={declared!r} "
                        f"{made.stderr.strip()[-160:]!r}")

    # --- (i) refused before any write -------------------------------------------------------------
    asks = {
        "template-unknown": (("ghost-1", "--template", "teams/ghost"), ("teams/ghost",)),
        "flag-retired": (("ghost-2", "--template", "teams/solo", "--compose", "git par-lot"), ("--document",)),
        "document-unknown": (("ghost-3", "--template", "teams/solo", "--document", "all git/inconnu"), ("git/inconnu",)),
        "document-unknown ": (("ghost-4", "--template", "teams/solo", "--document", "all git/par-lot plans/shared"),
                              ("plans/shared",)),
        "document-unknown  ": (("ghost-5", "--template", "teams/solo", "--document", "all nosuch/x"), ("nosuch/x",)),
        "usage": (("ghost-6", "--teams", "solo", "--document", "all git/par-lot"), ("usage",)),
    }
    wrong = []
    for code, (args, said) in asks.items():
        played = o.call("team", "declare", *args)
        found = code_of(played) if code.strip() != "usage" else ("usage" if "usage:" in played.stderr else "")
        if played.returncode != 2 or found != code.strip() or not all(one in played.stderr for one in said):
            wrong.append(f"{code.strip()}: rc={played.returncode} {played.stderr.strip()[-160:]!r}")
    left = sorted(path.name for path in (o.teams.iterdir() if o.teams.is_dir() else ())
                  if path.name.startswith("ghost"))
    if not wrong and not left:
        bench.refusals += len(asks)
        held("(i) refused before any write", "teams/ghost template-unknown; --compose flag-retired naming --document; "
             "git/inconnu, plans/shared (requires plan) and nosuch/x document-unknown; --teams the usage; no "
             "teams/ghost-* left")
    else:
        failures.append(f"  ✗ (i) refused                {wrong} left={left}")

    # --- (j) the document rendered ------------------------------------------------------------------
    started = o.call("team", "start", "demo", "--message", "go", "--no-tick", now="07:50")
    first = next(iter(T.by_kind(o.events("demo"), "team-started")), {})
    copy = directory / "TEAM-demo-par-lot.md"
    head = (directory / "TEAM-demo.md").read_text(encoding="utf-8") if (directory / "TEAM-demo.md").is_file() else ""
    serve = re.search(r"^serve: \|\n((?:  .*\n)+)", head, re.M)
    served = serve.group(1).split() if serve else []
    rendered = copy.read_text(encoding="utf-8") if copy.is_file() else ""
    if (started.returncode == 0 and first.get("root") == "supervisor"
            and rendered.strip() == body_of(HOUSE["git/par-lot.md"]) and not rendered.startswith("---")
            and "TEAM-demo-par-lot.md" in served and "TEAM.md" in served
            and first.get("documents") == [{"document": "TEAM-demo-par-lot.md", "template": "git/par-lot",
                                            "origin": "house", "roles": []}]
            and (directory / "TEAM.md").read_text(encoding="utf-8") == declared):
        held("(j) the document rendered", "demo starts: TEAM-demo-par-lot.md rendered, the body of par-lot.md, served "
             "by the head beside TEAM.md; team-started.documents git/par-lot; TEAM.md at its bytes")
    else:
        failures.append(f"  ✗ (j) rendered              rc={started.returncode} served={served} rendered={rendered!r} "
                        f"documents={first.get('documents')} {started.stderr.strip()[-160:]!r}")

    # --- (k) a birth without a preset ---------------------------------------------------------------
    played = o.call("team", "declare", "ghost-7", "--document", "all git/par-lot")
    written = o.call("team", "declare", "loose", "--document", "all git/par-lot", "--member", "a", "agents/k/a",
                     "--root", "a")
    loose = o.teams / "loose" / "TEAM.md"
    text = loose.read_text(encoding="utf-8") if loose.is_file() else ""
    if (played.returncode == 2 and code_of(played) == "team-invalid"
            and not (o.teams / "ghost-7").exists() and written.returncode == 0
            and text == "---\ndocuments: |\n  all git/par-lot\nagents: |\n  a agents/k/a\nroot: a\n---\n"
            and (S.declaration_of(o, "loose").get("verdict") or {}).get("ok") is True):
        bench.refusals += 1
        held("(k) a birth without a preset", "no --template: without a member team-invalid, no teams/ghost-7; with "
             "--member a --root a: TEAM.md written without template:, judged ok")
    else:
        failures.append(f"  ✗ (k) without a preset       rc={played.returncode}/{written.returncode} text={text!r} "
                        f"{(played.stderr or written.stderr).strip()[-200:]!r}")

    # --- (m) a preset is never a line of documents: ------------------------------------------------------------
    laid(shelf, S.SHELF)
    played = o.call("team", "declare", "ghost-8", "--template", "teams/solo", "--document", "all seasons/house-flow")
    if (played.returncode == 2 and code_of(played) == "document-unknown" and "template:" in played.stderr
            and not (o.teams / "ghost-8").exists()):
        bench.refusals += 1
        held("(m) a preset is never a line of documents:", "--document 'all seasons/house-flow': document-unknown "
             "naming template:, no teams/ghost-8")
    else:
        failures.append(f"  ✗ (m) no preset as a document rc={played.returncode} {played.stderr.strip()[-200:]!r}")
    return 0
