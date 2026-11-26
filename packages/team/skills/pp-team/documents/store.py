"""The `documents` domain, layer `store`: where a team's documents are read, and nothing judged.

A definition belongs here when it reads from the system for a document and gives back what it read: a document found
among the templates and the team's directory, its text, its front matter, the bytes of `SEASON.md` and of the documents
a start rendered, whether a path stands, the entries missing, the documents a member mounts and their laws, whether an
agent is born, the inventories and the tools the engine knows, the lines a run is served, the slots a run holds, a
member's description, the environment of a run. A front matter of bytes a start is about to write is read by the rule
its caller gives (`made`). It judges nothing and imports no rule and no face: what the documents are worth belongs to
a rule, and an act chains the reading and the judgement.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from house.model import TEAMS, TEAM_DOC, decline
from house.rules import agent_meta, body_of, team_root
from house.store import ENTRY
from template.model import SEASON_DOC
from documents.model import MEMBER_FAMILY, NO_DESCRIPTION, SPEC
from season.store import manifests_named, season_word


def document_found(templates: dict[str, dict], directory: Path, document: str, at: Path) -> dict:
    """-> where a document a line names stands: `{template, origin, path}` -- a template the house sees for
    `<directory>/<name>` (`origin` house or package), the file `<name>.md` of the team's `directory` for `<name>`
    (`origin` team). DECLINES `document-unknown` citing `at`: no such document, or a preset; `template-invalid` for a
    template whose front matter the engine cannot read."""
    if "/" in document:
        found = templates.get(document)
        if found is not None and found["error"]:
            decline(found["error"])
        if found is None or found["kind"] != "document":
            decline(f"document-unknown -- {at}: documents: `{document}` -- "
                    + ("a preset, named by `template:`" if found else "no template of that name")
                    + " (`team templates`).")
        return {"template": document, "origin": found["origin"], "path": found["path"]}
    path = directory / f"{document}.md"
    if not path.is_file():
        decline(f"document-unknown -- {at}: documents: `{document}` -- no {path}: a name without `/` is a file of the "
                "team's directory, `<directory>/<name>` a template (`team templates`).")
    return {"template": document, "origin": "team", "path": path}


def document_front(conductor, path: Path, data: bytes | None = None, made=None) -> dict | None:
    """-> the front matter of a document of the team's directory, from its bytes about to be written (`data`, read by
    `made`, the rule the act that plans them gives: `document_planned`) or from the file; None when it has none the
    engine can read."""
    try:
        document = conductor.reading.read(path) if data is None else made(conductor, path, data)
    except (conductor.Refusal, OSError):
        return None
    return document.front


def view_of(conductor, directory: Path, name: str, roles: dict, composed: list[dict], member: str | None = None,
            planned: dict[str, bytes | None] | None = None, made=None) -> list[dict]:
    """-> the VIEW of a member: the documents of the team's directory it receives, in order, each `{document,
    template, roles, effect, by}` -- the ONE place that decides who receives what. First every `TEAM-<name>-<x>.md` at
    the root, sorted by name, for everyone: `served` by the head of `TEAM-<name>.md` (`by: head`), or `mounted` by the
    engine when its front matter declares `mount:` (`by: engine`); a document written by hand has no filter. Then, for
    `member`, each document of `composed` rendered under `roles/` for a role key the member holds (`roles`: `{key:
    [members]}`), once whatever the keys it shares, in their order: mounted by the member's vector (`by: vector`),
    `mounted` when it declares `mount:` (its laws, its tools, its body), `served` otherwise (its body alone). A
    document of a role the season rendered and that is missing on disk STAYS in the view: the member's next mount
    refuses `mount-missing` naming it, never a vector dropped in silence; a start renders it again. Without
    `member`, the root alone: what every member receives. From a season (`team-started.documents`, the files on
    disk) or from the declaration (the documents in memory and the `planned` bytes, `documents_planned`, read by
    `made`, the rule that reads bytes about to be written: `document_front`)."""
    planned = planned or {}
    known = {one["document"]: one for one in composed}
    standing = {one.name for one in team_documents(directory, name) if planned.get(one.name, b"") is not None}
    found = []
    for document in sorted(standing | {one for one, data in planned.items() if data is not None and "/" not in one}):
        front = document_front(conductor, directory / document, planned.get(document), made) or {}
        mounts = bool(str(front.get("mount") or "").strip())
        entry = known.get(document) or {}
        found.append({"document": document, "template": entry.get("template"), "roles": [],
                      "effect": "mounted" if mounts else "served", "by": "engine" if mounts else "head"})
    if member is None:
        return found
    held = {key for key, members in roles.items() if member in members}
    for one in composed:
        if not one["roles"] or not held & set(one["roles"]):
            continue
        data = planned.get(one["document"])
        if data is None and one["document"] in planned:
            continue                                   # removed by this start
        front = document_front(conductor, directory / one["document"], data,   # missing: kept, its mount says it
                               made) or {}
        mounts = bool(str(front.get("mount") or "").strip())
        found.append({"document": one["document"], "template": one["template"], "roles": one["roles"],
                      "effect": "mounted" if mounts else "served", "by": "vector"})
    return found


def season_view(root: Path, conductor, name: str, started: dict | None, member: str) -> list[dict]:
    """-> the view of a member in the season under way (`view_of`): the roles and the documents `team-started` kept,
    the documents its start rendered on disk; [] for a team never started."""
    if started is None:                                             # no start
        return []
    return view_of(conductor, team_root(root, name), name, started.body.roles or {}, started.body.documents or [],
                   member)


def member_vector(root: Path, conductor, name: str, started: dict | None, member: str) -> str | None:
    """-> the vector of a member, `team-member:<team>/<member>`, when its season's view holds a document of a role;
    None otherwise: a member without one pays no gesture."""
    view = season_view(root, conductor, name, started, member)
    return f"{MEMBER_FAMILY}:{name}/{member}" if any(one["by"] == "vector" for one in view) else None


def team_documents(directory: Path, name: str) -> list[Path]:
    """-> every `TEAM-<name>-<x>.md` standing in the team's directory, sorted by name."""
    prefix = f"TEAM-{name}-"
    if not directory.is_dir():
        return []
    return sorted((one for one in directory.iterdir() if one.is_file() and one.name.startswith(prefix)
                   and one.name.endswith(".md") and len(one.name) > len(prefix) + len(".md")), key=lambda one: one.name)


def served_of(conductor, directory: Path, name: str) -> list[str]:
    """-> what the head of `TEAM-<name>.md` serves after the document itself, whose name the act composes
    (`documents_written`, by the face `document_name`): `TEAM.md` when its body says something
    -- the owner's word, served as it is and read again as soon as it changes --, then the package's `TEAM_WORK.md`
    -- how a
    team works, read before the team's other documents it tells how to read --, then `SEASON.md` when its body says
    something -- the owner's word of the season, served as it is and read again as soon as it changes --, then what
    every member's view (`view_of`) gives the head to serve: each `TEAM-<name>-<x>.md` of the root that does not
    mount, sorted by name -- the engine mounts the others, a second reading would bring their body twice; a document
    of a role, under `roles/`, is its members' vector's. Their NAMES alone, never their bodies: pp serves them, the
    spec found by its name in the refs of the package the member's instance plays."""
    declared = directory / TEAM_DOC
    word = body_of(declared.read_text(encoding="utf-8")) if declared.is_file() else ""
    return [*([TEAM_DOC] if word else []), SPEC, *([SEASON_DOC] if season_word(directory) else []),
            *(one["document"] for one in view_of(conductor, directory, name, {}, []) if one["by"] == "head")]


def served_at(conductor, directory: Path, meta: Path, born: bool, document: str) -> bool:
    """-> whether a `serve:` document resolves for a run of the team: in the team's directory -- its runs' root of
    documents --, at the instance `meta` (`instance.resolve`), at the member's repository when it is born, or, for a
    bare name, as a skill's contract (the instance's skills, a harness home, the house's procs)."""
    if (directory / document).is_file() or conductor.instance.resolve(meta, document).is_file():
        return True
    if born and (meta.parent / document).is_file():
        return True
    stem = Path(document).stem
    return "/" not in document and (conductor.instance.skill_contract(meta, stem)
                                    or conductor.instance.adopted(meta, stem)) is not None


def said_description(conductor, path: Path) -> str:
    """-> the `description:` of a document's front matter, its blanks folded; "" when absent or unreadable."""
    try:
        said = conductor.reading.read(path).front.get("description")
    except (conductor.Refusal, OSError):
        return ""
    return " ".join(str(said or "").split())


def template_description(root: Path, conductor) -> str:
    """-> the `description:` of the member template the house's base carries (`MEMBER.md` of its user layer, the
    copy the house vendors), "" when none stands: a member still saying it has no description of its own."""
    package = manifests_named(root, conductor).get(conductor.instance.base_of(root))
    seed = package / conductor.install.USER / "MEMBER.md" if package is not None else None
    return said_description(conductor, seed) if seed is not None and seed.is_file() else ""


def description_of(root: Path, conductor, path: str, template: str) -> str:
    """-> what the members' sheet says of the agent at `path`: the `description:` of its `MEMBER.md`, or
    `no description` when it is absent, empty or still the template's."""
    said = said_description(conductor, agent_meta(root, path) / "MEMBER.md")
    return said if said and said != template else NO_DESCRIPTION


def document_read(path: Path) -> str:
    """-> the text of a file of the team's directory a line names, as it stands."""
    return path.read_text(encoding="utf-8")


def season_data(path: Path, text: str | None) -> bytes:
    """-> the bytes of `SEASON.md`: the file, or `text`, what `declare --season` is about to write there."""
    return path.read_bytes() if text is None else text.encode("utf-8")


def rendered_bytes(path: Path) -> bytes | None:
    """-> the bytes of a document of the team's directory, None when no such file stands."""
    return path.read_bytes() if path.is_file() else None


def path_stands(path: Path) -> bool:
    """-> whether anything stands at `path`."""
    return path.exists()


def entries_missing(root: Path, conductor, name: str, at: dict[str, list[str]]) -> list[str]:
    """-> each entry `at` names (`entries_at`: the documents each agent's path may play) that is neither in the team's
    directory nor resolved by the instance of the agent that plays it, `<path> lacks <document>`, in their order."""
    directory = team_root(root, name)
    return [f"{path} lacks {document}" for path, documents in at.items()
            for document in documents
            if not (directory / document).is_file()
            and (not conductor.instance.is_instance(agent_meta(root, path))
                 or not conductor.instance.resolve(agent_meta(root, path), document).is_file())]


def mounted_read(conductor, path: Path):
    """-> the engine's document of a file of the team's directory a member mounts; None when it has no front matter
    the engine can read, or stands not: it mounts nothing."""
    try:
        return conductor.reading.read(path)
    except (conductor.Refusal, OSError):
        return None


def document_laws(conductor, path: Path, document) -> tuple[list, list[str]]:
    """-> (the laws a mounted document declares, the documents its `serve:` lines name -- a row read from a material,
    `@<name>`, left out), read by the engine. DECLINES `team-invalid` naming `path` for a law or a line the engine
    cannot read."""
    try:
        laws = conductor.reading.constraints(document)
        served = [conductor.reading.ranged(token)[0] for row in conductor.reading.serve_lines(document)
                  if not any(one.startswith("@") for one in row)
                  for token in (row[1:] if row and row[0].endswith(":")
                                and row[0][:-1] in conductor.settings.SERVE_NATURES else row)]
    except conductor.Refusal as refusal:
        decline(f"team-invalid -- {path}: {refusal}")
    return laws, served


def is_born(conductor, meta: Path) -> bool:
    """-> whether the agent at `meta` stands, an instance."""
    return conductor.instance.is_instance(meta)


def homes_of(conductor, at: Path) -> list[Path]:
    """-> the homes of the packages the instance `at` vendors."""
    return list(conductor.instance.vendored(at))


def inventory_of(conductor, home: Path) -> set[str]:
    """-> the codes a home declares, the engine's inventory (`sections.inventory`)."""
    return conductor.sections.inventory(home)


def tools_unknown(conductor, document, at: Path) -> list[str]:
    """-> the names of the `tools:` of a mounted document that nothing resolves at the instance `at`, in their order."""
    return [one.name for one in conductor.compiling.tools_of(document, at) if not one.contract]


def served_lost(conductor, directory: Path, at: Path, born: bool, served: list[str],
                planned: dict[str, bytes | None]) -> list[str]:
    """-> the `serve:` documents of a mounted document that resolve nowhere for a run of the team (`served_at`) -- one
    this start removes (`planned`, None) counts as gone, one it writes as standing --, in their order."""
    return [one for one in served if (planned[one] is None if one in planned   # removed by this start
                                      else not served_at(conductor, directory, at, born, one))]


def slots_held(metas: list[Path], run: str) -> list[bool]:
    """-> for each agent's instance of `metas`, whether it holds the slot of the run `run` -- an opening under way: the
    house opened the run before any record names it."""
    sys.path.insert(0, str(Path(ENTRY).resolve().parents[1]))
    from _core import core                         # noqa: E402 -- the bootstrap
    persistence = core(ENTRY).persistence
    return [persistence.slot_of(meta, run).is_file() for meta in metas]


def run_documents(conductor, meta: Path) -> str:
    """-> the root of documents of the run the call plays in: `PP_DOCUMENTS`, the root the launcher gives the run (at
    its `-new`, while its slot is staged in the engine's process and not on disk yet), else the root kept at the slot
    of the run `PP_RUN` names at `meta`; "" without one."""
    documents = os.environ.get(conductor.context.DOCUMENTS, "").strip()
    run = os.environ.get(conductor.context.VARIABLE, "").strip()
    if not documents and run:
        slot = conductor.persistence.slot_of(meta, run)
        documents = conductor.persistence.documents_of(slot) if slot.exists() else ""
    return documents or ""


def in_team_run(root: Path, conductor, meta: Path) -> bool:
    """-> whether the call plays in a run a TEAM opened: its root of documents is the directory of a team of the
    house -- `PP_DOCUMENTS`, the root the launcher gives the run (at its `-new`, while its slot is staged in the
    engine's process and not on disk yet), else the root kept at the slot of the run `PP_RUN` names at `meta`."""
    documents = run_documents(conductor, meta)
    if not documents:
        return False
    directory = Path(documents).resolve()
    return directory.parent == (root.parent / TEAMS).resolve() and (directory / TEAM_DOC).is_file()
