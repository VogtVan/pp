"""Scenario `team-files` -- 3 case(s) (batch les-fichiers-sous-l-equipe, 2026-10-10): a team plays from
ITS directory, `teams/<name>/`, the root of documents of every run it opens -- nothing of it is written
in an agent's instance.
- (a) the team's documents in its directory: `team start` writes `TURN.md`, `TEAM-<name>.md` and
  `TEAM-IDLE.md` under `teams/<name>/`; a task and a daily played, the daily's entry laid in the team's
  directory ALONE is elected in the member's run; the agents carry no file of the team
- (b) the law TJ1 in the team's runs alone: a wake-up of the team reads TJ1 in its block; a run of the
  same agent opened without the team's root does not
- (c) the files of an earlier start leave: the team's bytes laid at an agent (`procs/TURN.md`,
  `procs/TEAM-IDLE.md`, `procs/TEAM-<name>.md`, `skills/team-entry/`) are removed at the start; an
  agent's own `procs/TURN.md` stays, and is said
"""
from __future__ import annotations

import re
import time

from tests.harness import cli, support

T = support(__file__, "team")
OWN_TURN = "---\nname: TURN\nconstraints.behavior: |\n  OX1  keep it short.\n---\n"


def _earlier(h, path: str) -> list:
    """Lays at `path` what a start before this version laid there, the team's very bytes: the overlay, the
    neutral, the team's document, the decider skill -> the files laid."""
    here = h.team_module().parent
    retired = here / "retired" if (here / "retired").is_dir() else here
    laid = []
    for source, where in (("agent-turn.md", ("procs", "TURN.md")), ("agent-idle.md", ("procs", "TEAM-IDLE.md")),
                          ("agent-entry.md", ("skills", "team-entry", "SKILL.md")),
                          ("agent-entry.py", ("skills", "team-entry", "team-entry.py"))):
        origin = (here if source in ("agent-turn.md", "agent-idle.md") else retired) / source
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


def _block(h, path: str) -> str:
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


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "fa": {"T1": [{"sleep": 0.1, "body": {"do": ["pa"]}},
                      {"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "standup"}}]}})
    by_kind, all_ended = T.by_kind, T.all_ended

    h.declare("files", "---\nagents: |\n  fa agents/fa\n  pa agents/pa\nreports: |\n  pa -> fa\nroot: fa\n"
                       "ceremonies: |\n  daily every weekday 09:30 with pa -> fa\n"
                       "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nKeep the files where the team lives.\n")
    (h.teams / "files" / "DAILY.md").write_text(T.DAILY_DOC, encoding="utf-8")
    h.call("agent", "add", "agents/pa")
    h.call("agent", "add", "agents/fa")
    earlier = _earlier(h, "agents/pa")
    own = h.meta_of("agents/fa") / "procs" / "TURN.md"
    own.parent.mkdir(parents=True, exist_ok=True)
    own.write_text(OWN_TURN, encoding="utf-8")

    started = h.call("team", "start", "files", "--message", "first task", *h.harnessed, now="09:10")
    first = h.settled("files", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    rung = h.call("team", "tick", "files", now="09:31")
    daily = h.settled("files", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found = h.events("files")
    key_pa = next((one.get("run") for one in by_kind(found, "wake-ended", agent="pa")), "")
    elected = h.elected("agents/pa", key_pa)
    directory = sorted(one.name for one in (h.teams / "files").iterdir() if one.is_file())

    # --- (a) the team's documents in its directory, none at the agents ------------------------------------
    at_pa = _team_files(h, "agents/pa")
    at_fa = _team_files(h, "agents/fa")
    if (started.returncode == 0 and first and rung.returncode == 0 and daily and key_pa
            and directory == ["DAILY.md", "TEAM-IDLE.md", "TEAM-files.md", "TEAM.md", "TURN.md"]
            and "DAILY.md" in elected and at_pa == [] and at_fa == ["procs/TURN.md"]):
        held("(a) the team's documents in its directory", f"teams/files/ carries {directory}; pa's run {key_pa} "
             f"elects {elected}, DAILY.md laid in the team's directory alone; agents/pa carries none of the team, "
             "agents/fa its own TURN.md alone")
    else:
        failures.append(f"  ✗ (a) the team's directory      start={started.returncode} first={first} rung={rung.returncode} "
                        f"daily={daily} key={key_pa} directory={directory} elected={elected} pa={at_pa} fa={at_fa} "
                        f"{started.stderr[-300:]!r}")

    # --- (b) TJ1 in the team's runs alone ------------------------------------------------------------------
    woken = "\n".join(h.prompts_of("pa"))
    bare = _block(h, "agents/pa")
    if "TJ1" in woken and bare and "TJ1" not in bare:
        held("(b) TJ1 in the team's runs alone", "pa's wake-up of the team reads TJ1; a run of agents/pa opened "
             "without the team's root does not")
    else:
        failures.append(f"  ✗ (b) TJ1 in the team's runs    woken={'TJ1' in woken} bare={len(bare)}c "
                        f"bare_tj1={'TJ1' in bare}")

    # --- (c) the files of an earlier start leave, the agent's own stays and is said -------------------------
    if (started.returncode == 0 and not any(one.exists() for one in earlier)
            and own.read_text(encoding="utf-8") == OWN_TURN and "agents/fa" in started.stderr
            and "kept" in started.stderr):
        held("(c) the files of an earlier start leave", f"{len(earlier)} files of the team's bytes removed from "
             "agents/pa; agents/fa's own TURN.md kept, and said")
    else:
        failures.append(f"  ✗ (c) the earlier files         left={[str(one) for one in earlier if one.exists()]} "
                        f"own={own.read_text(encoding='utf-8') == OWN_TURN} {started.stderr[-300:]!r}")
    return 0
