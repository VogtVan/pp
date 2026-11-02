"""Scenario `team-documents` -- 9 case(s): a team plays from ITS directory, `teams/<name>/`, the root of
documents of every run it opens; `TEAM.md` DECLARES the team and is never served; its intention is the body of
`teams/<name>/TEAM-<name>.md`, the document `team start` heads -- called at the kit's `turn.begin`, it serves
itself -- never copied into a message nor into the journal; the contract of the acts is team's fragment of the
standing orders; nothing of the team is written in an agent's instance. Six teams stand in one
house, each under its own names; the two that play run side by side, each case reads its team's journal, its
directory, its prompts.
- (a) the team's documents in its directory: `team start` writes `TEAM-<name>.md` and `TEAM-IDLE.md` under
  `teams/<name>/`, no law (`TURN.md`); a task and a daily played, the daily's entry laid in the team's
  directory ALONE is elected in the member's run; the agents carry no file of the team
- (b) the contract in the standing orders: the house's marble carries team's `system/SYSTEM.COMMON.md`; no
  document of a team carries it, and the skill keeps no contract of its own
- (c) the files of an earlier start leave: the team's bytes laid at an agent (`procs/TURN.md`,
  `procs/TEAM-IDLE.md`, `procs/TEAM-<name>.md`, `skills/team-entry/`) are removed at the start, and the law an
  earlier start laid in the team's directory (`teams/<name>/TURN.md` at its bytes) with them, said; an
  agent's own `procs/TURN.md` stays, and is said
- (d) the opening: the member's first prompt carries the reading of `TEAM-<name>` and its body in pp's output;
  the message of the wake-up carries no intention
- (e) a resume, the intention unchanged: the reading is not served again
- (f) the intention edited between two wake-ups of the same run -- no start, no reset: the next wake-up, under the
  same key, serves the new body and never the old one; a body written under `TEAM.md` is never served
- (g) the team's document: its head serves itself, with `next:` and `decide:` under entries alone; its body the
  intention as the owner wrote it, kept to the byte by a start; a team without `TEAM-<name>.md` refuses
  `team-document-missing`, nothing written
- (h) a run of the same agent opened without the team's root never reads the intention
- (i) `team-started` keeps no `intention`, its `digest` stays; a journal written with the field reads; the face
  says a `TEAM.md` changed since the start
"""
from __future__ import annotations

import json
import re
import threading

from tests.harness import cli, support

T = support(__file__, "team")
OWN_TURN = "---\nname: TURN\nconstraints.behavior: |\n  OX1  keep it short.\n---\n"
BODY = "Merge what is asked."
EDITED = "Merge and tag what is asked."
READING = "INFORMATION — TEAM-aim"
NOTE = "A note of the owner, never served."


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


def _outside(h, path: str) -> str:
    """-> what a run of the agent opened WITHOUT the team's root serves, chunk after chunk."""
    meta = h.meta_of(path)
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


def _document(h, name: str) -> str:
    own = h.teams / name / f"TEAM-{name}.md"
    return own.read_text(encoding="utf-8") if own.is_file() else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "fa": {"T1": [{"sleep": 0.1, "body": {"do": ["pa"]}},
                      {"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "standup"}}]},
        "lead": {"T1": [{"sleep": 0.1, "body": {"done": "one"}}],
                 "T2": [{"sleep": 0.1, "body": {"done": "two"}}],
                 "T3": [{"sleep": 0.1, "body": {"done": "three"}}]}})
    by_kind, all_ended, runs_launched = T.by_kind, T.all_ended, T.runs_launched
    ended_on = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)

    # --- every team declared and started before the first wait --------------------------------------------
    h.declare("files", "---\nagents: |\n  fa agents/fa\n  pa agents/pa\nreports: |\n  pa -> fa\nroot: fa\n"
                       "ceremonies: |\n  daily every weekday 09:30 with pa -> fa\n"
                       "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nKeep the files where the team lives.\n")
    (h.teams / "files" / "DAILY.md").write_text(T.DAILY_DOC, encoding="utf-8")
    h.declare("aim", f"---\nagents: |\n  lead agents/lead\nroot: lead\nschedule: off\n---\n{BODY}\n")
    h.declare("beat", "---\nagents: |\n  b agents/b\nroot: b\nentries: |\n  do -> WORK.md\nschedule: off\n---\n"
                      "Keep the beat.\n")
    (h.teams / "beat" / "WORK.md").write_text(T.WORK_DOC, encoding="utf-8")
    h.declare("mute", "---\nagents: |\n  q agents/q\nroot: q\nentries: |\n  do -> WORK.md\nschedule: off\n---\n")
    (h.teams / "mute" / "WORK.md").write_text(T.WORK_DOC, encoding="utf-8")
    h.declare("bare", "---\nagents: |\n  z agents/z\nroot: z\nschedule: off\n---\n")
    h.declare("old", "---\nagents: |\n  o agents/o\nroot: o\nschedule: off\n---\nThe old way.\n")
    h.call("agent", "add", "agents/pa")
    h.call("agent", "add", "agents/fa")
    earlier = _earlier(h, "agents/pa")
    retired = h.team_module().parent / "retired"                   # the law of team 0.39, laid in the team's directory
    former_law = h.teams / "files" / "TURN.md"
    former_law.write_bytes((retired / "agent-turn-0.39.txt").read_bytes())
    own = h.meta_of("agents/fa") / "procs" / "TURN.md"
    own.parent.mkdir(parents=True, exist_ok=True)
    own.write_text(OWN_TURN, encoding="utf-8")

    started = h.call("team", "start", "files", "--message", "first task", *h.harnessed, now="09:10")
    aimed = h.call("team", "start", "aim", "--message", "merge PR 11", *h.harnessed)
    # lead's second task is posted while its opening plays: the end of that wake-up resumes the same run on it
    second = h.call("team", "post", "aim", "--to", "lead", "--message", "merge PR 12")
    made = [h.call("team", "start", name, "--message", "x", *h.harnessed, "--no-tick")
            for name in ("beat", "mute", "bare")]
    started_event = (by_kind(h.events("aim"), "team-started") or [{}])[0]
    forged = {**started_event, "id": 1, "team": "old", "agents": {"o": "agents/o"}, "root": "o",
              "intention": "The old way.", "digest": "000000000000"}
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(json.dumps(forged) + "\n", encoding="utf-8")

    # --- the two chains, interleaved: files' task then its daily, aim's two tasks then the edited third ------
    first = h.settled("files", ended_on("T1"), timeout=60)
    rung = h.call("team", "tick", "files", now="09:31")
    resumed = h.settled("aim", ended_on("T2"), timeout=60)
    doc = h.teams / "aim" / "TEAM-aim.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace(BODY, EDITED), encoding="utf-8")
    declared = h.teams / "aim" / "TEAM.md"
    declared.write_text(declared.read_text(encoding="utf-8") + NOTE + "\n", encoding="utf-8")
    third = h.call("team", "post", "aim", "--to", "lead", "--message", "tag release 3")
    daily = h.settled("files", ended_on("T2"), timeout=60)
    edited = h.settled("aim", ended_on("T3"), timeout=60)

    outside = {}                                     # the two runs opened without a team's root, side by side
    openers = [threading.Thread(target=lambda path=path: outside.__setitem__(path, _outside(h, path)))
               for path in ("agents/pa", "agents/lead")]
    for one in openers:
        one.start()
    face = h.face("aim")
    old = h.face("old")
    for one in openers:
        one.join()

    # --- (a) the team's documents in its directory, none at the agents ------------------------------------
    found = h.events("files")
    key_pa = next((one.get("run") for one in by_kind(found, "wake-ended", agent="pa")), "")
    elected = h.elected("agents/pa", key_pa)
    directory = sorted(one.name for one in (h.teams / "files").iterdir() if one.is_file())
    at_pa = _team_files(h, "agents/pa")
    at_fa = _team_files(h, "agents/fa")
    if (started.returncode == 0 and first and rung.returncode == 0 and daily and key_pa
            and directory == ["DAILY.md", "TEAM-IDLE.md", "TEAM-files.md", "TEAM.md"]
            and "DAILY.md" in elected and at_pa == [] and at_fa == ["procs/TURN.md"]):
        held("(a) the team's documents in its directory", f"teams/files/ carries {directory}; pa's run {key_pa} "
             f"elects {elected}, DAILY.md laid in the team's directory alone; agents/pa carries none of the team, "
             "agents/fa its own TURN.md alone")
    else:
        failures.append(f"  ✗ (a) the team's directory      start={started.returncode} first={first} rung={rung.returncode} "
                        f"daily={daily} key={key_pa} directory={directory} elected={elected} pa={at_pa} fa={at_fa} "
                        f"{started.stderr[-300:]!r}")

    # --- (b) the contract in the standing orders -----------------------------------------------------------
    fragment = h.team_module().parents[2] / "system" / "SYSTEM.COMMON.md"
    contract = fragment.read_text(encoding="utf-8").split("---\n", 2)[-1].strip() if fragment.is_file() else ""
    marble = h.house / ".sys" / "system.common.md"
    marbled = marble.read_text(encoding="utf-8") if marble.is_file() else ""
    documents = [_document(h, name) for name in ("files", "aim", "beat", "mute", "bare")]
    kept = sorted(one.name for one in h.team_module().parent.glob("*.md"))
    if contract and contract in marbled and all(contract not in one for one in documents) and kept == ["SKILL.md", "agent-idle.md"]:
        held("(b) the contract in the standing orders", f"the house's marble carries team's SYSTEM.COMMON.md "
             f"({len(contract)} c); no team document carries it; the skill keeps {kept}")
    else:
        failures.append(f"  ✗ (b) the contract             fragment={fragment.is_file()} marbled={contract in marbled} "
                        f"in_documents={[contract in one for one in documents] if contract else None} kept={kept}")

    # --- (c) the files of an earlier start leave, the agent's own stays and is said -------------------------
    # no structured signal says a kept file: the start's stderr is read for the agent's path, the file and `kept`
    if (started.returncode == 0 and not any(one.exists() for one in earlier) and not former_law.exists()
            and "teams/files/TURN.md" in started.stderr and "removed" in started.stderr
            and own.read_text(encoding="utf-8") == OWN_TURN and "agents/fa" in started.stderr
            and "procs/TURN.md" in started.stderr and "kept" in started.stderr):
        held("(c) the files of an earlier start leave", f"{len(earlier)} files of the team's bytes removed from "
             "agents/pa, the law of team 0.39 removed from teams/files/ and said; agents/fa's own TURN.md kept, and said")
    else:
        failures.append(f"  ✗ (c) the earlier files         left={[str(one) for one in earlier if one.exists()]} "
                        f"law={former_law.exists()} own={own.read_text(encoding='utf-8') == OWN_TURN} {started.stderr[-300:]!r}")

    # --- (d) the opening: the intention served by pp, absent from the message --------------------------
    found = h.events("aim")
    prompts = h.prompts_of("lead")
    message, served = _split(prompts[0] if prompts else "")
    if (aimed.returncode == 0 and READING in served and BODY in served[served.find(READING):]
            and BODY not in message):
        held("(d) the opening serves the intention", f"lead's first prompt: `{READING}` and the body in pp's "
             f"output ({len(prompts[0])} c), the message ({len(message)} c) without it")
    else:
        failures.append(f"  ✗ (d) the opening              rc={aimed.returncode} reading={READING in served} "
                        f"in_message={BODY in message} {aimed.stderr[-200:]!r} {message[-300:]!r}")

    # --- (e) a resume, TEAM.md unchanged: nothing served again -------------------------------------------
    again = prompts[1] if len(prompts) > 1 else ""
    if second.returncode == 0 and resumed and again and READING not in again and BODY not in again:
        held("(e) a resume does not read it again", f"lead's second prompt ({len(again)} c): no `{READING}`, "
             "no body -- the reading proven in the run")
    else:
        failures.append(f"  ✗ (e) the unchanged resume     rc={second.returncode} resumed={resumed} "
                        f"prompts={len(prompts)} reading={READING in again} body={BODY in again}")

    # --- (f) the body edited mid-run: served at the next exchange, same key ------------------------------
    later = prompts[2] if len(prompts) > 2 else ""
    message3, served3 = _split(later)
    runs = runs_launched(found, "lead")
    if (third.returncode == 0 and edited and len(runs) == 1 and READING in served3 and EDITED in served3
            and BODY not in later and EDITED not in message3 and NOTE not in later
            and not by_kind(found, "team-started")[1:] and not by_kind(found, "run-reset")):
        held("(f) an edited body reaches the member mid-run", f"TEAM-aim.md rewritten, no start nor reset: lead's "
             f"third prompt, run {sorted(runs)[0]}, serves the new body, never the old one nor TEAM.md's note")
    else:
        failures.append(f"  ✗ (f) the edited body          rc={third.returncode} edited={edited} runs={runs} "
                        f"reading={READING in served3} new={EDITED in served3} old={BODY in later} note={NOTE in later}")

    # --- (g) the team's document, entries or not ---------------------------------------------------------
    aim_doc, beat_doc, mute_doc, bare_doc = (_document(h, name) for name in ("aim", "beat", "mute", "bare"))
    h.declare("nodoc", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nLost.\n")
    (h.teams / "nodoc" / "TEAM-nodoc.md").unlink(missing_ok=True)
    lost = h.call("team", "start", "nodoc", "--message", "x", "--no-tick")
    if (all(one.returncode == 0 for one in made)
            and "serve: |\n  TEAM-aim.md\n" in aim_doc and "attach: turn.begin" in aim_doc
            and "next:" not in aim_doc and "decide:" not in aim_doc and aim_doc.endswith(f"---\n{EDITED}\n")
            and "serve: |\n  TEAM-beat.md\n" in beat_doc and "next: WORK.md TEAM-IDLE.md" in beat_doc
            and "decide: pp-team entry beat" in beat_doc and beat_doc.endswith("---\nKeep the beat.\n")
            and "serve: |\n  TEAM-mute.md\n" in mute_doc and "decide: pp-team entry mute" in mute_doc
            and "serve: |\n  TEAM-bare.md\n" in bare_doc and "next:" not in bare_doc
            and lost.returncode == 2 and "team-document-missing" in lost.stderr
            and not h.journal_of("nodoc").exists() and not h.agent_stands("agents/n")):
        bench.refusals += 1
        held("(g) the team's document serves itself", "each head serves its own document, next and decide under "
             "entries alone; the bodies the owners' intentions to the byte; nodoc without its document refuses "
             "team-document-missing, no journal, no agent born")
    else:
        failures.append(f"  ✗ (g) the team's document      rc={[one.returncode for one in made]} aim={aim_doc!r} "
                        f"beat={beat_doc!r} mute={mute_doc!r} bare={bare_doc!r} lost={lost.returncode}:{lost.stderr[-200:]!r}")

    # --- (h) a run without the team's root never reads it ------------------------------------------------
    bare_lead = outside.get("agents/lead", "")
    if bare_lead and READING not in bare_lead and EDITED not in bare_lead and BODY not in bare_lead:
        held("(h) a run without the root does not read it", f"a run of agents/lead opened without "
             f"--documents ({len(bare_lead)} c): no `{READING}`, no body")
    else:
        failures.append(f"  ✗ (h) outside the team         {len(bare_lead)}c reading={READING in bare_lead} "
                        f"body={EDITED in bare_lead or BODY in bare_lead}")

    # --- (i) the journal keeps no copy; the face says a changed TEAM.md ------------------------------------
    if (started_event and "intention" not in started_event and len(str(started_event.get("digest") or "")) == 12
            and face.get("changed") is True and old.get("team") == "old"
            and (old.get("started") or {}).get("id") == 1 and old.get("changed") is True):
        held("(i) the journal keeps no copy", f"team-started without `intention`, digest "
             f"{started_event.get('digest')}; aim's face: changed since the start; a journal with the field reads "
             "(old's face, its start #1)")
    else:
        failures.append(f"  ✗ (i) the journal              keys={sorted(started_event)} changed={face.get('changed')!r} "
                        f"old={ {key: old.get(key) for key in ('team', 'started', 'changed')} }")
    return 0
