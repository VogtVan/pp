"""Scenario `team-door` -- 5 case(s): the TEAMS space, the door of the team package -- offered at TURN by
`overlays/TURN.md`, opened on its welcome `TEAMS-BOARD` once, closed on `-close` -- and where it writes: in the
house, wherever it is opened from. One house pinning `agent` and `team` alone, no `authoring` nor `plan`.
- (a) the door: a team `duo` declared in the house; `TEAMS` stands among TURN's offers; `-open TEAMS` enters the
  space on `TEAMS-BOARD`, its readings `team-board` -- `duo`'s line with its members, each `no description` -- and
  `team-templates` -- the team presets `teams/<name>` among them -- served to an INFER in the form `team-board` (words); the next block is
  the space's own WORK under its laws (TS1 to TS4), `TEAMS` the one space open; `-close` gives back the root it was
  opened from, no space open
- (b) written in the house from an agent: from the instance of `agents/pa`, `team declare crew --template teams/solo
  --description …` writes `teams/crew/` in the house, its `description:` read back by `status --json` with its
  members; a description of two lines refuses `team-invalid`, nothing written; the team started from the house,
  `team post crew --every … --description …` from the agent writes its `recurrence` in the house's journal, its
  description with it; from the agent still, `declaration crew --json` reads the house's `TEAM.md` (verdict ok, its
  description), and `pause`, `resume` then `stop crew --recurrence R1` write `recurrence-paused`, `recurrence-resumed`
  and `recurrence-stopped` in the house's journal; the agent's workspace outside its machine identical before and
  after, no team's records under its instance
- (c) the author's reference: the space's own block, once `-open TEAMS` has played its welcome, carries the reading
  of `TEAMS_CHEATSHEET.md` beside the one of `TEAM_WORK.md`, each a body of its own -- served, never its wording read
- (d) a team set up as the space teaches it: the fenced blocks of `procs/TEAMS.md`, each line a `team` command; the
  first, played line by line from the agent, declares a team, its members and role keys (`team declare`), then its
  season's contract (`team declare --season`) and reads its declaration -- every line rc 0, `TEAM.md` and `SEASON.md`
  in the house, the verdict ok, two role keys, the documents of a role in the views of its members alone -- two views,
  two sets --, no `team-started` (no journal); no line of any block plays `team start` -- the commands played,
  never a sentence read
- (e) a team changed as the space teaches it: the second block, played on the team (d) declared -- every line rc 0, a
  member added to `agents:` and to a role key, the members of (d) still there, `SEASON.md` at its bytes, the
  verdict ok, the document of the role in the added member's view, still no `team-started`
"""
from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

from conductor import Conductor, Refusal, compiling, discovery, instance, reading
from conductor.core import language
from tests.harness import INSTANCE, cli, pin_step, stepped, support

T = support(__file__, "team")

DESCRIBED = "Reviews the open work every morning."
TEAM_SAID = "Keeps the house's work moving."
LAWS = {"TS1", "TS2", "TS3", "TS4"}
SPACE = Path(__file__).resolve().parents[2] / "procs" / "TEAMS.md"


def tree(root, skipped) -> dict:
    """-> every file under `root` but those under `skipped`, by its relative path, with its bytes."""
    return {str(one.relative_to(root)): one.read_bytes() for one in sorted(root.rglob("*"))
            if one.is_file() and skipped not in one.parents}


def taught(path: Path) -> list[list[list[str]]]:
    """-> the fenced blocks of a document whose every line is a `team` command, each line split as a shell would."""
    blocks = re.findall(r"^```[a-z]*\n(.*?)^```", path.read_text(encoding="utf-8"), re.S | re.M)
    lines = [[shlex.split(one) for one in block.splitlines() if one.strip()] for block in blocks]
    return [block for block in lines if block and all(one[:1] == ["team"] for one in block)]


def roles_seen(read: dict) -> tuple[set, dict]:
    """-> (the role keys a `declaration --json` declares, each member's documents its vector mounts)."""
    declared = read.get("declared") or {}
    keys = {one.get("role") for one in declared.get("roles") or []}
    views = {one.get("member"): [doc.get("document") for doc in one.get("documents") or [] if doc.get("by") == "vector"]
             for one in declared.get("views") or []}
    return keys, views


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    pin_step(h.house)
    h.declare("duo", T.PAIR.format(m="dm", w="dw"))

    # --- (a) the door: offered, opened on its welcome, closed ----------------------------------------
    member = discovery.instance_member(h.engine)
    conductor = Conductor(member, h.engine, "t")
    before = conductor.start(conductor.boot("BOOT.md"))
    offered = "TEAMS" in {one.name for one in compiling.effective(h.house, reading.read(instance.resolve(h.house, "TURN.md")))[1]}
    welcome = work = back = None
    seen, opened, after, refused, titles, bodies = [], [], ["?"], "", [], {}
    try:
        conductor = Conductor(member, h.engine, "t")
        welcome = conductor.open("TEAMS", route=conductor.route("TEAMS"))
        fresh = lambda: Conductor(member, h.engine, "t")   # noqa: E731
        work = stepped(fresh, text="the board, in tables")   # the welcome is said to the principal: its print call
        while work is not None and work.document != "TEAMS" and len(seen) < 3:   # the welcome's frame closes first
            seen.append(work.document)
            work = stepped(fresh)
        titles = [title for title, _ in (getattr(work, "payloads", ()) or ())]
        bodies = {title: text for title, text in (getattr(work, "payloads", ()) or ())}
        opened = Conductor(member, h.engine, "t").spaces_open()
        back = Conductor(member, h.engine, "t").close()
        after = Conductor(member, h.engine, "t").spaces_open()
    except Refusal as refusal:
        refused = str(refusal)
    codes = {one.code for one in work.constraints} if work is not None else set()
    form = compiling.format_enumeration(h.house).get("team-board")
    readings = dict(getattr(welcome, "payloads", ()) or ())
    board = [json.loads(line) for line in readings.get("team-board", "").splitlines() if line.strip().startswith("{")]
    listed = [json.loads(line) for line in readings.get("team-templates", "").splitlines() if line.strip().startswith("{")]
    duo = next((one for one in board if one.get("team") == "duo"), {})
    if (offered and welcome is not None and welcome.root == "TEAMS" and welcome.document == "TEAMS-BOARD"
            and welcome.output == "team-board"
            and [(one.get("member"), one.get("description")) for one in duo.get("declared_members") or []]
            == [("dm", "no description"), ("dw", "no description")]
            and "teams/solo" in [one.get("template") for one in listed]
            and form is not None and form[0] == language.WORDS
            and work is not None and work.document == "TEAMS" and LAWS <= codes and opened == ["TEAMS"]
            and back is not None and before is not None and back.root == before.root and after == []):
        held("(a) the door", "TEAMS offered at TURN; opened on TEAMS-BOARD, its readings team-board (duo, its two "
             "members without a description) and team-templates (the team presets among them) to an INFER in words; then the WORK under TS1-TS4, TEAMS the one space open; closed, the root it was opened from back")
    else:
        failures.append(f"  ✗ (a) the door                offered={offered} root={getattr(welcome, 'root', None)} "
                        f"first={getattr(welcome, 'document', None)}/{getattr(welcome, 'output', None)} "
                        f"payloads={sorted(readings)} duo={duo} templates={[one.get('template') for one in listed]} form={form} "
                        f"work={getattr(work, 'document', None)} via={seen} codes={sorted(codes)} open={opened} "
                        f"back={getattr(back, 'root', None)} after={after} refused={refused[-200:]!r}")

    # --- (c) the author's reference: served by the space, beside the member's ---------------------------------
    sheet = [one for one in titles if one.split(".")[0] == "TEAMS_CHEATSHEET"]
    spec = [one for one in titles if one.split(".")[0] == "TEAM_WORK"]
    if sheet and spec and (bodies.get(sheet[0]) or "").strip() and bodies.get(sheet[0]) != bodies.get(spec[0]):
        held("(c) the author's reference", f"TEAMS's block serves {sheet[0]} beside {spec[0]}, each its own body "
             f"({len(bodies[sheet[0]])} c, {len(bodies[spec[0]])} c)")
    else:
        failures.append(f"  ✗ (c) the author's reference  titles={titles} work={getattr(work, 'document', None)} "
                        f"refused={refused[-200:]!r}")

    # --- (b) written in the house from an agent ----------------------------------------------------
    born = h.call("agent", "add", "agents/pa")
    agent_ws = h.meta_of("agents/pa").parent
    agent_meta = h.meta_of("agents/pa")
    from_agent = lambda *args: cli(h.engine, "--instance", str(agent_meta), *args, cwd=agent_ws, env=h.env)
    kept = tree(agent_ws, agent_meta / ".sys")
    bad = from_agent("team", "declare", "bad", "--template", "teams/solo", "--description", "one line\nand another")
    made = from_agent("team", "declare", "crew", "--template", "teams/solo", "--description", TEAM_SAID)
    listed = from_agent("team", "status", "--json")
    lines_ = [json.loads(line) for line in listed.stdout.splitlines() if line.strip()] if listed.returncode == 0 else []
    crew = next((one for one in lines_ if one.get("team") == "crew"), {})
    started = h.call("team", "start", "crew", "--no-tick")
    posed = from_agent("team", "post", "crew", "--message", "review the open work", "--every", "weekday 09:30",
                       "--description", DESCRIBED, "--no-tick")
    declared = from_agent("team", "declaration", "crew", "--json")
    try:
        read_crew = json.loads(declared.stdout) if declared.returncode == 0 else {}
    except ValueError:
        read_crew = {}
    held_back = [from_agent("team", verb, "crew", "--recurrence", "R1", *more)
                 for verb, more in (("pause", ()), ("resume", ("--no-tick",)), ("stop", ("--no-tick",)))]
    journal = h.journal_of("crew")
    found = T.lines(journal) if journal.is_file() else []
    recurrences = T.by_kind(found, "recurrence")
    turns = [one.get("kind") for one in found if one.get("kind") in ("recurrence-paused", "recurrence-resumed",
                                                                       "recurrence-stopped")]
    unchanged = tree(agent_ws, agent_meta / ".sys") == kept
    records = agent_meta / ".sys" / "records" / "teams"
    if (born.returncode == 0 and made.returncode == 0 and (h.teams / "crew" / "TEAM.md").is_file()
            and bad.returncode == 2 and "team-invalid" in bad.stderr and not (h.teams / "bad").exists()
            and crew.get("description") == TEAM_SAID
            and [one.get("member") for one in crew.get("declared_members") or []] == ["worker"]
            and not (agent_ws / "teams").exists() and started.returncode == 0 and posed.returncode == 0
            and [one.get("description") for one in recurrences] == [DESCRIBED] and unchanged
            and read_crew.get("team") == "crew" and (read_crew.get("verdict") or {}).get("ok") is True
            and read_crew.get("description") == TEAM_SAID and all(one.returncode == 0 for one in held_back)
            and turns == ["recurrence-paused", "recurrence-resumed", "recurrence-stopped"]
            and not records.exists()):
        held("(b) written in the house from an agent", "team declare --description from agents/pa: teams/crew/ in the "
             "house, its description and its member read back by status --json; two lines team-invalid, nothing "
             "written; started "
             "there, post --every --description from the agent: one recurrence in the house's journal with its "
             "description; declaration, pause, resume and stop --recurrence from the agent reach the house's "
             "TEAM.md and journal; the agent's workspace identical, no team's records under its instance")
    else:
        failures.append(f"  ✗ (b) from an agent           rc={[one.returncode for one in (born, made, started, posed)]} "
                        f"house={(h.teams / 'crew' / 'TEAM.md').is_file()} agent_teams={(agent_ws / 'teams').exists()} "
                        f"bad={bad.returncode}:{bad.stderr.strip()[-80:]!r} crew={crew} "
                        f"recurrences={[one.get('description') for one in recurrences]} unchanged={unchanged} "
                        f"records={records.exists()} declaration={declared.returncode}:{read_crew.get('description')!r} "
                        f"held_back={[(one.returncode, one.stderr.strip()[-80:]) for one in held_back]} turns={turns} "
                        f"{(made.stderr or started.stderr or posed.stderr).strip()[-200:]!r}")

    # --- (d) a team set up as the space teaches it, (e) changed as it teaches it ------------------------------------
    blocks = taught(SPACE)
    starts = [line for block in blocks for line in block if line[1:2] == ["start"]]
    played, after_setup, after_change = [], {}, {}
    if len(blocks) >= 2:
        played = [(line, from_agent(*line)) for line in blocks[0]]
    named = sorted({line[2] for block in blocks[:2] for line in block if len(line) > 2 and line[1] in ("declare", "declaration")})
    team = named[0] if len(named) == 1 else ""
    folder = h.teams / team if team else h.teams / "-"
    season_bytes = (folder / "SEASON.md").read_bytes() if (folder / "SEASON.md").is_file() else None
    read_setup = from_agent("team", "declaration", team, "--json") if team else None
    try:
        after_setup = json.loads(read_setup.stdout) if read_setup is not None and read_setup.returncode == 0 else {}
    except ValueError:
        after_setup = {}
    keys, views = roles_seen(after_setup)
    lines_played = [(one[1:3], done.returncode) for one, done in played]
    verbs = [one[1] + (" --season" if "--season" in one else "") for one, _ in played]
    if (len(blocks) >= 2 and not starts and played and all(done.returncode == 0 for _, done in played)
            and "declare" in verbs and "declare --season" in verbs and verbs.index("declare") < verbs.index("declare --season")
            and (folder / "TEAM.md").is_file() and season_bytes is not None
            and (after_setup.get("verdict") or {}).get("ok") is True and len(keys) >= 2
            and any(views.values()) and len({tuple(docs) for docs in views.values()}) >= 2
            and not h.journal_of(team).exists()):
        held("(d) set up as the space teaches it", f"TEAMS.md's first block, {len(played)} lines played from agents/pa "
             f"({', '.join(verbs)}): teams/{team}/TEAM.md and SEASON.md in the house, verdict ok, role keys "
             f"{sorted(keys)}, each member's role documents its own ({views}); "
             "no journal, no line plays start")
    else:
        failures.append(f"  ✗ (d) set up as taught       blocks={len(blocks)} starts={starts} team={team!r} "
                        f"played={lines_played} season={season_bytes is not None} "
                        f"verdict={after_setup.get('verdict')} keys={sorted(keys)} views={views} "
                        f"journal={h.journal_of(team).exists() if team else None} "
                        f"{[done.stderr.strip()[-160:] for _, done in played if done.returncode]!r}")

    changed = [(line, from_agent(*line)) for line in blocks[1]] if len(blocks) >= 2 and team else []
    read_change = from_agent("team", "declaration", team, "--json") if team else None
    try:
        after_change = json.loads(read_change.stdout) if read_change is not None and read_change.returncode == 0 else {}
    except ValueError:
        after_change = {}
    members_before = {one.get("member") for one in (after_setup.get("declared") or {}).get("agents") or []}
    members_after = {one.get("member") for one in (after_change.get("declared") or {}).get("agents") or []}
    added = members_after - members_before
    _, views_after = roles_seen(after_change)
    still = (folder / "SEASON.md").read_bytes() if (folder / "SEASON.md").is_file() else None
    if (changed and all(done.returncode == 0 for _, done in changed) and added
            and members_before and members_before <= members_after
            and any(op[1] == "declare" for op, _ in changed)
            and still == season_bytes and (after_change.get("verdict") or {}).get("ok") is True
            and all(views_after.get(one) for one in added) and not h.journal_of(team).exists()):
        held("(e) changed as the space teaches it", f"TEAMS.md's second block, {len(changed)} lines from agents/pa: "
             f"{sorted(added)} added to the members and to a role key, {sorted(members_before)} still there, its view "
             "holding the role's document; "
             "SEASON.md at its bytes, verdict ok, still no journal")
    else:
        failures.append(f"  ✗ (e) changed as taught      played={[(one[1:3], done.returncode) for one, done in changed]} "
                        f"added={sorted(added)} before={sorted(members_before)} after={sorted(members_after)} "
                        f"season_kept={still == season_bytes} "
                        f"verdict={after_change.get('verdict')} views={views_after} "
                        f"{[done.stderr.strip()[-160:] for _, done in changed if done.returncode]!r}")
    return 0
