"""The `documents` domain, layer `rules`: which documents a team declares and keeps, judged from the values it
is given.

A definition belongs here when it computes its answer from its arguments alone: a key named by its values, what a start
kept of the documents, the gap since the start, the entries each member receives, a document made of the bytes it is
given. It also JUDGES what a store read: the lines of a `documents:` key, the values, the roles, the collisions and the
holes of a rendering, a document of the team's own, the team's directory -- a document edited, a collision, the
intention misplaced --, the entries missing, the common documents of the members -- their laws, their tools, the lines
they are served --, the entry a wake-up plays under a run, and the vector a member asks for. It holds the name of a
team's document (`document_name`), which a decision writes and a face reads from here. A judgement that fails
DECLINES (`Declined`) with the text the refusal prints, and its caller refuses. It reads no disk, no clock and no
environment, prints nothing and never ends the call: what needs the system belongs to `store`. It may call the engine
it is given for reading a text alone -- a name's form, a section, a front matter, a document made of a text -- and
nothing else of it.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from house.model import BORDER, TEAMS, TEAM_DOC, decline
from house.rules import body_of
from template.model import ALL, BUILT_IN, HOLE, SEASON_DOC
from documents.model import IDLE, MOUNT_MOMENT, ROLES_DIR, SHEET, TEAM_LAW
from template.rules import holes_filled


def key_named(key: str, values: dict[str, str]) -> str:
    """-> a key of a `documents:` line as its values name it: a hole `{<name>}` filled when a value names it, the key as
    written otherwise -- what two lines are compared by."""
    hole = HOLE.fullmatch(key)
    return values.get(hole.group(1), key) if hole is not None and hole.group(1) else key


def documents_kept(rendering: dict) -> list[dict]:
    """-> what `team-started.documents` keeps of the documents a start renders: `[{document, template, origin,
    roles}]`, in their order."""
    return [{key: one[key] for key in ("document", "template", "origin", "roles")} for one in rendering["documents"]]


def rendered_kept(started: dict | None) -> dict[str, str]:
    """-> the documents the last start rendered, `{document: digest}`: `TEAM-<name>.md` and each document of a line."""
    return dict((started.body.rendered if started is not None else None) or {})


def documents_gap(name: str, started: dict, rendering: dict) -> dict | None:
    """-> the entry `documents` of `pending` -- `{key, started, declared}`, each side the documents (`documents_kept`)
    and the digest of each, `TEAM-<name>.md` apart -- when the documents the next start renders differ from those the
    last start rendered; None when they are the same."""
    head = document_name(name)
    then = {"documents": started.body.documents or [],
            "rendered": {one: digest for one, digest in (started.body.rendered or {}).items() if one != head}}
    now = {"documents": documents_kept(rendering),
           "rendered": {one: hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
                        for one, text in rendering["texts"].items()}}
    return None if then == now else {"key": "documents", "started": then, "declared": now}


# --- the entries: successors of each agent's DAG, from the team's directory --------------------

def entries_at(team: dict) -> dict[str, list[str]]:
    """-> for each agent's path, the entry documents its members may play, in the declaration's
    order: `do`'s for every member, a ceremony's for its participants and its facilitator."""
    played: dict[str, list[str]] = {}
    ceremonies = {one.name: one for one in team.ceremonies}
    for trigger, document in team.entries.items():
        members = (list(team.agents) if trigger == "do"
                   else [*ceremonies[trigger].participants, ceremonies[trigger].facilitator])
        for member in members:
            documents = played.setdefault(team.agents[member], [])
            if document not in documents:
                documents.append(document)
    return played


def document_planned(conductor, path: Path, data: bytes):
    """-> the engine's document of a text about to be written at `path` -- its front matter read as the engine reads a
    file's (`reading.front_matter`); `conductor.Refusal` when it opens on none or never closes it."""
    lines = data.decode("utf-8").splitlines()
    if not lines or lines[0].strip() != BORDER:
        raise conductor.Refusal("front-matter-missing", f"{path.name} does not open with a front matter")
    end = next((at for at, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    if end is None:
        raise conductor.Refusal("front-matter-unterminated", f"{path.name} never closes its front matter")
    return conductor.Document(name=path.stem, front=conductor.reading.front_matter(lines[1:end]), path=path)


def documents_lined(preset, own: list[tuple], given: dict[str, str], path: Path, code: str) -> list[tuple]:
    """-> the lines of `documents:` of ONE values file -- the preset's first (`preset`, `template_of`'s, None without
    one), each line of the file (`own`) replacing, in place, the preset's line whose key is the same once filled
    (`key_named`: the file's values, `given`, over the preset's defaults) --, `[(key, documents, at)]`, `at` the file
    the line is read from. DECLINES `code` (the file's, `template-invalid` for the preset's) for two lines of one file
    on one key once filled."""
    filling = {**{one["name"]: one["default"] for one in (preset.values if preset is not None else None) or []
                  if one["default"] is not None}, **given}
    lines: dict[str, tuple] = {}
    sources = (((preset.documents if preset is not None else None) or [], preset.path if preset is not None else None,
                {}, "template-invalid"),
               (own, path, {}, code))
    for source, at, lined, refused in sources:
        for key, documents in source:
            named = key_named(key, filling)
            if named in lined:
                decline(f"{refused} -- {at}: documents: `{key}` -- the key `{named}` said twice once filled: one line "
                        "per key.")
            lined[named] = True
            lines[named] = (key, documents, at)
    return list(lines.values())


def rendering_judged(name: str, team: dict, reads: list[tuple[str, dict]], path: Path) -> tuple:
    """-> (the values, `[{name, value, from}]`; the values by name; the lines, `[{key, team, season}]`; the documents,
    `[{document, template, origin, roles, members}]`; what renders each, `[(document, entry, roles)]`, `entry` its
    `{template, origin, path, keys}`) of the team's documents, judged from what `documents_of` read of `TEAM.md` and
    of `SEASON.md` at `path` (`reads`: `[(source, read)]`, the season's lines ADDED to the team's): the values the
    presets and the documents of both files declare, given by `TEAM.md` then by `SEASON.md`, `{team}` built in; each
    key filled (`holes_filled`) and judged on the team's `roles:`; each document once, `TEAM-<name>-<document's
    name>.md` -- at the root when the key `all` names it, under `roles/` otherwise. DECLINES, in this order:
    `value-unknown`, `value-missing`, `value-undeclared`, `role-unknown`, `document-collision`."""
    declared: dict[str, dict] = {}
    for _, read in reads:
        for one in read["declared"]:
            declared.setdefault(one["name"], one)
    given = {"team": team.read["given"], "season": dict(reads).get("season", {}).get("given") or {}}
    for named in given["season"]:
        if named not in declared:
            decline(f"value-unknown -- {path}: values: `{named}` -- what TEAM.md and SEASON.md name declares "
                    f"{', '.join(f'`{one}`' for one in declared) or 'no value'} (`team templates`).")
    values = [{"name": BUILT_IN, "value": name, "from": "built-in"}]
    for one in declared.values():
        source = next((source for source in ("season", "team") if one["name"] in given[source]), None)
        if source is not None:
            values.append({"name": one["name"], "value": given[source][one["name"]], "from": source})
        elif one["default"] is not None:
            values.append({"name": one["name"], "value": one["default"], "from": "default"})
        else:
            decline(f"value-missing -- {one['at']}: `{one['name']}` ({one['description']}) has no default -- give it "
                    "under `values:`, `<name> = <value>`.")
    filled = {one["name"]: one["value"] for one in values}
    lines: dict[str, dict] = {}
    found: dict[str, dict] = {}
    for source, read in reads:
        for key, documents, at in read["lines"]:
            said = holes_filled(key, filled, at)
            if said != ALL and said not in team.roles:
                decline(f"role-unknown -- {at}: documents: `{key} {' '.join(documents)}` -- the role `{said}` is not "
                        f"declared by teams/{name}/{TEAM_DOC}'s `roles:` "
                        f"({', '.join(f'`{one}`' for one in team.roles) or 'no key'}).")
            line = lines.setdefault(said, {"key": said, "team": [], "season": []})
            for one in documents:
                line[source] += [] if one in line[source] else [one]
                entry = found.setdefault(one, {**read["documents"][one], "keys": []})
                entry["keys"] += [] if said in entry["keys"] else [said]
    named: dict[str, str] = {}
    for one, entry in found.items():
        short = one.rsplit("/", 1)[-1]
        if short == SHEET or short in named:
            other = f"the members' sheet `TEAM-{name}-{SHEET}.md`" if short == SHEET else f"`{named[short]}`"
            decline(f"document-collision -- documents: `{one}` and {other} -- both would be rendered as "
                    f"TEAM-{name}-{short}.md: name one of them.")
        named[short] = one
    documents, made = [], []
    for one, entry in found.items():
        roles = [] if ALL in entry["keys"] else entry["keys"]
        short = one.rsplit("/", 1)[-1]
        document = f"{ROLES_DIR}/TEAM-{name}-{short}.md" if roles else f"TEAM-{name}-{short}.md"
        made.append((document, entry, roles))
        documents.append({"document": document, "template": one, "origin": entry["origin"], "roles": roles,
                          "members": list(dict.fromkeys(member for key in roles for member in team.roles[key]))
                          if roles else None})
    return values, filled, list(lines.values()), documents, made


def own_served(own: str, path: Path, roles: list[str]) -> str:
    """-> the text a file of the team's directory is served as, `own` as it stands -- under an empty front matter for a
    document of a role that has none: the engine mounts no document without one. DECLINES `document-holes` naming
    `path` for a hole `{<name>}`: only a template fills values."""
    if any(hole.group(1) for hole in HOLE.finditer(own)):
        decline(f"document-holes -- {path}: a hole `{{<name>}}` -- a file of the team's directory is "
                "served as it stands: lay a template under .pp/teams/templates/ to fill values.")
    return own if not roles or own.lstrip().startswith(BORDER) else f"{BORDER}\n{BORDER}\n{own}"


def edited_judged(target: Path, data: bytes | None, digest: str, head: bool) -> None:
    """DECLINES `rendered-edited` for a document the last start rendered (`digest`, the one the journal kept) whose
    bytes (`data`, None when it stands not) no longer carry that digest -- `head`: it is `TEAM-<name>.md`."""
    if data is not None and hashlib.sha256(data).hexdigest()[:12] != digest:
        where = (f"the body of {TEAM_DOC}" if head else
                 f"{TEAM_DOC}, {SEASON_DOC} or a template")
        decline(f"rendered-edited -- {target}: rendered by the last start, edited since -- a rendered document is "
                f"never edited: move the words to {where}, or delete it to render it again.")


def collision_judged(target: Path, stands: bool) -> None:
    """DECLINES `document-collision` for a document to render whose name a file no start rendered holds (`stands`)."""
    if stands:
        decline(f"document-collision -- {target}: stands and no start rendered it -- the owner's: "
                "move it, or name another document.")


def intention_judged(target: Path, data: bytes | None, intention: str, kept: dict[str, str], declared: Path) -> None:
    """DECLINES `intention-misplaced` for a `TEAM-<name>.md` no start rendered (`data`, its bytes; None when it stands
    not) whose body is not the `intention` this start renders, nor a document the last start rendered (`kept`) --
    the owner's word lives in the body of `TEAM.md` (`declared`)."""
    if data is None:
        return
    text = data.decode("utf-8")
    body = body_of(text) if text.lstrip().startswith(BORDER) else text.strip()
    if (body and body != intention
            and hashlib.sha256(data).hexdigest()[:12] not in kept.values()):   # a document renamed with its team
        decline(f"intention-misplaced -- {target}: its body was written by hand -- `team start` renders this "
                f"document from the team's template: move these words to the body of {declared}, "
                "the owner's word, served to every member, then start again.")


def missing_judged(missing: list[str], name: str) -> None:
    """DECLINES `entry-missing` for the entries nothing resolves (`missing`, `entries_missing`'s): the agent's run would
    name a successor it cannot play, and would play no exchange at all."""
    if missing:
        decline(f"entry-missing -- {'; '.join(missing)}: an entry lives in the team's directory "
               f"({TEAMS}/{name}/), or in the instance of every agent that plays it -- lay it there, then start again.")


def laws_judged(entry: dict, document, laws: list, member: str, where: str, held: dict[str, str],
                declared: set[str]) -> dict[str, str]:
    """-> the codes `member`'s view holds once the document of `entry` mounted (`held`, `{code: document}`, the
    document's laws added): its `mount:` and each of its `laws`, judged in its view. DECLINES, the member and the
    document named: `common-mount-moment`, a document of a role whose `mount:` is not `MOUNT_MOMENT`;
    `common-code-prefix`, a code that does not open on `TEAM_LAW`; `common-collision`, a code another document of the
    view declares, or one declared at the member (`declared`, `where` saying it)."""
    named = entry["document"]
    moment = str(document.front.get("mount") or "").strip()
    if entry["by"] == "vector" and moment != MOUNT_MOMENT:
        decline(f"common-mount-moment -- `mount: {moment}` ({named}), in the view of {member}: a document of "
                f"a role is mounted by its member's vector before the message of every exchange -- declare "
                f"`mount: {MOUNT_MOMENT}`.")
    held = dict(held)
    for law in laws:
        if not law.code.startswith(TEAM_LAW):
            decline(f"common-code-prefix -- `{law.code}` ({named}): a law of a document the team mounts "
                    f"opens on `{TEAM_LAW}`, the prefix kept for the team's laws -- recode it `{TEAM_LAW}<n>`.")
        if law.code in held:
            decline(f"common-collision -- `{law.code}` ({named}) is declared by {held[law.code]} too: both "
                    f"are mounted in the runs of {member} -- give one of them another code.")
        held[law.code] = named
        if law.code in declared:
            decline(f"common-collision -- `{law.code}` ({named}) is already declared at {member} ({where}): "
                    "mounted in its runs, it would refuse `mount-collision` at every exchange -- recode it.")
    return held


def tools_judged(unknown: list[str], named: str, member: str, where: str) -> None:
    """DECLINES `common-tool-unknown` for the first `tools:` name of the document `named` nothing resolves at the
    member (`unknown`, `tools_unknown`'s)."""
    if unknown:
        decline(f"common-tool-unknown -- `{unknown[0]}` ({named}): nothing resolves it at {member} "
                f"({where}) -- no document, no skill, no contract of a harness home; name one it plays.")


def serves_judged(lost: list[str], named: str, name: str, member: str, where: str) -> None:
    """DECLINES `common-serve-unknown` for the first `serve:` document of the document `named` that resolves nowhere
    for a run of the team (`lost`, `served_lost`'s)."""
    if lost:
        decline(f"common-serve-unknown -- `{lost[0]}` ({named}): neither in the team's directory "
                f"({TEAMS}/{name}/) nor resolved at {member} ({where}) -- lay it there, or name what it reads.")


# --- the entry of a wake-up, and a member's vector ----------------------------------------------

def run_under(state, standing: list, run: str) -> list:
    """-> the open intents (`standing`) of the wake-ups launched under the run `run`: their intent's run, or their
    `wake-launched`'s."""
    found = []
    for one in standing:
        launched = state.wake.launched.get(one.body.tag)
        if run in (one.body.run, launched.body.run if launched is not None else None):
            found.append(one)
    return found


def opening_under(state, standing: list, run: str, lines: list[dict]) -> list:
    """-> the intents of an opening's first exchange under the run `run`: the open intents without a run whose tag a
    line of the house's `messages.jsonl` (`lines`) names under that run."""
    opening = {one.body.tag for one in standing if one.body.run is None}
    return [state.wake.intents[line["tag"]] for line in lines
            if line.get("run") == run and line.get("tag") in opening]


def entry_chosen(state, under: list) -> str:
    """-> the entry the last wake-up of `under` plays: its task's ceremony's, any other task `do`'s; no entry: the
    neutral `TEAM-IDLE.md`."""
    started = state.season.started
    entries = (started.body.entries if started is not None else None) or {}
    task = state.task.tasks.get(under[-1].body.task)
    document = entries.get(str(task.ceremony)) if task is not None and task.ceremony else entries.get("do")
    return str(document or IDLE)


def vector_team(name: str, stands: bool) -> None:
    """DECLINES `team-unknown` for a vector whose team no `TEAM.md` declares (`stands`)."""
    if not stands:
        decline(f"team-unknown -- `{name}`: no {TEAMS}/{name}/{TEAM_DOC} in this house.")


def vector_started(name: str, started) -> None:
    """DECLINES `team-not-started` for a vector whose team has no season under way (`started`)."""
    if started is None:
        decline(f"team-not-started -- `{name}`: no season under way, no member's view to mount.")


def vector_member(name: str, member: str, agents: dict) -> None:
    """DECLINES `member-unknown` for a member the season under way does not know (`agents`)."""
    if member not in agents:
        decline(f"member-unknown -- `{member}`: the season of `{name}` knows {', '.join(agents) or 'nobody'}.")


def vector_caller(name: str, member: str, agents: dict, played: bool) -> None:
    """DECLINES `member-foreign` when the instance calling is not the agent that plays the member (`played`)."""
    if not played:
        decline(f"member-foreign -- `{name}/{member}` is played by {agents[member]}: another agent's vector is never "
                "mounted.")


def vector_root(name: str, documents: str, under: bool) -> None:
    """DECLINES `root-foreign` when the run's root of documents (`documents`) is not the team's directory (`under`)."""
    if not under:
        decline(f"root-foreign -- the run's root of documents is `{documents or 'none'}`, not {TEAMS}/{name}/: a "
                "member's documents are mounted under its team's directory alone.")


def document_name(name: str) -> str:
    """-> the file name of the team's document: `TEAM-<name>.md`."""
    return f"TEAM-{name}.md"
