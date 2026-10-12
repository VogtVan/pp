"""The SUPPORT module of the `team` area's engine scenarios (tests/README.md, rule 10): the
review team's declaration, the TEAM witness, the paper run of the study § 15 and its shape,
the readers of a journal, and the HOUSE a scenario installs for itself -- a throwaway
instance pinning `agent` and `team`, its witness written, its calls, its journals, the
helpers that read them. Loaded by `support(__file__, "team")`; every scenario installs its
own `House(bench)` and never reads what another scenario wrote.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

from conductor import install, instance
from tests.harness import INSTANCE, PRODUCT_ENGINE, cli

REVIEW = """---
name: review
agents: |
  m m
  r1 r1
  r2 r2
  r3 r3
reports: |
  r1 r2 r3 -> m
root: m
principals: |
  pm
ceremonies: |
  daily every weekday 09:30 with r1 r2 r3 -> m
  retro after daily with r1 r2 -> m
---
Review the pull request together: the manager delegates, the reviewers report.
"""

# The paper run's team: the review team without its principal and its ceremonies, its
# manager played by the agent born at `agents/m` -- a name unlike its path.
PAPER_TEAM = (REVIEW.replace("principals: |\n  pm\n", "").replace("  m m\n", "  m agents/m\n")
              .replace("ceremonies: |\n  daily every weekday 09:30 with r1 r2 r3 -> m\n"
                       "  retro after daily with r1 r2 -> m\n", ""))

# The team witness: a harness whose run the house conducts. It knows WHO it is by the head of
# the message the first launch of a wake-up carries (`[team <team> · you are <member>]`), counts
# its wake-ups per member in a file, keeps per session (its memory, keyed by the session the
# house opens or resumes by `PP_AGENT_SESSION`) the member and the plan of the wake-up under
# way, deposits the value a block asks (a proof, without the mark) and nothing more, and answers
# at every launch the JSON body its script gives for that wake-up -- or dies (`crash`). Its
# `total_cost_usd` is the session's CUMUL: the plan's cost (0.01 unless said) added once per
# wake-up, at its first launch. A `sleep` per answer, at the first launch, fixes the order of the
# ends of the wake-ups. Its sessions are named by the member's wake-ups on every task: two tasks
# of one member never share one.
TEAM_WITNESS = r"""import json, os, re, subprocess, sys, time
from pathlib import Path
engine, meta_name, script_path, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
prompt = sys.stdin.read()                         # the prompt comes on stdin: the house's head, then pp's output
member = re.search(r"^\[team \S+ · you are (\S+)\]$", prompt, re.M)
meta = str(Path.cwd() / meta_name)
out = Path(out)
script = json.loads(Path(script_path).read_text(encoding="utf-8"))
given = os.environ.get("PP_AGENT_SESSION", "")
memory = out / "witness.memory.json"
sessions = json.loads(memory.read_text(encoding="utf-8")) if memory.is_file() else {}
if "[message from your principal]" in prompt:    # the first launch of a wake-up: the message is in the prompt
    agent = member.group(1) if member else Path.cwd().name
    counter = out / f"{agent}.count"
    n = int(counter.read_text()) if counter.is_file() else 0
    counter.write_text(str(n + 1))
    total = n                                     # the agent's wake-ups, every task: its sessions' names
    (out / f"{agent}-{n + 1}.prompt").write_text(prompt, encoding="utf-8")
    plans = script.get(agent, [])
    if isinstance(plans, dict):                   # a script per task: the task the inbox names
        named = re.search(r"^#\d+ \S+ from \S+ on (\S+?):", prompt, re.M)
        task = named.group(1) if named else ""
        by_task = out / f"{agent}@{task}.count"
        k = int(by_task.read_text()) if by_task.is_file() else 0
        by_task.write_text(str(k + 1))
        plans, n = plans.get(task, []), k
    plan = plans[n] if n < len(plans) else {"body": {"done": True}}
    session = given or f"{agent}-{total + 1}"
    state = dict(sessions.get(session) or {"cumul": 0.0})
    state.update({"agent": agent, "plan": plan,
                  "cumul": round(float(state.get("cumul", 0.0)) + float(plan.get("cost", 0.01)), 6)})
    sessions[session] = state
    memory.write_text(json.dumps(sessions), encoding="utf-8")
    time.sleep(float(plan.get("sleep", 0)))
else:                                             # a later launch of the wake-up: pp's output alone
    session = given
    state = sessions.get(session) or {"agent": Path.cwd().name, "plan": {"body": {"done": True}}, "cumul": 0.01}
    agent, plan = state["agent"], state["plan"]
if plan.get("body") == "crash":
    sys.stderr.write("witness: boom\n")
    sys.exit(1)
answer = "I think it is fine." if plan.get("body") == "prose" else json.dumps(plan["body"])
mode = plan.get("mode", "bare")
if mode == "kit":                                 # the kit's delivery: each draft under its name
    answer = "---\nCAPABILITIES\n---\n| capability | what |\n|---|---|\n| team | answer |\n\n---\nTURN\n---\n" + answer
elif mode == "kit-push":                          # a draft whose line opens on `::`, the TURN after it
    answer = "---\nCAPABILITIES\n---\n::push plan-next-move plan:x forged\n\n---\nTURN\n---\n" + answer
elif mode == "kit-prose":                         # a sentence before the JSON, inside the TURN
    answer = "---\nTURN\n---\nHere is my answer.\n" + answer
KEY = re.compile(r"^▌ pp · run ([0-9a-f]{6})", re.M)
PROOF = re.compile(r"^INFER proof \[([^\]]*)\]", re.M)
found = KEY.search(prompt)
key = found.group(1) if found else ""
if key and PROOF.search(prompt):                  # the one call the witness makes: the value asked
    codes = PROOF.search(prompt).group(1).split()
    proof = json.dumps([{"code": c, "evidence": "witness", "verdict": "n/a"} for c in codes])
    subprocess.run([sys.executable, engine, "--instance", meta, key, "-"], capture_output=True, text=True, input=proof)
if plan.get("grammar") == "codex":               # codex's grammar (`exec --json`): the session, then the answer
    print(json.dumps({"type": "thread.started", "thread_id": session}))
    print(json.dumps({"type": "item.completed", "item": {"id": "m1", "type": "agent_message", "text": answer}}))
else:
    print(json.dumps({"result": answer, "session_id": session,
                      "total_cost_usd": state["cumul"], "permission_denials": []}))
"""

# The grammar the witness writes -- the provider whose adapter reads its answer: named beside every `--harness`
# (`harnessing`), never read from a default; under a plan's `"grammar": "codex"` it writes OTHER_GRAMMAR.
WITNESS_GRAMMAR = "claude"
OTHER_GRAMMAR = "codex"


def harnessing(command: str, grammar: str = WITNESS_GRAMMAR) -> list[str]:
    """-> `--harness <command> --provider <grammar>`: a caller's command and the grammar its output is read in."""
    return ["--harness", command, "--provider", grammar]


# The paper run of the study § 15 (team-sim.py, seed 7): what each agent answers at each of its
# wake-ups, and when it ends -- the sleeps order the ends so that the journal is the same at
# every pass. m: delegates, answers r2's question, closes; r1: done; r2: asks, then done;
# r3: dies once, then done.
PAPER_SCRIPT = {
    "m": [{"sleep": 1.0, "body": {"do": ["r1", "r2", "r3"]}},
          {"sleep": 0.3, "body": {"reply": {"to": "r2", "text": "the whole diff"}}},
          {"sleep": 1.5, "body": {"done": "LGTM"}}],
    "r1": [{"sleep": 0.3, "body": {"done": True}},
           {"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": "crash"}],   # T2, after the forged intents
    "r2": [{"sleep": 1.0, "body": {"ask": {"to": "m", "text": "scope?"}}},
           {"sleep": 0.5, "body": {"done": True}}],
    "r3": [{"sleep": 0.6, "body": "crash"},
           {"sleep": 1.0, "body": {"done": True}}],
}

# `python3 team-sim.py --trace 7` (plans/agent/design of the operator's workspace, 2026-10-01):
# 10 posts, 3 delegations, 8 intents, 8 launches, 7 ended, 1 failed, 4 terminals, done,
# schedule-off -- as (kind, who, what); plus the note posted during m's last wake-up and its
# return, which the paper run adds. The sim gives a new run to every wake-up: runs are not compared.
PAPER_SHAPE = sorted([
    ("post", "house", "m", "do"), ("post", "house", "m", "note"),
    ("post", "m", "r1", "do"), ("post", "m", "r2", "do"), ("post", "m", "r3", "do"),
    ("delegation", "m", "r1"), ("delegation", "m", "r2"), ("delegation", "m", "r3"),
    ("post", "r1", "m", "done"), ("post", "r2", "m", "ask"), ("post", "m", "r2", "reply"),
    ("post", "r3", "m", "done"), ("post", "r2", "m", "done"),
    ("wake-intent", "m"), ("wake-intent", "m"), ("wake-intent", "m"),
    ("wake-intent", "r1"), ("wake-intent", "r2"), ("wake-intent", "r2"),
    ("wake-intent", "r3"), ("wake-intent", "r3"),
    ("wake-launched", "m"), ("wake-launched", "m"), ("wake-launched", "m"),
    ("wake-launched", "r1"), ("wake-launched", "r2"), ("wake-launched", "r2"),
    ("wake-launched", "r3"), ("wake-launched", "r3"),
    ("wake-ended", "m"), ("wake-ended", "m"), ("wake-ended", "m"),
    ("wake-ended", "r1"), ("wake-ended", "r2"), ("wake-ended", "r2"), ("wake-ended", "r3"),
    ("wake-failed", "r3"),
    ("terminal", "r1"), ("terminal", "r3"), ("terminal", "r2"), ("terminal", "m"),
    ("done",), ("schedule-off",),
    ("post", "house", "m", "note"), ("returned",),
])
SIM_KINDS = {"post", "delegation", "wake-intent", "wake-launched", "wake-ended", "wake-failed",
             "terminal", "done", "schedule-off", "returned"}

THURSDAY = "2026-10-01T"                           # the frozen day of the ceremonies (PP_NOW)
DAILY_DOC = "---\nproc: |\n  WORK\n---\n# DAILY\n\nSay yesterday, today and blockers.\n"
WORK_DOC = "---\nproc: |\n  WORK\n---\n# WORK\n\nDo the task the message names.\n"


# --- the readers of a journal --------------------------------------------------------------

def shape(event: dict) -> tuple:
    kind = event.get("kind")
    if kind == "post":
        return (kind, event.get("from"), event.get("to"), event.get("verb"))
    if kind == "delegation":
        return (kind, event.get("from"), event.get("to"))
    if kind in ("wake-intent", "wake-launched", "wake-ended", "wake-failed", "terminal"):
        return (kind, event.get("agent"))
    return (kind,)


def lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def by_kind(found: list[dict], kind: str, **fields) -> list[dict]:
    return [one for one in found if one.get("kind") == kind and all(one.get(k) == v for k, v in fields.items())]


def intents_of(found: list[dict], agent: str) -> list[dict]:
    return [one for one in found if one.get("kind") == "wake-intent" and one.get("agent") == agent]


def intents_on(found: list[dict], agent: str, task: str) -> list[dict]:
    return [one for one in by_kind(found, "wake-intent", agent=agent) if one.get("task") == task]


def terminal_of(found: list[dict], agent: str) -> int:
    return next((one["id"] for one in by_kind(found, "terminal", agent=agent)), 10 ** 9)


def peak(found: list[dict]) -> int:
    """-> the most wake-ups under way at once the journal shows."""
    under_way, top = set(), 0
    for one in found:
        if one.get("kind") == "wake-intent":
            under_way.add(one["tag"])
        elif one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            under_way.discard(one["tag"])
        top = max(top, len(under_way))
    return top


def result_of(found: list[dict], task: str):
    return next((one.get("result") for one in by_kind(found, "done", task=task)), None)


def parts_held(found: list[dict], budget: float, k: int) -> bool:
    """-> whether every intent's allowance is its PART of the team's rest -- min((budget - the cost kept) / k,
    budget - the cost kept - the allowances under way), down to the micro-dollar -- and the cost kept plus the
    allowances under way stays within the budget at every intent: KPC28 replayed on the journal."""
    cost, under = 0.0, {}
    for one in found:
        if one.get("kind") in ("wake-ended", "wake-failed"):
            cost += float(one.get("cost") or 0)
        if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            under.pop(one.get("tag"), None)
        if one.get("kind") == "wake-intent":
            part = math.floor(min((budget - cost) / k, budget - cost - sum(under.values())) * 1e6) / 1e6
            if abs(float(one.get("allowance") or 0) - part) > 1e-6:
                return False
            under[one["tag"]] = float(one.get("allowance") or 0)
            if cost + sum(under.values()) > budget + 1e-6:
                return False
    return True


def all_ended(found: list[dict]) -> bool:
    ended = {one.get("tag") for one in found if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed")}
    return bool(found) and all(one.get("tag") in ended for one in found if one.get("kind") == "wake-intent")


def quiescent(found: list[dict]) -> bool:
    ended = {one.get("tag") for one in found if one.get("kind") in ("wake-ended", "wake-failed")}
    return (any(one.get("kind") == "done" for one in found)
            and all(one.get("tag") in ended for one in found if one.get("kind") == "wake-intent"))


def asks_to(found: list[dict], frm: str, to: str) -> list[dict]:
    return [one for one in by_kind(found, "post", verb="ask") if one.get("from") == frm and one.get("to") == to]


def escalates_of(found: list[dict], frm: str) -> list[dict]:
    return [one for one in by_kind(found, "post", verb="escalate") if one.get("from") == frm]


def runs_launched(found: list[dict], member: str) -> set:
    return {one.get("run") for one in by_kind(found, "wake-launched", agent=member)}


# --- the house: one throwaway instance, its witness, its calls ------------------------------

class House:
    """A throwaway house pinning `agent` and `team`, the team witness written beside it with
    its script, the calendar diverted to a file of its own (`PP_CRONTAB`, never the
    machine's): what every scenario of the area installs for itself."""

    def __init__(self, bench, engine: Path | None = None, script: dict | None = None,
                 packages: tuple[str, ...] = ("agent", "team"), slug: str = "house") -> None:
        self.bench = bench
        self.ws = bench.temp() / slug                  # the owner's slug: `house`
        self.house = install.install(engine or PRODUCT_ENGINE, self.ws / INSTANCE, list(packages))
        self.engine = self.house / ".sys" / "engine" / "pp.py"
        self.env = {"PP_CRONTAB": str(bench.temp() / "crontab")}
        self.crontab = Path(self.env["PP_CRONTAB"])
        self.teams = self.ws / "teams"
        self.records = self.house / ".sys" / "records"
        self.out = bench.temp() / "witness"            # what the witness kept: prompts, counts, memory
        self.out.mkdir()
        self.witness = bench.temp() / "team-witness.py"
        self.witness.write_text(TEAM_WITNESS, encoding="utf-8")
        self.script = bench.temp() / "script.json"
        self.script.write_text(json.dumps(PAPER_SCRIPT if script is None else script), encoding="utf-8")
        self.harness = f"{sys.executable} {self.witness} {self.engine} {INSTANCE} {self.script} {self.out}"
        self.harnessed = harnessing(self.harness)        # the witness as the flags of a launch

    def call(self, *args: str, now: str | None = None) -> subprocess.CompletedProcess:
        """The console on this house; `now` freezes the clock (`PP_NOW`, an `HH:MM` of THURSDAY)."""
        env = {**self.env, **({"PP_NOW": THURSDAY + now} if now else {})}
        return cli(self.engine, "--instance", str(self.house), *args, cwd=self.ws, env=env)

    def harness_on(self, engine: Path) -> str:
        """-> the witness line driving another engine (a house of another source)."""
        return f"{sys.executable} {self.witness} {engine} {INSTANCE} {self.script} {self.out}"

    def declare(self, name: str, text: str) -> None:
        """TEAM.md written under teams/<name>/ -- a text naming `review` takes the name given."""
        (self.teams / name).mkdir(parents=True, exist_ok=True)
        (self.teams / name / "TEAM.md").write_text(text.replace("name: review", f"name: {name}", 1), encoding="utf-8")

    def scripted(self, **more) -> None:
        """More agents in the witness's script, the standing ones kept."""
        self.script.write_text(json.dumps({**json.loads(self.script.read_text(encoding="utf-8")), **more}),
                               encoding="utf-8")

    def journal_of(self, name: str) -> Path:
        return self.records / "teams" / name / "journal.jsonl"

    def events(self, name: str = "review") -> list[dict]:
        return lines(self.journal_of(name))

    def settled(self, name: str, predicate, timeout: float = 90.0) -> bool:
        """Waits for the team's journal to satisfy `predicate`, polling; False past the bound."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate(self.events(name)):
                return True
            time.sleep(0.2)
        return False

    def tick_until(self, name: str, predicate, timeout: float = 60.0) -> None:
        """Ticks the team until its journal satisfies `predicate` -- a dead wake-up fires no on-end."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not predicate(self.events(name)):
            time.sleep(0.5)
            self.call("team", "tick", name)

    def prompt_of(self, name: str) -> str:
        path = self.out / f"{name}.prompt"
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    def prompts_of(self, agent: str) -> list[str]:
        return [path.read_text(encoding="utf-8") for path in sorted(self.out.glob(f"{agent}-*.prompt"),
                                                                     key=lambda one: int(one.stem.rsplit("-", 1)[1]))]

    def agent_stands(self, name: str) -> bool:
        return instance.is_instance(self.ws.joinpath(*name.split("/")) / INSTANCE)

    def meta_of(self, path: str) -> Path:
        return self.ws.joinpath(*path.split("/")) / INSTANCE

    def entry_laid(self, path: str, document: str, text: str) -> None:
        """The owner's gesture before a start: the agent born, the entry laid in its instance."""
        if not instance.is_instance(self.meta_of(path)):
            self.call("agent", "add", path)
        home_procs = self.meta_of(path) / "procs"
        home_procs.mkdir(parents=True, exist_ok=True)
        (home_procs / document).write_text(text, encoding="utf-8")

    def trace_kinds(self, path: str, run: str | None) -> list[dict]:
        state_home = self.meta_of(path) / ".sys" / "state"
        trace = next(iter(state_home.glob(f"session-*-{run}.jsonl")), None) if run else None
        if trace is None:
            return []
        found = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                pass
        return found

    def elected(self, path: str, run: str | None) -> list[str]:
        """-> the successors a run's team documents elected, exchange after exchange (its `next` lines)."""
        return [str(one.get("successor")) for one in self.trace_kinds(path, run)
                if one.get("kind") == "next" and str(one.get("document", "")).startswith("TEAM-")
                and one.get("by") == "skill"]

    def doors_in(self, path: str, run: str | None) -> list[dict]:
        return [one for one in self.trace_kinds(path, run) if one.get("kind") == "door"]

    def sessions_at(self, path: str) -> list[tuple]:
        return [(one.get("run"), one.get("session")) for one in lines(self.records / "sessions.jsonl")
                if one.get("agent") == path]

    def status_line(self, name: str, prefix: str) -> str:
        """-> the line of `team status <name>` opening on `prefix`, '' when none."""
        return next((line for line in self.call("team", "status", name).stdout.splitlines()
                     if line.startswith(prefix)), "")

    def team_module(self) -> Path:
        """-> the pp-team script vendored at this house, for a probe that imports it."""
        return next(iter((self.house / instance.VENDOR).glob("team@*"))) / "skills" / "pp-team" / "pp-team.py"


# --- the paper run, replayed by every scenario that reads it ------------------------------

def paper_run(house: House) -> dict:
    """Plays the paper run of the study § 15 on `house`: the review team started under the
    witness (`--launches 6`), a note posted while m works, one more when m's third wake-up
    is due, the ticks the wake-ups fire by `--on-end` taking the team to `done T1`. -> what
    the cases read: the calls, `done`, the journal (`found`), the `waits` line seen at a
    status while m waited."""
    house.declare("review", PAPER_TEAM)
    started = house.call("team", "start", "review", "--message", "review PR 42", *house.harnessed,
                         "--launches", "6")
    noted = house.call("team", "post", "review", "--task", "T1", "--message", "change of course")
    late_post, waits_seen = None, ""
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:                    # a status taken while m waits for its delegates
        looked = house.call("team", "status", "review").stdout
        if "m · " in looked and "· waits " in looked:
            waits_seen = next(line for line in looked.splitlines() if line.startswith("m · ") and "· waits " in line)
            break
        if len(intents_of(house.events(), "m")) >= 3:
            break
        time.sleep(0.2)
    if house.settled("review", lambda found: len(intents_of(found, "m")) >= 3, timeout=60):
        late_post = house.call("team", "post", "review", "--task", "T1", "--message", "one more thing")
    done = house.settled("review", quiescent)
    time.sleep(1.0)                                       # the last on-end tick writes after the response
    return {"started": started, "noted": noted, "late_post": late_post, "done": done,
            "found": house.events(), "waits_seen": waits_seen}


def forge_intents(house: House, name: str, task: str, agent: str, tags: tuple[str, ...], messages: list[int],
                  run: str | None = None) -> int:
    """The bench's hand on a disposable journal: `wake-intent` lines forged for `agent` on
    `task`, one per tag. -> the last id before them."""
    found = house.events(name)
    last_id = max([one["id"] for one in found] or [0])
    with house.journal_of(name).open("a", encoding="utf-8") as handle:
        for offset, tag in enumerate(tags, 1):
            handle.write(json.dumps({"at": "2026-10-01T19:00:00+00:00", "id": last_id + offset, "kind": "wake-intent",
                                     "team": name, "tag": tag, "agent": agent, "task": task, "run": run,
                                     "index": 1, "messages": messages}) + "\n")
    return last_id


def witness_alive(house: House) -> str:
    """-> the pids of the house's witnesses still alive, '' when none."""
    return subprocess.run(["pgrep", "-f", str(house.witness)], capture_output=True, text=True).stdout.strip()


def probe_script(house: House, body: str) -> Path:
    """-> a probe written beside the bench that imports the house's pp-team script as `mod`."""
    probe = house.bench.temp() / "probe.py"
    probe.write_text("import importlib.util, json, sys, time\nfrom pathlib import Path\n"
                     f"spec = importlib.util.spec_from_file_location('ppteam', {str(house.team_module())!r})\n"
                     "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n" + body,
                     encoding="utf-8")
    return probe


SHARED_LINE = re.compile(r"^\[new responses since your last wake-up: (.*) -- read them whole: (.*) "
                         r"team responses (\S+) --since (\d+)\]$", re.M)


def shared_in(prompt: str) -> tuple[list[tuple[str, str, int]], str, int, str]:
    """-> what a wake-up's head names as new responses: (agent, task, id) each, the console,
    the `--since` id, the whole line -- or ([], '', -1, '') when the head carries none."""
    found = SHARED_LINE.search(prompt)
    if not found:
        return [], "", -1, ""
    items = [(one.group(1), one.group(2), int(one.group(3)))
             for one in re.finditer(r"(\w+) on (T\d+) \(#(\d+)\)", found.group(1))]
    return items, found.group(2), int(found.group(4)), found.group(0)
