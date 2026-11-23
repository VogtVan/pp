#!/usr/bin/env python3
"""The house's hand over its agents: an agent is an instance anywhere under the house's
workspace that borrows the house's machine, and it IS its path -- relative to the house,
slugs joined by `/` (`ag1`, `rep1/ag1`) -- in every verb, every record, its branch and its git
identity; born and woken from here; the ONE launcher of a harness.

  pp-agent add <path> [--type member|chat]
      -> gives birth to the agent at `<path>`: the engine's install, an instance that BORROWS
         the house's machine, no door, the seed of an interactive instance, its slug the path's
         last segment, then its `max_harness_tool_output` set to 200000 through the engine's
         settings face -- the cap of one output of pp: a boot reaches the prompt in one launch --,
         said at the birth. `--type` writes a PROFILE through the same face: `member` --
         `capabilities: false`, `package.steering: off` (the boot without the table of
         capabilities nor the threads' pass, continuity as it stands); `chat` -- the member's lines, plus
         `continuity_history_day: never` (no weekly digest); a key
         the house does not know (its package not pinned) is left, and the birth names it.
         `agent-path-invalid` (a segment that is no slug, `..`, a leading `/`, an empty segment, a file
         on the path, a subtree that carries a machine of its own), `agent-exists`,
         `type-unsupported` (a type other than `member` or `chat`) -- nothing written.
  pp-agent import <path> --from <workspace>
      -> makes the instance of `<workspace>`, which carries its own machine, the agent at `<path>`:
         the engine's import moves its `.pp` under the house, takes its machine out, renews its runs
         and recomposes it as a borrower, its own files, records and traces kept; then takes out of
         `<workspace>` what pp wrote there and nobody changed, and names each file it leaves;
         `max_harness_tool_output` set as at `add`, its profile kept. The refusals of `add`, then
         `instance-missing`, `import-borrowed`, `import-version`, `import-packages`,
         `import-cross-device`, `maintenance-busy` -- nothing written.
  pp-agent run <path> (--message <text> | --message-file <path>) [--model <m>]
                      [--max-budget-usd <n>] [--permissions auto|strict|bypass]
                      [--effort low|medium|high|xhigh|max] [--launches <n>]
                      [--new | --run <key>] [--provider <name>] [--harness <command>]
                      [--work <repo> [--base <ref>]] [--door <document>] [--documents <dir>]
                      [--package <name>=on|off]... [--vector <family>:<id>]... [--json] [--quiet]
                      [--heartbeat <seconds>] [--dry-run]
      -> ONE exchange, as a message typed in a session, CONDUCTED BY THIS SCRIPT -- the run's
         principal. An opening: once everything is judged,
         this script plays `-new "<message>"` on the agent's instance as its principal
         (`--door <document>` names the run's ENTRY, carried by `PP_DOOR` on that call alone: `-new`
         opens it as a CALL above the boot; with `--run` it refuses `door-on-resume`; `--documents
         <dir>` -- absolute, or relative to the house's directory -- gives the run its ROOT of
         documents, carried by `PP_DOCUMENTS` on that call alone and kept by the engine at the run;
         under `--run` another root refuses `documents-fixed` before any launch; `--package
         <name>=on|off`, repeated, names the packages the run plays -- judged first,
         `package-invalid`, `package-base`, `package-unpinned` (a package not pinned switched on;
         switched off, it asks nothing) --, each switch the run does not play
         already played by the principal before every launch until the engine takes it, the waiting
         list of a conversation; `--vector <family>:<id>`, repeated, names what the run works on: the
         run KEEPS its vectors (`vectors.jsonl`) and this script mounts them at every exchange it
         conducts. A `--vector` given at a resume REPLACES the set the run keeps; `--vector -` empties
         it. For each vector the script is the one the family's manifest names as its verifier, read
         at the engine's face among the families the run plays. EVERY vector is verified first (the
         engine's `events.verified`: the script's `verify`, the vector on stdin). Then the exchange
         plays in three moves, the same at an opening and at a resume, every call the principal's.
         The call that carries the message (the `-new`, or the message of a resume) also carries
         `PP_HOLD_OUTPUT=true`: pp opens the exchange and renders no block. Each vector is posed by
         `-s <script> mount <id>` under the same flag: its laws and its offers are in force, what it
         serves waits at the run; the gesture names the script alone, and pp plays it when the root
         of the exchange offers it. One bare call then plays the exchange and gives the first
         prompt, rendered once: what the vectors mount stands before its first step. One
         vector refused at its verification (its form, its family, an address its verifier refuses):
         nothing is mounted, nothing kept, nothing launched. One gesture refused after every vector
         was verified (`offer-absent`, a refusal of the engine or of the script): nothing kept,
         nothing launched, but what the gestures before it mounted stays in force until the end of
         this exchange, and is not kept after it. At a resume, a vector refused at its verification
         leaves the run as it was; a gesture refused comes after the message: nothing was rendered,
         the message is on record and the run stands on the exchange it opened, for the next
         `--run <key>` to take up. At an opening a form or a family refused opens nothing, an address
         or a gesture refused leaves the run opened and never launched. Every refusal of a vector
         says ONE code,
         `vector-refused`, first on stderr and as the `code` of a `refused` event `{code, vector,
         detail}`, kept in the
         run's flow when a run stands), reads the key
         on the output's first line and holds the launcher's lock (`session-<key>.wake.lock`, this
         package's file beside the slot) from there to the records' write. Then the LOOP: the harness
         is launched in the agent's directory, in a session of its provider -- opened at the first
         launch, resumed at the next ones --, on the PROMPT: the first launch carries the message
         under `[message from your principal]`, then pp's whole output; every later launch pp's
         output alone. After each launch this script reads the run: an output HELD by the agent's
         value call, or a chunk waiting, or a block to advance -- its own bare call serves or
         advances, and the harness is launched again on what came back; a run PARKED (its passage over)
         with nothing held ends the loop: the response is composed of the words of its launches. A run the
         harness opened meanwhile (a `-new` it typed at the parked run) is a STRAY run, said on stderr
         and counted at the verdict, never forgotten. `--launches <n>` bounds the launches of one
         wake-up (24 by default, a whole number at least 1: `launches-invalid`): reached, the
         wake-up refuses `launches-spent`, its last response kept, the run left where it stands.
         `--run <key>` resumes the run: parked, the principal's `<key> "<message>"` opens the exchange
         (traced `prompt`); standing (a wake-up that died mid-loop), the loop goes on from where
         it stands and the verdict says `standing resumed`; renewed by an upgrade, the principal's call
         reopens it under its key. The harness runs with the MARBLE
         (`.sys/system.md`) and the house's wiring, its policy -- judged by the face, the
         model, the run's BUDGET CAP, the permission regime, the model's effort -- spelled by the adapter,
         the prompt on its standard input; its environment names the run (`PP_CONDUCTED_RUN`): the agent's calls are never the principal's.
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
                       [--vector <family>:<id>]... [--quiet] [--heartbeat <seconds>]
      -> a CONVERSATION at the foreground, conducted by this script: the messages are read on
         stdin, one per line (a line ending on a backslash goes on with the next, the backslash
         taken out and the line break kept; an empty line sends nothing); each message is ONE
         exchange -- the same exchange `run` plays --, of ONE run held from a message to the next
         with its session and its wake lock: the first message opens the run (`--run <key>` resumes
         one instead -- `run-unknown`, `session-missing`, `provider-mismatch`, `run-busy` judged
         before any message is read), every later message resumes it; a `run`, a `start` or any
         other wake-up on that run refuses `run-busy` while the conversation lives. `--work`,
         `--door` and `--documents` play at the opening alone (`documents-fixed` on a resume that
         names another root); `--package` seeds the conversation's waiting list before any message;
         `--vector <family>:<id>`, repeated, plays as under `run` at every exchange of the
         conversation: at an opening the vectors are verified once the first message opened the run,
         then mounted before it; at a resume they REPLACE the set the run keeps (`--vector -` empties
         it), and without the flag the kept set is mounted; a vector refused closes the conversation
         -- `vector-refused`, exit 2, nothing launched. After each exchange: the response on stdout as `run`
         prints it, the verdict line on stderr; an exchange that ends badly (`launches-spent`,
         `harness rc <c>`, the passage not over) says why on stderr and the conversation GOES ON --
         the run stands, the next message takes it up (`standing resumed`). A SIGINT during an
         exchange ends the harness (SIGTERM, SIGKILL after 5 s -- `run` too: no orphan) and the
         exchange is said `interrupted`: the words of the finished launches are kept with the error
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
      -> removes for good what the house keeps of runs of the agent -- their lines in the six
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
         agent's instance, relayed; `--json` the records' sums, the run's object under
         `conduction` and its `context` -- the context the last measured call sent the model, plus
         the flow since weighed by the adapter's constants, `estimated` when anything was added;
         `stats-unreadable` when the engine rendered no JSON
  pp-agent calibrate [<path> ...] [--json]
      -> per run of the agents named (every agent and the house without one): the context the
         provider's own store measured at its last call beside the two estimates and their gaps,
         then per provider the gaps and the constants fitted on its runs; reads only
  pp-agent responses [<path>] [--last n]  -> the n latest responses (default 1), newest first
  pp-agent messages [<path>] [--last n]   -> the n latest messages sent, newest first

The house is the instance this script belongs to. The engine launches nothing and reads no harness: this script launches, the
adapter reads (`conductor.adapters.answer` once a launch is over, `conductor.adapters.events` line by line
while it plays) -- a `--harness` command in the grammar `--provider` names beside it, never a default
(`grammar-missing`). The records are APPEND-ONLY -- `purge` alone rewrites one, without the lines of the
runs it removes, under the record's lock -- and this script is their only writer: `messages.jsonl` {at, from, to, run, message, policy},
`responses.jsonl` {at, agent, run, index, response, cost_usd, session_cost_usd, launches, denials,
error, harness_rc, flow, tokens_sent, words, model, effort} -- `flow` the voices of the exchange summed in tokens,
its `calls`, and `context` once a call was measured: what the last one sent the model; `tokens_sent` what every
measured call sent it, summed, null when the adapter measures none; `words` every words of the exchange's launches as
`{launch, text}`, the matter; `response` their composition, written once (in order, joined by a blank
line, a blank one dropped, nothing added); `model` and `effort` the policy
played; a wake-up the run's cap stopped between two launches says `error:
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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # the skill's folder: its layers
from model.words import USAGE  # noqa: E402
from store.refusal import refuse  # noqa: E402
from verbs.life import add, import_, prune, purge, remove, name_run  # noqa: E402
from verbs.read import (workdirs, flow, verify, listing, providers, status, exchanges, stats, calibrate,  # noqa: E402
                        responses, messages)
from verbs.talk import run, open_verb, close_verb, chat, start, wait, result, detached  # noqa: E402

def main(argv: list[str]) -> int:
    if argv[:1] == ["run"] and "--detached" in argv[1:]:
        return detached(argv[1:])
    entry = Path(__file__).resolve()               # the script `start` relaunches: its own
    verbs = {"add": add, "import": import_, "run": run, "chat": chat, "start": lambda rest: start(rest, entry),
             "wait": wait, "result": result,
             "workdirs": workdirs, "prune": prune, "purge": purge, "remove": remove, "flow": flow,
             "open": open_verb, "close": close_verb,
             "list": listing, "status": status, "responses": responses, "messages": messages,
             "name": name_run, "exchanges": exchanges, "stats": stats, "providers": providers, "verify": verify,
             "calibrate": calibrate}
    if not argv or argv[0] not in verbs:
        refuse(USAGE)
    return verbs[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
