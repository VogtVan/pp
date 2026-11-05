# team

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `1.0.0`

`team` is a package for [Procedural Prompting](../../README.md). It lets a house --
a workspace with the [`agent`](../agent/README.md) package -- run **teams** of agents
that work on one task together: one member receives the task, delegates parts to
others, waits for their answers and reports back to you.

A team needs no model to move. A short process, the **tick**, reads the team's state,
routes the acts the members say and launches the members that have something to do. Each
wake-up is ONE launch of an agent by the house, with what arrived for it at the head of its prompt.

## Role

A single agent answers one message at a time. Work such as a review by several
reviewers, a daily round of reports or a chain of steps needs agents that hand work to
one another, wait for one another and stop within limits you set. `team` keeps that
coordination explicit and bounded, and tells you what waits for you.

It answers four questions:

- Who is in the team, who reports to whom, and who receives a task?
- How do I give the team a task, follow it, and stop it?
- How much may the team spend, and how many wake-ups may it take?
- What does the team wait for from me: an answer, a decision, a result to read?

## Features

### A team is declared in one document

You declare a team in `teams/<name>/TEAM.md`: its members, each a name played by one
agent of the house (`r1 agents/reviewer`; one agent may play several members), who
reports to whom, the **root** that receives a task, the people allowed to post, and
optional limits and ceremonies, and the `name` the team is shown by -- changeable at any
time, the directory staying the team's identity. The team's intention lives beside it, in
`teams/<name>/TEAM-<name>.md`: you write its body, `team start` writes its head, and pp
serves it to every member. What every member must do in a team -- who answers to whom, the
messages it may send, the answer it owes -- is the package's part of the standing orders,
the same for every team. `team delete <name> --yes` removes a team and what it made.

```
---
agents: |
  lead agents/lead
  r1 agents/reviewer
  r2 agents/reviewer
reports: |
  r1 r2 -> lead
root: lead
budget: 5
---
Review the pull request together: the lead delegates, the reviewers report.
```

`./pp team templates` lists ready-made forms (`supervisor-workers`,
`lead-reviewers`, `chain`, `solo`, `empty`, `council`, `triage`, `cross-check`, `tree`), and `./pp team new <name> --template <t>`
writes a `TEAM.md` from one. `./pp team declaration <name>` shows how `start` judges
the document, without writing anything.

### Start, post, stop

| command | what it does |
|---|---|
| `./pp team start <name> --message "…"` | reads the declaration, creates the agents the house lacks, opens the first task; without `--message`, the team starts with no task and waits for its ceremonies and your posts |
| `./pp team post <name> --message "…"` | adds a task, an info, a reply or a stop at any time; `--name` names a task |
| `./pp team stop <name>` | stops the open tasks; `--kill` also ends the wake-ups under way |
| `./pp team pause <name>`, `./pp team resume <name>` | holds the team: nobody is woken until it resumes |
| `./pp team resume <name> --task <id>` | takes back a task a limit had stopped |
| `./pp team reset <name> --member <member>` | gives a member a new run at its next wake-up |

### The tick moves the team

`./pp team tick <name>` advances the team once: it collects the wake-ups that ended,
routes each act a member said to the member it is for, judges who waits for whom and
launches the next wake-ups. The end of every wake-up triggers the next tick, and the
NET catches a tick that died: a TIMER the tick arms at its end when something is due --
a process that sleeps until the deadline, ticks once and dies, one per team, none when
nothing is due. `schedule:` of `TEAM.md` says its step, how long it sleeps at most: `10s`,
`2m`, `1h` or a bare number of minutes, 5 minutes unless said, `off` for none. The timer
dies with the machine; ONE relaunch entry per house brings back every team that needs it
when the user opens a session (`@reboot` in the crontab on Linux, a value of the user's Run
key on Windows).

### One act for each message

A member speaks in acts -- a JSON value said alone, one element or a list of them, read as it is
said while the member still works: it hands work to the members
who report to it (`do`), asks a question of anyone in the team or of you (`ask`), or
answers a message it received (`{"re": <id>, "text": "…"}` -- « re » means « in answer
to »). Every `do` and `ask` a member receives is a debt: the member owes that message one
answer, in the same wake-up or a later one. The member that holds a task closes it by
answering the message that opened it, with the result; a member who only took part never
closes a task.

A member that puts an answer off is not forgotten. When the team stands still -- everyone
waiting for someone who waits too, or for a member that has nothing left to read -- the tick
reminds the member at the bottom of the chain that it still owes an answer, as long as it owes.
A member that stays SILENT -- `silence:` exchanges without one act, an `info` counts -- gets one
reminder, then is suspected as a failing member is: the tick answers in its place to the members
waiting for it, and a task you opened that its member leaves silent comes back to you: the team
sends you a notice. A member that says where it stands is never stopped by a count.

A member that keeps failing -- a model that errs, a program that crashes -- may be broken, or only
down for a while. The tick does not wait for it, and does not give it up either. Once a wake-up
of the member has failed for good, the member is suspected for a while: 5 minutes, or the
step of the team's schedule, doubled each time it fails again and never past `suspect-max:`
(10 minutes unless said). During that time no member wakes it: whatever a member asks of it
gets an answer from the tick in its place (« r2 is not answering at the moment; it is tried
again at 14:20:05 »). What YOU say to it -- a task, an info, an answer -- reaches it at once: the
tick launches it on your word, and that launch is its try. After that time, its next message
tries it again. If it answers, it is trusted again. Every other member reads, at the top of its
message, who is not answering at the moment. `./pp team resume <name> --task <id>` and a new
`./pp team start` trust it again at once. A launch the house itself refused before the
member's program ran -- a package missing, a run held -- counts against nobody: the member is
launched again at the next tick, and you get one notice.

### Limits that hold

The declaration may bound the team: `parallel` (launches at once), `budget` (dollars
since the start; each launch gets its share of what is left), `budget-launches` and
`launches` (launches of the team and of one task), `retries`, and `timeout` (a launch
stuck longer is ended). When a limit is reached, nothing more is launched and the team
sends you a notice. `./pp team budget <name> <usd>` raises the budget without a
restart.

### Ceremonies

A ceremony is a recurring task: `daily every weekday 09:30 with r1 r2 -> lead`. The
tick rings it once per period; `./pp team ring <name> <ceremony>` rings it at hand.
`any <n>` sets a quorum: the facilitator is woken at the n-th answer.

A task can recur too, without a meeting:
`./pp team post <name> --message "review the PRs" --to w --every "weekday 09:30"`. The tick
opens one task per period. It opens none while the one before is still open.
`./pp team recurrence <name> R1 --every "weekday 14:00"` changes its hour;
`./pp team stop <name> --recurrence R1` ends it.

### Following a team

| command | what it says |
|---|---|
| `./pp team status [<name>]` | the members, their runs, the tasks, the limits, the cost and what waits for you |
| `./pp team watch <name>` | the team's events as they happen |
| `./pp team log <name>`, `./pp team result <name>`, `./pp team responses <name>` | the journal, the result of a task, the members' answers |
| `./pp team inbox` | what waits for you: questions without an answer, the team's notices, tasks done, messages returned |

`status`, `log`, `responses`, `inbox` and `watch` take `--json`, the form a program
reads -- the [`ui`](../ui/README.md) package reads them. In `status --json`, each task
says the hour it was born (`at`) and the hour it ended (`ended`, null while it is open). What waits for you also
reaches your own sessions in the house, at the start of each exchange.

### One journal

A team's state is its journal: events appended, never rewritten, under the house's
records. Every reading computes the same state from the same lines. `pp-team` is its
only writer.

## Installation

`team` requires the `agent` package and the `kit`; the installer pulls both
automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> team -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add team
```

After a restart, the teams come back by the house's ONE relaunch entry: on Linux an
`@reboot` line in the user's crontab, so `cron` must be running (under WSL: `sudo service
cron start`); on Windows a value of the user's own Run key, which needs no administrator
rights. If the entry cannot be written, the teams run on without it, and you get a notice
that says why.

## Quick start

Write a team from a template, start it with its first task and follow it:

```sh
./pp team new review --template lead-reviewers \
  --member lead agents/lead --member rev agents/rev --budget 5
./pp team start review --message "Review the pull request #12."
./pp team watch review
```

Answer what the team asks you, then read the result:

```sh
./pp team inbox
./pp team post review --task <task> --reply <id> --message "Yes, keep the old API."
./pp team result review
```

Give the team another task later, or stop it:

```sh
./pp team post review --name "Second review" --message "Review #13 the same way."
./pp team stop review
```

## Reference

This section states the package in full: every key, verb, event, field and refusal, by
topic.

- [The declaration](#the-declaration)
- [The journal](#the-journal)
- [Starting a season](#starting-a-season)
- [Posting, stopping, taking a task back](#posting-stopping-taking-a-task-back)
- [Pausing, raising the budget, resetting a member](#pausing-raising-the-budget-resetting-a-member)
- [The tick](#the-tick)
- [Acts, debts and waits](#acts-debts-and-waits)
- [Deadlocks and relances](#deadlocks-and-relances)
- [Members that fail](#members-that-fail)
- [Notices of the team](#notices-of-the-team)
- [Limits](#limits)
- [The schedule and its net](#the-schedule-and-its-net)
- [Ceremonies](#ceremonies-1)
- [Entries and the team's directory](#entries-and-the-teams-directory)
- [One run per member](#one-run-per-member)
- [Task names](#task-names)
- [Templates](#templates)
- [Reading a declaration](#reading-a-declaration)
- [Following a team](#following-a-team-1)
- [The faces](#the-faces)
- [Routes and answers](#routes-and-answers)
- [Names and paths](#names-and-paths)

### The declaration

A house that pins the `team` package has **teams**. The owner DECLARES each team at
`teams/<name>/TEAM.md`. Its front matter says who the team is and how it is bounded; its
body is never served.

#### The keys of `TEAM.md`

| key | what it holds |
|---|---|
| `agents: |` | the MEMBERS, one `<name> <path>` per line: the member's name, then the path of the agent under the house that plays it. One path may play several members at will. |
| `reports: |` | who reports to whom, as edges `a b c -> d` |
| `root` | the member that receives a task |
| `principals: |` | the mandators allowed to post. The owner, the house's slug, is always admitted. |
| `ceremonies: |` | the ceremonies to come, read for their names, their participants and their `after` graph ([Ceremonies](#ceremonies-1)) |
| `work` | the repository each opening clones ([One run per member](#one-run-per-member)) |
| `name` | the name the team is shown by: one line of 1 to 80 printable characters, read at every call. A rename moves nothing: the directory is the team's identity. |
| `schedule:` | the step of the team's net ([The schedule and its net](#the-schedule-and-its-net)) |
| `entries:` | the document a wake-up plays on each trigger ([Entries and the team's directory](#entries-and-the-teams-directory)) |
| `parallel`, `budget`, `budget-launches:`, `launches:`, `retries:`, `timeout:` | the limits ([Limits](#limits)) |
| `silence:` | the silent exchanges that earn a member one reminder, 3 unless said ([Deadlocks and relances](#deadlocks-and-relances)) |
| `suspect-max:` | the longest suspicion of a failing member ([Members that fail](#members-that-fail)) |

#### The intention

The team's intention is the body of `teams/<name>/TEAM-<name>.md`, and that body is the
owner's. `team start` writes the document's head (`attach: turn.begin`, `proc: SERVE`
serving the document itself) and keeps its body to the byte. Without the file, `team start`
refuses `team-document-missing`.

The engine serves the body at a member's opening. It serves it again at the exchange after
the owner edits it, under the same key, with no new start. The intention is never copied
into a message nor into the journal.

`team status` says `TEAM.md changed since the start` when the declaration differs from the
start's `digest`.

#### The contract of the acts

The rules every member follows -- the acts it may say, the answer it owes -- are the
package's fragment of the standing orders, `packages/team/system/SYSTEM.COMMON.md`. That
fragment is compiled into every marble of the house (see
[The marble, in layers](../../docs/reference/instance.md#the-marble-in-layers)).

#### Deleting a team

`team delete <name> [--agent <path>]... [--yes] [--json]` removes a team and what it made:

- its timer;
- its relaunch entry;
- every run its wake-ups opened (`agent purge`, once `deleting` lets the guard go);
- its journal;
- `teams/<name>/`.

The agents are left standing, unless `--agent <path>` names one: it is then taken away
with the team by `agent remove` -- its runs purged, the files pp wrote in its directory and
its instance removed, its directory when nothing else stands in it. Only an agent the team
alone declares may be named: the dry run lists them under `agents`; another one refuses
`agent-shared` before anything is written. While a task is open, the command refuses
`team-busy`.

#### Renaming a team

`team rename <name> <new> [--json]` moves the team to `teams/<new>/` -- the name every verb
and the post address it by -- with its journal and the files beside it; the intention
`TEAM-<name>.md` becomes `TEAM-<new>.md`, and `name:` of `TEAM.md` is rewritten when it was
the old directory's name (a name of your own stays). It plays on a team at rest: a task
open or a wake-up under way refuses `team-busy`, a name taken `team-exists`, a name that is
not a slug `team-invalid`. The timer is disarmed and armed again by the next tick; the
relaunch entry does not change; the members' entries are laid again at the next start.

### The journal

The team's state is its JOURNAL, `.pp/.sys/records/teams/<name>/journal.jsonl`. It holds one
event per line, `{at, id, kind, team, …}`, each id being the previous one + 1.

`pp-team` alone writes it, appending under the record's lock. It is never rewritten, and it
is read again at every reading. A last line still being written is skipped; a torn line
anywhere else makes the reading refuse, by its name.

#### Snapshots

`./pp team snapshot <name>` writes ONE `snapshot {upto, state}` event under the journal's
lock: the replayed state, packed as JSON. The resolved tasks' messages are pruned from it;
the posts returned to the owner are kept by their ids.

Every state reader -- the tick, `status`, `responses`, `inbox` -- parses the journal from its
last snapshot line on and restarts there. `log` and `watch` read the whole history and never
show the snapshot. Nothing is rewritten: `status` renders the same bytes before and after.

#### Journals written by earlier versions

The code still reads older journals:

- A journal written before team 0.33.0 reads as written. Its `delegation` and `terminal`
  events still count, and a member's `done` or `escalate` to the member that delegated is
  read as the answer to that member's last `do`.
- `log` and `watch` say such a journal in today's words: a member's `done`, `reply` or
  `escalate` as `re` (`was` gives its old verb), an `escalate` to a principal as the team's
  `notice`. They never show `delegation` nor `terminal`, which the replay still reads.
- A journal written before team 0.40.0 keeps no rank: the tick routes nothing of the
  exchanges before it.
- A `launch.max_budget_usd` that an older journal kept is never passed on; `status` says so
  once.

### Starting a season

```
./pp team start <name> [--message "<text>" [--to <agent>]] [--budget <usd>]
    [--budget-launches <n>] [--package <name>=on|off]...
    [--member <agent> [--provider|--model|--effort|--permissions <v>] [--package <name>=on|off]...]...
```

`team start` opens a SEASON of the team: the first one, or one more on a team at work.

#### What start refuses

`team start` reads the declaration whole and refuses before anything is written:

| refusal | when |
|---|---|
| `team-unknown`, `team-invalid`, `root-missing`, `participant-unknown`, `ceremony-cycle`, `budget-invalid`, `package-invalid` | the declaration or the flags fail the judge, as named |
| `entry-missing` | an entry stands neither in the team's directory nor in the instance of an agent whose members play it |
| `package-required` | a member switches off `team` or a package it requires, read from the manifests |
| `package-unpinned` | a package the house does not pin is switched on (switched off, it asks nothing) |
| `package-dependency` | a package is switched on while the same composition switches off a package it requires |
| `member-held` | `TEAM.md` drops a member that holds an open task |
| `team-document-missing` | `teams/<name>/TEAM-<name>.md` is missing |
| `born-busy` | the birth lock of a path is held past `call_lock_wait` |

#### The season's own settings

The season's `--budget` and `--budget-launches` stand above those of `TEAM.md` until the
next season. They are kept at `team-started.season`; `TEAM.md` is left untouched.

The flags after a `--member`, up to the next one, are that member's profile, kept at
`team-started.profiles`. They replace the team's provider, model, effort or permissions for
that member.

#### The season decides the packages

In a team, the season decides which packages a member plays, never the member's own
`SETTINGS.md`. `team start` writes the SET of each member's packages: one `<name>=on|off`
for every package the house pins beyond its base.

- A package is `on` when the season switches it on, or when the team requires it (`team`
  and what it requires).
- Every other package is `off`.
- `--package <name>=on|off` before the first `--member` is the team's. A member's
  `--package` covers the team's, name by name.
- A season that names no package gives every member the packages the team requires, and
  nothing else.

The set is kept whole at `team-started.packages`, and at the `packages` of a profile that
names some. Every wake-up hands the whole set to the member's `agent start`: a run's
opening composes its first block with it, and a resume plays what the run does not hold
yet. A member therefore plays its season from its first block, whatever its agent's
settings say.

A package switched on whose requirement the set switches off refuses `package-dependency`
before anything is written: `--package doc=on` needs `--package steering=on` beside it.

A journal written by team 0.49.0 to 0.51.0 lists only the packages its season named. It is
read under the same rule: a package it does not name is off.

#### What a season keeps

A season keeps the members' runs, keys and sessions, the tasks, their waits and their
failures. It counts afresh the cost, `budget-spent`, `budget-launches` and each task's
`launches:`. A task that a final failure left blocked is taken back by `resume`.

#### What start writes

`team start` creates the agents the house lacks, at their paths. Each path is born once,
under the house's birth lock for that path (`state/born-<digest>.lock`, the same lock
`agent add` takes). Each new agent borrows the house's machine and gets no door.

It then writes `team-started`. Under `--message` it also writes the task `T<n>` and its `do`
post from the owner to `--to`, or to the root.

Without `--message`, no task opens. The season stands on its ceremonies and on the posts to
come, and the team is `idle`. The relaunch entry is laid at the start only when a task is
open or a ceremony is declared; otherwise the first post lays it.

### Posting, stopping, taking a task back

`start`, `post` and `stop` tick right after their write; `--no-tick` spares that tick.

#### `team post`

```
./pp team post <name> [--message …] [--to <agent>] [--task <id> | --name <text>] [--reply <id>] [--stop] [--as <principal>] [--every "<when>"]
```

`team post` adds a new task, or an `info`, a `reply` or a `stop` on a standing one.
`post --reply <id>` writes the principal's answer, a `re`. `post --every "<when>"` lays a
recurring task instead ([Recurring tasks](#recurring-tasks)).

| refusal | when |
|---|---|
| `task-closed` | the task is stopped or resolved |
| `principal-unknown` | the name is neither the owner nor a mandator |
| `every-invalid` | the period is not `day`, `weekday` or a day of the week, then `HH:MM` |

#### `team stop`

```
./pp team stop <name> [--task <id>] [--kill]
./pp team stop <name> --recurrence <R<n>>
```

`team stop --recurrence R<n>` ends a recurring task: no new task opens for it. The task it
opened last, if still open, goes on; `--task` stops it. `recurrence-unknown` names no
recurrence of the team; `recurrence-stopped` names one already ended.

#### `team recurrence`

```
./pp team recurrence <name> <R<n>> --every "<when>" [--as <principal>] [--no-tick]
```

`team recurrence` changes when a recurring task comes back: its day, its hour, or both. The
recurrence keeps its id, its member, its name and its text; to change one of those, stop it
and post a new one. A day is counted once: if the task already opened today, the new hour
starts at the next day it applies to.

| refusal | when |
|---|---|
| `recurrence-unknown` | no recurrence of the team has that id |
| `recurrence-stopped` | the recurrence was stopped |
| `every-invalid` | the period is not `day`, `weekday` or a day of the week, then `HH:MM` |
| `recurrence-unchanged` | the recurrence already comes back at that period |

`team stop` stops one task, or every open one. It posts the `stop` to every agent holding
the task: the task's agent unless it answered the opening, and each delegate that has not
answered its last `do`. It returns the posts left undelivered on the task.

The stop is delivered at once. A wake-up under way is not interrupted: it ends, its answer
is reaped and routed nowhere, and no agent is woken for the stop.

`--kill` ends, now, every wake-up under way on the task that has not answered: the launcher,
the harness and what it runs, all at once. It writes `wake-killed {tag, agent, task, run,
pid}`. Nothing is kept, nothing is retried, and the stop counts as delivered.

A wake-up that has answered is spared; the tick ends it and counts its cost. Whether it has
answered is read as the reap reads it: by (run, index), then without a run under the key
handed. A `stop --kill` ends the wake-up of its own task alone: the member keeps its key for
its other tasks.

A task stops whatever holds it. Every stop writes `stopped {task, by}` before its posts. A
task nobody holds any more stops without any post (`stopped -- nobody held it`), and the
team is free to start again.

#### `team resume --task`

`team resume <name> --task <id> [--message <text>] [--as <principal>] [--no-tick]` takes
back ONE task that a guard left with nobody due: a task stopped, held by a member's final
failure, or past `launches:`.

It is judged under the journal's lock. It refuses `budget-spent` (judged first),
`task-resolved` and `task-not-blocked`.

It writes `resumed {task, by, from}` and an `info` to each member it revives:

- the holders at the stop;
- the members whose final failure stands;
- the members with messages due past `launches:`.

The replay opens the task again. It counts the task's failures and its `launches:` from that
event, and drops the `terminal` that a final failure wrote. A resume never resets the team's
`budget` nor `budget-launches`, and the posts returned at the stop stay returned.

The next tick wakes each revived member in its run, under its key.

### Pausing, raising the budget, resetting a member

#### `team pause` and `team resume`

`team pause <name> [--as <principal>]` PAUSES the team. It is judged under the journal's
lock and refuses `team-not-started`, `principal-unknown` or `team-paused`. It writes
`paused {by}` and kills nothing: the wake-ups under way end on their own, and the tick reaps
them and routes their answers.

`team resume <name> [--as <principal>] [--no-tick]` ends the pause by writing
`unpaused {by}`; on a team not paused it refuses `team-not-paused`. Until then, the tick
writes no `wake-intent` and no `ceremony-due`; the pause is judged under the journal's lock
at each write.

During a pause, `post`, `stop`, `ring`, `budget`, `resume --task`, `reset` and a season write
as ever. The tick they play says `paused: nobody woken until team resume`. A season keeps
the pause.

The resume's tick does what is due at that moment. Each member due is woken in its own run.
A ceremony's period of the day rings when its hour is past and it never rang; a period that
passed during the pause never rings.

`status` says `paused since …`; its face says `state: paused` and `paused {by, at}`. The
relaunch entry stays.

#### `team budget`

`team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]` RAISES the
team's `budget` or `budget-launches`, without a start. It is judged under the journal's
lock:

| refusal | when |
|---|---|
| `team-not-started` | the team was never started |
| `budget-invalid` | the new bound is at or below what the team spent since its start |

It writes `budget-raised {budget, launches, by}`. The replay takes the new bounds and lifts
`budget-spent`. The members keep their runs, and the next tick wakes the members due in
them.

#### `team reset`

`team reset <name> [--member <m>]` makes the team forget a member's run. The agent's console
plays `-reset <key>`, and `run-reset {member, run}` is written. It is judged first under
`tick.lock` and refuses `team-busy` or `member-running`. The member's next wake-up opens a
new run ([One run per member](#one-run-per-member)).

### The tick

`./pp team tick <name>` ADVANCES the team. It is one short process.

#### The tick's lock

The tick runs under `tick.lock`, beside the journal, taken without waiting. When the lock is
held, the tick posts the mark `tick.pending` and leaves. The holder clears the mark, plays,
releases the lock, then reads the mark and plays again when it is set.

#### What one tick does

1. It reaps the wake-ups that ended.
2. It routes the ACTS the members said ([Acts, debts and waits](#acts-debts-and-waits)).
3. Before it wakes anyone, it breaks a deadlock ([Deadlocks and relances](#deadlocks-and-relances)).
4. It judges the waits.
5. It launches the next wake-ups.

The end of every wake-up ticks by `--on-end`. The schedule's net catches a tick that never
came ([The schedule and its net](#the-schedule-and-its-net)).

#### Reaping

The tick finds a launch by its `wake-launched` event, or by its tag at `messages.jsonl`; it
finds the response by (run, index). The reap judges the wake lock first, then reads the flow,
since a launch that is over wrote its end before it gave the lock back. So a launch that
ended is never taken for dead, and a kept answer is never killed.

A wake lock free without a response is a dead wake-up: it gets one retry, then it is
`final`. The tick then answers, in the member's place, every message of that wake-up that
owes an answer -- never a principal's opening.

For the root, the team's `notice` goes instead to a PERSON who has a box: the member that
delegated the task, else the task's principal; the owner when the team itself wrote the
task, as for a ceremony's task.

#### Reading a launch's flow

A wake-up is ONE launch (`agent start --launches 1`). The tick reads the launch's flow from
the exchange the launch OPENED. That exchange is found by the tag the house writes at its
`opened` (`agent start --tag`), looked for from the rank the journal last kept of the run.

The acts are read in that flow three ways: by `agent flow --from --follow` while the launch
plays, by the launch's FOLLOWER `team follow`, and again by the reap after it. Each act is
routed once, by its rank: `wake-routed`.

The launch's end is read at the flow too: `wake-ended {run, launch, state, cost, context}`.
Its `state` is what the house said of the run at `--on-end`: `standing` or `parked`. A
`standing` run is relaunched as soon as its wake lock is free, with `[nothing new]` at its
head when nothing is due. Its `context` is the last measure of the member's context that the
flow of the launch said, `{tokens, used, window}` as the house said it, or `null` when the
launch measured nothing. So the member's context can be read when it is at rest.

#### Launching a wake-up

The tick launches by the house's [console](../../docs/reference/console.md), in three
writes:

1. `wake-intent`, written FIRST;
2. `agent start --tag --on-end "<engine> --instance <house> team tick <name>"`, with
   `--run` to resume the agent's run on that task and the flags `team start` was given.
   `--harness` and `--provider` go together, the provider naming the grammar in which
   `pp-agent` reads the command's output;
3. `wake-launched`.

See the [`agent`](../agent/README.md) package for `agent start`.

#### The message of a wake-up

The message opens on the head line `[team <name> · you are <member>]`
([Names and paths](#names-and-paths)). Then come:

- the agent's inbox: each message as its head line, such as
  `#163 DO from supervisor on T8 -- you owe an answer`, with its text indented under it;
- the messages it still owes from earlier wake-ups;
- the contract: the three forms and the debt.

The team's intention is served by pp, never in the message.

What the others answered reaches a woken agent as ONE line. The head of its message names
each response other agents gave since its last wake-up in the team, by agent, task and
journal id. The cursor is its last `wake-intent` -- the journal's own cursor, nothing written.
The line gives the house console's absolute path and `team responses <name> --since <id>`.

While a member is suspected, every other wake-up's head says so after its first line:
`[not answering at the moment: <member> -- tried again at HH:MM:SS]`.

### Acts, debts and waits

#### What an act is

A member's ACT is a production of the engine's FORMAT mechanism (see
[The form of a said production](../../docs/reference/block.md#the-form-of-a-said-production)).
The format is `team-act`, declared once by the team package in `procs/TEAM-ACT.md`, mode
`response`: the value alone, no head.

An entry's step names the format (`INFER team-act => words`). The contract of the standing
orders, `system/SYSTEM.COMMON.md` of the package, describes it. The engine prescribes the
form and judges nothing of it.

There is no law: a message is a `words`. Every JSON object of a `words` that carries the key of a
form (`do`, `ask`, `re`) -- said alone as the contract asks, or found among other text -- is an
act, routed in its order. An act whose form is broken (cut short, a key its form does not carry,
a value of the wrong kind) is refused and the member is told why, as for an act whose sense is
wrong. A `words` without an act is SAID: it is routed to nobody and fails nothing.

| act | where it goes |
|---|---|
| `{"do": …}` | along the `reports:` edges: one `do` post per delegate, plus the `wait` of its `await` |
| `{"ask": …}` | to any member, or to a principal |
| `{"re": <id>, "text"}` | the answer to the message `#<id>` delivered to the member; it goes to that message's author |
| `{"info": {"to": …, "text"}}` | a piece of information to any member or principal (team 0.47.0): it opens no debt and holds no wait; a member's info launches nobody and rides the head of its recipient's next launch, a principal's wakes; to a principal it reaches their inbox at once |

#### Refused acts

An act whose sense is wrong is REFUSED at the routing: the tick writes `wake-refused` and
sends an `info` to the member, and the launch goes on. An act is refused when it names a
member nobody declared, when it is a `do` off the edges, or when it is a `re` citing a
message never delivered or citing an `info`.

#### Debts

Each `do` and `ask` delivered to a member opens ONE debt. The first answer that cites it
settles it; a later answer is posted as `info`.

The ROOT's answer to its task's opening:

- writes `done` with its text;
- settles every debt of the task;
- writes a `returned` for every post left undelivered on the task;
- writes `schedule-off`.

The root speaks to its principal by its own elements alone: `ask`, and the `re` to the
opening that closes the task.

#### Waits

A delegating member waits for its delegates. `wait-met` is written when every delegate has
answered its `do`. Every message except an answer to the round's `do`s and to the task's
opening passes an open wait.

The wait is the agent's to shorten. An answer that delegates may carry
`"await": {"any": n}`: the tick then relaunches the agent once n of that act's delegates
have answered, instead of all of them (`wait` at the journal). An `await` without a number
is refused at the routing.

### Deadlocks and relances

Before it wakes anyone, the tick breaks a DEADLOCK. It builds the wait-for graph of the open
tasks: a member waits for the members whose answer it awaits, and for a principal whose
reply to its question it awaits.

The greatest set of idle members -- no wake-up under way, nothing to receive -- whose every
wait stays inside the set is deadlocked (Chandy, Misra, Haas, 1983).

A member at the bottom of that set (waiting for nobody, or in a knot) that owes an answer is
RELANCED: it gets a wake-up with no new message, and its intent carries
`relance: "owed" | "cycle"`. No count bounds the relances (team 0.48.0): what bounds a long task
is `launches:`, `budget:` and `budget-launches:`. A member whose run STANDS on the task is
not relanced but CONTINUED (team 0.54.1): its run is relaunched with `[nothing new]` at its
head and its debts under `[you still owe an answer to]`; the relance plays only where that
continuation launched nothing -- its wait on the task holds.

What the tick watches is the member's SILENCE: its exchanges that end without one act (a `re`, a
`do`, an `ask`, an `info`) while it owes. At `silence:` such exchanges (3 unless `TEAM.md` says;
`team start --silence <n>`, `--member <m> --silence <n>`) the relance is a REMINDER
(`relance: "reminder"`), its head asking an answer or an `info`; one more silent exchange and the
member is SUSPECTED, as a failing member is ([Members that fail](#members-that-fail)): the tick
answers in its place to the members waiting for it, and a root's principal gets the team's
`notice` about it. A member that acts at every exchange is never reminded.

### Members that fail

The tick is a failure detector (Eventually Perfect, Chandra and Toueg, 1996), read from the
journal alone.

#### Suspicion

A member whose final failure stands -- on a task not stopped, with a reason other than
`budget-share` -- is SUSPECTED for an interval counted from the hour of that failure.

The interval's base is the step of the team's net in seconds (`schedule:`), 5 minutes
without it or under `off`. It doubles at each final failure in a row and never goes past
`suspect-max:` (10 minutes without it).

During the interval:

- no member wakes the suspected member;
- each tick answers in its place every debt it owes to a member, and every `do` or `ask` of
  a member that reaches it (`re`, `by: tick`, `suspected: true`, « no answer: <member> is not
  answering at the moment; it is tried again at HH:MM:SS »);
- what a PRINCIPAL says to it -- a task, an `info`, a `re` -- launches it at that very tick, and
  that launch is its try.

#### The try

Past the interval, the member's next message is its TRY. A member that owes only a
principal's opening is tried by a relance on it (`relance: "tried"`).

A try that fails is final at once and doubles the interval. A try that answers ends the
suspicion, and the member is tolerated one silent retry more (`retries:` + 1 per
repentance).

Nobody is excluded for good. `team resume --task` ends the suspicion of the task's members;
a season ends every suspicion.

#### Launches the house refused

A launch the HOUSE refused before any harness ran -- `agent start` ended without its report
-- is no failure of the member. The tick writes `wake-failed {house: true}`: never final, no
retry spent, no fall.

The member's messages go back to its inbox, and the next tick launches it again. The team
sends the owner one notice per (member, cause).

### Notices of the team

The tick says nothing to a principal in a member's name. Every post of the tick to a
principal is a NOTICE of the team (`{verb: notice, from: <team>}`):

- a guard was reached;
- or the notice is `about` a root that failed for good or is suspected -- by its falls, or by
  its silence (`cause: silence`).

A notice opens no debt. A notice about the root holds its wait on the principal
until the principal's answer cites it.

### Limits

The declaration may bound the tick.

| key | what it bounds | when it is reached |
|---|---|---|
| `parallel` | the wake-ups under way at most | an agent due beyond it is `deferred` and launched by a later tick |
| `budget` | the dollars the team may spend since its start: the sum of the costs its wake-ups reported | nothing is launched, `budget-spent` is written once and the owner gets the team's `notice` |
| `retries` | the wake-ups played again after a dead one, 1 unless said | the wake-up is `final` |
| `timeout:` | the seconds a wake lock may stay held after its launch (the journal's UTC `at` against the real clock) | the wake-up is ended by the kill gesture and FAILS: `wake-failed wake-timeout`, retried under `retries` |
| `launches:` | the launches of one task, retries included | `launches-spent` is written once, the owner gets the team's `notice`, the task is left open |
| `budget-launches:` | the team's total launches, counted from the last `team-started` | `budget-spent {unit: launches}` is written once |

A timeout is never written `wake-killed`: that event stays the owner's `stop --kill`.
`budget-launches:` is the bound that holds when the provider reports no cost.

Every launch that ended counts in the team's cost. `launches:` and `budget-launches:` count
the launches; a `launch-missing` spends no retry.

`team status` says the limits, the cost, each agent's runs and their state, the delegates it
waits for and the owner's inbox.

#### Each wake-up's share of the money

`pp-agent` caps a RUN, and a member's run lives through the team's whole work. So where the
adapter of the launch's grammar declares a cost scope (`COST`), the intent carries an
`allowance`: the wake-up's PART of what the team has left.

    allowance = min((budget - cost kept) / k,  budget - cost kept - allowances of the wake-ups under way)

Here k is the number of wake-ups that may play together, min(`parallel`, the members), so
that k members due together launch together. The allowance is reserved until the wake-up
ends.

`agent start --max-budget-usd` is the member's run cap: what the run spent plus the
allowance. A member due whose rest is all reserved is `deferred {reserved}`.

No cap per wake-up exists. `team start --max-budget-usd` refuses `flag-retired`. Without
`budget:`, no cap goes to `agent start`.

A wake-up that its run cap stopped between two launches -- its response's `error` is
`budget-spent` -- fails `budget-share {share, spent}`, read before its body. It is retried in
its run under `retries:` with a new share; its final notice says the share and the team's
rest.

`status` says `budget <spent>/<cap> USD · reserved <r> · left <l>`; `status --json` says
`budget {cap, spent, reserved, left}`.

### The schedule and its net

The team keeps its own NET: a timer, at every step. Its step is `schedule:` of `TEAM.md`,
read in seconds and kept at `team-started.schedule` with `unit: s`.

| `schedule:` | meaning |
|---|---|
| `5s`, `90s` | a step in seconds |
| `2m`, or a bare number of minutes | a step in minutes |
| `1h` | a step in hours |
| absent | 5 minutes |
| `off` | no net, ever |
| anything else | `team-invalid` |

#### The timer

A tick that ends leaving a deadline arms one detached process, `team timer <name>`. It
sleeps until the earliest deadline, at most one step away, plays one tick and dies. A
deadline is any of:

- a launch under way (its `timeout:` when one is declared);
- a suspected member with something to deliver;
- a member due but deferred;
- a standing run;
- the next ring of a ceremony.

There is one timer per team (`tick.timer` beside the journal), none when nothing is due, and
it is gone at `schedule-off`. The tick hands each timer a token and writes it in that mark:
the timer knows itself by it, on every system. The journal gets `timer-armed {due}` when a tick arms one where
none stood. A team at rest costs nothing: no tick plays while nothing is due.

#### The relaunch entry

The timer is a process: it dies when the machine stops or the user's session ends. So that
the teams come back on their own, the house keeps ONE relaunch entry for all of them. The
entry plays `team tick --all` once when the user opens a session: one tick for every team
that needs its net, and each tick arms its team's timer again.

| system | the entry | rights |
|---|---|---|
| Windows | the value `pp-team-<12 hex of the house>` of the user's Run key, `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`; its command runs `team tick --all` through `uvw` (uv's launcher without a window) when it is installed, through `<house>\pp.cmd` otherwise | the user's own key: no administrator rights, no elevation |
| Linux, WSL | the line `@reboot <python> <engine> --instance <house> team tick --all # pp-team <house>` in the user's crontab, found again by its mark | `cron` must run (under WSL: `sudo service cron start`); `@reboot` plays when cron starts |

A team needs its net while its `schedule:` is not `off` and a task is open or a ceremony is
declared. `team start` lays the entry when its team needs it and it is absent, and a `post`
that finds it gone lays it again. The tick, `team stop` and `team delete` remove it only when
NO team of the house needs it any more. The entry is laid, and the need judged and the entry
removed, under the house's relaunch lock (`state/relaunch.lock`): the stop of one team and
the start of another at the same moment never take the net of the team that needs it. The
journal gains no event for the entry: the system is the one truth of it.

An earlier version laid one entry per team. On Linux the house's first lay replaces those
lines. On Windows, a task an administrator account laid under team 0.44 is removed by hand:
`schtasks /Delete /TN pp-team\<12 hex>\<name> /F`.

#### When the system refuses the entry

A system may refuse the entry: a company policy that locks the Run key, `cron` not
installed, a crontab that cannot be written. The team starts anyway and runs on its timer;
only the relaunch after a restart is missing. The refusal is said three ways:

- on stderr: `relaunch not laid -- <why>`, rc 0;
- once per season, a `notice` of the team to the owner, in the inbox: what is missing and
  what to do to have it;
- at the face: `relaunch: false` and its `reason`.

`status` says `schedule · every 300 s · timer armed | no timer · relaunch laid | absent (<why>)`,
or `schedule · off`; the face says `schedule {seconds, timer, relaunch, reason}`.

Under `PP_CRONTAB=<file>` and `PP_RUNKEY=<file>`, those files stand for the crontab and the
Run key (the bench, a try); `PP_SCHEDULER=nt|posix` chooses which one the skill writes.

### Ceremonies

The tick RINGS the ceremonies.

#### When a ceremony rings

`start` judges the when of each ceremony line whole; anything else than these two forms is
`team-invalid`:

- `every day|weekday|mon..sun HH:MM with a b -> c`
- `after <other> with a b -> c`

A ceremony is due when its period is due and it has not rung yet in it. Under `every`, the
day conforms and the hour is past, by the house's local clock (`PP_NOW` stands for that
clock at the bench). Under `after`, the followed ceremony's task is resolved.

`ceremony-due` names the period: a ceremony rings once per period, and the journal is the
judge.

#### The ceremony task

A due ceremony becomes ONE ceremony task, from the team to its facilitator: its opening
`do` to the facilitator, and a `do` per participant. The wait gathers the answers, and the
opening waits with them. The facilitator concludes; its answer to the opening is the
result.

A ring names its task `<ceremony> YYYY-MM-DD HH:MM` (its local hour). It says a CONSIGNE,
never the ceremony's declaration line: the facilitator gathers the answers and concludes;
each participant takes part as the team's intention says and answers the facilitator.

#### Ringing at hand

`team ring <name> <ceremony> [--as <principal>] [--no-tick]` rings a declared ceremony at
hand, out of its hour. It is the tick's own ring -- `ceremony-due {ceremony, period, by}`,
ONE task to the facilitator, its opening `do` to the facilitator and a `do` per participant
-- under the period `manual-<id>`, the id of its own `ceremony-due`. So an `every` ceremony
still rings its date at its hour.

| refusal | when |
|---|---|
| `ceremony-unknown` | no such ceremony is declared |
| `ceremony-open` | a task of the ceremony is open |

#### Quorum

A ceremony line may end on `any <n>`, its QUORUM, with n from 1 to its participants
(`team-invalid` at `start` otherwise). Every ring of it writes
`wait {facilitator, any: n, to: the participants}` after its delegations. The facilitator
is woken at the n-th answer to its participants' `do`s.

### Recurring tasks

`team post <name> --message <text> [--to <member>] [--name <text>] [--as <principal>]
--every "<when>"` lays a RECURRENCE: the same task, given again at a set time. `<when>` is
read as a ceremony's: `day`, `weekday` or `mon` to `sun`, then the local hour `HH:MM`. The
post writes `recurrence {recurrence: R<n>, from, to, text, name, when, since}` and opens
nothing.

At each tick, a recurrence whose day has come and whose hour has passed opens ONE task for
that day: an OCCURRENCE. The occurrence is a task like one `post` opens -- its `do` to the
member (the root without `--to`), its answer, its stop -- and carries `recurrence` and
`period` (the local date). It is named `<name> YYYY-MM-DD HH:MM`, the recurrence's id when
no name was given.

- The first occurrence comes at the first period after the post: posted at 10:00, a
  `09:30` recurrence starts the next day.
- While the occurrence before is still open, the period opens nothing and writes
  `recurrence-skipped {recurrence, period, open}`: a member never holds the same work twice.
- Under a pause nothing opens; a period that passed during the pause never opens.
- A season keeps the recurrences; `team delete` removes them with the journal.

A live recurrence keeps the team's net: no `schedule-off`, the relaunch entry stays, and the
timer sleeps until its next period at most. `team stop <name> --recurrence R<n>` writes
`recurrence-stopped {recurrence, by}`.

`team recurrence <name> R<n> --every "<when>"` writes `recurrence-changed {recurrence, when,
since, by}`, `since` the local hour of the change. From then on the tick reads the new `when`
and the new `since`; the periods already handled stay handled. A period is the local DATE: it
opens once, whatever hour is in force when it comes. Changed at 10:00 from `09:30` to
`14:00`, a recurrence that opened its task at 09:30 opens nothing more that day, and opens the
next one at 14:00. Changed to an hour already past that day, it opens nothing that day.

### Entries and the team's directory

`entries:` of `TEAM.md` (`<trigger> -> <document>`, the trigger being `do` or a ceremony's
name) names the document a wake-up on that trigger plays. That document is a SUCCESSOR of
the agent's procedure, elected at EVERY exchange, opening or resume.

Everything of a team lives in ITS directory, `teams/<team>/`, and nothing in an agent's
instance. Every wake-up gets `agent start --documents teams/<team>`, the root of documents
of the run it opens.

A plan the members share lives there too: `pp-plan section <slug> Context --shared` births it under
`teams/<team>/plans/`, and every member's run reads and writes it with the plan package's own verbs
(its README says how). `TEAM.md` has nothing to declare for it.

`team start` writes there, beside `TEAM.md` and the entries' documents the owner writes:

- the head of `TEAM-<team>.md`, always. It is attached at the kit's `turn.begin`; its BODY
  is the owner's intention; `next:` lists every entry of the team, then the neutral
  `TEAM-IDLE.md`; it says `decide: pp-team entry <team>`.
- the neutral `TEAM-IDLE.md`.

The law `TURN.md` that an earlier version laid there is removed at the start: there is no
law, a message is a `words`.

`pp-team entry <team>` prints the entry of the team's wake-up under way on a run -- the run
given by `--run`, else `PP_RUN` -- and the neutral otherwise. It finds the house as the
machine the skill lives in.

The pilot, never the model, picks the procedure. No wake-up carries a door: `--door` and
`PP_DOOR` stay for `agent run`.

#### Teams laid before team 0.15.0

What a version before 0.15.0 laid at an agent is removed by the next start; a file that
differs is kept and said. A team standing across that upgrade is stopped, then started
again: its members' runs carry no root of documents (`documents-fixed`).

### One run per member

A member holds ONE run: one key and one session of its harness for the team's whole work.
That run is the one that first answered, readable or not (a `response-unreadable` keeps its
run for the retry). Every task of the member arrives in it by `--run`.

A member plays ONE wake-up at a time, on the first due task in the tasks' order; its other
tasks wait for its next wake-up in the same run. Its wait, its `await` and last delegation
included, stays by (member, task). The members play in parallel, `parallel:` bounding the
team.

The sharing line counts from the RUN's last wake-up, or from the team's start for a new run.

A house's `upgrade` keeps the key. It leaves the renewal mark at the slot's path; the next
wake-up resumes `--run <the same key>`, and the engine reopens the run under it.

A run whose slot `-reset` took, or that `team reset` forgot, gives way to a NEW run. The new
run's message opens on the history of every open task of the member, then its inbox; the
intention is served in its output.

A kept run whose wake lock is still held is busy, and never resumed.

`work:` gives a member's opening `agent start --work <repo>`: one clone per member, kept
with its run. `status` says each member's run, its state and its tasks.

### Task names

A task may carry a NAME, free text given by `--name <text>` at `team start` and at a
`team post` that opens a task. It is one line of 1 to 80 printable characters a user types,
its edges trimmed; anything else refuses `name-invalid`.

The name is kept as `name` on the `task` event. `status` says it (`T2 Prix de la DDR4 · open`),
and so do `status --json`, `log --json` and `watch --json`. A ceremony's ring names its task
itself ([The ceremony task](#the-ceremony-task)).

### Templates

A team may be born from a TEMPLATE. `team templates [--json]` lists the nine of them:

| template | its form |
|---|---|
| `supervisor-workers` | the root splits each task, one part per worker |
| `lead-reviewers` | the root does the work, each reviewer checks its draft; one reviewer is the pair |
| `chain` | each member hands the next step to the next one and passes the result back up |
| `solo` | one member |
| `empty` | one member, the smallest declaration |
| `council` | the root asks every expert the same question in one `do` and concludes at `await {any: n - 1}` |
| `triage` | the root hands each task whole to ONE specialist |
| `cross-check` | the root gives the same task to each twin and compares |
| `tree` | the root over `--squads <n>` squad leads (two unless said), each over the workers given to it in turn; the daily of the squad leads |

Their text lives in `packages/team/templates/<t>.md`; their FORM lives in the script.

#### `team new`

```
team new <name> --template <t> [--member <name> <path>]... [--root <member>] [--principal <p>]...
    [--budget <usd>] [--launches <n>] [--timeout <s>] [--schedule <step>|off] [--no-ceremony]
    [--intention-file <path>] [--squads <n>]
```

`team new` writes `teams/<name>/TEAM.md`:

- `--member` replaces the default members (`agents/<name>/<member>`);
- the form makes the root, the edges, the daily (when two members or more report to the
  root) and the names of the intention out of them;
- the limits are `budget: 5`, `launches: 24`, `timeout: 900` and `schedule: off` unless
  given.

The text is judged by `start`'s own judge (`judged`, with `declared` its reading of the
file) before any write. It is then linked in place, only where no `TEAM.md` stands. `new`
starts nothing.

| refusal | when |
|---|---|
| `team-exists` | a `TEAM.md` already stands |
| `template-unknown` | no such template |
| `team-invalid`, `participant-unknown`, `root-missing` | the text fails `start`'s judge |

A refusal leaves nothing behind.

### Reading a declaration

`team declaration <name> [--json]` READS a declaration. It says:

- `TEAM.md` whole;
- the verdict of `start`'s own judge: `ok`, or the refusal `start` would write, said with
  rc 0 (the judge DECLINES; `start` and `new` refuse with its words);
- its gap to the last start: `{key, started, declared}` for each front-matter key kept by
  `team-started` that the file now says otherwise.

The body is never pending: pp serves it at once. Nothing is written, there is no lock and no
tick.

#### `declared` under `--json`

The `--json` object says `declared`: the front matter as that judge reads it. That is the
members and their paths in order, the root, the edges, the principals, the limits of
`TEAM.md` alone, the schedule and the ceremonies' lines -- what the next start writes. It is
`null` under a refused verdict.

Each member there says `born` (an instance stands at its path) and `packages [{name, on}]`:
what a season that names no package gives it, born or not -- the packages the team requires
on, every other package the house pins beyond its base off. The member's SETTINGS plays no
part.

So a post knows what a season gives before it names a package.

### Following a team

A team is FOLLOWED without being moved.

| command | what it does |
|---|---|
| `./pp team status [<name>]` | reads the tasks, each agent's inbox and the last event; without a name, one line per team declared |
| `./pp team watch <name> [--task] [--json] [--heartbeat <s>] [--for <s>] [--until-done]` | writes on stderr every journal event as it arrives, every step of every wake-up under way and what its harness does between two steps (a tool called, its result, a thought, the words, the context); says `no event for <n>s` after the heartbeat |
| `./pp team log <name> [--task] [--last <n>]` | prints the journal, one line per event |
| `./pp team result <name> [<task>]` | prints a resolved task's result as JSON; refuses `task-open` or `result-missing` |
| `./pp team responses <name> [--since] [--agent] [--task] [--last]` | prints the members' responses, with their texts read at `responses.jsonl` |
| `./pp team inbox <name> --seen` | marks what waits for the owner as seen |

`watch` reads the agents' traces by the engine's reader and never writes them. It takes no
lock, writes nothing and never ticks.

For every wake-up it follows, `watch` also reads the run's flow (`agent flow --follow`, the
same reader as the follower's) and says the ACTIVITY of the harness between two steps, one
object `event: activity` per event under `--json` -- `{at, agent, run, event: activity, kind,
task, tag, launch, …}`, `kind` one of:

| kind | what the object carries |
|---|---|
| `tool` | `name`, `title` (its input on one line), `pp` (true for a call of the agent's console) |
| `tool-result` | `error`, `size` (the characters of the result) -- never its content |
| `thinking` | `text`, or `tokens` when the harness counts them alone |
| `words` | `text` |
| `context` | `tokens`, `used` (the part of the model's window), `window` |

Every text is cut at 80 characters (`ACTIVITY_TEXT`). The relay is bounded: at most 4
objects a second per wake-up (`ACTIVITY_RATE`); past that, the latest one is said once the
second turned, with `more` counting the objects it stands for; a `context` is always said.
Without `--json`, one line each: `[HH:MM:SS] <member> · <run> · tool Read · pp.py`,
`result ✓ 10.0 kB`, `thinking <text>`, `words <text>`, `context 34000 tokens`.

#### What waits for the owner

What waits for the owner reaches their own exchange. The package mounts `TEAM_INBOX.md` at
the kit's `turn.begin`, which plays `pp-team inbox`. It serves, under
`INFORMATION — team-inbox`, one line per team where, since the owner last said
`./pp team inbox <name> --seen`:

- a question (an agent's `ask`), or a notice of the team about a member, awaits its answer;
- a task was resolved;
- a notice of a guard came, or a post was returned.

`--seen` writes `inbox-seen` at the journal, the one event these readers write. When nothing
waits, there is no section.

The document says what that line renders and teaches no call. The gestures it sends the
agent to -- `inbox --seen`, `post --reply`, `result` -- live in `pp-team`'s `SKILL.md`.

### The faces

The fields below are what a program reads; the [`ui`](../ui/README.md) package reads them.

#### `team status --json`

`team status [<name>] --json` is the face a program reads, the post of `ui` first; the text's
bytes stay unchanged. With a name it prints ONE JSON object on one line; without a name, one
object per team declared. A team never started is
`{team, started: null, state: "never", waiting_on: []}`.

| field | what it says |
|---|---|
| the team's tasks | their text; their last event as `log --task` keeps them; holders, delegations, waits; their `cost`; `dos [{id, from, to, answered}]`; `waits` (`answered` of `of`); the `relance` of a wake-up under way; `running` (the wake-ups under way on the task) |
| its members | run, state, `context` (what its last wake-up left, `null` before its first one), the posts not delivered yet, the other members' answers since its run's last wake-up, the `packages` their run plays (read as `agent status` reads them); `owes`; `health {suspected, falls, tried_at, repents}` |
| its ceremonies | `next_due`, the local `YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring; `due`, the next tick rings it; the last ring and who answered it |
| its recurrences | `recurrences [{id, name, text, from, to, when, since, next_due, due, stopped, last}]`: `next_due` its next period, `null` once stopped; `due`, the next tick opens it; `last {period, task, state}` its last occurrence. Each task says its `recurrence`, `null` for a task no recurrence opened |
| the owner's box | what waits for the owner |
| `required` | the packages a member may not switch off: `team` and what it requires, the list `package-required` names. Every object says it, a team never started included. |
| `state` | derived from the replay, never written: `working` while a wake-up plays, `idle` when no task is open, else `waiting`; `paused` under a pause |
| `waiting_on` | every guard that holds, in the order the tick judges them: `members`, `launches`, `budget`, then `owner`, `suspected`, `due`. A suspected member gives `suspected` instead of `blocked`. |
| `season {n, at, budget, budget-launches}` | the starts, counted by the replay, and the season's own budget |
| `launch` | what the next wake-up gets, never `max_budget_usd`, with its `packages`; each member's is the same, its profile applied |
| `budget {cap, spent, reserved, left}` | the money ([Each wake-up's share of the money](#each-wake-ups-share-of-the-money)) |
| `schedule {seconds, timer, relaunch, reason}` | the net: its step, whether a timer is armed, whether the relaunch entry stands and why the system refused it |
| `paused {by, at}` | who paused the team, and when |

Both forms, with and without a name, say the team's `state`. Without a name, a team's line
counts `asks` (the agents' questions), `notices` (the team's) and `done` (the tasks resolved
and not seen), as `team inbox` does.

#### The other faces

| command | what it prints |
|---|---|
| `team log <name> --json` | one object per event, the object `watch --json` writes (`{at, team, event, id, …}`): a reader takes the history there and the live flow at `watch` |
| `team responses <name> --json` | one object per response, its whole text or `null` |
| `team inbox [<name>] --json` | one object per team where something waits for the owner, the questions and the returned posts with their texts |

`inbox` tells `questions` from `notices`, and says `awaits` while a notice about a member
holds it.

### Routes and answers

The routes and the answers hold:

- a `do` goes to an agent that reports to the answering one; on a ceremony task, its
  participants report to its facilitator;
- an `ask` goes to ANY member of the team, or to a principal;
- a `reply` goes only where an `ask` from its target to the answering member stands on the
  task;
- a `do` off the edges, an `ask` to a name nobody declared and a `re` citing a message never
  delivered are refused at the routing (`wake-refused`, an info to the member);
- a post to a principal -- the owner, a mandator, the team -- is delivered at its writing and
  never `returned`.

### Names and paths

A team speaks NAMES and addresses its agents by PATHS.

These say the member's name:

- the journal, whose `agent` field is the member's name;
- the inbox;
- `status` (`r1 · agents/reviewer · inbox 0`);
- the head of every wake-up, `[team <name> · you are <member>]`, after the lines
  `agent start` sets at the head of a prompt (the material's and the neighbours').

Every birth, `agent start`, wake lock and record of the house is addressed by the member's
path, read at `team-started.agents` (`{member: path}`) or at the intent's `path`.

A line of `agents:` written before reads the same way: `m manager` is the member `m` played
by the agent at `manager`.

## See also

- [`agent`](../agent/README.md) -- the house and `agent start`, which every wake-up uses.
- [`ui`](../ui/README.md) -- the post that reads the team's faces.
- [The operator's console](../../docs/reference/console.md) -- the console the tick launches by.
- [Channels and the delivery](../../docs/reference/block.md#channels-and-the-delivery) -- the said productions an act is one of.
