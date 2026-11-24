"""Scenario `ui-team-form-documents-delete` -- a house's document deleted from the list of documents, and what the list
never changes (batch la-liste-des-documents), on the bench's `pp-team` witness (`_documents`):
- `d` on `notes/style`, given to nobody, its name typed: `team document notes/style --delete --json`; the list read
  again no longer holds it
- `d` on `notes/release`, given to `readers` in the form: nothing played, the line of state says to give it to nobody
  first
- the verb's refusal `document-used` (another team names it): said on the line of state with that team
- `e` and `d` on a document of the package: nothing played, the line of state says it is the product's, read only
"""
from __future__ import annotations

from tests.harness import support

D = support(__file__, "documents")
F, T, P = D.F, D.T, D.P

OPEN = f"E,{D.TO_DOCUMENTS}"
DELETE = f"{OPEN},down,d,{F.typed('notes/style')},ctrl+enter"
USED = "pp-team: document-used -- `notes/style`: teams/ops/TEAM.md names it under documents: all.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-documents-delete", D.script())

    house.clear_journal()
    gone = house.render("--render", "teams", *D.SIZE, "--press", f"{DELETE},boxes")
    if house.gestures() == ["team document notes/style --delete --json"] and D.role_of(gone.stdout, "notes/style") is None \
            and D.role_of(gone.stdout, "notes/release") == "readers":
        held("d deletes a document given to nobody", house.gestures()[0])
    else:
        failures.append(f"  ✗ delete                      {house.gestures()} {D.rows(gone.stdout)} {gone.stdout[-1500:]!r}")

    house.clear_journal()
    given = house.render("--render", "teams", *D.SIZE, "--press", f"{OPEN},d,boxes")
    if house.gestures() == [] and "readers" in F.state(given.stdout).split() and D.rows(given.stdout):
        held("d on a document a role holds plays nothing", F.state(given.stdout)[:80])
    else:
        failures.append(f"  ✗ held by a role              {house.gestures()} {F.state(given.stdout)!r}")

    house.use(D.script(answers={"document": {"rc": 2, "err": USED}}))
    house.clear_journal()
    used = house.render("--render", "teams", *D.SIZE, "--press", f"{DELETE},boxes")
    state = F.state(used.stdout)
    if (house.gestures() == ["team document notes/style --delete --json"] and "document-used" in state.split()
            and "teams/ops/TEAM.md" in state and D.role_of(used.stdout, "notes/style") == "—"):
        held("the verb's refusal said on the line of state", state[:80])
    else:
        failures.append(f"  ✗ refused                     {house.gestures()} {state!r} {used.stdout[-1500:]!r}")

    house.use(D.script())
    house.clear_journal()
    product = house.render("--render", "teams", *D.SIZE, "--press", f"{OPEN},down,down,down,e,d,boxes")
    if house.gestures() == [] and P.palette_constant("DOC_READ_ONLY") in F.state(product.stdout):
        held("a document of the package is read only", F.state(product.stdout)[:80])
    else:
        failures.append(f"  ✗ product                     {house.gestures()} {F.state(product.stdout)!r}")
    return 0
