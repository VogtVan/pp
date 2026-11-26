"""The `declaration` domain, layer `verbs`: the verbs that write or read a declaration.

A definition belongs here when it plays such a verb or serves its command line: it reads the verb's arguments, writes
`TEAM.md` or `SEASON.md`, prints a declaration with its verdict and its gap, answers a verb that is retired, or
refuses with the usage. At a birth, `declare` reads the preset `--template` names first, then has the rule
`declare_changes` judge the changes, and refuses what it declines with the same text. A verb is where the skill meets
its caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from house.model import Declined, RETIRED_FLAGS, USAGE
from house.rules import journal_of, team_doc, team_root
from house.store import locks, machine_house, named_team, placed, refuse
from house.verbs import flags
from template.model import SEASON_DOC
from declaration.model import DECLARATION_FLAGS, DECLARE_FLAGS, DECLARE_MANY, DECLARE_PAIRS, DECLARE_TEAM, TICK_LOCK
from template.rules import key_stands, values_written
from template.store import text_handed
from template.acts import template_of, templates_of
from declaration.rules import declare_changes
from declaration.store import candidate_read
from declaration.acts import declaration_read, launch_judged, team_name
from season.rules import season_changes
from season.faces import in_season
from season.verbs import season_declared
from documents.acts import declared_face
from net.store import call_wait
from journal.faces import harmless
from journal.store import state_of


def asked_declare(rest: list[str], launched: bool = False) -> dict:
    """-> `declare`'s flags (`DECLARE_FLAGS`): `--season` and `--json` bare; a flag of `DECLARE_MANY` the list of what
    it was given -- `--member` a `(name, path)`, `--value` a `(name, value)` cut at its first `=`, `--role` a `(key,
    [members])`, its members the words up to the next flag, the others a word --; any other flag once, None when not
    given. Refused before anything is read: `flag-retired` (a bound of before, `--compose`, `--no-compose`); the usage
    for a flag `declare` does not take, a flag short of its words, a flag given twice, a `--value` without `=`, a
    `--document` without a key and a document, a flag of
    `TEAM.md` alone (`DECLARE_TEAM`) under `--season`, and a call that names no key -- `launched`: the season's flags
    of `start` named one (`season_declared`); `team-invalid` for a line
    break in a word a line of the file is made of, and for one name given twice to a flag or given to a flag and to
    its contrary (`DECLARE_PAIRS`): a call says each line once."""
    found: dict = {flag: [] if flag in DECLARE_MANY else False if words == 0 else None
                   for flag, words in DECLARE_FLAGS.items()}
    given: set[str] = set()
    index = 0
    while index < len(rest):
        word = rest[index]
        flag = word[2:] if word.startswith("--") else ""
        if word in RETIRED_FLAGS:
            refuse(f"flag-retired -- `{word}`: the bounds count launches -- say `{RETIRED_FLAGS[word]}`.")
        if word in ("--compose", "--no-compose"):
            now = "--no-document <key>" if word == "--no-compose" else '--document "<key>|all <document> ..."'
            refuse(f"flag-retired -- `{word}`: a team names its documents by key -- say `{now}`.")
        if flag not in DECLARE_FLAGS or (flag in given and flag not in DECLARE_MANY):
            refuse(USAGE)
        given.add(flag)
        words = DECLARE_FLAGS[flag]
        if words is None:                                  # a role: its key, then its members up to the next flag
            last = next((at for at in range(index + 1, len(rest)) if rest[at].startswith("--")), len(rest))
            said = rest[index + 1:last]
        else:
            last = index + 1 + words
            said = rest[index + 1:last]
            if len(said) != words:
                refuse(USAGE)
        if not said and words != 0:
            refuse(USAGE)
        if flag not in ("description", "body-file") and any("\n" in one or "\r" in one for one in said):
            refuse(f"team-invalid -- `--{flag}`: one line, no line break.")
        if flag == "value":
            named, equal, value = said[0].partition("=")
            if not equal or not named.strip():
                refuse(USAGE)
            found[flag].append((named.strip(), value.strip()))
        elif flag == "document":
            if len(said[0].split()) < 2:
                refuse(USAGE)
            found[flag].append(" ".join(said[0].split()))
        elif flag == "report":                         # an edge: its members, then the one they report to
            sources, arrow, target = said[0].partition("->")
            if not arrow or not sources.split() or len(target.split()) != 1:
                refuse(f"team-invalid -- `--report {said[0]}`: one edge, `<member>... -> <member>`.")
            found[flag].append((target.strip(), f"{' '.join(sources.split())} -> {target.strip()}"))
        elif flag == "member":
            found[flag].append((said[0], said[1]))
        elif flag == "role":
            found[flag].append((said[0], said[1:]))
        elif flag in DECLARE_MANY:
            found[flag].append(said[0])
        else:
            found[flag] = True if words == 0 else said[0]
        index = last
    if found["season"] and any(flag in given for flag in DECLARE_TEAM):
        refuse(USAGE)
    if not given - {"season", "json"} and not launched:    # no key named: nothing to write
        refuse(USAGE)
    named_by = {"value": lambda one: one[0], "document": lambda one: one.split()[0], "member": lambda one: one[0],
                "role": lambda one: one[0], "report": lambda one: one[0]}
    for flag, contrary in DECLARE_PAIRS:
        names = [named_by[flag](one) for one in found[flag]]
        twice = next((one for one in names if names.count(one) > 1), None)
        if twice is None:
            twice = next((one for one in found[contrary] if found[contrary].count(one) > 1), None)
            flag = contrary if twice is not None else flag
        if twice is not None:
            refuse(f"team-invalid -- `--{flag} {twice}` given twice: a call says each line once.")
        both = next((one for one in names if one in found[contrary]), None)
        if both is not None:
            refuse(f"team-invalid -- `--{flag} {both}` and `--{contrary} {both}`: a call writes a line or takes it "
                   "out, never both.")
    return found


def declare_verb(rest: list[str]) -> int:
    """`team declare <name> [--season] …`: the ONE verb that WRITES a team's values, the team born or standing --
    `teams/<name>/TEAM.md`, or `teams/<name>/SEASON.md` under `--season` (the season's documents: `--template`,
    `--value`, `--document`, `--body-file`; and the season's flags of `start`, read by `season_declared`, judged by
    `launch_judged` and written by `season_changes`, as `start` writes them; the team must stand, `team-unknown`
    otherwise). Without the file, it is
    written from the flags; with it, the keys the flags name are written and they alone (`declare_changes`,
    `values_written`): every other key, every other line of a block and the body stay at their bytes --
    `--body-file` replaces the body, the owner's word, by the file's text -- `--body-file -` by standard input's. The verb REFUSES a write that makes one of
    `start`'s checks fail when that check passed before it: the declaration is read as it stands, then as it would
    stand with the text to write, by `start`'s own checks in `start`'s order (`declaration_read`: the team, the
    season, the entries, the documents, the directory). A check that passed at the first reading and fails at the second refuses, and nothing is
    written -- at a birth, every refusal does. A check that already failed before the call, or that could not run
    because an earlier one failed, never stops the write: the verb writes, and its verdict names the refusal `start`
    would give -- so a `SEASON.md` written under a `TEAM.md` that is refused is written unjudged. Both files are
    written OFF SEASON alone -- before a first start, or after `team stop` --: in season the verb refuses
    `season-running`, naming `team stop`, nothing written. Written under the team's `tick.lock`, waited
    within `call_lock_wait` (`team-busy` beyond): a tick never reads a file half written, and two calls write one
    after the other; a birth is judged once before the lock, so that a refusal leaves no record of a team that is not.
    No event is written to the journal, no document is rendered, nobody is launched -- what is written applies at
    the next `team start`. Says the file, the keys written (`written`: the keys
    whose text changed in the file, in the order a birth lays them, `body` last -- none for a call that changes
    nothing), `declaration`'s verdict -- `ok`, or the refusal of a check the call did not break -- and the gap to the last start; under `--json` ONE object `{team, file, written, verdict: {ok, refusal}, pending}`.
    Written in the HOUSE (`machine_house()`), whatever instance calls: an agent that borrows the machine writes its
    house's team, never one of its own."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    rest, launched = season_declared(rest)
    asked = asked_declare(rest, launched=bool(launched and (launched["asked"] or launched["packages"]
                                                            or launched["profiles"])))
    season = asked["season"]
    doc = team_doc(root, name)
    path = team_root(root, name) / SEASON_DOC if season else doc
    if season and not doc.is_file():
        refuse(f"team-unknown -- no {doc}: `team declare {name}` writes the team first, then its season.")
    body = None if asked["body-file"] is None else text_handed(asked["body-file"])   # `-`: what a form hands over
    if asked["body-file"] is not None and body is None:
        refuse(f"team-invalid -- `--body-file {Path(asked['body-file'])}`: no such file.")
    if body is not None:
        body = "" if not body.strip() else body if body.endswith("\n") else body + "\n"

    def made() -> tuple[str | None, str | None, list[str], dict]:
        """-> (the file's text, None when it stands not, the text as the flags make it -- None when they leave a
        file that stands not without a key and without a body --, the keys whose text changes, the declaration as
        it would stand, `declaration_read`), judged: a check that passed on the declaration as it stands and fails
        with the text to write refuses -- at a birth, every check that fails --; in season, `season-running`."""
        running = in_season(name, state_of(journal_of(root, name)), f"writing {path.name}")
        if running:
            refuse(running)
        before = path.read_bytes().decode("utf-8") if path.is_file() else None
        born = before is None and not season
        template = None
        if born and asked["template"] is not None:     # a birth: the preset read, then the changes judged
            try:
                template = template_of(conductor, templates_of(root, conductor), asked["template"], "`--template`",
                                       "team")
            except Declined as declining:
                refuse(str(declining))
        try:
            changes, keys = declare_changes(name, asked, template)
        except Declined as declining:
            refuse(str(declining))
        if launched:                                   # the season's flags of `start`: judged, then its one writer
            try:
                stood = values_written(conductor, before or "", changes, body)
            except conductor.Refusal as refusal:
                refuse(f"season-invalid -- {path}: {refusal}")
            launch_judged(root, conductor, name, launched, stood)
            more = season_changes(launched["asked"], launched["packages"], launched["profiles"])
            changes, keys = changes + more, keys + [key for key, _ in more]
        try:
            after = values_written(conductor, before or "", changes, body)
        except conductor.Refusal as refusal:
            refuse(f"{'season' if season else 'team'}-invalid -- {path}: {refusal}")
        stood = declaration_read(root, conductor, name)["checks"] if doc.is_file() else None
        read = declaration_read(root, conductor, name, **{"season" if season else "doc": after})
        broken = next((said for check, said in read["checks"].items() if said is not None
                       and (stood is None or stood.get(check, "") is None)), None)
        if broken is not None:
            refuse(broken)
        if before is None and after == values_written(conductor, "", []):
            after = None                               # contraries alone on a file that stands not: none is born
        moved = [key for key in (*keys, *(["body"] if body is not None else []))
                 if key_stands(conductor, before, key) != key_stands(conductor, after, key)]
        return before, after, moved, read

    if not doc.is_file():                              # a birth: judged before the lock lays the team's records
        made()
    lock = locks(conductor)
    lease = lock.acquire(journal_of(root, name).parent / TICK_LOCK, wait=call_wait(root, conductor))
    if lease is None:
        refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing written, replay once "
               "it has played.")
    try:
        before, after, keys, read = made()
        if after != before:
            placed(path, after.encode("utf-8"))
    finally:
        lock.release(lease)
    shown = str(path.relative_to(root.parent))
    verdict = {"ok": read["refusal"] is None, "refusal": read["refusal"]}
    if asked["json"]:
        print(json.dumps({"team": name, "file": shown, "written": keys, "verdict": verdict,
                          "pending": read["pending"]}, ensure_ascii=False))
        return 0
    started = read["started"]
    gap_said = (f"not started -- start it: team start {name} --message <text>" if started is None else
                f"pending until a new start (#{started.id}): {', '.join(one['key'] for one in read['pending'])}"
                if read["pending"] else f"nothing pending since the start (#{started.id})")
    print(f"pp-team: {shown} " + (f"written · {', '.join(keys)}" if keys else "as it stood · nothing written")
          + (" · verdict ok" if read["refusal"] is None else f" · verdict refused: {read['refusal']}") + f" · {gap_said}")
    return 0


def new_retired(rest: list[str]) -> int:
    """`new`: the verb of before -- refuses `verb-retired`, naming the verb that took its place."""
    refuse("verb-retired -- `new` is gone: `team declare <name> --template <directory>/<name> "
           "[--member <name> <path>]...` writes a team's values, the team born or standing -- then `team start <name>`.")


def declaration_verb(rest: list[str]) -> int:
    """`team declaration <name> [--json] [[--season] --text-file <path>|-]`: the team's declaration READ -- `TEAM.md`
    whole, start's own judge's verdict (`ok`, or the refusal `start` would write: said, never refused) and its gap to
    the last start, key by key (`declaration_read`). Under `--text-file`, a CANDIDATE text -- `-`: standard input --
    read in the place of `TEAM.md`, or of `SEASON.md` under `--season`, and said as if it were written: its text, its
    verdict, `declared` and each member's view; `--season` without it is the usage. Nothing written, no lock, never a
    tick. Read in the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, DECLARATION_FLAGS)
    as_json = asked["json"]
    if asked["season"] and asked["text-file"] is None:
        refuse(USAGE)
    candidate = candidate_read(asked)
    path = team_doc(root, name)
    if not path.is_file():
        refuse(f"team-unknown -- no {path}: the owner declares the team there.")
    data = candidate.encode("utf-8") if candidate is not None and not asked["season"] else path.read_bytes()
    read = declaration_read(root, conductor, name, **({} if candidate is None else
                                                      {"season" if asked["season"] else "doc": candidate}))
    team, refusal, started, rendering = read["team"], read["refusal"], read["started"], read["rendering"]
    planned, opened, pending, changed = read["planned"], read["opened"], read["pending"], read["changed"]
    shown_path = str(path.relative_to(root.parent))
    text = data.decode("utf-8")
    season = team_root(root, name) / SEASON_DOC
    season_face = None
    if season.is_file() or (candidate is not None and asked["season"]):
        said = candidate.encode("utf-8") if candidate is not None and asked["season"] else season.read_bytes()
        season_face = {"path": str(season.relative_to(root.parent)), "text": said.decode("utf-8"),
                       "digest": hashlib.sha256(said).hexdigest()[:12]}
    if as_json:
        print(json.dumps({"team": name, "name": team_name(root, conductor, name),
                          "description": None if team is None else team.description, "path": shown_path, "text": text,
                          "digest": hashlib.sha256(data).hexdigest()[:12],
                          "verdict": {"ok": refusal is None, "refusal": refusal},
                          "started": None if started is None else {"at": started.at, "id": started.id,
                                                                    "digest": started.body.digest,
                                                                    "state": "stopped" if read["stopped"] else "running"},
                          "changed": changed, "pending": pending, "season": season_face,
                          "declared": None if team is None else declared_face(root, conductor, name, team, rendering,
                                                                               planned, opened)},
                         ensure_ascii=False))
        return 0
    print(f"pp-team: {shown_path}")
    print(harmless(text.rstrip("\n")))
    if season_face is not None:
        print(f"pp-team: {season_face['path']}")
        print(harmless(season_face["text"].rstrip("\n")))
    print("verdict ok" if refusal is None else f"verdict refused: {refusal}")
    named = team.template if team is not None else None
    if named:
        print(f"template {named['template']} ({named['origin']})"
              + "".join(f" · {one['name']} = {one['value']}" for one in named["values"]))
    for one in (rendering or {}).get("lines") or []:
        print(f"documents {one['key']}: " + " ".join([*one["team"], *one["season"]]))
    for key, members in (team.roles if team is not None else {}).items():
        print(f"role {key}: {', '.join(members) if members else 'no member'}")
    if started is None:
        print("not started")
    elif pending:
        print(f"pending until a new start (#{started.id}):")
        for one in pending:
            print(f"  {one['key']}: {json.dumps(one['started'], ensure_ascii=False)} -> "
                  f"{json.dumps(one['declared'], ensure_ascii=False)}")
    elif changed:
        print(f"changed since the start (#{started.id}): the body alone, served already")
    elif team is not None:
        print(f"unchanged since the start (#{started.id})")
    return 0
