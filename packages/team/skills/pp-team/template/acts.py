"""The `template` domain, layer `acts`: the templates listed and read, a preset and a document made of them.

A definition belongs here when it chains a store's reading and a rule's judgement for a verb or another act, reading
and judging in the order the work has always had, so a refusal comes at the same rank: the templates the house sees,
each read then judged (`templates_of`); the preset a name chooses, judged whole as a `Template` (`template_of`); a
document's text read, then its holes filled (`document_rendered`). Only verbs and other acts call it; no store, face
or rule does, and it imports no act of another domain. It may use the lower layers of any domain.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from house.model import Declined
from house.rules import body_of
from house.store import refuse
from template.model import Template
from template.rules import document_filled, template_judged, template_named, template_seen, templates_pinned
from template.store import pins_of, template_front, template_text, templates_listed


def templates_of(root: Path, conductor) -> dict[str, dict]:
    """-> every template the house SEES, by its name `<directory>/<name>`: each `<directory>/<name>.md` under
    `<house>/.pp/teams/templates/` first, then under the package's `templates/`, nothing else -- a name of the house
    replacing the package's. A template is a PRESET when its front matter carries one of `PRESET_KEYS` (the
    `documents:` it gives, a team's `form:` or `members:`), a DOCUMENT otherwise; a preset's `nature` is `team` when it
    carries one of `TEAM_KEYS`, `season` otherwise; one whose `requires:` names a package the house does not pin is not
    seen. Each `{template, kind, nature, origin, path, front, description, requires, error}`,
    sorted by name -- `error` the refusal a template whose front matter the engine cannot read gives where it is named
    (`template-invalid`), None otherwise. REFUSES `template-invalid`, citing the file: a directory or a name that is no
    slug."""
    found: dict[str, dict] = {}
    for origin, path in templates_listed(root):
        name = f"{path.parent.name}/{path.stem}"
        if name in found:
            continue
        try:
            template_named(conductor, path, name)
        except Declined as declining:
            refuse(str(declining))
        front, refusal = template_front(conductor, path)
        found[name] = template_seen(name, origin, path, front, refusal)
    return templates_pinned(found, pins_of(conductor, root))


def template_of(conductor, templates: dict[str, dict], template: str, where, nature: str | None = None) -> Template:
    """-> the PRESET `template` names as its file says it: its description, the values it declares (`values: |`,
    `values_declared`), the lines of its `documents:` (`documents_declared`) and, for a team, its form, its default
    members, its root and edges (what a preset without `form:` writes as they stand), the paragraph the intention
    gains with the daily, its limits, `schedule`, its role keys (`roles: |`, `<key> <place>...` per line, each place
    one its form has (`PLACES`) written as a hole, `{root}`: filled by the members the form puts there and written
    into a team's `TEAM.md` at its birth, never read for the team after it) and its intention. DECLINES, citing
    `where`: `template-unknown` for a
    name no preset the house sees carries, or one of another `nature` than the one asked (`team` for `TEAM.md`,
    `season` for `SEASON.md`); `template-invalid` for a front matter the engine cannot read, a `form:` no
    form, a `values:` or `documents:` line of another form, a `roles:` line that names anything but places its form
    has, or a `daily:` or `squads:` key: each is a value the preset declares."""
    judged = template_judged(conductor, templates, template, where, nature)
    return replace(judged, intention=body_of(template_text(judged.path)))


def document_rendered(conductor, path: Path, values: dict[str, str], headed: bool = False) -> str:
    """-> the document a template makes: its body under its CONDUCTED head (`conducted_head`: every key but the
    template's own, at its bytes), the holes of both filled (`holes_filled`). `headed`: the document opens on a front
    matter even when no key is left -- an empty one: a document of a role is mounted, and the engine mounts no
    document without one. DECLINES `value-undeclared`."""
    return document_filled(conductor, template_text(path), path, values, headed)
