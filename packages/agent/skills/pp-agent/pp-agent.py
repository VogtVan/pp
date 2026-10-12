#!/usr/bin/env python3
"""The house's hand over its agents: an agent is an instance anywhere under the house's
workspace that borrows the house's machine, and it IS its path -- relative to the house,
slugs joined by `/` (`ag1`, `rep1/ag1`) -- in every verb, every record, its branch and its git
identity; born and woken from here; the ONE launcher of a harness.

  pp-agent add <path> [--type <package>]
      -> gives birth to the agent at `<path>`: the engine's install, an instance that BORROWS
         the house's machine, no door, the seed of an interactive instance, its slug the path's
         last segment, then its `max_harness_tool_output` set to 200000 through the engine's
         settings face -- the cap of one output of pp: a boot reaches the prompt in one launch --,
         said at the birth; `agent-path-invalid` (a segment that is no slug, `..`, a leading `/`, an
         empty segment, a file on the path, a subtree that carries a machine of its own),
         `agent-exists`, `type-unsupported` -- nothing written.
  pp-agent run <path> (--message <text> | --message-file <path>) [--model <m>]
                      [--max-budget-usd <n>] [--permissions auto|strict|bypass]
                      [--effort low|medium|high|xhigh|max] [--launches <n>]
                      [--new | --run <key>] [--provider <name>] [--harness <command>]
                      [--work <repo> [--base <ref>]] [--door <document>] [--documents <dir>]
                      [--package <name>=on|off]... [--json] [--quiet] [--heartbeat <seconds>] [--dry-run]
      -> ONE exchange, as a message typed in a session, CONDUCTED BY THIS SCRIPT -- the run's
         principal (engine `0.1.0-beta.57`: the run's mode). An opening: once everything is judged,
         this script plays `-new "<message>"` on the agent's instance under the principal's mark
         (`--door <document>` names the run's ENTRY, carried by `PP_DOOR` on that call alone: `-new`
         opens it as a CALL above the boot; with `--run` it refuses `door-on-resume`; `--documents
         <dir>` -- absolute, or relative to the house's directory -- gives the run its ROOT of
         documents, carried by `PP_DOCUMENTS` on that call alone and kept by the engine at the run;
         under `--run` another root refuses `documents-fixed` before any launch; `--package
         <name>=on|off`, repeated, names the packages the run plays -- judged first,
         `package-invalid`, `package-base`, `package-unpinned` --, each switch the run does not play
         already played under the mark before every launch until the engine takes it, the waiting
         list of a conversation), reads the key
         on the output's first line and holds the launcher's lock (`session-<key>.wake.lock`, this
         package's file beside the slot) from there to the records' write. Then the LOOP: the harness
         is launched in the agent's directory, in a session of its provider -- opened at the first
         launch, resumed at the next ones --, on the PROMPT: the first launch carries the message
         under `[message from your principal]`, then pp's whole output; every later launch pp's
         output alone. After each launch this script reads the run: an output HELD by the agent's
         value call, or a chunk waiting, or a block to advance -- its own marked bare call serves or
         advances, and the harness is launched again on what came back; a run PARKED at its FINAL
         with nothing held ends the loop: the harness's last message is the response. A run the
         harness opened meanwhile (a `-new` it typed at the FINAL) is a STRAY run, said on stderr
         and counted at the verdict, never forgotten. `--launches <n>` bounds the launches of one
         wake-up (24 by default, a whole number at least 1: `launches-invalid`): reached, the
         wake-up refuses `launches-spent`, its last response kept, the run left where it stands.
         `--run <key>` resumes the run: parked, the marked `<key> "<message>"` opens the exchange
         (traced `prompt`); standing (a wake-up that died mid-loop), the loop goes on from where
         it stands and the verdict says `standing resumed`; renewed by an upgrade, the marked call
         reopens it under its key. The harness runs with the MARBLE OF THE MODE
         (`.sys/system.common.md`) and the house's wiring, its policy -- judged by the face, the
         model, the run's BUDGET CAP, the permission regime, the model's effort -- spelled by the adapter,
         the prompt on its standard input; its environment never carries the principal's mark.
         `--max-budget-usd <n>` is the budget cap of what the RUN spends over all its exchanges: before every launch
         the run's remainder (the cap less the `cost_usd` of its responses and of the exchange's
         launches) is computed -- none left, nothing is launched (`budget-spent`: refused before an
         exchange, the run as it was; between two launches the loop stops, the last response kept,
         the run standing) --, and handed to the launch's policy where the adapter spells
         `max_budget_usd` (its `SPELLS`); under an adapter whose cost has no scope (`COST` None) a cap
         refuses `budget-unmeasured`. The agent calls pp for its values alone (a proof piped to
         `./pp <key> -`). After the loop: the answer to `responses.jsonl` -- `cost_usd` the SUM of
         the launches' costs, each read in the scope the adapter of the grammar declares (`COST`:
         `session`, the difference between the cumul it reports and the cumul before it; `launch`,
         as reported), `session_cost_usd` the run's cumul in that session, `launches` the
         launches --, the message to `messages.jsonl`,
         the session to `sessions.jsonl`; an answer without a session identity keeps nothing. stdout
         carries what was kept: the response's text (a line opening on `::` prefixed with a
         backslash: the console reads such a line as a directive of the house's bus), or with `--json`
         the response's record line plus `session` and `state`; the verdict line and every refusal go
         to stderr. A failure that kept a response renders it first. While the harness plays, the run's
         trace is followed -- read, never written -- and each step it records is said on stderr as one
         line (`[HH:MM:SS] <key> · opened | <stack> | answer | refused <code> | repair <doc> |
         skill <name> | compacted`, `· parked` on a block that waits), as are this script's own steps
         (`launch <n> · <c> chars · <cost> USD`, `served held output`, `served chunk`, `advanced`,
         `stray run <key>`), one JSON object per line under `--json`; after `--heartbeat` seconds
         without a step (60 by default) a line says `no event for <n>s`, and again at every such
         stretch; `--quiet` says none of it. 0 when the harness exited 0 and the run parked with one
         more response; 2 otherwise. `--dry-run` says the marked `-new` (or `<key> "<message>"`) it
         would play, the composed line, its variables and the head of the first prompt, and launches
         nothing: no run opened. A second wake-up of the same run refuses `run-busy` before anything
         is touched; the lock file carries the wake-up's mark (`{at, message}`: its hour, the head of
         its message) and stays, free, once it is over. The prompt opens on the NEIGHBOURS line when
         other runs of the agent play -- `[runs under way: <key> since HH:MM « <head> » · …]`, a
         blank line, then the message under its head; the record keeps the message as given. While
         the machine is under maintenance nothing is launched: the console that plays `run` holds the
         machine's maintenance lock shared, and refuses `maintenance-in-progress` before the skill
         starts.
         The line of `messages.jsonl` is written AT THE LAUNCH, before the harness, with
         `tag` under `--tag` and `pid` for a detached wake-up: a wake-up under way is on
         record, one that keeps no response leaves its message standing. `--on-end
         <command>` plays that command by the shell once the records are written and the
         wake lock RELEASED (`PP_AGENT_NAME`, `PP_AGENT_RUN`, `PP_AGENT_STATE` in its
         environment; its exit code said, never the wake-up's), never on a wake-up that
         died before any record.
         `--work <repo>` gives the run its MATERIAL: after the key's reservation and before any
         record, under the house's file lock for that repository (`.sys/state/work-<digest>.lock`,
         acquired within `call_lock_wait`, `work-busy` beyond), the skill clones the repository
         by `git clone --no-checkout` under `<path>/work/<key>` (hard links on one file
         system) and cuts the branch `agent/<path>/<key>` from the repository's current branch
         (`--base <ref>` names another); a `.gitignore` (`*`) is laid under `work/` once; a git
         that fails refuses `work-clone-failed` with its stderr's tail -- nothing launched, no
         record line, the wake lock released and its file removed. The record `workdirs.jsonl`
         gains `{at, agent, run, repo, path, branch, base, state: open}`. The harness is launched
         in `<path>/` as ever: the face `conductor.adapters.launch` receives the material
         (`workdir={path, branch, base}`) and composes its head and `PP_WORKDIR`/`PP_CONSOLE`
         the same for every provider; this skill adds the git identity of the exchange to the
         environment (`GIT_AUTHOR_NAME`/`GIT_COMMITTER_NAME` = <path>, `…_EMAIL` =
         <path, `/` read `.`>@<the house's slug>). After the harness, under the same lock, the branch is
         pushed to the repository by its absolute path; `workdirs.jsonl` gains a line with
         `pushed`, `commits` (ahead of the base), `dirty` and `state: pushed|unpushed` (with its
         `reason`); a push that fails keeps the response, says `push failed` and exits 2. A
         resume (`--run`) reopens the run's material as recorded (`workdir-missing` when the
         clone is gone); `--work` on a run that has one refuses `work-standing`. `--dry-run
         --work` shows the head and the variables and clones nothing.
  pp-agent chat <path> [--run <key>] [--model <m>] [--max-budget-usd <n>] [--permissions auto|strict|bypass]
                       [--effort low|medium|high|xhigh|max] [--launches <n>]
                       [--provider <name>] [--harness <command>] [--work <repo> [--base <ref>]]
                       [--door <document>] [--documents <dir>] [--package <name>=on|off]...
                       [--quiet] [--heartbeat <seconds>]
      -> a CONVERSATION at the foreground, conducted by this script: the messages are read on
         stdin, one per line (a line ending on a backslash goes on with the next, the backslash
         taken out and the line break kept; an empty line sends nothing); each message is ONE
         exchange -- the same exchange `run` plays --, of ONE run held from a message to the next
         with its session and its wake lock: the first message opens the run (`--run <key>` resumes
         one instead -- `run-unknown`, `session-missing`, `provider-mismatch`, `run-busy` judged
         before any message is read), every later message resumes it; a `run`, a `start` or a
         team's wake-up on that run refuses `run-busy` while the conversation lives. `--work`,
         `--door` and `--documents` play at the opening alone (`documents-fixed` on a resume that
         names another root); `--package` seeds the conversation's waiting list before any message. After each exchange: the response on stdout as `run`
         prints it, the verdict line on stderr; an exchange that ends badly (`launches-spent`,
         `harness rc <c>`, the frontier missed) says why on stderr and the conversation GOES ON --
         the run stands, the next message takes it up (`standing resumed`). A SIGINT during an
         exchange ends the harness (SIGTERM, SIGKILL after 5 s -- `run` too: no orphan) and the
         exchange is said `interrupted`: the last answer of a finished launch is kept with the error
         `interrupted`, nothing when no launch had finished; the run stands and the conversation
         waits for the next message. The interruption is kept in the MARK of the run's wake lock
         (`interrupted: true`), and the next wake-up of the run -- in this conversation or another
         process -- opens its first prompt on `[interrupted by your principal]` before the message's
         head, says `· after an interruption` at its verdict and clears the mark. A SIGINT while
         waiting for a message, or the end of stdin,
         closes the conversation: the lock released, exit 0; `chat --run <key>` or `run --run <key>`
         takes the run up. `--message`, `--message-file`, `--dry-run`, `--json`, `--tag`, `--on-end`
         and `--new` refuse `flag-unsupported`.
  pp-agent start <path> … [the flags of run] [--tag <id>] [--on-end <command>]
      -> the same exchange DETACHED: the child `run … --detached` (its own session) draws
         the key, holds the wake lock, writes its mark, then reports ONE JSON line
         `{"key", "pid"}` on its stdout -- printed here, exit 0, under a second; after the
         report the child's stdout goes nowhere and its stderr to the wake log
         `session-<key>.wake.log` beside the lock. A refusal before the report is relayed
         on stderr, exit 2. `--json` and `--dry-run` refuse (`flag-unsupported`).
  pp-agent wait <path> <key> [--timeout <seconds>]
      -> waits, looking at the wake lock every 0.2 s and never taking it, until it is free;
         then the run's last response as `run` prints it (0 parked, 2 otherwise);
         `wake-dead` when the last launch added no response (the wake log's tail on
         stderr), `wait-timeout` past the bound.
  pp-agent result <path> <key>        -> the run's last response at once; `wake-running` while
                                         the lock is held and no response came, `wake-dead`,
                                         `result-missing`
  pp-agent workdirs [<path>]
      -> one line per material, the last state of each run's: agent, run, branch, repository,
         commits ahead of the base, clean or dirty, pushed or not, the run's state (running,
         parked, standing, gone); a clone gone is said.
  pp-agent prune <path> <key> [--force]
      -> removes the run's clone: refuses `run-busy` while a wake-up plays the run,
         `workdir-unpushed` when commits of the branch were not sent to the repository
         (`--force` removes them), `workdir-unknown` without a material on record; writes
         `{state: pruned}` to `workdirs.jsonl`.
  pp-agent purge <path> (<key> ... | --before <YYYY-MM-DD>) [--yes] [--force] [--json]
      -> removes for good what the house keeps of runs of the agent -- their lines in the five
         records, their flow, their clone -- and has the engine remove what the agent keeps of them
         (`./pp -purge` on its instance); without `--yes` says it and writes nothing; all or
         nothing: `run-busy` under a held wake lock, `workdir-unpushed` (`--force`), the engine's
         `call-busy` relayed; `run-unknown`, `purge-invalid`; `--json` one object.
  pp-agent flow <path> <key> [--exchange <n>] [--json]
      -> the flow the run's exchanges kept (`flows/<digest>/<key>.jsonl`): every event a flow says,
         one line each -- under `--json` the very objects `chat --json` said; `run-unknown`.
  pp-agent list [--json]              -> the agents of the house -- every instance under its workspace
                                         that borrows its machine, by its path: runs, wake-ups under
                                         way, responses; `--json` one object per agent
  pp-agent status <path> [--json]     -> each run (key, exchanges, running when a wake-up plays,
                                         dead when its last launch added no response, parked or
                                         standing, its session), a launch whose agent opened no
                                         run, the responses, the providers wired; `--json` one object
                                         per run -- the state that prevails, its NAME, the records
                                         summed (cost, launches, first message, hours) -- then one
                                         for the providers
  pp-agent name <path> <key> [<name>] -> the run's name, kept at `names.jsonl` (the last line wins):
                                         what a user types, one line of 1 to 60 printable characters,
                                         its edges trimmed (`name-invalid` otherwise); without a name,
                                         the current one
  pp-agent exchanges <path> <key> [--json]
      -> the run's history: each message paired with the response that answers it, by the hour
         of the two records, `(no response)` or `null` when none came
  pp-agent stats <path> <key> [--json]
      -> the detail of the run's conduction as the engine's `-stats <key>` renders it on the
         agent's instance, relayed; `--json` the records' sums and the run's object under
         `conduction`; `stats-unreadable` when the engine rendered no JSON
  pp-agent responses [<path>] [--last n]  -> the n latest responses (default 1), newest first
  pp-agent messages [<path>] [--last n]   -> the n latest messages sent, newest first

The house is the instance this script belongs to. The engine launches nothing and reads no harness: this script launches, the
adapter reads (`conductor.adapters.answer` once a launch is over, `conductor.adapters.events` line by line
while it plays) -- a `--harness` command in the grammar `--provider` names beside it, never a default
(`grammar-missing`). The records are APPEND-ONLY -- `purge` alone rewrites one, without the lines of the
runs it removes, under the record's lock -- and this script is their only writer: `messages.jsonl` {at, from, to, run, message, policy},
`responses.jsonl` {at, agent, run, index, response, cost_usd, session_cost_usd, launches, denials,
error, harness_rc, flow} -- a wake-up the run's cap stopped between two launches says `error:
"budget-spent"` and `budget {cap, spent}` --, `sessions.jsonl` {at, agent, run, provider, session} -- a run's last line
holds its session --, `names.jsonl` {at, agent, run, name} -- the run's name, the last line
wins. A launch always has its run: this script opens it before the harness plays.

Guards: `agent-unknown`, `agent-path-invalid`, `agent-exists`, `type-unsupported`,
`message-missing` (a wake-up carries a message), `run-unknown`, `run-busy` (a wake-up plays
that run already), `maintenance-in-progress` (the machine is under maintenance: the detached
child of `start` holds the machine shared itself, the console holds it for `run`),
`session-missing` (a run
with no session recorded is never launched; an answer with no identity keeps nothing),
`provider-mismatch` (a session belongs to its provider), `launches-invalid` (a whole number, at
least 1), `launches-spent` (the bound reached, the last response kept, the run left standing),
`budget-spent` (the run's cap reached: before an exchange nothing is launched nor recorded; between
two launches the last response is kept, the run left standing), `budget-unmeasured` (a cap under an
adapter whose `COST` is None: no cost to hold it by),
`heartbeat-invalid` (a whole number of seconds, at least 1),
`flag-unsupported` (`--json`, `--dry-run` under start), `start-timeout`, `start-garbled`,
`wake-dead`, `wake-running`, `wait-timeout`, `result-missing`, `work-clone-failed`, `work-busy`, `work-standing`,
`workdir-missing`, `workdir-unknown`, `workdir-unpushed`, the face's `workdir-invalid` and
`workdir-unsupported`,
`provider-missing`, `provider-ambiguous`, the face's
own (`provider-unknown`, `launch-unsupported`, `policy-unknown`, `policy-invalid`,
`policy-unsupported`, `answer-unsupported`); any other call says the usage in one line,
exit 2.
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

RESPONSES = "responses.jsonl"
MESSAGES = "messages.jsonl"
SESSIONS = "sessions.jsonl"
NAMES = "names.jsonl"            # the name of a run, given by `name`: the last line of a run wins
WORKDIRS = "workdirs.jsonl"
FLOWS = "flows"                 # under the house's records: one file per run, every event its exchanges said
WORK = "work"                   # under an agent's directory: one clone per run, `work/<key>`
USAGE = ("usage: pp-agent add <path> [--type <package>] | run|start <path> (--message <text> | "
         "--message-file <path>) [--model <m>] [--max-budget-usd <n>] [--permissions auto|strict|bypass] "
         "[--effort low|medium|high|xhigh|max] [--launches <n>] [--new | --run <key>] [--provider <name>] [--harness <command>] [--work <repo> [--base <ref>]] "
         "[--door <document>] [--package <name>=on|off]... [--tag <id>] [--on-end <command>] "
         "[--json] [--quiet] [--heartbeat <seconds>] [--dry-run] | chat <path> [--run <key>] [--model <m>] "
         "[--max-budget-usd <n>] [--permissions auto|strict|bypass] [--effort low|medium|high|xhigh|max] "
         "[--launches <n>] [--provider <name>] [--harness <command>] [--work <repo> [--base <ref>]] "
         "[--door <document>] [--documents <dir>] [--package <name>=on|off]... [--json] [--quiet] "
         "[--heartbeat <seconds>] | wait <path> <key> [--timeout <seconds>] | "
         "result <path> <key> | workdirs [<path>] | prune <path> <key> [--force] | "
         "purge <path> (<key> ... | --before <YYYY-MM-DD>) [--yes] [--force] [--json] | "
         "flow <path> <key> [--exchange <n>] [--json] | "
         "list [--json] | status <path> [--json] | name <path> <key> [<name>] | exchanges <path> <key> [--json] | "
         "stats <path> <key> [--json] | providers [--json] | responses [<path>] [--last n] | messages [<path>] [--last n]")
RUN_FLAGS = {"message": True, "message-file": True, "model": True, "max-budget-usd": True, "permissions": True, "effort": True,
             "launches": True, "door": True, "documents": True,
             "run": True, "provider": True, "harness": True, "work": True, "base": True, "tag": True,
             "on-end": True, "new": False, "json": False, "quiet": False, "heartbeat": True, "dry-run": False,
             "detached": False, "package": True}
REPEATED = ("package",)         # the flags given several times, kept as a list
HEARTBEAT = 60                  # seconds without a step before a line says so
WAIT_INTERVAL = 0.2             # seconds between two looks at the wake lock while `wait` waits
REPORT_WAIT = 20                # seconds `start` gives its child to report {key, pid}
LAUNCHES = 24                   # launches of the harness one wake-up may play, unless `--launches` says
TERMINATE_WAIT = 5              # seconds an interrupted harness gets to end on SIGTERM before SIGKILL
PRINCIPAL = "PP_CONDUCTED_BY_PRINCIPAL"   # the principal's mark: on this script's own calls to pp, never the CLI's
HEAD = "[message from your principal]"    # opens the first prompt of a wake-up, the message under it
INTERRUPTED = "[interrupted by your principal]"   # before HEAD, in the wake-up after an interrupted one
HOUSE = "."                     # the house itself, addressed as an agent: its own instance, its own runs
FAMILY = "agent-run"            # the vector family of the runs: `agent-run:<path>/<key>`, verified here
CALLS = ("tool", "tool-result", "thinking", "words")   # what a launch does, read on the harness's output as it comes
VOICES = ("opened", "principal", "conduction", "agent") + CALLS   # what a conversation's flow says beside the run's
# steps: the house opening a run, the principal's message, pp's output served to the harness, the harness's answer,
# and what the harness does during a launch -- a call of a tool, its result, a thought, words
FLOW = VOICES + ("ready", "response", "verdict", "waiting", "refused", "closed", "policy", "conduct", "package")   # every kind of the flow but `step`
SETTABLE = {"model": "model", "max_budget_usd": "max-budget-usd", "permissions": "permissions",
            "effort": "effort"}   # what `set` may change: policy key -> flag
FLOW_VOICES = ("principal", "conduction", "pp_input", "pp_result", "tool_input", "tool_result", "words",
               "thinking")       # the voices a `flow` sums, in tokens; `calls` beside them
PP_VOICES = ("conduction", "pp_input", "pp_result")   # what of the flow is pp's: its outputs, the calls of it
HARNESS_CAP = 200000            # `max_harness_tool_output` an agent is born with: one output of pp, one launch
KEY_LINE = re.compile(r"^▌ pp · run ([0-9a-f]{6})")   # the first line of every output of the engine
NAME_CHARS = 60                                        # a run's name: a title a user types, never a key


def refuse(said: str) -> None:
    sys.stderr.write(f"pp-agent: {said}\n")
    raise SystemExit(2)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- the house and its agents -----------------------------------------------------------

def house():
    """-> (the house's instance root, the conductor module) -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core, home                          # noqa: E402 -- the bootstrap
    root = home(__file__)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(__file__)


def agent_at(root: Path, conductor, path: str) -> Path:
    """-> where the agent `path` stands: `<house>/<path>/<instance dir>`, the instance
    directory named as the house's own. An agent IS its path, relative to the house's
    workspace, written with `/`, every segment a slug -- anything else refuses
    `agent-path-invalid`. `.` is the HOUSE itself: its own instance."""
    if path == HOUSE:
        return root
    segments = path.split("/")
    if not path or not all(conductor.instance.valid_slug(one) for one in segments):
        refuse(f"agent-path-invalid -- `{path}`: an agent is its path under the house, slugs joined by `/` "
               "(lowercase, digits and single dashes; no `..`, no leading `/`, no empty segment).")
    return root.parent.joinpath(*segments) / root.name


def named_agent(root: Path, conductor, rest: list[str]) -> tuple[str, Path, list[str]]:
    """-> (the agent's path, its instance root, the rest): the first word is the agent's
    path, where an instance must stand (`agent-unknown`)."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    path, meta = rest[0], agent_at(root, conductor, rest[0])
    if not conductor.instance.is_instance(meta):
        refuse(f"agent-unknown -- no agent at `{path}` under {root.parent} (`./pp agent add {path}` creates it).")
    return path, meta, rest[1:]


def house_judged(conductor, meta: Path, name: str, key: str | None, asked: dict) -> None:
    """The house's own refusals, before any provider is judged or any message read: its material would
    be a clone in its own tree (`work-on-house`), and a run the LLM conducts -- a conversation of its
    host -- has no session the house can take up (`run-unconducted`). Any other agent passes."""
    if name != HOUSE:
        return
    if asked.get("work") is not None:
        refuse("work-on-house -- the house works in its own tree: `--work` gives an AGENT its clone.")
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key) if key else None
    if slot is not None and slot.is_file() and persistence.mode_of(slot) != persistence.PRINCIPAL:
        refuse(f"run-unconducted -- run {key} is conducted by the LLM of its host, not by the house: "
               "`chat .` opens a run of its own.")


def faced_slots(conductor, meta: Path, name: str) -> list[Path]:
    """-> the runs the faces show of an agent: all its slots; of the house, the runs its principal
    conducts alone -- the conversations of its host stay out."""
    persistence = conductor.persistence
    slots = persistence.slots(meta)
    if name != HOUSE:
        return slots
    return [one for one in slots if persistence.mode_of(one) == persistence.PRINCIPAL]


def agents_of(root: Path, conductor) -> list[tuple[str, Path]]:
    """-> (path, instance root) of every agent of the house: each instance under the house's
    workspace that borrows the machine (`instance.borrowers`), at any depth, by its path."""
    return [(one.parent.relative_to(root.parent).as_posix(), one)
            for one in conductor.instance.borrowers(root)]


# --- the records of the house ------------------------------------------------------------

def record(root: Path, name: str) -> Path:
    return root / ".sys" / "records" / name


def lines_of(path: Path) -> list[dict]:
    """-> the record's lines, oldest first. A LAST line that does not parse is a writer still
    writing it and is skipped; one anywhere else is a hand in the file and refuses."""
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8").splitlines()
    found = []
    for number, line in enumerate(raw, 1):
        if not line.strip():
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            if number == len(raw):
                continue
            refuse(f"line {number} of {path.name} is not a record -- this script is the "
                   "only writer, the file is not for hand edits.")
    return found


def append(path: Path, entry: dict) -> None:
    """Appends ONE line under the record's lock: two wake-ups never mix their lines."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    path.parent.mkdir(parents=True, exist_ok=True)
    with core(__file__).record.held(path):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def session_of_run(root: Path, name: str, key: str) -> dict | None:
    """-> the run's last line at `sessions.jsonl` -- its provider and its session -- or None."""
    found = [one for one in lines_of(record(root, SESSIONS)) if one.get("agent") == name and one.get("run") == key]
    return found[-1] if found else None


def name_of(root: Path, name: str, key: str) -> str:
    """-> the run's name, the last line of `names.jsonl` for it -- '' when none was given."""
    found = [one for one in lines_of(record(root, NAMES)) if one.get("agent") == name and one.get("run") == key]
    return str(found[-1].get("name") or "") if found else ""


def cumuls_of(root: Path, name: str, key: str) -> dict:
    """-> what the records say of a run, summed: the responses, the cost (the sum of the
    numeric `cost_usd`, None when none), the launches, the first message and its hour, the
    hour of the last line of either record."""
    answered = answered_by(root, name, key)
    sent = [one for one in lines_of(record(root, MESSAGES)) if one.get("to") == name and one.get("run") == key]
    costs = [one["cost_usd"] for one in answered if isinstance(one.get("cost_usd"), (int, float))]
    launches = [one["launches"] for one in answered if isinstance(one.get("launches"), int)]
    ats = [str(one["at"]) for one in answered + sent if one.get("at")]
    return {"responses": len(answered),
            "cost_usd": round(sum(costs), 6) if costs else None,
            "launches": sum(launches),
            "first_message": str(sent[0].get("message", "")) if sent else None,
            "first_at": str(sent[0].get("at")) if sent and sent[0].get("at") else None,
            "last_at": max(ats) if ats else None}


def spent_of(root: Path, name: str, key: str | None) -> float:
    """-> what the run spent so far: the sum of the `cost_usd` of its responses, 0 for a run not yet opened
    or whose costs are unknown."""
    return float(cumuls_of(root, name, key)["cost_usd"] or 0.0) if key is not None else 0.0


def budget_of(policy: dict, spent: float) -> dict | None:
    """-> the run's budget as the faces say it, `{cap, spent, left}`, from the policy's cap and what the run
    spent; None without a cap. `left` goes below 0 when the last launch went past the cap."""
    cap = policy.get("max_budget_usd")
    if not isinstance(cap, (int, float)):
        return None
    return {"cap": float(cap), "spent": round(spent, 6), "left": round(float(cap) - spent, 6)}


def cost_scope(conductor, root: Path, grammar: str) -> str | None:
    """-> the scope of the cost the adapter of `grammar` reads, as its `wire.py` declares it (`COST`):
    `session` (the session's cumul at that launch), `launch` (that launch alone), or None (no cost read,
    or no declaration)."""
    scope = getattr(conductor.adapters.load(grammar, root), "COST", None)
    return scope if scope in ("session", "launch") else None


def costed(scope: str | None, read, cumul: float | None) -> tuple[float | None, float | None]:
    """-> (the launch's cost, the session's cumul after it) from the cost the adapter read, in its scope;
    (None, the cumul as it was) when it read none or declares no scope."""
    if scope is None or not isinstance(read, (int, float)):
        return None, cumul
    if scope == "session":
        return round(float(read) - float(cumul or 0.0), 6), float(read)
    return round(float(read), 6), round(float(cumul or 0.0) + float(read), 6)


def unmeasured(conductor, root: Path, asked: dict, policy: dict) -> str | None:
    """-> the refusal of a cap the run cannot hold: `budget-unmeasured` when the policy carries a cap and
    the adapter of the run's grammar declares no scope of cost; None otherwise."""
    if "max_budget_usd" not in policy:
        return None
    grammar = grammar_of(asked, provider_of(conductor, root, asked)[1])
    try:
        if cost_scope(conductor, root, grammar) is not None:
            return None
    except conductor.Refusal as refusal:
        return str(refusal)
    return (f"budget-unmeasured -- the adapter of `{grammar}` declares no scope for the cost it reads (`COST` None): "
            "no cap can be held on its runs -- drop `--max-budget-usd`.")


def limiter(conductor, root: Path, provider: str | None, policy: dict, spent: float):
    """-> `limit(spent_now)`: the policy of the NEXT launch, given what the exchange spent so far
    (`spent_now`, None for nothing) on top of what the run spent before it (`spent`) -- the run's
    remainder as `max_budget_usd` where the adapter of `provider` spells the key (its `SPELLS`), the
    key dropped where it does not; None when the cap leaves nothing. Without a cap, the policy as is."""
    cap = policy.get("max_budget_usd")
    if not isinstance(cap, (int, float)):
        return lambda spent_now: policy
    spells = ()
    if provider is not None:
        try:
            spells = tuple(getattr(conductor.adapters.load(provider, root), "SPELLS", ()))
        except conductor.Refusal as refusal:
            refuse(str(refusal))

    def limit(spent_now: float | None) -> dict | None:
        left = round(float(cap) - spent - float(spent_now or 0.0), 6)
        if left <= 0:
            return None
        launched = {key: value for key, value in policy.items() if key != "max_budget_usd"}
        if "max_budget_usd" in spells:
            launched["max_budget_usd"] = left
        return launched
    return limit


def counted_since(conductor, meta: Path, key: str, answered: list[dict]) -> tuple[list[dict], int | None]:
    """-> (the responses of the run whose flow fills its context now, the index of the first of them
    when a compaction was declared, else None): after `-compacted` the slot's `boot` mark holds the
    count of exchanges the engine had, so the flow counts from the response after the conducted one of
    that rank -- a bare exchange the engine never saw counts on the side of the compaction it follows."""
    boot = conductor.persistence.boot_of(conductor.persistence.slot_of(meta, key))
    if boot <= 0:
        return answered, None
    seen = 0
    for at, one in enumerate(answered):
        if one.get("conducted", True) is not False:
            seen += 1
            if seen == boot:
                return answered[at + 1:], int(one.get("index") or at + 1) + 1
    return answered, None


def window_of(conductor, root: Path, name: str, key: str, cache: dict | None = None) -> int | None:
    """-> the context window of the run's MODEL -- the model of its last message -- as the adapter of
    its session's provider declares it (`CONTEXT_WINDOWS` of its `wire.py`, the models verified alone);
    None for a caller's command, an undeclared model, or no model named."""
    provider = (session_of_run(root, name, key) or {}).get("provider")
    sent = [one for one in lines_of(record(root, MESSAGES)) if one.get("to") == name and one.get("run") == key]
    model = (sent[-1].get("policy") or {}).get("model") if sent else None
    if not provider or not model:
        return None
    cache = {} if cache is None else cache
    if provider not in cache:
        try:
            cache[provider] = dict(getattr(conductor.adapters.load(provider, root), "CONTEXT_WINDOWS", {}) or {})
        except conductor.Refusal:
            cache[provider] = {}
    window = cache[provider].get(model)
    return int(window) if isinstance(window, int) and window > 0 else None


def context_of(rows: list[dict], window: int | None, served=None, since: int | None = None) -> dict | None:
    """-> what the flow of the run's responses `rows` says of its context, APPROACHED (the harness's
    own base left out): the voices summed in tokens and their `total`, the `window` and the part of it
    `used`, pp's part (`tokens`, `share` of the flow, `served` the engine's `-stats` beside), the
    `calls`, the `reread` (per exchange, its calls times the context at its start plus half its flow)
    and `since`; None when no row carries a flow."""
    flows = [one["flow"] for one in rows if isinstance(one.get("flow"), dict)]
    if not flows:
        return None
    voices = {voice: sum(int(one.get(voice) or 0) for one in flows) for voice in FLOW_VOICES}
    total = sum(voices.values())
    pp = sum(voices[voice] for voice in PP_VOICES)
    reread, at_start = 0, 0
    for one in flows:
        size = sum(int(one.get(voice) or 0) for voice in FLOW_VOICES)
        reread += int(one.get("calls") or 0) * (at_start + size // 2)
        at_start += size
    return {"flow": {**voices, "total": total}, "window": window,
            "used": round(total / window, 4) if window else None,
            "pp": {"tokens": pp, "share": round(pp / total, 4) if total else None,
                   "served": served if isinstance(served, int) else None},
            "calls": sum(int(one.get("calls") or 0) for one in flows), "reread": reread, "since": since}


def context_seen(full: dict | None) -> dict | None:
    """-> the run's context as `status --json` says it, reduced to what a table shows: `tokens` (the
    flow's total), `used`, `pp` (pp's share of the flow); None without a flow."""
    if full is None:
        return None
    return {"tokens": full["flow"]["total"], "used": full["used"], "pp": full["pp"]["share"]}


def run_known(conductor, meta: Path, key: str) -> bool:
    """Whether a run of the agent wears that key."""
    persistence = conductor.persistence
    return key in {persistence.run_id_of(one) for one in persistence.slots(meta)}


def json_flag(rest: list[str]) -> tuple[bool, list[str]]:
    """-> (whether `--json` was asked, the rest without it)."""
    return "--json" in rest, [one for one in rest if one != "--json"]


# --- the run, read at the agent ---------------------------------------------------------

def trace_events(conductor, meta: Path, key: str) -> list[dict]:
    """-> the events the run's trace holds, in order -- [] when no trace stands."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    log = persistence.trace_of(slot)
    if not log or not (slot.parent / log).is_file():
        return []
    found = []
    for line in (slot.parent / log).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            continue
    return found


def standing_of(conductor, meta: Path, key: str) -> tuple[str, str]:
    """-> (`parked` | `standing`, the stack of the last block): parked when the last block
    rendered waits for the principal's message (a FINAL), standing on its block otherwise."""
    blocks = [one for one in trace_events(conductor, meta, key) if one.get("kind") == "block"]
    if not blocks:
        return "standing", ""
    last = blocks[-1]
    return ("parked" if last.get("wait") else "standing"), str(last.get("stack", ""))


# --- run -----------------------------------------------------------------------------------

def flags(rest: list[str]) -> dict:
    """-> the run's flags, from `RUN_FLAGS`; anything else is the usage."""
    found: dict = {name: (None if takes else False) for name, takes in RUN_FLAGS.items()}
    for name in REPEATED:
        found[name] = []
    index = 0
    while index < len(rest):
        word = rest[index]
        name = word[2:] if word.startswith("--") else ""
        if name not in RUN_FLAGS:
            refuse(USAGE)
        if RUN_FLAGS[name]:
            if index + 1 >= len(rest):
                refuse(USAGE)
            if name in REPEATED:
                found[name].append(rest[index + 1])
            else:
                found[name] = rest[index + 1]
            index += 2
        else:
            found[name] = True
            index += 1
    if found["message"] is not None and found["message-file"] is not None:
        refuse("one message: --message or --message-file, not both.")
    if found["new"] and found["run"] is not None:
        refuse("one run: --new opens, --run <key> resumes, not both.")
    if found["base"] is not None and found["work"] is None:
        refuse("`--base <ref>` names what `--work <repo>` cuts the branch from: give --work too.")
    return found


def message_of(asked: dict) -> str | None:
    """-> the message to send: the text given, the file's content (`-` reads stdin), or
    None when none was given."""
    if asked["message"] is not None:
        return str(asked["message"])
    if asked["message-file"] is None:
        return None
    if asked["message-file"] == "-":
        return sys.stdin.read().rstrip("\n")
    path = Path(asked["message-file"])
    if not path.is_file():
        refuse(f"message-file-missing -- {path} is no file.")
    return path.read_text(encoding="utf-8").rstrip("\n")


def asked_policy(asked: dict) -> dict:
    """-> the policy the flags give, as typed: the model, the budget, the regime, the effort."""
    policy: dict = {}
    if asked["model"] is not None:
        policy["model"] = asked["model"]
    if asked["max-budget-usd"] is not None:
        policy["max_budget_usd"] = asked["max-budget-usd"]
    if asked["permissions"] is not None:
        policy["permissions"] = asked["permissions"]
    if asked["effort"] is not None:
        policy["effort"] = asked["effort"]
    return policy


def policy_of(conductor, asked: dict) -> dict:
    """-> the policy as the face judged it (`conductor.adapters.judged`): the flags given,
    typed and checked -- the policy that composes the line is the one the record keeps."""
    try:
        return conductor.adapters.judged(asked_policy(asked))
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    return {}


def set_policy(conductor, root: Path, asked: dict, fields: dict) -> str | None:
    """A `set` of a conversation's flow: the model, the budget, the permission regime or the effort
    of the NEXT launches, judged by the face with the rest of the policy before `asked` takes them.
    -> None when it holds, else the code of its refusal, `asked` untouched: `provider-fixed` (a
    session belongs to its provider), `policy-unknown` or `policy-invalid` (the face's own),
    `budget-unmeasured` for a cap under an adapter whose cost has no scope (its `COST`), and
    `policy-unsupported` for a regime the run's provider does not spell (its adapter's `SPELLS`;
    a caller's command spells what it is given)."""
    if "provider" in fields:
        return "provider-fixed"
    try:
        conductor.adapters.judged({**asked_policy(asked), **fields})
    except conductor.Refusal as refusal:
        return refusal.code
    if "max_budget_usd" in fields:
        refused = unmeasured(conductor, root, asked, {"max_budget_usd": fields["max_budget_usd"]})
        if refused is not None:
            return refused.split(" ", 1)[0]
    if "permissions" in fields:
        provider = provider_of(conductor, root, asked)[1]
        if provider is not None:
            try:
                spelled = getattr(conductor.adapters.load(provider, root), "SPELLS", ())
            except conductor.Refusal as refusal:
                return refusal.code
            if "permissions" not in spelled:
                return "policy-unsupported"
    for key, value in fields.items():
        asked[SETTABLE[key]] = value
    return None


def provider_of(conductor, root: Path, asked: dict) -> tuple[list[str], str | None]:
    """-> (the harness command's head, or the provider's name): the caller's command,
    else the caller's provider, else the ONE the house is wired with. A caller's command
    owes the grammar its output is read in, `--provider` beside it (`grammar-missing`)."""
    if asked["harness"] is not None:
        if asked["provider"] is None:
            refuse("grammar-missing -- `--harness` runs a caller's command: name the grammar its output is "
                   "read in with `--provider <name>` beside it -- the provider whose adapter reads it.")
        return shlex.split(asked["harness"]), None
    if asked["provider"] is not None:
        return [], str(asked["provider"])
    wired = conductor.install.wired_providers(root.parent)
    if not wired:
        refuse("provider-missing -- no --harness, no --provider, and the house is wired with no adapter.")
    if len(wired) > 1:
        refuse(f"provider-ambiguous -- the house is wired with {', '.join(wired)}: name one with --provider.")
    return [], wired[0]


def grammar_of(asked: dict, provider: str | None) -> str:
    """-> the provider whose adapter READS what the harness prints: the provider launched, or under a
    caller's command the one `--provider` names beside it (`provider_of` refuses a command without it)."""
    return provider or str(asked["provider"])


def provider_named(conductor, root: Path, asked: dict) -> str:
    """-> the name of the harness a launch plays: the provider, or `harness` for a caller's command."""
    return provider_of(conductor, root, asked)[1] or "harness"


def compose(conductor, root: Path, meta: Path, head: list[str], provider: str | None,
            prompt: str, policy: dict, session: str | None,
            workdir: dict | None = None) -> tuple[list[str], dict, str]:
    """-> (argv, env, stdin): the caller's command with the session in `PP_AGENT_SESSION`,
    or the line the provider's adapter composes -- the agent's marble, the house's wiring,
    the policy, the session opened (None) or resumed, the material --; `stdin` the prompt
    the process reads on its standard input, the material's head before it. A caller's
    command gets the material as the face composes it for a provider: the same head, the
    same `PP_WORKDIR` and `PP_CONSOLE` (`conductor.adapters.material`, `headed`,
    `console_of`)."""
    adapters = conductor.adapters
    try:
        if head:
            held = adapters.material(workdir)
            console = adapters.console_of(meta.parent)
            env = {"PP_AGENT_SESSION": session} if session else {}
            if held:
                env.update({"PP_WORKDIR": held["path"], "PP_CONSOLE": str(console)})
            return list(head), env, adapters.headed(prompt, held, console)
        return adapters.launch(provider, meta.parent, meta, prompt, marble=meta / ".sys" / "system.common.md",
                               wiring=root.parent, policy=policy or None, session=session, workdir=workdir)
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    return [], {}, ""


def read_answer(conductor, meta: Path, grammar: str, played: subprocess.CompletedProcess) -> dict:
    """-> what the harness answered, its session identity owed: read by the adapter of `grammar`
    (`conductor.adapters.answer`), a caller's command as a provider's. No identity refuses
    `session-missing`: nothing is kept."""
    try:
        return conductor.adapters.answer(grammar, meta, played.stdout, played.stderr)
    except conductor.Refusal as refusal:
        refuse(f"{refusal} -- nothing recorded")
    return {}


def resumable(conductor, root: Path, meta: Path, name: str, key: str, provider: str | None) -> str:
    """-> the session a resume reopens: the run stands, its session is recorded
    (`session-missing` otherwise -- nothing is launched), under the provider it was opened
    with (`provider-mismatch`; None is a caller's command)."""
    if not conductor.persistence.slot_of(meta, key).is_file():
        refuse(f"run-unknown -- no run `{key}` at {meta}.")
    known = session_of_run(root, name, key)
    if known is None:
        refuse(f"session-missing -- run {key} has no session recorded at {SESSIONS}: it is never "
               "launched without one; `--new` opens another run.")
    if known.get("provider") != provider:
        refuse(f"provider-mismatch -- run {key} lives in a session of "
               f"{known.get('provider') or 'a caller command'}, not of {provider or 'a caller command'}.")
    return str(known["session"])


RESUMED = {"model": "model", "max_budget_usd": "max-budget-usd", "permissions": "permissions",
           "effort": "effort"}   # what a resume takes from the run's last policy: policy key -> flag


def resumed_of(conductor, root: Path, name: str, key: str | None, asked: dict) -> dict:
    """-> the call's flags, completed on a resume by what the RUN was: the provider of its session
    when neither `--provider` nor `--harness` is given, and each key of its last policy (the
    `policy` of its last line at `messages.jsonl`) the call does not give. A flag of the call
    always prevails. A run opened under a caller's command cannot be relaunched without it
    (`harness-required`); a provider the house is no longer wired with refuses
    (`provider-unwired`). No session recorded: the flags as given (`resumable` says
    `session-missing`)."""
    known = session_of_run(root, name, key) if key else None
    if known is None:
        return asked
    filled = dict(asked)
    if asked["harness"] is None and asked["provider"] is None:
        recorded = known.get("provider")
        if not recorded:
            refuse(f"harness-required -- run {key} lives in the session of a caller's command: "
                   "resume it with that command, `--harness <command>`.")
        wired = conductor.install.wired_providers(root.parent)
        if recorded not in wired:
            refuse(f"provider-unwired -- run {key} lives in a session of {recorded}, and the house is wired "
                   f"with {', '.join(wired) or 'no adapter'}.")
        filled["provider"] = recorded
    sent = [one for one in lines_of(record(root, MESSAGES)) if one.get("to") == name and one.get("run") == key]
    policy = dict(sent[-1].get("policy") or {}) if sent else {}
    for field, flag in RESUMED.items():
        if asked[flag] is None and policy.get(field) is not None:
            filled[flag] = policy[field]
    return filled


def harmless(text: str) -> str:
    """-> a text an agent or a message carried, as stdout may print it: each line opening on
    `::`, blanks before it included, prefixed with a backslash -- the console reads such a line
    as a directive of the house's bus, and an agent's words never give pp an order."""
    return "\n".join("\\" + one if one.lstrip().startswith("::") else one for one in text.split("\n"))


def rendered(kept: dict, session: str, state: str, as_json: bool) -> None:
    """Prints on stdout what the call kept: the response's record line with its session and
    state (`--json`), or the response's text, `harmless`. Nothing when the harness gave no text."""
    if as_json:
        print(json.dumps({**kept, "session": session, "state": state}, ensure_ascii=False))
    elif kept["response"] is not None:
        print(harmless(kept["response"]))


def launches_of(asked: dict) -> int:
    """-> the launches one wake-up may play: `--launches`, a whole number at least 1
    (`launches-invalid` otherwise), 24 without it."""
    if asked["launches"] is None:
        return LAUNCHES
    try:
        count = int(asked["launches"])
    except ValueError:
        count = 0
    if count < 1:
        refuse(f"launches-invalid -- `--launches {asked['launches']}`: a whole number of launches, at least 1.")
    return count


def heartbeat_of(asked: dict) -> int:
    """-> the seconds without a step before a line says so: `--heartbeat`, a whole number
    at least 1 (`heartbeat-invalid` otherwise), 60 without it."""
    if asked["heartbeat"] is None:
        return HEARTBEAT
    try:
        seconds = int(asked["heartbeat"])
    except ValueError:
        seconds = 0
    if seconds < 1:
        refuse(f"heartbeat-invalid -- `--heartbeat {asked['heartbeat']}`: a whole number of seconds, at least 1.")
    return seconds


def tracing(conductor):
    """-> the engine's `state.log` module: the one reader of a run's trace (`follow`,
    `step_of`, `said`), shared with whoever else follows a run."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.log")


def step_sayer(log, as_json: bool):
    """-> the `say` of a wake-up watched from stderr: every step of the run or of the house
    said by the engine's `log.said` -- one line each, text or JSON --, the VOICES of a
    conversation (what a flow alone renders) left unsaid."""
    def say(key: str, line: str, kind: str, fields: dict) -> None:
        if kind not in VOICES:
            log.said(key, line, kind, fields, as_json)
    return say


def event_of(key: str | None, kind: str, fields: dict) -> dict:
    """-> one event of a flow: `kind`, `at` and `run` first -- a voice or a house's word under its own kind,
    a step of the run or of the house under `step` with its `event`."""
    if kind in FLOW:
        return {"kind": kind, "at": now(), "run": key or None, **fields}
    return {"kind": "step", "at": now(), "run": key or None, "event": kind, **fields}


def event_sayer(stream):
    """-> the `say` of a conversation's FLOW: one JSON object per line on `stream` (`event_of`) -- a voice
    under its own kind (`opened`, `principal`, `conduction`, `agent`), a step of the run or of the house
    under `step` with its `event` and its fields, the grammar `run --json` says on stderr. Its `told`
    prints an event already built: the very object a keeper kept."""
    def told(event: dict) -> None:
        print(json.dumps(event, ensure_ascii=False), file=stream, flush=True)

    def say(key: str, line: str, kind: str, fields: dict) -> None:
        told(event_of(key, kind, fields))
    say.told = told
    return say


def flow_of(root: Path, name: str, key: str) -> Path:
    """-> the flow file of the run `key` of the agent `name`: `flows/<digest of its path>/<key>.jsonl`."""
    import hashlib
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]
    return record(root, FLOWS) / digest / f"{key}.jsonl"


def keeper(root: Path, name: str, say):
    """-> `say` wrapped by the KEEPER of the run's flow: every event it receives -- voices and steps, before
    the caller chooses what to say of it -- appended to the run's flow file (`flow_of`), one JSON line each,
    then handed on: the very object to a flow's `told`, the words as they came to any other `say`. Its
    `recorded` keeps an event without saying it -- the end of an exchange `run` never says on stderr. One
    writer per run at a time: the one that holds its wake lock."""
    def kept(key: str | None, kind: str, fields: dict) -> dict:
        event = event_of(key, kind, fields)
        if key:
            path = flow_of(root, name, key)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def wrapped(key: str, line: str, kind: str, fields: dict) -> None:
        event = kept(key, kind, fields)
        told = getattr(say, "told", None)
        if told is not None:
            told(event)
        else:
            say(key, line, kind, fields)
    wrapped.told = getattr(say, "told", None)
    wrapped.recorded = lambda key, kind, fields: kept(key, kind, fields) and None
    return wrapped


def flow_closed(issue: dict, reason: str | None) -> None:
    """Keeps the end of an exchange in its run's flow -- `response` when one was kept, then `verdict` --
    without saying it: for `run`, `start` and the text of `chat`, whose stderr says the verdict its own way."""
    keep = issue.get("say")
    if keep is None or not issue.get("key"):
        return
    if issue["kept"] is not None:
        keep.recorded(issue["key"], "response", {**issue["kept"], "session": issue["done"]["session"],
                                                 "state": issue["said"]})
    keep.recorded(issue["key"], "verdict", verdict_of(issue, reason))


def followed(trace, log, key: str, say, kept: list | None) -> int:
    """Reads what the run's trace gained: each event kept RAW in `kept` (when given), each step
    `say`d. -> the count of steps said."""
    fresh = trace.fresh()
    if kept is not None:
        kept.extend(fresh)
    steps = [one for one in map(log.step_of, fresh) if one is not None]
    for line, kind, fields in steps:
        say(key, line, kind, fields)
    return len(steps)


def waited(argv: list[str], cwd: Path, environment: dict, trace, key: str,
           beat: int, say, log, stdin: str = "", kept: list | None = None, heard=None) -> subprocess.CompletedProcess:
    """-> the harness's play, once it ends: the prompt written on its standard input and
    the input closed, its streams kept in files (never a pipe it could fill), and, while
    it plays, every 0.2 s: each COMPLETE line its standard output gained handed to `heard`
    (a line still being written waits for its end), and the run's trace followed by the engine's
    reader -- one step `say`d at a time, one more after every `beat` seconds without one, the events
    read kept raw in `kept`. Without a trace to follow (`--quiet`) the steps are not followed; with
    neither, it waits. The whole output is rendered at the end. The prompt rides stdin and never the
    line: an argument is bounded, a prompt is bounded by the model alone."""
    with tempfile.TemporaryDirectory() as scratch, tempfile.TemporaryFile() as err, \
            tempfile.TemporaryFile() as fed:
        fed.write(stdin.encode("utf-8"))               # a file, never a pipe: the harness reads at its pace
        fed.seek(0)
        written = Path(scratch) / "stdout"
        with open(written, "wb") as out, open(written, "rb") as reading:   # two handles: two offsets
            process = subprocess.Popen(argv, cwd=str(cwd), env=environment, stdin=fed, stdout=out, stderr=err)
            rest = b""

            def lines(last: bool = False) -> None:
                nonlocal rest
                rest += reading.read()
                *whole, rest = rest.split(b"\n")
                if last and rest:
                    whole, rest = whole + [rest], b""
                for one in whole:
                    heard(one.decode("utf-8", "replace"))

            try:
                if trace is None and heard is None:
                    process.wait()
                else:
                    still, beats = time.monotonic(), 0
                    while True:
                        ended = process.poll() is not None
                        if heard is not None:
                            lines()
                        if trace is not None:
                            steps = followed(trace, log, key, say, kept)
                            if steps:
                                still, beats = time.monotonic(), 0
                            elif time.monotonic() - still >= beat * (beats + 1):
                                beats += 1
                                say(key, f"no event for {beat * beats}s", "quiet", {"seconds": beat * beats})
                        if ended:
                            break
                        time.sleep(0.2)
                    if heard is not None:
                        lines(last=True)
            except KeyboardInterrupt:              # the launcher is interrupted: the harness goes with it, no orphan
                process.terminate()
                try:
                    process.wait(TERMINATE_WAIT)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise
            reading.seek(0)
            printed = reading.read()
        err.seek(0)
        return subprocess.CompletedProcess(argv, process.returncode, printed.decode("utf-8", "replace"),
                                           err.read().decode("utf-8", "replace"))


def hearer(conductor, meta: Path, grammar: str, key: str, say, exchange_no: int, launch: int, flow=None):
    """-> the `heard` of ONE launch: each line of the harness's output read by the adapter of `grammar`
    (`conductor.adapters.events`), each event in the common schema said under its own kind with
    `exchange` and `launch` -- a `tool` also says `pp`, whether its `shell` calls the agent's console
    (`./pp`, or the console by its absolute path) -- and counted by `flow` when one is given. A line the
    face refuses (`events-malformed`) is said as a `refusal` step and the reading goes on: a call badly
    told does not end a launch."""
    console = str(conductor.adapters.console_of(meta.parent))

    def heard(line: str) -> None:
        try:
            found = conductor.adapters.events(grammar, meta, line)
        except conductor.Refusal as refusal:
            say(key, f"refused {refusal.code}", "refusal", {"code": refusal.code, "detail": str(refusal)})
            return
        for one in found:
            kind = one.pop("kind")
            if kind == "tool":
                one["pp"] = pp_called(one.get("shell"), console)
            if flow is not None:
                flow.heard(kind, one)
            say(key, "", kind, {"exchange": exchange_no, "launch": launch, **one})
    return heard


class Flow:
    """What the flow of ONE exchange carries, summed by voice in tokens -- the engine's estimate
    (`conductor.metrics.tokens`, the rule of `-stats`): `principal` what a prompt carries beside pp's
    output (the head, the message), `conduction` pp's output served, `pp_input` and `pp_result` the
    calls of the agent's console and their results (paired by `id`), `tool_input` and `tool_result`
    the other tools', `words` the model's words (the launch's answer when the adapter says none),
    `thinking` its thought (its text estimated, or the tokens the host counts); `calls` the calls to
    the model -- one per launch, one more per call of a tool. `sums` is what the record keeps."""

    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.sums = {voice: 0 for voice in FLOW_VOICES}
        self.sums["calls"] = 0
        self.piped: set[str] = set()
        self.worded = False

    def launch(self, prompt: str, output: str) -> None:
        """A launch on `prompt`, whose tail is pp's `output` (empty for a bare exchange)."""
        self.sums["calls"] += 1
        self.sums["conduction"] += self.tokens(output) if output else 0
        self.sums["principal"] += self.tokens(prompt[:len(prompt) - len(output)])
        self.worded = False

    def heard(self, kind: str, one: dict) -> None:
        """One event of the launch, in the common schema (`pp` already said on a `tool`)."""
        if kind == "tool":
            self.sums["calls"] += 1
            size = self.tokens(json.dumps(one.get("input") or {}, ensure_ascii=False))
            if one.get("pp"):
                self.piped.add(str(one.get("id")))
                self.sums["pp_input"] += size
            else:
                self.sums["tool_input"] += size
        elif kind == "tool-result":
            voice = "pp_result" if str(one.get("id")) in self.piped else "tool_result"
            self.sums[voice] += self.tokens(str(one.get("content") or ""))
        elif kind == "thinking":
            counted = one.get("tokens")
            self.sums["thinking"] += counted if isinstance(counted, int) else self.tokens(str(one.get("text") or ""))
        elif kind == "words":
            self.worded = True
            self.sums["words"] += self.tokens(str(one.get("text") or ""))

    def answered(self, text: str | None) -> None:
        """The launch's answer: counted as the model's words when the adapter said none."""
        if not self.worded and text:
            self.sums["words"] += self.tokens(text)


def pp_called(shell: str | None, console: str) -> bool:
    """-> whether a command calls the agent's console: its first word `./pp`, or the console by its
    absolute path."""
    try:
        words = shlex.split(shell or "")
    except ValueError:
        words = (shell or "").split()
    return bool(words) and words[0] in ("./pp", console)


def principal_environment(door: str | None = None, documents: str | None = None) -> dict:
    """-> the environment of this script's OWN calls to the agent's conductor: the launcher's,
    without what a run of the house would name to it (`PP_RUN`, `PP_HOME`, a session, a root of
    documents), plus the principal's mark -- the one site that poses it -- and, at an opening
    alone, the entry `--door` names, carried by `PP_DOOR`, and the root `--documents` names,
    carried by `PP_DOCUMENTS`."""
    environment = {one: value for one, value in os.environ.items()
                   if one not in ("PP_RUN", "PP_HOME", "PP_AGENT_SESSION", "PP_DOOR", "PP_DOCUMENTS")}
    environment[PRINCIPAL] = "true"
    if door is not None:
        environment["PP_DOOR"] = door
    if documents is not None:
        environment["PP_DOCUMENTS"] = documents
    return environment


def harness_environment(env: dict) -> dict:
    """-> the environment of the CLI: the launcher's without the principal's mark -- the one site
    that retires it: the agent's calls are never the principal's -- nor `PP_RUN`, `PP_HOME`,
    `PP_AGENT_SESSION`, `PP_DOOR`, `PP_DOCUMENTS`; plus what the adapter adds (`PP_MARBLE`, the
    session, the material)."""
    environment = {one: value for one, value in os.environ.items()
                   if one not in (PRINCIPAL, "PP_RUN", "PP_HOME", "PP_AGENT_SESSION", "PP_DOOR", "PP_DOCUMENTS")}
    environment.update(env)
    return environment


def engine_of(conductor, root: Path) -> Path:
    """-> the house's engine, the one the agents borrow."""
    return conductor.instance.engine_root(root) / "pp.py"


def conducted(conductor, root: Path, meta: Path, *args: str, door: str | None = None,
              documents: str | None = None) -> subprocess.CompletedProcess:
    """ONE call of this script to the agent's conductor under the principal's mark -- the house's
    engine on the agent's instance: `-new "<message>"` at an opening, `<key> "<message>"` at a
    frontier, the bare `<key>` that serves what the run holds or makes it advance, `-peek` for the
    block that stands. The engine judges; this script reads what it printed."""
    return subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta), *args],
                          capture_output=True, text=True, env=principal_environment(door, documents))


def principal_line(conductor, root: Path, meta: Path, *args: str, door: str | None = None,
                   documents: str | None = None) -> str:
    """-> the marked call as `--dry-run` says it: the mark, the door and the root when carried, the line."""
    return (f"{PRINCIPAL}=true " + (f"PP_DOOR={door} " if door is not None else "")
            + (f"PP_DOCUMENTS={shlex.quote(documents)} " if documents is not None else "")
            + shlex.join([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta), *args]))


def opened(conductor, root: Path, meta: Path, message: str, door: str | None,
           documents: str | None = None) -> tuple[str, str]:
    """-> (the key, the first output) of the run `-new "<message>"` opened under the mark on the
    agent's instance -- the key read on the output's first line. A `-new` the engine refuses
    (`door-unknown`, `documents-unknown`, `conducted-by-invalid`) launches nothing and leaves no run."""
    played = conducted(conductor, root, meta, "-new", message, door=door, documents=documents)
    found = KEY_LINE.match(played.stdout)
    if played.returncode != 0 or found is None:
        refuse(f"{refusal_of(played) or 'the opening gave no key'} -- nothing launched, no run opened")
    return found.group(1), played.stdout


def documents_asked(root: Path, asked: dict) -> str | None:
    """-> the root of documents `--documents` names, made absolute -- a relative path read from the
    house's directory --, None when the flag is absent. The engine judges the directory at `-new`."""
    given = asked.get("documents")
    if given is None:
        return None
    path = Path(given).expanduser()
    return str((path if path.is_absolute() else root.parent / path).resolve())


def documents_judged(conductor, meta: Path, key: str | None, documents: str | None) -> None:
    """Refuses `documents-fixed` before anything is launched when a resume names a root other than the
    one its run was opened with: a run keeps the composition it opened."""
    if key is None or documents is None:
        return
    held = conductor.persistence.documents_of(conductor.persistence.slot_of(meta, key))
    if Path(documents) != Path(held or "."):
        refuse(f"documents-fixed -- run {key} keeps the root of documents it opened with "
               f"({held or 'none'}): another root opens another run.")


def refusal_of(played: subprocess.CompletedProcess) -> str:
    """-> what the engine refused, in one line: its `REFUSED` line without the prefix, else the
    last line it printed, '' when it printed nothing."""
    lines = (played.stderr or played.stdout).strip().splitlines()
    said = next((one for one in lines if "REFUSED" in one), lines[-1] if lines else "")
    return said.strip().removeprefix("pp: ")


def served(conductor, root: Path, meta: Path, key: str, say, saying: bool) -> str | None:
    """The principal's bare call on a run the harness just left: it serves the output the agent's
    value call HELD, or the chunk waiting, or makes the run advance -- the engine alone judges
    which. -> what the engine printed, the next prompt; None when it refused (the repair bound,
    a run complete), the refusal said."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    what = ("served held output" if persistence.held_of(slot) else
            "served chunk" if persistence.pending_of(slot) else "advanced")
    played = conducted(conductor, root, meta, key)
    if played.returncode != 0 or not played.stdout.strip():
        why = refusal_of(played)
        if saying:
            say(key, f"refused {why or 'nothing'}", "refusal", {"detail": why})
        return None
    if saying:
        say(key, what, "advanced" if what == "advanced" else "served", {"what": what})
    return played.stdout


def resumed(conductor, root: Path, meta: Path, key: str, message: str) -> tuple[str, bool]:
    """-> (the first output a resume serves, whether the run was STANDING). A run parked at its
    frontier, or renewed by an upgrade: the marked `<key> "<message>"` opens the exchange (traced
    `prompt`; a renewed run reopens under its key). A run standing mid-exchange -- a wake-up died
    in its loop --: what it holds or the chunk waiting, by the marked bare call; else the block
    that stands, by `-peek`."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    waiting = bool(persistence.held_of(slot) or persistence.pending_of(slot))
    if persistence.renewed(slot) is not None or (standing_of(conductor, meta, key)[0] == "parked" and not waiting):
        return conducted(conductor, root, meta, key, message).stdout, False
    if waiting:
        return conducted(conductor, root, meta, key).stdout, True
    return conducted(conductor, root, meta, key, "-peek").stdout, True


def strays_of(persistence, meta: Path, known: set, key: str, say, saying: bool) -> list[str]:
    """-> the runs born at the agent since `known` but `key`: STRAY runs -- a `-new` the harness
    typed at the FINAL --, each said; `known` grows with them."""
    found = sorted({persistence.run_id_of(one) for one in persistence.slots(meta)} - known - {key})
    for stray in found:
        known.add(stray)
        if saying:
            say(key, f"stray run {stray}", "stray", {"run": stray})
    return found


def locks(conductor):
    """-> the engine's `state.lock` module: the wake lock a wake-up holds, the machine's
    maintenance lock a detached wake-up holds shared."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.lock")


def marked(lease, message: str, launched: int) -> None:
    """Writes the wake-up's MARK into the wake lock file it holds: the hour it started, the
    head of its message -- what a neighbour's line reads while the lock is held -- and how
    many responses the run had before this launch: a wake-up over that added none is DEAD."""
    handle = lease.handle
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps({"at": now(), "message": first_line(message),
                             "responses": launched}, ensure_ascii=False) + "\n")
    handle.flush()


def held_mark(lease, message: str) -> None:
    """Writes the MARK of a conversation that takes the wake lock of a run it resumes, before any
    message: the hour of the take, the head of the run's last message -- what a neighbour's line
    reads meanwhile --, `held: "chat"`; an interruption the mark before carried is kept, for the
    next message to say it; no `responses` -- no wake-up's outcome is awaited before a launch."""
    handle = lease.handle
    handle.seek(0)
    try:
        before = json.loads(handle.read())
    except ValueError:
        before = {}
    mark = {"at": now(), "message": first_line(message), "held": "chat"}
    if isinstance(before, dict) and before.get("interrupted") is True:
        mark["interrupted"] = True
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps(mark, ensure_ascii=False) + "\n")
    handle.flush()


def interrupted_mark(lease) -> None:
    """Adds `interrupted: true` to the MARK of the wake-up that holds `lease` -- its hour, its
    message and its responses kept: the next wake-up of the run reads it before it writes its own
    mark, which clears it."""
    handle = lease.handle
    handle.seek(0)
    try:
        mark = json.loads(handle.read())
    except ValueError:
        mark = {}
    handle.seek(0)
    handle.truncate()
    handle.write(json.dumps({**(mark if isinstance(mark, dict) else {}), "interrupted": True},
                            ensure_ascii=False) + "\n")
    handle.flush()


def message_head(after: bool) -> str:
    """-> the head the message opens under in the first prompt of a wake-up: the principal's,
    preceded by the interruption's when the run's last wake-up was interrupted."""
    return f"{INTERRUPTED}\n{HEAD}" if after else HEAD


def first_line(text: str) -> str:
    """-> the first line of a text that says something, cut at 60 characters: the head a
    neighbour reads -- for a team's wake-up, `[team <name> · you are <member>]`."""
    return next((" ".join(one.split()) for one in text.splitlines() if one.strip()), "")[:60]


def mark_of(lock, meta: Path, key: str) -> dict:
    """-> the mark the last launcher of `key` wrote into its wake lock file, {} when there
    is none or it does not read."""
    try:
        read = json.loads(launch_of(meta, key).read_text(encoding="utf-8"))
        return read if isinstance(read, dict) else {}
    except (OSError, ValueError):
        return {}


def answered_by(root: Path, name: str, key: str) -> list[dict]:
    """-> the responses of the run `key`, oldest first."""
    return [one for one in lines_of(record(root, RESPONSES)) if one.get("agent") == name and one.get("run") == key]


def launch_of(meta: Path, key: str) -> Path:
    """-> the LAUNCHER's file of the run `key`, `session-<key>.wake.lock` beside the run's
    slot: the lock a wake-up holds for its whole life and the mark it writes. The path is
    this package's published contract (README) -- the engine names none."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    return core(__file__).persistence.slot_of(meta, key).with_name(f"session-{key}.wake.lock")


def unconducted(conductor, root: Path, meta: Path, key: str, head: list[str], provider: str | None, grammar: str,
                limit, session: str | None, material: dict | None, identity: dict, message: str,
                neighbours: list, log, beat: int, say, cumul: float | None, scope: str | None, exchange_no: int = 0,
                after: bool = False, before=None) -> dict:
    """An exchange the house does NOT conduct (`conduct off`): ONE launch of the harness on its
    session, the message under its head (`after`: the interruption's head before it) and nothing
    of pp -- no call of pp before, during or after; the answer read as `exchanged` reads it, its
    cost read in the adapter's scope (`costed`); the launch's policy is `limit`'s (`limiter`), none
    left and nothing is launched. The run stays where it stands. `before(key)`, when a conversation
    gives it, plays ahead of the launch. -> the account `exchanged` renders."""
    flow = Flow(conductor.metrics.tokens)
    done = {"answered": None, "played": None, "launches": 1, "cost_usd": None, "session_cost_usd": cumul,
            "denials": [], "strays": [], "spent": False, "budget_spent": False, "interrupted": False,
            "session": session, "flow": flow.sums}
    launched = limit(None)
    if launched is None:
        done["launches"], done["budget_spent"] = 0, True
        return done
    if before is not None:
        before(key, say)
    prompt = headed(f"{message_head(after)}\n{message}", neighbours)
    flow.launch(prompt, "")
    argv, env, stdin = compose(conductor, root, meta, head, provider, prompt, launched, session, material)
    environment = harness_environment(env)
    environment.update(identity)
    try:
        played = waited(argv, meta.parent, environment, None, key, beat, say, log, stdin,
                        heard=hearer(conductor, meta, grammar, key, say, exchange_no, 1, flow))
    except KeyboardInterrupt:
        done["interrupted"] = True
        return done
    done["played"] = played
    if played.returncode != 0 and not played.stdout.strip():
        return done
    read = read_answer(conductor, meta, grammar, played)
    done["session"] = read["session"]
    launch_cost, done["session_cost_usd"] = costed(scope, read.get("cost_usd"), cumul)
    done["cost_usd"] = launch_cost
    done["denials"] = list(read.get("denials") or [])
    done["answered"] = read
    flow.answered(read["response"])
    say(key, "", "agent", {"exchange": exchange_no, "launch": 1, "text": read["response"], "cost_usd": launch_cost})
    return done


def served_of(kept: list | None, output: str) -> dict:
    """-> what a `conduction` says of the output it carries: `chars`, its length; with the trace's
    events since the conduction before (`kept`, None when no trace is followed), `blocks` --
    `{stack, command, wait}` of each block the engine rendered, the outputs held for this launch
    or the one it advanced to -- and `left` when the output is a piece of a cut one, the characters
    still to come."""
    said: dict = {"chars": len(output)}
    if kept is None:
        return said
    said["blocks"] = [{"stack": str(one.get("stack", "")), "command": str(one.get("command", "")),
                       "wait": bool(one.get("wait"))} for one in kept if one.get("kind") == "block"]
    pieces = [one for one in kept if one.get("kind") in ("cut", "chunk")]
    if pieces:
        said["left"] = int(pieces[-1].get("left") or 0)
    return said


def exchanged(conductor, root: Path, meta: Path, key: str, head: list[str], provider: str | None, grammar: str,
              limit, session: str | None, material: dict | None, identity: dict, message: str, output: str,
              neighbours: list, trace, log, beat: int, say, bound: int, cumul: float | None, scope: str | None,
              exchange_no: int = 0, after: bool = False, before=None) -> dict:
    """The LOOP of one exchange: the harness launched on the prompt -- the first time the message
    under its head (`after`: the interruption's head before it) then `output`, pp's first output;
    then pp's outputs alone --, in the session the
    first launch opened; after each launch the run is read: an output held, a chunk waiting or a
    block to advance -> this script's marked bare call, and the harness again on what came back;
    parked at its FINAL with nothing held -> over, the harness's last message is the response.
    Every step is `say`d while the trace is followed; two VOICES are said at every launch whatever
    the trace -- `conduction`, pp's output served to the harness, alone; `agent`, what the harness
    answered --, which a flow renders and a wake-up watched from stderr leaves unsaid.
    Before every launch `limit` (`limiter`) gives its policy, the run's remainder in it: none left, the
    loop stops there (`budget_spent`), the last response kept.
    -> {answered, played, launches, cost_usd, session_cost_usd, denials, strays, spent, budget_spent,
    interrupted, session}: the cost the SUM of the launches' costs, each read in the adapter's scope (`costed`);
    `interrupted` when a SIGINT ended the launch under way -- the harness terminated, what the
    finished launches answered kept, the run left where it stands. `before(key)`, when a conversation
    gives it, plays ahead of every launch -- `run` gives none."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    saying = trace is not None
    known = {persistence.run_id_of(one) for one in persistence.slots(meta)}
    flow = Flow(conductor.metrics.tokens)
    done = {"answered": None, "played": None, "launches": 0, "cost_usd": None, "session_cost_usd": cumul,
            "denials": [], "strays": [], "spent": False, "budget_spent": False, "interrupted": False,
            "session": session, "flow": flow.sums}
    kept: list[dict] = []                          # the trace's events since the conduction said last
    first = True
    while True:
        if done["launches"] >= bound:
            done["spent"] = True
            return done
        launched = limit(done["cost_usd"])
        if launched is None:                       # the run's cap leaves nothing: no launch more
            done["budget_spent"] = True
            return done
        if before is not None:
            before(key, say)
        prompt = headed(f"{message_head(after)}\n{message}\n\n{output}", neighbours) if first else output
        argv, env, stdin = compose(conductor, root, meta, head, provider, prompt, launched, done["session"], material)
        environment = harness_environment(env)
        environment.update(identity)
        done["launches"] += 1
        flow.launch(prompt, output)
        if saying:
            followed(trace, log, key, say, kept)
        say(key, "", "conduction", {"exchange": exchange_no, "launch": done["launches"], "text": output,
                                    **served_of(kept if saying else None, output)})
        kept.clear()
        try:
            played = waited(argv, meta.parent, environment, trace, key, beat, say, log, stdin, kept,
                            hearer(conductor, meta, grammar, key, say, exchange_no, done["launches"], flow))
        except KeyboardInterrupt:                  # the harness ended with the interruption: the loop stops here
            done["interrupted"] = True
            return done
        done["played"] = played
        first = False
        done["strays"] += strays_of(persistence, meta, known, key, say, saying)
        if played.returncode != 0 and not played.stdout.strip():
            return done
        read = read_answer(conductor, meta, grammar, played)   # no identity: nothing kept, said
        done["session"] = read["session"]
        launch_cost, done["session_cost_usd"] = costed(scope, read.get("cost_usd"), done["session_cost_usd"])
        if launch_cost is not None:
            done["cost_usd"] = round(float(done["cost_usd"] or 0.0) + launch_cost, 6)
        done["denials"] += list(read.get("denials") or [])
        done["answered"] = read
        flow.answered(read["response"])
        say(key, "", "agent", {"exchange": exchange_no, "launch": done["launches"], "text": read["response"],
                               "cost_usd": launch_cost})
        if saying:
            say(key, f"launch {done['launches']} · {len(stdin)} chars"
                + (f" · {launch_cost:g} USD" if launch_cost is not None else ""), "launch",
                {"launch": done["launches"], "chars": len(stdin), "cost_usd": launch_cost})
        if played.returncode != 0:
            return done
        if (not persistence.held_of(slot) and not persistence.pending_of(slot)
                and standing_of(conductor, meta, key)[0] == "parked"):
            return done
        output = served(conductor, root, meta, key, say, saying)
        if output is None:
            return done


def wake_log_of(lock, meta: Path, key: str) -> Path:
    """-> the wake LOG of the run `key`, `session-<key>.wake.log` beside its wake lock: the
    launcher's file, where a detached wake-up writes what `run` says on stderr."""
    return launch_of(meta, key).with_name(f"session-{key}.wake.log")


def reported(lock, meta: Path, key: str) -> None:
    """The detached child's REPORT: one JSON line `{key, pid}` on stdout, the parent's
    answer; then stdout goes to nowhere and stderr to the wake log -- the parent is gone."""
    print(json.dumps({"key": key, "pid": os.getpid()}), flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    quiet = os.open(os.devnull, os.O_WRONLY)
    log = os.open(wake_log_of(lock, meta, key), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.dup2(quiet, 1)
    os.dup2(log, 2)
    os.close(quiet)
    os.close(log)


def on_end(command: str, root: Path, name: str, key: str | None, state: str) -> None:
    """Plays the caller's `--on-end` command by the shell, once the wake lock is released and
    the records written: `PP_AGENT_NAME`, `PP_AGENT_RUN` and `PP_AGENT_STATE` in its
    environment, its exit code said on stderr -- never the wake-up's own."""
    environment = {**os.environ, "PP_AGENT_NAME": name, "PP_AGENT_RUN": key or "", "PP_AGENT_STATE": state}
    played = subprocess.run(command, shell=True, cwd=str(root.parent), env=environment)
    print(f"pp-agent: on-end rc {played.returncode}", file=sys.stderr)


def under_way(lock, persistence, meta: Path, key: str | None = None) -> list[tuple[str, str, str]]:
    """-> (key, since HH:MM, the head of the message) of every run of the agent whose wake
    lock is held -- a wake-up under way, its slot reserved or opened -- but `key`: the local
    hour of its mark and the first line of its message; a mark the file does not carry reads
    as `?`."""
    found = []
    state = meta / persistence.DIRECTORY
    for path in sorted(state.glob("session-*.wake.lock")) if state.is_dir() else []:
        other = path.name.removeprefix("session-").split(".", 1)[0]
        if other == key or not lock.held(path):
            continue
        since, head = "?", "?"
        try:
            mark = json.loads(path.read_text(encoding="utf-8"))
            since = datetime.fromisoformat(str(mark.get("at"))).astimezone().strftime("%H:%M")
            head = first_line(str(mark.get("message", ""))) or "?"
        except (OSError, ValueError, AttributeError, TypeError):
            pass
        found.append((other, since, head))
    return found


def headed(prompt: str, neighbours: list[tuple[str, str, str]]) -> str:
    """-> the prompt with the neighbours line at its head -- `[runs under way: <key> since
    HH:MM « head » · …]`, a blank line, the message -- or the prompt alone when no other
    run of the agent plays."""
    if not neighbours:
        return prompt
    line = " · ".join(f"{key} since {since} « {head} »" for key, since, head in neighbours)
    return f"[runs under way: {line}]\n\n{prompt}"


# --- the material: one clone per run, inside the agent's home ------------------------------

class WorkFailure(Exception):
    """A step of the material that refuses -- said by the caller once the wake lock is dealt with."""


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """One git command, captured: the clone and the repository are always named by absolute paths."""
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=str(cwd) if cwd else None)


def repo_lock_of(root: Path, conductor, repo: Path) -> Path:
    """-> the house's lock file for ONE target repository: `.sys/state/work-<digest>.lock`,
    the digest of the repository's absolute path -- the repository itself is never written
    but by its refs."""
    import hashlib
    digest = hashlib.sha1(str(repo).encode("utf-8")).hexdigest()[:12]
    return root / conductor.persistence.DIRECTORY / f"work-{digest}.lock"


def call_wait(conductor, root: Path) -> float:
    """-> `call_lock_wait` as the house's settings say it, 30 s without them."""
    try:
        return float(conductor.settings.of(root).call_lock_wait)
    except Exception:                                   # no settings to read: the engine's seed
        return 30.0


@contextmanager
def under_repo_lock(conductor, root: Path, repo: Path):
    """The clone and the push of one repository, one wake-up at a time: the lock acquired
    within `call_lock_wait`, `work-busy` beyond."""
    lock = locks(conductor)
    path = repo_lock_of(root, conductor, repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    lease = lock.acquire(path, wait=call_wait(conductor, root))
    if lease is None:
        raise WorkFailure(f"work-busy -- another wake-up clones or pushes {repo} and has not finished within "
                          "call_lock_wait: replay once it has.")
    try:
        yield lease
    finally:
        lock.release(lease)


def workdir_of(root: Path, name: str, key: str) -> dict | None:
    """-> the last line of `workdirs.jsonl` for the run: its material's state, or None."""
    found = [one for one in lines_of(record(root, WORKDIRS)) if one.get("agent") == name and one.get("run") == key]
    return found[-1] if found else None


def material_of(entry: dict) -> dict:
    """-> what the face takes: the path under the workspace, the branch, the base."""
    return {"path": entry["path"], "branch": entry["branch"], "base": entry["base"]}


def base_of(repo: Path, asked: str | None) -> tuple[str, str]:
    """-> (ref, short sha) of what the run's branch is cut from: the repository's current
    branch, or the ref asked by `--base`; a ref that is no commit refuses `work-clone-failed`."""
    ref = asked
    if ref is None:
        current = git("symbolic-ref", "--short", "-q", "HEAD", cwd=repo)
        ref = current.stdout.strip() or "HEAD"
    found = git("rev-parse", "--short", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=repo)
    if found.returncode != 0 or not found.stdout.strip():
        raise WorkFailure(f"work-clone-failed -- `{ref}` is no commit of {repo}: "
                          f"{found.stderr.strip()[-200:] or 'not a git repository'}")
    return ref, found.stdout.strip()


def identity_of(name: str, slug: str) -> dict:
    """-> the git identity of the exchange, in the harness's environment: the agent's path,
    its address at the house (`rep1/ag1` -> `rep1.ag1@<slug>`)."""
    email = f"{name.replace('/', '.')}@{slug or 'house'}"
    return {"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email,
            "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email}


def planned(name: str, key: str, repo: Path, asked: str | None) -> dict:
    """-> the material a dry run would place: nothing cloned, the repository read for its base."""
    try:
        ref, sha = base_of(repo, asked)
    except WorkFailure:
        ref, sha = asked or "HEAD", "?"
    return {"repo": str(repo), "path": f"{WORK}/{key}", "branch": f"agent/{name}/{key}", "base": f"{ref}@{sha}"}


def placed(conductor, root: Path, name: str, meta: Path, key: str, repo: Path, asked: str | None) -> dict:
    """The clone of the run: under the repository's lock, `git clone --no-checkout` to
    `<path>/work/<key>` (hard links on one file system), the branch
    `agent/<path>/<key>` cut from the base; a `.gitignore` under `work/` once. A git that
    fails refuses `work-clone-failed`, the half clone removed. -> the `open` line written."""
    home = meta.parent / WORK
    clone = home / key
    with under_repo_lock(conductor, root, repo):
        ref, sha = base_of(repo, asked)
        home.mkdir(parents=True, exist_ok=True)
        ignore = home / ".gitignore"
        if not ignore.exists():
            ignore.write_text("*\n", encoding="utf-8")
        cloned = git("clone", "-q", "--no-checkout", str(repo), str(clone))
        if cloned.returncode != 0:
            shutil.rmtree(clone, ignore_errors=True)
            raise WorkFailure(f"work-clone-failed -- git clone of {repo}: {cloned.stderr.strip()[-300:]}")
        local = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=clone)
        start = ref if local.returncode == 0 else f"origin/{ref}"
        switched = git("switch", "-q", "-c", f"agent/{name}/{key}", start, cwd=clone)
        if switched.returncode != 0:
            shutil.rmtree(clone, ignore_errors=True)
            raise WorkFailure(f"work-clone-failed -- git switch -c agent/{name}/{key} {start}: "
                              f"{switched.stderr.strip()[-300:]}")
    entry = {"at": now(), "agent": name, "run": key, "repo": str(repo), "path": f"{WORK}/{key}",
             "branch": f"agent/{name}/{key}", "base": f"{ref}@{sha}", "state": "open"}
    append(record(root, WORKDIRS), entry)
    return entry


def standing_material(root: Path, name: str, meta: Path, key: str) -> dict | None:
    """-> the run's material as recorded, None when it has none; `workdir-missing` when the
    clone is gone or was pruned: a run is never resumed without its material."""
    entry = workdir_of(root, name, key)
    if entry is None:
        return None
    if entry.get("state") == "pruned":
        raise WorkFailure(f"workdir-missing -- the material of run {key} ({entry['path']}) was pruned: a run is "
                          "never resumed without its material; a new run clones again.")
    if not (meta.parent / entry["path"]).is_dir():
        raise WorkFailure(f"workdir-missing -- the material of run {key} ({entry['path']}) is gone: "
                          f"`agent prune {name} {key} --force` forgets it, a new run clones again.")
    return entry


def shipped(conductor, root: Path, name: str, entry: dict) -> dict:
    """The push after the harness, under the repository's lock: the branch to the repository
    by its absolute path; `commits` ahead of the base, `dirty` when the clone has unstaged
    changes. A push that fails is recorded (`pushed: false`, its `reason`) -- the response
    is the harness's, the branch stays in the clone. -> the line written."""
    clone = agent_at(root, conductor, name).parent / entry["path"]
    repo = Path(entry["repo"])
    base_sha = str(entry["base"]).rsplit("@", 1)[-1]
    counted = git("rev-list", "--count", f"{base_sha}..HEAD", cwd=clone)
    commits = int(counted.stdout.strip()) if counted.returncode == 0 and counted.stdout.strip().isdigit() else None
    dirty = bool(git("status", "--porcelain", cwd=clone).stdout.strip())
    reason = None
    try:
        with under_repo_lock(conductor, root, repo):
            pushed = git("push", "-q", str(repo), entry["branch"], cwd=clone)
        if pushed.returncode != 0:
            reason = pushed.stderr.strip()[-300:] or f"git push rc {pushed.returncode}"
    except WorkFailure as failure:
        reason = str(failure)
    line = {**entry, "at": now(), "state": "pushed" if reason is None else "unpushed",
            "pushed": reason is None, "commits": commits, "dirty": dirty}
    line.pop("reason", None)
    if reason is not None:
        line["reason"] = reason
    append(record(root, WORKDIRS), line)
    return line


def add(rest: list[str]) -> int:
    """`agent add <path> [--type <package>]`: gives birth to the agent at `<path>` by the
    engine's own install -- an instance that BORROWS the house's machine, no door, the seed
    of an interactive instance, its slug the path's last segment. Refuses before writing:
    `agent-path-invalid`, `agent-exists`, `type-unsupported` (an agent is born of the kit alone),
    and a path under a subtree that carries another machine. The birth plays under the house's
    BIRTH lock for that path (`born-busy` past `call_lock_wait`), the one a team's start takes:
    one path is born once, whoever asks."""
    root, conductor = house()
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    path, rest = rest[0], rest[1:]
    if rest and (rest[0] != "--type" or len(rest) != 2):
        refuse(USAGE)
    meta = agent_at(root, conductor, path)
    if rest:
        refuse(f"type-unsupported -- `--type {rest[1]}`: an agent is born of the kit alone, no type is resolved.")
    if conductor.instance.is_instance(meta):
        refuse(f"agent-exists -- an instance stands at `{path}` already ({meta}).")
    if any(one.exists() and not one.is_dir() for one in [meta.parent, *meta.parent.parents]
           if one.is_relative_to(root.parent)):
        refuse(f"agent-path-invalid -- `{path}`: a file stands on that path under {root.parent}.")
    instance = conductor.instance
    try:
        machine, borrowed = instance.machine_of(root), instance.machine_of(meta)
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    if borrowed != machine:
        refuse(f"agent-path-invalid -- `{path}` stands under {borrowed.parent}, which carries a machine of its own: "
               "an agent borrows the house's machine.")
    lock = locks(conductor)
    gate = birth_lock_of(root, conductor, path)
    gate.parent.mkdir(parents=True, exist_ok=True)
    lease = lock.acquire(gate, wait=call_wait(conductor, root))
    if lease is None:
        refuse(f"born-busy -- `{path}` is being born by another call that has not finished within call_lock_wait: "
               "replay once it has.")
    try:
        if instance.is_instance(meta):
            refuse(f"agent-exists -- an instance stands at `{path}` already ({meta}).")
        try:
            conductor.install.install(instance.engine_root(root) / "pp.py", meta, [], slug=path.rsplit("/", 1)[-1],
                                      doors=False, borrow=True)
        except conductor.Refusal as refusal:
            refuse(str(refusal))
    finally:
        lock.release(lease)
    print(f"pp-agent: {path} born -- {meta} borrows the machine of {machine}; {capped(conductor, meta)}")
    return 0


def capped(conductor, meta: Path) -> str:
    """Sets the agent's `max_harness_tool_output` at the size of a prompt, through the engine's
    settings face (`settings.write`: one line of the agent's own settings, judged by the reading,
    the file never opened here): an output of pp reaches the harness whole, a boot in one launch.
    -> what the birth says of it."""
    conductor.settings.write(meta, "max_harness_tool_output", HARNESS_CAP)
    return f"max_harness_tool_output {HARNESS_CAP}"


def birth_lock_of(root: Path, conductor, path: str) -> Path:
    """-> the house's BIRTH lock for one agent's path: `.sys/state/born-<digest>.lock`, the
    digest of the path -- the lock a team's start takes too, so that one path is born once."""
    import hashlib
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:12]
    return root / conductor.persistence.DIRECTORY / f"born-{digest}.lock"


def exchange(conductor, root: Path, name: str, meta: Path, asked: dict, key: str | None, message: str | None,
             lease, say=None, before=None) -> dict:
    """ONE exchange of a message with the agent at `meta`, conducted by the house -- the one
    function `run` and `chat` play: every judgment before the launch (the harness, the policy, the
    run, its session, its material, the composed line), the opening (`key` None: the marked `-new`,
    the launcher's lock taken then) or the resume (under `lease` when the caller holds it, taken here
    otherwise: `run-busy`), the message's line at `messages.jsonl`, the trace followed, the LOOP, the
    material sent back, the response and the session recorded, the run's state read. A refusal met
    before the launch gives a lock taken here back and leaves the run as it was. -> the ISSUE:
    `dry` (a dry run: said, nothing opened), else `key`, `lease` (held by the caller from here),
    `kept` (the response's record line, None when nothing was kept -- then `reason` says why),
    `done` (the loop's account), `played` (the last launch), `said` (`parked`, `standing`, `stopped`,
    `interrupted`), `arrived`, `stack`, `exchanges`, `standing` (a standing run taken up), `sent_back`
    (the material's push), `bound`, `interrupted`, `after` (the run's last wake-up was interrupted: the
    message's head opens on the interruption's). `say(key, line, kind, fields)` is who says the
    steps and the voices: the engine's `log.said` on stderr unless the caller gives its own; `before(key, say)`
    plays ahead of every launch when the caller gives it (the switches waiting: a conversation's, or the
    `--package` of a wake-up), handed the exchange's own `say`."""
    instance, persistence = conductor.instance, conductor.persistence
    bare = asked.get("conduct") is False and key is not None   # `conduct off`: one launch, no call of pp
    policy = policy_of(conductor, asked)
    beat = heartbeat_of(asked)
    bound = launches_of(asked)
    house_judged(conductor, meta, name, key, asked)
    head, provider = provider_of(conductor, root, asked)   # the harness first: a refusal writes nothing
    grammar = grammar_of(asked, provider)
    refused = unmeasured(conductor, root, asked, policy)
    if refused is not None:
        refuse(refused)
    try:
        scope = cost_scope(conductor, root, grammar)
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    opening = key is None
    if asked["door"] is not None and not opening:
        refuse("door-on-resume -- a door opens a run's FIRST exchange; a resume continues the conversation.")
    documents = documents_asked(root, asked)
    lock = locks(conductor)
    if not opening and not persistence.slot_of(meta, key).is_file():
        refuse(f"run-unknown -- no run `{key}` at {meta}.")
    documents_judged(conductor, meta, key, documents)
    if not asked["dry-run"] and message is None:   # judged before anything is opened
        refuse("message-missing -- a wake-up carries a message: it is the harness's prompt, as a message "
               "typed in a session.")
    spent = spent_of(root, name, key)
    limit = limiter(conductor, root, provider, policy, spent)
    if limit(None) is None:                        # the cap reached: nothing launched, nothing recorded
        said = budget_of(policy, spent)
        reason = (f"budget-spent -- run {key} spent {said['spent']:g} USD of its {said['cap']:g} USD cap: nothing "
                  f"launched, the run as it was -- raise the cap (`--max-budget-usd`, a `set`) to go on")
        if asked["dry-run"]:
            refuse(reason)
        return {"dry": False, "key": key, "lease": lease, "kept": None, "reason": reason, "played": None,
                "done": {"answered": None, "played": None, "launches": 0, "cost_usd": None, "session_cost_usd": None,
                         "denials": [], "strays": [], "spent": False, "budget_spent": True, "interrupted": False,
                         "session": None, "flow": {}},
                "said": "", "arrived": False, "stack": "", "exchanges": persistence.turns_of(persistence.slot_of(meta, key)),
                "standing": False, "sent_back": None, "bound": bound, "interrupted": False, "after": False,
                "budget": said}
    slug = str(instance.read(root).get("slug", ""))
    taken = False                                  # the launcher's lock, when this call takes it itself
    if lease is None and not opening and not asked["dry-run"]:
        lease = lock.try_(launch_of(meta, key))
        if lease is None:
            refuse(f"run-busy -- a wake-up plays run {key}: one wake-up at a time on a run.")
        taken = True
    work = Path(asked["work"]).resolve() if asked["work"] is not None else None
    shown = message if message is not None else "<the message>"
    try:                                           # every judgment before the opening and the launch: a
        if opening:                                # refusal here leaves the run as it was, and opens none
            session = None
        elif lease is not None and not taken and session_of_run(root, name, key) is None:
            session = None                         # the caller's own run, no launch of it ever answered: a fresh session
        else:
            session = resumable(conductor, root, meta, name, key, provider)
        entry = None
        try:
            if not opening:
                entry = standing_material(root, name, meta, key)
                if work is not None and entry is not None:
                    raise WorkFailure(f"work-standing -- run {key} has its material already ({entry['path']} of "
                                      f"{entry['repo']}): one run, one material.")
            if work is not None and entry is None:
                base_of(work, asked["base"])       # a repository that cannot be cloned refuses now: no run opened
                entry = planned(name, key or "<key>", work, asked["base"])
        except WorkFailure as failure:
            refuse(str(failure))
        material = material_of(entry) if entry is not None else None
        preview = headed(f"{HEAD}\n{shown}\n\n<the output of ./pp {'-new' if opening else key}>",
                         under_way(lock, persistence, meta, key))
        argv, env, stdin = compose(conductor, root, meta, head, provider, preview, limit(None), session, material)
    except SystemExit:
        if taken:
            lock.release(lease)
        raise
    identity = identity_of(name, slug) if material is not None else {}
    if asked["dry-run"]:
        print(f"pp-agent: dry run -- {name} · cwd {meta.parent} · nothing launched, no run opened")
        print(principal_line(conductor, root, meta, *(["-new", shown] if opening else [key, shown]),
                             door=asked["door"] if opening else None,
                             documents=documents if opening else None))
        print(shlex.join(argv))
        for one, value in {**env, **identity}.items():
            print(f"  env {one}={value}")
        for value in asked.get("package") or []:   # the switches a launch would play, none played
            switch, _, state = str(value).partition("=")
            print(f"  package {switch} {state}")
        print(f"--- stdin ({len(stdin)} chars) ---")   # the head of the first prompt: what the harness reads first
        print(stdin)
        return {"dry": True}
    standing = False
    after = not opening and mark_of(lock, meta, key).get("interrupted") is True   # read before this wake-up's mark
    log = tracing(conductor)
    trace = None
    if opening:                                    # all judged: the run opened under the mark, the lock, the material
        key, output = opened(conductor, root, meta, message or "", asked["door"], documents)
        lease = lock.try_(launch_of(meta, key))
        if lease is None:
            refuse(f"run-busy -- a wake-up plays run {key}: one wake-up at a time on a run.")
        marked(lease, message or "", 0)
        if work is not None:
            try:
                entry = placed(conductor, root, name, meta, key, work, asked["base"])
            except WorkFailure as failure:
                lock.release(lease)
                refuse(f"{failure} -- run {key} opened, nothing launched")
            material = material_of(entry)
    elif bare:                                     # an exchange the house does not conduct: pp is not called
        marked(lease, message or "", len(answered_by(root, name, key)))
        output = ""
    else:                                          # the wake-up's mark, then the exchange opened or taken up
        marked(lease, message or "", len(answered_by(root, name, key)))
        if not asked["quiet"]:                     # followed BEFORE the call that serves the first output
            trace = log.follow(meta, key, from_end=True)
        output, standing = resumed(conductor, root, meta, key, message or "")
    neighbours = under_way(lock, persistence, meta, key)
    if asked["detached"]:                          # the lock held, the run known: the parent may go
        reported(lock, meta, key)
    sent = {"at": now(), "from": slug, "to": name, "run": key,       # the message at the launch:
            "message": message, "policy": policy}                    # a wake-up under way is on record
    if bare:
        sent["conducted"] = False
    if asked["tag"] is not None:
        sent["tag"] = str(asked["tag"])
    if asked["detached"]:
        sent["pid"] = os.getpid()
    append(record(root, MESSAGES), sent)
    if say is None:
        say = step_sayer(log, asked["json"])
    say = keeper(root, name, say)                  # every event of the exchange kept in the run's flow
    if opening and not asked["quiet"]:             # an opening reads its trace whole: the boot's blocks
        trace = log.follow(meta, key)
    exchange_no = persistence.turns_of(persistence.slot_of(meta, key)) + 1
    say(key, "", "opened", {"agent": name, "exchange": exchange_no, "resumed": not opening, "standing": standing,
                            "provider": provider or "harness", "policy": policy,
                            "packages": packages_of(conductor, meta, key), "cap": cap_of(conductor, meta),
                            "documents": persistence.documents_of(persistence.slot_of(meta, key)) or None,
                            "budget": budget_of(policy, spent),
                            **({"conducted": False} if bare else {}), **({"interrupted": True} if after else {})})
    say(key, "", "principal", {"exchange": exchange_no, "text": message})
    cumul_before = next((one.get("session_cost_usd") for one in reversed(answered_by(root, name, key))
                         if isinstance(one.get("session_cost_usd"), (int, float))), None)   # the session's cumul so far
    if bare:
        done = unconducted(conductor, root, meta, key, head, provider, grammar, limit, session, material, identity,
                           message or "", neighbours, log, beat, say, cumul_before, scope, exchange_no, after, before)
    else:
        done = exchanged(conductor, root, meta, key, head, provider, grammar, limit, session, material, identity,
                         message or "", output, neighbours, trace, log, beat, say, bound, cumul_before, scope,
                         exchange_no, after, before)
    played, answered, interrupted = done["played"], done["answered"], done["interrupted"]
    if interrupted:                                # the next wake-up of the run says it to the model
        interrupted_mark(lease)
    sent_back = shipped(conductor, root, name, entry) if entry is not None else None   # the branch, whatever the answer
    issue = {"dry": False, "key": key, "lease": lease, "kept": None, "reason": None, "done": done, "played": played,
             "say": say,
             "said": "", "arrived": False, "stack": "", "exchanges": 0, "standing": standing, "sent_back": sent_back,
             "bound": bound, "interrupted": interrupted, "after": after,
             "budget": budget_of(policy, spent + float(done["cost_usd"] or 0.0))}
    if answered is None:                           # no launch finished: nothing kept
        stack = standing_of(conductor, meta, key)[1]
        issue["reason"] = (f"interrupted -- run {key} stands on `{stack}`, nothing recorded: the next message, or "
                           f"`--run {key}`, takes it up" if interrupted else
                           f"harness rc {played.returncode}: {played.stderr.strip()[-300:] or 'no output'} -- nothing recorded")
        return issue
    error = answered.get("error")
    if interrupted:
        error = "interrupted"
    elif played.returncode != 0 and error is None:
        error = f"harness rc {played.returncode}: {(played.stderr or played.stdout).strip()[-300:]}"
    elif played.returncode == 0 and done["budget_spent"]:
        error = "budget-spent"                     # the run's cap stopped it between two launches
    at = now()
    index = len(answered_by(root, name, key)) + 1
    kept = {"at": at, "agent": name, "run": key, "index": index, "response": answered["response"],
            "cost_usd": done["cost_usd"], "session_cost_usd": done["session_cost_usd"], "launches": done["launches"],
            "denials": done["denials"], "error": error, "harness_rc": played.returncode}
    if error == "budget-spent":
        said = issue["budget"]
        kept["budget"] = {"cap": said["cap"], "spent": said["spent"]}
    if bare:
        kept["conducted"] = False
    kept["flow"] = dict(done["flow"])
    append(record(root, RESPONSES), kept)
    if (session_of_run(root, name, key) or {}).get("session") != done["session"]:
        append(record(root, SESSIONS), {"at": at, "agent": name, "run": key, "provider": provider,
                                        "session": done["session"]})
    slot = persistence.slot_of(meta, key)
    state, stack = standing_of(conductor, meta, key)
    settled = not persistence.held_of(slot) and not persistence.pending_of(slot)
    arrived = (played.returncode == 0 and (state == "parked" or bare) and settled and not done["spent"]
               and not done["budget_spent"] and not interrupted and answered.get("response") is not None)
    issue.update({"kept": kept, "arrived": arrived, "stack": stack, "exchanges": persistence.turns_of(slot),
                  "said": ("interrupted" if interrupted else "stopped" if played.returncode != 0 else
                           "unconducted" if bare else "parked" if arrived else "standing")})
    return issue


def verdict(name: str, key: str, issue: dict) -> str:
    """-> the verdict line of an exchange, as stderr says it: the agent, the run, the exchange, its
    state, the harness's exit code, the cost, the launches, the strays, a standing run taken up, a
    wake-up after an interruption, the material's push; under a cap, what the run spent of it."""
    done, played, sent_back = issue["done"], issue["played"], issue["sent_back"]
    cost, said = done["cost_usd"], issue.get("budget")
    branch = ""
    if sent_back is not None:
        branch = (f" · {sent_back['branch']} {'pushed' if sent_back['pushed'] else 'push failed'}"
                  f" ({sent_back.get('commits')} commit(s){', dirty' if sent_back.get('dirty') else ''})")
    return (f"pp-agent: {name} · run {key} · exchange {issue['exchanges']} · {issue['said']} · harness rc {played.returncode}"
            + (f" · {cost:g} USD" if isinstance(cost, float) else "")
            + (f" · {said['spent']:g}/{said['cap']:g} USD cap" if said else "") + f" · {done['launches']} launch(es)"
            + (f" · {len(done['strays'])} stray run(s)" if done["strays"] else "")
            + (" · standing resumed" if issue["standing"] else "")
            + (" · after an interruption" if issue["after"] else "") + branch)


def reason_of(conductor, meta: Path, key: str, issue: dict) -> str | None:
    """-> why an exchange that kept a response did not end well -- the first that applies: the
    interruption, the harness's exit code, the run's cap reached, the launches spent, the frontier missed,
    the push that failed --; None when it ended well."""
    done, played, sent_back, stack = issue["done"], issue["played"], issue["sent_back"], issue["stack"]
    if issue["interrupted"]:
        return f"interrupted -- run {key} stands on `{stack}`: the next message, or `--run {key}`, takes it up"
    if played.returncode != 0:
        return f"harness rc {played.returncode}: {(played.stderr or played.stdout).strip()[-300:]}"
    if done["budget_spent"]:
        said = issue["budget"]
        return (f"budget-spent -- run {key} spent {said['spent']:g} USD of its {said['cap']:g} USD cap; the last response "
                f"is kept, the run stands on `{stack}`: raise the cap (`--max-budget-usd`, a `set`) and `--run {key}` "
                "takes it up")
    if done["spent"]:
        return (f"launches-spent -- run {key} played {issue['bound']} launch(es) without reaching its frontier; the last "
                f"response is kept, the run stands on `{stack}`: `--run {key}` takes it up, `--launches` raises the bound")
    if not issue["arrived"]:
        refused = [one for one in trace_events(conductor, meta, key) if one.get("kind") == "refusal"]
        why = f"; last refusal: {refused[-1].get('detail', '')}" if refused else ""
        return f"the run did not reach its frontier -- it stands on `{stack}`, the response recorded{why}"
    if sent_back is not None and not sent_back["pushed"]:
        return (f"push failed -- {sent_back.get('reason')} -- the response is kept, the branch "
                f"{sent_back['branch']} stays in {sent_back['path']}: replay a wake-up once the repository answers.")
    return None


def run(rest: list[str]) -> int:
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    asked = flags(rest)
    switches = asked_switches(conductor, meta, asked)        # judged before anything: a refusal leaves nothing
    asked = resumed_of(conductor, root, name, asked["run"], asked)
    waiting = seeded(conductor, meta, asked["run"], switches)
    issue = exchange(conductor, root, name, meta, asked, asked["run"], message_of(asked), None,
                     before=replayer(conductor, root, meta, waiting) if waiting else None)
    if issue["dry"]:
        return 0
    lock = locks(conductor)
    key, lease, kept = issue["key"], issue["lease"], issue["kept"]
    if kept is None:                               # nothing kept: the lock given back, the reason said
        flow_closed(issue, issue["reason"])
        if lease is not None:
            lock.release(lease)
        refuse(issue["reason"])
    flow_closed(issue, reason_of(conductor, meta, key, issue))   # kept before the lock goes: one writer at a time
    said = issue["said"]
    lock.release(lease)                            # the records written: the wake-up is over
    if asked["on-end"] is not None:                # after the release: the command may reopen this run
        on_end(str(asked["on-end"]), root, name, key, said)
    rendered(kept, issue["done"]["session"], said, asked["json"])
    sys.stdout.flush()
    print(verdict(name, key, issue), file=sys.stderr)
    reason = reason_of(conductor, meta, key, issue)
    if reason is not None:
        refuse(reason)
    return 0


def typed(stream):
    """-> the messages typed on `stream`, one per line: a line ending on a backslash goes on with
    the next -- the backslash taken out, the line break kept --; an empty message sends nothing."""
    parts: list[str] = []
    for line in stream:
        line = line.rstrip("\n")
        if line.endswith("\\"):
            parts.append(line[:-1] + "\n")
            continue
        parts.append(line)
        message, parts = "".join(parts), []
        if message.strip():
            yield message
    message = "".join(parts).rstrip("\n")
    if message.strip():
        yield message


def commanded(stream, busy):
    """-> the COMMANDS of a conversation's flow, read on `stream` by a thread of its own so that one
    arrives during an exchange too -- one JSON object per line: `{"kind": "message", "text": …}`
    yields `("message", text)`; `{"kind": "stop"}` raises SIGINT at this process while an exchange
    plays (`busy` set: the harness ends, the exchange is said `interrupted`) and does nothing
    otherwise; `{"kind": "set", …}` yields `("set", fields, line)` -- the policy of the next launches;
    `{"kind": "conduct", "on": …}` yields `("conduct", on, line)`; `{"kind": "package", "name": …,
    "on": …}` yields `("package", name, on, line)`;
    `{"kind": "quit"}` ends the commands after the exchange under way; a line that does
    not read yields `("refused", "command-unreadable", line)`, a kind nobody knows
    `("refused", "command-unknown", line)`. The end of the stream ends the commands."""
    import queue
    import signal
    import threading
    box: queue.Queue = queue.Queue()
    main = threading.main_thread().ident

    def reading() -> None:
        for raw in stream:
            line = raw.rstrip("\n")
            try:
                read = json.loads(line)
            except ValueError:
                box.put(("refused", "command-unreadable", line))
                continue
            kind = read.get("kind") if isinstance(read, dict) else None
            if kind == "message" and isinstance(read.get("text"), str):
                box.put(("message", read["text"]))
            elif kind == "set":
                box.put(("set", {key: value for key, value in read.items() if key != "kind"}, line))
            elif kind == "conduct" and isinstance(read.get("on"), bool):
                box.put(("conduct", read["on"], line))
            elif kind == "package" and isinstance(read.get("name"), str) and isinstance(read.get("on"), bool):
                box.put(("package", read["name"], read["on"], line))
            elif kind == "stop":
                if busy.is_set() and main is not None:   # to the MAIN thread, where the exchange waits on the harness
                    signal.pthread_kill(main, signal.SIGINT)
            elif kind == "quit":
                box.put(("quit",))
                break
            else:
                box.put(("refused", "command-unknown", line))
        box.put(None)

    threading.Thread(target=reading, daemon=True).start()
    while True:
        item = box.get()
        if item is None or item[0] == "quit":
            return
        yield item


def verdict_of(issue: dict, reason: str | None) -> dict:
    """-> the fields of a `verdict` event: what the verdict line says, as data -- the state, the
    harness's exit code, the cost, the launches, the strays, a standing run taken up, whether a
    response was kept, the run's budget under a cap, and the reason when the exchange did not end well."""
    done, played = issue["done"], issue["played"]
    kept = issue["kept"] is not None
    state = issue["said"] if kept else ("interrupted" if issue["interrupted"] else "stopped")
    return {"exchange": issue["exchanges"], "state": state, "harness_rc": played.returncode if played else None,
            "cost_usd": done["cost_usd"], "launches": done["launches"], "strays": len(done["strays"]),
            "standing_resumed": issue["standing"], "kept": kept, "budget": issue.get("budget"),
            **({"reason": reason} if reason else {})}


def chat(rest: list[str]) -> int:
    """`agent chat`: a CONVERSATION at the foreground, conducted by the house -- the messages read on
    stdin one per line (`typed`), each an `exchange` of ONE run, held with its session and its wake
    lock from a message to the next: the first message opens the run (`--run <key>` resumes one),
    every later one resumes it. After each exchange the response goes to stdout and the verdict to
    stderr, as `run` says them; an exchange that ends badly says why on stderr and the conversation
    goes on, the run standing for the next message. A SIGINT during an exchange ends the harness and
    is said `interrupted`; one while waiting for a message, or the end of stdin, closes the
    conversation: the lock released, exit 0, the run resumable by `--run <key>`.
    Under `--json` the conversation is a FLOW: commands on stdin (`commanded`), events on stdout --
    one JSON object per line, each naming its voice by its `kind` (`event_sayer`: `opened`,
    `principal`, `conduction`, `agent`, `step`; here `ready`, `response`, `verdict`, `waiting`,
    `refused`, `closed`) --, stderr silent from the first command on."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    asked = flags(rest)
    switches = asked_switches(conductor, meta, asked)        # the conversation's waiting list, seeded below
    for flag in ("message", "message-file", "tag", "on-end"):
        if asked[flag] is not None:
            refuse(f"flag-unsupported -- `--{flag}` has no meaning under chat: the messages are the lines of stdin, "
                   "a tag and an on-end belong to one wake-up.")
    for flag in ("dry-run", "new", "detached"):
        if asked[flag]:
            refuse(f"flag-unsupported -- `--{flag}` has no meaning under chat: a dry run is `run --dry-run`, "
                   "the first message opens the run.")
    persistence = conductor.persistence
    key = asked["run"]
    opening = key is None
    if asked["door"] is not None and not opening:
        refuse("door-on-resume -- a door opens a run's FIRST exchange; a resume continues the conversation.")
    if not opening and persistence.slot_of(meta, key).is_file():
        documents_judged(conductor, meta, key, documents_asked(root, asked))
    lock = locks(conductor)
    house_judged(conductor, meta, name, key, asked)
    asked = resumed_of(conductor, root, name, key, asked)   # a resume keeps what the run was
    head, provider = provider_of(conductor, root, asked)   # judged before any message is read
    refused = unmeasured(conductor, root, asked, policy_of(conductor, asked))
    if refused is not None:
        refuse(refused)
    heartbeat_of(asked)
    launches_of(asked)
    lease = None
    if not opening:
        if not persistence.slot_of(meta, key).is_file():
            refuse(f"run-unknown -- no run `{key}` at {meta}.")
        resumable(conductor, root, meta, name, key, provider)
        lease = lock.try_(launch_of(meta, key))
        if lease is None:
            refuse(f"run-busy -- a wake-up plays run {key}: one wake-up at a time on a run.")
        sent = [one for one in lines_of(record(root, MESSAGES)) if one.get("to") == name and one.get("run") == key]
        held_mark(lease, str(sent[-1].get("message") or "") if sent else "")
    waiting = seeded(conductor, meta, key, switches)
    if asked["json"]:
        return flowing(conductor, root, name, meta, asked, key, lease, lock, waiting)
    before = replayer(conductor, root, meta, waiting)
    try:
        for message in typed(sys.stdin):
            issue = exchange(conductor, root, name, meta, asked, key, message, lease, before=before)
            key, lease = issue["key"], issue["lease"]
            flow_closed(issue, issue["reason"] if issue["kept"] is None else reason_of(conductor, meta, key, issue))
            if issue["kept"] is None:              # nothing kept: said, the run standing for the next message
                print(f"pp-agent: {issue['reason']}", file=sys.stderr)
                sys.stderr.flush()
                continue
            rendered(issue["kept"], issue["done"]["session"], issue["said"], False)
            sys.stdout.flush()
            print(verdict(name, key, issue), file=sys.stderr)
            reason = reason_of(conductor, meta, key, issue)
            if reason is not None:
                print(f"pp-agent: {reason}", file=sys.stderr)
            sys.stderr.flush()
    except KeyboardInterrupt:                      # while waiting for a message: the conversation closes
        pass
    finally:
        if lease is not None:
            lock.release(lease)
    return 0


def cap_of(conductor, meta: Path) -> dict:
    """-> the cap the run's outputs are cut under: `set` the agent's `max_harness_tool_output`,
    `applied` what the engine serves this run -- the house conducts it, so the floor of a
    principal's cap holds (`settings.served_cap`, the engine's one rule)."""
    face = conductor.settings
    cap = face.of(meta).harness_cap
    return {"set": cap, "applied": face.served_cap(cap, True)}


def packages_of(conductor, meta: Path, key: str | None) -> list[dict]:
    """-> the packages the agent's instance pins beyond its base, each `{name, on}` as the run
    plays it: the switches of SETTINGS and of the run, their dependents with them -- read on the
    engine's faces, the run's slot set into the play for the reading and taken out after; without
    a run, as the switches of SETTINGS alone say them."""
    instance, persistence = conductor.instance, conductor.persistence
    instance.play_off(meta, persistence.off_of(persistence.slot_of(meta, key)) if key is not None else ())
    try:
        off = instance.switched_off(meta)
    finally:
        instance.play_off(meta, ())
    base = instance.base_of(meta)
    return [{"name": name, "on": name not in off} for name in instance.pins(meta) if name != base]


def ready_of(conductor, root: Path, name: str, meta: Path, asked: dict, key: str | None) -> dict:
    """-> what a conversation's flow says of its run before any message (`ready`): the agent, whether
    the run is taken up, the provider, the policy, the packages and the cap -- read by the functions
    `opened` reads them with -- the run's budget under a cap, whether the next exchanges are conducted, the switches waiting
    (`pending`, none at the start of a conversation) and the root of documents (`documents`: the
    run's under `--run`, the one `--documents` names at an opening, None without). The run itself is
    the event's `run`: its key under `--run`, none at an opening."""
    persistence = conductor.persistence
    documents = (persistence.documents_of(persistence.slot_of(meta, key)) if key is not None
                 else documents_asked(root, asked)) or None
    policy = policy_of(conductor, asked)
    return {"agent": name, "resumed": key is not None, "provider": provider_named(conductor, root, asked),
            "policy": policy, "packages": packages_of(conductor, meta, key),
            "cap": cap_of(conductor, meta), "budget": budget_of(policy, spent_of(root, name, key)),
            "conducted": asked.get("conduct") is not False, "pending": [], "documents": documents}


def refused_switch(played: subprocess.CompletedProcess) -> tuple[str, str]:
    """-> (code, detail) of a switch the engine refused: its `REFUSED — <code> — <detail>` line read."""
    parts = refusal_of(played).split(" — ")
    if parts[0] == "REFUSED" and len(parts) > 1:
        return parts[1].strip(), " — ".join(parts[2:]).strip()
    return refusal_of(played), ""


def played_on(packages: list[dict], name: str) -> bool | None:
    """-> whether `name` plays among `packages` (`packages_of`), None when it is not pinned there."""
    return next((one["on"] for one in packages if one.get("name") == name), None)


def switch_tried(conductor, root: Path, meta: Path, key: str, name: str, on: bool, line: str, waiting: dict, say) -> None:
    """One switch of the conversation's WAITING LIST played on the run under the mark: accepted, it
    leaves the list and `package` says it applied (`pending: false`, the packages now); refused because
    the package holds the run's view (`package-in-flight`), it stays and waits for the next launch, said
    by nobody; refused for any other cause, it leaves the list and `refused` says the engine's code and
    detail."""
    played = conducted(conductor, root, meta, key, "-enable" if on else "-disable", name)
    if played.returncode == 0:
        waiting.pop(name, None)
        say(key, f"package {name} {'on' if on else 'off'}", "package",
            {"name": name, "on": on, "pending": False, "packages": packages_of(conductor, meta, key)})
        return
    code, detail = refused_switch(played)
    if code == "package-in-flight":
        return
    waiting.pop(name, None)
    say(key, f"refused {code}", "refused", {"code": code, "line": line, "detail": detail})


def switched(conductor, root: Path, meta: Path, asked: dict, key: str | None, item: tuple, say,
             waiting: dict) -> None:
    """`conduct` and `package`, the principal's words on a conversation's run. `conduct` says whether
    the next exchanges are conducted (`asked["conduct"]`; `run-missing` before the run is opened).
    `package` asks a package in or out of the run's play: the state the run plays already -> the
    waiting for that name drops, `package` says it (`pending: false`); no run yet -> it WAITS in the
    conversation's list (`waiting`, `{name: (on, line)}`), `package` says it (`pending: true`), and the
    first launch after the opening plays it; a run -> the engine's `-disable`/`-enable` under the mark
    at once: applied (`pending: false`), or held by the run's view (`package-in-flight`) -> it waits
    for the next launch (`pending: true`), or refused for another cause -> `refused` with the
    engine's code and detail. The list lives in this process alone: closing the conversation drops it."""
    line = item[-1]
    if item[0] == "conduct":
        if key is None:
            say("", "", "refused", {"code": "run-missing", "line": line})
            return
        asked["conduct"] = item[1]
        say(key, "", "conduct", {"on": item[1]})
        return
    name, on = item[1], item[2]
    packages = packages_of(conductor, meta, key)
    if played_on(packages, name) is on:            # already so: nothing to wait for
        waiting.pop(name, None)
        say(key or "", "", "package", {"name": name, "on": on, "pending": False, "packages": packages})
        return
    waiting[name] = (on, line)
    if key is not None:
        switch_tried(conductor, root, meta, key, name, on, line, waiting, say)
        if name not in waiting:
            return
    say(key or "", "", "package", {"name": name, "on": on, "pending": True, "packages": packages})


def replayer(conductor, root: Path, meta: Path, waiting: dict, say=None):
    """-> the hook handed to `exchange`: before every launch, the switches waiting are played on the run
    in the order they came, each by `switch_tried`, said by `say` -- a conversation's flow --, else by the
    exchange's own (`told`: on stderr and kept in the run's flow, a wake-up's `--package`)."""
    def before(key: str, told=None) -> None:
        for name, (on, line) in list(waiting.items()):
            switch_tried(conductor, root, meta, key, name, on, line, waiting, say or told)
    return before


def asked_switches(conductor, meta: Path, asked: dict) -> list[tuple[str, bool, str]]:
    """-> the `--package <name>=on|off` of a launch as (name, on, value), judged before anything is opened
    or written, against the packages the agent's instance pins: `package-invalid` (not the form),
    `package-base` (the instance's base), `package-unpinned` (a name it does not pin)."""
    found = []
    base = conductor.instance.base_of(meta)
    pinned = {one["name"] for one in packages_of(conductor, meta, None)}
    for value in asked.get("package") or []:
        name, _, state = str(value).partition("=")
        if not name or state not in ("on", "off"):
            refuse(f"package-invalid -- `--package {value}`: the form is <name>=on or <name>=off.")
        if name == base:
            refuse(f"package-base -- `{name}` is the instance's base: it always plays.")
        if name not in pinned:
            refuse(f"package-unpinned -- `{name}` is not pinned by {meta}: the packages it pins are "
                   f"{', '.join(sorted(pinned)) or 'none'}.")
        found.append((name, state == "on", str(value)))
    return found


def seeded(conductor, meta: Path, key: str | None, switches: list) -> dict:
    """-> the waiting list a launch's `--package` starts with, `{name: (on, value)}`: each switch the run (or,
    before it, the instance's SETTINGS) does not play already, in the order given -- the last word on a name wins."""
    packages = packages_of(conductor, meta, key)
    waiting: dict = {}
    for name, on, value in switches:
        waiting.pop(name, None)
        if played_on(packages, name) is not on:
            waiting[name] = (on, value)
    return waiting


def flowing(conductor, root: Path, name: str, meta: Path, asked: dict, key: str | None, lease, lock,
            waiting: dict | None = None) -> int:
    """The conversation as a FLOW (`chat --json`): `ready` first, the run as judged before any message
    (`ready_of`), then `waiting`; the commands read by `commanded`, each `message`
    one `exchange` whose steps and voices `event_sayer` says on stdout; after it, `response` (the
    record's line plus `session` and `state`) when one was kept, `verdict` (the verdict as data,
    its `reason` when the exchange did not end well), then `waiting`; a `set` that holds is said by
    `policy` (the provider and the policy of the next launch), one that does not by `refused`;
    `conduct` and `package` are played by `switched`, a switch the run cannot take yet waiting in the
    conversation's list until a launch plays it (`replayer`); a bad command is `refused` and the flow goes on; `quit`, the end of stdin or a SIGINT while waiting closes it: `closed`,
    the lock released, exit 0."""
    import threading
    say = event_sayer(sys.stdout)
    busy = threading.Event()
    waiting = {} if waiting is None else waiting   # the switches asked and not yet played: {name: (on, line)}
    before = replayer(conductor, root, meta, waiting, say)
    try:
        ready = ready_of(conductor, root, name, meta, asked, key)
        ready["pending"] = [{"name": one, "on": on} for one, (on, _) in waiting.items()]   # `--package`, seeded
        say(key or "", "", "ready", ready)
        say(key or "", "", "waiting", {})
        for item in commanded(sys.stdin, busy):
            if item[0] == "refused":
                say(key or "", "", "refused", {"code": item[1], "line": item[2]})
                continue
            if item[0] in ("conduct", "package"):
                switched(conductor, root, meta, asked, key, item, say, waiting)
                continue
            if item[0] == "set":
                code = set_policy(conductor, root, asked, item[1])
                if code is not None:
                    say(key or "", "", "refused", {"code": code, "line": item[2]})
                else:
                    say(key or "", "", "policy", {"provider": provider_named(conductor, root, asked),
                                                  "policy": policy_of(conductor, asked)})
                continue
            busy.set()
            try:
                issue = exchange(conductor, root, name, meta, asked, key, item[1], lease, say=say, before=before)
            finally:
                busy.clear()
            key, lease = issue["key"], issue["lease"]
            told = issue.get("say") or say             # the exchange's keeper: kept in the flow, and said
            if issue["kept"] is not None:
                told(key, "", "response", {**issue["kept"], "session": issue["done"]["session"], "state": issue["said"]})
                reason = reason_of(conductor, meta, key, issue)
            else:
                reason = issue["reason"]
            told(key, "", "verdict", verdict_of(issue, reason))
            say(key, "", "waiting", {})
    except KeyboardInterrupt:                      # while waiting for a command: the conversation closes
        pass
    finally:
        if lease is not None:
            lock.release(lease)
        say(key or "", "", "closed", {})
    return 0


def start(rest: list[str]) -> int:
    """`agent start`: the wake-up DETACHED -- the child is `run … --detached`, the process
    that lives with the harness and holds the wake lock; it reports `{key, pid}` on its
    stdout once the lock is held, and the parent prints that line and returns. A refusal
    the child says before its report reaches the parent on stderr and is relayed."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    asked = flags(rest[1:])                        # judged here too: the usage says itself once
    for flag in ("json", "dry-run"):
        if asked[flag]:
            refuse(f"flag-unsupported -- `--{flag}` has no meaning under start: the report is JSON already, "
                   "a dry run is `run --dry-run`.")
    argv = [sys.executable, str(Path(__file__).resolve()), "run", *rest, "--detached"]
    apart = {"start_new_session": True} if os.name != "nt" else {
        "creationflags": getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
    child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             cwd=os.getcwd(), env=dict(os.environ), **apart)
    assert child.stdout is not None and child.stderr is not None
    import threading
    box: dict = {}

    def reading() -> None:
        box["line"] = child.stdout.readline()

    reader = threading.Thread(target=reading, daemon=True)
    reader.start()
    reader.join(REPORT_WAIT)
    line = str(box.get("line", "")).strip()
    if not line:
        if child.poll() is None:                   # no report in time: the child is not ours to keep
            child.kill()
        said = child.stderr.read().strip() if reader.is_alive() is False else ""
        refuse(said.removeprefix("pp-agent: ") if said else
               f"start-timeout -- the wake-up reported nothing in {REPORT_WAIT}s")
    try:
        report = json.loads(line)
    except ValueError:
        refuse(f"start-garbled -- the wake-up reported `{line[:80]}`")
    print(json.dumps({"key": report.get("key"), "pid": report.get("pid")}))
    return 0


def outcome(conductor, root: Path, name: str, meta: Path, key: str, lock) -> int:
    """Renders the last response of the run `key` as `run` does, when the last launch left
    one: the text on stdout, the verdict on stderr, 0 when the run parked with a response;
    `wake-dead` when the launch ended without a response (the wake log's tail said)."""
    persistence = conductor.persistence
    mark = mark_of(lock, meta, key)
    answered = answered_by(root, name, key)
    launched = mark.get("responses")
    if isinstance(launched, int) and len(answered) <= launched:
        log = wake_log_of(lock, meta, key)
        tail = log.read_text(encoding="utf-8").strip().splitlines()[-5:] if log.is_file() else []
        for one in tail:
            print(f"  {one}", file=sys.stderr)
        refuse(f"wake-dead -- the wake-up of run {key} ended without a response.")
    if not answered:
        refuse(f"result-missing -- run {key} has no response recorded.")
    kept = answered[-1]
    slot = persistence.slot_of(meta, key)
    state, stack = standing_of(conductor, meta, key) if slot.is_file() else ("standing", "")
    exchanges = persistence.turns_of(slot) if slot.is_file() else 0
    session = (session_of_run(root, name, key) or {}).get("session", "")
    arrived = kept.get("harness_rc") == 0 and state == "parked" and kept.get("response") is not None
    said = "parked" if arrived else ("stopped" if kept.get("harness_rc") else "standing")
    rendered(kept, str(session), said, False)
    sys.stdout.flush()
    cost, launches = kept.get("cost_usd"), kept.get("launches")
    print(f"pp-agent: {name} · run {key} · exchange {exchanges} · {said} · harness rc {kept.get('harness_rc')}"
          + (f" · {cost:g} USD" if isinstance(cost, float) else "")
          + (f" · {launches} launch(es)" if isinstance(launches, int) else ""), file=sys.stderr)
    return 0 if arrived else 2


def keyed(rest: list[str]) -> tuple[str, str, list[str]]:
    """-> (path, key, the rest) of `wait` and `result`: the agent's path then the run's key."""
    if len(rest) < 2 or rest[0].startswith("--") or rest[1].startswith("--"):
        refuse(USAGE)
    return rest[0], rest[1], rest[2:]


def wait(rest: list[str]) -> int:
    """`agent wait <path> <key> [--timeout <seconds>]`: waits for the run's wake lock to be
    free -- looked at, never taken -- then renders the outcome; `wait-timeout` past the bound."""
    root, conductor = house()
    name, key, rest = keyed(rest)
    name, meta, _ = named_agent(root, conductor, [name])
    bound = None
    if rest[:1] == ["--timeout"] and len(rest) == 2:
        try:
            bound = float(rest[1])
        except ValueError:
            refuse(f"`{rest[1]}` is not a number of seconds.")
    elif rest:
        refuse(USAGE)
    lock = locks(conductor)
    deadline = None if bound is None else time.monotonic() + bound
    while lock.held(launch_of(meta, key)):
        if deadline is not None and time.monotonic() >= deadline:
            refuse(f"wait-timeout -- a wake-up still plays run {key} after {bound:g}s.")
        time.sleep(WAIT_INTERVAL)
    return outcome(conductor, root, name, meta, key, lock)


def result(rest: list[str]) -> int:
    """`agent result <path> <key>`: the run's last response at once -- `wake-running` while a
    wake-up plays and has not answered yet, `wake-dead` or `result-missing` otherwise."""
    root, conductor = house()
    name, key, rest = keyed(rest)
    if rest:
        refuse(USAGE)
    name, meta, _ = named_agent(root, conductor, [name])
    lock = locks(conductor)
    if lock.held(launch_of(meta, key)):
        launched = mark_of(lock, meta, key).get("responses")
        if not isinstance(launched, int) or len(answered_by(root, name, key)) <= launched:
            refuse(f"wake-running -- a wake-up plays run {key}: `agent wait {name} {key}` waits for it.")
    return outcome(conductor, root, name, meta, key, lock)


def workdirs(rest: list[str]) -> int:
    """`agent workdirs [<path>]`: one line per material, the last state of each run's --
    the branch, the repository, the commits ahead of the base (read in the clone), clean or
    dirty, pushed or not, the run's state."""
    root, conductor = house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, _, rest = named_agent(root, conductor, rest)
    if rest:
        refuse(USAGE)
    lock, persistence = locks(conductor), conductor.persistence
    latest: dict = {}
    for one in lines_of(record(root, WORKDIRS)):
        if name is None or one.get("agent") == name:
            latest[(one["agent"], one["run"])] = one
    if not latest:
        print("pp-agent: no material yet.")
        return 0
    for (agent, key), one in latest.items():
        meta = agent_at(root, conductor, agent)
        if one.get("state") == "pruned":
            print(f"{agent} · run {key} · {one['branch']} · {one['repo']} · pruned")
            continue
        clone = meta.parent / one["path"]
        if clone.is_dir():
            counted = git("rev-list", "--count", f"{str(one['base']).rsplit('@', 1)[-1]}..HEAD", cwd=clone)
            ahead = counted.stdout.strip() if counted.returncode == 0 else "?"
            tidy = "dirty" if git("status", "--porcelain", cwd=clone).stdout.strip() else "clean"
        else:
            ahead, tidy = "?", "clone gone"
        sent = "pushed" if one.get("pushed") else ("unpushed" if one.get("state") == "unpushed" else "not pushed yet")
        if lock.held(launch_of(meta, key)):
            state = "running"
        elif not persistence.slot_of(meta, key).is_file():
            state = "gone"
        else:
            state = standing_of(conductor, meta, key)[0]
        print(f"{agent} · run {key} · {one['branch']} · {one['repo']} · {ahead} ahead · {tidy} · {sent} · {state}")
    return 0


def unpushed(entry: dict, clone: Path) -> int:
    """-> the commits of a run's clone the repository has not received: 0 when the clone is gone."""
    if not clone.is_dir():
        return 0
    at_target = git("rev-parse", "--verify", "--quiet", entry["branch"], cwd=Path(entry["repo"]))
    since = at_target.stdout.strip() if at_target.returncode == 0 else str(entry["base"]).rsplit("@", 1)[-1]
    counted = git("rev-list", "--count", f"{since}..HEAD", cwd=clone)
    return int(counted.stdout.strip()) if counted.returncode == 0 and counted.stdout.strip().isdigit() else 0


def prune(rest: list[str]) -> int:
    """`agent prune <path> <key> [--force]`: removes the run's clone -- `run-busy` while a
    wake-up plays the run, `workdir-unpushed` over commits the repository has not received
    (`--force` removes them), `workdir-unknown` without a material on record; `pruned` written."""
    root, conductor = house()
    name, key, rest = keyed(rest)
    force = rest == ["--force"]
    if rest and not force:
        refuse(USAGE)
    name, meta, _ = named_agent(root, conductor, [name])
    entry = workdir_of(root, name, key)
    if entry is None or entry.get("state") == "pruned":
        refuse(f"workdir-unknown -- run {key} of {name} has no material on record.")
    lock = locks(conductor)
    if lock.held(launch_of(meta, key)):
        refuse(f"run-busy -- a wake-up plays run {key}: prune its material once it is over.")
    clone = meta.parent / entry["path"]
    ahead = unpushed(entry, clone) if not force else 0
    if ahead:
        refuse(f"workdir-unpushed -- {ahead} commit(s) of {entry['branch']} were not sent to {entry['repo']}: "
               "`--force` removes them.")
    shutil.rmtree(clone, ignore_errors=True)
    line = {**entry, "at": now(), "state": "pruned"}
    append(record(root, WORKDIRS), line)
    print(f"pp-agent: {name} · run {key} · {entry['path']} removed")
    return 0


PURGED = (RESPONSES, MESSAGES, SESSIONS, NAMES, WORKDIRS)   # the records a run of an agent leaves lines in


def of_run(one: dict, name: str, key: str) -> bool:
    """Whether a record's line belongs to the run `key` of the agent `name` (`to` names it on `messages`)."""
    return one.get("run") == key and (one.get("agent") == name or one.get("to") == name)


def rewritten_without(path: Path, name: str, key_set: set) -> None:
    """Rewrites a record WITHOUT the lines of the runs `key_set` of the agent `name`, under the record's
    lock: a temporary beside it, then one rename -- every other line kept to the byte. The one write of a
    record that is not an append: `purge` alone plays it."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    if not path.is_file():
        return
    with core(__file__).record.held(path):
        kept = []
        for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
            try:
                one = json.loads(line)
            except ValueError:
                kept.append(line)
                continue
            if not (isinstance(one, dict) and one.get("run") in key_set
                    and (one.get("agent") == name or one.get("to") == name)):
                kept.append(line)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.purge")
        temporary.write_text("".join(kept), encoding="utf-8")
        os.replace(temporary, path)


def flow(rest: list[str]) -> int:
    """`agent flow <path> <key> [--exchange <n>] [--json]`: the flow the run's exchanges kept -- under `--json`
    each line as it was kept, the very object `chat --json` said; otherwise one line per event: the hour, the
    exchange, the kind (a step by its event), the first line of its text. `--exchange <n>` keeps the events of
    the n-th exchange, from its `opened` on. `run-unknown` for a key no run wears; a run older than the
    keeper has no flow: nothing printed."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    wanted = None
    if "--exchange" in rest:
        at = rest.index("--exchange")
        value = rest[at + 1] if at + 1 < len(rest) else ""
        if not value.isdigit() or int(value) < 1:
            refuse(USAGE)
        wanted = int(value)
        del rest[at:at + 2]
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    path = flow_of(root, name, key)
    if not path.is_file() and not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    current = None
    for event in lines_of(path):
        if event.get("kind") == "opened":
            current = event.get("exchange")
        if wanted is not None and current != wanted:
            continue
        if as_json:
            print(json.dumps(event, ensure_ascii=False))
            continue
        kind = event.get("event") if event.get("kind") == "step" else event.get("kind")
        text = event.get("text") or event.get("response") or event.get("title") or event.get("reason") or ""
        print(f"{str(event.get('at', ''))[11:19]}  #{current or '-'}  {kind}  {harmless(first_line(str(text)))}".rstrip())
    return 0


def engine_purge_of(conductor):
    """-> the engine's `state.purge` module, `purge-unsupported` before beta.66."""
    try:
        import importlib
        return importlib.import_module(f"{conductor.__name__}.state.purge")
    except ImportError:
        refuse("purge-unsupported -- the house's engine predates `./pp -purge` (beta.66): `./pp upgrade` first.")


def weights_of(conductor, root: Path, name: str, meta: Path, keys: list[str]) -> dict:
    """-> {key: {lines, files, bytes, flow}}: what a purge of each run would count -- the lines of the five
    records that carry it, the files the engine keeps of it (`state.purge.files_of`: `session-<key>.*` and
    the traces of its key, the table of the traces' keys read once), their bytes, and the bytes of its flow
    file (`null` without one). Reads only."""
    engine_purge = engine_purge_of(conductor)
    found = {record_name: lines_of(record(root, record_name)) for record_name in PURGED}
    state = meta / conductor.persistence.DIRECTORY
    keyed = engine_purge.traces.keys_of(state) if state.is_dir() else {}
    weights = {}
    for key in keys:
        own = set(state.glob(f"session-{key}.*")) if state.is_dir() else set()
        own |= {state / trace for trace, run in keyed.items() if run == key}
        files = [path for path in own if path.is_file()]
        kept_flow = flow_of(root, name, key)
        weights[key] = {"lines": sum(1 for lines in found.values() for one in lines if of_run(one, name, key)),
                        "files": len(files), "bytes": sum(path.stat().st_size for path in files),
                        "flow": kept_flow.stat().st_size if kept_flow.is_file() else None}
    return weights


def weight_sum(weights: list[dict]) -> dict:
    """-> the sum of runs' weights; `flow` null when none of them keeps a flow."""
    flows = [one["flow"] for one in weights if one["flow"] is not None]
    return {"lines": sum(one["lines"] for one in weights), "files": sum(one["files"] for one in weights),
            "bytes": sum(one["bytes"] for one in weights), "flow": sum(flows) if flows else None}


def held_by_guardian(conductor, root: Path, name: str, keys: list[str]) -> None:
    """Asks the engine, before any removal, whether the family's guardian keeps one of the runs
    (`events.guarded` on `agent-run:<path>/<key>`): a package that declares itself the guardian of the
    family answers -- this one names none. A no refuses `run-held` with the guardian's reason, nothing
    removed; no guardian declared, nothing plays."""
    for key in keys:
        try:
            conductor.events.guarded(root, f"{FAMILY}:{name}/{key}")
        except conductor.Refusal as refusal:
            refuse(f"run-held -- {str(refusal).split(' — ', 1)[-1]}; nothing removed.")


def verify(rest: list[str]) -> int:
    """`pp-agent verify` (the vector on stdin): the VERIFIER of the family `agent-run:<path>/<key>`, the
    engine's call -- rc 0 when the house or the agent keeps something of the run (a line of the records,
    a file of the engine, its flow), `run-unknown` otherwise; a family this package does not declare is not
    its to judge (`family-foreign`). Reads only."""
    if rest:
        refuse(USAGE)
    root, conductor = house()
    prefix, _, ident = sys.stdin.read().strip().partition(":")
    if prefix != FAMILY:
        refuse(f"family-foreign -- `{prefix}:` is not a family agent declares ({FAMILY}); its owner verifies it.")
    path, _, key = ident.rpartition("/")
    if not path or not key:
        refuse(f"run-unknown -- `{ident}`: a run is named `<path>/<key>`.")
    name, meta, _ = named_agent(root, conductor, [path])
    weight = weights_of(conductor, root, name, meta, [key])[key]
    if not (weight["lines"] or weight["files"] or weight["flow"] is not None):
        refuse(f"run-unknown -- no run `{key}` of {name}.")
    return 0


def purge(rest: list[str]) -> int:
    """`agent purge <path> (<key> … | --before <YYYY-MM-DD>) [--yes] [--force] [--json]`: removes for good
    what the house keeps of runs of the agent -- their lines in the five records, their clone -- then has
    the engine remove what the agent keeps of them, `./pp -purge` played on the agent's instance: each
    record by its writer. Without `--yes` it says what it would remove and writes nothing. All or nothing:
    a run whose wake lock is held refuses `run-busy`, a clone with unsent commits `workdir-unpushed`
    (`--force` removes them), the engine's `call-busy` is relayed -- and nothing is removed anywhere."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    confirmed, force = "--yes" in rest, "--force" in rest
    rest = [one for one in rest if one not in ("--yes", "--force")]
    engine_purge = engine_purge_of(conductor)
    before = None
    if "--before" in rest:
        at = rest.index("--before")
        value = rest[at + 1] if at + 1 < len(rest) else ""
        try:
            before = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            refuse(f"purge-invalid -- `--before {value}`: a date is written YYYY-MM-DD.")
        del rest[at:at + 2]
    if (before is None) == (not rest) or any(one.startswith("-") for one in rest):
        refuse(USAGE)
    lines = {record_name: lines_of(record(root, record_name)) for record_name in PURGED}
    recorded = {one.get("run") for found in lines.values() for one in found
                if one.get("agent") == name or one.get("to") == name}
    persistence = conductor.persistence
    if before is None:
        keys = list(dict.fromkeys(rest))
        unknown = [key for key in keys if key not in recorded and not engine_purge.files_of(meta, key)
                   and not flow_of(root, name, key).is_file()]
        if unknown:
            refuse(f"run-unknown -- `{' '.join(unknown)}`: no run of {name} wears that key; nothing removed.")
        for key in keys:
            house_judged(conductor, meta, name, key, {})
    else:
        candidates = sorted((recorded | set(engine_purge.known(meta))) - {None})
        if name == HOUSE:                                  # the house's own: its runs of the post alone
            candidates = [key for key in candidates if key in recorded or
                          (persistence.slot_of(meta, key).is_file()
                           and persistence.mode_of(persistence.slot_of(meta, key)) == persistence.PRINCIPAL)]
        keys = []
        for key in candidates:
            ats = [one.get("at") for found in lines.values() for one in found if of_run(one, name, key) and one.get("at")]
            last = max((datetime.fromisoformat(at) for at in ats), default=None)
            written = engine_purge.last_write(engine_purge.files_of(meta, key))
            newest = max((one for one in (last, written) if one is not None), default=None)
            if newest is not None and newest < before:
                keys.append(key)
    held_by_guardian(conductor, root, name, keys)         # all or nothing: the family's guardian first
    lock = locks(conductor)
    leases = []
    try:
        for key in keys:                                   # all or nothing: every wake lock first
            wake = launch_of(meta, key)
            if not confirmed or not wake.exists():
                taken = lock.held(wake)
            else:
                lease = lock.try_(wake)
                taken = lease is None
                if lease is not None:
                    leases.append(lease)
            if taken:
                refuse(f"run-busy -- a wake-up or a conversation holds run {key} of {name}: nothing removed; "
                       "purge it once it is over.")
        runs = []
        for key in keys:
            entry = workdir_of(root, name, key)
            clone = meta.parent / entry["path"] if entry and entry.get("state") != "pruned" else None
            if confirmed and clone is not None and not force:
                ahead = unpushed(entry, clone)
                if ahead:
                    refuse(f"workdir-unpushed -- {ahead} commit(s) of {entry['branch']} were not sent to "
                           f"{entry['repo']}: `--force` removes them; nothing removed.")
            kept_flow = flow_of(root, name, key)
            runs.append({"key": key, "lines": {record_name: sum(1 for one in found if of_run(one, name, key))
                                               for record_name, found in lines.items()},
                         "files": [], "bytes": 0,
                         "workdir": entry["path"] if clone is not None and clone.is_dir() else None,
                         "flow": kept_flow.stat().st_size if kept_flow.is_file() else None})
        held_keys = [one["key"] for one in runs if engine_purge.files_of(meta, one["key"])]
        if held_keys:                                      # the agent first: its engine removes, or nothing does
            played = subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta),
                                     "-purge", *held_keys, "-json"] + (["--yes"] if confirmed else []),
                                    capture_output=True, text=True, cwd=root.parent)
            if played.returncode != 0:
                refuse(f"{first_line(played.stderr).removeprefix('pp: REFUSED — ').strip()} -- the engine of {name} "
                       "refused; nothing removed.")
            told = json.loads(played.stdout)
            for one in told.get("runs") or []:
                for run_entry in runs:
                    if run_entry["key"] == one.get("key"):
                        run_entry["files"], run_entry["bytes"] = list(one.get("files") or []), int(one.get("bytes") or 0)
        if confirmed:
            for record_name in PURGED:
                rewritten_without(record(root, record_name), name, set(keys))
            for run_entry in runs:
                if run_entry["workdir"]:
                    shutil.rmtree(meta.parent / run_entry["workdir"], ignore_errors=True)
                flow_of(root, name, run_entry["key"]).unlink(missing_ok=True)
    finally:
        for lease in leases:
            lock.release(lease)
    totals = {"lines": sum(sum(one["lines"].values()) for one in runs),
              "files": sum(len(one["files"]) for one in runs), "bytes": sum(one["bytes"] for one in runs)}
    if as_json:
        print(json.dumps({"dry": not confirmed, "agent": name, "runs": runs, **totals}, ensure_ascii=False))
        return 0
    verb = "purged" if confirmed else "would purge"
    print(f"pp-agent: {name} · {verb} {len(runs)} run(s) -- {totals['lines']} line(s), {totals['files']} file(s), "
          f"{totals['bytes']} bytes")
    for one in runs:
        counted = ", ".join(f"{record_name.removesuffix('.jsonl')} {n}" for record_name, n in one["lines"].items() if n)
        print(f"  run {one['key']} · lines {counted or 'none'} · {len(one['files'])} file(s), {one['bytes']} bytes"
              + (f" · material {one['workdir']}" if one["workdir"] else "")
              + (f" · flow {one['flow']} bytes" if one["flow"] is not None else ""))
    return 0


# --- the readings ---------------------------------------------------------------------------

def last_of(rest: list[str]) -> tuple[str | None, int]:
    """-> (the agent named, or None; the count `--last n`, default 1)."""
    name, count = None, 1
    if rest and not rest[0].startswith("--"):
        name, rest = rest[0], rest[1:]
    if rest[:1] == ["--last"] and len(rest) == 2:
        try:
            count = int(rest[1])
        except ValueError:
            refuse(f"`{rest[1]}` is not a number.")
        if count < 1:
            refuse("`--last` wants at least 1.")
    elif rest:
        refuse(USAGE)
    return name, count


def listing(rest: list[str]) -> int:
    root, conductor = house()
    as_json, rest = json_flag(rest)
    if rest:
        refuse(USAGE)
    found = agents_of(root, conductor)
    if not found and not as_json:
        print(f"pp-agent: no agent under {root.parent} yet -- `./pp agent add <path>` creates one.")
        return 0
    responses = lines_of(record(root, RESPONSES))
    lock = locks(conductor)
    for name, meta in ([(HOUSE, root)] if as_json else []) + found:   # the house heads the face, never the text
        slots = faced_slots(conductor, meta, name)
        running = len(under_way(lock, conductor.persistence, meta))
        answered = len([one for one in responses if one.get("agent") == name])
        if as_json:
            keys = [conductor.persistence.run_id_of(slot) for slot in slots]
            weight = weight_sum(list(weights_of(conductor, root, name, meta, keys).values()))
            print(json.dumps({"agent": name, "runs": len(slots), "running": running, "responses": answered,
                              "weight": weight}))
            continue
        print(f"{name} · {len(slots)} run(s) · {running} running · {answered} response(s)")
    return 0


def last_policy(root: Path, name: str, sent: list[dict]) -> dict | None:
    """-> what the agent's last run played: `{provider, policy}` -- the provider of its last session
    (`harness` for a caller's command) and the policy of its last message, all runs taken together;
    None when no message was ever sent to it."""
    if not sent:
        return None
    sessions = [one for one in lines_of(record(root, SESSIONS)) if one.get("agent") == name]
    provider = (sessions[-1].get("provider") or "harness") if sessions else None
    return {"provider": provider, "policy": dict(sent[-1].get("policy") or {})}


def providers(rest: list[str]) -> int:
    """`agent providers [--json]`: each provider the house is wired with, what its adapter SPELLS
    of a policy, the MODELS it names and the scope of the COST it reads -- read from the adapter
    itself (`SPELLS`, `MODELS`, `COST` of its `wire.py`, loaded by the engine's face); one line each,
    or one object `{provider, spells, models, cost}` under `--json`; nothing when the house is wired
    with none."""
    root, conductor = house()
    as_json, rest = json_flag(rest)
    if rest:
        refuse(USAGE)
    for provider in conductor.install.wired_providers(root.parent):
        try:
            wire = conductor.adapters.load(provider, root)
        except conductor.Refusal as refusal:
            refuse(str(refusal))
        spells, models = list(getattr(wire, "SPELLS", ())), list(getattr(wire, "MODELS", ()))
        cost = getattr(wire, "COST", None)
        if as_json:
            print(json.dumps({"provider": provider, "spells": spells, "models": models, "cost": cost}))
            continue
        print(f"{provider} · spells {', '.join(spells) or '—'} · models {', '.join(models) or '—'} · cost {cost or '—'}")
    return 0


def status(rest: list[str]) -> int:
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    if rest:
        refuse(USAGE)
    persistence, lock = conductor.persistence, locks(conductor)
    slots = faced_slots(conductor, meta, name)
    if not slots and not as_json:
        print(f"pp-agent: {name} -- no run yet.")

    def dead(key: str) -> bool:
        """The last launch of `key` is over and added no response: its mark says how many stood."""
        launched = mark_of(lock, meta, key).get("responses")
        return isinstance(launched, int) and len(answered_by(root, name, key)) <= launched

    sent = [one for one in lines_of(record(root, MESSAGES)) if one.get("to") == name]

    def policy_of_run(key: str) -> dict:
        """-> the policy of the run's last message, `{}` when none was sent."""
        found = [one for one in sent if one.get("run") == key]
        return dict(found[-1].get("policy") or {}) if found else {}

    windows: dict = {}                             # the adapters' windows, loaded once per provider
    state_dir = meta / persistence.DIRECTORY
    standing = {persistence.run_id_of(one) for one in persistence.slots(meta)}
    lone = [path.name.removeprefix("session-").split(".", 1)[0]
            for path in (sorted(state_dir.glob("session-*.wake.lock")) if state_dir.is_dir() else [])]
    weights = (weights_of(conductor, root, name, meta,
                          list(dict.fromkeys([persistence.run_id_of(slot) for slot in slots] + lone)))
               if as_json else {})
    faced_keys: list[str] = []

    def faced(key: str, exchanges: int, state: str, stack: str, known: dict | None) -> None:
        """One run as the face says it: the state that prevails, the name, the records summed, its policy,
        its budget under a cap, its context reduced."""
        rows, since = counted_since(conductor, meta, key, answered_by(root, name, key))
        context = context_seen(context_of(rows, window_of(conductor, root, name, key, windows), None, since))
        print(json.dumps({"agent": name, "run": key, "name": name_of(root, name, key), "exchanges": exchanges,
                          "state": state, "stack": stack, "session": known.get("session") if known else None,
                          "provider": (known.get("provider") or "harness") if known else None,
                          **cumuls_of(root, name, key), "policy": policy_of_run(key),
                          "budget": budget_of(policy_of_run(key), spent_of(root, name, key)), "context": context,
                          "weight": weights[key]}, ensure_ascii=False))
        faced_keys.append(key)

    for slot in slots:
        key = persistence.run_id_of(slot)
        state, stack = standing_of(conductor, meta, key)
        where = "parked at FINAL" if state == "parked" else f"standing on {stack or 'its block'}"
        if lock.held(launch_of(meta, key)):    # the wake lock IS the state: a wake-up plays
            where = f"running (a wake-up plays) -- {where}"
            state = "running"
        elif dead(key):
            where = f"dead (a wake-up ended without its response) -- {where}"
            state = "dead"
        known = session_of_run(root, name, key)
        if as_json:
            faced(key, persistence.turns_of(slot), state, stack, known)
            continue
        held = (f"session {known['session']} ({known.get('provider') or 'harness'})" if known else "no session")
        print(f"run {key} · {persistence.turns_of(slot)} exchange(s) · {where} · {held}")
    for path in sorted(state_dir.glob("session-*.wake.lock")) if state_dir.is_dir() else []:
        key = path.name.removeprefix("session-").split(".", 1)[0]    # a launch whose agent opened no run
        if key in standing:
            continue
        if lock.held(path):
            if as_json:
                faced(key, 0, "running", "", None)
                continue
            print(f"run {key} · 0 exchange(s) · running (a wake-up plays, no run opened yet) · no session")
        elif dead(key):
            if as_json:
                faced(key, 0, "dead", "", None)
                continue
            print(f"run {key} · 0 exchange(s) · dead (a wake-up ended without its response) · no session")
    answered = [one for one in lines_of(record(root, RESPONSES)) if one.get("agent") == name]
    wired = conductor.install.wired_providers(root.parent)
    if as_json:
        print(json.dumps({"agent": name, "providers": list(wired), "last": last_policy(root, name, sent),
                          "weight": weight_sum([weights[key] for key in faced_keys]),
                          "packages": packages_of(conductor, meta, None)}, ensure_ascii=False))
        return 0
    print(f"{len(answered)} response(s)")
    print(f"providers: {', '.join(wired) if wired else '—'}")
    return 0


def name_run(rest: list[str]) -> int:
    """`name <path> <key> [<name>]`: the run's name, kept by this script alone at
    `names.jsonl`; without a name, the current one is said."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    if not rest or len(rest) > 2 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    if not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    if len(rest) == 1:
        current = name_of(root, name, key)
        print(f"pp-agent: {name} · run {key} · " + (f"named {current}" if current else "(no name)"))
        return 0
    wanted = rest[1].strip()
    if not wanted or len(wanted) > NAME_CHARS or not wanted.isprintable():   # a line break would split a table's row
        shown = " ".join(rest[1].split())[:40]
        refuse(f"name-invalid -- `{shown}`: a run's name is one line of 1 to {NAME_CHARS} printable characters.")
    append(record(root, NAMES), {"at": now(), "agent": name, "run": key, "name": wanted})
    print(f"pp-agent: {name} · run {key} · named {wanted}")
    return 0


def paired(sent: list[dict], answered: list[dict]) -> dict[int, dict]:
    """-> {the rank of a message (from 1): the response that answers it}. A response answers the LAST
    message of the run sent at its hour or before; two responses never take one message and both
    records keep their order -- a response that shares the second of the next message stays at its own
    message when the response after it would otherwise have none. An exchange that kept nothing leaves
    its message unanswered. Records the hour cannot order (a response older than every message) pair by
    rank."""
    hours = [str(one.get("at") or "") for one in sent]
    ranks: list[int] = []
    rank = len(sent)                               # from the last response back: below the next one's message
    for one in reversed(answered):
        hour = str(one.get("at") or "")
        rank -= 1
        while rank >= 0 and hours[rank] > hour:
            rank -= 1
        if rank < 0:
            return {number: one for number, one in enumerate(answered[:len(sent)], 1)}
        ranks.append(rank)
    return {rank + 1: one for rank, one in zip(reversed(ranks), answered)}


def exchanges(rest: list[str]) -> int:
    """`exchanges <path> <key> [--json]`: the run's history -- its messages in order, each paired with
    the response that answers it, by the hour of the two records (`paired`), `null` when none came."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    if not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    sent = [one for one in lines_of(record(root, MESSAGES)) if one.get("to") == name and one.get("run") == key]
    answered = paired(sent, answered_by(root, name, key))
    for number, message in enumerate(sent, 1):
        response = answered.get(number)
        if as_json:
            print(json.dumps({"agent": name, "run": key, "index": number, "at": message.get("at"),
                              "message": message.get("message"),
                              "response": response.get("response") if response else None,
                              "cost_usd": response.get("cost_usd") if response else None,
                              "launches": response.get("launches") if response else None,
                              "error": response.get("error") if response else None,
                              "harness_rc": response.get("harness_rc") if response else None,
                              "conducted": message.get("conducted", True) is not False},
                             ensure_ascii=False))
            continue
        said = first_line(str(message.get("message", "")))
        if response is None:
            print(f"#{number}  {message.get('at')}  {said} -> (no response)")
            continue
        cost, launches = response.get("cost_usd"), response.get("launches")
        print(f"#{number}  {message.get('at')}  {said} -> "
              + (first_line(str(response["response"])) if response.get("response") is not None else "(no response)")
              + (f" · {cost:g} USD" if isinstance(cost, (int, float)) else "")
              + (f" · {launches} launch(es)" if isinstance(launches, int) else ""))
    return 0


def stats(rest: list[str]) -> int:
    """`stats <path> <key> [--json]`: the detail of the run's conduction, as the engine's own
    `-stats <key>` renders it on the agent's instance -- relayed, never recomputed; under
    `--json` the records' sums and the run's object under `conduction`."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    if not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    played = subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta), "-stats", key]
                            + (["-json"] if as_json else []), capture_output=True, text=True, cwd=root.parent)
    if not as_json:
        sys.stdout.write(played.stdout)
        sys.stderr.write(played.stderr)
        return played.returncode
    try:
        runs = json.loads(played.stdout).get("runs") or []
    except (ValueError, AttributeError):
        refuse(f"stats-unreadable -- the engine's `-stats {key} -json` rendered no JSON: {first_line(played.stderr)}")
    slot = conductor.persistence.slot_of(meta, key)
    summed = cumuls_of(root, name, key)
    conduction = runs[0] if runs else {}
    rows, since = counted_since(conductor, meta, key, answered_by(root, name, key))
    context = context_of(rows, window_of(conductor, root, name, key), conduction.get("tokens"), since)
    print(json.dumps({"agent": name, "run": key, "cost_usd": summed["cost_usd"], "launches": summed["launches"],
                      "exchanges": conductor.persistence.turns_of(slot), "conduction": conduction,
                      "context": context}, ensure_ascii=False))
    return 0


def responses(rest: list[str]) -> int:
    root, conductor = house()
    name, count = last_of(rest)
    if name is not None:
        named_agent(root, conductor, [name])
    found = [one for one in lines_of(record(root, RESPONSES)) if name is None or one.get("agent") == name]
    if not found:
        print("pp-agent: no response recorded yet.")
        return 0
    for one in list(reversed(found))[:count]:
        cost, launches = one.get("cost_usd"), one.get("launches")
        print(f"{one['at']}  {one['agent']} · run {one['run']} · #{one['index']} · rc {one['harness_rc']}"
              + (f" · {cost:g} USD" if isinstance(cost, (int, float)) else "")
              + (f" · {launches} launch(es)" if isinstance(launches, int) else "")
              + (f" · denials {len(one['denials'])}" if one.get("denials") else ""))
        print(harmless(one["response"]) if one.get("response") is not None else "(no response)")
    return 0


def messages(rest: list[str]) -> int:
    root, conductor = house()
    name, count = last_of(rest)
    if name is not None:
        named_agent(root, conductor, [name])
    found = [one for one in lines_of(record(root, MESSAGES)) if name is None or one.get("to") == name]
    if not found:
        print("pp-agent: no message sent yet.")
        return 0
    for one in list(reversed(found))[:count]:
        print(f"{one['at']}  {one['from']} -> {one['to']} · run {one['run']} · policy {json.dumps(one['policy'])}"
              + (f" · tag {one['tag']}" if one.get("tag") is not None else "")
              + (f" · pid {one['pid']}" if one.get("pid") is not None else ""))
        print(harmless(str(one["message"])))
    return 0


def detached(rest: list[str]) -> int:
    """The child of `agent start`, `run … --detached`: it outlives the console that launched
    its parent, so it holds the machine's maintenance lock SHARED itself, for its whole life
    -- under a maintenance it refuses `maintenance-in-progress` before anything is touched."""
    root, conductor = house()
    with contextlib.ExitStack() as stack:
        try:
            stack.enter_context(locks(conductor).serving(root))
        except conductor.Refusal as refusal:
            refuse(str(refusal))
        return run(rest)


def main(argv: list[str]) -> int:
    if argv[:1] == ["run"] and "--detached" in argv[1:]:
        return detached(argv[1:])
    verbs = {"add": add, "run": run, "chat": chat, "start": start, "wait": wait, "result": result,
             "workdirs": workdirs, "prune": prune, "purge": purge, "flow": flow,
             "list": listing, "status": status, "responses": responses, "messages": messages,
             "name": name_run, "exchanges": exchanges, "stats": stats, "providers": providers, "verify": verify}
    if not argv or argv[0] not in verbs:
        refuse(USAGE)
    return verbs[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
