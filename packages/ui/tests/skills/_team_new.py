"""_team_new -- what the scenarios of `N`, a team written from the post's form of TEAM.md, share (rule 10): the form's
size, the keys that reach its fields, the commands it plays, the reader of a field's help; the house is `_teams`' --
the bench's `pp-team` witness replaying `team templates --json` as team 1.26.0 says it: its documents, the presets of a
season, then the presets of a team, `teams/supervisor-workers` the first, declaring two values."""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")   # the readers of a form by its zones, the keys that type
T, P = F.T, F.P

SIZE = F.SIZE
FIRST, LEAD = T.PRESETS[0], T.PRESETS[1]      # the first preset of a team the face says, then the second


def typed(text: str) -> str:
    """-> the keys that type `text`."""
    return F.typed(text)


def keys(*parts: str) -> str:
    return ",".join(one for one in parts if one)


# `N` opens on the name, in the section Team: then the description, then the roles; the other sections by
# `ctrl+pagedown`, each focused on its first field -- Preset on the preset, Members on the members, then the root
TO_ROLES = "tab,tab"
TO_PRESET, TO_MEMBERS = F.team_to("Preset"), F.team_to("Members")
TO_DOCUMENTS, TO_LIMITS = F.team_to("Documents"), F.team_to("Limits")
NAMED = "N," + typed("ram")
BORN = "--schedule 30s --json"          # what a team born writes last: its schedule, 30s unless typed
DECLARED = f"team declare ram --template {FIRST['template']} {BORN}"


def born(name: str):
    """-> what `team declaration <name> --json` says once `N` wrote the team from the first preset: its members at
    `agents/<name>/<member>`, never started."""
    return T.declaration(name, [(one, f"agents/{name}/{one}") for one in FIRST["members"]], FIRST["limits"],
                         started=False, template=FIRST["template"])


def help_under(rows: list[str], name: str) -> str:
    """-> the help a form shows under the field `name`: the rows after its box, up to the next title or blank."""
    at = next((n for n, row in enumerate(rows) if row == P.field_title(name)), None)
    if at is None:
        return ""
    close = next((n for n in range(at, len(rows)) if rows[n].startswith("└")), None)
    if close is None:
        return ""
    found = []
    for row in rows[close + 1:]:
        if not row or row.startswith("[") or row == P.field_title(row.lower()) and row[:1].isupper():
            break
        found.append(row)
    return " ".join(found)
