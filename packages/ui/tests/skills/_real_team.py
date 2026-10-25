"""_real_team -- what the scenarios of the Teams tab at the REAL of the bench share (rule 10): a throwaway
house pinning `ui` (so `agent` and `team`), the team `essai` declared under it -- `lead` its root, `dev` and
`rev` reporting to it, `pm` a principal, a ceremony `daily` of `dev` and `rev` facilitated by `lead`, no
calendar line (`schedule: off`) --, the team witness of `team` (its support's `TEAM_WITNESS`) written beside it
with its script and handed to every wake-up by `--harness` with the grammar it writes, never a provider
launched; the calendar diverted to a file of the bench (`PP_CRONTAB`) and the clock frozen on a Thursday at
08:00 (`PP_NOW`), before the daily's hour, so that no tick rings it on its own. `render` plays `./pp ui … --
--harness <the witness> --provider <its grammar>` there, `call` the console; the readers of a team's
journal, of `team status --json` and of the witness's processes; `edit`, the owner's edit of `TEAM.md`. A house may
declare `essai` otherwise (`BUDGETED`: under `budget: 3`)."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from conductor import contributions
from tests.harness import INSTANCE, SOURCE, cli

W = contributions.module_at(SOURCE / "packages" / "team" / "tests" / "engine" / "_team.py")
WITNESS_GRAMMAR = W.WITNESS_GRAMMAR   # the grammar the team witness writes, named beside its `--harness`
TEAM = "essai"
NOW = "2026-10-01T08:00"             # a Thursday, before the daily's 09:30: no tick rings it on its own
DECLARED = """---
name: essai
agents: |
  lead agents/lead
  dev agents/dev
  rev agents/rev
reports: |
  dev rev -> lead
root: lead
principals: |
  pm
ceremonies: |
  daily every weekday 09:30 with dev rev -> lead
schedule: off
---
Try the post on the real verbs of team.
"""
BUDGETED = DECLARED.replace("schedule: off\n", "schedule: off\nbudget: 3\n")


def lines(path: Path) -> list[dict]:
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()] if path.is_file() else []


class RealTeam:
    """One house, the team `essai` declared, the team witness and its script: what each real scenario of the
    Teams tab installs for itself."""

    def __init__(self, bench, name: str, script: dict, declared: str = DECLARED) -> None:
        env = bench.env(name, packages=("ui",))
        self.made, self.engine = env.made, env.engine
        self.ws = env.made.parent
        (self.ws / "teams" / TEAM).mkdir(parents=True)
        (self.ws / "teams" / TEAM / "TEAM.md").write_text(declared, encoding="utf-8")
        self.out = bench.temp() / f"{name}-witness"
        self.out.mkdir()
        self.witness = bench.temp() / f"{name}-team-witness.py"
        self.witness.write_text(W.TEAM_WITNESS, encoding="utf-8")
        self.script = bench.temp() / f"{name}-script.json"
        self.script.write_text(json.dumps(script), encoding="utf-8")
        self.harness = f"{sys.executable} {self.witness} {self.engine} {INSTANCE} {self.script} {self.out}"
        self.harnessed = W.harnessing(self.harness, WITNESS_GRAMMAR)   # the witness as the flags of a launch
        self.crontab = bench.temp() / f"{name}-crontab"
        self.env = {"PP_CRONTAB": str(self.crontab), "PP_NOW": NOW}

    def render(self, *args: str):
        """`./pp ui <args> -- --harness <the witness> --provider <its grammar>` in the house."""
        return cli(self.engine, "ui", *args, "--", *self.harnessed, cwd=self.ws, env=self.env)

    def call(self, *args: str):
        """The house's console, under the bench's calendar and clock."""
        return cli(self.engine, *args, cwd=self.ws, env=self.env)

    def start(self, message: str = "go", *more: str):
        """`team start essai` by the console, the witness as the harness of every wake-up."""
        return self.call("team", "start", TEAM, "--message", message, *self.harnessed, *more)

    def edit(self, old: str, new: str, team: str = TEAM) -> None:
        """The owner's edit of `teams/<team>/TEAM.md`, in the house: `old` replaced by `new`."""
        path = self.ws / "teams" / team / "TEAM.md"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

    # ---------- what the team wrote ----------
    def events(self, team: str = TEAM) -> list[dict]:
        return lines(self.made / ".sys" / "records" / "teams" / team / "journal.jsonl")

    def kinds(self, kind: str, team: str = TEAM, **fields) -> list[dict]:
        return [one for one in self.events(team) if one.get("kind") == kind
                and all(one.get(key) == value for key, value in fields.items())]

    def settled(self, predicate, timeout: float = 30.0, team: str = TEAM) -> bool:
        """Waits for the team's journal to satisfy `predicate`, polling; False past the bound."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate(self.events(team)):
                return True
            time.sleep(0.2)
        return False

    def state(self, team: str = TEAM) -> dict:
        """-> `team status <team> --json`, the face the post reads."""
        played = self.call("team", "status", team, "--json")
        return json.loads(played.stdout) if played.returncode == 0 and played.stdout.strip() else {}

    def face(self, *verb: str) -> dict:
        """-> the one JSON object a face of the console prints (`team declaration essai --json`), {} otherwise."""
        played = self.call(*verb)
        return json.loads(played.stdout) if played.returncode == 0 and played.stdout.strip() else {}

    def responses(self) -> list[dict]:
        return lines(self.made / ".sys" / "records" / "responses.jsonl")

    def alive(self) -> list[str]:
        """-> the processes of this house's team witness still running."""
        found = subprocess.run(["pgrep", "-af", str(self.witness)], capture_output=True, text=True)
        return [one for one in found.stdout.splitlines() if "pgrep" not in one]


def asking(bench, name: str, declared: str = DECLARED) -> tuple["RealTeam", dict, str, bool]:
    """A team where `dev`, delegated T1 by `lead`, asks the OWNER a question, then waits for the reply: started
    without a tick, the owner read from the face, the witness's script written, one tick -- the journal waited
    until the question is posted and both wake-ups ended. -> the team, the `ask` post, the owner, and
    whether the start was played."""
    team = RealTeam(bench, name, {}, declared)
    begun = team.start("go", "--no-tick")
    owner = team.state().get("owner")
    team.script.write_text(json.dumps({
        "lead": {"T1": [{"body": {"do": ["dev"]}}, {"body": {"done": "replied"}}]},
        "dev": {"T1": [{"body": {"ask": {"to": owner, "text": "which branch?"}}}, {"body": {"done": True}}]}}),
        encoding="utf-8")
    team.call("team", "tick", TEAM)
    team.settled(lambda events: any(one.get("kind") == "post" and one.get("verb") == "ask" for one in events)
                 and sum(1 for one in events if one.get("kind") == "wake-ended") >= 2)
    ask = next((one for one in team.kinds("post", verb="ask")), {})
    return team, ask, owner, begun.returncode == 0
