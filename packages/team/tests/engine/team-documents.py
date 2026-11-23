"""Scenario `team-documents` -- 15 case(s): a team plays from ITS directory, `teams/<name>/`, the root of
documents of every run it opens; `TEAM.md` DECLARES the team, and its body is the OWNER'S WORD, served by its name;
`teams/<name>/TEAM-<name>.md` is RENDERED by every `team start` -- its head, called at the kit's `turn.begin`,
serving itself, and for its body the intention of the template `TEAM.md` names, empty without one -- never copied
into a message nor into the journal, which keeps its digest; the contract of the acts is team's fragment of the
standing orders; nothing of the team is written in an agent's instance. Six teams stand in one
house, each under its own names; the two that play run side by side, each case reads its team's journal, its
directory, its prompts.
- (a) the team's documents in its directory: `team start` writes `TEAM-<name>.md` -- no file of that name stood
  before it --, `TEAM-<name>-members.md` and
  `TEAM-IDLE.md` under `teams/<name>/`, `SEASON.md` with the launch its flags give, and `TURN.md`, the overlay of
  the kit's turn whose `output:` is the module's `ACT_FORMAT`: the WORK line of each member's first block names that
  format; a task and a daily played, the daily's entry laid in
  the team's directory ALONE is elected in the member's run of the daily; the agents carry no file of the team
- (b) the contract in the standing orders: the house's marble carries team's `system/SYSTEM.md`; no
  document of a team carries it, and the skill keeps no contract of its own
- (c) the files of an earlier start leave: the team's bytes laid at an agent (`procs/TURN.md`,
  `procs/TEAM-IDLE.md`, `procs/TEAM-<name>.md`, `skills/team-entry/`) are removed at the start; the law an
  earlier start laid in the team's directory (`teams/<name>/TURN.md` at its bytes) is replaced by the overlay, said;
  a `TURN.md` of the owner standing there is kept, and said; a second start leaves the overlay at its bytes and
  says nothing of it; an agent's own `procs/TURN.md` stays, and is said
- (d) the opening: the member's first prompt carries the reading of `TEAM-<name>`, the intention rendered with its
  name, then the reading of `TEAM.md`, the owner's word, then the reading of the package's `TEAM_WORK.md` and its
  body, before the members' sheet; the message of the wake-up carries neither
- (e) a resume of the same run, nothing changed -- the member asks the owner, the owner's reply wakes it on
  the same task: neither reading is served again
- (f) the owner's word edited between two wake-ups of the same run -- the body of `TEAM.md` rewritten, no start, no
  reset: the next wake-up, under the same key, serves the new body under `TEAM.md` and never the old one; the
  intention, unchanged, is not served again
- (g) the team's document: its head serves itself, then `TEAM.md` when its body says something -- a `TEAM.md`
  without a body adds nothing to `serve:` --, with `next:` and `decide:` under entries alone; its body the intention
  rendered, empty without a template; no start writes `TEAM.md`: its bytes the same before and after each
- (h) a run of the same agent opened without the team's root never reads the intention, and its WORK line names
  the `output:` of the kit's turn, as the house's own turn does -- never the act's format
- (i) `team-started` keeps no `intention`, its `digest` stays, and `rendered` keeps the digest of the
  `TEAM-<name>.md` the start wrote; a journal written with the field `intention` reads; the face says a `TEAM.md`
  changed since the start
- (j) the rule of service: a `TEAM-<name>-<x>.md` laid by hand before the start is served after `TEAM-<name>.md`,
  `TEAM.md` and `TEAM_WORK.md`, the head's `serve:` naming them in that order, then every `TEAM-<name>-<x>.md`
  by name; the member's first prompt carries its reading; under entries, `next:` and `decide:` stand as before
- (k) the members' sheet: `TEAM-<name>-members.md`, no front matter, one row per member -- reports to, the model and
  the effort of its profile or the team's launch, its `description:`, `no description` for a member left on the
  kit's template --; its reading reaches the member; `declaration --json` says the same descriptions, the team's
  directory and the members' instances unchanged; a team declaring `roles:` gets a column `roles` after `reports
  to`, each member's keys joined by a comma, `—` without one; a team without a role keeps the five columns
- (l) the common document mounted, never served: a `TEAM-<name>-common.md` declaring `mount: turn.begin`, its law
  `TM1`, its `tools:` and `serve:` resolved -- the start writes a head serving `TEAM-<name>.md`, `TEAM_WORK.md`, the
  members' sheet and the notes laid by hand, never the common: the engine mounts it
- (m) the common judged before any write: a law coded outside `TM` refuses `common-code-prefix`, a tool nothing
  resolves `common-tool-unknown`, a row nothing serves `common-serve-unknown`, a code two mounted documents share or
  that a member declares `common-collision` naming the member -- before the first start the member not born stays
  unborn, no journal; after it the journal byte for byte; the team's directory byte for byte across every refusal
- (n) the packages declare no team law: the engine's inventory (`sections.inventory`) of every package the house
  plays holds no code of the `TM` prefix -- the examples the team package teaches are no declared law
- (o) refused, nothing written: a rendered `TEAM-<name>.md` retouched refuses `rendered-edited`; a
  `TEAM-<name>.md` written by hand, which no start rendered, refuses `intention-misplaced`, its remedy naming the
  body of `TEAM.md`; a template whose intention holds a hole nothing declares refuses `value-undeclared` -- the
  team's directory and its journal byte for byte across each
"""
from __future__ import annotations

import json
import re
import threading

import hashlib

from conductor import Refusal, instance, sections
from tests.harness import cli, support

T = support(__file__, "team")
OWN_TURN = "---\nname: TURN\nconstraints.behavior: |\n  OX1  keep it short.\n---\n"
BODY = "Merge what is asked."
EDITED = "Merge and tag what is asked."
READING = "INFORMATION — TEAM-aim"                 # the intention, rendered from the template TEAM.md names
WORD_READING = "INFORMATION — TEAM.md"             # the owner's word: the body of TEAM.md
SPEC_READING = "INFORMATION — TEAM_WORK"           # the package's reference on how a team works, served after it
HOLED = "---\ndescription: a hole nothing declares\nform: one\nmembers: |\n  alone\n---\n{root} follows {nobody}.\n"
NOTES = "Each member keeps its own branch."
FA_SAID = "Merges what its reports bring back."
SHEET_HEAD = ["member", "reports to", "model", "effort", "description"]
STEP = re.compile(r"^WORK (\S+) => \S+", re.M)      # the WORK line of a block: its form


def _earlier(h, path: str) -> list:
    """Lays at `path` what a start before this version laid there, the team's very bytes: the overlay, the
    neutral, the team's document, the decider skill -> the files laid."""
    here = h.team_module().parent
    retired = here / "retired" if (here / "retired").is_dir() else here
    laid = []
    for source, where in (("agent-turn-0.32.txt", ("procs", "TURN.md")), ("agent-idle.md", ("procs", "TEAM-IDLE.md")),
                          ("agent-entry.md", ("skills", "team-entry", "SKILL.md")),
                          ("agent-entry.py", ("skills", "team-entry", "team-entry.py"))):
        origin = (here if source == "agent-idle.md" else retired) / source   # the law as those starts laid it
        target = h.meta_of(path).joinpath(*where)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(origin.read_bytes())
        laid.append(target)
    team_doc = h.meta_of(path) / "procs" / "TEAM-files.md"
    team_doc.write_text("---\nproc: |\n  SERVE\nserve: |\n  TEAM-files.md\nattach: turn.begin\n"
                        "next: DAILY.md TEAM-IDLE.md\ndecide: team-entry files\n---\n# TEAM-files\n", encoding="utf-8")
    laid.append(team_doc)
    return laid


def _team_files(h, path: str) -> list[str]:
    meta = h.meta_of(path)
    found = ([str(one.relative_to(meta)) for one in (meta / "procs").glob("*.md") if not one.name.startswith("_")]
             if (meta / "procs").is_dir() else [])           # a `_` file is the install's working note, no team's
    if (meta / "skills" / "team-entry").exists():
        found.append("skills/team-entry")
    return sorted(found)


def _form(path) -> str:
    """-> the `output:` a document's front matter names, read by the engine's face; "" without the file or the key."""
    try:
        return sections.get(path, "output")
    except (OSError, Refusal):
        return ""


def _asked(served: str) -> str:
    """-> the form the first WORK line of pp's output names; "" without one."""
    found = STEP.search(served)
    return found.group(1) if found else ""


def _outside(h, path: str | None) -> str:
    """-> what a run opened WITHOUT a team's root serves, chunk after chunk: the agent's at `path`, the house's own
    without one."""
    meta = h.meta_of(path) if path else h.house
    opened = cli(h.engine, "--instance", str(meta), "-new", cwd=meta.parent, env=h.env)
    chunks = [opened.stdout]
    key = re.search(r"run ([0-9a-f]{6})", opened.stdout)
    for _ in range(12):
        if not key or "a reading continues" not in chunks[-1]:
            break
        chunks.append(cli(h.engine, "--instance", str(meta), key.group(1), cwd=meta.parent, env=h.env).stdout)
    return "".join(chunks)


def _split(prompt: str) -> tuple[str, str]:
    """-> (the message of a wake-up, pp's output after it)."""
    at = prompt.find("▌ pp · run")
    return (prompt, "") if at < 0 else (prompt[:at], prompt[at:])


def _rows(text: str) -> dict[str, dict]:
    """-> the sheet's rows by member, each its cells by the header's columns; {} without a table."""
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    cells = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    if len(cells) < 2:
        return {}
    head = cells[0]
    return {row[0]: dict(zip(head, row)) for row in cells[2:] if len(row) == len(head)} if head == SHEET_HEAD else {}


def _tree(*roots) -> dict[str, bytes]:
    """-> every file at or under the roots, by its path, at its bytes."""
    files = [one for root in roots for one in ([root] if root.is_file() else sorted(root.rglob("*")))]
    return {str(one): one.read_bytes() for one in files if one.is_file()}


def _document(h, name: str) -> str:
    own = h.teams / name / f"TEAM-{name}.md"
    return own.read_text(encoding="utf-8") if own.is_file() else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "fa": {"T1": [{"sleep": 0.1, "body": {"do": ["pa"]}},
                      {"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "standup"}}]},
        # lead holds ONE task, one run: it asks the owner twice, each reply waking it again under the same key
        "lead": {"T1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which PR?"}}},
                        {"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which tag?"}}},
                        {"sleep": 0.1, "body": {"done": "three"}}]}})
    by_kind, all_ended, runs_launched = T.by_kind, T.all_ended, T.runs_launched
    ended_on = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)

    # --- every team declared and started before the first wait --------------------------------------------
    h.declare("files", "---\nagents: |\n  fa agents/fa\n  pa agents/pa\nreports: |\n  pa -> fa\nroot: fa\n"
                       "ceremonies: |\n  daily every weekday 09:30 with pa -> fa\n"
                       "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nKeep the files where the team lives.\n")
    (h.teams / "files" / "DAILY.md").write_text(T.DAILY_DOC, encoding="utf-8")
    h.declare("aim", f"---\ntemplate: teams/solo\nagents: |\n  lead agents/lead\nschedule: off\n---\n{BODY}\n")
    (h.teams / "aim" / "TEAM-aim-notes.md").write_text(f"# Notes\n\n{NOTES}\n", encoding="utf-8")   # laid by hand
    h.declare("beat", "---\nagents: |\n  b agents/b\nroot: b\nentries: |\n  do -> WORK.md\nschedule: off\n---\n"
                      "Keep the beat.\n")
    (h.teams / "beat" / "WORK.md").write_text(T.WORK_DOC, encoding="utf-8")
    h.declare("mute", "---\nagents: |\n  q agents/q\nroot: q\nentries: |\n  do -> WORK.md\nschedule: off\n---\n")
    (h.teams / "mute" / "WORK.md").write_text(T.WORK_DOC, encoding="utf-8")
    h.declare("bare", "---\nagents: |\n  z agents/z\nroot: z\nschedule: off\n---\n")
    h.declare("old", "---\nagents: |\n  o agents/o\nroot: o\nschedule: off\n---\nThe old way.\n")
    h.call("agent", "add", "agents/pa")
    h.call("agent", "add", "agents/fa")
    fa_member = h.meta_of("agents/fa") / "MEMBER.md"          # fa's own description; pa stays on the kit's template
    fa_member.write_text(re.sub(r"^description:.*?\n(?=\S)", f"description: {FA_SAID}\n",
                                fa_member.read_text(encoding="utf-8"), count=1, flags=re.M | re.S), encoding="utf-8")
    earlier = _earlier(h, "agents/pa")
    retired = h.team_module().parent / "retired"                   # the law of team 0.39, laid in the team's directory
    former_law = h.teams / "files" / "TURN.md"
    former_law.write_bytes((retired / "agent-turn-0.39.txt").read_bytes())
    own = h.meta_of("agents/fa") / "procs" / "TURN.md"
    own.parent.mkdir(parents=True, exist_ok=True)
    own.write_text(OWN_TURN, encoding="utf-8")
    owner_turn = h.teams / "bare" / "TURN.md"                   # the owner's own overlay of the turn, in bare's directory
    owner_turn.write_text(OWN_TURN, encoding="utf-8")

    stood = [name for name in ("files", "aim", "beat", "mute", "bare") if (h.teams / name / f"TEAM-{name}.md").exists()]
    declared_before = {name: (h.teams / name / "TEAM.md").read_bytes() for name in ("files", "aim", "beat", "mute", "bare")}
    started = h.call("team", "start", "files", "--message", "first task", *h.harnessed,
                     "--member", "pa", "--model", "m-pa", "--effort", "high", now="09:10")
    aimed = h.call("team", "start", "aim", "--message", "merge PR 11", *h.harnessed)
    made = [h.call("team", "start", name, "--message", "x", *h.harnessed, "--no-tick")
            for name in ("beat", "mute", "bare")]
    declared_same = all((h.teams / name / "TEAM.md").read_bytes() == data for name, data in declared_before.items())
    started_event = (by_kind(h.events("aim"), "team-started") or [{}])[0]
    forged = {**started_event, "id": 1, "team": "old", "agents": {"o": "agents/o"}, "root": "o",
              "intention": "The old way.", "digest": "000000000000"}
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(json.dumps(forged) + "\n", encoding="utf-8")

    # --- the two chains, interleaved: files' task then its daily, aim's one task through two replies ----------
    asks = lambda found: [one["id"] for one in by_kind(found, "post", verb="ask", **{"from": "lead"})]
    asked = lambda n: lambda found: len(asks(found)) >= n and all_ended(found)
    first = h.settled("files", ended_on("T1"), timeout=60)
    rung = h.call("team", "tick", "files", now="09:31")
    opened = h.settled("aim", asked(1), timeout=60)
    second = h.call("team", "post", "aim", "--task", "T1", "--reply", str((asks(h.events("aim")) or [0])[0]),
                    "--message", "merge PR 12")
    resumed = h.settled("aim", asked(2), timeout=60)
    declared = h.teams / "aim" / "TEAM.md"
    declared.write_text(declared.read_text(encoding="utf-8").replace(BODY, EDITED), encoding="utf-8")
    third = h.call("team", "post", "aim", "--task", "T1", "--reply", str((asks(h.events("aim")) or [0, 0])[-1]),
                   "--message", "tag release 3")
    daily = h.settled("files", ended_on("T2"), timeout=60)
    edited = h.settled("aim", ended_on("T1"), timeout=60)
    sheet_path = h.teams / "files" / "TEAM-files-members.md"
    sheet = sheet_path.read_text(encoding="utf-8") if sheet_path.is_file() else ""
    before = _tree(h.teams / "files", h.meta_of("agents/fa") / "MEMBER.md", h.meta_of("agents/pa") / "MEMBER.md")
    told = h.call("team", "declaration", "files", "--json")
    after = _tree(h.teams / "files", h.meta_of("agents/fa") / "MEMBER.md", h.meta_of("agents/pa") / "MEMBER.md")

    outside = {}                                     # the two runs opened without a team's root, side by side
    openers = [threading.Thread(target=lambda path=path: outside.__setitem__(path, _outside(h, path)))
               for path in ("agents/pa", "agents/lead", None)]
    for one in openers:
        one.start()
    face = h.face("aim")
    old = h.face("old")
    for one in openers:
        one.join()

    # --- (a) the team's documents in its directory, none at the agents ------------------------------------
    found = h.events("files")
    # the daily plays in a run of its own (its carrier the ceremony): its key is read on pa's wake-up on T2
    key_pa = next((one.get("run") for one in by_kind(found, "wake-ended", agent="pa")
                   if str(one.get("tag", "")).startswith("pa-T2-")), "")
    elected = h.elected("agents/pa", key_pa)
    directory = sorted(one.name for one in (h.teams / "files").iterdir() if one.is_file())
    at_pa = _team_files(h, "agents/pa")
    at_fa = _team_files(h, "agents/fa")
    act_format = h.module().ACT_FORMAT
    turn_form = _form(h.teams / "files" / "TURN.md")
    asked = {member: _asked(_split((h.prompts_of(member) or [""])[0])[1]) for member in ("fa", "pa")}
    if (started.returncode == 0 and first and rung.returncode == 0 and daily and key_pa and not stood
            and directory == ["DAILY.md", "SEASON.md", "TEAM-IDLE.md", "TEAM-files-members.md", "TEAM-files.md", "TEAM.md",
                              "TURN.md"]
            and turn_form == act_format and asked == {"fa": act_format, "pa": act_format}
            and "DAILY.md" in elected and at_pa == [] and at_fa == ["procs/TURN.md"]):
        held("(a) the team's documents in its directory", f"no TEAM-<name>.md before the starts; teams/files/ "
             f"carries {directory}, TURN.md's output `{turn_form}` the module's ACT_FORMAT, the form the WORK line "
             f"of fa's and pa's first block names; pa's run {key_pa} "
             f"elects {elected}, DAILY.md laid in the team's directory alone; agents/pa carries none of the team, "
             "agents/fa its own TURN.md alone")
    else:
        failures.append(f"  ✗ (a) the team's directory      start={started.returncode} first={first} rung={rung.returncode} "
                        f"daily={daily} key={key_pa} directory={directory} turn={turn_form!r} asked={asked} "
                        f"elected={elected} pa={at_pa} fa={at_fa} stood={stood} "
                        f"{started.stderr[-300:]!r}")

    # --- (b) the contract in the standing orders -----------------------------------------------------------
    fragment = h.team_module().parents[2] / "system" / "SYSTEM.md"
    contract = fragment.read_text(encoding="utf-8").split("---\n", 2)[-1].strip() if fragment.is_file() else ""
    marble = h.house / ".sys" / "system.md"
    marbled = marble.read_text(encoding="utf-8") if marble.is_file() else ""
    documents = [_document(h, name) for name in ("files", "aim", "beat", "mute", "bare")]
    kept = sorted(one.name for one in h.team_module().parent.glob("*.md"))
    if contract and contract in marbled and all(contract not in one for one in documents) and kept == ["SKILL.md", "agent-idle.md"]:
        held("(b) the contract in the standing orders", f"the house's marble carries team's SYSTEM.md "
             f"({len(contract)} c); no team document carries it; the skill keeps {kept}")
    else:
        failures.append(f"  ✗ (b) the contract             fragment={fragment.is_file()} marbled={contract in marbled} "
                        f"in_documents={[contract in one for one in documents] if contract else None} kept={kept}")

    # --- (c) the files of an earlier start leave, the agent's own stays and is said -------------------------
    # no structured signal says a kept file: the start's stderr is read for the path, the file and `kept`
    beat_turn = h.teams / "beat" / "TURN.md"
    laid_once = beat_turn.read_bytes() if beat_turn.is_file() else None
    h.off_season("beat")
    restarted = h.call("team", "start", "beat", "--no-tick")
    laid_twice = beat_turn.read_bytes() if beat_turn.is_file() else None
    former_bytes = (retired / "agent-turn-0.39.txt").read_bytes()
    if (started.returncode == 0 and not any(one.exists() for one in earlier)
            and former_law.is_file() and former_law.read_bytes() != former_bytes and _form(former_law) == act_format
            and "teams/files/TURN.md" in started.stderr
            and owner_turn.read_text(encoding="utf-8") == OWN_TURN and "teams/bare/TURN.md" in made[2].stderr
            and "kept" in made[2].stderr
            and restarted.returncode == 0 and laid_once and laid_twice == laid_once
            and _form(beat_turn) == act_format and "TURN.md" not in restarted.stderr
            and own.read_text(encoding="utf-8") == OWN_TURN and "agents/fa" in started.stderr
            and "procs/TURN.md" in started.stderr and "kept" in started.stderr):
        held("(c) the files of an earlier start leave", f"{len(earlier)} files of the team's bytes removed from "
             "agents/pa; the law of team 0.39 in teams/files/ replaced by the overlay and said; the owner's TURN.md "
             "in teams/bare/ kept and said; beat's second start leaves the overlay at its bytes, unsaid; agents/fa's "
             "own TURN.md kept, and said")
    else:
        failures.append(f"  ✗ (c) the earlier files         left={[str(one) for one in earlier if one.exists()]} "
                        f"law={former_law.is_file()}/{_form(former_law)!r} "
                        f"owner={owner_turn.read_text(encoding='utf-8') == OWN_TURN}:{made[2].stderr[-200:]!r} "
                        f"again={restarted.returncode}/{laid_once == laid_twice}/{laid_once is not None}:"
                        f"{restarted.stderr[-200:]!r} "
                        f"own={own.read_text(encoding='utf-8') == OWN_TURN} {started.stderr[-300:]!r}")

    # --- (d) the opening: the intention served by pp, absent from the message --------------------------
    found = h.events("aim")
    prompts = h.prompts_of("lead")
    message, served = _split(prompts[0] if prompts else "")
    try:                                              # the spec's first line, read where the house resolves it
        spec_path = instance.resolve(h.house, "TEAM_WORK.md")
        spec_said = next((line for line in spec_path.read_text(encoding="utf-8").splitlines() if line.strip()), "")
    except (OSError, ValueError, LookupError):
        spec_path, spec_said = None, ""
    at = {"intention": served.find(READING), "word": served.find(WORD_READING), "spec": served.find(SPEC_READING),
          "sheet": served.find("INFORMATION — TEAM-aim-members")}
    if (aimed.returncode == 0 and -1 < at["intention"] < at["word"] < at["spec"] < at["sheet"]
            and "`lead`" in served[at["intention"]:at["word"]] and BODY in served[at["word"]:at["spec"]]
            and BODY not in message and "`lead`" not in message
            and spec_said and spec_said in served[at["spec"]:at["sheet"]]):
        held("(d) the opening serves the intention, then the owner's word", f"lead's first prompt: `{READING}` "
             f"naming lead, `{WORD_READING}` and the body of TEAM.md in pp's "
             f"output ({len(prompts[0])} c), then `{SPEC_READING}` and its body before the members' sheet; the "
             f"message ({len(message)} c) without them")
    else:
        failures.append(f"  ✗ (d) the opening              rc={aimed.returncode} reading={READING in served} "
                        f"order={at} spec={spec_path} spec_body={bool(spec_said) and spec_said in served} "
                        f"in_message={BODY in message} {aimed.stderr[-200:]!r} {message[-300:]!r}")

    # --- (e) a resume, TEAM.md unchanged: nothing served again -------------------------------------------
    again = prompts[1] if len(prompts) > 1 else ""
    if (opened and second.returncode == 0 and resumed and again and READING not in again
            and WORD_READING not in again and BODY not in again and len(runs_launched(found, "lead")) == 1):
        held("(e) a resume does not read them again", f"lead's second prompt ({len(again)} c): no `{READING}`, "
             f"no `{WORD_READING}`, no body -- the readings proven in the run")
    else:
        failures.append(f"  ✗ (e) the unchanged resume     rc={second.returncode} opened={opened} resumed={resumed} "
                        f"prompts={len(prompts)} runs={runs_launched(found, 'lead')} reading={READING in again} "
                        f"body={BODY in again} {second.stderr[-200:]!r}")

    # --- (f) the body edited mid-run: served at the next exchange, same key ------------------------------
    later = prompts[2] if len(prompts) > 2 else ""
    message3, served3 = _split(later)
    runs = runs_launched(found, "lead")
    if (third.returncode == 0 and edited and len(runs) == 1 and WORD_READING in served3
            and EDITED in served3[served3.find(WORD_READING):] and READING not in served3
            and BODY not in later and EDITED not in message3
            and not by_kind(found, "team-started")[1:] and not by_kind(found, "run-reset")
            and T.result_of(found, "T1") == "three"):
        held("(f) the owner's word edited reaches the member mid-run", f"the body of TEAM.md rewritten, no start nor "
             f"reset: lead's third prompt, run {sorted(runs)[0]}, serves the new body under TEAM.md, never the old "
             "one; the intention is not served again")
    else:
        failures.append(f"  ✗ (f) the edited word          rc={third.returncode} edited={edited} runs={runs} "
                        f"word={WORD_READING in served3} new={EDITED in served3} old={BODY in later} "
                        f"intention={READING in served3}")

    # --- (g) the team's document, entries or not ---------------------------------------------------------
    aim_doc, beat_doc, mute_doc, bare_doc = (_document(h, name) for name in ("aim", "beat", "mute", "bare"))
    aim_body = aim_doc.split("---\n", 2)[-1] if aim_doc.startswith("---\n") else aim_doc
    if (all(one.returncode == 0 for one in made) and declared_same
            and "serve: |\n  TEAM-aim.md\n  TEAM.md\n" in aim_doc and "attach: turn.begin" in aim_doc
            and "next:" not in aim_doc and "decide:" not in aim_doc and "`lead`" in aim_body and BODY not in aim_doc
            and "serve: |\n  TEAM-beat.md\n  TEAM.md\n" in beat_doc and "next: WORK.md TEAM-IDLE.md" in beat_doc
            and "decide: pp-team entry beat" in beat_doc and beat_doc.endswith("\n---\n")
            and "serve: |\n  TEAM-mute.md\n  TEAM_WORK.md\n" in mute_doc and "decide: pp-team entry mute" in mute_doc
            and mute_doc.endswith("\n---\n")
            and "serve: |\n  TEAM-bare.md\n  TEAM_WORK.md\n" in bare_doc and "next:" not in bare_doc
            and bare_doc.endswith("\n---\n")):
        held("(g) the team's document is rendered", "each head serves its own document, then TEAM.md where its body "
             "says something (aim, beat), not where it says none (mute, bare); next and decide under entries alone; "
             "aim's body the intention naming lead, the others' empty; TEAM.md's bytes the same across the five starts")
    else:
        failures.append(f"  ✗ (g) the team's document      rc={[one.returncode for one in made]} same={declared_same} "
                        f"aim={aim_doc!r} beat={beat_doc!r} mute={mute_doc!r} bare={bare_doc!r}")

    # --- (h) a run without the team's root never reads it ------------------------------------------------
    bare_lead = outside.get("agents/lead", "")
    kit_turn = next((home / "procs" / "TURN.md" for home in instance.vendored(h.house) if home.name.startswith("kit@")),
                    None)
    kit_form = _form(kit_turn) if kit_turn else ""
    forms = {path or "house": _asked(served) for path, served in outside.items()}
    if (bare_lead and READING not in bare_lead and EDITED not in bare_lead and BODY not in bare_lead
            and kit_form and kit_form != act_format
            and forms == {"agents/pa": kit_form, "agents/lead": kit_form, "house": kit_form}):
        held("(h) a run without the root does not read it", f"a run of agents/lead opened without "
             f"--documents ({len(bare_lead)} c): no `{READING}`, no body; the WORK line of agents/pa's, of "
             f"agents/lead's and of the house's own turn names `{kit_form}`, the output of the kit's turn")
    else:
        failures.append(f"  ✗ (h) outside the team         {len(bare_lead)}c reading={READING in bare_lead} "
                        f"body={EDITED in bare_lead or BODY in bare_lead} kit={kit_form!r} forms={forms}")

    # --- (i) the journal keeps no copy; the face says a changed TEAM.md ------------------------------------
    if (started_event and "intention" not in started_event and len(str(started_event.get("digest") or "")) == 12
            and (started_event.get("rendered") or {}).get("TEAM-aim.md")
            == hashlib.sha256(aim_doc.encode("utf-8")).hexdigest()[:12]
            and face.get("changed") is True and old.get("team") == "old"
            and (old.get("started") or {}).get("id") == 1 and old.get("changed") is True):
        held("(i) the journal keeps no copy", f"team-started without `intention`, digest "
             f"{started_event.get('digest')}, the digest of the TEAM-aim.md it rendered under `rendered`; aim's face: "
             "changed since the start; a journal with the field reads "
             "(old's face, its start #1)")
    else:
        failures.append(f"  ✗ (i) the journal              keys={sorted(started_event)} changed={face.get('changed')!r} "
                        f"rendered={started_event.get('rendered')} "
                        f"old={ {key: old.get(key) for key in ('team', 'started', 'changed')} }")
    # --- (j) the rule of service: a document laid by hand is served after the team's own ---------------------
    notes_reading = "INFORMATION — TEAM-aim-notes"
    first_served = _split(prompts[0] if prompts else "")[1]
    if ("serve: |\n  TEAM-aim.md\n  TEAM.md\n  TEAM_WORK.md\n  TEAM-aim-members.md\n  TEAM-aim-notes.md\nattach: turn.begin\n" in aim_doc
            and notes_reading in first_served and NOTES in first_served[first_served.find(notes_reading):]
            and NOTES not in again
            and "serve: |\n  TEAM-beat.md\n  TEAM.md\n  TEAM_WORK.md\n  TEAM-beat-members.md\nattach:" in beat_doc
            and "next: WORK.md TEAM-IDLE.md\ndecide: pp-team entry beat\n" in beat_doc):
        held("(j) a document laid by hand is served", "aim's head serves TEAM-aim.md, TEAM.md, TEAM_WORK.md, then TEAM-aim-members.md and "
             "TEAM-aim-notes.md by name; lead's first prompt carries the notes' reading, its resume does not again; "
             "beat's next and decide stand")
    else:
        failures.append(f"  ✗ (j) the rule of service       aim={aim_doc[:220]!r} notes={notes_reading in first_served} "
                        f"body={NOTES in first_served} again={NOTES in again} beat={beat_doc[:260]!r}")

    # --- (k) the members' sheet: written at the start, served, said again by the declaration -----------------
    h.declare("rk", "---\nagents: |\n  ka agents/rk-a\n  kb agents/rk-b\n  kc agents/rk-c\nreports: |\n  kb kc -> ka\n"
                    "root: ka\nroles: |\n  make ka kb\n  inspect kb\n  observe\nschedule: off\n---\nHold the roles.\n")
    roled = h.call("team", "start", "rk", "--no-tick")
    roled_sheet = h.teams / "rk" / "TEAM-rk-members.md"
    roled_lines = [line.strip() for line in (roled_sheet.read_text(encoding="utf-8") if roled_sheet.is_file() else "")
                   .splitlines() if line.strip().startswith("|")]
    roled_cells = [[cell.strip() for cell in line.strip("|").split("|")] for line in roled_lines]
    roled_rows = ({row[0]: dict(zip(roled_cells[0], row)) for row in roled_cells[2:]} if len(roled_cells) > 2 else {})
    rows = _rows(sheet)
    fa_row, pa_row = rows.get("fa") or {}, rows.get("pa") or {}
    pa_first = _split((h.prompts_of("pa") or [""])[0])[1]
    try:
        face_k = json.loads(told.stdout) if told.returncode == 0 else {}
    except ValueError:
        face_k = {}
    said_k = {one.get("member"): one.get("description") for one in (face_k.get("declared") or {}).get("agents") or []}
    if (sheet and not sheet.startswith("---") and sorted(rows) == ["fa", "pa"]
            and fa_row.get("description") == FA_SAID and pa_row.get("description") == "no description"
            and pa_row.get("reports to") == "fa" and (pa_row.get("model"), pa_row.get("effort")) == ("m-pa", "high")
            and (fa_row.get("model"), fa_row.get("effort")) == ("agent default", "default")
            and "INFORMATION — TEAM-files-members" in pa_first and FA_SAID in pa_first
            and said_k == {"fa": FA_SAID, "pa": "no description"} and before == after and before
            and roled.returncode == 0
            and roled_cells[:1] == [["member", "reports to", "roles", "model", "effort", "description"]]
            and {member: row.get("roles") for member, row in roled_rows.items()}
            == {"ka": "make", "kb": "make, inspect", "kc": "—"}):     # files' sheet: `_rows` reads its five columns
        held("(k) the members' sheet", f"TEAM-files-members.md without front matter, {len(rows)} rows: pa reports to "
             f"fa on its profile m-pa/high, `no description` on the kit's template; fa on the agent's default, its "
             f"own description; pa's first prompt reads it; declaration --json says the same, {len(before)} files "
             "unchanged; rk's sheet a column roles after reports to -- ka make, kb make, inspect, kc —; files' "
             "sheet without a role keeps its five columns")
    else:
        failures.append(f"  ✗ (k) the members' sheet        sheet={sheet[:400]!r} rows={rows} roled={roled_cells} "
                        f"{roled.stderr.strip()[-160:]!r} "
                        f"read={'INFORMATION — TEAM-files-members' in pa_first} said={said_k} "
                        f"unchanged={before == after} rc={told.returncode}:{told.stderr[-200:]!r}")

    # --- (l) and (m): the common document, mounted and judged ------------------------------------------------
    h.declare("kin", "---\nagents: |\n  ka agents/ka\n  kb agents/kb\nreports: |\n  kb -> ka\nroot: ka\n"
                     "schedule: off\n---\nHold the common.\n")
    kin = h.teams / "kin"
    (kin / "TEAM-kin-notes.md").write_text("# Notes\n\nNothing mounts here.\n", encoding="utf-8")
    h.call("agent", "add", "agents/ka")
    ka_law = h.meta_of("agents/ka") / "procs" / "KA-OWN.md"
    ka_law.parent.mkdir(parents=True, exist_ok=True)
    ka_law.write_text("---\ndescription: ka's own law\nconstraints.behavior: |\n  TM7  ka's own.\n---\n", encoding="utf-8")
    common, rules = kin / "TEAM-kin-common.md", kin / "TEAM-kin-rules.md"
    good = ("---\nmount: turn.begin\nconstraints.behavior: |\n  TM1  keep the team's branch.\ntools: |\n  pp-team\n"
            "serve: |\n  TEAM-kin-notes.md\n---\nWhat every member holds.\n")
    variants = {"common-code-prefix": (good.replace("TM1", "KX1"), None, ()),
                "common-tool-unknown": (good.replace("  pp-team\n", "  no-such-tool\n"), None, ("no-such-tool",)),
                "common-serve-unknown": (good.replace("  TEAM-kin-notes.md\n", "  NOWHERE.md\n"), None, ("NOWHERE.md",)),
                "common-collision": (good, good.replace("What every", "What the rules"), ("TM1",)),
                "common-collision ": (good.replace("TM1", "TM7"), None, ("TM7", "ka", "agents/ka"))}

    def refusals(after_start: bool) -> list[str]:
        wrong = []
        for label, (text, other, said) in variants.items():
            if after_start and label != "common-collision ":
                continue
            common.write_text(text, encoding="utf-8")
            rules.unlink(missing_ok=True)
            if other is not None:
                rules.write_text(other, encoding="utf-8")
            tree, journal = _tree(kin), (h.journal_of("kin").read_bytes() if h.journal_of("kin").is_file() else None)
            played = h.call("team", "start", "kin", "--message", "x", "--no-tick")
            now_journal = h.journal_of("kin").read_bytes() if h.journal_of("kin").is_file() else None
            if (played.returncode != 2 or f"pp-team: {label.strip()} --" not in played.stderr
                    or not all(one in played.stderr for one in said) or _tree(kin) != tree or now_journal != journal
                    or (not after_start and h.agent_stands("agents/kb"))):
                wrong.append(f"{label.strip()}: rc={played.returncode} same={_tree(kin) == tree} "
                             f"journal={now_journal == journal} kb={h.agent_stands('agents/kb')} {played.stderr[-200:]!r}")
        rules.unlink(missing_ok=True)
        return wrong

    unborn = refusals(False)
    common.write_text(good, encoding="utf-8")
    kin_started = h.call("team", "start", "kin", "--message", "x", "--no-tick")
    kin_doc = _document(h, "kin")
    h.off_season("kin")                                  # the next start judged off season
    born_wrong = refusals(True)
    expected = ("serve: |\n  TEAM-kin.md\n  TEAM.md\n  TEAM_WORK.md\n  TEAM-kin-members.md\n  TEAM-kin-notes.md\n"
                "attach: turn.begin\n")
    if kin_started.returncode == 0 and expected in kin_doc and "TEAM-kin-common.md" not in kin_doc:
        held("(l) the common mounted, never served", "kin's head serves TEAM-kin.md, TEAM.md, TEAM_WORK.md, the members' sheet "
             "and the notes; TEAM-kin-common.md, at mount: turn.begin, is not in its serve")
    else:
        failures.append(f"  ✗ (l) the common not served  rc={kin_started.returncode} head={kin_doc[:300]!r} "
                        f"{kin_started.stderr[-300:]!r}")
    if not unborn and not born_wrong and kin_started.returncode == 0:
        bench.refusals += len(variants) + 1
        held("(m) the common judged before any write", "common-code-prefix, common-tool-unknown, common-serve-unknown, "
             "common-collision between two mounted documents and with ka's own TM7 -- kb unborn, no journal; after the "
             "start, the collision again: the journal and teams/kin byte for byte")
    else:
        failures.append(f"  ✗ (m) the common judged       before={unborn} after={born_wrong}")

    # --- (n) the packages declare no team law ---------------------------------------------------------------
    team_codes = {home.name: sorted(code for code in sections.inventory(home) if re.fullmatch(r"TM[0-9]+", code))
                  for home in instance.vendored(h.house)}
    declared_tm = {name: codes for name, codes in team_codes.items() if codes}
    if team_codes and not declared_tm:
        held("(n) the packages declare no team law", f"the inventory of {len(team_codes)} packages "
             f"({', '.join(sorted(team_codes))}) holds no TM code")
    else:
        failures.append(f"  ✗ (n) the packages declare no team law  homes={sorted(team_codes)} tm={declared_tm}")

    # --- (o) refused, nothing written: a document retouched, an intention misplaced, a hole undeclared ----------
    def stands(name: str) -> tuple:
        journal = h.journal_of(name)
        return _tree(h.teams / name), journal.read_bytes() if journal.is_file() else None

    code_of = lambda played: (re.search(r"^pp-team: (\S+) --", played.stderr, re.M) or [None, ""])[1]
    mute_path = h.teams / "mute" / "TEAM-mute.md"
    rendered = mute_path.read_bytes()
    mute_path.write_bytes(rendered + b"A line of the owner.\n")
    h.off_season("mute")
    before = stands("mute")
    retouched = h.call("team", "start", "mute", "--no-tick")
    same_mute = stands("mute") == before
    mute_path.write_bytes(rendered)
    h.declare("mis", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\n")
    (h.teams / "mis" / "TEAM-mis.md").write_text("The team's intention, written here by hand.\n", encoding="utf-8")
    before = stands("mis")
    misplaced = h.call("team", "start", "mis", "--no-tick")
    same_mis = stands("mis") == before
    holed = h.house / "teams" / "templates" / "teams" / "holed.md"
    holed.parent.mkdir(parents=True, exist_ok=True)
    holed.write_text(HOLED, encoding="utf-8")
    h.declare("holed", "---\ntemplate: teams/holed\nagents: |\n  n agents/n\nschedule: off\n---\n")
    before = stands("holed")
    undeclared = h.call("team", "start", "holed", "--no-tick")
    same_holed = stands("holed") == before
    if (retouched.returncode == 2 and code_of(retouched) == "rendered-edited" and "TEAM-mute.md" in retouched.stderr
            and same_mute
            and misplaced.returncode == 2 and code_of(misplaced) == "intention-misplaced"
            and "TEAM-mis.md" in misplaced.stderr and "TEAM.md" in misplaced.stderr.replace("TEAM-mis.md", "")
            and same_mis and before[1] is None
            and undeclared.returncode == 2 and code_of(undeclared) == "value-undeclared" and "nobody" in undeclared.stderr
            and same_holed and not h.agent_stands("agents/n")):
        bench.refusals += 3
        held("(o) refused, nothing written", "TEAM-mute.md retouched: rendered-edited naming it; TEAM-mis.md written "
             "by hand, never rendered: intention-misplaced, its remedy naming TEAM.md; {nobody} in a template's "
             "intention: value-undeclared; each team's directory and journal byte for byte, agents/n not born")
    else:
        failures.append(f"  ✗ (o) refused                 rc={retouched.returncode}/{misplaced.returncode}/"
                        f"{undeclared.returncode} codes={code_of(retouched)}/{code_of(misplaced)}/{code_of(undeclared)} "
                        f"same={same_mute}/{same_mis}/{same_holed} {retouched.stderr.strip()[-160:]!r} "
                        f"{misplaced.stderr.strip()[-200:]!r} {undeclared.stderr.strip()[-160:]!r}")
    return 0
