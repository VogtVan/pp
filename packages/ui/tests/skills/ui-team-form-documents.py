"""Scenario `ui-team-form-documents` -- the section Documents of the team's form is the list of every document
(batch la-liste-des-documents), on the bench's `pp-team` witness (`_documents`):
- `E`, Documents: the house's documents first, then the package's under the separator `product · read only`, each
  with its roles (`—` for none); the line naming the team's own file `notes.md` kept in a last group; the key `all`
  written on two lines, each document of both said `all` (todo la-cle-sur-deux-lignes); the document
  under the cursor shows its holes (one field per value it declares) and its text -- no value yet, its source, the
  hole said `{tag}`
- `enter` on a document's role ticks roles: `all` and `readers` on `notes/style`, `all` taken off `review/read-files`;
  the form written plays the lines of `documents:` they make, the two lines of `all` one line that keeps
  `notes.md` -- nothing written before
The holes of a document typed: `ui-team-form-documents-holes` (cut by case, rule 10).
"""
from __future__ import annotations

from tests.harness import support

D = support(__file__, "documents")
F, T, P = D.F, D.T, D.P

OPEN = f"E,{D.TO_DOCUMENTS}"
TICKED = ",".join([OPEN, "down,enter", D.ALL, "down,space", "ctrl+enter",    # notes/style: all, then readers under it
                   "down,down,down,enter", D.ALL, "ctrl+enter", D.WRITE])      # review/read-files: all taken off
WRITTEN = ("team declare core-review --document 'all notes.md notes/style' "
           "--document 'readers notes/release notes/style' --json")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-documents", D.script())

    # --- the list, its groups, the panes of the document under the cursor -------------------------------------------
    shown = house.render("--render", "teams", *D.SIZE, "--press", f"{OPEN},{D.PAUSE},boxes")
    rows = D.rows(shown.stdout)
    firsts = [one[0] for one in rows]
    wanted = ["notes/release", "notes/style", "── product · read only ──", "review/read-commits", "review/read-files",
              "── kept as written ──", "notes.md"]
    holes, text = F.zone_rows(shown.stdout, "form-holes"), " ".join(F.zone_rows(shown.stdout, "form-doc"))
    if (shown.returncode == 0 and firsts == wanted and D.role_of(shown.stdout, "notes/release") == "readers"
            and D.role_of(shown.stdout, "notes/style") == "—" and D.role_of(shown.stdout, "review/read-files") == "all"
            and D.role_of(shown.stdout, "notes.md") == "all" and "Tag" in holes
            and D.SAID["notes/release"] in text and house.gestures() == []):
        held("the list of every document, the panes of the first", f"{firsts}; holes {holes[:3]}; text {text[:50]!r}")
    else:
        failures.append(f"  ✗ list                        rc={shown.returncode} {rows} {holes} {text!r} "
                        f"{shown.stdout[-2500:]!r} {shown.stderr[-400:]!r}")

    # --- roles ticked, the lines of documents written, the team's own file kept ------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *D.SIZE, "--press", TICKED)
    if house.gestures() == [WRITTEN]:
        held("roles ticked write their lines, notes.md kept", WRITTEN)
    else:
        failures.append(f"  ✗ roles                       {house.gestures()}")

    return 0
