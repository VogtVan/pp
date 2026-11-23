"""_team_form_view -- what `ui-team-form-view` and `ui-team-form-view-left` share (rule 10): the bench's `pp-team`
witness on `core-review`, its SEASON.md on the preset `seasons/files` -- a line of documents whose key is a hole,
`{readers}` --, its role `readers` held by `reviewer`, its TEAM.md's body after a blank line; `declared.views` says
what each member reads, the candidate adds the line typed for every member."""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P

ROLE_DOC = "roles/TEAM-core-review-read-files.md"
VIEWS = [{"member": "lead", "roles": [], "documents": [T.document("TEAM-core-review-trunk.md", "served")]},
         {"member": "reviewer", "roles": ["readers"],
          "documents": [T.document("TEAM-core-review-trunk.md", "served"),
                        T.document(ROLE_DOC, "mounted", ("readers",))]}]
LINE_DOC = "TEAM-core-review-branches.md"        # what the candidate gives every member: the line typed
CANDIDATE_VIEWS = [{**one, "documents": one["documents"] + [T.document(LINE_DOC, "served")]} for one in VIEWS]
FACE = T.declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer")], {"budget": 1.0},
                     template="teams/supervisor-workers", roles=(("readers", ["reviewer"]),), season=T.CORE_SEASON,
                     documents=(("all", ["git/trunk"]),), views=VIEWS,
                     season_file={"template": "seasons/files", "values": [("readers", "readers")]},
                     body="\nThe owner's word.\n")
CANDIDATE = {**FACE, "declared": {**FACE["declared"], "views": CANDIDATE_VIEWS}}
REFUSAL = "pp-team: role-unknown -- teams/core-review/SEASON.md: documents: `writers` is no role.\n"
LINE = "all git/trunk git/branches"     # `all`, a key the preset gives: its line keeps the preset's git/trunk
# the list of the season, its Documents: the preset's line `all git/trunk`, locked, its separator, then git/branches --
# `all` ticked on it makes LINE; ticked off, the text is the file again
TICK = f"{F.TO_SEASON_DOCUMENTS},down,down,enter,{F.ALL},ctrl+enter"
UNTICKED = f"{F.TO_SEASON_DOCUMENTS},down,down,enter,down,space,space,ctrl+enter"     # `all` ticked, then unticked
TO_VIEW = F.section(2)                 # from Documents: Members, whose side pane shows the view by member
ASKED = "declaration core-review --text-file"   # how the witness's journal says a view asked of a text


def script(**extra) -> dict:
    """-> the witness on `core-review`'s face, the candidate's view or `extra` (`candidate_refusal`)."""
    return T.script(declarations={**T.DECLARATIONS, "core-review": FACE},
                    **(extra or {"candidates": {"core-review": CANDIDATE}}))


def constant(name: str) -> str:
    try:
        return P.palette_constant(name)
    except KeyError:
        return f"<no {name}>"


def asked(house) -> list[str]:
    """-> the views asked of a text since the journal was last cleared."""
    return [one for one in house.journal_lines() if one.startswith(ASKED)]


def member(view: list[str], name: str) -> str:
    """-> what the view says of `name`: its row and the rows that follow it, up to the next member's."""
    found, said = [], False
    for row in view:
        head = row.split(":")[0].split()[:1]
        if head and head[0] in ("lead", "reviewer"):
            said = head[0] == name
        if said:
            found.append(row)
    return " ".join(found)


def opening(view: list[str]) -> bool:
    """-> whether the view is the one `declared.views` says: the role's document to `reviewer` alone, no line typed."""
    return (ROLE_DOC in member(view, "reviewer") and ROLE_DOC not in member(view, "lead")
            and LINE_DOC not in " ".join(view))
