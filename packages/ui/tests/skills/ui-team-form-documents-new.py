"""Scenario `ui-team-form-documents-new` -- a house's document created and its text changed from the list of
documents (batch la-liste-des-documents), on the bench's `pp-team` witness (`_documents`), the post writing no file:
- `n`, a name typed: `team document notes/new --new --json`; the list read again holds it, under the cursor, its
  source open for editing
- `e` opens the source of `notes/release`; a key typed, then back on the list, `e` writes it: `team document
  notes/release --body-file - --json`, the text typed on its input
- `e`, a key typed, `escape` (batch l-echap-qui-garde-la-saisie): the confirmation asked first;
  `ctrl+enter` there throws the source away, nothing played, the form still open; `escape` there gives the source
  back, the key still typed; a field of the form left for, `escape` asks again -- the source typed counts for the form
  (review #15797) --, `escape` there gives the form back, and `e` then writes the key typed
"""
from __future__ import annotations

from tests.harness import support

D = support(__file__, "documents")
F, T, P = D.F, D.T, D.P

OPEN = f"E,{D.TO_DOCUMENTS}"
BACK = "shift+tab,shift+tab"           # from the source: the hole `tag`, then the list
WRITTEN = "team document notes/release --body-file - --json"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-documents-new", D.script())

    # --- n: a house's document born, chosen, its source open -------------------------------------------------------
    house.clear_journal()
    made = house.render("--render", "teams", *D.SIZE, "--press", f"{OPEN},n,{F.typed('notes/new')},ctrl+enter,boxes")
    source = " ".join(F.zone_rows(made.stdout, "form-doc"))
    if (house.gestures() == ["team document notes/new --new --json"] and D.role_of(made.stdout, "notes/new") == "—"
            and "# notes/new" in source and house.journal_lines().count("templates --json") >= 2):
        held("n creates a house's document, its source open", f"{house.gestures()}; {source[:40]!r}")
    else:
        failures.append(f"  ✗ new                         {house.gestures()} {D.rows(made.stdout)} {source!r} "
                        f"{house.journal_lines()} {made.stdout[-2000:]!r} {made.stderr[-300:]!r}")

    # --- e: the source written by the verb ---------------------------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *D.SIZE, "--press", f"{OPEN},e,x,{BACK},e")
    said = D.bodies(house)
    if (house.gestures() == [WRITTEN] and said
            and said[0].startswith("x---") and D.SAID["notes/release"] in said[0]):
        held("e writes the source by the verb", f"{house.gestures()[0]}; body {said[0][:30]!r}")
    else:
        failures.append(f"  ✗ edit                        {house.gestures()} {said}")

    # --- escape: the source thrown away ------------------------------------------------------------------------------
    house.clear_journal()
    left = house.render("--render", "teams", *D.SIZE, "--press", f"{OPEN},e,x,escape,ctrl+enter,{D.PAUSE},boxes")
    text = " ".join(F.zone_rows(left.stdout, "form-doc"))
    if house.gestures() == [] and D.SAID["notes/release"] in text and "x---" not in text and D.rows(left.stdout):
        held("escape, then ctrl+enter, throws the source away", f"nothing played; {text[:40]!r}")
    else:
        failures.append(f"  ✗ escape                      {house.gestures()} {text!r} {left.stdout[-1500:]!r}")
    house.clear_journal()
    house.render("--render", "teams", *D.SIZE, "--press",
                 f"{OPEN},e,x,escape,escape,shift+tab,escape,escape,shift+tab,e")   # the source, then the hole `tag`
    said = D.bodies(house)
    if house.gestures() == [WRITTEN] and said and said[0].startswith("x---"):
        held("escape asks for a source typed, in it or in a field", f"{house.gestures()[0]}; body {said[0][:30]!r}")
    else:
        failures.append(f"  ✗ source back                 {house.gestures()} {said}")
    return 0
