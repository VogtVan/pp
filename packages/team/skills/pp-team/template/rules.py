"""The `template` domain, layer `rules`: what a template becomes once its values are given, and what it is worth.

A definition belongs here when it computes its answer from its arguments alone: the members a form lays out, given as a
`Shape`, the values a template declares checked and applied, the holes of a text filled, a number read from a flag, the
lines of a `documents:` key, what a values file that names no template and no document declares, the head a document is
conducted by, the values a template or a values file declares, the values written into a front matter, the value a key
stands at in a text. It also JUDGES what a store read: a template's name, a template seen with its front matter, the
templates the house pins, a preset as its file says it, given as a `Template`, a document's text filled, the places of a
document -- the package's templates given as an argument --, a new document, the values of a dry render and the name the
render keeps; a list of names quoted (`quoted`), which its refusals write; and a value as `SEASON.md`'s front matter
reads it back (`season_said`). A judgement that fails DECLINES with the text the refusal prints, and its caller refuses
-- `numbered` too, whose decline `declare_verb` refuses. It reads no disk, no clock and no environment and prints
nothing: what needs the system belongs to `store`. It may call the engine it is given for reading a text alone -- a
name's form, a section, a front matter, a document made of a text -- and nothing else of it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from house.model import BORDER, Declined, decline
from house.rules import block, body_of
from template.model import (ALL, BUILT_IN, FORM_NAMES, HOLE, PLACES, PRESET_KEYS, SQUADS, TEAM_KEYS, TEMPLATE_KEYS,
                            TEMPLATES_PLACE, Shape, Template)


def edges_members(preset: dict) -> list[str]:
    """-> the members a team preset without `members:` names by its `root:` and its `reports:` -- the root first, then
    each member of an edge in its order, each once: what `team templates` shows of its team."""
    named = [str(preset.root)] if preset.root else []
    for edge in preset.reports:
        sources, _, target = edge.partition("->")
        named += [*sources.split(), *target.split()]
    return list(dict.fromkeys(named))


def daily_of(form: str | None, values: dict[str, str], chiefs: list[str], head: str) -> str | None:
    """-> the daily's line under a wide form (`star`, `tree`): the value `daily` its rhythm, the `chiefs` -- the
    members who report to the root `head` -- its participants, the root its facilitator; None for another form, an
    empty rhythm, or fewer than two chiefs."""
    rhythm = values.get("daily") or ""
    return (f"daily {rhythm} with {' '.join(chiefs)} -> {head}"
            if form in ("star", "tree") and rhythm and len(chiefs) >= 2 else None)


def formed(template: dict, members: list[str], root: str | None, values: dict[str, str]) -> Shape:
    """-> the team a template's FORM makes of its members, in their order, under the `values` applied (`{name:
    value}`): `star` -- the root (the first, or `root` moved to the head) and every other member reporting to it,
    the daily when two of them or more report to it; `chain` -- each member reporting to the one before it,
    the first the root; `one` -- a single member, the root; `tree` -- the root, then `squads` squad
    leads reporting to it (the value `squads`, a whole number of 1 or more, else SQUADS), then the workers, given to
    the squad leads in turn and reporting to theirs, the daily of the squad leads when they are two or
    more. The daily's rhythm is the value `daily`: empty, or not declared, no daily. A template without `form:`
    says its own `reports:` as they stand, its root `root`, else its
    `root:`, else the first member, no daily. A form given members it cannot hold DECLINES `team-invalid`;
    a root nobody declared is said as asked, for the judge to refuse. `holes` are the values built in a team preset,
    which the form makes of the members: what the intention names them by (`intention_rendered`); `places` the same
    places as lists of members (`PLACES` says those each form has): what a preset's role keys name (`preset_roles`)."""
    form, name = template.form, template.template
    if form is None:
        root = root or (str(template.root) if template.root else None)
    if form == "one" and len(members) != 1:
        decline(f"team-invalid -- template `{name}` holds one member: {len(members)} given.")
    if form not in ("one", None) and len(members) < 2:
        decline(f"team-invalid -- template `{name}` holds two members or more: {len(members)} given.")
    squads = values.get("squads") if form == "tree" else None
    if squads is not None and (not squads.isdigit() or int(squads) < 1):
        decline(f"team-invalid -- template `{name}`: `squads = {squads}` -- a whole number of 1 or more.")
    leads = SQUADS if squads is None else int(squads)
    if form == "tree" and len(members) < 1 + 2 * leads:
        decline(f"team-invalid -- template `{name}` with {leads} squad lead(s) holds {1 + 2 * leads} members or "
                f"more -- the root, the squad leads, one worker each at least: {len(members)} given.")
    order = ([root] + [one for one in members if one != root]) if root in members else list(members)
    head = root or order[0]
    others = [one for one in order if one != head]
    chiefs, workers = (others[:leads], others[leads:]) if form == "tree" else (others, [])
    crews = {chief: workers[at::leads] for at, chief in enumerate(chiefs)} if form == "tree" else {}
    if form in ("star", "tree"):
        reports = ([f"{' '.join(chiefs)} -> {head}"] if chiefs else []) + [
            f"{' '.join(crew)} -> {chief}" for chief, crew in crews.items()]
    elif form == "chain":
        reports = [f"{order[at]} -> {order[at - 1]}" for at in range(1, len(order))]
    elif form is None:
        reports = list(template.reports)
    else:
        reports = []
    daily = daily_of(form, values, chiefs, head)
    holes = {"root": f"`{head}`", "others": quoted(others) if others else "",
             "chain": " -> ".join(f"`{one}`" for one in order), "last": f"`{order[-1]}`",
             "squads": quoted(chiefs) if chiefs else "", "workers": quoted(workers) if workers else "",
             "tree": "; ".join(f"`{chief}` with {quoted(crew)}" for chief, crew in crews.items()),
             "quorum": str(max(1, len(others) - 1)), "count": str(len(others))}
    places = {"root": [head], "others": others, "squads": chiefs, "workers": workers, "last": [order[-1]]}
    return Shape(members=order, root=head, reports=reports, ceremony=daily, holes=holes, places=places)


def numbered(flag: str, value: str, whole: bool):
    """-> a limit given on the command line as the number it says -- DECLINES `team-invalid` naming the flag
    otherwise; the judge then bounds it as it bounds `TEAM.md`'s."""
    try:
        return int(value) if whole or value.isdigit() else float(value)
    except ValueError:
        decline(f"team-invalid -- `--{flag} {value}`: a {'whole number' if whole else 'number'}.")


def holes_filled(text: str, values: dict[str, str], where) -> str:
    """-> `text` with each hole `{<name>}` replaced by its value and `{{`, `}}` one brace each -- the ONE filling of the
    product: a team preset's intention (`intention_rendered`), a document (`document_rendered`) and a key of a line. A
    placeholder `<name>` the member fills in is never read. A hole no value names DECLINES `value-undeclared`, citing
    `where`."""
    def one(found: re.Match) -> str:
        if found.group(1) is None:
            return found.group(0)[0]
        if found.group(1) not in values:
            decline(f"value-undeclared -- {where}: `{found.group(0)}` -- no template declares `{found.group(1)}` "
                    "(`values:`); a brace of the text itself is written twice, `{{` or `}}`.")
        return values[found.group(1)]
    return HOLE.sub(one, text)


def values_applied(declared: list[dict], given: dict[str, str], path: Path, whose: str, source: str) -> list[dict]:
    """-> the values a values file APPLIES to what its template declares (`values_declared`'s, in their order):
    `[{name, value, from}]`, `from` the `source` (`season`, `team`) for a value given, `default` otherwise -- the ONE
    judge of them. DECLINES `value-unknown` for a value given that `whose` template does not declare,
    `value-missing` for a value without a default that is not given."""
    names = [one["name"] for one in declared]
    for named in given:
        if named not in names:
            decline(f"value-unknown -- {path}: values: `{named}` -- {whose} declares "
                    f"{', '.join(f'`{one}`' for one in names) or 'no value'} (`team templates`).")
    values = []
    for one in declared:
        if one["name"] in given:
            values.append({"name": one["name"], "value": given[one["name"]], "from": source})
        elif one["default"] is not None:
            values.append({"name": one["name"], "value": one["default"], "from": "default"})
        else:
            decline(f"value-missing -- {path}: `{one['name']}` ({one['description']}) has no default -- give it under "
                    "`values:`, `<name> = <value>`.")
    return values


def row_named(key: str, row: str) -> str | None:
    """-> the name of a line of the block `key`, by which `values_written` reaches it: an edge of `reports:`,
    `<member>... -> <target>`, by its target -- an edge has no key --; any other line by its first word, up to an
    `=`; None for a blank line."""
    if key == "reports":
        sources, arrow, target = row.partition("->")
        return target.strip() if arrow and target.strip() else None
    return row.split()[0].partition("=")[0] if row.split() else None


def documents_declared(conductor, front: dict, path: Path, code: str) -> list[tuple[str, list[str]]]:
    """-> the lines of a `documents: |` block, one per key, `<key> <document> ...`, in their order: `(key, documents)`
    -- the key `all`, a role key or a hole `{<name>}` the values fill (a hole by its name: `{{` and `}}` are none); a
    document `<directory>/<name>`, a template the house sees, or `<name>`, a file `<name>.md` of the team's directory.
    DECLINES `code` citing `path` for a line of another form: a key said twice, a key without a document, a document
    twice on its line, a word no such name."""
    found: list[tuple[str, list[str]]] = []
    slug = conductor.instance.valid_slug
    for line in block(front, "documents"):
        key, *documents = line.split()
        if (not documents or any(key == one for one, _ in found) or len(set(documents)) != len(documents)
                or not (key == ALL or slug(key) or ((hole := HOLE.fullmatch(key)) is not None and hole.group(1)))
                or any(not all(slug(part) for part in one.split("/")) or one.count("/") > 1 for one in documents)):
            decline(f"{code} -- {path}: documents: `{line}` -- one line per key, `<key>|{ALL} <document> ...`, the key "
                    "once, each document `<directory>/<name>` or `<name>` once on its line.")
        found.append((key, documents))
    return found


def documents_none(path: Path) -> dict:
    """-> what `documents_of` says of a values file that names no preset and no document."""
    return {"path": path, "template": None, "lines": [], "documents": {}, "declared": [], "given": {}}


def conducted_head(conductor, text: str) -> str:
    """-> the front matter of a template without the template's own keys (`TEMPLATE_KEYS`), cut by the engine's
    spans (`sections.front_span`, `key_span`) -- each other key at its bytes, in its order; "" when none is left."""
    lines = text.splitlines()
    try:
        start, end = conductor.sections.front_span(lines)
    except conductor.Refusal:
        return ""
    spans = [span for key in TEMPLATE_KEYS if (span := conductor.sections.key_span(lines, start, end, key))]
    for first, last in sorted(spans, reverse=True):
        del lines[first:last]
        end -= last - first
    kept = lines[start:end]
    return f"{BORDER}\n" + "\n".join(kept) + f"\n{BORDER}\n" if any(one.strip() for one in kept) else ""


def values_declared(conductor, front: dict, path: Path) -> list[dict]:
    """-> the values a template declares under `values: |`, one line each `<name> [= <default>] -- <description>`, in
    their order: `{name, description, default}`, `default` None without `=`. DECLINES `template-invalid` citing the
    template for a line of another form, a name no slug, a name said twice, or `team` -- the value built in."""
    found: list[dict] = []
    for line in block(front, "values"):
        said, cut, description = line.partition(" -- ")
        named, equal, default = said.partition("=")
        named = named.strip()
        if (not cut or not description.strip() or not conductor.instance.valid_slug(named) or named == BUILT_IN
                or any(one["name"] == named for one in found) or (equal and not default.strip())):
            decline(f"template-invalid -- {path}: values: `{line}` -- one line per value, `<name> [= <default>] -- "
                    f"<description>`, its name a slug said once, `{BUILT_IN}` built in.")
        found.append({"name": named, "description": description.strip(),
                      "default": default.strip() if equal else None})
    return found


def values_given(conductor, front: dict, path: Path, code: str) -> dict[str, str]:
    """-> the values a values file GIVES under `values: |`, one line each `<name> = <value>`, the value empty or not:
    `{name: value}` in their order -- the ONE reader of them, `SEASON.md`'s and `TEAM.md`'s. DECLINES `code`
    (`season-invalid`, `team-invalid`) for a line of another form, a name no slug or said twice."""
    given: dict[str, str] = {}
    for line in block(front, "values"):
        named, equal, value = line.partition("=")
        named = named.strip()
        if not equal or not conductor.instance.valid_slug(named) or named in given:
            decline(f"{code} -- {path}: values: `{line}` -- one line per value, `<name> = <value>`, each once.")
        given[named] = value.strip()
    return given


def values_written(conductor, text: str, changes: list[tuple], body: str | None = None) -> str:
    """-> the text of a VALUES FILE -- `TEAM.md`, `SEASON.md` -- with the keys `changes` name written: the ONE writer
    of a key of one, `declare`'s and `start`'s (the flags of a season). Every other key, line and token of the front
    matter and the body stay at their bytes; a line written takes the file's own line ending; a text without a front
    matter gains one before it. `changes`, in the order new keys are laid, each `(key, change)`:
    - a text: the line `<key>: <text>`, in the key's place when it stands, at the end of the front matter otherwise;
    - None: the key taken out, its block with it;
    - a list of `(word, form)`: the lines of the block `<key>: |`, each named by `row_named`. `form` receives the
      first line named `word` (None when no line has that name) and returns the line to write: it takes the place of
      ALL the lines named `word`, or is added after the block's last line when none stood; None takes all of them
      out. `word` None adds a line whatever stands; a block left without a line leaves with its key.
    `body`: the text after the front matter, replaced whole. A front matter that never closes raises the engine's
    `Refusal`."""
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != BORDER:        # no front matter: one is laid before the text
        lines = [f"{BORDER}{eol}", f"{BORDER}{eol}", *lines]
    start, end = conductor.sections.front_span([one.rstrip("\r\n") for one in lines])

    def placed_at(key: str, new: list[str]) -> None:
        nonlocal end
        found = conductor.sections.key_span([one.rstrip("\r\n") for one in lines], start, end, key)
        first, last = (end, end) if found is None else found
        lines[first:last] = new
        end += len(new) - (last - first)

    for key, change in changes:
        if change is None or isinstance(change, str):
            placed_at(key, [] if change is None else [f"{key}: {change}{eol}"])
            continue
        found = conductor.sections.key_span([one.rstrip("\r\n") for one in lines], start, end, key)
        head, rows = f"{key}: |{eol}", []
        if found is not None:
            said = lines[found[0]].rstrip("\r\n").split(":", 1)[1].strip()
            head = lines[found[0]] if said == "|" else head
            rows = lines[found[0] + 1:found[1]] if said in ("|", "") else [f"  {said}{eol}"]
        for word, form in change:
            named = [] if word is None else [rank for rank, row in enumerate(rows) if row_named(key, row) == word]
            at = named[0] if named else None
            new = form(None if at is None else rows[at].strip())
            for rank in reversed(named if new is None else named[1:]):   # a key said on several lines: one, or none
                del rows[rank]
            if new is not None and at is None:
                last = max((rank for rank, row in enumerate(rows) if row.strip()), default=-1) + 1
                rows.insert(last, f"  {new}{eol}")
            elif new is not None and new != rows[at].strip():
                rows[at] = f"  {new}{eol}"
        placed_at(key, [head, *rows] if any(row.strip() for row in rows) else [])
    if body is not None:
        if not lines[end].endswith(("\n", "\r")):
            lines[end] += eol
        lines[end + 1:] = [body] if body else []
    return "".join(lines)


def key_stands(conductor, text: str | None, key: str) -> str | None:
    """-> what a values file says under `key`, at its bytes: the key's lines in its front matter, or, for `body`, the
    text after it -- None without the file, the key, or a body."""
    if not text:
        return None
    lines = text.splitlines(keepends=True)
    if lines[0].strip() != BORDER:                     # no front matter: the whole text is the body
        return text if key == "body" else None
    bare = [one.rstrip("\r\n") for one in lines]
    start, end = conductor.sections.front_span(bare)
    if key == "body":
        return "".join(lines[end + 1:]) or None
    found = conductor.sections.key_span(bare, start, end, key)
    return None if found is None else "".join(lines[found[0]:found[1]])


def template_named(conductor, path: Path, name: str) -> None:
    """DECLINES `template-invalid` citing the file `path` for a template whose `<directory>/<name>` is not two slugs."""
    if not (conductor.instance.valid_slug(path.parent.name) and conductor.instance.valid_slug(path.stem)):
        decline(f"template-invalid -- {path}: `{name}` -- a template is `<directory>/<name>.md`, each a slug.")


def template_seen(name: str, origin: str, path: Path, front: dict, refusal) -> dict:
    """-> a template as `templates_of` lists it, from its front matter (`front`, `template_front`'s): `{template,
    origin, path, front, kind, nature, description, requires, error}` -- `kind` `preset` when the front matter carries one of
    `PRESET_KEYS`, `document` otherwise; `nature` `team` when it carries one of `TEAM_KEYS`, `season` otherwise;
    `error` the refusal the template gives where it is named when the engine could not read it (`refusal`), None
    otherwise."""
    error = None if refusal is None else f"template-invalid -- {path}: {refusal}"
    needed = front.get("requires") or []
    needed = [str(one) for one in needed] if isinstance(needed, list) else re.split(r"[\s,]+", str(needed))
    return {"template": name, "origin": origin, "path": path, "front": front,
            "kind": "preset" if any(key in front for key in PRESET_KEYS) else "document",
            "nature": "team" if any(key in front for key in TEAM_KEYS) else "season",
            "description": str(front.get("description") or ""),
            "requires": [one for one in needed if one], "error": error}


def templates_pinned(found: dict[str, dict], pinned: set[str]) -> dict[str, dict]:
    """-> the templates `found` the house sees, sorted by name: each whose `requires:` names only packages the house
    pins (`pinned`)."""
    return {name: found[name] for name in sorted(found) if set(found[name]["requires"]) <= pinned}


def template_judged(conductor, templates: dict[str, dict], template: str, where, nature: str | None = None) -> Template:
    """-> the PRESET `template` names among `templates` (`templates_of`'s), judged and given as a `Template` whose
    `intention` is empty: `template_of` reads the file and gives it. DECLINES, citing `where`, `template-unknown` for a
    name no preset carries or one of another `nature`; citing the file, `template-invalid` for a front matter the
    engine could not read, a `form:` no form, a `daily:` or `squads:` key, a `roles:` line that names anything but
    places its form has, a `values:` or `documents:` line of another form."""
    found = templates.get(template)
    if found is not None and found["error"]:
        decline(found["error"])
    if found is None or found["kind"] != "preset" or nature not in (None, found["nature"]):
        presets = [name for name, one in templates.items()
                   if one["kind"] == "preset" and nature in (None, one["nature"])]
        decline(f"template-unknown -- {where}: `template: {template}` -- the presets are "
                f"{', '.join(presets) or 'none'} (`team templates`).")
    path, front = found["path"], found["front"]
    form = front.get("form")
    if form is not None and str(form) not in FORM_NAMES:
        decline(f"template-invalid -- {path}: `form: {form}` -- {', '.join(FORM_NAMES)}.")
    for key in ("daily", "squads"):
        if key in front:
            decline(f"template-invalid -- {path}: `{key}:` -- a template declares it as a value: `values: |`, "
                    f"`{key} = {front[key]} -- <description>`.")
    places = PLACES[None if form is None else str(form)]
    for line in block(front, "roles"):
        if any(not (one.startswith("{") and one.endswith("}") and one[1:-1] in places) for one in line.split()[1:]):
            decline(f"template-invalid -- {path}: roles: `{line}` -- a line names its key, then places of "
                    + (f"the form `{form}`" if form is not None else "a preset without `form:`") + ", which are "
                    + ", ".join(f"{{{one}}}" for one in places) + ".")
    return Template(template=template, origin=found["origin"], path=path,
                    values=values_declared(conductor, front, path),
                    documents=documents_declared(conductor, front, path, "template-invalid"),
                    description=found["description"], form=None if form is None else str(form),
                    team=bool(set(TEAM_KEYS) & set(front)),
                    members=block(front, "members"), root=front.get("root"), reports=block(front, "reports"),
                    roles=block(front, "roles"),
                    daily_intention=str(front.get("daily-intention") or ""),
                    limits={key: front[key] for key in ("budget", "launches", "timeout") if key in front},
                    schedule=front.get("schedule"),
                    intention="")


def document_filled(conductor, text: str, path: Path, values: dict[str, str], headed: bool = False) -> str:
    """-> the document the template `text` (the file at `path`) makes: its body under its CONDUCTED head
    (`conducted_head`), the holes of both filled (`holes_filled`); `headed`: an empty front matter when no key is left.
    DECLINES `value-undeclared`."""
    fronted = text.lstrip().startswith(BORDER)
    body = holes_filled(body_of(text) if fronted else text.strip(), values, path)
    head = holes_filled(conducted_head(conductor, text), values, path) if fronted else ""
    if headed and not head:
        head = f"{BORDER}\n{BORDER}\n"
    return head + (body + "\n" if body else "")


def document_places(root: Path, conductor, name: str, package: Path) -> tuple[Path, Path]:
    """-> (the house's file of the document `name`, the package's): `<house>/.pp/teams/templates/<directory>/<name>.md`
    and `<directory>/<name>.md` under `package`, the package's templates (`TEMPLATES`, given by `document_verb`),
    standing or not. DECLINES `template-invalid` for a name that is not `<directory>/<name>`, each a slug."""
    parts = name.split("/")
    if len(parts) != 2 or not all(conductor.instance.valid_slug(part) for part in parts):
        decline(f"template-invalid -- `{name}`: a document is named `<directory>/<name>`, each part a slug.")
    return root / TEMPLATES_PLACE / parts[0] / f"{parts[1]}.md", package / parts[0] / f"{parts[1]}.md"


def document_judged(conductor, name: str, text: str) -> None:
    """Judges the text `--body-file` hands over for the house's document `name`: a front matter the engine reads, no
    key of a preset (`PRESET_KEYS`), its `values:` of the form a template declares (`values_declared`). DECLINES
    `document-invalid`, naming what fails."""
    lines = text.splitlines()
    try:
        start, end = conductor.sections.front_span(lines)
        front = conductor.reading.front_matter(lines[start:end])
    except conductor.Refusal as refusal:
        decline(f"document-invalid -- {name}: {refusal} -- a document starts with its front matter, between two `---` "
                "lines.")
    preset = [key for key in PRESET_KEYS if key in front]
    if preset:
        decline(f"document-invalid -- {name}: `{preset[0]}:` is a key of a preset; a document has none of `documents`, "
                "`form` or `members`.")
    try:
        values_declared(conductor, front, Path(name))
    except Declined as declining:
        decline(f"document-invalid -- {name}: {str(declining).split(' -- ', 1)[-1]}")


def render_values(name: str, declared: list[dict], given: dict[str, str], defaults: dict[str, str],
                  withdrawn: set[str], asked: list[str]) -> list[dict]:
    """-> the values of a dry render of the document `name`, `[{name, value, from}]`, `team` first, then each value the
    document declares (`declared`): the one `--value` gives (`given`), else the team's (`defaults`) unless the call
    withdrew it (`withdrawn`), else the document's default. DECLINES `value-unknown` for a `--value` (`asked`) the
    document does not declare, `value-missing` for a value without one."""
    names = [BUILT_IN, *(one["name"] for one in declared)]
    for named in asked:
        if named not in names:
            decline(f"value-unknown -- `--value {named}`: {name} declares "
                    f"{', '.join(f'`{one}`' for one in names[1:]) or 'no value'} (`team templates`).")
    values = []
    for named, default in [(BUILT_IN, None), *((one["name"], one["default"]) for one in declared)]:
        if named in given:
            values.append({"name": named, "value": given[named], "from": "given"})
        elif named in defaults and named not in withdrawn:
            values.append({"name": named, "value": defaults[named], "from": "default"})
        elif default is not None:
            values.append({"name": named, "value": default, "from": "default"})
        elif named != BUILT_IN and named in withdrawn:
            decline(f"value-missing -- `--render {name}`: `{named}` has no default, and `--value {named}=` took "
                    f"its value away -- give it a value, `--value {named}=<value>`.")
        elif named != BUILT_IN:
            decline(f"value-missing -- `--render {name}`: `{named}` has no default -- give it, `--value "
                    f"{named}=<value>`, or name a team that gives it (`--team`).")
    return values


def render_named(name: str, values: list[dict], text: str, withdrawn: set[str]) -> None:
    """DECLINES `value-missing` for a dry render of the document `name` whose text (`text`) holds the hole `{team}`
    when no value names the team -- the call took it away (`withdrawn`), or no team and no `--value` gave it."""
    holes = {hole.group(1) for hole in HOLE.finditer(text) if hole.group(1)}
    if BUILT_IN in holes and not any(one["name"] == BUILT_IN for one in values) and BUILT_IN in withdrawn:
        decline(f"value-missing -- `--render {name}`: `{BUILT_IN}` -- the team's name, taken away by `--value "
                f"{BUILT_IN}=` -- give it, `--value {BUILT_IN}=<name>`.")
    if BUILT_IN in holes and not any(one["name"] == BUILT_IN for one in values):
        decline(f"value-missing -- `--render {name}`: `{BUILT_IN}` -- the team's name: `--team <team>` or "
                f"`--value {BUILT_IN}=<name>`.")


def quoted(names: list[str]) -> str:
    """-> names as the intention says them: `a`, `a` and `b`, `a`, `b` and `c`."""
    marked = [f"`{one}`" for one in names]
    return marked[0] if len(marked) == 1 else ", ".join(marked[:-1]) + " and " + marked[-1]


def season_said(value) -> str:
    """-> a value as SEASON.md's front matter reads it back: bare when the engine's reader reads it as that very string,
    a JSON string otherwise."""
    text = str(value)
    return text if re.fullmatch(r"[A-Za-z0-9_./@+-]+", text) and not re.fullmatch(r"[-+.0-9eE]+", text) \
        and text.lower() not in ("yes", "no", "on", "off", "true", "false", "null", "y", "n", "~") else json.dumps(text)
