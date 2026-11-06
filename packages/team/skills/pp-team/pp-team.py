#!/usr/bin/env python3
"""The house's hand over its teams: a team is DECLARED by its owner at
`<house>/teams/<name>/TEAM.md`, started, posted to, stopped, read -- and ADVANCED by ticks.
Its state is its JOURNAL, read again at every reading. This script keeps no clock: a tick is
one short process, launched by the end of a wake-up (`--on-end`), by a post, or by the team's
TIMER -- the NET under every other trigger, a process the tick arms and that dies after one tick --,
and after a restart by the team's relaunch entry in the system's scheduler, laid and removed by this
script on the owner's commands (the engine never writes the scheduler); the wake-ups a tick launches
are the house's own console's (`agent start`).

A team is made of MEMBERS: `agents: |` of `TEAM.md` declares one `<name> <path>` per line -- the
member's NAME, a slug unique in the team, then the PATH of the agent that plays it; one path may
come back, several members on one agent. The journal (its `agent` field is the member's name), the
inbox, `status` and the head of every wake-up (`[team <team> · you are <member>]`) speak names;
every call to the house -- `agent start`, a wake lock, a record of the house, a birth -- is
addressed by the member's path, read at `team-started.agents` (`{name: path}`).

  pp-team start <name> [--message <text> [--to <member>]] [--budget <usd>] [--budget-launches <n>]
                       [--provider <name>] [--harness <command>] [--model <m>]
                       [--permissions auto|strict|bypass] [--effort low|medium|high|xhigh|max] [--no-tick]
                       [--package <name>=on|off]...
                       [--member <member> [--provider|--model|--effort|--permissions <v>]
                        [--package <name>=on|off]...]...
      -> a SEASON, on a team at work too: the members' runs kept, the cost, budget-spent, budget-launches
         and each task's launches: counted afresh; `--message` optional -- without it no task opens, the
         season stands on its ceremonies and the posts to come, the relaunch entry laid only under an
         open task or a declared ceremony; the
         season's budget at `team-started.season`, the team's packages (`--package` before the first
         `--member`: every member's run, over its agent's SETTINGS) at `team-started.packages`, each
         member's profile at `team-started.profiles` -- its own `--package` covers the team's name by name
         (`participant-unknown`, `package-invalid`, `package-required`, `package-unpinned` for a package
         not pinned switched on, `package-dependency` for a package switched on whose requirement the
         season switches off, `member-held`, `budget-invalid` -- all judged before any write);
         `--max-budget-usd` refuses `flag-retired`, nothing written: a wake-up's share is computed on
         the team's `budget:` (`team budget` raises it);
         `TEAM.md` read WHOLE and judged before anything is written (`team-unknown`,
         `team-invalid`, `root-missing`, `participant-unknown`, `ceremony-cycle`,
         `entry-missing` -- an entry absent from the instance of an agent that
         plays it); the agents the house lacks born at their paths, each path once, under
         the house's birth lock for that path (`install(…, borrow=True)`: an instance that borrows
         the house's machine, no door); then the team's documents written in ITS directory,
         `teams/<name>/` -- the root of documents of every run the team opens (`agent start
         --documents`), nothing written in an agent's instance: the HEAD of `TEAM-<name>.md`, always
         (attached at the kit's `turn.begin`, `proc: SERVE` serving the document itself; with entries,
         `next:` every entry of the team then `TEAM-IDLE.md`, `decide: pp-team entry <name>`), its BODY --
         the team's intention, the owner's -- kept to the byte, `team-document-missing` without the file;
         and, with entries, the neutral `TEAM-IDLE.md` (from
         `agent-idle.md`); the law `TURN.md` an earlier version wrote there is removed and said, a
         different one is the owner's: kept and said. At each agent of the team, what an earlier
         version laid there -- `procs/TURN.md`, `procs/TEAM-IDLE.md`, `skills/team-entry/` at the
         team's bytes, `procs/TEAM-<name>.md` deciding by `team-entry <name>` -- is removed; another
         is the agent's own: kept and said;
         then, under the journal's lock, `team-started` (the launch flags kept under `launch`),
         `task T<n>` and the `do` post from the owner to `--to` or the root; then a tick, unless
         `--no-tick`.
  pp-team post <name> [--message <text>] [--to <member>] [--task <id> | --name <text>] [--reply <id>]
                      [--stop] [--as <principal>] [--no-tick]
      -> without `--task` a NEW task (`task` + its `do` post) to `--to` or the root, `--name` its name --
         one line of 1 to 80 printable characters, a user's text (`name-invalid`; at `start` too); with
         `--task` an `info` on that task -- a `reply` under `--reply <id>`, a `stop` under
         `--stop` --; `--as` a mandator or the owner (`principal-unknown`); `team-not-started`,
         `task-unknown`, `task-closed`, `message-unknown`, `message-missing`; then a tick.
  pp-team stop <name> [--task <id>] [--kill] [--no-tick]
      -> `stopped {task, by}` -- the task stops whatever holds it --, then a `stop` post to every
         member holding the task (its member unless terminal, and every delegate without a
         terminal; none when nobody holds it: `stopped -- nobody held it`), or every open task,
         delivered at once -- to a run STANDING on the task, at the head of one more launch; the posts left undelivered on it `returned`; a wake-up under way ends on its own
         and its answer is routed nowhere -- under `--kill` it is ended now by its launcher's
         process group (`wake-killed`), nothing kept, never retried.
  pp-team tick <name>                 -> ONE advance of the team (below); an on-end tick carries `PP_AGENT_RUN`
                                         and `PP_AGENT_STATE`, the end of the launch that fired it
  pp-team tick --all                  -> one advance of every team of the house that needs its net, in the order
                                         of their names -- what the house's relaunch entry plays at logon; a team
                                         that fails is said on stderr, the others advance
  pp-team follow <name> <tag>         -> the FOLLOWER of one launch: keeps `agent flow --from --follow` open on
                                         its flow, routes each act as it comes, writes the launch's end at its
                                         `verdict`, ticks after; spawned detached by the tick at every launch,
                                         its output at `follow.log` beside the journal
  pp-team status [<name>] [--json]    -> the state read from the journal; without a name, one
                                         line per team declared under `teams/`. Under `--json`
                                         the face a program reads: ONE object for the team named
                                         (its state and what it waits on, its season, its launch,
                                         its tasks and the wake-ups under way on each, members,
                                         ceremonies with their next ring, the owner's box), one per
                                         line without a name (its state, `asks` and `done` as the
                                         inbox counts them); each says `team`, the directory -- the
                                         team's identity --, and `name`, the `name:` of its `TEAM.md`
                                         (one line of 1 to 80 printable characters, `name-invalid`;
                                         the directory's name without it), read at every call: a
                                         rename moves nothing. The texts say the name, the directory
                                         after it when they differ. Nothing written.
  pp-team watch <name> [--task <id>] [--json] [--heartbeat <s>] [--for <s>] [--until-done]
      -> a READER: the journal's events as they arrive, the steps of every wake-up under way and
         what its harness does between two steps -- its flow read by `agent flow --follow`: a
         tool called, its result by its size, a thought, the words, the context measured --
         on stderr (`[HH:MM:SS] <team> · #<id> <kind> …`, `[HH:MM:SS] <member> · <run> · <step>`,
         `[HH:MM:SS] <member> · <run> · tool <name> · <title>`), `no event for <n>s` after
         `--heartbeat` seconds without one (60), one JSON object per line under `--json` (an
         activity: `event: activity`, its `kind`, at most ACTIVITY_RATE a second per wake-up,
         `more` on the one said for those it stands for); until Ctrl-C, `--for` seconds, or
         `--until-done` (no wake-up under way, and no task open or nothing due on them). No lock,
         nothing written, never a tick.
  pp-team log <name> [--task <id>] [--last <n>] [--json]
      -> the journal, one line per event, on stdout; under `--json` one object per event, the
         form `watch --json` writes (`event_object`)
  pp-team result <name> [<task>]      -> a resolved task's result as JSON on stdout (the last
                                         resolved without a task); `task-open`, `result-missing`
  pp-team responses <name> [--since <id>] [--agent <a>] [--task <t>] [--last <n>] [--json]
      -> the responses the team's agents gave, one per `wake-ended`, the text read at the house's
         record by (agent, run, index); `--since` those after a journal id -- what the head of
         a wake-up names: `[new responses since your last wake-up: r1 on T1 (#14) … -- read them
         whole: <house console> team responses <name> --since <id>]`; under `--json` one object
         per response, its text whole or `null`. Nothing written.
  pp-team inbox [<name>] [--seen | --json]
      -> one line per team where something waits for the owner (the questions without a reply,
         the tasks resolved and the posts returned since the last `inbox-seen`), one object per
         such team under `--json`; `--seen` writes `inbox-seen` -- the one write of these readers
  pp-team entry <name> [--run <key>]  -> the document the team's wake-up under that run (`PP_RUN`
                                         when `--run` is absent) plays this exchange: its task's
                                         ceremony's entry, else `do`'s, else `TEAM-IDLE.md` -- also
                                         for a key no wake-up of the team holds. The decider of the
                                         team's document, played by the engine of the agent; the
                                         house is the machine this script lives in. Nothing written.
  pp-team reset <name> [--member <m>] -> the run of each member named (every member without
                                         `--member`) FORGOTTEN by its agent's console (`-reset
                                         <key>`), then `run-reset {member, run}`: its next wake-up
                                         opens a new run told every open task; judged first under
                                         `tick.lock` (`team-busy` past `call_lock_wait`):
                                         `team-not-started`, `participant-unknown`, `member-running`.
  pp-team pause <name> [--as <principal>]
      -> PAUSES the team: judged under the journal's lock (`team-unknown`, `team-not-started`,
         `principal-unknown`, `team-paused` -- paused already), then `paused {by}`. Nothing is killed: the
         wake-ups under way end on their own and the tick reaps them and routes their answers; until the
         resume, the tick rings no ceremony and wakes nobody -- a post, a stop, a ring at hand, a budget, a
         task's resume or a season are written as ever, and the tick they play says `paused: nobody woken
         until team resume`. A season keeps the pause. No tick.
  pp-team resume <name> [--as <principal>] [--no-tick]
      -> RESUMES the paused team: judged under the journal's lock (`team-unknown`, `team-not-started`,
         `principal-unknown`, `team-not-paused`), then `unpaused {by}`; then the relaunch entry laid again,
         and a tick: what is due NOW -- each member due woken in its own run, the day's period of a ceremony
         rung when its hour is past and it never rang; a period passed during the pause is never rung.
  pp-team resume <name> --task <id> [--message <text>] [--as <principal>] [--no-tick]
      -> takes back ONE task a guard left with nobody due: STOPPED, held by a member's final failure,
         or past `launches:`. Judged under the journal's lock before anything is written (`team-unknown`,
         `team-not-started`, `principal-unknown`, `task-unknown`, `task-resolved`, `budget-spent` -- the
         team's `budget` or `budget-launches` reached: never reset by a resume, raised by `team budget` --,
         then `task-not-blocked`);
         then `resumed {task, by, from}` -- the task open again, its members' failures at zero, the
         terminals its final failures wrote dropped, its wake-ups counted afresh -- and an `info` (the
         message, `the task resumes` unless said) to each member it revives: the holders at the stop,
         the members whose final failure stands, the members with messages due past `launches:`. The
         posts returned at the stop stay returned. Then the relaunch entry laid again, and a tick.
  pp-team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]
      -> RAISES the team's `budget` (dollars) or `budget-launches` (wake-ups) without a start: judged
         under the journal's lock (`team-unknown`, `team-not-started`, `principal-unknown`,
         `budget-invalid` -- a number at or below what the team spent since its start: the cost kept,
         the launches); then `budget-raised {budget, launches, by}` -- the replay's limits raised,
         `budget-spent` lifted: the next exhaustion writes it again --; the members keep their runs.
         Then the relaunch entry laid again, and a tick.
  pp-team ring <name> <ceremony> [--as <principal>] [--no-tick]
      -> rings a declared ceremony AT HAND, out of its hour: what the tick's ring writes --
         `ceremony-due {ceremony, period, by}`, ONE task from the team to the facilitator, its opening
         `do` to the facilitator, a `do` per participant, the quorum's `wait` -- under the period `manual-<id>`, the id of
         its own `ceremony-due`: no date is taken, the `every` rings its day at its hour all the same.
         Judged under the journal's lock first: `team-unknown`, `team-not-started`, `principal-unknown`,
         `ceremony-unknown`, `ceremony-open` (a task of the ceremony still open). Then the relaunch
         entry laid again, and a tick.

  pp-team declaration <name> [--json]
      -> the declaration READ: `TEAM.md` whole, the verdict of `start`'s own judge -- `ok`, or the
         refusal `start` would write, said with rc 0 (a broken `TEAM.md` is shown to be mended, never
         refused) -- and its GAP to the last start: `{key, started, declared}` per key of the front
         matter `team-started` kept that the file now says otherwise (`agents`, `reports`, `root`,
         `principals`, `ceremonies` by their lines, `entries`, `work`, `limits`, `schedule`) -- what
         a new `start` would change; the body is never pending, pp serves it at once. Under `--json`
         ONE object `{team, name, path, text, digest, verdict: {ok, refusal}, started: {at, id, digest} |
         null, changed, pending}` (`pending` null under a refused verdict); the text says the path,
         the text, `verdict ok` or the refusal, then a line per key pending, or `not started`.
         Nothing written, no lock, never a tick; `team-unknown`, the usage.
  pp-team templates [--json]
      -> the TEMPLATES a team starts from, one line each -- its name, its default members, what it is --
         `supervisor-workers` (the root splits each task, one part per worker), `lead-reviewers` (the root
         does the work, each reviewer checks its draft), `chain` (each member hands the next step to the
         next one and passes the result back up), `solo`, `empty`, `council` (the root asks every expert
         the same question and concludes at its quorum), `triage` (the root hands each task whole to ONE
         specialist), `cross-check` (the root gives the same task to each twin and compares), `tree` (the
         root over its squad leads, each over its own workers); under `--json` one object per line,
         `{template, description, members, root, reports, ceremony, limits, intention}`. Nothing written.
  pp-team new <name> --template <t> [--member <name> <path>]... [--root <member>] [--principal <p>]...
                     [--budget <usd>] [--launches <n>] [--timeout <s>] [--schedule <minutes>|off]
                     [--no-ceremony] [--intention-file <path>] [--squads <n>]
      -> `teams/<name>/TEAM.md` and `teams/<name>/TEAM-<name>.md` WRITTEN from a template -- the declaration,
         then the team's document, the template's intention its body (`packages/team/templates/<t>.md`: its text --
         description, default members at `agents/<name>/<member>`, the daily, the limits, the intention):
         `--member` replaces the default members in the order given, and the template's FORM makes the
         root, the edges and the names of the intention of them -- the first member, or `--root`, is the
         root; the others report to it (`supervisor-workers`, `lead-reviewers`: the daily when two or
         more do, unless `--no-ceremony`; `council`, `triage`, `cross-check`), or each to the one before
         it (`chain`); `tree` takes the `--squads <n>` members after the root as its squad leads (the
         template's two unless said), reporting to the root, and gives the members after them to the
         squad leads in turn, as their workers -- the daily of the squad leads when they are two or more;
         `solo` and `empty` hold one member. The text is JUDGED by `start`'s own judge before any write, then written once
         -- linked in place only where no TEAM.md stands: `team-exists`, `template-unknown`,
         `team-invalid` (a member's path, a form given members it cannot hold, a limit that is no
         number, `--squads` off `tree` or below 1), `participant-unknown`, `root-missing`, the usage -- nothing left behind. Nothing starts:
         `team start` does. The TEAM.md written is the owner's: `new` never writes over it.
  pp-team delete <name> [--yes] [--json]
      -> the team REMOVED with what it made: its timer, its relaunch entry, every run its wake-ups opened
         (`agent purge <path> <run>... --yes` by the house's console), its journal and the files beside it,
         then `teams/<name>/` whole; without `--yes` it says what it would remove and writes nothing; under
         `--json` ONE object `{team, name, dry, directory, journal, relaunch, timer, runs: [{member, path,
         run}], agents}` -- `agents` the paths the team declares that no other team does: they stay. Under
         `tick.lock` waited within `call_lock_wait`: `team-unknown`, `team-busy` (a task open, a wake-up
         under way, the lock held -- `team stop <name> --kill` first); `deleting` written first, so that the
         guard lets the team's runs go; a purge refused stops it, `delete-failed`, and `delete --yes` again
         goes on. The agents and the runs the team never opened stay.

A TICK takes `tick.lock` beside the journal WITHOUT waiting: held by another tick, it posts the
mark `tick.pending`, tries once more and exits 0 having written nothing. The holder clears the
mark, plays its steps, releases the lock, THEN reads the mark: set, it takes the lock again
and plays once more. A wake-up is ONE LAUNCH of the harness (`agent start … --launches 1`), and what
the member says in it is read AS IT COMES: each `words` of the launch (a block of text between two
calls of the tool, kept at the run's flow by the house) is read by `agent flow --from` -- by the
launch's FOLLOWER while it plays, by the reap after --, and each ACT a `words` carries (`candidates_of`:
a JSON object, or a list of them, with the key of a form -- `do` with its `await`, `ask`, `re` -- alone or
written among other text) is routed once by its rank (`wake-routed {run, launch, words, line}`), or refused
and said to the member when its form or its sense is wrong (`wake-refused`, an `info`); a `words` without
an act is SAID: nothing written, nothing fails. The steps: 1. REAP -- each `wake-intent` without an end: its launch by
its `wake-launched` event, else by its tag at the house's `messages.jsonl` (read from the cursor
`tick.cursor`: a late `wake-launched`), else none: `wake-failed launch-missing`, never final and costing
no retry -- nothing was launched; launched, its wake lock is judged FIRST: held within `timeout:`, the
launch plays and its follower reads it; free, or held past the bound, its flow is read from the rank the
journal reached and the launch ENDED as the flow says: `wake-ended {run, launch, state, cost, flow}` --
`state` what the house said of the run at `--on-end`, `standing` (the run waits for a production:
relaunched as soon as its lock is free) or `parked` (it waits for a message) --, or `wake-failed
wake-dead` when no response stands (the harness died: one retry, its messages back in the inbox;
spent: `final`, and the tick ANSWERS in the member's place every message of the launch that owes --
never the opening a principal posted: the team tells that principal with a `notice` about the root),
`wake-timeout` when held past the bound (killed); 2. ROUTE -- an act's elements become posts in their
order: `do` to a member that reports to the acting one (on a ceremony task its participants report to
its facilitator) and the `wait` its `await` declares, `ask` to any member of the team or to a principal,
the answer `{"re": <id>}` to the author of the message it cites; a `do` off the edges, an `ask` to a name
nobody declared, a `re` citing a message never delivered to the member, an `await` of no number are
REFUSED (`wake-refused {…, why}`, an `info` to the member): nothing posted, the launch goes on. Each `do`
or `ask` delivered to a member opens ONE debt: the
first answer that cites it settles it -- a delegate's slot in its parent's wait --, a later one is
posted `info`; the ROOT's answer to the task's opening writes `done` with its text, settles every
debt of the task, `returned` for every post to an agent left undelivered on it, and `schedule-off`
when no task stays open and no ceremony is declared; a post to a principal is delivered at its
writing and never returned; 3. WAITS -- an (agent, task) whose every delegate on that task has
answered its `do` -- or, under the `await {any: n}` its last delegating answer there declared, n of
them: `wait-met`; 4. RING -- each ceremony whose period is due (`every`: the day conforms and the
hour is past, by `PP_NOW` or the local clock; `after`: the followed ceremony's task resolved)
and not yet rung (`ceremony-due` names the period: the journal is the judge) becomes ONE
ceremony task from the team to its facilitator, its OPENING `do` to the facilitator and a `do` per
participant -- the wait does the rest, and the facilitator's answer to the opening resolves it;
5. WAKE -- each MEMBER, in the declaration's order, with messages due, no launch of its under way
and the wake lock of its run free, is LAUNCHED ONCE -- on the first task, in the tasks' order, whose
wait is closed or carries a message that passes it (any but an answer to the round's `do`s and
the task's opening):
`wake-intent` WRITTEN FIRST, then `agent start … --launches 1 --tag <tag> --on-end "<engine> --instance
<house> team tick <name>"` (`--run <key>`, the member's run for the task's CARRIER, while its slot stands --
a renewal mark an upgrade left included; none yet, an OPENING, named after the carrier by `agent name`), then
`wake-launched` with the launch's RANK in the run, then its follower spawned; its other tasks wait for its
next launch, each in the run of its carrier. A member whose run STANDS (its last
launch left it waiting for a production) is RELAUNCHED on the task it stands on as soon as its lock is
free, `[nothing new]` at its head when nothing is due, unless its wait on that task holds. A member
holds ONE run, ONE key and ONE session per CARRIER of its tasks -- a task alone, the recurrence of its
occurrences, the ceremony of its rings --: the run that first answered there, the carrier's later tasks
arriving in it; it plays one launch at a time. The members play in parallel; `parallel:` bounds the team. The HEAD
of a launch -- what the tick writes before pp's output in the prompt -- opens on the inbox of that task
-- each message its head line, `#<id> DO from <member> on <task> -- you owe an answer`, its text
indented under it --, or `[nothing new]`, then the messages it still owes from earlier launches, the
line naming what the others answered since THIS run's last launch (the team's start for a new run);
nothing else: the contract of the acts is the body of the team's document, served by pp at the
start of the exchange; a NEW run of a member whose run `-reset` or `team reset` forgot opens on
`[history of <task> for <member>]` for the open tasks of its carrier -- what it was told there and what
it answered --, then its inbox. The head never carries the team's intention: it is the body of
`TEAM.md`, served by pp to the team's runs -- the team's document names it in its `serve:` row at the
kit's `turn.begin`, the reading proven by its content, served again at the next exchange when the
owner edits it. An
OPENING carries the team's material (`work:` -- passed as `--work`, a clone per run, kept with
its run); a resume never does. No wake-up carries a door: the trigger's ENTRY (`entries:` of
TEAM.md -- a ceremony task: its entry; else `do`'s) is a successor the agent's DAG elects at
EVERY exchange, opening or resume -- the team's document at the kit's `turn.begin`, in the team's
directory, decides by `pp-team entry <name>`. Every wake-up gets `--documents teams/<name>`: the
run opens under the team's root of documents. On a STOPPED task an answer is routed
nowhere, a dead wake-up is never retried, and nobody is woken: the stop is delivered at once -- a run STANDING on the task gets it at the head of one more launch.
The bounds count from the last `team-started`: the cost of every wake-up that answered (ended
or failed), and the wake-ups LAUNCHED under `launches` and `budget-launches`. A wake-up gets its SHARE of
the money: under `budget:`, where the adapter of the launch's grammar declares a cost scope (`COST`),
its intent carries an `allowance` -- min((`budget` - the cost kept) / k, `budget` - the cost kept -
the allowances of the wake-ups under way), k the wake-ups that may play together, min(`parallel`, the
members) -- reserved until its end, and `agent start --max-budget-usd` is the member's RUN cap: what
the run spent (its responses' `cost_usd`) plus the allowance; a member due whose rest is all reserved
is `deferred {reserved}`. Elsewhere no cap goes to `agent start`, and nothing is reserved: no per-wake
cap exists, and a `launch.max_budget_usd` an older journal kept is never passed. A wake-up being one
launch, the cap never falls between two launches: the share is the cap the harness plays under, and
what the launch reports is charged whole at its end.

THE NET of a team is its TIMER, at every step of `schedule:` (`off` for none ever, 5 minutes unless
said, kept in seconds at `team-started.schedule`): the tick arms it when a deadline stands, the
step bounding its sleep. The timer dies with the machine; ONE RELAUNCH ENTRY per HOUSE plays
`team tick --all` at the user's next logon -- one tick per team that needs its net -- and so arms the
timers again: the value `pp-team-<12 hex of the house>` of the user's Run key
(`HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`) under Windows, written with no right the
user lacks; a line `@reboot <python> <engine> --instance <house> team tick --all >/dev/null 2>&1
# pp-team <house>` in the user's crontab elsewhere -- or, under `PP_CRONTAB=<file>` and
`PP_RUNKEY=<file>`, those files (the bench, a try); `PP_SCHEDULER=nt|posix` names the façade. A
verb whose team needs its net -- a task open or a ceremony declared -- lays it after writing its
journal (`start`, a `post` that finds it gone); the tick at `schedule-off`, `stop` and `delete`
remove it only when NO team of the house needs it any more, judged and removed under
`state/relaunch.lock`. An entry the system refuses is SAID -- stderr (`relaunch not laid`), a notice
of the team to the owner once per season, the face -- and the team starts: it runs on its timer.

The house is the instance this script belongs to. The journal `.sys/records/teams/<name>/journal.jsonl` is APPEND-ONLY and this script
is its only writer: `{at, id, kind, team, ...}`, the id the previous one + 1, read and written
under the record's lock. A reader skips a last line still being written; a line that does
not parse anywhere else refuses by its name. Any other call says the usage in one line, exit 2.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import queue
import re
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

TEAMS = "teams"                  # under the house's root: one directory per team, its TEAM.md
TEAM_DOC = "TEAM.md"
JOURNAL = "journal.jsonl"        # under the house's records: teams/<name>/journal.jsonl
TICK_LOCK = "tick.lock"          # beside the journal: one tick at a time
TICK_MARK = "tick.pending"       # beside the journal: a tick asked while another played
MESSAGES = "messages.jsonl"      # the house's record pp-agent writes at every launch: read here for a late launch
TICK_CURSOR = "tick.cursor"      # beside the journal: how far the tick read messages.jsonl, the tags it keeps
TICK_TIMER = "tick.timer"        # beside the journal: the TIMER armed under the minute, {pid, due}, one at most
TIMER_WAIT = 2.0                 # seconds a timer waits for its mark to carry its token, before it leaves
TIMER_RETRY = 2.0                # seconds a timer waits before it plays its tick again under a maintenance
TIMER_RETRIES = 300              # the ticks a timer plays again under a maintenance at most: ten minutes
FOLLOW_LOG = "follow.log"        # beside the journal: what the followers of the launches said
CREATE_NEW_PROCESS_GROUP = 0x00000200   # Windows' process creation flags and answers, read on any system
CREATE_NO_WINDOW = 0x08000000
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
ERROR_ACCESS_DENIED = 5
BORDER = "---"
MODES = ("every", "after")       # a ceremony's rhythm: at a period, or after another ceremony
DOWS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")   # the days `every <dow> HH:MM` may name
NOW = "PP_NOW"                   # names the tick's wall clock (ISO, naive local): the bench, a try
CLOSED = ("stopped", "resolved")
ELEMENTS = {"do": {"do", "await"}, "ask": {"ask"}, "re": {"re", "text"}, "info": {"info"}}   # an act's forms and their keys
RETIRED_VERBS = ("done", "reply", "escalate", "note")   # the verbs of before -- an answer's until team 0.33.0, the
#                                                  principal's note until 0.47.0 --: read in a journal alone
OWED = "you owe an answer"                       # what the head says of a message whose debt stands
RELANCED = "[no new message: you still owe an answer]"   # the first line of a relance's head, for a debt alone
NOTHING_NEW = "[nothing new]"                    # the head of a relaunch of a standing run nothing arrived for
REMINDED_HEAD = ("[no new message: you still owe an answer and said nothing for several exchanges -- answer it now, "
                 "or say where you stand with an info]")   # the first line of a REMINDER's head (row 115)
DEFAULT_SILENCE = 3                              # silent parked exchanges that earn ONE reminder, unless TEAM.md says
MEMBER_TYPE = "member"                           # the profile `agent add` gives a member born by a start
DEFAULT_RETRIES = 1                              # wake-ups played again after a dead one, unless TEAM.md says
LIMITS = ("parallel", "budget", "retries", "timeout", "launches", "budget-launches", "suspect-max", "silence")   # the keys of TEAM.md that bound the tick
RETIRED_LIMITS = {"wakes": "launches", "budget-wakes": "budget-launches"}   # the keys of before: refused by name where written,
#                                                                            read where a journal already wrote them
RETIRED_FLAGS = {"--wakes": "--launches", "--budget-wakes": "--budget-launches"}
STOPPED_HEAD = "[the task is stopped: say no act, let your run park]"   # the head of the last launch of a run standing on a stopped task
DEFAULT_SCHEDULE = 300                           # seconds between two ticks of the net, unless TEAM.md says
DEFAULT_SUSPECT_MAX = 600                        # seconds: the longest interval a suspected member waits, unless TEAM.md says
MINUTE = 60                                      # the seconds of `m` and of a bare number of minutes in a duration
HOUR = 60 * MINUTE                               # the seconds of `h`
CRONTAB = "PP_CRONTAB"                           # names a file that stands for the user's crontab: the bench, a try
SCHEDULER = "PP_SCHEDULER"                       # names the scheduler's façade, `nt` or `posix`: the bench plays both
RUNKEY = "PP_RUNKEY"                             # names a file that stands for the user's Run key: one value per line
TIMER_ENV = "PP_TEAM_TIMER"                      # marks the tick a timer plays: read then taken out by `tick`
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"   # under HKEY_CURRENT_USER: played at the user's logon
RELAUNCH_PREFIX = "pp-team"                      # the head of the house's value in the Run key
RELAUNCH_LOCK = "relaunch.lock"                  # under the house's state: the relaunch entry laid, judged, removed
USAGE = ("usage: pp-team start <name> [--message <text> [--to <member>] [--name <text>]] [--budget <usd>] "
         "[--budget-launches <n>] [--provider <name>] [--harness <command>] "
         "[--model <m>] [--permissions auto|strict|bypass] "
         "[--effort low|medium|high|xhigh|max] [--no-tick] [--package <name>=on|off]... "
         "[--member <member> [--provider <name>] [--model <m>] [--effort <e>] [--permissions <p>] "
         "[--package <name>=on|off]...]... | "
         "post <name> [--message <text>] [--to <member>] [--task <id> | --name <text>] [--reply <id>] [--stop] "
         "[--as <principal>] [--every \"day|weekday|mon..sun HH:MM\" [--context <n>%]] "
         "[--no-tick] | stop <name> [--task <id>] [--kill] [--no-tick] | stop <name> --recurrence <R<n>> [--no-tick] | "
         "recurrence <name> <R<n>> [--every \"day|weekday|mon..sun HH:MM\"] [--context <n>%|off] [--message <text>] "
         "[--as <principal>] [--no-tick] | "
         "recurrence <name> --task <T<n>> --every \"day|weekday|mon..sun HH:MM\" [--context <n>%] [--as <principal>] "
         "[--no-tick] | "
         "tick <name> | tick --all | follow <name> <tag> | "
         "timer <name> --sleep <seconds> --due <local date-time> --token <token> | "
         "status [<name>] [--json] | "
         "watch <name> [--task <id>] [--json] [--heartbeat <seconds>] [--for <seconds>] [--until-done] | "
         "log <name> [--task <id>] [--last <n>] [--json] | result <name> [<task>] | "
         "responses <name> [--since <id>] [--agent <member>] [--task <t>] [--last <n>] [--json] | "
         "inbox [<name>] [--seen | --json] | "
         "snapshot <name> | entry <name> --run <key> | reset <name> [--member <member>] | "
         "pause <name> [--as <principal>] | resume <name> [--as <principal>] [--no-tick] | "
         "resume <name> --task <id> [--message <text>] [--as <principal>] [--no-tick] | "
         "budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick] | "
         "ring <name> <ceremony> [--as <principal>] [--no-tick] | templates [--json] | "
         "new <name> --template <t> [--member <name> <path>]... [--root <member>] [--principal <p>]... "
         "[--budget <usd>] [--launches <n>] [--timeout <s>] [--schedule <n>s|<n>m|<n>h|<minutes>|off] [--no-ceremony] "
         "[--intention-file <path>] [--squads <n>] | declaration <name> [--json] | "
         "delete <name> [--agent <path>]... [--yes] [--json] | rename <name> <new> [--json]")
LAUNCH_FLAGS = {"provider": True, "harness": True, "model": True, "permissions": True, "effort": True}
START_FLAGS = {"message": True, "to": True, "name": True, "no-tick": False, "budget": True, "budget-launches": True,
               "silence": True, **LAUNCH_FLAGS}
PROFILE_KEYS = ("provider", "model", "effort", "permissions")   # what a member's profile may replace
POST_FLAGS = {"message": True, "to": True, "task": True, "reply": True, "stop": False, "as": True, "name": True,
              "every": True, "context": True, "no-tick": False}
STOP_FLAGS = {"task": True, "kill": False, "recurrence": True, "no-tick": False}
RECURRENCE_FLAGS = {"every": True, "context": True, "message": True, "task": True, "as": True, "no-tick": False}
WATCH_FLAGS = {"task": True, "json": False, "heartbeat": True, "for": True, "until-done": False}
LOG_FLAGS = {"task": True, "last": True, "json": False}
INBOX_FLAGS = {"seen": False, "json": False}
DELETE_FLAGS = {"yes": False, "json": False}     # `--agent <path>`, repeatable, is taken out before (`agents_asked`)
RENAME_FLAGS = {"json": False}
RESPONSES_FLAGS = {"since": True, "agent": True, "task": True, "last": True, "json": False}
ENTRY_FLAGS = {"run": True}
RESET_FLAGS = {"member": True}
RESUME_FLAGS = {"task": True, "message": True, "as": True, "no-tick": False}
PAUSE_FLAGS = {"as": True}
RING_FLAGS = {"as": True, "no-tick": False}
BUDGET_FLAGS = {"launches": True, "as": True, "no-tick": False}
STATUS_FLAGS = {"json": False}
RESUMED = "the task resumes"                     # the note of a resume that names no message
IDLE = "TEAM-IDLE.md"                            # the neutral successor: a wake-up whose trigger names no entry
IDLE_SOURCE = "agent-idle.md"                    # beside this script -> the team's directory: the same bytes for every team
DECIDER = "pp-team entry"                        # what a team document's `decide:` plays: this skill's verb
ACT_FORMAT = "team-act"                          # the OUTPUT format an act is a production of (procs/TEAM-ACT.md declares it)
RETIRED = {("procs", "TURN.md"): "retired/agent-turn-0.32.txt",   # what an earlier version laid at an agent -> the
           ("procs", IDLE): "agent-idle.md",       # bytes it laid, beside this script or under `retired/`
           ("skills", "team-entry", "SKILL.md"): "retired/agent-entry.md",
           ("skills", "team-entry", "team-entry.py"): "retired/agent-entry.py"}
RETIRED_IN_TEAM = {"TURN.md": ("retired/agent-turn-0.32.txt", "retired/agent-turn-0.39.txt")}   # the team's own law of
                                                 # an earlier version, in the team's directory: removed at the start
ELEMENTS_LIST = ("do", "ask", "re", "info")      # the forms, in the order the contract says them
DEFAULT_HEARTBEAT = 60                           # seconds without a step before watch says so
ACTIVITY_RATE = 4                                # activity objects `watch` says per second and per launch: a reader
                                                 # takes in four lines a second; the surplus is folded into the last
                                                 # one said (`more`), a `context` always passes
ACTIVITY_TEXT = 80                               # characters of a text an activity object carries: a tool's title,
                                                 # a thought, the words -- never the content of a result
ACTIVITY_KINDS = ("tool", "tool-result", "thinking", "words", "context")   # what a flow says of a launch's activity
ACTIVITY_DRAIN = 1.0                             # seconds a reader of a flow keeps draining after its wake-up ended
DEAD = ("delegation", "terminal")                # the events a journal written before team 0.33.0 carries: the replay
                                                 # reads them, no face says them
HISTORY_CHARS = 200                              # a message's text in a reopened run's history
NAME_CHARS = 80                                  # a task's name: one line a user types, read in a table
RUN_NAME_CHARS = 60                              # a run's name, as `agent name` bounds it
TEMPLATES = Path(__file__).resolve().parents[2] / "templates"   # the package's team templates, one `<t>.md` each
FORMS = {"supervisor-workers": "star", "lead-reviewers": "star", "chain": "chain", "solo": "one", "empty": "one",
         "council": "star", "triage": "star", "cross-check": "star", "tree": "tree"}
SQUADS = 2                                       # the squad leads of a `tree` its template does not count
NEW_FLAGS = {"template": True, "member": True, "root": True, "principal": True, "budget": True, "launches": True,
             "timeout": True, "schedule": True, "no-ceremony": False, "intention-file": True, "squads": True}
REPEATED = ("member", "principal")               # the flags `new` takes several times


def refuse(said: str) -> None:
    sys.stderr.write(f"pp-team: {said}\n")
    raise SystemExit(2)


class Declined(Exception):
    """A declaration the judge does not accept: its text is the refusal `start` writes."""


def decline(said: str) -> None:
    raise Declined(said)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- the house -----------------------------------------------------------------------------

def house():
    """-> (the house's instance root, the conductor module) -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core, home                          # noqa: E402 -- the bootstrap
    root = home(__file__)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(__file__)


def locks(conductor):
    """-> the engine's `state.lock` module: the tick lock, and the launchers' files it tests."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.lock")


def tracing(conductor):
    """-> the engine's `state.log` module: the one reader of a trace (`tail`, `follow`,
    `step_of`, `said`), shared with `pp-agent`."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.log")


def house_console(root: Path, conductor) -> Path:
    """-> the house's console by its absolute path (`pp`, `pp.cmd` on Windows): what an agent
    calls to read what the head of its message names."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.packaging.adapters").console_of(root.parent)


def owner_of(root: Path, conductor) -> str:
    """-> the team's OWNER: the house's slug."""
    return str(conductor.instance.slug(root))


def team_doc(root: Path, name: str) -> Path:
    return root.parent / TEAMS / name / TEAM_DOC


def team_root(root: Path, name: str) -> Path:
    """-> the team's directory: its TEAM.md, its entries, its documents -- the root of documents of
    every run the team opens."""
    return root.parent / TEAMS / name


def journal_of(root: Path, name: str) -> Path:
    return root / ".sys" / "records" / TEAMS / name / JOURNAL


def record_of(root: Path, name: str) -> Path:
    """-> one of the house's records -- written by pp-agent, read here."""
    return root / ".sys" / "records" / name


def agent_meta(root: Path, path: str) -> Path:
    """-> where the agent `path` stands: an agent IS its path under the house, slugs joined by
    `/` (`m`, `squad/r9`), its instance directory named as the house's own. The path is judged
    at the declaration (`path_valid`)."""
    return root.parent.joinpath(*path.split("/")) / root.name


def path_valid(conductor, path: str) -> bool:
    """-> whether `path` is an agent's path: slugs joined by `/`, no `..`, no leading `/`, no
    empty segment."""
    return bool(path) and all(conductor.instance.valid_slug(one) for one in path.split("/"))


def path_of(state: dict, member: str) -> str:
    """-> the path of the agent that plays `member`, read at `team-started.agents`: the team
    speaks names, the house addresses its agents by their paths."""
    return str(((state["started"] or {}).get("agents") or {}).get(member, member))


def path_of_intent(state: dict, intent: dict) -> str:
    """-> the path of the agent a wake-up woke: the `path` its intent carries, else its
    member's path."""
    return str(intent.get("path") or path_of(state, intent["agent"]))


def birth_lock_of(root: Path, conductor, path: str) -> Path:
    """-> the house's BIRTH lock for one agent's path: `.sys/state/born-<digest>.lock`, the
    digest of the path -- the lock `pp-agent add` takes too, so that one path is born once."""
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:12]
    return root / conductor.persistence.DIRECTORY / f"born-{digest}.lock"


def launch_of(conductor, meta: Path, run: str) -> Path:
    """-> the launcher's file of an agent's run, `session-<run>.wake.lock` beside its slot --
    the `agent` package's published contract: held while a wake-up plays."""
    return conductor.persistence.slot_of(meta, run).with_name(f"session-{run}.wake.lock")


def engine_of(root: Path, conductor) -> Path:
    """-> the engine the house's console runs: the one a tick names in `--on-end`."""
    return conductor.instance.engine_root(root) / "pp.py"


def retired_flags(rest: list[str]) -> None:
    """A flag of before (`--wakes`, `--budget-wakes`: the bounds counted wake-ups) refuses `flag-retired`
    naming the flag that took its place; nothing is parsed after it."""
    for flag in rest:
        if flag in RETIRED_FLAGS:
            refuse(f"flag-retired -- `{flag}`: the bounds count launches -- say `{RETIRED_FLAGS[flag]}`.")


def flags(rest: list[str], table: dict[str, bool]) -> dict:
    """-> the verb's flags from its table (True: takes a value); anything else is the usage."""
    found: dict = {name: (None if takes else False) for name, takes in table.items()}
    index = 0
    while index < len(rest):
        word = rest[index]
        name = word[2:] if word.startswith("--") else ""
        if name not in table:
            refuse(USAGE)
        if table[name]:
            if index + 1 >= len(rest):
                refuse(USAGE)
            found[name] = rest[index + 1]
            index += 2
        else:
            found[name] = True
            index += 1
    return found


def named_team(conductor, rest: list[str]) -> tuple[str, list[str]]:
    """-> (the team's name, the rest): the first word names the team, a slug."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    name = rest[0]
    if not conductor.instance.valid_slug(name):
        refuse(f"team-invalid -- `{name}`: a team's name is lowercase, digits and single dashes.")
    return name, rest[1:]


# --- the declaration: TEAM.md read whole ---------------------------------------------------

def block(front: dict, key: str) -> list[str]:
    """-> the non-empty lines of a `key: |` block, stripped; nothing for an absent key."""
    return [line.strip() for line in str(front.get(key, "")).splitlines() if line.strip()]


def team_name(root: Path, conductor, name: str) -> str:
    """-> the name a team is SHOWN by: the `name:` of its `TEAM.md`, read at every call -- the directory's name, the
    team's identity, when the key is absent or the file cannot be read. Nothing keyed by it: a rename moves no
    journal, no relaunch entry, no file."""
    try:
        said = conductor.reading.read(team_doc(root, name)).front.get("name")
    except (conductor.Refusal, OSError):
        return name
    shown = "" if said is None else str(said).strip()
    return shown if shown and len(shown) <= NAME_CHARS and shown.isprintable() else name


def labelled(root: Path, conductor, name: str) -> str:
    """-> how a text says a team: its name, the directory's name after it when they differ."""
    shown = team_name(root, conductor, name)
    return name if shown == name else f"{shown} ({name})"


def body_of(text: str) -> str:
    """-> the text after the front matter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != BORDER:
        return ""
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    return "\n".join(lines[end + 1:]).strip() if end is not None else ""


def when_of(words: list[str]) -> dict | None:
    """-> the period an `every` names, `{kind, at}` -- `day`, `weekday` or a day of the week, then the local hour
    `HH:MM` --, or None when the words say anything else: the ONE reader of a period, a ceremony's and a
    recurrence's."""
    at = words[1] if len(words) == 2 else ""
    timed = (len(at) == 5 and at[2] == ":" and at[:2].isdigit() and at[3:].isdigit()
             and int(at[:2]) < 24 and int(at[3:]) < 60)
    if len(words) != 2 or words[0] not in ("day", "weekday", *DOWS) or not timed:
        return None
    return {"kind": words[0], "at": at}


UNITS = {"m": MINUTE, "h": HOUR, "d": 24 * HOUR}  # the units of a recurrence's duration


def every_of(text: str) -> dict:
    """-> the period a recurrence's `--every` names: a dated one, `{kind, at}` as `when_of` reads it, or a DURATION
    `<n>m|<n>h|<n>d` -- n a whole number from 1, a minute at least --, `{kind: "interval", every, seconds}`;
    `every-invalid` naming both forms otherwise. A ceremony reads `when_of` alone: it has no duration."""
    words = text.split()
    found = when_of(words)
    duration = re.fullmatch(r"([1-9][0-9]*)([mhd])", words[0]) if len(words) == 1 else None
    if found is None and duration is not None:
        found = {"kind": "interval", "every": words[0], "seconds": int(duration.group(1)) * UNITS[duration.group(2)]}
    if found is None:
        refuse(f"every-invalid -- `--every {' '.join(words)[:40]}`: a recurrence comes back "
               "`day|weekday|mon..sun HH:MM`, the local hour, or every `<n>m|<n>h|<n>d`.")
    return found


def said_when(when: dict) -> str:
    """-> a recurrence's period as the faces say it after `every`: `weekday 09:30`, or `4h`."""
    return str(when.get("every")) if when.get("kind") == "interval" else f"{when.get('kind')} {when.get('at')}"


def ceremony_of(line: str, agents: dict, path: Path) -> dict:
    """-> one ceremony as its line declares it: `<name> every … [with a b -> c [any <n>]]` or
    `<name> after <other> … [with a b -> c [any <n>]]` -- the name, the mode, what it follows, its
    participants, its facilitator and its quorum (n of the participants whose terminal answers wake
    the facilitator, `None` for all); the rest of the words kept as the text the rhythm will read."""
    words = line.split()
    if len(words) < 2 or words[1] not in MODES:
        decline(f"team-invalid -- {path}: ceremonies: `{line}` -- a line is `<name> every …` or `<name> after <other> …`.")
    name, mode = words[0], words[1]
    spec = words[2:words.index("with")] if "with" in words else words[2:]
    after, when = None, None
    if mode == "after":
        if len(spec) != 1 or spec[0] == "with":
            decline(f"team-invalid -- {path}: ceremonies: `{line}` -- `after` names the ceremony it follows, "
                   "and nothing else.")
        after = spec[0]
    else:
        when = when_of(spec)
        if when is None:
            decline(f"team-invalid -- {path}: ceremonies: `{line}` -- the when is "
                   "`every day|weekday|mon..sun HH:MM`.")
    participants: list[str] = []
    facilitator, quorum = None, None
    if "with" in words:
        tail = words[words.index("with") + 1:]
        if "->" in tail:
            at = tail.index("->")
            participants, targets = tail[:at], tail[at + 1:]
            if len(targets) == 3 and targets[1] == "any":       # the quorum: `-> c any <n>`
                n = targets[2]
                if not n.isdigit() or not 1 <= int(n) <= len(participants):
                    decline(f"team-invalid -- {path}: ceremonies: `{line}` -- the quorum is `any <n>`, n from 1 to "
                           f"the {len(participants)} participant(s).")
                quorum, targets = int(n), targets[:1]
            if len(targets) != 1:
                decline(f"team-invalid -- {path}: ceremonies: `{line}` -- one facilitator after `->`, "
                       "then `any <n>` at most.")
            facilitator = targets[0]
        else:
            participants = tail
        for one in participants + ([facilitator] if facilitator else []):
            if one not in agents:
                decline(f"participant-unknown -- {path}: ceremony `{name}` names `{one}`, a member nobody declared.")
    if facilitator is None or not participants:
        decline(f"team-invalid -- {path}: ceremonies: `{line}` -- a ceremony owes its participants and its "
               "facilitator: `with a b -> c`.")
    return {"name": name, "mode": mode, "after": after, "when": when, "participants": participants,
            "facilitator": facilitator, "quorum": quorum, "text": line}


def acyclic(ceremonies: list[dict], path: Path) -> None:
    """The `after` graph must be a DAG: a loop would ring for ever -- `ceremony-cycle`."""
    follows = {one["name"]: one["after"] for one in ceremonies}
    for start in follows:
        seen, step = [start], follows[start]
        while step is not None:
            if step in seen:
                decline(f"ceremony-cycle -- {path}: `{' -> '.join(seen + [step])}` -- `after` loops; the chain "
                       "of ceremonies must end.")
            seen.append(step)
            step = follows.get(step)


def declared(root: Path, conductor, name: str) -> dict:
    """-> the team as `TEAM.md` declares it, read WHOLE and judged before anything is written
    (`judged`)."""
    path = team_doc(root, name)
    if not path.is_file():
        refuse(f"team-unknown -- no {path}: the owner declares the team there.")
    try:
        document = conductor.reading.read(path)
    except conductor.Refusal as refusal:
        refuse(f"team-invalid -- {path}: {refusal}")
    try:
        return judged(conductor, document.front, path.read_bytes(), path, name)
    except Declined as declining:
        refuse(str(declining))


def judged(conductor, front: dict, data: bytes, path: Path, name: str) -> dict:
    """-> the team a declaration's text declares, judged whole -- the agents and their types, the
    edges, the root, the mandators, the ceremonies (their names, participants and `after`
    graph), `work`, the name shown -- `name:`, the directory's name without it -- and the digest; each defect
    DECLINES by its name (`Declined`, its
    text the refusal `start` writes). `start` judges the file standing at `path`, `new` the text it is
    about to write there, `declaration` the file as it stands, saying the verdict."""
    said = front.get("name")
    shown = name if said is None else str(said).strip()
    if not shown or len(shown) > NAME_CHARS or not shown.isprintable():
        decline(f"name-invalid -- {path}: `name: {' '.join(str(said).split())[:40]}` -- a team's name is one line of 1 "
                f"to {NAME_CHARS} printable characters.")
    agents: dict[str, str] = {}
    for line in block(front, "agents"):
        words = line.split()
        if len(words) != 2:
            decline(f"team-invalid -- {path}: agents: `{line}` -- one line per member, `<name> <path>`.")
        member, at = words
        if not conductor.instance.valid_slug(member):
            decline(f"team-invalid -- {path}: agents: `{member}` -- a member's name is one slug (lowercase, "
                   "digits and single dashes), no `/`.")
        if not path_valid(conductor, at):
            decline(f"team-invalid -- {path}: agents: `{at}` -- an agent is its path under the house, slugs "
                   "(lowercase, digits and single dashes) joined by `/`.")
        if member in agents:
            decline(f"team-invalid -- {path}: agents: `{member}` declared twice -- one name per member.")
        agents[member] = at
    if not agents:
        decline(f"team-invalid -- {path}: `agents:` declares nobody.")
    reports = []
    for line in block(front, "reports"):
        if "->" not in line:
            decline(f"team-invalid -- {path}: reports: `{line}` -- an edge is `a b -> c`.")
        left, right = line.split("->", 1)
        sources, targets = left.split(), right.split()
        if not sources or len(targets) != 1:
            decline(f"team-invalid -- {path}: reports: `{line}` -- members on the left, one member on the right.")
        for one in sources + targets:
            if one not in agents:
                decline(f"participant-unknown -- {path}: reports: `{one}` is a member nobody declared.")
        reports.append({"from": sources, "to": targets[0]})
    root_agent = str(front.get("root") or "").strip()
    if not root_agent:
        decline(f"root-missing -- {path}: `root:` names the member a task goes to when no `--to` names one.")
    if root_agent not in agents:
        decline(f"participant-unknown -- {path}: root `{root_agent}` is a member nobody declared.")
    principals = []
    for line in block(front, "principals"):
        if len(line.split()) != 1:
            decline(f"team-invalid -- {path}: principals: `{line}` -- one name per line.")
        principals.append(line)
    ceremonies = [ceremony_of(line, agents, path) for line in block(front, "ceremonies")]
    names = [one["name"] for one in ceremonies]
    for one in ceremonies:
        if names.count(one["name"]) > 1:
            decline(f"team-invalid -- {path}: ceremonies: `{one['name']}` declared twice.")
        if one["after"] is not None and one["after"] not in names:
            decline(f"team-invalid -- {path}: ceremonies: `{one['name']}` follows `{one['after']}`, a ceremony nobody declared.")
    acyclic(ceremonies, path)
    entries: dict[str, str] = {}
    for line in block(front, "entries"):
        if "->" not in line:
            decline(f"team-invalid -- {path}: entries: `{line}` -- one line is `<trigger> -> <document>`.")
        trigger, document = (part.strip() for part in line.split("->", 1))
        if not trigger or len(document.split()) != 1:
            decline(f"team-invalid -- {path}: entries: `{line}` -- one trigger, one document.")
        if trigger != "do" and trigger not in names:
            decline(f"team-invalid -- {path}: entries: `{trigger}` is neither `do` nor a declared "
                   "ceremony's name.")
        if trigger in entries:
            decline(f"team-invalid -- {path}: entries: `{trigger}` declared twice.")
        entries[trigger] = document
    work = front.get("work")
    return {"agents": agents, "reports": reports, "root": root_agent, "principals": principals,
            "ceremonies": ceremonies, "entries": entries, "work": None if work is None else str(work),
            "limits": limits_of(front, path), "schedule": schedule_of(front, path),
            "name": shown, "digest": hashlib.sha256(data).hexdigest()[:12]}


def seconds_of_duration(value) -> int | None:
    """-> the SECONDS a declaration's duration says -- `10s`, `2m`, `1h`, or a bare whole number of MINUTES (the form
    of before: `schedule: 5`) --, None for a form this contract cannot read or a duration under a second."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value * MINUTE if value >= 1 else None
    text = str(value).strip()
    unit = 1 if text.endswith("s") else MINUTE if text.endswith("m") else HOUR if text.endswith("h") else None
    digits = text[:-1] if unit is not None else text
    if not digits.isdigit() or int(digits) < 1:
        return None
    return int(digits) * (unit or MINUTE)


def schedule_of(front: dict, path: Path) -> int | None:
    """-> the net's step in SECONDS: `schedule:` of `TEAM.md` -- `off` (None: no net, ever), `<n>s`, `<n>m`, `<n>h`
    or a bare whole number of minutes, DEFAULT_SCHEDULE when the key is absent; any other value refuses
    `team-invalid` naming the four forms."""
    if "schedule" not in front:
        return DEFAULT_SCHEDULE
    value = front["schedule"]
    if value is False or (isinstance(value, str) and value.strip() == "off"):
        return None
    seconds = seconds_of_duration(value)
    if seconds is None:
        decline(f"team-invalid -- {path}: `schedule: {value}` -- `off`, or how long the team's timer sleeps at most, "
                "a second at least: `10s`, `2m`, `1h`, or a bare number of minutes (`5`).")
    return seconds


def schedule_seconds(started: dict | None) -> int | None:
    """-> the net's step in seconds as the start kept it: `team-started.schedule` with its `unit` (`s`, team 0.41.0),
    minutes when a journal written before kept no unit, DEFAULT_SCHEDULE when the start kept nothing; None under
    `off`."""
    if not started or "schedule" not in started:
        return DEFAULT_SCHEDULE
    value = started.get("schedule")
    if value is None:
        return None
    return int(value) if started.get("unit") == "s" else int(value) * MINUTE


def limits_of(front: dict, path: Path) -> dict:
    """-> the bounds `TEAM.md` declares, each judged: `parallel` a whole number of 1 or more,
    `budget` a number above 0 (dollars), `retries` a whole number of 0 or more, `timeout` a
    number of seconds above 0, `launches` (the launches of one task) and `budget-launches` (the
    launches of the season) whole numbers of 1 or more, `suspect-max` a duration (`20s`, `2m`, bare minutes),
    kept in seconds, `silence` a whole number of 1 or more (the silent parked exchanges that earn one reminder;
    DEFAULT_SILENCE without it); an absent key is no bound; any other value
    refuses `team-invalid` naming the key and the value; a key of before (`launches`, `budget-launches`: the
    bounds counted wake-ups) refuses `limit-retired` naming the key that took its place."""
    found: dict = {}
    for key, now in RETIRED_LIMITS.items():
        if key in front:
            decline(f"limit-retired -- {path}: `{key}:` is gone -- the bounds count launches: say `{now}:`.")
    for key in LIMITS:
        if key not in front:
            continue
        value = front[key]
        whole = isinstance(value, int) and not isinstance(value, bool)
        number = whole or (isinstance(value, float) and value == value)
        if key == "parallel" and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `parallel: {value}` -- a whole number of 1 or more.")
        if key == "budget" and (not number or value <= 0):
            decline(f"team-invalid -- {path}: `budget: {value}` -- a number of dollars above 0.")
        if key == "retries" and (not whole or value < 0):
            decline(f"team-invalid -- {path}: `retries: {value}` -- a whole number of 0 or more.")
        if key == "timeout" and (not number or value <= 0):
            decline(f"team-invalid -- {path}: `timeout: {value}` -- a number of seconds above 0.")
        if key in ("launches", "budget-launches") and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `{key}: {value}` -- a whole number of 1 or more.")
        if key == "silence" and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `silence: {value}` -- a whole number of 1 or more: the silent parked "
                    "exchanges that earn one reminder.")
        if key == "suspect-max":                           # kept in seconds: the longest interval of a suspicion
            value = seconds_of_duration(value)
            if value is None:
                decline(f"team-invalid -- {path}: `suspect-max: {front[key]}` -- a duration: seconds (`20s`), "
                        "minutes (`2m`, `10`).")
        found[key] = value
    return found


# --- the templates: a TEAM.md to start from ------------------------------------------------

def template_of(conductor, template: str) -> dict:
    """-> one template as its file says it: its description, its default members, its daily's rhythm
    and the paragraph the intention gains with it, its limits, `schedule`, its `squads` (a `tree`'s squad
    leads), and its intention -- `template-unknown` for a name the package carries no file of."""
    path = TEMPLATES / f"{template}.md"
    if template not in FORMS or not path.is_file():
        refuse(f"template-unknown -- `{template}`: the templates are {', '.join(FORMS)} (`team templates`).")
    document = conductor.reading.read(path)
    front = document.front
    return {"template": template, "description": str(front.get("description") or ""),
            "members": block(front, "members"), "daily": front.get("daily"),
            "daily_intention": str(front.get("daily-intention") or ""),
            "limits": {key: front[key] for key in ("budget", "launches", "timeout") if key in front},
            "schedule": front.get("schedule"), "squads": front.get("squads"),
            "intention": body_of(path.read_text(encoding="utf-8"))}


def quoted(names: list[str]) -> str:
    """-> names as the intention says them: `a`, `a` and `b`, `a`, `b` and `c`."""
    marked = [f"`{one}`" for one in names]
    return marked[0] if len(marked) == 1 else ", ".join(marked[:-1]) + " and " + marked[-1]


def formed(template: dict, members: list[str], root: str | None, ceremony: bool, squads: int | None = None) -> dict:
    """-> the team a template's FORM makes of its members, in their order: `star` -- the root
    (the first, or `root` moved to the head) and every other member reporting to it, the daily
    when two of them or more report to it; `chain` -- each member reporting to the one before it,
    the first the root; `one` -- a single member, the root; `tree` -- the root, then `squads` squad
    leads reporting to it (the template's `squads`, else SQUADS), then the workers, given to the
    squad leads in turn and reporting to theirs, the daily of the squad leads when they are two or
    more. A form given members it cannot hold refuses `team-invalid`; a root nobody declared is
    written as asked, for the judge to refuse."""
    form, name = FORMS[template["template"]], template["template"]
    if form == "one" and len(members) != 1:
        refuse(f"team-invalid -- template `{name}` holds one member: {len(members)} given.")
    if form != "one" and len(members) < 2:
        refuse(f"team-invalid -- template `{name}` holds two members or more: {len(members)} given.")
    leads = squads if squads is not None else int(template.get("squads") or SQUADS)
    if form == "tree" and len(members) < 1 + 2 * leads:
        refuse(f"team-invalid -- template `{name}` with {leads} squad lead(s) holds {1 + 2 * leads} members or "
               f"more -- the root, the squad leads, one worker each at least: {len(members)} given.")
    order = ([root] + [one for one in members if one != root]) if root in members else list(members)
    head = root or order[0]
    others = [one for one in order if one != head]
    chiefs, workers = (others[:leads], others[leads:]) if form == "tree" else (others, [])
    crews = {chief: workers[at::leads] for at, chief in enumerate(chiefs)} if form == "tree" else {}
    if form in ("star", "tree"):
        reports = ([f"{' '.join(chiefs)} -> {head}"] if chiefs else []) + [
            f"{' '.join(crew)} -> {chief}" for chief, crew in crews.items()]
    elif form == "chain":
        reports = [f"{order[at]} -> {order[at - 1]}" for at in range(1, len(order))]
    else:
        reports = []
    daily = (f"daily {template['daily']} with {' '.join(chiefs)} -> {head}"
             if form in ("star", "tree") and ceremony and template["daily"] and len(chiefs) >= 2 else None)
    holes = {"root": f"`{head}`", "others": quoted(others) if others else "",
             "chain": " -> ".join(f"`{one}`" for one in order), "last": f"`{order[-1]}`",
             "squads": quoted(chiefs) if chiefs else "", "workers": quoted(workers) if workers else "",
             "tree": "; ".join(f"`{chief}` with {quoted(crew)}" for chief, crew in crews.items()),
             "quorum": str(max(1, len(others) - 1)), "count": str(len(others)),
             "daily": template["daily_intention"] if daily else ""}
    def filled(text: str) -> str:
        for hole, value in holes.items():
            text = text.replace("{" + hole + "}", value)
        return re.sub(r"\n{3,}", "\n\n", text).strip()
    holes["daily"] = filled(holes["daily"])
    return {"members": order, "root": head, "reports": reports, "ceremony": daily,
            "intention": filled(template["intention"])}


def composed(name: str, members: dict[str, str], team: dict, principals: list[str], limits: dict,
             schedule) -> str:
    """-> the text of `TEAM.md`: the declaration, its front matter in its own keys -- the intention is the team's
    document's."""
    lines = [BORDER, "agents: |", *(f"  {member} {path}" for member, path in members.items())]
    if team["reports"]:
        lines += ["reports: |", *(f"  {one}" for one in team["reports"])]
    lines.append(f"root: {team['root']}")
    if principals:
        lines += ["principals: |", *(f"  {one}" for one in principals)]
    if team["ceremony"]:
        lines += ["ceremonies: |", f"  {team['ceremony']}"]
    lines += [f"{key}: {value}" for key, value in limits.items()]
    if schedule is not None:
        lines.append(f"schedule: {schedule}")
    lines.append(BORDER)
    return "\n".join(lines) + "\n"


def asked_new(rest: list[str]) -> dict:
    """-> `new`'s flags: `--member <name> <path>` and `--principal <p>` several times, the others
    once (the usage otherwise)."""
    found: dict = {"member": [], "principal": []}
    index = 0
    while index < len(rest):
        word = rest[index]
        flag = word[2:] if word.startswith("--") else ""
        if word in RETIRED_FLAGS:
            refuse(f"flag-retired -- `{word}`: the bounds count launches -- say `{RETIRED_FLAGS[word]}`.")
        if flag not in NEW_FLAGS:
            refuse(USAGE)
        if flag == "member":
            if index + 2 >= len(rest):
                refuse(USAGE)
            found["member"].append((rest[index + 1], rest[index + 2]))
            index += 3
        elif NEW_FLAGS[flag]:
            if index + 1 >= len(rest) or (flag not in REPEATED and flag in found):
                refuse(USAGE)
            if flag in REPEATED:
                found[flag].append(rest[index + 1])
            else:
                found[flag] = rest[index + 1]
            index += 2
        else:
            found[flag] = True
            index += 1
    if "template" not in found:
        refuse(USAGE)
    return found


def numbered(flag: str, value: str, whole: bool):
    """-> a limit given on the command line as the number it says -- `team-invalid` naming the flag
    otherwise; the judge then bounds it as it bounds `TEAM.md`'s."""
    try:
        return int(value) if whole or value.isdigit() else float(value)
    except ValueError:
        refuse(f"team-invalid -- `--{flag} {value}`: a {'whole number' if whole else 'number'}.")


def templates_verb(rest: list[str]) -> int:
    """`team templates [--json]`: one line per template -- its name, its default members, its
    description; under `--json` one object per line, the team it makes for its default members.
    Nothing written."""
    _, conductor = house()
    asked = flags(rest, STATUS_FLAGS)
    for name in FORMS:
        template = template_of(conductor, name)
        team = formed(template, template["members"], None, True)
        if asked["json"]:
            print(json.dumps({"template": name, "description": template["description"],
                              "members": team["members"], "root": team["root"],
                              "reports": [{"from": one.split("->")[0].split(), "to": one.split("->")[1].strip()}
                                          for one in team["reports"]],
                              "ceremony": team["ceremony"], "limits": template["limits"],
                              "intention": team["intention"]}, ensure_ascii=False))
        else:
            print(f"{name}  {', '.join(team['members'])} -- {template['description']}")
    return 0


def new_verb(rest: list[str]) -> int:
    """`team new <name> --template <t> …`: `TEAM.md` composed from the template, JUDGED by `start`'s
    own judge, then written once -- a temporary beside it, linked in place only where no `TEAM.md`
    stands --, and `TEAM-<name>.md` beside it, the template's intention its body. Every refusal comes
    before any write: nothing is left. Nothing starts: `team start` does."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = asked_new(rest)
    path = team_doc(root, name)
    if path.exists():
        refuse(f"team-exists -- {path} stands: a template writes a new team, never over the owner's.")
    template = template_of(conductor, asked["template"])
    squads = None
    if "squads" in asked:
        if FORMS[asked["template"]] != "tree":
            refuse(f"team-invalid -- `--squads {asked['squads']}`: the template `{asked['template']}` has no squads -- "
                   "`--squads` is the template `tree`'s alone.")
        squads = numbered("squads", asked["squads"], True)
        if squads < 1:
            refuse(f"team-invalid -- `--squads {asked['squads']}`: a whole number of 1 or more.")
    given = asked["member"] or [(one, f"agents/{name}/{one}") for one in template["members"]]
    members: dict[str, str] = {}
    for member, at in given:
        if member in members:
            refuse(f"team-invalid -- `--member {member}` given twice: one name per member.")
        members[member] = at
    for one in asked["principal"]:
        if not one or len(one.split()) != 1 or one != one.strip():
            refuse(f"team-invalid -- `--principal {one}`: one name, no blank.")
    team = formed(template, list(members), asked.get("root"), not asked.get("no-ceremony"), squads)
    limits = dict(template["limits"])
    for flag, whole in (("budget", False), ("launches", True), ("timeout", False)):
        if flag in asked:
            limits[flag] = numbered(flag, asked[flag], whole)
    schedule = template["schedule"]
    if "schedule" in asked:
        schedule = asked["schedule"]                       # `off`, `5s`, `2m`, minutes: start's own judge reads it
    elif schedule is False:
        schedule = "off"
    intention = team["intention"]
    if "intention-file" in asked:
        own = Path(asked["intention-file"])
        if not own.is_file():
            refuse(f"team-invalid -- `--intention-file {own}`: no such file.")
        intention = own.read_text(encoding="utf-8")
    text = composed(name, {one: members[one] for one in team["members"] if one in members}, team,
                    asked["principal"], limits, schedule)
    lines = text.splitlines()
    try:
        front = conductor.reading.front_matter(lines[1:lines.index(BORDER, 1)])
    except conductor.Refusal as refusal:
        refuse(f"team-invalid -- {path}: {refusal}")
    try:
        judged(conductor, front, text.encode("utf-8"), path, name)
    except Declined as declining:
        refuse(str(declining))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}-{secrets.token_hex(3)}")
    temporary.write_text(text, encoding="utf-8")
    try:
        os.link(temporary, path)                   # never over a TEAM.md another hand wrote meanwhile
    except FileExistsError:
        refuse(f"team-exists -- {path} stands: written meanwhile by another hand.")
    finally:
        temporary.unlink()
    placed(path.parent / document_name(name), team_document(name, [], intention.strip() + "\n" if intention.strip() else ""))
    print(f"pp-team: {path.relative_to(root.parent)} written from template {asked['template']} · members "
          f"{', '.join(team['members'])} · root {team['root']} -- start it: team start {name} --message <text>")
    return 0


# --- the declaration read: its text, its verdict, its gap to the start ---------------------------

PENDING = ("agents", "reports", "root", "principals", "ceremonies", "entries", "work", "limits", "schedule")


def kept_at_start(started: dict, key: str):
    """-> what `team-started` kept of one key of the front matter, in the journal's form -- a ceremony by
    its declaration line."""
    if key == "ceremonies":
        return [one.get("text") for one in started.get("ceremonies") or []]
    if key == "schedule":
        return schedule_seconds(started)
    empty = {"agents": {}, "reports": [], "principals": [], "entries": {}, "limits": {}}
    return started.get(key, empty.get(key))


def gap(started: dict, team: dict) -> list[dict]:
    """-> what a new `start` would change: `{key, started, declared}` per key of the front matter
    `team-started` kept that the declaration now says otherwise, in `PENDING`'s order. The body is never
    pending: pp serves it to the team's runs as soon as it changes."""
    found = []
    for key in PENDING:
        now_said = [one["text"] for one in team["ceremonies"]] if key == "ceremonies" else team[key]
        then = kept_at_start(started, key)
        if then != now_said:
            found.append({"key": key, "started": then, "declared": now_said})
    return found


def declared_face(root: Path, conductor, team: dict) -> dict:
    """-> the front matter of `TEAM.md` as start's own judge read it, what the next start writes: the members and
    their paths in the order declared -- each with `born` (an instance stands at its path) and the `packages` a season
    without `--package` gives it (`season_set`: the packages the team requires on, every other pin off), born or not --,
    the root, the edges, the principals, the limits of `TEAM.md` alone, the schedule, the ceremonies' lines, the
    entries, the work -- the intention and the digest left to the text."""
    silent = [{"name": name, "on": state == "on"} for name, state in set_of(season_set(root, conductor, {})).items()]
    return {"agents": [{"member": member, "path": path,
                        "born": conductor.instance.is_instance(agent_meta(root, path)), "packages": silent}
                       for member, path in team["agents"].items()],
            "root": team["root"], "reports": team["reports"], "principals": team["principals"],
            "limits": team["limits"], "schedule": team["schedule"],
            "ceremonies": [one["text"] for one in team["ceremonies"]], "entries": team["entries"], "work": team["work"]}


def packages_at(root: Path, conductor, path: str, run: str | None = None, season: dict | None = None) -> dict:
    """-> `{born, packages [{name, on}]}` for the agent at `path`: born, the packages its instance pins beyond its
    base as `run` plays them -- the run's own switches over its SETTINGS, their dependents with them, read on the
    engine's faces as `agent status` reads them, the run's slot set into the play for the reading and taken out
    after; without a run, the `season`'s set (`season_played`: what its next opening gets, every pin named) --; not
    born yet, the house's pins beyond its base under the season's set."""
    instance, persistence, meta = conductor.instance, conductor.persistence, agent_meta(root, path)
    season = dict(season or {})
    if not instance.is_instance(meta):
        base = instance.base_of(root)
        return {"born": False, "packages": [{"name": name, "on": season.get(name, "on") == "on"}
                                            for name in instance.pins(root) if name != base]}
    slot = persistence.slot_of(meta, run) if run else None
    instance.play_switches(meta, persistence.switches_of(slot) if slot is not None and slot.is_file() else season)
    try:
        off = instance.switched_off(meta)
    finally:
        instance.play_switches(meta, {})
    base = instance.base_of(meta)
    return {"born": True, "packages": [{"name": name, "on": name not in off}
                                       for name in instance.pins(meta) if name != base]}


def declaration_verb(rest: list[str]) -> int:
    """`team declaration <name> [--json]`: the team's declaration READ -- `TEAM.md` whole, start's own
    judge's verdict (`ok`, or the refusal `start` would write: said, never refused) and its gap to the
    last start, key by key. Nothing written, no lock, never a tick."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    as_json = flags(rest, STATUS_FLAGS)["json"]
    path = team_doc(root, name)
    if not path.is_file():
        refuse(f"team-unknown -- no {path}: the owner declares the team there.")
    data = path.read_bytes()
    team, refusal = None, None
    try:
        team = judged(conductor, conductor.reading.read(path).front, data, path, name)
    except conductor.Refusal as reading:
        refusal = f"team-invalid -- {path}: {reading}"
    except Declined as declining:
        refusal = str(declining)
    replayed = state_of(journal_of(root, name))
    started = replayed["started"]
    pending = None if team is None else ([] if started is None else gap(started, team))
    changed = bool(started) and changed_since_start(root, name, started)
    shown_path = str(path.relative_to(root.parent))
    text = data.decode("utf-8")
    if as_json:
        print(json.dumps({"team": name, "name": team_name(root, conductor, name), "path": shown_path, "text": text,
                          "digest": hashlib.sha256(data).hexdigest()[:12],
                          "verdict": {"ok": team is not None, "refusal": refusal},
                          "started": None if started is None else {"at": started.get("at"), "id": started.get("id"),
                                                                    "digest": started.get("digest")},
                          "changed": changed, "pending": pending,
                          "declared": None if team is None else declared_face(root, conductor, team)},
                         ensure_ascii=False))
        return 0
    print(f"pp-team: {shown_path}")
    print(harmless(text.rstrip("\n")))
    print("verdict ok" if team is not None else f"verdict refused: {refusal}")
    if started is None:
        print("not started")
    elif pending:
        print(f"pending until a new start (#{started.get('id')}):")
        for one in pending:
            print(f"  {one['key']}: {json.dumps(one['started'], ensure_ascii=False)} -> "
                  f"{json.dumps(one['declared'], ensure_ascii=False)}")
    elif changed:
        print(f"changed since the start (#{started.get('id')}): the body alone, served already")
    elif team is not None:
        print(f"unchanged since the start (#{started.get('id')})")
    return 0


# --- the journal: the team's one truth ----------------------------------------------------

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


PLAIN = ("started", "tasks", "done", "intents", "launched", "stops", "limits", "deferred",
         "delegations", "schedule", "cost", "budget_spent", "seen", "rung", "ends", "fails", "last",
         "seasons", "paused", "routed", "flow", "standing", "deleting", "recurrences", "silences",
         "context")   # the JSON-ready parts
PER_TASK = ("waits", "last_delegation", "wait_met")      # keyed by (agent, task): packed as rows


def packed(state: dict) -> dict:
    """-> the replayed state as JSON data, for ONE `snapshot` event: sets and tuples become
    lists, tuple keys and integer keys become rows (JSON would turn an integer key into its
    digits, and a reader asking by the id would find nothing). The messages of RESOLVED
    tasks are PRUNED unless the owner's box still reads them (a post to the owner, a post
    returned): no reader replays them -- the inboxes filter resolved tasks out, a reply cites
    an open task's post -- and the pruning is what makes a long journal's state light."""
    owner = str((state["started"] or {}).get("owner"))
    resolved = {task_id for task_id, one in state["tasks"].items() if one.get("state") == "resolved"}
    kept = {key: value for key, value in state["messages"].items()
            if value.get("task") not in resolved or value.get("to") == owner or key in state["returned"]}
    return {**{key: state[key] for key in PLAIN},
            **{key: [[agent, task, value] for (agent, task), value in state[key].items()] for key in PER_TASK},
            "messages": {str(key): value for key, value in kept.items()},
            "returned_to": [[key, to] for key, to in state["returned_to"].items()],
            "delivered": sorted(state["delivered"]),
            "ended": sorted(state["ended"]),
            "failures": [[agent, task, count] for (agent, task), count in state["failures"].items()],
            "terminals": sorted([agent, task] for agent, task in state["terminals"]),
            "runs": [[member, carrier, run] for member, held in state["runs"].items() for carrier, run in held.items()],
            "returned": sorted(state["returned"]),
            "killed": sorted(state["killed"]),
            "kills": sorted([agent, task] for agent, task in state["kills"]),
            "launches_spent": sorted(one for one in state["launches_spent"] if one is not None),
            "reset": dict(state["reset"]),
            "resumed": dict(state["resumed"]),
            "fell": sorted([agent, task] for agent, task in state["fell"]),
            "debts": [[key, value] for key, value in state["debts"].items()],
            "health": {member: dict(one) for member, one in state["health"].items()},
            "house": sorted(state["house"])}


def per_task(data: dict, key: str) -> dict:
    """-> one of the states keyed by (agent, task), from its rows -- or from the map keyed by
    agent a snapshot of team 0.11 or before kept, each entry given the task it was about."""
    kept = data.get(key) or []
    if isinstance(kept, list):
        return {(agent, task): value for agent, task, value in kept}
    tasks = {one.get("id"): one.get("task") for one in data.get("delegations") or []}
    last = data.get("last_delegation") or {}
    found = {}
    for agent, value in kept.items():
        if key == "waits":
            found[(agent, value.get("task"))] = value
        else:
            found[(agent, tasks.get(value if key == "last_delegation" else last.get(agent)))] = value
    return found


def unpacked(data: dict) -> dict:
    """-> the state a `snapshot` event kept, back in its working types; a key a snapshot of an earlier
    version did not keep takes its empty value."""
    empty = {"fails": [], "routed": {}, "flow": {}, "standing": {}, "deleting": False, "recurrences": {}, "silences": [],
             "context": {}}
    return {**{key: data.get(key, empty.get(key)) for key in PLAIN},
            "limits": {RETIRED_LIMITS.get(key, key): value                # a snapshot of before (team 0.39.0): its
                       for key, value in (data.get("limits") or {}).items()},   # bounds counted wake-ups
            **{key: per_task(data, key) for key in PER_TASK},
            "messages": {int(key): value for key, value in (data.get("messages") or {}).items()},
            "returned_to": {int(key): to for key, to in (data.get("returned_to") or [])},
            "delivered": set(data.get("delivered") or []),
            "ended": set(data.get("ended") or []),
            "failures": {(agent, task): count for agent, task, count in (data.get("failures") or [])},
            "terminals": {(agent, task) for agent, task in (data.get("terminals") or [])},
            "runs": runs_unpacked(data.get("runs") or [], data),
            "returned": set(data.get("returned") or []),
            "killed": set(data.get("killed") or []),
            "kills": {(agent, task) for agent, task in (data.get("kills") or [])},
            "launches_spent": set(data.get("launches_spent") or data.get("wakes_spent") or []),   # `wakes_spent`: a snapshot of before
            "reset": dict(data.get("reset") or {}),
            "resumed": dict(data.get("resumed") or {}),
            "fell": {(agent, task) for agent, task in (data.get("fell") or [])},
            "debts": ({int(key): value for key, value in data["debts"]} if "debts" in data
                      else debts_rebuilt(data)),
            "health": {member: dict(one) for member, one in (data.get("health") or {}).items()},
            "house": set(data.get("house") or [])}


def debts_rebuilt(data: dict) -> dict:
    """-> the debts a snapshot of team 0.32.2 or before did not keep, rebuilt from the messages it kept: a
    `do` or an `ask` to a member on an open task owes until an answer of its member cites it."""
    messages = {int(key): value for key, value in (data.get("messages") or {}).items()}
    agents = ((data.get("started") or {}).get("agents") or {})
    open_tasks = {key for key, one in (data.get("tasks") or {}).items() if one.get("state") == "open"}
    debts: dict = {}
    state = {"messages": {}, "started": data.get("started")}
    for key in sorted(messages):
        one = messages[key]
        state["messages"][key] = one
        if one.get("verb") in ("do", "ask") and one.get("to") in agents and one.get("task") in open_tasks:
            debts[key] = None
        cited = cited_of(state, one)
        if cited is not None and debts.get(cited, "x") is None and messages[cited].get("to") == one.get("from"):
            debts[cited] = key
    return debts


def runs_unpacked(rows: list, data: dict) -> dict:
    """-> the runs each member holds by CARRIER, from a snapshot's rows `[member, carrier, run]`; a row
    `[member, run]` of team 1.0.0 goes to the carrier of the task of the member's last intent."""
    found: dict = {}
    for row in rows:
        if len(row) == 3:
            found.setdefault(row[0], {})[row[1]] = row[2]
            continue
        last = max((one for one in (data.get("intents") or {}).values() if one.get("agent") == row[0]),
                   key=lambda one: int(one.get("id") or 0), default=None)
        if last is not None:
            found.setdefault(row[0], {})[carrier_of(data, last.get("task"))] = row[1]
    return found


def carrier_of(state: dict, task: str | None) -> str | None:
    """-> the CARRIER of a task, what a member's run is kept by: an occurrence's recurrence, a ring's
    ceremony, any other task itself."""
    held = (state.get("tasks") or {}).get(task) or {}
    return held.get("recurrence") or held.get("ceremony") or task


def run_held(state: dict, member: str, task: str | None) -> str | None:
    """-> the run the member holds for the task's carrier, None before its first wake-up there."""
    return (state["runs"].get(member) or {}).get(carrier_of(state, task))


def carrier_name(state: dict, team: str, carrier: str) -> str:
    """-> the name a run of the carrier carries: a recurrence's name, else `<team> R<n>`; a task's name, else
    `<team> T<n>`; a ceremony's; cut at the run name's bound."""
    recurrence = state["recurrences"].get(carrier)
    task = state["tasks"].get(carrier)
    if recurrence is not None:
        text = recurrence.get("name") or f"{team} {carrier}"
    elif task is not None:
        text = task.get("name") or f"{team} {carrier}"
    else:
        text = carrier
    return " ".join(str(text).split())[:RUN_NAME_CHARS].strip()


def tailed(path: Path) -> list[dict]:
    """-> the journal's events FROM its last `snapshot` line on (found by a text scan and
    verified by a parse), or all of them when none stands -- the read a state needs: the
    lines before the snapshot are never parsed."""
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8")
    at = raw.rfind('"kind": "snapshot"')
    while at >= 0:
        start = raw.rfind("\n", 0, at) + 1
        end = raw.find("\n", at)
        try:
            candidate = json.loads(raw[start:] if end < 0 else raw[start:end])
        except ValueError:
            candidate = None
        if isinstance(candidate, dict) and candidate.get("kind") == "snapshot":
            found = []
            lines = raw[start:].splitlines()
            for number, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    found.append(json.loads(line))
                except ValueError:
                    if number == len(lines):
                        continue
                    refuse(f"line {number} of the journal's tail is not a record -- this script is "
                           "the only writer, the file is not for hand edits.")
            return found
        at = raw.rfind('"kind": "snapshot"', 0, at)   # the match was a text's: scan on
    return lines_of(path)


def state_of(path: Path) -> dict:
    """-> the team's state, read from the last snapshot on: what every judge and every
    status reads -- `lines_of` whole stays the historians' (`log`, `watch`, `of_task`)."""
    return replay(tailed(path))


def cited_of(state: dict, one: dict) -> int | None:
    """-> the id of the message a post ANSWERS, or None: a `re` cites it, a principal's `reply` too; in a journal
    written before team 0.33.0 a member's `reply` cites the ask it answered, and its `done` or `escalate` to the
    member that delegated answers that member's last `do` to it on the task."""
    verb = one.get("verb")
    if verb == "re":
        return one.get("re")
    if verb == "reply":
        return one.get("reply")
    if verb in ("done", "escalate") and is_member(state, one.get("to")):
        dos = [key for key, message in state["messages"].items()
               if message.get("verb") == "do" and message.get("from") == one.get("to")
               and message.get("to") == one.get("from") and message.get("task") == one.get("task") and key < one["id"]]
        return max(dos) if dos else None
    return None


def opening_of(state: dict, task: str) -> int | None:
    """-> the task's OPENING message: the first `do` its author posted to its member -- what the member that
    holds the task answers to close it. None when the journal holds none (a ceremony rung before team 0.33.0)."""
    held = state["tasks"].get(task) or {}
    return next((key for key in held.get("messages") or []
                 if (state["messages"].get(key) or {}).get("verb") == "do"
                 and state["messages"][key].get("from") == held.get("from")
                 and state["messages"][key].get("to") == held.get("to")), None)


def owes(state: dict, key) -> bool:
    """-> whether the message's debt stands: a `do` or an `ask` delivered to a member, no answer of its yet."""
    return state["debts"].get(key, "x") is None


def is_notice(state: dict, one: dict) -> bool:
    """-> whether a post is a NOTICE of the team to a principal: a `notice`, or an `escalate` to a principal in a journal
    written before team 0.36.0."""
    return one.get("verb") == "notice" or (one.get("verb") == "escalate" and not is_member(state, one.get("to")))


def notice_about(state: dict, one: dict) -> str | None:
    """-> the member a notice concerns -- its `about`, or the member that wrote an `escalate` to a principal before team
    0.36.0 --; None for a guard's notice."""
    if one.get("verb") == "notice":
        return one.get("about")
    return one.get("from") if is_member(state, one.get("from")) else None


def answered_by_principal(state: dict) -> set:
    """-> the ids a principal's answer cites: its `re`, or its `reply` written before team 0.36.0."""
    return {cited_of(state, one) for one in state["messages"].values()
            if one.get("verb") in ("re", "reply") and is_principal(state, one.get("from"))} - {None}


def worded(state: dict, one: dict) -> dict:
    """-> a post as the faces say it, in the words of the debt: a member's `done`, `reply` or `escalate` to a member,
    and a principal's `reply`, written before team 0.36.0, said `re` to the message it answers (`cited_of`; a `done` to a
    principal answers the task's opening) with `was` its verb; an `escalate` to a principal said as the team's `notice`,
    `about` the member that wrote it; a `note` written before team 0.47.0 said `info`; any other post as it is."""
    verb = one.get("verb")
    if verb == "note":                                           # the principal's note until team 0.47.0: an info
        return {**{key: value for key, value in one.items() if key != "verb"}, "verb": "info", "was": verb}
    if verb not in RETIRED_VERBS:
        return one
    rest = {key: value for key, value in one.items() if key not in ("verb", "reply")}
    if verb == "escalate" and not is_member(state, one.get("to")):
        about = one.get("from") if is_member(state, one.get("from")) else None
        return {**rest, "verb": "notice", "from": (state["started"] or {}).get("team") or one.get("team"),
                **({"about": about} if about else {}), "was": verb}
    cited = cited_of(state, one)
    if cited is None and verb == "done":
        cited = opening_of(state, one.get("task"))
    return {**rest, "verb": "re", "re": cited, "was": verb}


def said_so_far() -> dict:
    """-> what a reader of the journal keeps of the events it read, to say the next ones (`read_on`)."""
    return {"started": None, "messages": {}, "tasks": {}}


def read_on(context: dict, one: dict) -> dict | None:
    """-> one event as `log` and `watch` say it, `context` -- what the events before it said -- kept up to date: a post
    in the words of the debt (`worded`), None for an event no version writes any more (`DEAD`), any other as it is."""
    kind = one.get("kind")
    if kind == "team-started":
        context["started"] = one
    elif kind == "task":
        context["tasks"][one["task"]] = {"from": one.get("from"), "to": one.get("to"), "messages": []}
    elif kind == "post":
        held = context["tasks"].get(one.get("task"))
        if held is not None and one["id"] not in context["messages"]:
            held["messages"].append(one["id"])
        context["messages"][one["id"]] = one
        return worded(context, one)
    return None if kind in DEAD else one


def replay(events: list[dict]) -> dict:
    """-> the team's STATE, computed from its journal alone: the last `team-started`, the tasks
    with their state and their messages, every message by its id, the messages delivered (the
    ones an intent carried, the ones returned, a stop to an agent whose wake-up was killed), the
    intents and their launches, ends, failures and kills, the terminals, the delegations, the
    runs each member holds, ONE per CARRIER of its tasks (`carrier_of`) -- the last that answered there, readable or not --, the waits declared
    (`await`), the last delegation and the waits met -- each by (member, task) --, the stops posted
    to each agent, the results, the owner's cursor (`inbox-seen`), the members `team reset` took
    their run from (`run-reset`, the member's run dropped), the (member, task) whose terminal a final
    failure wrote, the starts counted (`seasons` -- each a SEASON: its limits TEAM.md's under the season's own,
    the cost, `budget-spent` and `launches-spent` afresh, the members' runs kept), the bounds `team budget` raised (`budget-raised`: the limits raised, `budget_spent`
    lifted), and the last `resumed` of each task -- `team resume` opens the task again, sets its
    members' failures to zero, drops the terminals its final failures wrote and lifts `launches-spent`:
    the task's counters count from there. A journal written by team 0.39.0 counted wake-ups: its
    `team-started.limits` and `season` keys `launches` and `budget-launches` are read as `launches` and
    `budget-launches`, its `wakes-spent` as `launches-spent`, its `budget-raised {wakes}` as `{launches}`;
    nothing is written under those names again. The run a failed launch leaves: `wake-failed {state}`, read at
    agent's face, says whether it STANDS (relaunched while its retries last) or is parked; a final failure stands
    nobody. A `stop` posted to an agent whose run stands on the task is not delivered at once: it rides the head
    of one more launch (`dues`). A ceremony's task rung at hand keeps who rang it (`by`, from
    its `ceremony-due`). The team is PAUSED from a `paused` to its `unpaused` (`paused` `{by, at, id}`,
    else None). Each task keeps its `text` and its `last` event `{id, kind, at}` -- the last
    event that belongs to it (`task_of`). The DEBTS: each `do` or `ask` posted to a member on an open
    task opens one (`None`), the first answer of that member that cites it settles it (the answer's id;
    `closed` when the task resolves); the delegations are the `do`s between members, and a member is
    TERMINAL on a task once its last `do` there is answered -- by it, or in its place after a final failure
    (`delegation` and `terminal` events of a journal written before team 0.33.0 read the same). A `launch-missing` counts no failure: nothing was launched. A
    post to a principal is delivered at its writing: the principal's box reads it, and it is
    never returned. A task stops by its `stopped` event, whatever holds it (a `stop` post stops
    it too: a journal written before the event). The HEALTH of each member (`health`, the failure detector
    ◇P): `falls` its final failures in a row since it last answered -- on a task not stopped, a `budget-share`
    apart -- and `at` the hour of the last, the member SUSPECTED while `falls` stands; a launch the HOUSE refused
    (`wake-failed {house: true}`, never final) counts no failure and no fall (`house`: its tags); a wake-up that ends
    answered makes a suspected member REPENT (`falls` back to 0, its failures counted afresh, `repents` one
    more: one silent retry more); `team resume --task` ends the suspicion of the task's members, a season ends
    every suspicion. A `silence {agent, task, exchanges}` the tick wrote (row 115) is a fall too (`cause: silence`),
    lifted by a routed act of the member alone -- never by a launch that ends saying nothing. The tick's
    answer in a suspected member's place (`suspected`) delivers the message it answers. The RECURRENCES the owner posted
    (`recurrence {R<n>}`) keep the periods they sounded -- by an occurrence, a task that carries `recurrence` and
    `period`, or by a `recurrence-skipped` --, their last occurrence and their stop (`recurrence-stopped`); a
    `recurrence-changed` replaces its `when` and its `since`, its context limit (`context`) or its text, the periods
    sounded kept: a period is its date, counted once; a recurrence born of a task (`recurrence {task}`) has that task
    for its last occurrence; a `run-renewed` detaches the run it names from its recurrence -- the member's
    next wake-up there opens a new one. Each member's CONTEXT is the `context` of its last `wake-ended` (`None` without one, or for a journal written
    before team 0.54.0)."""
    state: dict = {"started": None, "tasks": {}, "messages": {}, "delivered": set(),
                   "intents": {}, "launched": {}, "ended": set(), "failures": {}, "terminals": set(),
                   "delegations": [], "runs": {}, "done": {}, "returned": set(),
                   "wait_met": {}, "last_delegation": {}, "schedule": True,
                   "limits": {}, "cost": 0.0, "budget_spent": False, "deferred": [], "returned_to": {},
                   "waits": {}, "killed": set(), "kills": set(), "stops": {}, "seen": 0,
                   "launches_spent": set(), "rung": {}, "ends": [], "fails": [], "last": None, "reset": {},
                   "resumed": {}, "fell": set(), "seasons": 0, "paused": None, "debts": {}, "health": {},
                   "routed": {}, "flow": {}, "standing": {}, "house": set(), "deleting": False, "recurrences": {},
                   "silences": [], "context": {}}
    floor = 0
    rung_by: dict = {}
    snap = next((one for one in reversed(events) if one.get("kind") == "snapshot"), None)
    if snap is not None:                           # the replay restarts at the LAST snapshot
        state = unpacked(snap.get("state") or {})
        floor = int(snap.get("upto") or 0)
    for one in events:
        kind = one.get("kind")
        if kind == "snapshot" or int(one.get("id") or 0) <= floor:
            continue
        state["last"] = {"id": one.get("id"), "kind": kind, "at": one.get("at")}
        if kind == "team-started":                        # a season: the counts afresh, the runs kept
            state["started"] = one
            state["seasons"] = int(state.get("seasons") or 0) + 1
            state["schedule"] = True
            state["limits"] = {RETIRED_LIMITS.get(key, key): value for key, value in {
                **dict(one.get("limits") or {}),
                **{key: value for key, value in (one.get("season") or {}).items() if value is not None}}.items()}
            state["cost"], state["budget_spent"] = 0.0, False
            state["launches_spent"] = set()
            state["health"] = {}                          # nobody suspected at a season's start
        elif kind == "task":
            state["tasks"][one["task"]] = {"id": one["task"], "from": one.get("from"), "to": one.get("to"),
                                           "text": one.get("text"), "state": "open", "messages": [],
                                           "ceremony": one.get("ceremony"), "period": one.get("period"),
                                           "name": one.get("name"), "at": one.get("at"), "ended": None,
                                           "recurrence": one.get("recurrence")}
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:                    # an occurrence: its period sounded
                recurrence["sounded"].append(one.get("period"))
                recurrence["last"] = one["task"]
            if one.get("ceremony") and rung_by.get((one["ceremony"], one.get("period"))):
                state["tasks"][one["task"]]["by"] = rung_by[(one["ceremony"], one.get("period"))]
        elif kind == "post":
            state["messages"][one["id"]] = one
            task = state["tasks"].get(one.get("task"))
            if task is not None:
                task["messages"].append(one["id"])
            verb, to = one.get("verb"), one.get("to")
            if verb == "do" and is_member(state, to):
                if is_member(state, one.get("from")):     # a delegation is the do itself
                    state["delegations"].append({"id": one["id"], "from": one["from"], "to": to,
                                                 "task": one.get("task")})
                    state["last_delegation"][(one["from"], one.get("task"))] = one["id"]
                state["terminals"].discard((to, one.get("task")))   # a new round for that member
            if verb in ("do", "ask") and is_member(state, to) and task is not None and task["state"] == "open":
                state["debts"][one["id"]] = None          # one debt, open until its first answer
            cited = cited_of(state, one)
            if cited is not None and owes(state, cited) and state["messages"][cited].get("to") == one.get("from"):
                state["debts"][cited] = one["id"]         # the first answer settles it
                if state["messages"][cited].get("verb") == "do":
                    state["terminals"].add((one.get("from"), one.get("task")))
                if one.get("verb") == "stop" and task["state"] == "open":
                    task["state"], task["ended"] = "stopped", one.get("at")
            if one.get("suspected") and cited is not None:  # answered in a suspected member's place: delivered
                state["delivered"].add(cited)
            if one.get("verb") == "stop":                 # delivered at once -- but to a run STANDING on the task:
                state["stops"].setdefault(one.get("to"), []).append(one["id"])   # the head of one more launch
                if state["standing"].get(one.get("to")) != one.get("task"):
                    state["delivered"].add(one["id"])
            elif is_principal(state, one.get("to")):      # delivered at once: the principal's box reads it
                state["delivered"].add(one["id"])
            if is_member(state, one.get("from")) and one.get("by") != "tick":   # an act of a member suspected by
                health = state["health"].get(one.get("from")) or {}        # silence lifts it: it repents (row 115)
                if health.get("falls") and health.get("cause") == "silence":
                    health.update({"falls": 0, "repents": int(health.get("repents") or 0) + 1})
        elif kind == "silence":                           # the member's silence fell: a fall of the detector (row 115)
            state["silences"].append(one)
            health = state["health"].setdefault(one.get("agent"), {"falls": 0, "repents": 0})
            health.update({"falls": int(health.get("falls") or 0) + 1, "at": one.get("at"), "cause": "silence"})
        elif kind == "stopped":
            task = state["tasks"].get(one.get("task"))
            if task is not None and task["state"] == "open":
                task["state"], task["ended"] = "stopped", one.get("at")
        elif kind == "wake-intent":
            state["intents"][one["tag"]] = one
            state["delivered"].update(one.get("messages") or [])
        elif kind == "wake-launched":
            state["launched"][one["tag"]] = one
        elif kind == "wake-routed" or kind == "wake-refused":   # an act read at the flow: the rank reached
            state["routed"][one["tag"]] = max(int(state["routed"].get(one["tag"]) or 0), int(one.get("line") or 0))
        elif kind == "wake-ended":
            state["ended"].add(one["tag"])
            state["ends"].append(one)
            charged(state, one)
            intent = state["intents"].get(one["tag"])
            if intent is not None:                          # the context its exchange left, null unmeasured
                state["context"][intent["agent"]] = one.get("context")
            if intent is not None and one.get("run"):       # the run that answered is the carrier's
                state["runs"].setdefault(intent["agent"], {})[carrier_of(state, intent.get("task"))] = one["run"]
                if one.get("flow") is not None:
                    state["flow"][str(one["run"])] = int(one["flow"])
                if one.get("state") == "standing":          # the run waits for a production: relaunched
                    state["standing"][intent["agent"]] = intent.get("task")
                else:
                    state["standing"].pop(intent["agent"], None)
            health = state["health"].get((intent or {}).get("agent")) or {}
            if health.get("falls") and health.get("cause") != "silence":   # a fallen member answered: it repents;
                #                                              a silence is lifted by an act of its alone (row 115)
                health.update({"falls": 0, "repents": int(health.get("repents") or 0) + 1})
                for slot in [slot for slot in state["failures"] if slot[0] == intent["agent"]]:
                    del state["failures"][slot]
        elif kind == "wake-failed":
            state["ended"].add(one["tag"])
            state["fails"].append(one)
            charged(state, one)
            intent = state["intents"].get(one["tag"])
            if intent is not None and one.get("run"):       # a launch that failed: its run stays the carrier's
                state["runs"].setdefault(intent["agent"], {})[carrier_of(state, intent.get("task"))] = one["run"]
            launched_run = (state["launched"].get(one["tag"]) or {}).get("run") or one.get("run")
            if launched_run and one.get("flow") is not None:   # the flow of a dead launch is read: never again
                state["flow"][str(launched_run)] = int(one["flow"])
            if one.get("house"):                            # the house refused the launch: the member did nothing
                state["house"].add(one["tag"])
            if intent is not None:
                slot = (intent["agent"], intent["task"])
                if one.get("reason") != "launch-missing" and not one.get("house"):   # the agent's retries count what it did
                    state["failures"][slot] = state["failures"].get(slot, 0) + 1
                if one.get("state") == "standing" and not one.get("final"):   # the run stands: relaunched
                    state["standing"][intent["agent"]] = intent.get("task")
                elif one.get("state") is not None or one.get("final"):      # parked, or its retries spent
                    state["standing"].pop(intent["agent"], None)
                if one.get("final") and (state["tasks"].get(intent["task"]) or {}).get("state") != "stopped":
                    state["fell"].add(slot)                     # its terminal is the failure's
                    state["terminals"].add(slot)
                    health = state["health"].setdefault(intent["agent"], {"falls": 0, "repents": 0})   # SUSPECTED
                    health.update({"falls": int(health.get("falls") or 0) + 1, "at": one.get("at"), "cause": "fall"})
                for mid in intent.get("messages") or []:    # a retry sends them again; a final failure keeps them
                    if one.get("final"):
                        state["delivered"].add(mid)
                    else:
                        state["delivered"].discard(mid)
        elif kind == "wake-killed":
            state["ended"].add(one["tag"])
            state["killed"].add(one["tag"])
            state["kills"].add((one["agent"], one.get("task")))
        elif kind == "terminal":
            state["terminals"].add((one["agent"], one["task"]))
        elif kind == "delegation":                        # written before team 0.33.0: its do counts
            pass
        elif kind == "wait":
            state["waits"][(one["agent"], one.get("task"))] = {"any": one.get("any"), "to": list(one.get("to") or []),
                                                               "task": one.get("task"), "id": one["id"]}
        elif kind == "wait-met":
            state["wait_met"][(one["agent"], one.get("task"))] = one["id"]
        elif kind == "done":
            state["done"][one["task"]] = one
            task = state["tasks"].get(one["task"])
            if task is not None:
                task["state"], task["ended"] = "resolved", one.get("at")
                state["terminals"].add((task["to"], one["task"]))
            for key, settled in list(state["debts"].items()):
                if settled is None and (state["messages"].get(key) or {}).get("task") == one["task"]:
                    state["debts"][key] = "closed"        # the root's answer settles every debt of the task
        elif kind == "returned":
            state["returned"].add(one["message"])
            state["returned_to"][one["message"]] = one.get("to")
            state["delivered"].add(one["message"])
        elif kind == "schedule-off":
            state["schedule"] = False
        elif kind == "budget-spent":
            state["budget_spent"] = True
        elif kind == "budget-raised":                     # `team budget` raised a bound: spent no more
            if one.get("budget") is not None:
                state["limits"]["budget"] = float(one["budget"])
            raised = one.get("launches", one.get("wakes"))     # `wakes`: the field of before (team 0.39.0)
            if raised is not None:
                state["limits"]["budget-launches"] = int(raised)
            state["budget_spent"] = False
        elif kind in ("launches-spent", "wakes-spent"):      # `wakes-spent`: the kind of before (team 0.39.0)
            state["launches_spent"].add(one.get("task"))
        elif kind == "ceremony-due":
            state["rung"].setdefault(str(one.get("ceremony")), []).append(str(one.get("period")))
            if one.get("by"):                             # a ring at hand: its task, written next, keeps who rang
                rung_by[(one.get("ceremony"), one.get("period"))] = one["by"]
        elif kind == "deferred":
            state["deferred"].append(one)
        elif kind == "inbox-seen":
            state["seen"] = int(one.get("upto") or 0)
        elif kind == "run-reset":                         # `team reset` forgot one run of the member
            held = state["runs"].get(one.get("member")) or {}
            for carrier in [carrier for carrier, run in held.items() if run == one.get("run")]:
                del held[carrier]
            state["standing"].pop(one.get("member"), None)
            state["reset"][one.get("member")] = one["id"]
        elif kind == "paused":                            # `team pause`: nobody woken, nothing rung
            state["paused"] = {"by": one.get("by"), "at": one.get("at"), "id": one.get("id")}
        elif kind == "unpaused":                          # `team resume` without a task: the team back
            state["paused"] = None
        elif kind == "deleting":                          # `team delete --yes`: the team lives no more
            state["deleting"] = True
        elif kind == "recurrence":                        # `team post --every`: a task that comes back
            state["recurrences"][one["recurrence"]] = {
                "id": one["recurrence"], "from": one.get("from"), "to": one.get("to"), "text": one.get("text"),
                "name": one.get("name"), "when": one.get("when"), "since": one.get("since"), "at": one.get("at"),
                "context": one.get("context"), "first": 0, "stopped": None, "sounded": [], "task": one.get("task"),
                "last": one.get("task")}                  # a recurrence born of a task: its origin its last occurrence
        elif kind == "recurrence-skipped":                # the occurrence before still open: the period sounded
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:
                recurrence["sounded"].append(one.get("period"))
        elif kind == "recurrence-stopped":                # `team stop --recurrence`
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:
                recurrence["stopped"] = {"by": one.get("by"), "at": one.get("at"), "id": one.get("id")}
        elif kind == "recurrence-changed":                # `team recurrence`: what it carries replaced, the periods kept
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None and "when" in one:       # a duration a change gives: its first slot one later
                recurrence["when"], recurrence["since"] = one.get("when"), one.get("since")
                recurrence["first"] = 1
            if recurrence is not None and "context" in one:
                recurrence["context"] = one["context"]
            if recurrence is not None and "text" in one:       # the occurrences to come open with it
                recurrence["text"] = one["text"]
        elif kind == "run-renewed":                       # the recurrence's run past its limit: detached from it
            held = state["runs"].get(one.get("member")) or {}
            if held.get(one.get("recurrence")) == one.get("run"):
                del held[one.get("recurrence")]
        elif kind == "resumed":                           # `team resume` took the task back
            task = state["tasks"].get(one.get("task"))
            if task is not None and task["state"] == "stopped":
                task["state"], task["ended"] = "open", None
            state["resumed"][one.get("task")] = one["id"]
            state["launches_spent"].discard(one.get("task"))
            for slot in [slot for slot in state["failures"] if slot[1] == one.get("task")]:
                del state["failures"][slot]
            for slot in [slot for slot in state["fell"] if slot[1] == one.get("task")]:
                state["fell"].discard(slot)
                state["terminals"].discard(slot)
            for member in members_of(state, one.get("task")):   # the owner trusts them again
                if (state["health"].get(member) or {}).get("falls"):
                    state["health"][member]["falls"] = 0
        task = state["tasks"].get(task_of(state, one))
        if task is not None:
            task["last"] = {"id": one.get("id"), "kind": kind, "at": one.get("at")}
    return state


def charged(state: dict, one: dict) -> None:
    """Adds the cost a wake-up's end carries to the team's season and to the task of its intent (`cost` of the
    task, kept with the task through every season and every snapshot)."""
    cost = one.get("cost")
    if not isinstance(cost, (int, float)) or isinstance(cost, bool):
        return
    state["cost"] += float(cost)
    task = state["tasks"].get((state["intents"].get(one.get("tag")) or {}).get("task"))
    if task is not None:
        task["cost"] = float(task.get("cost") or 0.0) + float(cost)


def task_of(state: dict, one: dict) -> str | None:
    """-> the task an event belongs to, as `log --task` keeps it (`of_task`): the task it names, or
    the task of the intent its `tag` names -- a launch, an end, a failure of a wake-up."""
    if one.get("task"):
        return one["task"]
    return (state["intents"].get(one.get("tag")) or {}).get("task") if one.get("tag") else None


def members_of(state: dict, task: str | None) -> list[str]:
    """-> the members a task concerns: the one that holds it, those a message on it was posted to, those woken
    on it."""
    held = state["tasks"].get(task) or {}
    found = [held.get("to")] + [one.get("to") for one in state["messages"].values() if one.get("task") == task]
    found += [one.get("agent") for one in state["intents"].values() if one.get("task") == task]
    return [one for one in dict.fromkeys(found) if is_member(state, one)]


def open_intents(state: dict) -> list[dict]:
    """-> the intents without an end: the wake-ups under way, in the journal's order."""
    return [one for tag, one in state["intents"].items() if tag not in state["ended"]]


def reserved_of(state: dict) -> float:
    """-> the money the wake-ups under way may still spend: the allowances of the intents without an
    end since the last `team-started`."""
    since = int((state["started"] or {}).get("id") or 0)
    return round(sum(float(one.get("allowance") or 0) for one in open_intents(state)
                     if int(one.get("id") or 0) > since), 6)


def share_of(state: dict) -> dict | None:
    """-> the team's budget as the faces say it, `{cap, spent, reserved, left}`: `left` the rest no wake-up
    holds, below 0 when the last ones went past; None without `budget:`."""
    cap = state["limits"].get("budget")
    if cap is None:
        return None
    reserved = reserved_of(state)
    return {"cap": float(cap), "spent": round(state["cost"], 6), "reserved": reserved,
            "left": round(float(cap) - state["cost"] - reserved, 6)}


def allowance_of(state: dict, started: dict) -> float | None:
    """-> the money a wake-up launched now may spend: its PART of the team's rest, min((budget - the cost
    kept) / k, the rest no wake-up under way holds) -- k the wake-ups that may play together, min(`parallel`,
    the members), the members without `parallel:` --, down to the micro-dollar; None without `budget:`."""
    share = share_of(state)
    if share is None:
        return None
    members = max(1, len(started.get("agents") or {}))
    parallel = state["limits"].get("parallel")
    k = members if parallel is None else max(1, min(int(parallel), members))
    part = min((share["cap"] - share["spent"]) / k, share["left"])
    return math.floor(part * 1e6) / 1e6


def measured(root: Path, conductor, started: dict) -> bool:
    """-> whether the adapter of the launches' grammar declares a scope for the cost it reads (`COST`):
    the provider `team start` kept, else the one the house is wired with -- what `agent start` holds a
    run's cap by. False when none is known or the adapter refuses."""
    grammar = (started.get("launch") or {}).get("provider")
    if grammar is None:
        wired = conductor.install.wired_providers(root.parent)
        grammar = wired[0] if len(wired) == 1 else None
    if grammar is None:
        return False
    try:
        return getattr(conductor.adapters.load(str(grammar), root), "COST", None) in ("session", "launch")
    except conductor.Refusal:
        return False


def inbox(state: dict, agent: str) -> list[dict]:
    """-> the messages to `agent` that no event delivered, on tasks not resolved, in order."""
    return [one for one in state["messages"].values()
            if one.get("to") == agent and one["id"] not in state["delivered"]
            and (state["tasks"].get(one.get("task")) or {}).get("state") != "resolved"]


def is_open(state: dict, task) -> bool:
    return (state["tasks"].get(task) or {}).get("state") == "open"


def wait_open(state: dict, agent: str, task: str) -> bool:
    """-> whether the agent waits on the task: a delegate of its on that task, still open, has no
    terminal yet. Under the `await {any: n}` of its last delegating answer on that task, that
    answer's delegates count apart: the wait stays open while fewer than n of them are terminal.
    Its delegations on another task neither hold nor free this one. A delegate is terminal once it
    answered its last `do` on the task (`replay`)."""
    if not is_open(state, task):
        return False
    mine = [one for one in state["delegations"] if one["from"] == agent and one["task"] == task]
    wait = state["waits"].get((agent, task))
    if wait is None or wait["id"] < state["last_delegation"].get((agent, task), 0):
        return any((one["to"], task) not in state["terminals"] for one in mine)
    round_ = {(to, task) for to in wait["to"]}
    if sum(1 for slot in round_ if slot in state["terminals"]) < wait["any"]:
        return True
    return any((one["to"], task) not in state["terminals"] for one in mine if (one["to"], task) not in round_)


def held_by_wait(state: dict, agent: str, task: str, one: dict) -> bool:
    """-> whether a message WAITS while the member waits on the task: an answer to one of its `do`s there,
    or the task's opening -- the member answers it once its round is in. Every other message wakes it."""
    cited = cited_of(state, one)
    if cited is not None:
        answered = state["messages"].get(cited) or {}
        return answered.get("verb") == "do" and answered.get("from") == agent and answered.get("task") == task
    return one.get("id") == opening_of(state, task)


def busy(state: dict, member: str) -> bool:
    """-> whether a wake-up of the member is under way: an intent of its without an end, whatever
    its task -- a member plays one wake-up at a time, in its one run."""
    return any(one["agent"] == member and tag not in state["ended"] for tag, one in state["intents"].items())


def owed_by(state: dict, member: str) -> list[int]:
    """-> the debts the member owes, in order: each `do` or `ask` delivered to it on an open task that no
    answer of its settled yet."""
    return [key for key, one in sorted(state["messages"].items())
            if one.get("to") == member and owes(state, key) and key in state["delivered"]
            and is_open(state, one.get("task"))]


def waits_for(state: dict) -> dict[str, set[str]]:
    """-> the WAIT-FOR graph of the team, on every open task: a -> b while a `do` or an `ask` of the member a
    to the member b still owes its answer, and a -> p while an `ask` of a to the principal p, or a notice of the team to p
    about a, has no answer of p that cites it -- a notice of a silence holds no wait: the try waits for no answer
    (row 115). A principal waits on nobody."""
    answered = answered_by_principal(state)
    edges: dict[str, set[str]] = {}
    for key, one in state["messages"].items():
        to = one.get("to")
        notice = is_notice(state, one) and one.get("cause") != "silence"   # a silence notice holds no wait (row 115)
        frm = notice_about(state, one) if notice else one.get("from")
        if not is_member(state, frm) or not is_open(state, one.get("task")):
            continue
        if (owes(state, key) and is_member(state, to)) or (
                (one.get("verb") == "ask" or notice) and is_principal(state, to) and key not in answered):
            edges.setdefault(str(frm), set()).add(str(to))
    return edges


def receives(state: dict, member: str) -> bool:
    """-> whether the member has something to receive: a message the ordinary rule would deliver it now --
    one its open wait does not hold; the members' `info`s alone are nothing to receive (`quiet`)."""
    return any(loud(state, box) and not (wait_open(state, member, task)
                                         and all(held_by_wait(state, member, task, one) for one in loud(state, box)))
               for task, box in dues(state, member))


def deadlocked(state: dict) -> set[str]:
    """-> the DEADLOCKED set of the team (Chandy, Misra, Haas 1983, the communication model): the greatest set of
    IDLE members -- no wake-up under way, nothing to receive -- whose every wait stays in the set; a principal is
    in none, since it may always post. Computed from the idle members, dropping any whose wait leaves the set,
    until nothing moves."""
    edges = waits_for(state)
    members = list((state["started"] or {}).get("agents") or {})
    found = {one for one in members if not busy(state, one) and not receives(state, one)}
    moved = True
    while moved:
        moved = False
        for one in list(found):
            if any(other not in found for other in edges.get(one, ())):
                found.discard(one)
                moved = True
    return found


def reached(edges: dict[str, set[str]], member: str) -> set[str]:
    """-> every member and principal the member reaches by its waits."""
    seen, stack = set(), list(edges.get(member, ()))
    while stack:
        one = stack.pop()
        if one not in seen:
            seen.add(one)
            stack.extend(edges.get(one, ()))
    return seen


def at_bottom(state: dict, member: str) -> bool:
    """-> whether the member stands at the BOTTOM of the deadlocked set: in it, and every member it reaches by its
    waits reaches it back -- a sink (it waits for nobody) or a knot. Its answer unblocks those that wait on it."""
    if member not in deadlocked(state):
        return False
    edges = waits_for(state)
    return all(member in reached(edges, one) for one in reached(edges, member))


def principal_opening(state: dict, key: int) -> bool:
    """-> whether the debt is the opening a principal posted: never answered in its member's place."""
    message = state["messages"].get(key) or {}
    return key == opening_of(state, message.get("task")) and not is_member(state, message.get("from"))


def silence_since(state: dict, member: str, task: str) -> int:
    """-> the journal id the member's SILENCE on the task counts from: the latest of its last routed act on the task
    (a post of its, `info` included, never one the tick wrote in its place), the task's `resumed`, the season's
    `team-started`, and its last `silence` fall there."""
    acts = [key for key, one in state["messages"].items()
            if one.get("from") == member and one.get("task") == task and one.get("by") != "tick"]
    falls = [int(one.get("id") or 0) for one in state["silences"] if one.get("agent") == member and one.get("task") == task]
    return max(acts + falls + [state["resumed"].get(task, 0), int((state["started"] or {}).get("id") or 0)])


def silence_of(state: dict, member: str, task: str) -> int:
    """-> the member's SILENCE on the task (row 115): its exchanges there that ended PARKED (`wake-ended {state:
    parked}`) since `silence_since` -- the exchanges begun after its last act --; a relaunch of a standing run counts
    not. Read from the journal alone: nothing is written to count."""
    since = silence_since(state, member, task)
    return sum(1 for one in state["ends"]
               if one.get("state") == "parked"
               and (state["intents"].get(one.get("tag")) or {}).get("agent") == member
               and (state["intents"].get(one.get("tag")) or {}).get("task") == task
               and int((state["intents"].get(one.get("tag")) or {}).get("id") or 0) > since)


def silence_limit(state: dict, member: str) -> int:
    """-> the silent parked exchanges that earn the member ONE reminder: its profile's `--silence`, else the season's
    or `TEAM.md`'s `silence:` (`state["limits"]`), else DEFAULT_SILENCE."""
    profile = profile_of(state["started"] or {}, member)
    if profile.get("silence") is not None:
        return int(profile["silence"])
    return int(state["limits"].get("silence") or DEFAULT_SILENCE)


def reminded_at(state: dict, member: str, task: str) -> bool:
    """-> whether a REMINDER already carried the member's debts on the task since its silence counts."""
    since = silence_since(state, member, task)
    return any(one.get("relance") == "reminder" and one.get("agent") == member and one.get("task") == task
               and int(one.get("id") or 0) > since for one in state["intents"].values())


def relance_of(state: dict, member: str) -> tuple[str, str | None] | None:
    """-> why the tick RELANCES the member: it owes an answer and stands at the bottom of the deadlocked set --
    `("owed", None)` a sink, `("cycle", <member>)` a knot, naming a member it waits on; `("reminder", None)` once its
    silence on the task of its first debt reaches `silence:` and no reminder carried it yet (row 115) --; None
    otherwise. No count bounds the relances: `launches:`, `budget:` and `budget-launches:` bound a long task."""
    debts = owed_by(state, member)
    if not debts or not at_bottom(state, member):
        return None
    task = str(state["messages"][debts[0]].get("task"))
    if silence_of(state, member, task) >= silence_limit(state, member) and not reminded_at(state, member, task):
        return ("reminder", None)
    waits = sorted(waits_for(state).get(member, ()))
    return ("owed", None) if not waits else ("cycle", waits[0])


def silences(state: dict, name: str, clock: datetime, member: str | None = None) -> list[dict]:
    """-> what the tick writes for each member whose SILENCE fell (row 115): `silence {agent, task, exchanges}` for a
    debtor, no wake-up of its under way, whose silent parked exchanges on a task it owes on reach `silence:` + 1 --
    the one after its reminder --; for a member suspected already, once its interval passed, one silent exchange
    more (its try said nothing) is one more fall. The replay makes each a fall of the detector (`health.falls + 1`,
    `cause: silence`). A root's principal gets the team's notice about it, once per opening. Judged for ONE member
    (`member`) right before its own wake, on the journal as it stands then -- a launch of its may have ended
    since the tick began --, or for every member."""
    events: list[dict] = []
    for member in ([member] if member else list((state["started"] or {}).get("agents") or {})):
        if busy(state, member):
            continue
        suspicion = suspicion_of(state, member)
        for task in dict.fromkeys(str(state["messages"][key].get("task")) for key in owed_by(state, member)):
            n = silence_of(state, member, task)
            fell = (n >= 1 and clock >= suspicion["until"]) if suspicion is not None else (
                n >= silence_limit(state, member) + 1)
            if not fell:
                continue
            events.append({"kind": "silence", "agent": member, "task": task, "exchanges": n})
            opening = opening_of(state, task)
            told = any(is_notice(state, one) and one.get("about") == member and one.get("task") == task
                       and one["id"] > int(opening or 0) for one in state["messages"].values())
            if is_root(state, member, task) and not told:
                events.append({"kind": "post", "task": task, "from": name, "to": told_of(state, member, task),
                               "verb": "notice", "about": member, "cause": "silence",
                               "text": f"{member} said nothing on {task} for {n} exchange(s) while it owes an answer: "
                                       "suspected, tried again once its interval has passed"})
            break                                                # one fall per tick and member
    return events


def suspicion_of(state: dict, member: str) -> dict | None:
    """-> the member's SUSPICION (the failure detector ◇P, Chandra and Toueg 1996), read from the journal alone:
    `{falls, until}` while a final failure of its stands -- its INTERVAL runs from the hour of the last one for the
    base of the team's net in seconds (`schedule:`, DEFAULT_SCHEDULE without it or under `off`) doubled at each
    final failure in a row and never above `suspect-max:` (DEFAULT_SUSPECT_MAX without it), `until` the local hour
    it ends --, None for a member not suspected."""
    health = (state.get("health") or {}).get(member) or {}
    falls = int(health.get("falls") or 0)
    if not falls or not health.get("at"):
        return None
    base = schedule_seconds(state.get("started")) or DEFAULT_SCHEDULE
    bound = int(state["limits"].get("suspect-max") or DEFAULT_SUSPECT_MAX)
    at = datetime.fromisoformat(str(health["at"])).astimezone().replace(tzinfo=None)
    return {"falls": falls, "until": at + timedelta(seconds=min(base * 2 ** (falls - 1), bound))}


def within(state: dict, member: str, clock: datetime) -> bool:
    """-> whether the member is suspected and its interval still runs: nobody wakes it."""
    suspicion = suspicion_of(state, member)
    return suspicion is not None and clock < suspicion["until"]


def not_answering(member: str, suspicion: dict) -> str:
    return f"no answer: {member} is not answering at the moment; it is tried again at {suspicion['until']:%H:%M:%S}"


def suspected_answers(state: dict, clock: datetime) -> list[dict]:
    """-> what the tick writes for each SUSPECTED member within its interval, no wake-up of its under way: every
    debt it owes to a MEMBER and every `do` or `ask` of a member that reaches it answered in its place (`re`, `by:
    tick`, `suspected`, the hour of its try said), which delivers the message and wakes its author. What a PRINCIPAL
    says to the member is never answered for: a launch of the member delivers it at this very tick (`woken`), and
    that launch is its try; a principal's opening delivered before the fall stays owed, tried once the interval
    passed (`tried_of`). A member's message that owes nothing waits for the try."""
    events: list[dict] = []
    for member in list((state["started"] or {}).get("agents") or {}):
        suspicion = suspicion_of(state, member)
        if suspicion is None or clock >= suspicion["until"] or busy(state, member):
            continue
        said = not_answering(member, suspicion)
        reaching = [one["id"] for one in inbox(state, member) if owes(state, one["id"]) and is_open(state, one.get("task"))]
        for key in dict.fromkeys(owed_by(state, member) + reaching):
            message = state["messages"][key]
            if is_member(state, message.get("from")):
                events.append({"kind": "post", "task": message.get("task"), "from": member, "to": message.get("from"),
                               "verb": "re", "re": key, "by": "tick", "suspected": True, "text": said})
    return events


def tried_of(state: dict, member: str, clock: datetime) -> tuple[str, None] | None:
    """-> `("tried", None)` when the tick TRIES the suspected member by a relance: its interval passed, no wake-up
    of its under way, and a principal's opening among its debts -- what nothing else would deliver it again. A
    member with another message to receive is tried by that message, as any wake-up."""
    suspicion = suspicion_of(state, member)
    if suspicion is None or clock < suspicion["until"] or busy(state, member):
        return None
    return ("tried", None) if any(principal_opening(state, key) for key in owed_by(state, member)) else None


def health_lines(state: dict, member: str) -> str:
    """-> the HEALTH VIEW a wake-up's head carries: one line per other member suspected, the hour of its try --
    '' when nobody is."""
    found = []
    for other in list((state.get("started") or {}).get("agents") or {}):
        suspicion = suspicion_of(state, other) if other != member else None
        if suspicion is not None:
            found.append(f"[not answering at the moment: {other} -- tried again at {suspicion['until']:%H:%M:%S}]")
    return "\n".join(found)


def is_member(state: dict, name) -> bool:
    return name in ((state["started"] or {}).get("agents") or {})


def parent_of(state: dict, agent: str, task: str) -> str:
    """-> whom the agent reports to on this task: the one that delegated it, else the task's
    author (a principal)."""
    for one in reversed(state["delegations"]):
        if one["to"] == agent and one["task"] == task:
            return str(one["from"])
    return str((state["tasks"].get(task) or {}).get("from") or (state["started"] or {}).get("owner") or "")


def told_of(state: dict, member: str, task: str) -> str:
    """-> whom the team's NOTICE about the member on this task goes to -- a person with a box, never the team: the
    member that delegated the task to it, else the task's principal, the owner when the team itself wrote the task (a
    ceremony's)."""
    for one in reversed(state["delegations"]):
        if one["to"] == member and one["task"] == task:
            return str(one["from"])
    started = state["started"] or {}
    author = (state["tasks"].get(task) or {}).get("from")
    return str(author if author and author != started.get("team") else started.get("owner") or "")


def is_root(state: dict, agent: str, task: str) -> bool:
    """-> whether the agent holds the task from a principal: its `done` resolves the task."""
    held = state["tasks"].get(task) or {}
    return held.get("to") == agent and not is_member(state, held.get("from"))


def is_principal(state: dict, name) -> bool:
    """-> whether `name` is one a team answers to: its owner, a mandator of `principals:`, or the
    team itself (the author of a ceremony task)."""
    started = state["started"] or {}
    return name is not None and (name == started.get("owner") or name == started.get("team")
                                 or name in (started.get("principals") or []))


def edges_of(state: dict, task: str) -> set[tuple[str, str]]:
    """-> the (agent, the one it reports to) pairs that route on the task: the `reports:` edges,
    and on a ceremony task each participant reporting to the ceremony's facilitator."""
    started = state["started"] or {}
    pairs = {(child, str(one.get("to"))) for one in started.get("reports") or [] for child in one.get("from") or []}
    ceremony = (state["tasks"].get(task) or {}).get("ceremony")
    for one in started.get("ceremonies") or []:
        if ceremony is not None and one.get("name") == ceremony:
            pairs |= {(child, str(one.get("facilitator"))) for child in one.get("participants") or []}
    return pairs


def written(conductor, path: Path, name: str, judge) -> list[dict]:
    """The journal's critical section: under its lock the events are read, `judge(state,
    events)` says the events to append -- without `at`, `id`, `team` -- or refuses, and they
    are appended with the next ids. -> the events written, whole."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with conductor.record.held(path):
        events = tailed(path)
        state = replay(events)
        last = max((int(one.get("id") or 0) for one in events), default=0)
        made = []
        for offset, one in enumerate(judge(state, events), 1):
            made.append({"at": now(), "id": last + offset, "kind": one["kind"], "team": name,
                         **{key: value for key, value in one.items() if key != "kind"}})
        with path.open("a", encoding="utf-8") as handle:
            for one in made:
                handle.write(json.dumps(one, ensure_ascii=False) + "\n")
    return made


def appended(conductor, path: Path, name: str, events: list[dict]) -> list[dict]:
    """Appends the events given, judged already: the tick's writes."""
    return written(conductor, path, name, lambda state, lines: events) if events else []


def next_task(state: dict) -> str:
    return f"T{len(state['tasks']) + 1}"


# --- the agents, by the house's console ----------------------------------------------------

def born(root: Path, conductor, paths: list[str]) -> list[str]:
    """Creates the agents the house lacks by the house's own console, `agent add <path> --type member`: an
    instance at each path under the house that BORROWS the house's machine, no door, its
    SETTINGS at the cap and the member's profile `add` writes (its boot without the catalog of skills nor
    the threads' pass) -- each path once, however many members it plays -- never
    by an import of another package's script. `add` plays under the house's BIRTH lock for the
    path (`born-busy` past `call_lock_wait`): two starts that name one new path give it birth
    once, the other reads `agent-exists`. -> the paths born."""
    engine = engine_of(root, conductor)
    made = []
    for name in dict.fromkeys(paths):
        if conductor.instance.is_instance(agent_meta(root, name)):
            continue
        added = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "add", name,
                                "--type", MEMBER_TYPE],
                               capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
        if added.returncode == 0:
            made.append(name)
        elif "agent-exists" not in added.stderr:
            refuse(f"agent-add-failed -- `{name}` could not be born under the house: "
                   f"{(added.stderr or added.stdout).strip()[-300:]}")
    return made


def placed(target: Path, data: bytes) -> None:
    """Writes `target` whole: a temporary beside it, then one rename."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}-{secrets.token_hex(3)}")
    temporary.write_bytes(data)
    os.replace(temporary, target)


# --- the entries: successors of each agent's DAG, from the team's directory --------------------

def entries_at(team: dict) -> dict[str, list[str]]:
    """-> for each agent's path, the entry documents its members may play, in the declaration's
    order: `do`'s for every member, a ceremony's for its participants and its facilitator."""
    played: dict[str, list[str]] = {}
    ceremonies = {one["name"]: one for one in team["ceremonies"]}
    for trigger, document in team["entries"].items():
        members = (list(team["agents"]) if trigger == "do"
                   else [*ceremonies[trigger]["participants"], ceremonies[trigger]["facilitator"]])
        for member in members:
            documents = played.setdefault(team["agents"][member], [])
            if document not in documents:
                documents.append(document)
    return played


def entries_judged(root: Path, conductor, name: str, team: dict) -> None:
    """Refuses `entry-missing` before anything is written when an entry is neither in the team's
    directory nor resolved by the instance of an agent that plays it (a document of its type) --
    the agent's run would name a successor it cannot play, and would play no exchange at all."""
    directory = team_root(root, name)
    missing = [f"{path} lacks {document}" for path, documents in entries_at(team).items()
               for document in documents
               if not (directory / document).is_file()
               and (not conductor.instance.is_instance(agent_meta(root, path))
                    or not conductor.instance.resolve(agent_meta(root, path), document).is_file())]
    if missing:
        refuse(f"entry-missing -- {'; '.join(missing)}: an entry lives in the team's directory "
               f"({TEAMS}/{name}/), or in the instance of every agent that plays it -- lay it there, then start again.")


def team_document(name: str, documents: list[str], intention: str) -> bytes:
    """-> `TEAM-<name>.md` of the team's directory: the HEAD this skill writes -- called at the kit's
    `turn.begin` of every exchange of the team's runs, its `SERVE` serves the document itself, its body
    read once and again when it changes; with entries, at its exit this skill's verb `entry` elects among
    them and the neutral successor -- then the BODY, the team's intention, as its owner wrote it."""
    elected = (f"next: {' '.join([*documents, IDLE])}\ndecide: {DECIDER} {name}\n" if documents else "")
    return (f"---\nproc: |\n  SERVE\nserve: |\n  {document_name(name)}\nattach: turn.begin\n{elected}---\n"
            + intention).encode("utf-8")


def document_name(name: str) -> str:
    """-> the file name of the team's document: `TEAM-<name>.md`."""
    return f"TEAM-{name}.md"


def intention_of(path: Path) -> str:
    """-> the owner's part of the team's document: its text after the head this skill writes, the whole text
    when it carries none."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith(BORDER + "\n"):
        return text
    end = text.find(f"\n{BORDER}\n", len(BORDER))
    return text[end + len(BORDER) + 2:] if end >= 0 else text


def documents_written(root: Path, name: str, team: dict) -> None:
    """Writes the team's documents in its directory, at every start: the head of `TEAM-<name>.md` -- its body,
    the owner's intention, kept to the byte --, `TEAM-IDLE.md` with entries. The law an earlier version laid there, `TURN.md`
    at its bytes (`RETIRED_IN_TEAM`), is removed and said: the team's runs no longer carry it, a message
    is a `words` read at the flow; a `TURN.md` or a `TEAM-IDLE.md` standing there and different is the
    owner's: kept, and said."""
    here = Path(__file__).resolve().parent
    directory = team_root(root, name)
    entries = list(dict.fromkeys(team["entries"].values()))
    for target_name, sources in RETIRED_IN_TEAM.items():
        target = directory / target_name
        if not target.is_file():
            continue
        if any(target.read_bytes() == (here / one).read_bytes() for one in sources):
            target.unlink()                             # an earlier version's law: the team's, removed
            print(f"pp-team: {TEAMS}/{name}/{target_name} removed -- the law of an earlier version", file=sys.stderr)
        else:
            print(f"pp-team: {TEAMS}/{name}/{target_name} kept -- not the team's: the owner's own stays",
                  file=sys.stderr)
    if entries:
        target, data = directory / IDLE, (here / IDLE_SOURCE).read_bytes()
        if target.is_file() and target.read_bytes() != data:
            print(f"pp-team: {TEAMS}/{name}/{IDLE} kept -- not the team's: the owner's own stays", file=sys.stderr)
        elif not target.is_file():
            placed(target, data)
    own = directory / document_name(name)
    placed(own, team_document(name, entries, intention_of(own)))


def cleared(root: Path, name: str, team: dict) -> None:
    """Removes from each agent of the team what an earlier version laid in its instance: the files at
    the team's very bytes (`RETIRED`: the law and the neutral successor of team 0.32, the decider skill)
    and `procs/TEAM-<name>.md` deciding by `team-entry <name>`; a file that differs is the agent's own --
    kept, and said. Nothing of a team is written there."""
    here = Path(__file__).resolve().parent
    for path in dict.fromkeys(team["agents"].values()):
        meta = agent_meta(root, path)
        for where, source in RETIRED.items():
            target = meta.joinpath(*where)
            if not target.is_file():
                continue
            if (here / source).is_file() and target.read_bytes() == (here / source).read_bytes():
                target.unlink()
            else:
                print(f"pp-team: {path} · {'/'.join(where)} kept -- not the team's: the agent's own stays",
                      file=sys.stderr)
        skill = meta / "skills" / "team-entry"
        if skill.is_dir() and not any(skill.iterdir()):
            skill.rmdir()
        laid = meta / "procs" / f"TEAM-{name}.md"
        if laid.is_file():
            if f"decide: team-entry {name}" in laid.read_text(encoding="utf-8", errors="replace"):
                laid.unlink()
            else:
                print(f"pp-team: {path} · procs/TEAM-{name}.md kept -- not the team's: the agent's own stays",
                      file=sys.stderr)


def entry_of(root: Path, name: str, run: str) -> str:
    """-> the document the wake-up of the team under the run `run` plays: the last wake-up of the
    team launched under that key and not ended -- its intent's run, its `wake-launched`, else its
    tag at the house's `messages.jsonl` (an opening's first exchange plays before the tick writes
    `wake-launched`) --; its task's ceremony names its entry, any other task `do`'s; no entry, no
    such wake-up, no journal: the neutral `TEAM-IDLE.md`. Nothing written, no lock."""
    journal = journal_of(root, name)
    if not journal.is_file():
        return IDLE
    state = state_of(journal)
    standing = open_intents(state)
    under = [one for one in standing
             if run in (one.get("run"), (state["launched"].get(one["tag"]) or {}).get("run"))]
    if not under:
        opening = {one["tag"] for one in standing if one.get("run") is None}
        under = [state["intents"][line["tag"]] for line in lines_of(record_of(root, MESSAGES))
                 if line.get("run") == run and line.get("tag") in opening]
    if not under:                                  # an opening under way: the house opened the run before any
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # record names it -- the agent's slot says it
        from _core import core                     # noqa: E402 -- the bootstrap
        persistence = core(__file__).persistence
        under = [one for one in standing if one.get("run") is None
                 and persistence.slot_of(agent_meta(root, path_of_intent(state, one)), run).is_file()]
    if not under:
        return IDLE
    entries = (state["started"] or {}).get("entries") or {}
    task = state["tasks"].get(under[-1].get("task")) or {}
    document = entries.get(str(task["ceremony"])) if task.get("ceremony") else entries.get("do")
    return str(document or IDLE)


# --- the relaunch entry: the house's way back after a restart, ONE for all its teams ------------

def table_read() -> tuple[list[str], str]:
    """-> (the calendar's lines, '') -- the file `PP_CRONTAB` names when it is set (absent:
    empty), else the user's crontab (`crontab -l`; none yet: empty); or ([], why) when no
    table can be read."""
    given = os.environ.get(CRONTAB)
    if given:
        path = Path(given)
        if not path.is_file():
            return [], ""
        try:
            return path.read_text(encoding="utf-8").splitlines(), ""
        except OSError as why:
            return [], f"{given}: {why}"
    try:
        played = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    except OSError as why:
        return [], f"crontab: {why}"
    if played.returncode == 0:
        return played.stdout.splitlines(), ""
    if "no crontab" in (played.stderr or ""):
        return [], ""
    return [], (played.stderr or "").strip() or f"crontab -l rc {played.returncode}"


def table_write(lines: list[str]) -> str:
    """Replaces the calendar with these lines -- the `PP_CRONTAB` file, or `crontab -`.
    -> '' or why it could not be written."""
    text = "\n".join(lines) + ("\n" if lines else "")
    given = os.environ.get(CRONTAB)
    if given:
        try:
            Path(given).write_text(text, encoding="utf-8")
            return ""
        except OSError as why:
            return f"{given}: {why}"
    try:
        played = subprocess.run(["crontab", "-"], input=text, capture_output=True, text=True)
    except OSError as why:
        return f"crontab: {why}"
    return "" if played.returncode == 0 else ((played.stderr or "").strip() or f"crontab - rc {played.returncode}")


def mark_of(root: Path) -> str:
    """-> the mark that ends the house's one line in the crontab: how it is found again and removed."""
    return f"# pp-team {root}"


def marked(line: str, root: Path) -> bool:
    """-> whether a crontab line is the house's: its mark, or the mark of one of its teams that an earlier version laid
    (`# pp-team <house> <team>`) -- never the line of a house whose path only begins like this one's."""
    _, found, rest = line.rstrip().rpartition(" # pp-team ")
    return bool(found) and (rest == str(root) or rest.startswith(f"{root} "))


def value_name(root: Path) -> str:
    """-> the house's value in the user's Run key: `pp-team-<12 hex of the house's path>`, so that two houses of one
    user never take each other's."""
    return f"{RELAUNCH_PREFIX}-{hashlib.sha1(str(root).encode('utf-8')).hexdigest()[:12]}"


def runkey_read() -> tuple[dict[str, str], str]:
    """-> ({value: command}, '') of the user's Run key -- the file `PP_RUNKEY` names when it is set (one line
    `<value>\t<command>` per value; absent: empty), else `RUN_KEY` under HKEY_CURRENT_USER by `winreg`; or ({}, why)."""
    given = os.environ.get(RUNKEY)
    if given:
        path = Path(given)
        if not path.exists():
            return {}, ""
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as why:
            return {}, f"{given}: {why}"
        return dict(one.split("\t", 1) for one in lines if "\t" in one), ""
    try:
        import winreg
        found: dict[str, str] = {}
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            index = 0
            while True:
                try:
                    value, data, _ = winreg.EnumValue(key, index)
                except OSError:
                    return found, ""
                found[str(value)] = str(data)
                index += 1
    except (ImportError, OSError) as why:
        return {}, f"Run key: {why}"


def runkey_write(value: str, command: str | None) -> str:
    """Writes ONE value of the user's Run key -- `command` set, None removed -- in the `PP_RUNKEY` file or by `winreg`,
    under no right the user lacks. -> '' or why it could not be written."""
    given = os.environ.get(RUNKEY)
    if given:
        found, why = runkey_read()
        if why:
            return why
        found.pop(value, None)
        if command is not None:
            found[value] = command
        try:
            Path(given).write_text("".join(f"{one}\t{data}\n" for one, data in found.items()), encoding="utf-8")
            return ""
        except OSError as why:
            return f"{given}: {why}"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if command is None:
                winreg.DeleteValue(key, value)
            else:
                winreg.SetValueEx(key, value, 0, winreg.REG_SZ, command)
        return ""
    except FileNotFoundError:
        return ""
    except (ImportError, OSError) as why:
        return f"Run key: {why}"


def call_wait(root: Path, conductor) -> float:
    """-> `call_lock_wait` as the house's SETTINGS say it, 30 s without them: how long a verb
    waits for one of the house's locks."""
    try:
        return float(conductor.settings.of(root).call_lock_wait)
    except (AttributeError, TypeError, ValueError):
        return 30.0


def relaunch_held(root: Path, conductor):
    """-> the lease on the house's RELAUNCH lock (`state/relaunch.lock`), waited for within `call_lock_wait` -- the
    entry is laid, judged and removed under it, so that the stop of one team and the start of another at once never
    take the net of the team in need --, or None past the bound."""
    return locks(conductor).acquire(root / ".sys" / "state" / RELAUNCH_LOCK, wait=call_wait(root, conductor))


def scheduler(system: str | None = None) -> str:
    """-> the façade that holds the relaunch entry: `nt` (the user's Run key) or `posix` (the user's crontab) -- the
    system given, else `PP_SCHEDULER` (the bench plays both façades on one machine), else the system this process runs
    on."""
    return system or os.environ.get(SCHEDULER) or ("nt" if os.name == "nt" else "posix")


def run_command(root: Path, conductor) -> str:
    """-> what the Run key plays at logon: `uvw run <engine> --instance <house> team tick --all` -- uv's launcher
    without a window -- when `uvw` is found, else the house's console by its absolute path."""
    windowless = shutil.which("uvw")
    if windowless:
        return f'"{windowless}" run "{engine_of(root, conductor)}" --instance "{root}" team tick --all'
    return f'"{house_console(root, conductor)}" team tick --all'


def reboot_line(root: Path, conductor) -> str:
    """-> the house's relaunch line in the crontab: `@reboot`, the interpreter and the engine by their absolute paths --
    the form `--on-end` composes, a line cron replays as is."""
    engine = engine_of(root, conductor)
    return (f"@reboot {shlex.quote(sys.executable)} {shlex.quote(str(engine))} "
            f"--instance {shlex.quote(str(root))} team tick --all >/dev/null 2>&1 {mark_of(root)}")


def needing(root: Path, but: str | None = None) -> list[str]:
    """-> the teams of the house that need their net, in the order of their names: started, `schedule:` not `off`, a
    task open or a ceremony declared -- `but` left out (a team being deleted)."""
    home = root.parent / TEAMS
    names = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    found = []
    for name in names:
        journal = journal_of(root, name)
        if name == but or not journal.is_file():
            continue
        state = state_of(journal)
        if state["started"] is not None and schedule_seconds(state["started"]) is not None and not netless(state):
            found.append(name)
    return found


def laid_now(root: Path, conductor, system: str | None = None) -> str:
    """Lays the house's entry, the relaunch lock held by the caller: the Run key's value when it differs, or the
    crontab with every line marked for the house replaced by its one line. -> '' or why the system refused it."""
    if scheduler(system) == "nt":
        found, why = runkey_read()
        if why:
            return why
        command = run_command(root, conductor)
        return "" if found.get(value_name(root)) == command else runkey_write(value_name(root), command)
    lines, why = table_read()
    if why:
        return why
    line = reboot_line(root, conductor)
    kept = [one for one in lines if not marked(one, root)]
    return "" if [one for one in lines if marked(one, root)] == [line] else table_write(kept + [line])


def relaunch_laid(root: Path, conductor, system: str | None = None) -> str:
    """Lays the house's ONE relaunch entry under the relaunch lock -- after the verb wrote its journal. -> '' or why the
    system refused it."""
    lease = relaunch_held(root, conductor)
    if lease is None:
        return "the relaunch lock is busy"
    try:
        return laid_now(root, conductor, system)
    finally:
        locks(conductor).release(lease)


def relaunch_removed(root: Path, conductor, name: str, but: str | None = None, system: str | None = None) -> None:
    """Removes the house's relaunch entry when NO team of the house needs its net any more (`but` left out) -- judged
    and removed in one hold of the relaunch lock; a removal the system refuses is said on stderr, in the words of the
    team `name` whose verb tried it."""
    lease = relaunch_held(root, conductor)
    if lease is None:
        sys.stderr.write(f"pp-team: {name} · relaunch not removed -- the relaunch lock is busy\n")
        return
    try:
        if needing(root, but):
            return
        if scheduler(system) == "nt":
            found, why = runkey_read()
            if not why and value_name(root) in found:
                why = runkey_write(value_name(root), None)
        else:
            lines, why = table_read()
            kept = [one for one in lines if not marked(one, root)]
            if not why and len(kept) != len(lines):
                why = table_write(kept)
        if why:
            sys.stderr.write(f"pp-team: {name} · relaunch not removed -- {why}\n")
    finally:
        locks(conductor).release(lease)


def relaunch_standing(root: Path, system: str | None = None) -> bool:
    """-> whether the house's relaunch entry stands: its value in the Run key, or its line in the crontab."""
    if scheduler(system) == "nt":
        return value_name(root) in runkey_read()[0]
    return any(one.rstrip().endswith(mark_of(root)) for one in table_read()[0])


def relaunch_notice(state: dict) -> dict | None:
    """-> the last notice of the season that said the relaunch entry was refused, None when none did."""
    since = int((state["started"] or {}).get("id") or 0)
    said = [one for one in state["messages"].values()
            if one.get("relaunch") and one.get("verb") == "notice" and int(one["id"]) > since]
    return said[-1] if said else None


def relaunch_said(root: Path, conductor, name: str, journal: Path) -> None:
    """Lays the relaunch entry, and SAYS a refusal of the system without failing: on stderr, and ONCE per season as a
    notice of the team to the owner (`relaunch: true`, its `why`, no `about`: it holds no wait); the team runs on its
    timer meanwhile."""
    why = relaunch_laid(root, conductor)
    if not why:
        return
    sys.stderr.write(f"pp-team: {name} · relaunch not laid -- {why}\n")
    state = state_of(journal)
    if relaunch_notice(state) is not None:
        return
    task = next((one["id"] for one in state["tasks"].values() if one["state"] == "open"), None)
    appended(conductor, journal, name, [
        {"kind": "post", "task": task, "from": name, "to": str((state["started"] or {}).get("owner")), "verb": "notice",
         "relaunch": True, "why": why,
         "text": (f"the team {name} cannot be relaunched after a restart: the system refused its entry at logon "
                  f"({why}). It runs on its timer until this session ends. To keep it running across a restart, "
                  f"let the user write their Run key (Windows) or start cron (Linux), then start the team again.")}])


def netted(root: Path, conductor, name: str, state: dict) -> None:
    """Lays the team's relaunch entry again when a verb finds it gone and the team needs its net; the timer is armed
    by the tick that follows the verb (`armed`); nothing under `off`."""
    if schedule_seconds(state["started"]) is not None and not netless(state) and not relaunch_standing(root):
        relaunch_said(root, conductor, name, journal_of(root, name))


TIMER_TICKING = False            # set in the timer's own tick: the timer it arms next is no news for the journal


def timer_mark(root: Path, name: str) -> Path:
    return journal_of(root, name).parent / TICK_TIMER


def timer_standing(root: Path, name: str) -> dict:
    """-> the TIMER that stands for the team, `{pid, due, token}` while its process is alive -- the mark beside the
    journal, read and judged by its pid --, {} when none stands or the process is gone."""
    try:
        found = json.loads(timer_mark(root, name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    pid = found.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return {}
    return found if alive(pid) else {}


def alive(pid: int, system: str = os.name) -> bool:
    """-> whether the process `pid` runs. Under Windows the system is asked (`asked_alive`): there `os.kill`
    sends no signal 0, it ends the process. Elsewhere the signal 0, which a process of another user answers
    by a refusal -- alive all the same."""
    if system == "nt":
        return asked_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def asked_alive(pid: int) -> bool:
    """-> whether Windows says the process `pid` runs: `OpenProcess` for its exit code alone, then
    `GetExitCodeProcess` -- `STILL_ACTIVE` while it runs. A process the system refuses to open (another
    user's) runs; one it cannot find has ended."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    handle = kernel.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ctypes.get_last_error() == ERROR_ACCESS_DENIED
    try:
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == STILL_ACTIVE
    finally:
        kernel.CloseHandle(handle)


def apart(system: str = os.name) -> dict:
    """-> the arguments that start a process detached from the caller: under Windows a console of its own that
    no window shows, in a process group of its own -- closing the operator's window ends nothing; elsewhere a
    session of its own, its group, which `ended_now` ends whole."""
    if system == "nt":
        return {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def disarmed(root: Path, name: str) -> None:
    """Ends the team's timer, when one stands, and removes its mark: the net leaves with `schedule-off`."""
    standing = timer_standing(root, name)
    if standing:
        ended_now(int(standing["pid"]))
    timer_mark(root, name).unlink(missing_ok=True)


def due_now(state: dict, member: str) -> bool:
    """-> whether the member is due a launch the tick did not play: idle, something to receive on an open task whose
    launches are not spent, the budget not spent -- held by `parallel:` or by the budget's rest, launched by a
    later tick --, or its run standing on an open task."""
    if busy(state, member) or state["budget_spent"]:
        return False
    standing_on = state["standing"].get(member)
    if standing_on is not None and is_open(state, standing_on):
        return True
    return any(task not in state["launches_spent"] and loud(state, box)
               and not (wait_open(state, member, task)
                        and all(held_by_wait(state, member, task, one) for one in loud(state, box)))
               for task, box in dues(state, member))


def deadline_of(state: dict, clock: datetime, step: int) -> datetime | None:
    """-> the hour the next tick is DUE under the timer, None when nothing is due: a launch under way (its `timeout:`
    when one is declared, else the step), a suspected member within its interval with something to deliver or to
    answer (its `until`), a member due but not launched (the step), the next ring of an `every` ceremony or the next
    period of a live recurrence -- each at
    most the step away, the earliest of them, never before the next second. A paused team waits on its launches
    under way alone."""
    soon = clock + timedelta(seconds=step)
    due: list[datetime] = []
    timeout = state["limits"].get("timeout")
    for tag in state["intents"]:
        if tag in state["ended"]:
            continue
        launched = state["launched"].get(tag)
        if launched is not None and timeout is not None and launched.get("at"):
            born = datetime.fromisoformat(str(launched["at"])).astimezone().replace(tzinfo=None)
            due.append(min(soon, born + timedelta(seconds=float(timeout))))
        else:
            due.append(soon)
    if not state["paused"]:
        for member in list((state["started"] or {}).get("agents") or {}):
            suspicion = suspicion_of(state, member)
            if suspicion is not None and clock < suspicion["until"]:
                if owed_by(state, member) or any(loud(state, box) for _, box in dues(state, member)):
                    due.append(min(soon, suspicion["until"]))
            elif due_now(state, member):
                due.append(soon)
        for ceremony in (state["started"] or {}).get("ceremonies") or []:
            ring = next_due(ceremony, state)
            if ring is not None:
                due.append(max(datetime.fromisoformat(ring), clock + timedelta(seconds=1)))
        for recurrence in live_recurrences(state):
            sound = recurrence_next(recurrence)
            if sound is not None:
                due.append(max(datetime.fromisoformat(sound), clock + timedelta(seconds=1)))
    return max(min(due), clock + timedelta(seconds=1)) if due else None


def armed(root: Path, conductor, name: str, journal: Path) -> int:
    """Step 7, under any `schedule:` but `off`: the TIMER. When the tick leaves a deadline (`deadline_of`),
    ONE process is spawned detached -- this script, `timer <name> --token <t>`, outside the console: it holds no hold
    on the machine while it sleeps until that hour, then plays one tick by the house's console and dies --, and the mark beside the journal says `{pid, due, token}`: the pid of the process spawned (uv's
    launcher under Windows, alive while the timer lives: the test of life and the root of the tree a stop ends), its
    hour, and the TOKEN the timer knows itself by; the journal is read again once the mark is written, and a team
    that no longer needs its net (a `stop` wrote and disarmed meanwhile, outside the tick's lock) is disarmed at once;
    a timer standing for an hour no later
    than the new one is kept, a later one ended and replaced; nothing is spawned when nothing is due. `timer-armed {due}` is
    written when a tick arms a timer where none stood -- the timer's own tick, which arms the next, writes
    nothing. -> the events written."""
    state = state_of(journal)
    seconds = schedule_seconds(state["started"])
    if seconds is None or netless(state):
        return 0
    clock = tick_now()
    due = deadline_of(state, clock, seconds)
    if due is None:
        return 0
    standing = timer_standing(root, name)
    if standing:
        try:
            if datetime.fromisoformat(str(standing.get("due"))) <= due:
                return 0                                         # a timer stands for an hour no later: kept
        except ValueError:
            pass
        ended_now(int(standing["pid"]))
    wait = max(0.0, (due - clock).total_seconds())
    token = secrets.token_hex(8)
    log = journal.parent / FOLLOW_LOG
    with log.open("ab") as handle:                # the skill itself, never the console: no hold on the machine while it sleeps
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "timer", name,
                                  "--sleep", f"{wait:.3f}", "--due", due.isoformat(timespec="seconds"),
                                  "--token", token],
                                 stdin=subprocess.DEVNULL, stdout=handle, stderr=handle, cwd=str(root.parent),
                                 env={**os.environ, "PP_HOME": str(root)}, **apart())
    mark = timer_mark(root, name)
    temporary = mark.with_name(f".{mark.name}.{os.getpid()}")
    temporary.write_text(json.dumps({"pid": child.pid, "due": due.isoformat(timespec="seconds"), "token": token}),
                         encoding="utf-8")
    os.replace(temporary, mark)
    if netless(state_of(journal)):                 # a verb that leaves the net (a stop) wrote and disarmed while this
        disarmed(root, name)                       # tick spawned: read again after the mark, the timer leaves with it
        return 0
    if standing or TIMER_TICKING:
        return 0
    return len(appended(conductor, journal, name, [{"kind": "timer-armed", "due": due.isoformat(timespec="seconds")}]))


def timer_verb(rest: list[str]) -> int:
    """`team timer <name> --sleep <seconds> --due <local date-time> --token <token>`: the TIMER's own process, spawned
    by the tick (`armed`) as this script itself, outside the console: it holds no hold on the machine while it sleeps,
    and a maintenance plays meanwhile. It knows itself by the TOKEN the tick handed it, never by a pid: under Windows
    uv's launcher stands between the process the tick spawned and the Python that plays this script. It waits for its
    mark to carry its token (TIMER_WAIT at most: a mark the tick never wrote, it leaves), sleeps the seconds given --
    leaving at once when the mark no longer carries it: disarmed, or replaced by a timer due earlier --, takes its mark
    away and plays ONE tick by the house's console (`ticked_by_console`), which arms the next timer when a deadline
    still stands. Then it dies: no process outlives its deadline."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, {"sleep": True, "due": True, "token": True})
    if not asked["token"]:
        refuse(USAGE)
    try:
        left = float(asked["sleep"] or "")
    except ValueError:
        refuse(USAGE)
    mark = timer_mark(root, name)
    token = asked["token"]
    named_at = time.monotonic() + TIMER_WAIT
    while timer_standing(root, name).get("token") != token:
        if time.monotonic() >= named_at:
            return 0                                             # never named: not the team's timer
        time.sleep(0.05)
    deadline = time.monotonic() + max(0.0, left)
    while time.monotonic() < deadline:
        if timer_standing(root, name).get("token") != token:
            return 0                                             # disarmed, or replaced
        time.sleep(min(0.5, max(0.0, deadline - time.monotonic())))
    if timer_standing(root, name).get("token") == token:
        mark.unlink(missing_ok=True)
    return ticked_by_console(root, conductor, name)


def ticked_by_console(root: Path, conductor, name: str) -> int:
    """The timer's tick, played by the house's console -- a process of its own under the machine's shared hold, the
    engine and this package as the machine holds them at that hour (after an upgrade, the new ones) --, marked by
    `TIMER_ENV`; a tick the console refuses `maintenance-in-progress` is played again every TIMER_RETRY seconds,
    TIMER_RETRIES times at most, then said: the house's relaunch entry stays the net. -> the tick's exit code."""
    argv = [sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "team", "tick", name]
    played = None
    for _ in range(TIMER_RETRIES + 1):
        played = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=str(root.parent),
                                env={**os.environ, TIMER_ENV: "1"})
        if "maintenance-in-progress" not in played.stderr:
            break
        time.sleep(TIMER_RETRY)
    sys.stdout.write(played.stdout)
    sys.stderr.write(played.stderr)
    if "maintenance-in-progress" in played.stderr:
        sys.stderr.write(f"pp-team: {name} · the timer's tick met a maintenance {TIMER_RETRIES} times -- "
                         "the house's relaunch entry stays the net\n")
    return played.returncode


def netless(state: dict) -> bool:
    """-> whether the team no longer needs its net: started, no task open, no ceremony
    declared, no recurrence live -- the condition under which `schedule-off` is written."""
    started = state["started"]
    return (started is not None
            and not any(one["state"] == "open" for one in state["tasks"].values())
            and not (started.get("ceremonies") or [])
            and not live_recurrences(state))


# --- the tick: one advance of the team ------------------------------------------------------

def launch_flags(launch: dict) -> list[str]:
    """-> the flags `agent start` gets from what `team start` kept: the harness or the
    provider, the model, the budget, the permission regime, the model's effort. A wake-up is ONE
    launch: `--launches 1` rides every call, never a flag of the start."""
    found: list[str] = []
    for key, flag in (("harness", "--harness"), ("provider", "--provider"), ("model", "--model"),
                      ("max_budget_usd", "--max-budget-usd"), ("permissions", "--permissions"),
                      ("effort", "--effort")):
        if launch.get(key) is not None:
            found += [flag, str(launch[key])]
    return found + ["--launches", "1"]


def cursor_of(state: dict, agent: str, run: str | None, before: int) -> int:
    """-> the RUN's cursor in the team: the id of the last `wake-intent` of that run before the
    one being written (`before`) -- an intent that resumed it, or the one that opened it --, or
    the `team-started` for a new run: a new session knows nothing. The cursor is the journal's:
    nothing is written to share."""
    mine = [int(one.get("id") or 0) for tag, one in state["intents"].items()
            if run is not None and one.get("agent") == agent and int(one.get("id") or 0) < before
            and (one.get("run") == run or (state["launched"].get(tag) or {}).get("run") == run)]
    return max(mine or [int((state["started"] or {}).get("id") or 0)])


def shared(state: dict, agent: str, cursor: int) -> list[dict]:
    """-> the `wake-ended` events of OTHER agents after the cursor: the responses new to the
    agent, in the journal's order."""
    return [one for one in state["ends"] if int(one.get("id") or 0) > cursor and one.get("agent") != agent]


def sharing_line(state: dict, news: list[dict], console: Path, name: str, cursor: int) -> str:
    """-> the ONE line that names the responses new to the agent and the verb to read them
    whole, or '' when nothing is new."""
    if not news:
        return ""
    named = ", ".join(f"{one.get('agent')} on {(state['intents'].get(one.get('tag')) or {}).get('task')} (#{one['id']})"
                      for one in news)
    return (f"[new responses since your last wake-up: {named} -- read them whole: "
            f"{console} team responses {name} --since {cursor}]")


def clipped(text) -> str:
    """-> a message's text as a history line carries it: HISTORY_CHARS at most."""
    text = str(text or "")
    return text if len(text) <= HISTORY_CHARS else text[:HISTORY_CHARS - 1] + "…"


def history_of(state: dict, agent: str, task: str) -> str:
    """-> what a NEW run must be told of a task the member already worked: the messages
    delivered to the member on the task, then the posts its answers made there, one line each,
    under `[history of <task> for <agent>]` -- or '' when the member has no past on the task.
    The texts are clipped; `team responses` reads the answers whole."""
    told = [f"#{one['id']} {one.get('verb')} from {one.get('from')}: {clipped(one.get('text'))}".rstrip()
            for one in state["messages"].values()
            if one.get("to") == agent and one.get("task") == task and one["id"] in state["delivered"]]
    said = [f"#{one['id']} {one.get('verb')} to {one.get('to')}: {clipped(one.get('text'))}".rstrip()
            for one in state["messages"].values() if one.get("from") == agent and one.get("task") == task]
    if not told and not said:
        return ""
    return f"[history of {task} for {agent}]\n" + "\n".join(told + said)


def histories_of(state: dict, member: str, task: str) -> str:
    """-> what a NEW run of a member must be told: the history of the open tasks of the task's CARRIER -- the
    task alone, or the open occurrences of a recurrence, the open rings of a ceremony --, in the tasks' order;
    '' when the member has no past there."""
    carrier = carrier_of(state, task)
    return "\n\n".join(one for one in (history_of(state, member, other) for other, held in state["tasks"].items()
                                       if held.get("state") == "open" and carrier_of(state, other) == carrier) if one)


def message_of(state: dict, agent: str, one: dict) -> str:
    """-> a message as a wake-up's head shows it: `#163 DO from supervisor on T8 -- you owe an answer`, the
    kind in capitals and the id an answer cites (`RE #175`); the debt said while it stands -- and, for the
    opening of a task the member holds, that its answer closes the task --; the text indented under it."""
    cited = cited_of(state, one)
    head = (f"#{one['id']} {str(one.get('verb') or '').upper()}" + (f" #{cited}" if cited is not None else "")
            + f" from {one.get('from')} on {one.get('task')}")
    if owes(state, one["id"]) and one.get("to") == agent:
        head += f" -- {OWED}"
        if one["id"] == opening_of(state, one.get("task")):
            head += f", and your answer to it closes {one.get('task')}"
    text = str(one.get("text") or "")
    return head + "".join(f"\n  {line}" for line in text.splitlines())


def headed(team: str, agent: str, box: list[dict], news_line: str = "",
           history: str = "", state: dict | None = None, relance: tuple[str, str | None] | None = None,
           task: str | None = None) -> str:
    """-> the HEAD of a launch, what the tick writes before pp's output in the prompt: its first line says
    who is launched, `[team <team> · you are <member>]`; then the inbox -- what arrived for the member since
    its last launch, each message its head line and its text under it (`message_of`) --, or `[nothing new]`
    when a standing run is relaunched with nothing to deliver; a `stop` at the head of a run standing on the
    stopped task opens on `STOPPED_HEAD`: the run says no act and parks; the messages delivered at an earlier launch
    that the member still owes an answer on the TASK of the launch (every open task when none is named), under
    `[you still owe an answer to]`; the line naming what the
    others answered since this run's last launch, when something is new. Nothing else: the contract of the
    acts is the body of the team's document, served by pp at the start of the member's exchange. A NEW run
    of a member that had one opens, after its first line, on the history of its open tasks, then the inbox.
    A RELANCE opens on the line that says why the member is launched -- `[no new message: you still owe an
    answer]`, or, in a cycle of waits, `[you and <member> wait on each other: answer first]`, or, a REMINDER,
    `REMINDED_HEAD` (an answer or an info asked) --, then the
    members' infos that waited for it when there are any, then its debts. While another member is SUSPECTED, the HEALTH VIEW follows the first line, one line each: `[not
    answering at the moment: <member> -- tried again at HH:MM]`. The team's intention is never in the
    message: pp serves it from `TEAM.md` (`team_document`)."""
    state = state if state is not None else {"messages": {}, "debts": {}, "tasks": {}, "started": None}
    health = health_lines(state, agent)
    shown = {one["id"] for one in box}
    lines = [message_of(state, agent, one) for one in box]
    still = [message_of(state, agent, one) for key, one in sorted(state["messages"].items())
             if key not in shown and one.get("to") == agent and owes(state, key) and key in state.get("delivered", ())
             and is_open(state, one.get("task")) and (task is None or one.get("task") == task)]
    told = history + "\n\n" if history else ""
    if relance is not None:
        why = (REMINDED_HEAD if relance[0] == "reminder" else RELANCED if relance[1] is None
               else f"[you and {relance[1]} wait on each other: answer first]")
        inboxed = why + "\n\n" + ("[inbox]\n" + "\n".join(lines) + "\n\n" if lines else "")
    elif lines:
        inboxed = "[inbox]\n" + "\n".join(lines) + "\n\n"
        if any(one.get("verb") == "stop" for one in box):      # a run standing on a stopped task: its last launch
            inboxed = STOPPED_HEAD + "\n\n" + inboxed
    else:
        inboxed = NOTHING_NEW + "\n\n"
    return (f"[team {team} · you are {agent}]\n\n" + (health + "\n\n" if health else "") + told + inboxed
            + ("[you still owe an answer to]\n" + "\n".join(still) + "\n\n" if still else "")
            + (news_line + "\n\n" if news_line else "")).rstrip("\n") + "\n"


def spent_on(state: dict, run: str) -> float:
    """-> what the run spent in the team's wake-ups, as the journal charged them: the sum of the costs
    of its ends and failures -- what `agent start --max-budget-usd` gets added to a wake-up's share."""
    return round(sum(float(one.get("cost") or 0) for one in state["ends"] + state["fails"]
                     if one.get("run") == run), 6)


ACT_OPENED = re.compile(r'\{\s*"(?:do|ask|re|info)"\s*:')   # an object that opens on the key of a form


def candidates_of(text: str) -> list[tuple[list | None, str]]:
    """-> the CANDIDATES a `words` carries, in their order: each JSON value found in its text -- the text alone,
    a sentence around it, a ``` block, several values -- that is an object, or a list of objects, with a key of
    a form (`do`, `ask`, `re`, `info`) at its first level, as `(elements, "")`; and each object opened on such a key
    that does not read as JSON, as `(None, why)`. Anything else is SAID: prose, a table, a JSON value without
    the key of a form, a verb of an answer before team 0.33.0 (`done`, `reply`, `escalate`) -- nothing of it
    is a candidate. A value read is never searched inside: what it holds is its own."""
    decoder, found, spans, at = json.JSONDecoder(), [], [], 0
    while True:
        starts = [one for one in (text.find("{", at), text.find("[", at)) if one >= 0]
        if not starts:
            break
        start = min(starts)
        try:
            value, end = decoder.raw_decode(text, start)
        except ValueError:
            at = start + 1
            continue
        if not isinstance(value, (dict, list)):
            at = start + 1
            continue
        spans.append((start, end))
        elements = [value] if isinstance(value, dict) else value
        if elements and all(isinstance(one, dict) for one in elements) and any(
                form in one for one in elements for form in ELEMENTS):
            found.append((start, elements, ""))
        at = end
    for opened in ACT_OPENED.finditer(text):
        if not any(start <= opened.start() < end for start, end in spans):
            found.append((opened.start(), None, f"`{text[opened.start():opened.start() + 40]}` is no JSON value: "
                                                "an act is one JSON object, or a list of them, written whole"))
    return [(elements, why) for _, elements, why in sorted(found, key=lambda one: one[0])]


def act_formed(elements: list) -> None:
    """Judges the FORM of a candidate before its sense: every element an object of ONE form, no key beyond
    that form's, its values of their kind -- `do` an object of member -> work or a list of members, `ask` and
    `info` an object of `to` and `text` or a text, `re` the id of a message and a text. A fault raises `Refused`
    with its reason; the `await` is judged with its `do` (`awaited`)."""
    for one in elements:
        if not isinstance(one, dict):
            raise Refused(f"{json.dumps(one)[:40]} is not an object: each element of an act is one object")
        forms = [form for form in ELEMENTS if form in one]
        if len(forms) != 1:
            raise Refused(f"an element carries {' and '.join(forms) or 'none'} of the forms do, ask, re, info: "
                          "it carries exactly one")
        form = forms[0]
        extra = sorted(set(one) - ELEMENTS[form])
        if extra:
            raise Refused(f"the key `{extra[0]}` does not belong to the form `{form}`, whose keys are "
                          + ", ".join(f"`{key}`" for key in sorted(ELEMENTS[form])))
        said = one[form]
        if form == "do" and not (
                (isinstance(said, dict) and said and all(isinstance(key, str) and isinstance(text, str)
                                                         for key, text in said.items()))
                or (isinstance(said, list) and said and all(isinstance(name, str) for name in said))):
            raise Refused(f"do {json.dumps(said)[:40]}: the form is {{\"<member>\": \"<the work>\"}} "
                          "or a list of members")
        if form == "ask" and not (isinstance(said, str) or (
                isinstance(said, dict) and not set(said) - {"to", "text"}
                and all(isinstance(value, str) for value in said.values()))):
            raise Refused(f"ask {json.dumps(said)[:40]}: the form is {{\"to\": \"<member>\", \"text\": \"...\"}}")
        if form == "info" and not (isinstance(said, str) or (
                isinstance(said, dict) and not set(said) - {"to", "text"}
                and all(isinstance(value, str) for value in said.values()))):
            raise Refused(f"info {json.dumps(said)[:40]}: the form is {{\"to\": \"<member or principal>\", \"text\": \"...\"}}")
        if form == "re" and (cited_id(said) is None or not isinstance(one.get("text", ""), str)):
            raise Refused(f"re {json.dumps(said)[:40]}: the form is {{\"re\": <the message number>, \"text\": \"...\"}}")


class Refused(Exception):
    """An act the tick refuses to route, said to the member: its form broken (`act_formed`, `candidates_of`) or its
    sense wrong -- a member nobody declared, a `do` off the edges, a `re` citing a message never delivered to the
    member, an `await` of no number."""


def awaited(said, delegates: int) -> int:
    """-> n of `{"any": n}`: a whole number from 1 to the delegates of the act; any other value is
    refused."""
    n = said.get("any") if isinstance(said, dict) and set(said) == {"any"} else None
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= delegates:
        raise Refused(f"await {json.dumps(said)}: the form is {{\"any\": n}}, n from 1 to the {delegates} delegate(s)")
    return n


def resolution(state: dict, task: str, result) -> list[dict]:
    """-> what closes a task the root answered: `done` with the result, a `returned` for every post to an agent
    left undelivered on it, `schedule-off` when no task stays open, no ceremony is declared and no recurrence lives."""
    events: list[dict] = [{"kind": "done", "task": task, "result": result}]
    for one in state["messages"].values():
        if one.get("task") == task and one["id"] not in state["delivered"]:
            events.append({"kind": "returned", "message": one["id"], "to": one.get("from")})
    others_open = [one for one in state["tasks"].values() if one["id"] != task and one["state"] == "open"]
    if (not others_open and not ((state["started"] or {}).get("ceremonies") or []) and not live_recurrences(state)
            and state["schedule"]):
        events.append({"kind": "schedule-off"})
    return events


def cited_id(said) -> int | None:
    """-> the id a `re` names -- `12` or `"#12"` --, None for any other value."""
    if isinstance(said, bool):
        return None
    if isinstance(said, int):
        return said
    text = str(said).strip().lstrip("#")
    return int(text) if text.isdigit() else None


def routed(state: dict, intent: dict, elements: list[dict], settled: set | None = None,
           closed: set | None = None) -> list[dict]:
    """-> the events an ACT writes: its ELEMENTS as posts, in their order -- a `do` to each member named that
    reports to the acting one (and the `wait` its `await` declares), an `ask` to any member of the team or
    to a principal, an answer `{"re": <id>}` to the author of the message it cites, on that message's task,
    an `info` to any member or principal (the parent on the task when it names nobody): no debt, no wait, off
    every edge (row 114). The first answer to a `do` or an `ask` settles its debt; a later one is posted `info:
    true`. The ROOT's answer to its task's opening resolves the task (`resolution`). Refused, nothing written: a
    member nobody declared, a `do` off the edges, a `re` citing a message never delivered to the member or
    citing an `info`, an `await` of no number. `settled` and `closed` carry what the acts said before it in the
    same `words` settled and closed."""
    agent, task = intent["agent"], intent["task"]
    events: list[dict] = []
    held = state["tasks"].get(task) or {}
    edges = edges_of(state, task)
    settled = set() if settled is None else settled
    closed = set() if closed is None else closed
    for one in elements:
        form = next(form for form in ELEMENTS if form in one)
        if form == "do":
            asked = one["do"]
            pairs = list(asked.items()) if isinstance(asked, dict) else [(name, held.get("text") or "")
                                                                          for name in (asked or [])]
            for target, text in pairs:
                if not is_member(state, target):
                    raise Refused(f"do names `{target}`, a member nobody declared")
                if (target, agent) not in edges:
                    raise Refused(f"do names `{target}`, off the edges: `{target}` does not report to `{agent}`")
                events.append({"kind": "post", "task": task, "from": agent, "to": target, "verb": "do",
                               "text": str(text)})
            if "await" in one:
                events.append({"kind": "wait", "agent": agent, "task": task, "any": awaited(one["await"], len(pairs)),
                               "to": [target for target, _ in pairs]})
        elif form == "ask":
            asked = one["ask"] if isinstance(one["ask"], dict) else {"text": one["ask"]}
            target = asked.get("to") or parent_of(state, agent, task)
            if not is_member(state, target) and not is_principal(state, target):
                raise Refused(f"ask names `{target}`, a member nobody declared")
            events.append({"kind": "post", "task": task, "from": agent, "to": target, "verb": "ask",
                           "text": str(asked.get("text") or "")})
        elif form == "info":
            said = one["info"] if isinstance(one["info"], dict) else {"text": one["info"]}
            target = said.get("to") or parent_of(state, agent, task)
            if not is_member(state, target) and not is_principal(state, target):
                raise Refused(f"info names `{target}`, a member nobody declared")
            events.append({"kind": "post", "task": task, "from": agent, "to": target, "verb": "info",
                           "text": str(said.get("text") or "")})
        else:
            cited = cited_id(one["re"])
            answered = state["messages"].get(cited) if cited is not None else None
            if answered is None or answered.get("to") != agent or cited not in state["delivered"]:
                raise Refused(f"re #{str(one['re']).lstrip('#')}: no message #{str(one['re']).lstrip('#')} "
                              f"was delivered to `{agent}`")
            if answered.get("verb") == "info":
                raise Refused(f"re #{cited} answers an info: an info owes nothing, nobody answers it")
            on = answered.get("task")
            due = owes(state, cited) and cited not in settled and on not in closed
            post = {"kind": "post", "task": on, "from": agent, "to": answered.get("from"), "verb": "re",
                    "re": cited, "text": str(one.get("text") or "")}
            if not due:
                post["info"] = True
            events.append(post)
            if due:
                settled.add(cited)
                if cited == opening_of(state, on) and is_root(state, agent, on):
                    closed.add(on)
                    events += resolution(state, on, post["text"])
    return events


# --- the flow of a launch: read by agent's face, routed as it comes ------------------------------

def flow_lines(root: Path, conductor, path: str, run: str, start: int) -> list[tuple[int, dict]]:
    """-> the lines of the run's flow from the rank `start` on (the first line is 1), each with its rank,
    read by the house's own console: `agent flow <path> <run> --json --from <start>` -- the one way the
    tick reads what a launch says, never the file. A console that refuses (a run the agent forgot)
    reads as nothing."""
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                             "--json", "--from", str(max(1, start))], capture_output=True, text=True,
                            cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return []
    found = []
    for offset, line in enumerate(played.stdout.splitlines()):
        if not line.strip():
            continue
        try:
            found.append((max(1, start) + offset, json.loads(line)))
        except ValueError:
            continue
    return found


def act_routed(conductor, journal: Path, name: str, tag: str, rank: int, ordinal: int, text: str) -> list[dict]:
    """ONE `words` of a launch, routed under the journal's lock -- once: a `wake-routed` of the tag at
    that rank standing, nothing is written again (the follower and the tick read the same flow). Each
    CANDIDATE the `words` carries (`candidates_of`) is judged in its order, whole or not at all: one whose
    form and sense are right writes `wake-routed {tag, agent, run, launch, words, line}` then its posts; one
    whose form is broken (`act_formed`) or whose sense is wrong writes `wake-refused {…, why}` and an `info` to the
    member; on a stopped task each goes nowhere (`wake-routed` with `nowhere`); a `words` without a candidate
    writes nothing. -> the events written."""
    found = candidates_of(text)
    if not found:
        return []

    def judge(state: dict, events: list[dict]) -> list[dict]:
        intent = state["intents"].get(tag)
        launch = state["launched"].get(tag) or {}
        if intent is None or rank <= int(state["routed"].get(tag) or 0):
            return []
        marked = {"kind": "wake-routed", "tag": tag, "agent": intent["agent"], "run": launch.get("run"),
                  "launch": launch.get("launch"), "words": ordinal, "line": rank}
        if (state["tasks"].get(intent["task"]) or {}).get("state") == "stopped":
            return [{**marked, "nowhere": True} for _ in found]
        written_now: list[dict] = []
        settled: set = set()
        closed: set = set()
        for elements, broken in found:
            try:
                if elements is None:
                    raise Refused(broken)
                act_formed(elements)
                written_now += [marked, *routed(state, intent, elements, settled, closed)]
            except Refused as why:
                written_now += [{**marked, "kind": "wake-refused", "why": str(why)},
                                {"kind": "post", "task": intent["task"], "from": name, "to": intent["agent"],
                                 "verb": "info", "text": f"your act was refused: {why}"}]
        return written_now
    return written(conductor, journal, name, judge)


def opened_by(one: dict, tag: str) -> bool:
    """-> whether a line of a flow OPENS the launch's own exchange: an `opened` carrying the tag the tick handed
    `agent start` (agent 0.31.1) -- what the reader starts at, never a kept rank alone; an `opened` of another
    exchange (a chat, a launch of before) closes what is read."""
    return one.get("kind") == "opened" and str(one.get("tag") or "") == tag


def flow_read(root: Path, conductor, name: str, journal: Path, tag: str) -> dict:
    """Reads the flow of the launch `tag` from the rank the journal last kept of the run (from 1 when it kept
    none), finds the exchange the launch OPENED by its tag (`opened_by`) and routes every `words` of that
    exchange that reads as an act, in order (`act_routed`); nothing before that `opened` is routed. -> what the
    flow said of the launch's END: `{"ended", "response", "verdict", "cost", "context", "rank"}` -- `ended` once its
    `verdict` line stands (the house wrote the end of the exchange before it gave the wake lock back), `response`
    the `response` line's fields when one was kept, `cost` the sum of the `agent` events' costs, `context` the last
    `context` the exchange said (`measured_of`), `rank` the last line read. Nothing written beyond the routing."""
    state = state_of(journal)
    intent, launch = state["intents"].get(tag) or {}, state["launched"].get(tag) or {}
    run, path = str(launch.get("run") or ""), path_of_intent(state, intent)
    told = {"ended": False, "response": None, "verdict": None, "cost": 0.0, "context": None,
            "rank": int(state["flow"].get(run) or 0)}
    if not run:
        return told
    ordinal, opened = 0, False
    for rank, one in flow_lines(root, conductor, path, run, told["rank"] + 1):
        kind = one.get("kind")
        told["rank"] = rank
        if kind == "opened":                       # the launch's own exchange opens here, by its tag: what
            ordinal, opened = 0, opened_by(one, tag)   # stands before it is an earlier one's, never routed
        if not opened:
            continue
        if kind == "words":
            ordinal += 1
            act_routed(conductor, journal, name, tag, rank, ordinal, str(one.get("text") or ""))
        elif kind == "agent":
            cost = one.get("cost_usd")
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                told["cost"] = round(told["cost"] + float(cost), 6)
        elif kind == "context":
            told["context"] = measured_of(one)
        elif kind == "response":
            told["response"] = one
        elif kind == "verdict":
            told["verdict"], told["ended"] = one, True
            break
    return told


def measured_of(one: dict) -> dict:
    """-> a flow's `context` object as the journal keeps it, `{tokens, used, window}` as the house said them."""
    return {key: one.get(key) for key in ("tokens", "used", "window")}


def followed(root: Path, conductor, name: str, journal: Path, tag: str) -> int:
    """`team follow <name> <tag>`: the FOLLOWER of one launch -- keeps ONE `agent flow <path> <run> --json
    --from <rank> --follow` open on the launch's flow, from the rank the journal last kept of the run (from 1
    when it kept none), finds the exchange the launch OPENED by its tag (`opened_by`) and reads what it
    streams line by line: each `words` of that exchange that is an act routed as it comes (`act_routed`, once
    by its rank), the team ticked after it (an act may wake another member); at the exchange's `verdict` the
    launch's END is written (`ended_from_flow`) and the team ticked, and the follower leaves -- as it does when
    the stream ends (no launch plays and nothing comes), or when the intent is ended in the journal. A stream
    that ends at the `verdict` of an EARLIER exchange, before the launch's `opened`, is opened again from the
    rank reached while the launch's wake lock is held. Spawned detached by the tick at every launch, outside
    the tick's lock. -> the acts it routed."""
    state = state_of(journal)
    intent, launch = state["intents"].get(tag), state["launched"].get(tag) or {}
    run = str(launch.get("run") or "")
    if intent is None or not run or tag in state["ended"]:
        return 0
    path = path_of_intent(state, intent)
    engine = engine_of(root, conductor)
    told = {"ended": False, "response": None, "verdict": None, "cost": 0.0, "context": None,
            "rank": int(state["flow"].get(run) or 0)}
    routed_count, ordinal, opened = 0, 0, False
    while True:
        start = told["rank"] + 1
        stream = subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                                   "--json", "--from", str(start), "--follow"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=str(root.parent),
                                  env=dict(os.environ))
        assert stream.stdout is not None
        for rank, line in enumerate(stream.stdout, start):
            if not line.strip():
                continue
            try:
                one = json.loads(line)
            except ValueError:
                continue
            kind = one.get("kind")
            told["rank"] = rank
            if kind == "opened":                   # the launch's own exchange opens here, by its tag: what
                ordinal, opened = 0, opened_by(one, tag)   # stands before it is an earlier one's, never routed
            if not opened:
                continue
            if kind == "words":
                ordinal += 1
                if act_routed(conductor, journal, name, tag, rank, ordinal, str(one.get("text") or "")):
                    routed_count += 1
                    ticked(root, conductor, name)
            elif kind == "agent":
                cost = one.get("cost_usd")
                if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                    told["cost"] = round(told["cost"] + float(cost), 6)
            elif kind == "context":
                told["context"] = measured_of(one)
            elif kind == "response":
                told["response"] = one
            elif kind == "verdict":
                told["verdict"], told["ended"] = one, True
                break
        stream.stdout.close()
        stream.wait()
        if told["ended"] or opened or not held_run(root, conductor, path, run):
            break                                  # over; or the launch's exchange seen or gone: the reap reads on
    if told["ended"]:                               # the launch is over: its end written here, the tick after
        state = state_of(journal)
        if tag not in state["ended"] and tag in state["intents"]:
            ending(conductor, journal, name, tag,
                   ended_from_flow(state, state["intents"][tag], state["launched"].get(tag) or {}, told, None,
                                   (None, False) if told.get("response") else awaits_of(root, conductor, path, run)))
        ticked(root, conductor, name)
    return routed_count


def follow(rest: list[str]) -> int:
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    journal = journal_of(root, name)
    if not journal.is_file():
        refuse(f"team-not-started -- {name} was never started.")
    count = followed(root, conductor, name, journal, rest[0])
    print(f"pp-team: {name} · follow {rest[0]} · {count} act(s) routed")
    return 0


def following(root: Path, conductor, name: str, tag: str) -> None:
    """Spawns the follower of the launch `tag`, detached -- its own session, its output appended to
    `follow.log` beside the journal --: the tick that launched it goes on."""
    engine = engine_of(root, conductor)
    log = journal_of(root, name).parent / FOLLOW_LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as handle:
        subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "team", "follow", name, tag],
                         stdin=subprocess.DEVNULL, stdout=handle, stderr=handle, cwd=str(root.parent),
                         env=dict(os.environ), **apart())


def failed(state: dict, intent: dict, reason: str, cost=None, run: str | None = None,
           extra: dict | None = None) -> list[dict]:
    """-> the events a dead wake-up writes: `wake-failed` -- a retry left: its messages go back
    to the inbox (the replay discards them from the delivered); spent: `final`, and the tick ANSWERS
    in the member's place each message of the wake-up whose debt stands (`re`, `by: tick`, « the
    wake-up failed: <reason> »), which wakes their authors -- never the opening a principal posted:
    the root's debt stays owed and the team tells its principal (a `notice` about the root). On a stopped task it is
    `final` at once and goes nowhere.
    A `launch-missing` -- a tick died between the intent and the spawn -- is never final and
    spends no retry: nothing was launched. A wake-up that answered before it failed carries the
    `cost` its answer reported, and the `run` that answered when the answer was conducted -- or the run the
    face knows the state of (`state`, read at agent's face: `standing` or `parked`): that run
    stays the member's, and the retry resumes it. `extra` joins the event's fields (the rank of the flow
    read). A member that repented is
    tolerated one silent retry more per repentance; a SUSPECTED member's failure -- its try -- is final at once."""
    agent, task = intent["agent"], intent["task"]
    stopped = (state["tasks"].get(task) or {}).get("state") == "stopped"
    retries = (state["limits"].get("retries", DEFAULT_RETRIES)
               + int(((state.get("health") or {}).get(agent) or {}).get("repents") or 0))
    final = stopped or (reason != "launch-missing" and (suspicion_of(state, agent) is not None
                                                        or state["failures"].get((agent, task), 0) >= retries))
    events: list[dict] = [{"kind": "wake-failed", "tag": intent["tag"], "agent": agent, "task": task,
                           "final": final, "reason": reason}]
    if isinstance(cost, (int, float)) and not isinstance(cost, bool):
        events[0]["cost"] = cost
    if run:
        events[0]["run"] = run
    events[0].update({key: value for key, value in (extra or {}).items() if value is not None})
    if final and not stopped:
        said = f"the wake-up failed: {reason}"
        for key in intent.get("messages") or []:
            message = state["messages"].get(key) or {}
            on = message.get("task")
            if not owes(state, key) or (key == opening_of(state, on) and not is_member(state, message.get("from"))):
                continue
            events.append({"kind": "post", "task": on, "from": agent, "to": message.get("from"), "verb": "re",
                           "re": key, "text": said, "by": "tick"})
        if is_root(state, agent, task):
            events.append({"kind": "post", "task": task, "from": (state["started"] or {}).get("team"),
                           "to": told_of(state, agent, task), "verb": "notice", "about": agent, "text": said})
    return events


def house_failed(state: dict, name: str, intent: dict, why: str) -> list[dict]:
    """-> the events a launch the HOUSE refused writes: `agent start` ended before any harness, without its report
    (a package the agent does not pin, a run held, a session missing, a provider unwired). `wake-failed {reason:
    launch-failed: <why>, house: true}`, never final: no retry spent, no fall, no suspicion -- the member did
    nothing --, its messages back in its inbox, so that the next tick launches it again; and ONE notice of the
    team to the owner per (member, cause) since the season began (`house: true`, no `about`: it holds no wait)."""
    said = " ".join(why.split())
    events: list[dict] = [{"kind": "wake-failed", "tag": intent["tag"], "agent": intent["agent"], "task": intent["task"],
                           "final": False, "reason": f"launch-failed: {said}", "house": True}]
    told = f"the house could not launch {intent['agent']}: {said}"
    since = int((state["started"] or {}).get("id") or 0)
    if not any(one.get("house") and one.get("verb") == "notice" and one.get("text") == told and one["id"] > since
               for one in state["messages"].values()):
        events.append({"kind": "post", "task": intent["task"], "from": name, "to": str((state["started"] or {}).get("owner")),
                       "verb": "notice", "house": True, "text": told})
    return events


def aged(launch: dict) -> float:
    """-> the launch's age in seconds: the journal's UTC `at` against the real UTC clock
    (`PP_NOW` plays no part here: a timeout compares two wall-clock stamps)."""
    try:
        born = datetime.fromisoformat(str(launch.get("at")))
    except ValueError:
        return 0.0
    return (datetime.now(timezone.utc) - born).total_seconds()


def ending(conductor, journal: Path, name: str, tag: str, events: list[dict]) -> list[dict]:
    """Appends the events that END the intent `tag`, judged under the journal's lock: nothing
    when another writer ended it meanwhile (a `stop --kill`, another tick)."""
    return written(conductor, journal, name, lambda state, lines: [] if tag in state["ended"] else events)


def messages_cursor(root: Path, name: str, state: dict) -> dict[str, dict]:
    """-> the tags `agent start` wrote at the house's `messages.jsonl` for launches the journal does not
    know the launch of yet, each with its `run` and `pid`: the record is read INCREMENTALLY, from the byte
    the cursor `tick.cursor` beside the journal reached (whole lines alone), under the tick's lock; the
    tags of intents launched or ended leave the cursor. What a late `wake-launched` and the bounds'
    count of the launches read, in place of the record whole."""
    cursor_path = journal_of(root, name).parent / TICK_CURSOR
    try:
        cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cursor = {}
    offset, tags = int(cursor.get("offset") or 0), dict(cursor.get("tags") or {})
    record = record_of(root, MESSAGES)
    if record.is_file():
        with record.open("rb") as handle:
            handle.seek(offset)
            raw = handle.read()
        whole = raw[:raw.rfind(b"\n") + 1] if b"\n" in raw else b""
        for line in whole.decode("utf-8", "replace").splitlines():
            try:
                one = json.loads(line)
            except ValueError:
                continue
            if isinstance(one, dict) and one.get("tag"):
                tags[str(one["tag"])] = {"run": one.get("run"), "pid": one.get("pid")}
        offset += len(whole)
    tags = {tag: one for tag, one in tags.items() if tag in state["intents"] and tag not in state["launched"]
            and tag not in state["ended"] or tag not in state["intents"]}
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = cursor_path.with_name(f".{cursor_path.name}.{os.getpid()}")
    temporary.write_text(json.dumps({"offset": offset, "tags": tags}), encoding="utf-8")
    os.replace(temporary, cursor_path)
    return tags


def answered_in_flow(root: Path, conductor, state: dict, intent: dict, launch: dict) -> bool:
    """-> whether the launch's flow carries the END of its exchange (a `response` line after the `opened` that
    carries the launch's tag): a wake-up that answered -- the kill spares it, the reap ends it with its cost."""
    run = launch.get("run")
    if not run:
        return False
    start = int(state["flow"].get(str(run)) or 0) + 1
    opened = False
    for _, one in flow_lines(root, conductor, path_of_intent(state, intent), str(run), start):
        if one.get("kind") == "opened":
            opened = opened_by(one, str(intent.get("tag")))
        if opened and one.get("kind") == "response":
            return True
    return False


def awaits_of(root: Path, conductor, path: str, run: str) -> tuple[str | None, bool]:
    """-> (what the run's stack awaits, whether its harness session stands), read at agent's FACE (`agent
    status <path> --json`: `awaits`, `session`): `standing` (a production: the run is relaunched) or `parked`
    (a message); (None, False) when the face says nothing of that run. The one reading of a run's state a
    launch without a response leaves -- never deduced from the failure; the run is resumed only with its
    session (a launch killed before its harness said anything left none: `session-missing` otherwise)."""
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "status", path, "--json"],
                            capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    for line in played.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if one.get("run") == run and one.get("awaits") in ("message", "production"):
            return ("parked" if one["awaits"] == "message" else "standing"), bool(one.get("session"))
    return None, False


def ended_from_flow(state: dict, intent: dict, launch: dict, told: dict, hint: str | None,
                    awaits: tuple[str | None, bool] = (None, False)) -> list[dict]:
    """-> the events that END a launch whose flow said its end: `wake-ended {tag, agent, run, launch, state,
    cost, flow, context}` when a response was kept -- `state` what the house said of the run at `--on-end` (the
    `response` line's, else `hint`, the `PP_AGENT_STATE` the on-end tick carries): `standing`, the run
    waits for a production and is relaunched; `parked`, it waits for a message --; `wake-failed wake-dead
    {state}` when the launch ended without a response (the harness died): `state` what the run awaits, read at
    agent's face (`awaits`); no run on it, the member keeps the run that answered before or opens a new one.
    `flow` is the rank of the flow the journal reached: the next launch of the run reads from there; `context` the
    last context the exchange measured, None when it measured none."""
    response = told.get("response") or {}
    cost = told.get("cost") if told.get("cost") else response.get("cost_usd")
    run, rank = launch.get("run"), told.get("rank")
    if not told.get("response"):
        said, resumable = awaits
        return failed(state, intent, "wake-dead", None, run if resumable else None, {"flow": rank, "state": said})
    said = str(response.get("state") or hint or "parked")
    return [{"kind": "wake-ended", "tag": intent["tag"], "agent": intent["agent"], "run": run,
             "launch": launch.get("launch"), "state": said, "cost": cost, "flow": rank, "context": told.get("context")}]


def reaped(root: Path, conductor, name: str, journal: Path, hint: tuple[str, str] | None = None) -> int:
    """Step 1 and 2 (and 6 on a root's `done`): each intent without an end is matched to its launch,
    its flow is READ from the rank the journal reached -- every `words` that reads as an act routed, once
    (`flow_read`; the follower reads the same flow while the launch plays, and a launch under way within
    `timeout:` is left to it) --, and the launch is ended when its flow says so (`ended_from_flow`):
    `wake-ended` with the run's state and its cost, or `wake-failed`. A launch whose flow has no end:
    its wake lock held past `timeout:`, it is killed and fails `wake-timeout`; its lock free, it died
    without saying so -- `wake-failed wake-dead`. A launch that fails carries the run's `state`, read at
    agent's face (`awaits_of`): standing, the run is relaunched while its retries last. `hint` is what the on-end tick carries, `(run, state)`
    from `PP_AGENT_RUN` and `PP_AGENT_STATE`. -> the events written."""
    lock = locks(conductor)
    count = 0
    state = state_of(journal)
    for tag in list(state["intents"]):
        intent = state["intents"][tag]
        if tag in state["ended"]:
            continue
        launch = state["launched"].get(tag)
        if launch is None:
            found = messages_cursor(root, name, state).get(tag)
            if found is None or not found.get("run"):
                count += len(ending(conductor, journal, name, tag, failed(state, intent, "launch-missing")))
                state = state_of(journal)
                continue
            launch = appended(conductor, journal, name, [{"kind": "wake-launched", "tag": tag, "agent": intent["agent"],
                                                          "run": found["run"], "pid": found.get("pid"),
                                                          "launch": launches_of_run(state, str(found["run"])) + 1}])[0]
            count += 1
            state = state_of(journal)
        run = str(launch.get("run") or "")
        path = path_of_intent(state, intent)
        held = lock.held(launch_of(conductor, agent_meta(root, path), run))   # judged BEFORE the flow is read: a
        bound = state["limits"].get("timeout")                                # launch over wrote its end first
        if held and (bound is None or aged(launch) <= float(bound)):
            continue                                           # the launch plays: its follower reads its flow
        told = flow_read(root, conductor, name, journal, tag)
        state = state_of(journal)
        if not told["ended"]:
            if held:
                # a stuck launch: past the bound it is ended by the kill gesture and
                # FAILS -- the retries apply; `wake-killed` stays the principal's word
                pid = launch.get("pid")
                if isinstance(pid, int):
                    ended_now(pid)
                said, resumable = awaits_of(root, conductor, path, run)
                count += len(ending(conductor, journal, name, tag,
                                    failed(state, intent, "wake-timeout", None, run if resumable else None,
                                           {"flow": told["rank"], "state": said})))
            else:
                said, resumable = awaits_of(root, conductor, path, run)
                count += len(ending(conductor, journal, name, tag,
                                    failed(state, intent, "wake-dead", None, run if resumable else None,
                                           {"flow": told["rank"], "state": said})))
            state = state_of(journal)
            continue
        said = hint[1] if hint is not None and hint[0] == run else None
        if (state["tasks"].get(intent["task"]) or {}).get("state") == "stopped" and told.get("response"):
            events = [{"kind": "wake-ended", "tag": tag, "agent": intent["agent"], "run": run,
                       "launch": launch.get("launch"), "state": str((told["response"] or {}).get("state") or said or "parked"),
                       "cost": told.get("cost") or (told["response"] or {}).get("cost_usd"), "flow": told["rank"],
                       "context": told.get("context")}]
        else:
            events = ended_from_flow(state, intent, launch, told, said,
                                     (None, False) if told.get("response") else awaits_of(root, conductor, path, run))
        count += len(ending(conductor, journal, name, tag, events))
        state = state_of(journal)
    return count


def launches_of_run(state: dict, run: str) -> int:
    """-> the launches the journal knows of the run: its `wake-launched` events -- the rank the next one
    takes, and the rank of the exchange in the run's flow (`agent flow --exchange`)."""
    return sum(1 for one in state["launched"].values() if one.get("run") == run)


def waits_met(conductor, name: str, journal: Path) -> int:
    """Step 3: each (agent, task) whose agent delegated on that open task and whose wait there
    closed -- every delegate on it terminal, or n of them under its `await` -- gets `wait-met`,
    once per round of delegations. -> the events written."""
    state = state_of(journal)
    events = []
    for (agent, task), last in state["last_delegation"].items():
        if (is_open(state, task) and not wait_open(state, agent, task)
                and state["wait_met"].get((agent, task), 0) < last):
            events.append({"kind": "wait-met", "agent": agent, "task": task})
    return len(appended(conductor, journal, name, events))


def tick_now() -> datetime:
    """-> the tick's wall clock, LOCAL and naive: `PP_NOW` (ISO) when the variable is set --
    the bench, a try --, else the house's local time (the one the timer and the relaunch entry play under)."""
    given = os.environ.get(NOW, "").strip()
    if not given:
        return datetime.now()
    try:
        return datetime.fromisoformat(given)
    except ValueError:
        refuse(f"now-invalid -- `{NOW}={given}` is no ISO date-time.")


def conforms(when: dict, day) -> bool:
    """-> whether an `every` ceremony rings on that day (a date or a date-time): every day, a
    weekday, or its one day of the week -- the ONE reading of the rhythm's days."""
    kind = when.get("kind")
    weekday = day.weekday()
    return kind == "day" or (kind == "weekday" and weekday < 5) or (kind in DOWS and weekday == DOWS.index(kind))


def due_period(ceremony: dict, state: dict) -> str | None:
    """-> the period the ceremony owes a ring for, or None. An `every` ceremony is due once
    its day conforms and its hour is past (the period is the local date); an `after` one is
    due for each period its followed ceremony RESOLVED and it did not ring yet (inherited).
    The periods already rung are the state's (`rung`): a snapshot carries them."""
    already = set(state["rung"].get(str(ceremony["name"]), []))
    if ceremony["mode"] == "every":
        now = tick_now()
        when = ceremony.get("when") or {}
        if conforms(when, now) and now.strftime("%H:%M") >= str(when.get("at")):
            period = now.date().isoformat()
            if period not in already:
                return period
        return None
    for period in sorted(set(state["rung"].get(str(ceremony["after"]), []))):
        held_task = next((one for one in state["tasks"].values()
                          if one.get("ceremony") == ceremony["after"] and one.get("period") == period), None)
        if held_task is not None and held_task["state"] == "resolved" and period not in already:
            return period
    return None


def next_due(ceremony: dict, state: dict) -> str | None:
    """-> the local date-time `YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring: today when
    the day conforms and its period is not rung yet -- its hour past or not --, else the next
    conforming day; None for an `after` ceremony, which follows the one it names. A ring at hand
    (`manual-<id>`) takes no date: it moves nothing here, as in `due_period`."""
    if ceremony["mode"] != "every":
        return None
    when = ceremony.get("when") or {}
    already = set(state["rung"].get(str(ceremony["name"]), []))
    today = tick_now().date()
    for ahead in range(8):
        day = today + timedelta(days=ahead)
        if conforms(when, day) and day.isoformat() not in already:
            return f"{day.isoformat()}T{when.get('at')}"
    return None


def named(conductor, asked: dict) -> dict:
    """-> the `name` field a task is born with: `{"name": <text>}` under `--name`, `{}` without --
    a task born without a name writes the fields it always wrote. A name is what a user types: free
    text on ONE line, its spaces at the edges dropped, 1 to `NAME_CHARS` characters, every one
    printable -- a line break or a control character would split the task's line in `status`, `log`
    and `watch`. `name-invalid` otherwise."""
    given = asked.get("name")
    if given is None:
        return {}
    text = given.strip()
    if not text or len(text) > NAME_CHARS or not text.isprintable():
        shown_name = " ".join(given.split())[:40]
        refuse(f"name-invalid -- `--name {shown_name}`: a task's name is one line of 1 to {NAME_CHARS} printable "
               "characters.")
    return {"name": text}


def consignes(team: str, ceremony: dict, at: str) -> tuple[str, str]:
    """-> (the facilitator's task text, each participant's `do` text): what a ring ASKS, never the
    ceremony's declaration line -- the team's intention and the ceremony's entry say what to do."""
    head = f"the ceremony `{ceremony['name']}` of team {team} rings ({at})"
    participants = ", ".join(str(one) for one in ceremony["participants"])
    return (f"{head}: gather the answers of {participants}, then answer this message with the conclusion -- "
            "your answer closes the ceremony.",
            f"{head}: take part in it as the team's intention says, and answer {ceremony['facilitator']}.")


def ringing(state: dict, team: str, ceremony: dict, period: str, by: str | None = None) -> list[dict]:
    """-> the events one ring writes: `ceremony-due` (with `by`, the principal, for a ring at
    hand), ONE ceremony task from the team to the facilitator, its OPENING `do` from the team to the
    facilitator, then a `do` post facilitator -> each participant, then under the line's quorum the
    `wait {any: n}` an `await` writes -- the wait does the rest (the opening waits with the answers),
    and the facilitator's answer to the opening resolves the task. The task is
    NAMED `<ceremony> YYYY-MM-DD HH:MM`, the local hour of the ring, and says a consigne."""
    task = next_task(state)
    facilitator = str(ceremony["facilitator"])
    at = tick_now().strftime("%Y-%m-%d %H:%M")
    asked, taking = consignes(team, ceremony, at)
    due = {"kind": "ceremony-due", "ceremony": ceremony["name"], "period": period}
    if by is not None:
        due["by"] = by
    events: list[dict] = [due,
                          {"kind": "task", "task": task, "from": team, "to": facilitator,
                           "ceremony": ceremony["name"], "period": period, "name": f"{ceremony['name']} {at}",
                           "text": asked},
                          {"kind": "post", "task": task, "from": team, "to": facilitator, "verb": "do", "text": asked}]
    for one in ceremony["participants"]:
        events.append({"kind": "post", "task": task, "from": facilitator, "to": one, "verb": "do",
                       "text": taking})
    if ceremony.get("quorum"):
        events.append({"kind": "wait", "agent": facilitator, "task": task, "any": ceremony["quorum"],
                       "to": list(ceremony["participants"])})
    return events


def live_recurrences(state: dict) -> list[dict]:
    """-> the recurrences of the team not stopped, in the order they were posted."""
    return [one for one in (state.get("recurrences") or {}).values() if one.get("stopped") is None]


def sounds_at(recurrence: dict, day) -> datetime:
    """-> the local date-time a recurrence's period of that day sounds at: the day, at the recurrence's hour."""
    hour, minute = (int(part) for part in str(recurrence["when"]["at"]).split(":"))
    return datetime(day.year, day.month, day.day, hour, minute)


def slot_of(recurrence: dict, now: datetime) -> tuple[int, datetime]:
    """-> the SLOT of a recurrence by a duration under way at `now` -- its rank k and its instant, `since + k x seconds`,
    k never under the recurrence's first (0 at the pose, 1 after a change that gave the duration)."""
    since = datetime.fromisoformat(str(recurrence["since"]))
    seconds = int(recurrence["when"]["seconds"])
    rank = max(int((now - since).total_seconds() // seconds), int(recurrence.get("first") or 0))
    return rank, since + timedelta(seconds=rank * seconds)


def slot_period(moment: datetime) -> str:
    """-> the period of a slot: its local instant `YYYY-MM-DDTHH:MM`."""
    return moment.isoformat(timespec="minutes")


def recurrence_period(recurrence: dict) -> str | None:
    """-> the period a live recurrence owes now, or None: its day conforms, its hour is past, that period sounds after
    the recurrence was posted (`since`) and it has not sounded yet -- by an occurrence or a skip. The period is the
    local date, as a ceremony's. By a DURATION, the slot under way alone -- its instant past and not sounded --: a
    slot that passed whole without a tick, or under a pause, never sounds later."""
    now = tick_now()
    if recurrence.get("stopped") is None and recurrence["when"].get("kind") == "interval":
        _, moment = slot_of(recurrence, now)
        period = slot_period(moment)
        return period if moment <= now and period not in recurrence["sounded"] else None
    if recurrence.get("stopped") is not None or not conforms(recurrence["when"], now):
        return None
    moment = sounds_at(recurrence, now.date())
    period = now.date().isoformat()
    if now >= moment and moment > datetime.fromisoformat(str(recurrence["since"])) \
            and period not in recurrence["sounded"]:
        return period
    return None


def recurrence_next(recurrence: dict) -> str | None:
    """-> the local date-time `YYYY-MM-DDTHH:MM` a live recurrence sounds at next: the first conforming day from today,
    its period not sounded and after `since`; by a duration, the slot under way while it is not sounded, else the slot
    after it; None once it is stopped."""
    if recurrence.get("stopped") is not None:
        return None
    if recurrence["when"].get("kind") == "interval":                 # the slot under way while it owes, else the next
        now = tick_now()
        _, moment = slot_of(recurrence, now)
        if moment <= now and slot_period(moment) in recurrence["sounded"]:
            moment += timedelta(seconds=int(recurrence["when"]["seconds"]))
        return slot_period(moment)
    since = datetime.fromisoformat(str(recurrence["since"]))
    today = tick_now().date()
    for ahead in range(8):
        day = today + timedelta(days=ahead)
        if (conforms(recurrence["when"], day) and day.isoformat() not in recurrence["sounded"]
                and sounds_at(recurrence, day) > since):
            return sounds_at(recurrence, day).isoformat(timespec="minutes")
    return None


def sounding(state: dict, recurrence: dict, period: str) -> list[dict]:
    """-> the events one period of a recurrence writes: its OCCURRENCE -- a task like one `post` opens, from the
    recurrence's principal to its member, NAMED `<name> YYYY-MM-DD HH:MM` (the recurrence's id without a name), with
    `recurrence` and `period`, then its opening `do` -- or, while the occurrence before it is still open,
    `recurrence-skipped {open}` and nothing opened: a member never holds the same work twice."""
    before = state["tasks"].get(recurrence.get("last") or "")
    if before is not None and before["state"] == "open":
        return [{"kind": "recurrence-skipped", "recurrence": recurrence["id"], "period": period, "open": before["id"]}]
    task = next_task(state)
    sender, to, text = recurrence.get("from"), recurrence.get("to"), recurrence.get("text")
    return [{"kind": "task", "task": task, "from": sender, "to": to,
             "name": f"{recurrence.get('name') or recurrence['id']} "
                     + (period.replace("T", " ") if recurrence["when"].get("kind") == "interval"
                        else f"{period} {recurrence['when']['at']}"), "text": text,
             "recurrence": recurrence["id"], "period": period},
            {"kind": "post", "task": task, "from": sender, "to": to, "verb": "do", "text": text}]


def sounded(conductor, name: str, journal: Path) -> int:
    """Step 4, after the ceremonies: each live recurrence whose period is due SOUNDS it -- once per period, the
    journal the judge, the period judged again under the journal's lock; a paused team sounds nothing. -> the events
    written."""
    count = 0
    for one in live_recurrences(state_of(journal)):
        if recurrence_period(one) is None:
            continue

        def judge(now_state: dict, events: list[dict], key=one["id"]) -> list[dict]:
            recurrence = now_state["recurrences"].get(key) or {}
            period = recurrence_period(recurrence) if recurrence else None
            return [] if now_state["paused"] or period is None else sounding(now_state, recurrence, period)
        count += len(written(conductor, journal, name, judge))
    return count


def rung(conductor, name: str, journal: Path) -> int:
    """Step 4: each ceremony whose period is due and not yet rung is RUNG -- once per period,
    the journal the judge: two ticks in one minute ring once. A paused team rings nothing, the pause
    judged under the journal's lock at the write. -> the events written."""
    state = state_of(journal)
    ceremonies = (state["started"] or {}).get("ceremonies") or []
    count = 0
    for one in ceremonies:
        state = state_of(journal)
        period = due_period(one, state)
        if period is not None:
            count += len(written(conductor, journal, name, lambda now_state, events, one=one, period=period:
                                 [] if now_state["paused"] else ringing(now_state, name, one, period)))
    return count


def launched(root: Path, conductor, name: str, started: dict, path: str, run: str | None,
             tag: str, message: str, allowance: float | None = None, member: str | None = None) -> tuple[dict | None, str]:
    """`agent start <path>` by the house's own console -- the agent that plays the member: the
    message, the tag, the on-end tick, the run to resume -- or, at an opening, the team's material
    (`work:`: a clone per member, `pp-agent`'s; a resume reopens its own) --, the launch flags kept
    at `team-started`, and the team's directory as the run's root of documents (`--documents`). No
    door: the entry is a successor the agent's DAG elects at every exchange (`documents_written`). Under an
    `allowance`, `--max-budget-usd` is the member's RUN cap: what the run spent plus the allowance; without
    one no cap is passed. The member's PROFILE at `team-started.profiles` replaces the team's provider, model,
    effort or permissions it names; the switches of the season -- the team's `--package`, covered name by name
    by the member's -- go as `--package <name>=on|off`, which the run's opening composes its first block with and
    a resume plays before its first launch. -> ({key, pid}, '') or (None, why)."""
    engine = engine_of(root, conductor)
    on_end = f"{shlex.quote(sys.executable)} {shlex.quote(str(engine))} --instance {shlex.quote(str(root))} team tick {name}"
    argv = [sys.executable, str(engine), "--instance", str(root), "agent", "start", path,
            "--message", message, "--tag", tag, "--on-end", on_end, "--documents", str(team_root(root, name))]
    if run:
        argv += ["--run", run]
    elif started.get("work"):
        argv += ["--work", str(material_of(root, str(started["work"])))]
    launch = dict(started.get("launch") or {})
    launch.pop("max_budget_usd", None)                   # an older journal's per-wake cap is never passed
    profile = profile_of(started, member)
    launch.update({key: profile[key] for key in PROFILE_KEYS if profile.get(key) is not None})
    if allowance is not None:
        spent = spent_on(state_of(journal_of(root, name)), run) if run else 0.0
        launch["max_budget_usd"] = round(spent + allowance, 6)
    argv += launch_flags(launch)
    for value in season_played(root, conductor, started, member):   # the season's set: one switch per pin
        argv += ["--package", value]
    played = subprocess.run(argv, capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return None, (played.stderr or played.stdout).strip()[-300:] or f"agent start rc {played.returncode}"
    try:
        report = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None, f"agent start reported `{played.stdout.strip()[:80]}`"
    return report, ""


def material_of(root: Path, work: str) -> Path:
    """-> the repository `work:` of TEAM.md names: absolute, `~` expanded, a relative path read
    from the house's root."""
    path = Path(work).expanduser()
    return path if path.is_absolute() else root.parent / path


def held_run(root: Path, conductor, path: str, run: str) -> bool:
    """-> whether the run's wake lock is held at the agent `path`: a wake-up of it plays, or has
    kept its answer and is still releasing -- the reap's own test. Resumed now, `agent start
    --run` would refuse `run-busy`; the end of that wake-up ticks once the lock is free."""
    return locks(conductor).held(launch_of(conductor, agent_meta(root, path), run))


def went(state: dict, tagged: set[str], tag: str) -> bool:
    """-> whether the intent was LAUNCHED: its `wake-launched` event, or its tag at the house's
    `messages.jsonl` (`tagged`: what the cursor read of it) -- the reap's own test. The bounds count
    these alone."""
    return tag in state["launched"] or tag in tagged


def woken(root: Path, conductor, name: str, journal: Path) -> int:
    """Step 5: each member, in the declaration's order, with messages due on its tasks, no launch of its
    under way and its run not held, is LAUNCHED once -- on the first task, in the tasks' order, whose
    wait is closed or carries a passing verb: the intent WRITTEN FIRST, then the launch, then
    `wake-launched` -- or `wake-failed` when the console launched nothing. Its other tasks wait for
    its next launch, each in the run of its carrier. A member whose run STANDS (its last launch left it waiting for a
    production: `wake-ended {state: standing}`) is RELAUNCHED on the task it stands on as soon as its
    wake lock is free, with `[nothing new]` at its head when nothing is due, unless its wait on that
    task holds -- a CONTINUATION, judged BEFORE any relance: a standing debtor continues, its debts under
    `[you still owe an answer to]`, never with the head of a relance. Before them, the SILENCES (`silences`): each
    debtor whose silent parked exchanges reached `silence:` + 1 falls -- `silence` written, the member suspected. A
    member at the bottom of the deadlocked set that OWES an answer and whose continuation launched nothing (no run
    standing, or its wait holds) is RELANCED (`relance_of`), without a count -- at `silence:` the relance is a
    REMINDER --: launched on the first task where it owes, its debts for messages, under every guard of a launch.
    Before all, the failure detector: each SUSPECTED member within its interval is answered for on the messages
    of members (`suspected_answers`) and launched on what a PRINCIPAL says to it alone -- that launch is its try;
    its interval passed, its next message is its try, and a member owing a principal's opening alone is tried by a
    relance on it (`tried_of`). The members play
    in parallel, one run each; `parallel:` bounds the team. `launches:` bounds the launches of one task
    and `budget-launches:` those of the season. A stopped task launches nobody -- but a run STANDING on it,
    launched ONE more time with the stop at its head (`dues`); under `work:` a run RELAUNCHABLE on its standing
    task takes no other task's head (one clone, one task at a time: T7) -- held by its `await`, or by that task's
    `launches:` spent, it does, as a run without `work:`: a member's other tasks never starve. A member whose share of the budget is all held by
    the launches under way is deferred; a paused team launches nobody. -> the events written."""
    count = 0
    state = state_of(journal)
    if state["paused"]:
        return 0
    started = state["started"] or {}
    tagged = set(messages_cursor(root, name, state))
    clock = tick_now()
    count += len(written(conductor, journal, name, lambda now_state, events: suspected_answers(now_state, clock)))
    fallen = False
    for agent in list(started.get("agents") or {}):
        fell = written(conductor, journal, name, lambda now_state, events: silences(now_state, name, clock, agent))
        if fell:                                                 # its silence fell: answered for at this very tick
            count += len(fell)
            count += len(written(conductor, journal, name, lambda now_state, events: suspected_answers(now_state, clock)))
            fallen = True
        now_state = state_of(journal)
        suspected = within(now_state, agent, clock)              # within its interval: what a principal says to it
        launched_now = 0                                         # launches it -- its try --, nothing else does
        for task, box in dues(now_state, agent):
            if not loud(now_state, box):                         # members' infos alone: they ride the head of its
                continue                                         # next launch, whatever its cause [114]
            if suspected and not any(is_principal(now_state, one.get("from")) for one in box):
                continue
            launched_now += woken_on(root, conductor, name, journal, started, tagged, agent, task)
        count += launched_now
        if suspected:
            continue
        if not launched_now:                                     # nothing received: its try, its continuation, else a relance
            now_state = state_of(journal)
            tried = tried_of(now_state, agent, clock) if suspicion_of(now_state, agent) is not None else None
            standing_on = now_state["standing"].get(agent)       # a run that stands: relaunched, nothing new
            if tried is None and standing_on is not None and is_open(now_state, standing_on):
                continued = woken_on(root, conductor, name, journal, started, tagged, agent, standing_on, standing=True)
                count += continued
                if continued:                                    # a standing debtor CONTINUES: never the head of a relance
                    continue
                now_state = state_of(journal)
            why = tried or relance_of(now_state, agent)          # a suspect past its interval: its TRY first; then a
            if why is not None:                                  # debtor whose continuation launched nothing (its wait holds)
                debts = owed_by(now_state, agent)
                key = next((one for one in debts if principal_opening(now_state, one)), debts[0]) if why[0] == "tried" else debts[0]
                task = now_state["messages"][key].get("task")
                count += woken_on(root, conductor, name, journal, started, tagged, agent, task, relance=why)
    if fallen:                                                   # a fall answered for a member judged already: once more
        count += woken(root, conductor, name, journal)
    return count


def woken_on(root: Path, conductor, name: str, journal: Path, started: dict, tagged: set[str],
             agent: str, task: str, relance: tuple[str, str | None] | None = None, standing: bool = False) -> int:
    """One (member, task) of step 5, judged on the state read again; the house is addressed by
    the member's path. The member's run for the task's CARRIER (`carrier_of`: the task, an occurrence's
    recurrence, a ring's ceremony) is resumed while its slot stands -- a renewal mark an upgrade left
    included --; none yet, its slot gone (`-reset`) or its run dropped (`team reset`), a new run OPENS, told
    the history of the carrier's open tasks, and is NAMED after the carrier (`run_named`) -- as it does at the first
    wake-up on a new occurrence once its recurrence's run reached its context limit (`renewal_of`, `run-renewed` written
    with the intent): a name the house
    refuses is said at `wake-launched` (`name-refused`), the launch plays on. A RELANCE (`relance`: its reason) carries
    the member's debts on the task as its messages and, as its inbox, the members' infos waiting there alone. A STANDING run (`standing`) is
    relaunched on the task it stands on with whatever is due there, `[nothing new]` when nothing is,
    unless its wait on that task holds. The launch is ONE launch of the harness (`--launches 1`); its
    `wake-launched` carries the launch's RANK in the run, and its FOLLOWER is spawned to read its flow
    while it plays. A launch the house refuses before any harness is no fall (`house_failed`). -> the events
    written."""
    count = 0
    state = state_of(journal)
    path = path_of(state, agent)
    if relance is None:
        box, carried = dict(dues(state, agent)).get(task) or [], []
        if not standing and not loud(state, box):
            return 0                                             # members' infos alone launch nobody [114]
    else:
        box = [one for one in dict(dues(state, agent)).get(task) or [] if quiet(state, one)]   # the infos ride its head
        carried = [key for key in owed_by(state, agent) if state["messages"][key].get("task") == task]
        judged = tried_of(state, agent, tick_now()) if relance[0] == "tried" else relance_of(state, agent)
        if judged != relance or not carried:
            return 0
    if standing and (state["standing"].get(agent) != task or run_held(state, agent, task) is None):
        return 0
    standing_on = state["standing"].get(agent)
    if (started.get("work") and relance is None and standing_on not in (None, task) and is_open(state, standing_on)
            and standing_on not in state["launches_spent"] and not wait_open(state, agent, standing_on)):
        return 0                                                 # under work: a run relaunchable on its standing task takes no
        #                                                          other task's head; held by its await or by the task's
        #                                                          bound, it does (no starvation)
    if not (box or carried or standing) or busy(state, agent):
        return 0
    kept = run_held(state, agent, task)                         # the run of the task's carrier
    if kept is not None and held_run(root, conductor, path, kept):
        return 0
    heard = loud(state, box)
    if wait_open(state, agent, task) and (not heard or all(held_by_wait(state, agent, task, one) for one in heard)):
        return 0
    per_task = state["limits"].get("launches")
    since = max(state["resumed"].get(task, 0),                  # a resume, or a season, counts afresh
                int((state["started"] or {}).get("id") or 0))
    task_wakes = sum(1 for tag, one in state["intents"].items()
                     if one.get("task") == task and int(one.get("id") or 0) > since and went(state, tagged, tag))
    if per_task is not None and task_wakes >= per_task:     # the task's launches are spent
        if task not in state["launches_spent"]:
            count += len(appended(conductor, journal, name, [
                {"kind": "launches-spent", "task": task, "spent": task_wakes, "launches": per_task},
                {"kind": "post", "task": task, "from": name, "to": str(started.get("owner")), "verb": "notice",
                 "text": f"the task's launches are spent: {task_wakes} of {per_task}; {agent} stays due on {task}"}]))
        return count
    budget = state["limits"].get("budget")
    if budget is not None and state["cost"] >= budget:        # the team has spent what it may
        if not state["budget_spent"]:
            count += len(appended(conductor, journal, name, [
                {"kind": "budget-spent", "spent": round(state["cost"], 6), "budget": budget},
                {"kind": "post", "task": task, "from": name, "to": str(started.get("owner")), "verb": "notice",
                 "text": f"the budget is spent: {state['cost']:g} of {budget:g} USD; {agent} stays due on {task}"}]))
        return count
    total_bound = state["limits"].get("budget-launches")
    since_start = sum(1 for tag, one in state["intents"].items()
                      if int(one.get("id") or 0) > int(started.get("id") or 0) and went(state, tagged, tag))
    if total_bound is not None and since_start >= total_bound:   # the costless bound, since the start
        if not state["budget_spent"]:
            count += len(appended(conductor, journal, name, [
                {"kind": "budget-spent", "spent": since_start, "budget": total_bound, "unit": "launches"},
                {"kind": "post", "task": task, "from": name, "to": str(started.get("owner")), "verb": "notice",
                 "text": f"the budget is spent: {since_start} of {total_bound} launches; {agent} stays due on {task}"}]))
        return count
    parallel = state["limits"].get("parallel")
    if parallel is not None and len(open_intents(state)) >= parallel:
        return len(appended(conductor, journal, name, [{"kind": "deferred", "agent": agent, "task": task}]))
    allowance = allowance_of(state, started) if measured(root, conductor, started) else None
    if allowance is not None and allowance <= 0:                 # the rest all held by the wake-ups under way
        return len(appended(conductor, journal, name, [{"kind": "deferred", "agent": agent, "task": task,
                                                        "reserved": reserved_of(state)}]))
    run = kept
    if run is not None and not conductor.persistence.slot_of(agent_meta(root, path), run).is_file():
        run = None                                               # forgotten (`-reset`): a new run
    renewal = renewal_of(state, agent, task, run)
    if renewal is not None:
        run = None                                               # past the recurrence's limit: a new run
    history = histories_of(state, agent, task) if run is None else ""   # an opening is told its carrier's past
    tag = f"{agent}-{task}-{secrets.token_hex(3)}"
    made = written(conductor, journal, name, lambda now_state, events: [] if now_state["paused"] else [
        *([renewal] if renewal is not None else []),
        {"kind": "wake-intent", "tag": tag, "agent": agent, "path": path, "task": task, "run": run,
         "messages": [one["id"] for one in box] if relance is None else carried + [one["id"] for one in box],
         **({"relance": relance[0]} if relance else {}),
         **({"allowance": allowance} if allowance is not None else {})}])
    if not made:
        return count                                             # paused meanwhile: nobody woken
    intent = made[-1]
    count += len(made)
    fresh = state_of(journal)
    cursor = cursor_of(fresh, agent, run, intent["id"])
    line = sharing_line(state, shared(fresh, agent, cursor), house_console(root, conductor), name, cursor)
    report, why = launched(root, conductor, name, started, path, run, tag,
                           headed(name, agent, box, line, history, fresh, relance, task), allowance, member=agent)
    if report is None:                                           # the house refused, before any harness: no fall
        return count + len(appended(conductor, journal, name, house_failed(state_of(journal), name, intent, why)))
    refused = "" if run else run_named(root, conductor, path, str(report.get("key")), carrier_name(fresh, name, carrier_of(fresh, task)))
    made = written(conductor, journal, name, lambda now_state, events: [
        {"kind": "wake-launched", "tag": tag, "agent": agent, "run": report.get("key"), "pid": report.get("pid"),
         "launch": launches_of_run(now_state, str(report.get("key"))) + 1,
         **({"name-refused": refused} if refused else {})}])
    following(root, conductor, name, tag)
    return count + len(made)


def renewal_of(state: dict, agent: str, task: str, run: str | None) -> dict | None:
    """-> the `run-renewed {member, recurrence, task, run, used, limit}` the member's wake-up on `task` writes before its
    intent, None when it resumes `run`: the task is an occurrence whose recurrence carries a context limit, this is the
    member's FIRST wake-up on it -- an occurrence is never cut between two runs --, and the last measure of `run` (the
    last `wake-ended` of that run that carries a context, read from the journal alone) reached the limit. Without a
    limit, without a measure, or under it, the run is resumed."""
    recurrence = state["recurrences"].get((state["tasks"].get(task) or {}).get("recurrence"))
    if run is None or recurrence is None or recurrence.get("context") is None:
        return None
    if any(one.get("agent") == agent and one.get("task") == task for one in state["intents"].values()):
        return None
    measure = next((one["context"] for one in reversed(state["ends"])
                    if one.get("run") == run and isinstance(one.get("context"), dict)), None)
    used = (measure or {}).get("used")
    if not isinstance(used, (int, float)) or used * 100 < recurrence["context"]:
        return None
    return {"kind": "run-renewed", "member": agent, "recurrence": recurrence["id"], "task": task, "run": run,
            "used": used, "limit": recurrence["context"]}


def dues(state: dict, agent: str) -> list[tuple[str, list[dict]]]:
    """-> what a launch of the agent would deliver, task by task in the tasks' order: (task, its inbox
    on that task) for each task that has some -- a stopped task has none to deliver, its stop delivered
    at once, unless the agent's run STANDS on it: then its stop alone, the head of one more launch
    (the run parks there)."""
    waiting = inbox(state, agent)
    found = []
    for task, held in state["tasks"].items():
        if held.get("state") == "resolved":
            continue
        box = [one for one in waiting if one.get("task") == task]
        if held.get("state") == "stopped":
            box = [one for one in box if one.get("verb") == "stop" and state["standing"].get(agent) == task]
        if box:
            found.append((task, box))
    return found


def quiet(state: dict, one: dict) -> bool:
    """-> whether a message launches nobody: a MEMBER's `info` -- it waits in its recipient's box and rides the head of
    its next launch, whatever its cause; an `info` of a principal or of the team is due as any message (row 114)."""
    return one.get("verb") == "info" and is_member(state, one.get("from"))


def loud(state: dict, box: list[dict]) -> list[dict]:
    """-> the messages of a box that make their recipient due: every one but the members' `info`s (`quiet`)."""
    return [one for one in box if not quiet(state, one)]


def ticked(root: Path, conductor, name: str, hint: tuple[str, str] | None = None) -> int:
    """ONE advance of the team under `tick.lock`, taken without waiting: held, the mark is
    posted and the tick leaves; the holder clears the mark, plays reap, waits, ring, wake and the net
    (the relaunch entry removed and the timer disarmed at `schedule-off`, the timer armed
    when a deadline stands), releases, then reads the mark and plays again when it is set. `hint` is what
    an on-end tick carries of the launch that fired it: `(run, state)`. -> the events written."""
    journal = journal_of(root, name)
    if state_of(journal)["started"] is None:
        print(f"pp-team: {name} · not started: nothing to advance")
        return 0
    lock = locks(conductor)
    home = journal.parent
    home.mkdir(parents=True, exist_ok=True)
    path, mark = home / TICK_LOCK, home / TICK_MARK
    lease = lock.try_(path)
    if lease is None:
        try:
            with open(mark, "x", encoding="utf-8") as handle:
                handle.write(now() + "\n")
        except FileExistsError:
            pass
        lease = lock.try_(path)
        if lease is None:
            print(f"pp-team: {name} · a tick plays: marked pending")
            return 0
    count, rounds = 0, 0
    while True:
        mark.unlink(missing_ok=True)
        rounds += 1
        count += reaped(root, conductor, name, journal, hint)
        hint = None
        count += waits_met(conductor, name, journal)
        count += rung(conductor, name, journal)
        count += sounded(conductor, name, journal)
        count += woken(root, conductor, name, journal)
        if netless(state_of(journal)):             # 7. the net, under the lock: a tick that arms and one that
            relaunch_removed(root, conductor, name)   # disarms never cross -- the condition of schedule-off: the
            disarmed(root, name)                   # net leaves with it
        else:
            count += armed(root, conductor, name, journal)   # the timer, when a deadline stands
        lock.release(lease)
        if not mark.exists():
            break
        lease = lock.try_(path)
        if lease is None:
            break                                              # the tick that marked plays now
    print(f"pp-team: {name} · tick · {count} event(s) written in {rounds} round(s)")
    if state_of(journal)["paused"]:
        print(f"pp-team: {name} · paused: nobody woken until team resume")
    return count


def tick(rest: list[str]) -> int:
    global TIMER_TICKING
    TIMER_TICKING = os.environ.pop(TIMER_ENV, "") == "1"     # the timer's own tick: taken out, no child inherits it
    root, conductor = house()
    if rest == ["--all"]:
        for name in needing(root):                 # the house's relaunch entry at logon: every team in need
            try:
                ticked(root, conductor, name)
            except SystemExit as failed:           # a team that refuses is said; the others advance
                if failed.code not in (0, None):
                    sys.stderr.write(f"pp-team: {name} · tick failed, the other teams advance\n")
        return 0
    name, rest = named_team(conductor, rest)
    if rest:
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    run, said = os.environ.get("PP_AGENT_RUN", "").strip(), os.environ.get("PP_AGENT_STATE", "").strip()
    ticked(root, conductor, name, (run, said) if run and said else None)   # an on-end tick says its launch's end
    return 0


# --- the verbs -----------------------------------------------------------------------------

MEMBER_FLAGS = {"provider": True, "model": True, "effort": True, "permissions": True, "package": True, "silence": True}


def season_flags(rest: list[str]) -> tuple[list[str], list[str], dict]:
    """-> (the team's flags, the team's packages, the members' profiles): what follows a `--member <name>` up to the
    next one is that member's -- `--provider`, `--model`, `--effort`, `--permissions` and `--package <name>=on|off`
    repeated --, as `{member: {key: value, packages: [...]}}`; the flags before the first `--member` are the team's,
    its `--package <name>=on|off`, repeated, taken apart as the team's packages. Anything else is the usage."""
    at, team_part, packages, profiles = 0, [], [], {}
    while at < len(rest) and rest[at] != "--member":
        if rest[at] == "--package":
            if at + 1 >= len(rest):
                refuse(USAGE)
            packages.append(rest[at + 1])
            at += 2
            continue
        team_part.append(rest[at])
        at += 1
    while at < len(rest):
        if at + 1 >= len(rest) or rest[at + 1].startswith("--"):
            refuse(USAGE)
        profile = profiles.setdefault(rest[at + 1], {})
        at += 2
        while at < len(rest) and rest[at] != "--member":
            key = rest[at][2:] if rest[at].startswith("--") else ""
            if key not in MEMBER_FLAGS or at + 1 >= len(rest):
                refuse(USAGE)
            if key == "package":
                profile.setdefault("packages", []).append(rest[at + 1])
            else:
                profile[key] = rest[at + 1]
            at += 2
    return team_part, packages, profiles


def season_of(asked: dict) -> dict:
    """-> the season's own limits, `{budget, budget-launches, silence}` -- the ones given, each judged: a number of
    dollars above 0, whole numbers of 1 or more (`budget-invalid`, `team-invalid` for `--silence`)."""
    found: dict = {}
    if asked["budget"] is not None:
        try:
            found["budget"] = float(asked["budget"])
        except ValueError:
            found["budget"] = 0.0
        if not found["budget"] > 0:
            refuse(f"budget-invalid -- `--budget {asked['budget']}`: a number of dollars above 0.")
    if asked["budget-launches"] is not None:
        if not str(asked["budget-launches"]).isdigit() or int(asked["budget-launches"]) < 1:
            refuse(f"budget-invalid -- `--budget-launches {asked['budget-launches']}`: a whole number of 1 or more.")
        found["budget-launches"] = int(asked["budget-launches"])
    if asked.get("silence") is not None:
        if not str(asked["silence"]).isdigit() or int(asked["silence"]) < 1:
            refuse(f"team-invalid -- `--silence {asked['silence']}`: a whole number of 1 or more.")
        found["silence"] = int(asked["silence"])
    return found


def manifests_named(root: Path, conductor) -> dict[str, Path]:
    """-> {package name: its vendored root} over the house's WHOLE composition, switched off included."""
    named: dict = {}
    for package_root in conductor.instance.vendored(root, switched=False):
        try:
            named[str(conductor.instance.manifest_of(package_root)["name"])] = package_root
        except conductor.Refusal:
            continue
    return named


def required_by_team(root: Path, conductor) -> set[str]:
    """-> `team` and every package it requires, transitively, as the house's manifests say them
    (`topology.closure`)."""
    return conductor.topology.closure(manifests_named(root, conductor), "team")


def switches_composed(*lists: list) -> dict[str, str]:
    """-> `{name: "on"|"off"}` from lists of `<name>=on|off`, each later list covering the earlier name by name, the
    last word on a name winning within a list; the order is the order the names first came."""
    found: dict[str, str] = {}
    for values in lists:
        for value in values or []:
            name, _, state = str(value).partition("=")
            found[name] = state
    return found


def season_switches(started: dict, member: str | None = None) -> dict[str, str]:
    """-> the switches the season gives a member's wake-up, `{name: "on"|"off"}`: the team's packages
    (`team-started.packages`), covered name by name by the member's profile; the team's alone without a member."""
    return switches_composed(started.get("packages") or [], profile_of(started, member).get("packages") or [])


def season_set(root: Path, conductor, switches: dict[str, str]) -> list[str]:
    """-> the SET of a member's packages a season gives, `[<name>=on|off, ...]`: one per pin of the house beyond its
    base, in the pins' order -- `on` when `switches` switches it on or the team requires it (`required_by_team`),
    `off` otherwise. The one rule of a season's packages: `start` writes it, and a journal of before, whose list
    names some pins alone, is read under it -- a pin it does not name is off. The member's SETTINGS plays no part."""
    instance = conductor.instance
    base, needed = instance.base_of(root), required_by_team(root, conductor)
    return [f"{name}={switches.get(name) or ('on' if name in needed else 'off')}"
            for name in instance.pins(root) if name != base]


def set_of(values: list) -> dict[str, str]:
    """-> `{name: on|off}` of a set (`season_set`), in its order."""
    return switches_composed(values)


def season_played(root: Path, conductor, started: dict, member: str | None = None) -> list[str]:
    """-> the set a member's wake-up plays: the season's lists at `team-started` (`season_switches`) read under the
    rule of the set (`season_set`) -- the journal's set itself, every pin of a journal of before named."""
    return season_set(root, conductor, season_switches(started, member))


def profiles_judged(root: Path, conductor, team: dict, packages: list, profiles: dict) -> None:
    """Judges the team's packages and the members' profiles before any write: a member nobody declared
    (`participant-unknown`), a switch off its form (`package-invalid`), a package the team needs switched off
    (`package-required` -- `team` and what it requires), a package the house does not pin switched on
    (`package-unpinned`), a package switched on whose requirement the season's SET -- the team's switches covered by
    the member's, every other pin off unless the team requires it (`season_set`) -- switches off
    (`package-dependency`). A package the house does not pin, switched off, asks nothing: it leaves the set."""
    if not packages and not profiles:
        return
    named = manifests_named(root, conductor)
    needed = conductor.topology.closure(named, "team")
    pinned = set(conductor.instance.pins(root))

    def judged(values: list, whom: str) -> None:
        for value in values or []:
            package, _, state = str(value).partition("=")
            if not package or state not in ("on", "off"):
                refuse(f"package-invalid -- `--package {value}` for {whom}: the form is <name>=on or <name>=off.")
            if state == "off" and package in needed:
                refuse(f"package-required -- `{package}` cannot be switched off for {whom}: the team needs it "
                       f"({', '.join(sorted(needed))}).")
            if package not in pinned and state == "on":
                refuse(f"package-unpinned -- `{package}` is not pinned by the house: the packages it pins are "
                       f"{', '.join(sorted(pinned))}.")

    def dependent(composed: dict, whom: str) -> None:
        off = {name for name, state in composed.items() if state == "off"}
        for name, state in composed.items():
            if state != "on":
                continue
            lacking = sorted((conductor.topology.closure(named, name) - {name}) & off)
            if lacking:
                refuse(f"package-dependency -- `{name}=on` for {whom} needs {', '.join(lacking)}, which the season "
                       "switches off: a package never plays without what it requires.")

    judged(packages, "the team")
    dependent(set_of(season_set(root, conductor, switches_composed(packages))), "the team")
    for member, profile in profiles.items():
        if member not in team["agents"]:
            refuse(f"participant-unknown -- `--member {member}` names a member nobody declared.")
        if profile.get("silence") is not None:
            if not str(profile["silence"]).isdigit() or int(profile["silence"]) < 1:
                refuse(f"team-invalid -- `--member {member} --silence {profile['silence']}`: a whole number of 1 or more.")
            profile["silence"] = int(profile["silence"])
        judged(profile.get("packages") or [], member)
        dependent(set_of(season_set(root, conductor, switches_composed(packages, profile.get("packages") or []))),
                  member)


def held_by_dropped(state: dict, team: dict) -> list[tuple[str, str]]:
    """-> (member, task) of each member the new `TEAM.md` drops while it holds an open task."""
    before = list(((state["started"] or {}).get("agents") or {}))
    dropped = [one for one in before if one not in team["agents"]]
    return [(member, task["id"]) for task in state["tasks"].values() if task["state"] == "open"
            for member in holders(state, task) if member in dropped]


def start(rest: list[str]) -> int:
    """`team start`: a SEASON of the team -- the first, or one more on a team at work. `TEAM.md` read whole and
    judged, the season's budget, the team's packages, the members' profiles and the gestures judged before any
    write; then the agents the house lacks born, the team's documents written, `team-started` (its `season`,
    `packages` and `profiles` when given)
    and, under `--message`, a task and its `do` -- without it no task opens, the season stands on its ceremonies and
    the posts to come; the relaunch entry laid under an open task or a declared ceremony, the first `post` laying it
    otherwise; a tick unless `--no-tick`. The members keep their runs."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if "--max-budget-usd" in rest:
        refuse("flag-retired -- `--max-budget-usd`: no cap per wake-up any more -- a wake-up's share is computed on "
               "the team's `budget:` of TEAM.md (each its part of the rest), and `team budget` raises it.")
    retired_flags(rest)
    team_part, packages, profiles = season_flags(rest)
    asked = flags(team_part, START_FLAGS)
    if asked["harness"] is not None and asked["provider"] is None:   # every wake-up would refuse it: said once, here
        refuse("grammar-missing -- `--harness` runs a caller's command at every wake-up: name the grammar its "
               "output is read in with `--provider <name>` beside it -- the provider whose adapter reads it.")
    season = season_of(asked)
    team = declared(root, conductor, name)
    profiles_judged(root, conductor, team, packages, profiles)
    packages = season_set(root, conductor, switches_composed(packages))   # the season's SET, written whole
    for profile in profiles.values():
        if profile.get("packages"):
            profile["packages"] = season_set(root, conductor, switches_composed(packages, profile["packages"]))
    journal = journal_of(root, name)
    before = state_of(journal)
    standing = [one["id"] for one in before["tasks"].values() if one["state"] == "open"]
    held = held_by_dropped(before, team)
    if held:
        refuse(f"member-held -- TEAM.md drops {held[0][0]}, which holds {held[0][1]}: a season loses no work -- "
               "keep the member until the task ends, or stop it.")
    naming = named(conductor, asked) if asked["message"] is not None else {}
    target = asked["to"] or team["root"]
    if target not in team["agents"]:
        refuse(f"participant-unknown -- `--to {target}` names a member nobody declared.")
    entries_judged(root, conductor, name, team)
    if not (team_root(root, name) / document_name(name)).is_file():
        refuse(f"team-document-missing -- no {team_root(root, name) / document_name(name)}: the team's intention "
               "lives there, its body -- write it (empty is allowed), then start again.")
    created = born(root, conductor, list(team["agents"].values()))
    documents_written(root, name, team)
    cleared(root, name, team)
    owner = owner_of(root, conductor)
    launch = {key: asked[flag] for key, flag in (("harness", "harness"), ("provider", "provider"), ("model", "model"),
                                                  ("permissions", "permissions"), ("effort", "effort"))
              if asked[flag] is not None}

    def judge(state: dict, events: list[dict]) -> list[dict]:
        made = [{"kind": "team-started", "agents": team["agents"], "reports": team["reports"], "root": team["root"],
                 "principals": team["principals"], "owner": owner, "ceremonies": team["ceremonies"],
                 "entries": team["entries"], "work": team["work"],
                 "launch": launch, "limits": team["limits"],
                 **({"season": season} if season else {}), "packages": packages,
                 **({"profiles": profiles} if profiles else {}),
                 "schedule": team["schedule"], "unit": "s", "digest": team["digest"]}]
        if asked["message"] is not None:
            task = next_task(state)
            made += [{"kind": "task", "task": task, "from": owner, "to": target, **naming, "text": asked["message"]},
                     {"kind": "post", "task": task, "from": owner, "to": target, "verb": "do", "text": asked["message"]}]
        return made

    made = written(conductor, journal, name, judge)
    said = (f" · task {made[1]['task']} to {target} · post #{made[2]['id']} do {owner} -> {target}"
            if len(made) > 1 else " · no task opened" + (f", {', '.join(standing)} open" if standing else ""))
    print(f"pp-team: {name} started · members {', '.join(team['agents'])}"
          + (f" (born: {', '.join(created)})" if created else " (all standing)") + said)
    if team["schedule"] is not None and not netless(state_of(journal)):   # the relaunch entry under a task, a
        relaunch_said(root, conductor, name, journal)                    # ceremony or a recurrence; the first post
        #                                                                  lays it otherwise; the tick arms the timer
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def principal_of(state: dict, owner: str, asked: str | None) -> str:
    """-> who posts: the mandator `--as` names (declared under `principals:`) or the owner."""
    if asked is None:
        return owner
    allowed = [owner] + list((state["started"] or {}).get("principals") or [])
    if asked not in allowed:
        refuse(f"principal-unknown -- `--as {asked}`: the principals are {', '.join(allowed)} (the owner, then "
               "`principals:` of TEAM.md).")
    return asked


def limit_of(text: str, off: bool = False) -> int | None:
    """-> the context limit `--context` says: a whole percentage of the window from 1 to 99, `70` worth `70%`; None for
    `off` where `off` is allowed (the limit taken away); `context-invalid` otherwise."""
    said = text.strip()
    if off and said == "off":
        return None
    number = said[:-1] if said.endswith("%") else said
    if not number.isdigit() or not 1 <= int(number) <= 99:
        refuse(f"context-invalid -- `--context {said[:20]}`: a recurrence's context limit is a share of the window, "
               "1% to 99%" + (", or off" if off else "") + ".")
    return int(number)


def post(rest: list[str]) -> int:
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, POST_FLAGS)
    if asked["reply"] is not None and (asked["task"] is None or asked["stop"]):
        refuse(USAGE)
    if asked["name"] is not None and asked["task"] is not None:   # a name is given at a task's birth alone
        refuse(USAGE)
    if asked["every"] is not None and (asked["task"] is not None or asked["reply"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a recurrence is laid on a task to come alone
    if asked["context"] is not None and asked["every"] is None:
        refuse(USAGE)                                             # a context limit is a recurrence's alone
    limit = limit_of(asked["context"]) if asked["context"] is not None else None
    when = None
    if asked["every"] is not None:
        when = every_of(asked["every"])
    if asked["message"] is None and not asked["stop"]:
        refuse("message-missing -- a post carries its text: --message <text> (optional under --stop).")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)
    naming = named(conductor, asked)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        started = state["started"]
        if started is None:
            refuse(f"team-not-started -- {name} was never started: `team start {name} --message …` first.")
        agents = list(started.get("agents") or {})
        sender = principal_of(state, owner, asked["as"])
        if asked["to"] is not None and asked["to"] not in agents:
            refuse(f"participant-unknown -- `--to {asked['to']}` names a member nobody declared.")
        if when is not None:                      # a recurrence: nothing opens now, the tick sounds its periods
            return [{"kind": "recurrence", "recurrence": f"R{len(state['recurrences']) + 1}", "from": sender,
                     "to": asked["to"] or str(started.get("root")), **naming, "text": asked["message"], "when": when,
                     "since": tick_now().isoformat(timespec="seconds"), "context": limit}]
        if asked["task"] is None:
            target = asked["to"] or str(started.get("root"))
            task = next_task(state)
            return [{"kind": "task", "task": task, "from": sender, "to": target, **naming, "text": asked["message"]},
                    {"kind": "post", "task": task, "from": sender, "to": target, "verb": "do", "text": asked["message"]}]
        task = state["tasks"].get(asked["task"])
        if task is None:
            refuse(f"task-unknown -- no task `{asked['task']}` of {name}: the tasks are "
                   f"{', '.join(state['tasks']) or 'none'}.")
        if task["state"] in CLOSED:
            refuse(f"task-closed -- {task['id']} is {task['state']}: a post opens a new task instead.")
        verb, cited = "info", None
        target = asked["to"] or task["to"]
        if asked["stop"]:
            text = asked["message"] if asked["message"] is not None else ""
            return stopping(state, task, sender, text, [target] if asked["to"] else holders(state, task))
        if asked["reply"] is not None:
            try:
                cited = int(asked["reply"].lstrip("#"))
            except ValueError:
                cited = -1
            answered = state["messages"].get(cited)
            if answered is None or answered.get("task") != task["id"]:
                refuse(f"message-unknown -- no post #{asked['reply']} on {task['id']}.")
            verb = "re"
            if asked["to"] is None and answered.get("from") in agents:
                target = str(answered["from"])
            elif asked["to"] is None and answered.get("about") in agents:
                target = str(answered["about"])
        one = {"kind": "post", "task": task["id"], "from": sender, "to": target, "verb": verb,
               "text": asked["message"] if asked["message"] is not None else ""}
        if cited is not None:
            one["re"] = cited
        return [one]

    made = written(conductor, journal, name, judge)
    if made[0]["kind"] == "recurrence":
        print(f"pp-team: {name} · recurrence {made[0]['recurrence']} to {made[0]['to']} · every "
              f"{said_when(made[0]['when'])}"
              + (f" · context {made[0]['context']}%" if made[0]["context"] is not None else "")
              + f" · #{made[0]['id']} -- the tick opens one task per period")
    if made[0]["kind"] == "task":
        print(f"pp-team: {name} · task {made[0]['task']} to {made[0]['to']} · post #{made[1]['id']} do "
              f"{made[1]['from']} -> {made[1]['to']}")
    for one in made:
        if one["kind"] == "stopped":
            posted = any(other["kind"] == "post" for other in made)
            print(f"pp-team: {name} · {one['task']} · stopped #{one['id']}" + ("" if posted else " -- nobody held it"))
        elif one["kind"] == "post" and made[0]["kind"] != "task":
            print(f"pp-team: {name} · {one['task']} · post #{one['id']} {one['verb']} {one['from']} -> {one['to']}")
        elif one["kind"] == "returned":
            print(f"pp-team: {name} · post #{one['message']} returned to {one['to']}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # a post lays the net again when it finds it gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def holders(state: dict, task: dict) -> list[str]:
    """-> the agents holding the task: its agent unless it is terminal on it, then every delegate
    on it without a terminal, in the order of their delegations."""
    found = [] if (task["to"], task["id"]) in state["terminals"] else [str(task["to"])]
    for one in state["delegations"]:
        if one["task"] == task["id"] and (one["to"], task["id"]) not in state["terminals"] and one["to"] not in found:
            found.append(str(one["to"]))
    return found


def stopping(state: dict, task: dict, sender: str, text: str, to: list[str]) -> list[dict]:
    """-> the events that stop a task: `stopped {task, by}` -- the task stops whatever holds it --,
    then a `stop` post to each agent named (none when nobody holds the task), then a `returned`
    for every post left undelivered on the task, to its author."""
    events: list[dict] = [{"kind": "stopped", "task": task["id"], "by": sender}]
    events += [{"kind": "post", "task": task["id"], "from": sender, "to": one, "verb": "stop", "text": text}
               for one in to]
    for mid in task["messages"]:
        one = state["messages"][mid]
        if mid not in state["delivered"]:
            events.append({"kind": "returned", "message": mid, "to": one.get("from")})
    return events


def ended_now(pid: int) -> bool:
    """Ends a detached launcher by its process group -- the launcher, the harness it runs and
    what that runs. -> False when the group was gone already. Windows: `taskkill /T`."""
    if os.name == "nt":
        return subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True).returncode == 0
    try:
        os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def kills(root: Path, conductor, name: str, state: dict, task: str, said: list[str]) -> list[dict]:
    """-> `wake-killed` for every launch under way on the task whose flow says no end, its launcher
    ended by its process group; a launch that answered (its `response` at the flow) is spared -- the reap
    ends it, its cost counted --; a launcher gone already, or not launched yet, is said and left to the
    reap."""
    events = []
    for one in open_intents(state):
        if one["task"] != task:
            continue
        launch = state["launched"].get(one["tag"]) or messages_cursor(root, name, state).get(one["tag"]) or {}
        pid = launch.get("pid")
        if launch.get("run") and answered_in_flow(root, conductor, state, one, launch):
            said.append(f"{task} · {one['agent']} has answered: spared -- the reap ends it")
        elif not isinstance(pid, int):
            said.append(f"{task} · {one['agent']} not launched yet: it ends on its own")
        elif ended_now(pid):
            said.append(f"{task} · killed {one['agent']} (pid {pid}, run {launch.get('run')})")
            events.append({"kind": "wake-killed", "tag": one["tag"], "agent": one["agent"], "task": task,
                           "run": launch.get("run"), "pid": pid})
        else:
            said.append(f"{task} · {one['agent']}'s pid {pid} is gone already")
    if not any(line.startswith(f"{task} · killed") for line in said):
        said.append(f"{task} · nothing to kill")
    return events


def stop(rest: list[str]) -> int:
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, STOP_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    said: list[str] = []
    if asked["recurrence"] is not None and (asked["task"] is not None or asked["kill"]):
        refuse(USAGE)                                             # a recurrence stops alone: its occurrence by --task

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if asked["recurrence"] is not None:
            recurrence = state["recurrences"].get(asked["recurrence"])
            if recurrence is None:
                refuse(f"recurrence-unknown -- no recurrence `{asked['recurrence']}` of {name}: the recurrences are "
                       f"{', '.join(state['recurrences']) or 'none'}.")
            if recurrence["stopped"] is not None:
                refuse(f"recurrence-stopped -- {recurrence['id']} was stopped at #{recurrence['stopped']['id']}.")
            return [{"kind": "recurrence-stopped", "recurrence": recurrence["id"], "by": owner}]
        if asked["task"] is not None:
            task = state["tasks"].get(asked["task"])
            if task is None:
                refuse(f"task-unknown -- no task `{asked['task']}` of {name}.")
            if task["state"] in CLOSED:
                refuse(f"task-closed -- {task['id']} is {task['state']} already.")
            chosen = [task]
        else:
            chosen = [one for one in state["tasks"].values() if one["state"] == "open"]
        made: list[dict] = []
        for task in chosen:
            if asked["kill"]:
                made += kills(root, conductor, name, state, task["id"], said)
            made += stopping(state, task, owner, "", holders(state, task))
        return made

    made = written(conductor, journal_of(root, name), name, judge)
    if not made:
        print(f"pp-team: {name} · no open task")
        return 0
    if made[0]["kind"] == "recurrence-stopped":
        print(f"pp-team: {name} · recurrence {made[0]['recurrence']} stopped #{made[0]['id']} -- its open occurrence "
              "lives on")
    for line in said:
        print(f"pp-team: {name} · {line}")
    for one in made:
        if one["kind"] == "stopped":
            posted = any(other["kind"] == "post" and other.get("task") == one["task"] for other in made)
            print(f"pp-team: {name} · {one['task']} · stopped #{one['id']}" + ("" if posted else " -- nobody held it"))
        elif one["kind"] == "post":
            print(f"pp-team: {name} · {one['task']} · post #{one['id']} stop {one['from']} -> {one['to']}")
        elif one["kind"] == "returned":
            print(f"pp-team: {name} · post #{one['message']} returned to {one['to']}")
    if netless(state_of(journal_of(root, name))):
        relaunch_removed(root, conductor, name)    # the last task stopped, no ceremony: the net leaves
        disarmed(root, name)
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def snapshot_verb(rest: list[str]) -> int:
    """`team snapshot <name>`: ONE `snapshot {upto, state}` event, written under the
    journal's lock -- the replay restarts there; nothing is rewritten, no reader changes."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if rest:
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started: `team start {name} --message …` first.")
        last = max((int(one.get("id") or 0) for one in events), default=0)
        return [{"kind": "snapshot", "upto": last, "state": packed(state)}]

    made = written(conductor, journal_of(root, name), name, judge)
    print(f"pp-team: {name} · snapshot #{made[0]['id']} upto #{made[0]['upto']}")
    return 0


def counted(messages: list[dict]) -> str:
    """-> `do 1, note 2`: the messages by verb, in the order the verbs appear."""
    seen: dict[str, int] = {}
    for one in messages:
        seen[one.get("verb", "?")] = seen.get(one.get("verb", "?"), 0) + 1
    return ", ".join(f"{verb} {count}" for verb, count in seen.items())


def changed_since_start(root: Path, name: str, started: dict) -> bool:
    """-> whether `TEAM.md` differs from the `digest` its start kept."""
    return bool(started.get("digest")) and (
        hashlib.sha256(team_doc(root, name).read_bytes()).hexdigest()[:12] != started["digest"])


def waited_by(state: dict, member: str) -> list[str]:
    """-> the delegates the member waits for on open tasks: no terminal yet, sorted."""
    return sorted({one["to"] for one in state["delegations"] if one["from"] == member
                   and is_open(state, one["task"]) and (one["to"], one["task"]) not in state["terminals"]})


def owner_box(state: dict, owner: str) -> list[dict]:
    """-> the posts to the owner and the posts returned to them, in the journal's order."""
    return [one for one in state["messages"].values()
            if one.get("to") == owner or state["returned_to"].get(one["id"]) == owner]


def status_of(root: Path, conductor, name: str) -> int:
    """`team status <name>`: the state read from the journal -- nothing written."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    started = state["started"]
    if started is None:
        print(f"team {name} · declared, not started")
        return 0
    principals = list(started.get("principals") or [])
    owner = str(started.get("owner"))
    print(f"team {name} · owner {owner} · principals {', '.join(principals) or '—'}"
          f" · started {started.get('at')} (#{started.get('id')})")
    paused = state["paused"]
    if paused:
        print(f"paused since {paused.get('at')} by {paused.get('by')} (#{paused.get('id')}) · nobody is woken "
              f"until team resume")
    if changed_since_start(root, name, started):
        print("TEAM.md changed since the start · the body reaches the members at their next exchange · "
              "the front matter waits a stop then a start")
    limits = state["limits"]
    if limits:
        said = [f"parallel {limits['parallel']}" if "parallel" in limits else "",
                f"budget {limits['budget']:g} USD" if "budget" in limits else "",
                f"retries {limits['retries']}" if "retries" in limits else "",
                f"timeout {limits['timeout']:g}" if "timeout" in limits else "",
                f"launches {limits['launches']}" if "launches" in limits else "",
                f"budget-launches {limits['budget-launches']}" if "budget-launches" in limits else "",
                f"suspect-max {limits['suspect-max']} s" if "suspect-max" in limits else "",
                f"silence {limits['silence']}" if "silence" in limits else ""]
        print("limits · " + " · ".join(one for one in said if one))
    seasons = int(state.get("seasons") or 1)
    if seasons > 1 or started.get("season") or started.get("profiles"):
        own = started.get("season") or {}
        print(f"season {seasons} · since {started.get('at')}"
              + (f" · budget {own['budget']:g} USD" if own.get("budget") is not None else "")
              + (f" · budget-launches {own['budget-launches']}" if own.get("budget-launches") is not None else "")
              + (f" · silence {own['silence']}" if own.get("silence") is not None else "")
              + (f" · profiles {', '.join(started.get('profiles') or {})}" if started.get("profiles") else ""))
    retired = (started.get("launch") or {}).get("max_budget_usd")
    if retired is not None:
        print(f"launch · the start's --max-budget-usd {float(retired):g} is never passed: a wake-up's share is "
              "computed on budget:")
    seconds = schedule_seconds(started)
    if seconds is None:
        print("schedule · off")
    else:
        face = schedule_face(root, name, started, state)
        print(f"schedule · every {seconds} s · " + ("timer armed" if face["timer"] else "no timer") + " · relaunch "
              + ("laid" if face["relaunch"] else "absent" + (f" ({face['reason']})" if face["reason"] else "")))
    print(f"cost {state['cost']:.2f} USD" + (" · budget spent" if state["budget_spent"] else ""))
    share = share_of(state)
    if share is not None:
        print(f"budget {share['spent']:g}/{share['cap']:g} USD · reserved {share['reserved']:.2f} · "
              f"left {share['left']:.2f}")
    for one in state["recurrences"].values():
        last = state["tasks"].get(one.get("last") or "")
        print(f"{one['id']}" + (f" {one['name']}" if one.get("name") else "")
              + f" · every {said_when(one['when'])} · to {one['to']}"
              + (f" · from {one['task']}" if one.get("task") else "")
              + (f" · context {one['context']}%" if one.get("context") is not None else "")
              + (f" · stopped #{one['stopped']['id']}" if one["stopped"] else f" · next {recurrence_next(one)}")
              + (f" · last {last['id']} {last['state']}" if last else ""))
    for task in state["tasks"].values():
        resumed = state["resumed"].get(task["id"]) if task["state"] == "open" else None
        print(f"{task['id']}" + (f" {task['name']}" if task.get("name") else "") + f" · {task['state']}"
              + (f" · resumed #{resumed}" if resumed else "") + (f" · of {task['recurrence']}" if task.get("recurrence") else "")
              + f" · to {task['to']} · {len(task['messages'])} message(s)")
    for agent in started.get("agents") or {}:
        waiting = inbox(state, agent)
        line = (f"{agent} · {path_of(state, agent)} · inbox {len(waiting)}"
                + (f" ({counted([worded(state, one) for one in waiting])})" if waiting else ""))
        held = run_of(state, agent)
        if held is not None:
            key, how, tasks = held
            line += f" · run {key} · {how}" + (f" since {launched_at(state, agent)}" if how == "running" else "")
            line += " · on " + " ".join(tasks) if tasks else ""
        carried = state["runs"].get(agent) or {}
        if len(carried) > 1:                                 # one run per carrier: each said
            line += " · runs " + " ".join(f"{carrier} {run}" for carrier, run in carried.items())
        waited = waited_by(state, agent)
        if waited:
            line += " · waits " + " ".join(waited)
        owed = owed_by(state, agent)
        if owed:
            line += f" · owes {len(owed)}"
        suspicion = suspicion_of(state, agent)
        if suspicion is not None:
            line += f" · suspected · tried again at {suspicion['until']:%H:%M:%S}"
        print(line)
    box = owner_box(state, owner)
    print(f"owner inbox {len(box)}")
    for one in (worded(state, one) for one in box):
        print(f"  #{one['id']} {'question' if one.get('verb') == 'ask' else one.get('verb')} from {one.get('from')} "
              f"on {one.get('task')}" + (f" · about {one['about']}" if one.get("about") else "")
              + (" · returned" if state["returned_to"].get(one["id"]) == owner else ""))
    last = state["last"] or {}
    print(f"last event #{last.get('id')} {last.get('kind')} at {last.get('at')}")
    return 0


def status_object(root: Path, conductor, name: str, state: dict) -> dict:
    """`team status <name> --json`: the team as ONE JSON-ready object, every field read from the
    state the text reads -- the team, its state and what it waits on (`team_state`), its season and the
    launch its next wake-up gets, its tasks (text, last event, holders, delegations, waits, the wake-ups
    under way on it, their cost, the hour of its birth `at` and of its end `ended`, null while it is open), its
    members (run, state, their launch, the packages their run plays, what waits for
    them, the answers of the others they have not seen), its ceremonies (the next ring, whether the next tick rings, the last ring
    and who answered it), the owner's box and what still waits for them. `{team, started: null, state:
    "never", waiting_on: []}` for a team never started."""
    started = state["started"]
    if started is None:
        return {"team": name, "started": None, **team_state(state)}
    owner = str(started.get("owner"))
    launch = launch_face(root, conductor, started)
    tasks = []
    for task in state["tasks"].values():
        tasks.append({"id": task["id"], "name": task.get("name"), "text": task.get("text"), "last": task.get("last"),
                      "at": task.get("at"), "ended": task.get("ended") if task["state"] in CLOSED else None,
                      "state": task["state"], "from": task.get("from"), "to": task["to"],
                      "ceremony": task.get("ceremony"), "period": task.get("period"),
                      "recurrence": task.get("recurrence"),
                      "messages": len(task["messages"]), "resumed": state["resumed"].get(task["id"]),
                      "cost": round(float(task.get("cost") or 0.0), 6),
                      "holders": holders(state, task) if task["state"] != "resolved" else [],
                      "dos": [{"id": one["id"], "from": one["from"], "to": one["to"],
                               "answered": answer_of_debt(state, one["id"])}
                              for one in state["delegations"] if one["task"] == task["id"]],
                      "waits": [{"member": member, "any": wait.get("any"),
                                 "answered": sum(1 for to in wait["to"] if (to, task["id"]) in state["terminals"]),
                                 "of": len(wait["to"]), "open": wait_open(state, member, task["id"])}
                                for (member, on), wait in state["waits"].items() if on == task["id"]],
                      "running": running_on(state, task["id"])})
    members = []
    for member in started.get("agents") or {}:
        run, how, carried = run_of(state, member) or (None, None, [])
        last = last_launch(state, member) if how == "running" else None
        current = run if run not in (None, "?", "—") else None   # the run of its last launch
        cursor = cursor_of(state, member, current, 10 ** 12)
        members.append({"member": member, "path": path_of(state, member), "run": run, "how": how,
                        "since": (last or {}).get("at"), "tasks": carried, "waits": waited_by(state, member),
                        "owes": [{"id": key, "verb": state["messages"][key].get("verb"),
                                  "from": state["messages"][key].get("from"), "task": state["messages"][key].get("task")}
                                 for key in owed_by(state, member)],
                        "silence": [{"task": task, "exchanges": silence_of(state, member, task),
                                     "limit": silence_limit(state, member)}
                                    for task in dict.fromkeys(str(state["messages"][key].get("task"))
                                                              for key in owed_by(state, member))],
                        "health": health_face(state, member), "context": state["context"].get(member),
                        "launch": launch_face(root, conductor, started, member),
                        "runs": [{"carrier": carrier, "run": key, "name": carrier_name(state, name, carrier)}
                                 for carrier, key in (state["runs"].get(member) or {}).items()],
                        "packages": packages_at(root, conductor, path_of(state, member), current,
                                                set_of(season_played(root, conductor, started, member)))["packages"],
                        "pending": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"),
                                     "task": one.get("task")} for one in (worded(state, one) for one in inbox(state, member))],
                        "unseen": [{"member": one.get("agent"),
                                    "task": (state["intents"].get(one.get("tag")) or {}).get("task"), "id": one["id"]}
                                   for one in shared(state, member, cursor)]})
    ceremonies = []
    for ceremony in started.get("ceremonies") or []:
        rings = [task for task in state["tasks"].values() if task.get("ceremony") == ceremony["name"]]
        last = rings[-1] if rings else None
        ceremonies.append({"name": ceremony["name"], "mode": ceremony["mode"], "when": ceremony.get("when"),
                           "after": ceremony.get("after"), "participants": list(ceremony["participants"]),
                           "facilitator": ceremony["facilitator"], "quorum": ceremony.get("quorum"),
                           "next_due": next_due(ceremony, state), "due": due_period(ceremony, state) is not None,
                           "last": None if last is None else {"period": last.get("period"), "task": last["id"],
                                                               "state": last["state"], "by": last.get("by")},
                           "progress": [] if last is None else
                           [{"member": one, "answered": (one, last["id"]) in state["terminals"]}
                            for one in ceremony["participants"]]})
    recurrences = []
    for one in state["recurrences"].values():
        last = state["tasks"].get(one.get("last") or "")
        recurrences.append({"id": one["id"], "name": one.get("name"), "text": one.get("text"), "from": one.get("from"),
                            "to": one.get("to"), "when": one.get("when"), "since": one.get("since"),
                            "context": one.get("context"), "task": one.get("task"),
                            "next_due": recurrence_next(one), "due": recurrence_period(one) is not None,
                            "stopped": one["stopped"],
                            "last": None if last is None else {"period": last.get("period"), "task": last["id"],
                                                               "state": last["state"]}})
    waits = waiting(state)
    return {"team": name, "owner": owner, "principals": list(started.get("principals") or []),
            "started": {"at": started.get("at"), "id": started.get("id")}, **team_state(state),
            "paused": paused_face(state),
            "season": {"n": int(state.get("seasons") or 1), "at": started.get("at"),
                       "budget": (started.get("season") or {}).get("budget"),
                       "budget-launches": (started.get("season") or {}).get(          # `budget-wakes`: a season of before
                           "budget-launches", (started.get("season") or {}).get("budget-wakes"))}, "launch": launch,
            "changed": changed_since_start(root, name, started), "limits": dict(state["limits"]),
            "schedule": schedule_face(root, name, started, state),
            "cost": round(state["cost"], 6), "budget_spent": state["budget_spent"], "budget": share_of(state),
            "launches": {"launched": launched_since_start(root, state), "bound": state["limits"].get("budget-launches")},
            "last": state["last"], "tasks": tasks, "members": members, "ceremonies": ceremonies,
            "recurrences": recurrences,
            "owner_inbox": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"), "about": one.get("about"),
                             "task": one.get("task"), "returned": state["returned_to"].get(one["id"]) == owner}
                            for one in (worded(state, one) for one in owner_box(state, owner))],
            "waiting": {"questions": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"),
                                       "task": one.get("task")} for one in waits["questions"]],
                        "notices": [{"id": one["id"], "from": one.get("from"), "about": one.get("about"),
                                     "task": one.get("task"), "awaits": one["awaits"]} for one in waits["notices"]],
                        "infos": [{"id": one["id"], "from": one.get("from"), "task": one.get("task")}
                                  for one in waits["infos"]],
                        "done": [one["task"] for one in waits["done"]], "returned": list(waits["returned"])}}


def schedule_face(root: Path, name: str, started: dict, state: dict) -> dict:
    """-> the net as the face says it: `{seconds, timer, relaunch, reason}` -- `seconds` the step, `timer` whether a
    timer is armed, `relaunch` whether the relaunch entry stands, `reason` why the system refused it this season
    while it stays absent, else null; every one null under `off`."""
    seconds = schedule_seconds(started)
    if seconds is None:
        return {"seconds": None, "timer": None, "relaunch": None, "reason": None}
    standing = relaunch_standing(root)
    refused = None if standing else relaunch_notice(state)
    return {"seconds": seconds, "timer": bool(timer_standing(root, name)), "relaunch": standing,
            "reason": (refused or {}).get("why")}


def answer_of_debt(state: dict, key: int) -> int | None:
    """-> the id of the answer that settled the debt of the message `key`, None while it stands or when the task's close
    settled it."""
    settled = state["debts"].get(key)
    return settled if isinstance(settled, int) and not isinstance(settled, bool) else None


def health_face(state: dict, member: str) -> dict | None:
    """-> the member's HEALTH as the face says it: `{suspected, falls, cause, tried_at, repents}` -- `cause` of the
    last fall, `fall` or `silence` (row 115); `tried_at` the local hour of its try to the second while it is
    suspected --, None for a member that never fell since the season began."""
    health = (state.get("health") or {}).get(member)
    if not health:
        return None
    suspicion = suspicion_of(state, member)
    return {"suspected": suspicion is not None, "falls": int(health.get("falls") or 0), "cause": health.get("cause"),
            "tried_at": suspicion["until"].strftime("%Y-%m-%dT%H:%M:%S") if suspicion else None,
            "repents": int(health.get("repents") or 0)}


def paused_face(state: dict) -> dict | None:
    """-> `{by, at}` of the pause that stands, None when the team is not paused."""
    paused = state.get("paused")
    return None if not paused else {"by": paused.get("by"), "at": paused.get("at")}


def team_badges(name: str, state: dict) -> dict:
    """-> one line of `team status --json` without a name: the team, its start, its state and what it
    waits on, its tasks by state, the wake-ups under way, what waits for the owner as the inbox counts it
    (`waiting()`: `asks` the agents' questions, `notices` the team's notices, `done` the tasks resolved not seen),
    the last event."""
    if state["started"] is None:
        return {"team": name, "started": None, **team_state(state)}
    by_state = {"open": 0, "stopped": 0, "resolved": 0}
    for task in state["tasks"].values():
        by_state[task["state"]] = by_state.get(task["state"], 0) + 1
    waits = waiting(state)
    return {"team": name, "started": {"at": state["started"].get("at"), "id": state["started"].get("id")},
            **team_state(state), "paused": paused_face(state), "tasks": by_state, "running": len(open_intents(state)),
            "asks": len(waits["questions"]), "notices": len(waits["notices"]), "done": len(waits["done"]),
            "last": state["last"]}


def team_state(state: dict) -> dict:
    """-> `{state, waiting_on}`, the team as its face says it -- derived from the replay, never written:
    `never` before a start, `paused` from a `team pause` to its resume (above every other state),
    `working` while a wake-up plays, `idle` when no task is open, else `waiting`
    with every guard that holds, in the order `woken_on` judges them -- `members` (a member waits on its
    delegates, no message passes its wait), `launches` (an open task launches-spent), `budget` (money or budget-launches
    spent) --, then `owner` (a question to the owner, or a notice that holds a member, on an open task), `suspected` (a
    member of an open task is suspected: its final failure stands), `due` (messages due: the next tick launches)."""
    if state["started"] is None:
        return {"state": "never", "waiting_on": []}
    if state["paused"]:
        return {"state": "paused", "waiting_on": []}
    if open_intents(state):
        return {"state": "working", "waiting_on": []}
    open_tasks = [task for task, one in state["tasks"].items() if one["state"] == "open"]
    if not open_tasks:
        return {"state": "idle", "waiting_on": []}
    members = list(state["started"].get("agents") or {})
    due = {task for member in members for task, box in dues(state, member)
           if loud(state, box) and (not wait_open(state, member, task)
                                    or not all(held_by_wait(state, member, task, one) for one in loud(state, box)))}
    holds = []
    if any(wait_open(state, member, task) for member in members for task in open_tasks):
        holds.append("members")
    if any(task in state["launches_spent"] for task in open_tasks):
        holds.append("launches")
    if state["budget_spent"]:
        holds.append("budget")
    waits = waiting(state)
    if any(one.get("task") in open_tasks for one in waits["questions"] + [one for one in waits["notices"] if one["awaits"]]):
        holds.append("owner")
    if any(suspicion_of(state, member) is not None for task in open_tasks for member in members_of(state, task)):
        holds.append("suspected")
    if not state["budget_spent"] and any(task not in state["launches_spent"] for task in due):
        holds.append("due")
    return {"state": "waiting", "waiting_on": holds}


LAUNCH_KEYS = ("harness", "provider", "model", "permissions", "effort")


def launch_face(root: Path, conductor, started: dict, member: str | None = None) -> dict:
    """-> what the next wake-up gets of the launch `team start` kept: each key, `null` when absent -- never
    `max_budget_usd`, a per-wake cap an older journal may keep and the tick never passes --, and `packages`, the
    season's SET as `<name>=on|off`, one per pin (`season_played`): the team's; for a member, what its profile
    replaces, and the set its wake-up plays."""
    kept = started.get("launch") or {}
    profile = profile_of(started, member)
    face = {key: kept.get(key) for key in LAUNCH_KEYS}
    face.update({key: profile[key] for key in PROFILE_KEYS if profile.get(key) is not None})
    face["packages"] = season_played(root, conductor, started, member)
    return face


def profile_of(started: dict, member: str | None) -> dict:
    """-> the member's profile of the season (`team-started.profiles`), {} for none."""
    return dict(((started.get("profiles") or {}).get(member) or {})) if member else {}


def running_on(state: dict, task: str) -> list[dict]:
    """-> the wake-ups under way on the task, in the journal's order: each intent without an end that
    carries it -- its member, tag, run and hour once launched (`null` before), its allowance."""
    found = []
    for tag, one in state["intents"].items():
        if tag in state["ended"] or one.get("task") != task:
            continue
        launched = state["launched"].get(tag) or {}
        found.append({"member": one.get("agent"), "tag": tag, "run": launched.get("run"),
                      "since": launched.get("at"), "allowance": one.get("allowance"), "relance": one.get("relance")})
    return found


def last_launch(state: dict, member: str) -> dict | None:
    """-> the `wake-launched` of the member's last intent, None while that intent stands launched
    by nobody yet."""
    latest = None
    for one in sorted(state["intents"].values(), key=lambda entry: int(entry.get("id") or 0)):
        if one.get("agent") == member:
            latest = state["launched"].get(one.get("tag"))
    return latest


def launched_at(state: dict, member: str) -> str:
    """-> `HH:MM` (UTC) of the member's last launch -- `?` while its intent stands launched by
    nobody yet."""
    launch = last_launch(state, member)
    return str(launch["at"])[11:16] if launch is not None and launch.get("at") else "?"


def run_of(state: dict, member: str) -> tuple[str, str, list[str]] | None:
    """-> (run, state, tasks) of the member's ONE run, or None before its first wake-up: the run
    its last launch carried (`?` when none was launched); `running` while its last intent has no
    end, `killed` when a `stop --kill` ended it, `refused` when the house refused its launch, `dead` when it
    failed, `ended` otherwise; the
    tasks its wake-ups on that run carried, in the order of their first intent. After a `team reset`
    the intents before it are the forgotten run's: none since, the run is `—` and its state `reset`."""
    since = int(state["reset"].get(member) or 0)
    intents = [one for one in sorted(state["intents"].values(), key=lambda entry: int(entry.get("id") or 0))
               if one.get("agent") == member and int(one.get("id") or 0) > since]
    if not intents:
        return ("—", "reset", []) if member in state["reset"] else None
    runs = {str(one.get("tag")): (state["launched"].get(one.get("tag")) or {}).get("run") for one in intents}
    run = next((key for key in reversed(list(runs.values())) if key), None)
    tasks = list(dict.fromkeys(str(one.get("task")) for one in intents
                               if run is None or runs[str(one.get("tag"))] == run))
    last_tag = str(intents[-1].get("tag"))
    answered = {str(one.get("tag")) for one in state["ends"]}
    if last_tag not in state["ended"]:
        how = "running"
    elif last_tag in state["killed"]:
        how = "killed"
    elif last_tag in answered:
        how = "ended"
    elif last_tag in state["house"]:
        how = "refused"
    else:
        how = "dead"
    return run or "?", how, tasks


def status(rest: list[str]) -> int:
    """`team status [<name>] [--json]`: the text the owner reads, or under `--json` the face a
    program reads -- ONE object for the team named, one line per team declared without a name, each with
    `required`: the packages a member may not switch off (`required_by_team`, sorted), read once."""
    root, conductor = house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, rest = named_team(conductor, rest)
    as_json = flags(rest, STATUS_FLAGS)["json"]
    if name is not None:
        if not as_json:
            return status_of(root, conductor, name)
        if not team_doc(root, name).is_file():
            refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
        print(json.dumps({**status_object(root, conductor, name, state_of(journal_of(root, name))),
                          "name": team_name(root, conductor, name),
                          "required": sorted(required_by_team(root, conductor))}, ensure_ascii=False))
        return 0
    home = root.parent / TEAMS
    found = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    if as_json:
        needed = sorted(required_by_team(root, conductor)) if found else []
        for one in found:
            print(json.dumps({**team_badges(one, state_of(journal_of(root, one))),
                              "name": team_name(root, conductor, one), "required": needed}, ensure_ascii=False))
        return 0
    if not found:
        print(f"pp-team: no team declared under {home} yet.")
        return 0
    for name in found:
        state = state_of(journal_of(root, name))
        if state["started"] is None:
            print(f"{labelled(root, conductor, name)} · declared, not started")
            continue
        by_state: dict[str, int] = {}
        for task in state["tasks"].values():
            by_state[task["state"]] = by_state.get(task["state"], 0) + 1
        tally = ", ".join(f"{count} {kind}" for kind, count in by_state.items()) or "none"
        last = state["last"] or {}
        print(f"{labelled(root, conductor, name)} · {len(state['tasks'])} task(s): {tally} · last event "
              f"#{last.get('id')} {last.get('kind')} "
              f"at {last.get('at')}")
    return 0


# --- the readers: watch, log, result, inbox ------------------------------------------------

def harmless(text: str) -> str:
    """-> a text an agent or a principal wrote, as stdout may print it: each line opening on
    `::`, blanks before it included, prefixed with a backslash -- the console reads such a line
    as a directive of the house's bus, and nobody's words give pp an order."""
    return "\n".join("\\" + one if one.lstrip().startswith("::") else one for one in text.split("\n"))


def shown(one: dict) -> str:
    """-> one event as ONE line: `#<id> <kind> <what it says>` -- the form `log` prints and
    `watch` writes on stderr; a text of several lines is said on one."""
    kind = one.get("kind")
    text = " ".join(str(one.get("text") or "").split())
    short = text if len(text) <= 60 else text[:57] + "…"
    if kind == "post":
        return (f"#{one.get('id')} post {one.get('verb')}" + (f" #{one['re']}" if one.get("re") is not None else "")
                + f" {one.get('from')} -> {one.get('to')} on {one.get('task')}"
                + (f" · about {one['about']}" if one.get("about") else "")
                + (" · info" if one.get("info") else "") + (" · by the tick" if one.get("by") == "tick" else "")
                + (f": {short}" if short else ""))
    if kind == "task":
        return (f"#{one.get('id')} task {one.get('task')}" + (f" {one['name']}" if one.get("name") else "")
                + f" from {one.get('from')} to {one.get('to')}: {short}")
    if kind == "team-started":
        return f"#{one.get('id')} team-started · members {', '.join(one.get('agents') or {})} · root {one.get('root')}"
    if kind == "wake-intent":
        return f"#{one.get('id')} wake-intent {one.get('agent')} on {one.get('task')} · tag {one.get('tag')}"
    if kind == "wake-launched":
        return (f"#{one.get('id')} wake-launched {one.get('agent')} · run {one.get('run')} · pid {one.get('pid')}"
                + (f" · name refused: {one['name-refused']}" if one.get("name-refused") else ""))
    if kind == "wake-ended":
        return (f"#{one.get('id')} wake-ended {one.get('agent')} · run {one.get('run')}"
                + (f" · launch {one.get('launch')}" if one.get("launch") is not None else "")
                + (f" · {one.get('state')}" if one.get("state") else "") + f" · cost {one.get('cost')}")
    if kind == "wake-routed":
        return (f"#{one.get('id')} wake-routed {one.get('agent')} · run {one.get('run')} · words {one.get('words')}"
                + (" · nowhere" if one.get("nowhere") else ""))
    if kind == "wake-refused":
        return f"#{one.get('id')} wake-refused {one.get('agent')} · run {one.get('run')} · {one.get('why')}"
    if kind == "wake-failed":
        return (f"#{one.get('id')} wake-failed {one.get('agent')} on {one.get('task')} · {one.get('reason')}"
                + (f" · spent {one.get('spent')} of its share {one.get('share')} USD" if "share" in one else "")
                + (" · the house" if one.get("house") else "") + (" · final" if one.get("final") else ""))
    if kind == "timer-armed":
        return f"#{one.get('id')} timer-armed · due {str(one.get('due'))[11:19]}"
    if kind == "wake-killed":
        return f"#{one.get('id')} wake-killed {one.get('agent')} on {one.get('task')} · run {one.get('run')} · pid {one.get('pid')}"
    if kind in ("wait-met", "deferred"):
        return f"#{one.get('id')} {kind} {one.get('agent')} on {one.get('task')}"
    if kind == "wait":
        return f"#{one.get('id')} wait {one.get('agent')} on {one.get('task')} · any {one.get('any')} of {', '.join(one.get('to') or [])}"
    if kind == "done":
        return f"#{one.get('id')} done {one.get('task')} · {json.dumps(one.get('result'), ensure_ascii=False)}"
    if kind == "returned":
        return f"#{one.get('id')} returned #{one.get('message')} to {one.get('to')}"
    if kind == "stopped":
        return f"#{one.get('id')} stopped {one.get('task')} by {one.get('by')}"
    if kind == "ceremony-due":
        return (f"#{one.get('id')} ceremony-due {one.get('ceremony')} · {one.get('period')}"
                + (f" by {one.get('by')}" if one.get("by") else ""))
    if kind == "resumed":
        return f"#{one.get('id')} resumed {one.get('task')} by {one.get('by')} · from {', '.join(one.get('from') or [])}"
    if kind == "recurrence":
        when = one.get("when") or {}
        return (f"#{one.get('id')} recurrence {one.get('recurrence')}" + (f" {one['name']}" if one.get("name") else "")
                + f" from {one.get('from')} to {one.get('to')} · every {said_when(when)}"
                + (f" · from {one['task']}" if one.get("task") else "")
                + (f" · context {one['context']}%" if one.get("context") is not None else "") + f": {short}")
    if kind == "recurrence-skipped":
        return f"#{one.get('id')} recurrence-skipped {one.get('recurrence')} · {one.get('period')} · {one.get('open')} open"
    if kind == "recurrence-stopped":
        return f"#{one.get('id')} recurrence-stopped {one.get('recurrence')} by {one.get('by')}"
    if kind == "recurrence-changed":
        when = one.get("when") or {}
        return (f"#{one.get('id')} recurrence-changed {one.get('recurrence')} by {one.get('by')}"
                + (f" · every {said_when(when)}" if "when" in one else "")
                + (f" · context {one['context']}%" if one.get("context") is not None
                   else " · context off" if "context" in one else "")
                + (f": {short}" if "text" in one else ""))
    if kind == "run-renewed":
        return (f"#{one.get('id')} run-renewed {one.get('member')} · run {one.get('run')} of {one.get('recurrence')} "
                f"on {one.get('task')} · used {round(float(one.get('used') or 0) * 100)}% of {one.get('limit')}%")
    if kind == "budget-spent":
        return (f"#{one.get('id')} budget-spent {one.get('spent')} of {one.get('budget')} "
                + ("launches" if one.get("unit") in ("launches", "wakes") else "USD"))
    if kind == "silence":
        return f"#{one.get('id')} silence {one.get('agent')} on {one.get('task')} · {one.get('exchanges')} exchange(s)"
    if kind == "inbox-seen":
        return f"#{one.get('id')} inbox-seen up to #{one.get('upto')}"
    return f"#{one.get('id')} {kind}"


def of_task(events: list[dict], task: str) -> list[dict]:
    """-> the events of one task: those that name it, and the launches and ends of the
    intents it opened (found by their tag)."""
    tags = {one.get("tag") for one in events if one.get("kind") == "wake-intent" and one.get("task") == task}
    return [one for one in events if one.get("task") == task or (one.get("tag") in tags and one.get("kind") != "wake-intent")]


def event_object(name: str, one: dict) -> dict:
    """-> one journal event as the faces give it: `{at, team, event, ...}` -- its kind as `event`,
    the rest of its fields, its `id` among them. `watch --json` and `log --json` both write it."""
    return {"at": one.get("at"), "team": name, "event": one.get("kind"),
            **{key: value for key, value in one.items() if key not in ("at", "kind", "team")}}


def said_event(name: str, one: dict, as_json: bool) -> None:
    """One journal event on stderr, as `watch` says it: the line, or the JSON object;
    a `snapshot` is a reader's aid, not a team event, and is never said."""
    if one.get("kind") == "snapshot":
        return
    if as_json:
        text = json.dumps(event_object(name, one), ensure_ascii=False)
    else:
        text = f"[{datetime.now().strftime('%H:%M:%S')}] {name} · {shown(one)}"
    sys.stderr.write(text + "\n")
    sys.stderr.flush()


def seconds_of(asked: dict, flag: str, floor: float) -> float | None:
    """-> the seconds a flag names, at least `floor`; None without the flag."""
    if asked[flag] is None:
        return None
    try:
        value = float(asked[flag])
    except ValueError:
        value = -1.0
    if value < floor:
        refuse(f"{flag}-invalid -- `--{flag} {asked[flag]}`: a number of seconds, at least {floor:g}.")
    return value


def quiescent(state: dict) -> bool:
    """-> whether nothing can move: no intent without an end, and no task open -- or nothing a
    tick could still launch on them: no agent has a message due, or the budget is spent, or
    the due tasks' wake-ups are."""
    if open_intents(state):
        return False
    if not any(one["state"] == "open" for one in state["tasks"].values()) or state["budget_spent"]:
        return True
    for agent in (state["started"] or {}).get("agents") or {}:
        if any(task not in state["launches_spent"] and loud(state, box) for task, box in dues(state, agent)):
            return False
    return True


def activity_of(kind: str, one: dict) -> dict:
    """-> what an `activity` object of `watch` says of one event of a flow: a `tool` its `name`, its `title` and
    `pp`; a `tool-result` its `error` and the `size` of its content -- never the content --; a `thinking` its
    `tokens` or its `text`; `words` its `text`; a `context` its `tokens`, `used` and `window`; every text cut at
    `ACTIVITY_TEXT`."""
    def cut(text: object) -> str:
        return " ".join(str(text or "").split())[:ACTIVITY_TEXT]
    if kind == "tool":
        return {"kind": kind, "name": str(one.get("name") or ""), "title": cut(one.get("title")), "pp": one.get("pp") is True}
    if kind == "tool-result":
        return {"kind": kind, "error": one.get("error") is True, "size": len(str(one.get("content") or ""))}
    if kind == "thinking":
        tokens = one.get("tokens")
        return {"kind": kind, "tokens": tokens} if isinstance(tokens, int) else {"kind": kind, "text": cut(one.get("text"))}
    if kind == "words":
        return {"kind": kind, "text": cut(one.get("text"))}
    return {"kind": kind, "tokens": one.get("tokens"), "used": one.get("used"), "window": one.get("window")}


def activity_line(fields: dict) -> str:
    """-> an activity as the text watch says it: `tool Read · pp.py`, `result ✓ 10.0 kB`, `thinking <text>`,
    `words <text>`, `context 34000 tokens`."""
    kind = fields.get("kind")
    if kind == "tool":
        return f"tool {fields.get('name')}" + (f" · {fields['title']}" if fields.get("title") else "")
    if kind == "tool-result":
        size = int(fields.get("size") or 0)
        said = f"{size} B" if size < 1024 else f"{size / 1024:.1f} kB"
        return f"result {'✗' if fields.get('error') else '✓'} {said}"
    if kind == "context":
        return f"context {fields.get('tokens')} tokens"
    return f"{kind} {fields.get('text') if fields.get('text') is not None else fields.get('tokens', '')}".rstrip()


class ActivityReader:
    """The FLOW of one launch the watch follows, read by `agent flow <path> <run> --json --from <rank> --follow`
    in a thread of its own -- the same call as the follower --: from the `opened` of the launch's exchange, found
    by its tag, the events that say what the harness does (`ACTIVITY_KINDS`) come out of `fresh()` as the fields
    of an `activity` object, at most `ACTIVITY_RATE` per second: past that, the latest is HELD and the ones it
    replaces are counted, said with `more` once the second turned or at `close()`; a `context` always passes.
    `done` once the stream ended on its own."""

    def __init__(self, engine: Path, root: Path, path: str, run: str, tag: str, start: int) -> None:
        self.tag, self.opened, self.done = tag, False, False
        self.window: float | None = None             # the instant the current second opened
        self.count = 0                               # the objects said in it
        self.held: dict | None = None                # the latest object past the rate, said when the second turns
        self.dropped = 0                             # the objects it replaced
        self._queue: queue.Queue = queue.Queue()
        self._process = subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                                          "--json", "--from", str(max(1, start)), "--follow"],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                         cwd=str(root.parent), env=dict(os.environ))
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _read(self) -> None:
        assert self._process.stdout is not None
        for line in self._process.stdout:
            if line.strip():
                try:
                    self._queue.put(json.loads(line))
                except ValueError:
                    continue
        self._queue.put(None)

    def fresh(self, now: float) -> list[dict]:
        """-> the activity objects to say now: those read since the last call, under the rate, and the held one
        once the second turned."""
        said: list[dict] = []
        while True:
            try:
                one = self._queue.get_nowait()
            except queue.Empty:
                break
            if one is None:
                self.done = True
                break
            kind = one.get("kind")
            if kind == "opened":                     # the launch's own exchange opens here; another closes it
                self.opened = opened_by(one, self.tag)
            elif self.opened and kind in ACTIVITY_KINDS:
                fields = activity_of(str(kind), one)
                said += [fields] if kind == "context" else self._bounded(fields, now)
        return said + self._turned(now)

    def _bounded(self, fields: dict, now: float) -> list[dict]:
        out = self._turned(now)
        if self.window is None or now - self.window >= 1.0:
            self.window, self.count = now, 0
        if self.count < ACTIVITY_RATE - 1:           # the last slot of the second is the held one's
            self.count += 1
            return out + [fields]
        if self.held is not None:
            self.dropped += 1
        self.held = fields
        return out

    def _turned(self, now: float) -> list[dict]:
        """-> the held object once the second turned: it opens the next one."""
        if self.held is None or (self.window is not None and now - self.window < 1.0):
            return []
        self.window, self.count = now, 1
        return [self._flushed()]

    def _flushed(self) -> dict:
        said = {**self.held, **({"more": self.dropped} if self.dropped else {})}
        self.held, self.dropped = None, 0
        return said

    def close(self) -> list[dict]:
        """The stream ended: the process ended when still alive, the held object said. -> what is left to say."""
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
        return [self._flushed()] if self.held is not None else []


def watched(root: Path, conductor, name: str, asked: dict) -> int:
    """`team watch`: the journal and the traces of the wake-ups under way FOLLOWED -- read,
    never written, no lock taken -- until the bound asked, or Ctrl-C. Under `--json` each step of a
    wake-up says the `task`, the `tag` and the `launch` (its rank in the run) of the intent it follows.
    Beside the trace, the FLOW of each wake-up followed is read by its own `agent flow --follow`
    (`ActivityReader`, closed with the wake-up): what the harness does between two blocks is said as
    `activity` objects -- `{at, agent, run, event: activity, kind, task, tag, launch, …}` --, one line
    of text each without `--json`."""
    log = tracing(conductor)
    engine = engine_of(root, conductor)
    journal = journal_of(root, name)
    task = asked["task"]
    as_json = asked["json"]
    beat = int(seconds_of(asked, "heartbeat", 1) or DEFAULT_HEARTBEAT)
    bound = seconds_of(asked, "for", 0)
    state = state_of(journal)
    tail = log.tail(journal, from_end=True)
    context = said_so_far()                                # what the journal said: the next events said in its words
    for one in lines_of(journal):
        if one.get("kind") != "snapshot":
            read_on(context, one)
    follows: dict[str, tuple[str, str, object]] = {}      # tag -> (member, run, the run's reader)
    activities: dict[str, ActivityReader] = {}            # tag -> the reader of the launch's flow
    closing: dict[str, float] = {}                        # tag -> when its wake-up ended: its reader drains, then closes
    intents: dict[str, dict] = {str(tag): one for tag, one in state["intents"].items()}   # tag -> its wake-intent
    launches: dict[str, dict] = {str(tag): one for tag, one in state["launched"].items()}   # tag -> its wake-launched
    members = dict((state["started"] or {}).get("agents") or {})          # name -> the agent's path
    paths = {tag: path_of_intent(state, one) for tag, one in state["intents"].items()}   # tag -> path
    tags_of_task: set[str] = {tag for tag, one in state["intents"].items() if one.get("task") == task}
    for one in open_intents(state):                        # the wake-ups already under way: read on
        launch = state["launched"].get(one["tag"])
        if launch and launch.get("run") and (task is None or one["tag"] in tags_of_task):
            follows[one["tag"]] = (one["agent"], launch["run"],
                                   log.follow(agent_meta(root, paths[one["tag"]]), launch["run"], from_end=True))
            activities[one["tag"]] = ActivityReader(engine, root, paths[one["tag"]], str(launch["run"]), one["tag"],
                                                    int(state["flow"].get(str(launch["run"])) or 0) + 1)
    resumed: set[str] = {tag for tag, one in state["intents"].items() if one.get("run")}
    opened, still, beats = time.monotonic(), time.monotonic(), 0
    try:
        while True:
            moved = False
            for one in tail.fresh():
                kind, tag = one.get("kind"), one.get("tag")
                said = read_on(context, one) if kind != "snapshot" else one
                if kind == "team-started":
                    members = dict(one.get("agents") or {})
                if kind == "wake-intent":
                    paths[str(tag)] = str(one.get("path") or members.get(one.get("agent"), one.get("agent")))
                    intents[str(tag)] = one
                if kind == "wake-intent" and one.get("task") == task:
                    tags_of_task.add(str(tag))
                if kind == "wake-intent" and one.get("run"):       # a run resumed: its trace read from its end
                    resumed.add(str(tag))
                if kind == "wake-launched":
                    launches[str(tag)] = one
                if task is not None and one.get("task") != task and tag not in tags_of_task:
                    continue
                if said is not None:
                    said_event(name, said, as_json)
                    moved = True
                if kind == "wake-launched" and one.get("run") and tag not in follows:
                    at = paths.get(str(tag)) or str(members.get(one.get("agent"), one.get("agent")))
                    follows[str(tag)] = (str(one.get("agent")), str(one["run"]),
                                         log.follow(agent_meta(root, at), str(one["run"]),
                                                    from_end=str(tag) in resumed))
                    activities[str(tag)] = ActivityReader(engine, root, at, str(one["run"]), str(tag),
                                                          int(state["flow"].get(str(one["run"])) or 0) + 1)
            for tag in list(follows):
                agent, run, reader = follows[tag]
                intent = intents.get(tag) or {}
                for line, kind, fields in filter(None, map(log.step_of, reader.fresh())):
                    if as_json:                             # the step said with the intent it follows
                        fields = {**fields, "task": intent.get("task"), "tag": tag,
                                  "launch": (launches.get(tag) or {}).get("launch")}
                    log.said(run, line, kind, fields, as_json, who=agent)
                    moved = True
            now_at = time.monotonic()
            for tag in list(activities):                    # the activity of each launch followed, under the rate
                reader = activities[tag]
                agent, run = (follows.get(tag) or (intents.get(tag, {}).get("agent"), (launches.get(tag) or {}).get("run")))[:2]
                over = tag in closing and (reader.done or now_at - closing[tag] >= ACTIVITY_DRAIN)
                for fields in reader.fresh(now_at) + (reader.close() if over else []):
                    log.said(str(run), activity_line(fields), "activity",
                             {**fields, "task": (intents.get(tag) or {}).get("task"), "tag": tag,
                              "launch": (launches.get(tag) or {}).get("launch")}, as_json, who=str(agent))
                    moved = True
                if over:
                    del activities[tag], closing[tag]
            state = state_of(journal)
            for tag in list(follows):                       # a wake-up over leaves the watch; its flow drains, then closes
                if tag in state["ended"]:
                    del follows[tag]
                    if tag in activities:
                        closing[tag] = time.monotonic()
            if moved:
                still, beats = time.monotonic(), 0
            elif time.monotonic() - still >= beat * (beats + 1):
                beats += 1
                if as_json:
                    said_event(name, {"at": now(), "kind": "quiet", "seconds": beat * beats}, True)
                else:
                    sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {name} · no event for {beat * beats}s\n")
                    sys.stderr.flush()
            if asked["until-done"] and state["started"] is not None and quiescent(state):
                break
            if bound is not None and time.monotonic() - opened >= bound:
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        for reader in activities.values():
            reader.close()
    return 0


def watch(rest: list[str]) -> int:
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, WATCH_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    return watched(root, conductor, name, asked)


def log_verb(rest: list[str]) -> int:
    """`team log`: the journal rendered, one line per event, by task and by tail, in the words of the debt (`read_on`);
    under `--json` one object per event, the form `watch --json` writes."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, LOG_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    context, events = said_so_far(), []
    for one in lines_of(journal_of(root, name)):
        said = read_on(context, one) if one.get("kind") != "snapshot" else None
        if said is not None:
            events.append(said)
    if asked["task"] is not None:
        events = of_task(events, asked["task"])
    if asked["last"] is not None:
        try:
            last = int(asked["last"])
        except ValueError:
            last = -1
        if last < 1:
            refuse(f"last-invalid -- `--last {asked['last']}`: a whole number of 1 or more.")
        events = events[-last:]
    for one in events:
        print(json.dumps(event_object(name, one), ensure_ascii=False) if asked["json"] else harmless(shown(one)))
    return 0


def result(rest: list[str]) -> int:
    """`team result`: a resolved task's result as JSON on stdout."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if len(rest) > 1 or (rest and rest[0].startswith("--")):
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    if rest:
        task = state["tasks"].get(rest[0])
        if task is None:
            refuse(f"task-unknown -- no task `{rest[0]}` of {name}: the tasks are {', '.join(state['tasks']) or 'none'}.")
        if task["state"] != "resolved":
            refuse(f"task-open -- {task['id']} is {task['state']}: no result yet.")
        chosen = state["done"][task["id"]]
    else:
        resolved = list(state["done"].values())
        if not resolved:
            refuse(f"result-missing -- no task of {name} is resolved yet.")
        chosen = resolved[-1]
    print(json.dumps(chosen.get("result"), ensure_ascii=False))
    return 0


def responses_verb(rest: list[str]) -> int:
    """`team responses`: what the team's members said, one per `wake-ended`, the words of its launch read
    at the run's flow by the house's console; `--since`, `--agent`, `--task` filter, `--last` cuts; under
    `--json` one object per end, its text whole or `null`. Nothing written."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESPONSES_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    if state["started"] is None:
        refuse(f"team-not-started -- {name} was never started.")
    numbers: dict[str, int] = {}
    for flag in ("since", "last"):
        if asked[flag] is not None:
            try:
                numbers[flag] = int(asked[flag])
            except ValueError:
                numbers[flag] = -1
            if numbers[flag] < 0:
                refuse(f"{flag}-invalid -- `--{flag} {asked[flag]}`: a whole number of 0 or more.")
    chosen = []
    for one in state["ends"]:
        task = (state["intents"].get(one.get("tag")) or {}).get("task")
        if "since" in numbers and one["id"] <= numbers["since"]:
            continue
        if asked["agent"] is not None and one.get("agent") != asked["agent"]:
            continue
        if asked["task"] is not None and task != asked["task"]:
            continue
        chosen.append((one, task))
    if "last" in numbers:
        chosen = chosen[-numbers["last"]:] if numbers["last"] else []
    for one, task in chosen:
        intent = state["intents"].get(one.get("tag"))
        at = path_of_intent(state, intent) if intent else path_of(state, str(one.get("agent")))
        text = words_of(root, conductor, at, str(one.get("run") or ""), one.get("launch"))
        if asked["json"]:
            print(json.dumps({"id": one["id"], "member": one.get("agent"), "path": at, "task": task,
                              "run": one.get("run"), "launch": one.get("launch"), "at": one.get("at"),
                              "cost_usd": one.get("cost"), "response": text}, ensure_ascii=False))
            continue
        print(f"#{one['id']} {one.get('agent')} on {task} · run {one.get('run')}")
        print(harmless(text) if text is not None else "(response missing at the record)")
        print()
    return 0


def words_of(root: Path, conductor, path: str, run: str, launch) -> str | None:
    """-> what a launch SAID, its `words` joined by a blank line, read at the run's flow by the house's
    console (`agent flow --exchange <launch> --json`); None when the launch is unknown or its flow
    carries no words."""
    if not run or not isinstance(launch, int):
        return None
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                             "--json", "--exchange", str(launch)], capture_output=True, text=True,
                            cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return None
    texts = []
    for line in played.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict) and one.get("kind") == "words" and str(one.get("text") or "").strip():
            texts.append(str(one["text"]).strip())
    return "\n\n".join(texts) if texts else None


def waiting(state: dict) -> dict:
    """-> what waits for the owner: the QUESTIONS -- an agent's `ask` to them no answer of theirs cites --; the NOTICES of
    the team to them, each in the words of the debt (`worded`) with `awaits` -- a notice about a member on an open task
    no answer cites, which holds that member's wait and stays until the answer --, the others since the cursor
    `inbox-seen`; the INFOS sent to them since the cursor, which hold nobody; the tasks resolved and the posts
    returned to them since the cursor."""
    owner = str((state["started"] or {}).get("owner") or "")
    answered = answered_by_principal(state)
    to_owner = [one for one in state["messages"].values() if one.get("to") == owner]
    questions = [one for one in to_owner if one.get("verb") == "ask" and one["id"] not in answered]
    infos = [one for one in to_owner if one.get("verb") == "info" and one["id"] > state["seen"]]
    notices = []
    for one in to_owner:
        if not is_notice(state, one):
            continue
        awaits = (notice_about(state, one) is not None and one["id"] not in answered
                  and is_open(state, one.get("task")) and one.get("cause") != "silence")   # a silence holds nobody
        if awaits or one["id"] > state["seen"]:
            notices.append({**worded(state, one), "awaits": awaits})
    done = [one for one in state["done"].values() if int(one.get("id") or 0) > state["seen"]]
    returned = [mid for mid, to in state["returned_to"].items() if to == owner and mid > state["seen"]]
    return {"questions": questions, "notices": notices, "infos": infos, "done": done, "returned": returned}


def inbox_line(name: str, state: dict) -> str:
    """-> `review: T1 done · 1 question waiting for you · 2 notices · 1 info · 1 post returned`, or '' when
    nothing waits for the owner."""
    waits = waiting(state)
    parts = [f"{one['task']} done" for one in waits["done"]]
    asks, told = len(waits["questions"]), len(waits["notices"])
    if asks:
        parts.append(f"{asks} question{'s' if asks > 1 else ''} waiting for you")
    if told:
        parts.append(f"{told} notice{'s' if told > 1 else ''}")
    if waits["infos"]:
        parts.append(f"{len(waits['infos'])} info{'s' if len(waits['infos']) > 1 else ''}")
    if waits["returned"]:
        parts.append(f"{len(waits['returned'])} post{'s' if len(waits['returned']) > 1 else ''} returned")
    return f"{name}: " + " · ".join(parts) if parts else ""


def inbox_object(name: str, state: dict) -> dict | None:
    """-> what waits for the owner in one team, to READ: the questions, the notices, the infos and the posts returned
    with their texts, the tasks resolved by task and id -- None when nothing waits. `waiting()` decides."""
    waits = waiting(state)
    if not (waits["questions"] or waits["notices"] or waits["infos"] or waits["done"] or waits["returned"]):
        return None

    def post(one: dict) -> dict:
        return {"id": one["id"], "verb": one.get("verb"), "from": one.get("from"), "task": one.get("task"),
                "text": one.get("text")}

    return {"team": name, "questions": [post(one) for one in waits["questions"]],
            "notices": [{"id": one["id"], "from": one.get("from"), "about": one.get("about"), "task": one.get("task"),
                         "text": one.get("text"), "awaits": one["awaits"]} for one in waits["notices"]],
            "infos": [{"id": one["id"], "from": one.get("from"), "task": one.get("task"), "text": one.get("text")}
                      for one in waits["infos"]],
            "done": [{"task": one["task"], "id": one.get("id")} for one in waits["done"]],
            "returned": [post(state["messages"][mid]) for mid in waits["returned"] if mid in state["messages"]]}


def inbox_verb(rest: list[str]) -> int:
    """`team inbox`: one line per team where something waits for the owner -- under `--json` one
    object per such team; `--seen` writes the owner's cursor at the team's journal -- the one
    write of the readers, never beside `--json`."""
    root, conductor = house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, rest = named_team(conductor, rest)
    asked = flags(rest, INBOX_FLAGS)
    if asked["seen"] and asked["json"]:
        refuse(USAGE)
    if asked["seen"]:
        if name is None:
            refuse("inbox --seen names the team whose inbox was read: `team inbox <name> --seen`.")
        if not team_doc(root, name).is_file():
            refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")

        def judge(state: dict, events: list[dict]) -> list[dict]:
            if state["started"] is None:
                refuse(f"team-not-started -- {name} was never started.")
            upto = max((int(one.get("id") or 0) for one in events), default=0)
            return [{"kind": "inbox-seen", "upto": upto}] if upto > state["seen"] else []

        made = written(conductor, journal_of(root, name), name, judge)
        print(f"pp-team: {name} · inbox seen up to #{made[0]['upto']}" if made else f"pp-team: {name} · inbox seen already")
        return 0
    home = root.parent / TEAMS
    names = [name] if name else (sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else [])
    for one in names:
        state = state_of(journal_of(root, one))
        if state["started"] is None:
            continue
        if asked["json"]:
            found = inbox_object(one, state)
            if found is not None:
                print(json.dumps({**found, "name": team_name(root, conductor, one)}, ensure_ascii=False))
            continue
        line = inbox_line(labelled(root, conductor, one), state)
        if line:
            print(line)
    return 0


def entry_verb(rest: list[str]) -> int:
    """`team entry <name> [--run <key>]` -- prints the document the team's wake-up under that run
    (`PP_RUN` when `--run` is absent) plays this exchange (`entry_of`): the decider of the team's
    document, played by the agent's engine -- whose `PP_HOME` names the AGENT, so the house is the
    machine this script lives in, never the instance served. A team never started, a key no wake-up
    of the team holds: the neutral `TEAM-IDLE.md`, so that the agent's exchange always goes on.
    Nothing written."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import _machine, core                      # noqa: E402 -- the bootstrap
    root = _machine(__file__)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    conductor = core(__file__)
    name, rest = named_team(conductor, rest)
    asked = flags(rest, ENTRY_FLAGS)
    run = asked["run"] or os.environ.get("PP_RUN", "").strip()
    if not run:
        refuse(USAGE)
    print(entry_of(root, name, run))
    return 0


def run_named(root: Path, conductor, path: str, run: str, text: str) -> str:
    """`agent name <path> <run> <text>` by the house's console: an opening carries its carrier's name. -> ''
    once named, else what the house said -- the wake-up plays on unnamed."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent", "name",
                             path, run, text], capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-200:] or f"rc {played.returncode}"


def forgotten(root: Path, conductor, path: str, run: str) -> str:
    """`-reset <run>` by the console of the agent at `path` -- the house's engine addressing the
    agent's instance, the gesture an owner plays by hand. -> '' once forgotten, else what the
    engine said (`call-busy`: a call holds the run)."""
    meta = agent_meta(root, path)
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(meta), "-reset", run],
                            capture_output=True, text=True, cwd=str(meta.parent), env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def reset_verb(rest: list[str]) -> int:
    """`team reset <name> [--member <m>]`: every run of each member named -- every member without
    `--member` -- forgotten by its agent's console, one `run-reset {member, run}` per run; the next
    wake-up of the member on a task opens a new run, a new session, told the history of that task's carrier.
    Judged before anything is forgotten, under `tick.lock` waited within `call_lock_wait`
    (`team-busy` beyond) and held to the last write: no tick launches on a key being forgotten.
    A member without a run is said, nothing written for it; an agent's console that refuses stops
    the verb, the members forgotten before it written."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESET_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    journal = journal_of(root, name)
    journal.parent.mkdir(parents=True, exist_ok=True)
    lock = locks(conductor)
    lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
    if lease is None:
        refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing forgotten, "
               "replay once it has played.")
    said: list[str] = []
    try:
        state = state_of(journal)
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started: nothing to forget.")
        members = list((state["started"].get("agents") or {}))
        if asked["member"] is not None:
            if not is_member(state, asked["member"]):
                refuse(f"participant-unknown -- `{asked['member']}` is no member of {name}.")
            members = [asked["member"]]
        for member in members:
            runs = list(dict.fromkeys((state["runs"].get(member) or {}).values()))
            held = next((run for run in runs if held_run(root, conductor, path_of(state, member), run)), None)
            if busy(state, member) or held is not None:
                refuse(f"member-running -- a wake-up of {member} plays" + (f" in run {held}" if held else "")
                       + ": nothing forgotten, replay once it has ended.")
        for member in members:
            runs = list(dict.fromkeys((state["runs"].get(member) or {}).values()))
            if not runs:
                said.append(f"{member} · no run to forget")
            for run in runs:                                     # every run of the member, one per carrier
                why = forgotten(root, conductor, path_of(state, member), run)
                if why:
                    for line in said:
                        print(f"pp-team: {name} · {line}")
                    refuse(f"reset-failed -- the console of {path_of(state, member)} kept run {run}: {why}")
                made = appended(conductor, journal, name, [{"kind": "run-reset", "member": member, "run": run}])
                said.append(f"{member} · run {run} forgotten (run-reset #{made[0]['id']})")
    finally:
        lock.release(lease)
    for line in said:
        print(f"pp-team: {name} · {line}")
    if (journal.parent / TICK_MARK).exists():
        ticked(root, conductor, name)              # a tick asked while the reset held the lock plays now
    return 0


def team_runs(state: dict, events: list[dict]) -> list[dict]:
    """-> every run a wake-up of the team opened, `{member, path, run}` in the order the journal met them: the
    runs its `wake-launched` and `wake-ended` name, a member's path read at its intent or at the start."""
    paths: dict[str, str] = {}
    by_tag: dict[str, str] = {}
    found: dict[tuple[str, str], dict] = {}
    for one in events:
        kind = one.get("kind")
        if kind == "team-started":
            paths.update({str(member): str(path) for member, path in (one.get("agents") or {}).items()})
        elif kind == "wake-intent" and one.get("path"):
            by_tag[str(one.get("tag"))] = str(one["path"])
        elif kind in ("wake-launched", "wake-ended") and one.get("run"):
            member = str(one.get("agent"))
            path = by_tag.get(str(one.get("tag"))) or paths.get(member)
            if path:
                found.setdefault((path, str(one["run"])), {"member": member, "path": path, "run": str(one["run"])})
    for member, run in ((member, run) for member, held in state["runs"].items() for run in held.values()):
        if run and paths.get(member):
            found.setdefault((paths[member], run), {"member": member, "path": paths[member], "run": run})
    return list(found.values())


def declared_paths(root: Path, conductor, name: str) -> set[str]:
    """-> the paths of the agents a team's `TEAM.md` declares; none when it cannot be read or judged."""
    path = team_doc(root, name)
    try:
        return set(judged(conductor, conductor.reading.read(path).front, path.read_bytes(), path, name)["agents"].values())
    except (conductor.Refusal, Declined, OSError):
        return set()


def purged(root: Path, conductor, path: str, runs: list[str]) -> str:
    """`agent purge <path> <run> ... --yes` by the house's console -> '' once removed, else what it said."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent",
                             "purge", path, *runs, "--yes"], capture_output=True, text=True, cwd=str(root.parent),
                            env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def agents_asked(rest: list[str]) -> tuple[list[str], list[str]]:
    """-> (the paths `--agent <path>` names, in their order, each once; the rest of the flags)."""
    paths, kept, index = [], [], 0
    while index < len(rest):
        if rest[index] == "--agent":
            if index + 1 >= len(rest) or rest[index + 1].startswith("--"):
                refuse(USAGE)
            paths.append(rest[index + 1])
            index += 2
            continue
        kept.append(rest[index])
        index += 1
    return list(dict.fromkeys(paths)), kept


def agent_removed(root: Path, conductor, path: str) -> str:
    """`agent remove <path> --yes` by the house's console -> '' once removed, else what it said."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent",
                             "remove", path, "--yes"], capture_output=True, text=True, cwd=str(root.parent),
                            env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def delete_verb(rest: list[str]) -> int:
    """`team delete <name> [--agent <path>]... [--yes] [--json]`: removes the team and what it made -- its timer, its
    relaunch entry, every run its wake-ups opened (by `agent purge`, at each agent), its journal and the files beside
    it, then its directory, the owner's declaration and documents with it -- and, under `--agent`, the agents named
    (by `agent remove`, after the purge of the runs and before the directory goes). An agent named must be one the
    dry face lists under `agents` -- declared by this team and by no other -- else `agent-shared`, judged before any
    write. Without `--yes` it says what it would remove and writes nothing. Judged under `tick.lock` waited within
    `call_lock_wait` (`team-busy` beyond) and held to the end: `team-unknown`, `team-busy` while a task is open or a
    wake-up plays. Under `--yes`, `deleting` is written first, so that the team's guard lets its runs go; a purge or
    a removal refused stops the verb, said -- `delete` played again goes on. The agents not named stay: the ones no
    other team declares are said."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    wanted, rest = agents_asked(rest)
    asked = flags(rest, DELETE_FLAGS)
    directory = team_root(root, name)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    journal = journal_of(root, name)
    lock = locks(conductor)
    lease = None
    if journal.parent.is_dir():
        lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
        if lease is None:
            refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing removed, "
                   "replay once it has played.")
    try:
        state = state_of(journal)
        events = lines_of(journal) if journal.is_file() else []
        opened = [one["id"] for one in state["tasks"].values() if one["state"] == "open"]
        if opened or open_intents(state):
            refuse(f"team-busy -- {name} is at work ({', '.join(opened) or 'a wake-up plays'}): stop it first "
                   f"(`team stop {name} --kill`), then delete it.")
        runs = team_runs(state, events)
        relaunch = relaunch_standing(root)
        timer = bool(timer_standing(root, name))
        mine = set((state["started"] or {}).get("agents", {}).values()) if state["started"] else set()
        mine |= declared_paths(root, conductor, name)
        home = root.parent / TEAMS
        others: set[str] = set()
        for other in (sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []):
            if other != name:
                others |= declared_paths(root, conductor, other)
        agents = sorted(mine - others)
        shared = [one for one in wanted if one not in agents]
        if shared:
            refuse(f"agent-shared -- {', '.join(shared)}: not an agent {name} alone declares (another team declares it, "
                   f"or none does); the agents the team may take away are {', '.join(agents) or 'none'}; nothing removed.")
        told = {"team": name, "name": team_name(root, conductor, name), "dry": not asked["yes"],
                "directory": str(directory.relative_to(root.parent)),
                "journal": str(journal.parent.relative_to(root.parent)) if journal.parent.is_dir() else None,
                "relaunch": relaunch, "timer": timer, "runs": runs, "agents": agents, "removed": []}
        if asked["yes"]:
            if not state.get("deleting") and journal.is_file():
                appended(conductor, journal, name, [{"kind": "deleting"}])
            disarmed(root, name)
            if relaunch:
                relaunch_removed(root, conductor, name, but=name)
            by_path: dict[str, list[str]] = {}
            for one in runs:
                by_path.setdefault(one["path"], []).append(one["run"])
            for path, keys in by_path.items():
                if not agent_meta(root, path).is_dir():
                    continue
                why = purged(root, conductor, path, keys)
                if why:
                    refuse(f"delete-failed -- the purge of {', '.join(keys)} at {path} refused: {why} -- nothing more "
                           f"removed; `team delete {name} --yes` again goes on")
            for path in wanted:
                if not agent_meta(root, path).is_dir():
                    continue
                why = agent_removed(root, conductor, path)
                if why:
                    refuse(f"delete-failed -- the removal of {path} refused: {why} -- nothing more removed; "
                           f"`team delete {name} --yes` again goes on")
                told["removed"].append(path)
    finally:
        if lease is not None:
            lock.release(lease)
    if asked["yes"]:
        shutil.rmtree(journal.parent, ignore_errors=True)
        shutil.rmtree(directory, ignore_errors=True)
    if asked["json"]:
        print(json.dumps(told, ensure_ascii=False))
        return 0
    verb = "removed" if asked["yes"] else "would remove"
    print(f"pp-team: {name} · {verb}: {told['directory']}" + (f", {told['journal']}" if told["journal"] else "")
          + (", the relaunch entry" if relaunch else "") + (", the timer" if timer else "")
          + (f", {len(runs)} run(s): " + ", ".join(f"{one['path']} {one['run']}" for one in runs) if runs else ""))
    if told["removed"]:
        print(f"pp-team: {name} · the agents removed: {', '.join(told['removed'])}")
    staying = [one for one in agents if one not in told["removed"]]
    if staying:
        print(f"pp-team: {name} · the agents stay: {', '.join(staying)} -- no other team declares them"
              + ("" if asked["yes"] else f" (`--agent <path>` takes one away)"))
    if not asked["yes"]:
        print(f"pp-team: {name} · nothing written -- `team delete {name} --yes` removes it")
    return 0


def rename_verb(rest: list[str]) -> int:
    """`team rename <name> <new> [--json]`: moves the team to a new directory name -- its identity. Judged before any
    write: `new` as a team's name (`team-invalid`), `team-unknown`, `team-exists` when `teams/<new>/` or the records of
    `<new>` stand, `team-busy` under `tick.lock` past `call_lock_wait` or while a task is open or a wake-up plays.
    Then, the lock held: the timer disarmed (the next tick arms it again), `teams/<name>/` moved to `teams/<new>/`
    with the intention `TEAM-<name>.md` renamed `TEAM-<new>.md` inside it, the records of the team (its journal and
    the files beside it) moved, and `name:` of `TEAM.md` rewritten when it was the old directory's name -- a name of
    the owner's own stays. The house's relaunch entry does not change; the members' entries are laid again at the
    next start. Under `--json` ONE object `{from, to, name}`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    new, rest = named_team(conductor, rest)
    asked = flags(rest, RENAME_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    directory, target = team_root(root, name), team_root(root, new)
    journal, moved = journal_of(root, name), journal_of(root, new)
    if new == name or target.exists() or moved.parent.exists():
        refuse(f"team-exists -- {target} or its records stand already: another name.")
    lock = locks(conductor)
    lease = None
    if journal.parent.is_dir():
        lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
        if lease is None:
            refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing moved, "
                   "replay once it has played.")
    try:
        state = state_of(journal)
        opened = [one["id"] for one in state["tasks"].values() if one["state"] == "open"]
        if opened or open_intents(state):
            refuse(f"team-busy -- {name} is at work ({', '.join(opened) or 'a wake-up plays'}): stop it first "
                   f"(`team stop {name} --kill`), then rename it.")
        shown = team_name(root, conductor, name)
        disarmed(root, name)
        own = directory / document_name(name)
        if own.is_file() and not (directory / document_name(new)).exists():
            os.replace(own, directory / document_name(new))
        if journal.parent.is_dir():
            moved.parent.parent.mkdir(parents=True, exist_ok=True)
            os.replace(journal.parent, moved.parent)
        os.replace(directory, target)
    finally:
        if lease is not None:
            lock.release(lease)
    if shown == name:
        doc = team_doc(root, new)
        text = doc.read_text(encoding="utf-8")
        lines = text.split("\n")
        end = lines.index(BORDER, 1) if BORDER in lines[1:] else 0
        for index in range(1, end):
            if lines[index].rstrip() == f"name: {name}":
                lines[index] = f"name: {new}"
                placed(doc, "\n".join(lines).encode("utf-8"))
                break
        shown = new
    if asked["json"]:
        print(json.dumps({"from": name, "to": new, "name": shown}, ensure_ascii=False))
        return 0
    print(f"pp-team: {name} · renamed {new} · {TEAMS}/{new}/ and its records moved"
          + (f" · name: {shown}" if shown == new else f" · shown as {shown}"))
    return 0


def spent(root: Path, state: dict) -> str:
    """-> what the team has spent past its own bound since its last start, '' when nothing: the money
    (`budget`), the wake-ups launched (`budget-launches`), or a `budget-spent` already written -- the
    bounds of step 5, which a resume never resets."""
    limits = state["limits"]
    if state["budget_spent"]:
        return "budget-spent is written since the last start"
    if limits.get("budget") is not None and state["cost"] >= limits["budget"]:
        return f"{state['cost']:g} of {limits['budget']:g} USD spent"
    if limits.get("budget-launches") is not None:
        launched = launched_since_start(root, state)
        if launched >= limits["budget-launches"]:
            return f"{launched} of {limits['budget-launches']} launches"
    return ""


def launched_since_start(root: Path, state: dict) -> int:
    """-> the team's wake-ups LAUNCHED since its last `team-started` -- the `wake-launched` event,
    else the tag at the house's `messages.jsonl`: what `budget-launches` counts."""
    started = state["started"] or {}
    tagged = {str(one.get("tag")) for one in lines_of(record_of(root, MESSAGES)) if one.get("tag")}
    return sum(1 for tag, one in state["intents"].items()
               if int(one.get("id") or 0) > int(started.get("id") or 0) and went(state, tagged, tag))


def resume_verb(rest: list[str]) -> int:
    """`team resume <name> --task <id> [--message <text>] [--as <principal>] [--no-tick]`: takes back
    ONE task a guard left with nobody due -- stopped, held by a member's final failure, or past
    `launches:` --, judged under the journal's lock before anything is written; then `resumed {task, by,
    from}`, the origin the task's counters count from, and an `info` from the resumer to each member it
    revives: the holders at the stop, the members whose final failure stands, the members with
    messages due past `launches:`. The posts returned at the stop stay returned; the team's `budget` and
    `budget-launches` are never reset. Then the relaunch entry laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESUME_FLAGS)
    if asked["task"] is None:
        if asked["message"] is not None:
            refuse(USAGE)
        return unpause(root, conductor, name, asked)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)
    text = asked["message"] if asked["message"] is not None else RESUMED

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        task = state["tasks"].get(asked["task"])
        if task is None:
            refuse(f"task-unknown -- no task `{asked['task']}` of {name}: the tasks are "
                   f"{', '.join(state['tasks']) or 'none'}.")
        if task["state"] == "resolved":
            refuse(f"task-resolved -- {task['id']} is resolved: a post opens a new task instead.")
        why = spent(root, state)
        if why:
            refuse(f"budget-spent -- {name}: {why}; a resume never resets the team's budget -- `team budget "
                   f"{name} <usd> | --launches <n>` raises it.")
        fell = [agent for agent, one in sorted(state["fell"]) if one == task["id"]]
        causes = ((["stopped"] if task["state"] == "stopped" else []) + (["failed"] if fell else [])
                  + (["launches-spent"] if task["id"] in state["launches_spent"] else []))
        if not causes:
            refuse(f"task-not-blocked -- {task['id']} is open, no final failure stands on it and its launches "
                   "are not spent: nothing to take back.")
        revived = holders(state, task) if task["state"] == "stopped" else []
        revived += fell
        if task["id"] in state["launches_spent"]:
            revived += [agent for agent in (state["started"].get("agents") or {})
                        if any(one.get("task") == task["id"] for one in inbox(state, agent))]
        return ([{"kind": "resumed", "task": task["id"], "by": sender, "from": causes}]
                + [{"kind": "post", "task": task["id"], "from": sender, "to": one, "verb": "info", "text": text}
                   for one in dict.fromkeys(revived)])

    made = written(conductor, journal, name, judge)
    for one in made:
        if one["kind"] == "resumed":
            print(f"pp-team: {name} · {one['task']} · resumed #{one['id']} from {', '.join(one['from'])}")
        else:
            print(f"pp-team: {name} · {one['task']} · post #{one['id']} info {one['from']} -> {one['to']}")
    netted(root, conductor, name, state_of(journal))   # the task open again: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def pause_verb(rest: list[str]) -> int:
    """`team pause <name> [--as <principal>]`: the team PAUSED -- `paused {by}`, judged under the journal's
    lock; nothing killed, no tick: the wake-ups under way end on their own, and until `team resume <name>`
    the tick reaps and routes but rings and wakes nobody."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, PAUSE_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        if state["paused"]:
            refuse(f"team-paused -- {name} is paused since #{state['paused'].get('id')}: `team resume {name}` "
                   "takes it back.")
        return [{"kind": "paused", "by": sender}]

    made = written(conductor, journal_of(root, name), name, judge)[0]
    running = len(open_intents(state_of(journal_of(root, name))))
    print(f"pp-team: {name} · paused #{made['id']} by {made['by']} · {running} wake-up(s) under way end on their own"
          f" · nobody is woken until `team resume {name}`")
    return 0


def unpause(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> [--as <principal>] [--no-tick]`: the paused team taken back -- `unpaused {by}`,
    judged under the journal's lock; then the relaunch entry laid again, and a tick unless `--no-tick`:
    what is due now, each member in its own run."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        if not state["paused"]:
            refuse(f"team-not-paused -- {name} is not paused: `team resume {name} --task <id>` takes a task back.")
        return [{"kind": "unpaused", "by": sender}]

    made = written(conductor, journal, name, judge)[0]
    print(f"pp-team: {name} · unpaused #{made['id']} by {made['by']}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # the team back: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def budget_verb(rest: list[str]) -> int:
    """`team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]`: RAISES the team's bounds
    without a start -- `budget` in dollars, `budget-launches` in launches --, judged under the journal's lock
    before anything is written: each above what the team spent since its last start (`budget-invalid`).
    Then `budget-raised {budget, launches, by}`: the replay takes the new limits and lifts `budget-spent`;
    the members keep their runs. Then the relaunch entry laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    usd = None
    if rest and not rest[0].startswith("--"):
        usd, rest = rest[0], rest[1:]
    retired_flags(rest)
    asked = flags(rest, BUDGET_FLAGS)
    if usd is None and asked["launches"] is None:
        refuse(USAGE)
    try:
        money = None if usd is None else float(usd)
        wakes = None if asked["launches"] is None else int(asked["launches"])
    except ValueError:
        refuse(f"budget-invalid -- `{usd if asked['launches'] is None else asked['launches']}`: dollars are a number, "
               "launches a whole number.")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        if money is not None and not money > state["cost"]:
            refuse(f"budget-invalid -- {name}: {money:g} USD is not above the {state['cost']:g} USD spent since "
                   "the start.")
        launched = launched_since_start(root, state)
        if wakes is not None and not wakes > launched:
            refuse(f"budget-invalid -- {name}: {wakes} launches is not above the {launched} launched since the "
                   "start.")
        return [{"kind": "budget-raised", "by": sender,
                 **({"budget": money} if money is not None else {}), **({"launches": wakes} if wakes is not None else {})}]

    made = written(conductor, journal, name, judge)[0]
    said = " · ".join(one for one in (f"budget {made['budget']:g} USD" if "budget" in made else "",
                                      f"budget-launches {made['launches']}" if "launches" in made else "") if one)
    print(f"pp-team: {name} · raised #{made['id']} · {said}")
    state = state_of(journal)
    if any(one["state"] == "open" for one in state["tasks"].values()):
        netted(root, conductor, name, state)       # a task open: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def guard_verb(rest: list[str]) -> int:
    """`pp-team guard` (the vector on stdin): the GUARDIAN of the family `agent-run:<path>/<key>` -- the
    engine's call when `agent purge` asks before removing a run. A run a member of a LIVING team holds (the
    team started, a task open or a ceremony declared, and no `deleting` written) refuses, the team, the member and `team reset` named:
    purged, the member's next wake-up would find no run. Reads only, no lock."""
    if rest:
        refuse(USAGE)
    root, conductor = house()
    prefix, _, ident = conductor.reading.piped().strip().partition(":")
    if prefix != "agent-run":
        refuse(f"family-foreign -- `{prefix}:` is not a family this package guards (agent-run)")
    path, _, key = ident.rpartition("/")
    home = root.parent / TEAMS
    for name in sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []:
        journal = journal_of(root, name)
        if not journal.is_file():
            continue
        state = state_of(journal)
        if state["started"] is None or netless(state) or state.get("deleting"):
            continue
        for member, run in ((member, run) for member, held in state["runs"].items() for run in held.values()):
            if run == key and path_of(state, member) == path:
                refuse(f"member-run -- run {key} of {path} is the run of member {member} of team {name}, "
                       f"which lives: `team reset {name} --member {member}` first, or wait for the team's end")
    return 0


def ring_verb(rest: list[str]) -> int:
    """`team ring <name> <ceremony> [--as <principal>] [--no-tick]`: rings ONE declared ceremony at
    hand, out of its hour -- the tick's ring (`ringing`) under the period `manual-<id>`, the id of its
    own `ceremony-due`, which `by` names the principal of; judged under the journal's lock before
    anything is written, one ring of a ceremony at a time (`ceremony-open`). Then the relaunch entry
    laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    called, rest = rest[0], rest[1:]
    asked = flags(rest, RING_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        declared = state["started"].get("ceremonies") or []
        ceremony = next((one for one in declared if one.get("name") == called), None)
        if ceremony is None:
            refuse(f"ceremony-unknown -- {name} declares no ceremony `{called}`: the ceremonies are "
                   f"{', '.join(str(one.get('name')) for one in declared) or 'none'}.")
        held = [one["id"] for one in state["tasks"].values()
                if one.get("ceremony") == called and one["state"] == "open"]
        if held:
            refuse(f"ceremony-open -- {held[0]} of `{called}` is open: one ring at a time, ring again once it "
                   "is resolved or stopped.")
        first = max((int(one.get("id") or 0) for one in events), default=0) + 1
        return ringing(state, name, ceremony, f"manual-{first}", by=sender)

    made = written(conductor, journal, name, judge)
    task = next(one for one in made if one["kind"] == "task")
    print(f"pp-team: {name} · {called} rung at hand · {made[0]['period']} #{made[0]['id']} · task {task['task']} "
          f"to {task['to']}")
    netted(root, conductor, name, state_of(journal))   # a task open: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def same_period(one: dict, other: dict) -> bool:
    """-> whether two periods of a recurrence come back alike: the same dated period, or durations of the same
    seconds (`4h` and `240m`)."""
    if one.get("kind") == "interval" and other.get("kind") == "interval":
        return one.get("seconds") == other.get("seconds")
    return one == other


def recurrence_verb(rest: list[str]) -> int:
    """`team recurrence <name> <R<n>> [--every "<when>"] [--context <n>%|off] [--message <text>] [--as <principal>]
    [--no-tick]`: CHANGES a live recurrence -- its period, its context limit, its text, one of them at least.
    `recurrence-changed {recurrence, when, since, context, text, by}` carries what changes alone: `when` and `since` -- the
    local hour of the change -- for a new period, `context` for a new limit (`null` under `off`, the limit taken away),
    `text` for a new intention; judged under the journal's lock before anything is written, `message-missing` for an
    empty text, `recurrence-unchanged` when every value asked is in force. The replay replaces what the event carries
    and keeps the periods it sounded: a new hour holds from its next period after the change, a new limit from the next
    first wake-up on an occurrence, a new text from the next occurrence -- an occurrence sounded keeps its own.
    `team recurrence <name> --task <T<n>> --every "<when>" [--context <n>%] [--as <principal>] [--no-tick]`: lays a NEW
    recurrence on a task that exists -- `recurrence {R<n>, from, to, text, name, when, since, context, task}`, its member,
    its text and its name the task's, its principal the one who plays the verb --; the replay makes the task its LAST
    occurrence, so that no period opens one while it is open (`task-unknown`, `task-recurrent` for an occurrence or a
    ring's task; `R<n>` or `--message` beside `--task`, the usage). Then the net laid again, and a tick unless
    `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    called = None
    if rest and not rest[0].startswith("--"):
        called, rest = rest[0], rest[1:]
    asked = flags(rest, RECURRENCE_FLAGS)
    if called is None and (asked["task"] is None or asked["every"] is None or asked["message"] is not None):
        refuse(USAGE)                                 # a recurrence born of a task: its period owed, its text the task's
    if called is not None and (asked["task"] is not None
                               or (asked["every"] is None and asked["context"] is None and asked["message"] is None)):
        refuse(USAGE)
    if asked["message"] is not None and not asked["message"].strip():
        refuse("message-missing -- a recurrence carries its text: --message <text>, not empty.")
    when = None
    if asked["every"] is not None:
        when = every_of(asked["every"])
    limit = limit_of(asked["context"], off=called is not None) if asked["context"] is not None else None
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def born(state: dict, sender: str) -> list[dict]:
        task = state["tasks"].get(asked["task"])
        if task is None:
            refuse(f"task-unknown -- no task `{asked['task']}` of {name}: the tasks are "
                   f"{', '.join(state['tasks']) or 'none'}.")
        if task.get("recurrence") or task.get("ceremony"):
            refuse(f"task-recurrent -- {task['id']} is an occurrence of "
                   + (f"{task['recurrence']}" if task.get("recurrence") else f"the ceremony `{task['ceremony']}`")
                   + ": its run has a carrier already.")
        return [{"kind": "recurrence", "recurrence": f"R{len(state['recurrences']) + 1}", "from": sender,
                 "to": task["to"], **({"name": task["name"]} if task.get("name") else {}), "text": task.get("text"),
                 "when": when, "since": tick_now().isoformat(timespec="seconds"), "context": limit, "task": task["id"]}]

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        if called is None:
            return born(state, sender)
        recurrence = state["recurrences"].get(called)
        if recurrence is None:
            refuse(f"recurrence-unknown -- no recurrence `{called}` of {name}: the recurrences are "
                   f"{', '.join(state['recurrences']) or 'none'}.")
        if recurrence["stopped"] is not None:
            refuse(f"recurrence-stopped -- {recurrence['id']} was stopped at #{recurrence['stopped']['id']}.")
        changes: dict = {}
        if when is not None and not same_period(recurrence["when"], when):
            changes.update(when=when, since=tick_now().isoformat(timespec="seconds"))
        if asked["context"] is not None and recurrence.get("context") != limit:
            changes["context"] = limit
        if asked["message"] is not None and recurrence.get("text") != asked["message"]:
            changes["text"] = asked["message"]
        if not changes:
            refuse(f"recurrence-unchanged -- {recurrence['id']} comes back every {said_when(recurrence['when'])}, "
                   "its context limit "
                   + (f"{recurrence['context']}%" if recurrence.get("context") is not None else "off")
                   + ", its text as asked already.")
        return [{"kind": "recurrence-changed", "recurrence": recurrence["id"], **changes, "by": sender}]

    made = written(conductor, journal, name, judge)[0]
    if made["kind"] == "recurrence":
        print(f"pp-team: {name} · recurrence {made['recurrence']} to {made['to']} from {made['task']} · every "
              f"{said_when(made['when'])}" + (f" · context {made['context']}%" if made["context"] is not None else "")
              + f" · #{made['id']} -- no period opens a task while {made['task']} is open")
    else:
        print(f"pp-team: {name} · recurrence {made['recurrence']}"
              + (f" · every {said_when(made['when'])}" if "when" in made else "")
              + (f" · context {made['context']}%" if made.get("context") is not None
                 else " · context off" if "context" in made else "")
              + (" · text changed" if "text" in made else "")
              + f" · #{made['id']} -- from its next period" + (" and its next occurrence" if "context" in made else ""))
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # a live recurrence keeps the net
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def main(argv: list[str]) -> int:
    verbs = {"start": start, "post": post, "stop": stop, "tick": tick, "follow": follow, "timer": timer_verb, "status": status,
             "watch": watch, "log": log_verb, "result": result, "responses": responses_verb,
             "inbox": inbox_verb, "snapshot": snapshot_verb, "entry": entry_verb, "reset": reset_verb,
             "resume": resume_verb, "pause": pause_verb, "ring": ring_verb, "budget": budget_verb, "guard": guard_verb,
             "recurrence": recurrence_verb,
             "templates": templates_verb, "new": new_verb, "declaration": declaration_verb, "delete": delete_verb,
             "rename": rename_verb}
    if not argv or argv[0] not in verbs:
        refuse(USAGE)
    return verbs[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
