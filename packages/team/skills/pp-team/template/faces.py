"""The `template` domain, layer `faces`: how a template and its values are put into words.

A definition belongs here when it turns values into the text a member or a user reads -- the intention a template gives
a team -- and gives that text back without printing it. A list of names quoted, which a refusal of a rule writes, and a
value as `SEASON.md`'s front matter reads it back, which a rule writes into the file, are rules (`quoted`,
`season_said`, `template/rules.py`).
"""
from __future__ import annotations

import re

from template.rules import holes_filled


def intention_rendered(template: dict, team: dict, values: dict[str, str], daily: bool) -> str:
    """-> the intention a team preset makes of a team (`formed`'s): its body, each hole filled by the one filling
    (`holes_filled`) -- the values applied, then the values built in a team preset (`{root}`, `{others}`,
    `{chain}`, `{last}`, `{squads}`, `{workers}`, `{tree}`, `{quorum}`, `{count}`), which win name by name, and
    `{daily}`, the template's `daily-intention` when the daily stands (`daily`), nothing otherwise; a paragraph left
    empty closes up. DECLINES `value-undeclared` citing the template."""
    where = template.path or f"template `{template.template}`"
    holes = {**values, **team.holes, "daily": ""}
    holes["daily"] = holes_filled(template.daily_intention, holes, where).strip() if daily else ""
    return re.sub(r"\n{3,}", "\n\n", holes_filled(template.intention, holes, where)).strip()
