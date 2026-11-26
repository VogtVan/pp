"""The `declaration` domain, layer `acts`: a declaration read, then judged -- the two steps chained.

A definition belongs here when it chains a store's reading and a rule's judgement for a verb, or calls the acts and the
stores of other domains to do so: the name a team is shown by and its description, read from `TEAM.md` and judged, or
the directory's name and None when the file cannot be read; the team as it plays -- `TEAM.md` read, its preset and its
documents read, its values applied, then judged whole, the face that renders its intention given to the judge --,
refused when `TEAM.md` is missing; the declaration as it stands -- `TEAM.md`, `SEASON.md` or the text `declare` is about
to write -- judged by `start`'s own checks, with its gap to the last start; the members a `TEAM.md` declares with their
descriptions; the paths of its agents; the season's flags of a `declare --season`, judged by `start`'s own judges
(`launch_judged`). Only verbs and other acts call it; no store, face or rule does. It may use the lower layers of any
domain.

`template:` of `TEAM.md` NAMES a TEAM preset the house sees, `<directory>/<name>` -- a template that carries `form:`,
`members:` or `reports:` --, and `values: |` gives the values the preset and the documents declare, one
`<name> = <value>` per line (a value with a default may be left out; `daily =`, left empty, takes the daily out).
The key is optional: without it nothing is chosen in silence, the team is what `TEAM.md` writes. With it, every
`start` reads the preset again and the team PLAYS as both make it: the preset's `form:` makes the edges when
`TEAM.md` writes no `reports:`, the root when it writes no `root:` (the first member; a root written is the form's
head), and adds the daily to `ceremonies:` -- the value `daily` its rhythm, two members or more reporting to the
root in the edges as the team plays, `TEAM.md`'s own when it writes `reports:` -- unless `TEAM.md` writes a
ceremony named `daily`; the preset's `budget:`, `launches:`, `timeout:` and
`schedule:` are the defaults of `TEAM.md`'s own keys. A preset without `form:` makes no edge and no root:
`TEAM.md` writes its own. A member added under `agents:` or a preset changed takes effect at the next `start`,
no edge written; `declaration` says the gap first. One function reads a declaration (`team_played`): `start`,
`declaration`, `declare`, the roster, the members `status` and `delete` say. Kept by every season at
`team-started.template` (`{template, origin}`; no key without a preset), the values `TEAM.md` applies at
`team-started.values` (`{name: value}`).
"""
from __future__ import annotations

from pathlib import Path

from house.model import Declined
from house.rules import journal_of, team_doc, team_root
from house.store import owner_of, refuse
from template.rules import values_applied
from template.faces import intention_rendered
from declaration.rules import description_shown, judged, name_shown
from declaration.store import front_read, team_read
from season.rules import gap
from season.store import changed_since_start
from season.acts import season_gap, season_opened
from documents.rules import documents_gap
from documents.store import description_of
from documents.acts import directory_judged, documents_of, documents_planned, entries_judged
from journal.store import state_of


def team_name(root: Path, conductor, name: str) -> str:
    """-> the name a team is SHOWN by: the `name:` of its `TEAM.md`, read at every call (`front_read`) and judged
    (`name_shown`) -- the directory's name, the team's identity, when the key is absent or the file cannot be read.
    Nothing keyed by it: a rename moves no journal, no relaunch entry, no file."""
    try:
        front = front_read(conductor, team_doc(root, name))
    except (Declined, OSError):
        return name
    return name_shown(front, name)


def team_description(root: Path, conductor, name: str) -> str | None:
    """-> what a team DOES, as its `TEAM.md` says it under `description:`, read at every call (`front_read`) and never
    written to the journal: a description rewritten is read at the next call, without a start. None when the key is
    absent, the file cannot be read or the description is not one judged line (`description_shown`; `judged` refuses
    it at the start)."""
    try:
        front = front_read(conductor, team_doc(root, name))
    except (Declined, OSError):
        return None
    return description_shown(front)


def team_played(root: Path, conductor, name: str, text: str | None = None) -> dict:
    """-> the team as it PLAYS: what `teams/<name>/TEAM.md` and the preset it names make together, judged whole
    (`judged`) -- the ONE reader of a declaration: `start`, `declaration`, `declare` (the `text` it is about to write)
    and every face that says a team's members or its root. `template:`, `documents:` and `values:` are read by
    `documents_of`, the reader `SEASON.md` shares; the team's values are judged on what its preset and its documents
    declare (`values_applied`). The preset's form makes the edges, the root and the daily `TEAM.md` does not write, its
    limits and `schedule:` are the defaults of `TEAM.md`'s own keys (`shaped`), its intention is rendered for the team
    (`intention_rendered`). Without `template:` nothing is chosen in silence: the team is what `TEAM.md` writes, its
    intention empty. DECLINES by name: `team-invalid` (a front matter the engine cannot read, a `values:` or
    `documents:` line of another form, a form given members it cannot hold), `template-unknown`, `template-invalid`,
    `document-unknown`, `value-unknown`, `value-missing`, `value-undeclared` (a hole of the intention nothing
    declares), and the judge's own."""
    path = team_doc(root, name)
    front, data = team_read(conductor, path, text)
    read = documents_of(root, conductor, team_root(root, name), front, path, "team-invalid")
    applied = values_applied(read["declared"], read["given"], path, "what TEAM.md names", "team")
    return judged(conductor, front, data, path, name, owner_of(root, conductor),
                  {"template": read["template"], "applied": applied, "read": read}, intention_rendered)


def declared(root: Path, conductor, name: str) -> dict:
    """-> the team as it plays (`team_played`), read WHOLE and judged before anything is written: a defect refuses."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    try:
        return team_played(root, conductor, name)
    except Declined as declining:
        refuse(str(declining))


def declaration_read(root: Path, conductor, name: str, doc: str | None = None, season: str | None = None) -> dict:
    """-> a team's declaration as it stands -- `doc` and `season`: a text of `TEAM.md`, of `SEASON.md`, read in the
    file's place, what `declare` is about to write --, judged by `start`'s own checks in `start`'s order, the two
    files TOGETHER, and never refused: `{team` (as it plays, None when refused), `checks` (each check that RAN, in
    order, `{check: its refusal, None when it passes}`: `team` the team as it plays; then, the team read, `season`
    the season a start without a flag opens, `entries` an entry nothing resolves, `documents` the documents of both files and those that mount; then, the
    documents passed, `directory` the team's directory against the plan -- a check that could not run, the one
    before it failing, is absent), `refusal` (the first refusal of `checks`, the one `start` would write; None
    without one), `started` (the last `team-started`, None before one), `rendering`, `planned` and `opened` (the
    documents rendered in memory, the plan of the directory and the season; None when not judged), `pending` (the gap
    to the last start, key by key: `gap`, `documents_gap`, `season_gap`; `[]` before a start, None when `TEAM.md` is
    refused), `changed}` (the file differs from the one the last start read). Nothing written, no lock, never a
    tick: the ONE reading `declaration` says and `declare` judges its write by."""
    team, checks = None, {}

    def ran(check: str, judge):
        """-> what `judge` returns, None when it declines; `checks[check]` its refusal, None when it passes."""
        try:
            found = judge()
        except Declined as declining:
            checks[check] = str(declining)
            return None
        checks[check] = None
        return found

    team = ran("team", lambda: team_played(root, conductor, name, doc))
    state = state_of(journal_of(root, name))
    started = state.season.started
    rendering, planned, opened = None, None, None
    if team is not None:
        opened = ran("season", lambda: season_opened(root, conductor, name, team, {}, [], {}, season))
        ran("entries", lambda: entries_judged(root, conductor, name, team))
        found = ran("documents", lambda: documents_planned(root, conductor, name, started, team, season,
                                                           directory=False))
        if found is not None:
            rendering, planned = found
            ran("directory", lambda: directory_judged(root, name, started, team, planned))
    pending = None if team is None else ([] if started is None else gap(started, team))
    if pending is not None and started is not None and rendering is not None:
        moved = documents_gap(name, started, rendering)
        pending += [moved] if moved else []
    if pending is not None and started is not None and opened is not None:
        pending += season_gap(root, conductor, started, opened)
    return {"team": team, "refusal": next((said for said in checks.values() if said is not None), None),
            "checks": checks, "started": started, "stopped": state.season.stopped, "rendering": rendering, "planned": planned,
            "opened": opened,
            "pending": pending, "changed": started is not None and changed_since_start(root, name, started)}


def declared_members(root: Path, conductor, name: str, template: str) -> list[dict]:
    """-> `[{member, path, description}]`: the members a team's `TEAM.md` declares, in its order, each with what the
    members' sheet says of it (`description_of`: `no description` when its `MEMBER.md` says none); [] when the
    declaration cannot be read or is refused -- by its judge, or by a template the house lays wrong."""
    try:
        team = team_played(root, conductor, name)
    except (Declined, OSError, SystemExit):
        return []
    return [{"member": member, "path": at, "description": description_of(root, conductor, at, template)}
            for member, at in team.agents.items()]


def declared_paths(root: Path, conductor, name: str) -> set[str]:
    """-> the paths of the agents a team's `TEAM.md` declares; none when it cannot be read or judged."""
    try:
        return set(team_played(root, conductor, name).agents.values())
    except (Declined, OSError, SystemExit):
        return set()


def launch_judged(root: Path, conductor, name: str, launched: dict, text: str) -> None:
    """`start`'s judges (`season_opened`) on the season's flags of a `declare --season`, over `text`, SEASON.md as
    the call writes it without them: what `start` refuses of them refuses, by its code. A `TEAM.md` or a `SEASON.md`
    that `start` refuses already leaves the flags judged on their own, over no SEASON.md -- or unjudged, TEAM.md
    refused: the write goes on, as `declare` writes beside a refusal it did not cause."""
    try:
        team = team_played(root, conductor, name)
    except Declined:
        return
    flagged = (launched["asked"], launched["packages"], launched["profiles"])
    try:
        season_opened(root, conductor, name, team, *flagged, text=text)
        return
    except Declined as declining:
        refused = str(declining)
    try:
        season_opened(root, conductor, name, team, {}, [], {}, text=text)
    except Declined:
        try:
            season_opened(root, conductor, name, team, *flagged, text="")
        except Declined as declining:
            refuse(str(declining))
        return
    refuse(refused)
