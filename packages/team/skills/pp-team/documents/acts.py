"""The `documents` domain, layer `acts`: a team's documents read, then judged -- the steps chained.

A definition belongs here when it chains the readings of stores and the judgements of rules for a verb or another act,
reading and judging in the order the work has always had, so a refusal comes at the same rank: the documents a team
declares (`documents_of`); the documents a start renders (`documents_rendered`); the team's directory and its entries
checked against what a start would write (`directory_judged`, `entries_judged`); the common documents of the members
(`common_judged`); the documents a start writes, planned, kept and checked, then written in the team's directory; the
document the wake-up under a run plays, read from the journal and the house's records; a member's vector judged for
the instance and the run that ask, refused when a rule declines it; and two faces that must read -- the declaration
as it plays (`declared_face`), which reads the season and the members' descriptions, and the members' sheet
(`sheet_of`). Only verbs and other acts call it; no store, face or rule does, and it imports no act of another domain.
It may use the lower layers of any domain.

`TEAM.md` is the OWNER'S file: pp writes it on the owner's gesture alone (`team declare`: the keys its flags name,
the rest at its bytes), never in season. Its BODY is the owner's word:
the head of `TEAM-<name>.md` serves it by its name, as it stands -- no hole is filled --, and a member reads it
again as soon as it changes, without a start; a `TEAM.md` without a body is not served. `TEAM-<name>.md` is pp's:
RENDERED by every `start` -- its head, then for its body the INTENTION of the preset `TEAM.md` names, each hole
filled for the team as it plays: the values `TEAM.md` applies, then the ten values built in every team preset,
which the form makes of the members (`{root}`, `{others}`, `{chain}`, `{last}`, `{squads}`, `{workers}`, `{tree}`,
`{quorum}`, `{count}`, `{daily}`); empty without a preset. A member added or a preset changed is in the
intention at the next season. Its digest is kept at `team-started.rendered`: retouched, the next `start` refuses
`rendered-edited`; a `TEAM-<name>.md` no start rendered whose body is not that intention refuses
`intention-misplaced` -- the words belong in the body of `TEAM.md`, and pp moves nothing.

`documents: |` of `TEAM.md` and of `SEASON.md` -- the same grammar, read by ONE code (`documents_of`) -- names the
documents of each key, one `<key> <document> ...` per line, each key once in a file: the key `all` for every
member, a role key for the members who hold it, or a hole `{<name>}` a value fills; each document
`<directory>/<name>`, a template the house sees, or `<name>`, a file `<name>.md` of the team's directory, once on its
line. A preset's lines are the defaults of the file that names it: a line of the file replaces the preset's line
of the same key once both keys are filled. `SEASON.md`'s lines are ADDED to `TEAM.md`'s for the season: a key both
files name receives the documents of both. Every `start` renders each document ONCE (`documents_rendered`), as
`TEAM-<name>-<document>.md`, `<document>` the last part of its name -- at the root when the key `all` names it,
under `roles/` otherwise: a template's body under its conducted head, its holes filled (`document_rendered`); a
file of the team's directory as it stands, refused `document-holes` when it has a hole. The values: the presets
and the documents declare them, `TEAM.md` gives them, `SEASON.md` gives them over `TEAM.md`'s name by name,
`{team}` built in. A line taken out, its documents leave at the next `start`. Kept at `team-started.documents`
(`[{document, template, origin, roles}]`), their digests at `team-started.rendered`, the digest of `SEASON.md` at
`team-started.season-digest` when it says documents or values.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from house.model import Declined, TEAMS
from house.rules import agent_meta, journal_of, record_of, team_doc, team_root
from house.store import ENTRY, caller, lines_of, placed, refuse
from template.model import SEASON_DOC
from documents.model import ACT_FORMAT, IDLE, IDLE_SOURCE, MESSAGES, RETIRED_IN_TEAM, ROLES_DIR, TURN_DOC
from template.rules import documents_declared, documents_none, values_declared, values_given
from template.acts import document_rendered, template_of, templates_of
from season.rules import set_of
from season.store import season_front, season_set
from documents.rules import (collision_judged, document_name, document_planned, documents_lined,
                             edited_judged, entries_at, entry_chosen, intention_judged, laws_judged, missing_judged,
                             opening_under, own_served, rendered_kept, rendering_judged, run_under, serves_judged,
                             tools_judged, vector_caller, vector_member, vector_root, vector_started, vector_team)
from documents.faces import sheet_name, team_document, turn_overlay
from documents.store import (description_of, document_found, document_laws, document_read,
                             entries_missing, homes_of, inventory_of, is_born, mounted_read, path_stands,
                             rendered_bytes, run_documents, season_data, served_lost, served_of, slots_held,
                             template_description, tools_unknown, view_of)
from wake.rules import open_intents, path_of_intent
from journal.store import state_of


def documents_planned(root: Path, conductor, name: str, started: dict | None, team: dict,
                      season: str | None = None, directory: bool = True) -> tuple[dict, dict]:
    """-> (the team's documents as rendered in memory, `documents_rendered`'s; the plan of the team's directory:
    `{document: bytes to write, or None to remove}`), judged before any write, the DOCUMENTS whole -- `season`, a text
    of SEASON.md read in the file's place --, then the documents that mount as they WILL stand (`common_judged`), then
    the DIRECTORY (`directory_judged`) -- `directory` False leaves it to the caller, `declaration_read`, which says each
    check apart. A document the last start rendered that no line names any more is removed; one deleted by hand is
    rendered again. `TEAM-<name>.md` itself is written by `documents_written`: its head names what stands then."""
    folder = team_root(root, name)
    rendering = documents_rendered(root, conductor, name, team, season)
    planned: dict[str, bytes | None] = {one: text.encode("utf-8") for one, text in rendering["texts"].items()}
    planned.update({one: None for one in rendered_kept(started) if one not in rendering["texts"]
                    and one != document_name(name) and (folder / one).is_file()})
    common_judged(root, conductor, name, team, planned, rendering["documents"])
    if directory:
        directory_judged(root, name, started, team, planned)
    return rendering, planned


def documents_of(root: Path, conductor, directory: Path, front: dict, path: Path, code: str) -> dict:
    """-> what ONE values file -- `TEAM.md` (`code` `team-invalid`), `SEASON.md` (`season-invalid`) -- says of its
    documents, the ONE reader of both: the preset its `template:` names (`template_of`, of the file's nature; None
    without one), the lines of `documents:` -- the preset's first, each line of the file replacing, in place, the
    preset's line whose key is the same once filled (`key_named`: the file's values over the preset's defaults) --,
    `[(key, documents, at)]`, `at` the file the line is read from, two lines of one file on one key refused; each
    document found once (`document_found`), `{name: {template, origin, path}}`; the values the preset and the documents
    declare, the preset's first and the first of a name winning, `[{name, description, default, at}]`; the values the
    file gives (`values_given`). DECLINES `code` (`team-invalid`, `season-invalid`) for a line of another form, and
    `template-unknown`, `template-invalid`, `document-unknown`."""
    chosen = str(front.get("template") or "").strip() or None
    own = documents_declared(conductor, front, path, code)
    read = {**documents_none(path), "given": values_given(conductor, front, path, code)}
    if chosen is None and not own:
        return read
    templates = templates_of(root, conductor)
    nature = "team" if code == "team-invalid" else "season"
    preset = None if chosen is None else template_of(conductor, templates, chosen, path, nature)
    lines = documents_lined(preset, own, read["given"], path, code)
    found: dict[str, dict] = {}
    declared: dict[str, dict] = {one["name"]: {**one, "at": path}
                                 for one in (preset.values if preset is not None else None) or []}
    for _, documents, at in lines:
        for one in documents:
            if one in found:
                continue
            found[one] = document_found(templates, directory, one, at)
            if found[one]["origin"] != "team":
                for value in values_declared(conductor, templates[one]["front"], found[one]["path"]):
                    declared.setdefault(value["name"], {**value, "at": path})
    return {**read, "template": preset, "lines": lines,
            "documents": found, "declared": list(declared.values())}


def documents_rendered(root: Path, conductor, name: str, team: dict, text: str | None = None) -> dict:
    """-> the team's DOCUMENTS as the next start renders them, judged whole and rendered in memory: the lines of
    `TEAM.md` (`team["read"]`, `documents_of`'s) and of `teams/<name>/SEASON.md` -- the file, or `text`, what `declare
    --season` is about to write there --, read by the same code, the season's lines ADDED to the team's: a key said by
    both files receives the documents of both. Each key filled by the values (a hole `{<name>}`), then judged on the
    team's `roles:`; each document rendered ONCE, as `TEAM-<name>-<document's name>.md` -- at the root when the key
    `all` names it, under `roles/` otherwise, for the members who hold one of its keys --: a template's body under its
    conducted head, holes filled (`document_rendered`), a file of the team's directory as it stands. The values: what
    the presets and the documents of both files declare, given by `TEAM.md` then by `SEASON.md`, which wins name by
    name, `{team}` built in. `{documents: [{document, template, origin, roles, members}], lines: [{key, team,
    season}], values: [{name, value, from}], texts: {document: text}, season}` -- `members` None for a document of
    everyone, `[]` for one no key's member holds; `season` the digest of SEASON.md when it says documents or values,
    None otherwise. DECLINES, nothing written: `season-invalid`, `template-unknown`, `template-invalid`,
    `document-unknown`, `value-unknown` (a value SEASON.md gives that nothing declares), `value-missing`,
    `value-undeclared`, `role-unknown` (a key `roles:` does not declare, the line's file named),
    `document-collision` (two documents of one name, or a document named `members`), `document-holes` (a file of the
    team's directory with a hole)."""
    folder = team_root(root, name)
    path = folder / SEASON_DOC
    front = season_front(conductor, path, text)
    season = None
    if front is not None and any(key in front for key in ("template", "documents", "values")):
        season = documents_of(root, conductor, folder, front, path, "season-invalid")
    reads = [("team", team.read), *([("season", season)] if season is not None else [])]
    values, filled, lines, documents, made = rendering_judged(name, team, reads, path)
    texts = {}
    for document, entry, roles in made:
        if entry["origin"] == "team":
            texts[document] = own_served(document_read(entry["path"]), entry["path"], roles)
        else:
            texts[document] = document_rendered(conductor, entry["path"], filled, bool(roles))
    digest = None
    if season is not None:
        digest = hashlib.sha256(season_data(path, text)).hexdigest()[:12]
    return {"documents": documents, "lines": lines, "values": values, "texts": texts, "season": digest}


def directory_judged(root: Path, name: str, started: dict | None, team: dict, planned: dict[str, bytes | None]) -> None:
    """Judges the team's DIRECTORY against the plan a start has for it (`documents_planned`), before any write:
    `rendered-edited` for a document the last start rendered whose bytes no longer carry the digest the journal
    kept -- the owner's edit is never written over; `document-collision` for a document to render whose name a
    file the last start did not render holds; `intention-misplaced` for a `TEAM-<name>.md` no start rendered whose
    body is not the intention this start renders -- the owner's word lives in the body of `TEAM.md`, and pp moves
    nothing. DECLINES; what it judges no value of `TEAM.md` nor of `SEASON.md` settles alone."""
    folder = team_root(root, name)
    kept = rendered_kept(started)
    document = document_name(name)
    for one, digest in kept.items():
        edited_judged(folder / one, rendered_bytes(folder / one), digest, one == document)
    for one, data in planned.items():
        if data is not None and one not in kept:
            collision_judged(folder / one, path_stands(folder / one))
    if document not in kept:                           # never rendered: nothing but the intention may stand there
        intention_judged(folder / document, rendered_bytes(folder / document), team.intention, kept,
                         team_doc(root, name))


def entries_judged(root: Path, conductor, name: str, team: dict) -> None:
    """DECLINES `entry-missing` before anything is written when an entry is neither in the team's
    directory nor resolved by the instance of an agent that plays it (a document of its type) --
    the agent's run would name a successor it cannot play, and would play no exchange at all."""
    missing_judged(entries_missing(root, conductor, name, entries_at(team)), name)


def common_judged(root: Path, conductor, name: str, team: dict, planned: dict[str, bytes | None] | None = None,
                  composed: list[dict] | None = None) -> None:
    """Judges the VIEW of each member (`view_of`) before anything is written -- the documents it mounts, as they WILL
    stand when `planned` is given (`{document: bytes about to be written, or None about to be removed}`) and with the
    documents of a role `composed` renders (`documents_planned`): `start` refuses what it declines, `declaration` says
    it. Each
    defect DECLINES by its name, the member and the document named: `common-code-prefix`, a law whose code does not
    open on `TM` -- the prefix kept for the team's laws --; `common-collision`, a code two documents of one member's
    view declare, or a code declared at the member -- its every exchange would refuse `mount-collision` --: two
    documents of disjoint roles may carry the same code; `common-tool-unknown`, a `tools:` name nothing resolves at
    the member (a document, a skill, a contract of a harness home); `common-serve-unknown`, a `serve:` document
    neither in the team's directory -- one this start removes counts as gone -- nor resolved at the member (its
    instance, its repository, a skill); `common-mount-moment`, a document of a role whose `mount:` names another
    moment than `turn.begin`, the one its vector mounts it at. A member is judged at its instance; a member not born yet
    at the house's machine -- the base and the pins `agent add` gives it --, nothing written. The codes declared at a
    member are the engine's inventory (`sections.inventory`, the one `pp-authoring` derives free codes from) of its
    instance and of each package it plays; a row read from a material (`@<name>`) is the run's to resolve, not
    judged."""
    directory = team_root(root, name)
    planned, composed = planned or {}, composed or []
    read: dict[str, tuple | None] = {}

    def judged_document(document: str) -> tuple | None:
        if document not in read:
            path = directory / document
            if planned.get(document) is None:
                parsed = mounted_read(conductor, path)
            else:
                try:
                    parsed = document_planned(conductor, path, planned[document])
                except conductor.Refusal:
                    parsed = None
            if parsed is None:
                read[document] = None                  # no front matter to read: it mounts nothing
                return None
            read[document] = (parsed, *document_laws(conductor, path, parsed))
        return read[document]

    inventories: dict[Path, set[str]] = {}

    def inventory(home: Path) -> set[str]:
        if home not in inventories:
            inventories[home] = inventory_of(conductor, home)
        return inventories[home]

    for member, agent in team.agents.items():
        mounted = [one for one in view_of(conductor, directory, name, team.roles or {}, composed, member,
                                          planned, document_planned) if one["effect"] == "mounted"]
        if not mounted:
            continue
        meta = agent_meta(root, agent)
        born = is_born(conductor, meta)
        at = meta if born else root                    # not born: the house's machine, what `agent add` gives it
        where = agent if born else f"{agent}, not born: the house's machine"
        declared = set().union(*(inventory(home) for home in homes_of(conductor, at)),
                               inventory(meta) if born else set())
        held: dict[str, str] = {}
        for entry in mounted:
            found = judged_document(entry["document"])
            if found is None:
                continue
            document, laws, served = found
            held = laws_judged(entry, document, laws, member, where, held, declared)
            tools_judged(tools_unknown(conductor, document, at), entry["document"], member, where)
            serves_judged(served_lost(conductor, directory, at, born, served, planned), entry["document"], name, member,
                          where)


def documents_written(root: Path, conductor, name: str, team: dict, launch: dict, profiles: dict,
                      planned: dict[str, bytes | None]) -> dict[str, str]:
    """Writes the team's documents in its directory, at every start, and -> the digest of each document it renders
    (`team-started.rendered`, by its place): the documents of the lines first -- each document `planned` written, each
    no line names any more removed (`documents_planned`) --, the members' sheet (`sheet_of`), then
    `TEAM-<name>.md` -- its head serving `TEAM.md`'s body and every `TEAM-<name>-<x>.md` standing then, the sheet
    with them; its body the intention rendered (`team["intention"]`) --, `TEAM-IDLE.md` with entries, and `TURN.md`,
    the overlay of the kit's turn (`turn_overlay`). `TEAM.md` is never written. The law an earlier version laid
    there, `TURN.md` at its bytes (`RETIRED_IN_TEAM`), is replaced by the overlay and said; a `TURN.md` or a
    `TEAM-IDLE.md` standing there and different is the owner's: kept, and said -- under the owner's `TURN.md` the
    team's runs play the turn it writes."""
    here = Path(ENTRY).resolve().parent
    directory = team_root(root, name)
    entries = list(dict.fromkeys(team.entries.values()))
    target, data = directory / TURN_DOC, turn_overlay()
    if not target.is_file():
        placed(target, data)
    elif any(target.read_bytes() == (here / one).read_bytes() for one in RETIRED_IN_TEAM[TURN_DOC]):
        placed(target, data)                            # an earlier version's law: the team's, replaced
        print(f"pp-team: {TEAMS}/{name}/{TURN_DOC} replaced by the overlay of the turn -- it was the law of an "
              "earlier version", file=sys.stderr)
    elif target.read_bytes() != data:
        print(f"pp-team: {TEAMS}/{name}/{TURN_DOC} kept -- it is the owner's own: the team's runs ask for the form "
              f"`{ACT_FORMAT}` only if it carries `output: {ACT_FORMAT}`", file=sys.stderr)
    if entries:
        target, data = directory / IDLE, (here / IDLE_SOURCE).read_bytes()
        if target.is_file() and target.read_bytes() != data:
            print(f"pp-team: {TEAMS}/{name}/{IDLE} kept -- not the team's: the owner's own stays", file=sys.stderr)
        elif not target.is_file():
            placed(target, data)
    for document, data in planned.items():
        if data is None:
            (directory / document).unlink(missing_ok=True)
            print(f"pp-team: {TEAMS}/{name}/{document} removed -- no line names it any more", file=sys.stderr)
        else:
            placed(directory / document, data)
    roles = directory / ROLES_DIR
    if roles.is_dir() and not any(roles.iterdir()):
        roles.rmdir()                                  # no document of a role left
    placed(directory / sheet_name(name), sheet_of(root, conductor, name, team, launch, profiles))
    own = team_document(name, entries, team.intention + "\n" if team.intention else "",
                        [document_name(name), *served_of(conductor, directory, name)])
    placed(directory / document_name(name), own)
    return {document_name(name): hashlib.sha256(own).hexdigest()[:12],
            **{one: hashlib.sha256(data).hexdigest()[:12] for one, data in planned.items() if data is not None}}


def entry_of(root: Path, name: str, run: str) -> str:
    """-> the document the wake-up of the team under the run `run` plays: the last wake-up of the
    team launched under that key and not ended -- its intent's run, its `wake-launched`, else its
    tag at the house's `messages.jsonl` (an opening's first exchange plays before the tick writes
    `wake-launched`) --; its task's ceremony names its entry, any other task `do`'s; no entry, no
    such wake-up, no journal: the neutral `TEAM-IDLE.md`. Nothing written, no lock."""
    journal = journal_of(root, name)
    if not journal.is_file():
        return IDLE
    state = state_of(journal)
    standing = open_intents(state)
    under = run_under(state, standing, run)
    if not under:
        under = opening_under(state, standing, run, lines_of(record_of(root, MESSAGES)))
    if not under:                                  # an opening under way: the house opened the run before any
        waiting = [one for one in standing if one.body.run is None]   # record names it -- the agent's slot says it
        held = slots_held([agent_meta(root, path_of_intent(state, one)) for one in waiting], run)
        under = [one for one, slotted in zip(waiting, held) if slotted]
    if not under:
        return IDLE
    return entry_chosen(state, under)


def member_judged(root: Path, conductor, ident: str) -> tuple[str, str, dict]:
    """-> (team, member, the team's `team-started`) a vector `team-member:<team>/<member>` names, judged for the
    instance and the run that ask -- each defect refused by its code, read-only: `team-unknown` (no `TEAM.md`),
    `team-not-started`, `member-unknown` (a member the season under way does not know), `member-foreign` (the instance
    calling, `PP_HOME`, is not the agent that plays the member), `root-foreign` (the run's root of documents is not
    the team's directory)."""
    name, _, member = ident.strip().partition("/")
    try:
        vector_team(name, bool(name) and team_doc(root, name).is_file())
        started = state_of(journal_of(root, name)).season.started
        vector_started(name, started)
        agents = started.body.agents or {}
        vector_member(name, member, agents)
        calling = caller()
        vector_caller(name, member, agents,
                      calling is not None and calling.resolve() == agent_meta(root, agents[member]).resolve())
        documents = run_documents(conductor, calling)
        vector_root(name, documents, bool(documents) and Path(documents).resolve() == team_root(root, name).resolve())
    except Declined as declining:
        refuse(str(declining))
    return name, member, started


def declared_face(root: Path, conductor, name: str, team: dict, rendering: dict | None = None,
                  planned: dict[str, bytes | None] | None = None, opened: dict | None = None) -> dict:
    """-> the team as it plays (`team_played`), what the next start writes: the members and
    their paths in the order declared -- each with `born` (an instance stands at its path), the `packages` a season
    without `--package` gives it (`season_set`: the packages the team requires on, every other pin off), born or not,
    and its `description` as the members' sheet says it (`description_of`) --,
    the root, the edges, the principals, the limits, the schedule, the ceremonies' lines -- `TEAM.md`'s own, else
    what its preset's form and defaults make --, the entries, the work, the season a start without a flag opens
    (`season`: `{launch, limits, packages, profiles, work}`, None when SEASON.md is refused), the role keys in the
    order declared (`[{role, members}]`, each member's keys on its line), the lines of `documents:` by key, the
    team's and the season's (`documents`: `[{key, team, season}]`, None when the documents are refused), each
    member's VIEW as the next start renders it (`view_of`: `[{member, roles, documents}]`), the preset named
    (`{template, origin, values: [{name, value, from}]}`, `from` `team` or `default`; None without one) and the values
    the documents apply (`values`, `[{name, value, from}]`) -- the owner's word and the digest left to the text."""
    silent = [{"name": name, "on": state == "on"} for name, state in set_of(season_set(root, conductor, {})).items()]
    template = template_description(root, conductor)
    return {"agents": [{"member": member, "path": path,
                        "born": conductor.instance.is_instance(agent_meta(root, path)), "packages": silent,
                        "description": description_of(root, conductor, path, template),
                        "roles": [key for key, members in team.roles.items() if member in members]}
                       for member, path in team.agents.items()],
            "root": team.root, "reports": team.reports, "principals": team.principals,
            "limits": team.limits, "schedule": team.schedule,
            "ceremonies": [one.text for one in team.ceremonies], "entries": team.entries,
            "work": (opened or {}).get("work"),
            "season": None if opened is None else {"launch": opened["launch"], "limits": opened["season"],
                                                   "packages": opened["packages"], "profiles": opened["profiles"],
                                                   "work": opened["work"]},
            "roles": [{"role": key, "members": members} for key, members in team.roles.items()],
            "documents": None if rendering is None else rendering["lines"],
            "views": [{"member": member, "roles": [key for key, members in team.roles.items() if member in members],
                       "documents": view_of(conductor, team_root(root, name), name, team.roles,
                                            (rendering or {}).get("documents") or [], member, planned,
                                            document_planned)}
                      for member in team.agents],
            "template": team.template,
            "values": None if rendering is None else rendering["values"]}


def sheet_of(root: Path, conductor, name: str, team: dict, launch: dict, profiles: dict) -> bytes:
    """-> `TEAM-<name>-members.md`: no front matter, one table, one row per member in the declaration's order --
    whom it reports to (`reports:`), its role keys when the team declares any (`roles:`, joined by a comma, `—` for
    none), the model and the effort of its profile, else of the season's launch, else the agent's default, its
    description (`description_of`). A team without a role key keeps the five columns."""
    above = {child: str(one.get("to")) for one in team.reports for child in one.get("from") or []}
    template = template_description(root, conductor)
    cell = lambda text: " ".join(str(text).split()).replace("|", "\\|")
    rows = []
    for member, path in team.agents.items():
        profile = profiles.get(member) or {}
        model = profile.get("model") or launch.get("model") or "agent default"
        effort = profile.get("effort") or launch.get("effort") or "default"
        keys = [key for key, members in team.roles.items() if member in members]
        held = f" {cell(', '.join(keys) or '—')} |" if team.roles else ""
        rows.append(f"| {cell(member)} | {cell(above.get(member, '—'))} |{held} {cell(model)} | {cell(effort)} | "
                    f"{cell(description_of(root, conductor, path, template))} |")
    roles_head, roles_rule = (" roles |", "---|") if team.roles else ("", "")
    return (f"# The members of {name}\n\n| member | reports to |{roles_head} model | effort | description |\n"
            f"|---|---|{roles_rule}---|---|---|\n" + "\n".join(rows) + "\n").encode("utf-8")
