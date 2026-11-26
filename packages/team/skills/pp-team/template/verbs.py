"""The `template` domain, layer `verbs`: the command line of the verbs that read and write the templates.

A definition belongs here when it serves the command line of such a verb: it reads the verb's flags, prints the
templates the house sees as lines or as JSON, creates, writes or deletes a document of the house, renders a document as
a start would write it and prints it without writing it, or refuses with the usage. `document` refuses what its two
rules decline, the places of a document and a new document, by the same text; the dry render judges its values, reads
the template's holes, then judges the name it keeps. A verb is where the skill meets its caller: it may print, end the
call and use every other layer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from house.model import Declined, USAGE, decline
from house.rules import team_doc, team_root
from house.store import machine_house, named_team, placed, refuse
from house.verbs import flags
from template.model import BUILT_IN, DOCUMENT_FLAGS, DOCUMENT_SKELETON, SEASON_DOC, TEMPLATES_FLAGS
from template.rules import (document_judged, document_places, edges_members, formed, render_named,
                            render_values, values_declared, values_given)
from template.faces import intention_rendered
from template.store import TEMPLATES, document_kind, document_users, template_text, text_handed
from template.acts import document_rendered, template_of, templates_of
from declaration.store import candidate_read
from declaration.acts import team_played
from season.store import season_front


def templates_verb(rest: list[str]) -> int:
    """`team templates [--json]`: every template the house sees (`templates_of`), one line each -- its name, its kind
    (`preset` or `document`), its origin, a team preset's default members, its description --, under it one line per
    value it declares and, for a preset, one per line of its `documents:`; under `--json` one object per template,
    `{template, kind, origin, description, values}` -- each value `{name, description, default}` --, `requires` when
    it names packages, a preset's `documents` (`[{key, documents}]`, the keys as written: a template knows no team)
    and, for a team preset, `{form, members, root, reports, ceremony, limits, intention}`, the team it makes for its
    default members, with `roles` (`[{role, places}]`, the places as written) when it has `roles:`. Nothing
    written; a template the engine cannot read, or a line of another form, gives its own line
    `{template, origin, refusal}` (`template-invalid`), the others listed. Read in the HOUSE (`machine_house()`),
    whatever instance calls. `--render` renders one document instead (`render_dry`)."""
    root, conductor = machine_house()
    asked = flags(rest, TEMPLATES_FLAGS)
    if asked["render"] is not None:
        return render_dry(root, conductor, asked)
    if asked["value"] or asked["team"] is not None or asked["season"] or asked["text-file"] is not None:
        refuse(USAGE)
    for name, one in templates_of(root, conductor).items():
        try:
            if one["error"]:
                decline(one["error"])
            said = {"template": name, "kind": one["kind"], "origin": one["origin"], "description": one["description"],
                    "values": values_declared(conductor, one["front"], one["path"])}
            if one["requires"]:
                said["requires"] = one["requires"]
            if one["kind"] == "preset":
                preset = template_of(conductor, {name: one}, name, one["path"])
                said["documents"] = [{"key": key, "documents": documents} for key, documents in preset.documents]
                if preset.team:
                    defaults = {value["name"]: value["default"] or "" for value in preset.values}
                    team = formed(preset, preset.members or edges_members(preset), None, defaults)
                    said.update({"form": preset.form, "members": team.members, "root": team.root,
                                 "reports": [{"from": edge.split("->")[0].split(), "to": edge.split("->")[1].strip()}
                                             for edge in team.reports],
                                 "ceremony": team.ceremony, "limits": preset.limits,
                                 "intention": intention_rendered(preset, team, defaults, bool(team.ceremony))})
                    if preset.roles:
                        said["roles"] = [{"role": line.split()[0], "places": line.split()[1:]}
                                         for line in preset.roles]
        except Declined as declining:
            said = {"template": name, "origin": one["origin"], "refusal": str(declining)}
        if asked["json"]:
            print(json.dumps(said, ensure_ascii=False))
            continue
        if "refusal" in said:
            print(f"{name}  refused · {one['origin']} -- {said['refusal']}")
            continue
        members = f"  {', '.join(said['members'])}" if "members" in said else ""
        print(f"{name}  {one['kind']} · {one['origin']}{members} -- {one['description']}")
        for value in said["values"]:
            default = f" = {value['default']}" if value["default"] is not None else ""
            print(f"    {value['name']}{default} -- {value['description']}")
        for line in said.get("documents") or []:
            print(f"    documents: {line['key']} {' '.join(line['documents'])}")
    return 0


def document_verb(rest: list[str]) -> int:
    """`team document <directory>/<name> [--new | --body-file <path>|- | --delete] [--json]`: the ONE writer of the
    house's documents, `<house>/.pp/teams/templates/<directory>/<name>.md`, as `declare` is the one writer of the
    values files. Without an action, the SOURCE of the document the house sees -- the house's file first, else the
    package's -- read, nothing written: its name, kind, origin and path, then its text whole; under `--json` ONE
    object `{template, origin, kind, path, text}`. `--new` writes the skeleton of a document (`DOCUMENT_SKELETON`),
    its directory born when needed; `--body-file` replaces the text of the house's document by the file's -- `-` by
    standard input's --, judged first (`document_judged`); `--delete` removes it, and its directory with its last
    document. Each writes the house's file alone: a team's file, a journal and the package are never touched, and a
    refusal writes nothing. Says what it did -- and the package's document of the same name, which the house's masks
    once created and shows again once deleted --; under `--json` ONE object `{template, done, path, package}`,
    `package` that document's path or null. REFUSES: `template-invalid` (a name that is not `<directory>/<name>`),
    `document-unknown` (no document of that name, or a preset to replace or delete), `document-exists` (`--new` on a
    name the house has), `document-preset` (`--new` on the name of a package's preset, which it would hide),
    `document-readonly` (a document the package alone carries, to replace or delete), `document-invalid` (a text
    `document_judged` refuses, or `--body-file` naming no file), `document-used` (a line of `documents:` names it,
    `document_users`, each said); two actions, or an action without its argument, are the usage. Read and written in
    the HOUSE (`machine_house()`), whatever instance calls."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    root, conductor = machine_house()
    name, asked = rest[0], flags(rest[1:], DOCUMENT_FLAGS)
    if sum(1 for action in ("new", "body-file", "delete") if asked[action] not in (None, False)) > 1:
        refuse(USAGE)
    try:
        own, packaged = document_places(root, conductor, name, TEMPLATES)
    except Declined as declining:
        refuse(str(declining))
    package = packaged if packaged.is_file() else None
    shown = (lambda path: str(path.relative_to(root.parent)) if path.is_relative_to(root.parent) else str(path))
    origin = "house" if own.is_file() else "package" if package is not None else None

    def said(done: str, path: Path, line: str) -> int:
        if asked["json"]:
            print(json.dumps({"template": name, "done": done, "path": shown(path),
                              "package": None if package is None else shown(package)}, ensure_ascii=False))
        else:
            print(f"pp-team: {name} {line}")
        return 0

    if asked["new"]:
        if own.is_file():
            refuse(f"document-exists -- {shown(own)}: the house already has `{name}` -- `team document {name}` prints "
                   "it, `--body-file` replaces its text.")
        if package is not None and document_kind(conductor, package) == "preset":
            refuse(f"document-preset -- {shown(package)}: `{name}` is a preset of the package, and a house document "
                   f"of that name would hide it -- choose another name; `team document {name}` prints the preset.")
        placed(own, DOCUMENT_SKELETON.format(name=own.stem).encode("utf-8"))
        return said("created", own, f"created · {shown(own)}" + (f" · it hides the package's {shown(package)}"
                                                                    if package is not None else ""))
    if origin is None:
        refuse(f"document-unknown -- `{name}`: neither the house nor the package has a document of that name "
               "(`team templates` lists them).")
    if asked["body-file"] is None and not asked["delete"]:
        path = own if origin == "house" else package
        text = path.read_bytes().decode("utf-8")
        kind = document_kind(conductor, path)
        if asked["json"]:
            print(json.dumps({"template": name, "origin": origin, "kind": kind, "path": shown(path), "text": text},
                             ensure_ascii=False))
        else:
            sys.stdout.write(f"pp-team: {name} · {kind} · {origin} · {shown(path)}\n{text}")
        return 0
    if origin == "package":
        refuse(f"document-readonly -- {shown(package)}: `{name}` belongs to the package and cannot be changed -- "
               f"`team document {name} --new` gives the house its own document of that name, used in its place.")
    if document_kind(conductor, own) == "preset":
        refuse(f"document-unknown -- {shown(own)}: `{name}` is a preset, not a document: this verb prints a preset "
               "but never replaces or deletes one.")
    if asked["delete"]:
        users = document_users(root, conductor, name)
        if users:
            refuse(f"document-used -- `{name}` is still named on a line of `documents:` by " + "; ".join(users)
                   + " -- take it off each of these lines first: `team declare <team> [--season] --document "
                   "\"<key> <document> ...\"` rewrites a line, `--no-document <key>` removes it; a house's preset is "
                   "changed in its own file.")
        own.unlink()
        if not any(own.parent.iterdir()):
            own.parent.rmdir()
        return said("deleted", own, f"deleted · {shown(own)}" + (f" · the package's {shown(package)} is used again"
                                                                    if package is not None else ""))
    text = text_handed(asked["body-file"])
    if text is None:
        refuse(f"document-invalid -- `--body-file {Path(asked['body-file'])}`: there is no such file.")
    try:
        document_judged(conductor, name, text)
    except Declined as declining:
        refuse(str(declining))
    if own.read_bytes() == text.encode("utf-8"):
        return said("unchanged", own, f"unchanged · {shown(own)} · the same text, nothing written")
    placed(own, text.encode("utf-8"))
    return said("replaced", own, f"replaced · {shown(own)}")


def render_dry(root: Path, conductor, asked: dict) -> int:
    """`team templates --render <directory>/<name> [--value <name>=<value>]... [--team <team> [[--season] --text-file
    <path>|-]] [--json]`: ONE document rendered as `team start` writes it at the root of a team's directory -- its
    conducted head and its body, holes filled by the one filling (`document_rendered`) -- and NOTHING written. The
    values: each `--value` given, else the team's under `--team` (`team` its name, the values its `TEAM.md` applies,
    those its `SEASON.md` gives over them -- under `--text-file`, the CANDIDATE text (`candidate_read`) in the place
    of `TEAM.md`, of `SEASON.md` under `--season`, the other file read on the disk: the values the start takes if
    the text is written), else the document's default; a value given empty (`--value <name>=`) is WITHDRAWN: the team's is not
    taken, the document's default is, or `value-missing`; under `--json` ONE object `{template, text, values: [{name,
    value, from}]}`, `from` `given` or `default`, the text alone otherwise. Refuses: `template-unknown` (no document
    of that name -- a preset is none), `template-invalid`, `team-unknown`, `team-invalid` (a `--text-file` path that
    is no file), the team's own refusal, `value-unknown` (a value the document does not declare), `value-missing` (a
    value without one, named), the usage (a `--value` without `=`, `--season` or `--text-file` without `--team`,
    `--season` without `--text-file`)."""
    if (asked["team"] is None and (asked["season"] or asked["text-file"] is not None)
            or asked["season"] and asked["text-file"] is None):
        refuse(USAGE)
    candidate = candidate_read(asked)
    name = asked["render"]
    given: dict[str, str] = {}
    for one in asked["value"]:
        named, equal, value = one.partition("=")
        if not equal or not named.strip():
            refuse(USAGE)
        given[named.strip()] = value.strip()
    withdrawn = {named for named, value in given.items() if not value}   # given empty: the team's not taken
    asked_names = list(given)
    given = {named: value for named, value in given.items() if value}
    found = templates_of(root, conductor).get(name)
    try:
        if found is not None and found["error"]:
            decline(found["error"])
        if found is None or found["kind"] != "document":
            decline(f"template-unknown -- `--render {name}`: no document of that name"
                    + (" -- a preset renders none" if found else "") + " (`team templates`).")
        defaults: dict[str, str] = {}
        if asked["team"] is not None:
            team_name, _ = named_team(conductor, [asked["team"]])
            if not team_doc(root, team_name).is_file():
                refuse(f"team-unknown -- no {team_doc(root, team_name)}: the owner declares the team there.")
            season_path = team_root(root, team_name) / SEASON_DOC
            team = team_played(root, conductor, team_name, None if asked["season"] else candidate)
            season = season_front(conductor, season_path, candidate if asked["season"] else None) or {}
            defaults = {BUILT_IN: team_name, **{one["name"]: one["value"] for one in team.applied},
                        **values_given(conductor, season, season_path, "season-invalid")}
        declared = values_declared(conductor, found["front"], found["path"])
        values = render_values(name, declared, given, defaults, withdrawn, asked_names)
        render_named(name, values, template_text(found["path"]), withdrawn)
        text = document_rendered(conductor, found["path"], {one["name"]: one["value"] for one in values})
    except Declined as declining:
        refuse(str(declining))
    if asked["json"]:
        print(json.dumps({"template": name, "text": text, "values": values}, ensure_ascii=False))
    else:
        sys.stdout.write(text)
    return 0
