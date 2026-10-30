# team

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.43.0`

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
| `./pp team post <name> --message "…"` | adds a task, a note, a reply or a stop at any time; `--name` names a task |
| `./pp team stop <name>` | stops the open tasks; `--kill` also ends the wake-ups under way |
| `./pp team pause <name>`, `./pp team resume <name>` | holds the team: nobody is woken until it resumes |
| `./pp team resume <name> --task <id>` | takes back a task a limit had stopped |
| `./pp team reset <name> --member <member>` | gives a member a new run at its next wake-up |

### The tick moves the team

`./pp team tick <name>` advances the team once: it collects the wake-ups that ended,
routes each act a member said to the member it is for, judges who waits for whom and
launches the next wake-ups. The end of every wake-up triggers the next tick, and the
NET catches a tick that died: `schedule:` of `TEAM.md` says its step -- `5s` or `30s`
under a minute, `2m` or a bare number of minutes at the minute and above, 5 minutes
unless said, `off` for none. At the minute and above the net is one line of the
system's calendar (cron); under the minute it is a timer the tick arms at its end when
something is due -- a process that sleeps until the deadline, ticks once and dies, one
per team, none when nothing is due. On Windows the skill writes no calendar line: a
Task Scheduler entry (`schtasks`) that runs the tick every few minutes does the same job.

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
reminds the member at the bottom of the chain that it still owes an answer. After two
reminders without an answer, the tick answers in its place (« no answer »), so that the member
waiting for it goes on; it never answers in your place: a task you opened that its member does
not close comes back to you: the team sends you a notice.

A member that keeps failing -- a model that errs, a program that crashes -- may be broken, or only
down for a while. The tick does not wait for it, and does not give it up either. Once a wake-up
of the member has failed for good, the member is suspected for a while: 5 minutes, or the
step of the team's schedule, doubled each time it fails again and never past `suspect-max:`
(10 minutes unless said). During that time no member wakes it: whatever a member asks of it
gets an answer from the tick in its place (« r2 is not answering at the moment; it is tried
again at 14:20:05 »). What YOU say to it -- a task, a note, an answer -- reaches it at once: the
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

On Linux the tick's safety net uses the user's crontab; under WSL, `cron` must be
running (`sudo service cron start`).

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

`team delete <name> [--yes] [--json]` removes a team and what it made:

- its timer;
- its calendar line;
- every run its wake-ups opened (`agent purge`, once `deleting` lets the guard go);
- its journal;
- `teams/<name>/`.

The agents are left standing. While a task is open, the command refuses `team-busy`.

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
    [--budget-launches <n>]
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
| `member-held` | `TEAM.md` drops a member that holds an open task |
| `team-document-missing` | `teams/<name>/TEAM-<name>.md` is missing |
| `born-busy` | the birth lock of a path is held past `call_lock_wait` |

#### The season's own settings

The season's `--budget` and `--budget-launches` stand above those of `TEAM.md` until the
next season. They are kept at `team-started.season`; `TEAM.md` is left untouched.

The flags after a `--member`, up to the next one, are that member's profile, kept at
`team-started.profiles`. They replace the team's provider, model, effort or permissions for
that member. Each `--package` goes to the member's `agent start`, in its run.

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
come, and the team is `idle`. The calendar line is laid at the start only when a task is
open or a ceremony is declared; otherwise the first post lays it.

### Posting, stopping, taking a task back

`start`, `post` and `stop` tick right after their write; `--no-tick` spares that tick.

#### `team post`

```
./pp team post <name> [--message …] [--to <agent>] [--task <id>] [--reply <id>] [--stop] [--as <principal>]
```

`team post` adds a new task, or a `note`, a `reply` or a `stop` on a standing one.
`post --reply <id>` writes the principal's answer, a `re`.

| refusal | when |
|---|---|
| `task-closed` | the task is stopped or resolved |
| `principal-unknown` | the name is neither the owner nor a mandator |

#### `team stop`

```
./pp team stop <name> [--task <id>] [--kill]
```

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

It writes `resumed {task, by, from}` and a `note` to each member it revives:

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
calendar line stays.

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

The launch's end is read at the flow too: `wake-ended {run, launch, state, cost}`. Its
`state` is what the house said of the run at `--on-end`: `standing` or `parked`. A
`standing` run is relaunched as soon as its wake lock is free, with `[nothing new]` at its
head when nothing is due.

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

There is no law: a message is a `words`. Every `words` of the launch that reads as a
`team-act` value -- one JSON element or a list, said alone -- is an act. A `words` of another
form is SAID: it is routed to nobody and fails nothing.

| act | where it goes |
|---|---|
| `{"do": …}` | along the `reports:` edges: one `do` post per delegate, plus the `wait` of its `await` |
| `{"ask": …}` | to any member, or to a principal |
| `{"re": <id>, "text"}` | the answer to the message `#<id>` delivered to the member; it goes to that message's author |

#### Refused acts

An act whose sense is wrong is REFUSED at the routing: the tick writes `wake-refused` and
sends a `note` to the member, and the launch goes on. An act is refused when it names a
member nobody declared, when it is a `do` off the edges, or when it is a `re` citing a
message never delivered.

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
`relance: "owed" | "cycle"`.

After two relances on a debt still owed, the tick answers it in the member's place (`re`,
`by: tick`, `preempted`). It never does so for a principal's opening: the team's `notice`
about the root goes to its principal instead.

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
- what a PRINCIPAL says to it -- a task, a note, a `re` -- launches it at that very tick, and
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
- or the notice is `about` a root that failed for good, was preempted on the principal's
  opening, or is suspected.

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

The team lays its own SCHEDULE. Its step is `schedule:` of `TEAM.md`, read in seconds and
kept at `team-started.schedule` with `unit: s`.

| `schedule:` | meaning |
|---|---|
| `5s`, `30s` | a step under the minute |
| `2m`, or a bare number of minutes | a step at the minute and above, whole minutes there |
| absent | 5 minutes |
| `off` | no net, ever |
| anything else | `team-invalid` |

#### At the minute and above: one calendar line

The net is ONE line of the user's crontab per team: a tick every step, with the
interpreter, the engine and the house by their absolute paths. The line is found again and
removed by its mark `# pp-team <house> <name>`. It is the NET that catches a dead tick, a
dead wake-up or a machine asleep.

`team start` lays the line, and a `post` that finds it gone with a task open lays it again.
The tick and `team stop` remove it when no task stays open and no ceremony is declared.

The journal gains no event for the line: the calendar is the one truth of its own line.
`status` reads it there (`schedule · every 5 min · laid | absent`, `schedule · off`).

#### Under the minute: a timer

Under the minute the net is a TIMER. A tick that ends leaving a deadline arms one detached
process, `team timer <name>`. It sleeps until the earliest deadline (at most one step away),
plays one tick and dies. A deadline is any of:

- a launch under way;
- a suspected member with something to deliver;
- a member due but deferred;
- a standing run;
- the next ring of a ceremony.

There is one timer per team (`tick.timer` beside the journal), none when nothing is due, and
it is gone at `schedule-off`. The journal gets `timer-armed {due}` when a tick arms one where
none stood. The face says `schedule {seconds, minutes, laid}`.

#### Who writes the calendar

The skill writes the calendar, on the owner's commands and in the tick alone, never the
engine. The table is read and rewritten whole under the house's calendar lock
(`state/crontab.lock`), so two verbs of two teams at once lose no line.

A table that cannot be written is said (`schedule not laid`, on stderr, rc 0), and the team
starts anyway: it advances by `--on-end`, without its net.

Under `PP_CRONTAB=<file>`, that file stands for the table (the bench, a try). On Windows the
skill writes nothing; the WSL and Task Scheduler ways are in
[The tick moves the team](#the-tick-moves-the-team) and [Installation](#installation).

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

### Entries and the team's directory

`entries:` of `TEAM.md` (`<trigger> -> <document>`, the trigger being `do` or a ceremony's
name) names the document a wake-up on that trigger plays. That document is a SUCCESSOR of
the agent's procedure, elected at EVERY exchange, opening or resume.

Everything of a team lives in ITS directory, `teams/<team>/`, and nothing in an agent's
instance. Every wake-up gets `agent start --documents teams/<team>`, the root of documents
of the run it opens.

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
    [--budget <usd>] [--launches <n>] [--timeout <s>] [--schedule <minutes>|off] [--no-ceremony]
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

Each member there says `born` (an instance stands at its path) and `packages [{name, on}]`,
the packages it plays:

- for an agent born: what its instance pins beyond its base, as the member's run plays them
  -- its SETTINGS and the switches of that run --, read on the engine's faces as
  `agent status --json` reads them;
- for an agent not born yet: what its birth gives, the house's pins beyond its base, each
  on.

So a post can choose a member's packages before its first season.

### Following a team

A team is FOLLOWED without being moved.

| command | what it does |
|---|---|
| `./pp team status [<name>]` | reads the tasks, each agent's inbox and the last event; without a name, one line per team declared |
| `./pp team watch <name> [--task] [--json] [--heartbeat <s>] [--for <s>] [--until-done]` | writes on stderr every journal event as it arrives and every step of every wake-up under way; says `no event for <n>s` after the heartbeat |
| `./pp team log <name> [--task] [--last <n>]` | prints the journal, one line per event |
| `./pp team result <name> [<task>]` | prints a resolved task's result as JSON; refuses `task-open` or `result-missing` |
| `./pp team responses <name> [--since] [--agent] [--task] [--last]` | prints the members' responses, with their texts read at `responses.jsonl` |
| `./pp team inbox <name> --seen` | marks what waits for the owner as seen |

`watch` reads the agents' traces by the engine's reader and never writes them. It takes no
lock, writes nothing and never ticks.

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
| its members | run, state, the posts not delivered yet, the other members' answers since its run's last wake-up, the `packages` their run plays (read as `agent status` reads them); `owes`; `health {suspected, falls, tried_at, repents}` |
| its ceremonies | `next_due`, the local `YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring; `due`, the next tick rings it; the last ring and who answered it |
| the owner's box | what waits for the owner |
| `required` | the packages a member may not switch off: `team` and what it requires, the list `package-required` names. Every object says it, a team never started included. |
| `state` | derived from the replay, never written: `working` while a wake-up plays, `idle` when no task is open, else `waiting`; `paused` under a pause |
| `waiting_on` | every guard that holds, in the order the tick judges them: `members`, `launches`, `budget`, then `owner`, `suspected`, `due`. A suspected member gives `suspected` instead of `blocked`. |
| `season {n, at, budget, budget-launches}` | the starts, counted by the replay, and the season's own budget |
| `launch` | what the next wake-up gets, never `max_budget_usd`, with its `packages`; each member's is the same, its profile applied |
| `budget {cap, spent, reserved, left}` | the money ([Each wake-up's share of the money](#each-wake-ups-share-of-the-money)) |
| `schedule {seconds, minutes, laid}` | the net |
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
  delivered are refused at the routing (`wake-refused`, a note to the member);
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
