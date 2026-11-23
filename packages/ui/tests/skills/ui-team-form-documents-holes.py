"""Scenario `ui-team-form-documents-holes` -- the holes of the document chosen in the list of documents (batch
la-liste-des-documents, cut from `ui-team-form-documents`), on the bench's `pp-team` witness (`_documents`):
- a value typed in the hole `tag` of `notes/release`: its text rendered anew after the pause on the typed TEAM.md
  (`templates --render notes/release --text-file`, `tag = 1.0` in it); `notes/style`, which declares `tag` too, shows
  the same value and its text rendered for it
- the form written plays `--value tag=1.0`: the hole's value is a line of `values:`
- Preset (batch les-volets-par-onglet), `core-review` naming no preset: no field -- `tag`, a document's value, is not
  listed there --, a line says no preset is chosen; the file in the side pane holds `tag = 1.0`
"""
from __future__ import annotations

from tests.harness import support

D = support(__file__, "documents")
F, T, P = D.F, D.T, D.P

OPEN = f"E,{D.TO_DOCUMENTS}"
TYPED = f"{OPEN},tab,1,full_stop,0"     # the hole `tag` of notes/release
VALUED = "team declare core-review --value tag=1.0 --json"
TO_PRESET = "ctrl+pageup,ctrl+pageup"   # from Documents: Preset


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-documents-holes", D.script())

    # --- a hole typed: the text rendered anew, the value shared by name, written to values: ---------------------------
    house.clear_journal()
    typed = house.render("--render", "teams", *D.SIZE, "--press", f"{TYPED},{D.PAUSE},shift+tab,down,{D.PAUSE},boxes")
    asked = D.renders(house)
    holes, text = F.zone_rows(typed.stdout, "form-holes"), " ".join(F.zone_rows(typed.stdout, "form-doc"))
    typed_for = lambda document: any(one.startswith(f"templates --render {document} --text-file") and "tag = 1.0" in one
                                     for one in asked)
    if typed_for("notes/release") and typed_for("notes/style") and "1.0" in holes and D.TAGGED in text:
        held("a hole typed: the text rendered anew, the value shared", f"{asked}; notes/style: {text[:40]!r}")
    else:
        failures.append(f"  ✗ hole                        {asked} {holes} {text!r} {typed.stdout[-2000:]!r}")
    house.clear_journal()
    house.render("--render", "teams", *D.SIZE, "--press", f"{TYPED},ctrl+enter")
    if house.gestures() == [VALUED]:
        held("the value of a hole written to values:", house.gestures()[0])
    else:
        failures.append(f"  ✗ value written               {house.gestures()}")

    # --- Preset without a preset: no field, a line says so; the hole's value in the file ----------------------------
    preset = house.render("--render", "teams", *D.SIZE, "--press", f"{TYPED},{TO_PRESET},boxes")
    rows, file = F.fields(preset.stdout), F.zone_rows(preset.stdout, "form-file")
    none = P.palette_constant("PRESET_NONE")
    if (preset.returncode == 0 and P.field_title("tag") not in rows and none in " ".join(rows)
            and "tag = 1.0" in file):
        held("Preset without a preset: no field, said; the document's value not listed", f"{none!r}; tag = 1.0 in the file")
    else:
        failures.append(f"  ✗ preset none                 rc={preset.returncode} {rows} {file} {preset.stderr[-300:]!r}")
    return 0
